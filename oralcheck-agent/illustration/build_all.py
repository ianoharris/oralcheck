"""Rebuild every prototype output from the atlas model, in order.

python build_all.py out_dir [--no-video]
Needs: the anatomy3d head.glb (see render_plate.py), Playwright with Chromium, ffmpeg.
"""
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).parent; PY = sys.executable
out = Path(sys.argv[1]).resolve(); work = out / "work"; (work / "side").mkdir(parents=True, exist_ok=True); (work / "front").mkdir(exist_ok=True)
run = lambda *a: subprocess.run([PY, *map(str, a)], cwd=HERE, check=True)

run("render_plate.py", HERE / "shots/side_masks.json", work / "side")                  # side-view outlines and cross-sections
run("render_plate.py", HERE / "shots/front_ids.json", work / "front")                  # what is in front of what, open mouth
run("tracer.py", work / "side", work / "side_paths.json", "all=2.0,40,0.7", "head=6,2000,1,0", "brain=4,500,1", "skull_mid=2.5,150,0.8",
    "vertebrae=2,60,0.7", "tongue=3,200,0.7", "genio=3,200,0.7", "upper_inc=1.5,40,0.5", "lower_inc=1.5,40,0.5")
run("build_plate_b.py", work / "side_paths.json", work / "side", out / "plate_b.svg")
run("build_plate_a.py", work / "front", out / "plate_a.svg")
run("make_post.py", out / "plate_a.svg", out / "plate_b.svg", out)
LESIONS = [("a", "white", 386, 640, 340), ("a", "red", 640, 572, 340), ("a", "speckled", 214, 600, 340), ("a", "ulcer", 608, 694, 340),
           ("a", "lump", 340, 482, 340), ("a", "lip", 640, 934, 340), ("a", "lichen", 500, 500, 1000),
           ("b", "floor", 756, 683, 160), ("b", "base", 590, 705, 160)]                     # plate, name, centre, crop width
for p, n, x, y, w in LESIONS:
    run("preview.py", out / f"plate_{p}.svg", work / f"les_{n}.html", f"{x - w // 2} {y - w // 2} {w} {w}", f"lesion-{n}")
    run("shoot.py", work / f"les_{n}.html", out / f"lesion_{n}.png", "600x600")
run("preview.py", out / "plate_a.svg", work / "a.html", "-60 0 1120 1000", "labels"); run("shoot.py", work / "a.html", out / "plate_a_labelled.png", "1120x1000")
run("preview.py", out / "plate_b.svg", work / "b.html", "120 0 820 1025", "airway", "mouth"); run("shoot.py", work / "b.html", out / "plate_b_full_head.png", "820x1025")
if "--no-video" not in sys.argv:
    run("make_reel.py", "2d", out / "plate_a.svg", out / "plate_b.svg", out / "reel_2d_illustration.mp4")
    run("reel3d_frames.py", work / "frames3d"); run("make_reel.py", "3d", work / "frames3d", out / "reel_3d_turning.mp4")
print("done:", out)
