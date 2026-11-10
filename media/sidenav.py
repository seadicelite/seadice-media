"""左の記事一覧（全メディア。設定 "sideIndex": false で止める）。build.py の最後に毎回呼ばれ、冪等に次を入れる。
 - /nav.json: カテゴリごとの記事一覧（新しい順）。一覧を開くときに1回だけ読む（全ページに埋め込むと重くなるため）
 - /sn-{ハッシュ}.css・.js: 一覧の見た目と動き。全ページから同じファイルを読む（firebase.json で長くキャッシュ）
 - サイト内の全 index.html: PCは左端の縦タブ（クリックで開く。ホバーで勝手に開くと読んでいる途中に気が散るため）、スマホは左下のボタン（タップで開く）と、一覧のパネル
 - 読んだ印（readcheck.py と同じキー {slug}-read）と「もう一度読みたい」（{slug}-again）を一覧に出し、すべて・未読・もう一度・読んだで絞り込む。
   カテゴリごとに読んだ本数を細い棒で出す。記録はこの端末のブラウザ（localStorage）だけ。サーバーへは何も送らない。"""
import hashlib, html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape

CSS = (".sn-b{position:fixed;z-index:900;left:12px;bottom:calc(12px + env(safe-area-inset-bottom));display:flex;align-items:center;gap:6px;"
       "min-height:56px;padding:0 16px;font:inherit;font-size:14px;font-weight:700;color:var(--text,#E6EAF2);background:var(--card,var(--panel,#121926));"
       "border:1px solid var(--border,var(--line,#26324A));border-radius:8px;cursor:pointer}"
       "@media(max-width:959px){.sn-b{padding:0 14px}.sn-bl,.sn-b small{display:none}body::after{content:"";display:block;height:76px}}"
       ".sn-b[hidden]{display:none}.sn-b:hover,.sn-b[aria-expanded=true]{border-color:var(--accent,#7FB2FF)}.sn-b small{font-size:12px;font-weight:400;color:var(--muted,#9AA4B5)}"
       ".sn-b svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round}"
       ".sn-p{position:fixed;z-index:1000;left:0;top:0;bottom:0;width:min(360px,88vw);display:flex;flex-direction:column;"
       "background:var(--bg,#0B0F17);border-right:1px solid var(--border,var(--line,#26324A))}.sn-p[hidden]{display:none}"
       ".sn-h{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:14px 16px 10px}"
       ".sn-h b{font-size:16px;color:var(--text,#E6EAF2)}.sn-h b small{margin-left:6px;font-size:12px;font-weight:400;color:var(--muted,#9AA4B5)}.sn-x{font:inherit;font-size:14px;min-height:52px;padding:0 14px;color:var(--text,#E6EAF2);"
       "background:transparent;border:1px solid var(--border,var(--line,#26324A));border-radius:8px;cursor:pointer}"
       ".sn-q{margin:0 16px 10px;font:inherit;font-size:16px;min-height:48px;padding:0 12px;color:var(--text,#E6EAF2);background:var(--card,var(--panel,#121926));"
       "border:1px solid var(--border,var(--line,#26324A));border-radius:8px}.sn-q::placeholder{color:var(--muted,#9AA4B5);opacity:1}.sn-q:focus{outline:2px solid var(--accent,#7FB2FF);outline-offset:1px}"
       ".sn-l{flex:1;overflow-y:auto;overscroll-behavior:contain;padding:0 16px 16px}"
       "/* 記事ページの FAQ（details・summary）の見た目を一覧の中では打ち消す */"
       ".sn-l details{margin:0 0 4px;padding:0;background:none;border:0;border-radius:0!important}"
       ".sn-l summary::before{content:none}.sn-l summary{display:flex;align-items:center;gap:8px;min-height:48px;padding:0;"
       "font-size:15px;font-weight:700;color:var(--text,#E6EAF2);cursor:pointer;list-style:none}.sn-l summary::-webkit-details-marker{display:none}"
       ".sn-l summary i{width:10px;height:10px;border-radius:50%;flex:0 0 10px}.sn-l summary small{margin-left:auto;font-size:12px;font-weight:400;color:var(--muted,#9AA4B5)}"
       ".sn-l summary::after{content:\"+\";font-size:18px;color:var(--muted,#9AA4B5);width:16px;text-align:center}.sn-l details[open] summary::after{content:\"-\"}"
       ".sn-l ul{list-style:none;margin:0 0 10px;padding:0}.sn-l li a{display:block;padding:10px 0 10px 18px;font-size:14px;line-height:1.55;"
       "color:var(--text,#E6EAF2);text-decoration:none}@media(hover:hover){.sn-l li a:hover{color:var(--accent,#7FB2FF)}}"
       ".sn-x:focus-visible,.sn-l summary:focus-visible,.sn-l li a:focus-visible,.sn-f a:focus-visible{outline:2px solid var(--accent,#7FB2FF);outline-offset:2px}"
       ".sn-l li a[aria-current]{color:var(--accent,#7FB2FF);font-weight:700}.sn-l li a[aria-current]::before{content:\"いま読んでいる記事\";display:block;font-size:12px;font-weight:400;color:var(--muted,#9AA4B5)}"
       ".sn-f small{display:block;margin-top:6px;font-size:12px;line-height:1.6;color:var(--muted,#9AA4B5)}.sn-m{font-size:14px;color:var(--muted,#9AA4B5);padding:12px 0}.sn-f{margin:0;padding:12px 16px calc(12px + env(safe-area-inset-bottom));"
       "border-top:1px solid var(--border,var(--line,#26324A));font-size:14px}.sn-f a{color:var(--accent,#7FB2FF)}"
       ".sn-o{position:fixed;inset:0;z-index:950;background:rgba(0,0,0,.55)}.sn-o[hidden]{display:none}"
       "@media(min-width:960px){.sn-b{left:0;bottom:auto;top:50%;transform:translateY(-50%);flex-direction:column;min-height:0;"
       "padding:16px 10px;border-left:0;border-radius:0 8px 8px 0;writing-mode:vertical-rl;letter-spacing:.2em}"
       ".sn-b small,.sn-b svg{display:none}}"
       ".sn-t{display:flex;gap:6px;margin:0 16px 10px}.sn-t button{flex:1 1 0;min-width:0;white-space:nowrap;font:inherit;font-size:13px;min-height:52px;padding:0 4px;"
       "color:var(--text,#E6EAF2);background:transparent;border:1px solid var(--border,var(--line,#26324A));border-radius:8px;cursor:pointer}"
       ".sn-t button small{margin-left:3px;font-size:12px;color:var(--muted,#9AA4B5)}.sn-t button[aria-pressed=true]{background:var(--accent,#7FB2FF);border-color:var(--accent,#7FB2FF);color:var(--bg,#0B0F17)}"
       ".sn-t button[aria-pressed=true] small{color:inherit}.sn-l summary{flex-wrap:wrap;padding:10px 0 8px;min-height:0}.sn-l summary::after{order:1}"
       ".sn-l summary .sn-g{order:2;flex:0 0 100%;height:3px;margin-top:6px;background:var(--border,var(--line,#26324A));border-radius:2px;overflow:hidden}.sn-g span{display:block;height:100%}"
       ".sn-l li{display:flex;align-items:center}.sn-l li[hidden],.sn-l details[hidden]{display:none}.sn-l li a{flex:1;min-width:0;padding-left:0}"
       ".sn-s{display:inline-block;width:12px;height:12px;margin:0 8px 0 2px;border:1.5px solid var(--muted,#9AA4B5);border-radius:50%;vertical-align:-1px;box-sizing:border-box}"
       ".sn-l li[data-r] .sn-s{background:var(--accent,#7FB2FF);border-color:var(--accent,#7FB2FF)}.sn-l li[data-r] a{color:var(--muted,#9AA4B5)}"
       ".sn-v{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}"
       ".sn-a{flex:0 0 52px;height:52px;display:flex;align-items:center;justify-content:center;background:transparent;border:0;border-radius:8px;cursor:pointer;color:var(--muted,#9AA4B5)}"
       ".sn-a svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linejoin:round}.sn-a[aria-pressed=true]{color:var(--accent,#7FB2FF)}.sn-a[aria-pressed=true] svg{fill:currentColor}"
       ".sn-a:focus-visible,.sn-t button:focus-visible{outline:2px solid var(--accent,#7FB2FF);outline-offset:2px}"
       "@media print{.sn-b,.sn-p,.sn-o{display:none!important}}")

