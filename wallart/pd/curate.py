#!/usr/bin/env python3
"""
Curate harvested public-domain records into a listable wall-art catalogue.

    python3 curate.py --records pd/raw/records --out pd            # -> artworks.jsonl.gz, SUMMARY.md
    python3 curate.py --records pd/raw/records --out pd --min-score 20

Input: the {source}.jsonl.gz files written by harvest.py.
Output: {out}/artworks.jsonl.gz and {out}/SUMMARY.md.

Pipeline (each record stops at the first filter it fails; counts go in
SUMMARY.md):

  no_image          no full-resolution URL
  licence           not CC0 / Public Domain Mark
  not_wall          objects (furniture, ceramics, coins, arms, textiles ...),
                    ephemera, cigarette/trade cards, fragments
  photo_people      photographs of people (carte de visite, portraits ...)
  copyright_uk      artist died after 1955, or no death year and the work /
                    artist is too recent to be sure (UK term is life + 70)
  bad_title         untitled, fragments, "study for", album leaves, series
                    cards, title pages ...
  sensitive         nudity, gore/violence, racist or offensive historic terms
  too_small         long side < 2000 px (only where the size is known)
  low_demand        score below --min-score (obscure portraits of sitters,
                    anonymous ornament prints, unthemed objects ...)
  no_english_title  Dutch-only title with no usable English subject
  compliance        eBay title fails compliance.check (VeRO words)
  duplicate_work    same artist + same work already kept (best copy wins)
  duplicate_title   eBay title already used by another artwork

The Met / Rijksmuseum give no pixel size in metadata; those records pass the
size filter as "unknown" (image_width/height null) and should be checked at
download time.
"""

import argparse
import collections
import functools
import gzip
import hashlib
import json
import random
import re
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import compliance  # noqa: E402

UK_CUTOFF_DEATH = 1955          # PD in the UK in 2026: died 1955 or earlier
MIN_LONG_SIDE = 2000
MAX_TITLE = 80

THEMES = ["birds", "horses", "dogs", "cats", "farm_animals", "wild_animals", "sea_life",
          "insects_butterflies", "botanical_flowers", "fruit_food", "landscapes",
          "seascapes_ships", "japanese_woodblock", "famous_masters", "portraits",
          "city_architecture", "maps_vintage", "posters_vintage", "religious_art",
          "abstract_modern", "still_life", "other"]

STORE_OF = {}
for t in ("famous_masters", "japanese_woodblock", "landscapes", "city_architecture"):
    STORE_OF[t] = "posterleaf-store1"
for t in ("birds", "horses", "dogs", "cats", "farm_animals", "wild_animals", "sea_life",
          "insects_butterflies"):
    STORE_OF[t] = "mercury-usm"
for t in ("botanical_flowers", "fruit_food", "still_life", "religious_art"):
    STORE_OF[t] = "lunar-kms"
for t in ("seascapes_ships", "maps_vintage", "posters_vintage", "portraits",
          "abstract_modern", "other"):
    STORE_OF[t] = "luxvia-art"
STORES = ["posterleaf-store1", "mercury-usm", "lunar-kms", "luxvia-art"]

# --------------------------------------------------------------------------
# what belongs on a wall  (from build_art_catalogue.py, extended)
# --------------------------------------------------------------------------
WALL = re.compile(
    r"paint|print|drawing|watercolo|woodblock|woodcut|etching|engraving|"
    r"lithograph|poster|\bmaps?\b|cartograph|atlas|photograph|album|scroll|fresco|"
    r"illustration|plate|panel|miniature|pastel|charcoal|sketch|gouache|"
    r"aquatint|mezzotint|drypoint|ukiyo|surimono|chromolitho|book|codices|"
    r"manuscript|folio|design|graphic|works on paper|\bart\b|image|gravure|stencil|"
    r"ink on|pencil|chalk|tempera|oil on|on canvas|on panel|on paper|print",
    re.I)
# Checked against classification/objectName (and medium for a few words that
# only ever mean an object).
NOT_WALL = re.compile(
    r"andiron|vase|coin|medal|sword|armor|armour|helmet|dagger|rifle|"
    r"pistol|furniture|chair|table\b|cabinet|desk|chest|drawer|bureau|"
    r"snuffbox|teapot|bowl|dish|plate\b|platter|saucer|tureen|"
    r"cup\b|mug\b|jug|jar\b|bottle|flask|decanter|goblet|tankard|"
    r"figurine|statuette|sculpture|bust\b|relief|plaque|medallion|"
    r"textile|dress|coat\b|shoe|hat\b|fan\b|glove|apron|costume\b|"
    r"jewel|ring\b|necklace|bracelet|brooch|pendant|earring|"
    r"watch\b|clock|instrument|violin|piano|flute|drum\b|"
    r"fragment|sherd|shard|tile\b|brick|pot\b|pottery|porcelain|ceramic|faience|"
    r"stoneware|earthenware|glass\b|stained glass|enamel|lacquer|ivory|netsuke|jade|"
    r"button|buckle|spoon|fork|knife|candlestick|lamp|mirror|"
    r"box\b|case\b|binding|sampler|quilt|carpet|rug\b|coverlet|tapestry|embroider|lace\b|"
    r"certificate|indenture|bookplate|trade card|invitation|playing card|"
    r"stove|kettle|basket|tray|stand\b|frame\b|model\b|tool\b|weapon|"
    r"cigarette|tobacco|baseball card|trading card|ephemera|banknote|stamp\b|"
    r"wallpaper sample|pattern book|furnishing|metalwork|silver\b|gold\b|bronze|"
    r"woodwork|mold\b|mould\b|seal\b|token|scarab|amulet|mask\b|doll|toy\b|"
    r"negative|lantern slide|stereograph|stereo card|stereoview|postcard|"
    r"penning|munt|scale model|ship model|daguerreotype|tintype|ambrotype|carte-de-visite|"
    r"cabinet card|cabinet photograph",
    re.I)

PHOTO = re.compile(r"photograph|albumen|gelatin silver|salted paper|platinum print|"
                   r"collodion|cyanotype|photogravure|\bfoto", re.I)
PEOPLE = re.compile(r"portrait|\bmr\.?\b|\bmrs\.?\b|\bmiss\b|\bman\b|\bwoman\b|\bmen\b|"
                    r"\bwomen\b|\bgirl|\bboy|child|family|\bfamilie|portret|lady|"
                    r"gentleman|people|group|soldier|sitter|figure|couple|wedding|"
                    r"\bhis\b|\bher\b|historical persons|actor|actress|dancer|bride", re.I)

# Titles that make a print unsellable however good the picture is.
BAD_TITLE = re.compile(
    r"^untitled|^\[|fragment|sherd|study for|studies for|studie voor|verso|recto|"
    r"^plate \d+$|^page \d+|^no\. ?\d+$|unidentified|album leaf|^leaf from|"
    r"from the .{0,40}series|\(N\d+\)|\(T\d+\)|trade card|"
    r"cigarette|tobacco|business card|letterhead|^titelpagina|title page|"
    r"^blad met|^schetsblad|sketchbook page|^sheet of studies|^studies|^study of|"
    r"^(?:design|designs|drawing|sketch|study|project|proposal) for (?:an? |the |two |three )?"
    r"(?:[\w-]+ ){0,3}(?:ceiling|wall|panel|frame|chair|table|cup|clock|vase|snuff|watch|"
    r"ring|brooch|jewel|sword|gun|pistol|monument|tomb|altar|lock|key|handle|mantel\w*|"
    r"chimney\w*|overdoor|door|window|furniture|cabinet|bed|sofa|settee|candelabr\w*|"
    r"lamp|textile|carpet|rug|wallpaper|fabric|silver\w*|border|fan|box|urn|tureen|"
    r"stove|grate|fireplace|console|commode|bookcase|mirror|chandelier|sconce|lantern|"
    r"railing|gate|balustrade|staircase|stair|column|capital|pilaster|cornice|moulding|"
    r"molding|ornament\w*|decoration|trim|tassel|lace|embroider\w*|garniture|salt|"
    r"spoon|fork|knife|plate|dish|bowl|ewer|pitcher|jug|teapot|coffee\w*|sugar\w*|"
    r"inkstand|snuffbox|buckle|button|necklace|pendant|bracelet|earring|tiara|crown|"
    r"medal|coin|seal|monogram|cipher|letter|title|frontispiece|cover|binding|bookplate)\b|"
    r"^overdoor|^mantel|^sidewall|^wallpaper|^textile|^fragment|"
    r"^ornament|^ornamenten|^rand|^fries|^border|^frieze|^cartouche|^vignet|"
    r"^studieblad|^after$|^before$|^initial|^letter [a-z]$|^alphabet|^tekstblad|^text|^blank|^empty|"
    r"^proof|^trial proof|^counterproof|^reverse|^back of|^modelblad|^pagina|"
    r"^kopstuk|^sluitstuk|^embleem|^wapen|^coat of arms|^arms of|^seal of|"
    r"^medal|^munt|^penning|^kaart met|^almanak|^kalender|^calendar|"
    r"^exlibris|^ex libris|^bookplate|^book cover|^boekband|^omslag|^cover",
    re.I)

