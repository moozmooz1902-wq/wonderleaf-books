import re, sys, zipfile, xml.etree.ElementTree as ET
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R  = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"

def load(path):
    z = zipfile.ZipFile(path)
    shared = []
    if "xl/sharedStrings.xml" in z.namelist():
        for si in ET.fromstring(z.read("xl/sharedStrings.xml")):
            shared.append("".join(t.text or "" for t in si.iter(NS + "t")))
    rels = {}
    for rel in ET.fromstring(z.read("xl/_rels/workbook.xml.rels")):
        rels[rel.get("Id")] = rel.get("Target").lstrip("/")
    sheets = []
    for sh in ET.fromstring(z.read("xl/workbook.xml")).iter(NS + "sheet"):
        t = rels[sh.get(R + "id")]
        sheets.append((sh.get("name"),
                       t if t.startswith("xl/") else "xl/" + t))
    out = {}
    for name, target in sheets:
        rows = []
        for row in ET.fromstring(z.read(target)).iter(NS + "row"):
            cells = {}
            for c in row.iter(NS + "c"):
                ref = c.get("r") or ""
                col = re.match(r"[A-Z]+", ref)
                col = col.group(0) if col else ""
                v = c.find(NS + "v")
                isel = c.find(NS + "is")
                if c.get("t") == "s" and v is not None:
                    val = shared[int(v.text)]
                elif isel is not None:
                    val = "".join(t.text or "" for t in isel.iter(NS + "t"))
                elif v is not None:
                    val = v.text
                else:
                    val = ""
                if val not in (None, ""):
                    cells[col] = str(val).strip()
            rows.append(cells)
        out[name] = rows
    return out

def cols(cells):
    def idx(c):
        n = 0
        for ch in c:
            n = n * 26 + (ord(ch) - 64)
        return n
    return [cells[k] for k in sorted(cells, key=idx)]
