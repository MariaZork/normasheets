"""Figures for the Navier–Stokes series. Each function returns an SVG string.

Use in a sheet:   - figure: {name: kolmogorov_spectrum, max_width: 560}
"""
import math

from normasheets.svg import (AMBER, BG, CARD, CAT, CYAN, FAINT, GREEN, INK, LINE, LINE2, MAIN, MATH, MUTED,
                            ROSE, TILE, arrow, circle, hatch, line, math_label, path, pow10, rect,
                            svg, text)

DNS, LES, RANS = CAT  # validated categorical slots


# ------------------------------------------------------------------ #2 MAC grid
def mac_grid():
    x0, y0, s, n = 28, 16, 80, 3
    g = ""
    for i in range(n + 1):
        g += line(x0 + i * s, y0, x0 + i * s, y0 + n * s, LINE2, 1.5)
        g += line(x0, y0 + i * s, x0 + n * s, y0 + i * s, LINE2, 1.5)
    g += rect(x0 + s, y0 + s, s, s, fill="#5cc8e80f", stroke=CYAN, width=1.5)
    for r in range(n):
        for c in range(n):
            g += circle(x0 + c * s + s / 2, y0 + r * s + s / 2, 5, AMBER)
    for r in range(n):                      # u on vertical faces
        for c in range(n + 1):
            x, y = x0 + c * s, y0 + r * s + s / 2
            g += arrow(x - 11, y, x + 13, y, CYAN, 2.5, head=8)
    for r in range(n + 1):                  # v on horizontal faces
        for c in range(n):
            x, y = x0 + c * s + s / 2, y0 + r * s
            g += arrow(x, y + 11, x, y - 13, ROSE, 2.5, head=8)
    cx, cy = x0 + 1.5 * s, y0 + 1.5 * s
    g += math_label(cx + 9, cy - 9, "p", "i,j", AMBER)
    g += math_label(x0 + 2 * s + 5, cy - 13, "u", "i+½,j", CYAN)
    g += math_label(cx + 8, y0 + s - 14, "v", "i,j+½", ROSE)
    W, H = x0 * 2 + n * s, y0 * 2 + n * s
    return svg(g, W, H)


# ------------------------------------------------------------------ #4 Kolmogorov spectrum + DNS/LES/RANS bands
def _pope_E(k, L=1.0, eta=1e-3, CK=1.5, eps=1.0, p0=2, cL=6.78, beta=5.2, ceta=0.4):
    fL = ((k * L) / math.sqrt((k * L) ** 2 + cL)) ** (5 / 3 + p0)
    fE = math.exp(-beta * (((k * eta) ** 4 + ceta ** 4) ** 0.25 - ceta))
    return CK * eps ** (2 / 3) * k ** (-5 / 3) * fL * fE


