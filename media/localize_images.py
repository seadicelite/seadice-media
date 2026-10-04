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

from PIL import Image

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
    base = cfg["url"].rstrip("/") + "/img/"
    n = 0
    for slug, i in images.items():
        if isinstance(i, dict) and i.get("local") and not i.get("og") and (out / f"{slug}.webp").exists():
            save_jpeg_og(Image.open(out / f"{slug}.webp").convert("RGB"), out / f"{slug}-og.jpg")
            i["og"] = f"{base}{slug}-og.jpg"
            ip.write_text(json.dumps(images, ensure_ascii=False, indent=1))
            continue
        if not isinstance(i, dict) or i.get("local") or not str(i.get("src", "")).startswith("http"):
            continue
        try:
            im = Image.open(io.BytesIO(fetch(i["src"]))).convert("RGB")
        except Exception as e:  # noqa: BLE001
            print("skip", slug, e)
            continue
        w, h = save_webp(im, out / f"{slug}.webp", 960)
        save_webp(im, out / f"{slug}-sm.webp", 500)
        save_jpeg_og(im, out / f"{slug}-og.jpg")
        old = i["src"]
        i.update(remote=old, remote640=i.get("src640"), src=f"{base}{slug}.webp", src640=f"{base}{slug}-sm.webp", og=f"{base}{slug}-og.jpg", w=w, h=h, local=True)
        art = site / slug / "index.html"
        if art.exists():
            t = art.read_text()
            t = t.replace(f'src="{old}" width="', f'src="{i["src"]}" width="').replace(old, i["src"])
            t = re.sub(r'(<figure class="hero"><img [^>]*?)width="\d+" height="\d+"', rf'\g<1>width="{w}" height="{h}"', t, count=1)
            art.write_text(t)
        ip.write_text(json.dumps(images, ensure_ascii=False, indent=1))
        n += 1
        print("local", slug, w, h)
        time.sleep(0.4)
    print("done", n)


if __name__ == "__main__":
    main(sys.argv[1])
