"""独学の科学の印刷用テンプレート(/templates/ と /templates/{id}/)。dokugaku_tools.py が PAGES に足す。

方針:
- 1テンプレート1ページ。シート(.tp-sheet)は画面で書き込めて、そのまま印刷・PDF保存できる(@media print でシートだけを白地で出す)
- 根拠の数値は、出典照合済みの記事に書いてあるものだけを使う(記事を新しく読まずに数字を足さない)
- 入力はブラウザの中だけで扱い、保存も送信もしない
新しいテンプレートを足すときは T に1件追加し、ハブの一覧(HUB_ITEMS)にも並べる。
"""
import html
import json

E = html.escape
BASE = "https://dokugaku.seadice.win/"
PUB = {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}
PARENT = {"label": "勉強のテンプレート", "path": "/templates/"}
DATE = "2026-10-08"

SRC = {
    "cepeda": 'Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., &amp; Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. <i>Psychological Science</i>, 19(11), 1095–1102. <a href="https://doi.org/10.1111/j.1467-9280.2008.02209.x" rel="noopener">https://doi.org/10.1111/j.1467-9280.2008.02209.x</a>',
    "roediger": 'Roediger, H. L., &amp; Karpicke, J. D. (2006). Test-enhanced learning: Taking memory tests improves long-term retention. <i>Psychological Science</i>, 17(3), 249–255. <a href="https://doi.org/10.1111/j.1467-9280.2006.01693.x" rel="noopener">https://doi.org/10.1111/j.1467-9280.2006.01693.x</a>',
    "rowland": 'Rowland, C. A. (2014). The effect of testing versus restudy on retention: A meta-analytic review of the testing effect. <i>Psychological Bulletin</i>, 140(6), 1432–1463. <a href="https://doi.org/10.1037/a0037559" rel="noopener">https://doi.org/10.1037/a0037559</a>',
    "gollwitzer": 'Gollwitzer, P. M., &amp; Sheeran, P. (2006). Implementation intentions and goal achievement: A meta-analysis of effects and processes. <i>Advances in Experimental Social Psychology</i>, 38, 69–119. <a href="https://doi.org/10.1016/S0065-2601(06)38002-1" rel="noopener">https://doi.org/10.1016/S0065-2601(06)38002-1</a>',
    "duckworth": 'Duckworth, A. L., Grant, H., Loew, B., Oettingen, G., &amp; Gollwitzer, P. M. (2011). Self-regulation strategies improve self-discipline in adolescents: Benefits of mental contrasting and implementation intentions. <i>Educational Psychology</i>, 31(1), 17–26. <a href="https://doi.org/10.1080/01443410.2010.506003" rel="noopener">https://doi.org/10.1080/01443410.2010.506003</a>',
    "buehler": 'Buehler, R., Griffin, D., &amp; Ross, M. (1994). Exploring the “planning fallacy”: Why people underestimate their task completion times. <i>Journal of Personality and Social Psychology</i>, 67(3), 366–381. <a href="https://doi.org/10.1037/0022-3514.67.3.366" rel="noopener">https://doi.org/10.1037/0022-3514.67.3.366</a>',
    "kruger": 'Kruger, J., &amp; Evans, M. (2004). If you don’t want to be late, enumerate: Unpacking reduces the planning fallacy. <i>Journal of Experimental Social Psychology</i>, 40(5), 586–598. <a href="https://doi.org/10.1016/j.jesp.2003.11.001" rel="noopener">https://doi.org/10.1016/j.jesp.2003.11.001</a>',
    "harkin": 'Harkin, B., Webb, T. L., Chang, B. P. I., Prestwich, A., Conner, M., Kellar, I., Benn, Y., &amp; Sheeran, P. (2016). Does monitoring goal progress promote goal attainment? A meta-analysis of the experimental evidence. <i>Psychological Bulletin</i>, 142(2), 198–229. <a href="https://doi.org/10.1037/bul0000025" rel="noopener">https://doi.org/10.1037/bul0000025</a>',
}

CSS = (".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".note{background:rgba(90,176,255,.07);border:1px solid rgba(90,176,255,.25);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}.note a,.sources a,.xbody li a,.xbody p a{color:var(--link)}"
       ".rt-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.rt-t caption{text-align:left;font-size:13px;color:var(--muted);margin-bottom:6px}"
       ".rt-t th,.rt-t td{border:1px solid var(--border);padding:10px;text-align:left}.rt-t th{background:var(--card)}"
       "details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}summary{cursor:pointer;font-weight:700;font-size:15px}details p{font-size:15px;margin-top:8px}"
       ".sources{margin-top:48px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;word-break:break-all}"
       ".xbody ol.steps{margin:12px 0 12px 22px}.xbody ol.steps li{font-size:15px;margin:6px 0}"
       # 操作パネルと印刷ボタン
       ".tp-opt{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:16px 18px;margin:16px 0;display:grid;gap:8px}"
       ".tp-opt label{font-size:14px;font-weight:700}"
       ".tp-opt input,.tp-opt select{font:inherit;font-size:16px;padding:10px 12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);color-scheme:dark;min-height:46px;width:100%}"
       ".tp-bar{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0}"
       ".tp-btn{font:inherit;font-size:16px;font-weight:800;padding:13px 18px;border:0;border-radius:12px;background:var(--accent);color:#0B1020;cursor:pointer;min-height:48px}"
       ".tp-btn2{font:inherit;font-size:15px;font-weight:700;padding:12px 16px;border:1px solid var(--border);border-radius:12px;background:var(--card);color:var(--text);cursor:pointer;min-height:48px}"
       ".tp-btn:focus-visible,.tp-btn2:focus-visible{outline:2px solid var(--accent);outline-offset:3px}"
       ".tp-hint{font-size:13px;color:var(--muted);margin:0}"
       # 紙(画面では白い紙の見た目、印刷ではシートだけ)
       ".tp-sheet{background:#fff;color:#1d2330;border-radius:6px;padding:26px 22px;margin:8px 0 28px;box-shadow:0 8px 28px rgba(0,0,0,.4);font-size:14px;line-height:1.6;overflow-x:auto}"
       ".tp-sheet,.tp-sheet *{box-sizing:border-box}.tp-sheet *{color:inherit}.tp-pg+.tp-pg{margin-top:36px;padding-top:28px;border-top:2px dashed #c9ced8}"
       ".tp-h{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;border-bottom:2px solid #1d2330;padding-bottom:6px;margin-bottom:14px}"
       ".tp-h b{font-size:19px;letter-spacing:.04em}.tp-h span{font-size:12px;color:#55607a}"
       ".tp-sheet input,.tp-sheet textarea{font:inherit;font-size:16px;color:#1d2330;background:transparent;border:0;border-bottom:1px solid #9aa3b4;border-radius:0;width:100%;padding:4px 2px;min-height:34px}"
       ".tp-sheet input:focus{outline:2px solid #5AB0FF;outline-offset:1px}.tp-sheet input::placeholder{color:#a3abbb}"
       ".tp-sheet table{width:100%;border-collapse:collapse;margin:8px 0}.tp-sheet th,.tp-sheet td{border:1px solid #b9c0cc;padding:4px 6px;vertical-align:top;text-align:left}"
       ".tp-sheet th{background:#eef1f6;font-size:12px;font-weight:700}.tp-sheet td input{border-bottom:0;min-height:30px}"
       ".tp-lbl{font-size:12px;font-weight:700;color:#55607a;margin:12px 0 2px;display:block}"
       ".tp-ln{height:32px;border-bottom:1px solid #c4cad6}"
       ".tp-tip{font-size:12px;color:#55607a;background:#f4f6fa;border-radius:6px;padding:8px 10px;margin:10px 0}"
       ".tp-foot{display:flex;justify-content:space-between;gap:8px;font-size:10px;color:#7a8396;margin-top:14px;border-top:1px solid #dde1e8;padding-top:6px}"
       "@page{size:A4;margin:12mm}"
       "@media print{body>*:not(main),main>*:not(.xbody),.xbody>*:not(.tp-sheet){display:none!important}"
       "html,body,main,.xbody{padding:0!important;margin:0!important;max-width:none!important;width:auto!important}html,body{background:#fff!important;background-image:none!important}"".tp-sheet input[type=date]:invalid{color:transparent}.tp-sheet input::-webkit-calendar-picker-indicator{display:none}"
       ".tp-sheet{box-shadow:none;border-radius:0;padding:0 2px;margin:0;font-size:10.5pt;overflow:visible}.tp-sheet input{font-size:11pt;min-height:0}"
       ".tp-sheet input::placeholder{color:transparent}.tp-pg{break-after:page}.tp-pg:last-child{break-after:auto}.tp-pg+.tp-pg{margin-top:0;padding-top:0;border-top:0}"
       ".tp-sheet th{-webkit-print-color-adjust:exact;print-color-adjust:exact}.tp-noprint{display:none!important}}")

