#!/usr/bin/env python3
"""Which community cards EXIST by name, and which have a free instance now.

The REST API has no gputypes endpoint, so the only honest way to ask is to
attempt a create and read the answer. Three answers are possible and they
mean different things:

    a pod object        the name is valid AND an instance was free. Deleted
                        immediately - it exists for about a second.
    500 "no instances"  the name is valid, nothing free right now
    a bare LIST         the name is NOT a gpuTypeId at all, and the whole
                        request was rejected on schema. This is the one that
                        quietly idled five shards: one bad name in the list
                        kills the request for every good name beside it.

Anything created here is deleted in a finally block, so a crash cannot leave
a pod billing.
"""
import json, subprocess, sys

API = "https://rest.runpod.io/v1"
# 16 GB is the floor: the NF4 transformer peaks at 16.1 GB.
CARDS = [
 "NVIDIA RTX A4000", "NVIDIA RTX A4500", "NVIDIA RTX A5000", "NVIDIA RTX A6000",
 "NVIDIA GeForce RTX 3090", "NVIDIA GeForce RTX 3090 Ti",
 "NVIDIA GeForce RTX 4080", "NVIDIA GeForce RTX 4080 SUPER",
 "NVIDIA GeForce RTX 4090", "NVIDIA GeForce RTX 5080", "NVIDIA GeForce RTX 5090",
 "NVIDIA RTX 2000 Ada Generation", "NVIDIA RTX 4000 Ada Generation",
 "NVIDIA RTX 4000 SFF Ada Generation", "NVIDIA RTX 5000 Ada Generation",
 "NVIDIA RTX 6000 Ada Generation", "NVIDIA L4", "NVIDIA L40", "NVIDIA L40S",
 "NVIDIA A30", "NVIDIA A40", "NVIDIA A100 80GB PCIe",
]


def post(card, cloud):
    body = {"name": "probe-card", "imageName": "runpod/base:0.7.0-ubuntu2404",
            "gpuTypeIds": [card], "gpuCount": 1, "cloudType": cloud,
            "containerDiskInGb": 80, "volumeInGb": 0}
    out = subprocess.run(["curl", "-sS", "--max-time", "60", "-X", "POST",
                          f"{API}/pods", "-H", "Content-Type: application/json",
                          "-d", json.dumps(body)], capture_output=True, text=True).stdout
    try:
        return json.loads(out)
    except Exception:
        return {"error": out[:120]}


def kill(pid):
    subprocess.run(["curl", "-sS", "--max-time", "60", "-X", "DELETE",
                    f"{API}/pods/{pid}"], capture_output=True, text=True)


if __name__ == "__main__":
    cloud = sys.argv[1] if len(sys.argv) > 1 else "COMMUNITY"
    print(f"{cloud}\n{'card':<36}{'$/hr':>7}  verdict")
    for c in CARDS:
        r = post(c, cloud)
        pid = r.get("id") if isinstance(r, dict) else None
        try:
            if pid:
                print(f"{c:<36}{r.get('costPerHr', 0):>7.2f}  FREE NOW")
            elif not isinstance(r, dict):
                print(f"{c:<36}{'-':>7}  NOT A GPU TYPE ID")
            else:
                e = str(r.get("error", ""))
                print(f"{c:<36}{'-':>7}  {'none free' if 'no instance' in e or 'no longer' in e else e[:60]}")
        finally:
            if pid:
                kill(pid)
