#!/usr/bin/env python3
"""
OralCheck risk score: sensitivity of tier assignments to odds-ratio uncertainty.

What this does
--------------
The instrument turns published odds ratios (OR) into integer weights with
    weight = round(ln(OR) * k),   k = 4.47
where k is anchored so that daily tobacco (OR 6.0) lands on 8. This script asks
how fragile the tier assignments are once each OR is allowed to vary within its
published 95% confidence interval.

For each sourced OR it draws ln(OR) ~ Normal(ln(point), se), with
    se = (ln(upper) - ln(lower)) / (2 * 1.959964)
so the draws reproduce the published CI. Weights are re-rounded on every draw.
The full profile space is enumerated (not sampled) and every profile's tier is
recorded on every draw. Everything reported downstream comes from the resulting
per-profile score histogram.

Two scale treatments (see --mode):
  fixed     k stays at 4.47; each OR varies independently. Isolates per-weight
            sensitivity.
  floating  the daily-tobacco OR is drawn from its CI, k is recomputed so the
            anchor still yields 8, then every other weight (sourced or not) is
            re-derived on that k. Sourced weights: round(ln(OR_draw) * k).
            Unsourced weights: round(w_deployed / 4.47 * k), i.e. their implied
            OR is held fixed and re-scaled. Tests whether calibration depends on
            a quantity that is itself uncertain.

What is NOT propagated (held at the deployed weight) and why:
  age, sex, dental, symptom      no case-control OR with a CI exists; age and
                                 sex are matching variables in the source
                                 studies, dental is a detection-delay proxy by
                                 the instrument's own account, symptom is a
                                 clinical red flag not an exposure
  hpv (all options)              the question is a self-reported proxy, and no
                                 published OR exists for "has had an HPV-related
                                 condition". See --hpv for scenario runs that
                                 score it at published HPV-16 ORs instead.
  family=distant, diet=weekly, sun=regular, systemic=unsure,
  hpv=neither/unknown, sex=preferNotToSay
                                 design hedges with no epidemiological referent

Symptom handling: the deployed engine (src/lib/riskEngine.ts) forces the high
tier for symptom = yes AND symptom = unsure. Both are excluded from the scored
space by default. --score-unsure-symptom includes the "unsure" slice as a
scored 3-point answer, which is what the written spec describes.

This is a sensitivity analysis over published confidence intervals. It is not
a validation and does not touch clinical outcomes.

Usage
-----
  python3 scripts/sensitivity_analysis.py                 # fixed scale
  python3 scripts/sensitivity_analysis.py --mode floating
  python3 scripts/sensitivity_analysis.py --hpv dsouza_oral
  python3 scripts/sensitivity_analysis.py --alcohol-map frequency
  python3 scripts/sensitivity_analysis.py --json out.json --csv profiles.csv

Standard library plus numpy only.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from dataclasses import dataclass

import numpy as np

# ----------------------------------------------------------------------------
# The instrument, exactly as deployed (src/lib/questions.ts, riskEngine.ts)
# ----------------------------------------------------------------------------

K_DEPLOYED = 4.47
ANCHOR_WEIGHT = 8          # daily tobacco is pinned here
INTERACTION_BONUS = 3      # tobacco daily/occasional AND alcohol daily/weekly
BOUNDARIES = (4, 13, 22)   # low <=4 | moderate <=13 | elevated <=22 | high
TIERS = ("low", "moderate", "elevated", "high")

QUESTIONS: list[tuple[str, list[tuple[str, int]]]] = [
    ("age",      [("under35", 0), ("35to54", 2), ("55to64", 4), ("65plus", 6)]),
    ("sex",      [("male", 3), ("female", 0), ("preferNotToSay", 2)]),
    ("tobacco",  [("daily", 8), ("occasional", 5), ("former", 2), ("never", 0)]),
    ("alcohol",  [("daily", 5), ("weekly", 3), ("rarely", 1), ("never", 0)]),
    ("betel",    [("current", 9), ("past", 4), ("never", 0)]),
    ("hpv",      [("vaccinated", 0), ("neither", 2), ("history", 5), ("unknown", 1)]),
    ("sun",      [("daily", 2), ("regular", 1), ("minimal", 0)]),
    ("symptom",  [("yes", 6), ("unsure", 3), ("no", 0)]),
    ("family",   [("yes", 3), ("distant", 1), ("no", 0), ("unsure", 0)]),
    ("systemic", [("yes", 5), ("unsure", 1), ("no", 0)]),
    ("diet",     [("daily", 0), ("weekly", 1), ("rarely", 3)]),
    ("dental",   [("recent", 0), ("fewyears", 1), ("longago", 2), ("never", 3)]),
]
QID = {q: i for i, (q, _) in enumerate(QUESTIONS)}
OPTS = {q: [o for o, _ in opts] for q, opts in QUESTIONS}
OIDX = {q: {o: j for j, (o, _) in enumerate(opts)} for q, opts in QUESTIONS}
DEPLOYED = {q: {o: w for o, w in opts} for q, opts in QUESTIONS}

PLAIN = {
    "age": {"under35": "under 35", "35to54": "aged 35 to 54", "55to64": "aged 55 to 64", "65plus": "65 or older"},
    "sex": {"male": "male", "female": "female", "preferNotToSay": "sex not given"},
    "tobacco": {"daily": "daily tobacco", "occasional": "occasional tobacco", "former": "former tobacco", "never": "never tobacco"},
    "alcohol": {"daily": "daily alcohol", "weekly": "alcohol a few times a week", "rarely": "rare alcohol", "never": "no alcohol"},
    "betel": {"current": "current betel", "past": "past betel", "never": "no betel"},
    "hpv": {"vaccinated": "HPV-vaccinated", "neither": "unvaccinated, no HPV history", "history": "HPV history", "unknown": "HPV status unknown"},
    "sun": {"daily": "daily unprotected sun", "regular": "regular sun", "minimal": "minimal sun"},
    "symptom": {"yes": "symptom", "unsure": "unsure about symptom", "no": "no symptom"},
    "family": {"yes": "close relative with oral cancer", "distant": "distant relative", "no": "no family history", "unsure": "family history unknown"},
    "systemic": {"yes": "immunosuppressed", "unsure": "immune status unsure", "no": "no immune condition"},
    "diet": {"daily": "daily fruit and veg", "weekly": "weekly fruit and veg", "rarely": "rarely eats fruit and veg"},
    "dental": {"recent": "dental visit within a year", "fewyears": "dental visit 1 to 3 years ago", "longago": "dental visit over 3 years ago", "never": "never seen a dentist"},
}

# ----------------------------------------------------------------------------
# Sourced odds ratios. Only entries listed here are propagated.
# point, lo, hi are exactly as published. Nothing here is approximated.
# ----------------------------------------------------------------------------


@dataclass(frozen=True)
class OR:
    point: float
    lo: float
    hi: float
    source: str
    site: str
    note: str = ""

    @property
    def log_se(self) -> float:
        return (math.log(self.hi) - math.log(self.lo)) / (2 * 1.959964)


# Primary sources. Keys are (question, option) or ("interaction",).
SOURCES: dict[tuple, OR] = {
    ("tobacco", "daily"): OR(3.39, 2.64, 4.35,
        "Possenti et al. 2026, Oncology Reviews (meta-analysis, 25 studies): current vs never smokers",
        "oral cavity",
        "Gandini et al. 2008 IJC gives oral RR 3.43 (2.37-4.94), consistent. Pharynx current: 4.24 (2.96-6.09)."),
    ("tobacco", "occasional"): OR(1.48, 1.04, 2.09,
        "Berthiller et al. 2016, Int J Epidemiol (INHANCE pooled): >0-3 cigarettes/day vs never",
        "oral cavity",
        "Closest published category to 'occasionally'. >3-5/day: 2.23 (1.45-3.42); >5-10/day: 2.18 (1.68-2.83)."),
    ("tobacco", "former"): OR(1.41, 1.20, 1.66,
        "Possenti et al. 2026, Oncology Reviews (meta-analysis, 23 studies): former vs never smokers",
        "oral cavity"),
    ("betel", "current"): OR(7.74, 5.38, 11.13,
        "Guha et al. 2014, Int J Cancer (IARC meta-analysis, 31 studies): betel quid WITH tobacco, Indian subcontinent",
        "oral cavity and oropharynx",
        "Betel quid WITHOUT tobacco, India: 2.56 (2.00-3.28); Taiwan: 10.98 (4.86-24.84). Question does not ask about tobacco in the quid."),
    ("betel", "past"): OR(6.87, 4.10, 11.52,
        "Gupta et al. 2022, Ann Glob Health (meta-analysis, 7 studies): former betel quid WITH tobacco vs never",
        "oral cavity",
        "Former betel WITHOUT tobacco: 5.61 (2.24-14.04, 4 studies). Risk reversal after cessation is small."),
    ("family", "yes"): OR(1.53, 1.11, 2.11,
        "Negri et al. 2009, Int J Cancer (INHANCE pooled, 12 studies): first-degree relative with head and neck cancer",
        "oral cavity",
        "All head and neck: 1.68 (1.23-2.29); oropharynx 1.55 (1.16-2.07)."),
    ("systemic", "yes"): OR(2.56, 2.17, 3.01,
        "Engels et al. 2011, JAMA (US Transplant Cancer Match cohort): SIR, 'other oral cavity and pharynx', solid organ transplant recipients",
        "oral cavity and pharynx (excl. lip, oropharynx)",
        "This is a standardised incidence ratio, not an OR, and covers transplant only. Oropharynx incl. tonsil SIR 2.01 (1.64-2.43); lip 16.78 (14.02-19.92)."),
    ("diet", "rarely"): OR(1 / 0.51, 1 / 0.65, 1 / 0.40,
        "Pavia et al. 2006, Am J Clin Nutr (meta-analysis, 16 studies): inverse of OR 0.51 (0.40-0.65) per daily portion of fruit",
        "oral cavity",
        "Inverted so that low intake is the exposure. INHANCE (Chuang 2012) Q4 vs Q1 fruit for HNC: 0.52 (0.43-0.62)."),
    ("sun", "daily"): OR(1.67, 1.38, 2.03,
        "Kenborg et al. 2010, Cancer Causes Control (Danish population-based case-control): outdoor work >10 years, lip cancer",
        "lip only",
        "Single study, male wage earners in Denmark. No meta-analysis exists for lip cancer and sun exposure."),
    ("interaction",): OR(3.09, 1.82, 5.23,
        "Hashibe et al. 2009, CEBP (INHANCE pooled, 17 studies): multiplicative interaction parameter psi, ever tobacco x ever alcohol",
        "oral cavity",
        "All head and neck: 2.15 (1.53-3.04). psi is the joint OR divided by the product of the single-exposure ORs, which is exactly what the flat bonus represents."),
}

# Alcohol: Bagnardi et al. 2015, Br J Cancer, oral cavity and pharynx, 52 studies.
# The questionnaire asks frequency; Bagnardi reports grams/day. The mapping is a
# judgment and is exposed as a switch.
BAGNARDI = {
    "heavy":    OR(5.13, 4.31, 6.10, "Bagnardi et al. 2015, Br J Cancer: >50 g/day vs non/occasional drinkers", "oral cavity and pharynx"),
    "moderate": OR(1.83, 1.62, 2.07, "Bagnardi et al. 2015, Br J Cancer: >12.5-50 g/day", "oral cavity and pharynx"),
    "light":    OR(1.13, 1.00, 1.26, "Bagnardi et al. 2015, Br J Cancer: <=12.5 g/day", "oral cavity and pharynx"),
}
ALCOHOL_MAPS = {
    # ordinal-to-ordinal: the instrument's three levels onto Bagnardi's three
    "quantity":  {"daily": "heavy", "weekly": "moderate", "rarely": "light"},
    # frequency-faithful: daily drinking at typical amounts is 'moderate' in
    # g/day terms; 'rarely' falls inside Bagnardi's reference group, so it has
    # no published OR and stays at the deployed weight
    "frequency": {"daily": "moderate", "weekly": "light"},
}

# HPV scenarios. The deployed weight (5) is a deliberately deflated proxy with no
# published OR behind it. These scenarios score "history" at a published OR for a
# confirmed HPV-16 exposure, to show what the proxy would need to carry if it were
# treated as the real thing.
HPV_SCENARIOS = {
    "deployed": None,
    "hobbs_oroph": OR(4.3, 2.1, 8.9,
        "Hobbs et al. 2006, Clin Otolaryngol (meta-analysis): HPV detection, oropharynx", "oropharynx",
        "Tonsil: 15.1 (6.8-33.7); oral cavity: 2.0 (1.2-3.4)."),
    "dsouza_oral": OR(14.6, 6.3, 36.6,
        "D'Souza et al. 2007, NEJM (US case-control): oral HPV-16 infection", "oropharynx"),
    "dsouza_sero": OR(32.2, 14.6, 71.3,
        "D'Souza et al. 2007, NEJM (US case-control): HPV-16 L1 seropositivity", "oropharynx"),
}


def js_round(x: np.ndarray | float):
    """Math.round semantics for non-negative values (half rounds up).
    Python's round() is banker's rounding and would differ at .5."""
    return np.floor(np.asarray(x) + 0.5).astype(np.int64)


def implied_or(weight: int, k: float = K_DEPLOYED) -> float:
    return math.exp(weight / k)


# ----------------------------------------------------------------------------
# Building the set of sourced entries for a run
# ----------------------------------------------------------------------------


def build_sources(alcohol_map: str, hpv: str) -> dict[tuple, OR]:
    src = dict(SOURCES)
    for opt, level in ALCOHOL_MAPS[alcohol_map].items():
        src[("alcohol", opt)] = BAGNARDI[level]
    if HPV_SCENARIOS[hpv] is not None:
        src[("hpv", "history")] = HPV_SCENARIOS[hpv]
    return src


# ----------------------------------------------------------------------------
# Profile enumeration
# ----------------------------------------------------------------------------


def enumerate_profiles(score_unsure_symptom: bool, restrict: dict[str, list[str]] | None = None) -> np.ndarray:
    """Return an (N, 12) int8 matrix of option indices, every combination.
    restrict maps a question to the subset of options to enumerate."""
    ranges = []
    restrict = restrict or {}
    for q, opts in QUESTIONS:
        if q in restrict:
            ranges.append([OIDX[q][o] for o in restrict[q]])
        elif q == "symptom":
            allowed = [OIDX["symptom"]["no"]]
            if score_unsure_symptom:
                allowed.append(OIDX["symptom"]["unsure"])
            ranges.append(allowed)
        else:
            ranges.append(list(range(len(opts))))
    grids = np.meshgrid(*[np.array(r, dtype=np.int8) for r in ranges], indexing="ij")
    return np.stack([g.ravel() for g in grids], axis=1)


def interaction_mask(P: np.ndarray) -> np.ndarray:
    t = P[:, QID["tobacco"]]
    a = P[:, QID["alcohol"]]
    t_on = (t == OIDX["tobacco"]["daily"]) | (t == OIDX["tobacco"]["occasional"])
    a_on = (a == OIDX["alcohol"]["daily"]) | (a == OIDX["alcohol"]["weekly"])
    return t_on & a_on


def deployed_scores(P: np.ndarray) -> np.ndarray:
    s = np.zeros(len(P), dtype=np.int64)
    for q, opts in QUESTIONS:
        w = np.array([w for _, w in opts])
        s += w[P[:, QID[q]]]
    s += INTERACTION_BONUS * interaction_mask(P)
    return s


def tier_of(scores: np.ndarray, boundaries=BOUNDARIES) -> np.ndarray:
    return np.searchsorted(np.array(boundaries), scores, side="left").astype(np.int8)
    # score <= 4 -> 0, 5..13 -> 1, 14..22 -> 2, >=23 -> 3


# ----------------------------------------------------------------------------
# Drawing weights
# ----------------------------------------------------------------------------


def draw_weight_tables(src: dict[tuple, OR], n: int, mode: str, centre: str, rng) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    """Return (W, bonus, k): W[q] is an (n, n_options) int array of weights per draw,
    bonus is (n,), k is (n,)."""
    # draw ln(OR) for each sourced key
    draws: dict[tuple, np.ndarray] = {}
    for key, o in src.items():
        if centre == "published":
            mu = math.log(o.point)
        else:  # deployed-centre: implied OR from the deployed weight, published CI width
            w = INTERACTION_BONUS if key == ("interaction",) else DEPLOYED[key[0]][key[1]]
            mu = w / K_DEPLOYED
        draws[key] = rng.normal(mu, o.log_se, size=n)

    if mode == "floating":
        k = ANCHOR_WEIGHT / draws[("tobacco", "daily")]
    else:
        k = np.full(n, K_DEPLOYED)

    W = []
    for q, opts in QUESTIONS:
        tab = np.zeros((n, len(opts)), dtype=np.int64)
        for j, (o, w_dep) in enumerate(opts):
            key = (q, o)
            if key in draws:
                tab[:, j] = js_round(draws[key] * k)
            elif mode == "floating":
                tab[:, j] = js_round(w_dep / K_DEPLOYED * k)
            else:
                tab[:, j] = w_dep
        W.append(tab)
    if ("interaction",) in draws:
        bonus = js_round(draws[("interaction",)] * k)
    elif mode == "floating":
        bonus = js_round(INTERACTION_BONUS / K_DEPLOYED * k)
    else:
        bonus = np.full(n, INTERACTION_BONUS)
    return W, bonus, k


def point_weight_table(src: dict[tuple, OR], k: float) -> dict[str, dict[str, int]]:
    """Deterministic weights at published point estimates on scale k."""
    out = {}
    for q, opts in QUESTIONS:
        out[q] = {}
        for o, w_dep in opts:
            key = (q, o)
            if key in src:
                out[q][o] = int(js_round(math.log(src[key].point) * k))
            else:
                out[q][o] = int(js_round(w_dep / K_DEPLOYED * k))
    key = ("interaction",)
    out["interaction"] = {"bonus": int(js_round(math.log(src[key].point) * k)) if key in src
                          else int(js_round(INTERACTION_BONUS / K_DEPLOYED * k))}
    return out


# ----------------------------------------------------------------------------
# Propagation: per-profile score histogram over draws
# ----------------------------------------------------------------------------

_ACTIVE_SOURCES: set = set()
NS = 64  # score bins 0..63; anything above is clipped (still 'high', boundaries never exceed 30)


def propagate(P: np.ndarray, W: list[np.ndarray], bonus: np.ndarray, verbose=True) -> np.ndarray:
    """Return hist (N, NS) uint16: count of draws on which profile i scored s.

    Profiles that share the same constant-part sum and the same combination of
    answers on the draw-dependent questions have identical score distributions,
    so the per-draw work is done once per such group and scattered back.
    Under the floating scale every question is draw-dependent through k, but
    the unsourced questions depend on k only, so draws are first grouped by
    the weight rows they induce on those questions."""
    n = len(bonus)
    N = len(P)
    nq = len(W)
    # in floating mode every table varies; separate 'varies only via k' questions
    # (no sourced option) from 'sourced' ones using the deployed source keys
    sourced_q = [i for i in range(nq) if any(((QUESTIONS[i][0], o) in _ACTIVE_SOURCES) for o in OPTS[QUESTIONS[i][0]])]
    const_q = [i for i in range(nq) if i not in sourced_q]
    sizes = [W[i].shape[1] for i in sourced_q]
    combos = np.array(list(itertools.product(*[range(s) for s in sizes])), dtype=np.int64)
    combo_of = np.zeros(N, dtype=np.int64)
    for i, sz in zip(sourced_q, sizes):
        combo_of = combo_of * sz + P[:, i]
    # interaction mask on the combo grid
    ti, ai = sourced_q.index(QID["tobacco"]), sourced_q.index(QID["alcohol"])
    t, a = combos[:, ti], combos[:, ai]
    imask_c = (((t == OIDX["tobacco"]["daily"]) | (t == OIDX["tobacco"]["occasional"]))
               & ((a == OIDX["alcohol"]["daily"]) | (a == OIDX["alcohol"]["weekly"]))).astype(np.int64)
    # group draws by the weight rows they induce on const questions
    if const_q:
        keys = np.concatenate([W[i] for i in const_q], axis=1)
    else:
        keys = np.zeros((n, 1), dtype=np.int64)
    _, grp_first, grp_id = np.unique(keys, axis=0, return_index=True, return_inverse=True)
    grp_id = grp_id.ravel()
    hist = np.zeros((N, NS), dtype=np.uint16)
    t0 = time.time()
    done = 0
    for g, d0 in enumerate(grp_first):
        draws = np.where(grp_id == g)[0]
        base = np.zeros(N, dtype=np.int64)
        for i in const_q:
            base += W[i][d0][P[:, i]]
        pair_key = base * len(combos) + combo_of
        pairs, pair_of = np.unique(pair_key, return_inverse=True)
        pair_of = pair_of.ravel()
        pbase = pairs // len(combos)
        pcombo = pairs % len(combos)
        hp = np.zeros((len(pairs), NS), dtype=np.uint16)
        ar = np.arange(len(pairs))
        for d in draws:
            v = bonus[d] * imask_c
            for c, i in enumerate(sourced_q):
                v = v + W[i][d][combos[:, c]]
            sc = pbase + v[pcombo]
            np.clip(sc, 0, NS - 1, out=sc)
            hp[ar, sc] += 1
            done += 1
            if verbose and done % 2000 == 0:
                print(f"  draw {done}/{n}  ({time.time() - t0:.0f}s)", file=sys.stderr)
        hist += hp[pair_of]
    return hist


def cumulative(hist: np.ndarray) -> np.ndarray:
    return np.cumsum(hist, axis=1, dtype=np.int32)


def tier_probs(cum: np.ndarray, boundaries=BOUNDARIES) -> np.ndarray:
    n = cum[:, -1:].astype(np.float64)
    b = list(boundaries)
    p_low = cum[:, b[0]]
    p_mod = cum[:, b[1]] - cum[:, b[0]]
    p_ele = cum[:, b[2]] - cum[:, b[1]]
    p_high = cum[:, -1] - cum[:, b[2]]
    return np.stack([p_low, p_mod, p_ele, p_high], axis=1) / n


# ----------------------------------------------------------------------------
# Analysis
# ----------------------------------------------------------------------------


def describe(P_row: np.ndarray) -> str:
    parts = []
    for q, _ in QUESTIONS:
        o = OPTS[q][P_row[QID[q]]]
        # skip the 'nothing to say' answers so descriptions stay short
        if (q, o) in {("tobacco", "never"), ("alcohol", "never"), ("betel", "never"),
                      ("sun", "minimal"), ("symptom", "no"), ("family", "no"),
                      ("family", "unsure"), ("systemic", "no"), ("diet", "daily"),
                      ("dental", "recent"), ("hpv", "vaccinated")}:
            continue
        parts.append(PLAIN[q][o])
    return ", ".join(parts) if parts else "every answer at its lowest weight"


def analyse(P, cum, dep_score, boundaries=BOUNDARIES, stable_at=0.95):
    pt = tier_probs(cum, boundaries)
    dep_tier = tier_of(dep_score, boundaries)
    N = len(P)
    p_dep = pt[np.arange(N), dep_tier]
    # 'under' = the draws say a HIGHER tier than the deployed instrument reads.
    # That is the dangerous direction: the tool is telling this person they are
    # safer than the evidence supports.
    ar = np.arange(4)
    p_under = (pt * (ar[None, :] > dep_tier[:, None])).sum(axis=1)
    p_over = (pt * (ar[None, :] < dep_tier[:, None])).sum(axis=1)
    stable = pt.max(axis=1) >= stable_at
    # boundary instability: profile has >=5% of draws on each side of boundary b
    n = cum[:, -1].astype(np.float64)
    bnd = {}
    for name, b in zip(("low/moderate", "moderate/elevated", "elevated/high"), boundaries):
        below = cum[:, b] / n
        straddle = (below >= 0.05) & (below <= 0.95)
        bnd[name] = {
            "profiles_straddling_pct": 100 * straddle.mean(),
            "mean_crossing_mass_pct": 100 * np.minimum(below, 1 - below).mean(),
        }
    return {
        "pt": pt, "dep_tier": dep_tier, "p_dep": p_dep, "p_under": p_under,
        "p_over": p_over, "stable": stable, "boundaries": bnd,
    }


def summarise(P, cum, dep_score, boundaries=BOUNDARIES):
    r = analyse(P, cum, dep_score, boundaries)
    N = len(P)
    dep_tier = r["dep_tier"]
    out = {
        "n_profiles": int(N),
        "boundaries": list(boundaries),
        "deployed_tier_share_pct": {t: float(100 * (dep_tier == i).mean()) for i, t in enumerate(TIERS)},
        "stable_pct": float(100 * r["stable"].mean()),
        "stable_pct_by_deployed_tier": {t: float(100 * r["stable"][dep_tier == i].mean()) if (dep_tier == i).any() else None
                                        for i, t in enumerate(TIERS)},
        "mean_p_deployed_tier_pct": float(100 * r["p_dep"].mean()),
        "under_called": {  # dangerous direction
            "mean_prob_pct": float(100 * r["p_under"].mean()),
            "profiles_with_p_ge_5pct": float(100 * (r["p_under"] >= 0.05).mean()),
            "profiles_with_p_ge_50pct": float(100 * (r["p_under"] >= 0.50).mean()),
        },
        "over_called": {
            "mean_prob_pct": float(100 * r["p_over"].mean()),
            "profiles_with_p_ge_5pct": float(100 * (r["p_over"] >= 0.05).mean()),
            "profiles_with_p_ge_50pct": float(100 * (r["p_over"] >= 0.50).mean()),
        },
        "boundary_instability": r["boundaries"],
        # transition matrix: deployed tier -> mean probability of each drawn tier
        "transition_pct": {
            TIERS[i]: {TIERS[j]: float(100 * r["pt"][dep_tier == i, j].mean()) for j in range(4)}
            for i in range(4) if (dep_tier == i).any()
        },
    }
    return out, r


CORE_Q = ("tobacco", "alcohol", "betel", "hpv", "systemic", "family")


def worst_profiles(P, r, dep_score, which: str, top: int = 12):
    """Highest-probability misclassified profiles, one per distinct combination
    of the core exposures, preferring the simplest profile in each group."""
    p = r["p_under"] if which == "under" else r["p_over"]
    cand = np.where(p >= 0.05)[0]
    if len(cand) == 0:
        return []
    nonzero = (P[cand] != 0).sum(axis=1)  # crude 'how many answers moved off the first option'
    order = cand[np.lexsort((nonzero, -np.round(p[cand], 2)))]
    seen, rows = set(), []
    for i in order:
        core = tuple(int(P[i, QID[q]]) for q in CORE_Q)
        if core in seen:
            continue
        seen.add(core)
        rows.append({
            "profile": describe(P[i]),
            "deployed_score": int(dep_score[i]),
            "deployed_tier": TIERS[r["dep_tier"][i]],
            "p_under_pct": float(100 * r["p_under"][i]),
            "p_over_pct": float(100 * r["p_over"][i]),
            "tier_probs_pct": {t: float(100 * r["pt"][i, j]) for j, t in enumerate(TIERS)},
        })
        if len(rows) >= top:
            break
    return rows


def by_score(P, r, dep_score):
    out = []
    for sc in np.unique(dep_score):
        m = dep_score == sc
        out.append({"score": int(sc), "tier": TIERS[tier_of(np.array([sc]))[0]], "n_profiles": int(m.sum()),
                    "share_pct": float(100 * m.mean()),
                    "stable_pct": float(100 * r["stable"][m].mean()),
                    "under_mean_pct": float(100 * r["p_under"][m].mean()),
                    "over_mean_pct": float(100 * r["p_over"][m].mean())})
    return out


def answer_enrichment(P, r, which="under", top=12):
    """Which answers are over-represented in the misclassification mass.
    ratio = share of misclassification mass carried by profiles with this answer,
    divided by the answer's share of the profile space."""
    p = r["p_under"] if which == "under" else r["p_over"]
    total = p.sum()
    rows = []
    for q, _ in QUESTIONS:
        col = P[:, QID[q]]
        for j, o in enumerate(OPTS[q]):
            m = col == j
            if not m.any() or m.all():
                continue
            share = p[m].sum() / total if total > 0 else 0.0
            rows.append({"answer": f"{q}={o}", "mass_share_pct": float(100 * share),
                         "space_share_pct": float(100 * m.mean()), "ratio": float(share / m.mean())})
    rows.sort(key=lambda x: -x["ratio"])
    return rows[:top]


