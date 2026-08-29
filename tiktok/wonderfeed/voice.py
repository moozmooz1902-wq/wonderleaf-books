"""Optional voiceover via a fal TTS endpoint."""

from pathlib import Path

from . import falclient


def synthesise(text, settings, fal_key, workdir, log=print):
    """Return a path to an audio file, or None if voiceover is switched off."""
    cfg = settings.get("voiceover", {})
    if cfg.get("mode", "none") != "tts":
        return None
    out = Path(workdir) / "voice.mp3"
    log("  voiceover ...")
    try:
        result = falclient.run(
            cfg["tts_endpoint"],
            {"text": text, "voice": cfg.get("voice", "Rachel")},
            fal_key,
            timeout=180,
            log=log,
        )
        url = falclient._first_url(result, "audio", "audio_url", "audio_file")
        out.write_bytes(falclient.fetch(url))
        return out
    except Exception as exc:
        log(f"  voiceover failed ({exc}); shipping silent - add sound in the TikTok app")
        return None
