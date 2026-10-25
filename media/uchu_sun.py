#!/usr/bin/env python3
"""宇宙の研究の道具「もし太陽の明るさが違ったら」(sites/uchu/sun-brightness/index.html) を書き出す。
バーで太陽の明るさを変えると、地球に届く光・地球の温度の目安・生き物が住める範囲（ハビタブルゾーン、Kopparapu 2013 の太陽系の値）を出し、
金星・地球・火星がその範囲に入るかを図で見せる。若い太陽の時代は「暗い太陽のパラドックス」（Feulner 2012）として、わかっていないことを書く。
使い方: python3 media/uchu_sun.py （直したら実行して、build.py uchu も実行する）"""
import html, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sites/uchu/sun-brightness/index.html"
URL = "https://uchu.seadice.win/sun-brightness/"
E = html.escape

TBB, TAVG = 254.0, 288.0  # 地球の黒体温度と平均気温（K、NASA Earth Fact Sheet）
HZ_IN, HZ_OUT = 0.99, 1.70  # 今の太陽での内側（水を失う）・外側（温室効果の最大）の限界（AU、Kopparapu 2013）
PLANETS = [("金星", 0.723), ("地球", 1.0), ("火星", 1.524)]  # 太陽からの平均距離（AU、NASA）
PRESETS = [("生まれたころ（約75%）", 0.75), ("今", 1.0), ("約10億年後（約1.1倍）", 1.1), ("今の0.5倍", 0.5), ("今の2倍", 2.0)]


def calc(l):
    tbb = TBB * l ** 0.25
    return dict(tbb=tbb, tg=TAVG + (tbb - TBB), hin=HZ_IN * l ** 0.5, hout=HZ_OUT * l ** 0.5)


def where(d, c):
    return "住める範囲の内側（太陽に近すぎる）" if d < c["hin"] else "住める範囲の外側（遠すぎる）" if d > c["hout"] else "住める範囲の中"


def table():
    rows = []
    for name, l in PRESETS:
        c = calc(l)
        rows.append(f"<tr><th>{name}</th><td>{c['tbb'] - 273.15:.0f}℃</td><td>{c['hin']:.2f}〜{c['hout']:.2f}</td>"
                    f"<td>{where(1.0, c).replace('住める範囲の内側（太陽に近すぎる）', '近すぎる側に外れる').replace('住める範囲の外側（遠すぎる）', '遠すぎる側に外れる').replace('住める範囲の中', '範囲の中')}</td></tr>")
    return "".join(rows)


FAQ = [
    ("太陽が明るくなると、地球はいつ住めなくなるの？", "太陽は少しずつ明るくなっていて、約10億年後には地球が生き物の住めない暑さになると見積もられています。この道具の範囲（Kopparapu 2013）では、今の地球は住める範囲の内側の端の近くにあり、太陽が今より約2%明るくなると、水を失い始める限界を越える計算です。ただしこれは雲を入れない控えめな計算の境目で、実際にいつ住めなくなるかの見積もり（約10億年後）とは別のものです。雲の効果などで、実際の限界はもっと外にある可能性があります。"),
    ("温度の目安はどうやって出しているの？", "地球が太陽の光を受けて温まり、宇宙へ熱を出してつり合う温度（黒体温度、今は約−19℃）を、届く光の4乗根に比例させて出しています。地面の目安は、今の温室効果の上乗せ（約34度）を変えないとした、とても粗い値です。本当は水蒸気・雲・氷の量が変わるので、大きくずれます。"),
    ("暗い太陽のパラドックスとは？", "生まれたころの太陽は今より暗く、地球に届く光は約25%少なかったと考えられています。ほかの条件が今と同じなら地球は凍っていたはずですが、38億〜25億年前に液体の水や生き物がいた証拠があります。温室効果ガスが多かったなどの説がありますが、決着していません。"),
]

