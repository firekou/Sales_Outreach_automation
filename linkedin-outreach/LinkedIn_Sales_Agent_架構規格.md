# LinkedIn Sales Navigator — Agent 自動化分工與治理框架

> 版本：v1.0 | 日期：2026-05-30 | 負責人：Frank Kao

---

## 一、架構總覽

本框架以一個 **Orchestrator Agent** 為核心，統一排程、拆解任務，並協調以下五個專責 Agent 協同運作，同時透過治理層確保帳號安全與合規發送。

```
Orchestrator Agent
  ├── Search Agent      → 搜尋並擷取潛在客戶名單
  ├── Qualify Agent     → ICP 評分與優先序排列
  ├── Outreach Agent    → 個人化訊息發送與序列管理
  ├── Track Agent       → 回覆偵測、熱度標記、CRM 同步
  └── Analytics Agent   → 效益分析、A/B 測試、模型迭代
```

---

## 二、各 Agent 職責規格

### 🧠 Orchestrator Agent

| 項目 | 說明 |
|------|------|
| 觸發方式 | 每日 08:00（排程）或手動指令 |
| 核心職責 | 任務拆解、Agent 呼叫排程、錯誤重試、治理決策 |
| 輸出 | 任務執行日誌、每日摘要報告 |
| 工具 | Claude Sonnet API、Make/n8n Webhook |

**每日執行序列：**
1. 讀取配額設定（今日可發送數量）
2. 呼叫 Search Agent 補充名單
3. 呼叫 Qualify Agent 評分排序
4. 呼叫 Outreach Agent 發送訊息
5. 呼叫 Track Agent 掃描回覆
6. 呼叫 Analytics Agent 更新數據
7. 推播 Slack 日報

---

### 🔍 Search Agent

| 項目 | 說明 |
|------|------|
| 輸入 | ICP 條件（職稱、產業、公司規模、地區、關鍵字） |
| 工具 | Apify LinkedIn Sales Navigator Scraper |
| 輸出 | 結構化 Lead 清單（姓名、職稱、公司、LinkedIn URL、連結人數） |
| 去重邏輯 | 比對既有 CRM 中的 LinkedIn URL，已聯繫過的跳過 |
| 黑名單 | 競業公司、已拒絕聯繫者自動排除 |

**搜尋條件範例（台灣市場）：**
```json
{
  "geography": ["Taiwan"],
  "titles": ["CTO", "VP Engineering", "Head of Product", "Technical Director"],
  "company_size": ["51-200", "201-500", "501-1000"],
  "industries": ["Software", "FinTech", "E-Commerce", "SaaS"],
  "keywords": ["AI", "digital transformation", "automation"]
}
```

---

### 🎯 Qualify Agent

| 項目 | 說明 |
|------|------|
| 輸入 | Search Agent 輸出的 Lead 清單 |
| 工具 | Claude Haiku（快速推論）、Exa Search（近期動態查詢） |
| 輸出 | 每筆 Lead 的 ICP 分數（0-100）+ 優先級（A/B/C） |

**評分維度：**

| 維度 | 權重 | 說明 |
|------|------|------|
| 職稱匹配度 | 30% | 是否為決策者或影響者 |
| 公司規模 | 20% | 是否在目標區間 |
| 產業吻合 | 20% | 是否在核心產業清單 |
| 近期動態 | 20% | 近 30 天有無職位異動、融資、招募 AI 職缺 |
| 共同連結 | 10% | 是否有一度連結或共同社群 |

**分級規則：**
- A 級（80+）：優先發送 InMail
- B 級（60-79）：發送 Connection Request + 個人化訊息
- C 級（<60）：放入候補池，等待下週

---

### ✉️ Outreach Agent

| 項目 | 說明 |
|------|------|
| 輸入 | Qualify Agent 輸出的 A/B 級 Lead |
| 工具 | Claude Sonnet（訊息生成）、Make.com + Phantombuster/Dripify（自動發送） |
| 輸出 | 發送記錄、訊息內容快照 |

