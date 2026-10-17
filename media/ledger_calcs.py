"""お金と心理の「計算表」記事に、数字を入れるとその場で計算する道具を差し込む（記事の表はそのまま残す）。

  python3 media/ledger_calcs.py && python3 media/build.py ledger

別ページにせず記事の中に置くのは、同じ用事のページを2つに分けないため（docs/quality/tool.md の「1テーマ1ページ」）。
記事の <!--lcalc-->…<!--/lcalc--> を毎回作り直す（冪等）。差し込む位置は CALCS の anchor（記事の表の前の段落）の直前。
文言・数字は記事に載っているものだけを使う。入力はブラウザの外に送らない（特別費の表だけ、この端末の localStorage に残す）。
新しい計算表を足すときは CALCS に1件足す。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "sites/ledger"

CSS = ("<style>.lc{background:var(--card);border:1.5px solid var(--text);border-radius:14px;padding:18px;margin:22px 0}"
       ".lc h3{font-size:17px;margin:0 0 4px}.lc .lc-lead{font-size:13px;color:var(--muted);line-height:1.7;margin:0 0 6px}"
       ".lc label{display:block;font-size:15px;font-weight:800;margin:14px 0 4px}.lc label small{display:block;font-weight:400;font-size:12px;color:var(--muted);line-height:1.6}"
       ".lc input{width:100%;font:inherit;font-size:16px;padding:12px;border:1px solid var(--border);border-radius:10px;background:#fff;color:var(--text)}"
       ".lc input:focus-visible,.lc button:focus-visible{outline:3px solid var(--accent2);outline-offset:2px}"
       ".lc-out{margin-top:16px;border-top:1px solid var(--border);padding-top:14px}.lc-k{font-size:13px;color:var(--muted);margin:0}"
       ".lc-big{font-size:28px;font-weight:900;color:var(--accent);margin:2px 0 6px;line-height:1.3}.lc-sub{font-size:14px;line-height:1.8;margin:6px 0 0}"
       ".lc-err{font-size:14px;font-weight:700;color:var(--accent);margin:0}"
       ".lc-meter{position:relative;height:14px;background:var(--bg);border:1px solid var(--border);border-radius:4px;margin:14px 0 22px}"
       ".lc-meter>span{display:block;height:100%;background:var(--accent2);border-radius:3px}"
       ".lc-meter i{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--text)}.lc-meter i b{position:absolute;top:20px;left:-12px;font-size:12px;font-style:normal;font-weight:400;white-space:nowrap}"
       ".lc-t{width:100%;border-collapse:collapse;font-size:14px;margin:10px 0 0}.lc-t th,.lc-t td{border:1px solid var(--border);padding:8px;text-align:left}.lc-t th{background:var(--bg);font-weight:700}"
       ".lc-grid{display:grid;grid-template-columns:1fr;gap:0 14px}@media(min-width:620px){.lc-grid{grid-template-columns:1fr 1fr}}"
       ".lc-n{font-size:12px;color:var(--muted);line-height:1.7;margin:10px 0 0}"
       ".lc-clear{font:inherit;font-size:14px;background:none;border:0;color:var(--link);text-decoration:underline;padding:10px 0;cursor:pointer}</style>")

NUM = ("function num(s){s=String(s).replace(/[０-９．，]/g,function(c){return String.fromCharCode(c.charCodeAt(0)-65248)}).replace(/[,\\s円]/g,'');if(!s)return 0;"
       "var m=s.match(/^(\\d+(?:\\.\\d+)?)(万(\\d+)?)?$/);if(!m)return NaN;var v=parseFloat(m[1]);if(m[2])v=v*10000+(m[3]?parseInt(m[3],10):0);return v}"
       "function yen(v){return Math.round(v).toLocaleString('ja-JP')+'円'}function $(i){return document.getElementById(i)}")

EMERGENCY = """<div class="lc" id="lc-em"><h3>自分の数字で計算する</h3>
<p class="lc-lead">金額を入れると、その場で月数を出します。入力した金額は送信も保存もしません。「30万」のような書き方でも入れられます。</p>
<div class="lc-grid">
<label for="em-a">A すぐ使える預金<small>普通預金など、数日以内に引き出せるお金の合計</small></label><input id="em-a" inputmode="numeric" placeholder="例：600000" autocomplete="off">
<label for="em-b">B 固定費（月）<small>家賃・光熱費・通信費・保険料・ローンの返済など</small></label><input id="em-b" inputmode="numeric" placeholder="例：120000" autocomplete="off">
<label for="em-c">C 削れない変動費（月）<small>食費や日用品のうち、切り詰めても必要な額</small></label><input id="em-c" inputmode="numeric" placeholder="例：60000" autocomplete="off">
<label for="em-s">毎月貯金に回せる額（任意）<small>目標までの月数を出します</small></label><input id="em-s" inputmode="numeric" placeholder="例：20000" autocomplete="off">
</div>
<div class="lc-out" id="em-out" aria-live="polite" aria-atomic="true"><p class="lc-k">A・B・Cを入れると、ここに結果が出ます。</p></div>
<noscript><p class="lc-n">計算にはJavaScriptを使います。下の表で同じ計算ができます。</p></noscript>
</div>
<script>(function(){%NUM%
function calc(){var a=num($('em-a').value),b=num($('em-b').value),c=num($('em-c').value),s=num($('em-s').value),o=$('em-out');
 if([a,b,c,s].some(isNaN)){o.innerHTML='<p class="lc-err">金額は数字で入れてください（例：600000、60万）。</p>';return}
 var d=b+c;if(d<=0||!$('em-a').value){o.innerHTML='<p class="lc-k">A・B・Cを入れると、ここに結果が出ます。</p>';return}
 var m=a/d,w=Math.min(100,m/6*100);
 var rows=[1,3,6].map(function(k){var g=d*k,lack=g-a;return'<tr><th scope="row">'+k+'か月分</th><td>'+yen(g)+'</td><td>'+(lack<=0?'届いています':'あと'+yen(lack)+(s>0?'（毎月'+yen(s)+'で約'+Math.ceil(lack/s)+'か月）':''))+'</td></tr>'}).join('');
 o.innerHTML='<p class="lc-k">手元の貯金は、生活費（D＝'+yen(d)+'）の</p><p class="lc-big">約'+(Math.floor(m*10)/10)+'か月分</p>'+
  '<div class="lc-meter" role="img" aria-label="6か月分を端とした目盛りで、約'+(Math.floor(m*10)/10)+'か月分"><span style="width:'+w.toFixed(1)+'%"></span><i style="left:16.6%"><b>1か月</b></i><i style="left:50%"><b>3か月</b></i><i style="left:99%"><b>6か月</b></i></div>'+
  '<table class="lc-t"><tr><th scope="col">目標</th><th scope="col">必要な額</th><th scope="col">いまとの差</th></tr>'+rows+'</table>'+
  '<p class="lc-n">目標の月数に、研究で決まった正解はありません。下の「続けるためのコツ」のチェック表で、自分の状況から決めてください。</p>'}
['em-a','em-b','em-c','em-s'].forEach(function(i){$(i).addEventListener('input',calc)});calc()})();</script>"""

IRREGULAR_ITEMS = [
    ("年1回の税金・保険料", "自動車税、年払いの保険、固定資産税など"),
    ("車検・免許や資格の更新", "2年ごとなら、1回の額を2で割って入れる"),
    ("冠婚葬祭", "お祝い・香典・服装や移動の費用も。去年の回数分"),
    ("帰省・旅行", "交通費・宿泊費・手土産"),
    ("家電・家具の買い替え", "壊れそうな物と、およその値段"),
    ("医療・歯科・メガネ", "定期的な検診や、作り替えの時期"),
    ("子どもや家族の行事", "入学・進級の準備、発表会、修学旅行"),
    ("年会費・年払いの契約", "カードの年会費、年払いのサブスク、会員費"),
    ("季節の衣類・寝具", "冬物のコート、子どもの靴の買い替え"),
    ("贈り物・記念日", "誕生日、お歳暮やお中元、季節の行事"),
]
IRREGULAR = ("""<div class="lc" id="lc-ir"><h3>1年分を入れて、毎月の取り分けを計算する</h3>
<p class="lc-lead">下の10項目に、去年の明細などを見て<b>1年分の額</b>を入れます。当てはまらない項目は空欄のままで構いません。入力はこの端末のブラウザの中だけに残り、どこにも送られません。</p>
<div class="lc-grid">"""
    + "".join(f'<label for="ir-{i}">{i + 1} {n}<small>{h}</small></label><input id="ir-{i}" class="ir-v" inputmode="numeric" placeholder="1年分（円）" autocomplete="off">'
              for i, (n, h) in enumerate(IRREGULAR_ITEMS))
    + """</div>
