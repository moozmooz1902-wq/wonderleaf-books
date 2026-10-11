#!/usr/bin/env python3
"""Night sky and solar system. Added 11 Oct 2026 as a fourth subject kind.

Why this block and not three hundred more small towns: the duplicate audit on
the first 12,834 panels found every near-twin was a shared COMPOSITION, not a
shared subject, and the thing most likely to produce shared compositions is a
subject the model cannot tell apart. FLUX knows the moon, Saturn and an aurora
apart. It does not know Tipton from Bloxwich, and renders a generic British
town for both.

Celestial is also entirely IP-free - the IAU constellation roster is a fact,
not a work - and it is a block the measured competitor corpus sells (moon,
star, constellation, galaxy, nebula, planet all appear in the mined titles)
and this catalogue had none of.

Two things are deliberately left out:
  * the zodiac GLYPHS. They are letterforms, so the OCR gate would reject
    most of them and the rest would be a sign nobody can read.
  * 64 of the 88 constellations. A star field of an obscure southern
    constellation hashes the same as any other star field, which is exactly
    the near-duplication this catalogue is built to avoid. Only the ones with
    a shape a buyer recognises are here.
"""

MOON = [
 "a new moon","a waxing crescent moon","a first quarter moon",
 "a waxing gibbous moon","a full moon","a waning gibbous moon",
 "a last quarter moon","a waning crescent moon","a thin crescent moon",
 "a harvest moon","a wolf moon in January","a snow moon in February",
 "a worm moon in March","a pink moon in April","a flower moon in May",
 "a strawberry moon in June","a buck moon in July","a sturgeon moon in August",
 "a corn moon in September","a hunter's moon in October",
 "a beaver moon in November","a cold moon in December","a blue moon",
 "a supermoon","a blood moon","a micromoon","a moonrise over water",
 "a moon behind thin cloud","a moon and a single bare branch",
 "the full moon low over a rooftop","a daytime moon in a pale sky",
 "the moon reflected in a still lake","a crescent moon and the evening star",
]

PLANETS = [
 "the planet Mercury","the planet Venus","the planet Earth from space",
 "the planet Mars","the planet Jupiter","the planet Saturn with its rings",
 "the planet Uranus","the planet Neptune","the dwarf planet Pluto",
 "the dwarf planet Ceres","the dwarf planet Eris","Saturn's rings edge on",
 "Jupiter's great red spot","the moons of Jupiter in a row",
 "Earth's curve from high altitude","the far side of the moon",
 "a crater field on the moon","the surface of Mars","an asteroid",
 "a comet with two tails","Halley's comet","a long period comet",
 "a meteor over a field","a fireball meteor",
]

DEEP_SKY = [
 "the Milky Way arching overhead","the galactic core",
 "a spiral galaxy seen face on","a spiral galaxy seen edge on",
 "the Andromeda galaxy","a barred spiral galaxy","two colliding galaxies",
 "a globular star cluster","an open star cluster","the Pleiades star cluster",
 "the Hyades star cluster","the Beehive cluster","the Double Cluster",
 "the Orion nebula","a pillar of interstellar dust","a dark nebula",
 "a planetary nebula ring","a supernova remnant","a reflection nebula",
 "an emission nebula","a protoplanetary disc","a star forming region",
 "a red giant star","a white dwarf star","a binary star pair",
 "a brown dwarf","a neutron star","a black hole accretion disc",
]

ATMOSPHERE = [
 "the northern lights over a pine forest","the aurora over a fjord",
 "the aurora over a frozen loch","the aurora over snow fields",
 "the aurora over the open sea","the aurora over a mountain ridge",
 "the aurora over a lone cabin","the southern lights",
 "a green auroral curtain","a red aurora","a total solar eclipse",
 "a partial solar eclipse","an annular eclipse ring of fire",
 "the diamond ring at totality","the solar corona",
 "a total lunar eclipse","a sun halo","a sun dog",
 "a crepuscular ray sky","noctilucent clouds","a zodiacal light glow",
 "the midnight sun","the blue hour sky","a green flash at sunset",
 "a moonbow","a star trail circle around the pole star",
 "a long star trail over a ridge","the Perseid meteor shower",
 "the Geminid meteor shower","the Leonid meteor shower",
 "the Quadrantid meteor shower","the Orionid meteor shower",
 "the Lyrid meteor shower","a sky full of stars over a desert",
 "a sky full of stars over the sea","a sky full of stars over a moor",
 "a starry sky over a lighthouse","a starry sky over a stone circle",
 "a starry sky over a bothy","a starry sky over a dark wood",
]

# Only the shapes a buyer can name. 24 of the 88.
CONSTELLATIONS = [
 "the constellation Orion","the constellation Ursa Major",
 "the constellation Ursa Minor","the constellation Cassiopeia",
 "the constellation Cygnus","the constellation Lyra",
 "the constellation Scorpius","the constellation Sagittarius",
 "the constellation Taurus","the constellation Gemini",
 "the constellation Leo","the constellation Draco",
 "the constellation Perseus","the constellation Andromeda",
 "the constellation Pegasus","the constellation Aquila",
 "the constellation Crux the Southern Cross","the constellation Centaurus",
 "the constellation Canis Major","the constellation Auriga",
 "the constellation Bootes","the constellation Hercules",
 "the constellation Carina","the constellation Delphinus",
 "the Plough asterism","Orion's belt","the Summer Triangle",
 "the Great Square of Pegasus","the Coathanger asterism",
 "the Winter Hexagon",
]

ALL = MOON + PLANETS + DEEP_SKY + ATMOSPHERE + CONSTELLATIONS

if __name__ == "__main__":
    import collections
    for k, v in list(globals().items()):
        if isinstance(v, list) and k.isupper() and k != "ALL":
            print(f"{k:<20}{len(v):>6}")
    d = [x for x, c in collections.Counter(ALL).items() if c > 1]
    print(f"{'TOTAL':<20}{len(ALL):>6}   unique {len(set(ALL))}   dupes {d}")
