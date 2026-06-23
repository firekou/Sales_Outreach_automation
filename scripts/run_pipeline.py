#!/usr/bin/env python3
"""
AI Token King — Workshop Pipeline Runner
=========================================
Run this after filling in workshop_config.py and .env.

    cd scripts
    python run_pipeline.py

What it does:
  Step 1 — Scrapes LinkedIn leads matching your search combos (via Apify)
  Step 2 — Generates personalised message drafts in your language (via Claude AI)
  Step 3 — Exports a ready-to-import CSV for Dripify or Expandi

Output: scripts/output/dripify_<yourname>_<timestamp>.csv
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ── Load participant config ───────────────────────────────────────────
try:
    from workshop_config import MY_ACCOUNT_KEY, MY_ACCOUNT
except ImportError:
    print("❌  workshop_config.py not found.")
    print("   Make sure you're running this from inside the scripts/ directory:")
    print("       cd scripts")
    print("       python run_pipeline.py")
    sys.exit(1)

if MY_ACCOUNT_KEY == "yourname":
    print("❌  You haven't filled in workshop_config.py yet.")
    print("   Open scripts/workshop_config.py and set MY_ACCOUNT_KEY to your name.")
    sys.exit(1)

SCRIPTS_DIR = Path(__file__).parent
OUTPUT_DIR  = SCRIPTS_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
PYTHON      = sys.executable


# ── Helpers ──────────────────────────────────────────────────────────
def banner(text):
    print(f"\n{'─' * 60}")
    print(f"  {text}")
    print(f"{'─' * 60}")

def run_step(label, cmd):
    banner(label)
    result = subprocess.run(cmd, cwd=SCRIPTS_DIR)
    if result.returncode != 0:
        print(f"\n❌  Step failed (exit code {result.returncode}).")
        print("    Read the error message above, fix it, then re-run.")
        sys.exit(result.returncode)

def latest(pattern):
    files = sorted(OUTPUT_DIR.glob(pattern), key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0].name if files else None


# ── Main ─────────────────────────────────────────────────────────────
def main():
    print(f"\n{'=' * 60}")
    print(f"  AI Token King — Workshop Pipeline")
    print(f"  Account : {MY_ACCOUNT_KEY}  ({MY_ACCOUNT['display_name']})")
    print(f"  Started : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'=' * 60}")
    print(f"\n  ⏱  Total estimated time: 50–60 minutes")
    print(f"  (Most of that is Step 1 waiting on Apify — go grab a coffee.)")

    # ── Step 1: Scrape ───────────────────────────────────────────────
    run_step(
        "STEP 1 / 3 — Scraping LinkedIn leads via Apify  (~45 min)",
        [PYTHON, "apify_linkedin_scraper.py",
         "--account", MY_ACCOUNT_KEY,
         "--skip-asana-dedup"],
    )

    leads_csv = latest("leads_v2_*.csv")
    if not leads_csv:
        print("❌  No leads CSV found after scraping. Something went wrong in Step 1.")
        sys.exit(1)
    print(f"\n  ✅ Leads saved → output/{leads_csv}")

    # ── Step 2: Draft ────────────────────────────────────────────────
    run_step(
        "STEP 2 / 3 — Generating personalised message drafts via Claude AI  (~10 min)",
        [PYTHON, "linkedin_processor.py",
         "draft", f"output/{leads_csv}",
         "--account", MY_ACCOUNT_KEY],
    )

    drafts_json = latest("drafts_*.json")
    if not drafts_json:
        print("❌  No drafts JSON found after Step 2. Something went wrong.")
        sys.exit(1)
    print(f"\n  ✅ Drafts saved → output/{drafts_json}")

    # ── Step 3: Export ───────────────────────────────────────────────
    run_step(
        "STEP 3 / 3 — Exporting Dripify / Expandi import CSV",
        [PYTHON, "dripify_export.py",
         f"output/{drafts_json}",
         "--account", MY_ACCOUNT_KEY],
    )

    final_csv = latest(f"dripify_{MY_ACCOUNT_KEY}_*.csv") or latest("dripify_*.csv")

    print(f"\n{'=' * 60}")
    print(f"  ✅  PIPELINE COMPLETE")
    print(f"{'=' * 60}")
    if final_csv:
        print(f"\n  Your output CSV:")
        print(f"  📄  scripts/output/{final_csv}")
        print(f"\n  Import this file into Dripify or Expandi to launch your campaign.")
        print(f"  Set your campaign messages to {{{{custom1}}}} and {{{{custom2}}}}.")
    print()


if __name__ == "__main__":
    main()
