"""build.py の最後に呼ばれる追加ページ生成。設定ファイルがあるメディアだけ処理する(無ければ何もしない)。

- media/{slug}-guides.json   : 悩み別・年齢別のまとめページ → /guide/ と /guide/{id}/
- media/{slug}-glossary.json : 用語集 → /glossary/
- media/{slug}-pages.json    : 手書き本文の固定ページ(例: 印刷用ルール表) → /{path}/
- media/{slug}-map.json      : 記事マップ(マインドマップ) → /map/ (media/mindmap.py)
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


def _page(cfg, theme, favicon, css, rel, title, desc, body, graph, trail, extra_css="", head=""):
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
{favicon}{head}
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
<footer><p><a href="/about/">このメディアについて</a> | <a href="/sources/">出典と検証の方法</a> | <a href="/disclaimer/">免責事項</a>{"".join(f' | <a href="{n["path"]}">{E(n["label"])}</a>' for n in cfg.get("footerNav", cfg.get("extraNav", [])))} | <a href="https://seadice.win/">SEADICE</a> | &copy; SEADICE</p></footer>
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
        # ガイドの "app"（設定の apps[].id）があれば、記事末尾と同じアプリカードを最後に置く。"appLabel" で見出しの一言を変えられる
        app = next((a for a in cfg.get("apps") or [] if a["id"] == x.get("app")), None)
        app_css = ""
        if app:
            import apps
            c = apps.card_html(app, cfg)
            if x.get("appLabel"):
                c = c.replace("この記事の内容を続けるなら", E(x["appLabel"]), 1)
            body += "\n  " + c
            app_css = apps.CSS
        by = {p["slug"]: p for p in posts}
        graph = [{"@type": "CollectionPage", "name": x["title"], "url": cfg["url"] + rel, "description": x["lead"],
                  "mainEntity": {"@type": "ItemList", "itemListElement": [
                      {"@type": "ListItem", "position": i + 1, "url": f'{cfg["url"]}{s}/', "name": by[s]["title"]}
                      for i, s in enumerate([s for s in x["slugs"] if s in by])]}}]
        urls.append(_page(cfg, theme, favicon, css, rel, f'{x["title"]} | {cfg["name"]}', x["lead"][:120], body, graph,
                          [(g["title"], cfg["url"] + "guide/"), (x["label"], cfg["url"] + rel)], app_css))
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
                          trail, p.get("css", ""), p.get("head", "")))
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
        # 直前の半角スペースも一緒に消す(残すとビルドのたびにスペースが1つずつ増える)
        t = re.sub(r' *<span class="checked"[^>]*>.*?</span>', "", t)
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
    """media/{slug}-crosslinks.json: {記事slug: [[他メディアslug, 記事slug], ...]} を記事末の「ほかのメディアの関連記事」に出す。
    行き先が STUDY（siteType: course）なら記事slugの代わりにレッスンidを書き、「無料講座で体系的に学ぶ」に出す。
    STUDY の看板ツールの path（例 bouhan-check/）を書くと、記事末の先頭「読んだあとに使う」に出す（base.md「読んだあとの一歩」）。"""
    m = _load(cfg["slug"], "crosslinks")
    if not m:
        return 0
    import re
    n = 0
    for slug, refs in m.items():
        f = ROOT / cfg["path"] / slug / "index.html"
        if not f.exists():
            continue
        items = study = tool = ""
        for ms, s in refs:
            oc = json.loads((ROOT / f"media/{ms}.json").read_text())
            if oc.get("siteType") == "course" and oc.get("tool") and s == oc["tool"]["path"]:
                x = oc["tool"]
                tool += (f'<a href="{oc["url"]}{s}" target="_blank" rel="noopener"><span class="rb"><small>{E(oc["name"])}（無料ツール・登録不要）</small>'
                         f'<p>{E(x["title"])}</p><small>{E(x["desc"])}</small></span></a>')
                continue
            if oc.get("siteType") == "course":
                # STUDY（無料講座）のレッスンへのリンク。s はレッスンid
                ls = {l["id"]: l for c in json.loads((ROOT / f"media/{ms}-course.json").read_text())["chapters"] for l in c["lessons"]}
                if s in ls:
                    study += f'<a href="{oc["url"]}course/{s}/" target="_blank" rel="noopener"><span class="rb"><small>{E(oc["name"])}（無料講座）</small><p>{E(ls[s]["title"])}</p></span></a>'
                continue
            op = {p["slug"]: p for p in json.loads((ROOT / f"media/{ms}-posts.json").read_text())}
            if s not in op:
                continue
            items += f'<a href="{oc["url"]}{s}/" target="_blank" rel="noopener"><span class="rb"><small>{E(oc["name"])}</small><p>{E(op[s]["title"])}</p></span></a>'
        t = re.sub(r"<!--xlinks-->.*?<!--/xlinks-->", "", f.read_text(), flags=re.S)
        if items or study or tool:
            block = ('<!--xlinks-->' + (f'<section class="related"><h2>読んだあとに使う</h2>{tool}</section>' if tool else '') + (f'<section class="related"><h2>ほかのメディアの関連記事</h2>{items}</section>' if items else '')
                     + (f'<section class="related"><h2>無料講座で体系的に学ぶ</h2>{study}</section>' if study else '') + '<!--/xlinks-->')
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


MATRIX_CSS = (".mrow{display:grid;gap:12px;grid-template-columns:1fr}@media(min-width:760px){.mrow{grid-template-columns:1fr 1fr}}"
              ".mrow a{display:block;background:var(--card);border:1px solid var(--border);border-radius:16px;padding:16px 18px;text-decoration:none;color:var(--text)}"
              ".mrow a:hover,.mrow a:focus-visible{border-color:var(--accent)}"
              ".mrow b{display:block;font-size:17px;line-height:1.5}.mrow span{display:block;font-size:13px;color:var(--muted);line-height:1.7;margin-top:6px}"
              ".mstage{margin:0 0 40px;scroll-margin-top:72px}.mstage>h2{font-size:19px;line-height:1.5;margin:0 0 14px}"
              ".mstage>h2 small{display:block;font-size:12px;letter-spacing:.08em;color:var(--accent);margin-bottom:2px}")


def matrix_guides(cfg, posts, cats, images, types, theme, favicon, css, card):
    """media/{slug}-matrix.json に "guide" があれば、表の行ごとのガイド /guide/{行id}/ と一覧 /guide/ を作る。
    行のページは列（段階）の順に記事を並べ、記事が無い段階は出さない。記事側には関連記事の直前に「この悩みを順に読む」を入れる。
    -guides.json（手書きのガイド）があるメディアでは使わない（/guide/ が衝突するため）。
    表ファイルが無く、記事の "stage" でマスを数えるメディア（ai など）は、設定の "gridGuide"
    （guide の中身＋ stages: [{id, stage, label, q}]）から、行＝カテゴリ・列＝段階の表をその場で組み立てる。"""
    m = _load(cfg["slug"], "matrix")
    if not m and cfg.get("gridGuide"):
        gg = cfg["gridGuide"]
        m = {"guide": gg, "cols": gg["stages"], "rows": [
            {"id": c["id"], "label": c["name"], "lead": c.get("guideLead", ""), "cells": {
                s["id"]: [p["slug"] for p in posts if p.get("category") == c["name"] and p.get("stage") == s["stage"]] for s in gg["stages"]}}
            for c in cfg["categories"] if isinstance(c, dict)]}
    if not m or not m.get("guide") or _load(cfg["slug"], "guides"):
        return []
    import re
    g, cols, by = m["guide"], m["cols"], {p["slug"]: p for p in posts}
    have_of = {r["id"]: [c for c in cols if any(s in by or s.startswith("https://") for s in r["cells"].get(c["id"], []))] for r in m["rows"]}
    rows = [r for r in m["rows"] if have_of[r["id"]]]
    urls = []
    nav = "".join(f'<a href="/guide/{r["id"]}/">{E(r["label"])}</a>' for r in rows)
    for r in rows:
        rel, have = f'guide/{r["id"]}/', have_of[r["id"]]
        here = f'href="/guide/{r["id"]}/"'
        secs, items = "", []
        for c in have:
            ss = r["cells"].get(c["id"], [])
            arts = [s for s in ss if s in by]
            items += arts
            ext = "".join(f'<p class="xlead"><a href="{E(u)}" style="color:var(--link);font-weight:700">{E(g.get("toolLabel", "チェック表・ツールを使う"))}</a></p>' for u in ss if u.startswith("https://"))
            secs += (f'  <section class="mstage" id="{c["id"]}"><h2><small>{cols.index(c) + 1:02d} {E(c["label"])}</small>{E(c["q"].split("（")[0])}</h2>'
                     f'<div class="grid">{_cards(arts, posts, cats, images, types, card)}</div>{ext}</section>\n')
        title = g["rowTitle"].replace("{label}", r["label"])
        lead = r.get("lead") or g["rowLead"].replace("{label}", r["label"])
        steps = " → ".join(f'<a href="#{c["id"]}" style="color:var(--link)">{E(c["label"])}</a>' for c in have)
        cur = here + ' aria-current="page"'
        body = (f'  <div class="hero"><h1>{E(title)}</h1></div>\n  <p class="xlead">{E(lead)}</p>\n'
                f'  <p class="xlead" style="font-size:14px">この順に読めます: {steps}</p>\n'
                f'{secs}  <h2 style="font-size:17px;margin:8px 0 12px">ほかのお悩み</h2>\n  <nav class="gnav" aria-label="{E(g["title"])}">{nav.replace(here, cur)}</nav>\n')
        graph = [{"@type": "CollectionPage", "name": title, "url": cfg["url"] + rel, "description": lead,
                  "mainEntity": {"@type": "ItemList", "itemListElement": [
                      {"@type": "ListItem", "position": i + 1, "url": f'{cfg["url"]}{s}/', "name": by[s]["title"]} for i, s in enumerate(items)]}}]
        urls.append(_page(cfg, theme, favicon, css, rel, f'{title} | {cfg["name"]}', lead[:120], body, graph,
                          [(g["title"], cfg["url"] + "guide/"), (r["label"], cfg["url"] + rel)], MATRIX_CSS))
        for c in have:
            for s in r["cells"].get(c["id"], []):
                f = ROOT / cfg["path"] / s / "index.html"
                if s not in by or not f.exists():
                    continue
                t = re.sub(r"<!--gstep-->.*?<!--/gstep-->", "", f.read_text(), flags=re.S)
                block = ('<!--gstep--><div role="navigation" aria-label="この悩みを順に読む" style="background:var(--card);border:1px solid var(--border);border-radius:14px;padding:14px 18px;margin:32px 0;font-size:14px;line-height:1.9">'
                         f'<b>「{E(r["label"])}」を順に読む</b><br>'
                         + " → ".join(f'<b>{E(x["label"])}（この記事）</b>' if x is c else f'<a href="/guide/{r["id"]}/#{x["id"]}" style="color:var(--link)">{E(x["label"])}</a>' for x in have)
                         + f'<br><a href="/guide/{r["id"]}/" style="color:var(--link);font-weight:700">この悩みのガイドを見る</a></div><!--/gstep-->')
                if "<!--related-->" in t:
                    t = t.replace("<!--related-->", block + "<!--related-->", 1)
                f.write_text(t)
    cards = "".join(f'<a href="/guide/{r["id"]}/"><b>{E(r["label"])}</b><span>{E("・".join(c["label"] for c in have_of[r["id"]]))}</span></a>' for r in rows)
    body = f'  <div class="hero"><h1>{E(g["title"])}</h1></div>\n  <p class="xlead">{E(g["lead"])}</p>\n  <div class="mrow">{cards}</div>'
    urls.append(_page(cfg, theme, favicon, css, "guide/", f'{g["title"]} | {cfg["name"]}', g["lead"][:120], body,
                      [{"@type": "CollectionPage", "name": g["title"], "url": cfg["url"] + "guide/", "description": g["lead"],
                        "hasPart": [{"@type": "CollectionPage", "name": r["label"], "url": f'{cfg["url"]}guide/{r["id"]}/'} for r in rows]}],
                      [(g["title"], cfg["url"] + "guide/")], MATRIX_CSS))
    return urls


def apply(cfg, posts, cats, images, types, theme, favicon, css, card):
    urls = guides(cfg, posts, cats, images, types, theme, favicon, css, card)
    urls += matrix_guides(cfg, posts, cats, images, types, theme, favicon, css, card)
    urls += glossary(cfg, posts, theme, favicon, css)
    urls += pages(cfg, theme, favicon, css)
    import mindmap  # 記事マップ /map/ (media/{slug}-map.json があるメディアだけ)
    urls += mindmap.build(cfg, posts, cats, lambda rel, title, desc, body, graph, trail, extra_css="":
                          _page(cfg, theme, favicon, css, rel, title, desc, body, graph, trail, extra_css))
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
