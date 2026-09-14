"""Build the MAGNHIFFIC static site on the mhongoose (Nicepage 5.2.4) framework.

Run:  python build_site.py
Output: magnhiffic_site/*.html   (CSS/JS/images are copied in beforehand)

Everything user-visible lives in this file. To change the wordmark, the nav,
the footer acknowledgement, or any page's prose, edit here and re-run.
"""
import math
import os, re, hashlib, shutil

SITE = "../docs"   # GitHub Pages publishing root

# ---------------------------------------------------------------------- theme
# EVERY font, size and colour of the site is set here, and nowhere else.
# Change a value, run `python3 build_site.py`, and it applies to all 17 pages:
# the build writes docs/theme.css from this dict, and every page loads that
# file last, so its rules win over nicepage.css and over the page stylesheets.
#
# Do NOT edit fonts in nicepage.css — that file is the framework and is meant
# to stay untouched.
THEME = {
    # --- fonts.  Any family that is not websafe must ALSO be listed in
    #     GOOGLE_FONTS below, or the browser falls back silently.
    "body_font":      "'Open Sans', sans-serif",   # paragraphs, tables, nav
    "heading_font":   "Roboto, sans-serif",        # h1-h6
    "display_font":   "'Cantata One', serif",      # Home hero title + strapline
    "wordmark_font":  "Roboto, sans-serif",        # MAGNHIFFIC in the black bar

    # --- sizes.  root_size scales the entire site (everything else is rem).
    "root_size":      "16px",
    "body_size":      "1rem",
    "hero_size":      "4.5rem",     # Home hero title, desktop
    "wordmark_size":  "1.75rem",

    # --- weight and letter-spacing of the display elements
    "heading_weight": "700",
    "hero_weight":    "900",
    "hero_tracking":  "4px",

    # --- colours
    "accent":     "#478ac9",   # links, inline buttons, star hover fill
    "text_color": "#3e3e3e",   # body copy
    "dark_bg":    "#000000",   # header bar, More Info band, footer

    # --- Sample-table subsample fills.  The table sits on the black band, so
    #     these are dark tints that keep white text readable.  Blue vs amber
    #     is the colour-blind-safe pair; change the hexes, not the pairing.
    "magnum_bg":     "#14395c",   # MAGNUM subsample rows
    "radio_loud_bg": "#5c3a14",   # radio-loud subsample rows
    "other_bg":      "#2b2b2b",   # additional sources
}

# Google Fonts to load, in the API's own syntax (family, then the weights you
# actually use — loading fewer weights makes the page faster).  Spaces are "+".
GOOGLE_FONTS = [
    "Roboto:100,300,400,500,700,900",
    "Open+Sans:300,300i,400,400i,600,600i,700,700i",
    "Cantata+One",
]

# Back-compatible aliases: the rest of the script reads these two names.
ACCENT = THEME["accent"]
HERO_FONT = THEME["display_font"]

# Radius of the Home-page star, in percent of its box. Bigger = wider star.
STAR_RADIUS = 34.0   # node distance from centre, % of the star box
STAR_BOX = 480       # side of the square the star is drawn in, px
STAR_NODE = 116      # diameter of each round button, px

# ---------------------------------------------------------------- site chrome

NAV = [
    ("Home.html",                "Home",        []),
    ("Publications.html",        "Publications",[]),
    ("Survey.html",              "Survey",      [("Science.html", "Science")]),
    ("Sample.html",              "Sample",      []),
    ("Public-Data-Release.html", "Public Data", []),
    ("Team.html",                "Team",        [("Data.html",     "Team Data"),
                                                 ("Gallery.html",  "Gallery"),
                                                 ("Releases.html", "Releases"),
                                                 ("Projects.html", "Projects")]),
    ("Contact.html",             "Contact",     []),
]

WORDMARK_FULL = "MeerKAT AGN HI Feeding &amp; Feedback Investigation Close-by"

# Drop-in logo: put a file at images/magnhiffic_logo.png and set this to its
# name; the header/hero will use the image instead of the text wordmark.
LOGO_IMAGE = None

# NOTE FOR REVIEW: the template credited ERC grant 882793 "MeerGas", which is the
# MHONGOOSE-side grant. Replace the text below with MAGNHIFFIC's own funding
# acknowledgement (and swap images/LOGO_ERC-FLAG_EUNEGATIF1.jpg + the erc.europa.eu
# link in footer() if the funder differs).
FUNDING = ('MAGNHIFFIC is supported by INAF \u2013 Istituto Nazionale di Astrofisica. '
           '[Funding acknowledgement to be completed \u2013 see REVIEW_NOTES.md]&nbsp;')

NAV_LINK = ("u-button-style u-nav-link u-text-active-palette-1-base "
            "u-text-hover-palette-2-base")


def _nav_items(link_cls, sub_cls_of, collapsed=False):
    out = []
    for href, label, subs in NAV:
        sub = ""
        if subs:
            inner = "".join(
                '<li class="u-nav-item"><a class="%s" href="%s">%s</a>\n</li>'
                % ("u-button-style u-nav-link" if collapsed
                   else "u-black u-button-style u-nav-link", h, l)
                for h, l in subs)
            sub = ('<div class="u-nav-popup"><ul class="u-h-spacing-20 u-nav '
                   'u-unstyled u-v-spacing-10 u-nav-%d">%s</ul>\n</div>\n'
                   % (sub_cls_of[href], inner))
        style = "" if collapsed else ' style="padding: 10px 20px;"'
        out.append('<li class="u-nav-item"><a class="%s" href="%s"%s>%s</a>%s</li>'
                   % (link_cls, href, style, label, sub or "\n"))
    return "".join(out)


def header():
    """Sticky black header: wordmark (or logo) + dropdown nav + offcanvas nav."""
    if LOGO_IMAGE:
        brand = ('<a href="Home.html" class="u-image u-logo u-image-1">\n'
                 '          <img src="images/%s" class="u-logo-image u-logo-image-1">\n'
                 '        </a>' % LOGO_IMAGE)
    else:
        brand = ('<a href="Home.html" class="u-logo u-wordmark">'
                 '<span class="u-wordmark-text">MAGNHIFFIC</span></a>')

    main = _nav_items(NAV_LINK, {"Survey.html": 2, "Team.html": 3})
    coll = _nav_items("u-button-style u-nav-link",
                      {"Survey.html": 5, "Team.html": 6}, collapsed=True)
    return """<!-- ==== SHARED HEADER: identical on all pages. Edit here, then run sync_chrome.py (or rebuild). ==== -->
<header class="u-black u-clearfix u-header u-sticky u-sticky-2694 u-header" id="sec-fe27"><div class="u-clearfix u-sheet u-sheet-1">
        %s
        <nav class="u-menu u-menu-dropdown u-offcanvas u-menu-1" data-responsive-from="MD">
          <div class="menu-collapse" style="font-size: 1rem; letter-spacing: 0px;">
            <a class="u-button-style u-custom-left-right-menu-spacing u-custom-padding-bottom u-custom-top-bottom-menu-spacing u-nav-link u-text-active-palette-1-base u-text-hover-palette-2-base" href="#">
              <svg class="u-svg-link" viewBox="0 0 24 24"><use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#menu-hamburger"></use></svg>
              <svg class="u-svg-content" version="1.1" id="menu-hamburger" viewBox="0 0 16 16" x="0px" y="0px" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg"><g><rect y="1" width="16" height="2"></rect><rect y="7" width="16" height="2"></rect><rect y="13" width="16" height="2"></rect>
</g></svg>
            </a>
          </div>
          <div class="u-custom-menu u-nav-container">
            <ul class="u-nav u-unstyled u-nav-1">%s</ul>
          </div>
          <div class="u-custom-menu u-nav-container-collapse">
            <div class="u-black u-container-style u-inner-container-layout u-opacity u-opacity-95 u-sidenav">
              <div class="u-inner-container-layout u-sidenav-overflow">
                <div class="u-menu-close"></div>
                <ul class="u-align-center u-nav u-popupmenu-items u-unstyled u-nav-4">%s</ul>
              </div>
            </div>
            <div class="u-black u-menu-overlay u-opacity u-opacity-70"></div>
          </div>
        </nav>
      </div></header>
<!-- ==== END SHARED HEADER ==== -->""" % (brand, main, coll)


def footer():
    return """<!-- ==== SHARED FOOTER: identical on all pages. Edit here, then run sync_chrome.py (or rebuild). ==== -->
<footer class="u-align-center u-black u-clearfix u-footer u-footer" id="sec-2012"><div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-border-3 u-border-grey-dark-1 u-line u-line-horizontal u-line-1"></div>
        <a href="https://erc.europa.eu/" class="u-image u-logo u-image-1" data-image-width="1160" data-image-height="511">
          <img src="images/LOGO_ERC-FLAG_EUNEGATIF1.jpg" class="u-logo-image u-logo-image-1">
        </a>
        <p class="u-align-left u-small-text u-text u-text-variant u-text-1"> %s<br>
        </p>
      </div></footer>
<!-- ==== END SHARED FOOTER ==== -->""" % FUNDING


def google_fonts_url():
    """The single <link> that loads every family named in GOOGLE_FONTS."""
    return ("https://fonts.googleapis.com/css?family="
            + "|".join(GOOGLE_FONTS) + "&display=swap")


def head(title, css, description=""):
    return """<!DOCTYPE html>
<html style="font-size: THEME_ROOT_SIZE;" lang="en"><head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta charset="utf-8">
    <meta name="keywords" content="MAGNHIFFIC, MeerKAT, AGN, neutral hydrogen, HI, AGN feeding, AGN feedback, radio galaxies, nearby galaxies, radio astronomy">
    <meta name="description" content="%s">
    <title>%s</title>
    <link rel="stylesheet" href="nicepage.css" media="screen">
<link rel="stylesheet" href="%s" media="screen">
    <link rel="stylesheet" href="theme.css" media="screen">
    <script class="u-script" type="text/javascript" src="jquery.js" defer=""></script>
    <script class="u-script" type="text/javascript" src="nicepage.js" defer=""></script>
    <meta name="generator" content="Nicepage 5.2.4, nicepage.com">
    <link id="u-theme-google-font" rel="stylesheet" href="%s">
    <script type="application/ld+json">{
\t\t"@context": "http://schema.org",
\t\t"@type": "Organization",
\t\t"name": "MAGNHIFFIC"
}</script>
    <meta name="theme-color" content="%s">
    <meta property="og:title" content="%s">
    <meta property="og:description" content="%s">
    <meta property="og:type" content="website">
  </head>""".replace("THEME_ROOT_SIZE", THEME["root_size"]) % (
        description, title, css, google_fonts_url(), ACCENT, title, description)


