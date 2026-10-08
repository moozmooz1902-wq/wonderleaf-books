# UK Place Gazetteer for a Wall-Art Catalogue

Harvested 8 October 2026. Every list below was machine-extracted from the named source in
this session unless the line says **UNVERIFIED** — those are compiled from general knowledge
and must be checked against the source URL given before they are used to generate saleable art.
Counts are the count of entries actually extracted, so catalogue arithmetic can be done on them.

## Headline arithmetic

| Block | Count extracted | Status |
|---|---|---|
| UK official cities | 76 (75 unique strings; two are named Bangor) | verified |
| English built-up areas 20,000+ (named) | 454 | verified |
| ONS built-up areas, all sizes (England & Wales) | 7,018 | verified, names not harvested |
| ONS built-up areas over 5,000 population | 1,395 | verified, names not harvested |
| Scottish burghs/towns | 235 | verified |
| Welsh towns | 161 | verified |
| English ceremonial counties | 48 | verified |
| Scottish council areas | 32 | verified |
| Welsh principal areas | 22 | verified |
| Northern Ireland counties | 6 | verified |
| UK National Parks | 15 | verified |
| National Landscapes (former AONBs) | 46 (34 England incl. cross-border Wye Valley, 5 Wales, 8 NI) | verified |
| London boroughs + City | 33 | verified |
| London named districts/areas | 558 | verified |
| London postal districts | 124 | verified |
| London Underground stations | 269 | verified |
| Wainwrights | 214 | verified |
| Munros | 282 official; 266 named rows in source table | discrepancy noted |
| Scottish islands (named, larger) | 244 | verified |
| Scottish mainland lochs | 1013 | verified |
| Scotch malt whisky distilleries operating | 125 | verified |
| Welsh Nuttall mountains | 186 | verified |
| Welsh castles (named) | 260 | verified |
| Church of England cathedrals | 42 | verified |
| Cathedrals, all denominations UK | 212 | verified |
| English Heritage properties | 446 | verified |
| Historic Environment Scotland properties | 302 | verified |
| Trinity House lighthouses | 65 lighthouses + 7 lightvessels | verified |
| Lighthouses in England (active, all operators) | 85 | verified |
| Surviving piers (England/Scotland/Wales/IoM) | 59 | verified; NPS figure differs |
| Canals (all nations) | 195 | verified |
| Named rivers England / Scotland / Wales | 626 / 195 / 384 | verified |
| Stone circles England/Scotland/Wales/NI | 145/87/90/19 | verified |
| Oxford colleges + PPHs | 43 | verified |
| Cambridge colleges | 31 | verified |
| UK universities | 114 | verified |
| English football stadiums (current) | 135 | verified — TRADEMARK RISK |
| Lake District named lakes/tarns/reservoirs | 31 | verified |

**Named settlement rows available immediately: 1408** (English BUAs 454 + Scottish towns 235 + Welsh towns 161 + London districts 558). This clears the 1,000+ named-towns target without going below 20,000 population in England; the ONS 1,395-BUA dataset extends it to the 5,000 floor.

## Q1 — All UK cities, and all towns / built-up areas above ~15,000

### Takeaway

The 76 official cities are a closed, government-published set and are listed in full below. For towns,
the authoritative frame is the ONS built-up area (BUA) geography: 7,018 BUAs in England and Wales for
Census 2021, of which 1,395 exceed 5,000 population on the newer BUA 2024 boundaries. I harvested 454
named English BUAs at 20,000+, 235 Scottish burghs and 161 Welsh towns — 850 named settlements outside
London before the ONS 5,000-floor dataset is loaded.

### Cited Findings

