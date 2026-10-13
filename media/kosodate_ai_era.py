"""AI時代の子育ての柱ページ /ai-era-parenting/。「AI時代の子育てで大事なことは？」という広い問いに1ページで答える。
AIの要約や本でよく見る説を1つずつ、このメディアの記事の出典で判定する。数字は各記事にあるものだけを使う(新しい数字を足さない)。
実行すると media/kosodate-pages.json の ai-era-parenting を書き換える(ほかの固定ページは残す)。
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = "ai-era-parenting"
DATE = "2026-10-13"

# (説, 判定, わかっている度, 研究でわかったこと, 家庭でやること, [(記事slug, リンク文)])
CLAIMS = [
    ("AIの答えを疑う力（批判的思考）を育てる", "大事。根拠あり", "★★☆",
     "4〜6歳の子ども310人の研究では、同じ科学の質問について、先生や友達より音声AIに聞いて、その説明を信じたいと答える子が多くいました。6〜10歳では、AIが作った文章や画像を人が作ったものと見分ける力が大人より低いこともわかっています。確かめる力は放っておいても育ちにくい一方、ネットの情報の確かめ方を1時間の授業6回で教えた高校では、判断する力がはっきり伸びました。「AIにわざと間違えさせて親子で探す」遊びそのものを試した研究は見つかっておらず、間違いを見せるだけより「なぜ間違いか」を説明させる方が効果が上がっています。",
     "AIの答えを見たら「本当かな？ どこで確かめる？」と一緒に別の情報源を開く。間違いを見つけたら「なぜ間違いだと思う？」と理由を言わせる。",
     [("child-ai-critical-thinking-fact-check", "子どもがAIの答えを鵜呑みにしないか心配。疑う力は育てられる？"),
      ("ai-voice-assistant-child-trust", "子どもはAIの答えをどれだけ信じる？"),
      ("ai-book-report-homework-help", "読書感想文・自由研究にAIはどこまでOK？")]),
    ("やり抜く力（グリット）や成長マインドセットを鍛える", "効果は思われているより小さい", "★★☆",
     "やり抜く力や成長マインドセットを鍛える教育プログラムの効果は、大規模な分析では小さいとわかっています。将来との関連を長く追った研究で根拠が強いのは「自己制御」で、子ども時代の自己制御の高さは32歳時点の健康・お金・犯罪歴と関連していました。",
     "教材やプログラムに頼るより、おやつの前に少し待つ・順番を守るといった「待つ」小さな練習を日常に入れる。",
     [("non-cognitive-skills-kids", "AI時代に伸ばしたい子どもの力は何？「非認知能力」の中身")]),
    ("創造力・試行錯誤する力を伸ばす", "大事だが、鍛え方の効果は小さめ", "★☆☆",
     "創造力トレーニングの効果は、169件の研究をまとめた2024年の分析で、これまで報告されてきたより小さい可能性が高いとわかりました。生成AIのアイデアを借りると、大人の実験では作品の評価は上がった一方、ほかの人の作品と似通いやすくなりました。",
     "先にAIに案を出させず、まず自分で考えてから比べる順番にする。メディアの「ながら使い」を減らす。",
     [("creativity-training-ai-era", "AI時代に伸ばしたい「創造力」は鍛えられる？")]),
    ("宿題・読書感想文をAIに丸投げさせない", "大事。根拠あり", "★★★",
     "高校生約1,000人の実験で、答えまで出すAIで練習した生徒は、AIなしのテストで成績が17%下がりました。ヒントだけを出すように作ったAIでは、低下はほとんど防げました。文部科学省の指針も、AIの生成物をそのまま自分の作品として出すことを「不適切又は不正な行為」としています。",
     "「答えは聞かない。ヒントだけ聞く」を家のルールにする。どこまでAI、どこから自分の頭かを宿題ごとに決める。",
     [("homework-ai-thinking-skills", "宿題にAIを使わせると考える力は落ちる？"),
      ("ai-answers-memory-retention", "AIに聞けば覚えなくていい？")]),
    ("親が関わり、使い方のルールを話し合う", "大事。根拠あり", "★★☆",
     "小中高生約1万1千人の調査では、AIを使う力の高さは、家庭の経済状況より、親の関わりや学校の支援との関連の方が強くみられました。米国の12〜13歳約1万人の調査では、利用時間を把握し上限を決めている家庭ほど問題のある使い方が少なく、ご褒美や罰に使うことは長い利用と関連していました。",
     "ルールは親が一方的に決めず、子どもと話して紙に書く。端末を見るなら先に約束し、年齢とともに任せる範囲を広げる。",
     [("ai-literacy-gap-academic-achievement", "AIで学力の差は広がる？"),
      ("parent-ai-monitoring-how-much", "子どものAI利用、親はどこまで見る？")]),
    ("AIに悩みを相談させない", "禁止より「人にも話せる」関係", "★★☆",
     "米国の12〜21歳を対象にした2025年の調査では、19.2%がAIに心の悩みを相談し、そのうち63.3%は誰にも話していませんでした。子どもの危機を想定した相談で、友達役のAIが具体的な相談先を示せた返答は11.1%でした。",
     "「AIに話したことも、話していいよ」と伝えておく。命に関わる悩みは、人につなぐ。",
     [("ai-chatbot-worry-consultation-safety", "子どもがAIに悩み相談。安全？")]),
    ("「好き」や好奇心を深掘りさせ、将来から逆算しない", "研究はまだ少ない", "★☆☆",
     "「好き」を深掘りした子がAI時代に有利になるかを直接追った研究は、このメディアでは見つかっていません。わかっているのは、小学生の将来の夢は変わりやすく、2年の間に約6割が夢を少なくとも1つ変えていたことです。",
     "夢を早く決めさせず、親が見せる職業や体験の幅を広げる。",
     [("no-career-dream-elementary-school", "小学生で将来の夢がない。大丈夫？")]),
]

FAQ = [
    ("AI時代の子育てで一番大事なことは？",
     "研究で根拠がそろっているのは、AIを答えでなくヒントとして使わせることと、親が関わってルールを話し合うことです。答えまで出すAIで練習した高校生は、AIなしのテストで成績が17%下がりました。子どものAIを使う力は、家庭の経済状況より親の関わりとの関連が強くみられました。"),
    ("やり抜く力（グリット）を鍛えれば、AI時代に強い子になる？",
     "やり抜く力や成長マインドセットを鍛える教育プログラムの効果は、大規模な分析では思われているより小さいとわかっています。将来との関連で根拠が強いのは自己制御で、家庭では「待つ」小さな練習を日常に入れるのが基本です。"),
    ("子どもにAIの答えを疑う力は必要？",
     "必要です。4〜6歳では先生や友達より音声AIの説明を信じたいと答える子が多く、6〜10歳ではAIが作った文章や画像を見分ける力が大人より低いことがわかっています。AIの答えを見たら、一緒に別の情報源で確かめる習慣が手がかりになります。"),
]


def build():
    rows = "".join(
        f'<tr><td><a href="#c{i}">{c}</a></td><td>{v}</td><td class="lv">{s}</td></tr>'
        for i, (c, v, s, *_r) in enumerate(CLAIMS, 1))
    items = ""
    for i, (c, v, s, found, todo, links) in enumerate(CLAIMS, 1):
        ls = "".join(f'<p class="ml"><a href="/{slug}/">詳しく：{t}</a></p>' for slug, t in links)
        items += (f'<li id="c{i}"><p class="mh"><strong>{c}</strong><span class="lv" title="わかっている度">わかっている度 {s}</span></p>'
                  f'<p><b>判定：{v}。</b>{found}</p><p><b>家庭でやること：</b>{todo}</p>{ls}</li>\n')
    body = f"""<p class="lead2">結論：AI時代の子育てで研究の根拠がそろっているのは、①AIを答えでなくヒントとして使わせる、②AIの答えを一緒に確かめる、③親が関わってルールを話し合う、の3つです。よく勧められる「やり抜く力を鍛える教材」の効果は、思われているより小さいとわかっています。</p>
