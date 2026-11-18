"""記事マップ(マインドマップ)ページ → /map/。media/{slug}-map.json があるメディアだけ。extras.apply から呼ばれる。

中心(メディア名) → 分野(カテゴリ) → 問い(枝) → 記事(葉)。分野はタップで開閉する <details>、中身は入れ子の <ul> なので、
JSなしで動き、AIや検索エンジンにはそのまま構造化された目次として読める。

map.json の形:
  {"title", "seo_title", "desc", "lead", "date",
   "branches": {カテゴリ名: [{"label": 問い, "slugs": [記事slug...], "tools": [{"label", "path"}]}]}}
新しい記事を書いたら、合う枝の slugs に足す。足し忘れた記事は、そのカテゴリの「新しい記事」の枝に自動で入る(ビルド時に警告を出す)。
"""
import html
import json
import re

E = html.escape

CSS = (".mm-lead{font-size:15px;line-height:1.85;max-width:680px;margin:0 0 8px}"
       ".mm-stat{font-size:13px;color:var(--muted);margin:0 0 28px}"
       ".mm{margin:0 0 40px}"
       ".mm-root{position:relative;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;"
       "min-height:96px;margin:0 0 20px;padding:16px;border-radius:24px;background:radial-gradient(circle at 30% 20%,rgba(242,166,90,.28),transparent 60%),var(--card);"
       "border:1px solid var(--accent)}"
       ".mm-root b{font-size:20px;letter-spacing:.06em}.mm-root span{font-size:13px;color:var(--muted);margin-top:4px}"
       ".mm-cats{list-style:none;margin:0;padding:0 0 0 18px;border-left:2px solid var(--border)}"
       ".mm-cat{position:relative;z-index:1;margin:0 0 14px;background:var(--card);border:1px solid var(--border);border-top:3px solid var(--c);border-radius:16px}"
       ".mm-cat::before{content:\"\";position:absolute;left:-21px;top:26px;width:19px;border-top:2px solid var(--border)}"
       ".mm-cat summary{list-style:none;cursor:pointer;display:flex;align-items:center;gap:10px;padding:14px 16px;min-height:52px;font-size:16px;font-weight:800;border-radius:14px}"
       ".mm-cat summary::-webkit-details-marker{display:none}"
       ".mm-cat summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}"
       ".mm-cat summary::after{content:\"\";margin-left:auto;flex:none;width:9px;height:9px;border-right:2px solid var(--muted);border-bottom:2px solid var(--muted);transform:rotate(45deg) translate(-2px,-2px);transition:transform .2s}"
       ".mm-cat details[open] summary::after{transform:rotate(-135deg) translate(-2px,-2px)}"
       ".mm-n{flex:none;font-size:12px;font-weight:700;color:var(--c);border:1px solid var(--c);border-radius:999px;padding:1px 9px}"
       ".mm-d{display:block;font-size:12.5px;font-weight:400;color:var(--muted);margin-top:2px;line-height:1.5}"
       ".mm-br{list-style:none;margin:0 16px 14px 22px;padding:0 0 0 16px;border-left:2px solid var(--border)}"
       ".mm-bl{position:relative;font-size:14px;font-weight:800;color:var(--c);margin:14px 0 4px}"
       ".mm-bl::before{content:\"\";position:absolute;left:-18px;top:.75em;width:14px;border-top:2px solid var(--border)}"
       ".mm-bl small{font-weight:400;color:var(--muted);margin-left:6px}"
       ".mm-lv{list-style:none;margin:0;padding:0}"
       ".mm-lv a{display:block;padding:8px 10px;border-radius:10px;font-size:14px;line-height:1.6;color:var(--text);text-decoration:none}"
       ".mm-lv a:hover,.mm-lv a:focus-visible{background:rgba(255,255,255,.06);color:var(--link)}"
       ".mm-tool{display:inline-block;font-size:11px;font-weight:700;color:var(--bg);background:var(--c);border-radius:6px;padding:1px 6px;margin-right:6px;vertical-align:1px}"
       "@media(min-width:900px){"
       ".mm-root{width:240px;min-height:120px;margin:0 auto 28px}"
       ".mm-root::after{content:\"\";position:absolute;top:100%;left:50%;height:28px;border-left:2px solid var(--border)}"
       ".mm-cols{position:relative;display:grid;grid-template-columns:repeat(3,1fr);gap:28px;padding-top:28px;align-items:start}"
       ".mm-cols::before{content:\"\";position:absolute;top:0;left:calc((100% - 56px)/6);right:calc((100% - 56px)/6);border-top:2px solid var(--border)}"
       ".mm-col{position:relative}"
       ".mm-col::before{content:\"\";position:absolute;top:-28px;bottom:40px;left:50%;border-left:2px solid var(--border)}"
       ".mm-cats{padding:0;border:0}.mm-cat::before{display:none}"
       "}")

