# S2 — 104 意圖前置法：完整自動化流程設計

**版本：** 1.0  
**日期：** 2026-06-20  
**Owner：** Frank  
**狀態：** 設計階段  
**依賴文件：**
- `02-S2-104-intent.md`（策略邏輯）
- `02-S2-legitimacy-framework.md`（接觸合理性框架 — 話術設計的邏輯依據）
- `07-make-automation-spec.md`（Make Flow 1-3，S1 架構參考）
- `sales/linkedin-asana-crm-setup.md`（Asana CRM 規格）

---

## 一、整體架構概覽

```
┌──────────────────────────────────────────────────────────────────┐
│                       S2 INTENT PIPELINE                          │
│               觸發點：104 / CakeResume 職缺刊登行為                │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Apify          │     │  Thunderbit     │
│  104.com.tw     │     │  CakeResume     │
│  Scraper        │     │  Scraper        │
│  (每日 09:00)   │     │  (每日 09:00)   │
└────────┬────────┘     └────────┬────────┘
         └──────────┬────────────┘
                    │ 合併職缺資料
                    ▼
         ┌──────────────────┐
         │ Make: 關鍵字過濾  │
         │ 高/中意圖分級     │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Apollo.io        │
         │ 公司名稱 →       │
         │ 決策者 Email     │
         │ + LinkedIn URL   │
         └────────┬─────────┘
                  │
                  ▼
         ┌──────────────────┐
         │ Claude API       │
         │ S2 ICP 評分      │
         │ + 個人化話術生成  │
         └────────┬─────────┘
                  │
         ┌────────┴──────────────────┐
         │                           │
         ▼                           ▼
┌─────────────────┐       ┌─────────────────┐
│ Asana           │       │ Dripify         │
│ Task 建立       │       │ Campaign 匯入   │
│ (Lead Pool S00) │       │ (S2 序列)       │
└─────────────────┘       └─────────────────┘
```

---

## 二、工具棧規格

| 工具 | 用途 | 備註 |
|------|------|------|
| **Apify** | 抓取 104.com.tw 職缺（每日排程） | Actor: unfenced-group/taiwan104-scraper |
| **Thunderbit** | 抓取 CakeResume 職缺（Chrome 擴充，半手動） | 暫無排程 API，需手動觸發或 webhook |
| **Make.com** | 流程串接、資料轉換、條件路由 | 新增 Flow 4（S2 專用） |
| **Apollo.io** | 公司名稱 → 決策者 Email + LinkedIn URL | API: `POST /v1/people/search` |
| **Claude API** | 職缺文字分析 + S2 ICP 評分 + 話術生成 | claude-sonnet-4-6，max_tokens: 800 |
| **Asana** | Lead Task 建立（Section 00）+ 策略標籤 S2 | Project GID: 1205513725053633 |
| **Dripify** | LinkedIn 連線請求 + 三封信序列自動發送 | S2 Campaign 獨立建立 |

---

## 三、Make Flow 4：S2 每日職缺意圖掃描

### 觸發條件

- **模組：** Make Scheduler
- **排程：** 每日 09:00（Asia/Taipei，UTC+8）
- **Flow 編號：** Flow 4（接續 07-make-automation-spec.md 的 Flow 1-3）

### 完整流程步驟

```
[Scheduler 09:00]
  → [Step 1: Apify 104 Scraper 啟動]
  → [Step 2: 等待 Apify 完成（Poll）]
  → [Step 3: 取得 104 職缺結果]
  → [Step 4: Thunderbit Webhook 接收 CakeResume 職缺]（異步）
  → [Step 5: 合併 + 去重（by 公司名稱 + 職缺標題）]
  → [Step 6: 關鍵字過濾 + 意圖分級]
  → [Step 7: Apollo.io 公司查詢 → 決策者資料]
  → [Step 8: Claude API — S2 職缺分析 + ICP 評分]
  → [Step 9: 去重檢查（比對 Asana 現有 Lead）]
  → [Step 10: Asana — 批次建立 S2 Lead Tasks]
  → [Step 11: 篩出 A 級 Lead → 生成 Dripify CSV]
  → [Step 12: Google Drive 上傳 CSV]
  → [Step 13: Email 通知 Kid]
```

