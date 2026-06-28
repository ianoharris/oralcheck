# Outreach Drafts

This folder holds auto-generated follow-up email drafts created by `oralcheck-agent/outreach_tracker.py`.

Each file is named `YYYY-MM-DD-Name-Org.md` and contains a YAML front matter block (recipient info, dates) followed by the email body.

## How to send a draft

1. Open the `.md` file and copy the email body below the front matter.
2. Paste it into Outlook and address it to the `to:` field in the front matter.
3. After sending, update the corresponding row in the Google Sheet:
   - **Status** column: change `Pending` to `Followed Up`
   - **Last_Followup** column: enter today's date as `YYYY-MM-DD`

The tracker runs every Sunday and skips any row that is not `Pending`, so updating the sheet prevents duplicate follow-ups from being generated.
