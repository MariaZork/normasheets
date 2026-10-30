"""Load a series, render each sheet to HTML, screenshot it, run layout checks, export JPG + PDF."""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader
from markupsafe import Markup

from .blocks import SpecError, grid_template, render_blocks
from .inline import color_value, inline

PKG = Path(__file__).parent
ASSETS = PKG / "assets"

DEFAULTS = {
    "series": "",
    "author": "",
    "kicker": "Cheat sheet · {series}",
    "byline": "Prepared by **{author}**",
    "size": {"width": 1080, "height": 1350, "scale": 2},
    "jpg_quality": 93,
    "theme": "dark",
    "palette": {},
    "macros": {},
    "lint": {"forbid": []},
    "output": "out",
    "pdf": "series.pdf",
    "pdf_mode": "raster",   # raster: pages are the exact JPG renders (same look in every viewer); vector: selectable text
    "figures": "figures.py",
    "min_footer_gap": 10,
    "max_free_space": 140,
    "extra_css": "",
    "logo": "",
    "credit": "made with **NoRMA** · github.com/mariazork/normasheets",
}


@dataclass
class Series:
    root: Path
    cfg: dict
    sheets: list  # list[(path, dict, raw_text)]
    figures: dict = field(default_factory=dict)


@dataclass
class Report:
    name: str
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    gap: float | None = None
    outputs: list = field(default_factory=list)


# ------------------------------------------------------------------ loading
def _merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_series(path: Path) -> Series:
    path = Path(path).resolve()
    if path.is_file():
        root, only = path.parent, [path]
    else:
        root, only = path, None
    cfg_file = root / "series.yaml"
    cfg = _merge(DEFAULTS, yaml.safe_load(cfg_file.read_text("utf-8")) if cfg_file.exists() else {})
    if only is None:
        listed = cfg.get("sheets")
        files = [root / f for f in listed] if listed else sorted(
            p for p in root.glob("*.yaml") if p.name != "series.yaml")
    else:
        files = only
    sheets = []
    for f in files:
        raw = f.read_text("utf-8")
        try:
            data = yaml.safe_load(raw) or {}
        except yaml.YAMLError as e:
            raise SpecError(f"{f.name}: YAML error: {e}") from e
        sheets.append((f, data, raw))
    s = Series(root=root, cfg=cfg, sheets=sheets)
    s.figures = load_figures(root / cfg["figures"])
    return s


