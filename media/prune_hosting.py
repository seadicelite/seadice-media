"""Hosting の古い版を消して、無料枠（10GB）の容量上限 429 を防ぐ。

チャネルの保持数（live は5件）を設定しても、古い版はすぐには消えない。2026-10-10 には各サイトに
FINALIZED の版が29件ずつ残り、容量上限でデプロイが止まった。デプロイのあとにこれを走らせる。

残すもの: 各チャネルの直近 KEEP 件のリリースが使っている版。それ以外の FINALIZED 版を消す。
プロジェクト内の全サイト（本体 seadiceweb を含む）が対象。

使い方: GOOGLE_APPLICATION_CREDENTIALS=<サービスアカウントJSON> python3 media/prune_hosting.py [--dry-run]
"""
import sys

import google.auth
from google.auth.transport.requests import AuthorizedSession

PROJECT = "seadiceweb"
KEEP = 5
API = "https://firebasehosting.googleapis.com/v1beta1/"


def pages(session, url, key):
    token = ""
    while True:
        res = session.get(url + (f"&pageToken={token}" if token else ""))
        res.raise_for_status()
        data = res.json()
        yield from data.get(key, [])
        token = data.get("nextPageToken")
        if not token:
            return


def main():
    dry = "--dry-run" in sys.argv
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    s = AuthorizedSession(creds)
    total_n = total_b = 0
    for site in pages(s, f"{API}projects/{PROJECT}/sites?pageSize=100", "sites"):
        name = site["name"].split("/")[-1]
        keep = set()
        for ch in pages(s, f"{API}sites/{name}/channels?pageSize=100", "channels"):
            res = s.get(f"{API}{ch['name']}/releases?pageSize={KEEP}")
            res.raise_for_status()
            keep |= {r["version"]["name"] for r in res.json().get("releases", [])[:KEEP] if "version" in r}
        old = [v for v in pages(s, f'{API}sites/{name}/versions?pageSize=100&filter=status%3D%22FINALIZED%22', "versions")
               if v["name"] not in keep]
        for v in old:
            if not dry:
                s.delete(API + v["name"]).raise_for_status()
            total_b += int(v.get("versionBytes", 0))
        total_n += len(old)
        if old:
            print(f"{name}: {len(old)} versions")
    print(f"{'would delete' if dry else 'deleted'} {total_n} versions, {total_b / 1e9:.2f} GB")


if __name__ == "__main__":
    main()