# 開く: スマホはタップ、PC（ホバーできる・幅960px以上）はホバーでも開く。クリックで開いたら、離れても閉じない
JS = ("var K=document.getElementById('sn-p').getAttribute('data-k'),b=document.getElementById('sn-b'),p=document.getElementById('sn-p'),o=document.getElementById('sn-o'),"
      "l=document.getElementById('sn-l'),q=document.getElementById('sn-q'),tb=document.getElementById('sn-tb'),D=null,ld=0,pin=0,t=0,R={},A={},F='all',"
      "hv=matchMedia('(hover:hover) and (min-width:960px)');b.hidden=false;"
      "function get(k){try{return JSON.parse(localStorage.getItem(k)||'{}')||{}}catch(e){return{}}}"
      "function esc(s){return s.replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
      "var BM='<svg viewBox=\"0 0 24 24\" aria-hidden=\"true\"><path d=\"M6 3h12v18l-6-4.5L6 21z\"/></svg>';"
      # 読んだ・もう一度は開くたびに読み直す（記事の下のボタンで変わるため）
      "function draw(){R=get(K+'-read');A=get(K+'-again');var h=location.pathname,s='';D.forEach(function(g){var cur=0,r=0,li=g[2].map(function(a){var k=a[0],u='/'+k+'/',c=u==h;if(c)cur=1;if(R[k])r++;"
      "return '<li data-k=\"'+esc((a[1]+' '+(a[2]||'')).toLowerCase())+'\" data-s=\"'+k+'\"'+(R[k]?' data-r':'')+(A[k]?' data-a':'')+'><a href=\"'+u+'\"'+(c?' aria-current=\"page\"':'')+'><i class=\"sn-s\" aria-hidden=\"true\"></i>'+(R[k]?'<span class=\"sn-v\">読んだ </span>':'')+esc(a[1])+'</a>'"
      "+'<button type=\"button\" class=\"sn-a\" aria-pressed=\"'+!!A[k]+'\" aria-label=\"もう一度読みたい: '+esc(a[1])+'\">'+BM+'</button></li>'}).join('');"
      "s+='<details data-n=\"'+esc(g[0].toLowerCase())+'\"'+(cur?' open data-c':'')+'><summary><i style=\"background:'+g[1]+'\"></i>'+esc(g[0])+'<small>'+r+' / '+g[2].length+'</small><span class=\"sn-g\"><span style=\"width:'+Math.round(r*100/g[2].length)+'%;background:'+g[1]+'\"></span></span></summary><ul>'+li+'</ul></details>'});"
      "l.innerHTML=s;cnt();flt();here()}"
      "function cnt(){var n=0,r=0,a=0;D.forEach(function(g){g[2].forEach(function(x){n++;if(R[x[0]])r++;if(A[x[0]])a++})});"
      "var c={all:n,un:n-r,again:a,read:r};[].forEach.call(tb.children,function(e){var f=e.getAttribute('data-f');e.lastChild.textContent=c[f];e.setAttribute('aria-pressed',f==F)});"
      "document.getElementById('sn-c').textContent=n+'本';document.getElementById('sn-tt').textContent='（'+r+' / '+n+'本 読んだ）'}"
      "function okF(i){return F=='all'||(F=='read'?i.hasAttribute('data-r'):F=='again'?i.hasAttribute('data-a'):!i.hasAttribute('data-r'))}"
      # 今読んでいる記事を一覧の中ほどに送る（scrollIntoView はページ本体まで動かすので使わない）
      "function here(){var a=l.querySelector('[aria-current]');if(a&&!p.hidden&&a.offsetParent)l.scrollTop=a.offsetTop-l.offsetTop-l.clientHeight/2}"
      "function load(){if(ld)return;ld=1;fetch('/nav.json').then(function(r){return r.json()}).then(function(j){D=j;draw()})"
      ".catch(function(){ld=0;l.innerHTML='<p class=\"sn-m\">一覧を読み込めませんでした。通信を確かめて、もう一度開いてください。</p>'})}"
      "function open(f){clearTimeout(t);load();p.hidden=false;b.setAttribute('aria-expanded','true');if(!hv.matches){o.hidden=false;document.documentElement.style.overflow='hidden'}if(D)draw();if(f&&hv.matches)q.focus({preventScroll:true})}"
      "function close(){clearTimeout(t);pin=0;p.hidden=true;o.hidden=true;b.setAttribute('aria-expanded','false');document.documentElement.style.overflow=''}"
      "b.onclick=function(){if(!p.hidden&&pin){close();b.focus()}else{pin=1;open(1)}};"
      ""
      "[b,p].forEach(function(e){e.addEventListener('mouseleave',function(){if(!hv.matches||pin)return;clearTimeout(t);t=setTimeout(close,300)});"
      "e.addEventListener('mouseenter',function(){if(e==p)clearTimeout(t)})});"
      "b.addEventListener('touchstart',load,{passive:true});"
      "o.onclick=close;document.addEventListener('click',function(e){if(!p.hidden&&!p.contains(e.target)&&!b.contains(e.target))close()});document.getElementById('sn-x').onclick=function(){close();b.focus()};"
      "document.addEventListener('keydown',function(e){if(e.key=='Escape'&&!p.hidden){close();b.focus()}});"
      # 押すと印を付け外しする。押した行は、絞り込み中でもすぐには消さない（押し間違いを戻せるように）
      "l.addEventListener('click',function(e){var x=e.target.closest('.sn-a');if(!x)return;var i=x.parentNode,k=i.getAttribute('data-s');A=get(K+'-again');if(A[k]){delete A[k];i.removeAttribute('data-a')}else{A[k]=new Date().toISOString().slice(0,10);i.setAttribute('data-a','')}"
      "x.setAttribute('aria-pressed',!!A[k]);try{localStorage.setItem(K+'-again',JSON.stringify(A))}catch(e){l.insertAdjacentHTML('afterbegin','<p class=\"sn-m\">このブラウザでは保存できません（プライベートブラウズなど）。ページを開き直すと印は消えます。</p>')}cnt()});"
      "tb.addEventListener('click',function(e){var x=e.target.closest('button');if(!x)return;F=x.getAttribute('data-f');if(D){cnt();flt()}});"
      "function hits(v){return [].filter.call(l.querySelectorAll('li'),function(i){return okF(i)&&i.getAttribute('data-k').indexOf(v)>=0}).length}"
      # 0件なら語尾を1字ずつ削って探し直す（「既読スルー」→「既読」）。カテゴリ名に当たればそのまま
      "function flt(){if(!D)return;var w=q.value.trim().toLowerCase(),v=w,n=0;while(v.length>2&&!hits(v)&&![].some.call(l.querySelectorAll('details'),function(d){return d.getAttribute('data-n').indexOf(v)>=0}))v=v.slice(0,-1);[].forEach.call(l.querySelectorAll('details'),function(d){var k=0,g=v&&d.getAttribute('data-n').indexOf(v)>=0;"
      "[].forEach.call(d.querySelectorAll('li'),function(i){var m=okF(i)&&(!v||g||i.getAttribute('data-k').indexOf(v)>=0);i.hidden=!m;if(m)k++});"
      "d.hidden=!k;n+=k;d.open=(v||F!='all')?!!k:d.hasAttribute('data-c')});[].forEach.call(l.querySelectorAll('.sn-m'),function(m){m.remove()});"
      "if(!n)l.insertAdjacentHTML('beforeend','<p class=\"sn-m\">'+(w?'「'+esc(q.value)+'」を含む記事は見つかりませんでした。短い言葉で探してみてください。':F=='again'?'「もう一度読みたい」記事はまだありません。一覧の右の印か、記事の下のボタンで付けられます。':F=='read'?'読んだ記事はまだありません。記事の下の「読んだ記事にする」を押すと、ここに入ります。':'すべて読みました。')+'</p>');"
      "else if(v!=w)l.insertAdjacentHTML('afterbegin','<p class=\"sn-m\">「'+esc(q.value)+'」を含む記事はないので、「'+esc(v)+'」で探しました。</p>')}q.oninput=flt")


