/**
 * Every SEER-derived headline figure the site quotes, in one place.
 *
 * These used to be typed out separately in nine files, and they drifted. The
 * site simultaneously claimed late-stage survival was 38% (results page), 40%
 * (facts and overview pages), and "around 67 percent" for regional disease (a
 * published article), all from a SEER release that had since been superseded
 * twice. Anything on the site that quotes SEER should read from here.
 *
 * The message catalogues can't import this, since they're JSON and translated,
 * so `messages/*.json` still carries its own copies of these numbers in prose.
 * When a figure here changes, grep the catalogues for the old one too.
 *
 * Source: NCI SEER Cancer Stat Facts: Oral Cavity and Pharynx Cancer.
 */
export const SEER = {
  source: "https://seer.cancer.gov/statfacts/html/oralcav.html",
  /** Date the numbers below were last read off the SEER page. */
  lastVerified: "2026-08-30",

  /** Estimated for 2026. */
  newCasesPerYear: 60_480,
  /** Estimated for 2026. */
  deathsPerYear: 13_150,

  /**
   * Five-year relative survival by SEER *summary* stage, 2016–2022.
   *
   * Summary stage is localized / regional / distant, which is not the same
   * thing as AJCC Stage I–IV. The site used to present these figures as
   * "Stage I" and "Stage IV" survival, which attributed one staging system's
   * numbers to another. Copy should say localized and distant, or plainly
   * "before it spreads" and "once it has spread".
   */
  survival: {
    localized: 88.7,
    regional: 69.7,
    distant: 36.0,
    overall: 69.9,
  },

  /** Share of cases diagnosed at each summary stage, 2016–2022. */
  stageShare: { localized: 26, regional: 55, distant: 12, unknown: 6 },

  /** Age-adjusted incidence per 100,000 per year, 2019–2023. */
  incidencePer100k: { male: 17.5, female: 6.6 },

  /** 2019–2023. */
  medianAgeAtDiagnosis: 65,

  /**
   * Share of new cases by age at diagnosis, SEER 21, 2019–2023, from the same
   * Stat Facts page. These are SEER's own bands, which are not decades
   * (20–34, then 35–44 and so on); do not relabel them as "your 20s".
   */
  newCaseShareByAge: {
    under20: 0.4,
    "20-34": 1.7,
    "35-44": 3.9,
    "45-54": 12.6,
    "55-64": 29.0,
    "65-74": 30.3,
    "75-84": 16.3,
    over84: 5.8,
  },
} as const;

/**
 * Age-specific incidence: new cases per 100,000 people in each five-year age
 * group, per year. Both sexes, all races, delay-adjusted, SEER 21, 2019–2023
 * (November 2025 submission), read off SEER*Explorer's "Rates by Age" table.
 *
 * Kept in five-year groups because that is how SEER publishes them. Two
 * adjacent groups cannot be merged into a decade by averaging their rates;
 * that needs each group's population, which this table does not give.
 */
export const SEER_BY_AGE = {
  source:
    "https://seer.cancer.gov/statistics-network/explorer/application.html?site=3&data_type=1&graph_type=3&compareBy=sex&chk_sex_1=1&rate_type=2&race=1",
  lastVerified: "2026-10-26",
  ratePer100k: {
    "15-19": 0.4,
    "20-24": 0.6,
    "25-29": 1.1,
    "30-34": 1.8,
    "35-39": 3.0,
    "40-44": 5.5,
    "45-49": 10.2,
    "50-54": 18.8,
    "55-59": 29.0,
    "60-64": 38.6,
    "65-69": 45.3,
    "70-74": 49.0,
    "75-79": 50.9,
    "80-84": 51.6,
    "85-89": 49.8,
    "90+": 46.6,
  },
} as const;

/**
 * Rounded forms for display. Headline numbers read better rounded, but the
 * rounding happens here rather than being typed by hand at each call site, so
 * a corrected source figure can't leave a stale rounded copy behind.
 */
export const SEER_DISPLAY = {
  newCases: SEER.newCasesPerYear.toLocaleString("en-US"),
  deaths: SEER.deathsPerYear.toLocaleString("en-US"),
  survivalLocalized: `${Math.round(SEER.survival.localized)}%`,
  survivalDistant: `${Math.round(SEER.survival.distant)}%`,
  /**
   * How much more often men are diagnosed, from the incidence rates.
   *
   * The exact quotient is 2.65, and copy rounds it *down* to 2.6 rather than up
   * to 2.7. Deliberate: the screener already scores tobacco and alcohol, which
   * account for part of the male excess, so every statement of this ratio on
   * the site errs low. It also keeps the number identical to the one on
   * /methods and in the sex question, which derive the weight from a
   * conservative OR of 2.0 for the same reason.
   */
  maleRatio: `${(Math.floor((SEER.incidencePer100k.male / SEER.incidencePer100k.female) * 10) / 10).toFixed(1)}×`,
} as const;

/**
 * "About one death every N minutes", derived rather than written down, since
 * the previous hard-coded interval (50 minutes) silently stopped matching the
 * death count printed directly beside it.
 */
export const minutesBetweenDeaths = Math.round(
  (365 * 24 * 60) / SEER.deathsPerYear,
);
