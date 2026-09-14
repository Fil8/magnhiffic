#!/usr/bin/env python3
"""Propagate the shared header/footer from one page to all the others.

The site is flat HTML, so the navigation bar and footer are physically
duplicated into every page. Edit them in ONE page (in Pinegrow, or any editor),
then run this to copy that version into the other 16:

    python3 sync_chrome.py                 # use Home.html as the source
    python3 sync_chrome.py Science.html    # use a different page as the source
    python3 sync_chrome.py --check         # report drift, change nothing

Only the regions between these markers are touched:

    <!-- ==== SHARED HEADER ... ==== -->   ...   <!-- ==== END SHARED HEADER ==== -->
    <!-- ==== SHARED FOOTER ... ==== -->   ...   <!-- ==== END SHARED FOOTER ==== -->

Everything outside them is left byte-for-byte alone. Keep the marker comments:
delete them and this script can no longer find the region (it will tell you
rather than guess).

The nav has no current-page highlight (neither did the template it came from),
so the header really is identical on every page and can be copied verbatim.
"""
import os
import re
import shutil
import sys

def _find_site():
    """Locate the directory holding the .html pages.

    Works whether this script sits beside the pages (flat layout) or in
    tools/ next to a docs/ publishing root (GitHub Pages layout).
    Override with:  SITE=/path/to/pages python3 sync_chrome.py Home.html
    """
    env = os.environ.get("SITE")
    if env:
        return env
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (here, os.path.join(here, "docs"),
                 os.path.join(os.path.dirname(here), "docs")):
        if os.path.isdir(cand) and any(f.endswith(".html") for f in os.listdir(cand)):
            return cand
    return here


SITE = _find_site()
REGIONS = [
    ("<!-- ==== SHARED HEADER", "<!-- ==== END SHARED HEADER ==== -->"),
    ("<!-- ==== SHARED FOOTER", "<!-- ==== END SHARED FOOTER ==== -->"),
]


def pages():
    return sorted(f for f in os.listdir(SITE) if f.endswith(".html"))


def extract(text, start_tag, end_tag, page):
    i = text.find(start_tag)
    if i < 0:
        raise SystemExit(
            "%s: marker %r not found. Was the comment deleted? "
            "Restore it or regenerate with build_site.py." % (page, start_tag)
        )
    j = text.find(end_tag, i)
    if j < 0:
        raise SystemExit("%s: found %r but not its END marker." % (page, start_tag))
    return i, j + len(end_tag)


def main():
    args = [a for a in sys.argv[1:]]
    check = "--check" in args
    args = [a for a in args if not a.startswith("--")]
    source = args[0] if args else "Home.html"
    if source not in pages():
        raise SystemExit("source page %r not found in %s" % (source, SITE))

    src = open(os.path.join(SITE, source), encoding="utf-8").read()
    blocks = []
    for start_tag, end_tag in REGIONS:
        i, j = extract(src, start_tag, end_tag, source)
        blocks.append(src[i:j])

    changed, drifted = [], []
    for page in pages():
        if page == source:
            continue
        path = os.path.join(SITE, page)
        text = open(path, encoding="utf-8").read()
        new = text
        for (start_tag, end_tag), block in zip(REGIONS, blocks):
            i, j = extract(new, start_tag, end_tag, page)
            if new[i:j] != block:
                new = new[:i] + block + new[j:]
        if new != text:
            drifted.append(page)
            if not check:
                shutil.copy2(path, path + ".bak")
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                changed.append(page)

    if check:
        if drifted:
            print("header/footer differ from %s on %d page(s):" % (source, len(drifted)))
            for p in drifted:
                print("  " + p)
        else:
            print("all %d pages match %s" % (len(pages()), source))
        return
    if changed:
        print("updated %d page(s) from %s (.bak written beside each):" % (len(changed), source))
        for p in changed:
            print("  " + p)
    else:
        print("nothing to do - all pages already match %s" % source)


if __name__ == "__main__":
    main()