def boundary_shift_table(P, cum, dep_score, shifts=(-2, -1, 0, 1, 2)):
    """Effect of moving one boundary at a time. Deployed tiers are recomputed on
    the shifted boundaries too, so this measures stability of the instrument as
    it would then be, not agreement with today's tiers."""
    rows = []
    for bi, name in enumerate(("low/moderate", "moderate/elevated", "elevated/high")):
        for s in shifts:
            b = list(BOUNDARIES)
            b[bi] += s
            if not (b[0] < b[1] < b[2]):
                continue
            summ, r = summarise(P, cum, dep_score, tuple(b))
            rows.append({
                "boundary": name, "shift": s, "boundaries": b,
                "stable_pct": summ["stable_pct"],
                "under_mean_pct": summ["under_called"]["mean_prob_pct"],
                "under_ge5_pct": summ["under_called"]["profiles_with_p_ge_5pct"],
                "over_mean_pct": summ["over_called"]["mean_prob_pct"],
                "straddle_pct": summ["boundary_instability"][name]["profiles_straddling_pct"],
            })
    return rows


def profile_index(P, **answers) -> int:
    row = np.zeros(P.shape[1], dtype=np.int8)
    for q, _ in QUESTIONS:
        row[QID[q]] = OIDX[q][answers[q]]
    hit = np.where((P == row).all(axis=1))[0]
    if len(hit) == 0:
        raise ValueError(f"profile not in enumerated space: {answers}")
    return int(hit[0])