NON_LATIN = re.compile(r"[^\x00-\x7FÀ-ɏ‘’“”–—]")

# Nudity, gore/violence, explicit. Matched on title + tags.
SENSITIVE = re.compile(
    r"\bnude|\bnudes\b|\bnaked|nudity|\bnaakt|erotic|\bsex\b|sexual|\bbreast|nipple|"
    r"genital|penis|vagina|buttock|partes posteriores|\bbathers?\b|bathing wom|"
    r"undress|quasi-nude|\bharem\b|odalisque|brothel|prostitut|courtesan|whore|"
    r"\blust\b|seduc|\bleda\b|\bsatyr|priapus|\bvenus\b|\bsusanna\b|\bbathsheba\b|"
    r"\bdanae\b|\blucretia\b|\brape\b|\braped\b|abduction|"
    r"murder|massacre|slaughter|\bkill|execution|executed|behead|decapitat|"
    r"\btorture|corpse|cadaver|suicide|\bhanged|\bhanging of|gallows|gibbet|"
    r"holofernes|head of (?:saint |st\. )?john the baptist|\bsalome\b|"
    r"\bdead\b|\bdeath of\b|\bdying\b|\bblood|bloody|wounded|mutilat|dissect|"
    r"flaying|flayed|martyrdom|\bmartyr|slain|carnage|atrocit|\bwar dead|"
    r"\bdeath\b|memento mori|macabre|\bdevil|satan|"
    r"\bdemons?\b|\bwitch|sabbat|\bhell\b|inferno|temptation of|\bdrunk|vomit|urinat|"
    r"defecat|\bexcrement|debauch|orgy|orgie|caricature|satire|satirical|spotprent|cartoon",
    re.I)
# Racist / offensive historic language. Titles with these are dropped
# outright, not rewritten.
OFFENSIVE = re.compile(
    r"\bnegro|\bnegress|\bnigg|\bcoon\b|darkie|darky|pickaninny|picaninny|mammy|"
    r"\bsavages?\b|\bsquaw|redskin|red indian|mulatt|\bhalf-?breed|\bcoolie|"
    r"chinaman|\bchinee|\bjap\b|\bjaps\b|\bnip\b|\bjew\b|\bjews\b|\bjewess|"
    r"blackamoor|hottentot|bushm[ae]n|\beskimo|\bgypsy|\bgipsy|"
    r"\bgypsies|\bzigeuner|\bheathen|\bbarbarian|\bcannibal|cripple|"
    r"\bidiot|lunatic|imbecile|\bmidget|\bdwarf|\bfreak|slave|slavery|"
    r"\bnazi|swastika|hitler|ku klux|\bkkk\b|minstrel|golliwog|golly\b|"
    r"\bmohammedan|\binfidel",
    re.I)

MUSEUM = re.compile(r"museum|museo|gallery|galerie|rijks|smithsonian|metropolitan|"
                    r"art institute|cleveland|yale|national gallery|\bmet\b|collection",
                    re.I)

# Artists a British print buyer searches for by name (score points).
# Natural-history "famous" names are scored but keep their subject theme.
FAMOUS = {
    "vincent van gogh": 100, "claude monet": 95, "katsushika hokusai": 95,
    "utagawa hiroshige": 85, "ando hiroshige": 85, "gustav klimt": 90, "rembrandt": 85,
    "johannes vermeer": 90, "pierre-auguste renoir": 80, "auguste renoir": 80,
    "edgar degas": 80, "paul cezanne": 75, "paul gauguin": 75, "edouard manet": 75,
    "j. m. w. turner": 85, "joseph mallord william turner": 85, "william turner": 60,
    "john constable": 75, "thomas gainsborough": 70, "william blake": 70,
    "john william waterhouse": 85, "john everett millais": 75,
    "dante gabriel rossetti": 70, "edward burne-jones": 70, "burne-jones": 70,
    "william morris": 80, "alphonse mucha": 80, "henri de toulouse-lautrec": 80,
    "edvard munch": 80, "gustave dore": 70, "caspar david friedrich": 75,
    "hieronymus bosch": 80, "pieter bruegel": 80, "pieter brueghel": 75,
    "sandro botticelli": 80, "leonardo da vinci": 85, "michelangelo": 80,
    "raphael": 75, "caravaggio": 80, "francisco goya": 80, "francisco de goya": 80,
    "diego velazquez": 75, "el greco": 70, "peter paul rubens": 70,
    "albrecht durer": 80, "john singer sargent": 75, "winslow homer": 70,
    "mary cassatt": 70, "james mcneill whistler": 70, "camille pissarro": 70,
    "georges seurat": 75, "henri rousseau": 70, "amedeo modigliani": 75,
    "egon schiele": 75, "wassily kandinsky": 80, "vasily kandinsky": 80,
    "piet mondrian": 75, "kitagawa utamaro": 70, "utagawa kuniyoshi": 75,
    "henri matisse": 80, "paul klee": 70, "franz marc": 70, "kazimir malevich": 60,
    "maria sibylla merian": 70, "pierre-joseph redoute": 75, "pierre joseph redoute": 75,
    "john james audubon": 85, "ernst haeckel": 80, "john gould": 70, "edward lear": 60,
    "mark catesby": 55, "basilius besler": 60, "robert jacob gordon": 20,
    "jan van huysum": 55, "rachel ruysch": 55, "jan davidsz de heem": 50,
    "berthe morisot": 65, "alfred sisley": 65, "gustave caillebotte": 65,
    "eugene delacroix": 60, "jean-francois millet": 60, "jean-baptiste-camille corot": 60,
    "odilon redon": 65, "henri fantin-latour": 60, "james tissot": 60,
    "frederic leighton": 60, "lawrence alma-tadema": 60, "george stubbs": 75,
    "edwin landseer": 65, "beatrix": 0, "carl larsson": 65, "hilma af klint": 60,
    "ohara koson": 75, "ohara shoson": 70, "kawase hasui": 0, "ito jakuchu": 70,
    "tsukioka yoshitoshi": 60, "kawanabe kyosai": 60, "shibata zeshin": 55,
    "jan steen": 50, "frans hals": 60, "jacob van ruisdael": 55, "aelbert cuyp": 50,
    "hendrick avercamp": 60, "canaletto": 70, "giovanni battista piranesi": 65,
    "francesco guardi": 55, "titian": 70, "jan van eyck": 70, "hans holbein": 60,
    "lucas cranach": 55, "gerard david": 40, "william hogarth": 55,
    "aubrey beardsley": 65, "walter crane": 55, "kate greenaway": 55,
    "arthur rackham": 70, "edmund dulac": 65, "kay nielsen": 0, "john tenniel": 65,
    "ivan bilibin": 55, "jules cheret": 60, "theophile-alexandre steinlen": 65,
    "leonetto cappiello": 0, "koloman moser": 60, "georges barbier": 55,
    "ferdinand hodler": 55, "vilhelm hammershoi": 60, "joaquin sorolla": 60,
    "anders zorn": 55, "ilya repin": 50, "ivan aivazovsky": 65, "ivan shishkin": 55,
    "rembrandt van rijn": 85, "rembrandt harmensz van rijn": 85, "raffaello sanzio": 75,
    "michelangelo buonarroti": 80, "tiziano vecellio": 70, "giovanni antonio canal": 70,
    "hiroshige": 85, "hokusai": 95, "utamaro": 70, "kuniyoshi": 75, "vincent willem van gogh": 100,
    "albrecht durer": 80, "durer": 80, "francisco jose de goya y lucientes": 80,
    "goya": 80, "jmw turner": 85, "joseph mallord william turner": 85,
    "pierre joseph redoute": 75, "auguste rodin": 0,
}
# Artists whose FAMOUS entry should NOT force the famous_masters theme,
# because their buyers search by subject (bird, botanical ...).
NATURALISTS = {"maria sibylla merian", "pierre-joseph redoute", "pierre joseph redoute",
               "john james audubon", "ernst haeckel", "john gould", "edward lear",
               "mark catesby", "basilius besler", "robert jacob gordon", "george stubbs",
               "edwin landseer", "jan van huysum", "rachel ruysch", "jan davidsz de heem"}
