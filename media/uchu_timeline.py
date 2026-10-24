#!/usr/bin/env python3
"""宇宙の研究の道具「宇宙の年表」(sites/uchu/timeline/index.html) を書き出す。
バーを動かすと、その時刻の宇宙の年齢・温度・大きさ（シミュレーターと同じフリードマン方程式・Planck 2018 の値）と、
そのころ起きたと考えられていることを、確かさの札つきで出す。記事の題名は media/uchu-posts.json から取り、無い記事へのリンクは出さない。
使い方: python3 media/uchu_timeline.py （できごと・出典を直したら実行して、build.py uchu も実行する）"""
import html, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "sites/uchu/timeline/index.html"
URL = "https://uchu.seadice.win/timeline/"
E = html.escape

SRC = {  # key: (表示, DOI か URL)
    "P": ("Planck Collaboration (2020). Planck 2018 results. VI. Cosmological parameters. <i>Astronomy &amp; Astrophysics</i>, 641, A6.", "https://doi.org/10.1051/0004-6361/201833910"),
    "Fx": ("Fixsen, D. J. (2009). The Temperature of the Cosmic Microwave Background. <i>The Astrophysical Journal</i>, 707, 916.", "https://doi.org/10.1088/0004-637X/707/2/916"),
    "HP": ("Hawking, S. W., &amp; Penrose, R. (1970). The singularities of gravitational collapse and cosmology. <i>Proceedings of the Royal Society of London A</i>, 314, 529.", "https://doi.org/10.1098/rspa.1970.0021"),
    "G": ("Guth, A. H. (1981). Inflationary universe: A possible solution to the horizon and flatness problems. <i>Physical Review D</i>, 23, 347.", "https://doi.org/10.1103/PhysRevD.23.347"),
    "Bz": ("Bazavov, A., et al. (2012). Chiral and deconfinement aspects of the QCD transition. <i>Physical Review D</i>, 85, 054503.", "https://doi.org/10.1103/PhysRevD.85.054503"),
    "St": ("Steigman, G. (2007). Primordial Nucleosynthesis in the Precision Cosmology Era. <i>Annual Review of Nuclear and Particle Science</i>, 57, 463.", "https://doi.org/10.1146/annurev.nucl.56.080805.140437"),
    "BL": ("Bromm, V., &amp; Larson, R. B. (2004). The First Stars. <i>Annual Review of Astronomy and Astrophysics</i>, 42, 79.", "https://doi.org/10.1146/annurev.astro.42.053102.134034"),
    "Ca": ("Carniani, S., et al. (2024). Spectroscopic confirmation of two luminous galaxies at a redshift of 14. <i>Nature</i>, 633, 318.", "https://doi.org/10.1038/s41586-024-07860-9"),
    "Ba": ("Bañados, E., et al. (2017). An 800-million-solar-mass black hole in a significantly neutral Universe at a redshift of 7.5. <i>Nature</i>, 553, 473.", "https://doi.org/10.1038/nature25180"),
    "MD": ("Madau, P., &amp; Dickinson, M. (2014). Cosmic Star-Formation History. <i>Annual Review of Astronomy and Astrophysics</i>, 52, 415.", "https://doi.org/10.1146/annurev-astro-081811-125615"),
    "R": ("Riess, A. G., et al. (1998). Observational Evidence from Supernovae for an Accelerating Universe and a Cosmological Constant. <i>The Astronomical Journal</i>, 116, 1009.", "https://doi.org/10.1086/300499"),
    "Pe": ("Perlmutter, S., et al. (1999). Measurements of Ω and Λ from 42 High-Redshift Supernovae. <i>The Astrophysical Journal</i>, 517, 565.", "https://doi.org/10.1086/307221"),
    "Co": ("Connelly, J. N., et al. (2012). The Absolute Chronology and Thermal Processing of Solids in the Solar Protoplanetary Disk. <i>Science</i>, 338, 651.", "https://doi.org/10.1126/science.1226919"),
    "Bb": ("Barboni, M., et al. (2017). Early formation of the Moon 4.51 billion years ago. <i>Science Advances</i>, 3, e1602365.", "https://doi.org/10.1126/sciadv.1602365"),
    "Al": ("Allwood, A. C., et al. (2006). Stromatolite reef from the Early Archaean era of Australia. <i>Nature</i>, 441, 714.", "https://doi.org/10.1038/nature04764"),
    "Re": ("Renne, P. R., et al. (2013). Time Scales of Critical Events Around the Cretaceous-Paleogene Boundary. <i>Science</i>, 339, 684.", "https://doi.org/10.1126/science.1230492"),
    "SS": ("Schröder, K.-P., &amp; Smith, R. C. (2008). Distant future of the Sun and Earth revisited. <i>Monthly Notices of the Royal Astronomical Society</i>, 386, 155.", "https://doi.org/10.1111/j.1365-2966.2008.13022.x"),
    "Sa": ("Sawala, T., et al. (2025). No certainty of a Milky Way–Andromeda collision. <i>Nature Astronomy</i>, 9, 1206.", "https://doi.org/10.1038/s41550-025-02563-1"),
    "AL": ("Adams, F. C., &amp; Laughlin, G. (1997). A dying universe: the long-term fate and evolution of astrophysical objects. <i>Reviews of Modern Physics</i>, 69, 337.", "https://doi.org/10.1103/RevModPhys.69.337"),
    "H": ("Hawking, S. W. (1975). Particle creation by black holes. <i>Communications in Mathematical Physics</i>, 43, 199.", "https://doi.org/10.1007/BF02345020"),
    "D": ("DESI Collaboration (2025). DESI DR2 results. II. Measurements of baryon acoustic oscillations and cosmological constraints. <i>Physical Review D</i>, 112, 083515.", "https://doi.org/10.1103/tr6y-kpc6"),
}

