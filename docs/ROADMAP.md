# OralCheck roadmap

The running list. Two rules:

1. **Nothing gets deleted.** Shipped items move to *Shipped* with a date. Rejected
   ideas move to *Decided against* with the reason, so the same idea does not get
   re-litigated from scratch in six months.
2. **Open items stay open until they are actually done.** An item that was raised,
   half-built, or blocked on something external stays in *Open* with its blocker
   named. This is the list's whole purpose: the things that come up once, sound
   good, and are never mentioned again.

Last updated: 2026-09-01

**Mirrored to an artifact Ian reads:**
https://claude.ai/code/artifact/cc490e4b-1ee3-4062-bc56-eada066f1003
Update both together. See `AGENTS.md`.

---

## Open — blocked on something external

| Item | Blocked on | Notes |
|---|---|---|
| ~~Publishing articles from `/review/<slug>`~~ | **Done — it already was** | `ADMIN_SECRET` has been set in Vercel (Preview + Production) since 2026-08-24; this entry was simply never marked off. Verified 2026-09-01: `/api/publish` and `/api/draft` both return **401**, not 503, for a missing or wrong secret, which is the signature of a configured and correctly-gating secret. The header is `x-oralcheck-admin`. |
| A named clinical reviewer on `/methods` | Marquette Chair + Associate Dean for Research | **Dr. Yeshwant Rawal reviewed the methodology on 2026-08-24** and called it "done thoughtfully and based on evidence through relevant literature". He is President of the American Board of Oral & Maxillofacial Pathology, so this is a serious credential. **He has agreed in principle** (2026-08-25): "I would be very happy to associate myself with this excellent project." Conditional on his Chair and Associate Dean for Research, both copied. He asked whether there is a UW-Madison mentor or institutional protocol; there is neither, and the reply says so plainly. **Ian sent the final weights on 2026-09-01, as promised.** His name still does not go on the site until his institution clears it. |
| A real quote on the homepage | The same permission | Currently carries a cited NCI SEER statistic, which is honest but is a citation rather than an endorsement. Rawal's review is the first plausible source for a real one. Do not fabricate one, and do not quote him until he says yes. |
| A UW-Madison faculty mentor | Their replies | **Ian replied to both Glazer and Brant on 2026-09-01.** Brant's three methodology criticisms were acted on before the reply went out: two were added to `/methods` as stated limitations (pooled ORs across source populations, judgment-set cutoffs), and the third, oral cavity vs oropharynx, is being addressed in the product. Waiting on his answer about the clinical half and about whether UW's ICTR biostatistics route is open to an undergraduate. |
| Whether UW considers this a university project at all | Ian's academic advisor | **Raised by Dr. Brant, 2026-08-30**, and it outranks the IRB question. Faculty must disclose anything job-related or using university resources, and Brant specifically guessed the source papers were pulled through UW library access. He also questioned whether the site's disclaimer is actually sufficient protection or only reads that way. Ian asserting "this is not a UW project" is not the same as UW determining it. Ask the academic advisor, and ask specifically about (1) what counts as a university resource for an undergraduate and (2) whether the disclaimer holds up. Monetization would raise the stakes on all of it; there is none and no plan for any. |
| Registering GA4 custom definitions | Two one-time Google console steps | Cannot be done from here: the **Analytics Admin API is disabled** on Cloud project 130228649204 (only the Data API is on), and the service account would then also need **Editor** on the property rather than Viewer. `oralcheck-agent/register_ga_dimensions.py` is written and dry-runs cleanly; it creates all six once those are done. Doing it by hand in GA4 Admin -> Custom definitions is about a minute each and needs no API at all. **It is six parameters, not one**: dimensions `risk_tier`, `has_urgent_symptom`, `source`; metrics `risk_score`, `question_count`. Registration is never retroactive, so every day unregistered is data that cannot be recovered. |
| A written UW IRB determination | Ian submitting it | The tool stores nothing, so it is almost certainly *not human subjects research* under UW's HRPP, but the assertion is worth having on paper for Marquette's Associate Dean. Free, and Ian can submit it himself. |
| Co-branded Marquette flyer | The approval above | Rawal proposed a design "to reflect our two institutions". Corrected in the reply: OralCheck is not a UW project and cannot carry UW branding. Marquette + OralCheck only. |
| Judge whether the reel skip-rate fix worked | A new reel going out | 83.7% skip. Frame-0 fix and cover image both shipped, but only affect reels rendered *after* they landed. The three currently scheduled were rendered before. |
| Trustworthy completion rate over 90d | ~2 weeks of clean events | The double-count fix shipped 2026-08-10. Until then only short windows are reliable. 30-day read at fix time: **91.4%**. |
| Outreach replies | Ian sending them | 10 contacts: the original 7 in `outreach-contacts.csv` (Penn/CIGOH, Tufts x2, Columbia x2, HNCA, AAOM) plus 3 at Marquette. **Drafts are written** in `outreach-drafts/` as of 2026-08-18, so the only remaining step is pasting them into Outlook and sending. Update Status to `Followed Up` after each, or the Sunday tracker will generate duplicates. |
| ~~LinkedIn auto-publishing~~ | **Done 2026-09-01** | Both accounts are connected in Publora with valid tokens. The plan is now `WEEKLY_PLAN=instagram:2,linkedin:1`: each post targets one network rather than fanning out to all of them, which is what made the quota impossible before. Three platform-targets sits exactly at the Starter cap, so raising either number needs a bigger plan. |