JAPANESE_ARTISTS = re.compile(
    r"hokusai|hiroshige|utamaro|kuniyoshi|kunisada|toyokuni|harunobu|eisen|koson|shoson|"
    r"yoshitoshi|kiyonaga|sharaku|shunsho|hokkei|gakutei|kyosai|zeshin|jakuchu|"
    r"kiyochika|yoshitora|sadahide|shigenobu|shunei|koryusai|bairei|keinen|hiroshige ii|"
    r"hokuba|shinsai|toyohiro|kiyonobu|masanobu|chikanobu|gekko|yoshiiku|kunichika|"
    r"hirosada|sadanobu|yoshikazu|hokuju|shigemasa|eishi|choki|kitao|katsukawa|"
    r"utagawa|torii|suzuki|kitagawa|katsushika|keisai|kawanabe|ogata|tsukioka",
    re.I)

# Subject vocabulary -> (theme, display word). First theme listed in
# THEME_ORDER that matches wins; display word goes into the eBay title.
SUBJECTS = {
    "birds": [
        ("kingfisher", "Kingfisher"), ("owls?", "Owl"), ("peacocks?|peafowl|peahen", "Peacock"),
        ("robins?", "Robin"), ("wrens?", "Wren"), ("sparrows?", "Sparrow"),
        ("swallows?", "Swallow"), ("herons?|egrets?", "Heron"), ("cranes?", "Crane"),
        ("storks?", "Stork"), ("flamingos?|flamingoes", "Flamingo"), ("parrots?|macaws?|cockatoos?|parakeets?", "Parrot"),
        ("hummingbirds?|humming birds?", "Hummingbird"), ("pheasants?", "Pheasant"),
        ("eagles?", "Eagle"), ("hawks?|falcons?", "Hawk"), ("swans?", "Swan"),
        ("ducks?|mallards?|drakes?", "Duck"), ("geese|goose", "Goose"), ("pelicans?", "Pelican"),
        ("finch(?:es)?|goldfinch(?:es)?|bullfinch(?:es)?|chaffinch(?:es)?", "Finch"),
        ("blue ?tits?|titmouse|chickadees?", "Blue Tit"), ("magpies?", "Magpie"),
        ("crows?|ravens?|rooks?|jackdaws?", "Crow"), ("doves?|pigeons?", "Dove"),
        ("woodpeckers?", "Woodpecker"), ("puffins?", "Puffin"), ("penguins?", "Penguin"),
        ("toucans?", "Toucan"), ("blackbirds?|thrush(?:es)?", "Songbird"), ("jays?", "Jay"),
        ("orioles?|warblers?|tanagers?|cardinals? bird|bluebirds?|buntings?", "Songbird"),
        ("gulls?|seagulls?|terns?", "Gull"), ("hoopoes?", "Hoopoe"), ("birds?", "Bird"),
        ("ornithology|aves", "Bird"),
    ],
    "horses": [("horses?|mares?|stallions?|ponies|pony|foals?|colts?|equestrian|"
                "racehorses?|horseman|horsemen|hunter horse", "Horse")],
    "dogs": [("dogs?|hounds?|spaniels?|terriers?|puppy|puppies|greyhounds?|pugs?|poodles?|"
              "setters?|pointers? dog|retrievers?|dachshunds?|whippets?|collies?|"
              "beagles?|foxhounds?|mastiffs?|bulldogs?|lurchers?", "Dog")],
    "cats": [("cats?|kittens?|kitty", "Cat")],
    "farm_animals": [
        ("cows?|cattle|oxen|\box\b|bulls?|calf|calves|heifers?", "Cow"),
        ("sheep|lambs?|ewes?|rams?", "Sheep"), ("pigs?|hogs?|swine|sows?|piglets?", "Pig"),
        ("goats?", "Goat"), ("hens?|chickens?|roosters?|cockerels?|cocks?|poultry|chicks?", "Chicken"),
        ("donkeys?|asses?|mules?", "Donkey"), ("farmyard|barnyard", "Farm Animals"),
        ("highland cattle", "Highland Cow"),
    ],
    "wild_animals": [
        ("hares?", "Hare"), ("rabbits?|bunny|bunnies", "Rabbit"), ("foxes|fox\b", "Fox"),
        ("stags?|deer|does?\b|fawns?|reindeer|elk|moose|antelopes?|gazelles?", "Deer"),
        ("lions?|lioness", "Lion"), ("tigers?|tigress", "Tiger"), ("leopards?|panthers?|cheetahs?", "Leopard"),
        ("elephants?", "Elephant"), ("giraffes?", "Giraffe"), ("zebras?", "Zebra"),
        ("bears?", "Bear"), ("wolf|wolves", "Wolf"), ("monkeys?|apes?|chimpanzees?|gorillas?|baboons?|orangutans?", "Monkey"),
        ("squirrels?", "Squirrel"), ("hedgehogs?", "Hedgehog"), ("badgers?", "Badger"),
        ("otters?", "Otter"), ("mice|mouse|rats?\b", "Mouse"), ("bats?\b", "Bat"),
        ("camels?", "Camel"), ("rhinoceros|rhino", "Rhinoceros"), ("hippopotamus|hippo", "Hippo"),
        ("kangaroos?", "Kangaroo"), ("bison|buffalo(?:es)?", "Bison"), ("boars?", "Boar"),
        ("frogs?|toads?", "Frog"), ("snakes?|serpents?", "Snake"), ("lizards?|chameleons?", "Lizard"),
        ("tortoises?|turtles?", "Tortoise"), ("crocodiles?|alligators?", "Crocodile"),
        ("animals?|mammals?|wildlife|zoology|menagerie", "Animal"),
    ],
    "sea_life": [
        ("fish(?:es)?|carp|koi|trout|salmon|pike|goldfish|mackerel|herring|cod\b", "Fish"),
        ("shells?|seashells?|mollus[ck]s?|conch|nautilus", "Seashell"), ("crabs?", "Crab"),
        ("lobsters?", "Lobster"), ("octopus|octopuses|squid", "Octopus"),
        ("jellyfish|medusae|siphonophor", "Jellyfish"), ("corals?", "Coral"),
        ("whales?", "Whale"), ("dolphins?|porpoises?", "Dolphin"), ("sharks?", "Shark"),
        ("seahorses?|sea horses?", "Seahorse"), ("starfish", "Starfish"),
        ("seals?\b|walrus", "Seal"), ("marine life|sea creatures|ichthyology", "Sea Life"),
    ],
    "insects_butterflies": [
        ("butterfl(?:y|ies)|moths?|lepidoptera|caterpillars?", "Butterfly"),
        ("dragonfl(?:y|ies)", "Dragonfly"), ("beetles?|coleoptera", "Beetle"),
        ("bees?|bumblebees?|wasps?", "Bee"), ("insects?|entomolog|grasshoppers?|crickets?|"
                                              "cicadas?|ladybirds?|ladybugs?|spiders?", "Insect"),
    ],
    "botanical_flowers": [
        ("roses?", "Rose"), ("tulips?", "Tulip"), ("lil(?:y|ies)", "Lily"), ("irises|iris", "Iris"),
        ("peon(?:y|ies)", "Peony"), ("orchids?", "Orchid"), ("chrysanthemums?", "Chrysanthemum"),
        ("sunflowers?", "Sunflower"), ("poppies|poppy", "Poppy"), ("camellias?", "Camellia"),
        ("lotus", "Lotus"), ("daisies|daisy", "Daisy"), ("carnations?", "Carnation"),
        ("hyacinths?", "Hyacinth"), ("narcissus|daffodils?", "Daffodil"), ("magnolias?", "Magnolia"),
        ("hydrangeas?", "Hydrangea"), ("wisteria", "Wisteria"), ("cherry blossoms?|plum blossoms?|"
                                                                   "blossoms?", "Blossom"),
        ("anemones?", "Anemone"), ("violets?|pansies|pansy", "Violet"), ("geraniums?|pelargoniums?", "Geranium"),
        ("cactus|cacti|succulents?", "Cactus"), ("ferns?", "Fern"), ("mushrooms?|fungi|toadstools?", "Mushroom"),
        ("seaweeds?|algae", "Seaweed"), ("palms?\b", "Palm"), ("herbs?\b", "Herb"),
        ("botany|botanical|botanic|herbarium|plants?\b|flora\b|florilegium", "Botanical"),
        ("flowers?|floral|bouquets?|garlands?|wreaths?|blooms?", "Flower"),
        ("leaves|leaf\b|foliage|branch(?:es)?", "Botanical"),
    ],
    "fruit_food": [
        ("apples?", "Apple"), ("pears?", "Pear"), ("grapes?|vines?", "Grapes"), ("lemons?", "Lemon"),
        ("oranges?|citrus", "Orange"), ("cherr(?:y|ies)", "Cherry"), ("strawberr(?:y|ies)", "Strawberry"),
        ("peach(?:es)?", "Peach"), ("plums?", "Plum"), ("melons?", "Melon"), ("figs?", "Fig"),
        ("pomegranates?", "Pomegranate"), ("pineapples?", "Pineapple"), ("berr(?:y|ies)", "Berries"),
        ("vegetables?|cabbages?|asparagus|artichokes?|onions?|carrots?|pumpkins?|gourds?", "Vegetable"),
        ("fruits?|pomology", "Fruit"), ("bread|cheese|oysters?|wine|kitchen|butcher", "Kitchen"),
    ],
    "seascapes_ships": [
        ("ships?|shipping|vessels?|frigates?|men-of-war|man-of-war|steamers?|steamships?|"
         "schooners?|brigs?|galleons?|yachts?|fleet|naval|men of war", "Ship"),
        ("boats?|sailboats?|sailing|fishing boats?|barges?|rowing|canoes?", "Boat"),
        ("lighthouses?", "Lighthouse"), ("harbou?rs?|ports?\b|quays?|docks?|piers?", "Harbour"),
        ("seascapes?|seas?\b|ocean|waves?|coast(?:al|line)?|shores?|beach(?:es)?|marine|"
         "maritime|cliffs?|bays?\b|zeegezicht", "Seascape"),
        ("shipwrecks?|wrecks?", "Shipwreck"),
    ],
    "landscapes": [
        ("mountains?|mount\b|mt\.|alps|alpine|peaks?|fuji", "Mountain"), ("waterfalls?|cascades?", "Waterfall"),
        ("lakes?|loch", "Lake"), ("rivers?|streams?|brooks?|creek", "River"),
        ("forests?|woods?\b|woodland|trees?|oaks?|willows?|pines?|birch(?:es)?", "Trees"),
        ("snow|winter", "Winter"), ("sunsets?|sunrise|twilight|dusk|dawn|evening|night|moonlight|moon", "Moonlight"),
        ("gardens?|parks?\b", "Garden"), ("fields?|meadows?|pastures?|harvest|haystacks?|wheat|"
                                         "countryside|pastoral|farm\b|farms|village|cottages?|"
                                         "windmills?|mills?", "Countryside"),
        ("valley|glen|hills?|moors?\b|heath|dunes?|canyons?|desert|gorge", "Landscape"),
        ("landscapes?|scenery|vistas?|panorama|view of|views of|landschap|gezicht", "Landscape"),
    ],
    "city_architecture": [
        ("venice|venetian", "Venice"), ("london|thames", "London"), ("paris|seine", "Paris"),
        ("rome|roman forum|colosseum", "Rome"), ("amsterdam", "Amsterdam"),
        ("cathedrals?|churches|church|abbey|chapel|basilica|mosque|temple|pagoda|shrine", "Church"),
        ("bridges?", "Bridge"), ("castles?|palaces?|chateau|fort\b|fortress|towers?", "Castle"),
        ("streets?|squares?|market|canals?|city|cities|town|townscape|cityscape|urban|"
         "buildings?|architecture|architectural|ruins?|houses?|facade|interior", "Architecture"),
    ],
    "portraits": [("self-portrait|self portrait|portraits?|portret|likeness|head of a|bust of|"
                   "young woman|young man|girl|lady|woman|women|boy|child|children|mother|"
                   "family|couple|gentleman|madame|mademoiselle|\bmrs\b|\bmr\b", "Portrait")],
    "religious_art": [("madonna|virgin|mary\b|christ|jesus|holy family|annunciation|nativity|"
                       "crucifixion|resurrection|apostles?|biblical|bible|"
                       "(?:saint|st\.?|san|santa|sainte) (?:john|peter|paul|jerome|francis|george|"
                       "sebastian|catherine|anthony|mary|michael|luke|mark|matthew|andrew|james|"
                       "joseph|anne|barbara|christopher|dominic|nicholas|margaret|agnes|lucy|"
                       "cecilia|stephen|lawrence|bartholomew|thomas|philip|simon|jude|augustine|"
                       "ambrose|gregory|benedict|bernard|clare|elizabeth|veronica|roch|hubert|"
                       "eustace|ursula|apollonia|dorothy|giles|christina|helena|bruno)\b(?!-)|"
                       "angels?|evangelist|adoration|magi|last supper|pieta|lamentation|"
                       "entombment|ascension|assumption|baptism|prophet|moses|abraham|david and|"
                       "noah|buddha|bodhisattva|guanyin|kannon|arhat|deity|hindu|krishna|shiva|"
                       "vishnu|ganesh|religious|devotional|altarpiece|icon\b", "Religious")],
    "still_life": [("still[- ]life|still lifes|stilleven|nature morte|vanitas|breakfast piece|"
                    "tabletop", "Still Life")],
    "abstract_modern": [("abstract|abstraction|composition|cubis|constructivis|suprematis|"
                         "futuris|de stijl|bauhaus|geometric|improvisation|non-objective|"
                         "orphism|expressionis|fauvis|art deco|art nouveau|secession|jugendstil", "Abstract")],
}
# (the vocabulary strings are not raw strings: "\b" in them arrives as a
#  backspace character, so turn it back into a word boundary)
SUBJECT_RX = {t: [(re.compile(r"\b(?:" + p.replace("\x08", r"\b") + r")\b", re.I), w)
                  for p, w in lst]
              for t, lst in SUBJECTS.items()}
