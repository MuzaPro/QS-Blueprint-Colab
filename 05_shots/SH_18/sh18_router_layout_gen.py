"""Generate the photonic-router wafer layout textures for SH_18 (v13).

  python sh18_router_layout_gen.py            (plain Python 3 + Pillow + numpy)
  -> tex/router_L1_waveguides.png   sharp surface layer: waveguides, labels, marks
     tex/router_L2_metal.png        mid layer: heater pads, electrode traces, bond pads (pre-blurred)
     tex/router_L3_deep.png         deep layer: soft dark regions (heavily blurred)
     tex/router_active.png          the 3 lanes the photons actually use (for a faint cyan trace)
All images: white = structure, black = empty, grayscale 8-bit. They map 1:1 onto the
router's object-space footprint (see U/V mapping in sh18_v13_router_build.py).

Design (physically motivated, simplified for readability):
- 13 parallel waveguide lanes (0.10 m apart). Lanes 0 and +-4 sit under the photon
  guides of the shot (world y -6.9 / -6.5 / -7.3).
- Three switch-fabric blocks, each a brick-wall ("Clements") mesh of Mach-Zehnder
  interferometer switches: S-bend in, directional coupler, two arms with a thermo-optic
  heater on one arm, coupler, S-bend out. This is how real programmable photonic routers
  steer photons between any input and output - "the great number of possible paths".
- Between blocks: waveguide crossing / shuffle regions and labels.
- Metal layer (heaters, traces to bond pads on both long edges) is drawn on its own
  layer so it can sit visibly *below* the surface in the shader (depth blur + parallax).
"""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "tex")
os.makedirs(OUT, exist_ok=True)

# router footprint in object space (Plane.004 / photonic-router-wafer)
X0, X1 = -10.78, 27.71          # m
Y0, Y1 = -0.954, 0.954
PPM = 200                        # output pixels per metre
SS = 2                           # supersampling for drawing
W = round((X1 - X0) * PPM)
H = round((Y1 - Y0) * PPM)
S = PPM * SS


def px(x, y):
    """object metres -> supersampled pixel (y up)."""
    return ((x - X0) * S, (Y1 - y) * S)


def new():
    return Image.new("L", (W * SS, H * SS), 0)


def finish(img, blur_m=0.0, gain=1.0):
    img = img.resize((W, H), Image.LANCZOS)
    if blur_m > 0:
        img = img.filter(ImageFilter.GaussianBlur(blur_m * PPM))
    if gain != 1.0:
        a = np.asarray(img).astype(np.float32) * gain
        img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    return img


L1, L2, L3, LA = new(), new(), new(), new()
d1, d2, d3, da = (ImageDraw.Draw(i) for i in (L1, L2, L3, LA))

LANES = [k * 0.10 for k in range(-6, 7)]          # 13 lanes
ACTIVE = {0.0, 0.4, -0.4}
WG = 0.022                                         # waveguide line width (m)
XL, XR = X0 + 1.25, X1 - 1.25                      # keep clear of the rounded ends

# ---------------------------------------------------------------- MZI mesh geometry
MZI_LEN = 1.40
GAP_C = 0.03                                       # coupler gap
D1 = (0.10 - GAP_C) / 2