---

### Step 1：Apify 104 Scraper 啟動

- **模組：** HTTP POST
- **Endpoint：** `https://api.apify.com/v2/acts/unfenced-group~taiwan104-scraper/runs`
- **Headers：** `Authorization: Bearer {{APIFY_TOKEN}}`
- **Body：**
```json
{
  "keywords": "AI,ChatGPT,LLM,生成式AI,流程自動化,RPA,數位轉型,AI助理,AI客服,大語言模型,機器學習,SaaS導入,系統整合",
  "maxResults": 200,
  "location": "台灣",
  "datePosted": "last24hours"
}
```

> **說明：** 每日只抓「過去 24 小時」新刊登職缺，確保 24 小時內觸達的時效性。

---

### Step 2：Poll for Completion（輪詢 104 結果）

- 每 3 分鐘查詢 Run 狀態，最多等待 20 分鐘
- 完成條件：`status === "SUCCEEDED"`
- 逾時處理：告警 Email → frank.kao@insight-software.com

---

### Step 3：取得 104 職缺原始資料

- **Endpoint：** `GET https://api.apify.com/v2/actor-runs/{runId}/dataset/items?token={{APIFY_TOKEN}}&format=json`
- **萃取欄位：**

| 欄位 | Apify 路徑 | 說明 |
|------|-----------|------|
| `company_name` | `custName` | 公司名稱 |
| `job_title` | `jobName` | 職缺標題 |
| `job_desc` | `description` | 職缺描述（含關鍵字分析用） |
| `job_url` | `link` | 104 職缺連結 |
| `posted_date` | `appearDate` | 刊登日期 |
| `company_size` | `employees` | 員工人數範圍 |
| `industry` | `industryDesc` | 產業別 |
| `salary` | `salaryDesc` | 薪資描述 |
| `location` | `jobAddrNoDesc` | 工作地點 |

---

### Step 4：Thunderbit Webhook 接收 CakeResume 職缺（異步）

> **現況說明：** Thunderbit 目前不支援原生排程，採用 Webhook 接收方式：
> - 每日由 Thunderbit Chrome Extension 手動觸發，抓取 CakeResume 關鍵字職缺頁面
> - 資料透過 Thunderbit → Make Webhook 接收
> - **短期過渡方案**：Kid 每日 08:45 手動觸發 Thunderbit，確保資料在 09:00 前就緒

- **Make Webhook URL：** 從 Make 建立 Custom Webhook 模組取得
- **Thunderbit 抓取目標：** `https://www.cake.me/jobs?q=AI&q=ChatGPT&q=自動化&location_list[]=Taiwan`
- **Thunderbit 欄位設定：**

| Thunderbit 欄位名稱 | 對應 CakeResume 欄位 |
|-------------------|-------------------|
| `company_name` | 公司名稱 |
| `job_title` | 職缺標題 |
| `job_desc` | 職務描述 |
| `job_url` | 職缺頁面 URL |
| `posted_date` | 刊登時間 |
| `company_size` | 員工人數（如有顯示）|

---

### Step 5：合併 + 去重

- 將 104 職缺列表 + CakeResume 職缺列表合併為單一陣列
- **去重 Key：** `company_name` + `job_title`（完全相同視為重複）
- 合併後預期每日數量：**30–150 筆**

---

### Step 6：關鍵字過濾 + 意圖分級

Make Filter 模組，依以下規則分級：

**A 級（高意圖，立即觸達）：**
```
job_title 或 job_desc 包含任一：
  AI工具 / ChatGPT / LLM / 生成式AI / Prompt Engineer / AI助理 / AI客服 / 大語言模型
```

