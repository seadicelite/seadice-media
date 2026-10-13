"""AI時代の子育て「ゲーム・SNSの見守りノート」(/game-mimamori/)。kosodate_tools.py が読み込む。

親だけが使う。子どもを監視・制限する道具ではなく、親の声かけと「終わる場面」を記録して、
関わり方を見直すためのノート。記録はブラウザの中だけ(localStorage)。サーバーへは送らない。判定・診断はしない。
説明の文と数字は、出典照合済みの記事2本（game-cant-stop-time-limit-taking-away・gaming-disorder-children-research）
の出典だけを使う。
"""
import json

URL = "https://kosodate.seadice.win/game-mimamori/"

FAQ = [
    ("子どもがゲームやSNSをやめられないとき、取り上げた方がいいですか？",
     "取り上げるだけで問題が減るという研究結果はそろっていません。中高生1,651人の調査では、親がルールを一方的に押しつけると感じている子ほど、問題のあるゲームの使い方が多い関連がありました。画面の時間をごほうびや罰に使う家庭では、子どもの画面時間が長い関連も見られています。このノートでは、取り上げる前に、終わる場面と声かけを見直すことをすすめています。"),
    ("子どもに記録していることを伝えた方がいいですか？",
     "このノートが記録するのは、子どもの行動ではなく、親の声かけと終わる場面です。親が自分の関わり方を見直すためのメモなので、子どもに見せる必要はありません。ただ、記録を理由に叱ったり、取り上げの根拠にしたりはしないでください。"),
    ("記録はどこかに保存されますか？",
     "この端末のブラウザの中だけに保存されます。SEADICEのサーバーには送らず、登録もいりません。機種変更のときは「記録を書き出す」で保存したファイルを、新しい端末で読み込んでください。"),
    ("これでゲーム障害かどうかわかりますか？",
     "わかりません。このページは判定や診断をしません。WHOの基準でゲーム障害が検討されるのは、自分でコントロールできない・ほかのことより優先される・悪い影響が出ても続ける、という状態がふつう12か月以上続き、生活に大きな支障が出ている場合です。長い時間遊ぶ子の大多数は当てはまりません。気になるときは、かかりつけの小児科や相談窓口に相談できます。"),
    ("1日何時間までなら大丈夫ですか？",
     "すべての子に当てはまる「何時間まで」の答えは、研究ではまだ出ていません。時間の長さより、睡眠・学校・食事など生活への影響を見る考え方が中心です。このノートの「生活の様子」は、そのためのチェックです。"),
]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "ゲーム・SNSの見守りノート", "url": URL, "applicationCategory": "LifestyleApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "子どもがゲームやSNSをやめられないときに、親が使う見守りのノート。終わる場面と声かけを1タップで記録し、揉めずに終われた声かけ・揉めやすい時間帯・生活の様子の変化と、次に試すことがわかります。取り上げや監視はしません。記録はこの端末の中だけ。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}
LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
faq_html = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ))

SOURCES = (
    '<li>Bradt, L., et al. (2023). Does parents\' perceived style of setting limits to gaming matter? <i>Journal of Adolescence</i>. <a href="https://doi.org/10.1002/jad.12271" target="_blank" rel="noopener">doi:10.1002/jad.12271</a></li>'
    '<li>Tang, L., et al. (2018). Mothers\' and fathers\' media parenting practices associated with young children\'s screen-time. <i>BMC Obesity</i>. <a href="https://doi.org/10.1186/s40608-018-0214-4" target="_blank" rel="noopener">doi:10.1186/s40608-018-0214-4</a></li>'
    '<li>Hiniker, A., et al. (2016). Screen Time Tantrums. <i>CHI 2016</i>. <a href="https://doi.org/10.1145/2858036.2858278" target="_blank" rel="noopener">doi:10.1145/2858036.2858278</a></li>'
    '<li>Nielsen, P., et al. (2019). Linking parental mediation practices to adolescents\' problematic online screen use. <i>Journal of Behavioral Addictions</i>. <a href="https://doi.org/10.1556/2006.8.2019.61" target="_blank" rel="noopener">doi:10.1556/2006.8.2019.61</a></li>'
    '<li>国立病院機構久里浜医療センター (2019). ネット・ゲーム使用と生活習慣についてのアンケート結果（概要）. <a href="https://www.ncasa-japan.jp/pdf/document15.pdf" target="_blank" rel="noopener">ncasa-japan.jp</a></li>'
    '<li>World Health Organization. Frequently asked questions: Gaming disorder. <a href="https://www.who.int/standards/classifications/frequently-asked-questions/gaming-disorder" target="_blank" rel="noopener">who.int</a></li>'
    '<li>そのほかの研究とデータは、<a href="/game-cant-stop-time-limit-taking-away/">ゲームをやめられない・取り上げる前の記事</a>と<a href="/gaming-disorder-children-research/">ゲーム障害の記事</a>の出典にまとめています。</li>'
)

