# 發送前就緒清單 — 2026-06-19 批次（S1 直攻法）

本檔說明這批名單「正式發送」前還需要什麼。分成：**已自動完成**、**需要金鑰/環境**、
**需要人工決定**三類，避免把「草稿完成」誤當成「已發送」。

---

## A. 已自動完成（本環境內可做的，已做）

- ✅ Phase 1 選樣：從既有抓取名單篩 HOT/WARM，排除 2 筆 AI 供應商（非買方）
- ✅ Phase 2 分析：10 筆完成 AI 使用者類型 + 痛點 + 切入角色（覆蓋 A/B/C/D）
- ✅ Phase 3 文案：連線邀請 + 三封信序列，長度自檢全數通過
- ✅ Phase 4 CSV：兩支 Expandi 匯入檔（custom_variable_1/2/3）
- ✅ 離線去重：`python lead-drafts/dedup_local_check.py <csv...>` → 10 筆全新
  （已攔截並替換 Monica、Amanda 兩筆先前已接觸者）

---

## B. 需要金鑰 / 環境（本雲端環境沒有，須在 Frank 本機或 CI 設定）

| 項目 | 指令 / 動作 | 需要 |
|------|------------|------|
| live 抓取（如要重抓最新名單） | `python scripts/apify_linkedin_scraper.py --account frank` | `APIFY_TOKEN`、`LINKEDIN_LI_AT` |
| 腳本自動生成草稿（本批已手工等效產出，可選） | `python scripts/linkedin_processor.py draft ...` | `ANTHROPIC_API_KEY` |
| **線上 Asana 去重（發送前必做）** | `python scripts/asana_dedup.py check <leads.csv>` | `ASANA_TOKEN`、`ASANA_PROJECT_GID` |
| 寫入 Asana CRM 任務 | `python scripts/linkedin_processor.py asana <leads.csv>` | `ASANA_TOKEN` |

> 設定：`cd scripts && cp .env.example .env`，填入金鑰後 `pip install -r requirements.txt`。
> ⚠ 離線去重只比對 repo 內的歷史檔；**線上 Asana 去重是發送前的最終把關**，不可略過。

---

## C. 需要人工決定 / 操作（不該由自動化代替）

1. **Frank 審核 10 封連線邀請 + Day1 文案** → 通過「三自問」後，由 `pending_review` 轉 `approved`。
2. **在 Asana 為 10 筆建立 Task**，聯絡階段=`連線未發`、策略來源=S1、執行環境=`地端 Expandi`。
3. **匯入 Expandi**（地端、走 Frank 住宅 IP 的瀏覽器 session）：
   - 建立兩個 Campaign（或合併），類型選 Sales Navigator
   - 上傳兩支 CSV → 對應 custom_variable_1/2/3 → 設定 4 步 Sequence（見 `outreach-schedule-20260619.md`）
   - 啟動（每日上限 25，本批共 10，安全）
4. **第二封有回覆版 / 第三封引入方案**：依對方實際回覆，由 Frank 人工判斷後發送（內容已備在各 `lead-0X-*.md`）。

---

## D. 一鍵自我檢查（可在任何環境跑）

```bash
# 重新產生草稿與 CSV（單一真實來源）
python lead-drafts/s1-batch-20260619/build_batch.py
python lead-drafts/s1-batch-20260619-warm/build_batch.py

# 離線去重（應回報「全部為新名單」）
python lead-drafts/dedup_local_check.py \
  lead-drafts/s1-batch-20260619/s1-batch-20260619-expandi.csv \
  lead-drafts/s1-batch-20260619-warm/s1-batch-20260619-warm-expandi.csv
```

---

## 結論

**這批的狀態是「草稿就緒、可進審核」，不是「已發送」。** 真正送出前，缺口只有三個且都需要人：
①填金鑰 ②跑線上 Asana 去重 ③Frank 核准並從地端 Expandi 啟動。
自動化能做到的（選樣、分析、文案、CSV、離線去重）都已完成並可重跑驗證。
