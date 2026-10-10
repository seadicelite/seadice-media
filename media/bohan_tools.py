"""防犯メディアの個人向けWebツール（/sagi-check/ /ai-tenken/ /aikotoba/）を media/bohan-pages.json に書き出す。

  python3 media/bohan_tools.py && python3 media/build.py bohan

文言は、出典照合済みの記事の結論・「今日からできること」だけを使う（記事にない数字や助言を足さない）。
入力はブラウザの中だけで扱い、送信しない。保存するのはセルフ点検のチェック状態だけ（localStorage）。
- 詐欺かもチェック: SIGNS に項目を足す（記事が増えたら、その記事の結論から1〜2文で）
- セルフ点検: TENKEN に項目を足す（記事の「今日からできること」から）
ページの型は docs/quality/tool.md。
"""
import html
import json
from pathlib import Path

E = html.escape
ROOT = Path(__file__).resolve().parent.parent
URL = "https://bohan.seadice.win/"
PUB = {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}

CONTACTS = ('<ul class="bt-contact"><li>いま身の危険がある・事件に巻き込まれた：<a href="tel:110">110番</a></li>'
            '<li>詐欺かどうか相談したい：警察相談専用電話 <a href="tel:%239110">#9110</a></li>'
            '<li>お金・契約のトラブル：消費者ホットライン <a href="tel:188">188</a></li></ul>')

# (id, グループ, 当てはまること, 記事slug, 記事の結論・すること)
SIGNS = [
    ("h1", "common", "「今すぐ」「今日中に」と急がされている", "ai-era-scam-checklist",
     "急がされたら、それ自体を詐欺のサインと考え、その場で決めません。"),
    ("h2", "common", "「誰にも言わないで」と口止めされた", "fake-police-call-scam",
     "口止めは、相談させないための手口です。家族や身近な人にすぐ話します。"),
    ("t1", "tel", "家族を名乗る声で、事故・トラブル・急なお金の話をされた", "ai-voice-clone-family-scam",
     "AIで作った偽物の声を正しく見抜けたのは73%でした。声で判断せず、いったん切って登録してある本人の番号にかけ直します。"),
    ("t2", "tel", "警察・検察を名乗る相手が、振り込み・暗証番号・資産の確認を求めてきた", "fake-police-call-scam",
     "その場で電話を切り、言われた番号ではなく、自分で調べた警察署か #9110 にかけて確かめます。"),
    ("t3", "tel", "「+」で始まる番号（国際電話）からかかってきた", "international-call-block-scam",
     "2025年に特殊詐欺に使われた電話番号の75.5%は国際電話番号でした。知らない番号は留守番電話にし、着信ブロックを設定します。"),
    ("m1", "mail", "メールやSMSのリンクから、ログインや支払いを求められた", "phishing-mail-sms-2025",
     "リンクは開かず、いつも使う公式アプリやブックマークから入って確かめます。"),
    ("m2", "mail", "日本語は自然だが、急いで手続きするよう求めるメールだった", "ai-written-phishing-email",
     "日本語が自然でも安全とは限りません。研究では、AIが自動で書いた詐欺メールのクリック率は30〜44%でした。"),
    ("m3", "mail", "貼り紙・シール・メールのQRコードから、支払いやログインを求められた", "qr-code-phishing-sticker",
     "QRコードは貼り替えシールでないか触って確かめ、支払いやログインは公式アプリから行います。"),
    ("w1", "net", "パソコンやスマホに「ウイルスに感染」と出て、電話番号が表示された", "tech-support-scam-popup",
     "表示された番号には電話せず、タブやブラウザを閉じます。閉じられないときは再起動します。"),
    ("w2", "net", "有名人が投資やもうけ話をすすめる動画・広告を見た", "deepfake-video-celebrity-ad",
     "本物そっくりの動画は、人の目では見抜けません。動画だけを根拠にお金を動かさないでください。"),
    ("w3", "net", "相場より極端に安い通販サイトで買おうとしている", "fake-shopping-site-checklist",
     "安すぎる通販サイトは偽物かもしれません。支払う前に、記事の見分け方で確かめます。"),
    ("s1", "sns", "SNSで知り合った人や広告から、LINEに移るよう誘われた", "sns-investment-scam-line",
     "SNS型投資詐欺では、被害時の連絡ツールの9割以上がLINEでした。別のアプリに誘われたら、それ自体を警戒のサインと考えます。"),
    ("s2", "sns", "会ったことのない恋人・友人から、お金や投資の話が出た", "romance-scam-matching-app",
     "会えない相手からのお金の話は、ロマンス詐欺の典型です。送る前に、やりとりの画面を家族や知人に見せます。"),
    ("s3", "sns", "「即日即金」「ホワイト案件」などの高額バイトに誘われた", "yami-baito-recruitment-signs",
     "それは闇バイトのサインです。応募した若者は使い捨てにされます。応募せず、身近な人か #9110 に相談します。"),
    ("p1", "pay", "暗号資産（仮想通貨）で送るよう求められた", "crypto-transfer-scam-signs",
     "「暗号資産で送って」は詐欺のサインです。2025年は1,243件・196.9億円の被害があり、件数は前年の10倍を超えました。"),
    ("p2", "pay", "知らない個人名義の口座への振り込みを求められた", "sns-investment-scam-line",
     "知らない個人名義の口座への振り込みには応じません。会社や送金先の名前を自分で検索して確かめます。"),
]
SIGN_GROUPS = [("common", "どんな連絡でも"), ("tel", "電話"), ("mail", "メール・SMS・QRコード"),
               ("net", "パソコン・ネット"), ("sns", "SNS・出会い・バイト"), ("pay", "お金の送り方")]