**B 級（中意圖，48 小時內觸達）：**
```
job_title 或 job_desc 包含任一：
  流程自動化 / RPA / 數位轉型 / SaaS / 系統整合 / AI / 機器學習 / 智慧化
  但不包含 A 級關鍵字
```

**C 級（低意圖，放入觀察池）：**
```
job_title 或 job_desc 包含任一：
  數位化 / 效率提升 / 降本增效 / 工具整合
  但不包含 A / B 級關鍵字
```

> **過濾後預估：** A 級 5-15 筆 / 日，B 級 10-30 筆 / 日，C 級暫存不處理

---

### Step 7：Apollo.io 公司查詢 → 決策者資料

對每筆 A 級和 B 級職缺，用公司名稱查詢 Apollo.io：

- **Endpoint：** `POST https://api.apollo.io/v1/people/search`
- **Headers：** `x-api-key: {{APOLLO_API_KEY}}`
- **Body：**
```json
{
  "q_organization_name": "{company_name}",
  "person_titles": ["CEO", "執行長", "總經理", "CTO", "IT Director", "VP Engineering", "數位長", "創辦人", "Co-founder", "Director"],
  "organization_locations": ["Taiwan"],
  "per_page": 3
}
```

- **萃取欄位：**

| Apollo 欄位 | 說明 |
|------------|------|
| `first_name` + `last_name` | 決策者姓名 |
| `title` | 職稱 |
| `email` | Email（用於 Apollo Email Sequence，備用） |
| `linkedin_url` | LinkedIn Profile URL（Dripify 主要使用） |
| `organization.estimated_num_employees` | 公司員工數（補充 104 資料）|

> **Apollo 找不到決策者時：** 記錄 `linkedin_url = null`，跳過 Dripify 步驟，仍建立 Asana Task 供 Kid 手動處理。

---

### Step 8：Claude API — S2 職缺分析 + ICP 評分

- **Endpoint：** `https://api.anthropic.com/v1/messages`
- **model：** `claude-sonnet-4-6`
- **max_tokens：** 800
- **temperature：** 0.6

> **設計依據：** 本 Prompt 的話術生成嚴格遵守 `02-S2-legitimacy-framework.md` 的合理性原理——徵才是「狀態證據」非「採購訊號」，訊息必須包含一句「對方會對自己點頭」的中間步驟，且嚴禁出現「正好／剛好」等巧合詞。

**Prompt 模板（Flow 4 專用）：**

