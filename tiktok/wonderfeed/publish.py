"""Delivery.

Two paths, and the difference matters:

* `save_local`  - writes the MP4 plus a caption sidecar. This is the path that
  works today and keeps the TikTok Shop product link, because you attach the
  product when you schedule the video in TikTok Studio.
* `upload_to_inbox` - pushes the MP4 into the TikTok app's drafts via the
  Content Posting API (`video.upload` scope). Still needs you to open the app
  to publish, but saves the file transfer.

Direct public posting (`video.publish`) is deliberately NOT implemented here:
until an app passes TikTok's audit it can only post SELF_ONLY, and even once
audited the API cannot attach a Shop product tag - which would cost you the
link that makes the video worth posting.
"""

import json
import re
from pathlib import Path

import requests

TOKEN_URL = "https://open.tiktokapis.com/v2/oauth/token/"
INBOX_INIT = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"


class PublishError(RuntimeError):
    pass


def caption_text(brief, product, settings):
    """Caption + hashtags + required AI disclosure, ready to paste."""
    parts = [brief["caption"].strip()]
    tags = " ".join(f"#{t}" for t in brief["hashtags"])
    if tags:
        parts.append(tags)
    if settings.get("posting", {}).get("ai_disclosure", True):
        raw = settings["posting"].get("ai_disclosure_text", "AI generated")
        tag = re.sub(r"[^A-Za-z0-9]", "", raw)  # TikTok hashtags are alphanumeric only
        if tag:
            parts.append(f"#{tag}")
    return "\n\n".join(parts)


def save_local(video_path, brief, product, settings, out_dir, stem):
    """Write the MP4 and a .txt with everything you need to post it."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    final_video = out_dir / f"{stem}.mp4"
    if Path(video_path).resolve() != final_video.resolve():
        final_video.write_bytes(Path(video_path).read_bytes())

    sidecar = out_dir / f"{stem}.txt"
    body = [
        "CAPTION (paste into TikTok)",
        "-" * 40,
        caption_text(brief, product, settings),
        "",
        "PRODUCT TO TAG",
        "-" * 40,
        f"{product['name']}  -  £{product.get('price_gbp', '?')}",
        product.get("link") or "(no link set in products.yaml)",
        "",
        "HOOK",
        "-" * 40,
        brief["hook"],
        "",
        "VOICEOVER SCRIPT (if you want to record it yourself)",
        "-" * 40,
        brief["voiceover"],
        "",
        "BEFORE YOU POST",
        "-" * 40,
        "1. Tag the product above (this is why we do not auto-post).",
        "2. Turn ON the 'AI-generated content' toggle under Post > More options.",
        "   The hashtag alone is not TikTok's required disclosure.",
        "3. Add a trending sound at low volume - reach is worse without one.",
    ]
    sidecar.write_text("\n".join(body), encoding="utf-8")

    (out_dir / f"{stem}.json").write_text(
        json.dumps({"product_id": product["id"], "brief": brief}, indent=2),
        encoding="utf-8",
    )
    return final_video, sidecar


# -- optional TikTok drafts upload ---------------------------------------


def refresh_access_token(client_key, client_secret, refresh_token):
    resp = requests.post(
        TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "client_key": client_key,
            "client_secret": client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        },
        timeout=30,
    )
    body = resp.json()
    if resp.status_code >= 400 or "access_token" not in body:
        raise PublishError(f"token refresh failed [{resp.status_code}]: {str(body)[:300]}")
    return body["access_token"], body.get("refresh_token", refresh_token)


def upload_to_inbox(video_path, access_token, log=print):
    """Send the MP4 to the creator's TikTok drafts. Returns publish_id."""
    path = Path(video_path)
    size = path.stat().st_size
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }
    init = requests.post(
        INBOX_INIT,
        headers=headers,
        json={
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": size,
                "chunk_size": size,
                "total_chunk_count": 1,
            }
        },
        timeout=60,
    )
    body = init.json()
    if init.status_code >= 400 or not body.get("data", {}).get("upload_url"):
        raise PublishError(f"inbox init failed [{init.status_code}]: {str(body)[:400]}")

    upload_url = body["data"]["upload_url"]
    publish_id = body["data"]["publish_id"]

    put = requests.put(
        upload_url,
        headers={
            "Content-Type": "video/mp4",
            "Content-Length": str(size),
            "Content-Range": f"bytes 0-{size - 1}/{size}",
        },
        data=path.read_bytes(),
        timeout=300,
    )
    if put.status_code >= 400:
        raise PublishError(f"upload failed [{put.status_code}]: {put.text[:300]}")
    log(f"  uploaded to TikTok drafts (publish_id {publish_id})")
    return publish_id


def check_status(publish_id, access_token):
    resp = requests.post(
        STATUS_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json; charset=UTF-8",
        },
        json={"publish_id": publish_id},
        timeout=30,
    )
    return resp.json()
