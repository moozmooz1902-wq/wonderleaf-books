#!/usr/bin/env python3
"""Production worker: generate, read the output, and reject what has writing on it.

Five of the first sixteen panels came back with lettering or a fake artist's
signature - "W ITBEY" across a harbour, "N2Z1" on a seafront, a monogram in
the corner of a linocut. guidance_scale is 0 for schnell, so negative prompts
are inert and there is no prompt wording that fixes it. The only thing that
works is looking at the result.

EasyOCR runs on the same GPU in about 50 ms, against roughly 2,000 ms for a
generation, so the gate costs about 2.5% and saves a listing that would have
gone up with a garbled word printed across it.

A rejected job is retried with a different seed, up to --retries times. The
rejection rate is reported at the end, because that number is what the
catalogue budget is built on.

Resumable: every finished SKU is appended to done.txt.
"""
import argparse, hashlib, json, os, sys, time, zlib

# A detection has to be reasonably confident AND reasonably large before it
# counts. FLUX leaves faint marks everywhere that OCR will happily read as a
# letter; rejecting on those throws away good work.
MIN_CONF = 0.35
MIN_AREA = 0.0012          # share of the panel
MIN_CHARS = 2


def text_marks(reader, img, keep=1.0):
    """Read the WHOLE panel, then ignore what the crop is about to remove.

    This is read on the uncropped generation, not on the cropped panel, and
    the difference is not academic. A screenprint of Antigua Guatemala went
    into a store bucket with GUATEMALA across the foot in inch-high caps.
    The gate had run after the crop, so all it saw was the top two
    millimetres of a row of letters - mutilated shapes that OCR will not
    read confidently - while the full letters sat just below the cut. Text
    that STRADDLES the crop line was invisible to a gate that only ever saw
    one side of it.

    So: detect on the full image, where the letters are whole, and then
    reject only the marks that reach into the part being kept. A signature
    lying entirely in the discarded tenth is still not a rejection, which is
    the whole reason the crop exists.
    """
    import numpy as np
    a = np.asarray(img.convert("RGB"))
    H, W = a.shape[:2]
    cut = H * keep
    out = []
    for box, txt, conf in reader.readtext(a):
        t = "".join(c for c in txt if c.isalnum())
        if len(t) < MIN_CHARS or conf < MIN_CONF:
            continue
        xs = [p[0] for p in box]; ys = [p[1] for p in box]
        # Judge what SURVIVES the crop, not what was generated. Reading the
        # whole panel is right - a title straddling the cut is unreadable on
        # the cropped copy - but rejecting on the mark's full size was an
        # over-correction: a signature sitting at 88-96% of the height keeps
        # only a two-percent sliver after the bottom tenth goes, and that
        # sliver is not what anyone will see. So the box is clipped to the
        # kept area and MIN_AREA is applied to what is left of it.
        top, bot = min(ys), min(max(ys), cut)
        if bot <= top:                # wholly inside the discarded strip
            continue
        area = (max(xs) - min(xs)) * (bot - top) / (W * cut)
        if area >= MIN_AREA:
            # y is where the mark sits, as a fraction of the KEPT height.
            # Without it a rejection record says what was read but not
            # where, and "is this a title across the picture or speckle in
            # the bottom corner" is the whole question.
            out.append((txt, round(float(conf), 2), round(area, 4),
                        round(top / cut, 2)))
    return out


