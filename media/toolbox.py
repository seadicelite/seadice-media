"""ツールとアプリを目立つ場所に出す（全メディア共通）。build.py から毎回呼ばれ、冪等に次を適用する。
 - 記事: 冒頭の要約の直後（最初の h2 の前）に「この記事と一緒に使える」<!--toolbox-->…<!--/toolbox--> を差し込む。ツール1つ＋アプリ1つまで
 - トップ: ヒーロー直下の「使えるツールとアプリ」（top_html を build.py が埋め込む）
 - 一覧: /tools/（toolboxHub で変更可）に全件のハブページ。既に手書きのページがある場合は上書きせずリンクだけ張る
設定はメディア設定の "toolbox" 配列（並び順＝トップでの表示順）。apps 配列のアプリも自動で含める。
  {"name", "desc", "href"（ツールのURL。自サイトは /path/）, "appStoreId"（あればアプリ扱い）, "id"（アプリのアイコン名）,
   "slugs": [記事slug], "cats": [カテゴリ名], "all": true（どの記事にも出す既定）, "top": false（トップに出さない）,
   "glyph"（Webツールのアイコンの種類。省略時は名前から決める。GLYPHS のキー）}
"toolboxTop": false でトップの枠を出さない（トップに手書きのツール枠があるメディア）。
記事ごとの選び方: toollinks.json の指定 > slugs 一致 > cats 一致 > all。ツールとアプリそれぞれ最上位を1つずつ。JS 不使用。"""
import html, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ICON_SRC = ROOT.parent / "SEADICE/p/icons/apps"  # 本体サイトのアプリアイコン(112px WebP)
E = html.escape
MARK = "<!--toolbox-hub-->"
# Webツールのアイコン: 名前から種類を見分けて、種類ごとの1色の線画にする（全部同じ記号だとアプリの画像だけが目立つため）。
# 設定の "glyph" で種類を直接指定できる。上から順に最初に当たった種類を使う
GLYPHS = {
    "play": '<circle cx="12" cy="12" r="8.5"/><path d="M10 8.5l5 3.5-5 3.5z"/>',
    "timer": '<circle cx="12" cy="13" r="7.5"/><path d="M12 13V9M10 2.5h4M12 2.5v3"/>',
    "clock": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.5 2"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4M8 14h3M8 17h6"/>',
    "shield": '<path d="M12 3l7.5 3v5.5c0 4.5-3.2 8-7.5 9.5-4.3-1.5-7.5-5-7.5-9.5V6z"/><path d="M9 12l2 2 4-4"/>',
    "heart": '<path d="M12 19.5s-7.5-4.5-7.5-10A4 4 0 0112 7.5a4 4 0 017.5 2c0 5.5-7.5 10-7.5 10z"/>',
    "table": '<rect x="3.5" y="4.5" width="17" height="15" rx="2"/><path d="M3.5 9.5h17M3.5 14.5h17M9.5 4.5v15"/>',
    "quiz": '<circle cx="12" cy="12" r="8.5"/><path d="M9.5 9.5a2.5 2.5 0 114 2c-1 .7-1.5 1.2-1.5 2.5M12 16.5v.5"/>',
    "chat": '<path d="M4.5 5.5h15v10h-8l-4 3.5v-3.5h-3z"/><path d="M8 10.5h8"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5"/>',
    "dial": '<path d="M4 16a8 8 0 1116 0"/><path d="M12 16l3.5-5M4 16h16"/>',
    "check": '<rect x="4.5" y="3.5" width="15" height="17" rx="2"/><path d="M8 9l1.5 1.5 3-3M8 15l1.5 1.5 3-3M14.5 9h2M14.5 15h2"/>',
    "note": '<path d="M6.5 3.5h11v17h-11z"/><path d="M9.5 8h5M9.5 11.5h5M9.5 15h3M4.5 7h2M4.5 12h2M4.5 17h2"/>',
    "print": '<path d="M7 9V3.5h10V9M7 17H4.5V9h15v8H17"/><rect x="7" y="14" width="10" height="6.5"/>',
    "home": '<path d="M3.5 11.5L12 4l8.5 7.5"/><path d="M6 9.5v10h12v-10M10 19.5v-5h4v5"/>',
    "key": '<circle cx="8" cy="12" r="4"/><path d="M12 12h8.5M17.5 12v3M20.5 12v2.5"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8.5 10.5V7.5a3.5 3.5 0 017 0v3M12 14.5v2.5"/>',
    "spark": '<path d="M12 3v5M12 16v5M3 12h5M16 12h5M6 6l3 3M15 15l3 3M18 6l-3 3M9 15l-3 3"/>',
}
GLYPH_RULES = [
    ("play", "先に動く"), ("timer", "タイマー|秒"), ("clock", "何時"), ("calendar", "復習"), ("home", "空き巣|自宅|わが家"), ("key", "合言葉"),
    ("lock", "暗号"), ("shield", "詐欺|危険"), ("dial", "診断|判定|タイプ|天気|体験"), ("heart", "脈あり|冷めた|ふたり"),
    ("table", "早見表|索引|辞典"), ("quiz", "クイズ|問"), ("check", "チェック|点検"),
    ("note", "記録|ノート|日記|メモ|シート|ログ"), ("chat", "話す|SNS|相談|声かけ|言いかえ"),
    ("print", "テンプレート|印刷|カード|ルール"), ("search", "探す"),
]