def page(title, css, sections, description="", body_class="u-body"):
    return "%s\n  <body class=\"%s\">\n    %s\n    %s\n    %s\n  \n</body></html>\n" % (
        head(title, css, description), body_class, header(),
        "\n    ".join(sections), footer())


def write(name, html):
    with open(os.path.join(SITE, name), "w", encoding="utf-8") as fh:
        fh.write(html)
    return name


TPL = "template_css"


def tpl_css(name):
    with open(os.path.join(TPL, name), encoding="utf-8") as fh:
        return fh.read()


def write_css(name, text):
    with open(os.path.join(SITE, name), "w", encoding="utf-8") as fh:
        fh.write(text)
    return name


def tint(hex_colour, frac):
    """Mix a #rrggbb colour with white.  frac=0 -> unchanged, 1 -> white."""
    h = hex_colour.lstrip("#")
    rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
    return "#%02x%02x%02x" % tuple(
        int(round(v + (255 - v) * frac)) for v in rgb)


def write_theme_css():
    """Render THEME into docs/theme.css.

    Every page links this file AFTER nicepage.css and after its own
    stylesheet, so these rules decide the site's typography and accent
    colour.  Nicepage's two font hooks (.u-custom-font.u-text-font and
    .u-custom-font.u-heading-font) carry !important in the framework sheet,
    which is why the overrides for those two selectors need it as well; the
    rest win on ordering alone.
    """
    t = dict(THEME)
    t["display_font"] = t.get("display_font") or t["heading_font"]
    t["accent_light"] = tint(t["accent"], 0.27)
    for k in ("magnum", "radio_loud", "other"):
        t[k + "_head"] = tint(t[k + "_bg"], 0.22)
    css = """/* theme.css -- GENERATED by tools/build_site.py from the THEME dict.
   Do not hand-edit: the next build overwrites this file.  To change a font,
   a size or the accent colour, edit THEME at the top of build_site.py and
   re-run it. */

/* ------------------------------------------------------------------ fonts */

.u-body {
  font-family: %(body_font)s;
  font-size: %(body_size)s;
  color: %(text_color)s;
}

h1, h2, h3, h4, h5, h6 {
  font-family: %(heading_font)s;
  font-weight: %(heading_weight)s;
}

.u-custom-font.u-text-font    { font-family: %(body_font)s !important; }
.u-custom-font.u-heading-font { font-family: %(heading_font)s !important; }

/* Header wordmark (the black bar) */
.u-header .u-wordmark .u-wordmark-text {
  font-family: %(wordmark_font)s;
  font-size: %(wordmark_size)s;
}

/* Home hero */
.u-hero-wordmark {
  font-family: %(display_font)s;
  font-weight: %(hero_weight)s;
  letter-spacing: %(hero_tracking)s;
}

.u-hero-subtitle { font-family: %(display_font)s; }

/* --------------------------------------------------------------- colours */

/* Accent: inline links and active nav items. */
.u-text-palette-1-base,
li.active > a.u-button-style.u-text-palette-1-base,
a.u-button-style.u-text-palette-1-base { color: %(accent)s !important; }

/* Accent as a fill: palette swatches 1 and 3, and the star's hover state. */
.u-palette-1-base,
.u-palette-3-base,
section.u-palette-1-base:before,
section.u-palette-3-base:before,
.u-section-2 a.u-star-node:hover,
.u-section-2 a.u-star-node:focus { background-color: %(accent)s; }

.u-border-palette-3-base { border-color: %(accent)s; }

/* Hover/active states use the framework's lighter step of the same ramp,
   derived here from the accent so one edit recolours both. */
a.u-link.u-hover-palette-1-light-1:hover,
.u-active-palette-1-light-1:active { color: %(accent_light)s !important; }

.u-border-hover-palette-1-light-1:hover,
.u-border-active-palette-1-light-1:active { border-color: %(accent_light)s; }

.u-palette-1-light-1,
section.u-palette-1-light-1:before { background-color: %(accent_light)s; }

/* The dark bands: header bar, More Info section, footer. */
.u-black,
section.u-black:before,
.u-black.u-sidenav:before { background-color: %(dark_bg)s; }

/* ------------------------------------------- Sample table, by subsample */

tr.u-sample-magnum     > td { background-color: %(magnum_bg)s; }
tr.u-sample-radio_loud > td { background-color: %(radio_loud_bg)s; }
tr.u-sample-other      > td { background-color: %(other_bg)s; }

/* Group label rows: same hue, one step lighter, left-aligned. */
tr.u-sample-group.u-sample-magnum     > td { background-color: %(magnum_head)s; }
tr.u-sample-group.u-sample-radio_loud > td { background-color: %(radio_loud_head)s; }
tr.u-sample-group.u-sample-other      > td { background-color: %(other_head)s; }

tr.u-sample-group > td {
  font-family: %(heading_font)s;
  font-weight: %(heading_weight)s;
  text-align: left;
  letter-spacing: 1px;
  padding-top: 10px;
  padding-bottom: 10px;
}

tr.u-sample-group .u-sample-ref   { color: #ffffff; text-decoration: underline; }
tr.u-sample-group .u-sample-count { font-weight: 400; opacity: 0.75; }

/* Legend swatches in the intro paragraph. */
.u-sample-key {
  display: inline-block;
  width: 0.9em;
  height: 0.9em;
  vertical-align: -0.05em;
  border: 1px solid rgba(255, 255, 255, 0.5);
}

.u-sample-key-magnum     { background-color: %(magnum_bg)s; }
.u-sample-key-radio_loud { background-color: %(radio_loud_bg)s; }
.u-sample-key-other      { background-color: %(other_bg)s; }
""" % t
    return write_css("theme.css", css)


def btn(href, label, n, external=False):
    """Inline text link styled like the template's borderless accent links."""
    tgt = ' target="_blank"' if external else ""
    return ('<a href="%s" class="u-active-none u-border-none u-btn u-button-link '
            'u-button-style u-hover-none u-none u-text-palette-1-base u-btn-%d"%s>%s</a>'
            % (href, n, tgt, label))


def card(icon, title, blurb, href, label, i):
    """One tile of a card repeater (used by the Data page)."""
    return """<div class="u-align-center u-container-style u-list-item u-repeater-item">
              <div class="u-container-layout u-similar-container u-valign-top u-container-layout-%d"><span class="u-file-icon u-icon u-icon-circle u-palette-3-base u-text-white u-icon-%d"><img src="images/%s" alt=""></span>
                <h5 class="u-text u-text-%d">%s</h5>
                <p class="u-text u-text-grey-40 u-text-%d">%s</p>
                <a href="%s" class="u-border-2 u-border-palette-3-base u-btn u-btn-round u-button-style u-hover-palette-3-base u-none u-radius-25 u-text-hover-white u-text-palette-3-base u-btn-%d">%s</a>
              </div>
            </div>""" % (i, i, icon, 2 * i + 1, title, 2 * i + 2, blurb, href, i, label)


def star_points(n=5, radius=STAR_RADIUS, cx=50.0, cy=50.0, start=-90.0):
    """Centres of n nodes on a circle, in percent of the container box.

    start=-90 puts node 1 at the top; nodes then run clockwise.
    """
    out = []
    for k in range(n):
        a = math.radians(start + k * 360.0 / n)
        out.append((cx + radius * math.cos(a), cy + radius * math.sin(a)))
    return out


def star_nav(items, radius=STAR_RADIUS):
    """The five section buttons arranged as a star.

    items: list of (icon, title, blurb, href, label) - the same tuples the old
    card grid used, so labels and links stay declared in one place (HOME_STAR).
    Geometry is computed here: change STAR_RADIUS to resize the star and the
    connecting pentagram follows automatically.
    """
    pts = star_points(len(items), radius)

    # Pentagram: visit every second vertex (0-2-4-1-3), closing the path.
    order = [(2 * k) % len(items) for k in range(len(items))]
    lines = " ".join("%.2f,%.2f" % pts[k] for k in order)

    nodes = []
    for i, (icon, title, blurb, href, label) in enumerate(items, 1):
        x, y = pts[i - 1]
        nodes.append(
            '<a href="%s" title="%s" class="u-star-node u-star-node-%d" '
            'style="left: %.2f%%; top: %.2f%%;">'
            '<span class="u-star-icon"><img src="images/%s" alt=""></span>'
            '<span class="u-star-label">%s</span></a>'
            % (href, title, i, x, y, icon, label))

    return ('<div class="u-star-nav">\n'
            '                  <svg class="u-star-lines" viewBox="0 0 100 100" '
            'preserveAspectRatio="none" aria-hidden="true" focusable="false">\n'
            '                    <polygon points="%s"></polygon>\n'
            '                  </svg>\n                  %s\n'
            '                </div>'
            % (lines, "\n                  ".join(nodes)))


