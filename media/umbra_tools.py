"""しぐさと本音のWebツール（/redflag-check/ と /myakuari-check/）。umbra_shigusa.py から呼ばれる。

  python3 media/umbra_shigusa.py && python3 media/build.py umbra

判定の文言は、出典照合済みの記事の結論だけを使う（AIには判定・アドバイスを書かせない）。入力はブラウザの中だけで判定し、送信・保存しない。
- 危険な相手のサイン: REDFLAG に項目を足す（記事が増えたら、その記事の結論から1行で）
- 脈ありチェック: umbra-shigusa.json の like タグの項目から自動で作る（索引に足せばツールにも出る）
ページの型は docs/quality/tool.md。
"""
import html
import json
import re
from pathlib import Path

E = html.escape
ROOT = Path(__file__).resolve().parent.parent
PUB = {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}
URL = "https://umbra.seadice.win/"

# 相談先（内閣府・警察庁の公的窓口）
CONTACTS = ('<ul class="tl-contact"><li>いま危険がある・身の危険を感じる：<a href="tel:110">110番</a></li>'
            '<li>DV相談ナビ（最寄りの相談窓口につながる）：<a href="tel:%238008">#8008</a></li>'
            '<li>DV相談＋（電話は24時間。メール・チャットもあり）：<a href="tel:0120279889">0120-279-889</a></li>'
            '<li>つきまとい・脅しなどの警察相談：<a href="tel:%239110">#9110</a></li></ul>')

# (id, グループ, 当てはまる行動, 記事slug, 記事の結論から1〜2文)
REDFLAG = [
    ("n1", "now", "叩く・押す・物を投げるなど、体や物への暴力がある", None, ""),
    ("n2", "now", "「別れたら〜する」など、脅すようなことを言われる", None, ""),
    ("c1", "control", "友達や家族と会うのを嫌がられ、会う回数が減った", "jealousy-possessiveness-control-research",
     "嫉妬という感情より、それが外出や交友の制限に結びつくかどうかが、関係の安全性を左右します。"),
    ("c2", "control", "「心配だから」と、外出・服装・交友を制限される", "jealousy-possessiveness-control-research",
     "「心配だから」という説明が、具体的な制限とセットになっていないかが手がかりです。納得できない制限は、距離を置く理由になり得ます。"),
    ("c3", "control", "スマホや位置情報を、同意なく見られる・見せるよう求められる", "partner-phone-checking-surveillance-research",
     "同意なく繰り返し監視することは、研究では「サイバーコントロール」という別の問題として扱われています。"),
    ("c4", "control", "お金を一方的に管理される・働くのを止められる", "financial-infidelity-warning-signs-research",
     "お金を隠すことと、収入や支出を一方的に管理・制限する「経済的DV」は別物です。研究では後者を暴力の一形態としています。"),
    ("c5", "control", "「ノー」と言うと、不機嫌になる・責められる", "jealousy-possessiveness-control-research",
     "こちらの「ノー」が尊重されるかどうかは、関係の安全性を見る手がかりです。"),
    ("m1", "mind", "言ったこと・あったことを「なかった」と言われ、自分の記憶や感覚を疑うようになった", "gaslighting-early-warning-signs",
     "「自分の感覚がおかしいのかも」という戸惑いそのものが、ガスライティングを経験した人に報告されている反応です。"),
    ("m2", "mind", "傷つけられる→謝られる→やり直しを約束される、を繰り返している", "moral-harassment-behavior-patterns-research",
     "「傷つける→謝る→やり直しを約束する」の繰り返しは、加害のサイクルとして研究で報告されています。"),
    ("m3", "mind", "ひどい扱いと優しさが交互に来て、離れられない", "trauma-bonding-why-hard-to-leave-research",
     "ひどい扱いと優しさが交互に来ることと力の差が、離れにくさと結びついていました。離れられないのは、あなたの弱さではありません。"),
    ("m4", "mind", "見下す・バカにする言い方をよくされる", "dating-violence-recognition-gender-gap-research",
     "支配や見下しのような目立ちにくい行動は、殴るなどの行動より暴力として気づかれにくいことがわかっています。"),
    ("e1", "early", "出会ってすぐ、大量の連絡・贈り物・「運命の人」という言葉が続く", "love-bombing-warning-signs-research",
     "強い好意そのものが悪いわけではありません。進むスピードと、こちらの境界線をどう扱うかを合わせて見ます。"),
    ("e2", "early", "最初は魅力的だったのに、約束を守らない・人を利用する言動が目立ってきた", "charming-first-impression-narcissism-research",
     "自己愛の傾向が強い人は第一印象で好かれやすく、数週間たつと評価が下がる傾向が確認されています。「話のうまさ」より「約束を守るか」を見ます。"),
    ("e3", "early", "謝らない・話をそらす・人のせいにする、が続く", "non-apology-psychology-barriers-research",
     "一度謝らなかったことだけで決めつけず、繰り返しのパターンと、言葉のあとに行動が変わるかを見ます。"),
]
GROUPS = [("now", "すぐに安全を考えたいこと"), ("control", "行動を制限される・孤立させられる"),
          ("mind", "気持ちや感覚を揺さぶられる"), ("early", "関係の始まり方・ふだんの言動")]

