"""独学の科学「勉強法の効く・効かない早見表」(/hayami/)を生成し、各記事に早見表へのリンクを差し込む。

データは media/dokugaku-hayami.json
  items: [{id, name(勉強法), belief(よく言われること), level(a=効く/b=条件しだい/c=当てにならない), text, slug, evidence("meta"|なし)}]
実行: python3 media/dokugaku_hayami.py && python3 media/build.py dokugaku
出力: media/dokugaku-pages.json(extras.pages が /hayami/ を書き出す)、各記事の <!--hayami--> ブロック
"""
import html
import json
import re
from pathlib import Path

E = html.escape
ROOT = Path(__file__).resolve().parent.parent
URL = "https://dokugaku.seadice.win/hayami/"
D = json.loads((ROOT / "media/dokugaku-hayami.json").read_text())["items"]
posts = {p["slug"]: p for p in json.loads((ROOT / "media/dokugaku-posts.json").read_text())}
cfg = json.loads((ROOT / "media/dokugaku.json").read_text())
cats = {c["name"]: c for c in cfg["categories"]}
for x in D:
    assert x["slug"] in posts, x["slug"]
LV = {"a": "効く", "b": "条件しだい", "c": "当てにならない"}
LV_NOTE = {"a": "複数の研究で効果が確認されている", "b": "効く場面と効かない場面がある", "c": "研究で支持されていない、または逆効果"}
order = {"a": 0, "b": 1, "c": 2}
D.sort(key=lambda x: (order[x["level"]], list(cats).index(posts[x["slug"]]["category"])))


def item(x):
    c = cats[posts[x["slug"]]["category"]]
    ev = "・メタ分析あり" if x.get("evidence") == "meta" else ""
    return (f'<li class="hy" id="{x["id"]}" data-c="{c["id"]}" data-l="{x["level"]}">'
            f'<p class="hy-h"><span class="lv lv-{x["level"]}">{LV[x["level"]]}</span><span class="hy-c" style="color:{c["color"]}">{E(c["name"])}{ev}</span></p>'
            f'<h3>{E(x["name"])}</h3><p class="hy-b">よく言われること：{E(x["belief"])}</p><p>{E(x["text"])}</p>'
            f'<a href="/{x["slug"]}/">記事を読む：{E(posts[x["slug"]]["title"])}</a></li>')


used = [c for c in cats.values() if any(posts[x["slug"]]["category"] == c["name"] for x in D)]
chips = '<button type="button" class="hc on" data-f="" aria-pressed="true">すべて</button>' + "".join(
    f'<button type="button" class="hc" data-f="{c["id"]}" aria-pressed="false">{E(c["name"])}</button>' for c in used)
lchips = '<button type="button" class="hl on" data-l="" aria-pressed="true">すべて</button>' + "".join(
    f'<button type="button" class="hl" data-l="{k}" aria-pressed="false">{v}</button>' for k, v in LV.items())
cnt = {k: sum(1 for x in D if x["level"] == k) for k in "abc"}
faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": f'「{x["name"]}」は効果がありますか？',
     "acceptedAnswer": {"@type": "Answer", "text": f'{LV[x["level"]]}。{x["text"]}', "url": URL + "#" + x["id"]}} for x in D]}
faq_json = json.dumps(faq, ensure_ascii=False).replace("</", "<\\/")
body = f"""<p>よく言われる勉強法を、研究で「効く」「条件しだい」「当てにならない」に分けました。気になるやり方を選ぶと、根拠と記事にすぐ進めます。</p>
<script type="application/ld+json">{faq_json}</script>
<p class="note">内訳：効く {cnt["a"]}／条件しだい {cnt["b"]}／当てにならない {cnt["c"]}（全{len(D)}項目）</p>
<ul class="legend"><li><span class="lv lv-a">効く</span>{LV_NOTE["a"]}</li><li><span class="lv lv-b">条件しだい</span>{LV_NOTE["b"]}</li><li><span class="lv lv-c">当てにならない</span>{LV_NOTE["c"]}</li></ul>
<p class="flabel">悩みから</p><div class="fchips">{chips}</div>
<p class="flabel">判定から</p><div class="fchips">{lchips}</div>
<h2>勉強法の一覧</h2>
<p id="cnt" class="note" aria-live="polite"></p>
<ul class="hyl">{"".join(item(x) for x in D)}</ul>
<h2>このページについて</h2>
<p>内容は、独学の科学で公開している記事（それぞれ論文などの出典を確認済み）をもとにしています。多くの研究は大学生や短い課題が対象で、社会人の長い独学にそのまま当てはまるとは限りません。「効く」と判定したやり方も、自分に合うか小さく試して確かめてください。</p>
<script>
(function(){{
var f='',l='',li=[].slice.call(document.querySelectorAll('.hy')),cnt=document.getElementById('cnt');
function each(s,fn){{[].forEach.call(document.querySelectorAll(s),fn)}}
function filt(){{var n=0;li.forEach(function(e){{var ok=(!f||e.dataset.c===f)&&(!l||e.dataset.l===l);e.hidden=!ok;if(ok)n++}});cnt.textContent=n+'件'}}
function grp(sel,key,set){{each(sel,function(b){{b.onclick=function(){{set(b.dataset[key]);each(sel,function(x){{x.classList.toggle('on',x===b);x.setAttribute('aria-pressed',x===b)}});filt()}}}})}}
grp('.hc','f',function(v){{f=v}});grp('.hl','l',function(v){{l=v}});filt();
}})();
</script>"""
css = (".fchips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px}"
       ".hc,.hl{font:inherit;font-size:14px;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:999px;padding:8px 14px;cursor:pointer}"
       ".hc.on,.hl.on{border-color:var(--accent);color:var(--accent)}"
       "button:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"
       ".flabel{font-size:13px!important;color:var(--muted);margin:14px 0 6px!important}"
       ".legend{list-style:none;margin:8px 0 12px!important;padding:0}.legend li{font-size:14px;margin:6px 0}.legend .lv{margin-right:8px}"
       ".hyl{list-style:none;margin:10px 0 0!important;padding:0;display:grid;gap:12px}"
       ".hy{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--border);border-radius:14px;padding:16px 18px;margin:0!important;scroll-margin-top:72px}"
       ".hy[data-l=a]{border-left-color:#7FD6A4}.hy[data-l=b]{border-left-color:#F5C542}.hy[data-l=c]{border-left-color:#F08A8A}.hy:target{box-shadow:0 0 0 2px var(--accent)}"
       ".hy h3{font-size:17px;margin:6px 0 4px}.hy p{font-size:15px;line-height:1.8;margin:6px 0}.hy .hy-b{color:var(--muted);font-size:14px}.hy a{font-size:14px;color:var(--link)}"
       ".hy-h{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:0!important}.hy-c{font-size:12px;font-weight:700}"
       ".lv{display:inline-block;font-size:12px;font-weight:800;border-radius:999px;padding:3px 10px;border:1px solid}"
       ".lv-a{color:#7FD6A4;border-color:#7FD6A4}.lv-b{color:#F5C542;border-color:#F5C542}.lv-c{color:#F08A8A;border-color:#F08A8A}")
