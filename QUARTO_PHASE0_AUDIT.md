# Phase 0 — Inventory Audit & Decisions

Read-only audit (no site changes). Date: 2026-06-17. Companion to `QUARTO_MIGRATION_PLAN.md`.

## A. Publications

**87 folders → 84 real publications + 3 demos to drop.**

Demos (drop): `preprint/` (“An example preprint”), `conference-paper/` (`example1`), `journal-article/` (“Journal of Source Themes”).

### Category split (drives `references.bib` `keywords`)
| Category | Count | `keywords` tag | Notes |
|---|---|---|---|
| Journal articles (peer-reviewed) | 71 | `journal` | incl. 1 `@inproceedings` (`tadano-2015-gr`, AIP) |
| arXiv preprints | 4 | `preprint` | `asai-2025-fr`, `ohnishi-2025-cy`, `pohle-2025-ja`, `xiao-2025-st` |
| JP reviews / magazine articles | 8 | `review` | `tadano-2024-ee`(セラミックス), `tadano-2023-butsuri`(日本物理学会誌), `masuki-2023-zn`+`nomura-2020-px`+`tadano-2020-yq`+`tadano-2017-mw`(固体物理), `2020-lb`(応用物理), `tadano-2020-fy`(シミュレーション) |
| Technical report | 1 | `report` | `tadano-2019-vn` (ISSP Supercomputer Center Activity Report) |
| **Real total** | **84** | | |

### Data-quality findings (for Phase 2)
- **`tadano-2023-butsuri` has no `cite.bib`** (only `index.md`) → must author its BibTeX entry by hand. *(Codex’s catch — confirmed.)*
- **`hirayama-2022-xy`** is an arXiv preprint (arXiv:2207.12595) but its `cite.bib` has an **empty `journal`** → add the arXiv id.
- **DOIs are sparse:** only **17 of 85** `cite.bib` carry a DOI; 3 carry `url_pdf`. Web DOI/PDF links will therefore be present for a minority. Optional later enrichment via Crossref; out of scope for “simple”.
- The HugoBlox `publication_types` field is **unreliable** for categorization (the `article` type is used for *both* arXiv preprints and JP magazines). Categorization above is keyed off **venue**, not pubtype.

### Reconciliation vs current CV (`CV_Tadano.pdf`, updated 2026-01-22)
CV lists **74 Papers + 12 Book chapters/reviews = 86**. Website has **84**.
- **Papers:** site 71+4 preprints = 75 ≈ CV 74 (±1; settle line-by-line in Phase 2).
- **Reviews:** site has **8**; CV has **12** → **4 book chapters are NOT on the website** and must be authored from CV text if the auto-CV is to match:
  1. FC レポート Vol. 42, 59–63 (2025)
  2. 計算科学を活用した熱電変換材料… CMC (2022)
  3. マイクロ・ナノ熱工学の進展… NTS (2021)
  4. フォノンエンジニアリング… NTS (2017)

**Decisions (publications):**
- **P1. ✅ DECIDED — add all 4.** Hand-author the 4 missing book chapters into `references.bib` (`keywords=review`) so the auto-CV matches the current CV’s 12-item review section. They will also appear on the website publications page.
- **P2. ✅ DECIDED — drop.** `tadano-2019-vn` (internal ISSP activity report; not in CV) will be excluded. ⇒ Real publications carried forward = **83** (84 − report) **+ 4 book chapters = 87 entries in `references.bib`** (71 journal + 4 preprint + 12 review).

## B. Talks / presentations — three sources disagree

| Source | Invited | Oral | Poster | Total | Currency |
|---|---|---|---|---|---|
| `content/event/*` folders | 39 (`featured:true`) | 8 contributed | — | **47 real** (+1 demo `example`) | current-ish |
| CV “Invited talks & seminars” | **40** | — | — | 40 | **current (2026-01)** ✅ |
| `all_presentations.md` | 29 | 25 | 28 | **82** | **STALE** (invited list ends 2022) |

Findings:
- The **CV (40 invited)** is the authoritative, most-current source for invited talks; event folders (39) are nearly aligned (±1).
- `all_presentations.md` is the **only** source for the **~53 contributed oral+poster** presentations, but its *invited* section is outdated (last entry 2022).
- Event folders carry structured `event`/`location`/`date`/URLs; the markdown lists are plain text.

