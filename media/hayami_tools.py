"""記事メディアの研究早見表(/hayami/)と悩みチェック(/check/)を生成し、各記事の末尾に両方への案内を差し込む。

対象は「わかっている度(.evidence)」「数字(.stats)」「今日やること(.step)」の型を持つ記事メディア(下の M に設定があるもの)。
中身は各記事(出典照合済み)のタイトル・わかっている度・数字・3行でわかる・今日やることを集めたものだけ。新しい主張は足さない。
記事が増えれば自動で載る。デプロイ時(.github/workflows/deploy.yml)にも build.py の前に実行する。
実行: python3 media/hayami_tools.py kokoro kosodate oya && python3 media/build.py {slug}
出力: media/{slug}-pages.json の check / hayami(ほかの固定ページは残す)、各記事の <!--ktools--> ブロック
新しいメディアに広げるときは M に1件足し、deploy.yml の引数にも slug を足す。
"""
import html
import json
import re
import sys
from pathlib import Path

E = html.escape
ROOT = Path(__file__).resolve().parent.parent
PUB = {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}

# メディアごとの言葉。area は「〜の悩み」の言い方、safe は記事末の相談先の1文(各メディアのルールと同じ)
M = {
    "kokoro": {
        "area": "AI・スマホ・SNS・在宅勤務まわりの悩み",
        "hayami_title": "AI・スマホ疲れの研究早見表",
        "hayami_seo": "AI・スマホ・SNS疲れの研究早見表｜悩み{n}件の答えと今日やること",
        "hayami_desc": "AIについていけない、スマホがやめられない、SNSで比べて落ち込む、在宅勤務で孤独。悩み{n}件について研究でわかったことと今日やることを、わかっている度（★3段階）つきで一覧にしました。出典照合済み。",
        "check_title": "AI・スマホ疲れのセルフチェック",
        "check_name": "AI・スマホ疲れのセルフチェック（今日やることリスト）",
        "check_seo": "AI・スマホ・SNS疲れのセルフチェック｜悩みを選ぶと今日やることがわかる（無料）",
        "check_desc": "AIについていけない、通知で集中できない、休むと罪悪感。当てはまる悩みを{n}件から選ぶと、研究にもとづく「今日やること」をまとめます。診断はしません。無料・登録不要。",
        "check_link": "セルフチェックで「今日やること」をまとめる",
        "app_cat": "HealthApplication",
        "examples": ["notifications-focus", "rest-guilt", "ai-cant-keep-up"],
        "safe": "つらい状態が2週間以上続くときや、日常生活に支障があるときは、医療機関や、こころの健康相談統一ダイヤル（0570-064-556）などの相談窓口に相談できます。",
        "diag_q": "このチェックで、心の状態を診断できますか？",
        "diag_a": "できません。点数や判定は出さず、選んだ悩みについて記事で紹介している「今日やること」をまとめるだけの道具です。つらい状態が続くときは、医療機関や相談窓口に相談できます。",
    },
    "kosodate": {
        "area": "子どものAI・スマホ・学び・心の悩み",
        "hayami_title": "子どものAI・スマホの研究早見表",
        "hayami_seo": "子どものAI・スマホ・学びの研究早見表｜悩み{n}件の答えと今日やること",
        "hayami_desc": "子どものAIの使わせ方、スクリーンタイム、ながら勉強、SNS、親子の会話。悩み{n}件について研究でわかったことと今日やることを、わかっている度（★3段階）つきで一覧にしました。出典照合済み。",
        "check_title": "子育ての悩みチェック",
        "check_name": "子どものAI・スマホの悩みチェック（今日やることリスト）",
        "check_seo": "子どものAI・スマホの悩みチェック｜選ぶと親が今日やることがわかる（無料）",
        "check_desc": "AIで宿題をしてしまう、スマホの時間が長い、ルールが守れない。当てはまる悩みを{n}件から選ぶと、研究にもとづく親の「今日やること」をまとめます。診断はしません。無料・登録不要。",
        "check_link": "悩みチェックで親の「今日やること」をまとめる",
        "app_cat": "LifestyleApplication",
        "examples": [],
        "safe": "子どもの発達・睡眠・心の様子で気になることがあれば、かかりつけの小児科や自治体の子育て相談窓口に相談できます。",
        "diag_q": "このチェックで、子どもの発達や心の状態を判定できますか？",
        "diag_a": "できません。点数や判定は出さず、選んだ悩みについて記事で紹介している「今日やること」をまとめるだけの道具です。気になる様子が続くときは、かかりつけの小児科や自治体の子育て相談窓口に相談できます。",
    },
    "oya": {
        "area": "親の物忘れ・体・運転・ひとり暮らし・介護の悩み",
        "hayami_title": "親が年をとったときの研究早見表",
        "hayami_seo": "親の物忘れ・運転・ひとり暮らしの研究早見表｜悩み{n}件の答えと今日やること",
        "hayami_desc": "親の物忘れ、補聴器、運転、ひとり暮らし、冬の寒さ、介護とお金。悩み{n}件について研究と公的資料でわかったことと今日やることを、わかっている度（★3段階）つきで一覧にしました。出典照合済み。",
        "check_title": "親のことの悩みチェック",
        "check_name": "親が年をとったときの悩みチェック（今日やることリスト）",
        "check_seo": "親の物忘れ・運転・ひとり暮らしの悩みチェック｜選ぶと今日やることがわかる（無料）",
        "check_desc": "親が物忘れをする、運転が心配、ひとり暮らしが不安。当てはまる悩みを{n}件から選ぶと、研究と公的資料にもとづく「今日やること」をまとめます。診断はしません。無料・登録不要。",
        "check_link": "悩みチェックで「今日やること」をまとめる",
        "app_cat": "LifestyleApplication",
        "examples": [],
        "safe": "親の物忘れや体の様子で気になることがあれば、かかりつけ医か、お住まいの地域の地域包括支援センターに相談できます。",
        "diag_q": "このチェックで、親が認知症かどうかわかりますか？",
        "diag_a": "わかりません。点数や判定は出さず、選んだ悩みについて記事で紹介している「今日やること」をまとめるだけの道具です。気になる様子があるときは、かかりつけ医か地域包括支援センターに相談できます。",
    },
}