# Compositions that are MEANT to be sparse. "Small and centred on a vast
# expanse of plain paper" is the whole brief for G8_minimal, so it cannot be
# held to the same floor as a meadow.
MINIMAL_GRAMS = {"G8_minimal", "B1_specimen", "C2_disc", "S2_single", "B5_single"}
# RECALIBRATED 12 Oct, against the panels the first floor threw away.
#
# The first numbers, 0.10 and 0.18, were fitted to a 141-panel eval whose
# median busyness was 52% - and that sample was nearly all old-grid
# material. The work the fleet has LEFT is heavily the new kinds and the
# flat techniques, which are legitimately flatter: screenprint's own median
# is 28.9%. So the floor started rejecting 46% of generations, and three
# shards came up at 100%.
#
# 80 of the rejected panels were regenerated with every gate off and looked
# at (wallart-samples/17_called_empty.jpg). The bottom of that range is
# genuinely failed - two dots on a blue field, a red smear, an unreadable
# blob, all under 0.045. Everything from about 0.05 up is the minimal
# poster the catalogue is partly MADE of: a pelican, a barred owl, a
# collared dove, a quarter moon, a watering can, each small and centred on
# a plain ground. Those sell. Throwing them away was the bug.
#
# Busyness cannot tell a tiny RECOGNISABLE subject from a tiny smear - that
# is beyond what a contrast measure can see - so the floor is set where it
# only catches the near-blank, and "small but legible" is allowed through.
# At these numbers 4 of those 80 stay rejected, and they are the right 4.
BUSY_FLOOR = {"minimal": 0.035, "other": 0.055}


def busyness(img):
    """What share of the sheet carries a mark.

    Not ink coverage: a dark ground is not emptiness. This is local contrast -
    the share of 16x16 tiles whose range is more than 12 levels - so a flat
    field of any colour reads as empty and a speckled one does not.

    Measured over the 141-panel eval of 11 Oct: median 52%, and the four
    panels under 15% were the four nobody would buy - a red hot poker alone
    on a blank sheet at 9%, a star cluster at 11%. Screenprint and the
    neutral palette sit lowest by technique and palette, which is the pair
    that produces an empty sheet with one small object on it.
    """
    import numpy as np
    a = np.asarray(img.convert("L").resize((256, 384)), dtype=np.int16)
    t = a.reshape(24, 16, 16, 16).swapaxes(1, 2).reshape(-1, 256)
    return float(((t.max(1) - t.min(1)) > 12).mean())


# Measured on 6,000 random panels from the live buckets, 12 Oct 2026.
#
# PEOPLE, all kinds. Of the eight highest-scoring panels six held real human
# figures - a cyanotype whose white silhouettes came out as little people, a
# street full of them, a row of silhouettes along the foot of a seaweed
# scatter. 0.85 is the 98th percentile and flags about 2.3%. Recall is
# worth more than precision here: a regenerated panel costs $0.0003 and a
# listing with a person in it breaks the seller's rule outright.
#
# EYES, creature panels ONLY. Run over everything this check is noise - of
# the 48 highest scores in the first scan, exactly one was an animal, and it
# was really measuring how faceted the brushwork was. On creatures it works:
# at 0.85 it flags about 2% of them, and what it flags is mostly invertebrates
# that FLUX gave a face to.
QUALITY_HUMAN = 0.85
QUALITY_EYES = 0.85


def backup_meta(s3, bucket, a):
    """Copy the run's metadata to R2 beside the panels.

    Every panel goes to R2 the moment it is made and is then deleted from the
    container disk, so the ARTWORK already survives any pod loss. The
    metadata did not: manifest.jsonl says which SKU is which subject,
    technique, composition, palette and seed, and it lived only on that disk.

    Most of it is recomputable - a SKU is a hash of the job, so re-expanding
    the grid recovers everything except the seed and the OCR marks - but
    "most of it is recomputable" is not a backup, and a pod that vanishes
    should not cost anything that cannot be bought back for a fraction of a
    penny. A failure here is reported and never stops the run; losing the
    backup is not a reason to stop making panels.
    """
    if s3 is None or not bucket:
        return
    tag = f"{(a.part or 'all').replace('/', 'of')}-{os.environ.get('RUNPOD_POD_ID', 'nopod')}"
    for fn in ("manifest.jsonl", "done.txt", "rejects.jsonl"):
        fp = os.path.join(a.out, fn)
        if not os.path.exists(fp):
            continue
        try:
            with open(fp, "rb") as fh:
                s3.put_object(Bucket=bucket, Key=f"wallart/manifests/{tag}-{fn}",
                              Body=fh.read(), ContentType="text/plain")
        except Exception as e:
            print(f"  manifest backup failed: {e}", flush=True)


