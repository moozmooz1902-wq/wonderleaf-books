"""
Wonderleaf Books — Web Version (Streamlit)
==========================================

Free web hosting via Streamlit Community Cloud.

DEPLOYMENT (one time, ~20 min):

1. Create a GitHub account: https://github.com (free, 2 min)

2. Create a new repository:
   - Click "+" top right → "New repository"
   - Name: wonderleaf-books
   - Set to Public (Streamlit's free tier needs public repos)
   - Click "Create repository"

3. Upload files to the repo:
   - Click "uploading an existing file"
   - Drag in: wonderleaf_web.py, requirements.txt
   - Scroll down, click "Commit changes"

4. Deploy on Streamlit Cloud:
   - Go to https://share.streamlit.io
   - Sign in with GitHub
   - Click "Create app" → pick your wonderleaf-books repo
   - Main file: wonderleaf_web.py
   - Click "Deploy"
   - Wait ~2 min for deploy

5. Add API keys as secrets (Streamlit encrypts them):
   - Click the three dots on your app → "Settings" → "Secrets"
   - Paste this format (replace with your keys):

       ANTHROPIC_API_KEY = "sk-ant-..."
       FAL_KEY = "fal_..."
       APP_PASSWORD = "wonderleaf2026"

       # Optional - unlocks the eBay Research tools.
       # Free keys from https://developer.ebay.com/my/keys
       EBAY_CLIENT_ID = "YourApp-PRD-..."
       EBAY_CLIENT_SECRET = "PRD-..."
       EBAY_MARKETPLACE = "EBAY_GB"

   - Click "Save"
   - App auto-restarts with keys loaded

6. Done! You now have a URL like https://wonderleaf-books.streamlit.app
   Bookmark it. That's the app forever.
"""

import streamlit as st
import json
import time
import base64
import io
import mimetypes
from pathlib import Path
import tempfile


# ==========================================================================
# CONFIG - Keys and password from Streamlit secrets (production)
# or user input (local dev)
# ==========================================================================

def get_secret(key, default=""):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


ANTHROPIC_KEY = get_secret("ANTHROPIC_API_KEY")
FAL_KEY = get_secret("FAL_KEY")
APP_PASSWORD = get_secret("APP_PASSWORD")


def _slugify(text):
    """Turn a book title into a safe filename slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)  # remove punctuation
    text = re.sub(r"[\s_-]+", "-", text)   # spaces to hyphens
    text = text.strip("-")
    return text[:60] or "book"


# ==========================================================================
# PASSWORD GATE (simple, prevents random people using your API credits)
# ==========================================================================

def check_password():
    """Simple password gate. If APP_PASSWORD isn't set, skips gate."""
    if not APP_PASSWORD:
        return True
    if st.session_state.get("password_ok"):
        return True

    st.title("🌙 Wonderleaf Books")
    with st.form("login"):
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Enter"):
            if pwd == APP_PASSWORD:
                st.session_state["password_ok"] = True
                st.rerun()
            else:
                st.error("Wrong password")
    st.stop()


# ==========================================================================
# STORY GENERATION (Claude)
# ==========================================================================

STORY_PROMPT = """You are a professional children's picture book author writing for Wonderleaf Books, a British publisher of gentle picture books for ages 3-7.

Write a complete 20-page picture book based on these two inputs:

- Title: {title}
- Story brief: {brief}

First identify the MAIN CHARACTER from the title and brief. For example:
- Title "Sweet Dreams, Little Unicorn" → character "Little Unicorn"
- Title "Fox's First Christmas" → character "Fox"
- Title "When Little Girl Started School" → character "Little Girl"

WRITING RULES:
- British English throughout (colour, mum, cosy, dreamt, favourite)
- Ages 3-7 vocabulary: simple, warm, gentle
- Each story page: 2-4 short sentences maximum
- Story arc: gentle setup -> gentle journey/discovery -> warm resolution
- Never scary. Never conflict beyond soft, relatable feelings.
- Warm, comforting ending

For pages 3-18 (16 pages), also give a SCENE description for the illustration.
The scene should:
- Show a DIFFERENT moment from the story text on that page
- Feature the main character doing something specific
- Include setting/environment details
- Be a single visual moment

OUTPUT FORMAT (return ONLY valid JSON, no preamble):

{{
  "character": "the main character name you identified",
  "dedication": "one warm dedication line for page 2",
  "closing": "warm closing sentences for page 19",
  "pages": [
    {{"page": 3, "text": "...", "scene": "..."}},
    ... 16 total pages (3 through 18) ...
  ]
}}"""


