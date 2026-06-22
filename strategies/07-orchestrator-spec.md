# Orchestrator Agent 技術規格

**文件代號：** 07-orchestrator-spec  
**版本：** v2.0（混合架構）  
**建立日期：** 2026-06-09  
**更新日期：** 2026-06-10  
**負責人：** Frank × Edwin（系統實作）  

---

## 一、系統定位

Orchestrator Agent 是四套 LinkedIn 開發策略的每日排程中心。

每天 09:00 自動啟動，完成：
1. 雲端部分：104 掃描、LinkedIn 資料抓取（Apify）、Heat Score 計算、去重、Asana 寫入、簡報生成
2. 地端部分：LinkedIn 實際操作（連線邀請、私訊、社群評論）

**核心設計原則：人只需要在 09:30 看一份簡報，做一個決定。**

---

## 二、為什麼需要混合架構

LinkedIn 有兩層封鎖機制，純雲端方案無法繞過：

| 封鎖層次 | 問題 | 原因 |
|---------|------|------|
| **IP 層** | GitHub Actions / AWS 等 Datacenter IP 被 LinkedIn 直接封鎖 | LinkedIn 維護 Datacenter IP 黑名單 |
| **帳號 Session 層** | 從未登入過的環境突然操作帳號，觸發異常警報 | LinkedIn 追蹤裝置指紋與登入地點 |

**地端可以穩定運作的原因：** 同一台電腦、同一組住宅 IP（Residential IP）長期登入，session 是被 LinkedIn 信任的環境。

**解法：** 只把「需要 LinkedIn 帳號操作」的部分留在地端，其餘全部雲端處理。

---

## 三、混合架構全景

```
08:55 — GitHub Actions 觸發（UTC 00:55 = TST 08:55）
           │
           ├── [雲端] 104 職缺掃描（S2-Agent）
           │     └── 無需登入，完全沒有 IP 問題
           │
           ├── [雲端] LinkedIn 資料抓取（S1 / S6 / S5 情報蒐集）
           │     └── 透過 Apify Residential Proxy 解決 IP 問題
           │         → apify_linkedin_scraper.py（已有）
           │
           ├── [雲端] Heat Score 計算 + Lead 去重
           │     └── asana_dedup.py（已有）
           │
           ├── [雲端] Asana 任務寫入
           │     └── 新增 Task / 更新已有 Task / Comment
           │
09:10 — [雲端] 每日簡報生成 → 寄送至 Frank（Gmail）
           │     包含：今日 A 級 Lead 清單 + 話術草稿 + Dripify 匯入檔
           │
           └── [雲端] 產出 Dripify CSV → 上傳至 Dropbox / Google Drive
                     （地端的觸發點）

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

09:00 — 地端 cron 啟動（Mac / Windows 排程器）
           │
           ├── 從 Dropbox / Google Drive 下載今日 Dripify CSV
           │
           ├── 匯入 Dripify → 執行連線邀請 / 私訊序列
           │     └── Dripify 從本機瀏覽器 session 操作，LinkedIn 視為正常人類行為
           │
           ├── S5 社群評論（地端執行）
           │     └── 從雲端下載今日評論草稿 → 人工確認後發出（或半自動）
           │
09:25 — 地端回報完成狀態 → POST webhook → 更新 Asana Task 狀態
```

---

## 四、雲端元件規格（GitHub Actions）

### 觸發設定

```yaml
# .github/workflows/linkedin-orchestrator.yml

name: LinkedIn Orchestrator Daily
on:
  schedule:
    - cron: '55 0 * * 1-5'  # UTC 00:55 = TST 09:05（週一至週五）
  workflow_dispatch:           # 允許手動觸發

jobs:
  orchestrate:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4
      - name: Run Orchestrator
        env:
          APIFY_TOKEN: ${{ secrets.APIFY_TOKEN }}
          ASANA_TOKEN: ${{ secrets.ASANA_TOKEN }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GMAIL_CREDENTIALS: ${{ secrets.GMAIL_CREDENTIALS }}
          DROPBOX_TOKEN: ${{ secrets.DROPBOX_TOKEN }}
        run: python orchestrator/main.py
```