# (id, グループ, やること, 所要, 記事slug)
TENKEN = [
    ("a1", "acc", "メール・銀行・よく使う通販のパスワードを、それぞれ別のものにした", "15分", "password-reuse-risk"),
    ("a2", "acc", "大事なアカウントで二段階認証（登録したスマホでの確認）をオンにした", "10分", "two-factor-passkey-account"),
    ("a3", "acc", "パスキーに対応しているサービスは、パスキーを設定した", "5分", "two-factor-passkey-account"),
    ("t1", "tel", "固定電話の国際電話を休止した（国際電話不取扱受付センターに申し込み・無料）", "10分", "international-call-block-scam"),
    ("t2", "tel", "携帯電話で、迷惑電話・国際電話の着信ブロックを設定した", "10分", "international-call-block-scam"),
    ("t3", "tel", "知らない番号からの電話は、すぐ出ずに留守番電話にしている", "0分", "international-call-block-scam"),
    ("s1", "sns", "スマホのカメラで、写真に位置情報を付けない設定にした", "3分", "sns-photo-location-home"),
    ("s2", "sns", "窓からの眺め・玄関・近所の店が写った写真を投稿しない", "習慣", "sns-photo-location-home"),
    ("s3", "sns", "旅行や外出先の写真は、帰ってから投稿している", "習慣", "sns-photo-location-home"),
    ("s4", "sns", "顔と声がはっきり入った動画の公開範囲を、友達・フォロワー限定にした", "3分", "sns-video-voice-clone-risk"),
    ("i1", "ai", "パスワード・カード番号・口座番号などは、AIチャットに入力しないと決めた", "1分", "ai-chat-input-personal-info"),
    ("i2", "ai", "AIチャットに貼る文章は、人名を「Aさん」、会社名を「X社」に置き換えている", "2分", "ai-chat-input-personal-info"),
    ("i3", "ai", "AIチャットの設定で「学習への利用」と「共有リンク」を確かめた", "3分", "ai-chat-input-personal-info"),
    ("f1", "fam", "家族だけの合言葉を決めた", "10分", "ai-voice-clone-family-scam"),
    ("f2", "fam", "離れて暮らす家族に「お金の電話は一度切って、私の携帯にかけ直して」と伝えた", "5分", "ai-voice-clone-family-scam"),
    ("f3", "fam", "メールやSMSのリンクからは入らず、公式アプリやブックマークから入ると決めた", "1分", "phishing-mail-sms-2025"),
]
TENKEN_GROUPS = [("acc", "アカウント"), ("tel", "電話"), ("sns", "SNSの写真・動画"), ("ai", "AIチャット"), ("fam", "家族との決まり")]

TITLES = json.loads((ROOT / "media/bohan-posts.json").read_text())
TITLES = {p["slug"]: p["title"].split("。")[0] for p in (TITLES if isinstance(TITLES, list) else TITLES["posts"])}

