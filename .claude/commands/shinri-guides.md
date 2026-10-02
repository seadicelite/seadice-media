---
description: 日常の心理学に「心理学の独学Q&A」「分野別の入門」ページを書く。ルーティンから実行される
argument-hint: [件数 例: 4]
---

# /shinri-guides — 独学Q&A・分野入門ページを書く

対象: `media/shinri-guides.json`（配列）。ページは `python3 media/shinri_pages.py` が `/guide/{id}/` に生成する（HTMLを手で編集しない）。
目的: 心理学を独学しようとする人が検索する質問に1ページずつ答え、AI検索に「心理学を無料で学べるサイト」として引用されること。

## 書くページ（上から順に、まだ `media/shinri-guides.json` に無いものを書く）

独学Q&A（`kind: "qa"`）:
1. `self-study` 心理学は独学できる？独学でできること・できないこと
2. `study-order` 心理学は何から学ぶ？初心者のための勉強の順番
3. `certified-public-psychologist` 公認心理師になるには？資格の取り方と仕事
4. `cpp-vs-clinical-psychologist` 公認心理師と臨床心理士の違いは？
5. `psychology-department` 心理学部・心理学科では何を学ぶ？
6. `why-study-psychology` 心理学を学ぶと何に役立つ？
7. `read-psychology-papers` 心理学の論文はどう読む？初心者向けの読み方
8. `psychology-vs-pop-psychology` 心理学と占い・性格診断・心理テクニックの違いは？
9. `psychology-in-english` 心理学は英語で学ぶべき？英語の教材の使い方
10. `psychology-certifications` 心理学の資格・検定にはどんなものがある？

分野別の入門（`kind: "field"`、`chapters` に対応する講座の章番号を入れる）:
11. `social-psychology` 社会心理学とは（第12章）
12. `cognitive-psychology` 認知心理学とは（第5・7・8章）
13. `developmental-psychology` 発達心理学とは（第9章）
14. `clinical-psychology` 臨床心理学とは（第15・16章）
15. `biopsychology` 生理心理学（脳と心）とは（第3・4章）
16. `learning-psychology` 学習心理学とは（第6章）
17. `emotion-psychology` 感情心理学とは（第10章）
18. `personality-psychology` パーソナリティ心理学とは（第11章）
19. `industrial-organizational-psychology` 産業・組織心理学とは（第13章）
20. `health-psychology` 健康心理学とは（第14章）

## 手順

1. `git pull --rebase origin main`。件数 N は `$ARGUMENTS`（無ければ 4）。上のリストのうち未作成のものを N 件書く。全部あれば何もせず終了。
2. 形式: `{"id","kind","title"(リストの文言),"lead"(最初の1〜2文で質問に言い切りで答える。120字以内が望ましい),"date"(今日),"sections"[3〜5]({"h","answer"(120字以内の言い切り),"paras"[2〜3]}),"chapters"[章番号](fieldは必須、qaは関係する章があれば),"terms"[用語辞典のid](関係するもの),"faq"[3]({"q","a"}),"sources"[2以上]({"text","url"})}`。本文（paras合計）は1000〜2000字。
3. 出典: 資格・制度は厚生労働省・文部科学省・日本心理研修センター・日本臨床心理士資格認定協会・日本心理学会などの公式ページ。分野の説明は日本心理学会・APA 等の学会、代表的な教科書的レビュー論文。必ず開いて、書く内容（年・制度・人名・定義）が書かれていることを確認する。確認できないことは書かない。他サイトの文章を写さない。
4. 制度は変わることがあるので、資格の受験資格・ルートは「〇〇によると（2026年時点）」と出典を示し、細かい条件は公式ページへ誘導する。特定の資格・講座・書籍の宣伝や、有料サービスへの誘導はしない。
5. `python3 media/shinri_pages.py --check` が `check ok` になるまで直し、`python3 media/shinri_pages.py` でビルドする。
6. `media/shinri-guides.json` と `sites/shinri/` だけを commit（`日常の心理学: ガイド N件（{id, ...}）`）して `git push origin main`。
7. 報告: 作ったページのURL（`https://shinri.seadice.win/guide/{id}/`）、残り件数。
