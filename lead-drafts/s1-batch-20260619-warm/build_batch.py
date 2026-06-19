#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S1 直攻法 — 2026-06-19 WARM 補批產生器（單一真實來源）

目的：補上第一批 HOT 缺少的 Type A（身份建構者）話術組合。
從既有抓取名單 (scripts/output/leads_v2_20260603.csv) 的 56 筆 WARM 中精選 5 筆，
覆蓋 A / A / B / C / D，結合本檔手寫的深度分析與三封信序列，產出 MD + Expandi CSV。

執行：python lead-drafts/s1-batch-20260619-warm/build_batch.py
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEADS_CSV = ROOT / "scripts" / "output" / "leads_v2_20260603.csv"
OUT_DIR = Path(__file__).resolve().parent
ACCOUNT = "frank"

BATCH = {
    "Tina Yi Ching Chen": {
        "slug": "lead-01-tina-chen",
        "first": "Tina", "last": "Chen",
        "ai_type": "A（身份建構者）",
        "dev_logic": "在以製造為本的傳統紡織/織帶公司 E.C.I. 扛起 B2B/B2C 數位轉型與 SEO/AEO 前沿佈局——她正在把自己重新定義成「傳統製造業裡最懂數位與 AI 的那個人」。",
        "turning_point": "從傳統紡織行銷跨到『數位轉型推手』身份——在一個不被視為數位的產業裡建立全新標籤。",
        "next_step": "讓紡織供應鏈的數位/AI 創新做出可見成果，鞏固『傳統產業數位轉型代表人物』的定位。",
        "pain": "怕在傳統產業推數位轉型『孤軍奮戰、做半套』；轉型若沒做出來，新身份就站不住，前沿性也沒人看見。",
        "angle": "成為她『在傳統製造業把 AI 轉型做成可展示成果』的裝備提供者，讓轉型宣告變成有系統的方法論。",
        "hook": "她在製造為本的紡織業裡做 SEO/AEO 與供應鏈數位創新——傳統產業數位先行者，要的是『成為行業裡最早用好 AI 的人』。",
        "connection": "Tina 你好，看到你在 E.C.I. 帶紡織供應鏈的數位轉型，還做到 SEO/AEO 這種前沿的搜尋佈局——說實話，在以製造為本的傳統產業裡推這些，比在數位原生公司難太多，也更少人做得起來。我在做企業 AI 導入，特別佩服在傳統產業裡真的把數位做出來的人。想跟你連結交流，Frank。",
        "day1": [
            "Tina 謝謝你接受連結。",
            "我最近在觀察傳統製造業的數位轉型，發現一個很真實的現象：真正在推的人，往往是公司裡少數的「先行者」，能力跟視野都夠，但最大的挑戰不是自己會不會，而是怎麼讓整個組織、甚至供應鏈上下游跟得上，不是只有你一個人在前面跑。",
            "想請教你：以你在 E.C.I. 推數位/AI 的經驗，這種「先行者的孤獨」對你來說是不是真的存在？你都怎麼帶其他人？",
            "純粹好奇，沒有要推銷。Frank",
        ],
        "day57_reply": [
            "謝謝你的分享，你說的（複述他提到的觀點）我特別有感——在傳統產業當數位先行者，最難的真的是那個「把自己看到的，變成別人也能用的」過程。",
            "我最近整理了一些「傳統製造業出身的人，怎麼把 AI 變成自己可展示的轉型成果」的案例，重點不是工具，是怎麼讓你的前沿性被看見、被組織複製。",
            "不是廠商案例，是實踐者的打法。有興趣我傳給你——覺得以你在 E.C.I. 的位置會很有共鳴。Frank",
        ],
        "day57_noreply": [
            "Tina，再打擾一下。",
            "上次的問題可能時機不巧。",
            "我最近在整理一份「傳統產業數位先行者怎麼把 AI 轉型做成可展示成果」的觀察，幾位在製造業裡的人怎麼讓自己的前沿性站得住。",
            "不用特別回我，想看我直接傳給你——感覺跟你在 E.C.I. 走的路有交集。Frank",
        ],
        "day812": [
            "Tina，看你在 E.C.I. 走的路，我想直接說個觀察：",
            "你在做的事，本質上是在把自己變成「傳統紡織業裡最懂 AI 與數位的那個人」——這個身份很有價值，但它需要被「看得見的成果」撐住，不然在傳統產業很容易被當成不務正業。",
            "我們做 AI Token King 的一個出發點，就是幫像你這樣的先行者，把零散的 AI 嘗試變成一套可展示、可被組織複製的方法，讓你的轉型不只是你一個人的事。",
            "想約 20 分鐘——不是簡報，是讓你直接看跟 E.C.I. 的情境對不對得上，也想聽你在傳統產業推這件事的真實經驗。方便嗎？Frank",
        ],
    },
    "Jerry Chen, Ph.D.": {
        "slug": "lead-02-jerry-chen",
        "first": "Jerry", "last": "Chen",
        "ai_type": "A（身份建構者）／帶 B 風險意識",
        "dev_logic": "科學博士背景轉進藥廠商業與行銷，歷經 AstraZeneca、Takeda，現投入本土新銳生技 HanchorBio——他在重新定義自己：從科學家變成『懂科學又懂商業』的稀缺複合型人才。",
        "turning_point": "從研究/科學跨到藥廠商業營運與行銷——身份從『做科學的』變成『把科學變成商業價值的』。",
        "next_step": "在 HanchorBio 把腫瘤產品線商業化做出來，鞏固『科學×商業』雙棲身份。",
        "pain": "怕在 AI 浪潮裡，科學×商業的稀缺優勢被『會用 AI 的人』追上；想率先把 AI 用好，但醫藥法遵嚴、資料敏感，不能亂用。",
        "angle": "成為他『在嚴謹生技醫藥場域，把 AI 變成可控的個人/團隊裝備』的夥伴，為複合身份再加一層。",
        "hook": "科學博士→藥廠商業的複合身份＋高度法遵——要講『讓你在生技商業圈成為最早真正用好 AI 的人，且守得住合規』。",
        "connection": "Jerry 你好，你的軌跡很有意思——科學博士背景，一路在 AstraZeneca、Takeda 做到腫瘤/血液的商業與行銷，現在投入本土生技 HanchorBio。能同時懂科學語言又能扛商業營運的人，在生技圈是真的稀缺。我在做企業 AI 導入，特別關注像你這種跨科學與商業的複合型角色怎麼運用 AI。想跟你連結交流，Frank。",
        "day1": [
            "Jerry 謝謝你接受連結。",
            "我最近在觀察生技醫藥圈導 AI 的狀況，發現一個有意思的點：這個領域的人通常很聰明、學習力強，但因為法遵嚴、資料敏感，反而比一般產業更難放手用 AI，結果常常是「知道 AI 有用，但不知道在合規前提下怎麼用得到位」。",
            "想請教你：以你橫跨科學和商業的角度，你覺得生技行銷/商業這塊，AI 現在最大的卡點是法遵限制，還是大家還沒找到對的用法？",
            "純粹好奇，沒有要推銷。Frank",
        ],
        "day57_reply": [
            "謝謝你的分享，你說的（複述他提到的觀點）很到位——生技圈導 AI，難的不是聰不聰明，是怎麼在合規前提下用到位。",
            "我最近整理了一些「高度法遵產業的人，怎麼把 AI 變成自己可控、可展示的專業裝備」的做法，重點是在不踩線的前提下，讓你比同領域的人更早把 AI 用好。",
            "不是廠商案例，是實踐打法。有興趣我傳給你——覺得以你科學×商業的位置會很有共鳴。Frank",
        ],
        "day57_noreply": [
            "Jerry，再打擾一下。",
            "上次的問題可能時機不巧。",
            "我最近在整理一份「法遵嚴謹的生技醫藥場域怎麼把 AI 用得到位又不踩線」的觀察。",
            "不用特別回我，想看我直接傳給你——感覺跟你橫跨科學與商業的角色有交集。Frank",
        ],
        "day812": [
            "Jerry，看你走的路，我想直接說個觀察：",
            "你最稀缺的優勢是「同時懂科學語言和商業營運」，但在 AI 這波裡這個優勢有個風險——如果你不率先把 AI 變成自己的裝備，會用 AI 的人可能用更快的速度補上科學或商業的另一邊。反過來，如果你是生技商業圈裡最早把 AI 用好、又守得住合規的人，那個位置幾乎沒人搶得走。",
            "我們做 AI Token King 的設計，剛好能在合規可控的前提下，讓你的 AI 使用變成可展示的專業能力。",
            "想約 20 分鐘——不是簡報，是讓你直接試一次，看跟你的工作情境合不合。方便嗎？Frank",
        ],
    },
    "Ling Cheng": {
        "slug": "lead-03-ling-cheng",
        "first": "Ling", "last": "Cheng",
        "ai_type": "B（效率優化者）",
        "dev_logic": "10 年以上資深 B2B 行銷，橫跨綠能、智慧製造到車用資安（VicOne），靠跨部門、跨國 campaign 的執行力與穩定產出建立價值。AI 對她是讓複雜行銷更可控、可追蹤的工具。",
        "turning_point": "從單一產業 B2B 行銷走到車用資安這種高技術、跨國、跨部門領域——課題是複雜度暴增時還要維持成效穩定。",
        "next_step": "讓跨部門/跨國行銷在 AI 加持下產出更可預測、可追蹤、能向上交代。",
        "pain": "跨部門跨國 campaign 複雜，AI 工具若各團隊各用各的反而更亂、成效更難追；怕引進後出狀況在管理層失分。",
        "angle": "成為她『讓跨部門 AI 行銷成果可預測、可追蹤、能向上交代』的可靠夥伴。",
        "hook": "跨部門全球 campaign＋車用資安高技術門檻——AI 要幫上忙得先解決『用法一致、成果可追蹤』。",
        "connection": "Ling 你好，看到你有 10 年以上 B2B 行銷，還橫跨綠能、智慧製造到車用資安——這幾個領域的技術門檻和銷售週期都很硬，要做跨部門、跨國的 campaign 又能穩定出成效，真的不容易。我在做企業 AI 導入，對高技術 B2B 的行銷怎麼用 AI 提升特別有興趣。想跟你連結交流，Frank。",
        "day1": [
            "Ling 謝謝你接受連結。",
            "我最近在看 B2B（尤其技術門檻高的產業）導 AI 行銷的狀況，發現一個共同卡點：用 AI 加速產出很容易，但跨部門、跨國團隊一旦各用各的工具和方法，成效反而更難彙整、更難向上說清楚，主管等於把不可控帶進來了。",
            "想請教你：以你在 VicOne 帶跨部門 campaign 的經驗，你會擔心 AI 工具導入後「更難追蹤、更難交代」這件事嗎？還是你們已經有解？",
            "純粹好奇，沒有要推銷。Frank",
        ],
        "day57_reply": [
            "謝謝分享，你說的（複述他提到的痛點）很中肯——B2B 跨部門行銷導 AI，難的從來不是產出，是怎麼讓成效可控、可追蹤、能對上報告。",
            "我最近整理了一些「高技術 B2B 團隊讓 AI 用法一致、成果可衡量」的做法，讓主管不用擔心引進工具反而帶進不可控。",
            "不是廠商案例，是實際打法。有興趣我傳給你——覺得對 VicOne 的跨部門運作用得上。Frank",
        ],
        "day57_noreply": [
            "Ling，再打擾一下。",
            "上次的問題可能時機不對。",
            "我最近在整理一份「高技術 B2B 行銷讓 AI 成效可控、可追蹤」的觀察，幾個跨部門團隊怎麼避免導入後反而更亂。",
            "不用特別回我，想看我直接傳給你——感覺跟你帶的跨部門 campaign 有交集。Frank",
        ],
        "day812": [
            "Ling，看你帶的跨部門、跨國行銷，我想直接說個觀察：",
            "你要讓 AI 真正幫到這種複雜度的 campaign，關鍵不在工具多強，而在——怎麼讓不同部門、不同國家的團隊用同一套標準在用 AI，讓成果可追蹤、可彙整、你能對上交代。沒有這層，AI 只會讓複雜度更失控。",
            "我們做 AI Token King 正是為了這個：讓團隊的 AI 使用標準化、可衡量，主管手上有依據。",
            "想約 20 分鐘——不是簡報，是讓你直接看跟 VicOne 的跨部門情境對不對得上。方便嗎？Frank",
        ],
    },
    "Jimmy Lo": {
        "slug": "lead-04-jimmy-lo",
        "first": "Jimmy", "last": "Lo",
        "ai_type": "C（影響力建構者）／帶 A 領域轉進特質",
        "dev_logic": "16 年數位行銷老將，已把 GenAI 整進行銷流程，現投入 ESG/永續媒體（RECCESSARY）——在新興的 ESG 領域建立自己的話語權與影響力資產。",
        "turning_point": "從電商/數位行銷轉向 ESG 永續這個新興、有意義的領域——建立『ESG×數位×AI』交叉點的個人權威。",
        "next_step": "讓自己成為 ESG 行銷/永續商業成長領域、且懂 AI 落地的代表性聲音。",
        "pain": "已走在前面（GenAI workflow），瓶頸是怎麼把領先實踐沉澱成可規模化、可對外展示的影響力資產，而非只是內部效率；怕新領域話語權建立得不夠快。",
        "angle": "以同儕出現，成為他『把 GenAI 行銷實踐放大成 ESG 領域影響力資產』的夥伴。",
        "hook": "他已 integrate GenAI into workflows＋投入 ESG——要講『讓你的觀點與產出在 ESG 這個新領域領先、被看見』。",
        "connection": "Jimmy 你好，你的組合很少見——16 年數位行銷底子，已經把 GenAI 整進行銷流程，現在又投入 ESG 永續這個還在成形的領域。能同時站在「AI 落地」和「ESG」兩個前沿的人不多。我自己在做 AI 導入與管理，很想跟真的在用、又在新領域卡位的人交流。想跟你連結，Frank。",
        "day1": [
            "Jimmy 謝謝你接受連結。",
            "你已經把 GenAI 整進行銷 workflow，這跟大多數還在試水溫的人不是同一個階段，所以我想聊的也不一樣。",
            "我最近在觀察：像你這種已經跑在前面、又在 ESG 這種新興領域卡位的人，真正的課題常常不是「會不會用 AI」，而是「怎麼把自己領先的實踐，變成可被看見、可建立領域話語權的資產」。",
            "想請教你：在 ESG 這塊，你覺得你個人的 AI 實踐已經幫你建立起識別度了嗎，還是還在累積？純粹好奇。Frank",
        ],
        "day57_reply": [
            "謝謝你的分享，你講的（複述他提到的觀點）很有意思——這正是走在前面、又在開拓新領域的人才會遇到的問題。",
            "我最近整理了一些「把領先的 AI 實踐沉澱成可展示、可建立話語權的資產」的做法，幾個人怎麼在新興領域用 AI 把產出速度和影響力同時拉高。",
            "不是工具教學，是打法。有興趣我傳給你——覺得以你在 ESG×AI 的位置會有共鳴。Frank",
        ],
        "day57_noreply": [
            "Jimmy，再打擾一下。",
            "上次的問題可能時機不巧。",
            "我最近在整理一份「把領先 AI 實踐變成領域影響力資產」的觀察，幾個人怎麼在新興領域用 AI 放大話語權。",
            "不用特別回我，想看我直接傳給你——感覺以你在 ESG×AI 走的路會有共鳴。Frank",
        ],
        "day812": [
            "Jimmy，跟你交流這段時間，我感覺你對 AI 跟 ESG 的判斷都很清楚——知道什麼是真趨勢、什麼是包裝。",
            "正因為這樣我才想直接問：你現在這些領先的 GenAI 行銷實踐，多半還綁在你個人和現在的流程上吧？如果能變成一套可被複用、可對外展示的東西，對你在 ESG 領域建立話語權會是放大器。",
            "我們做 AI Token King 的其中一個出發點正是這個。想讓你花 20 分鐘試一次——不是要你採購，是覺得你這種真把 AI 用在前沿的人，用起來會有意思，也想聽你的回饋。方便嗎？Frank",
        ],
    },
    "Liz Chen": {
        "slug": "lead-05-liz-chen",
        "first": "Liz", "last": "Chen",
        "ai_type": "D（組織決策者）",
        "dev_logic": "高階主管（Sr. Managing Director），同時扛 marketing 與 BD，技術（FPGA/Edge AI）與商業執行雙棲。KPI 是整體事業成果，AI 的考量是對事業、客戶價值、風險與 ROI。",
        "turning_point": "從行銷/BD 走到 Sr. Managing Director——責任變成整個事業線的商業成果與方向。",
        "next_step": "讓 Terasic 在 Edge AI 這波（vision/defense/medical/aerospace）抓住定位，決策要有依據。",
        "pain": "怕在 Edge AI 多應用領域押錯方向/工具導致資源錯置、事業落後；需要有框架、有 ROI 依據的決策，對董事會交代得清楚。",
        "angle": "成為她『讓 Edge AI 事業與內部 AI 導入決策有框架、有 ROI 依據』的夥伴。",
        "hook": "Sr. MD、FPGA＋Edge AI 跨國防/醫療/航太——對她講組織決策依據與 ROI，不講功能。",
        "connection": "Liz 你好，看到你在 Terasic 做到 Sr. Managing Director，同時扛 marketing 和 business development，又跨 FPGA、Edge AI 到國防、醫療、航太這些硬領域——技術深度加商業執行兩邊都要扛，這個位置很硬。我在做企業 AI 導入與管理，特別關注像你這種要為整個事業線做 AI 方向決策的人。想跟你連結交流，Frank。",
        "day1": [
            "Liz 謝謝你接受連結。",
            "我最近在跟一些要為整個事業線做 AI 決策的高階主管交流，發現大家共同的壓力不是「要不要做 AI」，而是「在這麼多應用方向（你們甚至橫跨國防、醫療、航太）裡，怎麼判斷資源該押哪、用什麼框架決策、怎麼跟董事會交代 ROI」。",
            "想請教你：以 Terasic 在 Edge AI 的佈局，你做這類方向決策時，最希望手上有、但目前比較缺的是什麼？",
            "純粹想聽決策者視角，沒有要推銷。Frank",
        ],
        "day57_reply": [
            "謝謝你願意分享，你提到的（複述他提到的觀點）很關鍵——這正是事業線決策者最需要、但市面工具最少幫上忙的一塊。",
            "我最近整理了一些「組織做 AI 導入/方向決策的框架」，重點是怎麼讓決策有依據、有 ROI 說明、對上對下都交代得清楚。不是廠商型錄，是決策框架。",
            "有興趣我傳給你參考——覺得對 Terasic 這種多應用線的決策很用得上。Frank",
        ],
        "day57_noreply": [
            "Liz，再打擾一下。",
            "上次的問題可能時機不巧。",
            "我最近在整理一份「事業線主管做 AI 方向決策的框架與 ROI 說明」的觀察，幾家公司怎麼把 AI 決策做得更紮實。",
            "不用特別回我，想看我直接傳給你——感覺跟你在 Terasic 要扛的決策有交集。Frank",
        ],
        "day812": [
            "Liz，看你在 Terasic 扛的範圍，我想直接說個觀察：",
            "你的位置上，AI 真正的風險不是「沒跟上」，而是「在這麼多應用方向裡押錯資源、或導入後說不清楚 ROI」。對 Sr. MD 來說，沒有一套決策框架和可衡量的成果，比慢一步更危險。",
            "我們做 AI Token King，設計就是讓組織的 AI 使用可被衡量、可被彙整成決策依據，讓你對上對下都有東西可說。",
            "想約 20 分鐘——不是簡報，是讓你直接看這套框架跟 Terasic 的決策需求對不對得上，由你判斷。方便嗎？Frank",
        ],
    },
}


