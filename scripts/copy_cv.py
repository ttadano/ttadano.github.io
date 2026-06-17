#!/usr/bin/env python3
"""Post-render: also expose the generated CV at the legacy /uploads/CV_Tadano.pdf
path, so existing links (e.g. from the Google Scholar profile) keep working."""
import pathlib, shutil

src = pathlib.Path("_site/CV_Tadano.pdf")
if src.exists():
    dst = pathlib.Path("_site/uploads")
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy(src, dst / "CV_Tadano.pdf")
    print(f"copy_cv: {src} -> {dst / 'CV_Tadano.pdf'}")
else:
    print("copy_cv: _site/CV_Tadano.pdf not present (HTML-only render); skipped")