def sku_for(job, prefix="WA"):
    """A SKU derived from WHAT the job is, never from where it sits in a list.

    This is what makes the run resumable. The first version numbered jobs by
    position after a seeded shuffle, which is reproducible only while the
    subject list never changes - add one flower and every SKU after it moves,
    so everything already generated looks unfinished and gets made again.
    Hashing the job content instead means a SKU is the same for ever, lists
    can be extended at any time, and "what is already done" is simply "what
    is already in the bucket".

    CRC32 IS NOT WIDE ENOUGH. It collided on the very first run of 12,834
    jobs - 2^32 means a collision is likely past about 65,000, and 937,500
    jobs would collide roughly a hundred thousand times, each one silently
    dropping a design. 64 bits puts that at effectively never.
    """
    key = "|".join(str(job[k]) for k in ("kind", "subject", "tech", "gram", "pal"))
    return f"{prefix}-{hashlib.blake2b(key.encode(), digest_size=8).hexdigest()}"


# Measured on the finished 12,834-panel block: 1.5% of designs have a near
# twin from a DIFFERENT design, and every one of the closest pairs is a
# minimal composition - a red fox and a whippet, cow parsley and a curlew,
# a kingfisher and a barn owl. Different subjects, but "small and centred on
# a vast expanse of plain paper" looks the same at thumbnail size whatever
# is in the middle, which is exactly how a buyer sees an eBay search grid.
# The hash is not being fooled; it is reporting something true.
#
# So these compositions are capped. They sell, and they are cheap to make,
# but at an equal share of the grid they would be a sixth of five million
# listings all looking alike. The cap is applied by SKU hash, so which ones
# survive is deterministic and a resumed run makes the same choices.
# C2_disc joined these on 11 Oct. The audit found every near-twin in the
# first block was a minimal composition - a small subject on an empty
# sheet - and "one large disc centred on a plain flat ground" is that
# same picture for all 155 celestial subjects: a circle. Capped like the
# other two rather than dropped, because the composition does sell.
# G10_abstract joined on 12 Oct. Even reworded to build the abstraction
# FROM the place, an all-over field with no focal point is the
# composition least able to tell one subject from another, and it was
# 8 of the 28 panels in the audit's closest-pair list.
THIN_GRAMMARS = {"G8_minimal": 0.35, "B1_specimen": 0.45, "C2_disc": 0.30,
                 "G10_abstract": 0.50}


def _thin(jobs):
    kept = []
    for j in jobs:
        keep = THIN_GRAMMARS.get(j["gram"])
        if keep is None:
            kept.append(j); continue
        h = int(hashlib.blake2b(j["sku"].encode(), digest_size=4).hexdigest(), 16)
        if (h % 1000) / 1000.0 < keep:
            kept.append(j)
    return kept


