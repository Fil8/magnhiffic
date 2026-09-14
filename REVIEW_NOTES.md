# MAGNHIFFIC website — things you need to check

The site is complete and internally consistent, but a number of items could not
be resolved from the material supplied. They are listed worst-first.

## 1. The sample table has 33 rows, but the text says 22 AGN

`sample_table.csv` — extracted from the sample-table image in your preliminary
site — contains **33 objects**. The Survey and Science prose (also taken from
your preliminary site) says the survey observes **22 galaxies**, split 10
radiative / 12 radio-jetted.

These cannot both be right. Either the table includes objects that are not in
the observed sample, or the prose is out of date. **Nothing in the supplied
material resolves this**, so I left both numbers as they were rather than
silently editing one to match the other. The Sample page states its own row
count automatically, so fixing `sample_table.csv` fixes the page.

## 2. Coordinates I corrected

Three rows in the preliminary table were wrong; I checked all 33 against SIMBAD
(30 agreed to better than 7 arcsec) and corrected these:

| Object | Was | Now |
|---|---|---|
| IC 1459 | wrong position | 22:57:10.6 −36:27:44 |
| NGC 0289 | wrong position | 00:52:42.4 −31:12:21 |
| ESO 428-G14 | carried NGC 1433's coordinates | 07:16:31.2 −29:19:29 |

`ESO 428-G14` also had **no distance**; I derived D_L = 25.0 Mpc from its
redshift with H0 = 67.8. Please confirm — it is the only derived value in the
table.

## 3. NED links that pointed at the wrong galaxy

In the preliminary table, `NGC 4696`, `ESO 428-G14` and `NGC 3557` reused the
NED URL of the row above them (`ngc+2663`, `NGC1433`, `NGC3100`). Fixed. All 33
links are now distinct and name-matched, but I could not verify that each URL
actually resolves at NED — spot-check a few.

## 4. Funding acknowledgement — placeholder, must be replaced

The template's footer credited **ERC grant 882793 "MeerGas"**, which is the
MHONGOOSE-side grant, not MAGNHIFFIC's. Nothing in your preliminary site gave a
MAGNHIFFIC funding statement, so the footer now reads:

> MAGNHIFFIC is supported by INAF – Istituto Nazionale di Astrofisica.
> [Funding acknowledgement to be completed – see REVIEW_NOTES.md]

Edit `FUNDING` in `build_site.py`. If the funder is not the ERC, also replace
`images/LOGO_ERC-FLAG_EUNEGATIF1.jpg` and the `https://erc.europa.eu/` link
inside `footer()`.

## 5. Other placeholders, all marked `[...]` in the page text

- **Team** — only you (PI) are listed. Two `[Add team member: ...]` slots in `TEAM`.
- **Publications** — MAGNHIFFIC has no survey papers yet, so the page lists the
  four sample-selection references as "background papers". Add real papers to
  `PUB_BACKGROUND`.
- **Contact** — no address. The template rendered its address as an image
  (`images/adres.png`) to deter harvesting; do the same or edit the paragraph.
- **Public Data Release**, **Releases**, **Projects**, **Gallery** — drafted
  structure, placeholder content, no repository links (none exist yet).
- **Survey policy PDF** — the template linked one; MAGNHIFFIC has none.

## 6. The password gate is obscurity, not security

Unchanged from the template's mechanism, which is entirely client-side: the
content lives at `<Page>_<sha256(password)>.html`, and `nicepage.js` redirects
there if the typed password hashes correctly. Anyone who learns the hashed
filename can open the content directly, and the hash is in the page source.

**Do not put anything confidential behind it.**

Password is currently `magnhiffic`. To change it, edit `TEAM_PASSWORD` in
`build_site.py` and re-run — every gated file is renamed automatically.

## 7. Images

Your preliminary site contained five images. Only two are real science figures:

- `fornaxAcontHI.jpg` — Fornax A, HI on continuum → Home hero, Science, Public Data, Gallery
- `beamNhiwhiteNo.jpg` — column density vs. angular resolution → Survey, Science, Gallery

The other three (`0fd3416c`, `68f64b9d`, `8ad73f3c`) were **Nicepage stock
photos** — a woman at a laptop, an office interior, a handshake — not
MAGNHIFFIC content. I dropped them and used the template's MeerKAT photographs
for the decorative bands instead. Replace those with MAGNHIFFIC figures when
you have them.

There is **no logo**. The header and hero use a text wordmark. Drop a file at
`images/magnhiffic_logo.png` and set `LOGO_IMAGE = "magnhiffic_logo.png"` in
`build_site.py` to switch over.

## 8. I could not view the site in a browser

The sandbox cannot download a headless browser (its binaries sit behind a
blocked host), so **no page was ever visually rendered**. Verification was
structural: every internal link resolves, every referenced image exists, every
stylesheet is reachable, no page has an HTML nesting error, and no template
survey name or personnel string survives.

Layout geometry was reused verbatim from the template's stylesheets wherever the
content shape was unchanged, so those sections should look as they do on the
MHONGOOSE site. The sections I wrote fresh CSS for — the Sample table, the
Gallery grid, Publications, and the Public Data figure band — have had **no
visual check at all**. Open those four first, and check them at narrow window
widths too.
