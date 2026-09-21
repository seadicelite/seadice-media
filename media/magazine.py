"""マガジン型トップページ(ナゾロジー風ヒーロー + BigGo風の速報ティッカー)。build.py から呼ばれる。JS不使用。"""
import html

E = html.escape
EXTRA_CSS = """
.ticker{position:fixed;top:56px;left:0;right:0;z-index:90;height:34px;background:var(--card);border-bottom:1px solid var(--border);display:flex;align-items:center;overflow:hidden}
.ticker .lb{flex:0 0 auto;font-size:11px;font-weight:800;letter-spacing:.14em;color:var(--bg);background:var(--accent);padding:0 12px;height:100%;display:flex;align-items:center}
.ticker .tr{flex:1;overflow:hidden;white-space:nowrap;mask-image:linear-gradient(90deg,transparent,#000 24px,#000 calc(100% - 24px),transparent)}
.ticker .tk{display:inline-block;padding-left:100%;animation:tk 60s linear infinite}
.ticker .tr:hover .tk{animation-play-state:paused}
.ticker a{color:var(--text);font-size:12.5px;text-decoration:none;margin-right:36px}.ticker a b{color:var(--accent);font-weight:700;margin-right:6px}
@keyframes tk{to{transform:translateX(-100%)}}@media(prefers-reduced-motion:reduce){.ticker .tk{animation:none;padding-left:0}}
main.mag{padding-top:132px}
.mhero{display:grid;gap:16px;grid-template-columns:1fr;margin-bottom:44px}@media(min-width:860px){.mhero{grid-template-columns:1.6fr 1fr}}
.feat{position:relative;display:flex;align-items:flex-end;min-height:340px;border-radius:18px;overflow:hidden;text-decoration:none;color:var(--text);border:1px solid var(--border);background:linear-gradient(140deg,color-mix(in srgb,var(--c) 45%,var(--bg)),color-mix(in srgb,var(--c) 8%,var(--bg)))}
.feat svg.bg{position:absolute;right:-30px;top:-20px;width:260px;height:260px;fill:var(--c);opacity:.18}
.feat img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.feat .sh{position:absolute;inset:0;background:linear-gradient(180deg,transparent 30%,rgba(0,0,0,.78))}
.feat .in{position:relative;padding:22px 24px}.feat .tag{background:var(--bg)}.feat h2{font-size:clamp(22px,4.2vw,30px);line-height:1.4;margin:10px 0 8px;font-weight:800}.feat p{font-size:14px;opacity:.88;max-width:560px}
.side{display:flex;flex-direction:column;gap:10px}.side h3{font-size:12px;letter-spacing:.14em;color:var(--muted)}
.srow{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--text)}.srow:hover{border-color:var(--accent)}.srow .t{font-size:14.5px;font-weight:700;line-height:1.5;margin-top:6px}.srow time{font-size:11px;color:var(--muted)}
.tiles{display:grid;gap:12px;grid-template-columns:1fr 1fr;margin-bottom:44px}@media(min-width:760px){.tiles{grid-template-columns:repeat(3,1fr)}}
.tile{display:block;text-decoration:none;color:var(--text);background:linear-gradient(150deg,color-mix(in srgb,var(--c) 22%,var(--card)),var(--card));border:1px solid var(--border);border-top:3px solid var(--c);border-radius:14px;padding:16px}.tile:hover{border-color:var(--c)}
.tile svg{width:26px;height:26px;fill:var(--c)}.tile b{display:block;font-size:15px;margin:8px 0 4px}.tile span{display:block;font-size:12px;color:var(--muted);line-height:1.6}.tile i{font-style:normal;font-size:11px;color:var(--c);display:block;margin-top:8px}
.two{display:grid;gap:28px;grid-template-columns:1fr;margin-bottom:44px}@media(min-width:860px){.two{grid-template-columns:1.4fr 1fr}}
.rank{list-style:none;counter-reset:r}.rank li{counter-increment:r;display:flex;gap:12px;align-items:flex-start;padding:12px 0;border-bottom:1px solid var(--border)}
.rank li::before{content:counter(r);flex:0 0 30px;height:30px;border-radius:8px;background:var(--card);border:1px solid var(--border);display:flex;align-items:center;justify-content:center;font-weight:800;color:var(--accent)}
.rank li:nth-child(-n+3)::before{background:var(--accent);color:var(--bg);border-color:var(--accent)}
.rank a{color:var(--text);text-decoration:none;font-size:14.5px;font-weight:700;line-height:1.55}.rank a:hover{color:var(--accent)}.rank small{display:block;font-size:11px;color:var(--muted);margin-top:2px}
.nrow{display:flex;gap:12px;align-items:baseline;padding:11px 0;border-bottom:1px solid var(--border);text-decoration:none;color:var(--text)}.nrow:hover .t{color:var(--accent)}.nrow time{flex:0 0 74px;font-size:11.5px;color:var(--muted);font-variant-numeric:tabular-nums}.nrow .t{font-size:14.5px;line-height:1.55}.nrow .c{font-size:11px;color:var(--c);margin-left:8px;white-space:nowrap}
.sechead{display:flex;align-items:baseline;justify-content:space-between;margin:0 0 14px}.sechead h2{font-size:18px;font-weight:800;padding-left:12px;border-left:4px solid var(--accent)}.sechead span{font-size:12px;color:var(--muted)}
.mini{display:grid;gap:12px;grid-template-columns:1fr 1fr}@media(min-width:760px){.mini{grid-template-columns:repeat(4,1fr)}}
.mini a{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 14px;text-decoration:none;color:var(--text);font-size:13.5px;font-weight:700;line-height:1.5}.mini a:hover{border-color:var(--accent)}.mini small{display:block;font-size:11px;color:var(--muted);font-weight:400;margin-top:4px}
.trust{display:grid;gap:10px;grid-template-columns:1fr;margin:48px 0 8px}@media(min-width:760px){.trust{grid-template-columns:repeat(3,1fr)}}
.trust div{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px;font-size:12.5px;color:var(--muted);line-height:1.7}.trust b{display:block;color:var(--accent);font-size:13px;margin-bottom:2px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin:0 0 14px}.tabs a{font-size:12px;color:var(--text);text-decoration:none;border:1px solid var(--border);border-radius:999px;padding:4px 12px;background:var(--card)}
"""


