---
description: 日常の心理学の心理学用語辞典で、用語の個別ページ（〇〇とは）を作る・用語を増やす。ルーティンから実行される
argument-hint: [件数 例: 10]
---

# /shinri-terms — 用語の個別ページを作る

対象: `media/shinri-glossary.json`。ページは `python3 media/shinri_pages.py` が生成する（HTMLを手で編集しない）。
目的: 「〇〇とは」という検索で、AI検索（Google AI Overview 等）に引用されること。1語1ページで、定義を冒頭で言い切る。

## 手順

1. `git pull --rebase origin main`。件数 N は `$ARGUMENTS`（無ければ 5）。
2. **対象を選ぶ**: `detail` が無い用語を上から N 件。全用語に `detail` があれば、講座のレッスンの `terms`（`media/shinri-course.json`）のうち用語辞典に無い重要な用語を N 件、新しい用語として追加する（`id` は英小文字ハイフン、`field` は既存の分野名か「心理学の基礎」「心理学の研究法」「脳と心」「学習と記憶」「発達」「感情とパーソナリティ」「社会心理学」「心の健康」から選ぶ。`def` は「〇〇とは、△△のことです。」で始める。`slug` は姉妹メディア記事が無ければ ""）。用語数が 200 に達したら新規追加はしない。
3. 各用語に次を追加する（既存の `mere-exposure` が見本）:
   - `date`: 今日（YYYY-MM-DD）
   - `detail`: 3〜4段落・合計400〜800字。誰がいつ提唱・発見したか、代表的な研究の内容、限界や誤解されやすい点。
   - `example`: 日常の例を1〜2文。
   - `faq`: 3問。1問目は必ず「〇〇とは何ですか？」で、答えは定義と同じ趣旨。残りは「〇〇と△△の違いは？」「〇〇は本当か？」など、実際に検索されそうな質問。
   - `sources`: 2件以上。原典（その概念を最初に報告した論文・著作）を必ず1件含め、残りは代表的なレビュー・メタ分析・学会・公的機関。DOI があれば `https://doi.org/...`。
4. 出典は必ず開いて（Crossref `https://api.crossref.org/works/{doi}`、Europe PMC、出版社ページ等）、書いた年・人名・内容が出典と一致することを確認する。確認できない数値や主張は書かない。要旨が読めない論文は、タイトルと書誌情報で言える範囲だけに使う。教科書・まとめサイトの文章を写さない。絵文字、診断・治療の助言、断定（「必ず」）を書かない。
5. `python3 media/shinri_pages.py --check` が `check ok` になるまで直し、`python3 media/shinri_pages.py` でビルドする。`sites/shinri/glossary/{id}/index.html` ができたことを確認する。
6. `media/shinri-glossary.json` と `sites/shinri/` だけを commit（`日常の心理学: 用語ページ N件（{用語名, ...}）`）して `git push origin main`。検査に落ちた用語は、その用語の追加分だけ取り消してから commit する。
7. 報告: 作ったページのURL（`https://shinri.seadice.win/glossary/{id}/`）、残りの未作成数、用語の総数。