def glyph(it):
    k = it.get("glyph") or next((g for g, pat in GLYPH_RULES if re.search(pat, it.get("name", ""))), "spark")
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{GLYPHS.get(k, GLYPHS["spark"])}</svg>'
CSS = (".tbx{margin:28px 0;background:var(--card);border:1.5px solid var(--accent);border-radius:16px;padding:16px}"
       ".tbx .tbh,.tbtop .tbh{font-size:13px;font-weight:800;letter-spacing:.08em;color:var(--accent);margin:0 0 10px}"
       ".tbi{display:flex;gap:12px;align-items:center;text-decoration:none;color:var(--text);padding:10px 0;border-top:1px solid var(--border)}"
       ".tbx .tbi:first-of-type{border-top:0}"
       ".tbic{flex:0 0 48px;width:48px;height:48px;border-radius:12px;overflow:hidden;display:flex;align-items:center;justify-content:center;"
       "background:color-mix(in srgb,var(--accent) 16%,var(--card))}.tbic img{width:48px;height:48px;display:block}.tbic svg{width:28px;height:28px;fill:none;stroke:var(--accent);stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}"
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


def _row(it, cfg, icon=True):
    ic = f'<img src="{it["icon"]}" alt="" width="48" height="48" loading="lazy">' if it.get("icon") else glyph(it)
    ics = f'<span class="tbic">{ic}</span>' if icon else ""
    if it["app"]:
        href, kind, go, ext = store_url(it, cfg), "iPhoneアプリ・無料・広告なし", "App Storeで見る", ' target="_blank" rel="noopener"'
    else:
        href, kind, go, ext = it["href"], "Webツール・登録不要・無料", "使ってみる", ""
    return (f'<a class="tbi" href="{E(href, quote=True)}"{ext}>{ics}'
            f'<span class="tbt"><em>{kind}</em><b>{E(it["name"])}</b><small>{E(it["desc"])}</small></span><span class="tbgo">{go}</span></a>')


def pick(cfg, p, its):
    def score(x):
        return 3 if p["slug"] in x.get("slugs", []) else 2 if p["category"] in x.get("cats", []) else 1 if x.get("all") else 0
    # 記事ごとに指定済みの「ツールで確かめる」(media/{slug}-toollinks.json) があれば、その先頭をツール枠に使う
    if _toollinks(cfg).get(p["slug"], None) == []:  # toollinks で空を指定した記事には、合う道具がないので何も出さない
        return []
    tl = (_toollinks(cfg).get(p["slug"]) or [None])[0]
    if tl:
        its = [{"name": tl[1], "desc": tl[2], "href": tl[0], "app": False, "slugs": [p["slug"]], "_tl": 4}] + its
        score0 = score
        score = lambda x: x.get("_tl") or score0(x)  # noqa: E731
    best = []
    for want_app in (False, True):
        cand = [x for x in its if x["app"] == want_app and score(x) and x.get("href") != f'/{p["slug"]}/']  # 道具を置いた記事自身へはリンクしない
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
            + "".join(_row(x, cfg, cfg.get("toolboxArticleIcon", True)) for x in got)  # "toolboxArticleIcon": false で記事内は文字だけ
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
        if CSS[:40] not in s2 and "footer{border-top" in s2:  # ".tbx{" だけだとメディアの articleCss に含まれていて誤判定する
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
