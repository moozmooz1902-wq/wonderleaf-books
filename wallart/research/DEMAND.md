# Text & typography wall art: where the demand is (UK first, US second)

Research date: **25 Sep 2026**. Scope: quote and phrase prints, personalised name, family and wedding prints, nursery, scripture, café, kitchen and bathroom signs, motivational, man cave and bar, places. Seller context: 7 eBay UK stores, flat vector typography with small ornaments, A4/A3 unframed, £4.99–£12.99, a target of about 1M listings per store. Store 1 already has 424k wall-art listings, 89% of them near-duplicates, with almost no sales (`pod/analysis/store1_findings.md`).

Machine-readable version: `wallart/research/niche_weights.json` (54 niches, 7 stores, shares sum to 1).
Raw evidence: `wallart/research/raw/ebay_uk_page1_2026-09-25.json` holds 303 eBay UK searches with result counts and the top-10 "X sold" listings for each.

---

## 0. How the numbers were collected, and what they can and can't tell you

| Source | Status | What we got |
|---|---|---|
| **eBay UK search, active listings** (`ebay.co.uk/sch/i.html?_nkw=…&_ipg=120`) | **Worked** (curl with a session cookie; about 15% of requests got 403 and were retried) | **Measured:** result count per term (competition), and the "X sold" counter on page-1 listings. That counter is the lifetime sales of a multi-quantity listing. It is not a 90-day window. |
| eBay UK **sold/completed** (`LH_Sold=1&LH_Complete=1`) | **Blocked**: redirects to sign-in | Not used. No sell-through rates. |
| Etsy UK/US search, market and bestseller pages | **Blocked** (403 on every URL, both curl and fetch) | Only third-party figures (eRank, EtsyHunt, insightagent), labelled as **estimates**. |
| Amazon UK best sellers | **Blocked** (503) | Nothing. |
| Desenio | **Blocked** (429 / TLS reset) | Nothing. |
| Not On The High Street (NOTHS) search | **Worked** | **Measured:** catalogue size per term, the order of the top 15 products (relevance/popularity), and prices. NOTHS does not show sold counts. |
| eBay policy pages, trade-mark and copyright articles, dates | Worked via web search | Cited inline. |

**Caveats that matter.**
- The page-1 "sum of sold" in the raw file includes non-print items that match the words, such as knitting patterns under "knitting print" and printer ink under "brother print". Every figure quoted below names the specific listing, so you can see it really is a print, plaque or sign.
- Where a phrase sells in **thousands** as a wooden or metal **plaque** or a **vinyl sticker**, that proves the *phrase* has demand. It does **not** prove the A4 paper *print* will convert as well. I flag these cases as "phrase-proven, format-unproven".
- Demand scores (1–10) are my judgement, anchored on these measurements. They are not search volumes.

---

## 1. Executive summary

1. **On eBay UK, typography sells when it is personalised or aimed at a gift recipient. Generic décor quotes barely sell.**
   - `personalised word art print`: 42 of 136 page-1 listings show sales. The leaders sell in the high hundreds to 1,640, all at £4.49–£6.99:
     - Song Lyrics LP 1,640
     - OUR SONG 1,335
     - FAMILY TREE 1,127
     - GRADUATION 1,036
     - Family Heart 860
     - HEART Mum/Nanna 699
   - Generic quote searches barely sell:

     | Search | Results | Page-1 listings with sales |
     |---|---|---|
     | `quote print` | 110,000+ | 2 of 120 |
     | `inspirational quote print` | 19,000+ | 2 |
     | `bible verse print` | 13,000+ | **0** |
     | `mental health print` | 36,000+ | **0** |
     | `self love print` | — | **0** |
     | `dictionary definition print` | — | **0** |
     | `star sign print` | — | **0** |
     | `coordinates print` | — | **0** |

   - The US/Etsy-style "minimalist quote décor" market is real (third-party estimate: 50,000+ monthly Etsy searches), but it is **not an eBay UK market**.
2. **"Personalise with your name" wins, and pre-filled names lose.**

   | Search | Results | Page-1 listings with sales |
   |---|---|---|
   | `smith family print` | 1,200+ | **0** of 120 |
   | `olivia name print` | 79 | **0** |
   | `personalised family name print a4` | 413 | 3, with 30 sales in total |

   Every personalised best-seller found is an "ANY NAME" template listing, where the buyer sends the names. Generating millions of pre-filled surname or first-name listings is the same failure mode as the store 1 re-rolls.
3. **The phrases with the biggest measured demand are sign and plaque phrases**:
   - best friend, neighbour and colleague hearts: 7,843 / 6,704 / 1,349 / 1,290 / 1,076 sold
   - personalised home bar: 9,692
   - shed and summer house: 2,063 / 2,239
   - hot tub and caravan rules: 1,477 / 1,172 / 948
   - prosecco humour: 1,864
   - "Christmas at the [Surname]s": 1,504

   All sold at £2.99–£5.99. The A4-print versions of these phrases are **mostly absent**, which makes them both an opening and a risk: the phrase is proven, the paper format is not. Test before scaling, and keep a small plaque or metal-sign product in mind for later.
4. **Top measured non-personalised print demand: educational wall charts.**
   - "2D & 3D Shapes Educational Maths Poster": 1,385 sold at £3.69
   - Periodic Table: 747 and 510
   - Know Your Colours: 489

   These are pure typography and layout, facts are not copyrightable, and there are hundreds of topics.
5. **Strong gifting occasions on eBay UK:**
   - **Teacher thank-you** (1,008 / 596 / 457 / 438 / 353 sold; only 1,600 competing listings)
   - **new baby birth details** (983 / 976)
   - **Mum/Nan** (699 / 541 / 506)
   - **Grandad** (628)
   - **graduation** (1,036)
   - **memorial and pet loss** (Robins Appear A4 print 277; Rainbow Bridge personalised print £16.95, 440)
6. **Religious prints are weak on eBay UK.**
   - Bible verse, Psalm, Lord's Prayer and "bible quote a4" prints: 0 sales on page 1.
   - The best Islamic result is the Ayatul Kursi canvas at 122.
   - Prayer **cards** do sell (Serenity Prayer 320).
   - The faith store should lean on **memorial and comfort**, with scripture as a smaller share and as the Etsy/US cross-list candidate.
7. **Places and dialect: demand is real but it doesn't show on eBay.**
   - Yorkshire, Geordie, Scouse, Scottish and dialect prints: 0 sales on page 1, with 46–2,300 results.
   - Independent UK shops sell these at £12.50+.
   - Railway-poster place prints were earlier measured at 19–27 sold per town.
   - Store 7 is the weakest store on eBay evidence, and the best candidate to cut volume or cross-list to Etsy/NOTHS.

---

## 2. Ranked niche demand (UK, eBay-measured, US noted)

The rank uses measured sold counts of *print or print-equivalent* listings and the ratio of sold-bearing listings to total results. The full list of 54 niches, with phrases, is in the JSON.

