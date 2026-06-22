# Expandi Sequence Builder — 訊息模板

## 設定說明

在 Expandi Campaign Sequence 裡設定三個步驟：

| Step | 類型 | Message 欄位填入 | 等待條件 |
|------|------|-----------------|----------|
| 1 | Visit Profile | （無訊息） | 0 天 |
| 2 | Connect | `{{custom_variable_1}}` | 等待接受 |
| 3 | Message | `{{custom_variable_2}}` | 接受後 1 天 |
| 4 | Message（如無回覆） | `{{custom_variable_3}}` | 7 天後 |

---

## 各 Lead 完整訊息（按優先序）

> 以下是每位 lead 的個人化訊息。
> CSV 匯入後 Expandi 自動代入，不需手動複製。
> 若需手動寄送，依序找到對應的人複製即可。

---

### 01. Allen Sun | Head of ASRock AI | 華擎科技 ASRock Inc.
**ICP:** 100 | **Heat:** 72 | **LinkedIn:** https://www.linkedin.com/in/ACwAAF_O2fsB4R3kgcPzFxWJ0w9WLJVw4GDEAeU

**Step 2 — Connect（custom_variable_1）：**
```
Allen 你好，看到你在 About 寫的「bridging the gap between silicon and software」，這句話讓我停下來多讀了幾遍——因為這正是我觀察到硬體背景的 AI 領導者最獨特的優勢所在。你在 2024 年親手創立 ASRock AI Center，這個動作本身就是在做一件很少人有能力做的事：從最底層的基礎設施往上重新定義 AI 應用的邊界。我在 AI Token 這塊服務不少從硬體或工程背景切入 AI 轉型的領導者，很想多了解你們 AI Center 目前走的方向，也許能交流一些有意思的視角。期待連結！Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Allen 謝謝你接受連結！

我有認真讀你的 LinkedIn，ASRock AI Center 聚焦在 AI Infrastructure、本地推論平台、CUDA/ROCm 生態系這幾個方向——光是這個組合就知道你們是少數真的從底層硬體能力出發在做 AI 的團隊，不是在追風口。

我自己在觀察一件事：很多企業在建 AI 基礎設施的時候，硬體端很強，但到了「讓組織內部真正用起來、產出可量化的成果」這一段，往往是最難過的關卡——不是技術問題，而是 AI 使用的方式和成本結構沒有被好好設計。

想請教你一個問題：ASRock AI Center 現在在推動內部或外部的 AI 落地時，你覺得最難讓對方「真正動起來」的阻力是什麼？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Allen，分享一個我最近觀察到的事：

硬體出身的 AI 團隊，在推組織轉型時通常有一個隱性優勢——他們對「系統整體性」的直覺比純軟體團隊強，但也有一個常見盲點：怎麼把這個優勢翻譯成非工程部門能買單的語言。

ASRock AI Center 做到現在，這個「內部說服」的難題，你們是怎麼解的？

Frank
```

---

### 02. Chi-Chung Chen | Director of Product and Machine Learning | aetherAI 雲象科技
**ICP:** 90 | **Heat:** 72 | **LinkedIn:** https://www.linkedin.com/in/ACwAAB01g5EB3w0Sgi0oa-1sbFkP32n6gHQag9g

**Step 2 — Connect（custom_variable_1）：**
```
Chi-Chung 你好，看到你 About 裡那句「from single-product vendors to comprehensive platform ecosystems」，這句話讀起來不像總結，更像一個正在進行中的賭注。從 GigaPixel 演算法到 Gaia 基礎模型，你們走的路徑很清晰——但平台化最難的部分往往不是技術，而是怎麼讓整個組織的工作方式跟上這個轉型節奏。我在關注幾家正在做類似跨越的 AI 醫療團隊，覺得你們的路徑很值得深聊。想加你交流，Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Chi-Chung，謝謝你接受連線！

我有認真看了一下你們 aetherAI 的發展軌跡——從 seed 到 IPO，再到現在同時在台灣、日本、德國三個市場推進，這種跨文化的醫療 AI 落地其實比純技術問題複雜得多。

你現在同時帶 ML 和 PM 兩個部門，我很好奇一件事：

**當 Gaia 這樣的基礎模型要從研究成果轉化成三個市場都能用的產品功能，你們內部 ML 團隊和 PM 團隊的協作節奏是怎麼跑的？** 是 PM 主導 roadmap、ML 往後接，還是你有建立一套不太一樣的機制？

問這個是因為我接觸過不少 AI 產品團隊，這個介面往往是平台化能不能成的關鍵變數，每家解法都不太一樣，想聽聽你們的版本。

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Chi-Chung，分享一個觀察：

AI 醫療產品在做平台化的時候，有一個很特殊的挑戰——「可解釋性」的標準在不同市場（台灣、日本、德國）差異極大，這讓同一個基礎模型的商業化路徑變得很複雜。

你們在 Gaia 的跨市場落地上，這個差異目前是怎麼被管理的？

Frank
```

