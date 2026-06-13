#!/usr/bin/env python3
"""
AI Token King — Taiwan Reserve 500
台灣 LinkedIn Sales Navigator 儲備名單抓取器

目標：一次性批量收集 500 筆台灣潛在客戶存入儲備池，
      作為每日發送配額的後備補充來源。

與 apify_linkedin_scraper.py 的差異：
  - 目標 500 筆（而非按日限額抓取）
  - 7 個搜尋組合（擴充覆蓋範圍），總配額 650 筆緩衝去重
  - 儲存至 output/reserve/ 獨立資料夾
  - 包含所有等級（HOT / WARM / COLD），COLD 一起進儲備池
  - 支援 --target N 指定目標數量（預設 500）

Actor: bestscrapers/sales-navigator-scraper-by-filters
"""

import os
import csv
import json
import time
import logging
from datetime import datetime
from pathlib import Path

try:
    from apify_client import ApifyClient
    from dotenv import load_dotenv
except ImportError:
    print("請先安裝依賴套件：pip install -r requirements.txt")
    raise

load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN", "")
if not APIFY_TOKEN:
    raise SystemExit("❌ 缺少 APIFY_TOKEN，請在 .env 檔設定")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

ACTOR_ID = "bestscrapers/sales-navigator-scraper-by-filters"
TAIWAN_GEO = 104187078

ACCOUNTS = {
    "frank": {
        "display_name": "Frank Kao",
        "title": "CEO, AI Token King",
        "style_hint": "高層對高層，重願景與風險控管，語氣從容自信",
        "icp_focus": ["CxO", "Founder", "Co-Founder", "President", "GM", "總經理", "執行長"],
        "daily_limit": 25,
        "send_window": "08:00–09:00",
    },
    "jet": {
        "display_name": "Jet",
        "title": "Business Director, AI Token King",
        "style_hint": "商務合作切入，著重通路機會與毛利結構",
        "icp_focus": ["Channel Manager", "Partner Manager", "Solution Architect", "Sales Director", "通路經理"],
        "daily_limit": 25,
        "send_window": "10:00–11:00",
    },
    "kid": {
        "display_name": "Kid",
        "title": "業務銷售, AI Token King",
        "style_hint": "親切 ENFJ 風格，直接切痛點，主動但不卑微",
        "icp_focus": ["IT Manager", "IT Director", "CIO", "Head of IT", "資訊主管"],
        "daily_limit": 30,
        "send_window": "14:00–15:00",
    },
    "lauren": {
        "display_name": "Lauren",
        "title": "商務暨人資主管, AI Token King",
        "style_hint": "BD 合作視角，著重行銷代理商痛點與 AI 工具效率",
        "icp_focus": ["Marketing Director", "Agency Owner", "Creative Director", "Head of Marketing", "行銷總監"],
        "daily_limit": 25,
        "send_window": "16:00–17:00",
    },
    "alice": {
        "display_name": "Alice Wu",
        "title": "Product Manager, AI Token King",
        "style_hint": "產品對產品，技術同理心，INFP 溫和好奇",
        "icp_focus": ["CTO", "VP Product", "Head of Product", "Engineering Manager", "技術長"],
        "daily_limit": 20,
        "send_window": "11:00–12:00",
    },
}
DEFAULT_ACCOUNT = "kid"

