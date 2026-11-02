# OralCheck: a free, private oral cancer risk questionnaire with weights drawn mainly from published odds ratios

**Ian Harris**, OralCheck (independent project). Contact: [email]

## Abstract

**Background.** An estimated 60,480 US cases of oral cavity and pharynx cancer, and 13,150 deaths, are projected for 2026. Five-year relative survival is 88.7% while localized and 36.0% once spread to distant sites, yet only 26% of cases are diagnosed while localized. A dental examination finds them earlier, but people unaware of their risk rarely ask.

**Methods.** OralCheck (oralcheck.org) is a free web questionnaire that ranks self-reported risk and directs users to a dentist. Twelve questions cover established risk factors, dental-visit recency and current symptoms. Most weights equal round(ln(OR) × 4.47), chosen so daily tobacco (OR 6.0) scores 8; four depart from this formula by stated judgment, and three items are not derived from odds ratios. A 3-point term models the tobacco and alcohol interaction. Tier cutoffs were set by judgment. A board-certified oral and maxillofacial pathologist (August 2026) and a head-and-neck surgeon (September 2026) reviewed the method.

**Results.** Scores span 0 to 61, in four tiers: Low (0 to 4), Moderate (5 to 13), Elevated (14 to 22), High (23 or more). Male sex alone scores 3 (Low); daily smoking, 8 (Moderate); tobacco plus alcohol with interaction, 16 (Elevated); adding betel quid, 25 (High). Any current or possible symptom returns the top result. Review added an immune and radiation question and stated limitations. It runs in English, Spanish and Portuguese, in the browser, and stores no answers.

**Conclusions.** Transparent, literature-derived weighting can yield an accessible risk-awareness tool. It has not been validated; that requires outcome data and biostatistical support.

*Word count (Background through Conclusions, including section labels): 250.*

## Plain-language summary

OralCheck is a free, two-minute website that asks 12 questions about known oral cancer risk factors and suggests whether to raise them with a dentist; it does not diagnose cancer. This poster explains how each answer is scored from published research, where the scoring relies on judgment instead, and what testing it still needs.

## Notes for Ian before submitting

- Replace `[email]` in the author line, here and on the poster.
- The epidemiology figures are SEER Cancer Stat Facts, read 30 August 2026 (`src/lib/seerStats.ts`). Survival is by SEER summary stage, not AJCC stage.
- Reviewers are deliberately unnamed. Do not add names, institutions or quotes until each has agreed in writing.
