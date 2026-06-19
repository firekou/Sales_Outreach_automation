# S1 直攻法 — 2026-06-19 批次索引

**策略：** S1 直攻法（主動搜尋 ICP → 深度個人化切入）
**發送帳號：** Frank Kao（CEO, AI Token King ／ 兌心科技）— 高層對高層
**工具：** Expandi — Sales Navigator Campaign
**名單來源：** `scripts/output/leads_v2_20260603.csv`（既有抓取結果，本批從 35 筆 HOT 中精選）
**匯入檔：** `s1-batch-20260619-expandi.csv`
**排程：** `../outreach-schedule-20260619.md`
**狀態：** 🟡 草稿完成、長度自檢通過，**待人工審核核准後**匯入 Expandi（pending_review）

> 透過 `.claude/skills/s1-director-direct-outreach` Skill 執行。
> Phase 1 因本環境無 `APIFY_TOKEN`/金鑰，未做 live 抓取，改用既有抓取名單為輸入；
> Phase 2–5（分析 / 文案 / CSV / 排程）由 S1 Director 完整產出。

---

## 本批 Lead 清單（5 筆，品質>數量）

| # | 姓名 | 職稱 | 公司 | ICP | AI 類型 | 切入角色 |
|---|------|------|------|-----|---------|---------|
| 01 | Ella Hung | Director of Digital Marketing | ACES Group 宏致集團 | 83 | D 組織決策者 | 讓 AI 轉型對董事會說得出 ROI |
| 02 | YuYu Chen | Head of IT | Koo Foundation 和信治癌中心 | 80 | D（強 B 風險趨避） | 醫療場域 AI 風險把關＋可稽核 |
| 03 | James Wu | Director of Technology & Innovation | InterContinental Kaohsiung | 80 | B 效率優化者 | 飯店多部門 AI 用法一致、可追蹤 |
| 04 | Monica Hsueh | Global Marketing Director | Speed 3D Inc. | 85 | C 影響力建構者 | 領先 AI 實踐→可展示資產 |
| 05 | Amanda Ye | Director, Global Marketing | ARBOR Technology | 80 | D 組織決策者 | 跨國行銷 AI 一致化、可衡量 |

**類型分布：** D ×3、B ×1、C ×1。本批為 Director 級、Frank 人設適配。
**缺口（誠實標註）：** HOT 池中無清楚的 Type A（身份建構者／明顯職涯轉型）訊號，故本批未含 A 型；
下批可從 WARM 池（56 筆）補上轉型背景者以平衡話術組合。

---

## Phase 1 選樣與排除（Director 判斷）

從 35 筆 HOT 中，**刻意排除**了數筆「本身就是 AI 供應商」的高分 Lead，避免把直攻買方話術
用錯對象（應走合作/通路而非 S1 直攻）：

| 排除對象 | 分數 | 原因 | 建議改走 |
|---------|------|------|---------|
| Cheng-Ho (C.H.) Wu @ cacaFly（Head of Cloud & AI Business） | 95 | 本身做 AI 顧問/實作，是同業而非買方 | 合作/生態夥伴洽談 |
| Chi-Chung Chen @ aetherAI（Director of Product & ML） | 85 | 醫療 AI 產品公司核心，AI 自造方 | 合作/技術交流 |

> 這體現 Skill 的「品質 > 數量」與「誠實回報」準則：分數高 ≠ 適合 S1 直攻。

---

## Expandi Campaign 欄位對應

| Expandi Custom | 內容 | 序列步驟 |
|----------------|------|---------|
| `custom_variable_1` | 連線邀請（148–157 字，已個人化） | Step 2 Connect |
| `custom_variable_2` | 第一封 Day 1（`[P]` 分段） | Step 3 Message（接受後 Day 1） |
| `custom_variable_3` | 第二封 無回覆追蹤版（`[P]` 分段） | Step 4 Message（Day 7 無回覆） |

**第二封「有回覆版」與第三封「引入方案」不放 CSV** —— 依對方回覆內容人工判斷後發送
（見各 lead-0X md）。這是 Skill 規定的「人在迴路」。

---

## Asana CRM 追蹤（建立任務）

每筆建立一張 Task（Project：LinkedIn 開發 — 2026-06）：

- **任務名稱：** `[姓名] @ [公司] — S1`
- **負責人：** Frank
- **自訂欄位：** Heat/ICP Score、AI 使用者類型、策略來源=S1、聯絡階段=`連線未發`、執行環境=`地端 Expandi`
- **描述：** 帶入該 lead 的【分析】+ 三封信草稿
- **去重：** 匯入前先 `python asana_dedup.py check`（本批 linkedin_url 對既有名單比對）

階段流轉：`連線未發 → 等待接受 → 第一封 → 第二封 → 第三封 → 進入 Demo`

---

## 檔案清單

| 檔案 | 說明 |
|------|------|
| `build_batch.py` | 批次產生器（單一真實來源；回查名單真實欄位 + 手寫文案 → MD + CSV） |
| `lead-01-ella-hung.md` … `lead-05-amanda-ye.md` | 5 筆完整分析 + 三封信序列 |
| `s1-batch-20260619-expandi.csv` | Expandi 匯入檔（custom_variable_1/2/3） |
| `../outreach-schedule-20260619.md` | 發送排程與配額設定 |