| # | Niche | Buyer search terms (UK) | Best measured evidence, eBay UK page 1 | Price seen | Competition (results) |
|---|---|---|---|---|---|
| 1 | Personalised family word-art | personalised family print, personalised word art print, family tree print | Family Tree 1,127; Family Heart 860; Stick Family 543 | £5.99–6.99 | 150,000+ (broad) / 2,900+ (exact) |
| 2 | Teacher / TA / nursery-leaving thank-you | teacher thank you print, teacher gift print, leaving nursery gift | STAR 1,008+; Rainbow 596+/457+; Leaving Nursery A4 438 / 353; A5 budget 231 | £4.29–7.95 | **1,600+** |
| 3 | Our song / your words (buyer text) | personalised song lyrics print, first dance print | 1,640; 1,435; 1,335 | £4.49–6.49 | 39,000+ — **legal risk** |
| 4 | Friendship: best friend, sister, auntie, neighbour, colleague | best friend print, friendship print, neighbour gift, colleague gift | Plaques 7,843 / 6,704 / 1,349 / 1,290 / 1,076; print "Friendship Print Funny Best Friend" 1,222 | £4.99–5.99 | 6,200–7,900 |
| 5 | New baby birth details | personalised baby print, new baby print personalised, baby birth print | 983 / 976; "The Day You Were Born" A4 166 | £5.33–8.99 | 11,000+ |
| 6 | Home bar / pub / beer garden | bar sign, home bar sign, pub sign print, personalised bar sign | Plaques 9,692 / 3,415 / 1,420 / 1,066 / 911 / 900 | £4.99–5.99 | 130,000+ |
| 7 | Mum / Nan / Grandma | mum print personalised, nan print, mothers day print | 699; 541+; 506+; 129+ | £4.95–5.99 | 2,600–9,700 |
| 8 | Educational wall charts | classroom poster, times tables poster, educational poster | Shapes 1,385; Periodic Table 747 / 510; Colours 489 | £3.69 | 8,300+ |
| 9 | Wedding, Mr & Mrs, anniversary | mr and mrs print, wedding anniversary print, paper anniversary | 1st anniv "One Year As Mr & Mrs" 270+ / 188+; Mr & Mrs print 65+ / 62 | £4.95–7.95 | **3,500+** (mr and mrs) |
| 10 | Graduation / retirement / leaving | graduation gift print, retirement gift print, leaving gift | Graduation word art 1,036; Police retirement word art 316; retirement plaque 754 | £3.99–5.99 | 620–2,200 |
| 11 | Dad / Grandad | grandad print, dad print personalised, fathers day print | Grandad word art 628; 589+; 350 | £4.95–6.99 | 1,600–7,600 |
| 12 | Shed / summer house / garden / allotment | shed sign, summer house sign, allotment sign | Plaques 2,239 / 2,063 / 1,529 / 1,316 / 883 / 571 | £2.99–8.90 | **341** (allotment) to 18,000 |
| 13 | Caravan / campervan / hot tub | caravan sign, hot tub sign, caravan rules | Plaques 1,477 / 1,172 / 1,138 / 1,122 / 948 | £3.99–5.99 | **37** ("caravan rules print") |
| 14 | Memorial & sympathy (public-domain poems) | memorial print, sympathy gift, remembrance poem print | Keepsake 1,248; Robins Appear A4 print 277; "Miss Me But Let Me Go" A4 94; Death Is Nothing At All card 468 | £3.99–8.95 | 170–1,100 (exact) |
| 15 | Pet memorial | pet memorial print, rainbow bridge poem, pet loss print | Rainbow Bridge card 965; personalised poem print 440 at **£16.95**; cat print 54 at £16.95 | £4–16.95 | 711–3,500 |
| 16 | Bathroom / loo humour | bathroom wall art funny, toilet sign funny, loo print | Mona Lisa toilet A4 227; Laundry Symbols 198+; set of 3 Nice Butt 178; Wash Your Hands 60+; Poo Room plaque 582 | £3.78–6.99 | 13,000+ / **676** (loo print) |
| 17 | House rules lists | house rules print, bathroom rules print, nanny's house rules | Hot Tub Rules 1,477; Caravan Rules 948; Toilet Rules 404; Nanny's House Rules 221 | £3.99–9.99 | 473–2,100 |
| 18 | Prosecco / gin / wine / coffee humour | prosecco sign, gin print, coffee print | Prosecco plaque 1,864 / 472 / 460; Coffee print 67+ | £4.99 | **402–426** (prosecco) |
| 19 | Man cave / garage (no brands) | man cave sign, garage sign | Man Cave plaque 924; Beer Funny tin 1,107 (brand signs excluded) | £4.45–5.95 | 86,000–180,000 |
| 20 | Christmas family / decor typography | christmas sign, christmas at the sign | "Christmas at the [Surname]" plaques 1,504 / 437 / 279 | £4.95–6.99 | 100,000+ |
| 21 | Birthday age / born-in year | 60th birthday print, 18th birthday print, year you were born | Any-Age word art A4 367; 1966 poster 316 / 181 | £5.99–9.67 | 488–3,500 |
| 22 | Christening / godparents | christening print, godparent gift | Godparent plaques 381 / 225 / 179 | £4.99 | **94** (godparents print) |
| 23 | Pet humour / pet-parent | cat lover gift, dog lover gift, dog print funny | Cat Lady sign 1,262; cat sign 927; dog sign 545; "dog on toilet" A4 by breed 37–71 each | £3.99–4.99 | 8,700–25,000 |
| 24 | New home / address | new home print, personalised new home print | Housewarming print 266+; House Map word art 195; plaque 177 | £5.99–6.99 | 9,700+ |
| 25 | Retro café / menu signs (no brands) | cafe sign, coffee bar sign | Full English tin 647; Herb Garden 335; Coffee Menu 301 | £3.95 | 11,000–35,000 |
| 26 | Nursery name prints | nursery name print, personalised nursery print | 77; 34 on eBay (Etsy much larger: EtsyHunt **estimate** 1,175 total sales for one felt-animal name listing) | £3.45–6.96 | 1,400+ (eBay) / 1.03M listings on Etsy (**third-party**) |
| 27 | Motivational (public-domain) | motivational poster, desiderata print | Desiderata A4 80; Man in the Arena 45; Invictus 36; Churchill 37. "Do it anyway" 223 is copyrighted, see §8 | £4.15–5.99 | 36,000–57,000 |
| 28 | Christian scripture | bible verse print, scripture wall art | **0** prints with sales across 8 searches; Divine Mercy A4 62; framed Lord's Prayer 179 | £3.94–8.50 | 13,000–110,000 |
| 29 | Islamic | islamic print, ayatul kursi print | Ayatul Kursi canvas 122; 99 Names A1 79+; calligraphy canvas 76+ | £9.99–14.89 | **217** (ayatul kursi) |
| 30 | Places / town typography | [town] print | Railway posters 19–27 per town (earlier run); generic "town print" 1 listing with sales | £3.95–16.95 | Tiny per town |
| 31 | Dialect & regional sayings | yorkshire sayings print | **0** on eBay; independent shops sell at £12.50+ | — | 46–2,300 |
| 32 | Minimal décor words | minimalist quote print, typography print | "pink lips... QUOTE UNFRAMED TYPOGRAPHY a4" 216; "be own kind beautiful" 151 | £3.99 | 110,000+ |

