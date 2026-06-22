#!/usr/bin/env python3
"""
AI Token King — S1 Agent（LinkedIn 直攻法）

承接 apify_linkedin_scraper.py 的輸出，補充 S1 策略所需的深度分析：
  1. AI 使用者類型分類（A/B/C/D）
  2. 發展邏輯三步驟分析
  3. S1 三封信序列生成（依話術 SOP 05-talk-scripts.md）
  4. Heat Score 計算（對齊 07-orchestrator-spec.md §七）
  5. 輸出 Dripify CSV + Asana JSON

用法：
  python s1_agent.py output/leads_v2_*.csv [--account kid] [--top 20]

流程：
  apify_linkedin_scraper.py → leads_v2_*.csv
                ↓
          s1_agent.py（本腳本）
                ↓
     s1_drafts_*.json      ← 三封信草稿 + 分析結果
     s1_dripify_*.csv      ← 匯入 Dripify（連線邀請 + 第一封）
     s1_asana_*.json       ← 寫入 Asana Task
"""

import os
import csv
import json
import argparse
from datetime import datetime
from pathlib import Path

try:
    import anthropic
    from dotenv import load_dotenv
except ImportError:
    print("請先安裝：pip install anthropic python-dotenv")
    raise

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
client_ai = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 帳號人設 ──────────────────────────────────────────────
ACCOUNTS = {
    "frank": {"display_name": "Frank Kao", "title": "CEO, AI Token King",
              "style": "高層對高層，從容自信，重願景與風險管控，不用銷售話術"},
    "kid":   {"display_name": "Kid", "title": "業務銷售, AI Token King",
              "style": "親切 ENFJ 風格，直接切痛點，主動但不卑微"},
    "lauren":{"display_name": "Lauren", "title": "商務暨人資主管, AI Token King",
              "style": "BD 合作視角，著重效率痛點與 AI 工具帶來的利潤提升"},
}
DEFAULT_ACCOUNT = "kid"

# ── AI 使用者類型定義 ─────────────────────────────────────
AI_USER_TYPES = {
    "A": {
        "name": "身份建構者 Identity Builder",
        "signals": ["轉型", "轉職", "跨域", "MBA", "非技術背景分享AI文章", "重新定義"],
        "position_desire": "在舊行業裡最懂新科技的人，或完成數位轉型的標竿人物",
        "core_fear": "被時代淘汰，或轉型失敗後兩頭空",
        "atk_value": "讓他有具體的「轉型裝備」，能對外展示的那種",
        "angle": "讓你在你所在行業裡成為那個最早真正用好 AI 的人",
    },
    "B": {
        "name": "效率優化者 Efficiency Maximizer",
        "signals": ["Operations", "PM", "業務主管", "流程優化", "長期在同公司", "穩定晉升"],
        "position_desire": "讓公司運作最順的關鍵人，缺了他什麼都動不了",
        "core_fear": "引進工具後出了問題，在老闆面前失分",
        "atk_value": "可靠的、有人顧的、出了事有窗口的服務",
        "angle": "讓你的工作成果更可預測、更可追蹤、更能向上交代",
    },
    "C": {
        "name": "影響力建構者 Influence Builder",
        "signals": ["Founder", "顧問", "講師", "個人品牌", "持續寫文章", "高追蹤數", "KOL"],
        "position_desire": "某領域的公認意見領袖，讓自己的品牌比公司品牌更有價值",
        "core_fear": "掉隊——別人用 AI 每天產出大量內容，他還在手寫",
        "atk_value": "讓觀點生產速度和品質都超越同類競爭者",
        "angle": "讓你的觀點生產速度和傳播深度同時提升",
    },
    "D": {
        "name": "組織決策者 Organizational Decision Maker",
        "signals": ["CEO", "總監", "VP", "事業部負責人", "管理層超過三年", "談市場趨勢"],
        "position_desire": "讓公司在 AI 轉型中不掉隊的決策者，或讓公司超越競爭對手的人",
        "core_fear": "做了錯誤的工具選擇，導致資源浪費，或公司在轉型上落後對手",
        "atk_value": "降低組織導入 AI 的決策風險，清楚 ROI 對上對下都能交代",
        "angle": "讓你的組織 AI 導入決策有依據、有框架、有成果可以展示",
    },
}

