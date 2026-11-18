"""チョコの研究（choco）の研究一覧 /research/ を media/choco-studies.json から作り、media/choco-pages.json に書き出す。

- 入力: media/choco-studies.json（配列。各要素 {"cat","authors","title","journal","url","level","finding","article"}）
  article は記事slug（空文字可）。複数のときはカンマ区切りか配列でもよい
- 同じ url は1件にまとめる（確認レベルは高い方、結論は先に書かれた方、記事は全部）
- 記事リンクは、media/choco-posts.json にある記事か sites/choco/{slug}/index.html がある記事だけ付ける
- 件数・分野ごとの件数は自動でタイトル・説明・目次に入る
- media/choco-pages.json のほかのページ（/tool/ など）は残す

使い方: python3 media/choco_research.py   （そのあと python3 media/build.py choco）
"""
import json
import re
from html import escape as E
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG = "choco"
DATE = "2026-10-20"

CATS = [  # (名前, id, 説明)
    ("豆と発酵", "bean", "カカオの品種・産地・発酵。豆の段階で香りの元がどう決まるか。"),
    ("焙煎と練り", "roast", "焙煎の温度と時間、コンチング（練り）。香りが生まれ、飛んでいく工程。"),
    ("テンパリング", "temper", "カカオバターの6つの結晶と、溶かす・冷ます・戻す温度、種を足す方法。"),
    ("口どけと保存", "texture", "ブルーム（白くなる）、粒の細かさとなめらかさ、成分の移り方。"),
    ("香りと味", "flavor", "香りの主役の成分、苦み・渋みのもと。"),
    ("感じ方", "perception", "チョコを欲しくなる理由、音や形で変わる感じ方。"),
    ("体と安全", "safety", "カカオフラバノールの大規模試験、犬のチョコ中毒、鉛・カドミウム。"),
]
LEVELS = {  # 名前: (順位, css)
    "数字確認": (3, "lv-o"),
    "要旨で照合": (2, "lv-n"),
    "書誌のみ": (1, "lv-b"),
}

CSS = (".lvb{display:inline-block;font-size:12px;font-weight:700;border:1px solid currentColor;border-radius:4px;padding:0 8px;margin-left:6px;white-space:nowrap}"
       ".lv-o{color:#FFFBF6;background:#7A3B1E;border-color:#7A3B1E}.lv-n{color:#7A3B1E}.lv-b{color:#5E4637;border-style:dotted}"
       ".lvlist{list-style:none}.lvlist li{margin:8px 0 !important;font-size:14px}.lvnote{font-size:13px;color:var(--muted);margin-top:8px}"
       ".rsec{font-size:20px;margin:48px 0 6px;padding-top:12px;border-top:2px solid var(--text);scroll-margin-top:72px}"
       ".rlead{font-size:14px;color:var(--muted);margin:0 0 8px}.rlist{list-style:none}.ritem{padding:14px 0;border-bottom:1px solid var(--border)}"
       ".rh{font-size:15px;line-height:1.6}.rt{font-size:15px;line-height:1.85;margin-top:4px}.rj{font-size:13px;color:var(--muted);margin-top:4px;line-height:1.6}"
       ".rl{font-size:13px;margin-top:6px}.rl a,.rfoot a{color:var(--link)}.rfoot{margin-top:40px;font-size:14px}"
       ".gnav a{min-height:44px;display:inline-flex;align-items:center;border-radius:6px}.points{border-radius:8px}")


def _articles(v):
    if isinstance(v, list):
        return [s.strip().strip("/") for s in v if s and s.strip()]
    return [s.strip().strip("/") for s in str(v or "").split(",") if s.strip()]


def load_studies():
    rows = json.loads((ROOT / f"media/{SLUG}-studies.json").read_text())
    by, order = {}, []
    for r in rows:
        key = r["url"].strip().rstrip("/").lower()
        arts = _articles(r.get("article"))
        if key not in by:
            r = dict(r, articles=arts)
            by[key] = r
            order.append(key)
            continue
        cur = by[key]
        for a in arts:
            if a not in cur["articles"]:
                cur["articles"].append(a)
        if LEVELS.get(r.get("level"), (0,))[0] > LEVELS.get(cur.get("level"), (0,))[0]:
            cur["level"] = r["level"]
    return [by[k] for k in order]


def post_titles():
    f = ROOT / f"media/{SLUG}-posts.json"
    posts = json.loads(f.read_text()) if f.exists() else []
    t = {p["slug"]: p["title"] for p in posts}
    site = ROOT / "sites" / SLUG
    for d in site.iterdir() if site.exists() else []:
        if d.is_dir() and d.name not in t and (d / "index.html").exists():
            m = re.search(r"<h1[^>]*>(.*?)</h1>", (d / "index.html").read_text(), re.S)
            if m and '<article' in (d / "index.html").read_text()[:20000]:
                t[d.name] = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return t


