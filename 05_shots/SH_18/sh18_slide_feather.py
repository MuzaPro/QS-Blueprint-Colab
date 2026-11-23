"""Feather the alpha of a rendered slide PNG towards its borders (elliptical falloff),
so objects the camera crops dissolve into the slide black instead of ending on a hard edge.
usage: python sh18_slide_feather.py in.png out.png [inner=0.62] [outer=1.0]"""
import sys
import numpy as np
from PIL import Image
src, dst = sys.argv[1], sys.argv[2]
inner = float(sys.argv[3]) if len(sys.argv) > 3 else 0.62
outer = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
im = Image.open(src)
a = np.array(im).astype(np.float32)          # handles 8/16-bit RGBA via PIL modes
h, w = a.shape[:2]
y, x = np.mgrid[0:h, 0:w]
r = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
t = np.clip((r - inner) / (outer - inner), 0, 1)
m = 1 - t * t * (3 - 2 * t)                   # smoothstep
a[..., 3] *= m
a[..., :3] *= m[..., None]                    # keep it clean on black (premultiplied-looking edge)
Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA").save(dst)
