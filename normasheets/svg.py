"""Small helpers for writing figure functions (figures.py) that return SVG strings."""
from __future__ import annotations

import html
import math

# theme colours (dark theme)
INK, MUTED, FAINT, LINE, LINE2 = "#e8eef8", "#8fa1bd", "#62738f", "#22314b", "#2f4a72"
CYAN, AMBER, ROSE, GREEN = "#5cc8e8", "#f2b45a", "#ef7a8a", "#7ed6a5"
CARD, BG, TILE = "#121c2e", "#0c1320", "#0e1626"
# validated categorical slots for 3 series on the dark surface (colour-blind safe)
CAT = ["#2f9cc4", "#c4566b", "#c98428"]

SANS = "Inter"
MATH = "KaTeX_Math"
MAIN = "KaTeX_Main"


def svg(body: str, w: float, h: float, max_width: float | None = None) -> str:
    mw = f"max-width:{max_width}px;margin:0 auto;" if max_width else ""
    return (f'<svg viewBox="0 0 {w:g} {h:g}" xmlns="http://www.w3.org/2000/svg" '
            f'style="display:block;width:100%;height:auto;{mw}">{body}</svg>')


def text(x, y, s, fill=INK, size=12, anchor="start", weight=None, family=SANS, italic=False, raw=False, **kw):
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    wt = f' font-weight="{weight}"' if weight else ""
    it = ' font-style="italic"' if italic else ""
    content = s if raw else html.escape(str(s), quote=False)
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-size="{size}" text-anchor="{anchor}" '
            f'font-family="{family}"{wt}{it}{extra}>{content}</text>')


def math_label(x, y, main, sub="", fill=INK, size=17, anchor="start"):
    """Italic math symbol with an upright subscript, e.g. math_label(10, 20, 'u', 'i+½,j')."""
    s = html.escape(main)
    if sub:
        s += f'<tspan font-family="{MAIN}" font-style="normal" font-size="{size * 0.7:.0f}" dy="{size * 0.3:.0f}">{html.escape(sub)}</tspan>'
    return text(x, y, s, fill=fill, size=size, anchor=anchor, family=MATH, italic=True, raw=True)


def line(x1, y1, x2, y2, stroke=MUTED, width=1.5, dash=None, opacity=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' stroke-opacity="{opacity}"' if opacity is not None else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"{d}{o}/>'


def arrow(x1, y1, x2, y2, color=MUTED, width=1.6, head=8, dash=None, opacity=None):
    a = math.atan2(y2 - y1, x2 - x1)
    bx, by = x2 - head * math.cos(a), y2 - head * math.sin(a)
    px, py = -math.sin(a) * head * 0.5, math.cos(a) * head * 0.5
    o = f' fill-opacity="{opacity}"' if opacity is not None else ""
    return (line(x1, y1, bx, by, color, width, dash, opacity) +
            f'<path d="M{x2:.1f} {y2:.1f} L{bx + px:.1f} {by + py:.1f} L{bx - px:.1f} {by - py:.1f}Z" fill="{color}"{o}/>')


def path(points, stroke=INK, width=2.2, fill="none", close=False, **kw):
    d = " ".join(f"{'M' if i == 0 else 'L'}{x:.1f} {y:.1f}" for i, (x, y) in enumerate(points))
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<path d="{d}{" Z" if close else ""}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"{extra}/>'


def rect(x, y, w, h, fill="none", stroke=None, rx=0, width=1.4, **kw):
    s = f' stroke="{stroke}" stroke-width="{width}"' if stroke else ""
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"{s}{extra}/>'


def circle(cx, cy, r, fill=INK, **kw):
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in kw.items())
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{extra}/>'


def hatch(pid, color, bg=BG, size=7, opacity=0.55):
    """<pattern> for 'modelled / discarded' regions; use fill='url(#pid)'."""
    return (f'<pattern id="{pid}" width="{size}" height="{size}" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="{size}" height="{size}" fill="{bg}"/><line x1="0" y1="0" x2="0" y2="{size}" stroke="{color}" '
            f'stroke-width="2.2" stroke-opacity="{opacity}"/></pattern>')


SUP = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def pow10(d: int) -> str:
    return "10" + str(d).translate(SUP)
