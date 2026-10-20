"""お煎餅ラボの /flavor/（まだ世の中にない煎餅の味を探す）を media/senbei-pages.json に書き出す。
データ: media/senbei-flavors.json（市販の煎餅・米菓の味 839件、2026-10-20 時点。集め方はページ内に書く）
判定の根拠: 組み合わせの研究メモ（香り成分共有説 Ahn 2011 は採点に使わない）。点数化はしない。
実行: python3 media/senbei_flavor.py && python3 media/build.py senbei"""
import collections, html, json, re
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
DATE = "2026-10-20"
FL = json.loads((ROOT / "media/senbei-flavors.json").read_text())

# 土台（1つ選ぶ）: id, 表示名, 味名の要素（どれかが付いていれば土台が同じとみなす）, 系統タグ
BASES = [
    ("soy", "醤油", ["醤油"], ["G", "Na", "SOY"]),
    ("salt", "塩", ["塩"], ["Na"]),
    ("sugar", "砂糖・ざらめ", ["砂糖", "ざらめ", "黒糖"], ["S"]),
    ("amakara", "甘辛", ["みりん・甘辛"], ["S", "Na", "G", "SOY"]),
    ("miso", "味噌", ["味噌"], ["G", "Na"]),
]
# 足す味（系統ごと）: id, 表示名, 味名の要素, 系統タグ, 家で試すなら
G, I, NA, S, B, A, F, CIT, C, P, K, W, FAT, DA, M = "G I Na S B A F CIT C P K W FAT DA M".split()
ADDS = [
    ("果物", [
        ("ichigo", "いちご", ["いちご"], ["F1"], "フリーズドライのいちごを細かく砕き、焼いた後にまぶす"),
        ("ringo", "りんご", ["りんご"], [F], "乾燥りんごを細かく刻んでのせる。生の果汁は水分でしけやすい"),
        ("momo", "桃", ["桃"], [F], "桃のジャムをごく薄く塗り、低い温度で乾かす"),
        ("yonashi", "洋梨", ["洋梨"], [F], "洋梨のジャムをごく薄く塗り、低い温度で乾かす"),
        ("kaki", "柿", ["柿"], [F], "干し柿を細かく刻んでのせる"),
        ("budo", "ぶどう", ["ぶどう"], [F], "干しぶどうを刻むか、ぶどうのジャムをごく薄く塗る"),
        ("mango", "マンゴー", ["マンゴー"], [F], "ドライマンゴーを細かく刻んでのせる"),
    ]),
    ("柑橘・酸味", [
        ("lemon", "レモン", ["レモン"], [A, "F1", CIT], "レモンの皮を少しすりおろしてのせる"),
        ("yuzu", "柚子", ["柚子"], [A, F, CIT, W], "柚子の皮を少しすりおろしてのせる"),
        ("sudachi", "すだち・かぼす", ["すだち・かぼす・ライム"], [A, F, CIT], "皮を少しすりおろすか、果汁を1滴だけ落とす"),
        ("mikan", "みかん", ["みかん"], [F, CIT], "乾かしたみかんの皮を細かく刻んでのせる"),
        ("ume", "梅", ["梅"], [A], "梅肉を薄く塗るか、乾燥梅の粉をまぶす"),
    ]),
    ("うま味", [
        ("nori", "のり", ["のり", "青のり"], [G, W], "焼いた後に刻み海苔か青のりをのせる"),
        ("katsuo", "かつお", ["かつお"], [I, M], "削り節を指でもんで粉にし、焼いた後にまぶす"),
        ("konbu", "昆布", ["昆布・だし"], [G], "昆布茶の粉をごく少量まぶす"),
        ("cheese", "チーズ", ["チーズ"], [G, NA, FAT, DA, "Dy"], "粉チーズをのせて、焦がさない程度に軽くあぶる"),
        ("ebi", "えび", ["えび"], [M, W], "干しえびを細かく砕いてまぶす"),
        ("mentai", "明太子", ["明太子・たらこ"], [NA, M], "明太子を薄く塗り、中まで火が通るように軽くあぶる"),
        ("tomato", "トマト", ["トマト"], [G, A], "トマトペーストをごく薄く塗って乾かす"),
    ]),
    ("香り・辛味", [
        ("wasabi", "わさび", ["わさび"], [P, K], "練りわさびをほんの少し醤油や水で溶いて塗る。少なめから"),
        ("sansho", "山椒", ["山椒"], [P, W], "粉山椒をひとつまみ、焼いた後にふる"),
        ("togarashi", "唐辛子", ["唐辛子・辛口", "七味"], [C], "一味唐辛子を少しずつふる"),
        ("kosho", "黒こしょう", ["黒こしょう"], [P], "粗びきの黒こしょうを焼いた後にふる"),
        ("goma", "ごま", ["ごま"], [FAT, W], "炒りごまを生地にのせて焼くか、焼いた後に貼りつける"),
        ("shiso", "しそ", ["しそ"], [W], "乾燥しその粉をまぶす"),
        ("ninniku", "にんにく", ["にんにく"], [P, K], "にんにくの粉をごく少量まぶす"),
        ("curry", "カレー", ["カレー"], [C, K], "カレー粉をごく少量まぶす"),
    ]),
    ("甘い・乳", [
        ("butter", "バター", ["バター"], [FAT, "Dy"], "焼いた後に溶かしバターを薄く塗る"),
        ("milk", "ミルク", ["ミルク"], [DA, "Dy"], "練乳を薄く塗って乾かす"),
        ("choco", "チョコ", ["チョコ"], [S, B], "溶かしたチョコを片面に薄く塗って冷やす"),
        ("matcha", "抹茶", ["抹茶"], [B, W], "抹茶を茶こしで薄くふる"),
        ("kinako", "きなこ", ["きなこ"], [W], "きなこを茶こしで薄くふる"),
        ("honey", "はちみつ", ["はちみつ"], [S], "はちみつを薄く塗る（1歳未満の子には与えない）"),
    ]),
]
ADD = {a[0]: a for _, xs in ADDS for a in xs}
BASE = {b[0]: b for b in BASES}

