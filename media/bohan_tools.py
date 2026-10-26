"""防犯メディアの個人向けWebツール（/akisu-me/ /hitorigurashi/ /sagi-check/ /link-check/ /ai-tenken/ /aikotoba/）を media/bohan-pages.json に書き出す。

  python3 media/bohan_tools.py && python3 media/build.py bohan

文言は、出典照合済みの記事の結論・「今日からできること」だけを使う（記事にない数字や助言を足さない）。
入力はブラウザの中だけで扱い、送信しない。保存するのはセルフ点検のチェック状態だけ（localStorage）。
- 詐欺かもチェック: SIGNS に項目を足す（記事が増えたら、その記事の結論から1〜2文で）
- セルフ点検: TENKEN に項目を足す（記事の「今日からできること」から）
- 空き巣の目で点検: AKISU に項目を足す（空き巣の記事の「今日からできること」から。段階は下見の3点）
- 一人暮らしの防犯チェック: HITORI に項目を足す（一人暮らし・夜道・SNSの記事の「今日からできること」から。優先は統計で多い手口に当たるかで決める）
- 記事 → ツールのリンク（media/bohan-toollinks.json）は SIGNS / TENKEN の記事slugから自動で作る。本体のツールは HONTAI に書く（json を手で直すと消える）
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
    ("a0", "acc", "スマホ・パソコン・アプリの自動更新をオンにした", "5分", "security-checkup-expert-priorities"),
    ("a1", "acc", "メール・銀行・よく使う通販のパスワードを、それぞれ別のものにした", "15分", "password-reuse-risk"),
    ("a2", "acc", "大事なアカウントで二段階認証（登録したスマホでの確認）をオンにした", "10分", "two-factor-passkey-account"),
    ("a3", "acc", "パスキーに対応しているサービスは、パスキーを設定した", "5分", "two-factor-passkey-account"),
    ("a4", "acc", "使っていないアカウントを、受信箱と保存済みパスワードから洗い出した", "15分", "unused-accounts-cleanup"),
    ("d1", "dev", "スマホの画面ロックを6桁以上の暗証番号にした", "3分", "lost-stolen-smartphone-prep"),
    ("d2", "dev", "遠隔で探す・ロック・消去する機能をオンにし、家族の端末から開く方法を試した", "5分", "lost-stolen-smartphone-prep"),
    ("d3", "dev", "位置情報・マイク・カメラを許可しているアプリを見直し、用途に合わないものを外した", "15分", "app-permissions-review"),
    ("d4", "dev", "自宅・職場以外のWi-Fiに自動でつながらない設定にした", "3分", "public-wifi-real-risk"),
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
    ("f4", "fam", "離れて暮らす親と一緒に、親のスマホの自動更新と知らない番号の着信設定を確かめた", "15分", "parents-smartphone-security-check"),
    ("f5", "fam", "親のスマホの画面ロックと「遠隔で探す」がオンか、親の同意をとって一緒に確かめた", "5分", "parents-smartphone-security-check"),
]
TENKEN_GROUPS = [("acc", "アカウント"), ("dev", "スマホ・Wi-Fi"), ("tel", "電話"), ("sns", "SNSの写真・動画"), ("ai", "AIチャット"), ("fam", "家族との決まり")]

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

TOOLS = [("akisu-me", "空き巣の目で、わが家を点検", "空き巣が下見で見る「留守か・近づけるか・時間がかかるか」の順に、わが家の隙を見つける"),
         ("hitorigurashi", "一人暮らしの防犯チェック", "住まい・帰り道・部屋にいるとき・SNSで当てはまる隙を選ぶと、今週やること3つがわかる"),
         ("sagi-check", "この連絡、詐欺かも？チェック", "電話・メール・SNSの連絡で、当てはまるサインを選ぶと、すぐやることがわかる"),
         ("link-check", "そのリンクちょっと待った", "届いたSMS・メールのリンクを貼ると、詐欺の報告一覧と偽ドメインを点検し、AIが危険度と理由を返す"),
         ("ai-tenken", "AI時代の防犯 セルフ点検", "お金をかけずにできる24の対策を、自分の進み具合で確かめる"),
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
              "自動更新・パスワード・二段階認証・国際電話の休止・SNS写真の位置情報・AIチャットの入力・家族の合言葉など、お金をかけずにできる24の対策を点検する無料ツール。進み具合は端末の中だけに保存、登録不要・広告なし。", TK_FAQ)
 + '<p>AIで声や写真が悪用される時代に、お金をかけずにできる対策を24個並べました。やったものにチェックすると、進み具合が出ます。無料・登録不要で、チェックは<strong>この端末の中だけ</strong>に保存し、どこにも送りません。</p>'
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

# ---- 空き巣の目で、わが家を点検 ----
# 警察庁「侵入者プロファイリング」の下見の3点（留守か・入りやすいか・逃げやすいか）の順に、外から見える隙を選ぶ。
# (id, 段階, 空き巣から見える隙, 直し方, 所要, 並べ替え用の秒数, 記事slug)
AKISU = [
    ("r1", "rusu", "郵便受けに、新聞や手紙がたまっていることがある",
     "旅行や帰省の前は新聞を止め、郵便物は家族や近所の人に取ってもらいます。", "10分", 600, "vacation-empty-home-burglary"),
    ("r2", "rusu", "旅行や外出先の写真を、出かけている間にSNSに載せることがある",
     "写真は帰ってから載せます。「いま家を空けている」ことを知らせずに済みます。", "0分", 0, "sns-photo-location-home"),
    ("r3", "rusu", "家を長く空けるとき、隣の人に伝えていない",
     "隣の人に留守を伝えると、見慣れない人や車に気づいてもらえます。", "2分", 120, "vacation-empty-home-burglary"),
    ("r4", "rusu", "夜に留守にすると、家の外が真っ暗になる",
     "玄関灯は暗くなる前からつけておきます。今ある照明にタイマー機能があれば、それを使うだけで十分です。", "3分", 180, "burglary-daylight-darkness-risk"),
    ("c1", "chika", "窓や玄関の前が、植木や荷物で道路や隣の家から見えにくい",
     "窓の前の植木を剪定し、荷物をどけて、道路や隣の家から見通せるようにします。", "5分", 300, "burglary-daylight-darkness-risk"),
    ("c2", "chika", "塀や窓の近くに、脚立・台・箱など足場になる物がある",
     "足場になる物を片付けます。侵入者は窓の近くの足場と死角を見ています。", "30分", 1800, "window-glass-breaking-burglary"),
    ("c3", "chika", "近所の人とあいさつすることが、ほとんどない",
     "近所の人にあいさつします。犯行をあきらめた理由で多いのは「近所の人に声をかけられたり、じろじろ見られた」ことです。", "毎日数秒", 5, "burglar-target-selection-5-minutes"),
    ("c4", "chika", "合鍵を、植木鉢の下・郵便受け・メーターボックスなど家の外に置いている",
     "合鍵は外に置かず、必要な本数だけにして持ち歩きます。侵入者はこうした隠し場所をよく見ています。", "1分", 60, "burglar-target-selection-5-minutes"),
    ("j1", "jikan", "ゴミ出しや近所への買い物くらいなら、鍵をかけずに出かける",
     "数分の外出でも、窓と玄関の鍵をかけます。鍵のかけ忘れは、一戸建てで2番目、共同住宅で1番目に多い侵入手口です。", "10秒", 10, "burglar-target-selection-5-minutes"),
    ("j2", "jikan", "窓に補助の鍵があるのに、ふだんは使っていない",
     "クレセント錠と補助の鍵の両方をかけます。窓を開けるまでの時間が増えます。", "10秒", 10, "window-glass-breaking-burglary"),
    ("j3", "jikan", "雨戸やシャッターがあるのに、出かけるときに閉めていない",
     "外出するときは雨戸やシャッターを閉めます。警察庁がガラス破りの対策として挙げている方法です。", "1分", 60, "window-glass-breaking-burglary"),
    ("j4", "jikan", "家にいるときや寝るときは、玄関や窓の鍵をかけていない",
     "在宅中も玄関の鍵とドアガードをかけます。家の人がいるかどうかに関係なく、窓ガラスを割って押し入る手口があります。", "5秒", 5, "home-invasion-robbery-at-home"),
    ("j5", "jikan", "「オートロックだから」「高い階だから」と、部屋の玄関やベランダの窓を開けておくことがある",
     "建物の入口と部屋の鍵は別に考えます。4階建以上の共同住宅でも、侵入手口の1位は鍵のかけ忘れ、侵入口の1位は玄関でした。", "10秒", 10, "auto-lock-apartment-burglary"),
    ("j6", "jikan", "今の家に入居したとき、鍵を交換したかを確かめていない",
     "管理会社や大家さんに、入居前に鍵を交換したかを聞きます。4階建以上の共同住宅では、侵入の24.6%が合かぎによるものでした。", "10分", 600, "moving-new-home-security"),
]
AKISU_STAGES = [
    ("rusu", "1. 留守かどうかを見る", "空き巣は人と顔を合わせずに済む家を探します。留守を確かめる方法で最も多いのはインターホンを鳴らすこと、次に見るのが郵便受けです。",
     "留守がわかりやすい", "留守がわかりにくい"),
    ("chika", "2. 見られずに近づけるかを見る", "空き巣が避けたいのは、人に見られることです。死角・足場・近所の目を見ています。",
     "見られずに近づけそう", "近づくと見られそう"),
    ("jikan", "3. 入るのに時間がかかるかを見る", "侵入に5分かかると約7割が、10分以上かかるとほとんどがあきらめると、警察庁は紹介しています。",
     "すぐ入れそう", "時間がかかりそう"),
]
AKISU_NEAR = ("a1", "この1〜2か月の間に、家や近所で空き巣の被害があった", "repeat-burglary-victimization")

AM_FAQ = [
    ("空き巣は、どんな家を狙いますか？",
     "警察庁によると、空き巣は下見で「留守か」「入りやすいか」「逃げやすいか」の3点を確かめます。研究では、家の豊かさより、犯人の家からの近さや入りやすさの方が狙われやすさに強く影響していました。"),
    ("お金をかけずにできる対策で、いちばん大事なものは？",
     "短い外出でも、今ある鍵を全部かけることです。鍵のかけ忘れは、一戸建てで2番目、共同住宅で1番目に多い侵入手口です（警察庁、令和7年）。"),
    ("隙が0個なら、空き巣に入られませんか？",
     "入られないとは言い切れません。この点検は、外から見える隙のうち、記事で調べた代表的なものだけを並べています。逃げやすさ（駅に近い、人通りが少ないなど）のように、家では変えられない条件もあります。"),
    ("選んだ内容はどこかに送られますか？", "送られません。結果はすべてブラウザの中で出し、保存もしません。"),
]


def _am_row(i, t):
    return f'<label><input type="checkbox" value="{i}"><span>{E(t)}</span></label>'


am_rows = "".join(
    f'<h2>{E(sl)}</h2><p class="bt-sub" style="padding:0 4px 6px">{E(sd)}</p>'
    + "".join(_am_row(i, t) for i, g, t, *_ in AKISU if g == sk)
    for sk, sl, sd, _, _ in AKISU_STAGES)
am_rows += ('<h2>4. 近くで被害があったか</h2><p class="bt-sub" style="padding:0 4px 6px">空き巣は、一度成功した家や、その近くに戻ってくることがあります。</p>'
            + _am_row(AKISU_NEAR[0], AKISU_NEAR[1]))
am_data = json.dumps({"items": {i: [g, t, f, m, sec, s, TITLES.get(s, s)] for i, g, t, f, m, sec, s in AKISU},
                      "stages": [[k, {"rusu": "留守か", "chika": "近づけるか", "jikan": "時間がかかるか"}[k], bad, good] for k, l, _, bad, good in AKISU_STAGES],
                      "near": [AKISU_NEAR[2], TITLES.get(AKISU_NEAR[2], AKISU_NEAR[2])]}, ensure_ascii=False)
am_body = (ld("空き巣の目で、わが家を点検", "akisu-me",
              "空き巣が下見で確かめる「留守か・見られずに近づけるか・入るのに時間がかかるか」の順に、わが家の外から見える隙を選ぶと、空き巣から見た下見メモと、手間の小さい順の直し方がわかる無料ツール。警察庁の資料と研究にもとづく。登録不要・広告なし。", AM_FAQ)
 + '<p>空き巣は、入る前に家を「下見」します。見ているのは<strong>留守か・見られずに近づけるか・入るのに時間がかかるか</strong>です。その順に、わが家に当てはまるものを選んでください。空き巣の目に見える隙と、手間の小さい順の直し方を表示します。無料・登録不要で、選んだ内容はどこにも送られません。</p>'
 + '<p class="bt-sub">家の外に出て、道路から自分の家を眺めながら選ぶと、空き巣と同じ景色で確かめられます。</p>'
 + f'<form class="bt-box" id="am" onsubmit="return false">{am_rows}<button type="submit" class="bt-btn">空き巣の目で見る</button></form>'
 + '<div class="bt-res" id="am-out" aria-live="polite" hidden></div>'
 + '<p class="answer"><strong>結論：空き巣が選ぶのは、豊かな家より「手早く、見られずに入れそうな家」です。</strong>留守のサインを消し、死角と足場を減らし、短い外出でも鍵を全部かけると、空き巣の目には「面倒な家」に見えます。どれもお金はかかりません。</p>'
 + '<h2>なぜ「空き巣の目」で点検するのか</h2><p>空き巣は、慣れた手順で家を品定めしています。経験の多い侵入窃盗犯50人への聞き取りでは、45人が決まったパターンで家の中を物色しており、手慣れた習慣で動いていました。3か国の侵入窃盗1,835件の分析では、犯人の家に近い地域や一戸建ての多い地域ほど狙われやすく、地域の豊かさは一貫した影響を示しませんでした（'
 + art("burglar-target-selection-5-minutes") + '）。</p>'
 + '<p>守る側も、相手が見る点に合わせて直すのがいちばん無駄がありません。英国の犯罪調査では、ドアと窓の鍵に屋外の照明などを組み合わせた家は、何も対策がない家より侵入被害から20倍以上守られていました。</p>'
 + '<table class="bt-t"><caption class="bt-sub">空き巣の下見と、家でできること</caption><thead><tr><th>空き巣が見ること</th><th>家でできること</th></tr></thead><tbody>'
 '<tr><td>留守か（インターホン・郵便受け）</td><td>新聞と郵便を止める、隣に伝える、外出中の写真は帰ってから載せる</td></tr>'
 '<tr><td>入りやすいか（死角・足場）</td><td>植木を剪定する、足場になる物を片付ける、合鍵を外に置かない</td></tr>'
 '<tr><td>時間がかかるか（鍵）</td><td>短い外出でも鍵を全部かける、補助の鍵と雨戸を使う</td></tr>'
 '<tr><td>逃げやすいか（人通り・近所の目）</td><td>近所の人にあいさつする</td></tr></tbody></table>'
 + '<div class="bt-note">戸締まり・見通し・手入れ・被害後の備えを、犯罪学の4原則でもう少しくわしく確かめたいときは、<a href="https://hanzaigaku.seadice.win/bouhan-check/">自宅の防犯チェック（18項目）</a>を使えます。</div>'
 + faq_html(AM_FAQ) + other_tools("akisu-me")
 + '<div class="sources"><h2>出典</h2><ol>'
 '<li>警察庁「住まいる防犯110番 侵入者プロファイリング（心理と行動）」 <a href="https://www.npa.go.jp/safetylife/seianki26/theme_a/a_e_1.html" rel="noopener">https://www.npa.go.jp/safetylife/seianki26/theme_a/a_e_1.html</a></li>'
 '<li>警察庁「住まいる防犯110番 データで見る侵入犯罪の脅威」（令和7年のデータ） <a href="https://www.npa.go.jp/safetylife/seianki26/theme_a/a_b_1.html" rel="noopener">https://www.npa.go.jp/safetylife/seianki26/theme_a/a_b_1.html</a></li>'
 '<li>警察庁「住まいる防犯110番 手口で見る侵入犯罪の脅威」 <a href="https://www.npa.go.jp/safetylife/seianki26/theme_a/a_d_1.html" rel="noopener">https://www.npa.go.jp/safetylife/seianki26/theme_a/a_d_1.html</a></li>'
 '<li>Townsley, M., et al. (2015). Burglar target selection: A cross-national comparison. <i>Journal of Research in Crime and Delinquency</i>, 52(1), 3-31. <a href="https://pmc.ncbi.nlm.nih.gov/articles/PMC4361488/" rel="noopener">https://pmc.ncbi.nlm.nih.gov/articles/PMC4361488/</a></li>'
 '<li>Tseloni, A., Thompson, R., Grove, L., Tilley, N., &amp; Farrell, G. (2017). The effectiveness of burglary security devices. <i>Security Journal</i>, 30(2), 646-664. <a href="https://doi.org/10.1057/sj.2014.30" rel="noopener">https://doi.org/10.1057/sj.2014.30</a></li>'
 '<li>個々の数字の出典は、各解説記事の末尾にあります。</li></ol></div>'
 + "<script>(function(){var D=" + am_data.replace("</", "<\\/") + r""";
