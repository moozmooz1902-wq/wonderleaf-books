"""Which bucket this catalogue goes to.

Each eBay account has its own R2 bucket, so this is the one thing to change
when the same pipeline runs for a different store.

    account : M12K
    bucket  : tshirt-m12k

Credentials never live in this file. They are read from the environment on
the pod, so they stay on the seller's machine.
"""
import os

ACCOUNT = "M12K"
BUCKET  = os.environ.get("R2_BUCKET", "tshirt-m12k")

# Public r2.dev hostname for tshirt-m12k. The hash is assigned by Cloudflare
# and is not derivable from the bucket name, so it is recorded here.
PUBLIC_BASE = os.environ.get(
    "R2_PUBLIC_BASE",
    "https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev").rstrip("/")


def image_url(sku):
    if not PUBLIC_BASE:
        return f"https://SET-R2_PUBLIC_BASE-FIRST/{sku}.jpg"
    return f"{PUBLIC_BASE}/{sku}.jpg"
