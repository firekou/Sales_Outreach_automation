#!/usr/bin/env python3
"""
Expandi Campaign Setup Script
Usage: python3 scripts/expandi_setup_campaign.py

Creates "S1-Frank-20260615" Sales Navigator campaign in Expandi with:
- 4-step sequence: Visit Profile → Connect → Day1 Message → Day7 Follow-up
- 15 leads from lead-drafts/s1-batch-20260615-expandi.csv
- 25 connections/day, 08:00-09:00 Taipei time

Credentials: set EXPANDI_API_KEY and EXPANDI_API_SECRET env vars,
or edit the constants below.
"""

import csv
import json
import os
import sys
import time
import requests
from pathlib import Path

# ── Credentials (set via env vars, do NOT commit actual values) ──────────────
API_KEY    = os.environ.get("EXPANDI_API_KEY",    "4a0ea236-d270-49ab-8856-590d0c180d1a")
API_SECRET = os.environ.get("EXPANDI_API_SECRET", "7cfec9d1-15dc-4556-8fa2-26c075a01f35")

BASE_URL   = "https://api.expandi.io/api/v1"
CSV_PATH   = Path(__file__).parent.parent / "lead-drafts" / "s1-batch-20260615-expandi.csv"

CAMPAIGN_NAME     = "S1-Frank-20260615"
DAILY_LIMIT       = 25
WORKING_HOURS_START = 8   # 08:00 Taipei (UTC+8)
WORKING_HOURS_END   = 9   # 09:00 Taipei

# ── Session setup ─────────────────────────────────────────────────────────────
session = requests.Session()
session.auth = (API_KEY, API_SECRET)
session.headers.update({
    "Content-Type": "application/json",
    "Accept": "application/json",
})

def api(method, path, **kwargs):
    url = f"{BASE_URL}{path}"
    r = getattr(session, method)(url, **kwargs)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    if not r.ok:
        print(f"  ✗ {method.upper()} {path} → {r.status_code}: {data}")
        r.raise_for_status()
    return data


def step1_get_account():
    """Get Frank's LinkedIn account ID."""
    print("1. Fetching LinkedIn accounts...")
    data = api("get", "/accounts")
    accounts = data if isinstance(data, list) else data.get("data", [data])
    print(f"   Found {len(accounts)} account(s):")
    for a in accounts:
        print(f"   - [{a.get('id')}] {a.get('name')} | {a.get('email')} | {a.get('status')}")
    # Return first active account (Frank)
    active = [a for a in accounts if a.get("status") in ("active", "connected", None)]
    if not active:
        raise RuntimeError("No active accounts found. Connect Frank's LinkedIn in Expandi first.")
    chosen = active[0]
    print(f"   ✓ Using account: {chosen.get('name')} (id={chosen.get('id')})")
    return chosen["id"]


def step2_create_campaign(account_id):
    """Create the Sales Navigator campaign."""
    print(f"\n2. Creating campaign '{CAMPAIGN_NAME}'...")
    payload = {
        "name": CAMPAIGN_NAME,
        "type": "sales_navigator",          # Sales Navigator campaign type
        "accountId": account_id,
        "settings": {
            "dailyConnectionLimit": DAILY_LIMIT,
            "workingHoursStart": WORKING_HOURS_START,
            "workingHoursEnd": WORKING_HOURS_END,
            "timezone": "Asia/Taipei",
            "smartLimits": True,
            "weekends": False,
        }
    }
    data = api("post", "/campaigns", json=payload)
    campaign_id = data.get("id") or data.get("data", {}).get("id")
    print(f"   ✓ Campaign created: id={campaign_id}")
    return campaign_id


def step3_setup_sequence(campaign_id):
    """Set up the 4-step sequence."""
    print("\n3. Setting up sequence steps...")

    steps = [
        {
            "type": "view_profile",
            "order": 1,
            "delay": 0,          # seconds after previous step
        },
        {
            "type": "connect",
            "order": 2,
            "delay": 3600,       # 1 hour after visiting profile
            "message": "{{custom1}}",
        },
        {
            "type": "message",
            "order": 3,
            "delay": 86400,      # 1 day after connection accepted
            "waitForAcceptance": True,
            "message": "{{custom2}}",
        },
        {
            "type": "message",
            "order": 4,
            "delay": 604800,     # 7 days after Step 3
            "sendOnlyIfNoReply": True,
            "message": "{{custom3}}",
        },
    ]

    for step in steps:
        result = api("post", f"/campaigns/{campaign_id}/steps", json=step)
        step_id = result.get("id") or result.get("data", {}).get("id")
        print(f"   ✓ Step {step['order']} ({step['type']}) created: id={step_id}")
        time.sleep(0.5)

    print("   ✓ Sequence configured")


def step4_import_leads(campaign_id):
    """Import 15 leads with personalized custom variables."""
    print(f"\n4. Importing leads from {CSV_PATH.name}...")

    leads = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            leads.append({
                "profileUrl": row["linkedin"],
                "firstName":  row["first_name"],
                "lastName":   row["last_name"],
                "companyName": row.get("company_name", ""),
                "position":   row.get("position", ""),
                "location":   row.get("location", ""),
                "custom1":    row["custom1"],
                "custom2":    row["custom2"],
                "custom3":    row["custom3"],
                "tags":       row.get("tags", "S1,frank"),
            })

    print(f"   Loaded {len(leads)} leads, importing in batch...")
    payload = {"leads": leads}
    result = api("post", f"/campaigns/{campaign_id}/leads", json=payload)
    imported = result.get("imported") or result.get("data", {}).get("imported", len(leads))
    print(f"   ✓ {imported} leads imported")
    return imported


def step5_activate_campaign(campaign_id):
    """Activate (start) the campaign."""
    print(f"\n5. Activating campaign {campaign_id}...")
    result = api("patch", f"/campaigns/{campaign_id}", json={"status": "active"})
    status = result.get("status") or result.get("data", {}).get("status")
    print(f"   ✓ Campaign status: {status}")


def main():
    print("=" * 60)
    print("Expandi Campaign Setup — S1-Frank-20260615")
    print("=" * 60)

    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found at {CSV_PATH}")
        sys.exit(1)

    try:
        account_id  = step1_get_account()
        campaign_id = step2_create_campaign(account_id)
        step3_setup_sequence(campaign_id)
        step4_import_leads(campaign_id)
        step5_activate_campaign(campaign_id)

        print("\n" + "=" * 60)
        print("✅ DONE — Campaign is live!")
        print(f"   Name:       {CAMPAIGN_NAME}")
        print(f"   Campaign ID: {campaign_id}")
        print(f"   Leads:       15")
        print(f"   Schedule:    08:00–09:00 Taipei, 25/day")
        print(f"   View at:     https://app.expandi.io/campaigns/{campaign_id}")
        print("=" * 60)

    except requests.HTTPError as e:
        print(f"\n✗ API Error: {e}")
        print("Check that:")
        print("  1. EXPANDI_API_KEY / EXPANDI_API_SECRET are correct")
        print("  2. Frank's LinkedIn account is connected in Expandi")
        print("  3. Your Expandi plan supports Sales Navigator campaigns")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise


if __name__ == "__main__":
    main()