<div class="lc-out" id="ir-out" aria-live="polite" aria-atomic="true"><p class="lc-k">金額を入れると、ここに結果が出ます。</p></div>
<button type="button" class="lc-clear" id="ir-clear">入力をすべて消す</button>
<noscript><p class="lc-n">計算にはJavaScriptを使います。下の表で同じ計算ができます。</p></noscript>
</div>
<script>(function(){%NUM%
var K='ledger-irregular-v1',els=[].slice.call(document.querySelectorAll('.ir-v'));
try{var sv=JSON.parse(localStorage.getItem(K)||'[]');els.forEach(function(e,i){if(sv[i])e.value=sv[i]})}catch(e){}
function calc(){var v=els.map(function(e){return num(e.value)}),o=$('ir-out');
 try{localStorage.setItem(K,JSON.stringify(els.map(function(e){return e.value})))}catch(e){}
 if(v.some(isNaN)){o.innerHTML='<p class="lc-err">金額は数字で入れてください（例：30500、5万）。</p>';return}
 var t=v.reduce(function(a,b){return a+b},0);if(t<=0){o.innerHTML='<p class="lc-k">金額を入れると、ここに結果が出ます。</p>';return}
 var n=v.filter(function(x){return x>0}).length;
 o.innerHTML='<p class="lc-k">特別費の1年分（'+n+'項目）は'+yen(t)+'。毎月取り分ける額は</p><p class="lc-big">約'+yen(Math.ceil(t/12))+'</p>'+
  '<p class="lc-sub">給料日に、この額を生活費とは別の口座や袋に移します。一度に無理なら、まず半分の約'+yen(Math.ceil(t/24))+'から始めても構いません。</p>'+
  '<p class="lc-n">見積もりは「節約できたらいいな」でなく、去年の実際の額で入れると、少なめに見積もるずれを防げます。</p>'}
els.forEach(function(e){e.addEventListener('input',calc)});
$('ir-clear').addEventListener('click',function(){if(!confirm('入力した金額をすべて消しますか？'))return;els.forEach(function(e){e.value=''});calc()});
calc()})();</script>""")

CALCS = [
    ("emergency-savings-months-calculator", '<p class="t">まず、自分の数字を入れる表です。', EMERGENCY),
    ("irregular-expenses-monthly-setaside-calculator", '<p class="t">次に、書き出した額を計算表に入れます。', IRREGULAR),
]


def main():
    for slug, anchor, block in CALCS:
        f = SITE / slug / "index.html"
        h = f.read_text()
        if "<!--lcalc-->" in h:
            h = h[:h.index("<!--lcalc-->")] + h[h.index("<!--/lcalc-->") + len("<!--/lcalc-->"):]
        if anchor not in h:
            print("skip (anchor not found):", slug)
            continue
        new = "<!--lcalc-->" + CSS + block.replace("%NUM%", NUM) + "<!--/lcalc-->"
        h = h.replace(anchor, new + anchor, 1)
        f.write_text(h)
        print("calc:", slug)


if __name__ == "__main__":
    main()
