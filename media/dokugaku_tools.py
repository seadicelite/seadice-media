"""独学の科学のWebツールページ。dokugaku_hayami.py が読み込み、media/dokugaku-pages.json に一緒に書き出す。

数値は記事 /spaced-review-why-it-works/ で出典照合済みの Cepeda ら(2008) の結果だけを使う。
新しいツールを足すときは docs/quality/tool.md のページの型に合わせ、PAGES に追加する。
"""
import json

E_URL = "https://dokugaku.seadice.win/review-timing/"

# Cepedaら(2008): テストまでの日数 → 最もよく残った「学習から復習まで」の日数
POINTS = [(7, 1), (35, 11), (70, 21), (350, 21)]

ld = {"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "復習日の計算機（試験日から逆算）", "url": E_URL, "applicationCategory": "EducationalApplication",
     "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
     "description": "試験日や使う日を入れると、分散学習の研究（Cepedaら 2008）をもとに、1回目の復習に向く日を計算します。無料・広告なし・登録不要。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": "復習は何日後にすればいいですか？",
         "acceptedAnswer": {"@type": "Answer", "text": "使う日までの長さで変わります。Cepedaら（2008）では、1週間後のテストなら1日後、35日後なら11日後、70日後と1年後なら21日後の復習が最もよく残りました。"}},
        {"@type": "Question", "name": "試験まで3日しかないときはどうすればいいですか？",
         "acceptedAnswer": {"@type": "Answer", "text": "研究で確かめられた最短は7日後のテストです。それより短いときは、今日学んで翌日に1回思い出す練習をするのが目安です。テストが近いほど、間をあけるかどうかの差は小さくなります。"}},
        {"@type": "Question", "name": "入力した日付はどこかに送られますか？",
         "acceptedAnswer": {"@type": "Answer", "text": "送られません。計算はすべてブラウザの中で行い、保存もしません。"}}]}]}

LD = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
pts = json.dumps(POINTS)

body = f"""<script type="application/ld+json">{LD}</script>
<p>試験日（覚えたことを使う日）を入れると、1回目の復習に向く日を計算します。無料・広告なし・登録不要で、入力した日付はどこにも送られません。</p>
<form class="rt-box" id="rt" onsubmit="return false">
<label for="rt-d">試験日・使う日</label>
<input type="date" id="rt-d" required>
<label for="rt-s">勉強する日（初めて覚える日）</label>
<input type="date" id="rt-s">
<button type="submit" id="rt-b">復習日を計算する</button>
<div id="rt-out" class="rt-out" aria-live="polite" hidden></div>
</form>
<p class="answer"><strong>目安：使う日が近いほど早めに、遠いほど間をあけて1回目の復習をします。</strong>1週間後なら翌日、約1か月後なら10日後前後、70日以上先なら3週間後です。</p>
<h2>計算のしかた</h2>
<p>分散学習（間をあけた復習）の大規模な実験、Cepedaら（2008）の結果を使っています。約1,350人が雑学知識を覚え、間隔をいろいろ変えて1回復習し、最長1年後にテストを受けました。最適な間隔での復習は、間をあけない復習より正答が64%多くなりました。</p>
<table class="rt-t"><caption>実験で最もよく残った間隔</caption><thead><tr><th>テストまで</th><th>最もよく残った復習のタイミング</th></tr></thead>
<tbody><tr><td>7日後</td><td>学習の1日後</td></tr><tr><td>35日後</td><td>学習の11日後</td></tr><tr><td>70日後</td><td>学習の21日後</td></tr><tr><td>350日後</td><td>学習の21日後</td></tr></tbody></table>
<p>この4点の間の日数は、SEADICEが直線でつないで見積もっています（実験で直接確かめた値ではありません）。7日より短いときは翌日、350日より長いときは21日後を表示します。</p>
<div class="note">実験の対象は大学生などの成人で、課題は雑学知識の暗記でした。計算・作文などの技能や、何度も復習する場合にそのまま当てはまるとは限りません。くわしくは<a href="/spaced-review-why-it-works/">分散学習の記事</a>で解説しています。</div>
<h2>入力例</h2>
<table class="rt-t"><thead><tr><th>勉強する日</th><th>試験日</th><th>1回目の復習</th></tr></thead>
<tbody><tr><td>10月1日</td><td>10月8日（7日後）</td><td>10月2日</td></tr><tr><td>10月1日</td><td>11月5日（35日後）</td><td>10月12日</td></tr><tr><td>10月1日</td><td>12月10日（70日後）</td><td>10月22日</td></tr></tbody></table>
<h2>よくある質問</h2>
<details open><summary>復習は何日後にすればいいですか？</summary><p>使う日までの長さで変わります。Cepedaら（2008）では、1週間後のテストなら1日後、35日後なら11日後、70日後と1年後なら21日後の復習が最もよく残りました。</p></details>
<details><summary>試験まで3日しかないときはどうすればいいですか？</summary><p>研究で確かめられた最短は7日後のテストです。それより短いときは、今日学んで翌日に1回思い出す練習をするのが目安です。テストが近いほど、間をあけるかどうかの差は小さくなります。</p></details>
<details><summary>入力した日付はどこかに送られますか？</summary><p>送られません。計算はすべてブラウザの中で行い、保存もしません。</p></details>
<h2>復習のときにやること</h2>
<p>復習はノートを読み返すより、本を閉じて思い出す方が残ります（<a href="/retrieval-practice-vs-rereading/">思い出す練習の記事</a>）。ほかの勉強法の効き目は<a href="/hayami/">勉強法の効く・効かない早見表</a>にまとめています。</p>
<div class="sources"><h2>出典</h2><ol><li>Cepeda, N. J., Vul, E., Rohrer, D., Wixted, J. T., &amp; Pashler, H. (2008). Spacing effects in learning: A temporal ridgeline of optimal retention. <i>Psychological Science</i>, 19(11), 1095–1102. <a href="https://doi.org/10.1111/j.1467-9280.2008.02209.x" rel="noopener">https://doi.org/10.1111/j.1467-9280.2008.02209.x</a></li></ol></div>
<script>
(function(){{
var P={pts},d=document.getElementById('rt-d'),s=document.getElementById('rt-s'),o=document.getElementById('rt-out');
function iso(t){{var z=new Date(t.getTime()-t.getTimezoneOffset()*6e4);return z.toISOString().slice(0,10)}}
function gap(n){{if(n<=P[0][0])return 1;for(var i=1;i<P.length;i++){{var a=P[i-1],b=P[i];if(n<=b[0])return Math.round(a[1]+(b[1]-a[1])*(n-a[0])/(b[0]-a[0]))}}return P[P.length-1][1]}}
function fmt(t){{return (t.getMonth()+1)+'月'+t.getDate()+'日（'+'日月火水木金土'[t.getDay()]+'）'}}
var t0=new Date();t0.setHours(0,0,0,0);s.value=iso(t0);
document.getElementById('rt').addEventListener('submit',function(){{
 if(!d.value){{d.focus();return}}
 var st=s.value?new Date(s.value+'T00:00'):t0,ex=new Date(d.value+'T00:00'),n=Math.round((ex-st)/864e5);
 o.hidden=false;
 if(n<1){{o.innerHTML='<p>試験日は、勉強する日より後の日付にしてください。</p>';return}}
 if(n<2){{o.innerHTML='<p>試験は翌日です。今日のうちに、本を閉じて思い出す練習を1回してから寝ましょう。</p>';return}}
 var g=Math.min(gap(n),n-1),r=new Date(st.getTime()+g*864e5);
 o.innerHTML='<p class="rt-l">1回目の復習に向く日</p><p class="rt-v">'+fmt(r)+'</p><p>勉強する日の'+g+'日後・試験の'+(n-g)+'日前（試験まで'+n+'日）</p>'+(n<7?'<p class="rt-n">7日より短い期間は研究で確かめられていないため、翌日を目安にしています。</p>':n>350?'<p class="rt-n">350日より長い期間は研究の範囲外のため、21日後を目安にしています。</p>':'');
}});
}})();
</script>"""

