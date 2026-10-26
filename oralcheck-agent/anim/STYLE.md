# OralCheck animation house style

Animated reels for Instagram, 1080 x 1920, 30 fps, 25 to 40 seconds. Started
26 Oct 2026 after Ian's note that animation gets views (his 3D skull reel,
immersive if not very accurate, doubled his average reel views) and that reels
drive site traffic. Two samples set the style: `gauze.html` (2D) and
`zoom.html` (3D). `anim.py` voices, renders and mixes them.

## Ideas first

An animation is only as good as its question. Before building one:

- **Read what has already been posted** (`ideas.json`, `used_topics.json`,
  `calendar/calendar.json`). The feed has run the stadium comparison, the
  two-week sore, survival by stage, HPV vs tobacco, what the dentist checks
  and the self-exam walkthrough. A new reel needs a new angle, not a re-skin.
- **Lead with a question people already half-wonder** ("why does my dentist
  grab my tongue?"), a what-if, a zoom, a ranking or a guess. The first line
  is the hook and the subject is already moving on frame 0.
- **Every claim has a checked source** and the source is on screen. Facts come
  from `topics.py` or `src/lib/seerStats.ts`, or a primary source checked on
  the day (NIDCR, ACS, CDC, NCI). Never more specific than the source: ACS
  says "almost all" are squamous cell, so the reel says "almost all", not
  "9 in 10".

## The look

| | |
|---|---|
| Ground | warm paper `#f5f3f0`, never pure white or black |
| Subject | teal `#0d7377`; only the thing being talked about is teal |
| Accent | coral `#e8634a`, at most one beat per reel, for the thing that matters |
| Context | clay: ivory bone, white teeth, pale pink-white soft tissue, matte |
| Type | DM Serif Display for titles, labels and numbers; Source Sans 3 in sentence case for captions and everything small. No monospace, no uppercase tracking (Ian, 26 Oct: the mono chrome looked "so claude code") |
| Faces | none. No skin, no eyes: realism with a face is what read as uncanny |

**2D** uses the illustrated plates (`reel2d/plate_*.svg`). Movement in a flat
drawing comes from the camera (the SVG viewBox) and from 2.5D tricks: a copy
of a part laid behind it and shifted becomes its side wall when it turns.

**3D** uses three.js with clay materials, soft ambient occlusion, a
transparent background over the paper, and teal for the subject. Two worlds
can cross-fade (the jaw model, then a cell-scale block), which is what makes
a powers-of-ten zoom feel continuous.

## The frame (`house.css`, `house.js`)

The brand mark at the top left (no step counter, no rule, no eyebrow), the
stage band (y 230 to 1230), a **readout** in serif for the number that carries
the idea (field of view, a step), word-synced captions at y 1270, a slim
progress line, the source and licence line, and the end card with the address.
A label (a teal sentence-case line over a serif title) with a solid dot and a
thin leader line marks the subject. Scenes draw only the stage. The calendar
reels (`reel2d/scene.html`) use the same frame.

## Motion

- Ease out (quartic). No bounce, no spin for its own sake.
- Nothing holds still for more than about a second; the camera always drifts.
  (The 21 Sept reel review found scenes freezing for 5 s, a likely cause of
  the 83.7% skip rate.)
- One idea per line, one move per line. A cut gets the soft "glide" sound; the
  end card gets the low tone; labels get the tap.
- Numbers count, scales move on a log scale, labels hold one side per line.

## Honesty on screen

- Drawings of signs carry "Illustration for education, not a real case. Not
  reviewed by a clinician." (`foot` / `foot_on` in the script).
- Cell-scale scenes are illustrations: the credit says the number of cells is
  not to scale. Cells carry dark edges so each one reads as its own shape.
- A 2D turn shows its side face only on the trailing side (clip it), never as
  a second outline behind; a 3D jaw that opens must split the gum mesh at the
  bite, or the upper gum swings down and reads as a second tongue.
- The plates and the jaw model are CC BY-SA, so the licence line is always on.

## Making a new one

1. Pick the question; check the facts; write 5 or 6 lines of at most about 14
   words each in `anim.SCRIPTS`, each with a `key` and an `eyebrow`.
2. Write `anim/<name>.html`: import `house.js`, draw the stage in
   `window.render(t)` keyed to the shot start times, end with `frame(t)`.
3. Preview silently with fake timings before spending on voice, then
   `python anim.py <name> out.mp4`.