def home_sec2_css():
    """CSS for the Home "More Info" + star section (was section 3, now 2).

    The star itself is driven by three numbers:
      STAR_BOX   - side of the square the star is drawn in (px, desktop)
      STAR_NODE  - diameter of each round button (px, desktop)
      STAR_RADIUS (top of file) - node distance from the centre, in %% of the box
    The nodes' left/top come from star_nav(); everything below is presentation.
    """
    return """

.u-section-2 {
  background-image: none;
}

.u-section-2 .u-sheet-1 {
  min-height: 984px;
}

.u-section-2 .u-layout-wrap-1 {
  margin-top: 38px;
  margin-bottom: 0;
}

.u-section-2 .u-layout-cell-1 {
  min-height: 564px;
}

.u-section-2 .u-container-layout-1 {
  padding: 30px;
}

.u-section-2 .u-text-1 {
  font-weight: 700;
  font-size: 2.25rem;
  margin: 6px 0 0;
}

.u-section-2 .u-text-2 {
  line-height: 1.4;
  margin: 20px 0 0;
}

.u-section-2 .u-btn-1 {
  background-image: none;
  padding: 0;
}

.u-section-2 .u-layout-cell-2 {
  min-height: 564px;
}

.u-section-2 .u-container-layout-2 {
  padding: 10px;
}

/* ---------------------------------------------------------------- the star */

.u-section-2 .u-star-nav {
  position: relative;
  width: %(box)dpx;
  height: %(box)dpx;
  max-width: 100%%;
  margin: 20px auto 0;
}

.u-section-2 .u-star-lines {
  position: absolute;
  left: 0;
  top: 0;
  width: 100%%;
  height: 100%%;
  overflow: visible;
  pointer-events: none;
}

.u-section-2 .u-star-lines polygon {
  fill: none;
  stroke: %(accent)s;
  stroke-width: 1.5;
  stroke-opacity: 0.55;
  vector-effect: non-scaling-stroke;
}

.u-section-2 a.u-star-node {
  position: absolute;
  transform: translate(-50%%, -50%%);
  width: %(node)dpx;
  height: %(node)dpx;
  border-radius: 50%%;
  /* The nodes carry no framework colour/button tokens on purpose: u-none
     forces background-color transparent !important on .u-button-style, which
     would strip the fill. Everything a node needs is declared here. */
  border: 2px solid %(accent)s;
  margin: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 0;
  cursor: pointer;
  white-space: nowrap;
  text-decoration: none;
  color: %(accent)s;
  background-color: rgba(0, 0, 0, 0.85);
  background-image: none;
  text-align: center;
  line-height: 1.1;
  transition: background-color 0.25s, color 0.25s, transform 0.25s;
}

.u-section-2 a.u-star-node:hover,
.u-section-2 a.u-star-node:focus {
  background-color: %(accent)s;
  color: #ffffff;
  transform: translate(-50%%, -50%%) scale(1.08);
}

.u-section-2 .u-star-icon {
  display: block;
  width: %(icon)dpx;
  height: %(icon)dpx;
}

.u-section-2 .u-star-icon img {
  width: 100%%;
  height: 100%%;
  object-fit: contain;
}

.u-section-2 .u-star-label {
  font-size: 0.875rem;
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: lowercase;
}

/* ------------------------------------------------------------ the gallery */

.u-section-2 .u-gallery-1 {
  width: 1140px;
  height: 240px;
  margin: 82px auto 60px 0;
}

.u-section-2 .u-gallery-inner-1 {
  grid-template-columns: repeat(3, auto);
  grid-gap: 10px;
}

.u-section-2 .u-over-slide-1,
.u-section-2 .u-over-slide-2,
.u-section-2 .u-over-slide-3 {
  background-image: linear-gradient(0deg, rgba(0,0,0,0.2), rgba(0,0,0,0.2));
  padding: 20px;
}

.u-section-2 .u-gallery-item-2,
.u-section-2 .u-gallery-item-3 {
  margin-top: 0;
  margin-bottom: 0;
}

/* Breakpoints follow the framework's own layout grid: the two cells sit side
   by side down to 768px and stack at 767px and below (nicepage.css). The star
   box is sized to fit the cell it lands in at each step. */
@media (max-width: 1199px) {
  .u-section-2 .u-sheet-1 {
    min-height: 900px;
  }

  .u-section-2 .u-layout-cell-1 {
    min-height: %(cell1199)dpx;
  }

  .u-section-2 .u-layout-cell-2 {
    min-height: %(cell1199)dpx;
  }

  .u-section-2 .u-star-nav {
    width: %(box1199)dpx;
    height: %(box1199)dpx;
  }

  .u-section-2 a.u-star-node {
    width: %(node1199)dpx;
    height: %(node1199)dpx;
  }

  .u-section-2 .u-star-icon {
    width: %(icon1199)dpx;
    height: %(icon1199)dpx;
  }

  .u-section-2 .u-gallery-1 {
    width: 940px;
    height: 198px;
  }
}

/* Cells are still side by side here but only ~360px wide, so the star shrinks
   hard and the labels drop a step. */
@media (max-width: 991px) {
  .u-section-2 .u-sheet-1 {
    min-height: 1000px;
  }

  .u-section-2 .u-layout-cell-1 {
    min-height: %(cell991)dpx;
  }

  .u-section-2 .u-layout-cell-2 {
    min-height: %(cell991)dpx;
  }

  .u-section-2 .u-container-layout-2 {
    padding: 4px;
  }

  .u-section-2 .u-star-nav {
    width: %(box991)dpx;
    height: %(box991)dpx;
  }

  .u-section-2 a.u-star-node {
    width: %(node991)dpx;
    height: %(node991)dpx;
  }

  .u-section-2 .u-star-icon {
    width: %(icon991)dpx;
    height: %(icon991)dpx;
  }

  .u-section-2 .u-star-label {
    font-size: 0.6875rem;
  }

  .u-section-2 .u-gallery-1 {
    width: 720px;
    height: 455px;
  }

  .u-section-2 .u-gallery-inner-1 {
    grid-template-columns: repeat(2, auto);
  }
}

/* Cells stack: the star gets the full sheet width back. */
@media (max-width: 767px) {
  .u-section-2 .u-sheet-1 {
    min-height: 1900px;
  }

  .u-section-2 .u-container-layout-1 {
    padding-left: 10px;
    padding-right: 10px;
  }

  .u-section-2 .u-layout-cell-2 {
    min-height: %(cell767)dpx;
  }

  .u-section-2 .u-star-nav {
    width: %(box767)dpx;
    height: %(box767)dpx;
  }

  .u-section-2 a.u-star-node {
    width: %(node767)dpx;
    height: %(node767)dpx;
  }

  .u-section-2 .u-star-icon {
    width: %(icon767)dpx;
    height: %(icon767)dpx;
  }

  .u-section-2 .u-star-label {
    font-size: 0.8125rem;
  }

  .u-section-2 .u-gallery-1 {
    width: 540px;
    height: 1024px;
  }

  .u-section-2 .u-gallery-inner-1 {
    grid-template-columns: repeat(1, auto);
  }
}

/* Phones: a 340px sheet leaves no room for a star, so the buttons become a
   plain centred row. Once they are static the inline left/top is ignored. */
@media (max-width: 575px) {
  .u-section-2 .u-sheet-1 {
    min-height: 1750px;
  }

  .u-section-2 .u-layout-cell-2 {
    min-height: 100px;
  }

  .u-section-2 .u-star-nav {
    width: 100%%;
    height: auto;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 14px;
  }

  .u-section-2 .u-star-lines {
    display: none;
  }

  .u-section-2 a.u-star-node {
    position: static;
    transform: none;
    width: %(node575)dpx;
    height: %(node575)dpx;
  }

  .u-section-2 .u-star-icon {
    width: %(icon575)dpx;
    height: %(icon575)dpx;
  }

  .u-section-2 a.u-star-node:hover,
  .u-section-2 a.u-star-node:focus {
    transform: scale(1.08);
  }
}
""" % dict(
        {"accent": ACCENT, "box": STAR_BOX, "node": STAR_NODE},
        # box/node at each breakpoint, as a fraction of the desktop size
        **{k % bp: int(v * f) for bp, (bf, nf) in
           {1199: (0.85, 0.88), 991: (0.65, 0.62),
            767: (0.83, 0.86), 575: (0.80, 0.80)}.items()
           for k, v, f in (("box%d", STAR_BOX, bf), ("node%d", STAR_NODE, nf))},
        **{"icon": int(STAR_NODE * 0.34)},
        **{"icon%d" % bp: int(STAR_NODE * nf * 0.34) for bp, nf in
           {1199: 0.88, 991: 0.62, 767: 0.86, 575: 0.80}.items()},
        # the cell must clear the star box plus its 20px top margin and the
        # container padding, or the star pushes the cell taller than the row
        **{"cell%d" % bp: int(STAR_BOX * bf) + 20 + 2 * pad for bp, bf, pad in
           [(1199, 0.85, 10), (991, 0.65, 4), (767, 0.83, 10)]})


def gallery(items):
    """items: list of (image, heading, caption)"""
    inner = "".join(
        """<div class="u-effect-fade u-gallery-item%s">
              <div class="u-back-slide">
                <img class="u-back-image u-expanded" src="images/%s">
              </div>
              <div class="u-over-slide u-shading u-over-slide-%d">
                <h3 class="u-gallery-heading">%s</h3>
                <p class="u-gallery-text">%s</p>
              </div>
            </div>""" % ("" if i == 1 else " u-gallery-item-%d" % i, img, i, head_, cap)
        for i, (img, head_, cap) in enumerate(items, 1))
    return ('<div class="u-gallery u-layout-grid u-lightbox u-no-transition '
            'u-show-text-on-hover u-gallery-1">\n          '
            '<div class="u-gallery-inner u-gallery-inner-1">\n            %s\n'
            '          </div>\n        </div>' % inner)


# ---------------------------------------------------------------------- Home

HOME_BLURB = (
    'MAGNHIFFIC ("MeerKAT AGN HI Feeding &amp; Feedback Investigation Close-by") '
    'is a survey of 22 nearby Active Galactic Nuclei (AGN) performing sensitive '
    'observations of their neutral hydrogen (HI). MAGNHIFFIC investigates the '
    'typical column densities of the HI inflows and outflows involved in AGN '
    'feedback (10<sup>18-19</sup> cm<sup>-2</sup>) with kilo-parsec resolution, '
    'or better, using {MEERKAT} and ancillary observations of the multi-phase gas.')

HOME_MORE = (
    'MAGNHIFFIC probes part of the parameter space in AGN studies that has not '
    'yet been observed with any radio telescope. The {MEERKAT} observations provide '
    'at least 10 times deeper HI column density sensitivity than existing data, '
    'while improving the spatial and spectral resolution by at least a factor 3. '
    'MAGNHIFFIC will be the benchmark study of the distribution and kinematics of '
    'the HI in galaxies hosting an AGN.&nbsp;<br>The sample of nearby AGN is '
    'divided between radiative AGN and radio-jetted AGN and spans different '
    'energetic outputs, ages, host galaxies and environments.&nbsp;Combining the '
    'HI with the molecular and ionised gas, MAGNHIFFIC will infer the physical '
    'conditions and the total mass of the multi-phase outflows, and investigate '
    'their impact on the star formation of the host galaxies.&nbsp;')

# Home gallery strip. Swap in the three new science images once the files are in
# docs/images/ - build_home() warns and keeps the old strip until they are.
HOME_GALLERY = [
    "NGC3100_group_opt_hi.jpg",
    "cenA_axes.jpg",
    "NGC_1316_apod.jpg",
]
HOME_GALLERY_FALLBACK = [
    "2017_meerkat_01-1030x578.jpg",
    "2018-MeerKAT-4-1030x688.jpg",
    "fornaxAcontHI.jpg",
]

MEERKAT_LINK_ATTRS = ('class="u-active-none u-border-none u-btn u-button-link '
                      'u-button-style u-hover-none u-none u-text-palette-1-base '
                      'u-btn-%d" target="_blank"')


def meerkat(n):
    return ('<a href="https://www.sarao.ac.za/science/meerkat/" ' +
            (MEERKAT_LINK_ATTRS % n) + '>MeerKAT</a>')


# The five section buttons of the Home star. Order is the drawing order:
# node 1 sits at the top, the rest run clockwise.
HOME_STAR = [
    ("860766-ab3e1c93.png",  "The Team",   "A list of MAGNHIFFIC team members",
     "Team.html", "team"),
    ("1534069-91ba2df8.png", "The Sample", "The 22 AGN of MAGNHIFFIC and their properties",
     "Sample.html", "sample"),
    ("1087927-e922035e.png", "The Science", "The science behind MAGNHIFFIC",
     "Science.html", "science"),
    ("4675731-c24b0e52.png", "The Survey", "The MAGNHIFFIC survey and its observations",
     "Survey.html", "survey"),
    ("1822940-3e8f21d7.png", "The Data",   "A link to MAGNHIFFIC data (team only)",
     "Data.html", "data"),
]


