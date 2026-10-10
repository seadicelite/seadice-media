"""お金と心理のWebツールページ。実行すると media/ledger-pages.json に書き込む(extras.pages が /{path}/ を書き出す)。

  python3 media/ledger_tools.py && python3 media/build.py ledger

文言・数字は、出典照合済みの記事に載っているものだけを使う。記録はブラウザの localStorage だけに保存し、送信しない。
iOSアプリ Spendology(SEADICE/~/Developer/ファイナンス系/spendology)の Web 版。アプリの紹介は App Store 公開後に足す。
新しいツールを足すときは docs/quality/tool.md のページの型に合わせ、PAGES に追加する。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "https://ledger.seadice.win/wait-list/"

CHECKS = [
    ("お腹が空いている", "食べてから決める"),
    ("不安・落ち込み・イライラが強い", "気分が落ち着いてから決める"),
    ("「残り○分」「本日限り」に急かされている", "締め切りを外して、本当に欲しいかを考える"),
    ("買い物リストや予定に無かった物", "リストに書いて、次の買い物の日に決める"),
    ("今月の予算を決めていない、または超えている", "予算の残りを確かめてから決める"),
    ("使う場面を、日付つきで言えない", "使う日が決まるまで保留する"),
]

FAQ = [
    ("衝動買いを防ぐには、何時間待てばいいですか？",
     "研究で決まった正解の時間はありません。このページでは24時間を基本に、買う前チェックで2個以上当てはまったときは3日を目安にしています。大切なのは長さより、その場で決めずに、空腹や焦りなど「いまの状態」から離れてから選び直すことです。"),
    ("待つリストに入れた物や金額は、どこかに送られますか？",
     "送られません。記録はこのブラウザの中（localStorage）だけに保存され、SEADICEのサーバーには届きません。ブラウザの履歴やサイトデータを消すと、記録も消えます。"),
    ("買う前チェックで「2個以上なら待つ」の根拠は？",
     "2個という数は研究で決まった基準ではなく、目安です。チェックの各項目は、空腹で食べ物以外の物も多く手に取った研究、不安や落ち込み・時間の圧力と衝動買いの関連、買い物リストや予算のように前もって決める工夫の研究にもとづいています。"),
    ("「守れたお金」は貯金と同じですか？",
     "同じではありません。待ったあとに「買わない」と決めた物の金額を足したもので、実際に口座に貯まったお金ではありません。そのお金を貯金に回したいときは、決めた日に別の口座へ移すと、守れたお金が本当の貯金になります。"),
]

SOURCES = [
    ("Plantinga, A., Krijnen, J. M. T., Zeelenberg, M., & Breugelmans, S. M. (2018). Evidence for opportunity cost neglect in the poor. Journal of Behavioral Decision Making, 31(1), 65-73.", "https://doi.org/10.1002/bdm.2041"),
    ("Xu, A. J., Schwarz, N., & Wyer, R. S., Jr. (2015). Hunger promotes acquisition of nonfood objects. Proceedings of the National Academy of Sciences, 112(9), 2688-2692.", "https://doi.org/10.1073/pnas.1417712112"),
    ("Davydenko, M., Kolbuszewska, M., & Peetz, J. (2021). A meta-analysis of financial self-control strategies. PLoS ONE, 16(7), e0253938.", "https://doi.org/10.1371/journal.pone.0253938"),
    ("Zhao, Y., Li, Y., Wang, N., Zhou, R., & Luo, X. (2022). A Meta-Analysis of Online Impulsive Buying and the Moderating Effect of Economic Development Level. Information Systems Frontiers, 24, 1667–1688.", "https://doi.org/10.1007/s10796-021-10170-4"),
    ("Cheema, A., & Bagchi, R. (2011). The Effect of Goal Visualization on Goal Pursuit. Journal of Marketing, 75(2), 109-123.", "https://doi.org/10.1509/jmkg.75.2.109"),
]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "衝動買いを防ぐ待つリスト", "url": URL, "applicationCategory": "FinanceApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "欲しい物をすぐ買わずにリストへ入れ、24時間・3日・1週間たってから「まだ欲しい？」と決める衝動買い対策ツール。研究にもとづく買う前チェック6項目、買わずに守れたお金の記録つき。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}
LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")

checks_html = "".join(
    f'<label class="wl-ck"><input type="checkbox" name="ck" value="{i}"><span>{q}<small>{a}</small></span></label>'
    for i, (q, a) in enumerate(CHECKS))
faq_html = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}</summary><p>{a}</p></details>' for i, (q, a) in enumerate(FAQ))
src_html = "".join(f'<li>{t} <a href="{u}" target="_blank" rel="noopener">{u}</a></li>' for t, u in SOURCES)

BODY = """<script type="application/ld+json">%LD%</script>
<p>欲しい物を見つけたら、すぐ買わずにこのリストへ入れます。24時間・3日・1週間たったら、もう一度このページを開いて「まだ欲しい？」に答えます。買わなかった金額は「守れたお金」として貯まっていきます。無料・広告なし・登録不要です。</p>