---

### 03. Tzu-Hsuan Andrea Chuang | Director, Genomics Product Development | Taiwan Genomic Industry Alliance Inc. (TGIA)
**ICP:** 90 | **Heat:** 72 | **LinkedIn:** https://www.linkedin.com/in/ACwAAAGwmzUBtgVo6WPpp8qhhl6y4WrgtkARRvU

**Step 2 — Connect（custom_variable_1）：**
```
Andrea 你好，我在看你的 About 時注意到最後那句話——「system-level approaches to translational reasoning」，這個方向讓我停下來多想了一下。從 ISO 15189 實驗室到 IND-enabling studies，你走的其實是一條從「執行精準度」往「決策架構」移動的路，而你現在試圖把這些整合成一套系統性的方法論，這個轉變本身就很值得聊。我自己在協助不同領域的研究者和開發者思考如何把複雜的專業邏輯轉化成可操作的框架，感覺我們在關注的問題有些交集。想連結，之後有機會交流。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Andrea，謝謝你接受連結！

我在你的 About 裡看到一個讓我很好奇的描述——你說你目前在探索「system-level approaches to translational reasoning」。這個方向聽起來不只是方法上的調整，更像是在重新定義轉譯開發裡「推理」這件事本身應該怎麼發生。

從你的背景來看，你同時有臨床數據、生統框架、還有 CRO/CDMO 合作的實戰經驗——這些組合其實非常稀有，但我猜把它們整合成一套別人能理解、能複製的邏輯，可能才是現在最難的部分？

想直接問你一個問題：你現在在建構這套「轉譯推理框架」的過程中，覺得最難被系統化、或最難跟外部團隊溝通的環節是哪一塊？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Andrea，分享一個我觀察到的案例：

有幾位從臨床或實驗室背景出發的研究者，在嘗試把自己的方法論「可輸出化」的過程中，發現最大的阻力不是知識本身，而是——如何讓外部受眾在短時間內建立足夠的信任框架，才能「接得住」你的邏輯。

你在建構那套轉譯推理框架的過程中，有沒有碰到類似的溝通難題？

Frank
```

---

### 04. Chien-Ming Huang | Head of AI | Agaruda
**ICP:** 88 | **Heat:** 72 | **LinkedIn:** https://www.linkedin.com/in/ACwAAAiOOXsBP-aRh5sd2CcHZ4DKSTjPAyjCT7o

**Step 2 — Connect（custom_variable_1）：**
```
Chien-Ming 你好，看到你在 Agaruda 從零建立整個 AI 部門，還要同步定義策略、對齊產品跟商業目標——這個組合其實挺少見的，大多數 Head of AI 要不是偏技術、就是偏管理，你看起來兩邊都要扛。我在協助幾個類似角色的 AI 負責人處理「讓 AI 投入在組織內部說得清楚、算得明白」這件事，覺得你的路徑很有意思，想連結交流一下。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Chien-Ming 謝謝你接受連結！

我有認真看你的背景——從 Trend Micro 做 LLM fine-tuning 跟惡意程式偵測，到現在在 Agaruda 主導整個 AI 部門的建制，這個跨度其實蠻大的。

我特別好奇一件事：你在 About 裡提到要「align AI initiatives with product and business priorities」——這句話背後通常藏著很多張力，尤其是當 AI 團隊還在建構期的時候，技術端的節奏跟商業端的期待往往不太一樣。

想請問你：目前在 Agaruda，你覺得讓 AI 工作「對內說清楚價值」這件事，你們現在是怎麼處理的？是有一套內部的評估框架，還是還在摸索中？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Chien-Ming，補充一個觀察：

從零建立 AI 部門的人，在組織內通常有一個特殊的壓力來源——你必須同時是「AI 的布道者」和「AI 投資的守門人」，但這兩個角色其實在邏輯上有張力：布道者傾向擴大應用範圍，守門人必須過濾掉沒有 ROI 的嘗試。

這個角色張力，你是怎麼在 Agaruda 內部找到平衡的？

Frank
```

