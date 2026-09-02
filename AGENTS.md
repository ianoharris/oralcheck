<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Keep the tracker current

`docs/ROADMAP.md` is the source of truth for what is open, blocked, and shipped.
It is mirrored to a published artifact Ian reads:

**https://claude.ai/code/artifact/cc490e4b-1ee3-4062-bc56-eada066f1003**

**At the end of any turn that changes the state of the work, update both.** That
means: something shipped, a new blocker appeared, a blocker cleared, an outreach
email was sent or answered, or a decision was made. Do it as part of the turn,
not when asked. Ian should never have to ask what the current state is.

To update the artifact, republish the same file with `url` set to the link above,
or it creates a second artifact instead of updating this one.

Two rules the roadmap exists to enforce, and they apply to the artifact too:

1. **Nothing gets deleted.** Shipped items move to *Shipped* with a date.
   Rejected ideas move to *Decided against* with the reason, so the same idea is
   not re-litigated from scratch in six months.
2. **An open item stays open until it is actually done**, with its blocker named.
   The entire purpose of the list is the things that come up once, sound good,
   and are never mentioned again.

The artifact's most useful distinction is **blocked on Ian** versus **blocked on
someone else**. Preserve it. Everything in the first group should be something he
can finish without writing code.

# Keep the owner's guide current

`docs/OWNERS_GUIDE.md` explains the whole project to Ian in plain language: the
medicine, the methodology, the hosting, the decisions and why they went that way,
the limitations, and the questions he will be asked. It exists so he is never
caught not knowing something about his own project.

**Update it in the same turn as any change that makes it wrong.** That means:

- a question added, removed, or re-weighted, or a band boundary moved
- a clinician reviewing it, or agreeing (or declining) to be named
- a change to hosting, the stack, or a major dependency
- refreshed SEER figures
- a change to the social cadence or the agent's design
- anything significant that broke, and how it was found

It is written for someone who is not a developer. Keep it plain, keep the
diagrams, and do not let it drift into changelog prose: it is a guide, not a log.
`docs/ROADMAP.md` is the log.

# House rules

- **No em dashes** in anything written for Ian or published under his name, on
  the site, in captions, or in outreach email. Use commas, colons, or periods.
- **Never fabricate a quote, endorsement, credential, or affiliation.** Cite a
  real source with a link instead. A named clinician goes on the site only after
  they have explicitly agreed in writing.
- **Epidemiology figures come from `src/lib/seerStats.ts`.** Case counts, death
  counts, survival by stage, incidence by sex, and median age at diagnosis all
  live there with the source URL and a `lastVerified` date. Do not type one of
  these numbers into a component. The message catalogues necessarily carry their
  own copies in prose, since they are JSON and translated, so when a figure
  changes, grep `messages/*.json` for the old one as well. Re-check the file
  against SEER annually: the case and death figures are year-stamped
  projections and go stale on a schedule.
- **Survival by stage is SEER *summary* stage**, which is localized, regional,
  and distant. It is not AJCC Stage I through IV, and copy must not present it
  as such. Say "while still localized" and "once it has spread to distant
  sites", or name the summary stage.
- **OralCheck is not a UW-Madison project.** Ian is a UW-Madison undergraduate,
  but the university does not sponsor, endorse, or review it, and its name and
  marks must not appear on anything. Correct that assumption whenever it appears,
  including when someone else introduces it.
