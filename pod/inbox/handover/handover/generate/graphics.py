"""
graphics.py — the graphic design engine.

WHY THIS SCALES WHERE TEXT DIDN'T
    "Just A Yorkshire Mum Who Loves Dogs" and "Just A Manchester Mum Who
    Loves Dogs" are one idea with a word swapped. But a wolf on a moonlit
    ridge, a wolf in a pine forest and a wolf in a snowstorm are three
    genuinely different pictures. Scene is real differentiation for art in a
    way that it never was for a sentence.

STRUCTURE
    SUBJECT x SCENE x STYLE x COMPOSITION

    Mixed-radix indexing (same as the Posterleaf generator): design N
    decomposes into exactly one combination, so collisions are impossible.

BUILT FOR A BLACK T-SHIRT, NOT A POSTER
    * bold and readable at arm's length, not detailed like wall art
    * stylised and graphic — photoreal prints muddy through a DTF underbase
    * light-toned artwork, since it prints in light ink on black
    * single strong subject with a clean silhouette
    * no scene fills the frame — the background is suggested, not painted,
      or it becomes a rectangle of ink on the shirt

IP SAFETY
    No characters, franchises, brands, clubs, or real people. Mythology,
    animals and folklore are free to use.
"""

# ================================================================= SUBJECTS
# (name, family, poses that suit it)
# family gates which styles and scenes pair with it.
SUBJECTS = [

    # --- dragons & mythic beasts: the strongest fantasy sellers ---------
    ("Welsh Dragon", "dragon"), ("Norse Serpent Dragon", "dragon"),
    ("Eastern Dragon", "dragon"), ("Horned Dragon", "dragon"),
    ("Winged Dragon", "dragon"), ("Frost Dragon", "dragon"),
    ("Ember Dragon", "dragon"), ("Sea Dragon", "dragon"),
    ("Baby Dragon", "dragon"), ("Skeletal Dragon", "dragon"),
    ("Two Headed Dragon", "dragon"), ("Coiled Dragon", "dragon"),
    ("Wyvern", "dragon"), ("Hydra", "dragon"), ("Basilisk", "dragon"),
    ("Phoenix", "mythic"), ("Griffin", "mythic"), ("Kraken", "mythic"),
    ("Minotaur", "mythic"), ("Centaur", "mythic"), ("Unicorn", "mythic"),
    ("Pegasus", "mythic"), ("Cerberus", "mythic"), ("Sphinx", "mythic"),
    ("Jackalope", "mythic"), ("Thunderbird", "mythic"),
    ("Kelpie", "mythic"), ("Selkie", "mythic"), ("Green Man", "mythic"),
    # ------------------------------------------------------------------
    # THE TEST EVERY SUBJECT MUST PASS
    #   1. would someone actually search for it?
    #   2. will it make a striking image on a black tee?
    # 81 were removed for failing one or the other — Gudgeon and Dace have no
    # audience, a Binman Truck and a Cement Mixer make dull artwork, a Sole
    # Fish is neither. Breadth is only worth anything if every listing is one
    # a buyer might want. Count is not the goal.
    #
    # SECOND BREADTH PASS — the niches people search by exact name
    # Coarse-grained subjects lose to specific ones. Someone does not search
    # "fish t shirt", they search "carp t shirt" or "tench t shirt". Each of
    # these is a small audience with almost no competition, and together they
    # are worth more than another hundred dragons.
    # ------------------------------------------------------------------

    # --- coarse fish for anglers: a large, loyal, underserved UK niche -----
    ("Common Carp", "sea"), ("Mirror Carp", "sea"), ("Leather Carp", "sea"),
    ("Ghost Carp", "sea"), ("Grass Carp", "sea"), ("Crucian Carp", "sea"),
    ("Tench", "sea"), ("Bream", "sea"), ("Roach", "sea"),
    ("Chub", "sea"), ("Barbel", "sea"),
    ("Zander", "sea"), ("Grayling", "sea"),
    ("Sea Bass", "sea"),
    ("Conger Eel", "sea"),
    ("Tope Shark", "sea"), ("Bluefin Tuna", "sea"),
    ("Tarpon", "sea"),
    ("Peacock Bass", "sea"), ("Arapaima", "sea"), ("Piranha", "sea"),
    ("Koi Butterfly", "sea"), ("Betta Fish", "sea"), ("Guppy", "sea"),
    ("Discus Fish", "sea"), ("Oscar Fish", "sea"), ("Axolotl Aquatic", "sea"),

    # --- butterflies and moths by species ---------------------------------
    ("Painted Lady Butterfly", "nature"), ("Small Tortoiseshell", "nature"),
    ("Comma Butterfly", "nature"), ("Brimstone Butterfly", "nature"),
    ("Orange Tip Butterfly", "nature"), ("Holly Blue", "nature"),
    ("Common Blue Butterfly", "nature"), ("Gatekeeper Butterfly", "nature"),
    ("Meadow Brown", "nature"), ("Speckled Wood", "nature"),
    ("Fritillary Butterfly", "nature"), ("Purple Emperor", "nature"),
    ("Blue Morpho", "nature"), ("Glasswing Butterfly", "nature"),
    ("Elephant Hawk Moth", "nature"), ("Hummingbird Hawk Moth", "nature"),
    ("Emperor Moth", "nature"), ("Tiger Moth", "nature"),
    ("Cinnabar Moth", "nature"), ("Poplar Hawk Moth", "nature"),

    # --- garden flowers and wildflowers by name ----------------------------
    ("Forget Me Not", "botanical"), ("Primrose", "botanical"),
    ("Buttercup", "botanical"),
    ("Daisy Chain", "botanical"),
    ("Red Campion", "botanical"),
    ("Harebell", "botanical"), ("Heather", "botanical"),
    ("Gorse", "botanical"),
    ("Hellebore", "botanical"), ("Anemone Flower", "botanical"),
    ("Ranunculus", "botanical"),
    ("Delphinium", "botanical"),
    ("Lupin", "botanical"), ("Hollyhock", "botanical"),
    ("Sweet Pea", "botanical"), ("Nasturtium", "botanical"),
    ("Marigold", "botanical"),
    ("Cosmos Flower", "botanical"),
    ("Echinacea", "botanical"), ("Rudbeckia", "botanical"),
    ("Bleeding Heart", "botanical"), ("Fuchsia", "botanical"),
    ("Passion Flower", "botanical"), ("Bird of Paradise Flower", "botanical"),
    ("Protea", "botanical"), ("Bougainvillea", "botanical"),
    ("Jasmine", "botanical"), ("Gardenia", "botanical"),

    # --- trades and professions: strong gift intent, low competition -------
    ("HGV Lorry", "machine"),
    ("Digger", "machine"), ("Crane", "machine"),
    ("Fire Engine", "machine"), ("Ambulance", "machine"),
    ("Police Car", "machine"), ("Lifeboat", "machine"),
    ("Chef Hat and Pan", "machine"),
    ("Combine Harvester", "machine"),
    ("Blacksmith Forge", "machine"),
    ("Welder Mask", "machine"),
    ("Photographer Lens", "machine"),
    ("DJ Decks", "machine"),

    # --- sports and pastimes ----------------------------------------------
    ("Dart Board", "machine"), ("Pool Cue", "machine"),
    ("Kayak", "machine"), ("Paddleboard", "machine"),
    ("Scuba Tank", "machine"),
    ("Parachute", "machine"), ("Hang Glider", "machine"),
    ("Horse Riding Saddle", "machine"),
    ("Falconry Glove", "machine"),
    ("Metal Detector", "machine"),
    ("Bushcraft Knife", "machine"),

    # --- games, tabletop, retro -------------------------------------------
    ("Twenty Sided Die", "y2k"), ("Dungeon Map", "y2k"),
    ("Wizard Staff", "y2k"), ("Potion Bottles", "y2k"),
    ("Arcade Cabinet", "y2k"), ("Games Console", "y2k"),
    ("Pixel Heart", "y2k"), ("Joystick", "y2k"),
    ("Rubik Cube", "y2k"), ("Boombox", "y2k"),
    ("Roller Skates", "y2k"), ("Lava Lamp", "y2k"),
    ("Disco Ball", "y2k"), ("Flip Phone", "y2k"),
    ("Floppy Disk", "y2k"), ("Polaroid Camera", "y2k"),

    # --- zodiac and symbols: evergreen gift searches -----------------------
    ("Aries Ram", "cosmic"), ("Taurus Bull", "cosmic"),
    ("Gemini Twins", "cosmic"), ("Cancer Crab", "cosmic"),
    ("Leo Lion", "cosmic"), ("Virgo Maiden", "cosmic"),
    ("Libra Scales", "cosmic"), ("Scorpio Scorpion", "cosmic"),
    ("Sagittarius Archer", "cosmic"), ("Capricorn Goat", "cosmic"),
    ("Aquarius Waves", "cosmic"), ("Pisces Fish", "cosmic"),
    ("Celtic Knot", "norse"), ("Triquetra", "norse"),
    ("Valknut", "norse"), ("Yggdrasil Tree", "norse"),
    ("Vegvisir", "norse"), ("Aegishjalmur", "norse"),
    ("Rune Stones", "norse"), ("Norse Longboat", "norse"),

    # --- more reptiles and amphibians -------------------------------------
    ("Bearded Dragon Pet", "reptile"), ("Blue Tongue Skink", "reptile"),
    ("Corn Snake", "reptile"), ("Milk Snake", "reptile"),
    ("Hognose Snake", "reptile"), ("Green Tree Python", "reptile"),
    ("Chameleon Veiled", "reptile"), ("Panther Chameleon", "reptile"),
    ("Tokay Gecko", "reptile"), ("Day Gecko", "reptile"),
    ("Horned Lizard", "reptile"), ("Frilled Lizard", "reptile"),
    ("Sulcata Tortoise", "reptile"), ("Hermann Tortoise", "reptile"),
    ("Red Eared Slider", "reptile"), ("Fire Salamander", "reptile"),
    ("Great Crested Newt", "reptile"), ("Natterjack Toad", "reptile"),

    # --- more small pets and cute -----------------------------------------
    ("Syrian Hamster", "cute"), ("Roborovski Hamster", "cute"),
    ("Netherland Dwarf Rabbit", "cute"), ("Rex Rabbit", "cute"),
    ("Flemish Giant Rabbit", "cute"), ("Angora Rabbit", "cute"),
    ("African Pygmy Hedgehog", "cute"), ("Quokka", "cute"),
    ("Fennec Kit", "cute"), ("Baby Otter", "cute"),
    ("Duckling", "cute"), ("Chick", "cute"), ("Piglet", "cute"),
    ("Lamb", "cute"), ("Foal", "cute"), ("Kitten", "cute"),
    ("Puppy", "cute"), ("Bear Cub", "cute"), ("Fox Cub", "cute"),

    # --- more gothic ------------------------------------------------------
    ("Raven Skull", "gothic"), ("Snake and Skull", "gothic"),
    ("Winged Skull", "gothic"),
    ("Reaper Scythe", "gothic"), ("Black Rose", "gothic"),
    ("Dead Tree", "gothic"), ("Crows on a Branch", "gothic"),
    ("Haunted House", "gothic"), ("Jack O Lantern", "gothic"),
    ("Witch Hat", "gothic"), ("Broomstick", "gothic"),
    ("Spell Book", "gothic"), ("Sigil Circle", "gothic"),
    ("Third Eye", "gothic"), ("Moth and Moon", "gothic"),

    # ------------------------------------------------------------------
    # BREADTH EXPANSION (Aug 2026)
    # 290 subjects averaging 486 listings each was the wrong shape: search
    # volume for "Welsh Dragon" is fixed, so 820 Welsh Dragon listings mostly
    # compete with each other. Every subject added here is a NEW search niche
    # that costs nothing extra to generate. Spread across 7 eBay accounts this
    # multiplies reach rather than dividing it.
    # ------------------------------------------------------------------

    # --- more dog breeds: 40 was a fraction of what people search ---------
    ("Cavapoo", "breed"), ("Cavachon", "breed"), ("Sprocker", "breed"),
    ("Sproodle", "breed"), ("Goldendoodle", "breed"), ("Maltipoo", "breed"),
    ("Bichon Frise", "breed"), ("Lhasa Apso", "breed"), ("Pekingese", "breed"),
    ("Papillon", "breed"), ("Pomeranian", "breed"), ("Japanese Spitz", "breed"),
    ("Samoyed", "breed"), ("Alaskan Malamute", "breed"), ("Chow Chow", "breed"),
    ("Saint Bernard", "breed"), ("Leonberger", "breed"), ("Mastiff", "breed"),
    ("Bullmastiff", "breed"), ("Cane Corso", "breed"), ("Boerboel", "breed"),
    ("American Bully", "breed"), ("Pitbull", "breed"),
    ("Bull Arab", "breed"), ("Dogue de Bordeaux", "breed"),
    ("English Bulldog", "breed"), ("Olde English Bulldogge", "breed"),
    ("Basenji", "breed"), ("Saluki", "breed"), ("Afghan Hound", "breed"),
    ("Irish Wolfhound", "breed"), ("Scottish Deerhound", "breed"),
    ("Lurcher", "breed"), ("Bloodhound", "breed"), ("Foxhound", "breed"),
    ("Harrier Dog", "breed"), ("Plott Hound", "breed"),
    ("Coonhound", "breed"), ("Rhodesian Ridgeback", "breed"),
    ("Pointer Dog", "breed"), ("German Shorthaired Pointer", "breed"),
    ("Brittany Spaniel", "breed"), ("Field Spaniel", "breed"),
    ("Clumber Spaniel", "breed"), ("Sussex Spaniel", "breed"),
    ("Welsh Springer Spaniel", "breed"), ("Flat Coated Retriever", "breed"),
    ("Chesapeake Bay Retriever", "breed"), ("Nova Scotia Duck Toller", "breed"),
    ("Curly Coated Retriever", "breed"), ("Australian Shepherd", "breed"),
    ("Australian Cattle Dog", "breed"), ("Blue Heeler", "breed"),
    ("Shetland Sheepdog", "breed"), ("Rough Collie", "breed"),
    ("Bearded Collie", "breed"), ("Briard", "breed"),
    ("Belgian Malinois", "breed"), ("Dutch Shepherd", "breed"),
    ("White Swiss Shepherd", "breed"), ("Anatolian Shepherd", "breed"),
    ("Pyrenean Mountain Dog", "breed"), ("Maremma Sheepdog", "breed"),
    ("Airedale Terrier", "breed"), ("Kerry Blue Terrier", "breed"),
    ("Wheaten Terrier", "breed"), ("Fox Terrier", "breed"),
    ("Lakeland Terrier", "breed"), ("Norfolk Terrier", "breed"),
    ("Norwich Terrier", "breed"), ("Cairn Terrier", "breed"),
    ("Scottish Terrier", "breed"), ("Skye Terrier", "breed"),
    ("Sealyham Terrier", "breed"), ("Dandie Dinmont Terrier", "breed"),
    ("Manchester Terrier", "breed"), ("Patterdale Terrier", "breed"),
    ("Jagdterrier", "breed"), ("Rat Terrier", "breed"),
    ("Miniature Schnauzer", "breed"), ("Giant Schnauzer", "breed"),
    ("Standard Poodle", "breed"), ("Miniature Poodle", "breed"),
    ("Toy Poodle", "breed"), ("Havanese", "breed"),
    ("Coton de Tulear", "breed"), ("Italian Greyhound", "breed"),
    ("Miniature Pinscher", "breed"), ("Affenpinscher", "breed"),
    ("Brussels Griffon", "breed"), ("Japanese Chin", "breed"),
    ("Pug Puppy", "breed"), ("Rescue Dog", "breed"), ("Three Legged Dog", "breed"),

    # --- more cat breeds --------------------------------------------------
    ("Russian Blue Cat", "breed"), ("Abyssinian Cat", "breed"),
    ("Burmese Cat", "breed"), ("Birman Cat", "breed"),
    ("Devon Rex Cat", "breed"), ("Cornish Rex Cat", "breed"),
    ("Scottish Fold Cat", "breed"), ("Munchkin Cat", "breed"),
    ("Turkish Van Cat", "breed"), ("Turkish Angora Cat", "breed"),
    ("Somali Cat", "breed"), ("Chartreux Cat", "breed"),
    ("Selkirk Rex Cat", "breed"), ("Manx Cat", "breed"),
    ("Savannah Cat", "breed"), ("Ocicat", "breed"),
    ("Calico Cat", "breed"), ("Tortie Cat", "breed"),
    ("Black Cat Portrait", "breed"), ("White Cat", "breed"),
    ("Grey Cat", "breed"), ("Rescue Cat", "breed"),

    # --- horses and farm --------------------------------------------------
    ("Arabian Horse", "breed"), ("Thoroughbred Horse", "breed"),
    ("Clydesdale Horse", "breed"), ("Friesian Horse", "breed"),
    ("Appaloosa Horse", "breed"), ("Palomino Horse", "breed"),
    ("Welsh Cob", "breed"), ("Dartmoor Pony", "breed"),
    ("Exmoor Pony", "breed"), ("New Forest Pony", "breed"),
    ("Connemara Pony", "breed"), ("Donkey", "breed"),
    ("Highland Bull", "breed"), ("Jersey Cow", "breed"),
    ("Belted Galloway", "breed"), ("Aberdeen Angus", "breed"),
    ("Suffolk Sheep", "breed"), ("Herdwick Sheep", "breed"),
    ("Jacob Sheep", "breed"), ("Goat", "breed"),
    ("Pygmy Goat", "breed"), ("Pig", "breed"), ("Kunekune Pig", "breed"),
    ("Llama", "breed"), ("Rooster", "breed"),

    # --- small pets -------------------------------------------------------
    ("Guinea Pig", "cute"), ("Hamster", "cute"),
    ("Chinchilla", "cute"), ("Rabbit", "cute"), ("Lop Rabbit", "cute"),
    ("Ferret", "cute"),
    ("Sugar Glider", "cute"), ("Axolotl", "cute"),

    # --- far more birds: birdwatching is a huge UK niche -------------------
    ("Blue Tit", "bird"), ("Great Tit", "bird"), ("Coal Tit", "bird"),
    ("Long Tailed Tit", "bird"), ("Goldfinch", "bird"), ("Chaffinch", "bird"),
    ("Bullfinch", "bird"), ("Greenfinch", "bird"), ("Siskin", "bird"),
    ("Wren", "bird"), ("Dunnock", "bird"), ("Blackbird", "bird"),
    ("Song Thrush", "bird"), ("Mistle Thrush", "bird"), ("Fieldfare", "bird"),
    ("Redwing", "bird"), ("Starling", "bird"), ("House Sparrow", "bird"),
    ("Nuthatch", "bird"), ("Treecreeper", "bird"), ("Goldcrest", "bird"),
    ("Woodpecker", "bird"), ("Green Woodpecker", "bird"), ("Jay", "bird"),
    ("Magpie", "bird"), ("Jackdaw", "bird"), ("Rook", "bird"),
    ("Kestrel", "bird"), ("Sparrowhawk", "bird"), ("Buzzard", "bird"),
    ("Red Kite", "bird"), ("Osprey", "bird"), ("Peregrine Falcon", "bird"),
    ("Merlin Bird", "bird"), ("Hen Harrier", "bird"), ("Tawny Owl", "bird"),
    ("Little Owl", "bird"), ("Short Eared Owl", "bird"),
    ("Kingfisher Diving", "bird"), ("Grey Heron", "bird"), ("Egret", "bird"),
    ("Curlew", "bird"), ("Oystercatcher", "bird"), ("Lapwing", "bird"),
    ("Avocet", "bird"), ("Gannet", "bird"), ("Cormorant", "bird"),
    ("Guillemot", "bird"), ("Razorbill", "bird"), ("Fulmar", "bird"),
    ("Arctic Tern", "bird"), ("Kittiwake", "bird"), ("Seagull", "bird"),
    ("Mute Swan", "bird"), ("Canada Goose", "bird"), ("Mallard", "bird"),
    ("Teal Duck", "bird"), ("Widgeon", "bird"), ("Grebe", "bird"),
    ("Moorhen", "bird"), ("Coot", "bird"), ("Pheasant", "bird"),
    ("Grouse", "bird"), ("Partridge", "bird"), ("Woodpigeon", "bird"),
    ("Collared Dove", "bird"), ("Swallow", "bird"), ("Swift Bird", "bird"),
    ("House Martin", "bird"), ("Cuckoo", "bird"), ("Nightingale", "bird"),
    ("Skylark", "bird"), ("Yellowhammer", "bird"), ("Linnet", "bird"),
    ("Toucan", "bird"), ("Macaw", "bird"), ("Cockatoo", "bird"),
    ("Parrot", "bird"), ("Budgerigar", "bird"), ("Flamingo", "bird"),
    ("Pelican", "bird"), ("Stork", "bird"), ("Crane Bird", "bird"),
    ("Ostrich", "bird"), ("Emu", "bird"), ("Cassowary", "bird"),
    ("Penguin", "bird"), ("King Penguin", "bird"), ("Kiwi Bird", "bird"),
    ("Hoopoe", "bird"), ("Bee Eater", "bird"), ("Roller Bird", "bird"),

    # --- more wildlife ----------------------------------------------------
    ("Cheetah", "wild"), ("Leopard", "wild"), ("Jaguar", "wild"),
    ("Cougar", "wild"), ("Caracal", "wild"), ("Serval", "wild"),
    ("Ocelot", "wild"), ("Clouded Leopard", "wild"), ("Black Panther", "wild"),
    ("White Tiger", "wild"), ("Bengal Tiger", "wild"), ("Siberian Tiger", "wild"),
    ("Black Bear", "wild"), ("Kodiak Bear", "wild"), ("Sun Bear", "wild"),
    ("Sloth Bear", "wild"), ("Panda", "wild"), ("Red Panda", "wild"),
    ("Coyote", "wild"), ("Jackal", "wild"), ("Dingo", "wild"),
    ("Fennec Fox", "wild"), ("Arctic Fox", "wild"), ("Grey Wolf", "wild"),
    ("Timber Wolf", "wild"), ("Dire Wolf", "wild"), ("Hyena", "wild"),
    ("Wolverine Animal", "wild"), ("Honey Badger", "wild"),
    ("Elephant", "wild"), ("African Elephant", "wild"), ("Rhino", "wild"),
    ("Hippo", "wild"), ("Giraffe", "wild"), ("Zebra", "wild"),
    ("Gazelle", "wild"), ("Antelope", "wild"), ("Wildebeest", "wild"),
    ("Water Buffalo", "wild"), ("Yak", "wild"), ("Musk Ox", "wild"),
    ("Moose", "wild"), ("Reindeer", "wild"), ("Caribou", "wild"),
    ("Roe Deer", "wild"), ("Fallow Deer", "wild"), ("Muntjac", "wild"),
    ("Ibex", "wild"), ("Chamois", "wild"), ("Mountain Goat", "wild"),
    ("Bighorn Sheep", "wild"), ("Wild Boar", "wild"), ("Warthog", "wild"),
    ("Gorilla", "wild"), ("Silverback Gorilla", "wild"), ("Chimpanzee", "wild"),
    ("Orangutan", "wild"), ("Baboon", "wild"), ("Mandrill", "wild"),
    ("Lemur", "wild"), ("Sloth", "wild"), ("Anteater", "wild"),
    ("Armadillo", "wild"), ("Pangolin", "wild"), ("Aardvark", "wild"),
    ("Meerkat", "wild"), ("Mongoose", "wild"), ("Raccoon", "wild"),
    ("Skunk", "wild"), ("Possum", "wild"), ("Koala", "wild"),
    ("Kangaroo", "wild"), ("Wallaby", "wild"), ("Wombat", "wild"),
    ("Tasmanian Devil", "wild"), ("Platypus", "wild"), ("Echidna", "wild"),
    ("Beaver", "wild"), ("Stoat", "wild"), ("Weasel", "wild"),
    ("Polecat", "wild"),
    ("Bat", "wild"),
    ("Fruit Bat", "wild"), ("Capybara", "wild"), ("Tapir", "wild"),
    ("Okapi", "wild"), ("Bongo Antelope", "wild"), ("Snow Monkey", "wild"),

    # --- sea life ---------------------------------------------------------
    ("Blue Whale", "sea"), ("Sperm Whale", "sea"), ("Narwhal", "sea"),
    ("Beluga Whale", "sea"), ("Dolphin", "sea"), ("Porpoise", "sea"),
    ("Hammerhead Shark", "sea"), ("Tiger Shark", "sea"), ("Whale Shark", "sea"),
    ("Basking Shark", "sea"), ("Nurse Shark", "sea"), ("Mako Shark", "sea"),
    ("Stingray", "sea"), ("Eagle Ray", "sea"), ("Cuttlefish", "sea"),
    ("Squid", "sea"), ("Giant Squid", "sea"), ("Nautilus", "sea"),
    ("Starfish", "sea"), ("Sea Urchin", "sea"), ("Hermit Crab", "sea"),
    ("Lobster", "sea"), ("Crab", "sea"),
    ("Clownfish", "sea"), ("Angelfish", "sea"), ("Lionfish", "sea"),
    ("Pufferfish", "sea"), ("Moray Eel", "sea"), ("Barracuda", "sea"),
    ("Marlin", "sea"), ("Swordfish", "sea"), ("Sailfish", "sea"),
    ("Tuna", "sea"), ("Trout", "sea"),
    ("Brown Trout", "sea"), ("Rainbow Trout", "sea"), ("Carp", "sea"),
    ("Perch", "sea"), ("Bass Fish", "sea"), ("Catfish", "sea"),
    ("Sturgeon", "sea"), ("Anglerfish", "sea"), ("Seal", "sea"),
    ("Grey Seal", "sea"), ("Sea Lion", "sea"), ("Walrus", "sea"),
    ("Sea Otter", "sea"), ("Coral Reef", "sea"), ("Anemone", "sea"),

    # --- reptiles and amphibians -----------------------------------------
    ("Komodo Dragon", "reptile"), ("Monitor Lizard", "reptile"),
    ("Tortoise", "reptile"), ("Terrapin", "reptile"),
    ("Python", "reptile"), ("Boa Constrictor", "reptile"),
    ("Anaconda", "reptile"), ("Adder", "reptile"), ("Grass Snake", "reptile"),
    ("Coral Snake", "reptile"), ("Black Mamba", "reptile"),
    ("King Cobra", "reptile"), ("Alligator", "reptile"), ("Caiman", "reptile"),
    ("Frog", "reptile"), ("Tree Frog", "reptile"), ("Poison Dart Frog", "reptile"),
    ("Toad", "reptile"), ("Newt", "reptile"), ("Salamander", "reptile"),
    ("Leopard Gecko", "reptile"), ("Crested Gecko", "reptile"),
    ("Slow Worm", "reptile"), ("Skink", "reptile"), ("Basilisk Lizard", "reptile"),

    # --- insects and minibeasts ------------------------------------------
    ("Bumblebee", "nature"), ("Honey Bee", "nature"),
    ("Ladybird", "nature"),
    ("Stag Beetle", "nature"), ("Scarab Beetle", "nature"),
    ("Rhinoceros Beetle", "nature"), ("Firefly", "nature"),
    ("Grasshopper", "nature"),
    ("Praying Mantis", "nature"),
    ("Cicada", "nature"), ("Damselfly", "nature"),
    ("Monarch Butterfly", "nature"), ("Peacock Butterfly", "nature"),
    ("Red Admiral", "nature"), ("Swallowtail Butterfly", "nature"),
    ("Luna Moth", "nature"), ("Death Head Moth", "nature"),
    ("Atlas Moth", "nature"),
    ("Tarantula", "nature"), ("Jumping Spider", "nature"),
    ("Scorpion", "nature"),

    # --- flowers, trees, plants ------------------------------------------
    ("Rose", "botanical"), ("Peony", "botanical"), ("Tulip", "botanical"),
    ("Daffodil", "botanical"), ("Bluebell", "botanical"),
    ("Snowdrop", "botanical"), ("Crocus", "botanical"), ("Iris", "botanical"),
    ("Lily", "botanical"), ("Orchid", "botanical"), ("Lotus", "botanical"),
    ("Poppy", "botanical"), ("Cornflower", "botanical"),
    ("Foxglove", "botanical"), ("Lavender", "botanical"),
    ("Hydrangea", "botanical"), ("Dahlia", "botanical"),
    ("Chrysanthemum", "botanical"), ("Camellia", "botanical"),
    ("Magnolia", "botanical"), ("Cherry Blossom", "botanical"),
    ("Wisteria", "botanical"), ("Honeysuckle", "botanical"),
    ("Clematis", "botanical"), ("Ivy", "botanical"),
    ("Holly and Berries", "botanical"), ("Mistletoe", "botanical"),
    ("Willow Tree", "botanical"), ("Birch Tree", "botanical"),
    ("Ash Tree", "botanical"), ("Beech Tree", "botanical"),
    ("Yew Tree", "botanical"), ("Rowan Tree", "botanical"),
    ("Horse Chestnut", "botanical"), ("Sycamore", "botanical"),
    ("Redwood", "botanical"), ("Bonsai Tree", "botanical"),
    ("Palm Tree", "botanical"), ("Baobab Tree", "botanical"),
    ("Olive Branch", "botanical"), ("Cactus", "botanical"),
    ("Succulent", "botanical"), ("Monstera Leaf", "botanical"),
    ("Acorn and Oak Leaf", "botanical"), ("Pine Cone", "botanical"),
    ("Dandelion Clock", "botanical"),
    ("Chanterelle", "botanical"),
    ("Porcini Mushroom", "botanical"), ("Toadstool Ring", "botanical"),

    # --- hobbies and objects: whole niches with no animal at all ----------
    ("Fishing Rod and Reel", "machine"), ("Fly Fishing Lure", "machine"),
    ("Tackle Box", "machine"), ("Compass and Map", "machine"),
    ("Hiking Boots", "machine"), ("Ice Axe", "machine"),
    ("Climbing Carabiner", "machine"), ("Camping Lantern", "machine"),
    ("Camp Fire", "machine"), ("Canoe Paddle", "machine"),
    ("Surfboard", "machine"), ("Skateboard", "machine"),
    ("Snowboard", "machine"), ("Skis", "machine"),
    ("Mountain Bike", "machine"), ("Road Bicycle", "machine"),
    ("Penny Farthing", "machine"), ("Motorcycle", "machine"),
    ("Cafe Racer Motorcycle", "machine"), ("Scrambler Motorcycle", "machine"),
    ("Classic Car", "machine"), ("Muscle Car", "machine"),
    ("Rally Car", "machine"), ("Camper Van", "machine"),
    ("Land Rover", "machine"), ("Tractor", "machine"),
    ("Steam Train", "machine"),
    ("Sailing Boat", "machine"), ("Tall Ship", "machine"),
    ("Lighthouse", "machine"), ("Anchor and Rope", "machine"),
    ("Ship Wheel", "machine"), ("Diving Helmet", "machine"),
    ("Hot Air Balloon", "machine"), ("Biplane", "machine"),
    ("Spitfire", "machine"), ("Glider", "machine"),
    ("Windmill", "machine"), ("Water Mill", "machine"),
    ("Acoustic Guitar", "machine"), ("Electric Guitar", "machine"),
    ("Bass Guitar", "machine"), ("Violin", "machine"), ("Cello", "machine"),
    ("Piano Keys", "machine"), ("Saxophone", "machine"),
    ("Trumpet", "machine"), ("Drum Kit", "machine"),
    ("Vinyl Record", "machine"), ("Cassette Tape", "machine"),
    ("Headphones", "machine"), ("Microphone", "machine"),
    ("Film Camera", "machine"),
    ("Telescope", "machine"), ("Microscope", "machine"),
    ("Darts", "machine"),
    ("Snooker Balls", "machine"), ("Boxing Gloves", "machine"),
    ("Kettlebell", "machine"), ("Barbell", "machine"),
    ("Running Shoes", "machine"), ("Football Boots", "machine"),
    ("Cricket Bat and Ball", "machine"), ("Rugby Ball", "machine"),
    ("Golf Clubs", "machine"), ("Tennis Racket", "machine"),
    ("Archery Bow", "machine"),
    ("Beehive", "machine"),
    ("Coffee Grinder", "machine"), ("Espresso Cup", "machine"),
    ("Teapot", "machine"), ("Whisky Glass", "machine"),
    ("Pint Glass", "machine"), ("Wine Bottle", "machine"),
    ("Cocktail Shaker", "machine"), ("Vintage Radio", "machine"),
    ("Tattoo Machine", "machine"),
    ("Stethoscope", "machine"),
    ("Welding Torch", "machine"),
    ("Chainsaw", "machine"), ("Axe and Log", "machine"),
    ("Anvil and Hammer", "machine"), ("Horseshoe", "machine"),

    # --- mythology by culture --------------------------------------------
    ("Phoenix Rising", "mythic"), ("Chimera", "mythic"), ("Manticore", "mythic"),
    ("Harpy", "mythic"),
    ("Cyclops", "mythic"), ("Medusa Head", "mythic"), ("Gorgon", "mythic"),
    ("Satyr", "mythic"), ("Faun", "mythic"), ("Nymph", "mythic"),
    ("Banshee", "mythic"), ("Leprechaun", "mythic"), ("Pooka", "mythic"),
    ("Cu Sith", "mythic"), ("Loch Ness Monster", "mythic"),
    ("Questing Beast", "mythic"), ("Wyrm", "mythic"), ("Cockatrice", "mythic"),
    ("Wendigo", "mythic"), ("Sasquatch", "mythic"),
    ("Yeti", "mythic"), ("Qilin", "mythic"), ("Fenghuang", "mythic"),
    ("Kitsune", "mythic"), ("Tengu", "mythic"), ("Oni Mask", "mythic"),
    ("Leviathan", "mythic"), ("Anubis", "mythic"),
    ("Bastet", "mythic"), ("Horus", "mythic"), ("Ra Sun Disc", "mythic"),
    ("Scarab Amulet", "mythic"), ("Ankh", "mythic"),
    ("Garuda", "mythic"), ("Naga", "mythic"), ("Roc Bird", "mythic"),
    ("Djinn", "mythic"), ("Golem", "mythic"), ("Minotaur Maze", "mythic"),
    ("Pegasus Wings", "mythic"), ("Kelpie Horse", "mythic"),

    # --- cosmic and science ----------------------------------------------
    ("Saturn", "cosmic"), ("Jupiter", "cosmic"), ("Mars", "cosmic"),
    ("Solar System", "cosmic"), ("Milky Way", "cosmic"),
    ("Black Hole", "cosmic"), ("Supernova", "cosmic"), ("Comet", "cosmic"),
    ("Meteor Shower", "cosmic"), ("Eclipse", "cosmic"),
    ("Aurora Borealis", "cosmic"), ("Constellation Chart", "cosmic"),
    ("Rocket Launch", "cosmic"), ("Space Shuttle", "cosmic"),
    ("Satellite", "cosmic"), ("Mars Rover", "cosmic"),
    ("Moon Phases", "cosmic"), ("Crescent Moon", "cosmic"),
    ("Atom Diagram", "cosmic"), ("DNA Helix", "cosmic"),
    ("Circuit Board", "cosmic"), ("Sound Wave", "cosmic"),

    # --- gothic and occult ------------------------------------------------
    ("Ram Skull", "gothic"), ("Bull Skull", "gothic"), ("Bird Skull", "gothic"),
    ("Skeleton Hand", "gothic"), ("Rib Cage", "gothic"), ("Spine", "gothic"),
    ("Ouija Board", "gothic"), ("Tarot Card", "gothic"),
    ("Crystal Ball", "gothic"), ("Cauldron", "gothic"),
    ("Poison Bottle", "gothic"), ("Apothecary Jar", "gothic"),
    ("Black Candle", "gothic"), ("Grave Stone", "gothic"),
    ("Coffin and Roses", "gothic"), ("Church Ruin", "gothic"),
    ("Gargoyle", "gothic"), ("Bat Swarm", "gothic"),
    ("Vampire Fangs", "gothic"), ("Moth and Skull", "gothic"),
    ("Hourglass", "gothic"), ("Pendulum", "gothic"),

    # --- cottagecore and folk --------------------------------------------
    ("Cottage in Woods", "cottage"), ("Garden Shed", "cottage"),
    ("Greenhouse", "cottage"), ("Picnic Basket", "cottage"),
    ("Jam Jars", "cottage"), ("Bread Loaf", "cottage"),
    ("Wheelbarrow", "cottage"),
    ("Hay Bales", "cottage"), ("Scarecrow", "cottage"),

    # --- dark academia ----------------------------------------------------
    ("Stack of Books", "academia"), ("Open Grimoire", "academia"),
    ("Quill and Inkwell", "academia"),
    ("Candle and Books", "academia"), ("Globe and Maps", "academia"),
    ("Botanical Plate", "academia"),
    ("Astrolabe", "academia"), ("Orrery", "academia"),

    # Figures where the face is covered, turned away or absent — asked for
    # after seeing AI faces come out uncanny in the first samples.
    ("Mermaid", "human"), ("Siren", "human"), ("Sea Witch", "human"),
    ("Plague Doctor", "human"), ("Witch", "human"), ("Druid", "human"),
    ("Monk", "human"), ("Pirate Captain", "human"), ("Highwayman", "human"),
    ("Falconer", "human"), ("Beekeeper", "human"), ("Lighthouse Keeper", "human"),
    ("Storm Chaser", "human"), ("Deep Sea Diver", "human"),
    ("Fenrir Wolf", "norse"), ("Jormungandr Serpent", "norse"),
    ("Valkyrie", "human"), ("Berserker", "human"),
    ("Odin's Ravens", "norse"), ("Viking Longship", "norse"),
    ("Norse Warrior", "human"), ("Shield Maiden", "human"),
    ("Mjolnir Hammer", "norse"),
    ("Valknut Symbol", "norse"), ("Runestone", "norse"),

    # --- wild animals: broadest appeal, works in every style -----------
    ("Wolf", "wild"), ("Lone Wolf", "wild"), ("Howling Wolf", "wild"),
    ("Arctic Wolf", "wild"), ("Wolf Pack", "wild"),
    ("Lion", "wild"), ("Lioness", "wild"), ("Tiger", "wild"),
    ("Snow Leopard", "wild"), ("Panther", "wild"), ("Lynx", "wild"),
    ("Bear", "wild"), ("Grizzly Bear", "wild"), ("Polar Bear", "wild"),
    ("Stag", "wild"), ("Elk", "wild"), ("Bison", "wild"), ("Ram", "wild"),
    ("Highland Cow", "wild"), ("Fox", "wild"), ("Red Fox", "wild"),
    ("Badger", "wild"), ("Otter", "wild"), ("Hare", "wild"),
    ("Hedgehog", "wild"), ("Red Squirrel", "wild"), ("Pine Marten", "wild"),
    ("Eagle", "bird"), ("Golden Eagle", "bird"), ("Owl", "bird"),
    ("Barn Owl", "bird"), ("Snowy Owl", "bird"), ("Raven", "bird"),
    ("Crow", "bird"), ("Falcon", "bird"), ("Kingfisher", "bird"),
    ("Heron", "bird"), ("Puffin", "bird"), ("Robin", "bird"),
    ("Swan", "bird"), ("Peacock", "bird"), ("Hummingbird", "bird"),
    ("Orca", "sea"), ("Humpback Whale", "sea"), ("Shark", "sea"),
    ("Great White Shark", "sea"), ("Octopus", "sea"), ("Jellyfish", "sea"),
    ("Sea Turtle", "sea"), ("Seahorse", "sea"), ("Manta Ray", "sea"),
    ("Koi Carp", "sea"), ("Salmon", "sea"), ("Pike", "sea"),
    ("Cobra", "reptile"), ("Rattlesnake", "reptile"), ("Viper", "reptile"),
    ("Chameleon", "reptile"), ("Gecko", "reptile"), ("Iguana", "reptile"),
    ("Crocodile", "reptile"), ("Bearded Dragon", "reptile"),
    ("Bee", "nature"), ("Butterfly", "nature"), ("Moth", "nature"),
    ("Dragonfly", "nature"), ("Beetle", "nature"), ("Spider", "nature"),

    # --- dinosaurs ------------------------------------------------------
    ("Tyrannosaurus Rex", "dino"), ("Triceratops", "dino"),
    ("Velociraptor", "dino"), ("Stegosaurus", "dino"),
    ("Brachiosaurus", "dino"), ("Spinosaurus", "dino"),
    ("Pterodactyl", "dino"), ("Ankylosaurus", "dino"),

    # --- skull, gothic, occult -----------------------------------------
    ("Skull", "gothic"), ("Horned Skull", "gothic"),
    ("Wolf Skull", "gothic"),
    ("Sugar Skull", "gothic"),
    ("Skull And Roses", "gothic"),
    ("Skull With Crown", "gothic"), ("Skull And Serpent", "gothic"),
    ("Grim Reaper", "human"), ("Hooded Figure", "human"),
    ("Anatomical Heart", "gothic"),
    ("Black Cat", "gothic"),
    ("Coffin", "gothic"),

    # --- warriors & folklore --------------------------------------------
    ("Samurai", "human"), ("Ronin", "human"), ("Ninja", "human"),
    ("Spartan Warrior", "human"), ("Knight", "human"),
    ("Knight Templar", "human"), ("Highland Warrior", "human"),
    ("Celtic Warrior", "human"), ("Gladiator", "human"),
    ("Archer", "human"), ("Swordsman", "human"),

    # --- cosmic ----------------------------------------------------------
    ("Astronaut", "human"), ("Space Cat", "cosmic"),
    ("Constellation", "cosmic"),
    ("Rocket", "cosmic"), ("Alien", "cosmic"), ("Cosmic Whale", "cosmic"),
    ("Cosmic Wolf", "cosmic"),

    # --- machines & vehicles --------------------------------------------
    ("Chopper Motorcycle", "machine"),
    ("Classic Hot Rod", "machine"),
    ("Fighter Plane", "machine"),
    ("Narrowboat", "machine"),

    # --- nature & botanical ---------------------------------------------
    ("Oak Tree", "botanical"), ("Pine Forest", "botanical"),
    ("Mushroom Cluster", "botanical"), ("Fly Agaric", "botanical"),
    ("Thistle", "botanical"), ("Fern", "botanical"),
    ("Wildflower Bunch", "botanical"), ("Sunflower", "botanical"),
    ("Mountain Range", "botanical"), ("Breaking Wave", "botanical"),]

