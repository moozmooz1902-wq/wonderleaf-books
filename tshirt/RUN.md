# Run order on the pod

    pip install boto3 pillow
    gunzip -f REPLICA_V5.csv.gz
    python3 render_all.py                 # ~20 min on 16 cores
    export R2_ACCOUNT_ID=...
    export R2_ACCESS_KEY_ID=...
    export R2_SECRET_ACCESS_KEY=...
    export R2_BUCKET=tshirt-m12k
    python3 r2_upload.py designs/
    python3 ebay_file.py                  # writes EBAY_UPLOAD.csv

Both the render and the upload are resumable: rerun either and it picks up
where it stopped.