function e(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function it(i){var d=D.items[i];return '<div class="bt-item"><b>'+e(d[1])+'</b>'+e(d[2])+'<span class="bt-sub" style="display:block">所要 '+e(d[3])+' ・ <a href="/'+d[5]+'/">'+e(d[6])+'</a></span></div>'}
document.getElementById('am').addEventListener('submit',function(){
 var ids=[].map.call(document.querySelectorAll('#am input:checked'),function(i){return i.value}),near=ids.indexOf('a1')>=0,o=document.getElementById('am-out');
 ids=ids.filter(function(i){return D.items[i]});
 var memo=D.stages.map(function(s){var n=ids.filter(function(i){return D.items[i][0]===s[0]}).length;
  return '<div class="bt-item"><b>'+e(s[1])+'：'+(n?e(s[2])+'（隙 '+n+'）':e(s[3]))+'</b></div>'}).join('');
 var h='<div class="bt-card'+(ids.length?' alert':'')+'"><h3>空き巣の下見メモ</h3>'+memo
  +'<p style="margin-top:10px">'+(ids.length?'空き巣の目には、隙が <strong>'+ids.length+' か所</strong>見えます。下の「先に直す3つ」から始めてください。':'選んだ中に、外から見える隙はありませんでした。ただし、この点検に無い隙もあります。短い外出でも鍵をかける習慣を続けてください。')+'</p></div>';
 if(near)h+='<div class="bt-card alert"><h3>いまは警戒期間です</h3><p>空き巣は、一度成功した家や、その近くに戻ってくることがあります。英国の研究では、被害の後1〜2か月の間、300〜400メートル以内の家でも危険が高まっていました。この期間は、出かける前の施錠確認を声に出して行い、窓と鍵を見直します。 <a href="/'+D.near[0]+'/">'+e(D.near[1])+'</a></p></div>';
 if(ids.length){var s=ids.slice().sort(function(a,b){return D.items[a][4]-D.items[b][4]});
  h+='<div class="bt-card"><h3>先に直す3つ（手間の小さい順）</h3>'+s.slice(0,3).map(it).join('')+'</div>';
  if(s.length>3)h+='<div class="bt-card"><h3>ほかの隙と直し方</h3>'+s.slice(3).map(it).join('')+'</div>'}
 h+='<div class="bt-card"><h3>毎日の点検はこちら</h3><p>家の隙を直したら、あとは出かけるたびの戸締まりです。外出の長さに合わせて玄関・窓・郵便受け・SNSをタップで確かめ、点検した時刻を残せます。外で「鍵閉めたっけ？」と思ったら、戻る前に記録を見るだけ。 <a href="https://seadice.win/tools/dekakeru-mae-tenken/">出かける前の30秒点検</a></p></div>';
 o.innerHTML=h;o.hidden=false;o.scrollIntoView({behavior:'smooth',block:'start'});
});})();</script>""")

# ---- 一人暮らしの防犯チェック ----
# 一人暮らしの記事（住まい・帰り道・在宅中・SNS）の「今日からできること」から、当てはまる隙を選ぶ。
# 並べ方: 警察庁・警視庁の統計で多い手口（鍵のかけ忘れ・玄関・窓・合かぎ・後ろから押し入る）に当たるものを先に、同じなら手間の小さい順。順番はSEADICEが決めた。
# (id, 場面, 当てはまる隙, 直し方, 所要, 優先(1が先), 並べ替え用の秒数, 記事slug)
HITORI = [
    ("e1", "sumai", "今の部屋に入居したとき、鍵を交換したかを確かめていない",
     "管理会社や大家さんに、入居前に鍵を交換したかを聞きます。交換していなければ相談します。", "10分", 2, 600, "moving-new-home-security"),
    ("e2", "sumai", "入居してから、すべての窓とベランダの鍵がきちんとかかるかを確かめていない",
     "すべての窓とドアの鍵がきちんとかかるかを、一度ずつ確かめます。", "10分", 3, 600, "moving-new-home-security"),
    ("e3", "sumai", "合鍵を、郵便受け・メーターボックス・植木鉢の下など、部屋の外に置いている",
     "合鍵は外に置かず、本数を最小限にして持ち歩きます。侵入者はこうした隠し場所をよく見ています。", "1分", 2, 60, "auto-lock-apartment-burglary"),
    ("e4", "sumai", "1〜3階に住んでいて、ベランダの外に登れる物（共用階段・縦樋・物置・塀）や、道路から見えない死角がないかを確かめていない",
     "ベランダから外を見て、登れる物と死角を確かめます。外出するときと寝る前は、ベランダ側の窓に鍵をかけます。福岡市の集合住宅の研究では、3階以下の部屋の被害率は4階以上の4倍以上でした。", "3分", 2, 180, "living-alone-floor-level-safety"),
    ("k1", "kaeri", "玄関の鍵を開ける前に、周りを見回していない",
     "鍵を開ける前に振り返り、誰かがいたら一度通り過ぎます。後ろから押し入られるのを防ぐために、警視庁が勧めている方法です。", "5秒", 1, 5, "living-alone-women-home-safety"),
    ("k2", "kaeri", "オートロックの入口を、知らない人と一緒に通ることがある",
     "知らない人が後ろから続いて入ろうとしたら、先に通してから入るか、その場を離れます。", "数秒", 2, 5, "auto-lock-apartment-burglary"),
    ("k3", "kaeri", "暗い道や人通りの少ない道でも、スマホを見ながら歩く",
     "暗い道や街灯の少ない道に入る手前で、スマホをポケットやバッグにしまいます。画面に集中していると、周りの景色や音に気づきにくくなります。", "0分", 3, 0, "night-walking-smartphone-awareness-risk"),
    ("k4", "kaeri", "帰り道は、両耳のイヤホンで音楽や動画を聞いている",
     "片耳だけにするか音量を下げて、近づく足音や声が聞こえるようにします。", "10秒", 3, 10, "night-walking-smartphone-awareness-risk"),
    ("k5", "kaeri", "近道なら、暗い道でも通る",
     "暗い近道より、街灯と人通りのある大通りを選びます。イギリスの研究では、同じ時間帯でも暗くなると対人強盗が約1.87倍でした。", "0分", 3, 0, "night-darkness-robbery-risk"),
    ("k6", "kaeri", "毎日ほぼ同じ時間に、同じ道で帰っている",
     "帰る道や時間を時々変えます。決まった時間と道を避けると、待ち伏せを避けやすくなります。", "0分", 3, 0, "stalking-acquaintance-consultation"),
    ("k7", "kaeri", "いつもの帰り道で、夜も開いている店や交番がどこにあるかを知らない",
     "帰り道を一度地図で見て、夜も開いている店と交番を覚えます。後をつけられていると感じたら、家が近くても帰らず、そこに入って助けを求めるか110番します。", "10分", 2, 600, "being-followed-walking-home"),
    ("h1", "heya", "部屋にいるときは、玄関の鍵やドアガードをかけていない",
     "帰ったらすぐに鍵とドアガードをかけます。警視庁は、オートロックや高い階でも玄関と窓を必ず施錠するよう呼びかけています。", "5秒", 1, 5, "living-alone-women-home-safety"),
    ("h2", "heya", "「高い階だから」と、ベランダの窓を開けたまま寝たり出かけたりする",
     "外出するときと寝る前は、高い階でもベランダの窓に鍵をかけます。共同住宅の侵入口の2位は窓です。", "10秒", 1, 10, "auto-lock-apartment-burglary"),
    ("h3", "heya", "知らない訪問者にも、ドアを開けて対応する",
     "インターホン越しに名前と用件を聞き、開けるときもドアガードをかけたままにします。業者や役所を名乗られても、すぐには開けません。", "1分", 2, 60, "home-invasion-robbery-at-home"),
    ("h4", "heya", "夜、カーテンに隙間がある。または玄関ドアの郵便受けから部屋の中が見える",
     "カーテンは隙間なく閉めます。のぞきは、カーテンのわずかな隙間や郵便受けから部屋をのぞきます。", "10秒", 3, 10, "living-alone-crime-methods"),
    ("h5", "heya", "下着を、外から見える形でベランダや庭に干している",
     "下着は室内か、バスタオルなどの内側に干します。宮城県警察が下着泥棒の対策として挙げている方法です。", "0分", 3, 0, "mens-laundry-fake-occupancy-myth"),
    ("n1", "dekake", "ゴミ出しや近所への買い物くらいなら、鍵をかけずに出かける",
     "数分の外出でも、玄関と窓の鍵をかけます。鍵のかけ忘れは、共同住宅で1番多い侵入手口です。", "10秒", 1, 10, "burglar-target-selection-5-minutes"),
    ("n2", "dekake", "外出先の写真を、出かけている間にSNSに載せる",
     "写真は帰ってから載せます。「いま家を空けている」ことを知らせずに済みます。", "0分", 3, 0, "sns-photo-location-home"),
    ("n3", "dekake", "窓からの景色・玄関・近所の店が写った写真を、SNSに載せている",
     "家の周りが写った写真は載せないか、写らないように撮ります。AIは景色だけで撮影場所を推定できるようになっています。", "毎回", 3, 30, "sns-photo-location-home"),
    ("n4", "dekake", "スマホのカメラの位置情報を、オフにしたか確かめていない",
     "カメラの設定で、写真に位置情報を付けないようにします。", "3分", 3, 180, "sns-photo-location-home"),
    ("n6", "dekake", "郵便物やDMを、宛名が読めるまま捨てている",
     "宛名の部分を細かく切ってから捨てます。郵便受けにも鍵をかけて、名前を見られないようにします。", "1分", 3, 60, "living-alone-crime-methods"),
    ("n5", "dekake", "警察相談専用電話 #9110 を、スマホに登録していない",
     "緊急ではない段階でも相談できる番号です。登録しておけば「大げさかも」と迷ったときにすぐかけられます。身の危険を感じたら110番です。", "1分", 3, 60, "stalking-acquaintance-consultation"),
]
HITORI_SCENES = [
    ("sumai", "1. 住まいと鍵", "入居したときの鍵と合鍵です。4階建以上の共同住宅では、合かぎが2番目に多い侵入手口でした。"),
    ("kaeri", "2. 帰り道と玄関", "後をつけて、玄関を開けた瞬間に押し入る手口があります。帰り道と、鍵を開けるまでの数秒を見ます。"),
    ("heya", "3. 部屋にいるとき", "「家にいれば大丈夫」とは限りません。在宅中に押し入る侵入強盗は、令和7年に前の年より13.2%増えました。"),
    ("dekake", "4. 出かけるとき・SNS", "短い外出の鍵と、SNSから留守や住まいが伝わらないかを見ます。"),
]
# 住まいの種類ごとの侵入手口（警察庁、令和7年のデータ）。選ぶと結果の冒頭に出し、4階建以上は合鍵の項目を先にする
HITORI_HOUSE = [
    ("apt", "アパート（3階建まで）", "3階建以下の共同住宅では、侵入手口の1位は鍵のかけ忘れ（47.4%）で、ガラス破り、合かぎ（12.9%）が続きます。侵入口の1位は玄関です。", []),
    ("mansion", "マンション（4階建以上）", "4階建以上の共同住宅でも、侵入手口の1位は鍵のかけ忘れ（39.5%）、2位は合かぎ（24.6%）です。オートロックがあっても、侵入口の1位は玄関です。", ["e1", "e3"]),
    ("house", "一戸建て", "一戸建てでは、ガラス破り（42.2%）と鍵のかけ忘れ（41.5%）が2大手口です。窓と、短い外出の鍵を先に見直します。", []),
]
HG_FAQ = [
    ("一人暮らしの防犯で、いちばん大事なことは何ですか？",
     "部屋にいるときも、数分の外出でも、玄関と窓の鍵をかけることです。共同住宅では、鍵のかけ忘れが1番多い侵入手口で、侵入口の1位は玄関でした（警察庁、令和7年）。オートロックや高い階でも、警視庁は玄関と窓を必ず施錠するよう呼びかけています。"),
    ("オートロックのマンションなら安全ですか？",
     "オートロックだけでは防げません。4階建以上の共同住宅でも、侵入手口の1位は鍵のかけ忘れ、2位は合かぎでした。オートロックは建物の鍵、部屋の鍵は別と考えて、毎回かけます。"),
    ("一人暮らしの部屋選びで、防犯のために見るところは？",
     "建物の入口の見通し、共用部の明るさ、窓の外に足場がないか、カメラ付きドアホンがあるかです。入居したら、鍵を交換したかを管理会社や大家さんに確かめます。"),
    ("選んだ内容はどこかに送られますか？",
     "送られません。結果はすべてブラウザの中で出します。前回と比べるために、選んだ項目と日付だけをこのブラウザに保存します。「記録を消す」で消せます。"),
]
HG_CSS = (".hg-chips{display:flex;flex-wrap:wrap;gap:8px;padding:4px 0 12px}"
          ".bt-box .hg-chips label{position:relative;display:inline-flex;align-items:center;gap:0;border:1px solid var(--border);border-radius:8px;padding:0 14px;min-height:44px;font-size:15px;background:var(--bg)}"
          ".hg-chips input{position:absolute;opacity:0;width:1px;height:1px}"
          ".bt-box .hg-chips label:has(input:checked){border-color:var(--accent);box-shadow:inset 0 0 0 1px var(--accent);font-weight:700}"
          ".hg-chips label:has(input:focus-visible){outline:2px solid var(--accent);outline-offset:2px}"
          ".hg-prev{font-size:14px;margin:0 0 4px}.hg-acts{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}"
          ".hg-acts button{min-height:44px;padding:0 14px;border:1px solid var(--border);border-radius:8px;background:var(--bg);color:var(--text);font:inherit;font-size:14px;cursor:pointer}")


def _hg_row(i, t):
    return f'<label><input type="checkbox" value="{i}"><span>{E(t)}</span></label>'


hg_rows = ('<h2>どこに住んでいますか</h2><div class="hg-chips" role="radiogroup" aria-label="住まいの種類">'
           + "".join(f'<label><input type="radio" name="hg-house" value="{k}">{E(l)}</label>' for k, l, _, _ in HITORI_HOUSE)
           + "</div>")
hg_rows += "".join(
    f'<h2>{E(sl)}</h2><p class="bt-sub" style="padding:0 4px 6px">{E(sd)}</p>'
    + "".join(_hg_row(i, t) for i, g, t, *_ in HITORI if g == sk)
    for sk, sl, sd in HITORI_SCENES)
hg_data = json.dumps({"items": {i: [g, t, f, m, p, sec, s, TITLES.get(s, s)] for i, g, t, f, m, p, sec, s in HITORI},
                      "scenes": [[k, l.split(". ")[1]] for k, l, _ in HITORI_SCENES],
                      "house": {k: [l, d, up] for k, l, d, up in HITORI_HOUSE}}, ensure_ascii=False)
hg_body = (ld("一人暮らしの防犯チェック", "hitorigurashi",
              "一人暮らしの住まい・帰り道・部屋にいるとき・出かけるときとSNSの22項目から当てはまる隙を選ぶと、いちばん気をつけたい場面と、統計をもとに優先した今週やること3つがわかる無料チェック。警察庁・警視庁の統計と研究にもとづく。登録不要・広告なし。", HG_FAQ)
 + '<p>一人暮らしの防犯は、何から始めればいいのでしょうか。住まい・帰り道・部屋にいるとき・出かけるときの4つの場面で、<strong>当てはまるものを選んでください</strong>。警察の統計で多い手口に当たる隙から順に、<strong>今週やること3つ</strong>を出します。無料・登録不要で、選んだ内容はどこにも送られません。</p>'
 + f'<form class="bt-box" id="hg" onsubmit="return false"><p class="hg-prev" id="hg-prev" hidden></p>{hg_rows}<button type="submit" class="bt-btn">今週やること3つを見る</button><noscript><p class="bt-sub">結果を出すにはJavaScriptが必要です。下の「やることの並べ方」と例の表は、そのまま読めます。</p></noscript></form>'
 + '<div class="bt-res" id="hg-out" aria-live="polite" hidden></div>'
 + '<p class="answer"><strong>結論：一人暮らしの防犯は、まず「部屋にいるときも、短い外出でも鍵をかける」と「玄関を開ける前に振り返る」です。</strong>共同住宅の侵入手口の1位は鍵のかけ忘れで、オートロックや高い階でも変わりません。どれもお金はかかりません。</p>'
 + '<h2>やることの並べ方</h2><p>選んだ隙は、次の順に並べます。警察庁と警視庁の統計で多い手口（鍵のかけ忘れ・玄関・窓・後ろから押し入る）に当たるものを先にし、合鍵やオートロック、訪問者への対応が続きます。同じ段階の中では、手間の小さい順です。この順番は、統計をもとにSEADICEが決めたもので、あなたの部屋の危なさを測ったものではありません。</p>'
 + '<table class="bt-t"><caption class="bt-sub">住まいの種類と、多い侵入手口（警察庁、令和7年のデータ）</caption><thead><tr><th>住まい</th><th>多い侵入手口</th></tr></thead><tbody>'
 '<tr><td>共同住宅（3階建以下）</td><td>1位 鍵のかけ忘れ（47.4%）、ガラス破り、合かぎ（12.9%）。侵入口の1位は玄関</td></tr>'
 '<tr><td>共同住宅（4階建以上）</td><td>1位 鍵のかけ忘れ（39.5%）、2位 合かぎ（24.6%）。侵入口の1位は玄関</td></tr>'
 '<tr><td>一戸建て</td><td>ガラス破り（42.2%）と鍵のかけ忘れ（41.5%）</td></tr></tbody></table>'
 + '<h2>使い方の例</h2><table class="bt-t"><thead><tr><th>選んだもの</th><th>今週やること3つ</th></tr></thead><tbody>'
 '<tr><td>マンション（4階建以上）／合鍵をメーターボックスに置いている／玄関の前で振り返らない／ベランダの窓を開けて寝る</td>'
 '<td>1. 玄関の鍵を開ける前に振り返る（5秒）<br>2. 寝る前にベランダの窓に鍵をかける（10秒）<br>3. 合鍵を外に置かず持ち歩く（1分）</td></tr></tbody></table>'
 + '<div class="bt-note">家の外から見える隙（郵便受け・死角・足場）は<a href="/akisu-me/">空き巣の目で、わが家を点検</a>で、出かけるたびの戸締まりは<a href="https://seadice.win/tools/dekakeru-mae-tenken/">出かける前の30秒点検</a>で確かめられます。</div>'
 + faq_html(HG_FAQ) + other_tools("hitorigurashi")
 + '<div class="sources"><h2>出典</h2><ol>'
 '<li>警察庁「住まいる防犯110番 手口で見る侵入犯罪の脅威」（令和7年のデータ） <a href="https://www.npa.go.jp/safetylife/seianki26/theme_a/a_d_1.html" rel="noopener">https://www.npa.go.jp/safetylife/seianki26/theme_a/a_d_1.html</a></li>'
 '<li>警察庁「住まいる防犯110番」侵入窃盗の発生状況・手口 <a href="https://www.npa.go.jp/safetylife/seianki26/theme_a/a_d_1_main.html" rel="noopener">https://www.npa.go.jp/safetylife/seianki26/theme_a/a_d_1_main.html</a></li>'
 '<li>警察庁「住まいる防犯110番 共同住宅の防犯関係基準」 <a href="https://www.npa.go.jp/safetylife/seianki26/theme_c/c_b_1.html" rel="noopener">https://www.npa.go.jp/safetylife/seianki26/theme_c/c_b_1.html</a></li>'
 '<li>警視庁「令和7年版 東京の犯罪」 <a href="https://www.keishicho.metro.tokyo.lg.jp/about_mpd/jokyo_tokei/jokyo/hanzai.files/tokyo.pdf" rel="noopener">https://www.keishicho.metro.tokyo.lg.jp/about_mpd/jokyo_tokei/jokyo/hanzai.files/tokyo.pdf</a></li>'
 '<li>個々の研究と数字の出典は、各解説記事の末尾にあります。</li></ol></div>'
 + "<script>(function(){var D=" + hg_data.replace("</", "<\\/") + r""",K='bohan-hitorigurashi',f=document.getElementById('hg'),o=document.getElementById('hg-out'),prev=null;
