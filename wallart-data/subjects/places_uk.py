#!/usr/bin/env python3
"""UK places worth putting on a wall. Curated, not scraped.

Every entry is a real place a UK buyer might search for. No trademarked
landmark, no private estate, no brand. Grouped so the mix can be weighted
later - a catalogue that is 90% Munros would be a strange catalogue.
"""

NATIONAL_PARKS = [
 "the Lake District","Snowdonia","the Peak District","Dartmoor","Exmoor",
 "the Yorkshire Dales","the North York Moors","Northumberland National Park",
 "the Brecon Beacons","the Pembrokeshire Coast","the Cairngorms",
 "Loch Lomond and the Trossachs","the New Forest","the South Downs",
 "the Broads","Bannau Brycheiniog",
]

AONB = [
 "the Cotswolds","the Chilterns","the Malvern Hills","the Quantock Hills",
 "the Mendip Hills","Cranborne Chase","the Dorset AONB",
 "Chichester Harbour","the Surrey Hills","the Kent Downs","the High Weald",
 "Dedham Vale","the Suffolk Coast","the Norfolk Coast","the Lincolnshire Wolds",
 "Cannock Chase","the Shropshire Hills","the Wye Valley","the Gower Peninsula",
 "the Llyn Peninsula","Anglesey","the Clwydian Range","the Forest of Bowland",
 "Arnside and Silverdale","the Solway Coast","the North Pennines",
 "the Nidderdale AONB","the Howardian Hills","the Tamar Valley",
 "the Blackdown Hills","the East Devon AONB","the North Devon Coast",
 "Bodmin Moor","the Lizard Peninsula","the Roseland Peninsula",
 "the Northumberland Coast","the Arnside Knott",
]

MOUNTAINS_HILLS = [
 "Ben Nevis","Scafell Pike","Snowdon","Yr Wyddfa","Helvellyn","Skiddaw",
 "Great Gable","Blencathra","Catbells","Haystacks","Striding Edge",
 "Cadair Idris","Tryfan","Glyder Fawr","Crib Goch","Pen y Fan","Sugar Loaf",
 "Ben Macdui","Cairn Gorm","Braeriach","Lochnagar","Ben Lomond","Ben More",
 "Buachaille Etive Mor","Bidean nam Bian","Aonach Eagach","Liathach",
 "An Teallach","Suilven","Stac Pollaidh","Quinag","Ben Hope","Schiehallion",
 "Ben Lawers","The Cobbler","Goatfell","Sgurr Alasdair","Bla Bheinn",
 "Kinder Scout","Mam Tor","Stanage Edge","Win Hill","Shutlingsloe",
 "Pen-y-ghent","Ingleborough","Whernside","Roseberry Topping","Sutton Bank",
 "High Cup Nick","Cross Fell","The Cheviot","Hadrian's Wall at Steel Rigg",
 "Haytor","Hound Tor","Bellever Tor","Brown Willy","Carn Brea","Glastonbury Tor",
 "Pendle Hill","Mow Cop","the Wrekin","the Long Mynd","Caer Caradoc",
 "Thorpe Cloud","Dovedale","the Roaches","Hen Cloud","Curbar Edge",
]

