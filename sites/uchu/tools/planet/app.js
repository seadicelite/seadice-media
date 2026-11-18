"use strict";
/* 1000億分の1の惑星 — 銀河のどこかの惑星に生まれて、一生を見届ける。
   数字は公開データと論文の見積もり。わからないところは「分かれ道」にして、選ぶかサイコロに任せる。
   記録はこの端末（localStorage）だけ。サーバーには何も送らない。 */

const $ = (s) => document.querySelector(s);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const R = Math.random;
const pick = (arr) => arr[Math.floor(R() * arr.length)];
const between = (a, b) => a + R() * (b - a);
const logBetween = (a, b) => Math.exp(between(Math.log(a), Math.log(b)));
function weighted(pairs) { let s = 0; for (const p of pairs) s += p[1]; let x = R() * s; for (const p of pairs) { x -= p[1]; if (x <= 0) return p[0]; } return pairs[pairs.length - 1][0]; }

const TAG = { sure: "確か", est: "推定", unk: "わからない", mark: "目印" };

/* ---------- 出典（本文の [n] と対応） ---------- */
const SOURCES = {
  nasa: "NASA Exoplanet Archive, Planetary Systems Composite Parameters（2026-10-20取得）",
  cassan: "Cassan et al. 2012, Nature 481, 167（銀河の星は平均1個以上の惑星を持つ）",
  reyle: "Reylé et al. 2021, A&A 650, A201（太陽から10パーセク以内の星の数え上げ）",
  fressin: "Fressin et al. 2013, ApJ 766, 81（ケプラーによる惑星の数の見積もり）",
  dressing: "Dressing & Charbonneau 2015, ApJ 807, 45（赤色矮星のまわりの惑星の数）",
  chen: "Chen & Kipping 2017, ApJ 834, 17（惑星の大きさと重さの関係）",
  madau: "Madau & Dickinson 2014, ARA&A 52, 415（宇宙で星が生まれた量の歴史）",
  fischer: "Fischer & Valenti 2005, ApJ 622, 1102（重い元素が多い星ほど巨大惑星を持ちやすい）",
  haisch: "Haisch, Lada & Lada 2001, ApJ 553, L153（惑星を生む円盤は数百万年で消える）",
  planck: "Planck Collaboration 2020, A&A 641, A6（宇宙の中身の割合）",
  rogers: "Rogers & Seager 2010, ApJ 712, 974（同じ大きさと重さでも中身は何通りもありうる）",
  fulton: "Fulton et al. 2017, AJ 154, 109（地球の1.5〜2倍の大きさの惑星が少ない「谷」）",
  greene: "Greene et al. 2023, Nature 618, 39 / Zieba et al. 2023, Nature 620, 746（TRAPPIST-1b・cに厚い大気は見えない）",
  kreidberg: "Kreidberg et al. 2019, Nature 573, 87（LHS 3844bに厚い大気はない）",
  zahnle: "Zahnle & Catling 2017, ApJ 843, 122（大気が残る惑星と残らない惑星の境目）",
  kopparapu: "Kopparapu et al. 2013, ApJ 765, 131（液体の水がありうる範囲）",
  gough: "Gough 1981, Solar Physics 74, 21（若い太陽は今より約3割暗かった）",
  schulte: "Schulte et al. 2010, Science 327, 1214（6600万年前の天体衝突と大量絶滅）",
  gehrels: "Gehrels et al. 2003, ApJ 585, 1169（近くの超新星がオゾン層に与える影響）",
  stevenson: "Stevenson 1999, Nature 400, 32（星を持たない惑星でも水が液体でいられる可能性）",
  sumi: "Sumi et al. 2023, AJ 166, 108（星を持たない惑星は、小さなものを含めると星1個あたり約20個という見積もり。幅が大きい）",
  rasio: "Rasio & Ford 1996, Science 274, 954（惑星どうしの重力の乱れで、惑星が放り出されることがある）",
  canup: "Canup & Asphaug 2001, Nature 412, 708（月は大きな天体の衝突でできたという説）",
  dawson: "Dawson & Johnson 2018, ARA&A 56, 175（ホットジュピターがどこから来たか）",
  luger: "Luger & Barnes 2015, Astrobiology 15, 119（赤色矮星は若いころほど明るく、近くの惑星は水を失いやすい）",
  kalirai: "Kalirai et al. 2008, ApJ 676, 594（年老いた星は外側を吹き飛ばして軽くなる）",
  sawala: "Sawala et al. 2025, Nature Astronomy（天の川銀河とアンドロメダ銀河が100億年以内にぶつかる確率は約半々）",
  schroder: "Schröder & Smith 2008, MNRAS 386, 155（年老いた太陽に地球は飲み込まれるか）",
  laughlin: "Laughlin, Bodenheimer & Adams 1997, ApJ 482, 420（軽い星は何兆年も燃え、まだ一つも燃え尽きていない）",
  vanderburg: "Vanderburg et al. 2020, Nature 585, 363（白色矮星のまわりを回る巨大惑星 WD 1856+534 b）",
  k218: "Madhusudhan et al. 2025, ApJL 983, L40 とその反論（K2-18bの大気の成分をめぐって意見が割れている）",
  caldeira: "Caldeira & Kasting 1992, Nature 360, 721（太陽が明るくなると二酸化炭素が減り、植物から先に生きられなくなる）",
  omalley: "O'Malley-James et al. 2013, Int. J. Astrobiology 12, 99（生き物の終わりは大きなものから。最後に残るのは微生物）",
  gould: "Gould 1989『ワンダフル・ライフ』（カンブリア紀の化石から、生命の歴史をやり直したら同じ結果にはならないと論じた）／ Conway Morris 2003『Life\'s Solution』（似た条件なら似た生き物に行き着きやすい）",
  walker: "Walker, Hays & Kasting 1981, JGR 86, 9776（岩と海が二酸化炭素を出し入れして、温度を保つ働き）",
  hoffman: "Hoffman et al. 1998, Science 281, 1342（地球全体が凍った時代があった）",
  raup: "Raup & Sepkoski 1982, Science 215, 1501（地球の歴史で起きた大量絶滅）",
  lyons: "Lyons, Reinhard & Planavsky 2014, Nature 506, 307（地球の大気に酸素が増えた歴史）",
  kiang: "Kiang et al. 2007, Astrobiology 7, 252（赤色矮星の光の下の光合成は、赤外線に近い光を使うかもしれない）",
  barnes: "Barnes 2017, Celest. Mech. Dyn. Astron. 129, 509（星に近い惑星は片面だけを星に向ける）",
};

/* ---------- 架空の名前 ---------- */
const SYL = ["ア","イ","ウ","エ","オ","カ","キ","ク","ケ","コ","サ","シ","ス","セ","ソ","タ","テ","ト","ナ","ニ","ノ","ハ","ヒ","フ","ホ","マ","ミ","ム","メ","モ","ユ","ラ","リ","ル","レ","ロ","ヴァ","ゼ","ガ","ド","ベ","ポ","ティ","ジュ"];
const END = ["ン","ス","ア","ル","ラ","ナ","","",""];
function makeName(n) { let s = ""; for (let i = 0; i < n; i++) s += pick(SYL); return s + pick(END); }

/* ---------- 星と惑星のつくり ---------- */
const STAR_TYPES = [
  // 型, 割合（太陽の近くの数え上げのおおよそ）, 質量の範囲（太陽=1）, 色
  { t: "M", name: "赤色矮星", w: 73, m: [0.08, 0.5], c: "#ff8a5c" },
  { t: "K", name: "オレンジ色の星", w: 13, m: [0.5, 0.85], c: "#ffb070" },
  { t: "G", name: "太陽に似た星", w: 7.5, m: [0.85, 1.1], c: "#ffe08a" },
  { t: "F", name: "白っぽい黄色の星", w: 3, m: [1.1, 1.5], c: "#fff3c4" },
  { t: "A", name: "白い星", w: 0.6, m: [1.5, 2.5], c: "#e3ebff" },
  { t: "B", name: "青白い重い星", w: 0.13, m: [2.5, 12], c: "#b9c9ff" },
];
const KINDS = {
  rocky: { name: "地球サイズの岩の惑星", r: [0.5, 1.25] },
  superE: { name: "スーパーアース（大きな岩の惑星）", r: [1.25, 2] },
  subnep: { name: "サブネプチューン（水素をまとった小さな惑星）", r: [2, 4] },
  nep: { name: "海王星のような氷の巨大惑星", r: [4, 7] },
  giant: { name: "木星のようなガスの巨大惑星", r: [8, 15] },
};
function starLum(M) { // 主系列のまんなか頃の明るさ（太陽=1）
  if (M < 0.43) return 0.23 * Math.pow(M, 2.3);
  if (M < 2) return Math.pow(M, 4);
  return 1.4 * Math.pow(M, 3.5);
}
function massFromRadius(kind, r) { // Chen & Kipping 2017 の関係をおおまかに
  if (r < 1.23) return Math.pow(r, 1 / 0.279);
  if (kind === "giant") return between(60, 1500);
  return 2 * Math.pow(r / 1.23, 1 / 0.589);
}

// 宇宙のいつ生まれたか: 星が多く生まれた時代ほど選ばれやすい（Madau & Dickinson 2014）
function sampleBirthGyr() {
  const H = 14.44, OL = 0.69, OM = 0.31, k = 1.5 * Math.sqrt(OL) / H;
  const pairs = [];
  for (let t = 0.4; t <= 13.8; t += 0.1) {
    const opz = Math.pow(Math.sqrt(OL / OM) / Math.sinh(k * t), 2 / 3);
    const psi = Math.pow(opz, 2.7) / (1 + Math.pow(opz / 2.9, 5.6));
    pairs.push([t, psi]);
  }
  return clamp(weighted(pairs) + between(-0.05, 0.05), 0.4, 13.8);
}