# 論文の出典（DOI は研究メモで書誌を確かめたもの）
SRC = {
    "yam": ("Yamaguchi 1967", "https://doi.org/10.1111/j.1365-2621.1967.tb09715.x"),
    "kur": ("Kurihara 2015（総説）", "https://doi.org/10.1155/2015/189402"),
    "bre": ("Breslin・Beauchamp 1995", "https://doi.org/10.1093/chemse/20.6.609"),
    "kea": ("Keast ほか 2004", "https://doi.org/10.1093/chemse/bjh045"),
    "mao": ("Mao ほか 2022", "https://doi.org/10.1038/s41538-022-00148-0"),
    "sch": ("Schifferstein・Verlegh 1996", "https://doi.org/10.1016/0001-6918(95)00040-2"),
    "nas": ("Nasrawi・Pangborn 1990", "https://doi.org/10.1016/0031-9384(90)90067-E"),
    "gai": ("Gaiser・Hayes 2023", "https://doi.org/10.1016/j.foodqual.2023.105041"),
    "lap": ("Lapid ほか 2008", "https://doi.org/10.1093/chemse/bjn026"),
    "ma": ("Ma ほか 2020", "https://doi.org/10.1093/chemse/bjaa020"),
    "pli": ("Pliner・Stallberg-White 2000", "https://doi.org/10.1006/appe.1999.0290"),
    "hek": ("Hekkert ほか 2003", "https://doi.org/10.1348/000712603762842147"),
    "spe": ("Spence 2020", "https://doi.org/10.1016/j.foodres.2020.109124"),
    "ahn": ("Ahn ほか 2011", "https://doi.org/10.1038/srep00196"),
}
# 組み合わせの判定: [系統a, 系統b, 根拠, 理由, 出典, 条件]。r=似た研究あり（その成分の組み合わせを人で調べた水溶液などの研究） e=推定 u=まだわからない。
# 最後の印: n=合いにくい方向（全体の「受け入れられやすい」を出さない・おまかせから外す） x=おまかせから外す
# 条件: "nb:X" = b側に X がない、"ni" = どちらにもかつお系(I)がない、"same" = a と b が同じ系統
RULES = [
    [G, I, "r", "グルタミン酸とイノシン酸を混ぜた水溶液で、うま味が強まる相乗効果が人で確かめられている。昆布・醤油・のりなどがグルタミン酸寄り、かつお節がイノシン酸寄りという食材の分け方は推定", ["yam", "kur"], "", ""],
    [S, A, "r", "砂糖とクエン酸の水溶液で、甘味と酸味が互いを感じにくくした（強さの研究で、好まれるかは別）", ["mao"], "", ""],
    [S, "F1", "r", "砂糖水にいちご・レモンの香りを添えると、甘味が強まり快く感じた（溶液の研究）", ["sch"], "", ""],
    [NA, B, "e", "塩は、尿素・キニーネなどの苦味の水溶液で多くの苦味を抑えた。抹茶やチョコの苦味で確かめた研究ではない", ["bre"], "", ""],
    [C, S, "e", "唐辛子の辛さのあとに砂糖水で口をすすぐと、辛さが和らいだ。一緒に食べたときの研究ではない", ["nas"], "", ""],
    [S, F, "e", "砂糖水にいちご・レモンの香りを添えると快く感じた研究からの類推。この果物で調べた研究ではない", ["sch"], "", ""],
    [K, W, "e", "2種類の香りを混ぜると、快さは強い方の香りに引っ張られた（香りだけの研究）。合うかどうかではなく、強い方が目立ちやすいという目安", ["lap", "ma"], "", ""],
    [S, M, "e", "砂糖水になじまない香り（ハム）を足すと快さが下がった研究からの類推で、甘さと魚介は合いにくい方向", ["sch"], "", "n"],
    [S, B, "e", "甘味で苦味が和らぐと考えられる（砂糖を苦味を抑える物として試した研究はあるが、結果は要旨で確かめられていない）", ["kea"], "", ""],
    [C, DA, "e", "唐辛子の辛さのあと、乳のたんぱく質を含む飲み物で辛さが和らいだ（牛乳などの飲み物の研究）", ["gai"], "", ""],
    [C, FAT, "e", "脂だけで辛さを和らげる効果は限られる（脂肪0%と10%の加糖乳で差がなかった）", ["nas", "gai"], "nb:DA", "n"],
    [S, NA, "u", "甘じょっぱい組み合わせは昔からなじみがあるが、好まれることを人で調べた研究は見つからなかった", [], "", ""],
    [CIT, CIT, "e", "香りの好ましさが近いものどうしは、少し上乗せされることがある（222組のうち6組だけ）", ["ma"], "same", "x"],
    ["SOY", "Dy", "u", "醤油とバター・チーズ・乳の相性を、人が味わって調べた研究は見つからなかった", [], "", ""],
    ["SOY", CIT, "u", "醤油と柑橘の相性を、人が味わって調べた研究は見つからなかった", [], "", ""],
    [P, "*", "u", "わさび・山椒・黒こしょう・にんにくの刺激は唐辛子と成分が違い、組み合わせの研究は見つからなかった", [], "", ""],
    [G, G, "u", "どちらもグルタミン酸が中心（という分け方は推定）で、うま味の相乗効果の根拠にはならない", [], "same,ni", ""],
]
NOVEL = {1: ["e", "なじみの土台に新しい味を1つ足す形は、受け入れられやすいと考えられる（子どもの試食意向と工業デザインの研究からの類推で、食べておいしいかを調べた研究ではない）", ["pli", "hek"]],
         2: ["u", "新しい味を2つ重ねたときに受け入れられやすいかは、研究が見つからなかった", []]}
