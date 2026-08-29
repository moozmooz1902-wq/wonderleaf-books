"""Turn a brief's beats into still frames, and optionally into motion clips."""

from pathlib import Path

from . import falclient

STILL_STYLE = (
    "Photorealistic interior photography, shot on a 35mm lens, natural window "
    "light, soft shadows, realistic materials and textures, colour-graded warm "
    "and neutral, vertical 9:16 composition, no text, no watermark, no people's "
    "faces in focus."
)

PLACEHOLDER_PALETTE = [(214, 206, 194), (226, 219, 208), (198, 190, 178)]


def placeholder_still(index, out_path, settings):
    """Offline stand-in so the pipeline can be exercised without API keys."""
    from PIL import Image, ImageDraw

    v = settings["video"]
    W, H = v["width"], v["height"]
    img = Image.new("RGB", (W, H), PLACEHOLDER_PALETTE[index % len(PLACEHOLDER_PALETTE)])
    d = ImageDraw.Draw(img)
    if index > 0:  # beats 2 and 3 show the trio on the wall
        top, h, w, gap = int(H * 0.42), int(H * 0.20), int(W * 0.22), int(W * 0.04)
        total = 3 * w + 2 * gap
        x = (W - total) // 2
        for _ in range(3):
            d.rectangle([x, top, x + w, top + h], fill=(250, 248, 244),
                        outline=(38, 38, 38), width=7)
            x += w + gap
    img.save(out_path, quality=92)
    return out_path


def build_stills(brief, product_image_bytes, settings, fal_key, workdir, log=print):
    """One still per beat, all anchored to the real product photo."""
    reference = falclient.data_url_from_bytes(product_image_bytes)
    endpoint = settings["models"]["still_endpoint"]
    stills = []
    for i, beat in enumerate(brief["beats"]):
        out = Path(workdir) / f"still{i}.jpg"
        prompt = f"{beat['scene']}. {STILL_STYLE}"
        log(f"  still {i + 1}/3 ...")
        data = falclient.image(endpoint, prompt, reference, fal_key, aspect="9:16", log=log)
        out.write_bytes(data)
        stills.append(out)
    return stills


def build_clips(brief, stills, settings, fal_key, workdir, log=print):
    """Animate each still. Falls back to the still if a clip fails."""
    endpoint = settings["models"]["motion_endpoint"]
    beat_seconds = settings["video"]["beat_seconds"]
    clips = []
    for i, (beat, still) in enumerate(zip(brief["beats"], stills)):
        out = Path(workdir) / f"clip{i}.mp4"
        ref = falclient.data_url_from_bytes(still.read_bytes())
        # Most image-to-video endpoints only accept 5s or 10s.
        duration = 5 if beat_seconds[i] <= 5 else 10
        log(f"  clip {i + 1}/3 ({duration}s) ...")
        try:
            data = falclient.video(endpoint, beat["motion"], ref, fal_key,
                                   duration=duration, log=log)
            out.write_bytes(data)
            clips.append(out)
        except Exception as exc:
            log(f"  clip {i + 1} failed ({exc}); falling back to a still pan")
            clips.append(None)
    return clips