function compositionFor(kind) { // 質量の割合の目安（%）。「わからない」は中身を決めきれない幅の目安
  const j = () => between(-4, 4);
  const c = {
    rocky: { iron: 30 + j(), rock: 58 + j(), water: 2, gas: 0, unk: 10 },
    superE: { iron: 26 + j(), rock: 45 + j(), water: 4, gas: 0, unk: 25 },
    subnep: { iron: 14, rock: 28 + j(), water: 10, gas: 8, unk: 40 },
    nep: { iron: 6, rock: 10, water: 44 + j(), gas: 10, unk: 30 },
    giant: { iron: 2, rock: 4, water: 4, gas: 70 + j(), unk: 20 },
  }[kind];
  return normalize(c);
}
function normalize(c) { const s = c.iron + c.rock + c.water + c.gas + c.unk; for (const k in c) c[k] = (c[k] / s) * 100; return c; }

function makePlanet(opts) {
  const galaxy = opts.galaxy || makeName(2) + "銀河";
  const rogue = !opts.forceM && opts.rogue && R() < 0.5;
  // 宇宙の画面で選んだ星から来たときは、その星の重さを使う
  const st = opts.forceM ? (STAR_TYPES.find((t) => opts.forceM < t.m[1]) || STAR_TYPES[STAR_TYPES.length - 1]) : weighted(STAR_TYPES.map((s) => [s, s.w]));
  const M = opts.forceM || between(st.m[0], st.m[1]);
  const star = { type: st.t, typeName: st.name, color: st.c, M, Lmid: starLum(M), tMS: 10 * M / starLum(M) * (M < 0.35 ? 7 : 1), name: opts.starName || makeName(2) };
  // 種類の割合は Fressin 2013・Dressing & Charbonneau 2015 の傾向（小さい惑星ほど多い、赤色矮星では巨大惑星が少ない）を丸めた目安。
  // 重い元素が少ない昔の宇宙では巨大惑星を減らす（Fischer & Valenti 2005 の傾向）
  const born = opts.forceBorn != null ? opts.forceBorn : opts.now ? 13.8 : sampleBirthGyr();
  const g = born < 1 ? 0.2 : born < 3 ? 0.6 : 1; // 宇宙の画面と同じ目安
  const kind = opts.forceKind ? opts.forceKind : st.t === "M"
    ? weighted([["rocky", 40], ["superE", 34], ["subnep", 21], ["nep", 3], ["giant", 2 * g]])
    : weighted([["rocky", 26], ["superE", 30], ["subnep", 28], ["nep", 7], ["giant", 9 * g]]);
  const r = between(KINDS[kind].r[0], KINDS[kind].r[1]);
  const scale = Math.sqrt(star.Lmid);
  const a = opts.forceA ? opts.forceA : kind === "giant" || kind === "nep" ? logBetween(0.03, 20) * Math.cbrt(M) : logBetween(0.012, 2.5) * Math.max(scale, Math.cbrt(M) * 0.3);
  return {
    name: makeName(3), letter: opts.forceLetter || pick(["b", "c", "d", "e", "f"]), galaxy, star, rogue: false, rogueBorn: rogue, kind, r, m: massFromRadius(kind, r), a,
    born, comp: compositionFor(kind),
    atm: kind === "giant" || kind === "nep" || kind === "subnep" ? 4 : r < 0.7 ? 1 : 2,
    waterInv: kind === "rocky" || kind === "superE" ? "some" : "deep",
    locked: false, life: "unknown", impacts: 0, flares: false, starPhase: "ms",
    starL: star.Lmid, alive: true, endReason: null,
  };
}

/* ---------- その時の状態 ---------- */
function luminosityAt(P, age) {
  const s = P.star;
  if (P.rogue || P.ejected) return 0;
  if (s.phase === "wd") return 0.001;
  if (s.phase === "giant") return 1500 * Math.pow(s.M, 1.5);
  const x = clamp(age / s.tMS, 0, 1);
  // 主系列では年をとるほど明るくなる（Gough 1981 を一般化した目安）。赤色矮星は生まれてしばらく、主系列に落ち着くまでずっと明るい（Luger & Barnes 2015）
  const pms = s.M < 0.5 ? 30 * Math.exp(-age / 0.05) + 2 * Math.exp(-age / 0.5) : 0;
  return (s.Lmid / 1.5) * (1 + 1.3 * Math.pow(x, 1.2) + pms);
}
function flux(P, age) { const L = luminosityAt(P, age); return L / (P.a * P.a); }
function surface(P, age) {
  const S = flux(P, age);
  if (P.rogue || P.ejected) {
    const inner = P.atm === 4 ? 60 : 30; // 内部の熱だけ。水素の厚い大気なら地表は暖かいかもしれない（Stevenson 1999）
    return { S: 0, T: inner + (P.rogueOcean ? 250 * Math.exp(-age / 10) : 0) };
  }
  const albedo = P.water === "ice" ? 0.6 : 0.3;
  const teq = 278.6 * Math.pow(S * (1 - albedo), 0.25);
  const green = [0, 5, 33, 0.8 * teq, 0][P.atm] || 0;
  let T = teq + green;
  // 液体の水がありうる範囲で、地球くらいの大気と水があれば、炭素の循環が温度を保つ（Walker et al. 1981）
  if (P.carbon === true && P.atm === 2 && P.waterInv !== "none" && S > 0.36 && S < 1.1) {
    const w = Math.min(1, (S - 0.36) / 0.15, (1.1 - S) / 0.15);
    T = T + (288 - T) * 0.8 * w;
  }
  return { S, T, teq };
}
function waterState(P, T) {
  if (P.rogueOcean) return T > 273 ? "ocean" : "ice";
  if (P.atm === 4) return "deep";
  if (P.waterInv === "none") return "none";
  if (P.atm === 0) return T < 200 ? "ice" : "none";
  if (T < 268) return "ice";
  if (T < 373) return P.waterInv === "global" ? "global" : "ocean";
  return "steam";
}
const WATER_WORD = { none: "なし（からから）", ice: "氷", ocean: "液体の海", global: "陸のない海", steam: "水蒸気", deep: "奥深くにあるかもしれない" };
const ATM_WORD = ["なし", "薄い", "地球くらい", "厚い（温室効果が強い）", "水素とヘリウムの厚い衣"];

/* ---------- 年の表し方 ---------- */
function fmtYears(gyr) {
  const y = gyr * 1e9;
  if (y < 1e4) return Math.round(y).toLocaleString("ja-JP") + "年";
  if (y < 1e8) return Math.round(y / 1e4).toLocaleString("ja-JP") + "万年";
  if (y < 1e12) return (Math.round(y / 1e7) / 10).toLocaleString("ja-JP") + "億年";
  return (Math.round(y / 1e11) / 10).toLocaleString("ja-JP") + "兆年";
}
function fmtUniverse(u) {
  if (Math.abs(u - 13.8) < 0.05) return "宇宙の「今」";
  return u < 13.8 ? `今から${fmtYears(13.8 - u)}前` : `今から${fmtYears(u - 13.8)}後`;
}