# ── Heat Score 計分規則（對齊 orchestrator-spec §七）────────
def calc_heat_score(lead: dict, ai_type: str) -> int:
    score = 0
    icp = int(lead.get("icp_score", 0) or 0)

    # 基礎 ICP 分數折算（原始最高 100 → 熱度最高 40）
    score += int(icp * 0.4)

    # AI 使用者類型加權
    type_bonus = {"D": 15, "B": 10, "A": 8, "C": 5}
    score += type_bonus.get(ai_type, 0)

    # 活躍度：近 30 天有發文（Apify 已篩選，固定加分）
    score += 10

    # 決策層職稱
    title = (lead.get("title") or "").lower()
    if any(kw in title for kw in ["ceo", "cto", "cdo", "cio", "founder", "總經理", "執行長", "創辦人"]):
        score += 10

    # 公司規模甜蜜區間
    combo = lead.get("combo_name", "")
    if "50" in combo or "200" in combo:
        score += 10

    return min(score, 100)


def heat_to_priority(score: int) -> str:
    if score >= 70:
        return "A"
    elif score >= 40:
        return "B"
    return "C"


# ── Claude 分析引擎 ───────────────────────────────────────
def analyze_lead(lead: dict) -> dict:
    """Step 1：AI 使用者類型分類 + 發展邏輯分析"""
    if not client_ai:
        return {"ai_type": "B", "development_logic": "（需 API Key 才能分析）",
                "career_turning_point": "", "next_goal": "", "recommended_angle": ""}

    prompt = f"""你是頂級業務分析師，專精 LinkedIn 個人檔案解讀。

請分析以下 Lead 的背景資料，輸出 JSON（只輸出 JSON，不加任何說明）：

Lead 資料：
姓名：{lead.get('name', '')}
職稱：{lead.get('title', '')}
公司：{lead.get('company', '')}
個人摘要：{lead.get('summary_snippet', '')}
搜尋組合：{lead.get('combo_name', '')}

AI 使用者類型定義：
A = 身份建構者：正在重新定義自己，AI 是升級標籤的工具
B = 效率優化者：靠把事情做好建立價值，AI 是省時省力的工具
C = 影響力建構者：建立個人品牌，AI 是加速觀點傳播的工具
D = 組織決策者：KPI 是整個組織成果，AI 是降低轉型風險的工具

請判斷並輸出：
{{
  "ai_type": "A|B|C|D",
  "ai_type_confidence": "high|medium|low",
  "development_logic": "50字以內：他從哪裡來、怎麼走到現在、職涯方向是什麼",
  "career_turning_point": "20字以內：他履歷中最關鍵的一個轉折點（沒有就留空）",
  "next_goal": "20字以內：他現在的狀態在為什麼目標鋪路",
  "recommended_angle": "30字以內：我們應該以什麼身份出現在他的發展路徑上",
  "personalization_hook": "30字以內：連線邀請中最能讓他有感的切入點（要具體，不能是通用句子）"
}}"""

    msg = client_ai.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return json.loads(msg.content[0].text.strip())
    except Exception:
        return {"ai_type": "B", "development_logic": msg.content[0].text[:100],
                "career_turning_point": "", "next_goal": "", "recommended_angle": "",
                "personalization_hook": ""}


