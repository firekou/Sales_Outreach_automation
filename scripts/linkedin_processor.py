#!/usr/bin/env python3
"""
AI Token King — LinkedIn Lead 處理引擎 v2
抓取後的 CSV 處理：評分、草稿生成、回覆分析、Asana 匯入、Make.com Webhook 觸發

用法：
  python linkedin_processor.py score   output/leads_xxx.csv [--account kid]
  python linkedin_processor.py draft   output/leads_xxx.csv [--account kid]
  python linkedin_processor.py reply   "對方回覆的文字內容" [--account kid]
  python linkedin_processor.py asana   output/leads_xxx.csv [--account kid]
  python linkedin_processor.py webhook output/drafts_xxx.json  ← 觸發 Make.com 自動發送

流程：
  1. score  → 評分排序
  2. draft  → 生成草稿（草稿寫入 Asana，等待人工審核）
  3. [人工審核] → 在 Asana 將草稿狀態改為「已核准」
  4. webhook → Make.com 偵測狀態變更 → Phantombuster 自動發送 LinkedIn 訊息
  5. reply  → 回覆分類 + Hot Lead 立即 Slack 通知
"""

import os
import sys
import csv
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import anthropic
    from dotenv import load_dotenv
except ImportError:
    print("請先安裝：pip install -r requirements.txt")
    raise

try:
    import requests as _requests
except ImportError:
    _requests = None

load_dotenv()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MAKE_WEBHOOK_URL   = os.getenv("MAKE_WEBHOOK_URL", "")
SLACK_WEBHOOK_URL  = os.getenv("SLACK_WEBHOOK_URL", "")
client_ai = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── 多帳號人設 ─────────────────────────────────────────────
ACCOUNT_PERSONAS = {
    "frank": {
        "display_name": "Frank Kao",
        "title": "CEO, AI Token King",
        "style": "高層對高層。語氣從容、重願景與風險管控。不用銷售話術，用商業判斷說話。",
        "daily_limit": 25,
        "send_window": "08:00–09:00",
    },
    "jet": {
        "display_name": "Jet",
        "title": "Business Director, AI Token King",
        "style": "商務合作切入。著重通路機會與毛利結構。直接說明雙贏空間，不拐彎抹角。",
        "daily_limit": 25,
        "send_window": "10:00–11:00",
    },
    "kid": {
        "display_name": "Kid",
        "title": "業務銷售, AI Token King",
        "style": "親切 ENFJ 風格。直接切痛點，語氣像朋友。主動但不卑微，結尾用選擇題不用拜託。",
        "daily_limit": 30,
        "send_window": "14:00–15:00",
    },
    "lauren": {
        "display_name": "Lauren",
        "title": "商務暨人資主管, AI Token King",
        "style": "BD 合作視角。著重行銷代理商效率痛點。帶出 AI 工具統一管理如何幫代理商提高利潤。",
        "daily_limit": 25,
        "send_window": "16:00–17:00",
    },
    "alice": {
        "display_name": "Alice Wu",
        "title": "Product Manager, AI Token King",
        "style": "產品對產品。技術同理心，INFP 溫和好奇。從產品人的視角問問題，不說教。",
        "daily_limit": 20,
        "send_window": "11:00–12:00",
    },
}
DEFAULT_ACCOUNT = "kid"

# ── ICP 評分規則 ──────────────────────────────────────────
AI_KW = ["ChatGPT", "OpenAI", "Claude", "Gemini", "AI", "LLM", "Copilot",
         "artificial intelligence", "machine learning", "Prompt"]
CLOUD_KW = ["AWS", "GCP", "Azure", "Bedrock", "Vertex", "Alibaba Cloud",
            "Tencent Cloud", "Volcano", "Doubao", "Huawei Cloud"]
