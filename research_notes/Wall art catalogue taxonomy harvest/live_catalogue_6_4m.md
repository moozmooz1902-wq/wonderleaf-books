# The live Fy! catalogue — all 6,448,043 of it

Built from Fy!'s own sitemaps, which they publish openly (their `robots.txt`
points agents at an `agents.md` and an MCP endpoint, so this is invited access,
not scraping round a blocker). **Free, and it took five minutes.**

The manifest holds one row per image: URL, title, source sitemap. It is
resumable — every sitemap processed is recorded, so the job can be killed and
restarted without losing or repeating work.

| | |
|---|---|
| Images manifested | **6,448,043** |
| Carrying a title | **3,582,363** |
| **Distinct titles** | **607,667** |
| Repeat rate | **83.0%** |

**The MEGA dump held 297,912 Fy! listings. The live catalogue is 21× that.**
Anything Fy!-specific in the earlier notes is superseded by this.

---

## Their 6.4 million products are about 608,000 designs

83% of titles are repeats of each other. A design is listed roughly **ten
times over** — different frame colours and sizes as separate products rather
than variations inside one listing.

That is worth sitting with. The headline "millions of designs" on these sites
is mostly listing multiplication, not drawing. Our plan already does the
opposite — sizes and frames as variations inside one listing — which means a
smaller, cleaner catalogue reaching the same SKU count.

---

## They resell public-domain archive material at scale

This is a whole business line I had not seen, and it needs no generation at
all.

**Russell Lee photographs — 15,065 listings.** US Farm Security Administration
documentary photography from the 1930s-40s. Federal government works, so
public domain.

> *Schoolchildren Jumping Rope, San Augustine, Texas By Russell Lee*
> *Cotton Pickers, Lehi, Arkansas By Russell Lee*
> *Mr, Leatherman Hitching Up His Burros, Pie Town, New Mexico By Russell Lee*

**Pierre-Joseph Redouté — 8,145 listings.** The botanical illustrator, died
1840, firmly out of copyright. Scanned plates from *Les Liliacées* and the rose
books, sold as prints.

**And they did not clean the archive metadata — 4,800 listings still carry the
Library of Congress's own cataloguing language:**

> *Untitled Photo, Possibly Related To Grandmother And Child, Southeast
> Missouri Farms By Russell Lee*

"Untitled Photo, Possibly Related To" is a LoC finding-aid phrase, not a title.
They bulk-imported an archive and listed the field as-is. It is sloppy, it is
visible to buyers, and it is a quality gap we can simply not have.

**The British equivalents are better for a UK audience and equally free**: the
Wellcome Collection, the Biodiversity Heritage Library, the British Library's
Flickr Commons release, Historic England's archive, out-of-copyright Ordnance
Survey mapping, and the Victorian natural-history plate tradition. Zero
generation cost, zero GPU, and a far stronger fit than Depression-era Texas for
someone buying in Britain.

---

## Three more templates, all running worldwide and skipping Britain

**`{PLACE} Stone Park Bauhaus Minimalist` — 5,660 listings.** Channel Islands,
Everglades, North Cascades, Nahuel Huapi, Sunderbans, Lake Bogoria, Selous,
Harare, Tabuk, Animas River. National parks and wild places worldwide rendered
as flat Bauhaus geometry.

The only British entry is the Channel Islands. We hold **15 National Parks and
46 National Landscapes**, and critically — **Bauhaus minimalist is vector
geometry, so this template is procedural, not diffusion.** Free to produce,
pixel-perfect, unlimited.

**`Affiche de voyage {PLACE}` — 5,525 listings, in French.** Saint-Malo,
Zugspitze, Switzerland, Irlande, Saint-Étienne, Bhutan, Rocky Mountain National
Park. So they do run a French-language line, and it is a straight translation
of the travel-poster template.

This qualifies the earlier language finding. The corpus is still >99% English,
but French is not noise — it is **one deliberate template**, and a cheap one to
copy, since the artwork is identical and only the caption changes. The same
would hold for German or Spanish if those markets are ever worth having.

**`Ohara Koson Inspired Bird Painting` — 5,335 listings.** Koson died in 1945,
so safely out of copyright. One pre-1956 printmaker, run to depth, on one
subject. The pattern generalises to any cleared artist: Redouté for botany,
Hokusai and Hiroshige for landscape, Audubon for birds, Haeckel for marine
life, Mucha for decorative figures.

---

## What this changes

1. **Add an archive line.** Public-domain British collections, properly
   catalogued and cleanly titled, at zero generation cost. They have proved
   the demand and left the quality on the table.
2. **The Bauhaus park template goes to the procedural renderer**, not the GPU.
3. **"Inspired by {cleared artist}" is a template, not a one-off** — pick six
   pre-1956 names and run each to depth across its natural subject.
4. **608,000 distinct designs is the real competitive benchmark**, not 6.4
   million. That is a number we can reach.
5. **A French caption line is nearly free** — same artwork, translated text —
   if we ever want it.

---

## Honest limits

- **Fy! only.** Displate's sitemap index returned 403 to the Python client
  (it answered curl earlier), so Displate is not in this manifest. Its
  non-licensed catalogue is roughly 1.5-2.5M images and remains to be added.
- Counts are of **listings carrying a title in the sitemap**; 2.87M images have
  no title there and are uncounted in the text figures.
- Nothing here measures sales. It measures what Fy! chose to list.
