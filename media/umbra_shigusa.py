"""しぐさ・ボディランゲージ索引(/shigusa/)を生成する。

データは media/umbra-shigusa.json(items=索引, quiz=4択。quizのcは正解を先頭に)。
実行: python3 media/umbra_shigusa.py && python3 media/build.py umbra
出力: media/umbra-pages.json(extras.pages が /shigusa/ を書き出す)
"""
import json, html
E = html.escape
from pathlib import Path
ROOT = str(Path(__file__).resolve().parent.parent) + "/"
_data = json.load(open(ROOT + "media/umbra-shigusa.json"))
D = [(x["part"], x["gesture"], x["belief"], x["level"], x["text"], x["slug"]) for x in _data["items"]]
Q = [(x["q"], x["c"], x["e"], x["slug"]) for x in _data["quiz"]]
LV = {"a": "手がかりになる", "b": "状況しだい", "c": "当てにならない"}
imgs = json.load(open(ROOT + "media/umbra-images.json"))
def th(s):
    i = imgs.get(s)
    if not i: return "", ""
    u = i["src640"] if "src640" in i else f"{i['raw']}&w=240&h=240&fit=crop&q=70&fm=webp"
    cr = f'<p class="cr">写真：<a href="{E(i.get("page",""))}" rel="nofollow noopener" target="_blank">{E(i.get("artist",""))}</a>（{E(i.get("license",""))}）</p>' if i.get("page") else ""
    return f'<img class="th" src="{E(u)}" alt="" width="96" height="96" loading="lazy" decoding="async">', cr
posts = {p["slug"]: p for p in json.load(open(ROOT + "media/umbra-posts.json"))}
for *_, s in D: assert s in posts, s
for *_, s in Q: assert s in posts, s
PART_ORDER = ["目・視線", "表情", "手・触れる", "姿勢・距離", "体の動き", "声・会話", "連絡・行動"]
D.sort(key=lambda x: PART_ORDER.index(x[0]) if x[0] in PART_ORDER else len(PART_ORDER))
parts = []
for x in D:
    if x[0] not in parts: parts.append(x[0])
items = "".join(
 f'<li class="sg{" hasth" if th(s)[0] else ""}" data-p="{E(p)}" data-k="{E(g+b+t)}">{th(s)[0]}<div class="sgx"><p class="sg-h"><span class="sg-part">{E(p)}</span><span class="lv lv-{l}">{LV[l]}</span></p>'
 f'<h3>{E(g)}</h3><p class="sg-b">よく言われる意味：{E(b)}</p><p>{E(t)}</p><a href="/{s}/">記事を読む：{E(posts[s]["title"])}</a>{th(s)[1]}</div></li>' for p, g, b, l, t, s in D)
