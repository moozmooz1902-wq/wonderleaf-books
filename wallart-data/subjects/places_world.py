#!/usr/bin/env python3
"""World cities and landscapes. The mined competitor titles put city names
at the top of the place demand - new york, chicago, london, paris, dubai,
toronto, singapore, sydney, cape town - so a UK-only list leaves the
biggest slice of the market on the table.

Cities are named plainly. No trademarked skyline, no branded building, no
night-illumination that carries its own copyright (see ip_check.py)."""

CITIES_EUROPE = [
 "Paris","Rome","Florence","Venice","Milan","Naples","Verona","Siena","Pisa",
 "Turin","Bologna","Genoa","Palermo","Amalfi","Positano","Cinque Terre",
 "Barcelona","Madrid","Seville","Valencia","Granada","Bilbao","San Sebastian",
 "Toledo","Cordoba","Malaga","Lisbon","Porto","Sintra","Madeira","Amsterdam",
 "Rotterdam","Utrecht","The Hague","Delft","Bruges","Ghent","Antwerp",
 "Brussels","Luxembourg City","Berlin","Munich","Hamburg","Cologne",
 "Frankfurt","Dresden","Heidelberg","Nuremberg","Rothenburg","Vienna",
 "Salzburg","Innsbruck","Hallstatt","Zurich","Geneva","Bern","Lucerne",
 "Interlaken","Zermatt","Prague","Cesky Krumlov","Budapest","Krakow","Warsaw",
 "Gdansk","Wroclaw","Bratislava","Ljubljana","Lake Bled","Zagreb","Dubrovnik",
 "Split","Hvar","Belgrade","Sarajevo","Sofia","Bucharest","Athens","Santorini",
 "Mykonos","Crete","Rhodes","Corfu","Istanbul","Cappadocia","Copenhagen",
 "Aarhus","Stockholm","Gothenburg","Oslo","Bergen","Tromso","the Lofoten Islands",
 "Helsinki","Rovaniemi","Reykjavik","Tallinn","Riga","Vilnius","Dublin",
 "Galway","Cork","Kilkenny","the Ring of Kerry","the Cliffs of Moher",
 "Connemara","Dingle","Killarney","Monaco","Nice","Cannes","Marseille",
 "Lyon","Bordeaux","Toulouse","Strasbourg","Annecy","Chamonix","Colmar",
 "Mont Saint-Michel","Saint-Malo","Honfleur","Giverny","Provence lavender fields",
]

CITIES_AMERICAS = [
 "New York City","Brooklyn","Manhattan skyline","Chicago","Boston",
 "Philadelphia","Washington DC","Miami","Key West","Savannah","Charleston",
 "New Orleans","Nashville","Austin","Houston","Dallas","San Antonio",
 "Denver","Salt Lake City","Santa Fe","Phoenix","Las Vegas","Los Angeles",
 "San Diego","San Francisco","Sausalito","Monterey","Big Sur","Portland",
 "Seattle","Anchorage","Honolulu","Maui","Detroit","Minneapolis","Milwaukee",
 "Pittsburgh","Cleveland","St Louis","Kansas City","Toronto","Montreal",
 "Quebec City","Vancouver","Victoria BC","Calgary","Banff","Lake Louise",
 "Jasper","Ottawa","Halifax","Whistler","Mexico City","Oaxaca","Guanajuato",
 "San Miguel de Allende","Tulum","Cancun","Havana","Trinidad Cuba",
 "San Juan Puerto Rico","Cartagena","Bogota","Medellin","Quito","Cusco",
 "Machu Picchu","Lima","La Paz","the Uyuni salt flats","Santiago",
 "Valparaiso","Patagonia","Torres del Paine","Buenos Aires","Montevideo",
 "Rio de Janeiro","Sao Paulo","Salvador Brazil","the Amazon rainforest",
 "Iguazu Falls","the Galapagos Islands","Antigua Guatemala","Panama City",
]

