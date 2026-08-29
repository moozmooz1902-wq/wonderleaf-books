"""Products and listings screens.

Everything here was previously terminal-only: generating the catalogue, screening
it for IP risk, attaching photos and links, and registering or culling listings.
Kept in its own module so app.py stays the simple one-button screen staff use.
"""

import os
import shutil
from pathlib import Path

import streamlit as st
import yaml

from . import catalogue as catalogue_mod
from . import compliance
from . import listings as listings_mod
from .config import ROOT, load_products
from .state import State

PRODUCTS_FILE = ROOT / "config" / "products.yaml"
ASSETS = ROOT / "assets"


def _save_products(products):
    with PRODUCTS_FILE.open("w", encoding="utf-8") as fh:
        yaml.safe_dump({"products": products}, fh, sort_keys=False,
                       allow_unicode=True, width=100)


# -- catalogue -----------------------------------------------------------


def render_catalogue(settings):
    st.markdown("#### Create products")
    st.caption("Generates product ideas as sets of three prints. Each one is "
               "checked for copyright problems before it is added.")

    have_key = bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
    if not have_key:
        st.warning("This needs ANTHROPIC_API_KEY in `tiktok/.env`.")

    niches = st.multiselect(
        "Categories", options=list(catalogue_mod.NICHES),
        default=["botanical", "family", "affirmation"],
        help="Cars, music and sport are higher risk - they are steered onto "
             "things nobody can own, like circuit layouts and route maps.",
    )
    for risky in ("cars", "music", "sport"):
        if risky in niches:
            st.info(f"**{risky}** is a high-risk category. Anything generated "
                    f"for it avoids real brands, bands and clubs, but check each "
                    f"one yourself before listing it.")
            break

    count = st.number_input("How many ideas", 1, 100, 12, step=1)

    if st.button("Generate ideas", type="primary", disabled=not (have_key and niches)):
        seen = {p["id"] for p in load_products()} if PRODUCTS_FILE.exists() else set()
        plan = catalogue_mod.allocate(int(count), niches)
        found, log = [], []
        bar = st.progress(0.0, text="Starting...")
        for i, (niche, n) in enumerate([(k, v) for k, v in plan.items() if v > 0]):
            bar.progress(i / max(len(plan), 1), text=f"Thinking about {niche}...")
            try:
                found.extend(catalogue_mod.generate_niche(
                    niche, n, os.environ["ANTHROPIC_API_KEY"], settings, seen,
                    log=log.append))
            except Exception as exc:
                st.error(f"{niche}: {exc}")
        bar.progress(1.0, text="Done")
        st.session_state["draft_concepts"] = found
        blocked = [line for line in log if "blocked" in line]
        if blocked:
            st.warning(f"{len(blocked)} idea(s) were rejected for copyright "
                       f"reasons and are not shown.")
            with st.expander("What was rejected and why"):
                st.code("\n".join(blocked), language=None)

    drafts = st.session_state.get("draft_concepts") or []
    if drafts:
        st.markdown(f"**{len(drafts)} idea(s) ready**")
        st.dataframe(
            [{"Name": c["name"], "Category": c["niche"], "Price": f"£{c['price_gbp']}",
              "Needs a look": "yes" if c.get("ip_review") else "",
              "Description": c["description"][:90]} for c in drafts],
            use_container_width=True, hide_index=True,
        )
        c1, c2 = st.columns(2)
        if c1.button("Add all to my products", type="primary"):
            path, total = catalogue_mod.write_back(drafts, log=lambda m: None)
            st.session_state.pop("draft_concepts", None)
            st.success(f"Added. You now have {total} products.")
            st.rerun()
        if c2.button("Discard these"):
            st.session_state.pop("draft_concepts", None)
            st.rerun()


# -- per-product setup ---------------------------------------------------