def kolmogorov_spectrum(kc=1.6):
    x0, x1 = -1, 3.4
    W, Hp, ml, mr, mt, bandH, bandGap = 560, 205, 50, 10, 24, 16, 6
    pw = W - ml - mr
    pts = [(x0 + (x1 - x0) * i / 400, math.log10(_pope_E(10 ** (x0 + (x1 - x0) * i / 400)))) for i in range(401)]
    ymax = max(p[1] for p in pts) + 0.4
    ymin = ymax - 7.2
    X = lambda lk: ml + (lk - x0) / (x1 - x0) * pw
    Y = lambda le: mt + (ymax - max(le, ymin)) / (ymax - ymin) * Hp
    g = ""
    for i, (a, b, lab) in enumerate([(x0, 0.75, "ENERGY"), (0.75, 2.05, "INERTIAL RANGE"), (2.05, x1, "DISSIPATION")]):
        if i == 1:
            g += rect(X(a), mt, X(b) - X(a), Hp, fill="#5cc8e80a")
        g += text((X(a) + X(b)) / 2, mt - 9, lab, MUTED, 11.5, "middle", 600, letter_spacing=".08em")
    for d in range(-1, 4):
        g += line(X(d), mt, X(d), mt + Hp, LINE, 1)
        g += text(X(d), mt + Hp + 16, pow10(d), FAINT, 11.5, "middle")
    g += line(ml, mt + Hp, ml + pw, mt + Hp, LINE2, 1) + line(ml, mt, ml, mt + Hp, LINE2, 1)
    g += text(ml - 12, mt + Hp / 2, "E(k)", MUTED, 12.5, "middle", family=MATH, italic=True,
              transform=f"rotate(-90 {ml - 12} {mt + Hp / 2})")
    g += text(ml + pw, mt + Hp + 16, "k", MUTED, 12.5, "end", family=MATH, italic=True)
    for lk, col in [(0, MUTED), (kc, LES), (3, MUTED)]:
        g += line(X(lk), mt + 8, X(lk), mt + Hp, col, 1.5, dash="4 4")
    a, b, off = 0.85, 1.95, 0.75
    ya = math.log10(_pope_E(10 ** a)) + off
    yb = ya - 5 / 3 * (b - a)
    g += line(X(a), Y(ya), X(b), Y(yb), AMBER, 2, dash="6 5")
    g += text(X(b) + 6, Y(yb) + 2, 'k<tspan font-family="KaTeX_Main" font-style="normal" font-size="12" dy="-8">−5/3</tspan>',
              AMBER, 17, family=MATH, italic=True, raw=True)
    g += path([(X(p[0]), Y(p[1])) for p in pts if p[1] >= ymin], INK, 2.5)
    g += math_label(X(0) + 5, mt + Hp - 8, "1/L", "", MUTED, 13)
    g += math_label(X(kc) + 5, mt + Hp - 8, "k", "c", LES, 13)
    g += math_label(X(3) - 5, mt + Hp - 8, "1/η", "", MUTED, 13, anchor="end")
    by = mt + Hp + 26
    defs = "".join(hatch(f"h{n}", c) for n, c in [("DNS", DNS), ("LES", LES), ("RANS", RANS)])
    for name, col, upto in [("DNS", DNS, x1), ("LES", LES, kc), ("RANS", RANS, None)]:
        g += text(ml - 8, by + bandH / 2 + 4.5, name, INK, 12.5, "end", 700)
        xr = ml if upto is None else X(upto)
        if xr > ml:
            g += rect(ml, by, xr - ml - 1, bandH, fill=col, rx=4)
        if xr < ml + pw:
            g += rect(xr + 1, by, ml + pw - xr - 1, bandH, fill=f"url(#h{name})", stroke=col, rx=4, width=1.2,
                      stroke_opacity=".7")
        by += bandH + bandGap
    g += text(ml + pw, by + 8, '<tspan font-weight="700" fill="#e8eef8">solid</tspan> = resolved · '
              '<tspan font-weight="700" fill="#e8eef8">hatched</tspan> = modeled · Pope model spectrum, L/η = 10³',
              MUTED, 11.5, "end", raw=True)
    return svg(f"<defs>{defs}</defs>{g}", W, by + 14)


# ------------------------------------------------------------------ #5 velocity profiles
def _erfc(x):
    t = 1 / (1 + 0.3275911 * x)
    y = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))))
    return y * math.exp(-x * x)


def _blasius(h=0.01, n=800, fpp0=0.332057):
    """RK4 for f''' + ½ f f'' = 0. Returns samples [(eta, f'(eta))] and eta where f' = 0.99."""
    s = [0.0, 0.0, fpp0]
    F = lambda y: [y[1], y[2], -0.5 * y[0] * y[2]]
    out, eta99, prev = [(0.0, 0.0)], None, (0.0, 0.0)
    for i in range(1, n + 1):
        k1 = F(s); k2 = F([v + h / 2 * k for v, k in zip(s, k1)])
        k3 = F([v + h / 2 * k for v, k in zip(s, k2)]); k4 = F([v + h * k for v, k in zip(s, k3)])
        s = [v + h / 6 * (a + 2 * b + 2 * c + d) for v, a, b, c, d in zip(s, k1, k2, k3, k4)]
        if eta99 is None and prev[1] < 0.99 <= s[1]:
            eta99 = prev[0] + (0.99 - prev[1]) / (s[1] - prev[1]) * h
        prev = (i * h, s[1])
        out.append(prev)
    return out, eta99


