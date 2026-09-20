# seadice-media

SEADICE の AI メディア運営エンジン。1つの設定ファイル(`media/{slug}.json`)で1媒体を運営する。

- 第1号: SEADICE RESEARCH → https://research.seadice.win/ (Firebase Hosting site `seadice-research`)
- 記事生成: `.claude/commands/media.md`（クラウドのルーティンが毎日実行）
- 一覧・sitemap 再生成: `python3 media/build.py research`
- 写真: `python3 media/photo.py research <slug> "<英語の検索語>"`（Wikimedia Commons、キー不要）
- 停止スイッチ: `media/research.json` の `enabled` を false にする
- 本体サイト(seadice.win)のリポジトリとは完全に独立している。