```
你是 AirTalk AI Token King 的 S2 Intent 分析 Agent。

【寄件人身份】
所有話術以 Frank（AI Token King 創辦人）的第一人稱撰寫。
Frank 在 LinkedIn 以創辦人身份主動出擊，不是業務人員。
- 對 CTO / 決策者：Frank 以創辦人對管理者的對等姿態對話
- 對 Head of AI / 建造者：Frank 以同樣在 build AI 產品的人提出觀察
- 對工程師：Frank 以「這個工具的建立者」分享給同樣在解決相同問題的人
自我介紹統一為「我是 Frank，AI Token King 的創辦人」，置於 msg1_body 開頭或自然銜接處。

【核心原則：合理性】
徵才行為是「狀態證據」，不是「採購訊號」。你不是因為對方徵才而推銷，
而是從徵才所證明的「狀態」推論出一個下游必然需求——那個需求才是合理理由。
合理性 = 訊息中必須有一句「對方會對自己點頭」的觀察。
嚴禁出現「正好」「剛好」等巧合詞（這是藉口的破綻）。
必須把「對方要徵的人」和「我們的工具」定位為互補，而非取代或無關。

分析以下職缺資訊，完成四項任務：

【職缺資料】
公司名稱：{company_name}
職缺標題：{job_title}
職缺描述：{job_desc}
公司規模：{company_size}
產業別：{industry}
決策者職稱：{decision_maker_title}（Apollo.io 取得，如無填「未知」）

【任務一：合理性閘門（先判斷，不通過則停）】
{
  "gate1_state_evidence": "通過/不通過",   // 訊號是否足以證明「規模化／投資」狀態？單一模糊職缺=不通過
  "gate2_middle_step_valid": "通過/不通過", // 接觸對象的角色是否真的會碰到下游問題？
  "gate3_complementary": "通過/不通過",     // 我們和他要徵的人是否互補（非無關）？
  "gate_result": "PASS/HOLD",              // 三道全過=PASS；任一不過=HOLD（降為觀察池，不生成話術）
  "gate_note": "若 HOLD，說明原因"
}

【任務二：對象判斷（決定用哪套理由）】
依職缺類型與 Apollo 決策者職稱，判斷接觸對象屬於哪一類：
{
  "persona": "建造者/技術人員/治理者",
  // 建造者：AI流程/RPA/應用開發，部門已有人 → 理由=規模化用量治理預警
  // 技術人員：工程師個人，非決策者 → 理由=工程師對工程師的工具分享（禁用商業語言）
  // 治理者：CTO/數位長/技術VP → 理由=投資的另一面是成本治理與ROI
  "persona_reason": "判斷依據（20字內）",
  "middle_step": "對方會對自己點頭的那句話（這是合理性的核心，必須對 persona 的角色為真）"
}

【任務三：S2 ICP 評分（輸出 JSON）】
依以下標準評分，total 最高 100 分：
{
  "intent_score": 0-40,      // 職缺描述對 AI 工具採購意圖的強度：明確採購意圖=40，技術型探索=25，模糊提及=10
  "company_fit": 0-25,       // 公司規模符合度：51-200人=25，11-50人=20，201-500人=15，其他=5
  "decision_maker_reach": 0-20, // 決策者可觸及程度：LinkedIn 可找到+職稱符合=20，有 LinkedIn 但職稱不符=10，找不到=0
  "timing_bonus": 0-15,      // 時機加分：職缺刊登 24 小時內=15，48小時內=10，其他=0
  "total": 以上加總,
  "grade": "A/B/C",          // A≥65, B:40-64, C<40
  "intent_type": "工具採購型/技術建設型/流程優化型/其他",
  "key_signal": "最能說明意圖的 1 句職缺描述原文（直接引用）"
}

【任務四：S2 個人化話術（依 persona 客製，遵守第一段合理性原則）】
話術結構必須是「先講下游問題、後講產品」，且嵌入 middle_step。
{
  "pain_point": "推斷的核心痛點（30字內，須對 persona 角色為真）",
  "product_fit": "AI Token King 對應的解法（30字內）",
  "connection_hook": "LinkedIn 連線請求用語（50字內）。開頭以對職缺的『具體觀察』切入（證明你真的讀過 JD），帶出 middle_step，不出現巧合詞、不直接推銷",
  "msg1_body": "連線接受後第一封訊息（100字內）。順序：① 具體觀察 → ② middle_step（讓他點頭）→ ③ 互補定位 → ④ 一個具體價值點。語氣依 persona：建造者=同行提醒、技術人員=工具分享、治理者=策略對話"
}

【任務五：風險評估】
{
  "risk_flag": "無/低/中/高",
  "risk_reason": "如有風險請說明（例：職缺為純招募無採購意涵、公司規模過小、persona 與理由錯位）"
}

若任務一 gate_result = HOLD，任務四 connection_hook 與 msg1_body 填「（合理性不足，暫不觸達，轉人工判斷）」。
只輸出純 JSON，不要任何額外說明文字。
```

---

### Step 9：Asana 去重檢查

在建立 Task 前，查詢 Asana 確認公司是否已存在：

- **模組：** Asana → Search Tasks
- **搜尋條件：** Project GID `1205513725053633`，notes 包含 `{company_name}` 且 `{job_title}`
- **若已存在：** 跳過建立，在現有 Task 的 C10 備註欄 append 「S2 新職缺訊號：{job_title} / {posted_date}」
- **若不存在：** 進入 Step 10 建立新 Task