---

### 05. Monica Hsueh | Global Marketing Director | Speed 3D Inc.
**ICP:** 88 | **Heat:** 72 | **LinkedIn:** https://www.linkedin.com/in/ACwAAAAOqRUB9D1gVlOqrWgk2fa8aF9Tx8TwLFw

**Step 2 — Connect（custom_variable_1）：**
```
Monica 你好，看到你 About 裡那句「bridge the gap between AI engineering and go-to-market」，我停下來多讀了幾次——因為這句話背後要成立，其實需要一套很紮實的 AI 使用方法論，不是每個人都能真正撐起來的。我自己在協助不同背景的人建立 AI 工作方式，發現最難的往往不是工具，而是怎麼把 AI 能力轉化成別人聽得懂、能信任的語言。覺得你在做的事很有意思，想連結認識一下。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Monica 謝謝你接受連結！

我認真翻了你的背景，有個問題一直在腦袋裡轉：

你在 About 裡提到同時在推進 health tech、deep research、immersive technology 這幾個方向——這些領域的 AI 應用邏輯其實差滿多的，從 VC pitching 的角度來說，要讓投資人快速理解你的 AI 策略有一致性，應該很考驗你怎麼建構那套敘事框架。

想請教你：你目前在跟投資人或合作夥伴溝通 AI 策略的時候，你覺得最難讓對方「真的聽懂」的部分是什麼？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Monica，最近看到一個有趣的現象：

在 AI 創業生態裡，最有影響力的行銷人，往往不是那種「會用最多 AI 工具」的人，而是那種「能幫技術團隊建立一套外部可信度敘事」的人——因為工具會迭代，但信任框架是人建的。

以你現在在 health tech + immersive tech 兩個賽道都有佈局的角度，你覺得這套「可信度敘事」目前還缺什麼？

Frank
```

---

### 06. Victoria Hsu | Adjunct Instructor  (Marketing/Sales/Product Development ) | 財團法人塑膠工業技術發展中心 (PIDC)
**ICP:** 88 | **Heat:** 72 | **LinkedIn:** https://www.linkedin.com/in/ACwAABZ8N68BUsewAoFM4DYjrXihDP_KubajubE

**Step 2 — Connect（custom_variable_1）：**
```
Victoria 你好，你 About 裡那個「turned」讓我停下來想了一下——從生醫工程師到手術器材業務，再到現在在 PIDC 教 Marketing 與 Product Development，你其實已經完成兩次身份轉換了。我在觀察一些在技術與商業之間跨界的專業人士，怎麼在這個 AI 快速改變溝通方式的時代，重新建立自己的方法論與話語權。覺得你的路徑很有代表性，想連結交流。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Victoria 謝謝你接受連結！

我最近在觀察一個現象：很多擁有深厚實戰背景的專業人士，在轉入教學或顧問角色的時候，反而會遇到一個矛盾——你的知識太豐富、太情境化，反而很難快速讓學員或客戶「接住」。

你從手術室旁邊跟外科醫師談器材，到現在在課堂上教 Marketing 和 Product Development，這個跨度其實非常大。

想請教你：你在把這些實戰經驗轉化成課程內容的時候，目前最大的挑戰是什麼？是知識的結構化、還是怎麼讓沒有醫療背景的學員也能理解你在說什麼？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Victoria，分享一個我觀察到的模式：

在從業務或執行角色轉向教學/顧問的過程中，最有說服力的人，往往不是那種「把過去經驗整理成清單」的人，而是那種「能夠重新命名自己的核心方法論」的人——一個好的命名，讓隱性知識變得可傳遞，也讓自己在市場上有了獨特的標籤。

你現在在建構那套跨領域方法論，有沒有開始在想，它應該叫什麼？

Frank
```

