# Brief: an honest review of the OralCheck 3D head model, and whether to rebuild it

Run this on Opus 5.5 at max effort. Read all of it before starting.

## Who this is for

Ian Harris runs OralCheck (oralcheck.org), a free, private oral cancer risk
screener. He is a UW-Madison undergraduate, but OralCheck is **not** a UW-Madison
project: the university's name and marks must not appear on anything, and you
should correct that assumption wherever it appears. The site is a Next.js app
(Vercel). There is also a Python social-post generator in `oralcheck-agent/`.

Over the last week a 3D head-and-neck model was built for him: an interactive
viewer published as a private artifact, plus stills and reels for Instagram. His
verdict on it, in his words:

> "it just feels very off", "it lacks depth, realism, and is uncanny / doesn't look
> professional", "the skin layer is honestly too terrifying"

He also thinks it "could be cool as an interactive piece on my website", and
suspects "there might be a better solution" than the current approach. He is not
sure. Your job is to find out, and to say so plainly.

## What exists

All paths are relative to `/Users/ianharris/projects/OralCheck/oralcheck-agent/anatomy3d/`.
**That folder is not committed yet**, so a fresh git worktree will not contain it:
read and run everything from that absolute path in Ian's main checkout, and put
any prototypes in your own scratch or a new folder rather than editing the
originals until Ian agrees.

| File | What it is |
|---|---|
| `export_head.py` | Blender (5.2) script. Builds the model from the open-source **Z-Anatomy** atlas (CC BY-SA 4.0, built on BodyParts3D): picks head-and-neck structures, rebuilds and parts the skin, generates the parts the atlas lacks (inner lips, cheek lining, floor of mouth, throat arches, soft palate lining), moves the tonsils, makes eyelashes and brows. Writes `head_raw.glb`. |
| `src/main.js` | The three.js viewer (bundled by `node build.mjs` into `anatomy.bundle.js`). Custom MeshPhysicalMaterial shaders via `onBeforeCompile`: triplanar photo textures, procedural noise, antialiasing of fine detail, wet clearcoat, an iris shader, a jaw rig, cut planes, x-ray mode, a label system that checks what is under each pointer. Debug API on `window.oc` (`view`, `mode`, `depth`, `mouth`, `label`, `check`, `pick`, `lips`, `dump`, ...). |
| `artifact.html` | The page around the viewer: Look (See-through, Layers, Mouth, Skin block), Cut (sagittal, coronal, axial), presets ("Show me"), search. Published at **https://claude.ai/artifact/ECiso41AwjuW8UstJXWYdV** (private to Ian). The model ships as base64 in `head.part1.txt` and `head.part2.txt` because artifacts do not serve `.glb`. |
| `render.py` | Renders shot lists in headless Chromium on the Mac GPU: `../.venv-stats/bin/python3.11 render.py shots.json outdir --size 900x1000`. A shot is `{"name": ..., "js": ["oc.view(30,4,1.9)", ...]}`; the last expression's value is printed (use `JSON.stringify(oc.check())` to verify labels). |
| `demo_video.py` | Records a captioned 70 s walkthrough: `../.venv-stats/bin/python3.11 demo_video.py out.mp4 --size 1920x1080`. |
| `tile.py`, `textures/` | Seamless photo textures and relief maps (some made with Gemini/ChatGPT from clinical photos Ian sent). |
| `ATTRIBUTION.md` | Licences and what was generated rather than taken from the atlas. |
| `stills/` | Renders, including before/after sheets and the demo video. |

The Z-Anatomy source (`Startup.blend`) sits in another session's scratchpad at
`/private/tmp/claude-501/-Users-ianharris-projects-OralCheck/634f3aef-ed1c-43ea-a1d2-663a14401869/scratchpad/zanat_dl/Z-Anatomy/`.
If you cannot read it, download Z-Anatomy again (ask Ian first: it is a large
download). A full export takes about 12 minutes:

```
blender -b --disable-autoexec --factory-startup <Startup.blend> --python export_head.py -- head_raw.glb
npx gltf-transform weld head_raw.glb w.glb && npx gltf-transform meshopt w.glb head.glb
```

