# Migration Plan: HugoBlox (Academic) → Quarto

Status: **v2 — reviewed by Codex, awaiting user go-ahead** (no implementation yet)
Target site: `https://ttadano.github.io/` (GitHub user-pages repo `ttadano/ttadano.github.io`)
Author: Terumasa Tadano

> **Review note (v2):** Incorporates Codex critique. Key changes: (a) real-publication **inventory audit** added as Phase 0 — `tadano-2023-butsuri` is a *real* article with no `cite.bib` and must be hand-added; (b) **CJK PDF smoke test moved to Phase 1** (prove `xelatex` + Noto CJK in CI before migrating content); (c) **single deployment path** chosen + the 3 stale Hugo workflows removed; (d) **formal BibTeX schemas** locked before authoring; (e) **redirect policy** elevated to a deliverable; (f) `render_bib.py` gets a fail-fast **validation** stage; (g) News/Projects/People/Links stay **hand-authored**, not part of the data pipeline.

## 1. Goals & constraints (agreed with user)

- Switch the static-site generator from Hugo + HugoBlox (Wowchemy/Academic) to **Quarto**, to escape the theme’s breaking-change treadmill.
- Keep the site **as simple as possible**. Dropping HugoBlox-specific features is acceptable.
- **Single source of truth in BibTeX**, in **two files**:
  - `references.bib` — papers (journal articles + book chapters/invited reviews).
  - `talks.bib` — presentations, each with a custom field **`invited = {true|false}`**.
- From those bibs, generate **both** the website pages **and** a **PDF CV** (full CV, clean default layout).
- Drop the “featured paper” distinction.
- Keep: **News**, **Projects**, **Postdocs & Visitors**, **Links**.
- Bilingual (JP/EN) i18n machinery is **out of scope** (content stays inline UTF-8; site chrome stays English).

## 2. What exists today (inventory)

| Area | Current (Hugo) | Count | Disposition |
|---|---|---|---|
| Home/landing | `content/_index.md` widgets: Biography, News, Experience, Contact(+map) | — | Rebuild as `index.qmd` (bio/interests/education/contact) + News listing |
| Author profile | `content/authors/admin/_index.md` (+ `avatar.jpg` 1.3 MB) | — | Becomes home/about + CV header; reuse avatar |
| Publications | `content/publication/<slug>/{index.md,cite.bib}` | 87 folders; **85 have `cite.bib`, 2 don’t** (`preprint/`=demo→skip; **`tadano-2023-butsuri/`=real review, no cite.bib→hand-add**). Of the 85 with cite.bib, 2 are demos (`conference-paper`=`example1`, `journal-article`). ⇒ ~**84 real**. | **Audit** (Phase 0) then merge → `references.bib`; reconcile against CV (74 papers + 12 reviews = 86) |
| Talks | `content/event/<slug>/index.md` (+ `content/talks/all_presentations.md`) | 48 events, **39** `featured: true`; **CV lists 40 invited** → reconcile the 39↔40 gap | Author `talks.bib` from events + CV invited list; **`featured`≠authoritative**, set `invited` explicitly |
| Projects | `content/projects_ongoing/*`, `content/projects_past/*` | 6 + 6 | Single `projects.qmd` (ongoing/past sections) |
| Postdocs/Visitors | `content/home/students.md` | — | `people.qmd` |
| Links | `content/home/links.md` | — | small page or footer |
| News | `content/news/<slug>/index.md` (bilingual JP/EN) | 19 | Quarto listing |
| CV | `static/uploads/CV_Tadano.pdf` (hand-made LaTeX) | — | Reproduce as `cv.qmd` → HTML + PDF |
| Demos | `content/post/*`, `content/research/*` | — | **Delete** |
| Config | GA `G-48HWEVBSFR`, math on, dark-mode toggle, search, CJK | — | Carry over to `_quarto.yml` |
| Deploy | GitHub Actions (`gh-pages.yml`) → `peaceiris` → `gh-pages` branch | — | Replace with `quarto-actions` |

The current CV (the rendering target for the auto-CV) contains: Personal Data, Research Interests, Education (3), Employment (7), **Awards (8)**, **Grants (11)**, Papers (74), Book chapters & invited review (12), Invited talks & seminars (40). Awards/Grants/Education/Employment/Interests are **not** in BibTeX and will be encoded as structured source.

## 3. Target architecture

### 3.1 Project layout (Quarto website)
```
_quarto.yml              # site config: theme, navbar, search, GA, pre-render hook
index.qmd                # Home: photo, bio, interests, education, contact + recent news
publications.qmd         # includes generated _gen/publications.md
talks.qmd                # includes generated _gen/talks.md
projects.qmd             # ongoing + past
people.qmd               # postdocs & visitors (+ links, or links.qmd)
cv.qmd                   # full CV → HTML + PDF (structured + bib-driven)
news/                    # one .qmd per news item + listing
references.bib           # papers (source of truth)
talks.bib                # presentations (source of truth, with `invited`)
scripts/render_bib.py    # bib → markdown partials (pre-render)
_gen/                    # generated partials (git-ignored): publications.md, talks.md, cv_*.md
assets/                  # avatar, css, csl
.github/workflows/publish.yml
```