---

## Open — ready to do

### Content and growth

- [x] ~~Reels drive follows but not site visits~~ — partly fixed 2026-09-01, and
      the entry contained a false premise. **A link sticker on the reel itself is
      not possible.** Reel captions render as plain text for everyone, clickable
      links on a Reel require a Meta Verified Plus subscription and are capped at
      2 to 6 reels a month, and Instagram's publishing API cannot place stickers
      at all: they exist only in the app. Resharing the reel to a Story with a
      link sticker is the one free clickable route, it is manual, and it takes
      about fifteen seconds. Approving a reel now sends a Telegram reminder with
      the steps and the date it becomes actionable. The end card was rebuilt: the
      address is now the largest element rather than the smallest, and it holds
      **4.5s instead of 2.4s** (of which 0.4s used to be fade, leaving about two
      seconds to read an address and decide to act).
- [ ] **Worth testing: comment-to-DM as the real fix.** Viewers comment a keyword
      and get the link in a DM automatically. It is free, unlimited, clickable,
      and unlike the Story sticker it needs no manual step per reel. Needs a
      third-party tool (ManyChat and similar) connected to the Instagram account,
      so it is a signup decision rather than a code change.
- [ ] **More post templates.** Twenty-one shapes now reachable (16 designed +
      5 basic). Keep going: the goal is enough that the feed never looks
      repetitive.
- [ ] **Reels have had none of this work.** The sixteen designed layouts are
      carousel/static only. Reels are still the old kinetic-text scenes with
      five backdrop variants, which is the next real design job.
- [ ] **One of six signs still has no clinical photo: the red patch
      (erythroplakia).** Ian found a good one at exodontia.info, but the site is
      all rights reserved ("Copyright @ Exodontia") with full terms and no open
      licence, so it is not usable as found. A permission request is drafted at
      `outreach-drafts/2026-09-01-Exodontia-Image-Permission.md`; it is one
      clinician running a teaching site, which is about as askable as this gets,
      and a named credit from a consultant oral surgeon beats an anonymous
      Commons file anyway. Fallback if declined: Openverse filtered to commercial
      use, or a CC BY case report in PLOS ONE / BMC Oral Health.
- [x] ~~A photo for lump/thickening~~ — **decided against 2026-09-01.** Ian
      dropped it. Photographs of a submucosal mass almost all come from surgical
      case reports, so an openly licensed one that reads clearly to a general
      audience is unlikely to turn up, and the entry would have sat open forever.
      The sign keeps its illustrated diagram.
- [ ] **Two sign photos carry no attribution.** `sore` and `lip` in
      `src/lib/signPhotos.json` have no `author`, `license` or `source`, where
      `white` and `mixed` have all three. Their provenance is not recorded
      anywhere, so it has to be re-established or the images replaced. On a page
      that argues everything is checkable, two uncredited clinical photos are the
      weak spot.
      (erythroplakia) and lump/thickening. No openly-licensed image found yet.

### Product and credibility

- [ ] **Find a biostatistician, not another clinician.** Brant's most useful
      sentence: a faculty mentor cannot tell you whether the stratification is
      valid, and conflating the two roles was a mistake. Ask whether UW's ICTR
      route is open to an undergraduate and whether it needs a faculty sponsor.
