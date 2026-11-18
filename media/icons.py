"""記事の「アイコン＋短い言葉」部品(2026-11-07〜)。seo.patch_article から毎ビルド呼ばれ、冪等。
 - 本文の <i data-ic="名前"></i> を線のインラインSVGに置き換える(名前は ICONS のキー)
 - .pts(アイコン付きの要点)/ .bars(数字の棒グラフ)を使う記事にだけ共通CSSを差し込む
色は各テンプレートの --accent --border --card --text --muted を使うので、全メディアで同じ書き方で済む。
書き方は docs/quality/article.md「文字を減らし、アイコンと図で見せる」。"""
import re

# 24x24・線幅2の線アイコン。意味が1つに決まるものだけを置く(飾り用のアイコンは足さない)
ICONS = {
    "check": '<path d="M5 12l5 5L20 7"/>',
    "ng": '<circle cx="12" cy="12" r="9"/><path d="M6 6l12 12"/>',
    "alert": '<path d="M12 3l10 18H2z"/><path d="M12 10v5M12 18v.5"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="1"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "phone": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="1"/><path d="M3 6l9 7 9-7"/>',
    "link": '<path d="M10 14a4 4 0 0 0 6 0l3-3a4 4 0 0 0-6-6l-1 1"/><path d="M14 10a4 4 0 0 0-6 0l-3 3a4 4 0 0 0 6 6l1-1"/>',
    "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="M16 16l5 5"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "calendar": '<rect x="3" y="5" width="18" height="16" rx="1"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "money": '<circle cx="12" cy="12" r="9"/><path d="M8 7l4 5 4-5M12 12v6M9 13h6M9 16h6"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="1"/><path d="M2 10h20M6 15h4"/>',
    "home": '<path d="M3 11l9-7 9 7"/><path d="M5 10v10h14V10"/>',
    "person": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/>',
    "family": '<circle cx="8" cy="7" r="3"/><circle cx="17" cy="9" r="2"/><path d="M2 20c0-4 3-6 6-6s6 2 6 6M14 20c0-3 1.5-5 3-5s4 2 4 5"/>',
    "talk": '<path d="M3 4h12v8H8l-5 4z"/><path d="M15 9h6v8l-3-2h-6v-3"/>',
    "book": '<path d="M4 4h7a2 2 0 0 1 2 2v14a2 2 0 0 0-2-2H4z"/><path d="M20 4h-5a2 2 0 0 0-2 2v14a2 2 0 0 1 2-2h5z"/>',
    "brain": '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 6 1V5a2 2 0 0 0-3-1z"/><path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-6 1"/>',
    "heart": '<path d="M12 20s-8-5-8-11a4 4 0 0 1 8-1 4 4 0 0 1 8 1c0 6-8 11-8 11z"/>',
    "idea": '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-4 10.5c.7.7 1 1.5 1 2.5h6c0-1 .3-1.8 1-2.5A6 6 0 0 0 12 3z"/>',
    "question": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.7v.5M12 17v.5"/>',
    "list": '<path d="M9 6h12M9 12h12M9 18h12M4 6h.5M4 12h.5M4 18h.5"/>',
    "step": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "doc": '<path d="M6 2h8l5 5v15H6z"/><path d="M14 2v5h5M9 13h7M9 17h7"/>',
    "chart": '<path d="M4 20V4M4 20h16"/><path d="M8 16v-4M12 16V8M16 16v-6"/>',
    "ai": '<rect x="6" y="6" width="12" height="12" rx="1"/><path d="M10 10h4v4h-4zM9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    "school": '<path d="M2 9l10-5 10 5-10 5z"/><path d="M6 11v5c2 2 10 2 12 0v-5"/>',
    "hospital": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M12 8v6M9 11h6"/>',
    "bank": '<path d="M3 9l9-5 9 5M5 9v9M10 9v9M14 9v9M19 9v9M3 21h18"/>',
}

CSS = (
    ".ic{width:22px;height:22px;flex:0 0 22px;fill:none;stroke:var(--accent);stroke-width:2;stroke-linecap:round;stroke-linejoin:round}"
    ".pts{list-style:none;padding:0;margin:20px 0;display:grid;gap:10px}"
    "@media(min-width:600px){.pts{grid-template-columns:1fr 1fr}}"
    ".pts li{display:flex;gap:12px;align-items:flex-start;margin:0;padding:14px 16px;background:var(--card);border:1px solid var(--border);border-radius:8px;line-height:1.6}"
    ".pts li .ic{margin-top:2px}"
    ".pts b{display:block;font-size:15px;color:var(--text)}"
    ".pts span{display:block;font-size:14px;color:var(--muted)}"
    ".bars{margin:20px 0;padding:14px 16px;border:1px solid var(--border);border-radius:8px;background:var(--card)}"
    ".bars .bt{font-size:14px;font-weight:700;margin:0 0 10px;color:var(--text)}"
    ".bars .br{margin:10px 0}"
    ".bars .bl{display:flex;justify-content:space-between;gap:8px;font-size:14px;color:var(--text)}"
    ".bars .bv{font-weight:700;color:var(--accent);white-space:nowrap}"
    ".bars .bx{height:8px;margin-top:4px;background:var(--border);border-radius:4px;overflow:hidden}"
    ".bars .bx i{display:block;height:100%;background:var(--accent)}"
    ".bars .bs{font-size:12px;color:var(--muted);margin:10px 0 0}"
)

_MARK = re.compile(r'<i data-ic="([a-z]+)"></i>')


def _svg(m):
    body = ICONS.get(m.group(1))
    if not body:
        return ""  # 知らない名前は消す(壊れた四角を出さない)
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{body}</svg>'


def apply(s):
    s = _MARK.sub(_svg, s)
    s = re.sub(r'<style id="ic">.*?</style>\n?', "", s, flags=re.S)
    if 'class="pts"' in s or 'class="bars"' in s or 'class="ic"' in s:
        s = s.replace("</head>", f'<style id="ic">{CSS}</style>\n</head>', 1)
    return s
