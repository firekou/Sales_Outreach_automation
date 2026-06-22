# AI Token King — 陌生開發自動化流程運作基礎

**版本：** 1.0  
**日期：** 2026-05-31  
**Owner：** Kid（執行）× Lauren（架構）× Alice（ICP 校準）  
**目標：** 1,500 封/月精準觸達，LinkedIn 渠道 MRR ≥ NT$50,000

---

## 總綱：三渠道組合邏輯

```
┌─────────────────────────────────────────────────────────────────────┐
│                     陌生開發三渠道全景                                │
│                                                                     │
│  【訊號偵測層】          【觸達渠道層】         【轉換追蹤層】          │
│                                                                     │
│  LinkedIn Sales Nav  →  LinkedIn 連結/InMail →                      │
│  104 職缺監控        →  LinkedIn 交叉觸達    →  Asana CRM           │
│  Apollo Intent       →  Email 自動序列      →  (統一管理)            │
│                                                                     │
│  合計容量：~1,500 封/月（單人執行）                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### 三渠道特性對照

| 維度 | LinkedIn | 104 + LinkedIn | Apollo |
|------|---------|----------------|--------|
| **本質** | 社群觸達 | 訊號偵測 → 交叉觸達 | 資料庫直接觸達 |
| **觸達方式** | 連結請求 + InMail | LinkedIn / Email（從104找到公司再轉） | Email 自動序列 |
| **月觸達量** | ~380 封（上限） | ~200 封 | ~800 封 |
| **需要對方接受** | 連結請求需對方同意 | 不需要（直接信箱） | 不需要（直接信箱） |
| **關係溫度** | 最高（先建立連結） | 中（訊號驅動，針對性強） | 較低（但量大） |
| **台灣覆蓋率** | 高（IT/科技圈） | 最高（本地招募市場） | 中（大公司好，中小較低） |
| **自動化程度** | 70%（Kid 仍需手動發送） | 60%（監控自動，觸達手動） | 90%（序列全自動） |
| **適合場景** | 建立長期關係、高價值Lead | 找到「正在投資AI的公司」 | 規模化觸達、補足 LinkedIn 缺口 |

---

## Part 1：Lead 訊號全景地圖

> **核心理念：訊號驅動的外撥，轉換率比冷撥高 4-8 倍。**
> 所有觸達都應該有「我為什麼現在聯繫你」的明確理由。

### 1.1 訊號分級體系（三渠道共用）

```
Tier 1 — 主動購買訊號（今天聯繫，訊號半衰期：48 小時）
  ✓ 對方主動詢問 AI Token King 相關資訊
  ✓ 競爭對手合約到期（從 Apollo Intent 偵測）
  ✓ 公司剛完成融資（LinkedIn / 104 新聞）
  ✓ 104 上開了「Prompt Engineer」或「AI Engineer」職缺（本週）

Tier 2 — 組織投資訊號（本週聯繫，訊號半衰期：7 天）
  ✓ 新任 IT 主管 / CTO 上任（LinkedIn Job Change Alert）
  ✓ 104 上開了 IT Manager / 數位轉型相關職缺
  ✓ 公司 LinkedIn 頁面貼文提到 AI 工具
  ✓ Apollo Intent：公司員工搜尋「API cost management」

Tier 3 — 背景符合訊號（本月培育，訊號半衰期：30 天）
  ✓ LinkedIn Profile 技能含 AWS / GCP / Azure / OpenAI
  ✓ 公司規模 50-200 人，行業符合 ICP
  ✓ 曾瀏覽 aitokenking.com.tw（若有追蹤像素）
  ✓ 104 職缺描述中提到 ChatGPT / 數位轉型（非本週）
```

### 1.2 ICP 評分矩陣（四渠道共用）

```
公司規模分數（0-25）：
  51-200 人 → 25 分（甜蜜點）
  11-50 人  → 20 分
  201-500 人 → 10 分
  其他      →  5 分

行業符合度（0-25）：
  科技/軟體/SaaS         → 25 分
  行銷代理商/廣告         → 20 分
  顧問/數位轉型服務        → 18 分
  電商/新零售             → 15 分
  教育科技               → 12 分
  其他                   →  5 分