HOWTO = ('<h2>印刷・PDF保存のしかた</h2>'
         '<p>「印刷する・PDFで保存」を押すと、シートだけがA4・白地で印刷されます。画面で書き込んだ文字はそのまま印刷され、空欄は手書き用の線になります。</p>'
         '<ul class="steps"><li><strong>パソコン</strong>：印刷画面の送信先（プリンター）で「PDFに保存」を選ぶ</li>'
         '<li><strong>iPhone・iPad</strong>：プリント画面の右上の共有ボタンから「“ファイル”に保存」を選ぶ</li>'
         '<li><strong>Android</strong>：プリンターの選択で「PDF形式で保存」を選ぶ</li></ul>')


def lines(n):
    return '<div class="tp-ln"></div>' * n


def foot(path):
    return f'<div class="tp-foot"><span>独学の科学（SEADICE）</span><span>{BASE}{path}/</span></div>'


def faq_ld(faqs):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}


def faq_html(faqs):
    return "<h2>よくある質問</h2>" + "".join(
        f'<details{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(faqs))


COMMON_FAQ = ("入力した内容はどこかに送られますか？", "送られません。書き込みはブラウザの中だけで扱い、保存もしません。ページを閉じると消えるので、残したいときは印刷するかPDFで保存してください。")


def page(t, sheet, controls, after, faqs, sources, js):
    path = "templates/" + t["id"]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CreativeWork", "name": t["title"], "url": f"{BASE}{path}/", "description": t["desc"], "inLanguage": "ja",
         "learningResourceType": "印刷用テンプレート", "isAccessibleForFree": True, "dateModified": DATE, "publisher": PUB},
        faq_ld(faqs + [COMMON_FAQ])]}
    others = "".join(f'<li><a href="/templates/{x["id"]}/">{E(x["title"])}</a></li>' for x in T if x["id"] != t["id"])
    body = ('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/") + "</script>"
            + f'<p>{t["lead"]}無料・登録不要。A4で印刷でき、PDFでも保存できます。</p>'
            + controls
            + '<div class="tp-bar"><button type="button" class="tp-btn" id="tp-print">印刷する・PDFで保存</button></div>'
            + f'<div class="tp-sheet" id="tp-sheet">{sheet}</div>'
            + after + HOWTO + faq_html(faqs + [COMMON_FAQ])
            + f'<h2>ほかのテンプレート</h2><ul class="steps">{others}</ul><p><a href="/templates/">勉強のテンプレート一覧に戻る</a></p>'
            + '<div class="sources"><h2>出典</h2><ol>' + "".join(f"<li>{SRC[s]}</li>" for s in sources) + "</ol></div>"
            + "<script>(function(){document.getElementById('tp-print').addEventListener('click',function(){window.print()});" + js + "})();</script>")
    return {"path": path, "title": t["title"], "seo_title": t["seo"], "date": DATE, "desc": t["desc"],
            "body": body, "css": CSS + t.get("css", ""), "parent": PARENT}


T = [
    {"id": "review-calendar", "title": "復習カレンダー（試験日から作って印刷）",
     "seo": "復習カレンダー テンプレート｜試験日から1回目の復習日を書き込んで印刷（無料・PDF）",
     "desc": "試験日と、範囲ごとに勉強する日を入れると、1回目の復習に向く日を書き込んだカレンダーを作って印刷・PDF保存できます。約1,350人の分散学習の研究（Cepedaら 2008）がもとの無料テンプレート。",
     "lead": "試験日と、範囲ごとに勉強する日を入れると、1回目の復習に向く日を書き込んだカレンダーができます。",
     "hub": "範囲ごとの「勉強する日・復習する日・試験日」を1枚のカレンダーに。", "basis": "分散学習（Cepedaら 2008）"},
    {"id": "recall-note", "title": "暗記ノート（思い出す練習用）",
     "seo": "暗記ノート テンプレート｜思い出す練習（テスト効果）用の印刷シート（無料・PDF）",
     "desc": "問いと答えを書いて、答えを折って隠して使う暗記ノートと、本を閉じて白紙に書き出すシートの2種類。読み返すより1週間後に残りやすい「思い出す練習」の研究がもとの無料テンプレート。",
     "lead": "答えを折って隠す「問いと答え」型と、本を閉じて書き出す「白紙」型の2種類です。",
     "hub": "答えを折って隠す一問一答型と、白紙に書き出す型の2種類。", "basis": "思い出す練習（Roediger・Karpicke 2006 ほか）"},
    {"id": "if-then", "title": "if-thenプランシート",
     "seo": "if-thenプラン テンプレート｜勉強を始める場面を決める印刷シート（無料・PDF）",
     "desc": "「もし〇〇したら、△△をする」の形で、勉強を始める場面と最初の行動を書くシート。机に貼れる切り取りカードと、2週間のチェック欄つき。94の検証をまとめた実行意図の研究がもとの無料テンプレート。",
     "lead": "「もし〇〇したら、△△をする」を書いて、勉強を始める場面を前もって決めるシートです。",
     "hub": "勉強を始める場面を1文で決める。机に貼れるカードつき。", "basis": "実行意図（Gollwitzer・Sheeran 2006 ほか）"},
    {"id": "wallpaper", "title": "if-thenプランの壁紙（スマホのロック画面用）",
     "seo": "勉強のスマホ壁紙｜if-thenプランを入れてロック画面に置く（無料・作成ツール）",
     "desc": "「もし〇〇したら、△△をする」を入れると、スマホのロック画面用の壁紙画像を作ります。勉強を始める場面を毎日目に入る所に置くための無料ツール。94の検証をまとめた実行意図の研究がもと。",
     "lead": "「もし〇〇したら、△△をする」を入れると、スマホのロック画面用の壁紙ができます。",
     "hub": "if-thenプランをロック画面に。入れるだけで壁紙画像ができる。", "basis": "実行意図（Gollwitzer・Sheeran 2006）"},
    {"id": "study-plan", "title": "勉強計画表（見積もり調整つき）",
     "seo": "勉強計画表 テンプレート｜やることを書き出し、過去の実績で見積もりを調整して印刷（無料・PDF）",
     "desc": "やることを書き出して時間を見積もり、前回の実績の倍率で調整する勉強計画表。期限までに間に合うかも計算します。人は作業時間を短く見積もりがちという計画錯誤の研究がもとの無料テンプレート。",
     "lead": "やることを全部書き出して時間を見積もり、過去の実績で調整する計画表です。期限に間に合うかも計算します。",
     "hub": "やることを書き出し、見積もりを過去の実績で調整する。", "basis": "計画錯誤（Buehlerら 1994 ほか）"},
    {"id": "study-log", "title": "勉強の記録表（1か月・印刷用）",
     "seo": "勉強の記録表 テンプレート｜1か月分を印刷して手書きで記録（無料・PDF）",
     "desc": "1日1行で、その日にやった勉強と時間を手書きで記録する1か月分の記録表。月を選ぶと日付と曜日が入ります。進み具合を確かめると目標が達成されやすいという138件の実験のメタ分析がもとの無料テンプレート。",
     "lead": "1日1行で、その日にやった勉強と時間を書き込む1か月分の記録表です。月を選ぶと日付と曜日が入ります。",
     "hub": "1日1行の手書き記録。月を選ぶと日付と曜日が入る。", "basis": "進み具合の記録（Harkinら 2016）"},
]
BY = {t["id"]: t for t in T}
PAGES = []

