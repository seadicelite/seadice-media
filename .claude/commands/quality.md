---
description: 品質基準の入口。サイトの種類（記事メディア・学習サイト・Webツール）ごとに docs/quality/ に分割済み
---

# 品質基準（入口）

品質基準はサイトの種類ごとに `docs/quality/` へ分割した（2026-10-03〜）。このファイルにルールを書き足さない。

1. `docs/quality/base.md` を読む（全種類共通）。
2. `media/{slug}.json` の `siteType` に応じて、`docs/quality/article.md` / `course.md` / `tool.md` のどれか1つを読む（`siteType` が無ければ `article`）。
3. サイト全体の定期チェックをするときだけ `docs/quality/site.md` を読む。