# 図のマインドマップ(JSで描く)。中身は下の入れ子リストと同じデータ。JSが動かない環境では図が出ず、リストだけになる。
VCSS = (".mv-wrap{width:min(1240px,100vw - 32px);margin:0 0 12px calc(50% - min(620px,50vw - 16px))}"
        ".mv{position:relative;height:74vh;min-height:440px;max-height:860px;overflow:auto;overscroll-behavior:contain;"
        "border:1px solid var(--border);border-radius:22px;background:radial-gradient(ellipse 60% 50% at 50% 50%,rgba(255,255,255,.045),transparent 70%),var(--bg);cursor:grab}"
        ".mv.drag{cursor:grabbing;user-select:none}"
        ".mv-bar{position:sticky;top:10px;left:10px;z-index:3;display:flex;gap:6px;width:max-content;height:0}"
        ".mv-bar button{width:40px;height:40px;border-radius:12px;border:1px solid var(--border);background:var(--card);color:var(--text);font:inherit;font-size:18px;cursor:pointer}"
        ".mv-bar button:focus-visible,.mv-n:focus-visible{outline:2px solid var(--text);outline-offset:2px}"
        ".mv-sizer{position:relative}.mv-stage{position:absolute;left:0;top:0;transform-origin:0 0}"
        ".mv-stage svg{position:absolute;left:0;top:0;overflow:visible;pointer-events:none}"
        ".mv-stage path{fill:none;stroke:var(--c);stroke-linecap:round;opacity:.75}"
        ".mv-n{position:absolute;box-sizing:border-box;margin:0;font:inherit;text-align:left;cursor:pointer}"
        ".mv-n[hidden]{display:none}"
        ".mv-l0{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:20px 14px;border:0;border-radius:999px;"
        "background:linear-gradient(135deg,var(--accent),var(--accent2));color:#140e1c;font-size:18px;font-weight:900;box-shadow:0 0 48px rgba(255,255,255,.12)}"
        ".mv-l0 small{display:block;font-size:12px;font-weight:700;opacity:.75;margin-top:2px}"
        ".mv-l1{padding:12px 14px;border:0;border-radius:16px;background:var(--c);color:#140e1c;font-size:15px;font-weight:800;line-height:1.45}"
        ".mv-l2{padding:8px 32px 8px 12px;border:2px solid var(--c);border-radius:12px;background:var(--card);color:var(--text);font-size:13.5px;font-weight:700;line-height:1.5}"
        ".mv-l2::after{content:\"＋\";position:absolute;right:10px;top:50%;transform:translateY(-50%);color:var(--c)}.mv-l2[aria-expanded=true]::after{content:\"－\"}"
        ".mv-l3{display:block;padding:5px 2px 5px 0;border-bottom:2px solid var(--c);color:var(--text);text-decoration:none;font-size:13px;line-height:1.55}"
        ".mv-l3:hover{color:var(--link)}"
        ".mv-n small{font-size:11px;font-weight:700;opacity:.7;margin-left:6px}"
        ".mv-hint{font-size:13px;color:var(--muted);margin:0 0 36px}"
        ".mm-h2{font-size:19px;margin:8px 0 6px}")