def _block(has_map, key, hint, css, js):
    tabs = "".join(f'<button type="button" data-f="{f}" aria-pressed="false">{t}<small></small></button>' for f, t in (("all", "すべて"), ("un", "未読"), ("again", "もう一度"), ("read", "読んだ")))
    ph = f"記事を探す（例: {E(hint)}）" if hint else "記事を探す"
    # 下の欄はマインドマップがあるメディアだけ（スマホで記事名の場所を狭めないため。保存の説明は免責事項と記事末尾にある）
    foot = '<p class="sn-f"><a href="/map/">問いからたどる（マインドマップ）</a></p>' if has_map else ''
    return (f'<!--sidenav--><link rel="stylesheet" href="/{css}">'
            f'<button type="button" class="sn-b" id="sn-b" aria-expanded="false" aria-controls="sn-p" aria-label="記事一覧" hidden>'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg><span class="sn-bl">記事</span>一覧<small id="sn-c"></small></button>'
            f'<div class="sn-o" id="sn-o" hidden></div>'
            f'<div class="sn-p" id="sn-p" data-k="{key}" role="navigation" aria-label="記事一覧" hidden><div class="sn-h"><b>記事一覧<small id="sn-tt"></small></b>'
            f'<button type="button" class="sn-x" id="sn-x">閉じる</button></div>'
            f'<input type="search" class="sn-q" id="sn-q" placeholder="{ph}" aria-label="記事を探す">'
            f'<div class="sn-t" id="sn-tb" role="group" aria-label="しぼりこみ">{tabs}</div>'
            f'<div class="sn-l" id="sn-l"><p class="sn-m">読み込み中です。</p></div>{foot}</div>'
            f'<script src="/{js}" defer></script><!--/sidenav-->')