PRIORITY_INDUSTRIES = {
    "Computer Software": 25, "Internet": 22,
    "Information Technology and Services": 22,
    "Marketing and Advertising": 20,
    "Management Consulting": 18,
    "Professional Services": 15,
    "E-commerce": 18, "Education": 15,
}
SIZE_SCORE = {"11-50": 20, "51-200": 25, "1-10": 5, "201-500": 10}


def icp_score(lead: dict) -> int:
    text = f"{lead.get('title','')} {lead.get('summary_snippet','')}".lower()
    score = SIZE_SCORE.get(lead.get("company_size", ""), 5)
    score += PRIORITY_INDUSTRIES.get(lead.get("industry", ""), 5)
    score += min(sum(1 for kw in AI_KW if kw.lower() in text) * 6, 25)
    score += min(sum(1 for kw in CLOUD_KW if kw.lower() in text) * 8, 25)
    return min(score, 100)


def classify(score: int) -> str:
    return "HOT" if score >= 70 else "WARM" if score >= 50 else "COLD"


# ── Claude 訊息草稿生成（帳號人設動態注入）──────────────
def get_connection_system(account: str) -> str:
    persona = ACCOUNT_PERSONAS.get(account, ACCOUNT_PERSONAS[DEFAULT_ACCOUNT])
    return f"""你是 {persona['display_name']}，{persona['title']}。
風格要求：{persona['style']}
任務：幫目標 Lead 寫一段 LinkedIn 連結請求附言（≤300字元，繁體中文）。
規則：像朋友、不推銷、先表達好奇和共鳴。結尾不要說「請多指教」。
格式：直接輸出訊息文字，不要加任何前綴說明。"""


def get_value_system(account: str) -> str:
    persona = ACCOUNT_PERSONAS.get(account, ACCOUNT_PERSONAS[DEFAULT_ACCOUNT])
    return f"""你是 {persona['display_name']}，{persona['title']}。
風格要求：{persona['style']}
任務：為這位 Lead 寫第一封價值觸達訊息（繁體中文，≤500字）。
結構：① 你觀察到的現象（跟對方公司/職稱相關）→ ② AI Token King 如何解決這個問題 → ③ 開放式問句收尾。
禁止：不要說「我想介紹我們的產品」。三版訊息可選：A（管理者痛點）B（老闆視角）C（代理商機會）。
格式：直接輸出訊息文字，不要加任何前綴說明。"""


def get_reply_system(account: str) -> str:
    persona = ACCOUNT_PERSONAS.get(account, ACCOUNT_PERSONAS[DEFAULT_ACCOUNT])
    return f"""你是 {persona['display_name']}，{persona['title']}。
分析這段 LinkedIn 回覆屬於哪一類，並建議下一步行動。
輸出 JSON（僅輸出 JSON，不加任何說明）：
{{
  "classification": "positive|neutral|negative",
  "sentiment_score": 1-5,
  "is_hot_lead": true|false,
  "key_signal": "對方說了什麼關鍵字",
  "route_to": "直銷/#leads-直銷|通路/#leads-通路|人工/#lead-review",
  "next_action": "下一步行動（一句話）",
  "reply_draft": "建議回覆訊息（繁體中文，≤300字）"
}}"""


def ai_message(system: str, user_prompt: str, max_tokens: int = 600) -> str:
    if not client_ai:
        return "[需要 ANTHROPIC_API_KEY 才能生成 AI 訊息]"
    msg = client_ai.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return msg.content[0].text.strip()


# ── Webhook / 通知 ─────────────────────────────────────────
def trigger_make_webhook(payload: dict, label: str = "") -> bool:
    """觸發 Make.com Webhook，啟動自動發送流程"""
    if not MAKE_WEBHOOK_URL:
        print(f"  ⚠ MAKE_WEBHOOK_URL 未設定，跳過 {label or 'webhook'}")
        return False
    if not _requests:
        print("  ⚠ requests 未安裝，跳過 webhook")
        return False
    try:
        resp = _requests.post(MAKE_WEBHOOK_URL, json=payload, timeout=10)
        if resp.status_code == 200:
            print(f"  ✅ Make.com webhook 已觸發：{label}")
            return True
        print(f"  ⚠ Make.com 回應 {resp.status_code}：{resp.text[:100]}")
    except Exception as e:
        print(f"  ⚠ Make.com webhook 失敗：{e}")
    return False


