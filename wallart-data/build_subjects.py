#!/usr/bin/env python3
"""Assemble gen/subjects.json from the subject modules.

The pod is sent the subject LISTS, not the expanded job grid: 284,665 jobs is
several megabytes of base64 inside a pod's start command and curl refuses it
with "Argument list too long". The pod expands the grid itself with the same
code, so this file and gen_gated.py must agree exactly - which they do by
both importing prompts.py.

The seed is fixed. Nothing here is random; the shuffle that mixes subjects
across the upload order is the SKU hash sort inside expand().
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "subjects"))

import places_uk, places_world, creatures, botanical          # noqa: E402
import celestial, stilllife, architecture                     # noqa: E402

OUT = os.path.join(HERE, "gen", "subjects.json")

data = {
    "place": places_uk.ALL + places_world.ALL,
    "creature": creatures.ALL,
    "botanical": botanical.ALL,
    "celestial": celestial.ALL,
    "stilllife": stilllife.ALL,
    "architecture": architecture.ALL,
    "seed": 101,
    "prefix": "WA",
}

# A subject that appears under two kinds is two different prompts and two
# different SKUs, so it is allowed - but a subject repeated inside one kind
# is the same SKU twice and would stop the run.
for k, v in data.items():
    if isinstance(v, list):
        dupes = [x for x in set(v) if v.count(x) > 1]
        assert not dupes, f"{k} repeats {dupes[:5]}"

if __name__ == "__main__":
    json.dump(data, open(OUT, "w"), indent=0)
    tot = sum(len(v) for v in data.values() if isinstance(v, list))
    for k, v in data.items():
        if isinstance(v, list):
            print(f"{k:<14}{len(v):>7,}")
    print(f"{'TOTAL':<14}{tot:>7,}  ->  {OUT}")