NAMED_PROFILES = {
    "young_hpv_history": dict(
        age="under35", sex="female", tobacco="never", alcohol="never", betel="never",
        hpv="history", sun="minimal", symptom="no", family="no", systemic="no",
        diet="daily", dental="recent"),
    "betel_tobacco_alcohol": dict(
        age="under35", sex="female", tobacco="daily", alcohol="daily", betel="current",
        hpv="vaccinated", sun="minimal", symptom="no", family="no", systemic="no",
        diet="daily", dental="recent"),
}


def named_profile_report(P, hist, dep_score, r):
    out = {}
    for name, ans in NAMED_PROFILES.items():
        try:
            i = profile_index(P, **ans)
        except ValueError:
            continue  # not in a restricted space
        h = hist[i].astype(np.float64)
        n = h.sum()
        cum = np.cumsum(h) / n
        scores = np.arange(NS)
        pct = {q: int(scores[np.searchsorted(cum, q / 100)]) for q in (2.5, 25, 50, 75, 97.5)}
        out[name] = {
            "description": describe(P[i]),
            "deployed_score": int(dep_score[i]),
            "deployed_tier": TIERS[r["dep_tier"][i]],
            "score_percentiles": pct,
            "tier_probs_pct": {t: float(100 * r["pt"][i, j]) for j, t in enumerate(TIERS)},
            "p_under_pct": float(100 * r["p_under"][i]),
            "p_over_pct": float(100 * r["p_over"][i]),
        }
    return out


