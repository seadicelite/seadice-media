"""記事マップ(マインドマップ)ページ → /map/。media/{slug}-map.json があるメディアだけ。extras.apply から呼ばれる。

中心(メディア名) → 分野(カテゴリ) → 問い(枝) → 記事(葉)。分野はタップで開閉する <details>、中身は入れ子の <ul> なので、
JSなしで動き、AIや検索エンジンにはそのまま構造化された目次として読める。

map.json の形:
  {"title", "seo_title", "desc", "lead", "date",
   "branches": {カテゴリ名: [{"label": 問い, "slugs": [記事slug...], "tools": [{"label", "path"}]}]}}
新しい記事を書いたら、合う枝の slugs に足す。足し忘れた記事は、そのカテゴリの「新しい記事」の枝に自動で入る(ビルド時に警告を出す)。
"""
import html
import json
import re

E = html.escape

CSS = (".mm-lead{font-size:15px;line-height:1.85;max-width:680px;margin:0 0 8px}"
       ".mm-stat{font-size:13px;color:var(--muted);margin:0 0 28px}"
       ".mm{margin:0 0 40px}"
       ".mm-root{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;"
       "min-height:96px;margin:0 0 20px;padding:16px;border-radius:24px;background:radial-gradient(circle at 30% 20%,rgba(242,166,90,.28),transparent 60%),var(--card);"
       "border:1px solid var(--accent)}"
       ".mm-root b{font-size:20px;letter-spacing:.06em}.mm-root span{font-size:13px;color:var(--muted);margin-top:4px}"
       ".mm-cats{list-style:none;margin:0;padding:0 0 0 18px;border-left:2px solid var(--border)}"
       ".mm-cat{position:relative;z-index:1;margin:0 0 14px;background:var(--card);border:1px solid var(--border);border-top:3px solid var(--c);border-radius:16px}"
       ".mm-cat::before{content:\"\";position:absolute;left:-21px;top:26px;width:19px;border-top:2px solid var(--border)}"
       ".mm-cat summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:10px;padding:14px 16px;min-height:52px;font-size:16px;font-weight:800;border-radius:14px}"
       ".mm-cat summary::-webkit-details-marker{display:none}"
       ".mm-cat summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"
       ".mm-cat summary::after{content:\"\";margin-left:auto;flex:none;width:9px;height:9px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);transform:rotate(45deg) translate(-2px,-2px);transition:transform .2s}"
       ".mm-cat details[open] summary::after{transform:rotate(-135deg) translate(-2px,-2px)}"
       ".mm-n{flex:none;font-size:12px;font-weight:700;color:var(--c);border:1px solid var(--c);border-radius:999px;padding:1px 9px}"
       ".mm-d{display:block;font-size:12.5px;font-weight:400;color:var(--muted);margin-top:2px;line-height:1.5}"
       ".mm-br{list-style:none;margin:0 16px 14px 22px;padding:0 0 0 16px;border-left:2px solid var(--border)}"
       ".mm-bl{position:relative;font-size:14px;font-weight:800;color:var(--c);margin:14px 0 4px}"
       ".mm-bl::before{content:\"\";position:absolute;left:-18px;top:.75em;width:14px;border-top:2px solid var(--border)}"
       ".mm-bl small{font-weight:400;color:var(--muted);margin-left:6px}"
       ".mm-lv{list-style:none;margin:0;padding:0}"
       ".mm-lv a{display:block;padding:8px 10px;border-radius:10px;font-size:14px;line-height:1.6;color:var(--text);text-decoration:none}"
       ".mm-lv a:hover,.mm-lv a:focus-visible{background:rgba(255,255,255,.06);color:var(--link)}"
       ".mm-tool{display:inline-block;font-size:11px;font-weight:700;color:var(--bg);background:var(--c);border-radius:6px;padding:1px 6px;margin-right:6px;vertical-align:1px}"
       "@media(min-width:900px){"
       ".mm-root{width:240px;min-height:120px;margin:0 auto 28px}"
       ".mm-root::after{content:\"\";position:absolute;top:100%;left:50%;height:28px;border-left:2px solid var(--border)}"
       ".mm-cols{position:relative;display:grid;grid-template-columns:repeat(3,1fr);gap:28px;padding-top:28px;align-items:start}"
       ".mm-cols::before{content:\"\";position:absolute;top:0;left:calc((100% - 56px)/6);right:calc((100% - 56px)/6);border-top:2px solid var(--border)}"
       ".mm-col{position:relative}"
       ".mm-col::before{content:\"\";position:absolute;top:-28px;bottom:40px;left:50%;border-left:2px solid var(--border)}"
       ".mm-cats{padding:0;border:0}.mm-cat::before{display:none}"
       "}")


