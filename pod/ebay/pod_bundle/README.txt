WONDERLEAF T-SHIRT RENDER BUNDLE
================================

Produces TWO files per design, matching the existing fulfilment flow:

    print/<design_id>.png    4500x5400 transparent   -> your printer
    mock/<design_id>.jpg     2000x2000               -> the eBay image

CPU ONLY. No GPU. No model. No image API. These are typography on black.

CONTENTS
    catalogue.json        50,740 designs  (core - recommended)
    catalogue_full.json   91,869 designs  (adds occasion crossing)
    run.py                the renderer
    sync_r2.sh            uploads to R2 and frees local disk
    photo_mockup.py       your mockup script, with the fabric warp limited to
                          the print window (verified identical output)
    blank.png             your black tee blank
    fonts/                6 SIL Open Font Licence display faces

DISK
    ~1.55 MB per design (876KB print + 678KB mock)
    50,740 designs  =  ~79 GB
    91,869 designs  =  ~142 GB
    Run sync_r2.sh alongside and you only need ~20 GB at any moment.

TIME (measured at 3.28s of CPU per design)
    16 cores:  50,740 -> 2.9 h     91,869 -> 5.2 h
    32 cores:  50,740 -> 1.4 h     91,869 -> 2.6 h
    64 cores:  50,740 -> 0.7 h     91,869 -> 1.3 h

RESUMABLE. Anything already on disk is skipped, so re-running after a
disconnect picks up where it stopped.