LBL = {"r": "似た研究あり（水溶液など）", "e": "推定", "u": "まだわからない"}


def tags(k):
    return set(BASE[k][3]) if k in BASE else set(ADD[k][3])


def judge(x, y):
    """2つの要素の組み合わせの見立て（JS の judge と同じ）"""
    X, Y = tags(x), tags(y)
    out = []
    for a, b, l, t, s, cond, flag in RULES:
        cs = cond.split(",") if cond else []
        for P1, P2 in ((X, Y), (Y, X)):
            if a not in P1 or (b != "*" and b not in P2):
                continue
            if "same" in cs and a != b:
                continue
            if "ni" in cs and (I in P1 or I in P2):
                continue
            nb = [c[3:] for c in cs if c.startswith("nb:")]
            if nb and nb[0] in P2:
                continue
            out.append([l, t, s, flag])
            break
    out.sort(key=lambda r: "reu".index(r[0]))
    return out[:2] or [["u", "この2つの組み合わせを、人が味わって調べた研究は見つからなかった", [], ""]]


# ---- データ（必要な列だけに絞る） ----
EL = {}  # 要素 → チップ/土台のid
for b in BASES:
    for e in b[2]:
        EL.setdefault(e, []).append(b[0])
for a in ADD.values():
    for e in a[2]:
        EL.setdefault(e, []).append(a[0])
KEYS = [b[0] for b in BASES] + list(ADD)
KI = {k: i for i, k in enumerate(KEYS)}
add_ids = set(ADD)
pref, urls, makers, prods, rows = [], [], [], [], []


def item_keys(x):
    ks = set()
    for e in x["elements"]:
        ks.update(EL.get(e, []))
    if "醤油" in x["elements"] and ({"砂糖", "ざらめ", "黒糖"} & set(x["elements"])):
        ks.add("amakara")  # 醤油＋砂糖も甘辛に数える
    return ks


for x in FL:
    ks = item_keys(x)
    if not ks & add_ids:
        continue  # 足す味が1つもない味は、どの検索にも当たらない
    if x["maker"] not in makers:
        makers.append(x["maker"])
    if urlparse(x["source"]).netloc == "item.rakuten.co.jp":
        src = 0  # 購入ページなのでリンクしない
    else:
        full = unquote(x["source"])  # 日本語のURLは元の文字に戻して軽くする（ブラウザが送るときに符号化し直す）
        cut = full.rstrip("/").rfind("/") + 1
        pre, rest = full[:cut], full[cut:]
        if pre not in pref:
            pref.append(pre)
        if [pref.index(pre), rest] not in urls:
            urls.append([pref.index(pre), rest])
        src = urls.index([pref.index(pre), rest]) + 1
    m = re.search(r"kamedaseika\.co\.jp/news/(20\d\d)", x["source"])
    yr = int(m.group(1)) - 2000 if m else (-1 if re.search(r"/products?/|lineup|/shop/", x["source"]) and "rakuten" not in x["source"] else 0)  # 西暦の下2桁、-1=商品ページに掲載、0=不明
    if x["product"] not in prods:
        prods.append(x["product"])
    name = [prods.index(x["product"]), "" if x["flavor"] in x["product"] else x["flavor"]]
    rows.append([makers.index(x["maker"]), name, sorted(KI[k] for k in ks), 1 if x["limited"] else 0, src, yr])


