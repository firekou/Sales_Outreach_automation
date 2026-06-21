# Sales Outreach Automation

AI Token King — LinkedIn 自動化陌生開發系統  
產品：[aitokenking.com.tw](https://aitokenking.com.tw)  
管理：Frank / Kid / Lauren

---

## 系統架構

```
四套並行策略 (S1 / S2 / S5 / S6)
         ↓
  Claude Agent 分析 + 三封信生成
         ↓
  Apify Scraper → ICP 評分 → Dripify CSV
         ↓
  Asana CRM 追蹤 → Ali Auditor 稽核
```

---

## 目錄結構

| 目錄 | 說明 |
|------|------|
| `.claude/agents/` | Claude Sub-agent 定義（S1 業務、稽核、Kid Sales） |
| `strategies/` | 四套 LinkedIn 開發策略 + 話術 + 自動化規格 |
| `sales/` | Sales Playbook、CRM 設定、每日 Ops SOP |
| `linkedin-outreach/` | Sales Agent 架構規格、TA Matrix、Phase 1 MVP |
| `scripts/` | Python 自動化腳本（Apify / Claude / Asana / Dripify） |
| `lead-drafts/` | 已分析 Lead 資料與 Dripify 草稿 |

---

## Claude Agents

| Agent | 用途 |
|-------|------|
| `Outreach-Sensei` | 世界頂級 Outreach 大師顧問：理論拆解 + Skill Roadmap + 精細化設計指導 |
| `AirTalk-S1-BizDev` | 深度 Lead 分析 + 三封信序列生成 |
| `Reply-Router` | 回覆分流 × 接球草稿生成器（P0 Skill）：意圖分類 + 路由建議 + 個人化接球草稿 |
| `ALI-Auditor` | 七層稽核 + 週報 + 回覆真實性評分 |
| `Kid-Sales` | 業務執行、客戶維護、收款 |

---

## 四套策略速查

| 代號 | 策略 | 觸發點 |
|------|------|--------|
| S1 | 直攻法 | 主動搜尋 ICP 目標 |
| S2 | 104 意圖前置法 | 職缺刊登行為偵測 |
| S5 | 社群潛伏法 | LinkedIn 社群共同成員 |
| S6 | 競品替換法 | 競品使用信號 |

詳細見 `strategies/` 目錄。

---

## 快速啟動

```bash
cd scripts/
cp .env.example .env
# 填入 APIFY_TOKEN, ANTHROPIC_API_KEY, ASANA_TOKEN

pip install -r requirements.txt

# 每日執行
python apify_linkedin_scraper.py    # 抓 Lead
python linkedin_processor.py        # ICP 評分 + 草稿生成
python asana_dedup.py               # 去重
python dripify_export.py            # 匯出 Dripify CSV
```

詳細見 `scripts/HOWTO.md`。

---

## AI 使用者類型分類

| Type | 名稱 | 核心恐懼 | 話術框架 |
|------|------|----------|----------|
| A | 身份建構者 | 被時代淘汰 | 「成為行業裡最早用好 AI 的人」 |
| B | 效率優化者 | 工具引進後出問題 | 「讓成果更可預測、可追蹤」 |
| C | 影響力建構者 | 競爭者用 AI 已在產出 | 「觀點生產速度和傳播深度同時提升」 |
| D | 組織決策者 | 做了錯誤工具選擇 | 「AI 導入決策有依據、有框架、有成果」 |