# w: 時刻の決め方 s=ビッグバンからの秒 / z=赤方偏移 / acc=加速の始まり / ago=今から何年前 / now / after=今から何年後
# l: k=わかっている h=有力な仮説 u=わかっていない e=計算の目安。本文の {キー} は出典番号になる
EV = [
    dict(n="プランク時間", w=("s", 1e-43), tl="10<sup>-43</sup>秒", l="u", a=["before-big-bang", "what-is-big-bang"],
         x="今の物理学（重力の理論と、ミクロの世界の理論）が、そのままでは使えなくなる時刻です。0秒に何があったのか、そもそも「始まり」があったのかは、わかっていません{HP}。"),
    dict(n="インフレーション", w=("s", 1e-36), tl="10<sup>-36</sup>〜10<sup>-32</sup>秒", l="h", a=["inflation"],
         x="ほんの一瞬で、宇宙が急に大きく膨らんだという仮説です{G}。宇宙がどこもほぼ同じ温度であることを説明できます。決め手になる「原始重力波」は、まだ見つかっていません。"),
    dict(n="クォークが陽子と中性子にまとまる", w=("s", 1e-5), tl="約10<sup>-5</sup>秒（10万分の1秒）", l="h", a=[],
         x="温度が約2兆度（約154 MeV）まで下がり、ばらばらに飛び回っていたクォークが集まって、陽子と中性子ができたと考えられています{Bz}。温度はスーパーコンピューターの計算で求めたもので、時刻は温度から見積もった目安です。"),
    dict(n="元素ができる", w=("s", 180), tl="約3分", l="k", a=["cosmic-elements", "big-bang-evidence"],
         x="陽子と中性子がくっつき、ヘリウムなどの軽い元素ができました。重さで約25%がヘリウムになり、計算した割合は観測とよく合います{St}。"),
    dict(n="物質が光より多くなる", w=("z", 3387), tl="約5万年", l="k", a=["dark-matter"],
         x="ここまでは光（放射）のエネルギーが宇宙の主役でした。ここから、ダークマターを含む物質が主役になり、物質のかたまりが重力で育ち始めます（赤方偏移 z=3387、Planck 2018 の値で計算）{P}。"),
    dict(n="晴れ上がり", w=("z", 1090), tl="約38万年", l="k", a=["big-bang-evidence", "age-of-universe"],
         x="宇宙が約3000度まで冷えて原子ができ、光がまっすぐ進めるようになりました。このときの光が、今「宇宙マイクロ波背景放射」として全天から届いています{P}。"),
    dict(n="暗黒時代", w=("z", 200), tl="晴れ上がりのあと〜最初の星まで", l="h", a=["first-stars"],
         x="まだ光る星がひとつもない時代です。水素とヘリウムのガスと、ダークマターだけがありました。この時代の水素が出す弱い電波を捕まえる試みは続いていますが、確かな観測はまだありません。"),
    dict(n="最初の星", w=("z", 20), tl="約1億〜2億年（z≈20〜30）", l="h", a=["first-stars", "star-formation"],
         x="ガスが重力で集まり、最初の星が生まれたと考えられる時期です。計算では赤方偏移 z≈20〜30 とされますが、最初の星そのものはまだ見つかっていません{BL}。"),
    dict(n="とても遠くで確かめられた銀河", w=("z", 14.32), tl="約2億9000万年", l="k", a=["jwst-discoveries", "first-stars"],
         x="ジェイムズ・ウェッブ宇宙望遠鏡が2024年に、赤方偏移 z=14.32 の銀河 JADES-GS-z14-0 を光の分析で確かめました{Ca}。いちばん遠い銀河の記録は、観測が進むたびに更新されています。宇宙がまだ今の約2%の年齢のころに、もう明るい銀河がありました。"),
    dict(n="宇宙の再電離（中ごろ）", w=("z", 7.67), tl="約6億7000万年", l="k", a=[],
         x="最初の星や銀河の強い光で、宇宙のガス（水素）が再び電気を帯びていきました。全体の半分が電気を帯びたのは赤方偏移 z≈7.7 ごろと見積もられています（宇宙背景放射の観測から）{P}。"),
    dict(n="巨大ブラックホールがもうある", w=("z", 7.54), tl="約6億9000万年", l="k", a=["first-blackholes", "quasars"],
         x="赤方偏移 z=7.54 のクエーサーの中心に、太陽の約8億倍のブラックホールが見つかっています{Ba}。こんなに早く、どうやってここまで育ったのかは、わかっていません。"),
    dict(n="星づくりのピーク", w=("z", 1.9), tl="約35億年（今から約100億年前）", l="k", a=["star-formation", "supernova-elements"],
         x="宇宙全体で星がいちばんさかんに生まれた時期です（赤方偏移 z≈1.9）。今は、このころの10分の1ほどのペースでしか星が生まれていません{MD}。"),
    dict(n="膨張が加速し始める", w=("acc", 0), tl="約77億年（今から約61億年前）", l="k", a=["dark-energy", "future-of-universe"],
         x="ダークエネルギーの押し広げる働きが、物質の引き戻す力を上回り、宇宙の膨張が速くなり始めました{R}{Pe}。時刻は Planck 2018 の値で計算したものです。ダークエネルギーの正体はわかっていません。"),
    dict(n="太陽系ができる", w=("ago", 4.567e9), tl="45.67億年前", l="k", a=["solar-system-formation", "sun-future"],
         x="太陽系でいちばん古い固体（隕石の中の粒）は、45.67億年前にできました{Co}。最初の星から約90億年後です。"),
    dict(n="月ができる", w=("ago", 4.51e9), tl="約45.1億年前", l="h", a=["moon-origin"],
         x="できたばかりの地球に火星くらいの天体がぶつかり、飛び散ったものから月ができたという説（ジャイアント・インパクト説）が有力です。月の石の分析から、月は約45.1億年前にはできていたとされます{Bb}。"),
    dict(n="地球に生命がいた証拠", w=("ago", 3.43e9), tl="遅くとも約34億年前", l="h", a=["earliest-life", "origin-of-life"],
         x="オーストラリアの約34億年前の岩に残る層の重なり（ストロマトライト）は、微生物がつくったと考える研究者が多い証拠です{Al}。もっと古い「最古の生命の跡」の報告もありますが、決着していません。"),
    dict(n="恐竜を絶滅させた小惑星", w=("ago", 6.6e7), tl="約6600万年前", l="k", a=["asteroid-impact"],
         x="メキシコのユカタン半島に小惑星がぶつかり、恐竜をふくむ多くの生き物が絶滅しました。衝突と絶滅の年代は、約6600万年前とほぼ同じ時期に測られています{Re}。"),
    dict(n="今", w=("now", 0), tl="約138億年", l="k", a=["age-of-universe", "edge-of-universe"],
         x="宇宙の年齢は約138億年（137.87億年）です{P}。宇宙を満たす光の温度は約2.7度（絶対温度、2.7255 K）まで下がっています{Fx}。"),
    dict(n="地球が生き物の住めない暑さになる", w=("after", 1e9), tl="約10億年後", l="h", a=["sun-future"],
         x="太陽は少しずつ明るくなっていて、約10億年後には地球が生き物の住めない暑さになると見積もられています{SS}。"),
    dict(n="天の川銀河とアンドロメダ銀河", w=("after", 1e10), tl="今後100億年のうち（起きるかは半々）", l="u", a=["andromeda-collision", "milky-way-shape"],
         x="アンドロメダ銀河は近づいていますが、2025年の研究では、今後100億年のうちに合体する確率は約50%とされました{Sa}。横向きの動きがまだ正確に測れていないためです。"),
    dict(n="太陽が赤色巨星になる", w=("after", 7.6e9), tl="約76億年後", l="h", a=["sun-future", "white-dwarf"],
         x="太陽は中心の水素を使い切ると大きくふくらみ、約76億年後には半径が今の約256倍になると計算されています{SS}。そのあとは外側を手放し、白色矮星として冷えていきます。"),
    dict(n="新しい星が生まれなくなる", w=("after", 1e14), tl="約10<sup>14</sup>年後（100兆年後）", l="h", a=["star-formation"],
         x="星の材料のガスが使い尽くされ、新しい星が生まれなくなり、光る星の時代が終わると見積もられています{AL}。残るのは白色矮星や中性子星、ブラックホールなど、星の燃えかすです。"),
    dict(n="ブラックホールの時代", w=("after", 1e40), tl="約10<sup>40</sup>〜10<sup>100</sup>年後", l="h", a=["hawking-radiation", "neutron-star"],
         x="星の燃えかすもなくなり、ブラックホールだけが残る時代だと考えられています{AL}。陽子がいつか壊れるのかどうかで、この時代の始まりは変わります（陽子が壊れるかどうかは、わかっていません）。"),
    dict(n="ブラックホールが蒸発する", w=("after", 1e67), tl="約10<sup>67</sup>年後（太陽ほどの重さの場合）", l="h", a=["hawking-radiation", "black-hole-size"],
         x="ホーキングの計算では、ブラックホールは光や粒子を少しずつ出して軽くなり、最後には消えます{H}。太陽ほどの重さなら約10<sup>67</sup>年かかります。この放射は、まだ観測されていません。"),
    dict(n="その先の宇宙", w=("after", 1e100), tl="10<sup>100</sup>年後〜", l="u", a=["future-of-universe", "dark-energy"],
         x="ダークエネルギーが今のまま変わらなければ、宇宙は冷たく暗いまま広がり続けます（ビッグフリーズ）。ただ、ダークエネルギーが弱まっているかもしれないという観測もあり{D}、宇宙の最後は、わかっていません。"),
]

