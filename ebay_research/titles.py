"""Title analysis: the heart of eBay keyword research.

An eBay title is 80 characters of search real estate.  What is in it decides
whether an item is found at all, so most of the useful research questions are
really questions about titles:

* Which words do the listings in this market actually use?
* Which words separate the sellers who move stock from the ones who don't?
* Is my title wasting space on noise ("L@@K", "WOW", "FREE POST") instead of
  the attributes buyers search for?

Everything here is pure Python over lists of strings -- no API, no pandas --
so it is fast, testable, and reusable on any corpus of titles.
"""

from __future__ import annotations

import math
import re
from collections import Counter

# Words that carry no search value in an eBay title.
STOPWORDS = frozenset(
    """
    a an and are as at be but by for from in into is it its of on or the to
    with your you my our this that these those all any can will your
    """.split()
)

# Filler that eats title characters without matching what buyers type.
NOISE_TOKENS = frozenset(
    """
    look wow rare hot sale best top quality cheap bargain must see item items
    ebay uk fast free post postage shipping delivery brand bnwt bnib genuine
    original authentic amazing perfect nice lovely great good excellent super
    l00k
    """.split()
)

SPAM_PATTERNS = [
    (re.compile(r"l@@k", re.I), "Uses 'L@@K' — a dead giveaway of an old-style listing and matches nothing."),
    (re.compile(r"!{2,}"), "Repeated exclamation marks waste characters."),
    (re.compile(r"[\*★☆►♦~]{2,}"), "Decorative symbols are not searchable."),
    (re.compile(r"\b(wow|look|must see|bargain)\b", re.I), "Hype words are not search terms."),
    (re.compile(r"\bfree (p&p|post|postage|shipping|delivery)\b", re.I), "Shipping terms belong in the postage settings, not the title."),
    (re.compile(r"\b(l@@k|xxx|!!!)\b", re.I), "Attention-grabbing filler."),
]

COLOURS = frozenset(
    """
    black white red blue green yellow pink purple grey gray brown orange
    beige cream navy silver gold bronze teal turquoise burgundy maroon ivory
    charcoal khaki lilac mint coral rose tan multicoloured multicolour
    """.split()
)

CONDITION_WORDS = frozenset(
    """
    new used vintage antique refurbished sealed unopened preowned pre-owned
    boxed unboxed mint nwt nwot spares repair faulty
    """.split()
)

SIZE_PATTERN = re.compile(
    r"\b(?:size\s*)?(?:xxs|xs|s|m|l|xl|xxl|xxxl|\d{1,3}(?:\.\d)?\s*(?:cm|mm|inch|in|\"|ft|kg|g|ml|l|oz|lb))\b",
    re.I,
)
YEAR_PATTERN = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")
MODEL_PATTERN = re.compile(r"\b(?=[a-z0-9-]*\d)(?=[a-z0-9-]*[a-z])[a-z0-9-]{3,}\b", re.I)
QUANTITY_PATTERN = re.compile(r"\b(\d+)\s*(?:x|pack|pcs|pieces|set)\b", re.I)

_TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9'&+/.-]*", re.I)


def normalise(title):
    """Lowercase and collapse whitespace, preserving in-word punctuation."""
    return re.sub(r"\s+", " ", (title or "").strip().lower())


def tokenize(title, drop_stopwords=True, drop_noise=False, min_length=2):
    """Split a title into comparable tokens."""
    tokens = []
    for match in _TOKEN_RE.finditer(normalise(title)):
        token = match.group(0).strip("-.'/&+")
        if len(token) < min_length and not token.isdigit():
            continue
        if drop_stopwords and token in STOPWORDS:
            continue
        if drop_noise and token in NOISE_TOKENS:
            continue
        tokens.append(token)
    return tokens


def ngrams(tokens, n):
    """All contiguous n-grams as space-joined strings."""
    if n <= 0 or len(tokens) < n:
        return []
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def phrase_counts(titles, sizes=(1, 2, 3), drop_noise=False):
    """Map ``n -> Counter`` of phrase frequencies across a corpus of titles."""
    result = {n: Counter() for n in sizes}
    for title in titles:
        tokens = tokenize(title, drop_noise=drop_noise)
        for n in sizes:
            result[n].update(ngrams(tokens, n))
    return result


def keyword_table(titles, size=1, top=40, drop_noise=False):
    """Rank phrases by how many listings use them.

    Document frequency ("how many listings contain this") is far more useful
    than raw frequency: a word repeated three times in one title should not
    outrank a word that appears in a hundred separate listings.
    """
    total = len([t for t in titles if t])
    if not total:
        return []
    doc_freq = Counter()
    raw_freq = Counter()
    for title in titles:
        tokens = tokenize(title, drop_noise=drop_noise)
        grams = ngrams(tokens, size)
        raw_freq.update(grams)
        doc_freq.update(set(grams))
    rows = []
    for phrase, docs in doc_freq.most_common(top):
        rows.append(
            {
                "phrase": phrase,
                "listings": docs,
                "share": round(docs / total, 4),
                "occurrences": raw_freq[phrase],
            }
        )
    return rows


