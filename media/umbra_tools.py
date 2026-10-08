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


def pages(D, posts):
    return [redflag_page(posts), myakuari_page(D, posts), uso_page(D, posts), sameta_page(posts)]


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
