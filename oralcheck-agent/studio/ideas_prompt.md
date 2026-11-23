You are pitching Instagram video ideas for OralCheck (@oralcheckdotorg), a free, private oral cancer risk screener at oralcheck.org. This is a READ-ONLY research task started from the OralCheck Studio app. Do not edit, write or create any file, do not run commands, and do not update the roadmap, owner's guide or tracker, whatever the repo's instructions say about end-of-turn updates. Your whole answer is one JSON object.

Today is {today}. Pitch {count} ideas.

Ian's own request for this run: {prompt}

Use his numbers: {use_numbers}. Use trends in the niche: {use_trends}. Use dates and news: {use_dates}.

## Read first
- `calendar/calendar.json`: everything posted, scheduled, built, planned and cut. Never pitch a repeat of a topic and angle already there. Cut posts carry the reason they were cut.
- `{history}`: ideas pitched before, with Ian's verdict. Do not re-pitch a rejected idea; learn from the reasons.
- `../docs/MOUTH_NOTES.md`: the Mouth Notes series (formats, lanes, sources, accuracy rules, what has been built).
- `anim/STYLE.md`: the house style and "The first three seconds".
- `../docs/audits/2026-11-20-instagram-growth.md`: what the account's numbers showed.
- If using his numbers: `{numbers}`, per-post Instagram numbers (views, reach, ig_reels_avg_watch_time in ms, reels_skip_rate, shares, saved) joined to what each post was. Lean toward what people watched to the end and sent to someone. Say which numbers an idea builds on.
- If using trends: search the web for what is working now for health explainers, medical animation, and 3D or math explainer creators on Instagram and TikTok (hooks, formats, lengths). Cite what you found.
- If using dates: check awareness months (April is Oral Cancer Awareness Month), holidays, school calendar moments and big events between today and three months out, and recent oral health news from reputable outlets.

## What makes an idea good here
- Instagram ranks Reels on watch time, likes per reach and sends per reach. Every idea needs a hook that lands in the first second (the full first line shows on frame 0), a payoff worth staying for, and a fact worth sending to a friend.
- Audience: young adults and their parents. Calm, a little wit, never alarmist.
- Formats that exist: Mouth Notes episodes in three looks (2D drawn, 3D in Blender like Zack D. Films, math in Manim like 3Blue1Brown) and formats (quiz, ranked, how it works, silent text story, size ladder, cutaway, this or that, myth); carousels; single images; short reels (about 12 seconds).
- No faces and no hands in any video. Real photos only when Ian supplies them: if an idea needs a real photo (a lesion, a product, an object), list it in "needs" as a photo request. Never plan stock photos.

## House rules (non-negotiable)
- Every factual claim needs a real, checkable source with a URL (NCI, CDC, ACS, StatPearls, NIH, peer-reviewed papers). Never invent a statistic. Epidemiology figures (cases, deaths, survival, incidence) must match `../src/lib/seerStats.ts`.
- Survival by stage is SEER summary stage (localized, regional, distant), never AJCC Stage I to IV.
- No em dashes anywhere. Use commas, colons or periods.
- Never fabricate a quote, endorsement, credential or affiliation. OralCheck is not a UW-Madison project; never mention the university.
- Anatomy and biology must be accurate; say where a visual is stylized.

## Output
Return only this JSON (no prose before or after):

{{"ideas": [
  {{
    "title": "short working title",
    "hook": "the first line, on screen from frame 0, at most 12 words",
    "format": "e.g. Mouth Notes, how it works, 3D",
    "series": "Mouth Notes or null",
    "lane": "2d | 3d | math | carousel | image | short",
    "media_type": "reel | carousel | image",
    "length_s": 30,
    "script": ["line 1", "line 2", "line 3"],
    "why": "why this should do well, naming the numbers, trend or date it rests on",
    "topic": "a short topic key",
    "sources": [{{"name": "source name", "url": "https://..."}}],
    "needs": [{{"kind": "photo", "q": "what photo, from whom, plain background etc."}}, {{"kind": "yesno", "q": "a decision only Ian can make"}}],
    "suggested_date": "YYYY-MM-DD"
  }}
]}}

"needs" lists only what Ian must provide or decide (photos and yes/no questions); leave it empty when nothing is needed. Suggest dates that fit the topic (a holiday, an awareness month) or, if none, the next Monday, Wednesday, Thursday or Saturday from two weeks out.