---

### Step 10：Asana — 批次建立 S2 Lead Tasks

**Task 命名格式（S2 專用）：**
```
[S2-{grade}-{total}分] {decision_maker_name} | {decision_maker_title} | {company_name}
```

**若無決策者資料（Apollo 未找到）：**
```
[S2-{grade}-{total}分] 待確認 | 待確認 | {company_name}
```

**Task Notes 格式：**
```
=== S2 Intent Lead ===
來源策略：S2（104 意圖前置法）
職缺平台：{104 或 CakeResume}
職缺標題：{job_title}
職缺連結：{job_url}
刊登日期：{posted_date}
意圖類型：{intent_type}
關鍵訊號：{key_signal}

=== 決策者資訊 ===
姓名：{decision_maker_name}（或「待確認」）
職稱：{decision_maker_title}（或「待確認」）
LinkedIn URL：{linkedin_url}（或「待確認」）
Email：{email}（或「未取得」）
公司名稱：{company_name}
公司規模：{company_size}
產業別：{industry}

=== S2 ICP 評分 ===
意圖強度：{intent_score}/40
公司符合度：{company_fit}/25
決策者可觸及：{decision_maker_reach}/20
時機加分：{timing_bonus}/15
ICP 總分：{total}/100
等級：{grade}

=== S2 合理性與對象 ===
合理性閘門：{gate_result}（{gate_note}）
接觸對象類型：{persona}（{persona_reason}）
中間步驟（點頭句）：{middle_step}

=== S2 話術素材 ===
核心痛點：{pain_point}
產品對應：{product_fit}
連線請求話術：{connection_hook}
第一封訊息草稿：{msg1_body}

=== 風險評估 ===
風險等級：{risk_flag}
風險說明：{risk_reason}

Lead 來源：Scout 自動（S2-104）
建立時間：{YYYY-MM-DD HH:MM}
```

**Custom Fields 填入（對應 linkedin-asana-crm-setup.md）：**

| Custom Field | 填入值 |
|-------------|--------|
| A1 Lead ID | `ATK-{YYYYMM}-{自動序號}` |
| A2 姓名 | {decision_maker_name} |
| A3 職稱 | {decision_maker_title} |
| A4 公司名稱 | {company_name} |
| A5 公司規模 | 對應 A5 選項 |
| A6 行業別 | 對應 A6 選項 |
| A7 LinkedIn URL | {linkedin_url} |
| A8 Lead 來源 | `Scout 自動` |
| B1 ICP 總分 | {total} |
| B5 訊號強度分數 | {intent_score}（取整數，max 25） |
| B8 HOT/WARM/COLD | ≥65=HOT，40-64=WARM，<40=COLD |
| **新增欄位** | **S2 策略標籤** = `S2-104` 或 `S2-CakeResume` |

---

### Step 11：篩出 A 級 Lead → 生成 Dripify CSV

只有 **grade = A**（ICP ≥ 65）且 **linkedin_url 不為空** 的 Lead 進入 Dripify：

**CSV 格式（對應 Dripify 匯入欄位）：**
```csv
firstname,lastname,occupation,companyName,linkedinUrl,custom1,custom2,custom3
{firstName},{lastName},{title},{company},{linkedinUrl},{connection_hook},{msg1_body},{job_title}
```

| 欄位 | Dripify 對應 | 說明 |
|------|------------|------|
| `custom1` | 連線請求附加訊息（Note） | S2 connection_hook 話術 |
| `custom2` | 第一封訊息（Message 1） | S2 msg1_body |
| `custom3` | 備用欄位 | 職缺標題（供後續 follow-up 個人化） |

---

### Step 12：Google Drive 上傳

- **資料夾：** AirTalk / S2 每日意圖名單
- **檔名：** `s2-intent-leads-{YYYY-MM-DD}.csv`
- **同時：** 將 B 級 Lead 另存 `s2-intent-watch-{YYYY-MM-DD}.csv`（供 Kid 人工判斷）