**Decisions (talks):**
- **T1. ✅ DECIDED — (B) Everything in BibTeX (~93).** `talks.bib` holds invited + oral + poster as `@misc` entries with required `type` ∈ {invited, oral, poster} and `scope` ∈ {international, domestic}. Sourcing: **invited (40) from the CV** (authoritative/current); **oral (25) + poster (28) from `all_presentations.md`**; enrich venue/location/date/URLs from event folders where a match exists. `invited = {true}` iff `type=invited`.
  - ⚠️ Authoring note: `all_presentations.md`’s *invited* section is stale (ends 2022) — ignore it for invited and use the CV. Posters/orals must be transcribed from plain-text bullets into structured `@misc` (the heaviest authoring task in the migration). Each entry needs `date` parsed from the JP/EN bullet (some have only month/year).
- **T2. ✅ invited rule:** `type=invited`/`invited=true` for every CV “Invited talks & seminars” entry (40); the 39↔40 event-folder gap is expected (recent 2025 talks lack folders) and resolved by sourcing invited from the CV.

## C. Redirects / URL stability (GitHub Pages, **no custom domain**)

Old URL patterns (Hugo): `/publication/<slug>/` (84), `/talk/<slug>/` (event permalink, 47), `/tag/*`, `/category/*`, `/publication-type/*`, menu paths `/featured`, `/talks`, `/project`, `/home/students`, `/home/links`, and **`/uploads/CV_Tadano.pdf`**.

GitHub Pages has no server-side redirects → use **Quarto `aliases`** (emit static meta-refresh stubs).
- **Must keep:** `/uploads/CV_Tadano.pdf` (CV link on Scholar/elsewhere) — serve the generated PDF at this exact path.
- **Nice to have:** redirect `/publication/` and `/talk/` roots → new list pages.
- **Skip** per-slug stubs for all 84+47 unless you know specific externally-cited deep links (academic citations point to DOIs, not Hugo pages). Low risk.

## D. Deployment decision

- **Current live path:** `gh-pages.yml` → `peaceiris/actions-gh-pages` → **`gh-pages` branch** (`publish_dir: ./public`). Pages source = gh-pages branch.
- Dormant: `publish.yaml` (→`main`, `actions/deploy-pages`) and `import-publications.yml` (HugoBlox bib importer, →`main`).
- **Decision:** new single `publish.yml` via **`quarto-actions` + `actions/deploy-pages`** (Pages source → “GitHub Actions”). **Remove all three** old workflows at cutover. *(User-approved deploy path.)*

## E. BibTeX schemas — FINAL (refined in Phase 2 after Codex review)

- `references.bib` (**87 entries**: 70 journal + 5 preprint + 12 review): required `author,title,year`; `keywords` ∈ {journal, preprint, review} (the `report` category was dropped with `tadano-2019-vn`); optional `doi,url,eprint,archiveprefix`.
- `talks.bib` (**100 entries**: 40 invited + 32 oral + 28 poster): required `author,title,venue,date(ISO, variable precision),year,presentationtype{invited|oral|poster},scope{international|domestic},invited(bool, true iff presentationtype=invited)`; optional `url`.
  - **Refinements vs the originally-locked schema** (from Codex review): `type`→`presentationtype` (avoids BibLaTeX `type` collision); `event`+`location` merged into a single `venue` (source data doesn't cleanly separate them); dates use variable ISO precision (`YYYY`/`YYYY-MM`/`YYYY-MM-DD`) rather than inventing days; CJK author names brace-protected (`{只野央将}`).
  - **Sourcing**: invited (40) + recent contributed (8) from structured event folders (reliable ISO dates); older oral/poster from `all_presentations.md`. The Paris HANAMI talk was `featured:false` in its folder but is invited per the CV — corrected (reconciles the 39↔40 gap).

## F. Phase 0 result — COMPLETE ✅

Inventory reconciled; demos and data-quality issues identified; schemas locked; deploy path fixed; redirect policy set; **all decisions resolved (P1 add-4, P2 drop-report, T1 full ~93-entry talks.bib, T2 invited-from-CV).**

**Deliverable sizes for Phase 2:** `references.bib` ≈ **87 entries** (71 journal + 4 preprint + 12 review); `talks.bib` ≈ **93 entries** (40 invited + 25 oral + 28 poster). Heaviest task = transcribing oral/poster bullets from `all_presentations.md` into structured `@misc`.

Ready for **Phase 1** (scaffold Quarto + remove 3 stale workflows + CJK-PDF CI smoke test).
