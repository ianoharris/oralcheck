# OralCheck — Oral Cancer Screening Awareness Tool
## Full Build Roadmap

---

## The Big Picture

You're building a patient-facing web app (deployed as a mobile-friendly site, installable like an app) where someone answers questions about their risk factors and gets a clear, educational risk summary with a nudge to see a dentist. Not a diagnosis tool — an awareness tool.

**Core features:**
1. Risk factor questionnaire (tobacco, alcohol, HPV, sun exposure, age, symptoms)
2. Personalized risk summary with educational content
3. "Find a dentist near me" map (free/low-cost clinics)
4. Shareable results page (so users can send to family members)
5. Informational pages about oral cancer signs and self-exam instructions

---

## Your Toolbelt (All Free)

### Building the App
| Tool | What It Does | Cost |
|---|---|---|
| **Claude Code** | Your AI coding partner — builds 90% of the app for you via plain English | Free tier available |
| **Cursor** (backup) | AI code editor if you want a visual IDE experience | Free tier |
| **VS Code** | Code editor where your files live | Free |
| **Git + GitHub** | Version control — saves your progress, needed for deployment | Free |
| **Node.js** | Runs your app locally on your computer during development | Free |

### Frontend (What Users See)
| Tool | What It Does | Cost |
|---|---|---|
| **Next.js** | React framework — builds fast, modern web apps | Free |
| **Tailwind CSS** | Styling without writing CSS from scratch | Free |
| **Framer Motion** | Smooth animations | Free |
| **Lucide Icons** | Clean icon set | Free |
| **Google Fonts** | Typography | Free |

### Backend (Behind the Scenes)
| Tool | What It Does | Cost |
|---|---|---|
| **Supabase** | Database + user analytics (if you want to track anonymous usage) | Free tier |
| **Anthropic API** | Powers the personalized risk summary text | Free tier ($5 credit) |
| **Google Maps API** | Powers the "find a clinic" feature | $200/month free credit |

### Deployment (Publishing It)
| Tool | What It Does | Cost |
|---|---|---|
| **Vercel** | Hosts your app on the internet, gives you a real URL | Free tier |
| **Namecheap** | Custom domain (like oralcheck.org) | ~$9/year |
| **PWA config** | Makes the site installable on phones like a real app | Free (built-in) |

### Design Assets
| Tool | What It Does | Cost |
|---|---|---|
| **Figma** | Design mockups before you build (optional but smart) | Free tier |
| **Unsplash** | Free stock photography | Free |
| **Heroicons / Lucide** | Icon libraries | Free |
| **Coolors.co** | Color palette generator | Free |

**Total cost: $0–$9** (only if you buy a domain)

---

## Design Language

This app is for regular people, potentially scared people. The design has to feel trustworthy, calm, and clinical — but not cold.

### Aesthetic Direction: "Warm Clinical"

**Color palette:**
- Primary: Deep teal (`#0D7377`) — medical trust without hospital blue
- Secondary: Warm white (`#FAF9F6`) — softer than pure white
- Accent: Coral (`#E8634A`) — for risk highlights and CTAs, suggests urgency without panic
- Text: Charcoal (`#2D2D2D`) — easier on the eyes than pure black
- Success/low risk: Sage green (`#7BA882`)
- Caution/moderate risk: Amber (`#D4A03C`)
- Alert/high risk: The coral above

**Typography:**
- Headlines: **DM Serif Display** — authoritative, editorial, warm
- Body: **Source Sans 3** — medical-grade readability, clean
- Data/stats: **JetBrains Mono** — for risk scores or percentages

**Design principles:**
- Lots of white space — don't overwhelm
- Rounded corners (12–16px) — approachable
- Subtle shadows, no hard borders
- Progress bar during questionnaire so users know how long it takes
- Icons next to every risk factor (cigarette, wine glass, sun, etc.)
- Mobile-first — most users will be on their phones
- No stock photos of mouths — use abstract illustrations or icons instead
- Animations should be gentle (fade-ins, not bounces)

