#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地去重檢查（離線版）

asana_dedup.py 需要 ASANA_TOKEN 才能比對線上 CRM；在沒有金鑰的環境裡，本工具改用
repo 內既有的「已接觸/已匯出」清單做離線預檢，並檢查多個批次之間是否互相重複。

比對來源（視為「可能已接觸」）：
  - scripts/output/asana_*.csv          （曾匯入 Asana 的名單）
  - lead-drafts/**/*expandi*.csv         （先前批次已產出的 Expandi 名單）
  - lead-drafts/*dripify*.csv            （先前批次已產出的 Dripify 名單）

用法：
  python lead-drafts/dedup_local_check.py <batch1.csv> [batch2.csv ...]
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def normalize_url(url: str) -> str:
    url = (url or "").strip().lower().rstrip("/")
    return url.split("?")[0] if "?" in url else url


def url_cols(fieldnames):
    return [c for c in fieldnames if c and c.lower() in ("linkedin", "linkedin_url", "url")]


def load_urls(path: Path):
    out = {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            rd = csv.DictReader(f)
            cols = url_cols(rd.fieldnames or [])
            if not cols:
                return out
            for row in rd:
                for c in cols:
                    u = normalize_url(row.get(c, ""))
                    if u.startswith("http"):
                        out[u] = row.get("name") or row.get("first_name") or ""
    except Exception as e:
        print(f"  ⚠ 讀取 {path.name} 失敗：{e}")
    return out


def main():
    if len(sys.argv) < 2:
        sys.exit("用法：python lead-drafts/dedup_local_check.py <batch.csv> [更多批次.csv]")
    batches = [Path(p) if Path(p).is_absolute() else ROOT / p for p in sys.argv[1:]]

    # 1) 建立「已接觸」URL 池
    contacted = {}
    sources = list((ROOT / "scripts" / "output").glob("asana_*.csv"))
    sources += [p for p in (ROOT / "lead-drafts").rglob("*expandi*.csv") if p not in batches]
    sources += [p for p in (ROOT / "lead-drafts").glob("*dripify*.csv")]
    for s in sources:
        contacted.update(load_urls(s))
    print(f"已接觸/已匯出來源：{len(sources)} 檔，共 {len(contacted)} 個不重複 URL")
    print("=" * 70)

    # 2) 逐批檢查 + 跨批次重複
    seen_across = {}
    exit_code = 0
    for b in batches:
        urls = load_urls(b)
        print(f"\n批次 {b.relative_to(ROOT)} — {len(urls)} 筆")
        for u, who in urls.items():
            flags = []
            if u in contacted:
                flags.append("已在既有名單"); exit_code = 1
            if u in seen_across:
                flags.append(f"與 {seen_across[u]} 跨批重複"); exit_code = 1
            seen_across[u] = b.name
            status = "  ".join(flags) if flags else "✅ 新名單，可發送"
            print(f"  - {who:20s} {status}")

    print("\n" + "=" * 70)
    print("結論：" + ("⚠ 有重複，請排除後再匯入" if exit_code else "✅ 全部為新名單，無重複，可進入核准流程"))
    print("（正式發送前仍須以 `python scripts/asana_dedup.py check` 對線上 Asana CRM 再驗一次）")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