COMMON_CSS = (".fchips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px}"
              ".hc,.hl{font:inherit;font-size:14px;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:999px;padding:8px 14px;cursor:pointer}"
              ".hc.on,.hl.on{border-color:var(--accent);color:var(--accent)}"
              "button:focus-visible,a:focus-visible,input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"
              ".flabel{font-size:13px!important;color:var(--muted);margin:14px 0 6px!important}"
              ".st{display:inline-block;font-size:12px;font-weight:800;border:1px solid var(--accent);color:var(--accent);border-radius:999px;padding:3px 10px}"
              ".kc{font-size:12px;font-weight:700;color:var(--muted)}"
              ".fq{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 16px;margin:10px 0}.fq summary{cursor:pointer;font-weight:700;font-size:15px;line-height:1.6}.fq p{font-size:15px;line-height:1.85;margin:10px 0 6px}"
              ".help{font-size:14px;line-height:1.8;color:var(--muted);border-top:1px solid var(--border);padding-top:16px;margin-top:32px}")
HAYAMI_CSS = COMMON_CSS + (
    ".hyl{list-style:none;margin:10px 0 0!important;padding:0;display:grid;gap:14px}"
    ".hy{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:14px;padding:18px 20px;margin:0!important;scroll-margin-top:72px}"
    ".hy:target{box-shadow:0 0 0 2px var(--accent)}"
    ".hy h3{font-size:17px;line-height:1.6;margin:8px 0 4px}.hy p{font-size:15px;line-height:1.8;margin:6px 0}.hy a{font-size:14px;color:var(--link)}"
    ".hy-h{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin:0!important}"
    ".hy-n{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}.hy-n b{font-size:20px;color:var(--accent)}.hy-n span{font-size:13px!important;color:var(--muted)}"
    ".hy-do{border-top:1px solid var(--border);padding-top:8px}.hy-do span{display:block;font-size:12px;font-weight:700;color:var(--muted)}.hy-do small{display:block;font-size:13px;color:var(--muted)}")
