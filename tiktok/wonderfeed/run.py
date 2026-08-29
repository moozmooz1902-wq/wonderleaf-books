"""Orchestrator. Build a batch of ready-to-schedule TikTok videos.

  python -m wonderfeed.run --count 7
  python -m wonderfeed.run --dry-run          # no API calls, no spend
  python -m wonderfeed.run --product botanical-3set --count 2
"""

import argparse
import random
import shutil
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path

from . import brief as brief_mod
from . import publish, render, visuals, voice
from .config import ConfigError, ROOT, load_products, load_settings, resolve_path, secret
from .state import State

DRY_BRIEF = {
    "hook": "That wall has been bare since you moved in.",
    "beats": [
        {"onscreen_text": "Bare wall since you moved in",
         "scene": "An empty magnolia wall above a beige linen sofa, morning light.",
         "motion": "slow push in"},
        {"onscreen_text": "Three prints. Ten minutes.",
         "scene": "The same wall with a trio of botanical line-art prints hung evenly.",
         "motion": "tilt up the wall"},
        {"onscreen_text": "Looks like you hired someone",
         "scene": "Wide styled living room, the trio centred above the sofa.",
         "motion": "slow pull back"},
    ],
    "voiceover": "This wall did nothing for two years. Three prints later it "
                 "looks like someone was paid to style it.",
    "caption": "The cheapest way to make a rented flat look finished.",
    "hashtags": ["homedecor", "rentersfriendly", "gallerywall", "ukhome", "wallart"],
}


def pick_jobs(products, state, settings, count, only_product=None, rng=random):
    """Choose (product, angle, room) triples, avoiding recently used pairs."""
    cooldown = settings["posting"]["angle_cooldown_days"]
    recent = state.recent_pairs(cooldown)
    pool = [p for p in products if not only_product or p["id"] == only_product]
    if not pool:
        raise ConfigError(f"No product matches id '{only_product}'")

    fresh, stale = [], []
    for p in pool:
        for angle in p["angles"]:
            (stale if (p["id"], angle) in recent else fresh).append((p, angle))
    rng.shuffle(fresh)
    rng.shuffle(stale)
    chosen = (fresh + stale)[:count]
    if len(chosen) < count:
        print(f"  note: only {len(chosen)} product/angle combos exist; "
              f"add more angles to products.yaml to post more per run")

    jobs = []
    for p, angle in chosen:
        rooms = p.get("rooms") or ["a tidy modern living room"]
        jobs.append({"product": p, "angle": angle, "room": rng.choice(rooms)})
    return jobs


def build_one(job, settings, state, keys, out_dir, dry_run, log=print):
    product, angle, room = job["product"], job["angle"], job["room"]
    log(f"* {product['name']} - angle: {angle}")

    workdir = Path(tempfile.mkdtemp(prefix="wonderfeed-"))
    try:
        # 1. script
        if dry_run:
            b = dict(DRY_BRIEF)
            log("  brief: (dry run, canned)")
        else:
            b = brief_mod.write_brief(
                product, angle, room, settings, keys["anthropic"],
                used_hooks=state.used_hooks(), log=log,
            )
        log(f"  hook: {b['hook']}")

        # 2. stills
        if dry_run:
            stills = [visuals.placeholder_still(i, workdir / f"still{i}.jpg", settings)
                      for i in range(3)]
        else:
            image_rel = (product.get("images") or [None])[0]
            if not image_rel:
                raise ConfigError(f"Product {product['id']} has no images")
            image_bytes = resolve_path(image_rel).read_bytes()
            seed_text = f"{product['id']}:{angle}:{room}"
            stills = visuals.build_stills(b, image_bytes, settings, keys["fal"],
                                          workdir, seed_text=seed_text, log=log)

        # 3. motion (optional)
        clips = [None, None, None]
        if settings["models"].get("use_motion") and not dry_run:
            clips = visuals.build_clips(b, stills, settings, keys["fal"], workdir, log=log)

        # 4. voiceover (optional)
        audio = None if dry_run else voice.synthesise(b["voiceover"], settings,
                                                      keys["fal"], workdir, log=log)

        # 5. render
        beat_seconds = settings["video"]["beat_seconds"]
        segments = []
        for i, beat in enumerate(b["beats"]):
            overlay = render.text_overlay_png(beat["onscreen_text"], settings,
                                              workdir / f"ov{i}.png")
            seg = workdir / f"seg{i}.mp4"
            if clips[i]:
                render.clip_to_segment(clips[i], overlay, beat_seconds[i], seg, settings)
            else:
                render.still_to_segment(stills[i], overlay, beat_seconds[i], seg,
                                        settings, zoom_in=(i % 2 == 0))
            segments.append(seg)
        final = render.concat(segments, workdir / "final.mp4", settings, audio=audio)

        # 6. deliver
        stem = f"{datetime.now(timezone.utc):%Y%m%d}-{state.next_index():03d}-{product['id']}"
        video_path, sidecar = publish.save_local(final, b, product, settings, out_dir, stem)
        log(f"  -> {video_path.name}  ({video_path.stat().st_size // 1024} KB, "
            f"{render.probe_duration(video_path):.1f}s)")

        state.record_video({
            "stem": stem, "product_id": product["id"], "angle": angle,
            "room": room, "hook": b["hook"], "caption": b["caption"],
            "dry_run": dry_run,
        })
        return {"ok": True, "stem": stem, "path": str(video_path)}
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build a batch of TikTok videos.")
    ap.add_argument("--count", type=int, default=None, help="how many videos")
    ap.add_argument("--product", help="restrict to one product id")
    ap.add_argument("--dry-run", action="store_true",
                    help="no API calls, placeholder visuals - proves the pipeline")
    ap.add_argument("--seed", type=int, help="deterministic job selection")
    ap.add_argument("--out", help="override output directory")
    args = ap.parse_args(argv)

    try:
        settings = load_settings()
        products = load_products()
    except ConfigError as exc:
        print(f"Config error: {exc}", file=sys.stderr)
        return 2

    keys = {"anthropic": "", "fal": ""}
    if not args.dry_run:
        try:
            keys["anthropic"] = secret("ANTHROPIC_API_KEY")
            keys["fal"] = secret("FAL_KEY")
        except ConfigError as exc:
            print(f"Config error: {exc}", file=sys.stderr)
            return 2

    count = args.count or settings["posting"]["per_run"]
    out_dir = Path(args.out) if args.out else resolve_path(settings["output"]["dir"])
    state = State()
    rng = random.Random(args.seed) if args.seed is not None else random

    print(f"Building {count} video(s) -> {out_dir}"
          f"{'  [DRY RUN]' if args.dry_run else ''}")
    jobs = pick_jobs(products, state, settings, count, args.product, rng)

    results = []
    for job in jobs:
        try:
            results.append(build_one(job, settings, state, keys, out_dir,
                                     args.dry_run))
        except Exception as exc:
            print(f"  FAILED: {exc}")
            traceback.print_exc(limit=2)
            results.append({"ok": False, "error": str(exc),
                            "product_id": job["product"]["id"]})
        state.save()

    ok = sum(1 for r in results if r.get("ok"))
    state.record_run({"requested": count, "built": ok, "dry_run": args.dry_run})
    state.save()
    print(f"\nDone: {ok}/{len(results)} built in {out_dir}")
    if ok:
        print("Next: open TikTok Studio, upload these, tag the product, "
              "schedule one per day.")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
