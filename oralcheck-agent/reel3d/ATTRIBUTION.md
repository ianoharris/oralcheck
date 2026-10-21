# Third-party assets in this folder

## oral.glb — anatomy
Trimmed from the Z-Anatomy Blender atlas by `export_oral.py` (teeth, jaw,
gums, tongue, soft palate, uvula, tonsils, floor-of-mouth muscles, salivary
glands, submandibular lymph nodes, lip muscle). Geometry unmodified apart from smoothing
on the soft tissue.

- "Z-Anatomy - The libre 3D atlas of anatomy" — CC BY-SA 4.0 —
  https://github.com/Z-Anatomy/Models-of-human-anatomy
- "BodyParts3D - The Database Center for Life Science" — CC BY-SA 2.1 Japan —
  https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html

Share-alike: `oral.glb` and every reel rendered from it are adaptations, so
they are shared under CC BY-SA 4.0, and each reel carries the credit line in
`reel3d.CREDIT` on screen and in its caption.

To regenerate: download Z-Anatomy.zip from the repo above, unzip, then
`blender -b --disable-autoexec --factory-startup Z-Anatomy/Startup.blend --python export_oral.py -- oral.glb`

## three.min.js — renderer
three.js r180 plus the GLTFLoader, RoomEnvironment and post-processing
addons, bundled into one file with esbuild. MIT licence, Copyright (c)
2010-2025 three.js authors. https://github.com/mrdoob/three.js

## SourceSans3.ttf, JetBrainsMono.ttf — fonts
Source Sans 3 (Adobe) and JetBrains Mono (JetBrains), both under the SIL Open
Font License 1.1, from https://github.com/google/fonts. Bundled so rendering
never waits on a network request.