css = (".rt-box{background:var(--card);border:1px solid var(--accent);border-radius:16px;padding:20px;margin:20px 0 24px;display:grid;gap:8px}"
       ".rt-box label{font-size:14px;font-weight:700;margin-top:6px}"
       ".rt-box input{font:inherit;font-size:16px;padding:12px;border-radius:10px;border:1px solid var(--border);background:var(--bg);color:var(--text);color-scheme:dark;min-height:48px}"
       ".rt-box button{font:inherit;font-size:16px;font-weight:800;margin-top:12px;padding:14px;border:0;border-radius:12px;background:var(--accent);color:#0B1020;cursor:pointer;min-height:48px}"
       ".rt-out{margin-top:14px;padding-top:14px;border-top:1px solid var(--border);font-size:15px;line-height:1.8}"
       ".rt-l{font-size:13px;color:var(--muted)}.rt-v{font-size:30px;font-weight:900;color:var(--accent);line-height:1.3;margin:2px 0 6px}.rt-n{font-size:13px;color:var(--muted);margin-top:6px}"
       ".answer{font-size:15px;margin:8px 0 18px;padding-left:14px;border-left:3px solid var(--accent)}"
       ".rt-t{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}.rt-t caption{text-align:left;font-size:13px;color:var(--muted);margin-bottom:6px}"
       ".rt-t th,.rt-t td{border:1px solid var(--border);padding:10px;text-align:left}.rt-t th{background:var(--card)}"
       ".note{background:rgba(90,176,255,.07);border:1px solid rgba(90,176,255,.25);border-radius:12px;padding:14px 18px;margin:18px 0;font-size:14px}.note a,.sources a{color:var(--link)}"
       "details{background:var(--card);border:1px solid var(--border);border-radius:12px;margin:10px 0;padding:12px 16px}summary{cursor:pointer;font-weight:700;font-size:15px}details p{font-size:15px;margin-top:8px}"
       ".sources{margin-top:48px;padding-top:20px;border-top:1px solid var(--border)}.sources h2{font-size:14px;color:var(--muted)}.sources li{font-size:12px;color:var(--muted);margin:8px 0 8px 18px;word-break:break-all}")

PAGES = [{"path": "review-timing", "title": "復習日の計算機（試験日から逆算）",
          "seo_title": "復習の間隔 計算｜試験日から逆算して1回目の復習日を出す（分散学習の研究をもとに）", "date": "2026-10-06",
          "desc": "試験日を入れると、1回目の復習に向く日を計算。1週間後なら翌日、約1か月後なら10日後前後。約1,350人の分散学習の研究（Cepedaら 2008）をもとにした無料・広告なしのツール。",
          "body": body, "css": css}]
