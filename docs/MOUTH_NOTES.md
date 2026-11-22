# Mouth Notes

OralCheck's reel series, from 14 December 2026. Ian chose (21 Nov) to keep all
four sample formats, add eight more, call it Mouth Notes, lean into anatomy and
"how it works", draw cell-scale scenes in 2D, and post twice a week (Monday and
Thursday at 10am Central), in place of one carousel or image a week.

**Accuracy (Ian, 21 Nov: "make sure it's anatomically and biologically accurate").**
Every anatomical and biological detail is checked against a source before it is drawn:
HPV is drawn as a smooth icosahedral shell with no spikes; the powers-of-ten zoom lands
on a basal cell, where dysplasia begins; severe dysplasia stops in the top third (full
thickness is carcinoma in situ); the lingual nerve runs close under the floor of the
mouth, so no episode says the nerves sit deep. Cell-scale episodes say on screen that
they are illustrations not reviewed by a clinician, until one is.

Every episode: the hook line whole on frame 0 over a moving picture; no faces, no
hands; calm with a little wit; every fact from `oralcheck-agent/topics.py`,
`src/lib/seerStats.ts`, the screener's own cited figures, or a source listed here,
and shown on screen. Formats and their scenes are listed in
`oralcheck-agent/anim/STYLE.md`.

## Schedule

| # | Date | Format | Episode | Replaces | Status |
|---|---|---|---|---|---|
| 1 | Mon 14 Dec | How it works · 01 | Why most HPV never becomes cancer | 14 Dec image (same topic) | built |
| 2 | Thu 17 Dec | Ranked · 01 | Five habits by how much they multiply risk | 17 Dec tobacco + alcohol reel | built |
| 3 | Mon 21 Dec | How it works · 02 | Powers of ten: smile to DNA | 21 Dec HPV throat reel (topic moves to #12) | to build |
| 4 | Thu 24 Dec | Guess · 01 | Three spots, one reason to book now | 24 Dec red patch carousel (same topic) | built |
| 5 | Mon 28 Dec | How it works · 03 | Life of a mouth cell | 28 Dec "60,480" image | to build |
| 6 | Thu 31 Dec | Read it · 01 | Before you google that spot | (nothing; open day) | built |
| 7 | Mon 4 Jan | How it works · 04 | Under the microscope | | to build |
| 8 | Thu 7 Jan | How it works · 05 | How tobacco damages DNA | | to build |
| 9 | Mon 11 Jan | Sized · 01 | How small is HPV? | | to build |
| 10 | Thu 14 Jan | Cutaway · 01 | What is under your tongue | | to build |
| 11 | Mon 18 Jan | This or that · 01 | Five rounds: worry or wait? | | to build |
| 12 | Thu 21 Jan | Myth · 01 | "If I can't see it, it isn't there" | | to build |

Replaced posts are marked cut in the calendar with a note, not deleted.

## Scripts and sources (new episodes)

The exact spoken lines live in `oralcheck-agent/anim.py` (`SCRIPTS`, one entry per scene); the summaries below are the plan they were written from, with the accuracy corrections of 21 Nov applied.

**3. Powers of ten.** "Let's zoom from your smile to a single strand of DNA." /
"Ten times closer: the side of the tongue, the most common place it starts." /
"A hundred times: the surface is a lining, many cells deep." / "A thousand
times: one cell from the lining. Almost all oral cancers start in this lining." / "Ten thousand times: the nucleus, where the cell keeps its DNA." /
"Cancer starts when changes to that DNA let a cell stop following the rules."
Sources: ACS, What Are Oral Cavity and Oropharyngeal Cancers?; NCI, What Is
Cancer?; topics `tongue_sides`. Magnifications are labels, not measurements.

**5. Life of a mouth cell.** "Your cheek lining replaces itself about every two
weeks." / "New cells are made at the bottom layer." / "They rise, flatten out,
and are shed at the surface." / "When a cell's DNA is damaged, it can keep
dividing instead of moving on." / "Enough of them can build into a growth you can
see or feel." Sources: StatPearls, Histology, Oral Mucosa (NCBI Bookshelf
NBK572115: buccal mucosa turnover about 14 days; 14 to 21 days for oral
epithelium); NCI, What Is Cancer?

**7. Under the microscope.** "What does a biopsy actually look for? Layers." /
"Normal lining: new cells at the bottom, flat ones on top, in order." / "Mild
dysplasia: abnormal cells, only in the lowest layers." / "Moderate, then severe:
they climb higher." / "Cancer: they break through the floor, into the tissue
beneath." / "Dysplasia is not cancer, but it can become cancer. That is why it
is worth finding." Sources: NCI Dictionary, oral epithelial dysplasia; NCI
Dictionary, invasive cancer; grading by thirds of the epithelium, as in the
standard (WHO) scheme. Illustration, not a real slide.

