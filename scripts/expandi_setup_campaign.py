#!/usr/bin/env python3
"""
Expandi Campaign Setup — S1-Frank-20260619
109 leads (原 Kid 帳號轉 Frank), TA 痛點個人化訊息
"""
import csv, json, os, sys, time
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

API_KEY    = os.environ.get("EXPANDI_API_KEY")
API_SECRET = os.environ.get("EXPANDI_API_SECRET")

if not API_KEY or not API_SECRET:
    print("ERROR: Set EXPANDI_API_KEY and EXPANDI_API_SECRET in .env")
    sys.exit(1)

BASE_URL        = "https://api.expandi.io/api/v1"
CSV_PATH        = Path(__file__).parent.parent / "lead-drafts" / "s1-batch-20260619-expandi.csv"
CAMPAIGN_NAME   = "S1-Frank-20260619"
DAILY_LIMIT     = 25
HOURS_START     = 8
HOURS_END       = 9

session = requests.Session()
session.auth = (API_KEY, API_SECRET)
session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})

def api(method, path, **kwargs):
    url = f"{BASE_URL}{path}"
    r = getattr(session, method)(url, **kwargs)
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text}
    if not r.ok:
        print(f"  ✗ {method.upper()} {path} → {r.status_code}: {json.dumps(data, ensure_ascii=False)[:300]}")
        r.raise_for_status()
    return data

def step1_get_account():
    print("1. Fetching LinkedIn accounts...")
    data = api("get", "/accounts")
    accounts = data if isinstance(data, list) else data.get("data", [data])
    print(f"   Found {len(accounts)} account(s):")
    for a in accounts:
        print(f"   - [{a.get('id')}] {a.get('name')} | {a.get('email')} | {a.get('status')}")
    active = [a for a in accounts if a.get("status") in ("active", "connected", None)]
    if not active:
        raise RuntimeError("No active accounts. Connect Frank's LinkedIn in Expandi first.")
    # Pick Frank's account
    chosen = active[0]
    print(f"   ✓ Using: {chosen.get('name')} (id={chosen.get('id')})")
    return chosen["id"]

def step2_create_campaign(account_id):
    print(f"\n2. Creating campaign '{CAMPAIGN_NAME}'...")
    payload = {
        "name": CAMPAIGN_NAME,
        "type": "sales_navigator",
        "accountId": account_id,
        "settings": {
            "dailyConnectionLimit": DAILY_LIMIT,
            "workingHoursStart": HOURS_START,
            "workingHoursEnd": HOURS_END,
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
    print("\n3. Setting up 4-step sequence...")
    steps = [
        {"type": "view_profile",  "order": 1, "delay": 0},
        {"type": "connect",       "order": 2, "delay": 3600,   "message": "{{custom1}}"},
        {"type": "message",       "order": 3, "delay": 86400,  "waitForAcceptance": True,       "message": "{{custom2}}"},
        {"type": "message",       "order": 4, "delay": 604800, "sendOnlyIfNoReply": True,        "message": "{{custom3}}"},
    ]
    for step in steps:
        result = api("post", f"/campaigns/{campaign_id}/steps", json=step)
        sid = result.get("id") or result.get("data", {}).get("id")
        print(f"   ✓ Step {step['order']} ({step['type']}) id={sid}")
        time.sleep(0.5)

def step4_import_leads(campaign_id):
    print(f"\n4. Importing leads from {CSV_PATH.name}...")
    leads = []
    with open(CSV_PATH, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            leads.append({
                "profileUrl":  row["linkedin_url"],
                "firstName":   row["first_name"],
                "lastName":    row["last_name"],
                "companyName": row.get("company", ""),
                "position":    row.get("title", ""),
                "custom1":     row["custom_variable_1"],
                "custom2":     row["custom_variable_2"],
                "custom3":     row["custom_variable_3"],
                "tags":        "S1,frank,20260619",
            })
    print(f"   Loaded {len(leads)} leads, importing...")
    result = api("post", f"/campaigns/{campaign_id}/leads", json={"leads": leads})
    imported = result.get("imported") or result.get("data", {}).get("imported", len(leads))
    print(f"   ✓ {imported} leads imported")
    return imported

def step5_activate(campaign_id):
    print(f"\n5. Activating campaign...")
    result = api("patch", f"/campaigns/{campaign_id}", json={"status": "active"})
    status = result.get("status") or result.get("data", {}).get("status", "active")
    print(f"   ✓ Status: {status}")

def main():
    print("=" * 60)
    print(f"  Expandi Setup — {CAMPAIGN_NAME}")
    print("=" * 60)

    if not CSV_PATH.exists():
        print(f"ERROR: CSV not found: {CSV_PATH}")
        sys.exit(1)

    try:
        account_id  = step1_get_account()
        campaign_id = step2_create_campaign(account_id)
        step3_setup_sequence(campaign_id)
        step4_import_leads(campaign_id)
        step5_activate(campaign_id)

        print("\n" + "=" * 60)
        print("✅ Campaign is LIVE!")
        print(f"   Name:     {CAMPAIGN_NAME}")
        print(f"   ID:       {campaign_id}")
        print(f"   Leads:    109")
        print(f"   Schedule: 08:00–09:00 Taipei, {DAILY_LIMIT}/day, weekdays only")
        print(f"   URL:      https://app.expandi.io/campaigns/{campaign_id}")
        print("=" * 60)

    except requests.HTTPError as e:
        print(f"\n✗ API Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise

if __name__ == "__main__":
    main()