---

### 07. Ken Chan | CTO, Vice President | AIRA 城智科技股份有限公司
**ICP:** 100 | **Heat:** 62 | **LinkedIn:** https://www.linkedin.com/in/ACwAACfM-kcBYlRHPqr45icg_Fv_xxVa0JFwgKY

**Step 2 — Connect（custom_variable_1）：**
```
Ken 你好，你 LinkedIn About 裡有句話讓我印象很深：「translating complex market insights into clear, actionable technology roadmaps」——這件事說起來簡單，但在 AI 落地的節奏下要做好，其實是整個組織最難對齊的一環。我自己在接觸不少科技公司 CTO 的過程中，發現大家卡關的點出奇地相似。你在城智科技把 Computer Vision 推進到現在這個階段，很想多了解你們的思路，加個連線交流看看！Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Ken 謝謝你接受連線！

我有稍微研究了一下城智科技在做的方向——把 AI 與 Computer Vision 深度整合進安防系統，這條路在台灣算是走得比較前面的。

我自己在和幾位 CTO 聊的過程中，發現一個蠻有趣的現象：當 AI 能力愈來愈強，反而「怎麼讓技術決策在組織內被理解和執行」變成了新的瓶頸——不是技術不夠，而是技術和業務之間的語言還沒對齊。

想請教你一個問題：以你現在在城智的角色，你覺得 AI 技術落地最難跨過的那道檻，是在哪個環節？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Ken，我最近在整理幾個 AI 落地案例，發現一個有趣的規律：

技術最難推動的地方，不是沒有資源，而是「決策週期比技術迭代週期慢一個量級」——工程端已經跑出結果，但組織端的信任還沒跟上。

這件事在做 Computer Vision 產品的團隊裡特別明顯。

不知道這個觀察在你們城智目前的節奏裡，有沒有共鳴？

Frank
```

---

### 08. Joy Chan | Deputy CEO,  CIO/CISO  | Taiwan Network Information Center (TWNIC)
**ICP:** 90 | **Heat:** 62 | **LinkedIn:** https://www.linkedin.com/in/ACwAAACgkrIBxvRKk83TMAbMSNmcpOYzRAGNIEM

**Step 2 — Connect（custom_variable_1）：**
```
Joy 你好，看到你在 TWNIC 同時扛著 CIO 和 CISO 的角色，就覺得這個組合很有意思——推動技術創新和守住資安邊界，這兩件事的張力在 AI 浪潮裡應該特別明顯。我自己在幫幾個技術領導者釐清 AI 導入的組織邏輯，發現像 TWNIC 這樣具有公共基礎設施性質的機構，面對的問題跟一般企業很不一樣。想跟你交流，加個連線。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Joy 謝謝你接受連線！

我最近在觀察一個現象：很多 CIO 層級的領導者在推 AI 的時候，技術選型其實不是最難的部分，反而是「怎麼讓組織相信這件事值得做、怎麼對上面說清楚投資邏輯」花了最多精力。

以你在 TWNIC 的位置來說——公共網路基礎設施機構、同時兼任 CISO——我很好奇，你們內部在評估 AI 相關投資或工具導入的時候，決策框架大概長什麼樣子？是比較偏向先從特定團隊試點、還是一開始就要設定全組織的標準？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Joy，上週讀到一篇研究，說公共基礎設施機構在導入 AI 的過程中，「治理框架缺位」比「技術不成熟」更常是卡關原因——因為組織的風險容忍度和技術可能性之間，通常有一段很難填補的信任差距。

以你同時掌管 CIO 和 CISO 的角色，這個觀察你有沒有感受到？

Frank
```

---

### 09. Amanda Ye | Director, Global Marketing Department | ARBOR Technology Corp.
**ICP:** 90 | **Heat:** 62 | **LinkedIn:** https://www.linkedin.com/in/ACwAAAsFqnUBUgr_X06KhlNMiz-sCsuh7NFe44I

