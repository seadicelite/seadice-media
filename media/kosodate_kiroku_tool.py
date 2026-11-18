"""AI時代の子育て「朝の様子の記録（登校しぶり）」(/asa-kiroku/)。kosodate_tools.py が読み込む。

記録はブラウザの中だけ(localStorage)。サーバーへは送らない。判定・診断はしない(数えて並べるだけ)。
説明の文は、出典照合済みの記事と公的な定義だけを使う。
"""
import json

URL = "https://kosodate.seadice.win/asa-kiroku/"

FAQ = [
    ("子どもが学校に行きたがらないとき、記録をつける意味はありますか？",
     "あります。行けた日・休んだ日・朝の体の訴えを並べると、曜日や行事との重なりなど、毎朝のやりとりの中では気づきにくい傾向が見えます。担任やスクールカウンセラー、かかりつけの小児科に相談するときも、日付つきの記録があると様子を短く正確に伝えられます。"),
    ("記録はどこかに保存されますか？",
     "この端末のブラウザの中だけに保存されます。SEADICEのサーバーには送らず、登録もいりません。機種変更のときは「記録を書き出す」で保存したファイルを、新しい端末で読み込んでください。"),
    ("記録から「不登校かどうか」を判定できますか？",
     "判定はしません。このページは記録を数えて並べるだけです。文部科学省は、登校という結果だけを目標にせず、休むことの意味と学びの遅れの両方に気を配りながら、はじまりの段階から支えることを求めています。日数より、本人の様子と気持ちを一緒に見てください。"),
    ("子どもに記録していることを伝えた方がいいですか？",
     "年齢によりますが、小学校高学年以上なら「様子を先生に伝えるために、つけてもいい？」と聞いてから始めると、監視されていると感じにくくなります。本人と一緒に「きょうの気分」を選ぶ使い方もできます。"),
]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "朝の様子の記録（登校しぶり）", "url": URL, "applicationCategory": "LifestyleApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "子どもが学校に行きたがらないときに、毎朝の様子（行けた・遅れて行けた・休んだ）と体の訴えを1タップで記録し、曜日ごとの傾向と、学校や相談先に見せるまとめを作れます。記録はこの端末の中だけ。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}
LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
faq_html = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ))