FAQ = [
    ("宇宙の年表は、どこまでわかっているの？", "晴れ上がり（約38万年後）から今までの大きなできごとは、観測でかなり確かめられています。いちばん最初の一瞬（インフレーション）や、最初の星、遠い未来のことは、仮説や計算の見積もりです。この年表では、できごとごとに「わかっている」「有力な仮説」「わかっていない」の札を付けています。"),
    ("宇宙の温度と広がりぐあいは、どうやって出しているの？", "宇宙を満たす光の温度は、今の2.7255度（絶対温度）を、そのときの距離の尺度で割って出しています（銀河どうしの距離が半分なら2倍の温度）。距離の尺度は、Planck 2018 で測られた物質・ダークエネルギー・光の量からフリードマン方程式で計算しています。最初の数秒は粒子の種類が変わるため、温度は粗い目安です。"),
    ("どうして目盛りが均等じゃないの？", "宇宙の歴史は、最初の1秒に多くのことが起き、そのあと138億年、さらに10の100乗年先まで続くためです。均等な目盛りでは最初の時代も地球の歴史も見えなくなるので、区間ごとに目盛りの刻み方を変えています（多くの区間は対数、46億年前〜1億年前は時間に比例）。"),
]


def ref(text, order):
    def f(m):
        k = m.group(1)
        if k not in order:
            order.append(k)
        return f'<a class="ref" href="#src-{order.index(k) + 1}">[{order.index(k) + 1}]</a>'
    return re.sub(r"\{(\w+)\}", f, text)


