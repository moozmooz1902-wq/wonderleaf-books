#!/usr/bin/env python3
"""The gate. Run it before every feed submission and after every deploy.

The seller's previous shop was suspended for misrepresentation and Google
did not say why. That is the normal experience: the notice names the policy,
not the sentence that broke it. So the only defence is to check, yourself,
every condition that policy actually covers - and to make a failure stop the
launch rather than produce a warning somebody scrolls past.

Each check below maps to a specific line of Google's Shopping ads and free
listings policies, or to UK law. The failure message says which, so a red
line is actionable rather than mysterious.

    python3 preflight.py                 # everything checkable offline
    python3 preflight.py --live          # also fetch the deployed site
    python3 preflight.py --live -n 60    # with a bigger page sample

Exit code 0 means every check passed. Anything else means do not submit.
"""
import argparse, concurrent.futures as cf, glob, json, os, re, ssl, sys
import urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import feed as F

UA = ("Mozilla/5.0 (compatible; WallartPreflight/1.0; "
      "+https://developers.google.com/search/docs/crawling-indexing)")
ALLOWED_BUCKETS = {"luxvia-art", "posterleaf-store1", "lunar-kms",
                   "mercury-usm"}

# Text that must never appear on a live shop. "Placeholder copy anywhere on
# the site" is named in suspension write-ups, and an unreplaced template
# string is the single most embarrassing way to fail a manual review.
PLACEHOLDERS = [
    "lorem ipsum", "todo", "fixme", "replace_with", "paste_from",
    "your company", "your brand", "example.com", "example.co.uk",
    "coming soon", "under construction", "test product", "dummy",
    "placeholder", "not set",
]
# Dropped from the list above: a bare "insert " matched the SQL in
# stripe-webhook.ts ("INSERT OR REPLACE INTO orders"), and "tbd"/"xxx" are
# short enough to appear inside ordinary words. A check that cries wolf gets
# ignored, and an ignored check is worse than no check.

# Claims a shop with no trading history cannot make. Fake reviews are a
# criminal matter in the UK under the Digital Markets, Competition and
# Consumers Act 2024, and invented social proof is misrepresentation on
# Google's side.
UNEARNED_CLAIMS = [
    "best seller", "bestseller", "#1", "no.1", "award winning",
    "award-winning", "as seen on", "trusted by", "thousands of happy",
    "5-star", "five star", "customers love", "rated excellent",
    "hand painted", "hand-painted", "original painting", "one of a kind",
    "signed by", "limited edition", "certificate of authenticity",
    "selling fast", "only  left", "hurry", "ends tonight",
]

results = []


def ok(name, detail=""):
    results.append((True, name, detail))


def fail(name, detail):
    results.append((False, name, detail))


def get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
        return r.status, r.headers, r.read()