**US and Etsy notes. None of these are measured by me; all are third-party estimates.**
- Etsy: "wall art" was the #3 search of 2025, down from #1 in 2024 (eRank).
- In eRank's UK December 2025 top 20, "personalised gift" is #3, "wall art" #17 and "art print" #20.
- Monthly Etsy search estimates (insightagent.app, "January 2026 Etsy sales data"):

  | Niche | Est. monthly searches | Competition |
  |---|---|---|
  | Nursery & kids' art | 140,000+ | — |
  | Minimalist quote prints | 50,000+ | very high |
  | Home décor typography | 45,000+ | — |
  | Personalised name prints | 30,000+ | — |
  | Scripture & faith | 25,000+ | low–medium |

- Etsy Seller Handbook, spring/summer 2026: searches for wall-art décor +110%, gallery prints +80%. Wooden and personalised name signs and personalised nursery décor are among the top Etsy home categories.

For a US push the order shifts: nursery, faith/scripture and minimalist quotes gain; UK "sign humour" (shed, caravan, prosecco) loses.

---

## 3. Evergreen versus seasonal, and when listings must be live

eBay listings index immediately, but Best Match favours listings with sales history. Etsy guidance is 3–6 weeks of "ranking maturation" before peak (listifyai 2026 holiday calendar). **Rule: live 6–8 weeks before the date, with all titles carrying the occasion word.**

| Occasion | 2026/27 date | Must be live by | Niches affected | Evidence |
|---|---|---|---|---|
| Christmas | 25 Dec 2026 (peak buying 20 Nov–14 Dec; Royal Mail last 2nd class ≈ 18 Dec) | **Now to 15 Oct** | Christmas family / "Christmas at the...", Grandad/Dad/Mum gifts, teacher (end of term), first Christmas, pet memorial baubles-to-print | "Christmas at the" plaque 1,504; Grandad "Christmas Present" titles 589+ / 350 |
| Remembrance | 8 Nov 2026 (Sunday), 11 Nov | 1 Oct | PD war poetry | "In Flanders' Fields" print 110 |
| Diwali | 8 Nov 2026 | 1 Oct | dharmic | eBay: 0 sales on page 1 (low) |
| Valentine's | 14 Feb 2027 | 1 Jan | Our song, engagement, couple prints | Song-lyric print titles include "Valentines"; "valentines day print for him" 362 results, 19 with sales |
| Ramadan / Eid al-Fitr | Ramadan ≈ 8 Feb 2027; Eid ≈ 9–10 Mar 2027 | 1 Jan | Islamic | Ramadan stickers 3,333 / 1,453 (decor, not prints); UK orders rise 3–4 weeks before each Eid (neanour.com, **third-party**) |
| **Mothering Sunday (UK)** | **7 Mar 2027** (4th Sunday of Lent) | **15 Jan** | Mum/Nan, family word-art | Mum/Nan titles all carry "Mother's Day"; Etsy: UK peak about 4 weeks before (listifyai) |
| St Patrick's / St David's | 17 Mar / 1 Mar | 1 Feb | Irish, Welsh | low |
| Easter | 28 Mar 2027 | 15 Feb | seasonal decor | eBay "easter print": 3 listings with sales (weak) |
| Eid al-Adha | ≈ 16 May 2027 | 1 Apr | Islamic | — |
| **Father's Day (UK)** | **20 Jun 2027** | **1 May** | Dad/Grandad, man cave, bar, shed, hobbies | Bar/man-cave plaque titles carry "Fathers Day" |
| Graduation | Jun–Jul | 1 May | graduation | 1,036 |
| **Teacher end of year** | UK schools break ≈ 16–23 Jul 2027 (Scotland late Jun) | **15 May** | teacher, nursery-leaving | 1,008 / 596 / 438; 57% of parents buy a teacher gift (Mumsnet via TES) |
| Weddings | May–Sep peak; engagements peak at Christmas and Valentine's | Mar | wedding, anniversary, readings | — |
| Back to school | Sep | 1 Aug | classroom / educational charts | classroom poster 8,300+ results, strong sales |
| New year | Jan | 1 Dec | gym, motivational, office | weak |
| Halloween | 31 Oct | 1 Sep | seasonal decor | "halloween print" 1 listing with sales out of 125 on page 1 — **skip** |

**Evergreen (about 70% of volume):** personalised family and home, new baby, nursery, birthdays, friendship, bathroom/kitchen/house rules, bar/man cave/shed/caravan, memorial and pet memorial, educational charts, places.

---

## 4. Personalisation: size, formats, and pre-filled versus "your name"

**Size.** On page 1 of `personalised print`, 48 of 134 listings show sales, against 2 of 120 for `quote print`. The personalised leaders sell hundreds to 1,640 each. The seller's catalogue has none of this format, and it is where the typography demand on eBay UK sits. UK personalised-gifts market: USD 1.88bn (2024), 7.1% CAGR (DataBridge, **third-party**).

**Formats that sell** (measured, eBay UK page 1):

| Format | Best listing seen | Sold |
|---|---|---|
| Song-lyric / "Our Song" (buyer text) | Personalised Song Lyrics LP Vinyl Record Word Art Print | 1,640 |
| Family tree word-art (names in leaves) | Personalised OUR FAMILY TREE Word Art Print | 1,127 |
| Graduation word-art | Personalised GRADUATION Mortarboard Word Art Print | 1,036 |
| Family heart word-art | Personalised Word Art Print Our Family Heart | 860 |
| Heart word-art for Mum/Nan/Godmother/Sister | Personalised HEART Word Art Print | 699 |
| Grandad word-art | Personalised Grandad Photo Collage Word Art Print | 628 |
| Stick-family typography | Personalised FAMILY Word Art Print Stick Family | 543 |
| Heart map (new home / first met) | Personalised Heart Map Word Art Print | 532 |
| Teacher thank-you (child + teacher name) | Personalised Leaving Nursery... A4 Print | 438 |
| Any-age number word-art | Personalised 16th 18th 21st 30th Any Age Number Word Art Print A4 | 367 |
| Police/occupation word-art | Personalised Police Helmet Word Art Print | 316 |
| 1st anniversary "One Year As Mr & Mrs" | 1st Wedding Anniversary Gift Personalised... Print | 270+ |
| House-warming print | PERSONALISED House Warming Print New Home Gift | 266+ |
| Star map (text) | Personalised Star Map Print | 154+ |
| Nursery name + animals | Personalised Name print a4 cute Jungle/Safari | 77 |

**Formats that do not show demand on eBay UK:** coordinates (0), pre-filled surnames ("smith family print" 0), pre-filled first names ("olivia name print" 0), birth "stats" (0), roman-numeral dates (0), "established" family signs (US-made acrylic at £35–45 sells about 100; UK £8.99 version 9).

**Pre-filled versus personalise-yourself.**
- Every high seller is a template listing that says "ANY NAME" or "Personalised" and takes the text via eBay's personalisation box or buyer message.
- Pre-filled listings target a search nobody types. "Smith Family" is not a query; "personalised family print" is. They also multiply near-identical listings, which is the store 1 duplicate problem again.
- **Recommendation:** personalised templates only. Show sample names in the image and put "Personalised / Any Name / Custom" in the title. Scale by *template design × occasion × recipient × style*, **not** by name.
- This needs an order-time rendering step (buyer text → SVG → print). Budget for it before listing. It is the real bottleneck, and it caps how many personalised listings make sense.
- **A realistic ceiling** is thousands to tens of thousands of distinct personalised templates, not hundreds of thousands. The shares in the JSON count *listings*. For personalised niches, fill them with genuinely different layouts, ornaments and occasions, and stop when the ideas run out. Unused allocation should go to evergreen non-personalised niches (educational charts, rules lists, humour), not to re-rolls.