# Order in which subject themes are tested (after maps/posters/japanese/masters).
SUBJECT_ORDER = ["still_life", "religious_art", "birds", "horses", "dogs", "cats",
                 "farm_animals", "insects_butterflies", "sea_life", "wild_animals",
                 "botanical_flowers", "fruit_food", "seascapes_ships", "city_architecture",
                 "landscapes", "abstract_modern", "portraits"]

MAP_RX = re.compile(r"\bmaps?\b|cartograph|\batlas\b|\bkaart\b|\bplattegrond|\bchart of\b|"
                    r"\bplan of\b|\bnautical chart|\bglobe\b|bird'?s[- ]eye view|"
                    r"\bcelestial\b|\bplattegrond", re.I)
POSTER_RX = re.compile(r"\bposters?\b|\baffiche|\baanplakbiljet|\bplakat|\bwpa\b", re.I)
JAPAN_RX = re.compile(r"\bjapan|japanese|ukiyo|surimono|edo period|meiji|\bjapans\b", re.I)
WOODBLOCK_RX = re.compile(r"woodblock|woodcut|\bprint|surimono|ukiyo|houtsnede|nishiki", re.I)
PORTRAIT_TITLE = re.compile(r"^(?:portrait|portret|self-portrait|zelfportret|bust of|head of)\b",
                            re.I)
NAT_HIST_RX = re.compile(r"natural history|ornithology|botany|botanical|zoolog|entomolog|"
                         r"ichthyolog|herpetolog|conchology|pomology|flora\b|fauna\b|"
                         r"\bplate \d|\bpl\.\s?\d|\btab\.\s?\d|curtis|species", re.I)

THEME_SCORE = {"birds": 30, "horses": 25, "dogs": 25, "cats": 25, "farm_animals": 22,
               "wild_animals": 25, "sea_life": 18, "insects_butterflies": 22,
               "botanical_flowers": 30, "fruit_food": 18, "landscapes": 15,
               "seascapes_ships": 15, "japanese_woodblock": 25, "famous_masters": 10,
               "portraits": 0, "city_architecture": 10, "maps_vintage": 22,
               "posters_vintage": 28, "religious_art": 5, "abstract_modern": 18,
               "still_life": 12, "other": 0}
# Unthemed works and portraits of (mostly obscure) sitters need more to be
# worth listing: a painting, colour, a famous hand.
THEME_MIN_EXTRA = {"other": 10, "portraits": 5}

THEME_WORD = {"birds": "Bird", "horses": "Horse", "dogs": "Dog", "cats": "Cat",
              "farm_animals": "Farm Animal", "wild_animals": "Animal", "sea_life": "Sea Life",
              "insects_butterflies": "Insect", "botanical_flowers": "Botanical",
              "fruit_food": "Fruit", "landscapes": "Landscape", "seascapes_ships": "Seascape",
              "japanese_woodblock": "Japanese Woodblock", "famous_masters": "",
              "portraits": "Portrait", "city_architecture": "Architecture",
              "maps_vintage": "Antique Map", "posters_vintage": "Vintage Poster",
              "religious_art": "Religious", "abstract_modern": "Abstract",
              "still_life": "Still Life", "other": ""}

