#!/usr/bin/env python3
"""Reject the two things that make generated art look generated: people, and
animal eyes that have gone wrong.

The seller's rule, 11 Oct 2026: no human figures at all, and no creature with
three eyes or a melted face. A listing with either is worse than no listing.

The method is CLIP zero-shot (openai/clip-vit-large-patch14, MIT licence,
so no commercial question). For each check the image is scored against a
bank of competing captions and the softmax mass that lands on the failure
captions is the score. That is more honest than a single caption, because
CLIP's absolute similarities mean nothing on their own - only the comparison
between captions carries information.

Thresholds are NOT guessed. calibrate() takes a labelled set, sweeps the
threshold, and reports precision and recall at each, so the number written
into the pipeline is one that was measured on real output.
"""
import json, sys
import numpy as np
from PIL import Image

MODEL = "openai/clip-vit-large-patch14"

HUMAN = {
    "fail": ["a person standing in the scene",
             "people walking, human figures",
             "a human face, a portrait of a man or woman",
             "a crowd of people"],
    "pass": ["an empty landscape with no people in it",
             "a deserted village with nobody in the street",
             "an animal on a plain background",
             "an abstract pattern with no figures",
             "a plant or flower study"],
}

EYES = {
    "fail": ["an animal with three eyes",
             "an animal with deformed melted eyes",
             "an animal face that is distorted and wrong",
             "an animal with mismatched uneven eyes",
             "a malformed animal with extra facial features"],
    "pass": ["an animal with two normal clear eyes",
             "a clean well drawn animal portrait",
             "a simple stylised animal illustration",
             "an animal seen from behind or in profile"],
}


def _unwrap(x):
    # transformers 5.x returns a BaseModelOutputWithPooling here, not a tensor
    return getattr(x, "pooler_output", x)


class Gate:
    def __init__(self, model=MODEL, device="cpu"):
        import torch
        from transformers import CLIPModel, CLIPProcessor
        self.torch = torch
        self.device = device
        self.m = CLIPModel.from_pretrained(model).to(device).eval()
        self.p = CLIPProcessor.from_pretrained(model)
        self.banks = {}
        for name, bank in (("human", HUMAN), ("eyes", EYES)):
            texts = bank["fail"] + bank["pass"]
            with torch.no_grad():
                t = self.p(text=texts, return_tensors="pt", padding=True).to(device)
                f = _unwrap(self.m.get_text_features(**t))
                f = f / f.norm(dim=-1, keepdim=True)
            self.banks[name] = (f, len(bank["fail"]))

    def scores(self, images):
        """Returns {check: array of failure probability}, one row per image."""
        torch = self.torch
        with torch.no_grad():
            i = self.p(images=images, return_tensors="pt").to(self.device)
            v = _unwrap(self.m.get_image_features(**i))
            v = v / v.norm(dim=-1, keepdim=True)
        out = {}
        for name, (f, nfail) in self.banks.items():
            logits = (100.0 * v @ f.T).softmax(dim=-1).cpu().numpy()
            out[name] = logits[:, :nfail].sum(axis=1)
        return out


def calibrate(scores, labels, name):
    """Sweep the threshold and print precision/recall, so the number chosen is
    a measurement and not a preference."""
    s, y = np.asarray(scores, float), np.asarray(labels, bool)
    print(f"\n{name}:  {y.sum()} bad of {len(y)}  "
          f"(bad mean {s[y].mean():.3f}, good mean {s[~y].mean():.3f})"
          if y.any() else f"\n{name}: no positives in the labelled set")
    if not y.any():
        return None
    print(f"   {'thresh':>7} {'caught':>7} {'recall':>7} {'false+':>7} {'prec':>6} {'loss%':>6}")
    best = None
    for t in np.quantile(s, np.linspace(0.50, 0.995, 20)):
        flag = s >= t
        tp, fp = int((flag & y).sum()), int((flag & ~y).sum())
        rec = tp / y.sum()
        prec = tp / max(tp + fp, 1)
        print(f"   {t:7.3f} {tp:7d} {rec:7.1%} {fp:7d} {prec:6.1%} {flag.mean():6.1%}")
        # recall first - a bad listing costs more than a wasted regeneration
        if rec >= 0.80 and (best is None or flag.mean() < best[1]):
            best = (float(t), float(flag.mean()), rec, prec)
    if best:
        print(f"   -> {best[0]:.3f}: catches {best[2]:.0%} of the bad ones, "
              f"regenerates {best[1]:.0%} of everything")
    return best


if __name__ == "__main__":
    import glob, os
    files = sorted(glob.glob(sys.argv[1] + "/*.jpg"))
    g = Gate()
    out = {}
    B = 8
    for i in range(0, len(files), B):
        chunk = files[i:i + B]
        imgs = [Image.open(f).convert("RGB") for f in chunk]
        s = g.scores(imgs)
        for j, f in enumerate(chunk):
            out[os.path.basename(f)] = {k: float(v[j]) for k, v in s.items()}
        print(f"  {min(i+B, len(files))}/{len(files)}", flush=True)
    json.dump(out, open(sys.argv[2], "w"), indent=1)
    print(f"wrote {sys.argv[2]}")