def generate_story(title, brief, api_key, status):
    import anthropic
    status.write("Writing story with Claude...")
    client = anthropic.Anthropic(api_key=api_key)
    resp = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=4000,
        messages=[{"role": "user", "content": STORY_PROMPT.format(
            title=title, brief=brief
        )}],
    )
    text = resp.content[0].text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
        text = text.strip()
    story = json.loads(text)
    if "pages" not in story or len(story["pages"]) != 16:
        raise ValueError(f"Expected 16 pages, got {len(story.get('pages', []))}")
    character = story.get("character", "the main character")
    status.write(f"Story written. Character: {character}. ({len(story['pages'])} pages)")
    return story


# ==========================================================================
# IMAGE GENERATION (fal.ai Flux Kontext via data URL)
# ==========================================================================

def make_data_url_from_bytes(image_bytes):
    """Turn image bytes into a base64 data URL (avoids fal storage API)."""
    from PIL import Image
    img = Image.open(io.BytesIO(image_bytes))
    if max(img.size) > 1536:
        img.thumbnail((1536, 1536), Image.LANCZOS)
    if img.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        bg.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = bg
    else:
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return f"data:image/jpeg;base64,{base64.b64encode(buf.getvalue()).decode('ascii')}"


def flux_kontext_generate(prompt, reference_url, fal_key, timeout=90):
    import requests
    submit = requests.post(
        "https://queue.fal.run/fal-ai/flux-pro/kontext",
        headers={"Authorization": f"Key {fal_key}",
                 "Content-Type": "application/json"},
        json={
            "prompt": prompt,
            "image_url": reference_url,
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
            "output_format": "png",
        },
        timeout=60,
    )
    submit.raise_for_status()
    req_id = submit.json()["request_id"]
    status_url = f"https://queue.fal.run/fal-ai/flux-pro/kontext/requests/{req_id}/status"
    result_url = f"https://queue.fal.run/fal-ai/flux-pro/kontext/requests/{req_id}"

    for _ in range(timeout):
        time.sleep(1)
        s = requests.get(status_url, headers={"Authorization": f"Key {fal_key}"}, timeout=30)
        if s.json().get("status") == "COMPLETED":
            break
    else:
        raise TimeoutError(f"Generation timed out after {timeout}s")

    result = requests.get(result_url, headers={"Authorization": f"Key {fal_key}"}, timeout=30)
    result.raise_for_status()
    image_url = result.json()["images"][0]["url"]
    png = requests.get(image_url, timeout=60).content
    return png


def generate_illustrations(story, character, cover_bytes, style, fal_key, progress_bar, status):
    status.write("Encoding cover as character reference...")
    reference_url = make_data_url_from_bytes(cover_bytes)

    if style == "color":
        style_tail = (
            f"Same {character} character from the reference image, same colours and features. "
            "Full-colour digital illustration, Disney/Pixar 3D animation style, "
            "vibrant, warm lighting, cinematic, gentle and safe for children, "
            "professional children's book illustration. White or soft background."
        )
    else:
        style_tail = (
            f"Same {character} character from the reference image, same features and proportions. "
            "Black and white pencil sketch illustration, classic children's picture book style, "
            "clean black outlines with soft crosshatch shading, hand-drawn warmth, "
            "Quentin Blake style, gentle and safe for children. White background, no colour."
        )

    illustrations = {}
    total = len(story["pages"])

    for i, entry in enumerate(story["pages"]):
        page_num = entry["page"]
        scene = entry["scene"]
        prompt = f"{scene}. {style_tail}"
        status.write(f"Illustration {i+1}/{total}: page {page_num}...")
        t0 = time.time()
        try:
            png = flux_kontext_generate(prompt, reference_url, fal_key)
            illustrations[page_num] = png
            status.write(f"Illustration {i+1}/{total}: done ({time.time()-t0:.1f}s)")
        except Exception as e:
            status.write(f"Illustration {i+1}/{total}: FAILED ({e})")
        # Progress bar: 10% - 90% during illustrations
        progress_bar.progress(0.1 + (i + 1) / total * 0.8)

    return illustrations