CHECK_CSS = COMMON_CSS + (
    ".kg{border:1px solid var(--border);border-radius:14px;padding:12px 16px 8px;margin:0 0 14px;background:var(--card);min-width:0}"
    ".kg legend{font-weight:800;font-size:15px;padding:0 6px}"
    ".kq{display:flex;gap:10px;align-items:flex-start;padding:10px 0;font-size:15px;line-height:1.6;cursor:pointer;border-top:1px solid var(--border)}.kq:first-of-type{border-top:0}"
    ".kq input{width:20px;height:20px;margin-top:2px;flex:none;accent-color:var(--accent)}"
    ".kbar{position:sticky;bottom:0;display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:12px 0;background:var(--bg)}"
    "#kgo,#ksave{font:inherit;font-weight:800;font-size:15px;padding:12px 20px;border-radius:12px;border:0;background:var(--accent);color:var(--bg);cursor:pointer}"
    "#ksave{background:transparent;color:var(--accent);border:1px solid var(--accent);padding:8px 14px;font-size:14px}"
    ".kout{margin:12px 0 24px}.kr{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:14px;padding:16px 18px;margin:12px 0}"
    ".kr ol{margin:8px 0;padding-left:20px}.kr li{font-size:15px;line-height:1.8;margin:8px 0}.kr a{font-size:14px;color:var(--link)}.kti{font-size:12px;color:var(--muted);margin-left:8px}"
    ".kt{width:100%;border-collapse:collapse;font-size:14px}.kt th,.kt td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top;line-height:1.7}")
FILTER_JS = """<script>
(function(){
var f='',l='',li=[].slice.call(document.querySelectorAll('.hy')),cnt=document.getElementById('cnt');
function each(s,fn){[].forEach.call(document.querySelectorAll(s),fn)}
function filt(){var n=0;li.forEach(function(e){var ok=(!f||e.dataset.c===f)&&(!l||e.dataset.l===l);e.hidden=!ok;if(ok)n++});cnt.textContent=n+'件'}
function grp(sel,key,set){each(sel,function(b){b.onclick=function(){set(b.dataset[key]);each(sel,function(x){x.classList.toggle('on',x===b);x.setAttribute('aria-pressed',x===b)});filt()}})}
grp('.hc','f',function(v){f=v});grp('.hl','l',function(v){l=v});filt();
})();
</script>"""
CHECK_JS = """<script>
(function(){
var D=JSON.parse(document.getElementById('kd').textContent),K='%s',f=document.getElementById('kf'),o=document.getElementById('kout'),sel=document.getElementById('ksel');
var bx=[].slice.call(f.querySelectorAll('input[type=checkbox]'));
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function cnt(){sel.textContent=bx.filter(function(b){return b.checked}).length+'件選択中'}
bx.forEach(function(b){b.onchange=cnt});
try{var s=JSON.parse(localStorage.getItem(K)||'[]');bx.forEach(function(b){b.checked=s.indexOf(b.value)>=0})}catch(e){}
cnt();
f.onsubmit=function(){
var c=bx.filter(function(b){return b.checked}).map(function(b){return b.value});
o.hidden=false;
if(!c.length){o.innerHTML='<p>当てはまる悩みを1つ以上選んでください。</p>';return false}
var h='<h2>今日やること（'+c.length+'件の悩みから）</h2>'+(c.length>2?'<p class="note">一度に全部やらず、上の1〜2個から始めてください。</p>':'');
c.forEach(function(k){var x=D[k];h+='<div class="kr"><p class="kc">'+esc(x.w)+'　わかっている度 '+x.s+'</p><ol>'+x.st.map(function(t){return'<li><b>'+esc(t.t)+'</b>'+(t.time?'<span class="kti">'+esc(t.time)+'</span>':'')+'<br>'+esc(t.d)+'</li>'}).join('')+'</ol><a href="/'+k+'/">記事で根拠を読む</a></div>'});
h+='<p><button type="button" id="ksave">この端末に保存</button> <span class="note">保存はこの端末のブラウザの中だけです。</span></p>';
o.innerHTML=h;o.scrollIntoView({behavior:'smooth',block:'start'});
document.getElementById('ksave').onclick=function(){try{localStorage.setItem(K,JSON.stringify(c));this.textContent='保存しました'}catch(e){this.textContent='保存できませんでした'}};
return false};
})();
</script>"""
BLOCK = re.compile(r"<!--ktools-->.*?<!--/ktools-->\n?", re.S)