def find(base, adds):
    exact, near = [], []
    for x in FL:
        ks = item_keys(x)
        if all(a in ks for a in adds):
            (exact if base in ks else near).append(x)
    return exact, near


# ---- 調べてわかったこと（表） ----
cnt = collections.Counter(e for x in FL for e in x["elements"])
dom = collections.Counter(urlparse(x["source"]).netloc for x in FL)
lim = sum(x["limited"] for x in FL)
top = cnt.most_common(12)
FRUIT_ROWS = [("いちご", "22件。ほとんどがチョコ・ミルク・クリームと組んだ甘い味。醤油・塩・えびと組んだものは見つからなかった"),
              ("りんご", "7件"), ("ぶどう", "4件（巨峰・山ぶどう・ラムレーズン）"), ("マンゴー", "3件"),
              ("桃", "1件だけ（2014年の期間限定品）。福島・山梨・岡山の土産の桃煎餅も見つからなかった"),
              ("メロン・バナナ・パイン・さくらんぼ・栗", "各1件"), ("洋梨（ラ・フランス）・梨・柿・スイカ", "0件（「柿の種」は柿の味ではない）"),
              ("レモン・柚子", "レモン34件・柚子31件で、もう定番")]
for k, v in [("いちご", 22), ("りんご", 7), ("ぶどう", 4), ("マンゴー", 3), ("桃", 1)]:
    assert cnt[k] == v, (k, cnt[k])
assert len(FL) == 839 and cnt["レモン"] == 34 and cnt["柚子"] == 31 and cnt["洋梨"] == 0 and cnt["柿"] == 0

# ---- 入力例 ----
EXAMPLES = [("soy", ["katsuo"]), ("salt", ["lemon"]), ("salt", ["ichigo", "sansho"]), ("sugar", ["yonashi", "matcha"]), ("soy", ["butter"]), ("amakara", ["sansho", "cheese"])]


def ex_row(b, adds):
    ex, nr = find(b, adds)
    n = len(ex) + len(nr)
    name = BASE[b][1] + "＋" + "＋".join(ADD[a][1] for a in adds)
    have = (f"{n}件（うち味名に{BASE[b][1]}もあるもの{len(ex)}件）" if n else "出てこなかった")
    ps = [b] + adds
    js = []
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            r = judge(ps[i], ps[j])[0]
            nm = lambda k: BASE[k][1] if k in BASE else ADD[k][1]  # noqa: E731
            js.append(f"{nm(ps[i])}×{nm(ps[j])}: {LBL[r[0]]}")
    return f"<tr><td>{E(name)}</td><td>{E(have)}</td><td>{E(' / '.join(js))}</td></tr>"


def chip(name, typ, v, label, checked=False):
    return f'<label class="sc"><input type="{typ}" name="{name}" value="{v}"{" checked" if checked else ""}><span>{E(label)}</span></label>'


FAQ = [
    ("ここで「見つからなかった」味は、世の中にまだない味？", "そうとは言い切れません。SEADICEが2026年10月20日までに、米菓メーカーの公式ニュース・商品ページ、PR TIMES、楽天市場（補助）で集めた839件の中に無い、というだけです。ぼんち・天乃屋などは公式サイトを読めず、亀田製菓の2007年より前、地域限定品も一部しか入っていません。"),
    ("「合いそうか」はどうやって決めている？", "味どうしの作用（うま味の相乗・塩で苦味が抑えられる・甘味で辛さが和らぐ・甘味と酸味が互いを弱めるなど）を人で調べた研究だけを使い、「似た研究あり（水溶液など）」「推定」「まだわからない」の3つで示します。「似た研究あり」は、その成分の組み合わせ（例: グルタミン酸×イノシン酸）を人で調べた研究があるときだけです。研究はほとんどが水溶液・スープ・飲み物で、焼いた煎餅で確かめた研究は見つかっていません。点数はつけません。"),
    ("香りの成分が似ている食材どうしは合う、という説は使わない？", "使いません。Ahn ほか（2011）はレシピに一緒に載るかを数えた統計で、人がおいしいと評価したデータではなく、東アジアの料理ではむしろ共有の少ない組み合わせが多いと報告しています。Spence（2020）の総説も、この説は信用を失ったと整理しています。"),
    ("試したい味や「合った・合わなかった」は、どこかに送られる？", "送られません。この端末のブラウザ（localStorage）にだけ保存されます。登録もいりません。消したいときは一覧の「消す」を押してください。"),
]