---

### Step 13：Email 通知 Kid

```
主旨：[AirTalk S2] 今日職缺意圖名單 — {YYYY-MM-DD}（A級 {N} 筆）

今日 104 + CakeResume 掃描完成。

【A 級 Lead（立即觸達）：{N} 筆】
已匯入 Dripify S2 Campaign，LinkedIn 序列將在 30 分鐘內啟動。
Asana Lead Pool 已建立對應 Task，請確認話術是否需調整。

【B 級 Lead（48 小時內觸達）：{M} 筆】
附件：s2-intent-watch-{YYYY-MM-DD}.csv
請人工判斷後手動加入 Dripify 或標記為 C 級。

【今日掃描摘要】
104 新職缺總數：{total_104} 筆
CakeResume 新職缺：{total_cake} 筆
過濾後 A 級：{N} 筆 / B 級：{M} 筆 / C 級（略過）：{P} 筆
Apollo 決策者找到率：{found}/{N+M} = {%}

Google Drive：{folder_link}
```

---

## 四、Dripify S2 Campaign 設定規格

### Campaign 命名規範
```
AirTalk S2 — 104 Intent — {YYYY-WW}（例：AirTalk S2 — 104 Intent — 2026-W25）
```

### 話術合理性原則（所有序列共用）

> 完整邏輯見 `02-S2-legitimacy-framework.md`。以下範本一律遵守：
> 1. **不出現「正好／剛好」等巧合詞**——這是藉口的破綻。
> 2. **先講下游問題、後講產品**——每封訊息嵌入一句「對方會對自己點頭」的中間步驟。
> 3. **互補定位**——把「對方要徵的人」和「我們的工具」框成互補，不是取代或無關。
> 4. **依對象（persona）切換語氣**——建造者＝同行提醒、技術人員＝工具分享、治理者＝策略對話。

實際 D0/D3 話術由 Claude（Step 8）依 persona 生成並帶入 `custom1`/`custom2`。以下為三種對象的**範本示意**，供 Prompt 校準與 Kid 手動微調參考。

---

### 範本 A｜對象＝建造者（AI 流程／開發部門主管）

**D0 連線請求（嵌入「規模化用量治理」的點頭句）**
```
{名字} 您好，看到貴團隊在擴編 AI 流程自動化的人手——通常團隊一擴大、同時跑的 AI 流程一多，API 用量就會開始分散、難追蹤。我們在幫台灣團隊處理這一塊，想跟您交流經驗。
```

**D3 連線接受後第一封（觀察 → 點頭句 → 互補 → 價值點）**
```
{名字} 您好，感謝接受連線！

我是 Frank，AI Token King 的創辦人。

看到你們在徵 {職缺名稱}，推測 AI 流程已經從試做走向多人、多專案同時上線。這個階段最常見的不是技術問題，而是「誰用了多少 token、哪個流程在燒錢」變得難掌握。

AI Token King 就是把這層用量管理先做好——你們新徵的工程師到職後可以直接用，不必自己花時間造一套監控。

如果這塊現在還沒有現成方案，要不要 5 分鐘聊聊你們的做法？
```

---

### 範本 B｜對象＝技術人員（工程師，工具分享語氣，禁商業語言）

**D0 連線請求**
```
{名字} 您好，看到你們團隊在做 AI 應用開發。我們也在這條路上，做了一個管理多個 LLM key 跟 token 用量的小工具，想跟同樣在實作的人交流一下。
```

**D3 連線接受後第一封**
```
{名字} 您好，感謝接受連線！

我是 Frank，AI Token King 這個工具的建立者。

同樣在做 LLM 應用，不知道你們會不會也遇到這些雜事：多個模型的 key 要分開管、想知道哪個實驗燒了多少 token、有時一個測試不小心把額度用爆。

我們做了 AI Token King 來解決這些——可以直接免費試，不用改你現有的程式，掛上去就能看用量。

如果你有空玩玩，很歡迎給我們技術上的回饋：aitokenking.com.tw
```

