#!/usr/bin/env python3
"""Would somebody buy this, frame it and hang it up?

Two earlier attempts at this got it wrong in instructive ways.

The first measured whether a phrase contained a word UK buyers search for
and reported that only 25% did. Wrong test: the search words live in the
TITLE - "Funny Bathroom Wall Art Print Framed Poster Gift" - which is how
the listing is found. "Wash your hands" does not need the word "bathroom"
in it.

The second was a growing pile of regexes for notice-board language. It
reached 10% and was by then cutting "WC", "Loo", "Gents" and "Please flush",
which are among the best-selling bathroom prints there are. Same lesson as
the t-shirt illustrations: a rule cannot judge whether something is
desirable.

What a rule CAN find is how the weak lines were made. 2,311 phrases were
written for the thin niches in one sitting, and 49% of them begin with a
word from the end of the line before:

    "Wash your hands"        -> "Hands washed properly"
    "Hands washed properly"  -> "Properly twenty seconds"
    "Take the long way"      -> "Long way round"

That is a chain, and chaining is how you produce volume quickly rather than
how you write something somebody wants on their wall. It is not proof of a
bad line - "Long way round" is a fine motorcycle print - so the chain only
marks a phrase as a suspect. It is cut when it also fails to stand on its
own: three words or fewer, or opening on a connective that only makes sense
as a continuation of the line before.
"""
import re

# words that only make sense carrying on from somewhere else
CONTINUATION = {
    "honestly", "obviously", "actually", "eventually", "finally", "already",
    "anyway", "somehow", "probably", "usually", "definitely", "then",
    "again", "soon", "nearly", "still", "too", "also", "instead", "except",
    "somewhere", "everywhere", "anywhere", "elsewhere", "here", "there",
    "that", "this", "it", "they", "them", "those", "these", "up", "down",
    "off", "back", "only", "just", "more", "less", "after", "before",
    "until", "while", "which", "whatever", "whoever", "because", "since",
    "so", "and", "but", "or", "yet", "however", "therefore", "thus",
}

# a single word only sells when the single word IS the design
SINGLE_OK = {
    "gather", "hygge", "breathe", "welcome", "love", "grateful", "blessed",
    "hello", "cheers", "wander", "bloom", "flourish", "stillness", "serenity",
    "sanctuary", "solitude", "wanderlust", "joy", "hope", "faith", "peace",
    "calm", "dream", "believe", "create", "wonder", "delight", "namaste",
    "bismillah", "alhamdulillah", "shalom", "nest", "hearth", "haven",
    "together", "always", "forever", "courage", "kindness", "gratitude",
    "unwind", "relax", "soak", "rest", "home", "family", "us", "kitchen",
    "pantry", "laundry", "loo", "toilet", "ladies", "gents", "bathroom",
    "garden", "shed", "studio", "workshop", "library", "nursery", "playroom",
    "snug", "bar", "cellar", "garage", "office", "petrolhead", "horsepower",
    "octane", "motorsport", "wc",
}


def words(phrase):
    return re.sub(r"[^A-Za-z0-9' ]", " ", phrase.replace(" / ", " ")).split()


def chained(prev_words, w):
    """Does this line start on a word the previous line just ended with?"""
    return bool(prev_words) and w and w[0].lower() in {
        x.lower() for x in prev_words[-3:]}


def verdict(phrase, prev_words=None):
    """-> (keep: bool, reason: str)"""
    if "{" in phrase:
        return True, "personalised"
    w = words(phrase)
    if not w:
        return False, "empty"
    low = [x.lower() for x in w]
    if len(w) == 1:
        return (True, "single-word format") if low[0] in SINGLE_OK \
            else (False, "one word, not a format")
    if low[0] in CONTINUATION and len(w) <= 3:
        return False, "opens on a connective"
    if chained(prev_words, w):
        if len(w) <= 3:
            return False, "chain link, too short to stand alone"
        if low[0] in CONTINUATION:
            return False, "chain link, opens on a connective"
    return True, "ok"


def filter_file(path):
    """-> (kept lines, [(line, reason)])"""
    head, body = open(path).read().split("---", 1)
    kept, cut, prev = [], [], None
    for line in body.splitlines():
        s = line.strip()
        if not s:
            continue
        ok, why = verdict(s, prev)
        (kept if ok else cut).append(s if ok else (s, why))
        prev = words(s)
    return head + "---\n" + "\n".join(kept) + "\n", cut


if __name__ == "__main__":
    import glob, os, sys
    from collections import Counter
    apply_it = "--apply" in sys.argv
    tot = n_cut = 0
    reasons = Counter(); samples = {"cut": [], "kept": []}
    for f in sorted(glob.glob("banks/niches/*.txt")):
        new, cut = filter_file(f)
        body = new.split("---", 1)[1]
        k = len([l for l in body.splitlines() if l.strip()])
        tot += k + len(cut); n_cut += len(cut)
        for s, why in cut:
            reasons[why] += 1
            if len(samples["cut"]) < 24 and hash(s) % 5 == 0:
                samples["cut"].append(f"{os.path.basename(f)[:-4]:<18} {s}")
        for l in body.splitlines():
            if l.strip() and len(samples["kept"]) < 24 and hash(l) % 97 == 0:
                samples["kept"].append(f"{os.path.basename(f)[:-4]:<18} {l.strip()}")
        if apply_it:
            open(f, "w").write(new)
    print(f"{tot:,} phrases, {n_cut:,} cut ({n_cut/tot:.0%}), {tot-n_cut:,} kept\n")
    for why, c in reasons.most_common():
        print(f"  {c:>5}  {why}")
    print("\n--- a random sample of what is CUT:")
    for s in samples["cut"][:18]:
        print("   ", s)
    print("\n--- a random sample of what is KEPT:")
    for s in samples["kept"][:18]:
        print("   ", s)