def stratified(P, r, by: str):
    """Stability and under-call by one question's answer."""
    out = {}
    col = P[:, QID[by]]
    for j, o in enumerate(OPTS[by]):
        m = col == j
        if not m.any():
            continue
        out[o] = {
            "stable_pct": float(100 * r["stable"][m].mean()),
            "under_mean_pct": float(100 * r["p_under"][m].mean()),
            "over_mean_pct": float(100 * r["p_over"][m].mean()),
        }
    return out


# ----------------------------------------------------------------------------
# Reporting
# ----------------------------------------------------------------------------


def or_table(src: dict[tuple, OR]) -> list[dict]:
    rows = []
    for key, o in src.items():
        if key == ("interaction",):
            w = INTERACTION_BONUS
            label = "tobacco x alcohol bonus"
        else:
            w = DEPLOYED[key[0]][key[1]]
            label = f"{key[0]}={key[1]}"
        rows.append({
            "factor": label,
            "deployed_weight": w,
            "implied_or": round(implied_or(w), 2),
            "published_or": o.point, "ci_lo": o.lo, "ci_hi": o.hi,
            "weight_at_published_point": int(js_round(math.log(o.point) * K_DEPLOYED)),
            "weight_range_over_ci": [int(js_round(math.log(o.lo) * K_DEPLOYED)), int(js_round(math.log(o.hi) * K_DEPLOYED))],
            "implied_or_inside_ci": bool(o.lo <= implied_or(w) <= o.hi),
            "site": o.site, "source": o.source, "note": o.note,
        })
    return rows