# ---------- 1. 復習カレンダー ----------
t = BY["review-calendar"]
controls = ('<div class="tp-opt"><label for="rc-ex">試験日・使う日</label><input type="date" id="rc-ex">'
            '<span class="tp-lbl" style="color:var(--text);font-size:14px">範囲と、勉強する日</span>'
            '<div id="rc-rows" style="display:grid;gap:8px"></div>'
            '<div class="tp-bar" style="margin:4px 0 0"><button type="button" class="tp-btn2" id="rc-add">範囲を足す</button>'
            '<button type="button" class="tp-btn" id="rc-go">カレンダーを作る</button></div>'
            '<p class="tp-hint" id="rc-msg" aria-live="polite">範囲は8つまで。カレンダーは試験日の月から最大4か月分です。</p></div>')
sheet = '<p>カレンダーを作るには、JavaScriptを有効にしてください。下の表と同じ手順で、紙のカレンダーに書き込むこともできます。</p>'
after = ('<p class="answer"><strong>目安：試験が近いほど早めに、遠いほど間をあけて1回目の復習をします。</strong>1週間後の試験なら翌日、約1か月後なら10日後前後、70日以上先なら3週間後です。</p>'
         '<h2>このテンプレートの根拠</h2>'
         '<p>約1,350人が雑学知識を覚え、間隔を変えて1回復習し、最長1年後にテストを受けた実験（Cepedaら 2008）の結果を使っています。最適な間隔で復習すると、間をあけない復習より正答が64%多くなりました。</p>'
         '<table class="rt-t"><caption>実験で最もよく残った間隔</caption><thead><tr><th>試験まで</th><th>1回目の復習</th></tr></thead>'
         '<tbody><tr><td>7日後</td><td>勉強の1日後</td></tr><tr><td>35日後</td><td>勉強の11日後</td></tr><tr><td>70日後</td><td>勉強の21日後</td></tr><tr><td>350日後</td><td>勉強の21日後</td></tr></tbody></table>'
         '<p>この4点の間の日数は、SEADICEが直線でつないで見積もっています（実験で直接確かめた値ではありません）。2回目以降の復習の最適な日は、この研究では確かめられていないため、カレンダーには書き込まず、表の空欄に自分で決めて書く形にしています。くわしくは<a href="/spaced-review-why-it-works/">分散学習の記事</a>と<a href="/review-timing/">復習日の計算機</a>で解説しています。</p>'
         '<h2>記入例</h2><table class="rt-t"><thead><tr><th>範囲</th><th>勉強する日</th><th>試験日</th><th>1回目の復習</th></tr></thead>'
         '<tbody><tr><td>第1章</td><td>10月1日</td><td>11月5日（35日後）</td><td>10月12日</td></tr><tr><td>第2章</td><td>10月8日</td><td>11月5日（28日後）</td><td>10月17日</td></tr><tr><td>第3章</td><td>10月29日</td><td>11月5日（7日後）</td><td>10月30日</td></tr></tbody></table>'
         '<p>復習の日は、ノートを読み返すより本を閉じて思い出す方が残ります。<a href="/templates/recall-note/">暗記ノート</a>と組み合わせて使えます。</p>')
faqs = [("復習は何日後にすればいいですか？", "試験までの長さで変わります。Cepedaら（2008）では、1週間後のテストなら1日後、35日後なら11日後、70日後と1年後なら21日後の復習が最もよく残りました。"),
        ("2回目以降の復習はいつすればいいですか？", "この研究では1回の復習の最適な間隔だけを調べています。2回目以降はカレンダーの表の空欄に自分で日を決めて書き、少しずつ間を広げるのが一般的なやり方です。")]
js = r"""
var P=[[7,1],[35,11],[70,21],[350,21]],R=document.getElementById('rc-rows'),ex=document.getElementById('rc-ex'),S=document.getElementById('tp-sheet'),M=document.getElementById('rc-msg');
function iso(t){var z=new Date(t.getTime()-t.getTimezoneOffset()*6e4);return z.toISOString().slice(0,10)}
function add(t,n){var d=new Date(t);d.setDate(d.getDate()+n);return d}
function gap(n){if(n<=P[0][0])return 1;for(var i=1;i<P.length;i++){var a=P[i-1],b=P[i];if(n<=b[0])return Math.round(a[1]+(b[1]-a[1])*(n-a[0])/(b[0]-a[0]))}return 21}
function md(t){return (t.getMonth()+1)+'/'+t.getDate()+'（'+'日月火水木金土'[t.getDay()]+'）'}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function row(nm,dt){if(R.children.length>=8){M.textContent='範囲は8つまでです。';return}var i=R.children.length+1,d=document.createElement('div');d.style.cssText='display:grid;grid-template-columns:1fr 1fr;gap:8px';
 d.innerHTML='<input aria-label="範囲'+i+'の名前" placeholder="第'+i+'章" maxlength="16" value="'+esc(nm||'')+'"><input type="date" aria-label="範囲'+i+'を勉強する日" value="'+(dt||'')+'">';R.appendChild(d)}
var t0=new Date();t0.setHours(0,0,0,0);ex.value=iso(add(t0,35));
row('第1章',iso(t0));row('第2章',iso(add(t0,7)));row('第3章',iso(add(t0,21)));
document.getElementById('rc-add').addEventListener('click',function(){row('','');R.lastChild&&R.lastChild.firstChild.focus()});
function build(){
 if(!ex.value){ex.focus();M.textContent='試験日を入れてください。';return}
 var E=new Date(ex.value+'T00:00'),ev={},it=[],bad=0;
 function put(d,k,s){var k2=iso(d);(ev[k2]=ev[k2]||[]).push([k,s])}
 [].forEach.call(R.children,function(r,i){var nm=r.children[0].value.trim()||('範囲'+(i+1)),v=r.children[1].value;if(!v)return;
  var st=new Date(v+'T00:00'),n=Math.round((E-st)/864e5);if(n<1){bad++;return}
  var g=n>=2?Math.min(gap(n),n-1):0,rv=g?add(st,g):null;put(st,'学',nm);if(rv)put(rv,'復',nm);it.push([nm,st,rv,n])});
 put(E,'試','試験');
 var first=new Date(E.getFullYear(),E.getMonth()-3,1),m0=new Date(E.getFullYear(),E.getMonth(),1);
 it.forEach(function(x){var m=new Date(x[1].getFullYear(),x[1].getMonth(),1);if(m<m0)m0=m});if(m0<first)m0=first;
 var h='<div class="tp-pg"><div class="tp-h"><b>復習カレンダー</b><span>試験日 '+md(E)+'</span></div><p class="rc-key"><span class="rc-m rc-s">学</span>勉強する日　<span class="rc-m rc-r">復</span>1回目の復習　<span class="rc-m rc-x">試</span>試験日</p>';
 for(var m=new Date(m0);m<=E;m=new Date(m.getFullYear(),m.getMonth()+1,1)){
  h+='<table class="rc-cal"><caption>'+m.getFullYear()+'年'+(m.getMonth()+1)+'月</caption><thead><tr>'+'日月火水木金土'.split('').map(function(w){return '<th>'+w+'</th>'}).join('')+'</tr></thead><tbody><tr>';
  var c=0;for(;c<m.getDay();c++)h+='<td></td>';
  for(var d=new Date(m);d.getMonth()===m.getMonth();d=add(d,1)){if(c&&c%7===0)h+='</tr><tr>';c++;var e=ev[iso(d)]||[];
   h+='<td><span class="rc-d">'+d.getDate()+'</span>'+e.map(function(x){return '<span class="rc-e"><span class="rc-m '+{'学':'rc-s','復':'rc-r','試':'rc-x'}[x[0]]+'">'+x[0]+'</span>'+(x[0]==='試'?'':esc(x[1]))+'</span>'}).join('')+'</td>'}
  for(;c%7;c++)h+='<td></td>';h+='</tr></tbody></table>'}
 h+='<table><thead><tr><th>範囲</th><th>勉強する日</th><th>1回目の復習</th><th>2回目以降の復習（自分で決める）</th><th style="width:3.5em">済</th></tr></thead><tbody>'+
  it.map(function(x){return '<tr><td>'+esc(x[0])+'</td><td>'+md(x[1])+'</td><td>'+(x[2]?md(x[2]):'翌日が試験')+'</td><td></td><td></td></tr>'}).join('')+'</tbody></table>'+
  '<p class="tp-tip">復習の日は、ノートを読み返すより、本を閉じて思い出してから答え合わせをします。</p>'+FOOT+'</div>';
 S.innerHTML=h;M.textContent=bad?('試験日より後の「勉強する日」が'+bad+'つあり、カレンダーに入れていません。'):'カレンダーを作りました。印刷するか、PDFで保存できます。'}
document.getElementById('rc-go').addEventListener('click',build);build();
""".replace("FOOT", json.dumps(foot("templates/review-calendar")))
t["css"] = (".rc-key{font-size:12px;margin:0 0 6px}.rc-m{display:inline-block;min-width:1.6em;text-align:center;font-size:11px;font-weight:800;border-radius:4px;padding:0 3px;margin-right:3px;-webkit-print-color-adjust:exact;print-color-adjust:exact}"
            ".rc-s{border:1.5px solid #1d2330}.rc-r{background:#1d2330;color:#fff!important}.rc-x{background:#c0392b;color:#fff!important}"
            ".tp-sheet table.rc-cal{table-layout:fixed;margin:10px 0 14px;break-inside:avoid}.rc-cal caption{text-align:left;font-weight:800;font-size:14px;padding-bottom:4px}"
            ".rc-cal th{text-align:center}.rc-cal td{height:64px;font-size:11px;line-height:1.35;padding:3px;word-break:break-all}.rc-d{display:block;font-size:12px;font-weight:700;color:#55607a}.rc-e{display:block;margin-top:2px}"
            "@media print{.rc-cal td{height:20mm}}")
