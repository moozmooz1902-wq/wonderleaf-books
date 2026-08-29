"""Thin fal.ai queue client - submit, poll, fetch bytes.

Kept generic so the model endpoints stay configurable in settings.yaml;
fal changes model slugs regularly.
"""

import base64
import io
import time

import requests

QUEUE = "https://queue.fal.run"


class FalError(RuntimeError):
    pass


def data_url_from_bytes(image_bytes, max_side=1536, quality=90):
    """Base64 data URL, so we never touch fal's separate storage API."""
    from PIL import Image

    img = Image.open(io.BytesIO(image_bytes))
    if max(img.size) > max_side:
        img.thumbnail((max_side, max_side), Image.LANCZOS)
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = bg
    else:
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def run(endpoint, payload, fal_key, timeout=300, poll=2.0, log=print):
    """Submit to the fal queue and block until the result is ready."""
    headers = {"Authorization": f"Key {fal_key}", "Content-Type": "application/json"}
    submit = requests.post(f"{QUEUE}/{endpoint}", headers=headers, json=payload, timeout=60)
    if submit.status_code >= 400:
        raise FalError(f"{endpoint} submit failed [{submit.status_code}]: {submit.text[:300]}")
    req_id = submit.json().get("request_id")
    if not req_id:
        raise FalError(f"{endpoint} returned no request_id: {submit.text[:200]}")

    base = f"{QUEUE}/{endpoint}/requests/{req_id}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(poll)
        s = requests.get(f"{base}/status", headers=headers, timeout=30)
        if s.status_code >= 400:
            raise FalError(f"{endpoint} status failed [{s.status_code}]: {s.text[:200]}")
        status = s.json().get("status")
        if status == "COMPLETED":
            break
        if status in ("FAILED", "ERROR"):
            raise FalError(f"{endpoint} reported {status}: {s.text[:300]}")
    else:
        raise FalError(f"{endpoint} timed out after {timeout}s")

    result = requests.get(base, headers=headers, timeout=60)
    if result.status_code >= 400:
        raise FalError(f"{endpoint} result failed [{result.status_code}]: {result.text[:300]}")
    return result.json()


def _first_url(result, *keys):
    for key in keys:
        node = result.get(key)
        if isinstance(node, dict) and node.get("url"):
            return node["url"]
        if isinstance(node, list) and node and isinstance(node[0], dict) and node[0].get("url"):
            return node[0]["url"]
    raise FalError(f"no media url in result keys {list(result)[:8]}")


def fetch(url, timeout=180):
    resp = requests.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.content


def image(endpoint, prompt, reference_url, fal_key, aspect="9:16", log=print):
    """Image edit/generate keeping the reference product consistent."""
    result = run(
        endpoint,
        {
            "prompt": prompt,
            "image_url": reference_url,
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
            "output_format": "jpeg",
            "aspect_ratio": aspect,
        },
        fal_key,
        timeout=180,
        log=log,
    )
    return fetch(_first_url(result, "images", "image"))


def video(endpoint, prompt, image_url, fal_key, duration=5, log=print):
    """Image-to-video."""
    result = run(
        endpoint,
        {
            "prompt": prompt,
            "image_url": image_url,
            "duration": str(int(duration)),
            "aspect_ratio": "9:16",
        },
        fal_key,
        timeout=600,
        log=log,
    )
    return fetch(_first_url(result, "video", "videos"))