LV = {"a": "手がかりになる", "b": "状況しだい", "c": "当てにならない"}

CSS = (".tl-box{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:18px 18px 8px;margin:20px 0}"
       ".tl-box h2{font-size:16px;margin:18px 0 8px}.tl-box h2:first-child{margin-top:0}"
       ".tl-box label{display:flex;gap:12px;align-items:flex-start;padding:12px 4px;border-top:1px solid var(--border);font-size:15px;line-height:1.6;cursor:pointer}"
       ".tl-box input{width:22px;height:22px;flex:0 0 22px;margin-top:1px;accent-color:var(--accent)}"
       ".tl-btn{display:block;width:100%;margin:16px 0 10px;padding:14px;border:0;border-radius:12px;background:var(--accent);color:var(--bg);font-size:16px;font-weight:800;cursor:pointer}"
       ".tl-res{margin:20px 0;scroll-margin-top:80px}.tl-res[hidden]{display:none}.tl-card{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:14px;padding:16px 18px;margin:12px 0}"
       ".tl-card.alert{border-left-color:#E5534B}.tl-card h3{font-size:16px;margin-bottom:6px}.tl-card p{font-size:15px;line-height:1.8}.tl-card a{color:var(--link)}"
       ".tl-item{margin:10px 0;padding:12px 0;border-top:1px solid var(--border);font-size:15px;line-height:1.8}.tl-item b{display:block}.tl-item a{color:var(--link)}"
       ".tl-contact{margin:8px 0 0 1.2em;font-size:15px;line-height:1.9}.tl-contact a{color:var(--link);font-weight:700}"
       ".lv{display:inline-block;font-size:12px;font-weight:700;border-radius:999px;padding:1px 10px;margin-right:6px}.lv-a{background:#3FB98A;color:#0F0B16}.lv-b{background:#E8B04B;color:#0F0B16}.lv-c{background:#5C5470;color:#ECE7F2}"
       ".tl-tw{overflow-x:auto}.tl-tw table{border-collapse:collapse;width:100%;font-size:14px}.tl-tw th,.tl-tw td{border:0;border-bottom:1px solid var(--border);background:none;padding:10px 6px;text-align:left;vertical-align:top}"
       "details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0}summary{cursor:pointer;padding:14px 18px;font-weight:700}details p{padding:0 18px 16px}")


def _ld(name, url, desc, faq):
    return json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": name, "url": url, "applicationCategory": "LifestyleApplication", "operatingSystem": "Any",
         "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}, "description": desc, "publisher": PUB},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]},
        ensure_ascii=False).replace("</", "<\\/")