def _asset(base, ext, body):
    """CSS と JS は全ページに埋め込まず、中身のハッシュを名前に入れた1ファイルにする（長くキャッシュでき、直しても全ページは書き換わらない）。"""
    name = f"sn-{hashlib.sha1(body.encode()).hexdigest()[:10]}.{ext}"
    for old in base.glob(f"sn-*.{ext}"):
        if old.name != name:
            old.unlink()
    f = base / name
    if not f.exists():
        f.write_text(body)
    return name


def apply(cfg, posts, cats):
    if not cfg.get("sideIndex", True):  # 新しいメディアにも最初から入れる。止めるときだけ設定に false
        return 0
    base = ROOT / cfg["path"]
    groups = []
    for name, c in cats.items():
        ps = sorted((p for p in posts if p.get("category") == name), key=lambda p: (p["date"], p["slug"]), reverse=True)
        if ps:
            groups.append([name, c["color"], [[p["slug"], p["title"], p.get("summary", "")] for p in ps]])
    data = json.dumps(groups, ensure_ascii=False, separators=(",", ":"))
    nf = base / "nav.json"
    if not nf.exists() or nf.read_text() != data:
        nf.write_text(data)
    css, js = _asset(base, "css", CSS), _asset(base, "js", f"(function(){{{JS}}})()")
    blk, n = _block((base / "map" / "index.html").exists(), cfg["slug"], cfg.get("sideHint", ""), css, js), 0
    for f in base.rglob("index.html"):
        s = f.read_text()
        if "</body>" not in s or "flutter_bootstrap.js" in s or "flutter.js" in s:  # Flutter の書き出しなど記事サイト以外には入れない
            continue
        t = re.sub(r"<!--sidenav-->.*?<!--/sidenav-->\n?", "", s, flags=re.S)
        m = re.search(r"<body[^>]*>", t)
        t = t[:m.end()] + blk + t[m.end():] if m else t.replace("</body>", blk + "\n</body>", 1)
        if t != s:
            f.write_text(t)
        n += 1
    return n
