# OralCheck — ADA Science Director Briefing

**For:** Jorge Rojas, ADA Science Director  
**Prepared by:** Ian Harris, OralCheck  
**Updated:** June 2026

---

## 1. What OralCheck Is

OralCheck (oralcheck.org) is a free, private, browser-based oral cancer risk screener. Ten questions, about two minutes, no account required. Answers never leave the device. The output is a risk tier and a plain-English summary of which factors are driving the score, with next steps calibrated to that tier.

The premise: oral cancer has an 84% five-year survival rate when caught at Stage I, but most cases are not diagnosed until Stage III or IV, where survival drops to around 38%. That gap is not a biology problem. It is a detection timing problem. OralCheck exists to move people toward a dental visit earlier, before symptoms become obvious.

---

## 2. The Science: How the Scoring Works

### Weight Derivation

Each risk factor is assigned a weight proportional to the natural log of its published odds ratio (OR), scaled by a constant k:

**weight = round( ln(OR) x k )**

The scaling constant k = 4.47 was chosen so that daily tobacco use (OR 6.0x per Gandini et al., 2008) maps to a weight of 8. This anchors all other weights to a consistent log-linear scale derived from the same evidence base.

A log-linear model was chosen deliberately: it means that the sum of weights approximates the log of the combined odds ratio, which is the standard approach in epidemiological risk scoring (the Framingham Heart Score uses the same structure). Under this model, purely multiplicative risks are correctly captured without a separate interaction term. The tobacco-alcohol interaction term (below) accounts for the supra-multiplicative effect observed in the literature.

### Risk Factor Table

| Factor | Published OR | Weight | Source |
|---|---|---|---|
| Tobacco, daily | 2.5 to 6.0x | 8 | Gandini et al., Oral Oncology, 2008 |
| Betel quid / paan / gutka, current | 7 to 10x | 9 | IARC Monograph 85, 2004 |
| Tobacco, occasional | ~3.0x | 5 | Gandini et al., Oral Oncology, 2008 |
| Alcohol, daily | ~3.0x | 5 | Bagnardi et al., Annals of Oncology, 2015 |
| HPV-related condition (history) | 3 to 5x blended | 5 | Gillison et al., JAMA, 2008 |
| Age 65+ | ~4.0x adjusted | 6 | NCI SEER, multivariable-adjusted |
| Age 55 to 64 | ~2.5x | 4 | NCI SEER |
| Betel quid, past use | ~2.5x | 4 | IARC Monograph 85, 2004 |
| Alcohol, weekly | ~2.0x | 3 | Bagnardi et al., Annals of Oncology, 2015 |
| Family history, first-degree | ~2.0x | 3 | Negri et al., Int J Cancer, 2009 |
| Diet low in fruits and vegetables | ~2.0x | 3 | Pavia et al., Oral Oncology, 2006 |
| Age 35 to 54 | ~1.5x | 2 | NCI SEER |
| Tobacco, former | ~1.5x | 2 | Gandini et al., Oral Oncology, 2008 |
| HPV, unvaccinated / no known history | ~1.5x proxy | 2 | D'Souza et al., NEJM, 2007; population exposure estimate |
| Sun exposure, lips unprotected | 2 to 3x | 2 | Perea-Milla Lopez et al., Br J Cancer, 2003 |

**HPV scoring note:** The screener asks about HPV in three tiers: vaccinated (0 pts), unvaccinated with no known history (2 pts), and prior HPV-related condition (5 pts). The 5-point tier uses Gillison et al., 2008 as its basis, blended conservatively across oral cavity and oropharyngeal sites. The 2-point tier for unvaccinated status is a behavioral proxy for elevated HPV-16 exposure probability, not a serostatus measure, and is cited accordingly. The distinction between oral cavity cancer (tobacco-dominant) and oropharyngeal cancer (HPV-dominant) is acknowledged in the limitations section.