- [x] ~~Oral cavity vs oropharynx~~ — shipped 2026-09-01, and **neither of the two
      options in this entry was taken**. Splitting into two scores would have built
      the oropharyngeal one on a single question, which is not a score. Dropping HPV
      to narrow the scope would have removed the fastest-growing part of the disease.
      The score stayed whole and the *explanation* changed: each question is tagged
      with the disease it speaks to, and the results page names which one a person's
      own factors point at. Shared factors (age, sex, family, immune, symptoms,
      dental) are excluded from the comparison so they cannot drag every profile
      toward whichever site has more questions. A site is named only at twice the
      other's weight.
- [ ] **Open, and it belongs to the clinicians: should the HPV weight rise?** It is
      5, from a conservative pooled OR, where the published association for confirmed
      HPV-16 with oropharyngeal cancer specifically is roughly 15. It was deflated
      *because* the score had to cover both diseases. Now that the results page says
      out loud which disease a profile points at, and admits the score understates an
      HPV-driven one, the reason for the deflation is weaker. Worth putting to Rawal
      and Brant together, since it is the one question both of them are placed to
      answer.
- [ ] **The web app has no test suite.** Everything in `oralcheck-agent/` has one and
      is exercised in CI; `src/` has none, so the risk engine is verified by hand
      each time. The site attribution added on 2026-09-01 is the kind of logic that
      would fail silently and clinically: worth a small runner over `computeRisk`
      covering the tier boundaries, the interaction bonus, and the site lean.
- [x] ~~Systemic risk factor question~~ — shipped 2026-08-27, weight 5.
- [x] ~~Sex at birth question~~ — shipped 2026-08-27, weight 3.
- [x] ~~Language dropdown~~ — shipped 2026-08-27. Renders any number of locales,
      names each language in its own language, closes on Escape and outside click.
- [x] ~~Portuguese translation~~ — shipped 2026-08-27.
- [ ] **Send Rawal the final weights.** Draft is written
      (`outreach-drafts/2026-08-27-Yeshwant-Rawal-WEIGHTS.md`) and the question is
      already live, which is the wrong order relative to what the previous reply
      promised. Send it. The one substantive question in it: the honest derivation
      gives the systemic question a weight of **5** (blended OR 3.0), joint fourth
      of twelve. He said "weighted high" and may have meant higher. He is the
      person who gets to say so.
- [x] ~~Site-wide survival statistics are stale~~ — fixed 2026-08-30. The audit
      turned up that it was not only the 84/38 pair: case count, death count,
      the death interval, and the sex ratio were all from superseded releases,
      and the site contradicted itself on late-stage survival (38% on results,
      40% on two learn pages, "around 67 percent" for regional in a published
      article). All now read from `src/lib/seerStats.ts`, which carries the
      source URL and a `lastVerified` date. **Re-check it annually**; the case
      and death figures are year-stamped projections and go stale on schedule.

- [x] ~~Tighten the terminology~~ — fixed 2026-09-01, and it was far smaller
      than this entry implied. An audit of all 71 uses of screening/screener/screen
      found that **most were already correct**: they describe the dentist's exam,
      which is exactly what the framing wants. Only four called OralCheck itself a
      screening, and the homepage CTA was the worst of them. Fixed: "Start
      Screening" became "Check your risk", "Screening logic informed by" became
      "Risk scoring informed by" (footer and privacy), and `/for-clinicians` no
      longer says "an elevated screen result". The results disclaimer now names
      what the real screening *is* rather than only what OralCheck is not.
      **Decided: the product keeps the name "risk screener."** It screens risk
      factors, not tissue, the phrase is accurate on that reading, and renaming it
      would cost the title tags, meta descriptions and search positioning of every
      page in three languages. The rule going forward is narrower and easier to
      hold: never say OralCheck *performs* a screening, and never call its output a
      screen result.
- [x] ~~Make `/methods` exceptional~~ — shipped 2026-08-27. Per-question rationale
      for all twelve, a "What this tool cannot tell you" section, a last-reviewed
      dateline at the top, and a review-and-maintenance block at the bottom. The
      one part deliberately left undone is naming the reviewer; see the blocked
      table above.
- [ ] **Add a "last reviewed" date to the rest of the clinical pages.** `/methods`
      has one as of 2026-08-27. The `/learn` articles do not. Mayo and NIH do this;
      it converts "someone wrote this once" into "someone maintains this".