DESC = "バーで太陽の明るさを変えると、地球に届く光・地球の温度の目安・生き物が住める範囲（ハビタブルゾーン）がどう動くかを計算する道具。金星・地球・火星が範囲に入るかを図で見る。"


def ld():
    org = {"@id": "https://seadice.win/#organization"}
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": "もし太陽の明るさが違ったら", "url": URL, "applicationCategory": "EducationalApplication", "operatingSystem": "Web",
         "inLanguage": "ja", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "description": DESC, "publisher": org, "dateModified": "2026-10-25"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "SEADICE", "item": "https://seadice.win/"},
            {"@type": "ListItem", "position": 2, "name": "宇宙の研究", "item": "https://uchu.seadice.win/"},
            {"@type": "ListItem", "position": 3, "name": "もし太陽の明るさが違ったら", "item": URL}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}


EXTRA_CSS = (".grid>*{min-width:0}.tw{overflow-x:auto;-webkit-overflow-scrolling:touch}.tw table{min-width:440px}.tw th,.tw td{white-space:nowrap}.readout em{font-style:normal;font-size:14px;color:var(--muted)}"
             ".stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0}.stats div{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px 12px}"
             ".stats small{display:block;font-size:12px;color:var(--muted)}.stats b{display:block;font-size:17px;color:var(--accent);line-height:1.4}.stats em{display:block;font-style:normal;font-size:12px;color:var(--muted)}"
             ".stats .w{grid-column:1/-1}.map{background:#05070C;border:1px solid var(--border);border-radius:8px;padding:12px;margin:8px 0}.map svg{display:block;width:100%;height:auto}"
             ".pre{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.pre button{font-size:14px;min-height:44px;padding:6px 12px}.note2{border-left:4px solid var(--accent)}")


def main():
    import re, readcheck
    sim = (ROOT / "sites/uchu/simulator/index.html").read_text()
    css = re.search(r"<style>\n(:root\{.*?)/\*rc\*/", sim, re.S).group(1)
    consts = json.dumps(dict(TBB=TBB, TAVG=TAVG, HI=HZ_IN, HO=HZ_OUT, P=PLANETS), ensure_ascii=False)
    pre = "".join(f'<button type="button" data-l="{l}">{E(n)}</button>' for n, l in PRESETS)
    page = TEMPLATE
    for k, v in {"%%CSS%%": css + EXTRA_CSS + "/*rc*/" + readcheck.CSS + "/*/rc*/", "%%C%%": consts, "%%TABLE%%": table(), "%%PRE%%": pre,
                 "%%FAQ%%": "".join(f"<dt>{E(q)}</dt><dd>{E(a)}</dd>" for q, a in FAQ), "%%LD%%": json.dumps(ld(), ensure_ascii=False)}.items():
        page = page.replace(k, v)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page)
    for n, l in PRESETS:
        c = calc(l)
        print(f"{n}: Tbb {c['tbb'] - 273.15:.1f}C ground~{c['tg'] - 273.15:.1f}C HZ {c['hin']:.2f}-{c['hout']:.2f} Earth {where(1, c)}")