def notify_slack_hot_lead(lead_info: dict, reply_text: str, analysis: dict):
    """Hot Lead 偵測後立即推播 Slack 通知"""
    if not SLACK_WEBHOOK_URL:
        return
    if not _requests:
        return
    channel = analysis.get("route_to", "#lead-review").split("/")[-1]
    msg = {
        "text": f"🔥 *Hot Lead 回覆* — 請 2 小時內跟進",
        "blocks": [
            {"type": "header", "text": {"type": "plain_text", "text": "🔥 Hot Lead 回覆偵測"}},
            {"type": "section", "fields": [
                {"type": "mrkdwn", "text": f"*姓名：*\n{lead_info.get('name', '—')}"},
                {"type": "mrkdwn", "text": f"*公司：*\n{lead_info.get('company', '—')}"},
                {"type": "mrkdwn", "text": f"*職稱：*\n{lead_info.get('title', '—')}"},
                {"type": "mrkdwn", "text": f"*ICP 分數：*\n{lead_info.get('icp_score', '—')}"},
                {"type": "mrkdwn", "text": f"*路由頻道：*\n#{channel}"},
                {"type": "mrkdwn", "text": f"*關鍵訊號：*\n{analysis.get('key_signal', '—')}"},
            ]},
            {"type": "section", "text": {"type": "mrkdwn",
                "text": f"*對方回覆：*\n> {reply_text[:300]}"}},
            {"type": "section", "text": {"type": "mrkdwn",
                "text": f"*建議回覆草稿：*\n{analysis.get('reply_draft', '—')}"}},
            {"type": "section", "text": {"type": "mrkdwn",
                "text": f"*下一步：* {analysis.get('next_action', '—')}  |  SLA：⏰ 2 小時內"}},
        ],
    }
    try:
        _requests.post(SLACK_WEBHOOK_URL, json=msg, timeout=10)
    except Exception:
        pass


def build_lead_prompt(lead: dict) -> str:
    return (
        f"姓名：{lead.get('name', '對方')}\n"
        f"職稱：{lead.get('title', '')}\n"
        f"公司：{lead.get('company', '')}\n"
        f"公司規模：{lead.get('company_size', '')} 人\n"
        f"行業：{lead.get('industry', '')}\n"
        f"個人摘要：{lead.get('summary_snippet', '')}\n"
        f"ICP 分類：{lead.get('classification', '')}\n"
        f"搜尋組合：{lead.get('combo_name', '')}"
    )


def cmd_score(csv_path: str):
    leads = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))

    for lead in leads:
        s = icp_score(lead)
        lead["icp_score"] = s
        lead["classification"] = classify(s)

    leads.sort(key=lambda x: -int(x["icp_score"]))
    hot = [l for l in leads if l["classification"] == "HOT"]
    warm = [l for l in leads if l["classification"] == "WARM"]

    print(f"\n📊 ICP 評分完成  總計 {len(leads)} 筆")
    print(f"   HOT  {len(hot)} 筆 | WARM {len(warm)} 筆 | COLD {len(leads)-len(hot)-len(warm)} 筆\n")
    print(f"{'分數':>5}  {'分類':>5}  {'姓名':<12}  {'職稱':<25}  {'公司'}")
    print("─" * 80)
    for l in leads[:30]:
        print(f"{l['icp_score']:>5}  {l['classification']:>5}  "
              f"{l['name']:<12}  {l['title'][:24]:<25}  {l['company']}")
    if len(leads) > 30:
        print(f"  ... 還有 {len(leads)-30} 筆，查看 CSV")

    out = OUTPUT_DIR / f"scored_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=leads[0].keys())
        writer.writeheader()
        writer.writerows(leads)
    print(f"\n💾 已儲存：{out.name}")