def main():
    posts = {p["slug"]: p["title"] for p in json.loads((ROOT / "media/uchu-posts.json").read_text())}
    order, evs, linked = [], [], []
    for e in EV:
        arts = [[s, posts[s]] for s in e["a"] if s in posts]
        linked += [s for s, _ in arts if s not in linked]
        evs.append({"n": e["n"], "w": list(e["w"]), "l": e["l"], "x": ref(e["x"], order), "tl": e.get("tl", ""), "a": arts})
    lab = {"k": "わかっている", "h": "有力な仮説", "u": "わかっていない"}
    items = "".join(f'<li><button type="button"><span class="tt">{e["tl"]}</span><span class="tn">{e["n"]}</span><span class="lb {e["l"]}">{lab[e["l"]]}</span>'
                    f'<span class="tx">{e["x"]}</span></button>'
                    + (('<span class="ta">' + " ／ ".join(f'<a href="/{a}/">{E(t)}</a>' for a, t in e["a"]) + "</span>") if e["a"] else "") + "</li>" for e in evs)
    assert all(e["tl"] for e in evs), "tl のないできごとがある"
    srcs = "".join(f'<li id="src-{i}">{SRC[k][0]} <a href="{SRC[k][1]}" target="_blank" rel="noopener">{E(SRC[k][1].replace("https://doi.org/", "doi:"))}</a></li>'
                   for i, k in enumerate(order, 1))
    sim = (ROOT / "sites/uchu/simulator/index.html").read_text()
    physics = re.search(r"// PHYSICS-START.*?// PHYSICS-END", sim, re.S).group(0)
    css = re.search(r"<style>\n(:root\{.*?)/\*rc\*/", sim, re.S).group(1)
    import readcheck  # 「読んだ」の札の見た目（記事ページと同じ）
    page = TEMPLATE
    for k, v in {"%%CSS%%": css + EXTRA_CSS + "/*rc*/" + readcheck.CSS + "/*/rc*/", "%%PHYSICS%%": physics, "%%EV%%": json.dumps(evs, ensure_ascii=False),
                 "%%NART%%": str(len(linked)), "%%SRCS%%": srcs, "%%LD%%": json.dumps(ld(), ensure_ascii=False),
                 "%%FAQ%%": "".join(f"<dt>{E(q)}</dt><dd>{E(a)}</dd>" for q, a in FAQ), "%%NEV%%": str(len(evs)), "%%ITEMS%%": items}.items():
        page = page.replace(k, v)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(evs)} events, {len(linked)} articles, {len(order)} sources")


