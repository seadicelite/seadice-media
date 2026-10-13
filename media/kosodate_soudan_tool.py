"""AI時代の子育て「AIに話す？人に話す？ 親子で考える10問」(/ai-soudan/)。kosodate_tools.py が読み込む。

場面ごとのおすすめと理由は、出典照合済みの記事の結論・今日やることだけを使う。
答えも約束カードもブラウザの中だけで扱い、サーバーへは送らない(書いた大人の名前も保存しない)。
"""
import html
import json

from kosodate_use_tools import BASE_CSS, _faq, _ld

E = html.escape
URL = "https://kosodate.seadice.win/ai-soudan/"
DESC = "宿題、けんか、つらい気持ち、こわい返事、名前の入力。10の場面を親子で「AIでいい／AIと人の両方／人に話す／AIに入れない」に分けて考え、最後に話せる大人を書いたわが家の約束カードを印刷できます。無料・登録不要。"

CH = [("ai", "AIに聞いてOK"), ("both", "AIにも人にも"), ("human", "人に話す"), ("no", "AIに入れない")]
# (場面, おすすめ, 理由, 記事slug)
QS = [
    ("算数の問題の解き方がわからない", "ai",
     "AIに聞いてOK。ただし「答えは言わずにヒントだけ教えて」と頼みます。答えを写すと学びは減り、ヒントとして使えば減りにくいとわかっています。", "homework-ai-thinking-skills"),
    ("好きな恐竜のことを、もっと知りたい", "ai",
     "AIに聞いてOK。でもAIも間違えるので、本や別のサイトでも確かめます。", "ai-chatbot-conversations-children-risk"),
    ("友だちとちょっとけんかした。どうあやまろう", "both",
     "AIに話してもかまいません。軽い悩みをAIに話して「役に立った」と感じる子は多くいます。そのうえで「AIに話したことも、人に話していい」と覚えておきます。", "ai-chatbot-worry-consultation-safety"),
    ("毎晩さびしくて、AIとだけ話している", "both",
     "AIと話すのは悪いことではありません。ただ、つらい気持ちをAIだけに話し続けず、家族や友だちにも話します。AIは気持ちを完全にはわかってくれません。", "ai-companion-loneliness"),
    ("家出したいと話したら、AIが「いいと思う」と言った", "human",
     "大きな決めごとは、人にも聞きます。AIは否定しないぶん、危ない考えにも賛成してしまうことがあります。", "ai-chatbot-worry-consultation-safety"),
    ("「死にたい」と思うくらい、つらい", "human",
     "AIだけで終わらせず、必ず人に話します。研究では、危機の場面でAIは危険に気づけない・大人につなげないことがありました。親に言いにくいときは、先生や保健室の先生、下の相談窓口でもかまいません。", "ai-chatbot-worry-consultation-safety"),
    ("だれかに体をさわられた・たたかれた", "human",
     "命や体に関わることは、AIではなく人に話します。親に言いにくいときに話せる大人を、前もって2〜3人決めておくと安心です。", "ai-chatbot-worry-consultation-safety"),
    ("AIから、気持ち悪い・こわい返事が来た", "human",
     "会話を止めて閉じていい。そして大人に話します。フィルターや年齢制限だけでは防ぎきれず、話してくれることがいちばんの守りになります。", "ai-sexual-violent-content-filter-age-limit"),
    ("名前と学校名を教えたら、もっとくわしく答えてくれそう", "no",
     "名前・住所・学校名・顔写真・パスワードは入れません。入れたことはAIの向こうの会社に届き、学習に使われることもあります。入れてしまったら、責めずに親と一緒に会話を消します。", "child-told-ai-name-school-privacy"),
    ("AIで変なことを話したのが親にばれたら、おこられそう", "human",
     "話して大丈夫。親は先に「話してくれたら怒らない」と約束し、話してくれたらまず「教えてくれてありがとう」と返します。叱られると思うと、子どもは話さなくなります。", "ai-sexual-violent-content-filter-age-limit"),
]
FAQ = [
    ("子どもがAIに悩みを相談するのは危ないですか？",
     "軽い悩みをAIに話すことは、多くの子が役に立ったと感じています。ただ、深刻な悩みではAIが危険に気づけない・大人につなげないことがあり、人に代わる相談相手にはなりません。命や体に関わる悩みは人に話す、と前もって約束しておくのが大切です。"),
    ("このクイズに「正解」はありますか？",
     "研究にもとづく記事から見た「おすすめ」を示していますが、家庭によって決め方は違ってかまいません。親子で答えがずれた場面こそ、話し合うきっかけにしてください。"),
    ("約束カードに書いた名前は保存されますか？",
     "保存しません。カードはこのページの中だけで作り、印刷するとそのまま使えます。SEADICEのサーバーには何も送りません。"),
]


