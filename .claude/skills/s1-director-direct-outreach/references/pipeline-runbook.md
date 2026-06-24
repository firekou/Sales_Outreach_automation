# Phase 4 & 5 參考 — Pipeline Runbook（管道、排程、追蹤）

整合自 `scripts/HOWTO.md` 與 `strategies/07-orchestrator-spec.md`。

---

## 0. 前置設定

```bash
cd scripts/
cp .env.example .env      # 填入 ANTHROPIC_API_KEY / APIFY_TOKEN / LINKEDIN_LI_AT /
                          #      ASANA_TOKEN / ASANA_PROJECT_GID / MAKE_WEBHOOK_URL / SLACK_WEBHOOK_URL
pip install -r requirements.txt
```

---

## 1. 完整指令鏈（一筆名單從抓到發）

```bash
# Step 1 抓名單 + ICP 評分 + 去重
python apify_linkedin_scraper.py --account frank        # → output/leads_*.csv

# Step 2 生成個人化草稿（pending_review）
python linkedin_processor.py draft output/leads_*.csv --account frank   # → drafts_*.json

# Step 3 匯入 Asana（人工在 Asana 審核、核准）
python linkedin_processor.py asana output/leads_*.csv --account frank

# Step 4 轉成發送工具 CSV
python dripify_export.py output/drafts_*.json --account frank           # → dripify_frank_*.csv

# Step 5 觸發發送（或交給 Make.com 偵測 Asana 狀態變更後自動發）
python linkedin_processor.py webhook output/drafts_*.json

# 回覆分析（Hot Lead → Slack SLA 2 小時）
python linkedin_processor.py reply "對方回覆文字" --account frank \
  --lead-name "王大明" --lead-company "智慧科技" --lead-title "IT Director" --icp-score 85
```

---

## 2. Dripify 匯入

| 序列步驟 | Dripify 訊息欄位 | 來源 |
|---------|----------------|------|
| 連結請求（Day 0） | `{{custom1}}` | Claude 生成連線邀請（≤300 字元） |
| Follow-up 1（Day 3） | `{{custom2}}` | Claude 生成價值觸達（第一封 Day 1） |
| Follow-up 2（Day 7） | 通用版 `Hi {{firstName}}, ...` | 自行撰寫 |

Campaign Settings（試營運／Frank）：每日上限 25 連結請求、工作日 08:00–17:00 台灣時間、操作間隔隨機 3–15 秒（用預設、勿改短）。

---

## 3. Expandi 匯入（Sales Navigator Campaign）

CSV：`s1-batch-YYYYMMDD-expandi.csv`；custom 對應 `custom1`＝連線邀請、`custom2`＝Day 1、`custom3`＝Day 7 追蹤。

```
Step 1 Visit Profile（等待 0 天，提升接受率）
Step 2 Connect      → {{custom1}}（≤200 字），等待直到接受
Step 3 Message Day1 → {{custom2}}（≤300 字），等待 7 天
Step 4 Message Day7 → {{custom3}}（≤350 字，無回覆追蹤）→ 結束/轉人工
```

設定：類型選 Sales Navigator、每日 Connection 25/day、發送時段 08:00–09:00、開啟 Smart Limits。
範例見 `lead-drafts/outreach-schedule-20260615.md` 與 `lead-drafts/s1-expandi-sequence-20260615.md`。

---

## 4. 排程（混合架構：雲端分析 + 地端操作）

LinkedIn 封鎖 Datacenter IP，故**只把需要 LinkedIn 帳號操作的部分留在地端**，其餘上雲。

**雲端（GitHub Actions cron，`55 0 * * 1-5` = TST 09:05）**：Apify 抓取（Residential Proxy）→ ICP/Heat 評分 → 去重 → Asana 寫入 → 09:10 每日簡報 Email（Frank）→ 產出 Dripify/Expandi CSV 至 Dropbox/Drive。

**地端（Mac launchd / Windows 工作排程器，09:00）**：`local_runner.py` 下載 CSV → 匯入 Dripify/Expandi（走本機住宅 IP 的瀏覽器 session，LinkedIn 視為正常人類）→ 回報 Asana。

完整 YAML、launchd plist、例外處理見 `strategies/07-orchestrator-spec.md`。

---

## 5. 每日配額（保護帳號，不可超量）

| 操作 | 每日上限 | 環境 |
|------|---------|------|
| 連線邀請 | 20–25 封/帳號 | 地端 Dripify/Expandi |
| 私訊 | 30 封 | 地端 |
| 社群評論（S5） | 5 則 | 地端人工確認 |

多帳號分時段並行範例（每日總配額約 125）：

| 時間窗 | 帳號 | 指令 |
|--------|------|------|
| 08:00–09:00 | frank | `python apify_linkedin_scraper.py --account frank` |
| 10:00–11:00 | jet | `... --account jet` |
| 11:00–12:00 | alice | `... --account alice` |
| 14:00–15:00 | kid | `... --account kid` |
| 16:00–17:00 | lauren | `... --account lauren` |

超配額的 A 級 Lead → 自動順延隔日，不降級。觸發異常警報 → 立即停手 24 小時。

---

## 6. Asana CRM 追蹤

Project 分區：🔴 A 級（今日）/ 🟡 B 級（本週）/ ⚪ 觀察池 / ✅ 已回覆 / ❌ 無回應 >21 天。

Task 欄位：名稱 `[姓名] @ [公司] — S1`；自訂欄位 Heat Score、AI 使用者類型、策略來源（多選）、
聯絡階段（連線未發 → 等待接受 → 第一封 → 第二封 → 第三封 → 進入 Demo）、執行環境。

追蹤週期：無回應 7 天追蹤、21 天最後一封給優雅出口、60 天移入 Nurture 清單等新訊號。
去重檢查：`python asana_dedup.py check output/leads_*.csv`。

---

## 7. 稽核（收尾，別自欺）

每週交給 `ALI-Auditor` agent 做漏斗真實性稽核：回覆真實性評分、漏斗完整性、效果歸因，
淘汰低回覆率的話術版本。Director 回報時據實呈現，不誇大數字。
