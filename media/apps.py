"""公開済みアプリとメディアの相互送客。build.py から毎回呼ばれ、冪等に次を適用する。
 - 記事末尾(関連記事の直前)にアプリカード <!--app-->…<!--/app--> を差し込む。1記事1アプリまで
 - アプリ用ページ /apps/{id}/ を生成する。アプリからはこのURLだけにリンクする(記事が増えると自動で育つ)
設定はメディア設定の "apps" 配列。どの記事に出すかは apps[].articles(slug の明示リスト)か、記事側の "app" フィールドで決める。
App Store リンクには ct={メディアslug} を付け、App Store Connect のアナリティクスで送客元を見られるようにする。JS 不使用。"""
import html, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
EMPTY = "<!--app--><!--/app-->"
CSS = (".appcard{display:flex;gap:14px;align-items:center;margin-top:40px;background:var(--card);border:1.5px solid var(--accent);border-radius:14px;padding:16px}"
       ".appcard img{flex:0 0 64px;width:64px;height:64px;border-radius:14px}.appcard .ab{min-width:0}"
       ".appcard small{display:block;font-size:12px;color:var(--accent);margin-bottom:2px}.appcard b{display:block;font-size:16px;line-height:1.4}"
       ".appcard p{font-size:14px;color:var(--muted);margin:4px 0 10px;line-height:1.6}"
       ".appcard a.ast{display:inline-block;background:var(--accent);color:var(--bg);font-weight:700;font-size:14px;text-decoration:none;padding:10px 18px;border-radius:10px}"
       ".omedia h3{font-size:16px;margin:24px 0 8px}.omedia h3 a{color:var(--accent)}.omedia ul{padding-left:1.2em;margin:0}"
       ".omedia li{margin:0;padding:6px 0;font-size:15px;line-height:1.6}.omedia li a{color:var(--text,inherit)}"
       ".appcard a.amore{display:inline-block;font-size:13px;color:var(--accent);margin-left:12px;padding:10px 0}")


def store_url(app, cfg):
    return f'https://apps.apple.com/app/id{app["appStoreId"]}?ct={cfg["slug"]}'


def app_for(cfg, p):
    apps = cfg.get("apps") or []
    if p.get("app"):
        return next((a for a in apps if a["id"] == p["app"]), None)
    return next((a for a in apps if p["slug"] in a.get("articles", [])), None)


def card_html(app, cfg):
    return (f'<!--app--><aside class="appcard" aria-label="関連アプリ"><img src="{app["icon"]}" alt="" width="64" height="64" loading="lazy">'
            f'<div class="ab"><small>この記事の内容を続けるなら</small><b>{E(app["name"])}</b><p>{E(app["catch"])}（無料・広告なし・iPhone）</p>'
            f'<a class="ast" href="{store_url(app, cfg)}" target="_blank" rel="noopener">App Storeで見る</a>'
            f'<a class="amore" href="/apps/{app["id"]}/">関連する記事</a></div></aside><!--/app-->')


def patch(cfg, posts):
    n = 0
    for p in posts:
        f = ROOT / cfg["path"] / p["slug"] / "index.html"
        if not f.exists():
            continue
        s = f.read_text()
        app = app_for(cfg, p)
        blk = card_html(app, cfg) if app else EMPTY
        if "<!--app-->" in s:
            s2 = re.sub(r"<!--app-->.*?<!--/app-->", lambda m: blk, s, flags=re.S)
        elif app and "<!--related-->" in s:
            s2 = s.replace("<!--related-->", blk + "\n    <!--related-->", 1)
        else:
            continue
        if app and ".appcard{" not in s2:
            s2 = s2.replace("footer{border-top", CSS + "footer{border-top", 1)
        if s2 != s:
            f.write_text(s2)
        n += bool(app)
    return n


def other_media(cfg, app_id):
    """同じアプリを apps[] に持つ、ほかのメディアの記事。アプリ用ページから他メディアへも送客する"""
    import json
    out = []
    for f in sorted((ROOT / "media").glob("*.json")):
        try:
            c = json.loads(f.read_text())
        except Exception:
            continue
        if not isinstance(c, dict) or c.get("slug") == cfg["slug"] or not c.get("url"):
            continue
        a = next((a for a in c.get("apps") or [] if a["id"] == app_id), None)
        pf = ROOT / f'media/{c.get("slug")}-posts.json'
        if not a or not pf.exists():
            continue
        posts = {p["slug"]: p for p in json.loads(pf.read_text())}
        items = [posts[s] for s in a.get("articles", []) if s in posts]
        items += [p for p in posts.values() if p.get("app") == app_id and p not in items]
        if items:
            out.append((c, items))
    return out


def others_html(cfg, app):
    blocks = []
    for c, items in other_media(cfg, app["id"]):
        lis = "".join(f'<li><a href="{c["url"]}{p["slug"]}/">{E(p["title"])}</a></li>' for p in items)
        blocks.append(f'<h3><a href="{c["url"]}apps/{app["id"]}/">{E(c["name"])}</a>（{len(items)}本）</h3><ul>{lis}</ul>')
    if not blocks:
        return ""
    return ('\n  <section class="omedia"><h2 class="sec">ほかのSEADICEメディアの記事</h2>'
            '<p class="lead">同じテーマを、別の切り口から扱った記事です。</p>' + "".join(blocks) + '</section>')


def hubs(cfg, posts, images, types, theme, favicon, css, cats, card):
    import extras
    urls = []
    for app in cfg.get("apps") or []:
        items = [p for p in posts if app_for(cfg, p) is app]
        rel = f'apps/{app["id"]}/'
        cards = "".join(card(p, cats, images, types) for p in items) or '<p class="empty">記事を準備中です。</p>'
        body = (f'  <div class="hero"><h1>{E(app["name"])}を使っている人へ</h1><p class="lead">{E(app["hubLead"])}</p></div>\n'
                f'  <aside class="appcard" style="margin-top:0"><img src="{app["icon"]}" alt="" width="64" height="64">'
                f'<div class="ab"><b>{E(app["name"])}</b><p>{E(app["catch"])}（無料・広告なし・iPhone）</p>'
                f'<a class="ast" href="{store_url(app, cfg)}" target="_blank" rel="noopener">App Storeで見る</a></div></aside>\n'
                f'  <h2 class="sec">関連する記事（{len(items)}本）</h2><div class="grid">{cards}</div>' + others_html(cfg, app))
        desc = f'{app["name"]}と一緒に読みたい、{cfg["name"]}の記事をまとめました。{app["hubLead"]}'
        graph = [{"@type": "CollectionPage", "name": f'{app["name"]}を使っている人へ', "url": cfg["url"] + rel, "description": desc,
                  "about": {"@type": "SoftwareApplication", "name": app["name"], "operatingSystem": "iOS", "applicationCategory": "HealthApplication",
                            "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}, "url": f'https://apps.apple.com/app/id{app["appStoreId"]}'},
                  "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}}]
        urls.append(extras._page(cfg, theme, favicon, css, rel, f'{app["name"]}を使っている人へ | {cfg["name"]}', desc, body, graph,
                                 [(f'{app["name"]}を使っている人へ', cfg["url"] + rel)], CSS))
    return urls


def apply(cfg, posts, cats, images, types, theme, favicon, css, card):
    if not cfg.get("apps"):
        return 0, []
    return patch(cfg, posts), hubs(cfg, posts, images, types, theme, favicon, css, cats, card)
