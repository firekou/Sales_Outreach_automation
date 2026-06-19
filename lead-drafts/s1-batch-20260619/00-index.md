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
| 04 | Yvonne C. | Chief Marketing Officer | hububble | 80 | C 影響力建構者 | MarTech 觀點產出與傳播放大 |
| 05 | Vanessa Chou | Director of Strategic Planning | MAKALOT 聚陽實業 | 80 | D 組織決策者 | 集團 AI 投資決策框架＋ROI |

**類型分布：** D ×3、B ×1、C ×1。本批為 Director 級、Frank 人設適配。
**Type A 缺口：** HOT 池無清楚 Type A 訊號，已在同日 WARM 補批
（`../s1-batch-20260619-warm/`）補上 2 筆 Type A，完整覆蓋 A/B/C/D。

### ⚠ 去重攔截紀錄（Director 判斷）
初稿原含 **Monica Hsueh（Speed 3D，85）** 與 **Amanda Ye（ARBOR，80）**，
經 `dedup_local_check.py` 比對發現兩人已在 **0613／0615 批次**接觸過
（出現在 `s1-batch-20260615-expandi.csv` 等），依「去重優先、避免重複觸及」原則**剔除**，
改換未接觸的 **Yvonne C.（hububble，C 型）** 與 **Vanessa Chou（聚陽，D 型）**。
→ 體現 Skill 的「人在迴路＋去重」：高分 ≠ 可發，必須過去重關。

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
