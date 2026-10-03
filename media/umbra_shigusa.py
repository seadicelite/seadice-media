"""しぐさ・ボディランゲージ索引(/shigusa/)を生成し、各記事に索引へのリンクを差し込む。

データは media/umbra-shigusa.json
  items   : 索引の項目 {part, gesture, belief, level(a/b/c), text, slug, id(アンカー), tags(purposesのid), evidence("meta"|"few"|なし)}
  quiz    : 4択 {q, c(正解を先頭に4つ), e, slug}
  purposes: 「知りたいことから」の入口 {id, label, lead}
実行: python3 media/umbra_shigusa.py && python3 media/build.py umbra
出力: media/umbra-pages.json(extras.pages が /shigusa/ を書き出す)、各記事の <!--shigusa--> ブロック
"""
import html
import json
import re
from pathlib import Path

E = html.escape
ROOT = str(Path(__file__).resolve().parent.parent) + "/"
URL = "https://umbra.seadice.win/shigusa/"
data = json.load(open(ROOT + "media/umbra-shigusa.json"))
D, Q, PUR = data["items"], data["quiz"], data.get("purposes", [])
LV = {"a": "手がかりになる", "b": "状況しだい", "c": "当てにならない"}
EV = {"meta": "メタ分析・レビューあり", "few": "このしぐさを直接調べた研究は少ない"}
PART_ORDER = ["目・視線", "表情", "手・触れる", "姿勢・距離", "体の動き", "声・会話", "連絡・行動"]
imgs = json.load(open(ROOT + "media/umbra-images.json"))
posts = {p["slug"]: p for p in json.load(open(ROOT + "media/umbra-posts.json"))}
for x in D + Q:
    assert x["slug"] in posts, x["slug"]
assert len({x["id"] for x in D}) == len(D), "id が重複"
D.sort(key=lambda x: PART_ORDER.index(x["part"]) if x["part"] in PART_ORDER else len(PART_ORDER))
parts = list(dict.fromkeys(x["part"] for x in D))


def nsrc(slug):
    t = open(f"{ROOT}sites/umbra/{slug}/index.html").read()
    i = t.find('class="sources"')
    return t[i:t.find("</ol>", i)].count("<li") if i >= 0 else 0


def th(slug):
    i = imgs.get(slug)
    if not i:
        return "", ""
    u = i["src640"] if "src640" in i else f"{i['raw']}&w=240&h=240&fit=crop&q=70&fm=webp"
    cr = f'<p class="cr">写真：<a href="{E(i.get("page", ""))}" rel="nofollow noopener" target="_blank">{E(i.get("artist", ""))}</a>（{E(i.get("license", ""))}）</p>' if i.get("page") else ""
    return f'<img class="th" src="{E(u)}" alt="" width="96" height="96" loading="lazy" decoding="async">', cr


def item(x):
    img, cr = th(x["slug"])
    ev = f'根拠：出典{nsrc(x["slug"])}件' + (f'・{EV[x["evidence"]]}' if x.get("evidence") in EV else "")
    return (f'<li class="sg{" hasth" if img else ""}" id="{x["id"]}" data-p="{E(x["part"])}" data-t="{" ".join(x.get("tags", []))}" data-k="{E(x["gesture"] + x["belief"] + x["text"])}">{img}<div class="sgx">'
            f'<p class="sg-h"><span class="sg-part">{E(x["part"])}</span><span class="lv lv-{x["level"]}">{LV[x["level"]]}</span></p>'
            f'<h3>{E(x["gesture"])} <a class="pl" href="#{x["id"]}" aria-label="「{E(x["gesture"])}」へのリンク">#</a></h3>'
            f'<p class="sg-b">よく言われる意味：{E(x["belief"])}</p><p>{E(x["text"])}</p><p class="ev">{ev}</p>'
            f'<a href="/{x["slug"]}/">記事を読む：{E(posts[x["slug"]]["title"])}</a>{cr}</div></li>')


