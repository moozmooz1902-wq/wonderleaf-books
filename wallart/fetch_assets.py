#!/usr/bin/env python3
"""Download the free assets the generator and renderer need. Safe to re-run.

    python3 fetch_assets.py

- Fonts: Google Fonts, all SIL Open Font License or Apache 2.0, so they can be
  used commercially and printed on products you sell.
- Scripture: World English Bible, British Edition. Public domain, British
  spelling, uses "LORD". The King James Version is avoided on purpose: in the
  UK it is still under Crown letters patent.
"""
import io, sys, urllib.request, zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = HERE / "assets" / "fonts"
RAW = "https://raw.githubusercontent.com/google/fonts/main/"

# local name -> path in the google/fonts repo
FONT_FILES = {
    "AbrilFatface.ttf": "ofl/abrilfatface/AbrilFatface-Regular.ttf",
    "BebasNeue.ttf": "ofl/bebasneue/BebasNeue-Regular.ttf",
    "Anton.ttf": "ofl/anton/Anton-Regular.ttf",
    "Pacifico.ttf": "ofl/pacifico/Pacifico-Regular.ttf",
    "GreatVibes.ttf": "ofl/greatvibes/GreatVibes-Regular.ttf",
    "Sacramento.ttf": "ofl/sacramento/Sacramento-Regular.ttf",
    "Allura.ttf": "ofl/allura/Allura-Regular.ttf",
    "Satisfy.ttf": "apache/satisfy/Satisfy-Regular.ttf",
    "AmaticSC.ttf": "ofl/amaticsc/AmaticSC-Bold.ttf",
    "AlfaSlabOne.ttf": "ofl/alfaslabone/AlfaSlabOne-Regular.ttf",
    "Rye.ttf": "ofl/rye/Rye-Regular.ttf",
    "DMSerifDisplay.ttf": "ofl/dmserifdisplay/DMSerifDisplay-Regular.ttf",
    "DMSerifDisplayItalic.ttf": "ofl/dmserifdisplay/DMSerifDisplay-Italic.ttf",
    "Cinzel.ttf": "ofl/cinzel/Cinzel%5Bwght%5D.ttf",
    "PlayfairDisplay.ttf": "ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf",
    "PlayfairDisplayItalic.ttf": "ofl/playfairdisplay/PlayfairDisplay-Italic%5Bwght%5D.ttf",
    "Montserrat.ttf": "ofl/montserrat/Montserrat%5Bwght%5D.ttf",
    "Oswald.ttf": "ofl/oswald/Oswald%5Bwght%5D.ttf",
    "JosefinSans.ttf": "ofl/josefinsans/JosefinSans%5Bwght%5D.ttf",
    "DancingScript.ttf": "ofl/dancingscript/DancingScript%5Bwght%5D.ttf",
    "Caveat.ttf": "ofl/caveat/Caveat%5Bwght%5D.ttf",
    "Fredoka.ttf": "ofl/fredoka/Fredoka%5Bwdth,wght%5D.ttf",
    "LeagueSpartan.ttf": "ofl/leaguespartan/LeagueSpartan%5Bwght%5D.ttf",
    "Lobster.ttf": "ofl/lobster/Lobster-Regular.ttf",
    "YesevaOne.ttf": "ofl/yesevaone/YesevaOne-Regular.ttf",
    "SpecialElite.ttf": "apache/specialelite/SpecialElite-Regular.ttf",
    "PermanentMarker.ttf": "apache/permanentmarker/PermanentMarker-Regular.ttf",
    "Limelight.ttf": "ofl/limelight/Limelight-Regular.ttf",
    "PoiretOne.ttf": "ofl/poiretone/PoiretOne-Regular.ttf",
    "Chewy.ttf": "apache/chewy/Chewy-Regular.ttf",
    "LuckiestGuy.ttf": "apache/luckiestguy/LuckiestGuy-Regular.ttf",
    "UnifrakturMaguntia.ttf": "ofl/unifrakturmaguntia/UnifrakturMaguntia-Book.ttf",
    "Raleway.ttf": "ofl/raleway/Raleway%5Bwght%5D.ttf",
    "CormorantGaramond.ttf": "ofl/cormorantgaramond/CormorantGaramond%5Bwght%5D.ttf",
}

BIBLE_URL = "https://ebible.org/Scriptures/eng-webbe_vpl.zip"


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    FONTS.mkdir(parents=True, exist_ok=True)
    bad = []
    for name, path in FONT_FILES.items():
        out = FONTS / name
        if out.exists() and out.stat().st_size > 1000:
            continue
        try:
            out.write_bytes(get(RAW + path))
            print("font", name)
        except Exception as e:
            bad.append(f"{name}: {e}")
    bible = HERE / "assets" / "eng-webbe_vpl.txt"
    if not bible.exists():
        z = zipfile.ZipFile(io.BytesIO(get(BIBLE_URL)))
        bible.write_bytes(z.read("eng-webbe_vpl.txt"))
        print("scripture downloaded")
    if bad:
        sys.exit("FAILED:\n  " + "\n  ".join(bad))
    print("assets ready")


if __name__ == "__main__":
    main()
