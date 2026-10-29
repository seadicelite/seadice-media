"""左の記事一覧（設定 "sideIndex": true のメディアだけ）。build.py の最後に毎回呼ばれ、冪等に次を入れる。
 - /nav.json: カテゴリごとの記事一覧（新しい順）。一覧を開いたときに1回だけ読む（全ページに埋め込むと重くなるため）
 - サイト内の全 index.html: PCは左端の縦タブ（ホバーかクリックで開く）、スマホは左下のボタン（タップで開く）と、一覧のパネル
記録は取らない。サーバーへは何も送らない。"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape

CSS = (".sn-b{position:fixed;z-index:900;left:12px;bottom:calc(12px + env(safe-area-inset-bottom));display:flex;align-items:center;gap:6px;"
       "min-height:48px;padding:0 16px;font:inherit;font-size:14px;font-weight:700;color:var(--text,#E6EAF2);background:var(--card,var(--panel,#121926));"
       "border:1px solid var(--border,var(--line,#26324A));border-radius:999px;cursor:pointer}"
       "@media(max-width:959px){body{padding-bottom:76px}.sn-b{transition:transform .2s}.sn-b.sn-away{transform:translateY(90px)}}"
       ".sn-b[hidden]{display:none}.sn-b:hover,.sn-b[aria-expanded=true]{border-color:var(--accent,#7FB2FF)}.sn-b small{font-size:12px;font-weight:400;color:var(--muted,#9AA4B5)}"
       ".sn-b svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round}"
       ".sn-p{position:fixed;z-index:1000;left:0;top:0;bottom:0;width:min(360px,88vw);display:flex;flex-direction:column;"
       "background:var(--bg,#0B0F17);border-right:1px solid var(--border,var(--line,#26324A))}.sn-p[hidden]{display:none}"
       ".sn-h{display:flex;align-items:center;justify-content:space-between;gap:8px;padding:14px 16px 10px}"
       ".sn-h b{font-size:16px;color:var(--text,#E6EAF2)}.sn-x{font:inherit;font-size:14px;min-height:44px;padding:0 14px;color:var(--text,#E6EAF2);"
       "background:transparent;border:1px solid var(--border,var(--line,#26324A));border-radius:8px;cursor:pointer}"
       ".sn-q{margin:0 16px 10px;font:inherit;font-size:16px;min-height:48px;padding:0 12px;color:var(--text,#E6EAF2);background:var(--card,var(--panel,#121926));"
       "border:1px solid var(--border,var(--line,#26324A));border-radius:8px}.sn-q::placeholder{color:var(--muted,#9AA4B5);opacity:1}.sn-q:focus{outline:2px solid var(--accent,#7FB2FF);outline-offset:1px}"
       ".sn-l{flex:1;overflow-y:auto;overscroll-behavior:contain;padding:0 16px 16px}"
       "/* 記事ページの FAQ（details・summary）の見た目を一覧の中では打ち消す */"
       ".sn-l details{margin:0;padding:0;background:none;border:0;border-top:1px solid var(--border,var(--line,#26324A));border-radius:0!important}"
       ".sn-l summary::before{content:none}.sn-l summary{display:flex;align-items:center;gap:8px;min-height:48px;padding:0;"
       "font-size:15px;font-weight:700;color:var(--text,#E6EAF2);cursor:pointer;list-style:none}.sn-l summary::-webkit-details-marker{display:none}"
       ".sn-l summary i{width:10px;height:10px;border-radius:50%;flex:0 0 10px}.sn-l summary small{margin-left:auto;font-size:12px;font-weight:400;color:var(--muted,#9AA4B5)}"
       ".sn-l summary::after{content:\"+\";font-size:18px;color:var(--muted,#9AA4B5);width:16px;text-align:center}.sn-l details[open] summary::after{content:\"-\"}"
       ".sn-l ul{list-style:none;margin:0 0 10px;padding:0}.sn-l li a{display:block;padding:10px 0 10px 18px;font-size:14px;line-height:1.55;"
       "color:var(--text,#E6EAF2);text-decoration:none}.sn-l li a:hover{color:var(--accent,#7FB2FF)}"
       ".sn-x:focus-visible,.sn-l summary:focus-visible,.sn-l li a:focus-visible,.sn-f a:focus-visible{outline:2px solid var(--accent,#7FB2FF);outline-offset:2px}"
       ".sn-l li a[aria-current]{color:var(--accent,#7FB2FF);font-weight:700}.sn-l li a[aria-current]::before{content:\"いま読んでいる記事\";display:block;font-size:12px;font-weight:400;color:var(--muted,#9AA4B5)}"
       ".sn-m{font-size:14px;color:var(--muted,#9AA4B5);padding:12px 0}.sn-f{margin:0;padding:12px 16px calc(12px + env(safe-area-inset-bottom));"
       "border-top:1px solid var(--border,var(--line,#26324A));font-size:14px}.sn-f a{color:var(--accent,#7FB2FF)}"
       ".sn-o{position:fixed;inset:0;z-index:950;background:rgba(0,0,0,.55)}.sn-o[hidden]{display:none}"
       "@media(min-width:960px){.sn-b{left:0;bottom:auto;top:50%;transform:translateY(-50%);flex-direction:column;min-height:0;"
       "padding:16px 10px;border-left:0;border-radius:0 8px 8px 0;writing-mode:vertical-rl;letter-spacing:.2em}"
       ".sn-b small,.sn-b svg{display:none}}"
       "@media print{.sn-b,.sn-p,.sn-o{display:none!important}}")

# 開く: スマホはタップ、PC（ホバーできる・幅960px以上）はホバーでも開く。クリックで開いたら、離れても閉じない
JS = ("var b=document.getElementById('sn-b'),p=document.getElementById('sn-p'),o=document.getElementById('sn-o'),"
      "l=document.getElementById('sn-l'),q=document.getElementById('sn-q'),D=null,ld=0,pin=0,t=0,"
      "hv=matchMedia('(hover:hover) and (min-width:960px)');b.hidden=false;"
      "function esc(s){return s.replace(/[&<>\"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]})}"
      "function draw(){var h=location.pathname,s='';D.forEach(function(g){var cur=0,li=g[2].map(function(a){var u='/'+a[0]+'/',c=u==h;if(c)cur=1;"
      "return '<li data-k=\"'+esc((a[1]+' '+(a[2]||'')).toLowerCase())+'\"><a href=\"'+u+'\"'+(c?' aria-current=\"page\"':'')+'>'+esc(a[1])+'</a></li>'}).join('');"
      "s+='<details'+(cur?' open':'')+'><summary><i style=\"background:'+g[1]+'\"></i>'+esc(g[0])+'<small>'+g[2].length+'本</small></summary><ul>'+li+'</ul></details>'});"
      "l.innerHTML=s;if(q.value)q.oninput();here()}"
      # 今読んでいる記事を一覧の中ほどに送る（scrollIntoView はページ本体まで動かすので使わない）
      "function here(){var a=l.querySelector('[aria-current]');if(a&&!p.hidden)l.scrollTop=a.offsetTop-l.offsetTop-l.clientHeight/2}"
      "function load(){if(ld)return;ld=1;fetch('/nav.json').then(function(r){return r.json()}).then(function(j){D=j;var c=0;j.forEach(function(g){c+=g[2].length});document.getElementById('sn-c').textContent=c+'本';document.getElementById('sn-t').textContent='（'+c+'本）';draw()})"
      ".catch(function(){ld=0;l.innerHTML='<p class=\"sn-m\">一覧を読み込めませんでした。通信を確かめて、もう一度開いてください。</p>'})}"
      "function open(f){clearTimeout(t);load();p.hidden=false;b.setAttribute('aria-expanded','true');if(!hv.matches){o.hidden=false;document.documentElement.style.overflow='hidden'}if(D)here();if(f)q.focus({preventScroll:true})}"
      "function close(){clearTimeout(t);pin=0;p.hidden=true;o.hidden=true;b.setAttribute('aria-expanded','false');document.documentElement.style.overflow=''}"
      "b.onclick=function(){if(!p.hidden&&pin){close();b.focus()}else{pin=1;open(1)}};"
      "b.addEventListener('mouseenter',function(){if(!hv.matches)return;load();clearTimeout(t);t=setTimeout(function(){open(0)},280)});"
      "[b,p].forEach(function(e){e.addEventListener('mouseleave',function(){if(!hv.matches||pin)return;clearTimeout(t);t=setTimeout(close,300)});"
      "e.addEventListener('mouseenter',function(){if(e==p)clearTimeout(t)})});"
      "b.addEventListener('touchstart',load,{passive:true});b.addEventListener('focus',load);"
      "o.onclick=close;document.addEventListener('click',function(e){if(!p.hidden&&!p.contains(e.target)&&!b.contains(e.target))close()});var y=scrollY;addEventListener('scroll',function(){var n=scrollY;if(!hv.matches)b.classList.toggle('sn-away',n>y&&n>200&&innerHeight+n<document.documentElement.scrollHeight-400);y=n},{passive:true});document.getElementById('sn-x').onclick=function(){close();b.focus()};"
      "document.addEventListener('keydown',function(e){if(e.key=='Escape'&&!p.hidden){close();b.focus()}});"
      "function hits(v){return [].filter.call(l.querySelectorAll('li'),function(i){return i.getAttribute('data-k').indexOf(v)>=0}).length}"
      # 0件なら語尾を1字ずつ削って探し直す（「既読スルー」→「既読」）。カテゴリ名に当たればそのまま
      "q.oninput=function(){if(!D)return;var w=q.value.trim().toLowerCase(),v=w,n=0;while(v.length>2&&!hits(v)&&![].some.call(l.querySelectorAll('summary'),function(x){return x.textContent.toLowerCase().indexOf(v)>=0}))v=v.slice(0,-1);[].forEach.call(l.querySelectorAll('details'),function(d){var k=0,g=v&&d.querySelector('summary').textContent.toLowerCase().indexOf(v)>=0;"
      "[].forEach.call(d.querySelectorAll('li'),function(i){var m=!v||g||i.getAttribute('data-k').indexOf(v)>=0;i.hidden=!m;if(m)k++});"
      "d.hidden=!k;n+=k;d.open=v?!!k:!!d.querySelector('[aria-current]')});var m=l.querySelector('.sn-m');if(m)m.remove();"
      "if(w&&!n)l.insertAdjacentHTML('beforeend','<p class=\"sn-m\">「'+esc(q.value)+'」を含む記事は見つかりませんでした。「LINE」「返信」「脈あり」「別れ」のような短い言葉で探してみてください。</p>');else if(n&&v!=w)l.insertAdjacentHTML('afterbegin','<p class=\"sn-m\">「'+esc(q.value)+'」を含む記事はないので、「'+esc(v)+'」で探しました。</p>')}")


def _block(has_map):
    foot = '<a href="/map/">問いからたどる（マインドマップ）</a>' if has_map else '<a href="/">トップに戻る</a>'
    return (f'<!--sidenav--><style>{CSS}</style>'
            f'<button type="button" class="sn-b" id="sn-b" aria-expanded="false" aria-controls="sn-p" hidden>'
            f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg>記事一覧<small id="sn-c"></small></button>'
            f'<div class="sn-o" id="sn-o" hidden></div>'
            f'<div class="sn-p" id="sn-p" role="navigation" aria-label="記事一覧" hidden><div class="sn-h"><b>記事一覧<span id="sn-t"></span></b>'
            f'<button type="button" class="sn-x" id="sn-x">閉じる</button></div>'
            f'<input type="search" class="sn-q" id="sn-q" placeholder="記事を探す（例: 脈あり）" aria-label="記事を探す">'
            f'<div class="sn-l" id="sn-l"><p class="sn-m">読み込み中です。</p></div><p class="sn-f">{foot}</p></div>'
            f'<script>(function(){{{JS}}})()</script><!--/sidenav-->')


def apply(cfg, posts, cats):
    if not cfg.get("sideIndex"):
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
    blk, n = _block((base / "map" / "index.html").exists()), 0
    for f in base.rglob("index.html"):
        s = f.read_text()
        if "</body>" not in s or "flutter" in s:  # Flutter の書き出しなど記事サイト以外には入れない
            continue
        t = re.sub(r"<!--sidenav-->.*?<!--/sidenav-->\n?", "", s, flags=re.S)
        m = re.search(r"<body[^>]*>", t)
        t = t[:m.end()] + blk + t[m.end():] if m else t.replace("</body>", blk + "\n</body>", 1)
        if t != s:
            f.write_text(t)
        n += 1
    return n