/* ---------- 出来事の台本 ---------- */
function buildScript(P) {
  const ev = [];
  const s = P.star;
  const add = (t, f) => ev.push({ t, ...f });
  const small = P.kind === "rocky" || P.kind === "superE";

  add(1e-5, { tag: "sure", src: ["haisch"], title: "ガスと塵の円盤の中で、生まれはじめた",
    text: P.rogueBorn ? "生まれた場所は、ある星のまわりの円盤。けれどこの惑星は、のちに星から離れていく。" : `${s.name}（${s.typeName}）のまわりの円盤で、塵が集まりはじめた。こうした円盤は望遠鏡で実際に見えている。` });
  add(2e-5, { tag: "unk", src: ["planck"], title: "銀河の重さの大半は、正体がわからない",
    text: `${P.galaxy}を形づくる重さの多くは、光らない「暗黒物質」だと考えられている。宇宙の中身の約95%（暗黒エネルギー約68%と暗黒物質約26%、Planck 2018 の値から計算）は、正体がまだわかっていない。` });
  if (P.born < 3) add(3e-5, { tag: "est", src: ["fischer"], title: "重い元素が少ない時代に生まれた",
    text: "宇宙の初めのころは、岩や鉄のもとになる重い元素がまだ少なかった。今の星では、重い元素が少ない星ほど巨大惑星を持ちにくい。この時代にどこまで惑星ができたかは、よくわかっていない。" });
  add(between(1, 10) * 1e-3, { tag: "sure", src: ["haisch"], title: "円盤のガスが消えた",
    text: P.atm === 4 ? "ガスが消える前に、まわりの水素とヘリウムをまとうことができた。" : "ガスが消えるのは数百万年ほど。ここから先、大気は自分の中から出てくるガスと、外から届くものしだい。" });
  add(1.5e-3, { tag: "unk", src: ["rogers"], title: "自分の中身は、外からは決めきれない",
    text: "同じ大きさと重さでも、鉄・岩・水・ガスの組み合わせは何通りも考えられる。成分の「わからない」部分は、その幅の目安。" });

  if (P.rogueBorn) {
    add(between(0.005, 0.1), { tag: "est", src: ["rasio", "sumi"], kind: "eject", title: "重力に振り回されて、星から放り出された",
      text: "ほかの惑星との重力の引っぱり合いで、星のまわりから飛び出した。星を持たない惑星は、小さなものまで含めると恒星より多いかもしれないという見積もりがある。" });
    add(between(0.15, 0.6), { tag: "unk", src: ["stevenson"], kind: "rogueOceanBranch", branch: true, title: "星の光のない場所に、海はあるか" });
  }
  if (small) {
    if (R() < 0.6) add(between(0.01, 0.1), { tag: "est", src: ["canup"], kind: "giantImpact", title: "火星くらいの天体がぶつかった",
      text: "惑星ができる最後の時期には、大きな天体どうしの衝突が起きやすい。地球の月も、こうした衝突でできたという説が有力（確かめられてはいない）。" });
    if (s.type === "M" && !P.rogueBorn) add(between(0.02, 0.3), { tag: "unk", src: ["luger", "greene", "kreidberg", "zahnle"], kind: "flareBranch", title: "星の激しいフレアを浴び続けた", branch: true });
    add(between(0.05, 0.4), { tag: "unk", src: [], kind: "waterBranch", title: "水はどれだけ届いたか", branch: true });
    if (!P.rogueBorn) add(between(0.4, 0.6), { tag: "unk", src: ["walker"], kind: "carbonBranch", title: "炭素の循環は働いているか", branch: true });
  }
  if (P.kind === "subnep" && !P.rogueBorn && s.Lmid / (P.a * P.a) > 5) add(between(0.1, 1), { tag: "unk", src: ["fulton"], kind: "envelopeBranch", title: "水素の衣は残ったか", branch: true });
  if (P.kind === "giant" && P.a < 0.1 && !P.rogueBorn) add(between(0.002, 0.05), { tag: "est", src: ["dawson"], title: "星のすぐそばまで移動してきた",
    text: "巨大なガスの惑星がここまで星に近いのは、遠くで生まれて内側へ移動してきたからだと考えられている（ホットジュピター）。どう移動したかは説が分かれる。" });
  if (!P.rogueBorn && P.a < 0.3 * Math.cbrt(s.M)) add(between(0.1, 1), { tag: "est", src: ["barnes"], kind: "lock", title: "片面だけが星を向くようになった",
    text: "星の重力に引かれて自転がゆっくりになり、昼の面と夜の面が決まった。" });

  // 天体の衝突（代表的なものだけ）。若いころほど多い
  const lifeSpan = Math.min(s.tMS, 2000);
  const nImp = 2 + Math.floor(R() * 3);
  for (let i = 0; i < nImp; i++) {
    const t = logBetween(0.05, Math.max(0.2, lifeSpan));
    add(t, { tag: "est", src: ["schulte"], kind: "impact", size: t < 1 ? pick([10, 20, 50]) : pick([1, 5, 10]) });
  }
  if (R() < 0.35) add(logBetween(0.1, Math.min(lifeSpan, 1000)), { tag: "est", src: ["gehrels"], kind: "supernova", title: "近くの星が超新星爆発を起こした", near: R() < 0.3 });
  if (R() < 0.1) add(logBetween(0.2, Math.min(lifeSpan, 1000)), { tag: "est", src: [], kind: "passStar", title: "ほかの星がすぐ近くを通り過ぎた" });
  if (!P.rogueBorn && (P.kind === "giant" || P.kind === "nep" || P.a > 3) && R() < 0.08) add(between(0.05, 2), { tag: "est", src: ["rasio"], kind: "eject", title: "重力に振り回されて、星から放り出された",
    text: "となりの惑星との重力の引っぱり合いで、軌道から飛び出した。ここからは星の光のない旅になる。" });

  add(between(0.3, 1.2), { tag: "unk", src: [], kind: "lifeBranch", branch: true, title: "生命は生まれたか" });
  if (R() < 0.25) add(between(1, Math.min(lifeSpan, 8)), { tag: "unk", src: ["k218"], kind: "mystery", branch: true, title: "大気に、正体のわからない成分の手がかり" });

  // 宇宙の「今」と、銀河どうしの衝突
  if (P.born < 13.8) add(13.8 - P.born, { tag: "mark", src: [], kind: "now", title: "宇宙の「今」に追いついた" });
  const mergeU = 13.8 + between(4, 15);
  if (mergeU > P.born && R() < 0.4) add(mergeU - P.born, { tag: "unk", src: ["sawala"], kind: "mergeBranch", branch: true, title: "となりの銀河とぶつかるかもしれない" });

  // 星の最期
  if (s.M >= 8) add(s.tMS, { tag: "est", src: [], kind: "starSN", title: `${s.name}が超新星爆発を起こした` });
  else if (s.M >= 0.5) {
    add(s.tMS * 0.97, { tag: "est", src: ["gough"], kind: "brighten", title: `${s.name}が明るくなってきた` });
    add(s.tMS, { tag: "unk", src: ["schroder"], kind: "redGiant", title: `${s.name}が赤色巨星にふくらんだ` });
    add(s.tMS * 1.12, { tag: "est", src: ["kalirai", "vanderburg"], kind: "whiteDwarf", title: `${s.name}が白色矮星になった` });
  } else {
    add(Math.min(s.tMS, 13.8 - P.born + 5) , { tag: "est", src: ["laughlin"], kind: "longLife", title: `${s.name}は、まだまだ燃え続ける` });
    add(s.tMS, { tag: "est", src: ["laughlin"], kind: "whiteDwarf", title: `${s.name}が、ついに燃え尽きた`, longLived: true });
  }
  if (s.M >= 0.5 && s.M < 8) add(s.tMS * 0.6, { tag: "est", src: ["kopparapu", "gough"], kind: "hzCheck", title: `${s.name}が少しずつ明るくなる` });

  ev.sort((x, y) => x.t - y.t);
  return ev;
}

function endAgeFor(P) {
  const s = P.star;
  if (P.rogueBorn || P.ejected) return 60;
  if (s.M >= 8) return s.tMS * 1.001;
  return s.tMS * 1.25;
}

/* ---------- 分かれ道 ---------- */
// 各選択肢: [ラベル, 説明, 効果]。サイコロの確率は本当の値がわからないので、すべて同じ確率にしている
function branchFor(P, e, age) {
  const sf = surface(P, age);
  switch (e.kind) {
    case "flareBranch":
      return { q: `${P.star.name}のような赤色矮星は、若いころ激しいフレアを何度も起こす。大気は残ったか。`,
        note: "赤色矮星は若いころ明るく、フレアも多い。JWST などの観測では、赤色矮星に近い岩の惑星 TRAPPIST-1b・c や LHS 3844b に厚い大気は見えていない。もっと離れた惑星ではわかっていない。",
        opts: [["大気が残った", "地球のような大気を保った", () => { P.atm = 2; }], ["はぎ取られた", "大気がなくなり、むき出しの岩になった", () => { P.atm = 0; }]] };
    case "waterBranch":
      return { q: "水は、氷を含む小さな天体がぶつかって届いたのか、もともと材料に入っていたのか。どれだけ届いたかはわからない。",
        note: "地球の水がどこから来たかも、まだ決着していない。",
        opts: [["からからのまま", "水はほとんどない", () => { P.waterInv = "none"; P.comp.water = 0.1; }], ["地球くらい", "海と陸がある量", () => { P.waterInv = "some"; }], ["陸のない海", "全体が深い海に包まれる", () => { P.waterInv = "global"; P.comp.water = 20; normalize(P.comp); }]] };
    case "envelopeBranch":
      return { q: "星の光で、水素の衣は宇宙へ逃げていったか。",
        note: "地球の1.5〜2倍の大きさの惑星が少ない「谷」は観測で確かめられている。衣が逃げたからだと考えられているが、逃げ方の仕組みは説が分かれる。",
        opts: [["残った", "サブネプチューンのまま", () => {}], ["逃げた", "岩の芯がむき出しのスーパーアースになった", () => { P.kind = "superE"; P.atm = 1; P.r = Math.min(P.r, 1.8); P.comp.gas = 0; normalize(P.comp); }]] };
    case "carbonBranch":
      if (P.atm !== 2 || P.waterInv === "none") return null;
      return { q: "地球では、火山が出す二酸化炭素と、岩が雨で溶けて二酸化炭素を吸い取る働きがつり合い、長いあいだ温度が保たれてきたと考えられている。この惑星でも、この働きはあるか。",
        note: "この働きには火山や陸の岩、もしかするとプレートの動きが要る。ほかの惑星で働くかは確かめられていない。地球でさえ、全体が凍った時代があった。",
        opts: [["働いている", "暗い時代も明るい時代も、温度が地球くらいに近づく", () => { P.carbon = true; }], ["働いていない", "温度は星の光と大気しだいで決まる", () => { P.carbon = false; }]] };
    case "rogueOceanBranch":
      if (P.kind !== "rocky" && P.kind !== "superE") return null;
      return { q: "星の光は届かない。それでも、厚い水素の大気が毛布のように内側の熱を閉じこめれば、表面に液体の海が残るかもしれない。",
        note: "星を持たない惑星の表面を観測できた例はまだない。見つかっているのも、重力レンズで一瞬見えたものだけ。",
        opts: [["水素の毛布と海がある", "厚い水素の大気が残り、内側の熱で海が凍らない", () => { P.rogueOcean = true; P.atm = 3; }], ["凍りついている", "大気は逃げ、すべてが氷に閉ざされる", () => { P.atm = 0; }]] };
    case "lifeBranch": {
      const liquid = ["ocean", "global"].includes(P.water) || (P.rogueOcean);
      if (!liquid) return null;
      return { q: "液体の水が長く続いた。生命は生まれたか。",
        note: "地球以外で生命が見つかった例は、まだ1つもない。だから、どれくらいの確率で生まれるのかは誰にもわからない。",
        opts: [["生まれた", "小さな生き物が生まれたことにして進む", () => { P.life = "yes"; }], ["生まれなかった", "生き物のいない海のまま進む", () => { P.life = "no"; }]] };
    }
    case "mystery": {
      if (P.atm === 0) return null;
      const o = [["生き物が出した気体", "生命のしるしだと考える", () => { P.life = "yes"; }], ["生き物と関係ない化学", "岩や火山の反応で説明する", () => {}], ["測りまちがい", "データのゆらぎだった", () => {}]];
      return { q: "望遠鏡でこの惑星の大気を見たら、説明のつかない成分の手がかりが出た。これは何か。",
        note: "実在の惑星 K2-18b でも、生命と関係するかもしれない成分の手がかりが報告され、別の研究者たちが「はっきりしない」と反論している。",
        opts: P.life === "no" ? o.slice(1) : o };
    }
    case "mergeBranch":
      return { q: `${P.galaxy}は、となりの銀河に近づいている。ぶつかるか。`,
        note: "天の川銀河とアンドロメダ銀河でさえ、100億年以内にぶつかる確率は約半々と見積もられている。ぶつかっても、星どうしが当たることはほとんどない。",
        opts: [["ぶつかる", "2つの銀河が混ざり合う。夜空の星の並びが変わる", () => { P.merged = true; }], ["すれ違う", "近づいたあと、また離れていく", () => {}]] };
    default: return null;
  }
}

