#!/usr/bin/env python3
"""ゼロから学ぶ貿易実務（貿易実務を無料で学べる学習サイト）を丸ごと生成する。boueki_pages.py をもとにした学習サイト版。記事エンジン(build.py / /media)の対象外。
使い方: python3 media/boueki_pages.py
 - 講座のレッスンは media/boueki-course.json の chapters[].lessons に1件足す（HTMLを手で編集しない）。
 - 用語は media/boueki-glossary.json に1件足す。slug は姉妹メディア(umbra / ledger)の記事slug。
 - AI検索に引用されやすいよう、各ページの冒頭で「〇〇とは、△△のことです。」と言い切り、
   WebSite / Course / LearningResource / DefinedTermSet / FAQPage / ItemList の JSON-LD と llms.txt を付ける。JS不使用。
 - デザインは教科書型（明るい背景、端末がダークモードなら暗い配色）。メディア用テンプレートは使わない。"""
import base64, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
CFG = json.loads((ROOT / "media/boueki.json").read_text())
COURSE = json.loads((ROOT / "media/boueki-course.json").read_text())
# サイト全体の更新日 = 最新レッスンの日付（レッスンごとの日付は lesson["date"]）
UPDATED = max([l.get("date", "2026-10-01") for c in COURSE["chapters"] for l in c["lessons"]] + [CFG.get("updated", "2026-10-01")])
TERMS = json.loads((ROOT / "media/boueki-glossary.json").read_text())
_gp = ROOT / "media/boueki-guides.json"
GUIDES = json.loads(_gp.read_text()) if _gp.exists() else []  # 独学Q&A(kind=qa)と分野入門(kind=field)
NAME, URL = CFG["name"], CFG["url"]
OUT = ROOT / CFG["path"]
PUBLISHER = {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}
CURL = f"{URL}course/"

ARTICLES = {}  # 姉妹メディアの記事（今は無し）

LESSONS = [(ch, l) for ch in COURSE["chapters"] for l in ch["lessons"]]
N_LESSONS, N_CH = len(LESSONS), len(COURSE["chapters"])

CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#F7F5F0;--paper:#FFFFFF;--text:#1C1E24;--sub:#4A4F5C;--muted:#646A78;--line:#E4DFD5;--accent:#0B6380;--accent-ink:#FFFFFF;--soft:#E3F1F5;--note:#FFF6DA;--ok:#1F7A4D}
@media(prefers-color-scheme:dark){:root{--bg:#111118;--paper:#1A1A24;--text:#ECEBF2;--sub:#C2C0CF;--muted:#A3A0B4;--line:#2D2C3A;--accent:#6CCBE3;--accent-ink:#0E1A20;--soft:#1C2E36;--note:#2B2717;--ok:#6FD3A0}}
html{-webkit-text-size-adjust:100%}body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Hiragino Sans','Noto Sans JP','Helvetica Neue',sans-serif;font-size:17px;line-height:1.9}
a{color:var(--accent)}a:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
header.site{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
header.site .in{max-width:960px;margin:0 auto;padding:10px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.logo{font-weight:800;font-size:17px;color:var(--text);text-decoration:none;letter-spacing:.02em}.logo small{font-size:12px;color:var(--muted);font-weight:600;margin-left:8px;letter-spacing:.08em}
header.site nav{display:flex;gap:4px;flex-wrap:wrap}header.site nav a{font-size:14px;color:var(--sub);text-decoration:none;padding:8px 10px;border-radius:8px}header.site nav a:hover,header.site nav a[aria-current]{background:var(--soft);color:var(--accent)}
main{max-width:760px;margin:0 auto;padding:28px 16px 72px}main.wide{max-width:960px}
.crumb{font-size:13px;color:var(--muted);margin-bottom:14px}.crumb a{color:var(--muted);text-decoration:none}.crumb a:hover{text-decoration:underline}
.kicker{display:inline-block;font-size:13px;font-weight:700;color:var(--accent);background:var(--soft);border-radius:999px;padding:3px 12px;margin-bottom:12px}
h1{font-size:clamp(26px,6vw,36px);line-height:1.35;font-weight:800;letter-spacing:.01em;margin-bottom:10px}
.updated{font-size:13px;color:var(--muted);margin-bottom:22px}
.lead{font-size:18px;color:var(--sub);margin:0 0 28px}
h2{font-size:23px;line-height:1.45;font-weight:800;margin:56px 0 12px;padding-top:6px}h2 .n{display:block;font-size:13px;color:var(--accent);letter-spacing:.12em;margin-bottom:2px}
h3{font-size:18px;font-weight:800;margin:28px 0 8px}
p{margin:14px 0}.answer{font-weight:700;color:var(--text);border-left:4px solid var(--accent);padding:2px 0 2px 14px;margin:10px 0 18px}
.box{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:20px 22px;margin:20px 0}.box h2,.box .bt{font-size:15px;font-weight:800;color:var(--accent);letter-spacing:.06em;margin:0 0 8px;padding:0}
.box ul,.box ol{padding-left:22px}.box li{margin:6px 0}
.box.key{background:var(--soft);border-color:transparent}.box.note{background:var(--note);border-color:transparent;font-size:15px}
.btns{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 32px}.btn{display:inline-block;font-size:16px;font-weight:700;text-decoration:none;border-radius:12px;padding:12px 20px;background:var(--accent);color:var(--accent-ink)}.btn.sub{background:var(--paper);color:var(--accent);border:1px solid var(--line)}
.grid{display:grid;gap:12px;grid-template-columns:1fr}@media(min-width:680px){.grid{grid-template-columns:1fr 1fr}}
.card{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 18px;text-decoration:none;color:var(--text)}a.card:hover{border-color:var(--accent)}
.card b{display:block;font-size:17px;line-height:1.5}.card span{display:block;font-size:14px;color:var(--sub);line-height:1.7;margin-top:4px}.card small{display:block;font-size:12px;font-weight:700;color:var(--accent);letter-spacing:.1em;margin-bottom:4px}
.card.soon{opacity:.75}.card .st{display:inline-block;font-size:12px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:1px 10px;margin-top:8px}
ol.lessons{list-style:none;margin:10px 0 0}ol.lessons li{margin:0;border-top:1px solid var(--line)}ol.lessons a{display:flex;gap:10px;padding:10px 2px;text-decoration:none;color:var(--text);font-size:15px;line-height:1.6}ol.lessons a:hover{color:var(--accent)}ol.lessons .no{flex:0 0 42px;color:var(--muted);font-variant-numeric:tabular-nums}
ol.lessons a[aria-current]{color:var(--accent);font-weight:700}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.chips a{font-size:14px;color:var(--text);text-decoration:none;background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:8px 14px}.chips a:hover{border-color:var(--accent);color:var(--accent)}
table{width:100%;border-collapse:collapse;margin:16px 0;font-size:15px;background:var(--paper)}th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top;line-height:1.7}th{background:var(--soft);font-weight:700}
@media(max-width:640px){table,tbody,tr,td{display:block;width:100%}thead{display:none}tr{border:1px solid var(--line);border-radius:12px;margin:12px 0;padding:6px 0;background:var(--paper)}td{border:0;padding:5px 14px}td::before{content:attr(data-l);display:block;font-size:12px;color:var(--muted)}}
.term{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0}.term .tt{font-size:17px;font-weight:800;line-height:1.5}.term .en{font-size:13px;color:var(--muted);font-weight:600;margin-left:6px}.term p{margin:6px 0 0;font-size:15px;color:var(--sub)}.term .more{display:inline-block;margin-top:8px;font-size:14px}
details{background:var(--paper);border:1px solid var(--line);border-radius:14px;margin:12px 0;padding:0}summary{cursor:pointer;padding:14px 18px;font-weight:700;font-size:16px;line-height:1.6}details>div,details>p{padding:0 18px 16px;font-size:15px;color:var(--sub)}
.quiz ol{padding-left:22px;margin:6px 0 10px}.quiz li{margin:4px 0}.quiz details details{border-style:dashed;margin:10px 0 0}.quiz details details summary{font-size:14px;color:var(--accent);padding:10px 14px}.quiz .ans{color:var(--ok);font-weight:700}
.qz{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0}.qz .qq{font-weight:700;margin:0 0 10px;line-height:1.7}.qz .src-l{font-size:12px;color:var(--muted);font-weight:600;display:block;margin-bottom:2px}
.qz .chs{display:grid;gap:8px}.qz button{font:inherit;font-size:15px;text-align:left;line-height:1.6;color:var(--text);background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px 14px;cursor:pointer}.qz button:hover:not(:disabled){border-color:var(--accent)}.qz button:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.qz button:disabled{cursor:default}.qz button.ok{border:2px solid var(--ok);background:color-mix(in srgb,var(--ok) 12%,var(--paper))}.qz button.ng{border:2px solid #C2410C;background:color-mix(in srgb,#C2410C 10%,var(--paper))}
.qz .res{font-weight:800;margin:10px 0 0}.qz .res.ok{color:var(--ok)}.qz .res.ng{color:#C2410C}.qz details{margin:10px 0 0;border-style:dashed}.qz details summary{font-size:14px;color:var(--accent);padding:10px 14px}.qz details p{padding:0 14px 12px;margin:0;font-size:15px;color:var(--sub)}
.score{font-size:17px;font-weight:800;margin:16px 0 0}.score:empty{display:none}.score ul{font-size:15px;font-weight:400;margin:8px 0 0 20px}
.review{background:var(--soft);border-radius:16px;padding:18px 20px;margin:20px 0}.review .bt{font-size:15px;font-weight:800;color:var(--accent);letter-spacing:.06em;margin:0 0 4px}.review>p{font-size:14px;color:var(--sub);margin:0 0 6px}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:40px 0 0}.pn a{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:12px 16px;text-decoration:none;color:var(--text);font-size:14px;line-height:1.5}.pn a:hover{border-color:var(--accent)}.pn small{display:block;font-size:12px;color:var(--accent);font-weight:700}.pn .nx{text-align:right;grid-column:2}
@media(max-width:520px){.pn{grid-template-columns:1fr}.pn .nx{grid-column:1}}
.final{margin:48px 0 0;background:var(--paper);border:2px solid var(--accent);border-radius:20px;padding:22px 20px 10px}.final h2{margin:0 0 10px;padding:0}.final .fk{font-size:13px;font-weight:800;color:var(--accent);letter-spacing:.12em;margin:0 0 4px}.final details{background:var(--bg)}
.done{margin:24px 0 0;background:var(--soft);border-radius:20px;padding:22px 20px}.done .dt{font-size:20px;font-weight:800;margin:0}.done .dd{font-size:15px;color:var(--sub);margin:6px 0 0}.done details{background:var(--paper)}
.src{margin-top:48px;padding-top:18px;border-top:1px solid var(--line)}.src h2{font-size:15px;margin:0 0 8px;color:var(--muted)}.src li{font-size:13px;color:var(--muted);margin:6px 0 6px 20px;line-height:1.7;word-break:break-word}.src a{color:var(--muted)}
.ex li{margin:6px 0}.ex small{color:var(--muted)}
footer.site{border-top:1px solid var(--line);padding:28px 16px;text-align:center;font-size:13px;color:var(--muted);line-height:2.2}footer.site a{color:var(--muted);margin:0 8px;text-decoration:none}footer.site a:hover{text-decoration:underline}
.hero{padding:20px 0 4px}.hero h1{font-size:clamp(32px,8vw,48px)}.hero .tag{font-size:16px;font-weight:700;color:var(--accent);margin-bottom:6px}
.stats{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:14px;color:var(--muted);margin:-12px 0 28px}.stats b{color:var(--text);font-size:16px}"""


def favicon():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0B6380"/>'
           '<text x="32" y="44" font-size="34" font-family="-apple-system,sans-serif" font-weight="800" text-anchor="middle" fill="#fff">貿</text></svg>')
    return f'<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}">'


FAV = favicon()
CUR = ' aria-current="page"'
NAV = [("/course/", "講座"), ("/glossary/", "用語辞典")]


QUIZ_JS = """document.querySelectorAll('.quiz').forEach(function(z){var qs=z.querySelectorAll('.qz'),n=0,ok=0,miss={};
qs.forEach(function(q){var bs=q.querySelectorAll('button'),a=+q.dataset.a;bs.forEach(function(b,i){b.addEventListener('click',function(){if(q.dataset.done)return;q.dataset.done=1;n++;
var r=q.querySelector('.res');if(i===a){ok++;r.textContent='正解です';r.className='res ok'}else{miss[q.dataset.h]=q.dataset.t;r.textContent='不正解です（正解は '+(a+1)+'）';r.className='res ng'}
bs.forEach(function(x,j){x.disabled=true;if(j===a)x.classList.add('ok');else if(j===i)x.classList.add('ng')});var d=q.querySelector('details');d.open=true;d.querySelector('summary').textContent='解説';
if(n===qs.length){var s=z.querySelector('.score'),k=Object.keys(miss).sort(function(x,y){return miss[x]<miss[y]?-1:1}),h=qs.length+'問中'+ok+'問正解。';
if(!k.length)h+='全問正解です。';else if(z.dataset.mode==='test')h+='次のレッスンを読み直しましょう。<ul>'+k.map(function(u){return '<li><a href="'+u+'">'+miss[u]+'</a></li>'}).join('')+'</ul>';else h+='間違えた問題は、本文を読み直してから次に進みましょう。';s.innerHTML=h}})})})});"""


def quiz_html(items, mode="lesson"):
    """items: [(問題, レッスン番号, レッスンURL)]。タップで採点（JS）。JSなしでも「答えを見る」で答えを確認できる。"""
    out = ""
    for i, (q, no, href) in enumerate(items):
        chs = "".join(f'<button type="button">{j+1}. {E(c)}</button>' for j, c in enumerate(q["choices"]))
        tag = f'<span class="src-l">レッスン{no}から</span>' if mode != "lesson" else ""
        out += (f'<div class="qz" data-a="{q["a"]}" data-h="{href}" data-t="レッスン{no}を読み直す">{tag}<p class="qq">Q{i+1}. {E(q["q"])}</p>'
                f'<div class="chs">{chs}</div><p class="res" aria-live="polite"></p>'
                f'<details><summary>答えを見る</summary><p><span class="ans">正解: {q["a"]+1}. {E(q["choices"][q["a"]])}</span><br>{E(q["exp"])}</p></details></div>')
    return f'<div class="quiz" data-mode="{mode}">{out}<div class="score" aria-live="polite"></div></div>'


def lesson_no(l):
    for ch in COURSE["chapters"]:
        for i, x in enumerate(ch["lessons"]):
            if x["id"] == l["id"]:
                return f'{ch["no"]}-{i+1}'


def complete(ch):
    return ch["lessons"] and len(ch["lessons"]) >= len(ch.get("plan", []))


def test_path(ch):
    return f'course/{ch["id"]}-test/'


def crumbs(trail):
    items = [("HOME", "https://seadice.win/"), (NAME, URL)] + trail
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def write(path, full_title, desc, body, graph, trail=(), og_type="article", current="", wide=False, noindex=False):
    url = f"{URL}{path}" if path else URL
    ld = {"@context": "https://schema.org", "@graph": graph + ([crumbs(list(trail))] if not noindex else [])}
    nav = "".join(f'<a href="{h}"{CUR if h == current else ""}>{E(t)}</a>' for h, t in NAV)
    bc = ""
    if trail:
        parts = ['<a href="https://seadice.win/">HOME</a>', f'<a href="/">{E(NAME)}</a>'] + [f'<a href="{u.replace(URL, "/")}">{E(n)}</a>' for n, u in trail[:-1]] + [E(trail[-1][0])]
        bc = f'<p class="crumb">{" / ".join(parts)}</p>'
    out = f'''<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc, quote=True)}">
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{url}">'}
<meta property="og:title" content="{E(full_title, quote=True)}">
<meta property="og:description" content="{E(desc, quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{E(NAME, quote=True)}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
{'' if noindex else '<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">'}
<meta name="color-scheme" content="light dark">
{FAV}
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
<style>{CSS}</style>
</head>
<body>
<header class="site"><div class="in"><a class="logo" href="/">{E(NAME)}<small>貿易実務を無料で学ぶ</small></a><nav aria-label="サイト内">{nav}</nav></div></header>
<main{' class="wide"' if wide else ''}>
{bc}{body}
</main>
{'<script>' + QUIZ_JS + '</script>' if 'class="quiz"' in body else ''}
<footer class="site"><p><a href="/course/">ゼロから学ぶ貿易実務入門</a><a href="/glossary/">貿易用語辞典</a><br><a href="/about/">このサイトについて</a><a href="/sources/">出典と検証の方法</a><a href="/disclaimer/">免責事項</a><a href="mailto:hi@seadice.win">お問い合わせ</a><br><a href="https://seadice.win/">運営: SEADICE</a></p></footer>
</body>
</html>
'''
    d = OUT / path if path else OUT
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(out)
    return url


def faq_html(faq):
    return "".join(f"<details open><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def body_len(l):
    return sum(len(x) for sec in l["sections"] for x in sec["paras"])


def read_min(l):
    """日本語の黙読はおよそ毎分500字。要点・キーワード・確認問題の時間も足す。"""
    return max(3, round(body_len(l) / 500) + 2)


def check():
    """公開前の機械チェック。1つでも落ちたら終了コード1（ルーティンはこれが通らないと公開しない）。"""
    errs, ids = [], set()
    for ch in COURSE["chapters"]:
        for l in ch["lessons"]:
            tag = f'{ch["no"]}:{l.get("id")}'
            if l["id"] in ids: errs.append(f"{tag} id重複")
            ids.add(l["id"])
            for k in ("date", "title", "short", "description", "goals", "summary", "sections", "terms", "quiz", "sources"):
                if not l.get(k): errs.append(f"{tag} {k}が空")
            if body_len(l) < 1000: errs.append(f"{tag} 本文{body_len(l)}字（1000字以上必要）")
            if len(l.get("sources", [])) < 2: errs.append(f"{tag} 出典が2件未満")
            if "とは" not in (l.get("summary") or [""])[0]: errs.append(f"{tag} 要点1文目が「〇〇とは」の定義になっていない")
            for i, q in enumerate(l.get("quiz", [])):
                if len(q["choices"]) != 3 or not 0 <= q["a"] < 3: errs.append(f"{tag} 確認問題{i+1}の形式")
            for e in l.get("examples", []):
                if e["slug"] not in ARTICLES: errs.append(f'{tag} examplesの記事slugが存在しない: {e["slug"]}')
            if "{{" in json.dumps(l, ensure_ascii=False): errs.append(f"{tag} プレースホルダが残っている")
    gids = set()
    for g in GUIDES:
        tag = f'guide {g.get("id")}'
        if g["id"] in gids: errs.append(f"{tag} id重複")
        gids.add(g["id"])
        if g.get("kind") not in ("qa", "field"): errs.append(f"{tag} kindはqaかfield")
        for k in ("title", "lead", "sections", "sources", "date"):
            if not g.get(k): errs.append(f"{tag} {k}が空")
        if sum(len(x) for sec in g.get("sections", []) for x in sec["paras"]) < 800: errs.append(f"{tag} 本文800字未満")
        if g.get("kind") == "field" and not g.get("chapters"): errs.append(f"{tag} 分野ページにchaptersが無い")
    for t in TERMS:
        if t.get("detail") and not rich(t): errs.append(f'用語 {t["id"]} は detail があるが、個別ページの条件（detail400字以上・sources・faq）を満たしていない')
        if "とは" not in t["def"].split("。")[0]: errs.append(f'用語 {t["id"]} の定義の1文目が「〇〇とは」になっていない')
    return errs


def lurl(l):
    return f"{CURL}{l['id']}/"


# ---------------- 講座 ----------------
def course_ld():
    return {"@type": "Course", "@id": CURL + "#course", "name": COURSE["title"], "description": COURSE["desc"], "url": CURL, "inLanguage": "ja",
            "provider": PUBLISHER, "isAccessibleForFree": True, "educationalLevel": "初級",
            "offers": {"@type": "Offer", "price": 0, "priceCurrency": "JPY", "category": "Free"},
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Online", "courseWorkload": f"PT{max(N_LESSONS, 1) * 10}M"},
            "syllabusSections": [{"@type": "Syllabus", "name": f'第{c["no"]}章 {c["title"]}', "description": c["desc"]} for c in COURSE["chapters"]]}


def chapter_list(current=None):
    out = ""
    for c in COURSE["chapters"]:
        if c["lessons"]:
            items = "".join(f'<li><a href="/course/{l["id"]}/"{CUR if current == l["id"] else ""}><span class="no">{c["no"]}-{i+1}</span>{E(l["short"])}</a></li>' for i, l in enumerate(c["lessons"]))
            out += f'<div class="card" id="ch{c["no"]}"><small>第{c["no"]}章</small><b>{E(c["title"])}</b><span>{E(c["desc"])}</span><ol class="lessons">{items}</ol>' + (f'<p style="margin:10px 0 0;font-size:14px;font-weight:700"><a href="/{test_path(c)}">第{c["no"]}章のまとめテスト（{sum(len(x["quiz"]) for x in c["lessons"])}問）</a></p>' if complete(c) else '') + '</div>'
        else:
            out += f'<div class="card soon" id="ch{c["no"]}"><small>第{c["no"]}章</small><b>{E(c["title"])}</b><span>{E(c["desc"])}</span><span class="st">準備中</span></div>'
    return out


def course_index():
    first = LESSONS[0][1] if LESSONS else None
    body = f'''<span class="kicker">無料の貿易実務講座</span>
<h1>{E(COURSE["title"])}</h1>
<p class="updated">全{N_CH}章 ・ 公開中 {N_LESSONS}レッスン ・ 更新日 {UPDATED}</p>
<p class="lead">{E(COURSE["title"])}は、貿易の仕事の全体像をゼロから学べる無料のオンライン講座です。貿易実務検定C級の出題範囲をカバーしています。登録は不要で、1レッスン10分ほどで読めます。</p>
{f'<div class="btns"><a class="btn" href="/course/{first["id"]}/">第1章から学びはじめる</a><a class="btn sub" href="/glossary/">用語辞典を見る</a></div>' if first else ''}
<div class="box key"><p class="bt">この講座の特徴</p><ul>
<li>1レッスンは「前回の復習 → 学習目標 → 要点 → 本文 → キーワード（日本語・英語） → 確認クイズ」の順に進みます。読んだ直後にクイズで思い出し、章の最後のまとめテストで仕上げます。</li>
<li>本文は、税関・ジェトロ・国際商業会議所（ICC）などの一次情報をもとに書いています。各レッスンの末尾に出典があります。</li>
<li>確認問題はすべてオリジナルです。過去問や市販の問題集の問題は使っていません。最後の章で模擬試験に挑戦できます。</li>
</ul></div>
<h2><span class="n">CONTENTS</span>講座の目次</h2>
<p class="answer">貿易とは何か（第1章）から始め、インコタームズ、代金決済、運送、保険、通関、貿易書類、貿易英語まで、全{N_CH}章で学び、最後に模擬試験で仕上げます。</p>
<div class="grid">{chapter_list()}</div>'''
    graph = [course_ld(), {"@type": "ItemList", "name": f'{COURSE["title"]}のレッスン一覧', "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": l["title"], "url": lurl(l)} for i, (_, l) in enumerate(LESSONS)]}]
    return write("course/", f'{COURSE["title"]}（無料の貿易実務講座）| {NAME}',
                 f'{COURSE["desc"]}全{N_CH}章。登録不要。', body, graph, trail=[("講座", CURL)], current="/course/", wide=True)


def lesson(ci, li):
    ch = COURSE["chapters"][ci]
    l = ch["lessons"][li]
    idx = next(i for i, (_, x) in enumerate(LESSONS) if x["id"] == l["id"])
    prev_l = LESSONS[idx - 1][1] if idx > 0 else None
    next_l = LESSONS[idx + 1][1] if idx < len(LESSONS) - 1 else None
    no = f'{ch["no"]}-{li+1}'
    secs = "".join(f'<h2><span class="n">{i+1:02d}</span>{E(s["h"])}</h2><p class="answer">{E(s["answer"])}</p>' + "".join(f"<p>{E(p)}</p>" for p in s["paras"]) for i, s in enumerate(l["sections"]))
    terms = "".join(f'<div class="term"><span class="tt">{E(t["ja"])}</span><span class="en">{E(t["en"])}</span><p>{E(t["def"])}</p></div>' for t in l["terms"])
    exs = "".join(f'<li><a href="{ARTICLES[e["slug"]][0]}">{E(e["text"])}</a> <small>（{E(ARTICLES[e["slug"]][2])}）</small></li>' for e in l.get("examples", []) if e["slug"] in ARTICLES)
    quiz = quiz_html([(q, no, lurl(l).replace(URL, "/")) for q in l["quiz"]])
    # 前回の復習: 直前のレッスンと、3つ前のレッスンから1問ずつ（間隔をあけて思い出すと定着しやすい）
    rv = [(LESSONS[k][1], LESSONS[k][1]["quiz"][idx % len(LESSONS[k][1]["quiz"])]) for k in (idx - 1, idx - 3) if k >= 0]
    review = (f'<div class="review"><p class="bt">前回の復習（1分）</p><p>本文に入る前に、前のレッスンの内容を思い出してみましょう。</p>'
              + quiz_html([(q, lesson_no(x), lurl(x).replace(URL, "/")) for x, q in rv], mode="review") + '</div>') if rv else ""
    last = li == len(ch["lessons"]) - 1 and complete(ch)
    srcs = "".join(f'<li><a href="{s["url"]}" target="_blank" rel="noopener">{E(s["text"])}</a></li>' for s in l["sources"])
    chlist = "".join(f'<li><a href="/course/{x["id"]}/"{CUR if x["id"] == l["id"] else ""}><span class="no">{ch["no"]}-{j+1}</span>{E(x["short"])}</a></li>' for j, x in enumerate(ch["lessons"]))
    body = f'''<span class="kicker">第{ch["no"]}章 {E(ch["title"])} ・ レッスン{no}</span>
<h1>{E(l["title"])}</h1>
<p class="updated">読む時間の目安: {read_min(l)}分 ・ 公開日 {l.get("date", UPDATED)}</p>
{review}
<div class="box"><p class="bt">このレッスンの学習目標</p><ul>{"".join(f"<li>{E(g)}</li>" for g in l["goals"])}</ul></div>
<div class="box key"><p class="bt">要点</p><ol>{"".join(f"<li>{E(s)}</li>" for s in l["summary"])}</ol></div>
{secs}
<h2><span class="n">KEYWORDS</span>キーワード（日本語・英語）</h2>
<p class="answer">このレッスンで覚えておきたい用語です。貿易の書類や契約は英語が中心なので、英語名も一緒に覚えましょう。</p>
{terms}
{f'<h2><span class="n">EXAMPLES</span>身近な例で深める</h2><p class="answer">このレッスンの内容を、日常の疑問にあてはめた研究解説記事です。</p><ul class="ex">{exs}</ul>' if exs else ''}
<div class="src"><h2>出典</h2><ol>{srcs}</ol></div>
<section class="final" aria-labelledby="quiz-h">
<p class="fk">LESSON {no} の仕上げ</p>
<h2 id="quiz-h">確認クイズ（全{len(l["quiz"])}問）</h2>
<p class="answer">読んだ直後に思い出すと、記憶に残りやすくなります。選択肢をタップして答えてください。</p>
<div class="quiz">{quiz}</div>
</section>
<div class="done"><p class="dt">レッスン{no}はここまでです</p><p class="dd">クイズで迷った問題があれば、その見出しの本文を読み直してから次に進みましょう。</p>
<div class="btns" style="margin:14px 0 0">{f'<a class="btn" href="/{test_path(ch)}">第{ch["no"]}章のまとめテストに挑戦</a>' if last else ''}{f'<a class="btn{" sub" if last else ""}" href="/course/{next_l["id"]}/">次のレッスン: {E(next_l["short"])}</a>' if next_l else '<a class="btn" href="/course/">講座の目次へ（次の章は準備中です）</a>'}{f'<a class="btn sub" href="/course/{prev_l["id"]}/">前のレッスン</a>' if prev_l else ''}</div>
<details style="margin-top:16px"><summary>第{ch["no"]}章 {E(ch["title"])} のレッスン一覧</summary><div><ol class="lessons">{chlist}</ol><p style="margin:10px 0 0;font-size:14px"><a href="/course/">講座の目次（全{N_CH}章）へ</a></p></div></details>
</div>'''
    url = lurl(l)
    graph = [
        {"@type": ["Article", "LearningResource"], "headline": l["title"], "description": l["description"], "url": url, "inLanguage": "ja",
         "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "datePublished": l.get("date", UPDATED), "dateModified": l.get("modified", l.get("date", UPDATED)),
         "author": {"@type": "Organization", "name": f"{NAME}編集部"}, "publisher": PUBLISHER, "isAccessibleForFree": True,
         "learningResourceType": "Lesson", "educationalLevel": "初級", "timeRequired": f"PT{read_min(l)}M",
         "teaches": [t["ja"] for t in l["terms"]], "isPartOf": {"@id": CURL + "#course"},
         "position": idx + 1, "citation": [s["url"] for s in l["sources"]]},
        {"@type": "DefinedTermSet", "name": f'{l["short"]}のキーワード', "hasDefinedTerm": [
            {"@type": "DefinedTerm", "name": t["ja"], "alternateName": t["en"], "description": t["def"]} for t in l["terms"]]},
        faq_ld([(q["q"], f'{q["choices"][q["a"]]}。{q["exp"]}') for q in l["quiz"]]),
    ]
    return write(f'course/{l["id"]}/', f'{l["title"]}｜貿易実務入門 {no} | {NAME}', l["description"], body, graph,
                 trail=[("講座", CURL), (f'第{ch["no"]}章 {ch["title"]}', CURL), (l["short"], url)], current="/course/")


def chapter_test(ch):
    """章のまとめテスト。各レッスンの問題を、レッスンが交互になるように並べる。"""
    ls = ch["lessons"]
    items = [(l["quiz"][k], f'{ch["no"]}-{i+1}', lurl(l).replace(URL, "/")) for k in range(max(len(l["quiz"]) for l in ls)) for i, l in enumerate(ls) if k < len(l["quiz"])]
    url = f"{URL}{test_path(ch)}"
    title = f'第{ch["no"]}章 {ch["title"]} まとめテスト'
    nxt = next((c for c in COURSE["chapters"] if c["no"] == ch["no"] + 1 and c["lessons"]), None)
    body = f'''<span class="kicker">第{ch["no"]}章のまとめ</span>
<h1>{E(title)}（全{len(items)}問）</h1>
<p class="updated">対象: レッスン{ch["no"]}-1〜{ch["no"]}-{len(ls)} ・ 目安 {max(3, len(items) // 2)}分</p>
<p class="lead">第{ch["no"]}章「{E(ch["title"])}」で学んだ内容を、まとめて確かめるテストです。レッスンが混ざった順番で出題します。最後に、間違えた問題のレッスンへのリンクが出ます。</p>
{quiz_html(items, mode="test")}
<div class="done"><p class="dt">第{ch["no"]}章はここまでです</p><p class="dd">間違えた問題は、表示されたレッスンを読み直してから、もう一度このテストに挑戦しましょう。</p>
<div class="btns" style="margin:14px 0 0">{f'<a class="btn" href="/course/{nxt["lessons"][0]["id"]}/">第{nxt["no"]}章へ進む: {E(nxt["title"])}</a>' if nxt else '<a class="btn" href="/course/">講座の目次へ</a>'}<a class="btn sub" href="/course/#ch{ch["no"]}">第{ch["no"]}章のレッスン一覧</a></div></div>'''
    graph = [{"@type": "Quiz", "name": title, "url": url, "inLanguage": "ja", "educationalLevel": "初級", "isAccessibleForFree": True,
              "about": ch["title"], "isPartOf": {"@id": CURL + "#course"}, "publisher": PUBLISHER,
              "hasPart": [{"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["choices"][q["a"]]}} for q, _, _ in items]}]
    return write(test_path(ch), f'{title}（全{len(items)}問）| {NAME}',
                 f'第{ch["no"]}章「{ch["title"]}」の確認問題{len(items)}問。タップで答えて、間違えた問題のレッスンを読み直せます。無料・登録不要。', body, graph,
                 trail=[("講座", CURL), (f'第{ch["no"]}章 {ch["title"]}', CURL), ("まとめテスト", url)], current="/course/")


# ---------------- 用語辞典 ----------------
def glossary():
    fields = list(dict.fromkeys(t["field"] for t in TERMS))
    url = f"{URL}glossary/"
    body = (f'<span class="kicker">全{len(TERMS)}語</span><h1>貿易用語辞典</h1><p class="updated">更新日 {UPDATED}</p>'
            f'<p class="lead">貿易用語辞典は、貿易実務でよく使う用語を、一文の定義でまとめたページです。英語名も一緒に載せています。</p>'
            '<div class="chips">' + "".join(f'<a href="#f{i}">{E(f)}</a>' for i, f in enumerate(fields)) + '</div>')
    for i, f in enumerate(fields):
        body += f'<h2 id="f{i}"><span class="n">{i+1:02d}</span>{E(f)}の用語</h2>'
        for t in (t for t in TERMS if t["field"] == f):
            a = ARTICLES.get(t.get("slug"))
            more = f'<a class="more" href="{a[0]}">解説記事: {E(a[1])}（{E(a[2])}）</a>' if a else ""
            name = f'<a href="/glossary/{t["id"]}/">{E(t["term"])}</a>' if rich(t) else E(t["term"])
            body += f'<div class="term" id="{t["id"]}"><span class="tt">{name}</span><span class="en">{E(t["en"])}</span><p>{E(t["def"])}</p>{more}</div>'
    body += f'<div class="box key" style="margin-top:36px"><p class="bt">貿易実務を基礎から学ぶなら</p><p style="margin:0">用語の背景にある貿易の流れは、無料講座「<a href="/course/">{E(COURSE["title"])}</a>」で順番に学べます。</p></div>'
    graph = [{"@type": "DefinedTermSet", "@id": url, "name": "貿易用語辞典", "url": url, "inLanguage": "ja", "dateModified": UPDATED, "publisher": PUBLISHER,
              "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": f'{url}#{t["id"]}', "name": t["term"], "alternateName": t["en"],
                                  "description": t["def"], "url": f'{url}{t["id"]}/' if rich(t) else f'{url}#{t["id"]}', "inDefinedTermSet": url} for t in TERMS]}]
    return write("glossary/", f"貿易用語辞典（{len(TERMS)}語をやさしく解説）| {NAME}",
                 f"通関、保税地域、インコタームズなど、貿易実務でよく使う用語{len(TERMS)}語を一文の定義と英語名でやさしく解説。",
                 body, graph, trail=[("貿易用語辞典", url)], current="/glossary/")


def rich(t):
    """個別ページを出せるだけの中身がある用語か（薄いページは作らない）。"""
    return len("".join(t.get("detail", []))) >= 400 and t.get("sources") and t.get("faq")


def term_lessons(t):
    """この用語をキーワードに含むレッスン（講座で詳しく学べる場所）。"""
    key = t["term"].split("（")[0]
    return [(ch, l) for ch, l in LESSONS if any(key in k["ja"] or k["ja"] in key for k in l["terms"])]


def term_page(t):
    url = f'{URL}glossary/{t["id"]}/'
    key = t["term"].split("（")[0]
    a = ARTICLES.get(t.get("slug"))
    ls = term_lessons(t)
    rel = [x for x in TERMS if x["field"] == t["field"] and x["id"] != t["id"]][:6]
    faq = [(q["q"], q["a"]) for q in t["faq"]]
    body = f'''<span class="kicker">{E(t["field"])}</span>
<h1>{E(key)}とは</h1>
<p class="updated">英語: {E(t["en"])} ・ 更新日 {t.get("date", UPDATED)}</p>
<p class="lead">{E(t["def"])}</p>
<h2><span class="n">01</span>{E(key)}をくわしく</h2>
{"".join(f"<p>{E(x)}</p>" for x in t["detail"])}
{f'<h2><span class="n">02</span>身近な例</h2><p class="answer">{E(t["example"])}</p>' if t.get("example") else ""}
{f'<h2><span class="n">03</span>講座で学ぶ</h2><p class="answer">{E(key)}は、無料講座「{E(COURSE["title"])}」の次のレッスンで詳しく学べます。</p><ol class="lessons">' + "".join(f'<li><a href="/course/{l["id"]}/"><span class="no">第{ch["no"]}章</span>{E(l["title"])}</a></li>' for ch, l in ls) + "</ol>" if ls else ""}
<h2><span class="n">FAQ</span>よくある質問</h2>
{faq_html(faq)}
{'<h2><span class="n">RELATED</span>同じ分野の用語</h2><div class="chips">' + "".join(f'<a href="/glossary/{x["id"]}/">{E(x["term"])}</a>' if rich(x) else f'<a href="/glossary/#{x["id"]}">{E(x["term"])}</a>' for x in rel) + "</div>" if rel else ""}
<div class="src"><h2>出典</h2><ol>{"".join(f'<li><a href="{x["url"]}" target="_blank" rel="noopener">{E(x["text"])}</a></li>' for x in t["sources"])}</ol></div>
<p style="margin-top:28px"><a href="/glossary/">貿易用語辞典の一覧へ（{len(TERMS)}語）</a></p>'''
    graph = [{"@type": "DefinedTerm", "@id": url, "name": key, "alternateName": t["en"], "description": t["def"], "url": url,
              "inDefinedTermSet": {"@type": "DefinedTermSet", "name": "貿易用語辞典", "url": f"{URL}glossary/"}},
             {"@type": "Article", "headline": f"{key}とは", "description": t["def"], "url": url, "inLanguage": "ja",
              "datePublished": t.get("date", UPDATED), "dateModified": t.get("date", UPDATED), "mainEntityOfPage": {"@type": "WebPage", "@id": url},
              "author": {"@type": "Organization", "name": f"{NAME}編集部"}, "publisher": PUBLISHER, "citation": [x["url"] for x in t["sources"]]},
             faq_ld(faq)]
    return write(f'glossary/{t["id"]}/', f'{key}とは？意味と例をやさしく解説 | {NAME}', t["def"][:120], body, graph,
                 trail=[("貿易用語辞典", f"{URL}glossary/"), (f"{key}とは", url)], current="/glossary/")


# ---------------- トップ ----------------
def home():
    pick = ["customs-clearance", "incoterms", "bonded-area", "customs-broker", "export", "import"]
    tmap = {t["id"]: t for t in TERMS}
    chips = "".join(f'<a href="/glossary/#{i}">{E(tmap[i]["term"])}</a>' for i in pick if i in tmap)
    first = LESSONS[0][1] if LESSONS else None
    body = f'''<div class="hero"><p class="tag">{E(CFG["tagline"])}</p><h1>{E(NAME)}</h1></div>
<p class="lead">{E(CFG["lead"])}</p>
<p class="stats"><span><b>{N_CH}</b>章の無料講座</span><span><b>{N_LESSONS}</b>レッスン公開中</span><span><b>{len(TERMS)}</b>語の用語辞典</span><span>登録不要</span></p>
<div class="btns">{f'<a class="btn" href="/course/{first["id"]}/">講座を第1章から始める</a>' if first else ''}<a class="btn sub" href="/glossary/">貿易用語辞典を見る</a></div>
<h2><span class="n">01</span>無料講座「{E(COURSE["title"])}」</h2>
<p class="answer">貿易の流れから、インコタームズ、代金決済、運送、保険、通関、貿易書類、貿易英語までを順番に学べる全{N_CH}章の講座です。貿易実務検定C級の出題範囲をカバーしています。</p>
<div class="grid">{chapter_list()}</div>
<p style="margin-top:14px"><a href="/course/">講座の目次をすべて見る</a></p>
<h2><span class="n">02</span>貿易用語辞典</h2>
<p class="answer">貿易実務でよく使う用語を、一文の定義と英語名でまとめています。はじめての人は次の用語から。</p>
<div class="chips">{chips}</div>
<p><a href="/glossary/">用語辞典をすべて見る（{len(TERMS)}語）</a></p>
<h2><span class="n">03</span>よくある質問</h2>
{faq_html(CFG["faq"])}'''
    graph = [
        {"@type": "WebSite", "@id": URL + "#website", "name": NAME, "url": URL, "description": CFG["description"], "inLanguage": "ja", "publisher": PUBLISHER},
        {"@type": "WebPage", "name": NAME, "url": URL, "description": CFG["description"], "isPartOf": {"@id": URL + "#website"}, "dateModified": UPDATED, "publisher": PUBLISHER},
        course_ld(), faq_ld(CFG["faq"]),
    ]
    return write("", f'{NAME} | {CFG["titleSuffix"]}', CFG["description"], body, graph, og_type="website", wide=True)


# ---------------- 信頼ページ・その他 ----------------
TRUST = {
    "about": ("このサイトについて", f"{NAME}の運営者と、講座・用語辞典の作り方を説明します。", [
        ("運営", [f"{NAME}は、アプリスタジオ SEADICE（シーダイス）が運営する、貿易実務を無料で学べる学習サイトです。登録や料金は必要ありません。"]),
        ("目的", ["貿易の仕事に就いた人や、貿易実務検定を目指す人が、費用をかけずに貿易実務の全体像を順番に学べるようにすることです。"]),
        ("作り方", ["講座と用語辞典は、AI（Claude）が税関・ジェトロ・国際商業会議所（ICC）などの一次情報を調べ、内容を確認したうえで、日本語で独自に書いています。特定の教科書の翻訳ではありません。確認問題・模擬試験はすべてオリジナルで、過去問や市販の問題集の問題は使っていません。",
                  "各レッスンの末尾に出典を載せています。確認できなかった内容は書きません。"]),
        ("お問い合わせ", ['誤りのご指摘やご意見は <a href="mailto:hi@seadice.win">hi@seadice.win</a> までお送りください。返信が必要な場合はその旨をお書きください。'])]),
    "sources": ("出典と検証の方法", f"{NAME}で使う出典の基準と、内容の確認方法を説明します。", [
        ("使う出典", ["税関・財務省・経済産業省などの公的機関、ジェトロ、国際商業会議所（ICC）などの一次情報を使います。", "個人のブログや、出典の示されていない情報は使いません。"]),
        ("確認の方法", ["書く内容が出典に書かれていることを、公式のページを開いて1件ずつ確認します。確認できなかった数値や主張は削除します。", "通関や規制などの制度は改正されることがあります。実際の手続の前には、税関や所管省庁の最新情報を確認してください。"]),
        ("訂正", ["誤りが見つかった場合は確認のうえ修正し、ページの更新日を新しくします。"])]),
    "disclaimer": ("免責事項", f"{NAME}の利用にあたっての注意事項です。", [
        ("情報の性質", [f"{NAME}の内容は、貿易実務の一般的な知識の提供であり、個別の取引や手続についての助言ではありません。"]),
        ("専門家への相談", ["実際の取引や通関手続については、税関の相談窓口、通関業者、ジェトロの貿易投資相談などの専門家に確認してください。"]),
        ("責任の範囲", ["内容には正確を期していますが、完全性を保証するものではありません。内容を参考にした行動の結果について、当サイトは責任を負いません。"])]),
}


def trust_pages():
    urls = []
    for slug, (title, desc, secs) in TRUST.items():
        body = f'<h1>{E(title)}</h1><p class="updated">更新日 {UPDATED}</p>' + "".join(
            f'<h2><span class="n">{i+1:02d}</span>{E(h)}</h2>' + "".join(f"<p>{p}</p>" for p in ps) for i, (h, ps) in enumerate(secs))
        url = f"{URL}{slug}/"
        graph = [{"@type": "AboutPage" if slug == "about" else "WebPage", "name": title, "url": url, "inLanguage": "ja",
                  "isPartOf": {"@type": "WebSite", "name": NAME, "url": URL}, "publisher": PUBLISHER, "dateModified": UPDATED}]
        urls.append(write(f"{slug}/", f"{title} | {NAME}", desc, body, graph, trail=[(title, url)]))
    return urls


def extras(urls):
    from seo import AI_BOTS, INDEXNOW_KEY
    bots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in AI_BOTS)
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\n{bots}Sitemap: {URL}sitemap.xml\n# AI向けの案内: {URL}llms.txt\n")
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    sm = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{UPDATED}</lastmod>\n  </url>\n" for u in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    lines = [f"# {NAME}", "", f"> {CFG['description']}", "",
             f"{NAME}はSEADICE(https://seadice.win/)が運営する、貿易実務を無料で学べる学習サイトです。登録不要・無料。",
             f"貿易実務検定C級の範囲をカバーする無料講座「{COURSE['title']}」（全{N_CH}章）と、貿易用語辞典（{len(TERMS)}語）を掲載しています。",
             "本文は税関・ジェトロ・ICCなどの一次情報をもとに日本語で独自に書いており、各ページに出典があります。", "",
             "## 主要ページ", "", f"- トップ: {URL}", f"- 無料講座「{COURSE['title']}」: {CURL}",
             f"- 貿易用語辞典: {URL}glossary/",
             f"- このサイトについて: {URL}about/", f"- 出典と検証の方法: {URL}sources/", "",
             "## 講座の目次", ""]
    for c in COURSE["chapters"]:
        lines.append(f'- 第{c["no"]}章 {c["title"]}: {c["desc"]}' + ("" if c["lessons"] else "（準備中）"))
        lines += [f'  - {c["no"]}-{i+1} {l["title"]}: {lurl(l)}' for i, l in enumerate(c["lessons"])]
    lines += ["", "## 運営", "", "- SEADICE: https://seadice.win/", ""]
    (OUT / "llms.txt").write_text("\n".join(lines))
    body = ('<h1>ページが見つかりません</h1><p class="lead">お探しのページは移動したか、削除された可能性があります。</p>'
            f'<div class="btns"><a class="btn" href="/">{E(NAME)}のトップへ</a><a class="btn sub" href="/course/">講座の目次</a><a class="btn sub" href="/glossary/">用語辞典</a></div>')
    write("_404/", f"ページが見つかりません | {NAME}", "ページが見つかりません。", body, [], noindex=True)
    (OUT / "_404/index.html").rename(OUT / "404.html")
    (OUT / "_404").rmdir()


if __name__ == "__main__":
    import sys
    if "--check" in sys.argv:
        errs = check()
        print("\n".join(errs) if errs else f"check ok ({N_LESSONS} lessons, {len(TERMS)} terms)")
        sys.exit(1 if errs else 0)
    OUT.mkdir(parents=True, exist_ok=True)
    urls = [home(), course_index()]
    for ci, ch in enumerate(COURSE["chapters"]):
        for li in range(len(ch["lessons"])):
            urls.append(lesson(ci, li))
        if complete(ch):
            urls.append(chapter_test(ch))
    urls += [glossary()] + [term_page(t) for t in TERMS if rich(t)]
    urls += trust_pages()
    extras(urls)
    print(f"built {CFG['path']} ({N_LESSONS} lessons, {len(TERMS)} terms, {len(urls)} pages)")