### 雲端執行的四支 Sub-Agent

**S2-Agent（104 掃描）— 完全雲端，無限制**

```yaml
trigger: github_actions_cron
task:
  - 掃描 104 新職缺（關鍵字過濾）
  - 比對 Asana 已有公司（去重）
  - 定位 LinkedIn 決策者（Apify 抓取公司 LinkedIn 頁面）
  - 產出 Lead JSON
execution_env: cloud_only
ip_requirement: none  # 104 無需 LinkedIn session
```

**S1-Agent（情報蒐集部分）— Apify Residential Proxy**

```yaml
trigger: github_actions_cron
task:
  - 根據 ICP 條件，從 LinkedIn 搜尋新目標（Apify）
  - 抓取目標的 About / 最近貼文 / 職稱轉變（Apify）
  - Claude Agent 判斷 AI 使用者類型（A/B/C/D）
  - 產出個人化話術草稿
  - 產出 Dripify CSV（連線邀請欄位填好）
execution_env: cloud_apify
ip_requirement: residential_proxy  # Apify 處理
note: "只做資料蒐集 + 草稿生成，實際發送在地端"
```

**S6-Agent（競品信號掃描）— Apify Residential Proxy**

```yaml
trigger: github_actions_cron
task:
  - 掃描 104 職缺中的競品關鍵字
  - 掃描 LinkedIn 貼文 / 技能欄位中的競品使用信號（Apify）
  - 比對競品痛點速查表
  - 產出個人化話術草稿 + Dripify CSV
execution_env: cloud_apify
ip_requirement: residential_proxy
```

**S5-Agent（社群情報蒐集）— Apify Residential Proxy**

```yaml
trigger: github_actions_cron
task:
  - 掃描目標社群的昨日熱門貼文（Apify）
  - 識別符合 ICP 的活躍成員
  - 生成今日評論草稿（JSON 格式，地端人工確認）
  - 識別已有重複互動者 → 升格為 Lead
execution_env: cloud_apify
ip_requirement: residential_proxy
note: "評論草稿在地端確認後發出，不在雲端自動發送"
```

---

## 五、地端元件規格

### 觸發方式

**Mac（launchd）**

```xml
<!-- ~/Library/LaunchAgents/com.airtalk.linkedin.plist -->
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.airtalk.linkedin</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/[你的帳號]/airtalk/local_runner.py</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
</dict>
</plist>
```

**Windows（工作排程器）**

```
觸發器：每天 09:00
動作：python C:\airtalk\local_runner.py
條件：只有電腦開機時才執行（若電腦未開機，下次開機時補跑）
```

### 地端執行流程（`local_runner.py`）

```python
# 偽代碼，說明邏輯

def run():
    # Step 1：等雲端作業完成（最多等到 09:15）
    wait_for_cloud_ready(timeout=900)

    # Step 2：下載今日產出
    dripify_csv = download_from_dropbox("today_dripify.csv")
    comment_drafts = download_from_dropbox("today_comments.json")

    # Step 3：匯入 Dripify
    dripify_import(dripify_csv)
    print(f"已匯入 {len(dripify_csv)} 筆 Lead 至 Dripify")

    # Step 4：顯示評論草稿（等人工確認）
    # 若設定 auto_comment=True，直接發出
    show_comment_drafts(comment_drafts)

    # Step 5：回報完成狀態至 Asana
    webhook_notify_asana(status="local_tasks_dispatched")
```

---

## 六、Lead 資料格式（不變）

每支 Sub-Agent 回傳統一格式：

```json
{
  "lead_id": "LI-20260609-0042",
  "name": "陳志明",
  "title": "業務總監",
  "company": "瑞泰科技",
  "linkedin_url": "https://linkedin.com/in/...",
  "source_strategy": ["S1", "S6"],
  "ai_user_type": "B",
  "heat_score": 0,
  "development_logic": "從傳統製造業業務轉型，現負責公司數位化採購，職涯往管理層發展",
  "pain_point": "現有工具缺乏中文場景支援",
  "recommended_angle": "成為他在 AI 工具選型上的風險把關者",
  "action": {
    "type": "connection_request",
    "draft": "陳志明你好，看到你在瑞泰科技負責業務數位化...",
    "priority": "A",
    "due": "2026-06-09",
    "execution_env": "local_dripify"
  },
  "asana_task_id": null,
  "created_at": "2026-06-09T09:18:00+08:00"
}
```