head = '<script type="application/ld+json">' + json.dumps({"@context": "https://schema.org", "@graph": [
    {"@type": "WebApplication", "name": "まだない煎餅の味を探す", "url": "https://senbei.seadice.win/flavor/", "applicationCategory": "UtilitiesApplication",
     "operatingSystem": "Any", "browserRequirements": "JavaScript", "isAccessibleForFree": True, "inLanguage": "ja",
     "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"}, "dateModified": DATE,
     "description": "土台の味（醤油・塩・砂糖・甘辛・味噌）と足す味を選ぶと、SEADICEが調べた市販の煎餅・米菓839件の味にその組み合わせがあるかと、合いそうかを研究の根拠つきで出す無料ツール。",
     "publisher": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}},
    {"@type": "Dataset", "name": "市販の煎餅・米菓の味 839件（2026年10月20日時点）", "url": "https://senbei.seadice.win/flavor/#data",
     "description": "米菓メーカー14の出典（公式ニュース・商品ページ、PR TIMES、楽天市場は補助）から、商品×味を1件として集め、味名に書かれた要素を付けた一覧。", "dateModified": DATE,
     "creator": {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE"}},
    {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]},
    ensure_ascii=False) + "</script>"

form = ('<form class="sd-tool" id="sbf" onsubmit="return false" aria-label="煎餅の味の組み合わせを選ぶ">'
        '<fieldset class="sg"><legend>1. 土台の味を1つ</legend><div class="scs">'
        + "".join(chip("base", "radio", b[0], b[1], b[0] == "soy") for b in BASES) + '</div></fieldset>'
        '<fieldset class="sg"><legend>2. 足す味を1つか2つ</legend>'
        + "".join(f'<p class="gl">{E(g)}</p><div class="scs">' + "".join(chip("add", "checkbox", a[0], a[1]) for a in xs) + '</div>' for g, xs in ADDS)
        + '<p class="hint" id="hint">3つ目を選ぶと、先に選んだ方が外れます。おまかせは、足す味2つの組み合わせが839件の味名に無く、研究と食い違わないものから選びます（美味しいとは限りません）。</p></fieldset>'
        '<div class="btns"><button type="button" class="bt bt1" id="omakase">おまかせ: 839件にない組み合わせを1つ出す</button>'
        '<button type="button" class="bt" id="clr">足す味を外す</button></div></form>')

res = ('<section class="res" aria-live="polite" aria-label="結果"><h2 class="resh" id="rt">足す味を選んでください</h2>'
       '<p class="saved" id="omk" hidden></p><div class="ri"><p class="rn">839件の味名にあるか</p><div id="r1"><p class="rw">土台と足す味を選ぶと、SEADICEが調べた市販の煎餅・米菓839件の味の中に、同じ組み合わせがあるかを出します。</p></div></div>'
       '<div class="ri"><p class="rn">合いそうか（研究から）</p><div id="r2"><p class="rw">-</p></div></div>'
       '<div class="ri"><p class="rn">試すなら</p><div id="r3"><p class="rw">-</p></div></div>'
       '<button type="button" class="bt bt1" id="save" disabled>この味を「試したい味」に入れる</button><p class="saved" id="savedmsg" hidden></p>'
       '<p class="disc">「似た研究あり」も、水溶液・スープ・飲み物での研究です。焼いた煎餅で確かめた研究は見つかっていません。味を保証するものではありません。商品名は「ある・ない」を示すためで、勧めるものではありません。</p></section>')

mylist = ('<section class="my" id="my" aria-labelledby="myh"><h2 class="sec2" id="myh">試したい味（この端末だけに保存）</h2>'
          '<p class="t2">試したら「合った」「合わなかった」を1回押して残せます。登録はいらず、どこにも送られません。</p>'
          '<ul class="myl" id="myl"></ul><p class="t2" id="myempty">まだありません。結果の下の「試したい味に入れる」で足せます。</p>'
          '<details class="exp"><summary>一覧を文字で書き出す（メモ帳に貼れます）</summary><textarea id="myout" readonly rows="5" aria-label="書き出した一覧"></textarea></details></section>')

answer = ('<p class="answer2"><b>先に結論:</b> SEADICEが集めた市販の煎餅・米菓839件の味（2026年10月20日時点）では、果物の味は少なく、桃は1件、洋梨・梨・柿は0件でした。'
          '成分の組み合わせを人で調べた研究があるのは、うま味の相乗（グルタミン酸×イノシン酸）、甘味と酸味が互いを弱める、砂糖水にいちご・レモンの香り、などで、どれも水溶液での研究です。煎餅で確かめた研究は見つかっていません。</p>')

findings = ('<h2 class="sec2" id="data">調べてわかったこと（839件の味）</h2>'
            f'<p class="t2">1件は「1つの商品×1つの味」です（袋の大きさ違い・包装違い・再発売はまとめました）。うち{lim}件が期間限定・地域限定・店舗限定です。味名に書かれた言葉から「要素」を付けて数えました。</p>'
            '<div class="tblwrap"><table class="tbl"><thead><tr><th>よく出る要素</th><th>件数</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{E(k)}</td><td>{v}</td></tr>" for k, v in top)
            + '</tbody></table></div><p class="tblnote">醤油・塩は、味名に書かれていない定番品が多いので、実際より少なく数えています（例: 「濃い海苔味」は のり だけを数えた）。</p>'
            '<div class="tblwrap"><table class="tbl"><thead><tr><th>果物</th><th>839件の中で</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{E(k)}</td><td>{E(v)}</td></tr>" for k, v in FRUIT_ROWS)
            + '</tbody></table></div>'
            '<h3 class="h3">どう集めたか</h3><ul class="srcl">'
            '<li>米菓メーカーの公式ニュース・商品ページ: 亀田製菓（2007〜2026年のニュース見出し 約700件）、栗山米菓（2020年〜 約230件）、岩塚製菓（2023年〜 約130件）、三幸製菓・越後製菓（ニュース一覧と商品ページを全件）など</li>'
            '<li>PR TIMES の発表と、公式ページが見つからない土産煎餅・果物味・酒粕を補うための楽天市場（補助の出典。購入ページなので、このページからはリンクしていません）</li>'
            '<li>果物は重点的に探しました。使った検索語は、たとえば桃なら「桃 せんべい」「白桃 おかき」「もも あられ」「ピーチ せんべい」、洋梨なら「ラ・フランス せんべい」「洋梨 せんべい」、柿なら「干し柿 せんべい」「柿味 おかき」など（楽天市場・PR TIMES・Web検索、岡山県のアンテナショップの通販も「白桃」「桃」で全件）</li></ul>'
            '<div class="tblwrap"><table class="tbl"><thead><tr><th>出典</th><th>件数</th></tr></thead><tbody>'
            + "".join(f"<tr><td>{E(k)}{'（補助）' if k == 'item.rakuten.co.jp' else ''}</td><td>{v}</td></tr>" for k, v in dom.most_common())
            + '</tbody></table></div>'
            '<h3 class="h3">データの限界（漏れていそうな所）</h3><ul class="srcl">'
            '<li>ぼんち・天乃屋（歌舞伎揚）は公式サイトを読めず、PR TIMES と楽天市場の分だけ。歴代の期間限定味はもっと多いはずです</li>'
            '<li>小倉山荘・播磨屋本店・九十九島せんべい本舗・坂角総本舗は、サイトにつながらず調べていません</li>'
            '<li>亀田製菓の2007年より前、栗山米菓の2020年より前、岩塚製菓・三幸製菓の2023年より前は、ニュース一覧がなく入っていません</li>'
            '<li>ご当地限定品（各地のご当地味など）は一部だけ。ギフトの箱の中の全種類も入っていません</li>'
            '<li>南部せんべい・瓦せんべい・炭酸せんべいなど小麦の煎餅や、えびせんべいも含みます</li></ul>')

method = ('<h2 class="sec2">「合いそうか」の考え方</h2>'
          '<p class="t2">選んだ味を2つずつ組にして、味どうしの作用を人で調べた研究があるかを見ます。Spence（2020）の整理にならい、「文化としてのなじみ」と「味どうしの作用（抑える・強める）」で考え、点数はつけません。'
          '香りの成分を多く共有する食材ほど合う、という説（Ahn ほか 2011）は、レシピの統計で人の評価ではないため使いません。</p>'
          '<div class="tblwrap"><table class="tbl"><thead><tr><th>組み合わせ</th><th>見立て</th><th>出典</th></tr></thead><tbody>'
          + "".join(f'<tr><td>{E(name)}</td><td>{LBL[r[2]]}: {E(r[3])}{"（合いにくい方向）" if r[6] == "n" else ""}</td><td>{"、".join(E(SRC[s][0]) for s in r[4]) or "-"}</td></tr>'
                    for name, r in zip(["うま味（醤油・昆布・のり・チーズ）×かつお", "甘味×酸味（梅・柑橘）", "甘味×いちご・レモンの香り", "塩・醤油×苦味（抹茶・チョコ）", "唐辛子×甘味", "甘味×ほかの果物の香り",
                                        "強い香り（カレー・にんにく・わさび）×ほかの香り", "甘味×魚介（えび・かつお・明太子）", "甘味×苦味", "唐辛子×乳（チーズ・ミルク）", "唐辛子×脂（バター・ごま）",
                                        "甘味×塩味（甘じょっぱい）", "柑橘×柑橘", "醤油×バター・チーズ・ミルク", "醤油×柑橘", "わさび・山椒・黒こしょう・にんにく×何か", "うま味×うま味（どちらもグルタミン酸）"], RULES))
          + f'<tr><td>なじみの土台＋新しい味1つ</td><td>推定: {E(NOVEL[1][1])}。合いにくい方向の見立てが1つでもあるときは出しません</td><td>Pliner・Stallberg-White 2000、Hekkert ほか 2003</td></tr>'
          + f'<tr><td>新しい味を2つ重ねる</td><td>まだわからない: {E(NOVEL[2][1])}</td><td>-</td></tr>'
          '</tbody></table></div>'
          '<p class="t2">食材をうま味系・酸味系などに分けるのは、一般的な食品の性質による推定です（含まれる成分の量は確かめていません）。うま味の相乗効果のくわしい説明は'
          '<a href="/umami-synergy-nori-senbei/">醤油煎餅に海苔や昆布が合うのはなぜ？</a>にあります。</p>'
          '<h2 class="sec2">入力例と結果</h2><div class="tblwrap"><table class="tbl"><thead><tr><th>組み合わせ</th><th>足す味の組み合わせが839件の味名に</th><th>合いそうか（組ごと）</th></tr></thead><tbody>'
          + "".join(ex_row(b, a) for b, a in EXAMPLES) + '</tbody></table></div>')

srcs = ('<h2 class="sec2">出典</h2><ul class="srcl">'
        + "".join(f'<li>{E(v[0])} <a href="{v[1]}" target="_blank" rel="noopener">{v[1][16:]}</a></li>' for v in SRC.values())
        + '<li>市販の味のデータ: 各メーカーの公式サイト・PR TIMES（各件の出典はツールの結果に表示）、楽天市場（補助、リンクなし）。調べた日 2026年10月20日</li></ul>')

faq = '<h2 class="sec2">よくある質問</h2>' + "".join(f'<details{" open" if i == 0 else ""}><summary>{E(q)}</summary><p>{E(a)}</p></details>' for i, (q, a) in enumerate(FAQ))
foot = ('<p class="rfoot">煎餅の膨らみや硬さの目安は<a href="/tool/">煎餅の組み合わせツール</a>、研究の全体は<a href="/research/">研究一覧</a>にあります。</p>'
        f'<p class="sd-updated">最終更新: 2026年10月20日（味のデータは2026年10月20日時点）</p>')

lead = ('<p class="xlead">土台の味と、足す味を1つか2つ選ぶと、SEADICEが調べた市販の煎餅・米菓839件の味にその組み合わせがあるか、合いそうかを研究の根拠つきで出します。'
        '気になった味は「試したい味」としてこの端末に残せます。</p>')

data = {"K": KEYS, "N": {k: (BASE[k][1] if k in BASE else ADD[k][1]) for k in KEYS}, "T": {k: sorted(tags(k)) for k in KEYS},
        "H": {k: ADD[k][4] for k in ADD}, "R": RULES, "V": NOVEL, "S": {k: list(v) for k, v in SRC.items()},
        "M": makers, "Q": prods, "P": pref, "U": urls, "D": rows}
JS = (open(ROOT / "media/senbei_flavor.js").read())
script = "<script>(function(){var Z=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";" + JS + "})();</script>"