# Dutch (Rijksmuseum) title vocabulary: enough to translate the most common
# simple titles. Anything left untranslated -> build from English subject tags.
NL = [
    (r"^gezicht op (?:de |het )?", "View of "), (r"^gezicht in (?:de |het )?", "View in "),
    (r"^portret van (?:een )?", "Portrait of "), (r"^zelfportret", "Self-Portrait"),
    (r"^stilleven met ", "Still Life with "), (r"^stilleven", "Still Life"),
    (r"^landschap met ", "Landscape with "), (r"^landschap", "Landscape"),
    (r"^rivierlandschap met ", "River Landscape with "), (r"^rivierlandschap", "River Landscape"),
    (r"^winterlandschap met ", "Winter Landscape with "), (r"^winterlandschap", "Winter Landscape"),
    (r"^zeegezicht met ", "Seascape with "), (r"^zeegezicht", "Seascape"),
    (r"^duinlandschap", "Dune Landscape"), (r"^bloemstilleven", "Flower Still Life"),
    (r"^bloemen in een vaas", "Flowers in a Vase"), (r"^vaas met bloemen", "Vase of Flowers"),
    (r"^schepen (?:op|bij|in) ", "Ships at "), (r"^schip ", "Ship "), (r"^schepen", "Ships"),
    (r"^kaart van ", "Map of "), (r"^plattegrond van ", "Plan of "),
    (r"^kasteel ", "Castle "), (r"^kerk ", "Church "), (r"^de ", "The "), (r"^het ", "The "),
    (r"^een ", "A "),
]
NL_WORDS = {
    "vogel": "Bird", "vogels": "Birds", "paard": "Horse", "paarden": "Horses", "hond": "Dog",
    "honden": "Dogs", "kat": "Cat", "katten": "Cats", "koe": "Cow", "koeien": "Cows",
    "schaap": "Sheep", "schapen": "Sheep", "haas": "Hare", "vos": "Fox", "hert": "Deer",
    "leeuw": "Lion", "olifant": "Elephant", "uil": "Owl", "pauw": "Peacock", "vis": "Fish",
    "vissen": "Fish", "vlinder": "Butterfly", "vlinders": "Butterflies", "bloem": "Flower",
    "bloemen": "Flowers", "roos": "Rose", "rozen": "Roses", "tulp": "Tulip", "tulpen": "Tulips",
    "boom": "Tree", "bomen": "Trees", "molen": "Windmill", "windmolen": "Windmill",
    "rivier": "River", "zee": "Sea", "strand": "Beach", "schip": "Ship", "schepen": "Ships",
    "boot": "Boat", "boten": "Boats", "kerk": "Church", "brug": "Bridge", "kasteel": "Castle",
    "stad": "City", "dorp": "Village", "haven": "Harbour", "gracht": "Canal", "winter": "Winter",
    "met": "with", "en": "and", "op": "on", "in": "in", "bij": "near", "van": "of", "de": "the",
    "het": "the", "een": "a", "aan": "on", "te": "at", "twee": "Two", "drie": "Three",
    "landschap": "Landscape", "gezicht": "View", "stilleven": "Still Life", "vaas": "Vase",
    "fruit": "Fruit", "vruchten": "Fruit", "druiven": "Grapes", "appels": "Apples",
    "zwaan": "Swan", "zwanen": "Swans", "eend": "Duck", "eenden": "Ducks", "haan": "Cockerel",
    "kip": "Chicken", "kippen": "Chickens", "papegaai": "Parrot", "reiger": "Heron",
    "ijsvogel": "Kingfisher", "ooievaar": "Stork", "valk": "Falcon", "adelaar": "Eagle",
    "konijn": "Rabbit", "aap": "Monkey", "beer": "Bear", "wolf": "Wolf", "tijger": "Tiger",
    "kreeft": "Lobster", "krab": "Crab", "schelp": "Shell", "schelpen": "Shells",
    "insect": "Insect", "insecten": "Insects", "kever": "Beetle", "rups": "Caterpillar",
    "bos": "Forest", "berg": "Mountain", "bergen": "Mountains", "meer": "Lake",
    "waterval": "Waterfall", "maan": "Moon", "maanlicht": "Moonlight", "ijs": "Ice",
    "schaatsers": "Skaters", "boerderij": "Farm", "hooiberg": "Haystack", "tuin": "Garden",
    "bloeiende": "Flowering", "tak": "Branch", "takken": "Branches", "vogelnest": "Bird's Nest",
    "kaart": "Map", "plattegrond": "Plan", "zeeslag": "Sea Battle", "vuurtoren": "Lighthouse",
    "zeilschip": "Sailing Ship", "zeilschepen": "Sailing Ships", "vissersboten": "Fishing Boats",
    "vissersboot": "Fishing Boat", "duinen": "Dunes", "weide": "Meadow", "rund": "Cattle",
    "runderen": "Cattle", "vee": "Cattle", "stier": "Bull", "ezel": "Donkey", "geit": "Goat",
    "varken": "Pig", "varkens": "Pigs", "gezicht op": "View of", "noord": "North", "zuid": "South",
    "oude": "Old", "nieuwe": "New", "grote": "Great", "kleine": "Small", "zwarte": "Black",
    "witte": "White", "rode": "Red", "blauwe": "Blue", "gele": "Yellow", "groene": "Green",
    "tussen": "between", "onder": "under", "boven": "above", "voor": "before", "achter": "behind",
    "zittende": "Seated", "staande": "Standing", "liggende": "Lying", "vliegende": "Flying",
    "vogelvlucht": "Bird's-Eye View",
}

BRIT = [(r"\bcolor", "colour"), (r"\bColor", "Colour"), (r"\bgray\b", "grey"), (r"\bGray\b", "Grey"),
        (r"\bharbor", "harbour"), (r"\bHarbor", "Harbour"), (r"\bcenter\b", "centre"),
        (r"\bCenter\b", "Centre"), (r"\btheater", "theatre"), (r"\bTheater", "Theatre"),
        (r"\bfavorite", "favourite"), (r"\bFavorite", "Favourite"), (r"\bneighbor", "neighbour"),
        (r"\bNeighbor", "Neighbour"), (r"\bjewelry", "jewellery"), (r"\bJewelry", "Jewellery"),
        (r"\bplow", "plough"), (r"\bPlow", "Plough"), (r"\bvalor\b", "valour"),
        (r"\bhonor", "honour"), (r"\bHonor", "Honour"), (r"\barbor\b", "arbour"),
        (r"\bArbor\b", "Arbour"), (r"\bcatalog\b", "catalogue")]
SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "from", "in", "into", "of", "off",
         "on", "or", "the", "to", "with", "over", "under", "near", "after", "upon", "du", "de",
         "la", "le", "les", "des", "et", "van", "von", "der", "den", "di", "da", "del", "en", "aux"}
NOT_A_PERSON = re.compile(
    r"&|\bcompany\b|\bco\.|\binc\b|\bltd\b|publisher|manufactur|works\b|press\b|studio|"
    r"factory|firm\b|unknown|anonymous|anoniem|unidentified|after |attributed|workshop|"
    r"school|circle of|follower|manner of|style of|artist|maker|master of|\bmeester\b|"
    r"\bdesigned\b|\bprinted\b", re.I)
PARTICLE = {"van", "de", "der", "del", "di", "da", "le", "la", "von", "ter", "ten", "du", "des"}


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def norm(s):
    return re.sub(r"[^a-z0-9 ]+", " ", strip_accents(s or "").lower()).strip()


@functools.lru_cache(maxsize=None)
def famous_key(artist):
    a = norm(artist)
    if not a or NOT_A_PERSON.search(artist):
        return None, 0
    toks = set(a.split())
    for name, pts in FAMOUS.items():
        nt = norm(name).split()
        if not nt:
            continue
        if len(nt) == 1:
            if a == nt[0]:
                return name, pts
        elif set(nt) <= toks:
            return name, pts
    return None, 0


