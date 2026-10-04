"""しぐさ索引(/shigusa/)の項目イラスト。線画のインラインSVG(64x64、色は currentColor)。

キーは media/umbra-shigusa.json の items[].id。無い項目は記事の写真を使う。
"""


def eye(cx, cy, w=12, h=7, px=None, py=None, r=3):
    px = cx if px is None else px
    py = cy if py is None else py
    return (f'<path d="M{cx - w} {cy} Q{cx} {cy - h * 1.6} {cx + w} {cy} Q{cx} {cy + h * 1.6} {cx - w} {cy}Z"/>'
            f'<circle cx="{px}" cy="{py}" r="{r}" fill="currentColor"/>')


def fig(x, y=10, arms=None):
    """立ち姿の棒人間。y は頭の中心。arms を渡すと腕を差し替える。"""
    a = arms if arms is not None else f'<polyline points="{x - 8},{y + 20} {x},{y + 11} {x + 8},{y + 20}"/>'
    return (f'<circle cx="{x}" cy="{y}" r="5"/><line x1="{x}" y1="{y + 5}" x2="{x}" y2="{y + 26}"/>'
            f'<polyline points="{x - 6},{y + 42} {x},{y + 26} {x + 6},{y + 42}"/>' + a)


def arrow(x1, y1, x2, y2, both=False):
    import math
    a = math.atan2(y2 - y1, x2 - x1)

    def head(x, y, ang):
        p1 = (x - 5 * math.cos(ang - 0.5), y - 5 * math.sin(ang - 0.5))
        p2 = (x - 5 * math.cos(ang + 0.5), y - 5 * math.sin(ang + 0.5))
        return f'<polyline points="{p1[0]:.1f},{p1[1]:.1f} {x},{y} {p2[0]:.1f},{p2[1]:.1f}"/>'
    s = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>' + head(x2, y2, a)
    return s + (head(x1, y1, a + math.pi) if both else "")


def phone(inner=""):
    return f'<rect x="20" y="6" width="24" height="52" rx="4"/><line x1="29" y1="52" x2="35" y2="52"/>{inner}'


def chair(x0=8, x1=26, seat=40):
    return (f'<line x1="{x0}" y1="{seat}" x2="{x1}" y2="{seat}"/><line x1="{x0}" y1="{seat}" x2="{x0}" y2="20"/>'
            f'<line x1="{x0}" y1="{seat}" x2="{x0}" y2="58"/><line x1="{x1}" y1="{seat}" x2="{x1}" y2="58"/>')


FACE = '<circle cx="32" cy="32" r="22"/>'

