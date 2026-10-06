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
                f'  <h2 class="sec">関連する記事（{len(items)}本）</h2><div class="grid">{cards}</div>')
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
