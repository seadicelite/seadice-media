"""build.py の最後に呼ばれる追加ページ生成。設定ファイルがあるメディアだけ処理する(無ければ何もしない)。

- media/{slug}-guides.json   : 悩み別・年齢別のまとめページ → /guide/ と /guide/{id}/
- media/{slug}-glossary.json : 用語集 → /glossary/
- media/{slug}-pages.json    : 手書き本文の固定ページ(例: 印刷用ルール表) → /{path}/
- media/{slug}-audited.json  : 点検済み記事 → 記事の「わかっている度」の横に「出典照合済み」を表示
                               要素は "slug" または {"slug": ..., "date": "YYYY-MM-DD"}
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape


def _load(slug, name):
    f = ROOT / f"media/{slug}-{name}.json"
    return json.loads(f.read_text()) if f.exists() else None


def _page(cfg, theme, favicon, css, rel, title, desc, body, graph, trail, extra_css=""):
    url = cfg["url"]
    purl = url + rel
    crumbs = [("HOME", "https://seadice.win/"), (cfg["name"], url)] + trail
    ld = {"@context": "https://schema.org", "@graph": graph + [{"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}]}
    bc = " / ".join(f'<a href="{u}" style="color:var(--muted)">{E(n)}</a>' for n, u in crumbs[:-1]) + " / " + E(crumbs[-1][0])
    out = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc, quote=True)}">
<link rel="canonical" href="{purl}">
<meta property="og:title" content="{E(title, quote=True)}">
<meta property="og:description" content="{E(desc, quote=True)}">
<meta property="og:url" content="{purl}">
<meta property="og:type" content="website">
<meta name="robots" content="index,follow">
{favicon}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{css}{EXTRA_CSS}{extra_css}{cfg.get("extraCss", "")}</style>
</head>
<body>
<nav class="top">
  <a href="https://seadice.win/" class="nav-logo">SEADICE</a>
  <a href="/" class="r">{E(cfg["name"])}</a>
</nav>
<main>
  <p style="font-size:12px;color:var(--muted);margin:0 0 16px">{bc}</p>
{body}
</main>
<footer><p><a href="/about/">このメディアについて</a> | <a href="/sources/">出典と検証の方法</a> | <a href="/disclaimer/">免責事項</a>{"".join(f' | <a href="{n["path"]}">{E(n["label"])}</a>' for n in cfg.get("extraNav", []))} | <a href="https://seadice.win/">SEADICE</a> | &copy; SEADICE</p></footer>
</body>
</html>
'''
    d = ROOT / cfg["path"] / rel
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(out)
    return purl


EXTRA_CSS = (".xlead{font-size:15px;line-height:1.85;max-width:680px;margin:0 0 20px}"
             ".points{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:20px 22px;margin:0 0 32px}"
             ".points h2{font-size:13px;letter-spacing:.12em;color:var(--accent);margin:0 0 8px}"
             ".points li{margin:8px 0 8px 20px;font-size:15px;line-height:1.75}"
             ".gnav{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 28px}"
             ".gnav a{display:inline-block;font-size:13px;color:var(--text);text-decoration:none;background:var(--card);border:1px solid var(--border);border-radius:999px;padding:8px 14px}"
             ".gnav a:hover,.gnav a[aria-current]{border-color:var(--accent);color:var(--accent)}"
             ".terms dt{font-size:17px;font-weight:700;margin:28px 0 6px;scroll-margin-top:72px}"
             ".terms dt small{font-size:12px;font-weight:400;color:var(--muted);margin-left:8px}"
             ".terms dd{font-size:15px;line-height:1.85;margin:0}"
             ".terms dd .rel{display:block;font-size:13px;margin-top:6px;color:var(--muted)}"
             ".terms a,.xbody a{color:var(--link)}"
             ".xbody{max-width:720px}.xbody h2{font-size:19px;margin:36px 0 10px}.xbody p{font-size:15px;line-height:1.85;margin:10px 0}"
             ".xbody table{width:100%;border-collapse:collapse;font-size:14px;margin:12px 0}"
             ".xbody th,.xbody td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top;line-height:1.7}"
             ".xbody th{background:var(--card)}.xbody .fill{display:block;border-bottom:1px solid var(--muted);min-height:28px;margin-top:6px}"
             ".xbody ul{margin:8px 0 8px 22px}.xbody li{margin:6px 0;font-size:15px;line-height:1.75}"
             ".xbody .note{font-size:13px;color:var(--muted)}")


def _cards(slugs, posts, cats, images, types, card):
    by = {p["slug"]: p for p in posts}
    return "".join(card(by[s], cats, images, types) for s in slugs if s in by)


def guides(cfg, posts, cats, images, types, theme, favicon, css, card):
    g = _load(cfg["slug"], "guides")
    if not g:
        return []
    urls = []
    nav = "".join(f'<a href="/guide/{x["id"]}/">{E(x["label"])}</a>' for x in g["items"])
    for x in g["items"]:
        rel = f'guide/{x["id"]}/'
        pts = "".join(f"<li>{E(p)}</li>" for p in x.get("points", []))
        here = 'href="/guide/' + x["id"] + '/"'
        cur_nav = nav.replace(here, here + ' aria-current="page"')
        body = (f'  <div class="hero"><h1>{E(x["title"])}</h1></div>\n  <p class="xlead">{E(x["lead"])}</p>\n'
                f'  <nav class="gnav" aria-label="{E(g["title"])}">{cur_nav}</nav>\n'
                + (f'  <div class="points"><h2>まず知っておきたいこと</h2><ul>{pts}</ul></div>\n' if pts else "")
                + f'  <div class="grid">{_cards(x["slugs"], posts, cats, images, types, card)}</div>'
                + (f'\n  <p class="xlead" style="margin-top:28px"><a href="{g["cta"]["href"]}" style="color:var(--link);font-weight:700">{E(g["cta"]["label"])}</a></p>' if g.get("cta") else ""))
        by = {p["slug"]: p for p in posts}
        graph = [{"@type": "CollectionPage", "name": x["title"], "url": cfg["url"] + rel, "description": x["lead"],
                  "mainEntity": {"@type": "ItemList", "itemListElement": [
                      {"@type": "ListItem", "position": i + 1, "url": f'{cfg["url"]}{s}/', "name": by[s]["title"]}
                      for i, s in enumerate([s for s in x["slugs"] if s in by])]}}]
        urls.append(_page(cfg, theme, favicon, css, rel, f'{x["title"]} | {cfg["name"]}', x["lead"][:120], body, graph,
                          [(g["title"], cfg["url"] + "guide/"), (x["label"], cfg["url"] + rel)]))
    items = "".join(f'<a class="card" href="/guide/{x["id"]}/"><div class="cb"><p class="t">{E(x["title"])}</p><p class="d">{E(x["lead"][:80])}…</p></div></a>' for x in g["items"])
    body = f'  <div class="hero"><h1>{E(g["title"])}</h1></div>\n  <p class="xlead">{E(g["lead"])}</p>\n  <div class="grid">{items}</div>'
    if g.get("cta"):
        body += f'\n  <p class="xlead" style="margin-top:28px"><a href="{g["cta"]["href"]}" style="color:var(--link);font-weight:700">{E(g["cta"]["label"])}</a></p>'
    urls.append(_page(cfg, theme, favicon, css, "guide/", f'{g["title"]} | {cfg["name"]}', g["lead"][:120], body,
                      [{"@type": "CollectionPage", "name": g["title"], "url": cfg["url"] + "guide/", "description": g["lead"]}],
                      [(g["title"], cfg["url"] + "guide/")]))
    return urls


def glossary(cfg, posts, theme, favicon, css):
    terms = _load(cfg["slug"], "glossary")
    if not terms:
        return []
    by = {p["slug"]: p for p in posts}
    rows = ""
    for t in terms:
        rel = "、".join(f'<a href="/{s}/">{E(by[s]["title"])}</a>' for s in t.get("slugs", []) if s in by)
        rows += (f'<dt id="{t["id"]}">{E(t["term"])}' + (f'<small>{E(t["en"])}</small>' if t.get("en") else "") + "</dt>"
                 f'<dd>{E(t["def"])}' + (f'<span class="rel">関連記事: {rel}</span>' if rel else "") + "</dd>")
    url = cfg["url"] + "glossary/"
    lead = f'{cfg["name"]}の記事に出てくる言葉を、専門用語を使わずに説明します（{len(terms)}語）。'
    body = f'  <div class="hero"><h1>用語集</h1></div>\n  <p class="xlead">{E(lead)}</p>\n  <dl class="terms">{rows}</dl>'
    graph = [{"@type": "DefinedTermSet", "name": f'{cfg["name"]} 用語集', "url": url, "hasDefinedTerm": [
        {"@type": "DefinedTerm", "name": t["term"], "description": t["def"], "url": f'{url}#{t["id"]}'} for t in terms]}]
    return [_page(cfg, theme, favicon, css, "glossary/", f'用語集（{len(terms)}語をやさしく解説）| {cfg["name"]}', lead, body, graph,
                  [("用語集", url)])]


def pages(cfg, theme, favicon, css):
    ps = _load(cfg["slug"], "pages")
    if not ps:
        return []
    urls = []
    for p in ps:
        rel = p["path"].strip("/") + "/"
        body = f'  <div class="hero"><h1>{E(p["title"])}</h1></div>\n  <div class="xbody">{p["body"]}</div>'
        graph = [{"@type": "WebPage", "name": p["title"], "url": cfg["url"] + rel, "description": p["desc"],
                  "dateModified": p.get("date"), "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}}]
        trail = ([(p["parent"]["label"], cfg["url"] + p["parent"]["path"].strip("/") + "/")] if p.get("parent") else []) + [(p["title"], cfg["url"] + rel)]
        urls.append(_page(cfg, theme, favicon, css, rel, f'{p.get("seo_title") or p["title"]} | {cfg["name"]}', p["desc"], body, graph,
                          trail, p.get("css", "")))
    return urls


def badges(cfg):
    a = _load(cfg["slug"], "audited")
    if a is None:
        return 0
    n = 0
    for e in a:
        slug, date = (e, "") if isinstance(e, str) else (e["slug"], e.get("date", ""))
        f = ROOT / cfg["path"] / slug / "index.html"
        if not f.exists():
            continue
        t = f.read_text()
        import re
        t = re.sub(r'<span class="checked"[^>]*>.*?</span>', "", t)
        tag = (f'<span class="checked" style="font-size:12px;color:var(--accent);border:1px solid var(--accent);border-radius:999px;padding:3px 10px">'
               f'出典照合済み{"（" + date + "）" if date else ""}</span>')
        i = t.find('<div class="evidence">')
        if i >= 0:
            j = t.find("</div>", i)
            t = t[:j] + tag + t[j:]
        else:  # 「わかっている度」が無いメディアは、読了時間の行に並べる
            i = t.find('<p class="meta">')
            if i < 0:
                continue
            j = t.find("</p>", i)
            t = t[:j] + " " + tag + t[j:]
        f.write_text(t)
        n += 1
    return n


def top_links(cfg):
    """トップページの見出し直下に、まとめページ・用語集などへの入口を置く。"""
    links = [(n["label"], n["path"]) for n in cfg.get("extraNav", [])]
    if not links or cfg.get("layout") == "hub":  # hub はトップ本文に同じ入口を持つ
        return
    f = ROOT / cfg["path"] / "index.html"
    t = f.read_text()
    nav = '<nav class="gnav" aria-label="ガイド" style="margin:4px 0 24px">' + "".join(f'<a href="{p}">{E(l)}</a>' for l, p in links) + "</nav>"
    k = "</div>"
    m = t.find("<!--mastend-->")  # mastheadHtml を使うメディアは、このマーカーの直後に置く
    if m >= 0:
        t = t[:m] + nav + t[m:]
        if ".gnav{" not in t:
            t = t.replace("</style>", EXTRA_CSS + "</style>", 1)
        f.write_text(t)
        return
    i = t.find('<div class="maghead">')
    if i < 0:
        i = t.find('<div class="hero">')
    if i < 0:
        return
    j = t.find(k, i) + len(k)
    t = t[:j] + nav + t[j:]
    if ".gnav{" not in t:
        t = t.replace("</style>", EXTRA_CSS + "</style>", 1)
    f.write_text(t)


def crosslinks(cfg):
    """media/{slug}-crosslinks.json: {記事slug: [[他メディアslug, 記事slug], ...]} を記事末の「ほかのメディアの関連記事」に出す。"""
    m = _load(cfg["slug"], "crosslinks")
    if not m:
        return 0
    import re
    n = 0
    for slug, refs in m.items():
        f = ROOT / cfg["path"] / slug / "index.html"
        if not f.exists():
            continue
        items = ""
        for ms, s in refs:
            oc = json.loads((ROOT / f"media/{ms}.json").read_text())
            op = {p["slug"]: p for p in json.loads((ROOT / f"media/{ms}-posts.json").read_text())}
            if s not in op:
                continue
            items += f'<a href="{oc["url"]}{s}/" target="_blank" rel="noopener"><span class="rb"><small>{E(oc["name"])}</small><p>{E(op[s]["title"])}</p></span></a>'
        t = re.sub(r"<!--xlinks-->.*?<!--/xlinks-->", "", f.read_text(), flags=re.S)
        if items:
            block = f'<!--xlinks--><section class="related"><h2>ほかのメディアの関連記事</h2>{items}</section><!--/xlinks-->'
            k = "<!--/related-->"
            t = t.replace(k, k + block, 1) if k in t else t.replace("</article>", block + "</article>", 1)
            n += 1
        f.write_text(t)
    return n


def term_links(cfg, posts, limit=4, write=True):
    """記事本文で用語集の言葉が最初に出てきた1か所を /glossary/#id へのリンクにする（1記事 limit 個まで）。
    対象は本文の <p>・<li>（パンくず・読了時間・研究カードの出典名・出典欄は除く）。見出し・既存リンク・JSON-LD・FAQの質問には付けない。
    表記は用語の括弧の前（「エポケー（判断停止）」→「エポケー」）。1文字の語は誤爆するので、用語に "match" で表記を指定したときだけ使う。
    その用語の主記事（slugs の先頭）では、記事自体が説明しているのでリンクしない。何度ビルドしても同じ結果になる。"""
    import re
    terms = _load(cfg["slug"], "glossary")
    if not terms:
        return 0
    forms = []
    for x in terms:
        ms = x.get("match") or [re.split(r"[（(]", x["term"])[0].strip()]
        for m in ms:
            if len(m) >= 2:
                forms.append((m, x["id"], (x.get("slugs") or [None])[0]))
    forms.sort(key=lambda f: -len(f[0]))  # 長い表記を優先（「無知のヴェール」を「無知」より先に）
    old = re.compile(r'<a class="gl" href="/glossary/#[^"]*">(.*?)</a>')
    # 本文の段落と箇条書きだけ。研究カードの出典名・条件欄（who/cond）や見出し的な行（ttl）には付けない
    para = re.compile(r'(?s)<(p|li)(?![^>]*class="(?:breadcrumb|meta|who|cond|ttl)")(\s[^>]*)?>.*?</\1>')
    n = 0
    for post in posts:
        f = ROOT / cfg["path"] / post["slug"] / "index.html"
        if not f.exists():
            continue
        src = f.read_text()
        t = old.sub(r"\1", src)
        a, b = t.find("<article"), t.find("</article>")
        stop = [i for i in (t.find("<h2>出典", a), t.find("<!--related-->", a), t.find('class="related"', a)) if a < i < b]
        b = min(stop) if stop else b
        if a < 0 or b < 0:
            continue
        body, used, count = t[a:b], set(), 0

        def link_p(m):
            nonlocal count
            s = m.group(0)
            for form, tid, main in forms:
                if count >= limit:
                    break
                if tid in used or main == post["slug"]:
                    continue
                parts, depth = re.split(r"(<[^>]+>)", s), 0
                for k, seg in enumerate(parts):
                    if seg.startswith("<"):
                        depth += 1 if re.match(r"<a\b", seg) else -1 if seg.startswith("</a") else 0
                        continue
                    i = seg.find(form) if depth == 0 else -1
                    if i >= 0:
                        parts[k] = seg[:i] + f'<a class="gl" href="/glossary/#{tid}">{form}</a>' + seg[i + len(form):]
                        s = "".join(parts)
                        used.add(tid)
                        count += 1
                        break
            return s
        body = para.sub(link_p, body)
        t = t[:a] + body + t[b:]
        if 'class="gl"' in t and ".gl{" not in t:
            t = t.replace("</style>", "a.gl{color:inherit;text-decoration:underline dotted;text-underline-offset:3px}</style>", 1)
        if t != src:
            n += 1
            if write:
                f.write_text(t)
    return n


def apply(cfg, posts, cats, images, types, theme, favicon, css, card):
    urls = guides(cfg, posts, cats, images, types, theme, favicon, css, card)
    urls += glossary(cfg, posts, theme, favicon, css)
    urls += pages(cfg, theme, favicon, css)
    n = badges(cfg)
    term_links(cfg, posts)
    crosslinks(cfg)
    top_links(cfg)
    if urls:
        sm = ROOT / cfg["path"] / "sitemap.xml"
        s = sm.read_text()
        latest = max((p["date"] for p in posts), default="")
        add = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{latest}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>\n"
                      for u in urls if f"<loc>{u}</loc>" not in s)
        if add:
            sm.write_text(s.replace("</urlset>", add + "</urlset>"))
    return len(urls), n
