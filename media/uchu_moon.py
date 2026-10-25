#!/usr/bin/env python3
"""宇宙の研究の道具「もし月の距離が違ったら」(sites/uchu/moon-distance/index.html) を書き出す。
バーで月までの距離を変えると、潮の大きさ・1日の長さ・1か月の長さ・空の月の大きさと日食・満月の明るさ・地球の歴史でその距離だったころを計算して出す。
1日の長さは地球の自転と月の公転の角運動量の合計が変わらないとした計算（太陽の潮は入れない）。地層の記録（Williams 2000、Meyers & Malinverno 2018）と答え合わせする。
使い方: python3 media/uchu_moon.py （直したら実行して、build.py uchu も実行する）"""
import html, json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sites/uchu/moon-distance/index.html"
URL = "https://uchu.seadice.win/moon-distance/"
E = html.escape

# 数字（NASA NSSDC のファクトシート）
G, ME, MM, RE, RM = 6.674e-11, 5.9722e24, 7.346e22, 6.371e6, 1737.4e3
I = 0.3308 * ME * RE ** 2
D0, PERI, APO = 3.844e8, 3.633e8, 4.055e8
RS, DS = 695700e3, 1.496e11
SUN_TIDE = 0.5  # 太陽の潮を起こす力は月の約半分（NOAA）
DAY0 = 86164.1  # 今の自転1回（恒星日、秒）
M = ME + MM
MU = ME * MM / M
L = I * 2 * math.pi / DAY0 + MU * math.sqrt(G * M * D0)
REC = [(1.0, 0, "今"), (0.965, 6.2e8, "約6億2000万年前"), (340900e3 / D0, 1.4e9, "約14億年前")]  # 距離の比, 何年前, 表示


def calc(d):
    w = (L - MU * math.sqrt(G * M * d)) / I
    day = 2 * math.pi / w / 3600
    month = 2 * math.pi * math.sqrt(d ** 3 / (G * M)) / 86400
    syn = 1 / (1 / month - 1 / 365.256)
    k = (D0 / d) ** 3
    ang = math.degrees(2 * RM / d)
    sun = math.degrees(2 * RS / DS)
    return dict(day=day, month=month, syn=syn, tide=k, spring=(k + SUN_TIDE) / (1 + SUN_TIDE), ang=ang, r=ang / sun,
                bright=(D0 / d) ** 2)


def ecl(r):
    big, small = r * D0 / PERI, r * D0 / APO
    if small >= 1:
        return "皆既日食は起きうる（金環日食は起きない）"
    if big < 1:
        return "金環日食は起きうる（皆既日食は起きない）"
    return "皆既日食も金環日食も起きうる（今と同じ）"


PRESETS = [("今", D0), ("約6億2000万年前", 0.965 * D0), ("約14億年前", 340900e3), ("今の半分", D0 / 2), ("今の1.3倍", 1.3 * D0)]


def short(r):
    big, small = r * D0 / PERI, r * D0 / APO
    return "皆既だけ" if small >= 1 else "金環だけ" if big < 1 else "皆既も金環も"


def table():
    rows = []
    for name, d in PRESETS:
        c = calc(d)
        tide = "今と同じ" if abs(c["tide"] - 1) < 0.03 else f"今の{c['tide']:.2g}倍"
        rows.append(f"<tr><th>{name}<small>{round(d / 1e5) * 100:,} km</small></th><td>{c['day']:.1f}時間</td><td>{c['syn']:.1f}日</td>"
                    f"<td>{tide}</td><td>{short(c['r'])}</td></tr>")
    return "".join(rows)


FAQ = [
    ("月が近いと、なぜ1日が短くなるの？", "地球の自転と月の公転の「回る勢い（角運動量）」の合計は、ほぼ変わらないためです。月が近い（公転の勢いが小さい）ぶん、地球の自転が速くなります。今は潮の力で地球の自転の勢いが月の公転に移り、1日がのびて月が遠ざかっています。"),
    ("この計算は本当に合っているの？", "地層の記録（約6億2000万年前に21.9±0.4時間、約14億年前に18.68±0.25時間）と比べると、計算は22.0時間と18.6時間で、誤差の幅に入りました。ただし計算に入れた距離も同じ研究の見積もりなので、独立した確かめではなく「角運動量の考え方と記録が食い違わない」ことの確認です。太陽の潮や地球の形の変化は入れていないので、目安です。"),
    ("月がもっと遠くなるとどうなるの？", "今のしくみのままなら、月は少しずつ遠ざかり、いつか地球の1日と月の1か月が同じ長さになる所で止まると考えられています。この道具の計算では、約55万4000kmで約47日です。そこまでに何年かかるかは、遠ざかる速さが変わるため、この道具では出していません。"),
]