AI 使用訊號（0-25）：
  明確提到 OpenAI/Claude/Gemini → +15 分
  提到 AI 工具/機器學習          → +10 分
  提到數位轉型                   →  +8 分
  104 開 AI 相關職缺             → +12 分（Tier 1 加倍）

雲端使用背景（0-25）：
  AWS / GCP / Azure 明確提到    → +20 分
  阿里雲 / 騰訊雲 / 火山引擎     → +18 分
  只提到雲端（未指定供應商）      → +10 分

分類閾值：
  HOT  ≥ 70 分 → 本週優先觸達
  WARM 50-69 分 → 本月排程觸達
  COLD < 50 分 → 觀察池
```

---

## Part 2：純 LinkedIn 流程

**月觸達容量：~380 封（連結請求 330 + InMail 50）**  
**適用場景：建立關係、高價值 Lead、需要暖身的決策者**

### 2.1 完整流程圖

```
[A-LI-Scout 自動偵測]
        ↓
  Lead 進入 Asana「00 Lead Pool」
        ↓
  Gate 0：ICP 分數 ≥ 50？
    否 → 標記 COLD，進觀察池
    是 ↓
  [A-LI-Writer 生成草稿]
  連結請求草稿（≤300字元）
        ↓
  Kid 審閱草稿（目標：5 分鐘/筆）
        ↓
  Kid 手動在 LinkedIn 發送連結請求
  → Asana 移至「01 Connection Sent」
        ↓
  ┌─────────────────────────────┐
  │   等待回應（最多 14 天）      │
  └─────────────────────────────┘
        ↓
  已接受連結？
    否（14天後）→ InMail 補一封（HOT Lead 才做）
                  → 仍無回應 → COLD，60天後重啟
    是 ↓
  → Asana 移至「02 Connected / Awaiting Value Touch」
        ↓
  [A-LI-Writer 生成價值觸達訊息]
        ↓
  Kid 審閱 → 手動發送
  → Asana 移至「03 Value Sent / Awaiting Reply」
        ↓
  ┌─────────────────────────────┐
  │   等待回應（Day 3/7/14/21）  │
  │   A-LI-Tracker 自動提醒      │
  └─────────────────────────────┘
        ↓
  回覆？
    正面 → Section 04 HOT → Demo 預約
    中性 → Section 05 WARM → 問一個問題
    負面 → Section 09 CLOSED → 優雅結束
    無回應 Day 21 → Section 09 NURTURE
```

### 2.2 LinkedIn 每日發送節奏

```
工作日建議節奏（避免觸發 LinkedIn 風控）：
  早上 9:00-10:00：發 10-12 封連結請求
  下午 2:00-3:00：發跟進訊息給已連結的 Lead（不限量）
  下午 5:00：處理當日回覆

每週上限：
  連結請求：100-120 封（不要衝到上限，保留緩衝）
  InMail：最多 12-15 封/週（月 50 封均攤）
  
危險警號（立刻暫停）：
  ✗ LinkedIn 出現「你可能認識...嗎？」確認彈窗
  ✗ 連結請求被對方標記為「不認識此人」
  ✗ 帳號出現暫時限制通知
```

### 2.3 三個搜尋組合（搭配 apify_linkedin_scraper.py）

**組合 A — 科技公司 IT 決策者**
```
職稱：IT Manager, IT Director, Head of IT, Technology Manager, CTO
公司規模：51-200 人
行業：Computer Software, Internet, IT Services
地區：Taiwan
活躍度：近 30 天有發文
預估月新增 Lead：100-150 筆
```

**組合 B — 行銷代理商高層**
```
職稱：Marketing Director, Creative Director, Head of Content,
     Digital Marketing Manager, Agency Owner
公司規模：11-50 人
行業：Marketing & Advertising, Internet
地區：Taiwan
預估月新增 Lead：50-80 筆
```

**組合 C — 數位轉型顧問 / 服務商**
```
職稱：Digital Transformation Manager, AI Consultant,
     Innovation Manager, CDO, Head of Digital