def cmd_draft(csv_path: str, account: str = DEFAULT_ACCOUNT):
    leads = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    hot_leads = [l for l in leads if l.get("classification") in ("HOT", "WARM")]

    if not hot_leads:
        print("⚠ 沒有 HOT/WARM 等級的 Lead，請先執行 score 指令確認分類。")
        return

    persona = ACCOUNT_PERSONAS.get(account, ACCOUNT_PERSONAS[DEFAULT_ACCOUNT])
    conn_sys  = get_connection_system(account)
    value_sys = get_value_system(account)

    print(f"\n✍ 帳號 [{account}] {persona['display_name']} — 生成 {len(hot_leads)} 筆草稿...\n")
    results = []

    for i, lead in enumerate(hot_leads, 1):
        prompt = build_lead_prompt(lead)
        print(f"[{i}/{len(hot_leads)}] {lead.get('name')} | {lead.get('company')}")

        conn_msg  = ai_message(conn_sys, prompt)
        value_msg = ai_message(value_sys, prompt)

        result = {
            "name":               lead.get("name"),
            "title":              lead.get("title"),
            "company":            lead.get("company"),
            "icp_score":          lead.get("icp_score"),
            "classification":     lead.get("classification"),
            "linkedin_url":       lead.get("linkedin_url"),
            "source_account":     lead.get("source_account", account),
            "sender_name":        persona["display_name"],
            "connection_request": conn_msg,
            "value_touch":        value_msg,
            "asana_task_name":    lead.get("asana_task_name", ""),
            "draft_status":       "pending_review",
            "generated_at":       datetime.now().isoformat(),
        }
        results.append(result)

        print(f"  連結請求：{conn_msg[:60]}...")
        print(f"  價值觸達：{value_msg[:60]}...")
        print()

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_json = OUTPUT_DIR / f"drafts_{ts}.json"
    out_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    out_csv = OUTPUT_DIR / f"drafts_{ts}.csv"
    with out_csv.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"💾 草稿已儲存：{out_json.name}")
    print(f"\n📋 下一步流程：")
    print(f"  1. 在 Asana 審閱草稿（狀態：pending_review）")
    print(f"  2. 核准後將 Asana 任務「Connection Status」改為「已核准」")
    print(f"  3. Make.com 偵測到狀態變更，自動呼叫 Phantombuster 發送 LinkedIn 訊息")
    print(f"  ─ 或手動觸發：python linkedin_processor.py webhook {out_json.name}")


def cmd_reply(reply_text: str, account: str = DEFAULT_ACCOUNT,
              lead_name: str = "", lead_company: str = "",
              lead_title: str = "", icp_score: str = ""):
    print(f"\n🔍 分析回覆中...\n原文：{reply_text[:100]}...\n")

    reply_sys = get_reply_system(account)
    result_text = ai_message(reply_sys, f"LinkedIn 回覆原文：\n{reply_text}", max_tokens=800)

    try:
        result = json.loads(result_text)
    except json.JSONDecodeError:
        result = {"raw": result_text, "classification": "unclear"}

    cls = result.get("classification", "unclear")
    cls_cn = {"positive": "✅ 正面", "neutral": "➡️ 中性", "negative": "❌ 負面"}.get(cls, f"❓ {cls}")
    is_hot = result.get("is_hot_lead", cls == "positive")

    print(f"分類：{cls_cn}  {'🔥 HOT LEAD' if is_hot else ''}")
    print(f"情感分數：{result.get('sentiment_score', '?')} / 5")
    print(f"關鍵訊號：{result.get('key_signal', '')}")
    print(f"路由頻道：{result.get('route_to', '#lead-review')}")
    print(f"下一步：{result.get('next_action', '')}")
    print(f"\n── 建議回覆草稿 ──────────────────────────────")
    print(result.get("reply_draft", "[生成失敗]"))
    print("──────────────────────────────────────────────")

    # Hot Lead → 立即 Slack 通知
    if is_hot and SLACK_WEBHOOK_URL:
        lead_info = {"name": lead_name, "company": lead_company,
                     "title": lead_title, "icp_score": icp_score}
        notify_slack_hot_lead(lead_info, reply_text, result)
        print(f"\n🔔 已推播 Slack 通知至 {result.get('route_to', '#lead-review')}（SLA：2 小時）")
    elif is_hot:
        print(f"\n⚠ SLACK_WEBHOOK_URL 未設定，請手動通知 {result.get('route_to', '#lead-review')}")


