"""ツールとアプリを目立つ場所に出す（全メディア共通）。build.py から毎回呼ばれ、冪等に次を適用する。
 - 記事: 冒頭の要約の直後（最初の h2 の前）に「この記事と一緒に使える」<!--toolbox-->…<!--/toolbox--> を差し込む。ツール1つ＋アプリ1つまで
 - トップ: ヒーロー直下の「使えるツールとアプリ」（top_html を build.py が埋め込む）
 - 一覧: /tools/（toolboxHub で変更可）に全件のハブページ。既に手書きのページがある場合は上書きせずリンクだけ張る
設定はメディア設定の "toolbox" 配列（並び順＝トップでの表示順）。apps 配列のアプリも自動で含める。
  {"name", "desc", "href"（ツールのURL。自サイトは /path/）, "appStoreId"（あればアプリ扱い）, "id"（アプリのアイコン名）,
   "slugs": [記事slug], "cats": [カテゴリ名], "all": true（どの記事にも出す既定）, "top": false（トップに出さない）}
"toolboxTop": false でトップの枠を出さない（トップに手書きのツール枠があるメディア）。
記事ごとの選び方: toollinks.json の指定 > slugs 一致 > cats 一致 > all。ツールとアプリそれぞれ最上位を1つずつ。JS 不使用。"""
import html, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICON_SRC = ROOT.parent / "SEADICE/p/icons/apps"  # 本体サイトのアプリアイコン(112px WebP)
E = html.escape
MARK = "<!--toolbox-hub-->"
TOOL_SVG = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h7v7H4zm9 0h7v7h-7zM4 13h7v7H4zm12 0h2v3h3v2h-3v3h-2v-3h-3v-2h3z"/></svg>')
CSS = (".tbx{margin:28px 0;background:var(--card);border:1.5px solid var(--accent);border-radius:16px;padding:16px}"
       ".tbx .tbh,.tbtop .tbh{font-size:13px;font-weight:800;letter-spacing:.08em;color:var(--accent);margin:0 0 10px}"
       ".tbi{display:flex;gap:12px;align-items:center;text-decoration:none;color:var(--text);padding:10px 0;border-top:1px solid var(--border)}"
       ".tbx .tbi:first-of-type{border-top:0}"
       ".tbic{flex:0 0 48px;width:48px;height:48px;border-radius:12px;overflow:hidden;display:flex;align-items:center;justify-content:center;"
       "background:color-mix(in srgb,var(--accent) 16%,var(--card))}.tbic img{width:48px;height:48px;display:block}.tbic svg{width:26px;height:26px;fill:var(--accent)}"
       ".tbt{flex:1;min-width:0}.tbt b{display:block;font-size:15px;line-height:1.45}.tbt small{display:block;font-size:13px;color:var(--muted);line-height:1.6;margin-top:2px}"
       ".tbt em{display:inline-block;font-style:normal;font-size:12px;color:var(--accent);margin-bottom:2px}"
       ".tbgo{flex:0 0 auto;font-size:13px;font-weight:700;color:var(--bg);background:var(--accent);border-radius:10px;padding:9px 12px;white-space:nowrap}"
       ".tball{display:inline-block;font-size:13px;font-weight:700;color:var(--link);padding:10px 0 0}"
       ".tbtop{margin:0 0 36px}.tbgrid{display:grid;gap:10px;grid-template-columns:1fr}@media(min-width:760px){.tbgrid{grid-template-columns:1fr 1fr}}"
       ".tbgrid .tbi{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:12px 14px}.tbgrid .tbi:hover{border-color:var(--accent)}"
       "@media(max-width:420px){.tbgo{display:none}}")


def hub_path(cfg):
    return cfg.get("toolboxHub", "/tools/")


def store_url(it, cfg):
    return f'https://apps.apple.com/app/id{it["appStoreId"]}?ct={cfg["slug"]}'