PAGES.append(page(t, sheet, controls, after, faqs, ["cepeda"], js))

# ---------- 2. 暗記ノート ----------
t = BY["recall-note"]
qa_rows = "".join(f'<tr><td class="rn-n">{i}</td><td><input aria-label="問い{i}"></td><td class="rn-a"><input aria-label="答え{i}"></td><td></td><td></td></tr>' for i in range(1, 16))
sheet = ('<div class="tp-pg" id="rn-qa"><div class="tp-h"><b>暗記ノート（問いと答え）</b><span>日付　　／　　</span></div>'
         '<label class="tp-lbl" for="rn-r1">範囲</label><input id="rn-r1" placeholder="例：第3章 貿易条件">'
         '<table class="rn-t"><thead><tr><th class="rn-n">No</th><th>問い（本を見ながら作る）</th><th class="rn-a">答え　← ここで折って隠す</th><th class="rn-c">1回目<br>○×</th><th class="rn-c">翌日<br>○×</th></tr></thead>'
         f'<tbody>{qa_rows}</tbody></table>'
         '<p class="tp-tip">答えの列を折って隠し、問いだけを見て答えを書き出す（言う）→ 開いて答え合わせ → ○×をつける。×の問いから、翌日もう一度。</p>'
         + foot("templates/recall-note") + '</div>'
         '<div class="tp-pg" id="rn-bl" hidden><div class="tp-h"><b>暗記ノート（白紙に書き出す）</b><span>日付　　／　　</span></div>'
         '<label class="tp-lbl" for="rn-r2">範囲</label><input id="rn-r2" placeholder="例：第3章 貿易条件">'
         '<span class="tp-lbl">1. 本を閉じて、覚えていることを全部書き出す（3分）</span>' + lines(13)
         + '<span class="tp-lbl">2. 本を開いて答え合わせ。抜けていた所・まちがえた所</span>' + lines(6)
         + '<span class="tp-lbl">3. 翌日、何も見ずにもう一度書き出せたか</span>'
           '<p style="font-size:13px;margin:6px 0">日付　　／　　　　□ ほぼ書けた　　□ 半分くらい　　□ ほとんど出てこない（範囲を小さくして、読み直してから試す）</p>'
         + foot("templates/recall-note") + '</div>')
controls = ('<div class="tp-opt"><label for="rn-k">シートの種類</label><select id="rn-k"><option value="qa">問いと答え（答えを折って隠す・15問）</option><option value="bl">白紙に書き出す（読んだあとに使う）</option></select>'
            '<p class="tp-hint">問いと答えは画面で入力してから印刷することも、空欄のまま印刷して手書きすることもできます。</p></div>')
after = ('<p class="answer"><strong>結論：読み返すより、本を閉じて思い出す方が残ります。</strong>思い出したあとに答え合わせをすると、効果がさらに大きくなります。</p>'
         '<h2>このテンプレートの根拠</h2>'
         '<p>Roediger・Karpicke（2006）では、短い文章を4回読んだグループは1週間後に40%思い出せたのに対し、1回読んで3回思い出す練習をしたグループは61%でした。5分後のテストでは読み返しの方が上だったため、「すぐの手ごたえ」と「1週間後に残るか」は別だとわかります。</p>'
         '<table class="rt-t"><caption>思い出す練習の効果（Rowland 2014、61研究のまとめ）</caption><thead><tr><th>やり方</th><th>効果の大きさ</th></tr></thead>'
         '<tbody><tr><td>答え合わせあり</td><td>0.73</td></tr><tr><td>答え合わせなし</td><td>0.39</td></tr><tr><td>手がかりから答えを書き出す</td><td>0.61</td></tr><tr><td>選択肢から選ぶ</td><td>0.29</td></tr></tbody></table>'
         '<p>このため、どちらのシートも「答え合わせ」の欄と、選ばずに「書き出す」形にしています。答え合わせなしで半分も思い出せなかった場合は、効果がほぼありませんでした。何も出てこないときは範囲を小さくしてください。くわしくは<a href="/retrieval-practice-vs-rereading/">思い出す練習の記事</a>で解説しています。</p>'
         '<h2>記入例（問いと答え）</h2><table class="rt-t"><thead><tr><th>問い</th><th>答え</th><th>1回目</th><th>翌日</th></tr></thead>'
         '<tbody><tr><td>FOBで、売り手の費用負担はどこまで？</td><td>本船に積み込むまで</td><td>×</td><td>○</td></tr><tr><td>分散学習とは？</td><td>間をあけて復習すること</td><td>○</td><td>○</td></tr></tbody></table>'
         '<p>翌日にもう一度やる日は、<a href="/templates/review-calendar/">復習カレンダー</a>で決められます。</p>')
faqs = [("暗記ノートはどう使えば効果がありますか？", "答えを隠して、問いだけを見て答えを書き出し、そのあと必ず答え合わせをします。Rowland（2014）のまとめでは、答え合わせありの効果（0.73）は、なし（0.39）のほぼ2倍でした。"),
        ("問いと答え型と白紙型はどう使い分けますか？", "用語や一問一答で覚える内容は問いと答え型、流れや仕組みを理解したい章は、読んだあとに白紙型で書き出すのが向いています。")]
js = r"""
var k=document.getElementById('rn-k'),a=document.getElementById('rn-qa'),b=document.getElementById('rn-bl');
k.addEventListener('change',function(){a.hidden=k.value!=='qa';b.hidden=k.value!=='bl'});
"""
t["css"] = (".tp-sheet table.rn-t{table-layout:fixed}.rn-n{width:2.4em;text-align:center!important;color:#55607a}.rn-c{width:4em;white-space:nowrap;text-align:center!important}"
            ".tp-sheet .rn-a{border-left:2px dashed #55607a}.rn-t td{height:36px;padding:0 4px}@media print{.rn-t td{height:11mm}}")
PAGES.append(page(t, sheet, controls, after, faqs, ["roediger", "rowland"], js))

# ---------- 3. if-thenプラン ----------
t = BY["if-then"]
def ifthen(n, a, b, ph1, ph2):
    return (f'<div class="it-p"><span class="tp-lbl">{n}</span><div class="it-row"><span>もし</span><input id="it-{a}" placeholder="{ph1}"><span>したら、</span></div>'
            f'<div class="it-row"><input id="it-{b}" placeholder="{ph2}"><span>をする。</span></div></div>')