Then rebuild the base64 parts (`base64` of `head.glb`, split in two halves) before publishing.

## History you should know (so you do not repeat it)

- **Skin.** The atlas skin is a hollow shell about 3 mm thick, made of pieces that do not quite meet, and it is low detail, so the face looks like a mannequin. Rebuilding it took many rounds (voxel remesh, fusing the two layers, stepping back onto the atlas surface, special cases for ears, eyes and nostrils). Pits, pleats, slits, torn ears and holes each appeared and were fixed. **On 23 October Ian asked for the skin to be removed entirely** ("too terrifying"). It is now left out of the file (`SKIN_IN_MODEL = False` in `export_head.py`); the code is kept. The Skin button, the "show the face" switch and the Lips preset are gone; the peel slider now starts at muscle.
- **Lips.** Ian placed the lip line himself with a slider page (the atlas mouth slit was 14.5 mm too low). With no skin there are no visible lips; only the generated inner-lip linings remain.
- **Earlier verdicts from Ian:** flesh-coloured skin, raw red muscle and a dark background looked "terrifying"; plaster skin "looked bad"; "the textures still look weird"; muscle and vessels looked "like painted concrete"; a mouth on a bare skull looked uncanny; "so many sharp lines and messed up geometries".
- **What did work:** the mouth interior (teeth, gums, tongue, the "say ahh" view of uvula, tonsils and throat) after colours were matched to clinical photos; the see-through mode that lights one structure in teal; the label checking.
- **Reels** use a different pipeline (`oralcheck-agent/reel3d.py`, `reel3d/scene.html`) built on the same atlas, ivory bone and glossy teeth on pale grey. They are less criticised. Keep them in mind; do not break them.

## What to do

### 0. Ask Ian questions first, to sharpen this brief

Before any research or code, ask Ian a short round of questions (use the
question tool, a few at a time, with concrete options and a recommended one
first). Then rewrite this brief with his answers folded in, show him the changed
parts, and only start once he is happy with it. Ask what you actually need, for
example:

- **What should it feel like?** Show 3 or 4 contrasting reference images you found (photoreal like Complete Anatomy, clean illustration like Netter, stylised glass-and-teal, flat diagram) and ask which is closest to what he has in mind, and which he dislikes.
- **What is it for?** Teaching the public where oral cancer starts, credibility with clinicians, social content, or the website centrepiece. Which matters most?
- **Scope:** the whole head and neck, or only the mouth and throat?
- **Face:** no face at all, a neutral clean bust, or something else? (He found both the skin and a mouth on a bare skull unsettling.)
- **Budget:** would he pay for a licensed model or embed (BioDigital, Zygote and the like), and roughly how much a month or once?
- **Time:** a quick restyle this week, or a proper rebuild?
- **Website:** where it would live, and whether it must work well on phones.
- **Who else sees it:** clinicians he is talking to, his followers, or both?

Keep it to what changes the plan; skip anything the repo already answers.

### 1. Look at what "professional" means first

Search the web for professional cranial and head-and-neck anatomy imagery and
interactive viewers, and look at enough of it to be specific. For example:
Complete Anatomy (3D4Medical / Elsevier), Visible Body, BioDigital Human (which has
an embeddable viewer and an API), Zygote Body, Primal Pictures, Kenhub,
TeachMeAnatomy, Netter's illustrations, Sobotta, medical illustration portfolios
(AMI, the Association of Medical Illustrators), and the anatomy models on Sketchfab.
Also look at clinical oral-exam photography and patient-education pages from
cancer centres (Mayo, MD Anderson, NCI, NHS, the Oral Cancer Foundation), since that
is who OralCheck is speaking to.

Write down what concretely makes those look professional and not uncanny:
lighting (key, fill, rim; soft shadows; ambient occlusion), materials (subsurface
scattering, how muscle fibre direction and fascia are drawn, how bone is
coloured), palette, background, depth cues, level of stylisation (illustration vs
photoreal), how they avoid the uncanny valley (many show no face at all, or a
clean neutral bust), labelling and leader lines, typography, and how much they
show at once. Save the references you lean on (links, plus screenshots where
the licence allows) in a references section.