**發送配額限制（每帳號上限）：**
- InMail：每日最多 20 封
- Connection Request：每日最多 50 則
- Follow-up 訊息：每日最多 30 則

**序列設計（3-touch）：**

```
Day 0  │ 初次接觸
       │ → 個人化 Connection Request（含近期 Post 提及）
       │
Day 3  │ Follow-up #1（若已連結未回覆）
       │ → 簡短價值主張 + 一個具體問題
       │
Day 7  │ Follow-up #2（最後一次）
       │ → 提供資源（文章/案例）+ 軟性 CTA
       │
Day 14 │ 自動標記為 Cold，移出序列
```

**訊息生成 Prompt 架構：**
```
角色：你是 [公司名] 的 BD 代表
目標：針對 [姓名] 在 [公司] 擔任 [職稱] 的背景，撰寫一封 80 字以內的 LinkedIn 訊息
參考資料：近期動態 [XXX]、共同點 [XXX]
語調：專業但親切，不過度推銷
結尾：附上一個開放式問題
禁止：不要提到競業、不要貼上會議連結
```

---

### 📡 Track Agent

| 項目 | 說明 |
|------|------|
| 觸發方式 | 每日 17:00 掃描 + 即時 Webhook（如有回覆） |
| 工具 | Apify LinkedIn Message Scraper、Google Calendar API、Gmail |
| 輸出 | 回覆分類標籤、CRM 狀態更新、會議邀請草稿 |

**回覆分類邏輯（Claude Haiku 分類）：**

| 分類 | 標籤 | 後續動作 |
|------|------|---------|
| 正面回應，有興趣 | 🔥 Hot | Orchestrator 通知業務，自動草擬回覆 + 排程 Demo |
| 詢問更多資訊 | 🌡️ Warm | 自動寄送產品一頁報告 + 3 天後 Follow-up |
| 婉拒 | ❄️ Cold | 標記不再聯繫，加入黑名單 |
| 無法判斷 | ❓ Unclear | 推送給人工確認 |

**Hot Lead 偵測後立即推播 Slack 通知（2 小時內人工確認）**

---

### 📊 Analytics Agent

| 項目 | 說明 |
|------|------|
| 觸發方式 | 每週一 09:00 |
| 工具 | Google Sheets、Claude Sonnet（洞察解讀） |
| 輸出 | 週報（PDF）、ICP 模型迭代建議、A/B 測試結論 |

**追蹤 KPI：**
- 搜尋名單量 / 合格率（Qualify 通過 %）
- Connection Request 接受率
- InMail 回覆率
- Lead → Meeting 轉換率
- 各訊息版本 A/B 勝率
- 每筆有效 Lead 成本（時間成本）

**A/B 測試機制：**
每週自動生成 2 個訊息版本，各發送 50 封，以回覆率決定下週使用版本，Analytics Agent 每週回饋結果給 Orchestrator 更新模板庫。

---

## 三、治理層規格

### 速率限制
- 發送行為加入隨機延遲（3-15 秒間隔），模擬人類操作節奏
- 每帳號達到日限 80% 即停止，保留緩衝
- 異常偵測：若接受率連續 3 天 < 10%，自動暫停並告警

### 人工審核閘門
- ICP 分數 A 級且對方為 C-level：自動推送人工確認後再發送
- 訊息被 LinkedIn 標記警告：立即暫停並通知管理員

### 帳號安全
- Apify Actor 搭配住宅代理 IP（Residential Proxy）
- 登入行為模擬：避免高頻操作，每次操作間距 > 2 秒
- 多帳號輪換（如有多個 Sales Navigator 席位）

### 通知與告警（Slack）
```
每日摘要（18:00）：
  ✅ 今日發送：XX 封
  🔥 Hot Lead：XX 筆
  📈 接受率：XX%
  ⚠️ 異常告警：（如有）
```

