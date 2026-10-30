"""Block renderers: each YAML block becomes an HTML fragment.

A block is a mapping with exactly one *type key* (math, text, table, ...) plus optional
shared options:  size (font scale), align (left|center|right), mt (margin-top px).
A bare list under a type key is accepted wherever a list is the main payload.
"""
from __future__ import annotations

import html

from markupsafe import Markup
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

from .inline import color_value, inline, tex_span


class SpecError(ValueError):
    pass


SHARED = {"size", "align", "mt", "class"}
RENDERERS: dict = {}


def block(name):
    def deco(fn):
        RENDERERS[name] = fn
        return fn
    return deco


def render_blocks(blocks, ctx) -> str:
    return "\n".join(render_block(b, ctx) for b in (blocks or []))


def render_block(b, ctx) -> str:
    if isinstance(b, str):
        b = {"text": b}
    if not isinstance(b, dict):
        raise SpecError(f"block must be a mapping, got {b!r}")
    keys = [k for k in b if k not in SHARED and k in RENDERERS]
    if len(keys) != 1:
        unknown = [k for k in b if k not in SHARED and k not in RENDERERS]
        hint = f" (unknown: {', '.join(unknown)})" if unknown else ""
        raise SpecError(f"block needs exactly one type key from {sorted(RENDERERS)}{hint}: {b!r}")
    kind = keys[0]
    body = RENDERERS[kind](b[kind], b, ctx)
    style = []
    if b.get("size"):
        style.append(f"font-size:{b['size']}em")
    if b.get("align"):
        style.append(f"text-align:{b['align']}")
    if b.get("mt") is not None:
        style.append(f"margin-top:{b['mt']}px")
    cls = f"blk blk-{kind} {b.get('class', '')}".strip()
    st = f' style="{";".join(style)}"' if style else ""
    return f'<div class="{cls}"{st}>{body}</div>'


def _as_list(v):
    return v if isinstance(v, list) else [v]


# ---------------------------------------------------------------- text-ish
@block("text")
def _text(v, b, ctx):
    return f'<div class="note">{inline(v)}</div>'


@block("label")
def _label(v, b, ctx):
    return f'<div class="sublabel">{inline(v)}</div>'


@block("spacer")
def _spacer(v, b, ctx):
    return f'<div style="height:{int(v)}px"></div>'


@block("html")
def _html(v, b, ctx):
    return str(v)


# ---------------------------------------------------------------- math
@block("math")
def _math(v, b, ctx):
    items = v if isinstance(v, list) else [v]
    out = []
    for it in items:
        if isinstance(it, dict):
            out.append(tex_span(it["tex"], display=True, size=it.get("size")))
        else:
            out.append(tex_span(str(it), display=True))
    return "".join(out)


@block("equation")
def _equation(v, b, ctx):
    """Main equation with a label column on the left."""
    width = v.get("label_width", 196)
    lab = f'<b>{inline(v.get("label", ""))}</b>{inline(v.get("sub", ""))}'
    return (f'<div class="eqrow" style="grid-template-columns:{width}px minmax(0,1fr)">'
            f'<div class="eqlab">{lab}</div><div class="eqbody">{tex_span(v["tex"], True, v.get("tex_size"))}</div></div>')


@block("boxes")
def _boxes(v, b, ctx):
    """Row of small labelled formula boxes."""
    cells = []
    for it in v:
        lab = inline(it.get("label", ""))
        cells.append(f'<div class="box"><div class="boxlab">{lab}</div>{tex_span(it["tex"], True)}</div>')
    return f'<div class="boxes" style="grid-template-columns:repeat({len(v)},minmax(0,1fr))">{"".join(cells)}</div>'


@block("named_math")
def _named_math(v, b, ctx):
    """Two-column list: coloured name, formula."""
    rows = []
    for it in v:
        sw = f'<span class="sw" style="background:{color_value(it["color"])}"></span>' if it.get("color") else ""
        rows.append(f'<span class="nm">{sw}{inline(it["name"])}</span>{tex_span(it["tex"], True)}')
    return f'<div class="named">{"".join(rows)}</div>'


# ---------------------------------------------------------------- lists
@block("bullets")
def _bullets(v, b, ctx):
    items = v["items"] if isinstance(v, dict) else v
    dot = color_value(v.get("color", "cyan")) if isinstance(v, dict) else "var(--cyan)"
    lis = "".join(f"<li>{inline(t)}</li>" for t in items)
    return f'<ul class="bullets" style="--dot:{dot}">{lis}</ul>'


@block("steps")
def _steps(v, b, ctx):
    items = v["items"] if isinstance(v, dict) else v
    col = color_value(v.get("color", "cyan")) if isinstance(v, dict) else "var(--cyan)"
    lis = "".join(f"<li>{inline(t)}</li>" for t in items)
    return f'<ol class="steps" style="--sc:{col}">{lis}</ol>'


@block("checklist")
def _checklist(v, b, ctx):
    items = v["items"] if isinstance(v, dict) else v
    cols = v.get("columns", 2) if isinstance(v, dict) else 2
    lis = "".join(f"<li>{inline(t)}</li>" for t in items)
    return f'<ul class="checklist" style="columns:{cols}">{lis}</ul>'


