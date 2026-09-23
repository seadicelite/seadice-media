#!/usr/bin/env python3
"""media/{slug}-posts.json から一覧ページ(sites/{slug}/index.html)とsitemapを再生成する。
使い方: python3 media/build.py <slug>   （設定は media/{slug}.json の theme / categories / types）
記事を追加するときは posts.json の先頭に1件足してから実行する。JS不使用。"""
import html, json, sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ICONS = {  # カテゴリ用アイコン(24x24 path)
    "moon": "M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z",
    "target": "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 5a5 5 0 1 1 0 10 5 5 0 0 1 0-10zm0 3a2 2 0 1 0 0 4 2 2 0 0 0 0-4z",
    "clock": "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm1 5v5.4l3.7 2.2-.8 1.3L11 13V7z",
    "heart": "M12 21s-8-5.2-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 5.8-8 11-8 11z",
    "repeat": "M17 2l4 4-4 4V7H8a3 3 0 0 0-3 3v1H3v-1a5 5 0 0 1 5-5h9V2zm-10 20l-4-4 4-4v3h9a3 3 0 0 0 3-3v-1h2v1a5 5 0 0 1-5 5H7v3z",
    "book": "M4 4h7a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4V4zm16 0h-4a3 3 0 0 0-2 .8V20a2 2 0 0 1 2-2h4V4z",
    "mask": "M12 3C7 3 3 5 3 9c0 5 4 12 9 12s9-7 9-12c0-4-4-6-9-6zM8.5 9a2 2 0 1 1 0 4 2 2 0 0 1 0-4zm7 0a2 2 0 1 1 0 4 2 2 0 0 1 0-4z",
    "eye": "M12 5C6 5 2 12 2 12s4 7 10 7 10-7 10-7-4-7-10-7zm0 11a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm0-2.2a1.8 1.8 0 1 0 0-3.6 1.8 1.8 0 0 0 0 3.6z",
    "shield": "M12 2l8 3v6c0 5-3.5 9.5-8 11-4.5-1.5-8-6-8-11V5l8-3z",
    "link": "M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1 1.4 1.4 1-1a2 2 0 1 1 2.8 2.8l-3 3a2 2 0 0 1-2.8 0zm4-4a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1-1.4-1.4-1 1a2 2 0 1 1-2.8-2.8l3-3a2 2 0 0 1 2.8 0z",
    "dot": "M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z",
}
DEFAULT_THEME = {"bg": "#05050C", "card": "#0C0C1A", "accent": "#00FFD1", "accent2": "#38BDF8", "border": "#1a1a2e",
                 "text": "#e2e8f0", "muted": "#8592a6", "link": "#7dd3fc"}
LEGACY = {  # 旧形式(カテゴリ名だけ)の既定
    "睡眠": ("sleep", "#6366f1", "moon"), "集中力": ("focus", "#06b6d4", "target"), "先延ばし": ("delay", "#f59e0b", "clock"),
    "気分・ストレス": ("mood", "#ec4899", "heart"), "習慣": ("habit", "#10b981", "repeat"), "記憶・学習": ("memory", "#8b5cf6", "book")}


def cats_of(cfg):
    out = {}
    for c in cfg["categories"]:
        if isinstance(c, str):
            i, col, ic = LEGACY[c]
            out[c] = {"id": i, "color": col, "icon": ICONS[ic]}
        else:
            out[c["name"]] = {"id": c["id"], "color": c["color"], "icon": ICONS.get(c.get("icon", "dot"), ICONS["dot"])}
    return out


def img_url(i, w, h):
    if "src" in i:  # Wikimedia Commons(標準幅のサムネイルURL)
        return i["src640"] if w <= 640 else i["src"]
    return f"{i['raw']}&w={w}&h={h}&fit=crop&q=70&fm=webp"


def card(p, cats, images, types):
    c = cats.get(p["category"], {"id": "x", "color": "#64748b", "icon": ICONS["dot"]})
    img = ""
    if p["slug"] in images:
        i = images[p["slug"]]
        img = f'<img src="{img_url(i, 640, 320)}" width="640" height="320" alt="{html.escape(i["alt"], quote=True)}" loading="lazy">'
    th = f'<div class="th" style="--c:{c["color"]}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{c["icon"]}"/></svg>{img}</div>'
    tl = types.get(p.get("type", ""), "")
    tb = f'<span class="ty">{html.escape(tl)}</span>' if tl else ""
    return (f'<a class="card" href="/{p["slug"]}/">{th}<div class="cb"><span class="tag" style="--c:{c["color"]}">{html.escape(p["category"])}</span>{tb}'
            f'<p class="t">{html.escape(p["title"])}</p><p class="d">{html.escape(p["summary"])}</p><time datetime="{p["date"]}">{p["date"]}</time></div></a>')


CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}:root{--bg:%(bg)s;--card:%(card)s;--accent:%(accent)s;--accent2:%(accent2)s;--border:%(border)s;--text:%(text)s;--muted:%(muted)s;--link:%(link)s}html{scroll-behavior:smooth}body{background:var(--bg);color:var(--text);font-family:-apple-system,'Helvetica Neue',sans-serif;line-height:1.7;-webkit-text-size-adjust:100%%}nav.top{position:fixed;top:0;left:0;right:0;z-index:100;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);background:color-mix(in srgb,var(--bg) 82%%,transparent);border-bottom:1px solid var(--border);padding:0 20px;height:56px;display:flex;align-items:center;justify-content:space-between}.nav-logo{font-size:15px;font-weight:800;letter-spacing:.15em;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none}nav.top a.r{font-size:13px;color:var(--muted);text-decoration:none;letter-spacing:.08em}main{max-width:960px;margin:0 auto;padding:88px 20px 64px}.hero{padding:24px 0 28px}h1{font-size:clamp(28px,7vw,46px);font-weight:800;letter-spacing:.06em;line-height:1.15;background:linear-gradient(90deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}.tagline{font-size:15px;color:var(--muted);margin-top:8px;letter-spacing:.04em}.lead{font-size:15px;color:var(--text);opacity:.85;margin-top:14px;max-width:620px}.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 40px}.chip{display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--text);text-decoration:none;border:1px solid var(--border);background:var(--card);border-radius:999px;padding:7px 14px}.chip svg{width:15px;height:15px;fill:var(--c)}.chip:hover{border-color:var(--c)}h2.sec{font-size:14px;letter-spacing:.14em;color:var(--muted);margin:0 0 14px}h2.cat{display:flex;align-items:center;gap:8px;font-size:18px;margin:44px 0 14px;padding-left:12px;border-left:4px solid var(--c)}h2.cat svg{width:20px;height:20px;fill:var(--c)}.grid{display:grid;gap:16px;grid-template-columns:1fr}@media(min-width:620px){.grid{grid-template-columns:1fr 1fr}}@media(min-width:900px){.grid{grid-template-columns:1fr 1fr 1fr}}.card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--border);border-radius:14px;overflow:hidden;text-decoration:none;color:var(--text);transition:border-color .15s,transform .15s}.card:hover{border-color:var(--accent);transform:translateY(-2px)}.th{position:relative;overflow:hidden;aspect-ratio:16/8;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,color-mix(in srgb,var(--c) 38%%,var(--bg)),color-mix(in srgb,var(--c) 10%%,var(--bg)))}.th img{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}.th svg{width:44px;height:44px;fill:var(--c);opacity:.95}.cb{padding:14px 16px 16px}.tag{display:inline-block;font-size:11px;letter-spacing:.06em;color:var(--c);border:1px solid var(--c);border-radius:4px;padding:1px 8px}.ty{display:inline-block;font-size:11px;letter-spacing:.06em;color:var(--bg);background:var(--accent);border-radius:4px;padding:1px 8px;margin-left:6px}.card .t{font-size:16px;font-weight:700;line-height:1.5;margin:8px 0 6px}.card .d{font-size:13px;color:var(--muted);line-height:1.65}.card time{display:block;font-size:11px;color:var(--muted);margin-top:10px}.empty{grid-column:1/-1;background:var(--card);border:1px dashed var(--border);border-radius:12px;padding:20px;font-size:14px;color:var(--muted)}.adslot{margin:40px 0;min-height:250px;background:var(--card);border:1px dashed var(--border);border-radius:12px;display:none}.about{margin-top:56px;padding:22px;background:var(--card);border:1px solid var(--border);border-radius:16px;font-size:14px;color:var(--text);opacity:.92}.about strong{color:var(--accent)}.about a{color:var(--link)}footer{border-top:1px solid var(--border);padding:24px;text-align:center;font-size:12px;color:var(--muted)}footer a{color:var(--muted);margin:0 6px}"""


def build(slug, preview=None):
    cfg = json.loads((ROOT / f"media/{slug}.json").read_text())
    pf = ROOT / (f"media/{slug}-posts.sample.json" if preview else f"media/{slug}-posts.json")
    posts = json.loads(pf.read_text())
    ip = ROOT / f"media/{slug}-images.json"
    images = json.loads(ip.read_text()) if ip.exists() else {}
    theme = {**DEFAULT_THEME, **cfg.get("theme", {})}
    cats = cats_of(cfg)
    types = {t["id"]: t["label"] for t in cfg.get("types", [])}
    posts = sorted(posts, key=lambda p: p["date"], reverse=True)
    name, url = cfg["name"], cfg["url"]
    tagline = cfg.get("tagline", "")
    lead = cfg.get("lead", "")
    chips = "".join(f'<a class="chip" href="#c-{v["id"]}" style="--c:{v["color"]}"><svg viewBox="0 0 24 24"><path d="{v["icon"]}"/></svg>{html.escape(n)}</a>' for n, v in cats.items())
    latest = "".join(card(p, cats, images, types) for p in posts[:12]) or '<p class="empty">記事を準備中です。</p>'
    secs = ""
    for n, v in cats.items():
        items = [p for p in posts if p["category"] == n]
        body = "".join(card(p, cats, images, types) for p in items) or '<p class="empty">記事を準備中です。</p>'
        secs += f'<section id="c-{v["id"]}"><h2 class="cat" style="--c:{v["color"]}"><svg viewBox="0 0 24 24"><path d="{v["icon"]}"/></svg>{html.escape(n)}</h2><div class="grid">{body}</div></section>'
    mag = cfg.get("layout") == "magazine"
    ticker_html = ""
    if mag:
        import magazine
        ticker_html, body_html = magazine.render(cfg, posts, cats, images, types, img_url, card)
        extra_css = magazine.EXTRA_CSS
        secs_html = secs.replace('<section id="c-', '<section style="margin-top:8px" id="c-')
    ttl = f"{name} | {cfg.get('titleSuffix', '')}".rstrip(" |")
    desc = html.escape(cfg.get("description", ""), quote=True)
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": name, "url": url, "publisher": {"@type": "Organization", "name": "SEADICE", "url": "https://seadice.win"}},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": 1, "name": name, "item": url}]}]}, ensure_ascii=False)
    about = cfg.get("about", "記事はAIが公開された研究論文や公的機関の資料を調べ、出典の内容を確認して作成しています。SEADICEが独自に実験したものではありません。各記事の末尾に出典を掲載しています。")
    out = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(ttl)}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{html.escape(ttl, quote=True)}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<script type="application/ld+json">{ld}</script>
<style>{CSS % theme}{extra_css if mag else ""}</style>
</head>
<body>
<nav class="top">
  <a href="https://seadice.win/" class="nav-logo">SEADICE</a>
  <a href="/" class="r">{html.escape(name)}</a>
</nav>
{ticker_html}<main{' class="mag"' if mag else ''}>
  {'' if mag else f'<div class="hero"><h1>{html.escape(name)}</h1><p class="tagline">{html.escape(tagline)}</p><p class="lead">{html.escape(lead)}</p></div><div class="chips" aria-label="カテゴリ">{chips}</div><h2 class="sec">LATEST</h2><div class="grid">{latest}</div>'}
  {body_html + secs_html if mag else secs}

  <div class="about"><strong>このメディアについて</strong><br>{about} 写真は <a href="https://commons.wikimedia.org/" target="_blank" rel="noopener">Wikimedia Commons</a> の自由ライセンス素材で、各記事に撮影者とライセンスを表示しています。</div>
</main>
<footer><p><a href="/about/">このメディアについて</a> | <a href="/sources/">出典と検証の方法</a> | <a href="/disclaimer/">免責事項</a>{"".join(f' | <a href="{n["path"]}">{html.escape(n["label"])}</a>' for n in cfg.get("extraNav", []))} | <a href="https://seadice.win/">SEADICE</a> | &copy; SEADICE</p></footer>
</body>
</html>
'''
    outdir = Path(preview) if preview else ROOT / cfg["path"]
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "index.html").write_text(out)
    if preview:
        return print("preview:", outdir / "index.html")
    sm = ROOT / cfg["path"] / "sitemap.xml"
    s = sm.read_text() if sm.exists() else '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n</urlset>\n'
    urls = ([url] + [f"{url}{p['slug']}/" for p in posts] + [f"{url}{x}/" for x in ("about", "sources", "disclaimer")]
             + [url.rstrip("/") + n["path"] for n in cfg.get("extraNav", []) if not n["path"].startswith("http")])
    add = "".join(f'  <url>\n    <loc>{u}</loc>\n    <lastmod>{posts[0]["date"] if posts else ""}</lastmod>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n' for u in urls if f"<loc>{u}</loc>" not in s)
    sm.write_text(s.replace("</urlset>", add + "</urlset>") if add else s)
    import seo
    n, pages = seo.apply(cfg, posts, images)
    print(f"built {cfg['path']}index.html ({len(posts)} posts), seo-patched {n} articles, {len(pages)} trust pages")


if __name__ == "__main__":
    a = sys.argv[1:]
    build(a[0] if a else "research", a[a.index("--preview") + 1] if "--preview" in a else None)
