#!/usr/bin/env python3
"""Plants. The biggest subject group in the mined competitor titles once
people are ruled out, so it carries real weight. Common names only - no
cultivar trademarks, no breeder-protected variety names."""

GARDEN_FLOWERS = [
 "a single anemone","white anemones","japanese anemone","a dahlia",
 "cafe au lait dahlia","pompon dahlia","a peony","coral peony","tree peony",
 "a garden rose","an english rose","a climbing rose","rose hips","ranunculus",
 "pink tulips","parrot tulips","white tulips","fringed tulips","daffodils",
 "narcissus","snowdrops","crocuses","bluebells","grape hyacinth","hyacinth",
 "allium heads","nerine","amaryllis","freesia","sweet peas","delphiniums",
 "lupins","foxgloves","hollyhocks","snapdragons","stocks","nigella",
 "love-in-a-mist","cosmos","zinnia","marigold","calendula","nasturtium",
 "sunflower","helenium","rudbeckia","echinacea","gaillardia","coreopsis",
 "aster","michaelmas daisy","chrysanthemum","gerbera","carnation","dianthus",
 "sweet william","phlox","penstemon","salvia","agastache","monarda",
 "verbena bonariensis","scabious","knautia","astrantia","alchemilla mollis",
 "geranium cranesbill","hardy geranium","hellebore","christmas rose",
 "lenten rose","primrose","polyanthus","auricula","cyclamen","violet",
 "pansy","viola","forget-me-not","wallflower","honesty","aquilegia",
 "columbine","bleeding heart","solomon's seal","lily of the valley",
 "camellia","magnolia branches","cherry blossom","apple blossom",
 "wisteria","clematis","honeysuckle","jasmine","passion flower",
 "hydrangea heads","lacecap hydrangea","oakleaf hydrangea","lilac",
 "mock orange","buddleia","fuchsia","begonia","impatiens","petunia",
 "lobelia","alyssum","osteospermum","gazania","dahlia pompon",
 "lily","stargazer lily","tiger lily","calla lily","arum lily","canna lily",
 "iris","bearded iris","siberian iris","flag iris","gladiolus","crocosmia",
 "red hot poker","agapanthus","nerine bowdenii","colchicum","sternbergia",
]

WILDFLOWERS = [
 "wild poppies","field poppy","welsh poppy","oxeye daisy","cow parsley",
 "queen anne's lace","hogweed","wild carrot","yarrow","meadowsweet",
 "ragged robin","red campion","white campion","bladder campion","corncockle",
 "cornflower","corn marigold","scabious field","devil's-bit scabious",
 "knapweed","thistles","spear thistle","melancholy thistle","teasels",
 "burdock","dandelion clock","coltsfoot","hawkbit","cat's ear","goat's beard",
 "buttercup","celandine","marsh marigold","water lily","yellow flag",
 "purple loosestrife","rosebay willowherb","great willowherb","hemp agrimony",
 "valerian","red valerian","foxglove wild","toadflax","yellow rattle",
 "eyebright","selfheal","betony","wood sage","bugle","ground ivy",
 "wild thyme","marjoram","clover","red clover","bird's-foot trefoil",
 "vetch","tufted vetch","meadow vetchling","restharrow","sainfoin",
 "harebell","bellflower","sheep's-bit","heather","bell heather","ling heather",
 "cross-leaved heath","gorse","broom","bilberry","crowberry","bog cotton",
 "bog asphodel","sundew","butterwort","orchid common spotted","bee orchid",
 "pyramidal orchid","early purple orchid","twayblade","wild garlic",
 "ramsons","wood anemone","wood sorrel","dog violet","primrose wild",
 "cowslip","oxlip","snake's head fritillary","wild daffodil","star of bethlehem",
 "sea holly","sea thrift","sea campion","samphire","sea kale","marram grass",
 "yellow horned poppy","viper's bugloss","birdsfoot","kidney vetch",
]

