#!/usr/bin/env python3
"""A one-job upload relay: accept a file over HTTP, put it in R2.

WHY THIS EXISTS. The upload files are built in the session container, which
has no R2 credentials - they live on the RunPod template and nowhere else,
which is the rule that keeps them out of the repo and out of chat. The
obvious alternative was to build the files ON a pod, but the builder needs
the job grid, and the grid needs subjects.json plus prompts.py: 54 KB
compressed, 73 KB as base64, against a start-command limit somewhere
between 60 and 70 thousand characters. Measured, not guessed.

So the data goes the other way. This is about two kilobytes, fits with
room to spare, and the files travel container -> pod -> R2 without the
credentials ever moving.

  PUT /up/<token>/<bucket>/<key...>   body is the file
  GET /health                          -> "ok"

The token is generated per run and passed in the start command. The pod's
proxy URL is only semi-private - anyone holding the pod id can reach port
8000 - so without it this would be an open door into the seller's bucket.
It is also why the pod is deleted the moment the transfer is done.
"""
import os, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import boto3
from botocore.config import Config

TOKEN = os.environ.get("RELAY_TOKEN", "")
ALLOW = tuple(x for x in os.environ.get("RELAY_PREFIXES", "ebay/").split(",") if x)

s3 = boto3.client(
    "s3",
    endpoint_url=f"https://{os.environ['R2_ACCOUNT_ID']}.r2.cloudflarestorage.com",
    aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
    aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
    config=Config(signature_version="s3v4", max_pool_connections=16,
                  retries={"max_attempts": 10, "mode": "adaptive"}),
    region_name="auto")

TYPES = {".zip": "application/zip", ".csv": "text/csv",
         ".gz": "application/gzip", ".txt": "text/plain"}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        sys.stderr.write("%s - %s\n" % (self.address_string(), a[0] % a[1:]))

    def do_GET(self):
        ok = self.path == "/health"
        self.send_response(200 if ok else 404)
        self.end_headers()
        self.wfile.write(b"ok" if ok else b"no")

    def do_PUT(self):
        try:
            _, up, tok, bucket, *rest = self.path.split("/")
            key = "/".join(rest)
        except ValueError:
            return self.fail(400, "bad path")
        if up != "up" or not TOKEN or tok != TOKEN:
            return self.fail(403, "bad token")
        # A relay that will write anywhere is a relay that can overwrite the
        # catalogue. Only the agreed prefixes.
        if not key.startswith(ALLOW):
            return self.fail(403, "prefix not allowed")
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        ext = os.path.splitext(key)[1]
        try:
            s3.put_object(Bucket=bucket, Key=key, Body=body,
                          ContentType=TYPES.get(ext, "application/octet-stream"))
        except Exception as e:
            return self.fail(500, str(e)[:200])
        self.send_response(200)
        self.end_headers()
        self.wfile.write(f"{bucket}/{key} {n}".encode())
        print(f"PUT {bucket}/{key} {n:,} bytes", flush=True)

    def fail(self, code, msg):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(msg.encode())


if __name__ == "__main__":
    print(f"relay up, prefixes {ALLOW}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", 8001), H).serve_forever()