function e(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function ld(){try{return JSON.parse(localStorage.getItem(K))}catch(x){return null}}
function sv(v){try{v?localStorage.setItem(K,JSON.stringify(v)):localStorage.removeItem(K)}catch(x){}}
function md(t){var d=new Date(t);return (d.getMonth()+1)+'月'+d.getDate()+'日'}
function it(i){var d=D.items[i];return '<div class="bt-item"><b>'+e(d[1])+'</b>'+e(d[2])+'<span class="bt-sub" style="display:block">所要 '+e(d[3])+' ・ <a href="/'+d[6]+'/">'+e(d[7])+'</a></span></div>'}
prev=ld();
if(prev&&prev.ids){if(prev.h){var r0=f.querySelector('input[name=hg-house][value="'+prev.h+'"]');if(r0)r0.checked=true}prev.ids.forEach(function(i){var c=f.querySelector('input[value="'+i+'"]');if(c)c.checked=true});
 var p=document.getElementById('hg-prev');p.textContent='前回（'+md(prev.t)+'）の答えを入れてあります。直したものは外してから、もう一度見てください。';p.hidden=false}
f.addEventListener('submit',function(){
 var hc=f.querySelector('input[name=hg-house]:checked'),h=hc&&D.house[hc.value],up=h?h[2]:[];
 var ids=[].map.call(f.querySelectorAll('input[type=checkbox]:checked'),function(i){return i.value}).filter(function(i){return D.items[i]});
 function pr(i){return up.indexOf(i)>=0?1:D.items[i][4]}
 var s=ids.slice().sort(function(a,b){return pr(a)-pr(b)||D.items[a][5]-D.items[b][5]}),r='';
 if(h)r+='<div class="bt-card"><h3>'+e(h[0])+'で多い手口</h3><p>'+e(h[1])+'</p></div>';
 var w=D.scenes.map(function(c){var n=ids.filter(function(i){return D.items[i][0]===c[0]});return [c[1],n.length,n.reduce(function(a,i){return a+4-pr(i)},0)]}),top=w.slice().sort(function(a,b){return b[2]-a[2]})[0];
 r+='<div class="bt-card'+(ids.length?' alert':'')+'"><h3>'+(ids.length?'いちばん気をつけたい場面：'+e(top[0]):'当てはまるものは選ばれませんでした')+'</h3>'
  +w.map(function(c){return '<div class="bt-item"><b>'+e(c[0])+'：'+(c[1]?'隙 '+c[1]+' か所':'隙なし')+'</b></div>'}).join('')
  +(prev&&prev.ids?'<p style="margin-top:10px">前回（'+md(prev.t)+'）は隙 '+prev.ids.length+' か所、今回は '+ids.length+' か所です。'+(prev.ids.length>ids.length?(prev.ids.length-ids.length)+' か所減りました。':'')+'</p>':'')
  +(ids.length?'':'<p style="margin-top:10px">当てはまるものがなければ、このチェックの範囲では隙は見つかりませんでした。ただし、このチェックにない隙もあります。部屋にいるときも鍵をかける習慣を続けてください。</p>')+'</div>';
 if(s.length){r+='<div class="bt-card"><h3>今週やること3つ</h3>'+s.slice(0,3).map(it).join('')+'</div>';
  if(s.length>3)r+='<details><summary>ほかの隙と直し方（'+(s.length-3)+'）</summary>'+s.slice(3).map(it).join('')+'</details>'}
 r+='<div class="bt-card"><h3>困ったときの連絡先</h3><ul class="bt-contact"><li>いま身の危険がある：<a href="tel:110">110番</a></li><li>つきまといや不審な人のことを相談したい：<a href="tel:%239110">#9110</a></li></ul>'
  +'<div class="hg-acts"><button type="button" id="hg-copy">やることをコピー</button><button type="button" id="hg-del">記録を消す</button></div></div>';
 o.innerHTML=r;o.hidden=false;
 var now={t:Date.now(),ids:ids,h:hc?hc.value:''};sv(now);prev=now;
 document.getElementById('hg-copy').onclick=function(){var t='一人暮らしの防犯チェック（'+md(now.t)+'）\n'+s.map(function(i,n){return (n+1)+'. '+D.items[i][2]}).join('\n');
  var bt=this;try{navigator.clipboard.writeText(t).then(function(){bt.textContent='コピーしました'},function(){bt.textContent='コピーできませんでした'})}catch(x){bt.textContent='コピーできませんでした'}};
 document.getElementById('hg-del').onclick=function(){sv(null);prev=null;this.textContent='消しました';document.getElementById('hg-prev').hidden=true};
 o.scrollIntoView({behavior:'smooth',block:'start'});
});})();</script>""")

# ---- そのリンクちょっと待った（リンクの詐欺チェック） ----
# 判定は url-check-worker の /web（詐欺リスト・日本でよく見られているサイト・偽ドメインの点検 → AI）。アプリ link_matta と同じ判定
LC_API = "https://url-check.seadice-home.workers.dev"
LC_FAQ = [
    ("届いたSMSのリンクが本物か、どうやって確かめればいいですか？",
     "リンクは押さずに、この欄に文ごと貼って確かめます。結果が「開いて大丈夫そうです」でも、ログインや支払いは、いつも使う公式アプリかブックマークから入るのが確実です。宅配・カード会社・携帯会社を名乗るSMSは、名乗った会社と行き先のドメインが合っているかが一番の手がかりです。"),
    ("「開いて大丈夫そうです」と出たら安全ですか？",
     "安全の保証ではありません。新しく作られたばかりの詐欺サイトは、どの一覧にもまだ載っていないことがあります。IDやカード番号を求められたら、届いたリンクからではなく公式アプリから入り直してください。"),
    ("貼った文やURLはどこに送られますか？",
     "確かめるURLと貼った文を、SEADICEの判定サーバー（Cloudflare）に送り、判定のためにAI（AnthropicのClaude）にも渡します。電話番号・メールアドレス・8けた以上の数字は、送る前にこのブラウザの中で伏せます。氏名・住所やURLの中の文字は伏せられないので、貼る前に消してください。判定サーバーは中身を保存せず、ログにも残しません。この画面にも履歴は残りません。「中身を見てくる」を押したときだけ、サーバーがリンク先のページを読みに行き、ドメインの登録日を公開の登録情報（RDAP）に問い合わせます。"),
    ("リンクを開いてしまった・情報を入れてしまったときは？",
     "パスワードを入れたなら、すぐ公式サイトや公式アプリからパスワードを変え、同じパスワードを使っているほかのサービスも変えます。カード番号を入れたなら、カード会社に連絡して止めてもらいます。迷ったら警察相談専用電話 #9110 か消費者ホットライン 188 に相談してください。"),
    ("「中身を見てくる」とは何ですか？",
     "SEADICEのサーバーが代わりにリンク先のページを文字だけ読み、どんなサイトか、パスワードやカード番号の入力欄があるか、いつ作られたドメインかをAIがまとめます。あなたの端末ではページを開きません。ボタンを押したときだけ読みに行きます（読みに行くと、相手のサーバーには誰かが開いたことが伝わるためです）。"),
]
lc_body = (ld("そのリンクちょっと待った（リンクの詐欺チェック）", "link-check",
              "届いたSMS・LINE・メールのリンクを貼ると、詐欺サイトの報告一覧・会社名を借りた偽ドメイン・短縮URLの行き先を点検し、AIが危険度0〜100と理由を返す無料ツール。登録不要・広告なし。", LC_FAQ)
 + '<p>SMS・LINE・メールで届いたリンクを、押す前にここに貼ってください。リンクだけでも、届いた文ごとでもかまいません。危険度を0〜100で出し、「開いて大丈夫そうです」「ちょっと待った」「開かないで」のどれかと、その理由を返します。無料・登録不要です。</p>'
 + '<form class="bt-box" id="lc" onsubmit="return false"><label for="lc-in" style="border:0;padding:0 0 8px;display:block;font-weight:700">届いたリンク、または文ごと</label>'
 '<textarea id="lc-in" rows="5" maxlength="1500" required placeholder="例）お荷物をお届けにあがりましたが不在の為持ち帰りました。配送物は下記よりご確認ください。https://…" '
 'style="width:100%;min-height:120px;padding:12px;border:1px solid var(--border);border-radius:10px;background:var(--bg);color:var(--text);font:inherit;font-size:16px;line-height:1.7"></textarea>'
 '<button type="submit" class="bt-btn" id="lc-go">このリンクを確かめる</button>'
 '<p class="bt-sub" style="margin-bottom:10px">確かめるURLと文を、SEADICEの判定サーバーとAI（Claude）に送ります。電話番号・メールアドレス・長い数字は送る前に伏せます。氏名・住所は貼る前に消してください。サーバーには保存しません。</p></form>'
 + '<div class="bt-res" id="lc-out" aria-live="polite" hidden></div>'
 + '<p class="answer"><strong>結論：届いたリンクは、押す前に「名乗っている会社」と「行き先のドメイン」が合っているかを見ます。</strong>合っていなければ開かず、公式アプリやブックマークから確かめます。このチェックは、その見比べと詐欺の報告一覧の照合を代わりに行います。</p>'
 + '<h2>判定のしかた</h2><ol class="bt-note" style="padding-left:2.2em">'
 '<li><b>詐欺の報告一覧と照らし合わせる</b>：フィッシングに使われたと報告されたサイト約5万件（Phishing.Database、毎日更新）と、日本でよく見られているサイト約7万件（Chrome UX Report の上位10万件から、誰でもページを置ける場所を除いたもの）。</li>'
 '<li><b>URLの書き方を点検する</b>：amazon・rakuten・sagawa などの会社名を借りた別のドメイン、1文字だけ変えたつづり、日本の会社がまず使わない末尾（.top・.cn など）、「@」入り、番号だけ、暗号化なし（http）。短縮URLは、短縮サービスにだけ問い合わせて最後の行き先までたどります（受け取った人ごとに作られた短縮URLだと、問い合わせたことが送り主に伝わる場合があります）。</li>'
 '<li><b>AIが文の言い方も読む</b>：「お荷物を持ち帰りました」「未払い」「本日中」のような、急がせる・不安にさせる言い方と行き先を合わせて、危険度とひとことの理由を出します。詐欺の報告一覧に載っていれば、AIが低く言っても危険度90以上にします。</li></ol>'
 + '<h2>どれくらい当たるか</h2><p>同じ判定を、JPCERT/CCが公開した日本のフィッシングURL（2026年3〜5月の一覧）のうち、4〜5月の200件で試しました。「開いて大丈夫そうです」と出たものは0件、「開かないで」は31件で、残りの169件は「ちょっと待った」でした。日本でよく見られている正規のサイト100件では、97件が「開いて大丈夫そうです」、3件が「ちょっと待った」で、「開かないで」は0件でした。URLだけを渡した測定で、届いた文は使っていません。AIの答えは毎回少し変わるので、もう一度測ると数件ずれることがあります（SEADICE調べ、2026年10月）。</p><p><b>偽サイトの多くは「開かないで」ではなく「ちょっと待った」と出ます。</b>「ちょっと待った」が出たら、開かずに公式アプリやブックマークから確かめてください。</p>'
 + '<table class="bt-t"><caption class="bt-sub">入力例と結果の例</caption><thead><tr><th>貼ったもの</th><th>結果</th></tr></thead><tbody>'
 '<tr><td>「お荷物を持ち帰りました」＋ sagawa-exp.top のリンク</td><td>開かないで（社名を借りた別のドメイン・日本の会社がまず使わない末尾・急がせる文）</td></tr>'
 '<tr><td>詐欺の報告一覧に載っているサイト</td><td>開かないで（危険度90以上）</td></tr>'
 '<tr><td>bit.ly などの短縮URL</td><td>最後の行き先までたどって、行き先で判断</td></tr>'
 '<tr><td>https://www.amazon.co.jp/</td><td>開いて大丈夫そうです（公式ドメイン）</td></tr></tbody></table>'
 + '<h2>このチェックにできないこと</h2><ul class="bt-note" style="padding-left:2.2em">'
 '<li>「開いて大丈夫そうです」は安全の保証ではありません。作られたばかりの詐欺サイトを見逃すことがあります。</li>'
 '<li>電話・訪問・SNSのやりとりそのものは判定しません。連絡の内容が不安なら ' + '<a href="/sagi-check/">この連絡、詐欺かも？チェック</a> を使ってください。</li>'
 '<li>AIに聞ける回数には1日の上限があります。上限を超えたときは、一覧と書き方の点検だけで判断し、そのことを結果に書きます。このとき、日本でよく見られているサイト以外は「開いて大丈夫そうです」と出しません。</li></ul>'
 + faq_html(LC_FAQ) + other_tools("link-check")
 + '<div class="sources"><h2>出典</h2><ol>'
 '<li>JPCERT/CC「フィッシングURL」一覧（2026年3〜5月） <a href="https://github.com/JPCERTCC/phishurl-list" rel="noopener">https://github.com/JPCERTCC/phishurl-list</a></li>'
 '<li>Phishing.Database（MIT License） <a href="https://github.com/Phishing-Database/Phishing.Database" rel="noopener">https://github.com/Phishing-Database/Phishing.Database</a></li>'
 '<li>Chrome UX Report（Google、CC BY-SA 4.0）の上位サイト一覧 <a href="https://github.com/zakird/crux-top-lists" rel="noopener">https://github.com/zakird/crux-top-lists</a></li>'
 '<li>手口の解説と数字の出典は、' + art("phishing-mail-sms-2025") + ' と ' + art("qr-code-phishing-sticker") + ' の末尾にあります。</li></ol></div>'
 + "<script>(function(){var A=" + json.dumps(LC_API) + ",C=" + json.dumps(CONTACTS)
 + r""";