公司規模：11-200 人
行業：Management Consulting, IT Services, Professional Services
關鍵字：AI OR ChatGPT OR digital transformation
預估月新增 Lead：40-70 筆
```

---

## Part 3：104 + LinkedIn 交叉流程

**月觸達容量：~200 封（從 104 識別公司，再透過 LinkedIn 觸達）**  
**適用場景：找到「正在投資 AI」的公司，切入時機最精準**

### 3.1 104 作為訊號偵測器的邏輯

```
一般業務的邏輯：
  「我猜這家公司可能用 AI」→ 發訊息 → 對方沒感覺

104 訊號驅動的邏輯：
  「這家公司昨天在招 AI Engineer，表示他們現在正在擴大 AI 用量」
  → 發訊息 → 「是的，我們正好在找管理 AI 成本的方案」
  
訊號半衰期：新職缺 → 1 週內觸達效果最好
```

### 3.2 完整流程圖

```
[每週一 09:00，Kid 手動或腳本掃描 104]
        ↓
  搜尋關鍵字：
    「AI工程師」「Prompt Engineer」「資料科學家」
    「MLOps」「機器學習」「數位轉型」
  篩選：台灣、50-500人、近7天開缺
        ↓
  整理成「104_leads_本週日期.csv」
  欄位：公司名、職缺名、公司規模、地區、職缺連結
        ↓
  [雲端處理：linkedin_processor.py 交叉比對]
  → 用公司名在 LinkedIn 搜尋
  → 找到 IT主管 / CTO / HR Director
  → 計算 ICP 分數（加入「104 AI職缺」加 12 分 Tier 1 bonus）
        ↓
  Gate：分數 ≥ 60？（104 訊號提高門檻）
    否 → 進 Lead Pool 觀察
    是 ↓
  [A-LI-Writer 生成 104 版觸達訊息]
  （強調：「我看到你們在招 AI Engineer...」）
        ↓
  Kid 審閱 → LinkedIn 連結請求 或 Email
```

### 3.3 104 專屬三種切入角度

**角度 A：招募訊號切入（IT 主管 / CTO）**
```
「您好，看到 [公司名] 最近在招 AI 工程師，
 表示貴公司的 AI API 使用量應該即將快速成長。

 很多同規模的公司在這個階段會遇到同一個問題：
 工程師各自用 OpenAI、Claude、Gemini，
 但月底要算每個專案的 AI 成本時，完全拆不清楚。

 我們做的就是解決這個問題——
 每個部門分配 Token 預算、月底一張 ROI 報表。

 你們現在工程師人數大概多少？」
```

**角度 B：數位轉型切入（CDO / 數位轉型主管）**
```
「您好，看到 [公司名] 積極在做數位轉型，
 也在招募相關人才，令人印象深刻。

 分享一個我們觀察到的盲點：
 AI 工具導入很快，但費用管控機制往往跟不上，
 三個月後老闆問 ROI，數據卻散在不同平台的帳單裡。

 我們剛好在填補這個空白，
 有沒有機會用 15 分鐘分享幾個案例？」
```

**角度 C：HR 切入（招募窗口 → 轉介 IT 主管）**
```
「您好，我知道 HR 最近也開始大量使用 AI 工具來加速篩選。

 有個小問題很多 HR 跟我反映：
 這些工具的費用很難歸到 HR 預算，
 要跟財務說明時說不清楚。

 我們有個方案可以幫 HR 把 AI 工具的費用自動追蹤，
 月底出一張報告直接給 CFO 看。

 請問貴公司負責 IT 採購的主管是哪位？
 如果方便的話可以幫我引薦嗎？」
```

### 3.4 104 監控職缺關鍵字清單

```
第一優先（AI 直接訊號）：
  AI工程師、AI Engineer、Prompt Engineer、LLM Engineer
  機器學習工程師、MLOps Engineer、資料科學家 Data Scientist
  AI產品經理、AI Product Manager

第二優先（雲端/基礎架構訊號）：
  雲端工程師、Cloud Engineer、DevOps Engineer
  IT Manager、IT Director、資訊主管
  系統架構師、Solution Architect

第三優先（數位轉型訊號）：
  數位轉型、Digital Transformation、CDO
  創新部門、Innovation Manager
  電商技術、Tech Lead