days = "".join(f"<td>{i}</td>" for i in range(1, 15))
sheet = ('<div class="tp-pg"><div class="tp-h"><b>if-thenプラン</b><span>書いた日　　／　　</span></div>'
         '<label class="tp-lbl" for="it-g">目標（何のために勉強する？）</label><input id="it-g" placeholder="例：来年3月の簿記2級に受かる">'
         + ifthen("プラン1（始める場面）", "a1", "b1", "帰りの電車に座る", "単語アプリを開いて10問解く")
         + ifthen("プラン2（もう1つ決めるなら）", "a2", "b2", "夕食の食器を片づける", "机でテキストを1ページ開く")
         + '<div class="it-p"><span class="tp-lbl">つまずきそうな場面への備え</span><div class="it-row"><span>もし</span><input id="it-a3" placeholder="疲れてやる気が出ない"><span>なら、</span></div>'
           '<div class="it-row"><input id="it-b3" placeholder="1問だけ解く"><span>をする。</span></div></div>'
         '<span class="tp-lbl">できた日に○（2週間）</span><table class="it-d"><tbody><tr>' + days + '</tr><tr>' + "<td></td>" * 14 + '</tr></tbody></table>'
         '<p class="tp-tip">3日続かなかったら、意志のせいではなく場面が合っていないサインです。「帰りの電車」→「昼休み」のように、きっかけの場面を変えて書き直します。</p>'
         '<div class="it-card"><span class="it-cut">切り取り線で切って、その場面で目に入る所に貼る</span><p><b>もし</b> <span id="it-c1">＿＿＿＿＿＿＿＿</span> <b>したら、</b><br><span id="it-c2">＿＿＿＿＿＿＿＿</span> <b>をする。</b></p></div>'
         + foot("templates/if-then") + '</div>')
controls = ('<div class="tp-bar"><button type="button" class="tp-btn2" id="it-ex">記入例を入れる</button><button type="button" class="tp-btn2" id="it-clr">空欄に戻す</button></div>'
            '<p class="tp-hint">シートの線の上に直接書き込めます。空欄のまま印刷して手書きにもできます。</p>')
after = ('<p class="answer"><strong>結論：「いつ・どこで・何をやるか」を前もって1文で決めておくと、目標を実行しやすくなります。</strong>プランは1つか2つに絞ります。</p>'
         '<h2>このテンプレートの根拠</h2>'
         '<p>「もし場面Yになったら、行動Zをする」と前もって決めることを実行意図（if-thenプラン）と呼びます。94の独立した検証をまとめたメタ分析（Gollwitzer・Sheeran 2006）では、目標の達成に「中〜大」の効果（d=0.65）がありました。</p>'
         '<p>勉強では、重要な試験を控えた高校2年生66人のうち、30分で「望む結果・妨げになる壁・if-thenプラン」を書いた組が、問題集の練習問題を60%以上多く解きました（Duckworthら 2011）。このシートの「つまずきそうな場面への備え」は、この「壁」を書く部分にあたります。</p>'
         '<div class="note">効果の大きさは研究によって差があり、勉強で確かめた研究は高校生・小学生が中心です。社会人の独学で同じ効果が出るとは限りません。くわしくは<a href="/implementation-intentions-if-then-study/">実行意図の記事</a>で解説しています。</div>'
         '<h2>記入例</h2><table class="rt-t"><thead><tr><th>もし（場面）</th><th>をする（最初の行動）</th></tr></thead>'
         '<tbody><tr><td>帰りの電車に座ったら</td><td>単語アプリを開いて10問解く</td></tr><tr><td>夕食の食器を片づけたら</td><td>机でテキストを1ページ開く</td></tr><tr><td>疲れてやる気が出ないなら</td><td>1問だけ解く</td></tr></tbody></table>'
         '<p>場面は「毎日ほぼ必ず起きること」、行動は「始めた瞬間にやること」にすると書きやすくなります。続いた日は<a href="/templates/study-log/">勉強の記録表</a>に残せます。</p>')
faqs = [("if-thenプランとは何ですか？", "「もし場面Yになったら、行動Zをする」の形で、いつ・どこで・どう行動するかを前もって決めておくことです。94の検証をまとめた分析（Gollwitzer・Sheeran 2006）では、目標の達成に中〜大の効果（d=0.65）がありました。"),
        ("「毎日1時間勉強する」と書くのではだめですか？", "「毎日1時間」は目標で、いつ始めるかの場面が決まっていません。「夕食を片づけたら机でテキストを開く」のように、始める場面と最初の行動をセットにして書きます。")]
js = r"""
var X={g:'来年3月の簿記2級に受かる',a1:'帰りの電車に座る',b1:'単語アプリを開いて10問解く',a2:'夕食の食器を片づける',b2:'机でテキストを1ページ開く',a3:'疲れてやる気が出ない',b3:'1問だけ解く'};
function $(i){return document.getElementById('it-'+i)}
function sync(){$('c1').textContent=$('a1').value||'＿＿＿＿＿＿＿＿';$('c2').textContent=$('b1').value||'＿＿＿＿＿＿＿＿'}
Object.keys(X).forEach(function(k){$(k).addEventListener('input',sync)});
$('ex').addEventListener('click',function(){Object.keys(X).forEach(function(k){$(k).value=X[k]});sync()});
$('clr').addEventListener('click',function(){Object.keys(X).forEach(function(k){$(k).value=''});sync()});
"""
t["css"] = (".it-p{margin:6px 0 4px}.it-row{display:flex;align-items:flex-end;gap:6px;margin:2px 0}.it-row span{white-space:nowrap;font-weight:700;padding-bottom:6px}.it-row input{flex:1;min-width:0}"
            ".tp-sheet table.it-d{table-layout:fixed}.it-d td{text-align:center;font-size:11px;color:#55607a;height:22px;padding:2px}.it-d tr+tr td{height:34px}"
            ".it-card{border:2px dashed #55607a;border-radius:8px;padding:10px 14px;margin:14px 0 4px;max-width:420px}.it-cut{font-size:11px;color:#55607a}.it-card p{font-size:16px;line-height:1.9;margin:4px 0 0}"
            "@media print{.it-d tr+tr td{height:10mm}}")
PAGES.append(page(t, sheet, controls, after, faqs, ["gollwitzer", "duckworth"], js))

# ---------- 4. 勉強計画表 ----------
t = BY["study-plan"]
sp_rows = "".join(f'<tr><td><input aria-label="やること{i}" class="sp-w"></td><td><input aria-label="見積もり{i}（時間）" class="sp-e" type="number" inputmode="decimal" min="0" step="0.5"></td>'
                  f'<td class="sp-a"></td><td></td><td></td></tr>' for i in range(1, 13))
sheet = ('<div class="tp-pg"><div class="tp-h"><b>勉強計画表</b><span>作った日　　／　　</span></div>'
         '<div class="sp-g"><div><label class="tp-lbl" for="sp-goal">目標（終わらせたいこと）</label><input id="sp-goal" placeholder="例：問題集の第1〜3章を終える"></div>'
         '<div><label class="tp-lbl" for="sp-due">期限</label><input id="sp-due" type="date" required></div>'
         '<div><label class="tp-lbl" for="sp-r">前回は見積もりの何倍かかった？</label><input id="sp-r" type="number" inputmode="decimal" min="1" max="5" step="0.1" placeholder="例：1.5"></div>'
         '<div><label class="tp-lbl" for="sp-d">1日に使える時間（時間）</label><input id="sp-d" type="number" inputmode="decimal" min="0.25" max="16" step="0.25" placeholder="例：1"></div></div>'
         '<table class="sp-t"><thead><tr><th>やること（ひとつ残らず書き出す）</th><th class="sp-n">見積もり<br>（時間）</th><th class="sp-n">調整後<br>（×倍率）</th><th class="sp-n">実際に<br>かかった</th><th class="sp-c">済</th></tr></thead>'
         f'<tbody>{sp_rows}</tbody><tfoot><tr><th>合計</th><th id="sp-te"></th><th id="sp-ta"></th><th></th><th></th></tr></tfoot></table>'
         '<p class="sp-res" id="sp-res">期限までの日数　＿＿日　／　必要な日数（調整後の合計 ÷ 1日の時間）　＿＿日</p>'
         '<p class="tp-tip">「1章を終える」ではなく「読む・例題を解く・間違いを直す・復習する」と分けて書く。復習の時間も最初から入れる。終わったら「実際にかかった」を書き、次の計画の倍率に使う。</p>'
         + foot("templates/study-plan") + '</div>')
