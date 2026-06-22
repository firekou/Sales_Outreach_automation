# LinkedIn Lead 自動化系統 — 操作手冊 v2

## 資料夾結構

```
scripts/
├── apify_linkedin_scraper.py   # Step 1：從 LinkedIn 抓取名單（支援多帳號）
├── linkedin_processor.py       # Step 2：評分、草稿生成、Asana 匯出、Webhook 觸發
├── asana_dedup.py              # Step 2a：Asana CRM 去重工具
├── requirements.txt
├── .env.example                # 複製為 .env 後填入金鑰
├── HOWTO.md                    # 本文件
└── output/                     # 所有輸出檔案存放處
```

## Dripify 自動發送整合

### 標準流程（三步驟）

```bash
# Step 1：生成個人化草稿
python linkedin_processor.py draft output/leads_*.csv --account frank

# Step 2：轉換成 Dripify CSV
python dripify_export.py output/drafts_*.json --account frank
# → 輸出 output/dripify_frank_*.csv

# Step 3：上傳 Dripify → Leads → Import → Upload CSV
```

### Dripify Campaign 訊息設定（重要）

上傳 CSV 後，在 Campaign 的訊息欄位填入以下變數，讓每個 Lead 收到 Claude 生成的個人化訊息：

| 序列步驟 | Dripify 訊息欄位 | 說明 |
|---------|----------------|------|
| 連結請求（Day 0）| `{{custom1}}` | Claude 生成的 ≤300 字元個人化附言 |
| Follow-up 1（Day 3）| `{{custom2}}` | Claude 生成的價值觸達訊息 |
| Follow-up 2（Day 7）| 自行撰寫通用版 | 可用 `Hi {{firstName}}, ...` 格式 |

### 試營運速率設定（Frank 帳號）

Dripify 後台 → Campaign Settings：
- **每日上限：25 個連結請求**
- **發送時間：工作日 08:00–17:00 台灣時間**
- **操作間隔：隨機 3–15 秒**（Dripify 預設即可，不要改短）

---



```bash
cd scripts/
cp .env.example .env
```

編輯 `.env`，填入以下值：

| 變數 | 必填 | 取得方式 |
|------|------|---------|
| `ANTHROPIC_API_KEY` | ✅ | https://console.anthropic.com → API Keys |
| `APIFY_TOKEN` | ✅ | https://console.apify.com/account/integrations |
| `LINKEDIN_LI_AT` | ✅ | Chrome → F12 → Application → Cookies → linkedin.com → `li_at` |
| `ASANA_TOKEN` | ✅ | Asana → My Settings → Apps → Personal Access Tokens |
| `ASANA_PROJECT_GID` | ✅ | LinkedIn CRM 專案 URL 中的 GID 數字 |
| `MAKE_WEBHOOK_URL` | ✅ | Make.com → Webhook 模組 → 複製 URL |
| `SLACK_WEBHOOK_URL` | ✅ | Slack → Incoming Webhooks → 複製 URL |

---

## 全自動化流程（每日執行）

```
每日 08:00（Make.com Orchestrator 觸發）
  │
  ├── Step 1：apify_linkedin_scraper.py --account [帳號名稱]
  │           → 抓取名單、ICP 評分（HOT≥70 / WARM 50-69 / COLD<50）
  │           → 自動 Asana 去重（跳過任何帳號已接觸過的）
  │           → 輸出 output/leads_*.csv
  │
  ├── Step 2：linkedin_processor.py draft output/leads_*.csv --account [帳號名稱]
  │           → 為 HOT/WARM Lead 生成個人化草稿
  │           → 輸出 output/drafts_*.json（draft_status: pending_review）
  │           → Asana 匯入：linkedin_processor.py asana output/leads_*.csv
  │
  ├── Step 3：[人工審核] 在 Asana 將草稿 Connection Status 改為「已核准」
  │           ↳ 這是唯一需要人工操作的步驟
  │
  ├── Step 4：Make.com 偵測 Asana 狀態變更 → 呼叫 Phantombuster → 自動發送 LinkedIn 訊息
  │           ↳ 或手動觸發：python linkedin_processor.py webhook output/drafts_*.json
  │
  └── Step 5：Track Agent（每日 17:00，Make.com 觸發）
              → Apify 掃描 LinkedIn 訊息回覆
              → Claude Haiku 分類（positive/neutral/negative）
              → Hot Lead → 立即 Slack 推播（SLA 2 小時）
              → 更新 Asana 任務狀態
```

---

## 多帳號執行（每日並行）

| 時間窗 | 帳號 | 指令 |
|--------|------|------|
| 08:00–09:00 | frank | `python apify_linkedin_scraper.py --account frank` |
| 10:00–11:00 | jet | `python apify_linkedin_scraper.py --account jet` |
| 11:00–12:00 | alice | `python apify_linkedin_scraper.py --account alice` |
| 14:00–15:00 | kid | `python apify_linkedin_scraper.py --account kid` |
| 16:00–17:00 | lauren | `python apify_linkedin_scraper.py --account lauren` |

**每日總配額：125 connections（frank 25 + jet 25 + alice 20 + kid 30 + lauren 25）**

---

## 手動指令參考

### 重新評分
```bash
python linkedin_processor.py score output/leads_xxx.csv
```

### 生成草稿（指定帳號）
```bash
python linkedin_processor.py draft output/leads_xxx.csv --account kid
python linkedin_processor.py draft output/leads_xxx.csv --account frank
```

### 分析 Lead 回覆（含 Hot Lead Slack 通知）
```bash
python linkedin_processor.py reply "謝謝你的訊息，我們目前有在評估 AI 工具" \
  --account kid \
  --lead-name "王大明" \
  --lead-company "智慧科技" \
  --lead-title "IT Director" \
  --icp-score "85"
```

### 匯出 Asana CRM CSV
```bash
python linkedin_processor.py asana output/leads_xxx.csv --account kid
```

### Asana 去重檢查
```bash
python asana_dedup.py check output/leads_xxx.csv
python asana_dedup.py stats
python asana_dedup.py lookup "https://linkedin.com/in/someone"
```

### 觸發 Make.com 自動發送
```bash
python linkedin_processor.py webhook output/drafts_xxx.json
```

---

## ICP 評分邏輯

| 分類 | 分數 | 行動 |
|------|------|------|
| HOT | ≥70 | 同日生成草稿，審核後自動發送 |
| WARM | 50–69 | 次日批次，審核後自動發送 |
| COLD | <50 | 培育池，每月觸達 |

評分因子：職稱決策力（30pt）+ 公司規模（15pt）+ 產業匹配（20pt）+ 活躍度（15pt）+ AI 痛點訊號（20pt）

---

## 搜尋組合說明

| 組合 | 目標族群 | 上限 | 優先 |
|------|---------|------|------|
| A | 科技公司 IT 決策者（11-200人） | 80 | P1 |
| B | 行銷代理商高層（11-200人） | 60 | P2 |
| C | 數位轉型顧問/CDO（11-200人） | 60 | P3 |
| D | SaaS/軟體新創 CTO/VP（11-200人） | 80 | P1 |
| E | 電商/新零售 Operations（11-200人） | 50 | P4 |
| G | Product/Engineering Manager（11-200人）| 70 | P2 |
