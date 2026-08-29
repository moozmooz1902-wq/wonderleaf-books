"""Assemble beats into a 1080x1920 TikTok MP4 with ffmpeg.

On-screen text is drawn with Pillow into a transparent PNG and overlaid,
rather than using ffmpeg's drawtext - it avoids the filtergraph escaping
minefield and gives real word wrapping and stroke control.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


class RenderError(RuntimeError):
    pass


def ffmpeg_exe():
    """Find a full-featured ffmpeg. Playwright's stripped build will not do."""
    env = os.environ.get("FFMPEG_BINARY")
    if env and Path(env).exists():
        return env
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:  # pragma: no cover
        raise RenderError(
            "No ffmpeg found. Install one with: pip install imageio-ffmpeg"
        ) from exc


def _run(args):
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = proc.stderr.strip().splitlines()[-12:]
        raise RenderError("ffmpeg failed:\n  " + "\n  ".join(tail))


def _font(size):
    from PIL import ImageFont

    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def text_overlay_png(text, settings, out_path):
    """Transparent 1080x1920 PNG holding one beat's burned-in caption."""
    from PIL import Image, ImageDraw

    v = settings["video"]
    W, H = v["width"], v["height"]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = _font(v["font_size"])

    # Wrap to the usable width (85% of frame).
    max_w = int(W * 0.85)
    words, lines, cur = str(text).split(), [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)

    line_h = int(v["font_size"] * 1.28)
    block_h = line_h * len(lines)

    # Sit inside TikTok's safe area, biased up - the bottom is covered by the
    # caption and the action rail.
    safe_top = int(H * v["safe_top_pct"])
    safe_bottom = int(H * (1 - v["safe_bottom_pct"]))
    bias = v.get("text_bias", 0.18)
    y = safe_top + int((safe_bottom - safe_top - block_h) * bias)

    for line in lines:
        w = draw.textlength(line, font=font)
        draw.text(
            ((W - w) / 2, y),
            line,
            font=font,
            fill=v["font_colour"],
            stroke_width=v["stroke_width"],
            stroke_fill=v["stroke_colour"],
        )
        y += line_h

    img.save(out_path, "PNG")
    return out_path


def still_to_segment(still, overlay, duration, out_path, settings, zoom_in=True):
    """Ken Burns move over a still, with the text overlay burned in."""
    v = settings["video"]
    W, H, fps = v["width"], v["height"], v["fps"]
    frames = max(2, int(round(duration * fps)))
    # Oversample first so the zoom stays sharp.
    zoom = (
        f"min(1+0.0011*on,1.13)" if zoom_in else f"max(1.13-0.0011*on,1.0)"
    )
    vf = (
        f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,"
        f"crop={W * 2}:{H * 2},"
        f"zoompan=z='{zoom}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
        f":s={W}x{H}:fps={fps},"
        f"trim=end_frame={frames},setpts=PTS-STARTPTS[bg];"
        f"[bg][1:v]overlay=0:0:format=auto,format=yuv420p"
    )
    _run([
        ffmpeg_exe(), "-y", "-loglevel", "error",
        "-loop", "1", "-framerate", str(fps), "-t", f"{duration}", "-i", str(still),
        "-i", str(overlay),
        "-filter_complex", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(fps), "-an",
        str(out_path),
    ])
    return out_path


def clip_to_segment(clip, overlay, duration, out_path, settings):
    """Trim/scale a generated video clip to the beat and burn the text in."""
    v = settings["video"]
    W, H, fps = v["width"], v["height"], v["fps"]
    vf = (
        f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},fps={fps},trim=duration={duration},setpts=PTS-STARTPTS[bg];"
        f"[bg][1:v]overlay=0:0:format=auto,format=yuv420p"
    )
    _run([
        ffmpeg_exe(), "-y", "-loglevel", "error",
        "-i", str(clip), "-i", str(overlay),
        "-filter_complex", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-r", str(fps), "-an",
        str(out_path),
    ])
    return out_path


def concat(segments, out_path, settings, audio=None):
    """Join beat segments and lay the voiceover (or silence) underneath."""
    fps = settings["video"]["fps"]
    with tempfile.TemporaryDirectory() as tmp:
        listfile = Path(tmp) / "segments.txt"
        listfile.write_text(
            "".join(f"file '{Path(s).resolve()}'\n" for s in segments), encoding="utf-8"
        )
        args = [
            ffmpeg_exe(), "-y", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(listfile),
        ]
        if audio:
            # apad keeps a short voiceover from truncating the video via -shortest.
            args += [
                "-i", str(audio),
                "-filter_complex", "[1:a]apad,aresample=44100[aout]",
                "-map", "0:v:0", "-map", "[aout]",
            ]
        else:
            args += [
                "-f", "lavfi", "-i",
                "anullsrc=channel_layout=stereo:sample_rate=44100",
                "-map", "0:v:0", "-map", "1:a:0",
            ]
        args += [
            "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-shortest", "-movflags", "+faststart",
            str(out_path),
        ]
        _run(args)
    return out_path


def probe_duration(path):
    """Duration in seconds, via ffmpeg's own stderr (no ffprobe dependency)."""
    proc = subprocess.run(
        [ffmpeg_exe(), "-i", str(path)], capture_output=True, text=True
    )
    for line in proc.stderr.splitlines():
        if "Duration:" in line:
            stamp = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = stamp.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return None