controls = '<p class="tp-hint">シートに直接書き込むと、調整後の時間と合計、期限に間に合うかを計算します。空欄のまま印刷して手書きにもできます。</p>'
after = ('<p class="answer"><strong>結論：見積もりは頭の中の予想ではなく、過去に実際かかった時間を基準にします。</strong>やることを細かく書き出すと、ずれも小さくなります。</p>'
         '<h2>このテンプレートの根拠</h2>'
         '<p>人は自分の作業時間を短く見積もりがちで、これを計画錯誤と呼びます。卒業論文を書く大学生の研究（Buehlerら 1994）では、提出までの予測は平均33.9日、実際は平均55.5日で、予測どおりに終えたのは29.7%でした。</p>'
         '<table class="rt-t"><caption>過去の実績を予測に結びつけた実験（Buehlerら 1994 研究4）</caption><thead><tr><th>予測のしかた</th><th>予測時間内に終えた人</th></tr></thead>'
         '<tbody><tr><td>何も指示しない</td><td>29.3%</td></tr><tr><td>過去の似た課題を思い出すだけ</td><td>38.1%</td></tr><tr><td>過去の実績を今回の予測に結びつける</td><td>60.0%</td></tr></tbody></table>'
         '<p>やることを細かく書き出してから予測した人は、所要時間を長く見積もり、一部の実験ではその方が実際に近くなりました（Kruger・Evans 2004）。このため計画表は「書き出す欄」と「過去の倍率をかける欄」を分けています。倍率の1.5は記入例で、研究の値ではありません。自分の記録から出した倍率を使ってください。くわしくは<a href="/planning-fallacy-study-plans/">計画錯誤の記事</a>で解説しています。</p>'
         '<h2>記入例（倍率1.5・1日1時間）</h2><table class="rt-t"><thead><tr><th>やること</th><th>見積もり</th><th>調整後</th></tr></thead>'
         '<tbody><tr><td>第1章を読む</td><td>2時間</td><td>3時間</td></tr><tr><td>例題を解く</td><td>3時間</td><td>4.5時間</td></tr><tr><td>間違いを直す・復習</td><td>2時間</td><td>3時間</td></tr><tr><td>合計</td><td>7時間</td><td>10.5時間（11日）</td></tr></tbody></table>'
         '<p>前回の倍率がわからないときは、<a href="/templates/study-log/">勉強の記録表</a>で「実際にかかった時間」を残すところから始めます。</p>')
faqs = [("勉強計画が毎回倒れるのはなぜですか？", "意志の問題というより見積もり方の問題です。人は予測するとき目の前の計画の流れを思い描き、過去の遅れを参考にしにくいことが研究で示されています（Buehlerら 1994）。"),
        ("倍率はどう決めればいいですか？", "前回、同じような量に見積もりの何倍かかったかを記録から出します。記録がなければ、この計画表の「実際にかかった」欄を埋めて、次の計画から使います。")]
js = r"""
function $(i){return document.getElementById(i)}
function num(v){v=parseFloat(v);return isFinite(v)&&v>0?v:0}
function f(v){return Math.round(v*10)/10}
function calc(){var r=num($('sp-r').value)||1,te=0,ta=0;
 [].forEach.call(document.querySelectorAll('.sp-t tbody tr'),function(tr){var e=num(tr.querySelector('.sp-e').value),c=tr.querySelector('.sp-a');te+=e;ta+=e*r;c.textContent=e?f(e*r):''});
 $('sp-te').textContent=te?f(te):'';$('sp-ta').textContent=te?f(ta):'';
 var d=num($('sp-d').value),due=$('sp-due').value,o=$('sp-res');
 if(!te||!d||!due){o.textContent='期限までの日数　＿＿日　／　必要な日数（調整後の合計 ÷ 1日の時間）　＿＿日';return}
 var t0=new Date();t0.setHours(0,0,0,0);var left=Math.round((new Date(due+'T00:00')-t0)/864e5),need=Math.ceil(ta/d);
 o.textContent='期限までの日数 '+left+'日　／　必要な日数 '+need+'日　→ '+(left>=need?'間に合う見込み（余裕 '+(left-need)+'日）':'このままでは'+(need-left)+'日足りない。やることを減らすか、期限か1日の時間を見直す')}
document.querySelector('.tp-sheet').addEventListener('input',calc);
"""
t["css"] = (".sp-g{display:grid;grid-template-columns:1fr 1fr;gap:4px 14px}.sp-g>div:first-child{grid-column:1/-1}"
            ".tp-sheet table.sp-t{table-layout:fixed;margin-top:14px}.sp-n{width:5.2em;text-align:center!important}.sp-c{width:2.6em}.sp-t td{height:34px;padding:0 4px}.sp-a{text-align:center!important;vertical-align:middle!important;font-weight:700}"
            "@media(max-width:520px){.sp-n{width:3.6em}.sp-c{width:2em}.sp-t th{font-size:10px}}.sp-t tfoot th{text-align:center}.sp-t tfoot th:first-child{text-align:left}.sp-res{font-size:13px;font-weight:700;margin:8px 0 0}@media print{.sp-t td{height:10mm}}")
PAGES.append(page(t, sheet, controls, after, faqs, ["buehler", "kruger"], js))

# ---------- 5. 勉強の記録表(印刷用) ----------
t = BY["study-log"]
sl_rows = "".join(f'<tr><td class="sl-dt">／</td><td></td><td></td><td></td></tr>' for _ in range(31))
sheet = ('<div class="tp-pg"><div class="tp-h"><b id="sl-ttl">勉強の記録表　　　年　　月</b><span>記録は1日1行</span></div>'
         '<label class="tp-lbl" for="sl-goal">今月の目標</label><input id="sl-goal" placeholder="例：問題集を1周する">'
         '<table class="slp-t"><thead><tr><th class="sl-dt">日付</th><th>今日やったこと（行動を書く）</th><th class="sl-m">時間</th><th class="sl-ok">○</th></tr></thead>'
         f'<tbody id="sl-b">{sl_rows}</tbody></table>'
         '<p class="sl-sum">記録した日　＿＿日　　合計時間　＿＿時間＿＿分　　来月変えること：</p>'
         + foot("templates/study-log") + '</div>')
controls = ('<div class="tp-opt"><label for="sl-mo">月</label><input type="month" id="sl-mo"></div>')
after = ('<p class="answer"><strong>結論：進み具合を確かめる回数を増やすと、目標は達成されやすくなります。</strong>書き残す形の方が効果は大きめでした。1日1行で十分です。</p>'
         '<h2>このテンプレートの根拠</h2>'
         '<p>138件の実験・19,951人をまとめたメタ分析（Harkinら 2016）では、進み具合を確かめる回数を増やす工夫が、目標の達成を後押ししました（効果の大きさ d=0.40）。確かめた内容を書き残した場合（0.43）は、書き残さない場合（0.29）より効果が大きめでした。</p>'
         '<p>同じ分析では、行動を記録すると行動に、結果を記録すると結果に効きました。このため記録表は「何ページ読んだか」より「何をしたか」を書く形にしています。</p>'
         '<div class="note">実験の多くは運動や食事などの健康の目標で、勉強で確かめた研究はまだ少なめです。スマホで記録したい人は<a href="/study-log/">勉強の記録シート（Web版）</a>も使えます。くわしくは<a href="/study-log-progress-monitoring/">勉強の記録の記事</a>で解説しています。</div>'
         '<h2>記入例</h2><table class="rt-t"><thead><tr><th>日付</th><th>今日やったこと</th><th>時間</th></tr></thead>'
         '<tbody><tr><td>10/1（水）</td><td>過去問1回分を解いて答え合わせ</td><td>60分</td></tr><tr><td>10/2（木）</td><td>まちがえた12問を解き直し</td><td>25分</td></tr><tr><td>10/3（金）</td><td>第3章を読む前に章末問題を3分解いた</td><td>40分</td></tr></tbody></table>'
         '<p>記録した時間は、次の<a href="/templates/study-plan/">勉強計画表</a>で見積もりの倍率を出すのに使えます。</p>')
