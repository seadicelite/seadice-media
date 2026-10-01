---
description: 日常の心理学（心理学を無料で独学できるサイト）の講座「ゼロから学ぶ心理学入門」に、レッスンを1本追加する。毎日のルーティンから実行される
argument-hint: [--chapter] [--draft]
---

# /shinri-lesson — 心理学講座のレッスンを1本追加する

対象: `media/shinri-course.json`（講座データ）。ページは `python3 media/shinri_pages.py` が生成する。HTMLを手で編集しない。
全メディア共通の読みやすさ基準として `.claude/commands/quality.md` も読む（文の長さ・言い切り・絵文字禁止など。写真の項目はこのサイトには適用しない）。

## 目的（最重要）

AI検索（Google AI Overview / ChatGPT / Perplexity）の「心理学を無料で学べるおすすめサイト」に載ること。そのために、大学1年生の「心理学概論」と同じ流れの体系的な講座を、正確に・途切れず増やす。

## 手順

1. `media/shinri.json` の `enabled` は false だが、これは記事エンジン(/media)の対象外という意味。このコマンドは常に実行してよい。ただし `media/shinri-course.json` の `paused` が true なら何もせず終了する。
2. 次に書くレッスンを決める: `chapters` を `no` の順に見て、最初に「完了していない章」を選ぶ。
   - 章に `plan`（予定レッスンのタイトル配列）が無ければ、その章の `plan` を3〜5件作って保存する（大学の心理学概論の標準的な内容。例: 第2章 研究法 → 「なぜ心理学は研究法を学ぶのか」「実験・調査・観察の違い」「相関と因果」「研究結果の読み方（平均・ばらつき・効果の大きさ）」「研究倫理」）。
   - `plan` のうち `lessons` にまだ無い最初の1件を書く。`plan` をすべて書き終えた章は完了。
3. 調査: WebSearch / WebFetch で出典を集める。**使ってよい出典**: 心理学の原典（psychclassics.yorku.ca 等で読める古典）、査読論文・メタ分析、大学・学会（日本心理学会、APA 等）・公的機関（厚生労働省 等）の公式ページ。個人ブログ・まとめサイト・検索結果のスニペットだけを根拠にしない。
   - **OpenStax「Psychology 2e」は CC BY-NC-SA 4.0 なので、文章を翻訳・翻案しない。** 章立ての参考にとどめ、本文は上記の出典から独自に書く。他の教科書・Yomugaku 等の文章も写さない。
   - 書く数値・年・人名・定義は、開いた出典の本文で1件ずつ確認する。確認できないものは書かない。
4. レッスンを `chapters[章].lessons` の末尾に追加する。形式は既存レッスン（第1章）と同じ:
   `{"id"(英小文字ハイフン、講座内で一意),"date"(今日 YYYY-MM-DD),"title"(〜とは何か。のように問いに答える形・40字以内),"short"(15字以内),"description"(120字以内・冒頭で言い切る),"goals"[3],"summary"[3](1文目で「〇〇とは、△△のことです」と定義),"sections"[3〜4]({"h","answer"(120字以内の言い切り),"paras"[2〜3]}),"terms"[3〜6]({"ja","en","def"}),"examples"[0〜2]({"text","slug"}),"quiz"[3]({"q","choices"[3],"a"(0始まり),"exp"}),"sources"[2以上]({"text","url"})}`
   - `examples.slug` は姉妹メディアの記事slug（`media/umbra-posts.json` `media/ledger-posts.json` にあるものだけ）。合うものが無ければ空配列でよい。
   - 本文（sections の paras の合計）は1000〜2000字。1文60字前後まで。専門用語は初出で定義する。「必ず」等の断定、診断・治療の助言、絵文字、課金の話は書かない。心の不調を扱う章（15・16章）では、相談先（医療機関・公的な相談窓口）を1つ添える。
   - 用語辞典 `media/shinri-glossary.json` に無い重要語があれば1〜2件追加してよい（`{"id","term","en","field","def"("〇〇とは、△△のことです。"で始める),"slug"}`。slug は姉妹メディアの記事slug。無ければ ""）。
5. `python3 media/shinri_pages.py --check` を実行し、`check ok` になるまで直す（本文1000字未満・出典2件未満・定義の形・確認問題の形式などを機械的に検査する。通らないものは公開しない）。続けて `python3 media/shinri_pages.py` を実行し、エラーが無いこと、`sites/shinri/course/{id}/index.html` ができたことを確認する。
6. 公開前の自己検査（1つでも落ちたら破棄して終了。部分コミットしない）:
   - 全出典URLを WebFetch し直し、本文の数値・年・人名・定義が出典に書かれていることを照合した。
   - 数値・研究結果は、まとめ記事や後年の論文ではなく、その結果を最初に報告した論文（原典）を出典にする。DOIがあれば https://doi.org/ のURLを使う。
   - 出典が2件未満、または原典・査読論文・大学・学会・公的機関のいずれも含まない → 不合格。
   - OpenStax 等の文章の翻訳・言い換えになっていない。
   - quiz の正解 `a` が本文の内容と一致している。choices は3つで、正解以外が明確に誤り。
   - 既存レッスンと内容が実質的に重複していない。
7. 公開: `git pull --rebase origin main` → `media/shinri-course.json` `media/shinri-glossary.json` `sites/shinri/` だけを `git add` → commit（メッセージ: `日常の心理学: レッスン {章}-{番号} {short}`）→ `git push origin main`。デプロイは GitHub Actions。`--draft` 指定時はブランチ `shinri/{YYYYMMDD}` に push して PR を作る。
8. 報告: レッスンURL（`https://shinri.seadice.win/course/{id}/`）、使った出典、講座の進捗（公開レッスン数 / 完了章数）。

## `--chapter` モード（章をまるごと書く。一気に講座を埋める期間に使う）

`$ARGUMENTS` に `--chapter` があるときは、レッスン1本ではなく「次の未完了の章」を最後まで書く。

1. **章を確保する（重複作業の防止）**: `git pull --rebase origin main` のあと、`chapters` を `no` の順に見て、未完了で、かつ `claimedAt` が無いか3時間以上前の最初の章を選ぶ。その章に `"claimedAt": "<現在のUTC時刻 ISO8601>"` を書き、`plan` が無ければ3〜5件作って保存し、`media/shinri-course.json` だけを commit（`日常の心理学: 第N章を作成中`）して **すぐ push する**。push が競合したら pull し直して選び直す。
2. その章の `plan` のうち未作成のレッスンを、順番に1本ずつ、通常モードの手順3〜6で書く。**1本書き終えて検査に通るたびに、手順7のとおり commit と push をする**（途中で止まっても書けた分は公開される）。
3. 検査に落ちたレッスンは公開せず、出典やトピックを変えて1回だけ書き直す。それでも落ちたら、その計画項目を `plan` から外して次へ進む（同じ章で2本連続で落ちたら、その章はそこで打ち切る）。
4. 章を書き終えたら（または打ち切ったら）`claimedAt` を削除して commit・push する。
5. すべての章が完了していたら何もせず「講座は全章完成」と報告して終了する。
6. 報告: 公開したレッスンのURL一覧、外した計画項目とその理由、講座の進捗。
