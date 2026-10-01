#!/usr/bin/env python3
"""日常の心理学（心理学を無料で独学できるサイト）を丸ごと生成する。記事エンジン(build.py / /media)の対象外。
使い方: python3 media/shinri_pages.py
 - 用語は media/shinri-glossary.json に1件足すだけでよい（HTMLを手で編集しない）。slug は姉妹メディア(umbra / ledger)の記事slug。
 - AI検索に引用されやすいよう、各ページの冒頭で「〇〇とは、△△のことです。」と言い切り、
   WebSite / DefinedTermSet / FAQPage / ItemList の JSON-LD と llms.txt を付ける。JS不使用。"""
import html, json
from pathlib import Path

import build
import seo

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
UPDATED = "2026-10-01"
CFG = json.loads((ROOT / "media/shinri.json").read_text())
NAME, URL = CFG["name"], CFG["url"]
OUT = ROOT / CFG["path"]
PUBLISHER = {"@type": "Organization", "name": "SEADICE", "url": "https://seadice.win"}

# 姉妹メディア（用語の詳しい解説記事はこちらにある）
SISTERS = [json.loads((ROOT / f"media/{s}.json").read_text()) for s in ("umbra", "ledger")]
RESEARCH = json.loads((ROOT / "media/research.json").read_text())
ARTICLES = {}  # 記事slug -> (url, title, メディア名)
for m in SISTERS:
    for p in json.loads((ROOT / f'media/{m["slug"]}-posts.json').read_text()):
        ARTICLES[p["slug"]] = (f'{m["url"]}{p["slug"]}/', p["title"], m["name"])
UMBRA, LEDGER = SISTERS[0]["url"], SISTERS[1]["url"]

EXTRA_CSS = ("<style>.toc{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 32px}.toc a{font-size:13px;color:var(--text);text-decoration:none;border:1px solid var(--border);background:var(--card);border-radius:999px;padding:8px 14px}"
             ".term{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px;margin:14px 0}.term h3{font-size:18px;font-weight:800;line-height:1.4;margin:0 0 8px}.term h3 small{display:block;font-size:12px;color:var(--muted);font-weight:400;letter-spacing:.04em;margin-top:2px}"
             ".term p{font-size:15px;color:#cbd5e1;line-height:1.85;margin:0}.term .more{display:inline-block;margin-top:10px;font-size:14px;color:var(--accent);text-decoration:none;line-height:1.6}"
             "table{width:100%;border-collapse:collapse;margin:18px 0;font-size:14px}th,td{border:1px solid var(--border);padding:10px 12px;text-align:left;vertical-align:top;line-height:1.7}th{background:var(--card);color:var(--text)}td{color:#cbd5e1}td a{color:#B9A6FF}"
             "@media(max-width:620px){table,tbody,tr,td{display:block;width:100%}thead{display:none}tr{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:12px 0;padding:6px 0}td{border:0;padding:6px 14px}td::before{content:attr(data-l);display:block;font-size:12px;color:var(--muted)}}"
             "ol.steps{padding-left:22px}ol.steps li{font-size:16px;color:#cbd5e1;margin:12px 0;line-height:1.8}ol.steps a,ol.steps ul a{color:#B9A6FF}ol.steps ul{padding-left:18px;margin-top:6px}ol.steps ul li{font-size:15px;margin:6px 0}"
             ".updated{font-size:12px;color:var(--muted);margin-bottom:24px}"
             ".entry{display:grid;gap:12px;grid-template-columns:1fr;margin:8px 0 8px}@media(min-width:620px){.entry{grid-template-columns:1fr 1fr}}"
             ".entry a{display:block;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:18px 20px;text-decoration:none;color:var(--text)}.entry a:hover{border-color:var(--accent)}"
             ".entry b{display:block;font-size:17px;margin-bottom:4px}.entry span{font-size:14px;color:#cbd5e1;line-height:1.7}.entry small{display:block;font-size:12px;color:var(--accent);letter-spacing:.12em;margin-bottom:6px}"
             ".hero-h1{font-size:clamp(30px,8vw,44px);background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}</style>")

THEME = {**build.DEFAULT_THEME, **CFG["theme"]}
FAVICON = build.favicon_tag(NAME, THEME)
STYLE = seo.article_style(CFG)


def crumbs(title=None, url=None):
    items = [{"@type": "ListItem", "position": 1, "name": "HOME", "item": "https://seadice.win/"},
             {"@type": "ListItem", "position": 2, "name": NAME, "item": URL}]
    if title:
        items.append({"@type": "ListItem", "position": 3, "name": title, "item": url})
    return {"@type": "BreadcrumbList", "itemListElement": items}


