# Phase 1 參考 — ICP 定義、搜尋組合、評分公式

來源整合自 `strategies/01-S1-direct-outreach.md`、`scripts/HOWTO.md`、
`strategies/07-orchestrator-spec.md`。此處為 S1 直攻法「建名單」階段的可執行濃縮版。

---

## 1. ICP 篩選條件

**職稱關鍵字（決策者）**
- 執行長 / CEO / 創辦人 / Co-founder
- 業務總監 / Sales Director / VP of Sales
- 行銷總監 / Marketing Director
- 營運長 / COO / 總經理
- IT 主管 / CTO / VP of Engineering / 數位轉型負責人

**公司規模**：10–500 人；甜蜜區間 **11–200 人**（中小企業決策者有明確採購權，又夠大到有預算）。

**產業優先序**
1. 科技 / SaaS / 數位服務
2. 顧問 / 培訓 / 教育
3. 電商 / 零售 / 品牌
4. 金融服務 / 保險

**活躍度**：近 30 天在 LinkedIn 有發文/互動者優先（有得研究、接受率高）。

---

## 2. 搜尋組合（Apify Sales Navigator Scraper）

Actor：`bestscrapers/sales-navigator-scraper-by-filters`；台灣 GEO：`104187078`。

| 組合 | 目標族群 | 上限 | 優先 |
|------|---------|------|------|
| A | 科技公司 IT 決策者（11–200 人） | 80 | P1 |
| B | 行銷代理商高層（11–200 人） | 60 | P2 |
| C | 數位轉型顧問 / CDO（11–200 人） | 60 | P3 |
| D | SaaS / 軟體新創 CTO/VP（11–200 人） | 80 | P1 |
| E | 電商 / 新零售 Operations（11–200 人） | 50 | P4 |
| G | Product / Engineering Manager（11–200 人） | 70 | P2 |

執行：`python apify_linkedin_scraper.py --account <frank|jet|alice|kid|lauren>`
（多帳號各有 icp_focus 偏好，例如 frank 偏 CxO/Founder/總經理）。

---

## 3. ICP 評分（5 維度，對齊 linkedin_processor.py）

```
總分 = 職稱決策力(30) + 公司規模(15) + 產業匹配(20) + 活躍度(15) + AI 痛點訊號(20)
```

| 分類 | 分數 | 行動 |
|------|------|------|
| HOT  | ≥ 70 | 同日生成草稿，審核後發送 |
| WARM | 50–69 | 次日批次，審核後發送 |
| COLD | < 50 | 培育池，每月觸達 |

重新評分：`python linkedin_processor.py score output/leads_*.csv`

---

## 4. Heat Score（多策略去重後的執行優先序）

當 Lead 可能被 S1/S2/S5/S6 多套策略同時識別時，由 Orchestrator 在去重後計算 Heat Score
決定當日執行優先序（S1 為冷觸達，單靠 S1 的 Lead 熱度通常較低）：

| 條件 | 加分 |
|------|------|
| 來自兩套以上策略同時識別 | +30 |
| AI 使用者類型為 D（組織決策者） | +15 |
| AI 使用者類型為 B（效率優化者） | +10 |
| S1：目標最近 30 天有發文（活躍） | +10 |
| 公司規模 50–200 人 | +10 |
| 職稱 CEO / 創辦人 / 執行長 | +10 |

| Heat Score | 優先級 | 當日行動 |
|-----------|--------|---------|
| ≥ 70 | A 級 | 今日地端 Dripify/Expandi 執行 |
| 40–69 | B 級 | 本週執行 |
| < 40 | C 級 | 觀察池 |

---

## 5. 去重（保護品牌與帳號）

```bash
python asana_dedup.py check  output/leads_*.csv     # 比對 Asana，標記重複
python asana_dedup.py stats                          # 去重統計
python asana_dedup.py lookup "https://linkedin.com/in/someone"
```

規則：若 `linkedin_url` 已存在於 Asana → 不新增 Task，只更新 heat_score 與 source_strategy，
並加一則 Comment。同一目標 7 天內被觸達過 → 自動跳過。
