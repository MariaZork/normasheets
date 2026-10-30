"""Fan of example sheets for the social preview."""
import base64
import io
from pathlib import Path

from PIL import Image

from normasheets.svg import svg

GALLERY = Path(__file__).resolve().parent.parent / "assets" / "gallery"


def _b64(name, w=300):
    im = Image.open(GALLERY / f"{name}.jpg").resize((w, int(w * 1.25)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=86)
    return base64.b64encode(buf.getvalue()).decode()


def sheet_fan(names=("04-turbulence", "01-equations", "06-finite-volume")):
    W, H, w = 640, 330, 222
    h = int(w * 1.25)
    places = [(-9, 92, 40), (0, 209, 12), (9, 326, 40)]   # angle, x, y
    order = [0, 2, 1]                                      # middle sheet on top
    g = ""
    for i in order:
        ang, x, y = places[i]
        cx, cy = x + w / 2, y + h / 2
        g += (f'<g transform="rotate({ang} {cx} {cy})">'
              f'<rect x="{x - 3}" y="{y - 3}" width="{w + 6}" height="{h + 6}" rx="12" fill="#2f4a72"/>'
              f'<image href="data:image/jpeg;base64,{_b64(names[i])}" x="{x}" y="{y}" width="{w}" height="{h}" '
              f'clip-path="inset(0 round 10px)"/></g>')
    return svg(g, W, H)