def render(cfg, posts, cats, images, types, img_url, card):
    def cat(p):
        return cats.get(p["category"], {"id": "x", "color": "#64748b", "icon": ""})

    def tag(p):
        c = cat(p)
        return f'<span class="tag" style="--c:{c["color"]}">{E(p["category"])}</span>'

    # ティッカー(速報を優先、なければ新着)
    tick_src = [p for p in posts if p.get("type") == "news"] or posts
    ticker = "".join(f'<a href="/{p["slug"]}/"><b>{E(p["date"][5:].replace("-", "/"))}</b>{E(p["title"])}</a>' for p in tick_src[:10])
    ticker_html = f'<div class="ticker"><span class="lb">NEWS</span><div class="tr"><div class="tk">{ticker}</div></div></div>' if ticker else ""

    # ヒーロー
    feat = next((p for p in posts if p.get("featured")), posts[0] if posts else None)
    hero = ""
    if feat:
        c = cat(feat)
        im = images.get(feat["slug"])
        bg = f'<img src="{img_url(im, 960, 540)}" alt="{E(im["alt"], quote=True)}" width="960" height="540"><span class="sh"></span>' if im else f'<svg class="bg" viewBox="0 0 24 24"><path d="{c["icon"]}"/></svg><span class="sh"></span>'
        others = [p for p in posts if p is not feat][:4]
        side = "".join(f'<a class="srow" href="/{p["slug"]}/">{tag(p)}<p class="t">{E(p["title"])}</p><time datetime="{p["date"]}">{p["date"]}</time></a>' for p in others)
        hero = (f'<div class="mhero"><a class="feat" style="--c:{c["color"]}" href="/{feat["slug"]}/">{bg}<div class="in">{tag(feat)}'
                f'<h2>{E(feat["title"])}</h2><p>{E(feat["summary"])}</p></div></a><div class="side"><h3>LATEST</h3>{side}</div></div>')

    # カテゴリタイル
    tiles = ""
    for n, v in cats.items():
        cnt = sum(1 for p in posts if p["category"] == n)
        desc = next((c.get("desc", "") for c in cfg["categories"] if isinstance(c, dict) and c["name"] == n), "")
        tiles += (f'<a class="tile" href="#c-{v["id"]}" style="--c:{v["color"]}"><svg viewBox="0 0 24 24"><path d="{v["icon"]}"/></svg>'
                  f'<b>{E(n)}</b><span>{E(desc)}</span><i>{cnt}本</i></a>')

    # ランキング + 速報
    ranked = sorted([p for p in posts if p.get("rank")], key=lambda p: p["rank"])[:5] or posts[:5]
    rank = "".join(f'<li><div><a href="/{p["slug"]}/">{E(p["title"])}</a><small>{E(p["category"])}</small></div></li>' for p in ranked)
    news = [p for p in posts if p.get("type") == "news"][:8]
    nrows = "".join(f'<a class="nrow" style="--c:{cat(p)["color"]}" href="/{p["slug"]}/"><time datetime="{p["date"]}">{p["date"][5:].replace("-", "/")}</time><span class="t">{E(p["title"])}<span class="c">{E(p["category"])}</span></span></a>' for p in news)
    two = (f'<div class="two"><section><div class="sechead"><h2>研究速報</h2><span>NEWS</span></div>{nrows or "<p class=empty>準備中です。</p>"}</section>'
           f'<section><div class="sechead"><h2>人気ランキング</h2><span>TOP 5</span></div><ol class="rank">{rank}</ol></section></div>')

    # 深掘り(カード)・用語(ミニ)・まとめ
    guides = [p for p in posts if p.get("type") == "guide"][:6]
    gsec = f'<section><div class="sechead"><h2>深掘り</h2><span>GUIDE</span></div><div class="grid">{"".join(card(p, cats, images, types) for p in guides)}</div></section>' if guides else ""
    terms = [p for p in posts if p.get("type") == "term"][:8]
    tsec = (f'<section style="margin-top:44px"><div class="sechead"><h2>用語ミニ辞典</h2><span>TERMS</span></div><div class="mini">'
            + "".join(f'<a href="/{p["slug"]}/">{E(p["title"])}<small>{E(p["category"])}</small></a>' for p in terms) + '</div></section>') if terms else ""
    weekly = [p for p in posts if p.get("type") == "weekly"][:3]
    wsec = (f'<section style="margin-top:44px"><div class="sechead"><h2>今週のまとめ</h2><span>WEEKLY</span></div><div class="grid">{"".join(card(p, cats, images, types) for p in weekly)}</div></section>') if weekly else ""

    trust = ('<div class="trust"><div><b>AIが出典を確認して作成</b>公開されている研究論文・公的機関の資料をAIが調べ、内容を照合しています。</div>'
             '<div><b>診断ではありません</b>特定の人を診断・判定するものではありません。深刻な被害や不調は専門機関へ。</div>'
             '<div><b>断定しません</b>仕草や行動は「研究ではこうだった」と精度や限界を添えて紹介します。</div></div>')
    return ticker_html, f'{hero}<h2 class="sec">CATEGORIES</h2><div class="tiles">{tiles}</div>{two}{gsec}{tsec}{wsec}{trust}'
