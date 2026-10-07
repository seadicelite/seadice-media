"""子育てデータ「AIで練習するSNS」(/sns-practice/)。kosodate_tools.py が読み込む。

相手役の投稿・DMは、ここに書いた文章だけを使う(AIに危ない大人やいじめ役を自由に演じさせない)。
AIの役目は、子どもが自由に書いた返事を「あんしん/ちょっと注意/きけん」に判定して短くコーチすることだけ。
AIが使えないとき(上限・通信エラー)は、選択肢を選べば最後まで練習できる。
返事は保存しない。個人情報らしい入力はブラウザ側で送信前に止める。

Worker の判定観点(steps.js)もここから書き出す:
  python3 media/kosodate_sns_tool.py --worker
"""
import json
import sys
from pathlib import Path

URL = "https://kosodate.seadice.win/sns-practice/"
WORKER = "https://kosodate-ai.seadice-lite.workers.dev/coach"

# v: safe(あんしん) / careful(ちょっと注意) / risky(きけん)
# point: Worker に渡す「この場面で安全な返し方の観点」(AIの判定基準)
SCENES = [
    {"id": "dm", "title": "知らない人からDMがきた", "kicker": "DM", "steps": [
        {"id": "dm1", "msgs": [["ゲーム好きのユウ", "はじめまして！きのうの投稿見たよ。ゲームうまいね。何年生？"]],
         "point": "知らない相手。学年・年齢・学校・住んでいる場所など自分のことは教えない。返事をしない、ブロックする、おうちの人に見せるのが安全。あいさつだけ返すのはちょっと注意。",
         "choices": [["4年生だよ！", "risky", "学年は、あなたをさがす手がかりになるよ。知らない人には教えないでね。"],
                     ["（返事しないで、おうちの人に見せる）", "safe", "いいね！知らない人からのDMは、まず大人に見せるのがいちばんあんしん。"],
                     ["ありがとう！", "careful", "やさしいね。でも知らない人とのやりとりは、つづくほど個人情報を聞かれやすくなるよ。"]]},
        {"id": "dm2", "msgs": [["ゲーム好きのユウ", "ふたりだけのひみつね。顔の写真を送ってくれたら、レアアイテムあげるよ"]],
         "point": "「ひみつ」「写真」「プレゼント」は危ない合図。写真は送らない。ひみつにしないで大人に話す。ブロック・通報する。",
         "choices": [["写真を送る", "risky", "「ひみつ」「写真」「プレゼント」は危ない合図。写真は一度送ると消せないよ。"],
                     ["いらない。ブロックする", "safe", "ばっちり！ことわってブロックして、おうちの人にも話そう。"],
                     ["どんなアイテム？", "careful", "気になるよね。でもプレゼントで気を引くのはよくある手口。話をつづけないのが安全だよ。"]]},
    ]},
    {"id": "photo", "title": "写真を投稿する前に", "kicker": "投稿", "steps": [
        {"id": "photo1", "msgs": [["あなたの下書き", "（家の前で、名札のついた服で撮った写真）「〇〇小のみんな、見てね！」"]],
         "point": "家の外観・名札・制服・学校名・場所がわかるものは、住んでいる所や学校を特定される。写真を変える、学校名を消す、投稿前に大人に見せるのが安全。",
         "choices": [["そのまま投稿する", "risky", "家・名札・学校名がそろうと、住んでいる所や学校がわかってしまうよ。"],
                     ["学校名だけ消して投稿する", "careful", "学校名を消したのはいいね。でも家の前や名札も手がかりになるよ。"],
                     ["写真を変えて、おうちの人に見せてから投稿する", "safe", "完ぺき！投稿する前に大人に見てもらうと、見落としに気づけるよ。"]]},
        {"id": "photo2", "msgs": [["あなたの下書き", "友だちのへん顔の写真。おもしろいから、のせちゃおうかな"]],
         "point": "人の写真は、のせる前に本人に「のせていい？」と聞く。本人がいやなら、のせない。本人ならどう感じるかを考える。",
         "choices": [["おもしろいから、のせる", "risky", "自分がのせられたらどう思うかな？人の写真は本人にきいてからにしよう。"],
                     ["友だちに「のせていい？」ときく", "safe", "すてき！本人がいいと言ったものだけのせようね。"],
                     ["顔を少しかくして、のせる", "careful", "かくしたのはいいね。でも本人がいやがるかもしれないから、まずきいてみよう。"]]},
    ]},
    {"id": "group", "title": "グループで悪口が始まった", "kicker": "グループ", "steps": [
        {"id": "group1", "msgs": [["クラスのグループ", "ねえ、Aちゃんってちょっとうざくない？"], ["クラスのグループ", "わかるw"]],
         "point": "悪口にのらない。話題を変える、だまってのらない、「やめようよ」と言う、つらければおうちの人や先生に相談する。悪口に同意するのはきけん。",
         "choices": [["「わかる〜」とのる", "risky", "のると、いじめに入ってしまうことになるよ。のらないのが大事。"],
                     ["「やめようよ」と書く", "safe", "勇気ある返事！言いにくいときは、話題を変えるだけでもいいよ。"],
                     ["何も書かない", "careful", "のらなかったのはいいね。気になるときは、おうちの人や先生に話してみよう。"]]},
        {"id": "group2", "msgs": [["クラスのグループ", "Aちゃんの変な投稿、スクショしてみんなに回そうよ"]],
         "point": "人の投稿をさらす・広めるのはいじめになる。広めない。大人に相談する。",
         "choices": [["スクショを回す", "risky", "広めると、もう取り消せないよ。Aちゃんのつらさも大きくなるよ。"],
                     ["回さない。先生かおうちの人に話す", "safe", "そのとおり！大人に話すのは「つげ口」じゃなくて、友だちを守ることだよ。"],
                     ["見るだけにする", "careful", "広めなかったのはいいね。止めたいときは、大人に話してみよう。"]]},
    ]},
    {"id": "mean", "title": "自分の投稿にいやなコメント", "kicker": "コメント", "steps": [
        {"id": "mean1", "msgs": [["知らないアカウント", "へたくそ。もう投稿すんな"]],
         "point": "言い返さない（言い合いが大きくなる）。返事をしない、ブロック・通報する、スクショを残しておうちの人に話す。自分を責めなくていい。",
         "choices": [["「そっちこそへたくそ！」と言い返す", "risky", "くやしいよね。でも言い返すと、言い合いが大きくなりやすいよ。"],
                     ["返事しないでブロックして、おうちの人に話す", "safe", "かんぺき！あなたは悪くないよ。つらい気持ちも話していいからね。"],
                     ["投稿を消す", "careful", "消してもいいよ。でも、いやな気持ちは一人でかかえないで、大人に話そう。"]]},
    ]},
    {"id": "likes", "title": "「いいね」が少ない", "kicker": "いいね", "steps": [
        {"id": "likes1", "msgs": [["お知らせ", "友だちの投稿に「いいね」50こ。あなたの投稿は2こ。"]],
         "point": "いいねの数は自分の価値ではない。比べすぎない、SNSの時間を決める、気持ちを家族や友だちに話す。いいね集めのために危ない投稿や個人情報を出すのはきけん。",
         "choices": [["もっと目立つ写真をのせて、いいねを集める", "risky", "いいねのために無理をすると、出さなくていいものまで出してしまいやすいよ。"],
                     ["数は気にしないで、アプリをとじて遊びに行く", "safe", "いいね！いいねの数は、あなたのよさとは関係ないよ。"],
                     ["もやもやしたまま、ずっと見つづける", "careful", "比べるとつらくなるよね。時間を決めて、もやもやは家族に話してみよう。"]]},
    ]},
    {"id": "link", "title": "プレゼントのリンクがきた", "kicker": "詐欺", "steps": [
        {"id": "link1", "msgs": [["プレゼント事務局", "おめでとう！あなたが当選しました。このリンクからIDとパスワードを入れてね"]],
         "point": "当選・プレゼントで、リンクを押させたりIDやパスワードを入れさせたりするのは詐欺の手口。押さない、入力しない、大人に見せる。",
         "choices": [["リンクを押してパスワードを入れる", "risky", "パスワードを入れると、アカウントをとられてしまうことがあるよ。"],
                     ["押さないで、おうちの人に見せる", "safe", "正解！「当選」「パスワードを入れて」は、詐欺のよくある手口だよ。"],
                     ["リンクを押して、中だけ見る", "careful", "押すだけでもあぶないページにつながることがあるよ。押さないのが安全。"]]},
    ]},
]