def main():
    sim = (ROOT / "sites/uchu/simulator/index.html").read_text()
    import re, readcheck
    css = re.search(r"<style>\n(:root\{.*?)/\*rc\*/", sim, re.S).group(1)
    cs = calc(D0)
    consts = json.dumps(dict(G=G, ME=ME, MM=MM, I=I, D0=D0, PERI=PERI, APO=APO, RM=RM, RS=RS, DS=DS, ST=SUN_TIDE, L=L, M=M, MU=MU,
                             REC=[[f, y] for f, y, _ in REC]))
    page = TEMPLATE
    for k, v in {"%%CSS%%": css + EXTRA_CSS + "/*rc*/" + readcheck.CSS + "/*/rc*/", "%%C%%": consts, "%%TABLE%%": table(),
                 "%%FAQ%%": "".join(f"<dt>{E(q)}</dt><dd>{E(a)}</dd>" for q, a in FAQ), "%%LD%%": json.dumps(ld(), ensure_ascii=False),
                 "%%DAY0%%": f"{cs['day']:.1f}"}.items():
        page = page.replace(k, v)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page)
    for name, d in PRESETS:
        c = calc(d)
        print(f"{name}: day {c['day']:.2f}h syn {c['syn']:.2f}d tide x{c['tide']:.2f} {ecl(c['r'])}")


DESC = "バーで月までの距離を変えると、潮の大きさ・1日の長さ・1か月の長さ・日食の起き方・満月から届く光の量が計算で出る道具。地層の記録とも答え合わせ。"


def ld():
    org = {"@id": "https://seadice.win/#organization"}
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": "もし月の距離が違ったら", "url": URL, "applicationCategory": "EducationalApplication", "operatingSystem": "Web",
         "inLanguage": "ja", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "description": DESC, "publisher": org, "dateModified": "2026-10-24"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "SEADICE", "item": "https://seadice.win/"},
            {"@type": "ListItem", "position": 2, "name": "宇宙の研究", "item": "https://uchu.seadice.win/"},
            {"@type": "ListItem", "position": 3, "name": "もし月の距離が違ったら", "item": URL}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}


EXTRA_CSS = (".grid>*{min-width:0}.tw{overflow-x:auto;-webkit-overflow-scrolling:touch}.tw table{min-width:440px}.tw th,.tw td{white-space:nowrap}.readout em{font-style:normal;font-size:14px;color:var(--muted)}"
             ".stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0}.stats div{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px 12px}"
             ".stats small{display:block;font-size:12px;color:var(--muted)}.stats b{display:block;font-size:17px;color:var(--accent);line-height:1.4}.stats em{display:block;font-style:normal;font-size:12px;color:var(--muted)}"
             ".stats .w{grid-column:1/-1}.sky{display:flex;gap:16px;align-items:center;justify-content:center;background:#05070C;border:1px solid var(--border);border-radius:8px;padding:16px;margin:8px 0}"
             ".sky figure{margin:0;text-align:center;font-size:12px;color:var(--muted)}.sky svg{display:block;margin:0 auto 4px}"
             ".pre{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.pre button{font-size:14px;min-height:44px;padding:6px 12px}"
             "table.cmp th small{display:block;font-size:12px;color:var(--muted);font-weight:400}.hist{border-left:4px solid var(--accent)}")