---

### 範本 C｜對象＝治理者（CTO／數位長，策略對話語氣）

**D0 連線請求**
```
{名字} 您好，看到貴公司正在投資擴建 AI 團隊。對管理者來說，投資的另一面通常是治理——多個團隊用不同 AI 工具時，成本怎麼看清楚、怎麼控管。這正是我們在處理的題目，想與您交流。
```

**D3 連線接受後第一封**
```
{名字} 您好，感謝接受連線！

我是 Frank，AI Token King 的創辦人。

從你們持續徵 AI 人才來看，這塊的投入是認真的。多數管理者在這個階段會開始問同一個問題：這些 AI 工具的錢花得值不值、各團隊的用量我有沒有可見度。

AI Token King 提供的就是這層治理視角——把 Claude / ChatGPT / Gemini 等多個 LLM 的用量與成本集中到一個地方，讓你在擴張的同時守得住預算。

如果這是你近期會關心的議題，方便安排 15 分鐘聊聊嗎？
```

---

### 後續追蹤（D7 / D14，三種對象共用骨架，語氣依 persona 微調）

**D7：第一封未回覆後追蹤（以「具體案例」延續合理性，不重複推銷）**
```
{名字} 您好，接續上次的訊息——我們最近協助一家規模相近的台灣團隊，解決了 AI API 用量失控的狀況：他們原本每月用量超出預算約 40%，導入後在不影響各團隊使用彈性的前提下，回到可控範圍。

如果你們在 AI 投入加大的過程中也在意這塊，或許值得 15 分鐘交流一下他們的做法。
```

**D14：第二封未回覆後追蹤（降壓收尾，留時機）**
```
{名字} 您好，知道大家都忙，這封就當作輕量的收尾：

AI Token King 提供 14 天免費試用，免信用卡、不需更動現有工具，掛上去就能直接看到貴團隊各 AI 工具的 token 用量：aitokenking.com.tw

現在時機未到也完全沒關係，之後有需要隨時找我。

Frank｜AI Token King 創辦人
```

### Dripify 進階設定

| 設定項目 | 值 |
|---------|---|
| Campaign 類型 | Drip Sequence |
| 每日連線上限 | 15 筆（與 S1 共用帳號配額，S2 優先分配 8 筆）|
| 發送時間 | 週一至週五 09:00-17:00（台灣時間）|
| 若連線被拒絕 | 自動結束序列，Asana 更新 C4 = 已拒絕 |
| 若連線超過 7 天未接受 | 序列暫停，Asana 移至 Section 09 |

---

## 五、S2 ICP 評分差異說明（vs S1）

S2 的評分邏輯與 S1 的 `07-make-automation-spec.md Flow 3` 不同，因為 **S2 的核心訊號是「職缺行為」而非「個人 LinkedIn 訊號」**：

| 評分維度 | S1 標準 | S2 標準 | 差異說明 |
|---------|--------|--------|---------|
| 訊號強度（B5） | LinkedIn 貼文/職稱/AI關鍵字 | 職缺描述中的 AI 採購意圖強度 | S2 直接用職缺判斷，訊號更明確 |
| 職稱決策力（B4） | CEO/CTO 等職稱（25分） | 決策者可觸及程度（20分） | S2 先有公司訊號，決策者需二次查找 |
| 時機加分（新增） | 無 | 職缺刊登時效（+15分）| S2 的核心優勢：24 小時搶先窗口 |
| 公司符合度（B2） | 員工人數範圍 | 同 S1 | 一致 |

**A 級觸發閾值：** S2 ≥ 65 分（S1 為 ≥ 45 分）
→ S2 因職缺訊號明確，閾值應更高，確保 A 級 Lead 品質。

---

## 六、異常處理規則

