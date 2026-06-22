# LinkedIn 每日作業流程 v2

**版本：** 2.0（試行期單帳號手動版）  
**日期：** 2026-06-22  
**適用對象：** Frank（主帳號）、Kid（接球與跟進）  
**配套工具：** LinkedIn Sales Navigator、Asana CRM、Claude（AirTalk-S1-BizDev、Reply-Router）

---

## 核心原則

> 每天的名單不多，這是優勢不是限制。每一次接觸都要像為對方量身打造——手動發送不是妥協，是在話術和流程穩定之前，保護名聲的正確選擇。

---

## 每日流程（Frank 主導，Kid 協助接球）

### 早上：名單準備與草稿生成（30-45 分鐘）

**步驟一：從 Asana CRM 確認今日待發名單**

打開 Asana「🎯 LinkedIn 台灣儲備名單 CRM v2」：
- 看 `❄️ COLD — 儲備觀察` section，找狀態為 `D1-待發` 的 task
- 每日建議發送量：**連線邀請 15-20 筆**（LinkedIn 單日上限約 20-25，保守控制）
- 優先順序：ICP 分數高的先發（50+ > 40-49 > 35-39）

**步驟二：用 AirTalk-S1-BizDev 生成草稿**

如果 Asana task 的 `custom_variable_1/2/3` 欄位已有草稿，直接用。
如果沒有（新名單），呼叫 AirTalk-S1-BizDev 生成：

```
【Lead 資訊】
姓名：
職稱：
公司：
LinkedIn About/貼文摘要：（貼入 Sales Navigator 上看到的內容）
搜尋組合：（A/B/C/D/H 等）
```

**步驟三：人工審閱草稿**

對照「三自問」（來自 S1 Agent）：
1. 如果我不是在賣東西，我還會發這封信嗎？
2. 這封信說的是他的事，還是我的事？
3. 如果他永遠不買，這段關係對他還有沒有價值？

三個都是「是」才發。

---

### 白天：手動發送（Frank 操作 Sales Navigator）

**發送連線邀請（custom_variable_1 的內容）：**
- 在 LinkedIn Sales Navigator 找到對方 profile
- 點「Connect」→ 貼入連線邀請文字
- 發送後立即更新 Asana task 狀態：`D1-待發` → `D1-已發`，備注發送日期

**發送 Day 1 私訊（custom_variable_2 的內容）：**
- 對方接受連線後，當天或隔天發出 Day 1 私訊
- 更新 Asana task 狀態：`D1-已發` → `D2-已發私訊`，備注日期

**Day 7 無回覆追蹤（custom_variable_3 的內容）：**
- 發出 Day 1 私訊後 7 天無回覆 → 發追蹤訊息
- 更新 Asana：`D2-已發私訊` → `D3-追蹤已發`

---

### 有回覆時：Reply-Router 接球流程（Kid 主導）

**步驟一：收到回覆，確認來自哪個 Asana task**

在 LinkedIn 收到訊息後，找到對應的 Asana task。

**步驟二：呼叫 Reply-Router 生成接球草稿**

把 Asana task 的 Lead 資訊 + 對話歷史 + 對方回覆原文，照 Reply-Router 的輸入格式貼入 Claude。

**步驟三：Kid 審閱草稿，10 秒決定**

- 零修改直接用 → 發送
- 微調口吻 → 調整後發送
- 不確定路由 → 看 Reply-Router 的路由建議（Jet/Yulenda）

**步驟四：更新 Asana task**

| 情境 | Asana 狀態更新 |
|------|--------------|
| HOT → 約到 Demo | → `Demo-已排定`，備注日期與出席者 |
| WARM → 繼續深化 | → `WARM-對話中`，備注最後一句話是什麼 |
| 低質 → 繼續觀察 | → `NURTURE-低溫`，備注下次觸達時間 |
| 異議型 → 進行中 | → `異議處理中`，備注異議類型 |
| 轉介型 → 建新節點 | → 建立新 Asana task（被轉介對象的名字） |
| 明確拒絕 | → `NURTURE-長期`，備注原因，標記下次觸達（3-6 個月後）|

**步驟五：把 Reply-Router 的 Ali 元資料貼進 Asana task 備注**

```
[Reply-Router 紀錄]
日期：
分類：HOT/WARM/低質/異議/轉介/拒絕
Ali 評分：X分
使用鉤子：
語氣寄存器：
草稿是否採用：是/微調/否
```

這樣 ALI-Auditor 週五稽核時有數據可用。

---

## 每日配額控制（保護帳號安全）

| 動作 | 每日上限 | 建議量 |
|------|---------|-------|
| 連線邀請 | 25 筆 | 15-20 筆 |
| 私訊（連線後） | 無硬上限，但克制 | ≤ 當日接受數 + 5 |
| 追蹤訊息 | 同上 | ≤ 10 |

> **帳號安全第一。** 寧可少發，不要觸發 LinkedIn 的異常偵測。名聲是複利資產，帳號被限流或封鎖的成本遠高於少發幾封信。

---

## 每週：ALI-Auditor 稽核（週五）

Frank 或 Lauren 呼叫 ALI-Auditor，輸入本週的：
- 發出連線邀請數
- 接受率
- 回覆數與回覆類型
- Demo 數
- Asana 各 section 的 task 數量變化

ALI-Auditor 輸出：帳面數字 vs 現實調整數字、異常標記、下週建議調整一件事。

---

## 未來擴展（等試行期穩定後才考慮）

| 時機 | 可能引入 |
|------|---------|
| 話術 A/B 有明確勝出版本 | 考慮 Expandi/Dripify 做部分自動化 |
| 帳號擴展到 2-3 個 | Orchestrator 排程 + 跨帳號去重 |
| 回覆量每週 > 50 筆 | Reply-Router 接 Asana Webhook 自動觸發 |

**現在不做這些，是因為還不需要，不是因為不知道怎麼做。**

---

*本文件取代舊版 `linkedin-sales-daily-ops.md`（仍保留供參考）*  
*下次複審：等第一輪 20 個 Lead 跑完，有真實數據後*
