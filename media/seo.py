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
RELATED_CSS = ".related{margin-top:56px;padding-top:24px;border-top:1px solid var(--border)}.related h2{font-size:14px;margin:0 0 12px;color:var(--muted);letter-spacing:.1em}.related a{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 16px;margin:10px 0;text-decoration:none;color:var(--text);font-size:15px;font-weight:700;line-height:1.5}.related a:hover{border-color:var(--accent)}.related small{display:block;font-size:11px;color:var(--accent);font-weight:400;margin-bottom:2px}"


def article_style(cfg):
    t = (ROOT / cfg["template"]).read_text()
    return re.search(r"<style>.*?</style>", t, re.S).group(0)


def footer_html(cfg):
    n = E(cfg["name"])
    return (f'<footer><p><a href="/">{n}</a> &nbsp;|&nbsp; <a href="/about/">このメディアについて</a> &nbsp;|&nbsp; <a href="/sources/">出典と検証の方法</a> '
            f'&nbsp;|&nbsp; <a href="/disclaimer/">免責事項</a> &nbsp;|&nbsp; <a href="https://seadice.win/">SEADICE</a> &nbsp;|&nbsp; &copy; SEADICE</p></footer>')


def related_block(p, posts):
    others = [q for q in posts if q["slug"] != p["slug"]]
    others.sort(key=lambda q: (q["category"] != p["category"], q.get("type") != p.get("type"), q["date"]), reverse=False)
    same = [q for q in others if q["category"] == p["category"]]
    rest = [q for q in others if q["category"] != p["category"]]
    pick = (sorted(same, key=lambda q: q["date"], reverse=True) + sorted(rest, key=lambda q: q["date"], reverse=True))[:3]
    if not pick:
        return "<!--related--><!--/related-->"
    items = "".join(f'<a href="/{q["slug"]}/"><small>{E(q["category"])}</small>{E(q["title"])}</a>' for q in pick)
    return f'<!--related--><section class="related"><h2>関連記事</h2>{items}</section><!--/related-->'


def patch_article(cfg, p, posts, images):
    f = ROOT / cfg["path"] / p["slug"] / "index.html"
    if not f.exists():
        return False
    s = f.read_text()
    url = f'{cfg["url"]}{p["slug"]}/'
    img = images.get(p["slug"])
    src = img.get("src") if img else None
    # --- head: 重複を除いて入れ直す
    for pat in (r'<meta property="og:image"[^>]*>\n?', r'<meta name="twitter:image"[^>]*>\n?', r'<meta name="robots"[^>]*>\n?',
                r'<link rel="preconnect" href="https://upload\.wikimedia\.org"[^>]*>\n?', r'<meta property="og:image:alt"[^>]*>\n?'):
        s = re.sub(pat, "", s)
    add = '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">\n'
    if src:
        add += (f'<meta property="og:image" content="{src}">\n<meta property="og:image:alt" content="{E(img["alt"], quote=True)}">\n'
                f'<meta name="twitter:image" content="{src}">\n<link rel="preconnect" href="https://upload.wikimedia.org" crossorigin>\n')
        s = re.sub(r'<meta name="twitter:card" content="[^"]*">', '<meta name="twitter:card" content="summary_large_image">', s)
    else:
        s = re.sub(r'<meta name="twitter:card" content="[^"]*">', '<meta name="twitter:card" content="summary">', s)
    s = re.sub(r'(<meta name="twitter:card"[^>]*>\n)', lambda m: m.group(1) + add, s, count=1)
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
    if ".related{" not in s:
        s = s.replace("footer{border-top", RELATED_CSS + "footer{border-top", 1)
    blk = related_block(p, posts)
    if "<!--related-->" in s:
        s = re.sub(r"<!--related-->.*?<!--/related-->", lambda m: blk, s, flags=re.S)
    else:
        s = s.replace('<div class="sources">', blk + '\n    <div class="sources">', 1)
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


def write_pages(cfg):
    st = article_style(cfg)
    concept = cfg.get("concept", "")
    concept_short = cfg.get("tagline", "")
    urls = []
    for slug, (title, desc, builder) in PAGES.items():
        ctx = {"name": cfg["name"], "concept_short": concept_short}
        secs = builder(cfg)
        body = "".join(
            f'<h2 class="sec"><span class="n">{i+1:02d}</span>{E(h)}</h2>' + "".join(f'<p class="t">{(x.format(**ctx) if "{" in x else x)}</p>' for x in ps)
            for i, (h, ps) in enumerate(secs))
        ttl = f'{title} | {cfg["name"]}'
        url = f'{cfg["url"]}{slug}/'
        ld = json.dumps({"@context": "https://schema.org", "@graph": [
            {"@type": "AboutPage" if slug == "about" else "WebPage", "name": ttl, "url": url, "inLanguage": "ja",
             "isPartOf": {"@type": "WebSite", "name": cfg["name"], "url": cfg["url"]},
             "publisher": {"@type": "Organization", "name": "SEADICE", "url": "https://seadice.win"}},
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


def apply(cfg, posts, images):
    n = sum(1 for p in posts if patch_article(cfg, p, posts, images))
    pages = write_pages(cfg)
    return n, pages
