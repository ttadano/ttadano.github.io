#!/usr/bin/env python3
"""Convert references.bib + talks.bib into Markdown partials under _gen/.

Runs as a Quarto `pre-render` step. Uses only the Python standard library so it
works under any python3 (locally and in CI) with no third-party dependency.

Pipeline: load -> validate (fail-fast) -> render. Bib fields are expected to be
single-line (the project's bib style); the parser is brace-balanced so nested
braces and $math$ in values are handled.
"""
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
GEN = ROOT / "_gen"


# ---------- parsing ----------
def parse_bib(text):
    entries, i, n = [], 0, len(text)
    while i < n:
        if text[i] != "@":
            i += 1
            continue
        j = text.index("{", i)
        etype = text[i + 1 : j].strip().lower()
        k = text.index(",", j)
        key = text[j + 1 : k].strip()
        depth, p = 0, j
        while p < n:
            if text[p] == "{":
                depth += 1
            elif text[p] == "}":
                depth -= 1
                if depth == 0:
                    break
            p += 1
        fields = parse_fields(text[k + 1 : p])
        fields["ENTRYTYPE"], fields["ID"] = etype, key
        entries.append(fields)
        i = p + 1
    return entries


def parse_fields(body):
    f, i, n = {}, 0, len(body)
    while i < n:
        while i < n and body[i] in " \t\r\n,":
            i += 1
        m = re.match(r"([A-Za-z][\w-]*)\s*=\s*", body[i:])
        if not m:
            break
        name = m.group(1).lower()
        i += m.end()
        if i < n and body[i] == "{":
            depth, s = 0, i
            while i < n:
                if body[i] == "{":
                    depth += 1
                elif body[i] == "}":
                    depth -= 1
                    if depth == 0:
                        i += 1
                        break
                i += 1
            val = body[s + 1 : i - 1]
        elif i < n and body[i] == '"':
            s = i + 1
            i += 1
            while i < n and body[i] != '"':
                i += 1
            val = body[s:i]
            i += 1
        else:
            s = i
            while i < n and body[i] != ",":
                i += 1
            val = body[s:i]
        f[name] = " ".join(val.split())
    return f


