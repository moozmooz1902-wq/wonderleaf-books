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


def _stripe_api(path):
    key = os.environ.get("STRIPE_SECRET_KEY")
    if not key:
        return None
    req = urllib.request.Request(
        "https://api.stripe.com/v1/" + path,
        headers={"Authorization": "Bearer " + key, "User-Agent": UA})
    with urllib.request.urlopen(
            req, timeout=30, context=ssl.create_default_context()) as r:
        return json.loads(r.read())


def _stripe_window(session_url):
    """The delivery estimate Stripe is holding for a session we just made.

    Returns (min, max) in business days, None if there is no key to ask
    with, or a string explaining why it could not be read. The session id
    is in the hosted URL, the session names a shipping rate, and the rate
    carries the estimate - two hops, no expand syntax to get wrong.
    """
    m = re.search(r"cs_[A-Za-z0-9_]+", session_url or "")
    if not m:
        return "no session id in the checkout URL"
    try:
        sess = _stripe_api(f"checkout/sessions/{m.group(0)}")
        if sess is None:
            return None
        opts = sess.get("shipping_options") or []
        if not opts:
            return ("the session carries no shipping option at all, so the "
                    "buyer is never quoted a delivery window")
        rate_id = opts[0].get("shipping_rate")
        rate = (rate_id if isinstance(rate_id, dict)
                else _stripe_api(f"shipping_rates/{rate_id}"))
        est = (rate or {}).get("delivery_estimate") or {}
        lo, hi = est.get("minimum") or {}, est.get("maximum") or {}
        if not lo or not hi:
            return "the shipping rate carries no delivery_estimate"
        if lo.get("unit") != "business_day" or hi.get("unit") != "business_day":
            return (f"the estimate is in {lo.get('unit')}/{hi.get('unit')}, "
                    f"not business days, so it cannot be compared with the "
                    f"feed")
        return int(lo["value"]), int(hi["value"])
    except Exception as e:
        return f"could not read the session back from Stripe: {e!r}"


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
                at = line.find(ph)
                # `placeholder="Admin key"` is an HTML attribute telling a
                # browser what to grey out in an empty input. It is not
                # placeholder copy, and reporting it trains people to read
                # this check's failures as noise - which is the only way a
                # real one gets ignored.
                if at >= 0 and ph == "placeholder" and \
                        line[at + len(ph):at + len(ph) + 1] == "=":
                    at = line.find(ph, at + 1)
                if at >= 0:
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
                # "#1" MEANS "#1 BEST SELLER", NOT "#1a1a1f".
                #
                # Stylesheets were excluded from this scan because hex
                # colours matched four times in global.css. That worked
                # until a page carried its own <style> block - the admin
                # dashboard - and the same false positive came straight
                # back. Excluding another file would have been the third
                # patch on the same hole, so fix the pattern instead: a
                # rank claim is never followed by a hex digit.
                if c == "#1" and len(flat) > at + 2 and \
                        flat[at + 2] in "0123456789abcdef":
                    continue
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
            # "unframed" is not a bucket. It is the shop's own static asset
            # directory, where catalogue/unframed.py writes the unframed
            # photographs - they are rendered here rather than by the GPU
            # run, so they ship with the site instead of living in R2. The
            # allow-list still applies to everything served out of a bucket;
            # the check above has already proved each unframed path points
            # at a file that exists.
            if b != "unframed" and b not in ALLOWED_BUCKETS:
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

    # EVERY TIER MUST USE ITS OWN PHOTOGRAPH.
    #
    # This used to assert "framed only", because no unframed photograph
    # existed and an unframed print sold against a picture of a framed one is
    # the clearest image/offer mismatch there is. Unframed now has its own
    # photographs (catalogue/unframed.py), so the check is no longer "do not
    # sell unframed" but the thing that rule was protecting: a variant's
    # picture has to show the variant. That also catches the failure the old
    # check could not - a framed variant pointed at an unframed picture.
    #
    # The files are checked on disk too. They ship as static assets, so a
    # missing one is a 404 on a live product page rather than a build error.
    import os as _os
    import re as _re2
    assets = _os.path.join(_os.path.dirname(HERE), "site", "public", "unframed")
    bad, missing = [], set()
    for p_ in cat["products"]:
        for v in p_["variants"]:
            ip = v["image_path"]
            if v["frame"] == "none":
                if not ip.startswith("unframed/"):
                    bad.append(f'{v["id"]}: unframed variant shows {ip}')
                elif not _os.path.exists(_os.path.join(assets,
                                                       _os.path.basename(ip))):
                    missing.add(_os.path.basename(ip))
            else:
                if "/listing/" not in ip or not ip.endswith(f'-{v["frame"]}.jpg'):
                    bad.append(f'{v["id"]}: {v["frame"]} variant shows {ip}')
    # THE TITLE HAS TO AGREE WITH THE TIER TOO.
    #
    # Every title template contains the word "Framed", because until the
    # unframed tier existed every product was framed. An unframed variant
    # inheriting that produces "... Framed Charcoal Print - Unframed Print,
    # A4" - a title that contradicts itself, which is a disapproval without
    # anyone even looking at the photograph.
    wrong_title = [
        v["id"] for p_ in cat["products"] for v in p_["variants"]
        if v["frame"] == "none" and _re2.search(r"\bframed\b", v["title"], _re2.I)
        and not _re2.search(r"\bunframed\b", v["title"].replace("Unframed", "U"), _re2.I)
    ]
    wrong_title = [
        v["id"] for p_ in cat["products"] for v in p_["variants"]
        if v["frame"] == "none"
        and _re2.search(r"(?<!un)\bframed\b", v["title"], _re2.I)
    ]
    if wrong_title:
        fail("no unframed product is called framed",
             f"{len(wrong_title)} title(s) contradict themselves, e.g. "
             + next(v["title"] for p_ in cat["products"] for v in p_["variants"]
                    if v["id"] == wrong_title[0]))
    else:
        ok("no unframed product is called framed")

    if bad:
        fail("every variant's photograph shows that variant",
             f"{len(bad)} mismatch(es): " + "; ".join(bad[:4]))
    elif missing:
        fail("every unframed photograph exists",
             f"{len(missing)} missing from site/public/unframed/, which is a "
             f"404 on a live product page: " + ", ".join(sorted(missing)[:4]))
    else:
        n_un = sum(1 for p_ in cat["products"] for v in p_["variants"]
                   if v["frame"] == "none")
        ok("every variant's photograph shows that variant",
           f"{n_un:,} unframed, rest framed")

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
def check_live(cat, cfg, sample, base_override=None):
    base = (base_override or f"https://{cfg['domain']}").rstrip("/")
    import random
    random.seed(4)

    def onbase(u):
        """Re-point a feed URL at the host actually under test.

        The feed carries absolute https://walryvo.com/... links, because that
        is what Merchant Center will be given. When these checks run against a
        staging deploy the custom domain is not attached yet, so fetching the
        feed's own URL tests nothing - it just fails to resolve. Same path,
        same query (?frame= and ?size= are the whole point of the price
        check), different host."""
        if not base_override:
            return u
        from urllib.parse import urlsplit, urlunsplit
        a, b = urlsplit(u), urlsplit(base)
        return urlunsplit((b.scheme, b.netloc, a.path, a.query, a.fragment))

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
        blocked = ("Disallow: /\n" in t
                   or re.search(r"Disallow:\s*/\s*$", t, re.M))
        if blocked and base_override:
            # Correct, and deliberate: robots.txt serves a blanket Disallow on
            # any host that is not the canonical domain, so a staging deploy
            # cannot be indexed as a second copy of the shop. Assert that it
            # IS blocked here rather than letting the real check pass by
            # accident on a host where allowing would be the bug.
            ok("staging host is closed to crawlers", base)
        elif blocked:
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

    # 4a-ii. NO PAGE MAY CLAIM A DELIVERY PRICE THE CONFIG DOES NOT SET.
    #
    # Found on 28 Oct by looking at a phone screenshot, not by any check.
    # Delivery moved from free to GBP 2.99 in business.config.json, the
    # footer and the feed followed it because they read the value, and the
    # HOME PAGE went on saying "Free UK delivery" twice in hardcoded text -
    # once in the hero and once in the assurance strip. A shop advertising
    # free delivery and charging 2.99 at the checkout is the plainest
    # misrepresentation there is, and it would have been live to Google.
    #
    # So the words are checked against the number on every page that has
    # them. This is the same discipline as the feed/page price check below;
    # it was simply never applied to the delivery line.
    try:
        free = cfg["fulfilment"]["delivery"][0]["price"] == 0
        liars = []
        for path in ("/", "/delivery", "/returns", "/faq", "/terms"):
            try:
                _s, _h, body = get(base + path)
                text = body.decode("utf-8", "replace").lower()
            except Exception:
                continue
            says_free = "free uk delivery" in text or "free delivery" in text
            if says_free and not free:
                liars.append(path)
        if liars:
            fail("no page promises free delivery while we charge for it",
                 f"{liars} say 'free delivery' but delivery costs "
                 f"{cfg['fulfilment']['delivery'][0]['price']}")
        else:
            ok("delivery price on the pages matches the config",
               "free" if free else
               f"{cfg['fulfilment']['delivery'][0]['price']:.2f}")
    except Exception as e:
        fail("delivery price on the pages matches the config", repr(e))

    # 4a-iii. GOOGLE'S OWNERSHIP FILE MUST STAY SERVED.
    #
    # Search Console verified walryvo.com on 28 Oct by fetching
    # /google<token>.html, and its own dialog says: "To stay verified,
    # don't remove the verification file." Lose it and the site quietly
    # becomes unverified, which takes the Merchant Center website claim
    # with it - and nothing on the site would look broken.
    #
    # The danger is not malice, it is tidying. site/public/google*.html is
    # one line of text with a meaningless name; it reads like debris. So
    # the check globs for whatever ownership files exist and asserts each
    # one is still served as a 200 at its exact path - which also covers
    # the Workers Assets html_handling setting silently reverting to the
    # default that 307s /foo.html to /foo.
    import glob as _glob
    pub = os.path.join(WEB, "site", "public")
    owners = sorted(_glob.glob(os.path.join(pub, "google*.html")))
    if not owners:
        ok("no Google ownership file to serve", "none in site/public")
    else:
        for f in owners:
            name = os.path.basename(f)
            try:
                st, _h, body = get(f"{base}/{name}")
                text = body.decode("utf-8", "replace").strip()
                if st != 200:
                    fail(f"Google ownership file {name} is served",
                         f"HTTP {st} - Search Console verification will "
                         f"lapse and the Merchant Center claim with it")
                elif "google-site-verification" not in text:
                    fail(f"Google ownership file {name} has the right body",
                         f"got {text[:60]!r}")
                else:
                    ok(f"Google ownership file {name} is served", "200")
            except Exception as e:
                fail(f"Google ownership file {name} is served", repr(e))

    # 4a-iii-b. THE BACK OFFICE MUST BE SHUT.
    #
    # /admin shows every order, every customer email and every visitor's
    # movements. It is behind a key, but a key is only as good as the day
    # nobody disabled it, and this is the one page on the site where being
    # wrong is a data breach rather than a disapproval. So: prove from
    # outside, with no credentials at all, that an anonymous request gets
    # nothing - and that robots is told to stay away as well, because an
    # indexed admin URL is an invitation even when it is locked.
    try:
        # urlopen raises on 4xx, and 401/403/404 are all expected answers
        # here, so take the status off the exception rather than treating
        # "the lock worked" as a transport failure.
        try:
            st, h, body = get(base + "/admin")
        except urllib.error.HTTPError as e:
            st, h, body = e.code, e.headers, e.read()
        txt = body.decode("utf-8", "replace")
        leaked = [w for w in ("Happening now", "All-time revenue",
                              "No orders yet", "wa_admin=")
                  if w in txt]
        robots_txt = get(base + "/robots.txt")[2].decode("utf-8", "replace")
        if st == 404:
            # Nothing deployed at /admin is also a safe state - there is no
            # dashboard to leak. Said plainly rather than passed silently,
            # because "the back office is missing" and "the back office is
            # locked" are different facts and only one of them is expected.
            ok("the admin page is not deployed yet",
               "HTTP 404 - run the three commands in DASHBOARD.md")
        elif leaked:
            fail("the admin page is not readable without the key",
                 "an anonymous request got " + ", ".join(leaked) +
                 " - the dashboard is OPEN. Check ADMIN_KEY is set and that "
                 "authed() is still called.")
        elif st not in (200, 401, 403, 503):
            fail("the admin page answers sensibly without a key",
                 f"HTTP {st}")
        elif "noindex" not in (h.get("x-robots-tag") or "").lower():
            fail("the admin page is marked noindex",
                 f"x-robots-tag is {h.get('x-robots-tag')!r}")
        elif "Disallow: /admin" not in robots_txt:
            fail("robots.txt disallows /admin", "it does not")
        else:
            ok("the admin page is shut to anonymous visitors",
               f"HTTP {st}, noindex, disallowed in robots.txt")
    except Exception as e:
        fail("the admin page is shut to anonymous visitors", repr(e))

    # And its data endpoint, which is the one that would actually hand over
    # the orders. A login form leaking nothing is no comfort if the JSON
    # behind it answers everyone.
    try:
        try:
            st, _h, body = get(base + "/api/admin")
            txt = body.decode("utf-8", "replace")
            if '"orders"' in txt or '"liveList"' in txt:
                fail("the admin data endpoint requires the key",
                     "it returned the dashboard payload to an anonymous "
                     "request")
            else:
                fail("the admin data endpoint requires the key",
                     f"HTTP {st} with an unexpected body: {txt[:120]}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                ok("the admin data endpoint is not deployed yet", "HTTP 404")
            elif e.code in (401, 403, 503):
                ok("the admin data endpoint requires the key", f"HTTP {e.code}")
            else:
                fail("the admin data endpoint requires the key",
                     f"HTTP {e.code}")
    except Exception as e:
        fail("the admin data endpoint requires the key", repr(e))

    # 4a-iv. STRIPE'S DELIVERY PROMISE MUST MATCH THE FEED'S.
    #
    # Found 28 Oct by opening a real checkout session and reading it:
    # Stripe said "2-7 business days" while the feed said 3 to 7. The
    # maximum had always added handling to transit; the minimum used
    # transit alone, so checkout promised a print could arrive in two days
    # when it takes at least one to make. Google names "hiding processing
    # delays behind a stated delivery time" as misrepresentation, and the
    # number at the moment of payment is the one that counts.
    #
    # Nothing short of creating a session catches this - the feed was
    # right, the pages were right, and only Stripe disagreed. So this
    # creates one. It is a session, not a charge, and nobody is billed.
    try:
        f = cfg["fulfilment"]
        want_min = f["min_handling_days"] + f["delivery"][0]["min_days"]
        want_max = f["dispatch_working_days"] + f["delivery"][0]["max_days"]
        row = F.items(cat, cfg)[0]
        import urllib.request as _u
        req = _u.Request(base + "/api/checkout",
                         data=json.dumps({"items": [{"id": row["id"],
                                                     "qty": 1}]}).encode(),
                         headers={"Content-Type": "application/json",
                                  "User-Agent": UA})
        with urllib.request.urlopen(req, timeout=40, context=ssl.create_default_context()) as r:
            sess = json.loads(r.read())
        if not sess.get("url"):
            fail("checkout quotes the same delivery window as the feed",
                 f"no session: {str(sess)[:120]}")
        else:
            # The estimate is on the session, not the page; read it back.
            _s2, _h2, body = get(sess["url"])
            txt = body.decode("utf-8", "replace")
            m = re.search(r"(\d+)\s*[-–]\s*(\d+)\s*business days", txt)
            if not m:
                # Stripe's hosted page is JavaScript-rendered, so urllib
                # sees a shell with no window in it. The first version of
                # this check reported PASS on that - a check whose
                # strongest statement was about text it never saw, the same
                # vacuous-pass bug the feed checker had.
                #
                # The page is not the only copy of the number. The session
                # carries the shipping rate we sent, so ask Stripe for it
                # directly. That is the real end-to-end test anyway: it
                # reads back what OUR endpoint actually submitted, rather
                # than what Stripe chose to render.
                got = _stripe_window(sess["url"])
                if got is None:
                    fail("checkout quotes the same delivery window as the "
                         "feed",
                         "NOT VERIFIED - the hosted page is JavaScript and "
                         "STRIPE_SECRET_KEY is not set, so the window could "
                         "not be read from the API either. Set that key, or "
                         "check it by hand in a browser.")
                elif isinstance(got, str):
                    fail("checkout quotes the same delivery window as the "
                         "feed", got)
                elif got != (want_min, want_max):
                    fail("checkout quotes the same delivery window as the "
                         "feed",
                         f"Stripe holds {got[0]}-{got[1]} business days, the "
                         f"feed says {want_min}-{want_max}. The number a "
                         f"buyer sees when they pay must not be faster than "
                         f"the one submitted to Google.")
                else:
                    ok("checkout quotes the same delivery window as the feed",
                       f"{want_min}-{want_max} business days, read back from "
                       f"the Stripe API")
            elif (int(m.group(1)), int(m.group(2))) != (want_min, want_max):
                fail("checkout quotes the same delivery window as the feed",
                     f"Stripe says {m.group(1)}-{m.group(2)} business days, "
                     f"the feed says {want_min}-{want_max}. The number a "
                     f"buyer sees when they pay must not be faster than "
                     f"the one submitted to Google.")
            else:
                ok("checkout quotes the same delivery window as the feed",
                   f"{want_min}-{want_max} business days")
    except Exception as e:
        fail("checkout quotes the same delivery window as the feed", repr(e))

    # 4b-ii. THE SERVED FEED IS THE FEED.
    #
    # Merchant Center is pointed at /feed.xml as a scheduled fetch, so from
    # here on the only feed that matters is the one the deploy is serving -
    # not the one sitting in this checkout. If a rebuild regenerated the
    # catalogue and the deploy did not carry the new feed.xml, Google would
    # go on reading last week's prices against this week's pages, which is
    # the price mismatch these checks exist to prevent, arriving by the one
    # route that leaves no trace on any page.
    #
    # So compare the bytes Google would fetch against the feed this
    # catalogue produces, item for item.
    try:
        want_xml = F.to_xml(F.items(cat, cfg), cfg, f"{cfg['brand']} products")
        s_feed, h_feed, body = get(base + "/feed.xml")
        if s_feed != 200:
            fail("served /feed.xml loads", f"HTTP {s_feed}")
        else:
            got = body.decode("utf-8", "replace")
            n_got, n_want = got.count("<item>"), want_xml.count("<item>")
            ctype = (h_feed.get("content-type") or "").lower()
            if n_got != n_want:
                fail("served feed matches the catalogue",
                     f"the deploy serves {n_got:,} items, this catalogue "
                     f"builds {n_want:,}. Rebuild the feed and redeploy - "
                     f"a scheduled fetch would read the stale one.")
            elif "xml" not in ctype:
                fail("served feed is sent as XML",
                     f"content-type {ctype!r}. Merchant Center sniffs the "
                     f"type and rejects a feed served as text/html.")
            elif got.strip() != want_xml.strip():
                # Same count, different bytes: a price, title or link moved.
                import difflib
                d = [l for l in difflib.unified_diff(
                        want_xml.splitlines(), got.splitlines(),
                        "catalogue", "served", n=0, lineterm="")
                     if l[:1] in "+-" and l[:3] not in ("+++", "---")]
                fail("served feed matches the catalogue",
                     f"{len(d)} lines differ. First: "
                     + " | ".join(d[:4]))
            else:
                ok("served feed is byte-identical to this catalogue",
                   f"{n_got:,} items, auto-fetchable at {base}/feed.xml")
    except Exception as e:
        fail("served /feed.xml loads", repr(e))

    # The promotions feed, fetched on the same schedule, must still be live
    # and must still be inside its own validity window.
    try:
        s_p, _h, body = get(base + "/promotions.xml")
        t = body.decode("utf-8", "replace")
        if s_p != 200:
            fail("served /promotions.xml loads", f"HTTP {s_p}")
        elif "promotion_id" not in t:
            # Google's promotions feed is RSS: one <item> per promotion
            # carrying g:promotion_id, not a <promotion> element.
            fail("promotions feed carries a promotion", t[:160])
        elif "product_applicability" not in t:
            fail("promotion says which products it applies to",
                 "product_applicability is required. all_products is what "
                 "lets one offer cover the catalogue without naming 2,508 "
                 "ids in the product feed.")
        else:
            import datetime as _dt
            m = re.search(r"<(?:g:)?promotion_effective_dates>([^<]+)<", t)
            if not m:
                fail("promotion states its effective dates",
                     "without them Google applies no end date and the offer "
                     "cannot be withdrawn cleanly.")
            else:
                a_s, b_s = m.group(1).split("/")
                start = _dt.datetime.fromisoformat(a_s)
                end = _dt.datetime.fromisoformat(b_s)
                now = _dt.datetime.now(start.tzinfo)
                if not (start <= now <= end):
                    fail("promotion window includes today",
                         f"{a_s} .. {b_s}. A promotion outside its window is "
                         f"disapproved, and the site would still be showing "
                         f"the offer.")
                else:
                    ok("promotions feed is live and inside its window",
                       f"ends {end.date()}, rolls forward on every fetch")
    except Exception as e:
        fail("served /promotions.xml loads", repr(e))

    # 4c. THE BIG ONE. Does each variant URL quote the feed's price?
    rows = F.items(cat, cfg)
    picks = random.sample(rows, min(sample, len(rows)))

    def check_one(r):
        try:
            status, _h, body = get(onbase(r["link"]))
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
        # THREE TRIES, THEN BELIEVE IT. On 28 Oct this check failed one
        # image out of 24 with IncompleteRead; the same URL then served
        # 166,551 identical bytes twelve times in a row and decoded
        # cleanly. The truncation was on this side of the proxy, not in
        # the image. A gate that cries wolf gets ignored, and this one
        # stands between the catalogue and a Google review - so retry the
        # transport, and keep failing on anything that survives it.
        u = onbase(r["image_link"])
        status = h = body = None
        last = None
        for _ in range(3):
            try:
                status, h, body = get(u)
                last = None
                break
            except Exception as e:
                last = e
        if last is not None:
            return f"{r['id']}: image {last!r} (3 attempts)"
        try:
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

    # 4d-bis. The same images, asked for with HEAD.
    #
    # WHY THIS EXISTS. On 28 Oct Merchant Center disapproved 192 items with
    # "Image not processed" while every image downloaded perfectly here. GET
    # was 200 and HEAD was 500: /img/[...path].ts exported GET and nothing
    # else, so Astro answered HEAD with a server error. Crawlers check an
    # image with HEAD before or instead of fetching it, so the route looked
    # broken to Google and healthy to us. A check that only ever sends GET
    # cannot see that, which is the whole point of this one.
    def head_img(r):
        u = onbase(r["image_link"])
        try:
            req = urllib.request.Request(u, method="HEAD",
                                         headers={"User-Agent": UA})
            with urllib.request.urlopen(
                    req, timeout=25,
                    context=ssl.create_default_context()) as resp:
                if resp.status != 200:
                    return f"{r['id']}: HEAD {resp.status}"
                ct = resp.headers.get("content-type", "")
                if not ct.startswith("image/"):
                    return f"{r['id']}: HEAD content-type {ct!r}"
            return None
        except Exception as e:
            return f"{r['id']}: HEAD {e!r}"

    heads = picks[:min(24, len(picks))]
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        probs = [p for p in ex.map(head_img, heads) if p]
    if probs:
        fail("images answer HEAD, not just GET",
             f"{len(probs)} of {len(heads)} failed: " + "; ".join(probs[:4]))
    else:
        ok("images answer HEAD, not just GET", f"{len(heads)} sampled")

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
    ap.add_argument("--base", default=None,
                    help="check this origin instead of https://<domain>. "
                         "For running the live checks against a workers.dev "
                         "deploy before the custom domain is attached - the "
                         "price-match check is worth running early, since it "
                         "is the one that catches what suspended the last "
                         "shop, and waiting for DNS to test it is backwards.")
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
            check_live(cat, cfg, a.sample, a.base)
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