| 異常情境 | 處理方式 |
|---------|----------|
| Apify 104 Scraper 返回 0 筆 | 告警 Email → frank.kao@insight-software.com，標注「今日 104 爬蟲無結果，請確認關鍵字設定」 |
| Apollo.io 找不到任何決策者 | 仍建立 Asana Task，A7 填「待人工查詢」，B8 = COLD，Kid 手動在 LinkedIn 搜尋 |
| Claude API 分析失敗 | 跳過評分，仍建立基礎 Task，Claude 分析欄位標注「待人工補充」，通知 Kid |
| 每日 A 級 Lead > 20 筆 | 只取 ICP 前 15 名進入 Dripify（避免當日配額超出），其餘排隊次日處理 |
| Thunderbit 當日未手動觸發 | Make 在 09:05 偵測 CakeResume Webhook 無資料，自動補送提醒 Email 給 Kid |
| 公司已在 Asana 有 Task | 不建立重複 Task，在現有 Task C10 備註欄 append 新職缺訊號（記錄持續意圖）|

---

## 七、KPI 與監控

| 指標 | 目標 | 監控方式 |
|------|------|---------|
| 每日職缺掃描量（A+B+C 合計） | ≥ 30 筆/日 | Make 執行日誌 |
| A 級 Lead 識別率 | ≥ 5 筆/日 | Step 13 Email 摘要 |
| Apollo 決策者找到率 | ≥ 60% | Step 13 Email 摘要 |
| S2 連線接受率 | ≥ 35%（目標，因有具體切入點）| Dripify Campaign Analytics |
| S2 有效回覆率（含 D7/D14） | ≥ 20% | Dripify + Asana |
| 24 小時觸達率（A 級 Lead） | ≥ 90% | 職缺刊登時間 vs Dripify 發送時間 |

---

## 八、環境變數（新增項目）

在 `07-make-automation-spec.md` 的環境變數基礎上，S2 Flow 需額外設定：

| 變數名稱 | 說明 | 取得方式 |
|---------|------|---------|
| `APIFY_ACTOR_104` | 固定值：`unfenced-group~taiwan104-scraper` | Apify Actor Store |
| `APOLLO_API_KEY` | Apollo.io API 金鑰 | Apollo → Settings → Integrations → API |
| `S2_MAKE_WEBHOOK_URL` | Thunderbit → Make 的 Webhook 接收網址 | Make → Custom Webhook 模組 |
| `DRIPIFY_CAMPAIGN_S2_ID` | S2 Campaign 的 Dripify ID | Dripify → Campaigns → {Campaign ID} |
| `GOOGLE_DRIVE_S2_FOLDER_ID` | S2 每日名單的 Google Drive 資料夾 ID | Google Drive 資料夾 URL 末段 |

---

## 九、實作優先順序（建議）

| 階段 | 項目 | 負責人 | 預計完成 |
|------|------|--------|---------|
| Phase 1 | Apify 104 Scraper 測試（手動執行，驗證資料品質）| Tommy | Week 1 |
| Phase 1 | Make Flow 4 基礎架構（Steps 1-6 關鍵字過濾）| Tommy | Week 1 |
| Phase 2 | Apollo.io API 串接（Step 7）| Tommy | Week 2 |
| Phase 2 | Claude S2 Prompt 測試與調校（Step 8）| Frank + Tommy | Week 2 |
| Phase 3 | Asana Task 自動建立（Steps 9-10）| Tommy | Week 3 |
| Phase 3 | Dripify S2 Campaign 建立 + CSV 匯入測試（Steps 11-13）| Kid + Tommy | Week 3 |
| Phase 4 | Thunderbit CakeResume 整合（Step 4）| Kid（操作）+ Tommy（Webhook）| Week 4 |
| Phase 4 | 全流程端對端測試 + KPI 基準建立 | Frank + Tommy + Kid | Week 4 |

---

*文件版本：1.0 | 建立日期：2026-06-20 | Owner：Frank*
