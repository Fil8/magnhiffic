"""Fetch 0.5 deg RGB cutouts from the Legacy Survey viewer for every source in
sample_table.csv, and drop them in ../docs/images/cutouts/ for the Sample
page's "Image" column to link to.

This is a one-off asset-acquisition step, run by hand when the sample
changes -- NOT part of build_site.py's regular build, which stays
dependency-free and offline. Re-run this after editing sample_table.csv,
then re-run build_site.py to pick up (or drop) the column entries.

Run:  python3 fetch_cutouts.py

Sources outside the Legacy Survey footprint get a small flat placeholder
image back instead of real imaging; anything under NO_COVERAGE_MAX_BYTES
is treated as "no coverage" and skipped (observed placeholder size: 6404
bytes, real 0.5 deg cutouts here run 70-240 KB).
"""
import csv
import os
import re
import time
import urllib.request

SITE = "../docs"
OUT_DIR = os.path.join(SITE, "images", "cutouts")

LAYER = "ls-dr11"
PIXSCALE = 3.0     # arcsec/pixel
SIZE = 600         # pixels -> 600 * 3.0 arcsec = 1800 arcsec = 0.5 deg
NO_COVERAGE_MAX_BYTES = 20000


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


def main():
    with open("sample_table.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    os.makedirs(OUT_DIR, exist_ok=True)
    kept, skipped = [], []
    for r in rows:
        name = r["name"]
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
            kept.append(name)
        time.sleep(0.3)   # be polite to the cutout service

    print("%d cutouts saved to %s" % (len(kept), OUT_DIR))
    if skipped:
        print("%d sources have no Legacy Survey coverage, skipped: %s"
              % (len(skipped), ", ".join(skipped)))


if __name__ == "__main__":
    main()
