# ttadano.github.io

Personal academic website of **Terumasa Tadano**, built with [Quarto](https://quarto.org).

## Sources of truth

- `references.bib` — papers (journal articles, preprints, reviews/book chapters).
  Each entry is tagged `keywords = {journal|preprint|review}`.
- `talks.bib` — presentations (`presentationtype = {invited|oral|poster}`,
  `scope = {international|domestic}`, `invited = {true|false}`).

`scripts/render_bib.py` (Python standard library only) runs as a Quarto
**pre-render** step: it validates both `.bib` files and generates Markdown
partials in `_gen/` for the Publications and Talks pages and for the CV. Edit a
`.bib` entry and the website *and* the PDF CV update on the next build.

## Build / preview

```bash
quarto preview      # local site at http://localhost (search + dark mode work over http)
quarto render       # full build incl. the PDF CV -> _site/
```

The PDF CV (`cv.qmd` → `CV_Tadano.pdf`) uses XeLaTeX and auto-selects an
installed CJK font (Noto Serif CJK JP in CI, Hiragino on macOS) for the
Japanese entries. A post-render step also mirrors it to `/uploads/CV_Tadano.pdf`.

## Layout

| Path | Purpose |
|---|---|
| `index.qmd` | Home (profile, recent news, contact) |
| `publications.qmd`, `talks.qmd` | Generated from the `.bib` files |
| `projects.qmd`, `people.qmd` | Hand-edited content |
| `news/` | One `.qmd` per news item + listing |
| `cv.qmd` | Full CV → HTML page + `CV_Tadano.pdf` |
| `scripts/` | `render_bib.py` (bib → Markdown), `copy_cv.py` (post-render) |
| `assets/` | `avatar.jpg`, `styles.css`, `dark.scss` |

## Deploy

GitHub Actions (`.github/workflows/publish.yml`) renders the site (installing
TinyTeX + Noto CJK), asserts the CJK PDF built, and publishes to GitHub Pages on
pushes to `master`.