FAQ = [
    ("子どもにSNSを使わせる前に、何を練習させればいいですか？",
     "知らない人に学年・学校・写真を教えない、悪口にのらない・広めない、いやなことがあったら大人に話す、リンクを押さない、の4つが基本です。このページでは、その場面をAIのコーチつきで体験できます。"),
    ("練習の相手は本物の人ですか？",
     "いいえ。相手役の投稿やメッセージは、SEADICEがあらかじめ用意した練習用の文章です。AI（Anthropic社のClaude）は、お子さんが書いた返事が安全かどうかを判定して、短くアドバイスするだけです。"),
    ("子どもが書いた返事は保存されますか？",
     "保存されません。返事は判定のためだけにAIへ送られ、SEADICEは残しません。名前・電話番号・学校名のような入力は、送る前に画面上で止めます。AIのアドバイスは1日30回までで、それを超えても選択肢を選べば練習を続けられます。"),
    ("何歳から使えますか？",
     "ひらがなが読める小学校低学年から、おうちの人と一緒に使えます。SNSを使い始める前の小学校高学年〜中学生には、ひとりでの練習にも向いています。"),
]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "AIで練習するSNS（子ども向け）", "url": URL, "applicationCategory": "EducationalApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "知らない人からのDM、写真の投稿、グループの悪口、詐欺リンクなど、SNSで起きやすい6つの場面を、本物のSNSを使う前に安全に練習できる子ども向けツール。返事にAIがアドバイス。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}
LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
faq_html = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ))
scene_rows = "".join(f'<tr><td>{s["title"]}</td><td>{s["steps"][0]["point"].split("。")[0]}。</td></tr>' for s in SCENES)
page_scenes = [{"id": s["id"], "title": s["title"], "kicker": s["kicker"],
                "steps": [{"id": t["id"], "msgs": t["msgs"], "choices": t["choices"]} for t in s["steps"]]} for s in SCENES]