**Step 2 — Connect（custom_variable_1）：**
```
Amanda 你好，看到你 About 裡寫的「transforming innovative technologies into scalable opportunities」這句話，覺得精準到有點心有戚戚——工業 IoT 的技術含量往往很高，但要讓不同市場的客戶都「看懂、想買」，行銷端要做的轉譯工作其實非常吃力。我在協助幾個科技品牌的全球行銷團隊用 AI 建立內容與策略的標準化流程，想多了解你們在跨市場推進時的實際狀況，想說先連線交流看看。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Amanda 謝謝你接受連線！

我有稍微看了一下 ARBOR 的產品線和你的背景，你們在工業 IoT 和嵌入式運算這塊技術積累很紮實，但我在想，像這種以硬體與解決方案為核心的 B2B 品牌，要在不同國際市場做出有感的品牌定位，行銷團隊其實要同時扮演「技術翻譯者」和「市場策略師」兩個角色——這個張力在全球團隊的協作上應該會更明顯。

想請教你一個問題：你在推進跨市場的 go-to-market 策略時，目前覺得最難「標準化」又不失在地感的環節是哪一塊？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Amanda，分享一個我最近觀察到的現象：

在硬體/工業解決方案公司做全球行銷的人，往往是整個組織裡最懂「技術語言和市場語言之間落差有多大」的那個人——也因此是最難被 AI 工具直接取代、但也最難讓 AI 工具真正幫到的角色。

你覺得你們現在在跨市場內容這塊，AI 目前能幫到哪裡，哪裡還幫不到？

Frank
```

---

### 10. Pei-Kang Hsieh | Director of Product Management | beBit TECH
**ICP:** 90 | **Heat:** 62 | **LinkedIn:** https://www.linkedin.com/in/ACwAAAbO1dgB2bg0v9kg4eOKvpZaef8O92AMr7U

**Step 2 — Connect（custom_variable_1）：**
```
Pei-Kang 你好，看到你 About 裡提到同時融合 engineering、design 與 PM 的視角來做決策——這其實是很少 Director 級別的人敢這樣定位自己的，通常到這個層級反而會淡化技術背景。我在做 AI 工具的業務開發，最近接觸了不少 PM Leader 在探索如何把這種跨域判斷力「外掛」給整個團隊，覺得你的經歷很有共鳴，想交流一下你們在 beBit TECH 這塊的思考。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Pei-Kang 謝謝你接受連線！

剛剛又重新看了一遍你的背景，有個問題一直在我腦中轉——

你提到自己的強項是把 engineering、design、PM 三塊整合在一起做判斷，這在個人層面顯然是很強的武器。但當你現在帶的是一個 PM 團隊，這種「整合式思維」其實很難直接教給別人，因為它更像是一種內化的直覺，而不是 SOP。

想請教你：在 beBit TECH，你目前怎麼看這件事？你會希望把這套思維「方法論化」讓團隊複製，還是你更傾向讓每個 PM 去發展自己的判斷風格，你來做最後的整合層？

純粹好奇你的思路，沒有標準答案那種問題 😄

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Pei-Kang，補充一個觀察：

我接觸過不少同時具備工程和設計背景的 PM Leader，發現他們在帶團隊的時候通常面對一個很有意思的矛盾——自己的判斷能力很強，但「強到很難讓別人的判斷邏輯被訓練出來」。

結果就是：團隊越依賴你，你就越難真正擴張組織的決策品質。

這個張力在你帶 PM 團隊的日常裡，有沒有感受到？

Frank
```

---

### 11. Syuan Yu Chen | Product Director | AI DataBrushing Technology Co., Ltd.
**ICP:** 90 | **Heat:** 62 | **LinkedIn:** https://www.linkedin.com/in/ACwAACSYWxQBttI3ploUWFVmuB0IEHVQDEIC9t4

