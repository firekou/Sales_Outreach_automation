#!/usr/bin/env python3
"""
AI Token King — Taiwan AI BizDev Search
台灣「已在用 AI 賺錢」公司決策者搜尋器

TA 定義（Frank, 2026-06-15）：
  - 已在用 AI 且能變現的公司（AI-native / AI-enabled）
  - 正在成長、優秀、聰明的公司
  - 這些公司不需要被教，他們有需求、有能力付費

搜尋邏輯：不找「想導入 AI 的人」，找「已在用 AI 跑業務的人」。
  → AI 職稱即公司 AI 成熟度的最強信號
  → AIGC / 創意科技代理商 → 拿 AI 賺客戶的錢
  → AI SaaS / 工具公司創辦人 → AI 是核心商業模式
  → 高速成長 SaaS 技術決策者 → AI 是競爭優勢的底層

四個搜尋組合（I / J / K / L）：
  I  AI 職能決策者     — 有 AI 職稱的高層，公司 AI 成熟度最高
  J  AIGC 創意代理商   — 拿 AI 幫客戶做創意/行銷內容，AI 是收入來源
  K  AI SaaS 創辦人    — AI 是核心產品，最懂也最有需求
  L  成長型 SaaS CTO   — 技術決策者，AI Token 最大消費方

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
        "style_hint": "高層對高層，重願景與 AI ROI，語氣從容自信",
        "daily_limit": 25,
        "send_window": "08:00–09:00",
    },
    "kid": {
        "display_name": "Kid",
        "title": "業務銷售, AI Token King",
        "style_hint": "親切 ENFJ 風格，直接切 AI Token 成本痛點",
        "daily_limit": 30,
        "send_window": "14:00–15:00",
    },
    "alice": {
        "display_name": "Alice Wu",
        "title": "Product Manager, AI Token King",
        "style_hint": "產品對產品，技術同理心，聚焦多模型管理痛點",
        "daily_limit": 20,
        "send_window": "11:00–12:00",
    },
}
DEFAULT_ACCOUNT = "kid"

# ── 四個新搜尋組合（AI BizDev 版）─────────────────────────────
BIZDEV_COMBOS = [
    {
        "name": "組合I：AI職能決策者（AI-Native公司高層）",
        "code": "combo_I",
        "priority": "P1",
        "ta": "TA-2/TA-6",
        "logic": "有 AI 職稱 = 公司已承諾投資 AI，是最強的 AI 成熟度信號",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "Head of AI", "Chief AI Officer", "VP of AI", "AI Director",
                "AI Lead", "Head of Machine Learning", "ML Lead",
                "Head of Data Science", "Chief Data Officer",
                "AI Product Manager", "Head of GenAI", "GenAI Lead",
                "AI Strategy", "AI負責人", "AI主管", "人工智慧主管",
            ],
            "company_headcounts": ["11-50", "51-200", "201-500"],
            "seniority_levels": ["Director", "CXO", "Vice President", "Experienced Manager"],
            "limit": 300,
        },
    },
    {
        "name": "組合J：AIGC創意代理商（拿AI賺客戶錢的公司）",
        "code": "combo_J",
        "priority": "P1",
        "ta": "TA-4",
        "logic": "AIGC / 創意科技代理商把 AI 直接轉化為收入，需要穩定的 Token 成本管控",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "Creative Director", "Head of Creative", "Creative Technologist",
                "Head of Innovation", "Innovation Director",
                "Head of Content", "Content Director", "Content Strategy",
                "Digital Creative Director", "Brand Director",
                "Agency Owner", "Agency Founder", "Agency CEO",
                "Head of Production", "Executive Creative Director",
            ],
            "company_headcounts": ["11-50", "51-200"],
            "functions": ["Marketing", "Media and Communication", "Design"],
            "seniority_levels": ["Director", "Owner/Partner", "CXO"],
            "limit": 250,
        },
    },
    {
        "name": "組合K：AI SaaS / 工具公司創辦人（AI是核心商業模式）",
        "code": "combo_K",
        "priority": "P1",
        "ta": "TA-1/TA-2",
        "logic": "AI 工具公司創辦人本身就在賣 AI，Token 成本直接影響毛利，是最強需求方",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "Founder", "Co-Founder", "CEO", "CTO", "CPO",
                "Managing Director", "General Manager",
                "創辦人", "執行長", "技術長", "負責人",
            ],
            "company_headcounts": ["1-10", "11-50"],
            "functions": ["Entrepreneurship", "Engineering", "Information Technology"],
            "seniority_levels": ["CXO", "Owner/Partner"],
            "limit": 350,
        },
    },
    {
        "name": "組合L：成長型SaaS技術決策者（AI Token最大消費方）",
        "code": "combo_L",
        "priority": "P2",
        "ta": "TA-2",
        "logic": "50-500人 SaaS 公司的 CTO/VP Eng 是 AI Token 消費主力，且有明確技術預算",
        "input": {
            "geo_codes": [TAIWAN_GEO],
            "title_keywords": [
                "CTO", "Chief Technology Officer", "VP Engineering",
                "VP of Engineering", "Head of Engineering",
                "VP Product", "Head of Product", "CPO",
                "Chief Product Officer", "技術長", "產品長",
            ],
            "company_headcounts": ["51-200", "201-500"],
            "functions": ["Engineering", "Product Management", "Information Technology"],
            "seniority_levels": ["CXO", "Vice President", "Director"],
            "limit": 250,
        },
    },
]

# ── ICP 評分（AI BizDev 版）— AI 信號權重大幅提升 ──────────────
TITLE_DECISION_KW = [
    "cto", "cio", "cdo", "cxo", "vp ", "svp", "evp", "chief",
    "director", "head of", "head,", "owner", "founder", "co-founder",
    "partner", "president", "cpo",
]
TITLE_INFLUENCER_KW = [
    "manager", "lead", "senior", "principal", "specialist",
]

# AI 職稱關鍵字（職稱本身帶 AI = 最強信號）
TITLE_AI_KW = [
    "ai ", "a.i.", "machine learning", "ml ", "llm", "genai",
    "generative", "head of data", "chief data", "data science",
    "chief ai", "head of ai", "ai director", "ai lead", "ai product",
    "ai strategy", "人工智慧", "ai主管", "ai負責人",
]

# AI 工具/技術信號（About 欄位）
AI_SIGNAL_KW = [
    "chatgpt", "openai", "claude", "anthropic", "gemini", "llm",
    "copilot", "gpt-4", "gpt4", "prompt", "generative ai",
    "rag", "langchain", "ai tool", "api key", "token budget",
    "ai platform", "llmops", "mlops", "bedrock", "vertex ai",
    "azure openai", "midjourney", "stable diffusion", "aigc",
    "large language model", "foundation model", "fine-tun",
    "vector db", "embedding", "ai agent", "agentic",
]

# 已在變現/成長的信號（About 欄位）
MONETIZE_KW = [
    "revenue", "growth", "scale", "monetize", "profitable", "roi",
    "product-led", "saas", "arr", "mrr", "b2b", "enterprise",
    "客戶", "營收", "成長", "獲利", "變現", "ai產品", "ai工具",
    "幫客戶", "為客戶", "提供ai",
]

INDUSTRY_KW_SCORE = {
    "artificial intelligence": 20, "machine learning": 20,
    "software": 18, "saas": 20, "tech": 18, "internet": 16,
    "information technology": 16, "startup": 16, "fintech": 16,
    "marketing": 15, "advertising": 15, "agency": 15, "media": 14,
    "consulting": 12, "digital": 12, "creative": 14,
    "e-commerce": 12, "ecommerce": 12, "data": 16,
}


def icp_score(title: str, about: str) -> tuple[int, list]:
    """
    AI BizDev 版 ICP 評分（總分上限 100）

    配分：
      職稱決策力   0-30  （高層 30 / 影響者 15 / 其他 5）
      AI 職稱信號  0-20  （職稱本身帶 AI 字樣 +20，最強信號）
      公司規模     0-10  （固定，Sales Nav 已做初篩）
      產業匹配     0-15
      AI 工具信號  0-15  （About 提及 AI 工具次數）
      變現信號     0-10  （About 提及成長/營收/客戶等）

    新增「AI 職稱信號」維度：職稱裡有 AI = 公司已承諾投入 AI 資源。
    """
    t = title.lower()
    a = (about or "").lower()
    signals = []

    # 1. 職稱決策力（0-30）
    if any(kw in t for kw in TITLE_DECISION_KW):
        title_pts = 30
        signals.append("決策者職稱")
    elif any(kw in t for kw in TITLE_INFLUENCER_KW):
        title_pts = 15
        signals.append("影響者職稱")
    else:
        title_pts = 5

    # 2. AI 職稱信號（0-20）：職稱本身帶 AI 字樣
    ai_title_pts = 20 if any(kw in t for kw in TITLE_AI_KW) else 0
    if ai_title_pts:
        signals.append("AI職稱")

    # 3. 公司規模（固定 10，Sales Nav 已做初篩）
    size_pts = 10

    # 4. 產業匹配（0-15）
    txt = t + " " + a
    industry_pts = 5
    for kw, pts in INDUSTRY_KW_SCORE.items():
        if kw in txt and pts > industry_pts:
            industry_pts = min(pts, 15)
    if industry_pts > 10:
        signals.append(f"產業({industry_pts})")

    # 5. AI 工具信號 About（0-15）
    ai_hits = sum(1 for kw in AI_SIGNAL_KW if kw in a)
    ai_pts = min(ai_hits * 5, 15)
    if ai_pts >= 5:
        signals.append(f"AI工具信號x{ai_hits}")

    # 6. 變現/成長信號（0-10）
    mon_hits = sum(1 for kw in MONETIZE_KW if kw in a)
    mon_pts = min(mon_hits * 3, 10)
    if mon_pts >= 3:
        signals.append("變現信號")

    total = min(title_pts + ai_title_pts + size_pts + industry_pts + ai_pts + mon_pts, 100)
    return total, signals


def classify(score: int) -> str:
    if score >= 70:
        return "HOT"
    elif score >= 50:
        return "WARM"
    return "COLD"


# ── Apify 執行（2-step 分頁，同主腳本）───────────────────────
def run_combo(combo: dict, client: ApifyClient) -> list:
    log.info(f"▶ 啟動 {combo['name']}（上限 {combo['input']['limit']} 筆）")
    log.info(f"   邏輯：{combo['logic']}")
    try:
        run = client.actor(ACTOR_ID).call(run_input=combo["input"])
    except Exception as e:
        log.error(f"  ✗ 初始化失敗：{e}")
        return []

    dataset_id = (
        run.default_dataset_id
        if hasattr(run, "default_dataset_id")
        else run["defaultDatasetId"]
    )
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
            pr_dataset_id = (
                pr.default_dataset_id
                if hasattr(pr, "default_dataset_id")
                else pr["defaultDatasetId"]
            )
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
    score, signals = icp_score(title, about)
    cls = classify(score)
    acc_info = ACCOUNTS.get(account, ACCOUNTS[DEFAULT_ACCOUNT])

    return {
        "lead_id":           raw.get("profile_id") or raw.get("id") or "",
        "name":              name,
        "title":             title,
        "company":           company,
        "location":          raw.get("location") or "",
        "linkedin_url":      raw.get("linkedin_url") or raw.get("profileUrl") or "",
        "lead_source":       "A-LI-Scout/AI-BizDev",
        "source_account":    account,
        "sender_name":       acc_info["display_name"],
        "icp_score":         score,
        "icp_signals":       ", ".join(signals),
        "classification":    cls,
        "search_combo":      combo["code"],
        "combo_name":        combo["name"],
        "combo_ta":          combo["ta"],
        "priority":          combo["priority"],
        "touch_number":      "D1-待發",
        "connection_status": "儲備-待分配",
        "reply_status":      "未回覆",
        "purchase_intent":   1,
        "summary_snippet":   about[:250],
        "scrape_date":       datetime.now().strftime("%Y-%m-%d"),
        "reserve_status":    "AI-BIZDEV",
        "asana_task_name": (
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


def save_results(leads: list, output_dir: Path) -> tuple:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_path  = output_dir / f"taiwan_ai_bizdev_{ts}.csv"
    json_path = output_dir / f"taiwan_ai_bizdev_{ts}.json"
    if leads:
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(leads[0].keys()))
            w.writeheader()
            w.writerows(leads)
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)
    return csv_path, json_path


def print_summary(leads: list, target: int, account: str):
    hot  = [l for l in leads if l["classification"] == "HOT"]
    warm = [l for l in leads if l["classification"] == "WARM"]
    cold = [l for l in leads if l["classification"] == "COLD"]

    from collections import Counter
    combo_counts = Counter(l["combo_name"] for l in leads)
    signal_counts = Counter()
    for l in leads:
        for sig in l.get("icp_signals", "").split(", "):
            if sig:
                signal_counts[sig] += 1

    achieved = "✅" if len(leads) >= target else "⚠"

    print("\n" + "=" * 70)
    print("  A-LI-Scout — 台灣 AI BizDev 名單（已在用 AI 賺錢的公司）")
    print(f"  帳號：{account} / {ACCOUNTS.get(account, ACCOUNTS[DEFAULT_ACCOUNT])['display_name']}")
    print("=" * 70)
    print(f"  {achieved} 抓取筆數：{len(leads)} / 目標 {target}")
    print(f"  HOT（≥70）：{len(hot)} 筆")
    print(f"  WARM（50-69）：{len(warm)} 筆")
    print(f"  COLD（<50）：{len(cold)} 筆")
    print()
    print("  各搜尋組合分佈：")
    for name, count in combo_counts.most_common():
        print(f"    {name[:50]}：{count} 筆")
    print()
    print("  ICP 信號分佈（Top 命中）：")
    for sig, count in signal_counts.most_common(8):
        print(f"    {sig}：{count} 筆")
    print()
    top = sorted(hot + warm, key=lambda x: -x["icp_score"])[:20]
    if top:
        print("  Top 20 HOT/WARM（優先觸達候選）：")
        for l in top:
            sigs = l.get("icp_signals", "")
            print(
                f"    [{l['icp_score']}分 {l['classification']}] "
                f"{l['name']} | {l['title'][:28]} | {l['company'][:22]}"
            )
            if sigs:
                print(f"         信號：{sigs}")
    print("=" * 70)
    print("  下一步：python apify_taiwan_ai_bizdev.py --import-asana")
    print("=" * 70)


def main():
    import argparse
    import copy

    parser = argparse.ArgumentParser(
        description="台灣『已在用 AI 賺錢的公司』決策者搜尋"
    )
    parser.add_argument(
        "--account",
        choices=list(ACCOUNTS.keys()),
        default=DEFAULT_ACCOUNT,
    )
    parser.add_argument(
        "--target",
        type=int,
        default=500,
        help="目標筆數（default: 500）",
    )
    parser.add_argument(
        "--combos",
        nargs="+",
        choices=[c["code"] for c in BIZDEV_COMBOS],
        default=None,
        help="僅執行指定組合，例如：--combos combo_I combo_K",
    )
    args = parser.parse_args()
    account  = args.account
    target   = args.target
    acc_info = ACCOUNTS[account]

    log.info(
        f"🤖 AI BizDev 搜尋啟動 — 帳號：{account}（{acc_info['display_name']}），"
        f"目標：{target} 筆"
    )
    log.info("  TA：已在用 AI 賺錢的公司 → AI職能高層 / AIGC代理商 / AI SaaS創辦人 / SaaS技術決策者")

    active_combos = copy.deepcopy(BIZDEV_COMBOS)
    if args.combos:
        active_combos = [c for c in active_combos if c["code"] in args.combos]

    output_dir = Path(__file__).parent / "output" / "ai_bizdev"
    output_dir.mkdir(parents=True, exist_ok=True)

    client   = ApifyClient(APIFY_TOKEN)
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
            log.info(f"  ✅ 已超過目標 {target} 筆的 110%，提前停止")
            all_leads = current_unique
            break

    log.info(f"📊 全域去重中（合併前 {len(all_leads)} 筆）...")
    unique = deduplicate(all_leads)
    unique.sort(key=lambda x: -x["icp_score"])
    log.info(f"📊 去重後 {len(unique)} 筆")

    try:
        from asana_dedup import get_existing_urls, filter_new_leads
        log.info("🔍 查詢 Asana CRM 已存在的 LinkedIn URL...")
        existing_urls = get_existing_urls()
        if existing_urls:
            unique, dupes = filter_new_leads(unique, existing_urls)
            log.info(f"  ✂ 跳過已在 Asana 的 {len(dupes)} 筆，剩 {len(unique)} 筆新 Lead")
    except Exception as e:
        log.warning(f"  ⚠ Asana 去重略過：{e}")

    final_leads = unique[:target]
    csv_path, json_path = save_results(final_leads, output_dir)
    log.info(f"💾 CSV：{csv_path}")
    log.info(f"💾 JSON：{json_path}")

    print_summary(final_leads, target, account)


if __name__ == "__main__":
    main()