CSS = (".tl{margin:8px 0 28px}.sd-tool{background:var(--card);border:1px solid var(--text);border-radius:8px;padding:16px}.sg{border:0;margin:0 0 14px;padding:0;min-width:0}"
       ".sg legend{font-size:15px;font-weight:800;margin-bottom:6px}.gl{font-size:13px;font-weight:700;color:var(--muted);margin:12px 0 6px}"
       ".scs{display:flex;flex-wrap:wrap;gap:8px}.sc{position:relative}.sc input{position:absolute;opacity:0;width:1px;height:1px}"
       ".sc span{display:inline-flex;align-items:center;min-height:48px;padding:0 14px;border:1px solid var(--muted);border-radius:6px;font-size:15px;background:var(--bg);cursor:pointer}"
       ".sc input:checked+span{background:#8A4512;border-color:#8A4512;color:#FFFCF4;font-weight:800;box-shadow:inset 0 0 0 2px #FFFCF4}"
       ".sc input:checked+span::before{content:'';display:inline-block;width:6px;height:11px;border:solid #FFFCF4;border-width:0 2px 2px 0;transform:rotate(45deg);margin:-3px 9px 0 0}"
       ".sc input:focus-visible+span,.bt:focus-visible{outline:2px solid #8A4512;outline-offset:2px}"
       ".hint{font-size:13px;color:var(--muted);margin:8px 0 0}.btns{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}"
       ".bt{min-height:48px;padding:0 16px;border:1px solid #1D2620;border-radius:6px;background:var(--bg);color:var(--text);font-size:15px;font-weight:700;cursor:pointer;font-family:inherit}"
       ".bt1{background:#1D2620;color:#F5EFE1}.bt:disabled{opacity:.5;cursor:default}"
       ".res{margin-top:16px;background:var(--card);border:1px solid var(--border);border-top:4px solid #C98A2B;border-radius:8px;padding:16px}"
       ".resh{font-size:18px;margin:0 0 6px;font-family:'Hiragino Mincho ProN','Yu Mincho',serif}.ri{padding:12px 0;border-top:1px solid var(--border)}.ri:first-of-type{border-top:0}"
       ".rn{font-size:13px;color:var(--muted);font-weight:700;margin:0 0 4px}.rw{font-size:14px;line-height:1.75;margin:4px 0}.rw a,.exl a{color:var(--link)}"
       ".big{font-size:16px;font-weight:800;margin:2px 0 4px}.exl{list-style:none;margin:6px 0;padding:0}.exl li{font-size:14px;line-height:1.7;padding:6px 0 6px 10px;border-left:3px solid #C98A2B;margin:6px 0}"
       ".exl small{display:block;font-size:12px;color:var(--muted)}"
       ".pj{margin:8px 0;padding:8px 0 0;border-top:1px dashed var(--border)}.pj:first-child{border-top:0;padding-top:0}.pjn{font-size:14px;font-weight:800;margin:0}"
       ".bs{display:inline-block;font-size:12px;font-weight:700;border:1px solid currentColor;border-radius:4px;padding:0 6px;margin-right:6px;background:var(--card)}"
       ".b-r{color:#8A4512}.b-e{color:#5C4636;border-style:dashed}.b-u{color:#36535E;border-style:dotted}"
       ".saved{font-size:14px;margin:8px 0 0;font-weight:700}.disc{margin-top:12px;font-size:13px;color:var(--muted);line-height:1.75}"
       ".answer2{font-size:15px;line-height:1.85;margin:0 0 24px;padding:12px 16px;background:#EFE5D0;border-left:4px solid #8A4512}"
       ".sec2{font-size:20px;margin:44px 0 10px;padding-top:12px;border-top:2px solid var(--text)}.h3{font-size:16px;margin:24px 0 8px}"
       ".t2{font-size:15px;line-height:1.85;margin:10px 0}.t2 a,.srcl a,.rfoot a{color:var(--link)}"
       ".tbl{width:100%;border-collapse:collapse;margin:12px 0 6px;font-size:14px;background:var(--card)}.tbl th,.tbl td{border:1px solid var(--border);padding:8px 10px;text-align:left;vertical-align:top;line-height:1.7}"
       ".tbl th{background:#EFE5D0}.tblwrap{overflow-x:auto}.tblnote{font-size:12px;color:var(--muted)}.srcl li{margin:8px 0 8px 20px;font-size:14px;line-height:1.75;word-break:break-word}"
       ".rfoot{margin-top:32px;font-size:14px}.sd-updated{font-size:13px;color:var(--muted)}"
       "details{background:var(--card);border:1px solid var(--border);border-radius:8px;margin:10px 0}details summary{cursor:pointer;padding:14px 18px;font-weight:700;font-size:15px}"
       "details p{padding:0 18px 16px;font-size:14px;line-height:1.8}"
       ".myl{list-style:none;margin:8px 0;padding:0}.myl li{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:12px;margin:10px 0}"
       ".myn{font-size:16px;font-weight:800;margin:0}.myd{font-size:12px;color:var(--muted);margin:2px 0 8px}.myb{display:flex;flex-wrap:wrap;gap:6px}"
       ".myb .bt{min-height:48px;font-size:14px;padding:0 12px}.myb .bt[aria-pressed=true]{background:#8A4512;border-color:#8A4512;color:#FFFCF4}.myb .del{margin-left:auto;border-color:var(--muted);font-weight:400}"
       ".exp textarea{display:block;width:calc(100% - 36px);margin:0 18px 16px;font-size:14px;padding:8px;border:1px solid var(--border);border-radius:6px;background:var(--bg);color:var(--text)}"
       "@media(min-width:600px){.res{padding:20px}}"
       "@media(min-width:960px){.tl{display:grid;grid-template-columns:1fr 1fr;gap:20px;align-items:start}.res{margin-top:0;position:sticky;top:16px;max-height:calc(100vh - 32px);overflow:auto}}")

