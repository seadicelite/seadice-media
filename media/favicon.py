#!/usr/bin/env python3
"""メディア・講座サイトのファビコン。seadice.win トップの各メディアのピクトグラム（1色の線画）を、テーマ色の角丸四角に白抜きで置く。
ページには <link rel="icon" href="/favicon.svg"> を入れ、sites/{slug}/favicon.svg を書き出す（Google 検索結果のアイコンは
data URI だと出ないため、ファイルにする）。
新しいメディアは PICTO に1行足す（無ければ汎用の丸）。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PICTO = {  # 24x24 の線画（トップページ p/index.html の .picto と同じ形）
    "ai": '<rect x="6.5" y="6.5" width="11" height="11" rx="1.5"/><path d="M9.5 3v3.5M14.5 3v3.5M9.5 17.5V21M14.5 17.5V21M3 9.5h3.5M3 14.5h3.5M17.5 9.5H21M17.5 14.5H21M10 12h4"/>',
    "bohan": '<path d="M12 3l7.5 3v5.5c0 4.5-3.2 8-7.5 9.5-4.3-1.5-7.5-5-7.5-9.5V6z"/><path d="M9 12l2 2 4-4"/>',
    "boueki": '<path d="M3.5 15.5h17l-2.5 5h-12z"/><path d="M6.5 15.5v-4h11v4M9.5 11.5v-4h5v4M12 7.5v-4"/>',
    "counselor": '<path d="M3.5 4.5h11v8h-6l-3 3v-3h-2z"/><path d="M17.5 8.5h3v8h-2v3l-3-3h-5v-1"/>',
    "dokugaku": '<path d="M12 6.5c-2-1.5-5-2-8.5-2v14c3.5 0 6.5.5 8.5 2 2-1.5 5-2 8.5-2v-14c-3.5 0-6.5.5-8.5 2zM12 6.5v14"/>',
    "hanzai": '<path d="M7 19.5c-1.5-2-2.5-4.5-2.5-7.5a7.5 7.5 0 0 1 15 0c0 2-.3 4-1 5.5"/><path d="M9.5 20.5c-1-1.8-1.5-4-1.5-8.5a4 4 0 0 1 8 0c0 2 0 4-.5 5.5"/><path d="M12 12v8.5"/>',
    "hanzaigaku": '<path d="M12 3.5v17M7.5 20.5h9M4.5 7.5h15M7 7.5l-3 6a3 3 0 0 0 6 0zM17 7.5l-3 6a3 3 0 0 0 6 0z"/>',
    "hoikushi": '<rect x="3.5" y="12.5" width="8" height="8" rx="1"/><rect x="12.5" y="12.5" width="8" height="8" rx="1"/><rect x="8" y="3.5" width="8" height="8" rx="1"/>',
    "kaigofukushi": '<path d="M12 20s-7.5-4.5-7.5-10a4 4 0 0 1 7.5-2 4 4 0 0 1 7.5 2c0 5.5-7.5 10-7.5 10z"/>',
    "kodokeizai": '<path d="M3.5 20.5h17M6.5 20.5v-6M11 20.5v-10M15.5 20.5v-4M19.5 20.5V6"/>',
    "kogei": '<path d="M3.5 11.5h17a8.5 8.5 0 0 1-17 0z"/><path d="M9 20.5h6M10 7.5c0-1.5 1.5-1.5 1.5-3M13.5 7.5c0-1.5 1.5-1.5 1.5-3"/>',
    "kokoro": '<path d="M2.5 12.5h4l2-5 3.5 10 2.5-7 1.5 2h5.5"/>',
    "kosodate": '<circle cx="8.5" cy="6" r="2.5"/><path d="M4.5 20.5v-5a4 4 0 0 1 8 0v5"/><circle cx="17" cy="10.5" r="2"/><path d="M14 20.5v-3a3 3 0 0 1 6 0v3"/>',
    "ledger": '<circle cx="12" cy="12" r="8.5"/><path d="M9 8l3 4 3-4M12 12v5M9.5 13.5h5"/>',
    "oya": '<circle cx="10" cy="5" r="2.5"/><path d="M6.5 20.5v-6a3.5 3.5 0 0 1 7 0v6"/><path d="M13.5 13.5l3 1.5v5.5"/>',
    "research": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/>',
    "choco": '<rect x="5" y="4" width="14" height="16" rx="1.5"/><path d="M5 9.3h14M5 14.6h14M12 4v16"/>',
    "senbei": '<circle cx="12" cy="12" r="8.5"/><path d="M8.5 9.5h.01M14.5 8h.01M15.5 13.5h.01M10 15h.01M12 11.5h.01"/>',
    "shakaihosho": '<path d="M3.5 12a8.5 8.5 0 0 1 17 0z"/><path d="M12 12v6.5a2 2 0 0 1-4 0M12 3.5v-1"/>',
    "shinri": '<path d="M14.5 20.5v-3h2a2 2 0 0 0 2-2V13l1.5-.5-1.5-3A7 7 0 1 0 7.5 15v5.5"/>',
    "tantei": '<rect x="3.5" y="4.5" width="17" height="12" rx="1.5"/><path d="M8.5 20.5h7"/><circle cx="11" cy="10" r="2.5"/><path d="M12.8 11.8l2.7 2.7"/>',
    "tetsugaku": '<circle cx="12" cy="12" r="8.5"/><path d="M9.6 9.6a2.5 2.5 0 1 1 3.4 2.3c-.6.3-1 .8-1 1.5v.6"/><circle cx="12" cy="16.8" r=".9" fill="currentColor" stroke="none"/>',
    "tetsugaku-nyumon": '<path d="M4.5 20.5h15M6 17.5h12M7.5 17.5v-8M12 17.5v-8M16.5 17.5v-8M4.5 9.5h15L12 4z"/>',
    "umbra": '<path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6z"/><circle cx="12" cy="12" r="2.5"/>',
}


def _ink(accent):
    """明るいテーマ色（黄・水色など）の上は黒っぽい線、暗い色の上は白い線にする（どちらもコントラストを保つ）。"""
    r, g, b = (int(accent.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    lum = sum(w * (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for w, c in zip((0.2126, 0.7152, 0.0722), (r, g, b)))
    return "#111" if lum > 0.3 else "#fff"


def svg(slug, accent, fg=None):
    """64x64。角丸8（質実剛健: 8px以下）、線は太め（16px表示でもつぶれない太さ）。"""
    fg = fg or _ink(accent)
    body = PICTO.get(slug, '<circle cx="12" cy="12" r="6"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="8" fill="{accent}"/>'
            f'<g transform="translate(8 8) scale(2)" fill="none" stroke="{fg}" color="{fg}" stroke-width="2.1" '
            f'stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>')


def tag(site_dir, accent, fg=None):
    """sites/{slug}/favicon.svg を（変わったときだけ）書き、<head> に入れるタグを返す。"""
    d = ROOT / site_dir  # 絶対パス（study.py の OUT）でもそのまま使える
    f = d / "favicon.svg"
    s = svg(d.name, accent, fg)
    if d.exists() and (not f.exists() or f.read_text() != s):
        f.write_text(s)
    return '<link rel="icon" type="image/svg+xml" href="/favicon.svg">'

