#!/usr/bin/env python3
"""
S1 Lead 草稿 → Dripify CSV 轉換腳本
從 lead-drafts/ 資料夾讀取草稿，產出 Dripify 匯入 CSV

用法：
  python generate_dripify.py
"""

import csv
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent

# ── Lead 資料（直接從草稿文件提取）───────────────────────

LEADS = [
    {
        "linkedin":     "https://www.linkedin.com/in/wanyi-lin/",  # 待補實際 URL
        "first_name":   "宛儀",
        "last_name":    "林",
        "company_name": "Appier",
        "position":     "行銷總監 Marketing Director",
        "location":     "台灣",
        "tags":         "S1,A級,TypeD,kid",
        "ai_type":      "D",
        "heat":         "95",
        "custom1": (
            "林總監，您在 LinkedIn 分享的那篇「AI 提案效率提升 3 倍」我有仔細讀過——"
            "您說的那個問題讓我印象很深：個人提升做到了，但「讓整個團隊一致使用」才是真正的關卡。"
            "這個問題我最近剛好在幫幾個行銷科技客戶處理，發現從「個人效率」到「組織標準化」"
            "中間有一個很多人跳過的步驟。我是 Kid，兌心科技業務。"
            "想跟您交流這個話題，希望有機會加個連結。"
        ),
        "custom2": (
            "林總監，您好，\n\n"
            "我直接說重點：您提到的「AI 工具導入後如何讓整個團隊一致使用」——"
            "這不是一個工具選擇的問題，這是一個管理問題。\n\n"
            "大多數行銷團隊的現況：Prompt 各寫各的、輸出品質不統一、"
            "主管沒辦法對上層報告 ROI。\n\n"
            "AI Token King 讓整個團隊的 AI 使用方式標準化、可追蹤，"
            "讓成果可以拿出數字給老闆看的那種。\n\n"
            "想問您一個問題：您目前的團隊在 AI 使用上，"
            "最大的不一致性發生在哪個環節？\n\n"
            "純粹好奇，沒有要推銷任何東西。\n\nKid"
        ),
    },
    {
        "linkedin":     "https://www.linkedin.com/in/chihao-chang/",  # 待補實際 URL
        "first_name":   "志豪",
        "last_name":    "張",
        "company_name": "（製造業）",
        "position":     "資深業務經理 Senior Sales Manager",
        "location":     "台灣",
        "tags":         "S1,A級,TypeA,kid",
        "ai_type":      "A",
        "heat":         "78",
        "custom1": (
            "志豪你好，你 LinkedIn About 欄位那句「傳統產業遇上 AI，我想成為那個懂得跨越的人」，"
            "我看到的時候停了一下。我在做的事情剛好和這個方向有交集——"
            "不是在賣工具，而是在幫業務型、非技術背景的人，把 AI 的使用方式系統化，"
            "讓它說得出成果、講得出故事。你這 12 年的業務積累加上你現在在做的事，"
            "我覺得有些東西值得聊。希望能加你為連結。Kid"
        ),
        "custom2": (
            "志豪你好，謝謝你接受連結邀請。\n\n"
            "我觀察你的貼文有一陣子了。從分享產品型錄，"
            "到分享 ChatGPT 提示詞、AI 報價單——"
            "你在做的是重新定義自己的業務工作方式。\n\n"
            "我想問你一個問題：你現在用 AI 做這些事，"
            "有沒有一個方式可以讓你在季末向上彙報時，"
            "清楚說出它帶來了什麼效益？\n\n"
            "純粹好奇，沒有要推銷任何東西。\n\nKid"
        ),
    },
    {
        "linkedin":     "https://www.linkedin.com/in/yijun-chen-career/",  # 待補實際 URL
        "first_name":   "怡君",
        "last_name":    "陳",
        "company_name": "職場進化論",
        "position":     "職涯顧問 / 創辦人",
        "location":     "台灣",
        "tags":         "S1,A級,TypeC,kid",
        "ai_type":      "C",
        "heat":         "80",
        "custom1": (
            "怡君你好，看到你說電子書花了三週、用 AI 大概三天就搞定——"
            "這句話很真實，也很多人有共鳴但說不出來。"
            "我在做的事情是幫個人品牌創辦人把零散的 AI 使用習慣，"
            "整理成一套可重複的內容生產流程。"
            "覺得你現在走的路和這件事很接近，想連上線交流。Kid"
        ),
        "custom2": (
            "怡君，連上線後又去把你最近幾篇文章讀了一遍，"
            "你寫跨職能轉型那篇有個觀點讓我印象很深：「轉型不是換跑道，是換看世界的方式」。\n\n"
            "你在限時動態分享 AI 工具心得，我有注意到。有實戰感，但比較零散。\n\n"
            "我想直接問你一個問題：你有沒有想過，"
            "你自己摸索 AI 的這個過程，本身就是一個極好的內容系列？\n\n"
            "你的 HR 背景 + 個人品牌視角 + 親身實踐——這個身份組合幾乎沒有人能複製。\n\n"
            "不知道你現在最花時間的內容環節是哪一塊？想聽你說說。\n\nKid"
        ),
    },
]

DRIPIFY_FIELDS = [
    "linkedin", "first_name", "last_name", "company_name",
    "position", "location", "tags", "custom1", "custom2", "custom3",
]

CONN_LIMIT  = 300
MSG1_LIMIT  = 1900


def truncate(text: str, limit: int, name: str) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) > limit:
        print(f"  ⚠ {name} 超過 {limit} 字（{len(text)}），已截斷")
        return text[:limit - 3] + "..."
    return text


def main():
    ts  = datetime.now().strftime("%Y%m%d")
    out = OUTPUT_DIR / f"s1-batch-{ts}-dripify.csv"

    rows = []
    for lead in LEADS:
        conn = truncate(lead["custom1"], CONN_LIMIT, f"{lead['first_name']} 連線邀請")
        msg1 = truncate(lead["custom2"], MSG1_LIMIT, f"{lead['first_name']} 第一封")
        rows.append({
            "linkedin":     lead["linkedin"],
            "first_name":   lead["first_name"],
            "last_name":    lead["last_name"],
            "company_name": lead["company_name"],
            "position":     lead["position"],
            "location":     lead["location"],
            "tags":         lead["tags"],
            "custom1":      conn,
            "custom2":      msg1,
            "custom3":      f"Heat:{lead['heat']}|Type:{lead['ai_type']}|S1",
        })

    with out.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=DRIPIFY_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n{'='*60}")
    print(f"  Dripify CSV 已產出：{out.name}")
    print(f"{'='*60}")
    print(f"  總筆數：{len(rows)}")
    for r in rows:
        print(f"  [{r['tags'].split(',')[1]}] {r['first_name']}{r['last_name']} @ {r['company_name']}")
        print(f"    連線邀請：{len(r['custom1'])} 字  第一封：{len(r['custom2'])} 字")
    print(f"\n  Dripify Campaign 設定提醒：")
    print(f"    連結請求訊息 → {{{{custom1}}}}")
    print(f"    Follow-up 1（連線接受後 Day 1）→ {{{{custom2}}}}")
    print(f"\n  注意：custom1 含換行會被壓縮為空格（LinkedIn 連線邀請限制）")
    print(f"        custom2 保留換行，Dripify 會正常顯示段落")
    print(f"\n  匯入步驟：")
    print(f"    1. Dripify → Leads → Import → Upload CSV")
    print(f"    2. 上傳 {out.name}")
    print(f"    3. 確認 LinkedIn URL 欄位對應正確")
    print(f"    ⚠ 執行前請先確認每筆 LinkedIn URL 為正確的個人檔案連結")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
