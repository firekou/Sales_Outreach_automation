#!/usr/bin/env python3
"""
TheirStack 台灣覆蓋程度測試
搜尋使用 GPT / Claude / OpenAI 的台灣公司

用法：
  python theirstack_test.py

環境變數（.env）：
  THEIRSTACK_API_KEY=eyJhbG...
"""

import os
import json
import sys

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("請先安裝：pip install requests python-dotenv")
    sys.exit(1)

load_dotenv()
API_KEY = os.getenv("THEIRSTACK_API_KEY", "")
BASE_URL = "https://api.theirstack.com/v1"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# 搜尋組合：技術關鍵字 × 台灣地區
SEARCH_QUERIES = [
    {
        "label": "OpenAI / ChatGPT — 台灣",
        "payload": {
            "technology_slugs": ["openai"],
            "company_country_codes": ["TW"],
            "limit": 20,
            "page": 0,
        },
    },
    {
        "label": "Anthropic / Claude — 台灣",
        "payload": {
            "technology_slugs": ["anthropic"],
            "company_country_codes": ["TW"],
            "limit": 20,
            "page": 0,
        },
    },
    {
        "label": "GPT（關鍵字搜尋）— 台灣",
        "payload": {
            "technology_slugs": ["gpt-4"],
            "company_country_codes": ["TW"],
            "limit": 20,
            "page": 0,
        },
    },
    {
        "label": "LangChain — 台灣",
        "payload": {
            "technology_slugs": ["langchain"],
            "company_country_codes": ["TW"],
            "limit": 20,
            "page": 0,
        },
    },
    {
        "label": "OpenAI — 台灣（含近期徵才訊號）",
        "payload": {
            "technology_slugs": ["openai"],
            "company_country_codes": ["TW"],
            "has_job_postings": True,
            "limit": 20,
            "page": 0,
        },
    },
]


def search_companies(label: str, payload: dict) -> dict:
    """呼叫 TheirStack 公司搜尋 API"""
    resp = requests.post(
        f"{BASE_URL}/companies/search",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def print_results(label: str, data: dict):
    total = data.get("total", 0)
    companies = data.get("data", [])

    print(f"\n{'='*65}")
    print(f"  {label}")
    print(f"{'='*65}")
    print(f"  總覆蓋公司數：{total}")
    print(f"  本批回傳：{len(companies)} 筆")
    print()

    if not companies:
        print("  （無結果）")
        return

    for i, c in enumerate(companies, 1):
        name     = c.get("name", "")
        domain   = c.get("domain", "")
        country  = c.get("country", "")
        size     = c.get("employee_count") or c.get("employee_count_range", "")
        industry = c.get("industry", "")
        jobs     = c.get("job_postings_count", "")
        linkedin = c.get("linkedin_url", "")
        techs    = [t.get("name", "") for t in c.get("technologies", [])[:5]]

        print(f"  [{i:02d}] {name} ({domain})")
        print(f"        規模：{size}  |  產業：{industry}  |  國家：{country}")
        if jobs:
            print(f"        現有職缺數：{jobs}")
        if linkedin:
            print(f"        LinkedIn：{linkedin}")
        if techs:
            print(f"        AI 技術棧：{', '.join(techs)}")
        print()


def check_available_tech_slugs():
    """查詢可用的技術 slugs（確認 openai / anthropic 等 slug 存在）"""
    resp = requests.get(
        f"{BASE_URL}/technologies",
        headers=HEADERS,
        params={"q": "openai", "limit": 10},
        timeout=20,
    )
    if resp.status_code == 200:
        data = resp.json()
        items = data.get("data", data) if isinstance(data, dict) else data
        print("\n[技術 Slug 確認]")
        for t in items[:10]:
            if isinstance(t, dict):
                print(f"  slug={t.get('slug','?')}  name={t.get('name','?')}")


def main():
    if not API_KEY:
        print("❌ 請在 .env 設定 THEIRSTACK_API_KEY")
        sys.exit(1)

    print(f"\n🔍 TheirStack 台灣覆蓋測試 — API Key: ...{API_KEY[-12:]}")

    # 先確認技術 slug
    try:
        check_available_tech_slugs()
    except Exception as e:
        print(f"  ⚠ Slug 查詢失敗（{e}），繼續主搜尋")

    # 逐一執行搜尋
    results_summary = []
    for q in SEARCH_QUERIES:
        try:
            data = search_companies(q["label"], q["payload"])
            print_results(q["label"], data)
            results_summary.append({
                "label": q["label"],
                "total": data.get("total", 0),
                "returned": len(data.get("data", [])),
            })
        except requests.HTTPError as e:
            print(f"\n  ❌ {q['label']} → HTTP {e.response.status_code}: {e.response.text[:200]}")
        except Exception as e:
            print(f"\n  ❌ {q['label']} → {e}")

    # 最後印摘要
    print(f"\n{'='*65}")
    print("  覆蓋程度摘要")
    print(f"{'='*65}")
    for r in results_summary:
        bar = "█" * min(r["total"] // 5, 40) if r["total"] else ""
        print(f"  {r['label'][:40]:<40} {r['total']:>5} 家  {bar}")
    print()
    print("  ℹ 免費帳號限制：50 家公司查詢 + 200 API Credits")
    print("  ℹ 如台灣覆蓋 < 50 家，建議補用 104 手動掃描作為訊號源")


if __name__ == "__main__":
    main()