- [ ] **Recruit 5–10 dental professionals** to review the screener questions, risk
      categorisation, results wording, and disclaimer. Higher value right now than
      more content.

### Distribution

- [ ] **Dental-office pilot.** The infrastructure already exists and is under-used:
      printable waiting-room flyer, QR generator, and a copy-paste embed on
      `/for-clinicians`. Ask for a **30-day pilot, not a partnership** — far easier
      to say yes to.
- [ ] **"Founding Practice" status** for pilot practices: badge, certificate,
      listing, early access. Gives status rather than asking a favour.
- [ ] **Per-practice aggregate stats** eventually (scans, completions, % elevated).
      Aggregate and de-identified only; never imply a practice receives individual
      health data.

### Infrastructure

- [ ] **Meta Graph API** for direct Instagram publishing, removing the Publora
      dependency and its 3-post cap. Needs a Facebook app, a linked Business
      account, and token refresh handling.
- [ ] Rotate the Google Places API key. Low priority: it is restricted to Places
      API (New) with a daily cap, so the blast radius is small.

---

## Shipped

Newest first.

### 2026-09-01 (late)
- **Reels have a design system.** Six scene archetypes in `reel_scenes.py`
  (splitstat, contrast, checklist, quote, term, enumerate), mapped to the content
  pillars, validated before render, de-duplicated within a reel, and never given
  a photo backdrop that would fight what they exist to show
- **Oral cavity vs oropharynx, without splitting the score.** The results page now
  names which of the two a profile points at. The case this fixes is a young
  non-smoker with HPV history: they scored 5 (moderate) off a total dominated by
  the tobacco and alcohol questions they answered "never" to, and the page now
  tells them their factors point at the oropharynx and that the score understates
  it, rather than leaving them to infer reassurance

### 2026-09-01 (night)
- **`find_care_click` has fired 0 times since it shipped**, across roughly 25
  completions. Tested it end to end on production rather than assuming it was
  broken: the handler pushes the right payload to `dataLayer` and a real
  `/g/collect` request leaves the browser with `en=find_care_click`. The
  instrumentation is fine. Nobody is clicking it
- **Found why it will always undercount**: the elevated and high tiers put a
  *second* route to `/find-care` in the next-steps list, and only the big CTA
  below it was tagged. Now both are, separated by a `source` parameter so they
  can be compared rather than merged
- `ADMIN_SECRET` was already set in Vercel and had been since 2026-08-24. The
  roadmap had it listed as blocking for a week for no reason

### 2026-09-01 (evening)
- **Reel end card rebuilt around the address.** It was the smallest element on
  the card under a two-line CTA; it is now the largest, with the site's own
  "Check your risk" wording above it so somebody who types the address lands on
  a button reading the words they just saw
- Hold went 2.4s to 4.5s and the fade 0.4s to 0.25s. Everyone who reaches the end
  card has already watched the whole reel, so the cost falls on the most
  interested part of the audience
- The rule under the address is short, centered and teal rather than a full-width
  coral underline. The old treatment read as a hyperlink, and the address is not
  tappable: something that looks tappable and is not is worse than no rule
- **The link sticker turned out to be impossible to automate**, so the pipeline
  now reminds instead. See the note in Open above

### 2026-09-01 (later)
- **The homepage button no longer claims the tool screens you.** "Start
  Screening" became "Check your risk". USPSTF's insufficient-evidence rating for
  oral cancer screening is the sharpest thing a clinician can raise, and the CTA
  was handing it to them on the first screen
- The results disclaimer now says what the screening test actually *is*, a short
  visual and tactile exam, rather than only listing what OralCheck is not. That
  turns a legal-sounding paragraph into a concrete next step
- `/for-clinicians` rewritten for precision, since clinicians are the readers
  most likely to object to the loose usage

### 2026-09-01
- **Cadence is now 2 Instagram + 1 LinkedIn a week**, set by `WEEKLY_PLAN` and
  published entirely through Publora. LinkedIn lands Tuesday or Wednesday
  morning rather than in Instagram's 5pm slot, and gets the rewritten LinkedIn
  caption instead of the hashtag version
- **A post now targets one network instead of every connected one.** Fanning out
  was what made the quota impossible: every network a post targets consumes its
  own scheduled-post slot, so three posts across two networks needed six against
  a cap of three