/* ---------- 生き物: 生まれ方・滅び方・終わり方 ---------- */
// 生命が生まれたら、地球の歩みを目安に進化の分かれ道と滅びを台本に足す。速さは惑星ごとに「地球の〇倍」（仮の値）
const LV = { base: "微生物", photo: "光合成する微生物", cell: "複雑な細胞の微生物", sea: "海の大きな生き物", plant: "陸の植物のような生き物", land: "陸の動物のような生き物", mind: "知的生命" };
function insertEvent(e) { const rest = script.splice(idx); rest.push(e); rest.sort((x, y) => x.t - y.t); script.push(...rest); }
function grav() { return P.m / (P.r * P.r); }
function traits(lv) {
  const t = [];
  if (P.star.type === "M" && !P.rogue && (lv === "photo" || lv === "plant")) t.push("赤い光をむだなく吸うため黒っぽい色（推定）");
  if (P.locked && lv !== "base") t.push("昼と夜の境目の、ちょうどよい温度の帯に住む");
  if (grav() > 1.4 && (lv === "land" || lv === "sea" || lv === "mind")) t.push(`重力が地球の約${grav().toFixed(1)}倍なので、低く平たい体（想像）`);
  if (P.star.type === "M" && !P.rogue && lv === "sea") t.push("フレアの紫外線を避けて深めの水に住む（想像）");
  return t;
}
const POOL = {
  sea: ["海底に根を張る、葉のような生き物", "やわらかい体で泳ぐ生き物", "殻を持つ小さな生き物", "砂にもぐる、細長い生き物", "群れで漂う、透明な生き物", "ほかの生き物を食べる、すばやい生き物"],
  plant: ["陸に広がる、こけのような生き物", "背の高い、木のような生き物"],
  land: ["陸を歩く生き物", "土の中に住む生き物", "群れで暮らす生き物", "空を飛ぶ生き物"],
};
function newGroup(lv, parent, why) {
  const B = P.bio;
  let what = { base: "化学のエネルギーで生きる小さな微生物", photo: "光で栄養をつくる微生物", cell: "大きく複雑な細胞を持つ微生物", mind: "道具と言葉を使う生き物" }[lv] || pick(POOL[lv]);
  if (lv === "land" && what === "空を飛ぶ生き物" && grav() > 1.2) what = "地面を這う生き物";
  const where = lv === "base" ? (P.rogue ? "光のない海の底" : pick(["浅い海", "海底の熱水の噴き出し口"])) : lv === "plant" || lv === "land" ? "陸" : lv === "mind" ? (P.waterInv === "global" ? "陸のない海" : "陸") : "海";
  const g = { id: B.groups.length, name: makeName(2), lv, what, where, traits: traits(lv), parent: parent ? parent.id : null, born: ageNow, died: null, cause: null, why };
  B.groups.push(g);
  const tr = g.traits.length ? "特徴: " + g.traits.join("、") + "。" : "";
  addFeed(`新しい生き物: ${g.name}（${LV[lv]}）`, `${parent ? `${parent.name}から分かれて` : ""}${g.what}が現れた。住む場所: ${g.where}。${tr}${why || ""}`, "unk", []);
  renderBio();
  return g;
}
const living = () => P.bio.groups.filter((g) => g.died === null);
function kill(g, cause) { g.died = ageNow; g.cause = cause; P.bio.lastDead = g; }
function checkEnd() { // 最後の1種類が滅んだら、生き物の時代の終わり（1回だけ）
  const B = P.bio;
  if (B.ended || living().length) return false;
  B.ended = true;
  const g = B.lastDead;
  B.endText = `最後まで生きていたのは${g.name}（${LV[g.lv]}）。${g.cause}。`;
  addFeed("生き物の終わり", B.endText + `この惑星に現れた生き物は、全部で${B.groups.length}種類だった。`, "est", []);
  return true;
}
function extinct(cause, frac, opts = {}) { // 一部が滅ぶ。opts.keepMicrobes で微生物は1つ残す
  const L = living().filter((g) => !opts.only || opts.only.includes(g.lv));
  if (!L.length) return [];
  const dead = L.filter(() => R() < frac);
  if (opts.keepMicrobes) { const m = living().filter((g) => g.lv === "base" || g.lv === "photo" || g.lv === "cell"); if (m.length && m.every((g) => dead.includes(g))) dead.splice(dead.indexOf(m[0]), 1); }
  dead.forEach((g) => kill(g, cause));
  if (dead.length) P.bio.luck.push({ age: ageNow, cause, n: dead.length });
  renderBio();
  return dead;
}
function afterExtinct() { checkEnd(); }
function radiate(when) { // 滅びのあと、生き残りから新しい生き物が広がる（地球でも大量絶滅のあとに起きた）
  insertEvent({ t: when, kind: "bioRad", tag: "est", src: ["raup"] });
}
const EVO = [
  { k: "photo", d: 0.9, need: () => !P.rogue, q: "光で栄養をつくる生き物は現れたか", note: "地球で光で酸素をつくる微生物が現れた時期は、研究によって幅が大きい（遅くとも約25〜30億年前）。ほかの星の光の下でも同じことが起きるかは、わからない。", src: ["kiang"] },
  { k: "oxygen", d: 1.3, need: () => P.bio.has.photo === true, auto: true },
  { k: "cell", d: 1.9, q: "細胞の中に別の細胞を取り込んだ、複雑な細胞は現れたか", note: "地球の動物や植物の細胞は、ある微生物が別の微生物を取り込んでできたと考えられている。これはとても珍しい出来事だったのかもしれない、という研究者もいる。" },
  { k: "sea", d: 3.2, need: () => P.bio.has.cell === true && P.bio.has.oxygen === true, q: "体が多くの細胞でできた、大きな生き物は現れたか", note: "地球では、生命の誕生から30億年以上かかった。酸素が少ないと大きな体はつくりにくいと考えられている。" },
  { k: "burst", d: 3.24, need: () => P.bio.has.sea === true, auto: true },
  { k: "plant", d: 3.3, need: () => P.bio.has.sea === true && P.bio.has.photo === true && P.waterInv !== "global" && !P.rogue, q: "陸に上がった生き物はいたか", note: "陸があるか、陸の上の乾きや紫外線に耐えられるかしだい。地球では、海で大きな生き物が現れてから約1億年後に、植物が陸に広がった。" },
  { k: "land", d: 3.35, need: () => P.bio.has.plant === true, auto: true },
  { k: "mind", d: 3.77, need: () => P.bio.has.sea === true, q: "道具と言葉を使う生き物は現れたか", note: "地球では、生命の誕生から約38億年かかった。知性が生まれるのが当たり前のことか、とても珍しいことかは、例が地球の1つしかないので誰にもわからない。" },
];
function startBio() {
  const pace = Math.exp(between(Math.log(0.4), Math.log(2.5)));
  P.bio = { groups: [], has: { base: true }, pace, start: ageNow, ended: false, declining: false, endText: "", S0: surface(P, ageNow).S, luck: [] };
  addFeed("生命のはじまり", `化学の反応から、最初の生き物が生まれた（と仮に決めた）。化学がどうやって生命になったのかは、地球でもまだわかっていない。この惑星の進化の速さは、仮に地球の${pace < 1 ? (1 / pace).toFixed(1) + "分の1" : pace.toFixed(1) + "倍"}とする（本当の速さはわからない）。`, "unk", []);
  newGroup("base", null, "");
  for (const v of EVO) insertEvent({ t: ageNow + v.d / pace * between(0.85, 1.2), kind: "bioEvo", evo: v, tag: v.auto ? "est" : "unk", src: v.src || [] });
  const n = 2 + Math.floor(R() * 3);
  for (let i = 0; i < n; i++) insertEvent({ t: ageNow + Math.exp(between(Math.log(0.4), Math.log(6))) / pace, kind: "bioME", tag: "est", src: ["raup"] });
  insertEvent({ t: ageNow + between(0.05, 0.3) / pace, kind: "bioRad", tag: "est", src: [] });
}
function handleBio(e) { // 戻り値: 分かれ道で止めるときは { branch }
  const B = P.bio;
  if (!B || B.ended) return null;
  if (B.declining && (e.kind === "bioRad" || e.kind === "bioEvo")) return null; // 星が明るくなりはじめたら、新しい生き物は増えない
  if (e.kind === "bioRad") {
    const L = living(); if (!L.length) return null;
    const top = ["mind", "land", "plant", "sea", "cell", "photo", "base"].find((l) => B.has[l] === true && l !== "mind");
    const parent = pick(L.filter((g) => g.lv === top).concat(L)).valueOf();
    newGroup(top, parent, "生き残った仲間から、新しい生き物が広がった。");
    return { done: true };
  }
  if (e.kind === "bioME") {
    if (living().length < 2) return null;
    const dead = extinct("原因のはっきりしない大量絶滅", between(0.4, 0.8), { keepMicrobes: true }); afterExtinct();
    if (!dead.length) return null;
    addFeed("大量絶滅", `${dead.map((g) => g.name).join("、")}が滅んだ。地球でも、大きな大量絶滅が少なくとも5回あった。原因は火山・気候の変化・天体の衝突などが考えられているが、この惑星で何が起きたかは、わからない。`, "est", ["raup"]);
    radiate(ageNow + between(0.01, 0.1) / B.pace);
    return { done: true };
  }
  if (e.kind === "bioEvo") {
    const v = e.evo;
    if (B.has[v.k] || (v.need && !v.need())) return null;
    const prevLv = { photo: ["base"], cell: ["base", "photo"], sea: ["cell"], plant: ["sea"], mind: ["land", "sea"] }[v.k];
    if (prevLv && !living().some((g) => prevLv.includes(g.lv))) return null; // もとになる生き物が滅んでいたら、この段階は来ない
    if (v.k === "oxygen") {
      B.has.oxygen = true;
      const dead = extinct("酸素が増え、酸素に弱い仲間が暮らせなくなった", 0.5, { only: ["base"], keepMicrobes: true }); afterExtinct();
      addFeed("大気に酸素が増えた", "光合成をする微生物が出す酸素が、大気にたまっていった。" + (dead.length ? `酸素に弱い${dead.map((g) => g.name).join("、")}が滅んだ（地球でも、酸素の少ない場所へ追いやられた微生物がいたと考えられている）。` : "大きな生き物が生まれる下地ができた。"), "est", ["lyons"]);
      return { done: true };
    }
    if (v.k === "burst") { B.has.burst = true; addFeed("いろいろな形の生き物が一気に増えた", "大きな生き物が現れたあと、短いあいだに体の形がさまざまに広がった（地球では約5億年前のカンブリア爆発）。", "est", []); const L = living().filter((g) => g.lv === "sea"); for (let i = 0; i < 2; i++) newGroup("sea", pick(L.length ? L : living()), ""); return { done: true }; }
    if (v.k === "land") { B.has.land = true; const pl = living().filter((g) => g.lv === "plant"); newGroup("land", pick(pl.length ? pl : living()), "陸の植物のような生き物を食べる生き物が、陸に上がった。"); return { done: true }; }
    return { branch: {
      q: v.q, note: v.note,
      opts: [["現れた", "進化が次の段階へ進む", () => { B.has[v.k] = true; const pp = living().filter((g) => prevLv.includes(g.lv)); newGroup(v.k, pick(pp), ""); if (v.k === "mind") luckChain(); if (v.k === "mind") insertEvent({ t: ageNow + 1e-5, kind: "bioCiv", tag: "unk", src: [], title: "その文明は、どれくらい続いたか", branch: true }); radiate(ageNow + between(0.02, 0.2) / B.pace); }],
             ["現れなかった", "この段階で止まったまま進む", () => { B.has[v.k] = "no"; }]] } };
  }
  return null;
}
function luckChain() {
  const B = P.bio; const m = B.groups[B.groups.length - 1];
  const line = []; let g = m; while (g) { line.unshift(g.name); g = g.parent !== null ? B.groups[g.parent] : null; }
  const luck = B.luck.map((l) => `生まれて${fmtYears(l.age)}後の「${l.cause}」（${l.n}種類が滅んだ）`);
  addFeed("ここまでの偶然", `${m.name}までの系統: ${line.join(" → ")}。途中で起きた滅び: ${luck.length ? luck.join("、") : "大きなものはなかった"}。このどれか1つでも違っていたら、${m.name}は生まれなかったかもしれない。生命の歴史をやり直したら同じ結果にはならない、と論じた研究者がいる。恐竜が滅んだあとに哺乳類が広がったことも、偶然の例としてよく挙げられる。一方で、似た条件なら似た生き物に行き着きやすいという考えもあり、どちらが正しいかはわからない。`, "unk", ["gould"]);
}
function civBranch() {
  const B = P.bio; const m = living().find((g) => g.lv === "mind");
  if (!m) return null;
  return { q: `${m.name}の文明は、どれくらい続いたか。`, note: "文明がどれくらい続くかは、宇宙に知的生命がどれくらいいるかを見積もる式（ドレイク方程式）の中で、いちばんわからない数の1つ。手がかりは、まだ1万年ほどしかない私たちの文明だけ。",
    opts: [["数千年", "短いあいだで終わった", () => insertEvent({ t: ageNow + between(2e-6, 8e-6), kind: "bioCivEnd", tag: "unk", src: [] })],
           ["数百万年", "長く続いた", () => insertEvent({ t: ageNow + between(1e-3, 5e-3), kind: "bioCivEnd", tag: "unk", src: [] })],
           ["星の最期まで", "星がふくらむ日まで続いた", () => {}]] };
}
function bioEnd(cause) { // すべて滅ぶ
  const B = P.bio; if (!B || B.ended) return;
  const L = living(); if (!L.length) { B.ended = true; return; }
  B.ended = true; L.forEach((g) => kill(g, cause));
  const last = [...L].sort((a, b) => ({ base: 0, photo: 1, cell: 2 }[a.lv] ?? 9) - ({ base: 0, photo: 1, cell: 2 }[b.lv] ?? 9))[0];
  B.endText = `最後まで生きていたのは${last.name}（${LV[last.lv]}）。${cause}。`;
  addFeed("生き物の終わり", B.endText + `この惑星に現れた生き物は、全部で${B.groups.length}種類だった。`, "est", []);
  renderBio();
}
// 受ける光がこの区切りを超えたら、その仲間が生きられなくなる。順番は論文の考え方、区切りの数字は SEADICE が置いた目安
const DECLINE = [["decPlant", 1.05], ["decLand", 1.07], ["decSea", 1.09], ["decCell", 1.1]];
function startDecline() { // 星が明るくなり、生き物が大きいものから順に消えていく（Caldeira & Kasting 1992 / O'Malley-James 2013）
  const B = P.bio; if (!B || B.declining || B.ended) return;
  B.declining = true; B.decStep = 0;
  addFeed("生き物の終わりが始まる", "星が明るくなってきた。" + (P.carbon ? "岩が二酸化炭素を吸い取る働きが強まり、大気の二酸化炭素が減っていく。" : "地表が暑くなっていく。") + "生き物は、大きなものから順に生きられなくなると考えられている（どの明るさで何が消えるかの区切りは、目安として置いた値）。", "est", ["caldeira", "omalley"]);
}
function declineTick(S) {
  const B = P.bio;
  while (B.declining && !B.ended && B.decStep < DECLINE.length && S > DECLINE[B.decStep][1]) { handleDecline({ kind: DECLINE[B.decStep][0], src: ["caldeira", "omalley"] }); B.decStep++; }
}
function handleDecline(e) {
  const B = P.bio; if (!B || B.ended) return null;
  const step = { decPlant: [["plant"], "二酸化炭素が足りなくなり、陸の植物のような生き物が育たなくなった", "陸の植物が消えていく"],
    decLand: [["land", "mind"], "食べ物の植物がなくなり、暑さも増して、陸の動物のような生き物が生きられなくなった", "陸の動物が消えていく"],
    decSea: [["sea"], "海が温まり、酸素も減って、海の大きな生き物が生きられなくなった", "海の大きな生き物が消えていく"],
    decCell: [["cell", "photo"], "残っていた複雑な細胞の微生物や、光合成をする微生物も消えた。小さな微生物だけが残っている", "微生物だけが残る"] }[e.kind];
  const dead = living().filter((g) => step[0].includes(g.lv));
  dead.forEach((g) => kill(g, "星が明るくなりすぎた"));
  if (!dead.length) return null;
  if (!living().length) { renderBio(); checkEnd(); return { done: true }; }
  addFeed(step[2], step[1] + `（${dead.map((g) => g.name).join("、")}）。`, "est", e.src);
  renderBio();
  return { done: true };
}

