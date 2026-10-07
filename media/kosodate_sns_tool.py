"""AI時代の子育て「AIで練習するSNS」(/sns-practice/)。kosodate_tools.py が読み込む。

- ステップモード: 20の場面をレベル順にクリアする。全部クリアで修了証(印刷できる)。進み具合は localStorage だけ
- フリーモード: 自由に投稿すると、AIのクラスメイトが短いコメントを返す。ときどき「事件」(ステップモードの場面)が混ざる。5投稿で終わり

相手役の危ない文章は kosodate_sns_scenes.py に書いたものだけ(AIに演じさせない)。
AIは「返事・投稿の判定と短いコーチ」と「クラスメイトの明るい短いコメント」だけ。Worker 側でもコメントを検査する。
AIが使えないとき(上限・通信エラー)も、選択肢と用意したコメントで最後まで練習できる。返事・投稿は保存しない。

Worker の判定観点(steps.js)もここから書き出す:
  python3 media/kosodate_sns_tool.py --worker
"""
import json
import sys
from pathlib import Path

from kosodate_sns_scenes import CLASSMATES, FALLBACK_COMMENTS, FREE_EVENTS, LEVELS, SCENES

URL = "https://kosodate.seadice.win/sns-practice/"
API = "https://kosodate-ai.seadice-home.workers.dev/"

FAQ = [
    ("子どもにSNSを使わせる前に、何を練習させればいいですか？",
     "知らない人に学年・学校・写真を教えない、悪口にのらない・広めない、いやなことがあったら大人に話す、リンクを押さない、の4つが基本です。このページでは20の場面をレベル順に練習でき、フリーモードでは自由に投稿しながら試せます。"),
    ("練習の相手は本物の人ですか？",
     "いいえ。知らない人やいじめ役などの危ない相手役は、SEADICEがあらかじめ用意した練習用の文章です。AI（Anthropic社のClaude）が行うのは、お子さんの返事や投稿が安全かの判定と短いアドバイス、フリーモードのクラスメイト役の短い明るいコメントだけです。"),
    ("子どもが書いた返事や投稿は保存されますか？",
     "保存されません。判定のためだけにAIへ送られ、SEADICEは残しません。名前・電話番号・学校名のような入力は、送る前に画面上で止めます。クリアした場面と修了証の名前は、この端末の中だけに保存されます。"),
    ("何歳から使えますか？",
     "ひらがなが読める小学校低学年から、おうちの人と一緒に使えます。レベル3はSNSを使い始める前の小学校高学年〜中学生向けです。"),
]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "AIで練習するSNS（子ども向け）", "url": URL, "applicationCategory": "EducationalApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "本物のSNSを使う前に、知らない人からのDM・悪口・写真の投稿・詐欺リンク・闇バイトのさそいなど20の場面を練習できる子ども向けツール。自由に投稿できるフリーモードつき。返事にAIがアドバイス。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}
LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
faq_html = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ))
lvname = dict(LEVELS)
scene_rows = "".join(f'<tr><td>{lvname[s["lv"]].split(" ")[0]}</td><td>{s["title"]}</td><td>{s["steps"][0]["point"].split("。")[0]}。</td></tr>' for s in SCENES)
DATA = {"levels": LEVELS, "events": FREE_EVENTS, "fallback": FALLBACK_COMMENTS, "mates": CLASSMATES,
        "scenes": [{"id": s["id"], "lv": s["lv"], "title": s["title"], "kicker": s["kicker"],
                    "steps": [{"id": t["id"], "msgs": t["msgs"], "choices": t["choices"]} for t in s["steps"]]} for s in SCENES]}