CSS = (".bt-box{background:var(--card);border:1px solid var(--accent);border-radius:16px;padding:18px 18px 8px;margin:20px 0}"
       ".bt-box h2{font-size:16px;margin:18px 0 6px}.bt-box h2:first-child{margin-top:0}"
       ".bt-box label{display:flex;gap:12px;align-items:flex-start;padding:12px 4px;border-top:1px solid var(--border);font-size:15px;line-height:1.6;cursor:pointer}"
       ".bt-box input[type=checkbox]{width:22px;height:22px;flex:0 0 22px;margin-top:1px;accent-color:var(--accent)}"
       ".bt-box label small{display:block;font-size:12px;color:var(--muted)}"
       ".bt-btn{display:block;width:100%;margin:16px 0 10px;padding:14px;border:0;border-radius:12px;background:var(--accent);color:var(--bg);font:inherit;font-size:16px;font-weight:800;cursor:pointer;min-height:48px}"
       ".bt-res{margin:20px 0;scroll-margin-top:80px}.bt-res[hidden]{display:none}"
       ".bt-card{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:14px;padding:16px 18px;margin:12px 0}"
       ".bt-card.alert{border-left-color:#E5534B}.bt-card h3{font-size:16px;margin-bottom:6px}.bt-card p{font-size:15px;line-height:1.8}"
       ".bt-item{padding:12px 0;border-top:1px solid var(--border);font-size:15px;line-height:1.8}.bt-item b{display:block}"
       ".bt-contact{margin:8px 0 0 1.2em;font-size:15px;line-height:1.9}.bt-contact a{font-weight:700}"
       ".bt-card a,.bt-item a,.bt-contact a,.bt-note a{color:var(--link)}"
       ".bt-bar{height:10px;border-radius:999px;background:var(--border);overflow:hidden;margin:8px 0 4px}.bt-bar i{display:block;height:100%;background:var(--accent);width:0}"
       ".bt-score{font-size:15px;font-weight:700}.bt-score b{font-size:26px;color:var(--accent)}"
       ".bt-note{background:rgba(93,169,233,.08);border:1px solid rgba(93,169,233,.3);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px;line-height:1.8}"
       ".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".bt-sub{font-size:13px;color:var(--muted)}"
       ".bt-tools{display:grid;gap:10px;margin:12px 0}.bt-tools a{display:block;background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px;color:var(--text);text-decoration:none;font-weight:700}"
       ".bt-tools a small{display:block;font-weight:400;font-size:13px;color:var(--muted)}.bt-tools a:hover{border-color:var(--accent)}"
       "details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}summary{cursor:pointer;font-weight:700;font-size:15px}details p{font-size:15px;margin-top:8px}"
       ".sources{margin-top:40px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;word-break:break-all}.sources a{color:var(--link)}")

TOOLS = [("sagi-check", "この連絡、詐欺かも？チェック", "電話・メール・SNSの連絡で、当てはまるサインを選ぶと、すぐやることがわかる"),
         ("ai-tenken", "AI時代の防犯 セルフ点検", "お金をかけずにできる16の対策を、自分の進み具合で確かめる"),
         ("aikotoba", "家族の合言葉カード", "AI音声のなりすましに備える合言葉の決め方と、印刷して使える手順カード")]


def other_tools(cur):
    return '<h2>ほかの防犯ツール</h2><div class="bt-tools">' + "".join(
        f'<a href="/{p}/">{E(t)}<small>{E(d)}</small></a>' for p, t, d in TOOLS if p != cur) + "</div>"