@functools.lru_cache(maxsize=None)
def surname(name):
    """'Vincent van Gogh' -> 'Van Gogh'. What a buyer types."""
    if not name or NOT_A_PERSON.search(name):
        return ""
    name = re.sub(r"\s*\(.*?\)", "", name).strip()
    name = NON_LATIN.sub("", name).strip(" ,;")
    if "," in name:  # "Hokusai, Katsushika" / "Wolgemut, Michael"
        parts = [p.strip() for p in name.split(",") if p.strip()]
        if len(parts) >= 2 and len(parts[0].split()) <= 3:
            name = parts[1] + " " + parts[0]
    if len(name) < 3:
        return ""
    low = norm(name)
    special = {"rembrandt": "Rembrandt", "hiroshige": "Hiroshige", "hokusai": "Hokusai",
               "utamaro": "Utamaro", "kuniyoshi": "Kuniyoshi", "canaletto": "Canaletto",
               "caravaggio": "Caravaggio", "titian": "Titian", "raphael": "Raphael",
               "michelangelo": "Michelangelo", "el greco": "El Greco", "leonardo": "Leonardo",
               "koson": "Koson", "shoson": "Shoson", "jakuchu": "Jakuchu",
               "yoshitoshi": "Yoshitoshi", "kunisada": "Kunisada", "toyokuni": "Toyokuni",
               "harunobu": "Harunobu", "eisen": "Eisen", "sharaku": "Sharaku",
               "kiyonaga": "Kiyonaga", "hokkei": "Hokkei", "kyosai": "Kyosai",
               "toulouse lautrec": "Toulouse-Lautrec", "burne jones": "Burne-Jones",
               "redoute": "Redoute", "durer": "Durer", "goya": "Goya",
               "velazquez": "Velazquez", "da vinci": "Leonardo da Vinci", "bruegel": "Bruegel",
               "brueghel": "Brueghel", "la tour": "La Tour", "van gogh": "Van Gogh"}
    for k, v in special.items():
        if k in low:
            return v
    parts = name.split()
    if len(parts) < 2:
        return name.title() if name.isupper() else name
    # drop suffixes like "the Elder", "II", "Jr."
    while len(parts) > 1 and parts[-1].lower().strip(".") in ("jr", "sr", "ii", "iii", "i", "elder",
                                                              "younger", "the"):
        parts = parts[:-1]
    for i, p in enumerate(parts[1:], 1):
        if p.lower() in PARTICLE:
            rest = [q.lower() if q.lower() in PARTICLE else q for q in parts[i + 1:]]
            return " ".join([p.capitalize()] + rest)
    s = parts[-1]
    return s.title() if s.isupper() else s


def titlecase(t):
    words = t.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        if i and lw in SMALL:
            out.append(lw)
        elif w.isupper() and len(w) > 1 and not re.match(r"^[IVXLC]+$", w):
            out.append(w.capitalize())
        elif w[:1].islower():
            out.append(w[:1].upper() + w[1:])
        else:
            out.append(w)
    return " ".join(out)


def brit(t):
    for a, b in BRIT:
        t = re.sub(a, b, t)
    return t


def clean_title(t, tc=True):
    t = t or ""
    t = t.replace("’", "'").replace("‘", "'").replace("“", "").replace("”", "")
    t = t.replace('"', "")
    m = re.search(r"(?:also )?(?:known|called) as\s+([^,;()]+)", t, re.I)
    if m:
        t = m.group(1)
    t = re.split(r",?\s+from (?:the |a )?(?:series|set|album|book|portfolio|publication|"
                 r"illustrated book|periodical|suite)\b", t, flags=re.I)[0]
    t = re.split(r",?\s+(?:no\.|number|plate|pl\.|folio|fol\.|page|p\.)\s*\d+", t, flags=re.I)[0]
    t = re.split(r"\s+/\s+|\s*;\s*|\s+—\s+|\s+-\s+(?=[A-Z])", t)[0]
    t = re.sub(r"\s*\([^)]*\)?", "", t)
    t = re.sub(r"\s*\[[^\]]*\]?", "", t)
    t = NON_LATIN.sub("", t)
    t = re.sub(r"(^|\s)'", r"\1", t)
    t = re.sub(r"(?<![sS])'(?=\s|$|,)", "", t)
    t = re.sub(r"\s+", " ", t).strip(" ,;:-.'")
    if len(t) > 3 and t.isupper():
        t = t.title()
    if not tc:
        return t
    return brit(titlecase(t)) if t else ""


def dutch_to_english(t):
    """Best-effort translation of simple Dutch titles; None if not confident."""
    low = t.strip()
    out = low
    matched = False
    for pat, rep in NL:
        new = re.sub(pat, rep, out, flags=re.I)
        if new != out:
            out = new
            matched = True
            break
    words = re.findall(r"[\w'’-]+|[,.]", out)
    if not words:
        return None
    if not matched and words[0].lower() not in NL_WORDS:
        return None  # sentence-initial capital hides whether it is Dutch
    res, unknown = [], 0
    for i, w in enumerate(words):
        lw = w.lower()
        if not matched and i == 0:
            res.append(NL_WORDS[lw])
        elif w in (",", "."):
            res.append(w)
        elif lw in NL_WORDS:
            res.append(NL_WORDS[lw])
        elif (w[:1].isupper() and not re.search(r"(?:sche|ij|ijk|heid|tje|je|ige|lijke)$", lw)) or w in ("View", "of", "with", "Portrait", "Landscape", "Still",
                                      "Life", "Seascape", "Ships", "Ship", "at", "Map", "Plan",
                                      "The", "A", "in", "River", "Winter", "Dune", "Castle",
                                      "Church", "Self-Portrait", "Flower", "Flowers", "Vase", "a"):
            res.append(w)  # proper noun or already English
        else:
            unknown += 1
    if unknown:
        return None
    s = " ".join(res).replace(" ,", ",").replace(" .", ".")
    return titlecase(s) if s else None


FOREIGN_SW = set("le la les des du et une un est pour avec sur dans au aux qui que pas mon ma "
                 "son sa ses ce cette il elle nous vous ils sont était el los las y con por una "
                 "der die das und mit im am ein eine zu auf ist nicht dem den gli della delle "
                 "degli nel nella sulla alla dei het een op bij voor naar niet".split())
ENGLISH_SW = set("the of and with a an in on at to from by for his her is are its their "
                 "near after under over into".split())


def is_foreign(title):
    toks = re.findall(r"[a-zà-ÿ]+", strip_accents(title.lower()).replace("'", " "))
    f = sum(t in FOREIGN_SW for t in toks)
    e = sum(t in ENGLISH_SW for t in toks)
    return f >= 2 and f > e


def clip(text, n):
    if len(text) <= n:
        return text
    cut = text[:n]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    cut = re.sub(r"\s+(?:and|of|the|with|in|on|at|a|an|for|to|by|from|&)$", "", cut, flags=re.I)
    return cut.strip(" ,;:-")


# --------------------------------------------------------------------------
def is_wall(r):
    cls = r.get("classification") or ""
    med = r.get("medium") or ""
    src = r["source"]
    if src == "met" and re.search(r"ephemera", cls, re.I) and not re.search(r"poster", cls, re.I):
        return False, "ephemera"
    if NOT_WALL.search(cls):
        return False, "object"
    if re.search(r"\b(?:porcelain|earthenware|stoneware|faience|silver|bronze|gold|ivory|"
                 r"textile|silk damask|velvet|enamel on copper|glass|marble|terracotta|"
                 r"carved|cast|wrought)\b", med, re.I) and not re.search(
                     r"paper|canvas|panel|silk\b|ink|watercolo|oil", med, re.I):
        return False, "object"
    if WALL.search(cls):
        return True, ""
    if src in ("rijks", "si") and re.search(r"paper|canvas|panel|ink|watercolo|oil|"
                                            r"engraving|etching|woodcut|lithograph", med, re.I):
        return True, ""
    return False, "object"


def copyright_ok(r):
    d = r.get("artist_death_year")
    if d:
        return d <= UK_CUTOFF_DEATH
    # No death year. Anonymous works: 70 years from making/publication.
    # Named artists without a death date: only if clearly old.
    latest = r.get("date_end") or r.get("date_begin")
    if not latest:
        ys = [int(y) for y in re.findall(r"(?<!\d)(1[0-9]{3}|20[0-2][0-9])(?!\d)",
                                          r.get("date") or "")]
        latest = max(ys) if ys else None
    b = r.get("artist_birth_year")
    if b and b > 1880:
        return False
    named = bool(r.get("artist")) and not NOT_A_PERSON.search(r.get("artist") or "")
    if latest is None:
        return not named and False  # no date at all: can't tell -> exclude
    return latest <= (1880 if named else 1900)