/* ---------- ふつうの出来事の中身 ---------- */
function resolveEvent(P, e, age) {
  const s = P.star;
  switch (e.kind) {
    case "giantImpact": P.impacts++; if (P.atm > 0) P.atm = Math.max(1, P.atm - 1); return { text: e.text };
    case "eject": if (P.ejected) return null; P.ejected = true; P.rogue = true; P.atm = Math.min(P.atm, P.atm === 4 ? 4 : 1); return { text: e.text };
    case "lock": if (P.rogue) return null; P.locked = true; return { text: e.text };
    case "impact": {
      P.impacts++;
      const big = e.size >= 10;
      let text = `直径およそ${e.size}kmの天体がぶつかった。`;
      if (P.atm === 4) text += "厚いガスの奥へ吸いこまれ、表面は何も変わらない。";
      else if (big && P.bio && !P.bio.ended && living().length) {
        const dead = extinct(`直径約${e.size}kmの天体の衝突`, e.size >= 50 ? 0.9 : 0.6, { keepMicrobes: true });
        text += "空が塵におおわれ、日光がさえぎられた。" + (dead.length ? `${dead.map((g) => g.name).join("、")}が滅んだ。` : "生き物はなんとか耐えた。") + "地球でも6600万年前、直径10kmほどの天体の衝突のあと、恐竜を含む多くの生き物が絶滅した。";
        if (dead.length) radiate(ageNow + between(0.005, 0.05) / P.bio.pace);
      }
      else if (big) text += "大きなクレーターができ、しばらく空が暗くなった。";
      else text += "小さなクレーターが1つ増えた。";
      return { text };
    }
    case "supernova": {
      if (!e.near) return { text: `約${Math.round(between(60, 300))}光年先の星が爆発した。夜空に、昼でも見えるほど明るい星が数か月輝いた。これだけ離れていれば、大気への影響は小さいと考えられている。` };
      let text = `約${Math.round(between(15, 26))}光年先という近さで星が爆発した。`;
      if (P.atm >= 1 && P.atm < 4) {
        text += "強い放射線で、紫外線を防ぐ大気の層が傷ついたかもしれない。";
        if (P.bio && !P.bio.ended) { const dead = extinct("近くの超新星の放射線", 0.5, { only: ["plant", "land", "mind"] }); text += dead.length ? `地表の${dead.map((g) => g.name).join("、")}が滅んだ。` : "地表の生き物は紫外線を多く浴びた。"; }
      }
      else text += "大気が厚いか、ないため、変わったことは少ない。";
      return { text };
    }
    case "passStar": return { text: "太陽と地球の距離の数千倍ほど先を、ほかの星が通った。遠くを回る氷の天体の軌道が乱れ、しばらく彗星が増えた。" };
    case "now": return { text: `生まれてから${fmtYears(age)}。ここが、私たちのいる「今」と同じ時刻。ここから先は、まだ誰も見たことのない未来。` };
    case "hzCheck": {
      const sf = surface(P, age);
      if (P.water === "ocean" || P.water === "global") return { text: `星は生まれたころよりかなり明るくなった。表面はおよそ${Math.round(sf.T - 273)}℃。` };
      return { text: "星は年をとるほど明るくなる。太陽も、生まれたころは今より約3割暗かった。" };
    }
    case "brighten": {
      const sf = surface(P, age);
      if ((P.water === "ocean" || P.water === "global") && sf.S > 1.1) { P.waterInv = "none"; P.atm = 3; return { text: "星が明るくなりすぎて、海が蒸発しはじめた。水蒸気は宇宙へ逃げていく。" + (P.life === "yes" ? "生き物は地下や深い場所に追いやられた。" : "") }; }
      return { text: "星の中心の燃料が尽きかけ、明るさが増していく。" };
    }
    case "redGiant": {
      const rMax = 1.0 * s.M; s.phase = "giant";
      if (P.rogue) return { text: "遠く離れた今は、もう関係がない。" };
      if (P.a < 0.7 * rMax) { P.alive = false; P.endReason = `ふくらんだ${s.name}に飲み込まれた`; return { text: `星が太陽系なら地球の軌道ほどまでふくらみ、近くを回っていたこの惑星は飲み込まれた。`, tag: "est" }; }
      if (P.a < 1.3 * rMax) return { branch: true, b: { q: "ふくらんだ星の外側ぎりぎりにいる。飲み込まれるか。",
        note: "太陽が年をとったとき地球が飲み込まれるかも、計算によって答えが分かれている。星が軽くなって惑星の軌道が広がる効果と、引きずりこまれる効果の勝負になる。",
        opts: [["飲み込まれる", "星の中へ落ちていく", () => { P.alive = false; P.endReason = `ふくらんだ${s.name}に飲み込まれた`; }], ["ぎりぎり逃れる", "焼かれながらも残る", () => { P.atm = 0; P.waterInv = "none"; }]] } };
      P.a *= s.M / (0.08 * s.M + 0.47); // 星が軽くなったぶん、軌道が広がる
      const S = 1500 * Math.pow(s.M, 1.5) / (P.a * P.a);
      if (P.kind !== "giant" && P.kind !== "nep" && S > 0.3 && S < 1.5) return { text: "星がふくらんで明るくなり、凍っていた表面の氷が一時的にとけた。星は軽くなり、軌道は外へ広がった。" };
      return { text: "星は外側のガスを吹き飛ばしながら軽くなり、惑星の軌道は外へ広がった。" };
    }
    case "whiteDwarf":
      s.phase = "wd";
      if (e.longLived) return { text: `${s.name}は燃料を使い切り、小さな白色矮星になったと考えられている。私たちの「今」の宇宙は若すぎて、ここまで生きた赤色矮星はまだ1つもない。誰も見たことのない最期。` };
      return { text: `${s.name}は地球ほどの大きさの白色矮星になった。光は弱く、この惑星はゆっくり冷えていく。白色矮星のまわりを回る惑星は、実際に見つかっている。` };
    case "longLife":
      return { text: `赤色矮星は燃料を少しずつ使うので、何千億年から何兆年も燃え続ける。私たちの「今」の時点では、燃え尽きた赤色矮星は宇宙に1つもない。` };
    case "starSN":
      P.alive = false; P.endReason = `${s.name}の超新星爆発に巻き込まれた`;
      return { text: "重い星は短い一生の最後に爆発する。惑星は吹き飛ばされるか、熱で表面をはぎ取られた。" };
    default: return { text: e.text || "" };
  }
}

