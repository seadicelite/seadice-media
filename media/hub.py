"""悩み・年齢から入るトップページ(layout: "hub")。build.py から呼ばれる。JS不使用。

忙しい読者がスマホで「自分の場合の答え」に少ない操作で届くことを優先する。
写真カードを全記事分並べず、記事一覧はテーマごとに折りたたむ(全記事へのリンクはHTMLに残す)。
設定は media/{slug}.json の "hub":
  ages:      [{label, sub, href}]          年齢などの入口(大きなボタン)
  questions: [{q, slug}]                   よくある悩み(答えは記事の summary を出す)
  actions:   [{label, desc, href}]         家族で使うページ(印刷用ルール表など)
  actionsLead: str                         actions の説明文
  agesTitle / agesLead / questionsTitle / questionsLead / actionsTitle: 見出しの差し替え(省略時は子育てデータ向けの文言)
"""
import html

E = html.escape
EXTRA_CSS = """
.kh{margin:0 0 56px}.kh>h2{font-size:20px;font-weight:900;line-height:1.5;margin:0 0 6px}.kh>p.kl{font-size:14px;color:var(--muted);line-height:1.8;margin:0 0 16px}
.kh-age{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(min-width:760px){.kh-age{grid-template-columns:repeat(4,1fr)}}
.kh-age a{display:block;background:var(--card);border:1.5px solid var(--text);border-radius:18px;padding:18px 16px;text-decoration:none;color:var(--text);box-shadow:3px 3px 0 var(--text)}
.kh-age a:hover,.kh-age a:focus-visible{transform:translate(-1px,-1px);box-shadow:4px 4px 0 var(--text)}
.kh-age b{display:block;font-size:22px;font-weight:900;line-height:1.3}.kh-age span{display:block;font-size:13px;color:var(--muted);line-height:1.6;margin-top:6px}
.kh-q{display:flex;flex-direction:column;gap:12px}
.kh-q a{display:block;background:var(--card);border:1px solid var(--border);border-left:5px solid var(--c,var(--accent));border-radius:14px;padding:16px 18px;text-decoration:none;color:var(--text)}
.kh-q a:hover,.kh-q a:focus-visible{border-color:var(--c,var(--accent))}
.kh-q b{display:block;font-size:16px;font-weight:800;line-height:1.55}.kh-q span{display:block;font-size:14px;color:var(--muted);line-height:1.75;margin-top:6px}
.kh-act{display:grid;gap:12px;grid-template-columns:1fr}@media(min-width:760px){.kh-act{grid-template-columns:repeat(3,1fr)}}
.kh-act a{display:block;background:var(--card);border:1.5px dashed var(--accent2);border-radius:16px;padding:16px 18px;text-decoration:none;color:var(--text)}
.kh-act b{display:block;font-size:16px;font-weight:800;color:var(--accent2)}.kh-act span{display:block;font-size:14px;color:var(--muted);line-height:1.7;margin-top:4px}
.kh .grid{margin-top:4px}
.kh-tool{display:block;margin:-24px 0 40px;background:var(--card);border:2px solid var(--accent);border-radius:18px;padding:18px 20px;text-decoration:none;color:var(--text);box-shadow:4px 4px 0 var(--accent)}
.kh-tool small{display:inline-block;font-size:12px;font-weight:800;color:#fff;background:var(--accent);border-radius:999px;padding:2px 10px}
.kh-tool b{display:block;font-size:18px;font-weight:900;margin-top:8px;line-height:1.5}.kh-tool span{display:block;font-size:14px;color:var(--muted);line-height:1.7;margin-top:4px}
.kh-tool i{display:inline-block;font-style:normal;font-size:14px;font-weight:800;color:var(--link);margin-top:8px}
.kh-cat{background:var(--card);border:1px solid var(--border);border-radius:16px;margin-bottom:12px}
.kh-cat summary{list-style:none;cursor:pointer;padding:16px 18px;display:flex;gap:12px;align-items:center}.kh-cat summary::-webkit-details-marker{display:none}
.kh-cat summary svg{flex:0 0 26px;width:26px;height:26px;fill:var(--c)}
.kh-cat summary div{flex:1}.kh-cat summary b{display:block;font-size:16px;font-weight:800}.kh-cat summary small{display:block;font-size:13px;color:var(--muted);line-height:1.6;margin-top:2px}
.kh-cat summary i{font-style:normal;font-size:13px;font-weight:700;color:var(--c);white-space:nowrap}
.kh-cat summary::after{content:"+";font-size:22px;font-weight:700;color:var(--muted);width:20px;text-align:center}.kh-cat[open] summary::after{content:"−"}
.kh-cat ul{list-style:none;border-top:1px solid var(--border);padding:4px 18px 8px}.kh-cat li{border-bottom:1px solid var(--border)}.kh-cat li:last-child{border-bottom:0}
.kh-cat li a{display:block;padding:12px 0;font-size:15px;line-height:1.6;color:var(--text);text-decoration:none}.kh-cat li a:hover{color:var(--accent)}
.kh-cat li.all a{font-size:14px;font-weight:700;color:var(--link)}
"""