- Reels never take the LinkedIn slot, since a vertical 9:16 video renders there
  as a small centered box. They take an Instagram slot and LinkedIn waits for a
  post that suits it, falling back only if the week is nothing but reels
- **The Monday run reported success while producing nothing.** It ran out of API
  credits mid-generation, told him "generating 1 post now", then went silent and
  exited 0 with a green check. Failures now reach Telegram with a plain reason,
  and a run where nothing could be built exits non-zero
- Instagram's weekly spread now knows about the LinkedIn slot. Caught by a test:
  both were landing on the same Wednesday of an otherwise empty week

### 2026-08-30 (later)
- **Two gaps closed that a reviewer found before we did.** Dr. Jason Brant's
  reply carried three methodology criticisms. One (oral cavity vs oropharyngeal)
  was already limitation #2. The other two were not on the page at all, and now
  are: that the weights are pooled from studies in different source populations
  and then applied to whoever opens the page, which is the largest single source
  of uncertainty in the score; and that the tier cutoffs were set by judgment
  against reference profiles rather than derived, with no sensitivity,
  specificity, or ROC behind them
- `/methods` now states the threshold provenance outright. It previously
  documented how the boundaries were *anchored*, which is not the same as saying
  where they came from, and a careful reader could have inferred more rigor than
  exists
- The new paragraph is wrapped in `t.has()`. English is written first and the
  translations follow on a separate run, and without the guard an unsynced locale
  renders the literal key path on the page

### 2026-08-30
- **Every SEER figure on the site corrected and consolidated.** Survival 84/38
  became 88.7 localized / 69.7 regional / 36.0 distant; cases 54,000 became
  60,480; deaths 11,580 became 13,150; "one death every 50 minutes" became 40,
  which is now derived from the death count rather than written down beside it;
  men 2x became 2.6x
- **Stage framing corrected.** The site presented SEER *summary* stage figures
  as AJCC "Stage I" and "Stage IV" survival, which attributes one staging
  system's numbers to another. Copy now says localized and distant, and
  `/methods` carries a stage table that says so explicitly
- `src/lib/seerStats.ts` is the single source for the TSX side. The message
  catalogues still hold their own copies, because they are JSON and translated,
  and the file says so

### 2026-08-27 (later)
- **API access restored** (Ian raised the workspace spend limit), which unblocked
  Portuguese, the announcement post, and `/api/summary`. The announcement carousel
  is scheduled on Instagram for **2026-08-28 22:00 UTC**