BODY = """<script type="application/ld+json">%LD%</script>
<p>本物のSNSを使う前に、知らない人からのDMや悪口、写真の投稿などを、安全に練習できる子ども向けのページです。20の場面をクリアしていく「ステップモード」と、自由に投稿して試す「フリーモード」があります。無料・広告なし・登録不要です。</p>
<div class="sp-app" id="sp">
<div class="sp-top"><b>れんしゅうSNS</b><span>あいては練習用のキャラクターだよ</span></div>
<div class="sp-tabs" role="tablist"><button type="button" id="sp-t1" role="tab" aria-selected="true">ステップモード</button><button type="button" id="sp-t2" role="tab" aria-selected="false">フリーモード</button></div>
<div id="sp-step">
<div id="sp-home">
<p class="sp-hi">「こんなとき、どうする？」を練習しよう。やってみたい場面をえらんでね。</p>
<p class="sp-prog" id="sp-prog"></p>
<div id="sp-levels"></div>
<div class="sp-cert-w" id="sp-cert-w"></div>
<p class="sp-rule">練習のおやくそく：ほんとうの名前・学校・住所・電話番号は書かないでね。</p>
</div>
<div id="sp-play" hidden>
<div class="sp-feed" id="sp-feed" aria-live="polite"></div>
<div class="sp-ans" id="sp-ans"></div>
<button type="button" class="sp-next" id="sp-next" hidden>つぎへ</button>
</div>
<div id="sp-end" hidden></div>
</div>
<div id="sp-free" hidden>
<p class="sp-hi">自由に投稿してみよう。クラスメイト（AI）がコメントしてくれるよ。ときどき、練習の「事件」がおきるかも。5回投稿したらおしまい。</p>
<div class="sp-comp"><textarea id="sp-post" maxlength="80" rows="2" placeholder="きょうあったこと、好きなものなど"></textarea>
<label for="sp-pic">写真をつける</label><select id="sp-pic"><option value="">つけない</option><option value="cat">ねこの写真</option><option value="sky">きれいな空の写真</option><option value="lunch">きょうのおやつの写真</option><option value="house">家の前で撮った自分の写真</option><option value="name">名札がうつった自分の写真</option><option value="friend">友だちのへん顔の写真</option></select>
<button type="button" id="sp-pbtn">投稿する</button><p class="sp-left" id="sp-left"></p></div>
<div class="sp-tl" id="sp-tl" aria-live="polite"></div>
</div>
</div>
<p class="answer"><strong>SNSを始める前に練習したいのは「教えない・のらない・押さない・話す」の4つです。</strong>知らない人に学年や写真を教えない、悪口にのらない、リンクを押さない、困ったら大人に話す。この4つを20の場面で体験できます。</p>
<h2>練習できる20の場面</h2>
<table class="sp-t"><thead><tr><th>レベル</th><th>場面</th><th>安全な返し方の目安</th></tr></thead><tbody>%ROWS%</tbody></table>
<h2>おうちの人へ：練習のあとに話したいこと</h2>
<ul>
<li><b>「何かあったら話してね。話してくれたら怒らないよ」と先に伝える。</b>サイバーいじめは子どもから話しにくく、親からは見えにくい問題です。日頃からネットの話を否定せずに聞く関わりが、研究の傾向と合っています（<a href="/cyberbullying-children-parent-awareness/">サイバーいじめの記事</a>）。</li>
<li><b>知らない人とのやりとりは、禁止より「一緒に見る」。</b>一律に禁止するより、一緒にゲームをする・話を聞くといった関わりの方が、見知らぬ人とのリスクを減らしやすいとわかっています（<a href="/online-gaming-strangers-chat-risk/">オンラインゲームの記事</a>）。</li>
<li><b>写真は「本人ならどう感じるか」。</b>投稿前に本人の気持ちを考え、特定されやすい情報を避け、公開範囲を絞るのが基本の対策です（<a href="/sharenting-sns-photo-risk/">写真の投稿の記事</a>）。</li>
<li><b>AIへの相談も否定しない。</b>深刻な悩みでは、AIは危険に気づけない・大人につなげないことがあります。「AIに話したことも人に話していい」と伝えておきます（<a href="/ai-chatbot-worry-consultation-safety/">AIへの相談の記事</a>）。</li>
</ul>
<p>修了証は「スマホを持つ前の約束」に使えます。家族のSNS・スマホのルールは<a href="/rules/">わが家のルールづくり</a>で作って印刷できます。</p>
<div class="note">危ない相手役の文章は、SEADICEが用意した練習用のものです。AI（Anthropic社のClaude）が行うのは、返事・投稿の判定と短いアドバイス、クラスメイト役の短いコメントだけで、入力は保存しません。AIは1日に決まった回数までで、それを超えても練習は続けられます。</div>
<h2>よくある質問</h2>
%FAQ%
<script>
(function(){
var D=%DATA%,API='%API%',$=function(i){return document.getElementById(i)},KEY='kosodate-sns-v1',cur,si,res,busy=false,aiOff=false;
var V={safe:['あんしん','ok'],careful:['ちょっと注意','mid'],risky:['きけん','ng']},BY={};D.scenes.forEach(function(s){s.steps.forEach(function(t){BY[t.id]=t})});
var PI=[/\\d{2,4}-?\\d{2,4}-?\\d{3,4}/,/\\d{7,}/,/@/,/(小学校|中学校|小学|中学|学園)/,/(丁目|番地|町|市|区|村)\\S{0,3}\\d/,/(住所|でんわ|電話)/];
var PICS={cat:['ねこの写真','safe'],sky:['空の写真','safe'],lunch:['おやつの写真','safe'],house:['家の前の自分の写真','risky','家の外がうつると、住んでいる場所の手がかりになるよ。写真を変えようね。'],name:['名札がうつった写真','risky','名札には名前や学校が書いてあるよ。うつっていない写真にしよう。'],friend:['友だちのへん顔','careful','人の写真は、のせる前に本人に「のせていい？」ときこうね。']};
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){return {}}}
function save(o){try{localStorage.setItem(KEY,JSON.stringify(o))}catch(e){}}
function hasPI(t){for(var k=0;k<PI.length;k++)if(PI[k].test(t))return true;return false}
function el(cls,html){var d=document.createElement('div');d.className=cls;d.innerHTML=html;return d}
function coachEl(v,txt,ai){return el('sp-c sp-'+V[v][1],'<b>'+V[v][0]+'</b><p>'+esc(txt)+'</p>'+(ai?'<small>AIコーチ</small>':''))}
function call(path,body){return fetch(API+path,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)}).then(function(r){return r.json().then(function(j){if(r.status!==200||!j.result)throw r.status;return j.result})})}
/* 返事の入力(ステップ・フリー共通) */
function replyBox(box,feed,t,onDone){
 box.innerHTML='<p class="sp-q">あなたなら、どう返す？</p><div class="sp-ch">'+t.choices.map(function(c,k){return '<button type="button" data-k="'+k+'">'+esc(c[0])+'</button>'}).join('')+'</div><div class="sp-free"><input type="text" maxlength="80" placeholder="自分のことばで書いてもいいよ" enterkeyhint="send"><button type="button">送る</button></div>';
 var inp=box.querySelector('input'),sb=box.querySelector('.sp-free button');
 function fin(me,v,fb,ai){feed.appendChild(el('sp-m sp-me','<p>'+esc(me)+'</p>'));var c=coachEl(v,fb,ai);feed.appendChild(c);box.innerHTML='';c.scrollIntoView({behavior:'smooth',block:'nearest'});onDone(v)}
 [].forEach.call(box.querySelectorAll('.sp-ch button'),function(b){b.onclick=function(){var c=t.choices[+b.getAttribute('data-k')];fin(c[0],c[1],c[2],false)}});
 function send(){if(busy)return;var x=inp.value.trim();if(!x)return;
  if(hasPI(x)){box.insertBefore(coachEl('risky','ストップ！それは名前・学校・住所・電話番号みたいな「個人情報」かも。練習でも書かないでね。',false),box.firstChild);inp.value='';return}
  if(aiOff){box.insertBefore(coachEl('careful','AIのコーチはきょうはお休み。上のボタンからえらんでね。',false),box.firstChild);return}
  busy=true;sb.disabled=true;sb.textContent='…';
  call('coach',{step:t.id,reply:x}).then(function(r){busy=false;if(!V[r.verdict])throw 0;fin(x,r.verdict,r.feedback,true)})
  .catch(function(s){busy=false;aiOff=true;sb.disabled=false;sb.textContent='送る';box.insertBefore(coachEl('careful',(s===429?'AIのコーチは、きょうの回数がおわりました。':'AIのコーチにつながりませんでした。')+'上のボタンからえらんでね。',false),box.firstChild)})}
 sb.onclick=send;inp.addEventListener('keydown',function(ev){if(ev.key==='Enter'&&!ev.isComposing){ev.preventDefault();send()}})}
/* ステップモード */
function home(){var st=load(),done=st.done||[],n=D.scenes.filter(function(s){return done.indexOf(s.id)>=0}).length;
 $('sp-home').hidden=false;$('sp-play').hidden=true;$('sp-end').hidden=true;
 $('sp-prog').innerHTML='<b>'+n+'</b> / '+D.scenes.length+' クリア<span><i style="width:'+(n/D.scenes.length*100)+'%"></i></span>';
 $('sp-levels').innerHTML=D.levels.map(function(L){return '<h3 class="sp-lv">'+L[1]+'</h3><div class="sp-scenes">'+D.scenes.filter(function(s){return s.lv===L[0]}).map(function(s){var ok=done.indexOf(s.id)>=0;return '<button type="button" data-id="'+s.id+'"'+(ok?' class="done"':'')+'><small>'+s.kicker+(ok?'<em>クリア</em>':'')+'</small>'+s.title+'</button>'}).join('')+'</div>'}).join('');
 [].forEach.call($('sp-levels').querySelectorAll('button'),function(b){b.onclick=function(){start(b.getAttribute('data-id'))}});
 var w=$('sp-cert-w');
 if(n===D.scenes.length){w.innerHTML='<p class="sp-cert-h">ぜんぶクリア！修了証をつくろう</p><input type="text" id="sp-nick" maxlength="12" placeholder="ニックネーム（本名でなくてOK）" value="'+esc(st.nick||'')+'"><button type="button" id="sp-cbtn">修了証を見る</button><div id="sp-cert"></div>';
  $('sp-cbtn').onclick=function(){var nk=$('sp-nick').value.trim()||'あなた';if(hasPI(nk)){nk='あなた'}var s2=load();s2.nick=nk;save(s2);var d=new Date();
   $('sp-cert').innerHTML='<div class="sp-certc" id="sp-certc"><p class="sp-ck">修了証</p><h4>SNSデビュー練習</h4><p class="sp-cn">'+esc(nk)+' さん</p><p>あなたは「れんしゅうSNS」の20の場面をすべてクリアしました。<br>教えない・のらない・押さない・話す。この4つを、本物のSNSでも守ってね。</p><p class="sp-cd">'+d.getFullYear()+'年'+(d.getMonth()+1)+'月'+d.getDate()+'日</p><div class="sp-cs"><span>おうちの人のサイン</span><span>本人のサイン</span></div></div><button type="button" id="sp-cprint">印刷する</button>';
   $('sp-cprint').onclick=function(){document.body.classList.add('sp-printing');window.print();setTimeout(function(){document.body.classList.remove('sp-printing')},500)}}}
 else{w.innerHTML='<p class="sp-cert-n">20の場面をぜんぶクリアすると、修了証がもらえるよ。</p>'}}
function start(id){cur=D.scenes.filter(function(s){return s.id===id})[0];si=0;res=[];$('sp-home').hidden=true;$('sp-end').hidden=true;$('sp-play').hidden=false;$('sp-feed').innerHTML='';step();$('sp').scrollIntoView({behavior:'smooth',block:'start'})}
function step(){var t=cur.steps[si];t.msgs.forEach(function(m){$('sp-feed').appendChild(el('sp-m sp-them','<small>'+esc(m[0])+'</small><p>'+esc(m[1])+'</p>'))});
 $('sp-next').hidden=true;replyBox($('sp-ans'),$('sp-feed'),t,function(v){res.push(v);$('sp-next').hidden=false;$('sp-next').textContent=si<cur.steps.length-1?'つぎへ':'ふりかえりを見る'})}
function end(){$('sp-play').hidden=true;var st=load();st.done=st.done||[];if(st.done.indexOf(cur.id)<0)st.done.push(cur.id);save(st);
 var e=$('sp-end'),ok=res.filter(function(v){return v==='safe'}).length;e.hidden=false;
 e.innerHTML='<p class="sp-score">'+esc(cur.title)+'<br><b>'+ok+' / '+res.length+'</b> あんしんな返し方</p><div class="sp-rv">'+cur.steps.map(function(t,i){return '<p><b>'+V[res[i]][0]+'</b>「'+esc(t.choices.filter(function(c){return c[1]==='safe'})[0][0].replace(/^（|）$/g,''))+'」が、あんしんな返し方の1つだよ。</p>'}).join('')+'</div>'
  +'<p class="sp-talk">おうちの人と話してみよう：「こんなことがあったら、だれに話す？」</p><div class="sp-btns"><button type="button" id="sp-again">もう一回</button><button type="button" id="sp-home-b">ほかの場面</button></div>';
 $('sp-again').onclick=function(){start(cur.id)};$('sp-home-b').onclick=home;e.scrollIntoView({behavior:'smooth',block:'start'})}
$('sp-next').onclick=function(){if(si<cur.steps.length-1){si++;step()}else end()};
/* フリーモード */
var posts=0,MAXP=5,evAt=[2,4],used=[],freeAi=true,safeN=0,evN=0;
function left(){$('sp-left').textContent=posts<MAXP?'あと'+(MAXP-posts)+'回投稿できるよ':''}
function mates(){return D.mates.slice().sort(function(){return Math.random()-.5})}
function addPost(txt,pic){var p=el('sp-post','<div class="sp-ph"><b>あなた</b><span>いま</span></div>'+(txt?'<p>'+esc(txt)+'</p>':'')+(pic?'<div class="sp-pic">［'+esc(PICS[pic][0])+'］</div>':'')+'<div class="sp-react"><span class="sp-like">いいね 0</span></div><div class="sp-cm"></div>');$('sp-tl').insertBefore(p,$('sp-tl').firstChild);return p}
function comments(p,list){var m=mates(),cm=p.querySelector('.sp-cm'),lk=p.querySelector('.sp-like'),n=0,target=3+Math.floor(Math.random()*10);
 var iv=setInterval(function(){n++;lk.textContent='いいね '+Math.min(n*2,target);if(n*2>=target)clearInterval(iv)},250);
 list.slice(0,2).forEach(function(c,i){setTimeout(function(){cm.appendChild(el('sp-cmt','<b>'+esc(c.name||m[i])+'</b>'+esc(c.text)))},700+i*900)})}
function fallbackC(){var m=mates();return [0,1].map(function(i){return {name:m[i],text:D.fallback[Math.floor(Math.random()*D.fallback.length)]}})}
function event(){var pool=D.events.filter(function(x){return used.indexOf(x)<0}),id=pool[Math.floor(Math.random()*pool.length)];used.push(id);var t=BY[id];evN++;
 var box=el('sp-ev','<p class="sp-evh">'+(id.indexOf('mean')===0?'あなたの投稿にコメントがつきました':id.indexOf('group')===0||id.indexOf('chain')===0?'グループにメッセージがきました':'DMがとどきました')+'</p>');
 var feed=el('sp-feed','');t.msgs.forEach(function(m){feed.appendChild(el('sp-m sp-them','<small>'+esc(m[0])+'</small><p>'+esc(m[1])+'</p>'))});
 var ans=el('sp-ans','');box.appendChild(feed);box.appendChild(ans);$('sp-tl').insertBefore(box,$('sp-tl').firstChild);
 $('sp-pbtn').disabled=true;replyBox(ans,feed,t,function(v){if(v==='safe')safeN++;if(posts>=MAXP)finish();else $('sp-pbtn').disabled=false});box.scrollIntoView({behavior:'smooth',block:'start'})}
function finish(){var s=el('sp-sum','<p><b>おつかれさま！</b>きょうのフリーモードはここまで。</p><p>事件 '+evN+' こ中、あんしんな返し方 '+safeN+' こ。</p><p class="sp-talk">長く見つづけないのも、SNSの大事なルールだよ。おうちの人に、どんな事件があったか話してみよう。</p><button type="button" id="sp-fre">もう一回</button>');$('sp-tl').insertBefore(s,$('sp-tl').firstChild);
 $('sp-fre').onclick=function(){posts=0;used=[];safeN=0;evN=0;$('sp-tl').innerHTML='';$('sp-pbtn').disabled=false;left()};$('sp-pbtn').disabled=true;left();s.scrollIntoView({behavior:'smooth',block:'start'})}
$('sp-pbtn').onclick=function(){if(busy||posts>=MAXP)return;var txt=$('sp-post').value.trim(),pic=$('sp-pic').value;if(!txt&&!pic)return;
 if(hasPI(txt)){$('sp-tl').insertBefore(coachEl('risky','投稿する前にストップ！名前・学校・住所・電話番号みたいな「個人情報」が入っているかも。消してから投稿しよう。',false),$('sp-tl').firstChild);return}
 if(pic&&PICS[pic][1]!=='safe'){$('sp-tl').insertBefore(coachEl(PICS[pic][1],PICS[pic][2],false),$('sp-tl').firstChild);$('sp-pic').value='';return}
 busy=true;$('sp-pbtn').disabled=true;posts++;left();var p=addPost(txt,pic);$('sp-post').value='';$('sp-pic').value='';
 var go=function(r){busy=false;if(r&&r.verdict&&r.verdict!=='safe'&&r.coach){p.appendChild(coachEl(r.verdict,r.coach,true))}
  comments(p,r&&r.comments&&r.comments.length?r.comments:fallbackC());
  setTimeout(function(){if(evAt.indexOf(posts)>=0)event();else if(posts>=MAXP)finish();else $('sp-pbtn').disabled=false},2400)};
 if(!freeAi||!txt){go(null);return}
 call('free',{post:txt}).then(go).catch(function(){freeAi=false;go(null)})};
/* タブ */
function tab(f){$('sp-step').hidden=f;$('sp-free').hidden=!f;$('sp-t1').setAttribute('aria-selected',!f);$('sp-t2').setAttribute('aria-selected',f)}
$('sp-t1').onclick=function(){tab(false);home()};$('sp-t2').onclick=function(){tab(true)};
home();left();
})();
</script>"""