排除關鍵字（避免誤判）：
  硬體工程師、製造業、傳統製造、生產線
  500人以上大型企業（決策慢，服務能力不足）
```

---

## Part 4：Apollo 流程

**月觸達容量：~800 封（Email 自動序列，無平台限制）**  
**適用場景：規模化觸達、LinkedIn 觸達不到的人、補足整體容量**

### 4.1 Apollo 如何取得聯絡資訊

```
Step 1：在 Apollo 資料庫搜尋
  篩選條件：
    地區：Taiwan
    職稱：IT Manager / IT Director / CTO / Marketing Director / CDO
    公司規模：50-500 人
    行業：Computer Software / Internet / Marketing / Consulting
    技術堆疊（選填）：AWS / Azure / GCP / OpenAI（若有資料）

Step 2：驗證信箱
  Apollo 自動標注：
    ✓ Verified（SMTP 驗證通過）→ 直接使用
    ~ Likely（格式推算）→ 謹慎使用
    ✗ Invalid → 排除

Step 3：匯出 CSV → 匯入發信序列
```

### 4.2 Apollo Email 五步序列設計

```
Day 1 — 切入信（個人化）
  主旨 A：「[公司名] 的 AI 工具費用，有辦法每月拆分嗎？」
  主旨 B：「[姓名]，一個關於 AI API 成本的問題」
  
  內文：
  「[姓名] 您好，

  我在研究台灣中小型科技公司管理 AI 工具費用的方式，
  發現一個普遍現象：同時用 3 個以上 AI 供應商的公司，
  有 70% 說不清楚每個部門的 AI 成本佔比。

  [公司名] 目前的 AI API 費用，是統一在 IT 預算，
  還是各部門分開吸收？

  這個問題的答案，通常決定了你們需不需要
  像 AITokenKing 這樣的統一管控工具。

  Kid | AI Token King
  aitokenking.com.tw」

---

Day 4 — 跟進（若未開信）
  主旨：「Re：AI API 費用管控」
  內文：
  「[姓名]，

  補充一個數字：我們服務的客戶平均在導入後，
  第一個月就找到 15-30% 的 AI 費用可以優化。

  主要是因為很多 API 調用其實在跑非必要的任務，
  統一管控後自然就減少了。

  您方便這週花 15 分鐘看看嗎？」

---

Day 8 — 案例分享（若未回覆）
  主旨：「和 [公司名] 類似的案例」
  內文：
  「[姓名]，

  分享一個規模和 [公司名] 相近的案例：
  一家 80 人的台灣 SaaS 公司，
  導入 AITokenKing 之前，
  每月 AI 費用有 40% 無法準確歸屬到專案。

  導入後 90 天，他們的 IT 主管
  第一次能在週報中清楚報告每個產品線的 AI ROI。

  您這邊也有類似的困擾嗎？」

---

Day 14 — 痛點確認（若未回覆）
  主旨：「[姓名]，一個直接的問題」
  內文：
  「[姓名]，

  直接問：
  貴公司現在有統一追蹤 AI 工具費用的機制嗎？

  如果有，我就不再打擾了。
  如果還沒有，我們有一個免費試用方案，
  三天就能看到你們的 AI 費用全景。

  要試看看嗎？」

---

Day 21 — Last Touch
  主旨：「最後一封，之後不再打擾」
  內文：
  「[姓名]，

  這是最後一封。

  如果現在不是合適的時機，完全沒關係。
  請告訴我什麼時候比較適合，
  或者直接回覆「不感興趣」，
  我會把您從名單中移除。

  祝工作順利。
  Kid」
```

### 4.3 Apollo 自動化設定要點

```
序列設定：
  發信時間：週一到週五，早上 9:00-11:00（對方時區）
  發信速度：每日最多 50 封（新帳號）→ 穩定後可到 100 封
  每封間隔：至少 60 秒（避免 Spam 偵測）

帳號暖機（新帳號必做，前 4 週）：
  第 1 週：10 封/天
  第 2 週：20 封/天
  第 3 週：35 封/天
  第 4 週：50 封/天
  → 開信率穩定在 30% 以上才繼續放量