/* ---------- 画面 ---------- */
const STORE = "wakusei.lives.v1";
function loadLives() { try { return JSON.parse(localStorage.getItem(STORE) || "[]"); } catch (_) { return []; } }
function saveLife(rec) { try { const l = loadLives(); l.unshift(rec); localStorage.setItem(STORE, JSON.stringify(l.slice(0, 10))); } catch (_) {} }

let P, script, idx, prog, speed, playing, timer, ageNow, tEnd, auto, durSec, log, segs;
const T0 = 1e-5;

function start() {
  const rogue = $("#opt-rogue").checked;
  const now = $("#opt-when").value === "now";
  durSec = Number($("#opt-len").value);
  auto = $("#opt-auto").checked;
  P = makePlanet({ rogue, now, ...FROM });
  $("#bio").hidden = true; $("#e-bio").hidden = true;
  script = buildScript(P);
  idx = 0; prog = 0; speed = 1; playing = true; ageNow = T0; log = []; segs = [];
  tEnd = endAgeFor(P);
  $("#screen-start").hidden = true; $("#screen-end").hidden = true; $("#screen-life").hidden = false;
  $("#feed").textContent = "";
  $("#auto").checked = auto;
  renderHead();
  update();
  setSpeed(1);
  clearInterval(timer);
  timer = setInterval(tick, 100);
  window.scrollTo(0, 0);
}

function remap() { prog = Math.log(ageNow / T0) / Math.log(tEnd / T0); }

function tick() {
  if (!playing) return;
  prog += (0.1 * speed) / durSec;
  ageNow = T0 * Math.pow(tEnd / T0, Math.min(prog, 1));
  while (idx < script.length && script[idx].t <= ageNow) {
    const e = script[idx++];
    if (fire(e)) break; // 分かれ道で止まる
    if (!P.alive) break;
  }
  update();
  if (!P.alive || prog >= 1) finish();
}

const STAR_EVENTS = ["brighten", "redGiant", "whiteDwarf", "longLife", "starSN", "hzCheck", "lock", "flareBranch", "envelopeBranch"];
function fire(e) {
  if (P.rogue && STAR_EVENTS.includes(e.kind)) return false;
  if (e.kind === "bioCiv") { const b = civBranch(); if (!b) return false; askBranch(e, b); return true; }
  if (e.kind === "bioCivEnd") { const m = P.bio && living().find((g) => g.lv === "mind"); if (!m) return false; kill(m, "文明が終わった（理由はわからない）"); checkEnd(); addFeed("文明の終わり", `${m.name}の文明が終わった。なぜ終わったのかは、わからない。ほかの生き物は生き続けている。`, "unk", []); renderBio(); return false; }
  if (e.kind && e.kind.startsWith("bio")) { const r = handleBio(e); if (r && r.branch) { askBranch({ title: "進化の分かれ道", src: e.src }, r.branch); return true; } return false; }
  const wasEjected = P.ejected;
  if (e.branch) {
    const b = branchFor(P, e, ageNow);
    if (!b) return false;
    askBranch(e, b);
    return true;
  }
  const r = resolveEvent(P, e, ageNow);
  if (!r) return false;
  if (r.branch) { askBranch(e, r.b); return true; }
  addFeed(e.title || impactTitle(e), r.text, r.tag || e.tag, e.src);
  if (!wasEjected && P.ejected) { tEnd = endAgeFor(P); remap(); renderHead(); }
  return false;
}
function impactTitle(e) { return e.size >= 10 ? "大きな天体がぶつかった" : "小さな天体がぶつかった"; }

let branchSeq = 0;
function askBranch(e, b) {
  playing = false;
  const my = ++branchSeq;
  const box = $("#branch");
  $("#branch-q").textContent = b.q;
  $("#branch-note").textContent = b.note;
  const opts = $("#branch-opts"); opts.textContent = "";
  const choose = (i, byDice) => {
    if (my !== branchSeq || box.hidden) return;
    const o = b.opts[i];
    o[2]();
    box.hidden = true;
    addFeed(e.title, `${b.q} → 「${o[0]}」${byDice ? "（サイコロで決めた）" : "（自分で選んだ）"}。${o[1]}。${b.note}`, "unk", e.src, true);
    playing = true;
    update();
    if (!P.alive) finish();
  };
  b.opts.forEach((o, i) => {
    const btn = el("button", "opt");
    btn.type = "button";
    btn.append(el("strong", null, o[0]), el("span", null, o[1]));
    btn.addEventListener("click", () => choose(i, false));
    opts.append(btn);
  });
  const dice = $("#branch-dice");
  dice.onclick = () => choose(Math.floor(R() * b.opts.length), true);
  box.hidden = false;
  opts.querySelector("button").focus();
  if (auto) setTimeout(() => { if (!box.hidden && my === branchSeq) choose(Math.floor(R() * b.opts.length), true); }, 4000);
}