# =================================================================== SCENES
# The background. Kept as an ATMOSPHERE rather than a full painted scene —
# a filled rectangle of ink looks wrong on a shirt.
SCENES = [
    # Removed Aug 2026: every scene that put something BEHIND the subject —
    # aurora, halo, nebula, radiant light, sacred geometry, hexagon outline.
    # They contradicted BASE ("subject isolated on pure black, nothing behind
    # it"), and the model resolved the contradiction by painting the thing
    # behind. Measured: those scenes flagged at 100% for light backgrounds.
    # "with nothing behind, pure black" is kept — it asks for the right thing.
    # Removed Aug 2026: triangle framing, split circle, arch shape, orbiting
    # rings, geometric light rays. Each drew a hard geometric shape AROUND
    # the subject, so the design read as a printed box on the shirt. The
    # organic framings (foliage, pine branches) stay — they follow the
    # artwork rather than boxing it in.
    # Atmosphere, not location. The references contain no depicted place —
    # they use splatter, smoke, foliage and glow so the subject dissolves
    # into the shirt. A painted scene becomes a rectangle of ink on cotton.
    ("surrounded by drifting embers", "fire"),
    ("wreathed in flames", "fire"),
    ("with glowing neon light trails", "glow"),
    ("backlit by a glowing moon", "glow"),
    ("with luminous particles floating", "glow"),
    ("framed by dark foliage", "botanical"),
    ("surrounded by leaves and vines", "botanical"),
    ("with wildflowers curling around", "botanical"),
    ("entwined with thorns and roses", "botanical"),
    ("with autumn leaves scattering", "botanical"),
    ("amid falling snow", "cold"),
    ("with frost crystals forming", "cold"),
    ("with water splashing around", "water"),
    ("with waves curling beneath", "water"),
    ("in swirling storm clouds", "storm"),
    ("with constellations glowing", "cosmic"),
    ("with nothing behind, pure black", "graphic"),
    ("with shattered glass fragments", "graphic"),
    ("with torn paper texture edges", "graphic"),
    ("with runes glowing faintly", "occult"),
    # --- added to raise the ceiling so no concept needs repeating ---------
    ("with swirling water ribbons", "water"),
    ("with rising bubbles", "water"),
    ("with cracked earth below", "arid"),
    ("with scattered feathers", "botanical"),
    ("with hanging moss", "botanical"),
    ("with mushrooms clustered below", "botanical"),
    ("with pine branches framing", "botanical"),
    ("with sparks scattering", "fire"),
    ("with icicles forming", "cold"),
    ("with torn cloth streaming", "smoke"),
    ("with black feathers falling", "smoke"),
    ("with light beams from above", "glow"),
    ("with alchemical symbols", "occult"),
    ("with candle flames around", "occult"),
    ("with rain streaking down", "storm"),
    ("with wind swept lines", "storm"),
]

