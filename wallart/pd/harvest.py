#!/usr/bin/env python3
"""
Harvest METADATA (never full images) for public-domain / CC0 artworks from
open-access museum sources into one normalised record format.

    python3 harvest.py --cache pd/raw --out pd/raw/records              # all sources
    python3 harvest.py --cache pd/raw --out pd/raw/records--sources met,aic
    python3 harvest.py ... --workers 8                                # API concurrency

Each source writes  {out}/{source}.jsonl.gz  (one normalised record per line):

    source, source_id, title, artist, artist_birth_year, artist_death_year,
    date, date_begin, date_end, classification, medium, tags[], description,
    culture, department, image_url, iiif_base, image_width, image_height,
    licence, page_url

Raw downloads (bulk dumps, API pages) are cached under --cache so a rerun
only fetches what is missing. Every network step is resumable.

Sources and routes (all keyless):
  met    MetObjects.csv bulk dump (Is Public Domain = True) -> prefilter to
         picture-like rows -> collection API objects/{id} for primaryImage.
  aic    Art Institute of Chicago full data dump (S3 tar.bz2), is_public_domain.
  cma    Cleveland Museum of Art open-access API, cc0=1&has_image=1.
  nga    National Gallery of Art (Washington) opendata CSVs, openaccess=1.
  rijks  Rijksmuseum OAI-PMH (EDM), sharded by identifier prefix; keeps
         PDM 1.0 / CC0 records with an image.
  si     Smithsonian Open Access bulk NDJSON on S3 (art units only), media
         usage.access == CC0.
  ycba   Yale Center for British Art OAI-PMH (LIDO) + IIIF manifest per CC0
         picture record (image URL and pixel size).

Only needs: python3 stdlib + requests + pandas.
"""

import argparse
import base64
import concurrent.futures as cf
import csv
import gzip
import io
import json
import os
import re
import sys
import tarfile
import threading
import time
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote

import requests

UA = "wallart-pd-harvest/1.0 (public-domain catalogue research; python-requests)"
SESSION_LOCAL = threading.local()


def session():
    s = getattr(SESSION_LOCAL, "s", None)
    if s is None:
        s = requests.Session()
        s.headers["User-Agent"] = UA
        s.headers["AIC-User-Agent"] = UA
        a = requests.adapters.HTTPAdapter(pool_connections=4, pool_maxsize=4)
        s.mount("https://", a)
        SESSION_LOCAL.s = s
    return s


def get(url, tries=6, timeout=90, **kw):
    """GET with backoff. Returns Response (status 200/404) or raises."""
    err = None
    for i in range(tries):
        try:
            r = session().get(url, timeout=timeout, **kw)
            if r.status_code in (200, 404):
                return r
            err = f"HTTP {r.status_code}"
            if r.status_code in (403, 407) and "agentproxy" in r.text[:500].lower():
                raise RuntimeError(f"blocked by egress proxy: {url}")
        except requests.RequestException as e:
            err = str(e)
        time.sleep(min(60, 2 ** i))
    raise RuntimeError(f"GET failed {url}: {err}")


def download(url, dest, log=True):
    """Stream a bulk file to disk once (skipped when already complete)."""
    dest = Path(dest)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    tmp = dest.with_suffix(dest.suffix + ".part")
    if log:
        print(f"  downloading {url}", flush=True)
    for i in range(5):
        try:
            with session().get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
            tmp.rename(dest)
            return dest
        except Exception as e:  # noqa
            print(f"    retry {i+1}: {e}", flush=True)
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"download failed: {url}")