COAST = [
 "Durdle Door","Lulworth Cove","Old Harry Rocks","Chesil Beach","Kimmeridge Bay",
 "the Seven Sisters","Beachy Head","Birling Gap","Botany Bay Kent",
 "the White Cliffs of Dover","Camber Sands","Dungeness","Holkham beach",
 "Wells-next-the-Sea","Blakeney Point","Southwold beach",
 "Walberswick","Covehithe","Cromer pier","Hunstanton cliffs","Brancaster",
 "Bamburgh beach","Holy Island","Lindisfarne","the Farne Islands",
 "Dunstanburgh Castle","Druridge Bay","Saltburn-by-the-Sea","Whitby harbour",
 "Robin Hood's Bay","Runswick Bay","Staithes","Filey Brigg","Flamborough Head",
 "Bempton Cliffs","Spurn Point","Formby beach","Crosby beach","Blackpool sands",
 "Morecambe Bay","St Bees Head","Silecroft beach","Allonby","Rhossili Bay",
 "Three Cliffs Bay","Worms Head","Barafundle Bay","Broad Haven","Whitesands Bay",
 "Newgale","Freshwater West","Tenby harbour","Saundersfoot","Mwnt beach",
 "Llangrannog","Aberdaron","Porthdinllaen","Whistling Sands","Newborough beach",
 "South Stack","Porth Swtan","Kynance Cove","Porthcurno","Sennen Cove",
 "Lands End","Cape Cornwall","St Michael's Mount","Marazion","Praa Sands",
 "Lizard Point","Kennack Sands","Coverack","Helford Passage","Gorran Haven",
 "Polperro","Looe","Talland Bay","Whitsand Bay","Bigbury-on-Sea","Burgh Island",
 "Hope Cove","Thurlestone","Bantham","Blackpool Sands Devon","Slapton Sands",
 "Start Point","Dartmouth harbour","Salcombe estuary","Croyde Bay","Woolacombe",
 "Putsborough","Saunton Sands","Lynmouth","Valley of Rocks","Clovelly",
 "Hartland Quay","Bude breakwater","Widemouth Bay","Crackington Haven",
 "Boscastle harbour","Tintagel","Trebarwith Strand","Polzeath","Daymer Bay",
 "Rock Cornwall","Padstow harbour","Trevone Bay","Constantine Bay","Treyarnon",
 "Bedruthan Steps","Mawgan Porth","Watergate Bay","Fistral beach","Crantock",
 "Holywell Bay","Perranporth","St Agnes Head","Chapel Porth","Portreath",
 "Godrevy","Gwithian","Hayle Towans","Carbis Bay","St Ives harbour",
 "Porthmeor beach","Zennor","Gurnard's Head","Pendeen Watch","Botallack",
 "the Needles","Alum Bay","Freshwater Bay","Compton Bay","Shanklin Chine",
 "Mullion Cove","Cadgwith","Church Cove","St Abbs","Coldingham Bay",
 "Bass Rock","North Berwick","Tantallon","Elie harbour","Anstruther",
 "Crail harbour","St Andrews West Sands","Lunan Bay","Stonehaven harbour",
 "Dunnottar","Bow Fiddle Rock","Findhorn","Sandwood Bay","Durness",
 "Balnakeil Bay","Achmelvich","Clachtoll","Luskentyre","Seilebost",
 "Traigh Mhor","Vatersay","Calgary Bay","Iona","Staffa","Fingal's Cave",
]

LOCHS_LAKES_RIVERS = [
 "Loch Lomond","Loch Ness","Loch Awe","Loch Katrine","Loch Tay","Loch Rannoch",
 "Loch Tummel","Loch Maree","Loch Assynt","Loch Shiel","Loch Morar","Loch Etive",
 "Loch Leven","Loch Duich","Loch Coruisk","Loch Torridon","Loch Broom",
 "Loch Lochy","Loch Garten","Loch an Eilein","Loch Muick","Loch Affric",
 "Windermere","Derwentwater","Ullswater","Coniston Water","Buttermere",
 "Crummock Water","Wastwater","Thirlmere","Grasmere","Rydal Water",
 "Ennerdale Water","Loweswater","Bassenthwaite Lake","Haweswater",
 "Tarn Hows","Blea Tarn","Red Tarn","Llyn Idwal","Llyn Ogwen","Llyn Padarn",
 "Llyn Gwynant","Llyn y Fan Fach","Llangorse Lake","Bala Lake",
 "the River Thames at Henley","the River Wye at Symonds Yat","the River Dart",
 "the River Severn at Ironbridge","the River Tyne at Newcastle",
 "the River Ouse at York","the River Cam at Cambridge","the River Avon at Bath",
 "the River Tweed","the River Spey","the River Dee at Chester",
 "the Norfolk Broads at Horsey","Ranworth Broad","the Fens at Wicken",
]