發信域名建議：
  主域名 aitokenking.com.tw → 不用來發冷郵件（保護主品牌）
  另設 mail.aitokenking.com.tw 或 outreach.aitokenking.tw 發冷郵件

垃圾信防護：
  ✓ 設定 SPF、DKIM、DMARC 紀錄
  ✓ 每封信要有 Unsubscribe 連結
  ✓ 退信率保持在 2% 以下
  ✓ 未開信率超過 70% → 暫停序列、重寫主旨
```

---

## Part 5：三渠道整合架構

### 5.1 月觸達容量分配

```
渠道              月觸達量    自動化比例    Kid 手動時間
─────────────────────────────────────────────────────
LinkedIn（Kid）     380 封      70%         約 2 小時/天
104 → LinkedIn      200 封      60%         約 30 分鐘/天
Apollo Email        800 封      90%         約 30 分鐘/天
─────────────────────────────────────────────────────
合計              1,380 封      78%         約 3 小時/天
```

### 5.2 Lead 去重與防重複觸達機制

```
同一個 Lead 在三個渠道的處理規則：

規則 1：LinkedIn 優先
  若已在 LinkedIn 連結或發過訊息 → 不要同時發 Apollo Email
  原因：同時收到兩個渠道的訊息，對方會覺得被騷擾

規則 2：Apollo → LinkedIn 升溫
  Apollo Email 對方有開信但未回覆（有溫度）
  → 可以在 LinkedIn 再次觸達（提到「我之前有寄信...」）

規則 3：104 訊號強化 LinkedIn 訊息
  從 104 找到的公司 → LinkedIn 找到決策者
  → LinkedIn 訊息中加入 104 職缺訊號角度
  → 不另外發 Apollo Email（避免重複）

Asana 防呆欄位：
  「已觸達渠道」：LinkedIn / Apollo / 104+LinkedIn / 多渠道
  「跨渠道備注」：記錄每個渠道的狀態
```

### 5.3 三渠道統一 Lead Pool 管理（Asana）

```
Lead 來源標記（custom field）：
  A-LI-Scout     → LinkedIn 搜尋
  104-Monitor    → 104 職缺偵測
  Apollo-DB      → Apollo 資料庫
  Referral       → 轉介
  Inbound        → 主動找上門

Section 對應（同一套 10 Section CRM）：
  00 Lead Pool     ← 三渠道 Lead 統一進入
  01-08            ← 依觸達進度移動（渠道無關）
  09 CLOSED        ← 三渠道統一結案

每個 Task 的「渠道」欄位讓 A-LI-Tracker
可以分別統計三渠道的轉換率，找出最 ROI 高的渠道。
```

### 5.4 跨渠道週節奏設計

```
週一（Lead 補充日）：
  09:00 — Kid 用腳本抓 LinkedIn 新 Lead（apify_linkedin_scraper.py）
  09:30 — Kid 手動掃 104 關鍵職缺，整理 104_leads_本週.csv
  10:00 — 傳給 Claude Code 做 ICP 評分 + 草稿生成
  10:30 — 確認 Apollo 本週序列名單，移除已回覆者

週二、三、四（觸達執行日）：
  09:00-10:00 — 發 LinkedIn 連結請求（每天 12-15 封）
  10:00-10:30 — 審閱並發送 A-LI-Writer 草稿（5-8 封）
  12:00-12:30 — 處理 LinkedIn Inbox 回覆
  17:00-17:30 — 更新 Asana 狀態，處理 Apollo 回覆通知

週五（回顧日）：
  16:00-17:00 — 週報檢視（A-LI-Tracker 自動生成）
    - 各渠道連結/開信/回覆率
    - HOT Lead 本週跟進狀態
    - 下週觸達計畫
```

---

## Part 6：Agent 自動化規格（擴展版）

### 6.1 A-LI-Scout（擴展到三渠道）

```
觸發條件：
  - 每週一早上 08:30 自動執行
  - LinkedIn：呼叫 Apify 執行三個搜尋組合
  - 104：呼叫 104_job_monitor.py 掃描關鍵職缺
  - Apollo：從 Apollo CSV 匯出中讀取新 Lead