<div class="wl-saved" aria-live="polite"><span>守れたお金</span><b id="wl-total">0円</b><em id="wl-count">買わなかった物 0件</em></div>

<form class="wl-box" id="wl-form" onsubmit="return false" novalidate>
<label for="wl-name">欲しい物</label>
<input id="wl-name" maxlength="40" placeholder="例：ワイヤレスイヤホン" autocomplete="off" enterkeyhint="next">
<label for="wl-price">金額（円）</label>
<input id="wl-price" inputmode="numeric" maxlength="10" placeholder="3000" autocomplete="off" enterkeyhint="next">
<p class="wl-year" id="wl-year" aria-live="polite"></p>
<label for="wl-alt">買わなかったら、そのお金で何をする？</label>
<input id="wl-alt" maxlength="60" placeholder="例：週末の外食に回す、旅行の資金にする" autocomplete="off" enterkeyhint="done">
<p class="wl-hint">「買わない」を「お金を別のことに取っておく」と言い換えると、買うと答える人が平均62.8%から47.8%に減った実験があります。</p>
<fieldset class="wl-cks"><legend>買う前チェック（いまの自分に当てはまるもの）</legend>%CHECKS%</fieldset>
<p class="wl-warn" id="wl-warn" aria-live="polite"></p>
<fieldset class="wl-wait"><legend>どれくらい待つ？</legend>
<label><input type="radio" name="wait" value="24" checked><span>24時間</span></label>
<label><input type="radio" name="wait" value="72"><span>3日</span></label>
<label><input type="radio" name="wait" value="168"><span>1週間</span></label>
</fieldset>
<p class="wl-err" id="wl-err" role="alert"></p>
<button type="button" id="wl-add">待つリストに入れる</button>
<p class="wl-n">記録はこのブラウザの中だけに保存され、どこにも送られません。通知は届かないので、待つ時間が終わったらこのページを開いてください。</p>
</form>

<div id="wl-ready"></div>
<h2 class="wl-h">待っている物</h2>
<div id="wl-waiting"><p class="wl-empty">まだ何も入っていません。カートに入れる前に、ここへ入れてみてください。</p></div>
<details class="wl-hist"><summary>決めた記録</summary><div id="wl-done"><p class="wl-empty">まだありません。</p></div></details>
<noscript><p class="note">このツールはJavaScriptを使います。説明と計算の目安は、下の文章で読めます。</p></noscript>

<p class="answer">衝動買いは、その場で決めずに時間を置くと防ぎやすくなります。空腹・落ち込み・「本日限り」の焦りは衝動買いと結びついていて、待つあいだにその状態から離れて選び直せます。</p>

