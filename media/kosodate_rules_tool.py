"""AI時代の子育て「わが家のAI・スマホのルールづくり」(/rules/)。kosodate_tools.py が読み込む。

選んだルールはブラウザの中だけで扱い、保存は localStorage(この端末)だけ。サーバーへは送らない。
「なぜ」の文は、出典照合済みの記事の結論だけを使う。
"""
import json

URL = "https://kosodate.seadice.win/rules/"

FAQ = [
    ("子どものスマホのルールは、何を決めればいいですか？",
     "「いつ・何を・何分まで」を具体的に決めるのが基本です。あわせて、寝る前に使わない時間、スマホを置く場所、使わない場面、困ったときに話す相手を決めておくと、家族で迷いにくくなります。"),
    ("ルールは親が決めるのと、子どもと一緒に決めるのとどちらがいいですか？",
     "中学生くらいの年齢では、一方的に縛るやり方は逆効果になりやすく、理由を伝えて子どもの言い分も聞きながら一緒に決める方が効果的だとわかっています。"),
    ("作ったルールはどこかに保存されますか？",
     "この端末のブラウザの中だけに保存されます。SEADICEのサーバーには送りません。印刷するか、共有ボタンで家族に送って使ってください。"),
]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "わが家のAI・スマホのルールづくり", "url": URL, "applicationCategory": "LifestyleApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "子どもの年齢を選び、時間・寝る前・置き場所・AIの使い方などのルールを選ぶと、印刷・共有できる家庭のルール表ができます。目安はWHO・米国小児科学会・ユネスコの指針と研究から。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}
LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
faq_html = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ))

