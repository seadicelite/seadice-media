"""子育てデータのWebツールページ。実行すると media/kosodate-pages.json に書き込む(extras.pages が /{path}/ を書き出す)。

  python3 media/kosodate_tools.py && python3 media/build.py kosodate

判定の文言は、出典照合済みの記事の結論だけを使う(AIには判定・アドバイスを書かせない)。
画像の読み取りは Worker kosodate-screen(/Users/hidenori/Developer/kosodate-screen-worker)。数字を読むだけ。
新しいツールを足すときは docs/quality/tool.md のページの型に合わせ、PAGES に追加する。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "https://kosodate.seadice.win/screen-time-check/"
WORKER = "https://kosodate-screen.seadice-lite.workers.dev/"

FAQ = [
    ("子どものスクリーンタイムは1日何時間までが目安ですか？",
     "WHO（2019年）は、1歳以下は画面を見せないこと、2〜4歳は1日1時間まで（少ないほどよい）を勧めています。小学生以上には決まった時間の線はなく、寝る前1時間は使わないことが研究から見た優先事項です。"),
    ("スクリーンタイムの画像はどこかに保存されますか？",
     "SEADICEは保存しません。画像は数字を読み取るためだけにAI（Anthropic社のClaude）へ送られ、SEADICEは画像も読み取った数字も残しません。手で入力した数字は、ブラウザの中だけで判定します。"),
    ("学習アプリやビデオ通話も時間に入れるべきですか？",
     "合計には入れて判定しますが、内訳で分けて表示します。研究では、教育的な内容や親子で一緒に見ることは言葉の発達とよい関連が見られており、時間だけでなく中身も一緒に見ることが大切です。"),
    ("判定で「目安より多め」と出たら、発達に問題があるということですか？",
     "いいえ。研究が示しているのは多くの子どもの傾向で、1人の子の発達を判定するものではありません。気になる様子があるときは、かかりつけの小児科や自治体の子育て相談に相談できます。"),
]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "子どものスクリーンタイム判定", "url": URL, "applicationCategory": "LifestyleApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "子どもの年齢とスクリーンタイムのスクショ（または時間）を入れると、WHOの目安と研究からわかっていることに照らして、いまの使い方と今日からできることを表示します。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}
LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")

faq_html = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ))

BODY = """<script type="application/ld+json">%LD%</script>
<p>子どもの年齢と、スマホ・タブレットのスクリーンタイムの画面（スクショ）を入れると、WHOの目安と研究でわかっていることに照らして、いまの使い方と今日からできることを表示します。無料・広告なし・登録不要です。</p>
<form class="st-box" id="st" onsubmit="return false">
<label for="st-age">お子さんの年齢</label>
<select id="st-age" required>
<option value="">選んでください</option><option value="u1">0歳</option><option value="a1">1歳</option><option value="a2">2〜4歳</option><option value="a5">5歳〜小学生</option><option value="jh">中学生</option><option value="hs">高校生</option>
</select>
<div class="st-up">
<p class="st-h">スクショから読み取る</p>
<p class="st-s">iPhoneの「設定 → スクリーンタイム → すべてのアクティビティを確認」、Androidの「Digital Wellbeing」やファミリーリンクの画面を撮って選んでください。お子さんの名前が写っている場合は、隠してから選んでください。</p>
<label class="st-file" for="st-img">スクショを選ぶ</label>
<input type="file" id="st-img" accept="image/*">
<p class="st-msg" id="st-msg" aria-live="polite"></p>
</div>
<p class="st-h">時間を確認・入力する</p>
<label>1日の合計（週の画面なら1日の平均）</label>
<div class="st-hm"><input type="number" id="st-th" inputmode="numeric" min="0" max="24" placeholder="0"><span>時間</span><input type="number" id="st-tm" inputmode="numeric" min="0" max="59" placeholder="0"><span>分</span></div>
<details class="st-more"><summary>内訳も入れる（わかる分だけ・分単位）</summary>
<div class="st-grid">
<label>動画（YouTubeなど）<input type="number" id="st-video" inputmode="numeric" min="0" placeholder="分"></label>
<label>ゲーム<input type="number" id="st-game" inputmode="numeric" min="0" placeholder="分"></label>
<label>SNS<input type="number" id="st-sns" inputmode="numeric" min="0" placeholder="分"></label>
<label>学習アプリ・電子書籍<input type="number" id="st-learning" inputmode="numeric" min="0" placeholder="分"></label>
<label>LINE・通話<input type="number" id="st-message" inputmode="numeric" min="0" placeholder="分"></label>
</div></details>
<label for="st-bed">寝る前の1時間に使っていますか？</label>
<select id="st-bed"><option value="u">わからない</option><option value="y">使っている日が多い</option><option value="n">ほとんど使わない</option></select>
<div id="st-tog-w"><label for="st-tog">動画は親子で一緒に見ることが多いですか？</label>
<select id="st-tog"><option value="u">わからない</option><option value="y">一緒に見ることが多い</option><option value="n">ひとりで見ることが多い</option></select></div>
<button type="submit" id="st-b">判定する</button>
<div id="st-out" class="st-out" aria-live="polite" hidden></div>
</form>
<p class="answer"><strong>目安：1歳以下は画面を見せない、2〜4歳は1日1時間まで（WHO）。</strong>小学生以上に決まった時間の線はなく、寝る前1時間は使わないことと、何を誰と見るかが研究から見た優先事項です。</p>
<h2>判定のしかた</h2>
<p>時間の線は、WHOが2019年に出した5歳未満の指針だけを使っています。5歳以上には公的な時間の線がないため、時間で「多い・少ない」は出さず、研究で関連が繰り返し確認されている点（寝る前の使用、SNS、ゲームと生活、近くを見る時間）を表示します。</p>
<table class="st-t"><caption>年齢ごとの判定</caption><thead><tr><th>年齢</th><th>時間の目安</th><th>あわせて見ること</th></tr></thead><tbody>
<tr><td>0〜1歳</td><td>見せない（ビデオ通話を除く）</td><td>親子で一緒に見ること</td></tr>
<tr><td>2〜4歳</td><td>1日1時間まで・少ないほどよい</td><td>親子で一緒に見ること、寝る前の使用</td></tr>
<tr><td>5歳〜小学生</td><td>決まった線はなし</td><td>寝る前の使用、ゲームと生活のリズム、近くを見る時間</td></tr>
<tr><td>中学生・高校生</td><td>決まった線はなし</td><td>寝る前の使用、SNSの時間、ゲームと生活のリズム</td></tr>
</tbody></table>
<div class="note">スクショは、数字を読み取るためだけにAI（Claude）へ送ります。判定と表示する文章は、AIではなく、出典と照らし合わせた<a href="/kids-screen-time-hours/">子育てデータの記事</a>の結論から出しています。読み取りは1日3回までです。</div>
<h2>入力例</h2>
<table class="st-t"><thead><tr><th>年齢</th><th>1日の合計</th><th>表示される内容</th></tr></thead><tbody>
<tr><td>3歳</td><td>1時間40分（動画のみ）</td><td>目安より40分多め。親子で一緒に見ること、終わり方の声かけ</td></tr>
<tr><td>小学4年生</td><td>2時間30分（寝る前も使う）</td><td>時間の線はなし。寝る前1時間の使用と、近くを見る時間・外遊び</td></tr>
<tr><td>中学2年生</td><td>3時間（SNS1時間半）</td><td>時間の線はなし。SNSの時間と、寝る前の使用</td></tr>
</tbody></table>
<h2>よくある質問</h2>
%FAQ%
<h2>くわしく読む</h2>
<p>年齢別の目安は<a href="/kids-screen-time-hours/">子どものスマホ・動画は何時間まで？</a>、ルールの決め方は<a href="/family-screen-time-rules-research/">子どものスマホルールの作り方</a>で解説しています。家族で話し合うときは<a href="/rules/">家庭のルール表（印刷用）</a>も使えます。</p>
<div class="sources"><h2>出典</h2><ol>
<li>World Health Organization (2019). To grow up healthy, children need to sit less and play more. <a href="https://www.who.int/news/item/24-04-2019-to-grow-up-healthy-children-need-to-sit-less-and-play-more" target="_blank" rel="noopener">WHO</a></li>
<li>Council on Communications and Media, American Academy of Pediatrics (2016). Media and Young Minds. <i>Pediatrics</i>. <a href="https://doi.org/10.1542/peds.2016-2591" target="_blank" rel="noopener">doi:10.1542/peds.2016-2591</a></li>
<li>Hale, L., &amp; Guan, S. (2015). Screen time and sleep among school-aged children and adolescents: a systematic literature review. <i>Sleep Medicine Reviews</i>. <a href="https://doi.org/10.1016/j.smrv.2014.07.007" target="_blank" rel="noopener">doi:10.1016/j.smrv.2014.07.007</a></li>
<li>Madigan, S., et al. (2020). Associations Between Screen Use and Child Language Skills: A Systematic Review and Meta-analysis. <i>JAMA Pediatrics</i>. <a href="https://doi.org/10.1001/jamapediatrics.2020.0327" target="_blank" rel="noopener">doi:10.1001/jamapediatrics.2020.0327</a></li>
<li>そのほか、各ポイントのリンク先の記事に出典を載せています。</li>
</ol></div>
<script>
(function(){
var W='%WORKER%',$=function(i){return document.getElementById(i)},msg=$('st-msg');
var K=['video','game','sns','learning','message'];
function n(i){var v=parseInt($(i).value,10);return isNaN(v)||v<0?0:v}
function setN(i,v){$(i).value=(v===null||v===undefined)?'':v}
function hm(m){var h=Math.floor(m/60),r=m%60;return (h?h+'時間':'')+(r||!h?r+'分':'')}
function young(a){return a==='u1'||a==='a1'||a==='a2'}
$('st-age').addEventListener('change',function(){$('st-tog-w').hidden=!(young(this.value)||this.value==='')});
$('st-img').addEventListener('change',function(){
 var f=this.files&&this.files[0];if(!f)return;
 msg.textContent='読み取っています（10秒ほどかかります）…';
 var img=new Image(),u=URL.createObjectURL(f);
 img.onload=function(){
  var s=Math.min(1,1600/Math.max(img.width,img.height)),c=document.createElement('canvas');
  c.width=Math.round(img.width*s);c.height=Math.round(img.height*s);c.getContext('2d').drawImage(img,0,0,c.width,c.height);URL.revokeObjectURL(u);
  var d=c.toDataURL('image/jpeg',0.85).split(',')[1];
  fetch(W,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({image:d,type:'image/jpeg'})})
  .then(function(r){return r.json().then(function(j){return {s:r.status,j:j}})})
  .then(function(x){
   if(x.s===429){msg.textContent='本日の読み取り回数の上限に達しました。明日またお試しください。下の欄に時間を入れれば、いますぐ判定できます。';return}
   var r=x.j.result;
   if(!r||!r.is_screen_time||r.total_min===null){msg.textContent='利用時間を読み取れませんでした。スクリーンタイムの画面か確認するか、下の欄に時間を入れてください。';return}
   setN('st-th',Math.floor(r.total_min/60));setN('st-tm',r.total_min%60);
   var sum={};K.forEach(function(k){sum[k]=0});
   (r.apps||[]).forEach(function(a){if(a.min&&sum[a.kind]!==undefined)sum[a.kind]+=a.min});
   K.forEach(function(k){setN('st-'+k,sum[k]||'')});
   if(r.late_min){$('st-bed').value='y'}
   $('st-img').value='';
   msg.textContent='読み取りました'+(r.period==='week_avg'?'（1日の平均）':'')+'。数字が画面と合っているか確かめてから「判定する」を押してください。'+(x.j.remaining>=0?'（きょうはあと'+x.j.remaining+'回）':'');
  }).catch(function(){msg.textContent='通信に失敗しました。下の欄に時間を入れれば判定できます。'});
 };
 img.onerror=function(){msg.textContent='画像を開けませんでした。別の画像を選ぶか、下の欄に時間を入れてください。'};
 img.src=u;
});
$('st').addEventListener('submit',function(){
 var a=$('st-age').value,o=$('st-out');
 if(!a){$('st-age').focus();return}
 var t=n('st-th')*60+n('st-tm'),b={};K.forEach(function(k){b[k]=n('st-'+k)});
 var bed=$('st-bed').value,tog=$('st-tog').value,P=[],head,lv='',bar='';
 var nc=Math.max(0,t-b.message);
 if(a==='u1'||a==='a1'){
  head=nc>0?'WHOの目安では、この年齢はビデオ通話以外の画面を見せないことが勧められています。':'WHOの目安どおりです。';lv=nc>0?'目安より多め':'目安どおり';
 }else if(a==='a2'){
  var d=t-60;lv=t<=60?'目安の範囲':t<=120?'目安より'+hm(d)+'多め':'目安の2倍を超えています';
  head='WHOの目安は1日1時間まで（少ないほどよい）です。';
  bar='<div class="st-bar"><span style="width:'+Math.min(100,t/180*100)+'%"></span><i style="left:'+(60/180*100)+'%"></i></div><p class="st-bl">線＝目安の1時間</p>';
 }else{
  head='小学生以上には、何時間までという決まった線はまだありません。時間より、次の点を見てください。';
 }
 if(bed==='y')P.push(['寝る前の使用','就寝前のスマホ・動画の利用は、子どもの睡眠時間を縮め、寝つきを遅らせる方向に働くことが、複数の研究で繰り返し確認されています。','寝る1時間前にスマホを置き場所に戻し、寝室に画面のある機器を置かない','/bedtime-screen-sleep/']);
 if(young(a)&&tog!=='y'&&(b.video>0||t>0))P.push(['親子で一緒に見る','スクリーン時間全体は言語スキルの低さと関連していますが、教育的な内容や親子で一緒に見ることは、言語スキルの高さと関連しています。','できるだけ一緒に見て、見た後に内容について話しかける','/screen-time-language-development-toddler/']);
 if((a==='a2'||a==='a5')&&b.video>=30)P.push(['動画の終わらせ方','「ダメ」と頭ごなしに言うより、気持ちを一度認めてから次の見通しを伝える声かけのほうが、対立を減らしやすいとわかっています。','気持ちを一度認める、終わりの見通しを先に伝える、終わった後の楽しみを用意する','/youtube-more-please-how-to-say-no/']);
 if((a==='jh'||a==='hs'||a==='a5')&&b.sns>0)P.push(['SNSの時間','SNSを使う時間が増えるほど、読み書きや記憶のテストの点数が低くなる関連が、2年間の追跡調査（6,554人）でみられました。原因かどうかはまだわかっていません。','睡眠や運動の時間も確保しながら、使い方を子どもと一緒に見直す','/social-media-cognitive-performance-decline/']);
 if(!young(a)&&b.game>=60)P.push(['ゲームと生活','ゲームを「やめられない」子どもの多くは障害ではありません。プレイ時間の長さより、生活のリズムや学校・友人関係に支障が出ていないかが目安です。','生活のリズムが保てているか、学校や友人関係に支障がないかを見る','/gaming-disorder-children-research/']);
 if(!young(a)&&t>=120)P.push(['近くを見る時間','近くで見る時間（読書・スマホ・タブレット）が長い子どもほど、近視のリスクが高いという関連があります。屋外活動は近視を防ぐ方向に働きます。','屋外で過ごす時間を増やし、近くを見続けない工夫をする','/screen-time-myopia-eyesight/']);
 P.push(['ルールを具体的に決める','具体的なルールを決めて守らせる関わり方は、子どものスクリーンタイムが推奨時間内に収まりやすいことと関連していました。','「いつ・何を・何分まで」を家族で具体的に決める','/family-screen-time-rules-research/']);
 var mx=Math.max.apply(null,K.map(function(k){return b[k]})),bd='';
 if(mx>0){var L={video:'動画',game:'ゲーム',sns:'SNS',learning:'学習',message:'LINE・通話'};bd='<ul class="st-bd">'+K.filter(function(k){return b[k]>0}).map(function(k){return '<li><span>'+L[k]+'</span><b style="width:'+Math.max(4,b[k]/Math.max(t,mx)*100)+'%"></b><em>'+hm(b[k])+'</em></li>'}).join('')+'</ul>'}
 o.hidden=false;
 o.innerHTML='<p class="st-l">1日の合計</p><p class="st-v">'+hm(t)+'</p>'+(lv?'<p class="st-lv">'+lv+'</p>':'')+bar+'<p>'+head+'</p>'+bd
  +'<h3>気をつけたい点</h3>'+P.map(function(p){return '<div class="st-p"><b>'+p[0]+'</b><p>'+p[1]+'</p><p class="st-do">今日から：'+p[2]+'</p><a href="'+p[3]+'">根拠の記事を読む</a></div>'}).join('')
  +'<p class="st-n">研究が示しているのは多くの子どもの傾向で、お子さん1人の発達を判定するものではありません。責めるためではなく、減らせるところから1つ選ぶための目安です。</p>';
 o.scrollIntoView({behavior:'smooth',block:'start'});
});
})();
</script>"""

BODY = BODY.replace("%LD%", LD).replace("%FAQ%", faq_html).replace("%WORKER%", WORKER)

CSS = (".st-box{background:var(--card);border:1.5px solid var(--text);border-radius:18px;padding:20px;margin:20px 0 28px;display:grid;gap:8px;box-shadow:4px 4px 0 var(--text)}"
       ".st-box label{font-size:14px;font-weight:700;margin-top:6px;display:block}"
       ".st-box input,.st-box select{font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);min-height:48px;width:100%}"
       ".st-up{background:var(--bg);border:1.5px dashed var(--accent);border-radius:14px;padding:16px;margin:10px 0}"
       ".st-h{font-size:15px;font-weight:800;margin-top:6px}.st-s{font-size:13px;color:var(--muted);line-height:1.7;margin:4px 0 10px}"
       ".st-file{display:block;text-align:center;background:var(--accent);color:#fff!important;border-radius:12px;padding:14px;font-size:16px;font-weight:800;cursor:pointer;margin:0!important}"
       ".st-up input[type=file]{position:absolute;width:1px;height:1px;opacity:0}.st-up:focus-within .st-file{outline:3px solid var(--accent2);outline-offset:2px}"
       ".st-msg{font-size:14px;line-height:1.7;margin-top:10px}.st-msg:empty{display:none}"
       ".st-hm{display:flex;align-items:center;gap:8px}.st-hm input{width:90px}.st-hm span{font-size:15px}"
       ".st-more{background:none!important;border:0!important;padding:0!important;margin:4px 0!important}.st-more summary{font-size:14px;color:var(--link);font-weight:700;padding:8px 0}"
       ".st-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.st-grid label{font-size:13px;font-weight:600}"
       ".st-box button{font:inherit;font-size:17px;font-weight:800;margin-top:14px;padding:14px;border:1.5px solid var(--text);border-radius:12px;background:#E8B23A;color:var(--text);cursor:pointer;min-height:52px}"
       ".st-out{margin-top:16px;padding-top:16px;border-top:1px solid var(--border);font-size:15px;line-height:1.8}"
       ".st-l{font-size:13px;color:var(--muted)}.st-v{font-size:34px;font-weight:900;color:var(--accent);line-height:1.3}"
       ".st-lv{display:inline-block;font-size:14px;font-weight:800;border:1.5px solid var(--text);border-radius:999px;padding:2px 12px;margin:6px 0}"
       ".st-bar{position:relative;height:14px;background:var(--bg);border:1px solid var(--border);border-radius:999px;margin:10px 0 2px;overflow:hidden}.st-bar span{display:block;height:100%;background:var(--accent)}.st-bar i{position:absolute;top:-2px;bottom:-2px;width:3px;background:var(--text)}.st-bl{font-size:12px;color:var(--muted)}"
       ".st-bd{list-style:none;margin:12px 0}.st-bd li{display:grid;grid-template-columns:76px 1fr 72px;gap:8px;align-items:center;font-size:13px;margin:6px 0}.st-bd b{display:block;height:10px;background:var(--accent2);border-radius:999px}.st-bd em{font-style:normal;text-align:right}"
       ".st-out h3{font-size:16px;font-weight:900;margin:22px 0 10px}"
       ".st-p{background:var(--bg);border:1px solid var(--border);border-left:5px solid var(--accent2);border-radius:12px;padding:14px 16px;margin:10px 0}.st-p b{font-size:15px}.st-p p{font-size:14px;margin:4px 0}.st-do{font-weight:700}.st-p a{font-size:13px;color:var(--link)}"
       ".st-n{font-size:13px;color:var(--muted);margin-top:14px}"
       ".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".st-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.st-t caption{text-align:left;font-size:13px;color:var(--muted);margin-bottom:6px}"
       ".st-t th,.st-t td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top}.st-t th{background:var(--card)}"
       ".note{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}.note a,.sources a,.xbody p a{color:var(--link)}"
       ".xbody>details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}.xbody>details summary{cursor:pointer;font-weight:700;font-size:15px}.xbody>details p{font-size:15px;margin-top:8px}"
       ".sources{margin-top:48px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;word-break:break-all}")

PAGES = [{"path": "screen-time-check", "title": "子どものスクリーンタイム判定",
          "seo_title": "子どものスクリーンタイム判定｜スクショで年齢別の目安（WHO）と比べる",
          "date": "2026-10-06",
          "desc": "子どもの年齢とスクリーンタイムのスクショを入れると、WHOの目安（2〜4歳は1日1時間まで）と研究に照らして、いまの使い方と今日からできることを表示。無料・広告なし・登録不要。",
          "body": BODY, "css": CSS}]

if __name__ == "__main__":
    f = ROOT / "media/kosodate-pages.json"
    ps = json.loads(f.read_text())
    keep = [p for p in ps if p["path"] not in {x["path"] for x in PAGES}]
    f.write_text(json.dumps(keep + PAGES, ensure_ascii=False, indent=2) + "\n")
    print("wrote", [p["path"] for p in PAGES])
