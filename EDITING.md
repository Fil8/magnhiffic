# Editing the MAGNHIFFIC site visually

## Changing fonts, sizes and colours: one block, 17 pages

All typography and the accent colour now come from a single `THEME` dict at the
top of `tools/build_site.py`:

```python
THEME = {
    "body_font":     "'Open Sans', sans-serif",   # paragraphs, tables, nav
    "heading_font":  "Roboto, sans-serif",        # h1-h6
    "display_font":  "'Cantata One', serif",      # Home hero title + strapline
    "wordmark_font": "Roboto, sans-serif",        # MAGNHIFFIC in the black bar
    "root_size":     "16px",                      # scales the whole site
    "body_size":     "1rem",
    "hero_size":     "4.5rem",
    "wordmark_size": "1.75rem",
    "heading_weight":"700",
    "hero_weight":   "900",
    "hero_tracking": "4px",
    "accent":        "#478ac9",   # links, inline buttons, star hover
    "text_color":    "#3e3e3e",
    "dark_bg":       "#000000",   # header bar, More Info band, footer
}
```

Edit a value and rebuild:

    cd tools && python3 build_site.py

The build writes `docs/theme.css` from that dict, and every page loads it
*after* `nicepage.css` and after its own stylesheet — so these rules win. That
is the whole mechanism; there is nothing else to touch.

**Using a different font.** Set the family in `THEME`, then add it to
`GOOGLE_FONTS` just below (the API's own syntax, spaces written as `+`):

```python
"heading_font": "'Source Sans Pro', sans-serif",
GOOGLE_FONTS = ["Source+Sans+Pro:400,600,700", "Open+Sans:300,400,600,700", ...]
```

If you name a family and forget the `GOOGLE_FONTS` line, nothing errors — the
browser just falls back to the next family in the list, which is easy to
misread as "the change didn't work". Websafe families (Georgia, Arial, Times)
need no entry. Trim the weights you don't use; each one is a separate download.

`theme.css` itself is generated — don't hand-edit it, the next build replaces
it. If you want a rule that isn't covered by `THEME`, put it in the page's own
stylesheet, or extend `write_theme_css()` in the build script.

## Nicepage will not work — this is worth knowing up front

Nicepage cannot import HTML. It only opens its own project files, and a
published HTML export is a one-way output. That applies to the MHONGOOSE
template you sent me as well: both archives you gave me are HTML exports with
no project file, so neither could be opened in Nicepage.

One thing to check: your preliminary MAGNHIFFIC site was built with Nicepage
5.10.10, so **the project may still be on your machine** (look under
`Documents/Nicepage`). If it is, that one is editable in Nicepage — it just has
the layout you didn't want.

The pages I wrote use Nicepage's own CSS class vocabulary (`u-section-*`,
`u-sheet`, `u-btn`), so they look native and the stylesheets behave the same
way. That makes them *familiar*, not *importable*.

## Use Pinegrow instead

[Pinegrow](https://pinegrow.com) is the closest thing to what you wanted: a
desktop visual editor that works directly on existing HTML and CSS files. It
adds nothing of its own to your code — no framework, no wrapper, no project
format. You open the folder, edit visually, and it saves the same files.

It is commercial (one-off licence, free trial), macOS/Windows/Linux.

### Getting started

1. Unzip the site somewhere permanent.
2. Pinegrow → **File ▸ Open Project** → select the `magnhiffic_site` folder
   (open the *folder*, not a single page, so links between pages resolve and
   the stylesheets are picked up).
3. Double-click `index.html` in the file tree.

Editing text and swapping images is direct manipulation. For layout, select an
element and use the Style panel; Pinegrow writes to the real stylesheet, and
you choose which file the rule lands in — send new rules to the **page's own
stylesheet** (`Home.css`, `Science.css`, …), never to `nicepage.css`.

### The one thing to be careful about

`nicepage.css` (1.3 MB) is the framework: the grid, the responsive behaviour,
the recoloured palette. Treat it as read-only. If you change a rule there it
will affect every page in ways that are tedious to trace back.

Per-page geometry lives in the matching `<Page>.css`, each with four
breakpoints (1199 / 991 / 767 / 575 px). If you make a section taller, its
`min-height` may need raising in all four — Pinegrow shows the breakpoints in
its device bar, so check the narrow ones before saving.

### The navigation bar is duplicated 17 times

This is inherent to a flat HTML site — there is no server-side include, so the
header and footer are physically copied into every page. Editing the nav in
Pinegrow changes the page you are looking at and no other.

Fix it in one command. Edit the nav or footer on any single page, then:

    cd magnhiffic_site
    python3 sync_chrome.py Home.html      # copy that page's header+footer to the other 16
    python3 sync_chrome.py --check        # just report which pages have drifted

It only touches the regions between the `<!-- ==== SHARED HEADER ==== -->` and
`<!-- ==== SHARED FOOTER ==== -->` comments, leaves everything else byte-for-byte
alone, and writes a `.bak` beside each file it changes. Don't delete those
marker comments — without them the script can't locate the region, and it will
say so rather than guess.

## Alternatives, if you'd rather not buy a licence

| Tool | Notes |
|---|---|
| **VS Code** + *Live Preview* extension | Free. Not visual editing — you edit markup with the page live beside it. For text and image changes this is genuinely enough, and the class names are readable. |
| **CodePen / browser devtools** | Free, good for *trying* a CSS change: edit in the Styles inspector, see it instantly, then copy the rule into the page's `.css`. Nothing persists on its own. |
| **Webflow, Framer, Wix, Squarespace** | Avoid for this. Like Nicepage, they are closed builders that cannot ingest existing HTML — you would be rebuilding from scratch inside their editor. |

## Or skip the visual editor

For the changes you are most likely to want — text, team members,
publications, nav labels, the sample table — `build_site.py` is less work than
any editor, because one edit updates all 17 pages at once:

    python3 build_site.py

See `README.md` for the table of which constant controls what.

**Don't mix the two carelessly.** `build_site.py` regenerates the `.html` and
per-page `.css` files, so it overwrites visual edits made in Pinegrow. Pick one
as the source of truth per page. A reasonable split: use the build script for
text and structure, Pinegrow for fine layout work — and once you start editing
a page visually, stop regenerating that page.
