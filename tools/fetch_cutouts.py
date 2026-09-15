"""Fetch two Legacy Survey RGB cutouts per source in sample_table.csv -- a
1x1 deg wide-field view and a 0.3x0.3 deg zoom-in centred on the galaxy --
burn vertical scale bars into each, and drop them in
../docs/images/cutouts/ for the Sample page's "DES(rgb)" column to link to.

Both cutouts are the same pixel size (SIZE), so within each FOV an angular
bar comes out the same length in every image -- a fixed yardstick to
compare fields by -- while a physical bar (using each source's dl_mpc)
varies image to image, showing the true kpc scale of each galaxy. The
wide field uses a 2' / 30 kpc pair; the zoom-in, being ~3x finer per
pixel, uses a 30" / 10 kpc pair. Both bars are drawn vertically: the
angular bar in the bottom-left corner, the physical bar in the
bottom-right.

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
SIZE = 800   # pixels, both wide and zoom cutouts

FOV_WIDE_DEG = 1.0
FOV_ZOOM_DEG = 0.3
PIXSCALE_WIDE = FOV_WIDE_DEG * 3600 / SIZE   # 4.5 "/px
PIXSCALE_ZOOM = FOV_ZOOM_DEG * 3600 / SIZE   # 1.35 "/px

# (angular bar arcsec, physical bar kpc) per FOV.
BARS_WIDE = (120.0, 30.0)
BARS_ZOOM = (30.0, 10.0)

NO_COVERAGE_MAX_BYTES = 20000

# Sources whose Legacy Survey RGB cutout is unusable for reasons other than
# missing footprint coverage, so the NO_COVERAGE_MAX_BYTES check won't catch
# them: Centaurus A's cutout comes back with hard-edged rectangular colour
# blocks instead of a real image, reproducibly, across DR9/DR10/DR11 and
# multiple pixel scales -- almost certainly the survey's own mosaic/sky-
# background pipeline choking on its exceptional angular size and
# brightness. Source a Cen A image separately rather than re-fetching here.
KNOWN_BAD = {"Centaurus A"}

ARCSEC_PER_KPC_AT_1MPC = 206.265   # small-angle: 1 kpc subtends this many
                                    # arcsec at 1 Mpc; scales as 1/distance.
                                    # D_A is approximated as D_L (fine at
                                    # these low redshifts -- a few % at most).


def cutout_slug(name):
    """Filename stem for a source's cutout images. Shared with
    build_site.py so the Sample page links match what's actually on disk."""
    return re.sub(r"[^A-Za-z0-9_-]", "", name.replace(" ", "_"))


def ra_to_deg(s):
    h, m, sec = s.split(":")
    return (float(h) + float(m) / 60 + float(sec) / 3600) * 15


def dec_to_deg(s):
    sign = -1 if s.strip().startswith("-") else 1
    s = s.strip().lstrip("+-")
    d, m, sec = s.split(":")
    return sign * (float(d) + float(m) / 60 + float(sec) / 3600)


BAR_MARGIN = 30   # baseline distance from the bottom edge
BAR_INSET = 24    # bar column distance from the left/right edge


def _angular_label(angular_arcsec):
    """Arcsec as a compact label, switching to arcmin at/above 60"."""
    if angular_arcsec >= 60:
        return "%g'" % (angular_arcsec / 60)
    return '%g"' % angular_arcsec


def _draw_one_bar(draw, baseline_y, x, length_px, label, font):
    """One vertical bar, growing up from baseline_y at column x, with a
    fixed-position horizontal caption centred underneath -- so the label
    never has to share space with (or scale with) a very short bar."""
    y2 = baseline_y
    y1 = y2 - length_px

    draw.line([(x, y1), (x, y2)], fill="white", width=3)
    draw.line([(x - 5, y1), (x + 5, y1)], fill="white", width=3)
    draw.line([(x - 5, y2), (x + 5, y2)], fill="white", width=3)

    bbox = draw.textbbox((0, 0), label, font=font)
    tw = bbox[2] - bbox[0]
    draw.text((x - tw / 2, y2 + 6), label, fill="white", font=font)


def draw_scale_bars(path, dl_mpc, pixscale, angular_arcsec, phys_kpc):
    """Burn two vertical scale bars into the cutout at path: a fixed
    angular bar (same pixel length in every image at this pixel scale) in
    the bottom-left corner, and a physical bar sized from the source's
    luminosity distance (varies image to image) in the bottom-right."""
    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    font = ImageFont.load_default()
    baseline_y = im.height - BAR_MARGIN

    arcsec_per_kpc = ARCSEC_PER_KPC_AT_1MPC / dl_mpc
    phys_px = max(1, round(phys_kpc * arcsec_per_kpc / pixscale))
    ang_px = max(1, round(angular_arcsec / pixscale))

    _draw_one_bar(draw, baseline_y, BAR_INSET, ang_px,
                  _angular_label(angular_arcsec), font)
    _draw_one_bar(draw, baseline_y, im.width - BAR_INSET, phys_px,
                  "%g kpc" % phys_kpc, font)

    im.save(path, "JPEG", quality=90)


def _fetch(name, ra, dec, pixscale, suffix):
    url = ("https://www.legacysurvey.org/viewer/cutout.jpg?ra=%.6f&dec=%.6f"
           "&layer=%s&pixscale=%s&size=%d" % (ra, dec, LAYER, pixscale, SIZE))
    path = os.path.join(OUT_DIR, cutout_slug(name) + suffix + ".jpg")
    urllib.request.urlretrieve(url, path)
    if os.path.getsize(path) < NO_COVERAGE_MAX_BYTES:
        os.remove(path)
        return None
    return path


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
        dl_mpc = float(r["dl_mpc"])

        wide = _fetch(name, ra, dec, PIXSCALE_WIDE, "_wide")
        if wide:
            draw_scale_bars(wide, dl_mpc, PIXSCALE_WIDE, *BARS_WIDE)
        time.sleep(0.3)

        zoom = _fetch(name, ra, dec, PIXSCALE_ZOOM, "_zoom")
        if zoom:
            draw_scale_bars(zoom, dl_mpc, PIXSCALE_ZOOM, *BARS_ZOOM)
        time.sleep(0.3)

        if wide or zoom:
            kept.append(name)
        else:
            skipped.append(name)

    print("%d sources have at least one cutout saved to %s" % (len(kept), OUT_DIR))
    if skipped:
        print("%d sources skipped entirely: %s" % (len(skipped), ", ".join(skipped)))


if __name__ == "__main__":
    main()