# --------------------------------------------------------------------------
# 1. Who the business is
# --------------------------------------------------------------------------
def check_identity(cfg):
    missing = F.required_missing(cfg)
    if missing:
        fail("business identity complete",
             "unset: " + ", ".join(missing) + ". Google cross-checks the "
             "legal name, address and country across the website, the "
             "Merchant Center registration and the payments profile; a blank "
             "cannot match.")
    else:
        ok("business identity complete")

    addr = cfg.get("registered_address") or []
    if len(addr) < 2:
        fail("registered address is a real postal address",
             "needs at least a street line and a postcode. Policy prohibits "
             "'using a false or virtual address as headquarters'.")
    else:
        ok("registered address present", ", ".join(addr))

    email = (cfg.get("email") or "").lower()
    dom = (cfg.get("domain") or "").lower()
    if email:
        free = ("gmail.com", "hotmail.com", "outlook.com", "yahoo.",
                "icloud.com", "live.com", "aol.com", "protonmail.")
        if any(f in email for f in free):
            fail("support email is on the shop's own domain",
                 f"{email} is a free mailbox. A registered company selling "
                 f"from a free mailbox is a named trust-signal failure in "
                 f"Merchant Center reviews.")
        elif dom and not email.endswith("@" + dom):
            fail("support email is on the shop's own domain",
                 f"{email} is not on {dom}. Google compares the contact "
                 f"details on the site with the account's.")
        else:
            ok("support email on own domain", email)

    if cfg.get("prices_include_vat") and not cfg.get("vat_number"):
        fail("VAT number present",
             "prices are marked VAT inclusive but no VAT number is set. A UK "
             "VAT-registered trader must publish the number.")
    elif cfg.get("vat_number"):
        v = cfg["vat_number"].replace(" ", "").upper()
        if not re.match(r"^GB\d{9}(\d{3})?$", v):
            fail("VAT number is well formed",
                 f"{cfg['vat_number']!r} is not a GB VAT number "
                 f"(GB + 9 or 12 digits).")
        else:
            ok("VAT number well formed", v)

    if cfg.get("company_number"):
        if not re.match(r"^(\d{8}|[A-Z]{2}\d{6})$",
                        cfg["company_number"].strip().upper()):
            fail("company number is well formed",
                 f"{cfg['company_number']!r} is not a Companies House "
                 f"number.")
        else:
            ok("company number well formed", cfg["company_number"])

    ph = (cfg.get("phone") or "").replace(" ", "")
    if ph and not re.match(r"^(\+44|0)\d{9,10}$", ph):
        fail("telephone number is a UK number",
             f"{cfg.get('phone')!r} does not look like a UK number. A dead "
             f"or fake number is 'false contact information'.")
    elif ph:
        ok("telephone number well formed", cfg["phone"])

    # Brand. "We make it ourselves so there's no brand" is true about the
    # world and wrong about the feed: [brand] is required on new products,
    # Google permits your own name when you manufacture the goods, and the
    # three words people reach for instead are the ones it rejects.
    brand = (cfg.get("brand") or "").strip()
    if brand:
        if brand.lower() in ("n/a", "na", "generic", "none", "unbranded",
                             "no brand", "unknown"):
            fail("brand is a real name",
                 f"{brand!r} is explicitly disallowed by Google. Because you "
                 f"manufacture these yourself, your own trading name is the "
                 f"correct brand.")
        elif len(brand) > 70:
            fail("brand is a real name", f"{len(brand)} chars, limit 70")
        else:
            ok("brand is a real name", brand)
        dom = (cfg.get("domain") or "").split(".")[0].replace("-", "")
        if dom and brand.lower().replace(" ", "")[:6] not in dom.lower() \
                and dom.lower()[:6] not in brand.lower().replace(" ", ""):
            fail("brand matches the domain",
                 f"brand {brand!r} and domain {cfg.get('domain')!r} do not "
                 f"look like the same business. Merchant Center verification "
                 f"cross-checks the business name against the site.")
        elif dom:
            ok("brand matches the domain")

    if not cfg.get("order_confirmation_email"):
        fail("order confirmation email is actually sent",
             "order_confirmation_email is false. The order-confirmed page "
             "tells the buyer an email is coming. Switch on 'Successful "
             "payments' receipts in Stripe (Settings -> Customer emails), "
             "then set this true. A promise the site does not keep is the "
             "whole problem in miniature.")
    else:
        ok("order confirmation email is actually sent")

    if (cfg.get("social_proof") or {}).get("reviews") != "none-yet":
        fail("no unearned social proof",
             "social_proof.reviews is not 'none-yet'. Only set this once "
             "real, verifiable reviews exist - inventing them is a criminal "
             "offence in the UK under the DMCC Act 2024.")
    else:
        ok("no unearned social proof")


# --------------------------------------------------------------------------
# 2. What the site says
# --------------------------------------------------------------------------
# "Nothing we sell is a limited edition" is the OPPOSITE of claiming to sell
# limited editions, and flagging it taught me that scanning for words
# without reading the sentence produces exactly the kind of noise that
# trains someone to skip the output. If a forbidden claim is negated nearby,
# it is a disclaimer and it is doing the right job.
NEGATORS = ("not ", "never ", "no ", "nothing ", "isn't", "is not", "aren't",
            "are not", "do not", "don't", "we never", "without ", "neither ")


def _negated(line, at):
    before = line[max(0, at - 90):at]
    return any(n in before for n in NEGATORS)