def distinctive_terms(target_titles, background_titles, size=1, top=25, min_count=3):
    """Terms over-represented in ``target`` versus ``background``.

    Uses the log-odds ratio with an informative Dirichlet prior (Monroe et
    al.), which is the standard fix for the two ways naive frequency counts
    mislead: very common words dominating, and very rare words spiking on a
    single occurrence.  Positive z-scores mean "distinctive to the target".

    This is the engine behind gap analysis -- point it at sold items versus
    active listings and it tells you which words the market rewards.
    """
    target = Counter()
    background = Counter()
    for title in target_titles:
        target.update(ngrams(tokenize(title), size))
    for title in background_titles:
        background.update(ngrams(tokenize(title), size))

    combined = target + background
    total_target = sum(target.values())
    total_background = sum(background.values())
    alpha_zero = sum(combined.values())
    if not total_target or not total_background or not alpha_zero:
        return []

    scored = []
    for term, prior in combined.items():
        if combined[term] < min_count:
            continue
        y_t = target.get(term, 0) + prior
        y_b = background.get(term, 0) + prior
        denom_t = total_target + alpha_zero - y_t
        denom_b = total_background + alpha_zero - y_b
        if denom_t <= 0 or denom_b <= 0 or y_t <= 0 or y_b <= 0:
            continue
        delta = math.log(y_t / denom_t) - math.log(y_b / denom_b)
        variance = 1.0 / y_t + 1.0 / y_b
        z = delta / math.sqrt(variance)
        scored.append(
            {
                "phrase": term,
                "z_score": round(z, 3),
                "target_count": target.get(term, 0),
                "background_count": background.get(term, 0),
            }
        )
    scored.sort(key=lambda row: row["z_score"], reverse=True)
    return scored[:top]


def caps_ratio(title):
    """Share of alphabetic characters that are uppercase."""
    letters = [c for c in (title or "") if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)


def repeated_words(title):
    """Words used more than once — wasted characters on eBay."""
    counts = Counter(tokenize(title))
    return sorted(word for word, count in counts.items() if count > 1)


def detect_attributes(title):
    """Which buyer-facing attributes a title actually declares.

    eBay's search ranks on matched item specifics, and buyers filter on them.
    A title missing size/colour/condition is invisible to a whole class of
    searches, and this is the cheapest possible check for that.
    """
    text = normalise(title)
    tokens = set(tokenize(title))
    return {
        "colour": bool(tokens & COLOURS),
        "condition": bool(tokens & CONDITION_WORDS),
        "size_or_measure": bool(SIZE_PATTERN.search(text)),
        "year": bool(YEAR_PATTERN.search(text)),
        "model_or_code": bool(MODEL_PATTERN.search(text)),
        "quantity": bool(QUANTITY_PATTERN.search(text)),
    }


def spam_findings(title):
    """Human-readable problems found in a single title."""
    findings = []
    seen = set()
    for pattern, message in SPAM_PATTERNS:
        if pattern.search(title or "") and message not in seen:
            findings.append(message)
            seen.add(message)
    if caps_ratio(title) > 0.7 and len([c for c in title if c.isalpha()]) > 12:
        findings.append("Mostly uppercase — eBay treats it the same but buyers read it as shouting.")
    duplicates = repeated_words(title)
    if duplicates:
        findings.append(
            "Repeated words waste characters: " + ", ".join(duplicates[:5])
        )
    return findings


def title_stats(titles):
    """Corpus-level shape of the titles: length, words, caps, noise."""
    usable = [t for t in titles if t]
    if not usable:
        return {
            "count": 0,
            "avg_length": 0.0,
            "avg_words": 0.0,
            "pct_using_full_length": 0.0,
            "avg_caps_ratio": 0.0,
            "pct_with_noise": 0.0,
        }
    lengths = [len(t) for t in usable]
    words = [len(tokenize(t, drop_stopwords=False)) for t in usable]
    noisy = sum(1 for t in usable if set(tokenize(t)) & NOISE_TOKENS)
    long_enough = sum(1 for length in lengths if length >= 70)
    return {
        "count": len(usable),
        "avg_length": round(sum(lengths) / len(lengths), 1),
        "median_length": sorted(lengths)[len(lengths) // 2],
        "avg_words": round(sum(words) / len(words), 1),
        "pct_using_full_length": round(long_enough / len(usable), 4),
        "avg_caps_ratio": round(sum(caps_ratio(t) for t in usable) / len(usable), 3),
        "pct_with_noise": round(noisy / len(usable), 4),
    }