def render_setup(products):
    st.markdown("#### Finish setting up a product")
    st.caption("A product needs a photo and a shop link before real videos can "
               "be made for it.")

    incomplete = [p for p in products if not p.get("images") or not p.get("link")]
    if incomplete:
        st.warning(f"{len(incomplete)} of {len(products)} products still need a "
                   f"photo or a link.")

    labels = {f"{'⚠️ ' if (not p.get('images') or not p.get('link')) else '✅ '}"
              f"{p['name']}": p["id"] for p in products}
    choice = st.selectbox("Product", options=list(labels))
    if not choice:
        return
    pid = labels[choice]
    product = next(p for p in products if p["id"] == pid)

    st.text_area("Description", product.get("description", ""), disabled=True,
                 height=80)

    verdict, reasons = compliance.screen(product)
    if verdict == compliance.Verdict.BLOCK:
        st.error("**Do not list this.** " + "; ".join(reasons))
    elif verdict == compliance.Verdict.REVIEW:
        st.warning("**Check this one before listing.** " + "; ".join(reasons))
    else:
        st.success("No copyright problems found. Still check it yourself.")

    link = st.text_input(
        "TikTok Shop link", value=product.get("link", ""),
        placeholder="https://vt.tiktok.com/...",
        help="Create the listing in Seller Center first, then paste its link here.",
    )

    current = (product.get("images") or [None])[0]
    if current and (ROOT / current).exists():
        st.image(str(ROOT / current), width=200, caption="Current photo")
    photo = st.file_uploader("Photo of the prints", type=["png", "jpg", "jpeg", "webp"],
                             help="Every video is built from this, so the art in "
                                  "the video matches what you actually sell.")

    if st.button("Save", type="primary"):
        changed = False
        if link.strip() != product.get("link", ""):
            product["link"] = link.strip()
            changed = True
        if photo is not None:
            ASSETS.mkdir(parents=True, exist_ok=True)
            suffix = Path(photo.name).suffix.lower() or ".jpg"
            dest = ASSETS / f"{pid}{suffix}"
            dest.write_bytes(photo.getvalue())
            product["images"] = [str(dest.relative_to(ROOT))]
            changed = True
        if changed:
            _save_products(products)
            st.success("Saved.")
            st.rerun()
        else:
            st.info("Nothing to save.")


# -- listings ------------------------------------------------------------


def render_listings(settings, products):
    st.markdown("#### Listings")
    cfg = listings_mod.config(settings)
    lst = listings_mod.Listings()
    live = lst.live()
    free = cfg["cap"] - len(live)

    c1, c2, c3 = st.columns(3)
    c1.metric("Live listings", f"{len(live)}/{cfg['cap']}")
    c2.metric("Free slots", free)
    c3.metric("Culled", len([x for x in lst.data["listings"]
                             if x.get("status") == "culled"]))

    with st.expander("Register a new listing", expanded=not live):
        st.caption("Do this after you create the listing in Seller Center.")
        sku = st.text_input("SKU", placeholder="WL-001")
        labels = {p["name"]: p["id"] for p in products}
        pname = st.selectbox("Which product is it?", options=list(labels))
        title = st.text_input("Listing title", value=pname or "")
        if st.button("Add listing", type="primary", disabled=not (sku and pname)):
            try:
                lst.add(sku.strip(), labels[pname], title.strip())
                lst.save()
                st.success(f"Added {sku}. {free - 1} slots free.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

    if not live:
        return

    st.markdown("**How each listing is doing**")
    st.caption("Upload a Seller Center export on the Run screen to update these.")
    state = State()
    rows, culls = [], []
    for listing in live:
        v, reason, totals, vids = listings_mod.assess(listing, cfg, state)
        rows.append({"SKU": listing["sku"], "Verdict": v,
                     "Days": listings_mod.days_live(listing), "Videos": vids,
                     "Views": totals["views"], "Units": totals["units"],
                     "Why": reason})
        if v == "CULL":
            culls.append(listing["sku"])
    order = {"CULL": 0, "WATCH": 1, "NO DATA": 2, "TOO EARLY": 3, "KEEP": 4}
    rows.sort(key=lambda r: order.get(r["Verdict"], 9))
    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.caption("**CULL** = people saw it and nobody bought — the listing is dead. "
               "**WATCH** = hardly anyone saw it yet, so it has not been tested. "
               "They look the same on a sales report and need opposite responses.")

    if culls:
        st.warning(f"**Dead listings:** {', '.join(culls)}")
        pick = st.selectbox("Remove a dead listing", options=culls)
        if st.button(f"Mark {pick} as removed"):
            lst.cull(pick, "dead - no sales")
            lst.save()
            st.success(f"{pick} removed. Delist it in Seller Center too, then "
                       f"add a replacement.")
            st.rerun()


def render(settings):
    products = load_products()
    tabs = st.tabs(["Create products", "Photos & links", "Listings"])
    with tabs[0]:
        render_catalogue(settings)
    with tabs[1]:
        render_setup(products)
    with tabs[2]:
        render_listings(settings, products)
