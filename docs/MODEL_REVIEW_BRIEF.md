# Brief: an honest review of the OralCheck 3D head model, and whether to rebuild it

Run this on Opus 5.5 at max effort. Read all of it before starting. Rewritten on 23 October with Ian's answers to step 0; the original is `oralcheck-agent/anatomy3d/MODEL_REVIEW_PROMPT.md`.

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

## What Ian decided (23 October, answers to step 0)

These override anything later in this brief that disagrees with them. The
reference sheet he chose from (A photoreal 3D atlas, B painted NCI plate,
C Blausen rendered illustration, D Cancer Research UK line diagram, E and F the
current model) is reproduced in the review's references section.

| Question | Ian's answer |
|---|---|
| Look | Closest to a **rendered textbook illustration** (the Blausen Medical "Upper Respiratory System" style: clean, slightly stylised, with depth and soft shading). |
| Avoid | **Photoreal 3D** (Complete Anatomy / VOKA raw-muscle realism), the **current muscle view**, and the **current see-through mode**. None of the current model's looks survive. |
| Main job | A mix of **teaching the public where oral cancers start** (sides of the tongue, floor of the mouth, tonsils) and what to check, and **credibility with clinicians**. |
| Main use | **Instagram**: reels for video demos and static images for posts. The website is secondary. |
| Scope | Not decided. Prototype both **mouth and throat only** and **mouth first, head as faded context**; he will pick. |
| Face | A **faded side silhouette**, like the NCI and Blausen plates: a ghosted profile for context, no eyes looking at you, no skin texture. |
| Disease | **New requirement.** Show what disease looks like on the lining of the mouth (white patches, red patches, mixed red and white, ulcers, lumps and thickening, and any other way oral cancer and precancer show on the mucosa and lips), **illustrated in the same style, switchable**, at the real sites. |
| Lesion checking | **Sources only** for now: match each lesion illustration to published clinical photographs and cite them. No clinician has reviewed them, so say that wherever they appear, and never imply otherwise. |
| Motion | **Show both**: a short clip of a turning 3D model and a short clip of animated illustration (slow zoom and pan, layers fading in, a lesion appearing), so he can compare on his phone. |
| Budget | Prefers a **one-off payment** to a subscription. Give options with prices. The licence must allow use in Instagram posts and reels published by OralCheck. Ask before buying anything. |
| Website | Not decided. Recommend a place. |
| Timeline | Review and prototypes now. The full rebuild only after he picks a direction. |

What this changes below:

- The audit (step 2) is still done, but its job is now to explain **why** the current look fails and what can be reused (geometry, label checks, the render and reel pipelines). It does not need a full costed fix for every issue in a look Ian has already ruled out.
- Step 3 becomes a choice between routes to the textbook-illustration look, judged first on how the **stills and reels** look on a phone, then on credibility, one-off cost, licence for social use, and effort.
- Lesions are part of every option, not an add-on.
- The prototypes (deliverable 3) are fixed: see below.

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
- **23 October, after the step 0 questions:** Ian also ruled out the see-through (glass-and-teal) mode and the muscle view as looks, so "what did work" above is now about content (the mouth interior, the label checks), not style.

## What to do

### 0. Ask Ian questions first, to sharpen this brief

Done on 23 October. His answers are in "What Ian decided" above. Ask again only
if something new comes up that changes the plan.

### 1. Look at what "professional" means first

Search the web for professional head-and-neck and oral anatomy imagery, and look
at enough of it to be specific. Weight it towards what Ian chose:

- **Rendered and painted medical illustration**, the target look: Blausen Medical
  (its gallery on Wikimedia Commons is CC BY), Terese Winslow's NCI plates (NCI
  Visuals Online), Netter, Sobotta, Kenhub, TeachMeAnatomy, OpenStax Anatomy and
  Physiology, and portfolios of the Association of Medical Illustrators. Note how
  they stay professional without photorealism.
- **3D viewers**, for comparison and for the "turning model" reel option:
  Complete Anatomy, Visible Body, BioDigital Human, Zygote, Primal Pictures,
  VOKA, and anatomy models on Sketchfab. Note which of them look illustrated
  rather than photoreal, and how.
- **How oral lesions are shown to the public**: patient-education pages from
  cancer centres and charities (Mayo Clinic, MD Anderson, NCI, NHS, Cancer
  Research UK, the Oral Cancer Foundation, the American Dental Association), and
  clinical photo references for leukoplakia, erythroplakia, mixed
  red-and-white lesions, ulcers, lumps and induration, lichen planus-like
  lesions, and lip changes. Note which sites illustrate rather than photograph,
  and how they handle how graphic real photos are.
- **Medical content on Instagram**: a handful of accounts that post anatomy or
  oral health content that looks professional, for format, pacing and framing
  of reels and carousels at 4:5 and 9:16.

Write down what concretely makes the good ones look professional and not
uncanny: lighting and shading, palette, outlines, how much detail, background,
depth cues, how faces are handled, labels and leader lines, typography, and how
much they show at once. Save the references you lean on (links, plus
screenshots where the licence allows) in a references section, including the
A to F sheet Ian chose from.

### 2. Audit the current model

Render it from many angles and in every mode and preset (see `render.py` and the
`oc` API; `artifact.html` has the preset list) and compare with the references.
List the issues, each with what and where (with a render), severity (breaks
trust / looks amateur / minor) and root cause (atlas data, export script,
shaders, lighting, the page). Group them under the uncanny feeling and exactly
what produces it, geometry, materials, lighting and depth, colour, the eyes,
the mouth, cut views, x-ray mode, labels, page and controls, mobile, load size
(about 10 MB) and performance, accessibility, and licensing.