**Symptom override:** Any persistent symptom lasting 2+ weeks (red or white patch, non-healing ulcer, unexplained lump, difficulty swallowing) overrides the total score and triggers the highest tier regardless of points accumulated. These represent possible in-situ pathology rather than population-level risk exposures and are treated as clinical flags, not additive weights.

### Tobacco + Alcohol Interaction Term

When both tobacco and alcohol use are present at meaningful levels, the model adds an interaction bonus of +3 points.

Under a purely log-linear (multiplicative) model, tobacco OR 6x and alcohol OR 3x would combine to approximately 18x, mapping to 13 points. The published combined OR for heavy users of both is approximately 35x (Hashibe et al., INHANCE Consortium, 2009), which maps to approximately 16 points under the same formula. The +3 interaction bonus closes that gap. Without it, the model underestimates the risk for the highest-risk behavioral profile.

### Risk Tier Thresholds

| Tier | Score | Interpretation |
|---|---|---|
| Low | 0 to 4 | Below average population risk; routine dental care |
| Moderate | 5 to 13 | Elevated but common risk profile; mention to dentist |
| Elevated | 14 to 22 | Multiple compounding risk factors; schedule a dental screening |
| High | 23+ | Significant risk burden; dental evaluation recommended soon |

A daily smoker scores 8 (Moderate). Tobacco + alcohol + interaction = 16 (Elevated). Betel + tobacco + alcohol + interaction = 26+ (High).

---

## 3. Primary Sources

1. Gandini S, et al. Tobacco smoking and cancer: a meta-analysis. Oral Oncology. 2008;44(7):617-638.
2. Bagnardi V, et al. Alcohol consumption and site-specific cancer risk: a comprehensive dose-response meta-analysis. Annals of Oncology. 2015;26(1):39-55.
3. Gillison ML, et al. Distinct risk factor profiles for HPV type 16-positive and -negative head and neck cancers. JAMA. 2008;168(3):294-305.
4. IARC. Betel-quid and Areca-nut Chewing and Some Areca-nut Derived Nitrosamines. IARC Monograph 85. 2004.
5. Hashibe M, Brennan P, Chuang SC, et al. Interaction between tobacco and alcohol use and the risk of head and neck cancer: pooled analysis in the INHANCE Consortium. Cancer Epidemiology, Biomarkers & Prevention. 2009;18(2):541-550.
6. Negri E, Boffetta P, Berthiller J, et al. Family history of cancer: pooled analysis in the INHANCE Consortium. International Journal of Cancer. 2009;124(2):394-401.
7. D'Souza G, Kreimer AR, Viscidi R, et al. Case-control study of human papillomavirus and oropharyngeal cancer. New England Journal of Medicine. 2007;356(19):1944-1956.
8. Perea-Milla Lopez E, et al. Lifestyles, environmental and phenotypic factors associated with lip cancer. British Journal of Cancer. 2003;88(11):1702-1707.
9. Pavia M, et al. Evidence-based medicine on the relationship between diet and cancers of the oral cavity and pharynx. Oral Oncology. 2006;42(1):15-25.
10. National Cancer Institute. SEER Cancer Statistics Review 1975-2021.
11. American Cancer Society. Key Statistics for Oral Cavity and Oropharyngeal Cancers. 2024.
12. Napier SS, Speight PM. Natural history of potentially malignant oral lesions. Journal of Oral Pathology & Medicine. 2008;37(1):1-10.

---

## 4. Limitations: What This Tool Is and Is Not

These limitations are stated up front, not buried, because the distinction matters.

**OralCheck is an evidence-informed public health awareness tool. It is not a clinical diagnostic instrument.**

Specifically:

1. **Not validated against a clinical outcome dataset.** The weights are grounded in published literature, but they have not been calibrated against a prospective cohort. There is no sensitivity, specificity, or AUC data. The tier thresholds are working clinical estimates, not empirically derived cutoffs. This is the most significant limitation.

