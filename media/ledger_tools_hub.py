"""お金と心理(ledger)のツール一覧 /tools/ を、記事のうち計算表・チェック表・セルフチェックから作る。
トップより大事な入口なので、記事が増えたら毎回作り直す（deploy.yml で build.py の前に実行）。"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "sites", "ledger")
URL = "https://ledger.seadice.win"

GROUPS = [  # (id, 見出し, 説明, 判定)
    ("calc", "計算する", "1年でいくら・月いくら・何か月分。表に沿って計算すると、お金の重さが見えます。", lambda s: "calculator" in s or "outlook" in s),
    ("before", "買う前に確かめる", "買う直前に使うチェック表。迷ったら上から順に確かめるだけです。", lambda s: "checklist" in s),
    ("self", "自分のくせをチェック", "研究で使われる質問をもとにした振り返り。点数ではなく、くせに気づくためのものです。", lambda s: "self-check" in s or s.endswith("-check")),
]


def main():
    posts = json.load(open(os.path.join(ROOT, "media", "ledger-posts.json")))
    posts = posts if isinstance(posts, list) else posts["posts"]
    posts = [p for p in posts if os.path.exists(os.path.join(SITE, p["slug"], "index.html"))]
    groups = {g[0]: [] for g in GROUPS}
    for p in sorted(posts, key=lambda p: p["date"], reverse=True):
        for gid, _, _, hit in GROUPS:
            if hit(p["slug"]):
                groups[gid].append(p)
                break
    n = 1 + sum(len(v) for v in groups.values())

    def card(href, title, desc, badge):
        return (f'<a class="tool" href="{href}"><span class="tb">{badge}</span>'
                f'<b>{html.escape(title)}</b><span class="td">{html.escape(desc)}</span></a>')

    secs = ['<h2 id="wait">記録して使う</h2><p>欲しい物をすぐ買わずに入れておき、時間をおいて「まだ欲しい？」と決める道具です。記録はこの端末のブラウザ内だけに残ります。</p><div class="tools">'
            + card("/wait-list/", "衝動買いを防ぐ待つリスト", "24時間・3日・1週間たってから決める。買う前チェックと、守れたお金の記録つき。", "道具") + "</div>"]
    for gid, h, d, _ in GROUPS:
        if groups[gid]:
            secs.append(f'<h2 id="{gid}">{h}</h2><p>{d}</p><div class="tools">'
                        + "".join(card(f"/{p['slug']}/", p["title"], p.get("summary", ""), {"calc": "計算表", "before": "チェック表", "self": "セルフチェック"}[gid]) for p in groups[gid]) + "</div>")
    toc = "".join(f'<a href="#{i}">{h}</a>' for i, h in [("wait", "記録して使う")] + [(g[0], g[1]) for g in GROUPS if groups[g[0]]])

    tpl = open(os.path.join(SITE, "glossary", "index.html")).read()
    styles = tpl[tpl.index("<style>"):tpl.index("</head>")]
    styles = styles.replace("footer{", ".tools{display:grid;gap:12px;grid-template-columns:1fr;margin:14px 0}@media(min-width:620px){.tools{grid-template-columns:1fr 1fr}}.tool{display:block;background:var(--card);border:1px solid var(--border);padding:16px 18px;text-decoration:none;color:var(--text)}.tool:hover,.tool:focus-visible{border-color:var(--accent)}.tool b{display:block;font-size:16px;line-height:1.5;margin:6px 0 4px}.tool .td{display:block;font-size:13px;color:var(--muted);line-height:1.7}.tb{display:inline-block;font-size:12px;color:#FBF3E9;background:var(--accent2);padding:1px 8px}", 1)
    foot = tpl[tpl.index("<footer>"):]
    title = f"お金のツール{n}本｜計算表・買う前チェック・くせのチェック | お金と心理"
    desc = f"衝動買いを防ぐ待つリスト、1年でいくらの計算表、買う前のチェック表、研究の質問で振り返るセルフチェックなど、お金と心理の無料ツール{n}本。登録不要。"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": "お金のツール", "url": URL + "/tools/", "inLanguage": "ja", "description": desc,
         "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "お金と心理", "item": URL + "/"},
            {"@type": "ListItem", "position": 2, "name": "ツール", "item": URL + "/tools/"}]}]}
    out = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{URL}/tools/">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{URL}/tools/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary">
<meta name="robots" content="index,follow">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
{styles}</head>
<body>
<nav>
  <a href="https://seadice.win/" class="nav-logo">SEADICE</a>
  <a href="/" class="r">お金と心理</a>
</nav>
<article>
  <p class="breadcrumb"><a href="/">お金と心理</a> / ツール</p>
  <h1>お金のツール</h1>
  <p class="lead">読むだけで終わらせず、自分のお金で確かめるためのツール{n}本です。どれも無料・登録不要です。</p>
  <div class="toc">{toc}</div>
  {"".join(secs)}
</article>
{foot}'''
    os.makedirs(os.path.join(SITE, "tools"), exist_ok=True)
    open(os.path.join(SITE, "tools", "index.html"), "w").write(out)
    print(f"ledger tools: {n}")


if __name__ == "__main__":
    main()