FOLIAGE_TREES = [
 "eucalyptus sprigs","eucalyptus silver dollar","olive branch","bay leaves",
 "fern fronds","hart's tongue fern","maidenhair fern","bracken","polypody",
 "monstera leaf","philodendron leaf","banana leaf","palm leaf","fan palm",
 "rubber plant leaf","fiddle leaf fig","ivy","variegated ivy","hosta leaves",
 "heuchera leaves","bergenia","acanthus","euphorbia","hellebore foliage",
 "box topiary","yew hedge","beech hedge","oak leaves","acorns",
 "english oak","ancient oak","sessile oak","beech tree","copper beech",
 "silver birch","downy birch","birch grove","ash tree","rowan with berries",
 "hawthorn blossom","hawthorn berries","blackthorn","sloe berries","elder",
 "elderflower","elderberry","hazel catkins","alder","willow","weeping willow",
 "pussy willow","pollarded willow","field maple","sycamore","horse chestnut",
 "conkers","sweet chestnut","lime tree","london plane","poplar","aspen",
 "scots pine","caledonian pine","larch","douglas fir","norway spruce",
 "cedar of lebanon","monkey puzzle","juniper","holly with berries","mistletoe",
 "ginkgo leaves","japanese maple","acer palmatum","maple leaves","liquidambar",
 "magnolia tree","cherry tree","crab apple","apple tree","pear blossom",
 "quince blossom","fig leaves","vine leaves","grapevine","hop bine",
 "bamboo","pampas grass","miscanthus","stipa grass","feather grass",
 "grasses and seedheads","wheat ears","barley","oats","rye grass",
 "wild oats","quaking grass","hare's tail grass","bulrush","reeds","sedge",
]

HERBS_EDIBLE_FUNGI = [
 "lavender stems","french lavender","rosemary sprig","thyme","sage leaves",
 "mint","basil","oregano","chives","chive flowers","parsley","coriander",
 "dill","fennel heads","tarragon","lemon balm","borage","nasturtium leaves",
 "garlic bulb","onion","shallot","leek flower","artichoke head","cardoon",
 "rhubarb","strawberries","raspberries","blackberries","blueberries",
 "redcurrants","blackcurrants","gooseberries","cherries","plums","damsons",
 "figs","pomegranate","lemon branch","orange branch","olive with fruit",
 "pumpkin","squash","gourds","sweetcorn","chilli peppers","tomatoes on the vine",
 "fly agaric","chanterelle","porcini","morel","shaggy ink cap","puffball",
 "oyster mushroom","penny bun","parasol mushroom","bracket fungus",
 "lichen","moss","sphagnum moss","reindeer lichen","seaweed","bladderwrack",
 "kelp","sea lettuce","coral weed","succulents","echeveria","aloe vera",
 "jade plant","string of pearls","sedum","houseleek","prickly pear",
 "barrel cactus","saguaro cactus","agave","yucca","air plant","staghorn fern",
 "orchid stem","phalaenopsis orchid","cymbidium orchid","dendrobium orchid",
 "protea","king protea","banksia","leucadendron","strelitzia",
 "bird of paradise flower","anthurium","heliconia","frangipani","hibiscus",
 "bougainvillea","oleander","jacaranda blossom","mimosa","wattle",
 "dried hydrangea","dried poppy heads","honesty seed heads","lunaria",
 "nigella seed heads","allium seed heads","teasel heads","phlomis seed heads",
 "hare's tail dried","statice","strawflower","bunny tails","dried lavender",
]

ALL = GARDEN_FLOWERS + WILDFLOWERS + FOLIAGE_TREES + HERBS_EDIBLE_FUNGI

if __name__ == "__main__":
    import collections
    for k, v in list(globals().items()):
        if isinstance(v, list) and k.isupper() and k != "ALL":
            print(f"{k:<22}{len(v):>6}")
    d = [x for x, c in collections.Counter(ALL).items() if c > 1]
    print(f"{'TOTAL':<22}{len(ALL):>6}   unique {len(set(ALL))}   dupes {d}")
