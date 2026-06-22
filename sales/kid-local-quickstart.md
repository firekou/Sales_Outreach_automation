# Kid 本機執行指引 — LinkedIn Lead 抓取 & 雲端處理

**對象：** Kid（業務銷售）  
**目的：** 第一次在本機跑完整抓取→評分→Asana 匯入的完整流程  
**前置條件：** 已訂閱 LinkedIn Sales Navigator（任意方案均可）

---

## 一次性設定（只需做一次）

### Step 1：安裝 Python 3.10+

```bash
# 確認版本（3.10 以上才支援 list[dict] 型別標注）
python3 --version

# 如果沒有，請至 https://www.python.org/downloads/ 下載安裝
# Windows 建議安裝時勾選「Add Python to PATH」
```

### Step 2：複製程式庫並安裝依賴

```bash
# 如果還沒 clone 過
git clone https://github.com/firekou/virtual-strategy-lab.git
cd virtual-strategy-lab/projects/aitokenking/sales/scripts

# 安裝 Python 套件（只需一次）
pip install -r requirements.txt
```

### Step 3：建立 .env 設定檔

在 `scripts/` 目錄下新建 `.env` 檔（不要 commit，已在 .gitignore）：

```bash
# scripts/ 目錄下執行
cp .env.example .env
```

然後用任意文字編輯器開啟 `.env`，填入三個值：

```
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx     ← 從 console.anthropic.com 取得
APIFY_TOKEN=apify_api_xxxxxxxx        ← 已有：apify_api_A4SkZ...
LINKEDIN_LI_AT=AQEFAQ8B...            ← 見 Step 4 說明
```

### Step 4：取得 LinkedIn li_at Cookie

**li_at 是你的 LinkedIn 登入憑證，每次執行都從瀏覽器取得最新值。**

1. 用 **Chrome** 開啟並登入 LinkedIn Sales Navigator
2. 按 **F12**（開發者工具）→ 點選 **Application** 分頁
3. 左側展開 **Cookies** → 點 `https://www.linkedin.com`
4. 在右側列表找 **`li_at`** 這一行
5. 複製 **Value** 欄的完整字串（很長，以 `AQEF` 開頭）
6. 貼到 `.env` 的 `LINKEDIN_LI_AT=` 後面（不需加引號）

> **注意**：li_at 約一年有效，但帳號重新登出後立即失效，請重取。

---

## 每週執行流程

### Step A：執行抓取腳本（本機）

```bash
cd virtual-strategy-lab/projects/aitokenking/sales/scripts

python apify_linkedin_scraper.py
```

**預期輸出（約 5-20 分鐘）：**

```
10:23:01 [INFO] ▶ 啟動 組合A：科技公司IT決策者 (預估上限 300 筆)
10:23:35 [INFO]   ✓ Actor 完成，runId=xyz，狀態=SUCCEEDED
10:23:36 [INFO]   ✓ 取回 247 筆原始資料
10:23:36 [INFO] ⏳ 間隔 30 秒，避免 LinkedIn 頻率限制...
...
============================================================
  AI Token King — Lead 抓取結果摘要
============================================================
  總 Lead 數（去重後）：498 筆
  HOT（≥70分）：62 筆  ← 本週優先觸達
  WARM（50-69分）：187 筆  ← 本月排程觸達
  COLD（<50分）：249 筆  ← 觀察池
  ...
  輸出檔案：leads_20260602_102543.csv
```

輸出的 CSV 在 `scripts/output/leads_YYYYMMDD_HHMMSS.csv`。

---

### Step B：雲端評分複核（把 CSV 上傳到 Claude Code）

在 Claude Code 對話視窗，貼上以下指令（替換日期）：

```
請用 linkedin_processor.py 對今天的 Lead 檔做 score 複核：
檔案路徑：projects/aitokenking/sales/scripts/output/leads_20260602_102543.csv
```

或直接把 CSV 內容貼進對話（若檔案 < 200 行建議直接貼）。

雲端會輸出：
- 重新排序後的 Lead 表（HOT 優先）
- 各組合分數分布
- 異常 Lead 標記（分數 ≠ 搜尋組合預期時）

---

### Step C：生成個人化訊息草稿