CITIES_ASIA_PACIFIC = [
 "Tokyo","Kyoto","Osaka","Nara","Hakone","Mount Fuji","Hiroshima","Sapporo",
 "Kanazawa","Takayama","Nikko","Seoul","Busan","Jeju Island","Beijing",
 "Shanghai","Hong Kong","Guilin","Zhangjiajie","Chengdu","Xian","Lhasa",
 "Taipei","Singapore","Kuala Lumpur","Penang","Bangkok","Chiang Mai",
 "Krabi","Phuket","Koh Samui","Hanoi","Ha Long Bay","Hoi An","Ho Chi Minh City",
 "Luang Prabang","Siem Reap","Angkor Wat","Yangon","Bagan","Kathmandu",
 "Pokhara","the Everest region","Delhi","Jaipur","Udaipur","Jodhpur",
 "Varanasi","Kerala backwaters","Goa","Mumbai","Darjeeling","Colombo",
 "Kandy","the Maldives","Bali","Ubud","Jakarta","Komodo","Raja Ampat",
 "Manila","Palawan","Boracay","Sydney","Melbourne","Brisbane",
 # Perth, Western Australia. Perth in Perthshire is in places_uk.py, and the
 # bare name in both lists is the same subject string, so the same SKU twice.
 "Perth Australia",
 "Adelaide","Hobart","Cairns","the Great Barrier Reef","Uluru",
 "the Great Ocean Road","Byron Bay","Noosa","Auckland","Wellington",
 "Queenstown","Milford Sound","Rotorua","Christchurch","Fiordland",
 "Dubai","Abu Dhabi","Doha","Muscat","Petra","Wadi Rum","Jerusalem",
 "Tel Aviv","Beirut","Baku","Tbilisi","Yerevan","Samarkand","Bukhara",
]

CITIES_AFRICA = [
 "Cape Town","Table Mountain","Johannesburg","Durban","the Garden Route",
 "Stellenbosch","the Drakensberg","Kruger National Park","the Okavango Delta",
 "Victoria Falls","the Serengeti","the Ngorongoro Crater","Mount Kilimanjaro",
 "Zanzibar","Nairobi","the Masai Mara","Lamu","Addis Ababa","the Simien Mountains",
 "Lalibela","Marrakech","Fes","Chefchaouen","Essaouira","Casablanca",
 "the Sahara at Merzouga","the Atlas Mountains","Tunis","Cairo","Luxor",
 "Aswan","the Nile at Aswan","Dakar","Accra","Lagos","Windhoek",
 "the Namib Desert","Sossusvlei","Deadvlei","the Skeleton Coast",
 "Madagascar","the Avenue of the Baobabs","Seychelles","Mauritius",
]

LANDSCAPE_TYPES = [
 "a misty pine forest","an alpine meadow","a lavender field at dusk",
 "a sunflower field","a wheat field at harvest","terraced rice paddies",
 "an olive grove","a vineyard in autumn","a cherry orchard in blossom",
 "a desert dune at sunrise","a salt flat","a canyon at golden hour",
 "a glacier","an iceberg","a frozen lake","the northern lights",
 "a starry desert sky","the milky way over mountains","a coastal lighthouse",
 "a pier at sunset","a harbour at dawn","a fishing boat at anchor",
 "a rocky shoreline","a tidal estuary","a mangrove channel","a coral reef",
 "a waterfall in rainforest","a mountain tarn","a heather moor in August",
 "a bluebell wood in May","an autumn beech wood","a snow-covered forest",
 "a country lane in spring","a drystone wall across fells","a hay meadow",
 "a poppy field","a chalk downland","a reedbed at sunset","a saltmarsh",
 "a peat bog","a limestone pavement","a sea stack","a blowhole coastline",
 "a volcanic crater","a hot spring","a geyser field","a bamboo forest",
 "a eucalyptus forest","a redwood grove","a baobab at sunset","a savanna acacia",
]

ALL = (CITIES_EUROPE + CITIES_AMERICAS + CITIES_ASIA_PACIFIC + CITIES_AFRICA
       + LANDSCAPE_TYPES)

if __name__ == "__main__":
    import collections
    for k, v in list(globals().items()):
        if isinstance(v, list) and k.isupper() and k != "ALL":
            print(f"{k:<22}{len(v):>6}")
    d = [x for x, c in collections.Counter(ALL).items() if c > 1]
    print(f"{'TOTAL':<22}{len(ALL):>6}   unique {len(set(ALL))}   dupes {d}")
