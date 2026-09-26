#!/usr/bin/env python3
"""記事に写真を1枚入れる（キー不要）。1記事につき検索1回のみ。
使い方: python3 media/photo.py research <記事slug> "<英語の検索語>" [--replace|--openverse]
Wikimedia Commons で候補が無ければ Openverse（Flickr Commons・美術館コレクション等を横断検索）に自動フォールバックする。
--openverse は Commons を飛ばして最初から Openverse だけを検索する（Commonsの結果が弱い時の再検索用）。
自由に使えるライセンス（パブリックドメイン/CC0/CC BY/CC BY-SA）の写真だけを採用し、撮影者・ライセンス・元ページを必ず表示する。
候補なし・API失敗のときは何もせず正常終了（記事は写真なしでも成立する）。"""
import html, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "SEADICE-media/1.0 (https://seadice.win; hi@seadice.win)"
OK_LIC = re.compile(r"^(CC0|CC BY(?!-N)(?!.*\bN[CD]\b)|CC BY-SA(?!.*\bN[CD]\b)|Public domain|PD)", re.I)
OK_LIC_OV = {"cc0", "by", "by-sa", "pdm"}  # Openverse の license コード(nc/nd系は除く)
# 記事に不向きな種類の画像と、センシティブな内容（人物の露出・病院・事故・死・武器など）を題名と説明文から除外する
BAD_TITLE = re.compile(r"\b(map|logo|flag|diagram|chart|coat of arms|screenshot|scan|poster|stamp|illustration|statue|sculpture|"
                       r"nude|naked|nudity|topless|erotic|sex\w*|bikini|lingerie|underwear|fetish|porn\w*|"
                       r"patient|hospital|intensive care|surgery|wound|injur\w*|corpse|dead|death|funeral|autopsy|"
                       r"war|weapon|gun|blood|accident|crash|disaster|victim|suicide|drug\w*|child abuse)\b", re.I)
CSS = ".hero{margin:0 0 24px}.hero img{display:block;width:100%;height:auto;border-radius:14px;background:#0C0C1A}.hero figcaption{font-size:11px;color:var(--muted);margin-top:6px;line-height:1.5}.hero figcaption a{color:#7dd3fc}"
FIG = re.compile(r'<figure class="hero">.*?</figure>\s*', re.S)


def strip(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t or "")).strip()


def clean_artist(a):
    """作者欄がURLだけのとき（Pixabay等）は、ユーザー名を取り出して読める表記にする。"""
    if a.startswith("http"):
        name = re.sub(r"-\d+$", "", a.rstrip("/").split("/")[-1])
        return (name + (" (Pixabay)" if "pixabay" in a else ""))[:80]
    return a[:80] or "Unknown"


def search(query):
    params = {"action": "query", "format": "json", "generator": "search", "gsrsearch": f"{query} filetype:bitmap",
              "gsrnamespace": 6, "gsrlimit": 30, "prop": "imageinfo", "iiprop": "url|size|mime|extmetadata",
              "iiurlwidth": 960, "iiextmetadatafilter": "LicenseShortName|LicenseUrl|Artist|ImageDescription"}
    r = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    pages = json.load(urllib.request.urlopen(r, timeout=20)).get("query", {}).get("pages", {})
    return sorted(pages.values(), key=lambda p: p.get("index", 999))


def pick_commons(query, used):
    for p in search(query):
        ii = (p.get("imageinfo") or [{}])[0]
        m = ii.get("extmetadata", {})
        lic = strip(m.get("LicenseShortName", {}).get("value"))
        if (ii.get("mime") != "image/jpeg" or ii.get("width", 0) < 1200 or ii.get("width", 0) < ii.get("height", 0)
                or not OK_LIC.match(lic) or BAD_TITLE.search(p["title"] + " " + strip(m.get("ImageDescription", {}).get("value")))
                or p["title"] in used or not ii.get("thumburl")):
            continue
        base = ii["thumburl"].split("?")[0].replace("//thumb.wikimedia.org/", "//upload.wikimedia.org/")
        ratio = ii["thumbheight"] / ii["thumbwidth"]
        return {"file": p["title"], "src": re.sub(r"/\d+px-", "/960px-", base), "src640": re.sub(r"/\d+px-", "/500px-", base),
                "w": 960, "h": round(960 * ratio), "alt": strip(m.get("ImageDescription", {}).get("value")) or query,
                "artist": clean_artist(strip(m.get("Artist", {}).get("value"))), "license": lic,
                "licenseUrl": m.get("LicenseUrl", {}).get("value", ""), "page": ii["descriptionurl"], "source_label": "Wikimedia Commons"}
    return None


