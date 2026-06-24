# S1 直攻法 — 2026-06-19 WARM 補批索引

**策略：** S1 直攻法 ｜ **發送帳號：** Frank（CEO, AI Token King）— 高層對高層
**工具：** Expandi — Sales Navigator Campaign
**名單來源：** `scripts/output/leads_v2_20260603.csv`（56 筆 WARM 中精選）
**匯入檔：** `s1-batch-20260619-warm-expandi.csv`
**目的：** 補上 HOT 批缺少的 **Type A（身份建構者）**，讓本日整體話術完整覆蓋 A/B/C/D。
**狀態：** 🟡 草稿完成、長度自檢通過、去重通過，**待人工審核核准**（pending_review）

---

## 本批 Lead 清單（5 筆，刻意覆蓋 A/A/B/C/D）

| # | 姓名 | 職稱 | 公司 | ICP | AI 類型 | 切入角色 |
|---|------|------|------|-----|---------|---------|
| 01 | Tina Yi Ching Chen | Marketing Director | E.C.I. Elastic（紡織織帶） | 78 | **A 身份建構者** | 傳統製造業數位先行者→可展示成果 |
| 02 | Jerry Chen, Ph.D. | Marketing Associate Director | HanchorBio（生技腫瘤） | 78 | **A 身份建構者** | 科學×商業複合身份＋合規 AI 裝備 |
| 03 | Ling Cheng | Marketing Director | VicOne（車用資安） | 78 | B 效率優化者 | 跨部門 AI 行銷成果可追蹤、可交代 |
| 04 | Jimmy Lo | Head of Marketing, Director | RECCESSARY（ESG 媒體） | 78 | C 影響力建構者 | GenAI 實踐→ESG 領域影響力資產 |
| 05 | Liz Chen | Sr. Managing Director, Mktg & BD | Terasic（FPGA/Edge AI） | 78 | D 組織決策者 | 事業線 AI 決策框架＋ROI |

**類型分布：** A ×2、B ×1、C ×1、D ×1 —— 與 HOT 批合計：A ×2、B ×2、C ×2、D ×4。

---

## 為什麼補 Type A

HOT 池（35 筆）的訊號偏向決策者與效率/影響力型，缺少「明顯職涯轉型／在傳統產業重新定義
自己」的 Type A。WARM 池中找到兩個強訊號：

- **Tina（E.C.I. 紡織）**：在製造為本的傳統產業推 SEO/AEO 與供應鏈數位創新 → 典型
  「成為舊行業裡最懂新科技的人」。
- **Jerry（HanchorBio 生技）**：科學博士轉藥廠商業/行銷，正在建立「懂科學又懂商業」的稀缺身份。

Type A 話術核心＝**身份升級＋時間壓力**（見 `references/copywriting-playbook.md`），
與 D/B/C 的框架明顯不同，補上後本日話術組合完整。

---

## Expandi 欄位對應（同 HOT 批）

| Custom | 內容 | 序列步驟 |
|--------|------|---------|
| `custom_variable_1` | 連線邀請（已個人化） | Step 2 Connect |
| `custom_variable_2` | 第一封 Day 1（`[P]` 分段） | Step 3 Message |
| `custom_variable_3` | 第二封 無回覆追蹤版 | Step 4 Message（Day 7 無回覆） |

第二封有回覆版、第三封引入方案 → 依回覆**人工**發送（見各 `lead-0X-*.md`）。

---

## 檔案清單

| 檔案 | 說明 |
|------|------|
| `build_batch.py` | 批次產生器（回查名單真實欄位＋手寫文案 → MD + CSV） |
| `lead-01-tina-chen.md` … `lead-05-liz-chen.md` | 5 筆完整分析＋三封信序列 |
| `s1-batch-20260619-warm-expandi.csv` | Expandi 匯入檔 |
| 排程 | 與 HOT 批共用 `../outreach-schedule-20260619.md`（合計 10 筆，遠低於 25/day） |