def page():
    chs = "".join(f'<button type="button" data-c="{c}">{E(l)}</button>' for c, l in CH)
    qs = "".join(
        f'<li class="as-q" data-a="{a}"><p class="as-s"><span>{i + 1}</span>{E(s)}</p><div class="as-c" role="group" aria-label="{E(s)}">{chs}</div>'
        f'<p class="as-r" hidden><b>おすすめ：{E(dict(CH)[a])}</b> {E(why)} <a href="/{slug}/">記事</a></p></li>'
        for i, (s, a, why, slug) in enumerate(QS))
    table = "".join(f'<tr><td>{E(s)}</td><td>{E(dict(CH)[a])}</td></tr>' for s, a, _, _ in QS)
    body = _ld("AIに話す？人に話す？ 親子で考える10問", URL, DESC, FAQ) + f"""
<p class="answer">軽い悩みや調べものはAIに聞いてもかまいません。ただ、命や体に関わること、こわい返事、大きな決めごとは人に話し、名前や学校名はAIに入れない。これが研究にもとづく記事に共通する線引きです。親子で10の場面を分けてみてください。</p>
<ol class="as-list" id="as-list">{qs}</ol>
<p class="as-msg" id="as-msg" role="status"></p>
<div class="as-make">
<h2>わが家の約束カード</h2>
<p>親に言いにくいとき話せる大人を、子どもと一緒に2〜3人決めて書きます（名前は保存されません）。</p>
<label for="as-p1">話せる大人 1</label><input type="text" id="as-p1" maxlength="20" placeholder="例：おばあちゃん">
<label for="as-p2">話せる大人 2</label><input type="text" id="as-p2" maxlength="20" placeholder="例：担任の先生">
<label for="as-p3">話せる大人 3</label><input type="text" id="as-p3" maxlength="20" placeholder="例：保健室の先生">
<button type="button" class="k-btn" id="as-go">カードを作る</button>
</div>
<div id="as-out" hidden><div class="as-card" id="as-card"></div>
<div class="as-acts"><button type="button" class="k-btn" id="as-print">カードを印刷する</button></div></div>
<h2>相談窓口</h2>
<p>24時間こどもSOSダイヤル（文部科学省、通話無料）：<a href="tel:0120078310">0120-0-78310</a>。いじめ、家族のこと、ネットの悪口など、どんな悩みでも夜間・休日も相談できます。ほかの窓口は<a href="https://www.mext.go.jp/a_menu/shotou/seitoshidou/06112210.htm" target="_blank" rel="noopener">文部科学省の子供のSOSの相談窓口</a>にまとまっています。</p>
<h2>10問のおすすめ一覧</h2>
<table class="as-t"><thead><tr><th>場面</th><th>おすすめ</th></tr></thead><tbody>{table}</tbody></table>
<h2>よくある質問</h2>{_faq(FAQ)}
<div class="sources"><h2>根拠にした記事</h2><ol>""" + "".join(
        f'<li><a href="/{s}/">/{s}/</a></li>' for s in dict.fromkeys(q[3] for q in QS)) + """<li>論文・公的資料の出典は、各記事の出典欄に載せています（照合済み）。</li>
<li>文部科学省「子供のSOSの相談窓口」 <a href="https://www.mext.go.jp/a_menu/shotou/seitoshidou/06112210.htm" target="_blank" rel="noopener">mext.go.jp</a></li></ol></div>
<p class="note">おすすめは多くの家庭に向けた目安で、子どもの答えを採点するものではありません。答えが分かれた場面は、親子で話すきっかけにしてください。</p>
<script>
(function(){
var $=function(i){return document.getElementById(i)},L={ai:'AIに聞いてOK',both:'AIにも人にも',human:'人に話す',no:'AIに入れない'};
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
var qs=[].slice.call(document.querySelectorAll('.as-q'));
qs.forEach(function(q){[].forEach.call(q.querySelectorAll('.as-c button'),function(b){b.addEventListener('click',function(){
 var a=q.getAttribute('data-a'),c=b.getAttribute('data-c');
 [].forEach.call(q.querySelectorAll('.as-c button'),function(x){x.setAttribute('aria-pressed',x===b?'true':'false');x.classList.toggle('rec',x.getAttribute('data-c')===a)});
 q.classList.toggle('diff',c!==a);q.querySelector('.as-r').hidden=false;
 var n=qs.filter(function(x){return !x.querySelector('.as-r').hidden}).length,d=qs.filter(function(x){return x.classList.contains('diff')}).length;
 $('as-msg').textContent=n+' / 10問'+(n===10?(d?'。おすすめと分かれたのは'+d+'問。そこを親子で話してみてください。':'。すべておすすめと同じでした。'):'')})})});
$('as-go').addEventListener('click',function(){var p=['as-p1','as-p2','as-p3'].map(function(i){return $(i).value.trim()}).filter(Boolean);
 $('as-card').innerHTML='<p class="as-k">わが家のAIの約束</p><h3>AIに話す？人に話す？</h3><ul>'
 +'<li>調べものや勉強はAIに聞いてOK。答えではなくヒントをもらう</li>'
 +'<li>名前・住所・学校名・顔写真・パスワードはAIに入れない</li>'
 +'<li>こわい・気持ち悪い返事が来たら、閉じて大人に話す</li>'
 +'<li>命や体に関わること、大きな決めごとは、人に話す</li>'
 +'<li>話してくれたら、おうちの人は怒らない</li></ul>'
 +'<h4>話せる大人</h4><p class="as-ppl">'+(p.length?p.map(esc).join('　／　'):'（　　　　）（　　　　）（　　　　）')+'</p>'
 +'<p class="as-tel">24時間こどもSOSダイヤル 0120-0-78310（通話無料）</p>';
 $('as-out').hidden=false;$('as-out').scrollIntoView({behavior:'smooth',block:'start'})});
$('as-print').addEventListener('click',function(){window.print()});
})();
</script>"""
    css = BASE_CSS + (".as-list{list-style:none;margin:18px 0 8px;padding:0;display:grid;gap:12px}"
                      ".as-q{background:var(--card);border:1.5px solid var(--border);border-radius:16px;padding:14px 16px}"
                      ".as-s{font-size:16px;font-weight:800;line-height:1.6;display:flex;gap:10px}.as-s span{flex:0 0 26px;height:26px;border-radius:50%;background:var(--accent);color:#fff;font-size:13px;display:flex;align-items:center;justify-content:center}"
                      ".as-c{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px}"
                      ".as-c button{font:inherit;font-size:14px;font-weight:700;min-height:48px;padding:8px;border:1.5px solid var(--border);border-radius:12px;background:var(--bg);color:var(--text);cursor:pointer}"
                      ".as-c button[aria-pressed=true]{border-color:var(--text);background:#F6E3B0;color:#3B2F2A}.as-c button[aria-pressed=true]::before{content:'\\2713 '}"
                      ".as-c button.rec{outline:3px solid #4C9A6A;outline-offset:-3px}.as-c button.rec::after{content:'（おすすめ）';font-size:12px;font-weight:600}"
                      ".as-r{font-size:14px;line-height:1.8;margin-top:10px;padding:10px 12px;background:var(--bg);border-radius:10px}.as-r a{color:var(--link)}"
                      ".as-msg{font-size:14px;font-weight:700;min-height:1.4em;margin-bottom:10px}"
                      ".as-make{background:var(--card);border:1.5px solid var(--text);border-radius:18px;padding:18px 20px;margin:20px 0;display:grid;gap:6px;box-shadow:4px 4px 0 var(--text)}"
                      ".as-make h2{margin-top:0}.as-make label{font-size:14px;font-weight:700;margin-top:6px}"
                      ".as-make input{font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);min-height:48px;width:100%}.as-make .k-btn{margin-top:12px}"
                      ".as-card{background:#fff;border:2px solid var(--text);border-radius:18px;padding:22px 20px;color:#3B2F2A}"
                      ".as-k{font-size:13px;font-weight:800;color:var(--accent2)}.as-card h3{font-size:20px;font-weight:900;margin:4px 0 10px}.as-card ul{margin:0 0 0 20px}.as-card li{font-size:15px;line-height:1.75;margin:4px 0}"
                      ".as-card h4{font-size:14px;font-weight:800;color:var(--accent);margin:16px 0 4px}.as-ppl{font-size:16px;font-weight:700}.as-tel{font-size:14px;margin-top:14px;font-weight:700}"
                      ".as-acts{margin-top:12px;display:grid}"
                      ".as-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.as-t th,.as-t td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top;line-height:1.7}.as-t th{background:var(--card)}"
                      "@media print{body>*:not(main),main>*:not(.xbody),.xbody>*:not(#as-out),#as-out>*:not(#as-card){display:none!important}main{padding:0!important;margin:0!important;max-width:none!important}#as-card{border:0;padding:0}body{background:#fff!important;background-image:none!important}}")
    return {"path": "ai-soudan", "title": "AIに話す？人に話す？ 親子で考える10問",
            "seo_title": "子どもがAIに相談していい悩み・人に話す悩み｜親子で考える10問と約束カード",
            "date": "2026-10-13", "desc": DESC, "body": body, "css": css}


PAGE = page()