BODY = """<script type="application/ld+json">%LD%</script>
<p class="answer">子どもが学校に行きたがらないときは、毎朝の様子を1タップで記録しておくと、曜日や行事との重なりが見え、先生や相談先にも日付つきで伝えられます。このページは数えて並べるだけで、判定はしません。記録はこの端末の中だけに残ります。</p>
<form id="ak" class="ak-box" onsubmit="return false">
<label for="ak-d">日付</label>
<input type="date" id="ak-d">
<p class="ak-q">けさの様子</p>
<div class="ak-st" role="radiogroup" aria-label="けさの様子">
<button type="button" data-s="go" aria-pressed="false"><i class="c-go"></i>行けた</button>
<button type="button" data-s="late" aria-pressed="false"><i class="c-late"></i>遅れて行けた</button>
<button type="button" data-s="back" aria-pressed="false"><i class="c-back"></i>途中で帰った</button>
<button type="button" data-s="off" aria-pressed="false"><i class="c-off"></i>休んだ</button>
<button type="button" data-s="none" aria-pressed="false"><i class="c-none"></i>学校がない日</button>
</div>
<p class="ak-q">朝に言っていたこと・様子（いくつでも）</p>
<div class="ak-tg" id="ak-tg"></div>
<label for="ak-m">メモ（任意）</label>
<input type="text" id="ak-m" maxlength="120" placeholder="例：前の日に友だちとけんかしたと話していた">
<button type="button" id="ak-save" class="ak-main">この日を記録する</button>
<p class="ak-msg" id="ak-msg" role="status"></p>
</form>
<div id="ak-out" hidden>
<h2>この4週間</h2>
<div class="ak-cal" id="ak-cal" aria-label="4週間の記録"></div>
<p class="ak-lg"><span><i class="c-go"></i>行けた</span><span><i class="c-late"></i>遅れて</span><span><i class="c-back"></i>途中で帰った</span><span><i class="c-off"></i>休んだ</span><span><i class="c-none"></i>学校なし</span></p>
<h3>曜日ごとの「休んだ・遅れた・途中で帰った」</h3>
<ul class="ak-wk" id="ak-wk"></ul>
<h3>よく出た朝の訴え</h3>
<ul class="ak-wk" id="ak-tops"></ul>
<h3>学校・相談先に見せるまとめ</h3>
<p class="ak-s">直近30日の記録を文章にします。担任やスクールカウンセラー、小児科に相談するときにそのまま見せられます。</p>
<pre class="ak-sum" id="ak-sum"></pre>
<div class="ak-acts"><button type="button" id="ak-copy">まとめをコピー・共有する</button><button type="button" id="ak-exp">記録を書き出す</button></div>
<p class="ak-s"><label class="ak-imp">記録を読み込む（機種変更のとき）<input type="file" id="ak-imp" accept="application/json"></label> ／ <button type="button" class="ak-link" id="ak-clear">記録をすべて消す</button></p>
</div>
<h2>記録するときに大事なこと</h2>
<ul>
<li><b>日数で判定しない。</b>休んだ日数は様子をつかむ手がかりで、多い・少ないで良し悪しを決めるものではありません。文部科学省も、登校という結果だけを目標にしないよう求めています。</li>
<li><b>行かせるための記録にしない。</b>記録は、子どもの様子をわかって、先生や相談先と一緒に考えるための材料です。休んだ日を責める材料にしないでください。</li>
<li><b>体の訴えは軽く見ない。</b>研究のまとめでは、学校に行きにくい子の最初の訴えは腹痛や頭痛が多く、その多くは体の病気では説明できず、背景に不安があることが多いとされています。それでも痛みが続くときは、まずかかりつけの小児科で体の病気がないかを見てもらってください。そのときもこの記録が役に立ちます。</li>
<li><b>親だけで抱えない。</b>担任、スクールカウンセラー、自治体の教育相談窓口に相談できます。学校に行けない間の学びの場として、教育支援センター（適応指導教室）やフリースクールもあります。</li>
</ul>
<p>行き渋りが始まったときに親ができることと、国のデータ・研究でわかっていることは、<a href="%ARTICLE_URL%">%ARTICLE_TITLE%</a>にまとめています。</p>
<h2>記録の例</h2>
<table class="ak-t"><thead><tr><th>記録のしかた</th><th>見えてくること</th></tr></thead><tbody>
<tr><td>4週間、毎朝「行けた／遅れて／休んだ」だけを押す</td><td>月曜と休み明けに休みが集まっている、など曜日の傾向</td></tr>
<tr><td>「おなかが痛い」「眠れていない」などの訴えも押す</td><td>どの訴えが休んだ日と重なっているか。小児科で伝えやすくなる</td></tr>
<tr><td>行事や前日の出来事をメモに書く</td><td>テスト・体育・特定の授業など、きっかけの手がかり</td></tr>
</tbody></table>
<h2>よくある質問</h2>
%FAQ%
<div class="sources"><h2>出典</h2><ol>
%SOURCES%
</ol></div>
<p class="note">このページは記録と集計だけを行い、診断や判定はしません。お子さんの体や心の様子で気になることがあるときは、かかりつけの小児科、学校のスクールカウンセラー、自治体の教育相談窓口に相談できます。</p>
<script>
(function(){
var KEY='kosodate-asa-v1',$=function(i){return document.getElementById(i)};
var ST={go:'行けた',late:'遅れて行けた',back:'途中で帰った',off:'休んだ',none:'学校がない日'};
var TG=['おなかが痛い','頭が痛い','気持ちが悪い','だるい・起きられない','眠れていない','行きたくないと言った','理由は言わなかった','友だちのこと','勉強・テストのこと','先生のこと','行事・授業のこと'];
var WD=['日','月','火','水','木','金','土'];
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){return {}}}
function save(d){try{localStorage.setItem(KEY,JSON.stringify(d));return true}catch(e){return false}}
function ds(t){var z=function(n){return (n<10?'0':'')+n};return t.getFullYear()+'-'+z(t.getMonth()+1)+'-'+z(t.getDate())}
function day(s){var p=s.split('-');return new Date(+p[0],+p[1]-1,+p[2])}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var D=load(),cur=null;
$('ak-tg').innerHTML=TG.map(function(t){return '<button type="button" aria-pressed="false">'+t+'</button>'}).join('');
function pick(d){var r=D[d]||{};cur=r.s||null;
 [].forEach.call(document.querySelectorAll('.ak-st button'),function(b){b.setAttribute('aria-pressed',b.getAttribute('data-s')===cur?'true':'false')});
 [].forEach.call(document.querySelectorAll('#ak-tg button'),function(b){b.setAttribute('aria-pressed',(r.t||[]).indexOf(b.textContent)>=0?'true':'false')});
 $('ak-m').value=r.m||'';$('ak-msg').textContent=D[d]?'この日の記録があります。直すときは選び直して記録してください。':''}
$('ak-d').value=ds(new Date());$('ak-d').max=ds(new Date());pick($('ak-d').value);
$('ak-d').addEventListener('change',function(){if(this.value)pick(this.value)});
[].forEach.call(document.querySelectorAll('.ak-st button'),function(b){b.addEventListener('click',function(){cur=b.getAttribute('data-s');
 [].forEach.call(document.querySelectorAll('.ak-st button'),function(x){x.setAttribute('aria-pressed',x===b?'true':'false')})})});
[].forEach.call(document.querySelectorAll('#ak-tg button'),function(b){b.addEventListener('click',function(){b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')==='true'?'false':'true')})});
$('ak-save').addEventListener('click',function(){var d=$('ak-d').value;
 if(!d){$('ak-msg').textContent='日付を選んでください。';return}
 if(!cur){$('ak-msg').textContent='けさの様子を1つ選んでください。';return}
 var t=[].filter.call(document.querySelectorAll('#ak-tg button'),function(b){return b.getAttribute('aria-pressed')==='true'}).map(function(b){return b.textContent});
 D[d]={s:cur,t:t,m:$('ak-m').value.trim()};
 $('ak-msg').textContent=save(D)?d.replace(/-/g,'/')+' を記録しました。':'この端末では保存できませんでした（プライベートモードなど）。';draw()});
function bad(s){return s==='off'||s==='late'||s==='back'}
function draw(){var keys=Object.keys(D).sort();$('ak-out').hidden=!keys.length;if(!keys.length)return;
 var today=new Date(),start=new Date(today.getFullYear(),today.getMonth(),today.getDate()-27);start.setDate(start.getDate()-start.getDay());
 var h=WD.map(function(w){return '<b>'+w+'</b>'}).join('');
 for(var t=new Date(start);t<=today;t.setDate(t.getDate()+1)){var k=ds(t),r=D[k];
  h+='<span class="'+(r?'c-'+r.s:'c-emp')+'" title="'+k+(r?' '+ST[r.s]:'')+'">'+t.getDate()+'<small>'+(r?ST[r.s].slice(0,2):'')+'</small></span>'}
 $('ak-cal').innerHTML=h;
 var lim=ds(new Date(today.getFullYear(),today.getMonth(),today.getDate()-29)),rec=keys.filter(function(k){return k>=lim});
 var wn=[0,0,0,0,0,0,0],wa=[0,0,0,0,0,0,0],tc={};
 rec.forEach(function(k){var r=D[k],w=day(k).getDay();if(r.s!=='none'){wa[w]++;if(bad(r.s))wn[w]++}(r.t||[]).forEach(function(x){tc[x]=(tc[x]||0)+1})});
 $('ak-wk').innerHTML=[1,2,3,4,5,6,0].filter(function(w){return wa[w]}).map(function(w){return '<li><span>'+WD[w]+'曜</span><b style="width:'+Math.round(wn[w]/wa[w]*100)+'%"></b><em>'+wn[w]+' / '+wa[w]+'日</em></li>'}).join('')||'<li>学校がある日の記録がまだありません</li>';
 var tops=Object.keys(tc).sort(function(a,b){return tc[b]-tc[a]}).slice(0,5);
 $('ak-tops').innerHTML=tops.map(function(x){return '<li><span>'+esc(x)+'</span><em>'+tc[x]+'日</em></li>'}).join('')||'<li>まだありません</li>';
 var n={go:0,late:0,back:0,off:0};rec.forEach(function(k){if(n[D[k].s]!==undefined)n[D[k].s]++});
 var L=['朝の様子の記録（'+lim.replace(/-/g,'/')+'〜'+ds(today).replace(/-/g,'/')+'、記録した日だけ）',
  '行けた '+n.go+'日／遅れて行けた '+n.late+'日／途中で帰った '+n.back+'日／休んだ '+n.off+'日'];
 var many=[1,2,3,4,5,6,0].filter(function(w){return wa[w]&&wn[w]}).sort(function(a,b){return wn[b]/wa[b]-wn[a]/wa[a]}).slice(0,2);
 if(many.length)L.push('休み・遅れが多い曜日：'+many.map(function(w){return WD[w]+'曜（'+wn[w]+'/'+wa[w]+'日）'}).join('、'));
 if(tops.length)L.push('朝によく出た訴え：'+tops.map(function(x){return x+'（'+tc[x]+'日）'}).join('、'));
 var memo=rec.filter(function(k){return D[k].m}).slice(-8);
 if(memo.length){L.push('メモ：');memo.forEach(function(k){L.push('・'+k.slice(5).replace('-','/')+' '+ST[D[k].s]+'：'+D[k].m)})}
 $('ak-sum').textContent=L.join('\\n')}
$('ak-copy').addEventListener('click',function(){var t=$('ak-sum').textContent,b=this;
 if(navigator.share){navigator.share({title:'朝の様子の記録',text:t}).catch(function(){});return}
 if(navigator.clipboard){navigator.clipboard.writeText(t).then(function(){b.textContent='コピーしました'},function(){b.textContent='コピーできませんでした'})}});
$('ak-exp').addEventListener('click',function(){var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(D)],{type:'application/json'}));a.download='asa-kiroku-'+ds(new Date())+'.json';a.click()});
$('ak-imp').addEventListener('change',function(){var f=this.files[0];if(!f)return;var r=new FileReader();
 r.onload=function(){try{var x=JSON.parse(r.result),n=0;Object.keys(x).forEach(function(k){if(/^\\d{4}-\\d{2}-\\d{2}$/.test(k)&&x[k]&&ST[x[k].s]){D[k]=x[k];n++}});save(D);draw();pick($('ak-d').value);$('ak-msg').textContent=n+'日分を読み込みました。'}catch(e){$('ak-msg').textContent='読み込めないファイルでした。'}};r.readAsText(f)});
$('ak-clear').addEventListener('click',function(){if(!confirm('この端末の記録をすべて消します。よろしいですか？'))return;D={};save(D);draw();pick($('ak-d').value)});
draw();
})();
</script>"""

