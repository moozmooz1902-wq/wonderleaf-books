#!/usr/bin/env python3
"""Restructure the file to match the seller's known-good upload.

The first test failed on all fifty rows with 21919053, "VariationSpecificsSet
container is required". The seller then supplied a file that uploaded
successfully, and comparing the two field by field shows six differences. The
important one is that my first attempt put the variation set in the wrong
place - pipe-separated in C:Size - when the working file declares it on the
PARENT's RelationshipDetails, semicolon-separated.

Differences applied here, all taken from the working file:

  1. parent RelationshipDetails = "Size=S;M;L;XL;2XL"   (was blank)
  2. parent C:Size              = blank                 (was the pipe list)
  3. size values                = S / M / L / XL / 2XL  (was Small ... XX-Large)
  4. variations repeat *Category, *ConditionID, *Title and every C: specific
  5. variations carry NO CustomLabel, so an order reports the parent SKU -
     which is what the fulfilment tool resolves artwork from anyway
  6. *Location = "Manchester"                           (was "United Kingdom")
"""
import csv, os, collections

csv.field_size_limit(20 << 20)
SRC, TMP = "EBAY_ONE_FILE.csv", "EBAY_ONE_FILE.csv.new"
SIZES  = ["S", "M", "L", "XL", "2XL"]
SETSTR = "Size=" + ";".join(SIZES)
LOCATION = "Manchester"
OLD2NEW = {"Small": "S", "Medium": "M", "Large": "L",
           "X-Large": "XL", "XX-Large": "2XL"}

hdr = open(SRC, newline="", encoding="utf-8").readline().rstrip("\r\n").split(",")
I = {name: i for i, name in enumerate(hdr)}
SPECIFICS = [i for name, i in I.items() if name.startswith("C:") and name != "C:Size"]
I_ACT, I_SKU, I_CAT, I_TITLE = 0, I["CustomLabel"], I["*Category"], I["*Title"]
I_COND, I_REL, I_RD = I["*ConditionID"], I["Relationship"], I["RelationshipDetails"]
I_SIZE, I_LOC = I["C:Size"], I["*Location"]

parents = variations = 0
bad_size = collections.Counter()
with open(SRC, newline="", encoding="utf-8") as f, \
     open(TMP, "w", newline="", encoding="utf-8") as o:
    r = csv.reader(f); w = csv.writer(o, lineterminator="\r\n")
    next(r); w.writerow(hdr)
    cur = None                       # the parent row the variations belong to
    for row in r:
        if (row[I_REL] or "").strip() != "Variation":
            row[I_RD]   = SETSTR     # the parent declares the whole set
            row[I_SIZE] = ""         # and carries no single size
            row[I_LOC]  = LOCATION
            cur = row
            parents += 1
            w.writerow(row); continue

        # the old size label lives in C:Size; map it to the short form
        old = (row[I_SIZE] or "").strip()
        new = OLD2NEW.get(old)
        if new is None:
            bad_size[old] += 1
            new = old
        row[I_ACT]   = ""
        row[I_SKU]   = ""                     # variations carry no SKU
        row[I_CAT]   = cur[I_CAT]
        row[I_TITLE] = cur[I_TITLE]
        row[I_COND]  = cur[I_COND]
        row[I_REL]   = "Variation"
        row[I_RD]    = f"Size={new}"
        row[I_SIZE]  = new
        row[I_LOC]   = ""
        for i in SPECIFICS:                   # repeat every other item specific
            row[i] = cur[i]
        variations += 1
        w.writerow(row)
os.replace(TMP, SRC)
print(f"parents    {parents:,}  (RelationshipDetails = {SETSTR})")
print(f"variations {variations:,}")
print(f"unmapped size labels: {dict(bad_size) or 'none'}")