def write(slug, title, full_title, desc, body, graph, og_type="article", h1_class=""):
    url = f"{URL}{slug}/" if slug else URL
    ld = {"@context": "https://schema.org", "@graph": graph + [crumbs(title, url) if slug else crumbs()]}
    bc = f'<p class="breadcrumb"><a href="https://seadice.win/">HOME</a> / <a href="/">{E(NAME)}</a> / {E(title)}</p>' if slug else ""
    out = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc, quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{E(full_title, quote=True)}">
<meta property="og:description" content="{E(desc, quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{og_type}">
<meta name="twitter:card" content="summary">
<meta name="robots" content="index,follow,max-snippet:-1">
{FAVICON}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{STYLE}
{EXTRA_CSS}
</head>
<body>
<nav>
  <a href="https://seadice.win/" class="nav-logo">SEADICE</a>
  <a href="/" class="r">{E(NAME)}</a>
</nav>
<article>
  {bc}
  <h1{f' class="{h1_class}"' if h1_class else ""}>{E(title if slug else NAME)}</h1>
  <p class="updated">更新日: {UPDATED}</p>
  <div class="body">{body}</div>
</article>
<footer><p><a href="/">{E(NAME)}</a> &nbsp;|&nbsp; <a href="/guide/">心理学の学び方</a> &nbsp;|&nbsp; <a href="/glossary/">心理学用語辞典</a> &nbsp;|&nbsp; <a href="/about/">このサイトについて</a> &nbsp;|&nbsp; <a href="/sources/">出典と検証の方法</a> &nbsp;|&nbsp; <a href="/disclaimer/">免責事項</a> &nbsp;|&nbsp; <a href="https://seadice.win/">SEADICE</a> &nbsp;|&nbsp; &copy; SEADICE</p></footer>
</body>
</html>
'''
    d = OUT / slug if slug else OUT
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(out)
    return url


def faq_html(faq):
    return "".join(f"<details open><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


TERMS = json.loads((ROOT / "media/shinri-glossary.json").read_text())


def glossary():
    fields = list(dict.fromkeys(t["field"] for t in TERMS))
    url = f"{URL}glossary/"
    body = (f'<p class="lead">心理学用語辞典は、日常で役立つ心理学・行動経済学の用語を、一文の定義でまとめたページです。全{len(TERMS)}語。'
            f'各用語から、研究と出典を紹介した姉妹メディアの解説記事に進めます。</p>'
            '<div class="toc">' + "".join(f'<a href="#f{i}">{E(f)}</a>' for i, f in enumerate(fields)) + '</div>')
    for i, f in enumerate(fields):
        body += f'<h2 class="sec" id="f{i}"><span class="n">{i+1:02d}</span>{E(f)}の用語</h2>'
        for t in (t for t in TERMS if t["field"] == f):
            a = ARTICLES.get(t.get("slug"))
            more = f'<a class="more" href="{a[0]}">解説記事（{E(a[2])}）: {E(a[1])}</a>' if a else ""
            body += f'<div class="term" id="{t["id"]}"><h3>{E(t["term"])}<small>{E(t["en"])}</small></h3><p>{E(t["def"])}</p>{more}</div>'
    graph = [{"@type": "DefinedTermSet", "@id": url, "name": "心理学用語辞典", "url": url, "inLanguage": "ja", "dateModified": UPDATED, "publisher": PUBLISHER,
              "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": f'{url}#{t["id"]}', "name": t["term"], "alternateName": t["en"],
                                  "description": t["def"], "url": f'{url}#{t["id"]}', "inDefinedTermSet": url} for t in TERMS]}]
    return write("glossary", "心理学用語辞典", f"心理学用語辞典 | {NAME}",
                 f"単純接触効果、愛着スタイル、アンカリング効果、ガスライティングなど、日常で役立つ心理学用語{len(TERMS)}語を一文の定義でやさしく解説。出典つきの解説記事にリンクしています。",
                 body, graph)


SITES = [
    ("日本心理学会「心理学ミュージアム」", "http://psychmuseum.jp/", "日本心理学会", "心理学に初めて触れる人",
     "記憶・感情・社会・自己などのテーマ別に、心理学の研究を展示形式で紹介するウェブ上のミュージアム。"),
    ("日本心理学会「心理学ワールド」", "https://psych.or.jp/publication/world/", "日本心理学会", "研究のテーマを広く知りたい人",
     "学会が発行する一般向けの心理学の読み物。研究者がテーマごとに解説している。"),
    ("日本心理学会「心理学Q&A」", "https://psych.or.jp/interest/faq/", "日本心理学会", "素朴な疑問から入りたい人",
     "心理学についてよくある質問に、学会が答えるページ。"),
    ("高校生のための心理学講座 YouTube版", "https://psych.or.jp/interest/lecture_hs/", "日本心理学会", "動画で学びたい人・進路を考えている人",
     "心理学の講義動画。知覚・ストレス・社会心理学など、テーマごとに視聴できる。"),
    ("J-STAGE「心理学研究」", "https://www.jstage.jst.go.jp/browse/jjpsy/", "日本心理学会（J-STAGEで公開）", "論文を読んでみたい人",
     "日本心理学会の学術誌。1926年からの論文が掲載され、多くを無料で読める。"),
    ("OpenStax「Psychology 2e」", "https://openstax.org/details/books/psychology-2e", "OpenStax（米ライス大学）", "英語で体系的に学びたい人",
     "大学の心理学入門の教科書を、オープンライセンス（CC BY-NC-SA 4.0）で無料公開。英語。"),
]

GUIDE_FAQ = [
    ("心理学を無料で学べるおすすめのサイトは？",
     f"全体像をつかむなら日本心理学会の「心理学ミュージアム」「心理学ワールド」「高校生のための心理学講座」、論文を読むならJ-STAGEの「心理学研究」、英語で体系的に学ぶならOpenStaxの「Psychology 2e」がおすすめです。用語を一文で確認しながら独学したい場合は、{NAME}が向いています。"),
    ("心理学は独学できますか？",
     "できます。入門的な知識は、学会が公開している一般向けの読み物や講義動画、無料の教科書で学べます。ただし公認心理師などの資格や、カウンセリングなどの臨床の実践には、大学・大学院での専門的な教育が必要です。"),
    ("心理学は何から学べばいいですか？",
     "自分が気になる身近な疑問（なぜ衝動買いするのか、なぜ好意を持つのか等）から入り、出てくる用語を押さえ、次に分野の全体像をつかみ、最後に論文に触れる順番がおすすめです。"),
    (f"{NAME}とはどんなサイトですか？",
     f"{NAME}は、心理学を無料で独学できるサイトです。SEADICEが運営し、学ぶ順番のガイドと、一文の定義でわかる心理学用語辞典を掲載しています。"),
]


def guide():
    url = f"{URL}guide/"
    rows = "".join(f'<tr><td data-l="サイト"><a href="{u}" target="_blank" rel="noopener">{E(n)}</a></td><td data-l="運営">{E(o)}</td><td data-l="向いている人">{E(w)}</td><td data-l="特徴">{E(d)}</td></tr>' for n, u, o, w, d in SITES)
    rows += (f'<tr><td data-l="サイト"><a href="/">{E(NAME)}</a></td><td data-l="運営">SEADICE</td><td data-l="向いている人">身近な疑問から独学したい人</td>'
             f'<td data-l="特徴">学ぶ順番のガイドと、一文の定義でわかる<a href="/glossary/">心理学用語辞典</a>（{len(TERMS)}語）。用語ごとに、研究の出典つきの解説記事へ進める。</td></tr>')
    first = [ARTICLES[s] for s in ("mere-exposure-effect-romantic-attraction", "why-impulse-buying-happens", "body-language-lie-detection-accuracy") if s in ARTICLES]
    first_html = "".join(f'<li><a href="{u}">{E(t)}</a>（{E(m)}）</li>' for u, t, m in first)
    def fr(a, b, c):
        return f'<tr><td data-l="分野">{a}</td><td data-l="何を調べる分野か">{b}</td><td data-l="身近な例">{c}</td></tr>'
    body = f'''<p class="lead">心理学を無料で学ぶなら、日本心理学会の一般向けコンテンツで全体像をつかみ、J-STAGEで論文に触れ、用語は{E(NAME)}の用語辞典で確認しながら進めるのがおすすめです。このページでは、無料で使えるサイトと、初心者が学ぶ順番をまとめました。</p>