**Step 2 — Connect（custom_variable_1）：**
```
Syuan 你好，看到你主導了法語和西班牙語介面的上線，這其實是很多 SaaS 產品卡關的一步——光是確保不同語系市場的一致性就夠燒腦的了。我在關注幾位同時在跑多市場產品的 Director，覺得你的路徑很有意思，想連結交流。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Syuan 謝謝你接受連結！

我有在研究幾個在 SaaS 產品做多語系市場的案例，你的背景很特別——從硬體 IoT 到 Amazon 賣家工具，又橫跨美、歐、日、中不同市場，這種跨度在 Product Director 裡其實不多見。

我很好奇一件事：當你在同時維護這麼多市場版本的產品時，你目前覺得最難「標準化」的環節是哪個？是規格的對齊、跨部門的溝通節奏、還是其他地方？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Syuan，分享一個觀察：

跑過多語系市場的 PM 有個很獨特的直覺——他們對「哪些產品決策是真正通用的、哪些其實是文化假設」的感知，比只跑單一市場的人強很多。

但這個直覺很難被系統化，也很難被傳授給沒有類似經驗的團隊成員。

在你帶的團隊裡，這塊知識傳遞的問題，你現在是怎麼處理的？

Frank
```

---

### 12. Fabien Petitgrand | Chief Technology Officer | ubiik inc.
**ICP:** 88 | **Heat:** 62 | **LinkedIn:** https://www.linkedin.com/in/ACwAAAANXUwB8ibljBY66965qRQNNVEfMemqELQ

**Step 2 — Connect（custom_variable_1）：**
```
Fabien 你好，看到你 About 裡寫的「cellular-inspired」——這個定位讓我多想了幾秒，因為大多數 IoT 技術在講覆蓋和功耗，但你在講的是整個設計哲學的位移。我在觀察幾個正在重新定義垂直領域技術框架的團隊，ubiik 的方向很有意思。想跟你連線，多了解你們現在在台灣和海外市場的佈局邏輯。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Fabien，感謝你接受連線！

我最近在跟幾個做深度技術產品的 CTO 聊，發現一個很有趣的共同挑戰：技術本身已經領先，但「讓對的人在對的時間點理解這個技術的價值」這件事，反而變成最費力的環節——不管是內部推動、還是對外爭取合作或資源。

ubiik 在做的事，感覺技術門檻和敘事門檻都不低。想請教你，現在在你的角色上，哪個環節是你覺得最消耗精力、但又很難直接授權給團隊去處理的？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Fabien, a quick thought:

Deep tech companies like ubiik face a specific challenge: your technology is genuinely differentiated, but the "proof of value" cycle is long — and the window to get a strategic partner or enterprise customer to stay engaged through that cycle is short.

I've been thinking about how the best deep tech CTOs manage that attention gap. Curious what your current approach looks like.

Frank
```

---

### 13. Stan Yu (Hsien Wen) | Venture Partner, Head of Asia Pacific | Cardumen Capital
**ICP:** 88 | **Heat:** 62 | **LinkedIn:** https://www.linkedin.com/in/ACwAAB69ok4BeWeDddPs9NyRa4KNjVH2yg2wnUw

**Step 2 — Connect（custom_variable_1）：**
```
Stan 你好，看到 Cardumen 把「radical collaboration」放進核心文化，這句話讓我停下來想了一下——對一個橫跨歐洲、中東、亞太的基金來說，這其實是很高難度的承諾。我自己在做 AI 相關的業務開發，最近接觸了不少在亞太深耕的投資人，發現大家對 AI 怎麼真正改變投資判斷流程這件事，看法差距很大。你在台北這端怎麼落實這個「absolute availability」？很想聽你的觀點，先連線打個招呼。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Stan，謝謝你接受連線！

我注意到 Cardumen 同時跑三種不同策略——直投、基金投資、加上跨區域配置，光是要讓這三條線的資訊在歐洲總部跟亞太之間對齊，我就覺得資訊流的管理一定是個很真實的挑戰。

你在台北作為 Head of Asia Pacific，我好奇的是：你目前在評估一個新的創辦人或新市場機會時，從接觸到形成初步判斷，大概是什麼樣的流程？你覺得這個流程裡，哪個環節是你最想提速或提升品質的？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Stan，分享一個觀察：

亞太的 VC 在做跨區配置的時候，有個很現實的問題：總部的 deal flow 邏輯和亞太本地的創辦人節奏通常不同步，而這個不同步最後往往是由本地負責人用個人時間和判斷力來填補的。

你在台北這端，這個「填補落差」的成本，目前是怎麼被消化的？

Frank
```