def _faq(faq):
    return "".join(f'<details{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(faq))


def redflag_page(posts):
    for _, _, _, s, _ in REDFLAG:
        assert s is None or s in posts, s
    boxes = ""
    for g, gl in GROUPS:
        boxes += f"<h2>{E(gl)}</h2>" + "".join(f'<label><input type="checkbox" name="rf" value="{i}">{E(t)}</label>' for i, gg, t, _, _ in REDFLAG if gg == g)
    data = {i: {"g": g, "t": t, "s": s, "n": n, "title": posts[s]["title"] if s else ""} for i, g, t, s, n in REDFLAG}
    faq = [
        ("恋人の束縛やモラハラは、どんなサインで気づけますか？", "研究では、嫉妬という感情の強さより、外出や交友・お金・スマホなど具体的な行動の制限に結びつくかどうかが、関係の安全性を左右するとされています。見下す言動や「傷つける→謝る」の繰り返しも、目立ちにくいサインです。"),
        ("当てはまったら、相手はモラハラやDVの加害者ということですか？", "いいえ。このチェックは相手を診断したりラベルを貼ったりするものではありません。気になる行動のパターンに気づき、記録や相談につなげるためのものです。"),
        ("入力した内容はどこかに送られますか？", "送られません。チェックはこのページの中（お使いのブラウザ）だけで判定し、SEADICEにも外部にも送信・保存しません。"),
        ("どこに相談すればいいですか？", "判断に迷う段階でも、DV相談ナビ（#8008）やDV相談＋（0120-279-889）に状況を話すだけで相談できます。いま危険があるときは110番に連絡してください。"),
    ]
    desc = "恋人・パートナーの言動に当てはまるものを選ぶと、研究でわかっていることと、今日からできること・相談先を表示します。束縛・モラハラ・ガスライティング・ラブボミングなど14項目。無料・登録不要・入力は送信しません。"
    ex = [("「友達と会うのを嫌がられる」「お金を一方的に管理される」", "行動を制限されるサインが2つ。距離を置く理由になり得ること、DV相談ナビ #8008 などの相談先"),
          ("「自分の記憶を疑うようになった」", "気持ちを揺さぶられるサインが1つ。出来事と気持ちをその日のうちに記録すること"),
          ("「出会ってすぐ大量の連絡」だけ", "始まり方のサイン。ただちに危険とは言えず、進むスピードと境界線の扱われ方を見ること"),
          ("「物を投げる」を含む", "ほかの結果より先に、安全を最優先にする案内と110番・相談窓口")]
    arts = sorted({s for _, _, _, s, _ in REDFLAG if s})
    body = (f'<script type="application/ld+json">{_ld("危険な相手のサイン チェックリスト", URL + "redflag-check/", desc, faq)}</script>'
            '<p>恋人やパートナーの言動で、当てはまるものを選んでください。研究でわかっていることと、今日からできること・相談先を表示します。入力はこのページの中だけで判定し、どこにも送りません。</p>'
            f'<form class="tl-box" id="rf" onsubmit="return false">{boxes}<button type="button" class="tl-btn" id="rf-go">結果を見る</button></form>'
            '<div class="tl-res" id="rf-res" aria-live="polite" hidden></div>'
            '<p class="answer">危険のサインは、嫉妬や好意の強さより「行動を制限されるか」「こちらのノーが尊重されるか」に表れます。1つでも、制限や孤立させる言動が続くなら、一人で抱えず相談してください。</p>'
            '<h2>判定のしかた</h2><ul>'
            '<li>選んだ項目を4つのまとまりに分け、まとまりごとに、出典照合済みの記事の結論を表示します。点数や「危険度◯%」は出しません。</li>'
            '<li>暴力や脅しの項目を選んだときは、ほかの結果より先に、安全を最優先にする案内と相談先を表示します。</li>'
            '<li>「関係の始まり方」だけを選んだときは、ただちに危険とは言えない、という研究の結論を表示します。</li></ul>'
            '<h2>入力例と結果</h2><div class="tl-tw"><table><thead><tr><th scope="col">選んだもの</th><th scope="col">表示される内容</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in ex) + '</tbody></table></div>'
            '<h2>判定のもとにした記事</h2><p>それぞれ、論文などの出典と照合した記事です。</p><ul>'
            + "".join(f'<li><a href="/{s}/">{E(posts[s]["title"])}</a></li>' for s in arts) + '</ul>'
            f'<h2>相談先</h2>{CONTACTS}'
            f'<h2>よくある質問</h2>{_faq(faq)}'
            '<p class="note">このチェックは相手を診断したり、ラベルを貼ったりするためのものではありません。心身の不調や被害が深刻なときは、専門機関に相談してください。</p>'
            "<script>(function(){var D=" + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";var C=" + json.dumps(CONTACTS, ensure_ascii=False).replace("</", "<\\/") + ";"
            "function e(s){return String(s).replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
            "function card(t,b,a){return '<div class=\"tl-card'+(a?' alert':'')+'\"><h3>'+t+'</h3>'+b+'</div>'}"
            "function items(ids){return ids.filter(function(i){return D[i].s}).map(function(i){var x=D[i];return '<div class=\"tl-item\"><b>'+e(x.t)+'</b>'+e(x.n)+'<br><a href=\"/'+x.s+'/\">記事を読む：'+e(x.title)+'</a></div>'}).join('')}"
            "document.getElementById('rf-go').onclick=function(){var ids=[].slice.call(document.querySelectorAll('#rf input:checked')).map(function(x){return x.value});"
            "var by={now:[],control:[],mind:[],early:[]};ids.forEach(function(i){by[D[i].g].push(i)});var h='';"
            "if(by.now.length)h+=card('安全を最優先にしてください','<p>暴力や脅しがあるときは、関係を続けるかどうかより先に、あなたの安全を考えてください。一人で決めて実行する必要はありません。相談窓口と一緒に計画を立てられます。</p>'+C,1);"
            "if(by.control.length)h+=card('行動を制限されるサインが'+by.control.length+'つあります','<p>嫉妬や心配という説明があっても、外出・交友・お金・スマホなどの制限が続くなら、我慢すべきことではありません。距離を置く理由になり得ます。判断に迷う段階でも、DV相談ナビ（#8008）に状況を話すだけで相談できます。</p>'+items(by.control));"
            "if(by.mind.length)h+=card('気持ちや感覚を揺さぶられるサインが'+by.mind.length+'つあります','<p>今日できることは、出来事と、そのときの気持ちをその日のうちに書き留めることです。日付と、言われたことをそのまま残します。記録は、自分の感覚を確かめる手がかりになります。</p>'+items(by.mind));"
            "if(by.early.length)h+=card('関係の始まり方・ふだんの言動のサインが'+by.early.length+'つあります','<p>これだけで、ただちに危険とは言えません。1回で決めつけず、進むスピードと、こちらの境界線がどう扱われるかを、しばらく見てください。</p>'+items(by.early));"
            "if(!ids.length)h=card('選ばれた項目はありません','<p>このリストの行動には当てはまりませんでした。違和感があるときは、言動のパターンを記録しておくと、あとで自分の感覚を確かめる手がかりになります。</p>');"
            "else if(!by.now.length)h+=card('相談先',C);"
            "var r=document.getElementById('rf-res');r.innerHTML=h;r.hidden=false;r.scrollIntoView({behavior:'smooth',block:'start'})};})();</script>")
    return {"path": "redflag-check", "title": "危険な相手のサイン チェックリスト", "date": "2026-10-07",
            "desc": "恋人の束縛・モラハラ・ガスライティング・ラブボミング。当てはまる言動を選ぶと、研究でわかっていることと今日からできること・相談先を表示します。入力は送信しません。",
            "seo_title": "恋人は危険？束縛・モラハラ・DVのサイン チェックリスト（研究にもとづく）", "body": body, "css": CSS}


def myakuari_page(D, posts):
    xs = [x for x in D if "like" in x.get("tags", [])]
    for x in xs:
        assert x["slug"] in posts, x["slug"]
    boxes = "".join(f'<label><input type="checkbox" name="mk" value="{E(x["id"])}">{E(x["gesture"])}</label>' for x in xs)
    data = {x["id"]: {"l": x["level"], "g": x["gesture"], "t": x["text"], "s": x["slug"], "title": posts[x["slug"]]["title"]} for x in xs}
    cnt = {k: sum(1 for x in xs if x["level"] == k) for k in "abc"}
    a_names = "・".join(x["gesture"] for x in xs if x["level"] == "a")
    faq = [
        ("脈ありサインで、本当に当てになるものはありますか？", f"しぐさと本音が研究で調べた脈ありサイン{len(xs)}種類のうち、傾向が確認されている手がかりは{cnt['a']}種類（{a_names}）でした。どれも一瞬のしぐさではなく、やりとりの積み重ねで見るものです。"),
        ("よく目が合う・触れてくるのは脈ありですか？", "どちらも「状況しだい」です。目が合うのは競争や対立の場面でも起こり、触れる量は性格・文化・関係の段階で変わります。それだけで恋愛感情は決められません。"),
        ("結局、相手の気持ちはどう確かめればいいですか？", "研究では、人は相手の好意を読むのが苦手で、会話のあとは相手からの好意を実際より低く見積もりやすいことがわかっています。サインを増やして推測するより、軽く言葉で確かめたり、誘ってみたりする方が確実です。"),
        ("入力した内容はどこかに送られますか？", "送られません。このページの中（お使いのブラウザ）だけで判定し、SEADICEにも外部にも送信・保存しません。"),
    ]
    desc = f"気になる相手のしぐさ・行動を選ぶと、それぞれが研究で「手がかりになる」「状況しだい」「当てにならない」のどれかを表示します。脈ありサイン{len(xs)}種類。無料・登録不要・入力は送信しません。"
    ex = [("「近くに座る」「会話のテンポが合う」", "手がかりになるサインが2つ重なっている。それでも、しぐさだけで本音は決まらず、軽く言葉で確かめる段階"),
          ("「よく目が合う」「よく笑ってくれる」", "どちらも状況しだい。これだけでは好意かどうか決められない"),
          ("「返信が速い」", "当てにならない。返信の速さと好意を直接結びつけた決定的な研究はない")]
    body = (f'<script type="application/ld+json">{_ld("脈ありチェック", URL + "myakuari-check/", desc, faq)}</script>'
            f'<p>気になる相手について、当てはまるものを選んでください。それぞれのしぐさ・行動が、研究でどこまで好意の手がかりになるのかを表示します。入力はこのページの中だけで判定し、どこにも送りません。</p>'
            f'<form class="tl-box" id="mk" onsubmit="return false">{boxes}<button type="button" class="tl-btn" id="mk-go">結果を見る</button></form>'
            '<div class="tl-res" id="mk-res" aria-live="polite" hidden></div>'
            f'<p class="answer">脈ありサイン{len(xs)}種類のうち、研究で傾向が確認された手がかりは{cnt["a"]}種類だけです。好意は1つのしぐさでは決まらず、距離・同期・会話のテンポなどの積み重ねで見ます。</p>'
            '<h2>判定のしかた</h2><ul>'
            f'<li>選んだしぐさを、<a href="/shigusa/hantei/">しぐさ判定の集計</a>と同じ3段階（手がかりになる {cnt["a"]}／状況しだい {cnt["b"]}／当てにならない {cnt["c"]}）で分けて表示します。</li>'
            '<li>「手がかりになる」が2つ以上重なったときだけ、「手がかりが重なっている」と表示します。それでも好意の有無は断定しません。</li>'
            '<li>判定文は、しぐさ・ボディランゲージ索引と同じ、出典照合済みの記事の結論です。点数や「脈あり度◯%」は出しません。</li></ul>'
            '<h2>入力例と結果</h2><div class="tl-tw"><table><thead><tr><th scope="col">選んだもの</th><th scope="col">表示される内容</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in ex) + '</tbody></table></div>'
            '<h2>判定のもとにした記事</h2><ul>'
            + "".join(f'<li><span class="lv lv-{x["level"]}">{LV[x["level"]]}</span><a href="/{x["slug"]}/">{E(x["gesture"])}</a></li>' for x in sorted(xs, key=lambda x: "abc".index(x["level"]))) + '</ul>'
            f'<h2>よくある質問</h2>{_faq(faq)}'
            '<p class="note">相手の気持ちを断定するものではありません。結果は、確かめ方を考えるための手がかりとして使ってください。</p>'
            "<script>(function(){var D=" + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";var LV={a:'手がかりになる',b:'状況しだい',c:'当てにならない'};"
            "function e(s){return String(s).replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
            "function card(t,b){return '<div class=\"tl-card\"><h3>'+t+'</h3>'+b+'</div>'}"
            "document.getElementById('mk-go').onclick=function(){var ids=[].slice.call(document.querySelectorAll('#mk input:checked')).map(function(x){return x.value});"
            "var n={a:0,b:0,c:0};ids.forEach(function(i){n[D[i].l]++});var h='',m;"
            "if(!ids.length)m=['選ばれた項目はありません','<p>当てはまるものを1つ以上選んでください。</p>'];"
            "else if(n.a>=2)m=['研究で傾向が確認された手がかりが'+n.a+'つ重なっています','<p>それでも、しぐさだけで本音は決まりません。サインを探し続けるより、軽く言葉で確かめたり、誘ってみたりする段階です。</p>'];"
            "else if(n.a==1)m=['研究で傾向が確認された手がかりが1つあります','<p>1回ではなく、その人のふだんとの違いと、積み重ねで見ます。ほかの手がかりが重なるかを、しばらく見てください。</p>'];"
            "else if(n.b)m=['選んだサインは、理由が複数ある「状況しだい」のものです','<p>これだけでは、好意かどうかは決められません。好意の手がかりとして研究で傾向が確認されているのは、距離・しぐさの同期・会話のテンポです。</p>'];"
            "else m=['選んだサインは、研究で通説が支持されていないものです','<p>これらは好意の有無を判断する材料になりません。気になるなら、しぐさより言葉で確かめる方が確実です。</p>'];"
            "h+=card(m[0],m[1]);"
            "if(ids.length){h+=card('選んだしぐさの判定',ids.sort(function(x,y){return D[x].l<D[y].l?-1:1}).map(function(i){var x=D[i];return '<div class=\"tl-item\"><b><span class=\"lv lv-'+x.l+'\">'+LV[x.l]+'</span>'+e(x.g)+'</b>'+e(x.t)+'<br><a href=\"/'+x.s+'/\">記事を読む：'+e(x.title)+'</a></div>'}).join(''));"
            "h+=card('今日からできること','<p>1つのサインで決めない。自分の期待をいったん脇に置く。迷ったら、軽く言葉で確かめる。人は会話のあと、相手からの好意を実際より低く見積もりやすいことも研究でわかっています。</p><p><a href=\"/love-signals-flirting-research/\">脈ありサインは当てになる？スピードデートの研究</a>／<a href=\"/dating-invitation-rejection-anxiety-research/\">デートに誘えないのはなぜか</a></p>');"
            "if(D['love-bombing']&&ids.indexOf('love-bombing')>=0)h+=card('「出会ってすぐの猛烈な好意」を選んだ方へ','<p>強い好意そのものは悪いことではありません。進むスピードと、こちらの境界線がどう扱われるかもあわせて見てください。<a href=\"/redflag-check/\">危険な相手のサイン チェックリスト</a>で確かめられます。</p>')}"
            "var r=document.getElementById('mk-res');r.innerHTML=h;r.hidden=false;r.scrollIntoView({behavior:'smooth',block:'start'})};})();</script>")
    return {"path": "myakuari-check", "title": "脈ありチェック", "date": "2026-10-07",
            "desc": desc[:120], "seo_title": f"脈ありチェック｜そのしぐさは好意のサイン？{len(xs)}種類を研究で判定", "body": body, "css": CSS}


def pages(D, posts):
    return [redflag_page(posts), myakuari_page(D, posts)]


# 関連する記事の本文に、ツールへの「次の一歩」を差し込む（出典の直前。再実行しても1つだけになるよう置き換える）
BLOCK = re.compile(r"<!--tool-->.*?<!--/tool-->\n?", re.S)


def link_articles(D):
    targets = {}
    for _, _, _, s, _ in REDFLAG:
        if s:
            targets[s] = ("/redflag-check/", "危険な相手のサイン チェックリスト", "当てはまる言動を選ぶと、研究でわかっていることと相談先を表示します。")
    for x in D:
        if "like" in x.get("tags", []) and x["slug"] not in targets:
            targets[x["slug"]] = ("/myakuari-check/", "脈ありチェック", "気になる相手のしぐさを選ぶと、研究でどこまで好意の手がかりになるかを表示します。")
    for s in ("love-signals-flirting-research", "dating-invitation-rejection-anxiety-research"):
        targets.setdefault(s, ("/myakuari-check/", "脈ありチェック", "気になる相手のしぐさを選ぶと、研究でどこまで好意の手がかりになるかを表示します。"))
    n = 0
    for s, (href, name, what) in targets.items():
        f = ROOT / f"sites/umbra/{s}/index.html"
        if not f.exists():
            continue
        t = BLOCK.sub("", f.read_text())
        blk = (f'<!--tool--><p style="margin:28px 0;padding:14px 18px;border:1px solid var(--accent);border-radius:12px;background:var(--card);font-size:15px;line-height:1.8">'
               f'<a href="{href}" style="color:var(--link);font-weight:700">{name}で確かめる</a><br>'
               f'<span style="font-size:13px;color:var(--muted)">{what}無料・入力は送信しません。</span></p><!--/tool-->\n')
        k = t.find("<!--shigusa-->")
        k = k if k >= 0 else t.find('<div class="sources">')
        if k < 0:
            continue
        f.write_text(t[:k] + blk + t[k:])
        n += 1
    return n
