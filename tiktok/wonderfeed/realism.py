"""Camera recipes that keep generated stills from looking AI-generated.

The usual tells in synthetic interiors are over-symmetry, plastic surface
sheen, impossible soft light with no source, and a room too tidy to be real.
Prompt words like "hyperrealistic, 8k, ultra-detailed" make all of that worse,
not better - they push the model toward the glossy render look.

So each video draws a recipe: a real camera/lens pairing, one lighting
condition with a stated source, a film treatment, and two or three domestic
imperfections. Varying these across a batch is also what stops 100 videos from
looking like the same room.
"""

import hashlib
import random

CAMERAS = [
    "shot on a Canon EOS R6 with a 35mm f/1.8",
    "shot on a Fujifilm X-T4 with a 23mm f/2",
    "shot on a Sony A7III with a 50mm f/1.8",
    "shot on an iPhone 15 Pro, main camera",
    "shot on a Nikon Z6 with a 28mm f/2.8",
]

LIGHT = [
    "late afternoon sun coming through a window on the left, long soft shadows",
    "flat overcast daylight from a single window, low contrast",
    "warm lamp light in the evening, one visible light source, rest of room dim",
    "bright mid-morning light, slight lens flare near the window frame",
    "cool north-facing daylight, gentle shadow falloff across the wall",
]

TREATMENT = [
    "natural colour, slight film grain, muted contrast",
    "faint warm colour cast, gentle highlight rolloff",
    "neutral white balance, mild grain, true-to-life colours",
    "slightly desaturated, soft shadows, no HDR look",
]

# Small domestic truths. A real room has these; a rendered one does not.
IMPERFECTIONS = [
    "a UK plug socket visible on the wall",
    "white painted skirting board with a scuff",
    "a radiator partly in frame",
    "a slightly creased cushion",
    "a mug left on a side table",
    "a phone charger cable trailing down the wall",
    "a light switch just off-centre",
    "a rug that is not perfectly straight",
    "a few dried stems in a vase, slightly uneven",
    "faint marks on the wall paint",
]

FRAMING = [
    "eye-level, camera square to the wall",
    "slightly low angle looking up at the wall",
    "from the side of the room at a shallow angle",
    "over the back of the sofa toward the wall",
    "from a doorway, part of the door frame in shot",
    "three-quarter angle, wall receding to the right",
]

# Words that actively make output look synthetic - kept here so the negative
# guidance stays in one place.
AVOID = (
    "Not a 3D render, not CGI, not a showroom, not a catalogue photo. "
    "Avoid perfect symmetry, avoid glossy plastic surfaces, avoid unreadable "
    "text or lettering, avoid warped frame corners, avoid over-saturation."
)


def recipe(seed_text, beat_index):
    """Camera, light and grade are fixed per video - it is one room on one
    afternoon, and shifting them between beats reads as three separate shoots.
    Only framing and the visible clutter move from beat to beat."""
    shoot = random.Random(
        int(hashlib.sha256(seed_text.encode()).hexdigest()[:16], 16)
    )
    camera = shoot.choice(CAMERAS)
    light = shoot.choice(LIGHT)
    treatment = shoot.choice(TREATMENT)
    # Framing rotates through distinct set-ups without repeating within a video.
    order = FRAMING[:]
    shoot.shuffle(order)

    beat = random.Random(
        int(hashlib.sha256(f"{seed_text}:{beat_index}".encode()).hexdigest()[:16], 16)
    )
    return {
        "camera": camera,
        "light": light,
        "treatment": treatment,
        "framing": order[beat_index % len(order)],
        "imperfections": ", ".join(beat.sample(IMPERFECTIONS, 2)),
    }


def style_tail(seed_text, beat_index):
    """The realism block appended to a beat's scene description."""
    r = recipe(seed_text, beat_index)
    return (
        f"Photographed as a real interior photo: {r['camera']}, {r['light']}. "
        f"Composition {r['framing']}. Room is lived-in, not staged: "
        f"{r['imperfections']}. {r['treatment']}. "
        f"Vertical 9:16 crop. No text or watermark anywhere in the image. "
        f"{AVOID}"
    )
