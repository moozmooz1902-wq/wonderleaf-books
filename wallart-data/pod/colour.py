#!/usr/bin/env python3
"""Measured colour and composition features for one image.

Deliberately numpy, not a model: palette, lightness, saturation, contrast and
edge density are exactly measurable, and a caption would only describe them
less precisely. The model is saved for what it is actually better at - style
and subject - in embed.py.
"""
import numpy as np
from PIL import Image

SMALL = 96          # everything below is computed at this size


def feats(im: Image.Image) -> dict:
    im = im.convert("RGB")
    w0, h0 = im.size
    a = np.asarray(im.resize((SMALL, SMALL), Image.BILINEAR), dtype=np.float32) / 255.0

    mx = a.max(axis=2); mn = a.min(axis=2)
    val = mx
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    lum = 0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]

    # hue, only where the pixel is colourful enough for hue to mean anything
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    d = mx - mn
    hue = np.zeros_like(mx)
    m = d > 1e-6
    rm = m & (mx == r); gm = m & (mx == g) & ~rm; bm = m & ~rm & ~gm
    hue[rm] = ((g - b)[rm] / d[rm]) % 6
    hue[gm] = ((b - r)[gm] / d[gm]) + 2
    hue[bm] = ((r - g)[bm] / d[bm]) + 4
    hue = hue * 60.0
    strong = (sat > 0.18) & (val > 0.12)

    # a 12-bin hue histogram over the colourful pixels is the "colour scheme"
    if strong.sum() > 20:
        hh, _ = np.histogram(hue[strong], bins=12, range=(0, 360))
        hh = (hh / hh.sum()).astype(np.float32)
    else:
        hh = np.zeros(12, dtype=np.float32)

    # palette: k-means, 5 centres, on the colourful-or-not pixels alike
    flat = a.reshape(-1, 3)
    idx = np.random.default_rng(0).choice(flat.shape[0], size=min(1500, flat.shape[0]), replace=False)
    pts = flat[idx]
    cent = pts[np.random.default_rng(1).choice(pts.shape[0], size=5, replace=False)].copy()
    for _ in range(8):
        dist = ((pts[:, None, :] - cent[None, :, :]) ** 2).sum(axis=2)
        lab = dist.argmin(axis=1)
        for k in range(5):
            if (lab == k).any():
                cent[k] = pts[lab == k].mean(axis=0)
    share = np.bincount(lab, minlength=5).astype(np.float32); share /= share.sum()
    order = np.argsort(-share)
    pal = [[int(round(c * 255)) for c in cent[k]] for k in order]
    palshare = [float(share[k]) for k in order]

    # edge density: how much line and detail there is, the "flat vs busy" axis
    gy, gx = np.gradient(lum)
    edge = np.sqrt(gx * gx + gy * gy)

    # border vs centre lightness: white-background print or full-bleed panel
    bw = 10
    border = np.concatenate([lum[:bw, :].ravel(), lum[-bw:, :].ravel(),
                             lum[:, :bw].ravel(), lum[:, -bw:].ravel()])
    centre = lum[SMALL // 4:3 * SMALL // 4, SMALL // 4:3 * SMALL // 4]

    return {
        "wh": [w0, h0],
        "ratio": round(w0 / h0, 4),
        "lum": round(float(lum.mean()), 4),
        "lum_sd": round(float(lum.std()), 4),
        "sat": round(float(sat.mean()), 4),
        "sat_sd": round(float(sat.std()), 4),
        "colourful": round(float(strong.mean()), 4),
        "edge": round(float(edge.mean()), 5),
        "edge_p95": round(float(np.percentile(edge, 95)), 5),
        "contrast": round(float(lum.max() - lum.min()), 4),
        "border_lum": round(float(border.mean()), 4),
        "centre_lum": round(float(centre.mean()), 4),
        "border_sd": round(float(border.std()), 4),
        "hue12": [round(float(x), 4) for x in hh],
        "pal": pal,
        "pal_share": [round(x, 4) for x in palshare],
    }