JS = r"""<script>(function(){var D=%s;
var W=document.getElementById('mv');if(!W)return;W.hidden=false;document.getElementById('mv-hint').hidden=false;
var Z1=document.getElementById('mv-sizer'),S=document.getElementById('mv-stage'),G=S.querySelector('svg'),NS='http://www.w3.org/2000/svg';
var sm=innerWidth<640,LW=sm?[128,124,140,200]:[170,160,180,250],GX=sm?[34,30,26]:[64,52,40],GY=[26,14,4],Z=sm?.85:1,first=true;
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function mk(lv,col,html,href){var e=document.createElement(href?'a':(lv?'button':'div'));e.className='mv-n mv-l'+lv;if(href)e.href=href;else if(lv)e.type='button';
e.style.setProperty('--c',col);e.style.width=LW[lv]+'px';e.innerHTML=html;S.appendChild(e);return e}
var root={el:mk(0,'',  '<b>'+esc(D.name)+'</b><small>'+D.total+'本の記事</small>'),kids:[],open:true,lv:0},half=Math.ceil(D.c.length/2);
D.c.forEach(function(c,i){var n={el:mk(1,c.col,esc(c.n)+'<small>'+c.k+'</small>'),kids:[],open:true,lv:1,col:c.col,sd:i<half?1:-1};root.kids.push(n);
c.q.forEach(function(q){var m={el:mk(2,c.col,esc(q.n)+'<small>'+q.k+'</small>'),kids:[],open:false,lv:2,col:c.col,sd:n.sd};n.kids.push(m);
q.a.forEach(function(a){m.kids.push({el:mk(3,c.col,(a[2]?'<span class="mm-tool">ツール</span>':'')+esc(a[0]),a[1]),kids:[],lv:3,col:c.col,sd:n.sd})})})});
function each(n,f){f(n);n.kids.forEach(function(k){each(k,f)})}
each(root,function(n){if(n.lv==1||n.lv==2){n.el.setAttribute('aria-expanded',n.open);n.el.onclick=function(){if(moved)return;n.open=!n.open;n.el.setAttribute('aria-expanded',n.open);lay()}}});
function vis(n,v){n.el.hidden=!v;n.v=v;n.kids.forEach(function(k){vis(k,v&&n.open)})}
function ht(n){n.h=n.el.offsetHeight;var s=0,ks=n.open?n.kids:[];ks.forEach(function(k){s+=ht(k)});if(ks.length)s+=(ks.length-1)*GY[n.lv];n.ks=s;n.sh=Math.max(n.h,s);return n.sh}
var XR=[0,LW[0]/2+GX[0]];XR[2]=XR[1]+LW[1]+GX[1];XR[3]=XR[2]+LW[2]+GX[2];
function put(n,top){n.cy=top+n.sh/2;n.x=n.sd>0?XR[n.lv]:-XR[n.lv]-LW[n.lv];var y=n.cy-n.ks/2;if(n.open)n.kids.forEach(function(k){put(k,y);y+=k.sh+GY[n.lv]})}
function lay(){vis(root,true);var L=[],R=[];root.kids.forEach(function(k){(k.sd>0?R:L).push(k)});root.h=root.el.offsetHeight;
[L,R].forEach(function(side){var t=0;side.forEach(function(k){ht(k)});side.forEach(function(k){t+=k.sh});t+=(side.length-1)*GY[0];var y=-t/2;side.forEach(function(k){put(k,y);y+=k.sh+GY[0]})});
root.x=-LW[0]/2;root.cy=0;var a=1e9,b=-1e9,c=1e9,d=-1e9;each(root,function(n){if(!n.v)return;a=Math.min(a,n.x);b=Math.max(b,n.x+LW[n.lv]);c=Math.min(c,n.cy-n.el.offsetHeight/2);d=Math.max(d,n.cy+n.el.offsetHeight/2)});
var P=40,ox=P-a,oy=P-c,w=b-a+2*P,h=d-c+2*P;G.setAttribute('width',w);G.setAttribute('height',h);G.innerHTML='';
each(root,function(n){if(!n.v)return;n.el.style.left=(n.x+ox)+'px';n.el.style.top=(n.cy+oy-n.el.offsetHeight/2)+'px';
if(n.lv&&n.p){var p=n.p,x1=(n.sd>0?p.x+LW[p.lv]:p.x)+ox,y1=p.cy+oy,x2=(n.sd>0?n.x:n.x+LW[n.lv])+ox,y2=n.cy+oy,dx=(x2-x1)/2;
if(n.lv==3)y2=n.cy+oy+n.el.offsetHeight/2;if(p.lv==0)x1=p.x+LW[0]/2+ox;
var e=document.createElementNS(NS,'path');e.setAttribute('d','M'+x1+' '+y1+'C'+(x1+dx)+' '+y1+' '+(x2-dx)+' '+y2+' '+x2+' '+y2);e.style.setProperty('--c',n.col);e.setAttribute('stroke-width',[0,6,3.5,2][n.lv]);G.appendChild(e)}});
S.style.width=w+'px';S.style.height=h+'px';if(first)Z=Math.max(sm?.7:.72,Math.min(1,W.clientWidth/w,W.clientHeight/h));zoom(Z);if(first){first=false;W.scrollLeft=(ox*Z)-W.clientWidth/2;W.scrollTop=(oy*Z)-W.clientHeight/2}}
each(root,function(n){n.kids.forEach(function(k){k.p=n})});
function zoom(z){Z=Math.max(.3,Math.min(1.6,z));S.style.transform='scale('+Z+')';Z1.style.width=parseFloat(S.style.width)*Z+'px';Z1.style.height=parseFloat(S.style.height)*Z+'px'}
function zc(z){var cx=(W.scrollLeft+W.clientWidth/2)/Z,cy=(W.scrollTop+W.clientHeight/2)/Z;zoom(z);W.scrollLeft=cx*Z-W.clientWidth/2;W.scrollTop=cy*Z-W.clientHeight/2}
document.getElementById('mv-in').onclick=function(){zc(Z*1.2)};document.getElementById('mv-out').onclick=function(){zc(Z/1.2)};
document.getElementById('mv-fit').onclick=function(){var w=parseFloat(S.style.width),h=parseFloat(S.style.height);zoom(Math.min(W.clientWidth/w,W.clientHeight/h));W.scrollLeft=(w*Z-W.clientWidth)/2;W.scrollTop=(h*Z-W.clientHeight)/2};
var moved=false,dn=null;W.addEventListener('pointerdown',function(e){if(e.pointerType!='mouse'||e.button)return;dn={x:e.clientX,y:e.clientY,l:W.scrollLeft,t:W.scrollTop};moved=false});
addEventListener('pointermove',function(e){if(!dn)return;var dx=e.clientX-dn.x,dy=e.clientY-dn.y;if(!moved&&Math.abs(dx)+Math.abs(dy)<6)return;moved=true;W.classList.add('drag');W.scrollLeft=dn.l-dx;W.scrollTop=dn.t-dy});
addEventListener('pointerup',function(){dn=null;W.classList.remove('drag');setTimeout(function(){moved=false},0)});
W.addEventListener('click',function(e){if(moved){e.preventDefault();e.stopPropagation()}},true);
lay()})();</script>"""


