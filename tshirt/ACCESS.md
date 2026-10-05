# Access and infrastructure

What a new session needs to know to run this without asking the seller to
set anything up again. Read this before telling them to open a terminal.

## RunPod - WORKING, no setup needed

The API key is stored as an environment credential on the Claude
environment ("poster and t shirt data research"), named `RUNPOD_API_KEY`,
type Bearer, allowed host `rest.runpod.io`.

It is injected by the egress proxy, NOT exposed as a shell variable. So:

- `echo $RUNPOD_API_KEY` prints nothing. That is expected, not a fault.
- `curl https://rest.runpod.io/v1/pods` is already authenticated. Just call it.
- It works in the session it was added to - no need to start a new one.
- **Python's urllib gets 403 through the proxy; curl gets 200.** Fetch with
  curl, parse with Python.

Verified 2026-10-03: `GET /v1/pods` -> HTTP 200.

Useful endpoints (full spec at `GET /v1/openapi.json`):

    GET  /v1/pods                 list
    POST /v1/pods                 create (takes env, templateId, dockerStartCmd,
                                  computeType=CPU, cpuFlavorIds, vcpuCount,
                                  containerDiskInGb, cloudType=COMMUNITY|SECURE)
    POST /v1/pods/{id}/stop       stop (keeps the pod, disk persists if volume)
    DEL  /v1/pods/{id}            delete
    GET  /v1/billing/pods         spend

There is **no secrets endpoint**. Credentials reach a pod either through
`env` on pod creation or through a template's env.

## Cloudflare R2 - NOT connected

Bucket `tshirt-m12k`, account M12K.
Public base `https://pub-4b710c8610a84acc8fad1513f48132fd.r2.dev`
(public access is on; a GET of the root returns 404, which is correct for
an empty bucket).

**Do not try to add R2 through the "Create an account for Claude"
credential form.** That form injects a fixed header. R2's storage API signs
every request with a value computed from the secret, so a static
`Authorization: Bearer ...` cannot authenticate however the host is set.
This has already cost several rounds; do not retry it.

Two routes that do work:

1. **RunPod template (preferred).** The seller creates a template in the
   RunPod UI carrying `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID` and
   `R2_SECRET_ACCESS_KEY` as env vars. Pods are created with that
   `templateId`, so the pod holds the keys and Claude never does.
2. Plain environment variables on the Claude environment under those same
   three names, if an environment-variables section is offered separately
   from the credential form.

Nothing about rendering depends on R2. Only the upload step does.

## Pods seen on the account (2026-10-03)

    v4f4gjeot7i9t0  cpu3g  16 vCPU / 64 GB  50 GB disk  $0.64/hr  EXITED
    hzrsupgjqzlfrg  GPU    36 vCPU / 143 GB 30 GB disk  $0.74/hr  EXITED
    h9bfk4b8x0w4bw  GPU    12 vCPU / 31 GB  30 GB disk  $0.74/hr  EXITED

All three have **volume 0 GB**, so `/workspace` is container disk and is
wiped on stop. Anything uploaded to an earlier pod is gone. Create pods
with a volume if work needs to survive a stop.

The CPU pod ran 11 minutes before the seller stopped it, so the "it takes
forever" complaint is RunPod provisioning time, not the render.

## Costs, measured not estimated

    render      12.3 designs/sec/core, 79 KB per JPEG
                118,360 designs = 2.7 core-hours, 9.5 GB
    cpu3g       $0.64/hr (NOT the $0.20-0.40 quoted earlier - that was wrong)
    whole job   well under an hour, so roughly £0.50

A GPU is needed only for the illustrated 62%: ~10,000 images for 2,517
subjects, ~3h on a 4090, ~$2.50. Not started.

## Boundaries the seller agreed

- Claude starts, runs and stops pods without asking.
- Claude does **not** make payments or top up the card. Report the balance
  and let them do it.
- Anything irreversible or outward-facing - deleting a pod with unsaved
  work, pushing live eBay listings - gets confirmed first.

## Still blocked on the seller

- **Price.** `ebay_file.py` has 9.99 as a placeholder. The export has no
  price column, so it cannot be derived from any data held.
- Confirm eBay category 15687 matches their existing listings.
- Whether listings need S-XXL variations (current file is single-SKU).