def ld(name, path, desc, faqs):
    g = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": name, "url": URL + path + "/", "applicationCategory": "UtilitiesApplication",
         "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "description": desc, "publisher": PUB},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}]}
    return '<script type="application/ld+json">' + json.dumps(g, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def faq_html(faqs):
    return "<h2>よくある質問</h2>" + "".join(
        f'<details{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(faqs))


def art(slug):
    return f'<a href="/{slug}/">{E(TITLES.get(slug, slug))}</a>'


# ---- この連絡、詐欺かも？チェック ----
SAGI_FAQ = [
    ("詐欺かどうかは、どうやって見分ければいいですか？",
     "AIで声・動画・文面の偽物が作れるため、見て・聞いて見分けるのは難しくなっています。急がされたら止まる、自分から公式の窓口にかけ直す、お金の話は送る前に相談する、の3つの手順で守ります。"),
    ("サインが1つも当てはまらなければ安全ですか？",
     "安全とは言い切れません。このチェックは、記事で調べた代表的な手口のサインだけを並べたものです。迷ったら、送る前に家族や警察相談専用電話（#9110）、消費者ホットライン（188）に相談してください。"),
    ("選んだ内容はどこかに送られますか？", "送られません。判定はすべてブラウザの中で行い、保存もしません。"),
]
sagi_rows = "".join(
    f'<h2>{E(gl)}</h2>' + "".join(f'<label><input type="checkbox" value="{i}"><span>{E(t)}</span></label>' for i, g, t, _, _ in SIGNS if g == gk)
    for gk, gl in SIGN_GROUPS)
sagi_data = json.dumps({i: [t, s, TITLES.get(s, s), c] for i, _, t, s, c in SIGNS}, ensure_ascii=False)
sagi_body = (ld("この連絡、詐欺かも？チェック", "sagi-check",
                "電話・メール・SMS・SNSで届いた連絡に当てはまるサインを選ぶと、すぐやることと解説記事がわかる無料ツール。AI音声のなりすまし・ニセ警察・SNS型投資詐欺などに対応。登録不要・広告なし。", SAGI_FAQ)
 + '<p>電話・メール・SNSで届いた連絡に、当てはまるものを選んでください。すぐやることと、くわしい解説記事を表示します。無料・登録不要で、選んだ内容はどこにも送られません。</p>'
 + '<div class="bt-card alert"><h3>お金を送る前に、いったん止まってください</h3><p>まだ送っていなければ、このチェックを終えるまで送金・振り込み・暗号資産の送信をしないでください。</p></div>'
 + f'<form class="bt-box" id="sg" onsubmit="return false">{sagi_rows}<button type="submit" class="bt-btn">チェックする</button></form>'
 + '<div class="bt-res" id="sg-out" aria-live="polite" hidden></div>'
 + '<p class="answer"><strong>結論：声・動画・文面が本物そっくりでも、急がせる・口止めする・お金を求める連絡は疑ってかまいません。</strong>見分けるより、自分から公式の窓口にかけ直す手順で確かめます。</p>'
 + '<h2>どの手口にも効く3つの決まり</h2><ol class="bt-note" style="padding-left:2.2em">'
 '<li><b>急がされたら止まる</b>：「今すぐ」「誰にも言わないで」と言われたら、その場で決めません。</li>'
 '<li><b>自分からかけ直す・開き直す</b>：電話は一度切って公式の番号に。メール・SMSのリンクは押さず、公式アプリから。</li>'
 '<li><b>お金の話は送る前に相談する</b>：家族や #9110、188 に相談します。</li></ol>'
 + '<h2>チェックの根拠</h2><p>各項目は、このメディアで出典を照合した記事の結論をもとにしています。2025年の特殊詐欺は2万7,832件・1,423.1億円で、被害額は前年のほぼ2倍でした（警察庁）。手口ごとのまとめは '
 + art("ai-era-scam-checklist") + ' にあります。</p>'
 + '<table class="bt-t"><caption class="bt-sub">入力例と結果の例</caption><thead><tr><th>当てはまったこと</th><th>表示される、すぐやること</th></tr></thead><tbody>'
 '<tr><td>家族の声で「事故を起こした、今すぐお金が必要」</td><td>いったん切って、登録してある本人の番号にかけ直す</td></tr>'
 '<tr><td>「警察です」の電話で、口座の確認を求められた</td><td>電話を切り、自分で調べた警察署か #9110 にかけて確かめる</td></tr>'
 '<tr><td>SNSの投資の話で「LINEに移って」と誘われた</td><td>それ自体を警戒のサインと考え、送る前に画面を家族に見せる</td></tr></tbody></table>'
 + faq_html(SAGI_FAQ) + other_tools("sagi-check")
 + '<div class="sources"><h2>出典</h2><ol><li>警察庁「令和7年における特殊詐欺及びSNS型投資・ロマンス詐欺の認知・検挙状況等について（確定値）」(2026年5月22日) <a href="https://www.npa.go.jp/bureau/criminal/souni/tokusyusagi/hurikomesagi_toukei2025.pdf" rel="noopener">https://www.npa.go.jp/bureau/criminal/souni/tokusyusagi/hurikomesagi_toukei2025.pdf</a></li>'
 '<li>Mai, K. T., et al. (2023). Warning: Humans cannot reliably detect speech deepfakes. <i>PLOS ONE</i>, 18, e0285333. <a href="https://doi.org/10.1371/journal.pone.0285333" rel="noopener">https://doi.org/10.1371/journal.pone.0285333</a></li>'
 '<li>Heiding, F., et al. (2024). Devising and Detecting Phishing Emails Using Large Language Models. <i>IEEE Access</i>, 12, 42131-42146. <a href="https://doi.org/10.1109/ACCESS.2024.3375882" rel="noopener">https://doi.org/10.1109/ACCESS.2024.3375882</a></li>'
 '<li>個々の数字の出典は、各解説記事の末尾にあります。</li></ol></div>'
 + "<script>(function(){var D=" + sagi_data.replace("</", "<\\/") + ",C=" + json.dumps(CONTACTS)
 + r""";
function e(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
document.getElementById('sg').addEventListener('submit',function(){
 var ids=[].map.call(document.querySelectorAll('#sg input:checked'),function(i){return i.value}),o=document.getElementById('sg-out'),h='';
 if(!ids.length){h='<div class="bt-card"><h3>当てはまるサインはありませんでした</h3><p>ただし、安全とは言い切れません。このチェックに無い手口もあります。お金や個人情報を求められているなら、送る前に家族か窓口に相談してください。</p>'+C+'</div>'}
 else{h='<div class="bt-card alert"><h3>詐欺のサインが '+ids.length+' つ当てはまりました</h3><p>お金・暗証番号・個人情報は送らないでください。下の「すぐやること」を確かめ、迷ったら相談します。</p>'+C+'</div><div class="bt-card"><h3>すぐやること</h3>'
  +ids.map(function(i){var d=D[i];return '<div class="bt-item"><b>'+e(d[0])+'</b>'+e(d[3])+' <a href="/'+d[1]+'/">'+e(d[2])+'</a></div>'}).join('')+'</div>'}
 o.innerHTML=h;o.hidden=false;o.scrollIntoView({behavior:'smooth',block:'start'});
});})();</script>""")

# ---- AI時代の防犯 セルフ点検 ----
TK_FAQ = [
    ("AI時代の詐欺や乗っ取りに、まず何をすればいいですか？",
     "お金をかけずにできるのは、大事なアカウントのパスワードを別々にして二段階認証をオンにすること、知らない番号の電話にすぐ出ないこと、家族で合言葉を決めることです。"),
    ("チェックした内容はどこに保存されますか？",
     "この端末のブラウザの中だけです。サーバーには送りません。ブラウザのデータを消すと、チェックも消えます。"),
    ("全部やらないと意味がありませんか？",
     "いいえ。大事なアカウントや、家族との決まりなど、被害が大きいところから1つずつで十分です。"),
]
tk_rows = "".join(
    f'<h2>{E(gl)}</h2>' + "".join(f'<label><input type="checkbox" value="{i}"><span>{E(t)}<small>所要 {E(m)} ・ {art(s)}</small></span></label>'
                                  for i, g, t, m, s in TENKEN if g == gk)
    for gk, gl in TENKEN_GROUPS)
tk_body = (ld("AI時代の防犯 セルフ点検", "ai-tenken",
              "パスワード・二段階認証・国際電話の休止・SNS写真の位置情報・AIチャットの入力・家族の合言葉など、お金をかけずにできる16の対策を点検する無料ツール。進み具合は端末の中だけに保存、登録不要・広告なし。", TK_FAQ)
 + '<p>AIで声や写真が悪用される時代に、お金をかけずにできる対策を16個並べました。やったものにチェックすると、進み具合が出ます。無料・登録不要で、チェックは<strong>この端末の中だけ</strong>に保存し、どこにも送りません。</p>'
 + f'<p class="bt-score" aria-live="polite"><b id="tk-n">0</b> / {len(TENKEN)} できています</p><div class="bt-bar"><i id="tk-bar"></i></div><p class="bt-sub" id="tk-msg"></p>'
 + f'<div class="bt-box" id="tk">{tk_rows}</div>'
 + '<p><button type="button" id="tk-reset" class="bt-btn" style="background:var(--card);color:var(--text);border:1px solid var(--border)">チェックをすべて外す</button></p>'
 + '<p class="answer"><strong>結論：まずは「アカウント」と「家族との決まり」から。</strong>パスワードを別々にして二段階認証をオンにし、お金の電話は一度切ってかけ直すと家族で決めておきます。</p>'
 + '<h2>この点検の根拠</h2><p>項目は、このメディアで出典を照合した記事の「お金をかけずに今日からできること」から選んでいます。たとえば、35万件の乗っ取りの試みを分析した研究では、登録した端末での確認がフィッシングによる乗っ取りの94%以上を防ぎました（' + art("two-factor-passkey-account")
 + '）。2025年に特殊詐欺に使われた電話番号の75.5%は国際電話番号でした（' + art("international-call-block-scam") + '）。</p>'
 + '<table class="bt-t"><caption class="bt-sub">始める順番の例</caption><thead><tr><th>順番</th><th>やること</th><th>所要</th></tr></thead><tbody>'
 '<tr><td>1</td><td>メール・銀行・通販のパスワードを別々にする</td><td>15分</td></tr>'
 '<tr><td>2</td><td>同じアカウントで二段階認証をオンにする</td><td>10分</td></tr>'
 '<tr><td>3</td><td>家族で合言葉を決め、お金の電話はかけ直すと伝える</td><td>15分</td></tr></tbody></table>'
 + faq_html(TK_FAQ) + other_tools("ai-tenken")
 + '<div class="sources"><h2>出典</h2><ol><li>各項目の出典は、リンク先の解説記事の末尾にあります。</li></ol></div>'
 + "<script>(function(){var K='bohan-ai-tenken-v1',N=" + str(len(TENKEN)) + r""",S={};
try{S=JSON.parse(localStorage.getItem(K)||'{}')||{}}catch(e){S={}}
var bs=document.querySelectorAll('#tk input');
function upd(){var n=0;[].forEach.call(bs,function(b){if(b.checked)n++});document.getElementById('tk-n').textContent=n;document.getElementById('tk-bar').style.width=(n*100/N)+'%';
 document.getElementById('tk-msg').textContent=n===0?'できているものにチェックしてください。':n<N?'あと '+(N-n)+' 個。チェックのない項目のリンク先に、やり方があります。':'すべてできています。家族にもこのページを教えてあげてください。'}
function save(){var o={};[].forEach.call(bs,function(b){if(b.checked)o[b.value]=1});try{localStorage.setItem(K,JSON.stringify(o))}catch(e){document.getElementById('tk-msg').textContent='このブラウザでは保存できません（プライベートブラウズなど）。'}}
[].forEach.call(bs,function(b){b.checked=!!S[b.value];b.addEventListener('change',function(){save();upd()})});
document.getElementById('tk-reset').addEventListener('click',function(){if(!confirm('チェックをすべて外しますか？'))return;[].forEach.call(bs,function(b){b.checked=false});save();upd()});
upd();})();</script>""")

# ---- 家族の合言葉カード ----
AK_FAQ = [
    ("合言葉はどう決めればいいですか？",
     "SNSなどに出ていない、家族しか知らない思い出や呼び名を使います。急な電話では、合言葉を確かめてから話を進めます。"),
    ("AIで作った声は聞き分けられますか？",
     "研究では、偽物の声を正しく見抜けたのは73%でした。約12分練習しても見分ける力はほとんど伸びなかったため、声で判断しないことが大切です。"),
    ("このカードに合言葉を書いてもいいですか？",
     "書かないでください。カードをなくしたり写真に写ったりすると、合言葉が知られてしまいます。カードには確かめる手順だけを書き、合言葉は家族で覚えます。"),
]
IDEAS = ["家族だけが使っている、ペットや家族の呼び名", "子どものころの、家族だけの思い出の場所", "家族旅行で起きた、写真に残っていない出来事",
         "家族の誰かの、SNSに書いていない好物", "昔の家で使っていた、家族だけの言い方", "最初に家族で決めた、本人しか知らない質問と答え"]
ak_checks = ["SNS・ブログ・写真に出したことがない", "家族全員が、すぐ思い出せる", "名前・誕生日・住所など、調べればわかる情報ではない", "電話で言っても、まわりに聞かれて困らない"]
ak_body = (ld("家族の合言葉カード", "aikotoba",
              "AI音声のなりすまし詐欺に備えて、家族の合言葉の決め方を確かめ、電話を受けたときの手順を書いた印刷用カードを作る無料ツール。合言葉は入力・保存しない。登録不要・広告なし。", AK_FAQ)
 + '<p>家族の声そっくりの電話に備えて、合言葉を決め、電話を受けたときの手順を1枚のカードにします。無料・登録不要です。<strong>合言葉そのものは、このページに入力しません。</strong></p>'
 + '<div class="bt-box"><h2>1. 合言葉の題材を選ぶ</h2><p class="bt-sub">押すたびに、題材の例が変わります。家族で話して決めてください。</p>'
 '<p id="ak-idea" style="font-size:17px;font-weight:700;margin:10px 0" aria-live="polite">' + E(IDEAS[0]) + '</p>'
 '<button type="button" class="bt-btn" id="ak-next">ほかの例を見る</button>'
 '<h2>2. 決めた合言葉を確かめる</h2>' + "".join(f'<label><input type="checkbox" class="ak-c"><span>{E(c)}</span></label>' for c in ak_checks)
 + '<p id="ak-ok" class="bt-sub" aria-live="polite" style="padding:8px 4px 12px">4つ全部に当てはまる合言葉にしましょう。</p></div>'
 + '<div class="bt-box"><h2>3. 手順カードを作る</h2>'
 '<label for="ak-name" style="display:block;border:0;padding:4px 0">カードに書く家族の呼び名（任意）</label>'
 '<input id="ak-name" maxlength="20" placeholder="例：たかし" style="width:100%;font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);min-height:48px">'
 '<button type="button" class="bt-btn" id="ak-print">カードを印刷する</button><p class="bt-sub" style="padding-bottom:10px">呼び名は印刷にだけ使い、保存・送信しません。</p></div>'
 + '<div id="ak-card" class="bt-card"><h3>お金の電話が来たら（<span id="ak-who">家族</span>を名乗る電話）</h3><ol style="margin:6px 0 0 1.4em;font-size:15px;line-height:1.9">'
 '<li>声が似ていても、いったん切る</li><li>登録してある本人の番号に、自分からかけ直す</li><li>かけ直せないときは、合言葉を聞いてから話を進める</li>'
 '<li>「今すぐ」「誰にも言うな」は詐欺のサイン。一人で決めない</li><li>迷ったら 警察相談専用電話 #9110 ／ 危ないときは 110番</li></ol>'
 '<p class="bt-sub" style="margin-top:8px">本人の番号：＿＿＿＿＿＿＿＿＿＿＿　合言葉はこのカードに書かない</p></div>'
 + '<p class="answer"><strong>結論：声では本物か見分けられないので、声以外の確かめ方を家族で決めておきます。</strong>いったん切ってかけ直す、合言葉を聞く、の2つです。</p>'
 + '<h2>なぜ合言葉が必要なのか</h2><p>529人の実験で、AIで作った偽物の声を正しく見抜けたのは73%でした。偽物の声の例を聞かせても成績はわずかしか上がらず、約12分練習しても見分ける力はほとんど伸びませんでした。2025年のオレオレ詐欺は14,489件で、前の年より7,737件増えています。くわしくは '
 + art("ai-voice-clone-family-scam") + ' で解説しています。</p>'
 + '<p>声のなりすましは、SNSの動画の声から作られることもあります。合言葉は、SNSや写真に出ていない話題にします（' + art("sns-video-voice-clone-risk") + '）。</p>'
 + '<table class="bt-t"><caption class="bt-sub">合言葉の良い例・避けたい例</caption><thead><tr><th>良い例</th><th>避けたい例</th></tr></thead><tbody>'
 '<tr><td>家族だけが使う、昔の犬の呼び名</td><td>SNSに写真を載せているペットの名前</td></tr>'
 '<tr><td>家族旅行で起きた、写真に残っていない出来事</td><td>誕生日・出身校・住んでいる町</td></tr></tbody></table>'
 + faq_html(AK_FAQ) + other_tools("aikotoba")
 + '<div class="sources"><h2>出典</h2><ol><li>Mai, K. T., Bray, S., Davies, T., &amp; Griffin, L. D. (2023). Warning: Humans cannot reliably detect speech deepfakes. <i>PLOS ONE</i>, 18, e0285333. <a href="https://doi.org/10.1371/journal.pone.0285333" rel="noopener">https://doi.org/10.1371/journal.pone.0285333</a></li>'
 '<li>Yang, J., et al. (2026). Short-Term Perceptual Training Modulates Neural Responses to Deepfake Speech But Does Not Improve Behavioral Discrimination. <i>eNeuro</i>, 13. <a href="https://doi.org/10.1523/eneuro.0300-25.2026" rel="noopener">https://doi.org/10.1523/eneuro.0300-25.2026</a></li>'
 '<li>警察庁「令和7年における特殊詐欺及びSNS型投資・ロマンス詐欺の認知・検挙状況等について（確定値）」(2026年5月22日) <a href="https://www.npa.go.jp/bureau/criminal/souni/tokusyusagi/hurikomesagi_toukei2025.pdf" rel="noopener">https://www.npa.go.jp/bureau/criminal/souni/tokusyusagi/hurikomesagi_toukei2025.pdf</a></li></ol></div>'
 + "<script>(function(){var I=" + json.dumps(IDEAS, ensure_ascii=False) + r""",k=0;
document.getElementById('ak-next').addEventListener('click',function(){k=(k+1)%I.length;document.getElementById('ak-idea').textContent=I[k]});
var cs=document.querySelectorAll('.ak-c');[].forEach.call(cs,function(c){c.addEventListener('change',function(){var n=0;[].forEach.call(cs,function(x){if(x.checked)n++});
 document.getElementById('ak-ok').textContent=n===cs.length?'その合言葉なら大丈夫です。家族全員で覚えましょう。':'4つ全部に当てはまる合言葉にしましょう（いま '+n+' つ）。'})});
var nm=document.getElementById('ak-name');nm.addEventListener('input',function(){document.getElementById('ak-who').textContent=nm.value.trim()||'家族'});
document.getElementById('ak-print').addEventListener('click',function(){window.print()});
})();</script>""")
ak_css = ("@media print{body{background:#fff}body *{visibility:hidden}#ak-card,#ak-card *{visibility:visible}#ak-card{position:absolute;left:0;top:0;width:100%;background:#fff;color:#000;border:2px solid #000}"
          "#ak-card .bt-sub{color:#000}}")
T_CSS = (".bt-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.bt-t caption{text-align:left;margin-bottom:6px}"
         ".bt-t th,.bt-t td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top}.bt-t th{background:var(--card)}")

PAGES = [
    {"path": "sagi-check", "title": "この連絡、詐欺かも？チェック",
     "seo_title": "詐欺かも チェック｜電話・メール・SNSの連絡に当てはまるサインと、すぐやること（AI時代の手口に対応）",
     "date": "2026-10-11",
     "desc": "家族の声の電話、「警察です」の電話、LINEへの誘い、暗号資産の送金。当てはまるサインを選ぶと、すぐやることと解説記事がわかる。警察庁の統計と研究をもとにした無料・登録不要のチェック。",
     "body": sagi_body, "css": CSS + T_CSS},
    {"path": "ai-tenken", "title": "AI時代の防犯 セルフ点検",
     "seo_title": "AI時代の防犯 セルフ点検｜パスワード・電話・SNS・AIチャット・家族の16項目（無料・登録不要）",
     "date": "2026-10-11",
     "desc": "パスワードの使い回し、二段階認証、国際電話の休止、写真の位置情報、AIチャットへの入力、家族の合言葉。お金をかけずにできる16の対策を点検。進み具合は端末の中だけに保存。",
     "body": tk_body, "css": CSS + T_CSS},
    {"path": "aikotoba", "title": "家族の合言葉カード",
     "seo_title": "家族の合言葉 決め方｜AI音声のなりすまし詐欺に備える手順カード（印刷用・無料）",
     "date": "2026-10-11",
     "desc": "AIで作った偽物の声を見抜けたのは73%。声で判断せず、合言葉とかけ直しで確かめます。合言葉の決め方のチェックと、電話を受けたときの手順を書いた印刷用カード。",
     "body": ak_body, "css": CSS + T_CSS + ak_css},
]

if __name__ == "__main__":
    (ROOT / "media/bohan-pages.json").write_text(json.dumps(PAGES, ensure_ascii=False, indent=2) + "\n")
    print(len(PAGES), "pages")