# ── 7 個搜尋組合（擴充版，總配額 650 → 去重後目標 500）────────
RESERVE_COMBOS = [
    {
        "name": "組合A：科技公司IT決策者",
        "code": "combo_A",
        "priority": "P1",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "IT Manager", "IT Director", "Head of IT", "CIO",
                "Chief Information Officer", "資訊主管", "IT長",
            ],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Information Technology"],
            "seniority_levels": ["Director", "Experienced Manager", "CXO"],
            "posted_on_linkedin": "true",
            "limit": 100,
        },
    },
    {
        "name": "組合B：行銷代理商高層",
        "code": "combo_B",
        "priority": "P2",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "Marketing Director", "Head of Marketing", "Creative Director",
                "Head of Content", "Digital Marketing Manager",
                "Agency Owner", "行銷總監",
            ],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Marketing"],
            "seniority_levels": ["Director", "Owner/Partner", "CXO"],
            "posted_on_linkedin": "true",
            "limit": 80,
        },
    },
    {
        "name": "組合C：數位轉型顧問/服務商",
        "code": "combo_C",
        "priority": "P3",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "Digital Transformation", "AI Consultant", "Innovation Manager",
                "CDO", "Head of Digital", "數位轉型",
            ],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Consulting", "Information Technology"],
            "seniority_levels": ["Director", "CXO", "Experienced Manager"],
            "posted_on_linkedin": "true",
            "limit": 80,
        },
    },
    {
        "name": "組合D：SaaS/軟體新創 CTO/VP",
        "code": "combo_D",
        "priority": "P1",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "CTO", "Chief Technology Officer", "VP Engineering",
                "VP of Engineering", "Head of Engineering",
                "VP Product", "Co-Founder", "技術長",
            ],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Engineering", "Information Technology"],
            "seniority_levels": ["CXO", "Vice President", "Owner/Partner"],
            "posted_on_linkedin": "true",
            "limit": 100,
        },
    },
    {
        "name": "組合E：電商/新零售 Operations",
        "code": "combo_E",
        "priority": "P4",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "Head of Operations", "Operations Director", "Head of Growth",
                "Growth Manager", "E-commerce Director", "Head of Technology",
            ],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Operations", "Business Development"],
            "seniority_levels": ["Director", "Experienced Manager", "CXO"],
            "posted_on_linkedin": "true",
            "limit": 70,
        },
    },
    {
        "name": "組合G：Product/Engineering Manager",
        "code": "combo_G",
        "priority": "P2",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "Head of Product", "Product Director", "Engineering Manager",
                "AI Lead", "Head of AI", "AI Manager", "Data Lead", "ML Lead",
            ],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Product Management", "Engineering", "Information Technology"],
            "seniority_levels": ["Director", "Experienced Manager", "Strategic"],
            "posted_on_linkedin": "true",
            "limit": 90,
        },
    },
    {
        "name": "組合H：創辦人/總經理（廣義決策層）",
        "code": "combo_H",
        "priority": "P1",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "Founder", "CEO", "Chief Executive Officer", "Managing Director",
                "General Manager", "President", "執行長", "總經理",
                "創辦人", "負責人",
            ],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Entrepreneurship"],
            "seniority_levels": ["CXO", "Owner/Partner"],
            "posted_on_linkedin": "true",
            "limit": 130,
        },
    },
]
# 總原始上限 = 100+80+80+100+70+90+130 = 650

# ── ICP 評分（與主腳本一致）──────────────────────────────────
TITLE_DECISION_KW = [
    "cto", "cio", "cdo", "cxo", "vp ", "svp", "evp", "chief",
    "director", "head of", "head,", "owner", "founder", "co-founder",
    "partner", "president",
]
TITLE_INFLUENCER_KW = [
    "manager", "lead", "senior", "principal", "specialist", "engineer",
]
AI_SIGNAL_KW = [
    "chatgpt", "openai", "claude", "gemini", "llm", "copilot",
    "gpt-4", "gpt4", "prompt", "generative ai", "rag", "langchain",
    "ai tool", "api key", "token budget", "ai platform", "llmops",
    "mlops", "bedrock", "vertex ai", "azure openai",
]
INDUSTRY_KW_SCORE = {
    "software": 20, "saas": 20, "tech": 20, "internet": 20,
    "information technology": 20, "startup": 20, "fintech": 18,
    "marketing": 18, "advertising": 18, "agency": 18, "media": 16,
    "consulting": 15, "digital transformation": 15, "professional services": 12,
    "e-commerce": 12, "ecommerce": 12, "retail": 10, "commerce": 10,
    "education": 10, "edtech": 10, "learning": 10, "training": 8,
}


def icp_score(title: str, about: str) -> int:
    t = title.lower()
    a = (about or "").lower()
    txt = t + " " + a

    if any(kw in t for kw in TITLE_DECISION_KW):
        title_pts = 30
    elif any(kw in t for kw in TITLE_INFLUENCER_KW):
        title_pts = 15
    else:
        title_pts = 5

    size_pts = 15
    industry_pts = 5
    for kw, pts in INDUSTRY_KW_SCORE.items():
        if kw in txt and pts > industry_pts:
            industry_pts = pts

    activity_pts = 15
    ai_hits = sum(1 for kw in AI_SIGNAL_KW if kw in txt)
    ai_pts = min(ai_hits * 5, 15)

    return min(title_pts + size_pts + industry_pts + activity_pts + ai_pts, 100)


def classify(score: int) -> str:
    if score >= 70:
        return "HOT"
    elif score >= 50:
        return "WARM"
    return "COLD"