def render(cfg, posts, cats, images, types, card):
    h = cfg.get("hub", {})
    by_slug = {p["slug"]: p for p in posts}
    out = ""

    ages = h.get("ages", [])
    if ages:
        out += (f'<section class="kh"><h2>{E(h.get("agesTitle", "お子さんは何歳ですか？"))}</h2><p class="kl">{E(h.get("agesLead", "年齢ごとに、まず読んでほしい記事をまとめています。"))}</p><div class="kh-age">'
                + "".join(f'<a href="{E(a["href"], quote=True)}"><b>{E(a["label"])}</b><span>{E(a.get("sub", ""))}</span></a>' for a in ages)
                + "</div></section>")

    for tool in h.get("tools") or ([h["tool"]] if h.get("tool") else []):
        out += (f'<a class="kh-tool" href="{E(tool["href"], quote=True)}"><small>{E(tool.get("kicker", "ツール"))}</small>'
                f'<b>{E(tool["label"])}</b><span>{E(tool.get("desc", ""))}</span><i>使ってみる</i></a>')

    qs = [(q["q"], by_slug[q["slug"]]) for q in h.get("questions", []) if q["slug"] in by_slug]
    if qs:
        rows = ""
        for q, p in qs:
            c = cats.get(p["category"], {"color": "var(--accent)"})
            rows += f'<a href="/{p["slug"]}/" style="--c:{c["color"]}"><b>{E(q)}</b><span>{E(p["summary"])}</span></a>'
        out += f'<section class="kh"><h2>{E(h.get("questionsTitle", "よくある悩みから"))}</h2><p class="kl">{E(h.get("questionsLead", "研究と公的な指針から、先に答えを書いています。"))}</p><div class="kh-q">{rows}</div></section>'

    acts = h.get("actions", [])
    if acts:
        out += (f'<section class="kh"><h2>{E(h.get("actionsTitle", "家族で話し合うときに"))}</h2><p class="kl">{E(h.get("actionsLead", ""))}</p><div class="kh-act">'
                + "".join(f'<a href="{E(a["href"], quote=True)}"><b>{E(a["label"])}</b><span>{E(a.get("desc", ""))}</span></a>' for a in acts)
                + "</div></section>")

    out += f'<section class="kh"><h2>新しい記事</h2><div class="grid">{"".join(card(p, cats, images, types) for p in posts[:h.get("latest", 4)])}</div></section>'

    blocks = ""
    for n, v in cats.items():
        items = [p for p in posts if p["category"] == n]
        if not items:
            continue
        desc = next((c.get("desc", "") for c in cfg["categories"] if isinstance(c, dict) and c["name"] == n), "")
        lis = "".join(f'<li><a href="/{p["slug"]}/">{E(p["title"])}</a></li>' for p in items)
        blocks += (f'<details class="kh-cat" style="--c:{v["color"]}"><summary><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{v["icon"]}"/></svg>'
                   f'<div><b>{E(n)}</b><small>{E(desc)}</small></div><i>{len(items)}本</i></summary>'
                   f'<ul>{lis}<li class="all"><a href="/category/{v["id"]}/">{E(n)}の記事を写真つきで見る</a></li></ul></details>')
    out += f'<section class="kh"><h2>テーマから探す</h2><p class="kl">タップすると、そのテーマの記事が開きます。</p>{blocks}</section>'
    return out
