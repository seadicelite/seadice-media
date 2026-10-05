#!/usr/bin/env python3
"""SEADICE STUDY 共通エンジン。1分野1サイトの無料学習サイト（siteType: course）を生成・検査する。
最上位のルールは docs/study.md。デザイン・学習機能の修正はこのファイル1か所で行い、全サイトに反映する。
記事エンジン(build.py / /media)の対象外。shinri（ゼロから学ぶ心理学）は対象外で、shinri_pages.py が生成する。

使い方:
  python3 media/study.py {slug}            sites/{slug}/ を生成（生成後チェックも実行）
  python3 media/study.py {slug} --check    データ検査（study.md 14章A）＋一時ディレクトリに生成して生成後チェック。サイトは書き換えない
  python3 media/study.py --all [--check]   media/study-sites.json の engine が "study"（既定）の全サイト
  追加オプション: --course FILE（講座JSONを差し替える。表示確認用） --out DIR（出力先を差し替える）

読み込むファイル:
  media/{slug}.json            設定（下のキー一覧）
  media/{slug}-course.json     講座 {title, desc, chapters[{no,id,title,desc,plan[],care?,lessons[],test?[]}], mock?}
                               test: 章末テスト用の新しい問題 [{q,choices,a,exp,ref(章内のレッスンid),apply?}]。レッスンの確認問題と合わせて出題する
                               mock: 総まとめテスト {title, label?(リンク名。既定「模擬試験」), date, lead, parts[{name,desc,questions[{…,ref}]}]}
  media/{slug}-glossary.json   用語辞典 [{id, term, en, field, def, detail?[], example?, faq?[{q,a}], sources?[], date?}]
  media/{slug}-guides.json     任意。今は --check の対象のみ（ページは未生成）
  media/study-sites.json       全講座の一覧 [{slug, name, url, live, engine?}]。フッター「SEADICE STUDYの他の講座」に live:true を並べる

設定JSON（media/{slug}.json）のキー。文字列中の {course}（講座名）{chapters}（章数）{lessons}（公開レッスン数）{terms}（用語数）{name}（サイト名）は置き換える。
「HTML可」と書いたキー以外はプレーンテキスト（エスケープして出力）。
  必須（既存）:
    name, path, url, tagline, description, lead, titleSuffix, faq[[q,a]]
  見た目:
    theme        {accent, accentDark, soft, softDark, ink?(既定#FFFFFF), inkDark}  CSS変数 --accent / --soft / --accent-ink を作る
    icon         ファビコンの1文字（例: 貿）
    logoSub      ロゴ横の小見出し（例: 貿易実務を無料で学ぶ）
    extraNav     [{href, label, footer}] ヘッダーとフッターに足す分野固有のリンク（例: 模擬試験 /c/）
  講座ページ:
    courseKicker     講座ページの小見出し。講座ページの title にも使う（例: 無料の貿易実務講座）
    courseLead       講座ページのリード文
    courseFeatures   [li] 「この講座の特徴」の2項目め以降（1項目めはレッスンの型の説明でエンジン側が出す）
    courseContents   「講座の目次」直下の結論文
    lessonTag        レッスンページの title に入る講座の略称（例: 貿易実務入門）
    keywordsNote     レッスンのキーワード欄（旧形式）の説明文
    mockNote         講座の模擬試験ページの注意書き
    careHtml         HTML可。course.json の chapters[].care が true の章の全レッスンに出す相談先の枠
  用語辞典:
    glossaryName     用語辞典の名前（例: 貿易用語辞典）
    glossaryLead     用語辞典ページのリード文
    glossaryDesc     用語辞典ページの meta description
    glossaryCtaHead  用語辞典の末尾の案内枠の見出し
    glossaryCtaHtml  HTML可。その本文（講座へのリンクを含める）
  トップ:
    homeCourseAnswer   トップ「無料講座」直下の結論文
    homeGlossaryAnswer トップ「用語辞典」直下の結論文
    homeTerms          [用語id] トップに並べる入門用語
  信頼ページ・AI向け:
    trust        {"about": [[見出し, [段落(HTML可)]]], "sources": [...], "disclaimer": [...]}
    llmsIntro    [行] llms.txt の冒頭の説明文
  任意:
    practice     [[名前, URL, 説明]] 講座の外の演習ツール
    exam         本番形式の模擬試験コーナー（/{path}）。{path, kicker, h1, meta, lead, start, overview[li], note, crumb, title, desc, appName, faq[[q,a]]}
    forbidWords  [語] 他分野の文言の混入検査。生成した全ページにこれらの語があればエラー

レッスンの形式（study.md 5章）:
  新形式 question / review / sections / figure / apply / keep / terms / quiz[apply] / sources を、study.md 4章の並びで表示する。
         figure.kind は table（head, rows）/ svg（svg）/ swatches（items[{name,hex}]）。figure.after でどのセクションの後に置くか（0始まり、既定は最後）。
         本文の **語** は太字。
  旧形式 goals / summary を持つレッスン。従来どおりの並びで表示し、--check では「旧形式」の警告にとどめる。

学習機能（study.md 8章の優先1）: sites/{slug}/study.js（defer、外部リクエストなし）。保存は localStorage のみ・すべて try/catch。
クイズ（問題が100問以上ある講座）: /quiz/ と quiz.js、問題データ /quiz/data.json。10問チャレンジ・サバイバル・章別・苦手をつぶす。
  設定 quizName（例: 犯罪学クイズ）、quizRanks（成績の称号4段階）。間違えた記録は study.js と共通（同じ問題id）。
  進み具合（読み終えたボタン・確認問題を解き終えたら既読、講座ページとトップに既読と「続きから読む」）、
  確認問題の正誤と解説・間違えた問題の記録、/review/（間違えた問題だけを解き直す）、/cards/（用語の暗記カード、ライトナー方式）。
  JSが無効でも本文は読め、確認問題は <details> で答えを見られる。"""
import base64, html, json, re, shutil, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = html.escape
PUBLISHER = {"@type": "Organization", "@id": "https://seadice.win/#organization", "name": "SEADICE", "url": "https://seadice.win/"}
CUR = ' aria-current="page"'
ARTICLES = {}  # 姉妹メディアの記事（今は無し）

# ---------------- サイトの読み込み ----------------
SLUG = CFG = COURSE = TERMS = GUIDES = None
NAME = URL = CURL = UPDATED = None
OUT = None
LESSONS = []
N_LESSONS = N_CH = 0
SITES = []


def load(slug, course_file=None, out=None):
    global SLUG, CFG, COURSE, TERMS, GUIDES, NAME, URL, CURL, UPDATED, OUT, LESSONS, N_LESSONS, N_CH, SITES
    SLUG = slug
    CFG = json.loads((ROOT / f"media/{slug}.json").read_text())
    COURSE = json.loads(Path(course_file).read_text() if course_file else (ROOT / f"media/{slug}-course.json").read_text())
    TERMS = json.loads((ROOT / f"media/{slug}-glossary.json").read_text())
    gp = ROOT / f"media/{slug}-guides.json"
    GUIDES = json.loads(gp.read_text()) if gp.exists() else []
    NAME, URL = CFG["name"], CFG["url"]
    CURL = f"{URL}course/"
    OUT = Path(out) if out else ROOT / CFG["path"]
    LESSONS = [(ch, l) for ch in COURSE["chapters"] for l in ch["lessons"]]
    N_LESSONS, N_CH = len(LESSONS), len(COURSE["chapters"])
    # サイト全体の更新日 = 最新レッスンの日付
    UPDATED = max([l.get("date", "2026-10-01") for _, l in LESSONS] + [CFG.get("updated", "2026-10-01")])
    sp = ROOT / "media/study-sites.json"
    SITES = json.loads(sp.read_text()) if sp.exists() else []


def fmt(s):
    for k, v in (("course", COURSE["title"]), ("chapters", str(N_CH)), ("lessons", str(N_LESSONS)), ("terms", str(len(TERMS))), ("name", NAME)):
        s = s.replace("{" + k + "}", v)
    return s


def T(key, default=""):
    """設定のプレーンテキスト（置き換え＋エスケープ済み）"""
    return E(fmt(CFG.get(key, default)))


def H(key, default=""):
    """設定のHTML可の文字列（置き換えの値だけエスケープ）"""
    s = CFG.get(key, default)
    for k, v in (("course", COURSE["title"]), ("chapters", str(N_CH)), ("lessons", str(N_LESSONS)), ("terms", str(len(TERMS))), ("name", NAME)):
        s = s.replace("{" + k + "}", E(v))
    return s


def is_new(l):
    return "keep" in l or "question" in l


