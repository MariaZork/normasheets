"""Custom figures for this series.

Every public function here can be used in a sheet as
    - figure: {name: <function name>, args: {...}, max_width: 400}
and must return an SVG string. Helpers live in normasheets.svg.
"""
import math

from normasheets.svg import AMBER, CYAN, FAINT, INK, LINE2, MUTED, circle, line, path, svg, text


def lr_curve(best=0.003):
    W, H, ml, mb = 420, 190, 36, 28
    pw, ph = W - ml - 10, H - mb - 10
    lo, hi = -5, -1                                   # log10 learning rate range
    X = lambda lg: ml + (lg - lo) / (hi - lo) * pw
    Y = lambda v: 10 + (1 - v) * ph
    lb = math.log10(best)
    loss = lambda lg: min(1.0, 0.8 - 0.55 * math.exp(-(lg - lb) ** 2 / 1.2) + 1.6 * max(0.0, lg - lb - 0.35) ** 2)
    pts = [(X(lo + i * (hi - lo) / 120), Y(loss(lo + i * (hi - lo) / 120))) for i in range(121)]
    g = line(ml, 10 + ph, ml + pw, 10 + ph, LINE2, 1) + line(ml, 10, ml, 10 + ph, LINE2, 1)
    for d in range(lo, hi + 1):
        g += text(X(d), H - 8, f"1e{d}", FAINT, 11, "middle")
    g += path(pts, INK)
    bx = X(math.log10(best))
    g += line(bx, 10, bx, 10 + ph, AMBER, 1.5, dash="4 4") + text(bx + 6, 24, f"η = {best:g}", AMBER, 12)
    g += circle(bx, Y(loss(lb)), 4.5, AMBER)
    g += text(ml - 8, 18, "loss", MUTED, 11, "end")
    return svg(g, W, H)
