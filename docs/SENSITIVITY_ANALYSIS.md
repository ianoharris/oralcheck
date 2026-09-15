# Sensitivity of the OralCheck tiers to odds-ratio uncertainty

Run 14 September 2026 from `docs/prompts/sensitivity-analysis.md`.
Code: `scripts/sensitivity_analysis.py` (standard library plus numpy).
Raw outputs: `docs/sensitivity-runs/`.

This is a sensitivity analysis over published confidence intervals. It is not
a validation. The instrument has never been tested against clinical outcomes
and nothing below changes that.

## 1. The short version

- **The tiers are moderately fragile, and the fragility is not mainly CI width.**
  With the scale held at k = 4.47 and every sourced odds ratio (OR) allowed to
  vary within its published 95% CI, 73.7% of the profile space keeps one tier on
  at least 95% of draws. The elevated tier is the weak one: only 56% of elevated
  profiles are stable.
- **Most of the movement comes from point estimates disagreeing with the
  literature, not from the intervals around them.** If the deployed point
  estimates are kept and only the published interval widths are applied, the
  average profile lands in its deployed tier on 94% of draws. With the published
  point estimates, that falls to 83%.
- **The anchor is the largest single disagreement.** Daily tobacco is weighted
  as OR 6.0. The two meta-analyses of current smoking and oral cavity cancer
  give 3.39 (2.64 to 4.35) and 3.43 (2.37 to 4.94). The deployed value sits
  above both upper bounds. It is inside the pharyngeal interval of Gandini 2008
  (6.76, 2.86 to 15.98), so the anchor is a pharynx number applied to a scale
  whose other weights are mostly oral cavity numbers.
- **Letting the scale float on the published tobacco OR is not a small
  perturbation.** k becomes 6.56 (5.46 to 8.25) instead of 4.47. Every
  unpinned weight inflates by about half, 32% of the profile space is
  under-called relative to what the draws support, and over-calling vanishes.
  That is the calibration problem the floating run was designed to expose, and
  it is real.
- **Direction.** Under the fixed scale the errors split almost evenly:
  8.8% of tier mass is under-called (the dangerous direction) and 7.8% is
  over-called. The under-call is concentrated in two places: past betel users
  (weight 4, published OR implies 9) and profiles sitting at 20 to 22 points on
  the elevated/high boundary. The over-call is concentrated in daily and
  occasional tobacco users without betel, because the tobacco weights are above
  the literature.
- **Boundary shifts do not fix it.** Lowering the elevated/high boundary by two
  points buys 3 to 5 percentage points of stability. No one- or two-point move
  of any boundary changes the picture, because the instability lives in the
  weights.