page = {"path": "hayami", "title": "勉強法の効く・効かない早見表",
        "seo_title": f"勉強法の効く・効かない早見表｜{len(D)}の勉強法を研究で判定", "date": "2026-10-04",
        "desc": f"思い出す練習、分散学習、蛍光ペン、学習スタイル、ポモドーロ。よく言われる勉強法{len(D)}種類を、研究で「効く」「条件しだい」「当てにならない」に判定した早見表。出典つき。",
        "body": body, "css": css}
# よくある質問の一覧(/faq/)。各記事の FAQPage(確認済みの問答)をカテゴリ別に集める。AI検索で引用されやすい形
qa = []
for cname in cats:
    for p in [p for p in posts.values() if p["category"] == cname]:
        t = (ROOT / f'sites/dokugaku/{p["slug"]}/index.html').read_text()
        for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', t, re.S):
            d = json.loads(m)
            for node in d.get("@graph", [d]):
                if node.get("@type") == "FAQPage":
                    for q in node["mainEntity"]:
                        qa.append((cname, q["name"], q["acceptedAnswer"]["text"], p))
secs = ""
for cname in cats:
    rows = [x for x in qa if x[0] == cname]
    if not rows:
        continue
    secs += f'<h2>{E(cname)}</h2>' + "".join(
        f'<details class="fq"><summary>{E(q)}</summary><p>{E(a)}</p><a href="/{p["slug"]}/">記事を読む：{E(p["title"])}</a></details>' for _, q, a, p in rows)
faq2 = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a, "url": f'https://dokugaku.seadice.win/{p["slug"]}/'}} for _, q, a, p in qa]}
faq_page = {"path": "faq", "title": "独学・勉強法のよくある質問", "seo_title": f"独学・勉強法のよくある質問{len(qa)}問｜研究でわかった答え", "date": page["date"],
            "desc": f"「蛍光ペンは意味ある？」「勉強中の音楽は？」「AIに聞くと身につかない？」など、独学と勉強法のよくある質問{len(qa)}問に、研究でわかったことから答えます。出典つき。",
            "body": f'<p>独学と勉強法のよくある質問に、研究でわかったことから答えます。答えはそれぞれの記事（論文などの出典を確認済み）の内容です。くわしい根拠は各記事で読めます。</p><p><a href="/hayami/" style="color:var(--link);font-weight:700">勉強法の効く・効かない早見表も見る</a></p>'
                    + f'<script type="application/ld+json">{json.dumps(faq2, ensure_ascii=False).replace("</", chr(60) + chr(92) + "/")}</script>' + secs,
            "css": ".fq{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 16px;margin:10px 0}.fq summary{cursor:pointer;font-weight:700;font-size:15px;line-height:1.6}.fq p{font-size:15px;line-height:1.85;margin:10px 0 6px}.fq a{font-size:14px;color:var(--link)}"}
(ROOT / "media/dokugaku-pages.json").write_text(json.dumps([page, faq_page], ensure_ascii=False, indent=2) + "\n")

# 各記事の末尾(出典の直前)に、早見表の該当項目へのリンクを差し込む。再実行しても1つだけになる
BLOCK = re.compile(r"<!--hayami-->.*?<!--/hayami-->\n?", re.S)
n = 0
for x in D:
    f = ROOT / f'sites/dokugaku/{x["slug"]}/index.html'
    t = BLOCK.sub("", f.read_text())
    k = t.find('<div class="sources">')
    if k < 0:
        continue
    blk = (f'<!--hayami--><p style="margin:28px 0;padding:14px 18px;border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:12px;background:var(--card);font-size:15px;line-height:1.8">'
           f'<a href="/hayami/#{x["id"]}" style="color:var(--link);font-weight:700">勉強法の早見表で「{E(x["name"])}」の判定を見る</a><br>'
           f'<span style="font-size:13px;color:var(--muted)">ほかの勉強法も{len(D)}種類、研究で「効く・条件しだい・当てにならない」に分けています。</span></p><!--/hayami-->\n')
    f.write_text(t[:k] + blk + t[k:])
    n += 1
print("ok", len(D), "items,", n, "articles linked")