# =================================================================== STYLES
# Every one chosen because AI renders it reliably AND DTF prints it cleanly.
# Photoreal is deliberately absent — it prints muddy and reads cheap on cotton.
# =================================================================== STYLES
# Rebuilt around the reference designs. The defining characteristic of all of
# them: THE SUBJECT DISSOLVES INTO BLACK. No borders, no panels, no circles,
# no sticker outlines. The shirt colour IS the background, and the artwork
# fades into it via splatter, smoke, foliage or drips.
#
# This also makes DTF knockout easier rather than harder — you are removing
# pure black from around a naturally soft-edged subject, not cutting a hard
# rectangle out of a filled panel.
#
# Flat vector, stained glass, art nouveau, kawaii, low poly, Celtic knotwork
# and papercut were all removed: every one of them produces a hard bounded
# shape, which is the opposite of the look wanted.
STYLES = [
    # Removed Aug 2026: watercolour splatter, ink dispersion and dripping
    # paint. No amount of "solid, crisp, vibrant" in the base prompt stops a
    # watercolour splatter from splattering — these produce soft edges by
    # their nature, which is what the printer could not hold and what looked
    # faded on the shirt. The airbrush styles stay: smooth gradients but FULL
    # ink coverage, so they print solid.
    # --- painterly dark fantasy: the dominant reference look --------------
    ("dark fantasy digital painting, dramatic rim lighting, bold "
     "saturated colour, crisp edges", "painterly", 6),
    ("epic concept art, dramatic directional lighting, "
     "rich deep shadows, vivid highlights", "painterly", 6),
    ("hyper detailed digital illustration, glowing highlights, "
     "deep black ground, luminous colour", "painterly", 6),


    # --- neon and vivid colour (the dragon) --------------------------------
    ("vibrant neon airbrush art, saturated colour on black, sharp edges "
     "against pure black", "neon", 6),
    ("iridescent colour illustration, electric hues, glowing rim light, "
     "glowing against deep black", "neon", 6),
    ("psychedelic colour explosion, flowing vivid pigment, radiant glow "
     "on black", "neon", 6),

    # --- selective colour (the viking: greyscale plus glowing eyes) --------
    ("dramatic greyscale illustration with one glowing accent colour, "
     "smoky edges, high contrast", "selective", 3),
    ("monochrome charcoal artwork, single luminous colour highlight, "
     "against solid black", "selective", 3),

    # --- botanical framing (the panther) -----------------------------------
    ("subject framed by lush foliage, deep shadow, moonlit highlights, "
     "set against deep black", "botanical", 5),
    ("dark botanical illustration, leaves and vines surrounding subject, "
     "shadowed background", "botanical", 5),

    # --- tattoo: still valid, but no panel or border ----------------------
    ("neo traditional tattoo art, bold linework, rich saturated colour, "
     "no border, black background", "tattoo", 5),
    ("realistic tattoo shading, smooth gradients, deep blacks, "
     "vivid colour accents", "tattoo", 5),

    # --- airbrush and chrome ----------------------------------------------
    ("airbrushed illustration, smooth shading, glossy highlights, "
     "dark atmospheric background", "airbrush", 6),
    ("dark surreal art, double exposure effect, subject merged with "
     "landscape, black ground", "airbrush", 6),

    # --- comic and anime, softened ----------------------------------------
    ("anime key visual, dramatic lighting, bold painted background "
     "to black, cinematic", "anime", 6),
    ("bold graphic illustration, strong shading, glowing accents, "
     "shadowed edges", "anime", 6),
]

