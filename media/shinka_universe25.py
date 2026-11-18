"""進化の研究の道具 /universe-25-sim/（ユニバース25の記録と、単純な増え方の式を重ねて見る）を
media/shinka-pages.json に書き出す。ほかの固定ページ（/split/ など）は残す。

数字の出典: Calhoun JB (1973) Proc R Soc Med 66(1 Pt 2):80-88（2026-11-12 に本文と図2で照合）。
図2から目で読んだ点は「推定」として白丸で出す。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = "universe-25-sim"
TITLE = "ユニバース25の記録と、増え方の式を比べる"

# [日目, 数, 1=本文・図の書き込みで確かめた値 / 0=図2から読み取った推定]
REC = [[0, 8, 1], [104, 8, 1], [315, 620, 1], [560, 2200, 1], [736, 2056, 0], [800, 2000, 0], [900, 1900, 0],
       [960, 1700, 0], [1020, 1600, 0], [1210, 730, 0], [1270, 530, 0], [1331, 360, 0], [1444, 122, 1],
       [1471, 100, 1], [1588, 27, 1]]
EV = [[0, "1968年7月9日、4組（8匹）を囲いに入れる", "k"], [104, "最初の子が生まれる", "k"],
      [315, "620匹。ここから増え方が遅くなる", "k"], [560, "2,200匹で増えるのが止まる", "k"],
      [600, "最後に子が離乳まで育つ", "k"], [920, "このころが最後の妊娠", "k"],
      [1444, "1972年6月22日、122匹（オス22・メス100）", "k"],
      [1588, "1972年11月13日、27匹（メス23・オス4）。論文の記録はここまで", "k"],
      [1780, "論文の予測: 最後のオスが死ぬ（実際の日は確かめられていない）", "p"]]

BODY = """<p class="xlead">1968年にカルフーンが行ったマウスの実験「ユニバース25」の記録の点に、単純な式の線を重ねます。式に「子が育たなくなる日」を入れると、そのあとは年をとって死ぬだけでも数は減っていきます。けれど式は、記録のように2,200匹で増えるのを止めることはできません。なぜ増えるのが止まり、子が育たなくなったのか。そこが、この実験でまだわかっていないことです。</p>
<div class="tl"><div class="sd-tool" id="u25">
<div class="lg" aria-hidden="true"><span><i class="m k"></i>記録（確か）</span><span><i class="m e"></i>図から読んだ値（推定）</span><span><i class="m p"></i>論文時点の予測</span><span><i class="m s"></i>式（作り物）</span></div>
<svg id="ch" viewBox="0 0 640 382" role="img" aria-labelledby="cht chd"><title id="cht">ユニバース25の個体数の記録と、式の線のグラフ</title><desc id="chd">記録は点で、8匹から560日目に2,200匹まで増え、1588日目に27匹まで減った。式の線は破線で、下の条件で変わる。</desc></svg>
<div class="ctl">
<label class="tl2" for="dy">日を選ぶ <output id="dyo"></output></label><input type="range" id="dy" min="0" max="1780" step="1" value="560">
<div class="ev" id="ev" aria-live="polite"></div>
</div>
<div class="ctl"><p class="tl2">式の条件を変える</p>
<label for="k">環境収容力K（巣箱でゆとりをもって休める数） <output id="ko"></output></label><input type="range" id="k" min="500" max="8000" step="20" value="3840">
<label for="d">数が倍になる日数（増える速さ） <output id="do"></output></label><input type="range" id="d" min="20" max="200" step="1" value="33">
<label for="s">子が育たなくなる日 <output id="so"></output></label><input type="range" id="s" min="200" max="1800" step="10" value="600">
<label for="l">寿命のめやす <output id="lo"></output></label><input type="range" id="l" min="500" max="1100" step="10" value="800">
<button type="button" class="pk" id="rs">はじめの値に戻す</button>
</div>
<div class="out" id="out" aria-live="polite"><p class="o1" id="o1"></p><p class="o2" id="o2"></p></div>
<p class="sv">スライダーの値は、次に開いたときのために、この端末のブラウザにだけ保存します。</p>
</div></div>
<noscript><p class="note">この道具はJavaScriptで動きます。</p></noscript>
<h2 class="sec">この式の仮定</h2>
<p class="t">破線は、生き物の数の教科書に出る「ロジスティック式」に、寿命を足したものです。<strong>実験を再現したものではありません。</strong>次のことだけを決めて計算しています。</p>
<ul class="as"><li>104日目から子が生まれ始める（記録どおり）</li><li>はじめは決まった日数で倍に増え、環境収容力Kに近づくほど増え方が遅くなる</li><li>「子が育たなくなる日」から後は、子が増えない。<strong>この日は式が出すのではなく、人が決めて入れる</strong></li><li>寿命のめやすの前後200日のあいだに、少しずつ死ぬ（仮の形）</li><li>けんか・病気・群れの中の役割・オスとメスの違いは入れていない。外へは出ていけない（実験と同じ）</li></ul>
<p class="t">論文の本文は「増え始めは約55日で倍、315日目からは約145日で倍」と書いています<span class="ref">[1]</span>。ただ、104日目の8匹が315日目に620匹になるには、約33日で倍の計算になり、本文の数字と記録の点はそろっていません。この道具は、記録の点に近い33日をはじめの値にしています。</p>
<p class="t">寿命のめやすは、論文の「多くのマウスが800日（人なら80歳にあたる）まで生きた」をもとにしました<span class="ref">[1]</span>。死に方の形（前後200日でだんだん死ぬ）は仮のもので、形を変えれば減り方も変わります。</p>
<h2 class="sec">確かなこと・推定・わからないこと</h2>
<div class="kk"><div><p class="lv k">確か</p><p>4組から始め、560日目に2,200匹で増えるのが止まった。600日目を最後に子が育たなくなり、1972年11月の時点で27匹だった<span class="ref">[1]</span>。</p></div>
<div><p class="lv h">推定</p><p>白丸の値は、論文のグラフから目で読み取ったものと、736日目の書き込み（実測と見込みの線の境目にあり、どちらか断定できない）。1000日目より後は、別の研究のために約150匹を取り出したため、少し低く出ていると論文の図の説明にある<span class="ref">[1]</span>。</p></div>
<div><p class="lv u">わからない</p><p>なぜゆとりをもって休める数の約57%で増えるのが止まり、子が育たなくなったのか。カルフーンは社会の中の役割の不足と考えたが、1回の観察なので確かめられていない。人にどこまで当てはまるかも、わかっていない<span class="ref">[2]</span>。</p></div></div>
<h2 class="sec">授業で使うなら</h2>
<ol class="as"><li>「子が育たなくなる日」をいちばん右（止まらない）にすると、線はどうなる？ 600日目にすると？</li><li>減り方が式でも出せるなら、この実験で本当にわからないのは何？</li><li>巣箱でゆとりをもって休める数は3,840匹なのに、記録は2,200匹で止まった。この記録から言えることと、言えないことは？</li></ol>
<p class="t">記録の読み方と、人への当てはめをめぐる研究は<a href="/universe-25/">「ユニバース25は本当？」</a>に書きました。</p>
<h2 class="sec">出典</h2>
<ol class="src"><li>Calhoun JB (1973). Death Squared: The Explosive Growth and Demise of a Mouse Population. Proceedings of the Royal Society of Medicine 66(1 Pt 2): 80-88. <a href="https://doi.org/10.1177/00359157730661P202" rel="noopener">https://doi.org/10.1177/00359157730661P202</a>（本文と図2で、2026年11月12日に照合）</li>
<li>Ramsden E (2009). The urban animal: population density and social pathology in rodents and humans. Bulletin of the World Health Organization 87(2): 82. <a href="https://doi.org/10.2471/BLT.09.062836" rel="noopener">https://doi.org/10.2471/BLT.09.062836</a></li></ol>
<script>(function(){var REC=__REC__,EV=__EV__;
var q=function(i){return document.getElementById(i);},NS="http://www.w3.org/2000/svg",svg=q("ch");
var X0=48,X1=620,Y0=320,Y1=24,TMAX=1800,W=640,NW=false,IDS=["k","d","s","l","dy"],DEF={k:3840,d:33,s:600,l:800};
function fx(t){return X0+(X1-X0)*t/TMAX;}
function el(n,a,p){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);(p||svg).appendChild(e);return e;}
function tx(x,y,s,c,a){var e=el("text",{x:x,y:y,"class":c||"ax","text-anchor":a||"start"});e.textContent=s;return e;}
function fmt(v){return Math.round(v).toLocaleString("ja-JP");}
function sv(a,L){var lo=L-200;return a<lo?1:a>L+200?0:1-(a-lo)/400;}
function model(K,D,S,L){var r=Math.LN2/D,B=new Float64Array(TMAX+1),N=new Float64Array(TMAX+1),lo=L-200,full=0;
for(var t=0;t<=TMAX;t++){if(t-1>=104)full+=B[t-1];if(t-lo>=104&&t-lo<t)full-=B[t-lo];var n=8*sv(t+48,L)+full;
for(var u=Math.max(104,t-L-200);u<=t-lo&&u<t;u++)n+=B[u]*sv(t-u,L);N[t]=n;
if(t>=104&&t<S)B[t]=Math.max(0,r*n*(1-n/K));}return N;}
function last(day){var p=null;REC.forEach(function(x){if(x[0]<=day)p=x;});return p;}
function size(){W=Math.round(Math.min(640,Math.max(320,svg.clientWidth||640)));NW=W<520;X1=W-16;Y0=NW?250:320;svg.setAttribute("viewBox","0 0 "+W+" "+(Y0+(NW?78:62)));}
function draw(){size();var K=+q("k").value,D=+q("d").value,S=+q("s").value,L=+q("l").value,day=+q("dy").value,ST=S>=1800;
q("ko").textContent=fmt(K)+"匹";q("do").textContent=D+"日";q("so").textContent=ST?"止まらない":S+"日目";q("lo").textContent=L+"日";q("dyo").textContent=day+"日目";
var N=model(K,D,ST?1e9:S,L),mx=0;for(var i=0;i<=TMAX;i++)if(N[i]>mx)mx=N[i];
var YM=Math.max(4000,Math.ceil(Math.max(K,mx)*1.08/1000)*1000);function fy(v){return Y0-(Y0-Y1)*v/YM;}
while(svg.lastChild&&svg.lastChild.nodeName!=="desc"&&svg.lastChild.nodeName!=="title")svg.removeChild(svg.lastChild);
for(var v=0;v<=YM;v+=(YM>4000?2000:1000)){el("line",{x1:X0,x2:X1,y1:fy(v),y2:fy(v),"class":"gr"});tx(X0-6,fy(v)+4,fmt(v),"ax","end");}
for(var t=0;t<=TMAX;t+=(NW?600:300)){tx(fx(t),Y0+18,t+"日","ax",t>=TMAX?"end":"middle");}
el("line",{x1:X0,x2:X1,y1:fy(K),y2:fy(K),"class":"cap"});tx(X1,fy(K)-6,"K "+fmt(K)+"匹","ax","end");
var pm="";for(var t2=0;t2<=TMAX;t2+=4){pm+=(t2?"L":"M")+fx(t2).toFixed(1)+" "+fy(N[t2]).toFixed(1);}el("path",{d:pm,"class":"ms"});
var lt=ST?TMAX-10:Math.min(TMAX-10,S+120);tx(fx(lt),fy(N[lt])-10,"式（作り物）","lb2",ST?"end":"start");
el("path",{d:"M"+fx(1588)+" "+fy(27)+"L"+fx(1780)+" "+fy(0),"class":"pl"});
REC.forEach(function(p){el("circle",{cx:fx(p[0]),cy:fy(p[1]),r:p[2]?4.5:4,"class":p[2]?"dk":"de"});});
tx(fx(560)-10,fy(2200)-8,"記録","lb1","end");
el("line",{x1:fx(day),x2:fx(day),y1:Y1,y2:Y0,"class":"cur"});
(NW?["記録: Calhoun 1973（白丸は図から読んだ推定）","破線は式で、実験の再現ではない／人への当てはめは議論中","shinka.seadice.win/universe-25-sim/"]:["記録: Calhoun 1973（白丸は図から読んだ推定）／破線は式で、実験の再現ではない／人への当てはめは議論中","shinka.seadice.win/universe-25-sim/"]).forEach(function(s,i){tx(8,Y0+40+i*15,s,"ft");});
var e=null;EV.forEach(function(x){if(x[0]<=day)e=x;});var p=last(day);
q("ev").innerHTML='<p><span class="lv '+(e[2]=="p"?"h":"k")+'">'+(e[2]=="p"?"予測":"記録")+'</span>'+e[0]+'日目: '+e[1]+'</p><p class="cmp">直前の記録: '+p[0]+'日目に'+fmt(p[1])+'匹（'+(p[2]?"確か":"図から読んだ推定")+'）　／　式のこの日: 約'+fmt(N[day])+'匹</p>';
if(ST){q("o1").textContent="子が生まれ続ける式では、数はKの近くで止まり、減りません。";}
else{var z=null;for(var t3=S;t3<=TMAX;t3++){if(N[t3]<1){z=t3;break;}}q("o1").textContent="式では、"+S+"日目に子が育たなくなると、あとは年をとって死ぬだけで"+(z?"、"+z+"日目ごろに0になります。":"減っていきます。");}
q("o2").textContent="記録と比べると、560日目は記録2,200匹／式 約"+fmt(N[560])+"匹、1588日目は記録27匹／式 約"+fmt(N[1588])+"匹。式では、子が育たなくなった後は年をとって死ぬだけでも数は減ります（死に方の形は仮のもの）。式が出せないのは、なぜゆとりをもって休める数の約57%（2,200匹）で増えるのが止まり、子が育たなくなったのかです。";
try{localStorage.setItem("shinka-u25-v2",JSON.stringify(IDS.map(function(i){return +q(i).value;})));}catch(x){}}
try{var s=JSON.parse(localStorage.getItem("shinka-u25-v2")||"null");if(Array.isArray(s)&&s.length==IDS.length)IDS.forEach(function(i,j){var x=q(i),v=+s[j];if(isFinite(v))x.value=Math.min(+x.max,Math.max(+x.min,v));});}catch(x){}
IDS.forEach(function(i){q(i).addEventListener("input",draw);});
q("rs").addEventListener("click",function(){for(var k in DEF)q(k).value=DEF[k];draw();});
var rt;window.addEventListener("resize",function(){clearTimeout(rt);rt=setTimeout(draw,150);});
draw();})();</script>"""

CSS = (".tl{margin:8px 0 28px}.sd-tool{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:16px}"
       "#ch{width:100%;height:auto;display:block;margin:8px 0}#ch .ax{font-size:12px;fill:var(--muted)}#ch .ft{font-size:11px;fill:var(--muted)}"
       "#ch .gr{stroke:var(--border);stroke-width:1}#ch .cap{stroke:var(--muted);stroke-width:1;stroke-dasharray:6 4}"
       "#ch .ms{fill:none;stroke:var(--accent2);stroke-width:2.5;stroke-dasharray:9 5}#ch .lb1{font-size:13px;font-weight:800;fill:var(--accent)}#ch .lb2{font-size:13px;font-weight:800;fill:var(--accent2)}"
       "#ch .pl{fill:none;stroke:var(--accent);stroke-width:2;stroke-dasharray:3 4}#ch .dk{fill:var(--accent)}#ch .de{fill:var(--bg);stroke:var(--accent);stroke-width:2}"
       "#ch .cur{stroke:var(--text);stroke-width:1;stroke-dasharray:2 3}"
       ".lg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13px;color:var(--muted)}.lg span{display:inline-flex;align-items:center;gap:6px}"
       ".m{display:inline-block;width:18px;height:0;border-top:3px solid var(--accent)}.m.e{width:10px;height:10px;border:2px solid var(--accent);border-radius:50%}"
       ".m.k{width:10px;height:10px;border:0;border-radius:50%;background:var(--accent)}.m.p{border-top:3px dotted var(--accent)}.m.s{border-top:3px dashed var(--accent2)}.sv{font-size:13px;color:var(--muted);margin-top:10px}"
       ".ctl{border-top:1px solid var(--border);padding-top:12px;margin-top:12px}.tl2{display:block;font-size:14px;font-weight:800;margin:0 0 6px}"
       ".ctl label{display:flex;justify-content:space-between;gap:8px;font-size:14px;margin-top:14px}.ctl output{font-weight:800;color:var(--accent)}"
       ".ctl input[type=range]{width:100%;min-height:48px;accent-color:var(--accent)}"
       ".ev p{font-size:15px;margin:4px 0}.ev .cmp{font-size:13px;color:var(--muted)}"
       ".lv{display:inline-block;font-size:12px;font-weight:800;padding:1px 8px;border-radius:4px;margin-right:8px;border:1px solid currentColor}"
       ".lv.k{color:var(--accent)}.lv.h{color:var(--accent2)}.lv.u{color:var(--muted)}"
       ".pk{min-height:48px;padding:0 14px;margin-top:12px;font-size:14px;border:1px solid var(--muted);border-radius:6px;background:var(--bg);color:var(--text);cursor:pointer}"
       ".pk:focus-visible,.ctl input:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"
       ".out{border:1px solid var(--accent);border-radius:8px;padding:16px;margin-top:14px;background:var(--card)}.o1{font-size:18px;font-weight:800;line-height:1.6}.o2{font-size:14px;color:var(--muted);margin-top:6px}"
       ".as{margin:8px 0 16px 20px}.as li{margin:4px 0}.kk{display:grid;grid-template-columns:1fr;gap:10px;margin:8px 0 16px}"
       ".kk>div{border:1px solid var(--border);border-radius:8px;padding:12px;background:var(--card)}.kk p{font-size:14px}.kk .lv{margin-bottom:6px}"
       ".src li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;line-height:1.7}.src a{word-break:break-all}"
       "@media(min-width:720px){.kk{grid-template-columns:1fr 1fr 1fr}}")

DESC = ("ユニバース25の個体数の記録に、寿命つきの単純な式を重ねるグラフ。子が育たなくなる日の後は、年をとって死ぬだけでも数は減る。"
        "式が出せないのは、なぜ2,200匹で増えるのが止まり子が育たなくなったか。出典つき・無料・登録不要。")

GRAPH = {"@context": "https://schema.org", "@graph": [{"@type": "WebApplication", "name": TITLE,
         "url": f"https://shinka.seadice.win/{PATH}/", "applicationCategory": "EducationalApplication", "operatingSystem": "Any",
         "browserRequirements": "JavaScript", "isAccessibleForFree": True, "inLanguage": "ja",
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}, "description": DESC,
         "citation": "https://doi.org/10.1177/00359157730661P202",
         "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}}]}

PAGE = {"path": PATH, "title": TITLE,
        "seo_title": "ユニバース25の記録を式と比べるグラフ（環境収容力・寿命・子が育たなくなる日を変える）",
        "date": "2026-11-12", "desc": DESC,
        "body": BODY.replace("__REC__", json.dumps(REC)).replace("__EV__", json.dumps(EV, ensure_ascii=False)),
        "css": CSS,
        "head": '<script type="application/ld+json">' + json.dumps(GRAPH, ensure_ascii=False) + "</script>"}

if __name__ == "__main__":
    pf = ROOT / "media/shinka-pages.json"
    pages = [p for p in json.loads(pf.read_text()) if p.get("path") != PATH] + [PAGE]
    pf.write_text(json.dumps(pages, ensure_ascii=False, indent=2) + "\n")
    print("wrote", PATH)