def load_real_fields():
    found = {}
    with open(LEADS_CSV, encoding="utf-8-sig") as f:
        for d in csv.DictReader(f):
            if d["name"] in BATCH:
                found[d["name"]] = d
    missing = set(BATCH) - set(found)
    if missing:
        raise SystemExit(f"❌ 名單中找不到：{missing}")
    return found


def char_len(s):
    return len(s.replace("\n", ""))


def write_lead_md(name, b, real):
    conn = b["connection"]
    day1 = "\n\n".join(b["day1"])
    d57r = "\n\n".join(b["day57_reply"])
    d57n = "\n\n".join(b["day57_noreply"])
    d812 = "\n\n".join(b["day812"])
    md = f"""# {b['slug'][:7].upper()} — {name}

**批次：** 2026-06-19 WARM 補批 ｜ **策略：** S1 直攻法 ｜ **發送帳號：** Frank（CEO，高層對高層）

## 基本資料
| 欄位 | 內容 |
|------|------|
| 姓名 | {name} |
| 職稱 | {real['title']} |
| 公司 | {real['company']} |
| 地點 | {real['location']} |
| LinkedIn | {real['linkedin_url']} |
| 搜尋組合 | {real['combo_name']} |
| ICP 分數 / 分類 | {real['icp_score']} / {real['classification']} |

## 【分析】
- **AI 使用者類型**：{b['ai_type']}
- **發展邏輯**：{b['dev_logic']}
- **職涯轉折點**：{b['turning_point']}
- **他的下一步**：{b['next_step']}
- **核心痛點**：{b['pain']}
- **建議切入角色**：{b['angle']}
- **個人化鉤子**：{b['hook']}

## 【連線邀請】 ≤200 字（→ custom_variable_1）｜實際 {char_len(conn)} 字
{conn}

## 【第一封 Day 1】 ≤300 字（→ custom_variable_2）｜實際 {char_len(day1)} 字
{day1}

## 【第二封 有回覆版 Day 5-7】 ≤300 字｜實際 {char_len(d57r)} 字
{d57r}

## 【第二封 無回覆追蹤版 Day 5-7】 ≤250 字（→ custom_variable_3）｜實際 {char_len(d57n)} 字
{d57n}

## 【第三封 引入方案 Day 8-12】 ≤350 字｜實際 {char_len(d812)} 字
{d812}
"""
    (OUT_DIR / f"{b['slug']}.md").write_text(md, encoding="utf-8")


