#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
S1 直攻法 — 台灣 HOT/WARM 批次中文文案產生器（規模化）

讀取既有抓取名單，依職稱/摘要把每位 lead 分類為 AI 使用者類型 A/B/C/D，
套用對應的 S1 話術框架，產出「連線邀請 + Day1 + Day7 無回覆追蹤」三段中文文案，
全程 ≤300 字，輸出 Expandi 匯入 CSV（custom_variable_1/2/3，[P] 為段落分隔）。

注意：這是「規模化草稿」品質——以類型＋公司＋職稱客製，鉤子取自摘要；
深度不及逐筆手寫（如 lead-drafts/ 的 10 筆）。發送前仍須人工 review。

執行：python lead-drafts/tw_batch_generator.py scripts/output/leads_v2_20260603.csv
"""
import csv, sys, re
from pathlib import Path

def role_zh(title):
    t = title.lower()
    pairs = [
        ("ceo","執行長"),("chief executive","執行長"),("執行長","執行長"),
        ("founder","創辦人"),("co-founder","創辦人"),("創辦人","創辦人"),
        ("president","總經理"),("general manager","總經理"),("總經理","總經理"),
        ("managing director","董事總經理"),
        ("cio","資訊長"),("chief information","資訊長"),
        ("ciso","資安長"),("cto","技術長"),("chief technology","技術長"),("技術長","技術長"),
        ("cmo","行銷長"),("chief marketing","行銷長"),
        ("chief strategy","策略長"),("cso","策略長"),
        ("vp","副總"),("vice president","副總"),
        ("head of ai","AI 負責人"),("head of data","數據負責人"),("machine learning","ML 負責人"),("head of cloud","雲端負責人"),
        ("head of marketing","行銷負責人"),("marketing director","行銷總監"),("director of marketing","行銷總監"),
        ("global marketing","全球行銷總監"),("digital marketing","數位行銷總監"),("brand","品牌負責人"),
        ("communications","公關總監"),("pr","公關總監"),
        ("it director","IT 主管"),("head of it","IT 主管"),("information technology","IT 主管"),
        ("operations","營運總監"),("營運","營運總監"),
        ("product","產品總監"),("engineering","工程總監"),
        ("strategy","策略主管"),("strategic planning","策略規劃總監"),
        ("business development","業務發展總監"),("sales","業務總監"),("partnership","合作夥伴總監"),
        ("consultant","顧問"),("head of marketing","行銷負責人"),
    ]
    for k,v in pairs:
        if k in t:
            return v
    return "負責人"

def classify(title, summary):
    s = (title + " " + summary).lower()
    # A：明顯轉型 / 傳統產業數位先行者 / 跨界身份
    a_sig = ["transform","轉型","textile","manufacturing","traditional","turned ",
             "phd","ph.d","mba","architect turned","career"]
    # C：影響力 / 內容 / 品牌 / 社群 / 顧問 / KOL
    c_sig = ["marketing","brand","content","pr ","public relation","communications",
             "community","consultant","influencer","講師","顧問","kol","品牌","行銷"]
    # B：效率 / IT / 營運 / 產品 / 工程 / 流程
    b_sig = ["it ","information technology","operations","營運","product","engineering",
             "automation","pm","process","infrastructure","cto","cio","technology & innovation"]
    # D：決策層
    d_sig = ["ceo","founder","president","general manager","總經理","執行長","創辦人",
             "managing director","vp","vice president","partner","chief","head of ai",
             "strategy","strategic","business operations","cso","director, business"]
    title_l = title.lower()
    # 優先級：A 僅限明確傳統產業先行者（避免把數位/AI 公司誤判）；
    #         決策層職稱 → D；行銷/品牌/內容 → C；IT/營運/產品/工程 → B；否則 D
    if any(k in s for k in ["textile","garment","紡織","成衣","architect turned","turned marketer"]):
        return "A"
    if any(k in title_l for k in ["ceo","founder","president","general manager","總經理","執行長","創辦人","managing director","partner","chief strategy","cso","chief executive"]):
        return "D"
    if "vp" in title_l or "vice president" in title_l or "chief" in title_l and "marketing" not in title_l:
        return "D"
    if any(k in title_l for k in ["marketing","brand","content","communications","pr","品牌","行銷","consultant","顧問"]):
        return "C"
    if any(k in title_l for k in ["it","operations","product","engineering","營運","technology","cto","cio","data","machine learning","ai"]):
        return "B"
    if any(k in s for k in a_sig): return "A"
    return "D"

def cap(s, n):  # 安全裁切（理論上模板已 ≤300）
    return s if len(s)<=n else s[:n-1]+"…"

def build(p, co, role, ai_type):
    """回傳 (c1,c2,c3)，全程中文，單則 ≤300。"""
    T = {
"A": (
 f"{p} 你好，看到你在 {co} 帶{role}，在一個相對傳統的場域裡推 AI 與數位轉型——說實話，在這種環境當先行者，比在數位原生公司難太多，也更少人做得起來。我在做企業 AI 導入，特別佩服真的把轉型做出來的人。想跟你連結交流，Frank。",
 f"{p} 謝謝你接受連結。 [P] 我最近在觀察傳統產業的數位轉型，發現真正在推的人往往是公司裡少數的「先行者」，能力跟視野都夠，但最大的挑戰不是自己會不會，而是怎麼讓整個組織跟得上，不是只有你一個人在前面跑。 [P] 想請教你：以你在 {co} 的經驗，這種「先行者的孤獨」對你來說是不是真的存在？ [P] 純粹好奇，沒有要推銷。Frank",
 f"{p}，再打擾一下。 [P] 上次的問題可能時機不巧。 [P] 我最近在整理一份「傳統產業先行者怎麼把 AI 轉型做成可展示成果」的觀察，幾位在傳產裡的人怎麼讓自己的前沿性站得住。 [P] 不用特別回我，想看我直接傳給你——感覺跟你在 {co} 走的路有交集。Frank",
),
"B": (
 f"{p} 你好，看到你在 {co} 擔任{role}，把 AI 與自動化導進實際營運——要讓工具在多團隊、多流程裡真的「順」進去又穩定，比想像中難很多。我在做企業 AI 導入，對怎麼讓 AI 落地後可控、可追蹤特別有興趣。想跟你連結交流，Frank。",
 f"{p} 謝謝你接受連結。 [P] 我最近在看企業導 AI 的狀況，發現一個常見卡點：用 AI 加速產出不難，但不同團隊各用各的、用法不一致，成效反而更難追蹤、更難向上交代，等於把不可控帶進來。 [P] 想請教你：以 {co} 目前的進度，你覺得讓 AI 穩定落地，最難的是工具選擇，還是讓大家用得一致這一段？ [P] 純粹好奇，沒有要推銷。Frank",
 f"{p}，再打擾一下。 [P] 上次的問題可能時機不對。 [P] 我最近在整理一份「讓 AI 工具在組織裡用法一致、成效可追蹤」的觀察，幾個團隊怎麼避免導入後反而更亂。 [P] 不用特別回我，想看我直接傳給你——感覺跟你在 {co} 要處理的事有交集。Frank",
),
"C": (
 f"{p} 你好，看到你在 {co} 帶{role}，又持續在產出與經營影響力——能把內容/品牌做出聲量、又願意走在 AI 前沿的人不多。我自己在做 AI 導入與管理，很想跟真的在用 AI、又有觀點的人交流。想跟你連結，Frank。",
 f"{p} 謝謝你接受連結。 [P] 我最近在觀察：像你這種走在前面的人，用 AI 的瓶頸通常不是「會不會」，而是「怎麼用 AI 放大產出速度和影響力，又不讓內容失去你的專業深度和個人味」。 [P] 想請教你：以你現在在 {co} 的狀態，這個平衡已經是個課題了嗎，還是還沒到那一步？ [P] 純粹好奇，沒有要推銷。Frank",
 f"{p}，再打擾一下。 [P] 上次的問題可能時機不巧。 [P] 我最近在整理一份「內容/品牌型專業者怎麼用 AI 放大影響力又不失專業深度」的觀察。 [P] 不用特別回我，想看我直接傳給你——感覺以你在 {co} 走的方向會有共鳴。Frank",
),
"D": (
 f"{p} 你好，看到你在 {co} 擔任{role}，要為組織的 AI 方向做判斷——在這個位置上，難的往往不是要不要做 AI，而是怎麼判斷資源該押哪、怎麼跟上面交代成效。我在做企業 AI 導入與管理，特別關注像你這種要扛組織級決策的人。想跟你連結交流，Frank。",
 f"{p} 謝謝你接受連結。 [P] 我最近跟不少要為組織做 AI 決策的主管交流，發現共同的壓力是：AI 投入不小，但「決策依據、成效衡量、怎麼跟董事會說清楚 ROI」這幾關，市面上很少有工具真的幫得上。 [P] 想請教你：以 {co} 目前推 AI 的狀況，你做這類方向決策時，最希望手上有、但目前比較缺的是什麼？ [P] 純粹想聽決策者視角，沒有要推銷。Frank",
 f"{p}，再打擾一下。 [P] 上次的問題可能時機不巧。 [P] 我最近在整理一份「組織做 AI 導入/方向決策的框架與 ROI 說明」的觀察，幾家公司怎麼把 AI 決策做得更紮實、更好對上交代。 [P] 不用特別回我，想看我直接傳給你——感覺跟你在 {co} 要扛的決策有交集。Frank",
),
    }
    return T[ai_type]

def L(s): return len(s.replace(" [P] ",""))

def main():
    src = Path(sys.argv[1] if len(sys.argv)>1 else "scripts/output/leads_v2_20260603.csv")
    rows=[d for d in csv.DictReader(open(src,encoding="utf-8-sig"))]
    out=Path("lead-drafts/s1-taiwan-hot-batch")
    out.mkdir(parents=True, exist_ok=True)
    fields=["linkedin","first_name","last_name","company_name","position","location",
            "custom_variable_1","custom_variable_2","custom_variable_3",
            "ai_type","icp_score","classification"]
    n=0; over=0; dist={}
    with open(out/"s1-taiwan-all-expandi.csv","w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f,quoting=csv.QUOTE_ALL); w.writerow(fields)
        for r in rows:
            cls=r.get("classification","").upper()
            if cls not in ("HOT","WARM"): continue
            name=r["name"].strip(); title=r["title"].strip(); company=r["company"].strip()
            summary=(r.get("summary_snippet") or "")
            first=name.split()[0] if name.split() else name
            last=" ".join(name.split()[1:]) if len(name.split())>1 else ""
            t=classify(title,summary); role=role_zh(title)
            co = company if len(company)<=18 else company[:18]
            c1,c2,c3=build(first,co,role,t)
            for c in (c1,c2,c3):
                if L(c)>300: over+=1
            dist[t]=dist.get(t,0)+1; n+=1
            w.writerow([r.get("linkedin_url",""),first,last,company,title,r.get("location",""),
                        c1,c2,c3,t,r.get("icp_score",""),cls])
    print(f"✅ 產出 {n} 筆 → {out}/s1-taiwan-all-expandi.csv")
    print("類型分布：",dist," | 超過300的訊息數：",over)

if __name__=="__main__":
    main()