- **Two questions added, closing the two gaps `/methods` had been listing as its
  own known limitations.** Sex at birth (weight 3) and the combined immune and
  radiation history question (weight 5, Rawal's wording unchanged). Twelve
  questions now, and the count is no longer stated anywhere
- **Tier thresholds deliberately did not move.** The maximum went 53 → 61, and
  rescaling proportionally would have pushed the High boundary to 26, demoting an
  unchanged betel + tobacco + alcohol profile (25) from High to Elevated. A new
  question must not make an existing profile look safer, so the boundaries stayed
  and the reasoning is written on the page
- **`/methods` rewritten**: per-question rationale for all twelve including the
  two weakest links stated as weak (the HPV proxy, and dental visits which are a
  detection proxy and not a risk factor at all), a "What this tool cannot tell
  you" section, and a last-reviewed dateline
- **The results page had been serving English to every Portuguese visitor, in
  two separate places.** `riskEngine` picked its message catalogue with
  `locale === "es" ? es : en`, and `/api/summary` built its prompt the same way,
  so `/pt/results` wrapped translated chrome around English factor labels,
  guidance, and a freshly generated English paragraph that never looked like a
  missing translation. The summary's language table is now typed as a complete
  record over `AppLocale`, so the next language fails the typecheck instead
- Median age at diagnosis corrected 62 → 65 (SEER 2019–2023)

### 2026-08-27
- i18n generalised from bilingual to multilingual: target locales read from
  `routing.ts`, **per-locale snapshots** (one shared snapshot would have made the
  second language skip every changed string), and an explicit translator brief
  per locale so "pt" cannot silently become European Portuguese
- Language switcher is a dropdown; a segmented slider fails at three locales
- `manual_post.py`: queue a hand-written post with no model call in the path, so
  an announcement can say something exact, and the pipeline survives a week with
  no API access
- Announcement carousel built and queued, held until Portuguese is actually live

### 2026-08-24
- **Dr. Yeshwant Rawal's review acted on the same day.** Symptom question now
  includes growth of the gums and recent tooth mobility, both named by him
- Lower risk tiers now carry an explicit caveat that a low score rules nothing
  out, because roughly 1 in 4 oral cancers occur in people with none of the
  conventional contributing factors (25-30% in the never-smoker/never-drinker
  literature). "Your risk profile looks low" was reassuring precisely the people
  it should not. Suppressed when an urgent symptom is reported, so it never
  competes with the urgent banner
- One malformed idea response no longer kills the weekly run: `_extract_json_array`
  salvages per-object, and each format is isolated in `generate_by_type`
- Printable QR section and the disclaimer with Terms/Privacy links on the home page

### 2026-08-18
- Security review: unauthenticated `/api/publish` closed, spoofable rate-limit IP
  fixed, `/api/geocode` metered, CSP added (see the section at the foot of this file)
- Terms of Use at `/terms`, English and Spanish
- **The translation cache bug**: `i18n-sync` compared array-valued keys by
  reference, so all 45 of them (the Terms and Privacy sections, learn-page lists,
  checklists) were retranslated on every single run, forever, on Opus 4.8. A
  no-change run went from 5+ minutes to 0.13 seconds and zero API calls. This was
  the source of the unexplained API spend
- Translation moved to Sonnet 4.6; `/api/summary` given a daily ceiling
- `find_care_click` and QR `?src=` tagging: all five key metrics now instrumented
- Homepage line replaced with cited NCI SEER data, source linked
- Outreach drafts written for Marquette (Bhagavatula, Rawal, Khaled) and the
  seven contacts that had never been emailed

### 2026-08-17
- The sixteen designed templates promoted into `layouts.py` and wired into
  `render_deck`, so the generator can actually select them. They existed only as
  fixed-copy mockups in `template_demo.py`, which nothing imported: every post
  shipped from the five generic shapes, which is why the output looked nothing
  like the approved designs
- `photocompare` resolves two clinical photos from the site's own `/public/signs`
  library, so it no longer depends on the single-image stock fetch
- Review is serial and format-ordered (carousel, then reel, then image), each post
  scheduled before the next is sent
- Rejections name the post they belong to
- Slow steps announce themselves and edit in place when they finish
- Queue directory untracked; stale pending posts pruned after 3 days. Two June
  drafts were committed to git and led every batch for two months
- LinkedIn handoff sends every slide plus a PDF for a native document carousel,
  instead of only the first image
- Booked slots persist in `schedule.json`, so a top-up run spaces posts against
  what an earlier run scheduled instead of restarting from tomorrow and stacking
  two posts onto the same evening
- `test_review.py`: review flow covered offline (ordering, serial review, progress
  messages, rejection labelling, stale pruning, slot spacing), running in CI

### 2026-08-16
- Topical hook finder (`hooks.py`), feeding dated cultural hooks into idea generation
- Six topical, image-carrying templates (16 total)
- Roadmap (this file)

### 2026-08-10
- Reel cover images, chosen by scoring candidate frames rather than a fixed timestamp
- Posts render 4:5 (1080×1350), fixing the profile-grid crop that was cutting headlines
- Ideas generated per format with per-format top-up ("more reels")
- `/help` in the Telegram bot, answered inline wherever it is listening
- Rejection reasons captured and fed into future idea generation as standing rules
- Reels alternate light/dark themes
- Screener completion counted once per screener (was reporting 119% completion)
- Em dash ban applied to English summaries, not only Spanish
- 84% survival stat removed as a hardcoded prompt instruction
- LinkedIn post handoff to Telegram for native scheduling
- Publora 403 diagnosed as a plan quota; quota errors now skip retries and explain themselves
- Post spacing fixed (was scheduling two posts at the identical timestamp)
- Reel hook readable at frame 0 (was blank until ~2.0s)
- Five reel backdrop variants
- Website screenshots as an image source, fixing caption/image mismatch
- LinkedIn banner and square logo
- Review section on `/about`
- Press kit at `/press`
- GA4 stats script (`oralcheck-agent/ga_stats.py`)

### Earlier
- Google Places as primary clinic source, OpenStreetMap fallback (Manhattan 9.2s → 0.5s)
- Find Care map fixed and sped up (40.5s → 1.9s), mock data removed
- Full Spanish translation with an auto-translate pipeline for new content
- NIH self-exam photos on `/learn/self-exam`
- Clinical photos behind an opt-in reveal on `/learn/signs`
- Emoji replaced with Phosphor icons
- Email capture moved to a dialog at the end of the screener
- Resend live on oralcheck.org

---

## Decided against (for now)

| Idea | Why | Revisit when |
|---|---|---|
| AI image diagnosis ("upload a photo of your mouth") | Moves the product into clinical decision support, with a far heavier regulatory and validation burden. Current strength is the low-risk awareness → education → professional care model. | Never, without a clinical partner and a validation study |
| Paying dentists per patient | Wrong incentive; makes a health tool feel commercial | Not planned |
| Buffer as a second scheduler | Free tier has no open API, so posts would be pasted in by hand anyway. No better than the Telegram handoff, plus a second dashboard. | If Buffer reopens API access |
| LinkedIn API direct publishing | Company-page posting needs the Community Management API: restricted to reviewed legal organisations, explicitly not available to individuals | If OralCheck incorporates |

---

## The five numbers worth tracking

Everything else is vanity. Pull with `oralcheck-agent/ga_stats.py`.

1. Screener starts
2. Screener completion rate
3. Share of users landing in elevated/high risk
4. Share clicking through to Find Care
5. Dental practices actively distributing OralCheck

Current (30-day, ending 2026-08-16, excluding the bot spike): **65 users, 33
starts, 30 completions (91%)**. All-time: 728 users.

All five are now instrumented as of 2026-08-18, but three need one manual step
each before they report:

| # | Mechanism | Manual step still required |
|---|---|---|
| 3 | `risk_tier` / `risk_score` sent on `screener_completed` | Register `risk_tier` as a **custom dimension** in GA4 (Admin, Custom definitions). Event params do not appear in reports until registered, and registration is **not retroactive**. |
| 4 | `find_care_click` on the results CTA, tagged with tier | Register `risk_tier` as above; the event itself needs nothing. |
| 5 | `/qr` tags the encoded URL with `?src=<practice>` | Type a name on `/qr` before printing. An untagged code still works, it just cannot be attributed. |

Number 4 is the one that matters most: it is the closest thing the tool has to
"did this send someone toward care", and it is the first thing every partnership
email will be asked to justify.

## Security review, 2026-08-18

Triggered by a traffic spike. Findings and what was done.

| Finding | Severity | State |
|---|---|---|
| `/api/publish` had no authentication. It commits to and deletes from the GitHub repo with `GITHUB_ACCESS_TOKEN`, so anyone could push an unreviewed article live and delete the draft behind it | Critical | Fixed: shared-secret gate, fails closed if `ADMIN_SECRET` is unset |
| `/api/draft` served unreviewed medical content to anyone who guessed a slug | Moderate | Fixed: same gate |
| `getIp` read the first `x-forwarded-for` entry, which is client-supplied, so anyone could rotate their rate-limit bucket per request | Moderate | Fixed: prefers `x-vercel-forwarded-for` / `x-real-ip`, which the platform sets and clients cannot forge |
| `/api/geocode` was an unmetered proxy to Nominatim under our application name | Moderate | Fixed: 20/min limit, 200-char cap on the forwarded query |
| No Content-Security-Policy | Moderate | Fixed: policy added, verified against the running app |
| `uuid` bounds check, via resend/svix | Moderate | Fixed: `npm audit fix` |

Open, with reasoning:

- **`sharp` libvips CVEs (high).** Fix requires Next 16.2.4 to 16.3.1. Not taken yet:
  the CVEs need attacker-controlled image bytes, and `next/image` has no
  `remotePatterns` configured, so `/_next/image` rejects remote URLs (verified:
  400). sharp only ever sees files from `public/`. **This becomes live the moment
  `remotePatterns` is added** — upgrade Next first if that day comes.
- **Rate limiting is in-memory and per-instance.** The real ceiling is
  `limit x concurrent instances`, and it resets when an instance recycles. It
  stops one client hammering one warm instance; it is not a spend cap. The
  durable protections are the provider-side quotas. Swap for Redis
  (`@upstash/ratelimit`) to make the numbers mean what they say.
- **CSP carries `'unsafe-inline'` and `'unsafe-eval'` in `script-src`**, because
  Next hydration and the GA snippet inject inline script without a nonce. It
  still blocks script from unlisted origins, off-site form posts, base-tag
  injection, and framing. Nonce-based CSP is the upgrade.
