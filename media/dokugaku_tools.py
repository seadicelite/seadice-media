"""独学の科学のWebツールページ。dokugaku_hayami.py が読み込み、media/dokugaku-pages.json に一緒に書き出す。

数値は記事 /spaced-review-why-it-works/ で出典照合済みの Cepeda ら(2008) の結果だけを使う。
新しいツールを足すときは docs/quality/tool.md のページの型に合わせ、PAGES に追加する。
"""
import json

E_URL = "https://dokugaku.seadice.win/review-timing/"

# Cepedaら(2008): テストまでの日数 → 最もよく残った「学習から復習まで」の日数
POINTS = [(7, 1), (35, 11), (70, 21), (350, 21)]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "復習日の計算機（試験日から逆算）", "url": E_URL, "applicationCategory": "EducationalApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "試験日や使う日を入れると、分散学習の研究（Cepedaら 2008）をもとに、1回目の復習に向く日を計算します。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "復習は何日後にすればいいですか？",
         "acceptedAnswer": {"@type": "Answer", "text": "使う日までの長さで変わります。Cepedaら（2008）では、1週間後のテストなら1日後、35日後なら11日後、70日後と1年後なら21日後の復習が最もよく残りました。"}},
        {"@type": "Question", "name": "試験まで3日しかないときはどうすればいいですか？",
         "acceptedAnswer": {"@type": "Answer", "text": "研究で確かめられた最短は7日後のテストです。それより短いときは、今日学んで翌日に1回思い出す練習をするのが目安です。テストが近いほど、間をあけるかどうかの差は小さくなります。"}},
        {"@type": "Question", "name": "入力した日付はどこかに送られますか？",
         "acceptedAnswer": {"@type": "Answer", "text": "送られません。計算はすべてブラウザの中で行い、保存もしません。"}}]}]}

LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
pts = json.dumps(POINTS)