# ルールの候補。ages: 表示する年齢、on: 最初からチェックする年齢、why/href: 根拠(照合済み記事の結論)
RULES = [
    {"sec": "寝る前と置き場所", "items": [
        {"id": "bedroom", "t": "スマホ・タブレットを寝室に持ち込まない", "ages": "a2 a5 jh", "on": "a2 a5 jh",
         "why": "寝る1時間前にスマホを置き場所に戻し、寝室に画面のある機器を置かないことが、研究から見た基本の対策です。", "href": "/bedtime-screen-sleep/"},
        {"id": "charge", "t": "夜はリビングの決めた場所で充電する", "ages": "a5 jh", "on": "a5 jh"},
        {"id": "back", "t": "使い終わったら決めた場所に戻す", "ages": "a2 a5 jh", "on": ""},
    ]},
    {"sec": "使わない場面", "items": [
        {"id": "meal", "t": "食事中は画面を見ない", "ages": "a2 a5 jh", "on": "a2 a5 jh"},
        {"id": "hw", "t": "宿題中は動画やSNSを見ない（ながら勉強をしない）", "ages": "a5 jh", "on": "a5 jh",
         "why": "宿題中に動画やスマホを同時に使う「ながら勉強」は、実行機能や成績の低さと関連する研究があります。", "href": "/homework-media-multitasking/"},
        {"id": "talk", "t": "家族で話す時間は画面を置く", "ages": "a2 a5 jh", "on": ""},
    ]},
    {"sec": "見るもの・使い方", "items": [
        {"id": "together", "t": "動画はできるだけ親子で一緒に見て、見た後に話す", "ages": "u1 a1 a2", "on": "a2",
         "why": "スクリーン時間全体は言語スキルの低さと関連しますが、教育的な内容や親子で一緒に見ることは、言語スキルの高さと関連しています。", "href": "/screen-time-language-development-toddler/"},
        {"id": "apps", "t": "見る動画・使うアプリは親と決める", "ages": "a2 a5", "on": "a2 a5"},
        {"id": "pay", "t": "課金・アプリの追加は親に聞いてから", "ages": "a5 jh", "on": "a5 jh"},
        {"id": "game", "t": "ゲームのチャットで知らない人とやりとりしたら話す", "ages": "a5 jh", "on": "a5 jh",
         "why": "一律に禁止するより、一緒にゲームをする・話を聞くといった関わりの方が、見知らぬ人とのリスクを減らしやすいとわかっています。", "href": "/online-gaming-strangers-chat-risk/"},
    ]},
    {"sec": "AIの使い方", "items": [
        {"id": "aiwith", "t": "AIは大人と一緒に使う", "ages": "a5", "on": "a5",
         "why": "ひとりで使わせるのは13歳からが目安です。それより前は親と一緒に、答えを確かめながら使えば、学びに役立つ場面もあります。", "href": "/ai-age-for-kids/"},
        {"id": "aihint", "t": "宿題ではAIに答えを聞かず、ヒントだけもらう", "ages": "a5 jh", "on": "a5 jh",
         "why": "答えを写すと学びは減り、ヒントとして使えば減りにくいとわかっています。", "href": "/homework-ai-thinking-skills/"},
        {"id": "aifirst", "t": "まず自分で考えてから、AIを使う", "ages": "a5 jh", "on": "jh"},
        {"id": "aicheck", "t": "AIの答えは、本や別のサイトでも確かめる", "ages": "a5 jh", "on": "jh"},
        {"id": "aiinfo", "t": "名前・住所・学校名・顔写真はAIに入れない", "ages": "a5 jh", "on": "a5 jh"},
    ]},
    {"sec": "困ったとき", "items": [
        {"id": "tell", "t": "いやなこと・こわいことがあったら、家族のだれかに話す", "ages": "a5 jh", "on": "a5 jh"},
        {"id": "aitell", "t": "AIに話したことも、人に話していい", "ages": "a5 jh", "on": "a5 jh",
         "why": "深刻な悩みでは、AIは危険に気づけない・大人につなげないことがあり、人に代わる相談相手にはなりません。", "href": "/ai-chatbot-worry-consultation-safety/"},
        {"id": "noangry", "t": "（大人）話してくれたことを、まず怒らずに聞く", "ages": "a5 jh", "on": "a5 jh"},
    ]},
    {"sec": "大人も守ること", "items": [
        {"id": "adultmeal", "t": "（大人）食事中は大人もスマホを見ない", "ages": "u1 a1 a2 a5 jh", "on": "a2 a5 jh"},
        {"id": "adulttalk", "t": "（大人）子どもと話すときは、画面から目を離す", "ages": "u1 a1 a2 a5 jh", "on": "u1 a1 a2 a5 jh",
         "why": "スマホの使用量そのものより、子どもと過ごす時間に関わりが途切れないようにする工夫が大切です。", "href": "/parent-smartphone-technoference-children/"},
    ]},
]