TEMPLATE = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>もし太陽の明るさが違ったら｜地球の温度と住める範囲を計算 | 宇宙の研究</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="description" content="''' + DESC + r'''">
<link rel="canonical" href="https://uchu.seadice.win/sun-brightness/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="宇宙の研究">
<meta property="og:title" content="もし太陽の明るさが違ったら｜地球の温度と住める範囲を計算">
<meta property="og:description" content="太陽の明るさを変えると、地球の温度の目安と生き物が住める範囲がどう動くかを計算。登録なし・無料。">
<meta property="og:url" content="https://uchu.seadice.win/sun-brightness/">
<meta property="og:image" content="https://seadice.win/icons/seadice_ogp.png">
<meta name="theme-color" content="#0A0E16">
<script type="application/ld+json">%%LD%%</script>
<style>
%%CSS%%</style>
</head>
<body>
<nav class="top"><div class="wrap"><a class="site" href="/">宇宙の研究</a><a href="/tools/">道具</a></div></nav>
<main class="wrap">
<ol class="crumb"><li><a href="https://seadice.win/">HOME</a></li><li><a href="/">宇宙の研究</a></li><li aria-current="page">もし太陽の明るさが違ったら</li></ol>
<h1>もし太陽の明るさが違ったら 地球の温度と住める範囲の計算機</h1>
<p class="lead">太陽は生まれてから少しずつ明るくなっていて、これからも明るくなります。バーで太陽の明るさを変えると、<strong>地球に届く光・地球の温度の目安・生き物が住める範囲（ハビタブルゾーン）</strong>がどう動くかを計算し、金星・地球・火星がその範囲に入るかを図で見せます。今の地球は、住める範囲の内側の端の近くにいます。</p>

<div class="grid">
<div>
<div class="readout"><span>太陽の明るさ <b id="lv">-</b> <em id="lr"></em></span></div>
<label for="slider" class="note">太陽の明るさ（今の0.3倍〜2倍、目盛りは対数）</label>
<input type="range" id="slider" min="0" max="1000" step="1" value="0" aria-valuetext="">
<div class="stats">
<div><small>地球に届く太陽の光</small><b id="sF">-</b><em>明るさに比例</em></div>
<div><small>地球の黒体温度</small><b id="sT">-</b><em>今は約−19℃</em></div>
<div class="w"><small>地面の温度のごく粗い目安（温室効果を今のままとした場合）</small><b id="sG">-</b><em>今の平均は約15℃。水蒸気・雲・氷が変わるので大きくずれます</em></div>
<div class="w"><small>生き物が住める範囲（太陽からの距離）</small><b id="sH">-</b><em id="sP"></em></div>
</div>
<div class="map"><svg id="map" viewBox="0 0 360 110" role="img" aria-label="太陽からの距離と、生き物が住める範囲"></svg><p class="note" style="margin:6px 0 0">緑の帯が生き物が住める範囲（計算の目安）。目盛りは太陽からの距離（天文単位、1＝今の地球と太陽の距離）。</p></div>
<div class="pre" role="group" aria-label="よく使う明るさ">%%PRE%%</div>
<div class="card note2"><p id="msg" style="margin:0"></p></div>
</div>
<div class="side">
<h2 style="margin-top:0">よく使う明るさの計算結果</h2>
<div class="card tw"><table><thead><tr><th>太陽の明るさ</th><th>黒体温度</th><th>住める範囲（天文単位）</th><th>地球の位置</th></tr></thead><tbody>%%TABLE%%</tbody></table><p class="note" style="margin:10px 0 0">住める範囲は「温室効果が必要なだけ強まる」とした計算で、黒体温度は温室効果を入れない値です。そのため、暗い太陽では「範囲の中なのに寒い」という食い違いが出ます。生まれたころの太陽でのこの食い違いが、まだ解けていない「暗い太陽のパラドックス」です<a class="ref" href="#src-3">[3]</a>。範囲の境目は雲を入れない控えめな計算なので、「外れる」は「住めなくなる時期」を表すものではありません。</p></div>
<h2>計算のしかたと限界</h2>
<ul>
<li><b>住める範囲</b>: Kopparapu ほか（2013）の太陽系での値（内側は水を失い始める0.99天文単位、外側は二酸化炭素の温室効果で温められる限界の1.70天文単位）を、太陽の明るさの平方根に比例させて動かしています<a class="ref" href="#src-1">[1]</a>。この範囲は「二酸化炭素などの温室効果が、海が凍らないよう必要なだけ強まる」とした計算なので、温室効果を今のままとした「地面の目安」とは食い違うことがあります。この計算は雲を入れていないので、実際の範囲は両側にもう少し広がる可能性があると論文自身が書いています。太陽の色（表面温度）は今と同じとしています。</li>
<li><b>黒体温度</b>: 地球が受けた光と宇宙へ出す熱がつり合う温度です。今は約254K（約−19℃）で<a class="ref" href="#src-2">[2]</a>、届く光の4乗根に比例させています。地球の白さ（反射率）は今と同じとしています。</li>
<li><b>地面の目安</b>: 今の平均気温（約288K、15℃）と黒体温度の差（約34度）を温室効果の上乗せとして足しただけの、とても粗い値です。</li>
<li>惑星の距離は今の平均の値です<a class="ref" href="#src-2">[2]</a>。</li>
</ul>
<h2>よくある質問</h2>
<dl class="faq">%%FAQ%%</dl>
</div>
</div>