def generate_s1_scripts(lead: dict, analysis: dict, account: str) -> dict:
    """Step 2：生成 S1 三封信序列"""
    if not client_ai:
        return {"connection_request": "[需 API Key]", "msg1": "[需 API Key]",
                "msg2_with_reply": "[需 API Key]", "msg2_no_reply": "[需 API Key]",
                "msg3": "[需 API Key]"}

    persona = ACCOUNTS.get(account, ACCOUNTS[DEFAULT_ACCOUNT])
    ai_type = analysis.get("ai_type", "B")
    type_info = AI_USER_TYPES.get(ai_type, AI_USER_TYPES["B"])

    system = f"""你是 {persona['display_name']}，{persona['title']}。
風格：{persona['style']}

你正在執行 S1 LinkedIn 直攻法。
核心哲學：你不是在賣軟體，你是在成為對方發展路徑上的必要夥伴。
絕對不推銷、不用「介紹產品」這類措辭。
所有訊息都要讓對方感覺「這個人真的研究過我」。"""

    prompt = f"""請為以下 Lead 生成 S1 策略三封信序列。

Lead 分析結果：
- 姓名：{lead.get('name', '對方')}
- 職稱：{lead.get('title', '')}
- 公司：{lead.get('company', '')}
- 個人摘要：{lead.get('summary_snippet', '')[:300]}
- AI 使用者類型：{ai_type}（{type_info['name']}）
- 發展邏輯：{analysis.get('development_logic', '')}
- 職涯轉折點：{analysis.get('career_turning_point', '')}
- 他的下一個目標：{analysis.get('next_goal', '')}
- 建議切入角色：{analysis.get('recommended_angle', '')}
- 個人化鉤子：{analysis.get('personalization_hook', '')}
- 他的核心恐懼：{type_info['core_fear']}
- AI Token King 對他的意義：{type_info['atk_value']}
- 第三封的框架：{type_info['angle']}

請輸出 JSON（只輸出 JSON）：
{{
  "connection_request": "連線邀請附言，≤200字，不推銷，讓他感覺你研究過他。結尾不要說「請多指教」",
  "msg1": "第一封私訊，連線接受後 Day 1，≤300字，問一個讓他想回答的問題，結尾說「純粹好奇，沒有要推銷任何東西」",
  "msg2_with_reply": "第二封（對方有回覆版），≤300字，複述他說的觀點 → 提供低門檻資訊 → 讓他說好",
  "msg2_no_reply": "第二封（對方無回覆追蹤版），≤250字，換個角度再試一次，給他一個優雅的出口",
  "msg3": "第三封引入方案，≤350字，以「成為他所需角色」為框架，切入點是他的發展邏輯，而不是產品功能，結尾邀請 20 分鐘"
}}"""

    msg = client_ai.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    try:
        return json.loads(msg.content[0].text.strip())
    except Exception:
        raw = msg.content[0].text.strip()
        return {"connection_request": raw[:200], "msg1": "", "msg2_with_reply": "",
                "msg2_no_reply": "", "msg3": ""}


