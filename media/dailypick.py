"""トップに日替わりで1本の記事を出す（設定 "dailyPick": {"col": マスの列id, "title": 見出し} があるメディアだけ）。
media/{slug}-matrix.json のその列に入っている記事から、日本時間の日付で1本を選ぶ。選ぶのはブラウザの中だけで、何も送らない。
HTML にはビルドした日の1本を書いておく（JSが動かない環境・クローラー向け）。build.py の最後（readcheck の前）に毎回呼ばれ、冪等。"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
CSS = ("/*dp*/.dp-box{margin:0 0 28px}.dp-h{font-size:13px;font-weight:700;letter-spacing:.08em;color:var(--accent);margin:0 0 8px}"
       "a.dp{display:block;background:var(--card);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:8px;padding:14px 16px;text-decoration:none;color:var(--text)}"
       "a.dp:hover{border-color:var(--accent)}a.dp b{display:block;font-size:17px;line-height:1.5;margin:0 0 6px}a.dp span{display:block;font-size:14px;color:var(--muted);line-height:1.7}a.dp.rc-done b{padding-right:64px}/*/dp*/")


def apply(cfg, posts):
    dp = cfg.get("dailyPick")
    f = ROOT / f"media/{cfg['slug']}-matrix.json"
    if not dp or not f.exists():
        return 0
    by = {p["slug"]: p for p in posts}
    m = json.loads(f.read_text())
    picks = [by[s] for r in m["rows"] for s in r["cells"].get(dp["col"], []) if s in by]
    if not picks:
        return 0
    data = json.dumps([[p["slug"], p["title"], p.get("summary", "")] for p in picks], ensure_ascii=False).replace("</", "<\\/")
    # HTML にはビルドした日（日本時間）の1本を書く（JSと同じ選び方。JSが動かない環境・クローラー向け）
    import time
    p0 = picks[int((time.time() + 32400) // 86400) % len(picks)]
    box = (f'<!--dailypick--><section class="dp-box" aria-labelledby="dp-h"><p class="dp-h" id="dp-h">{E(dp.get("title", "今日の1本"))}</p>'
           f'<a class="dp" id="dp" href="/{p0["slug"]}/"><b>{E(p0["title"])}</b><span>{E(p0.get("summary", ""))}</span></a></section>'
           "<script>(function(){var L=" + data + ",d=Math.floor((Date.now()+324e5)/864e5),x=L[d%L.length],a=document.getElementById('dp');"
           "a.href='/'+x[0]+'/';a.firstChild.textContent=x[1];a.lastChild.textContent=x[2]})()</script><!--/dailypick-->")
    t = (ROOT / cfg["path"] / "index.html")
    s = t.read_text()
    if "<!--dailypick-->" in s:
        s = re.sub(r"<!--dailypick-->.*?<!--/dailypick-->", lambda _: box, s, flags=re.S)
    else:
        s = re.sub(r"(<div class=\"(?:maghead|hero)\">.*?</div>)", lambda m_: m_.group(1) + box, s, count=1, flags=re.S)
    s = re.sub(r"/\*dp\*/.*?/\*/dp\*/", "", s, flags=re.S).replace("</style>", CSS + "</style>", 1)
    t.write_text(s)
    return len(picks)
