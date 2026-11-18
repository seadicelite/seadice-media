"""AI時代の子育て「れんしゅうAI」(/ai-practice/)。kosodate_tools.py が読み込む。

れんしゅうシリーズの2本目(1本目は /sns-practice/)。子どもがスマホ・タブレットでAIを使い始めるころに、
12の場面を選んで練習する。ページはAIを呼ばず、入力も送らない(選んだ返し方とクリアした場面は localStorage だけ)。
見た目は sns-practice の CSS(sp-*)をそのまま使う。場面は kosodate_ai_scenes.py。
"""
import json

from kosodate_ai_scenes import LEVELS, SCENES
from kosodate_sns_tool import CSS as SNS_CSS

URL = "https://kosodate.seadice.win/ai-practice/"
N = len(SCENES)

FAQ = [
    ("子どもがAIを使い始める前に、何を練習させればいいですか？",
     "答えをうのみにせず「たしかめる」、名前や学校を「入れない」、宿題や作文を「まかせきりにしない」、こわい答えや悩みは大人に「話す」の4つが基本です。このページでは、宿題の丸写し・AIのまちがい・家族の声をまねる電話・にせ動画など12の場面で練習できます。"),
    ("練習の相手は本物のAIですか？",
     "いいえ。「れんしゅうAI」の言葉は、SEADICEがあらかじめ用意した練習用の文章です。このページはAIを呼び出さず、お子さんの選んだ返し方もどこにも送りません。クリアした場面と修了証の名前は、この端末の中だけに保存されます。"),
    ("何歳から使えますか？",
     "ひらがなが読める小学校中学年から、おうちの人と一緒に使えます。ユネスコの目安は13歳からで、それより前は親と一緒に使うのが研究から見た安心な形です。レベル3は中学生になる前の練習向けです。"),
    ("SNSの練習もできますか？",
     "できます。同じれんしゅうシリーズの「れんしゅうSNS」で、知らない人からのDM・悪口・写真の投稿など20の場面を練習できます。iPhone・iPadのアプリ版もあります。"),
]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "れんしゅうAI（子ども向けAIの使い方練習）", "url": URL, "applicationCategory": "EducationalApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "子どもがAIを使い始めるころに、宿題の丸写し・AIのまちがい・個人情報・AIの友だち・家族の声をまねる電話・にせ動画など12の場面を練習できるツール。修了証つき。AIを呼び出さず入力も送らない。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}
LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
faq_html = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ))
lvname = dict(LEVELS)
rows = "".join(f'<tr><td>{lvname[s["lv"]].split(" ")[0]}</td><td>{s["title"]}</td><td>{s["point"]}。<a href="{s["art"][0]}">根拠</a></td></tr>' for s in SCENES)
DATA = {"levels": LEVELS, "scenes": [{k: s[k] for k in ("id", "lv", "title", "kicker", "art", "steps")} for s in SCENES]}

