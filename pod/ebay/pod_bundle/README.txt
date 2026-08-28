WONDERLEAF T-SHIRT RENDER BUNDLE
================================

Two files per design, matching the existing fulfilment flow:

    print/<design_id>.png    4500x5400 transparent   -> your printer
    mock/<design_id>.jpg     2000x2000               -> the eBay image

CPU ONLY. No GPU, no model, no image API. These are typography on black.


QUICK START (32 vCPU pod)
-------------------------
    cd /workspace
    tar xzf tshirt_pod_bundle.tar.gz
    cd pod_bundle
    pip install Pillow numpy scipy

    python3 run.py --workers 4 --limit 40        # smoke test - LOOK at mock/
    python3 run.py --workers 32                  # the real run


DISK
----
Two ways to handle it:

  A) --upload  (recommended, works on a 5GB pod)
     Each file goes to R2 and is deleted locally the moment it is written, so
     peak disk stays near zero.

         rclone config create r2 s3
         rclone config update r2 provider Other
         rclone config update r2 access_key_id KEY
         rclone config update r2 secret_access_key SECRET
         rclone config update r2 endpoint https://ACCOUNT_ID.r2.cloudflarestorage.com
         rclone config update r2 no_check_bucket true

         python3 run.py --workers 32 --upload r2:YOUR-BUCKET/art

     Writes to art/raw/ and art/mock/ - the paths print_tool.py already reads.

  B) Keep everything local
     Raise Container disk in the pod template overrides:
         50,740 designs -> 75 GB      91,869 designs -> 136 GB
     Then run sync_r2.sh in a second terminal to upload afterwards.

Either way, 20-30 GB of container disk is a sensible cushion. It costs
$0.001/GB/hr - about 3p an hour for 30 GB.


TIME  (measured: 3.28s of CPU per design)
-----
    16 cores:  50,740 -> 2.9 h     91,869 -> 5.2 h
    32 cores:  50,740 -> 1.4 h     91,869 -> 2.6 h
    64 cores:  50,740 -> 0.7 h     91,869 -> 1.3 h

At $1.28/hr for 32 vCPU that is about $1.80 for the core catalogue.

RESUMABLE. Anything already on disk (or already uploaded) is skipped, so
re-running after a disconnect picks up where it stopped.


CONTENTS
--------
    catalogue.json        50,740 designs  (core - recommended)
    catalogue_full.json   91,869 designs  (adds occasion crossing)
    run.py                the renderer
    sync_r2.sh            batch upload, for option B
    photo_mockup.py       your mockup script, warp limited to the print window
                          (verified: max pixel difference 7 of 255 vs original)
    blank.png             your black tee blank
    fonts/                6 SIL Open Font Licence display faces
