# OralCheck roadmap

The running list. Two rules:

1. **Nothing gets deleted.** Shipped items move to *Shipped* with a date. Rejected
   ideas move to *Decided against* with the reason, so the same idea does not get
   re-litigated from scratch in six months.
2. **Open items stay open until they are actually done.** An item that was raised,
   half-built, or blocked on something external stays in *Open* with its blocker
   named. This is the list's whole purpose: the things that come up once, sound
   good, and are never mentioned again.

Last updated: 2026-10-26

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
| **Dr. Louise Davies has offered a 30-minute meeting** | Her admin scheduling it, week of 21 Sept or later | **2026-09-14.** Professor jointly appointed in Endocrine Surgery (Surgery) and Head & Neck Surgical Oncology (Otolaryngology) **at UW-Madison**, announced Nov 2025, previously Dartmouth and the VA Outcomes Group. She built the **NCI Oral Cancer Survival Calculator** (seer.cancer.gov/survivalcalculator) and shared it unprompted. She is also the leading researcher on **thyroid cancer overdiagnosis** and served as a subject matter expert reviewer for the **USPSTF on thyroid cancer screening**, plus an IARC task force. That makes her the single person most likely to press the overdiagnosis and USPSTF-I-statement critique, and the single person best placed to supervise a validation. She is at UW, which is where the affiliation question, the faculty mentor gap and the third letter all converge. Do not pitch; ask for critique. |
| Whether UW considers this a university project at all | Ian's academic advisor | **Raised by Dr. Brant, 2026-08-30**, and it outranks the IRB question. Faculty must disclose anything job-related or using university resources, and Brant specifically guessed the source papers were pulled through UW library access. He also questioned whether the site's disclaimer is actually sufficient protection or only reads that way. Ian asserting "this is not a UW project" is not the same as UW determining it. Ask the academic advisor, and ask specifically about (1) what counts as a university resource for an undergraduate and (2) whether the disclaimer holds up. Monetization would raise the stakes on all of it; there is none and no plan for any. |
| ~~Registering GA4 custom definitions~~ | **Done 2026-09-14** | All five are registered, done by hand in GA4 Admin -> Custom definitions, which needs neither the Analytics Admin API nor an Editor grant on the property. Dimensions `risk_tier`, `has_urgent_symptom`, `cta_source`; metrics `risk_score`, `question_count`. `risk_tier` turned out to have been registered since 2026-08-23, so that one has been collecting for three weeks. The other four start from today: GA4 does not backfill, so the window before this is permanently blank. `register_ga_dimensions.py` is kept for the next parameter the site starts sending, and still needs the API enabled to run. |
| A written UW IRB determination | Ian submitting it | The tool stores nothing, so it is almost certainly *not human subjects research* under UW's HRPP, but the assertion is worth having on paper for Marquette's Associate Dean. Free, and Ian can submit it himself. |
| Co-branded Marquette flyer | The approval above | Rawal proposed a design "to reflect our two institutions". Corrected in the reply: OralCheck is not a UW project and cannot carry UW branding. Marquette + OralCheck only. |
| Judge whether the reel skip-rate fix worked | Real engagement data on a reel built after 2026-09-21 | 83.7% skip, measured before any of these fixes. Frame-0 was checked directly against tonight's scheduled reel (2026-09-21, Stoptober): confirmed legible by ~0.1s in the real exported video, so that part is working. The same pass found a separate, real bug and a likely bigger contributor to the skip rate; both are fixed, see Shipped. What is still unmeasured either way: whether any of this moves the actual skip number, which needs a reel built with the fixes in place and real Instagram insights on it. |
| Trustworthy completion rate over 90d | ~2 weeks of clean events | The double-count fix shipped 2026-08-10. Until then only short windows are reliable. 30-day read at fix time: **91.4%**. |
| Outreach replies | Ian sending them | 10 contacts: the original 7 in `outreach-contacts.csv` (Penn/CIGOH, Tufts x2, Columbia x2, HNCA, AAOM) plus 3 at Marquette. **Drafts are written** in `outreach-drafts/` as of 2026-08-18, so the only remaining step is pasting them into Outlook and sending. Update Status to `Followed Up` after each, or the Sunday tracker will generate duplicates. |
| ~~Site's HPV stat corrected to 225%~~ | **Done 2026-10-26** | The homepage said "300% since the 1980s", citing a paper that says 225% from 1988 to 2004. Fixed in all three languages; Ian said "commit and push" on 26 Oct, so it goes live with the next Vercel deploy. |
| ~~Where Ian's three supplied photos came from~~ | **Done 2026-10-26** | The 1 Dec vial and the HPV render and tobacco photo in the 28 Oct LinkedIn image. Ian: "they're free to use". No licence or credit line needed. |
| ~~LinkedIn auto-publishing~~ | **Done 2026-09-01** | Both accounts are connected in Publora with valid tokens. The plan is now `WEEKLY_PLAN=instagram:2,linkedin:1`: each post targets one network rather than fanning out to all of them, which is what made the quota impossible before. Three platform-targets sits exactly at the Starter cap, so raising either number needs a bigger plan. |

---

## Open — ready to do

### Content and growth

