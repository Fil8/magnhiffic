"""Fetch 0.8 deg RGB cutouts from the Legacy Survey viewer for every source in
sample_table.csv, burn in a 1 kpc scale bar (using each source's dl_mpc), and
drop them in ../docs/images/cutouts/ for the Sample page's "DES(rgb)" column
to link to.

This is a one-off asset-acquisition step, run by hand when the sample
changes -- NOT part of build_site.py's regular build, which stays
dependency-free and offline. Re-run this after editing sample_table.csv,
then re-run build_site.py to pick up (or drop) the column entries.

Needs Pillow for the scale-bar overlay:  pip install pillow
Run:  python3 fetch_cutouts.py

Sources outside the Legacy Survey footprint get a small flat placeholder
image back instead of real imaging; anything under NO_COVERAGE_MAX_BYTES
is treated as "no coverage" and skipped (observed placeholder size: 6404
bytes, real cutouts here run well into six figures).

CAVEAT: at this pixel scale (needed to cover 0.8 deg without an enormous
image), 1 kpc is sub-5-pixel for every source beyond Centaurus A, and
under 2 px past ~30 Mpc -- the bar is drawn at its true (rounded) length
regardless, so for the more distant sources it will be little more than a
tick mark. A distance-independent angular bar, or a larger fixed physical
scale (e.g. 10 kpc), would stay legible across the whole sample if that
turns out to matter more than literal 1 kpc.
"""
import csv
import os
import re
import time
import urllib.request

from PIL import Image, ImageDraw, ImageFont

SITE = "../docs"
OUT_DIR = os.path.join(SITE, "images", "cutouts")

LAYER = "ls-dr11"
PIXSCALE = 3.6     # arcsec/pixel
SIZE = 800         # pixels -> 800 * 3.6 arcsec = 2880 arcsec = 0.8 deg
NO_COVERAGE_MAX_BYTES = 20000

# Sources whose Legacy Survey RGB cutout is unusable for reasons other than
# missing footprint coverage, so the NO_COVERAGE_MAX_BYTES check won't catch
# them: Centaurus A's cutout comes back with hard-edged rectangular colour
# blocks instead of a real image, reproducibly, across DR9/DR10/DR11 and
# multiple pixel scales -- almost certainly the survey's own mosaic/sky-
# background pipeline choking on its exceptional angular size and
# brightness. Source a Cen A image separately rather than re-fetching here.
KNOWN_BAD = {"Centaurus A"}

BAR_KPC = 1.0
ARCSEC_PER_KPC_AT_1MPC = 206.265   # small-angle: 1 kpc subtends this many
                                    # arcsec at 1 Mpc; scales as 1/distance.
                                    # D_A is approximated as D_L (fine at
                                    # these low redshifts -- a few % at most).


def cutout_slug(name):
    """Filename stem for a source's cutout image. Shared with build_site.py
    so the Sample page links match what's actually on disk."""
    return re.sub(r"[^A-Za-z0-9_-]", "", name.replace(" ", "_"))


def ra_to_deg(s):
    h, m, sec = s.split(":")
    return (float(h) + float(m) / 60 + float(sec) / 3600) * 15


def dec_to_deg(s):
    sign = -1 if s.strip().startswith("-") else 1
    s = s.strip().lstrip("+-")
    d, m, sec = s.split(":")
    return sign * (float(d) + float(m) / 60 + float(sec) / 3600)


def draw_scale_bar(path, dl_mpc):
    """Burn a 1 kpc scale bar into the bottom-right corner of the cutout at
    path, sized from the source's luminosity distance."""
    arcsec_per_kpc = ARCSEC_PER_KPC_AT_1MPC / dl_mpc
    bar_px = max(1, round(BAR_KPC * arcsec_per_kpc / PIXSCALE))

    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    w, h = im.size
    margin = 24
    y = h - margin
    x2 = w - margin
    x1 = x2 - bar_px

    draw.line([(x1, y), (x2, y)], fill="white", width=3)
    draw.line([(x1, y - 5), (x1, y + 5)], fill="white", width=3)
    draw.line([(x2, y - 5), (x2, y + 5)], fill="white", width=3)

    label = "1 kpc"
    font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x2 - tw, y - 20), label, fill="white", font=font)

    im.save(path, "JPEG", quality=90)


def main():
    with open("sample_table.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    os.makedirs(OUT_DIR, exist_ok=True)
    kept, skipped = [], []
    for r in rows:
        name = r["name"]
        if name in KNOWN_BAD:
            skipped.append(name + " (known-bad rendering, not footprint)")
            continue
        ra = ra_to_deg(r["ra"])
        dec = dec_to_deg(r["dec"])
        url = ("https://www.legacysurvey.org/viewer/cutout.jpg?ra=%.6f&dec=%.6f"
               "&layer=%s&pixscale=%s&size=%d" % (ra, dec, LAYER, PIXSCALE, SIZE))
        path = os.path.join(OUT_DIR, cutout_slug(name) + ".jpg")
        urllib.request.urlretrieve(url, path)
        size = os.path.getsize(path)
        if size < NO_COVERAGE_MAX_BYTES:
            os.remove(path)
            skipped.append(name)
        else:
            draw_scale_bar(path, float(r["dl_mpc"]))
            kept.append(name)
        time.sleep(0.3)   # be polite to the cutout service

    print("%d cutouts saved to %s" % (len(kept), OUT_DIR))
    if skipped:
        print("%d sources have no Legacy Survey coverage, skipped: %s"
              % (len(skipped), ", ".join(skipped)))


if __name__ == "__main__":
    main()
