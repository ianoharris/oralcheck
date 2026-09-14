# Prompt: sensitivity analysis of the OralCheck risk score

Paste everything below the line into a fresh Claude Fable 5 session
(`claude-fable-5`). Keep this file so the analysis can be re-run whenever a
weight or a boundary changes.

---

You are helping with a methods analysis for a published oral cancer risk
assessment tool. I need a quantitative sensitivity analysis, not a code review
and not a redesign. Work carefully and show your reasoning.

## The instrument

Twelve questions. Each answer carries an integer weight. The weights are
derived from published odds ratios by:

    weight = round( ln(OR) * k )        where k = 4.47

`k` was chosen as an anchor so that daily tobacco use, taken at OR 6.0, lands
on a weight of exactly 8. Check: ln(6.0) * 4.47 = 8.009 -> 8. Every other
weight in the instrument follows from that one anchoring choice.

Current weights as deployed:

| Question | Options and weights |
|---|---|
| age | under35=0, 35to54=2, 55to64=4, 65plus=6 |
| sex | male=3, female=0, preferNotToSay=2 |
| tobacco | daily=8, occasional=5, former=2, never=0 |
| alcohol | daily=5, weekly=3, rarely=1, never=0 |
| betel | current=9, past=4, never=0 |
| hpv | vaccinated=0, neither=2, history=5, unknown=1 |
| sun | daily=2, regular=1, minimal=0 |
| symptom | yes=6, unsure=3, no=0 |
| family | yes=3, distant=1, no=0, unsure=0 |
| systemic | yes=5, unsure=1, no=0 |
| diet | daily=0, weekly=1, rarely=3 |
| dental | recent=0, fewyears=1, longago=2, never=3 |

Two rules on top of the sum:

1. **Interaction bonus.** If tobacco is `daily` or `occasional` AND alcohol is
   `daily` or `weekly`, add a flat **+3**, representing the multiplicative
   joint effect of tobacco and alcohol.
2. **Urgent symptom override.** If `symptom` is `yes`, the tier is forced to
   `high` regardless of score.

Maximum possible score is 61 (58 from options plus the 3 interaction bonus).

Tier boundaries, set by judgment rather than derived from data:

| Tier | Score |
|---|---|
| low | 0 to 4 |
| moderate | 5 to 13 |
| elevated | 14 to 22 |
| high | 23 and above |

## What I need

Every odds ratio behind those weights has a published confidence interval, and
I used point estimates. I do not know how fragile the tier assignments are as a
result. That is the question.

### Step 1: source the odds ratios

For each of the twelve factors, find the odds ratio **and its confidence
interval** from the epidemiological literature for oral cavity and/or
oropharyngeal cancer. Prefer meta-analyses and pooled consortium analyses
(INHANCE work is directly relevant) over single studies.

For each factor report: point estimate, CI, source with citation, the
population it came from, and whether it is for oral cavity, oropharynx, or
both.

**Do not invent or approximate any number.** If you cannot find a defensible CI
for a factor, say so and exclude it from the propagation rather than guessing.
A short honest list of what you could not source is more useful to me than full
coverage built on estimates.

Note where my current weight implies an OR that disagrees with what you find.
Back out the implied OR from each weight using `OR = exp(weight / 4.47)` and
compare. I already suspect the HPV weight is too low: it is 5, implying an OR
near 3, where the published association for confirmed HPV-16 with
oropharyngeal cancer specifically is far higher.

### Step 2: handle the anchor properly

This is the subtle part and I want it addressed head on.

`k = 4.47` is not independent of the data. It is *defined* by the tobacco
anchor. So if the tobacco OR is itself uncertain, the whole scale is uncertain,
and every weight moves together rather than independently.

Run the propagation **both ways** and report both:

- **(a) Fixed scale.** Hold k = 4.47. Let each OR vary within its CI
  independently. This isolates per-weight sensitivity.
- **(b) Floating scale.** Let the tobacco OR vary within its CI, recompute k so
  the anchor still yields 8, and let the other ORs vary too. This tests whether
  the instrument's calibration depends on a quantity that is itself uncertain.

Tell me which is the more honest representation of the uncertainty, and why.

### Step 3: propagate

Sample each OR from a distribution consistent with its published CI. Odds
ratios are conventionally treated as log-normal, so sample in log space. Use at
least 10,000 draws.

The profile space is fully enumerable, so enumerate it rather than sampling it.
4 x 3 x 4 x 4 x 3 x 4 x 3 x 3 x 4 x 3 x 3 x 4 is roughly 3 million
combinations, which is tractable. Profiles with `symptom = yes` are forced to
high, so handle them separately or exclude them and say which you did.

For every profile, report the probability it lands in each tier across the
draws.

### Step 4: tell me what it means

- What fraction of the profile space has a **stable** tier, meaning one tier at
  95% or more of draws?
- Which tier boundary is the least stable, and by how much?
- Give me the concrete profiles most at risk of misclassification, described in
  plain language rather than as vectors.
- **Direction of error matters more than magnitude here.** A profile that
  should be elevated but reads moderate is a worse failure than the reverse,
  because this tool exists to get people examined. Separate the two directions
  and quantify each.
- Would shifting any boundary by a point or two materially improve stability?
  Show the effect rather than asserting it.

Check these two specific profiles, both real design decisions I made and would
like tested:

1. **A 30-year-old non-smoking, non-drinking person with HPV history.** Scores
   5 today, the bottom of moderate. This is the profile the instrument is most
   likely to under-serve, since the score is dominated by tobacco and alcohol
   questions they answer "never" to.
2. **Current betel user, daily tobacco, daily alcohol.** Scores 25 today, just
   above the high boundary at 23. I deliberately did not rescale the thresholds
   when I added two questions, specifically so this profile could not drop out
   of high. I want to know whether that holds across the CIs.

## Deliverables

1. The sourced OR table with citations.
2. Runnable Python that does the propagation, so I can re-run it whenever a
   weight changes. Self-contained, standard library plus numpy only.
3. The results, with the numbers stated plainly.
4. A short methods paragraph I could adapt for a conference abstract, written
   so a reviewer can see exactly what was done.

## Constraints

- **This is not a validation.** The instrument has never been tested against
  clinical outcomes and this analysis does not change that. Do not describe it
  as validation, and flag me if I start to.
- Do not soften the result. If the tiers turn out to be fragile, that is the
  finding and I need it stated clearly.
- Say what this method cannot tell me. A sensitivity analysis over published
  CIs assumes the underlying ORs transfer to the population using the tool, and
  they are pooled across mismatched source populations. That assumption is
  itself a limitation and belongs in the write-up, not buried.
- No em dashes in anything you draft for me.