**Tone of voice:**
- Second person ("You may be at higher risk...")
- Short sentences
- No medical jargon without a plain-language explanation next to it
- Encouraging, not alarming
- Always end with a clear action step

---

## App Architecture

```
oralcheck/
├── app/                        # Next.js pages
│   ├── page.tsx                # Landing page
│   ├── screener/
│   │   └── page.tsx            # The questionnaire
│   ├── results/
│   │   └── page.tsx            # Risk summary + recommendations
│   ├── find-care/
│   │   └── page.tsx            # Clinic finder map
│   ├── learn/
│   │   ├── signs/page.tsx      # Signs & symptoms guide
│   │   ├── self-exam/page.tsx  # How to do a self-exam
│   │   └── facts/page.tsx      # Oral cancer statistics
│   └── about/
│       └── page.tsx            # About the project + your bio
├── components/
│   ├── QuestionCard.tsx        # Individual question UI
│   ├── ProgressBar.tsx         # Questionnaire progress
│   ├── RiskGauge.tsx           # Visual risk display
│   ├── ClinicMap.tsx           # Google Maps integration
│   ├── ShareButton.tsx         # Share results
│   └── Layout/                 # Header, footer, nav
├── lib/
│   ├── riskEngine.ts           # Risk calculation logic
│   ├── questions.ts            # Questionnaire data
│   └── claude.ts               # API call to Claude for summaries
├── public/
│   ├── icons/                  # App icons for PWA
│   └── images/
└── styles/
    └── globals.css             # Tailwind + custom styles
```

---

## The 7 Things You Need to Build

### 1. Landing Page
**What it is:** The front door. Explains what the tool does in 5 seconds.

**Must include:**
- Headline: something like "2 minutes could save your life"
- One-sentence explainer
- Big "Start Screening" button
- Stats that hit hard (oral cancer survival rates, how early detection changes outcomes)
- Footer with disclaimer: "This is not a medical diagnosis"

**Claude Code prompt to start:**
> "Build me a Next.js landing page with a hero section, a stats bar showing oral cancer facts, and a CTA button. Use Tailwind, DM Serif Display for headlines, Source Sans 3 for body text, teal and coral color scheme."

---

### 2. Risk Questionnaire (The Core)
**What it is:** 8–12 questions, one at a time, full screen.

**Questions to include (based on real clinical risk factors):**
- Age range
- Tobacco use (cigarettes, chewing tobacco, vaping)
- Alcohol use frequency
- HPV status / history
- Sun exposure (lip cancer risk)
- History of mouth sores lasting 2+ weeks
- Family history of head/neck cancers
- Diet (low fruit/vegetable intake)
- Dental visit frequency
- Betel nut use (relevant for some populations)

**UI details:**
- One question per screen with large tap targets
- Progress bar at top
- Back button
- Answer options as big cards, not tiny radio buttons
- Smooth slide transition between questions

