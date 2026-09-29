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

# Filled in once the bucket's public access is switched on. Cloudflare gives
# a URL of the form https://pub-<hash>.r2.dev - the hash is random, so it
# cannot be derived from the bucket name and has to be pasted in.
PUBLIC_BASE = os.environ.get("R2_PUBLIC_BASE", "").rstrip("/")


def image_url(sku):
    if not PUBLIC_BASE:
        return f"https://SET-R2_PUBLIC_BASE-FIRST/{sku}.jpg"
    return f"{PUBLIC_BASE}/{sku}.jpg"