def _profile(curves, walls="both", arrows=0, top_arrow=False, W=230, H=104, ylab="y", xlab="u", ymax=1.0,
             marks=(), note=None):
    ml, mr, mt, mb = 22, 12, 10, 18
    pw, ph = W - ml - mr, H - mt - mb
    X = lambda u: ml + u * pw
    Y = lambda y: mt + ph - (y / ymax) * ph
    g = ""
    if walls in ("both", "bottom"):
        g += line(ml - 6, Y(0), ml + pw, Y(0), MUTED, 2.5)
    if walls == "both":
        g += line(ml - 6, Y(ymax), ml + pw, Y(ymax), MUTED, 2.5)
    if top_arrow:
        g += arrow(X(0.55), Y(ymax) - 5, X(0.97), Y(ymax) - 5, AMBER, 2, head=7)
        g += text(X(0.5), Y(ymax) - 1, "U", AMBER, 12, "end", family=MATH, italic=True)
    g += line(ml, Y(0), ml, Y(ymax), LINE2, 1)
    fn0 = curves[0]["fn"]
    for i in range(1, arrows):
        y = ymax * i / arrows
        u = fn0(y)
        if u * pw > 9:
            g += arrow(X(0), Y(y), X(u), Y(y), CYAN, 1.5, head=6, opacity=0.5)
    for c in curves:
        g += path([(X(c["fn"](ymax * i / 80)), Y(ymax * i / 80)) for i in range(81)], c.get("col", INK), 2.2,
                  stroke_opacity=c.get("op", 1))
    for m in marks:
        g += line(ml, Y(m["y"]), ml + pw, Y(m["y"]), AMBER, 1.3, dash="4 4")
        g += text(ml + 4, Y(m["y"]) - 5, m["label"], AMBER, 11.5)
    if note:
        g += note(X, Y)
    g += text(ml - 9, mt + ph / 2 + 4, ylab, MUTED, 12, "middle", family=MATH, italic=True)
    g += text(ml + pw, H - 3, xlab, MUTED, 12, "end", family=MATH, italic=True)
    return svg(g, W, H, max_width=W)


def couette():
    return _profile([{"fn": lambda y: y}], arrows=6, top_arrow=True)


def poiseuille():
    return _profile([{"fn": lambda y: 4 * y * (1 - y)}], arrows=7)


def stokes_plate():
    curves = [{"fn": (lambda t: lambda y: _erfc(y / (2 * math.sqrt(t))))(t), "col": CYAN, "op": op}
              for t, op in [(0.004, 1), (0.02, 0.7), (0.08, 0.45)]]
    return _profile(curves, walls="bottom", xlab="u/U",
                    note=lambda X, Y: text(X(0.42), Y(0.62), "later t → deeper", MUTED, 11.5))


def blasius():
    samples, eta99 = _blasius()
    fp = lambda eta: samples[min(len(samples) - 1, round(eta / 0.01))][1]
    return _profile([{"fn": fp}], walls="bottom", ymax=7, ylab="η", xlab="u/U = f′(η)", W=220, H=168, arrows=8,
                    marks=[{"y": eta99, "label": f"δ₉₉: η ≈ {eta99:.2f}"}])


# ------------------------------------------------------------------ #6 finite-volume cell, Sweby diagram
def fv_cell():
    W, H = 300, 190
    P = [(40, 60), (120, 22), (182, 70), (168, 152), (70, 166), (26, 118)]
    N = [(182, 70), (262, 52), (286, 132), (222, 176), (168, 152)]
    cP, cN, fm = (96, 100), (232, 118), (175, 111)
    g = path(P, CYAN, 1.6, fill="#5cc8e812", close=True) + path(N, LINE2, 1.6, fill="#ffffff06", close=True)
    g += line(182, 70, 168, 152, AMBER, 3)
    g += arrow(cP[0], cP[1], cN[0] - 2, cN[1], MUTED, 1.4, head=9, dash="5 4")
    nx, ny = 0.985, 0.17
    g += arrow(fm[0], fm[1], fm[0] + 46 * nx, fm[1] + 46 * ny - 30, AMBER, 2.4, head=10)
    g += circle(*cP, 5, CYAN) + circle(*cN, 5, MUTED)
    g += math_label(cP[0] - 20, cP[1] - 10, "P", "", CYAN) + math_label(cN[0] + 8, cN[1] + 5, "N", "", INK)
    g += math_label(fm[0] + 30, fm[1] - 26, "S", "f", AMBER) + math_label(fm[0] - 22, fm[1] + 36, "f", "", AMBER)
    g += math_label(122, 120, "d", "PN", MUTED, 15)
    g += text(cP[0] - 34, cP[1] + 40, 'cell volume V<tspan dy="4" font-size="9">P</tspan>', MUTED, 12, raw=True)
    return svg(g, W, H, max_width=280)