def _short(title):
    """記事タイトルの前半(問いの部分)を葉の文言にする。短すぎるときは全文。"""
    m = re.match(r"(.+?[。？?])", title)
    s = m.group(1).rstrip("。") if m else title
    return s if len(s) >= 8 else title


def build(cfg, posts, cats, page):
    """cats は build.cats_of の {カテゴリ名: 情報}。page は extras._page を部分適用した関数 (rel, title, desc, body, graph, trail, extra_css) -> url。"""
    from extras import _load
    m = _load(cfg["slug"], "map")
    if not m:
        return []
    by = {p["slug"]: p for p in posts}
    tree, used = [], set()
    for name, info in cats.items():
        c = dict(info, name=name)
        brs = []
        for b in m["branches"].get(c["name"], []):
            ss = [s for s in b["slugs"] if s in by]
            used.update(ss)
            if ss or b.get("tools"):
                brs.append((b["label"], ss, b.get("tools", [])))
        rest = [p["slug"] for p in posts if p["category"] == c["name"] and p["slug"] not in used]
        if rest:
            print(f"  map: 枝に入っていない記事 {len(rest)}本 ({c['name']}): {', '.join(rest)}")
            brs.append(("新しい記事", rest, []))
            used.update(rest)
        if brs:
            tree.append((c, brs))
    total = sum(len(ss) for _, brs in tree for _, ss, _ in brs)

    def cat_html(c, brs):
        n = sum(len(ss) for _, ss, _ in brs)
        lis = ""
        for label, ss, tools in brs:
            leaves = "".join(f'<li><a href="{E(t["path"])}"><span class="mm-tool">ツール</span>{E(t["label"])}</a></li>' for t in tools)
            leaves += "".join(f'<li><a href="/{s}/">{E(_short(by[s]["title"]))}</a></li>' for s in ss)
            lis += f'<li><p class="mm-bl">{E(label)}<small>{len(ss)}本</small></p><ul class="mm-lv">{leaves}</ul></li>'
        return (f'<li class="mm-cat" style="--c:{c.get("color", "var(--accent)")}"><details><summary>'
                f'<span>{E(c["name"])}<span class="mm-d">{E(c.get("desc", ""))}</span></span><span class="mm-n">{n}本</span></summary>'
                f'<ul class="mm-br">{lis}</ul></details></li>')

    k = -(-len(tree) // 3)  # PCでは3列。上から順に列を埋める
    cols = "".join(f'<div class="mm-col"><ul class="mm-cats">{"".join(cat_html(c, b) for c, b in tree[i * k:(i + 1) * k])}</ul></div>'
                   for i in range(3) if tree[i * k:(i + 1) * k])
    data = {"name": cfg["name"], "total": total, "c": [
        {"n": c["name"], "col": c.get("color", "#999"), "k": sum(len(ss) for _, ss, _ in brs), "q": [
            {"n": label, "k": len(ss), "a": [[t["label"], t["path"], 1] for t in tools] + [[_short(by[s]["title"]), f"/{s}/", 0] for s in ss]}
            for label, ss, tools in brs]} for c, brs in tree]}
    viewer = ('<div class="mv-wrap"><div class="mv" id="mv" hidden role="region" aria-label="マインドマップ（ドラッグやスクロールで移動）">'
              '<div class="mv-bar"><button type="button" id="mv-out" aria-label="縮小">－</button><button type="button" id="mv-in" aria-label="拡大">＋</button>'
              '<button type="button" id="mv-fit" aria-label="全体を表示" style="width:auto;padding:0 12px;font-size:13px">全体</button></div>'
              '<div class="mv-sizer" id="mv-sizer"><div class="mv-stage" id="mv-stage"><svg aria-hidden="true"></svg></div></div></div></div>'
              '<p class="mv-hint" id="mv-hint" hidden>問いをタップすると記事の枝が開きます。ドラッグやスクロールで動かせます。</p>')
    body = (f'  <div class="hero"><h1>{E(cfg["name"])} {E(m["title"])}</h1></div>\n'
            f'  <p class="mm-lead">{E(m["lead"])}</p>\n'
            f'  <p class="mm-stat">{len(tree)}分野・{sum(len(b) for _, b in tree)}の問い・{total}本の記事（記事が増えると自動で更新されます）</p>\n'
            f'  {viewer}\n'
            f'  <h2 class="mm-h2">一覧で見る</h2>\n'
            f'  <div class="mm"><div class="mm-root"><b>{E(cfg["name"])}</b><span>{total}本の記事</span></div>'
            f'<div class="mm-cols">{cols}</div></div>\n'
            + JS % json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    rel = "map/"
    url = cfg["url"] + rel
    order = [s for _, brs in tree for _, ss, _ in brs for s in ss]
    pub = {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}
    graph = [{"@type": "CollectionPage", "name": f'{cfg["name"]} {m["title"]}', "url": url, "description": m["desc"],
              "dateModified": max([m.get("date", "")] + [p["date"] for p in posts]), "publisher": pub,
              "mainEntity": {"@type": "ItemList", "numberOfItems": len(order), "itemListElement": [
                  {"@type": "ListItem", "position": i + 1, "name": by[s]["title"], "url": cfg["url"] + s + "/"} for i, s in enumerate(order)]}}]
    return [page(rel, f'{m.get("seo_title") or m["title"]} | {cfg["name"]}', m["desc"], body, graph, [(m["title"], url)], CSS + VCSS)]


def branches_for_llms(cfg, posts):
    """llms.txt の記事一覧を「カテゴリ > 問い」に分けるための {カテゴリ名: [(問い, [slug])]}。map が無ければ None。"""
    from extras import _load
    m = _load(cfg["slug"], "map")
    if not m:
        return None
    have = {p["slug"] for p in posts}
    return {c: [(b["label"], [s for s in b["slugs"] if s in have]) for b in bs] for c, bs in m["branches"].items()}
