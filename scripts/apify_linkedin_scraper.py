#!/usr/bin/env python3
"""
AI Token King — A-LI-Scout v2
LinkedIn Sales Navigator Lead 抓取腳本

修正版（v2）：
  ✅ 公司規模篩選（11-50 / 51-200 only）
  ✅ 活躍度篩選（posted_on_linkedin 近 30 天）
  ✅ 5 維度 ICP 評分（對齊 SOP：職稱/規模/產業/活躍/AI訊號）
  ✅ 6 個搜尋組合（A/B/C/D/E/G）
  ✅ HOT≥70 / WARM 50-69 / COLD<50（對齊 linkedin_processor.py）
  ✅ 多帳號支援（--account frank/jet/kid/lauren/alice）
  ✅ source_account 欄位紀錄來源帳號，供 Asana CRM 跨帳號去重

Actor: bestscrapers/sales-navigator-scraper-by-filters（100% 成功率）
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

ACTOR_ID = "bestscrapers/sales-navigator-scraper-by-filters"
TAIWAN_GEO = 104187078

# ── 多帳號設定 ─────────────────────────────────────────────
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

# ── 6 個搜尋組合 ──────────────────────────────────────────
SEARCH_COMBOS = [
    {
        "name": "組合A：科技公司IT決策者",
        "code": "combo_A", "priority": "P1",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": ["IT Manager", "IT Director", "Head of IT", "CIO", "Chief Information Officer", "資訊主管", "IT長"],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Information Technology"],
            "seniority_levels": ["Director", "Experienced Manager", "CXO"],
            "posted_on_linkedin": "true",
            "limit": 80,
        },
    },
    {
        "name": "組合B：行銷代理商高層",
        "code": "combo_B", "priority": "P2",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": ["Marketing Director", "Head of Marketing", "Creative Director", "Head of Content", "Digital Marketing Manager", "Agency Owner", "行銷總監"],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Marketing"],
            "seniority_levels": ["Director", "Owner/Partner", "CXO"],
            "posted_on_linkedin": "true",
            "limit": 60,
        },
    },
    {
        "name": "組合C：數位轉型顧問/服務商",
        "code": "combo_C", "priority": "P3",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": ["Digital Transformation", "AI Consultant", "Innovation Manager", "CDO", "Head of Digital", "數位轉型"],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Consulting", "Information Technology"],
            "seniority_levels": ["Director", "CXO", "Experienced Manager"],
            "posted_on_linkedin": "true",
            "limit": 60,
        },
    },
    {
        "name": "組合D：SaaS/軟體新創 CTO/VP",
        "code": "combo_D", "priority": "P1",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": ["CTO", "Chief Technology Officer", "VP Engineering", "VP of Engineering", "Head of Engineering", "VP Product", "Co-Founder", "技術長"],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Engineering", "Information Technology"],
            "seniority_levels": ["CXO", "Vice President", "Owner/Partner"],
            "posted_on_linkedin": "true",
            "limit": 80,
        },
    },
    {
        "name": "組合E：電商/新零售 Operations",
        "code": "combo_E", "priority": "P4",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": ["Head of Operations", "Operations Director", "Head of Growth", "Growth Manager", "E-commerce Director", "Head of Technology"],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Operations", "Business Development"],
            "seniority_levels": ["Director", "Experienced Manager", "CXO"],
            "posted_on_linkedin": "true",
            "limit": 50,
        },
    },
    {
        "name": "組合G：Product/Engineering Manager",
        "code": "combo_G", "priority": "P2",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": ["Head of Product", "Product Director", "Engineering Manager", "AI Lead", "Head of AI", "AI Manager", "Data Lead", "ML Lead"],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Product Management", "Engineering", "Information Technology"],
            "seniority_levels": ["Director", "Experienced Manager", "Strategic"],
            "posted_on_linkedin": "true",
            "limit": 70,
        },
    },
]

# ── SOP 5 維度 ICP 評分 ───────────────────────────────────
#
# 因為搜尋時已強制 company_headcounts=["11-50","51-200"] 和
# posted_on_linkedin="true"，所有回傳 Lead 都符合規模和活躍度條件。
# → 規模固定給 15 分，活躍度固定給 15 分。
# 其餘 3 個維度根據 Profile 內容計算。

TITLE_DECISION_KW = ["cto","cio","cdo","cxo","vp ","svp","evp","chief","director",
                     "head of","head,","owner","founder","co-founder","partner","president"]
TITLE_INFLUENCER_KW = ["manager","lead","senior","principal","specialist","engineer"]

AI_SIGNAL_KW = ["chatgpt","openai","claude","gemini","llm","copilot","gpt-4","gpt4",
                "prompt","generative ai","rag","langchain","ai tool","api key","token budget",
                "ai platform","llmops","mlops","bedrock","vertex ai","azure openai"]

INDUSTRY_KW_SCORE = {
    # P1 — 20分
    "software": 20, "saas": 20, "tech": 20, "internet": 20,
    "information technology": 20, "startup": 20, "fintech": 18,
    # P2 — 18分
    "marketing": 18, "advertising": 18, "agency": 18, "media": 16,
    # P3 — 15分
    "consulting": 15, "digital transformation": 15, "professional services": 12,
    # P4 — 12分
    "e-commerce": 12, "ecommerce": 12, "retail": 10, "commerce": 10,
    # P5 — 10分
    "education": 10, "edtech": 10, "learning": 10, "training": 8,
}


def icp_score_v2(title: str, about: str) -> int:
    """
    5 維度評分（總分上限 100）：
      1. 職稱匹配度  0-30
      2. 公司規模    15（固定，篩選保證）
      3. 產業匹配度  0-20（從 about 推斷）
      4. 活躍度訊號  15（固定，posted_on_linkedin 保證）
      5. AI 痛點訊號  0-15
    """
    t = title.lower()
    a = (about or "").lower()
    txt = t + " " + a

    # 1. 職稱匹配度
    if any(kw in t for kw in TITLE_DECISION_KW):
        title_pts = 30
    elif any(kw in t for kw in TITLE_INFLUENCER_KW):
        title_pts = 15
    else:
        title_pts = 5

    # 2. 公司規模（固定 15，篩選時已保證 11-200 人）
    size_pts = 15

    # 3. 產業匹配度（從 about 推斷）
    industry_pts = 5
    for kw, pts in INDUSTRY_KW_SCORE.items():
        if kw in txt and pts > industry_pts:
            industry_pts = pts

    # 4. 活躍度訊號（固定 15，posted_on_linkedin 保證）
    activity_pts = 15

    # 5. AI 工具痛點訊號
    ai_hits = sum(1 for kw in AI_SIGNAL_KW if kw in txt)
    ai_pts = min(ai_hits * 5, 15)

    return min(title_pts + size_pts + industry_pts + activity_pts + ai_pts, 100)


def classify(score: int) -> str:
    if score >= 70:
        return "HOT"
    elif score >= 50:
        return "WARM"
    return "COLD"


# ── Apify 執行流程（2-step）────────────────────────────────
def run_combo(combo: dict, client: ApifyClient) -> list:
    log.info(f"▶ 啟動 {combo['name']}")
    try:
        run = client.actor(ACTOR_ID).call(run_input=combo["input"])
    except Exception as e:
        log.error(f"  ✗ 初始化失敗：{e}")
        return []

    items = list(client.dataset(run["defaultDatasetId"]).iterate_items())
    if not items:
        log.warning("  ⚠ 無回應")
        return []

    first = items[0]
    request_id = first.get("request_id")

    # 同步返回（無 request_id）
    if not request_id:
        data = first.get("data", [])
        log.info(f"  ✓ 同步取回 {len(data)} 筆")
        return data

    log.info(f"  ✓ 初始化 request_id={request_id}，等待 7 分鐘...")
    time.sleep(420)

    all_data = []
    for page in range(1, 26):
        log.info(f"  第 {page} 頁...")
        try:
            pr = client.actor(ACTOR_ID).call(run_input={"request_id": request_id, "page": page})
            pi = list(client.dataset(pr["defaultDatasetId"]).iterate_items())
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


def normalize(raw: dict, combo: dict, account: str = DEFAULT_ACCOUNT) -> dict:
    title = raw.get("job_title") or raw.get("title") or ""
    about = raw.get("about") or ""
    name = raw.get("full_name") or raw.get("name") or ""
    company = raw.get("company") or ""
    score = icp_score_v2(title, about)
    cls = classify(score)
    acc_info = ACCOUNTS.get(account, ACCOUNTS[DEFAULT_ACCOUNT])
    return {
        "lead_id":          raw.get("profile_id") or raw.get("id") or "",
        "name":             name,
        "title":            title,
        "company":          company,
        "location":         raw.get("location") or "",
        "linkedin_url":     raw.get("linkedin_url") or raw.get("profileUrl") or "",
        "lead_source":      "A-LI-Scout/Apify-v2",
        "source_account":   account,
        "sender_name":      acc_info["display_name"],
        "icp_score":        score,
        "classification":   cls,
        "search_combo":     combo["code"],
        "combo_name":       combo["name"],
        "priority":         combo["priority"],
        "touch_number":     "D1-待發",
        "connection_status":"待發送",
        "reply_status":     "未回覆",
        "purchase_intent":  1,
        "summary_snippet":  about[:200],
        "scrape_date":      datetime.now().strftime("%Y-%m-%d"),
        "asana_task_name":  f"[{cls}-{score}][{account}] {name} | {title[:30]} | {company} | {score}分",
    }


def deduplicate(leads: list) -> list:
    seen = {}
    for lead in leads:
        key = lead["linkedin_url"] or lead["lead_id"]
        if not key:
            continue
        if key not in seen or lead["icp_score"] > seen[key]["icp_score"]:
            seen[key] = lead
    return list(seen.values())


def save(leads: list, output_dir: Path):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path  = output_dir / f"leads_v2_{ts}.csv"
    json_path = output_dir / f"leads_v2_{ts}.json"
    if leads:
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(leads[0].keys()))
            w.writeheader(); w.writerows(leads)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    return csv_path, json_path


def print_summary(leads: list, account: str = DEFAULT_ACCOUNT):
    hot  = [l for l in leads if l["classification"] == "HOT"]
    warm = [l for l in leads if l["classification"] == "WARM"]
    cold = [l for l in leads if l["classification"] == "COLD"]
    combo_counts = {}
    for l in leads:
        combo_counts[l["combo_name"]] = combo_counts.get(l["combo_name"], 0) + 1
    acc_info = ACCOUNTS.get(account, ACCOUNTS[DEFAULT_ACCOUNT])
    print("\n" + "=" * 65)
    print(f"  A-LI-Scout v2 — Lead 抓取結果摘要（帳號：{account} / {acc_info['display_name']}）")
    print("=" * 65)
    print(f"  總 Lead（去重）：{len(leads)} 筆")
    print(f"  HOT（≥70）：{len(hot)} 筆  ← 同日優先觸達，Make.com 自動排程")
    print(f"  WARM（50-69）：{len(warm)} 筆  ← 次日批次，審核後自動發送")
    print(f"  COLD（<50）：{len(cold)} 筆  ← 培育池")
    print(f"  日限額：{acc_info['daily_limit']} conn  發送時間窗：{acc_info['send_window']}")
    print()
    for name, count in combo_counts.items():
        print(f"  {name}：{count} 筆")
    print()
    top = sorted(hot + warm, key=lambda x: -x["icp_score"])[:10]
    if top:
        print("  Top 10 HOT/WARM：")
        for l in top:
            print(f"    [{l['icp_score']}分 {l['classification']}] "
                  f"{l['name']} | {l['title'][:28]} | {l['company'][:22]}")
    print("=" * 65)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="A-LI-Scout v2 — LinkedIn Lead 抓取")
    parser.add_argument(
        "--account",
        choices=list(ACCOUNTS.keys()),
        default=DEFAULT_ACCOUNT,
        help=f"發送帳號 (default: {DEFAULT_ACCOUNT})。各帳號有獨立配額與風格。",
    )
    parser.add_argument(
        "--skip-asana-dedup",
        action="store_true",
        help="跳過 Asana 去重檢查（快速模式，不建議用於正式執行）",
    )
    args = parser.parse_args()
    account = args.account
    acc_info = ACCOUNTS[account]

    log.info(f"📌 帳號：{account}（{acc_info['display_name']}），日限 {acc_info['daily_limit']}，時間窗 {acc_info['send_window']}")

    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    client = ApifyClient(APIFY_TOKEN)
    all_leads = []

    for i, combo in enumerate(SEARCH_COMBOS):
        if i > 0:
            log.info("⏳ 間隔 10 秒...")
            time.sleep(10)
        raw_items = run_combo(combo, client)
        normalized = [normalize(r, combo, account) for r in raw_items if r]
        log.info(f"  → 標準化 {len(normalized)} 筆")
        all_leads.extend(normalized)

    log.info(f"📊 合併前 {len(all_leads)} 筆，本地去重中...")
    unique = deduplicate(all_leads)
    unique.sort(key=lambda x: -x["icp_score"])
    log.info(f"📊 本地去重後 {len(unique)} 筆")

    # ── Asana CRM 去重（跨帳號，避免重複聯繫）──────────────
    if not args.skip_asana_dedup:
        try:
            from asana_dedup import get_existing_urls, filter_new_leads, normalize_url
            log.info("🔍 查詢 Asana CRM 已存在的 LinkedIn URL...")
            existing_urls = get_existing_urls()
            if existing_urls:
                unique, dupes = filter_new_leads(unique, existing_urls)
                if dupes:
                    log.info(f"  ✂ 已在 Asana 跳過 {len(dupes)} 筆，剩餘新 Lead {len(unique)} 筆")
            else:
                log.info("  ℹ Asana 無資料或未設定 ASANA_PROJECT_GID，跳過去重")
        except ImportError:
            log.warning("  ⚠ asana_dedup.py 未找到，跳過 Asana 去重")
        except Exception as e:
            log.warning(f"  ⚠ Asana 去重失敗（{e}），繼續執行")

    csv_path, json_path = save(unique, output_dir)
    log.info(f"💾 CSV：{csv_path}")
    print_summary(unique, account)
    log.info(f"✅ 完成。下一步：python linkedin_processor.py draft {csv_path.name} --account {account}")


if __name__ == "__main__":
    main()