### 3.2 Theme & chrome
- `theme: [litera, darkly]` (clean, readable, academic; trivially swappable — e.g. cosmo/flatly). Light+dark toggle.
- Built-in Quarto **search** (on by default).
- `google-analytics: "G-48HWEVBSFR"`.
- Navbar: **Home · Publications · Talks · Projects · People · CV**. Links → footer or People page. Contact (email/address) on Home; drop the interactive map (keep address text) for simplicity.
- Math: Quarto HTML MathJax (default); `$...$` in titles render fine.

### 3.3 Bib → content conversion (the core mechanism)

**Recommended: a `pre-render` Python script** (`scripts/render_bib.py`, dep: `bibtexparser`) that reads `references.bib` + `talks.bib` and emits markdown partials into `_gen/`. Wired via `_quarto.yml`:
```yaml
project:
  pre-render: python scripts/render_bib.py
```
The script:
- sorts entries reverse-chronological;
- groups papers into **Journal articles** vs **Book chapters & invited reviews** (category tag, see §3.4);
- groups talks into **Invited talks & seminars** (`invited=true`) vs **Other**, and Upcoming vs Past by date;
- **bold-faces “Tadano”** in author lists;
- renders per-entry links (DOI / PDF / code) when present;
- emits: `_gen/publications.md`, `_gen/talks.md`, `_gen/cv_papers.md`, `_gen/cv_reviews.md`, `_gen/cv_talks.md`.

Internal structure: `load_bibs → validate → normalize → render`. The **validate** stage fails fast on: missing `title`/date/`year`, duplicate keys, unparseable dates, invalid `invited` values, unknown `keywords` category; and emits a report of any untagged/non-journal entries. `_gen/` is git-ignored and fully disposable.

Pages and the CV `{{< include >}}` these partials, so **web and PDF use identical data and identical formatting**, matching the existing CV’s numbered style. This directly realizes “one BibTeX → webpage or PDF.”

**Fallback (simpler, less control):** Pandoc citeproc with `nocite: "@*"` + a CSL style — flat reverse-chronological list, DOI links via CSL, no type grouping without splitting bib files. Documented as plan B if the script proves not worth it.

### 3.4 BibTeX schema (locked before authoring — Phase 2 prerequisite)
- `references.bib` (`@article`/`@incollection`/`@inproceedings`): **required** `author`, `title`, `year`; recommended `journal`/`booktitle`, `volume`, `pages`. Keep generated keys (`Tadano2024-ee`, …; already unique). **Category** via `keywords` ∈ {`journal`, `review`} (the ~12 reviews/chapters tagged `review`; default `journal`). Optional `doi`, `url` (enriched from per-folder `index.md` where present).
- `talks.bib` (`@misc`, **~93 entries**): **required** `author`, `title`, `year`, `date` (ISO), `event`, `location`, **`type` ∈ {`invited`,`oral`,`poster`}**, **`scope` ∈ {`international`,`domestic`}**; `invited = {true}` iff `type=invited` (do **not** reuse Hugo `featured`). Optional `url`. Sourced: invited (40) from CV, oral (25)+poster (28) from `all_presentations.md`, enriched from event folders. Upcoming vs past derived from `date` at render time (never hand-encoded).
- The renderer validates against these schemas and **fails the build** on violations (see §3.3).

### 3.5 CV (`cv.qmd`)
- `format: { html: default, pdf: default }` → one source, an HTML CV page **and** a downloadable PDF.
- Structured sections written inline (seeded from current `CV_Tadano.pdf`): Personal Data, Research Interests, Education, Employment, Awards, Grants.
- Publications & talks via the generated partials (`_gen/cv_*.md`).
- **PDF + Japanese:** the CV contains substantial Japanese (book chapters, talks). PDF must use `pdf-engine: lualatex` (or `xelatex`) with a CJK-capable font (e.g. **Noto Serif CJK JP** via `luatexja`/`fontspec`). This is the **main technical risk** and requires CJK fonts + packages in CI.

## 4. Deployment
- **Single path:** one new `.github/workflows/publish.yml` using `quarto-dev/quarto-actions/{setup,render}` → `actions/deploy-pages` (artifact-based; set Pages source = “GitHub Actions”). Keep `.nojekyll`.
- **Remove the 3 stale Hugo workflows** as part of cutover: `gh-pages.yml` (live, master→gh-pages via peaceiris), `publish.yaml` (dormant, →main), and **`import-publications.yml`** (dormant HugoBlox bib importer — must go so it can’t fight the new pipeline).
- CI installs **TinyTeX + Noto CJK** (prefer `apt-get install fonts-noto-cjk` + `xelatex` first; `lualatex`/`luatexja` only if finer JP typography is needed) so the PDF CV builds. Add a CI assertion that the PDF exists and is non-trivially sized (don’t trust exit code alone).
- baseURL stays root (`https://ttadano.github.io/`).