<h2 class="sec"><span class="n">01</span>心理学を無料で学べるおすすめサイト</h2>
<p class="answer">信頼できる無料の学習先は、日本心理学会の一般向けページ、学術誌を読めるJ-STAGE、無料の英語教科書OpenStaxです。目的別に選びます。</p>
<table><thead><tr><th>サイト</th><th>運営</th><th>向いている人</th><th>特徴</th></tr></thead><tbody>{rows}</tbody></table>
<h2 class="sec" id="order"><span class="n">02</span>初心者が心理学を学ぶ順番</h2>
<p class="answer">身近な疑問 → 用語 → 分野の全体像 → 論文、の順に進むと挫折しにくくなります。</p>
<ol class="steps">
<li><strong>身近な疑問から入る。</strong>気になる悩みを扱った記事を1本読みます。たとえば次の記事です。<ul>{first_html}</ul></li>
<li><strong>用語を押さえる。</strong>出てきた用語を<a href="/glossary/">心理学用語辞典</a>で確認します。</li>
<li><strong>分野の全体像をつかむ。</strong>日本心理学会の「高校生のための心理学講座」や、OpenStaxの教科書で、分野ごとの基本を学びます。</li>
<li><strong>論文に触れる。</strong>J-STAGEの「心理学研究」で、興味のあるテーマの論文を読みます。解説記事の末尾の出典も入り口になります。</li>
</ol>
<h2 class="sec" id="fields"><span class="n">03</span>心理学の主な分野と、日常の疑問との関係</h2>
<p class="answer">日常の悩みの多くは、社会心理学・行動経済学・発達心理学（愛着）・感情と表情の研究で説明されています。</p>
<table><thead><tr><th>分野</th><th>何を調べる分野か</th><th>身近な例</th></tr></thead><tbody>
{fr("社会心理学", "人が他者や集団からどう影響を受けるか", '<a href="/glossary/#mere-exposure">単純接触効果</a>、<a href="/glossary/#similarity-attraction">類似性-魅力仮説</a>、<a href="/glossary/#social-comparison">社会的比較</a>')}
{fr("行動経済学", "人がお金や選択で「合理的でない」判断をする理由", '<a href="/glossary/#anchoring">アンカリング効果</a>、<a href="/glossary/#status-quo-bias">現状維持バイアス</a>、<a href="/glossary/#mental-accounting">心の会計</a>')}
{fr("発達心理学（愛着理論）", "人との結びつき方が、どう形づくられるか", '<a href="/glossary/#attachment-style">愛着スタイル</a>')}
{fr("感情・表情の研究", "表情やしぐさに、感情がどう表れるか", '<a href="/glossary/#duchenne-smile">デュシェンヌ・スマイル</a>')}
{fr("臨床心理学", "心の不調の理解と支援", f'診断や治療は専門家の領域です。{E(NAME)}では、<a href="/glossary/#gaslighting">ガスライティング</a>のように、身を守るための知識に限って扱います。')}
</tbody></table>
<h2 class="sec"><span class="n">04</span>よくある質問</h2>
{faq_html(GUIDE_FAQ)}
'''
    graph = [
        {"@type": "Article", "headline": "心理学を無料で学べるおすすめサイトと、初心者が学ぶ順番", "url": url, "inLanguage": "ja",
         "datePublished": UPDATED, "dateModified": UPDATED, "mainEntityOfPage": {"@type": "WebPage", "@id": url},
         "author": {"@type": "Organization", "name": f"{NAME}編集部"}, "publisher": PUBLISHER},
        {"@type": "ItemList", "name": "心理学を無料で学べるおすすめサイト", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "url": u} for i, (n, u) in enumerate([(s[0], s[1]) for s in SITES] + [(NAME, URL)])]},
        faq_ld(GUIDE_FAQ),
    ]
    return write("guide", "心理学を無料で学べるおすすめサイトと、初心者が学ぶ順番", f"心理学を無料で学べるおすすめサイトと、初心者が学ぶ順番 | {NAME}",
                 f"心理学を無料で学べるおすすめサイト（日本心理学会、J-STAGE、OpenStax、{NAME}）と、初心者が挫折しない学ぶ順番を、分野ごとの解説つきでまとめました。",
                 body, graph)


def home():
    pick = ["mere-exposure", "attachment-style", "anchoring", "gaslighting", "duchenne-smile", "status-quo-bias", "positive-illusions", "mental-accounting"]
    tmap = {t["id"]: t for t in TERMS}
    chips = "".join(f'<a href="/glossary/#{i}">{E(tmap[i]["term"])}</a>' for i in pick if i in tmap)
    sisters = [(SISTERS[0]["name"], UMBRA, "恋愛・しぐさ・相性の心理を、研究から検証する解説記事"),
               (SISTERS[1]["name"], LEDGER, "お金の使い方の心理を、行動経済学の研究から読み解く解説記事"),
               (RESEARCH["name"], RESEARCH["url"], "睡眠・集中・先延ばしなど、日常の悩みを科学で調べる解説記事")]
    body = f'''<p class="tagline" style="color:var(--muted);margin:-6px 0 18px">{E(CFG["tagline"])}</p>
