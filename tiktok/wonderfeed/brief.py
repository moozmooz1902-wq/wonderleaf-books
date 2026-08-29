"""Claude writes the video brief: hook, three beats, caption, hashtags.

The output drives every downstream stage, so it is strict JSON and validated
before anything expensive (image or video generation) runs.
"""

import json

SYSTEM = """You write short-form TikTok scripts for a UK wall-art shop. \
You are writing for TikTok Shop, where the video's only job is to stop the \
scroll and make someone tap the product link.

Hard rules:
- British English (colour, cosy, flat, wardrobe, skirting board).
- The viewer is scrolling at speed. The hook must land in under 1.5 seconds.
- Never say "buy now", "link in bio", "check out my shop" as the hook.
- No fake scarcity, no invented reviews, no invented statistics, no claims \
about delivery times or discounts that were not supplied to you.
- Sound like a person who decorated their own flat, not a brand advert.
- On-screen text: max 7 words per beat. It is read, not spoken.
- The product is a set of prints. Never imply it is framed unless told so.
"""

PROMPT = """Write ONE TikTok video for this product.

PRODUCT
Name: {name}
Price: £{price}
Description: {description}
Room setting for this video: {room}

ANGLE FOR THIS VIDEO (the specific viewer problem to open on):
{angle}

DO NOT reuse or lightly reword any of these hooks already used:
{used_hooks}

STRUCTURE - exactly three beats:
1. HOOK ({b0}s) - the problem, shot on a bare or badly-styled wall. \
Tension, no product visible yet.
2. REVEAL ({b1}s) - the prints go up. The moment of change.
3. PAYOFF ({b2}s) - the finished wall in a styled room, calm and aspirational.

For each beat give:
- "onscreen_text": max 7 words, the burned-in caption for that beat
- "scene": a literal visual description for an image generator. Describe the \
room, lighting, camera angle and where the artwork sits. Keep the upper third \
of the frame clear (plain wall, ceiling or empty space) because burned-in text \
sits there. For beats 2 and 3 the artwork on the wall MUST be the product from \
the reference image, unchanged.
- "motion": one short camera instruction (e.g. "slow push in", "tilt up the wall")

Also give:
- "hook": the hook line as one sentence (this is your beat-1 text, spelled out)
- "voiceover": 2-3 sentences of natural spoken narration covering all three \
beats, under 28 words total. Conversational, no advert voice.
- "caption": the TikTok caption, under 150 characters, no hashtags inside it
- "hashtags": 5-8 hashtags as an array of strings WITHOUT the # symbol. Mix \
broad (homedecor) with specific (rentersfriendly, gallerywall). UK-leaning.

Return ONLY valid JSON, no preamble, no code fence:

{{
  "hook": "...",
  "beats": [
    {{"onscreen_text": "...", "scene": "...", "motion": "..."}},
    {{"onscreen_text": "...", "scene": "...", "motion": "..."}},
    {{"onscreen_text": "...", "scene": "...", "motion": "..."}}
  ],
  "voiceover": "...",
  "caption": "...",
  "hashtags": ["...", "..."]
}}"""


class BriefError(RuntimeError):
    pass


def _strip_fence(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def validate(brief):
    """Fail loudly before we spend money on images."""
    if not isinstance(brief, dict):
        raise BriefError("brief is not an object")
    beats = brief.get("beats")
    if not isinstance(beats, list) or len(beats) != 3:
        raise BriefError(f"expected 3 beats, got {len(beats) if isinstance(beats, list) else 'none'}")
    for i, b in enumerate(beats):
        for field in ("onscreen_text", "scene", "motion"):
            if not str(b.get(field, "")).strip():
                raise BriefError(f"beat {i + 1} missing '{field}'")
        words = len(str(b["onscreen_text"]).split())
        if words > 9:
            raise BriefError(f"beat {i + 1} on-screen text is {words} words (max 7-ish)")
    for field in ("hook", "caption", "voiceover"):
        if not str(brief.get(field, "")).strip():
            raise BriefError(f"missing '{field}'")
    tags = brief.get("hashtags")
    if not isinstance(tags, list) or not 3 <= len(tags) <= 12:
        raise BriefError("hashtags must be a list of 3-12 items")
    brief["hashtags"] = [str(t).lstrip("#").strip() for t in tags if str(t).strip()]
    if len(brief["caption"]) > 200:
        brief["caption"] = brief["caption"][:197].rstrip() + "..."
    return brief


def write_brief(product, angle, room, settings, api_key, used_hooks=(), log=print):
    """Ask Claude for one video brief. Retries once on malformed output."""
    import anthropic

    beats = settings["video"]["beat_seconds"]
    prompt = PROMPT.format(
        name=product["name"],
        price=product.get("price_gbp", "—"),
        description=product["description"].strip(),
        room=room,
        angle=angle,
        used_hooks="\n".join(f"- {h}" for h in used_hooks[-40:]) or "- (none yet)",
        b0=beats[0], b1=beats[1], b2=beats[2],
    )

    client = anthropic.Anthropic(api_key=api_key)
    last_error = None
    for attempt in (1, 2):
        resp = client.messages.create(
            model=settings["models"]["script_model"],
            max_tokens=1500,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = _strip_fence(resp.content[0].text)
        try:
            return validate(json.loads(raw))
        except (json.JSONDecodeError, BriefError) as exc:
            last_error = exc
            log(f"  brief attempt {attempt} rejected: {exc}")
            prompt = (
                prompt
                + f"\n\nYour previous reply was rejected: {exc}. "
                "Return ONLY the corrected JSON."
            )
    raise BriefError(f"Claude did not return a usable brief: {last_error}")
