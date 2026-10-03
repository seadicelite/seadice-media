#!/usr/bin/env python3
"""日常の心理学（心理学を無料で独学できるサイト）を丸ごと生成する。記事エンジン(build.py / /media)の対象外。
使い方: python3 media/shinri_pages.py
 - 講座のレッスンは media/shinri-course.json の chapters[].lessons に1件足す（HTMLを手で編集しない）。
 - 用語は media/shinri-glossary.json に1件足す。slug は姉妹メディア(umbra / ledger)の記事slug。
 - AI検索に引用されやすいよう、各ページの冒頭で「〇〇とは、△△のことです。」と言い切り、
   WebSite / Course / LearningResource / DefinedTermSet / FAQPage / ItemList の JSON-LD と llms.txt を付ける。JS不使用。
 - デザインは教科書型（明るい背景、端末がダークモードなら暗い配色）。メディア用テンプレートは使わない。"""
import base64, html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
CFG = json.loads((ROOT / "media/shinri.json").read_text())
COURSE = json.loads((ROOT / "media/shinri-course.json").read_text())
# サイト全体の更新日 = 最新レッスンの日付（レッスンごとの日付は lesson["date"]）
UPDATED = max([l.get("date", "2026-10-01") for c in COURSE["chapters"] for l in c["lessons"]] + [CFG.get("updated", "2026-10-01")])
TERMS = json.loads((ROOT / "media/shinri-glossary.json").read_text())
_gp = ROOT / "media/shinri-guides.json"
GUIDES = json.loads(_gp.read_text()) if _gp.exists() else []  # 独学Q&A(kind=qa)と分野入門(kind=field)
NAME, URL = CFG["name"], CFG["url"]
OUT = ROOT / CFG["path"]
PUBLISHER = {"@type": "Organization", "name": "SEADICE", "url": "https://seadice.win"}
CURL = f"{URL}course/"

# 姉妹メディア（詳しい研究解説の記事はこちらにある）
SISTERS = [json.loads((ROOT / f"media/{s}.json").read_text()) for s in ("umbra", "ledger")]
RESEARCH = json.loads((ROOT / "media/research.json").read_text())
ARTICLES = {}  # 記事slug -> (url, title, メディア名)
for m in SISTERS:
    for p in json.loads((ROOT / f'media/{m["slug"]}-posts.json').read_text()):
        ARTICLES[p["slug"]] = (f'{m["url"]}{p["slug"]}/', p["title"], m["name"])

LESSONS = [(ch, l) for ch in COURSE["chapters"] for l in ch["lessons"]]
N_LESSONS, N_CH = len(LESSONS), len(COURSE["chapters"])

CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#F7F5F0;--paper:#FFFFFF;--text:#1C1E24;--sub:#4A4F5C;--muted:#646A78;--line:#E4DFD5;--accent:#4F46C8;--accent-ink:#FFFFFF;--soft:#EEECFB;--note:#FFF6DA;--ok:#1F7A4D}
@media(prefers-color-scheme:dark){:root{--bg:#111118;--paper:#1A1A24;--text:#ECEBF2;--sub:#C2C0CF;--muted:#A3A0B4;--line:#2D2C3A;--accent:#A9A2FF;--accent-ink:#14131C;--soft:#24223A;--note:#2B2717;--ok:#6FD3A0}}
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
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#4F46C8"/>'
           '<text x="32" y="44" font-size="34" font-family="-apple-system,sans-serif" font-weight="800" text-anchor="middle" fill="#fff">心</text></svg>')
    return f'<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}">'


FAV = favicon()
CUR = ' aria-current="page"'
NAV = [("/course/", "講座"), ("/guide/", "学び方"), ("/glossary/", "用語辞典")]


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
<header class="site"><div class="in"><a class="logo" href="/">{E(NAME)}<small>心理学を無料で独学</small></a><nav aria-label="サイト内">{nav}</nav></div></header>
<main{' class="wide"' if wide else ''}>
{bc}{body}
</main>
<footer class="site"><p><a href="/course/">ゼロから学ぶ心理学入門</a><a href="/guide/">心理学の学び方</a><a href="/glossary/">心理学用語辞典</a><br><a href="/about/">このサイトについて</a><a href="/sources/">出典と検証の方法</a><a href="/disclaimer/">免責事項</a><a href="mailto:hi@seadice.win">お問い合わせ</a><br><a href="https://seadice.win/">運営: SEADICE</a></p></footer>
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


# 心の不調を扱う章（course.json の chapters[].care が true）の全レッスンに出す相談先。番号は厚生労働省「まもろうよ こころ」で確認（2026-10-02）
CARE = ('<div class="box note"><p class="bt">つらいときの相談先</p>'
        '<p style="margin:0 0 8px">この講座は心理学の知識を学ぶためのもので、診断や治療の代わりにはなりません。気分の落ち込みや強い不安が続いてつらいときは、医療機関や、次のような公的な相談窓口に相談できます。</p><ul>'
        '<li>こころの健康相談統一ダイヤル <a href="tel:0570064556">0570-064-556</a>（都道府県・政令指定都市の公的な相談機関につながります。受付時間は地域によって異なります）</li>'
        '<li>よりそいホットライン <a href="tel:0120279338">0120-279-338</a>（24時間）</li></ul>'
        '<p style="margin:8px 0 0;font-size:13px">出典: <a href="https://www.mhlw.go.jp/mamorouyokokoro/soudan/tel/" target="_blank" rel="noopener">厚生労働省「まもろうよ こころ」電話相談</a></p></div>')


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
            out += f'<div class="card" id="ch{c["no"]}"><small>第{c["no"]}章</small><b>{E(c["title"])}</b><span>{E(c["desc"])}</span><ol class="lessons">{items}</ol></div>'
        else:
            out += f'<div class="card soon" id="ch{c["no"]}"><small>第{c["no"]}章</small><b>{E(c["title"])}</b><span>{E(c["desc"])}</span><span class="st">準備中</span></div>'
    return out


def course_index():
    first = LESSONS[0][1] if LESSONS else None
    body = f'''<span class="kicker">無料の心理学講座</span>
<h1>{E(COURSE["title"])}</h1>
<p class="updated">全{N_CH}章 ・ 公開中 {N_LESSONS}レッスン ・ 更新日 {UPDATED}</p>
<p class="lead">{E(COURSE["title"])}は、大学1年生の「心理学概論」と同じ流れで、心理学の全体像をゼロから学べる無料のオンライン講座です。登録は不要で、1レッスン10分ほどで読めます。</p>
{f'<div class="btns"><a class="btn" href="/course/{first["id"]}/">第1章から学びはじめる</a><a class="btn sub" href="/guide/">学び方を見る</a></div>' if first else ''}
<div class="box key"><p class="bt">この講座の特徴</p><ul>
<li>1レッスンは「学習目標 → 要点 → 本文 → キーワード（日本語・英語） → 確認問題 → 出典」の順に進みます。</li>
<li>本文は、心理学の原典や大学・公的機関の資料をもとに書いています。各レッスンの末尾に出典があります。</li>
<li>恋愛やお金の使い方など、身近な例とつなげて理解できるよう、姉妹メディアの研究解説記事を紹介しています。</li>
</ul></div>
<h2><span class="n">CONTENTS</span>講座の目次</h2>
<p class="answer">心理学とは何か（第1章）から始め、研究法、脳、感覚、記憶、発達、社会心理学、心理療法まで、全{N_CH}章で学びます。</p>
<div class="grid">{chapter_list()}</div>'''
    graph = [course_ld(), {"@type": "ItemList", "name": f'{COURSE["title"]}のレッスン一覧', "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": l["title"], "url": lurl(l)} for i, (_, l) in enumerate(LESSONS)]}]
    return write("course/", f'{COURSE["title"]}（無料の心理学講座）| {NAME}',
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
    quiz = "".join(
        f'<details open><summary>Q{i+1}. {E(q["q"])}</summary><div><ol>' + "".join(f"<li>{E(c)}</li>" for c in q["choices"]) +
        f'</ol><details><summary>答えを見る</summary><p><span class="ans">正解: {q["a"]+1}. {E(q["choices"][q["a"]])}</span><br>{E(q["exp"])}</p></details></div></details>'
        for i, q in enumerate(l["quiz"]))
    srcs = "".join(f'<li><a href="{s["url"]}" target="_blank" rel="noopener">{E(s["text"])}</a></li>' for s in l["sources"])
    chlist = "".join(f'<li><a href="/course/{x["id"]}/"{CUR if x["id"] == l["id"] else ""}><span class="no">{ch["no"]}-{j+1}</span>{E(x["short"])}</a></li>' for j, x in enumerate(ch["lessons"]))
    body = f'''<span class="kicker">第{ch["no"]}章 {E(ch["title"])} ・ レッスン{no}</span>
<h1>{E(l["title"])}</h1>
<p class="updated">読む時間の目安: {read_min(l)}分 ・ 公開日 {l.get("date", UPDATED)}</p>
<div class="box"><p class="bt">このレッスンの学習目標</p><ul>{"".join(f"<li>{E(g)}</li>" for g in l["goals"])}</ul></div>
<div class="box key"><p class="bt">要点</p><ol>{"".join(f"<li>{E(s)}</li>" for s in l["summary"])}</ol></div>
{CARE if ch.get("care") else ""}
{secs}
<h2><span class="n">KEYWORDS</span>キーワード（日本語・英語）</h2>
<p class="answer">このレッスンで覚えておきたい用語です。英語名も一緒に覚えると、海外の教科書や論文が読みやすくなります。</p>
{terms}
{f'<h2><span class="n">EXAMPLES</span>身近な例で深める</h2><p class="answer">このレッスンの内容を、日常の疑問にあてはめた研究解説記事です。</p><ul class="ex">{exs}</ul>' if exs else ''}
<div class="src"><h2>出典</h2><ol>{srcs}</ol></div>
<section class="final" aria-labelledby="quiz-h">
<p class="fk">LESSON {no} の仕上げ</p>
<h2 id="quiz-h">確認クイズ（全{len(l["quiz"])}問）</h2>
<p class="answer">学んだ内容を確かめましょう。答えを見る前に、自分で選んでみてください。</p>
<div class="quiz">{quiz}</div>
</section>
<div class="done"><p class="dt">レッスン{no}はここまでです</p><p class="dd">クイズで迷った問題があれば、その見出しの本文を読み直してから次に進みましょう。</p>
<div class="btns" style="margin:14px 0 0">{f'<a class="btn" href="/course/{next_l["id"]}/">次のレッスン: {E(next_l["short"])}</a>' if next_l else '<a class="btn" href="/course/">講座の目次へ（次の章は準備中です）</a>'}{f'<a class="btn sub" href="/course/{prev_l["id"]}/">前のレッスン</a>' if prev_l else ''}</div>
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
    return write(f'course/{l["id"]}/', f'{l["title"]}｜心理学入門 {no} | {NAME}', l["description"], body, graph,
                 trail=[("講座", CURL), (f'第{ch["no"]}章 {ch["title"]}', CURL), (l["short"], url)], current="/course/")


# ---------------- 用語辞典 ----------------
def glossary():
    fields = list(dict.fromkeys(t["field"] for t in TERMS))
    url = f"{URL}glossary/"
    body = (f'<span class="kicker">全{len(TERMS)}語</span><h1>心理学用語辞典</h1><p class="updated">更新日 {UPDATED}</p>'
            f'<p class="lead">心理学用語辞典は、日常で役立つ心理学・行動経済学の用語を、一文の定義でまとめたページです。各用語から、研究と出典を紹介した解説記事に進めます。</p>'
            '<div class="chips">' + "".join(f'<a href="#f{i}">{E(f)}</a>' for i, f in enumerate(fields)) + '</div>')
    for i, f in enumerate(fields):
        body += f'<h2 id="f{i}"><span class="n">{i+1:02d}</span>{E(f)}の用語</h2>'
        for t in (t for t in TERMS if t["field"] == f):
            a = ARTICLES.get(t.get("slug"))
            more = f'<a class="more" href="{a[0]}">解説記事: {E(a[1])}（{E(a[2])}）</a>' if a else ""
            name = f'<a href="/glossary/{t["id"]}/">{E(t["term"])}</a>' if rich(t) else E(t["term"])
            body += f'<div class="term" id="{t["id"]}"><span class="tt">{name}</span><span class="en">{E(t["en"])}</span><p>{E(t["def"])}</p>{more}</div>'
    body += f'<div class="box key" style="margin-top:36px"><p class="bt">心理学を基礎から学ぶなら</p><p style="margin:0">用語の背景にある心理学の全体像は、無料講座「<a href="/course/">{E(COURSE["title"])}</a>」で順番に学べます。</p></div>'
    graph = [{"@type": "DefinedTermSet", "@id": url, "name": "心理学用語辞典", "url": url, "inLanguage": "ja", "dateModified": UPDATED, "publisher": PUBLISHER,
              "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": f'{url}#{t["id"]}', "name": t["term"], "alternateName": t["en"],
                                  "description": t["def"], "url": f'{url}{t["id"]}/' if rich(t) else f'{url}#{t["id"]}', "inDefinedTermSet": url} for t in TERMS]}]
    return write("glossary/", f"心理学用語辞典（{len(TERMS)}語をやさしく解説）| {NAME}",
                 f"単純接触効果、愛着スタイル、アンカリング効果、ガスライティングなど、日常で役立つ心理学用語{len(TERMS)}語を一文の定義でやさしく解説。出典つきの解説記事にリンクしています。",
                 body, graph, trail=[("心理学用語辞典", url)], current="/glossary/")


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
{f'<h2><span class="n">RESEARCH</span>研究の解説記事</h2><p><a href="{a[0]}">{E(a[1])}</a>（{E(a[2])}）</p>' if a else ""}
<h2><span class="n">FAQ</span>よくある質問</h2>
{faq_html(faq)}
{'<h2><span class="n">RELATED</span>同じ分野の用語</h2><div class="chips">' + "".join(f'<a href="/glossary/{x["id"]}/">{E(x["term"])}</a>' if rich(x) else f'<a href="/glossary/#{x["id"]}">{E(x["term"])}</a>' for x in rel) + "</div>" if rel else ""}
<div class="src"><h2>出典</h2><ol>{"".join(f'<li><a href="{x["url"]}" target="_blank" rel="noopener">{E(x["text"])}</a></li>' for x in t["sources"])}</ol></div>
<p style="margin-top:28px"><a href="/glossary/">心理学用語辞典の一覧へ（{len(TERMS)}語）</a></p>'''
    graph = [{"@type": "DefinedTerm", "@id": url, "name": key, "alternateName": t["en"], "description": t["def"], "url": url,
              "inDefinedTermSet": {"@type": "DefinedTermSet", "name": "心理学用語辞典", "url": f"{URL}glossary/"}},
             {"@type": "Article", "headline": f"{key}とは", "description": t["def"], "url": url, "inLanguage": "ja",
              "datePublished": t.get("date", UPDATED), "dateModified": t.get("date", UPDATED), "mainEntityOfPage": {"@type": "WebPage", "@id": url},
              "author": {"@type": "Organization", "name": f"{NAME}編集部"}, "publisher": PUBLISHER, "citation": [x["url"] for x in t["sources"]]},
             faq_ld(faq)]
    return write(f'glossary/{t["id"]}/', f'{key}とは？意味と例をやさしく解説 | {NAME}', t["def"][:120], body, graph,
                 trail=[("心理学用語辞典", f"{URL}glossary/"), (f"{key}とは", url)], current="/glossary/")


# ---------------- 学び方ガイド ----------------
SITES = [
    ("高校生のための心理学講座 YouTube版", "https://psych.or.jp/interest/lecture_hs/", "日本心理学会", "動画で学びたい人・進路を考えている人",
     "心理学の講義動画。知覚・ストレス・社会心理学など、テーマごとに視聴できる。"),
    ("日本心理学会「心理学ミュージアム」", "http://psychmuseum.jp/", "日本心理学会", "心理学に初めて触れる人",
     "記憶・感情・社会・自己などのテーマ別に、心理学の研究を展示形式で紹介するウェブ上のミュージアム。"),
    ("日本心理学会「心理学ワールド」", "https://psych.or.jp/publication/world/", "日本心理学会", "研究のテーマを広く知りたい人",
     "学会が発行する一般向けの心理学の読み物。研究者がテーマごとに解説している。"),
    ("Asuka Academy「[Yale] 心理学入門」", "https://www.asuka-academy.com/", "Asuka Academy", "海外の大学の講義を日本語字幕で見たい人",
     "イェール大学の心理学入門の講義動画を、日本語字幕つきで視聴できる。無料の会員登録が必要。"),
    ("J-STAGE「心理学研究」", "https://www.jstage.jst.go.jp/browse/jjpsy/", "日本心理学会（J-STAGEで公開）", "論文を読んでみたい人",
     "日本心理学会の学術誌。1926年からの論文が掲載され、多くを無料で読める。"),
    ("OpenStax「Psychology 2e」", "https://openstax.org/details/books/psychology-2e", "OpenStax（米ライス大学）", "英語の教科書で体系的に学びたい人",
     "大学の心理学入門の教科書を、オープンライセンス（CC BY-NC-SA 4.0）で無料公開。英語。"),
]


def guide():
    url = f"{URL}guide/"
    gfaq = [
        ("心理学を無料で学べるおすすめのサイトは？",
         f"体系的に読んで学ぶなら{NAME}の無料講座「{COURSE['title']}」、動画なら日本心理学会の「高校生のための心理学講座」やAsuka Academyの「[Yale] 心理学入門」、論文ならJ-STAGEの「心理学研究」、英語の教科書ならOpenStaxの「Psychology 2e」がおすすめです。"),
        ("心理学は独学できますか？",
         "できます。入門的な知識は、無料の講座や学会が公開している読み物・講義動画、無料の教科書で学べます。ただし公認心理師などの資格や、カウンセリングなどの臨床の実践には、大学・大学院での専門的な教育が必要です。"),
        ("心理学は何から学べばいいですか？",
         "まず心理学とは何か・どう研究するかを学び、次に記憶や感情などの基礎分野、最後に社会心理学や心理療法などの応用分野に進む順番がおすすめです。大学の「心理学概論」もこの順番です。"),
        (f"{NAME}とはどんなサイトですか？",
         f"{NAME}は、心理学を無料で独学できるサイトです。SEADICEが運営し、大学の心理学概論と同じ流れの無料講座「{COURSE['title']}」と、心理学用語辞典を掲載しています。登録は不要です。"),
    ]
    own = (f'<tr><td data-l="サイト"><a href="/course/">{E(NAME)}「{E(COURSE["title"])}」</a></td><td data-l="運営">SEADICE</td>'
           f'<td data-l="向いている人">読んで体系的に独学したい人</td><td data-l="特徴">大学の心理学概論と同じ流れの全{N_CH}章の無料講座。確認問題・英語のキーワード・出典つき。登録不要。</td></tr>')
    rows = own + "".join(f'<tr><td data-l="サイト"><a href="{u}" target="_blank" rel="noopener">{E(n)}</a></td><td data-l="運営">{E(o)}</td><td data-l="向いている人">{E(w)}</td><td data-l="特徴">{E(d)}</td></tr>' for n, u, o, w, d in SITES)
    def fr(a, b, c):
        return f'<tr><td data-l="分野">{a}</td><td data-l="何を調べる分野か">{b}</td><td data-l="身近な例">{c}</td></tr>'
    body = f'''<span class="kicker">2026年版</span>
<h1>心理学を無料で学べるおすすめサイトと、初心者が学ぶ順番</h1>
<p class="updated">更新日 {UPDATED}</p>
<p class="lead">心理学を無料で独学するなら、読んで学ぶ講座・講義動画・論文の3種類を組み合わせるのがおすすめです。このページでは、無料で使える学習サイトと、初心者が挫折しない学ぶ順番をまとめました。</p>
<h2><span class="n">01</span>心理学を無料で学べるおすすめサイト</h2>
<p class="answer">読んで学ぶなら{E(NAME)}の講座、動画なら日本心理学会やAsuka Academy、論文はJ-STAGE、英語の教科書はOpenStaxが無料で使えます。</p>
<table><thead><tr><th>サイト</th><th>運営</th><th>向いている人</th><th>特徴</th></tr></thead><tbody>{rows}</tbody></table>
<h2 id="order"><span class="n">02</span>初心者が心理学を学ぶ順番</h2>
<p class="answer">「心理学とは何か・研究法」→「基礎分野」→「応用分野」→「論文」の順に進むと、挫折しにくくなります。</p>
<ol style="padding-left:22px">
<li><strong>心理学とは何か、どう研究するかを知る。</strong><a href="/course/">講座</a>の第1章・第2章で、心理学が「データで確かめる科学」であることを押さえます。</li>
<li><strong>基礎分野を学ぶ。</strong>脳、感覚と知覚、学習、記憶、感情など、心の基本的な仕組みを学びます。</li>
<li><strong>応用分野を学ぶ。</strong>発達、パーソナリティ、社会心理学、ストレスと健康、心理療法など、人の生活に近いテーマに進みます。</li>
<li><strong>論文に触れる。</strong>J-STAGEの「心理学研究」などで、興味のあるテーマの論文を読みます。講座の各レッスンの出典も入り口になります。</li>
</ol>
<h2 id="fields"><span class="n">03</span>心理学の主な分野と、日常の疑問との関係</h2>
<p class="answer">日常の悩みの多くは、社会心理学・行動経済学・発達心理学（愛着）・感情と表情の研究で説明されています。</p>
<table><thead><tr><th>分野</th><th>何を調べる分野か</th><th>身近な例</th></tr></thead><tbody>
{fr("社会心理学", "人が他者や集団からどう影響を受けるか", '<a href="/glossary/#mere-exposure">単純接触効果</a>、<a href="/glossary/#similarity-attraction">類似性-魅力仮説</a>、<a href="/glossary/#social-comparison">社会的比較</a>')}
{fr("行動経済学", "人がお金や選択で「合理的でない」判断をする理由", '<a href="/glossary/#anchoring">アンカリング効果</a>、<a href="/glossary/#status-quo-bias">現状維持バイアス</a>、<a href="/glossary/#mental-accounting">心の会計</a>')}
{fr("発達心理学（愛着理論）", "人との結びつき方が、どう形づくられるか", '<a href="/glossary/#attachment-style">愛着スタイル</a>')}
{fr("感情・表情の研究", "表情やしぐさに、感情がどう表れるか", '<a href="/glossary/#duchenne-smile">デュシェンヌ・スマイル</a>')}
{fr("臨床心理学", "心の不調の理解と支援", f'診断や治療は専門家の領域です。{E(NAME)}では、<a href="/glossary/#gaslighting">ガスライティング</a>のように、身を守るための知識に限って扱います。')}
</tbody></table>
{guide_lists()}
<h2><span class="n">04</span>よくある質問</h2>
{faq_html(gfaq)}'''
    graph = [
        {"@type": "Article", "headline": "心理学を無料で学べるおすすめサイトと、初心者が学ぶ順番", "url": url, "inLanguage": "ja",
         "datePublished": UPDATED, "dateModified": UPDATED, "mainEntityOfPage": {"@type": "WebPage", "@id": url},
         "author": {"@type": "Organization", "name": f"{NAME}編集部"}, "publisher": PUBLISHER},
        {"@type": "ItemList", "name": "心理学を無料で学べるおすすめサイト", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "url": u} for i, (n, u) in enumerate([(f'{NAME}「{COURSE["title"]}」', CURL)] + [(s[0], s[1]) for s in SITES])]},
        faq_ld(gfaq),
    ]
    return write("guide/", f"心理学を無料で学べるおすすめサイトと、初心者が学ぶ順番【2026年版】| {NAME}",
                 f"心理学を無料で独学できるおすすめサイト（{NAME}の無料講座、日本心理学会の講義動画、Asuka Academy、J-STAGE、OpenStax）と、初心者が挫折しない学ぶ順番をまとめました。",
                 body, graph, trail=[("心理学の学び方", url)], current="/guide/")


