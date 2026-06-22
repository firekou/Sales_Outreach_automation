#!/usr/bin/env python3
"""
AI Token King — Asana CRM 去重模組
在 Lead 匯入前，先比對 Asana 現有任務，避免任何帳號重複聯繫同一個人。

用法（模組引入）：
  from asana_dedup import get_existing_urls, filter_new_leads

用法（CLI）：
  python asana_dedup.py check output/leads_xxx.csv   ← 過濾新 Lead，輸出 new_leads_xxx.csv
  python asana_dedup.py stats                        ← 顯示 Asana CRM 統計
  python asana_dedup.py lookup linkedin.com/in/xxx   ← 查詢特定 URL 是否已存在

環境變數（.env）：
  ASANA_TOKEN        — Asana Personal Access Token
  ASANA_PROJECT_GID  — LinkedIn CRM 專案的 GID（URL 中的數字）
"""

import os
import sys
import csv
from pathlib import Path
from typing import Optional

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("請先安裝：pip install requests python-dotenv")
    raise

load_dotenv()
ASANA_TOKEN       = os.getenv("ASANA_TOKEN", "")
ASANA_PROJECT_GID = os.getenv("ASANA_PROJECT_GID", "")
ASANA_BASE_URL    = "https://app.asana.com/api/1.0"


def _headers() -> dict:
    if not ASANA_TOKEN:
        raise SystemExit("❌ 缺少 ASANA_TOKEN，請在 .env 設定（Asana → My Settings → Apps → Personal Access Tokens）")
    return {
        "Authorization": f"Bearer {ASANA_TOKEN}",
        "Accept": "application/json",
    }


def _get_tasks_page(project_gid: str, offset: Optional[str] = None) -> dict:
    params = {
        "opt_fields": "name,custom_fields.name,custom_fields.text_value,custom_fields.display_value",
        "limit": 100,
    }
    if offset:
        params["offset"] = offset
    resp = requests.get(
        f"{ASANA_BASE_URL}/projects/{project_gid}/tasks",
        headers=_headers(),
        params=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def normalize_url(url: str) -> str:
    """標準化 LinkedIn URL 格式（小寫、去尾斜線、去 query string）"""
    url = url.strip().lower().rstrip("/")
    if "?" in url:
        url = url.split("?")[0]
    return url


def get_existing_urls(project_gid: str = "") -> set:
    """
    從 Asana 專案取得所有已存在的 LinkedIn URL（任何帳號聯繫過的）。
    返回標準化後的 URL set，供去重使用。
    """
    gid = project_gid or ASANA_PROJECT_GID
    if not gid:
        return set()

    existing = set()
    offset = None

    while True:
        data = _get_tasks_page(gid, offset)
        tasks = data.get("data", [])

        for task in tasks:
            for cf in task.get("custom_fields", []):
                field_name = (cf.get("name") or "").lower()
                if "linkedin" in field_name and "url" in field_name:
                    val = cf.get("text_value") or cf.get("display_value") or ""
                    if val.strip():
                        existing.add(normalize_url(val))

        next_page = data.get("next_page")
        if not next_page:
            break
        offset = next_page.get("offset")

    return existing


def filter_new_leads(leads: list, existing_urls: set) -> tuple:
    """
    將 leads 分成 (new_leads, duplicate_leads)。
    已在 Asana 的 Lead 視為重複，不再匯入。
    """
    new_leads, duplicates = [], []
    for lead in leads:
        url = normalize_url(lead.get("linkedin_url", ""))
        if url and url in existing_urls:
            duplicates.append(lead)
        else:
            new_leads.append(lead)
    return new_leads, duplicates


# ── CLI 指令 ──────────────────────────────────────────────

def cmd_check(csv_path: str):
    """過濾 CSV 中已在 Asana 的 Lead，輸出純新 Lead 清單"""
    leads = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    print(f"\n🔍 查詢 Asana CRM 現有 Lead（project: {ASANA_PROJECT_GID or '未設定'}）...")

    if not ASANA_PROJECT_GID:
        print("⚠ ASANA_PROJECT_GID 未設定，無法去重。請在 .env 設定。")
        return

    existing = get_existing_urls()
    new_leads, duplicates = filter_new_leads(leads, existing)

    print(f"\n📊 結果：")
    print(f"  CSV 總計     ：{len(leads)} 筆")
    print(f"  已在 Asana   ：{len(duplicates)} 筆  ← 跳過（任何帳號聯繫過）")
    print(f"  新 Lead      ：{len(new_leads)} 筆  ← 可匯入")

    if duplicates:
        print(f"\n  重複的 Lead（前10筆）：")
        for l in duplicates[:10]:
            print(f"    {l.get('name','?')} | {l.get('company','?')} | {l.get('linkedin_url','')[:55]}")
        if len(duplicates) > 10:
            print(f"    ... 還有 {len(duplicates)-10} 筆")

    if new_leads:
        out = Path(csv_path).parent / f"new_{Path(csv_path).name}"
        with out.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=leads[0].keys())
            writer.writeheader()
            writer.writerows(new_leads)
        print(f"\n  ✅ 新 Lead 已存為：{out.name}")
    else:
        print(f"\n  ℹ 所有 Lead 都已在 Asana，無需匯入。")


def cmd_stats():
    """顯示 Asana CRM LinkedIn URL 統計"""
    if not ASANA_PROJECT_GID:
        print("⚠ ASANA_PROJECT_GID 未設定")
        return
    print(f"\n📊 Asana CRM 統計（project: {ASANA_PROJECT_GID}）...")
    existing = get_existing_urls()
    print(f"  已有 LinkedIn URL：{len(existing)} 筆（跨所有帳號）")


def cmd_lookup(linkedin_url: str):
    """查詢特定 LinkedIn URL 是否已在 Asana CRM"""
    if not ASANA_PROJECT_GID:
        print("⚠ ASANA_PROJECT_GID 未設定")
        return
    normalized = normalize_url(linkedin_url)
    print(f"\n🔍 查詢：{normalized}")
    existing = get_existing_urls()
    if normalized in existing:
        print(f"  ✅ 已在 Asana CRM（不重複觸達）")
    else:
        print(f"  ❌ 不在 Asana CRM（可加入觸達佇列）")


def main():
    if len(sys.argv) < 2:
        print("\nAI Token King — Asana CRM 去重工具")
        print("\n用法：python asana_dedup.py <指令> [參數]\n")
        print("  check  <leads.csv>      — 過濾 CSV，輸出純新 Lead")
        print("  stats                   — 顯示 Asana CRM 統計")
        print("  lookup <linkedin_url>   — 查詢特定 URL 是否存在")
        print()
        sys.exit(0)

    cmd = sys.argv[1]
    if cmd == "check":
        if len(sys.argv) < 3:
            print("❌ 請提供 CSV 路徑")
            sys.exit(1)
        cmd_check(sys.argv[2])
    elif cmd == "stats":
        cmd_stats()
    elif cmd == "lookup":
        if len(sys.argv) < 3:
            print("❌ 請提供 LinkedIn URL")
            sys.exit(1)
        cmd_lookup(sys.argv[2])
    else:
        print(f"❌ 未知指令：{cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
