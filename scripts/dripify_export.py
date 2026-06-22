#!/usr/bin/env python3
"""
AI Token King — Dripify 匯入 CSV 產生器

將 linkedin_processor.py draft 輸出的 drafts_*.json 轉換為
Dripify 可直接匯入的 CSV 格式，並帶入 Claude 生成的個人化訊息。

Dripify 欄位對應：
  custom1 ← connection_request（連結請求附言，≤300字元，Dripify campaign 設定 {{custom1}}）
  custom2 ← value_touch（第一封價值觸達訊息，≤500字元，Follow-up 1 設定 {{custom2}}）

Dripify Campaign 設定方式：
  連結請求訊息：{{custom1}}
  Follow-up 1（已連結後 Day 3）：{{custom2}}
  ── 以上讓每個 Lead 收到 Claude 生成的獨立個人化內容 ──

用法：
  python dripify_export.py output/drafts_xxx.json [--account frank]
  python dripify_export.py output/leads_xxx.csv   [--account frank]  ← 無草稿模式
"""

import os
import re
import sys
import csv
import json
import argparse
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# Dripify CSV 標準欄位順序
DRIPIFY_FIELDS = [
    "linkedin",
    "first_name",
    "last_name",
    "company_name",
    "position",
    "email",
    "location",
    "tags",
    "custom1",
    "custom2",
    "custom3",
]

# 連結請求訊息上限（LinkedIn 限制）
CONN_MSG_LIMIT = 300
VALUE_MSG_LIMIT = 1900  # LinkedIn 訊息上限


def split_name(full_name: str) -> tuple[str, str]:
    """
    將全名拆分為 (first_name, last_name)。
    支援英文、中文、中英混合名字。
    """
    if not full_name:
        return "", ""

    full_name = full_name.strip()

    # 純中文名：2-4 字（姓1字 + 名1-3字）
    if re.match(r"^[一-鿿·•]{2,5}$", full_name):
        last = full_name[0]
        first = full_name[1:]
        return first, last

    # 英文/混合：以空格拆分，最後一段為 last_name
    parts = full_name.split()
    if len(parts) == 1:
        return full_name, ""
    if len(parts) == 2:
        return parts[0], parts[1]
    # 多段：第一段為 first_name，最後一段為 last_name，中間合入 first_name
    return " ".join(parts[:-1]), parts[-1]


def truncate(text: str, limit: int, label: str = "") -> str:
    """截斷超過 LinkedIn / Dripify 限制的文字，並提示"""
    if not text:
        return ""
    if len(text) > limit:
        truncated = text[:limit - 3] + "..."
        if label:
            print(f"  ⚠ {label} 超過 {limit} 字元（{len(text)}），已截斷")
        return truncated
    return text


def build_tags(lead: dict, account: str) -> str:
    """組合 Dripify tags（用逗號分隔）"""
    tags = []
    cls = lead.get("classification", "")
    if cls:
        tags.append(cls)
    acc = lead.get("source_account") or account
    if acc:
        tags.append(acc)
    track = lead.get("sales_track", "")
    if track:
        tags.append(track)
    combo = lead.get("combo_name") or lead.get("search_combo", "")
    if combo:
        # 取組合代碼（如 combo_A）
        code = lead.get("search_combo", "").replace("組合", "combo_")
        if code:
            tags.append(code)
    return ",".join(tags)


def from_drafts_json(json_path: str, account: str) -> list[dict]:
    """從 drafts JSON 建立 Dripify 資料列（含個人化訊息）"""
    drafts = json.loads(Path(json_path).read_text(encoding="utf-8"))
    rows = []
    skipped = 0

    for d in drafts:
        url = d.get("linkedin_url", "").strip()
        if not url:
            skipped += 1
            continue

        first, last = split_name(d.get("name", ""))
        conn_msg   = truncate(d.get("connection_request", ""), CONN_MSG_LIMIT,
                              f"{d.get('name')} 連結請求")
        value_msg  = truncate(d.get("value_touch", ""), VALUE_MSG_LIMIT,
                              f"{d.get('name')} 價值觸達")

        rows.append({
            "linkedin":     url,
            "first_name":   first,
            "last_name":    last,
            "company_name": d.get("company", ""),
            "position":     d.get("title", ""),
            "email":        d.get("email", ""),
            "location":     d.get("location", ""),
            "tags":         build_tags(d, account),
            "custom1":      conn_msg,
            "custom2":      value_msg,
            "custom3":      f"ICP:{d.get('icp_score','')}|{d.get('classification','')}",
        })

    if skipped:
        print(f"  ⚠ 跳過 {skipped} 筆（無 LinkedIn URL）")
    return rows