def guide_page(g):
    url = f'{URL}guide/{g["id"]}/'
    chs = [c for c in COURSE["chapters"] if c["no"] in g.get("chapters", [])]
    secs = "".join(f'<h2><span class="n">{i+1:02d}</span>{E(x["h"])}</h2><p class="answer">{E(x["answer"])}</p>' + "".join(f"<p>{E(p)}</p>" for p in x["paras"]) for i, x in enumerate(g["sections"]))
    course = ""
    if chs:
        course = (f'<h2><span class="n">COURSE</span>講座で学ぶ</h2><p class="answer">無料講座「{E(COURSE["title"])}」の次の章で、順番に学べます。</p><div class="grid">'
                  + "".join(f'<div class="card"><small>第{c["no"]}章</small><b>{E(c["title"])}</b><ol class="lessons">' + "".join(f'<li><a href="/course/{l["id"]}/"><span class="no">{c["no"]}-{i+1}</span>{E(l["short"])}</a></li>' for i, l in enumerate(c["lessons"])) + "</ol></div>" for c in chs) + "</div>")
    kt = [t for t in TERMS if t["id"] in g.get("terms", [])]
    terms = ('<h2><span class="n">KEYWORDS</span>関連する用語</h2><div class="chips">' + "".join(f'<a href="/glossary/{t["id"]}/">{E(t["term"])}</a>' if rich(t) else f'<a href="/glossary/#{t["id"]}">{E(t["term"])}</a>' for t in kt) + "</div>") if kt else ""
    faq = [(q["q"], q["a"]) for q in g.get("faq", [])]
    kicker = "心理学の分野" if g["kind"] == "field" else "心理学の独学Q&A"
    body = f'''<span class="kicker">{kicker}</span>
<h1>{E(g["title"])}</h1>
<p class="updated">更新日 {g.get("date", UPDATED)}</p>
<p class="lead">{E(g["lead"])}</p>
{secs}{course}{terms}
{f'<h2><span class="n">FAQ</span>よくある質問</h2>{faq_html(faq)}' if faq else ""}
<div class="src"><h2>出典</h2><ol>{"".join(f'<li><a href="{x["url"]}" target="_blank" rel="noopener">{E(x["text"])}</a></li>' for x in g["sources"])}</ol></div>
<div class="box key" style="margin-top:28px"><p class="bt">次に読む</p><p style="margin:0"><a href="/guide/">心理学の学び方（おすすめサイトと学ぶ順番）</a> ・ <a href="/course/">無料講座の目次</a> ・ <a href="/glossary/">心理学用語辞典</a></p></div>'''
    graph = [{"@type": "Article", "headline": g["title"], "description": g["lead"], "url": url, "inLanguage": "ja",
              "datePublished": g.get("date", UPDATED), "dateModified": g.get("modified", g.get("date", UPDATED)), "mainEntityOfPage": {"@type": "WebPage", "@id": url},
              "author": {"@type": "Organization", "name": f"{NAME}編集部"}, "publisher": PUBLISHER, "citation": [x["url"] for x in g["sources"]]}]
    if faq:
        graph.append(faq_ld(faq))
    return write(f'guide/{g["id"]}/', f'{g["title"]} | {NAME}', g["lead"][:120], body, graph,
                 trail=[("心理学の学び方", f"{URL}guide/"), (g["title"], url)], current="/guide/")