BODY = """<script type="application/ld+json">%LD%</script>
<p class="answer">子どもがゲームやSNSをやめられないとき、取り上げる前に、終わる場面と声かけを1タップで記録してみてください。揉めずに終われた声かけと、揉めやすい時間帯が見えてきます。記録するのは子どもではなく親の関わり方で、取り上げや監視はしません。記録はこの端末の中だけに残ります。</p>
<form id="gm" class="gm-box" onsubmit="return false">
<label for="gm-d">日付</label>
<input type="date" id="gm-d">
<p class="gm-q">何をしていた？</p>
<div class="gm-ch" id="gm-what" role="radiogroup" aria-label="何をしていた">
<button type="button" data-v="game" aria-pressed="false">ゲーム</button>
<button type="button" data-v="sns" aria-pressed="false">SNS</button>
<button type="button" data-v="video" aria-pressed="false">動画</button>
</div>
<p class="gm-q">終わる場面はどうだった？</p>
<div class="gm-st" id="gm-end" role="radiogroup" aria-label="終わる場面">
<button type="button" data-v="self" aria-pressed="false"><i class="c-self"></i>自分で終われた</button>
<button type="button" data-v="cue" aria-pressed="false"><i class="c-cue"></i>声をかけて終われた</button>
<button type="button" data-v="wait" aria-pressed="false"><i class="c-wait"></i>区切りまで待って終われた</button>
<button type="button" data-v="fight" aria-pressed="false"><i class="c-fight"></i>揉めた・怒った</button>
</div>
<p class="gm-q">親がしたこと（いくつでも）</p>
<div class="gm-tg" id="gm-did"></div>
<p class="gm-q">時間帯</p>
<div class="gm-ch" id="gm-time" role="radiogroup" aria-label="時間帯">
<button type="button" data-v="day" aria-pressed="false">休日の昼</button>
<button type="button" data-v="eve" aria-pressed="false">夕方</button>
<button type="button" data-v="night" aria-pressed="false">夜</button>
<button type="button" data-v="bed" aria-pressed="false">寝る前</button>
</div>
<label for="gm-m">メモ（任意）</label>
<input type="text" id="gm-m" maxlength="120" placeholder="例：友だちと約束していた試合の途中だった">
<button type="button" id="gm-save" class="gm-main">この日を記録する</button>
<p class="gm-msg" id="gm-msg" role="status"></p>
</form>

<h2>週に1回、生活の様子</h2>
<p class="gm-s">時間の長さより、生活への影響を見ます。この1週間で当てはまるものを押してください（なければ何も押さずに記録）。</p>
<div class="gm-box">
<div class="gm-tg" id="gm-life"></div>
<button type="button" id="gm-lsave" class="gm-sub">今週の様子を記録する</button>
<p class="gm-msg" id="gm-lmsg" role="status"></p>
</div>

<div id="gm-out" hidden>
<h2>見えてきたこと（直近4週間）</h2>
<div class="gm-cal" id="gm-cal" aria-label="4週間の終わり方"></div>
<p class="gm-lg"><span><i class="c-self"></i>自分で</span><span><i class="c-cue"></i>声かけで</span><span><i class="c-wait"></i>区切りで</span><span><i class="c-fight"></i>揉めた</span></p>
<h3>揉めずに終われた声かけ</h3>
<ul class="gm-wk" id="gm-did-r"></ul>
<h3>揉めやすい時間帯</h3>
<ul class="gm-wk" id="gm-time-r"></ul>
<h3>生活の様子（週ごとの「当てはまる」の数）</h3>
<ul class="gm-wk" id="gm-life-r"></ul>
<h3>次に試すこと</h3>
<ul class="gm-next" id="gm-next"></ul>
<div class="gm-acts"><button type="button" id="gm-exp">記録を書き出す</button><label class="gm-imp">記録を読み込む<input type="file" id="gm-imp" accept="application/json"></label></div>
<p class="gm-s"><button type="button" class="gm-link" id="gm-clear">記録をすべて消す</button></p>
</div>

<h2>このノートの使い方で大事なこと</h2>
<ul>
<li><b>取り上げの根拠にしない。</b>中高生1,651人の調査では、親がルールを一方的に押しつけると感じている子ほど、問題のあるゲームの使い方が多い関連がありました。記録は、親が関わり方を見直すためのものです。</li>
<li><b>ごほうびや罰に使わない。</b>画面の時間をごほうびにしたり、罰として取り上げたりする家庭では、子どもの画面時間が長い関連がありました（幼児の研究）。</li>
<li><b>終わりは時計より「区切り」で。</b>幼児の家庭の記録では、遊びが自然に終わる区切りや、いつもの流れの中で終えると切り替えが楽になっていました。小学生以上のゲームで同じかはまだ確かめられていませんが、「この試合まで」と始める前に約束するのは試しやすい方法です。</li>
<li><b>やめにくさは珍しくない。</b>日本の10〜29歳の調査では、平日のゲームが1日1時間未満の人でも21.9%が「やめるべき時にやめられない」と答えていました。子どもの意志が弱い証拠ではありません。</li>
</ul>
<p>子どもと話してルールを決めるときは<a href="/rules/">スマホ・AIルールづくり（印刷用）</a>、終わりの声かけの言い方は<a href="/iikae/">声かけの言いかえ帳</a>が使えます。研究とデータは<a href="/game-cant-stop-time-limit-taking-away/">「子どもがゲームをやめられない・やめさせると怒る」</a>にまとめています。</p>
<h2>よくある質問</h2>
%FAQ%
<div class="sources"><h2>出典</h2><ol>
%SOURCES%
</ol></div>
<p class="note">このページは記録と集計だけを行い、診断や判定はしません。睡眠や学校など生活への大きな支障が長く続くときは、かかりつけの小児科、学校のスクールカウンセラー、自治体の相談窓口に相談できます。</p>
<script>
(function(){
var KEY='kosodate-game-v1',$=function(i){return document.getElementById(i)};
var END={self:'自分で終われた',cue:'声をかけて終われた',wait:'区切りまで待って終われた',fight:'揉めた・怒った'};
var WHAT={game:'ゲーム',sns:'SNS',video:'動画'},TIME={day:'休日の昼',eve:'夕方',night:'夜',bed:'寝る前'};
var DID=['始める前に「この試合まで」と約束した','終わる少し前に知らせた','やめる理由を伝えた','「あとどれくらい？」と聞いた','終わったあとにすることを用意した','取り上げると言った','強く言った','何も言わなかった'];
var LIFE=['寝る時間が遅くなった','朝起きられない日があった','宿題や学校に影響が出た','ごはんやお風呂を後回しにした','家族と話す時間が減った','イライラしていることが多かった'];
function load(){try{var x=JSON.parse(localStorage.getItem(KEY)||'{}')||{};x.d=x.d||{};x.w=x.w||{};return x}catch(e){return {d:{},w:{}}}}
function save(){try{localStorage.setItem(KEY,JSON.stringify(D));return true}catch(e){return false}}
function ds(t){var z=function(n){return (n<10?'0':'')+n};return t.getFullYear()+'-'+z(t.getMonth()+1)+'-'+z(t.getDate())}
function wk(t){var x=new Date(t.getFullYear(),t.getMonth(),t.getDate());x.setDate(x.getDate()-((x.getDay()+6)%7));return ds(x)}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var D=load(),sel={what:null,end:null,time:null};
$('gm-did').innerHTML=DID.map(function(t){return '<button type="button" aria-pressed="false">'+t+'</button>'}).join('');
$('gm-life').innerHTML=LIFE.map(function(t){return '<button type="button" aria-pressed="false">'+t+'</button>'}).join('');
function radio(id,key){[].forEach.call(document.querySelectorAll('#'+id+' button'),function(b){b.addEventListener('click',function(){sel[key]=b.getAttribute('data-v');
 [].forEach.call(document.querySelectorAll('#'+id+' button'),function(x){x.setAttribute('aria-pressed',x===b?'true':'false')})})})}
radio('gm-what','what');radio('gm-end','end');radio('gm-time','time');
function toggles(id){[].forEach.call(document.querySelectorAll('#'+id+' button'),function(b){b.addEventListener('click',function(){b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')==='true'?'false':'true')})})}
toggles('gm-did');toggles('gm-life');
function setRadio(id,v){[].forEach.call(document.querySelectorAll('#'+id+' button'),function(b){b.setAttribute('aria-pressed',b.getAttribute('data-v')===v?'true':'false')})}
function setTog(id,list){[].forEach.call(document.querySelectorAll('#'+id+' button'),function(b){b.setAttribute('aria-pressed',(list||[]).indexOf(b.textContent)>=0?'true':'false')})}
function picked(id){return [].filter.call(document.querySelectorAll('#'+id+' button'),function(b){return b.getAttribute('aria-pressed')==='true'}).map(function(b){return b.textContent})}
function pick(d){var r=D.d[d]||{};sel={what:r.w||null,end:r.e||null,time:r.t||null};setRadio('gm-what',sel.what);setRadio('gm-end',sel.end);setRadio('gm-time',sel.time);
 setTog('gm-did',r.a);$('gm-m').value=r.m||'';$('gm-msg').textContent=D.d[d]?'この日の記録があります。直すときは選び直して記録してください。':''}
$('gm-d').value=ds(new Date());$('gm-d').max=ds(new Date());pick($('gm-d').value);
$('gm-d').addEventListener('change',function(){if(this.value)pick(this.value)});
setTog('gm-life',(D.w[wk(new Date())]||{}).l);
$('gm-save').addEventListener('click',function(){var d=$('gm-d').value;
 if(!d){$('gm-msg').textContent='日付を選んでください。';return}
 if(!sel.end){$('gm-msg').textContent='終わる場面を1つ選んでください。';return}
 D.d[d]={w:sel.what,e:sel.end,t:sel.time,a:picked('gm-did'),m:$('gm-m').value.trim()};
 $('gm-msg').textContent=save()?d.replace(/-/g,'/')+' を記録しました。':'この端末では保存できませんでした（プライベートモードなど）。';draw()});
$('gm-lsave').addEventListener('click',function(){D.w[wk(new Date())]={l:picked('gm-life')};
 $('gm-lmsg').textContent=save()?'今週の様子を記録しました。':'この端末では保存できませんでした。';draw()});
function draw(){var keys=Object.keys(D.d).sort(),wks=Object.keys(D.w).sort();$('gm-out').hidden=!keys.length&&!wks.length;if($('gm-out').hidden)return;
 var today=new Date(),lim=ds(new Date(today.getFullYear(),today.getMonth(),today.getDate()-27)),rec=keys.filter(function(k){return k>=lim});
 var start=new Date(today.getFullYear(),today.getMonth(),today.getDate()-27);start.setDate(start.getDate()-((start.getDay()+6)%7));
 var h=['月','火','水','木','金','土','日'].map(function(w){return '<b>'+w+'</b>'}).join('');
 for(var t=new Date(start);t<=today;t.setDate(t.getDate()+1)){var k=ds(t),r=D.d[k];
  h+='<span class="'+(r?'c-'+r.e:'c-emp')+'" title="'+k+(r?' '+END[r.e]:'')+'">'+t.getDate()+'</span>'}
 $('gm-cal').innerHTML=h;
 var ok=function(r){return r.e!=='fight'};
 var dc={},dk={};rec.forEach(function(k){var r=D.d[k];(r.a||[]).forEach(function(a){dc[a]=(dc[a]||0)+1;if(ok(r))dk[a]=(dk[a]||0)+1})});
 var dl=Object.keys(dc).sort(function(a,b){return (dk[b]||0)/dc[b]-(dk[a]||0)/dc[a]||dc[b]-dc[a]});
 $('gm-did-r').innerHTML=dl.map(function(a){var p=Math.round((dk[a]||0)/dc[a]*100);return '<li><span>'+esc(a)+'</span><b style="width:'+p+'%"></b><em>'+(dk[a]||0)+' / '+dc[a]+'回</em></li>'}).join('')||'<li>「親がしたこと」を選んで記録すると出ます</li>';
 var tc={},tf={};rec.forEach(function(k){var r=D.d[k];if(!r.t)return;tc[r.t]=(tc[r.t]||0)+1;if(!ok(r))tf[r.t]=(tf[r.t]||0)+1});
 $('gm-time-r').innerHTML=Object.keys(TIME).filter(function(t){return tc[t]}).map(function(t){var p=Math.round((tf[t]||0)/tc[t]*100);return '<li><span>'+TIME[t]+'</span><b class="b-f" style="width:'+p+'%"></b><em>'+(tf[t]||0)+' / '+tc[t]+'回</em></li>'}).join('')||'<li>時間帯を選んで記録すると出ます</li>';
 $('gm-life-r').innerHTML=wks.slice(-8).map(function(w){var n=(D.w[w].l||[]).length;return '<li><span>'+w.slice(5).replace('-','/')+'の週</span><b class="b-l" style="width:'+Math.round(n/LIFE.length*100)+'%"></b><em>'+n+' / '+LIFE.length+'</em></li>'}).join('')||'<li>週に1回、生活の様子を記録すると出ます</li>';
 var nx=[],fights=rec.filter(function(k){return D.d[k].e==='fight'}).length,used=function(a){return dc[a]||0};
 if(used('取り上げると言った')||used('強く言った'))nx.push('取り上げや強い言い方を使った日がありました。取り上げをごほうびや罰に使う家庭ほど画面時間が長い関連があります。決めた時間と終わり方を、<a href="/rules/">子どもと話して決め直す</a>のを試してみてください。');
 if(fights&&!used(DID[0]))nx.push('揉めた日がありました。次は始める前に「この試合まで」「このステージまで」と、区切りで終わりを約束してみてください。');
 if(fights&&!used(DID[2]))nx.push('やめる理由（宿題・寝る時間を守るため など）を先に伝えると、押しつけと感じにくくなります。言い方は<a href="/iikae/">声かけの言いかえ帳</a>に例があります。');
 if(tf.bed||tf.night)nx.push('夜・寝る前に揉めやすいようです。寝る時間など生活の土台になる時間を、ゲームより先に決めておくと優先順位が崩れにくくなります。');
 var lw=wks.slice(-4),heavy=lw.filter(function(w){return (D.w[w].l||[]).length>=3}).length;
 if(heavy>=3)nx.push('生活の様子で当てはまるものが続いています。責めるより「最近どう？」と話を聞いてみてください。睡眠や学校への大きな支障が長く続くときは、かかりつけの小児科や相談窓口に相談できます。');
 var best=dl.filter(function(a){return dc[a]>=2&&(dk[a]||0)/dc[a]>=.7&&a!=='取り上げると言った'&&a!=='強く言った'})[0];
 if(best)nx.push('「'+esc(best)+'」の日は揉めずに終われることが多いようです。続けてみてください。');
 if(!nx.length)nx.push('記録が増えると、ここに次に試すことが出ます。まずは1週間、終わる場面だけでも押してみてください。');
 $('gm-next').innerHTML=nx.map(function(x){return '<li>'+x+'</li>'}).join('')}
$('gm-exp').addEventListener('click',function(){var a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(D)],{type:'application/json'}));a.download='game-mimamori-'+ds(new Date())+'.json';a.click()});
$('gm-imp').addEventListener('change',function(){var f=this.files[0];if(!f)return;var r=new FileReader();
 r.onload=function(){try{var x=JSON.parse(r.result),n=0;Object.keys(x.d||{}).forEach(function(k){if(/^\\d{4}-\\d{2}-\\d{2}$/.test(k)&&x.d[k]&&END[x.d[k].e]){D.d[k]=x.d[k];n++}});
  Object.keys(x.w||{}).forEach(function(k){if(/^\\d{4}-\\d{2}-\\d{2}$/.test(k))D.w[k]=x.w[k]});save();draw();pick($('gm-d').value);$('gm-msg').textContent=n+'日分を読み込みました。'}catch(e){$('gm-msg').textContent='読み込めないファイルでした。'}};r.readAsText(f)});
$('gm-clear').addEventListener('click',function(){if(!confirm('この端末の記録をすべて消します。よろしいですか？'))return;D={d:{},w:{}};save();draw();pick($('gm-d').value);setTog('gm-life',[])});
draw();
})();
</script>"""