def build_home():
    hero = """<section class="skrollable u-align-center u-clearfix u-image u-parallax u-section-1" id="carousel_c016" data-image-width="671" data-image-height="582">
      <div class="u-clearfix u-sheet u-sheet-1">
        <h1 class="u-hero-wordmark u-text u-text-body-alt-color u-text-1">MAGNHIFFIC</h1>
        <h5 class="u-hero-subtitle u-text u-text-body-alt-color u-text-2">%s</h5>
        <p class="u-text u-text-body-alt-color u-text-3"> %s<br>
        </p>
      </div>
    </section>""" % (WORDMARK_FULL, HOME_BLURB.replace("{MEERKAT}", meerkat(1)))

    imgs = HOME_GALLERY
    if not all(os.path.exists(os.path.join(SITE, "images", f)) for f in imgs):
        missing = [f for f in imgs
                   if not os.path.exists(os.path.join(SITE, "images", f))]
        print("  note: Home gallery falling back - missing %s" % ", ".join(missing))
        imgs = HOME_GALLERY_FALLBACK
    gal = gallery([(f, "", "") for f in imgs])

    # Section 2 of the old layout (the "Information on MAGNHIFFIC" card grid) is
    # gone: its five buttons now live in the star, in the right-hand cell here.
    more = """<section class="u-black u-clearfix u-section-2" id="carousel_d920">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-container-style u-layout-cell u-size-30 u-layout-cell-1">
                <div class="u-container-layout u-container-layout-1">
                  <h2 class="u-text u-text-1">More Info</h2>
                  <h6 class="u-custom-font u-text u-text-font u-text-2"> %s
                  </h6>
                </div>
              </div>
              <div class="u-container-style u-layout-cell u-size-30 u-layout-cell-2">
                <div class="u-container-layout u-container-layout-2">
                  %s
                </div>
              </div>
            </div>
          </div>
        </div>
        %s
      </div>
    </section>""" % (HOME_MORE.replace("{MEERKAT}", meerkat(1)),
                     star_nav(HOME_STAR), gal)

    desc = ("MAGNHIFFIC: a MeerKAT survey of neutral hydrogen in 22 nearby "
            "active galactic nuclei, probing AGN feeding and feedback.")
    html = page("Home", "Home.css", [hero, more], desc)
    write("Home.html", html)
    write("index.html", html)

    # ---- Home.css
    hero_font = ("\n  font-family: %s;" % HERO_FONT) if HERO_FONT else ""
    sec1 = """ .u-section-1 {
  background-image: url("images/fornaxAcontHI.jpg");
}

.u-section-1 .u-sheet-1 {
  min-height: 700px;
}

.u-section-1 .u-text-1 {
  font-size: %(hs)s;
  width: 894px;
  margin: 170px auto 0;%(hf)s
}

.u-section-1 .u-text-2 {
  font-size: 1.25rem;
  width: 894px;
  margin: 18px auto 0;
}

.u-section-1 .u-text-3 {
  font-size: 1.125rem;
  width: 894px;
  font-weight: normal;
  margin: 46px auto 60px;%(hf)s
}

.u-section-1 .u-btn-1 {
  background-image: none;
  padding: 0;
}

@media (max-width: 1199px) {
   .u-section-1 {
    background-position: 50%% 50%%;
  }

  .u-section-1 .u-sheet-1 {
    min-height: 620px;
  }
}

@media (max-width: 991px) {
  .u-section-1 .u-sheet-1 {
    min-height: 560px;
  }

  .u-section-1 .u-text-1 {
    width: 720px;
    font-size: 3.5rem;
    margin-top: 140px;
  }

  .u-section-1 .u-text-2 {
    width: 720px;
  }

  .u-section-1 .u-text-3 {
    width: 720px;
  }
}

@media (max-width: 767px) {
  .u-section-1 .u-sheet-1 {
    min-height: 520px;
  }

  .u-section-1 .u-text-1 {
    width: 540px;
    font-size: 2.75rem;
    margin-top: 120px;
  }

  .u-section-1 .u-text-2 {
    width: 540px;
    font-size: 1.125rem;
  }

  .u-section-1 .u-text-3 {
    width: 540px;
  }
}

@media (max-width: 575px) {
  .u-section-1 .u-sheet-1 {
    min-height: 480px;
  }

  .u-section-1 .u-text-1 {
    width: 340px;
    font-size: 2rem;
    letter-spacing: 2px;
    margin-top: 100px;
  }

  .u-section-1 .u-text-2 {
    width: 340px;
    font-size: 1rem;
  }

  .u-section-1 .u-text-3 {
    width: 340px;
  }
}""" % {"hf": hero_font, "hs": THEME["hero_size"]}
    write_css("Home.css", sec1 + home_sec2_css())


# ------------------------------------------------------------------- helpers

def link(href, label, n, external=False, title=None):
    tgt = ' target="_blank"' if external else ""
    ttl = ' title="%s"' % title if title else ""
    return ('<a%s href="%s" class="u-active-none u-border-none u-btn u-button-style '
            'u-hover-none u-none u-text-palette-1-base u-btn-%d"%s>%s</a>'
            % (ttl, href, n, tgt, label))


def bullets(items, n=1):
    lis = "".join(
        '\n                    <li>\n                      <div class="u-list-icon">\n'
        '                        <div>\u25cb</div>\n                      </div>%s\n'
        '                    </li>' % it for it in items)
    return ('<ul class="u-custom-list u-text u-text-default u-text-%d">%s\n'
            '                  </ul>' % (n, lis))


def two_col(sec_id, sec_no, left, right, extra_sec_class="", left_class="",
            right_class="u-align-center"):
    """Template's standard alternating text/image band."""
    return """<section class="u-black u-clearfix %su-section-%d" id="%s">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="%su-container-style u-layout-cell u-size-30 u-layout-cell-1">
                <div class="u-container-layout u-container-layout-1">
                  %s
                </div>
              </div>
              <div class="%s u-container-style u-layout-cell u-shape-rectangle u-size-30 u-layout-cell-2">
                <div class="u-container-layout u-valign-middle u-container-layout-2">
                  %s
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>""" % (extra_sec_class, sec_no, sec_id, left_class, left,
                     right_class, right)


def banner(sec_id, sec_no, heading, sub="", align="u-align-center"):
    """Single-column heading band used at the top of interior pages."""
    body = '<h2 class="u-text u-text-1">%s</h2>' % heading
    if sub:
        body += '\n        <p class="u-align-left u-text u-text-2">%s</p>' % sub
    return """<section class="%s u-black u-clearfix u-section-%d" id="%s">
      <div class="u-clearfix u-sheet u-sheet-1">
        %s
      </div>
    </section>""" % (align, sec_no, sec_id, body)


def circle_img(image, w, h, n=1):
    return ('<div class="u-image u-image-circle u-image-%d" data-image-width="%d" '
            'data-image-height="%d"></div>' % (n, w, h))


def plain_img(image, w, h, n=1, extra="u-image-circle u-preserve-proportions"):
    return ('<img class="u-image %s u-image-%d" src="images/%s" alt="" '
            'data-image-width="%d" data-image-height="%d">' % (extra, n, image, w, h))


# ------------------------------------------------------------------- Science

SCI_1 = (
    'MAGNHIFFIC will probe a part of parameter space in AGN studies that has not '
    'yet been observed with any radio telescope, enabling us to study the typical '
    'column densities of the neutral hydrogen (HI) inflows and outflows involved '
    'in AGN feeding and feedback (10<span style="font-size: 0.75rem;">18\u201319'
    '</span>&nbsp;cm<span style="font-size: 0.75rem;">\u22122</span>) with '
    'kilo-parsec resolution, or better.&nbsp;<br>The {MEERKAT} observations '
    'provide at least 10 times deeper HI column density sensitivity than existing '
    'data, while improving the spatial and spectral resolution by at least a '
    'factor 3. MAGNHIFFIC will be the benchmark study of the distribution and '
    'kinematics of the HI in galaxies hosting an AGN.&nbsp;')

SCI_2 = (
    'MAGNHIFFIC is a ground-breaking project that for the first time will study '
    'the process of feeding and feedback in 22 nearby AGN with different '
    'energetic outputs, different ages, in different hosts and in different '
    'environments. The sample is divided between radiative AGN (10 sources) and '
    'radio-jetted AGN (12 sources). Sources have been selected where sensitive '
    'observations of the molecular and ionised gas showed indications of on-going '
    'feeding and/or feedback (e.g. Maccagni et al. 2018, Ruffa et al. 2019a, '
    'Mingozzi et al. 2018, Venturi et al. 2020). The full sample is described '
    '{SAMPLE}.&nbsp;<br>Combining the HI with the molecular and ionised gas '
    'observations, MAGNHIFFIC will infer the physical conditions and the total '
    'mass of the multi-phase outflows, and investigate their impact on the star '
    'formation of the host galaxies. From the timescales of the interaction '
    'events, and by quantifying the effects of turbulence on the multi-phase IGM '
    'and ISM, MAGNHIFFIC will identify the AGN accretion mechanisms and study how '
    'they sustain recurrent nuclear activity.&nbsp;')

SCI_PROJECTS = [
    ("Cold gas accretion in radiative mode AGN and its effects on star formation",
     ["how is gas funneled from the IGM to the centre of radiative AGN?",
      "over which timescales can nuclear activity be sustained?",
      "to which extent are AGN outflows effective in unsettling the ISM and "
      "changing the star formation?"]),
    ("The role of cold gas in the duty-cycle of AGN",
     ["what is the origin of the cold gas found in the circum-nuclear regions of "
      "jetted AGN?",
      "how do radio jets modify the cold ISM from the circum-nuclear to the "
      "inter-galactic scales?",
      "which mechanisms sustain recursive AGN activity, and over which "
      "timescales?"]),
    ("MAGNHIFFIC results within the theoretical framework of AGN feeding and "
     "feedback",
     ["provide a detailed description of the expansion history of radiative winds "
      "and jets in radio-loud AGN",
      "determine which observational constraints identify and describe the "
      "phenomena of feeding and feedback in radiative AGN",
      "implement in hydrodynamical simulations the physical and kinematical "
      "conditions of the multi-phase ISM involved in feeding and feedback, to "
      "understand the duty-cycle of AGN"]),
]