# ==========================================================================
# PDF ASSEMBLY
# ==========================================================================

def build_pdf(title, story, cover_bytes, illustrations, status):
    from PIL import Image, ImageDraw, ImageFont

    status.write("Building PDF...")
    DPI = 300
    A4_W, A4_H = 2480, 3508
    MARGIN = int(15 * DPI / 25.4)
    CONTENT_W = A4_W - 2 * MARGIN
    CONTENT_H = A4_H - 2 * MARGIN

    # Streamlit Cloud font paths - Linux Debian
    def fnt(size, style="reg"):
        candidates = {
            "reg": [
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
                "/System/Library/Fonts/Georgia.ttf",
                "C:/Windows/Fonts/georgia.ttf",
            ],
            "bold": [
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
                "/System/Library/Fonts/Georgia Bold.ttf",
                "C:/Windows/Fonts/georgiab.ttf",
            ],
            "ital": [
                "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
                "/System/Library/Fonts/Georgia Italic.ttf",
                "C:/Windows/Fonts/georgiai.ttf",
            ],
        }
        for path in candidates[style]:
            if Path(path).exists():
                return ImageFont.truetype(path, size)
        return ImageFont.load_default()

    def draw_lines(draw, lines, y_start, f, colour, area_w, area_x, ls=1.4):
        y = y_start
        for line in lines:
            if line == "":
                bb = draw.textbbox((0, 0), "M", font=f)
                y += int((bb[3] - bb[1]) * ls * 0.5)
                continue
            bb = draw.textbbox((0, 0), line, font=f)
            x = area_x + (area_w - (bb[2] - bb[0])) // 2
            draw.text((x, y), line, font=f, fill=colour)
            y += int((bb[3] - bb[1]) * ls)
        return y

    def block_h(lines, f, ls=1.4):
        total = 0
        for line in lines:
            bb = ImageDraw.Draw(Image.new('RGB', (10, 10))).textbbox(
                (0, 0), "M" if line == "" else line, font=f
            )
            total += int((bb[3] - bb[1]) * ls * (0.5 if line == "" else 1.0))
        return total

    def load_from_bytes(img_bytes, max_w, max_h):
        img_rgba = Image.open(io.BytesIO(img_bytes)).convert('RGBA')
        bg = Image.new('RGBA', img_rgba.size, (255, 255, 255, 255))
        bg.paste(img_rgba, (0, 0), img_rgba)
        img = bg.convert('RGB')
        aw, ah = img.size
        scale = min(max_w / aw, max_h / ah)
        return img.resize((int(aw * scale), int(ah * scale)), Image.LANCZOS)

    def wrap(text, max_chars):
        out = []
        for para in text.split("\n"):
            words = para.split()
            cur = []
            for w in words:
                if len(" ".join(cur + [w])) > max_chars and cur:
                    out.append(" ".join(cur))
                    cur = [w]
                else:
                    cur.append(w)
            if cur:
                out.append(" ".join(cur))
        return out

    pages = []

    # Page 1: Title
    c = Image.new('RGB', (A4_W, A4_H), 'white')
    d = ImageDraw.Draw(c)
    title_lines = wrap(title, 22)
    y = int(A4_H * 0.13)
    y = draw_lines(d, title_lines, y, fnt(180, "bold"), (30, 30, 50), CONTENT_W, MARGIN, 1.15)
    y += 100
    cover_img = load_from_bytes(cover_bytes, int(CONTENT_W * 0.8), int(A4_H * 0.45))
    c.paste(cover_img, ((A4_W - cover_img.width) // 2, y))
    by_y = A4_H - int(A4_H * 0.10)
    draw_lines(d, ["by"], by_y - 100, fnt(52, "ital"), (80, 80, 100), CONTENT_W, MARGIN)
    draw_lines(d, ["Wonderleaf Books"], by_y, fnt(70, "bold"), (30, 30, 50), CONTENT_W, MARGIN)
    pages.append(c)

    # Page 2: Dedication
    c = Image.new('RGB', (A4_W, A4_H), 'white')
    d = ImageDraw.Draw(c)
    ded = story.get("dedication", "For every little dreamer.")
    ded_font = fnt(88, "ital")
    ded_lines = wrap(ded, 32)
    text_h = block_h(ded_lines, ded_font, 1.5)
    y = (A4_H - text_h) // 2
    draw_lines(d, ded_lines, y, ded_font, (40, 40, 60), CONTENT_W, MARGIN, 1.5)
    pages.append(c)

    # Pages 3-18
    story_font = fnt(76, "reg")
    for entry in story["pages"]:
        num = entry["page"]
        c = Image.new('RGB', (A4_W, A4_H), 'white')
        d = ImageDraw.Draw(c)
        lines = wrap(entry["text"], 34)
        text_h = block_h(lines, story_font, 1.55)
        art = None
        if num in illustrations:
            avail_h = CONTENT_H - text_h - 200
            art = load_from_bytes(illustrations[num], CONTENT_W, avail_h)
        total_h = text_h + (200 + art.height if art else 0)
        y = MARGIN + max(120, (CONTENT_H - total_h) // 2)
        y = draw_lines(d, lines, y, story_font, (30, 30, 50), CONTENT_W, MARGIN, 1.55)
        y += 100
        if art:
            c.paste(art, ((A4_W - art.width) // 2, y))
        pages.append(c)

    # Page 19: Closing
    c = Image.new('RGB', (A4_W, A4_H), 'white')
    d = ImageDraw.Draw(c)
    closing = story.get("closing", "And so, our story ends.")
    close_font = fnt(90, "reg")
    close_lines = wrap(closing, 32)
    text_h = block_h(close_lines, close_font, 1.55)
    y = MARGIN + max(200, (CONTENT_H - text_h) // 2 - 200)
    draw_lines(d, close_lines, y, close_font, (30, 30, 50), CONTENT_W, MARGIN, 1.55)
    pages.append(c)

    # Page 20: About
    c = Image.new('RGB', (A4_W, A4_H), 'white')
    d = ImageDraw.Draw(c)
    y = int(A4_H * 0.16)
    y = draw_lines(d, ["About Wonderleaf Books"], y, fnt(90, "bold"), (30, 30, 50), CONTENT_W, MARGIN, 1.3)
    y += 160
    body = [
        "Wonderleaf Books creates gentle,",
        "magical picture books for children",
        "\u2014 stories to be read at bedtime,",
        "cuddled up together.",
        "",
        "Every page is an adventure.",
    ]
    y = draw_lines(d, body, y, fnt(62, "reg"), (50, 50, 70), CONTENT_W, MARGIN, 1.55)
    y += 200
    draw_lines(d, ["Thank you for reading.", "", "\u2014 Wonderleaf Books"], y, fnt(62, "ital"),
                (40, 40, 60), CONTENT_W, MARGIN, 1.55)
    pages.append(c)

    # Save PDF to bytes
    pdf_buf = io.BytesIO()
    pages[0].save(pdf_buf, "PDF", resolution=DPI, save_all=True, append_images=pages[1:])
    pdf_buf.seek(0)
    status.write("PDF ready!")
    return pdf_buf.getvalue()


# ==========================================================================
# STREAMLIT UI
# ==========================================================================

def book_studio():
    st.title("🌙 Wonderleaf Books")
    st.markdown("Fill in the form and click **Generate**. PDF downloads at the end.")

    # Show config warnings if keys missing
    if not ANTHROPIC_KEY or not FAL_KEY:
        st.error(
            "**Setup incomplete.** Add these to Streamlit secrets (Settings → Secrets):\n\n"
            "```toml\n"
            'ANTHROPIC_API_KEY = "sk-ant-..."\n'
            'FAL_KEY = "fal_..."\n'
            'APP_PASSWORD = "your-password-here"\n'
            "```"
        )
        st.stop()

    # ---- Form (minimal - just 3 fields) ----
    title = st.text_input(
        "Book title",
        placeholder="Sweet Dreams, Little Unicorn",
    )

    cover_file = st.file_uploader(
        "Cover image (JPEG or PNG)",
        type=["png", "jpg", "jpeg", "webp"],
        help="Upload the cover of the book — becomes the character reference for every illustration",
    )

    brief = st.text_area(
        "Story brief (paste from your eBay description)",
        height=140,
        placeholder=(
            "e.g. 'Meet Little Unicorn, who is wide awake in the storybook nook "
            "while everyone else is fast asleep. Follow along on a gentle journey "
            "where dreams take shape and a warm feeling of sleepiness finally arrives.'"
        ),
    )

    # Advanced options - hidden in expander so form stays clean
    with st.expander("Advanced (optional)"):
        style = st.selectbox("Illustration style", ["pencil", "color"],
                              format_func=lambda x: "Pencil (B&W) — recommended" if x == "pencil" else "Colour")
        custom_sku = st.text_input("Custom filename (SKU)",
                                     placeholder="Auto-generated from title if blank",
                                     help="e.g. WL-000042 → book saves as WL-000042.pdf")

    generate = st.button("🎨 Generate Book", type="primary", use_container_width=True)

    # ---- Generation ----
    if generate:
        errors = []
        if not title: errors.append("Book title is empty")
        if not brief: errors.append("Story brief is empty")
        if not cover_file: errors.append("Cover image not uploaded")

        if errors:
            for e in errors:
                st.error(f"• {e}")
            st.stop()

        # Auto-generate SKU from title if not provided
        sku = custom_sku.strip() if custom_sku else _slugify(title)

        cover_bytes = cover_file.read()

        # Show cover preview
        st.image(cover_bytes, caption="Cover", width=200)

        progress_bar = st.progress(0.0)
        status = st.empty()
        log_area = st.expander("Log", expanded=False)
        log_lines = []

        class LogWriter:
            def write(self, msg):
                log_lines.append(msg)
                log_area.text("\n".join(log_lines[-40:]))
                status.write(msg)

        log = LogWriter()

        try:
            # Story - Claude auto-detects character from title + brief
            progress_bar.progress(0.02)
            story = generate_story(title, brief, ANTHROPIC_KEY, log)
            character = story.get("character", "the main character")
            progress_bar.progress(0.10)

            # Illustrations
            illustrations = generate_illustrations(
                story, character, cover_bytes, style, FAL_KEY, progress_bar, log
            )
            progress_bar.progress(0.92)

            # PDF
            pdf_bytes = build_pdf(title, story, cover_bytes, illustrations, log)
            progress_bar.progress(1.0)

            st.success(f"✓ Book ready! ({len(illustrations)}/{len(story['pages'])} illustrations)")

            st.download_button(
                "⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"{sku}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        except Exception as e:
            st.error(f"Error: {e}")
            import traceback
            log.write(traceback.format_exc())


def main():
    st.set_page_config(page_title="Wonderleaf", page_icon="🌙", layout="wide")

    check_password()

    with st.sidebar:
        st.markdown("## 🌙 Wonderleaf")
        section = st.radio(
            "Tool",
            ["Book Studio", "eBay Research"],
            captions=[
                "Generate an illustrated picture book",
                "Research listings, sellers and titles",
            ],
            label_visibility="collapsed",
        )
        st.divider()

    if section == "Book Studio":
        book_studio()
        return

    try:
        from ebay_research.ui import render as render_ebay_research
    except ImportError as exc:
        st.error(
            "The eBay research tools could not be loaded. Make sure the "
            f"`ebay_research` package is deployed alongside this app. ({exc})"
        )
        return
    render_ebay_research()


if __name__ == "__main__":
    main()