def expand(subjects, thin=True):
    """Build the full grid from the subject lists, exactly as the planner does,
    so a pod and this machine always agree on which SKU is which job."""
    import itertools, random, prompts as P
    jobs = []
    for s_, t, g, c in itertools.product(subjects.get("place", []),
                                         P.TECHNIQUE, P.GRAMMAR_PLACE, P.PALETTE):
        if P.ok(t, g, s_, c):
            jobs.append(dict(kind="place", subject=s_, tech=t, gram=g, pal=c,
                             prompt=P.place_prompt(s_, t, g, c)))
    for s_, t, g, c in itertools.product(subjects.get("creature", []),
                                         P.TECHNIQUE, P.GRAMMAR_CREATURE, P.PALETTE):
        if P.ok(t, g, s_, c):
            jobs.append(dict(kind="creature", subject=s_, tech=t, gram=g, pal=c,
                             prompt=P.creature_prompt(s_, t, g, c)))
    for s_, t, g, c in itertools.product(subjects.get("botanical", []),
                                         P.TECHNIQUE, P.GRAMMAR_BOTANICAL, P.PALETTE):
        if P.ok(t, g, s_, c):
            jobs.append(dict(kind="botanical", subject=s_, tech=t, gram=g, pal=c,
                             prompt=P.botanical_prompt(s_, t, g, c)))
    # The three kinds added 11 Oct 2026. Each carries its own grammars, which
    # is the point: more compositions that are genuinely different beats more
    # subjects the model renders the same way.
    for kind, grams, fn in (("celestial", P.GRAMMAR_CELESTIAL, P.celestial_prompt),
                            ("stilllife", P.GRAMMAR_STILLLIFE, P.stilllife_prompt),
                            ("architecture", P.GRAMMAR_ARCH, P.architecture_prompt)):
        for s_, t, g, c in itertools.product(subjects.get(kind, []),
                                             P.TECHNIQUE, grams, P.PALETTE):
            if P.ok(t, g, s_, c):
                jobs.append(dict(kind=kind, subject=s_, tech=t, gram=g, pal=c,
                                 prompt=fn(s_, t, g, c)))
    # The copyright gate, enforced here rather than reported somewhere else.
    # A blocked subject must never reach a prompt, let alone a listing.
    try:
        # the bundle unpacks flat, so ip_check.py lands beside this file
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import ip_check
        bad = ip_check.check_subjects(subjects)
        if bad:
            raise SystemExit(f"IP BLOCKLIST: refusing to generate {bad}")
        print(f"ip gate: {len(jobs):,} jobs, no blocked subject", flush=True)
    except ImportError:
        print("ip gate: ip_check.py not shipped to this pod - REFUSING", flush=True)
        raise SystemExit(2)

    pre = subjects.get("prefix", "WA")
    for j in jobs:
        j["sku"] = sku_for(j, pre)
    # ordered by the SKU hash: a stable pseudo-random shuffle, so any prefix
    # of the work is a fair mix of subjects, and adding subjects later
    # interleaves them instead of renumbering anything
    jobs.sort(key=lambda j: j["sku"])
    if thin:
        before = len(jobs)
        jobs = _thin(jobs)
        print(f"minimal-composition cap: {before - len(jobs):,} of {before:,} dropped",
              flush=True)
    seen = {}
    for j in jobs:                       # a collision would silently drop work
        seen.setdefault(j["sku"], []).append(j)
    dup = {k: v for k, v in seen.items() if len(v) > 1}
    if dup:
        raise SystemExit(f"SKU collision on {len(dup)} jobs: {list(dup)[:3]}")
    return jobs


