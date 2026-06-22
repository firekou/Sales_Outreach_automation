# Make 自動化流程規格書

**版本：** 1.0
**日期：** 2026-06-13
**Owner：** IC Tommy（AI 系統工程師）
**狀態：** 待實作

---

## 總覽

本文件定義 AirTalk LinkedIn 開發流程中，Make.com 負責串接的三條自動化流程：

| Flow | 名稱 | 觸發方式 | 核心目的 |
|------|------|---------|----------|
| Flow 1 | Dripify → Asana 狀態同步 | Dripify Webhook（連線接受） | 自動將 LinkedIn 連線狀態更新至 Asana 任務 |
| Flow 2 | 有回覆偵測 → Claude API → Kid 通知 | Dripify Webhook（收到回覆） | 自動分析潛在客戶回覆、生成草稿、通知 Kid 接球 |
| Flow 3 | 每週新名單批次分析 | 排程（每週一 09:00 台灣時間） | 自動抓取 Sales Navigator 名單、ICP 評分、生成 S1 訊息 |

---

## Flow 1：Dripify → Asana 狀態同步

### 觸發條件

- **模組：** Dripify Webhook
- **事件類型：** `connection_accepted`
- **說明：** 當對方接受 LinkedIn 連線邀請時觸發

### 流程步驟

```
[Dripify Webhook] → [Parse Webhook] → [Asana Search Tasks] → [Asana Update Task] → [Log to Google Sheet（選用）]
```

**Step 1：Parse Webhook**

從 Dripify 的 payload 中萃取以下欄位：

| 欄位 | Dripify payload 路徑 | 說明 |
|------|---------------------|------|
| `linkedin_url` | `lead.profileUrl` | 作為 Asana 任務的主鍵查詢條件 |
| `name` | `lead.firstName` + `lead.lastName` | 潛在客戶全名 |
| `timestamp` | `event.createdAt` | 事件發生時間（ISO 8601） |
| `title` | `lead.occupation` | 職稱（供新建任務使用） |
| `company` | `lead.companyName` | 公司名稱（供新建任務使用） |

**Step 2：Asana Search Tasks**

- **模組：** Asana → Search Tasks
- **搜尋條件：**
  - Project GID: `1205513725053633`
  - Notes contains: `{linkedin_url}`
- **目的：** 找到該潛在客戶對應的 Asana 任務

**Step 3：Asana Update Task**

- **模組：** Asana → Update Task
- **條件：** Step 2 找到任務（有結果）
- **更新內容：**
  - 在 notes 中將狀態行更新為：
    ```
    狀態: 連線已接受 / Kid / {YYYY-MM-DD}
    ```
  - 保留 notes 中其餘欄位不動

**Step 4（選用）：Log to Google Sheet**

- **模組：** Google Sheets → Add Row
- **目標試算表：** AirTalk LinkedIn 開發日誌
- **欄位：** 時間戳、姓名、公司、LinkedIn URL、事件類型、Asana 任務 GID

### 錯誤處理：Asana 找不到任務

若 Step 2 找不到對應任務，執行以下備援流程：

1. **Asana Create Task**
   - 任務名稱：`[未分類] {name} | {title}`
   - Notes：`LinkedIn URL: {linkedin_url}\n公司: {company}\n狀態: 連線已接受 / Kid / {YYYY-MM-DD}\n備註: 自動建立（Webhook 觸發，原任務未找到）`
   - 專案：`1205513725053633`
2. **Send Alert Email**
   - 收件人：`kid@aitokenking.com.tw`
   - 主旨：`[AirTalk] 新連線接受，找不到原任務：{name}`

### Module 設定摘要

| 模組 | 關鍵設定 |
|------|----------|
| Dripify Webhook | Campaign event type = `connection_accepted` |
| Asana Search | Filter: project GID + notes contains LinkedIn URL |
| Asana Update | 僅更新狀態行，保留其餘 notes 內容 |
| Error route | 建立新任務 + 發送告警 email |

---

## Flow 2：有回覆偵測 → Claude API → Kid 通知

### 觸發條件

- **模組：** Dripify Webhook
- **事件類型：** `message_received`
- **說明：** 當潛在客戶在 LinkedIn 回覆任何訊息時觸發

### 流程步驟

```
[Dripify Webhook]
  → [Parse Webhook]
  → [Asana Search Tasks]
  → [Extract Lead Context from Asana Notes]
  → [HTTP Module → Claude API]
  → [Parse Claude Response]
  → [Asana Update Task]
  → [Send Notification to Kid]
```

**Step 1：Parse Webhook**

| 欄位 | Payload 路徑 | 說明 |
|------|-------------|------|
| `linkedin_url` | `lead.profileUrl` | 查詢 Asana 任務的主鍵 |
| `reply_content` | `message.text` | 對方回覆的完整訊息內容 |
| `sender_name` | `lead.firstName` + `lead.lastName` | 回覆者姓名 |
| `timestamp` | `event.createdAt` | 回覆時間 |

**Step 2：Asana Search Tasks**

同 Flow 1 Step 2，以 `linkedin_url` 查詢專案 `1205513725053633` 中的任務