TEMPLATE = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>もし月の距離が違ったら｜潮・1日の長さ・日食を計算 | 宇宙の研究</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="description" content="''' + DESC + r'''">
<link rel="canonical" href="https://uchu.seadice.win/moon-distance/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="宇宙の研究">
<meta property="og:title" content="もし月の距離が違ったら｜潮・1日の長さ・日食を計算">
<meta property="og:description" content="月までの距離を変えると、潮・1日の長さ・日食がどう変わるかを計算。地層の記録で答え合わせ。登録なし・無料。">
<meta property="og:url" content="https://uchu.seadice.win/moon-distance/">
<meta property="og:image" content="https://seadice.win/icons/seadice_ogp.png">
<meta name="theme-color" content="#0A0E16">
<script type="application/ld+json">%%LD%%</script>
<style>
%%CSS%%</style>
</head>
<body>
<nav class="top"><div class="wrap"><a class="site" href="/">宇宙の研究</a><a href="/tools/">道具</a></div></nav>
<main class="wrap">
<ol class="crumb"><li><a href="https://seadice.win/">HOME</a></li><li><a href="/">宇宙の研究</a></li><li aria-current="page">もし月の距離が違ったら</li></ol>
<h1>もし月の距離が違ったら 潮・1日の長さ・日食の計算機</h1>
<p class="lead">月は今、地球から平均約38万4400km離れていて、毎年約3.8cmずつ遠ざかっています。バーで距離を変えると、<strong>潮の大きさ・1日の長さ・1か月の長さ・日食の起き方・満月の明るさ</strong>を計算します。昔の月がその距離だったころの地層の記録とも、答え合わせできます。</p>

<div class="grid">
<div>
<div class="readout"><span>月までの距離 <b id="dk">-</b> <em id="dr"></em></span></div>
<label for="slider" class="note">月までの距離（2万km〜55万km、目盛りは対数）</label>
<input type="range" id="slider" min="0" max="1000" step="1" value="0" aria-valuetext="">
<div class="stats">
<div><small>1日の長さ（自転1回＝恒星日）</small><b id="sDay">-</b><em>今は約%%DAY0%%時間</em></div>
<div><small>1か月（満月から満月）</small><b id="sMon">-</b><em>今は約29.5日</em></div>
<div><small>月が起こす潮の大きさ</small><b id="sTide">-</b><em id="sSpring"></em></div>
<div><small>満月から届く光の量</small><b id="sBr">-</b><em>距離の2乗に反比例（月面そのものの明るさは同じ）</em></div>
<div class="w"><small>空の月の大きさと日食</small><b id="sEcl">-</b><em id="sAng"></em></div>
</div>
<div class="pre" role="group" aria-label="よく使う距離">
<button type="button" data-d="384400">今</button><button type="button" data-d="370946">約6億2000万年前</button><button type="button" data-d="340900">約14億年前</button><button type="button" data-d="192200">今の半分</button><button type="button" data-d="499720">今の1.3倍</button>
</div>
<div class="sky" aria-hidden="true">
<figure><svg width="120" height="120" viewBox="-60 -60 120 120"><circle id="sun" r="20" fill="#E3B341"/></svg>太陽（大きさは同じ）</figure>
<figure><svg width="120" height="120" viewBox="-60 -60 120 120"><circle id="moon" r="20" fill="#C9CED6"/><circle id="sunring" r="20" fill="none" stroke="#E3B341" stroke-width="1" stroke-dasharray="3 3"/></svg>月（点線は太陽の大きさ）</figure>
</div>
<div class="card hist"><p class="note" style="margin:0 0 4px">地球の歴史で、月がこの距離だったころ</p><p id="hist" style="margin:0"></p></div>
</div>
<div class="side">
<h2 style="margin-top:0">よく使う距離の計算結果</h2>
<div class="card tw"><table class="cmp"><thead><tr><th>距離</th><th>1日</th><th>1か月</th><th>潮（月の分）</th><th>起きうる日食</th></tr></thead><tbody>%%TABLE%%</tbody></table>
<p class="note" style="margin:10px 0 0">地層の記録では、1日は約6億2000万年前に約21.9±0.4時間<a class="ref" href="#src-3">[3]</a>、約14億年前に約18.68±0.25時間<a class="ref" href="#src-4">[4]</a>。この計算（太陽の潮を入れない目安）は、記録の誤差の幅に入ります。ただし距離も同じ研究の見積もりを使っているので、独立した確かめではありません。</p></div>
<h2>計算のしかたと限界</h2>
<ul>
<li><b>1日の長さ</b>: 地球が1回自転する時間（恒星日、今は約23.9時間）です。ふだんの「1日24時間」は太陽が南に来てから次に来るまでで、約4分長くなります。地球の自転と月の公転の「回る勢い（角運動量）」の合計が変わらないとして計算しています。太陽の潮、地球の形や海の変化は入れていないので目安です。</li>
<li><b>1か月</b>: ケプラーの法則で月が1周する日数を出し、地球が太陽のまわりを回る分を足して、満月から満月までの日数にしています。</li>
<li><b>潮</b>: 潮を起こす力は距離の3乗に反比例します。太陽の潮の力は今の月の約半分としています<a class="ref" href="#src-5">[5]</a>。実際の潮の高さは、海岸の形でも大きく変わります。</li>
<li><b>日食</b>: 月の通り道は楕円なので、今と同じゆがみ方のまま距離だけ変えたとして、いちばん近いとき・遠いときの月の大きさを太陽と比べています。太陽の見かけの大きさの変化（約±1.7%）と、日食がどれくらいの頻度で起きるかは入れていません。</li>
<li><b>2万kmより近く</b>は、地球の潮の力で月が壊れると考えられる距離（流体のロッシュ限界、計算で約1万8000km）に近いので出していません。この計算では、約55万4000kmで地球の1日と月の1か月が約47日でそろい、それより先は計算が使えないので、55万kmまでにしています。そろう手前では、1日の長さが急にのびます。</li>
<li>「地球の歴史でこの距離だったころ」は、地層の記録がある2つの時点と今を結んだ目安です。記録より前のことは書いていません。</li>
</ul>
<h2>よくある質問</h2>
<dl class="faq">%%FAQ%%</dl>
</div>
</div>