# ============================================================= COMPOSITION
# Gated by subject type. A bear does not coil, a hammer has no profile pose,
# and a mushroom does not leap. Ungated, these are the pairings that make a
# catalogue look machine-built.
# (text, tag)
COMPOSITIONS = [
    ("head and shoulders portrait, facing forward", "creature"),
    ("full body, dynamic action pose", "creature"),
    ("side profile, strong silhouette", "creature"),
    ("coiled and looking upward", "serpentine"),
    ("roaring, mouth open, aggressive", "predator"),
    ("calm and watchful, three quarter view", "creature"),
    ("leaping mid air", "agile"),
    ("wings spread wide", "winged"),
    ("seen from below, heroic angle", "creature"),
    ("curled and resting", "creature"),
    ("two subjects together, dynamic", "any"),
    ("centred with radiating energy", "any"),
    ("chest up bust, dramatic pose", "creature"),
    ("centred, bold and iconic", "any"),
    ("three quarter view, detailed", "any"),
    ("stacked vertical arrangement", "any"),

    # --- for human figures: the face is never visible ---------------------
    # SDXL faces at this size often have subtle wrongness (asymmetric eyes,
    # odd teeth, plastic skin) that reads as cheap on a chest print. A covered
    # or turned-away face removes that, removes any likeness question, and
    # usually makes a stronger design anyway.
    ("seen from behind, facing away", "human"),
    ("face hidden in deep shadow", "human"),
    ("helmet visor down, face concealed", "human"),
    ("silhouetted against the light", "human"),
    ("hooded, face in darkness", "human"),
    ("head bowed, features obscured", "human"),
    ("masked, only the eyes visible", "human"),
    ("turned three quarters away", "human"),
]