```bash
# 本機執行（需要 ANTHROPIC_API_KEY）
python linkedin_processor.py draft output/leads_20260602_102543.csv
```

**或** 在 Claude Code 對話請求（雲端處理）：

```
請對 leads_20260602_102543.csv 的 HOT Lead 生成個人化訊息草稿。
```

輸出：`output/drafts_20260602_102543.csv`

每筆包含：
- `connection_note`：LinkedIn 連結請求附言（≤300字元）
- `value_message`：第一封 InMail / DM 價值觸達訊息（≤500字）

---

### Step D：人工審核草稿（不跳過）

1. 開啟 `drafts_YYYYMMDD.csv`
2. 逐筆確認訊息是否自然、個人化（非模板感）
3. 修改不自然的地方
4. **只有 Kid 親自確認過才能發送** — 這是流程紅線

---

### Step E：匯入 Asana

```bash
# 生成 Asana 格式 CSV
python linkedin_processor.py asana output/leads_20260602_102543.csv
```

輸出：`output/asana_import_YYYYMMDD.csv`

匯入步驟：
1. Asana → 「AI Token King Lead Pool」專案
2. 右上角 ⋮ → **Import** → **CSV**
3. 選擇 `asana_import_YYYYMMDD.csv`
4. 欄位對應：`asana_task_name` → Task 名稱，其餘照預設
5. 完成後 Lead 自動進入 Section 01（待驗證）

---

## 回覆處理（即時，每天）

當 LinkedIn Inbox 收到回覆，用 `reply` 指令分析：

```bash
python linkedin_processor.py reply "感謝你的訊息，我們目前有在評估一些 AI 工具，可以多介紹嗎？"
```

**或在 Claude Code 貼上對方回覆文字請求分析。**

輸出：
- 真實意圖分類（HOT / WARM / 低質 / 禮貌性）
- 回覆品質評分（0-10）
- 建議下一步（跟進 / Demo 邀約 / 移至 NURTURE）
- 草稿回覆訊息

---

## 異常排查

| 錯誤訊息 | 原因 | 解法 |
|---------|------|------|
| `❌ 缺少 APIFY_TOKEN` | .env 未建立或 Key 名稱錯誤 | 確認 `.env` 在 `scripts/` 目錄下 |
| `❌ 缺少 LINKEDIN_LI_AT` | Cookie 未填 | 重新從 Chrome DevTools 取得 |
| `Actor 執行失敗：401` | Apify token 無效 | 登入 apify.com 確認 Token 狀態 |
| `Actor 執行失敗：LinkedIn 403` | li_at Cookie 過期 | 重新登入 LinkedIn，重取 li_at |
| `run 狀態 = FAILED` | Sales Navigator 搜尋 URL 失效 | 在 LinkedIn 手動開搜尋頁，重新複製 URL 給工程師更新 |
| `0 筆資料` | 搜尋條件太嚴或頻率觸發 | 等 24 小時後重試，或縮小 maxResults |

---

## 每週節奏

| 時間 | 動作 | 工具 |
|------|------|------|
| 週一 09:00 | 執行抓取（Step A-B） | 本機腳本 |
| 週一 10:00 | 審核草稿（Step D） | 手動 |
| 週二-四 | 每天依草稿發送（≤20 則連結邀請） | LinkedIn 手動 |
| 每天 | 處理 Inbox 回覆（reply 指令） | 本機 or Claude Code |
| 週五 17:00 | A-LI-Auditor 稽核報告 | 自動（由 ALI-Auditor Agent 產出） |

---

## 檔案位置快速參考

```
scripts/
├── .env                        ← 你的憑證（不 commit）
├── .env.example                ← 格式範例
├── apify_linkedin_scraper.py   ← 本機抓取腳本
├── linkedin_processor.py       ← 雲端處理引擎
├── requirements.txt            ← 依賴套件清單
└── output/                     ← 所有輸出（不 commit）
    ├── leads_YYYYMMDD.csv
    ├── drafts_YYYYMMDD.csv
    └── asana_import_YYYYMMDD.csv
```

---

**第一次執行遇到問題？** 在 Claude Code 貼上錯誤訊息，或直接告訴 Edwin，24 小時內提供解法。
