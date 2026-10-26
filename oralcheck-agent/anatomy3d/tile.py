"""Make a photo into a seamless tile with an even light, plus a relief map.
python tile.py in.webp out_name [crop x0 y0 x1 y1]"""
import sys, numpy as np
from PIL import Image, ImageFilter
src, name = sys.argv[1], sys.argv[2]
im = Image.open(src).convert("RGB")
if len(sys.argv) > 3: im = im.crop(tuple(int(v) for v in sys.argv[3:7]))
im = im.resize((1024, 1024), Image.LANCZOS)
a = np.asarray(im).astype(np.float32) / 255
# even out the light: divide by a heavy blur (vignette, gradients), keep the overall colour
lo = np.asarray(im.filter(ImageFilter.GaussianBlur(160))).astype(np.float32) / 255
a = np.clip(a / np.maximum(lo, 0.05) * a.reshape(-1, 3).mean(0), 0, 1)
# seamless, one axis at a time: blend with a copy rolled by half along that axis, the original
# winning in the middle and the rolled copy (continuous across the wrap) at the edges
n = a.shape[0]; t = 1 - np.abs(np.linspace(-1, 1, n)); w = t * t * (3 - 2 * t)
out = a * w[None, :, None] + np.roll(a, n // 2, 1) * (1 - w[None, :, None])
out = out * w[:, None, None] + np.roll(out, n // 2, 0) * (1 - w[:, None, None])
Image.fromarray((out * 255).astype(np.uint8)).save(f"textures/{name}.jpg", quality=90)
# relief: luminance minus its blur, stretched to 0..1 around 0.5
g = Image.fromarray((out * 255).astype(np.uint8)).convert("L")
L = np.asarray(g).astype(np.float32); B = np.asarray(g.filter(ImageFilter.GaussianBlur(24))).astype(np.float32)
h = (L - B); h = 0.5 + h / (4 * h.std() + 1e-6)
Image.fromarray((np.clip(h, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1)).save(f"textures/{name}_h.jpg", quality=90)
print(name, "done", out.reshape(-1, 3).mean(0).round(3))
