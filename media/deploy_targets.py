"""push のたびに、デプロイするサイトを変更があったものだけに絞る。

push では変更があったサイトだけを出す（記事1本で全サイトに版が増え、Hosting の容量上限 429 に当たるのを防ぐ）。
毎晩の定期ビルド・手動実行・エンジンのコード変更のときは全サイト。

使い方: python3 media/deploy_targets.py <event_name> <before_sha> <after_sha>
出力（GITHUB_OUTPUT 用）: skip=true|false と target=...
  target は action-hosting-deploy の target にそのまま渡す。アクションが先頭に "hosting:" を付けるので、
  2サイト目以降には自分で付ける（例: seadice-ai,hosting:seadice-kokoro）。全サイトなら空。
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    event, before, after = (sys.argv[1:] + ["", "", ""])[:3]
    hosting = json.loads((ROOT / "firebase.json").read_text())["hosting"]
    site_by_dir = {h["public"].split("/", 1)[1]: h["site"] for h in hosting}

    if event != "push" or not before or set(before) == {"0"}:
        print("skip=false\ntarget=")
        return

    changed = subprocess.run(
        ["git", "diff", "--name-only", before, after],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()

    sites = set()
    for path in changed:
        parts = path.split("/")
        if parts[0] == "sites" and len(parts) > 1:
            if parts[1] in site_by_dir:
                sites.add(site_by_dir[parts[1]])
            continue
        if parts[0] == "media" and len(parts) == 2 and path.endswith(".json"):
            stem = parts[1][:-5]
            dirs = [d for d in site_by_dir if stem == d or stem.startswith(d + "-")]
            if dirs:
                sites.add(site_by_dir[max(dirs, key=len)])
                continue
        # エンジンのコード・共通設定・firebase.json など、どのサイトか決められない変更は全サイト
        print("skip=false\ntarget=")
        return

    print(f"skip={'false' if sites else 'true'}")
    print("target=" + ",hosting:".join(sorted(sites)))


if __name__ == "__main__":
    main()