BODY = """<script type="application/ld+json">%LD%</script>
<p>お子さんの年齢を選び、ルールを選んでいくと、家族で使えるルール表ができます。そのまま印刷したり、家族に送ったりできます。年齢ごとの目安は、WHO・米国小児科学会・ユネスコの指針と研究をもとにしています。無料・広告なし・登録不要です。</p>
<form class="rm-box" id="rm" onsubmit="return false">
<label for="rm-age">お子さんの年齢</label>
<select id="rm-age"><option value="">選んでください</option><option value="u1">1歳未満</option><option value="a1">1歳</option><option value="a2">2〜4歳</option><option value="a5">5歳〜小学生</option><option value="jh">中学生・高校生</option></select>
<div id="rm-main" hidden>
<p class="rm-tip" id="rm-tip"></p>
<h3>1日の時間</h3>
<div class="rm-two"><label>平日<select id="rm-wd"></select></label><label>休日<select id="rm-we"></select></label></div>
<p class="rm-warn" id="rm-warn" hidden>WHOの目安（2〜4歳は1日1時間まで）より長めです。</p>
<label for="rm-bed">寝る前に画面を消す時刻</label>
<select id="rm-bed"><option value="30">寝る30分前</option><option value="60" selected>寝る1時間前</option><option value="90">寝る1時間半前</option><option value="">決めない</option></select>
<div id="rm-list"></div>
<h3>わが家だけのルール（任意）</h3>
<input type="text" id="rm-c1" maxlength="40" placeholder="例：日曜の朝は家族で動画を1本だけ見る">
<input type="text" id="rm-c2" maxlength="40" placeholder="例：ゲームは宿題が終わってから">
<label for="rm-rev">ルールを見直す時期</label>
<select id="rm-rev"><option value="進級のとき">進級のとき</option><option value="誕生日">誕生日</option><option value="3か月後">3か月後</option></select>
<label class="rm-chk" id="rm-self-w"><input type="checkbox" id="rm-self"> 本人と話し合って決めた</label>
<button type="submit" id="rm-b">ルール表をつくる</button>
</div>
</form>
<div id="rm-out" hidden>
<div class="rm-card" id="rm-card"></div>
<div class="rm-acts"><button type="button" id="rm-print">印刷する</button><button type="button" id="rm-share">家族に送る</button></div>
<p class="rm-s">作ったルールはこの端末の中だけに保存されます（サーバーには送りません）。次に開いたときも続きから直せます。</p>
</div>
<p class="answer"><strong>ルールは「いつ・何を・何分まで」を具体的に決めるのが基本です。</strong>具体的なルールを決めて守る関わりは、推奨時間を守りやすいことと関連していました。中学生以上は本人と話し合って決めます。</p>
<h2>年齢ごとの目安</h2>
<table class="rm-t"><thead><tr><th>年齢</th><th>目安（指針・研究から）</th></tr></thead><tbody>
<tr><td>1歳未満</td><td>画面は見せない（ビデオ通話などは別）。WHOの指針より。</td></tr>
<tr><td>1歳</td><td>座ったまま動画やゲームを見続けることは勧められていない。WHOの指針より。</td></tr>
<tr><td>2〜4歳</td><td>画面は1日1時間まで、少ないほどよい（WHO）。見るときは親子で一緒に見る（米国小児科学会）。</td></tr>
<tr><td>5歳〜小学生</td><td>決まった時間の公的な目安はない。時間・場所・寝る前のルールを家族で決める。AIは大人と一緒に使う。</td></tr>
<tr><td>中学生・高校生</td><td>ルールは一方的に決めるより、本人と話し合って決める。授業でのAIツールの利用は13歳からが目安（ユネスコ、2023年）。</td></tr>
</tbody></table>
<h2>ルールを決めるときのコツ</h2>
<ul>
<li><b>具体的に決める。</b>「使いすぎない」ではなく「平日は夕食まで」のように決めます。具体的なルールを決めて守る関わりが多い家庭ほど、推奨時間を守れている関連がありました（<a href="/family-screen-time-rules-research/">ルールの作り方の記事</a>）。</li>
<li><b>子どもと一緒に決める。</b>中学生くらいの年齢では、一方的に縛るやり方は逆効果になりやすく、対話を通じた関わりの方が効果的だとわかっています（<a href="/junior-high-smartphone-rules-rebellion/">反抗期とスマホの記事</a>）。</li>
<li><b>大人も同じルールを守る。</b>親のスマホが親子の関わりをじゃまする「テクノフェアレンス」も研究されています。</li>
<li><b>見直す時期を決めておく。</b>年齢や学年が上がると、目安も変わります。</li>
</ul>
<p>いまの使い方を目安と比べたいときは、<a href="/screen-time-check/">スクリーンタイム判定</a>が使えます。</p>
<h2>よくある質問</h2>
%FAQ%
<div class="sources"><h2>出典</h2><ol>
<li>World Health Organization (2019). To grow up healthy, children need to sit less and play more. <a href="https://www.who.int/news/item/24-04-2019-to-grow-up-healthy-children-need-to-sit-less-and-play-more" target="_blank" rel="noopener">WHO</a></li>
<li>Council on Communications and Media, American Academy of Pediatrics (2016). Media and Young Minds. <i>Pediatrics</i>. <a href="https://doi.org/10.1542/peds.2016-2591" target="_blank" rel="noopener">doi:10.1542/peds.2016-2591</a></li>
<li>UNESCO (2023). Guidance for generative AI in education and research の公表. <a href="https://www.unesco.org/en/articles/unesco-governments-must-quickly-regulate-generative-ai-schools" target="_blank" rel="noopener">unesco.org</a></li>
<li>Hale, L., &amp; Guan, S. (2015). Screen time and sleep among school-aged children and adolescents: a systematic literature review. <i>Sleep Medicine Reviews</i>. <a href="https://doi.org/10.1016/j.smrv.2014.07.007" target="_blank" rel="noopener">doi:10.1016/j.smrv.2014.07.007</a></li>
<li>そのほか、各ルールの「なぜ」のリンク先の記事に出典を載せています。</li>
</ol></div>
<p class="note">このルール表は一般的な目安で、お子さんの発達や家庭の事情に合わせて調整してください。発達や睡眠で気になることがあるときは、かかりつけの小児科や自治体の子育て相談窓口に相談できます。</p>
<script>
(function(){
var R=%RULES%,$=function(i){return document.getElementById(i)},KEY='kosodate-rules-v1';
var AG={u1:'1歳未満',a1:'1歳',a2:'2〜4歳',a5:'5歳〜小学生',jh:'中学生・高校生'};
var TM={none:'画面は見せない（ビデオ通話は別）',30:'30分まで',60:'1時間まで',90:'1時間半まで',120:'2時間まで',180:'3時間まで',talk:'本人と決める',free:'決めない'};
function has(s,a){return (' '+s+' ').indexOf(' '+a+' ')>=0}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function opts(a){var k=(a==='u1'||a==='a1')?['none']:a==='a2'?['30','60','90','120']:a==='jh'?['talk','60','90','120','180','free']:['60','90','120','180','free'];return k.map(function(x){return '<option value="'+x+'">'+TM[x]+'</option>'}).join('')}
function load(){try{return JSON.parse(localStorage.getItem(KEY)||'null')}catch(e){return null}}
function save(s){try{localStorage.setItem(KEY,JSON.stringify(s))}catch(e){}}
function render(a,st){
 $('rm-main').hidden=!a;$('rm-out').hidden=true;if(!a)return;
 $('rm-wd').innerHTML=opts(a);$('rm-we').innerHTML=opts(a);
 var dflt=a==='a2'?'60':a==='u1'||a==='a1'?'none':a==='jh'?'talk':'60';
 $('rm-wd').value=st&&st.wd||dflt;$('rm-we').value=st&&st.we||dflt;
 $('rm-tip').textContent=a==='jh'?'中学生以上は、一方的に決めるより、理由を伝えて本人の言い分も聞きながら一緒に決める方が効果的だとわかっています。下の候補を、本人と話しながら選んでください。':a==='a5'?'小学生以上には、何時間までという公的な目安はありません。時間に加えて、寝る前・置き場所・使い方を決めておくのが研究から見た基本です。':'この年齢の目安はWHOの指針があります。最初から目安に沿ったルールを選んであるので、家庭に合わせて直してください。';
 $('rm-self-w').hidden=a!=='jh'&&a!=='a5';
 var h='';R.forEach(function(sec){var it=sec.items.filter(function(x){return has(x.ages,a)});if(!it.length)return;
  h+='<h3>'+sec.sec+'</h3>'+it.map(function(x){var on=st&&st.ids?st.ids.indexOf(x.id)>=0:has(x.on,a);
   return '<label class="rm-chk"><input type="checkbox" data-id="'+x.id+'"'+(on?' checked':'')+'> '+x.t+(x.why?'<small>なぜ：'+x.why+' <a href="'+x.href+'">記事</a></small>':'')+'</label>'}).join('')});
 $('rm-list').innerHTML=h;
 if(st){$('rm-bed').value=st.bed===undefined?'60':st.bed;$('rm-c1').value=st.c1||'';$('rm-c2').value=st.c2||'';$('rm-rev').value=st.rev||'進級のとき';$('rm-self').checked=!!st.self}
 warn();
}
function warn(){var a=$('rm-age').value,w=+$('rm-wd').value||0,e=+$('rm-we').value||0;$('rm-warn').hidden=!(a==='a2'&&(w>60||e>60))}
function state(){var ids=[].slice.call(document.querySelectorAll('#rm-list input:checked')).map(function(i){return i.getAttribute('data-id')});
 return {age:$('rm-age').value,wd:$('rm-wd').value,we:$('rm-we').value,bed:$('rm-bed').value,ids:ids,c1:$('rm-c1').value.trim(),c2:$('rm-c2').value.trim(),rev:$('rm-rev').value,self:$('rm-self').checked}}
function lines(s){var L=[],byId={};R.forEach(function(sec){sec.items.forEach(function(x){byId[x.id]=x})});
 L.push(['時間','平日：'+TM[s.wd]+(s.we!==s.wd?'／休日：'+TM[s.we]:'（休日も同じ）')]);
 if(s.bed)L.push(['寝る前と置き場所','寝る'+(s.bed==='60'?'1時間':s.bed==='90'?'1時間半':'30分')+'前には画面を消す']);
 R.forEach(function(sec){sec.items.forEach(function(x){if(s.ids.indexOf(x.id)>=0)L.push([sec.sec,x.t])})});
 if(s.c1)L.push(['わが家のルール',s.c1]);if(s.c2)L.push(['わが家のルール',s.c2]);return L}
function text(s){return 'わが家のAI・スマホのルール（'+AG[s.age]+'）\\n'+lines(s).map(function(l){return '・'+l[1]}).join('\\n')+'\\n見直す時期：'+s.rev+'\\n\\n'+location.origin+'/rules/'}
function card(s){var L=lines(s),g={},o=[];L.forEach(function(l){if(!g[l[0]]){g[l[0]]=[];o.push(l[0])}g[l[0]].push(l[1])});
 return '<p class="rm-k">'+AG[s.age]+'</p><h3>わが家のAI・スマホのルール</h3>'+o.map(function(k){return '<h4>'+esc(k)+'</h4><ul>'+g[k].map(function(t){return '<li>'+esc(t)+'</li>'}).join('')+'</ul>'}).join('')
  +'<p class="rm-rv">見直す時期：'+esc(s.rev)+'</p><div class="rm-sign"><span>決めた日</span><span>家族のサイン</span>'+(s.self?'<span>本人のサイン</span>':'')+'</div>'}
$('rm-age').addEventListener('change',function(){var st=load();render(this.value,st&&st.age===this.value?st:null)});
$('rm-wd').addEventListener('change',warn);$('rm-we').addEventListener('change',warn);
$('rm').addEventListener('submit',function(){var s=state();if(!s.age)return;save(s);$('rm-card').innerHTML=card(s);$('rm-out').hidden=false;$('rm-out').scrollIntoView({behavior:'smooth',block:'start'})});
$('rm-print').addEventListener('click',function(){window.print()});
$('rm-share').addEventListener('click',function(){var t=text(state()),b=this;
 if(navigator.share){navigator.share({title:'わが家のAI・スマホのルール',text:t}).catch(function(){});return}
 if(navigator.clipboard){navigator.clipboard.writeText(t).then(function(){b.textContent='コピーしました'},function(){b.textContent='コピーできませんでした'})}});
var st=load();if(st&&st.age){$('rm-age').value=st.age;render(st.age,st)}
})();
</script>"""

