# Hosting MAGNHIFFIC

Short answer: **yes, GitHub Pages works, and it's what I'd recommend.** The site
is plain HTML/CSS/JS with no server-side code, no database and no build step —
exactly what Pages is for. Total served size is 3.2 MB against a 1 GB limit.

Read the security note at the bottom before you push. It is the one thing here
that isn't just configuration.

---

## Repo layout

```
magnhiffic_repo/
  docs/          <- the ONLY thing GitHub Pages serves
    index.html   Home.html   Science.html   ...   (17 pages)
    images/  files/  nicepage.css  nicepage.js  jquery.js
    .nojekyll
  tools/         <- build machinery; in git, never published
    build_site.py  sync_chrome.py  sample_table.csv  template_css/
  README.md  REVIEW_NOTES.md  EDITING.md  HOSTING.md
```

Two deliberate choices:

**`docs/` as the publishing root.** Pages can serve the repo root, `docs/`, or a
branch. Using `docs/` keeps the build script, the sample-table CSV and the
template stylesheets version-controlled but unpublished. If you served the root
instead, `build_site.py` — which contains the gate password as a plain string —
would be downloadable.

**`.nojekyll`.** Pages runs Jekyll by default, and Jekyll silently drops files
and folders whose names begin with `_`. Our build inputs are all `_`-prefixed
(`_home_sec1.css`, `_gate_section.html`, …). They live in `tools/` and aren't
served, so nothing currently breaks — but this file removes the whole class of
failure, which is otherwise a genuinely baffling one to debug. Keep it.

## Deploying

```bash
cd magnhiffic_repo
git init && git add -A && git commit -m "MAGNHIFFIC website"
git branch -M main
git remote add origin https://github.com/<you>/<repo>.git
git push -u origin main
```

Then in the repo: **Settings → Pages → Source: "Deploy from a branch" →
Branch `main`, folder `/docs` → Save.** First build takes a couple of minutes.

You'll get `https://<you>.github.io/<repo>/`. Every link in the site is
relative and there are no `<base>` tags, so it works correctly under that
subpath — no changes needed. I verified all 50 served files resolve.

To publish at a bare domain instead, add a `CNAME` file in `docs/` containing
the hostname and point a DNS `CNAME` record at `<you>.github.io`. Pages
provisions the HTTPS certificate itself.

Updating later: edit, `git commit`, `git push`. The site redeploys on its own.

## Building inside this layout

`build_site.py` now writes to `../docs`, so run it from `tools/`:

```bash
cd tools && python3 build_site.py
```

`sync_chrome.py` finds the pages whether you run it from `tools/` or the repo
root, and takes a `SITE=` override:

```bash
python3 tools/sync_chrome.py --check        # report header/footer drift
python3 tools/sync_chrome.py Home.html      # propagate from Home to the rest
```

**One caution learned the hard way.** `sync_chrome.py` writes `.bak` files for
every page it modifies — so if you propagate an edit and then decide against
it, restoring only the page you started from leaves the change on the other 16.
Either restore every `.bak`, or just re-run `build_site.py`. Don't commit
`.bak` files; the `.gitignore` excludes them.

## Alternatives

| | Cost | Fits here? |
|---|---|---|
| **GitHub Pages** | free | Recommended. Version control and hosting in one place; a bad edit is one `git revert` away. |
| **Netlify** | free tier | Also good. Drag-and-drop the `docs/` folder, no git needed. Adds deploy previews and password protection on paid tiers. |
| **Cloudflare Pages** | free tier | Equivalent; fastest CDN of the three. |
| **Institutional web space** (INAF/ASTRON) | free | Worth asking about — a `inaf.it` URL carries more weight than `github.io`, and it's just an `scp` of `docs/`. No version history, though. |

All four serve static files; the site works unchanged on any of them. Editing
stays as described in `EDITING.md` (Pinegrow, or a text editor) — the host
doesn't constrain the editor.

---

## Security note: the password gate and public repos

**The password gate is obfuscation, not access control — and putting the repo
on GitHub makes that materially easier to notice.**

How the template's gate works: the public page carries a salt and a salted hash
of the password in plain HTML attributes, and the protected content sits in a
separate file whose *filename is the SHA-256 of the password*:

```
Data_c2ac40b6707337565f2852de3d5a2ade415c3c0272985a9de3a689e2a391bcb4.html
```

Anyone who can read the directory listing, guess the filename, or brute-force
the hash offline reads the content without ever entering the password. `magnhiffic`
falls in seconds to any wordlist. This is inherited from the MHONGOOSE template,
not something I introduced — but Pages changes the exposure in two ways:

1. **A public repo publishes the source**, including `build_site.py` with
   `TEAM_PASSWORD = "magnhiffic"` in clear text. Keeping the build script out of
   `docs/` stops it being *served*, but a public repo still shows it. Search
   engines also index the protected pages directly unless you exclude them.
2. **Pages on a private repo does not make the site private** on free or Pro
   plans — publishing from a private repo produces a *publicly visible* site.
   Private Pages sites require GitHub Enterprise Cloud. So "I'll just make the
   repo private" protects the source, not the pages.

Pick one, depending on what's behind the gate:

- **Nothing genuinely sensitive** (draft figures, internal links): change the
  password to something not in a dictionary, and accept the gate as a
  keep-honest-people-out speed bump. Add the protected filenames to
  `robots.txt` so they aren't indexed — it's currently `Disallow:` (i.e.
  allows everything).
- **Genuinely private data** (unpublished results, embargoed catalogues):
  don't put it on Pages at all. Use a private repo for the files, or an
  institutional server with real HTTP authentication, and link out from the
  public site. Netlify's password protection or Cloudflare Access are the
  cheap middle grounds.

Either way, **make the repo private if you push before the placeholders are
resolved** — `REVIEW_NOTES.md` records the unresolved funding statement and the
33-rows-vs-22-AGN sample question, and those shouldn't go public as-is.