items = "".join(item(x) for x in D)
chips = '<button type="button" class="chip on" data-f="" aria-pressed="true">すべて</button>' + "".join(f'<button type="button" class="chip" data-f="{E(p)}" aria-pressed="false">{E(p)}</button>' for p in parts)
pchips = '<button type="button" class="pchip on" data-g="" aria-pressed="true">指定しない</button>' + "".join(f'<button type="button" class="pchip" data-g="{x["id"]}" aria-pressed="false">{E(x["label"])}</button>' for x in PUR)
pleads = "".join(f'<p class="plead" data-g="{x["id"]}" hidden>{E(x["lead"])}</p>' for x in PUR)
qdata = json.dumps([{"q": x["q"], "c": x["c"], "e": x["e"], "u": f'/{x["slug"]}/', "t": posts[x["slug"]]["title"]} for x in Q], ensure_ascii=False).replace("</", "<\\/")
faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": f'「{x["gesture"]}」は「{x["belief"]}」のサインですか？',
     "acceptedAnswer": {"@type": "Answer", "text": f'{LV[x["level"]]}。{x["text"]}', "url": URL + "#" + x["id"]}} for x in D]}
faq_json = json.dumps(faq, ensure_ascii=False).replace("</", "<\\/")
body = f"""<p>気になったしぐさから、研究でわかっていることをすぐに調べられます。4択クイズで、思い込みとのズレを確かめることもできます。どのしぐさも、1つだけで相手の本音は決まりません。</p>
<script type="application/ld+json">{faq_json}</script>
<div id="daily" class="daily" aria-live="polite" hidden></div>
<div class="tabs" role="tablist"><button type="button" role="tab" id="t1" aria-selected="true" aria-controls="p1">しぐさを調べる</button><button type="button" role="tab" id="t2" aria-selected="false" aria-controls="p2">4択クイズ</button></div>
<section id="p1" role="tabpanel" aria-labelledby="t1">
<h2>しぐさを調べる</h2>
<p class="note">読みやすさは3段階です。「手がかりになる」でも、それだけで本音は決まりません。</p>
<ul class="legend"><li><span class="lv lv-a">手がかりになる</span>傾向として研究で確認されている</li><li><span class="lv lv-b">状況しだい</span>理由が複数あり、意味を1つに決められない</li><li><span class="lv lv-c">当てにならない</span>研究で通説が支持されていない</li></ul>
<p class="flabel">知りたいことから</p>
<div class="fchips">{pchips}</div>
{pleads}
<p class="flabel">体の部位から</p>
<div class="fchips">{chips}</div>
<label class="sr" for="q">しぐさを検索</label><input id="q" type="search" placeholder="例：目、腕、触る、声" autocomplete="off">
<p id="cnt" class="note" aria-live="polite"></p>
<ul class="sgl" id="list">{items}</ul>
</section>
<section id="p2" role="tabpanel" aria-labelledby="t2" hidden>
<h2>4択クイズ</h2>
<p class="note">全{len(Q)}問から、毎回10問がランダムに出ます。</p>
<div id="quiz" aria-live="polite"><noscript><p>クイズを遊ぶにはJavaScriptを有効にしてください。</p></noscript></div>
</section>
<h2>このページについて</h2>
<p>内容は、しぐさと本音で公開している記事（それぞれ論文などの出典を確認済み）をもとにしています。「根拠」の欄は、記事が挙げている出典の数と、メタ分析・レビュー（複数の研究をまとめた研究）を含むかどうかを示します。特定の人を診断したり、ラベルを貼ったりするためのものではありません。相手の気持ちは、しぐさより言葉と行動の積み重ねで確かめてください。</p>
<script>
(function(){{
var Q={qdata};
function sh(a){{a=a.slice();for(var k=a.length-1;k>0;k--){{var j=Math.floor(Math.random()*(k+1)),t=a[k];a[k]=a[j];a[j]=t}}return a}}
function esc(s){{var d=document.createElement('div');d.textContent=s;return d.innerHTML}}
function each(sel,fn){{[].forEach.call(document.querySelectorAll(sel),fn)}}
var t1=document.getElementById('t1'),t2=document.getElementById('t2'),p1=document.getElementById('p1'),p2=document.getElementById('p2'),started=false;
function tab(n){{var a=n===1;t1.setAttribute('aria-selected',a);t2.setAttribute('aria-selected',!a);p1.hidden=!a;p2.hidden=a;if(!a&&!started)start();}}
t1.onclick=function(){{tab(1)}};t2.onclick=function(){{tab(2)}};
var q=document.getElementById('q'),cnt=document.getElementById('cnt'),f='',g='',li=[].slice.call(document.querySelectorAll('.sg'));
function filt(){{var s=q.value.trim(),n=0;li.forEach(function(e){{var ok=(!f||e.dataset.p===f)&&(!g||(' '+e.dataset.t+' ').indexOf(' '+g+' ')>=0)&&(!s||e.dataset.k.indexOf(s)>=0||e.textContent.indexOf(s)>=0);e.hidden=!ok;if(ok)n++}});cnt.textContent=n?n+'件':'見つかりませんでした。条件を変えてみてください。'}}
q.oninput=filt;
function grp(sel,key,set){{each(sel,function(b){{b.onclick=function(){{set(b.dataset[key]);each(sel,function(x){{x.classList.toggle('on',x===b);x.setAttribute('aria-pressed',x===b)}});filt()}}}})}}
grp('.chip','f',function(v){{f=v}});
grp('.pchip','g',function(v){{g=v;each('.plead',function(p){{p.hidden=p.dataset.g!==v}})}});
var box=document.getElementById('quiz'),order,i,score;
function start(){{started=true;order=sh(Q).slice(0,10);i=0;score=0;show()}}
function choices(x,root,done){{var ch=sh(x.c);root.innerHTML=ch.map(function(c){{return '<button type="button" class="qb">'+esc(c)+'</button>'}}).join('');
each('#'+root.id+' .qb',function(b){{b.onclick=function(){{var ok=b.textContent===x.c[0];
each('#'+root.id+' .qb',function(e){{e.disabled=true;if(e.textContent===x.c[0]){{e.classList.add('right');e.textContent='正解：'+e.textContent}}else if(e===b){{e.classList.add('wrong');e.textContent='あなたの答え：'+e.textContent}}}});done(ok,b)}}}})}}
function show(){{if(i>=order.length)return end();var x=order[i];
box.innerHTML='<p class="qn">第'+(i+1)+'問 / 全'+order.length+'問</p><p class="qq">'+esc(x.q)+'</p><div class="qc" id="qc"></div><div class="qr"></div>';
choices(x,document.getElementById('qc'),function(ok){{if(ok)score++;
box.querySelector('.qr').innerHTML='<p class="res">'+(ok?'正解です':'不正解です')+'</p><p>'+esc(x.e)+'</p><p><a href="'+x.u+'">記事を読む：'+esc(x.t)+'</a></p><button type="button" class="nx">'+(i+1<order.length?'次の問題へ':'結果を見る')+'</button>';
var n=box.querySelector('.nx');n.onclick=function(){{i++;show()}};n.focus()}})}}
function end(){{var m=score>=8?'研究でわかっていることをよく押さえています。':score>=5?'通説と研究のズレに気づき始めています。':'しぐさの通説は、研究では当てにならないものが多いのです。';
box.innerHTML='<p class="qq">'+order.length+'問中 '+score+'問 正解</p><p>'+m+'</p><button type="button" class="nx" id="again">もう一度挑戦する</button> <button type="button" class="nx sub" id="look">しぐさを調べる</button>';
document.getElementById('again').onclick=start;document.getElementById('look').onclick=function(){{tab(1);t1.focus()}};document.getElementById('again').focus()}}
var dl=document.getElementById('daily'),now=new Date(),key='umbra-daily-'+now.getFullYear()+'-'+(now.getMonth()+1)+'-'+now.getDate();
var day=Math.floor((Date.UTC(now.getFullYear(),now.getMonth(),now.getDate()))/864e5),dx=Q[day%Q.length],prev=null;
try{{prev=localStorage.getItem(key)}}catch(e){{}}
dl.innerHTML='<p class="dh">今日の1問</p><p class="qq">'+esc(dx.q)+'</p><div class="qc" id="dc"></div><div class="dr"></div>';dl.hidden=false;
function dres(ok){{dl.querySelector('.dr').innerHTML='<p class="res">'+(ok?'正解です':'不正解です')+'</p><p>'+esc(dx.e)+'</p><p><a href="'+dx.u+'">記事を読む：'+esc(dx.t)+'</a></p><p class="note">明日は別の問題が出ます。</p>'}}
choices(dx,document.getElementById('dc'),function(ok,b){{try{{localStorage.setItem(key,b.textContent.replace(/^(正解|あなたの答え)：/,''))}}catch(e){{}}dres(ok)}});
if(prev){{each('#dc .qb',function(b){{if(b.textContent===prev)b.click()}})}}
filt();
if(location.hash){{var tg=document.getElementById(location.hash.slice(1));if(tg&&tg.classList.contains('sg'))tg.scrollIntoView()}}
}})();
</script>"""
css = (".tabs{display:flex;gap:8px;margin:20px 0 4px;border-bottom:1px solid var(--border)}"
 ".tabs button{font:inherit;font-size:15px;font-weight:700;background:none;color:var(--muted);border:0;border-bottom:3px solid transparent;padding:12px 14px;cursor:pointer}"
 ".tabs button[aria-selected=true]{color:var(--accent);border-bottom-color:var(--accent)}"
 "button:focus-visible,input:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"
 ".sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}"
 "#q{width:100%;box-sizing:border-box;font:inherit;font-size:16px;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:12px 14px;margin:8px 0 12px}"
 ".fchips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 8px}"
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
 ".nx{font:inherit;font-size:15px;font-weight:700;background:var(--accent);color:#1a1020;border:0;border-radius:10px;padding:12px 20px;margin-top:12px;cursor:pointer}.nx.sub{background:none;color:var(--accent);border:1px solid var(--accent)}"
 ".flabel{font-size:13px!important;color:var(--muted);margin:14px 0 6px!important}"
 ".pchip{font:inherit;font-size:14px;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:10px;padding:8px 14px;cursor:pointer}.pchip.on{border-color:var(--accent2);color:var(--accent2)}"
 ".plead{font-size:14px!important;line-height:1.8!important;background:var(--card);border-left:3px solid var(--accent2);border-radius:6px;padding:10px 14px;margin:4px 0 8px!important}"
 ".sg:target{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}.sg{scroll-margin-top:72px}"
 ".pl{font-size:14px!important;color:var(--muted)!important;text-decoration:none;margin-left:4px}"
 ".sg .ev{font-size:12px!important;color:var(--muted);margin:2px 0 6px!important}"
 ".daily{background:var(--card);border:1px solid var(--accent);border-radius:14px;padding:18px;margin:18px 0 8px}.dh{font-size:13px!important;font-weight:800;color:var(--accent);margin:0 0 6px!important}.dr .res{font-weight:800;font-size:16px;margin:14px 0 4px}.dr a{color:var(--link)}"
)
page = {"path": "shigusa", "title": "しぐさ・ボディランゲージ索引", "date": "2026-10-03",
 "desc": "目をそらす、腕を組む、髪を触る。気になったしぐさから研究でわかっていることを引けるボディランゲージ索引と、思い込みを確かめる4択クイズ。出典つきの記事にもとづいています。",
 "body": body, "css": css}