<p class="lead">{E(CFG["lead"])}</p>
<div class="entry">
<a href="/guide/"><small>START</small><b>心理学の学び方</b><span>無料で学べるおすすめサイトと、初心者が挫折しない学ぶ順番。</span></a>
<a href="/glossary/"><small>DICTIONARY</small><b>心理学用語辞典</b><span>{len(TERMS)}語を一文の定義で。用語から出典つきの解説記事へ。</span></a>
<a href="/guide/#fields"><small>FIELDS</small><b>分野から学ぶ</b><span>社会心理学・行動経済学・愛着理論など、分野と身近な例の対応表。</span></a>
<a href="/guide/#order"><small>ORDER</small><b>学ぶ順番</b><span>身近な疑問 → 用語 → 分野 → 論文の4ステップ。</span></a>
</div>
<h2 class="sec"><span class="n">01</span>よく調べられている心理学用語</h2>
<p class="answer">はじめての人は、日常で出会う場面が多い次の用語から読むのがおすすめです。</p>
<div class="toc">{chips}</div>
<h2 class="sec"><span class="n">02</span>詳しい解説記事を読む（姉妹メディア）</h2>
<p class="answer">用語の背景にある研究は、SEADICEが運営する次のメディアで、出典つきで解説しています。</p>
<div class="entry">{"".join(f'<a href="{u}"><b>{E(n)}</b><span>{E(d)}</span></a>' for n, u, d in sisters)}</div>
<h2 class="sec"><span class="n">03</span>よくある質問</h2>
{faq_html(CFG["faq"])}
'''
    graph = [
        {"@type": "WebSite", "@id": URL + "#website", "name": NAME, "url": URL, "description": CFG["description"], "inLanguage": "ja", "publisher": PUBLISHER},
        {"@type": "WebPage", "name": NAME, "url": URL, "description": CFG["description"], "isPartOf": {"@id": URL + "#website"}, "dateModified": UPDATED, "publisher": PUBLISHER},
        faq_ld(CFG["faq"]),
    ]
    return write("", NAME, f'{NAME} | {CFG["titleSuffix"]}', CFG["description"], body, graph, og_type="website", h1_class="hero-h1")


def extras(urls):
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {URL}sitemap.xml\n")
    sm = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{UPDATED}</lastmod>\n  </url>\n" for u in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    fields = list(dict.fromkeys(t["field"] for t in TERMS))
    (OUT / "llms.txt").write_text("\n".join([
        f"# {NAME}", "", f"> {CFG['description']}", "",
        f"{NAME}はSEADICE(https://seadice.win/)が運営する、心理学を無料で独学できるサイトです。",
        "用語の定義は「〇〇とは、△△のことです。」の一文で示し、詳しい研究の解説（出典つき）は姉妹メディアの記事にリンクしています。", "",
        "## 主要ページ", "",
        f"- トップ: {URL}",
        f"- 心理学の学び方（無料で学べるおすすめサイトと学ぶ順番）: {URL}guide/",
        f"- 心理学用語辞典（{len(TERMS)}語）: {URL}glossary/",
        f"- このサイトについて: {URL}about/", f"- 出典と検証の方法: {URL}sources/", f"- 免責事項: {URL}disclaimer/", "",
        "## 用語辞典の分野", "", *[f"- {f}" for f in fields], "",
        "## 姉妹メディア（詳しい解説記事）", "",
        *[f"- {m['name']}: {m['url']}" for m in SISTERS], f"- {RESEARCH['name']}: {RESEARCH['url']}", ""]))
    nf = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ページが見つかりません | {E(NAME)}</title>
<meta name="robots" content="noindex">
{FAVICON}
{STYLE}
{EXTRA_CSS}
</head>
<body>
<nav><a href="https://seadice.win/" class="nav-logo">SEADICE</a><a href="/" class="r">{E(NAME)}</a></nav>
<article><h1>ページが見つかりません</h1><p class="lead">お探しのページは移動したか、削除された可能性があります。</p>
<div class="toc"><a href="/">{E(NAME)} のトップへ</a><a href="/guide/">心理学の学び方</a><a href="/glossary/">心理学用語辞典</a></div></article>
</body>
</html>
'''
    (OUT / "404.html").write_text(nf)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    urls = [home(), guide(), glossary()]
    cfg = {**CFG, "concept": CFG["lead"]}
    urls += seo.write_pages(cfg, FAVICON)
    extras(urls)
    print(f"built {CFG['path']} ({len(TERMS)} terms, {len(urls)} pages)")