# ---------------- 見た目 ----------------
BASE_CSS = """*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#F7F5F0;--paper:#FFFFFF;--text:#1C1E24;--sub:#4A4F5C;--muted:#646A78;--line:#E4DFD5;--accent:%(accent)s;--accent-ink:%(ink)s;--soft:%(soft)s;--note:#FFF6DA;--ok:#1F7A4D;--ng:#B45309}
@media(prefers-color-scheme:dark){:root{--bg:#111118;--paper:#1A1A24;--text:#ECEBF2;--sub:#C2C0CF;--muted:#A3A0B4;--line:#2D2C3A;--accent:%(accentDark)s;--accent-ink:%(inkDark)s;--soft:%(softDark)s;--note:#2B2717;--ok:#6FD3A0;--ng:#F2B36A}}
html{-webkit-text-size-adjust:100%%}body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Hiragino Sans','Noto Sans JP','Helvetica Neue',sans-serif;font-size:17px;line-height:1.9}
a{color:var(--accent)}a:focus-visible,summary:focus-visible,button:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:4px}
header.site{position:sticky;top:0;z-index:10;background:color-mix(in srgb,var(--bg) 88%%,transparent);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
header.site .in{max-width:960px;margin:0 auto;padding:10px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.logo{font-weight:800;font-size:17px;color:var(--text);text-decoration:none;letter-spacing:.02em}.logo small{font-size:12px;color:var(--muted);font-weight:600;margin-left:8px;letter-spacing:.08em}
header.site nav{display:flex;gap:4px;flex-wrap:wrap}header.site nav a{font-size:14px;color:var(--sub);text-decoration:none;padding:8px 10px;border-radius:8px}header.site nav a:hover,header.site nav a[aria-current]{background:var(--soft);color:var(--accent)}
main{max-width:760px;margin:0 auto;padding:28px 16px 72px}main.wide{max-width:960px}
.crumb{font-size:13px;color:var(--muted);margin-bottom:14px}.crumb a{color:var(--muted);text-decoration:none}.crumb a:hover{text-decoration:underline}
.kicker{display:inline-block;font-size:13px;font-weight:700;color:var(--accent);background:var(--soft);border-radius:999px;padding:3px 12px;margin-bottom:12px}
h1{font-size:clamp(26px,6vw,36px);line-height:1.35;font-weight:800;letter-spacing:.01em;margin-bottom:10px}
.updated{font-size:13px;color:var(--muted);margin-bottom:22px}
.lead{font-size:18px;color:var(--sub);margin:0 0 28px}
h2{font-size:23px;line-height:1.45;font-weight:800;margin:56px 0 12px;padding-top:6px}h2 .n{display:block;font-size:13px;color:var(--accent);letter-spacing:.12em;margin-bottom:2px}
h3{font-size:18px;font-weight:800;margin:28px 0 8px}
p{margin:14px 0}.answer{font-weight:700;color:var(--text);border-left:4px solid var(--accent);padding:2px 0 2px 14px;margin:10px 0 18px}strong{font-weight:800;background:linear-gradient(transparent 62%%,var(--soft) 62%%)}
.box{background:var(--paper);border:1px solid var(--line);border-radius:16px;padding:20px 22px;margin:20px 0}.box h2,.box .bt{font-size:15px;font-weight:800;color:var(--accent);letter-spacing:.06em;margin:0 0 8px;padding:0}
.box ul,.box ol{padding-left:22px}.box li{margin:6px 0}
.box.key{background:var(--soft);border-color:transparent}.box.note{background:var(--note);border-color:transparent;font-size:15px}
.box.ask .q{font-size:19px;font-weight:800;line-height:1.6;margin:0}.box.ask .hint,.box.apply .hint{font-size:14px;color:var(--muted);margin:8px 0 0}.box.apply{border:2px dashed var(--line)}.box.apply p{margin:0}
.btns{display:flex;flex-wrap:wrap;gap:10px;margin:8px 0 32px}.btn{display:inline-block;font:inherit;font-size:16px;font-weight:700;text-decoration:none;border:0;cursor:pointer;border-radius:12px;padding:12px 20px;background:var(--accent);color:var(--accent-ink)}.btn.sub{background:var(--paper);color:var(--accent);border:1px solid var(--line)}
.grid{display:grid;gap:12px;grid-template-columns:1fr}@media(min-width:680px){.grid{grid-template-columns:1fr 1fr}}
.card{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 18px;text-decoration:none;color:var(--text)}a.card:hover{border-color:var(--accent)}
.card b{display:block;font-size:17px;line-height:1.5}.card span{display:block;font-size:14px;color:var(--sub);line-height:1.7;margin-top:4px}.card small{display:block;font-size:12px;font-weight:700;color:var(--accent);letter-spacing:.1em;margin-bottom:4px}
.card.soon{opacity:.75}.card .st{display:inline-block;font-size:12px;color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:1px 10px;margin-top:8px}
ol.lessons{list-style:none;margin:10px 0 0}ol.lessons li{margin:0;border-top:1px solid var(--line)}ol.lessons a{display:flex;gap:10px;padding:10px 2px;text-decoration:none;color:var(--text);font-size:15px;line-height:1.6}ol.lessons a:hover{color:var(--accent)}ol.lessons .no{flex:0 0 42px;color:var(--muted);font-variant-numeric:tabular-nums}
ol.lessons a[aria-current]{color:var(--accent);font-weight:700}ol.lessons .ck{margin-left:auto;flex:0 0 auto;font-size:12px;font-weight:700;color:var(--ok);border:1px solid currentColor;border-radius:999px;padding:0 8px;align-self:center}
.card ol.lessons span.no,.card ol.lessons span.ck{display:inline;margin-top:0}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.chips a{font-size:14px;color:var(--text);text-decoration:none;background:var(--paper);border:1px solid var(--line);border-radius:999px;padding:8px 14px}.chips a:hover{border-color:var(--accent);color:var(--accent)}
table{width:100%%;border-collapse:collapse;margin:16px 0;font-size:15px;background:var(--paper)}th,td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top;line-height:1.7}th{background:var(--soft);font-weight:700}
@media(max-width:640px){table,tbody,tr,td{display:block;width:100%%}thead{display:none}tr{border:1px solid var(--line);border-radius:12px;margin:12px 0;padding:6px 0;background:var(--paper)}td{border:0;padding:5px 14px}td::before{content:attr(data-l);display:block;font-size:12px;color:var(--muted)}}
figure.fig{margin:24px 0}figure.fig figcaption{font-size:14px;color:var(--muted);margin-top:6px}figure.fig svg{display:block;width:100%%;height:auto;max-width:640px;margin:0 auto}
ul.sw{list-style:none;display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px}ul.sw li{font-size:14px;line-height:1.5}ul.sw span{display:block;height:56px;border-radius:10px;border:1px solid var(--line);margin-bottom:4px}ul.sw code{display:block;font-size:12px;color:var(--muted)}
.term{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0}.term .tt{font-size:17px;font-weight:800;line-height:1.5}.term .en{font-size:13px;color:var(--muted);font-weight:600;margin-left:6px}.term p{margin:6px 0 0;font-size:15px;color:var(--sub)}.term .more{display:inline-block;margin-top:8px;font-size:14px}
details{background:var(--paper);border:1px solid var(--line);border-radius:14px;margin:12px 0;padding:0}summary{cursor:pointer;padding:14px 18px;font-weight:700;font-size:16px;line-height:1.6}details>div,details>p{padding:0 18px 16px;font-size:15px;color:var(--sub)}
.qz{background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0}.qz .qq{font-weight:700;margin:0 0 10px;line-height:1.7}.qz .src-l{font-size:12px;color:var(--muted);font-weight:600;display:block;margin-bottom:2px}
.qz .chs{display:grid;gap:8px}.qz button{font:inherit;font-size:15px;text-align:left;line-height:1.6;color:var(--text);background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px 14px;cursor:pointer}.qz button:hover:not(:disabled){border-color:var(--accent)}
.qz button:disabled{cursor:default}.qz button.ok{border:2px solid var(--ok);background:color-mix(in srgb,var(--ok) 12%%,var(--paper))}.qz button.ng{border:2px solid var(--ng);background:color-mix(in srgb,var(--ng) 10%%,var(--paper))}
.qz .res{font-weight:800;margin:10px 0 0}.qz .res:empty{display:none}.qz .res.ok{color:var(--ok)}.qz .res.ng{color:var(--ng)}.qz details{margin:10px 0 0;border-style:dashed}.qz details summary{font-size:14px;color:var(--accent);padding:10px 14px}.qz details p{padding:0 14px 12px;margin:0;font-size:15px;color:var(--sub)}.qz .ans{color:var(--ok);font-weight:700}
.score{font-size:17px;font-weight:800;margin:16px 0 0}.score:empty{display:none}.score ul{font-size:15px;font-weight:400;margin:8px 0 0 20px}
.review{background:var(--soft);border-radius:16px;padding:18px 20px;margin:20px 0}.review .bt{font-size:15px;font-weight:800;color:var(--accent);letter-spacing:.06em;margin:0 0 4px}.review>p{font-size:14px;color:var(--sub);margin:0 0 6px}
.pn{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:40px 0 0}.pn a{display:block;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:12px 16px;text-decoration:none;color:var(--text);font-size:14px;line-height:1.5}.pn a:hover{border-color:var(--accent)}.pn small{display:block;font-size:12px;color:var(--accent);font-weight:700}.pn .nx{text-align:right;grid-column:2}
@media(max-width:520px){.pn{grid-template-columns:1fr}.pn .nx{grid-column:1}}
.final{margin:48px 0 0;background:var(--paper);border:2px solid var(--accent);border-radius:20px;padding:22px 20px 10px}.final h2{margin:0 0 10px;padding:0}.final .fk{font-size:13px;font-weight:800;color:var(--accent);letter-spacing:.12em;margin:0 0 4px}.final details{background:var(--bg)}
.done{margin:24px 0 0;background:var(--soft);border-radius:20px;padding:22px 20px}.done .dt{font-size:20px;font-weight:800;margin:0}.done .dd{font-size:15px;color:var(--sub);margin:6px 0 0}.done details{background:var(--paper)}
.mark{margin:14px 0 0}.mark[aria-pressed=true]{background:var(--paper);color:var(--ok);border:2px solid var(--ok)}
.src{margin-top:48px;padding-top:18px;border-top:1px solid var(--line)}.src h2{font-size:15px;margin:0 0 8px;color:var(--muted)}.src li{font-size:13px;color:var(--muted);margin:6px 0 6px 20px;line-height:1.7;word-break:break-word}.src a{color:var(--muted)}
details.srcs{margin-top:40px}details.srcs summary{font-size:15px;color:var(--muted)}details.srcs ol{padding:0 18px 14px 40px}details.srcs li{font-size:13px;color:var(--muted);margin:6px 0;line-height:1.7;word-break:break-word}details.srcs a{color:var(--muted)}
.ex li{margin:6px 0}.ex small{color:var(--muted)}
.resume{background:var(--paper);border:2px solid var(--accent);border-radius:16px;padding:16px 20px;margin:0 0 28px}.resume p{margin:0 0 8px;font-size:15px;color:var(--sub)}.resume .btns{margin:0}
.fc{background:var(--paper);border:2px solid var(--accent);border-radius:20px;padding:28px 22px;text-align:center;margin:20px 0}.fc .fw{font-size:26px;font-weight:800;line-height:1.4}.fc .fe{font-size:14px;color:var(--muted);margin:4px 0 0}.fc .fd{font-size:16px;color:var(--sub);text-align:left;margin:18px 0 0}.fc .btns{justify-content:center;margin:20px 0 0}.fc .fn{font-size:13px;color:var(--muted);margin:16px 0 0}
footer.site{border-top:1px solid var(--line);padding:28px 16px;text-align:center;font-size:13px;color:var(--muted);line-height:2.2}footer.site a{color:var(--muted);margin:0 8px;text-decoration:none}footer.site a:hover{text-decoration:underline}footer.site .other{margin-top:10px}footer.site .other b{display:block;font-weight:700}
.hero{padding:20px 0 4px}.hero h1{font-size:clamp(32px,8vw,48px)}.hero .tag{font-size:16px;font-weight:700;color:var(--accent);margin-bottom:6px}
.stats{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:14px;color:var(--muted);margin:-12px 0 28px}.stats b{color:var(--text);font-size:16px}
.g-modes{display:grid;gap:12px;grid-template-columns:1fr;margin:8px 0 10px}@media(min-width:680px){.g-modes{grid-template-columns:1fr 1fr 1fr}}
.g-mode,.g-chb{font:inherit;text-align:left;cursor:pointer;color:var(--text);background:var(--paper);border:2px solid var(--line);border-radius:16px;padding:16px 18px;transition:transform .12s,border-color .12s}
.g-mode:hover:not(:disabled),.g-chb:hover{border-color:var(--accent);transform:translateY(-2px)}.g-mode:disabled{opacity:.6;cursor:default}
.g-mode b{display:block;font-size:19px;color:var(--accent)}.g-mode span{display:block;font-size:14px;color:var(--sub);line-height:1.6;margin-top:4px}.g-mode em{display:block;font-style:normal;font-size:13px;font-weight:700;color:var(--ok);margin-top:6px}.g-mode em:empty{display:none}
.g-mode[data-mode=ten]{background:var(--accent);border-color:var(--accent)}.g-mode[data-mode=ten] b,.g-mode[data-mode=ten] span,.g-mode[data-mode=ten] em{color:var(--accent-ink)}
.g-note{font-size:13px;color:var(--muted);margin:6px 0 0}
.g-chgrid{display:grid;gap:10px;grid-template-columns:1fr}@media(min-width:680px){.g-chgrid{grid-template-columns:1fr 1fr}}
.g-chb small{display:block;font-size:12px;font-weight:700;color:var(--accent);letter-spacing:.08em}.g-chb b{display:block;font-size:16px;line-height:1.5}
.g-rate{display:block;margin-top:8px}.g-rate i{display:block;height:6px;border-radius:3px;background:var(--accent);max-width:100%%}.g-rate em{display:block;font-style:normal;font-size:12px;color:var(--muted);margin-top:2px}
.g-head{display:flex;align-items:center;gap:14px;font-weight:800;font-variant-numeric:tabular-nums}.g-prog{color:var(--muted);font-size:14px}.g-pt{margin-left:auto;font-size:18px;color:var(--accent)}
.g-life{display:flex;gap:4px}.g-life i{width:14px;height:14px;border-radius:50%%;border:2px solid var(--ng)}.g-life i.on{background:var(--ng)}
.g-bar{height:8px;border-radius:4px;background:var(--line);margin:8px 0 16px;overflow:hidden}.g-bar i{display:block;height:100%%;background:var(--accent);transition:width .3s}
.g-card{background:var(--paper);border:2px solid var(--line);border-radius:20px;padding:22px 20px;position:relative}.g-src{font-size:12px;font-weight:700;color:var(--muted);letter-spacing:.06em;margin:0 0 6px}.g-q{font-size:19px;font-weight:800;line-height:1.65;margin:0 0 16px}
.g-chs{display:grid;gap:10px}.g-ch{font:inherit;font-size:16px;text-align:left;line-height:1.6;color:var(--text);background:var(--bg);border:2px solid var(--line);border-radius:14px;padding:12px 14px;cursor:pointer;display:flex;gap:12px;align-items:flex-start}
.g-ch b{flex:0 0 26px;height:26px;border-radius:50%%;background:var(--soft);color:var(--accent);font-size:14px;display:flex;align-items:center;justify-content:center;margin-top:1px}
.g-ch:hover:not(:disabled){border-color:var(--accent)}.g-ch:disabled{cursor:default}.g-ch.ok{border-color:var(--ok);background:color-mix(in srgb,var(--ok) 14%%,var(--paper))}.g-ch.ng{border-color:var(--ng);background:color-mix(in srgb,var(--ng) 12%%,var(--paper));animation:g-shake .3s}
.g-fb:empty{display:none}.g-fb{margin-top:16px}.g-ok,.g-ng{font-size:22px;font-weight:800;margin:0}.g-ok{color:var(--ok);animation:g-pop .35s}.g-ng{color:var(--ng)}.g-exp{font-size:15px;color:var(--sub);margin:8px 0}.g-read{font-size:14px;font-weight:700}.g-next{display:block;width:100%%;margin-top:16px}
.g-pop{position:absolute;top:14px;right:16px;font-size:13px;font-weight:800;letter-spacing:.1em;color:var(--accent-ink);background:var(--accent);border-radius:999px;padding:4px 12px;animation:g-pop .4s}
.g-res{text-align:center}.g-rank{font-size:15px;font-weight:800;color:var(--accent-ink);background:var(--accent);display:inline-block;border-radius:999px;padding:4px 16px;margin:4px 0 0;animation:g-pop .5s}.g-big{font-size:30px;font-weight:800;margin:10px 0 0}.g-sub{font-size:15px;color:var(--sub);margin:8px 0 0}
.g-miss{list-style:none;display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:10px 0 0}.g-miss a{display:inline-block;font-size:14px;border:1px solid var(--line);border-radius:999px;padding:6px 12px;text-decoration:none}.g-res .btns{justify-content:center;margin:20px 0 0}
@keyframes g-pop{0%%{transform:scale(.7);opacity:0}70%%{transform:scale(1.08)}100%%{transform:scale(1);opacity:1}}@keyframes g-shake{25%%{transform:translateX(-5px)}75%%{transform:translateX(5px)}}
@media(prefers-reduced-motion:reduce){.g-ok,.g-pop,.g-rank,.g-ch.ng{animation:none}.g-mode,.g-chb{transition:none}}
[hidden]{display:none!important}"""


def css():
    th = {"accent": "#0B6380", "accentDark": "#6CCBE3", "soft": "#E3F1F5", "softDark": "#1C2E36", "ink": "#FFFFFF", "inkDark": "#0E1A20"}
    th.update(CFG.get("theme", {}))
    return BASE_CSS % th


def favicon():
    color = CFG.get("theme", {}).get("accent", "#0B6380")
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="{color}"/>'
           f'<text x="32" y="44" font-size="34" font-family="-apple-system,sans-serif" font-weight="800" text-anchor="middle" fill="#fff">{E(CFG.get("icon", NAME[-1]))}</text></svg>')
    return f'<link rel="icon" type="image/svg+xml" href="data:image/svg+xml;base64,{base64.b64encode(svg.encode()).decode()}">'


