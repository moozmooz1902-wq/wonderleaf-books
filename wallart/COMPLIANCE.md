# IP and VeRO safety

eBay's VeRO programme lets rights owners have listings removed, and repeated
removals restrict or close the account. This catalogue is built so that
nothing we list gives a rights owner a reason to report it.

## How it is enforced

`compliance.py` is a gate that everything passes through:

| Stage | What is checked |
|---|---|
| Phrase banks (`banks/`) | Every hand-written line and slot value. Run `python3 compliance.py` for an audit; it must report 0. |
| Phrase expansion (`phrases.py`) | Every phrase a template produces, before it can be used. |
| Titles (`generate.py`) | Every 80-character title, so a venue or colour word can't collide with a brand. |
| AI phrases (`expand_phrases.py`) | Every phrase Claude writes, plus a system prompt forbidding lyrics, quotes, brands and slogan formats. |
| eBay files (`build_ebay.py`) | Every listing title and phrase again, at export. |

`python3 compliance.py "some text"` checks a single phrase.

## What is blocked

- **Brands:** drinks (Aperol, Pimm's, Baileys, Guinness, Hendrick's, Yorkshire Tea, Costa...), food, retail,
  fashion (including "Vogue"), cars (Ford, Bentley, Jaguar, Land Rover...), toys and games (Scrabble, Monopoly, Lego),
  tech.
- **Franchises and catchphrases:** Disney, Marvel, Harry Potter, Star Wars, Peaky Blinders, Only Fools and Horses,
  Friends, Bond, children's characters (Peppa, Gruffalo, Paddington...), "Keep Calm...", "Live Laugh Love",
  "There's no place like home".
- **Sport:** clubs, leagues, stadiums and tournaments (Premier League, Wembley, Wimbledon, F1...).
- **Protected food and drink names:** Champagne, Prosecco, Cava, Cognac, Tequila, Stilton, Melton Mowbray pork pie...
- **Trademarked or copyrighted phrases:** "Gin/Wine/Prosecco O'Clock", "Rosé All Day", "Eat Sleep ... Repeat",
  "Beast Mode", "Girl Boss", "Good Vibes Only", "Train Insane", "Bang Tidy", song titles and lyrics
  ("Let It Go", "Here Comes the Sun", "It's Five O'Clock Somewhere"...), and hymns still in copyright
  ("How Great Thou Art", "Morning Has Broken").
- **Artists still in copyright:** Banksy, Picasso, Dalí, Warhol, Lowry, Hockney, Hopper, Magritte and others (died
  after 1955), Frida Kahlo (the name is a trade mark), and museum names (they imply endorsement).
- **Celebrities and royals:** likeness and name rights.

## What was removed

The first audit caught 63 lines I had written. They were deleted from the banks, including:

- every "Keep Calm..." line
- every alcohol "o'clock" phrase
- Aperol, Tequila, Prosecco and Champagne mentions
- Yorkshire Tea
- "Beast Mode", "Girl Boss", "Just Dance", "Blonde Ambition", "Started From the Bottom", "Let It Go", "Let It Be"
- three hymns still in copyright
- "Rawr Means I Love You in Dinosaur"
- "Eat Sleep ... Repeat" templates

Place and name slots that collide with protected names were also removed: Wimbledon, Wembley, Tottenham, West Ham,
Vauxhall and Bentley as towns, and Ford as a surname.

## What is safe and why

- **Fonts:** Google Fonts under the SIL Open Font License or Apache 2.0. Both allow commercial printing
  (`assets/fonts/LICENSES.md`).
- **Scripture:** World English Bible, British Edition, which is public domain. The King James Version is avoided
  because it is under Crown letters patent in the UK. "World English Bible" is a trade mark, so it never appears
  in a title.
- **Maps:** Natural Earth outlines, which are public domain.
- **Quotes:** only proverbs and authors who died more than 70 years ago (Austen, Wilde, Shakespeare, Seneca,
  Marcus Aurelius...), which are out of copyright in the UK.
- **Everything else:** original wording written for this catalogue.

## Limits: what a word list cannot catch

- **An unfamiliar song lyric or modern poem.** AI-written phrases are also screened by the model. When the API key
  is available, the whole bank should get one model review pass as well.
- **Trade mark registrations change.** When eBay removes a listing, add the phrase to `compliance.py` and rebuild.
  The whole catalogue re-checks in minutes.
- **UK trade mark status of generic sign phrases.** Examples: "Home Sweet Home", "Kitchen Rules". These are widely
  used and hard to register as trade marks. No registration is known for any phrase kept here.