def _short(title):
    """記事タイトルの前半(問いの部分)を葉の文言にする。短すぎるときは全文。"""
    m = re.match(r"(.+?[。？?])", title)
    s = m.group(1).rstrip("。") if m else title
    return s if len(s) >= 8 else title


def build(cfg, posts, cats, page):
    """cats は build.cats_of の {カテゴリ名: 情報}。page は extras._page を部分適用した関数 (rel, title, desc, body, graph, trail, extra_css) -> url。"""
    from extras import _load
    m = _load(cfg["slug"], "map")
    if not m:
        return []
    by = {p["slug"]: p for p in posts}
    tree, used = [], set()
    for name, info in cats.items():
        c = dict(info, name=name)
        brs = []
        for b in m["branches"].get(c["name"], []):
            ss = [s for s in b["slugs"] if s in by]
            used.update(ss)
            if ss or b.get("tools"):
                brs.append((b["label"], ss, b.get("tools", [])))
        rest = [p["slug"] for p in posts if p["category"] == c["name"] and p["slug"] not in used]
        if rest:
            print(f"  map: 枝に入っていない記事 {len(rest)}本 ({c['name']}): {', '.join(rest)}")
            brs.append(("新しい記事", rest, []))
            used.update(rest)
        if brs:
            tree.append((c, brs))
    total = sum(len(ss) for _, brs in tree for _, ss, _ in brs)

    def cat_html(c, brs):
        n = sum(len(ss) for _, ss, _ in brs)
        lis = ""
        for label, ss, tools in brs:
            leaves = "".join(f'<li><a href="{E(t["path"])}"><span class="mm-tool">ツール</span>{E(t["label"])}</a></li>' for t in tools)
            leaves += "".join(f'<li><a href="/{s}/">{E(_short(by[s]["title"]))}</a></li>' for s in ss)
            lis += f'<li><p class="mm-bl">{E(label)}<small>{len(ss)}本</small></p><ul class="mm-lv">{leaves}</ul></li>'
        return (f'<li class="mm-cat" style="--c:{c.get("color", "var(--accent)")}"><details><summary>'
                f'<span>{E(c["name"])}<span class="mm-d">{E(c.get("desc", ""))}</span></span><span class="mm-n">{n}本</span></summary>'
                f'<ul class="mm-br">{lis}</ul></details></li>')

    k = -(-len(tree) // 3)  # PCでは3列。上から順に列を埋める
    cols = "".join(f'<div class="mm-col"><ul class="mm-cats">{"".join(cat_html(c, b) for c, b in tree[i * k:(i + 1) * k])}</ul></div>'
                   for i in range(3) if tree[i * k:(i + 1) * k])
    body = (f'  <div class="hero"><h1>{E(cfg["name"])} {E(m["title"])}</h1></div>\n'
            f'  <p class="mm-lead">{E(m["lead"])}</p>\n'
            f'  <p class="mm-stat">{len(tree)}分野・{sum(len(b) for _, b in tree)}の問い・{total}本の記事（記事が増えると自動で更新されます）</p>\n'
            f'  <div class="mm"><div class="mm-root"><b>{E(cfg["name"])}</b><span>{total}本の記事</span></div>'
            f'<div class="mm-cols">{cols}</div></div>')
    rel = "map/"
    url = cfg["url"] + rel
    order = [s for _, brs in tree for _, ss, _ in brs for s in ss]
    pub = {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}
    graph = [{"@type": "CollectionPage", "name": f'{cfg["name"]} {m["title"]}', "url": url, "description": m["desc"],
              "dateModified": max([m.get("date", "")] + [p["date"] for p in posts]), "publisher": pub,
              "mainEntity": {"@type": "ItemList", "numberOfItems": len(order), "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "name": by[s]["title"], "url": cfg["url"] + s + "/"} for i, s in enumerate(order)]}}]
    return [page(rel, f'{m.get("seo_title") or m["title"]} | {cfg["name"]}', m["desc"], body, graph, [(m["title"], url)], CSS)]


def branches_for_llms(cfg, posts):
    """llms.txt の記事一覧を「カテゴリ > 問い」に分けるための {カテゴリ名: [(問い, [slug])]}。map が無ければ None。"""
    from extras import _load
    m = _load(cfg["slug"], "map")
    if not m:
        return None
    have = {p["slug"] for p in posts}
    return {c: [(b["label"], [s for s in b["slugs"] if s in have]) for b in bs] for c, bs in m["branches"].items()}