- [ ] **Post idea, for later: oral cancer by age (Ian, 2026-10-26: "oral
      cancer incidence by age by 20-30, 30-40...").** A chart post, one bar
      per age band. Source: SEER. Stat Facts gives the share of new cases by
      age band (20 to 34, 35 to 44, 45 to 54 and so on, 2019 to 2023), not by
      decade; decade bands (20s, 30s) need SEER*Explorer's age-specific rates,
      read in 5-year groups and combined properly, not averaged. The figures
      go into `src/lib/seerStats.ts` with the URL and date before any post
      uses them. The honest framing: the young bars are small, which is the
      point to handle with care (HPV-linked throat cancers are the ones rising
      in younger adults, a separate figure).
- [ ] **New post formats, from a look at what works for health-education
      accounts (2026-10-22).** Ian asked for ideas. Proposed:
      1. **Quiz carousels** ("three things in a mouth, one needs a check;
         comment A, B or C, then swipe"). Sample built, not scheduled:
         `oralcheck-agent/queue/20261022_165517_474c3e1a/` (7 slides; the
         caption was edited so it does not give the answer away).
      2. **Comment-to-DM** ("comment CHECK for the screener link"), which
         gets round links not being tappable on posts and reels. **Blocked on
         Ian:** a comment-to-DM tool (ManyChat or similar) connected to the
         Instagram account; the captions can then carry the keyword.
      3. **A weekly series**, same format each week ("one place, one
         minute"), to build the habit of coming back.
      4. **Real questions answered**, one per card, from what people search.
      5. **Collab posts** with dental hygiene students or clinicians, only
         with people who have agreed in writing.
      6. **Trial Reels** (an Instagram setting that shows a reel to
         non-followers first). **Blocked on Ian:** toggled per reel in the app.
      **Blocked on Ian:** say which to add to the calendar. If quizzes, the
      sample can take a slot.

- [ ] **New layered head-and-neck model: built, not yet in the reels
      (2026-10-21).** Ian asked for a full head with every layer, textured,
      realistic, with a see-through option, the mouth and throat, all three
      planes, and pointers that hit the right thing. Built in
      `oralcheck-agent/anatomy3d/` from the whole Z-Anatomy atlas (about 1,100
      structures: skin, generated epidermis/dermis/fat layers, fascia, muscle,
      bone, teeth, cartilage, 240 vessels, 105 nerves, glands, nodes, eyes,
      brain, pharynx, larynx), with procedural tissue textures, capped
      sagittal, coronal and axial cuts, a peel slider, a see-through mode, and
      a stepped skin-layer block. Labels are checked against a GPU id pass: a
      label is drawn only if its dot sits on the structure it names (31 of 31
      in the test gallery). Interactive version:
      https://claude.ai/artifact/ECiso41AwjuW8UstJXWYdV
      - **First look (21 Oct): "lowkey looks terrifying."** Restyled the same
        night to the reels' clinical look: pale grey ground, plaster-white
        skin, desaturated tissue colours, no staring irises, opening on the
        see-through view. Labels re-checked: 31 of 31.
      - **Ian: "drop the skin from the default view" (21 Oct).** Done: it opens
        on see-through, the cut presets open peeled to muscle, Skin is an
        opt-in button. Labels re-checked: 31 of 31.
      - **Ian (22 Oct): the mouth should look real and wet, since that is
        where the cancers are.** Added an open-mouth view (the jaw swings on
        its joints, the tongue bends with it), true-to-life wet tissue with a
        camera exam light, and photo textures Ian generated with ChatGPT for
        the top and underside of the tongue, gums, lips and cheek lining. The
        atlas has no lips, cheek, palate or floor lining; generated versions
        of the cheek, inner lips and floor looked wrong and are hidden, and
        the lips are painted onto the skin instead. Still to do: a tonsil
        texture (Ian hit his image limit), better cheek and floor linings,
        and the soft palate, which is a flat plate in the atlas.
      - **Ian: "fix the missing pieces" (22 Oct). Done the same day.** The
        cheek linings, inner lips and floor of the mouth are rebuilt as
        smooth surfaces swept along the dental arch, measured from the gums,
        skin and tongue, and drawn from the inside only, so the open mouth
        reads as a cutaway; the lower lining moves with the jaw and the
        cheeks stretch. The soft palate is thickened. Swept lips looked like
        loose bands without the face around them, so lips stay painted on
        the skin in the Skin view. All 44 label checks pass. Still open: a
        tonsil texture.
      - **Ian (22 Oct): the back of the mouth cannot be seen from the front,
        it still looks uncanny ("gums without any skin"), the textures look
        weird, and muscle, tissue and vessels look like painted concrete.
        Done the same day.** The concrete look was fine texture flickering
        into grain at viewing distance: every fine pattern now fades out
        before it gets smaller than a pixel, vessels and fat are smooth and
        glossy, muscle is satiny with long fibres. The mouth takes its
        colours from clinical photos Ian sent as references (pale coral gum,
        pale pink tongue with a whitish coat, ivory teeth), is lit like a
        penlight exam, and catches small saliva glints; Ian's ChatGPT
        textures now give only fine detail. The Mouth view now shows the
        face around the open mouth: the skin is parted at the lips, the chin
        and lower lip move with the jaw, and the upper lip lifts. A new "Back
        of the mouth" preset opens wide, lowers the back of the tongue ("say
        ahh") and looks up from below the teeth, as in an exam, onto the
        uvula, the soft palate, the tonsils between their arches and the back
        of the throat. The atlas has no arches, throat wall or proper soft
        palate lining, so those are generated, and its tonsils (small and set
        level with the palate) are moved down into the arches; see
        `ATTRIBUTION.md`. An Open slider and a Show-the-face switch are on
        the page.
      - **Ian (22 Oct): "the main skin texture is so shitty." Done the same
        day.** The stucco was a bump texture, and the plaster white made it a
        mannequin. The skin is now a natural skin tone with soft mottling,
        warmer cheeks, nose, chin and ears, a faint sheen, light bleeding at
        the edges as in real skin, and pores only up close; the eyes have
        soft hazel irises and dark pupils instead of blank sculpted ones.
        Openings in the atlas's skin under the nose and along the smile lines
        are filled, and the inner skin layers no longer show through folds,
        which is what crumpled the skin under the nose. No downloaded texture
        was needed. All 51 label checks pass (31 gallery, 13 mouth, 7 in the
        face and "say ahh" views); the page has no errors on desktop or
        phone. Published as version 6.
      - **Blocked on Ian:** look at the restyled version and say whether
        reels and image posts should move to it.
      - **Then (code):** port `reel3d` to it. Renders take about a second a
        frame on the Mac GPU but would be far slower in software, so reels
        would render locally or on a GPU runner, not the current CPU-only
        GitHub runner.
      - **Known limits:** the outer skin is the atlas's low-detail surface:
        faint seam lines cross the forehead and cheeks, a few thin slits by
        the nose show the lining behind, and the inside of the skull in a
        midline cut is lumpy (the atlas's dura sheet). The open face looks
        right from the front; turned far to the side, the corners of the mouth
        stretch. The skin-layer block
        exists because the real layers are too thin to read on the head.
      - **Reviewed 23 Oct: replace it rather than port it** (see the next
        item and `docs/MODEL_REVIEW.md`). The review found the problems sit in
        the atlas itself (hollow, unclosed shells; generated sheets for the
        cheeks, throat wall and lips), so the "port `reel3d` to it" step above
        is on hold until Ian picks a direction. The artifact stays as it is.

- [ ] **Animated reels: Ian to rate the two samples (2026-10-26).** 2D
      (gauze) and 3D (zoom) in the house style, `oralcheck-agent/anim/`.
      **Waiting on Ian:** keep, change, or drop each, and whether animated
      reels replace some calendar reels. Unpicked ideas, kept for later, all
      checked against the posting history: why a white patch looks white
      (needs a pathology source), habits ranked by risk on a tier board (the
      screener's own sourced weights), what a swallow passes (side view), a
      drone flight over the tongue (3D), watching HPV settle into tonsil folds
      (needs a source on tonsil crypts), and a POV exam-light fly-through
      (overlaps the dental-check posts, ranked last).

- [ ] **Anatomy illustrations: pick the direction (prototypes 2026-10-23).**
      The model review recommends layered 2D illustration in the textbook
      style Ian picked (Blausen), traced from the same atlas, instead of 3D.
      Built: plate A (the open mouth from the front, seven switchable lesions),
      plate B (a side cut-away with a ghost head, switchable "where it starts"
      zones), two 4:5 posts, and two 12-second reels with identical captions,
      one illustrated and one 3D, for comparison. Code in
      `oralcheck-agent/illustration/` (`build_all.py` rebuilds everything).
      Review: https://claude.ai/artifact/6fwVAT9B2fAG7iYq6ffYbj ;
      prototypes: https://claude.ai/artifact/HNkBy65udqitq3m3WhvyRW
      - **Decided 23 Oct: 2D.** Ian: "go 2d". Scope not stated, so both
        plates go ahead as recommended unless he says otherwise. The 3D head
        is retired from future work: no reel port, no site page.
      - **Ian asked (23 Oct) whether a free 3D anatomy would still be cool
        somewhere on the site.** Answer given: not now. People come to check
        their risk and their own mouth; a 3D model adds load time, phone
        trouble and the same uncanny risk without helping them do either. If
        it comes back, the only version worth testing is a small optional
        "turn the mouth" view on one Learn page, off by default behind the 2D
        plate, built from a clean openly licensed mouth model (NIH 3D
        "Mouth, Female", CC BY 4.0) in the same illustration shading, and
        only after the 2D set ships. Parked, not rejected.
      - **Still blocked on Ian:** (2) plate A, plate B, or both (defaulting
        to both); (3) sources only for the lesion
        drawings, or one clinician look at the set before a lesion series
        goes out (recommended; an oral pathologist such as Dr. Rawal could do
        it without his name going on anything); (4) whether it goes on the
        Learn pages (`/learn/signs`, `/learn/white-and-red-patches`,
        `/learn/oral-cancer`).
      - **Done 23 Oct: lesion set redrawn** against the reference photos in
        the review (section 5), on both plates. Plate A: white patch, red
        patch, red and white (speckled) patch, sore that does not heal,
        swollen tonsil, lip sore, and lichen planus on both cheeks as a
        look-alike. Plate B: lumps in the floor of the mouth and at the base
        of the tongue. Each sits at its real site and depth. Still drawings
        by a non-clinician, so the caption line stays.
      - **Done 26 Oct: the reel pipeline and post pictures run on the
        plates** (`reel2d.py`, see Shipped). Thrush added to plate A for the
        wipe-test post.
      - **Then (code):** if wanted, put the plates on the Learn pages (read
        `node_modules/next/dist/docs/` first). Waits on (4) above.
      - **Licence:** traced from Z-Anatomy, so every output is CC BY-SA 4.0
        and carries the credit line in `oralcheck-agent/illustration/README.md`.

- [ ] **The site names UW-Madison in 17+ places, against its own rule (found
      2026-10-21).** The structured data Google reads lists "University of
      Wisconsin-Madison" as Ian's affiliation three times (sitewide in
      `layout.tsx` as the `reviewedBy` of the site, on the self-exam page, and
      as the founder's affiliation on `/press`), and the copy names it in the
      article byline, the About bio and title, the press boilerplate and the
      About page description, in all three languages. AGENTS.md says the name
      must not appear on anything, and the owner's guide tells Ian to say it is
      not a UW project. The structured-data `affiliation` is the strongest
      claim: it tells search engines the university stands behind the page.
      **Blocked on Ian:** whether to remove all of it, or keep "predental
      student" without naming the school. Relevant to the open question with
      his academic advisor.
- [ ] **Link the sources articles attribute claims to (found 2026-10-21).**
      Several published articles credit the ADA, USPSTF, Journal of Clinical
      Oncology and CDC without a link. The claims look accurate and none is a
      quote or endorsement, but the house rule is to cite a real source with a
      link. The stale-figure half of this item shipped the same day, see Shipped.

- [ ] **Article internal links all go to the home page (found 2026-10-21).**
      Links like "oral cancer screening: what to expect" inside the SEO
      articles point at `https://oralcheck.org` instead of
      `/learn/oral-cancer-screening-what-to-expect`. Fix in the markdown (and
      in the generator so new articles get it right). Not blocked; left alone
      during the redesign because another session was editing the article text.
- [ ] **Published articles are missing from the sitemap (found 2026-10-21).**
      `src/app/sitemap.ts` lists only the hand-written pages, so the 11 SEO
      articles rely on Google finding them through /learn. Add them from
      `getAllPublishedArticles()`. Not blocked.
- [ ] **Posting calendar: 30 posts, 27 Oct 2026 to 1 Jan 2027 (started
      2026-10-20).** Ian asked to stop the weekly back and forth and plan the
      whole autumn at once: 3 a week for 10 weeks, 10 reels (3D), 10 carousels
      (original look), 10 single images, reviewed on one page. Instagram Tue
      and Fri 5pm CT, LinkedIn Wed 9am CT, one reel a week. Pinned dates:
      Dental Hygiene Month (27 Oct reel), Great American Smokeout (LinkedIn
      18 Nov, the day before), new year (1 Jan reel).
      - **Done:** `post_calendar.py` (plan, build, review, upload, drip),
        `calendar/calendar.json` with all 30 ideas written, the review page
        template, `.github/workflows/calendar.yml` (daily 13:00 UTC, schedules
        approved posts 3 days ahead through Publora, so the 3-post cap is never
        exceeded), redo notes fed back into the rewrite, decisions tied to a
        post version so a rebuilt post comes back undecided, tests.
      - **Pushed 2026-10-21** (commit 4bba2c7). The daily job ran once by
        hand on GitHub and succeeded (nothing approved yet, so nothing sent).
      - **Review page published 2026-10-21:**
        https://claude.ai/artifact/6EAh4JWYH2K9Jub8ViNshy (decisions are saved
        in its database, collection `decisions`).
      - **Ian's first pass, 21 Oct (23 of 24 shown):** 11 approved, 11 redo,
        1 cut (8 Dec reel, "super boring"). The redos had four causes, all
        fixed the same day (see Shipped, 2026-10-21 late): six single images
        and one carousel with an unrelated stock photo; three reels whose
        highlight did not match the narration (lips, inner cheek, "a red
        patch" lit the teeth or the floor of the mouth); the 3D lips looking
        wrong; and a carousel that needed a picture of the patches.
      - **In progress:** rebuilding the 11 redos with Ian's notes, plus the
        6 posts that were never built (a network drop, then stopped so they
        would not be built with the old code). Then the review page is
        republished and the redone posts come back undecided.
      - **Waiting on Ian:** the redone posts and the last 7 (Dec 18 to Jan 1).
        **The 27 Oct reel is a redo, so it needs a decision by Fri 24 Oct.**
      - **27 Oct reel, again (21 Oct, night):** the early post was glitchy
        (labels jumping sides, gums pointer on a tooth). Both are fixed and
        it is being rebuilt with a hook that only names what it shows.
        **Waiting on Ian:** archive the glitchy post on Instagram, then
        approve the new one before it is reposted.
      - **26 Oct: the redo posts rebuilt on the illustrated plates.** The
        3D model is retired, so every redo, plus the three built posts that
        still carried 3D pictures or reels (28 Oct LinkedIn image, 3 Nov
        image, 1 Jan reel), is rebuilt with the plates: 27 Oct reel, 28 Oct,
        3 Nov, 6 Nov reel, 10 Nov reel (never built before), 13 Nov
        carousel, 24 Nov reel, 25 Nov LinkedIn image, 1 Dec image, 2 Dec
        LinkedIn carousel, 15 Dec image, 1 Jan reel. Each one answers its
        note: the inner cheek now lights the cheek, "redness or a patch"
        stays on the gums, the lips are drawn properly, the tongue carousel's
        picture comes straight after the cover, the wipe-test carousel shows
        thrush beside a white patch, and the look-alikes image shows lichen
        planus. The 1 Dec vaccine image keeps the "photo of a vaccine vial,
        or none" rule from 21 Oct.
      - **Ian cut the 27 Oct reel on 22 Oct** ("it said check your lips and
        highlighted the teeth"), on the 3D version. The rebuild answers that
        note, so it is back on the page undecided; cut it again if the idea
        itself is unwanted.
      - **The 27 Oct reel's date had passed** (Mon 26 Oct). Moved to the one
        open October Instagram slot, **Tue 27 Oct 10am CT**. The plates can
        show all six areas its brief names, so the "promised six, showed
        three" note is answered properly this time. If it is not approved
        by Tue morning, it moves to Tue 3 Nov, the next open slot.
      - **26 Oct, later: 27 Oct reel cut for good.** Ian: "forget the 27 oct
        just push the dates back i left the glitchy one." The glitchy post
        stays live on Instagram; nothing replaces it and the other dates do
        not move. The archive step above no longer applies.
      - **26 Oct, review round 3 (Ian's page notes):** 28 Oct, 31 Oct, 3 Nov,
        6 Nov, 13 Nov, 25 Nov and 26 Nov rebuilt to his notes, 1 Dec uses his
        vial photo; all back on the page undecided (page version 4). Approved
        and kept: 10 Nov reel, 24 Nov reel, 2 Dec carousel. See Shipped.
      - **26 Oct, evening: Brewers World Series carousel added**, Tue 27 Oct
        10am CT (the Instagram slot the cut reel left open; Game 4 is that
        night). "Banned at the Brewers' ballpark since 2016." Waiting on Ian's
        approval on the review page, and on the logo file if he wants it on the
        cover (the slot is built; it renders without one).
      - **Still to decide:** the 15 Dec image still shows the open-mouth view
        of the throat; it could move to the new HPV side view like 28 Oct.
        The reels built before today keep the old monospace look unless they
        are re-rendered.
      - **Then:** upload approved media to the `calendar-2026-fall` release,
        push calendar.json. Media goes on a release rather than into git; the
        repo is public, so approved posts are downloadable from there a few
        days before they go out.

- [ ] **Content engine v2: reels only now; posts went back to the original look
      (2026-10-08, revised 2026-10-20).** Ian's verdict on the feed: videos not engaging enough,
      posts and carousels "kinda lame". Asked what he wanted rather than
      guessing: **fully faceless and automated, $0 extra spend**, all four video
      directions (word-synced captions with fast cuts, explainer animations,
      real photos, quiz and myth formats) and three post directions (big and
      graphic, illustrated guides, creator-native).
      - **Phase 1, the look:** `art.py` (a code-drawn mouth map following the
        site's own self-exam steps, with a tongue-raised pose for the floor of
        the mouth, plus an icon set), `posts2.py` (16 slide templates), and
        `reel2.py` + `align.py` (the whole reel as one timeline, captions synced
        word by word via local faster-whisper, diagrams that react to the word
        being spoken, synthesized sound effects).
      - **Ian's feedback on the samples:** post styles good, voice fine, reel a
        touch fast, the NOPE stamp and the group-chat post off brand, and the
        ideas all sound the same. Acted on all of it: reel slowed (voice 1.12x
        to 1.05x, longer pauses between beats), stamp and chat removed (see
        *Decided against*).
      - **The ideas fix (`topics.py`):** the model used to choose the topic,
        format and wording itself and kept choosing the same five or six
        subjects in the same "X. Y." / "Most people don't know" grammar. Code
        now assigns every slot a topic from a 36-topic bank built from the
        site's own learn pages (least recently used first), a shape (quiz,
        myth, guide, compare, timeline, notes...), and an opening style, never
        repeated within a batch. Titles using the worn phrases get rewritten or
        dropped. The idea step no longer web-searches, which also makes it
        cheaper.
      - **Phase 2, wired in (`engine.py`):** every carousel, image and reel the
        pipeline builds now goes through the new templates. Reels are
        loudness-normalised to -14 LUFS (they were sitting near -28) and get a
        generated music bed. CI installs `faster-whisper`. Tests cover slot
        assignment, the banned-phrase check and spec validation.
      - **Tested end to end on 2026-10-08:** fresh ideas, specs, a rendered
        carousel, image and reel (31s, -14.2 LUFS). That pass caught and fixed:
        a reel that was mostly plain captions (the model asked for icons that
        did not exist; eight icons added, and specs that lean on captions,
        repeat a visual back to back, or use a worn phrase anywhere now get
        one rewrite), a cover hook running into the swipe pill, "2 minutes"
        splitting across lines on the end card, a single-place diagram that
        highlighted nothing, and copy that called a home check a "test".
      - **Pushed 2026-10-08.** First real use was the 19 Oct batch.
      - **Ian's verdict, 2026-10-20: the new style is too playful.** Posts
        (carousels and images) are back on the original renderers
        (`render_html.py`), which he prefers. The topic bank stays: ideas still
        come from `topics.py`, with post shapes renamed to suit the old
        layouts (myth, compare, steps, timeline, bignumber, qualifier,
        checklist, receipt, question), and the brief now carries each topic's
        facts. The "light" tone lane is retired: every slot is written calm
        and clinical. Also fixed: the least-recently-used rotation for shapes
        had never worked (it stored and looked up shapes under different keys).
      - **Reels are 3D now (2026-10-20).** A cleaned-up version of the
        original kinetic-type reel was tried the same day (one still
        background, dissolves, a progress bar) and Ian rated it worse than the
        original, so it was reverted. The original reel stays only as the
        automatic fallback when a 3D render fails. The old renderers stay in the code for one cycle behind
        `OC_ENGINE=v1` as a fallback; delete them once a week has gone through
        cleanly.

- [ ] **3D clinical reels (prototype 2026-10-20, narrated version the same day).** Ian wants videos that
      feel 3D and realistic but stay clinical and minimal, "kinda interactive",
      for $0. Prototype: real anatomy from **Z-Anatomy** (CC BY-SA 4.0, derived
      from BodyParts3D; every tooth, jaw, gums, tongue, soft palate, tonsils,
      floor-of-mouth muscle, salivary glands and neck lymph nodes), trimmed and
      exported once with **Blender** (already installed, run headless with
      scripts disabled), and rendered by **three.js** (MIT) inside the same
      headless-browser frame capture `reel2.py` already uses, so captions,
      voice alignment and audio carry over. Look: matte ivory anatomy on a pale
      studio grey, an atlas-style section cut through the upper jaw, the
      structure being discussed turning teal while everything around it fades
      to glass, a hairline label with a leader line, a tap ripple for the
      interactive feel. Renders at about 2 to 4 seconds a frame in software
      (what CI has), so a 30s reel is roughly 30 to 60 minutes of CI time
      before any speed work. Licence consequence: CC BY-SA means each reel
      carries an attribution line and is itself shared under CC BY-SA.
      **Direction approved 2026-10-20**, with notes (more texture on the bone,
      narration plus sound), all done the same day: procedural bone texture
      (fine pitting, mottling, roughness variation, generated in the shader
      since the meshes have no UVs) with glossier, whiter enamel; and
      `reel3d.py`, which builds a narrated reel from a list of shots (one
      spoken line plus a focus each: overview, tongue, floor, lips, gums,
      teeth, throat, nodes, glands, end card), with preset camera moves,
      word-timed captions and quiet clinical sound. Ian on the narrated
      sample: "great". **Wired into the weekly run the same day**: reels
      default to 3D (`REEL_ENGINE=3d`), the content step writes the shot plan
      from the topic's facts and may only point at the structures that topic
      is about (`topics.TOPIC_FOCI`), and a failed render falls back to the
      original reel. Fixed on the way: hidden structures (lips, nodes, glands)
      showed on a reel's first shot, because `visible` was `undefined` rather
      than `false`; fonts are now bundled so a slow Google Fonts request can
      no longer stall a render; CI renders a real 3D frame on every run.
      Assets and licences in `oralcheck-agent/reel3d/`. **Not pushed yet.**
      Still open: render speed (about 10 minutes for 22s locally, likely
      double on CI) and the interactive formats (see below).

- [ ] **Interactive 3D reel formats (proposed 2026-10-20).** Four ideas, all
      clinical rather than gimmicky: (1) *Do it with me*, the 3D mouth walks
      the 8 self-exam steps with a countdown ring so the viewer checks along in
      real time; (2) *A, B or C*, three pins on the model and "comment your
      letter" before a tap reveals the answer; (3) a *screener walkthrough*, a
      finger tapping through the real oralcheck.org screener on a phone; (4)
      *drag to day 15*, a slider across a 14-day calendar. 1, 2 and 4 reuse
      `reel3d.py` directly. **Blocked on Ian picking which to build.**

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
- [x] ~~Reels have had none of this work~~ — **done 2026-09-01.**
      `reel_scenes.py` adds six scene archetypes (splitstat, contrast, checklist,
      quote, term, enumerate) mapped to the content pillars, validated before
      render and de-duplicated within a reel. Note that their tests did not
      actually run on the runner until 2026-09-08: the import that reached them
      was killing the process first.
- [x] ~~A photo for the red patch (erythroplakia)~~ — **decided against
      2026-09-01.** The one Ian found is all rights reserved and he does not want
      to chase permission for it, which is a reasonable call: the sign already has
      an illustrated diagram and a photo is an upgrade, not a gap. Both remaining
      signs keep their diagrams. Reopen only if an openly licensed image turns up
      incidentally; do not go looking.
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

- [ ] **Pages with fade-in animations can render blank for visitors who turn
      on "reduce motion" (found 2026-10-21, while testing the learn page).**
      With reduced motion on, `FadeUp` and the learn cards render differently
      on the server and in the browser, React reports a hydration mismatch, and
      in a headless Chrome the `/learn` content stayed invisible, on
      oralcheck.org as well as locally. Needs a check in a real browser with the
      system setting on, then a fix in `src/components/FadeUp.tsx` and
      `AnimatedLearnCards.tsx`. Not blocked.
- [ ] **Two more screener citations that do not match their source (found
      2026-10-08, while fixing the figures below).** Same pattern as the ones
      fixed that day, but the fix is a judgment about the number, not just a
      journal name, so it was left for its own pass. (1) The tobacco question
      says smokeless tobacco carries 4 to 5x risk and credits Gandini 2008,
      which is a meta-analysis of *smoking* only. (2) The HPV question says
      "OR ~15x" and credits Gillison 2008; the ~15x figure looks like D'Souza
      2007's oral HPV-16 infection result (OR 14.6). Both need the source read
      and either the number or the citation changed, in all three languages.
      Not blocked.
- [ ] **Was `OralCheck_ADA_Briefing_v2.md` sent to anyone?** On Ian. Its
      reference list had the same wrong journals as `/methods` (Gandini, Bagnardi,
      Gillison, Pavia) and it said the combined tobacco plus alcohol OR was
      "approximately 35x" per Hashibe 2009, which is that paper's larynx
      figure. The repo copy is corrected. If a copy went out, the corrected one
      is worth resending with a one-line note; reviewers who check a citation
      and find it wrong stop trusting the rest.
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
      answer. **What the sensitivity analysis adds (2026-09-14):** no published OR
      exists for the self-report proxy, so the honest weight is unknown. Scored at
      the D'Souza 2007 OR for confirmed oral HPV-16 infection (14.6, weight 12) the
      young HPV-history profile is still moderate on 77% of draws; only at the
      seropositivity OR (32.2, weight 16) does it reach elevated reliably. Raising
      the weight to 12 moves it one point short of the band, not into it.
- [ ] **Open, and it needs a biostatistician as much as a clinician: the tobacco
      anchor and two other weights disagree with the meta-analyses.** From
      `docs/SENSITIVITY_ANALYSIS.md`. The anchor OR of 6.0 for daily tobacco is above
      the upper bound of both oral-cavity meta-analyses (Possenti 2026: 3.39, 2.64 to
      4.35; Gandini 2008: 3.43, 2.37 to 4.94); it is inside Gandini's *pharyngeal*
      interval, so it is a pharynx number scaling a mostly oral-cavity instrument.
      Past betel is weighted 4 where the former-chewer OR (Gupta 2022: 6.87) implies
      9. Occasional tobacco is 5 where the closest INHANCE category (Berthiller 2016:
      1.48) implies 2. Re-deriving the scale from the published tobacco OR inflates
      every other weight by about half and the current boundaries no longer mean what
      they were designed to. Three decisions are needed, none of them code: which
      tobacco OR the anchor should rest on, whether the boundaries float with it, and
      how "daily" and "occasionally" map to grams and cigarettes per day. Do not
      re-weight unilaterally; the betel + tobacco + alcohol profile's place in High
      depends on the alcohol mapping and that is a judgment call for the reviewers.
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

- [ ] **The Monday run dies at 6 hours and loses whatever it built (found
      2026-10-20).** GitHub-hosted runners stop every job at 6 hours; the
      workflow's `timeout-minutes: 840` is ignored. Waiting for picks (up to
      6h on its own) and the Telegram review share that one job, so every run
      since early October ended "cancelled". 12 Oct: no picks arrived, nothing
      built. 19 Oct: three built, the carousel rejected, then the run was
      killed mid-review and the built reel and image went with it. Nothing new
      scheduled either week. Fix: split picks and review into separate jobs
      (each gets its own 6h) and carry the queue between them as an artifact,
      or let review resume in a later run. Not blocked. **Worked around
      2026-10-20:** the Monday crons are paused (dispatch still works) and the
      autumn runs from the posting calendar, which builds locally and only
      uses CI for a short daily scheduling job. The real fix is still needed
      before the weekly flow is switched back on in January.

- [ ] **Meta Graph API** for direct Instagram publishing, removing the Publora
      dependency and its 3-post cap. Needs a Facebook app, a linked Business
      account, and token refresh handling.
      - **Code built 2026-10-26, switched off.** Ian: "we need to connect meta
        api so i dont get limited by publora". `meta_ig.py` publishes pictures,
        carousels and reels with Meta's own API (100 posts a day, so no
        practical cap); `post_calendar.py publish` sends each approved
        Instagram post at its time, every half hour
        (`.github/workflows/publish-instagram.yml`), because Instagram's API
        cannot schedule. Publora keeps LinkedIn. A weekly job refreshes the
        token (`meta-token.yml`). Everything stays off until the repo variable
        `IG_DIRECT` is 1. Tests cover what is due, what is too late, the
        switch, and caption limits.
      - **History:** the same idea failed in July with Meta's "(#10)
        Application does not have permission" on a Facebook Login token, and
        posting moved to Publora that day. Meta has since added Instagram
        Login, which needs no Facebook Page, and the new code defaults to it.
      - **Blocked on Ian** (no code): create a Meta app with the Instagram use
        case, add the OralCheck Instagram account (it must be a Business or
        Creator account), generate a token there, and paste the token and the
        Instagram user ID into the repo's secrets `INSTAGRAM_ACCESS_TOKEN` and
        `INSTAGRAM_USER_ID`. (`SECRETS_WRITE_TOKEN`, the GitHub token the
        weekly refresh uses to store the new token, was set by Ian on 26 Oct.)
      - **Then:** run "Diagnose Instagram Token" (it checks the account and
        quota, and has Meta prepare one real picture and reel without
        publishing), and only if both pass, set `IG_DIRECT` to 1.
      - **Watch:** GitHub starts scheduled jobs late. The daily calendar job
        set for 13:00 UTC has been starting between 16:25 and 19:00. If the
        half-hourly publish job is late in the same way, posts go out late;
        check the first week's actual post times.
- [ ] Rotate the Google Places API key. Low priority: it is restricted to Places
      API (New) with a daily cap, so the blast radius is small.

---

## Shipped

Newest first.

### 2026-10-26 (night): approved posts finally uploaded; daily job fixed
- **Nothing had been handed to Publora since the calendar was pushed.** The
  media release CI downloads from (`calendar-2026-fall`) had never been
  created, so the daily job crashed on the first approved post (Thu 29 Oct
  carousel) and scheduled nothing. Found while checking the release for the
  Meta work. The release is now created and all 14 approved posts are on it.
- **The daily job no longer dies on one bad post:** it logs it, tells Ian on
  Telegram, and carries on with the rest.
- **Not fixed by this:** the daily job starts hours late (see the Meta item),
  so a post approved the night before its date can miss its slot. Tomorrow's
  two posts (Brewers carousel, HPV LinkedIn image), approved tonight, need the
  calendar pushed and the job started by hand. Ian said go; pushed (c3c997c)
  and run by hand at 22:50 UTC: **the Brewers carousel (Tue 27 Oct 10am) and
  the 29 Oct carousel are scheduled in Publora.**
- **The HPV LinkedIn image was not scheduled: Publora's LinkedIn connection
  has expired.** Blocked on Ian: reconnect LinkedIn in Publora, then run the
  "OralCheck Posting Calendar" workflow again before 10am CT Tuesday (or
  that post waits for a new date). The error message now says an expired
  login plainly instead of "no connected account matched".
- Ian's page decisions applied: approved the Brewers carousel, 28 Oct, 31 Oct
  and 3 Nov (18 approved in all, all uploaded). New redo on 1 Dec ("make the
  background white the same color as the background of the vial image's
  white"): photo cards now take the photo's own white as their ground when it
  sits on plain white (`render_html._photo_ground`); 1 Dec rebuilt, back on
  the page undecided.

### 2026-10-26 (night): Brewers World Series carousel
- Ian asked for a Brewers post (Brewers lead the Rays 2 to 0) and picked
  "banned at the Brewers' ballpark since 2016" from three pitches. Eight
  slides: Milwaukee's November 2016 ban on smokeless tobacco at every city
  sports venue, 14 to 1, backed by the Brewers (WUWM); MLB's ban for new
  players nine days later (Sports Illustrated); why (NCI: causes oral cancer);
  where to look (ACS: leukoplakia is often found where it sits between the
  teeth and gums); and the two-week check.
- **A Brewers theme** in `render_html` (navy and gold, drawn baseball seams,
  the brand teal kept for the address), picked by an occasion naming the
  Brewers or the World Series. Covers can now carry a logo and a small note.
- **Team marks:** Ian chose team colours and the logo and took on the
  trademark risk. The cover and caption say the post is not affiliated with
  or endorsed by the Brewers or MLB, which keeps the no-implied-affiliation
  rule. The ballpark photo is a stock photo of American Family Field.
- **A white patch on the lower gum** added to plate A (`lesion-whitegum`,
  in `build_plate_a.py` and the pipeline's copy), where dip is held.

### 2026-10-26 (evening): Ian's third review round, the HPV figure, a new look
- **28 Oct LinkedIn image** ("low quality, intimidating"): now the side view
  with the base of the tongue and tonsils tinted ("Where HPV throat cancers
  start"), and the zone follows the curve of the tongue instead of a straight
  cut. Every plate still is now rendered at twice the size, which was the
  real cause of the soft pictures: a 1080 picture was being stretched to 1440.
- **31 Oct and 26 Nov holiday carousels** ("last slide not same theme, low
  quality"): the closing slide now carries the holiday's own theme.
- **3 Nov image** ("no picture, design the cover nicely"): a designed list
  card of six throat symptoms, no picture. **25 Nov** ("I don't see the 5
  things"): the same card listing the five look-alikes, caption trimmed to
  what the sources say.
- **6 Nov reel** ("audio too loud, no patches shown"): the patches are now
  drawn on the inner cheek and the side of the tongue. Two fixes made that
  work: the cheek has its own white and red patch drawings, and a bare
  "patch" now counts as a white patch.
- **13 Nov carousel** ("this idea is dumb"): swapped to the lower lip and the
  sun, a did-you-know, trimmed to the facts in `topics.py`.
- **1 Dec image**: Ian's own vial photo. **27 Oct reel**: cut (see Open).
- **28 Oct LinkedIn image, again** (Ian supplied an HPV render and a tobacco
  photo: "make the design nice"): a new side-by-side card,
  `render_html.versus_image`. Each photo carries its figure from Chaturvedi
  2011: HPV-positive throat cancers up 225%, HPV-negative ones (the kind linked
  to smoking) down 50%, 1988 to 2004. Drawn arrows, not +/- signs, since the
  serif minus reads as a dash. The plate credit came off the caption.
- **Music lowered again**, to 24 dB under the voice (was 18). Tested.
- **The HPV figure was wrong.** The topic fact and the site's homepage stat
  said HPV-positive throat cancers rose "300% since the 1980s", citing
  Chaturvedi 2011, which actually reports **225%, from 1988 to 2004**
  (HPV-negative fell by half). Corrected in `topics.py`, the writer's prompt,
  and `messages/en.json`, `es.json`, `pt.json`. Committed and pushed the same
  evening, with everything else from today.
- **A new look for reels and animations** (Ian: "so claude code looking"):
  monospace, uppercase tracking and step counters are gone; titles, labels
  and numbers are in DM Serif Display, everything small in Source Sans 3,
  the same as the site. Applies to `reel2d/scene.html` and `anim/house.css`.
- **Animation fixes:** the 3D jaw showed a second tongue when it opened (the
  upper gum swung down with the jaw); the gum mesh is now split at the bite.
  Cells have dark edges so each one reads. The 2D tongue's side wall only
  shows on the trailing side. All three are rules in `anim/STYLE.md`.
- **Photo search:** stock results whose labels are readable (a COVID vaccine
  brand passed once) are now rejected.
- **Review page republished** (version 4) with each rebuilt post undecided.

### 2026-10-26: reels and post pictures move to the illustrated plates
- **`reel2d.py` replaces `reel3d.py`** in the weekly run and the calendar.
  Same plan format (shots, each a spoken line and a focus), so the writer and
  the calendar did not change shape. `reel2d/scene.html` inlines both plates
  and moves a viewBox camera between foci, tints the subject teal (plate B's
  own zones, or a shaded copy laid just above the part on plate A so the
  teeth stay in front of the tongue), crosses over to the side view for the
  floor of the mouth, base of the tongue and roof of the mouth, and keeps the
  3D reel's captions, label, tap, sound and end card. Renders a 30-second reel
  in about 3 minutes without a GPU.
- **Signs follow the words.** A line naming a sign (white patch, red patch,
  sore, lump, speckled, thrush, lichen) shows its drawing at the place the
  line names, and never somewhere else; the footer "Illustration for
  education, not a real case. Not reviewed by a clinician." shows whenever
  one is on screen. New foci the 3D model could not show: lips, cheek,
  tonsils, base of the tongue, roof of the mouth.
- **Post pictures** (`topics.VISUAL`): "3d" stills became "plate" stills,
  optionally with a sign, and a new "pair" picture puts two signs side by
  side (wipe test: thrush, which wipes away, beside leukoplakia, which stays
  put). Look-alikes get lichen planus; lip, red patch, painless, two-week,
  edges and canker topics get their sign. Carousels now put the picture
  straight after the cover (Ian on the 13 Nov carousel).
- **Thrush drawn** on plate A (`lesions.thrush`), from the CDC's
  description; the illustration README says how to refresh the pipeline's
  copies of the plates.
- Tests: the reel content tests now cover Ian's three mismatch notes against
  the plates, the sign matching ("won't wipe away" is a white patch, "wipes
  away" is thrush), and that no picture is a retired 3D still; the render test
  checks the 2D scene draws, labels hold still, and every named sign exists on
  its plate. All pass.
- Docs: the owner's guide's reel and picture sections rewritten.
- Earlier today: the fork's review, the Mon/Tue/Thu 10am schedule and the
  retired 3D work were committed and pushed (master 7634ba0), so the new
  posting times are live for the daily job.
- **Review page republished** (https://claude.ai/artifact/6EAh4JWYH2K9Jub8ViNshy,
  version 3) with every rebuilt post undecided and Ian's 11 approvals kept.
  Review copies are now stored per version, so a rebuilt post can never show
  its old video. The heading no longer counts posts.
- **Caught while checking the rebuilds, and fixed in code:**
  - The 2 Dec carousel captioned the ulcer photo (`sore.jpg`, no attribution
    on file) as "oral thrush". A photo pair may now use only the two
    attributed photos, and each label must name what its photo shows, or the
    slide is dropped (tested). The rebuild tried the same mislabel with the
    leukoplakia photo and was dropped too. Its "day 3 to 5, thrush often
    resolves" timeline had no source and was removed.
  - The 27 Oct reel's caption again named six places while the shots showed
    three; the writer now rejects a caption or hook naming a place no shot
    shows. Rebuilt: four places shown, four named.
  - A line naming no place used to keep whatever place the writer picked (the
    6 Nov reel labelled the lips on "if a patch is still there"); it now shows
    the topic's own place (`topics.home_for`) or the whole mouth. "Under your
    jaw" now means the neck (1 Jan reel).
  - Two carousels crashed on a calendar idea with no occasion (`null`); fixed.
- **Music was too loud** (Ian, on the gauze sample). The bed was a fixed 0.11
  of whatever level the track arrived at; generated tracks are mastered up to
  9 dB hotter than the bundled one, so they played 6 to 10 dB under the voice.
  `reel2._final_audio` now measures both and seats the music 18 dB under the
  voice. Today's five rebuilt reels and both samples were re-mixed (all at
  -14 LUFS overall).
- **Animated reels: house style and two samples** (Ian: animation gets views;
  his 3D skull reel doubled his average). `anim.py`, `anim/house.css`,
  `anim/house.js`, `anim/STYLE.md`. Samples in `oralcheck-agent/anim/samples/`
  (not in git): `gauze.mp4`, 2D, "why does your dentist grab your tongue
  with gauze?" (NIDCR exam card, step 6), and `zoom.mp4`, 3D, a zoom from the
  jaw into the squamous lining and back out (ACS: almost all oral cancers are
  squamous cell carcinomas). Ideas were picked by Ian from a list checked
  against everything already posted, after he pointed out the first two
  pitches (a stadium crowd, the two-week sore) were played out.

### 2026-10-21 (late night): 27 Oct reel rebuilt
- Rebuilt with the label fixes. The first rebuild switched the gums shot to
  the tongue, because the gums pattern matched "gum" and "gums" but not
  "gumline" ("run your tongue along your gumline"); the pattern and a test
  now cover it. Its caption also claimed the gums were where most early
  cancers show; the new caption names the sides of the tongue and the floor
  of the mouth. Checked frame by frame and sent to Ian. **Not reposted:**
  waiting on Ian to archive the glitchy post and approve this one.

### 2026-10-21 (night): 3D reel label fixes, after the glitchy 27 Oct post
- **Ian: "the text boxes moved side to side and the arrow ... pointed at the
  teeth."** Two causes. The label chose its side of the screen every frame
  from where the subject was, so a camera drifting across the middle flipped
  it back and forth; it now chooses once per shot, from where the camera
  settles. The gums pointer aimed at the centre of the gum mesh, which wraps
  the teeth, so it landed on a tooth; it now aims at the front of the lower
  gum and follows the jaw. The same check found the salivary-glands pointer
  floating between the two glands; it now picks the near one.
- **How it got through:** only still frames were checked before posting. A
  new render test plays every labelled shot and fails if a label moves; it
  fails on the old code (tongue, gums, throat) and passes now.
- The 27 Oct reel goes back to redo with the hook changed from "six things"
  to "these" and a note to name only what the model shows.

### 2026-10-23 (evening): lesion set redrawn on both plates

- Ian chose 2D ("go 2d"). The lesion drawings, the roughest part of the prototypes, were redrawn against the openly licensed reference photos listed in `docs/MODEL_REVIEW.md` section 5 and checked side by side with them: a filmy, mottled white patch; a flat, velvety red patch; a new red and white (speckled) patch; a sore with a pale raised rim, raw base and yellow slough instead of a fried-egg look; a lobed, swollen tonsil; a scaly lip border with a crusted sore; and new lichen planus (a lacy web on both cheeks) as a look-alike. Plate B gained a floor-of-mouth lump and a base-of-tongue lump at the right depth.
- Code: `oralcheck-agent/illustration/lesions.py`. Prototypes artifact republished with all seven lesion buttons and their sources.

### 2026-10-23 (later): model review delivered; illustration prototypes

- Ian answered the review's opening questions: the rendered textbook look (Blausen) over photoreal 3D; none of the current looks; teach where it starts plus credibility with clinicians; mainly Instagram; a faded side silhouette for the face; illustrated, switchable lesions checked against published photos only; one-off payment if anything is bought; prototype both scopes and both motion styles. The brief with his answers is `docs/MODEL_REVIEW_BRIEF.md`.
- Review: `docs/MODEL_REVIEW.md`, pictures in `docs/model-review/`, artifact https://claude.ai/artifact/6fwVAT9B2fAG7iYq6ffYbj. Verdict: the model's problems are in the Z-Anatomy data (cutting it down the middle shows open shells, block-like nasal lining and slivers; the mouth is mostly generated sheets), so more shader work will not make it professional; 2D illustration is the better tool for this site.
- Prototypes: `oralcheck-agent/illustration/`, artifact https://claude.ai/artifact/HNkBy65udqitq3m3WhvyRW. Outlines traced from the atlas; the soft palate, lips, uvula, tonsils, pillars, cheeks and throat wall redrawn by hand. Both reels share captions; the end line uses the site's "more than two weeks" wording (ADA, Oral Cancer Foundation). Every frame says "Illustration for education, not a real case. Not reviewed by a clinician."
- Licensing research: Blausen plates are CC BY 3.0 (free, edits allowed, credit only); BioDigital, Visible Body and Complete Anatomy need paid permission for social posts; Netter web use expires after a year; one-off 3D models are $50 to $250 but bar AI use; commissioning runs about $500 to $3,400 a plate. OpenStax A&P 2e is now CC BY-NC-SA, not CC BY.
- Side finding: `oralcheck-agent/venv` is Python 3.14 with a numpy built for 3.13; nothing imports numpy there today.

### 2026-10-23: skin removed from the head model; review briefed

- Ian: "ok just delete the skin layer its honestly too terrifying". The skin, the fat under it and the lashes and brows are left out of the model file (`SKIN_IN_MODEL = False` in `export_head.py`; they are still built, because the mouth linings are fitted against the skin). The model dropped from 14 MB to 10.7 MB.
- Page: the Skin button, the "show the face" switch and the Lips preset are gone; the peel slider runs Muscle, Bone, Deep; the mouth presets are cutaways; the inner-lip linings are hidden in the whole-head view (they floated in front of the teeth). Labels: mouth 12 of 13 (the miss is the old Lips-on-skin check), gallery 29 of 31 (the same known bone-layer shot). Model republished (v9). Demo video re-recorded without the skin.
- Ian: the model "lacks depth, realism, and is uncanny / doesn't look professional", and "there might be a better solution". A brief for a full review is at `oralcheck-agent/anatomy3d/MODEL_REVIEW_PROMPT.md`: ask Ian questions first, study professional anatomy references online, list every issue with its fix, weigh fixing the Z-Anatomy pipeline against a licensed model, a stylised look, 2D illustration or a mouth-only scope, write directions for use, and plan a page on oralcheck.org. Offered to Ian as a task chip to run on Opus 5.5 at max effort. Done the same day: see the entry above.

### 2026-10-22 (late): neck, chin and smile-line marks fixed; demo video

- Ian: "fix the neck and chin marks first and the smile lines, then make the demo video".
- Cause: the atlas skin is a hollow shell about 3 mm thick, made of pieces that do not quite meet. Where it thins (chin and neck midline, sides of the neck, the folds from nose to mouth) the rebuild fused its two layers in patches, leaving pits, pleats and slits.
- Fix in `export_head.py`: thicken 2.5 mm each way so the layers fuse fully and the gaps close, then step back along the normal and snap onto the atlas skin where it is within 0.6 mm. The ears, eyes and nostrils are thickened only 0.6 mm and not stepped back (stepping back tore the ears). Also: the slit beside each nose wing now gets the full treatment, holes are closed regardless of height (small neck holes were being taken for the neck cut), leftover inner lining deep behind the teeth is removed, the jaw rig's fades are longer (they folded the skin at the angle of the jaw), and the lips part with a 0.1 mm gap (wider showed the teeth as a white line).
- Several attempts on the way made things worse (blobby smile lines, scattered dark flecks, torn ears, a hole beside the nose); each was reverted. The final build was checked by eye from the front, both sides, below the chin, the ear, the eye, the open mouth and "say ahh", and by casting rays across the neck and nose creases.
- Label checks: mouth 13 of 13 pass; gallery 29 of 31. The two failures are an old gallery shot that labels a nerve and an artery on the bone-only layer, which hides them by design since Ian's 22 Oct request; no published preset does that.
- Still rough: the underside of the nostrils seen from below, and two faint marks under the lower lip where the atlas slit was sealed. Logged under the head model item.
- Model republished (v8). Demo video: `oralcheck-agent/anatomy3d/stills/oralcheck_head_demo.mp4` (70 s, 1920x1080), recorded by `demo_video.py`.

### 2026-10-22 (evening): lips placed by Ian on the head model

- Ian: "the lip color is below the actual lip surface", then "let me adjust where the lips are and the mouth opening is myself". He set them with a private lip tuner (https://claude.ai/artifact/CJtRLTGNetc53Wyq3xz65o): the lips meet 14.5 mm above the slit the atlas skin has for a mouth, colour 9.5 mm up, 12.5 mm down, 31 mm half width.
- The atlas's slit is now sealed for good (edges drawn together and welded, the crease smoothed), and the skin is parted on Ian's line (`STOMION` in `export_head.py`, `LIP_LINE` in `src/main.js`). The upper lip now only lifts 3 mm when the mouth opens, since the upper teeth end just below the new line.
- Fixed the pink slivers that hung across the open mouth: the cut along the lip line had gaps wherever the bisect landed on an existing vertex, and the jaw rig moved those points halfway. Every edge between an upper and a lower face is now split and every point near the line is pushed onto its own lip. Checked by counting stretched triangles; the only ones left are at the corners, where the cheek is meant to stretch.
- Model republished (v7). Renders: `oralcheck-agent/anatomy3d/stills/lips_22oct.jpg`.
- Still to tidy: a faint mark where the old slit was sealed, dark specks on the sides of the neck, and a dotted line under the chin.

### 2026-10-22: posting moved to Mon/Tue/Thu 10am Central
- **Ian: followers are most active 9am to noon CDT on Mondays, Tuesdays and
  Thursdays; post then, except holidays.** Every regular calendar post (27 of
  them, through 29 Dec) moved, in order, to the next free Monday, Tuesday or
  Thursday at 10am Central, one per day. Holiday posts kept their slots
  (Halloween, the Smokeout's "tomorrow" post, Thanksgiving, New Year). Future
  batches plan Instagram Mon and Thu, LinkedIn Tue, all 10am Central; the
  calendar test checks the days and hour. **Blocked on Ian:** the daily
  GitHub job reads the calendar from the repo, so the new times take effect
  once it is committed and pushed.

### 2026-10-22: reach stat updates hourly; holiday posts themed
- **Ian: the "people reached" number hasn't updated.** The home page was
  prerendered once per deploy, so it showed 855+ from deploy day; the
  one-hour cache only applied to the GA read, which only ran at build. The
  page now declares `revalidate = 3600`; the build's route table shows `/en`,
  `/es` and `/pt` revalidating every hour. Pushed as `ae1aa0a` at Ian's
  request. After the deploy the site still read 855+, and so did GA itself
  (all-time users, read directly): GA's totals lag a day or two, so the number
  moves when GA's does, within the hour.
- **Halloween made "a little spooky" and a Thanksgiving post added (Ian).**
  Slides can now render in seasonal worlds: a Halloween night theme (moon,
  bats, a cobweb, pumpkin-orange accents) and a fall theme (warm paper, maple
  leaves), picked from the post's occasion and drawn behind the text so
  legibility is unchanged. The Halloween carousel (Sat 31 Oct, 5pm CT) was
  rebuilt with a lightly spooky hook ("Some things look frightening. One looks
  like nothing."). New: a Thanksgiving carousel for Thu 26 Nov, 5pm CT, the
  two-minute self-exam ("Before the leftovers, two minutes and a mirror."), 8
  slides. Note it lands the day before the 27 Nov low-cost-care carousel.
  **Blocked on Ian:** approve both on the review page.

### 2026-10-21 (evening, later): live reach stat, early reel, Halloween post
- **Home page: "2 min" became a live "people reached since launch" stat**,
  read from GA's total users on the server and cached for an hour, shown as
  "847+" with a "Live, updated hourly" label. Ian added the two Vercel values;
  verified on oralcheck.org after the deploy.
- **The 27 Oct reel was posted early, on 21 Oct, at Ian's request**, after a
  3D rebuild with his note applied (gums, sides of the tongue, floor of the
  mouth, each lit as named). Its first rebuild had timed out while the site
  build was using the CPU and silently fell back to the classic reel Ian rated
  "meh"; calendar builds now retry a failed 3D render instead, and frames get a
  5-minute timeout. Known weakness left in: the hook says "six things" and the
  model can show three (the caption lists all six).
- **Halloween carousel added for Sat 31 Oct, 5pm CT** ("Some things in your
  mouth look frightening. The one that matters looks like nothing."), built
  from the look-alikes and painless-signs facts, Halloween as framing only.
  Waiting on Ian's approval on the review page.

### 2026-10-21 (late night): analytics unblocked; article pages and fixes live
- **Google Analytics was being blocked by the site's own security policy.**
  GA4 sends page views to `analytics.google.com` and `www.google.com`;
  `connect-src` allowed only `*.analytics.google.com`, which never matches the
  bare host. The policy dates from 18 Aug, but GA kept counting until Google's
  tag moved to that address around 22 Sep. Measured against Vercel Analytics
  (unaffected): 21 Sep GA caught 18 of 20 page views; 22 Sep to 20 Oct it
  caught 32 of 285 (about 11%). Real traffic held at roughly 10 page views a
  day, so the GA "users drop" Ian saw from late September is mostly a
  measurement failure, not lost visitors. Now `*.google.com`, per Google's tag
  platform CSP guide; a live page view was seen reaching
  `analytics.google.com/g/collect` after the deploy.
- **Journal-style article page and the article figure fixes merged and
  pushed on Ian's go.** The live articles now use summary-stage wording and
  the seerStats figures.

### 2026-10-21 (night): results and Learn pages live
- **Merged and pushed on Ian's go**, after a clean production build. The
  `/results` cleanup: next steps straight after the result, one booking
  button per band, a visible gauge track, share and retake as quiet links
  (`results_primary_cta` no longer fires on elevated and high). The `/learn`
  page: 2 rows of 3 guide cards (Facts & Stats, HPV and Prevention came off
  the grid, their pages untouched) and the 5 newest articles with Load more.
- Still open from that work: on a symptom result the gauge shows a low green
  score beside a red "see a dentist soon" badge; /learn renders blank with
  "reduce motion" on.

### 2026-10-21 (evening): SEO keywords and a grounded article writer (pushed 21 Oct)
- **37 new SEO keywords** (51 in all), from Google autocomplete for oral
  cancer search terms: look-alikes ("leukoplakia vs thrush", "geographic
  tongue vs oral cancer"), throat and neck ("lump in neck under jaw"),
  common questions ("is oral cancer painful"), risk factors and screening
  ("oral cancer screening light"). Telegram had been saying the list was
  used up. Skipped on purpose: pet, billing-code, "near me", treatment and
  staging searches, vaping and nicotine pouches.
- **The article writer is grounded.** It now gets the site's SEER figures
  (moved into `topics.py` so the CI job can import them), the checked source
  list, and rules: no other statistics, no Stage I to IV, no named people, a
  linked Sources section. Its token limit was too small and cut articles off
  mid-sources, so it was raised and a cut-off article now fails instead of
  being saved. A sample article came back with only site figures and listed
  sources.
- **Three drafts from the summer are still unpublished** (risk factors, HPV
  connection, alcohol and tobacco), waiting on Ian at `/review/<slug>`.

### 2026-10-21 (late): fixes from Ian's calendar review (pushed 21 Oct)
- **Pictures come from the topic, not a stock search.** `topics.VISUAL`
  gives every topic a 3D still of the place in the mouth, one of the two
  attributed clinical photos, a stock photo of a literal subject that a
  vision check must confirm shows it, or no picture. Single images use a new
  light "plate" layout matching the reels. Carousels show the picture as its
  own untinted slide.
- **Reels light up what the voice names.** `reel3d.match_focus` reads each
  line: "tongue" lights the tongue, "under your tongue" the floor of the
  mouth, lips or cheeks get the whole mouth (the model has neither), and a
  line naming no place never lights the teeth. Shot lists are now saved in
  each reel's manifest.
- **The jaw opens** for tongue and floor-of-mouth shots, rotating the lower
  jaw, teeth and lower gums about the jaw joints.
- **Lips and throat meshes are no longer drawn.** The atlas has only the
  muscle under the lips, and its soft palate and tonsils are a flat strip and
  smooth blobs; Ian found both ugly. Throat shots look into the open mouth
  with a pointer to the back of it. The lip topic no longer becomes a reel.
- **Sources.** `topics.CITES` holds sources already cited on the site, each
  PubMed id re-checked on 21 Oct, mapped to topics. Posts with a research or
  statistics claim carry a short source line on the slide or reel and full
  references with links in the caption, kept through the LinkedIn rewrite.
- **Carousels, from sourced research** (Mosseri on carousels being re-shown
  from slide 2; Socialinsider 2026 benchmarks; the Debunking Handbook 2020;
  CDC Clear Communication Index): slide 2 must stand alone, myth slides lead
  with the fact, a swipe cue on every slide, a source line on content slides,
  4 to 5 content slides instead of 3 to 4, and a closing slide that asks for
  a save and a send before giving the address.

### 2026-10-21 (later)
- **Learn page condensed: six guide cards and a "Load more" article list.**
  Pushed 21 Oct. The card grid on
  `/learn` is now two rows of three on desktop. Facts & Stats, HPV, and
  Prevention left the grid because the Overview and Risk Factors cards cover
  most of the same ground; their pages, the sitemap, the footer links, and the
  links from other learn pages are unchanged. (Ian asked to drop two, but there
  were nine cards, so reaching two rows of three meant dropping three.) The
  articles list shows the five newest and a "Load more" button that adds five
  at a time; every article link is still in the HTML for search engines. New
  string in English, Spanish, and Portuguese.

### 2026-10-21 (later still)
- **Stale SEER figures outside the articles corrected** (same branch,
  `claude/article-house-rules-audit`, not yet pushed or deployed).
  `public/llms.txt`: 54,000 cases and "over 84%" survival became about 60,480
  projected for 2026 and about 89% localized / 36% distant; its title's em dash
  became a colon. The sex explanation on the results page: men "roughly twice"
  became 2.6 times in English, Spanish and Portuguese, with both i18n snapshots
  updated to match so the next sync does not retranslate over the edit. Same
  fix in the risk-factors draft. The July Tour de France idea brief in
  `oralcheck-agent/ideas.json` now says about 60,480 for 2026. The only
  remaining "84%" mentions are the agent's regression test and comment that
  check the old figure stays out.

### 2026-10-21 (later)
- **Published articles brought back in line with the house rules.** Committed
  on branch `claude/article-house-rules-audit`, **not yet pushed or deployed**,
  so the live site still has the old copy until it is merged. All 11 published
  articles and their Spanish translations were audited for stage I to IV
  survival wording, figures that differ from `seerStats.ts`, em dashes, any
  UW-Madison mention, and fabricated quotes or credentials. No em dashes, UW
  mentions, or fabricated quotes were found. Fixed, in English and Spanish:
  - *Survival rate and early detection:* the excerpt compared "stage I and
    stage IV" survival; it now says "while still localized" and "once it has
    spread to distant sites". Survival 84 to 86 / 67 / below 40 became 88.7 /
    69.7 / 36.0 with a link to SEER. "Roughly half diagnosed late (Oral Cancer
    Foundation)" became SEER's stage share: 26% localized, about two-thirds
    after spread. Men 2x became 2.6x.
  - *What does oral cancer look like:* 54,000 a year became about 60,480
    projected for 2026 (SEER).
  - *Self exam:* "over 80% early, below 40% late" became about 89% localized
    and 36% distant (SEER, 2016 to 2022).
  - *Symptoms:* men 2x became 2.6x.
  - Slugs and titles unchanged.

### 2026-10-21
- **Results page cleanup** (pushed 21 Oct). Ian called `/results` messy.
  What was actually wrong: the gauge's grey track was the same colour as the
  card behind it, so it disappeared and a low score drew as a lone green blob
  beside the needle (the loading skeleton was invisible the same way); about
  a dozen identical grey cards, with borders the same colour as their fill;
  four long factor write-ups sitting between the result and the next steps,
  which started about 2,400px down on a phone; a two-column factor grid that
  stretched short cards to the height of long ones; the low-score caveat
  wedged between the headline and its own summary; and the find-care button
  three times on elevated and high, ending in a pile of four differently
  styled actions. Now: result, then next steps, then the factors, the oral
  cavity or oropharynx note, reading, and the email copy. Steps and factors
  are one panel each with rows. One big find-care button per band: in the
  result card on elevated, high, and symptom results, under the next steps on
  low and moderate. Share and retake are quiet links under the email box. No
  copy, scoring, bands, or medical content changed. Analytics note:
  `results_primary_cta` no longer fires on elevated or high, because that
  button is no longer shown there. Files: `src/app/[locale]/results/page.tsx`,
  `src/components/RiskGauge.tsx`.

- **Article pages redesigned in a clinical journal style (not yet pushed;
  committed on branch `worktree-agent-a16b9234ccd3a0dda`).** Ian called the
  SEO article layout sloppy. Now: a "Patient guide" label, title, standfirst
  and one date and reading-time line; body at about 70 characters a line with
  hairline section breaks; a contents list (sticky on desktop, fold-out on a
  phone); numbered Sources when an article links out; the article's own
  disclaimer; a screener box and three related guides. No markdown in
  `content/` was touched. Also fixed on the way: shared articles now preview
  with their own title and the Learn image instead of the home page's;
  Spanish articles now name themselves as canonical instead of the English
  page; the byline "Written by Ian Harris, predental student at the
  University of Wisconsin-Madison" is replaced by "Published by OralCheck",
  since the articles name no author and UW is not to appear on the site.
  Found and not fixed: every internal link inside the articles points at the
  home page rather than the article it names, and published articles are not
  in the sitemap.
- **3D reels, original-look posts, and the posting calendar are live on
  master** (commit 4bba2c7). Reels render as narrated 3D scenes with the
  classic reel as fallback; posts use the original layouts; the Monday run is
  paused; `calendar.yml` runs daily at 13:00 UTC and was test-run once.
- **Carousels built from a site screenshot no longer crash.** The caption's
  photo credit expected a credit record and got the string "oralcheck.org".
  Our own page needs no credit line. Found by the calendar build.

### 2026-10-08
- **The settled tobacco plus alcohol figure is in the social topic bank.**
  `oralcheck-agent/topics.py`, `tobacco_plus_alcohol`: about 15 times for
  more than a pack a day plus three or more drinks a day (Hashibe 2009, 17
  pooled studies), the same wording the site now uses. The canker fact
  already said 7 to 14 days. Closes the follow-up the figures fix left open.
- **One figure everywhere for tobacco plus alcohol, and for canker sore
  healing time.** Live on oralcheck.org 2026-10-08 (commit f30f7dd, checked
  on the production pages in all three languages). Closes "The site
  contradicts itself on two figures". The Hashibe figure was taken from the
  paper's own Table 3, not from the abstract or a secondary quote.
  - **Tobacco plus alcohol: about 15 times, not 30.** Source: Hashibe et al.
    2009, *Cancer Epidemiology, Biomarkers & Prevention*, the pooled INHANCE
    analysis (17 studies, 11,221 cases). Table 3, oral cavity, more than 20
    cigarettes and 3 or more drinks a day against neither: OR 15.49 (7.24 to
    33.14). The "30-fold" had no source behind it; the nearest real figure is
    Blot 1988, *Cancer Research*, "more than 35-fold", but that is one US study
    of about 1,100 cases, oral and throat cancer counted together, at two or
    more packs and more than four drinks a day. Hashibe is larger, newer, and
    reports the mouth on its own. Copy now names the exposure ("more than a
    pack a day and three or more drinks a day") instead of "heavily", so the
    15 is not read as applying to everyone who smokes and drinks.
  - **Canker sores: 7 to 14 days, not 7 to 10.** Sources: the US National
    Library of Medicine's MeSH definition of aphthous stomatitis ("lasting for
    7 to 14 days and then heal without scarring") and the NHS mouth ulcer page
    ("within a week or 2"). It also lines up with the two-week rule; 7 to 10
    left an unexplained gap before day 14.
  - **Where it changed, in English, Spanish and Portuguese:** the oral cancer
    overview, risk factors page (two-factor box, alcohol card, FAQ), signs page
    (four places), canker page meta description and its share image, the
    alcohol question's explainer, the interaction guidance on results, the
    results page evidence note, and the AI summary prompt, which used to tell
    the model this person's risk was about 15x; it now gives the heaviest-user
    figure and tells the model not to state a multiple for the person, since
    the bonus also fires for occasional smokers and weekly drinkers. The four
    learn pages now link the figure's source in their Sources box. The
    alcohol explainer also now matches Bagnardi: about 2x for moderate
    drinking, about 5x for heavy, where it had said 2 to 3x.
  - **The `/methods` interaction explanation was wrong and is rewritten.** It
    said combined use is "roughly 15x" against "about 9x" from adding weights.
    But the weights are logarithms, so adding them already multiplies (6 x 3 =
    18x, more than 15). The real justification for +3 is Hashibe's
    interaction parameter: the joint effect is 2.15 times what multiplication
    predicts, and round(ln 2.15 x 4.47) = 3. The oral cavity value (3.09)
    would give 5, so +3 is the conservative reading. No weight or band moved.
  - **Seven of the 13 PubMed links on `/methods` opened unrelated papers**
    (a bocavirus review, a COPD index, a glioma study, an ephedra case report
    and others), and four citations named the wrong journal: Gandini is *Int J
    Cancer* not *Oral Oncology*, Bagnardi is *Br J Cancer* not *Annals of
    Oncology*, Gillison is *JNCI* not *JAMA*, and the Pavia entry described a
    paper that does not exist (the real one is *Am J Clin Nutr* 2006, the
    fruit and vegetable meta-analysis the sensitivity analysis already used).
    Every link was checked against PubMed's own record and corrected, and the
    same names fixed in the screener explainers, results page, risk engine
    comments and the ADA briefing. The Hashibe note claimed "OR 35.8x for heavy
    combined users"; that is the paper's larynx figure (36.87). Blot 1988 added
    as reference 14 so a reader who knows the 35-fold figure sees why it is not
    used.

### 2026-09-21
- **Four fixes to the reel pipeline, from frame-by-frame review of the reel
  that was about to post.** Asked how the reels could be improved; rather than
  general advice, pulled the actual Stoptober reel scheduled for that night and
  inspected it with ffmpeg (`blackdetect`, sub-second frame extraction) instead
  of guessing.
  1. **A real bug: a 0.23s black flash right before the end card**, measured
     with `blackdetect` at 28.47 to 28.70s. The outro faded in from black
     (`fade=in:st=0:d=0.25`) while every other cut in a reel, segment to
     segment via the concat demuxer, is an instant hard cut with no fade at
     all. Nothing before the outro faded *to* black either, so the mismatch
     produced a visible flash. Fixed by dropping the outro's fade-in to match
     the cut style used everywhere else.
  2. **Scenes were going fully static for several seconds.** Each scene
     animates in over 2.6s then held on a single frame, cloned by ffmpeg, for
     however long the narration ran; the "Tobacco. Alcohol. HPV." scene in
     tonight's reel sat completely frozen for about 5 seconds. On a feed with
     an 83.7% measured skip rate, several seconds of zero visual change early
     in a cold viewer's watch is a plausible driver on its own.
     `render_kinetic_frames` now keeps rendering slow, deterministic backdrop
     motion (blobs, sweep, grid, halo, rays, and the new photo backdrop, all
     now scrubbed by `--t` like the text already was, which some of them
     previously were not) for a further `KINETIC_HOLD_DRIFT` = 2.6s before
     anything freezes. Verified locally: a 5s test segment showed continued,
     measurable motion across nearly the entire hold instead of freezing after
     ~1.6s. Adds about 16 extra screenshots per segment, not a proportional
     re-render.
  3. **Reels had never actually gotten a real photo**, despite
     `kinetic_scene_html` already supporting one: `_assign_reel_visuals` only
     ever tried `site_shot` or `search_query`, and the reel-script prompt never
     told the model those fields existed, so they were always empty in
     practice. A segment can now ask for one of the two clinical sign photos
     with real attribution on file (`white_patch`, `mixed_patch`, both from the
     same library the carousels already use), capped at one per reel and kept
     out of stat/scene segments. `sore` and `lip` stay excluded (no recorded
     attribution, see the entry below) even if a script asks for them by name.
  4. **Music bed lowered from 0.17 to 0.11.** Ian flagged it as sitting a
     little too loud under the narration; `amix` runs with `normalize=0`, so
     this is a direct, unattenuated gain on the bed relative to the voice.
  All four covered by new checks in `test_render.py`: no black frame in the
  outro, hold-phase frames are not byte-identical, `REEL_SIGN_PHOTOS` cannot
  resolve `sore` or `lip`, and the music constant is pinned below 0.12. Frame-0
  legibility was also checked directly against tonight's real exported video
  and confirmed already working (readable by ~0.1s), so that earlier fix did
  not need touching. Whether skip rate actually improves is still open, see
  the entry above: it needs a reel built after this and real engagement data.

### 2026-09-18 (decided)
- **Decided against fixing the wrong-stat posts.** Asked directly whether to swap
  the queued Instagram carousel (still showing 84%/below 40%, scheduled 22:00 UTC)
  for the corrected, pre-built replacement before it fired. Ian said no, leave it
  as-is. The already-published LinkedIn post with the same wrong figures also stays
  up untouched. Root cause is still fixed (`SEER_FACTS`, see below), so this does not
  recur, but these two specific posts keep the pre-correction numbers permanently.

### 2026-09-18
- **The content generator had no grounded epidemiology numbers, and it showed.**
  The 2026-09-14 run published a LinkedIn post stating "approximately 84%"
  early-stage survival and "below 40%" late, the exact figures `seerStats.ts`
  corrected on 2026-08-30 after they had drifted across nine files on the site
  itself. The LinkedIn rewrite step wasn't the bug, it correctly obeyed its own
  instruction to preserve every number exactly as given; the original Instagram
  caption never had a grounded number to inherit, so the model filled the gap
  with a plausible stat pair from training data. Fixed: `SEER_FACTS` in
  `oralcheck_agent.py` mirrors `seerStats.ts` by hand and is now prepended to
  `SYSTEM_PROMPT`, which every idea and content generation call already
  receives. `test_render.py` now checks the pinned figures against
  `seerStats.ts` on every run and confirms the pre-correction numbers are
  absent from the prompt, so this is a test failure next time, not a silent
  drift. Found by checking Publora directly after being asked why nothing
  seemed to have scheduled; everything had scheduled, which is what surfaced
  what it had scheduled. The fix for the queued Instagram post (corrected
  caption, slide 5 re-rendered pixel-identical except 84 to 89 percent) was
  built and verified but never applied, see the entry directly below: Ian
  chose to leave both the carousel and the published LinkedIn post as they
  are

### 2026-09-14 (late, iii)
- **Every page swept at 375x812.** No horizontal overflow anywhere and exactly
  one `<h1>` on every page, which is the state the earlier passes were aiming at
- **`/find-care` had 127 touch targets under 44px**, which matters more than the
  count suggests: it is where the results page sends people, and the undersized
  controls were the clinic phone numbers (20px) and the category filters (34px).
  A phone number is the action on that page. Down to 4, and the remainder are
  Leaflet's own zoom buttons and its required attribution link
- **`/methods` had 13 "View on PubMed" links at 16px**, on the page whose whole
  purpose is that a clinician can check the sources. Now 0
- Back links were 20px on ten learn pages, `/methods` and `/review/[slug]`.
  Smaller fixes on `/press`, `/infographic`, `/for-clinicians` and the `/qr`
  input, which was a 38px form field
- **Inline prose links were deliberately left alone.** "canker sores" inside a
  sentence is exempt under WCAG 2.5.8, and padding it to 44px breaks the line
  spacing of the paragraph around it. The rule applies to standalone controls,
  not to every link

### 2026-09-14 (late, ii)
- **Content pages had no shared width, so several read as skinny.** The nav and
  footer are `max-w-6xl` while page containers ranged from `2xl` to `6xl`, and
  the learn section alone had six pages at `5xl` and three at `3xl`. About,
  For Clinicians, Methods, Press, Infographic, Learn Facts and Learn Self-exam
  are all on `max-w-5xl` now, which is where the learn section and the results
  page already were. Deliberate exceptions kept and worth not "fixing" later:
  `/privacy` and `/terms` stay `4xl` and `/learn/[slug]` stays `3xl` because
  they are single columns of prose, where a wider container makes the line
  length worse, and `/screener` stays `2xl` because one question at a time is
  the point
- **Widening prose is not the same as improving it.** Body copy in the widened
  pages is capped near 65 characters, since 1024px of unconstrained text runs
  past 105 characters a line and the guideline is 65 to 75
- **The About bio card was the case where that tradeoff did not work.** Capping
  the measure inside a full-width card left half the card empty, which looked
  worse than the original. It is two columns from `md` up now: identity block
  left, bio right at about 80 characters. The card uses the width and the
  measure stays readable, which single-column could not do at once

### 2026-09-14 (late)
- **A ninth learn guide: white and red patches.** `/learn/white-and-red-patches`,
  live in all three languages. Leukoplakia and erythroplakia are the actual
  precancerous lesions and `/learn/signs` gave them one line each. The topic was
  chosen off the traffic: `canker-sore-vs-oral-cancer` is the best organic page
  on the site by a wide margin, and it works because it answers one frightened
  person's specific question. "White patch in my mouth" is the same shape of
  query. Transformation rates are given as ranges rather than a single figure,
  because published estimates differ substantially by population and follow-up,
  and the page says so
- **Homepage and learn pages audited against the Web Interface Guidelines.** Two
  `<h1>` elements on the homepage, one hidden and one visible, so the hero line
  is now a `<p>` and the descriptive heading is the only h1. The hero photo, the
  largest above-the-fold element on the site, had no intrinsic size and no
  priority hint: it now has both, which removes a layout shift on every first
  load. Eight more `transition-all` declarations replaced with explicit property
  lists. Fifteen footer links were 18 to 20px tall, under the 24px minimum, and
  now clear it. The logo marquee pauses on keyboard focus as well as hover,
  since the logos are links and a keyboard user was chasing a moving target
- **Not a bug, recorded so it is not re-investigated:** the partner logos appear
  not to load when a test scrolls past them instantly. They load correctly on a
  real scroll. Lazy loading simply never fires when `scrollTo` skips an element

### 2026-09-14 (evening)
- **Sensitivity analysis of the tiers, run and written up.** `docs/SENSITIVITY_ANALYSIS.md`,
  code in `scripts/sensitivity_analysis.py`, raw outputs in `docs/sensitivity-runs/`.
  Every sourced OR sampled within its published 95% CI, 10,000 draws, the full
  995,328-profile space enumerated. Headline: **73.7% of profiles keep one tier on
  95% of draws** with the scale fixed, and the elevated/high boundary is the
  unstable one (20.9% of profiles straddle it). The fragility is not mainly CI
  width (that alone moves 6% of tier mass) but point estimates that disagree with
  the meta-analyses. Three stand out. **The tobacco anchor (OR 6.0) sits above the
  upper bound of both oral-cavity meta-analyses** (3.39, 2.64 to 4.35; 3.43, 2.37
  to 4.94), and letting the scale float on the published value inflates every
  other weight by about half and under-calls 32% of the space. **Past betel** is
  weighted 4 where the former-chewer OR implies 9. **Occasional tobacco** is 5
  where the closest published category implies 2. The betel + daily tobacco +
  daily alcohol profile stays high on 99.5% of draws under the primary alcohol
  mapping and is a coin flip under the alternative. The young HPV-history profile
  does not reach elevated at the median even when scored at the OR for confirmed
  oral HPV-16 infection. Age, sex, dental and the self-reported HPV proxy could
  not be sourced with a CI and were held fixed, so the stability numbers are
  upper bounds. **This is not a validation** and the write-up says so. Also found:
  the spec says only symptom = yes forces high; the code forces it for "unsure"
  too.
- **Analytics have been dropping events on every cold page load, all year.**
  `sendGAEvent` discards the event when `window.dataLayer` does not exist yet,
  warning only in the console. A click-through from the home page works; a
  *direct* load of `/screener` runs the mount effect before the GA script
  exists, and the event is gone. That is every QR scan, every link shared into
  a chat app, and every search click landing deep. It is why `screener_completed`
  has outrun `screener_started` **291 to 139** since January and why
  `ga_stats.py` kept printing "completion rate not reliable". Verified on
  production both ways before touching anything. `src/lib/ga.ts` queues the
  event and flushes it once GA appears, pushing an `arguments` object rather
  than an array so gtag parses it on the proven path. Live and confirmed
- **The email capture had no instrumentation.** Shown 101 times, nothing
  recorded on the far side. Now counted by tier, success and failure
- **`ga_stats.py` could not read the `.env` its own docstring tells you to fill
  in.** It was demanding credentials it had been told where to find
- **The feed is live again after 17 dark days.** The 19:00 backup cron fired,
  ran green in 22 minutes, and booked 15, 18 and 21 Sept. The stranded alcohol
  idea was released back into the pool by the fix made hours earlier:
  `Released 1 idea(s) claimed by a run that never finished: idea_528dc39d`

### 2026-09-14
- **The backup cron could race the run it was backing up.** "Skip if already run
  today" counted only runs that had *finished*. This workflow's normal state is
  waiting on a Telegram reply for hours, so the 14:00 Monday run is very often
  still in progress when the 19:00 backup fires, and the guard read that as
  "nothing has happened today": two idea batches, two sets of Publora slots
  against a cap of three, and both runs racing the same ledger push. It had not
  bitten yet only because every 14:00 run so far happened to finish inside five
  hours. The guard now also skips when another run today is still going. A manual
  dispatch is still never skipped
- **An idea claimed by a run that died was lost permanently.** `select()` marks
  an idea "selected" before the post is generated so two runs cannot claim the
  same one, and "selected" is in `USED_STATUSES`, so a run that dies in between
  leaves the topic both unbuilt and unsuggestable forever. The 2026-08-31 run
  stranded "Alcohol Is an Oral Cancer Risk Factor Most People Never Hear About"
  exactly this way, and neither failed 09-07 run could reach it. A fresh batch
  now hands back any claim with no manifest behind it, which is safe precisely
  there: nothing is legitimately mid-build at the start of a batch
- **Context:** the feed has been dark since 28 Aug. 09-07 failed twice on the
  import bug fixed the next day, and on 09-14 GitHub simply did not fire the
  14:00 cron at all, which is what the 19:00 backup exists for

### 2026-09-08
- **The Monday idea flow runs again.** It failed twice on 2026-09-07 and no
  content was scheduled for that week. `oralcheck_agent.py` validated the
  environment at import and called `sys.exit(1)` when `ANTHROPIC_API_KEY` was
  absent, and the reels-design-system commit had just made `test_render.py`
  import it. The verify step carries no secrets by design, so the import killed
  the runner. `SystemExit` is not an `Exception`, so it slipped through the
  tests' guards and the log read as "every check passed, exit code 1". Validation
  moved to `main()`; the CLI still fails fast, `--help` no longer needs a key.
  A subprocess regression test imports the agent with the key stripped and
  dotenv stubbed, since `find_dotenv` walks up from the module's own directory
  and would otherwise hide the bug on the laptop exactly as it did before.
  Test steps now run unbuffered so the next failure appears beside the check
  that died. The reel scene and outro checks had never run on the runner; they
  do now

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

- **Player photos on the Brewers post (2026-10-26).** Ian offered to take the
  liability, but the problem is not his risk: a real player's face beside
  "chewing tobacco causes oral cancer" says that player dips, a claim about a
  real person nobody can back up. A ballpark photo carries the same idea.

| Idea | Why | Revisit when |
|---|---|---|
| AI image diagnosis ("upload a photo of your mouth") | Moves the product into clinical decision support, with a far heavier regulatory and validation burden. Current strength is the low-risk awareness → education → professional care model. | Never, without a clinical partner and a validation study |
| Paying dentists per patient | Wrong incentive; makes a health tool feel commercial | Not planned |
| Buffer as a second scheduler | Free tier has no open API, so posts would be pasted in by hand anyway. No better than the Telegram handoff, plus a second dashboard. | If Buffer reopens API access |
| Quoting "30-fold" or "35-fold" for smoking plus drinking | Decided 2026-10-08. The 35-fold figure (Blot 1988) is real but is one 1980s US study, oral and throat cancer pooled, at two or more packs and four or more drinks a day. Hashibe 2009 pools 17 studies, reports the oral cavity alone, and gives about 15 at a pack and three drinks. "30-fold" matched no source at all. | A larger pooled estimate for the oral cavity alone |
| LinkedIn API direct publishing | Company-page posting needs the Community Management API: restricted to reviewed legal organisations, explicitly not available to individuals | If OralCheck incorporates |
| The posts2 templates for carousels and images (mouth-map illustrations, notes-app, text-post, bold posters) | Live for one batch, 19 Oct. Ian: too playful, prefers the original post look. The code stays because reels still borrow pieces of it | Not planned |
| A cleaned-up classic reel (one still background, no blur-in, colour-only emphasis, dissolves, a progress bar, a matching end card) | Built and sampled 2026-10-20 at Ian's request. His verdict: worse than the original, which itself was "very meh". Reverted the same day; reels went 3D instead | Not planned |
| A "light", gently witty tone lane for ideas | Retired 2026-10-20 with the posts2 look: the account should read clinical | Not planned |
| A "NOPE" stamp reel visual and a group-chat-style post template | Sampled 2026-10-08. Ian: off brand. The stamp read as flippant on a cancer account; the chat imitated a conversation nobody had | Not planned |
| A "trend comparison" idea lane ("a stadium holds 65,000...") | Six of the first 38 ideas used it. The tie-ins (Wimbledon, the Tour de France) read as forced, and a forced hook is worse than a plain post. Real awareness days stay | Not planned |

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