def short(title):
    m = re.match(r"^(.+?[？?])", title)
    return m.group(1) if m else title


def build():
    studies = load_studies()
    names = [c[0] for c in CATS]
    unknown = sorted({s["cat"] for s in studies} - set(names))
    if unknown:
        raise SystemExit(f"未知の分野: {unknown}（CATS に足す）")
    titles = post_titles()
    n = len(studies)
    counts = {c: sum(1 for s in studies if s["cat"] == c) for c in names}
    lv_counts = {lv: sum(1 for s in studies if s.get("level") == lv) for lv in LEVELS}

    parts = [f'<p class="xlead">チョコの研究がチョコについて調べた研究{n}件を、7つの分野に分けた一覧です。各行は1〜2行の結論と、どこまで原典を確かめたか（確認レベル）を示します。記事がある研究は記事へつながります。チョコの研究は、カカオバターの結晶と香りの成分の分析が多く、家庭のチョコ作りをそのまま比べた研究は少なめです。</p>',
             '<div class="points"><h2>確認レベルの見方</h2><ul class="lvlist">'
             f'<li><span class="lvb lv-o">数字確認</span> 原典（要旨または本文）を開き、ここに書いた数字と結論を確かめた（{lv_counts["数字確認"]}件）</li>'
             f'<li><span class="lvb lv-n">要旨で照合</span> 原典の要旨を開き、ここに書いた結論を確かめた。本文は読めていないものを含む（{lv_counts["要旨で照合"]}件）</li>'
             f'<li><span class="lvb lv-b">書誌のみ</span> 実在は確かめたが中身は読めていない。中身・数字は載せない（{lv_counts["書誌のみ"]}件）</li>'
             f'</ul><p class="lvnote">記事で数字を使うときは、原典を開き直して照合します。調べた日: {DATE}。</p></div>',
             '<nav class="gnav" aria-label="分野">' + "".join(f'<a href="#r-{cid}">{E(c)}（{counts[c]}）</a>' for c, cid, _ in CATS if counts[c]) + "</nav>"]
    for c, cid, lead in CATS:
        rows = [s for s in studies if s["cat"] == c]
        if not rows:
            continue
        items = []
        for s in rows:
            lv = s.get("level", "書誌のみ")
            css = LEVELS.get(lv, (0, "lv-b"))[1]
            links = [f'<a href="{E(s["url"], quote=True)}" target="_blank" rel="noopener">原典</a>']
            links += [f'<a href="/{a}/">記事: {E(short(titles[a]))}</a>' for a in s["articles"] if a in titles]
            items.append(f'<li class="ritem"><p class="rh"><b>{E(s["authors"])}</b> <span class="lvb {css}">{E(lv)}</span></p>'
                         f'<p class="rt">{E(s["finding"])}</p>'
                         f'<p class="rj"><i>{E(s["title"])}</i>. {E(s["journal"])}</p>'
                         f'<p class="rl">{" ／ ".join(links)}</p></li>')
        parts.append(f'<h2 class="rsec" id="r-{cid}">{E(c)}</h2><p class="rlead">{E(lead)}</p><ul class="rlist">{"".join(items)}</ul>')
    parts.append('<p class="rfoot">テンパリングの温度を、研究の数字をもとに手元で確かめる<a href="/tool/">テンパリング温度ガイド</a>もあります。研究の追加・訂正のご指摘は hi@seadice.win まで。</p>')

    cat_list = "・".join(names)
    page = {
        "path": "research",
        "title": "チョコの研究一覧",
        "seo_title": f"チョコの研究一覧（{n}件・確認レベルつき）",
        "date": DATE,
        "desc": f"チョコの発酵・焙煎・テンパリング・ブルーム・香り・感じ方・体と安全についての研究{n}件を、{cat_list}の7つに分けた一覧。1〜2行の結論と、原典をどこまで確かめたかを表示。",
        "body": "".join(parts),
        "css": CSS,
    }
    pf = ROOT / f"media/{SLUG}-pages.json"
    pages = json.loads(pf.read_text()) if pf.exists() else []
    pages = [p for p in pages if p.get("path") != "research"]
    tool_i = next((i for i, p in enumerate(pages) if p.get("path") == "tool"), None)
    pages.insert(0 if tool_i is None else tool_i + 1, page)
    pf.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n")
    print(f"research: {n} studies ({', '.join(f'{c} {counts[c]}' for c in names)}) -> {pf.relative_to(ROOT)}")


if __name__ == "__main__":
    build()
