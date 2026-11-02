# OralCheck: AI give-aways and repetition audit

Audited 2026-10-30. Read-only. Covers every string in `messages/en.json`, all 12 articles in `content/published/`, the page and component source, and the live site (all 32 sitemap URLs, `/results` reached by clicking through `/screener`, plus `/es`, `/es/learn/signs`, `/es/learn/oral-cancer-symptoms`, `/es/about`, `/pt`, `/pt/about`). Analytics were blocked and `oralcheck:notrack` set in every browser context. The one live results run called `/api/summary` once.

Scripts and raw data: `ui-audit/ngrams.py` (repeated n-grams), `ui-audit/counts.py` (tell-phrase counts), `ui-audit/crawl.py`, `ui-audit/crawl_es.py`, `ui-audit/crawl.json`. Screenshots: `ui-audit/shots-ai/`.

## Checklist used (sources)

- Wikipedia, [Signs of AI writing](https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing): AI vocabulary clusters ("crucial", "pivotal", "valuable", "enhance"), negative parallelisms ("not just X, it's Y", "not X but Y"), rule of three, title-case headings, too much bold, inline-header lists, summary or "Conclusion" sections, vague attribution ("research shows", "experts say", "some studies"), didactic disclaimers ("it is important to note"), "key takeaways" framing, placeholder URLs, and an abrupt change of style. The guide now lists em-dash overuse as a historical tell (2022 to September 2026). Mechanically removing em dashes leaves its own mark, covered in finding 4.
- Google Search Central, [Creating helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content): the "Who, How, Why" test. It should be obvious who wrote a page, readers should be told when automation or AI was used, and trust carries the most weight. Health is YMYL (your money or your life), where these signals count more ([Search Engine Roundtable](https://www.seroundtable.com/google-helpful-content-guidance-pages-experience-changes-35258.html), [Search Engine Journal](https://www.searchenginejournal.com/can-you-use-ai-to-write-for-ymyl/558945/)).
- Design write-ups on "AI slop": [Capital and Compute, "How to fix AI slop in web design, tell by tell"](https://capitalandcompute.net/blog/fix-ai-slop-design/), [DEV, "Why every AI-built website looks the same"](https://dev.to/alanwest/why-every-ai-built-website-looks-the-same-blame-tailwinds-indigo-500-3h2p), [Built In, "AI makes bad design look good enough"](https://builtin.com/articles/ai-design-slop-era). The tells they share: a stock section order (hero, logo row, three feature cards, CTA band), identical cards, count-up stat tiles, tracked all-caps eyebrows, "A · B · C" meta strings, monospace micro-labels, an arrow on every link, one accent-coloured word in the headline, 01/02/03 numbering on things that are not a sequence, slogans like "Elevate your X", and invented or vague metrics.

The site avoids the loudest first-wave tells: there is no purple gradient, gradient text, sparkle icon or emoji bullet. Its tells are the second-wave ones, plus a lot of repeated copy.

---

## The 5 biggest give-aways

### 1. The privacy promise is contradicted by an undisclosed AI-written results paragraph

The site says, in at least 8 places, that answers never leave the device:

- "Nothing is saved or sent anywhere." (`en.json:71`, home card, and `:1240` on the flyer)
- "Answers never leave the patient's device. No HIPAA concerns, no data liability." (`en.json:1161`, /for-clinicians)
- "Your answers stay on your device." (`:1549`, `:1787`, `:2060`)

On the results page, the tier, every factor label and every answer label (for example "HPV exposure: Have had an HPV-related condition") are POSTed to `/api/summary` (`src/app/[locale]/results/page.tsx:106`). That endpoint sends them to Claude Haiku (`src/app/api/summary/route.ts:93-104`), and the reply replaces the site's own summary, presented in the site's voice. The only hint is "Personalizing your summary…". The privacy page (`en.json:1289`) never mentions it. The owner's guide (Q9) tells Ian to answer "nothing is transmitted", which is not true.

The live paragraph I got reads as generated: "significantly multiplies your oral cancer risk… directly impacts survival outcomes, making early detection critical in your case. Contact a dentist or oral surgeon within the next few days." That last sentence contradicts the "this week" in the banner and the next-steps card on the same screen. It also asserted an unsourced claim ("People with both tobacco and alcohol exposure are diagnosed at more advanced stages more often") that no human reviewed.

**Why it costs trust:** this is the one promise the whole tool rests on, and anyone who opens the network tab, or any clinician Ian pitches, can see it is false. It also fails Google's "How" test, which asks a site to tell readers when AI wrote the content.

**Fix (recommended):** remove the AI summary. The deterministic summaries in `RiskEngine.summary` are already good, they are reviewed, and they are translated. Removing it also removes the inconsistency and the cost.

**Fix (if it stays):** label it, and stop making the absolute claim.
- Under the paragraph, add: "This paragraph was written by an AI model (Claude) from the factors listed below. Your answers are not stored."
- Home card: "Short, specific questions based on published risk factors. Your answers are not stored."
- For clinicians: "No answers are stored and nothing identifies the patient."
- Privacy, new section "The results summary": "To write the short summary on your results page, your risk tier and the answer labels are sent to Anthropic's Claude model. They are not linked to you and OralCheck does not store them. If you ask to email your result, your email address is used once to send it."
- Update OWNERS_GUIDE Q9 to match.

### 2. The articles read as machine-written SEO, and they are

All 12 articles in `content/published/` come from `seo_pipeline.py` (OWNERS_GUIDE:967). They are keyword-driven and carry no author and no disclosure. The template is visible from article to article:

| Pattern | Count |
|---|---|
| Opens with "Most people…" | 7 of 12 (`symptoms`, `early-signs`, `self-exam`, `mouth-sore`, `lip`, `screening`, `young-adults`) |
| Meta intro: "This article focuses / breaks down / walks through / is about…" | 7 of 12 |
| "It takes (only) a few minutes" in the closing CTA | 12 of 12 |
| Closer "It is not a diagnostic tool, but it is a practical / useful / reasonable starting point" (variants) | 8 of 12 |
| Final H2 is a CTA ("Take the Free Screener at OralCheck", "Take the Next Step", "Take a Few Minutes to Understand Your Own Risk") | 7 of 12, plus a literal `## Conclusion` (`survival-rate`) |
| Title Case H2s, a `---` rule between every section, bold inline-header paragraph lists | 12 of 12 |
| "Understanding…" sentence openers | 16 in 11 articles |
| "warrant(s)" | 18 in 11 articles |
| "significantly / substantially / dramatically / meaningfully" | 18 in 10 articles |

Kicker endings: "A white patch that will not scrape away is your mouth asking you to pay attention. The most useful thing you can do is listen." (`white-patch…:57`). "Early awareness is not about creating anxiety. It is about giving yourself the best possible chance…" (`self-exam:78`).

Placeholder links: 15 in-text links that say "see our article on X" go to `https://oralcheck.org` (the homepage). I confirmed this on the live pages (`survival-rate` 4, `oropharyngeal` 3, `tongue` 2, `lip` 2, `mouth-sore` 2, `white-patch` 1). Wikipedia lists placeholder and wrong-target URLs as a tell. One of these links points to an article that does not exist ("alcohol, tobacco, and oral cancer risk", `survival-rate`, `young-adults`).

Authorship: the hand-built Learn pages carry "Written by Ian Harris". The articles say only "Published by OralCheck", so a reader can tell two different writers are involved.

**Fix:**
- **Disclose.** Add to each article: "Drafted with AI assistance from a fixed source list, then reviewed and edited by Ian Harris on {date}." Only say "reviewed" if he did review it. If he did not, say "Drafted with AI assistance. Not yet reviewed by a clinician."
- **Merge the overlaps** (see finding M10). Six of the 12 articles cover the same ground as a Learn page.
- **Rewrite the template parts.** Cut every "Most people" opener and "This article…" sentence, and start with the fact. Example for `oral-cancer-symptoms`: "A mouth sore that has not healed in two weeks is the most common early sign of oral cancer, and it usually does not hurt." Make all headings sentence case. Delete the `---` rules. Replace the closing CTA H2 and paragraph with nothing, because the page template already adds "Check your own risk factors" (`ArticlePage.ctaHeading`), so every article currently ends with two CTAs. Delete the kicker sentences.
- **Fix the links.** Point them at real paths: `/learn/hpv`, `/learn/risk-factors`, `/learn/canker-sore-vs-oral-cancer`, `/learn/self-exam`, `/learn/signs`, `/learn/early-signs-of-oral-cancer`, `/learn/oral-cancer-screening-what-to-expect`, `/learn/what-does-oral-cancer-look-like`. Remove the one to the non-existent article.
- **Fix the pipeline.** Add these to the `seo_pipeline.py` instructions: no "Most people" or "This article" openers, no closing CTA section, sentence-case headings, no horizontal rules, internal links only to a supplied list of real slugs, and the 2-week threshold verbatim (see finding 3).

### 3. The same facts appear with different numbers, starting with the most important one

A visitor who reads two pages gets two different answers to the question that matters most: how long to wait.

| Fact | Versions on the site |
|---|---|
| **How long to wait before seeing someone** | "2 weeks": 61 times in en.json, the named "2-week rule" on 4 pages, 17 times on /learn/signs alone. "Two to three weeks": 19 times across 9 of 12 articles. **"Three weeks… This is the threshold used in clinical guidelines"** (`mouth-sore:52`), the "three-week rule" (`tongue:50`), and "A three-week wait-and-watch period is reasonable" (`tongue:62`). The Spanish articles carry the same thing ("dos o tres semanas"). |
| Erythroplakia risk | "50% or more… cancerous or precancerous at biopsy" (`en.json:833`). "14–50% malignant transformation rate" (`:1851`). "the large majority of erythroplakia biopsies" (`:2132`). |
| Leukoplakia risk | "roughly 5 to 17% will become malignant" (`:833`, `:1851`). "a few percent over several years" (`:2130`). |
| Tobacco | "Daily smokers face 2–6× higher risk" (`:1812`). "Heavy smokers are 6 to 27 times more likely" (`:539`). "OR 6.0×" (`:1324`). "roughly 75% of traditional oral cavity cancers" (`:538`, `:650`), unsourced. |
| "2 minutes" | Used for three different things: the screener (hero, flyer), the self-exam ("How to Do a 2-Minute Self-Exam"), and the dentist's exam ("2 min is all a dental screening takes"). The articles then say the self-exam takes "about five minutes" (`self-exam:20`) and the clinical exam "between two and five minutes" (`screening:18`). |
| Betel quid without tobacco | "Group 1 carcinogen" with or without tobacco (`:1898`, `:1429`). The `white-patch` article (`:45`) says IARC classes it without tobacco as "a probable carcinogen". That is wrong: IARC Monograph 85 put betel quid without tobacco in Group 1. |
| Stage | Methods says "Over 60% of oral cancers are found at stage III or IV" (`en.json:1464`). That is AJCC staging, which the house rule bans. The site's own SEER summary-stage figure is 55% regional plus 12% distant. |
| Who reviewed it | Methods says the review was by "a practising oral and maxillofacial pathologist" (one person, `:1481`). Two paragraphs later it says "Both clinicians who reviewed this" (`:1518`). The second review, by a head-and-neck surgeon in September per OWNERS_GUIDE:1155, never made it into the review paragraph. |
| HPV vaccine age | "FDA-approved through age 45" (Learn pages). "Catch-up vaccination is approved for adults up to age 26" (`oropharyngeal:34`). Both are partly right, but nothing explains how they fit together. |

**Why it costs trust:** stating the same fact in different words with different numbers is the strongest sign of text generated piece by piece. A dentist reading two pages will catch the 2-week versus 3-week conflict straight away.

**Fix:**
- Use one threshold, word for word, everywhere: "If a sore, patch or lump in your mouth has not cleared up in two weeks, have a dentist or doctor look at it." Replace every "two to three weeks" and "three weeks" with it, and delete the "three-week rule" paragraph in `tongue` and the "Three weeks or longer… clinical guidelines" bullet in `mouth-sore`.
- Erythroplakia: use one sourced range everywhere, the Patches wording plus a link to Warnakulasuriya, for example "Most red patches that are biopsied show severe dysplasia or cancer (Warnakulasuriya et al., Oral Diseases)". In the screener subtitle drop "14–50%".
- Leukoplakia: pick one framing, "a few percent over several years, higher for speckled or red-and-white patches", and use it in Signs and Questions.
- Tobacco: cite Gandini once with its figure and delete "6 to 27 times" and the unsourced "75%".
- "2 minutes": keep it for the screener only. Self-exam heading: "How to check your own mouth". Flyer stat: delete the "2 min" tile.
- Betel (`white-patch:45`): "IARC classifies betel quid as a Group 1 carcinogen whether or not tobacco is added."
- Methods `:1464`: "About two-thirds of cases are found after the cancer has spread, to nearby lymph nodes (55%) or to distant sites (12%)."
- Methods `:1481`: "…revised after review by a practising oral and maxillofacial pathologist in August 2026 and a head and neck surgeon in September 2026."

### 4. Em dashes were find-and-replaced with commas, which left comma splices everywhere

The English copy has no em dashes. Many sentences, though, still have the shape of an em-dash aside with a comma in its place, so they read as run-ons, and some no longer parse. The same splices carry into Spanish and Portuguese. Live examples:

- "certain strains, especially HPV-16 cause changes in cell DNA" (`en.json:307-309`, the comma is missing)
- "their effects are synergistic, not additive, someone who smokes more than a pack a day…" (`:527-528`)
- "isn't entirely preventable, some risk factors, like age and genetics, aren't in your control" (`:218`)
- "includes a 2-minute oral cancer screening, your dentist checks your lips…" (`:244`)
- "When to see a doctor, don't wait if:" (`:461`, rendered as an H2)
- "significantly raise oral cancer risk, cigarettes, cigars, pipes…" (`:539`)
- "easy to dismiss, people assume oral cancer is a smoker's disease" (`:347`). Also `:348` "HPV is extremely common, most sexually active adults…", `:354` "may still benefit, talk to your doctor", and `:305`.
- "You do not need to wait to see if it gets worse, 2 weeks is the threshold." (`:827`)
- "New or growing lumps deserve a look, feel for them during a self-exam." (`:1049`)
- "is already part of a routine cleaning, it takes 2 minutes" (`:1657`)
- Results and risk-engine text: `:1909`, `:1911`, `:1914`, `:1915`, `:1963`
- Learn cards: "and more, what raises your risk" (`:1072`), "and numbness, what to look for" (`:1082`), "warning signs look like, a plain-English overview" (`:1077`)

**Why it costs trust:** text written by a person does not break like this. It looks like one system's output was cleaned up by another, and grammar errors on a clinical page read as carelessness.

**Fix:** rewrite each one with a period or a colon. For example:
- "Oral cancer isn't entirely preventable. Some risk factors, like age and genetics, are out of your control. The biggest ones are not."
- "Used together, tobacco and alcohol multiply each other's effect. Someone who smokes more than a pack a day and has three or more drinks a day has about 15 times the risk of someone who does neither."
- "In some people, certain strains, especially HPV-16, change cell DNA in ways that can lead to cancer."
- Heading: "See a dentist without waiting if:"
- "A routine dental visit includes a short oral cancer check. Your dentist looks at your lips, gums, tongue, cheeks, palate and throat."

Run a pass over all three catalogues for `, [a-z]+ (is|are|it|you|they|people)` after a full clause.

### 5. The home page and Learn pages use the stock AI landing-page kit

Home (`src/app/[locale]/page.tsx`, screenshots `home-viewport.png`, `home-fold2.png`):
- **Hero:** an all-caps tracked eyebrow with a middot triad ("FREE · PRIVATE · EVIDENCE-BASED"), a slogan headline with one word in an accent colour ("2 minutes could *save* your life."), two pill buttons, and a "Featured in" line.
- **Stat tiles:** monospace count-up tiles: "60,480+", "89%", and "890+ people reached since launch" with "LIVE, UPDATED HOURLY" in mono caps. The "+" turns a SEER projection into a marketing number. "People reached" is undefined (it comes from GA users).
- **"Three things this tool does":** three identical rounded cards, each with an "→" CTA.
- **Pull quote:** it repeats the 89% from the tiles 20cm higher, this time as 88.7%.
- **Share band:** "Print it. Post it. Pass it on." (a three-beat slogan).
- **Logo marquee:** an unlabeled, greyscale, endlessly scrolling row (`LogoMarquee.tsx`). It holds the WDA, More Smiles Wisconsin, "Michael S. Harris DMD PA" and a general dentist. With no label, a "trusted by" row reads as endorsement. Suspected: the Harris practice may be a relative's, which a reader will notice. Nothing in the docs records what these logos mean.
- **Instagram strip.**

Every Learn page has the same skeleton: a tag eyebrow, H1, intro, a named "rule" box, sections, a six-item icon list of "what to do", "Common questions" with 5 FAQs (7 pages), an unlinked "Sources:" list ending "This page is educational and does not constitute medical advice" (6 pages), a CTA row starting "Take the free screener →" (17 pages), and a byline. The FAQs mostly restate the page body. On /learn/canker-sore-vs-oral-cancer the 2-week threshold appears 6 times. The slogan "2 minutes could save your life" is used 4 times: hero, flyer, the For Clinicians meta, and the results share text.

**Why it costs trust:** these are the patterns the "AI slop" write-ups list first, and a health site that looks like a SaaS template reads as a funnel, not a resource. "Could save your life" is also a fear claim the tool cannot back up, because the screener does not find cancer.

**Fix:**
- **Hero.** Drop the eyebrow triad. Replace the slogan with what the tool does: "Check your oral cancer risk factors in about two minutes." Sub-line: "Ten questions, scored from published studies. Your answers are not stored. It cannot tell you whether you have cancer, but it can tell you whether to book a dental visit soon." Keep one colour in the headline.
- **Stats.** Keep one plain sentence with its source and drop the count-up: "About 60,480 people in the US will be diagnosed this year. Only about 1 in 4 cases is found before it spreads (NCI SEER)." Remove the "people reached" tile, or if Ian wants to keep it, call it "screeners completed" and drop "LIVE".
- **Cards.** Replace "Three things this tool does" with a short paragraph and three plain links, or with a single real example result screenshot.
- **Logos.** Label the row with what is true, for example "Practices and groups that have shared OralCheck with patients", if each one has. Otherwise remove it. Leave out any practice with a family tie, or say so.
- **Share heading.** "Put a QR code where people wait".
- **Learn pages.** Keep FAQs only where the questions are real searches with answers not already on the page (Patches is the model). Cut the rest. Vary the CTA ("See which of these apply to you" on Risk factors, "Find a dentist near you" on Signs).

---

## Findings by severity

### High

| # | Location | Text | Tell | Fix |
|---|---|---|---|---|
| H1 | `results/page.tsx:106`, `api/summary/route.ts`, `en.json:71,1161,1240,1549,1787,2060`, Privacy `:1289` | "Nothing is saved or sent anywhere." / AI summary unlabeled | Undisclosed AI content (Google "How"); false privacy claim | Finding 1 |
| H2 | `content/published/*` | "Most people…", "This article…", "It takes only a few minutes", "## Conclusion", the kicker endings | Formulaic generated articles, no author | Finding 2 |
| H3 | 15 links in 6 articles | "[the HPV oral cancer connection](https://oralcheck.org)" | Placeholder URLs | Link the real slugs (finding 2) |
| H4 | `mouth-sore:52`, `tongue:50,62`, 9 articles | "Three weeks… threshold used in clinical guidelines", "three-week rule" | Contradicts the site's 2-week rule; vague authority | Finding 3 |
| H5 | `en.json:1464` | "Over 60% of oral cancers are found at stage III or IV" | AJCC staging, against the house rule | "About two-thirds are found after spreading, to lymph nodes (55%) or distant sites (12%)." |
| H6 | `white-patch…:45` | "betel quid without tobacco as a probable carcinogen" | Factual error, contradicts `en.json:1898` | "IARC classifies betel quid as a Group 1 carcinogen whether or not tobacco is added." |
| H7 | `en.json:833,1851,2130,2132`, `:539,1812` | Erythroplakia, leukoplakia and tobacco figures in 3 versions each | The same fact restated with different numbers | Finding 3 |
| H8 | `en.json:207,808,1005` (bylines), `:1537,1544,1545`, `:1980,2009,2018`, plus `layout.tsx` structured data (already on ROADMAP, blocked on Ian) | "predental student at the University of Wisconsin-Madison" | House-rule violation; implies affiliation | "Written by Ian Harris, a predental student." About title: "Founder · Predental student". Remove the `affiliation` in JSON-LD. |
| H9 | Comma splices, finding 4 | "especially HPV-16 cause changes" | Mechanical em-dash removal | Finding 4 |

### Medium

| # | Location | Text | Tell | Fix |
|---|---|---|---|---|
| M1 | Footer `en.json:37` (every page), `:1166`, `:1310`, `:1771` | "Risk scoring informed by ACS, NCI, and Oral Cancer Foundation clinical guidelines." | Vague authority. The weights come from odds ratios in named papers, not from guidelines, and the OCF is not a guideline body. | "Scores come from published studies, each listed on the methods page." Link it. |
| M2 | Sources lines `:148,289,380,512,670,807,1000` | "American Cancer Society, National Cancer Institute, CDC, Oral Cancer Foundation, World Health Organization." / "American Cancer Society (2024)" / "Figures are approximate and rounded for readability" | Unlinked lists of organisations; the rounding note sits next to "88.7%" | Link each source to the page actually used. Delete "(2024)" and the rounding sentence. |
| M3 | Unsourced claims: `:139` "Dentists find most early cases."; `:1666` "Most oral cancers caught early are found by people who already knew what to look for" (contradicts `:139`); `:400` canker sores "about 1 in 5 people"; `:1793` "Risk roughly doubles per decade above 40"; `:965` "Many offer free oral cancer screenings"; `self-exam:10` "Most people visit a dentist twice a year… roughly 363 days" (false); `early-signs:18` "Research consistently shows the average delay… is several months"; `lip:18` "some studies suggesting… 88 to 95 percent"; `oropharyngeal:28` "Research published in journals including the Journal of Clinical Oncology and data from the CDC consistently show…"; `young-adults` "There is a well-documented pattern: younger patients tend to be diagnosed at later stages"; `screening:69` "The American Dental Association supports this" | (see Location) | Vague attribution, unsourced clinical claims | Link a source or cut. For `:1666`, cut the sentence. For `self-exam:10`, open with "A dentist sees your mouth for a few minutes a year. You can check it once a month." |
| M4 | `:1761`, `:1471`, `:2208` vs `:79`, `:1888` | Two different "1 in 4"s: no risk factors, and found while localized | Repeated phrasing for unrelated facts, so readers conflate them | Cite the no-risk-factor figure (Suspected unsourced) and phrase it differently: "A meaningful share of oral cancers, roughly a quarter in published series, occur in people with none of these risk factors." Add the link. |
| M5 | `young-adults` title and intro | "Why Oral Cancer in Young Adults Is More Common Than Most People Expect" | Overclaim. SEER (`seerStats.ts` ageShare) puts 2.1% of cases under 35. | Title: "Oral cancer under 40: rare, but not impossible". State the SEER share in the first paragraph. |
| M6 | Methods `:1404,1468,1511,1516,1518,1464` | "It is worth being blunt about where these four numbers came from", "Two things worth being precise about", "stated plainly so nobody has to infer them", "Every question earns its place", "Not a risk factor at all, and the page is explicit about that", "worse than saying nothing" | Performative candor: the text comments on its own honesty, a recognisable LLM voice | Keep the substance and cut the throat-clearing. For example `:1516`: "These four boundaries were set by judgment against the reference profiles above, then checked against the spread of possible answers. No outcome data was used, so there is no sensitivity, specificity or ROC curve behind them." |
| M7 | `:131`, `:230`, `:527`, `:616`, `:748`, `:1939`, `:1258`, `:469`, `:1521` | "multiply risk, not just add", "doesn't just add the risks, it multiplies them", "synergistic, not additive", "multiplicative, not merely additive" (3 times), "Prevention isn't just about avoiding risk", "That's not reassuring, it's a reason", "a change to what the tool explains, not to what it computes" | Negative parallelism, about 10 times | State the interaction once, as a number: "together, about 15 times the risk of someone who does neither (Hashibe 2009)". Elsewhere drop the "not X" half. |
| M8 | en.json and articles | "single most/biggest/largest/strongest/clearest" 16 times; "actually" 21; "worth" 41; "significantly/substantially/dramatically/meaningfully" 37; "warrant(s)" 22; "precisely/exactly why" 8 | AI vocabulary clusters | Keep "single" for tobacco only. Delete most "actually" and intensifiers. "Warrants evaluation" becomes "should be checked". |
| M9 | Named rules: `:457,779,824` "The 2-week rule"; `:525` "The two-factor rule"; `tongue:50` "three-week rule"; `:393` "The quick answer"; `:2116` "The part that actually matters" | (see Location) | Invented branded rules and headings that announce themselves | Keep the 2-week guidance once per page as a plain sentence. Rename `:525` "Tobacco and alcohol together", `:2116` "When to get a patch checked". |
| M10 | Learn pages vs articles | `/learn/self-exam` and `oral-cancer-self-exam`; `/learn/canker-sore-vs-oral-cancer` and `mouth-sore-vs-oral-cancer`; `/learn/white-and-red-patches` and `white-patch-on-tongue…`; `/learn/hpv` and `oropharyngeal-cancer-hpv-adults`; `/learn/signs` with `oral-cancer-symptoms`, `early-signs-of-oral-cancer` and `what-does-oral-cancer-look-like` | Keyword-variant pages that repeat each other | Merge each article's unique parts into the Learn page and redirect the slug (that is a code change, after Ian agrees). Merge order: self-exam, mouth-sore, white-patch, symptoms. |
| M11 | `:1966`, `:1631`, results modal (`shots-ai/results.png`) | "The difference is dramatic… could be the most important appointment you make this year." / share text "I just used OralCheck… 2 minutes could save your life." / the email modal opens over a "See a dentist soon" result | Sales funnel tone; puts a slogan in the user's mouth | `:1966` ends "…against 36% once it has spread to distant sites. The exam takes a few minutes." Share text: "I checked my oral cancer risk factors with OralCheck, a free screener: {url}". Show the email offer inline below the next steps, not as a modal. |
| M12 | `:1911` | "the Wisconsin Tobacco Quit Line is available at 1-800-QUIT-NOW" | A local detail on a national site, plus a comma splice | "Call 1-800-QUIT-NOW to reach your state's free quit line." |
| M13 | `:1160-1161` | "Zero PHI collected… No HIPAA concerns, no data liability." | Legal overclaim, and not true while finding 1 stands | "No names, emails or answers are stored. Nothing identifies the patient." |
| M14 | Spanish catalogue | 102 strings use tú, 41 use usted, mixed on the same page (Signs, Results: "Evalúa tu riesgo" next to "Haga una cita… Mencione sus factores") | Machine-translation tell | Pick tú for the UI, or usted for clinical guidance, and apply one consistently. A native reviewer should do a pass. |
| M15 | Portuguese About bio (`pt.json` AboutPage) | "Há alguns anos, foi diagnosticada uma condição crônica…", "Acredita-se que deixar a comunidade mais saudável…" | The translation removed the first person, so Ian's own story reads as written by nobody | Restore the first person: "Há alguns anos fui diagnosticado com uma condição crônica…", "Acredito que…". |
| M16 | `:1980`, `:2001` | "available in English and Spanish" | Stale fact (Portuguese is live) | "in English, Spanish and Portuguese". |
| M17 | Articles vs Learn pages | Learn pages: "Written by Ian Harris". Articles: "Published by OralCheck" only | Unclear authorship (Google "Who") | Finding 2 disclosure line. |

### Low

| # | Location | Text | Tell | Fix |
|---|---|---|---|---|
| L1 | Methods headings `:1321,1326,1331,1335,1343,1403,1467,1478,1483,1517`, all article H2s | "Weight Derivation", "Known Limitations", "Common Oral Cancer Symptoms You Should Know" | Title case | Sentence case, to match the rest of the site |
| L2 | 40 arrows in en.json | "Take the free screener →", "Read →", "Learn more →" | An arrow on every link | Keep it on the one primary CTA per page |
| L3 | `:221-256`, `:124` | "01" to "06" on prevention steps (not a sequence); "FACT" label above each fact | Decorative numbering and labels | Drop the numbers and the label |
| L4 | `:305` | "HPV-positive cases rose 225% from 1988 to 2004" | A 20-year-old statistic presented as current | Use a recent trend figure from a linked source, or cut |
| L5 | `es` home stats | "60,480+", "88.7%" | US number formats in Spanish (should be 60.480 and 88,7 %) | Format numbers per locale |
| L6 | `es.json` AboutPage | "estudiante de predontología" | Suspected non-word | "estudiante universitario que se prepara para estudiar odontología" |
| L7 | Article layout | Lede sentence, then date and read time, then the rest of the same paragraph | A template splits the first paragraph | Put the metadata above the full first paragraph |
| L8 | `:65` | "Featured in The Drill · Wisconsin Dental Association" | True (April 2026, `docs/OralCheck_ADA_Briefing_v2.md:140`), but unlinked, which looks invented | Link to the issue, or write "Featured in the Wisconsin Dental Association's newsletter, The Drill (April 2026)" |
| L9 | `:1545` | "I care a lot about community health and finding ways to actually make a difference" | Generic line in an otherwise personal bio | Ian replaces it with one concrete reason in his own words. Do not invent one. |
| L10 | `:1070` vs `:1095` | "Risk Factors" vs "Risk Factor" vs "Risk factors" tags | Inconsistent labels | "Risk factors" everywhere |
| L11 | `oral-cancer-symptoms:30` | "Ear pain without hearing loss" | An odd qualifier, likely invented | "Ear pain on one side with no ear problem" (matches `:867`) |

---

## Repetition map (counted)

Method: 6-gram overlap across every en.json section and all 12 articles (`ngrams.py`), phrase counts (`counts.py`), and rendered-text counts on the 32 live pages (`crawl.json`).

**Disclaimers and boilerplate**
- "…and does not constitute medical advice": 19 documents (12 articles plus ArticlePage, Canker, HPV, OralCancer, Prevention, RiskFactors and Signs).
- "Medical Disclaimer: This article is intended for general informational purposes only": 10 articles. The article template also renders its own disclaimer slot.
- "This page is educational and does not constitute medical advice": 6 Learn pages.
- Footer disclaimer plus footer "Risk scoring informed by ACS, NCI…" on every page, so a Learn page shows 2 or 3 disclaimers.
- "not a medical diagnosis": 4 pages in the "Not a…" form and 4 in lower case, plus the footer.

**Calls to action**
- "Take the free screener →": 17 live pages. "Check your risk →": 5.
- "OralCheck offers a free (evidence-based) oral cancer risk screener at oralcheck.org. It takes only a few minutes…": 12 of 12 articles ("it takes only a few minutes" 8 times verbatim, "screener at oralcheck.org. It takes" 9 times).
- "can help you think through your…": 4 articles. "is designed to help you understand": 4.
- "It is not a diagnostic tool, but it is a … starting point": 8 articles.

**The same fact, restated**
- 2-week threshold: 61 mentions in en.json across 13 sections. 17 on /learn/signs, 7 on /learn/white-and-red-patches, 6 on /learn/canker-sore-vs-oral-cancer. Contradicted by "two to three weeks" or "three weeks" 19 times in 9 articles.
- 89% / 88.7% survival: 15 times in en.json (9 sections), 4 articles, 8 live pages, twice on the home page. 36%: 11 plus 3.
- "HPV(-16) is now the leading cause of oropharyngeal cancer": 6 documents (HpvMeta, HpvPage, LearnCards, Facts, Methods, RiskFactors, plus 2 articles).
- "15 times / 15-fold" tobacco plus alcohol: 9 times in 5 sections. The "multiplicative, not additive" framing: about 10 times.
- "2.6 times the rate of women": 8 times in en.json plus 2 articles.
- "1 in 4" or "a quarter": 8 times, for two unrelated facts (finding M4).
- "60,480": 5 plus 2.
- "2 minutes" or "two-minute": 28 times in en.json across 14 sections, for three different things (finding 3).
- "Gardasil 9 protects against HPV-16 and HPV-18": 4 times (Prevention body and FAQ, HPV body and FAQ).
- "Your answers stay on your device": 4 sections. "student at the University of Wisconsin-Madison": 5 sections.

**Structural repetition**
- Learn page skeleton (eyebrow, H1, intro, rule box, icon list, 5-question "Common questions", Sources line, CTA row, byline) on 7 pages.
- The six-item "what to do" icon list with a title and one-line description on Signs, Risk factors, Canker and Patches. The same icon-title-line grid appears in For clinicians "Why OralCheck", the flyer features and the results factors.
- Articles: 4 or 5 Title Case H2s, `---` between each, bold inline-header paragraphs, a closing CTA section, and a disclaimer, in 12 of 12.

## Spanish and Portuguese

- Both carry every English tell: the slogan, the triad eyebrow, the comma splices (for example "Cuándo consultar a un médico, no esperes si:", "no es completamente prevenible, algunos factores…"), the "realmente" and "realmente atraen" translations of "actually", and the "dos o tres semanas" contradiction in the Spanish articles.
- Spanish reads as machine translated mainly because of the tú/usted mix (M14) and US number formats (L5). The sentences themselves are fluent.
- Portuguese is fluent but impersonal. The About bio is the clearest machine tell on the site in any language (M15).

## What already works (keep)

The Patches page, the Methods limitations list, the "which of the two this points at" block on results, and the static `RiskEngine.summary` texts are specific and grounded, and they read like someone who knows the subject. They are the model for the rewrites above. The site has no gradient text, emoji bullets or sparkle icons.