ILL = {
    # 目・視線
    "eye-contact": eye(17, 32, 10, 6, 20, 32) + eye(47, 32, 10, 6, 44, 32) + '<line x1="27" y1="32" x2="37" y2="32" stroke-dasharray="2 3"/>',
    "look-away": eye(28, 36, 16, 9, 37, 32, 4) + arrow(44, 24, 56, 12),
    "pupil": eye(32, 32, 22, 12, r=8).replace('fill="currentColor"', 'fill="currentColor" fill-opacity=".3"') + '<circle cx="32" cy="32" r="3" fill="currentColor"/>',
    "blink": '<path d="M12 30 Q32 46 52 30"/><line x1="18" y1="36" x2="14" y2="42"/><line x1="26" y1="39" x2="24" y2="46"/><line x1="38" y1="39" x2="40" y2="46"/><line x1="46" y1="36" x2="50" y2="42"/>',
    "gaze-avoidance": FACE + '<line x1="18" y1="28" x2="28" y2="28"/><line x1="36" y1="28" x2="46" y2="28"/><circle cx="23" cy="32" r="2.5" fill="currentColor"/><circle cx="41" cy="32" r="2.5" fill="currentColor"/><line x1="28" y1="43" x2="36" y2="43"/>',
    # 表情
    "smile": FACE + '<path d="M20 29 q4 -5 8 0"/><path d="M36 29 q4 -5 8 0"/><line x1="15" y1="27" x2="11" y2="25"/><line x1="15" y1="31" x2="11" y2="32"/><line x1="49" y1="27" x2="53" y2="25"/><line x1="49" y1="31" x2="53" y2="32"/><path d="M22 38 Q32 48 42 38"/>',
    "microexpression": '<circle cx="27" cy="36" r="18"/><circle cx="21" cy="32" r="2" fill="currentColor"/><circle cx="33" cy="32" r="2" fill="currentColor"/><path d="M20 45 Q27 41 34 45"/><circle cx="50" cy="15" r="8"/><line x1="50" y1="15" x2="50" y2="10"/><line x1="50" y1="15" x2="54" y2="17"/><line x1="48" y1="5" x2="52" y2="5"/>',
    "first-impression": '<circle cx="26" cy="36" r="17"/><circle cx="20" cy="33" r="2" fill="currentColor"/><circle cx="32" cy="33" r="2" fill="currentColor"/><path d="M20 41 Q26 46 32 41"/><path d="M45 9 q0 -5 5 -5 q5 0 5 5 q0 4 -5 6 v4"/><circle cx="50" cy="25" r="1.5" fill="currentColor"/>',
    "eyebrow-flash": eye(30, 40, 16, 8) + '<path d="M14 22 Q30 11 46 22"/>' + arrow(54, 30, 54, 12),
    # 手・触れる
    "self-touch": '<circle cx="28" cy="30" r="18"/><circle cx="22" cy="27" r="2" fill="currentColor"/><circle cx="34" cy="27" r="2" fill="currentColor"/><line x1="23" y1="38" x2="31" y2="38"/><ellipse cx="45" cy="38" rx="6" ry="10" transform="rotate(-20 45 38)"/><line x1="50" y1="47" x2="56" y2="60"/>',
    "arm-cross": '<circle cx="32" cy="12" r="8"/><path d="M14 62 L17 34 Q32 25 47 34 L50 62"/><line x1="17" y1="40" x2="45" y2="50" stroke-width="4"/><line x1="47" y1="40" x2="19" y2="50" stroke-width="4"/>',
    "touch": fig(18, 12, '<polyline points="10,32 18,23"/><line x1="18" y1="23" x2="40" y2="22"/>') + fig(46, 12),
    # 姿勢・距離
    "body-orientation": fig(16, 10) + fig(48, 10) + arrow(10, 60, 24, 60) + arrow(54, 60, 40, 60),
    "distance": fig(12, 10) + fig(52, 10) + arrow(22, 36, 42, 36, both=True),
    "mimicry": fig(18, 12, '<polyline points="10,32 18,23 26,14"/>') + fig(46, 12, '<polyline points="54,32 46,23 38,14"/>'),
    "power-pose": '<circle cx="32" cy="9" r="6"/><line x1="32" y1="15" x2="32" y2="38"/><polyline points="20,60 32,38 44,60"/><polyline points="32,21 19,29 27,36"/><polyline points="32,21 45,29 37,36"/>',
    "lean-forward": chair(6, 24) + '<line x1="44" y1="34" x2="60" y2="34"/><line x1="52" y1="34" x2="52" y2="58"/><line x1="16" y1="38" x2="30" y2="20"/><circle cx="34" cy="14" r="6"/><polyline points="28,24 42,31"/><polyline points="16,38 32,38 32,56"/>',
    "leg-cross": chair(6, 24) + '<circle cx="18" cy="12" r="6"/><line x1="17" y1="18" x2="17" y2="38"/><polyline points="17,26 27,32"/><polyline points="17,38 36,40 36,58"/><polyline points="17,36 38,32 46,46"/>',
    # 体の動き
    "head-tilt": '<g transform="rotate(-18 32 34)"><circle cx="32" cy="34" r="18"/><circle cx="25" cy="31" r="2" fill="currentColor"/><circle cx="39" cy="31" r="2" fill="currentColor"/><path d="M26 41 Q32 45 38 41"/></g><path d="M18 10 Q30 2 42 8"/><polyline points="38,4 42,8 37,11"/>',
    "leg-jiggle": chair(10, 30) + '<circle cx="22" cy="12" r="6"/><line x1="21" y1="18" x2="21" y2="38"/><polyline points="21,38 42,38 42,54"/><path d="M48 42 q3 3 0 6"/><path d="M52 40 q5 5 0 10"/><path d="M36 54 q3 3 0 6" opacity=".6"/>',
    # 声・会話
    "voice-pitch": '<circle cx="22" cy="32" r="14"/><circle cx="26" cy="29" r="1.8" fill="currentColor"/><path d="M27 37 q4 1 6 -1"/><path d="M40 26 Q44 32 40 38"/><path d="M46 21 Q52 32 46 43"/><path d="M52 16 Q60 32 52 48"/>',
    "tempo": '<rect x="4" y="10" width="28" height="18" rx="5"/><polyline points="12,28 10,34 18,28"/><path d="M9 19 q3 -4 6 0 t6 0 t6 0"/><rect x="32" y="34" width="28" height="18" rx="5"/><polyline points="52,52 54,58 46,52"/><path d="M37 43 q3 -4 6 0 t6 0 t6 0"/>',
    "nodding": '<circle cx="28" cy="34" r="16"/><circle cx="22" cy="32" r="2" fill="currentColor"/><circle cx="34" cy="32" r="2" fill="currentColor"/><path d="M23 41 Q28 44 33 41"/>' + arrow(54, 18, 54, 50, both=True),
    # 連絡・行動
    "reply-speed": phone('<rect x="25" y="14" width="14" height="8" rx="3"/><rect x="25" y="26" width="10" height="6" rx="3"/>') + '<circle cx="47" cy="47" r="10" fill="var(--bg)"/><line x1="47" y1="47" x2="47" y2="41"/><line x1="47" y1="47" x2="51" y2="49"/>',
    "contact-frequency": phone('<line x1="25" y1="16" x2="39" y2="16"/><line x1="25" y1="25" x2="35" y2="25"/><line x1="25" y1="34" x2="30" y2="34"/>') + arrow(50, 14, 50, 40),
    "sns-avoid": phone(eye(32, 28, 8, 5, r=2) + '<line x1="24" y1="38" x2="40" y2="18"/>'),
    "silence": '<path d="M10 12 h44 a4 4 0 0 1 4 4 v22 a4 4 0 0 1 -4 4 h-30 l-10 10 v-10 h-4 a4 4 0 0 1 -4 -4 v-22 a4 4 0 0 1 4 -4z"/><circle cx="22" cy="27" r="2.5" fill="currentColor"/><circle cx="32" cy="27" r="2.5" fill="currentColor"/><circle cx="42" cy="27" r="2.5" fill="currentColor"/>',
    "stonewalling": '<circle cx="18" cy="32" r="13"/><line x1="12" y1="30" x2="16" y2="30"/><line x1="20" y1="30" x2="24" y2="30"/><line x1="14" y1="38" x2="22" y2="38"/><rect x="36" y="8" width="22" height="48"/><line x1="36" y1="20" x2="58" y2="20"/><line x1="36" y1="32" x2="58" y2="32"/><line x1="36" y1="44" x2="58" y2="44"/><line x1="47" y1="8" x2="47" y2="20"/><line x1="42" y1="20" x2="42" y2="32"/><line x1="52" y1="20" x2="52" y2="32"/><line x1="47" y1="32" x2="47" y2="44"/><line x1="42" y1="44" x2="42" y2="56"/><line x1="52" y1="44" x2="52" y2="56"/>',
    "play-hard-to-get": fig(14, 12) + fig(40, 12) + arrow(46, 34, 60, 34),
    "jealousy": '<rect x="18" y="30" width="28" height="24" rx="4"/><path d="M24 30 v-8 a8 8 0 0 1 16 0 v8"/><circle cx="32" cy="40" r="3" fill="currentColor"/><line x1="32" y1="43" x2="32" y2="48"/>',
    "love-bombing": '<rect x="6" y="30" width="28" height="20" rx="2"/><polyline points="6,30 20,42 34,30"/><rect x="18" y="18" width="28" height="20" rx="2" fill="var(--bg)"/><polyline points="18,18 32,30 46,18"/><rect x="30" y="6" width="28" height="20" rx="2" fill="var(--bg)"/><polyline points="30,6 44,18 58,6"/>',
    "no-apology": '<path d="M8 12 h48 a4 4 0 0 1 4 4 v22 a4 4 0 0 1 -4 4 h-32 l-10 10 v-10 h-6 a4 4 0 0 1 -4 -4 v-22 a4 4 0 0 1 4 -4z"/><text x="32" y="32" text-anchor="middle" font-size="12" fill="currentColor" stroke="none">ごめん</text><line x1="14" y1="34" x2="50" y2="20"/>',
    # 脈あり・嘘の通説(検索上位)
    "asks-questions": '<rect x="4" y="12" width="30" height="20" rx="5"/><polyline points="12,32 10,38 18,32"/><text x="19" y="27" text-anchor="middle" font-size="14" fill="currentColor" stroke="none">?</text><rect x="30" y="30" width="30" height="20" rx="5"/><polyline points="52,50 54,56 46,50"/><text x="45" y="45" text-anchor="middle" font-size="14" fill="currentColor" stroke="none">?</text>',
    "laughs-a-lot": FACE + '<path d="M20 28 q4 -5 8 0"/><path d="M36 28 q4 -5 8 0"/><path d="M20 36 Q32 52 44 36 Z"/><path d="M52 12 l4 -4"/><path d="M56 18 h5"/>',
    "self-disclosure": fig(14, 12) + fig(50, 12) + '<rect x="22" y="2" width="20" height="14" rx="4"/><line x1="26" y1="7" x2="38" y2="7"/><line x1="26" y1="11" x2="34" y2="11"/><polyline points="24,16 20,21 30,16"/>',
    "compliments": '<path d="M8 12 h44 a4 4 0 0 1 4 4 v20 a4 4 0 0 1 -4 4 h-28 l-10 10 v-10 h-6 a4 4 0 0 1 -4 -4 v-20 a4 4 0 0 1 4 -4z"/><path d="M30 18 l3 6 6 1 -4.5 4.5 1 6 -5.5 -3 -5.5 3 1 -6 -4.5 -4.5 6 -1z"/>',
    "blushing": FACE + '<circle cx="24" cy="27" r="2" fill="currentColor"/><circle cx="40" cy="27" r="2" fill="currentColor"/><path d="M26 41 Q32 45 38 41"/><line x1="15" y1="34" x2="19" y2="30"/><line x1="18" y1="36" x2="22" y2="32"/><line x1="42" y1="32" x2="46" y2="36"/><line x1="45" y1="30" x2="49" y2="34"/>',
    "teasing": fig(14, 12, '<polyline points="6,32 14,23"/><line x1="14" y1="23" x2="34" y2="18"/>') + fig(48, 14) + '<line x1="38" y1="12" x2="42" y2="8"/><line x1="40" y1="16" x2="45" y2="14"/>',
    "language-match": '<rect x="6" y="8" width="24" height="16" rx="4"/><line x1="11" y1="14" x2="25" y2="14"/><line x1="11" y1="19" x2="20" y2="19"/><rect x="34" y="40" width="24" height="16" rx="4"/><line x1="39" y1="46" x2="53" y2="46"/><line x1="39" y1="51" x2="48" y2="51"/><path d="M20 30 Q32 32 44 34" stroke-dasharray="2 3"/>' + arrow(40, 36, 44, 34),
    "eyes-up-right": eye(30, 36, 16, 9, 38, 31, 4) + arrow(44, 22, 56, 10) + '<text x="14" y="16" font-size="12" fill="currentColor" stroke="none">?</text>',
    "too-detailed": '<path d="M8 8 h48 a4 4 0 0 1 4 4 v28 a4 4 0 0 1 -4 4 h-30 l-10 10 v-10 h-8 a4 4 0 0 1 -4 -4 v-28 a4 4 0 0 1 4 -4z"/><line x1="14" y1="16" x2="50" y2="16"/><line x1="14" y1="22" x2="50" y2="22"/><line x1="14" y1="28" x2="50" y2="28"/><line x1="14" y1="34" x2="40" y2="34"/>',
    "nerves-visible": '<circle cx="28" cy="34" r="18"/><circle cx="22" cy="31" r="2" fill="currentColor"/><circle cx="34" cy="31" r="2" fill="currentColor"/><path d="M22 42 q3 -2 6 0 t6 0"/><path d="M48 10 q-3 5 0 7 q3 -2 0 -7z"/>' + eye(52, 40, 8, 5, r=2),
    # FBI系・通説の検証
    "honest-feet": '<ellipse cx="20" cy="40" rx="6" ry="12" transform="rotate(35 20 40)"/><ellipse cx="34" cy="44" rx="6" ry="12" transform="rotate(35 34 44)"/><rect x="46" y="6" width="14" height="24" rx="1"/><circle cx="56" cy="19" r="1.2" fill="currentColor"/>' + arrow(30, 24, 42, 14),
    "neck-touch": '<circle cx="32" cy="15" r="10"/><line x1="28" y1="25" x2="28" y2="34"/><line x1="36" y1="25" x2="36" y2="34"/><path d="M10 56 Q12 38 28 35 L36 35 Q52 38 54 56"/><ellipse cx="33" cy="38" rx="5" ry="7"/><line x1="37" y1="44" x2="44" y2="60"/>',
    "lip-compress": FACE + '<circle cx="24" cy="27" r="2" fill="currentColor"/><circle cx="40" cy="27" r="2" fill="currentColor"/><line x1="25" y1="41" x2="39" y2="41" stroke-width="4"/><line x1="22" y1="39" x2="20" y2="37"/><line x1="42" y1="39" x2="44" y2="37"/>',
    "steeple": '<path d="M30 12 C24 20 17 32 17 46 L21 58"/><path d="M34 12 C40 20 47 32 47 46 L43 58"/><path d="M30 12 Q32 9 34 12"/><line x1="30" y1="13" x2="27" y2="42"/><line x1="34" y1="13" x2="37" y2="42"/><path d="M17 46 Q22 50 27 42"/><path d="M47 46 Q42 50 37 42"/>',
    "torso-away": fig(16, 14) + '<circle cx="46" cy="14" r="5"/><circle cx="48.5" cy="13" r="1" fill="currentColor"/><line x1="46" y1="19" x2="46" y2="40"/><polyline points="43,56 46,40 49,56"/><line x1="46" y1="26" x2="53" y2="35"/>' + arrow(52, 60, 62, 60) + '<path d="M36 7 Q46 0 56 7"/><polyline points="52,3 56,7 51,10"/>',
    "eye-block": FACE + '<rect x="12" y="20" width="40" height="12" rx="6" fill="var(--bg)"/><line x1="18" y1="32" x2="16" y2="40"/><line x1="46" y1="32" x2="48" y2="40"/><line x1="27" y1="44" x2="37" y2="44"/>',
    "freeze": fig(24, 10, '<line x1="24" y1="18" x2="16" y2="34"/><line x1="24" y1="18" x2="32" y2="34"/>') + '<rect x="44" y="14" width="5" height="18" rx="1"/><rect x="54" y="14" width="5" height="18" rx="1"/>',
    "nose-touch": FACE + '<circle cx="24" cy="26" r="2" fill="currentColor"/><circle cx="40" cy="26" r="2" fill="currentColor"/><line x1="25" y1="44" x2="33" y2="44"/><circle cx="34" cy="34" r="3"/><line x1="36" y1="37" x2="46" y2="60" stroke-width="4"/>',
}


def svg(item_id):
    inner = ILL.get(item_id)
    if not inner:
        return ""
    return ('<span class="ill" aria-hidden="true"><svg viewBox="0 0 64 64" fill="none" stroke="currentColor" stroke-width="2.5" '
            f'stroke-linecap="round" stroke-linejoin="round">{inner}</svg></span>')