body = f"""<script type="application/ld+json">{LD}</script>
<p>試験日（覚えたことを使う日）を入れると、1回目の復習に向く日を計算します。無料・広告なし・登録不要で、入力した日付はどこにも送られません。</p>
<form class="rt-box" id="rt" onsubmit="return false">
<label for="rt-d">試験日・使う日</label>
<input type="date" id="rt-d" required>
<label for="rt-s">勉強する日（初めて覚える日）</label>
<input type="date" id="rt-s">
<button type="submit" id="rt-b">復習日を計算する</button>
<div id="rt-out" class="rt-out" aria-live="polite" hidden></div>
</form>
<p class="answer"><strong>目安：使う日が近いほど早めに、遠いほど間をあけて1回目の復習をします。</strong>1週間後なら翌日、約1か月後なら10日後前後、70日以上先なら3週間後です。</p>
<h2>計算のしかた</h2>
<p>分散学習（間をあけた復習）の大規模な実験、Cepedaら（2008）の結果を使っています。約1,350人が雑学知識を覚え、間隔をいろいろ変えて1回復習し、最長1年後にテストを受けました。最適な間隔での復習は、間をあけない復習より正答が64%多くなりました。</p>
<table class="rt-t"><caption>実験で最もよく残った間隔</caption><thead><tr><th>テストまで</th><th>最もよく残った復習のタイミング</th></tr></thead>
<tbody><tr><td>7日後</td><td>学習の1日後</td></tr><tr><td>35日後</td><td>学習の11日後</td></tr><tr><td>70日後</td><td>学習の21日後</td></tr><tr><td>350日後</td><td>学習の21日後</td></tr></tbody></table>
<p>この4点の間の日数は、SEADICEが直線でつないで見積もっています（実験で直接確かめた値ではありません）。7日より短いときは翌日、350日より長いときは21日後を表示します。</p>
<div class="note">実験の対象は大学生などの成人で、課題は雑学知識の暗記でした。計算・作文などの技能や、何度も復習する場合にそのまま当てはまるとは限りません。くわしくは<a href="/spaced-review-why-it-works/">分散学習の記事</a>で解説しています。</div>
<h2>入力例</h2>
<table class="rt-t"><thead><tr><th>勉強する日</th><th>試験日</th><th>1回目の復習</th></tr></thead>
<tbody><tr><td>10月1日</td><td>10月8日（7日後）</td><td>10月2日</td></tr><tr><td>10月1日</td><td>11月5日（35日後）</td><td>10月12日</td></tr><tr><td>10月1日</td><td>12月10日（70日後）</td><td>10月22日</td></tr></tbody></table>
<h2>よくある質問</h2>
<details open><summary>復習は何日後にすればいいですか？</summary><p>使う日までの長さで変わります。Cepedaら（2008）では、1週間後のテストなら1日後、35日後なら11日後、70日後と1年後なら21日後の復習が最もよく残りました。</p></details>
<details><summary>試験まで3日しかないときはどうすればいいですか？</summary><p>研究で確かめられた最短は7日後のテストです。それより短いときは、今日学んで翌日に1回思い出す練習をするのが目安です。テストが近いほど、間をあけるかどうかの差は小さくなります。</p></details>
<details><summary>入力した日付はどこかに送られますか？</summary><p>送られません。計算はすべてブラウザの中で行い、保存もしません。</p></details>
<h2>復習のときにやること</h2>
<p>復習はノートを読み返すより、本を閉じて思い出す方が残ります（<a href="/retrieval-practice-vs-rereading/">思い出す練習の記事</a>）。ほかの勉強法の効き目は<a href="/hayami/">勉強法の効く・効かない早見表</a>にまとめています。</p>
<div class="sources"><h2>出典</h2><ol><li>Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., &amp; Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. <i>Psychological Science</i>, 19(11), 1095–1102. <a href="https://doi.org/10.1111/j.1467-9280.2008.02209.x" rel="noopener">https://doi.org/10.1111/j.1467-9280.2008.02209.x</a></li></ol></div>
<script>
(function(){{
var P={pts},d=document.getElementById('rt-d'),s=document.getElementById('rt-s'),o=document.getElementById('rt-out');
function iso(t){{var z=new Date(t.getTime()-t.getTimezoneOffset()*6e4);return z.toISOString().slice(0,10)}}
function gap(n){{if(n<=P[0][0])return 1;for(var i=1;i<P.length;i++){{var a=P[i-1],b=P[i];if(n<=b[0])return Math.round(a[1]+(b[1]-a[1])*(n-a[0])/(b[0]-a[0]))}}return P[P.length-1][1]}}
function fmt(t){{return (t.getMonth()+1)+'月'+t.getDate()+'日（'+'日月火水木金土'[t.getDay()]+'）'}}
var t0=new Date();t0.setHours(0,0,0,0);s.value=iso(t0);
document.getElementById('rt').addEventListener('submit',function(){{
 if(!d.value){{d.focus();return}}
 var st=s.value?new Date(s.value+'T00:00'):t0,ex=new Date(d.value+'T00:00'),n=Math.round((ex-st)/864e5);
 o.hidden=false;
 if(n<1){{o.innerHTML='<p>試験日は、勉強する日より後の日付にしてください。</p>';return}}
 if(n<2){{o.innerHTML='<p>試験は翌日です。今日のうちに、本を閉じて思い出す練習を1回してから寝ましょう。</p>';return}}
 var g=Math.min(gap(n),n-1),r=new Date(st.getTime()+g*864e5);
 o.innerHTML='<p class="rt-l">1回目の復習に向く日</p><p class="rt-v">'+fmt(r)+'</p><p>勉強する日の'+g+'日後・試験の'+(n-g)+'日前（試験まで'+n+'日）</p>'+(n<7?'<p class="rt-n">7日より短い期間は研究で確かめられていないため、翌日を目安にしています。</p>':n>350?'<p class="rt-n">350日より長い期間は研究の範囲外のため、21日後を目安にしています。</p>':'');
}});
}})();
</script>"""