def smooth(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def mzi_offset(s):
    """offset toward the partner lane along one MZI, s in [0, MZI_LEN]."""
    segs = [(0.00, 0.20, 0, 1), (0.20, 0.32, 1, 1), (0.32, 0.52, 1, 0), (0.52, 0.87, 0, 0),
            (0.87, 1.07, 0, 1), (1.07, 1.19, 1, 1), (1.19, 1.39, 1, 0)]
    for a, b, f, t in segs:
        if a <= s <= b:
            return D1 * (f + (t - f) * smooth((s - a) / (b - a)))
    return 0.0


BLOCKS = [  # (x start, n columns, label)
    (-8.6, 6, "SW-A  MZI MESH 13x13"),
    (3.2, 5, "SW-B  MZI MESH 13x13"),
    (14.6, 6, "SW-C  MZI MESH 13x13"),
]
COL_PITCH = 1.62
CROSS_REGIONS = [(1.0, 2.6), (12.4, 14.0)]         # shuffle / crossing zones

events = {i: [] for i in range(len(LANES))}        # lane -> [(x0, dir)]
heaters = []                                       # (x0, y_lane)
for bx, ncol, _ in BLOCKS:
    for c in range(ncol):
        x0 = bx + c * COL_PITCH
        for i in range(c % 2, len(LANES) - 1, 2):
            events[i].append((x0, +1))
            events[i + 1].append((x0, -1))
            heaters.append((x0, LANES[i + 1]))


def lane_y(i, x):
    y = LANES[i]
    for x0, d in events[i]:
        if x0 <= x <= x0 + MZI_LEN:
            y += d * mzi_offset(x - x0)
    return y


def crossing_shift(i, x):
    """in crossing regions neighbouring lanes swap with X crossings (perfect shuffle look)."""
    for a, b in CROSS_REGIONS:
        if a <= x <= b:
            t = (x - a) / (b - a)
            # lanes swap in pairs in the first half, offset pairs in the second half
            if t < 0.5:
                k = i if i % 2 == 0 else i - 1
                partner = k + 1 if i == k else k
                if partner >= len(LANES) or partner < 0:
                    return 0.0
                return (LANES[partner] - LANES[i]) * math.sin(math.pi * t * 2) ** 2 * 0.0 + \
                       (LANES[partner] - LANES[i]) * smooth(t * 2) * (1 - smooth(t * 2 - 1))
    return 0.0


def draw_lane(draw, i, width, step=0.01):
    pts = []
    x = XL
    while x <= XR:
        pts.append(px(x, lane_y(i, x) + crossing_shift(i, x)))
        x += step
    draw.line(pts, fill=255, width=max(1, round(width * S)), joint="curve")


for i in range(len(LANES)):
    draw_lane(d1, i, WG)
    if round(LANES[i], 3) in ACTIVE:
        draw_lane(da, i, WG * 1.6)

# explicit X crossings in the crossing regions (straight diagonals read better than swaps)
for a, b in CROSS_REGIONS:
    for i in range(0, len(LANES) - 1, 2):
        m = (a + b) / 2
        d1.line([px(m - 0.25, LANES[i]), px(m + 0.25, LANES[i + 1])], fill=255, width=round(WG * S))
        d1.line([px(m - 0.25, LANES[i + 1]), px(m + 0.25, LANES[i])], fill=255, width=round(WG * S))
    # dashed frame
    for xx in np.arange(a, b, 0.08):
        d1.line([px(xx, 0.70), px(xx + 0.04, 0.70)], fill=170, width=round(0.008 * S))
        d1.line([px(xx, -0.70), px(xx + 0.04, -0.70)], fill=170, width=round(0.008 * S))

# ---------------------------------------------------------------- metal layer (L2)
for x0, yl in heaters:
    hx0, hx1 = x0 + 0.56, x0 + 0.84
    d2.rectangle([px(hx0, yl + 0.026), px(hx1, yl - 0.026)], fill=255)
    # contact squares + one trace to the nearest long edge
    for cx in (hx0 - 0.03, hx1 + 0.03):
        d2.rectangle([px(cx - 0.02, yl + 0.025), px(cx + 0.02, yl - 0.025)], fill=255)
    edge = 0.80 if yl >= 0 else -0.80
    tx = hx1 + 0.03
    d2.line([px(tx, yl), px(tx, edge)], fill=200, width=round(0.010 * S))
    d2.line([px(hx0 - 0.03, yl), px(hx0 - 0.03, edge)], fill=200, width=round(0.010 * S))

# bond pad rows along both long edges
x = XL + 0.2
while x < XR - 0.2:
    for edge in (0.835, -0.835):
        d2.rectangle([px(x, edge + 0.045), px(x + 0.07, edge - 0.045)], fill=255)
    x += 0.16
# common ground rails
for yy in (0.775, -0.775):
    d2.rectangle([px(XL + 0.1, yy + 0.008), px(XR - 0.1, yy - 0.008)], fill=230)

# ---------------------------------------------------------------- deep layer (L3)
for bx, ncol, _ in BLOCKS:
    xa, xb = bx - 0.25, bx + (ncol - 1) * COL_PITCH + MZI_LEN + 0.25
    d3.rectangle([px(xa, 0.66), px(xb, -0.66)], fill=170)          # trench under each mesh
    for c in range(ncol):                                            # denser bands per column
        x0 = bx + c * COL_PITCH + 0.5
        d3.rectangle([px(x0, 0.62), px(x0 + 0.42, -0.62)], fill=255)
for a, b in CROSS_REGIONS:
    d3.rectangle([px(a + 0.2, 0.35), px(b - 0.2, -0.35)], fill=120)
# a few big quiet blocks near the ends (I/O + monitor photodiodes)
d3.rectangle([px(XL, 0.55), px(XL + 1.0, -0.55)], fill=180)
d3.rectangle([px(XR - 1.4, 0.55), px(XR, -0.55)], fill=180)

# ---------------------------------------------------------------- surface details (L1)
font = ImageFont.load_default(size=round(0.055 * S))
small = ImageFont.load_default(size=round(0.04 * S))
for bx, ncol, label in BLOCKS:
    xa, xb = bx - 0.25, bx + (ncol - 1) * COL_PITCH + MZI_LEN + 0.25
    d1.text(px(xa + 0.05, 0.735), label, fill=230, font=font, anchor="ls")
    # block frame (thin) + corner crosses
    d1.rectangle([px(xa, 0.68), px(xb, -0.68)], outline=200, width=round(0.007 * S))
    for cx, cy in ((xa, 0.68), (xb, 0.68), (xa, -0.68), (xb, -0.68)):
        d1.line([px(cx - 0.05, cy), px(cx + 0.05, cy)], fill=255, width=round(0.01 * S))
        d1.line([px(cx, cy - 0.05), px(cx, cy + 0.05)], fill=255, width=round(0.01 * S))
    for c in range(ncol):
        d1.text(px(bx + c * COL_PITCH + 0.6, -0.735), f"C{c + 1:02d}", fill=190, font=small, anchor="ls")
for a, b in CROSS_REGIONS:
    d1.text(px(a + 0.1, 0.735), "XBAR", fill=230, font=font, anchor="ls")
# lane index ticks at the left I/O
for k, y in enumerate(LANES):
    d1.text(px(XL - 0.35, y), f"{k:02d}", fill=200, font=small, anchor="lm")
# grating-coupler fans at both ends of every lane
for y in LANES:
    for xe, sgn in ((XL, -1), (XR, 1)):
        for j in range(4):
            xx = xe + sgn * (0.03 + j * 0.025)
            d1.line([px(xx, y + 0.03), px(xx, y - 0.03)], fill=220, width=round(0.008 * S))

# ---------------------------------------------------------------- write
finish(L1).save(os.path.join(OUT, "router_L1_waveguides.png"))
finish(L2, blur_m=0.012).save(os.path.join(OUT, "router_L2_metal.png"))
finish(L3, blur_m=0.09, gain=1.0).save(os.path.join(OUT, "router_L3_deep.png"))
finish(LA, blur_m=0.006).save(os.path.join(OUT, "router_active.png"))
print("wrote", W, "x", H, "to", OUT, "| MZIs:", len(heaters))
