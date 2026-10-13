"""AI時代の子育て「宿題の環境チェック」(/shukudai-check/) と「声かけの言いかえ帳」(/iikae/)。kosodate_tools.py が読み込む。

どちらも文言は出典照合済みの記事の「今日やること」と結論だけを使う(新しい主張は足さない)。
選んだ内容はブラウザの中だけで扱い、サーバーへは送らない。判定・診断はしない。
"""
import html
import json

E = html.escape
PUB = {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}


def _ld(name, url, desc, faq):
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": name, "url": url, "applicationCategory": "LifestyleApplication",
         "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "description": desc, "publisher": PUB},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]}
    return '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def _faq(faq):
    return "".join(f'<details{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(faq))


BASE_CSS = (".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
            ".xbody p a,.xbody li a,.sources a,.note a{color:var(--link)}"
            ".xbody>details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}.xbody>details summary{cursor:pointer;font-weight:700;font-size:15px}.xbody>details p{font-size:15px;margin-top:8px}"
            ".sources{margin-top:48px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:13px;color:var(--muted);margin:8px 0 8px 18px}"
            ".note{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}"
            ".k-btn{font:inherit;font-size:16px;font-weight:800;padding:12px 14px;border:1.5px solid var(--text);border-radius:12px;background:#E8B23A;color:#3B2F2A;cursor:pointer;min-height:52px}"
            ".k-btn.sub{background:var(--card);color:var(--text)}")

# ---------------------------------------------------------------- 宿題の環境チェック
# 各問いの選択肢: (値, ラベル, 変えるとよいか, 優先度(小さいほど先), 変えること, 記事)
SQ = [
    {"id": "media", "q": "宿題中、動画やSNSは？", "opts": [
        ("off", "見ない", None),
        ("some", "ときどき見る", ("宿題の時間だけ、動画・SNSと通知をオフにする", "宿題中に動画やスマホを同時に使う「ながら勉強」は、実行機能や成績の低さと関連する研究があります（相関）。", "homework-media-multitasking", 2)),
        ("on", "つけっぱなし", ("宿題の時間だけ、動画・SNSと通知をオフにする。見たい動画は「終わったら一緒に見よう」と後の楽しみにする", "宿題中に動画やスマホを同時に使う「ながら勉強」は、実行機能や成績の低さと関連する研究があります（相関）。", "homework-media-multitasking", 1))]},
    {"id": "ai", "q": "わからない問題で、AIは？", "opts": [
        ("none", "使わない", None),
        ("hint", "ヒントだけ聞く", None),
        ("answer", "答えを聞く・写す", ("「答えは聞かない、ヒントだけ」と決め、まず5分は自分で考えてからAIを開く", "答えを写すと学びは減り、ヒントとして使えば減りにくいとわかっています。", "homework-ai-thinking-skills", 1))]},
    {"id": "start", "q": "宿題を始めるのは？", "opts": [
        ("early", "帰ってすぐ〜夕ごはんの前", None),
        ("after", "夕ごはんの後", None),
        ("late", "寝る前ぎりぎり", ("宿題を始める時間を前に出す（例：夕ごはんの前に、まず1問だけ）", "大学生の研究では、答えの写しは締め切り直前に増え、主な原因は時間に追われることでした。", "ai-homework-copying-what-to-say", 3))]},
    {"id": "music", "q": "音楽は？", "opts": [
        ("silent", "かけない", None),
        ("inst", "歌詞のない曲", None),
        ("lyrics", "歌詞のある曲", ("読む・書く勉強のときだけ、無音か歌詞のない曲にする。曲は始める前に決めておく", "メタ分析では、音楽は読解をわずかに下げ、歌詞のある曲は歌詞のない曲より妨げが大きいとわかりました。", "study-music-lyrics-concentration", 4))]},
    {"id": "phone", "q": "スマホはどこにある？", "opts": [
        ("away", "別の部屋・かばんの中", None),
        ("room", "同じ部屋の見えない所", None),
        ("desk", "机の上", ("宿題の間だけ、スマホを見えない・手の届かない場所に置く（暗記や計算の宿題のときだけ、でもよい）", "研究のまとめでは、スマホが机にあると記憶の課題で小さな低下が見られました。注意の課題では差がはっきりせず、まだ結論は出ていません。", "smartphone-on-desk-homework-focus", 5))]},
]
SFAQ = [
    ("宿題中にスマホを机に置くと、集中力は下がりますか？",
     "研究のまとめでは、記憶を使う課題で小さな低下が見られましたが、注意の課題では差がはっきりせず、まだ結論は出ていません。迷ったら、宿題の間だけ見えない・手の届かない場所に置くのが手軽です。"),
    ("勉強中に音楽を聴くのはだめですか？",
     "だめとは言えません。ただ、文章を読む勉強では音楽が読解をわずかに下げ、歌詞のある曲ほど妨げが大きい傾向があります。読む・書く勉強のときだけ無音か歌詞のない曲にする、という決め方ができます。"),
    ("チェックの結果はどこかに保存されますか？",
     "保存しません。選んだ内容はこのページの中だけで使い、SEADICEのサーバーには送りません。カードは印刷するか、共有ボタンで家族に送ってください。"),
]
S_URL = "https://kosodate.seadice.win/shukudai-check/"
S_DESC = "スマホの置き場所、音楽、動画、AIの使い方、始める時間を選ぶと、研究から見て今日変えるとよいことを1つと、机に貼れる「宿題の前の約束」カードを作ります。無料・登録不要。"


def _shukudai():
    qs = ""
    for q in SQ:
        qs += f'<fieldset class="sk-q"><legend>{E(q["q"])}</legend><div class="sk-o">'
        for v, lab, _ in q["opts"]:
            qs += f'<label><input type="radio" name="{q["id"]}" value="{v}"><span>{E(lab)}</span></label>'
        qs += "</div></fieldset>"
    data = {q["id"]: {v: (None if a is None else {"t": a[0], "why": a[1], "href": f"/{a[2]}/", "p": a[3]}) for v, _, a in q["opts"]} for q in SQ}
    rows = "".join(f'<tr><td>{E(q["q"])}</td><td>' + "<br>".join(f'{E(lab)}：{E(a[0])}' for v, lab, a in q["opts"] if a) + "</td></tr>" for q in SQ)
    body = _ld("宿題の環境チェック", S_URL, S_DESC, SFAQ) + f"""
<p class="answer">宿題中は、動画やSNSを同時に見ない、AIには答えでなくヒントだけ聞く、が研究から見た優先順です。音楽とスマホの置き場所は影響が小さめで、勉強の種類によって分かれます。下で今の様子を選ぶと、今日変える1つがわかります。</p>
<form id="sk" class="sk-box" onsubmit="return false">{qs}
<button type="button" class="k-btn" id="sk-go">今日変える1つを見る</button>
<p class="sk-msg" id="sk-msg" role="status"></p></form>
<div id="sk-out" hidden><div class="sk-card" id="sk-card"></div>
<div class="sk-acts"><button type="button" class="k-btn" id="sk-print">カードを印刷する</button><button type="button" class="k-btn sub" id="sk-share">共有・コピーする</button></div></div>
<h2>判定のしかた</h2>
<p>「変えるとよい」になる選び方と、そのときに勧める行動の一覧です。優先順は、研究でわかっている関連の強さと、宿題の中身への影響の大きさで決めています（動画・SNSとAIの答えを先に、音楽とスマホの置き場所を後に）。</p>
<table class="sk-t"><thead><tr><th>問い</th><th>変えるとよい選び方：勧める行動</th></tr></thead><tbody>{rows}</tbody></table>
<h2>決めるときのコツ</h2>
<ul><li>親が一方的に決めず、子どもの意見も聞いて決めます。置き場所や音楽は「禁止」ではなく、ありとなしで同じ量の宿題を比べる「実験」にすると話し合いやすくなります（<a href="/smartphone-on-desk-homework-focus/">スマホの置き場所の記事</a>、<a href="/study-music-lyrics-concentration/">音楽の記事</a>）。</li>
<li>リビングで宿題をする家庭では、親のスマホも同じ場所に置くと、ルールの理由を説明しやすくなります。</li>
<li>AIの使い方は、学校によって決まりが違います。家で決めたことを先生にも伝え、学校の方針を聞いておきます（<a href="/ai-homework-copying-what-to-say/">AIで宿題を写していたときの記事</a>）。</li></ul>
<h2>よくある質問</h2>{_faq(SFAQ)}
<div class="sources"><h2>根拠にした記事</h2><ol>
<li><a href="/homework-media-multitasking/">宿題中に動画やスマホを見る「ながら勉強」、学力への影響は？</a></li>
<li><a href="/homework-ai-thinking-skills/">宿題にAIを使わせると考える力は落ちる？</a></li>
<li><a href="/ai-homework-copying-what-to-say/">小学生がAIで宿題の答えを写していた。気づいたときの声かけと次のルール</a></li>
<li><a href="/study-music-lyrics-concentration/">中学生が勉強中に音楽を聴いている。歌詞のある曲ほど読む勉強のじゃまになりやすい</a></li>
<li><a href="/smartphone-on-desk-homework-focus/">宿題中、スマホを机に置くだけで集中力は下がる？</a></li>
<li>論文・公的資料の出典は、各記事の出典欄に載せています（照合済み）。</li></ol></div>
<p class="note">このチェックは家庭の環境を見直すための目安で、子どもの集中力や学力を判定するものではありません。</p>
<script>
(function(){{
var D={json.dumps(data, ensure_ascii=False)},Q={json.dumps([[q["id"], q["q"]] for q in SQ], ensure_ascii=False)},$=function(i){{return document.getElementById(i)}};
function esc(s){{return String(s).replace(/[&<>"]/g,function(c){{return {{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
function pick(){{var r={{}};Q.forEach(function(q){{var e=document.querySelector('input[name='+q[0]+']:checked');if(e)r[q[0]]=e.value}});return r}}
var last='';
$('sk-go').addEventListener('click',function(){{var r=pick();
 if(Object.keys(r).length<Q.length){{$('sk-msg').textContent='5つの問いすべてを選んでください。';return}}$('sk-msg').textContent='';
 var ch=[],ok=[];Q.forEach(function(q){{var a=D[q[0]][r[q[0]]];if(a)ch.push(a);else ok.push(q[1])}});ch.sort(function(a,b){{return a.p-b.p}});
 var h='<p class="sk-k">宿題の前の約束</p>';
 if(!ch.length)h+='<h3>今の環境は、研究から見てよい形です</h3><p>このまま続けてください。迷ったときは、もう一度選び直して確かめられます。</p>';
 else{{h+='<h3>今日変える1つ</h3><p class="sk-one">'+esc(ch[0].t)+'</p><p class="sk-why">なぜ：'+esc(ch[0].why)+' <a href="'+ch[0].href+'">記事</a></p>';
  if(ch.length>1)h+='<h4>慣れたら次に</h4><ul>'+ch.slice(1).map(function(a){{return '<li>'+esc(a.t)+' <a href="'+a.href+'">記事</a></li>'}}).join('')+'</ul>'}}
 if(ok.length)h+='<h4>このままでよいこと</h4><ul>'+ok.map(function(t){{return '<li>'+esc(t)+'</li>'}}).join('')+'</ul>';
 $('sk-card').innerHTML=h;$('sk-out').hidden=false;
 last='宿題の前の約束\\n'+(ch.length?ch.map(function(a,i){{return (i?'・':'今日：')+a.t}}).join('\\n'):'今の環境のまま続ける')+'\\n\\n'+location.origin+'/shukudai-check/';
 $('sk-out').scrollIntoView({{behavior:'smooth',block:'start'}})}});
$('sk-print').addEventListener('click',function(){{window.print()}});
$('sk-share').addEventListener('click',function(){{var b=this;if(navigator.share){{navigator.share({{title:'宿題の前の約束',text:last}}).catch(function(){{}});return}}
 if(navigator.clipboard)navigator.clipboard.writeText(last).then(function(){{b.textContent='コピーしました'}},function(){{b.textContent='コピーできませんでした'}})}});
}})();
</script>"""
    css = BASE_CSS + (".sk-box{background:var(--card);border:1.5px solid var(--text);border-radius:18px;padding:18px 20px;margin:20px 0 28px;display:grid;gap:4px;box-shadow:4px 4px 0 var(--text)}"
                      ".sk-q{border:0;padding:0;margin:10px 0 4px}.sk-q legend{font-size:15px;font-weight:800;margin-bottom:8px}"
                      ".sk-o{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.sk-o label{display:block;cursor:pointer}.sk-o input{position:absolute;opacity:0}"
                      ".sk-o span{display:flex;align-items:center;justify-content:center;text-align:center;min-height:52px;padding:8px;border:1.5px solid var(--border);border-radius:12px;background:var(--bg);font-size:14px;font-weight:700;line-height:1.4}"
                      ".sk-o input:checked+span{border-color:var(--text);background:#F6E3B0;color:#3B2F2A}.sk-o input:checked+span::before{content:'\\2713';margin-right:4px}.sk-o input:focus-visible+span{outline:3px solid var(--accent);outline-offset:2px}"
                      ".sk-box .k-btn{margin-top:14px}.sk-msg{font-size:14px;font-weight:700;min-height:1.4em}"
                      ".sk-card{background:#fff;border:2px solid var(--text);border-radius:18px;padding:22px 20px;color:#3B2F2A}.sk-card a{color:#2A6FA8}"
                      ".sk-k{font-size:13px;font-weight:800;color:var(--accent2)}.sk-card h3{font-size:20px;font-weight:900;margin:4px 0 8px}.sk-one{font-size:17px;font-weight:800;line-height:1.7}"
                      ".sk-why{font-size:14px;margin-top:8px;line-height:1.75}.sk-card h4{font-size:14px;font-weight:800;color:var(--accent);margin:16px 0 4px}.sk-card ul{margin:0 0 0 20px}.sk-card li{font-size:15px;line-height:1.7;margin:4px 0}"
                      ".sk-acts{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}"
                      ".sk-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.sk-t th,.sk-t td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top;line-height:1.7}.sk-t th{background:var(--card)}"
                      "@media(max-width:420px){.sk-o span{font-size:13px;padding:6px}}"
                      "@media print{body>*:not(main),main>*:not(.xbody),.xbody>*:not(#sk-out),#sk-out>*:not(#sk-card){display:none!important}main{padding:0!important;margin:0!important;max-width:none!important}#sk-card{border:0;padding:0}body{background:#fff!important;background-image:none!important}}")
    return {"path": "shukudai-check", "title": "宿題の環境チェック",
            "seo_title": "宿題に集中できる環境チェック｜スマホの置き場所・音楽・AIの使い方から今日変える1つがわかる",
            "date": "2026-10-13", "desc": S_DESC, "body": body, "css": css}


# ---------------------------------------------------------------- 声かけの言いかえ帳
# (グループ, 場面, よくある言い方, 言いかえ[], なぜ, 記事slug)
IK = [
    ("ほめる", "テストや作品がよくできた", "すごい！天才だね！", ["ここを工夫したんだね", "よく考えたね、最後まで続けたね"],
     "大げさな褒め言葉は、特に自己肯定感が低い子には逆効果になることがあります。能力より、努力や工夫した過程を具体的に褒める方が安全です。", "inflated-praise-self-esteem"),
    ("ほめる", "失敗が怖くて挑戦しない", "次は完璧にできるよ", ["やってみたこと自体が、まずいいね"],
     "挑戦をためらう様子が見えたら、結果より取り組んだこと自体を先に認めてから、できた・できなかったを話します。", "inflated-praise-self-esteem"),
    ("きょうだい", "きょうだいと比べたくなった", "お兄ちゃんはできたのに", ["（名前を出さず）ここまで自分でやったね。あと少しだね"],
     "きょうだいを比べる関わりは、自己肯定感の低下やきょうだい関係の悪化と関連があります。その子自身の行動だけを見て伝えます。", "sibling-comparison-self-esteem"),
    ("きょうだい", "「ずるい」「ひいきだ」と言われた", "そんなことないでしょ", ["そう感じたんだね", "お兄ちゃんは中学生だから門限が遅いんだよ（理由を伝える）"],
     "接し方の差そのものより、子どもが「不公平だ」と強く感じ続けるかどうかが心への影響を左右します。気持ちを受け止めてから理由を説明します。", "sibling-differential-treatment-fairness"),
    ("しかる・注意", "かんしゃくを起こした", "泣きやみなさい！", ["（安全を確かめて少し待ってから）イヤだったね", "（落ち着いてから）さっきは〜で嫌だったんだね"],
     "かんしゃくは多くの子に見られる発達の一部です。気持ちを言葉にして受け止める関わりは、問題行動の少なさと関連しています。", "tantrum-coping-children-research"),
    ("しかる・注意", "嘘をついた", "なんで嘘をついたの！", ["何があったか教えて", "本当のことを教えてくれてありがとう"],
     "失敗より隠したことを厳しく叱る対応は、かえって嘘を増やす可能性があります。まず事情を聞き、正直に話せたことを認めます。", "children-lying-development-age"),
    ("しかる・注意", "AIで宿題の答えを写していた", "なんでズルしたの", ["どこで止まった？", "この1問だけ、一緒に解き直してみよう"],
     "写しの多くは時間に追われたときに起きます。理由を聞けば、次に何を変えればよいかが決まります。", "ai-homework-copying-what-to-say"),
    ("画面・ゲーム", "動画をもっと見たがる", "ダメ、もう終わり！", ["まだ見たいよね。今日はここまでにしよう", "あと2つ見る？それとも1つにして次は絵本にする？"],
     "頭ごなしに言うより、気持ちを一度認めてから次の見通しを伝える声かけのほうが、対立を減らしやすいとわかっています。", "youtube-more-please-how-to-say-no"),
    ("画面・ゲーム", "ゲームをやめない", "今すぐやめなさい！", ["この試合が終わったら、セーブして終わりにしよう"],
     "幼児の研究では、自然な区切りで画面を終えると切り替えが楽でした。終わり方は前もって決めておきます。", "game-cant-stop-time-limit-taking-away"),
    ("思春期", "話しかけても「別に」", "ちゃんと話しなさい", ["（その場で聞き出さず、車の中や夕食後に）今日どうだった？"],
     "思春期に親子の会話が一時的に減るのは、発達の過程でよく見られる変化です。子どもが自然に話し始めやすい場面を待ちます。", "adolescent-parent-conversation-decline"),
    ("思春期", "言うことを聞かない", "先に宿題をやりなさい", ["後で疲れて集中できなくなるから、先にやっておこう", "8時か9時、どっちがいい？"],
     "年齢が上がるほど、一方的な指示より、理由を添えて選択肢を示す関わりの方が効果的になる可能性があります。", "adolescent-parent-conversation-decline"),
    ("進路・習い事", "習い事を辞めたいと言う", "最後まで続けなさい", ["辞めたい理由を教えて", "回数を減らす、教室を変えるという手もあるよ"],
     "思春期にかけて習い事をやめる子は多く、辞めること自体が将来に悪影響を与えるという直接の証拠は見つかっていません。", "children-quitting-activities-research"),
]
IFAQ = [
    ("子どもを褒めるときは、どんな言葉がいいですか？",
     "「すごい」「天才」のような大げさな言葉より、「ここを工夫したね」「最後まで続けたね」のように、努力や工夫した過程を具体的に伝える言葉が安全です。大げさな褒め言葉は、特に自己肯定感が低い子には逆効果になることがあります。"),
    ("叱るときに、まず何を言えばいいですか？",
     "かんしゃく・嘘・宿題の写しのどれでも、研究にもとづく記事に共通するのは「まず気持ちや事情を聞く」ことです。厳しい言葉で問い詰めるより、何があったかを聞いてから、次にどうするかを一緒に決めます。"),
    ("選んだ言いかえはどこかに保存されますか？",
     "保存しません。選んだ場面はこのページの中だけで使い、印刷するとその場面だけのカードになります。SEADICEのサーバーには何も送りません。"),
]
I_URL = "https://kosodate.seadice.win/iikae/"
I_DESC = "「すごい！天才！」「お兄ちゃんはできたのに」「なんで嘘をついたの」。つい出る言い方を、研究にもとづく言いかえに。褒める・叱る・きょうだい・ゲーム・思春期の12場面。選んだ場面だけ印刷できます。無料・登録不要。"


def _iikae():
    groups = []
    for g, *_ in IK:
        if g not in groups:
            groups.append(g)
    chips = '<button type="button" class="ik-chip" aria-pressed="true" data-g="">すべて</button>' + "".join(
        f'<button type="button" class="ik-chip" aria-pressed="false" data-g="{E(g)}">{E(g)}</button>' for g in groups)
    cards = ""
    for i, (g, scene, bad, goods, why, slug) in enumerate(IK):
        cards += (f'<article class="ik-c" data-g="{E(g)}"><p class="ik-g">{E(g)}</p><h3>{E(scene)}</h3>'
                  f'<p class="ik-bad"><span>よくある言い方</span>{E(bad)}</p>'
                  f'<div class="ik-good"><span>言いかえ</span><ul>' + "".join(f"<li>{E(x)}</li>" for x in goods) + "</ul></div>"
                  f'<p class="ik-why">なぜ：{E(why)} <a href="/{slug}/">記事</a></p>'
                  f'<label class="ik-sel"><input type="checkbox" data-i="{i}"> 貼る用に選ぶ</label></article>')
    body = _ld("声かけの言いかえ帳", I_URL, I_DESC, IFAQ) + f"""
<p class="answer">子どもへの声かけは、大げさに褒めるより工夫した過程を具体的に、叱る前にはまず気持ちや事情を聞くのが、研究にもとづく記事に共通する基本です。場面ごとに、つい出る言い方と言いかえを並べました。</p>
<div class="ik-chips" role="group" aria-label="場面のしぼりこみ">{chips}</div>
<div class="ik-list" id="ik-list">{cards}</div>
<div class="ik-bar"><button type="button" class="k-btn" id="ik-print">選んだ場面を印刷する</button><span id="ik-n" role="status">まだ選んでいません（選ばずに印刷すると全部）</span></div>
<h2>言いかえの元にしたこと</h2>
<p>言いかえは、AI時代の子育ての記事（出典照合済み）の「今日からできること」と結論だけから作っています。言いかえは魔法の言葉ではなく、ふだんの関わりの一部です。うまく言えなかった日があっても、落ち着いてから振り返れば十分です。</p>
<h2>よくある質問</h2>{_faq(IFAQ)}
<div class="sources"><h2>根拠にした記事</h2><ol>""" + "".join(
        f'<li><a href="/{s}/">/{s}/</a></li>' for s in dict.fromkeys(x[5] for x in IK)) + """<li>論文・公的資料の出典は、各記事の出典欄に載せています（照合済み）。</li></ol></div>
<p class="note">ここに挙げたのは多くの家庭に向けた一般的な言いかえです。かんしゃくで頭を打つ・物を投げるなどが繰り返し目立つときや、子どもの様子で気になることがあるときは、かかりつけの小児科や自治体の子育て相談窓口に相談できます。</p>
<script>
(function(){
var $=function(i){return document.getElementById(i)},cs=[].slice.call(document.querySelectorAll('.ik-c'));
[].forEach.call(document.querySelectorAll('.ik-chip'),function(b){b.addEventListener('click',function(){var g=b.getAttribute('data-g');
 [].forEach.call(document.querySelectorAll('.ik-chip'),function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
 cs.forEach(function(c){c.hidden=!!g&&c.getAttribute('data-g')!==g})})});
function upd(){var n=document.querySelectorAll('.ik-sel input:checked').length;$('ik-n').textContent=n?n+'場面を選んでいます':'まだ選んでいません（選ばずに印刷すると全部）';
 cs.forEach(function(c){c.classList.toggle('on',c.querySelector('input').checked)});document.body.classList.toggle('ik-some',n>0)}
[].forEach.call(document.querySelectorAll('.ik-sel input'),function(i){i.addEventListener('change',upd)});
$('ik-print').addEventListener('click',function(){window.print()});
})();
</script>"""
    css = BASE_CSS + (".ik-chips{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 6px}"
                      ".ik-chip{font:inherit;font-size:14px;font-weight:700;min-height:44px;padding:8px 16px;border:1.5px solid var(--border);border-radius:999px;background:var(--card);color:var(--text);cursor:pointer}"
                      ".ik-chip[aria-pressed=true]{border-color:var(--text);background:#F6E3B0;color:#3B2F2A}"
                      ".ik-list{display:grid;gap:14px;margin:14px 0 20px}"
                      ".ik-c{background:var(--card);border:1.5px solid var(--border);border-radius:16px;padding:16px 18px}.ik-c.on{border-color:var(--text);box-shadow:3px 3px 0 var(--text)}"
                      ".ik-g{font-size:12px;font-weight:800;color:var(--accent2)}.ik-c h3{font-size:17px;font-weight:900;margin:2px 0 10px}"
                      ".ik-bad,.ik-good{font-size:15px;line-height:1.7;margin:6px 0}.ik-bad span,.ik-good span{display:inline-block;font-size:12px;font-weight:800;padding:2px 8px;border-radius:6px;margin-right:8px}"
                      ".ik-bad{color:var(--muted)}.ik-bad span{border:1px solid var(--border)}"
                      ".ik-good span{background:var(--accent);color:#fff}.ik-good ul{margin:6px 0 0 20px}.ik-good li{font-weight:800;margin:3px 0}"
                      ".ik-why{font-size:13px;color:var(--muted);line-height:1.75;margin-top:8px}.ik-why a{color:var(--link)}"
                      ".ik-sel{display:flex;align-items:center;gap:8px;font-size:14px;font-weight:700;margin-top:8px;min-height:44px;cursor:pointer}.ik-sel input{width:22px;height:22px;accent-color:var(--accent)}"
                      ".ik-bar{display:grid;gap:8px;margin:8px 0 24px}.ik-bar span{font-size:13px;color:var(--muted)}"
                      "@media print{body>*:not(main),main>*:not(.xbody),.xbody>*:not(.ik-list){display:none!important}main{padding:0!important;margin:0!important;max-width:none!important}"
                      ".ik-c{break-inside:avoid;border:1px solid #888!important;box-shadow:none!important;display:block!important}.ik-sel{display:none!important}body.ik-some .ik-c:not(.on){display:none!important}body{background:#fff!important;background-image:none!important}}")
    return {"path": "iikae", "title": "声かけの言いかえ帳",
            "seo_title": "子どもへの声かけ 言いかえ帳｜褒め方・叱り方・きょうだい・ゲームの12場面（研究にもとづく）",
            "date": "2026-10-13", "desc": I_DESC, "body": body, "css": css}


PAGES = [_shukudai(), _iikae()]