css = (".rt-box{background:var(--card);border:1px solid var(--accent);border-radius:16px;padding:20px;margin:20px 0 24px;display:grid;gap:8px}"
       ".rt-box label{font-size:14px;font-weight:700;margin-top:6px}"
       ".rt-box input{font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);color-scheme:dark;min-height:48px}"
       ".rt-box button{font:inherit;font-size:16px;font-weight:800;margin-top:12px;padding:14px;border:0;border-radius:12px;background:var(--accent);color:#0B1020;cursor:pointer;min-height:48px}"
       ".rt-out{margin-top:14px;padding-top:14px;border-top:1px solid var(--border);font-size:15px;line-height:1.8}"
       ".rt-l{font-size:13px;color:var(--muted)}.rt-v{font-size:30px;font-weight:900;color:var(--accent);line-height:1.3;margin:2px 0 6px}.rt-n{font-size:13px;color:var(--muted);margin-top:6px}"
       ".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".rt-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.rt-t caption{text-align:left;font-size:13px;color:var(--muted);margin-bottom:6px}"
       ".rt-t th,.rt-t td{border:1px solid var(--border);padding:10px;text-align:left}.rt-t th{background:var(--card)}"
       ".note{background:rgba(90,176,255,.07);border:1px solid rgba(90,176,255,.25);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}.note a,.sources a{color:var(--link)}"
       "details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}summary{cursor:pointer;font-weight:700;font-size:15px}details p{font-size:15px;margin-top:8px}"
       ".sources{margin-top:48px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;word-break:break-all}")

PAGES = [{"path": "review-timing", "title": "復習日の計算機（試験日から逆算）",
          "seo_title": "復習の間隔 計算｜試験日から逆算して1回目の復習日を出す（分散学習の研究をもとに）", "date": "2026-10-06",
          "desc": "試験日を入れると、1回目の復習に向く日を計算。1週間後なら翌日、約1か月後なら10日後前後。約1,350人の分散学習の研究（Cepedaら 2008）をもとにした無料・広告なしのツール。",
          "body": body, "css": css}]

# ---- 勉強の記録シート(/study-log/) ----
# 数値は記事 /study-log-progress-monitoring/ で出典照合済みの Harkin ら(2016) の結果だけを使う。
# 記録はブラウザの localStorage だけに保存する(docs/quality/base.md「個人情報を集めない」)。
SL_URL = "https://dokugaku.seadice.win/study-log/"
sl_ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "勉強の記録シート（1日1行）", "url": SL_URL, "applicationCategory": "EducationalApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "その日に勉強したことを1行で記録し、続けた日数と合計時間を見える化する無料ツール。記録は端末の中だけに保存し、登録不要・広告なし。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "勉強の記録をつけると、本当に続くのですか？",
         "acceptedAnswer": {"@type": "Answer", "text": "進み具合を確かめる回数を増やすと、目標は達成されやすくなりました。138件の実験・19,951人をまとめたメタ分析（Harkinら 2016）の結果です。ただし多くは健康の目標で、勉強での研究はまだ少なめです。"}},
        {"@type": "Question", "name": "記録はどこに保存されますか？",
         "acceptedAnswer": {"@type": "Answer", "text": "この端末のブラウザの中だけです。サーバーには送りません。ブラウザのデータを消すと記録も消えるので、ときどき「書き出す」でファイルに保存してください。"}},
        {"@type": "Question", "name": "iPhoneで記録が消えないようにするには？",
         "acceptedAnswer": {"@type": "Answer", "text": "Safariの共有ボタンから「ホーム画面に追加」し、ホーム画面のアイコンから開いて記録してください。Safariは7日間開かなかったサイトの保存データを消すことがありますが、ホーム画面に追加したものは対象外です。Safariで開いたときとは保存場所が別になります。"}}]}]}
SL_LD = json.dumps(sl_ld, ensure_ascii=False).replace("</", "<\\/")