def build_science():
    left1 = ('<h2 class="u-text u-text-1">The Science</h2>\n'
             '                  <p class="u-align-justify u-text u-text-2"> %s\n'
             '                  </p>' % SCI_1.replace("{MEERKAT}", meerkat(1)))
    s1 = two_col("carousel_0fe1", 1, left1,
                 circle_img("beamNhiwhiteNo.jpg", 730, 730, 1))

    right2 = ('<p class="u-align-justify u-text u-text-1"> %s\n'
              '                  </p>'
              % SCI_2.replace("{SAMPLE}", link("Sample.html", "here", 1)))
    s2 = two_col("carousel_544c", 2,
                 plain_img("fornaxAcontHI.jpg", 671, 582, 1),
                 right2, left_class="", right_class="u-align-justify")

    # projects band
    proj_html = ""
    for i, (title, qs) in enumerate(SCI_PROJECTS, 1):
        intro = ("This project will combine the results of the MAGNHIFFIC "
                 "observations with hydrodynamical simulations to:"
                 if i == 3 else "This project will investigate:")
        proj_html += """
        <h5 class="u-text u-text-%d">%d. %s</h5>
        <p class="u-align-left u-text u-text-%d">%s</p>
        %s""" % (3 * i, i, title, 3 * i + 1, intro, bullets(qs, 3 * i + 2))

    s3 = """<section class="u-black u-clearfix u-section-3" id="sec-d121">
      <div class="u-clearfix u-sheet u-sheet-1">
        <h2 class="u-text u-text-1">MAGNHIFFIC projects</h2>
        <h5 class="u-text u-text-2">MAGNHIFFIC is organised around three complementary projects</h5>%s
      </div>
    </section>""" % proj_html

    desc = ("The science of MAGNHIFFIC: HI inflows and outflows, AGN duty cycles "
            "and multi-phase feedback in 22 nearby active galaxies.")
    write("Science.html", page("Science", "Science.css", [s1, s2, s3], desc))

    sec1 = """ .u-section-1 {
  background-image: none;
}

.u-section-1 .u-sheet-1 {
  min-height: 664px;
}

.u-section-1 .u-layout-wrap-1 {
  margin-top: 60px;
  margin-bottom: 60px;
}

.u-section-1 .u-layout-cell-1 {
  min-height: 484px;
}

.u-section-1 .u-container-layout-1 {
  padding: 30px;
}

.u-section-1 .u-text-1 {
  font-weight: 700;
  font-size: 2.25rem;
  margin: 0;
}

.u-section-1 .u-text-2 {
  line-height: 1.5;
  margin: 20px 0 0;
}

.u-section-1 .u-btn-1 {
  background-image: none;
  padding: 0;
}

.u-section-1 .u-layout-cell-2 {
  min-height: 484px;
}

.u-section-1 .u-container-layout-2 {
  padding: 20px;
}

.u-section-1 .u-image-1 {
  width: 420px;
  height: 420px;
  background-image: url("images/beamNhiwhiteNo.jpg");
  background-position: 50% 50%;
  margin: 0 auto;
}

@media (max-width: 1199px) {
  .u-section-1 .u-sheet-1 {
    min-height: 546px;
  }

  .u-section-1 .u-layout-cell-1 {
    min-height: 400px;
  }

  .u-section-1 .u-layout-cell-2 {
    min-height: 400px;
  }

  .u-section-1 .u-image-1 {
    width: 360px;
    height: 360px;
  }
}

@media (max-width: 991px) {
  .u-section-1 .u-sheet-1 {
    min-height: 442px;
  }

  .u-section-1 .u-layout-cell-1 {
    min-height: 324px;
  }

  .u-section-1 .u-layout-cell-2 {
    min-height: 324px;
  }

  .u-section-1 .u-image-1 {
    width: 284px;
    height: 284px;
  }
}

@media (max-width: 767px) {
  .u-section-1 .u-sheet-1 {
    min-height: 662px;
  }

  .u-section-1 .u-layout-cell-1 {
    min-height: 100px;
  }

  .u-section-1 .u-container-layout-1 {
    padding-left: 10px;
    padding-right: 10px;
  }

  .u-section-1 .u-layout-cell-2 {
    min-height: 100px;
  }

  .u-section-1 .u-image-1 {
    width: 340px;
    height: 340px;
  }
}

@media (max-width: 575px) {
  .u-section-1 .u-sheet-1 {
    min-height: 600px;
  }

  .u-section-1 .u-image-1 {
    width: 296px;
    height: 296px;
  }
}"""

    sec2 = """ .u-section-2 {
  background-image: none;
}

.u-section-2 .u-sheet-1 {
  min-height: 620px;
}

.u-section-2 .u-layout-wrap-1 {
  margin-top: 20px;
  margin-bottom: 60px;
}

.u-section-2 .u-layout-cell-1 {
  min-height: 484px;
}

.u-section-2 .u-container-layout-1 {
  padding: 20px;
}

.u-section-2 .u-image-1 {
  width: 420px;
  height: 364px;
  margin: 30px auto 0;
}

.u-section-2 .u-layout-cell-2 {
  min-height: 484px;
}

.u-section-2 .u-container-layout-2 {
  padding: 30px;
}

.u-section-2 .u-text-1 {
  line-height: 1.5;
  margin: 0;
}

.u-section-2 .u-btn-1 {
  background-image: none;
  padding: 0;
}

@media (max-width: 1199px) {
  .u-section-2 .u-sheet-1 {
    min-height: 546px;
  }

  .u-section-2 .u-layout-cell-1 {
    min-height: 400px;
  }

  .u-section-2 .u-image-1 {
    width: 360px;
    height: 312px;
  }

  .u-section-2 .u-layout-cell-2 {
    min-height: 400px;
  }
}

@media (max-width: 991px) {
  .u-section-2 .u-sheet-1 {
    min-height: 470px;
  }

  .u-section-2 .u-layout-cell-1 {
    min-height: 324px;
  }

  .u-section-2 .u-image-1 {
    width: 284px;
    height: 246px;
  }

  .u-section-2 .u-layout-cell-2 {
    min-height: 324px;
  }
}

@media (max-width: 767px) {
  .u-section-2 .u-sheet-1 {
    min-height: 700px;
  }

  .u-section-2 .u-layout-cell-1 {
    min-height: 100px;
  }

  .u-section-2 .u-image-1 {
    width: 340px;
    height: 295px;
  }

  .u-section-2 .u-layout-cell-2 {
    min-height: 100px;
  }

  .u-section-2 .u-container-layout-2 {
    padding-left: 10px;
    padding-right: 10px;
  }
}

@media (max-width: 575px) {
  .u-section-2 .u-image-1 {
    width: 296px;
    height: 257px;
  }
}"""

    sec3 = """ .u-section-3 {
  background-image: none;
}

.u-section-3 .u-sheet-1 {
  min-height: 1200px;
}

.u-section-3 .u-text-1 {
  font-weight: 700;
  font-size: 2.25rem;
  margin: 60px auto 0;
}

.u-section-3 .u-text-2 {
  font-weight: 300;
  margin: 14px auto 0;
}

.u-section-3 .u-text-3,
.u-section-3 .u-text-6,
.u-section-3 .u-text-9 {
  font-weight: 700;
  font-size: 1.25rem;
  margin: 46px 0 0;
}

.u-section-3 .u-text-4,
.u-section-3 .u-text-7,
.u-section-3 .u-text-10 {
  margin: 14px 0 0;
}

.u-section-3 .u-text-5,
.u-section-3 .u-text-8,
.u-section-3 .u-text-11 {
  line-height: 1.6;
  margin: 12px 0 0 20px;
}

@media (max-width: 1199px) {
  .u-section-3 .u-sheet-1 {
    min-height: 1240px;
  }
}

@media (max-width: 991px) {
  .u-section-3 .u-sheet-1 {
    min-height: 1340px;
  }
}

@media (max-width: 767px) {
  .u-section-3 .u-sheet-1 {
    min-height: 1520px;
  }

  .u-section-3 .u-text-1 {
    font-size: 1.875rem;
  }
}

@media (max-width: 575px) {
  .u-section-3 .u-sheet-1 {
    min-height: 1900px;
  }
}"""
    write_css("Science.css", sec1 + "\n\n" + sec2 + "\n\n" + sec3)


# -------------------------------------------------------------------- Survey

SURVEY_1 = (
    'MAGNHIFFIC observes a total of 22 nearby active galaxies with {MEERKAT}, '
    'spanning different energetic outputs, different ages, different host '
    'morphologies and different environments. The sample is divided between '
    'radiative AGN (10 sources) and radio-jetted AGN (12 sources), and is '
    'described {SAMPLE}.&nbsp;<br>'
    '<br>The observations reach HI column densities of '
    '10<span style="font-size: 0.875rem;">18\u201319</span>&nbsp;cm'
    '<span style="font-size: 0.875rem;">\u22122</span> at kilo-parsec resolution '
    'or better \u2014 at least 10 times deeper in column density than existing HI '
    'data of these systems, with spatial and spectral resolution improved by at '
    'least a factor 3. This is a part of parameter space in AGN studies that has '
    'not yet been observed with any radio telescope.&nbsp;<br>'
    '<br>The figure on this page shows the HI column density sensitivity reached '
    'by MAGNHIFFIC as a function of angular resolution, compared with existing HI '
    'observations of AGN hosts.&nbsp;')

SURVEY_2 = (
    'MAGNHIFFIC combines the MeerKAT HI observations with ancillary observations '
    'of the molecular and ionised gas in the same targets, so that the physical '
    'conditions and the total mass of the multi-phase inflows and outflows can be '
    'measured consistently across all gas phases. From the timescales of the '
    'interaction events, and by quantifying the effects of turbulence on the '
    'multi-phase IGM and ISM, MAGNHIFFIC will identify the AGN accretion '
    'mechanisms and study how they sustain recurrent nuclear activity.&nbsp;')


