#!/usr/bin/env python3
"""サイト全体の定期チェック（docs/quality/site.md の 1・3〜5 を機械的に一覧化する）。

使い方: python3 media/site_check.py [slug ...]   # 省略時は全メディア
ファイルは書き換えない。問題のあるページだけを出力する。
"""
import difflib, glob, html, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEADICE_LLMS = os.path.join(os.path.dirname(ROOT), "SEADICE", "p", "llms.txt")
ORG_ID = "https://seadice.win/#organization"  # seadice.win のトップと同じ @id で運営者を1つの実体にまとめる


def text_len(src):
    body = re.sub(r"(?s)<(script|style|head|nav|footer)\b.*?</\1>", "", src)
    return len(re.sub(r"\s+", "", html.unescape(re.sub(r"<[^>]+>", "", body))))


def check(cfg):
    slug, base = cfg["slug"], os.path.join(ROOT, cfg["path"])
    site_type = cfg.get("siteType", "article")
    url = cfg.get("url", "").rstrip("/")
    issues = []
    pages = {}
    for f in glob.glob(os.path.join(base, "**", "index.html"), recursive=True):
        rel = "/" + os.path.relpath(os.path.dirname(f), base).replace(os.sep, "/") + "/"
        pages["/" if rel == "/./" else rel] = open(f, encoding="utf-8").read()

    # 4. 運営者・免責・出典方針・llms.txt
    for need in ("/about/", "/disclaimer/", "/sources/"):
        if need not in pages:
            issues.append(f"必須ページなし: {need}")
    if not os.path.exists(os.path.join(base, "llms.txt")):
        issues.append("llms.txt なし")
    if url and os.path.exists(SEADICE_LLMS):
        host = re.sub(r"^https?://", "", url)
        if host not in open(SEADICE_LLMS, encoding="utf-8").read():
            issues.append(f"seadice.win の llms.txt に未掲載: {host}")
    no_id = sorted(p for p, h in pages.items() if '"Organization"' in h and ORG_ID not in h)
    if no_id:
        issues.append(f"運営者 Organization に {ORG_ID} が無い {len(no_id)}件: {', '.join(no_id[:8])}")

    # 5. sitemap とページ数
    sm = os.path.join(base, "sitemap.xml")
    if os.path.exists(sm):
        locs = {re.sub(r"^https?://[^/]+", "", u) or "/" for u in re.findall(r"<loc>([^<]+)</loc>", open(sm).read())}
        missing = sorted(p for p in pages if p not in locs and not p.startswith("/check/"))
        dead = sorted(p for p in locs if p not in pages)
        if missing:
            issues.append(f"sitemap 未掲載 {len(missing)}件: {', '.join(missing[:8])}")
        if dead:
            issues.append(f"sitemap にあるが実ページなし {len(dead)}件: {', '.join(dead[:8])}")
    else:
        issues.append("sitemap.xml なし")

    # 5. 孤立ページ（他のどのページからもリンクされていない）
    linked = set()
    for src, h in pages.items():
        for href in re.findall(r'href="([^"#?]+)', h):
            href = re.sub(r"^" + re.escape(url), "", href) if url else href
            if href.startswith("/"):
                linked.add(href if href.endswith("/") else href + "/")
            elif not href.startswith(("http", "mailto")):
                linked.add(os.path.normpath(os.path.join(src, href)).replace(os.sep, "/").rstrip("/") + "/")
    orphans = sorted(p for p in pages if p != "/" and p not in linked)
    if orphans:
        issues.append(f"孤立ページ {len(orphans)}件: {', '.join(orphans[:8])}")

    # JSON-LD
    bad = [p for p, h in pages.items() for blk in re.findall(r'(?s)<script type="application/ld\+json">(.*?)</script>', h)
           if not _parses(blk)]
    if bad:
        issues.append(f"JSON-LD パース失敗 {len(bad)}件: {', '.join(sorted(set(bad))[:8])}")

    # 1. 量産判定: 薄いページ・似たタイトル（記事メディアのみ）
    if site_type == "article":
        pj = os.path.join(ROOT, "media", f"{slug}-posts.json")
        posts = json.load(open(pj, encoding="utf-8")) if os.path.exists(pj) else []
        posts = posts if isinstance(posts, list) else posts.get("posts", [])
        # 記事は posts.json に載っているものだけ（ハブ・特設ページは対象外）
        arts = {p: h for p, h in pages.items() if p.strip("/") in {a.get("slug") for a in posts}}
        thin = sorted(p for p, h in arts.items() if text_len(h) < 800)
        if thin:
            issues.append(f"本文800字未満 {len(thin)}件: {', '.join(thin[:8])}")
        noimg = sorted(p for p, h in arts.items() if "<img" not in h)
        if noimg:
            issues.append(f"画像なし記事 {len(noimg)}件: {', '.join(noimg[:8])}")
        for i, a in enumerate(posts):
            for b in posts[i + 1:]:
                r = difflib.SequenceMatcher(None, a.get("title", ""), b.get("title", "")).ratio()
                if r >= 0.75:
                    issues.append(f"似たタイトル({r:.2f}): {a.get('slug')} / {b.get('slug')}")
    return slug, len(pages), issues


def _parses(s):
    try:
        json.loads(s)
        return True
    except ValueError:
        return False


def main():
    slugs = sys.argv[1:]
    total = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "media", "*.json"))):
        try:
            cfg = json.load(open(f, encoding="utf-8"))
        except ValueError:
            continue
        if not isinstance(cfg, dict) or "siteType" not in cfg or "path" not in cfg:
            continue
        if slugs and cfg["slug"] not in slugs:
            continue
        slug, n, issues = check(cfg)
        total += len(issues)
        print(f"## {slug} ({cfg['siteType']}, {n}ページ) {'OK' if not issues else f'{len(issues)}件'}")
        for i in issues:
            print(f"- {i}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