body = (lead + '<div class="tl">' + form + '<noscript><p class="t2">このツールはJavaScriptで動きます。下の「調べてわかったこと」と「合いそうかの考え方」の表は、そのまま読めます。</p></noscript>'
        + res + '</div>' + mylist + answer + findings + method + srcs + faq + foot + script)

page = {"path": "flavor", "title": "まだない煎餅の味を探す", "seo_title": "まだない煎餅の味を探す（市販839件の味と組み合わせの研究で確かめる）",
        "date": DATE,
        "desc": "土台（醤油・塩・砂糖・甘辛・味噌）と足す味を選ぶと、SEADICEが調べた市販の煎餅・米菓839件の味にあるかと、合いそうかを研究の根拠つきで表示。桃は1件、洋梨・柿は0件。無料・登録不要・送信なし。",
        "body": body, "css": CSS, "head": head}

if __name__ == "__main__":
    pf = ROOT / "media/senbei-pages.json"
    ps = [p for p in json.loads(pf.read_text()) if p["path"] != "flavor"] + [page]
    pf.write_text(json.dumps(ps, ensure_ascii=False, indent=1) + "\n")
    sz = len(script.encode())
    print(f"flavor: {len(rows)} rows embedded, script {sz/1024:.1f} KB, body {len(body.encode())/1024:.1f} KB")
