"""関係の記録（サンプル版）を sites/umbra/kiroku-sample/index.html に書き出す。アプリ化の判断用の試作。

  python3 media/umbra_kiroku_sample.py

- 検索に出さない（noindex）。sitemap・llms.txt・ナビには載せない（extras を通さず単体のHTMLとして書く）
- 記録の項目は危険な相手のサイン チェックリスト（umbra_tools.REDFLAG）と同じ
- 記録はこの端末のブラウザ（localStorage）にだけ保存し、どこにも送らない
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from umbra_tools import CONTACTS, GROUPS, REDFLAG  # noqa: E402

E = html.escape
ROOT = Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "media/umbra.json").read_text())
T = cfg["theme"]
posts = {p["slug"]: p for p in json.loads((ROOT / "media/umbra-posts.json").read_text())}

items = {i: {"g": g, "t": t, "s": s, "n": n, "title": posts[s]["title"] if s else ""} for i, g, t, s, n in REDFLAG}
boxes = ""
for g, gl in GROUPS:
    boxes += f'<p class="gl">{E(gl)}</p>' + "".join(f'<label><input type="checkbox" value="{i}">{E(t)}</label>' for i, gg, t, _, _ in REDFLAG if gg == g)

ITEMS_JS = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
CONTACTS_JS = json.dumps(CONTACTS, ensure_ascii=False).replace("</", "<\\/")

page = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>メモ</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:{T["bg"]};--card:{T["card"]};--accent:{T["accent"]};--border:{T["border"]};--text:{T["text"]};--muted:{T["muted"]};--link:{T["link"]}}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,'Helvetica Neue',sans-serif;line-height:1.7;-webkit-text-size-adjust:100%}}
header{{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 16px;background:var(--bg);border-bottom:1px solid var(--border)}}
header b{{font-size:15px}}
.exit{{border:0;border-radius:999px;background:#E5534B;color:#fff;font-weight:800;font-size:14px;padding:10px 16px;cursor:pointer}}
main{{max-width:640px;margin:0 auto;padding:16px 16px 64px}}
h1{{font-size:22px;margin:8px 0 6px}}h2{{font-size:17px;margin:32px 0 10px}}
p{{font-size:15px}}.muted{{color:var(--muted);font-size:13px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:16px;margin:14px 0}}
.warn{{border-left:4px solid var(--accent)}}.alert{{border-left:4px solid #E5534B}}
.gl{{font-weight:700;margin:16px 0 4px;font-size:14px;color:var(--muted)}}
label{{display:flex;gap:12px;align-items:flex-start;padding:10px 2px;border-top:1px solid var(--border);font-size:15px;line-height:1.6;cursor:pointer}}
input[type=checkbox]{{width:22px;height:22px;flex:0 0 22px;margin-top:1px;accent-color:var(--accent)}}
input[type=date],textarea{{width:100%;font:inherit;font-size:16px;color:var(--text);background:var(--bg);border:1px solid var(--border);border-radius:10px;padding:10px}}
textarea{{min-height:96px;margin-top:6px}}
.btn{{display:block;width:100%;margin-top:14px;padding:14px;border:0;border-radius:12px;background:var(--accent);color:var(--bg);font-size:16px;font-weight:800;cursor:pointer}}
.sub{{background:none;border:1px solid var(--border);color:var(--text);font-weight:700}}
.entry{{border-top:1px solid var(--border);padding:12px 0}}.entry:first-child{{border-top:0}}
.entry .d{{font-weight:800}}.entry ul{{margin:6px 0 0 1.2em;font-size:14px}}.entry .m{{font-size:14px;margin-top:6px;white-space:pre-wrap;color:var(--text);opacity:.9}}
.del{{background:none;border:0;color:var(--muted);font-size:13px;text-decoration:underline;cursor:pointer;padding:8px 0}}
.row{{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-top:1px solid var(--border);font-size:14px}}.row:first-child{{border-top:0}}
.row b{{white-space:nowrap}}.hl{{color:var(--accent)}}
a{{color:var(--link)}}.tl-contact{{margin:8px 0 0 1.2em;font-size:15px;line-height:1.9}}.tl-contact a{{font-weight:700}}
.ok{{color:var(--accent);font-weight:700;font-size:14px;min-height:1.5em;margin-top:8px}}
button:focus-visible,a:focus-visible,input:focus-visible,textarea:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
</style>
</head>
<body>
<header><b>関係の記録 <span class="muted">サンプル</span></b><button type="button" class="exit" id="exit">すぐ閉じる</button></header>
<main>
<h1>関係の記録（サンプル版）</h1>
<p>恋人やパートナーとの間で起きたことを、日付つきで記録します。あとから見返すと、同じことが繰り返されているかに気づけます。記録は相談するときの手がかりにもなります。</p>
<div class="card warn"><p><strong>記録はこの端末のブラウザにだけ保存されます。</strong>どこにも送信しません。そのかわり、この端末やブラウザを相手と共有していると、見られるおそれがあります。心配なときは記録しないか、使い終わったら「すべての記録を消す」を押してください。</p>
<p class="muted" style="margin-top:8px">右上の「すぐ閉じる」を押すと、関係のないページに切り替わります。</p></div>

<h2>今日の記録</h2>
<form class="card" id="f" onsubmit="return false">
<label style="display:block;border:0;padding:0" for="dt">日付</label><input type="date" id="dt">
{boxes}
<label style="display:block;border:0;padding:12px 0 0" for="memo">メモ（任意。言われたことや、そのときの気持ち）</label>
<textarea id="memo" maxlength="1000"></textarea>
<button type="button" class="btn" id="save">記録する</button>
<p class="ok" id="ok" aria-live="polite"></p>
</form>

<div id="safety"></div>
<h2>くり返し記録されていること</h2>
<div class="card" id="sum"><p class="muted">まだ記録がありません。</p></div>

<h2>これまでの記録</h2>
<div class="card" id="list"><p class="muted">まだ記録がありません。</p></div>

<h2>相談するとき</h2>
<div class="card"><p>記録を文章にまとめてコピーできます。相談窓口で状況を説明するときに使えます。</p>
<button type="button" class="btn sub" id="copy">記録を文章でコピーする</button><p class="ok" id="cok" aria-live="polite"></p>
<p style="margin-top:12px">相談先</p>{CONTACTS}</div>

<h2>記録を消す</h2>
<div class="card"><button type="button" class="btn sub" id="wipe">すべての記録を消す</button>
<p class="muted" style="margin-top:8px">消した記録は元に戻せません。</p></div>

<p class="muted" style="margin-top:24px">このページはサンプル版です。記録の項目は<a href="/redflag-check/">危険な相手のサイン チェックリスト</a>と同じで、出典照合済みの記事の結論にもとづいています。相手を診断したり、ラベルを貼ったりするためのものではありません。</p>
</main>
<script>(function(){{
var I={ITEMS_JS},K='umbra-kiroku-v1',C={CONTACTS_JS};
function load(){{try{{return JSON.parse(localStorage.getItem(K)||'[]')}}catch(e){{return[]}}}}
function store(a){{try{{localStorage.setItem(K,JSON.stringify(a));return true}}catch(e){{return false}}}}
function e(s){{return String(s).replace(/[&<>"]/g,function(c){{return{{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
function today(){{var d=new Date();return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)}}
var dt=document.getElementById('dt');dt.value=today();
function render(){{var a=load().sort(function(x,y){{return x.d<y.d?1:-1}});
 var L=document.getElementById('list'),S=document.getElementById('sum'),F=document.getElementById('safety');
 if(!a.length){{L.innerHTML=S.innerHTML='<p class="muted">まだ記録がありません。</p>';F.innerHTML='';return}}
 L.innerHTML=a.map(function(r){{return '<div class="entry"><p class="d">'+e(r.d)+'</p>'+(r.i.length?'<ul>'+r.i.map(function(i){{return '<li>'+e(I[i]?I[i].t:i)+'</li>'}}).join('')+'</ul>':'')+(r.m?'<p class="m">'+e(r.m)+'</p>':'')+'<button type="button" class="del" data-id="'+r.id+'">この記録を消す</button></div>'}}).join('');
 var n={{}};a.forEach(function(r){{r.i.forEach(function(i){{n[i]=(n[i]||0)+1}})}});
 var ks=Object.keys(n).filter(function(i){{return I[i]}}).sort(function(x,y){{return n[y]-n[x]}});
 S.innerHTML='<p class="muted">記録'+a.length+'件（'+e(a[a.length-1].d)+'〜'+e(a[0].d)+'）</p>'+(ks.length?ks.map(function(i){{var x=I[i];return '<div class="row"><span>'+e(x.t)+(n[i]>=3?'<br><span class="hl">3回以上記録されています。'+(x.n?e(x.n):'')+'</span>':'')+(x.s?'<br><a href="/'+x.s+'/">記事を読む</a>':'')+'</span><b>'+n[i]+'回</b></div>'}}).join(''):'<p class="muted">項目を選んだ記録はまだありません。</p>');
 var now=ks.some(function(i){{return I[i].g==='now'}});
 F.innerHTML=now?'<div class="card alert"><p><strong>暴力や脅しの記録があります。</strong>関係を続けるかどうかより先に、あなたの安全を考えてください。一人で決めて実行する必要はありません。</p>'+C+'</div>':'';
 [].forEach.call(L.querySelectorAll('.del'),function(b){{b.onclick=function(){{if(!confirm('この記録を消しますか？'))return;store(load().filter(function(r){{return r.id!==b.dataset.id}}));render()}}}});
}}
document.getElementById('save').onclick=function(){{
 var ids=[].slice.call(document.querySelectorAll('#f input[type=checkbox]:checked')).map(function(x){{return x.value}}),m=document.getElementById('memo').value.trim(),ok=document.getElementById('ok');
 if(!ids.length&&!m){{ok.textContent='項目を選ぶか、メモを書いてください。';return}}
 var a=load();a.push({{id:Date.now().toString(36),d:dt.value||today(),i:ids,m:m}});
 if(!store(a)){{ok.textContent='このブラウザでは保存できませんでした（プライベートモードなど）。';return}}
 [].forEach.call(document.querySelectorAll('#f input[type=checkbox]'),function(x){{x.checked=false}});document.getElementById('memo').value='';
 ok.textContent='記録しました。';render()}};
document.getElementById('copy').onclick=function(){{var a=load().sort(function(x,y){{return x.d<y.d?-1:1}}),c=document.getElementById('cok');
 if(!a.length){{c.textContent='まだ記録がありません。';return}}
 var t='関係の記録（'+a.length+'件）\\n'+a.map(function(r){{return '\\n■'+r.d+'\\n'+r.i.map(function(i){{return '・'+(I[i]?I[i].t:i)}}).join('\\n')+(r.m?'\\nメモ：'+r.m:'')}}).join('\\n');
 (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){{c.textContent='コピーしました。'}},function(){{c.textContent='コピーできませんでした。'}})}};
document.getElementById('wipe').onclick=function(){{if(!confirm('すべての記録を消します。元に戻せません。よろしいですか？'))return;try{{localStorage.removeItem(K)}}catch(e){{}}render()}};
document.getElementById('exit').onclick=function(){{location.replace('https://www.google.com/search?q=%E4%BB%8A%E6%97%A5%E3%81%AE%E5%A4%A9%E6%B0%97')}};
render();
}})();</script>
</body>
</html>
"""
out = ROOT / "sites/umbra/kiroku-sample/index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(page)
print("wrote", out)