**How risk scoring works (you'll encode this in `riskEngine.ts`):**
- Each answer maps to a weighted point value
- Tobacco = heavy weight, diet = lighter weight
- Use published literature (CAMBRA, AACR guidelines) to inform weights
- Output a risk tier: Low / Moderate / High / See a Dentist Soon
- This is NOT an algorithm pretending to be a doctor — it's an educational estimate

---

### 3. Results Page
**What it is:** The payoff. Personalized, clear, actionable.

**Must include:**
- Visual risk gauge (think speedometer, not a number)
- 2–3 sentence personalized summary (generated by Claude API based on their answers)
- Their specific risk factors listed with explanations
- What they can do about each one
- "Find a dentist" button (links to clinic finder)
- "Share with someone you care about" button
- Disclaimer banner

**Claude API integration:**
- Send the user's anonymized answers to Claude
- Prompt Claude to generate a warm, clear 3-sentence summary
- Example: "Based on your responses, your tobacco use and infrequent dental visits put you at moderate risk. The good news is that oral cancer found early has an 89% survival rate. Here's what you can do today."

---

### 4. Clinic Finder
**What it is:** Google Maps embed that shows nearby free/low-cost dental clinics.

**How to build it:**
- Use Google Maps JavaScript API (free tier)
- On load, request user's location
- Search for dental clinics nearby using Places API
- Filter or flag community health centers, dental schools, free clinics
- Show results as map pins + a scrollable list below the map

**Data sources for free clinics:**
- HRSA (Health Resources & Services Administration) has a public API of federally funded health centers
- Dental school clinic directories
- You could also hardcode a curated list for your area to start

---

### 5. Educational Pages
**What it is:** 2–3 pages of genuinely useful health content.

**Page 1: Signs & Symptoms**
- Red/white patches in the mouth
- Sores that don't heal in 2 weeks
- Lumps or thickening
- Difficulty swallowing
- Ear pain
- Use illustrations, not photos

**Page 2: How to Do a Self-Exam**
- Step-by-step guide (lips, gums, tongue, floor of mouth, palate, throat)
- Could include a simple diagram
- Takes 2 minutes — emphasize this

**Page 3: Facts & Stats**
- Incidence rates
- Survival rates by stage
- Demographics most affected
- HPV connection (this is the fastest-growing cause and many people don't know)

---

### 6. About Page
**What it is:** Your credibility page. This is the resume piece.

**Must include:**
- Your name and that you're a predental student
- Why you built this (personal mission statement)
- Sources cited (medical literature you referenced)
- Link to your LinkedIn
- Contact info

---

### 7. PWA Configuration (Making It "App-Like")
**What it is:** A few config files that make your website installable on phones.

**What you need:**
- `manifest.json` — app name, icons, theme color
- Service worker — enables offline access to educational pages
- Meta tags in the HTML head for iOS/Android
- Next.js has built-in PWA support via `next-pwa` package

**Result:** Users can tap "Add to Home Screen" and get an app icon. No App Store needed. Free.

---

## Build Order (Your Sprint Plan)

| Week | What to Build | Claude Code Can Handle |
|---|---|---|
| **Week 1** | Set up the project, build the landing page | 95% — just describe what you want |
| **Week 2** | Build the questionnaire UI + risk engine logic | 85% — you'll need to verify the medical accuracy of weights |
| **Week 3** | Build the results page + Claude API integration | 90% — describe the output format you want |
| **Week 4** | Build the clinic finder with Google Maps | 80% — API key setup is manual but Claude Code writes the rest |
| **Week 5** | Build educational pages + about page | 95% — content-heavy, Claude Code excels here |
| **Week 6** | PWA setup, polish, responsive testing, deploy to Vercel | 85% — deployment has a few manual steps |

---

## How to Deploy (Publish It Live)

### Step 1: Push to GitHub
Claude Code can help you set up a Git repo. You'll create a free GitHub account if you don't have one, then push your code.

### Step 2: Connect to Vercel
- Go to vercel.com, sign up free with your GitHub account
- Click "Import Project" and select your repo
- Vercel auto-detects Next.js and deploys it
- You get a free URL like `oralcheck.vercel.app`

### Step 3: Custom Domain (Optional, ~$9)
- Buy a domain on Namecheap (like oralcheck.org)
- Point it to Vercel in your domain settings (Vercel walks you through this)
- Now you have a real URL to put on your resume

### Step 4: PWA
- With the manifest and service worker configured, users on mobile can install it
- No App Store submission, no fees, no approval process

---

## Resume Line

When it's done, here's how you put it on your resume:

> **OralCheck — Oral Cancer Risk Awareness Tool** | Creator & Developer
> Built a patient-facing web application that educates users on oral cancer risk factors, provides personalized screening recommendations, and connects underserved populations with free dental care. Used AI to generate accessible health summaries. [oralcheck.org]

---

## First Thing to Do Right Now

1. Install Claude Code (or open it if you have it)
2. Say: *"Create a new Next.js project called oralcheck with Tailwind CSS and TypeScript. Set up the folder structure with pages for home, screener, results, find-care, learn, and about."*
3. You're building.