CSS = (".ak-box{background:var(--card);border:1.5px solid var(--text);border-radius:18px;padding:20px;margin:20px 0 28px;display:grid;gap:6px;box-shadow:4px 4px 0 var(--text)}"
       ".ak-box label,.ak-q{font-size:14px;font-weight:700;margin:10px 0 2px;display:block}"
       ".ak-box input[type=date],.ak-box input[type=text]{font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);min-height:48px;width:100%}"
       ".ak-st{display:grid;grid-template-columns:1fr 1fr;gap:8px}.ak-st button:last-child{grid-column:1/-1}"
       ".ak-st button,.ak-tg button{font:inherit;font-size:15px;font-weight:700;min-height:48px;padding:10px 12px;border:1.5px solid var(--border);border-radius:12px;background:var(--bg);color:var(--text);cursor:pointer;display:flex;align-items:center;gap:8px;justify-content:center}"
       ".ak-st button[aria-pressed=true],.ak-tg button[aria-pressed=true]{border-color:var(--text);background:#F6E3B0;color:#3B2F2A}"
       ".ak-st button[aria-pressed=true]::after,.ak-tg button[aria-pressed=true]::before{content:'\\2713';font-weight:900}"
       ".ak-tg{display:flex;flex-wrap:wrap;gap:8px}.ak-tg button{font-size:14px;font-weight:600;min-height:44px;border-radius:999px}"
       "i[class^=c-]{display:inline-block;width:14px;height:14px;border-radius:4px;flex:0 0 14px}"
       ".c-go{background:#4C9A6A}.c-late{background:#E8B23A}.c-back{background:#D9822B}.c-off{background:#B5523B}.c-none{background:#B9B0A8}"
       ".ak-main{font:inherit;font-size:17px;font-weight:800;margin-top:14px;padding:14px;border:1.5px solid var(--text);border-radius:12px;background:#E8B23A;color:#3B2F2A;cursor:pointer;min-height:52px}"
       ".ak-msg{font-size:14px;font-weight:700;min-height:1.4em}"
       ".ak-cal{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin:10px 0}.ak-cal b{font-size:12px;text-align:center;color:var(--muted)}"
       ".ak-cal span{font-size:13px;font-weight:700;text-align:center;border-radius:8px;padding:6px 0;line-height:1.3;color:#fff}.ak-cal span small{display:block;font-size:12px;font-weight:600}"
       ".ak-cal .c-emp{background:transparent;border:1px dashed var(--border);color:var(--muted)}.ak-cal .c-late,.ak-cal .c-none{color:#3B2F2A}"
       ".ak-lg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13px}.ak-lg span{display:flex;align-items:center;gap:6px}"
       ".ak-wk{list-style:none;margin:8px 0}.ak-wk li{display:grid;grid-template-columns:96px 1fr 64px;gap:8px;align-items:center;font-size:14px;margin:6px 0}.ak-wk b{display:block;height:10px;background:var(--accent);border-radius:999px;min-width:2px}.ak-wk em{font-style:normal;text-align:right}"
       ".ak-sum{white-space:pre-wrap;font:inherit;font-size:14px;line-height:1.8;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px}"
       ".ak-acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px}.ak-acts button{font:inherit;font-size:15px;font-weight:800;padding:12px;border:1.5px solid var(--text);border-radius:12px;background:var(--card);color:var(--text);cursor:pointer;min-height:52px}"
       ".ak-acts button:first-child{background:#E8B23A;color:#3B2F2A}"
       ".ak-s{font-size:13px;color:var(--muted);margin-top:10px;line-height:1.8}.ak-imp input{display:block;font-size:13px;margin-top:4px}"
       ".ak-link{font:inherit;font-size:13px;background:none;border:0;color:var(--link);text-decoration:underline;cursor:pointer;padding:8px 0}"
       ".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".ak-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.ak-t th,.ak-t td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top;line-height:1.7}.ak-t th{background:var(--card)}"
       ".xbody p a,.sources a,.note a{color:var(--link)}"
       ".xbody>details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}.xbody>details summary{cursor:pointer;font-weight:700;font-size:15px}.xbody>details p{font-size:15px;margin-top:8px}"
       ".sources{margin-top:48px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;word-break:break-all}"
       ".note{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}")


def page(article_slug, article_title, sources_html):
    body = (BODY.replace("%LD%", LD).replace("%FAQ%", faq_html).replace("%SOURCES%", sources_html)
            .replace("%ARTICLE_URL%", f"/{article_slug}/").replace("%ARTICLE_TITLE%", f"「{article_title}」"))
    return {"path": "asa-kiroku", "title": "朝の様子の記録（登校しぶり）",
            "seo_title": "子どもの登校しぶり 記録｜朝の様子を1タップで記録して曜日の傾向と学校に見せるまとめを作る",
            "date": "2026-10-13",
            "desc": "子どもが学校に行きたがらないとき、毎朝の様子（行けた・遅れて・休んだ）と体の訴えを1タップで記録。曜日ごとの傾向と、先生や相談先に見せるまとめを作れます。記録は端末の中だけ。無料・登録不要。",
            "body": body, "css": CSS}