評分與分類：
  - 計算 ICP 分數（含渠道特有 bonus）
  - 104 AI 職缺訊號：+12 分
  - Apollo Intent 訊號：+10 分
  - 去重：檢查 Asana 是否已有同一 LinkedIn URL / 信箱

輸出：
  - 建立 Asana Task（00 Lead Pool）
  - 通知 Kid：「本週新增 X 筆 HOT Lead，Y 筆 WARM Lead」

人機協作節點：
  - Kid 最終確認 Gate 0（每筆 2 分鐘目標）
```

### 6.2 A-LI-Writer（擴展 Email 版本）

```
LinkedIn 版：
  - 連結請求附言（≤300字元，中文）
  - 價值觸達訊息（≤500字，含訊號切入角度）
  - 跟進訊息（Day 3/7/14，各 3 個 A/B 版本）

Email 版（Apollo 序列）：
  - Day 1 切入信（個人化主旨 A/B + 正文）
  - Day 4/8/14/21 跟進信
  - 根據行業自動選擇：科技版 / 行銷版 / 顧問版

104 交叉觸達版：
  - 職缺訊號切入角度（自動抓取職缺名稱填入）
  - HR 轉介版本

所有版本輸出格式：
  - Asana 子任務（Kid 直接複製發送）
  - Google Docs 草稿（批次審閱用）
```

### 6.3 A-LI-Tracker（三渠道統一追蹤）

```
每日自動更新：
  - 掃描 Asana 各 Section 的 Lead 數量
  - 偵測逾期未行動的 Lead（>3 天無更新）
  - Apollo 開信/點擊數據同步（透過 Webhook）

每週五自動生成週報：
  ┌──────────────────────────────────────────────┐
  │  本週觸達週報（2026/W22）                      │
  ├──────────────────┬──────────┬──────────────── │
  │  渠道            │  送出    │  回覆率          │
  ├──────────────────┼──────────┼──────────────── │
  │  LinkedIn 連結    │  65 封  │  38%（接受率）   │
  │  LinkedIn InMail  │  12 封  │  25%             │
  │  Apollo Email     │  180 封 │  12%（開信率42%）│
  │  104→LinkedIn     │  28 封  │  32%             │
  ├──────────────────┴──────────┴──────────────── │
  │  本週新增 HOT：8 筆                            │
  │  本週 Demo 預約：2 場                           │
  │  本月累計 MRR 貢獻：NT$ 0（首月建立期）         │
  └──────────────────────────────────────────────┘

異常偵測：
  - 連結請求接受率 < 20% → 警告，檢查訊息品質
  - Email 退信率 > 3% → 警告，暫停序列
  - HOT Lead > 72 小時無行動 → 紅色警報
  - Lead Pool < 100 筆 → 補充提醒
```

---

## Part 7：關鍵績效指標（KPI）

### 7.1 三渠道分開追蹤

| 指標 | LinkedIn | Apollo Email | 104→LinkedIn |
|------|---------|-------------|-------------|
| 連結接受率 / 開信率 | ≥ 30% | ≥ 35% | ≥ 35% |
| 回覆率 | ≥ 25% | ≥ 8% | ≥ 30% |
| Demo 預約轉化率 | ≥ 5% | ≥ 2% | ≥ 6% |
| Lead → 成交率 | ≥ 3% | ≥ 1% | ≥ 4% |

> 104→LinkedIn 的轉化率預設最高，因為訊號最精準。

### 7.2 整體漏斗目標（月）

```
Lead Pool 新增：≥ 400 筆
  ↓ ICP 篩選（≥50分）
觸達發出：~1,380 封
  ↓
有回應（含正面+中性）：~200 封（~14%）
  ↓
Demo 感興趣：~40 筆
  ↓
Demo 確認：~15-20 場
  ↓
成交：≥ 5 個帳戶
  ↓
MRR 貢獻：≥ NT$ 50,000
```

---

## Part 8：實施路線圖

### Phase 1（現在，第 1-4 週）：LinkedIn Only

```
目標：建立基礎流程，跑通第一批 Lead