# Which composition tags each subject family can take.
COMP_FAMILIES = {
    "dragon":    {"creature", "serpentine", "predator", "winged", "any", "mono"},
    "mythic":    {"creature", "predator", "winged", "agile", "any", "mono"},
    "norse":     {"creature", "predator", "any", "mono"},
    "wild":      {"creature", "predator", "agile", "any", "mono"},
    "bird":      {"creature", "winged", "agile", "any", "mono"},
    "sea":       {"creature", "serpentine", "predator", "any", "mono"},
    "reptile":   {"creature", "serpentine", "predator", "any", "mono"},
    "cute":      {"creature", "any"},
    "nature":    {"creature", "winged", "any", "mono"},
    "dino":      {"creature", "predator", "agile", "any", "mono"},
    "gothic":    {"creature", "any", "mono"},
    "warrior":   {"creature", "predator", "any", "mono"},
    "cosmic":    {"creature", "any"},
    "machine":   {"any", "mono"},
    "botanical": {"any", "mono"},
}
# New families, Aug 2026. Each mirrors an existing family whose style and
# scene mix is already proven on the shirt, rather than inventing one.
COMP_FAMILIES["insect"] = COMP_FAMILIES["reptile"]
COMP_FAMILIES["fungi"] = COMP_FAMILIES["botanical"]
COMP_FAMILIES["mineral"] = COMP_FAMILIES["machine"]
COMP_FAMILIES["vehicle"] = COMP_FAMILIES["machine"]
COMP_FAMILIES["tool"] = COMP_FAMILIES["machine"]
COMP_FAMILIES["sport"] = COMP_FAMILIES["machine"]
COMP_FAMILIES["outdoor"] = COMP_FAMILIES["machine"]
COMP_FAMILIES["food"] = COMP_FAMILIES["machine"]
COMP_FAMILIES["music"] = COMP_FAMILIES["machine"]
COMP_FAMILIES["occult"] = COMP_FAMILIES["gothic"]
COMP_FAMILIES["seasonal"] = COMP_FAMILIES["gothic"]
COMP_FAMILIES["folk"] = COMP_FAMILIES["nature"]
COMP_FAMILIES["anatomy"] = COMP_FAMILIES["gothic"]
COMP_FAMILIES["farm"] = COMP_FAMILIES["wild"]
COMP_FAMILIES["amphibian"] = COMP_FAMILIES["reptile"]


# ------------------------------------------------------- pairing rules
# A stained glass axolotl is fine; a kawaii chibi grim reaper is not.
STYLE_FAMILIES = {
    "dragon":    {"painterly", "splatter", "neon", "tattoo", "airbrush",
                  "anime", "selective"},
    "mythic":    {"painterly", "splatter", "neon", "tattoo", "airbrush",
                  "anime", "selective"},
    "norse":     {"painterly", "splatter", "selective", "tattoo", "airbrush"},
    "wild":      {"painterly", "splatter", "neon", "botanical", "tattoo",
                  "airbrush", "selective", "anime"},
    "bird":      {"painterly", "splatter", "neon", "botanical", "tattoo",
                  "airbrush", "selective"},
    "sea":       {"painterly", "splatter", "neon", "tattoo", "airbrush",
                  "anime"},
    "reptile":   {"painterly", "splatter", "neon", "botanical", "tattoo",
                  "airbrush"},
    "cute":      {"painterly", "neon", "anime", "airbrush", "botanical"},
    "nature":    {"painterly", "splatter", "neon", "botanical", "airbrush"},
    "dino":      {"painterly", "splatter", "neon", "anime", "airbrush"},
    "gothic":    {"painterly", "splatter", "selective", "tattoo", "airbrush",
                  "neon"},
    "warrior":   {"painterly", "splatter", "selective", "tattoo", "airbrush",
                  "anime"},
    "cosmic":    {"painterly", "neon", "airbrush", "splatter", "anime"},
    "machine":   {"painterly", "splatter", "selective", "airbrush", "neon"},
    "botanical": {"painterly", "splatter", "neon", "botanical", "airbrush"},
    "breed":     {"painterly", "splatter", "neon", "botanical", "tattoo",
                  "airbrush", "anime", "selective"},
    "academia":  {"painterly", "splatter", "selective", "airbrush"},
    "cottage":   {"painterly", "splatter", "botanical", "airbrush", "neon"},
    "y2k":       {"neon", "airbrush", "splatter", "painterly"},

}
# New families, Aug 2026. Each mirrors an existing family whose style and
# scene mix is already proven on the shirt, rather than inventing one.
STYLE_FAMILIES["insect"] = STYLE_FAMILIES["reptile"]
STYLE_FAMILIES["fungi"] = STYLE_FAMILIES["botanical"]
STYLE_FAMILIES["mineral"] = STYLE_FAMILIES["machine"]
STYLE_FAMILIES["vehicle"] = STYLE_FAMILIES["machine"]
STYLE_FAMILIES["tool"] = STYLE_FAMILIES["machine"]
STYLE_FAMILIES["sport"] = STYLE_FAMILIES["machine"]
STYLE_FAMILIES["outdoor"] = STYLE_FAMILIES["machine"]
STYLE_FAMILIES["food"] = STYLE_FAMILIES["machine"]
STYLE_FAMILIES["music"] = STYLE_FAMILIES["machine"]
STYLE_FAMILIES["occult"] = STYLE_FAMILIES["gothic"]
STYLE_FAMILIES["seasonal"] = STYLE_FAMILIES["gothic"]
STYLE_FAMILIES["folk"] = STYLE_FAMILIES["cottage"]
STYLE_FAMILIES["anatomy"] = STYLE_FAMILIES["gothic"]
STYLE_FAMILIES["farm"] = STYLE_FAMILIES["breed"]
STYLE_FAMILIES["amphibian"] = STYLE_FAMILIES["reptile"]