CITIES_TOWNS = [
 "London","Edinburgh","Glasgow","Cardiff","Belfast","Manchester","Liverpool",
 "Birmingham","Leeds","Sheffield","Bristol","Newcastle upon Tyne","Nottingham",
 "Leicester","Brighton","Bath","York","Oxford","Cambridge","Canterbury",
 "Durham","Chester","Lincoln","Norwich","Exeter","Plymouth","Portsmouth",
 "Southampton","Winchester","Salisbury","Wells","Gloucester","Worcester",
 "Hereford","Shrewsbury","Ludlow","Stratford-upon-Avon","Warwick","Rye",
 "Lewes","Arundel","Whitstable","Deal","Folkestone","Hastings","Eastbourne",
 "Margate","Broadstairs","Southwold","Aldeburgh","Burnham Market","Holt",
 "Stamford","Louth","Beverley","Harrogate","Knaresborough","Ripon","Richmond",
 "Skipton","Settle","Hebden Bridge","Haworth","Saltaire","Ilkley","Otley",
 "Kendal","Keswick","Ambleside","Grasmere village","Hawkshead","Cartmel",
 "Ulverston","Whitehaven","Cockermouth","Penrith","Appleby","Alnwick",
 "Berwick-upon-Tweed","Hexham","Corbridge","Barnard Castle","Stokesley",
 "Helmsley","Pickering","Thirsk","Masham","Leyburn","Hawes","Reeth",
 "Grassington","Malham","Clitheroe","Lancaster","Garstang","Chipping",
 "Buxton","Bakewell","Castleton","Eyam","Matlock","Ashbourne","Leek",
 "Ironbridge","Bridgnorth","Much Wenlock","Bishop's Castle","Hay-on-Wye",
 "Ross-on-Wye","Tewkesbury","Cirencester","Stow-on-the-Wold","Burford",
 "Bourton-on-the-Water","Bibury","Castle Combe","Lacock","Bradford-on-Avon",
 "Frome","Shaftesbury","Sherborne","Bridport","Lyme Regis","Beer","Sidmouth",
 "Topsham","Totnes","Dartmouth","Salcombe","Kingsbridge","Modbury","Tavistock",
 "Chagford","Moretonhampstead","Dulverton","Dunster","Porlock","Minehead",
 "Watchet","Glastonbury","Street","Frome town","Bruton","Castle Cary",
 "Launceston","Bodmin","Fowey","Mevagissey","Truro","Falmouth","Penryn",
 "Helston","Penzance","Mousehole","Newlyn","Marazion town","St Just",
 "Wadebridge","Bude","Camelford","Liskeard","Saltash","Calstock",
 "Conwy","Llandudno","Beaumaris","Caernarfon","Porthmadog","Portmeirion",
 "Harlech","Barmouth","Dolgellau","Machynlleth","Aberystwyth","Aberaeron",
 "New Quay","Cardigan","Fishguard","St Davids","Solva","Narberth",
 "Laugharne","Llandeilo","Brecon","Crickhowell","Abergavenny","Monmouth",
 "Chepstow","Tenby town","Swansea","Mumbles","Llanelli","Carmarthen",
 "Stirling","Perth","Dundee","Aberdeen","Inverness","Fort William","Oban",
 "Pitlochry","Dunkeld","Aberfeldy","Callander","Dunblane","Linlithgow",
 "St Andrews","Falkland","Culross","Dunfermline","North Berwick town",
 "Dunbar","Melrose","Kelso","Jedburgh","Peebles","Moffat","Dumfries",
 "Kirkcudbright","Portpatrick","Girvan","Ayr","Largs","Rothesay","Tobermory",
 "Portree","Plockton","Ullapool","Gairloch","Applecross","Dornoch","Thurso",
 "Stromness","Kirkwall","Lerwick","Tarbert","Stornoway","Castlebay",
 "Armagh","Bangor County Down","Portrush","Ballycastle","Enniskillen",
 "Derry","Newcastle County Down","Strangford","Donaghadee","Cushendun",
]

ISLANDS = [
 "the Isle of Skye","the Isle of Mull","the Isle of Arran","Islay","Jura",
 "Tiree","Coll","Colonsay","Eigg","Rum","Canna","Muck","Raasay","Harris",
 "Lewis","North Uist","South Uist","Benbecula","Barra","Eriskay","St Kilda",
 "Orkney","Hoy","Westray","Papa Westray","Shetland","Unst","Yell","Fair Isle",
 "Bute","Cumbrae","Gigha","Kerrera","Lismore","Luing","Seil","Ulva","Iona isle",
 "Lundy","the Isles of Scilly","St Marys","Tresco","Bryher","St Martins",
 "the Isle of Man","the Isle of Wight","Hayling Island","Brownsea Island",
 "Caldey Island","Skomer","Skokholm","Ramsey Island","Bardsey Island",
 "Anglesey isle","Holy Island Anglesey","Rathlin Island","Lambay",
]