def cmd_asana(csv_path: str, account: str = DEFAULT_ACCOUNT):
    leads = list(csv.DictReader(open(csv_path, encoding="utf-8-sig")))
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = OUTPUT_DIR / f"asana_import_{ts}.csv"

    asana_fields = [
        "Name", "Section/Column", "Assignee", "Due Date",
        "ICP Score", "Classification", "Company", "Title",
        "Company Size", "Industry", "LinkedIn URL", "Lead Source",
        "Source Account", "Sender Name",
        "Touch Number", "Connection Status", "Reply Status",
        "Purchase Intent", "Search Combo", "Scrape Date", "Notes",
    ]

    section_map = {"HOT": "04 Replied — HOT", "WARM": "01 Connection Sent", "COLD": "00 Lead Pool"}
    persona = ACCOUNT_PERSONAS.get(account, ACCOUNT_PERSONAS[DEFAULT_ACCOUNT])

    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=asana_fields)
        writer.writeheader()
        for l in leads:
            cls = l.get("classification", "COLD")
            acc = l.get("source_account", account)
            writer.writerow({
                "Name": l.get("asana_task_name") or (
                    f"[{cls}][{acc}] "
                    f"{l.get('name','')} | {l.get('title','')[:25]} | "
                    f"{l.get('company','')} | {l.get('icp_score',0)}分"
                ),
                "Section/Column":  section_map.get(cls, "00 Lead Pool"),
                "Assignee":        "frank.kao@insight-software.com",
                "Due Date":        "",
                "ICP Score":       l.get("icp_score", ""),
                "Classification":  cls,
                "Company":         l.get("company", ""),
                "Title":           l.get("title", ""),
                "Company Size":    l.get("company_size", ""),
                "Industry":        l.get("industry", ""),
                "LinkedIn URL":    l.get("linkedin_url", ""),
                "Lead Source":     l.get("lead_source", "A-LI-Scout/Apify"),
                "Source Account":  acc,
                "Sender Name":     l.get("sender_name", persona["display_name"]),
                "Touch Number":    l.get("touch_number", "D1-待發"),
                "Connection Status": l.get("connection_status", "待發送"),
                "Reply Status":    l.get("reply_status", "未回覆"),
                "Purchase Intent": l.get("purchase_intent", "1"),
                "Search Combo":    l.get("combo_name", ""),
                "Scrape Date":     l.get("scrape_date", ""),
                "Notes":           "",
            })

    print(f"\n📋 Asana 匯入檔已生成：{out.name}")
    print(f"   共 {len(leads)} 筆 Task（來源帳號：{account}）")
    print(f"\n匯入步驟：")
    print(f"  1. Asana 專案 → Import / Export → Import CSV")
    print(f"  2. 選擇此 CSV 檔案")
    print(f"  3. 欄位對應確認（注意 Source Account / Sender Name 欄位）後匯入")
    print(f"  💡 建議先執行 asana_dedup.py check 確認無重複")


