#!/usr/bin/env python3
"""Buildings, details and structures. Added 11 Oct 2026 as a sixth kind.

enumerable_subject_lists.md draws the line for this block and it is followed
here: architectural STYLES and FEATURES are free and highly enumerable, while
anything that is a manufactured product - a car, a motorcycle, an aircraft, a
locomotive, a camera, a named chair - carries live trade-mark risk in the name
and the badge, and in the case of furniture UK unregistered design right too.
So there are no vehicles and no designer furniture in this file. Vernacular
buildings and plain structures are the safe, under-served slice, and they are
also the ones that look like somewhere rather than like a product.

Nothing here names a real individual building. "A Gothic cathedral west
front" is a building type; a particular cathedral is a place, and places live
in places_uk.py where the freedom-of-panorama reasoning already applies.
"""

BRITISH_STYLES = [
 "a Georgian townhouse front","a Georgian terrace in brick",
 "a Victorian red brick terrace","a Victorian villa with bay windows",
 "a Tudor timber framed house","a Jacobean gabled manor",
 "a Queen Anne doorway","a Regency stucco crescent",
 "an Arts and Crafts cottage","an Edwardian semi with a tiled path",
 "a 1930s suburban semi with a sunburst gate","an Art Deco cinema front",
 "a modernist white villa","a brutalist concrete tower",
 "a post war council block","a Gothic cathedral west front",
 "a Norman round arched church door","a Saxon stone church tower",
 "a perpendicular church window","a nonconformist chapel front",
 "a Scottish baronial tower house","a crow stepped gable house",
 "a Welsh chapel in grey stone","an Ulster farmhouse",
 "a Cotswold stone cottage","a thatched Devon longhouse",
 "a flint and brick Norfolk cottage","a weatherboarded Kentish house",
 "a pantiled Yorkshire farmhouse","a slate roofed Cumbrian farmstead",
]

VERNACULAR = [
 "an oast house with a cowl","a shepherd's hut on wheels",
 "a dovecote","a tower windmill","a post mill","a smock mill",
 "a watermill and wheel","a tide mill","a lighthouse on a rock",
 "a harbour lighthouse at the pier head","a lightkeeper's cottage",
 "a row of beach huts","a single blue beach hut","a boathouse on stilts",
 "a net drying shed","a fisherman's lockup","a lobster pot store",
 "a highland croft house","a bothy in a glen","a blackhouse with a thatch",
 "a bell tent in a field","a shepherd's bothy in snow",
 "a stone barn with ventilation slits","a Dutch barn",
 "a tithe barn interior","a granary on mushroom stones",
 "a hop kiln","a lime kiln","a pottery bottle kiln","a tin mine engine house",
 "a colliery winding tower","a railway signal box","a station waiting room",
 "a railway water tower","a level crossing gate","a goods shed",
 "a seaside bandstand","a pier pavilion","a lido and diving board",
 "a cricket pavilion","a village hall","a bus shelter on a green",
 "a red telephone box","a pillar box on a wall","a village pump",
 "a market cross","a lychgate","a tin tabernacle chapel",
 "a shepherd's fold in the hills","a drystone sheepfold","a gamekeeper's hut",
]

DETAILS = [
 "a sash window with twelve panes","a Georgian fanlight",
 "a bow shop window","a leaded casement window","a rose window tracery",
 "a quatrefoil window","an oriel window","a dormer window in a tiled roof",
 "a Dutch gable","a stepped gable","a bargeboard with a finial",
 "a thatched ridge pattern","a slate roof with graded courses",
 "a pantile roof detail","a chimney stack with pots",
 "a twisted Tudor chimney","a weathervane with a cockerel",
 "a clock face on a tower","a sundial on a wall","a boot scraper",
 "a brass letter plate","a six panel front door","a stable door",
 "a church door with iron straps","a porch with turned posts",
 "a cast iron balcony railing","a spiral iron staircase",
 "a wrought iron gate scroll","a park railing and finials",
 "a Doric column","an Ionic capital","a Corinthian capital",
 "a fluted pilaster","a dentil cornice","a stone corbel head",
 "a gargoyle spout","a green man roof boss","a vaulted stone ceiling",
 "a fan vault","a hammerbeam roof truss","a cruck frame",
 "an encaustic tiled floor","a terrazzo floor pattern",
 "a stained glass transom","a glass brick wall","a flint knapped wall",
 "a herringbone brick panel","a drystone wall with throughstones",
 "a cob wall under a thatch cap","a lath and plaster wall",
]

STRUCTURES = [
 "a packhorse bridge","a clapper bridge","a stone arched road bridge",
 "a railway viaduct across a valley","an aqueduct carrying a canal",
 "a suspension bridge tower","a cast iron footbridge",
 "a swing bridge over a dock","a canal lock and gates","a lock keeper's hut",
 "a canal tunnel mouth","a towpath bridge","a weir and sluice",
 "a sea wall and steps","a groyne running into the sea","a stone jetty",
 "a slipway and winch","a breakwater and beacon","a pier ironwork",
 "a dock crane","a wooden trestle jetty","a ford and footbridge",
 "a stile in a drystone wall","a kissing gate","a five bar gate",
 "a sheep creep in a wall","a cattle grid","a milestone",
 "a fingerpost signpost","a stone bothy marker cairn","a trig point pillar",
 "a hollow way between hedges","a ha ha in a park","a walled garden door",
 "an espaliered wall and fruit trees","a glasshouse and vents",
 "a cold frame","a potting shed window","a bee bole in a wall",
 "a dew pond and fence",
]

TOWNSCAPE = [
 "a row of simplified shopfronts","a cobbled alley between buildings",
 "a mews of coach houses","a market hall arcade",
 "a covered market roof structure","a glazed station canopy",
 "a terrace of coloured houses","a hillside of stacked houses",
 "a harbourside row of cottages","a street of white Georgian fronts",
 "a seafront terrace with balconies","a crescent of tall houses",
 "a square with railings and plane trees","an almshouse row",
 "a row of weavers' cottages with long windows","a back to back terrace yard",
 "a chapel and schoolhouse side by side","a pub on a corner",
 "a high street of mixed rooflines","a mill and chimney above a town",
]

ALL = BRITISH_STYLES + VERNACULAR + DETAILS + STRUCTURES + TOWNSCAPE

if __name__ == "__main__":
    import collections
    for k, v in list(globals().items()):
        if isinstance(v, list) and k.isupper() and k != "ALL":
            print(f"{k:<20}{len(v):>6}")
    d = [x for x, c in collections.Counter(ALL).items() if c > 1]
    print(f"{'TOTAL':<20}{len(ALL):>6}   unique {len(set(ALL))}   dupes {d}")