**Step 3：Extract Lead Context from Asana Task Notes**

從 Asana 任務的 notes 欄位，以正則表達式萃取以下資訊：

```
ai_type              → 正則: /AI類型:\s*(.+)/
personalization_hook → 正則: /個人化鉤子:\s*(.+)/
development_logic    → 正則: /開發邏輯:\s*(.+)/
title                → 正則: /職稱:\s*(.+)/
company              → 正則: /公司:\s*(.+)/
```

**Step 4：HTTP Module → Claude API**

- **Endpoint：** `https://api.anthropic.com/v1/messages`
- **Method：** POST
- **Headers：**
  ```
  x-api-key: {{ANTHROPIC_API_KEY}}
  anthropic-version: 2023-06-01
  content-type: application/json
  ```
- **Body：** 見 `08-claude-api-prompt-templates.md` 模板一
- **model：** `claude-sonnet-4-6`
- **max_tokens：** 600
- **temperature：** 0.7

**Step 5：Parse Claude Response**

```
Make JSON path: body.content[1].text
（Make 陣列索引從 1 開始）
```

**Step 6：Asana Update Task**

- 狀態行 → `有回覆-待接球 / Kid / {YYYY-MM-DD}`
- Append 至 notes 尾端：
  ```
  ---
  [{YYYY-MM-DD HH:MM}] 回覆摘要: {reply_content 前 80 字}
  草稿訊息:
  {claude_output}
  ```

**Step 7：Send Notification to Kid**

- **方式 A（Email）：**
  - 收件人：`kid@aitokenking.com.tw`
  - 主旨：`[接球] {sender_name} 回覆了！`
  - 內容：回覆原文 + Claude 草稿 + Asana 任務連結

- **方式 B（Line Notify）：**
  - Token: `{{LINE_NOTIFY_TOKEN}}`
  - 訊息：`[接球] {sender_name} 回覆了！\n公司: {company}\n回覆: {前50字}...\n草稿已存入 Asana 任務。`

### 錯誤處理

| 錯誤情境 | 處理方式 |
|---------|----------|
| Asana 找不到任務 | 建立佔位任務 + 告警 Email 給 Kid |
| Claude API 呼叫失敗 | 跳過草稿生成，仍更新 Asana 狀態，傳原始回覆給 Kid，標注「（草稿生成失敗，請手動回覆）」 |
| Dripify payload 缺少 reply_content | 預設值為「（訊息內容為空）」，繼續流程 |

---

## Flow 3：每週新名單批次分析

### 觸發條件

- **模組：** Make Scheduler
- **排程：** 每週一 09:00（Asia/Taipei 時區，UTC+8）

### 流程步驟

```
[Scheduler]
  → [Apify Actor Run × 4 combos]
  → [Poll for Completion]
  → [Fetch Apify Results]
  → [Google Sheets: Append Raw Profiles]
  → [Filter & ICP Scoring]
  → [Take Top 15 ICP ≥ 45]
  → [Claude API: Full S1 Analysis × 15]
  → [Build CSV]
  → [Google Drive: Upload CSV]
  → [Email to Kid]
  → [Asana: Batch Create Tasks]
```

**Step 1：Apify Actor Run（× 4 Combos）**

- **Actor：** `bestscrapers/sales-navigator-scraper-by-filters`
- **四組搜尋條件：**

  | Combo | 關鍵字 | 地區 | 職級 | 公司規模 |
  |-------|--------|------|------|----------|
  | C1 | AI, Machine Learning | 台灣（GEO 104187078） | CTO, VP Engineering | 51-500 人 |
  | C2 | Digital Transformation | 台灣 | Director, Head of | 51-500 人 |
  | C3 | Data, Analytics | 台灣 | Chief Data Officer, Director | 51-200 人 |
  | C4 | Product, Innovation | 台灣 | CPO, Product Director | 51-500 人 |

- **API：** `POST https://api.apify.com/v2/acts/bestscrapers~sales-navigator-scraper-by-filters/runs`
- **Headers：** `Authorization: Bearer {{APIFY_TOKEN}}`

**Step 2：Poll for Completion（輪詢）**

- 每 5 分鐘查詢 Run 狀態，最多等待 30 分鐘
- 完成條件：`status === "SUCCEEDED"`

**Step 3：Fetch Apify Results**

- `GET https://api.apify.com/v2/actor-runs/{runId}/dataset/items?token={{APIFY_TOKEN}}&format=json`
- 合併四組結果，去除重複 LinkedIn URL

**Step 4：Google Sheets — Append Raw Profiles**

- 試算表：AirTalk Raw Profiles
- 欄位：抓取時間、姓名、職稱、公司、LinkedIn URL、地區、公司規模、Combo 來源

**Step 5：Filter & ICP Scoring**

| 條件 | 加分 |
|------|------|
| 地區 = 台灣（必要條件） | 不符合直接排除 |
| 職稱含 CTO / VP / Director / Head / Chief | +30 |
| 公司規模 51-200 人 | +25 |
| 公司規模 201-500 人 | +20 |
| 職稱含 AI / Data / Digital | +20 |
| 職稱含 Product / Innovation | +15 |
| 有 LinkedIn Premium 標記 | +10 |
| 近 90 天有貼文活動 | +15 |

