"""読んだ記事のチェック（設定 "readCheck": true のメディアだけ）。build.py の最後に毎回呼ばれ、冪等に次を入れる。
 - 記事: 関連記事の上に「読んだ記事にする」ボタン（押し直すと取り消し）と「全N本のうちM本読んだ」
 - トップ・カテゴリ: 読んだ記事のカードに「読んだ」の札、見出しの下に読んだ本数
 - 道具: media/{slug}-matrix.json で道具のURLが入っている行の記事を「この道具とつながる記事」として並べ、読んだ本数と次に読む記事を出す
 - どのページでも、本文中の読んだ記事へのリンクに小さく「読んだ」を付ける
記録はブラウザの localStorage（キー {slug}-read、{記事slug: 日付}）だけ。サーバーへは送らない(docs/quality/base.md「個人情報を集めない」)。"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape

# 道具のページは手書きで変数名が違う（--card/--panel、--border/--line）ので両方を受ける
CARD, LINE = "var(--card,var(--panel,#121926))", "var(--border,var(--line,#26324A))"
CSS = (f".rc{{margin:40px 0 0;padding:18px;background:{CARD};border:1px solid {LINE};border-radius:8px;text-align:center}}"
       ".rc-b{font:inherit;font-size:15px;font-weight:700;min-height:48px;padding:10px 22px;border-radius:8px;cursor:pointer;"
       "background:var(--accent);color:var(--bg);border:1px solid var(--accent)}"
       ".rc-b[aria-pressed=true]{background:transparent;color:var(--accent)}"
       ".rc-n{font-size:13px;color:var(--muted);margin:10px 0 0;line-height:1.6}"
       ".rc-prog{font-size:13px;color:var(--muted);margin:0 0 18px}.rc-prog b{color:var(--accent)}"
       ".rc-done{position:relative}.rc-done::after{content:\"読んだ\";position:absolute;top:8px;right:8px;z-index:2;font-size:12px;font-weight:700;"
       "letter-spacing:.06em;padding:2px 8px;border-radius:4px;background:var(--bg);color:var(--accent);border:1px solid var(--accent)}"
       "a.rc-in::after{content:\"読んだ\";display:inline-block;margin-left:6px;font-size:12px;font-weight:700;line-height:1.5;padding:0 6px;"
       "border-radius:4px;color:var(--accent);border:1px solid var(--accent);vertical-align:1px;text-decoration:none}"
       f".rct{{margin:32px 0;padding:18px;background:{CARD};border:1px solid {LINE};border-radius:8px;text-align:left}}"
       ".rct h2{font-size:17px;margin:0 0 6px;padding:0;border:0}.rct .rc-n{margin:0 0 10px}.rct .rc-n b{color:var(--accent)}"
       ".rct ul{list-style:none;margin:0;padding:0}.rct li{margin:0;padding:0;border-top:1px solid " + LINE + "}"
       ".rct li a{display:block;padding:12px 0;font-size:15px;line-height:1.5;color:var(--text);text-decoration:none}.rct li a:hover{color:var(--accent)}"
       ".rct li small{display:block;font-size:12px;color:var(--muted)}.rct .rc-next{display:none;margin:0 0 12px;font-size:14px}"
       ".rct .rc-next a{color:var(--accent);font-weight:700}")

_LOAD = "var K='%s-read',R={};try{R=JSON.parse(localStorage.getItem(K)||'{}')||{}}catch(e){}"
# 本文中の読んだ記事へのリンクに印を付ける（カード型は右上の札、文中のリンクは小さな札）。上部ナビとフッターは除く
_MARK = ("function rcMark(){[].forEach.call(document.querySelectorAll('a[href]'),function(a){var h=a.getAttribute('href')||'',m=h.match(/^\\/([a-z0-9-]+)\\/$/);"
         "a.classList.remove('rc-done','rc-in');if(!m||!R[m[1]]||a.closest('nav.top,footer,.ticker'))return;"
         "a.classList.add(a.matches('a.card,a.feat,a.srow,a.dp')?'rc-done':'rc-in')})}rcMark();")


def _article_block(key, slug, total):
    js = (_LOAD % key + _MARK + f"var S='{slug}',T={total},b=document.getElementById('rc-b'),n=document.getElementById('rc-n');"
          "function c(){return Object.keys(R).length}"
          "function show(){var on=!!R[S];b.setAttribute('aria-pressed',on);b.textContent=on?'読んだ（押すと取り消し）':'読んだ記事にする';"
          "n.textContent=c()?'全'+T+'本のうち '+c()+'本 読みました。記録はこの端末のブラウザにだけ残ります。':'押すと、トップの一覧や道具のページに「読んだ」と出ます。記録はこの端末のブラウザにだけ残ります。'}"
          "b.onclick=function(){if(R[S])delete R[S];else R[S]=new Date().toISOString().slice(0,10);"
          "try{localStorage.setItem(K,JSON.stringify(R))}catch(e){n.textContent='このブラウザでは保存できません（プライベートブラウズなど）。';return}show()};show()")
    return (f'<!--readcheck--><div class="rc"><button type="button" class="rc-b" id="rc-b" aria-pressed="false">読んだ記事にする</button>'
            f'<p class="rc-n" id="rc-n" aria-live="polite"></p></div><script>(function(){{{js}}})()</script><!--/readcheck-->')


def _list_block(key, total):
    js = (_LOAD % key + _MARK + f"var T={total},k=Object.keys(R).length,p=document.getElementById('rc-prog');"
          "if(k&&p){p.innerHTML='全'+T+'本のうち <b>'+k+'本</b> 読みました（この端末の記録）';p.hidden=false}")
    return f"<!--readcheck--><script>(function(){{{js}}})()</script><!--/readcheck-->"


def _tool_block(key, arts):
    lis = "".join(f'<li><a href="/{p["slug"]}/"><small>{E(lab)}</small>{E(p["title"])}</a></li>' for p, lab in arts)
    js = (_LOAD % key + _MARK + "var L=[].map.call(document.querySelectorAll('#rct li a'),function(a){return a}),"
          "k=L.filter(function(a){return R[a.getAttribute('href').slice(1,-1)]}).length,n=document.getElementById('rct-n');"
          "if(k)n.innerHTML=L.length+'本のうち <b>'+k+'本</b> 読みました（この端末の記録）。';"
          "var x=L.filter(function(a){return !R[a.getAttribute('href').slice(1,-1)]})[0],nx=document.getElementById('rct-next');"
          "if(x&&k){nx.innerHTML='次に読むなら: <a href=\"'+x.getAttribute('href')+'\"></a>';nx.lastChild.textContent=x.lastChild.textContent;nx.style.display='block'}"
          "else if(!x){n.innerHTML='つながる記事を<b>すべて</b>読みました（この端末の記録）。'}")
    return (f'<!--readcheck--><section class="rct" id="rct" aria-labelledby="rct-h"><h2 id="rct-h">この道具とつながる記事（{len(arts)}本）</h2>'
            f'<p class="rc-n" id="rct-n" aria-live="polite">記事の下の「読んだ記事にする」を押すと、ここに読んだ本数が出ます。</p>'
            f'<p class="rc-next" id="rct-next"></p><ul>{lis}</ul></section><script>(function(){{{js}}})()</script><!--/readcheck-->')


def _put_css(s):
    """CSS は /*rc*/…/*/rc*/ の間に入れ、毎回差し替える（最初の版は印なしで .rc{ から .rc-done::after{…} までだった）。"""
    blk = "/*rc*/" + CSS + "/*/rc*/"
    if "/*rc*/" in s:
        return re.sub(r"/\*rc\*/.*?/\*/rc\*/", lambda m: blk, s, count=1, flags=re.S)
    m = re.search(r"\.rc\{margin:40px.*?\.rc-done::after\{[^}]*\}", s, flags=re.S)
    if m:
        return s[:m.start()] + blk + s[m.end():]
    return s.replace("</style>", blk + "</style>", 1)


def _sub(s, blk, before):
    if "<!--readcheck-->" in s:
        return re.sub(r"<!--readcheck-->.*?<!--/readcheck-->", lambda m: blk, s, flags=re.S)
    for b in before:
        if b in s:
            return s.replace(b, blk + "\n" + b, 1)
    return s.replace("</body>", blk + "\n</body>", 1)


def _tools(cfg, posts):
    """マスの表で、道具のURLが入っている行の記事（問いの列の順）を道具ごとに集める。"""
    f = ROOT / f"media/{cfg['slug']}-matrix.json"
    if not f.exists():
        return {}
    m, by, url = json.loads(f.read_text()), {p["slug"]: p for p in posts}, cfg["url"].rstrip("/")
    out = {}
    for r in m["rows"]:
        tools = {u[len(url):] for v in r["cells"].values() for u in v if u.startswith(url)}
        arts = [(by[s], r["label"]) for c in m["cols"] for s in r["cells"].get(c["id"], []) if s in by]
        for t in tools:
            if t.strip("/") in by:  # 記事と同じURLの道具（記事側にボタンがある）
                continue
            have = {p["slug"] for p, _ in out.setdefault(t, [])}
            out[t] += [a for a in arts if a[0]["slug"] not in have]
    return out


def apply(cfg, posts):
    if not cfg.get("readCheck"):
        return 0
    base, key, total, n = ROOT / cfg["path"], cfg["slug"], len(posts), 0
    for p in posts:
        f = base / p["slug"] / "index.html"
        if not f.exists():
            continue
        s = _sub(f.read_text(), _article_block(key, p["slug"], total), ["<!--related-->", '<div class="sources">'])
        f.write_text(_put_css(s))
        n += 1
    # トップとカテゴリは毎回作り直されるので、そのつど差し込む
    for f in [base / "index.html", *sorted((base / "category").glob("*/index.html"))]:
        s = f.read_text()
        if "<!--readcheck-->" not in s:
            s = re.sub(r"(<div class=\"(?:maghead|hero)\">.*?</div>)", r'\1<p class="rc-prog" id="rc-prog" hidden></p>', s, count=1, flags=re.S)
        s = _sub(s, _list_block(key, total), [])
        f.write_text(_put_css(s))
    # 道具（手書きのページ。フッターの前に入れる）
    for path, arts in _tools(cfg, posts).items():
        f = base / path.strip("/") / "index.html"
        if f.exists() and arts and "data-rc-own" not in f.read_text():  # 自分で読んだ本数を出す道具（年表）は除く
            s = _sub(f.read_text(), _tool_block(key, arts), ["<footer"])
            f.write_text(_put_css(s))
    return n
