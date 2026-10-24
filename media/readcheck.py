"""読んだ記事のチェック（設定 "readCheck": true のメディアだけ）。build.py の最後に毎回呼ばれ、冪等に次を入れる。
 - 記事: 関連記事の上に「読んだ記事にする」ボタン（押し直すと取り消し）と「全N本のうちM本読んだ」
 - トップ・カテゴリ: 読んだ記事のカードに「読んだ」の札、見出しの下に読んだ本数
記録はブラウザの localStorage（キー {slug}-read、{記事slug: 日付}）だけ。サーバーへは送らない(docs/quality/base.md「個人情報を集めない」)。"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CSS = (".rc{margin:40px 0 0;padding:18px;background:var(--card);border:1px solid var(--border);border-radius:12px;text-align:center}"
       ".rc-b{font:inherit;font-size:15px;font-weight:700;min-height:48px;padding:10px 22px;border-radius:8px;cursor:pointer;"
       "background:var(--accent);color:var(--bg);border:1px solid var(--accent)}"
       ".rc-b[aria-pressed=true]{background:transparent;color:var(--accent)}"
       ".rc-n{font-size:13px;color:var(--muted);margin:10px 0 0;line-height:1.6}"
       ".rc-prog{font-size:13px;color:var(--muted);margin:0 0 18px}.rc-prog b{color:var(--accent)}"
       ".rc-done{position:relative}.rc-done::after{content:\"読んだ\";position:absolute;top:8px;right:8px;z-index:2;font-size:12px;font-weight:700;"
       "letter-spacing:.06em;padding:2px 8px;border-radius:4px;background:var(--bg);color:var(--accent);border:1px solid var(--accent)}")

_LOAD = "var K='%s-read',R={};try{R=JSON.parse(localStorage.getItem(K)||'{}')||{}}catch(e){}"


def _article_block(key, slug, total):
    js = (_LOAD % key + f"var S='{slug}',T={total},b=document.getElementById('rc-b'),n=document.getElementById('rc-n');"
          "function c(){return Object.keys(R).length}"
          "function show(){var on=!!R[S];b.setAttribute('aria-pressed',on);b.textContent=on?'読んだ（押すと取り消し）':'読んだ記事にする';"
          "n.textContent=c()?'全'+T+'本のうち '+c()+'本 読みました。記録はこの端末のブラウザにだけ残ります。':'押すと、トップの一覧に「読んだ」と出ます。記録はこの端末のブラウザにだけ残ります。'}"
          "b.onclick=function(){if(R[S])delete R[S];else R[S]=new Date().toISOString().slice(0,10);"
          "try{localStorage.setItem(K,JSON.stringify(R))}catch(e){n.textContent='このブラウザでは保存できません（プライベートブラウズなど）。';return}show()};show()")
    return (f'<!--readcheck--><div class="rc"><button type="button" class="rc-b" id="rc-b" aria-pressed="false">読んだ記事にする</button>'
            f'<p class="rc-n" id="rc-n" aria-live="polite"></p></div><script>{js}</script><!--/readcheck-->')


def _list_block(key, total):
    js = (_LOAD % key + f"var T={total},m=0;"
          "[].forEach.call(document.querySelectorAll('a.card,a.feat,a.srow'),function(a){var s=(a.getAttribute('href')||'').replace(/\\//g,'');"
          "if(R[s]){a.classList.add('rc-done');a.setAttribute('aria-label',(a.textContent||'').trim()+'（読んだ）')}});"
          "var k=Object.keys(R).length,p=document.getElementById('rc-prog');"
          "if(k&&p){p.innerHTML='全'+T+'本のうち <b>'+k+'本</b> 読みました（この端末の記録）';p.hidden=false}")
    return f"<!--readcheck--><script>{js}</script><!--/readcheck-->"


def _put_css(s):
    return s if ".rc-done{" in s else s.replace("</style>", CSS + "</style>", 1)


def apply(cfg, posts):
    if not cfg.get("readCheck"):
        return 0
    base, key, total, n = ROOT / cfg["path"], cfg["slug"], len(posts), 0
    for p in posts:
        f = base / p["slug"] / "index.html"
        if not f.exists():
            continue
        s = f.read_text()
        blk = _article_block(key, p["slug"], total)
        if "<!--readcheck-->" in s:
            s = re.sub(r"<!--readcheck-->.*?<!--/readcheck-->", lambda m: blk, s, flags=re.S)
        elif "<!--related-->" in s:
            s = s.replace("<!--related-->", blk + "\n    <!--related-->", 1)
        else:
            s = s.replace('<div class="sources">', blk + '\n    <div class="sources">', 1)
        s = _put_css(s)
        f.write_text(s)
        n += 1
    # トップとカテゴリは毎回作り直されるので、そのつど差し込む
    for f in [base / "index.html", *sorted((base / "category").glob("*/index.html"))]:
        s = f.read_text()
        if "<!--readcheck-->" in s:
            continue
        s = re.sub(r"(<div class=\"(?:maghead|hero)\">.*?</div>)", r'\1<p class="rc-prog" id="rc-prog" hidden></p>', s, count=1, flags=re.S)
        s = s.replace("</body>", _list_block(key, total) + "\n</body>", 1)
        f.write_text(_put_css(s))
    return n