SCENE_FAMILIES = {
    "dragon":    {"splatter", "smoke", "fire", "glow", "storm", "graphic",
                  "occult", "cosmic"},
    "mythic":    {"splatter", "smoke", "glow", "storm", "graphic", "occult",
                  "cosmic", "fire"},
    "norse":     {"splatter", "smoke", "cold", "fire", "graphic", "occult",
                  "storm"},
    "wild":      {"splatter", "smoke", "botanical", "glow", "cold", "graphic",
                  "storm", "water"},
    "bird":      {"splatter", "smoke", "botanical", "glow", "graphic",
                  "cosmic", "storm"},
    "sea":       {"splatter", "water", "glow", "graphic", "smoke", "cosmic"},
    "reptile":   {"splatter", "botanical", "smoke", "glow", "graphic"},
    "cute":      {"splatter", "botanical", "glow", "graphic", "cosmic"},
    "nature":    {"splatter", "botanical", "glow", "graphic", "cosmic"},
    "dino":      {"splatter", "smoke", "fire", "botanical", "graphic"},
    "gothic":    {"smoke", "splatter", "occult", "glow", "graphic", "storm",
                  "fire"},
    "warrior":   {"splatter", "smoke", "fire", "storm", "graphic", "cold"},
    "cosmic":    {"cosmic", "glow", "graphic", "splatter", "smoke"},
    "machine":   {"smoke", "splatter", "fire", "graphic", "storm", "glow"},
    "botanical": {"botanical", "splatter", "glow", "graphic", "cosmic"},
    "breed":     {"splatter", "botanical", "glow", "graphic", "smoke",
                  "cosmic"},
    "academia":  {"smoke", "splatter", "occult", "glow", "graphic"},
    "cottage":   {"botanical", "splatter", "glow", "graphic"},
    "y2k":       {"glow", "graphic", "splatter", "cosmic", "smoke"},

}
# New families, Aug 2026. Each mirrors an existing family whose style and
# scene mix is already proven on the shirt, rather than inventing one.
SCENE_FAMILIES["insect"] = SCENE_FAMILIES["reptile"]
SCENE_FAMILIES["fungi"] = SCENE_FAMILIES["botanical"]
SCENE_FAMILIES["mineral"] = SCENE_FAMILIES["machine"]
SCENE_FAMILIES["vehicle"] = SCENE_FAMILIES["machine"]
SCENE_FAMILIES["tool"] = SCENE_FAMILIES["machine"]
SCENE_FAMILIES["sport"] = SCENE_FAMILIES["machine"]
SCENE_FAMILIES["outdoor"] = SCENE_FAMILIES["machine"]
SCENE_FAMILIES["food"] = SCENE_FAMILIES["machine"]
SCENE_FAMILIES["music"] = SCENE_FAMILIES["machine"]
SCENE_FAMILIES["occult"] = SCENE_FAMILIES["gothic"]
SCENE_FAMILIES["seasonal"] = SCENE_FAMILIES["gothic"]
SCENE_FAMILIES["folk"] = SCENE_FAMILIES["cottage"]
SCENE_FAMILIES["anatomy"] = SCENE_FAMILIES["gothic"]
SCENE_FAMILIES["farm"] = SCENE_FAMILIES["breed"]
SCENE_FAMILIES["amphibian"] = SCENE_FAMILIES["reptile"]


# Shared by every prompt. This is what makes it a t-shirt and not a poster.
# Kept short deliberately. SDXL's CLIP encoder hard-truncates at 77 tokens,
# and anything past that is silently discarded — including, in the first
# version, the very instructions that make the output printable.
# "subject fades into black" was in here, which is literally an instruction to
# produce the soft edges that will not print and will not hold adhesive. The
# design should be COMPLETE and SOLID on a black ground, not dissolving into
# it. Colour language is also stronger: a sample measured saturation 66 against
# a competitor's 93, which reads as dull in a scrolling feed.
# "solid black background" was a mistake: SDXL reads "solid background" as an
# instruction to PAINT a solid panel, so it filled the frame with a near-black
# rectangle and every design printed as a box. Measured on 10 generations,
# corner luminance ran 18-143 where clean black is under 12 — on some the
# corner was brighter than the subject.
#
# "isolated on pure black" asks for the same dark ground without implying a
# painted surface. The word "background" is deliberately absent.
BASE = (
    "t-shirt design, subject isolated on pure black, nothing behind it, "
    "bold saturated colour, high contrast, crisp clean edges, vibrant"
)
NEGATIVE = (
    "nude, nudity, naked, topless, cleavage, lingerie, bikini, sexual, "
    "suggestive, erotic, revealing clothing, "
    "faded, washed out, muted, desaturated, dull, pastel, "
    "translucent, hazy, wispy, blurry edges, "
    "grey background, light background, white background, border, frame, "
    "panel, backdrop, rectangle, box, full scene, greyscale, text"
)


# ============================================================ HOT NICHES
# Added from 2026 market research. Three findings drove these:
#   * occupation and profession niches dominate because shoppers search with
#     intent — someone buying a nurse shirt knows exactly what they want
#   * pet breeds are consistently top-earning across every platform
#   * current aesthetics (dark academia, cottagecore, Y2K, minimalist line
#     art) are climbing rather than saturated
HOT_SUBJECTS = [

    # --- dog breeds: highest-intent search on every platform -----------
    ("Labrador", "breed"), ("Golden Retriever", "breed"),
    ("German Shepherd", "breed"), ("French Bulldog", "breed"),
    ("Dachshund", "breed"), ("Cocker Spaniel", "breed"),
    ("Springer Spaniel", "breed"), ("Border Collie", "breed"),
    ("Jack Russell", "breed"), ("Staffordshire Bull Terrier", "breed"),
    ("Greyhound", "breed"), ("Whippet", "breed"), ("Pug", "breed"),
    ("Beagle", "breed"), ("Boxer Dog", "breed"), ("Rottweiler", "breed"),
    ("Doberman", "breed"), ("Cockapoo", "breed"), ("Labradoodle", "breed"),
    ("Shih Tzu", "breed"), ("Yorkshire Terrier", "breed"),
    ("Border Terrier", "breed"), ("West Highland Terrier", "breed"),
    ("Cavalier King Charles Spaniel", "breed"), ("Corgi", "breed"),
    ("Dalmatian", "breed"), ("Great Dane", "breed"), ("Poodle", "breed"),
    ("Bernese Mountain Dog", "breed"), ("Siberian Husky", "breed"),
    ("Akita", "breed"), ("Shiba Inu", "breed"), ("Vizsla", "breed"),
    ("Weimaraner", "breed"), ("Basset Hound", "breed"),
    ("Bull Terrier", "breed"), ("Chihuahua", "breed"),
    ("Old English Sheepdog", "breed"), ("Irish Setter", "breed"),
    ("Newfoundland", "breed"),
    # --- cat breeds ----------------------------------------------------
    ("Bengal Cat", "breed"), ("Siamese Cat", "breed"),
    ("Maine Coon", "breed"), ("British Shorthair", "breed"),
    ("Ragdoll Cat", "breed"), ("Persian Cat", "breed"),
    ("Sphynx Cat", "breed"), ("Norwegian Forest Cat", "breed"),
    ("Tabby Cat", "breed"), ("Ginger Cat", "breed"),
    ("Tuxedo Cat", "breed"), ("Tortoiseshell Cat", "breed"),
    # --- horses & farm -------------------------------------------------
    ("Shire Horse", "breed"), ("Shetland Pony", "breed"),
    ("Highland Pony", "breed"), ("Alpaca", "breed"), ("Sheep", "breed"),
    ("Hereford Bull", "breed"), ("Chicken", "breed"), ("Duck", "breed"),
    # --- dark academia: climbing, low saturation -----------------------
    ("Anatomical Diagram", "academia"), ("Celestial Chart", "academia"),
    ("Candlelit Library", "academia"), ("Marble Bust", "academia"),
    # --- cottagecore ---------------------------------------------------
    ("Mushroom Cottage", "cottage"), ("Wildflower Meadow", "cottage"),
    ("Beehive And Bees", "cottage"),
    ("Watering Can And Blooms", "cottage"), ("Hen And Chicks", "cottage"),
    ("Cottage Window", "cottage"), ("Pressed Flowers", "cottage"),
    # --- Y2K / retro -----------------------------------------------------
    ("Chrome Butterfly", "y2k"), ("Chrome Heart", "y2k"),
    ("Retro Sun And Palms", "y2k"),]
SUBJECTS = SUBJECTS + HOT_SUBJECTS

# Style and scene gating for the new families.
STYLE_FAMILIES["human"] = {"painterly", "splatter", "selective", "tattoo",
                           "airbrush", "anime", "neon"}
SCENE_FAMILIES["human"] = {"splatter", "smoke", "fire", "storm", "graphic",
                           "cold", "glow", "occult", "botanical", "water"}
COMP_FAMILIES["human"] = {"human"}          # faceless compositions only

STYLE_FAMILIES.update({
    "breed":    {"painterly", "splatter", "neon", "botanical", "tattoo",
                 "airbrush", "anime", "selective"},
    "academia": {"painterly", "splatter", "selective", "airbrush"},
    "cottage":  {"painterly", "splatter", "botanical", "airbrush", "neon"},
    "y2k":      {"neon", "airbrush", "splatter", "painterly"},
})
SCENE_FAMILIES.update({
    "breed":    {"splatter", "botanical", "glow", "graphic", "smoke",
                 "cosmic"},
    "academia": {"smoke", "splatter", "occult", "glow", "graphic"},
    "cottage":  {"botanical", "splatter", "glow", "graphic"},
    "y2k":      {"glow", "graphic", "splatter", "cosmic", "smoke"},
})
COMP_FAMILIES.update({
    "breed":    {"creature", "any"},
    "academia": {"any"},
    "cottage":  {"any"},
    "y2k":      {"any"},
})