function addFeed(title, text, tag, src, branch) {
  const li = el("li", "ev");
  const head = el("div", "ev-head");
  head.append(el("span", "ev-age", fmtYears(ageNow)), el("span", "tag tag-" + tag, TAG[tag]));
  if (branch) head.append(el("span", "tag tag-branch", "分かれ道"));
  li.append(head, el("p", "ev-title", title), el("p", "ev-text", text));
  if (src && src.length) li.append(el("p", "ev-src", "出典: " + src.map((k) => SOURCES[k]).join(" ／ ")));
  $("#feed").prepend(li);
  const lt = $("#latest"); lt.textContent = ""; lt.append(el("span", "tag tag-" + tag, TAG[tag]), document.createTextNode(title));
  log.push({ age: ageNow, title, tag, branch: !!branch });
}

function renderHead() {
  $("#p-name").textContent = `${P.name}`;
  $("#p-sub").textContent = P.rogue
    ? `${P.galaxy}をさまよう、星を持たない惑星 ／ ${KINDS[P.kind].name}`
    : `${P.galaxy}の${P.star.name}（${P.star.typeName}）を回る ${P.star.name} ${P.letter} ／ ${KINDS[P.kind].name}`;
}

function update() {
  const sf = surface(P, ageNow);
  P.water = waterState(P, sf.T);
  if (!playing) { renderStatic(sf); return; } // 分かれ道や一時停止のあいだは、状態を進めない
  if (P.life === "yes" && !P.bio) startBio();
  if (P.bio && !P.bio.ended && P.bio.frozen && ["ocean", "global"].includes(P.water)) { P.bio.frozen = false; addFeed("氷がとけた", "氷がとけ、生き残った生き物がふたたび広がりはじめた。", "est", ["hoffman"]); radiate(ageNow + 0.01); }
  if (P.bio && !P.bio.ended) {
    if (!P.rogue && !P.bio.declining && sf.S > Math.max(1.05, P.bio.S0 * 1.15) && P.star.M >= 0.5) startDecline();
    if (P.bio.declining) declineTick(sf.S);
    if (!P.rogue && sf.S > 1.1 && (P.waterInv === "some" || P.waterInv === "global")) { P.waterInv = "none"; P.atm = 3; addFeed("海が蒸発した", "受ける光が強くなりすぎて、海が蒸発し、水蒸気は宇宙へ逃げていった。", "est", ["kopparapu"]); P.water = waterState(P, surface(P, ageNow).T); }
    if (!P.alive) bioEnd(P.endReason || "惑星が失われた");
    else if (P.water === "ice" && P.ejected && !P.rogueOcean) {
      bioEnd("星から放り出され、海が凍りついた（地下の深い場所で生き延びたかは、わからない）");
    }
    else if (P.water === "ice") {
      if (!P.bio.frozen) {
        P.bio.frozen = true;
        const dead = extinct("惑星全体が凍りついた", 0.7, { keepMicrobes: true });
        addFeed("全球凍結", "惑星全体が氷に閉ざされた。" + (dead.length ? `${dead.map((g) => g.name).join("、")}が滅んだ。` : "") + "地球でも全体が凍った時代があり、そのときは氷の下や熱水の噴き出し口のまわりで生き物が生き延びたと考えられている。この惑星の生き物が、氷が続くあいだ生き延びられるかは、わからない（ここでは微生物が残ったことにしている）。", "unk", ["hoffman"]);
      }
    }
    else if (!["ocean", "global"].includes(P.water)) {
      P.life = "lost";
      bioEnd(P.ejected && !P.rogueOcean ? "星から放り出され、海が凍りついた" : "液体の水がなくなった（地下の深い場所で微生物が生き延びたかは、わからない）");
    }
  }
  if (P.life === "yes" && (!P.alive || ["none", "steam"].includes(P.water))) P.life = "lost";
  renderStatic(sf);
}
function renderStatic(sf) {
  const u = P.born + ageNow;
  $("#age").textContent = fmtYears(ageNow);
  $("#uni").textContent = fmtUniverse(u);
  $("#bar").style.width = (clamp(prog, 0, 1) * 100).toFixed(1) + "%";
  setMeter("temp", clamp((sf.T + 0) / 15, 0, 100), P.atm === 4 ? `雲の上で ${Math.round(sf.T - 273)}℃` : `${Math.round(sf.T - 273)}℃`);
  setMeter("atm", [0, 25, 50, 80, 100][P.atm], ATM_WORD[P.atm]);
  setMeter("water", { none: 0, ice: 30, ocean: 70, global: 100, steam: 50, deep: 50 }[P.water], WATER_WORD[P.water]);
  const impactRate = Math.exp(-ageNow / 0.3) * 100;
  setMeter("hit", clamp(impactRate + 5, 0, 100), impactRate > 40 ? "とても多い" : impactRate > 5 ? "ときどき" : "まれ");
  const L = luminosityAt(P, ageNow);
  setMeter("star", clamp(Math.log10(L + 1e-4) * 20 + 60, 0, 100), P.rogue ? "星の光は届かない" : L < 0.01 ? `太陽の${(L * 100).toFixed(2)}%` : `太陽の${L.toFixed(2)}倍`);
  $("#life").textContent = P.bio && !P.bio.ended ? `いる（仮に選んだ）。${living().length}種類` : P.bio ? "いたが、滅んだ" : { unknown: "わからない", yes: "いる（仮に選んだ）", no: "いない（仮に選んだ）", lost: "いたが、水が失われた（その後はわからない）" }[P.life];
  renderComp(); draw(sf);
  const state = P.alive ? P.water : "dead";
  const last = segs[segs.length - 1];
  if (!last || last.s !== state) segs.push({ s: state, p: prog });
}

function renderBio() {
  const box = $("#bio"); if (!box) return;
  if (!P.bio) { box.hidden = true; return; }
  box.hidden = false;
  const L = living(), D = P.bio.groups.filter((g) => g.died !== null);
  $("#bio-count").textContent = `今いる ${L.length}種類 ／ 滅んだ ${D.length}種類`;
  const ul = $("#bio-alive"); ul.textContent = "";
  for (const g of L) { const li = el("li"); li.append(el("strong", null, `${g.name}（${LV[g.lv]}）`), el("span", null, `${g.what}。${g.where}に住む。${fmtYears(ageNow - g.born)}前に現れた`)); ul.append(li); }
  const dl = $("#bio-dead"); dl.textContent = "";
  for (const g of D.slice(-6).reverse()) { const li = el("li"); li.append(el("strong", null, `${g.name}（${LV[g.lv]}）`), el("span", null, `${fmtYears(g.died - g.born)}続いて滅んだ。理由: ${g.cause}`)); dl.append(li); }
}
function renderBioHistory() {
  const box = $("#e-bio"); const ul = $("#e-bio-list"); ul.textContent = "";
  if (!P.bio) { box.hidden = true; return; }
  box.hidden = false;
  $("#e-bio-end").textContent = P.bio.endText || "生き物は、星の時代が終わるまで生き続けた。";
  const byId = (id) => P.bio.groups[id];
  for (const g of P.bio.groups) {
    const li = el("li");
    const life = g.died !== null ? `${fmtYears(g.died - g.born)}続いた。滅んだ理由: ${g.cause}` : "最後まで生きていた";
    li.append(el("strong", null, `${g.name}（${LV[g.lv]}）`), el("span", null, `生まれて${fmtYears(g.born)}後に現れた${g.parent !== null ? `（${byId(g.parent).name}から分かれた）` : "（最初の生き物）"}。${g.what}。${life}`));
    ul.append(li);
  }
}

function setMeter(id, v, word) { $("#m-" + id).style.width = v + "%"; $("#w-" + id).textContent = word; }

const COMP = [["iron", "鉄", "#8a6e5a"], ["rock", "岩", "#b09a7a"], ["water", "水・氷", "#5f8fbf"], ["gas", "水素・ヘリウム", "#d6c39a"], ["unk", "わからない", "unk"]];
function renderComp() {
  const box = $("#comp"); box.textContent = "";
  const leg = $("#comp-leg"); leg.textContent = "";
  for (const [k, name, c] of COMP) {
    const v = P.comp[k]; if (v < 0.5) continue;
    const seg = el("span", c === "unk" ? "seg seg-unk" : "seg");
    seg.style.width = v + "%"; if (c !== "unk") seg.style.background = c;
    box.append(seg);
    const li = el("li"); const sw = el("i", c === "unk" ? "sw seg-unk" : "sw"); if (c !== "unk") sw.style.background = c;
    li.append(sw, document.createTextNode(name)); leg.append(li);
  }
}

function planetColor() {
  if (!P.alive) return "#555b66";
  if (P.kind === "giant") return "#c9a26b";
  if (P.kind === "nep") return "#6f9fc4";
  if (P.kind === "subnep") return "#8fb3c2";
  return { ocean: "#3b6ea8", global: "#2d5f9a", ice: "#d3dce6", steam: "#c8c2b4", none: "#9a7b5f", deep: "#8fb3c2" }[P.water] || "#9a7b5f";
}
function draw(sf) {
  const svg = $("#scene");
  const s = P.star;
  const star = $("#sv-star"), pl = $("#sv-planet"), land = $("#sv-land");
  $("#sv-orbit").setAttribute("r", P.rogue ? 0 : 190);
  if (P.rogue) { star.setAttribute("r", 0); }
  else {
    const rs = s.phase === "giant" ? 70 : s.phase === "wd" ? 4 : clamp(26 + Math.log10(s.M + 0.05) * 24, 12, 44);
    star.setAttribute("r", rs); star.setAttribute("fill", s.phase === "wd" ? "#e8eef7" : s.phase === "giant" ? "#ff7043" : s.color);
  }
  const pr = clamp(16 + Math.log10(P.r) * 28, 10, 50);
  pl.setAttribute("r", pr); pl.setAttribute("fill", planetColor());
  land.setAttribute("r", (P.water === "ocean" && P.alive) ? pr * 0.45 : 0);
  svg.setAttribute("aria-label", `${P.name}: 表面の水は${WATER_WORD[P.water]}、大気は${ATM_WORD[P.atm]}`);
}