def year(v):
    """First plausible 3-4 digit year in a value, else None."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(v) if 0 < v < 2100 else None
    m = re.search(r"(?<!\d)(\d{3,4})(?!\d)", str(v))
    return int(m.group(1)) if m and 0 < int(m.group(1)) < 2100 else None


def to_int(v):
    try:
        return int(float(v))
    except (TypeError, ValueError):
        return None


def rec(**kw):
    base = dict(source="", source_id="", title="", artist="", artist_birth_year=None,
                artist_death_year=None, date="", date_begin=None, date_end=None,
                classification="", medium="", tags=[], description="", culture="",
                department="", image_url="", iiif_base="", image_width=None,
                image_height=None, licence="", page_url="")
    base.update(kw)
    return base


class Writer:
    def __init__(self, path):
        self.path = Path(path)
        self.tmp = self.path.with_suffix(".tmp.gz")
        self.f = gzip.open(self.tmp, "wt", encoding="utf-8")
        self.n = 0

    def write(self, r):
        self.f.write(json.dumps(r, ensure_ascii=False) + "\n")
        self.n += 1

    def close(self):
        self.f.close()
        os.replace(self.tmp, self.path)
        return self.n


# ---------------------------------------------------------------------------
# The Met
# ---------------------------------------------------------------------------
MET_CSV = "https://media.githubusercontent.com/media/metmuseum/openaccess/master/MetObjects.csv"
MET_API = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{}"
# Broad prefilter so we only spend API calls on picture-like rows. curate.py
# applies the strict wall-art rules afterwards.
MET_PICTURE = re.compile(
    r"paint|print|drawing|watercolo|woodblock|woodcut|etching|engraving|lithograph|"
    r"poster|map|photograph|album|scroll|illustration|plate|miniature|pastel|"
    r"charcoal|sketch|book|codices|manuscript|ukiyo|chromolitho|aquatint|mezzotint", re.I)
MET_OBJECTY = re.compile(
    r"^(?:coins?|vases?|ceramics.*|glass.*|textiles.*|metalwork.*|jewelry|arms|armor|"
    r"sculpture|bronzes|jade|netsuke|terracottas|furniture|woodwork.*|stucco|"
    r"medals and plaquettes|musical instruments|costume|shoes|lacquer)$", re.I)


def harvest_met(cache, out, workers, limit=None):
    csv_path = download(MET_CSV, cache / "MetObjects.csv")
    import pandas as pd
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    n_all = len(df)
    df = df[df["Is Public Domain"] == "True"]
    n_pd = len(df)
    cls = df["Classification"]
    name = df["Object Name"]
    pic = cls.str.contains(MET_PICTURE) | name.str.contains(MET_PICTURE)
    obj = cls.str.split("|").str[0].str.strip().str.match(MET_OBJECTY)
    df = df[pic & ~obj]
    print(f"  met: {n_all:,} csv rows, {n_pd:,} public domain, {len(df):,} picture-like -> API",
          flush=True)
    ids = df["Object ID"].tolist()
    if limit:
        ids = ids[:limit]
    rows = {r["Object ID"]: r for r in df.to_dict("records")}

    # API results cache: append-only jsonl of {id, primaryImage, tags, ...}
    api_cache = cache / "met_api.jsonl"
    done = {}
    if api_cache.exists():
        for line in open(api_cache, encoding="utf-8"):
            try:
                d = json.loads(line)
                done[str(d["objectID"])] = d
            except Exception:
                pass
    todo = [i for i in ids if i not in done]
    print(f"  met: {len(done):,} cached API objects, {len(todo):,} to fetch", flush=True)
    lock = threading.Lock()
    keep = ("objectID", "isPublicDomain", "primaryImage", "additionalImages", "tags",
            "artistEndDate", "artistBeginDate", "objectURL", "title", "classification",
            "objectName", "medium")

    def fetch(oid):
        r = get(MET_API.format(oid))
        if r.status_code == 404:
            return {"objectID": int(oid), "missing": True}
        d = r.json()
        d = {k: d.get(k) for k in keep}
        d["additionalImages"] = len(d.get("additionalImages") or [])
        return d

    t0 = time.time()
    with open(api_cache, "a", encoding="utf-8") as fh, \
            cf.ThreadPoolExecutor(workers) as ex:
        futs = {ex.submit(fetch, i): i for i in todo}
        for n, fu in enumerate(cf.as_completed(futs), 1):
            try:
                d = fu.result()
            except Exception as e:  # noqa
                print(f"    met {futs[fu]}: {e}", flush=True)
                continue
            with lock:
                fh.write(json.dumps(d, ensure_ascii=False) + "\n")
                done[str(d["objectID"])] = d
            if n % 5000 == 0:
                fh.flush()
                rate = n / (time.time() - t0)
                print(f"    met API {n:,}/{len(todo):,}  {rate:.0f}/s", flush=True)

    w = Writer(out / "met.jsonl.gz")
    for oid in ids:
        d = done.get(oid)
        row = rows[oid]
        if not d or d.get("missing") or not d.get("isPublicDomain") or not d.get("primaryImage"):
            continue
        tags = [t.get("term") for t in (d.get("tags") or []) if t.get("term")] \
            or [t for t in row["Tags"].split("|") if t]
        ends = [year(x) for x in row["Artist End Date"].split("|")]
        begins = [year(x) for x in row["Artist Begin Date"].split("|")]
        artists = [a.strip() for a in row["Artist Display Name"].split("|")]
        w.write(rec(
            source="met", source_id=oid, title=row["Title"],
            artist=artists[0] if artists else "",
            artist_birth_year=begins[0] if begins else None,
            artist_death_year=max([e for e in ends if e], default=None),
            date=row["Object Date"], date_begin=to_int(row["Object Begin Date"]),
            date_end=to_int(row["Object End Date"]),
            classification=" | ".join(x for x in (row["Classification"], row["Object Name"]) if x),
            medium=row["Medium"], tags=tags, culture=row["Culture"],
            department=row["Department"],
            image_url=d["primaryImage"], licence="CC0",
            page_url=row["Link Resource"] or f"https://www.metmuseum.org/art/collection/search/{oid}",
            extra_nationality=row["Artist Nationality"].split("|")[0],
        ))
    return w.close()


# ---------------------------------------------------------------------------
# Art Institute of Chicago
# ---------------------------------------------------------------------------
AIC_DUMP = "https://artic-api-data.s3.amazonaws.com/artic-api-data.tar.bz2"
AIC_IIIF = "https://www.artic.edu/iiif/2/{}"


def harvest_aic(cache, out, workers, limit=None):
    tar_path = download(AIC_DUMP, cache / "artic-api-data.tar.bz2")
    arts, agents = {}, {}
    # Keep only the fields we need while streaming the tarball (the full dump
    # unpacked is several GB of JSON).
    want = ("id", "title", "is_public_domain", "image_id", "thumbnail", "artist_id",
            "artist_title", "artist_display", "date_display", "date_start", "date_end",
            "classification_titles", "subject_titles", "term_titles", "style_titles",
            "artwork_type_title", "medium_display", "place_of_origin", "department_title",
            "short_description", "category_titles", "theme_titles", "material_titles",
            "technique_titles")
    print("  aic: reading dump", flush=True)
    with tarfile.open(tar_path, "r:bz2") as tf:
        for m in tf:
            if not m.isfile() or not m.name.endswith(".json"):
                continue
            if "/json/artworks/" in m.name:
                d = json.load(tf.extractfile(m))
                if d.get("is_public_domain") and d.get("image_id"):
                    arts[d["id"]] = {k: d.get(k) for k in want}
            elif "/json/agents/" in m.name:
                d = json.load(tf.extractfile(m))
                agents[d["id"]] = (d.get("birth_date"), d.get("death_date"), d.get("title"))
    print(f"  aic: {len(arts):,} public-domain artworks with image, {len(agents):,} agents",
          flush=True)
    w = Writer(out / "aic.jsonl.gz")
    for i, d in arts.items():
        th = d.get("thumbnail") or {}
        ag = agents.get(d.get("artist_id")) or (None, None, None)
        death = year(ag[1])
        if death is None:
            yrs = re.findall(r"(\d{4})\s*[–-]\s*(\d{4})", d.get("artist_display") or "")
            death = int(yrs[0][1]) if yrs else None
        wdt, hgt = to_int(th.get("width")), to_int(th.get("height"))
        iiif = AIC_IIIF.format(d["image_id"])
        # AIC's IIIF refuses "full"/"max" sizes; request an explicit width.
        full_w = wdt if wdt else 3000
        tags = [t for t in (d.get("subject_titles") or []) + (d.get("term_titles") or [])
                + (d.get("style_titles") or []) + (d.get("theme_titles") or []) if t]
        w.write(rec(
            source="aic", source_id=str(i), title=d.get("title") or "",
            artist=d.get("artist_title") or "", artist_birth_year=year(ag[0]),
            artist_death_year=death, date=d.get("date_display") or "",
            date_begin=d.get("date_start"), date_end=d.get("date_end"),
            classification=" | ".join([d.get("artwork_type_title") or ""]
                                      + (d.get("classification_titles") or [])),
            medium=d.get("medium_display") or "", tags=list(dict.fromkeys(tags)),
            description=(d.get("short_description") or "")[:600],
            culture=d.get("place_of_origin") or "", department=d.get("department_title") or "",
            image_url=f"{iiif}/full/{full_w},/0/default.jpg", iiif_base=iiif,
            image_width=wdt, image_height=hgt, licence="CC0",
            page_url=f"https://www.artic.edu/artworks/{i}",
        ))
    return w.close()


# ---------------------------------------------------------------------------
# Cleveland Museum of Art
# ---------------------------------------------------------------------------
CMA_API = ("https://openaccess-api.clevelandart.org/api/artworks/?cc0=1&has_image=1"
           "&limit={limit}&skip={skip}&fields=id,accession_number,title,creation_date,"
           "creation_date_earliest,creation_date_latest,culture,technique,department,"
           "collection,type,url,images,creators,share_license_status,description,"
           "digital_description,alternate_titles")


def harvest_cma(cache, out, workers, limit=None):
    d = cache / "cma"
    d.mkdir(parents=True, exist_ok=True)
    first = get(CMA_API.format(limit=1, skip=0)).json()
    total = first["info"]["total"]
    if limit:
        total = min(total, limit)
    page = 200
    skips = list(range(0, total, page))
    print(f"  cma: {total:,} CC0 records with image, {len(skips)} pages", flush=True)

    def fetch(skip):
        p = d / f"page{page}_{skip:06d}.json.gz"
        if p.exists():
            return
        r = get(CMA_API.format(limit=page, skip=skip), timeout=300)
        data = r.json()
        with gzip.open(p, "wt", encoding="utf-8") as f:
            json.dump(data["data"], f)

    with cf.ThreadPoolExecutor(min(workers, 3)) as ex:
        list(ex.map(fetch, skips))
    w = Writer(out / "cma.jsonl.gz")
    seen = set()
    for skip in skips:
        for a in json.load(gzip.open(d / f"page{page}_{skip:06d}.json.gz", "rt", encoding="utf-8")):
            if a["id"] in seen or a.get("share_license_status") != "CC0":
                continue
            seen.add(a["id"])
            imgs = a.get("images") or {}
            best = imgs.get("full") or imgs.get("print") or imgs.get("web") or {}
            pr = imgs.get("print") or {}
            if not best.get("url"):
                continue
            cr = [c for c in (a.get("creators") or []) if c.get("role") in (None, "artist")] \
                or (a.get("creators") or [])
            artist = ""
            if cr:
                artist = re.sub(r"\s*\(.*$", "", cr[0].get("description") or "").strip()
            deaths = [year(c.get("death_year")) for c in cr]
            w.write(rec(
                source="cma", source_id=str(a["id"]), title=a.get("title") or "",
                artist=artist, artist_birth_year=year(cr[0].get("birth_year")) if cr else None,
                artist_death_year=max([x for x in deaths if x], default=None),
                date=a.get("creation_date") or "", date_begin=a.get("creation_date_earliest"),
                date_end=a.get("creation_date_latest"),
                classification=" | ".join(x for x in (a.get("type"), a.get("collection")) if x),
                medium=a.get("technique") or "",
                tags=[], description=re.sub(r"<[^>]+>", "", a.get("description") or "")[:600],
                culture=", ".join(a.get("culture") or []), department=a.get("department") or "",
                image_url=best["url"], image_width=to_int(best.get("width")),
                image_height=to_int(best.get("height")),
                extra_print_jpg=pr.get("url") or "", licence="CC0",
                page_url=a.get("url") or "",
            ))
    return w.close()


# ---------------------------------------------------------------------------
# National Gallery of Art, Washington
# ---------------------------------------------------------------------------
NGA_RAW = "https://raw.githubusercontent.com/NationalGalleryOfArt/opendata/main/data/{}"


def harvest_nga(cache, out, workers, limit=None):
    import pandas as pd
    d = cache / "nga"
    d.mkdir(parents=True, exist_ok=True)
    files = ["objects.csv", "published_images.csv", "constituents.csv",
             "objects_constituents.csv", "objects_terms.csv"]
    for f in files:
        download(NGA_RAW.format(f), d / f)
    rd = lambda f, **k: pd.read_csv(d / f, dtype=str, keep_default_na=False, **k)
    imgs = rd("published_images.csv")
    imgs = imgs[(imgs["openaccess"] == "1") & (imgs["viewtype"] == "primary")]
    imgs = imgs.sort_values("sequence").drop_duplicates("depictstmsobjectid")
    objs = rd("objects.csv", usecols=["objectid", "title", "displaydate", "beginyear", "endyear",
                                     "medium", "attribution", "classification",
                                     "subclassification", "departmentabbr", "series"])
    cons = rd("constituents.csv", usecols=["constituentid", "forwarddisplayname", "beginyear",
                                          "endyear", "nationality", "constituenttype"])
    oc = rd("objects_constituents.csv", usecols=["objectid", "constituentid", "displayorder",
                                                "roletype"])
    oc = oc[oc["roletype"] == "artist"].copy()
    oc["displayorder"] = pd.to_numeric(oc["displayorder"], errors="coerce")
    oc = oc.merge(cons, on="constituentid", how="left")
    oc["endyear_i"] = pd.to_numeric(oc["endyear"], errors="coerce")
    first = oc.sort_values("displayorder").drop_duplicates("objectid").set_index("objectid")
    maxdeath = oc.groupby("objectid")["endyear_i"].max()
    terms = rd("objects_terms.csv", usecols=["objectid", "termtype", "term"])
    terms = terms[terms["termtype"].isin(["Keyword", "Theme", "Style", "School"])]
    tagmap = terms.groupby("objectid")["term"].apply(lambda s: list(dict.fromkeys(s))).to_dict()
    objs = objs.set_index("objectid")
    print(f"  nga: {len(imgs):,} open-access primary images", flush=True)
    w = Writer(out / "nga.jsonl.gz")
    for im in imgs.to_dict("records"):
        oid = im["depictstmsobjectid"]
        if oid not in objs.index:
            continue
        o = objs.loc[oid]
        a = first.loc[oid] if oid in first.index else None
        wdt, hgt = to_int(im["width"]), to_int(im["height"])
        # NGA's IIIF delivers at most 4096 px on the long side.
        if wdt and hgt and max(wdt, hgt) > 4096:
            s = 4096 / max(wdt, hgt)
            wdt, hgt = int(wdt * s), int(hgt * s)
        md = maxdeath.get(oid)
        w.write(rec(
            source="nga", source_id=oid, title=o["title"],
            artist=(a["forwarddisplayname"] if a is not None else "") or o["attribution"],
            artist_birth_year=year(a["beginyear"]) if a is not None else None,
            artist_death_year=int(md) if md == md and md is not None else None,
            date=o["displaydate"], date_begin=to_int(o["beginyear"]),
            date_end=to_int(o["endyear"]),
            classification=" | ".join(x for x in (o["classification"], o["subclassification"]) if x),
            medium=o["medium"], tags=tagmap.get(oid, []),
            culture=(a["nationality"] if a is not None else ""),
            department=o["departmentabbr"],
            image_url=f"{im['iiifurl']}/full/max/0/default.jpg", iiif_base=im["iiifurl"],
            image_width=wdt, image_height=hgt, licence="CC0",
            page_url=f"https://www.nga.gov/collection/art-object-page.{oid}.html",
            extra_series=o["series"],
        ))
    return w.close()


# ---------------------------------------------------------------------------
# Rijksmuseum (OAI-PMH, EDM)
# ---------------------------------------------------------------------------
RK_OAI = "https://data.rijksmuseum.nl/oai"
NS = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "edm": "http://www.europeana.eu/schemas/edm/",
    "edmfp": "http://www.europeanafashion.eu/edmfp/",
    "ore": "http://www.openarchives.org/ore/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "rdaGr2": "http://rdvocab.info/ElementsGr2/",
    "svcs": "http://rdfs.org/sioc/services#",
    "xml": "http://www.w3.org/XML/1998/namespace",
}
RDF_ABOUT = "{%s}about" % NS["rdf"]
RDF_RES = "{%s}resource" % NS["rdf"]
XML_LANG = "{%s}lang" % NS["xml"]
RK_OK_RIGHTS = ("publicdomain/mark/1.0", "publicdomain/zero/1.0")


def _label(el, prefer=("en", "nl", None)):
    labs = {}
    for p in el.findall("skos:prefLabel", NS):
        labs.setdefault(p.get(XML_LANG), p.text or "")
    for lang in prefer:
        if lang in labs:
            return labs[lang]
    return next(iter(labs.values()), "")


def _texts(cho, tag):
    out = {}
    for e in cho.findall(tag, NS):
        out.setdefault(e.get(XML_LANG), []).append((e.text or "").strip())
    return out


def rk_parse(record):
    md = record.find("oai:metadata", NS)
    if md is None:
        return None
    rdf = md.find("rdf:RDF", NS)
    agg = rdf.find("ore:Aggregation", NS)
    if agg is None:
        return None
    rights = (agg.find("edm:rights", NS).get(RDF_RES) if agg.find("edm:rights", NS) is not None
              else "")
    shown = agg.find("edm:isShownBy", NS)
    if not any(k in rights for k in RK_OK_RIGHTS) or shown is None:
        return {"skip": "rights" if shown is not None else "noimage"}
    cho = rdf.find("edm:ProvidedCHO", NS)
    concepts = {c.get(RDF_ABOUT): _label(c) for c in rdf.findall("skos:Concept", NS)}
    agents = {}
    for a in rdf.findall("edm:Agent", NS):
        agents[a.get(RDF_ABOUT)] = (
            _label(a),
            year((a.find("rdaGr2:dateOfBirth", NS).text
                  if a.find("rdaGr2:dateOfBirth", NS) is not None else None)),
            year((a.find("rdaGr2:dateOfDeath", NS).text
                  if a.find("rdaGr2:dateOfDeath", NS) is not None else None)))
    ref = lambda tag: [e.get(RDF_RES) for e in cho.findall(tag, NS) if e.get(RDF_RES)]
    titles = _texts(cho, "dc:title")
    title = (titles.get("en") or titles.get(None) or titles.get("nl") or [""])[0]
    title_nl = (titles.get("nl") or [""])[0]
    creators = [agents.get(c) for c in ref("dc:creator") if agents.get(c)]
    created = _texts(cho, "dcterms:created")
    img = shown.get(RDF_RES)
    iiif = ""
    m = re.match(r"(https://iiif\.micr\.io/[^/]+)/", img or "")
    if m:
        iiif = m.group(1)
    desc = _texts(cho, "dc:description")
    ident = cho.find("dc:identifier", NS)
    at = agg.find("edm:isShownAt", NS)
    deaths = [c[2] for c in creators if c[2]]
    return rec(
        source="rijks", source_id=(ident.text if ident is not None else
                                   record.find("oai:header/oai:identifier", NS).text),
        title=title, artist=creators[0][0] if creators else "",
        artist_birth_year=creators[0][1] if creators else None,
        artist_death_year=max(deaths) if deaths else None,
        date=(created.get("en") or created.get(None) or created.get("nl") or [""])[0],
        classification=" | ".join(concepts.get(t, "") for t in ref("dc:type")),
        medium=", ".join(concepts.get(t, "") for t in ref("edmfp:technique") + ref("dcterms:medium")),
        tags=[concepts[s] for s in ref("dc:subject") if concepts.get(s)],
        description=((desc.get("en") or desc.get("nl") or [""])[0])[:600],
        image_url=img, iiif_base=iiif, licence=("PDM 1.0" if "mark" in rights else "CC0"),
        page_url=at.get(RDF_RES) if at is not None else "",
        extra_title_nl=title_nl if title_nl != title else "",
        extra_title_lang="en" if titles.get("en") else "nl",
        extra_uri=record.find("oai:header/oai:identifier", NS).text,
    )


def rk_token(c, until):
    raw = (f"metadataPrefix=edm&from=1900-01-01T00%3A00%3A00Z&until={quote(until, safe='')}"
           f"&c={c}&s=0")
    return base64.b64encode(raw.encode()).decode()


def harvest_rijks(cache, out, workers, limit=None):
    """
    The OAI cursor (`c` in the resumption token) is the last record id and ids
    are compared as strings; every id starts '200'. So the list can be split
    into 100 independent shards at prefixes 20000..20099 and harvested in
    parallel. Each shard is cached as a finished .jsonl.gz, so a rerun only
    redoes unfinished shards.
    """
    d = cache / "rijks"
    d.mkdir(parents=True, exist_ok=True)
    until = "2099-01-01T00:00:00Z"
    starts = ["2"] + [f"200{i:02d}" for i in range(100)]
    starts = sorted(set(starts))
    bounds = list(zip(starts, starts[1:] + ["201"]))
    # shard 0 is ids < "20000" (i.e. "2000", "200", ...), cheap
    stats = {"pages": 0, "records": 0, "kept": 0}
    lock = threading.Lock()

    def shard(i, lo, hi):
        p = d / f"shard_{i:03d}.jsonl.gz"
        if p.exists():
            return
        tmp = d / f"shard_{i:03d}.part.gz"
        n = kept = 0
        with gzip.open(tmp, "wt", encoding="utf-8") as fh:
            url = f"{RK_OAI}?verb=ListRecords&resumptionToken={rk_token(lo, until)}"
            if lo == "2":
                url = f"{RK_OAI}?verb=ListRecords&metadataPrefix=edm"
            while url:
                r = get(url, timeout=180)
                root = ET.fromstring(r.content)
                err = root.find("oai:error", NS)
                if err is not None:
                    break
                lr = root.find("oai:ListRecords", NS)
                stop = False
                for record in lr.findall("oai:record", NS):
                    hid = record.find("oai:header/oai:identifier", NS).text.rsplit("/", 1)[-1]
                    if hid > hi:
                        stop = True
                        break
                    n += 1
                    try:
                        x = rk_parse(record)
                    except Exception as e:  # noqa
                        x = None
                    if x and "skip" not in x:
                        fh.write(json.dumps(x, ensure_ascii=False) + "\n")
                        kept += 1
                tok = lr.find("oai:resumptionToken", NS)
                with lock:
                    stats["pages"] += 1
                    if stats["pages"] % 500 == 0:
                        print(f"    rijks pages {stats['pages']:,}", flush=True)
                if stop or tok is None or not (tok.text or "").strip():
                    break
                url = f"{RK_OAI}?verb=ListRecords&resumptionToken={tok.text.strip()}"
                if limit and n >= limit:
                    break
        os.replace(tmp, p)
        with lock:
            stats["records"] += n
            stats["kept"] += kept
        print(f"    rijks shard {i:3d} [{lo}..{hi}] {n:,} records, {kept:,} PD+image", flush=True)

    with cf.ThreadPoolExecutor(workers) as ex:
        futs = [ex.submit(shard, i, lo, hi) for i, (lo, hi) in enumerate(bounds)]
        for f in futs:
            f.result()
    w = Writer(out / "rijks.jsonl.gz")
    seen = set()
    for i in range(len(bounds)):
        for line in gzip.open(d / f"shard_{i:03d}.jsonl.gz", "rt", encoding="utf-8"):
            x = json.loads(line)
            if x["extra_uri"] in seen:
                continue
            seen.add(x["extra_uri"])
            w.write(x)
    return w.close()


# ---------------------------------------------------------------------------
# Smithsonian (bulk S3 NDJSON)
# ---------------------------------------------------------------------------
SI_S3 = "https://smithsonian-open-access.s3-us-west-2.amazonaws.com/metadata/edan/{}/index.txt"
# Art-bearing units. Natural-history specimen units are photos of specimens,
# not plates; SIL is book-level records. HMSG is mostly still in copyright
# but curate.py filters on death year.
SI_UNITS = ["saam", "fsg", "chndm", "npg", "hmsg", "nasm"]


def _ft(content, key):
    return [x.get("content", "") for x in (content.get("freetext", {}).get(key) or [])]


def harvest_si(cache, out, workers, limit=None):
    d = cache / "si"
    d.mkdir(parents=True, exist_ok=True)
    w = Writer(out / "si.jsonl.gz")
    for unit in SI_UNITS:
        urls = get(SI_S3.format(unit)).text.split()
        if limit:
            urls = urls[:max(1, limit // 1000)]
        ud = d / unit
        ud.mkdir(exist_ok=True)

        def fetch(u):
            p = ud / (u.rsplit("/", 1)[-1] + ".utf8.gz")
            if p.exists():
                return p
            r = get(u, timeout=300)
            # keep only CC0 records with images, to keep the cache small
            keep = []
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code} {u}")
            for line in r.content.decode("utf-8", "replace").split("\n"):
                if '"CC0"' in line and "online_media" in line:
                    keep.append(line)
            with gzip.open(p.with_suffix(".part"), "wt", encoding="utf-8") as f:
                f.write("\n".join(keep))
            os.replace(p.with_suffix(".part"), p)
            return p

        with cf.ThreadPoolExecutor(min(workers, 8)) as ex:
            paths = list(ex.map(fetch, urls))
        n = 0
        for p in paths:
            for line in gzip.open(p, "rt", encoding="utf-8"):
                if not line.strip():
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                c = o.get("content", {})
                dnr = c.get("descriptiveNonRepeating", {})
                media = [m for m in (dnr.get("online_media", {}).get("media") or [])
                         if (m.get("usage") or {}).get("access") == "CC0"
                         and m.get("type") == "Images"]
                if not media:
                    continue
                m = media[0]
                best = None
                for res in m.get("resources") or []:
                    if res.get("label") == "High-resolution JPEG" and res.get("url"):
                        best = res
                if best is None:
                    for res in m.get("resources") or []:
                        if res.get("label", "").startswith("High-resolution") and res.get("url"):
                            best = res
                url = best["url"] if best else m.get("content")
                if not url:
                    continue
                names = _ft(c, "name")
                ist = c.get("indexedStructured", {})
                phys = c.get("freetext", {}).get("physicalDescription") or []
                medium = next((x.get("content", "") for x in phys if x.get("label") == "Medium"), "")
                # artist life dates appear in indexedStructured.name or in freetext
                death = None
                for nm in c.get("freetext", {}).get("name") or []:
                    yrs = re.findall(r"(\d{4})\s*[-–]\s*(\d{4})", nm.get("content", ""))
                    if yrs:
                        death = int(yrs[0][1])
                        break
                artist = ""
                for nm in c.get("freetext", {}).get("name") or []:
                    if nm.get("label", "").lower() in ("artist", "designer", "maker", "author",
                                                        "printmaker", "illustrator", "painter",
                                                        "engraver", "lithographer"):
                        artist = nm.get("content", "")
                        break
                artist = re.sub(r",?\s*(American|British|French|Japanese|German|Dutch|born|active).*$",
                                "", artist).strip()
                w.write(rec(
                    source="si", source_id=dnr.get("record_ID", o.get("id")),
                    title=(dnr.get("title") or {}).get("content", "") or o.get("title", ""),
                    artist=artist, artist_death_year=death,
                    date=(_ft(c, "date") or [""])[0],
                    classification=" | ".join(_ft(c, "objectType") + (ist.get("object_type") or [])),
                    medium=medium, tags=list(dict.fromkeys((ist.get("topic") or []) + _ft(c, "topic"))),
                    description="; ".join(_ft(c, "notes"))[:600],
                    culture=", ".join(ist.get("culture") or []), department=unit.upper(),
                    image_url=url, image_width=to_int((best or {}).get("width")),
                    image_height=to_int((best or {}).get("height")),
                    iiif_base=f"https://ids.si.edu/ids/iiif/{m.get('idsId')}" if m.get("idsId") else "",
                    licence="CC0", page_url=dnr.get("record_link") or dnr.get("guid") or "",
                    extra_dates=[x for x in ist.get("date") or []],
                ))
                n += 1
        print(f"  si/{unit}: {n:,} CC0 records with image", flush=True)
    return w.close()


# ---------------------------------------------------------------------------
# Yale Center for British Art (OAI-PMH LIDO + IIIF manifests)
# ---------------------------------------------------------------------------
YCBA_OAI = "https://harvester-bl.britishart.yale.edu/oaicatmuseum/OAIHandler"
YCBA_UA = "Mozilla/5.0 (compatible; wallart-pd-harvest/1.0)"
YCBA_PICTURE = re.compile(r"paint|drawing|watercolo|print|map|book|illustrat|poster|"
                          r"pastel|miniature", re.I)


def _lido(r, pat):
    return [html_unescape(x).strip() for x in re.findall(pat, r, re.S)]


def html_unescape(x):
    import html
    return html.unescape(x)


def ycba_parse(r):
    r = re.sub(r"\s+", " ", r)
    ident = re.search(r"<identifier>oai:tms\.ycba\.yale\.edu:(\d+)</identifier>", r)
    if not ident:
        return None
    oid = ident.group(1)
    cc0 = "publicdomain/zero" in r
    man = re.search(r"<lido:linkResource[^>]*>(https://manifests\.collections\.yale\.edu/ycba/obj/\d+)<", r)
    title = _lido(r, r'<lido:titleSet lido:type="Repository title">.*?<lido:appellationValue[^>]*>([^<]*)<') \
        or _lido(r, r"<lido:titleSet[^>]*>.*?<lido:appellationValue[^>]*>([^<]*)<")
    actors = _lido(r, r"<lido:displayActorInRole>([^<]*)<")
    artist, b, dth = "", None, None
    if actors:
        a0 = actors[0]
        m = re.match(r"(.*?),\s*(?:ca\.\s*)?(\d{3,4})?\s*[–-]\s*(?:ca\.\s*)?(\d{3,4})?", a0)
        if m:
            artist, b, dth = m.group(1), year(m.group(2)), year(m.group(3))
        else:
            artist = a0.split(",")[0]
        deaths = []
        for a in actors:
            m2 = re.search(r"[–-]\s*(?:ca\.\s*)?(\d{4})", a)
            if m2:
                deaths.append(int(m2.group(1)))
        dth = max(deaths) if deaths else dth
    cls = _lido(r, r"<lido:classification>.*?<lido:term>([^<]*)<")
    wt = _lido(r, r"<lido:objectWorkType>.*?<lido:term>([^<]*)<")
    subj = _lido(r, r"<lido:subjectConcept>.*?<lido:term>([^<]*)<")
    date = (_lido(r, r"<lido:displayDate>([^<]*)<") or [""])[0]
    ed = re.search(r"<lido:latestDate>(\d{3,4})", r)
    bd = re.search(r"<lido:earliestDate>(\d{3,4})", r)
    return rec(
        source="ycba", source_id=oid, title=(title or [""])[0], artist=artist,
        artist_birth_year=b, artist_death_year=dth, date=date,
        date_begin=int(bd.group(1)) if bd else None, date_end=int(ed.group(1)) if ed else None,
        classification=" | ".join(cls + wt), medium=(_lido(r, r"<lido:displayMaterialsTech>([^<]*)<") or [""])[0],
        tags=list(dict.fromkeys(subj + wt)), culture="British",
        image_url="", licence="CC0" if cc0 else "",
        page_url=f"https://collections.britishart.yale.edu/catalog/tms:{oid}",
        extra_manifest=man.group(1) if man else "",
    )


def harvest_ycba(cache, out, workers, limit=None):
    """
    OAI-PMH list (LIDO) -> CC0 picture records -> IIIF manifest for each to get
    the image URL and pixel size. The resumption token is an offset
    ("from:until:set:offset:prefix"), so pages are fetched in parallel.
    """
    d = cache / "ycba"
    d.mkdir(parents=True, exist_ok=True)
    hdr = {"User-Agent": YCBA_UA}

    def page(off):
        p = d / f"page_{off:06d}.jsonl.gz"
        if p.exists():
            return [json.loads(x) for x in gzip.open(p, "rt", encoding="utf-8") if x.strip()]
        url = (f"{YCBA_OAI}?verb=ListRecords&metadataPrefix=lido" if off == 0 else
               f"{YCBA_OAI}?verb=ListRecords&resumptionToken=0001-01-01:9999-12-31:.:{off}:lido")
        txt = get(url, timeout=300, headers=hdr).content.decode("utf-8", "replace")
        recs = [x for x in (ycba_parse(c) for c in txt.split("<record>")[1:]) if x]
        with gzip.open(p.with_suffix(".part"), "wt", encoding="utf-8") as f:
            for x in recs:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
        os.replace(p.with_suffix(".part"), p)
        return recs

    allrecs, off, step = [], 0, 100
    batch = max(1, workers)
    with cf.ThreadPoolExecutor(batch) as ex:
        while True:
            offs = list(range(off, off + step * batch, step))
            res = list(ex.map(page, offs))
            for r_ in res:
                allrecs.extend(r_)
            off += step * batch
            if any(len(r_) == 0 for r_ in res) or (limit and len(allrecs) >= limit):
                break
            if (off // step) % 50 == 0:
                print(f"    ycba listed {len(allrecs):,}", flush=True)
    uniq = {x["source_id"]: x for x in allrecs}
    cand = [x for x in uniq.values() if x["licence"] == "CC0" and x["extra_manifest"]
            and YCBA_PICTURE.search(x["classification"])]
    print(f"  ycba: {len(uniq):,} records, {len(cand):,} CC0 picture records -> manifests", flush=True)

    mcache = d / "manifests.jsonl"
    done = {}
    if mcache.exists():
        for line in open(mcache, encoding="utf-8"):
            try:
                x = json.loads(line)
                done[x["id"]] = x
            except Exception:
                pass
    todo = [x for x in cand if x["source_id"] not in done]
    lock = threading.Lock()

    def man(x):
        r = get(x["extra_manifest"], headers=hdr, timeout=120)
        if r.status_code != 200:
            return {"id": x["source_id"], "img": None}
        m = r.json()
        img = None
        try:
            body = m["items"][0]["items"][0]["items"][0]["body"]
            svc = body.get("service") or [{}]
            img = {"url": body.get("id"), "w": body.get("width"), "h": body.get("height"),
                   "iiif": svc[0].get("@id") or svc[0].get("id") or ""}
        except (KeyError, IndexError, TypeError):
            pass
        return {"id": x["source_id"], "img": img, "rights": m.get("rights")}

    with open(mcache, "a", encoding="utf-8") as fh, cf.ThreadPoolExecutor(workers) as ex:
        for n, res in enumerate(ex.map(man, todo), 1):
            with lock:
                fh.write(json.dumps(res) + "\n")
                done[res["id"]] = res
            if n % 2000 == 0:
                fh.flush()
                print(f"    ycba manifests {n:,}/{len(todo):,}", flush=True)
    w = Writer(out / "ycba.jsonl.gz")
    for x in cand:
        m = done.get(x["source_id"]) or {}
        img = m.get("img")
        if not img or not img.get("url") or "zero" not in (m.get("rights") or ""):
            continue
        x.update(image_url=img["url"], image_width=to_int(img.get("w")),
                 image_height=to_int(img.get("h")), iiif_base=img.get("iiif", ""))
        w.write(x)
    return w.close()


SOURCES = {"met": harvest_met, "aic": harvest_aic, "cma": harvest_cma, "nga": harvest_nga,
           "rijks": harvest_rijks, "si": harvest_si,
           "ycba": harvest_ycba}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", default=str(Path(__file__).parent / "raw"))
    ap.add_argument("--out", default=str(Path(__file__).parent / "raw" / "records"))
    ap.add_argument("--sources", default=",".join(SOURCES))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None, help="smoke test: cap records per source")
    a = ap.parse_args()
    cache, out = Path(a.cache), Path(a.out)
    cache.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    status = {}
    for s in a.sources.split(","):
        s = s.strip()
        t = time.time()
        print(f"[{s}]", flush=True)
        try:
            n = SOURCES[s](cache, out, a.workers, a.limit)
            status[s] = {"records": n, "seconds": round(time.time() - t)}
            print(f"[{s}] {n:,} records in {time.time() - t:.0f}s", flush=True)
        except Exception as e:  # noqa
            status[s] = {"error": str(e)}
            print(f"[{s}] FAILED: {e}", flush=True)
    sp = out / "harvest_status.json"
    old = json.loads(sp.read_text()) if sp.exists() else {}
    old.update(status)
    sp.write_text(json.dumps(old, indent=1))


if __name__ == "__main__":
    main()