def items(cfg):
    """設定の toolbox と apps 配列を1つのリストにする（アプリは id で重複を除く）。"""
    out = [dict(x) for x in cfg.get("toolbox") or []]
    have = {x.get("id") for x in out}
    for a in cfg.get("apps") or []:
        if a["id"] in have or not a.get("appStoreId"):  # 未公開（App Store ID 未定）のアプリは出さない
            continue
        out.append({"id": a["id"], "name": a["name"], "desc": a["catch"], "appStoreId": a["appStoreId"],
                    "icon": a.get("icon"), "slugs": a.get("articles", [])})
    for x in out:
        x["app"] = bool(x.get("appStoreId"))
        if x["app"] and not x.get("icon"):
            x["icon"] = _icon(cfg, x.get("id"))
    return out


def _icon(cfg, app_id):
    """アプリのアイコンを本体サイトから自サイトの img/apps/ にコピーして、そのパスを返す（外部リクエストを増やさない）。"""
    if not app_id:
        return None
    dst = ROOT / cfg["path"] / "img/apps" / f"{app_id}.webp"
    src = ICON_SRC / f"{app_id}.webp"
    if not dst.exists() and src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    return f"/img/apps/{app_id}.webp" if dst.exists() else None


def _row(it, cfg):
    ic = f'<img src="{it["icon"]}" alt="" width="48" height="48" loading="lazy">' if it.get("icon") else TOOL_SVG
    if it["app"]:
        href, kind, go, ext = store_url(it, cfg), "iPhoneアプリ・無料・広告なし", "App Storeで見る", ' target="_blank" rel="noopener"'
    else:
        href, kind, go, ext = it["href"], "Webツール・登録不要・無料", "使ってみる", ""
    return (f'<a class="tbi" href="{E(href, quote=True)}"{ext}><span class="tbic">{ic}</span>'
            f'<span class="tbt"><em>{kind}</em><b>{E(it["name"])}</b><small>{E(it["desc"])}</small></span><span class="tbgo">{go}</span></a>')


def pick(cfg, p, its):
    def score(x):
        return 3 if p["slug"] in x.get("slugs", []) else 2 if p["category"] in x.get("cats", []) else 1 if x.get("all") else 0
    # 記事ごとに指定済みの「ツールで確かめる」(media/{slug}-toollinks.json) があれば、その先頭をツール枠に使う
    tl = (_toollinks(cfg).get(p["slug"]) or [None])[0]
    if tl:
        its = [{"name": tl[1], "desc": tl[2], "href": tl[0], "app": False, "slugs": [p["slug"]], "_tl": 4}] + its
        score0 = score
        score = lambda x: x.get("_tl") or score0(x)  # noqa: E731
    best = []
    for want_app in (False, True):
        cand = [x for x in its if x["app"] == want_app and score(x)]
        if cand:
            best.append(max(cand, key=score))  # 同点なら設定の並び順で先のもの
    return best


_TL = {}


def _toollinks(cfg):
    if cfg["slug"] not in _TL:
        import extras
        _TL[cfg["slug"]] = extras._load(cfg["slug"], "toollinks") or {}
    return _TL[cfg["slug"]]


def article_html(cfg, p, its):
    got = pick(cfg, p, its)
    if not got:
        return "<!--toolbox--><!--/toolbox-->"
    return ('<!--toolbox--><aside class="tbx" aria-label="この記事と一緒に使えるツールとアプリ"><p class="tbh">この記事と一緒に使える</p>'
            + "".join(_row(x, cfg) for x in got)
            + f'<a class="tball" href="{hub_path(cfg)}">{E(cfg["name"])}のツールとアプリをすべて見る</a></aside><!--/toolbox-->')


def top_html(cfg):
    if cfg.get("toolboxTop") is False:  # トップに専用のツール枠を手で作ってあるメディア（防犯・お金と心理）
        return ""
    its = [x for x in items(cfg) if x.get("top", True)]
    if not its:
        return ""
    its = [x for x in its if not x["app"]] + [x for x in its if x["app"]]
    shown = its[:6]
    return (f'<section class="tbtop" aria-label="使えるツールとアプリ"><p class="tbh">使えるツールとアプリ（無料・登録不要）</p>'
            f'<div class="tbgrid">{"".join(_row(x, cfg) for x in shown)}</div>'
            f'<a class="tball" href="{hub_path(cfg)}">ツールとアプリをすべて見る（{len(items(cfg))}件）</a></section>')