---

## 四、技術棧與整合

| 層級 | 工具 | 用途 |
|------|------|------|
| 資料擷取 | Apify LinkedIn Sales Navigator Scraper | 搜尋名單、訊息掃描 |
| AI 推論 | Claude Sonnet 4.6 / Haiku 4.5 | 評分、訊息生成、回覆分類 |
| 自動化串接 | Make (Integromat) 或 n8n | Webhook 觸發、資料流串接 |
| CRM 儲存 | Asana (任務看板 + CRM) | Lead 狀態、對話歷程 |
| 報表 | Google Sheets | KPI 追蹤、週報 |
| 通知 | Slack Bot | 即時告警、每日摘要 |
| 搜尋增強 | Exa Web Search | 近期動態、公司新聞 |
| 排程 | Cowork 排程任務 | 每日/週定時觸發 |

---

## 五、資料流程圖（文字版）

```
LinkedIn Sales Nav
      │
      ▼
[Search Agent] ──Apify──▶ Lead 原始清單
      │
      ▼
[Qualify Agent] ──Claude──▶ ICP 評分 + A/B/C 分級
      │
      ▼
[Outreach Agent] ──Make──▶ 個人化訊息發送
      │
      ▼
[Track Agent] ──Apify/Gmail──▶ 回覆分類 + CRM 更新
      │
      ▼
[Analytics Agent] ──Asana + Google Sheets──▶ 週報 + 模型迭代
      │
      └──────────────────────────▶ 回饋 Orchestrator
                                     調整 ICP / 訊息策略
```

---

## 六、快速啟動清單

- [ ] 設定 Apify 帳號並取得 API Token
- [ ] 確認 Asana 專案 GID 並設定 LinkedIn CRM 看板
- [ ] 設定 Make 自動化場景（Orchestrator webhook）
- [ ] 配置 Claude API Key（Sonnet + Haiku）
- [ ] 建立 Slack Bot 並設定通知頻道
- [ ] 確認 LinkedIn Sales Navigator 帳號配額
- [ ] 設定 Cowork 排程任務（每日 08:00 觸發）
- [ ] 定義初版 ICP 條件（職稱、產業、地區）
- [ ] 建立初版訊息模板庫（A/B 各 2 版本）
- [ ] 設定黑名單與競業公司清單

---

## 七、多帳號並行設計

### 帳號分工原則
每個真實員工帳號對應不同 ICP 區間，錯開發送時間窗，共用同一套 Asana CRM。

| 帳號 | 角色 | ICP 目標區間 | 發送時間窗 | 每日上限 |
|------|------|------------|----------|---------|
| Frank | CEO（高信任度） | CxO / 創辦人 / 大型企業主 | 08:00–09:00 | 25 conn |
| Jet | 商務總監 | 通路商 / SI / 代理商合夥人 | 10:00–11:00 | 25 conn |
| Kid | 業務（主力） | IT 主管 / IT Director / CIO | 14:00–15:00 | 30 conn |
| Lauren | BD 主管 | 行銷代理商 / 顧問公司主管 | 16:00–17:00 | 25 conn |
| Alice | 產品經理 | CTO / VP Product / Engineering Head | 11:00–12:00 | 20 conn |

**總計：125 connections/day，625/週**

### 合規原則
- 每帳號使用各自的 IP（住宅代理或各自電腦）
- 不同帳號使用不同訊息風格（見 linkedin-cold-outreach-sop.md）
- 所有帳號的 Lead 統一進入同一個 Asana 專案，`source_account` 欄位標記來源
- 跨帳號去重：Asana 匯入前先查 LinkedIn URL 是否已存在，任何帳號聯繫過的自動跳過
- 每帳號達日限 80% 即停止，保留緩衝

---

*本文件為動態規格，Analytics Agent 每週回饋後由 Orchestrator 更新 ICP 條件與訊息策略。*