BODY = """<script type="application/ld+json">%LD%</script>
<p>本物のSNSを使う前に、知らない人からのDMや悪口、写真の投稿などを、安全に練習できる子ども向けのページです。相手役は練習用の文章で、お子さんの返事にはAIがアドバイスします。無料・広告なし・登録不要です。</p>
<div class="sp-app" id="sp">
<div class="sp-top"><b>れんしゅうSNS</b><span>あいては練習用のキャラクターだよ</span></div>
<div id="sp-home">
<p class="sp-hi">SNSで「こんなとき、どうする？」を練習しよう。やってみたい場面をえらんでね。</p>
<div class="sp-scenes" id="sp-scenes"></div>
<p class="sp-rule">練習のおやくそく：ほんとうの名前・学校・住所・電話番号は書かないでね。</p>
</div>
<div id="sp-play" hidden>
<div class="sp-feed" id="sp-feed" aria-live="polite"></div>
<div class="sp-ans" id="sp-ans">
<p class="sp-q">あなたなら、どう返す？</p>
<div class="sp-ch" id="sp-ch"></div>
<div class="sp-free"><input type="text" id="sp-in" maxlength="80" placeholder="自分のことばで書いてもいいよ" enterkeyhint="send"><button type="button" id="sp-send">送る</button></div>
</div>
<button type="button" class="sp-next" id="sp-next" hidden>つぎへ</button>
</div>
<div id="sp-end" hidden></div>
</div>
<p class="answer"><strong>SNSを始める前に練習したいのは「教えない・のらない・押さない・話す」の4つです。</strong>知らない人に学年や写真を教えない、悪口にのらない、リンクを押さない、困ったら大人に話す。この4つを場面ごとに体験できます。</p>
<h2>練習できる6つの場面</h2>
<table class="sp-t"><thead><tr><th>場面</th><th>安全な返し方の目安</th></tr></thead><tbody>%ROWS%</tbody></table>
<h2>おうちの人へ：練習のあとに話したいこと</h2>
<ul>
<li><b>「何かあったら話してね。話してくれたら怒らないよ」と先に伝える。</b>サイバーいじめは子どもから話しにくく、親からは見えにくい問題です。日頃からネットの話を否定せずに聞く関わりが、研究の傾向と合っています（<a href="/cyberbullying-children-parent-awareness/">サイバーいじめの記事</a>）。</li>
<li><b>知らない人とのやりとりは、禁止より「一緒に見る」。</b>一律に禁止するより、一緒にゲームをする・話を聞くといった関わりの方が、見知らぬ人とのリスクを減らしやすいとわかっています（<a href="/online-gaming-strangers-chat-risk/">オンラインゲームの記事</a>）。</li>
<li><b>写真は「本人ならどう感じるか」。</b>投稿前に本人の気持ちを考え、特定されやすい情報を避け、公開範囲を絞るのが基本の対策です（<a href="/sharenting-sns-photo-risk/">写真の投稿の記事</a>）。</li>
</ul>
<p>家族のSNS・スマホのルールは<a href="/rules/">わが家のルールづくり</a>で作って印刷できます。</p>
<div class="note">相手役の投稿・メッセージは、SEADICEが用意した練習用の文章です。AI（Anthropic社のClaude）が行うのは、お子さんの返事の判定と短いアドバイスだけで、返事は保存しません。</div>
<h2>よくある質問</h2>
%FAQ%
<script>
(function(){
var S=%SCENES%,W='%WORKER%',$=function(i){return document.getElementById(i)},cur,si,res,aiOff=false,busy=false;
var V={safe:['あんしん','ok'],careful:['ちょっと注意','mid'],risky:['きけん','ng']};
var PI=[/\\d{2,4}-?\\d{2,4}-?\\d{3,4}/,/\\d{7,}/,/@/,/(小学校|中学校|小学|中学|学園)/,/(丁目|番地|町|市|区|村)\\S{0,3}\\d/,/(住所|でんわ|電話)/];
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function add(cls,who,txt){var d=document.createElement('div');d.className='sp-m '+cls;d.innerHTML=(who?'<small>'+esc(who)+'</small>':'')+'<p>'+esc(txt)+'</p>';$('sp-feed').appendChild(d);d.scrollIntoView({behavior:'smooth',block:'nearest'})}
function coach(v,txt,ai){var d=document.createElement('div');d.className='sp-c sp-'+V[v][1];d.innerHTML='<b>'+V[v][0]+'</b><p>'+esc(txt)+'</p>'+(ai?'<small>AIコーチ</small>':'');$('sp-feed').appendChild(d);d.scrollIntoView({behavior:'smooth',block:'nearest'})}
function home(){$('sp-home').hidden=false;$('sp-play').hidden=true;$('sp-end').hidden=true;
 $('sp-scenes').innerHTML=S.map(function(s,i){return '<button type="button" data-i="'+i+'"><small>'+s.kicker+'</small>'+s.title+'</button>'}).join('');
 [].forEach.call($('sp-scenes').querySelectorAll('button'),function(b){b.onclick=function(){start(+b.getAttribute('data-i'))}})}
function start(i){cur=S[i];si=0;res=[];$('sp-home').hidden=true;$('sp-end').hidden=true;$('sp-play').hidden=false;$('sp-feed').innerHTML='';step()}
function step(){var t=cur.steps[si];t.msgs.forEach(function(m){add('sp-them',m[0],m[1])});
 $('sp-ans').hidden=false;$('sp-next').hidden=true;$('sp-in').value='';
 $('sp-ch').innerHTML=t.choices.map(function(c,k){return '<button type="button" data-k="'+k+'">'+esc(c[0])+'</button>'}).join('');
 [].forEach.call($('sp-ch').querySelectorAll('button'),function(b){b.onclick=function(){var c=t.choices[+b.getAttribute('data-k')];answer(c[0]);done(c[1],c[2],false)}})}
function answer(txt){add('sp-me','',txt);$('sp-ans').hidden=true}
function done(v,fb,ai){res.push(v);coach(v,fb,ai);$('sp-next').hidden=false;$('sp-next').textContent=si<cur.steps.length-1?'つぎへ':'ふりかえりを見る'}
function send(){if(busy)return;var txt=$('sp-in').value.trim(),t=cur.steps[si];if(!txt)return;
 for(var k=0;k<PI.length;k++){if(PI[k].test(txt)){coach('risky','ストップ！それは名前・学校・住所・電話番号みたいな「個人情報」かも。練習でも書かないでね。',false);$('sp-in').value='';return}}
 if(aiOff){coach('careful','AIのコーチはきょうはお休み。上のボタンからえらんでね。',false);return}
 busy=true;$('sp-send').disabled=true;answer(txt);var w=document.createElement('p');w.className='sp-wait';w.textContent='AIコーチが考えているよ…';$('sp-feed').appendChild(w);
 fetch(W,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({step:t.id,reply:txt})})
 .then(function(r){return r.json().then(function(j){return {s:r.status,j:j}})})
 .then(function(x){w.remove();if(x.s===200&&x.j.result&&V[x.j.result.verdict]){done(x.j.result.verdict,x.j.result.feedback,true)}else{throw x}})
 .catch(function(x){w.remove();aiOff=true;$('sp-ans').hidden=false;$('sp-feed').lastChild&&$('sp-feed').lastChild.classList.contains('sp-me')&&$('sp-feed').lastChild.remove();
  coach('careful',(x&&x.s===429?'AIのコーチは、きょうの回数がおわりました。':'AIのコーチにつながりませんでした。')+'上のボタンからえらんでね。',false)})
 .then(function(){busy=false;$('sp-send').disabled=false})}
function end(){$('sp-play').hidden=true;var e=$('sp-end'),ok=res.filter(function(v){return v==='safe'}).length;e.hidden=false;
 e.innerHTML='<p class="sp-score">'+cur.title+'<br><b>'+ok+' / '+res.length+'</b> あんしんな返し方</p><div class="sp-rv">'+cur.steps.map(function(t,i){return '<p><b>'+V[res[i]][0]+'</b>「'+esc(t.choices.filter(function(c){return c[1]==='safe'})[0][0].replace(/^（|）$/g,''))+'」が、あんしんな返し方の1つだよ。</p>'}).join('')+'</div>'
  +'<p class="sp-talk">おうちの人と話してみよう：「こんなことがあったら、だれに話す？」</p><div class="sp-btns"><button type="button" id="sp-again">もう一回</button><button type="button" id="sp-home-b">ほかの場面</button></div>';
 $('sp-again').onclick=function(){start(S.indexOf(cur))};$('sp-home-b').onclick=home;e.scrollIntoView({behavior:'smooth',block:'start'})}
$('sp-send').onclick=send;$('sp-in').addEventListener('keydown',function(ev){if(ev.key==='Enter'&&!ev.isComposing){ev.preventDefault();send()}});
$('sp-next').onclick=function(){if(si<cur.steps.length-1){si++;step()}else end()};
home();
})();
</script>"""