def search_openverse(query):
    params = {"q": query, "license_type": "commercial,modification", "mature": "false", "page_size": 20, "category": "photograph"}
    r = urllib.request.Request("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params), headers={"User-Agent": UA})
    return json.load(urllib.request.urlopen(r, timeout=20)).get("results", [])


def pick_openverse(query, used):
    for p in search_openverse(query):
        lic = (p.get("license") or "").lower()
        w, h = p.get("width") or 0, p.get("height") or 0
        title = p.get("title") or ""
        if (lic not in OK_LIC_OV or p.get("mature") or w < 1000 or w < h
                or BAD_TITLE.search(title) or p["url"] in used or not p.get("url")
                or not re.search(r"\.jpe?g($|\?)", p["url"], re.I)):
            continue
        lic_disp = {"cc0": "CC0", "pdm": "Public domain"}.get(lic, f"CC {lic.upper()}")
        ver = p.get("license_version")
        if ver and lic not in ("cc0", "pdm"):
            lic_disp = f"{lic_disp} {ver}"
        return {"file": p["url"], "src": p["url"], "src640": p["url"], "w": w, "h": h,
                "alt": title or query, "artist": clean_artist(p.get("creator") or "Unknown"), "license": lic_disp,
                "licenseUrl": p.get("license_url", ""), "page": p.get("foreign_landing_url") or p["url"],
                "source_label": (p.get("source") or p.get("provider") or "Openverse").capitalize()}
    return None


def main(media, slug, query, flag=""):
    cfg = json.loads((ROOT / f"media/{media}.json").read_text())
    art = ROOT / cfg["path"] / slug / "index.html"
    ip = ROOT / f"media/{media}-images.json"
    images = json.loads(ip.read_text()) if ip.exists() else {}
    text = art.read_text()
    if flag in ("--replace", "--openverse"):
        images.pop(slug, None)
        text = FIG.sub("", text)
    elif slug in images or 'class="hero"' in text:
        return print("skip: 既に写真あり")
    used = {i.get("file") for i in images.values() if isinstance(i, dict)}
    i = None
    if flag != "--openverse":
        try:
            i = pick_commons(query, used)
        except Exception as e:  # noqa: BLE001
            print("skip: Commons API 失敗", e)
    if not i:
        try:
            i = pick_openverse(query, used)
        except Exception as e:  # noqa: BLE001
            print("skip: Openverse API 失敗", e)
    if not i:
        return print("skip: 候補なし")
    i["alt"] = i["alt"][:140]
    images[slug] = i
    ip.write_text(json.dumps(images, ensure_ascii=False, indent=1))
    lic_html = f'<a href="{html.escape(i["licenseUrl"], quote=True)}" target="_blank" rel="noopener">{html.escape(i["license"])}</a>' if i["licenseUrl"] else html.escape(i["license"])
    fig = (f'<figure class="hero"><img src="{i["src"]}" width="{i["w"]}" height="{i["h"]}" alt="{html.escape(i["alt"], quote=True)}">'
           f'<figcaption>Photo: {html.escape(i["artist"])} / {lic_html} / '
           f'<a href="{i["page"]}" target="_blank" rel="noopener">{html.escape(i["source_label"])}</a></figcaption></figure>\n\n  ')
    text = text.replace('  <div class="ai-badge">', "  " + fig + '<div class="ai-badge">', 1)
    if ".hero{" not in text:
        text = text.replace("footer{border-top", CSS + "footer{border-top", 1)
    art.write_text(text)
    print("photo:", i["file"], "|", i["artist"], "|", i["license"], "|", i["source_label"])


if __name__ == "__main__":
    main(*sys.argv[1:5])