def sweby():
    W, H, ml, mr, mt, mb = 300, 192, 30, 10, 10, 26
    pw, ph, rM, pM = W - ml - mr, H - mt - mb, 3, 2.3
    X = lambda r: ml + r / rM * pw
    Y = lambda p: mt + ph - p / pM * ph
    minmod = lambda r: max(0, min(1, r))
    superbee = lambda r: max(0, min(2 * r, 1), min(r, 2))
    vanleer = lambda r: (r + abs(r)) / (1 + abs(r))
    rs = [rM * i / 120 for i in range(121)]
    curve = lambda f: [(X(r), Y(f(r))) for r in rs]
    g = path(curve(lambda r: min(2 * r, 2)) + [(X(rM), Y(0)), (X(0), Y(0))], "none", 0, fill="#5cc8e80d", close=True)
    g += path(curve(superbee) + list(reversed(curve(minmod))), "none", 0, fill="#5cc8e824", close=True)
    for p in (1, 2):
        g += line(ml, Y(p), ml + pw, Y(p), LINE, 1) + text(ml - 6, Y(p) + 4, p, FAINT, 11, "end")
    for r in (1, 2, 3):
        g += line(X(r), mt, X(r), mt + ph, LINE, 1) + text(X(r), mt + ph + 14, r, FAINT, 11, "middle")
    g += line(ml, mt + ph, ml + pw, mt + ph, LINE2, 1) + line(ml, mt, ml, mt + ph, LINE2, 1)
    g += text(ml + pw, H - 2, "r", MUTED, 13, "end", family=MATH, italic=True)
    g += text(ml - 18, mt + 12, "ψ", MUTED, 13, family=MATH, italic=True)
    for f, col in [(superbee, CAT[2]), (vanleer, CAT[1]), (minmod, CAT[0])]:
        g += path(curve(f), CARD, 5) + path(curve(f), col, 2.2)
    g += circle(X(1), Y(1), 4.5, INK, stroke=CARD, stroke_width=2)
    g += text(X(2.32), Y(2) - 6, "superbee", INK, 11.5, weight=700)
    g += text(X(2.3), Y(vanleer(2.3)) + 15, "van Leer", INK, 11.5, weight=700)
    g += text(X(2.3), Y(1) + 15, "minmod", INK, 11.5, weight=700)
    g += text(X(0.08), Y(2.12), "TVD region · 2nd-order band", MUTED, 11)
    return svg(g, W, H)


# ------------------------------------------------------------------ #7 dealiasing, D2Q9
def dealias_23():
    W, H, ml, mr = 360, 150, 14, 14
    pw, y = W - ml - mr, 88
    X = lambda k: ml + (k + 0.75) / 1.5 * pw
    defs = hatch("hR", ROSE, CARD, opacity=0.6)
    g = rect(X(-0.5), y - 10, X(0.5) - X(-0.5), 20, fill="#ffffff08", stroke=LINE2, rx=4, width=1)
    g += rect(X(-1 / 3), y - 10, X(1 / 3) - X(-1 / 3), 20, fill=CYAN, rx=4, fill_opacity=".85")
    g += rect(X(0.5), y - 10, X(2 / 3) - X(0.5), 20, fill="url(#hR)", stroke=ROSE, rx=4, width=1, stroke_opacity=".8")
    g += rect(X(-0.5), y - 10, X(-1 / 3) - X(-0.5), 20, fill="url(#hR)", stroke=ROSE, rx=4, width=1, stroke_opacity=".8")
    x1, x2 = X(7 / 12), X(-5 / 12)
    g += (f'<path d="M{x1:.1f} {y - 13} C {x1 - 20:.1f} {y - 78}, {x2 + 20:.1f} {y - 78}, {x2:.1f} {y - 14}" '
          f'fill="none" stroke="{ROSE}" stroke-width="1.8" stroke-dasharray="5 4"/>')
    g += f'<path d="M{x2:.1f} {y - 12} l-5 -9 l9 1z" fill="{ROSE}"/>'
    g += text((x1 + x2) / 2, y - 66, "aliases fold into (−N/2, −N/3): discarded", ROSE, 11.5, "middle")
    for k, lab in [(-0.5, "−N/2"), (-1 / 3, "−N/3"), (0, "0"), (1 / 3, "N/3"), (0.5, "N/2"), (2 / 3, "2N/3")]:
        g += line(X(k), y + 10, X(k), y + 16, MUTED, 1) + text(X(k), y + 29, lab, MUTED, 11.5, "middle")
    g += text(X(0), y + 4, "kept", BG, 11, "middle", 700)
    g += text(X(7 / 12), y + 46, "product", MUTED, 11, "middle") + text(X(-5 / 12), y + 46, "alias", MUTED, 11, "middle")
    return svg(f"<defs>{defs}</defs>{g}", W, H)