- **The 30-year-old with HPV history** cannot move under the primary
  propagation, because no published OR exists for the self-reported proxy and
  the weight is therefore held fixed. Scored at the published OR for confirmed
  oral HPV-16 infection (D'Souza 2007, 14.6), the median score becomes 12 and
  the profile is moderate on 77% of draws and elevated on 23%. Scored at HPV-16
  seropositivity (32.2) it is elevated on 86%. It never reaches high in any
  scenario without the symptom override.
- **The current betel, daily tobacco, daily alcohol profile** stays high on
  99.5% of draws under the primary mapping, with a 2.5th percentile score of
  24. That holds only because daily alcohol is mapped to Bagnardi's heavy band
  (OR 5.13, weight 7) and the interaction term to the INHANCE oral cavity
  parameter (3.09, weight 5), which together make up for daily tobacco falling
  from 8 to 5. If daily alcohol is instead mapped to the moderate band, the
  median score is 22 and the profile is elevated on 52% of draws. The design
  decision holds, but on a narrower margin than the deployed score of 25
  suggests, and it depends on the alcohol mapping.

## 2. Sourced odds ratios

Every OR is exactly as printed in the cited source. `w_dep` is the deployed
weight; `implied OR` is exp(w_dep / 4.47); `w_pub` is round(ln(OR) x 4.47)
at the published point estimate; `w over CI` is the same at the CI bounds.

| Factor and option | w_dep | implied OR | published OR (95% CI) | w_pub | w over CI | implied OR in CI? | site | source |
|---|---|---|---|---|---|---|---|---|
| tobacco = daily | 8 | 5.99 | 3.39 (2.64 to 4.35) | 5 | 4 to 7 | no | oral cavity | Possenti et al. 2026, Oncology Reviews; 25 studies, current vs never smokers. Corroborated by Gandini et al. 2008, Int J Cancer: oral RR 3.43 (2.37 to 4.94) |
| tobacco = occasional | 5 | 3.06 | 1.48 (1.04 to 2.09) | 2 | 0 to 3 | no | oral cavity | Berthiller et al. 2016, Int J Epidemiol; INHANCE pooled, >0 to 3 cigarettes/day vs never. Closest published category; >3 to 5/day is 2.23 (1.45 to 3.42) |
| tobacco = former | 2 | 1.56 | 1.41 (1.20 to 1.66) | 2 | 1 to 2 | yes | oral cavity | Possenti et al. 2026; 23 studies, former vs never |
| alcohol = daily | 5 | 3.06 | 5.13 (4.31 to 6.10) | 7 | 7 to 8 | no | oral cavity and pharynx | Bagnardi et al. 2015, Br J Cancer; heavy, >50 g/day, 52 studies. See mapping note below |
| alcohol = weekly | 3 | 1.96 | 1.83 (1.62 to 2.07) | 3 | 2 to 3 | yes | oral cavity and pharynx | Bagnardi et al. 2015; moderate, >12.5 to 50 g/day |
| alcohol = rarely | 1 | 1.25 | 1.13 (1.00 to 1.26) | 1 | 0 to 1 | yes | oral cavity and pharynx | Bagnardi et al. 2015; light, up to 12.5 g/day |
| betel = current | 9 | 7.49 | 7.74 (5.38 to 11.13) | 9 | 8 to 11 | yes | oral cavity and oropharynx | Guha et al. 2014, Int J Cancer (IARC); betel quid with tobacco, Indian subcontinent, 31 studies. Without tobacco: India 2.56 (2.00 to 3.28), Taiwan 10.98 (4.86 to 24.84) |
| betel = past | 4 | 2.45 | 6.87 (4.10 to 11.52) | 9 | 6 to 11 | no | oral cavity | Gupta et al. 2022, Ann Glob Health; former chewers of betel quid with tobacco vs never, 7 studies. Without tobacco: 5.61 (2.24 to 14.04), 4 studies |
| family = yes | 3 | 1.96 | 1.53 (1.11 to 2.11) | 2 | 0 to 3 | yes | oral cavity | Negri et al. 2009, Int J Cancer; INHANCE pooled, 12 studies, first-degree relative with head and neck cancer. All sites 1.68 (1.23 to 2.29) |
| systemic = yes | 5 | 3.06 | 2.56 (2.17 to 3.01) | 4 | 3 to 5 | no | oral cavity and pharynx | Engels et al. 2011, JAMA; US Transplant Cancer Match cohort, standardised incidence ratio for "other oral cavity and pharynx" in solid organ transplant recipients. SIR, not OR; transplant only |
| diet = rarely | 3 | 1.96 | 1.96 (1.54 to 2.50) | 3 | 2 to 4 | yes | oral cavity | Pavia et al. 2006, Am J Clin Nutr; inverse of OR 0.51 (0.40 to 0.65) per daily portion of fruit, 16 studies. INHANCE (Chuang 2012) top vs bottom quartile fruit: 0.52 (0.43 to 0.62) |
| sun = daily | 2 | 1.56 | 1.67 (1.38 to 2.03) | 2 | 1 to 3 | yes | lip only | Kenborg et al. 2010, Cancer Causes Control; Danish population-based case-control, male wage earners, outdoor work over 10 years. Single study |
| tobacco x alcohol bonus | +3 | 1.96 | 3.09 (1.82 to 5.23) | 5 | 3 to 7 | yes | oral cavity | Hashibe et al. 2009, CEBP; INHANCE pooled, 17 studies, multiplicative interaction parameter for ever tobacco x ever alcohol. All sites 2.15 (1.53 to 3.04) |

**Alcohol mapping.** The questionnaire asks frequency; Bagnardi reports
grams per day. The primary run maps the three deployed levels onto Bagnardi's
three bands in order (daily = heavy, weekly = moderate, rarely = light). The
alternative maps daily drinking at typical amounts to the moderate band and
weekly to light, leaving "rarely" inside Bagnardi's reference group with no
published OR. Both are reported; the choice matters for the betel profile.

**Could not be sourced, held at the deployed weight:**

| Factor | Why |
|---|---|
| age (all levels) | Age is a matching or adjustment variable in every source study. No case-control OR with a CI exists. SEER incidence rate ratios are rates, not odds ratios, and were not substituted |
| sex (all levels) | Same. The INHANCE sex analyses report within-sex ORs for other exposures, not a male-vs-female OR adjusted for tobacco and alcohol |
| hpv = history | The question is a self-reported proxy ("have had an HPV-related condition"). No published OR exists for that exposure. Schwartz et al. 1998 (JNCI) report that a history of genital warts raised oral SCC risk among men but give no OR in the abstract. Published ORs exist only for confirmed HPV-16 infection or seropositivity, and those are run as separate scenarios (section 4) |
| hpv = neither, unknown; sex = prefer not to say; family = distant; systemic = unsure; diet = weekly; sun = regular | Design hedges with no epidemiological referent |
| symptom | A clinical red flag, not an exposure. It also forces the tier, so its weight never matters |
| dental | A detection-delay proxy by the instrument's own account, not a risk factor |

The instrument has 13 weighted, non-reference options plus the bonus that
carry epidemiological meaning. Thirteen of them are propagated. The rest are
fixed, which means the propagation understates the true uncertainty. That is
stated again in section 6.

**Two discrepancies not in the table that matter:**

- **Betel without tobacco.** The question does not ask whether tobacco is in
  the quid. For a user chewing without tobacco on the Indian subcontinent the
  published OR is 2.56, which would be a weight of 4, not 9.
- **HPV.** The suspicion in the brief is confirmed. The deployed weight of 5
  implies OR 3.06. Confirmed HPV-16 in the oropharynx is 4.3 (Hobbs 2006
  meta-analysis of HPV detection), 14.6 (D'Souza 2007, oral HPV-16 infection)
  or 32.2 (D'Souza 2007, HPV-16 L1 seropositivity), which are weights of 7, 12
  and 16. None of them is the right OR for a self-report question, but the gap
  between 5 and any of them is the point.

## 3. The anchor

k = 4.47 is defined by the tobacco anchor, so it is not independent of the
data. The propagation was run both ways.

**(a) Fixed scale.** k held at 4.47; each OR drawn independently from its CI.
This isolates per-weight sensitivity. It also silently assumes the tobacco
point estimate of 6.0 is exact for the purpose of scaling everyone else, while
letting that same OR vary for its own weight. Those two treatments of one
number are inconsistent.

**(b) Floating scale.** The daily tobacco OR is drawn from its CI, k is
recomputed so the anchor still yields 8, every sourced weight is re-derived on
that k, and every unsourced weight is re-scaled by holding its implied OR
fixed. Daily tobacco is then always exactly 8 and carries no variance at all;
its uncertainty has been moved onto every other weight instead.

| | fixed (a) | floating (b) |
|---|---|---|
| k | 4.47 | 6.56 (5.46 to 8.25) |
| profiles with one tier on 95% of draws | 73.7% | 79.8% |
| mean probability of landing in the deployed tier | 83.3% | 67.9% |
| under-called mass (dangerous) | 8.8% | 32.0% |
| over-called mass | 7.8% | 0.2% |
| profiles with at least 5% under-call | 15.3% | 39.1% |
| profiles with at least 50% under-call | 8.5% | 32.1% |

The floating run's higher "stability" is not reassuring. It comes from 60% of
the profile space being deployed as high and staying there when everything
inflates. The moderate tier is stable on 13% of its profiles and the elevated
tier on 57%.

**Which is more honest.** (b), for the question the brief actually asks, which
is whether the calibration depends on a quantity that is itself uncertain. It
does, and the dependence is dominated by the tobacco point estimate rather
than its interval: the published OR is 3.39 and the anchor is 6.0. Anchoring
on an OR that the literature does not support means every other weight is
expressed in units that are too large, so the tier boundaries sit higher in OR
terms than they were designed to. (a) remains the right run for the narrower
question of which individual weights are fragile.

One caveat runs the other way. The boundaries were set against reference
profiles on the 4.47 scale, not against point values. If they are read as
pinned to those profiles, they should float with k, and (b) overstates the
damage. The reference profiles themselves do not survive re-derivation,
though: at published point estimates, daily tobacco plus daily alcohol plus
the interaction is 8 + 11 + 7 = 26 on the floating scale, not the 16 the
elevated band was built around, because the literature puts heavy alcohol
above current smoking for oral cavity cancer and the instrument has them the
other way round.

**Isolating interval width from point disagreement.** A diagnostic run keeps
the deployed implied ORs as the centre of each distribution and applies only
the published interval widths.

| | CI width only, fixed | CI width only, floating |
|---|---|---|
| k | 4.47 | 4.47 (3.93 to 5.20) |
| stable profiles | 73.5% | 65.6% |
| mean probability of deployed tier | 93.9% | 92.1% |
| under-called mass | 2.7% | 3.7% |
| over-called mass | 3.4% | 4.2% |

So interval width on its own moves about 6% of tier mass. Point-estimate
disagreement moves a further 11% under the fixed scale and a further 26%
under the floating scale. The finding is not "the CIs are wide". It is "the
point estimates used are not the ones in the meta-analyses, and the anchor is
the worst of them".

## 4. Propagation

ln(OR) drawn from Normal(ln(point), se) with se = (ln(hi) - ln(lo)) / 3.92,
10,000 draws, seed 20260914. Weights re-rounded on every draw with
round-half-up to match `Math.round`. The full profile space of 4 x 3 x 4 x 4
x 3 x 4 x 3 x 3 x 4 x 3 x 3 x 4 = 2,985,984 combinations was enumerated.

**Symptom.** The deployed engine forces high for symptom = yes and for
symptom = unsure (`riskEngine.ts`, `hasUrgentSymptom`). The written spec says
only "yes". Both slices were excluded from the scored space, leaving 995,328
profiles. Scoring the "unsure" slice as a 3-point answer instead, as the spec
describes, gives 1,990,656 profiles and slightly better numbers (77.9%
stable, 7.5% under-called, 6.9% over-called). The discrepancy between the spec
and the code is itself worth resolving.

**Deployed tier share of the enumerated space:** low 0.1%, moderate 6.1%,
elevated 34.2%, high 59.6%. Every combination counts once. The space is not
weighted by how common each profile is, so a current betel user with HPV
history and immunosuppression counts the same as a 40-year-old woman who has
never smoked. Section 6 covers what that does to the numbers.

### 4.1 Fixed scale, primary run

Transition matrix, rows deployed tier, columns mean share of draws:

| deployed | low | moderate | elevated | high |
|---|---|---|---|---|
| low | 97.4 | 2.6 | 0.0 | 0.0 |
| moderate | 0.6 | 77.4 | 21.9 | 0.0 |
| elevated | 0.0 | 7.1 | 71.0 | 21.9 |
| high | 0.0 | 0.0 | 9.0 | 91.0 |

**Least stable boundary.** Elevated/high. 20.9% of profiles have at least 5%
of draws on each side of it, against 5.3% for moderate/elevated and 0.1% for
low/moderate. The mean crossing mass is 5.1%, 1.3% and 0.0%.

**Where the fragility sits, by deployed score:**

| deployed score | tier | share of space | stable | under-called | over-called |
|---|---|---|---|---|---|
| 5 | moderate | 0.1% | 43% | 0% | 26% |
| 11 | moderate | 1.0% | 80% | 19% | 0% |
| 12 | moderate | 1.4% | 90% | 28% | 0% |
| 13 | moderate | 1.7% | 74% | 37% | 0% |
| 14 | elevated | 2.2% | 50% | 0% | 41% |
| 15 | elevated | 2.6% | 63% | 1% | 24% |
| 20 | elevated | 4.6% | 57% | 29% | 0% |
| 21 | elevated | 4.9% | 57% | 38% | 0% |
| 22 | elevated | 5.1% | 51% | 49% | 0% |
| 23 | high | 5.2% | 51% | 0% | 39% |
| 24 | high | 5.2% | 52% | 0% | 28% |
| 25 | high | 5.2% | 60% | 0% | 19% |
| 29 and above | high | 25% | 96 to 100% | 0% | under 1% |

**Direction, separated.**

Under-called (the deployed tier is below what the draws support). Mean 8.8%
of tier mass. 15.3% of profiles carry at least 5% and 8.5% carry at least
50%. In absolute terms most of this is elevated profiles that should read
high (7.5 of the 8.8 points); the moderate profiles that should read elevated
are 1.3 points of the total but 22% of the moderate tier's own mass. The
answers over-represented in the under-called mass:

| answer | share of under-called mass | share of space | ratio |
|---|---|---|---|
| betel = past | 82.6% | 33.3% | 2.48 |
| tobacco = never | 48.8% | 25.0% | 1.95 |
| tobacco = former | 36.7% | 25.0% | 1.47 |
| alcohol = daily | 31.9% | 25.0% | 1.28 |

Past betel dominates because its weight is 4 and the published former-chewer
OR implies 9. Never and former tobacco are over-represented because those
profiles get no compensating over-weight from the tobacco question.

Over-called (the deployed tier is above what the draws support). Mean 7.8%.
16.7% of profiles carry at least 5% and 6.9% carry at least 50%.

| answer | share of over-called mass | share of space | ratio |
|---|---|---|---|
| betel = never | 66.5% | 33.3% | 2.00 |
| tobacco = occasional | 44.6% | 25.0% | 1.79 |
| alcohol = rarely | 44.2% | 25.0% | 1.77 |
| family = yes | 32.4% | 25.0% | 1.30 |

Occasional tobacco is weighted 5 where the closest published category implies
2; daily tobacco is 8 where the literature implies 5. Profiles built on
tobacco without betel are therefore reading a tier too high.

**Concrete profiles most at risk of under-call** (every one of these reads
elevated today and lands high on essentially every draw):

- A man under 35 who chews betel in the past, drinks daily, works outdoors
  unprotected, has a close relative with oral cancer and is immunosuppressed.
  Score 22.
- A former smoker under 35, past betel, daily alcohol, outdoor sun, distant
  relative, immunosuppressed. Score 22.
- A former smoker under 35, past betel, daily alcohol, outdoor sun,
  immunosuppressed. Score 21.
- An occasional smoker under 35 with past betel, daily alcohol and outdoor sun.
  Score 22.

**Most at risk of over-call** (reads high today, lands elevated on essentially
every draw):

- A man under 35 who smokes daily, drinks rarely, works outdoors unprotected,
  has a close relative with oral cancer and is immunosuppressed. Score 23.
- The same without the alcohol and with a dental visit over three years ago.
  Score 23.
- A man under 35 who smokes daily and has a close relative with oral cancer.
  Score 14, reads elevated, lands moderate on every draw.

### 4.2 Floating scale

Transition matrix:

| deployed | low | moderate | elevated | high |
|---|---|---|---|---|
| low | 42.2 | 57.7 | 0.1 | 0.0 |
| moderate | 0.1 | 28.3 | 57.6 | 13.9 |
| elevated | 0.0 | 0.3 | 19.2 | 80.4 |
| high | 0.0 | 0.0 | 0.1 | 99.9 |

Four in five elevated profiles land high; more than half of moderate profiles
land elevated; more than half of low profiles land moderate. Over-call is
0.2%. The profiles most under-called are ordinary ones: a man under 35 who
smokes and drinks daily and works outdoors (score 21, high on 100% of draws);
a former smoker under 35 who drinks daily, works outdoors, has a close
relative with oral cancer and is immunosuppressed (score 20, high on 99.5%).
The only meaningful over-call is a woman under 35 whose sole factor is
occasional tobacco: score 5, reads moderate, lands low on 94% of draws.

### 4.3 Boundary shifts

One boundary moved at a time; the deployed tiers are recomputed on the
shifted boundaries, so this measures how stable the instrument would then be.

| boundary | shift | fixed: stable | fixed: under | fixed: over | floating: stable | floating: under |
|---|---|---|---|---|---|---|
| elevated/high | -2 (20) | 77.1% | 7.8% | 7.5% | 84.8% | 24.7% |
| elevated/high | -1 (21) | 75.3% | 8.4% | 7.7% | 82.3% | 28.4% |
| elevated/high | 0 (22) | 73.7% | 8.8% | 7.8% | 79.8% | 32.0% |
| elevated/high | +1 (23) | 72.5% | 9.1% | 7.9% | 77.5% | 35.5% |
| elevated/high | +2 (24) | 71.7% | 9.3% | 7.9% | 75.4% | 38.8% |
| moderate/elevated | -2 (11) | 75.7% | 8.0% | 6.9% | 81.6% | 30.4% |
| moderate/elevated | +2 (15) | 70.9% | 10.0% | 8.8% | 79.8% | 33.3% |
| low/moderate | -2 to +2 | 73.4 to 73.8% | 8.8% | 7.8 to 8.0% | 79.6 to 79.8% | 31.9 to 32.1% |

The best available move, lowering the elevated/high boundary to 20, gains
3.4 points of stability on the fixed scale and 5 on the floating scale, and
trims under-call by 1 and 7 points respectively. In the no-betel subspace it
goes the other way: stability falls from 69.6% to 68.2%, because that
subspace is over-called, not under-called. No shift of one or two points
changes the picture. The instability is in the weights.

### 4.4 The two named profiles

**Under 35, non-smoking, non-drinking, HPV history. Score 5, moderate.**
Sex taken as female so that nothing else contributes.

| scenario | HPV weight | score, median (2.5th to 97.5th) | low | moderate | elevated | high |
|---|---|---|---|---|---|---|
| primary (proxy held at 5) | 5 | 5 (5 to 5) | 0 | 100 | 0 | 0 |
| floating scale, proxy held | 7 | 7 (6 to 9) | 0 | 100 | 0 | 0 |
| Hobbs 2006, oropharynx HPV detection, 4.3 | 7 | 6 (3 to 10) | 12 | 88 | 0 | 0 |
| D'Souza 2007, oral HPV-16 infection, 14.6 | 12 | 12 (8 to 16) | 0 | 77 | 23 | 0 |
| D'Souza 2007, HPV-16 seropositivity, 32.2 | 16 | 15 (12 to 19) | 0 | 14 | 86 | 0 |
| floating scale with D'Souza 14.6 | 18 | 17 (11 to 25) | 0 | 11 | 79 | 10 |

The instrument does under-serve this profile, but by less than the raw
comparison of 3 against 15 suggests. Even scored at the published OR for
confirmed oral HPV-16 infection, the median lands one point short of elevated.
It reaches elevated reliably only at the seropositivity OR or on the floating
scale. It never reaches high in any run. Whether a self-reported "HPV-related
condition" deserves the OR for laboratory-confirmed HPV-16 is not something a
sensitivity analysis can decide, and the honest weight for the proxy is
unknown.

**Current betel, daily tobacco, daily alcohol. Score 25, high.**

| scenario | score, median (2.5th to 97.5th) | elevated | high |
|---|---|---|---|
| primary, fixed scale | 27 (24 to 30) | 0.5 | 99.5 |
| fixed scale, CI width only | 25 (22 to 28) | 6.8 | 93.2 |
| fixed scale, alcohol = moderate band | 22 (19 to 26) | 52.2 | 47.8 |
| floating scale | 39 (33 to 49) | 0 | 100 |
| floating scale, alcohol = moderate band | 33 (27 to 41) | 0 | 100 |

The decision not to rescale the thresholds holds under every run except one.
At published point estimates on k = 4.47 the profile scores 5 + 7 + 9 + 5 =
26: daily tobacco falls three points, and daily alcohol and the interaction
term rise two each. If daily alcohol is the moderate band rather than heavy,
the score is 22 and the profile is a coin flip between elevated and high.
The margin that protects this profile is therefore the alcohol mapping, not
the three points of headroom above 23.

## 5. What it means for the instrument

Stated as findings, not recommendations, because the brief asked for the
former.

1. The tobacco anchor is above the published interval for oral cavity cancer.
   Everything else is expressed in units derived from it. This is the first
   thing a reviewer with the meta-analyses in front of them will notice.
2. Past betel use is the single most under-weighted answer. Risk reversal
   after cessation is small in the published data; the deployed weight assumes
   it is large.
3. Occasional tobacco is the single most over-weighted answer relative to the
   closest published category.
4. Daily alcohol and the tobacco-alcohol bonus are both under-weighted if
   daily drinking is taken to mean heavy drinking, and about right if it is
   taken to mean moderate. The questionnaire cannot distinguish the two.
5. The elevated/high boundary is the least stable, and the profiles that
   straddle it are not exotic: former or never smokers with past betel and
   daily alcohol on one side, daily smokers without betel on the other.
6. The HPV weight is low against every published OR for confirmed infection,
   and the profile it under-serves does not reach elevated at the median even
   when scored at the oral-infection OR.
7. The spec and the code disagree on symptom = unsure. The code forces high;
   the spec scores it at 3.

## 6. What this method cannot tell you

- **Transportability.** The ORs are pooled across populations that do not
  match each other or the user base. Tobacco and family history come from
  INHANCE and global meta-analyses; betel from the Indian subcontinent, with a
  Taiwanese estimate four times higher for the same exposure; alcohol from a
  global meta-analysis; immunosuppression from US transplant recipients; sun
  exposure from Danish male wage earners; HPV from a single US case-control
  study. Summing their log-odds assumes each effect transports to whoever
  opens the page. Nothing in this analysis tests that assumption, and the
  intervals sampled here do not contain it. The true uncertainty is wider than
  anything reported above.
- **Unsourced weights.** Age, sex, dental, the HPV proxy and the hedge options
  were held fixed. Their uncertainty is not zero; it is unquantified. The
  stability figures are therefore upper bounds on stability.
- **Question-to-category mapping.** "Occasionally", "daily or near-daily" and
  "in the past" were mapped to published exposure categories by judgment. The
  alcohol mapping alone flips one of the two named profiles.
- **Uniform profile space.** Every combination counts once. The population
  that uses the tool is nothing like uniform over these answers. In the
  no-betel subspace, which is closer to a US user base, the instrument
  over-calls (15.6%) far more than it under-calls (3.2%) on the fixed scale,
  and under-calls 41.9% on the floating scale. A population-weighted version
  needs answer distributions the tool does not collect.
- **Independence.** Each OR was drawn independently. The published estimates
  are correlated through shared adjustment sets and overlapping study
  populations (several are INHANCE pooled analyses of the same studies). The
  floating scale captures one such correlation, through k, and no other.
- **Additivity.** The log-additive structure with a single interaction term is
  assumed, not tested. The published interaction parameter applies to ever
  tobacco and ever alcohol, not to the frequency-gated bonus rule.
- **The ratio measures are not all odds ratios.** The immunosuppression
  figure is a standardised incidence ratio; the diet figure is an inverted
  protective OR per portion; the sun figure is for lip cancer only.
- **Validity.** None of this says whether any tier corresponds to any level of
  actual risk. That requires outcome data, and the tool has none.

## 7. Methods paragraph

Weights in the instrument are integer transforms of published odds ratios,
w = round(4.47 ln OR), with the scale constant fixed so that daily tobacco use
at OR 6.0 receives 8 points; tier boundaries at 4, 13 and 22 points were set
by judgment. To quantify the sensitivity of tier assignment to uncertainty in
the source estimates, we identified a meta-analytic or pooled-consortium odds
ratio and 95% confidence interval for each weighted response option (13
options and one interaction term across seven questions; sources in Table 2),
holding options without a defensible published interval (age, sex, dental
attendance, self-reported HPV history and hedge responses) at their deployed
weights. For each of 10,000 Monte Carlo draws, each log odds ratio was
sampled from a normal distribution with mean ln(OR) and standard deviation
(ln U - ln L)/3.92, weights were re-rounded, and every profile in the fully
enumerated response space (995,328 combinations after excluding the symptom
responses that force the top tier) was re-scored and re-tiered. Two scale
treatments were run: a fixed scale holding the constant at 4.47, and a
floating scale in which the constant was recomputed on each draw from the
sampled tobacco odds ratio so that the anchor remained at 8 points. We report,
for each profile, the probability of assignment to each tier; the proportion
of profiles with a single tier on at least 95% of draws; the mass and
direction of disagreement with the deployed tier, separating profiles tiered
below the sampled evidence from those tiered above it; the sensitivity of
these quantities to one- and two-point shifts in each boundary; and scenario
analyses substituting published odds ratios for confirmed HPV-16 exposure for
the self-report proxy. This analysis evaluates internal robustness to
published parameter uncertainty only. It is not a validation against clinical
outcomes, it assumes that effect estimates pooled from heterogeneous source
populations transport to users of the instrument, it treats the sampled odds
ratios as independent, and it weights every response combination equally.

## 8. Re-running

```bash
python3 scripts/sensitivity_analysis.py
python3 scripts/sensitivity_analysis.py --mode floating
python3 scripts/sensitivity_analysis.py --hpv dsouza_oral
python3 scripts/sensitivity_analysis.py --alcohol-map frequency
python3 scripts/sensitivity_analysis.py --restrict betel=never
python3 scripts/sensitivity_analysis.py --centre deployed
python3 scripts/sensitivity_analysis.py --json out.json --csv profiles.csv
```

Homebrew `python3` (3.14) has numpy; `/usr/bin/python3` does not. A run takes
one to two minutes. When a weight changes, edit `QUESTIONS` in the script;
when a boundary changes, edit `BOUNDARIES`; when a better source turns up,
edit `SOURCES`. The named profiles are in `NAMED_PROFILES`.