# ---------------- 学習機能のJS（全サイト共通・外部リクエストなし） ----------------
STUDY_JS = r"""(function(){'use strict';
var KEY='study:'+(document.documentElement.getAttribute('data-site')||'x'),S=null,OK=true;
function load(){if(S)return S;try{S=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){S={};OK=false}S.read=S.read||{};S.miss=S.miss||{};S.cards=S.cards||{};return S}
function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){OK=false}}
function $(s,r){return(r||document).querySelectorAll(s)}
function esc(t){var d=document.createElement('i');d.textContent=t;return d.innerHTML}
function today(){return Math.floor((Date.now()-new Date().getTimezoneOffset()*6e4)/864e5)}
load();
/* 確認問題 */
function setupQuiz(z,onAnswer){var qs=$('.qz',z),n=0,ok=0,miss={};
qs.forEach(function(q){var bs=$('button',q),a=+q.dataset.a;bs.forEach(function(b,i){b.addEventListener('click',function(){if(q.dataset.done)return;q.dataset.done=1;n++;
var r=q.querySelector('.res'),id=q.dataset.q;if(i===a){ok++;r.textContent='正解です';r.className='res ok';if(id&&S.miss[id]){delete S.miss[id]}}
else{miss[q.dataset.h]=q.dataset.t;r.textContent='惜しい。正解は '+(a+1)+' です。解説を読んでみましょう';r.className='res ng';if(id)S.miss[id]={l:q.dataset.h,t:Date.now()}}
save();bs.forEach(function(x,j){x.disabled=true;if(j===a)x.classList.add('ok');else if(j===i)x.classList.add('ng')});var d=q.querySelector('details');d.open=true;d.querySelector('summary').textContent='解説';
if(onAnswer)onAnswer(q,i===a);
if(n===qs.length){var s=z.querySelector('.score');if(s){var k=Object.keys(miss),h=qs.length+'問中'+ok+'問正解。';
if(!k.length)h+='全問正解です。';else if(z.dataset.mode==='test')h+='次のレッスンを読み直すと、迷ったところがはっきりします。<ul>'+k.map(function(u){return '<li><a href="'+u+'">'+miss[u]+'</a></li>'}).join('')+'</ul>';
else if(z.dataset.mode!=='review'&&z.dataset.mode!=='redo')h+='迷った問題は<a href="/review/">復習ページ</a>に自動で入りました。';s.innerHTML=h}
if(z.dataset.l)markRead(z.dataset.l,true)}})})})}
/* 進み具合 */
function markRead(id,on){if(on){S.read[id]=today();S.last=id}else delete S.read[id];save();$('.mark').forEach(function(b){if(b.dataset.l===id)paint(b)})}
function paint(b){var on=!!S.read[b.dataset.l];b.setAttribute('aria-pressed',on?'true':'false');b.textContent=on?'読み終えました（もう一度押すとチェックを外せます）':'このレッスンを読み終えた'}
$('.mark').forEach(function(b){b.hidden=false;paint(b);b.addEventListener('click',function(){markRead(b.dataset.l,!S.read[b.dataset.l])})});
$('.quiz').forEach(function(z){if(z.dataset.mode!=='redo')setupQuiz(z)});
var items=$('li[data-l]'),seen={},order=[];items.forEach(function(li){var id=li.dataset.l;if(S.read[id]&&!li.querySelector('.ck')){var c=document.createElement('span');c.className='ck';c.textContent='読了';li.firstChild.appendChild(c)}
if(!seen[id]){seen[id]=1;order.push(li)}});
var rs=$('.resume');if(rs.length&&order.length){var done=order.filter(function(li){return S.read[li.dataset.l]}).length,mk=Object.keys(S.miss).length,at=0;
order.forEach(function(li,i){if(li.dataset.l===S.last)at=i+1});var nx=null;for(var i=0;i<order.length&&!nx;i++){var li=order[(at+i)%order.length];if(!S.read[li.dataset.l])nx=li}
if(done||mk)rs.forEach(function(r){var h='<p>'+order.length+'レッスン中 '+done+'レッスンを読みました。</p><div class="btns">';
if(nx)h+='<a class="btn" href="'+nx.querySelector('a').getAttribute('href')+'">続きから読む: '+esc(nx.dataset.s)+'</a>';
if(mk)h+='<a class="btn sub" href="/review/">間違えた問題を解き直す（'+mk+'問）</a>';r.innerHTML=h+'</div>';r.hidden=false})}
/* 復習ページ */
var rv=document.getElementById('redo');if(rv){var qs=$('.qz',rv),c=0;qs.forEach(function(q){if(S.miss[q.dataset.q]){q.hidden=false;c++}});
var m=document.getElementById('redo-msg');m.textContent=!OK?'このブラウザでは記録を保存できないため、復習リストを使えません。各章の章末テストで解き直せます。':(c?'解き直す問題は '+c+' 問です。正解した問題はリストから外れます。':'今は解き直す問題はありません。レッスンの確認問題で迷った問題が、ここに自動で集まります。');
setupQuiz(rv)}
/* 暗記カード（ライトナー方式: 間違えた語ほど早く出る） */
var cl=document.getElementById('cards');if(cl){var ds=[].slice.call($('details[data-t]',cl)),fc=document.getElementById('fc'),t0=today(),Q=[],cur=null,cnt=0,IV=[1,2,4,8,16];
function build(all){Q=ds.map(function(d,i){var st=S.cards[d.dataset.t];return{d:d,i:i,b:st?st.b:1.5,due:st?st.d:0}}).filter(function(x){return all||x.due<=t0}).sort(function(x,y){return x.b-y.b||x.due-y.due||x.i-y.i}).slice(0,20);cnt=0}
function show(){var f=fc;if(!Q.length){f.innerHTML='<p class="fw">今日のカードはここまでです</p><p class="fd">覚えていた語は、日をあけてまた出てきます。続けたいときは、全部の語からもう一度始められます。</p><div class="btns"><button type="button" class="btn" id="fc-all">全部の語でもう一度</button><a class="btn sub" href="/glossary/">用語辞典を見る</a></div>';
document.getElementById('fc-all').onclick=function(){build(true);show()};return}
cur=Q[0];var d=cur.d,w=d.querySelector('.tt').textContent,e=d.querySelector('.en').textContent,df=d.querySelector('p').textContent;
f.innerHTML='<p class="fw"></p><p class="fe"></p><p class="fd" hidden></p><div class="btns"><button type="button" class="btn" id="fc-show">意味を見る</button></div><div class="btns" hidden id="fc-r"><button type="button" class="btn" id="fc-ok">覚えていた</button><button type="button" class="btn sub" id="fc-ng">まだあやしい</button></div><p class="fn">残り '+Q.length+' 枚</p>';
f.querySelector('.fw').textContent=w;f.querySelector('.fe').textContent=e;f.querySelector('.fd').textContent=df;
document.getElementById('fc-show').onclick=function(){f.querySelector('.fd').hidden=false;this.parentNode.hidden=true;document.getElementById('fc-r').hidden=false;document.getElementById('fc-ok').focus()};
document.getElementById('fc-ok').onclick=function(){var b=Math.min(5,Math.floor(cur.b)+1);S.cards[cur.d.dataset.t]={b:b,d:t0+IV[b-1]};save();Q.shift();show()};
document.getElementById('fc-ng').onclick=function(){S.cards[cur.d.dataset.t]={b:1,d:t0};save();cur.b=1;Q.shift();Q.splice(Math.min(3,Q.length),0,cur);show()}}
cl.hidden=true;fc.hidden=false;document.getElementById('cards-note').hidden=false;build(false);show()}
})();"""


def quiz_html(items, mode="lesson", lid=None):
    """items: [(問題, レッスン番号, レッスンURL, 問題id)]。タップで採点（study.js）。JSなしでも「答えを見る」で答えを確認できる。"""
    out = ""
    for i, it in enumerate(items):
        q, no, href, qid = it
        chs = "".join(f'<button type="button">{j+1}. {E(c)}</button>' for j, c in enumerate(q["choices"]))
        tag = f'<span class="src-l">レッスン{no}から</span>' if mode != "lesson" else ('<span class="src-l">日常の場面で考える</span>' if q.get("apply") else "")
        out += (f'<div class="qz" data-a="{q["a"]}" data-q="{E(qid)}" data-h="{href}" data-t="レッスン{no}を読み直す"{" hidden" if mode == "redo" else ""}>{tag}<p class="qq">{"" if mode == "redo" else f"Q{i+1}. "}{E(q["q"])}</p>'
                f'<div class="chs">{chs}</div><p class="res" aria-live="polite"></p>'
                f'<details><summary>答えを見る</summary><p><span class="ans">正解: {q["a"]+1}. {E(q["choices"][q["a"]])}</span><br>{E(q["exp"])}</p></details></div>')
    return f'<div class="quiz" data-mode="{mode}"{f" data-l={chr(34)}{lid}{chr(34)}" if lid else ""}>{out}<div class="score" aria-live="polite"></div></div>'


def lesson_no(l):
    for ch in COURSE["chapters"]:
        for i, x in enumerate(ch["lessons"]):
            if x["id"] == l["id"]:
                return f'{ch["no"]}-{i+1}'


def complete(ch):
    return ch["lessons"] and len(ch["lessons"]) >= len(ch.get("plan", []))


def test_path(ch):
    return f'course/{ch["id"]}-test/'


def test_n(ch):
    return sum(len(x["quiz"]) for x in ch["lessons"]) + len(ch.get("test", []))


def mock_label():
    return COURSE["mock"].get("label", "模擬試験")


def crumbs(trail):
    items = [("HOME", "https://seadice.win/"), (NAME, URL)] + trail
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}


def nav_items():
    extra = [(x["href"], x["label"]) for x in CFG.get("extraNav", [])]
    quiz = [("/quiz/", "クイズ")] if has_quiz() else []
    return [("/course/", "講座")] + quiz + extra + [("/glossary/", "用語辞典"), ("/cards/", "暗記カード")]


def footer():
    extra = "".join(f'<a href="{x["href"]}">{E(x.get("footer", x["label"]))}</a>' for x in CFG.get("extraNav", []))
    others = [s for s in SITES if s.get("live") and s["slug"] != SLUG]
    other = ('<p class="other"><b>SEADICE STUDYの他の講座</b>' + "".join(f'<a href="{E(s["url"], quote=True)}">{E(s["name"])}</a>' for s in others) + '</p>') if others else ""
    quiz = f'<a href="/quiz/">{E(quiz_name())}</a>' if has_quiz() else ''
    return (f'<footer class="site"><p><a href="/course/">{E(COURSE["title"])}</a>{extra}<a href="/glossary/">{T("glossaryName")}</a>{quiz}<a href="/review/">間違えた問題の復習</a><a href="/cards/">暗記カード</a><br>'
            '<a href="/about/">このサイトについて</a><a href="/sources/">出典と検証の方法</a><a href="/disclaimer/">免責事項</a><a href="mailto:hi@seadice.win">お問い合わせ</a><br>'
            f'<a href="https://seadice.win/">運営: SEADICE</a></p>{other}</footer>')


def write(path, full_title, desc, body, graph, trail=(), og_type="article", current="", wide=False, noindex=False):
    url = f"{URL}{path}" if path else URL
    ld = {"@context": "https://schema.org", "@graph": graph + ([crumbs(list(trail))] if not noindex else [])}
    nav = "".join(f'<a href="{h}"{CUR if h == current else ""}>{E(t)}</a>' for h, t in nav_items())
    ldjson = json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
    bc = ""
    if trail:
        parts = ['<a href="https://seadice.win/">HOME</a>', f'<a href="/">{E(NAME)}</a>'] + [f'<a href="{u.replace(URL, "/")}">{E(n)}</a>' for n, u in trail[:-1]] + [E(trail[-1][0])]
        bc = f'<p class="crumb">{" / ".join(parts)}</p>'
    out = f'''<!DOCTYPE html>
<html lang="ja" data-site="{SLUG}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(full_title)}</title>
<meta name="description" content="{E(desc, quote=True)}">
{'<meta name="robots" content="noindex">' if noindex else f'<link rel="canonical" href="{url}">'}
<meta property="og:title" content="{E(full_title, quote=True)}">
<meta property="og:description" content="{E(desc, quote=True)}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{E(NAME, quote=True)}">
<meta property="og:locale" content="ja_JP">
<meta name="twitter:card" content="summary">
{'' if noindex else '<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large">'}
<meta name="color-scheme" content="light dark">
{FAV}
<script type="application/ld+json">{ldjson}</script>
<style>{CSS}</style>
<script src="/study.js" defer></script>
</head>
<body>
<header class="site"><div class="in"><a class="logo" href="/">{E(NAME)}<small>{T("logoSub")}</small></a><nav aria-label="サイト内">{nav}</nav></div></header>
<main{' class="wide"' if wide else ''}>
{bc}{body}
</main>
{footer()}
</body>
</html>
'''
    d = OUT / path if path else OUT
    d.mkdir(parents=True, exist_ok=True)
    (d / "index.html").write_text(out)
    return url