def d2q9():
    W, H, cx, cy, L = 230, 196, 115, 92, 62
    g = ""
    for i in (-1, 0, 1):
        g += line(cx - L, cy + i * L, cx + L, cy + i * L, LINE, 1) + line(cx + i * L, cy - L, cx + i * L, cy + L, LINE, 1)
    for (a, b), col in [((1, 0), CYAN), ((0, 1), CYAN), ((-1, 0), CYAN), ((0, -1), CYAN),
                        ((1, 1), ROSE), ((-1, 1), ROSE), ((-1, -1), ROSE), ((1, -1), ROSE)]:
        g += arrow(cx, cy, cx + a * (L - 4), cy - b * (L - 4), col, 2.2, head=10)
    g += circle(cx, cy, 6, AMBER)
    g += text(cx, H - 6, f'<tspan fill="{AMBER}" font-weight="700">w₀ = 4/9</tspan> · '
              f'<tspan fill="{CYAN}" font-weight="700">w₁₋₄ = 1/9</tspan> · '
              f'<tspan fill="{ROSE}" font-weight="700">w₅₋₈ = 1/36</tspan>', MUTED, 12, "middle", raw=True)
    return svg(g, W, H, max_width=230)


# ------------------------------------------------------------------ #8 CUDA
def cuda_grid():
    W, H, x0, y0, s, nx, ny, bx, by = 300, 210, 34, 18, 21, 12, 8, 6, 4
    g = ""
    for j in range(ny):
        for i in range(nx):
            alt = ((i // bx) + (j // by)) % 2
            g += rect(x0 + i * s + 1, y0 + (ny - 1 - j) * s + 1, s - 2, s - 2, fill=CAT[1] if alt else CAT[0],
                      rx=3, fill_opacity=".28" if alt else ".3")
    for bj in range(ny // by):
        for bi in range(nx // bx):
            g += rect(x0 + bi * bx * s, y0 + (ny // by - 1 - bj) * by * s, bx * s, by * s, stroke=INK, width=1.4,
                      stroke_opacity=".55")
    ti, tj = 8, 2
    g += rect(x0 + ti * s + 1, y0 + (ny - 1 - tj) * s + 1, s - 2, s - 2, fill=AMBER, rx=3)
    for a, b in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        g += rect(x0 + (ti + a) * s + 3, y0 + (ny - 1 - tj - b) * s + 3, s - 6, s - 6, stroke=AMBER, rx=2, width=1.6)
    yb = y0 + ny * s + 10
    g += arrow(x0, yb, x0 + 98, yb, CYAN, 2, head=7) + text(x0 + 104, yb + 4, "i = threadIdx.x, contiguous", MUTED, 11)
    g += arrow(x0 - 12, y0 + ny * s, x0 - 12, y0 + ny * s - 76, CYAN, 2, head=7)
    g += text(x0 - 18, y0 + ny * s - 84, "j", MUTED, 11, "middle")
    g += text(x0 + bx * s / 2, y0 - 5, "block (0,1)", MUTED, 11, "middle")
    g += text(x0 + bx * s * 1.5, y0 - 5, "block (1,1)", MUTED, 11, "middle")
    return svg(g, W, H)


def cuda_pipeline():
    W, H, bw, bh = 500, 210, 136, 46

    def box(x, y, title, sub, col):
        return (rect(x, y, bw, bh, fill=TILE, stroke=col, rx=10, width=1.6)
                + text(x + bw / 2, y + 20, title, INK, 12.5, "middle", 700)
                + text(x + bw / 2, y + 36, sub, MUTED, 11, "middle"))
    g = box(6, 14, "dt = CFL(max|u|)", "CUB reduce", GREEN)
    g += box(166, 14, "1 · predict u*, v*", "stencil kernel", CYAN)
    g += box(326, 14, "b = ρ/dt · ∇·u*", "stencil kernel", CYAN)
    g += box(326, 112, "2 · Poisson Ap = b", "Jacobi / RB-GS / MG", AMBER)
    g += box(166, 112, "3 · project u, v", "stencil kernel", CYAN)
    g += box(6, 112, "boundary conditions", "edge kernel", ROSE)
    g += arrow(142, 37, 166, 37) + arrow(302, 37, 326, 37) + arrow(394, 60, 394, 112)
    g += arrow(326, 135, 302, 135) + arrow(166, 135, 142, 135)
    g += f'<path d="M74 158 C 74 196, 30 196, 22 170 L 22 66" fill="none" stroke="{MUTED}" stroke-width="1.4" stroke-dasharray="4 4"/>'
    g += f'<path d="M22 60 l-4 8 h8z" fill="{MUTED}"/>' + text(92, 196, "next step · all arrays stay on the GPU", MUTED, 11)
    g += f'<path d="M462 124 C 488 124, 488 152, 462 152" fill="none" stroke="{AMBER}" stroke-width="1.6"/>'
    g += f'<path d="M462 152 l8 -4 v8z" fill="{AMBER}"/>'
    g += text(394, 178, "× N iterations · ~80–90% of time", AMBER, 11, "middle")
    return svg(g, W, H)


# ------------------------------------------------------------------ #9 Reynolds-number map
def reynolds_map(apps=None):
    W, H, ml, mr, x0, x1, y = 940, 160, 18, 18, -6, 11, 74
    pw = W - ml - mr
    X = lambda lg: ml + (lg - x0) / (x1 - x0) * pw
    defs = (f'<linearGradient id="lam"><stop offset="0" stop-color="{GREEN}" stop-opacity=".16"/>'
            f'<stop offset="1" stop-color="{GREEN}" stop-opacity=".16"/></linearGradient>'
            f'<linearGradient id="tr"><stop offset="0" stop-color="{GREEN}" stop-opacity=".16"/>'
            f'<stop offset="1" stop-color="{ROSE}" stop-opacity=".16"/></linearGradient>')
    g = rect(X(-6), y - 12, X(0) - X(-6), 24, fill=CYAN, rx=5, fill_opacity=".14")
    g += rect(X(0), y - 12, X(3.3) - X(0), 24, fill="url(#lam)")
    g += rect(X(3.3), y - 12, X(5.7) - X(3.3), 24, fill="url(#tr)")
    g += rect(X(5.7), y - 12, X(11) - X(5.7), 24, fill=ROSE, rx=5, fill_opacity=".16")
    for t, lg in [("creeping · Stokes", -3), ("laminar", 1.65), ("transition", 4.5), ("turbulent", 8.35)]:
        g += text(X(lg), y + 4.5, t, INK, 12, "middle", 700, letter_spacing=".04em")
    for d in range(-6, 12):
        g += line(X(d), y + 12, X(d), y + (18 if d % 2 == 0 else 15), MUTED, 1)
        if d % 2 == 0:
            g += text(X(d), y + 31, pow10(d), FAINT, 11.5, "middle")
    g += text(X(11), y + 31, "Re", MUTED, 12.5, "end", family=MAIN)
    apps = apps or [
        [-5, "bacterium", 1], [-3, "capillary blood", -1], [-1, "microfluidic chip", 1], [1.3, "insect flight", -1],
        [3.3, "aorta, peak", 1], [6.6, "car", -1, "end"], [6.9, "wind-turbine blade", 1],
        [7.5, "airliner wing", -1, "start"], [9.2, "ship hull", 1], [10.3, "atmosphere", -1]]
    for a in apps:
        lg, lab, side = a[0], a[1], a[2]
        anc = a[3] if len(a) > 3 else "middle"
        yd = y - 13 if side > 0 else y + 13
        yy = y - 40 if side > 0 else y + 52
        g += line(X(lg), yd, X(lg), yy, MUTED, 1, opacity=0.7)
        g += circle(X(lg), yd, 4.5, AMBER, stroke=CARD, stroke_width=2)
        dx = -4 if anc == "end" else 4 if anc == "start" else 0
        g += text(X(lg) + dx, yy - 6 if side > 0 else yy + 15, lab, INK, 12.5, anc)
    xt = X(math.log10(2300))
    g += line(xt, y - 26, xt, y + 12, GREEN, 1, dash="3 3") + text(xt - 6, y - 26, "pipe: 2300", GREEN, 11, "end")
    return svg(f"<defs>{defs}</defs>{g}", W, H)