def classify(r, text, title_en):
    """-> (theme, display_word, specific_words)"""
    cls = (r.get("classification") or "") + " " + (r.get("medium") or "")
    art = r.get("artist") or ""
    fam, _ = famous_key(art)
    if MAP_RX.search(cls) or MAP_RX.search(title_en):
        return "maps_vintage", "Antique Map"
    if POSTER_RX.search(cls):
        return "posters_vintage", "Vintage Poster"
    japanese = (JAPAN_RX.search((r.get("culture") or "") + " " + (r.get("department") or "")
                                + " " + cls + " " + " ".join(r.get("tags") or []))
                or JAPANESE_ARTISTS.search(art)) and WOODBLOCK_RX.search(cls)
    if japanese and (JAPANESE_ARTISTS.search(art) or re.search(r"japan", r.get("culture") or "", re.I)
                     or re.search(r"ukiyo|surimono|woodblock", cls, re.I)):
        return "japanese_woodblock", None
    if fam and fam not in NATURALISTS and FAMOUS[fam] >= 50:
        return "famous_masters", None
    if PORTRAIT_TITLE.search(title_en):
        return "portraits", "Portrait"
    for src_text in (title_en, text):
        if not src_text:
            continue
        for theme in SUBJECT_ORDER:
            for rx, word in SUBJECT_RX[theme]:
                if rx.search(src_text):
                    return theme, word
    return "other", None


def score_of(r, theme, fam_pts, title_en):
    s = 0
    cls = ((r.get("classification") or "") + " " + (r.get("medium") or "")).lower()
    if re.search(r"paint|oil on|tempera|on canvas|on panel", cls):
        s += 25
    elif re.search(r"poster", cls):
        s += 20
    elif re.search(r"woodblock|woodcut|houtsnede|ukiyo", cls):
        s += 20
    elif re.search(r"watercolo|gouache|pastel", cls):
        s += 15
    elif re.search(r"lithograph|chromolitho|aquatint|mezzotint|engraving|etching|print", cls):
        s += 10
    elif re.search(r"drawing|chalk|pencil|charcoal|ink", cls):
        s += 8
    elif PHOTO.search(cls):
        s += 8
    if re.search(r"colou?r|hand-colou?red|chromolitho|watercolo|polychrome|kleur|ingekleurd|"
                 r"nishiki|woodblock print; ink and colou?r", cls):
        s += 8
    if NAT_HIST_RX.search(cls + " " + " ".join(r.get("tags") or [])):
        s += 5
    s += fam_pts
    s += THEME_SCORE.get(theme, 0)
    w, h = r.get("image_width"), r.get("image_height")
    if w and h:
        m = max(w, h)
        s += 10 if m >= 4961 else 6 if m >= 3500 else 2 if m >= 2500 else 0
    if r.get("artist") and not NOT_A_PERSON.search(r["artist"]):
        s += 3
    if len(title_en.split()) >= 2:
        s += 2
    return s


TAIL_TOKENS = ["Vintage", "Art Print", "Wall Art", "A4 A3 A2", "Gift"]
TAIL_PRIORITY = ["Art Print", "Wall Art", "Vintage", "A4 A3 A2", "Gift"]


def build_title(artist_sur, fam, work, keywords):
    """Artist Surname, Work Title Keywords Vintage Art Print Wall Art A4 A3 A2 Gift"""
    head = f"{artist_sur}, {work}" if (artist_sur and fam) else work
    low_head = head.lower()
    kws = []
    for k in keywords:
        if k and k.lower() not in low_head and not any(k.lower() in x.lower() for x in kws):
            kws.append(k)
    # Head gets at most 80 - len("Art Print Wall Art") - keywords
    kw_str = " ".join(kws)
    reserve = len(" Art Print Wall Art") + (len(kw_str) + 1 if kw_str else 0)
    head = clip(head, max(24, MAX_TITLE - reserve))
    parts = [head] + ([kw_str] if kw_str else [])
    base = " ".join(parts)
    if len(base) > MAX_TITLE - len(" Art Print"):
        base = clip(base, MAX_TITLE - len(" Art Print"))
    chosen = set()
    length = len(base)
    for t in TAIL_PRIORITY:
        if t.lower() in base.lower():
            continue
        if length + 1 + len(t) <= MAX_TITLE:
            chosen.add(t)
            length += 1 + len(t)
    title = " ".join([base] + [t for t in TAIL_TOKENS if t in chosen
                               and t.lower() not in base.lower()])
    title = re.sub(r"\s+", " ", title).strip()
    return title


def best_image_key(r):
    w, h = r.get("image_width") or 0, r.get("image_height") or 0
    return max(w, h)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--records", default=str(HERE / "raw" / "records"))
    ap.add_argument("--out", default=str(HERE))
    ap.add_argument("--min-score", type=int, default=20)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    FILTERS = ["read", "no_image", "licence", "not_wall", "photo_people", "copyright_uk",
               "bad_title", "sensitive", "too_small", "no_english_title", "low_demand",
               "compliance", "duplicate_work", "duplicate_title", "kept"]
    counts = collections.defaultdict(collections.Counter)  # source -> filter -> n
    cand = []
    files = sorted(Path(a.records).glob("*.jsonl.gz"))
    for f in files:
        print(f"  reading {f.name}", flush=True)
        for line in gzip.open(f, "rt", encoding="utf-8"):
            r = json.loads(line)
            src = r["source"]
            c = counts[src]
            c["read"] += 1
            if not r.get("image_url"):
                c["no_image"] += 1
                continue
            if r.get("licence") not in ("CC0", "PDM 1.0"):
                c["licence"] += 1
                continue
            ok, why = is_wall(r)
            if not ok:
                c["not_wall"] += 1
                continue
            cls_med = (r.get("classification") or "") + " " + (r.get("medium") or "")
            raw_title = r.get("title") or ""
            tags = r.get("tags") or []
            if PHOTO.search(cls_med) and not re.search(r"paint|drawing|watercolo|lithograph|"
                                                       r"engraving|etching|woodcut", r.get("classification") or "", re.I):
                if PEOPLE.search(raw_title + " " + " ".join(tags)) or not raw_title:
                    c["photo_people"] += 1
                    continue
            if not copyright_ok(r):
                c["copyright_uk"] += 1
                continue
            # English working title
            title_en = ""
            if r["source"] == "rijks" and r.get("extra_title_lang") == "nl":
                t = dutch_to_english(clean_title(raw_title, tc=False)) if raw_title else None
                t = brit(t) if t else None
                title_en = t or ""
            else:
                title_en = clean_title(raw_title)
                if title_en and is_foreign(title_en) and not famous_key(r.get("artist") or "")[0]:
                    c["no_english_title"] += 1
                    continue
            if BAD_TITLE.search(raw_title.strip()) or (title_en and BAD_TITLE.search(title_en)):
                c["bad_title"] += 1
                continue
            text_all = " ".join([raw_title, " ".join(tags), r.get("description", "")[:300]
                                 if src != "cma" else ""])
            if SENSITIVE.search(raw_title + " " + " ".join(tags)) or OFFENSIVE.search(text_all) \
                    or OFFENSIVE.search(title_en):
                c["sensitive"] += 1
                continue
            w, h = r.get("image_width"), r.get("image_height")
            if w and h and max(w, h) < MIN_LONG_SIDE:
                c["too_small"] += 1
                continue
            subj_text = " ".join([title_en or "", " ".join(tags),
                                  raw_title if r.get("extra_title_lang") != "nl" else ""])
            theme, word = classify(r, subj_text, title_en or "")
            fam, fam_pts = famous_key(r.get("artist") or "")
            if not title_en:
                # Dutch-only: build a descriptive title from English subject tags
                if theme in ("other", "portraits") or not word:
                    c["no_english_title"] += 1
                    continue
                kind = "Etching" if re.search(r"etch|ets", cls_med, re.I) else \
                    "Engraving" if re.search(r"engrav|grav", cls_med, re.I) else \
                    "Drawing" if re.search(r"drawing|tekening", cls_med, re.I) else \
                    "Painting" if re.search(r"paint|schilder", cls_med, re.I) else "Print"
                if theme not in ("birds", "horses", "dogs", "cats", "farm_animals",
                                 "wild_animals", "sea_life", "insects_butterflies",
                                 "botanical_flowers", "fruit_food", "landscapes",
                                 "seascapes_ships", "maps_vintage", "posters_vintage",
                                 "japanese_woodblock", "still_life") or word in ("Animal",):
                    c["no_english_title"] += 1
                    continue
                kind = "" if kind == "Print" else kind
                title_en = f"{word} Antique {kind}".strip()
                # a clean English subject tag that names the same thing ("Blue Peacock")
                for tg in tags:
                    if (word.lower() in tg.lower() and tg.lower() != word.lower()
                            and len(tg) < 25 and re.fullmatch(r"[A-Za-z ]+", tg)):
                        title_en = f"{titlecase(tg)} Antique {kind}".strip()
                        break
            if len(title_en) < 3:
                c["bad_title"] += 1
                continue
            if theme in ("other", "portraits") and NOT_WALL.search(title_en):
                c["not_wall"] += 1
                continue
            sc = score_of(r, theme, fam_pts, title_en)
            if sc < a.min_score + THEME_MIN_EXTRA.get(theme, 0):
                c["low_demand"] += 1
                continue
            r["_title_en"] = title_en
            r["_theme"] = theme
            r["_word"] = word
            r["_fam"] = fam
            r["_score"] = sc
            cand.append(r)
    print(f"  {len(cand):,} candidates after filters", flush=True)

    # ---- dedupe works: same artist surname + same normalised title ---------
    cand.sort(key=lambda r: (-r["_score"], -best_image_key(r)))
    seen_work, seen_title = set(), set()
    kept = []
    for r in cand:
        src = r["source"]
        sur = surname(r.get("artist") or "")
        wkey = (norm(sur), norm(r["_title_en"]))
        generic = len(norm(r["_title_en"]).split()) <= 1
        if not generic and wkey in seen_work:
            counts[src]["duplicate_work"] += 1
            continue
        theme = r["_theme"]
        kw = []
        if theme == "japanese_woodblock":
            kw = ["Japanese Woodblock"]
            if r["_word"]:
                kw.insert(0, r["_word"])
        elif theme == "famous_masters":
            # subject word if any, then nothing else - the name sells it
            t2, w2 = classify({**r, "artist": "", "classification": "", "medium": "",
                               "culture": "", "tags": []}, r["_title_en"], r["_title_en"])
            if w2 and t2 not in ("portraits",):
                kw = [w2]
        else:
            if r["_word"] and r["_word"] not in ("Animal", "Portrait"):
                kw.append(r["_word"])
            tw = THEME_WORD.get(theme)
            if tw and tw not in kw and theme in ("botanical_flowers", "landscapes",
                                                 "seascapes_ships", "maps_vintage",
                                                 "posters_vintage", "still_life",
                                                 "religious_art", "abstract_modern"):
                kw.append(tw)
            if not kw and theme in ("wild_animals", "birds"):
                kw.append(THEME_WORD[theme])
        fam = r["_fam"] if r["_fam"] and FAMOUS.get(r["_fam"], 0) >= 50 else None
        title = build_title(sur, fam, r["_title_en"], kw)
        # non-famous artists: add surname if the title collides
        if title.lower() in seen_title and sur:
            title = build_title(sur, True, r["_title_en"], kw)
        if title.lower() in seen_title:
            counts[src]["duplicate_title"] += 1
            continue
        if MUSEUM.search(title) or compliance.check(title) is not None:
            counts[src]["compliance"] += 1
            continue
        seen_work.add(wkey)
        seen_title.add(title.lower())
        counts[src]["kept"] += 1
        store = STORE_OF[theme]
        o = {k: v for k, v in r.items() if not k.startswith("_") and not k.startswith("extra_")}
        o.update(theme=theme, score=r["_score"], ebay_title=title, store=store,
                 work_title=r["_title_en"], famous_artist=bool(fam),
                 artwork_id=f"{src}:{r['source_id']}")
        if r.get("extra_print_jpg"):
            o["image_url_jpg"] = r["extra_print_jpg"]
        kept.append(o)

    # ---- write -------------------------------------------------------------
    kept.sort(key=lambda o: (-o["score"], o["artwork_id"]))
    with gzip.open(out / "artworks.jsonl.gz", "wt", encoding="utf-8") as fh:
        for o in kept:
            fh.write(json.dumps(o, ensure_ascii=False) + "\n")
    assert len({o["artwork_id"] for o in kept}) == len(kept)
    assert all(len(o["ebay_title"]) <= MAX_TITLE for o in kept)
    write_summary(out, kept, counts, FILTERS, a)
    print(f"  {len(kept):,} curated artworks -> {out / 'artworks.jsonl.gz'}", flush=True)