def ld():
    org = {"@id": "https://seadice.win/#organization"}
    return {"@context": "https://schema.org", "@graph": [
        {"@type": "WebApplication", "name": "宇宙の年表", "url": URL, "applicationCategory": "EducationalApplication", "operatingSystem": "Web",
         "inLanguage": "ja", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "JPY"},
         "description": DESC, "publisher": org, "dateModified": "2026-10-24"},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "SEADICE", "item": "https://seadice.win/"},
            {"@type": "ListItem", "position": 2, "name": "宇宙の研究", "item": "https://uchu.seadice.win/"},
            {"@type": "ListItem", "position": 3, "name": "宇宙の年表", "item": URL}]},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]}


DESC = "バーを動かすと、ビッグバンから今、10の100乗年後まで、その時の宇宙の温度と広がりぐあい、起きたと考えられていることがわかる宇宙の年表。できごとごとに確かさ（わかっている・有力な仮説・わかっていない）と出典つき。"

EXTRA_CSS = (".now{border-left:4px solid var(--accent)}.now .nt{font-size:13px;color:var(--muted);margin:0 0 4px}.now .nn{font-size:19px;font-weight:700;margin:0 0 6px;line-height:1.45}"
             ".now .nx{font-size:15px;margin:0 0 10px}.now .na{display:flex;flex-direction:column;gap:6px;margin:0}.now .na a{font-size:14px}"
             ".nxt{font-size:14px;color:var(--muted);margin:10px 0 0}.nxt b{color:var(--text)}"
             ".stats{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:12px 0}.stats div{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px 12px}"
             ".stats small{display:block;font-size:12px;color:var(--muted)}.stats b{display:block;font-size:17px;color:var(--accent);line-height:1.4;word-break:break-all}"
             ".stats .w{grid-column:1/-1}.band{display:flex;height:10px;border-radius:4px;overflow:hidden;margin:6px 0 0}.band span{display:block;height:100%}"
             ".bandl{position:relative;height:20px;font-size:12px;color:var(--muted);margin:2px 0 0}.bandl span{position:absolute;top:0;white-space:nowrap;transform:translateX(-50%)}.bandl span:first-child{transform:none}.bandl span:last-child{transform:none}"
             "a.ref{font-size:12px;text-decoration:none;margin-left:2px}.tl .ta{display:block;font-size:13px;margin-top:4px}"
             "#tlist .tx a{color:var(--accent2)}.prog{font-size:13px;color:var(--muted);margin:8px 0 0}.prog b{color:var(--accent)}")

TEMPLATE = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>宇宙の年表｜ビッグバンから10の100乗年後まで、バーを動かして見る | 宇宙の研究</title>
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta name="description" content="''' + DESC + r'''">
<link rel="canonical" href="https://uchu.seadice.win/timeline/">
<meta property="og:type" content="website">
<meta property="og:site_name" content="宇宙の研究">
<meta property="og:title" content="宇宙の年表｜バーを動かして、その時の宇宙を見る">
<meta property="og:description" content="ビッグバンから今、10の100乗年後まで。その時の温度と広がりぐあい、起きたと考えられていることを確かさの札つきで。登録なし・無料。">
<meta property="og:url" content="https://uchu.seadice.win/timeline/">
<meta property="og:image" content="https://seadice.win/icons/seadice_ogp.png">
<meta name="theme-color" content="#0A0E16">
<script type="application/ld+json">%%LD%%</script>
<style>
%%CSS%%</style>
</head>
<body>
<nav class="top"><div class="wrap"><a class="site" href="/">宇宙の研究</a><a href="/tools/">道具</a></div></nav>
<main class="wrap" data-rc-own>
<ol class="crumb"><li><a href="https://seadice.win/">HOME</a></li><li><a href="/">宇宙の研究</a></li><li aria-current="page">宇宙の年表</li></ol>
<h1>宇宙の年表 ビッグバンから10<sup>100</sup>年後まで</h1>
<p class="lead">宇宙は約138億年前に、とても熱くて小さい状態から広がり始めました。バーを動かすと、その時の宇宙の<strong>温度</strong>と<strong>銀河どうしの距離が今の何倍か</strong>、、<strong>そのころ起きたと考えられていること</strong>が出ます。できごとには「わかっている」「有力な仮説」「わかっていない」の札を付けています。</p>