<h2>このツールのしくみと根拠</h2>
<ul>
<li><b>待つリスト</b>：その場では決めず、時間を置いてから「まだ欲しい？」に答えます。買い物リストや予算のように「誘惑の前に決めておく」工夫は、29の研究のまとめで、支出を減らし貯金を増やす方向に中くらいの効果がありました（d=0.57）。<a href="/impulse-buying-pre-purchase-checklist/">解説記事</a></li>
<li><b>買う前チェック</b>：空腹にした人は、食べ物ではない無料のクリップを平均3.93個取り、満腹の人（2.31個）より多く取りました。不安や落ち込み、時間の圧力も衝動買いと関係していました。<a href="/impulse-buying-pre-purchase-checklist/">解説記事</a></li>
<li><b>「今だけ」の表示</b>：ネットの衝動買いを調べた54の研究のまとめでは、販売促進（相関0.37）と「残りわずか」の表示（0.32）が衝動買いと結びついていました。<a href="/online-impulse-buying-tips/">解説記事</a></li>
<li><b>買わなかったら何をする？</b>：買わない選択を「お金を別のことに取っておく」と言い換えると、買う人が平均62.8%から47.8%に減りました（米国の5つの実験）。<a href="/sale-overbuying-opportunity-cost/">解説記事</a></li>
<li><b>守れたお金</b>：進み具合を目に見える形で示すと、ゴール近くでがんばりが落ちにくいという実験があります（お金ではなく握力の課題）。<a href="/savings-goal-visualization-progress-bar-research/">解説記事</a></li>
</ul>
<p class="note">待つ時間の長さ（24時間・3日・1週間）と「チェック2個以上で待つ」は、研究で決まった基準ではなく目安です。効果が示されたのは研究で試された方法で、このツール自体の効果を確かめたものではありません。</p>

<h2>使い方の例</h2>
<table class="wl-t"><caption>入れた物と、待ったあとの決め方の例</caption>
<tr><th>欲しい物・金額</th><th>当てはまったチェック</th><th>待つ時間</th><th>待ったあと</th></tr>
<tr><td>セールのスニーカー 8,000円</td><td>「本日限り」・予定に無かった</td><td>3日</td><td>セールが終わっても欲しくなかった → 買わない（守れたお金 +8,000円）</td></tr>
<tr><td>夜に見つけた本 1,500円</td><td>なし</td><td>24時間</td><td>翌日も読みたかった → 買う</td></tr>
<tr><td>疲れた日のコスメ 4,000円</td><td>落ち込み・空腹</td><td>3日</td><td>同じ物を持っていた → 買わない（+4,000円）</td></tr>
</table>
<p>予定外の買い物の年間の金額は「1回の金額 × 1か月の回数 × 12」で出せます。たとえば3,000円の予定外の買い物が月4回あると、1年で144,000円になります。</p>

<h2>よくある質問</h2>
%FAQ%

<div class="sources"><h2>出典</h2><ol>%SRC%</ol></div>

<script>
(function(){
var K='ledger-wait-list-v1',H=36e5,items=[];
function load(){try{items=JSON.parse(localStorage.getItem(K)||'[]')}catch(e){items=[]}}
function save(){try{localStorage.setItem(K,JSON.stringify(items));return true}catch(e){alert('このブラウザでは記録を保存できませんでした（プライベートブラウズなど）。');return false}}
function $(i){return document.getElementById(i)}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
function yen(v){return Math.round(v).toLocaleString('ja-JP')+'円'}
function num(s){s=String(s).replace(/[０-９]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-65248)}).replace(/[^0-9]/g,'');return s?parseInt(s,10):0}
function remain(t){var d=t-Date.now();if(d<=0)return'待つ時間が終わりました';var h=Math.floor(d/H),m=Math.floor(d%H/6e4);return h>=24?'あと'+Math.floor(h/24)+'日'+(h%24)+'時間':h>=1?'あと'+h+'時間'+m+'分':'あと'+Math.max(1,m)+'分'}
function day(t){var d=new Date(t);return d.getFullYear()+'/'+(d.getMonth()+1)+'/'+d.getDate()}
function hits(){return document.querySelectorAll('#wl-form input[name=ck]:checked').length}
function onCheck(){var n=hits(),w=$('wl-warn');w.textContent=n>=2?n+'個当てはまりました。今日は決めずに、時間を置くのがおすすめです（3日を選びました）。':'';if(n>=2&&!window.__wlTouched){document.querySelector('input[name=wait][value="72"]').checked=true}}
function onPrice(){var p=num($('wl-price').value);$('wl-year').textContent=p>0?'この金額の予定外の買い物が月2回あると1年で'+yen(p*24)+'、月4回なら'+yen(p*48)+'です。':''}
function add(){var n=$('wl-name').value.trim(),p=num($('wl-price').value),e=$('wl-err');
 if(!n){e.textContent='欲しい物の名前を入れてください';$('wl-name').focus();return}
 if(p<=0){e.textContent='金額を数字で入れてください';$('wl-price').focus();return}
 e.textContent='';var h=parseInt(document.querySelector('input[name=wait]:checked').value,10),now=Date.now();
 items.push({id:now,name:n,price:p,alt:$('wl-alt').value.trim(),hits:hits(),created:now,until:now+h*H,status:'waiting'});
 if(!save()){items.pop();return}
 $('wl-form').reset();window.__wlTouched=false;onCheck();onPrice();render();
 $('wl-waiting').scrollIntoView({behavior:'smooth',block:'start'})}