def write_summary(out, kept, counts, FILTERS, a):
    srcs = sorted(counts)
    L = []
    L.append("# Public-domain artwork catalogue: summary\n")
    L.append("Generated by `pd/curate.py` from the records written by `pd/harvest.py`. "
             "Every number below is counted from the files, nothing is estimated.\n")
    L.append(f"**Curated artworks: {len(kept):,}** (min score {a.min_score}).\n")
    L.append("## Filter funnel per source\n")
    L.append("Each record stops at the first filter it fails.\n")
    L.append("| filter | " + " | ".join(srcs) + " | total |")
    L.append("|---|" + "---:|" * (len(srcs) + 1))
    for f in FILTERS:
        vals = [counts[s].get(f, 0) for s in srcs]
        L.append(f"| {f} | " + " | ".join(f"{v:,}" for v in vals) + f" | {sum(vals):,} |")
    L.append("")
    # theme x source
    ts = collections.Counter((o["theme"], o["source"]) for o in kept)
    L.append("## Curated artworks: theme x source\n")
    L.append("| theme | store | " + " | ".join(srcs) + " | total |")
    L.append("|---|---|" + "---:|" * (len(srcs) + 1))
    for t in THEMES:
        vals = [ts.get((t, s), 0) for s in srcs]
        L.append(f"| {t} | {STORE_OF[t]} | " + " | ".join(f"{v:,}" for v in vals)
                 + f" | {sum(vals):,} |")
    tot = [sum(ts.get((t, s), 0) for t in THEMES) for s in srcs]
    L.append("| **total** | | " + " | ".join(f"**{v:,}**" for v in tot) + f" | **{sum(tot):,}** |")
    L.append("")
    # store x source
    ss = collections.Counter((o["store"], o["source"]) for o in kept)
    L.append("## Curated artworks: store x source\n")
    L.append("| store | " + " | ".join(srcs) + " | total |")
    L.append("|---|" + "---:|" * (len(srcs) + 1))
    for st in STORES:
        vals = [ss.get((st, s), 0) for s in srcs]
        L.append(f"| {st} | " + " | ".join(f"{v:,}" for v in vals) + f" | {sum(vals):,} |")
    L.append("")
    # resolution
    L.append("## Image size (long side, where the source states it)\n")
    L.append("| source | known | >= 4961 px (A2/A3@300) | 3500-4960 | 2000-3499 | unknown |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for s in srcs:
        rs = [o for o in kept if o["source"] == s]
        m = [max(o["image_width"], o["image_height"]) for o in rs
             if o.get("image_width") and o.get("image_height")]
        L.append(f"| {s} | {len(m):,} | {sum(x >= 4961 for x in m):,} | "
                 f"{sum(3500 <= x < 4961 for x in m):,} | {sum(2000 <= x < 3500 for x in m):,} | "
                 f"{len(rs) - len(m):,} |")
    L.append("")
    fam = collections.Counter(o["artist"] for o in kept if o["famous_artist"])
    L.append("## Famous artists (top 30 by curated works)\n")
    L.append(", ".join(f"{k} {v:,}" for k, v in fam.most_common(30)) + "\n")
    L.append("## Score distribution\n")
    sc = [o["score"] for o in kept]
    if sc:
        sc_sorted = sorted(sc)
        q = lambda p: sc_sorted[int(p * (len(sc_sorted) - 1))]
        L.append(f"min {sc_sorted[0]}, p25 {q(.25)}, median {q(.5)}, p75 {q(.75)}, "
                 f"p90 {q(.9)}, max {sc_sorted[-1]}\n")
    L.append("## Top 20 by score\n")
    for o in kept[:20]:
        L.append(f"- `{o['score']}` {o['ebay_title']}  _({o['source']}, {o['theme']})_")
    L.append("")
    L.append("## 30 random example titles\n")
    rnd = random.Random(a.seed)
    for o in rnd.sample(kept, min(30, len(kept))):
        L.append(f"- {o['ebay_title']}  _({o['source']}, {o['theme']}, {o['store']}, "
                 f"score {o['score']})_")
    L.append("")
    L.append("## Notes\n")
    L.append("- UK copyright: artist death year must be <= 1955. With no death year, a named "
             "artist's work must be dated <= 1880 (and artist born <= 1880); an anonymous "
             "work <= 1900. Records with no date at all are excluded.")
    L.append("- Met and Rijksmuseum metadata give no pixel sizes (image_width/height null); "
             "check the long side at download time and drop < 2000 px.")
    L.append("- NGA IIIF delivers at most 4096 px; recorded sizes are capped to that.")
    L.append("- AIC IIIF needs an explicit width (`/full/{w},/0/default.jpg`) and an "
             "`AIC-User-Agent` header.")
    L.append("- Cleveland `image_url` is the full TIFF; `image_url_jpg` is the 3400 px print JPG.")
    L.append("- Titles never contain museum names; every title passed `compliance.check`.")
    (out / "SUMMARY.md").write_text("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