def faq_html(faq):
    return "".join(f"<details open><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q, a in faq)


def faq_ld(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def body_len(l):
    return sum(len(x.replace("**", "")) for sec in l["sections"] for x in sec["paras"])


def read_min(l):
    """日本語の黙読はおよそ毎分500字。問いと覚える3つで1分、問題1問と図表に各30秒を足す。"""
    qs = len(l.get("quiz", [])) + (1 if l.get("review") else 0)
    return max(3, round(body_len(l) / 500 + 1 + 0.5 * qs + (0.5 if l.get("figure") else 0)))


def rich_text(s):
    """エスケープしてから **語** を太字にする。"""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", E(s))


# ---------------- 検査（study.md 14章A） ----------------
SENT = re.compile(r"[^。？！]*[。？！]?")


def sentences(p):
    return [s for s in (x.strip() for x in SENT.findall(p.replace("**", ""))) if s]


def check_quiz(tag, qs, errs, need=None):
    for i, q in enumerate(qs):
        if not q.get("q") or not q.get("exp") or len(q.get("choices", [])) < 2: errs.append(f"{tag} 確認問題{i+1}の形式（q / choices / exp）")
        elif not isinstance(q.get("a"), int) or not 0 <= q["a"] < len(q["choices"]): errs.append(f"{tag} 確認問題{i+1}の正解番号が選択肢の範囲外")
        elif need and len(q["choices"]) != need: errs.append(f"{tag} 確認問題{i+1}は{need}択")


def check_new(tag, l, first_in_ch, errs, warns):
    for k in ("question", "sections", "keep", "quiz", "sources", "title", "short", "description", "date", "apply"):
        if not l.get(k): errs.append(f"{tag} {k}が空")
    if l.get("goals") or l.get("summary"): errs.append(f"{tag} 新形式に goals / summary が残っている（keep に置き換える）")
    if len(l.get("title", "")) > 40: errs.append(f"{tag} titleが{len(l['title'])}字（40字まで）")
    if len(l.get("description", "")) > 120: errs.append(f"{tag} descriptionが{len(l['description'])}字（120字まで）")
    secs = l.get("sections", [])
    if not 1 <= len(secs) <= 3: errs.append(f"{tag} セクションが{len(secs)}個（1〜3）")
    n = body_len(l) if secs else 0
    if not 600 <= n <= 1000: errs.append(f"{tag} 本文{n}字（600〜1000字）")
    for si, s in enumerate(secs):
        if not s.get("h") or not s.get("answer") or not s.get("paras"): errs.append(f"{tag} セクション{si+1}に h / answer / paras が無い")
        bold = sum(x.count("**") for x in s.get("paras", []) + [s.get("answer", "")]) // 2
        if bold > 1: errs.append(f"{tag} セクション{si+1}の太字が{bold}か所（1か所まで）")
        for pi, p in enumerate(s.get("paras", [])):
            ss = sentences(p)
            if len(ss) > 3: errs.append(f"{tag} セクション{si+1}段落{pi+1}が{len(ss)}文（3文まで）")
            for x in ss:
                if len(x) > 80: errs.append(f"{tag} 80字を超える文（{len(x)}字）: {x[:30]}…")
    if len(l.get("keep", [])) != 3: errs.append(f"{tag} keepが{len(l.get('keep', []))}個（ちょうど3）")
    if len(l.get("terms", [])) > 3: errs.append(f"{tag} termsが{len(l['terms'])}語（3語まで）")
    for t in l.get("terms", []):
        if not (t.get("ja") and t.get("en") and t.get("def")): errs.append(f"{tag} terms の ja / en / def が空")
    qz = l.get("quiz", [])
    if len(qz) != 3: errs.append(f"{tag} quizが{len(qz)}問（3問）")
    if not any(q.get("apply") for q in qz): errs.append(f"{tag} quizに apply:true（日常の場面への応用）が無い")
    check_quiz(tag, qz, errs)
    if len(l.get("sources", [])) < 2: errs.append(f"{tag} 出典が2件未満")
    for s in l.get("sources", []):
        if not s.get("text") or not str(s.get("url", "")).startswith("http"): errs.append(f"{tag} 出典の text / url が不正")
    if l.get("review"): check_quiz(tag + " review", [l["review"]], errs)
    elif not first_in_ch: errs.append(f"{tag} review（前のレッスンの復習1問）が無い")
    f = l.get("figure")
    if not f: warns.append(f"{tag} 図か表（figure）が無い")
    else:
        k = f.get("kind")
        if k == "table":
            if not f.get("head") or not f.get("rows") or any(len(r) != len(f["head"]) for r in f["rows"]): errs.append(f"{tag} figure(table) の head / rows の列数が合わない")
        elif k == "svg":
            sv = f.get("svg", "")
            if not sv.lstrip().startswith("<svg") or re.search(r"<script|\son\w+\s*=|(?:href|src)\s*=\s*[\"']?https?:", sv, re.I): errs.append(f"{tag} figure(svg) は <svg> で始まり、script・イベント属性・外部参照を含めない")
        elif k == "swatches":
            if not f.get("items") or any(not re.fullmatch(r"#[0-9A-Fa-f]{6}", x.get("hex", "")) or not x.get("name") for x in f["items"]): errs.append(f"{tag} figure(swatches) の items は [{{name, hex(#RRGGBB)}}]")
        else: errs.append(f"{tag} figure.kind は table / svg / swatches")
        if not f.get("caption"): errs.append(f"{tag} figure.caption が空")


def check_data():
    errs, warns, ids = [], [], set()
    for ch in COURSE["chapters"]:
        for li, l in enumerate(ch["lessons"]):
            tag = f'{ch["no"]}:{l.get("id")}'
            if l.get("id") in ids: errs.append(f"{tag} id重複")
            ids.add(l.get("id"))
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", l.get("id", "")): errs.append(f"{tag} id は英小文字・数字・ハイフン")
            if "{{" in json.dumps(l, ensure_ascii=False): errs.append(f"{tag} プレースホルダが残っている")
            if is_new(l):
                check_new(tag, l, li == 0, errs, warns)
            else:
                warns.append(f"{tag} 旧形式（goals / summary）。新形式（study.md 5章）への書き直し候補")
                for k in ("date", "title", "short", "description", "goals", "summary", "sections", "terms", "quiz", "sources"):
                    if not l.get(k): errs.append(f"{tag} {k}が空")
                if len(l.get("sources", [])) < 2: errs.append(f"{tag} 出典が2件未満")
                check_quiz(tag, l.get("quiz", []), errs, need=3)
            for e in l.get("examples", []):
                if e["slug"] not in ARTICLES: errs.append(f'{tag} examplesの記事slugが存在しない: {e["slug"]}')
    gids = set()
    for g in GUIDES:
        tag = f'guide {g.get("id")}'
        if g["id"] in gids: errs.append(f"{tag} id重複")
        gids.add(g["id"])
        if g.get("kind") not in ("qa", "field"): errs.append(f"{tag} kindはqaかfield")
        for k in ("title", "lead", "sections", "sources", "date"):
            if not g.get(k): errs.append(f"{tag} {k}が空")
    tids = set()
    for t in TERMS:
        if t["id"] in tids: errs.append(f'用語 {t["id"]} id重複')
        tids.add(t["id"])
        if t.get("detail") and not rich(t): errs.append(f'用語 {t["id"]} は detail があるが、個別ページの条件（detail400字以上・sources・faq）を満たしていない')
        if not re.match(r"^[^。]{1,60}とは、", t["def"]): errs.append(f'用語 {t["id"]} の定義が「〇〇とは、」で始まっていない')
    for i in CFG.get("homeTerms", []):
        if i not in tids: errs.append(f"設定 homeTerms の用語idが存在しない: {i}")
    for k in ("name", "path", "url", "tagline", "description", "lead", "titleSuffix", "faq", "logoSub", "courseKicker", "courseLead", "courseContents",
              "lessonTag", "keywordsNote", "glossaryName", "glossaryLead", "glossaryDesc", "glossaryCtaHead", "glossaryCtaHtml",
              "homeCourseAnswer", "homeGlossaryAnswer", "trust", "llmsIntro", "theme", "icon"):
        if not CFG.get(k): errs.append(f"設定 media/{SLUG}.json に {k} が無い")
    if any(c.get("care") for c in COURSE["chapters"]) and not CFG.get("careHtml"): errs.append("care の章があるのに設定に careHtml が無い")
    for c in COURSE["chapters"]:
        cl = {l["id"] for l in c["lessons"]}
        check_quiz(f'第{c["no"]}章 章末テスト', c.get("test", []), errs)
        for i, q in enumerate(c.get("test", [])):
            if q.get("ref") not in cl: errs.append(f'第{c["no"]}章 章末テスト Q{i+1} の ref（章内のレッスンid）が存在しない: {q.get("ref")}')
        if c.get("test") and not complete(c): errs.append(f'第{c["no"]}章 は未完成なのに章末テストの問題がある')
    m = COURSE.get("mock")
    if m:
        lids = {l["id"] for _, l in LESSONS}
        for p in m["parts"]:
            for i, q in enumerate(p["questions"]):
                check_quiz(f'模擬試験 {p["name"]} Q{i+1}', [q], errs)
                if q.get("ref") not in lids: errs.append(f'模擬試験 {p["name"]} Q{i+1} の ref（レッスンid）が存在しない: {q.get("ref")}')
    return errs, warns


def check_output(out):
    """生成後チェック: 内部リンク切れ・h1が1つ・JSON-LDのパース・他分野の文言の混入。"""
    errs = []
    forbid = CFG.get("forbidWords", [])
    # フッター「SEADICE STUDYの他の講座」に並ぶ講座名は混入ではないので、検査の前に取り除く
    sp = ROOT / "media/study-sites.json"
    names = [x["name"] for x in json.loads(sp.read_text())] if sp.exists() else []
    def strip_names(t):
        for n in names: t = t.replace(n, " ")
        return t
    files = sorted(out.rglob("*.html"))
    for f in files:
        rel = f.relative_to(out)
        if rel.parts and rel.parts[0] in {x["href"].strip("/").split("/")[0] for x in CFG.get("extraNav", [])} and len(rel.parts) > 2:
            continue  # 分野固有の静的アプリ（例: /c/exam/ のFlutter）は対象外
        s = f.read_text()
        n1 = len(re.findall(r"<h1[\s>]", s))
        if n1 != 1: errs.append(f"{rel}: h1が{n1}個")
        for js in re.findall(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
            try: json.loads(js)
            except Exception as e: errs.append(f"{rel}: JSON-LDがパースできない ({e})")
        for href in re.findall(r'(?:href|src)="(/[^"#?]*)', s):
            if href.startswith("//"): continue
            p = out / href.lstrip("/")
            if not (p / "index.html").exists() and not (p.is_file()):
                errs.append(f"{rel}: 内部リンク切れ {href}")
        txt = strip_names(re.sub(r"<[^>]+>", " ", s))
        for w in forbid:
            if w in txt: errs.append(f"{rel}: 他分野の文言「{w}」が残っている")
    for f in ("llms.txt",):
        p = out / f
        if p.exists():
            for w in forbid:
                if w in strip_names(p.read_text()): errs.append(f"{f}: 他分野の文言「{w}」が残っている")
    js = out / "study.js"
    if js.exists() and js.stat().st_size > 10 * 1024: errs.append(f"study.js が {js.stat().st_size} バイト（10KB以内）")
    js = out / "quiz.js"
    if js.exists() and js.stat().st_size > 12 * 1024: errs.append(f"quiz.js が {js.stat().st_size} バイト（12KB以内）")
    return sorted(set(errs)), len(files)


def lurl(l):
    return f"{CURL}{l['id']}/"


# ---------------- 講座 ----------------
def course_ld():
    return {"@type": "Course", "@id": CURL + "#course", "name": COURSE["title"], "description": COURSE["desc"], "url": CURL, "inLanguage": "ja",
            "provider": PUBLISHER, "isAccessibleForFree": True, "educationalLevel": "初級",
            "offers": {"@type": "Offer", "price": 0, "priceCurrency": "JPY", "category": "Free"},
            "hasCourseInstance": {"@type": "CourseInstance", "courseMode": "Online", "courseWorkload": f"PT{max(N_LESSONS, 1) * 10}M"},
            "syllabusSections": [{"@type": "Syllabus", "name": f'第{c["no"]}章 {c["title"]}', "description": c["desc"]} for c in COURSE["chapters"]]}


def lesson_li(c, i, l, current=None):
    return f'<li data-l="{l["id"]}" data-s="{E(l["short"], quote=True)}"><a href="/course/{l["id"]}/"{CUR if current == l["id"] else ""}><span class="no">{c["no"]}-{i+1}</span>{E(l["short"])}</a></li>'


def chapter_list(current=None):
    out = ""
    for c in COURSE["chapters"]:
        if c["lessons"]:
            items = "".join(lesson_li(c, i, l, current) for i, l in enumerate(c["lessons"]))
            out += (f'<div class="card" id="ch{c["no"]}"><small>第{c["no"]}章</small><b>{E(c["title"])}</b><span>{E(c["desc"])}</span><ol class="lessons">{items}</ol>'
                    + (f'<p style="margin:10px 0 0;font-size:14px;font-weight:700"><a href="/{test_path(c)}">第{c["no"]}章の章末テスト（{test_n(c)}問）</a></p>' if complete(c) else '')
                    + (f'<p style="margin:6px 0 0;font-size:14px;font-weight:700"><a href="/course/mock-exam/">{E(mock_label())}に挑戦（{mock_n()}問）</a></p>' if c is COURSE["chapters"][-1] and COURSE.get("mock") else '') + '</div>')
        else:
            out += f'<div class="card soon" id="ch{c["no"]}"><small>第{c["no"]}章</small><b>{E(c["title"])}</b><span>{E(c["desc"])}</span><span class="st">準備中</span></div>'
    return out


RESUME = '<div class="resume" hidden aria-live="polite"></div>'


def features_first():
    n_new = sum(1 for _, l in LESSONS if is_new(l))
    if LESSONS and n_new * 2 >= len(LESSONS):
        return "1レッスンは約5分です。「このレッスンの問い → 前回の復習 → 本文と図 → あなたの場合は？ → 覚えるのはこの3つ → 確認問題」の順に進みます。読んだ直後に確認問題で思い出し、章の最後の章末テストで仕上げます。"
    return "1レッスンは「前回の復習 → 学習目標 → 要点 → 本文 → キーワード（日本語・英語） → 確認クイズ」の順に進みます。読んだ直後にクイズで思い出し、章の最後の章末テストで仕上げます。"


def course_index():
    first = LESSONS[0][1] if LESSONS else None
    feats = [E(features_first())] + [E(fmt(x)) for x in CFG.get("courseFeatures", [])] + [
        "読み終えたレッスンと、間違えた問題はこのブラウザに自動で記録されます（登録不要）。間違えた問題は「<a href=\"/review/\">復習</a>」で解き直せ、用語は「<a href=\"/cards/\">暗記カード</a>」で覚えられます。"]
    body = f'''<span class="kicker">{T("courseKicker")}</span>
<h1>{E(COURSE["title"])}</h1>
<p class="updated">全{N_CH}章 ・ 公開中 {N_LESSONS}レッスン ・ 更新日 {UPDATED}</p>
<p class="lead">{T("courseLead")}</p>
{RESUME}
{f'<div class="btns"><a class="btn" href="/course/{first["id"]}/">第1章から学びはじめる</a><a class="btn sub" href="/glossary/">用語辞典を見る</a></div>' if first else ''}
<div class="box key"><p class="bt">この講座の特徴</p><ul>
{"".join(f"<li>{x}</li>" for x in feats)}
</ul></div>
<h2><span class="n">CONTENTS</span>講座の目次</h2>
<p class="answer">{T("courseContents")}</p>
<div class="grid">{chapter_list()}</div>
{practice_html()}'''
    graph = [course_ld(), {"@type": "ItemList", "name": f'{COURSE["title"]}のレッスン一覧', "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": l["title"], "url": lurl(l)} for i, (_, l) in enumerate(LESSONS)]}]
    return write("course/", f'{COURSE["title"]}（{fmt(CFG["courseKicker"])}）| {NAME}',
                 f'{COURSE["desc"]}全{N_CH}章。登録不要。', body, graph, trail=[("講座", CURL)], current="/course/", wide=True)


def figure_html(f):
    cap = f'<figcaption>{E(f["caption"])}</figcaption>' if f.get("caption") else ""
    if f["kind"] == "table":
        head = "".join(f"<th>{E(h)}</th>" for h in f["head"])
        rows = "".join("<tr>" + "".join(f'<td data-l="{E(f["head"][j], quote=True)}">{E(c)}</td>' for j, c in enumerate(r)) + "</tr>" for r in f["rows"])
        return f'<figure class="fig"><table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>{cap}</figure>'
    if f["kind"] == "svg":
        sv = f["svg"].strip()
        if "role=" not in sv[:200]:
            sv = sv.replace("<svg", f'<svg role="img" aria-label="{E(f.get("caption", ""), quote=True)}"', 1)
        return f'<figure class="fig">{sv}{cap}</figure>'
    if f["kind"] == "swatches":
        items = "".join(f'<li><span style="background:{x["hex"]}" aria-hidden="true"></span>{E(x["name"])}<code>{x["hex"]}</code></li>' for x in f["items"])
        return f'<figure class="fig"><ul class="sw">{items}</ul>{cap}</figure>'
    return ""


def lesson_new(ch, li, l, idx, no, prev_l, next_l):
    fig = l.get("figure")
    after = fig.get("after", len(l["sections"]) - 1) if fig else -1
    secs = ""
    for i, s in enumerate(l["sections"]):
        secs += (f'<h2><span class="n">{i+1:02d}</span>{E(s["h"])}</h2><p class="answer">{rich_text(s["answer"])}</p>'
                 + "".join(f"<p>{rich_text(p)}</p>" for p in s["paras"]))
        if i == after:
            secs += figure_html(fig)
    rv = l.get("review")
    review = ""
    if rv and prev_l:
        review = (f'<div class="review"><p class="bt">前のレッスンの復習（1問）</p><p>本文に入る前に、前のレッスンを思い出してみましょう。</p>'
                  + quiz_html([(rv, lesson_no(prev_l), lurl(prev_l).replace(URL, "/"), f'{l["id"]}:r')], mode="review") + '</div>')
    terms = "".join(f'<div class="term"><span class="tt">{E(t["ja"])}</span><span class="en">{E(t["en"])}</span><p>{E(t["def"])}</p></div>' for t in l.get("terms", []))
    quiz = quiz_html([(q, no, lurl(l).replace(URL, "/"), f'{l["id"]}:{k}') for k, q in enumerate(l["quiz"])], lid=l["id"])
    last = li == len(ch["lessons"]) - 1 and complete(ch)
    srcs = "".join(f'<li><a href="{E(s["url"], quote=True)}" target="_blank" rel="noopener">{E(s["text"])}</a></li>' for s in l["sources"])
    return f'''<span class="kicker">第{ch["no"]}章 {E(ch["title"])} ・ レッスン{no}</span>
<h1>{E(l["title"])}</h1>
<p class="updated">約{read_min(l)}分 ・ 公開日 {l.get("date", UPDATED)}{f' ・ 更新日 {l["modified"]}' if l.get("modified") and l["modified"] != l.get("date") else ''}</p>
<div class="box ask"><p class="bt">このレッスンの問い</p><p class="q">{E(l["question"])}</p><p class="hint">読む前に、答えを少しだけ予想してみてください。当たっていなくても大丈夫です。</p></div>
{review}
{CFG.get("careHtml", "") if ch.get("care") else ""}
{secs}
<div class="box apply"><p class="bt">あなたの場合は？</p><p>{E(l["apply"])}</p><p class="hint">答えを書く必要はありません。少し思い浮かべるだけで、記憶に残りやすくなります。</p></div>
<div class="box key"><p class="bt">覚えるのはこの3つ</p><ol>{"".join(f"<li>{rich_text(k)}</li>" for k in l["keep"])}</ol></div>
{f'<h2><span class="n">TERMS</span>このレッスンの用語</h2>{terms}' if terms else ''}
<section class="final" aria-labelledby="quiz-h">
<p class="fk">LESSON {no} の確認</p>
<h2 id="quiz-h">確認問題（全{len(l["quiz"])}問）</h2>
<p class="answer">本文を見ずに答えてみましょう。思い出そうとすることが、いちばんの復習になります。</p>
{quiz}
</section>
{done_html(ch, l, no, prev_l, next_l, last)}
<details class="srcs"><summary>出典（{len(l["sources"])}件）</summary><ol>{srcs}</ol></details>'''


def done_html(ch, l, no, prev_l, next_l, last):
    chlist = "".join(lesson_li(ch, j, x, l["id"]) for j, x in enumerate(ch["lessons"]))
    nxt = (f'<a class="btn{" sub" if last else ""}" href="/course/{next_l["id"]}/">次のレッスン: {E(next_l["short"])}</a>' if next_l else
           (f'<a class="btn" href="/course/mock-exam/">{E(mock_label())}に挑戦する</a>' if COURSE.get("mock") and all(c["lessons"] for c in COURSE["chapters"]) else '<a class="btn" href="/course/">講座の目次へ（次の章は準備中です）</a>'))
    return f'''<div class="done"><p class="dt">レッスン{no}はここまでです</p><p class="dd">迷った問題は、その見出しの本文を読み直してから次に進みましょう。間違えた問題は<a href="/review/">復習ページ</a>に自動で入ります。</p>
<button type="button" class="btn sub mark" data-l="{l["id"]}" aria-pressed="false" hidden>このレッスンを読み終えた</button>
<div class="btns" style="margin:14px 0 0">{f'<a class="btn" href="/{test_path(ch)}">第{ch["no"]}章の章末テストに挑戦</a>' if last else ''}{nxt}{f'<a class="btn sub" href="/course/{prev_l["id"]}/">前のレッスン</a>' if prev_l else ''}</div>
<details style="margin-top:16px"><summary>第{ch["no"]}章 {E(ch["title"])} のレッスン一覧</summary><div><ol class="lessons">{chlist}</ol><p style="margin:10px 0 0;font-size:14px"><a href="/course/">講座の目次（全{N_CH}章）へ</a></p></div></details>
</div>'''


def lesson_old(ch, li, l, idx, no, prev_l, next_l):
    secs = "".join(f'<h2><span class="n">{i+1:02d}</span>{E(s["h"])}</h2><p class="answer">{rich_text(s["answer"])}</p>' + "".join(f"<p>{rich_text(p)}</p>" for p in s["paras"]) for i, s in enumerate(l["sections"]))
    terms = "".join(f'<div class="term"><span class="tt">{E(t["ja"])}</span><span class="en">{E(t["en"])}</span><p>{E(t["def"])}</p></div>' for t in l["terms"])
    exs = "".join(f'<li><a href="{ARTICLES[e["slug"]][0]}">{E(e["text"])}</a> <small>（{E(ARTICLES[e["slug"]][2])}）</small></li>' for e in l.get("examples", []) if e["slug"] in ARTICLES)
    quiz = quiz_html([(q, no, lurl(l).replace(URL, "/"), f'{l["id"]}:{k}') for k, q in enumerate(l["quiz"])], lid=l["id"])
    # 前回の復習: 直前のレッスンと、3つ前のレッスンから1問ずつ（間隔をあけて思い出すと定着しやすい）
    rv = []
    for k in (idx - 1, idx - 3):
        if k >= 0:
            x = LESSONS[k][1]
            qi = idx % len(x["quiz"])
            rv.append((x["quiz"][qi], lesson_no(x), lurl(x).replace(URL, "/"), f'{x["id"]}:{qi}'))
    review = (f'<div class="review"><p class="bt">前回の復習（1分）</p><p>本文に入る前に、前のレッスンの内容を思い出してみましょう。</p>'
              + quiz_html(rv, mode="review") + '</div>') if rv else ""
    last = li == len(ch["lessons"]) - 1 and complete(ch)
    srcs = "".join(f'<li><a href="{E(s["url"], quote=True)}" target="_blank" rel="noopener">{E(s["text"])}</a></li>' for s in l["sources"])
    return f'''<span class="kicker">第{ch["no"]}章 {E(ch["title"])} ・ レッスン{no}</span>
<h1>{E(l["title"])}</h1>
<p class="updated">約{read_min(l)}分 ・ 公開日 {l.get("date", UPDATED)}</p>
{review}
{CFG.get("careHtml", "") if ch.get("care") else ""}
<div class="box"><p class="bt">このレッスンの学習目標</p><ul>{"".join(f"<li>{E(g)}</li>" for g in l["goals"])}</ul></div>
<div class="box key"><p class="bt">要点</p><ol>{"".join(f"<li>{E(s)}</li>" for s in l["summary"])}</ol></div>
{secs}
<h2><span class="n">KEYWORDS</span>キーワード（日本語・英語）</h2>
<p class="answer">{T("keywordsNote")}</p>
{terms}
{f'<h2><span class="n">EXAMPLES</span>身近な例で深める</h2><p class="answer">このレッスンの内容を、日常の疑問にあてはめた研究解説記事です。</p><ul class="ex">{exs}</ul>' if exs else ''}
<section class="final" aria-labelledby="quiz-h">
<p class="fk">LESSON {no} の仕上げ</p>
<h2 id="quiz-h">確認クイズ（全{len(l["quiz"])}問）</h2>
<p class="answer">読んだ直後に思い出すと、記憶に残りやすくなります。選択肢をタップして答えてください。</p>
{quiz}
</section>
{done_html(ch, l, no, prev_l, next_l, last)}
<details class="srcs"><summary>出典（{len(l["sources"])}件）</summary><ol>{srcs}</ol></details>'''


def lesson(ci, li):
    ch = COURSE["chapters"][ci]
    l = ch["lessons"][li]
    idx = next(i for i, (_, x) in enumerate(LESSONS) if x["id"] == l["id"])
    prev_l = LESSONS[idx - 1][1] if idx > 0 else None
    next_l = LESSONS[idx + 1][1] if idx < len(LESSONS) - 1 else None
    no = f'{ch["no"]}-{li+1}'
    body = (lesson_new if is_new(l) else lesson_old)(ch, li, l, idx, no, prev_l, next_l)
    url = lurl(l)
    terms = l.get("terms", [])
    graph = [
        {"@type": ["Article", "LearningResource"], "headline": l["title"], "description": l["description"], "url": url, "inLanguage": "ja",
         "mainEntityOfPage": {"@type": "WebPage", "@id": url}, "datePublished": l.get("date", UPDATED), "dateModified": l.get("modified", l.get("date", UPDATED)),
         "author": {"@type": "Organization", "name": f"{NAME}編集部"}, "publisher": PUBLISHER, "isAccessibleForFree": True,
         "learningResourceType": "Lesson", "educationalLevel": "初級", "timeRequired": f"PT{read_min(l)}M",
         "teaches": [t["ja"] for t in terms] or l.get("keep", []), "isPartOf": {"@id": CURL + "#course"},
         "position": idx + 1, "citation": [s["url"] for s in l["sources"]]},
        faq_ld([(q["q"], f'{q["choices"][q["a"]]}。{q["exp"]}') for q in l["quiz"]]),
    ]
    if terms:
        graph.insert(1, {"@type": "DefinedTermSet", "name": f'{l["short"]}のキーワード', "hasDefinedTerm": [
            {"@type": "DefinedTerm", "name": t["ja"], "alternateName": t["en"], "description": t["def"]} for t in terms]})
    return write(f'course/{l["id"]}/', f'{l["title"]}｜{fmt(CFG["lessonTag"])} {no} | {NAME}', l["description"], body, graph,
                 trail=[("講座", CURL), (f'第{ch["no"]}章 {ch["title"]}', CURL), (l["short"], url)], current="/course/")


def practice_html(h="もっと演習する"):
    """SEADICEの既存の学習ツール（講座の外の演習）。設定の practice が空なら何も出さない。"""
    ps = CFG.get("practice", [])
    if not ps:
        return ""
    cards = "".join(f'<a class="card" href="{u}"><b>{E(n)}</b><span>{E(t)}</span></a>' for n, u, t in ps)
    return (f'<h2><span class="n">PRACTICE</span>{E(h)}</h2><p class="answer">講座で学んだあとの演習には、SEADICEの次のツールも使えます。いずれも無料です。</p>'
            f'<div class="grid">{cards}</div>')


def exam_corner():
    """本番形式の模擬試験コーナー（設定の exam）。試験本体は静的アプリ（例: /c/exam/）。"""
    x = CFG["exam"]
    path = x.get("path", "c/")
    url = f"{URL}{path}"
    faq = x["faq"]
    body = f'''<span class="kicker">{E(x["kicker"])}</span>
<h1>{E(x["h1"])}</h1>
<p class="updated">{E(x["meta"])} ・ 更新日 {UPDATED}</p>
<p class="lead">{E(x["lead"])}</p>
<div class="btns"><a class="btn" href="{x["start"]}">模擬試験を始める</a>{f'<a class="btn sub" href="/course/mock-exam/">講座の確認模試（{mock_n()}問）</a>' if COURSE.get("mock") else ''}</div>
<div class="box key"><p class="bt">模擬試験の概要</p><ul>{"".join(f"<li>{E(o)}</li>" for o in x["overview"])}</ul></div>
<div class="box note"><p style="margin:0">{E(x["note"])}</p></div>
<h2><span class="n">01</span>まだ学んでいない分野があるときは</h2>
<p class="answer">間違えた分野は、無料講座の該当する章で学び直せます。章末の章末テストで確かめてから、もう一度挑戦しましょう。</p>
<div class="grid">{chapter_list()}</div>
{practice_html("あわせて使える演習ツール")}
<h2><span class="n">FAQ</span>よくある質問</h2>
{faq_html(faq)}'''
    graph = [{"@type": "WebApplication", "name": x["appName"], "url": url, "applicationCategory": "EducationApplication", "operatingSystem": "Web",
              "inLanguage": "ja", "offers": {"@type": "Offer", "price": 0, "priceCurrency": "JPY"}, "publisher": PUBLISHER}, faq_ld(faq)]
    return write(path, f'{x["title"]} | {NAME}', x["desc"], body, graph, trail=[(x["crumb"], url)], current="/" + path, wide=True)


def mock_n():
    return sum(len(p["questions"]) for p in COURSE["mock"]["parts"])


def mock_exam():
    """模擬試験。全範囲のオリジナル問題を2部構成で出題し、間違えた問題のレッスンへ案内する。"""
    m = COURSE["mock"]
    ref = {l["id"]: (lesson_no(l), lurl(l).replace(URL, "/")) for _, l in LESSONS}
    url = f"{URL}course/mock-exam/"
    parts = "".join(f'<h2><span class="n">PART {i+1}</span>{E(p["name"])}（{len(p["questions"])}問）</h2><p class="answer">{E(p.get("desc", ""))}</p>'
                    + quiz_html([(q, *ref[q["ref"]], f"mock:{i}:{k}") for k, q in enumerate(p["questions"])], mode="test") for i, p in enumerate(m["parts"]))
    body = f'''<span class="kicker">総仕上げ</span>
<h1>{E(m["title"])}（全{mock_n()}問）</h1>
<p class="updated">対象: 講座の全範囲 ・ 目安 {max(10, mock_n() // 2)}分 ・ 更新日 {m.get("date", UPDATED)}</p>
<p class="lead">{E(m["lead"])}</p>
<div class="box note"><p style="margin:0">{T("mockNote")}</p></div>
{parts}
<div class="done"><p class="dt">おつかれさまでした</p><p class="dd">各PARTの最後に、間違えた問題のレッスンが表示されます。間違えた問題は<a href="/review/">復習ページ</a>にも入ります。</p>
<div class="btns" style="margin:14px 0 0"><a class="btn" href="/course/">講座の目次へ</a><a class="btn sub" href="/glossary/">用語辞典で復習する</a></div></div>
{practice_html("さらに演習する")}'''
    graph = [{"@type": "Quiz", "name": m["title"], "url": url, "inLanguage": "ja", "educationalLevel": "初級", "isAccessibleForFree": True,
              "isPartOf": {"@id": CURL + "#course"}, "publisher": PUBLISHER,
              "hasPart": [{"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["choices"][q["a"]]}} for p in m["parts"] for q in p["questions"]]}]
    return write("course/mock-exam/", f'{m["title"]}（全{mock_n()}問・無料）| {NAME}', m["lead"][:120], body, graph,
                 trail=[("講座", CURL), (mock_label(), url)], current="/course/")


def chapter_test(ch):
    """章の章末テスト。各レッスンの問題を、レッスンが交互になるように並べる。"""
    ls = ch["lessons"]
    items = [(l["quiz"][k], f'{ch["no"]}-{i+1}', lurl(l).replace(URL, "/"), f'{l["id"]}:{k}') for k in range(max(len(l["quiz"]) for l in ls)) for i, l in enumerate(ls) if k < len(l["quiz"])]
    ref = {l["id"]: (f'{ch["no"]}-{i+1}', lurl(l).replace(URL, "/")) for i, l in enumerate(ls)}
    extra = [(q, *ref[q["ref"]], f'{ch["id"]}:t{k}') for k, q in enumerate(ch.get("test", []))]
    if extra:
        quizzes = (f'<h2><span class="n">PART 1</span>レッスンの確認問題（{len(items)}問）</h2><p class="answer">各レッスンで解いた問題です。忘れていないか確かめましょう。</p>{quiz_html(items, mode="test")}'
                   f'<h2><span class="n">PART 2</span>章末の演習問題（{len(extra)}問）</h2><p class="answer">レッスンにはない、新しい問題です。日常の場面で考える問題も入っています。</p>{quiz_html(extra, mode="test")}')
    else:
        quizzes = quiz_html(items, mode="test")
    items = items + extra
    url = f"{URL}{test_path(ch)}"
    title = f'第{ch["no"]}章 {ch["title"]} 章末テスト'
    nxt = next((c for c in COURSE["chapters"] if c["no"] == ch["no"] + 1 and c["lessons"]), None)
    body = f'''<span class="kicker">第{ch["no"]}章のまとめ</span>
<h1>{E(title)}（全{len(items)}問）</h1>
<p class="updated">対象: レッスン{ch["no"]}-1〜{ch["no"]}-{len(ls)} ・ 目安 {max(3, len(items) // 2)}分 ・ 制限時間なし</p>
<p class="lead">第{ch["no"]}章「{E(ch["title"])}」で学んだ内容を、まとめて確かめるテストです。レッスンが混ざった順番で出題します。最後に、間違えた問題のレッスンへのリンクが出ます。</p>
{quizzes}
<div class="done"><p class="dt">第{ch["no"]}章はここまでです</p><p class="dd">間違えた問題は<a href="/review/">復習ページ</a>に入ります。表示されたレッスンを読み直してから、もう一度挑戦しましょう。</p>
<div class="btns" style="margin:14px 0 0">{f'<a class="btn" href="/course/{nxt["lessons"][0]["id"]}/">第{nxt["no"]}章へ進む: {E(nxt["title"])}</a>' if nxt else (f'<a class="btn" href="/course/mock-exam/">{E(mock_label())}に挑戦する</a>' if COURSE.get("mock") else '<a class="btn" href="/course/">講座の目次へ</a>')}<a class="btn sub" href="/course/#ch{ch["no"]}">第{ch["no"]}章のレッスン一覧</a></div></div>'''
    graph = [{"@type": "Quiz", "name": title, "url": url, "inLanguage": "ja", "educationalLevel": "初級", "isAccessibleForFree": True,
              "about": ch["title"], "isPartOf": {"@id": CURL + "#course"}, "publisher": PUBLISHER,
              "hasPart": [{"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["choices"][q["a"]]}} for q, _, _, _ in items]}]
    return write(test_path(ch), f'{title}（全{len(items)}問）| {NAME}',
                 f'第{ch["no"]}章「{ch["title"]}」の確認問題{len(items)}問。タップで答えて、間違えた問題のレッスンを読み直せます。無料・登録不要。', body, graph,
                 trail=[("講座", CURL), (f'第{ch["no"]}章 {ch["title"]}', CURL), ("章末テスト", url)], current="/course/")


# ---------------- 学習機能のページ ----------------
def review_page():
    """間違えた問題だけを解き直す。全問題を hidden で置き、study.js が記録にある問題だけを表示する。"""
    items = []
    for ch, l in LESSONS:
        no, href = lesson_no(l), lurl(l).replace(URL, "/")
        items += [(q, no, href, f'{l["id"]}:{k}') for k, q in enumerate(l["quiz"])]
        if is_new(l) and l.get("review"):
            idx = next(i for i, (_, x) in enumerate(LESSONS) if x["id"] == l["id"])
            if idx > 0:
                p = LESSONS[idx - 1][1]
                items.append((l["review"], lesson_no(p), lurl(p).replace(URL, "/"), f'{l["id"]}:r'))
    for ch in COURSE["chapters"]:
        ref = {l["id"]: (f'{ch["no"]}-{i+1}', lurl(l).replace(URL, "/")) for i, l in enumerate(ch["lessons"])}
        items += [(q, *ref[q["ref"]], f'{ch["id"]}:t{k}') for k, q in enumerate(ch.get("test", [])) if q.get("ref") in ref]
    if COURSE.get("mock"):
        ref = {l["id"]: (lesson_no(l), lurl(l).replace(URL, "/")) for _, l in LESSONS}
        for i, p in enumerate(COURSE["mock"]["parts"]):
            items += [(q, *ref[q["ref"]], f"mock:{i}:{k}") for k, q in enumerate(p["questions"]) if q.get("ref") in ref]
    body = f'''<span class="kicker">復習</span>
<h1>間違えた問題の復習</h1>
<p class="lead">レッスンの確認問題や章末テストで間違えた問題が、ここに自動で集まります。正解すると、リストから外れます。記録はこのブラウザの中だけに保存され、送信されません。</p>
<div id="redo"><p id="redo-msg" class="answer" aria-live="polite">間違えた問題の記録を使うには、ブラウザのJavaScriptを有効にしてください。各章の章末テストでも解き直せます。</p>
{quiz_html(items, mode="redo")}</div>
<div class="btns" style="margin-top:28px"><a class="btn" href="/course/">講座の目次へ</a><a class="btn sub" href="/cards/">暗記カードで用語を覚える</a></div>'''
    return write("review/", f"間違えた問題の復習 | {NAME}", f"{NAME}の確認問題で間違えた問題だけを、解説つきで解き直せるページです。登録不要。", body, [],
                 trail=[("間違えた問題の復習", f"{URL}review/")], noindex=True)


def cards_page():
    """用語辞典の暗記カード（ライトナー方式）。JSなしでは、用語を開いて意味を確かめる一覧として使える。"""
    lst = "".join(f'<details data-t="{t["id"]}"><summary><span class="tt">{E(t["term"])}</span> <span class="en">{E(t["en"])}</span></summary><p>{E(t["def"])}</p></details>' for t in TERMS)
    body = f'''<span class="kicker">全{len(TERMS)}語</span>
<h1>{T("glossaryName")}の暗記カード</h1>
<p class="lead">用語を見て意味を思い出し、「意味を見る」で確かめます。あやしかった語ほど早く、覚えていた語は日をあけて出てきます（ライトナー方式）。1回20枚まで、時間制限はありません。</p>
<p id="cards-note" class="updated" hidden>記録はこのブラウザの中だけに保存されます。登録は不要です。</p>
<div id="fc" class="fc" hidden aria-live="polite"></div>
<div id="cards"><p class="answer">用語をタップすると意味が開きます。意味を思い浮かべてから開くと、覚えやすくなります。</p>{lst}</div>
<div class="btns" style="margin-top:28px"><a class="btn sub" href="/glossary/">{T("glossaryName")}の一覧</a><a class="btn sub" href="/review/">間違えた問題の復習</a></div>'''
    return write("cards/", f'{fmt(CFG["glossaryName"])}の暗記カード | {NAME}', f'{fmt(CFG["glossaryName"])}の{len(TERMS)}語を、暗記カードで覚えられるページです。あやしい語ほど早く出ます。登録不要。', body, [],
                 trail=[(f'{fmt(CFG["glossaryName"])}の暗記カード', f"{URL}cards/")], noindex=True)

# ---------------- クイズ（ゲーム形式。/quiz/、quiz.js、/quiz/data.json） ----------------
QUIZ_JS = r"""(function(){'use strict';
var G=document.getElementById('game');if(!G)return;
var KEY='study:'+(document.documentElement.getAttribute('data-site')||'x'),S={},OK=true;
try{S=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){OK=false;S={}}
S.miss=S.miss||{};S.qz=S.qz||{};S.qz.best=S.qz.best||{};S.qz.ch=S.qz.ch||{};
function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){OK=false}}
function el(t,c,x){var e=document.createElement(t);if(c)e.className=c;if(x!=null)e.textContent=x;return e}
function shuf(a){a=a.slice();for(var i=a.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=a[i];a[i]=a[j];a[j]=t}return a}
var R=JSON.parse(G.dataset.ranks),D=null,M=document.getElementById('g-menu'),P=document.getElementById('g-play');
var st=null;/* 進行中のゲーム */
function rank(v,th){for(var i=th.length-1;i>=0;i--)if(v>=th[i])return R[i];return R[0]}
function menu(){P.hidden=true;M.hidden=false;
var w=D.q.filter(function(q){return S.miss[q.i]}).length,wb=G.querySelector('[data-mode=weak]');
wb.disabled=!w;wb.querySelector('span').textContent=w?'これまでに間違えた問題だけ（'+w+'問）。正解すると消えます':'今は間違えた問題はありません';
G.querySelectorAll('[data-best]').forEach(function(e){var b=S.qz.best[e.dataset.best];e.textContent=b?'自己ベスト '+b:''});
G.querySelectorAll('[data-ch]').forEach(function(b){var c=S.qz.ch[b.dataset.ch],r=b.querySelector('.g-rate');
if(c&&c.n){var v=Math.round(c.ok/c.n*100);r.querySelector('i').style.width=v+'%';r.querySelector('em').textContent='正答率 '+v+'%（'+c.n+'問）';r.hidden=false}})}
function start(mode,ch){var pool=D.q;
if(mode==='ch')pool=pool.filter(function(q){return q.c===+ch});
if(mode==='weak')pool=pool.filter(function(q){return S.miss[q.i]});
pool=shuf(pool);if(mode!=='surv')pool=pool.slice(0,10);
st={mode:mode,key:mode==='ch'?'ch'+ch:mode,qs:pool,k:0,ok:0,pt:0,combo:0,max:0,life:3,missed:[]};M.hidden=true;P.hidden=false;ask();window.scrollTo(0,G.offsetTop-70)}
function head(){var h=el('div','g-head'),surv=st.mode==='surv';
h.appendChild(el('span','g-prog',surv?(st.k+1)+'問目':(st.k+1)+' / '+st.qs.length));
h.appendChild(el('span','g-pt',st.pt+' pt'));
if(surv){var l=el('span','g-life');l.setAttribute('aria-label','ライフ 残り'+st.life);for(var i=0;i<3;i++)l.appendChild(el('i',i<st.life?'on':''));h.appendChild(l)}
var b=el('div','g-bar'),f=el('i');f.style.width=(surv?Math.min(100,st.k/30*100):st.k/st.qs.length*100)+'%';b.appendChild(f);
var w=el('div');w.appendChild(h);w.appendChild(b);return w}
function ask(){var q=st.qs[st.k];P.innerHTML='';P.appendChild(head());
var c=el('div','g-card');c.appendChild(el('p','g-src','第'+D.ch[q.c][0]+'章 '+D.ch[q.c][1]));c.appendChild(el('p','g-q',q.q));
var o=shuf(q.o.map(function(t,i){return{t:t,ok:i===q.a}})),bs=el('div','g-chs');
o.forEach(function(x,i){var b=el('button','g-ch');b.type='button';b.appendChild(el('b','',String(i+1)));b.appendChild(document.createTextNode(x.t));
b.onclick=function(){answer(q,o,i,bs)};bs.appendChild(b)});c.appendChild(bs);
var fb=el('div','g-fb');fb.setAttribute('aria-live','polite');c.appendChild(fb);P.appendChild(c);st.cur={q:q,o:o,bs:bs,fb:fb,done:false}}
function answer(q,o,i,bs){if(st.cur.done)return;st.cur.done=true;var ok=o[i].ok,fb=st.cur.fb,cs=S.qz.ch[q.c]=S.qz.ch[q.c]||{n:0,ok:0};cs.n++;
[].forEach.call(bs.children,function(b,j){b.disabled=true;if(o[j].ok)b.classList.add('ok');else if(j===i)b.classList.add('ng')});
if(ok){st.ok++;st.combo++;st.max=Math.max(st.max,st.combo);var add=100+20*Math.min(st.combo-1,5);st.pt+=add;cs.ok++;delete S.miss[q.i];
fb.appendChild(el('p','g-ok',st.combo>=2?st.combo+'連続正解！ +'+add:'正解！ +'+add));if(st.combo>=3){var p=el('span','g-pop',st.combo+' COMBO');fb.appendChild(p)}}
else{st.combo=0;st.life--;S.miss[q.i]={l:q.h,t:Date.now()};st.missed.push(q);fb.appendChild(el('p','g-ng','惜しい！'+(st.mode==='surv'?' ライフ -1':'')))}
save();fb.appendChild(el('p','g-exp',q.e));
var a=el('a','g-read','レッスン'+q.n+'を読む');a.href=q.h;fb.appendChild(a);
var last=st.mode==='surv'?st.life<=0||st.k+1>=st.qs.length:st.k+1>=st.qs.length,nx=el('button','btn g-next',last?'結果を見る':'次の問題へ');nx.type='button';
nx.onclick=function(){if(last)result();else{st.k++;ask()}};fb.appendChild(nx);nx.focus({preventScroll:true});
var h=P.querySelector('.g-pt');if(h)h.textContent=st.pt+' pt';var lf=P.querySelector('.g-life');if(lf)[].forEach.call(lf.children,function(x,j){x.className=j<st.life?'on':''})}
function result(){var surv=st.mode==='surv',n=st.k+1,v=surv?st.ok:Math.round(st.ok/n*100),r=surv?rank(st.ok,[0,5,15,30]):rank(v,[0,60,80,100]);
var best=S.qz.best[st.key]||0,nb=st.pt>best;if(nb)S.qz.best[st.key]=st.pt;save();
P.innerHTML='';var c=el('div','g-card g-res');c.appendChild(el('p','g-src','結果'));
c.appendChild(el('p','g-rank',r));c.appendChild(el('p','g-big',surv?st.ok+'問 正解':n+'問中 '+st.ok+'問 正解'));
c.appendChild(el('p','g-sub',st.pt+' pt'+(st.max>=2?' ・ 最大 '+st.max+' 連続正解':'')+(nb?' ・ 自己ベスト更新！':' ・ 自己ベスト '+best+' pt')));
if(st.missed.length){c.appendChild(el('p','g-sub','間違えた問題は「苦手をつぶす」と復習ページに入りました。読み直すならここから:'));var ul=el('ul','g-miss'),seen={};
st.missed.forEach(function(q){if(seen[q.h])return;seen[q.h]=1;var li=el('li'),a=el('a','','レッスン'+q.n);a.href=q.h;li.appendChild(a);ul.appendChild(li)});c.appendChild(ul)}
else c.appendChild(el('p','g-sub','全問正解です。この調子で、ほかのモードにも挑戦してみましょう。'));
var bs=el('div','btns'),again=el('button','btn','もう一度'),back=el('button','btn sub','メニューへ');again.type=back.type='button';
var md=st.mode,ch=st.key.slice(2);again.onclick=function(){start(md,ch)};back.onclick=menu;bs.appendChild(again);bs.appendChild(back);c.appendChild(bs);P.appendChild(c);again.focus({preventScroll:true})}
document.addEventListener('keydown',function(e){if(!st||P.hidden||!st.cur||st.cur.done)return;var k=+e.key;if(k>=1&&k<=st.cur.o.length){e.preventDefault();answer(st.cur.q,st.cur.o,k-1,st.cur.bs)}});
G.querySelectorAll('[data-mode]').forEach(function(b){b.onclick=function(){start(b.dataset.mode)}});
G.querySelectorAll('[data-ch]').forEach(function(b){b.onclick=function(){start('ch',b.dataset.ch)}});
fetch('/quiz/data.json').then(function(r){return r.json()}).then(function(d){D=d;G.hidden=false;document.getElementById('g-nojs').hidden=true;
if(!OK)document.getElementById('g-note').textContent='このブラウザでは記録を保存できないため、自己ベストと正答率は残りません。';menu()}).catch(function(){})
})();"""


def quiz_items():
    """クイズに出す全問題。レッスンの確認問題・復習問題・章末テスト・総まとめテスト。問題idは他のページと共通（間違えた記録を共有する）。"""
    out, ci_of, info = [], {}, {}
    for ci, ch in enumerate(COURSE["chapters"]):
        for i, l in enumerate(ch["lessons"]):
            ci_of[l["id"]] = ci
            info[l["id"]] = (f'{ch["no"]}-{i+1}', lurl(l).replace(URL, "/"))
    def add(qid, lid, q):
        out.append({"i": qid, "c": ci_of[lid], "q": q["q"], "o": q["choices"], "a": q["a"], "e": q["exp"], "n": info[lid][0], "h": info[lid][1]})
    for idx, (ch, l) in enumerate(LESSONS):
        for k, q in enumerate(l["quiz"]):
            add(f'{l["id"]}:{k}', l["id"], q)
        if is_new(l) and l.get("review") and idx > 0:
            add(f'{l["id"]}:r', LESSONS[idx - 1][1]["id"], l["review"])
    for ch in COURSE["chapters"]:
        for k, q in enumerate(ch.get("test", [])):
            add(f'{ch["id"]}:t{k}', q["ref"], q)
    for i, p in enumerate(COURSE.get("mock", {}).get("parts", [])):
        for k, q in enumerate(p["questions"]):
            add(f"mock:{i}:{k}", q["ref"], q)
    return out


def has_quiz():
    return len(quiz_items()) >= 100


def quiz_name():
    return CFG.get("quizName", "クイズ")


def quiz_page():
    items = quiz_items()
    n = len(items)
    chs = [c for c in COURSE["chapters"] if c["lessons"]]
    ci = {c["id"]: i for i, c in enumerate(COURSE["chapters"])}
    data = {"ch": [[c["no"], c["title"]] for c in COURSE["chapters"]], "q": items}
    (OUT / "quiz").mkdir(parents=True, exist_ok=True)
    (OUT / "quiz" / "data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    ranks = CFG.get("quizRanks", ["ビギナー", "ルーキー", "エキスパート", "マスター"])
    name, url = quiz_name(), f"{URL}quiz/"
    chbtn = "".join(f'<button type="button" class="g-chb" data-ch="{ci[c["id"]]}"><small>第{c["no"]}章</small><b>{E(c["title"])}</b>'
                    f'<span class="g-rate" hidden><i></i><em></em></span></button>' for c in chs)
    tests = "".join(f'<li><a href="/{test_path(c)}">第{c["no"]}章 {E(c["title"])}（{test_n(c)}問）</a></li>' for c in chs if complete(c))
    faq = [(f"{name}は無料ですか？", f"無料です。登録も不要で、{n}問すべてをブラウザで解けます。自己ベストや章ごとの正答率は、このブラウザの中だけに保存され、送信されません。"),
           (f"{name}の問題はどこから出ますか？", f"無料講座「{COURSE['title']}」の内容から出題します。各レッスンの確認問題、章末テスト、{mock_label() if COURSE.get('mock') else '章末の問題'}の問題を合わせた{n}問です。問題はすべてSEADICEのオリジナルです。"),
           ("間違えた問題はどうなりますか？", "「苦手をつぶす」モードと復習ページに自動で入ります。正解するとリストから外れます。解説の下のリンクから、その問題のレッスンを読み直せます。")]
    body = f'''<span class="kicker">クイズで学ぶ</span>
<h1>{E(name)}（全{n}問・無料）</h1>
<p class="lead">{E(COURSE["title"])}の内容から出題する、ゲーム形式のクイズです。1問ずつ答えて、連続正解でポイントが増えます。間違えた問題は解説とレッスンへのリンクが出るので、本を買わなくても、解きながら覚えられます。</p>
<div id="game" data-ranks="{E(json.dumps(ranks, ensure_ascii=False), quote=True)}" hidden>
<div id="g-menu">
<div class="g-modes">
<button type="button" class="g-mode" data-mode="ten"><b>10問チャレンジ</b><span>全範囲からランダムに10問</span><em data-best="ten"></em></button>
<button type="button" class="g-mode" data-mode="surv"><b>サバイバル</b><span>3回間違えるまで続く。何問いける？</span><em data-best="surv"></em></button>
<button type="button" class="g-mode" data-mode="weak"><b>苦手をつぶす</b><span></span></button>
</div>
<p id="g-note" class="g-note">記録（自己ベスト・正答率・間違えた問題）は、このブラウザの中だけに保存されます。数字キー1〜4でも答えられます。</p>
<h2><span class="n">CHAPTER</span>章をえらんで10問</h2>
<div class="g-chgrid">{chbtn}</div>
</div>
<div id="g-play" hidden></div>
</div>
<div id="g-nojs"><p class="answer">クイズを遊ぶには、ブラウザのJavaScriptを有効にしてください。同じ問題は、各章の章末テストでも解けます。</p></div>
<h2><span class="n">TEST</span>章末テストと{E(mock_label()) if COURSE.get("mock") else "模擬試験"}</h2>
<p class="answer">1問ずつではなく、まとめて解きたいときは章末テストを使います。</p>
<ul class="ex">{tests}{f'<li><a href="/course/mock-exam/">{E(mock_label())}（{mock_n()}問）</a></li>' if COURSE.get("mock") else ""}</ul>
<h2><span class="n">FAQ</span>よくある質問</h2>
{faq_html(faq)}
<script src="/quiz.js" defer></script>'''
    graph = [{"@type": "Quiz", "name": name, "url": url, "inLanguage": "ja", "educationalLevel": "初級", "isAccessibleForFree": True,
              "numberOfQuestions": n, "isPartOf": {"@id": CURL + "#course"}, "publisher": PUBLISHER}, faq_ld(faq)]
    return write("quiz/", f"{name}（全{n}問・無料）| {NAME}", f"{COURSE['title']}の内容から出題するゲーム形式の無料クイズ。10問チャレンジ・サバイバル・章別・苦手をつぶす の4モード、全{n}問。登録不要。",
                 body, graph, trail=[(name, url)], current="/quiz/", wide=True)



# ---------------- 用語辞典 ----------------
def glossary():
    fields = list(dict.fromkeys(t["field"] for t in TERMS))
    url = f"{URL}glossary/"
    gname = fmt(CFG["glossaryName"])
    body = (f'<span class="kicker">全{len(TERMS)}語</span><h1>{E(gname)}</h1><p class="updated">更新日 {UPDATED}</p>'
            f'<p class="lead">{T("glossaryLead")}</p>'
            f'<p><a href="/cards/">暗記カードで覚える（{len(TERMS)}語）</a></p>'
            '<div class="chips">' + "".join(f'<a href="#f{i}">{E(f)}</a>' for i, f in enumerate(fields)) + '</div>')
    for i, f in enumerate(fields):
        body += f'<h2 id="f{i}"><span class="n">{i+1:02d}</span>{E(f)}の用語</h2>'
        for t in (t for t in TERMS if t["field"] == f):
            a = ARTICLES.get(t.get("slug"))
            more = f'<a class="more" href="{a[0]}">解説記事: {E(a[1])}（{E(a[2])}）</a>' if a else ""
            name = f'<a href="/glossary/{t["id"]}/">{E(t["term"])}</a>' if rich(t) else E(t["term"])
            body += f'<div class="term" id="{t["id"]}"><span class="tt">{name}</span><span class="en">{E(t["en"])}</span><p>{E(t["def"])}</p>{more}</div>'
    body += f'<div class="box key" style="margin-top:36px"><p class="bt">{T("glossaryCtaHead")}</p><p style="margin:0">{H("glossaryCtaHtml")}</p></div>'
    graph = [{"@type": "DefinedTermSet", "@id": url, "name": gname, "url": url, "inLanguage": "ja", "dateModified": UPDATED, "publisher": PUBLISHER,
              "hasDefinedTerm": [{"@type": "DefinedTerm", "@id": f'{url}#{t["id"]}', "name": t["term"], "alternateName": t["en"],
                                  "description": t["def"], "url": f'{url}{t["id"]}/' if rich(t) else f'{url}#{t["id"]}', "inDefinedTermSet": url} for t in TERMS]}]
    return write("glossary/", f"{gname}（{len(TERMS)}語をやさしく解説）| {NAME}", fmt(CFG["glossaryDesc"]),
                 body, graph, trail=[(gname, url)], current="/glossary/")


def rich(t):
    """個別ページを出せるだけの中身がある用語か（薄いページは作らない）。"""
    return len("".join(t.get("detail", []))) >= 400 and t.get("sources") and t.get("faq")


def term_lessons(t):
    """この用語をキーワードに含むレッスン（講座で詳しく学べる場所）。"""
    key = t["term"].split("（")[0]
    return [(ch, l) for ch, l in LESSONS if any(key in k["ja"] or k["ja"] in key for k in l.get("terms", []))]


def term_page(t):
    url = f'{URL}glossary/{t["id"]}/'
    gname = fmt(CFG["glossaryName"])
    key = t["term"].split("（")[0]
    ls = term_lessons(t)
    rel = [x for x in TERMS if x["field"] == t["field"] and x["id"] != t["id"]][:6]
    faq = [(q["q"], q["a"]) for q in t["faq"]]
    body = f'''<span class="kicker">{E(t["field"])}</span>
<h1>{E(key)}とは</h1>
<p class="updated">英語: {E(t["en"])} ・ 更新日 {t.get("date", UPDATED)}</p>
<p class="lead">{E(t["def"])}</p>
<h2><span class="n">01</span>{E(key)}をくわしく</h2>
{"".join(f"<p>{E(x)}</p>" for x in t["detail"])}
{f'<h2><span class="n">02</span>身近な例</h2><p class="answer">{E(t["example"])}</p>' if t.get("example") else ""}
{f'<h2><span class="n">03</span>講座で学ぶ</h2><p class="answer">{E(key)}は、無料講座「{E(COURSE["title"])}」の次のレッスンで詳しく学べます。</p><ol class="lessons">' + "".join(f'<li><a href="/course/{l["id"]}/"><span class="no">第{ch["no"]}章</span>{E(l["title"])}</a></li>' for ch, l in ls) + "</ol>" if ls else ""}
<h2><span class="n">FAQ</span>よくある質問</h2>
{faq_html(faq)}
{'<h2><span class="n">RELATED</span>同じ分野の用語</h2><div class="chips">' + "".join(f'<a href="/glossary/{x["id"]}/">{E(x["term"])}</a>' if rich(x) else f'<a href="/glossary/#{x["id"]}">{E(x["term"])}</a>' for x in rel) + "</div>" if rel else ""}
<div class="src"><h2>出典</h2><ol>{"".join(f'<li><a href="{x["url"]}" target="_blank" rel="noopener">{E(x["text"])}</a></li>' for x in t["sources"])}</ol></div>
<p style="margin-top:28px"><a href="/glossary/">{E(gname)}の一覧へ（{len(TERMS)}語）</a></p>'''
    graph = [{"@type": "DefinedTerm", "@id": url, "name": key, "alternateName": t["en"], "description": t["def"], "url": url,
              "inDefinedTermSet": {"@type": "DefinedTermSet", "name": gname, "url": f"{URL}glossary/"}},
             {"@type": "Article", "headline": f"{key}とは", "description": t["def"], "url": url, "inLanguage": "ja",
              "datePublished": t.get("date", UPDATED), "dateModified": t.get("date", UPDATED), "mainEntityOfPage": {"@type": "WebPage", "@id": url},
              "author": {"@type": "Organization", "name": f"{NAME}編集部"}, "publisher": PUBLISHER, "citation": [x["url"] for x in t["sources"]]},
             faq_ld(faq)]
    return write(f'glossary/{t["id"]}/', f'{key}とは？意味と例をやさしく解説 | {NAME}', t["def"][:120], body, graph,
                 trail=[(gname, f"{URL}glossary/"), (f"{key}とは", url)], current="/glossary/")


# ---------------- トップ ----------------
def home():
    tmap = {t["id"]: t for t in TERMS}
    chips = "".join(f'<a href="/glossary/#{i}">{E(tmap[i]["term"])}</a>' for i in CFG.get("homeTerms", []) if i in tmap)
    first = LESSONS[0][1] if LESSONS else None
    gname = T("glossaryName")
    body = f'''<div class="hero"><p class="tag">{E(CFG["tagline"])}</p><h1>{E(NAME)}</h1></div>
<p class="lead">{E(CFG["lead"])}</p>
<p class="stats"><span><b>{N_CH}</b>章の無料講座</span><span><b>{N_LESSONS}</b>レッスン公開中</span><span><b>{len(TERMS)}</b>語の用語辞典</span><span>登録不要</span></p>
{RESUME}
<div class="btns">{f'<a class="btn" href="/course/{first["id"]}/">講座を第1章から始める</a>' if first else ''}{f'<a class="btn" href="/quiz/">{E(quiz_name())}で遊ぶ（{len(quiz_items())}問）</a>' if has_quiz() else ''}<a class="btn sub" href="/glossary/">{gname}を見る</a></div>
<h2><span class="n">01</span>無料講座「{E(COURSE["title"])}」</h2>
<p class="answer">{T("homeCourseAnswer")}</p>
<div class="grid">{chapter_list()}</div>
<p style="margin-top:14px"><a href="/course/">講座の目次をすべて見る</a></p>
<h2><span class="n">02</span>{gname}</h2>
<p class="answer">{T("homeGlossaryAnswer")}</p>
<div class="chips">{chips}</div>
<p><a href="/glossary/">用語辞典をすべて見る（{len(TERMS)}語）</a> ・ <a href="/cards/">暗記カードで覚える</a></p>
{practice_html()}
<h2><span class="n">FAQ</span>よくある質問</h2>
{faq_html(CFG["faq"])}'''
    graph = [
        {"@type": "WebSite", "@id": URL + "#website", "name": NAME, "url": URL, "description": CFG["description"], "inLanguage": "ja", "publisher": PUBLISHER},
        {"@type": "WebPage", "name": NAME, "url": URL, "description": CFG["description"], "isPartOf": {"@id": URL + "#website"}, "dateModified": UPDATED, "publisher": PUBLISHER},
        course_ld(), faq_ld(CFG["faq"]),
    ]
    return write("", f'{NAME} | {CFG["titleSuffix"]}', CFG["description"], body, graph, og_type="website", wide=True)


# ---------------- 信頼ページ・その他 ----------------
TRUST_META = {
    "about": ("このサイトについて", "{name}の運営者と、講座・用語辞典の作り方を説明します。"),
    "sources": ("出典と検証の方法", "{name}で使う出典の基準と、内容の確認方法を説明します。"),
    "disclaimer": ("免責事項", "{name}の利用にあたっての注意事項です。"),
}


def trust_pages():
    urls = []
    for slug, (title, desc) in TRUST_META.items():
        secs = CFG["trust"][slug]
        body = f'<h1>{E(title)}</h1><p class="updated">更新日 {UPDATED}</p>' + "".join(
            f'<h2><span class="n">{i+1:02d}</span>{E(h)}</h2>' + "".join(f"<p>{H_s(p)}</p>" for p in ps) for i, (h, ps) in enumerate(secs))
        url = f"{URL}{slug}/"
        graph = [{"@type": "AboutPage" if slug == "about" else "WebPage", "name": title, "url": url, "inLanguage": "ja",
                  "isPartOf": {"@type": "WebSite", "name": NAME, "url": URL}, "publisher": PUBLISHER, "dateModified": UPDATED}]
        urls.append(write(f"{slug}/", f"{title} | {NAME}", fmt(desc), body, graph, trail=[(title, url)]))
    return urls


def H_s(s):
    """HTML可の文字列（設定の値ではなく文字列そのもの）に置き換えを適用する。"""
    for k, v in (("course", COURSE["title"]), ("chapters", str(N_CH)), ("lessons", str(N_LESSONS)), ("terms", str(len(TERMS))), ("name", NAME)):
        s = s.replace("{" + k + "}", E(v))
    return s


def extras(urls):
    sys.path.insert(0, str(ROOT / "media"))
    from seo import AI_BOTS, INDEXNOW_KEY
    bots = "".join(f"User-agent: {b}\nAllow: /\n\n" for b in AI_BOTS)
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\n{bots}Sitemap: {URL}sitemap.xml\n# AI向けの案内: {URL}llms.txt\n")
    (OUT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY)
    (OUT / "study.js").write_text(STUDY_JS)
    sm = "".join(f"  <url>\n    <loc>{u}</loc>\n    <lastmod>{UPDATED}</lastmod>\n  </url>\n" for u in urls)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sm}</urlset>\n')
    lines = [f"# {NAME}", "", f"> {CFG['description']}", ""] + [fmt(x) for x in CFG["llmsIntro"]] + ["",
             "## 主要ページ", "", f"- トップ: {URL}", f"- 無料講座「{COURSE['title']}」: {CURL}",
             f"- {fmt(CFG['glossaryName'])}: {URL}glossary/",
             f"- このサイトについて: {URL}about/", f"- 出典と検証の方法: {URL}sources/", "",
             "## 講座の目次", ""]
    for c in COURSE["chapters"]:
        lines.append(f'- 第{c["no"]}章 {c["title"]}: {c["desc"]}' + ("" if c["lessons"] else "（準備中）"))
        lines += [f'  - {c["no"]}-{i+1} {l["title"]}: {lurl(l)}' for i, l in enumerate(c["lessons"])]
    others = [s for s in SITES if s.get("live") and s["slug"] != SLUG]
    if others:
        lines += ["", "## SEADICE STUDYの他の講座", ""] + [f'- {s["name"]}: {s["url"]}' for s in others]
    lines += ["", "## 運営", "", "- SEADICE: https://seadice.win/", ""]
    (OUT / "llms.txt").write_text("\n".join(lines))
    body = ('<h1>ページが見つかりません</h1><p class="lead">お探しのページは移動したか、削除された可能性があります。</p>'
            f'<div class="btns"><a class="btn" href="/">{E(NAME)}のトップへ</a><a class="btn sub" href="/course/">講座の目次</a><a class="btn sub" href="/glossary/">用語辞典</a></div>')
    write("_404/", f"ページが見つかりません | {NAME}", "ページが見つかりません。", body, [], noindex=True)
    (OUT / "_404/index.html").replace(OUT / "404.html")
    (OUT / "_404").rmdir()


def build():
    global CSS, FAV
    CSS, FAV = css(), favicon()
    OUT.mkdir(parents=True, exist_ok=True)
    urls = [home(), course_index()]
    for ci, ch in enumerate(COURSE["chapters"]):
        for li in range(len(ch["lessons"])):
            urls.append(lesson(ci, li))
        if complete(ch):
            urls.append(chapter_test(ch))
    if COURSE.get("mock"):
        urls.append(mock_exam())
    if CFG.get("exam"):
        urls.append(exam_corner())
    urls += [glossary()] + [term_page(t) for t in TERMS if rich(t)]
    urls += trust_pages()
    if has_quiz():
        urls.append(quiz_page())
        (OUT / "quiz.js").write_text(QUIZ_JS)
    review_page(); cards_page()  # noindex。sitemap には入れない
    extras(urls)
    return urls


CSS = FAV = ""


def print_warns(warns):
    old = [w for w in warns if "旧形式" in w]
    for w in warns:
        if w not in old: print("警告:", w)
    if old: print(f"警告: 旧形式のレッスン {len(old)} 本（表示はできる。新形式への書き直し候補）: " + ", ".join(w.split()[0] for w in old[:6]) + (" ほか" if len(old) > 6 else ""))


def run(slug, check_only, course_file=None, out=None):
    load(slug, course_file, out)
    errs, warns = check_data()
    if check_only:
        tmp = Path(tempfile.mkdtemp(prefix=f"study-{slug}-"))
        try:
            src = ROOT / CFG["path"]
            # 分野固有の静的アプリ（/c/exam/ など）はリンク検査のために一時ディレクトリへ複製する
            for x in CFG.get("extraNav", []):
                d = x["href"].strip("/").split("/")[0]
                if d and (src / d).exists():
                    shutil.copytree(src / d, tmp / d, dirs_exist_ok=True)
            load(slug, course_file, tmp)
            if not errs:
                build()
                oe, n = check_output(tmp)
                errs += oe
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
        print_warns(warns)
        print("\n".join(errs) if errs else f"check ok {slug} ({N_LESSONS} lessons, {len(TERMS)} terms, 警告 {len(warns)})")
        return not errs
    if errs:
        print("\n".join(errs))
        print(f"{slug}: データ検査で {len(errs)} 件のエラー。生成しません")
        return False
    urls = build()
    oe, n = check_output(OUT)
    print("\n".join(oe) if oe else "", end="\n" if oe else "")
    print(f"built {CFG['path'] if not out else out} ({N_LESSONS} lessons, {len(TERMS)} terms, {len(urls)} pages in sitemap, {n} html, 警告 {len(warns)})")
    return not oe


if __name__ == "__main__":
    a = sys.argv[1:]
    check_only = "--check" in a
    opt = lambda k: a[a.index(k) + 1] if k in a else None
    course_file, out = opt("--course"), opt("--out")
    pos = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] not in ("--course", "--out"))]
    if "--all" in a:
        sites = json.loads((ROOT / "media/study-sites.json").read_text())
        slugs = [s["slug"] for s in sites if s.get("engine", "study") == "study"]
    elif pos:
        slugs = pos[:1]
    else:
        print(__doc__.split("\n\n")[1]); sys.exit(2)
    ok = all([run(s, check_only, course_file, out) for s in slugs])
    sys.exit(0 if ok else 1)