def build_survey():
    left = ('<h2 class="u-text u-text-1">The Survey</h2>\n'
            '                  <p class="u-align-justify u-text u-text-2"> %s\n'
            '                  </p>'
            % SURVEY_1.replace("{MEERKAT}", meerkat(1))
                     .replace("{SAMPLE}", link("Sample.html", "here", 2)))
    right = ('<img class="u-image u-image-1" src="images/beamNhiwhiteNo.jpg" '
             'alt="" data-image-width="730" data-image-height="730">')
    s1 = """<section class="u-black u-clearfix u-section-1" id="carousel_0fe1">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-clearfix u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-container-style u-layout-cell u-size-30 u-layout-cell-1">
                <div class="u-container-layout u-container-layout-1">
                  %s
                </div>
              </div>
              <div class="u-align-center u-container-style u-layout-cell u-shape-rectangle u-size-30 u-layout-cell-2">
                <div class="u-container-layout u-container-layout-2">
                  %s
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>""" % (left, right)

    s2 = """<section class="u-black u-clearfix u-section-2" id="carousel_544c">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-container-style u-image u-layout-cell u-size-30 u-image-1" data-image-width="1030" data-image-height="578">
                <div class="u-container-layout u-valign-middle u-container-layout-1"></div>
              </div>
              <div class="u-align-justify u-container-style u-layout-cell u-size-30 u-layout-cell-2">
                <div class="u-container-layout u-valign-middle u-container-layout-2">
                  <h3 class="u-text u-text-1">Multi-phase gas</h3>
                  <p class="u-text u-text-2"> %s
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>""" % SURVEY_2

    desc = ("The MAGNHIFFIC survey: MeerKAT HI observations of 22 nearby AGN, "
            "reaching 10^18-19 cm^-2 at kpc resolution.")
    write("Survey.html", page("Survey", "Survey.css", [s1, s2], desc))
    write_css("Survey.css", tpl_css("_survey_sec1.css") + "\n\n" +
              tpl_css("_survey_sec2.css"))


# -------------------------------------------------------------------- Sample

SAMPLE_INTRO = (
    'The table below lists the {N} active galaxies observed by MAGNHIFFIC. An '
    '{ASCII} of this table is also available. Each object name links to its entry '
    'in the {NED}.&nbsp;<br>'
    '<br>Column densities and distances assume H'
    '<span style="font-size: 0.75rem;">0</span>&nbsp;=&nbsp;67.8 km s'
    '<span style="font-size: 0.75rem;">\u22121</span> Mpc'
    '<span style="font-size: 0.75rem;">\u22121</span>. AGN types distinguish '
    'radiative-mode (Seyfert) sources from radio-jetted (RL) sources; the '
    'environment column gives the group or cluster membership of the host.&nbsp;'
    '<br><br>{GROUPS} Rows are grouped by subsample and, within each group, '
    'sorted by increasing luminosity distance. {LEGEND}')

# Subsample groups, in the order they appear in the table.  The `key` must match
# the `subsample` column of sample_table.csv; any row whose value is not one of
# these keys falls into the last group.  A group with no rows is not rendered.
SAMPLE_GROUPS = [
    ("magnum", "MAGNUM subsample", "Venturi et al. (2017)",
     "https://doi.org/10.3389/fspas.2017.00046"),
    ("radio_loud", "Radio-loud subsample", "Ruffa et al. (2019)",
     "https://ui.adsabs.harvard.edu/abs/2019MNRAS.484.4239R/abstract"),
    ("other", "All other sources", None, None),
]


def group_rows(rows):
    """Split rows into (key, label, ref, url, rows) tuples in SAMPLE_GROUPS
    order, each sorted by ascending luminosity distance (blank distance last).
    Non-empty groups only."""
    keys = [g[0] for g in SAMPLE_GROUPS]
    out = []
    for key, label, ref, url in SAMPLE_GROUPS:
        if key == keys[-1]:      # last group also collects unknown values
            g = [r for r in rows if r.get("subsample", "") not in keys[:-1]]
        else:
            g = [r for r in rows if r.get("subsample", "") == key]

        def dist(r):
            try:
                return float(r["dl_mpc"])
            except (TypeError, ValueError):
                return float("inf")
        if g:
            out.append((key, label, ref, url, sorted(g, key=dist)))
    return out


def sample_groups_sentence(groups):
    """One sentence describing the subsample structure actually rendered, so
    the prose cannot drift from the table when rows are reassigned."""
    keys = [k for k, _l, _r, _u, _g in groups]
    main = [k for k in keys if k != "other"]
    if len(main) == 2:
        txt = ("The sample is made of two main subsamples &mdash; the MAGNUM "
               "galaxies and the radio-loud sources")
    else:
        txt = ("The sample is made of %d subsample%s"
               % (len(main), "" if len(main) == 1 else "s"))
    if "other" in keys:
        txt += " &mdash; plus additional sources."
    else:
        txt += "."
    return txt


def sample_legend(groups):
    """Inline colour key, one swatch per rendered group."""
    items = ['<span class="u-sample-key u-sample-key-%s"></span>&nbsp;%s '
             '(%d)' % (key, label, len(g)) for key, label, _r, _u, g in groups]
    return "&nbsp;&nbsp;&nbsp;".join(items)


def sample_table(groups):
    """groups: output of group_rows() — (key, label, ref, url, rows) tuples.
    Each row is a dict with name/ra/dec/dl_mpc/gal_type/agn_type/environment/
    ned_url/subsample.  Every group gets a coloured label row, and its data
    rows carry the group's class so theme.css can tint them."""
    head_cells = ["Name", "RA [J2000]", "Dec [J2000]",
                  "D<span style=\"font-size: 0.75rem;\">L</span> [Mpc]",
                  "Galaxy type", "AGN type", "Environment"]
    ths = "".join('\n                <th class="u-border-1 u-border-grey-30 '
                  'u-table-cell">%s</th>' % c for c in head_cells)
    trs = ""
    for key, label, ref, url, grp in groups:
        head = label
        if ref:
            head += " &mdash; " + ('<a href="%s" target="_blank" '
                                   'class="u-sample-ref">%s</a>' % (url, ref))
        head += ' <span class="u-sample-count">(%d objects)</span>' % len(grp)
        trs += ('\n              <tr class="u-sample-group u-sample-%s">'
                '\n                <td class="u-border-1 u-border-grey-30 '
                'u-table-cell" colspan="%d">%s</td>\n              </tr>'
                % (key, len(head_cells), head))
        for r in grp:
            nm = r["name"]
            if r.get("ned_url"):
                nm = ('<a href="%s" target="_blank" class="u-active-none '
                      'u-border-none u-btn u-button-link u-button-style '
                      'u-hover-none u-none u-text-hover-palette-1-base '
                      'u-text-white">%s</a>' % (r["ned_url"], r["name"]))
            cells = [nm, r["ra"], r["dec"], r["dl_mpc"] or "\u2013",
                     r["gal_type"], r["agn_type"], r["environment"]]
            tds = "".join('\n                <td class="u-border-1 '
                          'u-border-grey-30 u-table-cell">%s</td>' % c
                          for c in cells)
            trs += ('\n              <tr class="u-sample-%s" '
                    'style="height: 40px;">%s\n              </tr>' % (key, tds))
    return """<table class="u-table-entity u-table-entity-1">
            <colgroup>
              <col width="15%%"><col width="12%%"><col width="12%%"><col width="8%%"><col width="9%%"><col width="24%%"><col width="20%%">
            </colgroup>
            <thead class="u-black u-table-header u-table-header-1">
              <tr style="height: 46px;">%s
              </tr>
            </thead>
            <tbody class="u-align-center u-table-body">%s
            </tbody>
          </table>""" % (ths, trs)


