# MAGNHIFFIC website

Static site built on the same framework (Nicepage 5.2.4) as the MeerKAT Fornax
Survey / MHONGOOSE pages, with MAGNHIFFIC content. No build tooling, no server
side: it is plain HTML/CSS/JS and can be dropped onto any web host.

**Deploying?** See `HOSTING.md` — GitHub Pages works; `docs/` is the publishing
root. Read its security note before pushing: the password gate is obfuscation,
and Pages from a private repo still produces a public site.

**Want to edit this in a visual editor?** See `EDITING.md`. Short version:
Nicepage cannot import HTML (it never could — your template was an export too);
Pinegrow can, and edits these files directly.

**Read `REVIEW_NOTES.md` first** — it lists the placeholders and the two data
discrepancies you need to settle.

## Looking at it

    cd magnhiffic_site && python3 -m http.server 8000

then open <http://localhost:8000/>. Opening the `.html` files directly with
`file://` also works, though relative links behave slightly differently.

## Pages

| File | Nav label | Notes |
|---|---|---|
| `index.html` / `Home.html` | Home | identical; `index.html` is the entry point |
| `Science.html` | Science (under Survey) | three MAGNHIFFIC projects |
| `Survey.html` | Survey | |
| `Sample.html` | Sample | live HTML table, 33 objects, NED links |
| `Publications.html` | Publications | |
| `Public-Data-Release.html` | Public Data | |
| `Team.html` | Team | |
| `Contact.html` | Contact | |
| `Data.html` | Team Data | password gate |
| `Gallery.html` | Gallery | password gate |
| `Releases.html` | Releases | password gate |
| `Projects.html` | Projects | password gate |

The four gated pages each have a companion `<Page>_<hash>.html` holding the
actual content. Password: `magnhiffic`. See REVIEW_NOTES.md §6 — it is
obscurity, not access control.

## Editing

Two ways, pick one:

**Edit the HTML directly.** Fine for fixing a sentence. But the header, nav and
footer are duplicated into all 17 pages, so a change to those means 17 edits.

**Edit `build_site.py` and re-run** (recommended). Everything user-visible is a
constant near the top of the relevant function:

    python3 build_site.py

| To change | Edit |
|---|---|
| nav menu and dropdowns | `NAV` |
| wordmark / logo | `WORDMARK_FULL`, `LOGO_IMAGE` |
| footer funding text | `FUNDING` |
| fonts, sizes, accent colour | `THEME` + `GOOGLE_FONTS` (see below) |
| home page cards | `HOME_CARDS` |
| team list | `TEAM` |
| publications | `PUB_BACKGROUND` |
| data releases | `RELEASES` |
| gate password | `TEAM_PASSWORD` |
| sample table | `sample_table.csv` |

The script regenerates `*.html` and the per-page `*.css` only. It does not touch
`nicepage.css`, `nicepage.js`, `jquery.js`, `images/` or `files/`, so anything
you drop in there is safe.

`sample_table.csv` columns: `name, ra, dec, dl_mpc, gal_type, agn_type,
subsample, environment, ned_url`. Add or remove rows freely — the page and the
plain-text export at `files/magnhiffic_sample.txt` both follow the file, and the
intro text states the row count automatically.

`subsample` drives the grouping and the cell colours on the Sample page. Allowed
values are `magnum`, `radio_loud` and `other`; anything else falls into the last
group. Rows are rendered group by group in the order given by `SAMPLE_GROUPS`
and, inside each group, sorted by ascending `dl_mpc` — so moving a galaxy
between subsamples is a one-cell edit plus a rebuild. A group with no rows is
not rendered at all (that is why `other` is currently invisible). The three
fills are `magnum_bg`, `radio_loud_bg` and `other_bg` in `THEME`; the group
label rows use the same hues one step lighter, derived automatically.

## Fonts and colours

Both come from the `THEME` dict at the top of `build_site.py`. The build
renders it into `docs/theme.css`, which every page loads after `nicepage.css`
and after its own stylesheet — so `THEME` has the last word. Change a value,
re-run the build, done on all 17 pages. `EDITING.md` has the full key list and
the one gotcha (a new font family must also be added to `GOOGLE_FONTS`).

`THEME["accent"]` covers what the site actually uses: links, active nav items,
the palette-1 and palette-3 fills, the card-icon borders, the star's hover
state, and — derived automatically as a lighter tint — the hover/active
variants. `nicepage.css` still carries the framework's full five palettes with
all their light/dark steps; those steps are unused by these pages, so there is
no need to touch that file. `THEME["dark_bg"]` controls the black chrome
(header bar, More Info band, footer).

## Layout

Page geometry comes from the per-page stylesheets, split out of the template's
own and reused verbatim where the content shape was unchanged. Each has four
breakpoints (1199 / 991 / 767 / 575 px). If you add content to a section, its
`min-height` may need raising in all four.