chips = '<button type="button" class="chip on" data-f="">すべて</button>' + "".join(f'<button type="button" class="chip" data-f="{E(p)}">{E(p)}</button>' for p in parts)
qdata = json.dumps([{"q": q, "c": c, "e": e, "u": f"/{s}/", "t": posts[s]["title"]} for q, c, e, s in Q], ensure_ascii=False).replace("</", "<\\/")
body = f'''<p>気になったしぐさから、研究でわかっていることをすぐに調べられます。4択クイズで、思い込みとのズレを確かめることもできます。どのしぐさも、1つだけで相手の本音は決まりません。</p>
<div class="tabs" role="tablist"><button type="button" role="tab" id="t1" aria-selected="true" aria-controls="p1">しぐさを調べる</button><button type="button" role="tab" id="t2" aria-selected="false" aria-controls="p2">4択クイズ</button></div>
<section id="p1" role="tabpanel" aria-labelledby="t1">
<h2>しぐさを調べる</h2>
<p class="note">読みやすさは3段階です。「手がかりになる」でも、それだけで本音は決まりません。</p>
<ul class="legend"><li><span class="lv lv-a">手がかりになる</span>傾向として研究で確認されている</li><li><span class="lv lv-b">状況しだい</span>理由が複数あり、意味を1つに決められない</li><li><span class="lv lv-c">当てにならない</span>研究で通説が支持されていない</li></ul>
<label class="sr" for="q">しぐさを検索</label><input id="q" type="search" placeholder="例：目、腕、触る、声" autocomplete="off">
<div class="chips">{chips}</div>
<p id="cnt" class="note" aria-live="polite"></p>
<ul class="sgl" id="list">{items}</ul>
</section>
<section id="p2" role="tabpanel" aria-labelledby="t2" hidden>
<h2>4択クイズ</h2>
<div id="quiz" aria-live="polite"><noscript><p>クイズを遊ぶにはJavaScriptを有効にしてください。</p></noscript></div>
</section>
<h2>このページについて</h2>
<p>内容は、しぐさと本音で公開している記事（それぞれ論文などの出典を確認済み）をもとにしています。特定の人を診断したり、ラベルを貼ったりするためのものではありません。相手の気持ちは、しぐさより言葉と行動の積み重ねで確かめてください。</p>
<script>
(function(){{
var Q={qdata};
var t1=document.getElementById('t1'),t2=document.getElementById('t2'),p1=document.getElementById('p1'),p2=document.getElementById('p2');
function tab(n){{var a=n===1;t1.setAttribute('aria-selected',a);t2.setAttribute('aria-selected',!a);p1.hidden=!a;p2.hidden=a;if(!a&&!started)start();}}
t1.onclick=function(){{tab(1)}};t2.onclick=function(){{tab(2)}};
var q=document.getElementById('q'),cnt=document.getElementById('cnt'),f='',li=[].slice.call(document.querySelectorAll('.sg'));
function filt(){{var s=q.value.trim(),n=0;li.forEach(function(e){{var ok=(!f||e.dataset.p===f)&&(!s||e.dataset.k.indexOf(s)>=0||e.textContent.indexOf(s)>=0);e.hidden=!ok;if(ok)n++}});cnt.textContent=n?n+'件':'見つかりませんでした。別の言葉で探してみてください。'}}
q.oninput=filt;
[].forEach.call(document.querySelectorAll('.chip'),function(b){{b.onclick=function(){{f=b.dataset.f;[].forEach.call(document.querySelectorAll('.chip'),function(x){{x.classList.toggle('on',x===b);x.setAttribute('aria-pressed',x===b)}});filt()}}}});
var box=document.getElementById('quiz'),started=false,order,i,score;
function sh(a){{a=a.slice();for(var k=a.length-1;k>0;k--){{var j=Math.floor(Math.random()*(k+1)),t=a[k];a[k]=a[j];a[j]=t}}return a}}
function esc(s){{var d=document.createElement('div');d.textContent=s;return d.innerHTML}}
function start(){{started=true;order=sh(Q).slice(0,10);i=0;score=0;show()}}
function show(){{if(i>=order.length)return end();var x=order[i],ch=sh(x.c);
box.innerHTML='<p class="qn">第'+(i+1)+'問 / 全'+order.length+'問</p><p class="qq">'+esc(x.q)+'</p><div class="qc">'+ch.map(function(c){{return '<button type="button" class="qb">'+esc(c)+'</button>'}}).join('')+'</div><div class="qr"></div>';
[].forEach.call(box.querySelectorAll('.qb'),function(b){{b.onclick=function(){{ans(b,x)}}}});box.querySelector('.qq').focus&&0}}
function ans(b,x){{var ok=b.textContent===x.c[0];if(ok)score++;
[].forEach.call(box.querySelectorAll('.qb'),function(e){{e.disabled=true;if(e.textContent===x.c[0]){{e.classList.add('right');e.textContent='正解：'+e.textContent}}else if(e===b){{e.classList.add('wrong');e.textContent='あなたの答え：'+e.textContent}}}});
box.querySelector('.qr').innerHTML='<p class="res">'+(ok?'正解です':'不正解です')+'</p><p>'+esc(x.e)+'</p><p><a href="'+x.u+'">記事を読む：'+esc(x.t)+'</a></p><button type="button" class="nx">'+(i+1<order.length?'次の問題へ':'結果を見る')+'</button>';
var n=box.querySelector('.nx');n.onclick=function(){{i++;show()}};n.focus()}}
function end(){{var m=score>=8?'研究でわかっていることをよく押さえています。':score>=5?'通説と研究のズレに気づき始めています。':'しぐさの通説は、研究では当てにならないものが多いのです。';
box.innerHTML='<p class="qq">'+order.length+'問中 '+score+'問 正解</p><p>'+m+'</p><button type="button" class="nx" id="again">もう一度挑戦する</button> <button type="button" class="nx sub" id="look">しぐさを調べる</button>';
document.getElementById('again').onclick=start;document.getElementById('look').onclick=function(){{tab(1);t1.focus()}};document.getElementById('again').focus()}}
filt();
}})();
</script>'''
css = (".tabs{display:flex;gap:8px;margin:20px 0 4px;border-bottom:1px solid var(--border)}"
 ".tabs button{font:inherit;font-size:15px;font-weight:700;background:none;color:var(--muted);border:0;border-bottom:3px solid transparent;padding:12px 14px;cursor:pointer}"
 ".tabs button[aria-selected=true]{color:var(--accent);border-bottom-color:var(--accent)}"
 "button:focus-visible,input:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"
 ".sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}"
 "#q{width:100%;box-sizing:border-box;font:inherit;font-size:16px;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin:8px 0 12px}"
 ".chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px}"
 ".chip{font:inherit;font-size:14px;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:999px;padding:8px 14px;cursor:pointer}"
 ".chip.on{border-color:var(--accent);color:var(--accent)}"
 ".legend{list-style:none;margin:8px 0 16px!important;padding:0}.legend li{font-size:14px;margin:6px 0}.legend .lv{margin-right:8px}"
 ".sgl{list-style:none;margin:8px 0 0!important;padding:0;display:grid;gap:12px}"
 ".sg{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:16px 18px;margin:0!important}"
 ".sg.hasth{display:flex;gap:14px;align-items:flex-start}.th{width:96px;height:96px;object-fit:cover;border-radius:10px;flex:none;background:var(--border)}.sgx{min-width:0}.cr{font-size:12px!important;color:var(--muted);margin:8px 0 0!important}.cr a{font-size:12px!important;color:var(--muted)!important}"
 "@media(max-width:480px){.th{width:72px;height:72px}}"
 ".sg h3{font-size:17px;margin:6px 0 4px}.sg p{font-size:15px;line-height:1.8;margin:6px 0}.sg .sg-b{color:var(--muted);font-size:14px}.sg a{font-size:14px;color:var(--link)}"
 ".sg-h{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:0!important}.sg-part{font-size:12px;color:var(--muted)}"
 ".lv{display:inline-block;font-size:12px;font-weight:700;border-radius:999px;padding:3px 10px;border:1px solid}"
 ".lv-a{color:#7FD6A4;border-color:#7FD6A4}.lv-b{color:#F2C25A;border-color:#F2C25A}.lv-c{color:#F08A8A;border-color:#F08A8A}"
 "#quiz{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 18px;margin-top:8px}"
 ".qn{font-size:13px;color:var(--muted);margin:0 0 6px}.qq{font-size:17px;font-weight:700;line-height:1.7;margin:0 0 14px}"
 ".qc{display:grid;gap:10px}.qb{font:inherit;font-size:15px;text-align:left;line-height:1.6;background:var(--bg);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:12px 14px;cursor:pointer}"
 ".qb:disabled{cursor:default;opacity:.75}.qb.right{opacity:1;border-color:#7FD6A4;color:#7FD6A4;font-weight:700}.qb.wrong{opacity:1;border-color:#F08A8A;color:#F08A8A}"
 ".qr .res{font-weight:800;font-size:16px;margin:16px 0 4px}.qr a{color:var(--link)}"
 ".nx{font:inherit;font-size:15px;font-weight:700;background:var(--accent);color:#1a1020;border:0;border-radius:10px;padding:12px 20px;margin-top:12px;cursor:pointer}.nx.sub{background:none;color:var(--accent);border:1px solid var(--accent)}")
page = {"path": "shigusa", "title": "しぐさ・ボディランゲージ索引", "date": "2026-10-03",
 "desc": "目をそらす、腕を組む、髪を触る。気になったしぐさから研究でわかっていることを引けるボディランゲージ索引と、思い込みを確かめる4択クイズ。出典つきの記事にもとづいています。",
 "body": body, "css": css}
open(ROOT + "media/umbra-pages.json", "w").write(json.dumps([page], ensure_ascii=False, indent=2) + "\n")
print("ok", len(D), len(Q))
