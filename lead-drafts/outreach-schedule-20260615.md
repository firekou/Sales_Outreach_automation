# S1 外展排程 — 2026-06-15 啟動（Expandi + Sales Navigator）

**帳號:** Frank (25/day, 08:00–09:00)  
**工具:** Expandi — Sales Navigator Campaign  
**總人數:** 15 leads（含完整 3 封信序列）  
**匯入檔案:** `s1-batch-20260615-expandi.csv`  
**狀態:** 🟢 可立即匯入 Expandi 並啟動

---

## Expandi Campaign 設定

| 欄位 | 設定 |
|------|------|
| Campaign 名稱 | S1-Frank-20260615 |
| Campaign 類型 | **Sales Navigator Campaign** |
| LinkedIn 帳號 | Frank (frank.kao) |
| 每日 Connection 上限 | 25/day |
| 發送時段 | 08:00–09:00 |
| 安全模式 | 開啟（Smart Limits） |

---

## Expandi Sequence 設定（Campaign Steps）

```
Step 1 — Visit Profile
  └─ 動作：先瀏覽對方 LinkedIn 頁面（提升接受率）
  └─ 等待：0 天

Step 2 — Connect
  └─ 動作：送出連線邀請
  └─ 訊息：{{custom1}}（已個人化，≤200字）
  └─ 等待：直到接受

Step 3 — Message（Day 1，接受後）
  └─ 觸發：連線接受後 1 天
  └─ 訊息：{{custom2}}（已個人化，≤300字）
  └─ 等待：7 天

Step 4 — Message（Day 7，無回覆追蹤）
  └─ 觸發：Day 1 訊息送出後 7 天，且無回覆
  └─ 訊息：{{custom3}}（已個人化，≤350字）
  └─ 結束 / 轉人工跟進
```

---

## Expandi 操作步驟

1. 登入 Expandi → 選擇 Frank 帳號
2. 建立新 Campaign → 類型選 **「Sales Navigator」**
3. **匯入 leads**：
   - 選「Import CSV」
   - 上傳 `lead-drafts/s1-batch-20260615-expandi.csv`
   - 欄位對應：
     - `LinkedIn Profile URL` → LinkedIn URL
     - `first_name` / `last_name` → 姓名
     - `custom1` → Custom Variable 1（連線邀請文案）
     - `custom2` → Custom Variable 2（Day 1 訊息）
     - `custom3` → Custom Variable 3（Day 7 訊息）
4. 建立 Sequence（依上方步驟設定）
5. 設定每日上限：25 connections
6. 設定發送時段：08:00–09:00（台北時間）
7. 啟動 Campaign

---

## 今日發送名單（15 封，依優先序）

| # | 姓名 | 公司 | 職稱 | ICP | Heat |
|---|------|------|------|-----|------|
| 1 | Allen Sun | 華擎 ASRock | Head of ASRock AI | 100 | 72 |
| 2 | Chi-Chung Chen | aetherAI 雲象科技 | Dir. Product & ML | 90 | 72 |
| 3 | Tzu-Hsuan Andrea Chuang | TGIA | Dir. Genomics PD | 90 | 72 |
| 4 | Chien-Ming Huang | Agaruda | Head of AI | 88 | 72 |
| 5 | Monica Hsueh | Speed 3D | Global Mktg Dir. | 88 | 72 |
| 6 | Victoria Hsu | PIDC | Adj. Instructor | 88 | 72 |
| 7 | Ken Chan | AIRA 城智科技 | CTO, VP | 100 | 62 |
| 8 | Joy Chan | TWNIC | Deputy CEO/CIO/CISO | 90 | 62 |
| 9 | Amanda Ye | ARBOR Technology | Dir. Global Mktg | 90 | 62 |
| 10 | Pei-Kang Hsieh | beBit TECH | Dir. of PM | 90 | 62 |
| 11 | Syuan Yu Chen | AI DataBrushing | Product Director | 90 | 62 |
| 12 | Fabien Petitgrand | ubiik | CTO | 88 | 62 |
| 13 | Stan Yu | Cardumen Capital | VP/Head of APAC | 88 | 62 |
| 14 | Clara Cheng | Flytech Technology | Assoc. Mktg Dir. | 80 | 62 |
| 15 | Rayvatek International | Rayvatek 睿智創新 | CTO | 90 | 42 |

---

## 序列時間軸

```
D+0  (今日 08:00)  →  Visit Profile + 連線邀請（custom1）
D+1 ~ D+3          →  接受後 Expandi 自動發 Day 1 訊息（custom2）
D+8 ~ D+10         →  無回覆者自動發 Day 7 追蹤（custom3）
D+14+              →  第三封引入方案 — 待撰寫
```

---

## 後續行動佇列

### Phase 2 — 2026-06-16～17：AI-BizDev HOT 名單文案撰寫
- 47 HOT AI-BizDev 名單已匯入 Asana（HOT section）
- 優先撰寫前 15 名（Jane Lin、Jim Chang、Cheng-Ho Wu 等）
- 完成後生成第二個 Expandi CSV，建立 Campaign `S1-Frank-AI-BizDev-01`

### Phase 3 — 2026-06-18+：第二波發送
- AI-BizDev HOT 前 25 名（frank 帳號，08-09 時段，25/day）

---

## 監控指標（每週五 ALI-Auditor 稽核）

| 指標 | 目標 | 警示線 |
|------|------|--------|
| 連線接受率 | ≥35% | <20% |
| Day 1 回覆率 | ≥15% | <8% |
| Day 7 回覆率（追加） | ≥10% | <5% |
| 本週新連線數 | 15 | — |
| 本週回覆數 | ≥3 | 0 |