def patch(cfg, posts, its):
    n = 0
    for p in posts:
        f = ROOT / cfg["path"] / p["slug"] / "index.html"
        if not f.exists():
            continue
        s = f.read_text()
        blk = article_html(cfg, p, its)
        if "<!--toolbox-->" in s:
            s2 = re.sub(r"<!--toolbox-->.*?<!--/toolbox-->", lambda m: blk, s, flags=re.S)
        else:
            i = s.find('<div class="body"')
            j = s.find('<h2 class="sec"', i) if i >= 0 else -1
            if j < 0:
                continue
            s2 = s[:j] + blk + "\n" + s[j:]
        if ".tbx{" not in s2 and "footer{border-top" in s2:
            s2 = s2.replace("footer{border-top", CSS + "footer{border-top", 1)
        if s2 != s:
            f.write_text(s2)
        n += blk != "<!--toolbox--><!--/toolbox-->"
    return n


def hub(cfg, its, theme, favicon, css):
    import extras
    rel = hub_path(cfg).strip("/") + "/"
    f = ROOT / cfg["path"] / rel / "index.html"
    if f.exists() and MARK not in f.read_text():
        return None  # 手書きの一覧ページ（例: しぐさと本音の /tools/）は残す
    tools = [x for x in its if not x["app"]]
    apps = [x for x in its if x["app"]]
    sec = lambda h, xs: (f'<h2 class="sec" style="margin-top:28px">{h}</h2><div class="tbgrid">{"".join(_row(x, cfg) for x in xs)}</div>' if xs else "")
    name = cfg["name"]
    lead = (f'{name}の記事で紹介した研究や考え方を、その場で試せるWebツールとiPhoneアプリです。'
            '登録・ログインは不要で、すべて無料・広告なしで使えます。記録はお使いの端末の中だけに保存されます。')
    body = (f'  {MARK}<div class="hero"><h1>{E(name)}のツールとアプリ</h1><p class="lead">{E(lead)}</p></div>\n'
            + sec("Webツール（ブラウザですぐ使える）", tools) + sec("iPhoneアプリ", apps))
    desc = f'{name}の無料ツールとアプリ{len(its)}件。記事で紹介した研究をもとに、登録不要・広告なしでその場で試せます。'
    graph = [{"@type": "CollectionPage", "name": f"{name}のツールとアプリ", "url": cfg["url"] + rel, "description": desc,
              "mainEntity": {"@type": "ItemList", "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "name": x["name"],
                   "url": store_url(x, cfg).split("?")[0] if x["app"] else (cfg["url"].rstrip("/") + x["href"] if x["href"].startswith("/") else x["href"])}
                  for i, x in enumerate(tools + apps)]},
              "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}}]
    return extras._page(cfg, theme, favicon, css, rel, f"{name}のツールとアプリ（無料・登録不要）", desc, body, graph,
                        [("ツールとアプリ", cfg["url"] + rel)], CSS)


def llms_lines(cfg):
    """llms.txt に載せる「ツールとアプリ」の行（AI検索が道具を紹介できるように）。"""
    its = items(cfg)
    if not its:
        return []
    url = cfg["url"].rstrip("/")
    out = ["## ツールとアプリ（無料・登録不要）", "", f"- 一覧: {url}{hub_path(cfg)}"]
    for x in its:
        u = store_url(x, cfg).split("?")[0] if x["app"] else (url + x["href"] if x["href"].startswith("/") else x["href"])
        out.append(f"- [{x['name']}]({u}): {'iPhoneアプリ。' if x['app'] else 'Webツール。'}{x['desc']}")
    return out + [""]


def apply(cfg, posts, theme, favicon, css):
    its = items(cfg)
    if not its:
        return 0, []
    n = patch(cfg, posts, its)
    u = hub(cfg, its, theme, favicon, css)
    return n, [u] if u else []
