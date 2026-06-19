# S1 外展排程 — 2026-06-19 批次（Expandi + Sales Navigator）

**帳號：** Frank（frank.kao）｜25/day｜08:00–09:00 台灣時間
**工具：** Expandi — Sales Navigator Campaign
**總人數：** 10 leads（HOT 批 5 + WARM 補批 5，含完整三封信序列）
**匯入檔：**
- `s1-batch-20260619/s1-batch-20260619-expandi.csv`（HOT 5）
- `s1-batch-20260619-warm/s1-batch-20260619-warm-expandi.csv`（WARM 補批 5，補 Type A）
**去重：** 已過 `dedup_local_check.py`（10 筆全新，HOT 批已剔除 2 筆重複者並替換）
**狀態：** 🟡 待人工審核核准後可匯入啟動（pending_review）

---

## Expandi Campaign 設定

| 欄位 | 設定 |
|------|------|
| Campaign 名稱 | S1-Frank-20260619（HOT）／ S1-Frank-20260619-WARM（補批） |
| Campaign 類型 | **Sales Navigator Campaign** |
| LinkedIn 帳號 | Frank（frank.kao） |
| 每日 Connection 上限 | 25/day（本日共 10 筆，遠低於上限，安全） |
| 發送時段 | 08:00–09:00 |
| 安全模式 | 開啟（Smart Limits） |
| 操作間隔 | 隨機 3–15 秒（用預設，勿改短） |

---

## Sequence 設定（Campaign Steps）

```
Step 1 — Visit Profile
  └─ 先瀏覽對方頁面提升接受率｜等待 0 天
Step 2 — Connect
  └─ 訊息：{{custom_variable_1}}（連線邀請，已個人化，148–157 字）
  └─ 等待：直到接受
Step 3 — Message（Day 1，接受後）
  └─ 觸發：連線接受後 1 天
  └─ 訊息：{{custom_variable_2}}（第一封 Day 1）
  └─ 等待：7 天
Step 4 — Message（Day 7，無回覆追蹤）
  └─ 觸發：Day 1 訊息送出後 7 天且無回覆
  └─ 訊息：{{custom_variable_3}}（第二封 無回覆追蹤版）
  └─ 結束 → 轉人工跟進
```

> **第二封「有回覆版」與第三封「引入方案 Day 8-12」不進 Expandi 自動序列**，
> 一律由 Frank 依對方實際回覆內容人工判斷後發送（內容見各 `lead-0X-*.md`）。

---

## 匯入步驟

1. 登入 Expandi → 選 Frank 帳號
2. 新 Campaign → 類型選 **Sales Navigator**
3. Import CSV → 上傳 `s1-batch-20260619/s1-batch-20260619-expandi.csv`
4. 欄位對應：
   - `linkedin` → LinkedIn Profile URL
   - `first_name` / `last_name` → 姓名
   - `custom_variable_1/2/3` → Custom Variable 1/2/3
5. 設定 Steps（如上）→ 啟動

---

## 七天節奏（單筆 Lead 視角）

| 日 | 動作 | 內容 |
|----|------|------|
| Day 0 | Visit + Connect | custom_variable_1 連線邀請 |
| Day 1（接受後） | 第一封私訊 | custom_variable_2 |
| Day 5–7（有回覆） | **人工** 第二封有回覆版 | 複述其觀點 + 給低門檻資訊 |
| Day 7（無回覆） | 自動第二封追蹤 | custom_variable_3 |
| Day 8–12 | **人工** 第三封引入方案 | 邀 20 分鐘實機操作 |
| Day 21 無回應 | 最後一封 + 優雅出口 | 人工 |
| Day 60 無回應 | 移入 Nurture 池 | 等新訊號 |

---

## 發送前檢查清單（核准門檻）

- [ ] 5 筆 linkedin_url 經 `asana_dedup.py check` 確認未被任何帳號接觸過
- [ ] 每封信通過「三自問」（不是賣東西也會發 / 講他的事 / 不買也有價值）
- [ ] 連線邀請含具體個人化鉤子、無禁字（介紹/產品/合作機會/方案）
- [ ] Asana 已為 5 筆建立 Task，聯絡階段=連線未發
- [ ] Frank 核准 → 由 pending_review 轉 approved → 匯入 Expandi 啟動

---

## KPI 追蹤（本批，對齊 S1 目標）

| 指標 | 目標 | 本批基數 |
|------|------|---------|
| 連線接受率 | ≥30%（深做可達 55%） | 5 |
| 第一封回覆率 | ≥15% | 視接受數 |
| 第三封轉 Demo | ≥25% | 視對話數 |

> 結果回填 Asana；每週交 `ALI-Auditor` 做漏斗真實性稽核，淘汰低效話術版本。