**Step 6：Take Top 15（ICP ≥ 45）**

依 ICP 分數降序取前 15 名，不足 15 人則取所有 ≥ 45 者

**Step 7：Claude API — Full S1 Analysis（× 15 leads）**

使用 Make Iterator 對每位 Lead 呼叫一次 Claude API（見 `08-claude-api-prompt-templates.md` Flow 3 模板），萃取：`ai_type`、`personalization_hook`、`connection_request`、`msg1_day1`

**Step 8：Build CSV in Make**

```
firstname,lastname,occupation,companyName,linkedinUrl,custom1,custom2
{firstName},{lastName},{title},{company},{linkedinUrl},{connection_request},{msg1_day1}
```

**Step 9：Google Drive — Upload CSV**

- 資料夾：AirTalk / S1 週批次名單
- 檔名：`s1-leads-{YYYY-MM-DD}.csv`

**Step 10：Email to Kid**

- 主旨：`[AirTalk] 本週 S1 名單已就緒 — {YYYY-MM-DD}`
- 附 Google Drive 下載連結 + 前五名 ICP 預覽

**Step 11：Asana — Batch Create Tasks**

- 使用 Make Iterator + Asana Create Task 逐筆建立
- 任務格式：`{name} | {title} | {company}`
- 截止日：建立日 + 7 天

### 錯誤處理

| 錯誤情境 | 處理方式 |
|---------|----------|
| Apify 返回 0 筆結果 | 立即中止 + 告警 Email 至 `frank.kao@insight-software.com` |
| Apify 逾時（>30 分鐘） | 中止並告警，標注需手動重跑 |
| ICP ≥ 45 名單不足 5 人 | 繼續但 Email 標注「本週名單品質偏低，建議檢查搜尋條件」 |
| Claude API 部分失敗 | 記錄失敗 Lead，繼續其餘，最終 Email 附失敗清單 |

---

## 環境變數設定

| 變數名稱 | 說明 | 取得方式 |
|---------|------|----------|
| `APIFY_TOKEN` | Apify API 金鑰 | Apify Console → Settings → Integrations |
| `ANTHROPIC_API_KEY` | Claude API 金鑰 | Anthropic Console → API Keys |
| `ASANA_API_TOKEN` | Asana Personal Access Token | Asana → My Profile Settings → Apps → Personal Access Tokens |
| `ASANA_PROJECT_GID` | 固定值：`1205513725053633` | Asana 專案 URL 末段 |
| `DRIPIFY_WEBHOOK_SECRET` | Dripify Webhook 驗證簽名 | Dripify → Settings → Integrations → Webhooks |
| `LINE_NOTIFY_TOKEN` | Line Notify 推播 Token | Line Notify 官網 → 個人頁面 → 發行存取權杖 |
| `GOOGLE_SHEET_ID` | 日誌試算表 ID | Google Sheets URL 中段 |
| `GOOGLE_DRIVE_FOLDER_ID` | CSV 上傳目標資料夾 ID | Google Drive 資料夾 URL 末段 |

---

## Dripify Webhook 設定方式

1. 登入 Dripify → 右上角頭像 → **Settings**
2. 左側選單 → **Integrations** → **Webhooks** → **Add Webhook**
3. 貼入 Make Scenario 的 Dripify Webhook 模組 URL
4. 勾選事件：`connection_accepted`（Flow 1）、`message_received`（Flow 2）
5. Secret 欄位填入 `DRIPIFY_WEBHOOK_SECRET`
6. 點 **Save** 並用 **Send Test** 驗證

### Webhook Payload 格式（參考）

**connection_accepted：**
```json
{
  "event": { "type": "connection_accepted", "createdAt": "2026-06-13T09:00:00Z" },
  "lead": { "firstName": "Ken", "lastName": "Chan", "occupation": "CTO", "companyName": "AIRA 城智科技", "profileUrl": "https://www.linkedin.com/in/kenchan-example" },
  "campaign": { "id": "campaign_id", "name": "AirTalk S1 2026-W24" }
}
```

**message_received：**
```json
{
  "event": { "type": "message_received", "createdAt": "2026-06-13T10:30:00Z" },
  "lead": { "firstName": "Ken", "lastName": "Chan", "occupation": "CTO", "companyName": "AIRA 城智科技", "profileUrl": "https://www.linkedin.com/in/kenchan-example" },
  "message": { "text": "謝謝你的連線！你們在 AI 應用這塊有什麼新的進展嗎？", "direction": "inbound" }
}
```

---

## 錯誤處理與監控

- **全局錯誤 Email：** `frank.kao@insight-software.com`
- **Make log 保留：** 30 天
- **Incomplete executions：** 開啟自動重試（最多 3 次，間隔 10 分鐘）
- **Flow 2 異常監控：** 單日觸發超過 10 次視為異常，發送告警
- **Claude API 月度用量：** 每月第一週由 IC Tommy 盤點，確認未超過預算上限

---

*文件版本：1.0 | 最後更新：2026-06-13 | Owner：IC Tommy*