# ---------------------------------------------------- combinatorial index
# ---------------------------------------------------------------------------
# EXPANSION, Aug 2026 — 419 subjects across 15 NEW families.
#
# Added because the vocabulary ran dry: after excluding store 1's designs only
# 365,646 combinations remained and the m12k run used 360,000 of them. More of
# the same animals would not have helped — the per-subject cap is what binds,
# so the fix is MORE SUBJECTS, not more scenes.
#
# These are niches the first 1,093 did not touch at all: insects, fungi,
# minerals and fossils, vehicles, tools and trades, sports, outdoor and
# camping, food and drink, musical instruments, occult and tarot, seasonal
# (Halloween and Christmas), British folk, anatomy and skeletons, farm
# animals, amphibians. All have real t-shirt demand and all draw well as a
# bold isolated graphic on black, which is what the pipeline needs.
#
# 101 proposed names already existed and were dropped automatically rather
# than creating near-duplicates.
# ---------------------------------------------------------------------------
SUBJECTS += [
    ("Death's Head Hawkmoth", "insect"), ("Hercules Beetle", "insect"), ("Jewel Beetle", "insect"),
    ("Orchid Mantis", "insect"), ("Emperor Dragonfly", "insect"), ("Blue Dasher Dragonfly", "insect"),
    ("Carpenter Bee", "insect"), ("Paper Wasp", "insect"), ("Hornet", "insect"),
    ("Leafcutter Ant", "insect"), ("Bullet Ant", "insect"), ("Trapdoor Spider", "insect"),
    ("Peacock Spider", "insect"), ("Wolf Spider", "insect"), ("Black Widow", "insect"),
    ("Orb Weaver", "insect"), ("Emperor Scorpion", "insect"), ("Katydid", "insect"),
    ("Cricket", "insect"), ("Weevil", "insect"), ("Dung Beetle", "insect"),
    ("Glow Worm", "insect"), ("Mayfly", "insect"), ("Blue Morpho Butterfly", "insect"),
    ("Red Admiral Butterfly", "insect"), ("Hummingbird Hawkmoth", "insect"), ("Io Moth", "insect"),
    ("Cecropia Moth", "insect"), ("Rosy Maple Moth", "insect"), ("Giant Water Bug", "insect"),
    ("Antlion", "insect"), ("Death Cap", "fungi"), ("Morel Mushroom", "fungi"),
    ("Porcini", "fungi"), ("Shiitake", "fungi"), ("Oyster Mushroom", "fungi"),
    ("Enoki", "fungi"), ("Lion's Mane Mushroom", "fungi"), ("Turkey Tail", "fungi"),
    ("Chicken of the Woods", "fungi"), ("Bearded Tooth Fungus", "fungi"), ("Puffball", "fungi"),
    ("Stinkhorn", "fungi"), ("Bioluminescent Mushroom", "fungi"), ("Inky Cap", "fungi"),
    ("Bird's Nest Fungus", "fungi"), ("Coral Fungus", "fungi"), ("Bracket Fungus", "fungi"),
    ("Jelly Ear Fungus", "fungi"), ("Amethyst Deceiver", "fungi"), ("Parasol Mushroom", "fungi"),
    ("Blusher Mushroom", "fungi"), ("Velvet Shank", "fungi"), ("Witches Butter", "fungi"),
    ("Slime Mould", "fungi"), ("Lichen Cluster", "fungi"), ("Moss Cushion", "fungi"),
    ("Fern Frond", "fungi"), ("Liverwort", "fungi"), ("Amethyst Geode", "mineral"),
    ("Quartz Cluster", "mineral"), ("Pyrite Cube", "mineral"), ("Malachite", "mineral"),
    ("Labradorite", "mineral"), ("Obsidian Shard", "mineral"), ("Opal", "mineral"),
    ("Fluorite Cluster", "mineral"), ("Bismuth Crystal", "mineral"), ("Selenite Wand", "mineral"),
    ("Tourmaline", "mineral"), ("Citrine Point", "mineral"), ("Rose Quartz", "mineral"),
    ("Lapis Lazuli", "mineral"), ("Turquoise Nugget", "mineral"), ("Garnet Crystal", "mineral"),
    ("Meteorite Fragment", "mineral"), ("Trilobite Fossil", "mineral"), ("Ammonite Fossil", "mineral"),
    ("Amber with Insect", "mineral"), ("Petrified Wood", "mineral"), ("Geode Cross Section", "mineral"),
    ("Volcanic Bomb", "mineral"), ("Sulphur Crystal", "mineral"), ("Halite Cube", "mineral"),
    ("Azurite", "mineral"), ("Rhodochrosite", "mineral"), ("Moldavite", "mineral"),
    ("Agate Slice", "mineral"), ("Peacock Ore", "mineral"), ("Vintage Motorcycle", "vehicle"),
    ("Cafe Racer", "vehicle"), ("Scrambler Bike", "vehicle"), ("Dirt Bike", "vehicle"),
    ("Steam Locomotive", "vehicle"), ("Diesel Locomotive", "vehicle"), ("Bullet Train", "vehicle"),
    ("Tram Car", "vehicle"), ("Double Decker Bus", "vehicle"), ("Classic Pickup Truck", "vehicle"),
    ("Hot Rod", "vehicle"), ("Formula Car", "vehicle"), ("Bulldozer", "vehicle"),
    ("Excavator", "vehicle"), ("Crane Truck", "vehicle"), ("Tugboat", "vehicle"),
    ("Fishing Trawler", "vehicle"), ("Submarine", "vehicle"), ("Hovercraft", "vehicle"),
    ("Seaplane", "vehicle"), ("Cargo Ship", "vehicle"), ("Lighthouse Tender", "vehicle"),
    ("Airship", "vehicle"), ("Helicopter", "vehicle"), ("Cable Car", "vehicle"),
    ("Racing Bicycle", "vehicle"), ("Skateboard Deck", "vehicle"), ("Blacksmith Tongs", "tool"),
    ("Woodworking Plane", "tool"), ("Hand Saw", "tool"), ("Chisel Set", "tool"),
    ("Mallet", "tool"), ("Spirit Level", "tool"), ("Pipe Wrench", "tool"),
    ("Socket Set", "tool"), ("Torque Wrench", "tool"), ("Soldering Iron", "tool"),
    ("Angle Grinder", "tool"), ("Circular Saw", "tool"), ("Sewing Machine", "tool"),
    ("Knitting Needles", "tool"), ("Spinning Wheel", "tool"), ("Potter's Wheel", "tool"),
    ("Kiln", "tool"), ("Easel and Palette", "tool"), ("Fountain Pen", "tool"),
    ("Typewriter", "tool"), ("Printing Press", "tool"), ("Darkroom Enlarger", "tool"),
    ("Sextant", "tool"), ("Compass Rose", "tool"), ("Sundial", "tool"),
    ("Pocket Watch", "tool"), ("Grandfather Clock", "tool"), ("Weighing Scales", "tool"),
    ("Mortar and Pestle", "tool"), ("Alembic Still", "tool"), ("Bunsen Burner", "tool"),
    ("Slide Rule", "tool"), ("Abacus", "tool"), ("Drafting Compass", "tool"),
    ("Surfboard and Wave", "sport"), ("Longboard Surfer", "sport"), ("Skateboarder Mid Trick", "sport"),
    ("BMX Rider", "sport"), ("Mountain Biker", "sport"), ("Rock Climber", "sport"),
    ("Ice Climber", "sport"), ("Bouldering Hold", "sport"), ("Kayaker in Rapids", "sport"),
    ("Whitewater Raft", "sport"), ("Sailing Dinghy", "sport"), ("Windsurfer", "sport"),
    ("Kitesurfer", "sport"), ("Scuba Diver", "sport"), ("Free Diver", "sport"),
    ("Spearfisher", "sport"), ("Fly Fisherman", "sport"), ("Fishing Reel", "sport"),
    ("Angler's Catch", "sport"), ("Archer Drawing Bow", "sport"), ("Crossbow", "sport"),
    ("Fencing Sabre", "sport"), ("Muay Thai Fighter", "sport"), ("Judo Throw", "sport"),
    ("Karate Kick", "sport"), ("Sumo Wrestler", "sport"), ("Weightlifter", "sport"),
    ("Yoga Pose", "sport"), ("Marathon Runner", "sport"), ("Trail Runner", "sport"),
    ("Cyclist Peloton", "sport"), ("Horse Rider Jumping", "sport"), ("Polo Player", "sport"),
    ("Darts Board", "sport"), ("Snooker Table", "sport"), ("Bowling Pins", "sport"),
    ("Chess Knight", "sport"), ("Backpacking Tent", "outdoor"), ("Cast Iron Skillet", "outdoor"),
    ("Enamel Camp Mug", "outdoor"), ("Trekking Poles", "outdoor"), ("Vintage Lantern", "outdoor"),
    ("Hurricane Lamp", "outdoor"), ("Axe in Log", "outdoor"), ("Fire Steel", "outdoor"),
    ("Canoe on Lake", "outdoor"), ("Hammock Between Trees", "outdoor"), ("Mountain Range Silhouette", "outdoor"),
    ("Alpine Summit", "outdoor"), ("Glacier", "outdoor"), ("Waterfall", "outdoor"),
    ("Forest Trail", "outdoor"), ("Log Cabin", "outdoor"), ("Fire Lookout Tower", "outdoor"),
    ("Stone Bothy", "outdoor"), ("Dry Stone Wall", "outdoor"), ("Fell Gate", "outdoor"),
    ("Trig Point", "outdoor"), ("Signpost", "outdoor"), ("Milestone", "outdoor"),
    ("Wooden Bridge", "outdoor"), ("River Crossing", "outdoor"), ("Stargazing Camp", "outdoor"),
    ("Moka Pot", "food"), ("Chemex Brewer", "food"), ("Coffee Beans", "food"),
    ("Cafetiere", "food"), ("Latte Art", "food"), ("Tea Pot", "food"),
    ("Loose Leaf Tea", "food"), ("Matcha Whisk", "food"), ("Pint of Stout", "food"),
    ("Craft Beer Bottle", "food"), ("Hop Cone", "food"), ("Old Fashioned Cocktail", "food"),
    ("Sourdough Loaf", "food"), ("Croissant", "food"), ("Bagel", "food"),
    ("Pretzel", "food"), ("Pizza Slice", "food"), ("Taco", "food"),
    ("Ramen Bowl", "food"), ("Sushi Roll", "food"), ("Dim Sum Basket", "food"),
    ("Curry Bowl", "food"), ("Chilli Pepper", "food"), ("Garlic Bulb", "food"),
    ("Cheese Wheel", "food"), ("Honey Jar", "food"), ("Chocolate Bar", "food"),
    ("Doughnut", "food"), ("Cupcake", "food"), ("Ice Cream Cone", "food"),
    ("Watermelon Slice", "food"), ("Pineapple", "food"), ("Avocado", "food"),
    ("Hot Sauce Bottle", "food"), ("Cast Iron Pan", "food"), ("Banjo", "music"),
    ("Mandolin", "music"), ("Ukulele", "music"), ("Double Bass", "music"),
    ("Grand Piano", "music"), ("Synthesizer", "music"), ("Snare Drum", "music"),
    ("Djembe", "music"), ("Bodhran", "music"), ("Bagpipes", "music"),
    ("Accordion", "music"), ("Harmonica", "music"), ("Trombone", "music"),
    ("French Horn", "music"), ("Clarinet", "music"), ("Flute", "music"),
    ("Pan Pipes", "music"), ("Sitar", "music"), ("Kora", "music"),
    ("Turntable", "music"), ("Mixing Desk", "music"), ("Studio Microphone", "music"),
    ("Guitar Amp", "music"), ("Guitar Pedal", "music"), ("Tuning Fork", "music"),
    ("Metronome", "music"), ("Sheet Music Scroll", "music"), ("Concert Speaker Stack", "music"),
    ("Tarot Sun Card", "occult"), ("Tarot Moon Card", "occult"), ("Ouija Planchette", "occult"),
    ("Scrying Mirror", "occult"), ("Alchemical Sigil", "occult"), ("Philosopher's Stone", "occult"),
    ("Hermetic Seal", "occult"), ("Zodiac Wheel", "occult"), ("Astrolabe Chart", "occult"),
    ("Birth Chart", "occult"), ("Hamsa Hand", "occult"), ("Evil Eye", "occult"),
    ("Dream Catcher", "occult"), ("Smudge Bundle", "occult"), ("Candle and Skull", "occult"),
    ("Grimoire", "occult"), ("Spell Bottle", "occult"), ("Apothecary Shelf", "occult"),
    ("Voodoo Doll", "occult"), ("Black Cat and Moon", "occult"), ("Raven and Skull", "occult"),
    ("Hourglass and Skull", "occult"), ("Memento Mori", "occult"), ("Witch's Hat", "seasonal"),
    ("Black Cauldron", "seasonal"), ("Zombie Hand", "seasonal"), ("Vampire Bat Swarm", "seasonal"),
    ("Werewolf Howling", "seasonal"), ("Frankenstein Bolt", "seasonal"), ("Mummy Wrapping", "seasonal"),
    ("Headless Horseman", "seasonal"), ("Christmas Wreath", "seasonal"), ("Nutcracker Soldier", "seasonal"),
    ("Gingerbread House", "seasonal"), ("Snow Globe", "seasonal"), ("Reindeer Silhouette", "seasonal"),
    ("Sleigh Bells", "seasonal"), ("Christmas Bauble", "seasonal"), ("Advent Candle", "seasonal"),
    ("Yule Log", "seasonal"), ("Robin in Snow", "seasonal"), ("Snowman", "seasonal"),
    ("Ice Skate", "seasonal"), ("Easter Egg", "seasonal"), ("Spring Lamb", "seasonal"),
    ("Maypole", "seasonal"), ("Harvest Moon", "seasonal"), ("Cornucopia", "seasonal"),
    ("Bonfire Night Rocket", "seasonal"), ("Wicker Man", "folk"), ("Morris Dancer Bells", "folk"),
    ("Hobby Horse", "folk"), ("Corn Dolly", "folk"), ("Standing Stone Circle", "folk"),
    ("Barrow Mound", "folk"), ("Chalk Horse", "folk"), ("Sheela na Gig", "folk"),
    ("Celtic Knotwork", "folk"), ("Ogham Stave", "folk"), ("Pictish Beast", "folk"),
    ("Sea Shanty Anchor", "folk"), ("Scrimshaw Whale", "folk"), ("Ship in a Bottle", "folk"),
    ("Mermaid Tail", "folk"), ("Will o the Wisp", "folk"), ("Fairy Ring", "folk"),
    ("Hedgerow Gate", "folk"), ("Thatched Cottage", "folk"), ("Watermill", "folk"),
    ("Village Church", "folk"), ("Market Cross", "folk"), ("Shepherd's Crook", "folk"),
    ("Beehive Skep", "folk"), ("Cider Press", "folk"), ("Anatomical Skull", "anatomy"),
    ("Cross Section Skull", "anatomy"), ("Spine and Ribs", "anatomy"), ("Hand Bones", "anatomy"),
    ("Foot Bones", "anatomy"), ("Pelvis", "anatomy"), ("Ribcage with Flowers", "anatomy"),
    ("Lungs as Trees", "anatomy"), ("Heart with Roots", "anatomy"), ("Brain Coral", "anatomy"),
    ("Eye Anatomy", "anatomy"), ("Ear Anatomy", "anatomy"), ("Vertebrae Stack", "anatomy"),
    ("Femur", "anatomy"), ("Jawbone", "anatomy"), ("Animal Skull", "anatomy"),
    ("Fish Skeleton", "anatomy"), ("Snake Skeleton", "anatomy"), ("Bat Skeleton", "anatomy"),
    ("Frog Skeleton", "anatomy"), ("Cat Skull", "anatomy"), ("Horse Skull", "anatomy"),
    ("Deer Skull with Antlers", "anatomy"), ("Trilobite", "anatomy"), ("Ammonite", "anatomy"),
    ("Fossil Fish", "anatomy"), ("Boer Goat", "farm"), ("Tamworth Pig", "farm"),
    ("Gloucester Old Spot", "farm"), ("Clydesdale", "farm"), ("Rhode Island Red", "farm"),
    ("Silkie Chicken", "farm"), ("Bantam Rooster", "farm"), ("Muscovy Duck", "farm"),
    ("Indian Runner Duck", "farm"), ("Toulouse Goose", "farm"), ("Bronze Turkey", "farm"),
    ("Guinea Fowl", "farm"), ("Barn Owl in Rafters", "farm"), ("Border Collie Herding", "farm"),
    ("Sheepdog Whistle", "farm"), ("Hay Bale", "farm"), ("Barn", "farm"),
    ("Grain Silo", "farm"), ("Red Eyed Tree Frog", "amphibian"), ("Golden Poison Frog", "amphibian"),
    ("Glass Frog", "amphibian"), ("Tomato Frog", "amphibian"), ("Horned Frog", "amphibian"),
    ("Bullfrog", "amphibian"), ("Common Toad", "amphibian"), ("Fire Bellied Toad", "amphibian"),
    ("Cane Toad", "amphibian"), ("Spotted Salamander", "amphibian"), ("Olm", "amphibian"),
    ("Caecilian", "amphibian"), ("Hellbender", "amphibian"), ("Mudpuppy", "amphibian"),
    ("Surinam Toad", "amphibian"), ("Tree Frog Cluster", "amphibian"), ("Tadpole", "amphibian"),
    ("Frog Spawn", "amphibian"), ("Waxy Monkey Frog", "amphibian"), ("Reed Frog", "amphibian"),
    ("Mantella", "amphibian"), ("Spadefoot Toad", "amphibian"), ("Clawed Frog", "amphibian"),
    ("Marsh Frog", "amphibian"), ("Pool Frog", "amphibian"),
]

