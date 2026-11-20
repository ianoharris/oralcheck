# Instagram growth audit, 20 November 2026

Goal set by Ian: **visits to oralcheck.org**, not followers.

Sources: Instagram insights for all 36 posts on @oralcheckdotorg (read-only export,
`oralcheck-agent/ig_insights.py` via the "Export Instagram insights" workflow);
Google Analytics for the live site since April; and 14 top short videos from
dental creators and animated health explainers. Those came from YouTube Shorts,
where the same creators post the same videos without a login wall. Instagram
itself was not scraped: Ian chose public-only access, so Agent Reach's Instagram
channel (which needs a logged-in session) was not installed.

## Where things stand

| | |
|---|---|
| Followers | 149 |
| Reels, average views (last 6) | about 150 |
| Reels, skip rate | 66 to 86%, typically about 80% |
| Reels, average watch time (Oct and Nov) | 2.7 to 5 seconds, on reels 24 to 38 seconds long |
| Visits to the site from Instagram, 28 Oct to 19 Nov | 23 people, about one a day |
| Of those, started the screener | 2 |
| Website taps on the profile (latest day) | 2 |

Instagram defines skip rate as the share of viewers who swipe away within the first
three seconds. At about 80%, four in five people who are shown a reel are gone
before the reel has said anything. Everything else follows from that: a reel
that loses its audience in three seconds is shown to fewer people, earns no
follows, and sends no one to the site.

For context, Instagram is a small source of visitors overall. Since April the site
has had about 590 direct visitors (QR codes, shared links), 96 from Google, 35
from Facebook, 20 from Reddit, and about 40 from organic Instagram (plus about 50
from the paid Instagram ads in May).

## What the numbers say about your own posts

**The best performer is a carousel people sent to someone.** 24 July, "Your dentist
is doing more than checking for cavities", reached 496 views and was **shared 14
times**. No other post has more than 2 shares. It is practical, about the reader's
own next appointment, and easy to forward to a parent.

**The reel with the lowest skip rate had the bluntest opening line.** 5 November,
"No pain, no problem. That logic does not apply here.": 66% skip, 282 views, the
highest of any reel. The reels that open on a topic sentence ("Tobacco remains one
of the three primary modifiable risk factors...", "One month without alcohol is
genuinely worth something...") skip at 82 to 86%.

**The animated redo is holding attention better, early.** The 19 November age chart
reel has the longest average watch of any recent reel (9.6 seconds) after one day,
on only 35 views. Too early to call; worth re-checking in a week.

**Follows from posts are effectively zero.** That fits the goal: followers were never
the target. But it also means each reel has to be found by strangers on its own.

## What the niche does in the first three seconds that you don't

Frames at 0, 0.7, 1.5 and 3 seconds, side by side.

**Their opening frame is already the payoff.** Zack D. Films (11M followers, 3D
animated explainers, median 5.75M views a short) opens on a knife already cutting
a watermelon. Nucleus Medical Media's 21M-view short opens on the 3D anatomy already
moving under a big question. Dental Digest opens on a face mid-sentence, then a
prop. Something visibly changes about every 0.7 seconds.

**Their words are big, few and in the middle of the screen.** Two or three words at a
time, large, centred, timed to the voice ("Cut the" / "watermelon" / "like this").

**Yours open on a still picture and small, half-grey text.** In the 5 Nov, 9 Nov and
17 Nov reels the first three seconds show the same image throughout: the open-mouth
drawing (on two reels running, so a returning viewer has already seen it) or the
3D jaw. The hook line sits in the lower third in body-size type, and the words
not yet spoken are pale grey, so at a glance the first frame reads as a mostly
grey sentence over a diagram. The age reel opens on an empty chart. Nothing in
your first frame tells a scrolling thumb what is about to happen.

**Length.** Your reels run 24 to 38 seconds and people stay 3 to 5. Dr. Mark
Burhenne's two best shorts this year are 5 and 7 seconds: one bold statement, full
screen, done. The niche's winners are either very short or very fast.

**People.** The most-viewed mouth cancer short found (Oral Health Foundation, "Early
signs of mouth cancer", 42K views against a channel median of about 640) is a
dentist talking to camera, with burned-in subtitles. Every dental creator above
puts a face or hands on screen in the first second. OralCheck's reels have
neither, by design (the house style says no faces).

## What to change, in order of effect on site visits

1. **Rebuild the first second of every reel.** The first frame shows the hook in full
   (no grey words waiting to be revealed), in large type in the centre of the screen,
   over something already moving. A change on screen at least every second. No two
   reels in a row open on the same picture. This is a change to the house style
   (`oralcheck-agent/anim/STYLE.md`) and the reel templates, so it applies to every
   reel from then on, including the approved ones not yet posted.
2. **Open with the blunt line, not the topic.** "No pain, no problem" beat every topic
   sentence. The script writer should lead with the claim a viewer would argue with.
3. **Test a 7 to 12 second format.** One statement, one visual, the two-week rule,
   the address. Alternate with the longer animated reels and compare skip rates.
4. **Make more things worth sending.** The one post people shared was practical
   ("what your dentist checks"). More of those: what to ask at a cleaning, how to
   check a parent's mouth, what a two-week sore looks like on day 14.
5. **Give people a tap to the site.** Today the only route is the bio link, and it
   gets about two taps a day. Comment-to-DM (already on the tracker) turns each reel
   into a link; a Story with a link sticker on the day each reel posts is the free
   manual version.
6. **Consider hands or a face.** Your own hands doing the self-exam with a mirror, or
   you talking for five seconds, is the single thing every growing account in the
   niche has and OralCheck does not. Your call: it changes the no-faces rule.

## How to check whether it worked

Ask Claude to re-run the "Export Instagram insights" workflow after three or four
reels in the new style (it needs a one-time key generated on the Mac, so it is not a
button to press by hand), and compare skip rate and
average watch time against the table above. GA4's `instagram / social` source shows
whether the extra attention reaches the site.