BODY = (BODY.replace("%LD%", LD).replace("%FAQ%", faq_html).replace("%ROWS%", scene_rows).replace("%WORKER%", WORKER)
        .replace("%SCENES%", json.dumps(page_scenes, ensure_ascii=False).replace("</", "<\\/")))

CSS = (".sp-app{background:#fff;border:2px solid var(--text);border-radius:24px;margin:20px 0 32px;overflow:hidden;box-shadow:5px 5px 0 var(--text)}"
       ".sp-top{display:flex;justify-content:space-between;align-items:baseline;gap:8px;padding:14px 18px;background:#E3F1EA;border-bottom:1.5px solid var(--text)}.sp-top b{font-size:17px;font-weight:900;white-space:nowrap}.sp-top span{font-size:12px;color:var(--muted)}"
       "#sp-home,#sp-play,#sp-end{padding:18px}"
       ".sp-hi{font-size:16px;line-height:1.8;font-weight:700}"
       ".sp-scenes{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:14px 0}"
       ".sp-scenes button{font:inherit;text-align:left;font-size:15px;font-weight:800;line-height:1.5;padding:14px;border:1.5px solid var(--text);border-radius:14px;background:var(--bg);color:var(--text);cursor:pointer;min-height:84px}"
       ".sp-scenes small{display:block;font-size:12px;font-weight:800;color:var(--accent);margin-bottom:4px}"
       ".sp-rule{font-size:13px;color:var(--muted);line-height:1.7}"
       ".sp-feed{display:flex;flex-direction:column;gap:10px;min-height:120px}"
       ".sp-m{max-width:84%;border-radius:16px;padding:10px 14px;font-size:16px;line-height:1.7}.sp-m small{display:block;font-size:12px;font-weight:700;color:var(--muted)}"
       ".sp-them{align-self:flex-start;background:var(--bg);border:1px solid var(--border);border-top-left-radius:4px}"
       ".sp-me{align-self:flex-end;background:#2E7D60;color:#fff;border-top-right-radius:4px}"
       ".sp-c{border-radius:14px;padding:12px 14px;border:2px solid}.sp-c b{font-size:14px;font-weight:900}.sp-c p{font-size:15px;line-height:1.75;margin-top:2px}.sp-c small{font-size:11px;color:var(--muted)}"
       ".sp-ok{border-color:#2E7D60;background:#E3F1EA}.sp-ok b{color:#2E7D60}.sp-mid{border-color:#B7791F;background:#FFF3C4}.sp-mid b{color:#8A5A0B}.sp-ng{border-color:#BF4A33;background:#FBE3DC}.sp-ng b{color:#A63D28}"
       ".sp-wait{font-size:14px;color:var(--muted)}"
       ".sp-ans{margin-top:16px;padding-top:14px;border-top:1px dashed var(--border)}.sp-q{font-size:15px;font-weight:800}"
       ".sp-ch{display:grid;gap:8px;margin:10px 0}.sp-ch button{font:inherit;font-size:15px;text-align:left;padding:12px 14px;border:1.5px solid var(--text);border-radius:12px;background:#fff;color:var(--text);cursor:pointer;min-height:48px}"
       ".sp-free{display:flex;gap:8px}.sp-free input{flex:1;min-width:0;font:inherit;font-size:16px;padding:12px;border:1px solid var(--border);border-radius:12px;background:var(--bg);color:var(--text);min-height:48px}"
       ".sp-free button,.sp-next,.sp-btns button{font:inherit;font-size:16px;font-weight:800;padding:12px 16px;border:1.5px solid var(--text);border-radius:12px;background:#E8B23A;color:var(--text);cursor:pointer;min-height:48px}"
       ".sp-next{width:100%;margin-top:14px}"
       ".sp-score{font-size:16px;font-weight:800;text-align:center;line-height:1.6}.sp-score b{font-size:34px;color:var(--accent)}"
       ".sp-rv p{font-size:15px;line-height:1.7;background:var(--bg);border-radius:12px;padding:10px 12px;margin:8px 0}.sp-rv b{display:inline-block;font-size:12px;border:1px solid var(--text);border-radius:999px;padding:0 8px;margin-right:6px}"
       ".sp-talk{font-size:15px;font-weight:700;margin:14px 0;color:var(--accent2)}.sp-btns{display:grid;grid-template-columns:1fr 1fr;gap:10px}.sp-btns button:last-child{background:#fff}"
       ".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".sp-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.sp-t th,.sp-t td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top;line-height:1.7}.sp-t th{background:var(--card)}"
       ".xbody ul li a,.xbody p a,.note a{color:var(--link)}"
       ".xbody>details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}.xbody>details summary{cursor:pointer;font-weight:700;font-size:15px}.xbody>details p{font-size:15px;margin-top:8px}"
       ".note{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}")

PAGE = {"path": "sns-practice", "title": "AIで練習するSNS（子ども向け）",
        "seo_title": "子ども向けSNSの練習｜知らない人のDM・悪口・写真投稿をAIコーチつきで体験",
        "date": "2026-10-07",
        "desc": "本物のSNSを使う前に、知らない人からのDM、写真の投稿、グループの悪口、詐欺リンクなど6つの場面を安全に練習。返事にAIがアドバイス。無料・広告なし・登録不要。",
        "body": BODY, "css": CSS}

if __name__ == "__main__" and "--worker" in sys.argv:
    steps = {t["id"]: {"scene": s["title"], "msgs": [m[1] for m in t["msgs"]], "point": t["point"]} for s in SCENES for t in s["steps"]}
    out = Path("/Users/hidenori/Developer/kosodate-ai-worker/src/steps.js")
    out.write_text("// media/kosodate_sns_tool.py --worker で生成。手で編集しない\nexport const STEPS = "
                   + json.dumps(steps, ensure_ascii=False, indent=1) + ";\n")
    print("wrote", out, len(steps), "steps")