SL_JS = r"""
(function(){
var K='dokugaku-study-log-v1',L=[],ok=true;
function $(i){return document.getElementById(i)}
function load(){try{L=JSON.parse(localStorage.getItem(K)||'[]');if(!Array.isArray(L))L=[]}catch(e){ok=false;L=[]}}
function save(){try{localStorage.setItem(K,JSON.stringify(L));return true}catch(e){ok=false;msg('保存できませんでした。プライベートブラウズでは記録を残せません。');return false}}
function msg(t){$('sl-msg').textContent=t}
function iso(d){var z=new Date(d.getTime()-d.getTimezoneOffset()*6e4);return z.toISOString().slice(0,10)}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function stats(){
 var days={},total=0;L.forEach(function(e){days[e.d]=1;total+=(+e.m||0)});
 var t=new Date();t.setHours(0,0,0,0);var s=0,c=new Date(t);
 if(!days[iso(c)])c.setDate(c.getDate()-1);
 while(days[iso(c)]){s++;c.setDate(c.getDate()-1)}
 $('st-days').textContent=Object.keys(days).length;$('st-streak').textContent=s;
 $('st-total').textContent=total>=60?Math.floor(total/60)+'時間'+(total%60?total%60+'分':''):total+'分';
 var w='',d=new Date(t);d.setDate(d.getDate()-6);
 for(var i=0;i<7;i++){var k=iso(d),on=!!days[k];w+='<li class="'+(on?'on':'')+'"><span>'+'日月火水木金土'[d.getDay()]+'</span><b>'+(on?'記録':'なし')+'</b></li>';d.setDate(d.getDate()+1)}
 $('sl-week').innerHTML=w;
}
function render(){
 var l=L.slice().sort(function(a,b){return a.d<b.d?1:a.d>b.d?-1:b.t-a.t});
 $('sl-list').innerHTML=l.length?l.map(function(e){return '<li><div><time>'+esc(e.d.slice(5).replace('-','/'))+'</time>'+(e.m?'<span class="sl-min">'+esc(e.m)+'分</span>':'')+'<p>'+esc(e.w)+'</p></div><button type="button" class="sl-del" data-t="'+e.t+'" aria-label="'+esc(e.d)+'の記録を消す">消す</button></li>'}).join(''):'<li class="sl-empty">まだ記録がありません。今日やったことを1行書いてみましょう。</li>';
 stats();
}
load();
$('sl-d').value=iso(new Date());
if(navigator.storage&&navigator.storage.persist){try{navigator.storage.persist()}catch(e){}}
$('sl-f').addEventListener('submit',function(ev){
 ev.preventDefault();var w=$('sl-w').value.trim();if(!w){$('sl-w').focus();return}
 var m=parseInt($('sl-m').value,10);
 L.push({t:Date.now(),d:$('sl-d').value||iso(new Date()),w:w.slice(0,80),m:(m>0&&m<1440)?m:0});
 if(save()){$('sl-w').value='';$('sl-m').value='';msg('記録しました。');render()}
});
$('sl-list').addEventListener('click',function(ev){
 var b=ev.target.closest('.sl-del');if(!b)return;if(!confirm('この記録を消しますか？'))return;
 var t=+b.getAttribute('data-t');L=L.filter(function(e){return e.t!==t});if(save()){msg('消しました。');render()}
});
$('sl-exp').addEventListener('click',function(){
 var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify({app:'dokugaku-study-log',v:1,items:L})],{type:'application/json'}));
 a.download='study-log-'+iso(new Date())+'.json';document.body.appendChild(a);a.click();a.remove();msg('ファイルに書き出しました。');
});
$('sl-imp').addEventListener('change',function(){
 var f=this.files[0];if(!f)return;var r=new FileReader();
 r.onload=function(){try{var o=JSON.parse(r.result),it=Array.isArray(o)?o:o.items,have={},n=0;L.forEach(function(e){have[e.t]=1});
  it.forEach(function(e){if(e&&e.t&&e.d&&e.w&&!have[e.t]){L.push({t:+e.t,d:String(e.d).slice(0,10),w:String(e.w).slice(0,80),m:+e.m||0});n++}});
  if(save()){msg(n+'件を読み込みました。');render()}}catch(e){msg('読み込めませんでした。書き出したファイルを選んでください。')}};
 r.readAsText(f);this.value='';
});
render();
if(!ok)msg('このブラウザでは記録を保存できません。');
})();
"""