<p>AI時代の子育てについて、AIの要約や本・動画でよく見る説を1つずつ取り上げ、このメディアの記事で確かめた研究と公的な指針で判定しました。数字はすべて、リンク先の記事で出典（論文・公的資料）を確認できるものだけを載せています。</p>
<p class="note">「わかっている度」は研究の量と質から判断した3段階の目安です（★★★は研究の結果がそろっているもの、★☆☆は研究が少ない・結果が分かれているもの）。</p>
<h2>よく聞く説と判定（一覧）</h2>
<div class="tw"><table class="ct"><thead><tr><th>よく聞く説</th><th>判定</th><th>わかっている度</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>1つずつ確かめる</h2>
<ol class="mlist">
{items}</ol>
<h2>今日からできること</h2>
<p>読んで終わりにせず、家庭で使える道具を用意しています。どれも無料・登録不要で、入力した内容は外に送られません。</p>
<ul class="tl">
<li><a href="/rules/">わが家のAI・スマホのルールづくり</a>：年齢を選ぶと、宿題でのAIの使い方などを決めて印刷できるルール表ができます。</li>
<li><a href="/check/">子どものAI・スマホの悩みチェック</a>：当てはまる悩みを選ぶと、親が今日やることがわかります。</li>
<li><a href="/sns-practice/">子ども向けSNSの練習</a>：知らない人のDMなど20場面を、親子で体験できます。</li>
<li><a href="/screen-time-check/">スクリーンタイム判定</a>：利用時間を年齢別の目安と比べます。</li>
</ul>
<h2>年齢ごとに知りたいとき</h2>
<p><a href="/guide/">年齢別ガイド</a>（0〜2歳・3〜5歳・小学生・中高生）、<a href="/ai/">子どもとAI 10の問い</a>、<a href="/dos/">研究でわかった、親がやるといいこと</a>もあわせてどうぞ。</p>
<h2>よくある質問</h2>
<dl class="qa">{''.join(f'<dt>{q}</dt><dd>{a}</dd>' for q, a in FAQ)}</dl>
<p class="note">このページは「SEADICE」が運営する「AI時代の子育て」の記事から、研究と公的な指針で確かめた結論だけをまとめたものです。商品の紹介はしていません。最終確認日：{DATE}</p>"""
    css = (".mlist{padding-left:1.4em}.mlist li{margin:0 0 26px}.mlist p{margin:4px 0}.mh{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:baseline}"
           ".lv{font-size:12px;color:var(--accent);white-space:nowrap}.mh .lv{border:1px solid var(--accent);border-radius:999px;padding:1px 9px}"
           ".ml{font-size:14px}.lead2{font-weight:600}.tw{overflow-x:auto}.ct{border-collapse:collapse;width:100%;font-size:14px}"
           ".ct th,.ct td{border-bottom:1px solid var(--line,#ddd);padding:10px 8px;text-align:left;vertical-align:top}.ct a{display:inline-block;padding:2px 0}"
           ".tl li{margin:0 0 12px}.qa dt{font-weight:700;margin-top:16px}.qa dd{margin:4px 0 0}")
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}
    head = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False, separators=(",", ":")) + "</script>"
    return {"path": PATH, "title": "AI時代の子育てで大事なことは？よく聞く7つの説を研究で確かめた",
            "seo_title": "AI時代の子育てで大事なこと｜よく聞く7つの説を研究で判定（出典つき）",
            "desc": "AI時代の子育てで大事なことは？批判的思考・やり抜く力・創造力・宿題とAI・ルール・悩み相談・好きを伸ばす、の7つの説を研究と公的な指針で判定。根拠がそろうのは、AIをヒントとして使わせる・一緒に確かめる・親が関わってルールを話し合うことでした。",
            "date": DATE, "css": css, "head": head, "body": body}


if __name__ == "__main__":
    f = ROOT / "media/kosodate-pages.json"
    ps = json.loads(f.read_text())
    keep = [p for p in ps if p["path"] != PATH]
    f.write_text(json.dumps(keep + [build()], ensure_ascii=False, indent=2) + "\n")
    print("wrote", PATH)
