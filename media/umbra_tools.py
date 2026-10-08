"""しぐさと本音のWebツール（/redflag-check/ /myakuari-check/ /uso-check/ /sameta-check/）。umbra_shigusa.py から呼ばれる。

  python3 media/umbra_shigusa.py && python3 media/build.py umbra

判定の文言は、出典照合済みの記事の結論だけを使う（AIには判定・アドバイスを書かせない）。入力はブラウザの中だけで判定し、送信・保存しない。
- 危険な相手のサイン: REDFLAG に項目を足す（記事が増えたら、その記事の結論から1行で）
- 冷めたサインチェック: SAMETA に項目を足す（REDFLAG と同じく、記事の結論から1〜2文で）
- 脈ありチェック・嘘のサインチェック: umbra-shigusa.json の like / lie タグの項目から自動で作る（索引に足せばツールにも出る）
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
    ("c6", "control", "気づいたら、相談できる友人や家族がほとんどいなくなっていた", "friend-isolation-coercive-control-danger-research",
     "交友関係の制限が単独で起きているか、他の制限とセットになっているかを見ることが手がかりです。支配の強い相手と別れた・離れた状態は、研究で命に関わる危険因子として確認されています。"),
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
            "if(ids.length)h+=card('続けて記録したい人へ','<p>同じことが繰り返されているかは、日付つきで残すと見えてきます。<a href=\"/nikki/\">ふたりの日記</a>なら、気分の1タップと短い言葉のボタンで記録できます。記録は端末の中だけに保存されます。</p>');"
            "var r=document.getElementById('rf-res');r.innerHTML=h;r.hidden=false;r.scrollIntoView({behavior:'smooth',block:'start'})};})();</script>")
    return {"path": "redflag-check", "title": "危険な相手のサイン チェックリスト", "date": "2026-10-07",
            "desc": "恋人の束縛・モラハラ・ガスライティング・ラブボミング。当てはまる言動を選ぶと、研究でわかっていることと今日からできること・相談先を表示します。入力は送信しません。",
            "seo_title": "恋人は危険？束縛・モラハラ・DVのサイン チェックリスト（研究にもとづく）", "body": body, "css": CSS}


def _gesture_tool(xs, posts, fid, path, name, seo_title, desc, intro, answer, how, ex, faq, verdict_js, after_js, note):
    """索引の項目(xs)から、しぐさを選んで3段階の判定を見るツールを作る（脈ありチェック・嘘のサインチェック共通）。
    verdict_js は n={a,b,c}（選んだ数）と ids から m=[見出し, 本文HTML] を決めるJS。after_js は結果の末尾に足すカード。"""
    for x in xs:
        assert x["slug"] in posts, x["slug"]
    boxes = "".join(f'<label><input type="checkbox" name="{fid}" value="{E(x["id"])}">{E(x["gesture"])}</label>' for x in xs)
    data = {x["id"]: {"l": x["level"], "g": x["gesture"], "t": x["text"], "s": x["slug"], "title": posts[x["slug"]]["title"]} for x in xs}
    body = (f'<script type="application/ld+json">{_ld(name, URL + path + "/", desc, faq)}</script>'
            f'<p>{E(intro)}入力はこのページの中だけで判定し、どこにも送りません。</p>'
            f'<form class="tl-box" id="{fid}" onsubmit="return false">{boxes}<button type="button" class="tl-btn" id="{fid}-go">結果を見る</button></form>'
            f'<div class="tl-res" id="{fid}-res" aria-live="polite" hidden></div>'
            f'<p class="answer">{E(answer)}</p>'
            f'<h2>判定のしかた</h2><ul>{how}</ul>'
            '<h2>入力例と結果</h2><div class="tl-tw"><table><thead><tr><th scope="col">選んだもの</th><th scope="col">表示される内容</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in ex) + '</tbody></table></div>'
            '<h2>判定のもとにした記事</h2><ul>'
            + "".join(f'<li><span class="lv lv-{x["level"]}">{LV[x["level"]]}</span><a href="/{x["slug"]}/">{E(x["gesture"])}</a></li>' for x in sorted(xs, key=lambda x: "abc".index(x["level"]))) + '</ul>'
            f'<h2>よくある質問</h2>{_faq(faq)}'
            f'<p class="note">{E(note)}</p>'
            "<script>(function(){var D=" + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";var LV={a:'手がかりになる',b:'状況しだい',c:'当てにならない'};"
            "function e(s){return String(s).replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
            "function card(t,b){return '<div class=\"tl-card\"><h3>'+t+'</h3>'+b+'</div>'}"
            f"document.getElementById('{fid}-go').onclick=function(){{var ids=[].slice.call(document.querySelectorAll('#{fid} input:checked')).map(function(x){{return x.value}});"
            "var n={a:0,b:0,c:0};ids.forEach(function(i){n[D[i].l]++});var h='',m;"
            "if(!ids.length)m=['選ばれた項目はありません','<p>当てはまるものを1つ以上選んでください。</p>'];else{" + verdict_js + "}"
            "h+=card(m[0],m[1]);"
            "if(ids.length){h+=card('選んだしぐさの判定',ids.sort(function(x,y){return D[x].l<D[y].l?-1:1}).map(function(i){var x=D[i];return '<div class=\"tl-item\"><b><span class=\"lv lv-'+x.l+'\">'+LV[x.l]+'</span>'+e(x.g)+'</b>'+e(x.t)+'<br><a href=\"/'+x.s+'/\">記事を読む：'+e(x.title)+'</a></div>'}).join(''));" + after_js + "}"
            f"var r=document.getElementById('{fid}-res');r.innerHTML=h;r.hidden=false;r.scrollIntoView({{behavior:'smooth',block:'start'}})}};}})();</script>")
    return {"path": path, "title": name, "date": "2026-10-07", "desc": desc[:120], "seo_title": seo_title, "body": body, "css": CSS}


def myakuari_page(D, posts):
    xs = [x for x in D if "like" in x.get("tags", [])]
    cnt = {k: sum(1 for x in xs if x["level"] == k) for k in "abc"}
    a_names = "・".join(x["gesture"] for x in xs if x["level"] == "a")
    faq = [
        ("脈ありサインで、本当に当てになるものはありますか？", f"しぐさと本音が研究で調べた脈ありサイン{len(xs)}種類のうち、傾向が確認されている手がかりは{cnt['a']}種類（{a_names}）でした。どれも一瞬のしぐさではなく、やりとりの積み重ねで見るものです。"),
        ("よく目が合う・触れてくるのは脈ありですか？", "どちらも「状況しだい」です。目が合うのは競争や対立の場面でも起こり、触れる量は性格・文化・関係の段階で変わります。それだけで恋愛感情は決められません。"),
        ("結局、相手の気持ちはどう確かめればいいですか？", "研究では、人は相手の好意を読むのが苦手で、会話のあとは相手からの好意を実際より低く見積もりやすいことがわかっています。サインを増やして推測するより、軽く言葉で確かめたり、誘ってみたりする方が確実です。"),
        ("入力した内容はどこかに送られますか？", "送られません。このページの中（お使いのブラウザ）だけで判定し、SEADICEにも外部にも送信・保存しません。"),
    ]
    how = (f'<li>選んだしぐさを、<a href="/shigusa/hantei/">しぐさ判定の集計</a>と同じ3段階（手がかりになる {cnt["a"]}／状況しだい {cnt["b"]}／当てにならない {cnt["c"]}）で分けて表示します。</li>'
           '<li>「手がかりになる」が2つ以上重なったときだけ、「手がかりが重なっている」と表示します。それでも好意の有無は断定しません。</li>'
           '<li>判定文は、しぐさ・ボディランゲージ索引と同じ、出典照合済みの記事の結論です。点数や「脈あり度◯%」は出しません。</li>')
    ex = [("「近くに座る」「会話のテンポが合う」", "手がかりになるサインが2つ重なっている。それでも、しぐさだけで本音は決まらず、軽く言葉で確かめる段階"),
          ("「よく目が合う」「よく笑ってくれる」", "どちらも状況しだい。これだけでは好意かどうか決められない"),
          ("「返信が速い」", "当てにならない。返信の速さと好意を直接結びつけた決定的な研究はない")]
    verdict = ("if(n.a>=2)m=['研究で傾向が確認された手がかりが'+n.a+'つ重なっています','<p>それでも、しぐさだけで本音は決まりません。サインを探し続けるより、軽く言葉で確かめたり、誘ってみたりする段階です。</p>'];"
               "else if(n.a==1)m=['研究で傾向が確認された手がかりが1つあります','<p>1回ではなく、その人のふだんとの違いと、積み重ねで見ます。ほかの手がかりが重なるかを、しばらく見てください。</p>'];"
               "else if(n.b)m=['選んだサインは、理由が複数ある「状況しだい」のものです','<p>これだけでは、好意かどうかは決められません。好意の手がかりとして研究で傾向が確認されているのは、距離・しぐさの同期・会話のテンポです。</p>'];"
               "else m=['選んだサインは、研究で通説が支持されていないものです','<p>これらは好意の有無を判断する材料になりません。気になるなら、しぐさより言葉で確かめる方が確実です。</p>'];")
    after = ("h+=card('今日からできること','<p>1つのサインで決めない。自分の期待をいったん脇に置く。迷ったら、軽く言葉で確かめる。人は会話のあと、相手からの好意を実際より低く見積もりやすいことも研究でわかっています。</p><p><a href=\"/love-signals-flirting-research/\">脈ありサインは当てになる？スピードデートの研究</a>／<a href=\"/dating-invitation-rejection-anxiety-research/\">デートに誘えないのはなぜか</a></p>');"
             "if(D['love-bombing']&&ids.indexOf('love-bombing')>=0)h+=card('「出会ってすぐの猛烈な好意」を選んだ方へ','<p>強い好意そのものは悪いことではありません。進むスピードと、こちらの境界線がどう扱われるかもあわせて見てください。<a href=\"/redflag-check/\">危険な相手のサイン チェックリスト</a>で確かめられます。</p>');")
    return _gesture_tool(xs, posts, "mk", "myakuari-check", "脈ありチェック", f"脈ありチェック｜そのしぐさは好意のサイン？{len(xs)}種類を研究で判定",
                         f"気になる相手のしぐさ・行動を選ぶと、それぞれが研究で「手がかりになる」「状況しだい」「当てにならない」のどれかを表示します。脈ありサイン{len(xs)}種類。無料・登録不要・入力は送信しません。",
                         "気になる相手について、当てはまるものを選んでください。それぞれのしぐさ・行動が、研究でどこまで好意の手がかりになるのかを表示します。",
                         f"脈ありサイン{len(xs)}種類のうち、研究で傾向が確認された手がかりは{cnt['a']}種類だけです。好意は1つのしぐさでは決まらず、距離・同期・会話のテンポなどの積み重ねで見ます。",
                         how, ex, faq, verdict, after, "相手の気持ちを断定するものではありません。結果は、確かめ方を考えるための手がかりとして使ってください。")


def uso_page(D, posts):
    xs = [x for x in D if "lie" in x.get("tags", [])]
    cnt = {k: sum(1 for x in xs if x["level"] == k) for k in "abc"}
    faq = [
        ("嘘をつく人のしぐさで、当てになるものはありますか？", f"しぐさと本音が研究で調べた嘘のサイン{len(xs)}種類のうち、嘘の手がかりになると言えるものは{cnt['a']}種類でした。{cnt['c']}種類は研究で通説が支持されず、残りは緊張などほかの理由でも起こる「状況しだい」です。"),
        ("人は嘘をどのくらい見抜けますか？", "206本の研究文献をまとめた分析では、人が嘘を見抜ける正解率は平均で約54%でした。コインを投げたときの50%をわずかに上回る程度です。"),
        ("目をそらす・鼻を触るのは嘘のサインですか？", "どちらも「当てにならない」です。研究では通説が支持されていません。目をそらすのは緊張や考えごとでも起こります。"),
        ("嘘かどうか確かめたいときは、どうすればいいですか？", "しぐさより、話の内容を確かめるほうが研究の結果と合っています。時間・場所・人など、あとで確かめられる事実について自然に質問を重ね、責めずに話し合います。"),
        ("入力した内容はどこかに送られますか？", "送られません。このページの中（お使いのブラウザ）だけで判定し、SEADICEにも外部にも送信・保存しません。"),
    ]
    how = (f'<li>選んだしぐさを、<a href="/shigusa/hantei/">しぐさ判定の集計</a>と同じ3段階（手がかりになる {cnt["a"]}／状況しだい {cnt["b"]}／当てにならない {cnt["c"]}）で分けて表示します。</li>'
           '<li>いくつ選んでも、「嘘をついている」とは判定しません。しぐさから嘘を見抜ける正解率は平均で約54%で、判定できる根拠がないためです。</li>'
           '<li>判定文は、しぐさ・ボディランゲージ索引と同じ、出典照合済みの記事の結論です。点数や「嘘の確率◯%」は出しません。</li>')
    ex = [("「目をそらす」「鼻を触る」", "どちらも当てにならない。研究で通説が支持されていない"),
          ("「まばたきが増える」「答えるまでに間がある」", "当てにならない・状況しだいのサイン。緊張でも起こる"),
          ("いくつ選んでも", "「嘘をついている」とは表示せず、話の内容と事実を確かめる方法を表示")]
    verdict = ("if(n.c&&!n.b)m=['選んだサインは、研究で通説が支持されていないものです','<p>これらは嘘の証拠になりません。「嘘をつくと目をそらす」などは広く信じられていますが、研究の結果は支持していません。</p>'];"
               "else if(n.c)m=['選んだサインには、当てにならないものと、緊張でも起こるものが混ざっています','<p>どれも、嘘の証拠とは言えません。緊張・不安・考えごとでも同じしぐさが出ます。</p>'];"
               "else m=['選んだサインは、理由が複数ある「状況しだい」のものです','<p>緊張や負荷がかかると増える動きで、読めるのは「今、緊張しているかもしれない」までです。嘘かどうかは決められません。</p>'];"
               "m[1]+='<p>206本の研究文献をまとめた分析では、人が嘘を見抜ける正解率は平均で約54%でした。コインを投げたときの50%をわずかに上回る程度です。</p>';")
    after = ("h+=card('今日からできること','<p>しぐさだけで決めつけない。気になることは、時間・場所・人など、あとで確かめられる事実について自然に質問を重ねる。疑いが強いときは「嘘をついている」と決めつけず、「不安になっている」と自分の気持ちを伝える。</p><p><a href=\"/body-language-lie-detection-accuracy/\">しぐさで嘘は見抜ける？正解率は約54%</a>／<a href=\"/too-much-detail-lying-research/\">話が細かすぎるのは嘘のサインか</a></p>');")
    return _gesture_tool(xs, posts, "us", "uso-check", "嘘のサインチェック", f"嘘をつく人のしぐさは本当？嘘のサインチェック｜{len(xs)}種類を研究で判定",
                         f"目をそらす、鼻を触る、まばたきが増える。気になったしぐさを選ぶと、それぞれ研究で嘘の手がかりになるのかを表示します。嘘のサイン{len(xs)}種類。無料・登録不要・入力は送信しません。",
                         "相手の様子で気になったしぐさを選んでください。それぞれが、研究でどこまで嘘の手がかりになるのかを表示します。",
                         f"嘘のサインと言われる{len(xs)}種類のうち、嘘の手がかりになると言えるものは{cnt['a']}種類でした。嘘を確かめるには、しぐさより話の内容と事実を照らし合わせる方が確実です。",
                         how, ex, faq, verdict, after, "相手が嘘をついているかどうかを判定するものではありません。結果は、確かめ方を考えるための手がかりとして使ってください。")


# 冷めたサインチェック。(id, グループ, 当てはまること, 記事slug, 段階 a/b/c（""は段階をつけない）, 記事の結論から1〜2文)
SAMETA = [
    ("s1", "sns", "連絡の頻度が減った", "contact-frequency-decline-cooling-signal-research", "b",
     "連絡が減っても冷めたとは限りません。通話記録の研究では、間隔が空いた相手ほど次の通話が長くなる「埋め合わせ」が見られました（恋人に限った研究ではありません）。"),
    ("s2", "sns", "既読から返信までが遅くなった", "line-reply-speed-research", "c",
     "返信の速さと好意を直接結びつけた決定的な研究はありません。遠距離のカップルで満足度と結びついていたのは、速さではなく「きちんと応じてくれている」という感覚でした。"),
    ("s3", "sns", "自分のSNSやストーリーを見てくれなくなった", "story-view-avoidance-interest-concealment-research", "b",
     "見られているかもしれないという意識が、SNSでの振る舞いを慎重にさせることは報告されています。ただストーリーを見ない行動そのものを調べた研究は見当たらず、無関心の証拠とは言えません。"),
    ("s4", "sns", "説明なしに、連絡が完全に途絶えた", "ghosting-psychological-effects-research", "",
     "理由がわからず、自分で結末をつけられないことが、つらさの中心にあります。待つ期限を自分で決め、結末を相手任せにしないことが第一歩です。"),
    ("d1", "date", "デート中の沈黙が増えた", "silence-during-dates-liking-research", "c",
     "沈黙を気まずく感じるのは多くの人に共通する反応です。会話のあと、相手はこちらが思うよりも自分に好意を持っていることが多いとわかっています。"),
    ("d2", "date", "会うとそっけない・避けられている気がする", "pulling-away-liking-ambivalence-research", "b",
     "冷めたとは限りません。対人関係に不安を感じやすい人ほど、同じ相手に「近づきたい」気持ちと「離れたい」気持ちを同時に抱くことが確認されています。"),
    ("d3", "date", "付き合い（結婚）が長くなり、前より満足感が下がった", "marriage-satisfaction-u-curve-myth-research", "b",
     "長期の追跡調査では、満足度は平均して年数とともに下がりますが、推移は夫婦によって大きく異なります。「待てば戻る」とは言えず、個別の要因に目を向ける方が現実的です。"),
    ("k1", "core", "話をしても、わかってもらえた感じがしない", "partner-responsiveness-research", "a",
     "相手に「理解され、大切にされ、認められている」と感じている人ほど、関係の満足感が高いことが確認されています。いつも否定されたり、話をすり替えられたりするなら注意が必要です。"),
    ("k2", "core", "うれしい話をしても、一緒に喜んでくれなくなった", "partner-responsiveness-research", "a",
     "良い出来事を話したとき、相手が熱心に喜んでくれる関係ほど、親密さや毎日の満足感が高い傾向がありました。"),
    ("k3", "core", "「ありがとう」を言わなくなった・言われなくなった", "gratitude-relationship-maintenance-research", "a",
     "カップルを毎日調べた研究では、相手に感謝を感じた翌日、関係のつながりや満足感が高まっていました。感謝を伝えることは、数か月後の関係の質も予測していました。"),
    ("k4", "core", "喧嘩になると、怒鳴る・侮辱する・昔のことを持ち出す", "fight-style-relationship-research", "a",
     "夫婦を16年追った研究では、結婚1年目に夫がこうした行動を多く報告した夫婦ほど、離婚率が高くなっていました。喧嘩の回数より、喧嘩の中で出る行動が手がかりです。"),
    ("k5", "core", "喧嘩中に黙り込む・話し合いから去る", "stonewalling-conflict-withdrawal-warning-sign", "b",
     "心拍数が上がりすぎて頭が働かなくなっている可能性があります。1回で決めず、よくあるパターンか、話し合いに戻れるかを見ます。"),
    ("m1", "self", "既読や返信が気になって、何度も確認してしまう", "reply-anxiety-attachment-jealousy-research", "",
     "不安を感じやすい傾向の人は、連絡の間が空くこと自体を「見捨てられるサイン」と感じやすいとされています。相手の気持ちのサインというより、自分の側の反応として理解すると対処しやすくなります。"),
    ("m2", "self", "言わなくても察してほしいのに、わかってくれない", "mind-reading-expectation-mismatch-research", "",
     "「察して当然」という期待が強い人ほど、わかってもらえなかったとき「愛情がないから」と結びつけやすいことがわかっています。察してもらうより先に、言葉で伝えることから始めます。"),
]
SAMETA_GROUPS = [("sns", "連絡・SNSの変化"), ("date", "会っているとき・付き合いの長さ"), ("core", "話したとき・喧嘩のときの様子"), ("self", "自分の気持ち")]


def sameta_page(posts):
    for _, _, _, s, _, _ in SAMETA:
        assert s in posts, s
    boxes = ""
    for g, gl in SAMETA_GROUPS:
        boxes += f"<h2>{E(gl)}</h2>" + "".join(f'<label><input type="checkbox" name="sm" value="{i}">{E(t)}</label>' for i, gg, t, _, _, _ in SAMETA if gg == g)
    data = {i: {"g": g, "t": t, "s": s, "l": l, "n": n, "title": posts[s]["title"]} for i, g, t, s, l, n in SAMETA}
    cnt = {k: sum(1 for x in SAMETA if x[4] == k) for k in "abc"}
    faq = [
        ("連絡の頻度が減ったら、冷めたサインですか？", "単独のサインとしては弱いです。通話記録の研究では、連絡の間隔が空いた相手ほど次の通話が長くなる「埋め合わせ」の傾向も確認されています（恋人同士に限った分析ではありません）。頻度だけで判断せず、会話の中身もあわせて見ます。"),
        ("相手の気持ちが冷めたかどうかは、何を見ればわかりますか？", "研究で関係の満足感や別れのリスクと結びついていたのは、連絡の量や返信の速さより、話をしたときにわかってもらえると感じるか、感謝を伝え合っているか、喧嘩で怒鳴る・侮辱するなどの行動が出るかでした。それでも、相手の気持ちは言葉で確かめる方が確実です。"),
        ("付き合いが長くなれば、満足感が下がるのは自然ですか？待てば戻りますか？", "同じ夫婦を17年追った調査では、満足度は平均して年数とともに下がりましたが、推移は夫婦によって大きく異なりました。後半に自然と上向くという証拠は得られておらず、「待てば戻る」とは言えません。"),
        ("入力した内容はどこかに送られますか？", "送られません。このページの中（お使いのブラウザ）だけで判定し、SEADICEにも外部にも送信・保存しません。"),
    ]
    desc = "連絡が減った、返信が遅い、デートで沈黙が増えた。恋人や好きな人の変化を選ぶと、それぞれ研究で「冷めた」の手がかりになるのかと、今日からできることを表示します。14項目。無料・登録不要・入力は送信しません。"
    how = (f'<li>相手の変化を、しぐさ判定と同じ3段階（手がかりになる {cnt["a"]}／状況しだい {cnt["b"]}／当てにならない {cnt["c"]}）で分けて表示します。「手がかりになる」は、研究で関係の満足感や別れのリスクと結びついていたものです。</li>'
           '<li>連絡が途絶えた・自分の気持ちの項目は段階をつけず、記事の結論と、今日からできることを表示します。</li>'
           '<li>いくつ選んでも「冷めている」とは判定しません。点数や「冷め度◯%」も出しません。判定文は、出典照合済みの記事の結論だけです。</li>')
    ex = [("「連絡の頻度が減った」「返信が遅くなった」", "状況しだい・当てにならないサイン。これだけでは冷めたとは言えない"),
          ("「わかってもらえた感じがしない」「ありがとうを言わなくなった」", "関係の満足感と結びつく手がかりが2つ。冷めたと決めつける前に、自分の気持ちを言葉で伝える段階"),
          ("「喧嘩で怒鳴る・侮辱する」", "別れのリスクと結びつく手がかり。続くときは危険な相手のサイン チェックリストと相談先も表示"),
          ("「説明なしに連絡が途絶えた」", "待つ期限を自分で決め、結末を相手任せにしないこと")]
    arts = []
    for _, _, _, s, _, _ in SAMETA:
        if s not in arts:
            arts.append(s)
    body = (f'<script type="application/ld+json">{_ld("冷めたサインチェック", URL + "sameta-check/", desc, faq)}</script>'
            '<p>恋人や好きな人について、最近の変化で当てはまるものを選んでください。それぞれが研究でどこまで「冷めた」の手がかりになるのかと、今日からできることを表示します。入力はこのページの中だけで判定し、どこにも送りません。</p>'
            f'<form class="tl-box" id="sm" onsubmit="return false">{boxes}<button type="button" class="tl-btn" id="sm-go">結果を見る</button></form>'
            '<div class="tl-res" id="sm-res" aria-live="polite" hidden></div>'
            '<p class="answer">連絡が減った・返信が遅いは、それだけでは冷めたサインとは言えません。研究で関係の満足感や別れのリスクと結びついていたのは、話をわかってもらえるか、感謝を伝え合うか、喧嘩のしかたでした。</p>'
            f'<h2>判定のしかた</h2><ul>{how}</ul>'
            '<h2>入力例と結果</h2><div class="tl-tw"><table><thead><tr><th scope="col">選んだもの</th><th scope="col">表示される内容</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in ex) + '</tbody></table></div>'
            '<h2>判定のもとにした記事</h2><p>それぞれ、論文などの出典と照合した記事です。</p><ul>'
            + "".join(f'<li><a href="/{s}/">{E(posts[s]["title"])}</a></li>' for s in arts) + '</ul>'
            f'<h2>よくある質問</h2>{_faq(faq)}'
            '<p class="note">相手の気持ちを断定するものではありません。結果は、確かめ方や伝え方を考えるための手がかりとして使ってください。</p>'
            "<script>(function(){var D=" + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";var LV={a:'手がかりになる',b:'状況しだい',c:'当てにならない'};"
            "function e(s){return String(s).replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
            "function card(t,b,a){return '<div class=\"tl-card'+(a?' alert':'')+'\"><h3>'+t+'</h3>'+b+'</div>'}"
            "function items(ids){return ids.map(function(i){var x=D[i];return '<div class=\"tl-item\"><b>'+(x.l?'<span class=\"lv lv-'+x.l+'\">'+LV[x.l]+'</span>':'')+e(x.t)+'</b>'+e(x.n)+'<br><a href=\"/'+x.s+'/\">記事を読む：'+e(x.title)+'</a></div>'}).join('')}"
            "document.getElementById('sm-go').onclick=function(){var ids=[].slice.call(document.querySelectorAll('#sm input:checked')).map(function(x){return x.value});"
            "var A=ids.filter(function(i){return D[i].l=='a'}),B=ids.filter(function(i){return D[i].l=='b'||D[i].l=='c'}).sort(function(x,y){return D[x].l<D[y].l?-1:1}),S=ids.filter(function(i){return D[i].g=='self'}),h='';"
            "if(ids.indexOf('s4')>=0)h+=card('連絡が途絶えたとき','<p>相手の沈黙を、自分の価値の答えにしないでください。「1週間返事がなければ区切りにする」など、待つ期限を自分で決めます。送るなら、責めずに1通だけにします。</p>'+items(['s4']));"
            "if(ids.indexOf('k4')>=0)h+=card('怒鳴る・侮辱するが続くときは','<p>話すたびに否定される、怒鳴られる、見下されるなどが続くなら、冷めたかどうかの問題を超えています。<a href=\"/redflag-check/\">危険な相手のサイン チェックリスト</a>で確かめられます。身の安全に不安があるときは、DV相談ナビ（<a href=\"tel:%238008\">#8008</a>）に相談できます。</p>',1);"
            "if(A.length)h+=card('関係の中身に関わる手がかりが'+A.length+'つあります','<p>研究で関係の満足感や別れのリスクと結びついていたのは、連絡の量や返信の速さより、話をわかってもらえるか、感謝を伝え合うか、喧嘩のしかたでした。冷めたと決めつける前に、「私は〇〇と感じた」と自分の気持ちを言葉で伝えてみてください。</p>'+items(A));"
            "if(B.length)h+=card('よく言われる「冷めたサイン」が'+B.length+'つあります','<p>これだけでは、冷めたとは言えません。連絡の量や会ったときの様子は、忙しさ・緊張・不安など、気持ち以外の理由でも変わります。</p>'+items(B));"
            "if(S.length)h+=card('あなた自身の不安も関わっているかもしれません','<p>不安になるのは、性格の弱さではありません。相手の変化を読み解こうとするより、自分が何に不安を感じているかを言葉にする方が、すれ違いを減らせます。</p>'+items(S));"
            "if(!ids.length)h=card('選ばれた項目はありません','<p>当てはまるものを1つ以上選んでください。</p>');"
            "else h+=card('今日からできること','<p>1つの変化で決めない。うれしい話をして、相手の反応を見る。してもらった小さなことに、具体的に「ありがとう」と伝える。気になることは、責めずに「私は〇〇と感じた」と言葉で伝える。</p><p><a href=\"/partner-responsiveness-research/\">「わかってくれる人」と長続きするのはなぜか</a>／<a href=\"/fight-style-relationship-research/\">関係が続くかを分ける「喧嘩の型」</a></p>');"
            "var r=document.getElementById('sm-res');r.innerHTML=h;r.hidden=false;r.scrollIntoView({behavior:'smooth',block:'start'})};})();</script>")
    return {"path": "sameta-check", "title": "冷めたサインチェック", "date": "2026-10-08",
            "desc": "連絡が減った・返信が遅い・沈黙が増えた。恋人や好きな人の変化を選ぶと、研究で「冷めた」の手がかりになるのかと今日からできることを表示。入力は送信しません。",
            "seo_title": "冷めたサインチェック｜連絡が減った・返信が遅いは本当に冷めた？研究で判定", "body": body, "css": CSS}


def nikki_page(posts):
    """ふたりの日記の説明ページ（/nikki/、検索の入口）。日記の本体は /memo/（umbra_memo.py、noindex・タブ名「メモ」）。"""
    faq = [
        ("恋人とのことを記録しておくと、何の役に立ちますか？", "束縛や見下す言動は、1回だけだと「気のせいかも」と思いやすいものです。日付つきで残すと、同じことが繰り返されているかを自分の目で確かめられます。相談窓口で状況を説明するときの手がかりにもなります。"),
        ("記録した内容はどこに保存されますか？", "お使いの端末のブラウザの中だけです。SEADICEにも外部にも送信しません。そのかわり、別の端末やブラウザとは共有されず、ブラウザのデータを消すと記録も消えます。"),
        ("相手に見られないか心配です。", "日記のページ名は「メモ」と表示され、右上の「閉じる」を押すと天気の検索ページに切り替わります。それでも、相手と同じ端末やブラウザを使っていると見られることがあります。心配なときは、使い終わったら「すべての記録を消す」を押してください。"),
        ("つらいことがない日も書いていいですか？", "はい。よかった日・ふつうの日も1タップで残せます。ふだんの日記として使うほうが続けやすく、気分の変化も見えやすくなります。"),
    ]
    desc = "恋人・パートナーとの毎日を、気分の1タップと短い言葉のボタンで残す日記。同じことが30日に3回あると、研究でわかっていることをそっと知らせます。無料・登録不要・記録は端末の中だけ。"
    ex = [("「よかった」＋「話を聞いてくれた」", "その日の点が緑色で残る"),
          ("30日で「バカにされた」を3回記録", "「この30日で3回ありました」と、記事の結論と詳しい記事へのリンクを表示"),
          ("「叩かれた・物に当たられた」を記録", "安全を最優先にする一言と、110番・DV相談ナビ #8008 などの相談先を表示")]
    body = (f'<script type="application/ld+json">{_ld("ふたりの日記", URL + "nikki/", desc, faq)}</script>'
            '<p>恋人・パートナーとの毎日を、気分の1タップと短い言葉のボタンで残す日記です。最近2週間の気分を色で見返せて、同じことが繰り返されていたら、研究でわかっていることをそっと知らせます。</p>'
            '<p style="margin:22px 0"><a href="/memo/" class="tl-btn" style="text-align:center;text-decoration:none;color:var(--bg)">日記をはじめる</a></p>'
            '<p class="answer">嫌なことは、1回だけだと気のせいに思えます。日付つきで残せば、繰り返しに気づけます。記録は端末の中だけに保存し、どこにも送りません。</p>'
            '<h2>使い方</h2><ol style="padding-left:1.4em">'
            '<li>「今日はどんな日だった？」で、よかった／ふつう／もやもや／つらかった を1つ選ぶ</li>'
            '<li>あてはまることがあれば、「話を聞いてくれた」「バカにされた」などの短い言葉のボタンを選ぶ</li>'
            '<li>ひとことメモ（なくてもOK）を書いて「残す」</li></ol>'
            '<h2>見られにくくする工夫</h2><ul>'
            '<li>日記のページ名は「メモ」と表示されます。</li>'
            '<li>右上の「閉じる」を押すと、天気の検索ページに切り替わります。</li>'
            '<li>記録はこの端末のブラウザの中だけに保存され、SEADICEにも外部にも送られません。いつでも全部消せます。</li>'
            '<li>相手と同じ端末やブラウザを使っているときは、見られることがあります。</li></ul>'
            '<h2>知らせる内容と、その根拠</h2>'
            '<p>「気になること」のボタンは、<a href="/redflag-check/">危険な相手のサイン チェックリスト</a>と同じ項目です。同じことが30日に3回以上あったときだけ、出典照合済みの記事の結論を表示します。暴力や脅しを記録したときは、回数に関係なく相談先を表示します。</p>'
            '<h2>入力例と表示</h2><div class="tl-tw"><table><thead><tr><th scope="col">記録したこと</th><th scope="col">表示される内容</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in ex) + '</tbody></table></div>'
            f'<h2>相談先</h2>{CONTACTS}'
            f'<h2>よくある質問</h2>{_faq(faq)}'
            '<p class="note">相手を診断したり、ラベルを貼ったりするためのものではありません。心身の不調や被害が深刻なときは、専門機関に相談してください。</p>')
    return {"path": "nikki", "title": "ふたりの日記", "date": "2026-10-08", "desc": desc[:120],
            "seo_title": "ふたりの日記｜恋人との毎日を1タップで記録（束縛・モラハラの記録にも）", "body": body, "css": CSS}


# 恋愛・結婚の通説の判定（/renai-tsusetsu/）。「SEADICE調べ」の一次情報。数字は毎回このリストから数える。
# (通説, 段階 a=研究でおおむね支持 / b=条件しだい / c=研究では支持されない, 記事の結論から1〜2文, 記事slug)
TSUSETSU = [
    ("話をわかってくれる相手とは長続きする", "a", "相手に「理解され、大切にされ、認められている」と感じている人ほど、関係の満足感が高く、10年後の体のストレス反応も健康的でした。", "partner-responsiveness-research"),
    ("「ありがとう」を伝え合う関係は長続きする", "a", "相手に感謝を感じた翌日は関係の満足感が高まり、感謝を伝えることは数か月後の関係の質も予測していました。", "gratitude-relationship-maintenance-research"),
    ("笑いのツボが合う相手とはうまくいく", "a", "ジョークの多さではなく、二人で笑いのセンスを共有しているかが満足度と結びついていました。相手を見下すユーモアは満足度を下げます。", "humor-style-compatibility-research"),
    ("一度浮気した人は、また浮気する", "a", "484人を2つの交際にわたって追った研究では、最初の交際で浮気をした人が次の交際でも浮気をする割合は、しなかった人の約3倍でした。", "serial-infidelity-repeat-research"),
    ("「好き避け」は本当にある", "a", "「好き避け」は学術用語ではありませんが、不安を感じやすい人が同じ相手に「近づきたい」と「離れたい」を同時に抱くことは、6つの研究で確認されています。", "pulling-away-liking-ambivalence-research"),
    ("似た者同士はうまくいく", "b", "「似ている」と感じることは魅力を予測しますが、交際・結婚しているカップルでは、似ていることと満足度の関連は一貫していませんでした。", "similarity-attraction-compatibility-research"),
    ("会話のテンポが合う相手とは相性がいい", "b", "会話や動きの同期が高いペアほど、その場での好意は高い傾向がありました。ただし長い目で見た相性まで判断できるとは限りません。", "conversation-synchrony-compatibility-research"),
    ("年の差婚はうまくいかない", "b", "年の差そのものが失敗を決めるわけではありません。満足度の差は6〜10年で消えていきましたが、収入の悪化などつらい出来事には弱い傾向がありました。", "age-gap-marriage-satisfaction-research"),
    ("結婚前に同棲すると離婚しやすい", "b", "婚約前に同棲を始めた夫婦では満足度が低い傾向がありましたが、近年の世代では同棲の有無と離婚のしやすさの関連はほとんど見られません。", "premarital-cohabitation-divorce-risk-research"),
    ("喧嘩が多いカップルは別れる", "b", "別れのリスクと関わっていたのは喧嘩の回数ではなく、怒鳴る・侮辱する・話し合いから去るといった、喧嘩の中で出る行動でした。", "fight-style-relationship-research"),
    ("喧嘩中に黙り込む相手とはうまくいかない", "b", "黙り込みは離婚を予測する行動の一つとして報告されていますが、2025年の追試では「軽蔑」の方が影響が大きいという結果でした。繰り返すかどうかで見ます。", "stonewalling-conflict-withdrawal-warning-sign"),
    ("男性は体の浮気、女性は心の浮気が許せない", "b", "2択で聞くと男女差が出ますが、2択以外の聞き方では差が消え、男女とも体の浮気の方をよりつらいと答えた研究もあります。", "infidelity-jealousy-gender-difference-research"),
    ("男性は見た目、女性は経済力で相手を選ぶ", "b", "45カ国のアンケートではその傾向が確認されましたが、実際にスピードデートで出会った相手を好きになるかどうかでは、男女差はほとんど見られませんでした。", "mate-preference-gender-difference-research"),
    ("からかってくるのは好意の裏返し", "b", "からかいは親しみにも敵意にもなります。分かれ目は、言い返し合える対等さと、嫌がったらやめるかどうかです。", "teasing-affection-or-hostility-research"),
    ("失恋の痛みは女性の方が大きく、男性は引きずる", "b", "別れ直後の痛みは女性の方が大きいことが国際調査で確認されました。ただし「男性は引きずる」という回復の違いは、調査では測定されていません。", "breakup-recovery-gender-difference-research"),
    ("失恋は3か月で立ち直れる", "b", "別れ直後の落ち込みは多くの場合3か月ほどで元に戻りましたが、これは平均です。別れ方や支えてくれる人の有無で、回復の速さは変わります。", "breakup-recovery-time-research"),
    ("元恋人とは友達に戻れる", "b", "友達でいる理由が「安心」なら問題は少なく、「未練」が理由の友情は悪い結果につながっていました。", "staying-friends-with-ex-research"),
    ("「運命の人」を信じるとうまくいく", "c", "対立があっても関係への気持ちが冷めにくかったのは、関係は努力で育つと考える人でした。「相性がすべて」と考える人は、意見の違いが大きいと関係の質が下がりやすい傾向がありました。", "destiny-belief-relationship-satisfaction-research"),
    ("相性診断で結婚がうまくいくかわかる", "c", "結婚後に満足度が上がるか下がるかは、アンケートの回答ではほとんど予測できませんでした。関係の質を予測したのは、相手のコミットメントや感謝、喧嘩の少なさなど関係の中身です。", "marriage-compatibility-research"),
    ("結婚満足度はU字を描き、子育てが終われば戻る", "c", "同じ夫婦を17年追った調査では、満足度は平均して下がり続け、後半に上向く証拠は得られませんでした。U字は調べ方が生んだ見え方でした。", "marriage-satisfaction-u-curve-myth-research"),
    ("遠距離恋愛はうまくいかない", "c", "大学生2075人の調査では、遠距離かどうかで、幸福感・コミットメント・対立の頻度に差は見られませんでした。", "long-distance-relationship-satisfaction-research"),
    ("手に入りにくい相手ほど魅力的に見える", "c", "単に手に入りにくいだけの相手は好かれず、「自分にだけ気がある」相手が最も好かれました。駆け引きは「好き」という気持ちをむしろ下げることがあります。", "hard-to-get-scarcity-attraction-research"),
    ("別れと復縁を繰り返すのは絆が強いから", "c", "別れと復縁を繰り返す関係は、安定した関係と比べて身体的な暴力の報告がおよそ2倍、言葉の暴力もおよそ1.5倍でした。", "on-again-off-again-reconciliation-research"),
    ("マッチングアプリのプロフィールは嘘ばかり", "c", "身長・体重・年齢のずれは多くの人に見られましたが、ずれは小さく、メッセージで嘘をついたと答えたのは約7%でした。", "online-dating-profile-deception-research"),
    ("察してくれないのは愛情がないから", "c", "「察して当然」という期待が強い人ほど、誤解を「愛情がないから」と結びつけやすく、自分と相手の両方の満足度を下げていました。", "mind-reading-expectation-mismatch-research"),
]
TS_LV = {"a": "研究でおおむね支持", "b": "条件しだい", "c": "研究では支持されない"}
TS_CSS = (".hk-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:20px 0 8px}.hk-stats div{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:14px 10px;text-align:center}"
          ".hk-stats b{display:block;font-size:34px;line-height:1.1;color:var(--accent)}.hk-stats small{font-size:15px;color:var(--muted)}.hk-stats span{display:block;font-size:12px;color:var(--text);margin-top:6px}"
          ".hk-find li{margin:10px 0}.ts-item{padding:14px 0;border-top:1px solid var(--border);font-size:15px;line-height:1.8}.ts-item b{display:block;font-size:16px;margin-bottom:4px}.ts-item a{color:var(--link);font-size:14px}")


def tsusetsu_page(posts):
    for _, _, _, s in TSUSETSU:
        assert s in posts, s
    N = len(TSUSETSU)
    c = {k: sum(1 for x in TSUSETSU if x[1] == k) for k in "abc"}

    def pct(n):
        return round(n * 100 / N)

    def items(k):
        return "".join(f'<div class="ts-item"><b><span class="lv lv-{k}">{TS_LV[k]}</span>{E(m)}</b>{E(n)}<br><a href="/{s}/">記事を読む：{E(posts[s]["title"])}</a></div>'
                       for m, kk, n, s in TSUSETSU if kk == k)
    c_names = "「" + "」「".join(m for m, kk, _, _ in TSUSETSU if kk == "c") + "」"
    faq = [
        ("恋愛・結婚の通説は、どのくらい研究で支持されていますか？", f"しぐさと本音が研究で調べた恋愛・結婚の通説{N}個のうち、研究でおおむね支持されたのは{c['a']}個（{pct(c['a'])}%）でした。{c['b']}個は条件しだい、{c['c']}個は研究では支持されませんでした。"),
        ("研究で支持されなかった恋愛の通説は何ですか？", f"{c_names}の{c['c']}個です。"),
        ("長続きする関係について、研究で支持されたことは何ですか？", "話をわかってもらえると感じること、「ありがとう」を伝え合うこと、二人で笑いのセンスを共有していることが、関係の満足感と結びついていました。いずれも出会ったときの条件ではなく、付き合いの中で育てるものです。"),
        ("この判定は、誰がどうやって行いましたか？", "SEADICEが運営するしぐさと本音の編集部が、論文などの出典と照合した記事の結論をもとに、3段階で整理しました。新しい研究が出たら見直します。"),
    ]
    desc = f"運命の人、年の差婚、同棲、遠距離、浮気は繰り返すのか。恋愛・結婚の通説{N}個を論文で判定すると、研究でおおむね支持されたのは{c['a']}個、支持されなかったのは{c['c']}個でした。SEADICE調べ。"
    ld = json.dumps({"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "name": "恋愛・結婚の通説を研究で判定した結果", "url": URL + "renai-tsusetsu/", "description": desc, "publisher": PUB},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}]},
        ensure_ascii=False).replace("</", "<\\/")
    body = (f'<script type="application/ld+json">{ld}</script>'
            f'<p class="plead">よく言われる恋愛・結婚の通説{N}個を、論文と照らし合わせて3段階で判定しました。研究でおおむね支持されたのは{c["a"]}個だけで、{c["c"]}個は研究では支持されないという結果です。</p>'
            '<div class="hk-stats">' + "".join(f'<div><b>{c[k]}<small>/{N}</small></b><span>{TS_LV[k]}（{pct(c[k])}%）</span></div>' for k in "abc") + '</div>'
            '<p class="note">しぐさと本音（SEADICE）調べ。判定に使った記事はすべて、論文などの出典と照合しています。</p>'
            '<h2>わかったこと</h2><ul class="hk-find">'
            '<li><strong>長続きと結びつくのは、出会いの条件より付き合いの中身。</strong>話をわかってもらえる、感謝を伝え合う、笑いを共有する。どれも二人で育てられるものでした。</li>'
            '<li><strong>「条件で決まる」系の通説は当てにならない。</strong>運命の人、相性診断、遠距離は、それだけで関係の行方を決めませんでした。年の差や同棲も「条件しだい」でした。</li>'
            '<li><strong>喧嘩は回数より中身。</strong>別れのリスクと関わっていたのは、怒鳴る・侮辱する・話し合いから去るといった行動でした。</li>'
            '<li><strong>男女差の通説は、聞き方しだいで小さくなるものが多い。</strong>浮気の許せなさや相手に求める条件の男女差は、アンケートの形式や実際の出会いの場面では小さくなりました。</li></ul>'
            f'<h2>研究でおおむね支持された{c["a"]}個</h2><p>傾向が研究で確認されているものです。それでも、一人ひとりの関係に必ず当てはまるわけではありません。</p>{items("a")}'
            f'<h2>条件しだいの{c["b"]}個</h2><p>一部の条件や聞き方でだけ当てはまる、または通説より結論が細かいものです。</p>{items("b")}'
            f'<h2>研究では支持されない{c["c"]}個</h2><p>よく言われるのに、研究の結果が支持していない通説です。</p>{items("c")}'
            '<h2>判定の方法と限界</h2><ul>'
            f'<li>対象は、しぐさと本音で記事にした恋愛・結婚の通説{N}個です（{len({x[3] for x in TSUSETSU})}本の記事）。世の中の通説をすべて網羅したものではありません。脈ありサインなどのしぐさは<a href="/shigusa/hantei/">しぐさ判定の集計</a>で別に判定しています。</li>'
            '<li>「研究でおおむね支持」は追跡調査やメタ分析などで傾向が確認されているもの、「条件しだい」は一部の条件や聞き方でだけ当てはまるもの、「研究では支持されない」は研究の結果が通説を支持していないものです。</li>'
            '<li>判定は記事の出典（論文・メタ分析など）をもとにした編集部の整理です。新しい研究が出たら見直します。</li>'
            '<li>特定の人や関係を診断するためのものではありません。暴力や束縛があるときは、通説より先に<a href="/redflag-check/">危険な相手のサイン チェックリスト</a>で確かめ、相談先を頼ってください。</li></ul>'
            f'<h2>よくある質問</h2>{_faq(faq)}')
    return {"path": "renai-tsusetsu", "title": "恋愛・結婚の通説を研究で判定した結果", "date": "2026-10-08",
            "desc": f"運命の人・年の差・同棲・遠距離・浮気は繰り返す？恋愛・結婚の通説{N}個を論文で判定。研究で支持されたのは{c['a']}個、支持されないのは{c['c']}個。SEADICE調べ。",
            "seo_title": f"恋愛・結婚の通説{N}個を研究で判定｜運命の人・年の差・同棲・遠距離は本当？【SEADICE調べ】", "body": body, "css": CSS + TS_CSS}

# 本当？ウソ？クイズ（/quiz/）。しぐさ索引の判定と TSUSETSU から自動で問題を作る（判定や記事が増えると問題も増える）。
# 答えは3択（本当=a / 条件しだい=b / ウソ=c）。1回10問を a2・b4・c4 で混ぜる（「条件しだい」ばかりにならないように）。
QZ_LABEL = {"a": "本当", "b": "条件しだい", "c": "ウソ"}
QZ_CSS = ("#qz{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:22px 18px;margin:18px 0 8px}"
          ".qz-n{font-size:13px;color:var(--muted)}.qz-k{display:inline-block;font-size:12px;font-weight:700;color:var(--accent);margin-top:12px}"
          ".qz-q{font-size:20px;font-weight:800;line-height:1.6;margin:4px 0 4px}.qz-b{font-size:15px;color:var(--muted);margin-bottom:14px}"
          ".qz-c{display:grid;gap:10px}.qz-c button{font:inherit;font-size:17px;font-weight:700;padding:15px 14px;border-radius:14px;border:1px solid var(--border);background:rgba(255,255,255,.04);color:var(--text);cursor:pointer;text-align:center}"
          ".qz-c button:hover:not(:disabled){border-color:var(--accent)}.qz-c button.right{background:#3FB98A;color:#0F0B16;border-color:#3FB98A}.qz-c button.wrong{background:#5C5470;color:#ECE7F2}"
          ".qz-r{margin-top:14px}.qz-r .res{font-size:17px;font-weight:800}.qz-r p{font-size:15px;line-height:1.8;margin:6px 0}.qz-r a{color:var(--link)}"
          ".qz-go{display:block;width:100%;margin-top:14px;padding:14px;border:0;border-radius:12px;background:var(--accent);color:var(--bg);font:inherit;font-size:16px;font-weight:800;cursor:pointer}"
          ".qz-go.sub{background:none;color:var(--link);border:1px solid var(--border)}#qz .qz-score{font-size:32px;font-weight:900;line-height:1.3;margin:6px 0}#qz .qz-q{font-size:21px;font-weight:800;line-height:1.6}#qz .qz-msg{font-size:13px;color:var(--muted);margin-top:10px}")


def quiz_page(D, posts):
    qs = []
    for x in D:
        qs.append({"k": "しぐさ", "q": x["gesture"], "b": "よく言われる意味：" + x["belief"], "a": x["level"], "e": x["text"], "s": x["slug"], "t": posts[x["slug"]]["title"]})
    for m, lv, n, s in TSUSETSU:
        qs.append({"k": "恋愛・結婚の通説", "q": m, "b": "", "a": lv, "e": n, "s": s, "t": posts[s]["title"]})
    N = len(qs)
    c = {k: sum(1 for x in qs if x["a"] == k) for k in "abc"}
    faq = [
        ("このクイズの答えは、どうやって決めていますか？", f"しぐさと本音が論文などの出典と照合した記事の結論をもとに、「本当（研究で傾向が確認されている）」「条件しだい」「ウソ（研究では支持されない）」の3段階で判定したものです。全{N}問のうち、本当は{c['a']}問、条件しだいは{c['b']}問、ウソは{c['c']}問です。"),
        ("「嘘をつくと目をそらす」は本当ですか？", "研究では支持されていません。目をそらすのは緊張や考えごとでも起こり、嘘の手がかりにはなりません。人が嘘を見抜ける正解率は平均で約54%でした。"),
        ("恋愛の通説で、研究で支持されているものはありますか？", "話をわかってもらえると感じる相手と長続きする、「ありがとう」を伝え合う関係は長続きする、などは研究で傾向が確認されています。一方、「運命の人を信じるとうまくいく」「遠距離恋愛はうまくいかない」は支持されていません。"),
        ("結果は保存・送信されますか？", "されません。クイズはこのページの中だけで動き、答えも点数もSEADICEに送りません。「結果を共有」を押したときだけ、点数とこのページのURLを、あなたが選んだアプリに渡します。"),
    ]
    desc = f"「嘘をつくと目をそらす」「遠距離恋愛はうまくいかない」は本当？しぐさと恋愛の通説{N}問を、論文で確かめた答えで出題する3択クイズ。1回10問、解説と出典つき。無料・登録不要。"
    ex = [("「わざと目を合わせ続ける」は「正直で信頼できる」サイン？", "ウソ。研究では、嘘をついている人の方が長く目を合わせていた"),
          ("「しぐさや姿勢が似てくる」のは好意のサイン？", "本当。研究で傾向が確認されている手がかり"),
          ("「結婚前に同棲すると離婚しやすい」", "条件しだい。婚約前の同棲では傾向があったが、近年の世代ではほとんど見られない")]
    body = (f'<script type="application/ld+json">{_ld("本当？ウソ？恋愛としぐさの通説クイズ", URL + "quiz/", desc, faq)}</script>'
            f'<p>よく言われるしぐさの意味や恋愛の通説は、研究で確かめると本当なのか。全{N}問から10問を出題します。答えは「本当・条件しだい・ウソ」の3つから選ぶだけです。</p>'
            '<div id="qz" aria-live="polite"><noscript><p>クイズを遊ぶにはJavaScriptを有効にしてください。下の「出題例」で答えの一部を読めます。</p></noscript></div>'
            f'<p class="answer">しぐさと恋愛の通説{N}個のうち、研究で「本当」と言えたのは{c["a"]}個だけでした。{c["c"]}個は研究では支持されず、残りは条件しだいです。</p>'
            '<h2>答えの決め方</h2><ul>'
            f'<li>答えは、<a href="/shigusa/hantei/">しぐさ判定の集計</a>と<a href="/renai-tsusetsu/">恋愛・結婚の通説の判定</a>と同じ3段階です。どれも、論文などの出典と照合した記事の結論にもとづいています。</li>'
            '<li>「本当」は研究で傾向が確認されているもの、「条件しだい」は場面や聞き方で結果が変わるもの、「ウソ」は研究で通説が支持されていないものです。</li>'
            '<li>1回10問は、「本当」2問・「条件しだい」4問・「ウソ」4問の組み合わせで、毎回ちがう問題が出ます。</li></ul>'
            '<h2>出題例</h2><div class="tl-tw"><table><thead><tr><th scope="col">問題</th><th scope="col">答え</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{E(a)}</td><td>{E(b)}</td></tr>" for a, b in ex) + '</tbody></table></div>'
            f'<h2>よくある質問</h2>{_faq(faq)}'
            '<p class="note">クイズは、通説と研究のズレを知るためのものです。特定の人の気持ちや関係を判定するものではありません。</p>'
            "<script>(function(){var Q=" + json.dumps(qs, ensure_ascii=False).replace("</", "<\\/") + ",L={a:'本当',b:'条件しだい',c:'ウソ'},box=document.getElementById('qz'),order,i,score;"
            "function esc(s){return String(s).replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
            "function sh(a){a=a.slice();for(var j=a.length-1;j>0;j--){var k=Math.floor(Math.random()*(j+1)),t=a[j];a[j]=a[k];a[k]=t}return a}"
            "function pick(k,n){return sh(Q.filter(function(x){return x.a==k})).slice(0,n)}"
            "function start(){order=sh(pick('a',2).concat(pick('b',4),pick('c',4)));i=0;score=0;show()}"
            "function show(){if(i>=order.length)return end();var x=order[i];"
            "box.innerHTML='<p class=\"qz-n\">第'+(i+1)+'問 / 全'+order.length+'問</p><span class=\"qz-k\">'+esc(x.k)+'</span><p class=\"qz-q\">「'+esc(x.q)+'」</p>'+(x.b?'<p class=\"qz-b\">'+esc(x.b)+'</p>':'<p class=\"qz-b\">研究で確かめると？</p>')+'<div class=\"qz-c\">'+['a','b','c'].map(function(k){return '<button type=\"button\" data-k=\"'+k+'\">'+L[k]+'</button>'}).join('')+'</div><div class=\"qz-r\"></div>';"
            "[].forEach.call(box.querySelectorAll('.qz-c button'),function(b){b.onclick=function(){var ok=b.dataset.k==x.a;if(ok)score++;"
            "[].forEach.call(box.querySelectorAll('.qz-c button'),function(e){e.disabled=true;if(e.dataset.k==x.a){e.classList.add('right');e.textContent='答え：'+L[x.a]}else if(e===b)e.classList.add('wrong')});"
            "box.querySelector('.qz-r').innerHTML='<p class=\"res\">'+(ok?'正解です':'不正解です')+'</p><p>'+esc(x.e)+'</p><p><a href=\"/'+x.s+'/\">記事を読む：'+esc(x.t)+'</a></p><button type=\"button\" class=\"qz-go\">'+(i+1<order.length?'次の問題へ':'結果を見る')+'</button>';"
            "var n=box.querySelector('.qz-go');n.onclick=function(){i++;show();box.scrollIntoView({block:'start'})};n.focus()}})}"
            "function end(){var m=score>=8?'通説と研究のズレを、よく見抜いています。':score>=5?'通説と研究のズレに、気づき始めています。':'よく言われる通説には、研究では支持されないものが多いのです。';"
            "var txt='本当？ウソ？恋愛としぐさの通説クイズ 10問中'+score+'問正解でした';"
            "box.innerHTML='<p class=\"qz-n\">結果</p><p class=\"qz-score\">10問中 '+score+'問 正解</p><p>'+m+'</p><button type=\"button\" class=\"qz-go\" id=\"qz-sh\">結果を共有</button><button type=\"button\" class=\"qz-go sub\" id=\"qz-again\">別の10問に挑戦する</button>'"
            "+'<p class=\"qz-msg\">共有するのは点数とこのページのURLだけです。もっと難しい問題は、<a href=\"/shigusa/#quiz\">研究の4択クイズ（上級編）</a>へ。</p>';"
            "document.getElementById('qz-again').onclick=function(){start();box.scrollIntoView({block:'start'})};"
            "var s=document.getElementById('qz-sh');s.onclick=function(){var u=location.origin+location.pathname;"
            "if(navigator.share){navigator.share({text:txt,url:u}).catch(function(){})}"
            "else if(navigator.clipboard){navigator.clipboard.writeText(txt+' '+u).then(function(){s.textContent='コピーしました'},function(){s.textContent='コピーできませんでした'})}};s.focus()}"
            "start()})();</script>")
    return {"path": "quiz", "title": "本当？ウソ？恋愛としぐさの通説クイズ", "date": "2026-10-08", "desc": desc[:120],
            "seo_title": f"恋愛・しぐさの心理学クイズ｜本当？ウソ？通説{N}問を研究で判定", "body": body, "css": CSS + QZ_CSS}

# ツールとデータの一覧（/tools/）。迷わせないよう、目的ごとに「まずはこれ」を大きく1〜2枚、ほかは小さな文字リンクにする。
# (id, 見出し, 大きく出すカード[(上の小見出し, 名前, 説明, path)], 小さく出すリンク[(前置き, 名前, path)])
HUB = [
    ("kimochi", "相手の気持ちが知りたい",
     [("付き合う前なら", "脈ありチェック", "気になる相手のしぐさを選ぶと、研究でどこまで好意の手がかりになるかを表示します。", "/myakuari-check/"),
      ("付き合ってからなら", "冷めたサインチェック", "連絡が減った・返信が遅いなどの変化が、研究で「冷めた」の手がかりになるかを表示します。", "/sameta-check/")],
     [("話が本当か気になるときは", "嘘のサインチェック", "/uso-check/")]),
    ("anzen", "この人、大丈夫？と不安なとき",
     [("まずはここから", "危険な相手のサイン チェックリスト", "束縛・モラハラ・ガスライティングなど、当てはまる言動を選ぶと、研究でわかっていることと相談先を表示します。", "/redflag-check/")],
     [("出来事を記録しておきたいときは", "ふたりの日記", "/nikki/")]),
    ("data", "研究データで調べたい",
     [("楽しく確かめるなら", "本当？ウソ？クイズ", "「嘘をつくと目をそらす」「遠距離恋愛はうまくいかない」は本当？しぐさと恋愛の通説を、研究で確かめた答えで出題します。", "/quiz/"),
      ("1つずつ調べるなら", "しぐさ索引", "目をそらす、腕を組むなど、気になったしぐさの意味を、研究で判定した一覧から調べられます。", "/shigusa/")],
     [("判定を数えた結果は", "しぐさ判定の集計", "/shigusa/hantei/"), ("恋愛・結婚の通説は", "恋愛・結婚の通説の判定", "/renai-tsusetsu/"),
      ("言葉の意味は", "用語集", "/glossary/"), ("記事の全体像は", "記事のマインドマップ", "/map/")]),
]
HUB_CSS = (".hb-sec{margin:34px 0 0;scroll-margin-top:80px}.hb-sec h2{font-size:19px;margin-bottom:12px}"
           ".hb-cards{display:grid;gap:12px}@media(min-width:620px){.hb-cards.two{grid-template-columns:1fr 1fr}}"
           ".hb-card{display:block;padding:18px 18px 16px;border-radius:16px;text-decoration:none;color:var(--text);background:var(--card);border:1px solid var(--border);border-left:4px solid var(--accent);transition:border-color .15s}"
           ".hb-card:hover{border-color:var(--accent)}.hb-card small{display:block;font-size:12px;font-weight:700;letter-spacing:.06em;color:var(--accent)}"
           ".hb-card b{display:block;font-size:18px;margin:4px 0 6px}.hb-card span{display:block;font-size:14px;line-height:1.7;color:var(--muted)}.hb-card em{display:inline-block;margin-top:10px;font-style:normal;font-size:14px;font-weight:700;color:var(--link)}"
           ".hb-more{list-style:none;margin:12px 0 0;padding:0}.hb-more li{font-size:14px;color:var(--muted);padding:8px 2px}.hb-more a{color:var(--link);font-weight:700}")


def hub_page():
    secs = ""
    items = []
    for sid, h, cards, more in HUB:
        cs = "".join(f'<a class="hb-card" href="{p}"><small>{E(k)}</small><b>{E(n)}</b><span>{E(d)}</span><em>使ってみる ›</em></a>' for k, n, d, p in cards)
        ms = "".join(f'<li>{E(k)}：<a href="{p}">{E(n)}</a></li>' for k, n, p in more)
        secs += f'<section class="hb-sec" id="{sid}"><h2>{E(h)}</h2><div class="hb-cards{" two" if len(cards) > 1 else ""}">{cs}</div>' + (f'<ul class="hb-more">{ms}</ul>' if ms else "") + '</section>'
        items += [(n, p) for _, n, _, p in cards] + [(n, p) for _, n, p in more]
    desc = "脈ありチェック、冷めたサインチェック、危険な相手のサイン チェックリスト、しぐさ索引など、しぐさと本音の無料ツールと研究データを、知りたいことから選べます。登録不要・入力は送信しません。"
    ld = json.dumps({"@context": "https://schema.org", "@type": "CollectionPage", "name": "ツールとデータ", "url": URL + "tools/", "description": desc, "publisher": PUB,
                     "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "url": URL + p.strip("/") + "/"} for i, (n, p) in enumerate(items)]}},
                    ensure_ascii=False).replace("</", "<\\/")
    body = (f'<script type="application/ld+json">{ld}</script>'
            '<p class="plead">知りたいことに近いものを1つ選んでください。どれも無料・登録不要で、入力した内容はどこにも送りません。</p>'
            + secs +
            '<p class="note" style="margin-top:34px">いま身の危険があるときは、ツールより先に<a href="tel:110">110番</a>へ。判断に迷う段階でも、DV相談ナビ（<a href="tel:%238008">#8008</a>）に相談できます。</p>')
    return {"path": "tools", "title": "ツールとデータ", "date": "2026-10-08", "desc": desc[:120],
            "seo_title": "恋愛・しぐさの無料ツールと研究データ｜脈あり・冷めた・危険な相手のチェック", "body": body, "css": CSS + HUB_CSS}

def pages(D, posts):
    return [redflag_page(posts), myakuari_page(D, posts), uso_page(D, posts), sameta_page(posts), nikki_page(posts), tsusetsu_page(posts), quiz_page(D, posts), hub_page()]


# 関連する記事の本文に、ツールへの「次の一歩」を差し込む（出典の直前。再実行しても1つだけになるよう置き換える）
BLOCK = re.compile(r"<!--tool-->.*?<!--/tool-->\n?", re.S)


def link_articles(D):
    targets = {}
    for _, _, _, s, _ in REDFLAG:
        if s:
            targets[s] = ("/redflag-check/", "危険な相手のサイン チェックリスト", "当てはまる言動を選ぶと、研究でわかっていることと相談先を表示します。")
    for _, _, _, s, _, _ in SAMETA:
        targets.setdefault(s, ("/sameta-check/", "冷めたサインチェック", "相手の変化を選ぶと、研究で「冷めた」の手がかりになるのかと、今日からできることを表示します。"))
    for x in D:
        if "like" in x.get("tags", []) and x["slug"] not in targets:
            targets[x["slug"]] = ("/myakuari-check/", "脈ありチェック", "気になる相手のしぐさを選ぶと、研究でどこまで好意の手がかりになるかを表示します。")
    for x in D:
        if "lie" in x.get("tags", []) and x["slug"] not in targets:
            targets[x["slug"]] = ("/uso-check/", "嘘のサインチェック", "気になったしぐさを選ぶと、研究で嘘の手がかりになるのかを表示します。")
    targets.setdefault("body-language-lie-detection-accuracy", ("/uso-check/", "嘘のサインチェック", "気になったしぐさを選ぶと、研究で嘘の手がかりになるのかを表示します。"))
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
