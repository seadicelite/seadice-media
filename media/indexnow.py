"""デプロイ後、更新された記事URLを IndexNow(Bing・Yandex 等。ChatGPT検索などAI検索の情報源)に通知する。
usage: python3 media/indexnow.py <変更ファイル...>   (例: git diff --name-only HEAD~1 HEAD)
キーは公開前提の値。各サイトのルートに <KEY>.txt を置いている(seo.write_robots)。"""
import json, os, re, sys, urllib.request
from pathlib import Path
from seo import INDEXNOW_KEY

ROOT = Path(__file__).resolve().parent.parent
sites = {}
for f in (ROOT / "media").glob("*.json"):
    try:
        c = json.loads(f.read_text())
    except Exception:
        continue
    if isinstance(c, dict) and c.get("path") and c.get("url"):
        sites[c["path"].strip("/").split("/")[-1]] = c["url"]
sites.setdefault("shinri", "https://shinri.seadice.win/")

urls = {}
for name in sys.argv[1:]:
    m = re.match(r"sites/([^/]+)/(?:(.+)/)?index\.html$", name)
    if not m or m.group(1) not in sites:
        continue
    base = sites[m.group(1)]
    urls.setdefault(base, set()).add(base + (m.group(2) + "/" if m.group(2) else ""))
for base, us in urls.items():
    host = re.sub(r"^https?://", "", base).rstrip("/")
    body = json.dumps({"host": host, "key": INDEXNOW_KEY, "keyLocation": f"{base}{INDEXNOW_KEY}.txt",
                       "urlList": sorted(us)[:10000]}).encode()
    if os.environ.get("DRY"):
        print(host, sorted(us)); continue
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(host, len(us), "urls ->", r.status)
    except Exception as e:  # 通知の失敗でデプロイを止めない
        print(host, "indexnow failed:", e)
