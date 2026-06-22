# AirTalk — LinkedIn 陌生開發策略總覽

**產品：** AI Token King（aitokenking.com.tw）  
**管理負責人：** Frank  
**建立日期：** 2026-06-09  
**架構更新：** 2026-06-22（簡化為單帳號手動執行 + Asana CRM）

---

## 核心設計哲學

> 不是價格導向競爭，而是「深度個人化共情切入」。
> 在接觸任何一個人之前，必須理解他的發展邏輯，把我們變成他所需要的角色。

**三個必要步驟（每個 Lead 都適用）：**

1. **細讀背景**：公司成就、個人 LinkedIn 完整經歷
2. **定位發展邏輯**：他從哪來、走向哪裡、想成為誰
3. **成為他所需要的角色**：方案對接他的產業定位與發展路徑，而非推銷產品

---

## 四套並行策略

| 代號 | 策略名稱 | 觸發點 | 主動性 | 文件 |
|------|---------|--------|--------|------|
| S1 | 直攻法 | 主動搜尋目標人 | ★★★★★ | `01-S1-direct-outreach.md` |
| S2 | 104 意圖前置法 | 職缺刊登行為 | ★★★★☆ | `02-S2-104-intent.md` |
| S5 | 社群潛伏法 | 加入共同社群 | ★★★☆☆ | `03-S5-community.md` |
| S6 | 競品替換法 | 競品使用信號 | ★★★★★ | `04-S6-competitor.md` |

---

## 現行執行架構（試行期，單帳號手動）

```
Sales Navigator 搜尋名單
        │
        ▼
AirTalk-S1-BizDev（Claude Agent）
  ─ 深度分析 Lead 背景
  ─ 生成個人化三封信草稿
        │
        ▼
Frank 人工審閱 → LinkedIn 手動發送
        │
        ▼
對方回覆進來
        │
        ▼
Reply-Router（Claude Agent）
  ─ 意圖分類 + Ali 評分
  ─ 生成個人化接球草稿
        │
        ▼
Kid 人工審閱 → LinkedIn 手動發送
        │
        ▼
Asana CRM 回寫（手動更新狀態）
        │
        ▼
ALI-Auditor 週稽核
```

**為什麼現在不用自動排程工具（Expandi/Dripify）：**
- 目前只有一個 LinkedIn 帳號，試行期以累積經驗和調校話術為主
- 每日名單量小，手動發送可以保證每一次接觸的品質
- Asana CRM 已能完整記錄每個 Lead 的狀態，不需要第三方工具的排程功能
- 等話術與流程穩定後，再評估是否引入自動化工具

---

## 運作原則

| 原則 | 說明 |
|------|------|
| **策略標籤化** | 每筆 Lead 記錄觸達來源（S1/S2/S5/S6），追蹤各策略 ROI |
| **熱度分級** | S6 替換型 > S2 意圖型 > S5 社群型 > S1 冷觸達，優先資源給高熱度 |
| **每日節流** | LinkedIn 單帳號連線/訊息有上限，每日手動控制配額，保護帳號安全 |
| **Asana 即時回寫** | 每次發送、每次回覆後立即更新 Asana task 狀態，不欠帳 |
| **Ali 每週稽核** | 每週五 ALI-Auditor 掃全漏斗，確保狀態真實、不自欺 |

---

## 關聯文件

| 文件 | 說明 |
|------|------|
| `05-talk-scripts.md` | 四套策略完整話術 SOP（Kid-Sales 設計） |
| `06-ai-user-persona.md` | AI 使用者類型分類 × 話術對應矩陣 |
| `07-orchestrator-spec.md` | Orchestrator Agent 技術規格 |
| `02-S2-legitimacy-framework.md` | S2 接觸合理性框架（三對象客製化接觸理由）|
| `02-S2-104-intent-automation-spec.md` | S2 完整自動化流程規格（Make Flow 4）|
| `02-S2-flow-simulations.md` | S2 端對端流程模擬（3 筆案例：A 級 PASS / C 級 HOLD / B 級 PASS）|