---

## 5. The religious segment

**Measured, eBay UK:**
- Scripture *prints* barely sell:

  | Search | Results | Page-1 listings with sales |
  |---|---|---|
  | `bible verse print` | 13,000+ | **0** |
  | `psalm print` | 6,200+ | 0 |
  | `psalm 91 print` | 290 | 0 |
  | `the lords prayer print` | 856 | 0 |
  | `bible quote print a4` | 1,200+ | 0 |
  | `john 3 16 print` | 1,300+ | 1 (a John Lennon canvas) |
  | `christian print` | 110,000+ | 3 |

  The best print is "Jesus Divine Mercy Wall Art A4 Print" (62). Prayer **cards and framed small items** sell: Serenity Prayer credit-card size 320 / 264 / 193, "The Lords Prayer – Framed" 179, "Death Is Nothing At All" prayer card 468, "Footprints in the sand" A4 keepsake 684+ (but see §8).
- **Catholic:** Sacred Heart framed print 31; First Holy Communion is mostly cards (104).
- **Irish blessings:** `irish blessing print` 307 results, top 36 (a US wood sign). Celtic blessing keyrings and plaques 114 / 66. Low competition, low demand.
- **Islamic:**
  - Ayatul Kursi canvas 122 (£14.89); 99 Names of Allah A1 poster 79+; abstract calligraphy canvas 76+; Shahada A4 poster 14.
  - `bismillah print` and `mashallah print` show 0 sales.
  - Eid and Ramadan sell as **stickers and banners** (3,333 / 1,453 / 743).
  - Nikah cards and banners 246 / 121.
  - Price points are higher (median £15–30), so UK Muslim buyers look for premium or framed pieces.
  - Third-party (neanour.com): the most popular Islamic gifts are framed calligraphy sets for new homes, weddings and Eid, and there is an order surge 3–4 weeks before each Eid.
- **Hindu/Sikh/Jewish:** effectively no print sales on eBay UK. `diwali decor` 0; `waheguru print` 2 results; `jewish print` 0.

**What to make:**
- **Memorial and comfort texts** are where faith-adjacent demand actually converts: Robins Appear A4 277; Rainbow Bridge personalised print 440 at £16.95; memorial keepsakes 1,248.
- **Scripture:**
  - Short verses in KJV or World English Bible wording: Psalm 23, Jer 29:11, Phil 4:13, Josh 1:9, Prov 3:5–6, Num 6:24–26, 1 Cor 13:4–7, Psalm 46:10, John 3:16, Isaiah 40:31, the Lord's Prayer, the Beatitudes.
  - Also public-domain hymns (Amazing Grace, Be Thou My Vision, It Is Well).
  - Occasions: christening, confirmation and ordination, plus house blessings.
- **Islamic:**
  - Bismillah, Ayat al-Kursi (2:255), Al-Ikhlas, Al-Fatiha, "Verily with hardship comes ease" (94:6), the 99 Names, Alhamdulillah / SubhanAllah / MashaAllah, Eid/Ramadan Mubarak, and Nikah names + date.
  - Arabic + English, using geometric (not figurative) ornaments.
  - **The Arabic must be checked by a native reader.** A misspelled verse is worse than none, and verses of the Qur'an should not be placed in the bathroom/humour stores.
- **UK specifics:** KJV is Crown copyright *in the UK* (see §8). Use WEB/ASV wording or short quotations. The Catholic and Irish diaspora is strongest in NW England, Glasgow and Northern Ireland; Welsh-language blessings (Croeso, Cartref) are a small but uncontested space.
- **US upside:** the scripture/faith Etsy estimate is 25,000+ monthly searches with low–medium competition (third-party). This is the store to cross-list to Etsy/Amazon US first.

---

## 6. Room, hobby and audience niches: demand evidence