LANDMARKS_NATURAL = [
 "Stonehenge","Avebury","Castlerigg stone circle","the Rollright Stones",
 "the Callanish Stones","the Ring of Brodgar","Skara Brae","Maeshowe",
 "the Giant's Causeway","the Dark Hedges","Fingal's Cave Staffa",
 "Cheddar Gorge","Gordale Scar","Malham Cove","Janet's Foss","Aysgarth Falls",
 "High Force","Low Force","Hardraw Force","Catrigg Force","Kinder Downfall",
 "Thor's Cave","Lud's Church","the Devil's Arrows","Brimham Rocks",
 "the Cow and Calf","Almscliffe Crag","Hound Tor remains","Wistman's Wood",
 "Puzzlewood","the Forest of Dean","Sherwood Forest","the Major Oak",
 "Epping Forest","Burnham Beeches","Savernake Forest","Kielder Forest",
 "Glen Affric","Rothiemurchus","Abernethy Forest","the Hermitage Dunkeld",
 "the Fairy Pools Skye","the Quiraing","the Old Man of Storr","Neist Point",
 "the Fairy Glen","Mealt Falls","Kilt Rock","Elgol","Sligachan",
 "Glen Coe","Glen Etive","Rannoch Moor","the Devil's Staircase",
 "Glenfinnan viaduct","the Jacobite line","Corrieshalloch Gorge",
 "the Falls of Measach","Plodda Falls","the Falls of Bruar","Steall Falls",
 "Pistyll Rhaeadr","Swallow Falls Betws-y-Coed","Aber Falls","Henrhyd Falls",
 "Sgwd yr Eira","the Four Waterfalls Walk","Dan yr Ogof","the Elan Valley",
 "the Horseshoe Pass","the Devil's Bridge Ceredigion","Pontcysyllte Aqueduct",
 "the Ribblehead Viaduct","the Settle to Carlisle line","the Forth Bridge",
 "the Clifton Suspension Bridge","the Humber Bridge","the Menai Bridge",
 "the Severn Bridge","the Tyne Bridge","Durham Cathedral from the river",
 "Ely Cathedral from the fens","Lincoln Cathedral on the hill",
 "Salisbury Cathedral from the water meadows","Wells Cathedral",
 "Fountains Abbey","Rievaulx Abbey","Whitby Abbey","Tintern Abbey",
 "Bolton Abbey","Glastonbury Abbey","Lindisfarne Priory","Melrose Abbey",
 "Corfe Castle","Bamburgh Castle","Alnwick Castle","Dunstanburgh",
 "Warkworth Castle","Lindisfarne Castle","Eilean Donan","Urquhart Castle",
 "Stirling Castle","Edinburgh Castle rock","Tantallon Castle","Dunnottar Castle",
 "Kilchurn Castle","Castle Stalker","Caerphilly Castle","Conwy Castle",
 "Harlech Castle","Caernarfon Castle","Beaumaris Castle","Carreg Cennen",
 "Pembroke Castle","Carew Castle","Chepstow Castle","Raglan Castle",
 "Goodrich Castle","Ludlow Castle","Stokesay Castle","Kenilworth Castle",
 "Framlingham Castle","Orford Ness","Bodiam Castle","Leeds Castle Kent",
 "Dover Castle","Pevensey","Arundel Castle","Carisbrooke","Restormel",
 "Tintagel Castle","Pendennis Castle","St Mawes","Dunster Castle",
]

ALL = (NATIONAL_PARKS + AONB + MOUNTAINS_HILLS + COAST + LOCHS_LAKES_RIVERS
       + CITIES_TOWNS + ISLANDS + LANDMARKS_NATURAL)

if __name__ == "__main__":
    import collections
    groups = {k: v for k, v in globals().items()
              if isinstance(v, list) and k.isupper() and k != "ALL"}
    for k, v in groups.items():
        print(f"{k:<22}{len(v):>6}")
    d = [x for x, c in collections.Counter(ALL).items() if c > 1]
    print(f"{'TOTAL':<22}{len(ALL):>6}   unique {len(set(ALL))}   dupes {d}")