BODY = """<script type="application/ld+json">%LD%</script>
<p>子どもがスマホやタブレットでAIを使い始めるころに、「こんなとき、どうする？」を安全に練習できるページです。宿題の丸写し、AIのまちがい、名前を聞かれたとき、家族の声をまねる電話、にせ動画など12の場面があります。無料・広告なし・登録不要です。</p>
<div class="sp-app" id="sp">
<div class="sp-top"><b>れんしゅうAI</b><span>あいては練習用のAIだよ</span></div>
<div id="sp-step">
<div id="sp-home">
<p class="sp-hi">AIを使うときの「こんなとき、どうする？」を練習しよう。やってみたい場面をえらんでね。</p>
<p class="sp-prog" id="sp-prog"></p>
<div id="sp-levels"></div>
<div class="sp-cert-w" id="sp-cert-w"></div>
<p class="sp-rule">このページはほんもののAIにはつながっていないよ。えらんだ答えは、どこにも送られないよ。</p>
</div>
<div id="sp-play" hidden>
<div class="sp-feed" id="sp-feed" aria-live="polite"></div>
<div class="sp-ans" id="sp-ans"></div>
<button type="button" class="sp-next" id="sp-next" hidden>つぎへ</button>
</div>
<div id="sp-end" hidden></div>
</div>
</div>
<p class="answer"><strong>子どもがAIを使う前に練習したいのは「たしかめる・入れない・まかせきりにしない・話す」の4つです。</strong>AIの答えは本や教科書でたしかめる、名前や学校は入れない、宿題や作文はまかせきりにしない、こわい答えや悩みは大人に話す。この4つを12の場面で体験できます。</p>
<h2>練習できる12の場面</h2>
<table class="sp-t"><thead><tr><th>レベル</th><th>場面</th><th>安全な使い方の目安</th></tr></thead><tbody>%ROWS%</tbody></table>
<h2>おうちの人へ：練習のあとに話したいこと</h2>
<ul>
<li><b>宿題は「答え」でなく「ヒント」に。</b>答えを写す使い方では成績が下がり、ヒントとして使うと下がりにくいという研究があります。分かれ道は使い方です（<a href="/homework-ai-thinking-skills/">宿題とAIの記事</a>）。</li>
<li><b>AIへの相談を否定しない。そのうえで「人にも話していい」と伝える。</b>米国の12〜21歳の約5人に1人がAIに心の相談をし、そのうち6割強は誰にも話していませんでした（<a href="/ai-chatbot-worry-consultation-safety/">AIへの相談の記事</a>）。</li>
<li><b>設定だけに頼らず、話せる関係を。</b>AIとの性的なやりとりは12歳未満ほど多く、フィルターの効果も小さいとわかっています。「見てしまっても怒らないから教えてね」が守りの中心です（<a href="/ai-sexual-violent-content-filter-age-limit/">AIのフィルターの記事</a>）。</li>
<li><b>抜き打ちで履歴を見るより、時間と使い道を一緒に決める。</b>何もしないより、時間の把握や話し合いが問題の少なさと関連していました（<a href="/parent-ai-monitoring-how-much/">見守りの線引きの記事</a>）。</li>
</ul>
<p>家族のAI・スマホのルールは<a href="/rules/">わが家のルールづくり</a>で作って印刷できます。修了証は、そのルールと一緒に貼っておくのがおすすめです。</p>
<div class="note">れんしゅうシリーズ：<a href="/sns-practice/">れんしゅうSNS</a>（知らない人のDM・悪口・写真の投稿など20の場面）もあります。iPhone・iPadではアプリ<a href="https://apps.apple.com/app/id6820029513?ct=kosodate" target="_blank" rel="noopener">「れんしゅうSNS」（無料）</a>でも練習できます。</div>
<h2>よくある質問</h2>
%FAQ%
<script>
(function(){
var D=%DATA%,$=function(i){return document.getElementById(i)},KEY='kosodate-ai-practice-v1',cur,si,res;
var V={safe:['あんしん','ok'],careful:['ちょっと注意','mid'],risky:['きけん','ng']};
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){return {}}}
function save(o){try{localStorage.setItem(KEY,JSON.stringify(o))}catch(e){}}
function el(cls,html){var d=document.createElement('div');d.className=cls;d.innerHTML=html;return d}
function home(){var st=load(),done=st.done||[],n=D.scenes.filter(function(s){return done.indexOf(s.id)>=0}).length;
 $('sp-home').hidden=false;$('sp-play').hidden=true;$('sp-end').hidden=true;
 $('sp-prog').innerHTML='<b>'+n+'</b> / '+D.scenes.length+' クリア<span><i style="width:'+(n/D.scenes.length*100)+'%"></i></span>';
 $('sp-levels').innerHTML=D.levels.map(function(L){return '<h3 class="sp-lv">'+L[1]+'</h3><div class="sp-scenes">'+D.scenes.filter(function(s){return s.lv===L[0]}).map(function(s){var ok=done.indexOf(s.id)>=0;return '<button type="button" data-id="'+s.id+'"'+(ok?' class="done"':'')+'><small>'+s.kicker+(ok?'<em>クリア</em>':'')+'</small>'+s.title+'</button>'}).join('')+'</div>'}).join('');
 [].forEach.call($('sp-levels').querySelectorAll('button'),function(b){b.onclick=function(){start(b.getAttribute('data-id'))}});
 var w=$('sp-cert-w');
 if(n===D.scenes.length){w.innerHTML='<p class="sp-cert-h">ぜんぶクリア！修了証をつくろう</p><input type="text" id="sp-nick" maxlength="12" placeholder="ニックネーム（本名でなくてOK）" value="'+esc(st.nick||'')+'"><button type="button" id="sp-cbtn">修了証を見る</button><div id="sp-cert"></div>';
  $('sp-cbtn').onclick=function(){var nk=$('sp-nick').value.trim()||'あなた',s2=load();s2.nick=nk;save(s2);var d=new Date();
   $('sp-cert').innerHTML='<div class="sp-certc" id="sp-certc"><p class="sp-ck">修了証</p><h4>AIデビュー練習</h4><p class="sp-cn">'+esc(nk)+' さん</p><p>あなたは「れんしゅうAI」の'+D.scenes.length+'の場面をすべてクリアしました。<br>たしかめる・入れない・まかせきりにしない・話す。この4つを、ほんもののAIでも守ってね。</p><p class="sp-cd">'+d.getFullYear()+'年'+(d.getMonth()+1)+'月'+d.getDate()+'日</p><div class="sp-cs"><span>おうちの人のサイン</span><span>本人のサイン</span></div></div><button type="button" id="sp-cprint">印刷する</button>';
   $('sp-cprint').onclick=function(){document.body.classList.add('sp-printing');window.print();setTimeout(function(){document.body.classList.remove('sp-printing')},500)}}}
 else{w.innerHTML='<p class="sp-cert-n">'+D.scenes.length+'の場面をぜんぶクリアすると、修了証がもらえるよ。</p>'}}
function start(id){cur=D.scenes.filter(function(s){return s.id===id})[0];si=0;res=[];$('sp-home').hidden=true;$('sp-end').hidden=true;$('sp-play').hidden=false;$('sp-feed').innerHTML='';step();$('sp').scrollIntoView({behavior:'smooth',block:'start'})}
function step(){var t=cur.steps[si],f=$('sp-feed'),box=$('sp-ans');
 t.msgs.forEach(function(m){f.appendChild(el('sp-m '+(m[0].indexOf('あなた')===0?'sp-me':'sp-them'),'<small>'+esc(m[0])+'</small><p>'+esc(m[1])+'</p>'))});
 $('sp-next').hidden=true;
 box.innerHTML='<p class="sp-q">あなたなら、どうする？</p><div class="sp-ch">'+t.choices.map(function(c,k){return '<button type="button" data-k="'+k+'">'+esc(c[0])+'</button>'}).join('')+'</div>';
 [].forEach.call(box.querySelectorAll('button'),function(b){b.onclick=function(){var c=t.choices[+b.getAttribute('data-k')];
  f.appendChild(el('sp-m sp-me','<p>'+esc(c[0])+'</p>'));var e=el('sp-c sp-'+V[c[1]][1],'<b>'+V[c[1]][0]+'</b><p>'+esc(c[2])+'</p>');f.appendChild(e);box.innerHTML='';res.push(c[1]);
  $('sp-next').hidden=false;$('sp-next').textContent=si<cur.steps.length-1?'つぎへ':'ふりかえりを見る';e.scrollIntoView({behavior:'smooth',block:'nearest'})}})}
function end(){$('sp-play').hidden=true;var st=load();st.done=st.done||[];if(st.done.indexOf(cur.id)<0)st.done.push(cur.id);save(st);
 var e=$('sp-end'),ok=res.filter(function(v){return v==='safe'}).length;e.hidden=false;
 e.innerHTML='<p class="sp-score">'+esc(cur.title)+'<br><b>'+ok+' / '+res.length+'</b> あんしんな使い方</p><div class="sp-rv">'+cur.steps.map(function(t,i){return '<p><b>'+V[res[i]][0]+'</b>「'+esc(t.choices.filter(function(c){return c[1]==='safe'})[0][0])+'」が、あんしんな使い方の1つだよ。</p>'}).join('')+'</div>'
  +'<p class="sp-talk">おうちの人と話してみよう：「こんなことがあったら、どうする？」</p><p class="sp-rule">おうちの人へ：<a href="'+esc(cur.art[0])+'">'+esc(cur.art[1])+'</a></p><div class="sp-btns"><button type="button" id="sp-again">もう一回</button><button type="button" id="sp-home-b">ほかの場面</button></div>';
 $('sp-again').onclick=function(){start(cur.id)};$('sp-home-b').onclick=home;e.scrollIntoView({behavior:'smooth',block:'start'})}
$('sp-next').onclick=function(){if(si<cur.steps.length-1){si++;step()}else end()};
home();
})();
</script>"""

BODY = (BODY.replace("%LD%", LD).replace("%FAQ%", faq_html).replace("%ROWS%", rows)
        .replace("%DATA%", json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/")))

PAGE = {"path": "ai-practice", "title": "れんしゅうAI（子ども向け）",
        "seo_title": "子ども向けAIの使い方練習｜宿題の丸写し・AIのまちがい・にせ動画など12場面｜れんしゅうAI",
        "date": "2026-10-13",
        "desc": "子どもがAIを使い始めるころに、宿題の丸写し、AIのまちがい、名前を聞かれたとき、家族の声をまねる電話、にせ動画など12の場面を練習。修了証つき。AIにつながらず入力も送らない。無料・広告なし・登録不要。",
        "body": BODY, "css": SNS_CSS + ".sp-rule a{color:var(--link)}.sp-me small{color:#E3F1EA}"}