def main():
    real = load_real_fields()
    for name, b in BATCH.items():
        write_lead_md(name, b, real[name])
    csv_path = OUT_DIR / "s1-batch-20260619-warm-expandi.csv"
    fields = ["linkedin", "first_name", "last_name", "company_name", "position",
              "location", "custom_variable_1", "custom_variable_2", "custom_variable_3"]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_ALL)
        w.writerow(fields)
        for name, b in BATCH.items():
            r = real[name]
            w.writerow([r["linkedin_url"], b["first"], b["last"], r["company"],
                        r["title"], r["location"], b["connection"],
                        " [P] ".join(b["day1"]), " [P] ".join(b["day57_noreply"])])
    print("✅ WARM 補批產出完成\n" + "=" * 60)
    for name, b in BATCH.items():
        warn = []
        if char_len(b["connection"]) > 200:
            warn.append(f"連線{char_len(b['connection'])}>200")
        if char_len(''.join(b['day1'])) > 300:
            warn.append(f"Day1>{char_len(''.join(b['day1']))}")
        flag = "  ⚠ " + " ".join(warn) if warn else "  ✓ 長度 OK"
        print(f"{name:20s} {real[name]['icp_score']:>3} {b['ai_type'][:6]}{flag}")
    print("=" * 60 + f"\nCSV: {csv_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
