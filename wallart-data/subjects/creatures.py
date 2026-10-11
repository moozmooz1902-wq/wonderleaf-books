#!/usr/bin/env python3
"""Animals. British wildlife first, because the market is UK, then breeds
and the wider world. No pets by name, no mascots, nothing trademarked."""

BRITISH_MAMMALS = [
 "red fox","badger","otter","brown hare","mountain hare","rabbit","hedgehog",
 "red squirrel","grey squirrel","stoat","weasel","pine marten","polecat",
 "wildcat","red deer stag","red deer hind","roe deer","fallow deer",
 "muntjac deer","sika deer","reindeer","wild boar","water vole","field mouse",
 "harvest mouse","dormouse","shrew","mole","bank vole","common seal",
 "grey seal","harbour porpoise","bottlenose dolphin","minke whale",
 "basking shark","pipistrelle bat","brown long-eared bat","highland cow",
 "belted galloway","shetland pony","dartmoor pony","exmoor pony",
 "welsh mountain pony","new forest pony","herdwick sheep","swaledale sheep",
 "jacob sheep","valais blacknose sheep","suffolk sheep","texel sheep",
 "alpaca","llama","donkey","shire horse","clydesdale","gloucester old spot pig",
 "tamworth pig","kunekune pig","goat","pygmy goat","hereford cow","jersey cow",
 "friesian cow","aberdeen angus","longhorn cattle","white park cattle",
]

BRITISH_BIRDS = [
 "barn owl","tawny owl","little owl","short-eared owl","long-eared owl",
 "snowy owl","european robin","wren","blue tit","great tit","coal tit",
 "long-tailed tit","goldfinch","chaffinch","bullfinch","greenfinch","siskin",
 "linnet","yellowhammer","reed bunting","skylark","meadow pipit","dunnock",
 "house sparrow","tree sparrow","starling","blackbird","song thrush",
 "mistle thrush","fieldfare","redwing","nuthatch","treecreeper","goldcrest",
 "firecrest","swallow","house martin","sand martin","swift","cuckoo",
 "green woodpecker","great spotted woodpecker","lesser spotted woodpecker",
 "jay","magpie","jackdaw","rook","carrion crow","raven","chough",
 "kingfisher","dipper","grey wagtail","pied wagtail","yellow wagtail",
 "kestrel","sparrowhawk","buzzard","red kite","peregrine falcon","merlin",
 "hobby","golden eagle","white-tailed eagle","osprey","hen harrier",
 "marsh harrier","goshawk","puffin","razorbill","guillemot","black guillemot",
 "kittiwake","fulmar","gannet","cormorant","shag","herring gull",
 "black-headed gull","common tern","arctic tern","sandwich tern","little tern",
 "oystercatcher","curlew","lapwing","golden plover","ringed plover","dunlin",
 "redshank","greenshank","snipe","woodcock","avocet","black-tailed godwit",
 "turnstone","sanderling","grey heron","little egret","great white egret",
 "bittern","spoonbill","mute swan","whooper swan","bewick's swan",
 "canada goose","greylag goose","barnacle goose","brent goose","pink-footed goose",
 "mallard","teal","wigeon","pintail","shoveler","gadwall","tufted duck",
 "eider","goldeneye","goosander","red-breasted merganser","shelduck",
 "mandarin duck","great crested grebe","little grebe","moorhen","coot",
 "water rail","corncrake","pheasant","red grouse","black grouse","capercaillie",
 "grey partridge","red-legged partridge","quail","ptarmigan","nightjar",
 "nightingale","blackcap","chiffchaff","willow warbler","sedge warbler",
 "reed warbler","whitethroat","garden warbler","spotted flycatcher",
 "pied flycatcher","redstart","black redstart","wheatear","whinchat","stonechat",
 "ring ouzel","waxwing","crossbill","hawfinch","twite","snow bunting",
]

DOGS = [
 "border collie","labrador retriever","golden retriever","cocker spaniel",
 "english springer spaniel","cavalier king charles spaniel","dachshund",
 "french bulldog","english bulldog","pug","beagle","basset hound","whippet",
 "greyhound","italian greyhound","lurcher","jack russell terrier",
 "border terrier","west highland white terrier","scottish terrier",
 "cairn terrier","yorkshire terrier","airedale terrier","bull terrier",
 "staffordshire bull terrier","fox terrier","norfolk terrier","lakeland terrier",
 "bedlington terrier","irish wolfhound","scottish deerhound","afghan hound",
 "saluki","borzoi","great dane","saint bernard","newfoundland","bernese mountain dog",
 "rottweiler","doberman","boxer","german shepherd","belgian malinois",
 "siberian husky","alaskan malamute","samoyed","akita","shiba inu","chow chow",
 "shar pei","dalmatian","weimaraner","vizsla","pointer","english setter",
 "irish setter","gordon setter","flat-coated retriever","chesapeake bay retriever",
 "nova scotia duck tolling retriever","australian shepherd","shetland sheepdog",
 "rough collie","old english sheepdog","bearded collie","welsh corgi",
 "pembroke welsh corgi","cardigan welsh corgi","papillon","pomeranian",
 "chihuahua","maltese","bichon frise","shih tzu","lhasa apso","pekingese",
 "havanese","miniature schnauzer","standard schnauzer","giant schnauzer",
 "poodle","miniature poodle","toy poodle","cockapoo","labradoodle","cavapoo",
 "goldendoodle","sprocker","springador","puggle","basenji","rhodesian ridgeback",
 "portuguese water dog","spanish water dog","keeshond","finnish lapphund",
 "swedish vallhund","norwegian elkhound","leonberger","mastiff","bullmastiff",
]