<div class="grid">
<div>
<div class="readout" aria-live="off"><span>ビッグバンから <b id="rt">-</b></span><span id="rago"></span></div>
<label for="slider" class="note">時間（区間ごとに目盛りの刻みが違います。左がビッグバン直後、右が10<sup>100</sup>年後）</label>
<input type="range" id="slider" min="0" max="1000" step="1" value="0" aria-valuetext="">
<div class="band" id="band" aria-hidden="true"></div>
<div class="bandl" aria-hidden="true"><span style="left:0">直後</span><span style="left:17%">1秒</span><span style="left:33%">38万年</span><span style="left:60%">46億年前</span><span style="left:77%">今</span><span style="right:0;left:auto">10<sup>100</sup>年後</span></div>
<div class="btns">
<button type="button" id="prev">前のできごと</button>
<button type="button" id="next" class="primary">次のできごと</button>
<button type="button" id="now">今にもどる</button>
</div>
<div class="stats">
<div><small>宇宙を満たす光の温度</small><b id="sT">-</b></div>
<div><small>距離の尺度（銀河どうしの距離が今の何倍か）</small><b id="sA">-</b></div>
<div class="w"><small>この数字の確かさ</small><span id="sL" class="note"></span></div>
</div>
<div class="card now" aria-live="polite" aria-atomic="true"><p class="nt" id="cT"></p><p class="nn" id="cN"></p><p class="nx" id="cX"></p><p class="na" id="cA"></p><p class="nxt" id="cNext"></p></div>
</div>
<div class="side">
<h2 style="margin-top:0">年表（%%NEV%%のできごと）</h2>
<p class="note">できごとを押すと、その時刻に飛びます。札は確かさ: <span class="lb k">わかっている</span><span class="lb h">有力な仮説</span><span class="lb u">わかっていない</span></p>
<p class="prog" id="prog">年表につながる記事は%%NART%%本。記事の下の「読んだ記事にする」を押すと、ここに読んだ本数が出ます。</p>
<ol class="tl" id="tlist">%%ITEMS%%</ol>
</div>
</div>

<h2>この年表の数字の出し方と限界</h2>
<ul>
<li>「距離の尺度」は、銀河どうしのように重力で結びついていない2点の距離が、今と比べて何倍かを表します。宇宙全体が有限か無限かは、わかっていません。値は Planck 2018 の値（物質・ダークエネルギー・光の量）からフリードマン方程式で計算しています。<a href="/simulator/">宇宙をつくるシミュレーター</a>と同じ計算で、今の年齢は約138億年になります。</li>
<li>温度は、宇宙を満たす光の今の温度（2.7255 K）を、距離の尺度で割った値です。最初の約10秒は、粒子の種類（標準模型）とインフレーションのあと宇宙が熱くなり直したことを仮定した粗い目安で、電子と陽電子が消えて光が温められる分も入れています。インフレーションより前は計算できません。</li>
<li>1000億年より先の距離の尺度は、ダークエネルギーが今のまま変わらないと仮定して延ばしたものです。変わるかどうかは、わかっていません。</li>
<li>地球や太陽のできごとは「今から何年前・何年後」で測られた値を使っています。</li>
</ul>

<h2>よくある質問</h2>
<dl class="faq">%%FAQ%%</dl>

<h2>続けて使える道具</h2>
<ul class="rel">
<li><a href="/simulator/">宇宙をつくるシミュレーター</a>（宇宙の値を変えると、星ができるかが変わる）</li>
<li><a href="/tools/galaxy/">銀河と星の一生シミュレーター</a>（星と惑星が生まれて消えるまで）</li>
</ul>