faqs = [("勉強の記録をつけると、本当に続くのですか？", "進み具合を確かめる回数を増やすと、目標は達成されやすくなりました。138件の実験・19,951人をまとめたメタ分析（Harkinら 2016）の結果です。ただし多くは健康の目標で、勉強での研究はまだ少なめです。"),
        ("紙とアプリ、どちらで記録するのがいいですか？", "どちらでも構いません。大事なのは書き残すことと、ときどき見返して進み具合を確かめることです。続けやすい方を選んでください。")]
js = r"""
var mo=document.getElementById('sl-mo'),b=document.getElementById('sl-b');
var t0=new Date();mo.value=t0.getFullYear()+'-'+('0'+(t0.getMonth()+1)).slice(-2);
function fill(){var p=(mo.value||'').split('-'),y=+p[0],m=+p[1];if(!y||!m)return;
 var n=new Date(y,m,0).getDate();document.getElementById('sl-ttl').textContent='勉強の記録表　'+y+'年'+m+'月';
 [].forEach.call(b.rows,function(r,i){var c=r.cells[0];if(i<n){var d=new Date(y,m-1,i+1),w=d.getDay();r.hidden=false;c.textContent=m+'/'+(i+1)+'（'+'日月火水木金土'[w]+'）';c.className='sl-dt'+(w===0?' sl-sun':w===6?' sl-sat':'')}else r.hidden=true})}
mo.addEventListener('change',fill);fill();
"""
t["css"] = (".tp-sheet table.slp-t{table-layout:fixed}.sl-dt{width:5.6em;white-space:nowrap;font-size:12px}.sl-m{width:4.2em}.sl-ok{width:2.4em}"
            ".slp-t td{height:26px;padding:0 4px;vertical-align:middle}.sl-sun{color:#b03a2e!important}.sl-sat{color:#2c5fa8!important}.sl-sum{font-size:12px;margin:8px 0 0}"
            "@media print{.tp-sheet{font-size:9.5pt}.slp-t td{height:6.6mm}.tp-h{margin-bottom:6px}}")
PAGES.append(page(t, sheet, controls, after, faqs, ["harkin"], js))

# ---------- 6. if-thenプランの壁紙(画像を作るだけで印刷はしない) ----------
t = BY["wallpaper"]
WP_FAQ = [("壁紙にすると、本当に勉強を始めやすくなりますか？", "壁紙そのものの効果を確かめた研究はありません。根拠は、始める場面と行動を前もって決める実行意図の研究（94の検証のまとめで d=0.65）です。壁紙は、決めたプランを毎日目に入る所に置くための工夫です。"),
          ("文字が時計や通知に重なりませんか？", "時計が出る画面の上の方と、ボタンが並ぶ下の方を空けて、真ん中より少し下に文字を置いています。機種によってずれるときは、ロック画面の設定で写真の位置を上下に動かしてください。"),
          ("入力した内容はどこかに送られますか？", "送られません。画像はブラウザの中で作り、保存もしません。")]
wp_ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": t["title"], "url": f"{BASE}templates/wallpaper/", "applicationCategory": "EducationalApplication", "operatingSystem": "Any",
     "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}, "description": t["desc"], "dateModified": "2026-10-09", "publisher": PUB},
    faq_ld(WP_FAQ)]}
others = "".join(f'<li><a href="/templates/{x["id"]}/">{E(x["title"])}</a></li>' for x in T if x["id"] != "wallpaper")
wp_body = ('<script type="application/ld+json">' + json.dumps(wp_ld, ensure_ascii=False).replace("</", "<\\/") + "</script>"
           f'<p>{t["lead"]}無料・登録不要で、入力した文字はどこにも送られません。</p>'
           '<form class="tp-opt" id="wp-f" onsubmit="return false">'
           '<label for="wp-a">もし（毎日ほぼ必ず起きる場面）</label><input id="wp-a" maxlength="24" placeholder="帰りの電車に座ったら" value="帰りの電車に座ったら">'
           '<p class="tp-hint">「〜したら」「〜のとき」の形で書きます。</p>'
           '<label for="wp-b">をする（始めた瞬間にやること）</label><input id="wp-b" maxlength="24" placeholder="単語アプリで10問解く" value="単語アプリで10問解く">'
           '<label for="wp-g">目標（任意・小さく入ります）</label><input id="wp-g" maxlength="30" placeholder="例：来年3月の簿記2級に受かる">'
           '<div class="wp-2"><div><label for="wp-t">色</label><select id="wp-t"><option value="night">夜（紺と金）</option><option value="paper">紙（白とすみ色）</option><option value="sea">海（青のグラデーション）</option></select></div>'
           '<div><label for="wp-s">機種</label><select id="wp-s"><option value="1179x2556">iPhone</option><option value="1080x2400">Android</option></select></div></div>'
           '</form>'
           '<div class="wp-pv"><img id="wp-img" alt="作った壁紙のプレビュー" width="240" height="520"></div>'
           '<div class="tp-bar" style="justify-content:center"><a class="tp-btn" id="wp-dl" download="ifthen-wallpaper.png" href="#" style="text-decoration:none">壁紙を保存する</a></div>'
           '<p class="tp-hint" style="text-align:center">iPhoneは、上の画像を長押しして「“写真”に保存」でも保存できます。</p>'
           '<p class="answer"><strong>結論：始める場面と最初の行動を1文で決め、その場面で目に入る所に置きます。</strong>ロック画面なら、スマホを手に取るたびに目に入ります。</p>'
           '<h2>この壁紙の根拠</h2>'
           '<p>「もし場面Yになったら、行動Zをする」と前もって決めることを実行意図（if-thenプラン）と呼びます。94の独立した検証をまとめたメタ分析（Gollwitzer・Sheeran 2006）では、目標の達成に「中〜大」の効果（d=0.65）がありました。</p>'
           '<div class="note">壁紙にすること自体の効果を確かめた研究はありません。決めたプランを忘れないための置き場所の工夫です。プランは1つに絞り、3日続かなければ場面を変えて作り直してください。くわしくは<a href="/implementation-intentions-if-then-study/">実行意図の記事</a>で解説しています。</div>'
           '<h2>壁紙に設定するには</h2><ul class="steps">'
           '<li><strong>iPhone</strong>：「写真」アプリで保存した画像を開き、共有ボタン →「壁紙に使用」→ ロック画面に設定</li>'
           '<li><strong>Android</strong>：ギャラリーで画像を開き、メニュー →「壁紙に設定」→ ロック画面（機種によって表示が違います）</li></ul>'
           '<h2>入力例</h2><table class="rt-t"><thead><tr><th>もし</th><th>をする</th></tr></thead>'
           '<tbody><tr><td>帰りの電車に座ったら、</td><td>単語アプリで10問解く</td></tr><tr><td>朝のコーヒーをいれたら、</td><td>昨日の範囲を3分で書き出す</td></tr><tr><td>お風呂から上がったら、</td><td>テキストを1ページ開く</td></tr></tbody></table>'
           '<p>紙に書いて机に貼りたいときは<a href="/templates/if-then/">if-thenプランシート</a>が使えます。</p>'
           + faq_html(WP_FAQ)
           + f'<h2>ほかのテンプレート</h2><ul class="steps">{others}</ul><p><a href="/templates/">勉強のテンプレート一覧に戻る</a></p>'
           '<div class="sources"><h2>出典</h2><ol><li>' + SRC["gollwitzer"] + '</li></ol></div>')