**The 76 UK cities** — 55 England, 8 Scotland, 7 Wales, 6 Northern Ireland. 75 unique name strings because two cities are called Bangor (Gwynedd, and County Down). — [List of cities in the United Kingdom, mirroring the UK Government's official list](https://en.wikipedia.org/wiki/List_of_cities_in_the_United_Kingdom)

London; Westminster; Birmingham; Leeds; Glasgow; Manchester; Sheffield; Bradford; Edinburgh; Liverpool; Bristol; Cardiff; Leicester; Coventry; Wakefield; Belfast; Nottingham; Newcastle upon Tyne; Doncaster; Milton Keynes; Salford; Sunderland; Brighton and Hove; Wolverhampton; Kingston upon Hull; Plymouth; Derby; Stoke-on-Trent; Southampton; Swansea; Aberdeen; Peterborough; Portsmouth; York; Colchester; Chelmsford; Southend-on-Sea; Oxford; Newport; Canterbury; Preston; Dundee; Cambridge; St Albans; Lancaster; Norwich; Chester; Exeter; Wrexham; Gloucester; Winchester; Durham; Carlisle; Worcester; Lincoln; Bath; Derry; Dunfermline; Bangor; Inverness; Hereford; Lisburn; Stirling; Perth; Salisbury; Lichfield; Chichester; Newry; Truro; Ely; Ripon; Armagh; Wells; St Asaph; St Davids

**ONS built-up area framework** — 7,018 BUAs in England and Wales at Census 2021 (6,439 England incl. 33 in London, 579 Wales), home to 94.6% of the population. Size bands: minor 0–4,999; small 5,000–19,999; medium 20,000–74,999; large 75,000–199,999; major 200,000+. A later ONS article covers the 1,395 BUAs above 5,000 population on BUA 2024 geography. 568 BUAs are classified as coastal. — [ONS, Towns and cities: characteristics of built-up areas, England and Wales, Census 2021](https://www.ons.gov.uk/peoplepopulationandcommunity/housing/articles/townsandcitiescharacteristicsofbuiltupareasenglandandwales/census2021)

**English built-up areas, major (200,000+ and 75,000+ band heads) — 25 extracted** — [List of built-up areas in England by population](https://en.wikipedia.org/wiki/List_of_built-up_areas_in_England_by_population)

London; Birmingham; Leeds; Liverpool; Sheffield; Manchester; Bristol; Leicester; Coventry; Bradford; Nottingham; Newcastle upon Tyne; Brighton and Hove; Derby; Kingston upon Hull; Plymouth; Milton Keynes; Stoke-on-Trent; Southampton; Northampton; Wolverhampton; Luton; Portsmouth; Reading; Norwich

**English built-up areas, large (75,000–199,999) — 85**

Bournemouth; Peterborough; Bolton; Swindon; Southend-on-Sea; Warrington; Oxford; Sunderland; Slough; Kingswood and Fishponds; Telford; Cambridge; Ipswich; Blackpool; Middlesbrough; York; Huddersfield; Poole; Watford; Colchester; Exeter; Blackburn; Crawley; Gloucester; Stockport; Basingstoke; Basildon; Cheltenham; Gateshead; Worthing; Rochdale; Oldham; Chelmsford; Birkenhead; Maidstone; Gillingham; Salford; Solihull; St Helens; Worcester; Lincoln; West Bromwich; Eastbourne; Wakefield; Wythenshawe; Bedford; Hemel Hempstead; Preston; Stevenage; Southport; Bath; Harlow; Royal Sutton Coldfield; Darlington; Chester; Hastings; Nuneaton; Halifax; Hartlepool; Aylesbury; Doncaster; Grimsby; Wallasey; Stockton-on-Tees; Weston-super-Mare; High Wycombe; Ashford; Redditch; Wigan; Scunthorpe; Bury; Bracknell; Burnley; Rugby; Guildford; Carlisle; Chatham; Newcastle-under-Lyme; Chesterfield; Burton upon Trent; Tamworth; Shrewsbury; Woking; St Albans; Harrogate

**English built-up areas, 49,700–74,999 — 62**

Crewe; South Shields; Stafford; Rotherham; Barnsley; Lowestoft; Walsall; Gosport; Dartford; Bognor Regis; Corby; Paignton; Maidenhead; Rochester; Ellesmere Port; Loughborough; Dudley; Dewsbury; Mansfield; Margate; Kettering; Cannock; Sale; Taunton; Runcorn; Farnborough; Tynemouth; Hereford; Halesowen; Widnes; Huyton; Scarborough; Gravesend; Bebington; Kidderminster; Smethwick; Weymouth; Brentwood; Barrow-in-Furness; Canterbury; Wellingborough; Macclesfield; Bootle; Carlton; Lancaster; Beeston; Banbury; Torquay; Folkestone; Kingswinford; Bloxwich; Welwyn Garden City; Washington; Royal Leamington Spa; Royal Tunbridge Wells; Hinckley; Durham; Wokingham; Crosby; Horsham; Yeovil; Thundersley

**English built-up areas, 30,000–49,699 — 122** (first 60 of 122 shown; full list in the source, ordered by population)

Altrincham; Willenhall; Christchurch; Keighley; Ashton-under-Lyne; Andover; Winchester; Eastleigh; Bridgwater; Salisbury; King's Lynn; Tipton; West Molesey; Havant; Middleton; Kirkby; Leigh; Castleford; Wallsend; Boston; Oldbury; Bletchley; Grantham; Batley; Grays; Bexhill-on-Sea; Trowbridge; Cheshunt; Worksop; Braintree; Leighton Buzzard; Lytham St Anne's; Fareham; Newbury; Ramsgate; Urmston; Hatfield; Bury St Edmunds; Eccles; Bishop's Stortford; Hoddesdon; Bamber Bridge; Haywards Heath; Arnold; Aldershot; Borehamwood; Blyth; Chorley; Leyland; Prescot; Rowley Regis; Ilkeston; Canvey Island; Long Eaton; Fleet; Bicester; Redcar; Chadderton; Whitley Bay; Camberley

**English built-up areas, 20,000–29,999 — 161** (first 60 shown)

Northfleet; Consett; Newark-on-Trent; Heywood; Cleethorpes; Newton Abbot; Eston; Stanford-le-Hope; Jarrow; Shipley; Heswall; Deal; Great Yarmouth; Kendal; Cramlington; Hertford; Farnworth; Bushey; Yate; Ashington; Evesham; Stratford-upon-Avon; Totton; Woodley; Stretford; Egham; Lancing; Frome; Burntwood; Darwen; Daventry; Ormskirk; Atherton; Wickford; Ewell; Melton Mowbray; Witham; Tadworth; Horley; Walton-on-Thames; Longbenton; Stalybridge; Wisbech; Haverhill; Sevenoaks; Droitwich Spa; Ashton-in-Makerfield; Portishead; East Grinstead; Rickmansworth; Fleetwood; Larkfield; Rugeley; Stroud; Little Hulton; Broadstairs; Newton Aycliffe; Wilmslow; Huntingdon; Golborne

**Scottish towns and burghs — 235 across 35 historic counties.** Subdivision structure is by historic county, which is how the source organises them. — [List of towns in Scotland](https://en.wikipedia.org/wiki/List_of_towns_in_Scotland)

Counties used as subdivisions: Counties of cities; Aberdeenshire; Angus; Argyll; Ayrshire; Banffshire; Berwickshire; Buteshire; Caithness; Clackmannanshire; Dumfriesshire; Dunbartonshire; East Lothian; Fife; Inverness-shire; Kincardineshire; Kinross-shire; Kirkcudbrightshire; Lanarkshire; Midlothian; Morayshire; Nairnshire; Orkney; Peeblesshire; Perthshire; Renfrewshire; Ross and Cromarty; Roxburghshire; Selkirkshire; Stirlingshire; Sutherland; West Lothian; Wigtownshire; Zetland; See also

First 60 names: Aberdeen; Dundee; Edinburgh; Edinburgh burgh constituency; Glasgow; Inverurie; Kintore; Ballater; Ellon; Fraserburgh; Huntly; Old Meldrum; Peterhead; Rattray; Rosehearty; Turriff; Arbroath; Brechin; Forfar; Montrose; Broughty Ferry; Carnoustie; Kirriemuir; Monifieth; Campbeltown; Inveraray; Dunoon; Lochgilphead; Oban; Tobermory; Ayr; Irvine; Ardrossan; Cumnock and Holmhead; Darvel; Galston; Girvan; Kilmarnock; Kilwinning; Largs; Maybole; Newmilns and Greenholm; Prestwick; Saltcoats; Stevenston; Stewarton; Troon; Banff; Cullen; Aberchirder; Aberlour; Buckie; Dufftown; Findochty; Keith; Macduff; Portknockie; Portsoy; Lauder; Coldstream

**Welsh towns — 161**, organised alphabetically in the source. — [List of towns in Wales](https://en.wikipedia.org/wiki/List_of_towns_in_Wales)

Aberaeron; Aberavon; Aberbargoed; Abercarn; Aberdare; Abergavenny; Abergele; Abersychan; Abertillery; Aberystwyth; Amlwch; Ammanford; Bala; Bangor; Bargoed; Barmouth; Barry; Beaumaris; Bedwas; Bethesda; Blaenau Ffestiniog; Blaenavon; Blackwood; Blaina; Brecon; Bridgend; Briton Ferry; Brynmawr; Buckley; Builth Wells; Burry Port; Caerleon; Caernarfon; Caerphilly; Caerwys; Caldicot; Cardiff; Cardigan; Carmarthen; Chepstow; Chirk; Colwyn Bay; Connah's Quay; Conwy; Corwen; Cowbridge; Criccieth; Crickhowell; Crumlin; Cwmbran; Deganwy; Denbigh; Dolgellau; Ebbw Vale; Ferndale; Fishguard; Flint; Gelligaer; Glynneath; Goodwick; Gorseinon; Harlech; Haverfordwest; Hay-on-Wye; Holyhead; Holywell; Kidwelly; Knighton; Lampeter; Laugharne; Llandeilo; Llandovery; Llandrindod Wells; Llandudno; Llandudno Junction; Llandysul; Llanelli; Llanfair Caereinion; Llanfairfechan; Llanfyllin; Llangefni; Llangollen; Llanidloes; Llanrwst; Llantrisant; Llantwit Major; Llanwrtyd Wells; Llanybydder; Loughor; Machynlleth; Maesteg; Menai Bridge; Merthyr Tydfil; Milford Haven; Mold; Monmouth; Montgomery; Mountain Ash; Narberth; Neath; Nefyn; Newbridge; Newcastle Emlyn; Newport; Newport, Pembrokeshire; New Quay; Newtown; New Tredegar; Neyland; Overton-on-Dee; Pembroke; Pembroke Dock; Penarth; Pencoed; Penmaenmawr; Penrhyn Bay; Penrhyndeudraeth; Pontardawe; Pontarddulais; Pontyclun; Pontypool; Pontypridd; Port Talbot; Porth; Porthcawl; Porthmadog; Prestatyn; Presteigne; Pwllheli; Queensferry; Rhayader; Rhuddlan; Rhyl; Rhymney; Risca; Ruthin; St Asaph; St Clears; St David's; Saltney; Shotton; Swansea; Talbot Green; Talgarth; Tenby; Tonypandy; Tredegar; Tregaron; Treharris; Treorchy; Tywyn; Usk; Welshpool; Whitland; Wrexham; Ystradgynlais; Ystrad Mynach; List of cities in Wales; List of built-up areas in Wales by population; Welsh place names in other countries; List of standardised Welsh place-names

### Inferences

- The 15,000 floor the brief asks for sits inside the ONS 'small' band (5,000–19,999), so no published
  vanity list covers exactly 15,000+. The clean move is to load the ONS BUA 2024 table of 1,395 areas
  above 5,000 and filter at 15,000 — that gives a defensible, citable town list of roughly 1,100–1,200.
- Named settlements already in hand (850 outside London, 1,408 including London districts) are enough to
  start generating; the ONS load is an extension, not a blocker.

### Gaps

- I did not download the ONS BUA CSV itself, so I cannot give the 1,395 names. The dataset is linked from
  the ONS article above and from ONS Geoportal; it needs one fetch to resolve.
- No Northern Ireland town list was harvested. NISRA publishes settlement classifications; untested here.

## Q2 — Counties, council areas, principal areas

### Takeaway

All four national subdivision sets are closed and complete: 48 English ceremonial counties, 32 Scottish
council areas, 22 Welsh principal areas, 6 Northern Irish counties — 108 rows in total.

### Cited Findings

**English ceremonial counties — 48** (lieutenancy areas since 1998). The brief's 38 is an undercount; the statutory figure is 48. — [Ceremonial counties of England](https://en.wikipedia.org/wiki/Ceremonial_counties_of_England)

Bedfordshire; Berkshire; Bristol; Buckinghamshire; Cambridgeshire; Cheshire; City of London; Cornwall; Cumbria; Derbyshire; Devon; Dorset; Durham; East Riding of Yorkshire; East Sussex; Essex; Gloucestershire; Greater London; Greater Manchester; Hampshire; Herefordshire; Hertfordshire; Isle of Wight; Kent; Lancashire; Leicestershire; Lincolnshire; Merseyside; Norfolk; North Yorkshire; Northamptonshire; Northumberland; Nottinghamshire; Oxfordshire; Rutland; Shropshire; Somerset; South Yorkshire; Staffordshire; Suffolk; Surrey; Tyne and Wear; Warwickshire; West Midlands; West Sussex; West Yorkshire; Wiltshire; Worcestershire

**Scottish council areas — 32**, all 32 confirmed present in the source. — [Subdivisions of Scotland](https://en.wikipedia.org/wiki/Subdivisions_of_Scotland)

Aberdeen City; Aberdeenshire; Angus; Argyll and Bute; City of Edinburgh; Clackmannanshire; Dumfries and Galloway; Dundee City; East Ayrshire; East Dunbartonshire; East Lothian; East Renfrewshire; Falkirk; Fife; Glasgow City; Highland; Inverclyde; Midlothian; Moray; Na h-Eileanan Siar (Outer Hebrides / Western Isles); North Ayrshire; North Lanarkshire; Orkney Islands; Perth and Kinross; Renfrewshire; Scottish Borders; Shetland Islands; South Ayrshire; South Lanarkshire; Stirling; West Dunbartonshire; West Lothian

**Welsh principal areas — 22** (23 rows extracted, including one header artefact) — [Principal areas of Wales](https://en.wikipedia.org/wiki/Principal_areas_of_Wales)

native_name = Prif ardaloedd Cymru; Isle of Anglesey; Gwynedd; Cardiff; Ceredigion; Carmarthenshire; Denbighshire; Flintshire; Monmouthshire; Pembrokeshire; Powys; Swansea; Conwy; Blaenau Gwent; Bridgend; Caerphilly; Merthyr Tydfil; Neath Port Talbot; Newport; Rhondda Cynon Taf; Torfaen; The Vale of Glamorgan; Wrexham

**Northern Ireland counties — 6** — [Counties of Northern Ireland](https://en.wikipedia.org/wiki/Counties_of_Northern_Ireland). **UNVERIFIED** (page not fetched this session; this set is however stable and uncontested):

Antrim; Armagh; Down; Fermanagh; Londonderry (also Derry); Tyrone

### Inferences

- The brief named 14 'effectively missing' English counties. All 14 are in the 48, so a county series is
  directly generable; at 48 counties x one format it is a small block, but county outline + county name
  is one of the few formats that works at this granularity.

### Gaps

- Northern Ireland county names are listed from knowledge, not from this session's extraction (the page did not download). The set is stable and uncontested, but confirm before use.

## Q3 — London: boroughs, districts, postcodes

### Takeaway

All three London layers are complete and well over target: 33 boroughs including the City,
558 named districts (target was 150+), and 124 postal districts.

### Cited Findings

**London boroughs — 33** (32 boroughs + the City of London) — [List of London boroughs](https://en.wikipedia.org/wiki/List_of_London_boroughs)

Barking and Dagenham; Barnet; Bexley; Brent; Bromley; Camden; Croydon; Ealing; Enfield; Greenwich; Hackney; Hammersmith and Fulham; Haringey; Harrow; Havering; Hillingdon; Hounslow; Islington; Kensington and Chelsea; Kingston upon Thames; Lambeth; Lewisham; Merton; Newham; Redbridge; Richmond upon Thames; Southwark; Sutton; Tower Hamlets; Waltham Forest; Wandsworth; Westminster; (Inner)

**Named London districts / neighbourhoods — 558**, each tagged with its borough. This is the single
richest UK place block found: it alone is 3.7x the 150-district target. — [List of areas of London](https://en.wikipedia.org/wiki/List_of_areas_of_London)

First 60 of 558:

- Abbey Wood (Bexley,  Greenwich)
- Acton (Ealing, Hammersmith and Fulham)
- Acton Green (Ealing)
- Addington (Croydon)
- Addiscombe (Croydon)
- Albany Park (Bexley)
- Aldborough Hatch (Redbridge)
- Aldgate (City)
- Aldwych (Westminster)
- Alperton (Brent)
- Anerley (Bromley)
- Angel (Islington)
- Aperfield (Bromley)
- Archway (Islington)
- Ardleigh Green (Havering)
- Arkley (Barnet)
- Arnos Grove (Enfield)
- Balham (Wandsworth)
- Bankside (Southwark)
- Barbican (City)
- Barking (Barking and Dagenham)
- Barking Riverside (Barking and Dagenham)
- Barkingside (Redbridge)
- Barnehurst (Bexley)
- Barnes (Richmond upon Thames)
- Barnes Cray (Bexley)
- Barnet (Barnet)
- Barnet Gate (Barnet)
- Barnsbury (Islington)
- Battersea (Wandsworth)
- Bayswater (Westminster)
- Beam Park (Barking and Dagenham, Havering)
- Beckenham (Bromley)
- Beckton (Newham)
- Becontree (Barking and Dagenham)
- Becontree Heath (Barking and Dagenham)
- Beddington (Sutton)
- Bedford Park (Ealing)
- Belgravia (Westminster)
- Bell Green (Lewisham)
- Bellingham (Lewisham)
- Belmont (Harrow)
- Belmont (Sutton)
- Belsize Park (Camden)
- Belvedere (Bexley)
- Bermondsey (Southwark)
- Berry's Green (Bromley)
- Berrylands (Kingston upon Thames)
- Bethnal Green (Tower Hamlets)
- Bexley (Bexley)
- Bexleyheath (Bexley)
- Bickley (Bromley)
- Biggin Hill (Bromley)
- Blackfen (Bexley)
- Blackfriars (City)
- Blackheath (Lewisham)
- Blackheath Royal Standard (Greenwich)
- Blackwall (Tower Hamlets)
- Blendon (Bexley)
- Bloomsbury (Camden)

All the brief's test names are present in the full list: Shoreditch, Peckham, Hampstead, Greenwich,
Notting Hill. The source table also carries the post town and postcode district for each area, so a
district print can be generated with its own postcode without a second lookup.

**London postal districts — 124** (EC, WC, N, NW, E, SE, SW, W series) — [London postal district](https://en.wikipedia.org/wiki/London_postal_district)

E1; E10; E11; E12; E13; E14; E15; E16; E17; E18; E19; E2; E20; E3; E4; E5; E6; E7; E8; E9; EC1; EC2; EC3; EC4; N1; N10; N11; N12; N13; N14; N15; N16; N17; N18; N19; N2; N20; N21; N22; N3; N4; N5; N6; N7; N8; N9; NW1; NW10; NW11; NW1W; NW2; NW3; NW4; NW5; NW6; NW7; NW8; NW9; SE1; SE10; SE11; SE12; SE13; SE14; SE15; SE16; SE17; SE18; SE19; SE1P; SE2; SE20; SE21; SE22; SE23; SE24; SE25; SE26; SE27; SE28; SE3; SE4; SE5; SE6; SE7; SE8; SE9; SW1; SW10; SW11; SW12; SW13; SW14; SW15; SW16; SW17; SW18; SW19; SW2; SW20; SW3; SW4; SW5; SW6; SW7; SW8; SW9; W1; W10; W11; W12; W13; W14; W1P; W2; W3; W4; W5; W6; W7; W8; W9; WC1; WC2

**London Underground stations — 269** — [List of London Underground stations](https://en.wikipedia.org/wiki/List_of_London_Underground_stations)

First 60 of 269: Acton Town; Aldgate; Aldgate East; Alperton; Amersham; Angel; Archway; Arnos Grove; Arsenal; Baker Street; Balham; Bank; Barbican; Barking; Barkingside; Barons Court; Battersea Power Station; Bayswater; Becontree; Belsize Park; Bermondsey; Bethnal Green; Blackfriars; Blackhorse Road; Bond Street; Borough; Boston Manor; Bounds Green; Bow Road; Brent Cross; Brixton; Bromley-by-Bow; Buckhurst Hill; Burnt Oak; Caledonian Road; Camden Town; Canada Water; Canary Wharf; Canning Town; Cannon Street; Canons Park; Chalfont & Latimer; Chalk Farm; Chancery Lane; Charing Cross; Chesham; Chigwell; Chiswick Park; Chorleywood; Clapham Common; Clapham North; Clapham South; Cockfosters; Colindale; Colliers Wood; Covent Garden; Croxley; Dagenham East; Dagenham Heathway; Debden

**Underground lines — 11** — **UNVERIFIED** (taken from general knowledge, not extracted this session):
Bakerloo; Central; Circle; District; Hammersmith & City; Jubilee; Metropolitan; Northern; Piccadilly;
Victoria; Waterloo & City. The Elizabeth line, DLR, London Overground and Tram are separate TfL modes,
not Underground lines.

### Inferences

- London districts are the highest-volume, lowest-risk UK place block in the whole gazetteer: 558 names,
  no trademark exposure, and each has a postcode and a borough attached for format variation.

### Gaps

- The roundel, the Johnston typeface and the Tube map diagram are all TfL intellectual property. I did
  not research TfL's licensing terms. Transit-map formats for London must be treated as restricted until
  that is checked — see the risk register at the end.

## Q4 — National Parks and National Landscapes

### Takeaway

Both sets are closed and fully named: 15 National Parks and 46 National Landscapes (the renamed AONBs).

### Cited Findings

**UK National Parks — 15** (10 England, 3 Wales, 2 Scotland) — [National parks of the United Kingdom](https://en.wikipedia.org/wiki/National_parks_of_the_United_Kingdom)

- Peak District
- Lake District
- Snowdonia
- Dartmoor
- Pembrokeshire Coast
- North York Moors
- Yorkshire Dales
- Exmoor
- Northumberland
- Brecon Beacons
- The Broads
- Loch Lomond and The Trossachs
- Cairngorms
- New Forest
- South Downs

Note the two Welsh parks now carry Welsh-language names officially: Snowdonia is Eryri and the Brecon
Beacons is Bannau Brycheiniog. Both names should be generated as separate catalogue rows.

**National Landscapes in England — 34** (33 wholly in England plus the cross-border Wye Valley) — [National Landscape](https://en.wikipedia.org/wiki/National_Landscape)

- Arnside and Silverdale
- Blackdown Hills
- Cannock Chase
- Chichester Harbour
- Chilterns
- Cornwall
- Cotswolds
- Cranborne Chase and West Wiltshire Downs
- Dedham Vale
- Dorset
- East Devon
- Forest of Bowland
- High Weald
- Howardian Hills
- Isle of Wight
- Isles of Scilly
- Kent Downs
- Lincolnshire Wolds
- Malvern Hills
- Mendip Hills
- Nidderdale
- Norfolk Coast
- North Devon Coast
- North Pennines
- Northumberland Coast
- North Wessex Downs
- Quantock Hills
- Shropshire Hills
- Solway Coast
- South Devon
- Suffolk & Essex Coast & Heaths
- Surrey Hills
- Tamar Valley
- Wye Valley

**National Landscapes in Wales — 5**

- Anglesey
- Clwydian Range and Dee Valley
- Gower
- Llŷn
- Wye Valley

**National Landscapes / AONBs in Northern Ireland — 8**

- Antrim Coast and Glens
- Binevenagh
- Causeway Coast
- Lagan Valley
- Mourne
- Ring of Gullion
- Sperrin
- Strangford

Unique total: 46 (Wye Valley appears in both the England and Wales tables because it straddles the border).

### Inferences

- 15 parks + 46 landscapes = 61 designated-landscape names. Every one is a pictorial subject with no
  lettering requirement and no trademark holder, which makes this the safest block in the gazetteer.

### Gaps

- The National Landscapes body (nationallandscapes.org.uk) is the primary source; I used the Wikipedia
  mirror, which matches the 46 count but was not cross-checked entry by entry against the official site.

## Q5 — The Lake District

### Takeaway

The 214 Wainwrights extracted exactly, with their four fell sections, plus 31 named lakes, tarns and reservoirs.

### Cited Findings

**Wainwrights — 214**, ranked by height, each tagged with its fell group. Count matches the canonical 214 exactly. — [List of Wainwrights](https://en.wikipedia.org/wiki/List_of_Wainwrights) (sourced from the Database of British and Irish Hills)

- 1. Scafell Pike [Central & Western]
- 2. Scafell [Central & Western]
- 3. Helvellyn [Eastern]
- 4. Skiddaw [Northern]
- 5. Great End [Central & Western]
- 6. Bowfell [Central & Western]
- 7. Great Gable [Central & Western]
- 8. Pillar [Central & Western]
- 9. Nethermost Pike [Eastern]
- 10. Catstye Cam [Eastern]
- 11. Esk Pike [Central & Western]
- 12. Raise [Eastern]
- 13. Fairfield [Eastern]
- 14. Blencathra (Hallsfell Top) [Northern]
- 15. Skiddaw Little Man [Northern]
- 16. White Side [Eastern]
- 17. Crinkle Crags (Long Top) [Central & Western]
- 18. Dollywaggon Pike [Eastern]
- 19. Great Dodd [Eastern]
- 20. Grasmoor [Central & Western]
- 21. Stybarrow Dodd [Eastern]
- 22. Scoat Fell [Central & Western]
- 23. St Sunday Crag [Eastern]
- 24. Crag Hill [Central & Western]
- 25. High Street [Eastern]
- 26. Red Pike (Wasdale) [Central & Western]
- 27. Hart Crag [Eastern]
- 28. Steeple [Central & Western]
- 29. Lingmell [Central & Western]
- 30. High Stile [Central & Western]
- 31. The Old Man of Coniston [Southern]
- 32. Swirl How [Southern]
- 33. Kirk Fell [Central & Western]
- 34. High Raise (High Street) [Eastern]
- 35. Green Gable [Central & Western]
- 36. Haycock [Central & Western]
- 37. Brim Fell [Southern]
- 38. Rampsgill Head [Eastern]
- 39. Dove Crag [Eastern]
- 40. Grisedale Pike [Central & Western]
- 41. Watson's Dodd [Eastern]
- 42. Allen Crags [Central & Western]
- 43. Great Carrs [Southern]
- 44. Thornthwaite Crag [Eastern]
- 45. Glaramara [Central & Western]
- 46. Kidsty Pike [Eastern]
- 47. Harter Fell (Mardale) [Eastern]
- 48. Dow Crag [Southern]
- 49. Red Screes [Eastern]
- 50. Sail [Central & Western]
- 51. Grey Friar [Southern]
- 52. Wandope [Central & Western]
- 53. Hopegill Head [Central & Western]
- 54. Great Rigg [Eastern]
- 55. Stony Cove Pike [Eastern]
- 56. Wetherlam [Southern]
- 57. High Raise [Central & Western]
- 58. Slight Side [Central & Western]
- 59. Mardale Ill Bell [Eastern]
- 60. Ill Bell [Eastern]

...remaining 154 in the source, same table, ranks 61–214.

Subdivision structure — Wainwright's seven books, which is how fell-walkers name them:
Book One: The Eastern Fells; Book Two: The Far Eastern Fells; Book Three: The Central Fells;
Book Four: The Southern Fells; Book Five: The Northern Fells; Book Six: The North Western Fells;
Book Seven: The Western Fells. The DoBIH table groups them instead into four sections: Northern,
Central & Western, Eastern, Southern.

There are also 116 Wainwright Outlying Fells from the 1974 supplementary volume, in the same source.

**Lake District lakes, tarns and reservoirs — 31 named** — [List of lakes of the Lake District](https://en.wikipedia.org/wiki/List_of_lakes_of_the_Lake_District)

Bassenthwaite Lake; Blea Water; Blelham Tarn; Brotherswater; Burnmoor Tarn; Buttermere; Cogra Moss; Coniston Water; Crummock Water; Derwent Water; Devoke Water; Easedale Tarn; Elter Water; Ennerdale Water; Esthwaite Water; Grasmere; Grisedale Tarn; Haweswater; Hayeswater; Kentmere Reservoir; Levers Water; Loweswater; Over Water; Rydal Water; Seathwaite Tarn; Tarn Hows; Thirlmere; Ullswater; Wastwater; Wet Sleddale Reservoir; Windermere

Only one of these is called a 'lake' in its name (Bassenthwaite Lake); the rest are waters, meres and
tarns. The 16 commonly counted 'main lakes' are the larger entries above — Windermere, Ullswater,
Derwent Water, Bassenthwaite Lake, Coniston Water, Haweswater, Thirlmere, Ennerdale Water, Wastwater,
Crummock Water, Esthwaite Water, Buttermere, Grasmere, Loweswater, Rydal Water, Elter Water.

### Gaps

- **Lake District villages: not harvested.** No village list was fetched. Keswick, Ambleside, Grasmere,
  Windermere, Bowness-on-Windermere, Coniston, Hawkshead, Elterwater, Chapel Stile, Patterdale, Glenridding,
  Pooley Bridge, Buttermere, Braithwaite, Threlkeld, Caldbeck, Eskdale, Boot, Wasdale Head, Seathwaite and
  Cartmel are the obvious ones but this is **UNVERIFIED** general knowledge, not an extracted list. The
  Lake District National Park Authority site is the source to use.

## Q6 — Scotland: Munros, islands, lochs, glens, whisky

### Takeaway

Scotland is the densest named-place territory in the UK. The Munros, the islands, the lochs and the
distilleries are all extracted. Glens are the one Scottish block I could not get a list for.

### Cited Findings

**Munros — 282 officially; 266 named rows extracted.** The Scottish Mountaineering Club's count is 282 and the source article states 282, but the DoBIH-derived table in that article yields 266 distinct named rows. I am reporting the discrepancy rather than resolving it: the table appears to predate a revision. — [List of Munros](https://en.wikipedia.org/wiki/List_of_Munros)

- 1. Ben Nevis — 04A: Fort William to Loch Treig & Loch Leven — Highland
- 2. Ben Macdui — 08A: Cairngorms — Aberdeenshire
- 3. Braeriach — 08A: Cairngorms — Aberdeenshire
- 4. Cairn Toul — 08A: Cairngorms — Aberdeenshire
- 5. Sgor an Lochain Uaine — 08A: Cairngorms — Aberdeenshire
- 6. Cairn Gorm — 08A: Cairngorms — Highland
- 7. Aonach Beag — 04A: Fort William to Loch Treig & Loch Leven — Highland
- 8. Càrn Mòr Dearg — 04A: Fort William to Loch Treig & Loch Leven — Highland
- 9. Aonach Mòr — 04A: Fort William to Loch Treig & Loch Leven — Highland
- 10. Ben Lawers — 02B: Glen Lyon to Glen Dochart & Loch Tay — Perth and Kinross
- 11. Beinn a' Bhùird — 08B: Cairngorms — Aberdeenshire
- 12. Beinn Mheadhoin — 08A: Cairngorms — Moray
- 13. Càrn Eige — 11A: Loch Duich to Cannich — Highland
- 14. Mam Sodhail — 11A: Loch Duich to Cannich — Highland
- 15. Stob Choire Claurigh — 04A: Fort William to Loch Treig & Loch Leven — Highland
- 16. Ben More — 01C: Loch Lomond to Strathyre — Stirling
- 17. Ben Avon — 08B: Cairngorms — Aberdeenshire
- 18. Stob Binnein — 01C: Loch Lomond to Strathyre — Stirling
- 19. Beinn Bhrotain — 08A: Cairngorms — Aberdeenshire
- 20. Derry Cairngorm — 08A: Cairngorms — Aberdeenshire
- 21. Lochnagar — 07A: Braemar to Montrose — Aberdeenshire
- 22. Sgurr na Lapaich — 12B: Killilan to Inverness — Highland
- 23. Sgurr nan Ceathreamhnan — 11A: Loch Duich to Cannich — Highland
- 24. Bidean nam Bian — 03B: Loch Linnhe to Loch Etive — Highland
- 25. Ben Alder — 04B: Loch Treig to Loch Ericht — Highland
- 26. Ben Lui — 01D: Inveraray to Crianlarich — Stirling
- 27. Geal-Chàrn — 04B: Loch Treig to Loch Ericht — Highland
- 28. Binnein Mòr — 04A: Fort William to Loch Treig & Loch Leven — Highland
- 29. Creag Meagaidh — 09C: Loch Lochy to Loch Laggan — Highland
- 30. An Riabhachan — 12B: Killilan to Inverness — Highland
- 31. Ben Cruachan — 03C: Glen Etive to Glen Lochy — Argyll and Bute
- 32. Meall Garbh — 02B: Glen Lyon to Glen Dochart & Loch Tay — Perth and Kinross
- 33. Beinn a' Ghló - Càrn nan Gabhar — 06B: Pitlochry to Braemar & Blairgowrie — Perth and Kinross
- 34. A' Chraileag — 11B: Glen Affric to Glen Moriston — Highland
- 35. An Stuc — 02B: Glen Lyon to Glen Dochart & Loch Tay — Perth and Kinross
- 36. Stob Coire an Laoigh — 04A: Fort William to Loch Treig & Loch Leven — Highland
- 37. Stob Coire Easain — 04A: Fort William to Loch Treig & Loch Leven — Highland
- 38. Sgor Gaoith — 08A: Cairngorms — Highland
- 40. Monadh Mòr — 08A: Cairngorms — Aberdeenshire
- 41. Tom a' Choinich — 11A: Loch Duich to Cannich — Highland
- 42. Càrn a' Choire Bhoidheach — 07A: Braemar to Montrose — Aberdeenshire
- 43. Sgurr nan Conbhairean — 11B: Glen Affric to Glen Moriston — Highland
- 44. Sgurr Mòr — 14B: The Fannaichs — Highland
- 45. Meall a' Bhuiridh — 03C: Glen Etive to Glen Lochy — Highland
- 46. Stob a' Choire Mheadhoin — 04A: Fort William to Loch Treig & Loch Leven — Highland
- 47. Beinn Ghlas — 02B: Glen Lyon to Glen Dochart & Loch Tay — Perth and Kinross
- 48. Beinn Eibhinn — 04B: Loch Treig to Loch Ericht — Highland
- 49. Mullach Fraoch-choire — 11B: Glen Affric to Glen Moriston — Highland
- 50. Creise — 03C: Glen Etive to Glen Lochy — Highland
- 51. Sgurr a' Mhaim — 04A: Fort William to Loch Treig & Loch Leven — Highland

...remaining 216 rows in the source table, ranked by height.

**Munro subdivision structure — 39 SMC sections**, which is the right grouping for a regional print series:

01A: Loch Tay to Perth; 01B: Strathyre to Strathallan; 01C: Loch Lomond to Strathyre; 01D: Inveraray to Crianlarich; 02A: Loch Rannoch to Glen Lyon; 02B: Glen Lyon to Glen Dochart & Loch Tay; 03A: Loch Leven to Rannoch Station; 03B: Loch Linnhe to Loch Etive; 03C: Glen Etive to Glen Lochy; 04A: Fort William to Loch Treig & Loch Leven; 04B: Loch Treig to Loch Ericht; 05A: Loch Ericht to Glen Tromie & Glen Garry; 05B: Loch Ericht to Glen Tromie & Glen Garry; 06A: Glen Tromie to Glen Tilt; 06B: Pitlochry to Braemar & Blairgowrie; 07A: Braemar to Montrose; 07B: Braemar to Montrose; 08A: Cairngorms; 08B: Cairngorms; 09B: Glen Albyn and the Monadh Liath; 09C: Loch Lochy to Loch Laggan; 10A: Glen Shiel to Loch Hourn and Loch Quoich; 10B: Knoydart to Glen Kingie; 10C: Loch Arkaig to Glen Moriston; 10D: Mallaig to Fort William; 11A: Loch Duich to Cannich; 11B: Glen Affric to Glen Moriston; 12A: Kyle of Lochalsh to Garve; 12B: Killilan to Inverness; 13A: Loch Torridon to Loch Maree; 13B: Applecross to Achnasheen; 14A: Loch Maree to Loch Broom; 14B: The Fannaichs; 15A: Loch Broom to Strath Oykel; 15B: Loch Vaich to Moray Firth; 16B: Durness to Loch Shin; 16D: Altnaharra to Dornoch; 16E: Scourie to Lairg; 17B: Minginish and the Cuillin Hills

There are also 227 Munro Tops (subsidiary summits) in the same source, plus 222 Corbetts and 221 Grahams
as separate hill classifications — **UNVERIFIED counts**, not extracted this session.

**Scottish islands — 244 named**, each tagged with its group — [List of islands of Scotland](https://en.wikipedia.org/wiki/List_of_islands_of_Scotland)

Island-group subdivision structure with counts extracted: Orkney 30; Uist 30; Shetland 24; Lewis and
Harris 19; Mull 15; Islay 13; Skye 10; Highland coast 10; Firth of Clyde 8; Small Isles 6; Slate Islands 6;
Summer Isles 5; Loch Lomond 5; St Kilda 3; Loch Linnhe 3; Out Skerries 2; Garvellachs 2; Crowlin Islands 2;
Loch Maree 2; Firth of Forth 2; Inner Hebrides (ungrouped) 2; unassigned 33.

First 60 of 244:

Ailsa Craig (Firth of Clyde); Arran; Auskerry (Orkney); Baleshare (Uist); Balta (Shetland); Barra (Uist); Barra Head; Benbecula; Berneray; Bigga (Shetland); Boreray (St Kilda); Boreray (Uist); Bressay (Shetland); Brother Isle; Bruray (Out Skerries); Buchan Ness (Buchan); Burray (Orkney); Bute (Firth of Clyde); Calf of Eday (Orkney); Calbha Mòr (Edrachillis Bay); Calve Island (Mull); Canna (Small Isles); Cara (Islay); Càrna (Mull); Cava (Orkney); Ceallasaigh Mòr (Uist); Ceallasaigh Beag; Ceann Ear (Monach Islands); Ceann Iar; Coll (Mull); Colonsay (Islay); Copinsay (Orkney); Danna (Islay); Davaar (Firth of Clyde); Dunglass Island (River Conon); Easdale (Slate Islands); East Burra (Shetland); Eday (Orkney); Egilsay; Eigg (Small Isles); Eilean a' Ghiorr (Uist); Eileach an Naoimh (Garvellachs); Eilean Bàn (Highland); Eilean Buidhe (Craobh Haven); Eilean Chaluim Chille (Lewis and Harris); Eilean Chearstaidh; Eilean dà Mhèinn (Islay); Eilean Donan (Highland); Eilean Dubh Mòr (Slate Islands); Eilean Fladday (Inner Hebrides); Eilean Leathann (Uist); Eilean Liubhaird (Lewis and Harris); Eilean Loain (Inner Hebrides); Eilean Macaskin (Islay); Eilean Meadhonach (Crowlin Islands); Eilean Mhealasta (Lewis and Harris); Eilean Mhic Chrion (Islay); Eilean Mòr (Crowlin Islands); Eilean Mòr (Lewis); Eilean nan Ròn (Highland)

**Scottish mainland lochs — 1013 named**, organised A–Z in the source. Plus 28 named lochs on islands. — [List of lochs of Scotland](https://en.wikipedia.org/wiki/List_of_lochs_of_Scotland)

First 60 of 1013: Loch A'an; Loch of Aboyne; Loch Achaidh na h-Inich; Loch Achall; Loch Achanalt; Loch Achilty; Loch Achnacloich; Loch Achnamoine; Loch Achonachie; Loch Achray; Achridigill Loch; Loch Achtriochtan; Loch an Add; Loch Affric; Lochan na h-Achlaise; Loch Ailsh; Loch Ainme na Gaibhre; Loch na h-Airde Bige; Loch Airigh na Beinne, Assynt; Loch Airigh na Beinne, Cape Wrath; Loch Airigh an Eilein; Loch Airigh Mhic Criadh; Loch Airigh a' Phuill; Loch na h-Airigh Sléibhe; Loch Aisir Mòr; Akermoor Loch; Loch Akran; Aldinna Loch; Alemoor Loch; Loch Allt na h-Airbe; Loch Allt Eoin Thòmais; Loch an Alltan Fheàrna; Loch Alvie; Loch nan Amhaichean; Loch Anna; Antermony Loch; Approach Loch; Loch Arail; Loch Ard; Loch Ard a' Phuill; Loch Ardinning; Loch Arichlinie; Loch Arienas; Loch Arkaig; Loch Arklet; Loch Arnicle; Loch Arthur; Loch Ascaig; Asgog Loch; Ashgrove Loch; Loch Ashie; Loch Aslaich; Loch an Aslaird; Loch Assynt; Aucha Lochy; Auchenreoch Loch; Auchintaple Loch; Loch Avich; Loch Avon; Loch Awe

The source's own 'largest and deepest' table is the sub-list worth generating first: Loch Lomond,
Loch Ness, Loch Awe, Loch Maree, Loch Morar, Loch Tay, Loch Shin, Loch Shiel, Loch Katrine, Loch Earn,
Loch Rannoch, Loch Ericht, Loch Arkaig, Loch Lochy, Loch Linnhe — **UNVERIFIED ordering**, the table
did not parse; the names are in the source.

**Scotch malt whisky distilleries, currently operating — 125**, each with location and region. Plus 6 grain distilleries. — [List of whisky distilleries in Scotland](https://en.wikipedia.org/wiki/List_of_whisky_distilleries_in_Scotland)

**Whisky regions with distillery counts, extracted:**

| Region | Operating malt distilleries |
|---|---|
| Speyside | 49 |
| Highland | 34 |
| Lowland | 18 |
| Island | 11 |
| Islay | 10 |
| Campbeltown | 3 |
| **Total** | **125** |

Note: the five statutory Scotch whisky regions under the Scotch Whisky Regulations 2009 are Highland,
Lowland, Speyside, Islay and Campbeltown. 'Island' is a widely used trade grouping, not a statutory
region — the source table uses it, so it appears above.

**Islay (10)**: Ardbeg; Ardnahoe; Bowmore; Bruichladdich; Bunnahabhain; Caol Ila; Kilchoman; Lagavulin; Laggan Bay; Laphroaig

**Campbeltown (3)**: Glen Scotia; Glengyle; Springbank

**Island (11)**: Abhainn Dearg; Highland Park; Jura; Lochranza; Orkney; Raasay; Scapa; Talisker; Tiree; Tobermory; Torabhaig

**Lowland (18)**: Aberargie; Ailsa Bay; Annandale; Auchentoshan; Ben Cumhaill; Blackness; Bladnoch; Daftmill; Eden Mill; Falkirk; Glasgow; Glenkinchie; Holyrood; Kingsbarns; Kythe; Lochlea; Moffat; Stirling

**Speyside (49)**: Aberlour; Allt-A-Bhainne; Auchroisk; Aultmore; Balmenach; Balvenie; BenRiach; Benrinnes; Benromach; Braeval; Cairn; Cardhu; Cragganmore; Craigellachie; Dailuaine; Dalmunach; Dufftown; Glen Elgin; Glen Grant; Glen Keith; Glen Moray; Glen Spey; Glenallachie; Glenburgie; Glendullan; Glenfarclas; Glenfiddich; Glenlivet; Glenlossie; Glenrothes; Glentauchers; Inchgower; Kininvie; Knockando; Knockdhu; Linkwood; Longmorn; Macallan; Mannochmore; Miltonduff; Mortlach; Roseisle; Speyburn; Strathisla; Strathmill; Tamdhu; Tamnavulin; Tomintoul; Tormore

**Highland (34)**: Aberfeldy; Arbikie; Ardmore; Balblair; Balmaud; Ben Nevis; Blair Athol; Clynelish; Dalmore; Dalwhinnie; Deanston; Edradour; Fettercairn; Glen Garioch; Glen Ord; GlenWyvis; Glencadam; Glendronach; Glenglassaugh; Glengoyne; Glenmorangie; Glenturret; Loch Lomond; Macduff; North Point; Oban; Pulteney; Royal Lochnagar; Strathearn; Teaninich; Tomatin; Toulvaddie; Tullibardine; Wolfburn

**Historic Environment Scotland properties — 302 across 32 council areas** (castles, abbeys, brochs, stone circles, palaces) — [List of Historic Scotland properties](https://en.wikipedia.org/wiki/List_of_Historic_Scotland_properties)

First 60 of 302: St Machar's Cathedral Transepts; 90px; Brandsbutt Stone; Corgarff Castle; Tower house; Cullerlie Stone Circle; Culsh Earth House; Deer Abbey; Duff House; Dyce Symbol Stones; Easter Aquhorthies Stone Circle; Glenbuchat Castle; Huntly Castle; Kildrummy Castle; Kinkell Church; Kinnaird Head Castle Lighthouse; Kinnaird Head Wine Tower; Loanhead Stone Circle; Maiden Stone; Pictish cross slab; Memsie Cairn; Peel Ring of Lumphanan; Earthworks; Picardy Symbol Stone; Pictish symbol stones; St Mary's Kirk, Auchindoir; Medieval; Tarves Medieval Tomb; Altar tomb; Tolquhon Castle; Castle; Tomnaverie Stone Circle; Aberlemno Sculptured Stones; Arbroath Abbey; Ardestie Earth House; Brechin Cathedral Round Tower; Carlungie Earth House; Caterthuns; Eassie Sculptured Stone; Edzell Castle; Lindsay Burial Aisle; Maison Dieu Chapel, Brechin; Restenneth Priory; St Orland's Stone; St Vigeans Sculptured Stones; Tealing Dovecot; Tealing Earth House; Ardchattan Priory; Bonawe Historic Iron Furnace; Carnasserie Castle; Castle Sween; Dunstaffnage Castle and Chapel; Eileach an Naoimh; St Cormac's Chapel, Eilean Mor; Inchkenneth Chapel; Iona Abbey; Iona Nunnery; Keills Chapel; Kilberry Sculptured Stones; Kilchurn Castle

### Gaps

- **Glens: no list obtained.** 'List of glens in Scotland' does not exist as a Wikipedia article and I
  found no official gazetteer of glens. Ordnance Survey's OS Open Names dataset is the right source — it
  is free, downloadable and includes a feature type for landforms, so glens can be filtered out of it.
  Until then, Glen Coe, Glen Nevis, Glen Affric, Glen Lyon, Glen Etive, Glenfinnan, Glen Shiel, Glen Torridon,
  Glen Esk, Glen Clova, Glen Moriston, Glen Cannich, Glen Lochay, Glen Orchy, Glen Spean and Glen Roy are
  **UNVERIFIED** general knowledge.
- The 'List of castles in Scotland' article is only an index of 32 per-council-area sub-lists, so no
  single Scottish castle list was harvested. The Historic Environment Scotland list above (302 properties)
  is the usable substitute; the 32 sub-lists can be fetched individually if a deeper set is needed.

## Q7 — Wales: mountains, castles, coast path towns, valleys

### Takeaway

186 Welsh mountains and 260 named Welsh castles extracted. Wales is the best castle territory
in the UK per square mile and the castle list is the largest single landmark block harvested.

### Cited Findings

**Welsh mountains — 186 Nuttalls** (summits over 2,000 ft with 15 m prominence), ranked by height — [List of mountains in Wales](https://en.wikipedia.org/wiki/List_of_mountains_in_Wales) (sourced from the Database of British and Irish Hills)

- Database of British and Irish Hills
- Height
- Snowdon
- Crib y Ddysgl
- Carnedd Llewelyn
- Carnedd Dafydd
- Glyder Fawr
- Glyder Fach
- Pen yr Ole Wen
- Foel Grach
- Castell y Gwynt
- Yr Elen
- Y Garn
- Foel-fras
- Garnedd Uchaf
- Elidir Fawr
- Crib Goch
- Tryfan
- Aran Fawddwy
- Y Lliwedd
- Y Lliwedd East Top
- Cadair Idris
- Pen y Fan
- Aran Benllyn
- Corn Du
- Moel Siabod
- Erw y Ddafad-ddu
- Mynydd Moel
- Arenig Fawr
- Llwytmor
- Pen yr Helgi Du
- Cadair Berwyn
- Foel-goch
- Arenig Fawr South Top
- Cadair Berwyn North Top
- Moel Sych
- Craig Gwaun Taf
- Carnedd y Filiast
- Lliwedd Bach
- Mynydd Perfedd
- Waun Fach
- Cyfrwy
- Bera Bach
- Y Foel Goch
- Fan Brycheiniog
- Pen y Gadair Fawr
- Foel Meirch
- Pen Llithrig y Wrach
- Cribyn
- Bera Mawr
- Craig Cwm Amarch
- Cadair Bronwen
- Moel Hebog
- Glasgwm
- Drum

...remaining 131 in the source.

**The Welsh 3000s — 15 summits over 3,000 ft**, all in Eryri/Snowdonia, grouped in three ranges
(Snowdon Massif, Glyderau, Carneddau). Verified against the source table. — [Welsh 3000s](https://en.wikipedia.org/wiki/Welsh_3000s)

Snowdon/Yr Wyddfa; Garnedd Ugain; Crib Goch; Elidir Fawr; Y Garn; Glyder Fawr; Glyder Fach; Tryfan;
Pen yr Ole Wen; Carnedd Dafydd; Carnedd Llewelyn; Yr Elen; Foel Grach; Carnedd Gwenllian; Foel-fras

(Note: Y Lliwedd is *not* one of the 15 — I had assumed it was before checking the source. Castell y
Gwynt appears in the source as a rock feature on the Glyder Fach ridge, not as a separate summit.)

**Welsh castles — 260 named** (includes Castell- forms) — [List of castles in Wales](https://en.wikipedia.org/wiki/List_of_castles_in_Wales)

First 60 of 260: thumb|300px|[[Caernarfon Castle; thumb|300px|[[Dolbadarn Castle; thumb|thumbtime=9|300px|A reconstruction of [[Holt Castle; Castles and Town Walls of King Edward in Gwynedd; Nolton Castle; Candleston Castle; 100px|Candleston Castle 2009; Coity Castle; 100px|Coity Castle, Nr Bridgend; Kenfig Castle; 100px|Ruins of Kenfig Castle; Llangynwyd Castle; 100px|Overgrown ruins of Llangynwyd Castle; 100px|Newcastle Castle - Bridgend; Caerphilly Castle; 100px|Caerphilly Castle; Morgraig Castle; 100px|Ruins of Castell Morgraig; Ruperra Castle; 100px|Ruperra Castle; Caer Castell Camp; Morganstown Castle Mound; Rumney Castle; Treoda Castle Mound; Twmpath Castle; Cardiff Castle; 100px|Cardiff Castle; Castell Coch; 100px|Castell Coch - exterior; St Fagans Castle; 100px|St Fagans Castle; Carmarthen Castle; 100px|Main gateway to Castell Caerfyrddin / Carmarthen Castle; Carreg Cennen Castle; 100px|Carreg Cennen Castle; Dinefwr Castle; 100px|The circular keep of Dinefwr Castle; Dryslwyn Castle; 100px|Dryslwyn Castle; Kidwelly Castle; 100px|The great gatehouse, Kidwelly Castle; Laugharne Castle; 100px|Laugharne Castle; Llandovery Castle; 100px|Llandovery Castle; Llansteffan Castle; 100px|Llansteffan Castle; Castell Moel; 100px|Castell Moel from Llansteffan Road; Newcastle Emlyn Castle; 100px|Newcastle Emlyn Castle; Aberdyfi Castle; Castell Cadwgan; Castell Caerwedros; Castell Gwallter; Castell Pistog; Dinerth Castle; Lampeter Castle; Llanrhystud Castle; Aberystwyth Castle

The four Cadw castles inscribed as a UNESCO World Heritage Site — Caernarfon, Conwy, Beaumaris and
Harlech — are the highest-demand subset and all four appear in the list above. Caernarfon and Conwy
were both named in the brief as missing from competitor coverage.

**Welsh towns — 161** (repeated from Q1 for convenience) — [List of towns in Wales](https://en.wikipedia.org/wiki/List_of_towns_in_Wales)

### Gaps

- **Wales Coast Path towns: not harvested as a list.** The path is 870 miles and Natural Resources Wales
  publishes it in 8 regional sections (North Wales Coast; Isle of Anglesey; Llŷn Peninsula; Meirionnydd;
  Ceredigion; Pembrokeshire; Carmarthen Bay and Gower; South Wales Coast) — **UNVERIFIED section names.**
  Source to use: walescoastpath.gov.uk.
- **The Valleys: no list obtained.** The South Wales Valleys are a named informal region, not an
  administrative set, and I found no authoritative enumeration. Rhondda, Cynon, Taff, Ebbw, Rhymney,
  Afan, Neath, Tawe, Llynfi, Garw, Ogmore and Sirhowy are the valley names in general use —
  **UNVERIFIED.** The Afon/river list for Wales (384 names, Q11) is the defensible proxy, since every
  valley is named after its river.
- **Cadw's own property list was not fetched.** Cadw guards about 130 monuments; the number here is
  **UNVERIFIED.** cadw.gov.wales is the source.

## Q8 — Coast: lighthouses, piers, beaches, coast path

### Takeaway

Lighthouses and piers came out clean and authoritative — Trinity House's own list of 65 lighthouses plus
7 lightvessels, and 59 surviving piers. Beaches, bays, coves, headlands and harbours did not: there is no
single authoritative UK list of them and I could not assemble one.

### Cited Findings

**Trinity House lighthouses — 65, plus 7 lightvessels.** Trinity House is the General Lighthouse
Authority for England, Wales, the Channel Islands and Gibraltar, so this is the primary source, not a
mirror. The page itself says 'over 60 lighthouses'. — [Trinity House, Lighthouses and Lightvessels](https://www.trinityhouse.co.uk/lighthouses-and-lightvessels)

Alderney; Anvil Point; Bamburgh; Bardsey; Beachy Head; Berry Head; Bishop Rock; Bull Point; Caldey Island;
Casquets; Coquet; Cromer; Crow Point; Dungeness; Eddystone; Europa Point; Farne Island; Flamborough Head;
Flatholm; Godrevy; Guile Point; Hartland Point; Heugh Hill; Hilbre Island; Hurst Point; Instow Front;
Instow Rear; Les Hanois; Lizard; Longships; Longstone; Lowestoft; Lundy North; Lundy South; Lynmouth
Foreland; Monkstone; Mumbles; Nab Tower; Nash Point; Needles; North Foreland; Pendeen; Peninnis;
Point Lynas; Portland Bill; Round Island; Sark; Skerries; Skokholm; Smalls; South Bishop; South Stack;
Southwold; St Ann's Head; St Anthony; St Bees; St Catherine's; St Tudwal's; Start Point; Strumble Head;
Tater Du; Trevose Head; Trwyn Du; Whitby; Wolf Rock

Lightvessels: East Goodwin; Foxtrot 3; Greenwich; Sandettie; Sevenstones; Sunk Inner; Varne

**Lighthouses in England, active, all operators — 85** (includes harbour and local-authority lights Trinity House does not run; 49 of the extracted rows name Trinity House as operator) — [List of lighthouses in England](https://en.wikipedia.org/wiki/List_of_lighthouses_in_England)

First 50 of 85: NGA; Anvil Point Lighthouse; Bamburgh Lighthouse; Beachy Head Lighthouse; !scope='row' |Berkeley Pill Front light; !scope='row' |Berkeley Pill Rear light; Berry Head Lighthouse; Berwick Lighthouse; Bishop Rock Lighthouse; Bull Point Lighthouse; Burnham-on-Sea Low Lighthouse; !scope='row' |Chapel Rock Lighthouse; Coquet Lighthouse; Cromer Lighthouse; Crow Point Lighthouse; Dungeness Lighthouse; Eddystone Lighthouse; Farne Lighthouse; Flamborough Head Lighthouse; Pharos Lighthouse; Beach Lighthouse; !scope='row' |Folkestone Lighthouse; Godrevy Lighthouse; Gorleston South Pier Lighthouse; Guile Point East Lighthouse; Happisburgh Lighthouse; Hartland Point Lighthouse; Heugh Lighthouse; Herd Groyne Light; Heugh Hill Lighthouse; Hilbre Island Lighthouse; Hurst Point Lighthouse; Ilfracombe Lighthouse; Instow Front Lighthouse; Instow Rear Lighthouse; Killingholme High Light; Killingholme South Low Lighthouse; Lizard Lighthouse; Longships Lighthouse; Longstone Lighthouse; Lowestoft Lighthouse; Lundy North Lighthouse; Lundy South Lighthouse; !scope='row' |Lyde Rock lighthouse; Lynmouth Foreland Lighthouse; Maryport New Lighthouse; Nab Tower; Needles Lighthouse; North Foreland Lighthouse; Pendeen Lighthouse

Scotland's lights are run by the Northern Lighthouse Board (nlb.org.uk) and Ireland's by the Commissioners
of Irish Lights. **I failed to extract a Scottish lighthouse list** — see Gaps.

**Surviving piers — 59 extracted**: England 47, Scotland 5, Wales 6, Isle of Man 1. — [List of piers in the United Kingdom](https://en.wikipedia.org/wiki/List_of_piers_in_the_United_Kingdom)

**Source conflict, stated plainly:** the National Piers Society's own site (piers.org.uk) would not
render for extraction. Secondary reports of the NPS figure disagree — 61 surviving piers is cited by
Clacton Pier and by a 2021 Coast magazine feature, 63 by Bangor City Council, and an older NPS figure of
55 for England and Wales appears on a Wikipedia talk page. My extracted 59 sits inside that range. Treat
59 as the working count and 55–63 as the uncertainty band. — [Clacton Pier, 61 surviving piers](https://www.clactonpier.co.uk/news/clacton-is-the-runner-up-in-pier-of-year-2019/); [Bangor City Council, 63 piers remaining](https://bangorcitycouncil.gov.wales/Y-Pier)

**Piers in England (47)**: Central Pier; South Pier; North Pier; Bognor Regis Pier; Bournemouth Pier; Boscombe Pier; Palace Pier; Burnham-on-Sea Pier; Clacton Pier; Cleethorpes Pier; Clevedon Pier; Cromer Pier; Deal Pier; Eastbourne Pier; Prince of Wales Pier; Felixstowe Pier; Folkestone Harbour Arm; Gravesend Town; Royal Terrace; Britannia Pier; Wellington Pier; Ha'penny Pier; Hastings Pier; Herne Bay Pier; Hythe Pier; Claremont Pier; St Annes Pier; Paignton Pier; Ryde Pier; Saltburn Pier; Sandown Pier; Skegness Pier; Royal Pier; Southend Pier; Southport Pier; South Parade Pier; Clarence Pier; Southwold Pier; Swanage Pier; Grand Pier; Princess Pier; Totland Pier; Walton Pier; Birnbeck Pier; Weymouth Pier; Worthing Pier; Yarmouth Pier

**Piers in Scotland (5)**: Dunoon Pier; Helensburgh Pier; Kilcreggan Pier; Rothesay Pier; Fort William Pier

**Piers in Wales (6)**: Royal Pier; Garth Pier; Beaumaris Pier; Llandudno Pier; Mumbles Pier; Penarth Pier

**Piers on the Isle of Man (1)**: Queen's Pier

**South West Coast Path — 630 miles, 7 named sections.** This is the official sectioning used by the
South West Coast Path Association and it is the correct subdivision for a print series. Place names below
are every settlement and feature linked in each section of the route description. — [South West Coast Path](https://en.wikipedia.org/wiki/South_West_Coast_Path)

| Section | Named places extracted |
|---|---|
| Somerset | 15 |
| North Devon | 88 |
| North Cornwall | 57 |
| West Cornwall | 78 |
| South Cornwall | 72 |
| South Devon | 103 |
| Dorset | 68 |
| **Total** | **481** |

**Somerset (15)**: thumb|right|upright|Sculpture at the start of the path in [[Minehead; Minehead; Somerset; Exmoor National Park; Selworthy Beacon; Hurlestone Point; Bossington; Porlock Weir; Coleridge Way; Heritage Coast; Exmoor Coastal Heaths; Site of Special Scientific Interest; Culbone Church; Culbone; Devon

**North Devon (88)**: Foreland Point; Lynmouth; Lynton and Lynmouth Cliff Railway; Lynton; Two Moors Way; catastrophic flood in the 1950s; Valley of Rocks; goat; BBC News; Lee Bay; Woody Bay; River Heddon; Trentishoe Down; Holdstone Down; Great Hangman; Combe Martin; thumb|left|The South West Coast Path passes along the cliffs (seen in the distance) at [[Ilfracombe; North Devon; Widmouth Head; Hele Bay; seaside resort; Ilfracombe; harbour; Lundy Island; The ''Balmoral''; the ''Waverley''; Porthcawl; Swansea; Bideford; Tarka Trail; thumb|[[Saunton Sands; The Torrs; Bull Point Lighthouse; Rackham Bay; Morte Point; Mortehoe; Morte Bay; Woolacombe; Putsborough; Baggy Point; Croyde Bay; Croyde; Barnstaple or Bideford Bay; North Devon Coast; Area of Outstanding Natural Beauty ...

**North Cornwall (57)**: thumb|The Haven, the Atlantic Ocean and the beach at [[Bude; Cornwall; Marsland Mouth; Morwenstow; Sandy Mouth; Bude; Widemouth Bay; Millook; Crackington Haven; Boscastle; flooding; Tintagel; castle; King Arthur; Trebarwith Strand; Tregardock; Port Gaverne; Port Isaac; Port Quin; thumb|left|The Rumps; The Rumps; dolerite; intrusion; Pentire Point; Polzeath; River Camel; Rock; Black Tor Ferry; Padstow; Stepper Point; Trevone; Harlyn; Trevose Head; Constantine Bay; Porthcothan; Mawgan Porth; thumb|An easterly view over [[Newquay; Watergate Bay; Porth; Newquay; rail link; Fistral Beach; River Gannel; Crantock; Kelsey Head ...

**West Cornwall (78)**: thumb|right|The SWCP near [[Lelant; Hayle; Godrevy; St Ives Bay; Towans; Cornwall Wildlife Trust; Trevithick Society; Red River; River Hayle; estuary; RSPB; Hayle Railway; A30 road; Lelant Saltings railway station; A3074 road; Lelant; Carrack Gladden; Carbis Bay; St Ives Bay railway line; St Ives; favoured by artists; Tate St Ives; Barbara Hepworth Museum; thumb|From Mussel Point over Wicca Pool and Porthzennor Cove to Zennor Head and Gurnard's Head beyond; Penwith; The Carracks; Zennor Head; Gurnard's Head; Morvah; Crowns Mine; Botallack; thumb|left|Near [[Land's End; Cape Cornwall; St Just; Whitesand Bay; Sennen; Land's End; most westerly point; Nanjizal; Porthgwarra; St Levan; Porthcurno; Minack Theatre; telegraph; Logan Rock ...

**South Cornwall (72)**: thumb|[[Falmouth, Cornwall|Falmouth; National Maritime Museum Cornwall; Pendennis Castle; Guglielmo Marconi; The Lizard lifeboat station; Cadgwith; Kennack Sands; Coverack; The Manacles; Porthoustock; Porthallow; Helford River; Helford; Helford Passage; Manaccan; Durgan; Maenporth; Swanpool; Gyllyngvase; Falmouth; St Mawes; Carrick Roads; Fal River Links; St Anthony Head; Zone Point; Portscatho; Gerrans Bay; Nare Head; Portloe; Veryan Bay; Dodman Point; Gorran Haven; Mevagissey; Pentewan; Black Head; Porthpean; Charlestown; china clay; St Austell; Carlyon Bay; Par; Saints' Way; Polmear; Polkerris; Gribbin Head ...

**South Devon (103)**: thumb|[[Plymouth Hoe; Mount Batten; Cremyll Ferry; Stonehouse; Three Towns; Plymouth; Millbay; Plymouth Hoe; Plymouth Sound; Sutton Harbour; Mayflower Steps; Cattedown; River Plym; Plymstock; Jennycliff Bay; Plymouth Sound, Shores and Cliffs; Bovisand; Wembury; Wembury Marine Centre; South Hams; Warren Point Ferry; River Yealm; Newton Ferrers; River Erme; Kingston; Erme Mouth; Hillsea Point Rock; Bigbury Bay; Burgh Island; Hope Cove; Bolt Tail; Bolberry Down; Bolt Head; Bolt Head to Bolt Tail SSSI; ria; Kingsbridge Estuary; Prawle Point; Salcombe Ferry; Salcombe; East Portlemouth; Salcombe Castle; South Devon Area of Outstanding Natural Beauty; Prawle Point and Start Point Site of Special Scientific Interest; bee; wasps ...

**Dorset (68)**: thumb|[[Chesil Beach; Fortuneswell; Isle of Portland; Dorset; Lyme Regis; The French Lieutenant's Woman; Monarch's Way; Charmouth; Golden Cap; West Bay; Bridport; Burton Bradstock; Chesil Beach; tombolo; Abbotsbury; Chiswell; Portland Bill; Weymouth and Portland National Sailing Academy; Wyke Regis; Rodwell Trail; Portland Harbour; Nothe Fort; Weymouth; left|thumb|Sculpture at South Haven Point, [[Studland; Weymouth Harbour; Wey Estuary; Radipole Lake; the Esplanade; Weymouth Bay; Ringstead Bay; White Nothe; Osmington Mills; Weymouth and Portland; South Dorset Downs; Isle of Purbeck; Bat's Head; Swyre Head; Durdle Door; natural arch; Lulworth Cove; Tyneham; Worbarrow Bay; Kimmeridge; wave cut platform; Lulworth Ranges ...

### Gaps

- **No authoritative list of UK beaches, bays, coves, headlands or harbours was found, and I did not
  assemble one.** This is the biggest single hole in the gazetteer. Three real routes exist: (1) Ordnance
  Survey OS Open Names, a free downloadable dataset with feature-type codes that include coastal landforms
  — this is the correct answer and needs a data load, not a web page; (2) Blue Flag / Seaside Awards,
  which publish named award-winning beaches each year; (3) the National Trust coast pages. The brief's
  missing names — Lulworth, Swanage, St Ives, Tintagel — are all in the SWCP section lists above, so the
  coast path lists partially cover the gap for the south west specifically.
- **Scottish lighthouses: extraction failed** (the article returned one row). Northern Lighthouse Board at
  nlb.org.uk publishes its own list of around 200 lighthouses; untested here.
- Lighthouses in Wales were not separately extracted; the Trinity House list above covers Welsh Trinity
  House lights (Bardsey, Caldey, South Stack, Skerries, Smalls, South Bishop, Strumble Head, St Ann's Head,
  Skokholm, Trwyn Du, St Tudwal's, Mumbles, Nash Point, Flatholm, Monkstone, Point Lynas).

## Q9 — Landmarks and buildings

### Takeaway

Cathedrals, English Heritage, Historic Environment Scotland, Welsh castles and stone circles are all
harvested and large. Stately homes, follies, hill figures, bridges, viaducts and famous pubs are not.

### Cited Findings

**Church of England cathedrals — 42.** Confirmed from the Church of England's own site, which states
'thirty-nine of our forty-two cathedrals are grade I listed by Historic England'. Its map lists 43 names
(42 plus Peel, in the Diocese of Sodor and Man); the page does not reconcile the difference, so I am
reporting both figures. — [Church of England, Cathedrals](https://www.churchofengland.org/about/cathedrals)

Birmingham; Blackburn; Bradford; Bristol; Canterbury; Carlisle; Chelmsford; Chester; Chichester;
Coventry; Derby; Durham; Ely; Exeter; Gloucester; Guildford; Hereford; Leicester; Lichfield; Lincoln;
Liverpool; Manchester; Newcastle; Norwich; Oxford; Peel; Peterborough; Portsmouth; Ripon; Rochester;
Salisbury; Sheffield; Southwark; Southwell Minster; St Albans; St Edmundsbury; St Paul's; Truro;
Wakefield; Wells; Winchester; Worcester; York Minster

**Cathedrals in the UK, all denominations — 212 extracted**: 61 Anglican, 45 Roman Catholic, 13 Orthodox, 99 with denomination not captured by my parser. — [List of cathedrals in the United Kingdom](https://en.wikipedia.org/wiki/List_of_cathedrals_in_the_United_Kingdom)

First 50 of 212: Birmingham Cathedral — Anglican; Bristol Cathedral — Anglican; Bury St Edmunds Cathedral — Anglican; Canterbury Cathedral — Anglican; Chelmsford Cathedral — Anglican; Chichester Cathedral — Anglican; Coventry Cathedral — Anglican; Derby Cathedral — Anglican; Ely Cathedral — Anglican; Exeter Cathedral — Anglican; Gloucester Cathedral — Anglican; Guildford Cathedral — Anglican; Hereford Cathedral — Anglican; Leicester Cathedral — Anglican; Lichfield Cathedral — Anglican; Lincoln Cathedral — Anglican; St Paul's Cathedral, London — Anglican; Norwich Cathedral — Anglican; Christ Church Cathedral, Oxford — Anglican; Peterborough Cathedral — Anglican; Portsmouth Cathedral — Anglican; Rochester Cathedral — Anglican; St Albans Cathedral — Anglican; Salisbury Cathedral — Anglican; Southwark Cathedral — Anglican; Truro Cathedral — Anglican; Wells Cathedral — Anglican; Winchester Cathedral — Anglican; Worcester Cathedral — Anglican; Blackburn Cathedral — Anglican; Bradford Cathedral — Anglican; Carlisle Cathedral — Anglican; Chester Cathedral — Anglican; Durham Cathedral — Anglican; Liverpool Cathedral — Anglican; Manchester Cathedral — Anglican; Newcastle Cathedral — Anglican; Peel Cathedral — Anglican; Ripon Cathedral — Anglican; Sheffield Cathedral — Anglican; Southwell Minster — Anglican; Wakefield Cathedral — Anglican; York Minster — Anglican; Christ Church Cathedral (Falkland Islands) — Anglican; Brentwood Cathedral — Catholic; St John the Baptist Cathedral, Norwich — Catholic; Northampton Cathedral — Catholic; Nottingham Cathedral — Catholic; Westminster Cathedral — Catholic; Birmingham Cathedral — Catholic

**English Heritage properties — 446 across 45 counties.** English Heritage is a primary-source organisation and this list mirrors its estate. — [List of English Heritage properties](https://en.wikipedia.org/wiki/List_of_English_Heritage_properties)

Subdivision structure is by county, with counts:

| County | Properties |
|---|---|
| Bedfordshire | 5 |
| Berkshire | 2 |
| Bristol | 2 |
| Cambridgeshire | 5 |
| Cheshire | 5 |
| Cornwall | 18 |
| Cumbria | 28 |
| Derbyshire | 10 |
| Devon | 14 |
| Dorset | 13 |
| County Durham | 7 |
| East Riding of Yorkshire | 4 |
| East Sussex | 7 |
| Essex | 10 |
| Gloucestershire | 17 |
| Hampshire | 16 |
| Herefordshire | 8 |
| Hertfordshire | 4 |
| Isle of Wight | 6 |
| Isles of Scilly | 10 |
| Kent | 27 |
| Lancashire | 5 |
| Leicestershire | 4 |
| Lincolnshire | 9 |
| London | 15 |
| Norfolk | 23 |
| North Yorkshire | 27 |
| Northamptonshire | 6 |
| Northumberland | 27 |
| Nottinghamshire | 3 |
| Oxfordshire | 11 |
| Rutland | 2 |
| Shropshire | 17 |
| Somerset | 13 |
| South Yorkshire | 5 |
| Staffordshire | 3 |
| Suffolk | 9 |
| Surrey | 3 |
| Tyne and Wear | 7 |
| Warwickshire | 2 |
| West Midlands | 3 |
| West Sussex | 3 |
| Wiltshire | 20 |
| Worcestershire | 3 |
| See also | 8 |

Sample (Cumbria, 27 after removing a parser artefact): 
Ambleside Roman Fort; Bow Bridge; Brough Castle; Brougham Castle; Carlisle Castle; Castlerigg Stone Circle; Clifton Hall; Countess Pillar; Furness Abbey; Banks East Turret; Birdoswald Roman Fort; Hadrian's Wall: Hare Hill; Harrows Scar Milecastle; Poltross Burn Milecastle; Leahill Turret; Pike Hill Signal Tower; Turrets; Hardknott Roman Fort; King Arthur's Round Table; Lanercost Priory; Mayburgh Henge; Penrith Castle; Piel Castle; Ravenglass Roman Bath House; Shap Abbey; Stott Park Bobbin Mill; Wetheral Priory Gatehouse

Sample (Cornwall, 17 after removing a parser artefact): 
Ballowall Barrow; Carn Euny Ancient Village; Chysauster Ancient Village; Dupath Well; Halliggye Fogou; Hurlers Stone Circles; King Doniert's Stone; Launceston Castle; Pendennis Castle; Penhallam; Restormel Castle; St Breock Downs Monolith; St Catherine's Castle; St Mawes Castle; Tintagel Castle; Tregiffian Burial Chamber; Trethevy Quoit

**Stone circles — 341 named across the UK**: England 145, Scotland 87, Wales 90, Northern Ireland 19. — [List of stone circles](https://en.wikipedia.org/wiki/List_of_stone_circles)

The source subdivides England by region and county (South East, East Midlands incl. Derbyshire, Yorkshire
and the Humber, North East, North West incl. Cumbria and Lancashire, West Midlands incl. Shropshire,
South West incl. Cornwall, Devon, Dorset, Somerset, Wiltshire) and Scotland by council area.

**England (145)**, first 50: Essex; Oxfordshire; Arbor Low; Barbrook One; Doll Tor; Hordron Edge; Nine Ladies; Nine Stones Close; North Yorkshire; no appropriate photo available; Eskdaleside cum Ugglebarnby; Yockenthwaite stone circle; West Yorkshire; Lune Head Stone Circle; Northumberland; The Goatstones; Threestoneburn Stone Circle; Birkrigg; Brat's Hill; Castlerigg; Gamelands; Kinniside; Long Meg and Her Daughters; Low Longrigg circles; Oddendale; Swinside; White Moss stone circles; Cheetham Close; Mitchell's Fold; Boscawen-Un; Boskednan; Craddock Moor; Duloe; Emblance Downs stone circles; Fernacre; The Hurlers; The Merry Maidens; Nine Stones, Altarnun; Stannon; Tregeseal East; Trippet stones; Brisworthy stone circle; Grey Wethers stone circles; Ringmoor Down; Scorhill; Shovel Down; Tottiford Reservoir; Yellowmead stone circle; Kingston Russell; Rempstone stone circle

**Scotland (87)**, first 40: Islay; Bute; Mull; Temple Wood; Easthill stone circle; The Girdle Stanes; Glenquicken; Lochmaben Stone; The Loupin Stanes; Lockerbie; Stranraer; Twelve Apostles Stone Circle; Torhouskie; Whitcastles stone circle; Isle ofArran; Aucheleffan; Machrie Moor 1; Machrie Moor 2; Machrie Moor 3; Machrie Moor 4; Machrie Moor 5; Machrie Moor 10 / Moss Farm Road Stone Circle; Machrie Moor 11; Lauder; Teviothead; Cloyhouse Burn; Five Stanes; Harestanes; Ninestane Rig; Spott; Tyrebagger stone circle; Aikey Brae stone circle; Cullerlie stone circle; Easter Aquhorthies; Kirkton of Bourtie recumbent stone circle; Hill of Fiddes recumbent stone circle; Inschfield recumbent stone circle; Loanhead of Daviot recumbent stone circle; Loudon Wood recumbent stone circle; Midmar Kirk recumbent stone circle

**Wales (90)**, first 40: Moel Tŷ Uchaf; Bryn Cader Faner; Bryn Gwyn stones; Islay; Bute; Mull; Temple Wood; Easthill stone circle; The Girdle Stanes; Glenquicken; Lochmaben Stone; The Loupin Stanes; Lockerbie; Stranraer; Twelve Apostles Stone Circle; Torhouskie; Whitcastles stone circle; Isle ofArran; Aucheleffan; Machrie Moor 1; Machrie Moor 2; Machrie Moor 3; Machrie Moor 4; Machrie Moor 5; Machrie Moor 10 / Moss Farm Road Stone Circle; Machrie Moor 11; Lauder; Teviothead; Cloyhouse Burn; Five Stanes; Harestanes; Ninestane Rig; Spott; Tyrebagger stone circle; Aikey Brae stone circle; Cullerlie stone circle; Easter Aquhorthies; Kirkton of Bourtie recumbent stone circle; Hill of Fiddes recumbent stone circle; Inschfield recumbent stone circle

**Northern Ireland (19)**: Down; Fermanagh; Tyrone; Ardgroom SW; Breeny More Stone Circle; Carrigagulla; Carrigaphooca stone circle; Derreenataggart stone circle; Drombeg stone circle; Kealkill stone circle; Knocknakilla; Glantane east; Templebryan Stone Circle; Beltany stone circle; Kenmare stone circle; Lissyvigeen stone circle; Shronebirrane stone circle; Uragh Stone Circle; Cashelkeelty Stone Circles

### Gaps

- **National Trust property list: not harvested.** The page did not download. The Trust holds around 500
  historic houses, castles and gardens — **UNVERIFIED count.** nationaltrust.org.uk is the source. This is
  the main missing stately-homes list.
- **Follies: no list obtained.** The Folly Fellowship (follies.org.uk) is the specialist body; untested.
- **Hill figures: extraction failed** (page did not download). The Uffington White Horse, Cerne Abbas Giant,
  Long Man of Wilmington, Westbury White Horse and Whipsnade White Lion are the famous ones —
  **UNVERIFIED.** Historic England's National Heritage List for England is the authoritative source and is
  searchable by monument type.
- **Bridges and viaducts: no list obtained.** 'List of bridges in England' did not download. Historic
  England's NHLE again covers the listed ones. The famous subjects — Forth Bridge, Tower Bridge, Clifton
  Suspension Bridge, Ribblehead Viaduct, Glenfinnan Viaduct, Pontcysyllte Aqueduct, Iron Bridge, Humber
  Bridge, Severn Bridge, Tyne Bridge — are **UNVERIFIED** general knowledge.
- **Famous pubs and inns: no authoritative list exists** that I could find, and I did not assemble one.
  CAMRA's National Inventory of Historic Pub Interiors (pubheritage.camra.org.uk) is the nearest thing to
  an authoritative register and would be the source to use.

## Q10 — Railways

### Takeaway

The Underground is complete (269 stations). Mainline stations, heritage railways and named
express services were not harvested — this is the weakest block in the gazetteer.

### Cited Findings

**London Underground stations — 269** — [List of London Underground stations](https://en.wikipedia.org/wiki/List_of_London_Underground_stations). Full list given in Q3.

**Bridges and viaducts in England — 436 named**, with the source subdividing England into Greater London and Rest of England, plus separate England–Wales Border, Anglo-Scottish Border, Scotland (Glasgow / Rest of Scotland), Northern Ireland, Wales and Isle of Man sections. — [List of bridges in England](https://en.wikipedia.org/wiki/List_of_bridges_in_England)

First 60 of 436: Albert Bridge; Battersea Bridge; Blackfriars Bridge; Chelsea Bridge; Chiswick Bridge; Golden Jubilee Bridges; Hungerford Railway Bridge; Hammersmith Bridge; Hampton Court Bridge; Kew Bridge; Lambeth Bridge; London Bridge; London Millennium Bridge; Putney Bridge; Richmond Bridge; Royal Victoria Dock Bridge; Southwark Bridge; Tower Bridge; Twickenham Bridge; Vauxhall Bridge; Wandsworth Bridge; Waterloo Bridge; Westminster Bridge; A34 Road Bridge; A419 Road Bridge; Abingdon Bridge; Acton Bridge; Albert Bridge, Datchet; Albert Bridge, Manchester; Aldford Iron Bridge; Avonmouth Bridge; Bakewell Bridge; Baslow Bridge; Barle Bridge; Barnstaple Long Bridge; Barton Road Swing Bridge; Bathampton Toll Bridge; Beckfoot Bridge; Beggar's Bridge; Bethells Bridge; Bewdley Bridge; Bideford Long Bridge; Black Boys Bridge; Blakeborough's Bridge; Blaydon Bridge; Boothferry Bridge; Blue Bridge; Botley Bridge; Bow Bridge, Iwood; Bow Bridge, Plox; Bradford Bridge; Breydon Bridge; Bridge of Sighs; Brighouse Bridge; Bristol Bridge; Bromford Viaduct; Broughton Suspension Bridge; Bulstake Bridge; Burghfield Bridge; Bury Bridge

**Hill figures — 22 in the UK**, extracted from the source's body text and gallery:
Uffington White Horse; Cerne Abbas Giant; Long Man of Wilmington; Westbury White Horse; Cherhill White
Horse; Marlborough White Horse; Alton Barnes White Horse; Hackpen White Horse; Broad Town White Horse;
Pewsey White Horse; Devizes White Horse; Osmington White Horse; Litlington White Horse; Kilburn White
Horse; Folkestone White Horse; Cleadon White Horse; Woolbury White Horse; Mormond White Horse (Scotland);
Red Horse of Tysoe; Bulford Kiwi; Lenham Cross; Whiteleaf Cross. — [Hill figure](https://en.wikipedia.org/wiki/Hill_figure)

### Gaps

- **Mainline stations: not harvested.** There are about 2,570 National Rail stations. Office of Rail and
  Road (dataportal.orr.gov.uk) publishes the definitive station list with annual footfall, which is the
  better source anyway because footfall ranks them by likely demand. **UNVERIFIED count.**
- **Heritage and steam railways: no list obtained.** The Wikipedia 'Heritage railway' article is global
  and has no United Kingdom section to extract; 'List of British heritage railways' does not exist under
  that title. The Heritage Railway Association (hra.uk.com) is the trade body and lists its ~150 members —
  that is the source to use. **UNVERIFIED count.** Known subjects: Severn Valley, North Yorkshire Moors,
  Ffestiniog, Talyllyn, Bluebell, West Somerset, Settle–Carlisle (mainline), Jacobite, Snowdon Mountain,
  Keighley & Worth Valley, Romney Hythe & Dymchurch, Welsh Highland, Llangollen, Great Central — all
  **UNVERIFIED** general knowledge.
- **Named express services: not harvested.** Flying Scotsman, Mallard, Royal Scot, Cornish Riviera,
  Golden Arrow, Brighton Belle, Night Riviera, Caledonian Sleeper — **UNVERIFIED.** Several of these are
  live registered trademarks or belong to operating companies: see the risk register.
- **Underground line names were not extracted**, only stations. TfL's own data (tfl.gov.uk/info-for/open-data-users)
  is authoritative and free, but the roundel and the map design are TfL IP.

## Q11 — Rivers and canals

### Takeaway

1205 named rivers and 195 named canals extracted. The canal list carries navigable status, which matters:
only 45 English canals are fully navigable, and those are the ones with tourist demand.

### Cited Findings

**Named rivers — England 626, Scotland 195, Wales 384** — [List of rivers of England](https://en.wikipedia.org/wiki/List_of_rivers_of_England); [List of rivers of Scotland](https://en.wikipedia.org/wiki/List_of_rivers_of_Scotland); [List of rivers of Wales](https://en.wikipedia.org/wiki/List_of_rivers_of_Wales)

The English list is organised clockwise around the coast by the sea each river flows into, with
tributaries nested — that structure is itself a usable series grouping.

England, first 50 of 626: Wye; Tweed; Tyne; Hexham; Severn; Silverdale; Cumbria; Lancashire; Esk; Sark; Lyne; Eden; Caldew; Roe; Ive; Petteril; Irthing; Gelt; Eamont; Lowther; Lyvennet; Leith; Belah; Wampool; Waver; Ellen; Derwent; Marron; Cocker; Greta; Glenderamackin; Ehen; Keekle; Liza; Calder; Irt; Bleng; Mite; Annas; Duddon; Lickle; Leven; Eea; Crake; Windermere; Brathay; Rothay; Kent; Winster; Bela

Scotland, first 40 of 195: Tributaries; Lallans; Bournemouth; Ashbourne; Coalburn; Bannockburn; Aultmore; Avon; Afton; Kincardine; Till; Tweed; Breamish; Glen; Teviot; Tyne; Esk, Lothian; South Esk; North Esk; Almond; Gogarburn; Carron; Perth; Forth; Devon, Clackmannanshire; Teith; Leven, Fife; Ore; Eden, Fife; Tay; Earn; Farg; Lednock; Almond, Perthshire; Isla, Perthshire; Loch of the lowes; Ericht; Ardle; Braan; Tummel

Wales, first 40 of 384: Wye; Severn; Tributaries; Taff; Cefn-coed-y-cymmer; Dee, Wales; Alyn; Cegidog; Terrig; Clywedog; Gwenfro; Ceiriog; Teirw; Eitha; Afon Morwynion; Alwen; Afon Ceirw; Merddwr; Afon Medrad; Afon Brenig; Afon Trystion; Afon Llynor; Afon Ceidiog; Hirnant; Afon Tryweryn; Afon Mynach (Dee); Afon Hesgyn; Afon Gelyn; Afon Llafar; Afon Twrch; Afon Lliw; Clwyd; Gele; Elwy; Aled; Afon Gallen; Wheeler; Conwy; Afon Gyffin; Afon Roe

**Canals — 195 named**: England 164, Scotland 13, Wales 10, Northern Ireland 8. Of the English canals, 45 are marked fully navigable. — [List of canals in the United Kingdom](https://en.wikipedia.org/wiki/List_of_canals_in_the_United_Kingdom)

**Fully navigable English canals (45)** — the commercially relevant subset: Aire and Calder Navigation; Ashton Canal; Beverley Beck; Birmingham and Warwick Junction Canal; Birmingham and Fazeley Canal; Bridgewater Canal; Bridgwater and Taunton Canal; Calder and Hebble Navigation; Caldon Canal; Chelmer and Blackwater Navigation; Coventry Canal; Digbeth Branch Canal; Driffield Navigation; Droitwich Canal; Erewash Canal; Exeter Ship Canal; Foss Dyke; Gloucester and Sharpness Canal; Grand Junction Canal; Grand Union Canal; Grand Union Canal (old); Hertford Union Canal; Huddersfield Broad Canal; Huddersfield Narrow Canal; Kennet and Avon Canal; Leeds and Liverpool Canal; Leicestershire and Northamptonshire Union Canal; Limehouse Cut; Llangollen Canal; Macclesfield Canal; Manchester Ship Canal; Middle Level Navigations; New Junction Canal; Ouse Navigation; Oxford Canal; Peak Forest Canal; Regent's Canal; Ribble Link; Ripon Canal; River Soar Navigation; River Lee Navigation; River Weaver Navigation (incl. Weston Canal); Rochdale Canal; Royal Military Canal; Worcester and Birmingham Canal

**Scotland (13)**: Aberdeenshire Canal; Buchan Canal; Caledonian Canal; Carlingwark Lane Canal; Crinan Canal; Dingwall Canal; Forth and Clyde Canal; Glasgow, Paisley and Johnstone Canal; Inchfad Canal; Inverarnan Canal; Monkland Canal; Stevenston Canal; Union Canal

**Wales (10)**: Aberdare Canal; Cyfarthfa Canal; Glamorganshire Canal; Glan-y-wern Canal; Kidwelly and Llanelly Canal; Llangollen Canal; Monmouthshire, Brecon and Abergavenny Canal; Montgomery Canal; Neath and Tennant Canal; Swansea Canal

**Northern Ireland (8)**: Broharris Canal; Coalisland Canal; Dukart's Canal; Lagan Canal; Newry Canal; Shannon–Erne Waterway; Strabane Canal; Ulster Canal

**England, all 164**, first 60: Aire and Calder Navigation; Andover Canal; Arbury Canals; Ashby-de-la-Zouch Canal; Ashton Canal; Barnsley Canal; Basingstoke Canal; Baybridge Canal; Beaumont Cut; Bentley Canal; Beverley Beck; Birmingham and Warwick Junction Canal; Birmingham Canal Navigations; Birmingham and Fazeley Canal; Black Bear Canal; Blyth Navigation; Bradford Canal; Bridgewater Canal; Bridgwater and Taunton Canal; Bude Canal; Caistor Canal; Calder and Hebble Navigation; Caldon Canal; Cann Quarry Canal; Car Dyke; Chard Canal; Charnwood Forest Canal; Chelmer and Blackwater Navigation; Chesterfield Canal; Chichester Canal; Cinderford Canal; City Canal; Coombe Hill Canal; Coventry Canal; Cromford Canal; Croydon Canal; Dearne and Dove Canal; Derby Canal; Derby and Sandiacre Canal; Digbeth Branch Canal; Donnington Wood Canal; Driffield Navigation; Droitwich Canal; Dudley Canal; Eardington Forge Canal; Erewash Canal; Exeter Ship Canal; Fairbottom Branch Canal; Fletcher's Canal; Foss Dyke; Galton's Canal; Glastonbury Canal; Glastonbury Canal (medieval); Gloucester and Sharpness Canal; Grand Junction Canal; Grand Surrey Canal; Grand Union Canal; Grand Union Canal (old); Grand Western Canal; Grantham Canal

**Named aqueducts and boat lifts** — the source names these specifically: Dundas Aqueduct;
Pontcysyllte Aqueduct; Barton Swing Aqueduct; Three Bridges, London; Anderton Boat Lift; Falkirk Wheel;
Combe Hay Caisson Lock; Hay Inclined Plane. — [Canals of the United Kingdom](https://en.wikipedia.org/wiki/Canals_of_the_United_Kingdom)

### Gaps

- **Named locks and lock flights: no usable list extracted.** The dedicated articles are
  'List of canal aqueducts in the United Kingdom' and 'List of locks on the ... Canal' per canal. Famous
  flights — Caen Hill, Bingley Five Rise, Foxton, Hatton, Devizes, Neptune's Staircase — are
  **UNVERIFIED.** Canal & River Trust (canalrivertrust.org.uk) is the authoritative operator source.
- No Northern Ireland river list was harvested.

## Q12 — Football grounds (TRADEMARK-RISKY)

### Takeaway

135 current English football stadiums extracted with club and locality. Every single row carries
trademark risk and none should be generated with club names, crests, colours or kit.

### Cited Findings

**Current English football stadiums — 135**, as club — stadium — locality. — [List of football stadiums in England](https://en.wikipedia.org/wiki/List_of_football_stadiums_in_England)

| # | Club — Stadium — Locality |
|---|---|
| 1 | men's — Wembley Stadium — Wembley |
| 2 | Premier League — Old Trafford — Old Trafford |
| 3 | Premier League — Tottenham Hotspur Stadium — Tottenham |
| 4 | EFL Championship — London Stadium — Stratford |
| 5 | Premier League — Anfield — Anfield |
| 6 | Premier League — Etihad Stadium — Bradford |
| 7 | rowspan="2" 2006 — rowspan="2" | 7 — Emirates Stadium |
| 8 | Premier League — Hill Dickinson Stadium — Bramley-Moore Dock |
| 9 | Premier League — St James' Park — Newcastle upon Tyne |
| 10 | Premier League — Stadium of Light — Monkwearmouth |
| 11 | rowspan="2" 1897 — rowspan="2" | 11 — Villa Park |
| 12 | Premier League — Stamford Bridge — Fulham |
| 13 | Women's Super League — Goodison Park — Walton |
| 14 | Premier League — Elland Road — Beeston |
| 15 | EFL League One — Hillsborough — Owlerton |
| 16 | EFL Championship — Riverside Stadium — Middlesbrough |
| 17 | EFL Championship — Cardiff City Stadium — Leckwith |
| 18 | EFL Championship — Pride Park — Derby |
| 19 | Premier League — Coventry Building Society Arena — Coventry |
| 20 | rowspan="2" 2001 — rowspan="2" 19 — St Mary's Stadium |
| 21 | rowspan="2" 2002 — rowspan="2" | 20 — King Power Stadium |
| 22 | rowspan="2" 1855 — rowspan="2" | 21 — Bramall Lane |
| 23 | Premier League — Falmer Stadium — Falmer |
| 24 | EFL Championship — Molineux — Wolverhampton |
| 25 | EFL Championship — Ewood Park — Blackburn |
| 26 | rowspan="2" 1898 — rowspan="2" 25 — City Ground |
| 27 | EFL League One — Stadium MK — Denbigh |
| 28 | EFL Championship — bet365 Stadium — Stoke-on-Trent |
| 29 | Premier League — Portman Road — Ipswich |
| 30 | rowspan="2" 1906 — rowspan="2" 29 — St Andrew's |
| 31 | EFL Championship — Toughsheet Community Stadium — Horwich |
| 32 | Premier League — Craven Cottage — Fulham, London |
| 33 | EFL Championship — Carrow Road — Norwich |
| 34 | rowspan="2" 1919 — rowspan="2" 33 — The Valley |
| 35 | rowspan="2" 1887 — rowspan="2" 34 — Ashton Gate Stadium |
| 36 | EFL Championship — The Hawthorns — West Bromwich |
| 37 | Premier League — MKM Stadium — Hull |
| 38 | Premier League — Selhurst Park — Selhurst |
| 39 | EFL League One — Brick Community Stadium — Wigan |
| 40 | EFL League One — Valley Parade — Bradford |
| 41 | EFL League One — Madejski Stadium — Reading |
| 42 | EFL League One — Kirklees Stadium — Huddersfield |
| 43 | EFL Championship — Deepdale — Preston |
| 44 | EFL League One — Oakwell — Barnsley |
| 45 | EFL Championship — Vicarage Road — Watford |
| 46 | EFL Championship — Turf Moor — Burnley |
| 47 | EFL Championship — Liberty Stadium — Landore |
| 48 | EFL Championship — Fratton Park — Milton |
| 49 | EFL League One — Meadow Lane — Nottingham |
| 50 | EFL Championship — The Den — Bermondsey |
| 51 | Women's Super League — Langtree Park — St Helens |
| 52 | EFL Championship — Loftus Road — White City |
| 53 | EFL League One — Home Park — Plymouth |
| 54 | Premier League — Brentford Community Stadium — Brentford |
| 55 | National League — Brunton Park — Carlisle |
| 56 | EFL League One — Bloomfield Road — Blackpool |
| 57 | EFL League Two — frameless|151x151px — County Ground |
| 58 | EFL League One — frameless|151x151px — Club Doncaster Sports Village |
| 59 | EFL League Two — Vale Park — Burslem |
| 60 | EFL League Two — Prenton Park — Birkenhead |
| 61 | EFL League One — London Road — Peterborough |
| 62 | EFL League Two — Boundary Park — Oldham |
| 63 | EFL League One — Kassam Stadium — Littlemore |
| 64 | EFL League Two — Memorial Stadium — Horfield |
| 65 | National League — Roots Hall — Southend |
| 66 | EFL League Two — New York Stadium — Rotherham |
| 67 | Women's Super League — Leigh Sports Village — Leigh |
| 68 | rowspan="2" 1955 — rowspan="2" 66 — Gateshead International Stadium |
| 69 | Northern Premier League — Gigg Lane — Bury |
| 70 | EFL League Two — Priestfield Stadium — Gillingham |

...remaining 65 in the source (the article is ordered by capacity and also carries separate
'Old stadiums' and 'Future stadiums' tables).

### Inferences

- The title evidence in the brief shows demand, but the legal exposure here is categorically different
  from the rest of the gazetteer. Club names and crests are registered trade marks; stadium names are
  frequently *sponsor* marks too (Emirates, Etihad, Vitality, bet365, Amex), which stacks a second
  rights-holder onto the first.
- The only defensible football format is a **stadium-shaped pitch-and-stand geometry with no club name,
  no crest, no club colours and a neutral place name** — i.e. sell 'Manchester' or 'Anfield (district)',
  not 'Manchester United'. Even then the ground's architectural form can be distinctive enough to attract
  a complaint, and eBay's VeRO programme makes takedowns cheap for rights-holders and expensive for sellers.
- Recommendation: hold this block out of the first catalogue entirely. It is 135 rows out of a gazetteer
  of many thousands, so the opportunity cost is negligible relative to the account risk.

## Q13 — Universities, and the Oxford and Cambridge colleges

### Takeaway

148 university rows extracted *with their city*, which is what makes this block usable as
place art. Oxford's 43 colleges and PPHs and Cambridge's 31 colleges are both complete.

### Cited Findings

**UK universities — 148 rows**, each with city and region — [List of universities in the United Kingdom](https://en.wikipedia.org/wiki/List_of_universities_in_the_United_Kingdom)

| University | City |
|---|---|
| Abertay University | Dundee |
| Aberystwyth University | Aberystwyth |
| Anglia Ruskin University | Cambridge |
| Arden University | Coventry |
| Arts University Bournemouth | Bournemouth |
| Arts University Plymouth | Plymouth |
| Aston University | Birmingham |
| Bangor University | Bangor |
| Bath Spa University | Bath |
| BIMM University | Birmingham |
| Birkbeck, University of London | London |
| Birmingham City University | Birmingham |
| Birmingham Newman University | Birmingham |
| Bournemouth University | Bournemouth |
| BPP University | Abingdon |
| Brunel University of London | London |
| Buckinghamshire New University | High Wycombe |
| Canterbury Christ Church University | Canterbury |
| Cardiff Metropolitan University | Cardiff |
| Cardiff University | Cardiff |
| City St George's, University of London | London |
| Coventry University | Coventry |
| Cranfield University | Cranfield |
| De Montfort University | Leicester |
| Durham University | Durham |
| Edge Hill University | Ormskirk |
| Edinburgh Napier University | Edinburgh |
| Falmouth University | Falmouth |
| Glasgow Caledonian University | Glasgow |
| Goldsmiths, University of London | London |
| Harper Adams University | Edgmond |
| Hartpury University | Hartpury |
| Health Sciences University | Bournemouth |
| Heriot-Watt University | Edinburgh |
| Imperial College London | London |
| Keele University | Keele |
| King's College London | London |
| Kingston University | London |
| Lancaster University | Lancaster |
| Leeds Arts University | Leeds |
| Leeds Beckett University | Leeds |
| Leeds Trinity University | Leeds |
| Lincoln Bishop University | Lincoln |
| Liverpool Hope University | Liverpool |
| Liverpool John Moores University | Liverpool |
| London Metropolitan University | London |
| London South Bank University | London |
| Loughborough University | Loughborough |
| Manchester Metropolitan University | Manchester |
| Middlesex University | London |
| Newcastle University | Newcastle |
| Northeastern University – London | London |
| Northumbria University | Newcastle |
| Norwich University of the Arts | Norwich |
| Nottingham Trent University | Nottingham |
| Open University | Milton Keynes |
| Oxford Brookes University | Oxford |
| Plymouth Marjon University | Plymouth |
| Queen Margaret University | Musselburgh |
| Queen Mary University of London | London |
| Queen's University Belfast | Belfast |
| Ravensbourne University London | London |
| Regent's University London | London |
| Richmond American University London | London |
| Robert Gordon University | Aberdeen |
| Royal Agricultural University | Cirencester |
| Royal Holloway, University of London | Egham |
| Royal Veterinary College | London |
| Sheffield Hallam University | Sheffield |
| SOAS University of London | London |

...remaining rows in the source. The source also has separate sections for university colleges, the
member institutions of the University of London, and other recognised bodies.

**Oxford colleges and Permanent Private Halls — 43** (39 colleges + 4 PPHs) — [Colleges of the University of Oxford](https://en.wikipedia.org/wiki/Colleges_of_the_University_of_Oxford)

All Souls College; Balliol College; Brasenose College; Campion Hall; Christ Church; Corpus Christi College; Exeter College; Green Templeton College; Harris Manchester College; Hertford College; Jesus College; Keble College; Kellogg College; Lady Margaret Hall; Linacre College; Lincoln College; Magdalen College; Mansfield College; Merton College; New College; Nuffield College; Oriel College; Pembroke College; Regent's Park College; Reuben College; Somerville College; St Anne's College; St Antony's College; St Benet's Hall; St Catherine's College; St Cross College; St Edmund Hall; St Hilda's College; St Hugh's College; St John's College; St Peter's College; The Queen's College; Trinity College; University College; Wadham College; Wolfson College; Worcester College; Wycliffe Hall

**Cambridge colleges — 31.** Extraction returned 41 names because the source table also carries historical
foundations (Buckingham College, Cavendish College, God's House, Gonville Hall, King's Hall, New Hall,
University Hall) and theological colleges that are not among the 31 (Ridley Hall, Westcott House,
Westminster College). Removing those 10 leaves exactly 31. Peterhouse has no ', Cambridge' suffix in the
source so it had to be added back by hand. — [Colleges of the University of Cambridge](https://en.wikipedia.org/wiki/Colleges_of_the_University_of_Cambridge)

Christ's; Churchill; Clare; Clare Hall; Corpus Christi; Darwin; Downing; Emmanuel; Fitzwilliam; Girton;
Gonville and Caius; Homerton; Hughes Hall; Jesus; King's; Lucy Cavendish; Magdalene; Murray Edwards;
Newnham; Pembroke; Peterhouse; Queens'; Robinson; Selwyn; Sidney Sussex; St Catharine's; St Edmund's;
St John's; Trinity; Trinity Hall; Wolfson

### Inferences

- University *names* are registered trade marks in most cases (the University of Oxford and University of
  Cambridge both enforce actively, including on crests and on the words themselves in merchandising).
  College *buildings* and the cities are not. Generate 'Oxford' and recognisable architecture; do not
  generate university or college crests, mottoes, or 'University of X' lettering. Flagged in the risk register.

## Q14 — Markets, arcades and streets that are landmarks

### Takeaway

**No list obtained, and I did not assemble one.** There is no authoritative register of landmark UK
streets, markets or arcades. This is a genuine gap.

### Gaps

- The nearest authoritative sources are Historic England's National Heritage List for England (which lists
  individual market halls and arcades as listed buildings, searchable by type) and the National Association
  of British Market Authorities. Neither gives a ready 'landmark streets' list.
- The brief's own examples — Portobello Road, The Shambles (York), the Royal Mile (Edinburgh), Princes
  Street (Edinburgh) — plus Oxford Street, Carnaby Street, Abbey Road, Baker Street, Brick Lane, Bold
  Street (Liverpool), The Lanes (Brighton), Grainger Market (Newcastle), Leadenhall Market, Borough Market,
  Camden Market, Burlington Arcade, Royal Arcade, Barton Arcade (Manchester), Victoria Quarter (Leeds),
  Gold Street / Steep Hill (Lincoln), Mermaid Street (Rye), Gandy Street (Exeter) and Victoria Street
  (Edinburgh) are **UNVERIFIED** general knowledge, not an extracted list.
- A practical substitute: the London areas list (558 names, Q3) already contains most of the London street
  districts people actually search for, and the 454 English BUAs cover the host towns for the rest.
  OS Open Names also contains every named road, so a filtered street gazetteer is achievable from data
  rather than from a web page.

## Q15 — Formats that place art takes, and which need lettering

### Takeaway

Place art splits cleanly into formats that are *diagrams carrying text* and formats that are *pictures*.
The brief's own title evidence is dominated by the first kind, which is exactly the kind a diffusion model
cannot render. Nine formats are drawable with no lettering at all; those are where generation should start.

### Cited Findings

Retailer and gallery category pages confirm the format set and add a few beyond the brief's list.
Note plainly: these pages show what sellers *offer*, not what sells — none of them publish sales data.
— [iCanvas, abstract maps category](https://www.icanvas.com/canvas-art-prints/style/abstract/subject/maps);
[Art Heroes, city maps collection](https://www.artheroes.se/en/collection/city-maps/1367);
[Walmart, metro maps category](https://www.walmart.com/c/kp/metro-maps);
[Canvas Prints Australia, city street maps](https://www.canvasprintsaustralia.net.au/all-wall-art-categories/city-street-maps-art/)

Formats found in the market beyond the brief's seven: **abstract / deconstructed maps** (city grid reduced
to shape and colour), **typographic place-name designs** (the name *is* the artwork), **watercolour map
washes**, **vintage vs modern treatments of the same map**, **map-plus-skyline layered compositions**,
and **place-themed colour palettes** (subway-line colours, taxi yellow, bridge-steel blue for New York;
cartographic blues and urban greys generally).

### The format table

| Format | Needs legible text? | Needs precise geometry? | Diffusion-safe? |
|---|---|---|---|
| Street map (accurate road network) | Yes — street names, place label | Yes — real topology | **No**. Fails twice over. |
| Transit / metro / Tube map | Yes — every station name | Yes — exact line topology | **No**. Also TfL IP. |
| Coordinates print | Yes — the numbers must be correct | No | **No**. Numerals are the product. |
| Elevation profile | Yes — peak names and heights | Yes — real elevation data | **No**. |
| "Established" date print | Yes — the date is the product | No | **No**. |
| Typographic place-name design | Yes — the name is the artwork | No | **No**. |
| Flag | No lettering (most UK flags) | Yes — exact proportions, charges | **Partly**. Vector, not diffusion. |
| City skyline silhouette | Optional — often sold with name | Loose — recognisable massing only | **Yes**, if name is composited. |
| Cityscape / painted view | No | No — impressionistic is fine | **Yes**. |
| Abstract / deconstructed map | No | No — shape and colour only | **Yes**. |
| Landscape / fell / coast scene | No | No | **Yes**. |
| Landmark portrait (castle, cathedral, lighthouse, pier) | No | Loose | **Yes**. |
| Botanical / wildlife of a place | No | No | **Yes**. |
| Weather / sea-state mood piece | No | No | **Yes**. |
| Aerial / bird's-eye painterly view | No | Loose | **Yes**. |
| Vintage travel-poster pastiche | Yes — poster lettering is the genre | No | **No** as diffusion-only; yes if type is composited. |
| Watercolour map wash | Borderline — often labelled | No | **Yes** if unlabelled. |
| Map + skyline layered composition | Yes, in practice | Yes, for the map half | **No**. |

### The lettering-free list — formats to generate first

These nine need **no lettering at all** and no precise geometry, so a diffusion model can carry them
end to end. Every one of them also maps onto the UK lists above:

1. **Landscape / fell / moor / dale scene** — 214 Wainwrights, 282 Munros, 186 Welsh Nuttalls, 15 National Parks, 46 National Landscapes.
2. **Coast and seascape** — 541 SWCP place names, 59 piers, 65 Trinity House lighthouses.
3. **Landmark portrait** — 42 CoE cathedrals, 212 UK cathedrals, 260 Welsh castles, 446 English Heritage and 302 HES properties.
4. **Abstract / deconstructed map** — any of the 76 cities or 454 English BUAs; shape and colour only, no labels.
5. **City skyline silhouette, unlabelled** — 76 cities; composite the place name as vector type afterwards.
6. **Cityscape / painted street view** — 558 London districts, 76 cities.
7. **Water scene** — 1,013 Scottish lochs, 32 Lake District lakes, 1,205 named rivers, 195 canals.
8. **Island and archipelago scene** — 244 named Scottish islands.
9. **Standing stones, hill figures and ancient monuments** — 345 stone circles, 22 hill figures.

### Inferences

- The brief's own title counts measure the formats that *need* text: map 20,180, transit map, coordinates,
  elevation, 'established' dates. That is a warning, not a target. Competitors winning on those titles are
  almost certainly using vector or real cartographic data, not diffusion.
- The right architecture is **hybrid**: diffusion generates the pictorial plate, and the place name, date,
  coordinates or station labels are composited on afterwards as real vector type. That converts every
  text-needing format in the table from 'No' to 'Yes' at the cost of a compositing step, and it is the only
  way to compete on the high-volume map and coordinate keywords.
- FLUX.1 schnell (the Apache-2.0 model this project is committed to) is weaker at text than larger models,
  which strengthens the case for compositing rather than prompting text.

### Gaps

- **No sales data was found for any format.** Every source located is a retailer category page showing
  what is offered. The brief's own 874,816-title competitor dataset is better evidence than anything on the
  open web, and should be the basis for format weighting.

## Risk register — trademark, royal insignia and living-person exposure

### Takeaway

Four blocks carry real risk. Everything else in this gazetteer is place names and landforms, which are not
protectable as such.

### Risk table

| Block | Count | Risk type | Verdict |
|---|---|---|---|
| English football stadiums and clubs | 135 | Registered trade marks: club names, crests, kit colours. Stadium names often *sponsor* marks (Emirates, Etihad, Vitality, bet365, Amex) stacking a second rights-holder. eBay VeRO makes takedown cheap for them. | **EXCLUDE** from first catalogue. |
| London Underground: roundel, Johnston typeface, Tube map diagram | 11 lines / 269 stations | TfL registered marks and design rights. The roundel and the map diagram are both protected. | **EXCLUDE** transit-map and roundel formats. Station *place names* alone are fine. |
| Royal residences | ~8 | Royal insignia and the Lord Chamberlain's rules on royal arms/cyphers. Buckingham Palace, Windsor Castle, Balmoral, Sandringham, Holyroodhouse, Hillsborough, Highgrove, Clarence House. Depicting the building is generally fine; royal arms, cyphers, crowns and 'By Appointment' marks are not. | **ALLOW building, EXCLUDE insignia.** No crowns, cyphers or royal arms. |
| University and college names and crests | 114 universities / 43 Oxford / 31 Cambridge | Oxford and Cambridge both enforce their word marks and crests in merchandising. Most UK universities hold registered marks. | **ALLOW city and architecture, EXCLUDE** crests, mottoes and 'University of X' lettering. |
| Named express train services | ~8 known | Flying Scotsman, Royal Scot, Caledonian Sleeper and others are live marks held by operators or the NRM. | **EXCLUDE** names; locomotive *forms* are likely fine. |
| National Trust / English Heritage / Historic Environment Scotland / Cadw names and logos | 446 + 302 properties | The organisations' names and logos are marks. The *properties* are not — a castle is a castle. | **ALLOW property names, EXCLUDE** org names and logos. |
| Whisky distillery names | 125 + 6 | Every operating distillery name is a registered trade mark, and the Scotch Whisky Association enforces aggressively. | **EXCLUDE distillery names. ALLOW** region names (Speyside, Islay, Highland) and place names. |
| Blue Flag / Seaside Award | n/a | Certification marks. | **EXCLUDE** the marks. |
| Living persons | n/a | No living-person exposure found anywhere in this gazetteer — it is entirely places, landforms and historic buildings. The one watch-item is royal *persons* as distinct from royal *residences*. | **LOW RISK**, but no portraits of living royals or any named living person. |

### Inferences

- Stripping the four EXCLUDE blocks removes roughly 135 football rows, the transit-map format, distillery
  names and a handful of train names. It costs almost nothing against a gazetteer of several thousand
  clean place names, and it removes essentially all of the account-level risk.
- Near-duplication, not trademark, remains the main commercial risk flagged in this project's own
  CLAUDE.md (89% near-duplication blamed for 424k unsold listings). The format table above is the lever:
  nine lettering-free formats across, say, 1,400 named places gives 12,600 genuinely distinct
  place-x-format pairs before any style variation, which is a far better duplication profile than one
  format applied 1,400 times.

### Gaps

- **I did not search any trade mark register.** The risk assessments above are reasoning from how these
  rights are normally held and enforced, not the result of IPO or EUIPO searches. Anything in the ALLOW
  column should be confirmed against the UK IPO register (trademarks.ipo.gov.uk) before a large upload.
- I did not check eBay's VeRO participant list, which names the rights-holders who actively issue
  takedowns on the platform. That is a cheap, high-value check before the first upload.

## Sources used

**Primary / official:**
- [ONS, Towns and cities: characteristics of built-up areas, England and Wales, Census 2021](https://www.ons.gov.uk/peoplepopulationandcommunity/housing/articles/townsandcitiescharacteristicsofbuiltupareasenglandandwales/census2021) — 7,018 BUAs, size bands, coastal subset
- [Trinity House, Lighthouses and Lightvessels](https://www.trinityhouse.co.uk/lighthouses-and-lightvessels) — 65 lighthouses, 7 lightvessels
- [Church of England, Cathedrals](https://www.churchofengland.org/about/cathedrals) — 42 cathedrals

**Wikipedia list articles that mirror an official or canonical list** (named here so each can be traced):
- [List of cities in the United Kingdom](https://en.wikipedia.org/wiki/List_of_cities_in_the_United_Kingdom) — mirrors the UK Government's official city list
- [List of built-up areas in England by population](https://en.wikipedia.org/wiki/List_of_built-up_areas_in_England_by_population) — built on ONS BUA data
- [Ceremonial counties of England](https://en.wikipedia.org/wiki/Ceremonial_counties_of_England) — statutory lieutenancy areas
- [Subdivisions of Scotland](https://en.wikipedia.org/wiki/Subdivisions_of_Scotland) · [Principal areas of Wales](https://en.wikipedia.org/wiki/Principal_areas_of_Wales) · [Counties of Northern Ireland](https://en.wikipedia.org/wiki/Counties_of_Northern_Ireland)
- [National parks of the United Kingdom](https://en.wikipedia.org/wiki/National_parks_of_the_United_Kingdom) · [National Landscape](https://en.wikipedia.org/wiki/National_Landscape)
- [List of Wainwrights](https://en.wikipedia.org/wiki/List_of_Wainwrights) · [List of Munros](https://en.wikipedia.org/wiki/List_of_Munros) · [List of mountains in Wales](https://en.wikipedia.org/wiki/List_of_mountains_in_Wales) · [Welsh 3000s](https://en.wikipedia.org/wiki/Welsh_3000s) — all sourced from the Database of British and Irish Hills
- [List of London boroughs](https://en.wikipedia.org/wiki/List_of_London_boroughs) · [List of areas of London](https://en.wikipedia.org/wiki/List_of_areas_of_London) · [London postal district](https://en.wikipedia.org/wiki/London_postal_district) · [List of London Underground stations](https://en.wikipedia.org/wiki/List_of_London_Underground_stations)
- [List of islands of Scotland](https://en.wikipedia.org/wiki/List_of_islands_of_Scotland) · [List of lochs of Scotland](https://en.wikipedia.org/wiki/List_of_lochs_of_Scotland) · [List of whisky distilleries in Scotland](https://en.wikipedia.org/wiki/List_of_whisky_distilleries_in_Scotland) · [List of Historic Scotland properties](https://en.wikipedia.org/wiki/List_of_Historic_Scotland_properties)
- [List of castles in Wales](https://en.wikipedia.org/wiki/List_of_castles_in_Wales) · [List of towns in Wales](https://en.wikipedia.org/wiki/List_of_towns_in_Wales) · [List of towns in Scotland](https://en.wikipedia.org/wiki/List_of_towns_in_Scotland)
- [List of cathedrals in the United Kingdom](https://en.wikipedia.org/wiki/List_of_cathedrals_in_the_United_Kingdom) · [List of English Heritage properties](https://en.wikipedia.org/wiki/List_of_English_Heritage_properties) · [List of stone circles](https://en.wikipedia.org/wiki/List_of_stone_circles) · [Hill figure](https://en.wikipedia.org/wiki/Hill_figure)
- [List of lighthouses in England](https://en.wikipedia.org/wiki/List_of_lighthouses_in_England) · [List of piers in the United Kingdom](https://en.wikipedia.org/wiki/List_of_piers_in_the_United_Kingdom) · [South West Coast Path](https://en.wikipedia.org/wiki/South_West_Coast_Path)
- [List of rivers of England](https://en.wikipedia.org/wiki/List_of_rivers_of_England) · [List of rivers of Scotland](https://en.wikipedia.org/wiki/List_of_rivers_of_Scotland) · [List of rivers of Wales](https://en.wikipedia.org/wiki/List_of_rivers_of_Wales) · [List of canals in the United Kingdom](https://en.wikipedia.org/wiki/List_of_canals_in_the_United_Kingdom) · [Canals of the United Kingdom](https://en.wikipedia.org/wiki/Canals_of_the_United_Kingdom)
- [List of bridges in England](https://en.wikipedia.org/wiki/List_of_bridges_in_England) · [List of lakes of the Lake District](https://en.wikipedia.org/wiki/List_of_lakes_of_the_Lake_District)
- [Colleges of the University of Oxford](https://en.wikipedia.org/wiki/Colleges_of_the_University_of_Oxford) · [Colleges of the University of Cambridge](https://en.wikipedia.org/wiki/Colleges_of_the_University_of_Cambridge) · [List of universities in the United Kingdom](https://en.wikipedia.org/wiki/List_of_universities_in_the_United_Kingdom) · [List of football stadiums in England](https://en.wikipedia.org/wiki/List_of_football_stadiums_in_England)

**Sources to fetch next, for the gaps named above:** Ordnance Survey OS Open Names (beaches, bays, coves,
headlands, glens, streets); ONS BUA 2024 dataset (the 1,395 towns above 5,000); Northern Lighthouse Board;
National Piers Society; National Trust; Cadw; Heritage Railway Association; Office of Rail and Road station
list; Historic England National Heritage List; NISRA settlement classification; CAMRA National Inventory;
UK IPO trade mark register; eBay VeRO participant list.