sl_body = ('<script type="application/ld+json">' + SL_LD + '</script>'
 '<p>今日やった勉強を1行で記録し、続けた日数と合計時間を見える化します。無料・広告なし・登録不要。記録は<strong>この端末の中だけ</strong>に保存し、どこにも送りません。</p>'
 '<form class="sl-box" id="sl-f">'
 '<label for="sl-w">今日やったこと（1行）</label><input id="sl-w" maxlength="80" placeholder="例：英単語50個を思い出す練習" enterkeyhint="done" required>'
 '<div class="sl-row"><div><label for="sl-m">時間（分・任意）</label><input id="sl-m" type="number" inputmode="numeric" min="1" max="1439" placeholder="30"></div>'
 '<div><label for="sl-d">日付</label><input id="sl-d" type="date"></div></div>'
 '<button type="submit">記録する</button><p id="sl-msg" class="sl-msg" aria-live="polite"></p></form>'
 '<div class="sl-stats"><div><b id="st-days">0</b><span>記録した日</span></div><div><b id="st-streak">0</b><span>連続日数</span></div><div><b id="st-total">0分</b><span>合計時間</span></div></div>'
 '<p class="sl-cap">直近7日</p><ul class="sl-week" id="sl-week" aria-label="直近7日の記録"></ul>'
 '<h2>記録の一覧</h2><ul class="sl-list" id="sl-list"></ul>'
 '<div class="sl-io"><button type="button" id="sl-exp">記録をファイルに書き出す</button><label class="sl-file">ファイルから読み込む<input type="file" id="sl-imp" accept="application/json,.json"></label></div>'
 '<div class="note"><strong>記録が消えないように</strong><br>ブラウザのデータを消すと記録も消えます。ときどき「書き出す」でファイルに保存してください。iPhoneはSafariの共有ボタンから「ホーム画面に追加」し、<strong>ホーム画面のアイコンから開いて</strong>記録すると、7日間開かなくても消えにくくなります（Safariで開いたときとは保存場所が別です）。</div>'
 '<p class="answer"><strong>結論：進み具合を確かめる回数を増やすと、目標は達成されやすくなります。</strong>書き残す・人に見せる形の方が効果は大きめでした。1日1行で十分です。</p>'
 '<h2>なぜ記録が効くのか</h2>'
 '<p>138件の実験・19,951人をまとめたメタ分析（Harkinら 2016）では、進み具合を確かめる回数を増やす工夫が、目標の達成を後押ししました（効果の大きさ d=0.40）。確かめた内容を書き残した場合（0.43）は、書き残さない場合（0.29）より効果が大きめでした。</p>'
 '<table class="rt-t"><caption>確かめ方による効果の違い（Harkinら 2016）</caption><thead><tr><th>確かめ方</th><th>効果の大きさ</th></tr></thead>'
 '<tbody><tr><td>人に公開する</td><td>0.55</td></tr><tr><td>人に報告する</td><td>0.47</td></tr><tr><td>自分だけで確かめる</td><td>0.19</td></tr><tr><td>書き残す</td><td>0.43</td></tr><tr><td>書き残さない</td><td>0.29</td></tr></tbody></table>'
 '<div class="note">このメタ分析の実験の多くは、運動や食事などの健康の目標でした。勉強で確かめた研究はまだ少ないため、効き目は小さく試して確かめてください。くわしくは<a href="/study-log-progress-monitoring/">勉強の記録の記事</a>で解説しています。</div>'
 '<h2>記録の例</h2><table class="rt-t"><thead><tr><th>日付</th><th>今日やったこと</th><th>時間</th></tr></thead>'
 '<tbody><tr><td>10/1</td><td>過去問1回分を解いて答え合わせ</td><td>60分</td></tr><tr><td>10/2</td><td>まちがえた12問を解き直し</td><td>25分</td></tr><tr><td>10/3</td><td>第3章を読む前に章末問題を3分解いた</td><td>40分</td></tr></tbody></table>'
 '<p>「何ページ読んだか」のような結果だけでなく、「何をしたか」の行動を書くのがおすすめです。同じメタ分析では、行動を記録すると行動に、結果を記録すると結果に効きました。</p>'
 '<h2>よくある質問</h2>'
 '<details open><summary>勉強の記録をつけると、本当に続くのですか？</summary><p>進み具合を確かめる回数を増やすと、目標は達成されやすくなりました。138件の実験・19,951人をまとめたメタ分析（Harkinら 2016）の結果です。ただし多くは健康の目標で、勉強での研究はまだ少なめです。</p></details>'
 '<details><summary>記録はどこに保存されますか？</summary><p>この端末のブラウザの中だけです。サーバーには送りません。ブラウザのデータを消すと記録も消えるので、ときどき「書き出す」でファイルに保存してください。</p></details>'
 '<details><summary>iPhoneで記録が消えないようにするには？</summary><p>Safariの共有ボタンから「ホーム画面に追加」し、ホーム画面のアイコンから開いて記録してください。Safariは7日間開かなかったサイトの保存データを消すことがありますが、ホーム画面に追加したものは対象外です。Safariで開いたときとは保存場所が別になります。</p></details>'
 '<div class="sources"><h2>出典</h2><ol><li>Harkin, B., Webb, T. L., Chang, B. P. I., Prestwich, A., Conner, M., Kellar, I., Benn, Y., &amp; Sheeran, P. (2016). Does monitoring goal progress promote goal attainment? A meta-analysis of the experimental evidence. <i>Psychological Bulletin</i>, 142(2), 198–229. <a href="https://doi.org/10.1037/bul0000025" rel="noopener">https://doi.org/10.1037/bul0000025</a></li></ol></div>'
 '<script>' + SL_JS + '</script>')