---

## 七、熱度評分引擎（Heat Score）

每筆 Lead 在 Dedup 後進行熱度評分，決定今日執行優先序。

### 計分規則

| 條件 | 加分 |
|------|------|
| 來自兩套以上策略同時識別 | +30 |
| S2：職缺刊登在 7 天內 | +25 |
| S6：競品有近期漲價 / 功能異動訊號 | +25 |
| S6：目標對象最近有抱怨競品的公開貼文 | +20 |
| S5：已有 2 次以上社群互動記錄 | +20 |
| S1：目標對象最近 30 天有發文（活躍） | +10 |
| AI 使用者類型為 D（組織決策者） | +15 |
| AI 使用者類型為 B（效率優化者） | +10 |
| 公司規模 50–200 人（甜蜜區間） | +10 |
| 職稱為 CEO / 創辦人 / 執行長 | +10 |

### 優先級分類

| Heat Score | 優先級 | 當日行動 |
|-----------|--------|---------|
| ≥ 70 | A 級 | 今日地端 Dripify 執行 |
| 40–69 | B 級 | 本週執行 |
| < 40 | C 級 | 放入觀察池 |

---

## 八、Asana 任務寫入規格

### Project 結構

```
Asana Project：LinkedIn 開發 — [月份]
  ├── Section：🔴 A 級（今日）
  ├── Section：🟡 B 級（本週）
  ├── Section：⚪ 觀察池
  ├── Section：✅ 已回覆
  └── Section：❌ 無回應 > 21 天
```

### Task 欄位對應

| Asana 欄位 | 對應資料 |
|-----------|---------|
| Task 名稱 | `[姓名] @ [公司] — [策略代號]` |
| 負責人 | Kid（預設） |
| 截止日 | `action.due` |
| 描述 | `development_logic` + `recommended_angle` + 話術草稿 |
| 自訂欄位：Heat Score | `heat_score` |
| 自訂欄位：AI 使用者類型 | `ai_user_type` |
| 自訂欄位：策略來源 | `source_strategy`（多選） |
| 自訂欄位：聯絡階段 | 連線未發 / 等待接受 / 第一封 / 第二封 / 第三封 / 進入 Demo |
| 自訂欄位：執行環境 | 雲端自動 / 地端 Dripify / 人工確認 |

### 去重邏輯

```
IF lead.linkedin_url already exists in Asana:
  → 不新增 Task，只更新 heat_score 與 source_strategy
  → 新增 Comment：「[日期] 被 [策略代號] 再次識別，Heat Score 更新為 [X]」
ELSE:
  → 新增 Task
```

---

## 九、每日簡報格式

每天 09:10 由雲端發送至 Frank（frank.kao@insight-software.com）。

```
📊 LinkedIn 開發 — 每日簡報 [日期]

━━━━━━━━━━━━━━━━━━━━
今日新增 Lead

🔴 A 級（今日 Dripify 執行）：X 筆
🟡 B 級（本週執行）：X 筆
⚪ 觀察池：X 筆

━━━━━━━━━━━━━━━━━━━━
A 級 Lead 摘要

1. [姓名] @ [公司]
   來源：S2 + S6 ｜ 類型：B ｜ Heat：85
   切入點：[一句話摘要]
   Asana Task：[連結]

2. ...

━━━━━━━━━━━━━━━━━━━━
今日地端任務（09:00 自動執行）

• Dripify 匯入：X 筆（已自動執行）
• S5 評論草稿：X 則（需人工確認後發出）
• 需 Kid 介入的例外：[若有]

━━━━━━━━━━━━━━━━━━━━
累計追蹤

本週觸達：X 人 ｜ 回覆：X 人（回覆率 X%）
本月 Demo 預約：X 場
```