CSS = (".gm-box{background:var(--card);border:1.5px solid var(--text);border-radius:18px;padding:20px;margin:20px 0 28px;display:grid;gap:6px;box-shadow:4px 4px 0 var(--text)}"
       ".gm-box label,.gm-q{font-size:14px;font-weight:700;margin:10px 0 2px;display:block}"
       ".gm-box input[type=date],.gm-box input[type=text]{font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);min-height:48px;width:100%}"
       ".gm-st{display:grid;grid-template-columns:1fr 1fr;gap:8px}.gm-ch{display:flex;flex-wrap:wrap;gap:8px}"
       ".gm-st button,.gm-ch button,.gm-tg button{font:inherit;font-size:15px;font-weight:700;min-height:48px;padding:10px 14px;border:1.5px solid var(--border);border-radius:12px;background:var(--bg);color:var(--text);cursor:pointer;display:flex;align-items:center;gap:8px;justify-content:center}"
       ".gm-st button[aria-pressed=true],.gm-ch button[aria-pressed=true],.gm-tg button[aria-pressed=true]{border-color:var(--text);background:#F6E3B0;color:#3B2F2A}"
       ".gm-st button[aria-pressed=true]::after,.gm-ch button[aria-pressed=true]::after,.gm-tg button[aria-pressed=true]::before{content:'\\2713';font-weight:900}"
       ".gm-tg{display:flex;flex-wrap:wrap;gap:8px}.gm-tg button{font-size:14px;font-weight:600;min-height:44px;border-radius:999px}"
       "i[class^=c-]{display:inline-block;width:14px;height:14px;border-radius:4px;flex:0 0 14px}"
       ".c-self{background:#4C9A6A}.c-cue{background:#7FB08E}.c-wait{background:#E8B23A}.c-fight{background:#B5523B}"
       ".gm-main,.gm-sub{font:inherit;font-size:17px;font-weight:800;margin-top:14px;padding:14px;border:1.5px solid var(--text);border-radius:12px;background:#E8B23A;color:#3B2F2A;cursor:pointer;min-height:52px}"
       ".gm-sub{background:var(--card);color:var(--text)}"
       ".gm-msg{font-size:14px;font-weight:700;min-height:1.4em}"
       ".gm-cal{display:grid;grid-template-columns:repeat(7,1fr);gap:4px;margin:10px 0}.gm-cal b{font-size:12px;text-align:center;color:var(--muted)}"
       ".gm-cal span{font-size:13px;font-weight:700;text-align:center;border-radius:8px;padding:8px 0;color:#fff}"
       ".gm-cal .c-emp{background:transparent;border:1px dashed var(--border);color:var(--muted)}.gm-cal .c-wait,.gm-cal .c-cue{color:#3B2F2A}"
       ".gm-lg{display:flex;flex-wrap:wrap;gap:6px 14px;font-size:13px}.gm-lg span{display:flex;align-items:center;gap:6px}"
       ".gm-wk{list-style:none;margin:8px 0}.gm-wk li{display:grid;grid-template-columns:minmax(0,1.6fr) 1fr 64px;gap:8px;align-items:center;font-size:14px;margin:8px 0}"
       ".gm-wk b{display:block;height:10px;background:#4C9A6A;border-radius:999px;min-width:2px}.gm-wk b.b-f{background:#B5523B}.gm-wk b.b-l{background:#E8B23A}.gm-wk em{font-style:normal;text-align:right}"
       ".gm-next{margin:8px 0 8px 20px}.gm-next li{font-size:15px;line-height:1.8;margin:8px 0}.gm-next a{color:var(--link)}"
       ".gm-acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:16px}.gm-acts button,.gm-imp{font:inherit;font-size:15px;font-weight:800;padding:12px;border:1.5px solid var(--text);border-radius:12px;background:var(--card);color:var(--text);cursor:pointer;min-height:52px;text-align:center}"
       ".gm-imp input{display:block;font-size:12px;margin:6px auto 0;max-width:100%}"
       ".gm-s{font-size:13px;color:var(--muted);margin-top:10px;line-height:1.8}"
       ".gm-link{font:inherit;font-size:13px;background:none;border:0;color:var(--link);text-decoration:underline;cursor:pointer;padding:8px 0}"
       ".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".xbody p a,.sources a,.note a{color:var(--link)}"
       ".xbody>details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}.xbody>details summary{cursor:pointer;font-weight:700;font-size:15px}.xbody>details p{font-size:15px;margin-top:8px}"
       ".sources{margin-top:48px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;word-break:break-all}"
       ".note{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}")

PAGE = {"path": "game-mimamori", "title": "ゲーム・SNSの見守りノート",
        "seo_title": "子どもがゲーム・SNSをやめられない 記録｜取り上げる前に、終わる場面と声かけを1タップで見直す見守りノート",
        "date": "2026-10-13",
        "desc": "子どもがゲームやSNSをやめられないときに親が使うノート。終わる場面と声かけを1タップで記録し、揉めずに終われた声かけ・揉めやすい時間帯・生活の様子と、次に試すことがわかります。取り上げや監視はしません。記録は端末の中だけ。無料・登録不要。",
        "body": BODY.replace("%LD%", LD).replace("%FAQ%", faq_html).replace("%SOURCES%", SOURCES),
        "css": CSS}