def load_figures(path: Path) -> dict:
    if not path.exists():
        return {}
    spec = importlib.util.spec_from_file_location(f"norma_figures_{abs(hash(path))}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.pop(0)
    return {k: v for k, v in vars(mod).items() if callable(v) and not k.startswith("_")
            and getattr(v, "__module__", None) == mod.__name__}


# ------------------------------------------------------------------ HTML
class Ctx:
    def __init__(self, figures):
        self.figures = figures


def render_card(card: dict, ctx: Ctx) -> str:
    style = card.get("style", "")
    classes = ["card", style, "dense" if card.get("dense") else ""]
    css = []
    if card.get("math_size"):
        css.append(f"--ms:{card['math_size']}")
    if card.get("pad"):
        css.append(f"padding:{card['pad']}")
    head = ""
    if card.get("title"):
        dot = color_value(card.get("dot", "cyan"))
        tcls = "plain" if card.get("plain_title") else ""
        aside = f' <span class="aside">· {inline(card["aside"])}</span>' if card.get("aside") else ""
        head = (f'<h2><i class="dot" style="background:{dot}"></i>'
                f'<span class="{tcls}">{inline(card["title"])}</span>{aside}</h2>')
    st = f' style="{";".join(css)}"' if css else ""
    return f'<div class="{" ".join(c for c in classes if c)}"{st}>{head}{render_blocks(card.get("blocks"), ctx)}</div>'


def render_rows(rows, ctx: Ctx) -> str:
    out = []
    for r in rows or []:
        if "cards" not in r:  # a single card used as a full-width row
            r = {"cards": [r]}
        cards = r["cards"]
        css = [f"grid-template-columns:{grid_template(r.get('cols'), len(cards))}"]
        if r.get("align"):
            css.append(f"align-items:{r['align']}")
        if r.get("gap") is not None:
            css.append(f"gap:{r['gap']}px")
        if r.get("mt") is not None:
            css.append(f"margin-top:{r['mt']}px")
        out.append(f'<div class="row" style="{";".join(css)}">' + "".join(render_card(c, ctx) for c in cards) + "</div>")
    return "\n".join(out)


def build_html(series: Series, sheet: dict) -> str:
    cfg = series.cfg
    env = Environment(loader=FileSystemLoader(str(PKG / "templates")), autoescape=True)
    theme_path = Path(cfg["theme"])
    if not theme_path.suffix:
        theme_path = PKG / "themes" / f"{cfg['theme']}.css"
    elif not theme_path.is_absolute():
        theme_path = series.root / theme_path
    assets = ASSETS.resolve().as_uri()
    theme_css = theme_path.read_text("utf-8").replace("ASSETS", assets)
    fmt = {"series": cfg["series"], "author": cfg["author"], "number": sheet.get("number", "")}
    footer = sheet.get("footer") or {}
    ctx = Ctx(series.figures)
    return env.get_template("sheet.html.j2").render(
        sheet={"title": sheet.get("title", ""), "accent": sheet.get("accent", ""),
               "number": sheet.get("number"), "header_gap": sheet.get("header_gap")},
        title=inline(sheet.get("title", "")), accent=inline(sheet.get("accent", "")),
        subtitle=inline(sheet.get("subtitle", "")),
        kicker=inline(sheet.get("kicker", cfg["kicker"]).format(**fmt)),
        byline=inline(cfg["byline"].format(**fmt)) if cfg.get("author") else "",
        footer_left=inline(str(footer.get("left", cfg.get("footer_left", ""))).format(**fmt)),
        footer_right=inline(str(footer.get("right", cfg.get("footer_right", ""))).format(**fmt)),
        body=Markup(render_rows(sheet.get("rows"), ctx)),
        size=cfg["size"], palette=cfg.get("palette") or {},
        theme_css=Markup(theme_css), extra_css=Markup(cfg.get("extra_css", "") + sheet.get("extra_css", "")),
        macros=Markup(json.dumps(cfg.get("macros") or {})), assets=assets,
        credit=inline(cfg["credit"]) if cfg.get("credit") else "",
        logo=(series.root / cfg["logo"]).resolve().as_uri() if cfg.get("logo") else "",
    )


# ------------------------------------------------------------------ checks
QA_JS = r"""
() => {
  const R = {overflow: [], wraps: []};
  const name = el => { const c = el.closest('.card'); const h = c && c.querySelector('h2');
                       return h ? h.innerText.split('·')[0].trim().slice(0, 40) : '(no card)'; };
  const snip = el => (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 42);
  document.querySelectorAll('.card').forEach(card => {
    const cs = getComputedStyle(card), cr = card.getBoundingClientRect();
    const right = cr.right - parseFloat(cs.paddingRight) + 1, left = cr.left + parseFloat(cs.paddingLeft) - 1;
    card.querySelectorAll('.katex-display > .katex, svg, pre, table, .figure, .boxes, .tiles').forEach(el => {
      const r = el.getBoundingClientRect();
      const over = Math.max(r.right - right, left - r.left);
      if (over > 1) R.overflow.push({card: name(card), what: el.tagName.toLowerCase(), px: Math.round(over)});
    });
    card.querySelectorAll('pre').forEach(el => {
      const d = el.scrollWidth - el.clientWidth;
      if (d > 1) R.overflow.push({card: name(card), what: 'code line', px: d});
    });
  });
  const lines = el => { const cs = getComputedStyle(el); const lh = parseFloat(cs.lineHeight) || parseFloat(cs.fontSize) * 1.3;
                        const r = document.createRange(); r.selectNodeContents(el);
                        return r.getBoundingClientRect().height / lh; };
  document.querySelectorAll('td, th, .kv span, .chip, .card h2, .tag').forEach(el => {
    if (el.querySelector('.katex-display')) return;
    if (lines(el) > 1.6) R.wraps.push({card: name(el), text: snip(el)});
  });
  const bottoms = [...document.querySelectorAll('.card')].map(c => c.getBoundingClientRect().bottom);
  R.contentBottom = Math.max(...bottoms, 0);
  R.footerTop = document.querySelector('footer').getBoundingClientRect().top;
  const f = document.querySelector('footer'); R.footerOverflow = f.scrollWidth - f.clientWidth;
  R.tex = window.__texErrors || [];
  return R;
}
"""


def _strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _strings(v)


def lint(raw: str, cfg: dict, data=None) -> list:
    issues = []
    for s in _strings(data):
        if any(ord(c) < 32 and c not in "\n\t" for c in s):
            clean = "".join(c if ord(c) >= 32 or c in "\n\t" else "\\?" for c in s)[:60]
            issues.append(f"control character in \"{clean}\": a backslash was eaten by YAML double quotes; "
                          f"use single quotes '...' for LaTeX")
    for bad in (cfg.get("lint") or {}).get("forbid") or []:
        for i, line in enumerate(raw.splitlines(), 1):
            if bad in line:
                issues.append(f"line {i}: forbidden '{bad}'")
    return issues


# ------------------------------------------------------------------ build
def slug_of(path: Path) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", path.stem).strip("-")


def build(series: Series, out_dir: Path | None = None, formats=("jpg", "pdf"), only=None,
          keep_html=True, log=print) -> list:
    from playwright.sync_api import sync_playwright
    from pypdf import PdfReader, PdfWriter

    cfg = series.cfg
    out = Path(out_dir) if out_dir else series.root / cfg["output"]
    (out / "html").mkdir(parents=True, exist_ok=True)
    vector_pdf = "pdf" in formats and cfg.get("pdf_mode", "raster") == "vector"
    if vector_pdf:
        (out / "pdf").mkdir(parents=True, exist_ok=True)
    w, h, scale = cfg["size"]["width"], cfg["size"]["height"], cfg["size"].get("scale", 2)
    reports, pdf_pages, raster_pages = [], [], []

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=scale)
        for path, sheet, raw in series.sheets:
            num = sheet.get("number")
            if only and num not in only:
                continue
            slug = slug_of(path)
            rep = Report(name=f"#{num} {slug}" if num is not None else slug)
            reports.append(rep)
            rep.errors += lint(raw, cfg, sheet)
            try:
                html = build_html(series, sheet)
            except SpecError as e:
                rep.errors.append(str(e))
                continue
            html_path = out / "html" / f"{slug}.html"
            html_path.write_text(html, "utf-8")
            page.goto(html_path.resolve().as_uri())
            page.wait_for_function("window.__ready === true", timeout=20000)
            qa = page.evaluate(QA_JS)
            for t in qa["tex"]:
                rep.errors.append(f"KaTeX: {t['error']}  in  {t['tex'][:60]}")
            for o in qa["overflow"]:
                rep.errors.append(f"{o['what']} overflows card '{o['card']}' by {o['px']}px")
            gap = qa["footerTop"] - qa["contentBottom"]
            rep.gap = round(gap)
            if gap < cfg["min_footer_gap"]:
                rep.errors.append(f"content reaches the footer: gap {gap:.0f}px < {cfg['min_footer_gap']}px")
            elif gap > cfg["max_free_space"]:
                rep.warnings.append(f"{gap:.0f}px of free space above the footer")
            if qa["footerOverflow"] > 1:
                rep.errors.append("footer text does not fit on one line")
            for wr in qa["wraps"]:
                rep.warnings.append(f"wraps in '{wr['card']}': \"{wr['text']}\"")
            if "jpg" in formats:
                jp = out / f"{slug}.jpg"
                page.screenshot(path=str(jp), type="jpeg", quality=cfg["jpg_quality"])
                rep.outputs.append(jp)
            if "png" in formats:
                pp = out / f"{slug}.png"
                page.screenshot(path=str(pp), type="png")
                rep.outputs.append(pp)
            if "pdf" in formats and not vector_pdf:
                raster_pages.append(page.screenshot(type="jpeg", quality=max(cfg["jpg_quality"], 92)))
            if vector_pdf:
                pf = out / "pdf" / f"{slug}.pdf"
                page.pdf(path=str(pf), width=f"{w}px", height=f"{h}px", print_background=True,
                         prefer_css_page_size=True, page_ranges="1")
                pdf_pages.append(pf)
            if not keep_html:
                html_path.unlink(missing_ok=True)
        browser.close()

    title = cfg.get("series") or "Cheat sheets"
    if raster_pages:
        import io
        from PIL import Image
        imgs = [Image.open(io.BytesIO(b)).convert("RGB") for b in raster_pages]
        combined = out / cfg["pdf"]
        imgs[0].save(combined, "PDF", save_all=True, append_images=imgs[1:], resolution=72 * scale,
                     title=title, author=cfg.get("author", ""))
        log(f"PDF carousel: {combined}  ({len(imgs)} pages, raster)")
    if vector_pdf and pdf_pages:
        writer = PdfWriter()
        for pf in pdf_pages:
            writer.add_page(PdfReader(str(pf)).pages[0])
        writer.add_metadata({"/Title": title, "/Author": cfg.get("author", "")})
        combined = out / cfg["pdf"]
        with open(combined, "wb") as fh:
            writer.write(fh)
        log(f"PDF carousel: {combined}  ({len(pdf_pages)} pages, vector)")
    return reports
