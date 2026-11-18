"""テーマの表（マス）で、メディアの抜けを見る。

media/{slug}-matrix.json: {cols[{id,label,q}], rows[{id,label,cells{列id:[記事slug または https URL]}}], research[記事slug]}
  rows × cols のマスに記事を置き、空いているマス＝まだ答えていない問いを一覧にする。
  research は特定の犯罪に限らない研究の記事（表の外に置く）。

  python3 media/matrix.py {slug}          表と、空いているマス、表に置かれていない記事を出す
  python3 media/matrix.py {slug} --check  記事slugの実在と、全記事が表かresearchに置かれていることだけを検査（問題があれば終了コード1）
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(slug, check=False):
    m = json.loads((ROOT / f"media/{slug}-matrix.json").read_text())
    posts = {p["slug"] for p in json.loads((ROOT / f"media/{slug}-posts.json").read_text())}
    cols, errs, placed = m["cols"], [], set(m.get("research", []))
    for r in m["rows"]:
        for c in cols:
            for s in r["cells"].get(c["id"], []):
                if s.startswith("https://"):
                    continue
                if s not in posts:
                    errs.append(f'{r["label"]} × {c["label"]}: 記事がない {s}')
                placed.add(s)
    for s in m.get("research", []):
        if s not in posts:
            errs.append(f"research: 記事がない {s}")
    loose = sorted(posts - placed)
    if loose:
        errs.append("表に置かれていない記事（どのマスに入るか決めて matrix.json に足す）: " + ", ".join(loose))
    if check:
        print("\n".join(errs) or f"matrix ok {slug}")
        return 1 if errs else 0
    w = max(len(r["label"]) for r in m["rows"])
    print(" " * (w * 2) + " " + " ".join(f'{c["label"]:　<4}' for c in cols))
    gaps, filled = [], 0
    for r in m["rows"]:
        line = []
        for c in cols:
            n = len(r["cells"].get(c["id"], []))
            line.append(f"{n:>4}  " if n else "   ・ ")
            if n:
                filled += 1
            else:
                gaps.append((r, c))
        print(f'{r["label"]:　<{w}} ' + " ".join(line))
    total = len(m["rows"]) * len(cols)
    print(f"\n埋まっているマス {filled}/{total}（{filled * 100 // total}%）、研究の記事 {len(m.get('research', []))}本")
    by_col = {}
    for r, c in gaps:
        by_col.setdefault(c["label"], []).append(r["label"])
    print("\n空いているマス（列ごと）:")
    for c in cols:
        if c["label"] in by_col:
            print(f'- {c["label"]}（{c["q"]}）: ' + "、".join(by_col[c["label"]]))
    if errs:
        print("\n要確認:\n" + "\n".join(errs))
    return 0


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a:
        print(__doc__)
        sys.exit(0)
    sys.exit(main(a[0], "--check" in sys.argv))