def fmt_pct(x):
    return f"{x:5.1f}%"


def print_report(args, src, summ, r, P, hist, cum, dep_score, k):
    print("=" * 78)
    print(f"OralCheck sensitivity analysis   mode={args.mode}  centre={args.centre}  "
          f"alcohol-map={args.alcohol_map}  hpv={args.hpv}  draws={args.draws}  seed={args.seed}")
    print("=" * 78)
    print(f"profiles scored: {summ['n_profiles']:,}   (symptom=yes"
          f"{' and unsure' if not args.score_unsure_symptom else ''} excluded: forced high)")
    if args.mode == "floating":
        print(f"k under floating scale: median {np.median(k):.2f}, 95% interval "
              f"{np.percentile(k, 2.5):.2f} to {np.percentile(k, 97.5):.2f}  (deployed 4.47)")
    print()
    print("Sourced ORs vs deployed weights (k = 4.47)")
    print(f"{'factor':28s} {'w_dep':>5s} {'impl OR':>8s} {'pub OR':>7s} {'95% CI':>14s} {'w_pub':>5s} {'w over CI':>10s} in CI?")
    for row in or_table(src):
        print(f"{row['factor']:28s} {row['deployed_weight']:5d} {row['implied_or']:8.2f} {row['published_or']:7.2f} "
              f"{row['ci_lo']:6.2f}-{row['ci_hi']:<6.2f} {row['weight_at_published_point']:5d} "
              f"{row['weight_range_over_ci'][0]:4d}..{row['weight_range_over_ci'][1]:<4d} {'yes' if row['implied_or_inside_ci'] else 'NO'}")
    print()
    print("Deployed tier share of the profile space:",
          "  ".join(f"{t} {fmt_pct(v)}" for t, v in summ["deployed_tier_share_pct"].items()))
    print(f"Stable profiles (one tier on >=95% of draws): {fmt_pct(summ['stable_pct'])}")
    print("  by deployed tier:", "  ".join(f"{t} {fmt_pct(v)}" for t, v in summ["stable_pct_by_deployed_tier"].items() if v is not None))
    print(f"Mean probability that a profile lands in its deployed tier: {fmt_pct(summ['mean_p_deployed_tier_pct'])}")
    print()
    u, o = summ["under_called"], summ["over_called"]
    print("Direction of disagreement with the deployed tier")
    print(f"  UNDER-called (draws say higher tier than deployed reads; dangerous): mean {fmt_pct(u['mean_prob_pct'])}, "
          f"profiles with >=5%: {fmt_pct(u['profiles_with_p_ge_5pct'])}, with >=50%: {fmt_pct(u['profiles_with_p_ge_50pct'])}")
    print(f"  OVER-called  (draws say lower tier than deployed reads):            mean {fmt_pct(o['mean_prob_pct'])}, "
          f"profiles with >=5%: {fmt_pct(o['profiles_with_p_ge_5pct'])}, with >=50%: {fmt_pct(o['profiles_with_p_ge_50pct'])}")
    print()
    print("Transition matrix (rows: deployed tier; cols: mean % of draws in each tier)")
    print(f"{'':10s}" + "".join(f"{t:>10s}" for t in TIERS))
    for t, row in summ["transition_pct"].items():
        print(f"{t:10s}" + "".join(f"{row[c]:9.1f}%" for c in TIERS))
    print()
    print("Boundary instability")
    for name, v in summ["boundary_instability"].items():
        print(f"  {name:18s} profiles with >=5% of draws on each side: {fmt_pct(v['profiles_straddling_pct'])}   "
              f"mean crossing mass: {fmt_pct(v['mean_crossing_mass_pct'])}")
    print()
    print("Stratified by tobacco answer:")
    for o_, v in stratified(P, r, "tobacco").items():
        print(f"  {o_:11s} stable {fmt_pct(v['stable_pct'])}  under {fmt_pct(v['under_mean_pct'])}  over {fmt_pct(v['over_mean_pct'])}")
    print("Stratified by betel answer:")
    for o_, v in stratified(P, r, "betel").items():
        print(f"  {o_:11s} stable {fmt_pct(v['stable_pct'])}  under {fmt_pct(v['under_mean_pct'])}  over {fmt_pct(v['over_mean_pct'])}")
    print()
    print("By deployed score (where the fragility sits)")
    print(f"{'score':>5s} {'tier':9s} {'profiles':>9s} {'share':>7s} {'stable':>7s} {'under':>7s} {'over':>7s}")
    for row in by_score(P, r, dep_score):
        print(f"{row['score']:5d} {row['tier']:9s} {row['n_profiles']:9,d} {fmt_pct(row['share_pct']):>7s} {fmt_pct(row['stable_pct']):>7s} {fmt_pct(row['under_mean_pct']):>7s} {fmt_pct(row['over_mean_pct']):>7s}")
    print()
    print("Answers over-represented in the UNDER-called mass (ratio > 1 = carries more than its share)")
    for row in answer_enrichment(P, r, "under"):
        print(f"  {row['answer']:22s} carries {fmt_pct(row['mass_share_pct'])} of the mass vs {fmt_pct(row['space_share_pct'])} of the space   ratio {row['ratio']:.2f}")
    print("Answers over-represented in the OVER-called mass")
    for row in answer_enrichment(P, r, "over"):
        print(f"  {row['answer']:22s} carries {fmt_pct(row['mass_share_pct'])} of the mass vs {fmt_pct(row['space_share_pct'])} of the space   ratio {row['ratio']:.2f}")
    print()
    print("Named profiles")
    for name, v in named_profile_report(P, hist, dep_score, r).items():
        print(f"  {name}: {v['description']}")
        print(f"    deployed score {v['deployed_score']} ({v['deployed_tier']}); score percentiles 2.5/25/50/75/97.5: "
              + "/".join(str(v['score_percentiles'][q]) for q in (2.5, 25, 50, 75, 97.5)))
        print("    tier probabilities: " + "  ".join(f"{t} {fmt_pct(p)}" for t, p in v["tier_probs_pct"].items()))
        print(f"    under-called {fmt_pct(v['p_under_pct'])}   over-called {fmt_pct(v['p_over_pct'])}")
    print()
    print("Profiles most at risk of being UNDER-called (deployed tier below what the draws support)")
    for row in worst_profiles(P, r, dep_score, "under", args.top):
        tp = row["tier_probs_pct"]
        print(f"  {row['p_under_pct']:5.1f}%  score {row['deployed_score']:2d} {row['deployed_tier']:9s} "
              f"[L {tp['low']:.0f} M {tp['moderate']:.0f} E {tp['elevated']:.0f} H {tp['high']:.0f}]  {row['profile']}")
    print("Profiles most at risk of being OVER-called")
    for row in worst_profiles(P, r, dep_score, "over", args.top):
        tp = row["tier_probs_pct"]
        print(f"  {row['p_over_pct']:5.1f}%  score {row['deployed_score']:2d} {row['deployed_tier']:9s} "
              f"[L {tp['low']:.0f} M {tp['moderate']:.0f} E {tp['elevated']:.0f} H {tp['high']:.0f}]  {row['profile']}")
    print()
    print("Boundary shifts (one boundary at a time; deployed tiers recomputed on the shifted boundaries)")
    print(f"{'boundary':18s} {'shift':>5s} {'bounds':>12s} {'stable':>8s} {'under mean':>11s} {'under>=5%':>10s} {'over mean':>10s} {'straddle':>9s}")
    for row in boundary_shift_table(P, cum, dep_score):
        print(f"{row['boundary']:18s} {row['shift']:+5d} {str(row['boundaries']):>12s} {fmt_pct(row['stable_pct']):>8s} "
              f"{fmt_pct(row['under_mean_pct']):>11s} {fmt_pct(row['under_ge5_pct']):>10s} {fmt_pct(row['over_mean_pct']):>10s} {fmt_pct(row['straddle_pct']):>9s}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mode", choices=("fixed", "floating"), default="fixed")
    ap.add_argument("--centre", choices=("published", "deployed"), default="published",
                    help="centre each log-OR on the published point (default) or on the deployed weight's implied OR with the published CI width (diagnostic only)")
    ap.add_argument("--alcohol-map", choices=tuple(ALCOHOL_MAPS), default="quantity")
    ap.add_argument("--hpv", choices=tuple(HPV_SCENARIOS), default="deployed")
    ap.add_argument("--draws", type=int, default=10000)
    ap.add_argument("--seed", type=int, default=20260914)
    ap.add_argument("--score-unsure-symptom", action="store_true",
                    help="score symptom=unsure as a 3-point answer (written spec) instead of forcing high (deployed engine)")
    ap.add_argument("--restrict", default="",
                    help="restrict the enumerated space, e.g. 'betel=never,hpv=vaccinated|neither|unknown'")
    ap.add_argument("--top", type=int, default=12)
    ap.add_argument("--json", help="write full summary as JSON")
    ap.add_argument("--csv", help="write per-profile results as CSV")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    rng = np.random.default_rng(args.seed)
    src = build_sources(args.alcohol_map, args.hpv)
    _ACTIVE_SOURCES.clear(); _ACTIVE_SOURCES.update(src)
    restrict = {kv.split('=')[0]: kv.split('=')[1].split('|') for kv in args.restrict.split(',') if kv}
    P = enumerate_profiles(args.score_unsure_symptom, restrict)
    dep_score = deployed_scores(P)
    W, bonus, k = draw_weight_tables(src, args.draws, args.mode, args.centre, rng)
    if not args.quiet:
        print(f"enumerated {len(P):,} profiles; drawing {args.draws:,} weight tables ({args.mode} scale)", file=sys.stderr)
    hist = propagate(P, W, bonus, verbose=not args.quiet)
    cum = cumulative(hist)
    summ, r = summarise(P, cum, dep_score)
    print_report(args, src, summ, r, P, hist, cum, dep_score, k)

    if args.json:
        blob = {
            "config": vars(args),
            "k_summary": {"median": float(np.median(k)), "p2.5": float(np.percentile(k, 2.5)), "p97.5": float(np.percentile(k, 97.5))},
            "or_table": or_table(src),
            "point_weights_k447": point_weight_table(src, K_DEPLOYED),
            "point_weights_floating_k": point_weight_table(src, ANCHOR_WEIGHT / math.log(src[("tobacco", "daily")].point)),
            "summary": summ,
            "by_tobacco": stratified(P, r, "tobacco"),
            "by_betel": stratified(P, r, "betel"),
            "by_hpv": stratified(P, r, "hpv"),
            "named_profiles": named_profile_report(P, hist, dep_score, r),
            "worst_under": worst_profiles(P, r, dep_score, "under", args.top),
            "worst_over": worst_profiles(P, r, dep_score, "over", args.top),
            "by_score": by_score(P, r, dep_score),
            "enrichment_under": answer_enrichment(P, r, "under"),
            "enrichment_over": answer_enrichment(P, r, "over"),
            "boundary_shifts": boundary_shift_table(P, cum, dep_score),
        }
        with open(args.json, "w") as f:
            json.dump(blob, f, indent=1)
    if args.csv:
        import csv
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow([q for q, _ in QUESTIONS] + ["deployed_score", "deployed_tier", "p_low", "p_moderate", "p_elevated", "p_high", "p_under", "p_over", "stable"])
            for i in range(len(P)):
                w.writerow([OPTS[q][P[i, QID[q]]] for q, _ in QUESTIONS]
                           + [int(dep_score[i]), TIERS[r["dep_tier"][i]]]
                           + [f"{x:.4f}" for x in r["pt"][i]]
                           + [f"{r['p_under'][i]:.4f}", f"{r['p_over'][i]:.4f}", int(r["stable"][i])])


if __name__ == "__main__":
    main()
