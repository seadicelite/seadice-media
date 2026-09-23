"""UMBRA の記事HTMLを組み立てる共通関数（guide種類）。テンプレートの<style>を再利用し、記事ごとの内容だけを差し込む。"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape


def style():
    t = (ROOT / ".claude/commands/umbra-template.html").read_text()
    return re.search(r"<style>.*?</style>", t, re.S).group(0)


def _hero(a):
    """カテゴリ名から画像プール(umbra-images.json)を引いてヒーロー画像のHTMLを返す。見つからない場合は例外を投げる(画像なしで記事を出さないため)。"""
    cfg = json.loads((ROOT / "media/umbra.json").read_text())
    cat = next((c for c in cfg["categories"] if c["name"] == a["category"]), None)
    if cat is None:
        raise ValueError(f"umbra.json に category '{a['category']}' が見つかりません")
    images = json.loads((ROOT / "media/umbra-images.json").read_text())
    img = images.get(f"c-{cat['id']}")
    if img is None:
        raise ValueError(f"umbra-images.json に c-{cat['id']} の画像が登録されていません。画像なしで記事を公開しないでください。")
    return (
        f'<figure class="hero"><img fetchpriority="high" decoding="async" src="{img["src"]}" '
        f'width="{img["w"]}" height="{img["h"]}" alt="{E(img["alt"], quote=True)}">'
        f'<figcaption>Photo: {E(img["artist"])} / <a href="{img["licenseUrl"]}" target="_blank" rel="noopener">{E(img["license"])}</a> / '
        f'<a href="{img["page"]}" target="_blank" rel="noopener">Wikimedia Commons</a></figcaption></figure>'
    )


def make(a):
    """a: dict(slug,title,desc,category,color,date,minutes,lead,summary[3],secs[list],studies[list],steps[list],tips,idea{},faq[list],sources[list])"""
    url = f"https://umbra.seadice.win/{a['slug']}/"
    cites = [s["url"] for s in a["sources"]]
    faq_ld = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": ans}} for q, ans in a["faq"]]
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": a["title"], "datePublished": a["date"], "dateModified": a["date"],
         "author": {"@type": "Organization", "name": "SEADICE"}, "publisher": {"@type": "Organization", "name": "SEADICE", "url": "https://seadice.win"},
         "url": url, "citation": cites},
        {"@type": "FAQPage", "mainEntity": faq_ld},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "UMBRA", "item": "https://umbra.seadice.win/"},
            {"@type": "ListItem", "position": 2, "name": a["title"], "item": url}]}]}, ensure_ascii=False)
    d = E(a["desc"], quote=True)
    studies = "".join(f'<div class="study"><p class="who">{E(s["who"])}<span class="ref">[{s["ref"]}]</span></p><p class="find">{s["find"]}</p><p class="cond">{s["cond"]}</p></div>' for s in a["studies"])
    steps = "".join(f'<div class="step"><div class="num">{i+1}</div><div><p class="ttl">{E(s[0])}</p><p class="dsc">{s[1]}</p><p class="time">{E(s[2])}</p></div></div>' for i, s in enumerate(a["s3"][2]))
    faq = "".join(f'<details><summary>{E(q)}</summary><p>{ans}</p></details>' for q, ans in a["faq"])
    src = "".join(f'<li>{s["text"]} <a href="{s["url"]}" target="_blank" rel="noopener">{s["url"]}</a></li>' for s in a["sources"])
    idea = a["idea"]
    ideali = "".join(f"<li>{x}</li>" for x in idea["features"])
    sec = lambda n, h, ans, inner: f'<h2 class="sec"><span class="n">{n:02d}</span>{h}</h2>\n    <p class="answer">{ans}</p>\n    {inner}\n'
    body = "".join([
        sec(1, a["s1"][0], a["s1"][1], "".join(f'<p class="t">{p}</p>' for p in a["s1"][2])),
        sec(2, "研究でわかっていること", a["s2"], studies),
        sec(3, a["s3"][0], a["s3"][1], steps),
        sec(4, a["s4"][0], a["s4"][1], "<ul>" + "".join(f"<li>{x}</li>" for x in a["s4"][2]) + "</ul>" + (f'<div class="note">{a["note"]}</div>' if a.get("note") else "")),
        sec(5, "この研究から考えた、こんなアプリ", idea["answer"],
            f'<div class="idea"><p class="lb">APP IDEA</p><p class="nm">{E(idea["name"])}</p><p class="ba">{E(idea["ba"])}</p><ul>{ideali}</ul>'
            f'<p class="ask">こんなアプリがあったら使いたいですか？ 感想やほしい機能は <a href="https://seadice.win/#feedback">SEADICEのトップページ</a> から教えてください。</p></div>'),
        sec(6, "よくある質問", a["faq_answer"], faq),
    ])
    hero = _hero(a)
    return f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(a["title"])} | UMBRA</title>
<meta name="description" content="{d}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{E(a["title"], quote=True)} | UMBRA">
<meta property="og:description" content="{d}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{ld}</script>
{style()}
</head>
<body>
<nav>
  <a href="https://seadice.win/" class="nav-logo">SEADICE</a>
  <a href="/" class="r">UMBRA</a>
</nav>
<article>
  <p class="breadcrumb"><a href="/">UMBRA</a> / {E(a["short"])}</p>
  <span class="tag" style="color:{a["color"]};border-color:{a["color"]}">{E(a["category"])}</span>
  <h1>{E(a["title"])}</h1>
  <p class="meta"><time datetime="{a["date"]}">{a["date"]}</time> · 約{a["minutes"]}分で読めます</p>

  {hero}

  <div class="ai-badge"><strong>AIによる調査</strong><span>公開されている研究論文をAI（Claude）が調べ、内容を確認して整理しました。特定の人を診断・判定するものではありません。出典は末尾にあります。</span></div>

  <div class="body">
    <p class="lead">{a["lead"]}</p>

    <div class="summary">
      <h2>3行でわかる</h2>
      <ol>{"".join(f"<li>{x}</li>" for x in a["summary"])}</ol>
    </div>

    {body}
    <div class="sources">
      <h2>出典</h2>
      <ol>{src}</ol>
    </div>
  </div>
</article>
<footer><p><a href="/">UMBRA</a> &nbsp;|&nbsp; <a href="https://seadice.win/">SEADICE</a> &nbsp;|&nbsp; &copy; SEADICE</p></footer>
</body>
</html>
'''