# ---------- validation ----------
def die(msg):
    print(f"render_bib: ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def validate_refs(refs):
    seen = set()
    for e in refs:
        k = e["ID"]
        if k in seen:
            die(f"duplicate reference key: {k}")
        seen.add(k)
        for req in ("author", "title", "year"):
            if not e.get(req):
                die(f"reference {k} missing required field '{req}'")
        if e.get("keywords") not in ("journal", "preprint", "review"):
            die(f"reference {k} has invalid keywords={e.get('keywords')!r}")


def validate_talks(talks):
    seen = set()
    for e in talks:
        k = e["ID"]
        if k in seen:
            die(f"duplicate talk key: {k}")
        seen.add(k)
        for req in ("author", "title", "venue", "date", "presentationtype", "scope", "invited"):
            if not e.get(req):
                die(f"talk {k} missing required field '{req}'")
        if e["presentationtype"] not in ("invited", "oral", "poster"):
            die(f"talk {k} invalid presentationtype={e['presentationtype']!r}")
        if e["scope"] not in ("international", "domestic"):
            die(f"talk {k} invalid scope={e['scope']!r}")
        if not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?", e["date"]):
            die(f"talk {k} invalid date={e['date']!r}")
        if (e["invited"] == "true") != (e["presentationtype"] == "invited"):
            die(f"talk {k} invited/presentationtype mismatch")


# ---------- formatting ----------
def fmt_name(name):
    name = name.strip().strip("{}").strip()
    if "," in name:
        last, first = [x.strip() for x in name.split(",", 1)]
        inits = " ".join(p[0] + "." for p in re.split(r"[ .]+", first) if p)
        out = f"{inits} {last}".strip()
    else:
        out = name
    if "Tadano" in out or "只野" in out:
        out = f"**{out}**"
    return out


def authors(s):
    names = [fmt_name(x) for x in re.split(r"\s+and\s+", s) if x.strip()]
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


MON = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fmt_date(iso):
    p = iso.split("-")
    if len(p) == 3:
        return f"{MON[int(p[1])]} {int(p[2])}, {p[0]}"
    if len(p) == 2:
        return f"{MON[int(p[1])]} {p[0]}"
    return p[0]


def pub_line(e):
    a, t = authors(e["author"]), e["title"].strip().rstrip(".")
    if e["keywords"] == "preprint":
        ep = e.get("eprint", "")
        if ep:
            return f'{a}, "{t}", arXiv:{ep} ({e["year"]}). [arXiv](https://arxiv.org/abs/{ep})'
        return f'{a}, "{t}", {e.get("journal", "preprint")} ({e["year"]}).'
    if e["ENTRYTYPE"] == "incollection" or not e.get("journal"):
        venue = ", ".join(x for x in [f"*{e['booktitle']}*" if e.get("booktitle") else "", e.get("publisher", "")] if x)
        return f'{a}, "{t}", {venue} ({e["year"]}).'
    bits = f"*{e['journal']}*"
    if e.get("volume"):
        bits += f" **{e['volume']}**"
    if e.get("pages"):
        bits += f", {e['pages']}"
    s = f'{a}, "{t}", {bits} ({e["year"]}).'
    if e.get("doi"):
        s += f" [DOI](https://doi.org/{e['doi']})"
    return s


def talk_line(e):
    a, t = authors(e["author"]), e["title"].strip().rstrip(".")
    s = f'{a}, "{t}", {e["venue"]}, {fmt_date(e["date"])}.'
    if e.get("url"):
        s += f" [link]({e['url']})"
    return s


def numbered(items):
    return "\n".join(f"{i}. {x}" for i, x in enumerate(items, 1)) if items else "*None yet.*"


MON_NUM = {m.lower(): i for i, m in enumerate(MON) if m}


def sort_key(e):
    if e.get("date"):  # talks: precise ISO date
        return e["date"]
    mn = MON_NUM.get(e.get("month", "")[:3].lower(), 0)  # refs: year + month
    return f"{e.get('year', '0000')}-{mn:02d}"


def by_desc(entries):
    return sorted(entries, key=lambda e: (sort_key(e), e["ID"]), reverse=True)


def year_grouped(entries, line_fn):
    """entries pre-sorted desc; emit '### <year>' subsections with bulleted items
    (so the page's right-hand TOC lists years)."""
    out, cur = [], None
    for e in entries:
        y = e.get("year") or e.get("date", "")[:4]
        if y != cur:
            out.append(f"\n### {y}\n")
            cur = y
        out.append(f"- {line_fn(e)}")
    return "\n".join(out).strip() if out else "*None yet.*"


def talk_line_web(e):
    s = talk_line(e)
    if e["presentationtype"] != "invited":  # scope shown inline (no scope subsections on web)
        s = f"*[{'International' if e['scope'] == 'international' else 'Domestic'}]* " + s
    return s


# ---------- main ----------
def main():
    GEN.mkdir(exist_ok=True)
    refs = parse_bib((ROOT / "references.bib").read_text(encoding="utf-8"))
    talks = parse_bib((ROOT / "talks.bib").read_text(encoding="utf-8"))
    validate_refs(refs)
    validate_talks(talks)

    jour = by_desc([e for e in refs if e["keywords"] == "journal"])
    prep = by_desc([e for e in refs if e["keywords"] == "preprint"])
    revs = by_desc([e for e in refs if e["keywords"] == "review"])
    # Web page: grouped by type (##) then year (###) so the right-hand TOC lists years.
    (GEN / "publications.md").write_text(
        "## Journal Articles\n\n" + year_grouped(jour, pub_line)
        + "\n\n## Preprints\n\n" + year_grouped(prep, pub_line)
        + "\n\n## Reviews & Book Chapters\n\n" + year_grouped(revs, pub_line) + "\n",
        encoding="utf-8",
    )

    inv = by_desc([e for e in talks if e["presentationtype"] == "invited"])
    orals = by_desc([e for e in talks if e["presentationtype"] == "oral"])
    posters = by_desc([e for e in talks if e["presentationtype"] == "poster"])
    (GEN / "talks.md").write_text(
        "## Invited Talks & Seminars\n\n" + year_grouped(inv, talk_line_web)
        + "\n\n## Oral Presentations\n\n" + year_grouped(orals, talk_line_web)
        + "\n\n## Poster Presentations\n\n" + year_grouped(posters, talk_line_web) + "\n",
        encoding="utf-8",
    )

    # CV partials (consumed in Phase 5)
    (GEN / "cv_papers.md").write_text(numbered([pub_line(e) for e in by_desc(jour + prep)]) + "\n", encoding="utf-8")
    (GEN / "cv_reviews.md").write_text(numbered([pub_line(e) for e in revs]) + "\n", encoding="utf-8")
    (GEN / "cv_talks.md").write_text(numbered([talk_line(e) for e in inv]) + "\n", encoding="utf-8")

    print(f"render_bib: {len(refs)} refs (journal {len(jour)}, preprint {len(prep)}, review {len(revs)}); "
          f"{len(talks)} talks (invited {len(inv)}, oral {len(orals)}, poster {len(posters)}) -> _gen/")


if __name__ == "__main__":
    main()