function find(id){for(var i=0;i<items.length;i++)if(items[i].id===id)return items[i]}
function act(id,a){var it=find(id);if(!it)return;var prev=JSON.stringify(it),bak=items.slice();
 if(a==='skip'||a==='buy'){it.status=a==='skip'?'skipped':'bought';it.decided=Date.now()}
 else if(a==='more'){it.until=Date.now()+24*H}
 else if(a==='undo'){it.status='waiting';delete it.decided}
 else if(a==='del'){if(!confirm('「'+it.name+'」を記録ごと消しますか？'))return;items=items.filter(function(x){return x.id!==id})}
 if(!save()){items=bak;Object.assign(it,JSON.parse(prev));return}render()}
function render(){var now=Date.now(),ready=[],wait=[],done=[],tot=0,cnt=0;
 items.forEach(function(it){if(it.status==='waiting'){(it.until<=now?ready:wait).push(it)}else{done.push(it);if(it.status==='skipped'){tot+=it.price;cnt++}}});
 $('wl-total').textContent=yen(tot);$('wl-count').textContent='買わなかった物 '+cnt+'件';
 ready.sort(function(a,b){return a.until-b.until});wait.sort(function(a,b){return a.until-b.until});done.sort(function(a,b){return b.decided-a.decided});
 $('wl-ready').innerHTML=ready.length?'<h2 class="wl-h">待つ時間が終わりました</h2>'+
ready.map(function(it){return'<div class="wl-card wl-r"><p class="wl-t1"><b>'+
esc(it.name)+'</b><span>'+
yen(it.price)+'</span></p>'+
(it.alt?'<p class="wl-alt">買わなかったら：'+
esc(it.alt)+'</p>':'')+'<p class="wl-q">まだ欲しいですか？</p><div class="wl-btns"><button type="button" data-a="skip" data-id="'+
it.id+'" class="wl-skip">買わない</button><button type="button" data-a="buy" data-id="'+
it.id+'">やっぱり買う</button></div><button type="button" class="wl-link" data-a="more" data-id="'+
it.id+'">もう24時間待つ</button></div>'}).join(''):'';
 $('wl-waiting').innerHTML=wait.length?wait.map(function(it){var r=Math.min(1,Math.max(0,(now-it.created)/(it.until-it.created)));return'<div class="wl-card"><p class="wl-t1"><b>'+
esc(it.name)+'</b><span>'+
yen(it.price)+'</span></p><div class="wl-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="'+
Math.round(r*100)+'" aria-label="待った時間"><span style="width:'+
(r*100).toFixed(1)+'%"></span></div><p class="wl-rem">'+
remain(it.until)+(it.hits>=2?'　<em>チェック'+
it.hits+'個</em>':'')+'</p>'+
(it.alt?'<p class="wl-alt">買わなかったら：'+
esc(it.alt)+'</p>':'')+'<div class="wl-sm"><button type="button" class="wl-link" data-a="skip" data-id="'+
it.id+'">買わないと決める</button><button type="button" class="wl-link" data-a="del" data-id="'+
it.id+'">削除</button></div></div>'}).join(''):'<p class="wl-empty">'+
(ready.length?'いま待っている物はありません。':'まだ何も入っていません。カートに入れる前に、ここへ入れてみてください。')+'</p>';
 $('wl-done').innerHTML=done.length?'<ul class="wl-dl">'+
done.map(function(it){return'<li><span>'+
day(it.decided||it.created)+'</span><b>'+
(it.status==='skipped'?'買わなかった':'買った')+'</b><span>'+
esc(it.name)+'　'+
yen(it.price)+'</span><button type="button" class="wl-link" data-a="undo" data-id="'+
it.id+'">戻す</button><button type="button" class="wl-link" data-a="del" data-id="'+
it.id+'">削除</button></li>'}).join('')+'</ul>':'<p class="wl-empty">まだありません。</p>'}
document.addEventListener('click',function(e){var b=e.target.closest('[data-a]');if(b)act(Number(b.getAttribute('data-id')),b.getAttribute('data-a'))});
$('wl-add').addEventListener('click',add);
$('wl-form').addEventListener('change',function(e){if(e.target.name==='ck')onCheck();if(e.target.name==='wait')window.__wlTouched=true});
$('wl-price').addEventListener('input',onPrice);
['wl-name','wl-price'].forEach(function(id,i){$(id).addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();$(i?'wl-alt':'wl-price').focus()}})});
$('wl-alt').addEventListener('keydown',function(e){if(e.key==='Enter'){e.preventDefault();e.target.blur()}});
load();render();setInterval(render,6e4);
document.addEventListener('visibilitychange',function(){if(!document.hidden){load();render()}});
window.addEventListener('storage',function(e){if(e.key===K){load();render()}});
})();
</script>"""
BODY = BODY.replace("%LD%", LD).replace("%CHECKS%", checks_html).replace("%FAQ%", faq_html).replace("%SRC%", src_html)

CSS = (".wl-saved{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 12px;background:var(--card);border:1px solid var(--accent2);border-left:6px solid var(--accent2);border-radius:12px;padding:14px 18px;margin:18px 0}"
       ".wl-saved span{font-size:14px;color:var(--muted)}.wl-saved b{font-size:30px;font-weight:900;color:var(--accent2)}.wl-saved em{font-style:normal;font-size:13px;color:var(--muted)}"
       ".wl-box{background:var(--card);border:1.5px solid var(--text);border-radius:14px;padding:18px;margin:18px 0}"
       ".wl-box>label{display:block;font-size:15px;font-weight:800;margin:14px 0 6px}.wl-box>label:first-child{margin-top:0}"
       ".wl-box input:not([type]),.wl-box input[inputmode]{width:100%;font:inherit;font-size:16px;padding:12px;border:1px solid var(--border);border-radius:10px;background:#fff;color:var(--text)}"
       ".wl-box input:focus-visible,.wl-box button:focus-visible,.wl-card button:focus-visible{outline:3px solid var(--accent2);outline-offset:2px}"
       ".wl-year,.wl-hint{font-size:13px;color:var(--muted);line-height:1.7;margin:6px 0 0}.wl-year:empty{display:none}"
       ".wl-cks,.wl-wait{border:0;margin:16px 0 0;padding:0}.wl-cks legend,.wl-wait legend{font-size:15px;font-weight:800;margin-bottom:6px}"
       ".wl-ck{display:flex;gap:10px;align-items:flex-start;padding:10px 4px;border-top:1px solid var(--border);font-size:15px;cursor:pointer}.wl-ck input{width:20px;height:20px;margin-top:3px;flex:none;accent-color:var(--accent)}"
       ".wl-ck small{display:none;font-size:13px;color:var(--accent);font-weight:700}.wl-ck input:checked+span small{display:block}"
       ".wl-warn{font-size:14px;font-weight:700;color:var(--accent);margin:10px 0 0}.wl-warn:empty,.wl-err:empty{display:none}"
       ".wl-wait{display:flex;flex-wrap:wrap;gap:8px}.wl-wait legend{width:100%}.wl-wait label{cursor:pointer}.wl-wait input{position:absolute;opacity:0}"
       ".wl-wait span{display:inline-block;font-size:15px;padding:10px 16px;border:1.5px solid var(--border);border-radius:999px;background:#fff}.wl-wait input:checked+span{border-color:var(--text);background:var(--text);color:var(--card);font-weight:800}.wl-wait input:focus-visible+span{outline:3px solid var(--accent2);outline-offset:2px}"
       ".wl-err{font-size:14px;font-weight:700;color:var(--accent);margin:12px 0 0}"
       ".wl-box button{display:block;width:100%;font:inherit;font-size:17px;font-weight:800;margin-top:16px;padding:14px;border:1.5px solid var(--text);border-radius:12px;background:#E9C46A;color:var(--text);cursor:pointer;min-height:52px}"
       ".wl-n{font-size:12px;color:var(--muted);margin-top:10px;line-height:1.7}"
       ".wl-h{font-size:18px;margin:26px 0 10px}"
       ".wl-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 16px;margin:10px 0}.wl-r{border:2px solid var(--accent)}"
       ".wl-t1{display:flex;justify-content:space-between;gap:10px;font-size:16px;margin:0}.wl-t1 span{white-space:nowrap;font-weight:700}"
       ".wl-alt{font-size:14px;color:var(--accent2);margin:6px 0 0}.wl-q{font-size:16px;font-weight:800;margin:12px 0 8px}"
       ".wl-btns{display:grid;grid-template-columns:1fr 1fr;gap:10px}.wl-btns button{font:inherit;font-size:16px;font-weight:700;padding:12px;border:1.5px solid var(--text);border-radius:10px;background:#fff;color:var(--text);cursor:pointer;min-height:48px}.wl-btns .wl-skip{background:var(--accent2);border-color:var(--accent2);color:#fff}"
       ".wl-link{font:inherit;font-size:14px;background:none;border:0;color:var(--link);text-decoration:underline;padding:10px 6px;cursor:pointer}"
       ".wl-bar{height:10px;background:var(--bg);border:1px solid var(--border);border-radius:999px;overflow:hidden;margin:10px 0 4px}.wl-bar span{display:block;height:100%;background:var(--accent)}"
       ".wl-rem{font-size:14px;margin:0}.wl-rem em{font-style:normal;color:var(--accent);font-size:13px}.wl-sm{display:flex;gap:4px;margin-top:2px}"
       ".wl-empty{font-size:14px;color:var(--muted);background:var(--card);border:1px dashed var(--border);border-radius:12px;padding:16px;margin:10px 0}"
       ".wl-hist{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:12px 16px;margin:16px 0}.wl-hist summary{cursor:pointer;font-weight:700;font-size:15px;padding:4px 0}"
       ".wl-dl{list-style:none;margin:8px 0 0;padding:0}.wl-dl li{display:flex;flex-wrap:wrap;align-items:center;gap:4px 10px;font-size:14px;border-top:1px solid var(--border);padding:6px 0}.wl-dl b{font-size:13px}"
       ".answer{font-size:15px;margin:28px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".xbody ul li{font-size:15px;margin:8px 0}.xbody ul a{color:var(--link)}"
       ".wl-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.wl-t caption{text-align:left;font-size:13px;color:var(--muted);margin-bottom:6px}"
       ".wl-t th,.wl-t td{border:1px solid var(--border);padding:10px;text-align:left;vertical-align:top}.wl-t th{background:var(--card)}"
       ".note{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}.note a,.sources a{color:var(--link)}"
       ".xbody>details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}.xbody>details summary{cursor:pointer;font-weight:700;font-size:15px}.xbody>details p{font-size:15px;margin-top:8px}"
       ".sources{margin-top:48px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;word-break:break-all}"
       "@media(max-width:520px){.wl-t{font-size:13px}.wl-t th,.wl-t td{padding:8px}}")

PAGES = [{"path": "wait-list", "title": "衝動買いを防ぐ「待つリスト」",
          "seo_title": "衝動買いを防ぐ待つリスト｜研究にもとづく買う前チェックと、守れたお金の記録",
          "date": "2026-10-11",
          "desc": "欲しい物をすぐ買わずにリストへ入れ、24時間・3日・1週間たってから「まだ欲しい？」と決める衝動買い対策ツール。空腹・気分・「今だけ」を確かめる買う前チェックつき。無料・登録不要・記録はブラウザ内だけ。",
          "body": BODY, "css": CSS}]

if __name__ == "__main__":
    f = ROOT / "media/ledger-pages.json"
    ps = json.loads(f.read_text()) if f.exists() else []
    keep = [p for p in ps if p["path"] not in {x["path"] for x in PAGES}]
    f.write_text(json.dumps(keep + PAGES, ensure_ascii=False, indent=2) + "\n")
    print("wrote", [p["path"] for p in PAGES])