@block("chips")
def _chips(v, b, ctx):
    return '<div class="chips">' + "".join(f'<span class="chip">{inline(c)}</span>' for c in v) + "</div>"


@block("kvgrid")
def _kvgrid(v, b, ctx):
    items = v["items"] if isinstance(v, dict) else v
    cols = v.get("columns", 3) if isinstance(v, dict) else 3
    kw = v.get("key_width", 130) if isinstance(v, dict) else 130
    cells = "".join(f'<div class="kv"><b style="min-width:{kw}px">{inline(k)}</b><span>{inline(val)}</span></div>'
                    for k, val in items)
    return f'<div class="kvgrid" style="grid-template-columns:repeat({cols},minmax(0,1fr))">{cells}</div>'


@block("stats")
def _stats(v, b, ctx):
    cells = []
    for it in v:
        cells.append(f'<div class="stat"><div class="big">{inline(it["value"])}'
                     f'<small>{inline(it.get("unit", ""))}</small></div>'
                     f'<div class="note" style="margin-top:4px">{inline(it.get("caption", ""))}</div></div>')
    return f'<div class="stats">{"".join(cells)}</div>'


# ---------------------------------------------------------------- table
@block("table")
def _table(v, b, ctx):
    head = v.get("head") or []
    widths = v.get("widths") or []
    rows = v.get("rows") or []
    cls = "compact" if v.get("compact") else ""
    th = "".join(
        f'<th{f" style=\"width:{widths[i]}\"" if i < len(widths) and widths[i] else ""}>{inline(h)}</th>'
        for i, h in enumerate(head))
    trs = []
    for r in rows:
        tds = []
        for i, c in enumerate(r):
            cell = inline(c)
            if i == 0 and v.get("bold_first", True):
                cell = Markup(f"<b>{cell}</b>")
            tds.append(f"<td>{cell}</td>")
        trs.append("<tr>" + "".join(tds) + "</tr>")
    thead = f"<tr>{th}</tr>" if head else ""
    return f'<table class="{cls}">{thead}{"".join(trs)}</table>'


# ---------------------------------------------------------------- code
_FMT = HtmlFormatter(nowrap=True)
_LANG = {"cuda": "cuda", "cu": "cuda", "c++": "cpp", "openfoam": "cpp", "foam": "cpp"}


@block("code")
def _code(v, b, ctx):
    if isinstance(v, str):
        v = {"src": v}
    lang = _LANG.get(v.get("lang", "text"), v.get("lang", "text"))
    src = v["src"].rstrip("\n")
    try:
        body = highlight(src, get_lexer_by_name(lang), _FMT)
    except Exception:
        body = html.escape(src)
    fs = f' style="font-size:{v["font"]}px"' if v.get("font") else ""
    return f'<pre class="hl"{fs}>{body.rstrip()}</pre>'


# ---------------------------------------------------------------- figures & layout
@block("figure")
def _figure(v, b, ctx):
    if isinstance(v, str):
        v = {"name": v}
    name = v["name"]
    fn = ctx.figures.get(name)
    if fn is None:
        raise SpecError(f"figure '{name}' not found; define def {name}(**args) in figures.py "
                        f"(available: {', '.join(sorted(ctx.figures)) or 'none'})")
    svg = fn(**(v.get("args") or {}))
    mw = f"max-width:{v['max_width']}px;" if v.get("max_width") else ""
    cap = f'<div class="figcap">{inline(v["caption"])}</div>' if v.get("caption") else ""
    return f'<div class="figure" style="{mw}">{svg}</div>{cap}'


def grid_template(cols, n):
    if not cols:
        return f"repeat({n},minmax(0,1fr))"
    parts = []
    for c in cols:
        parts.append(f"minmax(0,{c}fr)" if isinstance(c, (int, float)) else str(c))
    return " ".join(parts)


@block("columns")
def _columns(v, b, ctx):
    items = v["items"]
    gt = grid_template(v.get("widths"), len(items))
    align = v.get("align", "start")
    gap = v.get("gap", 16)
    inner = "".join(f"<div>{render_blocks(col, ctx)}</div>" for col in items)
    return f'<div class="columns" style="grid-template-columns:{gt};gap:{gap}px;align-items:{align}">{inner}</div>'


@block("tiles")
def _tiles(v, b, ctx):
    """Numbered sub-cards side by side (e.g. the three steps of an algorithm)."""
    cells = []
    for i, t in enumerate(v, 1):
        col = color_value(t.get("color", "cyan"))
        num = f'<span class="n" style="background:{col}">{t.get("n", i)}</span>' if t.get("n", i) is not None else ""
        cells.append(f'<div class="tile"><h3>{num}{inline(t.get("title", ""))}</h3>'
                     f'{render_blocks(t.get("blocks"), ctx)}</div>')
    return f'<div class="tiles" style="grid-template-columns:repeat({len(v)},minmax(0,1fr))">{"".join(cells)}</div>'