def txt(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()


def split_title(t):
    m = re.search(r"[。？]", t)
    if not m:
        return t, ""
    return t[:m.end()].rstrip("。"), t[m.end():].strip()


def ld(graph):
    return '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def collect(cfg, site, posts):
    cats = {c["name"]: c for c in cfg["categories"]}
    D = []
    for p in posts:
        f = site / p["slug"] / "index.html"
        if not f.exists() or p.get("category") not in cats:
            continue
        h = BLOCK.sub("", f.read_text())
        lv = re.search(r"わかっている度 <b>(★+☆*)</b>\s*(\S+?)</span>", h)
        st = re.search(r'<div class="stat"><b>(.*?)</b><span>(.*?)</span>', h, re.S)
        summ = re.search(r'<div class="summary">.*?<ol>(.*?)</ol>', h, re.S)
        steps = re.findall(r'<p class="ttl">(.*?)</p>\s*<p class="dsc">(.*?)</p>(?:\s*<p class="time">(.*?)</p>)?', h, re.S)
        if not (lv and steps):
            continue
        worry, ans = split_title(p["title"])
        lis = re.findall(r"<li>(.*?)</li>", summ.group(1), re.S) if summ else []
        s1 = txt(lis[0]) if lis else ""
        D.append({"slug": p["slug"], "cat": cats[p["category"]]["id"], "catName": p["category"], "worry": worry,
                  "answer": ans or s1, "stars": lv.group(1), "lv": lv.group(2).strip(),
                  "num": txt(st.group(1)) if st else "", "numNote": txt(st.group(2)) if st else "",
                  "steps": [{"t": txt(a), "d": txt(b), "time": txt(c)} for a, b, c in steps]})
    order = list(cats)
    D.sort(key=lambda x: (order.index(x["catName"]), -x["stars"].count("★")))
    return D, [c for c in cats.values() if any(x["catName"] == c["name"] for x in D)]


def run(slug):
    m = M[slug]
    cfg = json.loads((ROOT / f"media/{slug}.json").read_text())
    site = ROOT / cfg["path"]
    base = cfg["url"]
    posts = json.loads((ROOT / f"media/{slug}-posts.json").read_text())
    D, used = collect(cfg, site, posts)
    n = len(D)
    date = max(p["date"] for p in posts)
    cnt = {k: sum(1 for x in D if x["stars"].count("★") == k) for k in (3, 2, 1)}
    safe = f'<p class="help">{E(m["safe"])}</p>'

    # ---------- 早見表 /hayami/ ----------
    def hy(x):
        s = x["steps"][0]
        num = (f'<p class="hy-n"><b>{E(x["num"])}</b><span>{E(x["numNote"])}</span></p>' if x["num"] else "")
        return (f'<li class="hy" id="{x["slug"]}" data-c="{x["cat"]}" data-l="{x["stars"].count("★")}">'
                f'<p class="hy-h"><span class="st">わかっている度 {x["stars"]} {E(x["lv"])}</span><span class="kc">{E(x["catName"])}</span></p>'
                f'<h3>{E(x["worry"])}</h3><p>{E(x["answer"])}</p>{num}'
                f'<p class="hy-do"><span>今日やること</span>{E(s["t"])}{"<small>" + E(s["time"]) + "</small>" if s["time"] else ""}</p>'
                f'<a href="/{x["slug"]}/">記事で根拠を読む</a></li>')

    chips = '<button type="button" class="hc on" data-f="" aria-pressed="true">すべて</button>' + "".join(
        f'<button type="button" class="hc" data-f="{c["id"]}" aria-pressed="false">{E(c["name"])}</button>' for c in used)
    lchips = '<button type="button" class="hl on" data-l="" aria-pressed="true">すべて</button>' + "".join(
        f'<button type="button" class="hl" data-l="{k}" aria-pressed="false">{"★" * k + "☆" * (3 - k)}</button>' for k in (3, 2, 1) if cnt[k])
    h_url = base + "hayami/"
    hayami_ld = ld([{"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f'「{x["worry"]}」について、研究でわかっていることは？',
         "acceptedAnswer": {"@type": "Answer", "text": f'{x["answer"]} 今日できること：{x["steps"][0]["t"]}。（わかっている度 {x["stars"]}）', "url": h_url + "#" + x["slug"]}} for x in D]}])
    breakdown = "／".join(f"{'★' * k + '☆' * (3 - k)} {cnt[k]}件" for k in (3, 2, 1) if cnt[k])
    hayami_body = f"""{hayami_ld}
<p class="answer"><strong>{E(m["area"])}{n}件に、研究でわかったことと今日やることを1行ずつ並べました。</strong>悩みか「わかっている度」で絞り込めます。</p>
<p class="note">内訳：{breakdown}。★が少ないものは研究が少ないか結果が分かれていて、まだ言い切れない話です。</p>
<p class="flabel">悩みから</p><div class="fchips">{chips}</div>
<p class="flabel">わかっている度から</p><div class="fchips">{lchips}</div>
<p><a href="/check/" style="color:var(--link);font-weight:700">自分の悩みを選んで「今日やること」をまとめる（{E(m["check_title"])}）</a></p>
<h2>悩み別の一覧</h2>
<p id="cnt" class="note" aria-live="polite"></p>
<ul class="hyl">{"".join(hy(x) for x in D)}</ul>
<h2>この早見表について</h2>
<p>内容は、{E(cfg["name"])}で公開している記事（それぞれ論文などの出典を確認済み）から、結論・数字・今日やることを抜き出したものです。研究の多くは特定の国・年齢・立場の人が対象で、相関を調べたものも含みます。くわしい対象と限界は各記事の「まだわかっていないこと」に書いています。</p>
<p>「わかっている度」は、★★★が複数の研究やメタ分析で結果がそろっているもの、★★☆が研究はあるが数や条件が限られるもの、★☆☆が研究がほとんどないか結果が分かれているものです。</p>
{safe}
{FILTER_JS}"""
    hayami_page = {"path": "hayami", "title": m["hayami_title"], "seo_title": m["hayami_seo"].format(n=n), "date": date,
                   "desc": m["hayami_desc"].format(n=n), "body": hayami_body, "css": HAYAMI_CSS}

    # ---------- 悩みチェック /check/ ----------
    c_url = base + "check/"
    groups = "".join(
        f'<fieldset class="kg"><legend>{E(c["name"])}</legend>' + "".join(
            f'<label class="kq"><input type="checkbox" value="{x["slug"]}"><span>{E(x["worry"])}</span></label>' for x in D if x["cat"] == c["id"]) + "</fieldset>"
        for c in used)
    data = json.dumps({x["slug"]: {"w": x["worry"], "a": x["answer"], "s": x["stars"], "st": x["steps"][:2]} for x in D}, ensure_ascii=False).replace("</", "<\\/")
    ex = [x for x in D if x["slug"] in m["examples"]] or [next(x for x in D if x["cat"] == c["id"]) for c in used[:3]]
    ex_rows = "".join(f'<tr><td>{E(x["worry"])}</td><td>{E(x["steps"][0]["t"])}{"<br>" + E(x["steps"][0]["time"]) if x["steps"][0]["time"] else ""}</td></tr>' for x in ex)
    faq = [(m["diag_q"], m["diag_a"]),
           ("選んだ内容はどこかに送られますか？", "送られません。まとめる処理はすべてブラウザの中で行います。「この端末に保存」を押したときだけ、この端末の中（ブラウザ）に保存されます。"),
           ("いくつ選べばいいですか？", f"いくつでも選べますが、一度に始めるのは1〜2個がおすすめです。全{n}件の中から、いちばん気になるものを選んでください。")]
    check_ld = ld([
        {"@type": "WebApplication", "name": m["check_name"], "url": c_url, "applicationCategory": m["app_cat"],
         "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "description": m["check_desc"].format(n=n), "publisher": PUB},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}])
    check_body = f"""{check_ld}
<p>当てはまる悩みを選ぶと、研究にもとづく「今日やること」をまとめます。点数や診断は出しません。無料・広告なし・登録不要で、選んだ内容はどこにも送られません。</p>
<form id="kf" onsubmit="return false">{groups}
<div class="kbar"><button type="submit" id="kgo">今日やることをまとめる</button><span id="ksel" class="note" aria-live="polite">0件選択中</span></div>
</form>
<div id="kout" class="kout" aria-live="polite" hidden></div>
<p class="answer"><strong>まず1〜2個に絞り、すぐできることから始めます。</strong>悩みごとに、記事で出典を確認した方法だけを出します。</p>
<h2>しくみ</h2>
<p>選んだ悩みごとに、記事の「今日やること」から最初の2つを表示します。どれも、その記事で論文などの出典を確認した内容です（対象の記事は全{n}本）。研究の対象や限界は、それぞれの記事で確かめられます。</p>
<h2>結果の例</h2>
<table class="kt"><thead><tr><th>選んだ悩み</th><th>今日やること（1つ目）</th></tr></thead><tbody>{ex_rows}</tbody></table>
<p><a href="/hayami/" style="color:var(--link);font-weight:700">全{n}件を一覧で見る（研究早見表）</a></p>
<h2>よくある質問</h2>
{"".join(f'<details class="fq"{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(faq))}
{safe}
<script type="application/json" id="kd">{data}</script>
{CHECK_JS % (slug + "-check")}"""
    check_page = {"path": "check", "title": m["check_title"], "seo_title": m["check_seo"], "date": date,
                  "desc": m["check_desc"].format(n=n), "body": check_body, "css": CHECK_CSS}

    pf = ROOT / f"media/{slug}-pages.json"
    old = json.loads(pf.read_text()) if pf.exists() else []
    keep = [p for p in old if p["path"] not in ("check", "hayami")]
    pf.write_text(json.dumps(keep + [check_page, hayami_page], ensure_ascii=False, indent=2) + "\n")

    # 各記事の出典の直前に、早見表と悩みチェックへの案内を差し込む(再実行しても1つだけ)
    linked = 0
    for x in D:
        f = site / x["slug"] / "index.html"
        t = BLOCK.sub("", f.read_text())
        k = t.find('<div class="sources">')
        if k < 0:
            continue
        blk = (f'<!--ktools--><p style="margin:28px 0;padding:14px 18px;border:1px solid var(--accent);border-radius:12px;background:var(--card);font-size:15px;line-height:1.8">'
               f'<span style="font-size:12px;color:var(--muted)">無料ツール</span><br>'
               f'<a href="/check/" style="color:var(--link);font-weight:800">{E(m["check_link"])}</a><br>'
               f'<span style="font-size:13px;color:var(--muted)">当てはまる悩みを選ぶだけ。診断はせず、記事の対策を一覧にします。</span><br>'
               f'<a href="/hayami/#{x["slug"]}" style="color:var(--link);font-size:14px">研究早見表でほかの悩み{n - 1}件も見る</a></p><!--/ktools-->\n')
        f.write_text(t[:k] + blk + t[k:])
        linked += 1
    print(slug, "ok", n, "items,", linked, "articles linked", f"(posts {len(posts)})")


if __name__ == "__main__":
    for s in sys.argv[1:] or list(M):
        run(s)