BODY = BODY.replace("%LD%", LD).replace("%FAQ%", faq_html).replace("%RULES%", json.dumps(RULES, ensure_ascii=False).replace("</", "<\\/"))

CSS = (".rm-box{background:var(--card);border:1.5px solid var(--text);border-radius:18px;padding:20px;margin:20px 0 28px;display:grid;gap:8px;box-shadow:4px 4px 0 var(--text)}"
       ".rm-box label{font-size:14px;font-weight:700;margin-top:6px;display:block}"
       ".rm-box input[type=text],.rm-box select{font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);min-height:48px;width:100%;margin-top:4px}"
       ".rm-box h3{font-size:16px;font-weight:900;margin:22px 0 4px;padding-top:14px;border-top:1px dashed var(--border)}"
       ".rm-tip{font-size:14px;line-height:1.75;background:var(--bg);border-left:4px solid var(--accent2);border-radius:8px;padding:12px 14px;margin-top:10px}"
       ".rm-two{display:grid;grid-template-columns:1fr 1fr;gap:10px}.rm-warn{font-size:13px;font-weight:700;color:var(--accent)}"
       ".rm-chk{display:flex!important;flex-wrap:wrap;gap:4px 10px;align-items:flex-start;font-size:15px!important;font-weight:600!important;line-height:1.6;padding:10px 0;border-bottom:1px solid var(--border);cursor:pointer}"
       ".rm-chk input{width:22px;height:22px;margin-top:2px;flex:0 0 22px;accent-color:var(--accent)}"
       ".rm-chk small{flex-basis:100%;padding-left:32px;font-size:13px;font-weight:400;color:var(--muted);line-height:1.65}.rm-chk small a{color:var(--link)}"
       ".rm-box button,.rm-acts button{font:inherit;font-size:17px;font-weight:800;margin-top:14px;padding:14px;border:1.5px solid var(--text);border-radius:12px;background:#E8B23A;color:var(--text);cursor:pointer;min-height:52px}"
       ".rm-card{background:#fff;border:2px solid var(--text);border-radius:18px;padding:22px 20px;margin:8px 0 0;color:#3B2F2A}"
       ".rm-card h3{font-size:21px;font-weight:900;margin:2px 0 10px}.rm-k{font-size:13px;font-weight:800;color:var(--accent2)}"
       ".rm-card h4{font-size:14px;font-weight:800;color:var(--accent);margin:16px 0 4px}.rm-card ul{margin:0 0 0 20px}.rm-card li{font-size:15px;line-height:1.7;margin:4px 0}"
       ".rm-rv{font-size:14px;margin-top:16px}.rm-sign{display:grid;grid-template-columns:1fr 1fr;gap:12px 16px;margin-top:16px}.rm-sign span{font-size:12px;color:#6E5F57;border-bottom:1px solid #6E5F57;padding-top:26px}"
       ".rm-acts{display:grid;grid-template-columns:1fr 1fr;gap:10px}.rm-acts button:last-child{background:var(--card)}.rm-s{font-size:13px;color:var(--muted);margin-top:8px}"
       ".answer{font-size:15px;margin:24px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".rm-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.rm-t th,.rm-t td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top;line-height:1.7}.rm-t th{background:var(--card)}"
       ".xbody ul li a,.xbody p a,.sources a,.note a{color:var(--link)}"
       ".xbody>details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}.xbody>details summary{cursor:pointer;font-weight:700;font-size:15px}.xbody>details p{font-size:15px;margin-top:8px}"
       ".sources{margin-top:48px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;word-break:break-all}"
       ".note{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}"
       "@media print{body>*:not(main),main>*:not(.xbody),.xbody>*:not(#rm-out),#rm-out>*:not(#rm-card){display:none!important}main{padding:0!important;margin:0!important;max-width:none!important}#rm-card{border:0;padding:0}body{background:#fff!important;background-image:none!important}}")

PAGE = {"path": "rules", "title": "わが家のAI・スマホのルールづくり",
        "seo_title": "子どものスマホ・AIルールの作り方｜年齢別に選んで印刷できるルール表",
        "date": "2026-10-07",
        "desc": "子どもの年齢を選び、時間・寝る前・置き場所・AIの使い方のルールを選ぶと、印刷・共有できる家庭のルール表ができます。WHO・米国小児科学会・ユネスコの指針と研究をもとに。無料・登録不要。",
        "body": BODY, "css": CSS}