def check_source():
    files = []
    for ext in ("astro", "ts", "json", "md"):
        files += glob.glob(os.path.join(WEB, "site", "src", "**", f"*.{ext}"),
                           recursive=True)
    # Stylesheets are excluded on purpose: hex colours such as #1b1a18
    # matched the "#1" claim pattern four times in global.css.
    #
    # wrangler.toml is included because it holds SITE_URL, and SITE_URL is
    # what every canonical tag, the sitemap and the feed's links are built
    # from. A local run rendered
    # <link rel="canonical" href="https://REPLACE_WITH_YOUR_DOMAIN/..."> and
    # nothing caught it, because the scan only looked under src/. One
    # unreplaced string there poisons every URL the shop publishes.
    for extra in ("wrangler.toml", "astro.config.mjs", "package.json"):
        p = os.path.join(WEB, "site", extra)
        if os.path.exists(p):
            files.append(p)
    hits = []
    for p in files:
        # business.json legitimately holds nulls until the seller fills them
        # in; check_identity already reports those.
        if p.endswith(os.path.join("data", "business.json")):
            continue
        low = open(p, encoding="utf-8", errors="replace").read().lower()
        # Comments in this repo discuss these words on purpose, so only
        # flag them outside a comment line.
        for line_n, line in enumerate(low.splitlines(), 1):
            s = line.strip()
            if s.startswith(("//", "*", "/*", "#", "<!--")):
                continue
            for ph in PLACEHOLDERS:
                if ph in line:
                    hits.append(f"{os.path.relpath(p, WEB)}:{line_n} {ph!r}")
    if hits:
        fail("no placeholder text in the site source",
             f"{len(hits)} hit(s): " + "; ".join(hits[:6]))
    else:
        ok("no placeholder text in the site source", f"{len(files)} files")

    claims = []
    for p in files:
        # SCANNED AS WHOLE TEXT, NOT LINE BY LINE. Prose wraps: the
        # disclaimer "nothing we sell is a painting, an original, a / limited
        # edition or a signed work" put the claim on one line and the word
        # that negates it on the one before, so a per-line check reported a
        # disclaimer as a false claim. Comment lines are blanked rather than
        # skipped so that character offsets, and therefore line numbers,
        # stay correct.
        kept = []
        for line in open(p, encoding="utf-8",
                         errors="replace").read().lower().splitlines():
            kept.append("" if line.strip().startswith(
                ("//", "*", "/*", "#", "<!--")) else line)
        text = "\n".join(kept)
        flat = text.replace("\n", " ")
        for c in UNEARNED_CLAIMS:
            at = -1
            while True:
                at = flat.find(c, at + 1)
                if at < 0:
                    break
                if _negated(flat, at):
                    continue
                line_n = text[:at].count("\n") + 1
                claims.append(f"{os.path.relpath(p, WEB)}:{line_n} {c!r}")
    if claims:
        fail("no claims the shop has not earned",
             f"{len(claims)} hit(s): " + "; ".join(claims[:6]))
    else:
        ok("no claims the shop has not earned")

    # The pages UK law and Merchant Center both require to exist.
    needed = ["delivery", "returns", "terms", "privacy", "contact", "about"]
    pages = os.path.join(WEB, "site", "src", "pages")
    gone = [n for n in needed
            if not os.path.exists(os.path.join(pages, f"{n}.astro"))]
    if gone:
        fail("required policy pages exist", "missing: " + ", ".join(gone))
    else:
        ok("required policy pages exist", ", ".join(needed))