var U=/https?:\/\/[^\s<>"'「」（）()、。]+/gi,f=document.getElementById('lc'),t=document.getElementById('lc-in'),b=document.getElementById('lc-go'),o=document.getElementById('lc-out'),last=null;
function e(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function mk(s){return s.replace(/[\w.+-]+@[\w-]+\.[\w.-]+/g,'[メール]').replace(/\d[\d\- ]{6,}\d/g,'[番号]')}
function mask(s){var r='',l=0,m;U.lastIndex=0;while((m=U.exec(s))){r+=mk(s.slice(l,m.index))+m[0];l=m.index+m[0].length}return r+mk(s.slice(l))}
var W={safe:['開いて大丈夫そうです','#4FB37A'],wait:['ちょっと待った','#F2B33D'],stop:['開かないで','#E5534B']},L={danger:'危険',caution:'注意',info:'参考'};
function post(p,d){return fetch(A+p,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(d),signal:AbortSignal.timeout?AbortSignal.timeout(45000):undefined}).then(function(r){return r.json().then(function(j){if(!r.ok)throw j.error||'error';return j})})}
function err(x){return x==='no_url'?'リンクが見つかりませんでした。「https://」から始まるリンクか、届いた文ごと貼ってください。':(x==='rate_limited'?'続けて確かめすぎたため、少し休んでいます。1分ほど待ってからもう一度押してください。':'判定サーバーにつながりませんでした。入力はそのまま残っています。少し待ってからもう一度押してください。')}
function show(d){var w=W[d.verdict]||W.wait,h='<div class="bt-card'+(d.verdict==='stop'?' alert':'')+'" style="border-left-color:'+w[1]+'"><p class="bt-score">危険度 <b style="color:'+w[1]+'">'+d.risk+'</b> / 100</p><div class="bt-bar" role="img" aria-label="危険度 '+d.risk+'"><i style="width:'+d.risk+'%;background:'+w[1]+'"></i></div><h3 style="font-size:22px;margin:10px 0 4px">'+w[0]+'</h3>'
 +(d.headline?'<p><b>'+e(d.headline)+'</b></p>':'')+(d.reason?'<p>'+e(d.reason)+'</p>':'')
 +(d.ai?'':'<p class="bt-sub">AIに聞けなかったため、詐欺の報告一覧とURLの書き方の点検だけで判断しました。</p>')
 +'<p class="bt-sub" style="margin-top:8px;word-break:break-all">行き先：'+e(d.finalUri)+'</p></div>';
 if(d.chain&&d.chain.length>1)h+='<div class="bt-card"><h3>短縮URLの行き先</h3>'+d.chain.map(function(u,i){return '<div class="bt-item" style="word-break:break-all">'+(i?'→ ':'')+e(u)+'</div>'}).join('')+'</div>';
 if(d.findings.length)h+='<div class="bt-card"><h3>点検で見つかったこと</h3>'+d.findings.map(function(x){return '<div class="bt-item"><b>【'+L[x.level]+'】'+e(x.title)+'</b>'+e(x.detail)+'</div>'}).join('')+'</div>';
 else h+='<div class="bt-card"><h3>点検で見つかったこと</h3><p>'+(d.known?'日本でよく見られているサイトで、URLの書き方にも気になる点はありませんでした。':'詐欺の報告一覧にはなく、URLの書き方にも気になる点はありませんでした。ただし、日本でよく見られているサイトの一覧にもありません。名乗っている会社やお店と、行き先が合っているか確かめてください。')+'</p></div>';
 h+='<div class="bt-card" id="lc-in2"><h3>中身を見てくる</h3><p>SEADICEのサーバーが代わりにページを読み、どんなサイトか、パスワードやカード番号の入力欄があるかを確かめます。あなたの端末では開きません。</p><button type="button" class="bt-btn" id="lc-insp">中身を見てくる</button></div>';
 if(d.verdict!=='safe')h+='<div class="bt-card"><h3>迷ったら相談</h3>'+C+'</div>';
 o.innerHTML=h;o.hidden=false;o.scrollIntoView({behavior:'smooth',block:'start'});
 document.getElementById('lc-insp').addEventListener('click',inspect);}
function inspect(){var x=document.getElementById('lc-in2'),k=document.getElementById('lc-insp');k.disabled=true;k.textContent='ページを読んでいます…';
 post('/inspect',{uri:last.finalUri,prevRisk:last.risk,local:{level:last.level,known:last.known,findings:last.findings.map(function(f){return f.title})}}).then(function(r){var p=r.page||{},w=W[r.verdict]||W.wait,li=[];
  li.push(p.reached?'ページを読めました'+(p.title?'（'+e(p.title)+'）':''):'ページを読めませんでした（消えたか、読ませない作りです）');
  if(p.hasPassword)li.push('パスワードの入力欄があります');if(p.hasCard)li.push('カード番号の入力欄があります');
  if(p.formElsewhere&&p.formElsewhere.length)li.push('入力した内容を別のサイト（'+e(p.formElsewhere.join('・'))+'）に送る作りです');
  if(r.age&&r.age.days!=null)li.push('ドメインが作られたのは '+e(r.age.created)+'（'+r.age.days+'日前）');
  x.innerHTML='<h3>中身を見てきました：'+w[0]+'（危険度 '+r.risk+'）</h3>'+(r.summary?'<p>'+e(r.summary)+'</p>':'')+(r.reason?'<p>'+e(r.reason)+'</p>':'')+li.map(function(s){return '<div class="bt-item">'+s+'</div>'}).join('');
 }).catch(function(z){k.disabled=false;k.textContent='中身を見てくる';x.insertAdjacentHTML('beforeend','<p class="bt-sub">'+e(z==='daily_limit'?'今日の上限に達したため、中身を見に行けませんでした。':err(z))+'</p>')})}
f.addEventListener('submit',function(){var v=t.value.trim();if(!v){t.focus();return}
 b.disabled=true;b.textContent='確かめています…';
 post('/web',{text:mask(v)}).then(function(d){last=d;show(d)}).catch(function(z){o.innerHTML='<div class="bt-card alert"><p>'+e(err(z))+'</p></div>';o.hidden=false})
 .then(function(){b.disabled=false;b.textContent='このリンクを確かめる'})});
})();</script>""")

PAGES = [
    {"path": "akisu-me", "title": "空き巣の目で、わが家を点検",
     "seo_title": "空き巣に狙われやすい家 チェック｜空き巣の下見の目で、わが家の隙を点検（無料・登録不要）",
     "date": "2026-10-13",
     "desc": "空き巣は下見で「留守か・見られずに近づけるか・入るのに時間がかかるか」を見ます。その順にわが家の隙を選ぶと、空き巣から見た下見メモと、手間の小さい順の直し方がわかる。警察庁の資料と研究にもとづく無料ツール。",
     "body": am_body, "css": CSS + T_CSS},
    {"path": "hitorigurashi", "title": "一人暮らしの防犯チェック",
     "seo_title": "一人暮らし 防犯 チェック｜部屋選び・帰り道・在宅中の隙と、今週やること3つ",
     "date": "2026-10-26",
     "desc": "一人暮らしの防犯は何から？ 住まい・帰り道・部屋にいるとき・SNSの22項目から当てはまる隙を選ぶと、警察の統計をもとに優先した、今週やること3つがわかる。オートロックのマンションにも対応。無料・登録不要。",
     "body": hg_body, "css": CSS + T_CSS + HG_CSS},
    {"path": "sagi-check", "title": "この連絡、詐欺かも？チェック",
     "seo_title": "詐欺かも チェック｜電話・メール・SNSの連絡に当てはまるサインと、すぐやること（AI時代の手口に対応）",
     "date": "2026-10-11",
     "desc": "家族の声の電話、「警察です」の電話、LINEへの誘い、暗号資産の送金。当てはまるサインを選ぶと、すぐやることと解説記事がわかる。警察庁の統計と研究をもとにした無料・登録不要のチェック。",
     "body": sagi_body, "css": CSS + T_CSS},
    {"path": "link-check", "title": "そのリンクちょっと待った",
     "seo_title": "URL 詐欺 チェック｜届いたSMS・メールのリンクを開く前に、危険度をAIが判定（無料・登録不要）",
     "date": "2026-10-20",
     "desc": "「お荷物を持ち帰りました」のSMSのリンク、押す前に貼るだけ。詐欺の報告一覧5万件・会社名を借りた偽ドメイン・短縮URLの行き先を点検し、AIが危険度0〜100と理由を返します。無料・登録不要。",
     "body": lc_body, "css": CSS + T_CSS},
    {"path": "ai-tenken", "title": "AI時代の防犯 セルフ点検",
     "seo_title": "AI時代の防犯 セルフ点検｜パスワード・電話・SNS・AIチャット・家族の24項目（無料・登録不要）",
     "date": "2026-10-11",
     "desc": "自動更新、パスワードの使い回し、二段階認証、国際電話の休止、写真の位置情報、AIチャットへの入力、家族の合言葉。お金をかけずにできる24の対策を点検。進み具合は端末の中だけに保存。",
     "body": tk_body, "css": CSS + T_CSS},
    {"path": "aikotoba", "title": "家族の合言葉カード",
     "seo_title": "家族の合言葉 決め方｜AI音声のなりすまし詐欺に備える手順カード（印刷用・無料）",
     "date": "2026-10-11",
     "desc": "AIで作った偽物の声を見抜けたのは73%。声で判断せず、合言葉とかけ直しで確かめます。合言葉の決め方のチェックと、電話を受けたときの手順を書いた印刷用カード。",
     "body": ak_body, "css": CSS + T_CSS + ak_css},
]

# 記事 → ツール（extras.tool_links が記事の関連記事の直前に出す）。各ツールが根拠に使っている記事に付ける
LINKS = {}
for path, items, idx in (("/akisu-me/", AKISU + [AKISU_NEAR + ("", "", 0, AKISU_NEAR[2])], 6), ("/hitorigurashi/", HITORI, 7), ("/sagi-check/", SIGNS, 3), ("/ai-tenken/", TENKEN, 4)):
    name, what = {p: (n, d) for p, n, d in TOOLS}[path.strip("/")]
    for it in items:
        LINKS.setdefault(it[idx], [])
        if not any(x[0] == path for x in LINKS[it[idx]]):
            LINKS[it[idx]].append([path, name, what])
for s in ("ai-voice-clone-family-scam", "sns-video-voice-clone-risk"):
    LINKS.setdefault(s, []).insert(0, ["/aikotoba/"] + [[n, d] for p, n, d in TOOLS if p == "aikotoba"][0])
LINKS.setdefault("ai-era-scam-checklist", [])
for p, n, d in TOOLS:
    if not any(x[0] == "/" + p + "/" for x in LINKS["ai-era-scam-checklist"]):
        LINKS["ai-era-scam-checklist"].append(["/" + p + "/", n, d])
LC_ROW = ["/link-check/"] + [[n, d] for p, n, d in TOOLS if p == "link-check"][0]
for s in ("phishing-mail-sms-2025", "qr-code-phishing-sticker", "fake-shopping-site-checklist", "ai-written-phishing-email"):
    LINKS.setdefault(s, [])
    if not any(x[0] == "/link-check/" for x in LINKS[s]):
        LINKS[s].insert(0, LC_ROW)
# 本体（seadice.win）のツール。記事のツール枠の先頭に出す（toollinks.json を手で直すと次の書き出しで消えるため、ここに書く）
DEKAKE = ["https://seadice.win/tools/dekakeru-mae-tenken/", "出かける前の30秒点検",
          "玄関・窓・郵便受け・SNSを外出の長さに合わせてタップ点検。点検した時刻が残り、外で「鍵閉めたっけ？」と思ったら見るだけ"]
HONTAI = [
    (s, DEKAKE) for s in ("window-glass-breaking-burglary", "burglary-daylight-darkness-risk", "vacation-empty-home-burglary")
] + [
    ("sns-photo-location-home", ["https://seadice.win/tools/shashin-ichijoho-keshi/", "写真の位置情報けし",
                                 "SNSに上げる前に、写真に残った撮影場所（緯度・経度）を見せてから消す。写真は送らず端末の中だけで処理"]),
]
for s, row in HONTAI:
    LINKS.setdefault(s, []).insert(0, row)

if __name__ == "__main__":
    (ROOT / "media/bohan-pages.json").write_text(json.dumps(PAGES, ensure_ascii=False, indent=2) + "\n")
    (ROOT / "media/bohan-toollinks.json").write_text(json.dumps(LINKS, ensure_ascii=False, indent=1) + "\n")
    print(len(PAGES), "pages")
