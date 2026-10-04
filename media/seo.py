"""SEO の後処理。build.py から毎回呼ばれ、既存の全記事に対して冪等に次を適用する。
 - og:image / twitter:image / robots(max-image-preview) / preconnect / ヒーロー画像の fetchpriority
 - Article 構造化データの強化(image, mainEntityOfPage, inLanguage, articleSection)
 - 関連記事ブロック(同じ分野を優先して3本)
 - フッターに /about/ /sources/ /disclaimer/ へのリンク
 - 信頼ページ(about / sources / disclaimer)の生成
JS 不使用。"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
LD = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
RELATED_CSS = (".related{margin-top:56px;padding-top:24px;border-top:1px solid var(--border)}.related h2{font-size:14px;margin:0 0 12px;color:var(--muted);letter-spacing:.1em}"
               ".related a{display:flex;gap:12px;align-items:center;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:10px;margin:10px 0;text-decoration:none;color:var(--text)}.related a:hover{border-color:var(--accent)}"
               ".related .rt{flex:0 0 72px;width:72px;height:72px;border-radius:8px;overflow:hidden;background:var(--border)}.related .rt img{display:block;width:100%;height:100%;object-fit:cover}"
               ".related .rb{min-width:0}.related small{display:block;font-size:12px;color:var(--accent);font-weight:400;margin-bottom:2px}.related .rb p{font-size:15px;font-weight:700;line-height:1.4;margin:0}")


PREVNEXT_CSS = (".prevnext{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:24px}"
                ".prevnext a{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--text)}.prevnext a:hover{border-color:var(--accent)}"
                ".prevnext small{display:block;font-size:12px;color:var(--accent);margin-bottom:4px}"
                ".prevnext p{font-size:13px;font-weight:700;line-height:1.4;margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}"
                "@media(max-width:480px){.prevnext{grid-template-columns:1fr}}")

LEGACY_CAT_ID = {"睡眠": "sleep", "集中力": "focus", "先延ばし": "delay", "気分・ストレス": "mood", "習慣": "habit", "記憶・学習": "memory"}


def _img_url(i, w=200, h=200):
    if "src" in i:
        return i["src640"] if w <= 640 else i["src"]
    return f"{i['raw']}&w={w}&h={h}&fit=crop&q=70&fm=webp"


def cat_id(cfg, name):
    for c in cfg.get("categories", []):
        if isinstance(c, dict) and c.get("name") == name:
            return c["id"]
    return LEGACY_CAT_ID.get(name, "x")


def prevnext_block(p, posts):
    if len(posts) < 2:
        return "<!--prevnext--><!--/prevnext-->"
    idx = next((i for i, q in enumerate(posts) if q["slug"] == p["slug"]), None)
    if idx is None:
        return "<!--prevnext--><!--/prevnext-->"
    prev_p = posts[idx - 1] if idx > 0 else posts[-1]
    next_p = posts[idx + 1] if idx < len(posts) - 1 else posts[0]
    def link(q, label):
        return f'<a href="/{q["slug"]}/"><small>{label}</small><p>{E(q["title"])}</p></a>'
    return f'<!--prevnext--><nav class="prevnext">{link(prev_p, "前の記事")}{link(next_p, "次の記事")}</nav><!--/prevnext-->'


def article_style(cfg):
    t = (ROOT / cfg["template"]).read_text()
    return re.search(r"<style>.*?</style>", t, re.S).group(0)


def footer_html(cfg):
    n = E(cfg["name"])
    return (f'<footer><p><a href="/">{n}</a> &nbsp;|&nbsp; <a href="/about/">このメディアについて</a> &nbsp;|&nbsp; <a href="/sources/">出典と検証の方法</a> '
            f'&nbsp;|&nbsp; <a href="/disclaimer/">免責事項</a> &nbsp;|&nbsp; <a href="https://seadice.win/">SEADICE</a> &nbsp;|&nbsp; &copy; SEADICE</p></footer>')


def related_block(p, posts, images):
    others = [q for q in posts if q["slug"] != p["slug"]]
    same = [q for q in others if q["category"] == p["category"]]
    rest = [q for q in others if q["category"] != p["category"]]
    pick = (same + rest)[:3]  # posts は build.py が日替わりでシャッフル済み。関連記事も毎日入れ替わる
    if not pick:
        return "<!--related--><!--/related-->"
    def item(q):
        img = images.get(q["slug"])
        thumb = f'<img src="{_img_url(img)}" alt="" width="200" height="200" loading="lazy" decoding="async">' if img else ""
        return (f'<a href="/{q["slug"]}/"><span class="rt">{thumb}</span>'
                f'<span class="rb"><small>{E(q["category"])}</small><p>{E(q["title"])}</p></span></a>')
    items = "".join(item(q) for q in pick)
    return f'<!--related--><section class="related"><h2>関連記事</h2>{items}</section><!--/related-->'


def shinri_block(slug):
    sc = ROOT / "media/shinri.json"
    gl = ROOT / "media/shinri-glossary.json"
    if not (sc.exists() and gl.exists()):
        return "<!--shinri--><!--/shinri-->"
    cfg = json.loads(sc.read_text())
    terms = [t for t in json.loads(gl.read_text()) if t.get("slug") == slug]
    if not cfg.get("live") or not terms:
        return "<!--shinri--><!--/shinri-->"
    u = cfg["url"]
    links = "、".join(f'<a href="{u}glossary/#{t["id"]}">{E(t["term"])}</a>' for t in terms)
    return (f'<!--shinri--><div class="note"><strong>この記事の心理学用語:</strong> {links}（{E(cfg["name"])}の心理学用語辞典）<br>'
            f'心理学を基礎から学ぶなら、無料講座「<a href="{u}course/">ゼロから学ぶ心理学入門</a>」へ。</div><!--/shinri-->')


def patch_article(cfg, p, posts, images, favicon=""):
    f = ROOT / cfg["path"] / p["slug"] / "index.html"
    if not f.exists():
        return False
    s = f.read_text()
    url = f'{cfg["url"]}{p["slug"]}/'
    # --- アクセシビリティ(設定 a11yFix のメディアだけ): 本文を<main>で囲む・ナビのタップ領域を44px以上に
    if cfg.get("a11yFix"):
        if "<main" not in s and "\n<article>" in s:
            s = s.replace("\n<article>", "\n<main>\n<article>", 1).replace("</article>", "</article>\n</main>", 1)
        if 'id="tap"' not in s:
            s = s.replace("</head>", '<style id="tap">nav a{display:inline-flex;align-items:center;min-height:44px}</style>\n</head>', 1)
    img = images.get(p["slug"])
    src = (img.get("og") or img.get("src")) if img else None  # og: SNS用JPEG(自サイト配信時)
    if src and src.startswith("/"):
        src = cfg["url"].rstrip("/") + src  # og:image・構造化データは絶対URLが必要
    # --- favicon(既存があれば入れ替え、無ければ追加)
    if favicon:
        s = re.sub(r'<link rel="icon"[^>]*>\n?', "", s)
        s = re.sub(r'(<meta name="twitter:card"[^>]*>\n)', lambda m: m.group(1) + favicon + "\n", s, count=1) if favicon not in s else s
    # --- head: 重複を除いて入れ直す
    for pat in (r'<meta property="og:image"[^>]*>\n?', r'<meta name="twitter:image"[^>]*>\n?', r'<meta name="robots"[^>]*>\n?',
                r'<link rel="preconnect" href="https://upload\.wikimedia\.org"[^>]*>\n?', r'<meta property="og:image:alt"[^>]*>\n?'):
        s = re.sub(pat, "", s)
    add = '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">\n'
    if src:
        add += (f'<meta property="og:image" content="{src}">\n<meta property="og:image:alt" content="{E(img["alt"], quote=True)}">\n'
                f'<meta name="twitter:image" content="{src}">\n' + ('<link rel="preconnect" href="https://upload.wikimedia.org" crossorigin>\n' if "upload.wikimedia.org" in src else ""))
        s = re.sub(r'<meta name="twitter:card" content="[^"]*">', '<meta name="twitter:card" content="summary_large_image">', s)
    else:
        s = re.sub(r'<meta name="twitter:card" content="[^"]*">', '<meta name="twitter:card" content="summary">', s)
    s = re.sub(r'(<meta name="twitter:card"[^>]*>\n)', lambda m: m.group(1) + add, s, count=1)
    # --- メディア固有の記事デザイン(cfg の articleCss)を後から差し込む。過去記事にも効く
    s = re.sub(r'<style id="theme">.*?</style>\n?', "", s, flags=re.S)
    if cfg.get("articleCss"):
        s = s.replace("</head>", f'<style id="theme">{cfg["articleCss"]}</style>\n</head>', 1)
    # --- 構造化データ(Article を強化)
    def fix_ld(m):
        try:
            d = json.loads(m.group(2))
        except Exception:
            return m.group(0)
        for node in d.get("@graph", []):
            if node.get("@type") == "Article":
                node["mainEntityOfPage"] = {"@type": "WebPage", "@id": url}
                node["inLanguage"] = "ja"
                node["articleSection"] = p["category"]
                node["isAccessibleForFree"] = True
                if src:
                    node["image"] = [src]
                else:
                    node.pop("image", None)
        return m.group(1) + json.dumps(d, ensure_ascii=False) + m.group(3)
    s = LD.sub(fix_ld, s, count=1)
    # --- ヒーロー画像の優先読み込み
    s = re.sub(r'(<figure class="hero"><img )(?!fetchpriority)', r'\1fetchpriority="high" decoding="async" ', s)
    # --- 関連記事
    old_related_css = ".related{margin-top:56px;padding-top:24px;border-top:1px solid var(--border)}.related h2{font-size:14px;margin:0 0 12px;color:var(--muted);letter-spacing:.1em}.related a{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 16px;margin:10px 0;text-decoration:none;color:var(--text);font-size:15px;font-weight:700;line-height:1.5}.related a:hover{border-color:var(--accent)}.related small{display:block;font-size:12px;color:var(--accent);font-weight:400;margin-bottom:2px}"
    if old_related_css in s:
        s = s.replace(old_related_css, RELATED_CSS, 1)
    elif ".related .rt{" not in s:
        s = s.replace("footer{border-top", RELATED_CSS + "footer{border-top", 1)
    blk = related_block(p, posts, images)
    if "<!--related-->" in s:
        s = re.sub(r"<!--related-->.*?<!--/related-->", lambda m: blk, s, flags=re.S)
    else:
        s = s.replace('<div class="sources">', blk + '\n    <div class="sources">', 1)
    # --- 前後の記事ナビ
    if ".prevnext{" not in s:
        s = s.replace("footer{border-top", PREVNEXT_CSS + "footer{border-top", 1)
    # テンプレートの nav{position:fixed}(上部ナビ用)が前後ナビにも効いて画面上部に重なるのを打ち消す
    PN_FIX = "nav.prevnext{position:static;height:auto;padding:0;background:none;border:0;backdrop-filter:none;-webkit-backdrop-filter:none;z-index:auto}"
    if PN_FIX not in s:
        s = s.replace("</head>", f"<style>{PN_FIX}</style>\n</head>", 1)
    pn = prevnext_block(p, posts)
    if "<!--prevnext-->" in s:
        s = re.sub(r"<!--prevnext-->.*?<!--/prevnext-->", lambda m: pn, s, flags=re.S)
    else:
        s = s.replace('<div class="sources">', pn + '\n    <div class="sources">', 1)
    # --- カテゴリタグをカテゴリ専用ハブページへのリンクにする（独立URLでSEO評価を受けられるように）
    cid = cat_id(cfg, p["category"])
    s = re.sub(r'<span class="tag"( style="[^"]*")?>([^<]*)</span>', rf'<a class="tag"\1 href="/category/{cid}/">\2</a>', s, count=1)
    s = re.sub(r'(<a class="tag"(?: style="[^"]*")?) href="/#c-[a-z]+"', rf'\1 href="/category/{cid}/"', s, count=1)
    if 'a.tag{text-decoration:none}' not in s:
        s = s.replace("footer{border-top", "a.tag{text-decoration:none}" + "footer{border-top", 1)
    # --- アクセシビリティ: 12px未満の文字をなくし、キーボード操作時のフォーカス表示を付ける
    s = re.sub(r'font-size:1[01](?:\.\d+)?px', 'font-size:12px', s)
    if "a:focus-visible" not in s:
        s = s.replace("footer{border-top", "a:focus-visible,summary:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}" + "footer{border-top", 1)
    # --- 独学サイト「日常の心理学」への送客（用語辞典に対応する用語がある記事だけ。media/shinri.json の live が true のときだけ出す）
    blk = shinri_block(p["slug"])
    if "<!--shinri-->" in s:
        s = re.sub(r"<!--shinri-->.*?<!--/shinri-->", lambda m: blk, s, flags=re.S)
    elif blk != "<!--shinri--><!--/shinri-->":
        s = s.replace("<!--related-->", blk + "\n    <!--related-->", 1)
    # --- フッター
    s = re.sub(r"<footer>.*?</footer>", lambda m: footer_html(cfg), s, count=1, flags=re.S)
    f.write_text(s)
    return True


PAGES = {
 "about": ("このメディアについて", "{name}の運営方針と、記事がどのように作られているかを説明します。", lambda c: [
   ("運営", ["{name} は、アプリスタジオ SEADICE（シーダイス）が運営するメディアです。", "{concept_short}"]),
   ("記事の作り方", ["記事は、AI（Claude）が公開されている研究論文や公的機関の資料を調べ、内容を確認して整理し、作成しています。SEADICE が独自に実験や調査をしたものではありません。",
                     "AI が作成した記事は、公開前に、出典の照合など決められた検査を通ったものだけを掲載します。検査を通らなかった記事は公開しません。"]),
   ("編集方針", ["確認できた出典だけを書きます。確認できなかった数値や主張は書きません。", "研究の対象や限界を、できるだけ添えて紹介します。断定は避け、「研究ではこうだった」と書きます。"]),
   ("お問い合わせ", ['記事の誤りのご指摘や、ご意見は <a href="mailto:hi@seadice.win">hi@seadice.win</a> までご連絡ください。'])]),
 "sources": ("出典と検証の方法", "{name}で使う出典の基準と、記事の検証方法を説明します。", lambda c: [
   ("使う出典", ["査読のある学術論文、メタ分析・システマティックレビュー、大学や公的機関の資料を使います。", "各記事の末尾に、著者、発行年、タイトル、掲載誌、リンクを載せています。"]),
   ("検証の方法", ["1. 論文の原典（要旨や本文）を開き、記事に書く数値と主張が、原典に書かれていることを1件ずつ照合します。",
                   "2. 原典が開けない場合は、別の信頼できる情報源（公的データベースや大学の発表）で確認できた内容だけを使います。",
                   "3. 確認できなかった数値や主張は、記事から削除します。"]),
   ("写真", ["記事の写真は、Wikimedia Commons の、自由に利用できるライセンス（パブリックドメイン、CC0、CC BY、CC BY-SA）の素材を使い、撮影者とライセンスを各記事に表示しています。"]),
   ("訂正について", ["誤りがあれば、確認のうえ修正し、記事の日付を更新します。ご指摘は hi@seadice.win までお願いします。"])]),
 "disclaimer": ("免責事項", "{name}の記事の利用にあたっての注意事項です。", lambda c: [
   ("情報の性質", ["{name}の記事は、公開された研究をもとにした一般的な情報の提供であり、診断、治療、法律上の助言の代わりになるものではありません。", "研究の結果は、対象となった集団についての傾向であり、すべての人に当てはまるとは限りません。"]),
   ("専門家への相談", ["心身の不調や、被害・トラブルが深刻な場合は、医師、専門の医療機関、法律の専門家、各種の公的な相談窓口に相談してください。"]),
   ("特定の人物について", ["記事の内容を使って、特定の人物を診断したり、決めつけたりすることは、お勧めしません。"]),
   ("責任の範囲", ["記事の内容には、正確を期していますが、その完全性や、特定の目的への適合性を保証するものではありません。記事を参考にした行動の結果について、当メディアは責任を負いません。"])]),
}


def write_pages(cfg, favicon=""):
    st = article_style(cfg) + (f'<style id="theme">{cfg["articleCss"]}</style>' if cfg.get("articleCss") else "")
    concept = cfg.get("concept", "")
    concept_short = cfg.get("tagline", "")
    urls = []
    for slug, (title, desc, builder) in PAGES.items():
        ctx = {"name": cfg["name"], "concept_short": concept_short}
        secs = (cfg.get("pageSections") or {}).get(slug) or builder(cfg)  # cfgでメディア固有の文面に上書きできる
        body = "".join(
            f'<h2 class="sec"><span class="n">{i+1:02d}</span>{E(h)}</h2>' + "".join(f'<p class="t">{(x.format(**ctx) if "{" in x else x)}</p>' for x in ps)
            for i, (h, ps) in enumerate(secs))
        ttl = f'{title} | {cfg["name"]}'
        url = f'{cfg["url"]}{slug}/'
        ld = json.dumps({"@context": "https://schema.org", "@graph": [
            {"@type": "AboutPage" if slug == "about" else "WebPage", "name": ttl, "url": url, "inLanguage": "ja",
             "isPartOf": {"@type": "WebSite", "name": cfg["name"], "url": cfg["url"]},
             "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
            {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": cfg["name"], "item": cfg["url"]},
                                                          {"@type": "ListItem", "position": 2, "name": title, "item": url}]}]}, ensure_ascii=False)
        page = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(ttl)}</title>
<meta name="description" content="{E(desc.format(name=cfg["name"]), quote=True)}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{E(ttl, quote=True)}">
<meta property="og:description" content="{E(desc.format(name=cfg["name"]), quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<meta name="robots" content="index,follow">
{favicon}
<script type="application/ld+json">{ld}</script>
{st}
</head>
<body>
<nav>
  <a href="https://seadice.win/" class="nav-logo">SEADICE</a>
  <a href="/" class="r">{E(cfg["name"])}</a>
</nav>
<article>
  <p class="breadcrumb"><a href="/">{E(cfg["name"])}</a> / {E(title)}</p>
  <h1>{E(title)}</h1>
  <div class="body">{body}</div>
</article>
{footer_html(cfg)}
</body>
</html>
'''
        d = ROOT / cfg["path"] / slug
        d.mkdir(parents=True, exist_ok=True)
        (d / "index.html").write_text(page)
        urls.append(url)
    return urls


INDEXNOW_KEY = "5e7c2a9d41b84f6fa3c0d8e2b917f4a6"
AI_BOTS = ["GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User", "PerplexityBot",
           "Perplexity-User", "Google-Extended", "Applebot-Extended", "Bingbot", "CCBot", "Meta-ExternalAgent", "Amazonbot", "DuckAssistBot"]


def _text(fragment):
    """HTML断片をAIが読みやすいプレーンテキストにする(段落・見出し・リストは改行を保つ)。"""
    t = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", fragment, flags=re.S)
    t = re.sub(r"<span class=\"ref\">\[(\d+)\]</span>", r"[\1]", t)
    t = re.sub(r'<span class="n">(\d+)</span>', r"\1 ", t)
    t = re.sub(r'<div class="num">(\d+)</div>\s*<div>\s*<p class="ttl">(.*?)</p>', r"\n\1. \2: ", t, flags=re.S)
    t = re.sub(r"<h2[^>]*>(.*?)</h2>", lambda m: "\n## " + re.sub("<[^>]+>", "", m.group(1)).strip() + "\n", t, flags=re.S)
    t = re.sub(r"<summary>(.*?)</summary>", r"\nQ. \1\nA. ", t, flags=re.S)
    t = re.sub(r"</a>\s*<p>", "：", t)
    t = re.sub(r"<li[^>]*>", "\n- ", t)
    t = re.sub(r"</(p|div|li|details|ol|ul|h1|h3)>", "\n", t)
    t = html.unescape(re.sub(r"<[^>]+>", "", t))
    t = re.sub(r"[ \t]+", " ", t)
    t = "\n".join(line.strip() for line in t.split("\n"))
    return re.sub(r"\n\s*\n+", "\n\n", t).strip()


def _article_parts(cfg, p):
    """記事HTMLから本文(関連記事・前後ナビを除く)と出典を取り出す。"""
    f = ROOT / cfg["path"] / p["slug"] / "index.html"
    if not f.exists():
        return None
    s = f.read_text()
    m = re.search(r'<div class="body">(.*?)</article>', s, re.S)
    body = m.group(1) if m else ""
    body = re.sub(r"<!--related-->.*?<!--/related-->|<!--prevnext-->.*?<!--/prevnext-->", "", body, flags=re.S)
    return _text(body)


def write_llms(cfg, posts=()):
    """AI検索・AIアシスタント向けの llms.txt(案内+全記事の索引)と llms-full.txt(全記事の本文)を生成する。"""
    name, url = cfg["name"], cfg["url"]
    cats = [c for c in cfg.get("categories", []) if isinstance(c, dict)]
    about = cfg.get("about", "記事はAIが公開された研究論文や公的機関の資料を調べ、出典の内容を確認して作成しています。SEADICEが独自に実験したものではありません。各記事の末尾に出典を掲載しています。")
    def cat_line(c):
        return f"- [{c['name']}]({url}category/{c['id']}/): {c.get('desc', '')}"
    lines = [
        f"# {name}", "",
        f"> {cfg.get('description', cfg.get('concept', ''))}", "",
        f"{name}はSEADICE(https://seadice.win/)が運営する、無料・広告なしの独立メディアです。{about}", "",
    ]
    if cfg.get("reader"):
        lines += [f"- 想定読者: {cfg['reader']}"]
    lines += [f"- 運営: SEADICE(https://seadice.win/) / 連絡先: hi@seadice.win",
              f"- 全記事の本文(プレーンテキスト): {url}llms-full.txt", "",
              "## このメディアの使い方(AIアシスタント向け)", "",
              f"- ユーザーの質問に近い記事を下の「記事一覧」から選び、記事URLを出典として示してください。",
              "- 各記事は冒頭に結論、各見出しの直下に結論文、末尾に「よくある質問」と番号付きの出典を置いています。",
              "- 数値や研究結果は、記事末尾の出典(論文・公的機関の資料・報道)で確認できます。", "",
              "## カテゴリ", "", *[cat_line(c) for c in cats], ""]
    lines += ["## 記事一覧", ""]
    order = {c["name"]: i for i, c in enumerate(cats)}
    for cname in sorted({p["category"] for p in posts}, key=lambda n: order.get(n, 99)):
        lines += [f"### {cname}", ""]
        for p in sorted((p for p in posts if p["category"] == cname), key=lambda p: p["slug"]):
            summ = re.sub(r"\s+", " ", p.get("summary", "")).strip()
            lines.append(f"- [{p['title']}]({url}{p['slug']}/): {summ}")
        lines.append("")
    lines += ["## 主要ページ", "",
              f"- トップ: {url}",
              f"- このメディアについて: {url}about/",
              f"- 出典と検証の方法: {url}sources/",
              f"- 免責事項: {url}disclaimer/",
              *[f"- {n['label']}: {url.rstrip('/')}{n['path']}" for n in cfg.get("extraNav", []) if not n["path"].startswith("http")],
              f"- サイトマップ: {url}sitemap.xml"]
    out = ROOT / cfg["path"]
    (out / "llms.txt").write_text("\n".join(lines) + "\n")
    full = [f"# {name} 全記事本文", "", f"> {cfg.get('description', '')}", "",
            f"出典: {url} (SEADICE運営)。引用の際は各記事のURLを示してください。", ""]
    for p in sorted(posts, key=lambda p: p["slug"]):
        text = _article_parts(cfg, p)
        if not text:
            continue
        full += ["---", "", f"# {p['title']}", "", f"URL: {url}{p['slug']}/", f"カテゴリ: {p['category']}",
                 f"公開日: {p.get('date', '')}", "", text, ""]
    (out / "llms-full.txt").write_text("\n".join(full) + "\n")


def write_robots(cfg):
    """AIクローラーを明示的に許可し、sitemap と llms.txt の場所を示す robots.txt を書く。"""
    url = cfg["url"]
    body = ["User-agent: *", "Allow: /", ""]
    for b in AI_BOTS:
        body += [f"User-agent: {b}", "Allow: /", ""]
    body += [f"Sitemap: {url}sitemap.xml", f"# AI向けの案内: {url}llms.txt / 全文: {url}llms-full.txt"]
    out = ROOT / cfg["path"]
    (out / "robots.txt").write_text("\n".join(body) + "\n")
    (out / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)


def apply(cfg, posts, images, favicon=""):
    n = sum(1 for p in posts if patch_article(cfg, p, posts, images, favicon))
    pages = write_pages(cfg, favicon)
    write_llms(cfg, posts)
    write_robots(cfg)
    return n, pages