---

### 14. Clara Cheng | Associate Marketing Director | Flytech Technology
**ICP:** 80 | **Heat:** 62 | **LinkedIn:** https://www.linkedin.com/in/ACwAAAObp4oBXxBzEZo7Jxujh4BhUgMQ8MQN-VE

**Step 2 — Connect（custom_variable_1）：**
```
Clara 你好，看到你 About 裡同時提到 organizational alignment 跟 new business development，這個組合讓我印象深刻——能把內部策略對齊跟外部業務開拓同步推進的行銷主管其實不多。我在協助 IT 產業的行銷團隊用 AI 建立更有效率的決策與內容體系，覺得你的背景跟我們正在做的事情很有交集，想連結認識一下。Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
Clara 謝謝你接受連結！

我看了你的背景，14 年 IT 產業行銷經驗，又同時在推 GTM 策略跟新業務開發，這種組合在市場上真的蠻少見的。

最近我在跟幾位行銷主管聊，大家都在面對一個類似的問題：AI 工具在團隊裡的導入，往往停在「個人用用」的階段，很難真正變成組織層面可以對上報告、可以衡量 ROI 的能力。

想請教你一個問題——以你現在帶行銷團隊的角度，你覺得 AI 在你們的工作流程裡，目前最大的卡點是什麼？是工具選擇、團隊接受度，還是根本還沒找到跟業績掛鉤的方式？

Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
Clara，分享一個我最近在觀察的現象：

IT 產業的行銷主管，在推動 AI 工具導入的時候，通常面對的不是「選哪個工具」的問題，而是「如何讓 AI 的應用成果對非行銷背景的決策者可見」——因為 ROI 不夠直觀，預算審核就很難過。

以你在 Flytech 同時推 GTM 和新業務的角色，這個「讓 AI 成果可見」的問題，你們目前是怎麼應對的？

Frank
```

---

### 15. Rayvatek International | Chief Technology Officer  | Rayvatek 睿智創新科技
**ICP:** 90 | **Heat:** 42 | **LinkedIn:** https://www.linkedin.com/in/ACwAAE6IfZwB35f_hglqNTwz7pFgdXSMbnIMWQE

**Step 2 — Connect（custom_variable_1）：**
```
看到 Rayvatek 把『Design to Mass Production』做成一站式服務，這個定位在台灣金屬 3D 列印市場其實非常有競爭力。身為 CTO 要同時把關技術深度又要讓客戶快速理解這條路徑的價值，這中間有一個很微妙的溝通落差需要被填補。我最近在研究製造業技術公司如何縮短客戶從「第一次接觸」到「信任決策」的週期，覺得跟您的場景很有關聯，想來交流一下您們目前的觀察。— Frank
```

**Step 3 — Day 1 Message（custom_variable_2）：**
```
感謝接受連線！

稍微研究了一下 Rayvatek 的服務架構，十年專業加上從設計到量產的完整能力，這在台灣製造業裡其實是很稀缺的組合。

不過我一直在思考一個問題：像你們這樣技術門檻很高的公司，客戶在詢單初期往往需要大量的來回溝通才能確認可行性——這個「技術評估前的教育成本」，在你們的業務流程裡目前是怎麼被消化的？

是靠業務工程師人工判斷，還是有什麼機制讓客戶在聯繫你們之前就能自己篩選需求？

純粹好奇你們實際運作的邏輯，因為這個環節在技術型製造服務公司裡通常是最耗資源、也最難標準化的地方。

— Frank
```

**Step 4 — Day 7 Follow-up（custom_variable_3）：**
```
補充一個想法：

金屬 3D 列印這個領域，詢單品質差異極大——有些客戶一開口就很明確，有些則需要好幾輪來回才能確認可行性。

我在想，如果有辦法讓「高品質詢單」在接觸你們之前就自動篩選出來，這件事對你們的技術團隊效率影響會有多大？

純粹好奇你的看法。

Frank
```
