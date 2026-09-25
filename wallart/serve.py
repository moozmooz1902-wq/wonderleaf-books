#!/usr/bin/env python3
"""On-demand image server - no image is ever stored.

Every catalogue row carries an img_path like
    /r/sage/classic_serif/stack/cup/QnV0IGZpcnN0LCAvICpjb2ZmZWUq.jpg
which encodes the whole design. Point the listing's picture URL at this server
and it draws the picture when asked. eBay copies each picture to its own
servers once when the listing is created, so each image is rendered roughly
once, ever. Seven million listings need no disk space and no image hosting.

    python3 serve.py --port 8080

    /r/<design>.jpg            flat artwork, 1600px wide (listing photo 2)
    /m/<design>.jpg            print on a wall, 1600x1600 (main listing photo)
    /p/A4/<design>.png         print file at 300dpi (A5, A4, A3, A2)

Put a CDN (e.g. Cloudflare, free tier) in front and cache /r and /m for a year.
Rendering takes ~20-60 ms per image on one CPU core.
"""
import argparse, base64, io, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from render import render, mockup
from styles import PALETTES, FONTSETS, LAYOUTS

MM = {"A5": 148, "A4": 210, "A3": 297, "A2": 420}      # paper widths in mm
PATH = re.compile(r"^/(r|m|p/(A[2-5]))/([a-z]+)/([a-z_]+)/([a-z]+)/([a-z0-9]+)/([A-Za-z0-9_-]+)\.(jpg|png)$")


def decode(b):
    return base64.urlsafe_b64decode(b + "=" * (-len(b) % 4)).decode()


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        m = PATH.match(self.path.split("?")[0])
        if not m:
            return self.send_error(404)
        kind, size, pal, fonts, layout, orn, b64, ext = m.groups()
        if pal not in PALETTES or fonts not in FONTSETS or layout not in LAYOUTS:
            return self.send_error(404)
        try:
            phrase = decode(b64)
        except Exception:
            return self.send_error(400)
        buf = io.BytesIO()
        if kind == "r":
            render(phrase, pal, fonts, layout, orn, 1600).save(buf, "JPEG", quality=90)
        elif kind == "m":
            mockup(render(phrase, pal, fonts, layout, orn, 1200), 1600).save(buf, "JPEG", quality=90)
        else:
            px = round(MM[size] / 25.4 * 300)
            render(phrase, pal, fonts, layout, orn, px).save(buf, "PNG", dpi=(300, 300))
        body = buf.getvalue()
        self.send_response(200)
        self.send_header("Content-Type", "image/png" if ext == "png" else "image/jpeg")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=31536000, immutable")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    a = ap.parse_args()
    print(f"serving on :{a.port}")
    ThreadingHTTPServer(("", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
