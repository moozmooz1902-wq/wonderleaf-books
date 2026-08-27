"""Quantify bigboxart's title formula against Wonderleaf's live titles."""
import re, collections

BBA = """Birch Forest Rhythm Minimalist Canvas Print Wall Art Home Decor Ready to Hang
Songbird at Rest Japandi Canvas Print Wall Art Home Decor Ready to Hang
Canyon Light and Shadow Landscape Canvas Print Wall Art Home Decor Ready to Hang
Pelican Study Vintage Canvas Print Wall Art Home Decor Ready to Hang
Misty Valley Reflection Scandinavian Canvas Print Wall Art Home Decor
Postcard from Abu Dhabi Vintage Canvas Print Wall Art Home Decor Ready to Hang
Hummingbird in Bloom Botanical Canvas Print Wall Art Home Decor Ready to Hang
Orange Geometry Mid-Century Canvas Print Wall Art Home Decor Ready to Hang
Solitary Path in Autumn Rustic Canvas Print Wall Art Home Decor Ready to Hang
Great Blue Heron Landscape Bird John James Audubon Framed Wall Art Print
Modern Botanical Study Mid-Century Set of 3 Framed Wall Art Prints Home Decor
Duck In A Suit Canvas Wall Art Print Home Decor Ready to Hang
Leopard Face Modern Framed Wall Art Print Home Decor Ready to Hang""".strip().split("\n")

WL = ["Rugby Ball Kraft Poster Terracotta A4 Wall Art Print",
      "Virgo Constellation Retro 70s Black And White A4 Wall Art Print",
      "Sea Turtle Watercolour Loose Muted Pastels A4 Wall Art Print"]

# the commercial / product-noun tail each seller buys with its characters
PRODUCT_WORDS = r"canvas|print|wall art|home decor|ready to hang|poster|picture|framed|unframed|set of|prints"

def commercial_chars(t):
    hits = [m.group(0) for m in re.finditer(PRODUCT_WORDS, t, re.I)]
    return sum(len(h) for h in hits)

print("=" * 68)
print("TITLE BUDGET: how each seller spends its 80 characters")
print("=" * 68)
for name, group in (("bigboxart", BBA), ("Wonderleaf", WL)):
    L = [len(t) for t in group]
    C = [commercial_chars(t) for t in group]
    print(f"\n  {name}")
    print(f"    title length      mean {sum(L)/len(L):5.1f}   unused of 80: {80-sum(L)/len(L):5.1f}")
    print(f"    product/commercial words   mean {sum(C)/len(C):5.1f} chars "
          f"({sum(C)/sum(L):.0%} of the title)")

print("\n" + "=" * 68)
print("STYLE VOCABULARY: searched vs not searched")
print("=" * 68)
searched = ["Minimalist","Japandi","Scandinavian","Botanical","Mid-Century","Vintage",
            "Modern","Coastal","Retro","Boho","Rustic","Art Deco","Landscape"]
not_searched = ["Kraft Poster","Muted Pastels","Terracotta","Ochre","Industrial Loft",
                "Colour Field","Tachisme","Watercolour Loose","Greyscale"]
print("\n  bigboxart uses (all high-volume search terms):")
print("   ", ", ".join(searched))
print("\n  Wonderleaf uses (generator taxonomy - near-zero search volume):")
print("   ", ", ".join(not_searched))
print("\n  -> Including a STYLE is right. The specific WORDS are what is wrong.")

print("\n" + "=" * 68)
print("GRID SERIES visible in bigboxart's catalogue")
print("=" * 68)
print("  'Postcard from {place}'  -> Abu Dhabi, Maldives, Provence, Boston,")
print("                              Mallorca, Richmond Park, the Cliffs")
print("  '{animal} In A Suit'     -> Duck, Giraffe, Hedgehog, Stag, Monkey")
print("  '{artist} {work}'        -> Audubon, Constable, Turner, Mucha,")
print("                              Waterhouse, Modigliani, Grimshaw, Ohara Koson")
print("  Same subject x {Canvas | Framed | Set of 3} = 2-3 listings per design")