<h2>出典</h2>
<ol class="src">%%SRCS%%</ol>
<p class="note" style="margin-top:16px">最終更新: 2026年10月24日。記録は何も取りません（読んだ記事の印は、この端末のブラウザの中だけ）。</p>
</main>
<footer><div class="wrap"><a href="/about/">このメディアについて</a> | <a href="/sources/">出典と検証の方法</a> | <a href="/disclaimer/">免責事項</a> | <a href="https://seadice.win/">SEADICE</a> | &copy; SEADICE</div></footer>
<script>
%%PHYSICS%%
(function(){
var EV=%%EV%%,S=OURS_S,YS=SPG/1e9,LN10=Math.LN10;
var TNOW=tOfA(S,1)*UNIT_S,OLs=Math.sqrt(OL0*1),TEND=S.T[S.T.length-1],LAEND=S.X[S.X.length-1]/LN10;
var LB={k:'わかっている',h:'有力な仮説',u:'わかっていない',e:'計算の目安'};
function $(i){return document.getElementById(i)}
// 時刻（ビッグバンからの秒）
EV.forEach(function(e){var w=e.w;
 e.t=w[0]=='s'?w[1]:w[0]=='z'?tOfA(S,1/(1+w[1]))*UNIT_S:w[0]=='acc'?tOfA(S,Math.cbrt(OM0/(2*OL0)))*UNIT_S:
 w[0]=='ago'?TNOW-w[1]*YS:w[0]=='now'?TNOW:TNOW+w[1]*YS;});
// 目盛り: 区間ごとに対数の刻み方を変える。k=0 ビッグバンからの秒(log) / 1 今から何年前(log) / 2 今から何年後(log)
var SEG=[[0,170,0,-43,0],[170,330,0,0,Math.log10(3.8e5*YS)],[330,600,0,Math.log10(3.8e5*YS),Math.log10(TNOW-4.6e9*YS)],
 [600,690,3,4.6e9,1e8],[690,770,1,8,0],[770,880,2,0,11],[880,1000,2,11,100]];
function tOfP(p){for(var i=0;i<SEG.length;i++){var g=SEG[i];if(p<=g[1]||i==SEG.length-1){var f=(p-g[0])/(g[1]-g[0]),v=g[3]+(g[4]-g[3])*f;
 return g[2]==0?Math.pow(10,v):g[2]==3?TNOW-v*YS:g[2]==1?(p>=770?TNOW:TNOW-Math.pow(10,v)*YS):TNOW+Math.pow(10,v)*YS;}}}
function pOfT(t){if(Math.abs(t-TNOW)<YS*1.5)return 770;var g,v;
 for(var i=0;i<SEG.length;i++){g=SEG[i];
  if(g[2]==0)v=Math.log10(t);else if(g[2]==3){if(t>=TNOW)continue;v=(TNOW-t)/YS;}else if(g[2]==1){if(t>=TNOW)continue;v=Math.log10((TNOW-t)/YS);}else{if(t<=TNOW)continue;v=Math.log10((t-TNOW)/YS);}
  var lo=Math.min(g[3],g[4]),hi=Math.max(g[3],g[4]);if(g[2]==0&&t>TNOW-4.6e9*YS&&i<3)continue;
  if(v>=lo-1e-9&&v<=hi+1e-9)return Math.round(g[0]+(v-g[3])/(g[4]-g[3])*(g[1]-g[0]));}
 return t<1?0:1000;}
// 表示の形
function sup(n){return '10<sup>'+n+'</sup>'}
function big(y,unit){ // 年や倍を日本語で
 if(y<1e4)return (y<10?y.toFixed(1).replace(/\.0$/,''):Math.round(y).toLocaleString('ja-JP'))+unit;
 if(y>=1e16){var e=Math.floor(Math.log10(y));return '約'+sup(e)+unit;}
 var r=Number(y.toPrecision(y>=1e9&&y<1e12?3:2)),cho=Math.floor(r/1e12),oku=Math.floor(r%1e12/1e8),man=Math.floor(r%1e8/1e4),s='約';
 if(cho)s+=cho+'兆';if(oku)s+=oku+'億';if(man&&!cho)s+=man+'万';return s+unit;}
function sec(t){if(t<0.01)return '約'+sup(Math.round(Math.log10(t)))+'秒';if(t<60)return '約'+Number(t.toPrecision(2))+'秒';
 if(t<3600)return '約'+Math.round(t/60)+'分';if(t<86400)return '約'+Math.round(t/3600)+'時間';var y=t/YS;if(y<1)return '約'+Math.round(t/86400)+'日';return big(y,'年');}
function la(t){var u=t/UNIT_S;if(u<=TEND)return Math.log10(aOfT(S,u));return LAEND+OLs*(u-TEND)/LN10;} // log10(今と比べた大きさ)
function temp(l){var lt=Math.log10(2.7255)-l;if(lt>=4)return big(Math.pow(10,lt),'度');if(lt>=1)return '約'+Math.round(Math.pow(10,lt)).toLocaleString('ja-JP')+'度（絶対温度）';
 if(lt>-3)return '約'+Number(Math.pow(10,lt).toPrecision(2))+'度（絶対温度）';if(lt>-300)return '約'+sup(Math.round(lt))+'度（絶対温度）';var e=Math.floor(Math.log10(-lt));return '約 10の（−'+(-lt/Math.pow(10,e)).toFixed(1)+'×10<sup>'+e+'</sup>）乗 度。0度にかぎりなく近い';}
function size(l){if(Math.abs(l)<0.004)return '今と同じ';if(l<0){var n=Math.pow(10,-l);return n<1e4?'今の約'+Number(n.toPrecision(2)).toLocaleString('ja-JP')+'分の1':'今の'+(n>=1e16?'約'+sup(Math.round(-l)):big(n,''))+'分の1';}
 var m=Math.pow(10,l);if(l<4)return '今の約'+Number(m.toPrecision(2))+'倍';if(l<300)return '今の'+(l>=16?'約'+sup(Math.round(l)):big(m,''))+'倍';
 var e=Math.floor(Math.log10(l));return '今の 10の（'+(l/Math.pow(10,e)).toFixed(1)+'×10<sup>'+e+'</sup>）乗 倍';}
function tEarly(t){var g=106.75,T;for(var i=0;i<3;i++){T=1.55*Math.pow(g,-0.25)/Math.sqrt(t);g=T>1e5?106.75:T>150?61.75:T>100?17.25:10.75;}return Math.log10(T*1.1605e10);} // 最初の1秒（log10 K）
function lT(t){if(t<1)return tEarly(t);var l=Math.log10(2.7255)-la(t);if(t>=10)return l;var w=Math.log10(t);return tEarly(t)*(1-w)+l*w;} // log10 K（1〜10秒はつなぐ）
function lA(t){if(t>=10)return la(t);var k=Math.log10(Math.pow(4/11,1/3))*(1-Math.max(0,Math.log10(Math.max(t,1))));return Math.log10(2.7255)-lT(t)+k;} // 最初の10秒は温度から
function ago(t){var d=(t-TNOW)/YS;if(Math.abs(d)<1.5)return '今';return d<0?'今から '+big(-d,'年')+'前':'今から '+big(d,'年')+'後';}
function lbl(l){return '<span class="lb '+l+'">'+LB[l]+'</span>'}
// 読んだ記事（記事ページの「読んだ記事にする」と同じ記録）
var R={};try{R=JSON.parse(localStorage.getItem('uchu-read')||'{}')||{}}catch(e){}
function arts(e){return e.a.map(function(a){return '<a href="/'+a[0]+'/"'+(R[a[0]]?' class="rc-in"':'')+'>'+a[1].replace(/</g,'&lt;')+'</a>'}).join('')}
// 帯（区間ごとの色）
var BC=['#7FB2E5','#5E93C8','#8FD1A8','#E3B341','#E9A0A0','#A1ACBE','#5B6478'],band='';
SEG.forEach(function(g,i){band+='<span style="width:'+((g[1]-g[0])/10)+'%;background:'+BC[i]+'"></span>'});$('band').innerHTML=band;
// 年表の一覧
var L=$('tlist');
[].forEach.call(L.children,function(li,i){li.querySelector('button').onclick=function(){go(pOfT(EV[i].t),i)};
 [].forEach.call(li.querySelectorAll('.ta a'),function(a){if(R[a.getAttribute('href').slice(1,-1)])a.classList.add('rc-in')})});
var all={},rd=0;EV.forEach(function(e){e.a.forEach(function(a){all[a[0]]=1})});for(var k in all)if(R[k])rd++;
if(rd)$('prog').innerHTML='年表につながる記事 '+Object.keys(all).length+'本のうち <b>'+rd+'本</b> 読みました（この端末の記録）。';
var sl=$('slider'),cur=-1;
function idx(t){var j=-1;EV.forEach(function(e,i){if(e.t<=t*1.0000001)j=i});return j}
function show(p,force){var t=force!=null?EV[force].t:tOfP(p),i=force!=null?force:idx(t),e=EV[Math.max(i,0)];
 $('rt').innerHTML=sec(t);$('rago').innerHTML=ago(t);
 var early=t<1e-32;var l=lT(t);$('sT').innerHTML=early?'わかっていない':l>=4?big(Math.pow(10,l),'度'):temp(Math.log10(2.7255)-l);$('sA').innerHTML=early?'わかっていない':size(lA(t));
 $('sL').innerHTML=early?'インフレーションより前は、今の物理学では計算できません。':t<10?'粗い目安。最初の数秒は、粒子の種類（標準模型）と、インフレーションのあと宇宙が熱くなり直したことを仮定した見積もりです。':t>TNOW+1e11*YS?'計算の目安（ダークエネルギーが今のまま変わらない場合）。':'Planck 2018 の値で計算した目安。';
 if(i!==cur){if(i<0){$('cT').innerHTML='';$('cN').innerHTML='ビッグバン直後';$('cX').innerHTML='バーを右に動かすか「次のできごと」を押してください。';$('cA').innerHTML='';}
 else{$('cT').innerHTML=(e.tl||sec(e.t))+'　'+lbl(e.l);$('cN').innerHTML=e.n;$('cX').innerHTML=e.x;$('cA').innerHTML=e.a.length?'くわしく読む: '+arts(e):'';}
 var n=EV[i+1];$('cNext').innerHTML=n?'次のできごと: <b>'+n.n+'</b>（'+(n.tl||sec(n.t))+'）':'これより先のことは、わかっていません。';}
 sl.setAttribute('aria-valuetext',(i>=0?e.n+'、':'')+'ビッグバンから'+sec(t).replace(/<sup>(.*?)<\/sup>/,'の$1乗'));
 if(i!==cur){[].forEach.call(L.children,function(li,k){li.classList.toggle('cur',k===i)});cur=i;}}
function go(p,i){sl.value=p;show(p,i)}
sl.oninput=function(){show(+sl.value)};
$('next').onclick=function(){var i=Math.min(cur+1,EV.length-1);go(pOfT(EV[i].t),i)};
$('prev').onclick=function(){var i=Math.max(cur-1,0);go(pOfT(EV[i].t),i)};
$('now').onclick=function(){go(770)};
var h=location.hash.match(/^#p=(\d+)$/);go(h?Math.min(1000,+h[1]):0);
})();
</script>
</body>
</html>
'''

if __name__ == "__main__":
    main()
