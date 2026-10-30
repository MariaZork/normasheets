"""Inline markup for text fields.

Supported (applied in this order, so math and code are never touched by the rest):
  $...$            inline KaTeX math        (write \\$ for a literal dollar sign)
  `code`           inline monospace
  **bold**         bold                     (write \\* for a literal asterisk)
  x_{sub}, x^{sup} subscript / superscript
  [[ok: text]]     status tag: ok | open | bad | info
  [[swatch: #hex]] small colour square
  [[color: name | text]]  coloured text (theme colour name or #hex)
  a real newline   line break
Everything else is HTML-escaped.
"""
from __future__ import annotations

import html
import re

from markupsafe import Markup

_ESC = {"\\$": "\x00D", "\\*": "\x00S", "\\`": "\x00B", "\\[": "\x00L"}
_UNESC = {"\x00D": "$", "\x00S": "*", "\x00B": "`", "\x00L": "["}

_MATH = re.compile(r"\$(.+?)\$")
_CODE = re.compile(r"`(.+?)`")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_SUB = re.compile(r"_\{(.+?)\}")
_SUP = re.compile(r"\^\{(.+?)\}")
_MACRO = re.compile(r"\[\[(\w+):\s*(.*?)\]\]")
_GREEK = re.compile(r"[α-ωϑϕϵ]+")

THEME_COLORS = {"cyan", "amber", "rose", "green", "ink", "muted"}


def color_value(name: str) -> str:
    name = str(name).strip()
    return f"var(--{name})" if name in THEME_COLORS else name


def tex_span(tex: str, display: bool = False, size: float | None = None) -> str:
    style = f' style="font-size:{size}em"' if size else ""
    return (f'<span class="tex" data-display="{"true" if display else "false"}"{style}>'
            f"{html.escape(tex, quote=False)}</span>")


def inline(text) -> Markup:
    if text is None:
        return Markup("")
    s = str(text)
    for k, v in _ESC.items():
        s = s.replace(k, v)

    slots: list[str] = []

    def stash(fragment: str) -> str:
        slots.append(fragment)
        return f"\x01{len(slots) - 1}\x01"

    s = _MATH.sub(lambda m: stash(tex_span(m.group(1))), s)
    s = _CODE.sub(lambda m: stash(f"<code>{html.escape(m.group(1), quote=False)}</code>"), s)
    s = html.escape(s, quote=False)
    s = _BOLD.sub(r"<b>\1</b>", s)
    s = _SUB.sub(r"<sub>\1</sub>", s)
    s = _SUP.sub(r"<sup>\1</sup>", s)

    def macro(m: re.Match) -> str:
        kind, arg = m.group(1), m.group(2)
        if kind in ("ok", "open", "bad", "info"):
            return f'<span class="tag {kind}">{arg}</span>'
        if kind == "swatch":
            return f'<span class="sw" style="background:{color_value(arg)}"></span>'
        if kind == "color":
            col, _, txt = arg.partition("|")
            return f'<span style="color:{color_value(col)}">{txt.strip()}</span>'
        return m.group(0)

    s = _MACRO.sub(macro, s)
    s = _GREEK.sub(r'<span class="gk">\g<0></span>', s)  # keep η, ω… lowercase inside UPPERCASE headers
    s = s.replace("\n", "<br>")
    s = re.sub("\x01(\\d+)\x01", lambda m: slots[int(m.group(1))], s)
    for k, v in _UNESC.items():
        s = s.replace(k, v)
    return Markup(s)
