"""Command line: normasheets build | init | blocks."""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from .blocks import RENDERERS, SpecError

PKG = Path(__file__).parent


def _print_reports(reports) -> int:
    errors = 0
    for r in reports:
        status = "FAIL" if r.errors else ("warn" if r.warnings else " ok ")
        gap = f"footer gap {r.gap}px" if r.gap is not None else ""
        print(f"[{status}] {r.name:<32} {gap}")
        for e in r.errors:
            print(f"        x {e}")
        for w in r.warnings:
            print(f"        ! {w}")
        errors += len(r.errors)
    print(f"\n{len(reports)} sheet(s), {errors} error(s), {sum(len(r.warnings) for r in reports)} warning(s)")
    return errors


def cmd_build(a) -> int:
    from .render import build, load_series
    try:
        series = load_series(Path(a.path))
    except (SpecError, FileNotFoundError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    only = {int(x) for x in a.only.split(",")} if a.only else None
    formats = tuple(f.strip() for f in a.formats.split(","))
    reports = build(series, out_dir=a.out, formats=formats, only=only, keep_html=not a.no_html)
    errors = _print_reports(reports)
    out = Path(a.out) if a.out else series.root / series.cfg["output"]
    print(f"output: {out}")
    return 1 if (errors and a.strict) else 0


def cmd_init(a) -> int:
    dst = Path(a.path)
    if dst.exists() and any(dst.iterdir()):
        print(f"error: {dst} is not empty", file=sys.stderr)
        return 2
    shutil.copytree(PKG / "scaffold", dst, dirs_exist_ok=True)
    cfg = dst / "series.yaml"
    cfg.write_text(cfg.read_text("utf-8").replace("{SERIES}", a.series).replace("{AUTHOR}", a.author), "utf-8")
    print(f"created {dst}\n  edit {dst}/01-intro.yaml, then:  normasheets build {dst}")
    return 0


def cmd_blocks(a) -> int:
    from . import blocks
    for name in sorted(RENDERERS):
        doc = (RENDERERS[name].__doc__ or "").strip().splitlines()
        print(f"  {name:<12} {doc[0] if doc else ''}")
    print("\nFull reference with examples: README.md")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="normasheets", description="NoRMA: Notes Rendered as Math Artwork. Build cheat sheets (JPG + PDF carousel) from YAML.")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="render a series folder (or one sheet .yaml)")
    b.add_argument("path")
    b.add_argument("--only", help="sheet numbers, e.g. 1,3,5")
    b.add_argument("--formats", default="jpg,pdf", help="jpg,pdf,png (default jpg,pdf)")
    b.add_argument("--out", help="output folder (default from series.yaml)")
    b.add_argument("--no-html", action="store_true", help="delete intermediate HTML")
    b.add_argument("--strict", action="store_true", help="exit 1 if any layout error")
    b.set_defaults(fn=cmd_build)

    i = sub.add_parser("init", help="create a new series from the starter template")
    i.add_argument("path")
    i.add_argument("--series", default="My series")
    i.add_argument("--author", default="Your Name")
    i.set_defaults(fn=cmd_init)

    k = sub.add_parser("blocks", help="list block types")
    k.set_defaults(fn=cmd_blocks)

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
