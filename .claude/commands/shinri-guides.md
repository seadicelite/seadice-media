---
description: ゼロから学ぶ心理学に「心理学の独学Q&A」「分野別の入門」ページを書く。ルーティンから実行される
argument-hint: [件数 例: 4]
---

# /shinri-guides — 独学Q&A・分野入門ページを書く

対象: `media/shinri-guides.json`（配列）。ページは `python3 media/shinri_pages.py` が `/guide/{id}/` に生成する（HTMLを手で編集しない）。
目的: 心理学を独学しようとする人が検索する質問に1ページずつ答え、AI検索に「心理学を無料で学べるサイト」として引用されること。


## 出典の確認方法（クラウド実行の制約。最重要・2026-10-03〜）

自動実行の環境からは、厚生労働省・学会・Crossref・Wikipedia・出版社サイトなど多くのサイトがネットワーク制限で開けない。開けるのは **PubMed Central（`https://pmc.ncbi.nlm.nih.gov/articles/PMC.../`）の論文ページ** と doi.org のリダイレクトだけ。したがって:

- **本文に書く事実（数値・年・人名・定義・研究の結果）は、PMC の論文ページを実際に開いて本文で確認したものだけにする。** 出典のうち少なくとも2件は PMC の論文（URLは `https://pmc.ncbi.nlm.nih.gov/articles/PMC{番号}/`）にする。
- PMC で全文が読めない古典（原典の論文・書籍）は、出典欄に「背景」として載せてよいが、その古典を根拠にした具体的な数値や細部は、PMC の論文で同じ内容が確認できた場合だけ書く。
- 検索結果のスニペット、要旨の推測、他サイトの要約を根拠にしない。開けなかった出典は使わない。
- 出典の `text` は必ず「著者 (年). 論文タイトル. 掲載誌, 巻(号), ページ.」の形で、**論文タイトルを省略しない**（照合に使うため）。DOI は実在を確認したものだけを書く。分からなければ DOI を書かず PMC の URL を使う。
- 日本の制度（資格・法律・相談窓口など）は確認できないので、自動実行では扱わない（必要なときは手元で人が確認して書く）。

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
10. （自動実行では扱わない：`psychology-certifications` 心理学の資格・検定。日本の制度のため手元で確認して書く）

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
3. 出典: 上の「出典の確認方法」に従い、PMC で全文を読める代表的なレビュー論文を中心にする。日本の制度の説明は書かない（必要なら「詳しくは公式サイトで」と案内するだけにする）。必ず開いて、書く内容（年・制度・人名・定義）が書かれていることを確認する。確認できないことは書かない。他サイトの文章を写さない。
4. 制度は変わることがあるので、資格の受験資格・ルートは「〇〇によると（2026年時点）」と出典を示し、細かい条件は公式ページへ誘導する。特定の資格・講座・書籍の宣伝や、有料サービスへの誘導はしない。
5. `python3 media/shinri_pages.py --check` が `check ok` になるまで直し、`python3 media/shinri_pages.py` でビルドする。
6. `media/shinri-guides.json` と `sites/shinri/` だけを commit（`ゼロから学ぶ心理学: ガイド N件（{id, ...}）`）して `git push origin main`。
7. 報告: 作ったページのURL（`https://shinri.seadice.win/guide/{id}/`）、残り件数。