def cmd_webhook(drafts_json_path: str):
    """手動觸發 Make.com Webhook，將核准的草稿送出自動發送流程"""
    drafts = json.loads(Path(drafts_json_path).read_text(encoding="utf-8"))
    approved = [d for d in drafts if d.get("draft_status") in ("approved", "已核准", None)]

    if not approved:
        print("⚠ 沒有狀態為『已核准』的草稿，請先在 Asana 審核。")
        print("  提示：將 draft_status 改為 'approved' 或在 Asana 中核准後 Make.com 會自動觸發。")
        return

    print(f"\n🚀 觸發 Make.com Webhook — {len(approved)} 筆草稿")
    success = 0
    for d in approved:
        payload = {
            "event":       "send_connection_request",
            "linkedin_url": d.get("linkedin_url"),
            "sender":       d.get("source_account", DEFAULT_ACCOUNT),
            "sender_name":  d.get("sender_name", ""),
            "message":      d.get("connection_request", ""),
            "lead_name":    d.get("name", ""),
            "company":      d.get("company", ""),
            "icp_score":    d.get("icp_score", ""),
            "asana_task":   d.get("asana_task_name", ""),
        }
        label = f"{d.get('name')} @ {d.get('company')}"
        if trigger_make_webhook(payload, label):
            success += 1

    print(f"\n✅ 已觸發 {success}/{len(approved)} 筆  |  Make.com → Phantombuster → LinkedIn 自動發送中")


COMMANDS = {
    "score":   (cmd_score,   "score   <leads.csv>        [--account X]  — 重新評分並排序"),
    "draft":   (cmd_draft,   "draft   <leads.csv>        [--account X]  — 生成 HOT/WARM 訊息草稿"),
    "reply":   (cmd_reply,   "reply   <回覆文字>         [--account X]  — 分析回覆 + Hot Lead Slack 通知"),
    "asana":   (cmd_asana,   "asana   <leads.csv>        [--account X]  — 輸出 Asana 匯入 CSV"),
    "webhook": (cmd_webhook, "webhook <drafts.json>                     — 觸發 Make.com 自動發送"),
}
ACCOUNT_CHOICES = list(ACCOUNT_PERSONAS.keys())


def main():
    parser = argparse.ArgumentParser(description="AI Token King — LinkedIn Lead 處理引擎 v2")
    parser.add_argument("command", choices=list(COMMANDS.keys()), help="執行指令")
    parser.add_argument("target", nargs="?", help="CSV / JSON 路徑 或 回覆文字")
    parser.add_argument("--account", choices=ACCOUNT_CHOICES, default=DEFAULT_ACCOUNT,
                        help=f"發送帳號（default: {DEFAULT_ACCOUNT}）")
    parser.add_argument("--lead-name",    default="", help="reply 指令：Lead 姓名（供 Slack 通知用）")
    parser.add_argument("--lead-company", default="", help="reply 指令：Lead 公司（供 Slack 通知用）")
    parser.add_argument("--lead-title",   default="", help="reply 指令：Lead 職稱（供 Slack 通知用）")
    parser.add_argument("--icp-score",    default="", help="reply 指令：ICP 分數（供 Slack 通知用）")

    # 相容舊版：直接 sys.argv 傳入
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    cmd = args.command

    if cmd in ("score", "asana"):
        if not args.target:
            print("❌ 請提供 CSV 路徑")
            sys.exit(1)
        if cmd == "score":
            cmd_score(args.target)
        else:
            cmd_asana(args.target, args.account)

    elif cmd == "draft":
        if not args.target:
            print("❌ 請提供 CSV 路徑")
            sys.exit(1)
        cmd_draft(args.target, args.account)

    elif cmd == "reply":
        if not args.target:
            print("❌ 請提供回覆文字（用引號包起來）")
            sys.exit(1)
        cmd_reply(
            args.target,
            account=args.account,
            lead_name=args.lead_name,
            lead_company=args.lead_company,
            lead_title=args.lead_title,
            icp_score=args.icp_score,
        )

    elif cmd == "webhook":
        if not args.target:
            print("❌ 請提供 drafts JSON 路徑")
            sys.exit(1)
        cmd_webhook(args.target)


if __name__ == "__main__":
    main()