# ── 主流程 ────────────────────────────────────────────────
def process_leads(csv_path: str, account: str, top_n: int):
    leads = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))

    # 只處理 HOT / WARM
    candidates = [l for l in leads if l.get("classification") in ("HOT", "WARM")]
    candidates.sort(key=lambda x: -int(x.get("icp_score", 0) or 0))
    candidates = candidates[:top_n]

    persona = ACCOUNTS.get(account, ACCOUNTS[DEFAULT_ACCOUNT])
    print(f"\n🚀 S1 Agent 啟動 — 帳號：{account}（{persona['display_name']}）")
    print(f"   處理 {len(candidates)} 筆 HOT/WARM Lead（來源：{Path(csv_path).name}）\n")

    results = []

    for i, lead in enumerate(candidates, 1):
        name = lead.get("name", "—")
        company = lead.get("company", "—")
        print(f"[{i:02d}/{len(candidates)}] {name} @ {company}")

        # Step 1：分析
        print(f"       → 分析發展邏輯與 AI 使用者類型...")
        analysis = analyze_lead(lead)
        ai_type = analysis.get("ai_type", "B")
        heat = calc_heat_score(lead, ai_type)
        priority = heat_to_priority(heat)

        print(f"       → 類型：{ai_type}（{AI_USER_TYPES.get(ai_type, {}).get('name', '')}）｜Heat：{heat}｜優先級：{priority}")

        # Step 2：生成三封信
        print(f"       → 生成 S1 三封信序列...")
        scripts = generate_s1_scripts(lead, analysis, account)

        conn_req = scripts.get("connection_request", "")
        print(f"       → 連線邀請（{len(conn_req)}字）：{conn_req[:50]}...")
        print()

        result = {
            # Lead 基本資料
            "lead_id":              lead.get("lead_id", ""),
            "name":                 lead.get("name", ""),
            "title":                lead.get("title", ""),
            "company":              lead.get("company", ""),
            "location":             lead.get("location", ""),
            "linkedin_url":         lead.get("linkedin_url", ""),
            "source_strategy":      "S1",
            "source_account":       account,
            "sender_name":          persona["display_name"],
            # 評分
            "icp_score":            lead.get("icp_score", 0),
            "classification":       lead.get("classification", ""),
            "heat_score":           heat,
            "priority":             priority,
            # AI 使用者分析
            "ai_user_type":         ai_type,
            "ai_type_name":         AI_USER_TYPES.get(ai_type, {}).get("name", ""),
            "ai_type_confidence":   analysis.get("ai_type_confidence", ""),
            "development_logic":    analysis.get("development_logic", ""),
            "career_turning_point": analysis.get("career_turning_point", ""),
            "next_goal":            analysis.get("next_goal", ""),
            "recommended_angle":    analysis.get("recommended_angle", ""),
            "personalization_hook": analysis.get("personalization_hook", ""),
            # 三封信序列
            "connection_request":   conn_req,
            "msg1_day1":            scripts.get("msg1", ""),
            "msg2_with_reply":      scripts.get("msg2_with_reply", ""),
            "msg2_no_reply":        scripts.get("msg2_no_reply", ""),
            "msg3_pitch":           scripts.get("msg3", ""),
            # 執行狀態
            "contact_stage":        "連線未發",
            "generated_at":         datetime.now().isoformat(),
            # Asana
            "asana_task_name":      f"[S1][{priority}][{ai_type}] {name} | {lead.get('title','')[:25]} | {company} | Heat:{heat}",
        }
        results.append(result)

    return results


def save_outputs(results: list, account: str):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. 完整 JSON（含所有分析結果）
    json_path = OUTPUT_DIR / f"s1_drafts_{account}_{ts}.json"
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    # 2. Dripify CSV（連線邀請 → custom1，第一封 → custom2）
    dripify_path = OUTPUT_DIR / f"s1_dripify_{account}_{ts}.csv"
    dripify_fields = ["linkedin", "first_name", "last_name", "company_name",
                      "position", "location", "tags", "custom1", "custom2", "custom3"]

    def split_name(full):
        parts = full.strip().split()
        if len(parts) == 1:
            return full, ""
        return " ".join(parts[:-1]), parts[-1]

    with dripify_path.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=dripify_fields)
        w.writeheader()
        for r in results:
            first, last = split_name(r.get("name", ""))
            conn = r.get("connection_request", "")
            if len(conn) > 300:
                conn = conn[:297] + "..."
            w.writerow({
                "linkedin":     r.get("linkedin_url", ""),
                "first_name":   first,
                "last_name":    last,
                "company_name": r.get("company", ""),
                "position":     r.get("title", ""),
                "location":     r.get("location", ""),
                "tags":         f"S1,{r.get('priority','')},{r.get('ai_user_type','')},{account}",
                "custom1":      conn,
                "custom2":      r.get("msg1_day1", "")[:1900],
                "custom3":      f"Heat:{r.get('heat_score','')}|Type:{r.get('ai_user_type','')}",
            })

    # 3. Asana JSON（供 asana_dedup.py 或 Asana API 寫入）
    asana_path = OUTPUT_DIR / f"s1_asana_{account}_{ts}.json"
    asana_tasks = []
    for r in results:
        asana_tasks.append({
            "name": r["asana_task_name"],
            "notes": (
                f"【發展邏輯】{r.get('development_logic', '')}\n\n"
                f"【轉折點】{r.get('career_turning_point', '')}\n"
                f"【下一個目標】{r.get('next_goal', '')}\n"
                f"【建議切入角色】{r.get('recommended_angle', '')}\n\n"
                f"【連線邀請】\n{r.get('connection_request', '')}\n\n"
                f"【第一封（Day 1）】\n{r.get('msg1_day1', '')}\n\n"
                f"【第二封-有回覆版】\n{r.get('msg2_with_reply', '')}\n\n"
                f"【第二封-無回覆追蹤版】\n{r.get('msg2_no_reply', '')}\n\n"
                f"【第三封-引入方案】\n{r.get('msg3_pitch', '')}"
            ),
            "custom_fields": {
                "Heat Score":     r.get("heat_score", 0),
                "AI 使用者類型":   r.get("ai_user_type", ""),
                "策略來源":       "S1",
                "聯絡階段":       "連線未發",
                "執行環境":       "地端 Dripify",
            },
            "linkedin_url":  r.get("linkedin_url", ""),
            "priority":      r.get("priority", "C"),
        })
    asana_path.write_text(json.dumps(asana_tasks, ensure_ascii=False, indent=2), encoding="utf-8")

    return json_path, dripify_path, asana_path