def write_sample_ascii(groups, total):
    """Plain-text export, same grouping and ordering as the table."""
    w = (18, 12, 13, 6, 6, 34)
    out = ["# MAGNHIFFIC sample (%d objects).  H0 = 67.8 km/s/Mpc" % total,
           "# grouped by subsample, then sorted by ascending distance",
           "# %-*s%-*s%-*s%*s %-*s %-*s%s"
           % (w[0] - 2, "name", w[1], "ra_j2000", w[2], "dec_j2000",
              w[3], "dl_mpc", w[4], "gtype", w[5], "agn_type", "environment")]
    for _k, label, ref, _u, grp in groups:
        out.append("#")
        out.append("# %s%s (%d objects)"
                   % (label, " -- " + ref if ref else "", len(grp)))
        for r in grp:
            out.append("  %-*s%-*s%-*s%*s %-*s %-*s%s"
                       % (w[0], r["name"], w[1], r["ra"], w[2], r["dec"],
                          w[3], r["dl_mpc"] or "-", w[4], r["gal_type"],
                          w[5], r["agn_type"], r["environment"]))
    d = os.path.join(SITE, "files")
    if not os.path.isdir(d):
        os.makedirs(d)
    with open(os.path.join(d, "magnhiffic_sample.txt"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


def build_sample(rows):
    groups = group_rows(rows)
    write_sample_ascii(groups, len(rows))
    intro = (SAMPLE_INTRO
             .replace("{N}", str(len(rows)))
             .replace("{GROUPS}", sample_groups_sentence(groups))
             .replace("{LEGEND}", sample_legend(groups))
             .replace("{ASCII}", link("files/magnhiffic_sample.txt",
                                      "ascii version", 1, external=True))
             .replace("{NED}", link("https://ned.ipac.caltech.edu/",
                                    "NASA/IPAC Extragalactic Database", 2,
                                    external=True)))
    s1 = """<section class="u-align-center u-black u-clearfix u-section-1" id="carousel_ddcf">
      <div class="u-clearfix u-sheet u-sheet-1">
        <h2 class="u-align-left u-text u-text-1">Sample List</h2>
        <p class="u-align-left u-text u-text-2">%s</p>
      </div>
    </section>""" % intro

    s2 = """<section class="u-align-center u-black u-clearfix u-section-2" id="sec-3fcc">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-expanded-width u-table u-table-1">
          %s
        </div>
      </div>
    </section>""" % sample_table(groups)

    desc = ("The MAGNHIFFIC sample: %d nearby AGN with coordinates, distances, "
            "host morphology, AGN classification and environment." % len(rows))
    write("Sample.html", page("Sample", "Sample.css", [s1, s2], desc))

    sec2 = """ .u-section-2 {
  background-image: none;
}

.u-section-2 .u-sheet-1 {
  min-height: 1400px;
}

.u-section-2 .u-table-1 {
  margin: 20px auto 60px;
}

.u-section-2 .u-table-entity-1 {
  font-size: 0.875rem;
}

.u-section-2 .u-table-header-1 {
  font-weight: 700;
}

@media (max-width: 1199px) {
  .u-section-2 .u-sheet-1 {
    min-height: 1300px;
  }

  .u-section-2 .u-table-entity-1 {
    font-size: 0.8125rem;
  }
}

@media (max-width: 991px) {
  .u-section-2 .u-sheet-1 {
    min-height: 1240px;
  }

  .u-section-2 .u-table-entity-1 {
    font-size: 0.75rem;
  }
}

@media (max-width: 767px) {
  .u-section-2 .u-sheet-1 {
    min-height: 1240px;
  }

  .u-section-2 .u-table-1 {
    overflow-x: auto;
  }

  .u-section-2 .u-table-entity-1 {
    font-size: 0.6875rem;
    min-width: 640px;
  }
}"""
    write_css("Sample.css", tpl_css("_sample_sec1.css") + "\n\n" + sec2)


# -------------------------------------------------------------- Publications

# NOTE FOR REVIEW: MAGNHIFFIC has no published survey papers yet in the material
# supplied. The entries below are the sample-selection references cited on the
# Science page, listed as "background papers". Add MAGNHIFFIC papers here as they
# appear; the page renders any number of entries.
PUB_BACKGROUND = [
    ("Maccagni et al. (2018)",
     "The flickering nuclear activity of Fornax A",
     "https://ui.adsabs.harvard.edu/abs/2020A%26A...634A...9M/abstract"),
    ("Mingozzi et al. (2018)",
     "AGN-driven outflows and the AGN feedback efficiency in nearby galaxies",
     "https://ui.adsabs.harvard.edu/abs/2019A%26A...622A.146M/abstract"),
    ("Ruffa et al. (2019a)",
     "The AGN fuelling/feedback cycle in nearby radio galaxies",
     "https://ui.adsabs.harvard.edu/abs/2019MNRAS.484.4239R/abstract"),
    ("Venturi et al. (2020)",
     "MAGNUM survey: compact jets causing large turmoil in galaxies",
     "https://ui.adsabs.harvard.edu/abs/2021A%26A...648A..17V/abstract"),
]


def build_publications():
    entries = ""
    for i, (auth, title, url) in enumerate(PUB_BACKGROUND, 1):
        entries += ('\n                    %s<br>%s<br>%s<br>\n                    <br>'
                    % (title, auth, link(url, url, i, external=True)))

    s1 = """<section class="u-black u-clearfix u-section-1" id="carousel_0fe1">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-1">
                <div class="u-container-layout u-container-layout-1">
                  <h2 class="u-text u-text-1">Publications</h2>
                  <h4 class="u-align-center u-text u-text-2">Survey papers</h4>
                  <p class="u-align-justify u-text u-text-3">The MAGNHIFFIC survey description paper and the first results papers are in preparation. This page will list all papers published or accepted using MAGNHIFFIC data.<br>
                    <br>
                  </p>
                  <h4 class="u-align-center u-text u-text-4">Background papers</h4>
                  <p class="u-align-justify u-text u-text-5">The papers below present the molecular and ionised gas observations on which the MAGNHIFFIC sample selection is based.<br>
                    <br>
                  </p>
                  <p class="u-align-left u-text u-text-6">%s
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>""" % entries

    desc = "Publications of the MAGNHIFFIC survey and the background papers behind its sample selection."
    write("Publications.html", page("Publications", "Publications.css", [s1], desc))

    sec1 = """ .u-section-1 {
  background-image: none;
}

.u-section-1 .u-sheet-1 {
  min-height: 900px;
}

.u-section-1 .u-layout-wrap-1 {
  margin-top: 60px;
  margin-bottom: 60px;
}

.u-section-1 .u-layout-cell-1 {
  min-height: 780px;
}

.u-section-1 .u-container-layout-1 {
  padding: 30px;
}

.u-section-1 .u-text-1 {
  font-weight: 700;
  font-size: 2.25rem;
  margin: 0;
}

.u-section-1 .u-text-2,
.u-section-1 .u-text-4 {
  font-weight: 700;
  margin: 34px auto 0;
}

.u-section-1 .u-text-3,
.u-section-1 .u-text-5 {
  margin: 14px 0 0;
}

.u-section-1 .u-text-6 {
  line-height: 1.6;
  margin: 6px 0 0;
}

.u-section-1 .u-btn-1,
.u-section-1 .u-btn-2,
.u-section-1 .u-btn-3,
.u-section-1 .u-btn-4 {
  background-image: none;
  padding: 0;
  word-break: break-all;
}

@media (max-width: 1199px) {
  .u-section-1 .u-sheet-1 {
    min-height: 940px;
  }
}

@media (max-width: 991px) {
  .u-section-1 .u-sheet-1 {
    min-height: 1000px;
  }
}

@media (max-width: 767px) {
  .u-section-1 .u-sheet-1 {
    min-height: 1120px;
  }

  .u-section-1 .u-container-layout-1 {
    padding-left: 10px;
    padding-right: 10px;
  }
}

@media (max-width: 575px) {
  .u-section-1 .u-sheet-1 {
    min-height: 1320px;
  }
}"""
    write_css("Publications.css", sec1)


# ---------------------------------------------------------------------- Team

# NOTE FOR REVIEW: only the PI is known from the material supplied. Add team
# members as "Name, Institute, Country" strings; the page renders any number.
TEAM = [
    "Filippo M. Maccagni (PI), INAF \u2013 Osservatorio Astronomico di Cagliari, Italy",
    "[Add team member: Name, Institute, Country]",
    "[Add team member: Name, Institute, Country]",
]


def build_team():
    s1 = banner("carousel_ddcf", 1, "Team",
                "The list below gives the MAGNHIFFIC team members.")
    s2 = """<section class="u-align-center u-black u-clearfix u-section-2" id="sec-2c09">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-align-left u-container-style u-layout-cell u-left-cell u-size-60 u-layout-cell-1">
                <div class="u-container-layout u-valign-top u-container-layout-1">
                  %s
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>""" % bullets(TEAM, 1)

    desc = "The MAGNHIFFIC team."
    write("Team.html", page("Team", "Team.css", [s1, s2], desc))
    write_css("Team.css", tpl_css("_team_sec1.css") + "\n\n" +
              tpl_css("_team_sec2.css"))


# ------------------------------------------------------- Public Data Release

def build_public_data():
    s1 = """<section class="u-black u-clearfix u-section-1" id="carousel_0fe1">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-1">
                <div class="u-container-layout u-container-layout-1">
                  <h2 class="u-text u-text-1">Public Data Releases</h2>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>"""

    body = (
        'MAGNHIFFIC observations are on-going. Public data releases \u2014 HI data '
        'cubes and moment maps of the survey targets \u2014 will be announced on this '
        'page as they become available, together with the release documentation '
        'describing the resolutions, sensitivities and reduction strategy '
        'used.&nbsp;<br>'
        '<br>Team members can access the internal data products via the '
        '%s page.&nbsp;<br>'
        '<br>[Placeholder \u2014 replace with the first public release description '
        'and repository link when available; see REVIEW_NOTES.md]&nbsp;'
        % link("Data.html", "Team Data", 1))

    s2 = """<section class="u-black u-clearfix u-section-2" id="carousel_1c2e">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-1">
                <div class="u-container-layout u-valign-top u-container-layout-1">
                  <h4 class="u-align-center u-text u-text-1">Data releases</h4>
                  <p class="u-align-justify u-text u-text-default u-text-2"> %s
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>""" % body

    s3 = """<section class="u-align-center u-black u-clearfix u-section-3" id="sec-9d61">
      <div class="u-clearfix u-sheet u-sheet-1">
        <img class="u-image u-image-contain u-image-default u-preserve-proportions u-image-1" src="images/fornaxAcontHI.jpg" alt="" data-image-width="671" data-image-height="582">
        <p class="u-align-center u-small-text u-text u-text-variant u-text-1">Fornax A: MeerKAT HI (contours) on the radio continuum.</p>
      </div>
    </section>"""

    desc = "MAGNHIFFIC public data releases: HI data cubes and moment maps."
    write("Public-Data-Release.html",
          page("Public Data Release", "Public-Data-Release.css",
               [s1, s2, s3], desc))
    write_css("Public-Data-Release.css",
              tpl_css("_public_data_release_sec1.css") + "\n\n" +
              tpl_css("_public_data_release_sec2.css") + "\n\n" +
              """ .u-section-3 {
  background-image: none;
}

.u-section-3 .u-sheet-1 {
  min-height: 640px;
}

.u-section-3 .u-image-1 {
  width: 520px;
  margin: 40px auto 0;
}

.u-section-3 .u-text-1 {
  margin: 14px auto 40px;
}

@media (max-width: 1199px) {
  .u-section-3 .u-sheet-1 {
    min-height: 560px;
  }

  .u-section-3 .u-image-1 {
    width: 440px;
  }
}

@media (max-width: 991px) {
  .u-section-3 .u-sheet-1 {
    min-height: 480px;
  }

  .u-section-3 .u-image-1 {
    width: 360px;
  }
}

@media (max-width: 767px) {
  .u-section-3 .u-sheet-1 {
    min-height: 420px;
  }

  .u-section-3 .u-image-1 {
    width: 300px;
  }
}

@media (max-width: 575px) {
  .u-section-3 .u-image-1 {
    width: 260px;
  }
}""")


# ------------------------------------------------------------------- Contact

def build_contact():
    s1 = """<section class="u-align-center u-black u-clearfix u-section-1" id="sec-c819">
      <div class="u-clearfix u-sheet u-sheet-1">
        <p class="u-text u-text-default u-text-1">If you have any questions about MAGNHIFFIC please feel free to send<br>an email to the PI, Filippo M. Maccagni.<br>
          <br>
          <br>
        </p>
        <p class="u-text u-text-default u-text-2">[Contact address placeholder &ndash; see REVIEW_NOTES.md. The template showed the address as an image (images/adres.png) to deter address harvesting; drop a MAGNHIFFIC equivalent in and swap this paragraph for an &lt;img&gt; tag.]<br>
          <br>
        </p>
      </div>
    </section>"""
    desc = "Contact the MAGNHIFFIC survey team."
    write("Contact.html", page("Contact", "Contact.css", [s1], desc))
    write_css("Contact.css", tpl_css("_contact_sec1.css") + """

.u-section-1 .u-text-2 {
  width: 620px;
  margin: 10px auto 60px;
}

@media (max-width: 767px) {
  .u-section-1 .u-text-2 {
    width: 340px;
  }
}""")


# ------------------------------------------------------- password-gated pages
#
# The gate is client-side (Nicepage's scheme, unchanged from the template):
#   * the public page (e.g. Data.html) shows only a password form;
#   * the real content lives at Data_<sha256(password)>.html;
#   * the body carries data-salt and data-salted-password = sha256(password+salt),
#     which nicepage.js checks before redirecting.
# This keeps unlisted URLs out of search engines but is NOT real access control:
# anyone who knows the hashed filename can open the content directly. Do not put
# anything genuinely confidential behind it.
#
# To change the password: edit TEAM_PASSWORD and re-run this script. Every gated
# page is renamed accordingly.

TEAM_PASSWORD = "magnhiffic"
GATE_SALTS = {"Data": "0f41", "Gallery": "0912",
              "Releases": "37f1", "Projects": "37f1"}


def _sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def gate_body_attrs(pagename):
    salt = GATE_SALTS[pagename]
    return ('data-home-page="%s.html" data-salt="%s" data-salted-password="%s" '
            'class="u-body u-xl-mode" data-lang="en"'
            % (pagename, salt, _sha(TEAM_PASSWORD + salt)))


def gate_section():
    return tpl_css("_gate_section.html")


def build_gate(pagename, title):
    """The public, password-prompt half of a gated page."""
    html = "%s\n  <body %s>\n    %s\n    %s\n    %s\n  \n</body></html>\n" % (
        head(title, "Page-Password-Template.css",
             "%s \u2014 MAGNHIFFIC team area (password protected)." % title),
        gate_body_attrs(pagename), header(), gate_section(), footer())
    write("%s.html" % pagename, html)


def build_protected(pagename, title, css, sections, description=""):
    """The content half, served at <page>_<sha256(password)>.html."""
    fname = "%s_%s.html" % (pagename, _sha(TEAM_PASSWORD))
    write(fname, page(title, css, sections, description))
    return fname


# ---- Team Data hub

DATA_CARDS = [
    ("1822940-3e8f21d7.png", "Releases",
     "Link to the page containing information on the MAGNHIFFIC data releases",
     "Releases.html", "Releases"),
    ("860766-ab3e1c93.png", "Gallery",
     "Link to the page containing MAGNHIFFIC images and posters",
     "Gallery.html", "Gallery"),
    ("1087927-e922035e.png", "Projects",
     "Link to the page describing on-going papers and projects",
     "Projects.html", "Projects"),
]


def build_data():
    build_gate("Data", "Team Data")

    cards = "".join("\n            " + card(ic, t, b, h, l, i)
                    for i, (ic, t, b, h, l) in enumerate(DATA_CARDS, 1))
    s1 = banner("carousel_ddcf", 1, "Data",
                "Internal MAGNHIFFIC data products, images and project list.")
    s2 = """<section class="u-align-center u-black u-clearfix u-section-2" id="sec-team-data">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-expanded-width u-list u-list-1">
          <div class="u-repeater u-repeater-1">%s
          </div>
        </div>
      </div>
    </section>""" % cards
    build_protected("Data", "Team Data", "Data.css", [s1, s2],
                    "MAGNHIFFIC internal data area.")
    write_css("Data.css", tpl_css("_data_sec1.css") + "\n\n" +
              tpl_css("_data_sec2.css"))


# ---- Gallery

def build_gallery():
    build_gate("Gallery", "Gallery")

    s1 = banner("carousel_ddcf", 1, "Image Gallery",
                "MAGNHIFFIC images and sample posters.")

    items = [
        ("fornaxAcontHI.jpg", "Fornax A",
         "MeerKAT HI (contours) overlaid on the radio continuum of Fornax A "
         "(NGC 1316), showing the cold gas around the restarted radio source."),
        ("beamNhiwhiteNo.jpg", "Column density vs resolution",
         "HI column density sensitivity reached by MAGNHIFFIC as a function of "
         "angular resolution, compared with existing observations."),
        ("2018-MeerKAT-1-1030x557.jpg", "MeerKAT",
         "The MeerKAT array in the Karoo, South Africa. Image credit: SARAO."),
    ]
    s2 = """<section class="u-align-center u-black u-clearfix u-section-2" id="sec-gal">
      <div class="u-clearfix u-sheet u-sheet-1">
        <h4 class="u-align-center u-text u-text-1">Survey images</h4>
        <p class="u-align-justify u-text u-text-2">The images below may be used for
        presentations and outreach with credit to the MAGNHIFFIC survey and SARAO/MeerKAT.
        [Placeholder &ndash; add sample posters and per-target images as they are produced.]</p>
        %s
      </div>
    </section>""" % gallery(items)

    build_protected("Gallery", "Gallery", "Gallery.css", [s1, s2],
                    "MAGNHIFFIC image gallery.")

    sec2 = """ .u-section-2 {
  background-image: none;
}

.u-section-2 .u-sheet-1 {
  min-height: 860px;
}

.u-section-2 .u-text-1 {
  font-weight: 700;
  margin: 40px auto 0;
}

.u-section-2 .u-text-2 {
  width: 940px;
  margin: 14px auto 0;
}

.u-section-2 .u-gallery-1 {
  min-height: 500px;
  width: 1140px;
  margin: 30px auto 60px;
}

.u-section-2 .u-gallery-inner-1 {
  grid-template-columns: repeat(3, 1fr);
  grid-auto-rows: 340px;
  gap: 10px;
}

@media (max-width: 1199px) {
  .u-section-2 .u-sheet-1 {
    min-height: 760px;
  }

  .u-section-2 .u-text-2 {
    width: 940px;
  }

  .u-section-2 .u-gallery-1 {
    width: 940px;
  }

  .u-section-2 .u-gallery-inner-1 {
    grid-auto-rows: 280px;
  }
}

@media (max-width: 991px) {
  .u-section-2 .u-sheet-1 {
    min-height: 640px;
  }

  .u-section-2 .u-text-2 {
    width: 720px;
  }

  .u-section-2 .u-gallery-1 {
    width: 720px;
  }

  .u-section-2 .u-gallery-inner-1 {
    grid-auto-rows: 220px;
  }
}

@media (max-width: 767px) {
  .u-section-2 .u-sheet-1 {
    min-height: 900px;
  }

  .u-section-2 .u-text-2 {
    width: 540px;
  }

  .u-section-2 .u-gallery-1 {
    width: 540px;
  }

  .u-section-2 .u-gallery-inner-1 {
    grid-template-columns: 1fr;
    grid-auto-rows: 260px;
  }
}

@media (max-width: 575px) {
  .u-section-2 .u-text-2 {
    width: 340px;
  }

  .u-section-2 .u-gallery-1 {
    width: 340px;
  }

  .u-section-2 .u-gallery-inner-1 {
    grid-auto-rows: 200px;
  }
}"""
    write_css("Gallery.css", tpl_css("_gallery_sec1.css") + "\n\n" + sec2)


# ---- Releases

RELEASE_POLICY = (
    'This page contains information on the MAGNHIFFIC survey data and links to '
    'the data repositories. If you are planning to use these MAGNHIFFIC data '
    'please familiarise yourself with the survey policy document first. Using '
    'the data implicitly assumes you agree with these policies.&nbsp;<br>'
    '<br>[Placeholder \u2014 add a link to the MAGNHIFFIC survey policy PDF, e.g. '
    'files/MAGNHIFFIC_Survey_Policies.pdf; see REVIEW_NOTES.md]&nbsp;')

RELEASES = [
    ("Internal Data Release 1",
     'Full-depth MeerKAT HI cubes and moment maps of the first MAGNHIFFIC '
     'targets.&nbsp;<br>'
     '<br>[Placeholder \u2014 list the galaxies included and add the repository '
     'link. Please see the {SAMPLE} webpage for further details on the global '
     'properties of these galaxies.]&nbsp;'),
    ("Continuum Data Release",
     'Radio continuum images of the MAGNHIFFIC targets, produced alongside the '
     'HI cubes.&nbsp;<br>'
     '<br>[Placeholder \u2014 add repository link and reduction notes.]&nbsp;'),
    ("Ancillary Data",
     'Molecular (CO) and ionised gas observations of the MAGNHIFFIC sample used '
     'for the multi-phase analysis.&nbsp;<br>'
     '<br>[Placeholder \u2014 add the list of ancillary datasets and their '
     'provenance.]&nbsp;'),
]


def build_releases():
    build_gate("Releases", "Releases")

    def band(sec_no, sec_id, heading, body, btn_no):
        return """<section class="u-black u-clearfix u-section-%d" id="%s">
      <div class="u-clearfix u-sheet u-sheet-1">
        <div class="u-clearfix u-expanded-width u-layout-wrap u-layout-wrap-1">
          <div class="u-layout">
            <div class="u-layout-row">
              <div class="u-container-style u-layout-cell u-size-60 u-layout-cell-1">
                <div class="u-container-layout u-container-layout-1">
                  %s
                  <p class="u-align-justify u-text u-text-2"> %s
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>""" % (sec_no, sec_id, heading, body)

    h1 = ('<h2 class="u-text u-text-1">Data Releases</h2>\n'
          '                  <h4 class="u-align-center u-text u-text-3">Survey Policies</h4>')
    secs = [band(1, "carousel_0fe1", h1, RELEASE_POLICY, 1)]
    for i, (title, body) in enumerate(RELEASES, 2):
        body = body.replace("{SAMPLE}", link("Sample.html", "sample", i))
        secs.append(band(i, "sec-rel-%d" % i,
                         '<h4 class="u-align-center u-text u-text-1">%s</h4>' % title,
                         body, i))

    build_protected("Releases", "Releases", "Releases.css", secs,
                    "MAGNHIFFIC data releases.")

    blocks = tpl_css("_releases_sec1.css") + """

.u-section-1 .u-text-3 {
  font-weight: 700;
  margin: 24px auto 0;
}
"""
    for k in (2, 3, 4):
        blocks += "\n\n" + tpl_css("_releases_sec%d.css" % k)
    write_css("Releases.css", blocks)


# ---- Projects

def build_projects():
    build_gate("Projects", "Projects")

    body = ('The list below gives an overview of MAGNHIFFIC papers and projects '
            'in progress.&nbsp;<br>'
            '<br>[Placeholder \u2014 link the shared project document, or list the '
            'projects here directly; see REVIEW_NOTES.md]&nbsp;')
    s1 = """<section class="u-black u-clearfix u-section-1" id="carousel_0fe1">
      <div class="u-clearfix u-sheet u-sheet-1">
        <h2 class="u-text u-text-default u-text-1">Papers and Projects in Progress</h2>
        <p class="u-align-justify u-text u-text-2"> %s
        </p>
      </div>
    </section>""" % body
    build_protected("Projects", "Projects", "Projects.css", [s1],
                    "MAGNHIFFIC papers and projects in progress.")
    write_css("Projects.css", tpl_css("_projects_sec1.css") + """

.u-section-1 .u-text-2 {
  width: 940px;
  margin: 20px auto 60px;
}

@media (max-width: 1199px) {
  .u-section-1 .u-text-2 {
    width: 940px;
  }
}

@media (max-width: 991px) {
  .u-section-1 .u-text-2 {
    width: 720px;
  }
}

@media (max-width: 767px) {
  .u-section-1 .u-text-2 {
    width: 540px;
  }
}

@media (max-width: 575px) {
  .u-section-1 .u-text-2 {
    width: 340px;
  }
}""")


def build_all():
    write_theme_css()
    build_home()
    build_science()
    build_survey()
    import csv as _csv
    with open("sample_table.csv") as fh:
        rows = list(_csv.DictReader(fh))
    build_sample(rows)
    build_publications()
    build_team()
    build_public_data()
    build_contact()
    build_data()
    build_gallery()
    build_releases()
    build_projects()
    shutil.copy2(os.path.join(TPL, "Page-Password-Template.css"),
                 os.path.join(SITE, "Page-Password-Template.css"))


if __name__ == "__main__":
    build_all()