def guide_lists():
    out = ""
    for kind, h, a in (("qa", "心理学の独学Q&A", "心理学を独学するときによくある疑問に、1ページずつ答えています。"),
                       ("field", "分野別の入門", "心理学の主な分野ごとに、何がわかる分野か、講座のどの章で学べるかをまとめています。")):
        gs = [g for g in GUIDES if g["kind"] == kind]
        if gs:
            out += f'<h2 id="{kind}"><span class="n">{"QA" if kind == "qa" else "FIELDS"}</span>{h}</h2><p class="answer">{a}</p><div class="grid">' + "".join(
                f'<a class="card" href="/guide/{g["id"]}/"><b>{E(g["title"])}</b><span>{E(g["lead"][:70])}…</span></a>' for g in gs) + "</div>"
    return out


# ---------------- トップ ----------------
def home():
    pick = ["mere-exposure", "attachment-style", "anchoring", "gaslighting", "duchenne-smile", "status-quo-bias", "positive-illusions", "mental-accounting"]
    tmap = {t["id"]: t for t in TERMS}
    chips = "".join(f'<a href="/glossary/#{i}">{E(tmap[i]["term"])}</a>' for i in pick if i in tmap)
    first = LESSONS[0][1] if LESSONS else None
    sisters = [(SISTERS[0]["name"], SISTERS[0]["url"], "恋愛・しぐさ・相性の心理を、研究から検証する"),
               (SISTERS[1]["name"], SISTERS[1]["url"], "お金の使い方の心理を、行動経済学から読み解く"),
               (RESEARCH["name"], RESEARCH["url"], "睡眠・集中・先延ばしなど、日常の悩みを科学で調べる")]
    body = f'''<div class="hero"><p class="tag">{E(CFG["tagline"])}</p><h1>{E(NAME)}</h1></div>
<p class="lead">{E(CFG["lead"])}</p>
<p class="stats"><span><b>{N_CH}</b>章の無料講座</span><span><b>{N_LESSONS}</b>レッスン公開中</span><span><b>{len(TERMS)}</b>語の用語辞典</span><span>登録不要</span></p>
<div class="btns">{f'<a class="btn" href="/course/{first["id"]}/">講座を第1章から始める</a>' if first else ''}<a class="btn sub" href="/guide/">心理学の学び方を見る</a></div>
<h2><span class="n">01</span>無料講座「{E(COURSE["title"])}」</h2>
<p class="answer">大学1年生の「心理学概論」と同じ流れで、心理学の全体像をゼロから学べる全{N_CH}章の講座です。</p>
<div class="grid">{chapter_list()}</div>
<p style="margin-top:14px"><a href="/course/">講座の目次をすべて見る</a></p>
<h2><span class="n">02</span>心理学用語辞典</h2>
<p class="answer">日常で出会うことの多い心理学用語を、一文の定義でまとめています。はじめての人は次の用語から。</p>
<div class="chips">{chips}</div>
<p><a href="/glossary/">用語辞典をすべて見る（{len(TERMS)}語）</a></p>
<h2><span class="n">03</span>身近な疑問から深める（姉妹メディア）</h2>
<p class="answer">講座で学んだ心理学が、恋愛やお金の悩みでどう役立つかは、SEADICEが運営する次のメディアで出典つきで解説しています。</p>
<div class="grid">{"".join(f'<a class="card" href="{u}"><b>{E(n)}</b><span>{E(d)}</span></a>' for n, u, d in sisters)}</div>
<h2><span class="n">04</span>よくある質問</h2>
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
        ("運営", [f"{NAME}は、アプリスタジオ SEADICE（シーダイス）が運営する、心理学を無料で独学できるサイトです。登録や料金は必要ありません。"]),
        ("目的", ["心理学を学びたい人が、費用をかけずに、大学の入門講義と同じ順番で心理学の全体像を学べるようにすることです。"]),
        ("作り方", ["講座と用語辞典は、AI（Claude）が心理学の原典、大学・学会・公的機関の資料を調べ、内容を確認したうえで、日本語で独自に書いています。特定の教科書の翻訳ではありません。",
                  "各レッスンの末尾に出典を載せています。確認できなかった内容は書きません。"]),
        ("お問い合わせ", ['誤りのご指摘やご意見は <a href="mailto:hi@seadice.win">hi@seadice.win</a> までお送りください。返信が必要な場合はその旨をお書きください。'])]),
    "sources": ("出典と検証の方法", f"{NAME}で使う出典の基準と、内容の確認方法を説明します。", [
        ("使う出典", ["心理学の原典（古典的な論文・著作）、査読のある学術論文、大学・学会・公的機関の資料を使います。", "個人のブログや、出典の示されていない俗説は使いません。"]),
        ("確認の方法", ["書く内容が出典に書かれていることを、原典や公式のページを開いて1件ずつ確認します。確認できなかった数値や主張は削除します。"]),
        ("訂正", ["誤りが見つかった場合は確認のうえ修正し、ページの更新日を新しくします。"])]),
    "disclaimer": ("免責事項", f"{NAME}の利用にあたっての注意事項です。", [
        ("情報の性質", [f"{NAME}の内容は、心理学の一般的な知識の提供であり、診断や治療、カウンセリングの代わりになるものではありません。"]),
        ("専門家への相談", ["心身の不調や悩みが深刻な場合は、医師や公認心理師などの専門家、公的な相談窓口に相談してください。"]),
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
             f"{NAME}はSEADICE(https://seadice.win/)が運営する、心理学を無料で独学できるサイトです。登録不要・無料。",
             f"大学1年生の「心理学概論」と同じ流れの無料講座「{COURSE['title']}」（全{N_CH}章）と、心理学用語辞典（{len(TERMS)}語）を掲載しています。",
             "本文は心理学の原典や大学・学会・公的機関の資料をもとに日本語で独自に書いており、各ページに出典があります。", "",
             "## 主要ページ", "", f"- トップ: {URL}", f"- 無料講座「{COURSE['title']}」: {CURL}",
             f"- 心理学を無料で学べるおすすめサイトと学ぶ順番: {URL}guide/", f"- 心理学用語辞典: {URL}glossary/",
             f"- このサイトについて: {URL}about/", f"- 出典と検証の方法: {URL}sources/", "",
             "## 講座の目次", ""]
    for c in COURSE["chapters"]:
        lines.append(f'- 第{c["no"]}章 {c["title"]}: {c["desc"]}' + ("" if c["lessons"] else "（準備中）"))
        lines += [f'  - {c["no"]}-{i+1} {l["title"]}: {lurl(l)}' for i, l in enumerate(c["lessons"])]
    lines += ["", "## 姉妹メディア（詳しい研究解説の記事）", "", *[f"- {m['name']}: {m['url']}" for m in SISTERS], f"- {RESEARCH['name']}: {RESEARCH['url']}", ""]
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
    urls += [guide(), glossary()] + [term_page(t) for t in TERMS if rich(t)] + [guide_page(g) for g in GUIDES]
    urls += trust_pages()
    extras(urls)
    print(f"built {CFG['path']} ({N_LESSONS} lessons, {len(TERMS)} terms, {len(urls)} pages)")