CATS = [
 "british shorthair","british longhair","persian cat","siamese cat",
 "maine coon","norwegian forest cat","siberian cat","ragdoll","birman",
 "bengal cat","abyssinian cat","russian blue","scottish fold","sphynx cat",
 "devon rex","cornish rex","burmese cat","tonkinese cat","oriental shorthair",
 "turkish van","turkish angora","somali cat","chartreux","manx cat",
 "egyptian mau","ocicat","american shorthair","exotic shorthair","ragamuffin",
 "selkirk rex","tabby cat","ginger cat","tortoiseshell cat","calico cat",
 "black cat","tuxedo cat","white cat","grey cat",
]

INSECTS_SMALL = [
 "red admiral butterfly","peacock butterfly","painted lady butterfly",
 "small tortoiseshell butterfly","comma butterfly","brimstone butterfly",
 "orange-tip butterfly","common blue butterfly","holly blue butterfly",
 "adonis blue butterfly","chalkhill blue butterfly","gatekeeper butterfly",
 "meadow brown butterfly","ringlet butterfly","speckled wood butterfly",
 "marbled white butterfly","swallowtail butterfly","purple emperor butterfly",
 "white admiral butterfly","silver-washed fritillary","dark green fritillary",
 "small copper butterfly","green hairstreak","elephant hawk-moth",
 "hummingbird hawk-moth","garden tiger moth","cinnabar moth","emperor moth",
 "luna moth","atlas moth","death's-head hawkmoth","poplar hawk-moth",
 "honey bee","bumblebee","red-tailed bumblebee","carder bee","mason bee",
 "leafcutter bee","hoverfly","ladybird","stag beetle","rose chafer",
 "green tiger beetle","devil's coach horse","dragonfly","emperor dragonfly",
 "golden-ringed dragonfly","banded demoiselle","azure damselfly",
 "common darter","grasshopper","bush cricket","praying mantis","cicada",
 "snail","garden spider","jumping spider","woodlouse","earthworm",
]

WORLD_WILDLIFE = [
 "lion","lioness","tiger","snow leopard","leopard","cheetah","jaguar","puma",
 "lynx","caracal","serval","ocelot","clouded leopard","african elephant",
 "asian elephant","giraffe","reticulated giraffe","zebra","grevy's zebra",
 "rhinoceros","black rhino","hippopotamus","cape buffalo","wildebeest",
 "impala","gazelle","springbok","oryx","kudu","eland","warthog","meerkat",
 "african wild dog","spotted hyena","aardvark","pangolin","honey badger",
 "gorilla","mountain gorilla","chimpanzee","orangutan","bonobo","gibbon",
 "mandrill","ring-tailed lemur","sifaka","japanese macaque","proboscis monkey",
 "howler monkey","spider monkey","capuchin monkey","marmoset","tarsier",
 "sloth","three-toed sloth","anteater","armadillo","capybara","tapir",
 "llama andean","alpaca andean","vicuna","guanaco","polar bear","brown bear",
 "grizzly bear","black bear","panda","red panda","sun bear","sloth bear",
 "arctic fox","arctic hare","snowy hare","wolverine","moose","elk","caribou",
 "musk ox","bison","american bison","pronghorn","bighorn sheep","mountain goat",
 "beaver","north american porcupine","raccoon","skunk","opossum","coyote",
 "grey wolf","arctic wolf","timber wolf","fennec fox","kit fox","dingo",
 "kangaroo","red kangaroo","wallaby","koala","wombat","tasmanian devil",
 "echidna","platypus","quokka","sugar glider","numbat","bilby",
 "giant tortoise","galapagos tortoise","sea turtle","green turtle",
 "leatherback turtle","hawksbill turtle","iguana","marine iguana","komodo dragon",
 "chameleon","panther chameleon","gecko","leopard gecko","axolotl",
 "poison dart frog","red-eyed tree frog","common frog","common toad","newt",
 "great crested newt","grass snake","adder","smooth snake","slow worm",
 "humpback whale","blue whale","sperm whale","orca","narwhal","beluga whale",
 "manta ray","whale shark","great white shark","hammerhead shark","seahorse",
 "octopus","cuttlefish","nautilus","jellyfish","clownfish","angelfish",
 "lionfish","pufferfish","sea otter","walrus","manatee","dugong","penguin",
 "emperor penguin","king penguin","gentoo penguin","little blue penguin",
 "albatross","wandering albatross","frigatebird","pelican","flamingo",
 "scarlet macaw","blue and gold macaw","toucan","hornbill","hoopoe",
 "kookaburra","lyrebird","bird of paradise","peacock","peahen","ostrich",
 "emu","cassowary","kiwi","secretary bird","bald eagle","harpy eagle",
 "condor","vulture","roadrunner","hummingbird","ruby-throated hummingbird",
 "kingfisher azure","bee-eater","roller","quetzal","puffin atlantic",
]

ALL = (BRITISH_MAMMALS + BRITISH_BIRDS + DOGS + CATS + INSECTS_SMALL + WORLD_WILDLIFE)

if __name__ == "__main__":
    import collections
    for k, v in list(globals().items()):
        if isinstance(v, list) and k.isupper() and k != "ALL":
            print(f"{k:<20}{len(v):>6}")
    d = [x for x, c in collections.Counter(ALL).items() if c > 1]
    print(f"{'TOTAL':<20}{len(ALL):>6}   unique {len(set(ALL))}   dupes {d}")