open(ROOT + "media/umbra-pages.json", "w").write(json.dumps([page], ensure_ascii=False, indent=2) + "\n")

# 各記事に、索引の該当項目へのリンクを差し込む(出典の直前。再実行しても1つだけになるよう置き換える)
BLOCK = re.compile(r"<!--shigusa-->.*?<!--/shigusa-->\n?", re.S)
n = 0
for x in D:
    f = Path(f'{ROOT}sites/umbra/{x["slug"]}/index.html')
    t = BLOCK.sub("", f.read_text())
    blk = (f'<!--shigusa--><p style="margin:28px 0;padding:14px 18px;border:1px solid var(--border);border-radius:12px;background:var(--card);font-size:15px;line-height:1.8">'
           f'<a href="/shigusa/#{x["id"]}" style="color:var(--link);font-weight:700">しぐさ・ボディランゲージ索引で「{E(x["gesture"])}」を見る</a><br>'
           f'<span style="font-size:13px;color:var(--muted)">ほかのしぐさも{len(D)}種類から調べられます。4択クイズもあります。</span></p><!--/shigusa-->\n')
    k = t.find('<div class="sources">')
    if k < 0:
        continue
    t = t[:k] + blk + t[k:]
    f.write_text(t)
    n += 1
print("ok", len(D), "items,", len(Q), "quiz,", n, "articles linked")