<h2>関連する記事</h2>
<ul class="rel">
<li><a href="/moon-moving-away/">月は毎年3.8cm遠ざかっている、レーザーでわかったこと</a></li>
<li><a href="/if-moon-disappeared/">もし月がなかったら地球はどうなるのか</a></li>
<li><a href="/moon-origin/">月はどうやってできたのか、ジャイアント・インパクト説の証拠</a></li>
<li><a href="/eclipses/">日食と月食はなぜ起きるのか、次に日本で見られるのはいつ</a></li>
</ul>

<h2>出典</h2>
<ol class="src">
<li id="src-1">NASA NSSDC. Moon Fact Sheet（距離 38万4400km、近いとき 36万3300km、遠いとき 40万5500km、半径 1737.4km、重さ）. <a href="https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html" target="_blank" rel="noopener">nssdc.gsfc.nasa.gov</a></li>
<li id="src-2">NASA NSSDC. Earth Fact Sheet / Sun Fact Sheet（地球の重さ・半径・慣性モーメント 0.3308、太陽の半径 69万5700km）. <a href="https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html" target="_blank" rel="noopener">nssdc.gsfc.nasa.gov</a></li>
<li id="src-3">Williams, G. E. (2000). Geological constraints on the Precambrian history of Earth's rotation and the Moon's orbit. <i>Reviews of Geophysics</i>, 38, 37. <a href="https://doi.org/10.1029/1999RG900016" target="_blank" rel="noopener">doi:10.1029/1999RG900016</a></li>
<li id="src-4">Meyers, S. R., &amp; Malinverno, A. (2018). Proterozoic Milankovitch cycles and the history of the solar system. <i>PNAS</i>, 115, 6363. <a href="https://doi.org/10.1073/pnas.1717689115" target="_blank" rel="noopener">doi:10.1073/pnas.1717689115</a></li>
<li id="src-5">NOAA. Tides and Water Levels: What Causes Tides?（太陽の潮を起こす力は月の約半分）. <a href="https://oceanservice.noaa.gov/education/tutorial_tides/tides02_cause.html" target="_blank" rel="noopener">oceanservice.noaa.gov</a></li>
</ol>
<p class="note" style="margin-top:16px">最終更新: 2026年10月24日。入力は送らず、この画面の中だけで計算します。</p>
</main>
<footer><div class="wrap"><a href="/about/">このメディアについて</a> | <a href="/sources/">出典と検証の方法</a> | <a href="/disclaimer/">免責事項</a> | <a href="https://seadice.win/">SEADICE</a> | &copy; SEADICE</div></footer>
<script>
(function(){
var C=%%C%%,DMIN=2e7,DMAX=5.5e8,$=function(i){return document.getElementById(i)},sl=$('slider');
function dOf(p){return DMIN*Math.pow(DMAX/DMIN,p/1000)}
function pOf(d){return Math.round(1000*Math.log(d/DMIN)/Math.log(DMAX/DMIN))}
function f(x,n){return Number(x.toPrecision(n||2)).toLocaleString('ja-JP')}
function t(x){return Math.abs(x-1)<0.03?'今と同じ':'今の'+f(x,2)+'倍'}
function calc(d){var w=(C.L-C.MU*Math.sqrt(C.G*C.M*d))/C.I,day=2*Math.PI/w/3600,mon=2*Math.PI*Math.sqrt(d*d*d/(C.G*C.M))/86400,
 syn=1/(1/mon-1/365.256),k=Math.pow(C.D0/d,3),ang=2*C.RM/d,sun=2*C.RS/C.DS;return{day:day,syn:syn,k:k,r:ang/sun,ang:ang*180/Math.PI,br:Math.pow(C.D0/d,2)}}
function ecl(r){var big=r*C.D0/C.PERI,small=r*C.D0/C.APO;if(small>=1)return '皆既日食は起きうるが、金環日食は起きない';if(big<1)return '金環日食は起きうるが、皆既日食は起きない';return '皆既日食も金環日食も起きうる（今と同じ）'}
function hist(d){var x=d/C.D0,k=Math.round(d/1e5)*100;
 if(Math.abs(x-1)<0.002)return '今の月の距離です。今は毎年約3.8cmずつ遠ざかっています。';
 if(x>1)return '今より遠い、未来の距離です。今は年約3.8cmずつ遠ざかっていますが、その速さは時代によって変わってきたので、何年後にこの距離になるかは出していません。';
 var s='地層の記録は2点だけです（約6億2000万年前に今の約0.965倍＝約37万1000km、約14億年前に約34万900km）。';
 if(x>=0.965)return s+'この距離は、今と約6億2000万年前の記録のあいだです。';
 if(x>=340900e3/C.D0)return s+'この距離は、約6億2000万年前と約14億年前の記録のあいだです。';
 return s+'この距離は14億年前の記録より近く、記録はありません。月ができたころ（約45億年前）はもっと近かったと考えられています。'}
function show(d){var c=calc(d);$('dk').textContent=(Math.round(d/1e5)*100).toLocaleString('ja-JP')+' km';$('dr').textContent=Math.abs(d/C.D0-1)<0.002?'（今の距離）':'（今の'+f(d/C.D0,3)+'倍）';
 $('sDay').textContent=c.day>48?'約'+(c.day/24).toFixed(1)+'日（'+Math.round(c.day)+'時間）':'約'+c.day.toFixed(1)+'時間';$('sMon').textContent=c.syn<2?'約'+(c.syn*24).toFixed(1)+'時間':'約'+c.syn.toFixed(1)+'日';
 $('sTide').textContent=t(c.k);var sp=(c.k+C.ST)/(1+C.ST);$('sSpring').textContent='大潮（月と太陽が並ぶとき）の目安は'+t(sp).replace('今の','今の約')+(c.k<C.ST?'。太陽の潮のほうが大きい':'');
 $('sBr').textContent=t(c.br);$('sEcl').textContent=ecl(c.r);$('sAng').textContent='空の月の大きさは平均で約'+c.ang.toFixed(2)+'度（太陽は約0.53度）';
 var rm=Math.min(56,20*c.r);$('moon').setAttribute('r',rm.toFixed(1));$('hist').textContent=hist(d);
 sl.setAttribute('aria-valuetext',(Math.round(d/1e5)*100)+'キロメートル、1日 約'+c.day.toFixed(1)+'時間、潮 '+t(c.k)+'、'+ecl(c.r))}
sl.oninput=function(){show(dOf(+sl.value))};
[].forEach.call(document.querySelectorAll('.pre button'),function(b){b.onclick=function(){var d=+b.getAttribute('data-d')*1e3;sl.value=pOf(d);show(d)}});
sl.value=pOf(C.D0);show(C.D0);
})();
</script>
</body>
</html>
'''

if __name__ == "__main__":
    main()
