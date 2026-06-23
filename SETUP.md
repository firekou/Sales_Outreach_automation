# Workshop Setup Guide

This guide walks you through running the LinkedIn outreach pipeline from scratch.  
No technical background needed — just follow the steps in order.

**Time required:** ~15 minutes to set up. The pipeline itself takes ~60 minutes to run (mostly waiting on LinkedIn to return data).

---

## What you'll build

By the end, you'll have a CSV file you can import directly into Dripify or Expandi.
It contains personalised LinkedIn connection request notes and follow-up messages written by Claude AI — one unique message per lead, tailored to that person's background.

---

## Step 1 — Install Python

You need Python 3.9 or newer.

**Check if you already have it:**
Open your terminal (Mac: `Terminal` app, Windows: `Command Prompt`) and type:
```
python3 --version
```

If you see `Python 3.9.x` or higher, skip to Step 2.

If not, download it from **https://python.org/downloads** and install it.

---

## Step 2 — Clone the repo

In your terminal:
```bash
git clone -b workshop/participant-setup https://github.com/antonioduran-insight/Antonio_Sales_Outreach_automation.git
cd Antonio_Sales_Outreach_automation
```

If you don't have git, download the repo as a ZIP from GitHub instead:
GitHub page → green **Code** button → **Download ZIP** → unzip it → open the folder in terminal.

---

## Step 3 — Install dependencies

```bash
cd scripts
pip3 install -r requirements.txt
```

This installs all the Python libraries the pipeline needs. It takes about 1 minute.

---

## Step 4 — Create your .env file

This file holds your API keys. It is **never uploaded to GitHub** (it's in `.gitignore`).

```bash
cp .env.example .env
```

Now open `.env` in any text editor and fill in:

| Field | What to put |
|---|---|
| `ANTHROPIC_API_KEY` | The shared key your workshop organiser gave you |
| `APIFY_TOKEN` | Your own Apify token (see below) |

**Getting your Apify token:**
1. Go to https://console.apify.com and create a free account
2. Click your avatar → **Settings** → **Integrations**
3. Under **API tokens**, click **+ Create new token**
4. Copy the token and paste it into `.env`

Leave all other fields blank — they're not needed for the workshop.

---

## Step 5 — Configure your account

Open `scripts/workshop_config.py` in a text editor. You'll see three sections:

### Section 1 — Who are you?

```python
MY_ACCOUNT_KEY = "yourname"   # change to your first name, e.g. "sarah"

MY_ACCOUNT = {
    "display_name": "Your Full Name",          # e.g. "Sarah Chen"
    "title":        "Your Role, Company Name", # e.g. "Head of Growth, Acme AI"
    "style_hint":   "...",                     # how you want to sound in messages
    "icp_focus":    [...],                     # job titles you're targeting
    "daily_limit":  20,
    "send_window":  "09:00–10:00",
}
```

### Section 2 — Where are you targeting?

Pick your target countries from the list of geo IDs in the file:

```python
MY_GEOS = [
    104187078,  # Taiwan
    101355337,  # Japan
]
```

### Section 3 — What kind of people?

Each "combo" is one LinkedIn search. Adjust the `title_keywords` to match your ICP.
Change `"limit": 20` to `"limit": 80` when you're ready for a full run.

---

## Step 6 — Run the pipeline

```bash
cd scripts          # make sure you're in the scripts/ folder
python3 run_pipeline.py
```

You'll see three steps run in sequence with progress updates in the terminal.

| Step | What happens | Time |
|---|---|---|
| 1 — Scrape | Pulls leads from LinkedIn Sales Navigator via Apify | ~45 min |
| 2 — Draft | Claude AI writes personalised messages for each lead | ~10 min |
| 3 — Export | Generates your final CSV | < 1 min |

Go make a coffee after starting Step 1. The script will wait for you.

---

## Step 7 — Find your output CSV

When the pipeline finishes, it tells you exactly where your file is:

```
📄  scripts/output/dripify_yourname_20260617_HHMMSS.csv
```

Open the `scripts/output/` folder — your file is the most recently created one.

---

## Step 7 — Send your CSV to Antonio

When the pipeline finishes, find your output file in `scripts/output/` — it will be named `dripify_yourname_date_time.csv`

Send this file to Antonio (Slack or email). He will consolidate all CSVs, remove duplicates, and import them into the team CRM where your leads will be waiting for you.

---

## LinkedIn function categories (for search combos)

When writing your own search combos in `workshop_config.py`, the `functions` field must use one of these exact values:

```
Accounting, Administrative, Arts and Design, Business Development,
Community and Social Services, Consulting, Education, Engineering,
Entrepreneurship, Finance, Healthcare Services, Human Resources,
Information Technology, Legal, Marketing, Media and Communication,
Military and Protective Services, Operations, Product Management,
Program and Project Management, Purchasing, Quality Assurance,
Real Estate, Research, Sales, Customer Success and Support
```

And `seniority_levels` must be one of:
```
Owner/Partner, CXO, Vice President, Director,
Experienced Manager, Entry Level Manager, Strategic,
Senior, Entry Level, In Training
```

---

## Troubleshooting

**`ModuleNotFoundError`**  
Run `pip3 install -r requirements.txt` again.

**`APIFY_TOKEN` error**  
Make sure you created a `.env` file (not just edited `.env.example`).

**`MY_ACCOUNT_KEY == "yourname"` error**  
You haven't edited `workshop_config.py` yet. Open it and fill in your name.

**Apify returns 0 leads**  
Your search combo filters may be too narrow. Try removing some `functions` filters or expanding `company_headcounts`.

**Apify "monthly usage limit exceeded"**  
You've used up your Apify free tier. Upgrade your plan or wait until next month.

**Claude API error**  
Check that `ANTHROPIC_API_KEY` is correctly pasted in `.env` with no extra spaces.