Week 1：
  □ Kid 本機設好 .env（Apify + LinkedIn li_at）
  □ 執行 apify_linkedin_scraper.py，取回第一批名單
  □ 傳給 Claude Code 做 ICP 評分
  □ 確認 Asana CRM 10 個 Section 建立完成

Week 2-3：
  □ 每天發 10-12 封 LinkedIn 連結請求
  □ 開始收到第一批接受回覆
  □ A-LI-Writer 生成價值觸達草稿，Kid 審閱發出

Week 4：
  □ 第一批回覆分類（A-LI-Tracker）
  □ 嘗試預約第一場 Demo
  □ 檢視連結接受率，若 < 25% → 調整訊息模板

KPI 目標：送出 200 封連結請求，回覆率 ≥ 20%
```

### Phase 2（第 5-8 週）：加入 Apollo Email

```
目標：提升觸達量至 ~800 封/月

Week 5：
  □ 申請 Apollo.io Basic（$49/月）
  □ 設定發信域名 mail.aitokenking.com.tw
  □ SPF / DKIM / DMARC DNS 設定
  □ 帳號暖機開始（10 封/天）

Week 6-7：
  □ 設計 5 步 Email 序列（參照 Part 4.2）
  □ 在 Apollo 搜尋 200 筆台灣目標 Lead
  □ 開始發送，監控開信率（目標 ≥ 35%）

Week 8：
  □ 分析 LinkedIn vs Apollo 回覆率差異
  □ 調整 Email 主旨和正文（A/B 測試）
  □ Apollo → LinkedIn 交叉觸達流程測試

KPI 目標：Apollo 發出 400 封，開信率 ≥ 35%，回覆率 ≥ 8%
```

### Phase 3（第 9-12 週）：加入 104 監控

```
目標：完整三渠道並行，觸達量達 1,500 封/月

Week 9：
  □ 104_job_monitor.py 腳本建立（或 Google Alert 替代）
  □ 設定每週一自動掃描 104 關鍵職缺
  □ 建立 104 Lead 識別 → LinkedIn 交叉觸達 SOP

Week 10-11：
  □ 三渠道 Lead Pool 統一管理（Asana 加入渠道來源欄位）
  □ 測試三渠道去重規則
  □ A-LI-Tracker 整合三渠道週報

Week 12：
  □ 完整月報覆盤（Jet + Frank）
  □ 確認 MRR 軌跡是否達 NT$ 50,000 目標
  □ 校正三渠道 ICP 評分權重

KPI 目標：月觸達量 ≥ 1,380 封，Demo ≥ 15 場，成交 ≥ 5 個
```

### Phase 4（第 13 週以後）：系統優化與規模化

```
□ 每季校正 ICP 定義（根據成交資料回饋）
□ A/B 測試結果驅動的訊息模板迭代
□ 若 MRR > NT$ 100,000 → 評估加入第二個 LinkedIn 帳號（SDR）
□ 若 Apollo 效果好 → 升級到 Apollo Professional（$99/月，更多資料）
□ 評估是否開啟東南亞市場（新加坡、馬來西亞）
```

---

## Part 9：相關文件索引

| 文件 | 路徑 | 說明 |
|------|------|------|
| LinkedIn 陌生開發 SOP | `sales/linkedin-cold-outreach-sop.md` | ICP、7步觸達、訊息模板 |
| LinkedIn Agent 自動化 | `sales/linkedin-agent-automation.md` | 三個 Agent 規格、KPI |
| CRM 追蹤流程 | `sales/linkedin-crm-tracking-flow.md` | 16狀態機、Gate 0-4 |
| Asana CRM 建置規格 | `sales/linkedin-asana-crm-setup.md` | 10 Section、40欄位、15自動化 |
| Kid 每日操作手冊 | `sales/linkedin-sales-daily-ops.md` | 三時段作業、回覆腳本 |
| Lead 抓取腳本 | `sales/scripts/apify_linkedin_scraper.py` | Apify + LinkedIn |
| 雲端處理引擎 | `sales/scripts/linkedin_processor.py` | ICP評分、草稿生成、回覆分析 |
| **本文件（總綱）** | `sales/outreach-automation-foundation.md` | 三渠道整合架構 ← |