# ── Apify 執行（2-step 分頁）─────────────────────────────────
def run_combo(combo: dict, client: ApifyClient) -> list:
    log.info(f"▶ 啟動 {combo['name']}（上限 {combo['input']['limit']} 筆）")
    try:
        run = client.actor(ACTOR_ID).call(run_input=combo["input"])
    except Exception as e:
        log.error(f"  ✗ 初始化失敗：{e}")
        return []

    dataset_id = run.default_dataset_id if hasattr(run, "default_dataset_id") else run["defaultDatasetId"]
    items = list(client.dataset(dataset_id).iterate_items())
    if not items:
        log.warning("  ⚠ 無回應")
        return []

    first = items[0]
    request_id = first.get("request_id")

    if not request_id:
        data = first.get("data", [])
        log.info(f"  ✓ 同步取回 {len(data)} 筆")
        return data

    log.info(f"  ✓ 初始化 request_id={request_id}，等待 7 分鐘...")
    time.sleep(420)

    all_data = []
    for page in range(1, 30):
        log.info(f"  第 {page} 頁...")
        try:
            pr = client.actor(ACTOR_ID).call(
                run_input={"request_id": request_id, "page": page}
            )
            pr_dataset_id = pr.default_dataset_id if hasattr(pr, "default_dataset_id") else pr["defaultDatasetId"]
            pi = list(client.dataset(pr_dataset_id).iterate_items())
        except Exception as e:
            log.error(f"  ✗ 第 {page} 頁失敗：{e}")
            break
        if not pi:
            break
        page_data = pi[0].get("data", [])
        if not page_data:
            break
        all_data.extend(page_data)
        log.info(f"  累計 {len(all_data)} 筆")
        if len(page_data) < 100 or len(all_data) >= combo["input"]["limit"]:
            break
        time.sleep(5)
    return all_data


def normalize(raw: dict, combo: dict, account: str) -> dict:
    title = raw.get("job_title") or raw.get("title") or ""
    about = raw.get("about") or ""
    name = raw.get("full_name") or raw.get("name") or ""
    company = raw.get("company") or ""
    score = icp_score(title, about)
    cls = classify(score)
    acc_info = ACCOUNTS.get(account, ACCOUNTS[DEFAULT_ACCOUNT])
    return {
        "lead_id":          raw.get("profile_id") or raw.get("id") or "",
        "name":             name,
        "title":            title,
        "company":          company,
        "location":         raw.get("location") or "",
        "linkedin_url":     raw.get("linkedin_url") or raw.get("profileUrl") or "",
        "lead_source":      "A-LI-Scout/Reserve-500",
        "source_account":   account,
        "sender_name":      acc_info["display_name"],
        "icp_score":        score,
        "classification":   cls,
        "search_combo":     combo["code"],
        "combo_name":       combo["name"],
        "priority":         combo["priority"],
        "touch_number":     "D1-待發",
        "connection_status": "儲備-待分配",
        "reply_status":     "未回覆",
        "purchase_intent":  1,
        "summary_snippet":  about[:200],
        "scrape_date":      datetime.now().strftime("%Y-%m-%d"),
        "reserve_status":   "RESERVE",
        "asana_task_name":  (
            f"[{cls}-{score}][{account}] {name} | {title[:30]} | {company} | {score}分"
        ),
    }


def deduplicate(leads: list) -> list:
    seen: dict = {}
    for lead in leads:
        key = lead["linkedin_url"] or lead["lead_id"]
        if not key:
            continue
        if key not in seen or lead["icp_score"] > seen[key]["icp_score"]:
            seen[key] = lead
    return list(seen.values())


def save_reserve(leads: list, output_dir: Path) -> tuple:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path  = output_dir / f"taiwan_reserve_500_{ts}.csv"
    json_path = output_dir / f"taiwan_reserve_500_{ts}.json"
    if leads:
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(leads[0].keys()))
            w.writeheader()
            w.writerows(leads)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    return csv_path, json_path