## 4.1 Redirects / URL stability (deliverable)
Old → new URLs change; some are externally cited (Google Scholar, etc.). Preserve via Quarto `aliases` (and/or a static `_redirects`/`<meta refresh>`):
- `/publication/<slug>/` (87) — add `aliases` on a publications anchor or per-slug stubs for any known-cited ones.
- `/talk/<slug>/` (Hugo `event` permalink) → new talks page.
- `/featured`, `/home/students`, `/home/links` → new pages.
- **`/uploads/CV_Tadano.pdf`** — keep this exact path serving a PDF (the generated CV or the legacy file) so existing CV links don’t 404.
Enumerate the must-keep set during Phase 0; default to the publications list anchor for the long tail.

## 5. Migration mechanics
1. Work on a branch `quarto-migration`; keep Hugo files until the Quarto site is verified, then remove them in the cutover commit.
2. Build & verify locally (`quarto preview`) and on a deploy preview before switching the Pages source.
3. Preserve assets: `avatar.jpg`, and keep hosting the old `CV_Tadano.pdf` until the generated PDF is signed off.
4. Add redirects/aliases for any externally-linked old URLs if needed (e.g. `/publication/...`). Low priority — academic deep links are rare; can add a few `aliases`.

## 6. Phased implementation
0. **Inventory audit & decisions** (no code): generate the real-vs-demo publication table (flag `tadano-2023-butsuri` no-cite.bib, reconcile vs CV 86); reconcile 39 featured events ↔ 40 CV invited; enumerate must-keep redirect URLs; lock the §3.4 BibTeX schemas; pick the single deploy path.
1. **Scaffold + CJK smoke test**: Quarto project, theme, navbar, search, GA, empty pages; **remove the 3 stale Hugo workflows**; new `publish.yml`; render a tiny Japanese `cv-smoke.qmd` PDF **in CI** to prove `xelatex`+Noto CJK *before* migrating content.
2. **Bibs**: author `references.bib` (merge ~83 real `cite.bib` + hand-add `tadano-2023-butsuri`, drop demos, tag `keywords`, enrich DOI) + `talks.bib` (events + CV invited; dedupe vs `all_presentations.md`), validated against the locked schemas.
3. **Converter**: `render_bib.py` (`load→validate→normalize→render`) + pre-render wiring; build Publications & Talks pages.
4. **Content (hand-authored)**: Home (bio/interests/education/contact), News listing, Projects, People, Links — kept out of the data pipeline.
5. **CV**: structured sections + bib-driven lists; HTML + PDF (CJK already proven in Phase 1).
6. **Cutover**: switch Pages source; add redirects/`aliases`; keep legacy `CV_Tadano.pdf` + old deep links live until signed off; remove Hugo `content/` last.
7. **QA**: confirm all ~84 publications + all talks present (diff against CV); link check; render check; visual pass; PDF (incl. Japanese) check + size assertion.

## 7. Risks / open questions (for review)
- **R1 — Japanese in PDF CV.** Needs lualatex/xelatex + Noto CJK in CI; highest-risk item. Fallback: commit a locally-built PDF.
- **R2 — Talks authoring effort.** ~48 events + 40 invited must be reconciled into `talks.bib`; talks-in-BibTeX is verbose. Source priority: event `index.md` (has venue/url) cross-checked against the CV list. Confirm `invited` flagging rule (CV “Invited talks & seminars” ⇒ `invited=true`).
- **R3 — Journal vs review tagging.** ~12 reviews/chapters must be tagged in `references.bib`; derive from existing `publication_types`/by hand.
- **R4 — Converter vs citeproc.** Pre-render Python script (full control, one consistent style, Python dep) vs citeproc+CSL (simplest, limited grouping). Plan recommends the script; is that acceptable, or prefer pure-Quarto citeproc?
- **R5 — Bib data quality.** `academic`-tool escaping quirks (e.g. `_\8\`), math in titles, missing DOIs, dedup. Mitigated by parsing + a normalization pass.
- **R6 — CV fidelity.** Exact numbered citation style and section ordering of the current CV to be reproduced by the converter.
- **R7 — URL stability.** Old `/publication/<slug>/`, `/talk/*`, `/featured`, `/uploads/CV_Tadano.pdf` change; handled by §4.1 redirect deliverable.
- **R8 — Inventory drift.** `tadano-2023-butsuri` has no `cite.bib`; counts differ across site (87/85/84) and CV (86); Phase 0 audit is the gate against silent content loss.
- **R9 — Competing workflows.** Three Hugo workflows exist; the dormant `import-publications.yml` writes Hugo pages from a `publications.bib` and must be removed so it can’t clobber the new pipeline. Pick one Pages deploy path before writing config.