2. **Oral cavity and oropharyngeal cancer are treated as a single entity.** These are biologically distinct diseases with different dominant etiologies: tobacco and alcohol drive oral cavity cancer; HPV-16 drives oropharyngeal cancer. A unified score is a meaningful simplification.

3. **Biological sex is not captured.** Men have approximately 2x the incidence of oral cancer compared to women. This affects calibration for female users.

4. **Immunosuppression is not asked about.** HIV, organ transplant recipients on immunosuppressive therapy, and long-term corticosteroid users face significantly elevated oral cancer risk. This is a gap.

5. **Self-reported data.** Tobacco and alcohol use are commonly under-reported.

6. **Dental visit frequency is a detection-delay proxy, not a causal risk factor.** Its weight is grounded in clinical rationale (dentists are the primary oral cancer screeners) rather than a direct epidemiological OR.

**Why stating this clearly is the right move:** A tool that overclaims its validation is a liability. A tool that is transparent about its limits and accurate within them is trustworthy. The goal of OralCheck is not to diagnose cancer. The goal is to move people from "I haven't thought about this" to "I am going to bring this up at my next dental visit." That goal does not require clinical validation. It requires accuracy about what the tool is for.

Validation against a clinical dataset is, in fact, exactly the kind of collaboration that a scientific partnership with the ADA could enable.

---

## 5. How the Website Works

Five sections:

- **Homepage:** Explains the problem and puts the screener one click away.
- **Screener:** Ten questions, one at a time, phone-optimized. Answers run entirely in the browser, no server, no storage.
- **Results:** Risk tier, ranked list of contributing factors, plain-English next steps calibrated to the tier. Symptoms trigger an immediate "book this week" message, not a someday suggestion.
- **Learn:** Eight evidence-based articles covering warning signs, self-exam, HPV and oral cancer, risk factors, prevention, what oral cancer is, statistics, and canker sore vs. oral cancer.
- **Find Care:** Real dental clinics, community health centers, dental schools, and HRSA-funded free clinics near the user.
- **For Clinicians:** A customizable, printable waiting room flyer. No login, no vendor relationship, no cost.

---

## 6. How the ADA Could Help

**1. Scientific review and feedback**

The Science Director or a designated reviewer could assess the weighting model and either flag methodological concerns or note that it is consistent with the published evidence base. Even informal feedback would materially improve the tool and carry credibility in every subsequent partnership conversation.

This would also be a natural first step toward the validation collaboration described above.

**2. Distribution to member dentists**

The ADA has 160,000+ member dentists. An appearance in ADA News, member communications, or the Morning Huddle newsletter would reach more waiting rooms in one week than any other available channel. The Wisconsin Dental Association featured OralCheck in their member newsletter (The Drill) in April 2026, which produced the largest single traffic spike in the site's history.

**3. ADA patient education materials**

A mention or link on ADA.org's patient-facing oral cancer awareness content would drive organic traffic from exactly the right audience.

**4. Find-a-Dentist integration**

When a user scores Elevated or High, they need to book a visit. An ADA relationship could enable an "Find an ADA member dentist near you" call-to-action on the results page.

**5. April Oral Cancer Awareness Month**

Co-promoting OralCheck during the April awareness campaign costs the ADA nothing and gives the campaign a free, interactive tool to point patients to.

---

## 7. Other Key Facts

- No PHI collected. No HIPAA exposure for any practice that shares the link.
- No commercial agenda. No paid tier, no data monetization, no sponsorship lock-in.
- Built by a predental student at UW-Madison, not a company.
- Already reaching users across 13 countries with no paid promotion.
- The survival rate gap is the core argument: 84% at Stage I, 38% at Stage IV. The tool exists to close that gap by getting people to a dental chair earlier.
- oralcheck.org/for-clinicians has the printable flyer. Any dentist leaving the meeting can customize and print it in under two minutes.