BODY = (BODY.replace("%LD%", LD).replace("%FAQ%", faq_html).replace("%ROWS%", scene_rows).replace("%API%", API)
        .replace("%DATA%", json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")))

CSS = (".sp-app{background:#fff;border:2px solid var(--text);border-radius:24px;margin:20px 0 32px;overflow:hidden;box-shadow:5px 5px 0 var(--text)}"
       ".sp-top{display:flex;justify-content:space-between;align-items:baseline;gap:8px;padding:14px 18px;background:#E3F1EA;border-bottom:1.5px solid var(--text)}.sp-top b{font-size:17px;font-weight:900;white-space:nowrap}.sp-top span{font-size:12px;color:var(--muted)}"
       ".sp-tabs{display:grid;grid-template-columns:1fr 1fr;border-bottom:1.5px solid var(--text)}.sp-tabs button{font:inherit;font-size:15px;font-weight:800;padding:12px;border:0;background:var(--bg);color:var(--muted);cursor:pointer;min-height:48px}.sp-tabs button[aria-selected=true]{background:#fff;color:var(--text);box-shadow:inset 0 -4px 0 var(--accent)}"
       "#sp-home,#sp-play,#sp-end,#sp-free{padding:18px}"
       ".sp-hi{font-size:16px;line-height:1.8;font-weight:700}"
       ".sp-prog{display:flex;align-items:center;gap:10px;font-size:14px;margin:10px 0}.sp-prog b{font-size:22px;color:var(--accent)}.sp-prog span{flex:1;height:10px;background:var(--bg);border:1px solid var(--border);border-radius:999px;overflow:hidden}.sp-prog i{display:block;height:100%;background:#2E7D60}"
       ".sp-lv{font-size:15px;font-weight:900;margin:18px 0 8px}"
       ".sp-scenes{display:grid;grid-template-columns:1fr 1fr;gap:10px}"
       ".sp-scenes button{font:inherit;text-align:left;font-size:15px;font-weight:800;line-height:1.5;padding:14px;border:1.5px solid var(--text);border-radius:14px;background:var(--bg);color:var(--text);cursor:pointer;min-height:84px}"
       ".sp-scenes button.done{background:#E3F1EA}.sp-scenes small{display:flex;justify-content:space-between;font-size:12px;font-weight:800;color:var(--accent);margin-bottom:4px}.sp-scenes em{font-style:normal;color:#2E7D60}"
       ".sp-cert-w{margin:20px 0 6px}.sp-cert-n{font-size:13px;color:var(--muted)}.sp-cert-h{font-size:16px;font-weight:900;color:#2E7D60}"
       ".sp-cert-w input,.sp-comp textarea,.sp-comp select{font:inherit;font-size:16px;padding:12px;border:1px solid var(--border);border-radius:12px;background:var(--bg);color:var(--text);width:100%;margin:8px 0;min-height:48px}"
       ".sp-certc{border:4px double #2E7D60;border-radius:16px;padding:24px 18px;text-align:center;margin:12px 0;background:#fff}.sp-ck{font-size:13px;font-weight:900;letter-spacing:.3em;color:#2E7D60}.sp-certc h4{font-size:24px;font-weight:900;margin:6px 0}.sp-cn{font-size:20px;font-weight:800;margin:10px 0}.sp-certc p{font-size:14px;line-height:1.8}.sp-cd{margin-top:10px;color:var(--muted)}.sp-cs{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:18px}.sp-cs span{font-size:12px;color:var(--muted);border-bottom:1px solid var(--muted);padding-top:24px}"
       ".sp-rule{font-size:13px;color:var(--muted);line-height:1.7;margin-top:12px}"
       ".sp-feed{display:flex;flex-direction:column;gap:10px}"
       ".sp-m{max-width:84%;border-radius:16px;padding:10px 14px;font-size:16px;line-height:1.7}.sp-m small{display:block;font-size:12px;font-weight:700;color:var(--muted)}"
       ".sp-them{align-self:flex-start;background:var(--bg);border:1px solid var(--border);border-top-left-radius:4px}"
       ".sp-me{align-self:flex-end;background:#2E7D60;color:#fff;border-top-right-radius:4px}"
       ".sp-c{border-radius:14px;padding:12px 14px;border:2px solid;margin:8px 0}.sp-c b{font-size:14px;font-weight:900}.sp-c p{font-size:15px;line-height:1.75;margin-top:2px}.sp-c small{font-size:11px;color:var(--muted)}"
       ".sp-ok{border-color:#2E7D60;background:#E3F1EA}.sp-ok b{color:#2E7D60}.sp-mid{border-color:#B7791F;background:#FFF3C4}.sp-mid b{color:#8A5A0B}.sp-ng{border-color:#BF4A33;background:#FBE3DC}.sp-ng b{color:#A63D28}"
       ".sp-ans{margin-top:12px}.sp-ans:not(:empty){padding-top:14px;border-top:1px dashed var(--border)}.sp-q{font-size:15px;font-weight:800}"
       ".sp-ch{display:grid;gap:8px;margin:10px 0}.sp-ch button{font:inherit;font-size:15px;text-align:left;padding:12px 14px;border:1.5px solid var(--text);border-radius:12px;background:#fff;color:var(--text);cursor:pointer;min-height:48px}"
       ".sp-free{display:flex;gap:8px}.sp-free input{flex:1;min-width:0;font:inherit;font-size:16px;padding:12px;border:1px solid var(--border);border-radius:12px;background:var(--bg);color:var(--text);min-height:48px}"
       ".sp-free button,.sp-next,.sp-btns button,#sp-pbtn,#sp-cbtn,#sp-cprint,#sp-fre{font:inherit;font-size:16px;font-weight:800;padding:12px 16px;border:1.5px solid var(--text);border-radius:12px;background:#E8B23A;color:var(--text);cursor:pointer;min-height:48px}"
       "#sp-pbtn,#sp-cbtn,#sp-cprint{width:100%}#sp-pbtn:disabled{opacity:.45;cursor:default}"
       ".sp-next{width:100%;margin-top:14px}"
       ".sp-score{font-size:16px;font-weight:800;text-align:center;line-height:1.6}.sp-score b{font-size:34px;color:var(--accent)}"
       ".sp-rv p{font-size:15px;line-height:1.7;background:var(--bg);border-radius:12px;padding:10px 12px;margin:8px 0}.sp-rv b{display:inline-block;font-size:12px;border:1px solid var(--text);border-radius:999px;padding:0 8px;margin-right:6px}"
       ".sp-talk{font-size:15px;font-weight:700;margin:14px 0;color:var(--accent2)}.sp-btns{display:grid;grid-template-columns:1fr 1fr;gap:10px}.sp-btns button:last-child{background:#fff}"
       ".sp-comp{background:var(--bg);border:1px solid var(--border);border-radius:14px;padding:14px;margin:12px 0}.sp-comp label{font-size:13px;font-weight:700}.sp-left{font-size:13px;color:var(--muted);margin-top:6px;text-align:center}"
       ".sp-tl{display:flex;flex-direction:column;gap:12px}"
       ".sp-post{border:1px solid var(--border);border-radius:14px;padding:14px}.sp-ph{display:flex;justify-content:space-between;font-size:13px}.sp-ph span{color:var(--muted)}.sp-post>p{font-size:16px;line-height:1.7;margin:6px 0}"
       ".sp-pic{font-size:14px;color:var(--muted);background:var(--bg);border-radius:10px;padding:18px;text-align:center}.sp-react{font-size:13px;font-weight:700;color:var(--accent);margin-top:8px}"
       ".sp-cmt{font-size:14px;line-height:1.6;background:var(--bg);border-radius:10px;padding:8px 12px;margin-top:6px}.sp-cmt b{margin-right:8px;font-size:13px}"
       ".sp-ev{border:2px solid var(--accent);border-radius:16px;padding:14px}.sp-evh{font-size:14px;font-weight:900;color:var(--accent);margin-bottom:8px}"
       ".sp-sum{border:2px solid #2E7D60;border-radius:16px;padding:16px;background:#E3F1EA}.sp-sum p{font-size:15px;line-height:1.8}"
       ".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".sp-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.sp-t th,.sp-t td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top;line-height:1.7}.sp-t th{background:var(--card)}"
       ".xbody ul li a,.xbody p a,.note a{color:var(--link)}"
       ".xbody>details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}.xbody>details summary{cursor:pointer;font-weight:700;font-size:15px}.xbody>details p{font-size:15px;margin-top:8px}"
       ".note{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}"
       "@media print{body.sp-printing>*:not(main),body.sp-printing main>*:not(.xbody),body.sp-printing .xbody>*:not(#sp),body.sp-printing #sp>*:not(#sp-step),body.sp-printing #sp-step>*:not(#sp-home),body.sp-printing #sp-home>*:not(#sp-cert-w),body.sp-printing #sp-cert-w>*:not(#sp-cert),body.sp-printing #sp-cert>*:not(#sp-certc){display:none!important}body.sp-printing .sp-app{border:0;box-shadow:none}body.sp-printing{background:#fff!important;background-image:none!important}}")

PAGE = {"path": "sns-practice", "title": "AIで練習するSNS（子ども向け）",
        "seo_title": "子ども向けSNSの練習｜知らない人のDM・悪口・写真投稿など20場面をAIコーチつきで体験",
        "date": "2026-10-07",
        "desc": "本物のSNSを使う前に、知らない人からのDM、写真の投稿、グループの悪口、詐欺リンク、闇バイトのさそいなど20の場面を練習。自由に投稿できるフリーモードと修了証つき。無料・広告なし・登録不要。",
        "body": BODY, "css": CSS}

if __name__ == "__main__" and "--app" in sys.argv:
    # アプリ版(れんしゅうSNS)用のデータを書き出す: python3 media/kosodate_sns_tool.py --app <アプリのassets/data>
    from kosodate_sns_scenes import FREE_NG, FREE_TOPICS
    out = Path(sys.argv[sys.argv.index("--app") + 1]) / "scenes_ja.json"
    out.write_text(json.dumps(dict(DATA, topics=FREE_TOPICS, ng=FREE_NG), ensure_ascii=False, indent=1) + "\n")
    print("wrote", out)

if __name__ == "__main__" and "--worker" in sys.argv:
    steps = {t["id"]: {"scene": s["title"], "msgs": [m[1] for m in t["msgs"]], "point": t["point"]} for s in SCENES for t in s["steps"]}
    out = Path("/Users/hidenori/Developer/kosodate-ai-worker/src/steps.js")
    out.write_text("// media/kosodate_sns_tool.py --worker で生成。手で編集しない\nexport const STEPS = "
                   + json.dumps(steps, ensure_ascii=False, indent=1) + ";\n"
                   + "export const MATES = " + json.dumps(CLASSMATES, ensure_ascii=False) + ";\n"
                   + "export const FALLBACK = " + json.dumps(FALLBACK_COMMENTS, ensure_ascii=False) + ";\n")
    print("wrote", out, len(steps), "steps")
