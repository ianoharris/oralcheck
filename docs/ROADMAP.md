# OralCheck roadmap

The running list. Two rules:

1. **Nothing gets deleted.** Shipped items move to *Shipped* with a date. Rejected
   ideas move to *Decided against* with the reason, so the same idea does not get
   re-litigated from scratch in six months.
2. **Open items stay open until they are actually done.** An item that was raised,
   half-built, or blocked on something external stays in *Open* with its blocker
   named. This is the list's whole purpose: the things that come up once, sound
   good, and are never mentioned again.

Last updated: 2026-08-17

---

## Open — blocked on something external

| Item | Blocked on | Notes |
|---|---|---|
| Judge whether the reel skip-rate fix worked | A new reel going out | 83.7% skip. Frame-0 fix and cover image both shipped, but only affect reels rendered *after* they landed. The three currently scheduled were rendered before. |
| Trustworthy completion rate over 90d | ~2 weeks of clean events | The double-count fix shipped 2026-08-10. Until then only short windows are reliable. 30-day read at fix time: **91.4%**. |
| Outreach replies | Ian sending them | 7 contacts sit in `outreach-contacts.csv` at status Pending: Penn/CIGOH, Tufts (x2), Columbia (x2), Head and Neck Cancer Alliance, AAOM. Drafts folder is empty apart from a README. |
| LinkedIn auto-publishing | Publora plan | Starter caps 3 active scheduled posts, counted **per platform target**, so 3 Instagram posts fill it. Code already supports LinkedIn: set `PUBLORA_PLATFORMS=instagram,linkedin` and `LINKEDIN_HANDOFF=0` if the plan changes. |

---

## Open — ready to do

### Content and growth

- [ ] **Reels drive follows but not site visits.** Instagram captions are not
      clickable, so the only path is profile → link in bio, and most people will
      not. Two concrete fixes: add a **link sticker on the reel itself**, and hold
      the final scene long enough to actually read the URL. Currently the outro is
      brief.
- [ ] **More post templates.** Twenty-one shapes now reachable (16 designed +
      5 basic). Keep going: the goal is enough that the feed never looks
      repetitive.
- [ ] **Reels have had none of this work.** The sixteen designed layouts are
      carousel/static only. Reels are still the old kinetic-text scenes with
      five backdrop variants, which is the next real design job.
- [ ] Two of six signs on `/learn/signs` still have **no clinical photo**: red patch
      (erythroplakia) and lump/thickening. No openly-licensed image found yet.

### Product and credibility

- [ ] **Tighten the terminology.** *Verified:* USPSTF gives oral cancer screening an
      "insufficient evidence" rating, but that statement is scoped to **primary care
      providers and explicitly not dental providers**. NCI says evidence is inadequate
      that screening reduces mortality. The sharpest framing is not "we are not a
      screening test" but: **OralCheck is a risk-assessment questionnaire; the
      screening test is the clinical exam a dentist performs.** OralCheck's job is to
      get someone to that exam. Worth auditing every use of the word "screening"
      against that.
- [ ] **Make `/methods` exceptional.** It is already cited and 275 lines, and it is
      now linked from the results page. Missing: per-question rationale, the source
      behind each factor, what the tool *cannot* tell you, last-reviewed date, and
      who reviewed it.
- [ ] **Add a "last reviewed" date** to clinical pages. Mayo and NIH do this; it
      converts "someone wrote this once" into "someone maintains this".
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

Current (30-day, 2026-08-10): 35 starts, 91.4% completion. Numbers 3, 4 and 5 are
not instrumented yet.

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
