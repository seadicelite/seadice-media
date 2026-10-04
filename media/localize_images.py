"""記事写真を自サイト配信に切り替える(外部画像の直リンクをやめる)。

使い方: python3 media/localize_images.py {media} && python3 media/build.py {media}

{media}-images.json の外部URL(Wikimedia Commons 等)を1回だけ取得し、WebP に変換して
sites/{media}/img/{記事slug}.webp(幅960まで) と {記事slug}-sm.webp(幅500まで) に保存する。
images.json の src / src640 を自サイトのURLに置き換え、元のURLは remote / remote640 に残す
(作者・ライセンス・出典ページの表示はそのまま)。記事本文の hero 画像の src と幅・高さも書き換える。
新しく photo.py で写真を付けたあとに再実行すると、まだ外部URLのものだけを処理する。
"""
import io
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # PILが無い環境(クラウドの自動実行など)では、元の縮小済み画像をそのまま保存する
    Image = None

ROOT = Path(__file__).resolve().parent.parent
UA = "SEADICE-media/1.0 (https://seadice.win/; hi@seadice.win)"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def save_webp(im, path, max_w):
    im = im.copy()
    if im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(path, "WEBP", quality=80, method=6)
    return im.width, im.height


def save_jpeg_og(im, path):
    """SNSのシェア画像用(WebP非対応のサービスがあるためJPEG)。"""
    im = im.copy()
    if im.width > 1200:
        im = im.resize((1200, round(im.height * 1200 / im.width)), Image.LANCZOS)
    im.save(path, "JPEG", quality=82, optimize=True, progressive=True)


def main(media):
    cfg = json.loads((ROOT / f"media/{media}.json").read_text())
    ip = ROOT / f"media/{media}-images.json"
    images = json.loads(ip.read_text())
    site = ROOT / cfg["path"]
    out = site / "img"
    out.mkdir(exist_ok=True)
    base = "/img/"  # ページ内は相対パス(独自ドメイン未接続の web.app でも表示できる)
    og_base = cfg["url"].rstrip("/") + "/img/"  # SNSのシェア画像は絶対URLが必要
    n = 0
    for slug, i in images.items():
        if Image and isinstance(i, dict) and i.get("local") and not i.get("og") and (out / f"{slug}.webp").exists():
            save_jpeg_og(Image.open(out / f"{slug}.webp").convert("RGB"), out / f"{slug}-og.jpg")
            i["og"] = f"{og_base}{slug}-og.jpg"
            ip.write_text(json.dumps(images, ensure_ascii=False, indent=1))
            continue
        if not isinstance(i, dict) or i.get("local") or not str(i.get("src", "")).startswith("http"):
            continue
        old = i["src"]
        try:
            raw = fetch(old)
            if Image:
                im = Image.open(io.BytesIO(raw)).convert("RGB")
                w, h = save_webp(im, out / f"{slug}.webp", 960)
                save_webp(im, out / f"{slug}-sm.webp", 500)
                save_jpeg_og(im, out / f"{slug}-og.jpg")
                names = (f"{slug}.webp", f"{slug}-sm.webp", f"{slug}-og.jpg")
            else:
                ext = ".png" if raw[:4] == b"\x89PNG" else ".jpg"
                (out / f"{slug}{ext}").write_bytes(raw)
                sm = i.get("src640")
                (out / f"{slug}-sm{ext}").write_bytes(fetch(sm) if sm and sm != old else raw)
                w, h = i.get("w"), i.get("h")
                names = (f"{slug}{ext}", f"{slug}-sm{ext}", f"{slug}{ext}")
                i["unconverted"] = True
        except Exception as e:  # noqa: BLE001
            print("skip", slug, e)
            continue
        i.update(remote=old, remote640=i.get("src640"), src=base + names[0], src640=base + names[1], og=og_base + names[2], w=w, h=h, local=True)
        art = site / slug / "index.html"
        if art.exists():
            t = art.read_text()
            t = t.replace(f'src="{old}" width="', f'src="{i["src"]}" width="').replace(old, i["src"])
            if w and h:
                t = re.sub(r'(<figure class="hero"><img [^>]*?)width="\d+" height="\d+"', rf'\g<1>width="{w}" height="{h}"', t, count=1)
            art.write_text(t)
        ip.write_text(json.dumps(images, ensure_ascii=False, indent=1))
        n += 1
        print("local", slug, w, h)
        time.sleep(0.4)
    # PILのある環境で、PIL無しで保存した画像(unconverted)をWebPに変換し直す
    if Image:
        for slug, i in images.items():
            if not (isinstance(i, dict) and i.get("unconverted")):
                continue
            src_file = out / i["src"].rsplit("/", 1)[1]
            if not src_file.exists():
                continue
            im = Image.open(src_file).convert("RGB")
            w, h = save_webp(im, out / f"{slug}.webp", 960)
            save_webp(im, out / f"{slug}-sm.webp", 500)
            save_jpeg_og(im, out / f"{slug}-og.jpg")
            old_src = i["src"]
            i.update(src=f"{base}{slug}.webp", src640=f"{base}{slug}-sm.webp", og=f"{og_base}{slug}-og.jpg", w=w, h=h)
            i.pop("unconverted", None)
            art = site / slug / "index.html"
            if art.exists():
                art.write_text(art.read_text().replace(old_src, i["src"]))
            ip.write_text(json.dumps(images, ensure_ascii=False, indent=1))
            n += 1
            print("converted", slug)
    # images.json に無いのに、記事本文に外部URLのヒーロー画像が直接書かれている場合
    for art in site.glob("*/index.html"):
        slug = art.parent.name
        t = art.read_text()
        m = re.search(r'<figure class="hero"><img [^>]*?src="(https?://[^"]+)"', t)
        if not m or slug in images or "/img/" in m.group(1):
            continue
        old = m.group(1)
        try:
            raw = fetch(old)
        except Exception as e:  # noqa: BLE001
            print("skip", slug, e)
            continue
        if Image:
            im = Image.open(io.BytesIO(raw)).convert("RGB")
            w, h = save_webp(im, out / f"{slug}.webp", 960)
            save_webp(im, out / f"{slug}-sm.webp", 500)
            save_jpeg_og(im, out / f"{slug}-og.jpg")
            new, sm, og = f"{base}{slug}.webp", f"{base}{slug}-sm.webp", f"{og_base}{slug}-og.jpg"
        else:
            (out / f"{slug}.jpg").write_bytes(raw)
            new = sm = f"{base}{slug}.jpg"
            og = f"{og_base}{slug}.jpg"
            w = h = None
        t = t.replace(old, new)
        if w and h:
            t = re.sub(r'(<figure class="hero"><img [^>]*?)width="\d+" height="\d+"', rf'\g<1>width="{w}" height="{h}"', t, count=1)
        art.write_text(t)
        images[slug] = {"src": new, "src640": sm, "og": og, "remote": old, "w": w, "h": h, "local": True, "alt": "", "from_article": True}
        if not Image:
            images[slug]["unconverted"] = True
        ip.write_text(json.dumps(images, ensure_ascii=False, indent=1))
        n += 1
        print("local(article)", slug)
    print("done", n)


if __name__ == "__main__":
    main(sys.argv[1])
