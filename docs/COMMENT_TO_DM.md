# Comment-to-DM setup

Chosen 20 Nov 2026 to give Instagram viewers a tappable link: someone comments
**CHECK** on any post or reel and automatically gets a DM with the link to the
screener. Today the only route is the bio link, which gets about two taps a day.

The posts do not mention it yet. The ask is switched on in one step at the end,
after the DM is tested, so nobody is told to comment for a link that never comes.

## 1. Connect a DM tool (Ian, about 15 minutes)

ManyChat is the usual choice and has a free plan. Its pricing page could not be
read automatically on 20 Nov, so check the free plan's contact limit when you
sign up; at OralCheck's volume it is very unlikely to matter.

1. Sign up at manychat.com and choose Instagram. Log in with the
   **@oralcheckdotorg** account (not @six52studios).
2. Allow the permissions it asks for (messages and comments).
3. Create a new automation and pick the trigger **"User comments on your Post or Reel"**.
   - Which posts: **any post or reel** (so new reels are covered without setup).
   - Keyword: **CHECK** (also add **check** and **Check** if it asks for exact matches).
4. Optional public reply to the comment: `Sent, check your DMs.`
5. The DM (copy this exactly; the link is tagged so Analytics shows these visits as their own source):

   > Here is the free oral cancer risk check: https://oralcheck.org/?utm_source=instagram&utm_medium=dm&utm_campaign=comment_check
   >
   > It takes about two minutes, is private, and needs no account. It is a risk check, not a diagnosis: anything in your mouth that has not healed in two weeks still means a dentist.

6. Turn the automation on.

## 2. Test it

From a different Instagram account, comment CHECK on any OralCheck post. The DM
should arrive within a minute. Tap the link and make sure it opens the site.

## 3. Switch the ask on

Tell Claude it works, or run this yourself:

```bash
gh variable set COMMENT_DM_KEYWORD --body CHECK --repo ianoharris/oralcheck
```

From the next post on, every Instagram caption opens with
"Comment CHECK and the link to the free risk check comes straight to your DMs."
(`meta_ig.full_caption`). To turn it off, delete the variable. Measure it in
Analytics under the source `instagram / dm`.