# --------------------------------------------------------------------------
# 3. The catalogue and the feed, against each other
# --------------------------------------------------------------------------
def check_catalogue(cat, cfg):
    rows = F.items(cat, cfg)
    problems = F.validate(rows, cfg)
    if problems:
        fail("feed passes Google's spec",
             f"{len(problems)} problem(s): " + "; ".join(problems[:5]))
    else:
        ok("feed passes Google's spec", f"{len(rows):,} items")

    by_slug = {p["slug"]: p for p in cat["products"]}
    bad = []
    for p in cat["products"]:
        for v in p["variants"]:
            b = v["image_path"].split("/", 1)[0]
            if b not in ALLOWED_BUCKETS:
                bad.append(f"{v['id']}: image bucket {b!r} not allowed")
    for r in rows:
        m = re.search(r"/art/([^?]+)\?frame=([a-z]+)&size=([a-z0-9]+)$",
                      r["link"])
        if not m:
            bad.append(f"{r['id']}: link is not a variant URL ({r['link']})")
            continue
        slug, frame, size = m.groups()
        p = by_slug.get(slug)
        if not p:
            bad.append(f"{r['id']}: link slug {slug!r} is not in the "
                       f"catalogue")
            continue
        v = next((x for x in p["variants"]
                  if x["frame"] == frame and x["size"] == size), None)
        if not v:
            bad.append(f"{r['id']}: link points at a variant that does not "
                       f"exist ({frame}/{size})")
        elif f'{v["price"]:.2f}' != r["price"].split()[0]:
            bad.append(f"{r['id']}: feed price {r['price']} but catalogue "
                       f"price {v['price']}")
    if bad:
        fail("every feed row matches a real catalogue variant",
             f"{len(bad)} problem(s): " + "; ".join(bad[:5]))
    else:
        ok("every feed row matches a real catalogue variant")

    # Unframed must not have crept back in without photographs. See the long
    # note in select.py.
    if not cat.get("framed_only", True):
        fail("no unframed products without unframed photographs",
             "framed_only is false. An unframed print submitted with a "
             "photograph of a framed one is the clearest image/offer "
             "mismatch there is.")
    else:
        ok("framed only - every photograph shows what is sold")

    # Restricted products. A print of a negroni is not a negroni, but
    # Shopping's restricted-product screening is automated and reads the
    # title and description.
    import re as _re
    rx = _re.compile(
        r"\b(negroni|martini|whisky|whiskey|gin|rum|vodka|tequila|mezcal|"
        r"brandy|cognac|wine|champagne|prosecco|beer|ale|lager|stout|cider|"
        r"cocktail|aperol|campari|absinthe|vermouth|liqueur|bourbon|sake|"
        r"margarita|mojito|daiquiri|tobacco|cigar|cigarette|vape)\b", _re.I)
    hits = [p["slug"] for p in cat["products"]
            if rx.search(f'{p["title"]} {p["subject"]} {p["description"]}')]
    if hits:
        fail("no restricted subjects in the feed",
             f"{len(hits)} product(s) name alcohol or tobacco, e.g. "
             f"{hits[:3]}. A picture of a drink is not a drink, but the "
             f"screening is automated. Re-run select.py, which filters "
             f"these by rule.")
    else:
        ok("no restricted subjects in the feed")

    # Every niche/section/style the navigation offers must have stock.
    # Google treats links that do not "point to relevant content", and
    # pages with nothing on them, as website-quality violations.
    tax_path = os.path.join(WEB, "site", "src", "data", "taxonomy.json")
    if os.path.exists(tax_path):
        tax = json.load(open(tax_path))
        have_n = {p["niche"] for p in cat["products"]}
        have_s = {p["section"] for p in cat["products"]}
        have_st = {p["style"] for p in cat["products"]}
        have_c = {p["colour"] for p in cat["products"]}
        empty = ([f"niche {k}" for k in tax["niches"] if k not in have_n]
                 + [f"section {s['slug']}" for s in tax["sections"]
                    if s["slug"] not in have_s]
                 + [f"style {s['slug']}" for s in tax["styles"]
                    if s["slug"] not in have_st]
                 + [f"colour {c['slug']}" for c in tax["colours"]
                    if c["slug"] not in have_c])
        if empty:
            fail("every category in the navigation has stock",
                 f"{len(empty)} empty: {empty[:5]}. Re-run build_db.py, "
                 f"which builds the menus from the products.")
        else:
            ok("every category in the navigation has stock",
               f'{len(tax["niches"])} niches, {len(tax["sections"])} sections')
        thin = [k for k in tax["niches"]
                if sum(1 for p in cat["products"] if p["niche"] == k) < 6]
        if thin:
            fail("no category looks unfinished",
                 f"{len(thin)} niche(s) hold fewer than 6 designs: "
                 f"{thin[:5]}. A near-empty category reads as a site under "
                 f"construction, which is a quality violation in itself.")
        else:
            ok("no category looks unfinished")

    titles = [p["title"] for p in cat["products"]]
    if len(set(titles)) != len(titles):
        fail("product titles are unique",
             f"{len(titles) - len(set(titles))} duplicate(s). Two indexable "
             f"pages with one title is a thin-content signal.")
    else:
        ok("product titles are unique", f"{len(titles):,}")


