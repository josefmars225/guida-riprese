# Displacement maps for the liquid-glass edge: R/G = 0.5 + inward normal * falloff, zero in the middle.
import sys, numpy as np
from PIL import Image
def sdf_round_rect(W, H, r):
    y, x = np.mgrid[0:H, 0:W].astype(float) + .5
    qx = np.abs(x - W / 2) - (W / 2 - r); qy = np.abs(y - H / 2) - (H / 2 - r)
    out = np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r
    return -out  # positive inside
def make(path, W, H, r, band, s=2):
    W, H, r, band = W * s, H * s, r * s, band * s
    d = sdf_round_rect(W, H, r)
    gy, gx = np.gradient(d)
    n = np.hypot(gx, gy) + 1e-9; nx, ny = gx / n, gy / n          # inward normal
    t = np.clip(1 - d / band, 0, 1); m = t ** 2.2                   # strongest at the rim
    rgb = np.stack([.5 + .5 * m * nx, .5 + .5 * m * ny, np.full_like(m, .5)], -1)
    Image.fromarray(np.round(np.clip(rgb, 0, 1) * 255).astype(np.uint8)).save(path, optimize=True)
out = sys.argv[1]
make(f"{out}/lg-card.png", 350, 290, 22, 20)
make(f"{out}/lg-clip.png", 350, 140, 22, 18)
make(f"{out}/lg-pill.png", 113, 54, 27, 22)
make(f"{out}/lg-pill-wide.png", 350, 54, 27, 22)