### 2. Audit the current model, exhaustively

Render it from many angles and in every mode and preset (see `render.py` and the
`oc` API; `artifact.html` has the preset list). Compare side by side with the
references. List **every** issue you can find, each with:

- what it is and where (with a render as evidence)
- severity (breaks trust / looks amateur / minor)
- the root cause (atlas data, the export script, the shaders, lighting, the page)
- the fix, and roughly what it costs

Cover at least: anatomical accuracy and plausibility; geometry (faceting,
interpenetration, gaps, crude atlas parts); materials and textures; lighting and
depth; colour and contrast; the uncanny feeling, and exactly what produces it;
the eyes; scale and proportions; the mouth; the cut views; the x-ray mode;
labels; the page design and controls; mobile; load size (about 10 MB of model) and
performance; accessibility; licensing and attribution.

### 3. Decide whether to fix it or replace it

Ian suspects a better solution exists. Evaluate seriously, with costs, licences,
and what each would look like on oralcheck.org:

- keep the Z-Anatomy pipeline and fix it (what would it take to look professional?)
- a professional licensed model or embed (BioDigital Human embed/API, Zygote, Visible Body, Complete Anatomy; pricing and licence terms)
- better open or CC models (Sketchfab CC BY, NIH 3D, BodyParts3D/Anatomography, Open Anatomy Project, newer Z-Anatomy releases)
- a deliberately **stylised** look (clean medical illustration, flat-shaded or toon, glass-and-teal) instead of chasing realism, which may be the most honest way out of the uncanny valley
- 2D or 2.5D illustration (layered SVG or Netter-style plates with interaction) instead of 3D
- a narrower scope: only the mouth and throat, which is where the cancers OralCheck screens for start, rather than a whole head

Give a recommendation, and say why the others lost. If the honest answer is that
3D is the wrong tool for this site, say that.

### 4. Directions for use

Write clear directions for:
- **visitors** (how to use the interactive piece, in plain words, short)
- **Ian** (how to re-render stills, re-record the demo, change a preset, re-export the model; what to never do)
- **the social pipeline** (which views are safe to use in posts and reels)

### 5. A plan for putting it on oralcheck.org

If you recommend an interactive piece on the website, plan it: where it lives
(for example under Learn), how it loads (lazy, not blocking the screener), mobile
behaviour and a fallback for weak devices, accessibility (keyboard, reduced motion,
text alternative), translations (the site's copy lives in `messages/*.json`), SEO,
and the medical framing (educational only, not a diagnosis). **This repo's Next.js
has breaking changes: read the relevant guide in `node_modules/next/dist/docs/`
before writing any site code** (see `AGENTS.md`).

## Deliverables

1. `docs/MODEL_REVIEW.md`: the full review (references, every issue with its fix,
   the recommendation, directions for use, the website plan).
2. The same review published as a private artifact Ian can read, with the renders
   inline.
3. If there are fixes that are clearly right and cheap, make them, and show
   before/after renders. Prototype a recommended new direction if you can (for
   example a restyled render or a small proof-of-concept page), published as a
   **separate** artifact. Do not overwrite the existing model artifact without
   Ian saying so.

## House rules (from the repo's `AGENTS.md`; follow them exactly)

- **No em dashes** in anything written for Ian or published under his name. Use commas, colons, or periods.
- Never fabricate a quote, endorsement, credential, or affiliation.
- Epidemiology figures come only from `src/lib/seerStats.ts`. Survival by stage is SEER *summary* stage (localized, regional, distant), not AJCC Stage I to IV.
- OralCheck is not a UW-Madison project.
- Never commit `.env*` or keys. Commit or push only when Ian asks.
- Ask before downloading large files or paying for anything.
- Keep `docs/ROADMAP.md`, `docs/OWNERS_GUIDE.md`, and the tracker artifact (https://claude.ai/code/artifact/cc490e4b-1ee3-4062-bc56-eada066f1003, republish with `url` set to that link) current in the same turn as any change of state.
- Ian is not a developer: write the review in plain language, with pictures.