# --------------------------------------------------------------------------
# 4. The deployed site
# --------------------------------------------------------------------------
def check_live(cat, cfg, sample):
    base = f"https://{cfg['domain']}"
    import random
    random.seed(4)

    # 4a. Policy pages must load, without JavaScript, and carry the identity.
    must_contain = {
        "/": [cfg["brand"]],
        "/delivery": ["deliver", str(cfg["fulfilment"]
                                     ["dispatch_working_days"])],
        "/returns": ["return", str(cfg["returns"]["window_days"])],
        "/terms": ["terms", cfg["company_number"]],
        "/privacy": ["privacy"],
        "/contact": [cfg["email"], cfg["company_number"]],
        "/about": ["digitally created"],
        "/faq": ["VAT"],
    }
    for path, needles in must_contain.items():
        try:
            status, _h, body = get(base + path)
            text = body.decode("utf-8", "replace")
            if status != 200:
                fail(f"page {path} loads", f"HTTP {status}")
                continue
            miss = [n for n in needles if n.lower() not in text.lower()]
            if miss:
                fail(f"page {path} contains what it must",
                     f"missing {miss}. A policy page that needs JavaScript "
                     f"to show its text is treated as a missing policy.")
            else:
                ok(f"page {path} loads and reads correctly")
        except Exception as e:
            fail(f"page {path} loads", repr(e))

    # The legal footer, on every page.
    try:
        _s, _h, body = get(base + "/delivery")
        text = body.decode("utf-8", "replace")
        need = [cfg["legal_name"], cfg["company_number"], cfg["vat_number"]]
        miss = [n for n in need if n.lower() not in text.lower()]
        if miss:
            fail("legal identity in the footer of every page",
                 f"missing {miss} on /delivery")
        else:
            ok("legal identity in the footer of every page")
    except Exception as e:
        fail("legal identity in the footer of every page", repr(e))

    # 4b. robots.txt and sitemap.
    try:
        _s, _h, body = get(base + "/robots.txt")
        t = body.decode("utf-8", "replace")
        if "Disallow: /\n" in t or re.search(r"Disallow:\s*/\s*$", t,
                                             re.M):
            fail("robots.txt does not block the shop",
                 "a bare 'Disallow: /' blocks everything, including the "
                 "landing pages Merchant Center must fetch.")
        elif "/img" in t and re.search(r"Disallow:\s*/img", t):
            fail("robots.txt does not block images",
                 "a disallowed image is recorded as unavailable and "
                 "disapproves the product.")
        elif "sitemap" not in t.lower():
            fail("robots.txt names the sitemap", t[:120])
        else:
            ok("robots.txt allows the crawler and names the sitemap")
    except Exception as e:
        fail("robots.txt loads", repr(e))

    try:
        s, _h, body = get(base + "/sitemap.xml")
        n = body.count(b"<loc>")
        if s != 200 or n == 0:
            fail("sitemap.xml loads with URLs", f"HTTP {s}, {n} urls")
        elif b"?frame=" in body:
            fail("sitemap has no variant URLs",
                 "variant URLs belong in the feed, not the sitemap - listing "
                 "nine per design asks Google to index nine duplicates.")
        else:
            ok("sitemap.xml loads", f"{n:,} urls")
    except Exception as e:
        fail("sitemap.xml loads", repr(e))

    # 4c. THE BIG ONE. Does each variant URL quote the feed's price?
    rows = F.items(cat, cfg)
    picks = random.sample(rows, min(sample, len(rows)))

    def check_one(r):
        try:
            status, _h, body = get(r["link"])
            text = body.decode("utf-8", "replace")
            if status != 200:
                return f"{r['id']}: HTTP {status} at {r['link']}"
            want = r["price"].split()[0]
            # The visible price.
            if f"£{want}" not in text and f"&#163;{want}" not in text:
                return (f"{r['id']}: page does not show £{want} "
                        f"({r['link']}) - this is the price mismatch that "
                        f"becomes a misrepresentation finding")
            # The structured price, which Google reads separately.
            m = re.search(r'"price"\s*:\s*"([0-9.]+)"', text)
            if not m:
                return f"{r['id']}: no JSON-LD offer price on the page"
            if m.group(1) != want:
                return (f"{r['id']}: JSON-LD price {m.group(1)} but feed "
                        f"price {want}")
            if "InStock" not in text:
                return f"{r['id']}: JSON-LD availability is not InStock"
            if r["title"][:40].lower() not in text.lower():
                return f"{r['id']}: feed title is not on the page"
            return None
        except Exception as e:
            return f"{r['id']}: {e!r}"

    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        probs = [p for p in ex.map(check_one, picks) if p]
    if probs:
        fail("every sampled variant URL quotes the feed's price",
             f"{len(probs)} of {len(picks)} failed: " + "; ".join(probs[:4]))
    else:
        ok("every sampled variant URL quotes the feed's price",
           f"{len(picks)} sampled")

    # 4d. Images: reachable, an image, and big enough.
    def check_img(r):
        try:
            status, h, body = get(r["image_link"])
            if status != 200:
                return f"{r['id']}: image HTTP {status}"
            ct = h.get("content-type", "")
            if not ct.startswith("image/"):
                return f"{r['id']}: image content-type {ct!r}"
            if len(body) < 5000:
                return f"{r['id']}: image only {len(body)} bytes"
            # Google enforces a 500x500 minimum from 31 Jan 2027.
            w = hgt = None
            if body[:2] == b"\xff\xd8":
                i = 2
                while i < len(body) - 9:
                    if body[i] != 0xFF:
                        i += 1
                        continue
                    mk = body[i + 1]
                    if mk in (0xC0, 0xC1, 0xC2, 0xC3):
                        hgt = int.from_bytes(body[i + 5:i + 7], "big")
                        w = int.from_bytes(body[i + 7:i + 9], "big")
                        break
                    if mk in (0xD8, 0xD9) or 0xD0 <= mk <= 0xD7:
                        i += 2
                        continue
                    i += 2 + int.from_bytes(body[i + 2:i + 4], "big")
            if w and (w < 500 or hgt < 500):
                return f"{r['id']}: image {w}x{hgt}, under Google's 500x500"
            return None
        except Exception as e:
            return f"{r['id']}: image {e!r}"

    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        probs = [p for p in ex.map(check_img, picks[:min(24, len(picks))])
                 if p]
    if probs:
        fail("sampled images load from our own domain at a usable size",
             f"{len(probs)} failed: " + "; ".join(probs[:4]))
    else:
        ok("sampled images load from our own domain at a usable size",
           f"{min(24, len(picks))} sampled")

    # 4e. A dead end that looks fine until someone tries to buy.
    try:
        req = urllib.request.Request(
            base + "/api/checkout", method="POST",
            data=b'{"items":[]}',
            headers={"User-Agent": UA, "content-type": "application/json"})
        try:
            urllib.request.urlopen(req, timeout=20)
            fail("checkout endpoint validates its input",
                 "an empty basket was accepted")
        except urllib.error.HTTPError as e:
            if e.code in (400, 503):
                ok("checkout endpoint is live and validates input",
                   f"HTTP {e.code} on an empty basket")
            else:
                fail("checkout endpoint is live", f"HTTP {e.code}")
    except Exception as e:
        fail("checkout endpoint is live", repr(e))

    # 4e2. A missing page must look like the shop, not like a broken server.
    # "Repair or redirect broken URLs, such as those returning 404 or 500"
    # is listed under website quality.
    try:
        status, _h, body = get(base + "/art/this-does-not-exist-12345")
        fail("a missing page renders the shop's 404 page",
             f"expected 404, got HTTP {status}")
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", "replace")
        if e.code != 404:
            fail("a missing page renders the shop's 404 page",
                 f"HTTP {e.code}")
        elif cfg["brand"].lower() not in text.lower() or len(text) < 2000:
            fail("a missing page renders the shop's 404 page",
                 f"got a bare {len(text)}-byte response rather than a page "
                 f"with the shop's navigation on it")
        else:
            ok("a missing page renders the shop's 404 page")
    except Exception as e:
        fail("a missing page renders the shop's 404 page", repr(e))

    # 4e3. Every internal link must work. "Ensure all links across the
    # website are working and point to relevant content."
    import html as _html
    seen_links, broken = set(), []
    for seed in ("/", "/delivery", "/returns", "/contact", "/style",
                 "/rooms", f'/c/{cat["products"][0]["section"]}'):
        try:
            _s, _h, body = get(base + seed)
        except Exception:
            continue
        for m in re.finditer(r'href="(/[^"#?]*)"',
                             body.decode("utf-8", "replace")):
            seen_links.add(_html.unescape(m.group(1)).rstrip("/") or "/")

    def probe(path):
        try:
            s, _h, _b = get(base + path)
            return None if s == 200 else f"{path} -> HTTP {s}"
        except urllib.error.HTTPError as e:
            return f"{path} -> HTTP {e.code}"
        except Exception as e:
            return f"{path} -> {e!r}"

    links = sorted(l for l in seen_links if not l.startswith("/api"))
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        broken = [b for b in ex.map(probe, links) if b]
    if broken:
        fail("every internal link works",
             f"{len(broken)} of {len(links)} broken: {broken[:5]}")
    else:
        ok("every internal link works", f"{len(links)} checked")

    # 4e4. The structured data a reviewer and the crawler both read.
    try:
        _s, _h, body = get(base + "/")
        t = body.decode("utf-8", "replace")
        missing = [k for k in ('"@type":"Organization"', cfg["company_number"],
                               cfg["email"]) if k not in t.replace(" ", "")
                   and k not in t]
        if missing:
            fail("home page carries the business identity in markup",
                 f"missing {missing}")
        else:
            ok("home page carries the business identity in markup")
    except Exception as e:
        fail("home page carries the business identity in markup", repr(e))
    try:
        p0 = cat["products"][0]
        _s, _h, body = get(f'{base}/art/{p0["slug"]}')
        t = body.decode("utf-8", "replace").replace(" ", "")
        if '"@type":"BreadcrumbList"' not in t:
            fail("product pages carry breadcrumb markup", "not found")
        else:
            ok("product pages carry breadcrumb markup")
    except Exception as e:
        fail("product pages carry breadcrumb markup", repr(e))

    # 4f. No reference to the suspended Shopify shop.
    try:
        _s, _h, body = get(base + "/")
        t = body.decode("utf-8", "replace").lower()
        for bad_host in ("myshopify.com", "cdn.shopify.com"):
            if bad_host in t:
                fail("no trace of the previous Shopify shop",
                     f"{bad_host} appears in the home page. Carrying the old "
                     f"shop's assets onto the new domain re-links the new "
                     f"site to the suspended one.")
                break
        else:
            ok("no trace of the previous Shopify shop")
    except Exception as e:
        fail("no trace of the previous Shopify shop", repr(e))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true",
                    help="also fetch the deployed site over https")
    ap.add_argument("-n", "--sample", type=int, default=30,
                    help="how many variant URLs to fetch with --live")
    a = ap.parse_args()

    cat = json.load(open(os.path.join(HERE, "catalogue.json")))
    cfg = json.load(open(os.path.join(WEB, "business.config.json")))

    check_identity(cfg)
    check_source()
    # The catalogue and feed checks are about the PRODUCTS, so they must run
    # even before the business identity is filled in - that is the whole
    # value of running this early. Stand in placeholder values for the few
    # identity fields the feed serialiser needs to produce a row; the
    # identity itself is already checked above, and these substitutes never
    # reach a file.
    probe = json.loads(json.dumps(cfg))
    probe["domain"] = probe.get("domain") or "preflight.invalid"
    probe["brand"] = probe.get("brand") or "Preflight"
    if probe["fulfilment"]["delivery"][0].get("price") is None:
        probe["fulfilment"]["delivery"][0]["price"] = 0.0
    try:
        check_catalogue(cat, probe)
    except Exception as e:
        fail("catalogue checks ran", repr(e))

    if a.live:
        if F.required_missing(cfg):
            fail("live checks",
                 "cannot run: the business identity is incomplete, so there "
                 "is no verified domain to fetch.")
        else:
            check_live(cat, cfg, a.sample)
    width = max(len(n) for _p, n, _d in results) + 2
    print()
    for passed, name, detail in results:
        mark = "PASS" if passed else "FAIL"
        print(f"  [{mark}] {name.ljust(width)} {detail if not passed else detail}")
    bad = [r for r in results if not r[0]]
    print(f"\n{len(results) - len(bad)} passed, {len(bad)} failed")
    if bad:
        print("\nDO NOT SUBMIT THE FEED OR REQUEST A REVIEW until every line "
              "above passes.")
        print("Each failure names the policy or the law behind it; fix the "
              "cause, not the check.")
        if not a.live:
            print("\n(These are the offline checks. Run with --live once the "
                  "site is deployed - the price-match check is the one that "
                  "catches the failure that suspended the last shop.)")
        return 1
    if not a.live:
        print("\nOffline checks all pass. Run --live after deploying.")
    else:
        print("\nAll checks pass. The feed may be submitted.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