_STYLE_BY_FAM, _SCENE_BY_FAM, _COMP_BY_FAM = {}, {}, {}
for _s in SUBJECTS:
    fam = _s[1]
    if fam not in _STYLE_BY_FAM:
        _STYLE_BY_FAM[fam] = [i for i, st in enumerate(STYLES)
                              if st[1] in STYLE_FAMILIES.get(fam, set())]
        _SCENE_BY_FAM[fam] = [i for i, sc in enumerate(SCENES)
                              if sc[1] in SCENE_FAMILIES.get(fam, set())]
        _COMP_BY_FAM[fam] = [i for i, cp in enumerate(COMPOSITIONS)
                             if cp[1] in COMP_FAMILIES.get(fam, {"any"})]

# Per-subject scene lists. Thermal overrides are applied HERE, before the
# block sizes are computed — applying them inside design() changed the list
# length after sizing and broke the bijection (two indices could decode to the
# same design). Word-boundary matching too: "tr-ICE-ratops" was matching "ice".
_HOT_WORDS = {"ember", "fire", "flame", "phoenix", "fiery"}
_COLD_WORDS = {"frost", "arctic", "polar", "snow", "ice", "frozen"}

# Match on the scene TEXT as well as its tag. "with candle flames around" is
# tagged occult, so a tag-only check let "Frost Dragon with candle flames"
# through 20 times.
_HOT_TEXT = ("flame", "fire", "ember", "burning", "spark")
_COLD_TEXT = ("snow", "frost", "ice", "icicle", "frozen")

# "Mermaid, helmet visor down" — helmet and mask compositions only suit
# subjects that actually wear one.
_HELMETED = {
    "Knight", "Knight Templar", "Spartan Warrior", "Samurai", "Gladiator",
    "Astronaut", "Deep Sea Diver", "Norse Warrior", "Berserker", "Valkyrie",
}
_MASKED = _HELMETED | {"Ninja", "Plague Doctor", "Highwayman"}
_HOODED = {
    "Grim Reaper", "Hooded Figure", "Witch", "Sea Witch", "Druid", "Monk",
    "Highwayman", "Storm Chaser", "Ronin",
}

_COMP_BY_SUBJECT = []
for _subj, _fam in SUBJECTS:
    _cp = list(_COMP_BY_FAM[_fam])
    if _fam == "human":
        _cp = [i for i in _cp
               if not ("helmet" in COMPOSITIONS[i][0] and _subj not in _HELMETED)
               and not ("masked" in COMPOSITIONS[i][0] and _subj not in _MASKED)
               and not ("hooded" in COMPOSITIONS[i][0] and _subj not in _HOODED)]
    _COMP_BY_SUBJECT.append(_cp)

_SCENE_BY_SUBJECT = []
for _subj, _fam in SUBJECTS:
    _sc = list(_SCENE_BY_FAM[_fam])
    _words = set(_subj.lower().replace("'", " ").split())
    if _words & _HOT_WORDS:
        _sc = [i for i in _sc
               if SCENES[i][1] != "cold"
               and not any(w in SCENES[i][0].lower() for w in _COLD_TEXT)] or _sc
    if _words & _COLD_WORDS:
        _sc = [i for i in _sc
               if SCENES[i][1] != "fire"
               and not any(w in SCENES[i][0].lower() for w in _HOT_TEXT)] or _sc
    _SCENE_BY_SUBJECT.append(_sc)


_OFFSETS, _total = [], 0
for _i, (_subj, _fam) in enumerate(SUBJECTS):
    n = (len(_STYLE_BY_FAM[_fam]) * len(_SCENE_BY_SUBJECT[_i])
         * len(_COMP_BY_SUBJECT[_i]))
    _OFFSETS.append(_total)
    _total += n


TOTAL_SPACE = _total


def design(index):
    """
    Return one design at position `index`.

    Mixed-radix decomposition: each index maps to exactly one
    (subject, style, scene, composition) tuple. No hashing, no collisions.
    """
    if index >= TOTAL_SPACE:
        raise IndexError(
            f"index {index} exceeds the space ({TOTAL_SPACE:,}). "
            "Add subjects, scenes or styles rather than repeating.")

    lo, hi = 0, len(SUBJECTS) - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if _OFFSETS[mid] <= index:
            lo = mid
        else:
            hi = mid - 1
    subject, fam = SUBJECTS[lo]
    local = index - _OFFSETS[lo]

    styles = _STYLE_BY_FAM[fam]
    scenes = _SCENE_BY_SUBJECT[lo]
    comps = _COMP_BY_SUBJECT[lo]


    comp = COMPOSITIONS[comps[local % len(comps)]][0]
    local //= len(comps)
    scene_text, scene_fam = SCENES[scenes[local % len(scenes)]]
    local //= len(scenes)
    style_text, style_fam, palette = STYLES[styles[local % len(styles)]]

    prompt = f"{subject} {scene_text}, {comp}, {style_text}, {BASE}"
    if fam == "human":
        # Belt and braces: the negative prompt blocks the obvious terms, but
        # some subjects (Mermaid, Siren, Valkyrie) have a strong association
        # with revealing depictions in the training data. Say it positively
        # too — models respond better to what TO draw than what to avoid.
        prompt += ", fully clothed, modest dress"

    return {
        "index": index,
        "subject": subject,
        "family": fam,
        "scene": scene_text,
        "style": style_text,
        "style_family": style_fam,
        "composition": comp,
        "palette": palette,
        "prompt": prompt,
        "negative": NEGATIVE,
    }


def generate(start=0, count=None):
    i = start
    made = 0
    while i < TOTAL_SPACE:
        yield design(i)
        made += 1
        if count and made >= count:
            return
        i += 1


if __name__ == "__main__":
    from collections import Counter
    print("GRAPHIC ENGINE")
    print(f"  subjects     : {len(SUBJECTS)}")
    print(f"  scenes       : {len(SCENES)}")
    print(f"  styles       : {len(STYLES)}")
    print(f"  compositions : {len(COMPOSITIONS)}")
    print(f"\n  UNIQUE DESIGNS: {TOTAL_SPACE:,}")

    fams = Counter(f for _, f in SUBJECTS)
    print(f"\n  subject families: {len(fams)}")
    for f, c in fams.most_common(6):
        print(f"    {f:<10} {c}")

    print("\nSAMPLE PROMPTS")
    step = max(1, TOTAL_SPACE // 8)
    for i in range(0, TOTAL_SPACE, step):
        d = design(i)
        if i > step * 7:
            break
        print(f"\n  [{d['family']}] {d['subject']}")
        print(f"    {d['prompt'][:150]}...")