def print_summary(results: list, json_path, dripify_path, asana_path, account: str):
    a_count = sum(1 for r in results if r["priority"] == "A")
    b_count = sum(1 for r in results if r["priority"] == "B")
    type_dist = {}
    for r in results:
        t = r.get("ai_user_type", "?")
        type_dist[t] = type_dist.get(t, 0) + 1

    print("\n" + "=" * 65)
    print(f"  S1 Agent 完成 — 帳號：{account}")
    print("=" * 65)
    print(f"  處理筆數：{len(results)}")
    print(f"  優先級 A（今日執行）：{a_count} 筆")
    print(f"  優先級 B（本週執行）：{b_count} 筆")
    print()
    print(f"  AI 使用者類型分布：")
    for t, cnt in sorted(type_dist.items()):
        print(f"    Type {t}（{AI_USER_TYPES.get(t,{}).get('name','')}）：{cnt} 筆")
    print()

    a_leads = sorted([r for r in results if r["priority"] == "A"],
                     key=lambda x: -x.get("heat_score", 0))[:5]
    if a_leads:
        print(f"  Top A 級 Lead（今日優先觸達）：")
        for r in a_leads:
            print(f"    [Heat:{r['heat_score']}][Type:{r['ai_user_type']}] "
                  f"{r['name']} | {r['title'][:20]} | {r['company']}")

    print()
    print(f"  輸出檔案：")
    print(f"    完整草稿：{json_path.name}")
    print(f"    Dripify：{dripify_path.name}  ← 直接匯入地端 Dripify")
    print(f"    Asana：  {asana_path.name}    ← 寫入 Asana CRM")
    print()
    print(f"  Dripify Campaign 設定提醒：")
    print(f"    連結請求訊息：{{{{custom1}}}}")
    print(f"    Follow-up 1（Day 1 連線接受後）：{{{{custom2}}}}")
    print()
    print(f"  下一步：")
    print(f"    1. 確認 s1_dripify_*.csv 草稿無誤")
    print(f"    2. 匯入 Dripify → 今日 A 級優先執行")
    print(f"    3. 執行 asana_dedup.py 寫入 Asana CRM")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(description="S1 Agent — LinkedIn 直攻法執行引擎")
    parser.add_argument("csv_path", help="apify_linkedin_scraper.py 的輸出 CSV")
    parser.add_argument("--account", choices=list(ACCOUNTS.keys()), default=DEFAULT_ACCOUNT,
                        help=f"發送帳號（預設：{DEFAULT_ACCOUNT}）")
    parser.add_argument("--top", type=int, default=20,
                        help="處理前 N 筆 HOT/WARM Lead（預設：20）")
    args = parser.parse_args()

    if not ANTHROPIC_API_KEY:
        print("❌ 缺少 ANTHROPIC_API_KEY，請在 .env 設定")
        raise SystemExit(1)

    results = process_leads(args.csv_path, args.account, args.top)

    if not results:
        print("⚠ 無可處理的 HOT/WARM Lead")
        return

    json_path, dripify_path, asana_path = save_outputs(results, args.account)
    print_summary(results, json_path, dripify_path, asana_path, args.account)


if __name__ == "__main__":
    main()
