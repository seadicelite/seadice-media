"""ふたりの日記（関係の記録のサンプル版）を sites/umbra/kiroku-sample/index.html に書き出す。アプリ化の判断用の試作。

  python3 media/umbra_kiroku_sample.py

- 検索に出さない（noindex）。sitemap・llms.txt・ナビには載せない（extras を通さず単体のHTMLとして書く）
- 気分（4段階）を1タップで残し、あったことは短い言葉のボタンで選ぶ。気になる項目は危険な相手のサイン チェックリスト（umbra_tools.REDFLAG）と同じで、
  同じ項目が30日に3回以上あったときだけ、記事の結論をやさしく添える
- 記録はこの端末のブラウザ（localStorage）にだけ保存し、どこにも送らない
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from umbra_tools import CONTACTS, REDFLAG  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "media/umbra.json").read_text())
T = cfg["theme"]

# 気になること: REDFLAG の id → ボタンに出す短い話し言葉
SHORT = {"c1": "会うのを嫌がられた", "c2": "行動を制限された", "c3": "スマホを見られた", "c4": "お金のことで縛られた", "c5": "断ったら怒られた", "c6": "相談できる人が減った",
         "m1": "「言ってない」と言われた", "m2": "謝られたけど、また同じこと", "m3": "優しい時とひどい時の差がつらい", "m4": "バカにされた",
         "e1": "連絡や好意が多すぎる", "e2": "約束を守ってくれない", "e3": "謝ってくれない", "n1": "叩かれた・物に当たられた", "n2": "脅すようなことを言われた"}
# SHORT に無い新しい項目は、チェックリストの文をそのまま使う（REDFLAG に足すときは SHORT にも短い言葉を足す）
GOOD = {"g1": "楽しかった", "g2": "話を聞いてくれた", "g3": "安心できた", "g4": "ちゃんと話し合えた", "g5": "ありがとうと言えた"}
items = {i: {"l": SHORT.get(i, t), "g": g, "n": n, "s": s} for i, g, t, s, n in REDFLAG}
items.update({i: {"l": l, "g": "good"} for i, l in GOOD.items()})
ITEMS_JS = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
CONTACTS_JS = json.dumps(CONTACTS, ensure_ascii=False).replace("</", "<\\/")
good_chips = "".join(f'<button type="button" class="chip" data-i="{i}">{l}</button>' for i, l in GOOD.items())
bad_chips = "".join(f'<button type="button" class="chip" data-i="{i}">{SHORT.get(i, t)}</button>' for i, _, t, *_ in sorted(REDFLAG, key=lambda r: r[1] == "now"))  # 重い項目は最後に

page = f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>メモ</title>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--bg:{T["bg"]};--card:{T["card"]};--accent:{T["accent"]};--border:{T["border"]};--text:{T["text"]};--muted:{T["muted"]};--link:{T["link"]};
--m1:#5FC79B;--m2:#8A93A6;--m3:#E8B04B;--m4:#E5737A}}
body{{background:var(--bg);color:var(--text);font-family:-apple-system,'Helvetica Neue',sans-serif;line-height:1.7;-webkit-text-size-adjust:100%}}
header{{position:sticky;top:0;z-index:10;display:flex;align-items:center;justify-content:space-between;padding:10px 16px;background:var(--bg);border-bottom:1px solid var(--border)}}
header b{{font-size:16px;letter-spacing:.04em}}
.exit{{border:1px solid var(--border);border-radius:999px;background:var(--card);color:var(--muted);font-size:13px;padding:8px 14px;cursor:pointer}}
main{{max-width:560px;margin:0 auto;padding:20px 16px 64px}}
h1{{font-size:24px;margin:4px 0 16px}}h2{{font-size:16px;margin:28px 0 10px}}
.muted{{color:var(--muted);font-size:13px}}
.card{{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:18px;margin:12px 0}}
.moods{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}}
.mood{{display:flex;flex-direction:column;align-items:center;gap:8px;padding:14px 4px;border:2px solid transparent;border-radius:16px;background:var(--bg);color:var(--text);font-size:13px;font-weight:700;white-space:nowrap;letter-spacing:-.02em;cursor:pointer}}
.mood i{{display:block;width:34px;height:34px;border-radius:50%;background:var(--c)}}
.mood[aria-pressed=true]{{border-color:var(--c);background:color-mix(in srgb,var(--c) 14%,var(--bg))}}
.step[hidden]{{display:none}}.step{{margin-top:18px}}
.step p{{font-size:14px;color:var(--muted);margin-bottom:8px}}
.chips{{display:flex;flex-wrap:wrap;gap:8px}}
.chip{{border:1px solid var(--border);border-radius:999px;background:var(--bg);color:var(--text);font-size:14px;padding:9px 14px;cursor:pointer}}
.chip[aria-pressed=true]{{border-color:var(--accent);background:color-mix(in srgb,var(--accent) 18%,var(--bg))}}
textarea{{width:100%;min-height:80px;font:inherit;font-size:16px;color:var(--text);background:var(--bg);border:1px solid var(--border);border-radius:14px;padding:12px}}
.btn{{display:block;width:100%;margin-top:16px;padding:15px;border:0;border-radius:14px;background:var(--accent);color:var(--bg);font-size:16px;font-weight:800;cursor:pointer}}
.ok{{color:var(--accent);font-weight:700;font-size:14px;min-height:1.4em;margin-top:8px;text-align:center}}
.dots{{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;text-align:center}}
.dot{{display:flex;flex-direction:column;align-items:center;gap:4px;font-size:11px;color:var(--muted);background:none;border:0;cursor:pointer;padding:4px 0}}
.dot i{{display:block;width:26px;height:26px;border-radius:50%;background:var(--c,transparent);border:1px dashed var(--border)}}
.dot.has i{{border:0}}
.note{{border-left:4px solid var(--m3)}}.note.red{{border-left-color:var(--m4)}}.note p{{font-size:15px}}.note a{{color:var(--link)}}
.entry{{border-top:1px solid var(--border);padding:12px 0;font-size:14px}}.entry:first-child{{border-top:0;padding-top:0}}
.entry .h{{display:flex;align-items:center;gap:8px;font-weight:700}}.entry .h i{{width:14px;height:14px;border-radius:50%;background:var(--c)}}
.entry .t{{margin-top:4px;opacity:.85}}.entry .m{{margin-top:4px;white-space:pre-wrap}}
.del{{background:none;border:0;color:var(--muted);font-size:12px;text-decoration:underline;cursor:pointer;padding:6px 0 0}}
details.card summary{{cursor:pointer;font-weight:700;font-size:15px}}
.sub{{background:none;border:1px solid var(--border);color:var(--text);font-weight:700}}
.tl-contact{{margin:8px 0 0 1.2em;font-size:14px;line-height:1.9}}.tl-contact a{{color:var(--link);font-weight:700}}
button:focus-visible,a:focus-visible,textarea:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
</style>
</head>
<body>
<header><b>メモ</b><button type="button" class="exit" id="exit">閉じる</button></header>
<main>
<h1>今日はどんな日だった？</h1>
<div class="card">
<div class="moods" role="group" aria-label="今日の気分">
<button type="button" class="mood" data-m="1" style="--c:var(--m1)" aria-pressed="false"><i></i>よかった</button>
<button type="button" class="mood" data-m="2" style="--c:var(--m2)" aria-pressed="false"><i></i>ふつう</button>
<button type="button" class="mood" data-m="3" style="--c:var(--m3)" aria-pressed="false"><i></i>もやもや</button>
<button type="button" class="mood" data-m="4" style="--c:var(--m4)" aria-pressed="false"><i></i>つらかった</button>
</div>
<div class="step" id="s-good" hidden><p>よかったことがあれば</p><div class="chips">{good_chips}</div></div>
<div class="step" id="s-bad" hidden><p>あてはまることがあれば（いくつでも）</p><div class="chips">{bad_chips}</div></div>
<div class="step" id="s-memo" hidden><p>ひとことメモ（なくてもOK）</p><textarea id="memo" maxlength="500" placeholder="言われたこと、そのときの気持ちなど"></textarea>
<button type="button" class="btn" id="save">残す</button></div>
<p class="ok" id="ok" aria-live="polite"></p>
</div>

<div id="notes"></div>

<h2>最近の2週間</h2>
<div class="card"><div class="dots" id="dots"></div><p class="muted" style="margin-top:10px">色をタップすると、その日の記録が見られます。</p><div id="day" style="margin-top:10px"></div></div>

<details class="card"><summary>これまでの記録</summary><div id="list" style="margin-top:12px"></div></details>
<details class="card"><summary>設定・相談先</summary>
<p style="font-size:14px;margin-top:12px">記録はこの端末のブラウザにだけ保存され、どこにも送られません。相手と端末を共有しているときは、見られることがあるので気をつけてください。「閉じる」を押すと、天気の検索ページに切り替わります。</p>
<button type="button" class="btn sub" id="copy">記録を文章でコピー（相談するとき用）</button><p class="ok" id="cok" aria-live="polite"></p>
<p style="font-size:14px;margin-top:12px">相談先</p>{CONTACTS}
<button type="button" class="btn sub" id="wipe" style="margin-top:20px">すべての記録を消す</button>
<p class="muted" style="margin-top:12px">サンプル版です。気になることの項目は、<a href="/redflag-check/" style="color:var(--link)">危険な相手のサイン チェックリスト</a>と同じく、出典照合済みの記事にもとづいています。</p>
</details>
</main>
<script>(function(){{
var I={ITEMS_JS},C={CONTACTS_JS},K='umbra-diary-v2',ML={{1:'よかった',2:'ふつう',3:'もやもや',4:'つらかった'}},MC={{1:'var(--m1)',2:'var(--m2)',3:'var(--m3)',4:'var(--m4)'}};
var mood=0,sel={{}};
function $(id){{return document.getElementById(id)}}
function load(){{try{{return JSON.parse(localStorage.getItem(K)||'[]')}}catch(e){{return[]}}}}
function store(a){{try{{localStorage.setItem(K,JSON.stringify(a));return true}}catch(e){{return false}}}}
function e(s){{return String(s).replace(/[&<>"]/g,function(c){{return{{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]}})}}
function ds(d){{return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2)}}
function md(s){{var p=s.split('-');return (+p[1])+'/'+(+p[2])}}
[].forEach.call(document.querySelectorAll('.mood'),function(b){{b.onclick=function(){{mood=+b.dataset.m;
 [].forEach.call(document.querySelectorAll('.mood'),function(x){{x.setAttribute('aria-pressed',x===b)}});
 $('s-good').hidden=mood>2;$('s-bad').hidden=mood<2;$('s-memo').hidden=false;$('ok').textContent=''}}}});
[].forEach.call(document.querySelectorAll('.chip'),function(b){{b.setAttribute('aria-pressed','false');b.onclick=function(){{var i=b.dataset.i;sel[i]=!sel[i];b.setAttribute('aria-pressed',!!sel[i])}}}});
function entryHtml(r,del){{var t=r.i.map(function(i){{return I[i]?I[i].l:''}}).filter(Boolean).join('・');
 return '<div class="entry"><div class="h" style="--c:'+MC[r.v]+'"><i></i>'+md(r.d)+'　'+ML[r.v]+'</div>'+(t?'<p class="t">'+e(t)+'</p>':'')+(r.m?'<p class="m">'+e(r.m)+'</p>':'')+(del?'<button type="button" class="del" data-id="'+r.id+'">この記録を消す</button>':'')+'</div>'}}
function render(){{var a=load().sort(function(x,y){{return x.d<y.d?1:x.d>y.d?-1:(x.id<y.id?1:-1)}}),by={{}};
 a.forEach(function(r){{(by[r.d]=by[r.d]||[]).push(r)}});
 var h='',d=new Date();d.setDate(d.getDate()-13);
 for(var k=0;k<14;k++){{var s=ds(d),rs=by[s],v=rs?Math.max.apply(null,rs.map(function(r){{return r.v}})):0;
  h+='<button type="button" class="dot'+(v?' has':'')+'" data-d="'+s+'"'+(v?' style="--c:'+MC[v]+'"':'')+' aria-label="'+md(s)+(v?' '+ML[v]:' 記録なし')+'"><i></i>'+md(s)+'</button>';d.setDate(d.getDate()+1)}}
 $('dots').innerHTML=h;
 [].forEach.call(document.querySelectorAll('.dot'),function(b){{b.onclick=function(){{var rs=by[b.dataset.d];$('day').innerHTML=rs?rs.map(function(r){{return entryHtml(r)}}).join(''):'<p class="muted">'+md(b.dataset.d)+'の記録はありません。</p>'}}}});
 $('list').innerHTML=a.length?a.map(function(r){{return entryHtml(r,1)}}).join(''):'<p class="muted">まだ記録がありません。</p>';
 [].forEach.call(document.querySelectorAll('.del'),function(b){{b.onclick=function(){{if(!confirm('この記録を消しますか？'))return;store(load().filter(function(r){{return r.id!==b.dataset.id}}));render()}}}});
 var lim=new Date();lim.setDate(lim.getDate()-30);var L=ds(lim),n={{}},hard=false;
 a.forEach(function(r){{if(r.d<L)return;r.i.forEach(function(i){{if(!I[i]||I[i].g==='good')return;n[i]=(n[i]||0)+1;if(I[i].g==='now')hard=true}})}});
 var o='';
 if(hard)o+='<div class="card note red"><p><strong>怖い思いをした日があったんですね。</strong>まず、あなたの安全がいちばん大事です。一人で抱えなくて大丈夫です。</p>'+C+'</div>';
 Object.keys(n).filter(function(i){{return n[i]>=3&&I[i].g!=='now'}}).sort(function(x,y){{return n[y]-n[x]}}).forEach(function(i){{var x=I[i];
  o+='<div class="card note"><p><strong>この30日で「'+e(x.l)+'」が'+n[i]+'回ありました。</strong></p><p style="margin-top:6px">'+e(x.n)+'</p>'+(x.s?'<p style="margin-top:6px"><a href="/'+x.s+'/">くわしく読む</a></p>':'')+'</div>'}});
 $('notes').innerHTML=o}}
$('save').onclick=function(){{if(!mood)return;
 var ids=Object.keys(sel).filter(function(i){{if(!sel[i]||!I[i])return false;var g=I[i].g==='good';return mood===2||(mood===1?g:!g)}});
 var a=load();a.push({{id:Date.now().toString(36),d:ds(new Date()),v:mood,i:ids,m:$('memo').value.trim()}});
 if(!store(a)){{$('ok').textContent='このブラウザでは保存できませんでした（プライベートモードなど）';return}}
 mood=0;sel={{}};$('memo').value='';
 [].forEach.call(document.querySelectorAll('.mood,.chip'),function(x){{x.setAttribute('aria-pressed','false')}});
 $('s-good').hidden=$('s-bad').hidden=$('s-memo').hidden=true;$('ok').textContent='残しました';render()}};
$('copy').onclick=function(){{var a=load().sort(function(x,y){{return x.d<y.d?-1:1}});
 if(!a.length){{$('cok').textContent='まだ記録がありません';return}}
 var t='記録（'+a.length+'件）\\n'+a.map(function(r){{var s=r.i.map(function(i){{return I[i]?I[i].l:''}}).filter(Boolean).join('、');return '\\n■'+r.d+'　'+ML[r.v]+(s?'\\n'+s:'')+(r.m?'\\nメモ：'+r.m:'')}}).join('\\n');
 (navigator.clipboard?navigator.clipboard.writeText(t):Promise.reject()).then(function(){{$('cok').textContent='コピーしました'}},function(){{$('cok').textContent='コピーできませんでした'}})}};
$('wipe').onclick=function(){{if(!confirm('すべての記録を消します。元に戻せません。よろしいですか？'))return;try{{localStorage.removeItem(K)}}catch(e){{}}$('day').innerHTML='';render()}};
$('exit').onclick=function(){{location.replace('https://www.google.com/search?q=%E4%BB%8A%E6%97%A5%E3%81%AE%E5%A4%A9%E6%B0%97')}};
render();
}})();</script>
</body>
</html>
"""
out = ROOT / "sites/umbra/kiroku-sample/index.html"
out.parent.mkdir(exist_ok=True)
out.write_text(page)
print("wrote", out)
