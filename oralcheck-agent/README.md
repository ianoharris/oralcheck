# OralCheck Agent

Python script that runs an Instagram content pipeline for [OralCheck](https://oralcheck.org) — an oral cancer risk screener.

Each run: generates a script + caption via Claude, generates a Reel or image via fal.ai, sends a Telegram preview for approval, then posts to Instagram via Publora on approval.

---

## Setup

### 1. Install dependencies

```bash
pip install anthropic httpx python-dotenv
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Where to get it |
|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `FAL_KEY` | [fal.ai dashboard](https://fal.ai) |
| `PUBLORA_API_KEY` | [Publora dashboard](https://publora.com) |
| `TELEGRAM_BOT_TOKEN` | Message [@BotFather](https://t.me/botfather) on Telegram → `/newbot` |
| `TELEGRAM_CHAT_ID` | Message [@userinfobot](https://t.me/userinfobot) to get your user ID |

After creating your Telegram bot, start a conversation with it (send it any message) before running the script — otherwise the bot can't send you messages.

---

## Usage

### Auto mode — picks the next content pillar automatically

```bash
python oralcheck_agent.py --auto
```

Rotates through five pillars (never repeats back-to-back):
- **Stats** — diagnosis and survival numbers
- **Myth busting** — HPV as leading cause, not just smokers
- **Self exam** — what to look for and how to check
- **HPV connection** — fastest growing group is adults 35-55
- **Screener CTA** — 2 minutes, free, oralcheck.org

Pillar rotation state is saved in `pillars.json`.

### Directed mode — you provide the brief

```bash
python oralcheck_agent.py --directed "Focus on HPV awareness for parents of teenagers"
```

### Media type

Both modes default to generating a Reel (vertical 9:16 video). Use `--media-type image` for a static square post:

```bash
python oralcheck_agent.py --auto --media-type image
python oralcheck_agent.py --directed "Your brief" --media-type image
```

---

## Approval flow

Once the preview is sent to Telegram:

| Reply | Action |
|---|---|
| `APPROVE` | Posts to Instagram via Publora, confirms in Telegram |
| `REJECT` | Bot asks what to change, regenerates, sends new preview |
| `SKIP` | Exits cleanly, nothing posted |

Timeout is 10 minutes. If no reply, the script exits without posting.

On rejection you have 5 minutes to send feedback. If no feedback is provided, the script regenerates with the original brief.

Up to 5 regeneration attempts before the script gives up.

---

## Files

```
oralcheck_agent.py   Main script
pillars.json         Pillar rotation state (auto-created on first run)
.env                 Your API keys (gitignored)
.env.example         Key names template
```