<h2>関連する記事</h2>
<ul class="rel">
<li><a href="/sun-future/">太陽はいつか消えるのか、50億年後の太陽と地球</a></li>
<li><a href="/earth-like-planets/">地球に似た惑星は見つかっているのか、ハビタブルゾーンとは</a></li>
<li><a href="/venus-hot/">金星はなぜ地球より熱いのか、温室効果が暴走した星</a></li>
<li><a href="/mars-water/">火星に水はあったのか、探査機が見つけた証拠</a></li>
</ul>

<h2>出典</h2>
<ol class="src">
<li id="src-1">Kopparapu, R. K., et al. (2013). Habitable Zones around Main-sequence Stars: New Estimates. <i>The Astrophysical Journal</i>, 765, 131. <a href="https://doi.org/10.1088/0004-637X/765/2/131" target="_blank" rel="noopener">doi:10.1088/0004-637X/765/2/131</a></li>
<li id="src-2">NASA NSSDC. Earth Fact Sheet / Planetary Fact Sheet（地球の黒体温度 254K・平均気温 288K、惑星の距離）. <a href="https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html" target="_blank" rel="noopener">nssdc.gsfc.nasa.gov</a></li>
<li id="src-3">Feulner, G. (2012). The faint young Sun problem. <i>Reviews of Geophysics</i>, 50, RG2006. <a href="https://doi.org/10.1029/2011RG000375" target="_blank" rel="noopener">doi:10.1029/2011RG000375</a></li>
<li id="src-4">Schröder, K.-P., &amp; Smith, R. C. (2008). Distant future of the Sun and Earth revisited. <i>Monthly Notices of the Royal Astronomical Society</i>, 386, 155. <a href="https://doi.org/10.1111/j.1365-2966.2008.13022.x" target="_blank" rel="noopener">doi:10.1111/j.1365-2966.2008.13022.x</a></li>
</ol>
<p class="note" style="margin-top:16px">最終更新: 2026年10月25日。入力は送らず、この画面の中だけで計算します。</p>
</main>
<footer><div class="wrap"><a href="/about/">このメディアについて</a> | <a href="/sources/">出典と検証の方法</a> | <a href="/disclaimer/">免責事項</a> | <a href="https://seadice.win/">SEADICE</a> | &copy; SEADICE</div></footer>
<script>
(function(){
var C=%%C%%,LMIN=0.3,LMAX=2,$=function(i){return document.getElementById(i)},sl=$('slider');
function lOf(p){return LMIN*Math.pow(LMAX/LMIN,p/1000)}
function pOf(l){return Math.round(1000*Math.log(l/LMIN)/Math.log(LMAX/LMIN))}
function c2(k){var c=k-273.15;return (c<0?'−':'')+Math.abs(c).toFixed(0)+'℃'}
function where(d,i,o){return d<i?'内側（近すぎる）':d>o?'外側（遠すぎる）':'範囲の中'}
var X=function(au){return 16+au/3*328};
function draw(i,o){var s='<line x1="16" y1="70" x2="344" y2="70" stroke="#26324A"/>';
 for(var a=0;a<=3;a+=1)s+='<line x1="'+X(a)+'" y1="66" x2="'+X(a)+'" y2="74" stroke="#26324A"/><text x="'+X(a)+'" y="92" fill="#A1ACBE" font-size="15" text-anchor="middle">'+a+'</text>';
 var x1=X(Math.min(i,3)),x2=X(Math.min(o,3));if(i<3)s+='<rect x="'+x1+'" y="54" width="'+Math.max(2,x2-x1)+'" height="32" fill="#8FD1A8" opacity=".35"/>';
 s+='<circle cx="'+X(0)+'" cy="70" r="9" fill="#E3B341"/>';
 C.P.forEach(function(p,k){var cx=X(p[1]);s+='<circle cx="'+cx+'" cy="70" r="5" fill="'+(k==1?'#7FB2E5':'#E9EDF3')+'"/><text x="'+cx+'" y="'+(k==1?30:48)+'" fill="#E9EDF3" font-size="16" text-anchor="middle">'+p[0]+'</text>'});
 $('map').innerHTML=s}
function show(l){var tbb=C.TBB*Math.pow(l,0.25),tg=C.TAVG+(tbb-C.TBB),i=C.HI*Math.sqrt(l),o=C.HO*Math.sqrt(l);
 $('lv').textContent='今の'+(Math.abs(l-1)<0.005?'1':l.toFixed(2))+'倍';$('lr').textContent=Math.abs(l-1)<0.005?'（今の太陽）':'';
 $('sF').textContent=Math.abs(l-1)<0.005?'今と同じ':'今の'+l.toFixed(2)+'倍';$('sT').textContent='約'+c2(tbb);$('sG').textContent='約'+c2(tg);
 $('sH').textContent=i.toFixed(2)+'〜'+o.toFixed(2)+' 天文単位';
 $('sP').textContent=C.P.map(function(p){return p[0]+': '+where(p[1],i,o)}).join(' ／ ');draw(i,o);
 var m;if(l>=0.65&&l<0.85)m='このくらい暗い太陽は、生まれたころの太陽に近い明るさです（地球に届く光は約25%少なかったと考えられています）。ほかの条件が今と同じなら地球は凍っていたはずですが、38億〜25億年前にも液体の水や生き物がいた証拠があります。温室効果ガスが多かったなどの説があり、まだ決着していません（暗い太陽のパラドックス）<a class="ref" href="#src-3">[3]</a>。';
 else if(1<i)m='この明るさでは、地球は住める範囲から、太陽に近すぎる側に外れます。雲を入れない控えめな計算では、海の水が空へ逃げ始める条件です。太陽は今も少しずつ明るくなっていて、約10億年後には地球が生き物の住めない暑さになると見積もられています<a class="ref" href="#src-4">[4]</a>。雲の効果などで、実際の限界はずれる可能性があります。';
 else if(o<1)m='この明るさでは、地球は住める範囲の外側に出ます。二酸化炭素の温室効果をいちばん強くしても、海が凍らずにいられない計算です。';
 else m=Math.abs(l-1)<0.005?'地球は住める範囲の中です。今の地球（1天文単位）は、内側の端（0.99天文単位）のすぐそばにいます。':'地球は住める範囲の中です。ただしこの範囲は、二酸化炭素などの温室効果が必要なだけ強まるとした計算です。温室効果が今のままなら、上の「地面の目安」のように'+(l<1?'寒く':'暑く')+'なります。';
 $('msg').innerHTML=m;sl.setAttribute('aria-valuetext','今の'+l.toFixed(2)+'倍の明るさ、地球は'+where(1,i,o))}
sl.oninput=function(){show(lOf(+sl.value))};
[].forEach.call(document.querySelectorAll('.pre button'),function(b){b.onclick=function(){var l=+b.getAttribute('data-l');sl.value=pOf(l);show(l)}});
sl.value=pOf(1);show(1);
})();
</script>
</body>
</html>
'''

if __name__ == "__main__":
    main()