def from_leads_csv(csv_path: str, account: str) -> list[dict]:
    """從 leads CSV 建立 Dripify 資料列（無 Claude 草稿，custom1/2 為空）"""
    leads = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    hot_warm = [l for l in leads if l.get("classification") in ("HOT", "WARM")]

    print(f"  ℹ 無草稿模式：custom1/2 留空，需在 Dripify Campaign 設定通用訊息模板")
    print(f"  建議：先執行 linkedin_processor.py draft 生成草稿，再用本腳本匯出")

    rows = []
    for l in hot_warm:
        url = l.get("linkedin_url", "").strip()
        if not url:
            continue
        first, last = split_name(l.get("name", ""))
        rows.append({
            "linkedin":     url,
            "first_name":   first,
            "last_name":    last,
            "company_name": l.get("company", ""),
            "position":     l.get("title", ""),
            "email":        l.get("email", ""),
            "location":     l.get("location", ""),
            "tags":         build_tags(l, account),
            "custom1":      "",
            "custom2":      "",
            "custom3":      f"ICP:{l.get('icp_score','')}|{l.get('classification','')}",
        })
    return rows


def save_dripify_csv(rows: list[dict], account: str) -> Path:
    ts  = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = OUTPUT_DIR / f"dripify_{account}_{ts}.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=DRIPIFY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return out


def print_summary(rows: list[dict], out_path: Path, account: str):
    has_custom1 = sum(1 for r in rows if r.get("custom1"))
    hot  = sum(1 for r in rows if "HOT" in r.get("tags", ""))
    warm = sum(1 for r in rows if "WARM" in r.get("tags", ""))

    print(f"\n{'='*60}")
    print(f"  Dripify 匯入檔案已生成")
    print(f"{'='*60}")
    print(f"  檔案：{out_path.name}")
    print(f"  帳號：{account}")
    print(f"  總筆數：{len(rows)}")
    print(f"  HOT：{hot}  WARM：{warm}")
    print(f"  含個人化訊息（custom1）：{has_custom1}/{len(rows)} 筆")

    print(f"\n{'─'*60}")
    print(f"  Dripify 匯入步驟")
    print(f"{'─'*60}")
    print(f"  1. 登入 Dripify → Leads → Import → Upload CSV")
    print(f"  2. 上傳 {out_path.name}")
    print(f"  3. 欄位對應確認（linkedin → LinkedIn URL）")
    print()
    print(f"  Campaign 訊息設定（重要）：")
    print(f"  ┌──────────────────────────────────────────────┐")
    print(f"  │  連結請求：{{{{custom1}}}}                       │")
    print(f"  │  Follow-up 1（Day 3）：{{{{custom2}}}}          │")
    print(f"  │  ↑ 這樣每個人收到的都是 Claude 個人化訊息    │")
    print(f"  └──────────────────────────────────────────────┘")
    print()
    print(f"  速率設定建議（Frank 帳號，試營運階段）：")
    print(f"  • 每日連結請求上限：20-25（Dripify 設定 25）")
    print(f"  • 操作間隔：隨機 3-15 秒（Dripify 預設即可）")
    print(f"  • 發送時間：工作日 08:00-17:00 台灣時間")

    if rows:
        print(f"\n  預覽前 3 筆連結請求：")
        for r in rows[:3]:
            msg = r.get("custom1", "[無草稿]")[:80]
            print(f"  [{r.get('first_name')} {r.get('last_name')} @ {r.get('company_name')}]")
            print(f"    {msg}...")
            print()
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="AI Token King — Dripify CSV 匯出工具")
    parser.add_argument("source", help="drafts_*.json 或 leads_*.csv 路徑")
    parser.add_argument(
        "--account",
        default="frank",
        choices=["frank", "jet", "kid", "lauren", "alice"],
        help="來源帳號（預設：frank）",
    )
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.exists():
        # 嘗試在 output/ 目錄找
        alt = Path(__file__).parent / "output" / args.source
        if alt.exists():
            source_path = alt
        else:
            print(f"❌ 找不到檔案：{args.source}")
            sys.exit(1)

    print(f"\n📤 Dripify 匯出 — 帳號：{args.account}  來源：{source_path.name}")

    suffix = source_path.suffix.lower()
    if suffix == ".json":
        rows = from_drafts_json(str(source_path), args.account)
    elif suffix == ".csv":
        rows = from_leads_csv(str(source_path), args.account)
    else:
        print(f"❌ 不支援的檔案格式：{suffix}（請提供 .json 或 .csv）")
        sys.exit(1)

    if not rows:
        print("⚠ 無可匯出的資料（確認 classification 為 HOT 或 WARM）")
        sys.exit(0)

    out_path = save_dripify_csv(rows, args.account)
    print_summary(rows, out_path, args.account)


if __name__ == "__main__":
    main()