Ian has ruled the current looks out, so keep fix costs brief. Spend the effort
on two questions instead: **what in it is worth keeping** (accurate geometry for
the mouth and throat, label checks, the render and reel pipelines), and
**whether the Z-Anatomy geometry can carry the textbook look** if it is
re-shaded, or whether it is too crude underneath.

### 3. Choose the route to the textbook-illustration look

Evaluate each route with costs, licence terms for Instagram use, and what its
stills and reels would look like on a phone:

- **Re-shade the existing 3D** (Z-Anatomy) in an illustrated style: soft
  shading, gentle outlines, a faded silhouette, a limited palette.
- **A licensed 3D model, one-off purchase** (Sketchfab store, TurboSquid,
  CGTrader, Zygote, and similar), restyled the same way. Check what each
  licence allows for social video.
- **Licensed 2D illustrations, one-off** (stock medical illustration, Blausen
  and Science Photo Library type libraries), animated for reels.
- **Original 2D or 2.5D illustration made for OralCheck**: layered vector or
  painted plates (a faded side profile cut-away, and a front view of the open
  mouth), animated by moving and fading layers. Free to own outright.
- **Free and open sources** (Blausen CC BY, Cancer Research UK CC BY-SA, NIH 3D,
  BodyParts3D, newer Z-Anatomy releases). Check what attribution and
  share-alike would mean on Instagram.
- **Subscriptions and embeds** (BioDigital, Visible Body, Complete Anatomy).
  Ian prefers one-off, so list these mainly so the choice is visible.

For every route, say how lesions would be drawn and switched on and off.

Give a recommendation and say why the others lost. If the honest answer is that
3D is the wrong tool for this, say that; the side-by-side motion clips (below)
are there so Ian can judge it himself.

### 4. Lesion illustrations

Plan and prototype a small set of lesion illustrations in the chosen style:
at least a white patch (leukoplakia) and a red patch (erythroplakia) on the side
of the tongue, an ulcer, and a lump or thickening on the floor of the mouth,
plus any others the sources show are common. For each:

- the site it is drawn at, and why (cite where these lesions usually appear)
- the published clinical photographs it was matched to, with links
- a plain caption saying what to look for and that any sore, patch or lump that
  does not heal in about two weeks should be seen by a dentist or doctor
  (check the wording against the cancer-centre sources and the site's existing
  copy, and do not invent figures)
- a note that it is an illustration for education, matched to published
  sources, and **not reviewed by a clinician**

### 5. Directions for use

Write clear directions for:
- **the social pipeline first**: how to make a still and a reel from the new
  look, which views and lesion toggles are safe to post, caption framing
  (educational, not diagnostic), attribution lines where a licence needs them
- **Ian**: how to re-render stills, re-record a clip, change a view, and what
  never to do
- **visitors**, briefly, if an interactive piece goes on the site

### 6. Where it could live on oralcheck.org

Ian has not decided. Recommend a place (for example a Learn page, the results
page, or both) and keep the plan short: how it loads (lazy, never blocking the
screener), mobile, a fallback for weak devices, accessibility (keyboard,
reduced motion, text alternative), translations (`messages/*.json`), SEO, and
the medical framing. **This repo's Next.js has breaking changes: read the
relevant guide in `node_modules/next/dist/docs/` before writing any site code**
(see `AGENTS.md`). No site code is written in this round.

## Deliverables

1. `docs/MODEL_REVIEW.md`: the full review (references, the audit, the routes
   and the recommendation, lesion plan, directions for use, the website
   recommendation).
2. The same review published as a private artifact Ian can read, with the
   renders and references inline.
3. **Prototypes**, published as a **separate** private artifact, in the
   textbook-illustration style with a faded side silhouette:
   - **Scope A, mouth and throat only**, and **scope B, mouth first with the
     head as faded context**, side by side, so Ian can pick. Each shows at
     least one lesion switched on and off.
   - **Two short clips** (about 8 to 12 seconds, 1080x1920 for reels): one of a
     turning 3D model, one of animated illustration (slow zoom and pan, layers
     fading in, a lesion appearing). Same subject, so the comparison is fair.
   - One example **4:5 static post** in the chosen look.
   Do not overwrite the existing model artifact or touch the reel pipeline
   (`reel3d.py`, the content calendar) without Ian saying so.
4. Nothing is bought, and no large download is made, without asking Ian first.

## House rules (from the repo's `AGENTS.md`; follow them exactly)

- **No em dashes** in anything written for Ian or published under his name. Use commas, colons, or periods.
- Never fabricate a quote, endorsement, credential, or affiliation.
- Epidemiology figures come only from `src/lib/seerStats.ts`. Survival by stage is SEER *summary* stage (localized, regional, distant), not AJCC Stage I to IV.
- OralCheck is not a UW-Madison project.
- Never commit `.env*` or keys. Commit or push only when Ian asks.
- Ask before downloading large files or paying for anything.
- Keep `docs/ROADMAP.md`, `docs/OWNERS_GUIDE.md`, and the tracker artifact (https://claude.ai/code/artifact/cc490e4b-1ee3-4062-bc56-eada066f1003, republish with `url` set to that link) current in the same turn as any change of state.
- Ian is not a developer: write the review in plain language, with pictures.