**8. How tobacco damages DNA.** "Tobacco carries dozens of cancer-causing
chemicals." / "In the cells lining your mouth, some of them stick to DNA." /
"The cell's repair systems fix most of that damage." / "Not all of it. A mistake
that slips through can switch off a gene that stops tumours." / "Quit, and the
risk drops measurably within a few years." Sources: Hecht, Nature Reviews Cancer
2003 (tobacco carcinogens, DNA adducts, repair, p53); topics `quitting`.

**9. Sized: how small is HPV?** "How small is HPV? Let's shrink." / "A grain of
rice." / "One cell from your cheek: about a twentieth of a millimetre." / "HPV:
about 55 nanometres. Nearly a thousand would fit across that one cell." / "Too
small to see, and most of the time the body clears it anyway." Sources: IARC
Monograph 90 (HPV particles about 55 nm); cytomorphometry of normal buccal cells
(mean diameter about 49.5 µm, Asian Journal of Medical Sciences 2023); topics
`hpv_is_common`.

**10. Cutaway: under your tongue.** "What is under your tongue? Let's peel it
back." / "First, the lining: thin, smooth, and where oral cancer starts." /
"Under it, a salivary gland, and the nerve that gives your tongue feeling." /
"Then the muscles that form the floor of your mouth." / "Pain usually starts
only when a growth reaches a nerve or breaks open, so early changes often do
not hurt." / "Lift your tongue and look at the floor of your mouth once a
month." Sources: ACS (lining, squamous cells); topics `floor_of_mouth`,
`painless`, `monthly_self_exam`. Schematic layers, not to scale.

**11. This or that: worry or wait?** "Five rounds. Worry or wait? Answer before
the reveal." / "A sore that hurts, and is shrinking after a week? Wait." /
"White coating that wipes off? Usually thrush, not cancer." / "A painless red
patch, three weeks old? Get it checked." / "A lump in your neck for a month, no
cold? Get it checked." / "A white patch that will not rub off? Get it checked."
Sources: topics `canker_vs_cancer`, `wipe_test`, `red_patch`, `neck_lump`,
`white_patch`.

**12. Myth: if I can't see it, it isn't there.** "Myth: if the mirror shows
nothing, there is nothing there." / "Some oral cancers start where a mirror
cannot reach: the base of the tongue and the tonsils." / "There is often nothing
to see at all." / "The signs are different: a sore throat that lasts, a lump in
the neck, ear pain on one side." / "Any of those for more than two weeks gets
checked." Sources: topics `throat_hpv_site`, `hpv_throat_symptoms`.

## Season 2: two lanes (planned 22 Nov 2026)

Ian (22 Nov): "Zack D Films type, 3Blue1Brown type", more posts, more views; four
Instagram posts a week with the calendar running further ahead; ask him for any real
photo a post needs (not video).

- **3D lane (Blender, `oralcheck-agent/blender/`)**: stylized, toy-like 3D with real
  lighting and camera moves, for "what happens if", "why does your body", "how it's
  done" and "you vs. the thing". Not the realistic head model Ian found uncanny.
- **Math lane (Manim, `oralcheck-agent/manim/`)**: 3Blue1Brown-style graphs and
  shapes that transform, for numbers and mechanisms.

What Instagram itself says it ranks Reels on: watch time, likes per reach and sends
per reach (Adam Mosseri, January 2025). So: a payoff worth watching to the end, and a
fact worth sending to someone.

| Idea | Lane | Source | Real image needed |
|---|---|---|---|
| The HPV vaccine is a virus with nothing inside (L1 shells, antibodies) | 3D, prototype | NCI, HPV vaccines (virus-like particles, no viral genes); 360 L1 copies | your Gardasil vial photo (have) |
| Quit smoking: your mouth at 1, 5 to 10 and 20 years | Manim, prototype | CDC, Benefits of Quitting (risk halves in 5 to 10 years; near a non-smoker at 20) | a cigarette or pack on plain background |
| Why does your tongue look furry? (papillae) | 3D | StatPearls, tongue anatomy | a real coated-tongue photo |
| Why your tongue has a map (geographic tongue, harmless) | 3D | StatPearls, geographic tongue | a real geographic-tongue photo |
| How a biopsy is taken, from inside the mouth | 3D | topics `biopsy` | none |
| A white blood cell vs HPV | 3D | CDC (most infections clear) | none |
| What a year of vaping does in your mouth: what is known and what is not | 3D | to research (ACS, CDC) | a vape on plain background |
| How much spit you make, and why dry mouth matters | Manim | to research (NIDCR) | none |
| Why "about 15 times" is multiplication, not addition | Manim | Hashibe 2009 (needs the single-habit figures first) | none |