def print_reserve_summary(leads: list, target: int, account: str):
    hot   = [l for l in leads if l["classification"] == "HOT"]
    warm  = [l for l in leads if l["classification"] == "WARM"]
    cold  = [l for l in leads if l["classification"] == "COLD"]
    combo_counts: dict = {}
    for l in leads:
        combo_counts[l["combo_name"]] = combo_counts.get(l["combo_name"], 0) + 1
    acc_info = ACCOUNTS.get(account, ACCOUNTS[DEFAULT_ACCOUNT])
    achieved = "✅" if len(leads) >= target else "⚠"

    print("\n" + "=" * 68)
    print(f"  A-LI-Scout — 台灣儲備名單（Reserve 500）")
    print(f"  帳號：{account} / {acc_info['display_name']}")
    print("=" * 68)
    print(f"  {achieved} 儲備筆數：{len(leads)} / 目標 {target}")
    print(f"  HOT（≥70）：{len(hot)} 筆")
    print(f"  WARM（50-69）：{len(warm)} 筆")
    print(f"  COLD（<50）：{len(cold)} 筆（納入儲備池）")
    print()
    print("  各搜尋組合分佈：")
    for name, count in combo_counts.items():
        print(f"    {name}：{count} 筆")
    print()
    top = sorted(hot + warm, key=lambda x: -x["icp_score"])[:15]
    if top:
        print("  Top 15 HOT/WARM（儲備優先觸達候選）：")
        for l in top:
            print(
                f"    [{l['icp_score']}分 {l['classification']}] "
                f"{l['name']} | {l['title'][:28]} | {l['company'][:22]}"
            )
    print("=" * 68)
    print(f"  下一步：將 CSV 匯入 Asana 或交由 linkedin_processor.py 批次生成草稿")
    print("=" * 68)


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="台灣 LinkedIn Sales Navigator 儲備名單 500 筆抓取"
    )
    parser.add_argument(
        "--account",
        choices=list(ACCOUNTS.keys()),
        default=DEFAULT_ACCOUNT,
        help=f"來源帳號標記 (default: {DEFAULT_ACCOUNT})",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=500,
        help="目標儲備筆數（default: 500）",
    )
    parser.add_argument(
        "--skip-asana-dedup",
        action="store_true",
        help="跳過 Asana 去重（快速模式，適合純備份收集）",
    )
    parser.add_argument(
        "--combos",
        nargs="+",
        choices=[c["code"] for c in RESERVE_COMBOS],
        default=None,
        help="僅執行指定組合，例如：--combos combo_A combo_D combo_H",
    )
    args = parser.parse_args()
    account = args.account
    target  = args.target
    acc_info = ACCOUNTS[account]

    log.info(
        f"🗂 台灣儲備名單任務啟動 — 帳號：{account}（{acc_info['display_name']}），"
        f"目標：{target} 筆"
    )

    active_combos = RESERVE_COMBOS
    if args.combos:
        active_combos = [c for c in RESERVE_COMBOS if c["code"] in args.combos]
        log.info(f"  ⚙ 只執行指定組合：{args.combos}")

    output_dir = Path(__file__).parent / "output" / "reserve"
    output_dir.mkdir(parents=True, exist_ok=True)

    client = ApifyClient(APIFY_TOKEN)
    all_leads: list = []

    for i, combo in enumerate(active_combos):
        if i > 0:
            log.info("⏳ 間隔 10 秒...")
            time.sleep(10)
        raw_items = run_combo(combo, client)
        normalized = [normalize(r, combo, account) for r in raw_items if r]
        log.info(f"  → 標準化 {len(normalized)} 筆")
        all_leads.extend(normalized)

        current_unique = deduplicate(all_leads)
        log.info(f"  📊 目前累計（去重）：{len(current_unique)} / {target} 筆")
        if len(current_unique) >= target * 1.1:
            log.info(f"  ✅ 已超過目標 {target} 筆的 110%，提前停止抓取")
            all_leads = current_unique
            break

    log.info(f"📊 合併前 {len(all_leads)} 筆，全域去重中...")
    unique = deduplicate(all_leads)
    unique.sort(key=lambda x: -x["icp_score"])
    log.info(f"📊 去重後 {len(unique)} 筆")

    if not args.skip_asana_dedup:
        try:
            from asana_dedup import get_existing_urls, filter_new_leads
            log.info("🔍 查詢 Asana CRM 已存在的 LinkedIn URL（跨帳號去重）...")
            existing_urls = get_existing_urls()
            if existing_urls:
                unique, dupes = filter_new_leads(unique, existing_urls)
                log.info(f"  ✂ 已在 Asana 跳過 {len(dupes)} 筆，剩餘新 Lead {len(unique)} 筆")
            else:
                log.info("  ℹ Asana 無資料或未設定 ASANA_PROJECT_GID，跳過去重")
        except ImportError:
            log.warning("  ⚠ asana_dedup.py 未找到，跳過 Asana 去重")
        except Exception as e:
            log.warning(f"  ⚠ Asana 去重失敗（{e}），繼續執行")

    # 截取目標筆數（優先保留高分 Lead）
    final_leads = unique[:target]
    log.info(f"✂ 截取前 {len(final_leads)} 筆作為儲備名單（按 ICP 分數排序）")

    csv_path, json_path = save_reserve(final_leads, output_dir)
    log.info(f"💾 CSV：{csv_path}")
    log.info(f"💾 JSON：{json_path}")

    print_reserve_summary(final_leads, target, account)

    log.info(
        f"✅ 儲備名單完成。"
        f"下一步：python linkedin_processor.py draft {csv_path.name} --account {account}"
    )


if __name__ == "__main__":
    main()