WP_JS = r"""
(function(){
var T={night:{bg:['#0B1020','#141d38'],fg:'#EAF0FA',sub:'#93A3BE',ac:'#F5C542'},paper:{bg:['#F7F5EF','#EDE9DF'],fg:'#1d2330',sub:'#6b7385',ac:'#1d2330'},sea:{bg:['#1e4f9c','#0B1020'],fg:'#FFFFFF',sub:'#bcd2f2',ac:'#8CE0FF'}};
var F='-apple-system,BlinkMacSystemFont,"Hiragino Sans","Hiragino Kaku Gothic ProN","Noto Sans JP",sans-serif';
function $(i){return document.getElementById(i)}
var url='';
function brk(c,s,max){var out=[],l='';for(var i=0;i<s.length;i++){var ch=s[i],t=l+ch;if(c.measureText(t).width>max&&l&&'、。，．」）！？ーっゃゅょ'.indexOf(ch)<0){out.push(l);l=ch}else l=t}if(l)out.push(l);return out}
function wrap(c,s,max){var n=brk(c,s,max).length,lo=max*.4,hi=max;if(n>1){for(var k=0;k<12;k++){var md=(lo+hi)/2;if(brk(c,s,md).length>n)lo=md;else hi=md}}return brk(c,s,hi).slice(0,3)}
function draw(){
 var sz=$('wp-s').value.split('x'),W=+sz[0],H=+sz[1],th=T[$('wp-t').value],c=document.createElement('canvas');c.width=W;c.height=H;var x=c.getContext('2d');
 var g=x.createLinearGradient(0,0,0,H);g.addColorStop(0,th.bg[0]);g.addColorStop(1,th.bg[1]);x.fillStyle=g;x.fillRect(0,0,W,H);
 var a=$('wp-a').value.trim()||'＿＿＿＿',b=$('wp-b').value.trim()||'＿＿＿＿',gl=$('wp-g').value.trim(),m=W*.11,mx=W-2*m,big=W*.072,sm=W*.044;
 x.textBaseline='top';x.font='700 '+big+'px '+F;var la=wrap(x,a+'、',mx),lb=wrap(x,b,mx);
 var h=sm*1.9+la.length*big*1.35+big*.5+sm*1.9+lb.length*big*1.35+sm*1.6+(gl?sm*3.2:0),y=Math.max(H*.40,H*.62-h/2);
 x.fillStyle=th.ac;x.fillRect(m,y,W*.06,W*.008);y+=sm*.9;
 x.font='600 '+sm+'px '+F;x.fillStyle=th.sub;x.fillText('もし',m,y);y+=sm*1.6;
 x.font='800 '+big+'px '+F;x.fillStyle=th.fg;la.forEach(function(l){x.fillText(l,m,y);y+=big*1.35});y+=big*.5;
 x.font='600 '+sm+'px '+F;x.fillStyle=th.sub;x.fillText('すぐに',m,y);y+=sm*1.6;
 x.font='800 '+big+'px '+F;x.fillStyle=th.ac;lb.forEach(function(l){x.fillText(l,m,y);y+=big*1.35});
 x.font='600 '+sm+'px '+F;x.fillStyle=th.sub;x.fillText('をする。',m,y);y+=sm*1.6;
 if(gl){y+=sm*1.2;x.font='500 '+(sm*.85)+'px '+F;x.fillText(wrap(x,'目標：'+gl,mx)[0],m,y)}
 c.toBlob(function(bl){if(!bl)return;if(url)URL.revokeObjectURL(url);url=URL.createObjectURL(bl);$('wp-img').src=url;$('wp-img').height=Math.round(240*H/W);$('wp-dl').href=url});
}
var tm;['wp-a','wp-b','wp-g','wp-t','wp-s'].forEach(function(i){$(i).addEventListener('input',function(){clearTimeout(tm);tm=setTimeout(draw,150)})});
draw();
})();
"""
PAGES.append({"path": "templates/wallpaper", "title": t["title"], "seo_title": t["seo"], "date": "2026-10-09", "desc": t["desc"],
              "body": wp_body + "<script>" + WP_JS + "</script>", "parent": PARENT,
              "css": CSS + ".wp-2{display:grid;grid-template-columns:1fr 1fr;gap:10px}.wp-2 label{display:block;margin-bottom:6px}"
                     ".wp-pv{display:flex;justify-content:center;margin:8px 0}.wp-pv img{width:240px;height:auto;border-radius:22px;border:1px solid var(--border);box-shadow:0 8px 28px rgba(0,0,0,.4);background:var(--card)}"})

# ---------- 一覧 /templates/ ----------
HUB_FAQ = [("勉強のテンプレートは無料ですか？", "無料です。登録も不要で、広告もありません。印刷するか、PDFで保存して使えます。"),
           ("学校や勉強会でコピーして配ってもいいですか？", "個人の勉強や、授業・勉強会でコピーして配るのは自由です。テンプレートそのものの販売や、ほかのサイトでの再配布はご遠慮ください。"),
           ("スマホだけで使えますか？", "使えます。画面で書き込んでからPDFで保存すると、印刷しなくても手元に残せます。毎日の記録をスマホでつけたい人は、Web版の勉強の記録シートも使えます。"),
           ("ほかの勉強テンプレートと何が違いますか？", "どのテンプレートも、効果が研究で確かめられた勉強法（思い出す練習・分散学習・if-thenプラン・過去の実績からの見積もり・進み具合の記録）をもとに欄を決めています。各ページに根拠の研究と出典を載せています。")]
cards = "".join(f'<a class="tp-card" href="/templates/{x["id"]}/"><b>{E(x["title"])}</b><span>{E(x["hub"])}</span><small>根拠：{E(x["basis"])}</small></a>' for x in T)
hub_ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "CollectionPage", "name": "勉強のテンプレート集", "url": BASE + "templates/", "inLanguage": "ja", "dateModified": DATE, "publisher": PUB,
     "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": f'{BASE}templates/{x["id"]}/', "name": x["title"]} for i, x in enumerate(T)]}},
    faq_ld(HUB_FAQ)]}
hub_body = ('<script type="application/ld+json">' + json.dumps(hub_ld, ensure_ascii=False).replace("</", "<\\/") + "</script>"
            '<p class="answer"><strong>独学の科学の勉強テンプレートは、効果が研究で確かめられた勉強法をそのまま紙で使える形にしたものです。</strong>無料・登録不要・広告なしで、A4で印刷でき、PDFでも保存できます。</p>'
            f'<div class="tp-grid">{cards}</div>'
            '<h2>おすすめの組み合わせ</h2>'
            '<ol class="steps"><li><a href="/templates/study-plan/">勉強計画表</a>でやることを書き出し、期限に間に合うか確かめる</li>'
            '<li><a href="/templates/if-then/">if-thenプランシート</a>で毎日始める場面を1つ決め、<a href="/templates/wallpaper/">壁紙</a>にしてロック画面に置く</li>'
            '<li>勉強した日は<a href="/templates/recall-note/">暗記ノート</a>で思い出す練習をし、<a href="/templates/review-calendar/">復習カレンダー</a>の日にもう一度</li>'
            '<li><a href="/templates/study-log/">勉強の記録表</a>に1行残し、実際にかかった時間を次の計画に使う</li></ol>'
            '<p>どの勉強法が研究で効くとわかっているかは、<a href="/hayami/">勉強法の早見表</a>にまとめています。</p>'
            + HOWTO + faq_html(HUB_FAQ))
hub_css = (CSS + ".tp-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px;margin:18px 0 28px}"
           ".tp-card{display:flex;flex-direction:column;gap:6px;background:var(--card);border:1px solid var(--border);border-top:3px solid var(--accent);border-radius:14px;padding:16px 18px;text-decoration:none;color:var(--text)}"
           ".tp-card span{color:var(--text)!important}.tp-card:hover,.tp-card:focus-visible{border-color:var(--accent)}.tp-card b{font-size:16px;line-height:1.5}.tp-card span{font-size:14px;line-height:1.7}.tp-card small{font-size:12px;color:var(--muted)}")
PAGES.insert(0, {"path": "templates", "title": "勉強のテンプレート集（無料・印刷できる）",
                 "seo_title": "勉強のテンプレート集｜無料で印刷・PDF保存できる学習計画表・記録表・暗記ノート",
                 "date": DATE, "desc": "勉強計画表・勉強の記録表・暗記ノート・復習カレンダー・if-thenプランシートを無料で印刷・PDF保存できます。スマホのロック画面用の壁紙も作れます。どれも効果が研究で確かめられた勉強法がもと。登録不要・広告なし。",
                 "body": hub_body, "css": hub_css})