function setSpeed(v) {
  speed = v;
  document.querySelectorAll("[data-speed]").forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.speed) === v)));
}

function finish() {
  if (!timer) return;
  clearInterval(timer); timer = null; playing = false;
  const reason = P.endReason || (P.rogue ? "内側の熱も尽き、暗い宇宙を冷えたまま漂い続ける" : P.star.phase === "wd" ? "白色矮星のそばで、ゆっくり冷えていく" : "星とともに、静かな時代に入った");
  if (!P.endReason && !P.rogue && P.star.phase !== "wd") P.star.phase = "wd";
  addFeed("一生の終わり", `${fmtYears(ageNow)}の一生。${reason}。` + (P.endReason ? "" : "ここから先は、長いあいだ大きな変化はないと考えられている。"), "est", []);
  const counts = { sure: 0, est: 0, unk: 0, mark: 0 };
  for (const l of log) counts[l.tag]++;
  const branches = log.filter((l) => l.branch).length;
  $("#screen-life").hidden = true; $("#screen-end").hidden = false;
  $("#e-name").textContent = P.name;
  $("#e-span").textContent = fmtYears(ageNow);
  $("#e-reason").textContent = reason;
  $("#e-born").textContent = `${fmtUniverse(P.born)}に生まれた`;
  $("#c-sure").textContent = counts.sure; $("#c-est").textContent = counts.est; $("#c-unk").textContent = counts.unk;
  $("#c-branch").textContent = branches;
  if (P.bio && !P.bio.ended && living().length) bioEnd(P.endReason ? P.endReason : P.star.phase === "wd" ? "星が白色矮星になり、光と熱が届かなくなった" : "惑星が冷えきった");
  renderTimeline(); renderSimilar(); renderBioHistory();
  const rec = { name: P.name, galaxy: P.galaxy, kind: KINDS[P.kind].name, span: fmtYears(ageNow), reason, unk: counts.unk, total: log.length, life: P.life, at: new Date().toISOString().slice(0, 10) };
  saveLife(rec); renderPast();
  $("#share").onclick = () => share(rec);
  window.scrollTo(0, 0);
}

function renderTimeline() {
  const box = $("#timeline"); box.textContent = "";
  const col = { none: "#9a7b5f", ice: "#d3dce6", ocean: "#3b6ea8", global: "#2d5f9a", steam: "#c8c2b4", deep: "#8fb3c2", dead: "#555b66" };
  segs.forEach((sg, i) => {
    const end = i + 1 < segs.length ? segs[i + 1].p : 1;
    const w = Math.max(0, end - sg.p) * 100; if (w < 0.2) return;
    const d = el("span", "tl-seg"); d.style.width = w + "%"; d.style.background = col[sg.s]; d.title = sg.s === "dead" ? "終わり" : WATER_WORD[sg.s];
    box.append(d);
  });
  const leg = $("#timeline-leg"); leg.textContent = "";
  const seen = [...new Set(segs.map((s) => s.s))];
  for (const s of seen) { const li = el("li"); const sw = el("i", "sw"); sw.style.background = col[s]; li.append(sw, document.createTextNode(s === "dead" ? "終わり" : WATER_WORD[s])); leg.append(li); }
}

let PLANETS = null;
async function loadPlanets() {
  if (PLANETS) return PLANETS;
  try { const r = await fetch("planets.json"); PLANETS = await r.json(); } catch (_) { PLANETS = null; }
  return PLANETS;
}
async function renderSimilar() {
  const box = $("#similar"); box.textContent = "読み込み中…";
  const d = await loadPlanets();
  if (!d) { box.textContent = "実在の惑星のデータを読み込めませんでした。"; return; }
  const S0 = P.rogue ? null : (P.star.Lmid / 1.5) / (P.a * P.a);
  const scored = [];
  for (const r of d.rows) {
    const [name, rade, , , , insol, , teff, , dist, year, method] = r;
    if (!rade) continue;
    let sc = Math.pow(Math.log(rade / P.r), 2) * 4;
    if (!P.rogue) { if (!insol) continue; sc += Math.pow(Math.log(insol / S0), 2) * 0.5; }
    scored.push([sc, name, rade, insol, dist, year]);
  }
  scored.sort((a, b) => a[0] - b[0]);
  box.textContent = "";
  for (const [, name, rade, insol, dist, year] of scored.slice(0, 3)) {
    const li = el("li");
    li.append(el("strong", null, name), el("span", null,
      `大きさ 地球の${rade.toFixed(2)}倍` + (insol ? ` ／ 受ける光 地球の${insol < 0.1 ? insol.toFixed(3) : insol.toFixed(2)}倍` : "") + (dist ? ` ／ ${Math.round(dist * 3.26).toLocaleString("ja-JP")}光年先` : "") + (year ? ` ／ ${year}年に発見` : "")));
    box.append(li);
  }
  $("#similar-note").textContent = P.rogue
    ? `星を持たない惑星は、NASA Exoplanet Archive の一覧（${d.count.toLocaleString("ja-JP")}個、${d.fetched}取得）には入っていない。重力レンズで一瞬見えたものがあるだけで、大きさはほとんどわかっていない。上は、星を回る惑星のうち大きさだけが近いもの。`
    : `NASA Exoplanet Archive の${d.count.toLocaleString("ja-JP")}個（${d.fetched}取得）から、大きさと受ける光が近いものを選んだ。似ているのは数字だけで、中身が似ているかはわからない。`;
}

function renderPast() {
  const l = loadLives(); const box = $("#past"); box.textContent = "";
  $("#past-wrap").hidden = l.length === 0;
  for (const r of l) {
    const li = el("li");
    li.append(el("strong", null, `${r.name}（${r.galaxy}）`), el("span", null, `${r.kind} ／ ${r.span} ／ ${r.reason} ／ わからなかったこと ${r.unk}個`));
    box.append(li);
  }
}

async function share(rec) {
  const text = `${rec.galaxy}の惑星「${rec.name}」として、${rec.span}を生きた。${rec.reason}。出来事${rec.total}個のうち、わからなかったことは${rec.unk}個。\n惑星と生命の一生シミュレーター（宇宙の研究）`;
  const url = location.href.split("#")[0];
  try {
    if (navigator.share) { await navigator.share({ text, url }); return; }
    await navigator.clipboard.writeText(text + "\n" + url);
    $("#share").textContent = "コピーしました";
  } catch (_) {}
}

/* ---------- はじまり ---------- */
// 宇宙の画面から来たとき: ?m=星の重さ&born=宇宙の年齢（10億年）&g=銀河名&s=星の名前
let FROM = {};
function readFrom() {
  const q = new URLSearchParams(location.search);
  const m = Number(q.get("m")), born = Number(q.get("born"));
  if (!(m >= 0.08 && m <= 12) || !(born >= 0.1 && born <= 100000)) return false;
  const k = q.get("k"), a = Number(q.get("a")), l = q.get("l") || "";
  FROM = { ...(k && KINDS[k] ? { forceKind: k } : {}), ...(a > 0.001 && a < 1000 ? { forceA: a } : {}), ...(/^[b-z]$/.test(l) ? { forceLetter: l } : {}), forceM: m, forceBorn: born, galaxy: (q.get("g") || "").slice(0, 20) || undefined, starName: (q.get("s") || "").slice(0, 20) || undefined };
  return true;
}
document.addEventListener("DOMContentLoaded", () => {
  $("#go").addEventListener("click", start);
  $("#again").addEventListener("click", start);
  $("#back").addEventListener("click", () => { FROM = {}; $("#from-note").hidden = true; $("#screen-end").hidden = true; $("#screen-start").hidden = false; window.scrollTo(0, 0); });
  $("#pause").addEventListener("click", () => { if (!$("#branch").hidden) return; playing = !playing; $("#pause").textContent = playing ? "一時停止" : "再開"; });
  document.querySelectorAll("[data-speed]").forEach((b) => b.addEventListener("click", () => setSpeed(Number(b.dataset.speed))));
  $("#auto").addEventListener("change", (e) => { auto = e.target.checked; });
  $("#skip").addEventListener("click", () => { if (!$("#branch").hidden) return; setSpeed(16); });
  $("#branch").addEventListener("keydown", (e) => { // 分かれ道を開いている間は、Tab で外に出ない
    if (e.key !== "Tab") return;
    const f = [...$("#branch").querySelectorAll("button")]; const i = f.indexOf(document.activeElement);
    if (e.shiftKey && i <= 0) { e.preventDefault(); f[f.length - 1].focus(); } else if (!e.shiftKey && i === f.length - 1) { e.preventDefault(); f[0].focus(); }
  });
  const src = $("#sources");
  for (const k in SOURCES) src.append(el("li", null, SOURCES[k]));
  renderPast();
  if (readFrom()) { $("#from-note").hidden = false; $("#from-note").textContent = `宇宙の画面で選んだ星「${FROM.starName || ""}」（${FROM.galaxy || ""}）のまわりに生まれます。`; start(); }
});