def main():
    ap = argparse.ArgumentParser()
    # --jobs ships a job file; --subjects ships the subject lists and the pod
    # expands the grid itself. 12,834 jobs is several MB of base64 inside the
    # pod's start command and `curl` refuses it with "Argument list too long",
    # so anything past a few hundred jobs goes by --subjects.
    ap.add_argument("--jobs", default="")
    ap.add_argument("--subjects", default="")
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--steps", type=int, default=4)
    ap.add_argument("--width", type=int, default=704)
    ap.add_argument("--height", type=int, default=1008)
    ap.add_argument("--retries", type=int, default=2)
    # A multiplier on BUSY_FLOOR, so 0 turns the emptiness gate off and 1.0
    # uses the measured floors. It costs about 5% more generations.
    ap.add_argument("--min-busy", type=float, default=1.0)
    # The people and eyes gate. CLIP ViT-L/14 is about 1.7 GB and will not
    # fit beside the NF4 transformer on a 16 GB card, so it runs on CPU
    # while the GPU makes the next batch. Thresholds were measured, not
    # chosen: see QUALITY_* below.
    ap.add_argument("--clip-gate", type=int, default=1)
    # Generate taller than needed and throw the bottom away. Measured on 129
    # panels: 96% of the fake signatures and stray marks sit below 90% of the
    # panel height, so a 10% crop removes almost all of them for the cost of
    # generating 11% more pixels. Trying to paint them out instead was tried
    # first and only half worked - see declutter.py.
    ap.add_argument("--crop-bottom", type=float, default=0.10)
    ap.add_argument("--tag", default="")
    ap.add_argument("--quant", default="nf4", choices=["none", "nf4"])
    ap.add_argument("--model", default="lzyvegetable/FLUX.1-schnell")
    ap.add_argument("--no-gate", action="store_true")
    # Upload each kept panel straight to R2 from the pod. The keys arrive as
    # environment variables from RunPod template vbsgwyibn1, so they live on
    # the pod and never in this repo or in a Claude session. Probed 11 Oct:
    # the token can WRITE to tshirt-m12k but cannot list or create buckets,
    # so until the seller makes a wall-art bucket this writes under a prefix.
    ap.add_argument("--r2-prefix", default="")
    # Route every panel to the bucket of the store that owns it, instead of
    # dumping the whole run in one place. allocate.py decides, by SKU hash,
    # and a design lands in exactly one store - four shops selling the same
    # picture compete with each other.
    ap.add_argument("--stores", default="")
    # Shard one job file across N pods: each takes every Nth job. Striping
    # rather than slicing so every pod gets the same mix of subjects and
    # techniques, and so the rate each one reports is comparable.
    # The grid is bigger than the catalogue on purpose. 5,204 subjects expand
    # to 1,195,035 base images, which is 4.78 million listings at four
    # colourways - about 20% more than the 5,000,000 target once the
    # 1,250,000 code-drawn listings are counted. --pool takes the first N of
    # the SKU-sorted grid, which is a fair mix of every kind, technique,
    # grammar and palette because that sort is a stable pseudo-random
    # shuffle. The rest of the grid is spare capacity: raising --pool later
    # adds listings without regenerating anything, because a SKU is a hash
    # of what the job IS and never of where it sits.
    ap.add_argument("--pool", type=int, default=0)
    ap.add_argument("--part", default="")      # "k/n", 1-based
    ap.add_argument("--resume", action="store_true")
    # Stop cleanly after this long, so a pod cannot quietly run all night if
    # something downstream is wedged. Work already uploaded is kept.
    ap.add_argument("--max-hours", type=float, default=0.0)
    # ONE SHARD AT A TIME. Moves the no-text clause back to the end of the
    # prompt, outside CLIP's 77-token window, which is where it lived before
    # 12 Oct. The point is to find out whether having it inside the window
    # suppresses text or produces it: this file's own first paragraph says
    # negative prompts are inert at guidance_scale 0, and the people
    # experiment on 13 Oct showed a negation moved into the attended part of
    # the prompt made the thing it named MORE common. Text is about half of
    # all rejections, so the answer is worth a shard.
    ap.add_argument("--clean-at-end", action="store_true")
    a = ap.parse_args()
    # Before anything builds a prompt. prompts.py is imported inside expand(),
    # so the flag has to be pushed into the module there, not here - this
    # import is the same module object either way.
    if a.clean_at_end:
        import prompts as _PP
        _PP.CLEAN_AT_END = True
        print("PROMPT VARIANT: _CLEAN at the end, outside CLIP's window", flush=True)
    os.makedirs(a.out, exist_ok=True)
    donep = os.path.join(a.out, "done.txt")
    done = {l.strip() for l in open(donep)} if os.path.exists(donep) else set()
    a.crop_bottom = max(0.0, min(0.25, a.crop_bottom))

    if a.subjects:
        jobs = expand(json.load(open(a.subjects)))
        json.dump(jobs, open(os.path.join(a.out, "jobs.json"), "w"))
    else:
        jobs = json.load(open(a.jobs))
    # --pool is applied BEFORE done.txt and before striping, so every shard
    # agrees on the same pool whatever each one has already finished.
    if a.pool:
        before = len(jobs)
        jobs = jobs[:a.pool]
        print(f"pool: {len(jobs):,} of {before:,} grid jobs", flush=True)
    jobs = [j for j in jobs if j["sku"] not in done]
    if a.part:
        k, nparts = (int(x) for x in a.part.split("/"))
        jobs = jobs[k - 1::nparts]
        print(f"part {k} of {nparts}", flush=True)
    if a.limit:
        jobs = jobs[:a.limit]
    gen_h = int(round(a.height / (1 - a.crop_bottom) / 16)) * 16
    print(f"generating {a.width}x{gen_h}, cropping the bottom "
          f"{a.crop_bottom:.0%} down to {a.width}x{a.height}", flush=True)
    print(f"{len(jobs):,} to generate at {a.width}x{a.height} "
          f"quant={a.quant} gate={'off' if a.no_gate else 'on'}", flush=True)

    import torch
    from diffusers import FluxPipeline
    kw = {"torch_dtype": torch.bfloat16}
    if a.quant == "nf4":
        from diffusers.quantizers import PipelineQuantizationConfig
        kw["quantization_config"] = PipelineQuantizationConfig(
            quant_backend="bitsandbytes_4bit",
            quant_kwargs={"load_in_4bit": True, "bnb_4bit_quant_type": "nf4",
                          "bnb_4bit_compute_dtype": torch.bfloat16},
            components_to_quantize=["transformer", "text_encoder_2"])
    pipe = FluxPipeline.from_pretrained(a.model, **kw)
    free = torch.cuda.mem_get_info()[0] / 2**30
    print(f"free vram {free:.0f} GB", flush=True)
    pipe.to("cuda") if (a.quant == "nf4" or free >= 40) else pipe.enable_model_cpu_offload()

    gate = None
    if a.clip_gate:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import quality_gate
            t_gate = time.time()
            gate = quality_gate.Gate(device="cpu")
            print(f"people/eyes gate ready on cpu in {time.time()-t_gate:.0f}s",
                  flush=True)
        except Exception as e:
            print(f"people/eyes gate UNAVAILABLE: {e}", flush=True)

    route = None
    if a.stores:
        import allocate
        route = allocate.store_for
        print("routing by store: " + ", ".join(
            f"{x['bucket']}={x['listings']:,}" for x in allocate.PLAN["stores"]), flush=True)

    s3 = bucket = mani_bucket = None
    if a.r2_prefix or a.stores:
        import boto3
        from botocore.config import Config
        bucket = os.environ.get("R2_BUCKET", "")
        s3 = boto3.client(
            "s3", endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
            aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
            config=Config(signature_version="s3v4", max_pool_connections=32),
            region_name="auto")
        # Some community hosts sit behind a TLS-intercepting middlebox and
        # every R2 call dies with "certificate verify failed: self-signed
        # certificate". Verification is NOT disabled - that would hand the
        # bucket's traffic to whatever is doing the intercepting. The pod
        # says so and stops, the same way it does for a dead CUDA runtime,
        # so it is relaunched elsewhere instead of billing while failing.
        try:
            s3.list_objects_v2(Bucket=(allocate.PLAN["stores"][0]["bucket"]
                                       if route else bucket), MaxKeys=1)
        except Exception as e:
            if "CERTIFICATE_VERIFY_FAILED" in str(e) or "SSLError" in type(e).__name__:
                print("R2_TLS_INTERCEPTED_ON_THIS_HOST", flush=True)
                raise SystemExit(3)
            raise
        mani_bucket = (allocate.PLAN["stores"][0]["bucket"] if route else bucket)
        if not route:
            print(f"uploading to s3://{bucket}/{a.r2_prefix.strip('/')}/", flush=True)
        # THE RESUME. done.txt lives on container disk and dies with the pod,
        # so the bucket is the only durable record of what has been made. If
        # the balance runs out mid-run, the pods stop, and the next pod picks
        # up exactly here.
        if a.resume:
            if route:
                import allocate
                targets = [(x["bucket"], x["key_prefix"].strip("/") + "/")
                           for x in allocate.PLAN["stores"]]
            else:
                targets = [(bucket, a.r2_prefix.strip("/") + "/")]
            n = 0
            for bkt, pre in targets:
                tok = None
                while True:
                    kw = {"Bucket": bkt, "Prefix": pre, "MaxKeys": 1000}
                    if tok:
                        kw["ContinuationToken"] = tok
                    r = s3.list_objects_v2(**kw)
                    for o in r.get("Contents", []):
                        k = o["Key"].rsplit("/", 1)[-1]
                        if k.endswith(".jpg"):
                            done.add(k[:-4]); n += 1
                    if not r.get("IsTruncated"):
                        break
                    tok = r["NextContinuationToken"]
            print(f"resume: {n:,} panels already across {len(targets)} bucket(s)",
                  flush=True)
            jobs = [j for j in jobs if j["sku"] not in done]

    reader = None
    if not a.no_gate:
        import easyocr
        reader = easyocr.Reader(["en"], gpu=True, verbose=False)
        print("ocr gate ready", flush=True)

    t0 = time.time()
    kept = rejected = gens = 0
    df = open(donep, "a")
    mf = open(os.path.join(a.out, "manifest.jsonl"), "a", encoding="utf-8")
    rf = open(os.path.join(a.out, "rejects.jsonl"), "a", encoding="utf-8")
    batches = 0

    queue = list(jobs)
    attempt = {j["sku"]: 0 for j in jobs}
    while queue:
        chunk, queue = queue[:a.batch], queue[a.batch:]
        gens_seed = [zlib.crc32(f"{j['sku']}#{attempt[j['sku']]}".encode()) % 2**31
                     for j in chunk]
        imgs = pipe(prompt=[j["prompt"] for j in chunk],
                    num_inference_steps=a.steps, guidance_scale=0.0,
                    width=a.width, height=gen_h, max_sequence_length=256,
                    generator=[torch.Generator("cpu").manual_seed(s) for s in gens_seed]
                    ).images
        gens += len(chunk)
        # The OCR gate reads the FULL generation; only the saved copy is
        # cropped. See text_marks(): a title straddling the crop line is
        # unreadable on the cropped panel and obvious on the whole one.
        full = imgs
        if a.crop_bottom > 0:
            imgs = [im.crop((0, 0, im.width, int(im.height * (1 - a.crop_bottom))))
                    for im in imgs]
        # The text gate first, on every panel in the batch.
        all_marks = [text_marks(reader, w, keep=1 - a.crop_bottom) if reader else []
                     for w in full]
        # Then people, and eyes on creatures that have a face - in ONE call
        # for the whole batch. Scoring the four panels one at a time cost
        # 12.5% of throughput on an A4500; CLIP on CPU at this size is
        # mostly per-call overhead, so the batch is close to free by
        # comparison. Only panels the text gate has not already rejected
        # are scored. A failure here is reported and keeps the batch -
        # losing the gate is not a reason to stop making panels.
        if gate is not None:
            need = [i for i, m in enumerate(all_marks) if not m]
            if need:
                try:
                    import prompts as _P
                    sc = gate.scores([imgs[i] for i in need])
                    for pos, i in enumerate(need):
                        jj = chunk[i]
                        h = float(sc["human"][pos])
                        if h >= QUALITY_HUMAN:
                            all_marks[i] = [["PEOPLE", round(h, 3), QUALITY_HUMAN]]
                        elif (jj.get("kind") == "creature"
                              and _P.has_face(jj.get("subject", ""))):
                            e = float(sc["eyes"][pos])
                            if e >= QUALITY_EYES:
                                all_marks[i] = [["EYES", round(e, 3), QUALITY_EYES]]
                except Exception as e:
                    print(f"  gate error, batch kept: {e}", flush=True)
        for (j, im, sd, whole, marks) in zip(chunk, imgs, gens_seed, full, all_marks):
            # An almost-empty sheet is not a cheap minimal composition, it is
            # a failed generation, and it is the one defect the OCR gate
            # cannot see. Same treatment: retry on a different seed.
            if not marks and a.min_busy:
                floor = (BUSY_FLOOR["minimal"] if j.get("gram") in MINIMAL_GRAMS
                         else BUSY_FLOOR["other"]) * a.min_busy
                b = busyness(im)
                if b < floor:
                    marks = [["EMPTY", round(b, 3), round(floor, 3)]]
            if marks and attempt[j["sku"]] < a.retries:
                attempt[j["sku"]] += 1
                # RETRY AT THE FRONT, NOT THE BACK.
                #
                # queue.append put a rejected job behind ~70,000 others, so a
                # pod never reached it again before --max-hours stopped it.
                # The job therefore never used its second and third attempts
                # and was never kept-anyway; it stayed "not done", and the
                # NEXT pod picked it up first, failed it once more, and threw
                # it to the back again. Hard jobs accumulated at the head of
                # every relaunch and were re-attempted for ever.
                #
                # Measured on the 13 Oct rotation: three fresh shards spent
                # their first few hundred generations on this backlog at
                # 31-57% rejection, and the rejections then nearly stopped -
                # 316 of 343 on the first shard happened before its 700th
                # panel. Retrying in place spends the retries while the pod
                # still has them and settles the job either way.
                queue.insert(0, j)
                rejected += 1
                rf.write(json.dumps({"sku": j["sku"], "try": attempt[j["sku"]],
                                     "marks": marks}) + "\n")
                continue
            if marks:
                rejected += 1
                rf.write(json.dumps({"sku": j["sku"], "try": "final", "kept_anyway": True,
                                     "marks": marks}) + "\n")
            path = os.path.join(a.out, j["sku"] + a.tag + ".jpg")
            im.save(path, "JPEG", quality=92)
            if s3 is not None:
                if route:
                    st = route(j["sku"])
                    bkt = st["bucket"]
                    key = f"{st['key_prefix'].strip('/')}/{j['sku']}{a.tag}.jpg"
                else:
                    bkt = bucket
                    key = f"{a.r2_prefix.strip('/')}/{j['sku']}{a.tag}.jpg"
                with open(path, "rb") as fh:
                    s3.put_object(Bucket=bkt, Key=key, Body=fh.read(),
                                  ContentType="image/jpeg")
                os.remove(path)        # the pod disk will not hold a million
            df.write(j["sku"] + "\n")
            mf.write(json.dumps({**j, "seed": sd, "marks": marks},
                                 ensure_ascii=False) + "\n")
            kept += 1
        df.flush(); mf.flush(); rf.flush()
        # THE MANIFEST IS NOT SAFE ON THE POD. Every panel goes to R2 the
        # moment it is made and is then deleted from the container disk, so
        # the artwork survives any pod loss - but manifest.jsonl, which says
        # which SKU is which subject, technique, composition, palette and
        # seed, lived only on that disk and died with it. Most of it is
        # recomputable, because a SKU is a hash of the job and re-expanding
        # the grid recovers everything but the seed and the OCR marks. "Most
        # of it" is not a backup. It goes to R2 too, every 25 batches, and a
        # pod that is lost now costs at most 25 batches of metadata.
        batches += 1
        if batches % 25 == 0:
            backup_meta(s3, mani_bucket, a)
        el = time.time() - t0
        print(f"  kept {kept:,} / {gens:,} generated  {gens/el:.2f} img/s  "
              f"reject {rejected/max(gens,1):.0%}  {el/60:.1f} min", flush=True)
        if a.max_hours and el > a.max_hours * 3600:
            print(f"STOPPING: hit --max-hours {a.max_hours}", flush=True)
            break

    el = time.time() - t0
    # Say plainly whether the shard was FINISHED or merely stopped. The first
    # run hit --max-hours on one shard, abandoned 245 jobs and still printed
    # GEN_DONE, so the block looked complete when it was 98.1% complete. An
    # unfinished shard must be loud, because the only other way to notice is
    # to count the bucket and subtract.
    backup_meta(s3, mani_bucket, a)          # always, finished or not
    left = len(queue)
    if left:
        print(f"UNFINISHED: {left:,} jobs left in this shard - "
              f"re-run with --resume to finish them", flush=True)
    else:
        print("SHARD COMPLETE", flush=True)
    print(f"DONE kept {kept:,} from {gens:,} generations in {el/60:.1f} min", flush=True)
    print(f"RATE: {3600*gens/el:,.0f} generations/hour", flush=True)
    print(f"REJECT_RATE: {rejected/max(gens,1):.4f}", flush=True)


if __name__ == "__main__":
    main()