sl_css = (".sl-box{background:var(--card);border:1px solid var(--accent);border-radius:16px;padding:20px;margin:20px 0;display:grid;gap:8px}"
          ".sl-box label,.sl-row label{font-size:14px;font-weight:700;display:block;margin:6px 0 6px}"
          ".sl-box input{width:100%;font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);color-scheme:dark;min-height:48px}"
          ".sl-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}"
          ".sl-box button{font:inherit;font-size:16px;font-weight:800;margin-top:12px;padding:14px;border:0;border-radius:12px;background:var(--accent);color:#0B1020;cursor:pointer;min-height:48px}"
          ".sl-msg{font-size:14px;color:var(--muted);min-height:1.5em}"
          ".sl-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:8px 0 16px}.sl-stats div{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px;text-align:center}"
          ".sl-stats b{display:block;font-size:24px;color:var(--accent);line-height:1.3}.sl-stats span{font-size:12px;color:var(--muted)}"
          ".sl-cap{font-size:13px;color:var(--muted);margin:0 0 6px}.sl-week{list-style:none;padding:0;display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin:0 0 8px}"
          ".sl-week li{border:1px solid var(--border);border-radius:10px;padding:6px 0;text-align:center;font-size:12px;color:var(--muted)}.sl-week li b{display:block;font-size:12px;font-weight:700}"
          ".sl-week li.on{background:rgba(245,197,66,.16);border-color:var(--accent);color:var(--text)}.sl-week li.on b{color:var(--accent)}"
          ".sl-list{list-style:none;padding:0;margin:12px 0}.sl-list li{display:flex;gap:12px;align-items:flex-start;justify-content:space-between;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 14px;margin:8px 0}"
          ".sl-list time{font-size:13px;font-weight:800;color:var(--accent);margin-right:8px}.sl-min{font-size:12px;color:var(--muted)}.sl-list p{font-size:15px;margin-top:2px;word-break:break-word}"
          ".sl-list li.sl-empty{display:block;color:var(--muted);font-size:14px}"
          ".sl-del{flex:none;font:inherit;font-size:13px;background:none;border:1px solid var(--border);color:var(--muted);border-radius:8px;padding:8px 12px;min-height:40px;cursor:pointer}"
          ".sl-io{display:flex;flex-wrap:wrap;gap:10px;margin:16px 0}.sl-io button,.sl-file{font:inherit;font-size:14px;font-weight:700;background:var(--card);border:1px solid var(--border);color:var(--text);border-radius:10px;padding:12px 14px;min-height:46px;cursor:pointer}"
          ".sl-file input{position:absolute;width:1px;height:1px;opacity:0}.sl-file:focus-within{outline:2px solid var(--accent);outline-offset:3px}")

PAGES.append({"path": "study-log", "title": "勉強の記録シート（1日1行）",
              "seo_title": "勉強の記録シート｜1日1行で続けた日数と時間を見える化（無料・登録不要）",
              "date": "2026-10-07",
              "desc": "今日やった勉強を1行で記録し、続けた日数・連続日数・合計時間を見える化。記録は端末の中だけに保存、登録不要・広告なし。138件の実験のメタ分析（Harkinら 2016）をもとにした使い方つき。",
              "body": sl_body, "css": css + sl_css,
              "head": '<link rel="manifest" href="/manifest.json"><link rel="apple-touch-icon" href="/apple-touch-icon.png"><meta name="apple-mobile-web-app-capable" content="yes"><meta name="mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="勉強の記録"><meta name="theme-color" content="#0B1020">'})
