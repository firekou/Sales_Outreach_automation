# S1 外展排程 — 2026-06-15 啟動

**帳號:** Frank (25/day, 08:00–09:00)  
**總人數:** 15 leads（含完整 3 封信序列）  
**匯入檔案:** `s1-batch-20260613_0439-dripify-full.csv`  
**狀態:** 🟢 可立即匯入 Dripify 並啟動

---

## Dripify Campaign 設定

| 欄位 | 設定 |
|------|------|
| Campaign 名稱 | S1-Frank-20260615 |
| LinkedIn 帳號 | Frank (frank.kao) |
| 每日上限 | 25 connections/day |
| 連線邀請送出時間 | 08:00–09:00 |
| Step 1 | Connect（使用 custom1 文案） |
| Step 2 | Message，觸發條件：接受後 D+0 ～ D+1（使用 custom2） |
| Step 3 | Message，觸發條件：D+7 且無回覆（使用 custom3） |

---

## 今日發送排程（2026-06-15，15 封）

**發送優先序**（依 Heat×ICP 加權，同 Heat 依 ICP 排序）：

| # | 姓名 | 公司 | 職稱 | ICP | Heat | 類型 |
|---|------|------|------|-----|------|------|
| 1 | Allen Sun | 華擎 ASRock | Head of ASRock AI | 100 | 72 | D |
| 2 | Chi-Chung Chen | aetherAI 雲象科技 | Dir. Product & ML | 90 | 72 | D |
| 3 | Tzu-Hsuan Andrea Chuang | TGIA | Dir. Genomics PD | 90 | 72 | A |
| 4 | Chien-Ming Huang | Agaruda | Head of AI | 88 | 72 | D |
| 5 | Monica Hsueh | Speed 3D | Global Mktg Dir. | 88 | 72 | A |
| 6 | Victoria Hsu | PIDC | Adj. Instructor | 88 | 72 | A |
| 7 | Ken Chan | AIRA 城智科技 | CTO, VP | 100 | 62 | D |
| 8 | Joy Chan | TWNIC | Deputy CEO/CIO/CISO | 90 | 62 | D |
| 9 | Amanda Ye | ARBOR Technology | Dir. Global Mktg | 90 | 62 | D |
| 10 | Pei-Kang Hsieh | beBit TECH | Dir. of PM | 90 | 62 | D |
| 11 | Syuan Yu Chen | AI DataBrushing | Product Director | 90 | 62 | D |
| 12 | Fabien Petitgrand | ubiik | CTO | 88 | 62 | D |
| 13 | Stan Yu | Cardumen Capital | VP/Head of APAC | 88 | 62 | D |
| 14 | Clara Cheng | Flytech Technology | Assoc. Mktg Dir. | 80 | 62 | D |
| 15 | Rayvatek International | Rayvatek 睿智創新 | CTO | 90 | 42 | D |

---

## 序列時間軸

```
D+0  (今日 14:00)  →  連線邀請送出（custom1，≤200字）
D+1  ～ D+2        →  對方接受後自動發 Day 1 訊息（custom2，≤300字）
D+7               →  無回覆者自動發 Day 7 訊息（custom3，≤350字）
D+14              →  第三封（引入方案）— 待撰寫，下一批
```

---

## 後續行動佇列

### Phase 2 — 2026-06-16～17：AI-BizDev HOT 名單文案撰寫
- 42 HOT AI-BizDev 名單已匯入 Asana（HOT section）
- Combo J + Combo K 結果補入中（background job 執行中）
- 優先撰寫前 15 名（Jane Lin、Jim Chang、Cheng-Ho Wu 等）
- 完成後生成第二個 Dripify CSV，指派給 frank 帳號

### Phase 3 — 2026-06-18+：第二波發送
- AI-BizDev HOT 前 15 名（frank 帳號，08-09 時段）
- AI-BizDev HOT 第 16-30 名（frank 帳號補量）

---

## 監控指標（每週五 ALI-Auditor 稽核）

| 指標 | 目標 | 警示線 |
|------|------|--------|
| 連線接受率 | ≥35% | <20% |
| Day 1 回覆率 | ≥15% | <8% |
| Day 7 回覆率（追加） | ≥10% | <5% |
| 本週新連線數 | 15 | — |
| 本週回覆數 | ≥3 | 0 |

---

## Dripify 操作步驟

1. 登入 Frank 的 Dripify 帳號
2. 建立新 Campaign：`S1-Frank-20260615`
3. 匯入 CSV：`lead-drafts/s1-batch-20260613_0439-dripify-full.csv`
4. 設定 Step 1 — Connect：
   - Message template: `{{custom1}}`
5. 設定 Step 2 — Message（接受後 1 天）：
   - Message template: `{{custom2}}`
6. 設定 Step 3 — Message（D+7，無回覆）：
   - Message template: `{{custom3}}`
7. 設定每日發送量：25/day
8. 啟動時間：14:00–15:00
9. 按上方優先序排列 lead 順序後啟動 Campaign