| Niche | Verdict | Evidence (eBay UK page 1, measured) |
|---|---|---|
| **Café / coffee / kitchen** | Phrase-proven (stickers), print-weak | Kitchen phrase stickers 3,668 / 2,023 / 1,161 / 1,051 / 966; retro kitchen tin signs 647 / 335 / 301; kitchen *prints* page-1 best 34. `kitchen wall art` 470,000+ results = saturated. NOTHS kitchen prints £10–15 (Put The Kettle On, Chef Was Cute). |
| **Bar / pub / gin / prosecco** | Strong phrases (plaque) | Personalised bar sign 9,692; Funny Bar Sign 3,415; Patient Bartender 1,420; Beer Garden 1,066; Prosecco 1,864; Gin Corner 888. `prosecco print` only 402 results. |
| **Bathroom humour** | Proven as prints | Mona Lisa toilet A4 227; Laundry Symbols 198+; set of 3 Nice Butt 178; Poo Room plaque 582; Toilet Rules 404; Wash Your Hands tin 700. "Animal/dog breed on toilet" A4 prints sell 37–71 each across breeds, which is a repeatable format. |
| **Garage / man cave** | Strong but brand-polluted | Man Cave plaque 924; Beer Funny tin 1,107. Many leaders are brands (Guinness 754, Esso 541, Captain Morgan 480, Only Fools and Horses 407), which carry trade-mark or TV-IP risk. Use generic phrases only. |
| **Shed / garden / allotment / summer house** | Strong (plaque) | 2,239 / 2,063 / 1,529 / 1,316 / 883 / 571; `allotment sign` only 341 results. |
| **Caravan / hot tub** | Strong (plaque), thin competition | 1,477 / 1,172 / 1,138 / 1,122 / 948; `caravan rules print` 37 results. |
| **Office / motivational** | Weak | `office wall art quote`: decals only; `wfh print` 43 results, no prints; `motivational print` 57,000+ results, 4 with sales (Rocky = IP). |
| **Classroom / teacher** | Strong | Teacher thank-you (above); educational posters 1,385 / 747 / 510 / 489; `growth mindset poster` 0 and `reading corner poster` 0 (the fact charts sell, the slogans don't). |
| **Gym** | Weak (IP-driven) | Leaders are Rocky / Ali / Tyson / Arnold (IP). Non-IP: exercise charts 477+. |
| **Nursery / kids** | Medium on eBay, strong on Etsy | New-baby personalised 983 / 976; name prints 77; kids' sets are mostly licensed characters (Spiderman 82+, Stitch, Frozen, Dumbo 408, Pooh 90). |
| **Pets** | Strong for humour and memorial | Cat Lady 1,262; cat sign 927; dog sign 545; pet memorial prints and plaques 440 / 383 / 305; `cat rules print` 0. |
| **Hobbies** | Long tail | Fishing plaque 483; horse-lover signs 1,103 / 473 / 409; golf gifts are mugs and socks; darts is player-branded (IP); cycling, running and horse-riding *prints* near zero. |
| **Friendship / colleague / neighbour** | Very strong phrases | 7,843 / 6,704 / 4,540 / 2,333 / 1,349 / 1,290 / 1,076 (plaques); print version 1,222. |
| **Memorial** | Strong and under-supplied | `bereavement gift print` 170 results, 11 with sales; `remembrance poem print` 284 results, 10 with sales. |

---

## 7. What top sellers do: style, colour, size, titles

**Titles** (verbatim best-sellers). The pattern is *Personalised + FORMAT + key noun + "Word Art Print" + recipient list + occasion list*, filling most of the 80 characters:

```
Personalised OUR FAMILY TREE Word Art Print Gift, Autumn Home Gift Mother's Day          1,127 sold
Personalised HEART Word Art Print Gift Mum Nanna Godmother, Sister, Mother's Day           699 sold
Personalised Leaving Nursery or Pre-School Thank You Gift For Teacher A4 Print             438 sold
Robins Appear When Loved Ones Are Near Memorial Quote Gift A4 Print Frameless              277 sold
Bathroom Print Stinky Toilet Funny Art Poster Picture Wall Art Monalisa A4                 227 sold
be own kind beautiful print a4  picture UNFRAMED typography wall art                       151 sold
2D & 3D Shapes - EDUCATIONAL MATHS POSTER - Numeracy Teaching Resource Revision          1,385 sold
Set of 3 Bathroom Prints Pictures Nice Butt Funny Elephant Zebra UNFRAMED A4               178 sold
```

- A recipient list (Mum Nanna Godmother Sister) and an occasion list (Birthday Christmas Mother's Day) in one title catch several searches with a single listing.
- **"A4", "Unframed" and "Print"** appear in the cheap winners. Honest format words sell at £3.99–£5.99.
- The room word goes in bathroom/kitchen titles (Bathroom, Toilet, Loo, Cloakroom, Downstairs Toilet).
- A colour word helps décor searches (sage, black and white, pink), but **none of the top personalised sellers lead with colour**. Colour is secondary for gifts.

**A suggested title grammar**, per niche type:
- Gift: `Personalised {Format} {Recipient} Print {Occasion1} {Occasion2} Gift A4 Unframed Keepsake`
- Room humour: `Funny {Room} Print {Phrase} {Room synonym} Wall Art A4 Unframed {Colour}`
- Faith/memorial: `{Text name} {Verse/Poem} Print {Memorial/Christian} Gift A4 {Occasion}`

**Visual style** (measured by what the best-sellers show and NOTHS top results; not a survey):
- **"Word art"**: names and words filling a shape (heart, tree, house, mortarboard, record). This is the #1 personalised style on eBay UK and suits a vector pipeline. It needs a word-cloud-into-shape renderer.
- **Clean serif or script + one small ornament** (heart, leaf sprig, star, robin, paw). This matches the "flat vector + small ornament" plan.
- **Black on white or cream**, with sage green, dusty pink and navy as second palettes. Nursery: pastels and rainbow. Bar/man cave: dark background, vintage "tin sign" and retro-pub lettering. Rules lists: marble, nautical or chalkboard themes.
- **Sets of 3** for bathroom and kids (178 and 37–82 sold). Sets are the one legitimate way to raise basket value on eBay.

**Sizes and prices:**
- A4 unframed at **£3.99–£6.99** is where the volume is.
- A5 budget versions exist ("A5 Budget Print – Ideal for Nursery & Multi-Buy", 231 sold at £4.29).
- Premium memorial/pet prints reach £16.95.
- Use **size and colour as eBay variations within one listing** (A5/A4/A3, framed later), not as separate listings (see §8).

---

## 8. Risks

### Copyright: quotes, lyrics, poems

- **Song lyrics:** in copyright for life + 70 years. Publishers (mostly PRS for Music members) monitor marketplaces and file bulk takedowns (copyrightaid.co.uk; shieldmyshop.com). Personalised "Our Song" prints are the #1 selling format measured (1,640 sold), yet printing the lyrics a buyer sends is still reproduction. **Offer "your own words / vows / story" and do not advertise song titles.** If you run lyric prints at all, keep them to one store and treat it as a known risk.
- **Modern poems and quotes to AVOID** (copyrighted or aggressively enforced):
  - "The Dash" (Linda Ellis): letters demanding settlements, per courthousenews.com.
  - "Do It Anyway" / Paradoxical Commandments: © Kent M. Keith 1968, renewed 2001. Often misattributed to Mother Teresa, and sells 223 on eBay under that name.
  - "Footprints in the Sand": authorship disputed and claimed; 684+ sold on eBay, but risky.
  - "She Is Gone" (David Harkins).
  - Captain Corelli's Mandolin reading (de Bernières; sells 128 / 95 on eBay).
  - e.e. cummings "i carry your heart".
  - Dylan Thomas.
  - Tolkien ("Not all who wander").
  - Churchill (d. 1965): his speeches stay in UK copyright until the end of 2035. Avoid long passages, and don't sell "Churchill quotes" posters at scale.
  - Dr Seuss ("Oh the places").
  - The Kohima Epitaph (J.M. Edmonds, d. 1958: UK copyright until end-2028).
  - Winnie-the-Pooh lines: UK copyright ran until end-2026, and Disney holds trade marks on the styling.
  - Any film or TV line: Rocky, Friends, Peaky Blinders, Only Fools and Horses, Disney songs ("Let it go").
- **Treated as public domain.** Rule of thumb for the UK: the author died before 1956.
  - Scripture in KJV (outside the UK), WEB or ASV
  - Shakespeare, Austen, Brontës, Burns, Byron, Browning, Rossetti, Tennyson, Dickens, Carroll, Kipling ("If—"), Henley ("Invictus"), T. Roosevelt ("Man in the Arena")
  - Ehrmann ("Desiderata", d. 1945; PD in the UK since 2016)
  - Henry Scott Holland ("Death is nothing at all")
  - McCrae ("In Flanders Fields"), Binyon ("For the Fallen", d. 1943)
  - "Do not stand at my grave and weep" (Frye) is widely treated as PD because it was never registered. Wikipedia and funeralverses.com treat it that way; this is *not legal advice*.
  - "Rainbow Bridge": origin contested. Medium risk.
- **Bible translations:** NIV and ESV allow up to 500 verses in *literary* works, but require written permission for artwork and products where the verse stands alone (Biblica/ESV terms via search results). **The KJV is under Crown letters patent in the UK** (Cambridge University Press administers it). Short quotations on prints are widely sold, but the safest UK wording is WEB or ASV, or KJV phrasing kept to a few words.

### Trade marks

- **"Keep Calm and Carry On"**: the UK application was originally refused. An EU mark was registered in 2011 to Keep Calm and Carry On Ltd and cloned into a UK mark after Brexit. An invalidation action was underway in 2020 (trademarkdirect.co.uk). **Final status not verified, so avoid the phrase and its parodies.**
- **"Mind the Gap"** and the Underground roundel: TfL owns 400+ registrations and runs an infringement team.
- **"Hakuna Matata"**: Disney, registered 2003.
- **Brands**: Guinness, Esso, Captain Morgan, Starbucks, VW (campervan), football clubs and crests, player names (Luke Littler), the Royal British Legion poppy.
- **"Live Laugh Love"**: no UK registration found in this research, and it sells widely (4,444 as stickers). *Not verified.* Low but non-zero risk.
- **"Gin O'Clock"**: a gin brand uses the name, and registration was not verified. Prefer "Gin Time" or "Ginspiration".
- Check ambiguous phrases on the UKIPO register (and USPTO for the US) before bulk use.

### eBay policy

- **Duplicate listings policy:** eBay forbids more than one fixed-price listing of an identical item from the same seller at the same time. That includes the same item "in different categories" **or "using different usernames"** (ebay.com help page, duplicate-listings policy, fetched). Consequences range from removal to account suspension.
  - **Running the same designs across 7 stores is a policy breach.** Each store must carry genuinely different designs and phrases. This is also why the store plan below gives each store a distinct market.
  - Within a store, colour and size must be **variations** of one listing, not separate listings. The store 1 export shows 668,935 of 669,137 listings are single-SKU with no variations, and 89% share a title with another listing.
- **Selling limits:** new accounts start around 10 items / £500; the UK figure is 5–10 items / £300–500 (webretailer, zikanalytics, third-party). Limits rise monthly with sales and feedback. GTC listings count against the limit.
- **Insertion fees:** about 30–35p per listing beyond the free allowance, with free allowances set by shop tier (Starter £7.95 … Enterprise £2,999.95/month ex VAT). These are third-party figures. I could not load eBay's own UK fee page (JavaScript-rendered), so check the allowance. **At 1M listings per store, fees alone could be up to about £300k/store/month if the allowance doesn't cover them.** Verify before scaling.
- **VeRO:** rights owners report infringing listings directly. The published participant list is not exhaustive, and Disney, sports leagues and music publishers are active. Repeated VeRO removals lead to restrictions, and in a multi-account setup that can bring linked accounts under review.
- **Personalised listings** need buyer-text capture (eBay's personalisation field) and fast custom fulfilment. Late or wrong personalisations are the main source of defects for this format.

---

## 9. Recommended allocation and store plan

### The seven store focuses

Each store sells to a **different buyer and a different search vocabulary**. That keeps stores from competing with each other and keeps them clear of the cross-account duplicate rule. About 64–70% of each store's volume goes to its core market. The rest goes to "diversifier" niches that belong to no other store, so one bad niche or season can't sink a store.

| Store | Name | Core buyer | Core niches (≈65–70%) | Diversifiers (≈30–35%) |
|---|---|---|---|---|
| 1 | **Personalised Couples, Family & Home** | Couples and households buying for themselves or as wedding/house gifts | Family word-art, Mr & Mrs / anniversaries, new home, our words, where-we-met, engagement/Valentine | Christmas family typography, personalised kitchen, surname meaning |
| 2 | **Baby, Nursery & Children** | Parents, grandparents, godparents; also teachers | New-baby birth details, nursery names, christening/godparents, kids' rooms, nursery quotes | **Educational wall charts** (strongest non-personalised demand), kids' affirmations |
| 3 | **Gifts for Them & Milestones** | Gift buyers searching by *recipient* | Mum/Nan, Dad/Grandad, friendship, teacher, birthday age, graduation/retirement | Occupation thank-yous, pet-parent prints |
| 4 | **Funny Home: Bathroom, Kitchen & House Rules** | Home décor buyers searching by *room* | Bathroom humour, house rules, kitchen humour, drinks humour, laundry/hallway | Pet humour, seasonal décor (Christmas first) |
| 5 | **Bar, Man Cave, Garden & Hobbies** | Men's gifts, home-bar and outdoor-space owners | Home bar/pub, man cave/garage, shed/summer house/allotment, caravan/hot tub, hobbies | Retro café menus, gym/sport, games room |
| 6 | **Faith, Memorial & Comfort** | Bereaved and faith buyers; highest price tolerance | PD memorial poems, pet memorial, Christian verses, Islamic, Irish/Celtic, Hindu/Sikh/Jewish | Remembrance (PD war poetry), PD wedding readings and house blessings |
| 7 | **Places, Words & Motivation** | Hometown pride, readers, self-improvers | UK town/county typography, dialect, PD motivational, PD literary | Office/WFH, minimalist décor words, definitions |

**Honest ranking of the stores by eBay-measured demand:** 3 ≈ 1 > 5 ≈ 2 > 4 > 6 > 7.
- **Store 7** has the weakest eBay evidence. Launch it last, cap it well below 1M until something sells, and treat it as the Etsy/NOTHS cross-list catalogue.
- **Store 6** memorial content is strong; its scripture content is weak on eBay UK but is the best US/Etsy cross-list.

### Niche allocation table

"Share" is the fraction of the 7M total, and each store sums to 1/7. Demand is 1–10. "Live in months" shows the months a listing must be active (letters = live, · = can be off). All figures come from `niche_weights.json`.

| Store | Niche | Core / div | Demand 1-10 | Competition | Live in months | Share of 7M | ≈ listings |
|---|---|---|---|---|---|---|---|
| 1 | Personalised family name word-art (family tree, family heart, stick family) (`fam_wordart`) | core | 9 | med | `evergreen` | 2.63% | 184,000 |
| 1 | Mr & Mrs, wedding date and anniversary prints (paper, cotton, silver, golden, any year) (`wedding_anniv`) | core | 8 | med | `JF··MJJAS··D` | 2.30% | 161,000 |
| 1 | New home / first home / address & house-number prints (`new_home`) | core | 7 | med | `··MAMJJAS···` | 1.64% | 115,000 |
| 1 | 'Our song' / first-dance / your-own-words text prints (buyer supplies text) (`our_words`) | core | 9 | med | `JF··MJJAS··D` | 1.48% | 104,000 |
| 1 | Where we met / heart map / coordinates / date & place prints (`where_we_met`) | core | 6 | med | `JF···J··S··D` | 0.99% | 69,000 |
| 1 | Engagement & Valentine's couple prints (`engaged_valentine`) | core | 6 | med | `JF········ND` | 0.82% | 57,000 |
| 1 | Christmas family & 'Christmas at the [Surname]s' typography (seasonal diversifier) (`xmas_family`) | div | 7 | med | `········SOND` | 2.30% | 161,000 |
| 1 | Personalised kitchen & 'X's Kitchen / Nanny's Kitchen' prints (diversifier) (`pers_kitchen`) | div | 5 | med | `·FM·······ND` | 1.48% | 104,000 |
| 1 | Surname meaning / name meaning prints (diversifier) (`surname_origin`) | div | 4 | low | `evergreen` | 0.66% | 46,000 |
| 2 | Personalised new baby birth-details prints (`baby_birth`) | core | 8 | med | `evergreen` | 3.10% | 217,000 |
| 2 | Nursery name prints with small vector animal/ornament (woodland, safari, sea, rainbow) (`nursery_name`) | core | 7 | high | `evergreen` | 2.41% | 169,000 |
| 2 | Kids' bedroom & playroom typography (sets of 3, name + theme, room rules) (`kids_room`) | core | 5 | med | `evergreen` | 1.72% | 120,000 |
| 2 | Christening, baptism, godparent & naming-day prints (`christening`) | core | 6 | med | `··MAMJJAS···` | 1.55% | 108,000 |
| 2 | Nursery quote prints (generic, non-IP) & first-birthday milestone prints (`nursery_quotes`) | core | 5 | high | `evergreen` | 1.20% | 84,000 |
| 2 | Educational typography wall charts (times tables, alphabet, phonics, days, colours, shapes) (`edu_charts`) | div | 8 | med | `J·····JAS···` | 3.44% | 241,000 |
| 2 | Kids' affirmations, growth-mindset & reading-corner posters (diversifier) (`kids_mindset`) | div | 3 | low | `·······AS···` | 0.86% | 60,000 |
| 3 | Mum / Nan / Nanny / Grandma personalised word-art & poems (`mum_nan`) | core | 8 | med | `·FMAM····OND` | 2.13% | 149,000 |
| 3 | Best friend / sister / auntie / neighbour / colleague friendship prints (`friendship`) | core | 8 | high | `evergreen` | 1.82% | 127,000 |
| 3 | Teacher / TA / nursery-leaving thank-you prints (personalised) (`teacher`) | core | 9 | med | `····MJJ····D` | 1.82% | 127,000 |
| 3 | Dad / Grandad personalised prints (`dad_grandad`) | core | 7 | med | `····MJ····ND` | 1.67% | 117,000 |
| 3 | Birthday age & 'year you were born' prints (16th-100th) (`birthday_age`) | core | 6 | med | `evergreen` | 1.37% | 96,000 |
| 3 | Graduation, retirement, leaving & new-job prints (`graduation_retire`) | core | 6 | med | `··M·MJJ····D` | 1.06% | 74,000 |
| 3 | Occupation & carer thank-you prints (nurse, carer, vet nurse, hairdresser, midwife) (diversifier) (`occupation`) | div | 5 | low | `····M······D` | 2.28% | 160,000 |
| 3 | Pet-parent personalised prints (dog mum, pet names, 'the dog's house') (diversifier) (`pet_parent`) | div | 5 | med | `evergreen` | 2.13% | 149,000 |
| 4 | Bathroom / toilet / loo humour typography (`bath_humour`) | core | 7 | high | `evergreen` | 2.86% | 200,000 |
| 4 | House rules / family rules / bathroom rules lists (`house_rules`) | core | 6 | med | `evergreen` | 2.14% | 150,000 |
| 4 | Kitchen & food humour / kitchen typography (`kitchen_humour`) | core | 6 | high | `evergreen` | 1.96% | 137,000 |
| 4 | Prosecco / wine / gin / tea & coffee humour (kitchen & lounge) (`drinks_humour`) | core | 6 | med | `evergreen` | 1.61% | 113,000 |
| 4 | Laundry room, hallway & entryway typography (`laundry_hall`) | core | 5 | med | `evergreen` | 1.25% | 88,000 |
| 4 | Seasonal decor typography: Christmas, Halloween, Easter, autumn (diversifier) (`seasonal_decor`) | div | 5 | high | `·FM····ASOND` | 2.50% | 175,000 |
| 4 | Funny dog & cat typography (diversifier) (`pet_humour`) | div | 6 | med | `evergreen` | 1.96% | 137,000 |
| 5 | Home bar / pub / beer garden signs (personalised '[Name]'s Bar' + funny) (`home_bar`) | core | 8 | high | `···AMJ····ND` | 2.82% | 197,000 |
| 5 | Man cave / garage / workshop typography (no brands) (`man_cave`) | core | 7 | high | `····MJ····ND` | 1.94% | 136,000 |
| 5 | Shed, summer house, garden & allotment typography (`shed_garden`) | core | 7 | med | `··MAMJJ·····` | 1.94% | 136,000 |
| 5 | Caravan, campervan, motorhome & hot-tub typography (`caravan_tub`) | core | 7 | med | `··MAMJJA···D` | 1.59% | 111,000 |
| 5 | Hobby typography: fishing, golf, darts, snooker, cycling, running, knitting, horses (`hobbies`) | core | 5 | med | `····MJ····ND` | 1.59% | 111,000 |
| 5 | Café / coffee bar / diner retro menu typography (no brands) (diversifier) (`cafe_retro`) | div | 5 | high | `evergreen` | 2.12% | 148,000 |
| 5 | Gym, sport & training motivation (no athletes, no film quotes) (diversifier) (`gym_sport`) | div | 4 | high | `J·······S···` | 1.41% | 99,000 |
| 5 | Gaming / games-room typography (no brands or game names) (diversifier) (`games_room`) | div | 4 | med | `··········ND` | 0.88% | 62,000 |
| 6 | Memorial & sympathy poems/verses (public-domain texts only) (`memorial_poems`) | core | 7 | med | `evergreen` | 2.82% | 197,000 |
| 6 | Pet memorial & pet-loss prints (personalised name) (`pet_memorial`) | core | 7 | med | `evergreen` | 2.12% | 148,000 |
| 6 | Christian scripture & prayer prints (KJV/WEB wording) (`christian_verses`) | core | 5 | low | `··MA·······D` | 1.76% | 123,000 |
| 6 | Islamic calligraphy-style & English Islamic typography (Ayat al-Kursi, Bismillah, Nikah, Eid, Ramadan) (`islamic`) | core | 5 | low | `JFMAMJ······` | 1.41% | 99,000 |
| 6 | Irish & Celtic blessings, Scottish/Welsh blessings (`irish_celtic`) | core | 4 | low | `··M········D` | 1.06% | 74,000 |
| 6 | Hindu, Sikh & Jewish typography (Om, Ik Onkar, Diwali, Shalom) (`dharmic_other`) | core | 2 | low | `··MA····SON·` | 0.53% | 37,000 |
| 6 | Wedding readings, house blessings & public-domain love poetry (diversifier) (`wedding_readings`) | div | 4 | low | `··MAMJJA····` | 2.47% | 173,000 |
| 6 | Remembrance & military commemoration (public-domain war poetry) (diversifier) (`remembrance`) | div | 4 | low | `·········ON·` | 2.12% | 148,000 |
| 7 | UK town/city/county typographic prints (name + postcode district + founding/landmark words + small vector ornament) (`place_typo`) | core | 6 | low | `evergreen` | 3.47% | 243,000 |
| 7 | Motivational & inspirational prints from public-domain texts (Desiderata, If-, Invictus, Man in the Arena, Stoic sayings) (`motivational_pd`) | core | 5 | med | `J·······S···` | 2.32% | 162,000 |
| 7 | Regional dialect & sayings (Yorkshire, Geordie, Scouse, Brummie, Lancashire, Black Country, Cockney, Scots, Welsh) (`dialect`) | core | 3 | low | `evergreen` | 1.93% | 135,000 |
| 7 | Literary & book-lover quotes from public-domain authors (Austen, Shakespeare, Wilde, Brontë, Carroll, Dickens, Burns) (`literary_pd`) | core | 4 | med | `evergreen` | 1.35% | 94,000 |
| 7 | Minimalist décor words & Scandi-style quote prints (colour/room-led) (diversifier) (`minimal_decor`) | div | 4 | high | `evergreen` | 2.70% | 189,000 |
| 7 | Office, work-from-home & study motivation (diversifier) (`office_wfh`) | div | 3 | med | `J·······S···` | 1.74% | 122,000 |
| 7 | Dictionary-definition & word-meaning prints (diversifier) (`definitions`) | div | 3 | low | `evergreen` | 0.77% | 54,000 |

| Store | Name | Core share of store | Store share of 7M |
|---|---|---|---|
| 1 | Personalised Couples, Family & Home | 69% | 14.3% |
| 2 | Baby, Nursery & Children | 70% | 14.3% |
| 3 | Gifts for Them & Milestones | 69% | 14.3% |
| 4 | Funny Home: Bathroom, Kitchen & House Rules | 69% | 14.3% |
| 5 | Bar, Man Cave, Garden & Hobbies | 69% | 14.3% |
| 6 | Faith, Memorial & Comfort | 68% | 14.3% |
| 7 | Places, Words & Motivation | 64% | 14.3% |

### How to use these shares without repeating the store 1 failure

1. **The shares are ceilings, not targets.** A niche earns its listings only through genuinely different *phrases or templates*. My suggested cap is **≤ 20 visual variants per phrase or template**, each differing in layout, ornament or typeface, not only palette. Palette and size go into eBay **variations** inside one listing. For example, the ~127k `teacher` allocation is about 6k templates × 20 layouts. If a niche runs out of real ideas, stop and move the remainder to `edu_charts`, `house_rules`, `bath_humour` or `memorial_poems`, which have the deepest phrase banks.
2. **Never list the same design in two stores.** eBay's duplicate policy explicitly covers "different usernames". The niche → store mapping in the JSON is exclusive for that reason.
3. **Test before you scale.**
   - Put 200–500 listings live per core niche for 4–6 weeks.
   - Then cut niches where no listing gets a sale, and scale the ones that do.
   - Plaque-proven phrases (bar, shed, caravan, friendship, prosecco) are the biggest unknowns. The phrase demand is in the thousands, but paper-print conversion is untested.
4. **Launch order by season** (from 25 Sep 2026):
   - Christmas stock now: `xmas_family`, `seasonal_decor`, plus the gift stores 3 and 5.
   - Mothering Sunday / Valentine's / Eid by mid-January.
   - Father's Day / teacher by May.
   - Back-to-school charts by August.
5. **Personalised stores (1, 2, 3) need order-time rendering** before they scale. Budget that first: without it, the strongest measured niches can't be fulfilled.

---

## 10. What I could not verify

- **Sell-through and time windows:** eBay sold-listing search requires sign-in, so the "X sold" figures are lifetime counters on long-running listings. They show *which* things sell, not how fast.
- **Etsy, Amazon UK and Desenio data:** all blocked. Every Etsy volume above (50,000+ minimalist quotes, 140,000+ nursery, 25,000+ scripture, 30,000+ personalised names) is a **third-party estimate** (insightagent.app / EverBee-derived blogs / eRank). I did not measure them.
- **eBay UK shop-tier free-listing allowances** and the exact per-listing insertion fee at 1M listings: the official page didn't render. Third-party sources say about £0.30–0.35.
- **"Keep Calm and Carry On"** UK/EU mark: current validity after the 2020 invalidation action is unknown. Also unverified: "Live Laugh Love" and "Gin O'Clock" registrations, the copyright status of "Rainbow Bridge", "Footprints" and "Miss Me But Let Me Go", and whether KJV Crown rights would ever be enforced against short print quotations.
- **US market:** not measured on eBay.com or Etsy US; the US notes are third-party only.
- **Paper-print conversion of plaque-proven phrases:** unknown until tested.

---

## 11. Sources

**Measured (fetched 25 Sep 2026):**
- eBay UK search pages for the 303 terms listed in `raw/ebay_uk_page1_2026-09-25.json` (URL pattern `https://www.ebay.co.uk/sch/i.html?_nkw=<term>&_ipg=120`).
- NOTHS search pages `https://www.notonthehighstreet.com/search?term=<term>` for: personalised print, quote print, family print, kitchen print, bathroom print, nursery print, wedding print, new home print, teacher print, pet print, bible verse print, map print, town print, christmas print, motivational print.
- Earlier repo research: `pod/RESEARCH_WHAT_SELLS.md`, `pod/RESEARCH_COMPETITORS.md`, `pod/strategy/02_POSTER_RESEARCH.md`, `pod/analysis/store1_findings.md`, `pod/data/poster_niches.json`, `pod/ebay/data/wallart_concepts.json`, `pod/research/ebay_corpus/*` (branch `origin/claude/poster-tshirt-data-research-60x4vg`).

**Third-party / policy / legal:**
- eBay duplicate listings policy: https://www.ebay.com/help/policies/listing-policies/duplicate-listings-policy?id=4255
- eBay selling limits and fees (third-party): https://www.webretailer.com/ebay/what-are-ebay-selling-limits/ · https://www.valueaddedresource.net/ebay-uk-cracks-down-private-sellers-free-listings/ · https://www.baslondigital.com/post/ebay-shop-fees
- eRank: https://help.erank.com/blog/top-etsy-searches-in-2025/ · https://help.erank.com/blog/the-uks-top-etsy-keywords-december-2025/
- Etsy niche estimates: https://www.insightagent.app/guides/best-selling-printable-wall-art-etsy · https://aliciarafieiblog.com/etsy-printables-that-sell/ · https://etsyhunt.com/best-etsy-wall-art
- Etsy trend report (via search summary): https://www.etsy.com/seller-handbook/article/1473931456647
- Holiday listing calendar: https://www.listifyai.net/blog/etsy-holiday-calendar-2026
- Dates: https://ukmothersday.co.uk/uk-mothers-day-2027/ · https://publicholidays.co.uk/eid-al-fitr/ · https://www.awarenessdays.com/awareness-days-calendar/diwali/
- Teacher gifts: https://www.tes.com/magazine/archive/one-10-parents-spends-least-ps25-end-year-gift-teacher
- Islamic décor UK (third-party): https://neanour.com/blogs/news/islamic-wall-art-trends-2025 · https://www.accio.com/business/uk_ramadan_eid_retail_trend_analysis
- UK personalised gifts market (third-party): https://www.databridgemarketresearch.com/reports/uk-personalized-gifts-market
- Keep Calm trade mark: https://blog.trademarkdirect.co.uk/2020/08/trademark-registration-dispute-over.html
- TfL / Mind the Gap: https://www.mondaq.com/uk/trademark/1781124/trade-marks-on-the-move-protecting-london-transport-brands-and-slogans
- Hakuna Matata: https://www.cbc.ca/news/entertainment/disney-trademark-hakuna-matata-1.4957382
- Lyrics copyright: https://copyrightaid.co.uk/forum/viewtopic.php?t=2066 · https://www.shieldmyshop.com/blog/2026-04-09-song-lyrics-movie-quotes-etsy-products-copyright
- Bible copyright: https://www.blueletterbible.org/versions.cfm · https://en.wikipedia.org/wiki/King_James_Version
- The Dash: https://www.courthousenews.com/georgia-supremes-deal-defeat-to-the-dash-poet/
- Paradoxical Commandments: https://www.paradoxicalcommandments.com/permission-to-reprint
- Do Not Stand At My Grave: https://en.wikipedia.org/wiki/Do_Not_Stand_at_My_Grave_and_Weep
- Yorkshire dialect retail: https://thegreatyorkshireshop.co.uk/collections/yorkshire-phrase-prints · https://lighthouselane.co.uk/products/yorkshire-a-z-of-dialect-print
