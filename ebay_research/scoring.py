"""Listing-quality scoring and title construction.

Research is only useful if it ends in a decision.  This module turns a
market corpus into a concrete verdict on one title, and then into a
suggested replacement built from the terms that market actually uses.

The score is deliberately explainable: every point is attributed to a named
component with its own reason string, so a seller can see *why* a title
scored 48 rather than being handed an opaque number.
"""

from __future__ import annotations

from .titles import (
    NOISE_TOKENS,
    caps_ratio,
    detect_attributes,
    keyword_table,
    ngrams,
    repeated_words,
    spam_findings,
    tokenize,
)

MAX_TITLE_LENGTH = 80
IDEAL_MIN_LENGTH = 65

WEIGHTS = {
    "length": 25,
    "keywords": 30,
    "attributes": 20,
    "cleanliness": 15,
    "differentiation": 10,
}


def market_vocabulary(titles, top=30):
    """Ranked phrases for a market, keyed by phrase with its listing share."""
    vocabulary = {}
    for size, limit in ((1, top), (2, max(top // 2, 10))):
        for row in keyword_table(titles, size=size, top=limit, drop_noise=True):
            # Keep the strongest signal when a phrase shows up at two sizes.
            existing = vocabulary.get(row["phrase"])
            if existing is None or row["share"] > existing["share"]:
                vocabulary[row["phrase"]] = {
                    "share": row["share"],
                    "listings": row["listings"],
                    "size": size,
                }
    return vocabulary


def _score_length(title):
    length = len(title or "")
    if length == 0:
        return 0.0, "Title is empty."
    if length > MAX_TITLE_LENGTH:
        return (
            WEIGHTS["length"] * 0.3,
            f"{length} characters — eBay truncates at {MAX_TITLE_LENGTH}. "
            f"Cut {length - MAX_TITLE_LENGTH}.",
        )
    if length >= IDEAL_MIN_LENGTH:
        return (
            WEIGHTS["length"],
            f"{length}/{MAX_TITLE_LENGTH} characters — good use of the space.",
        )
    ratio = length / IDEAL_MIN_LENGTH
    return (
        WEIGHTS["length"] * ratio,
        f"Only {length}/{MAX_TITLE_LENGTH} characters used. "
        f"{MAX_TITLE_LENGTH - length} characters of free search coverage are going to waste.",
    )


def _score_keywords(title, vocabulary):
    if not vocabulary:
        return WEIGHTS["keywords"] * 0.5, "No market corpus to compare against.", [], []
    tokens = tokenize(title, drop_noise=False)
    present = set(tokens) | set(ngrams(tokens, 2))

    ranked = sorted(vocabulary.items(), key=lambda kv: kv[1]["share"], reverse=True)
    covered_weight = 0.0
    total_weight = 0.0
    matched, missing = [], []
    for phrase, meta in ranked[:20]:
        weight = meta["share"]
        total_weight += weight
        if phrase in present:
            covered_weight += weight
            matched.append(phrase)
        else:
            missing.append({"phrase": phrase, "share": meta["share"]})

    coverage = covered_weight / total_weight if total_weight else 0.0
    reason = (
        f"Matches {len(matched)} of the top {min(len(ranked), 20)} phrases buyers "
        f"see in this market ({coverage:.0%} of the weighted vocabulary)."
    )
    return WEIGHTS["keywords"] * coverage, reason, matched, missing[:10]


def _score_attributes(title):
    found = detect_attributes(title)
    hits = sum(1 for value in found.values() if value)
    total = len(found)
    missing = [name for name, value in found.items() if not value]
    reason = f"Declares {hits}/{total} searchable attributes."
    if missing:
        reason += " Missing: " + ", ".join(m.replace("_", " ") for m in missing) + "."
    return WEIGHTS["attributes"] * (hits / total), reason, found


def _score_cleanliness(title):
    findings = spam_findings(title)
    noise = sorted(set(tokenize(title)) & NOISE_TOKENS)
    penalty = min(len(findings) * 0.25 + len(noise) * 0.15, 1.0)
    score = WEIGHTS["cleanliness"] * (1.0 - penalty)
    if not findings and not noise:
        reason = "No filler or hype words — every character is doing work."
    else:
        reason = "Filler found: " + ", ".join(noise) if noise else "Formatting issues found."
    return score, reason, findings


def _score_differentiation(title, vocabulary):
    tokens = set(tokenize(title, drop_noise=True))
    if not tokens:
        return 0.0, "Nothing to differentiate."
    if not vocabulary:
        return WEIGHTS["differentiation"] * 0.5, "No market corpus to compare against."
    generic = {
        phrase
        for phrase, meta in vocabulary.items()
        if meta["size"] == 1 and meta["share"] >= 0.5
    }
    distinct = tokens - generic
    ratio = len(distinct) / len(tokens)
    reason = (
        f"{len(distinct)} of {len(tokens)} words are specific to your item rather "
        "than boilerplate every competitor uses."
    )
    return WEIGHTS["differentiation"] * min(ratio * 1.5, 1.0), reason


def score_title(title, market_titles=None, vocabulary=None):
    """Score one title against a market, 0-100, with an explained breakdown."""
    title = (title or "").strip()
    if vocabulary is None:
        vocabulary = market_vocabulary(market_titles or [])

    length_score, length_reason = _score_length(title)
    keyword_score, keyword_reason, matched, missing = _score_keywords(title, vocabulary)
    attribute_score, attribute_reason, attributes = _score_attributes(title)
    clean_score, clean_reason, findings = _score_cleanliness(title)
    diff_score, diff_reason = _score_differentiation(title, vocabulary)

    total = length_score + keyword_score + attribute_score + clean_score + diff_score

    if total >= 80:
        verdict = "Strong — this title is competitive as written."
    elif total >= 60:
        verdict = "Decent, with clear headroom."
    elif total >= 40:
        verdict = "Weak — it is losing searches to better-written competitors."
    else:
        verdict = "Poor — rewrite it before listing."

    return {
        "title": title,
        "length": len(title),
        "score": round(total, 1),
        "verdict": verdict,
        "caps_ratio": round(caps_ratio(title), 3),
        "repeated_words": repeated_words(title),
        "components": [
            {"name": "Length use", "score": round(length_score, 1),
             "max": WEIGHTS["length"], "reason": length_reason},
            {"name": "Market keywords", "score": round(keyword_score, 1),
             "max": WEIGHTS["keywords"], "reason": keyword_reason},
            {"name": "Attributes", "score": round(attribute_score, 1),
             "max": WEIGHTS["attributes"], "reason": attribute_reason},
            {"name": "Cleanliness", "score": round(clean_score, 1),
             "max": WEIGHTS["cleanliness"], "reason": clean_reason},
            {"name": "Differentiation", "score": round(diff_score, 1),
             "max": WEIGHTS["differentiation"], "reason": diff_reason},
        ],
        "matched_keywords": matched,
        "missing_keywords": missing,
        "attributes": attributes,
        "problems": findings,
    }


def suggest_title(core_terms, market_titles=None, vocabulary=None, max_length=MAX_TITLE_LENGTH):
    """Build a title: your core terms first, then the market's best phrases.

    Greedy packing by phrase value (listing share x phrase length), because on
    eBay every extra matched term is a new search you appear in, and unused
    characters are pure waste.
    """
    if vocabulary is None:
        vocabulary = market_vocabulary(market_titles or [])

    parts = []
    used_tokens = set()

    for term in core_terms or []:
        term = " ".join(str(term).split())
        if not term:
            continue
        tokens = set(tokenize(term))
        if tokens and tokens.issubset(used_tokens):
            continue
        candidate = " ".join(parts + [term])
        if len(candidate) <= max_length:
            parts.append(term)
            used_tokens |= tokens

    ranked = sorted(
        vocabulary.items(),
        key=lambda kv: kv[1]["share"] * (1 + 0.3 * (kv[1]["size"] - 1)),
        reverse=True,
    )
    for phrase, _meta in ranked:
        if phrase in NOISE_TOKENS:
            continue
        tokens = set(tokenize(phrase))
        if not tokens or tokens.issubset(used_tokens):
            continue
        display = phrase.title() if phrase.islower() else phrase
        candidate = " ".join(parts + [display])
        if len(candidate) <= max_length:
            parts.append(display)
            used_tokens |= tokens

    suggestion = " ".join(parts).strip()
    return {
        "title": suggestion,
        "length": len(suggestion),
        "characters_free": max(0, max_length - len(suggestion)),
        "terms_used": parts,
    }


def compare_titles(before, after, market_titles=None):
    """Score two titles against the same market and report the delta."""
    vocabulary = market_vocabulary(market_titles or [])
    first = score_title(before, vocabulary=vocabulary)
    second = score_title(after, vocabulary=vocabulary)
    return {
        "before": first,
        "after": second,
        "delta": round(second["score"] - first["score"], 1),
    }


def audit_listings(listings, top=25):
    """Rank a seller's own listings worst-first so they know what to fix.

    Scoring each listing against the corpus it belongs to means the advice is
    relative to that seller's actual market, not a generic checklist.
    """
    titles = [l.title for l in listings if l.title]
    vocabulary = market_vocabulary(titles)
    rows = []
    for listing in listings:
        if not listing.title:
            continue
        result = score_title(listing.title, vocabulary=vocabulary)
        rows.append(
            {
                "item_id": listing.item_id,
                "title": listing.title,
                "score": result["score"],
                "length": result["length"],
                "price": listing.price,
                "problems": result["problems"][:3],
                "missing_keywords": [m["phrase"] for m in result["missing_keywords"][:5]],
                "url": listing.url,
            }
        )
    rows.sort(key=lambda row: row["score"])
    return rows[:top]