---

## 十、每日配額管理（LinkedIn 節流）

| 操作類型 | 每日上限 | 執行環境 | 分配方式 |
|---------|---------|---------|---------|
| 連線邀請發送 | 20 封 | 地端 Dripify | S1: 10 / S2: 6 / S6: 4 |
| 私訊發送 | 30 封 | 地端 Dripify | 依優先級排序發完為止 |
| 社群評論 | 無限制 | 地端人工確認 | S5: 5 則（品質控制） |

超過配額的 A 級 Lead → 自動順延至隔日，不降級。

---

## 十一、例外處理

| 例外狀況 | 處理方式 |
|---------|---------|
| GitHub Actions 超時（> 30 分鐘） | 記錄錯誤，已完成的部分照常寫入 Asana，簡報標注未完成項目 |
| Apify 配額耗盡 | 跳過 LinkedIn 抓取，只執行 104 掃描，簡報標注 |
| Asana API 連線失敗 | Lead List 暫存本地 JSON，下次執行時補寫 |
| 地端電腦未開機（09:00） | local_runner.py 開機後自動補跑（當天內有效） |
| 地端電腦未開機（整天） | 當日地端任務跳過，Asana Task 狀態保持「連線未發」，明日繼續 |
| 同一目標在 7 天內被觸達過 | 自動跳過，記錄至 Asana Comment |
| LinkedIn 帳號觸發異常警報 | 立即停止地端操作，通知 Frank，等 24 小時後再啟動 |

---

## 十二、技術棧總覽

| 元件 | 方案 | 執行環境 |
|------|------|---------|
| 排程觸發（雲端） | GitHub Actions cron | 雲端 |
| 排程觸發（地端） | Mac launchd / Windows 工作排程器 | 地端 |
| Orchestrator 主程式 | Python + Claude API | 雲端 |
| LinkedIn 資料抓取 | Apify（Residential Proxy） | 雲端 |
| 104 職缺掃描 | Apify 104 Scraper / 直接 HTTP | 雲端 |
| LinkedIn 操作執行 | Dripify（從地端匯入 CSV） | 地端 |
| 社群評論 | 地端人工確認後發出 | 地端 |
| Asana 寫入 | Asana MCP Server | 雲端 |
| 每日簡報發送 | Gmail MCP Server | 雲端 |
| 地端 ↔ 雲端資料交換 | Dropbox / Google Drive | 雙向 |

---

## 十三、啟動順序（Phase 0 MVP）

```
Week 1：雲端管道打通
  → GitHub Actions + S2-Agent（104 掃描）+ Asana 寫入 + 簡報 Email
  → 驗證：每天收到簡報，Asana 有新 Task

Week 2：Apify 接入 + 地端 Dripify 手動匯入
  → S1-Agent 加入，雲端產出 CSV，人工匯入 Dripify 測試
  → 驗證：CSV 格式正確，Dripify 能正常執行連線邀請

Week 3：地端 cron 自動化
  → local_runner.py 設定 launchd / 工作排程器
  → 驗證：09:00 自動下載 CSV 並匯入 Dripify，無需人工介入

Week 4：S6 + S5 加入，完整四套並行
  → 驗證去重邏輯、Heat Score 排序是否符合預期
```

---

### 相關現有程式碼

| 檔案 | 用途 |
|------|------|
| `projects/aitokenking/sales/scripts/apify_linkedin_scraper.py` | LinkedIn 資料抓取（Apify） |
| `projects/aitokenking/sales/scripts/asana_dedup.py` | Asana 去重邏輯（可直接複用） |
| `projects/aitokenking/sales/scripts/linkedin_processor.py` | Lead 處理流程 |
| `projects/aitokenking/sales/scripts/dripify_export.py` | 產出 Dripify CSV（已有） |

---

*文件版本：v2.0（混合架構）｜ v1.0 → v2.0 更新：LinkedIn 操作改為地端 Dripify 執行，雲端只做資料蒐集與分析*
