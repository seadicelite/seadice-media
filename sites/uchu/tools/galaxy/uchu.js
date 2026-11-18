"use strict";
/* 宇宙の一生 — ビッグバンから、銀河・星・惑星が生まれては消えていくまで。
   銀河の動きは本物の重力計算ではなく、動きのイメージ。時代ごとの説明と数の傾向は論文にもとづく。
   点1つは、たくさんの星の代表。記録はどこにも送らない。 */

const $ = (s) => document.querySelector(s);
const el = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; };
const R = Math.random;
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const between = (a, b) => a + R() * (b - a);
const pick = (a) => a[Math.floor(R() * a.length)];
const smooth = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
function weighted(pairs) { let s = 0; for (const p of pairs) s += p[1]; let x = R() * s; for (const p of pairs) { x -= p[1]; if (x <= 0) return p[0]; } return pairs[pairs.length - 1][0]; }
function poisson(l) { let n = 0, p = Math.exp(-l), s = p, u = R(); while (u > s && n < 20) { n++; p *= l / n; s += p; } return n; }

const TAG = { sure: "確か", est: "推定", unk: "わからない", mark: "目印" };
const SOURCES = {
  planck: "Planck Collaboration 2020, A&A 641, A6（宇宙の年齢138億年・宇宙の中身の割合）",
  cyburt: "Cyburt et al. 2016, Rev. Mod. Phys. 88, 015004（最初の数分で水素とヘリウムの原子核ができた）",
  springel: "Springel et al. 2005, Nature 435, 629（暗黒物質が網の目のように集まる計算）",
  carniani: "Carniani et al. 2024, Nature 633, 318（ビッグバンから約3億年後の銀河を JWST が確認）",
  madau: "Madau & Dickinson 2014, ARA&A 52, 415（宇宙で星が生まれた量の歴史）",
  connelly: "Connelly et al. 2012, Science 338, 651（太陽系で最も古い固まりは約45.7億年前）",
  riess: "Riess et al. 1998, AJ 116, 1009 / Perlmutter et al. 1999, ApJ 517, 565（宇宙の膨張は加速している）",
  krauss: "Krauss & Scherrer 2007, Gen. Rel. Grav. 39, 1545（遠い未来には、ほかの銀河が見えなくなる）",
  adams: "Adams & Laughlin 1997, Rev. Mod. Phys. 69, 337（星の時代の終わりと、その先の宇宙）",
  cassan: "Cassan et al. 2012, Nature 481, 167（星は平均1個以上の惑星を持つ）",
  fischer: "Fischer & Valenti 2005, ApJ 622, 1102（重い元素が多い星ほど巨大惑星を持ちやすい）",
  kopparapu: "Kopparapu et al. 2013, ApJ 765, 131（液体の水がありうる、星からの距離の範囲）",
  fressin: "Fressin et al. 2013, ApJ 766, 81 / Dressing & Charbonneau 2015, ApJ 807, 45（小さい惑星ほど多い。赤色矮星では巨大惑星が少ない）",
  k218: "Madhusudhan et al. 2025, ApJL 983, L40 とその反論（K2-18b の大気の成分をめぐって、生命のしるしかどうか意見が割れている）",
  lyons: "Lyons, Reinhard & Planavsky 2014, Nature 506, 307（地球の大気に酸素が増えた歴史）",
  morris: "Morris et al. 2018, PNAS 115, E2274（陸の植物が現れた時期）",
  kiang: "Kiang et al. 2007, Astrobiology 7, 252（赤色矮星の光の下の光合成は、赤外線に近い光を使うかもしれない）",
  takai: "Takai et al. 2008, PNAS 105, 10949（122℃でも増える微生物）",
  christner: "Christner et al. 2014, Nature 512, 310（南極の氷の下の湖に微生物がいる）",
  barnes: "Barnes 2017, Celest. Mech. Dyn. Astron. 129, 509（星に近い惑星は片面だけを星に向ける）",
  chen: "Chen & Kipping 2017, ApJ 834, 17（惑星の大きさと重さの関係）",
  sawala: "Sawala et al. 2025, Nature Astronomy（天の川銀河とアンドロメダ銀河が100億年以内にぶつかる確率は約半々）",
};

/* ---------- 時代の説明（t は宇宙の年齢、10億年単位） ---------- */
const ERAS = [
  { t: 0, tag: "est", src: ["planck"], title: "ビッグバン", text: "宇宙は、とても熱くて濃い状態から広がりはじめた。約138億年前のこと。「始まりそのもの」に何があったか、その前に何かあったのかは、わからない。" },
  { t: 3e-53, tag: "unk", src: [], title: "一瞬で急に膨らんだ（かもしれない）", text: "生まれてすぐ（1秒の1兆分の1のさらに1兆分の1より短い間）、急激に膨らんだという説（インフレーション）がある。多くの研究者が支持しているが、直接は確かめられていない。" },
  { t: 6e-15, tag: "sure", src: ["cyburt"], title: "最初の数分: 水素とヘリウムの原子核", text: "宇宙が冷えて、水素とヘリウムの原子核ができた。計算と、古いガスの観測がよく合っている。岩や鉄のもとになる重い元素は、まだない。" },
  { t: 3.8e-4, tag: "sure", src: ["planck"], title: "38万年: 宇宙の晴れ上がり", text: "原子ができて、光がまっすぐ進めるようになった。このときの光は今も「宇宙マイクロ波背景放射」として、空のあらゆる方向から届いている。" },
  { t: 5e-3, tag: "est", src: ["springel", "planck"], title: "暗黒時代: 見えないものが集まる", text: "星はまだ1つもない。光らない「暗黒物質」が重力で少しずつ集まり、網の目をつくる。暗黒物質の正体は、わからない。" },
  { t: 0.12, tag: "unk", src: [], title: "最初の星", text: "網の目の結び目で、最初の星が光りはじめた。とても重く、すぐに爆発したと考えられているが、最初の星そのものはまだ見つかっていない。" },
  { t: 0.3, tag: "sure", src: ["carniani"], title: "見つかっている中で最も古い銀河のころ", text: "星が集まって銀河になる。JWST は、ビッグバンから約3億年後の銀河を実際に見つけている。本当の最初の銀河がいつできたかは、まだわからない。" },
  { t: 2.5, tag: "sure", src: ["madau"], title: "星がいちばん多く生まれた時代", text: "ビッグバンから20〜40億年後ごろ、宇宙で星が最も盛んに生まれた。今は、そのころの10分の1ほどしか生まれていない。" },
  { t: 7.7, tag: "est", src: ["riess"], title: "膨張が加速しはじめる", text: "宇宙の膨張がだんだん速くなっていることは、観測で確かめられている。加速が始まったのは、ビッグバンから70〜80億年ごろと見積もられている。理由（暗黒エネルギー）の正体はわからない。" },
  { t: 9.2, tag: "sure", src: ["connelly"], title: "私たちの太陽系が生まれる", text: "このころ（約46億年前）、天の川銀河のどこかで、私たちの太陽と地球が生まれた。" },
  { t: 13.8, tag: "mark", src: [], title: "宇宙の「今」", text: "ここが、私たちのいる今。ここから先は、まだ誰も見たことのない未来。" },
  { t: 20, tag: "est", src: ["madau", "sawala"], title: "星の誕生が減っていく", text: "星の材料のガスが少なくなり、新しく生まれる星は減っていく。近くの銀河どうしはぶつかって、1つにまとまっていく。" },
  { t: 150, tag: "est", src: ["krauss"], title: "ほかの銀河が見えなくなる", text: "加速する膨張で、まとまった銀河のまわり以外は遠ざかり、光が届かなくなっていく。この時代の天文学者には、宇宙が膨張していることすらわからないかもしれない。" },
  { t: 3000, tag: "est", src: ["adams"], title: "赤色矮星だけが光る時代", text: "太陽のような星はとうに燃え尽き、残るのは小さく暗い赤色矮星だけ。そのまわりの惑星は、まだ光を受けている。" },
  { t: 7000, tag: "est", src: ["adams"], title: "最後の星が燃え尽きていく", text: "数兆年から十数兆年かけて、最後の赤色矮星も燃え尽きていく（ガスから星が細々と生まれ続ければ、100兆年ほど先まで続くという見積もりもある）。残るのは、冷えていく星の燃えかすと、そのまわりの惑星たち。" },
  { t: 29000, tag: "unk", src: ["adams"], title: "その先", text: "宇宙の最期は、冷えきって静かに終わるという説が有力。けれど暗黒エネルギーの正体しだいで変わり、本当のところはわからない。" },
];

/* ---------- 時間の進み方 ---------- */
// 0〜0.06: ビッグバン〜晴れ上がり（演出）／0.06〜0.16: 38万年〜1億年／0.16〜0.7: 1億年〜今／0.7〜1: 今〜30兆年（どれも対数）
const T_CMB = 3.8e-4, T_DARK = 0.1, T_NOW = 13.8, T_END = 3e4;
function timeAt(p) {
  if (p < 0.06) { const x = p / 0.06; return x < 0.3 ? 1e-56 * Math.pow(6e-15 / 1e-56, x / 0.3) : 6e-15 * Math.pow(T_CMB / 6e-15, (x - 0.3) / 0.7); }
  if (p < 0.16) return T_CMB * Math.pow(T_DARK / T_CMB, (p - 0.06) / 0.1);
  if (p < 0.7) return T_DARK * Math.pow(T_NOW / T_DARK, (p - 0.16) / 0.54);
  return T_NOW * Math.pow(T_END / T_NOW, (p - 0.7) / 0.3);
}
function fmtTime(t) {
  const y = t * 1e9;
  if (y < 1 / 3.15e7) { const sec = y * 3.15576e7; return sec <= 0 ? "0秒" : `10の${Math.floor(Math.log10(sec))}乗秒`; } // 1秒より短いあいだは桁で表す
  if (y < 1 / 8760) return Math.max(1, Math.round(y * 3.15e7 / 60)) + "分";
  if (y < 1) return Math.round(y * 365) + "日";
  if (y < 1e4) return Math.round(y).toLocaleString("ja-JP") + "年";
  if (y < 1e8) return Math.round(y / 1e4).toLocaleString("ja-JP") + "万年";
  if (y < 1e12) return (Math.round(y / 1e7) / 10).toLocaleString("ja-JP") + "億年";
  return (Math.round(y / 1e11) / 10).toLocaleString("ja-JP") + "兆年";
}
function relNow(t) { if (Math.abs(t - T_NOW) < 0.05) return "宇宙の「今」"; return t < T_NOW ? `今から${fmtTime(T_NOW - t)}前` : `今から${fmtTime(t - T_NOW)}後`; }

// 星が生まれる量（Madau & Dickinson 2014 の式を宇宙の年齢に直す。今より先はゆるやかに減る目安）
function sfr(t) {
  if (t < 0.12) return 0;
  if (t > T_NOW) return sfr(T_NOW) * Math.exp(-(t - T_NOW) / 15);
  if (t < 0.6) return Math.max(0.12, sfrMD(t)); // 最初の星の時代（どれくらい生まれたかはわからないので、見える程度に置いた）
  return sfrMD(t);
}
function sfrMD(t) {
  const H = 14.44, OL = 0.69, OM = 0.31, k = 1.5 * Math.sqrt(OL) / H;
  const opz = Math.pow(Math.sqrt(OL / OM) / Math.sinh(k * t), 2 / 3);
  return Math.pow(opz, 2.7) / (1 + Math.pow(opz / 2.9, 5.6)) / 9.5; // 山のてっぺんがおよそ1
}

/* ---------- 星 ---------- */
const STAR_TYPES = [
  { t: "M", name: "赤色矮星", w: 73, m: [0.08, 0.5], c: "#ff8a5c" },
  { t: "K", name: "オレンジ色の星", w: 13, m: [0.5, 0.85], c: "#ffb070" },
  { t: "G", name: "太陽に似た星", w: 7.5, m: [0.85, 1.1], c: "#ffe08a" },
  { t: "F", name: "白っぽい黄色の星", w: 3, m: [1.1, 1.5], c: "#fff3c4" },
  { t: "A", name: "白い星", w: 0.6, m: [1.5, 2.5], c: "#e3ebff" },
  { t: "B", name: "青白い重い星", w: 0.13, m: [2.5, 12], c: "#b9c9ff" },
];
function starLum(M) { if (M < 0.43) return 0.23 * Math.pow(M, 2.3); if (M < 2) return Math.pow(M, 4); return 1.4 * Math.pow(M, 3.5); }
function lifetime(M) { return 10 * M / starLum(M) * (M < 0.35 ? 7 : 1); }

const SYL = ["ア","イ","ウ","エ","オ","カ","キ","ク","ケ","コ","サ","シ","ス","セ","ソ","タ","テ","ト","ナ","ニ","ノ","ハ","ヒ","フ","ホ","マ","ミ","ム","メ","モ","ユ","ラ","リ","ル","レ","ロ","ヴァ","ゼ","ガ","ド","ベ","ポ","ティ","ジュ"];
const END = ["ン","ス","ア","ル","ラ","ナ","","",""];
const makeName = (n) => { let s = ""; for (let i = 0; i < n; i++) s += pick(SYL); return s + pick(END); };

/* ---------- 世界 ---------- */
let lastFind = 0, followed = null;
let eraHold = 0, hzList = [], found = null, revealed = false, lifeP = 0.1;
let halos, parts, stars, flashes, counts, eraIdx, prog, speed, playing, last, durSec, tNow, logs, lastLogAt, selected;
const MAX_STARS = 1400;

function haloPos(h, t) { // 銀河の中心の位置（動きのイメージ）
  if (h.fate === "merge") {
    const tg = halos[h.target]; const tp = haloPos(tg, t);
    const s = smooth((t - h.tm * 0.35) / (h.tm * 0.65));
    return [h.x + (tp[0] - h.x) * s, h.y + (tp[1] - h.y) * s];
  }
  if (h.fate === "drift") { const f = Math.pow(1 + Math.max(0, t - 12) / 12, 1.1); return [0.5 + (h.x - 0.5) * f, 0.5 + (h.y - 0.5) * f]; }
  return [h.x, h.y];
}

function init() {
  halos = [];
  halos.push({ x: 0.5, y: 0.5, mass: 4, fate: "stay" });
  for (let i = 1; i < 15; i++) {
    let x, y; do { x = between(0.06, 0.94); y = between(0.06, 0.94); } while (Math.hypot(x - 0.5, y - 0.5) < 0.12);
    halos.push({ x, y, mass: Math.exp(between(Math.log(0.2), Math.log(2.5))) });
  }
  // 行き先: 近くの大きな銀河に合流するか、膨張で遠ざかるか
  halos.forEach((h, i) => {
    if (i === 0) return;
    const d = Math.hypot(h.x - 0.5, h.y - 0.5);
    let best = -1, bd = 9;
    halos.forEach((o, j) => { if (j !== i && o.mass > h.mass && (j === 0 || o.fate !== "drift")) { const dd = Math.hypot(o.x - h.x, o.y - h.y); if (dd < bd) { bd = dd; best = j; } } });
    if (d < 0.3 || (best >= 0 && bd < 0.2)) { h.fate = "merge"; h.target = d < 0.3 ? 0 : best; h.tm = h.target === 0 ? Math.exp(between(Math.log(3), Math.log(60))) : Math.exp(between(Math.log(0.8), Math.log(10))); }
    else h.fate = "drift";
  });
  // 合流先が遠ざかる銀河なら、自分も一緒に遠ざかる
  halos.forEach((h) => { if (h.fate === "merge" && halos[h.target].fate === "drift" && h.tm > 12) h.tm = between(2, 12); });
  halos.forEach((h) => { h.size = 0.036 * Math.sqrt(h.mass); h.born = false; h.merged = false; h.name = makeName(2) + "銀河"; });

  parts = [];
  for (let i = 0; i < 1600; i++) {
    const x = R(), y = R();
    let best = 0, bd = 9;
    halos.forEach((h, j) => { const d = Math.hypot(h.x - x, h.y - y) / Math.sqrt(h.mass); if (d < bd) { bd = d; best = j; } });
    parts.push({ h: best, ox: x - halos[best].x, oy: y - halos[best].y });
  }
  stars = []; flashes = []; logs = []; hzList = []; found = null; revealed = false;
  $("#search-result").textContent = ""; $("#reveal").hidden = true; $("#reveal-result").textContent = "";
  lastFind = 0; followed = null; $("#follow").hidden = true; $("#discover").hidden = true;
  counts = { found: 0, born: 0, died: 0, sn: 0, pBorn: 0, pLost: 0, merges: 0, galaxies: 0 };
  eraIdx = -1; eraHold = 0; prog = 0; speed = 1; playing = true; last = 0; lastLogAt = -9; selected = null;
  $("#log").textContent = "";
  $("#star-panel").hidden = true;
}

function rootOf(i) { let h = halos[i]; while (h.fate === "merge" && h.merged) { i = h.target; h = halos[i]; } return i; }

const KINDS = { rocky: "地球サイズの岩の惑星", superE: "スーパーアース（大きな岩の惑星）", subnep: "サブネプチューン（水素をまとった小さな惑星）", nep: "海王星のような氷の巨大惑星", giant: "木星のようなガスの巨大惑星" };
const logBetween = (a, b) => Math.exp(between(Math.log(a), Math.log(b)));
function makePlanets(M, t, n, isM) {
  // 種類の割合は Fressin 2013・Dressing & Charbonneau 2015 の傾向を丸めた目安（惑星版と同じ）
  const g = t < 1 ? 0.2 : t < 3 ? 0.6 : 1;
  const L = starLum(M), list = [];
  for (let i = 0; i < n; i++) {
    const k = isM ? weighted([["rocky", 40], ["superE", 34], ["subnep", 21], ["nep", 3], ["giant", 2 * g]]) : weighted([["rocky", 26], ["superE", 30], ["subnep", 28], ["nep", 7], ["giant", 9 * g]]);
    const a = k === "giant" || k === "nep" ? logBetween(0.03, 20) * Math.cbrt(M) : logBetween(0.012, 2.5) * Math.max(Math.sqrt(L), Math.cbrt(M) * 0.3);
    const S = L / (a * a);
    // 液体の水がありうる距離（Kopparapu 2013 のおおよその範囲）にある岩の惑星だけを「水がありうる」とする
    const hz = (k === "rocky" || k === "superE") && S > 0.36 && S < 1.1;
    const rr = { rocky: [0.5, 1.25], superE: [1.25, 2], subnep: [2, 4], nep: [4, 7], giant: [8, 15] }[k];
    const rad = between(rr[0], rr[1]);
    const mass = rad < 1.23 ? Math.pow(rad, 1 / 0.279) : 2 * Math.pow(rad / 1.23, 1 / 0.589); // Chen & Kipping 2017 のおおまかな関係
    list.push({ k, a, S, hz, rad, grav: mass / (rad * rad), locked: a < 0.3 * Math.cbrt(M), life: null, alive: true, cand: false, checked: false, announced: false });
  }
  list.sort((x, y) => x.a - y.a);
  list.forEach((p, i) => { p.letter = "bcdefghij"[i] || "z"; });
  return list;
}

function spawnStar(hi, t) {
  const h = halos[hi];
  const popIII = t < 0.4;
  let M, type;
  if (popIII) { M = between(20, 100); type = { name: "最初の世代の重い星", c: "#cfe0ff", t: "III" }; }
  else { type = weighted(STAR_TYPES.map((s) => [s, s.w])); M = between(type.m[0], type.m[1]); }
  const metal = t < 1 ? 0.2 : t < 3 ? 0.6 : 1; // 重い元素が少ない昔は惑星が少ない、という傾向の目安
  const np = popIII ? 0 : poisson(1.6 * metal);
  const r = h.size * (0.15 + -Math.log(1 - R() * 0.95) * 0.7);
  const s = { h: hi, r, a: R() * 6.283, w: (0.25 + R() * 0.3) / Math.sqrt(r * 30 + 0.2), M, type, born: t, dies: t + (popIII ? 0.003 : lifetime(M)), planets: np, pLeft: np, alive: true, name: null, x: 0, y: 0 };
  s.pl = makePlanets(M, t, np, type.t === "M");
  for (const p of s.pl) if (p.hz) hzList.push({ s, p });
  stars.push(s); counts.born++; counts.pBorn += np;
}

function killStar(s, t) {
  s.alive = false; counts.died++;
  let lost = 0;
  if (s.M >= 8) counts.sn++;
  for (const p of s.pl) {
    // 重い星は爆発で、それ以外はふくらんだ星に近い惑星が飲み込まれる（赤色巨星の大きさは、おおよそ星の重さ×1天文単位の目安）
    if (p.alive && (s.M >= 8 || (s.M >= 0.5 && p.a < s.M))) { p.alive = false; lost++; }
    if (p.life === "yes") p.life = "gone"; // 星が燃え尽きたら、生き物もいなくなったとする
  }
  s.pLeft -= lost; counts.pLost += lost;
  flashes.push({ x: s.x, y: s.y, r: s.M >= 8 ? 14 : 6, life: 1, c: s.M >= 8 ? "#cfe0ff" : "#ff7043" });
  if (selected === s) showStar(s);
  const g = halos[rootOf(s.h)];
  if (s.M >= 8 && t > 0.4) addLog(t, "est", `${g.name}で、重い星が超新星爆発` + (lost ? `。惑星${lost}個が吹き飛んだ` : ""), true);
  else if (lost) addLog(t, "est", `${g.name}で、年老いた星がふくらみ、惑星${lost}個を飲み込んだ`, true);
}

function addLog(t, tag, text, throttle, action) {
  if (throttle && prog - lastLogAt < 0.012) return;
  if (throttle) lastLogAt = prog;
  const li = el("li");
  li.append(el("span", "lt", fmtTime(t)), el("span", "tag tag-" + tag, TAG[tag]), document.createTextNode(text));
  if (action) { const b = el("button", "mini", action[0]); b.type = "button"; b.addEventListener("click", action[1]); li.append(b); }
  const box = $("#log"); box.prepend(li);
  while (box.children.length > 40) box.lastChild.remove();
}

/* ---------- 1コマ進める ---------- */
function step(dtReal) {
  const p0 = prog;
  eraHold = Math.max(0, eraHold - dtReal);
  if (playing) prog = Math.min(1, prog + (dtReal * (eraHold > 0 ? 0.02 : speed)) / durSec);
  const t0 = timeAt(p0), t = timeAt(prog); tNow = t;
  const dt = Math.max(0, t - t0);

  // 時代の説明
  if (eraIdx + 1 < ERAS.length && ERAS[eraIdx + 1].t <= t) { eraIdx++; showEra(ERAS[eraIdx]); eraHold = 3; } // 1コマに1つずつ。新しい時代は3秒ほぼ止めて、説明を読めるようにする

  // 銀河の合流
  halos.forEach((h, i) => {
    if (h.fate === "merge" && !h.merged && t >= h.tm) {
      h.merged = true; counts.merges++;
      const a = halos[rootOf(i)];
      if (h.born && a.born) addLog(t, "est", `${h.name}が${a.name}とぶつかり、1つの銀河にまとまった`, false);
      stars.forEach((s) => { if (s.h === i) s.h = h.target; });
      halos[h.target].mass += h.mass; halos[h.target].size = 0.036 * Math.sqrt(halos[h.target].mass);
    }
  });

  // 星が生まれる（銀河の重さに比例。点の数には上限がある）
  if (dt > 0 && t > 0.12) {
    const rate = sfr(t) * 200; // 10億年あたりの点の数（全体）
    const alive = stars.length;
    const n = Math.min(40, Math.floor(rate * dt + R()));
    for (let k = 0; k < n && alive + k < MAX_STARS; k++) {
      const hi = weighted(halos.map((h, j) => [j, h.merged ? 0 : h.mass]));
      const h = halos[hi];
      if (!h.born) { h.born = true; counts.galaxies++; if (t > 0.25) addLog(t, "sure", `${h.name}で星が光りはじめた`, false); }
      spawnStar(hi, t);
    }
  }
  // 生命: 液体の水がありうる惑星に5億年いたら、つまみの確率で一度だけ決める（本当の確率は誰にもわからない）
  for (const o of hzList) {
    if (o.p.life !== null || !o.s.alive || !o.p.alive) continue;
    if (t - o.s.born > 0.5) o.p.life = R() < lifeP ? "yes" : "no";
  }
  // 発見: 私たちの銀河で、生命がいられるかもしれない惑星が見つかる（多すぎないよう間をあける）
  if (t > 1 && prog - lastFind > 0.025 && counts.found < 14) {
    const c = hzList.filter((o) => !o.p.announced && o.p.alive && o.s.alive && rootOf(o.s.h) === 0 && t - o.s.born > 0.5);
    if (c.length) { const o = pick(c); o.p.announced = true; lastFind = prog; counts.found++; announce(o.s, o.p, t); }
  }
  // 星が燃え尽きる
  for (const s of stars) if (s.alive && s.dies <= t) killStar(s, t);
  // 燃え尽きた星は、しばらくして点を消す（数え上げは残す）
  if (stars.length > MAX_STARS * 0.9) stars = stars.filter((s) => s.alive || s === selected);

  // 星をまわす
  for (const s of stars) { s.a += s.w * dtReal * 0.6; }
  for (const f of flashes) f.life -= dtReal * 1.2;
  flashes = flashes.filter((f) => f.life > 0);

  if (prog >= 1 && playing) { playing = false; $("#pause").textContent = "もう一度見る"; addLog(t, "unk", "ここで画面は終わり。この先の宇宙がどうなるかは、わからない。", false); }
}

/* ---------- 描く ---------- */
let cv, ctx, W, H, DPR;
function resize() {
  DPR = Math.min(2, window.devicePixelRatio || 1);
  const w = cv.clientWidth; W = w; H = Math.round(w * (w < 600 ? 1 : 0.62));
  cv.style.height = H + "px"; cv.width = W * DPR; cv.height = H * DPR;
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
}
function toScreen(x, y) { const s = Math.max(W, H); return [W / 2 + (x - 0.5) * s * 0.95, H / 2 + (y - 0.5) * s * 0.95]; }

function draw() {
  const t = tNow;
  ctx.fillStyle = "#05060a"; ctx.fillRect(0, 0, W, H);
  // ビッグバン〜晴れ上がり: 画面全体が熱く光り、だんだん冷える（色だけで表す）
  if (t < T_CMB * 1.5) {
    const x = prog / 0.06; // 0→1
    const col = x < 0.35 ? "#fff8ea" : x < 0.7 ? "#ffd59a" : x < 0.95 ? "#e0763c" : "#7a2e1c";
    ctx.globalAlpha = t < T_CMB ? 1 : clamp(1 - (t - T_CMB) / (T_CMB * 0.5), 0, 1);
    ctx.fillStyle = col; ctx.fillRect(0, 0, W, H);
    ctx.globalAlpha = 1;
    if (t < T_CMB) return;
  }
  // 暗黒物質とガス: 網の目に集まっていく
  const collapse = smooth((Math.log10(t) - Math.log10(0.003)) / (Math.log10(3) - Math.log10(0.003)));
  const gasA = t < 3 ? 0.75 : Math.max(0.12, 0.75 * Math.sqrt(3 / t));
  ctx.fillStyle = "#7d89a8"; ctx.globalAlpha = gasA;
  const hp = halos.map((h) => haloPos(h, t));
  for (const q of parts) {
    const c = hp[q.h]; const f = 1 - 0.88 * collapse;
    const [sx, sy] = toScreen(c[0] + q.ox * f, c[1] + q.oy * f);
    if (sx < -2 || sy < -2 || sx > W + 2 || sy > H + 2) continue;
    ctx.fillRect(sx, sy, 1.6, 1.6);
  }
  ctx.globalAlpha = 1;
  // 星
  const scale = Math.max(W, H) * 0.95;
  for (const s of stars) {
    if (!s.alive && (s.M >= 8 || s.type.t === "III")) continue; // 重い星は爆発して、点は残さない
    const c = hp[s.h];
    const [cx, cy] = toScreen(c[0], c[1]);
    s.x = cx + Math.cos(s.a) * s.r * scale; s.y = cy + Math.sin(s.a) * s.r * scale * 0.55;
    if (s.x < -3 || s.y < -3 || s.x > W + 3 || s.y > H + 3) continue;
    if (!s.alive) { ctx.fillStyle = "#4a5060"; ctx.fillRect(s.x - 0.6, s.y - 0.6, 1.2, 1.2); continue; } // 燃えかす
    const z = s.M >= 2.5 ? 3 : s.M >= 0.85 ? 2.2 : 1.6;
    ctx.fillStyle = s.type.c; ctx.fillRect(s.x - z / 2, s.y - z / 2, z, z);
  }
  // 燃え尽きた瞬間（輪で表す）
  for (const f of flashes) {
    ctx.strokeStyle = f.c; ctx.globalAlpha = clamp(f.life, 0, 1); ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.arc(f.x, f.y, f.r * (1.6 - f.life), 0, 6.283); ctx.stroke();
  }
  ctx.globalAlpha = 1;
  if (found) { ctx.strokeStyle = "#7fd1ff"; ctx.lineWidth = 1; for (const c of found.cands) if (c.s.alive) { ctx.beginPath(); ctx.arc(c.s.x, c.s.y, 5, 0, 6.283); ctx.stroke(); } }
  if (selected && selected.alive) { ctx.strokeStyle = "#ffd36b"; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(selected.x, selected.y, 8, 0, 6.283); ctx.stroke(); }
}

/* ---------- 文字の表示 ---------- */
function showEra(e) {
  $("#era-title").textContent = e.title;
  const mini = $("#era-mini"); mini.textContent = ""; mini.append(el("span", "tag tag-" + e.tag, TAG[e.tag]), document.createTextNode(e.title));
  const tg = $("#era-tag"); tg.className = "tag tag-" + e.tag; tg.textContent = TAG[e.tag];
  $("#era-text").textContent = e.text;
  $("#era-src").textContent = e.src.length ? "出典: " + e.src.map((k) => SOURCES[k]).join(" ／ ") : "";
  addLog(e.t, e.tag, e.title, false);
}
function renderStats() {
  const alive = stars.filter((s) => s.alive);
  const pAlive = counts.pBorn - counts.pLost;
  $("#t-age").textContent = prog === 0 ? "0秒" : fmtTime(tNow);
  $("#t-rel").textContent = relNow(tNow);
  $("#bar").style.width = (prog * 100).toFixed(1) + "%";
  $("#n-gal").textContent = halos.filter((h, i) => h.born && !h.merged && inView(haloPos(h, tNow))).length;
  $("#n-star").textContent = alive.length.toLocaleString("ja-JP");
  $("#n-died").textContent = counts.died.toLocaleString("ja-JP");
  $("#n-pl").textContent = pAlive.toLocaleString("ja-JP");
  $("#n-pl-lost").textContent = counts.pLost.toLocaleString("ja-JP");
}
function inView(p) { const [x, y] = toScreen(p[0], p[1]); return x > 0 && y > 0 && x < W && y < H; }

function showStar(s) {
  selected = s;
  if (!s.name) s.name = makeName(2);
  const g = halos[rootOf(s.h)];
  const panel = $("#star-panel"); const wasHidden = panel.hidden; panel.hidden = false;
  if (wasHidden && window.innerWidth < 960) panel.scrollIntoView({ block: "nearest" });
  $("#sp-name").textContent = `${s.name}（${s.type.name}）`;
  const age = Math.max(0, Math.min(tNow, s.dies) - s.born);
  $("#sp-info").textContent = `${g.name} ／ 重さ 太陽の${s.M < 1 ? s.M.toFixed(2) : s.M.toFixed(1)}倍 ／ ${s.alive ? `生まれて${fmtTime(age)}。寿命はおよそ${fmtTime(s.dies - s.born)}` : "もう燃え尽きた"} ／ 惑星 ${s.planets}個` + (s.planets !== s.pLeft ? `（うち${s.planets - s.pLeft}個は亡くなった）` : "");
  const list = $("#sp-planets"); list.textContent = "";
  if (s.type.t === "III") $("#sp-note").textContent = "最初の世代の星には、惑星の材料（重い元素）がほとんどなかったと考えられている。";
  else if (s.planets === 0) $("#sp-note").textContent = "この星には、惑星が生まれなかった。";
  else $("#sp-note").textContent = "";
  for (const p of s.pl) {
    const li = el("li");
    const lifeWord = !p.hz ? "" : !revealed ? (p.cand ? " ／ 生命のしるしに似た反応が出た（本物かはわからない）" : " ／ 生命: 答え合わせまでわからない")
      : { yes: " ／ 生命: いる", no: " ／ 生命: いない", gone: " ／ 生命: いたが、いなくなった", null: " ／ 生命: まだ決まっていない" }[p.life];
    li.append(el("strong", null, `${s.name} ${p.letter}`), el("span", null, `${KINDS[p.k]} ／ 受ける光 地球の${p.S < 0.01 ? p.S.toExponential(1) : p.S < 10 ? p.S.toFixed(2) : Math.round(p.S)}倍` + (p.hz ? " ／ 液体の水がありうる距離" : "") + (p.alive ? "" : " ／ 亡くなった") + lifeWord));
    if (p.alive && p.hz) { const b = el("button", "mini", "生命の可能性を追う"); b.type = "button"; b.addEventListener("click", () => follow(s, p)); li.append(b); }
    if (p.alive) {
      const a = el("a", null, "この惑星の一生を見る");
      a.href = `../planet/?m=${s.M.toFixed(3)}&born=${s.born.toFixed(3)}&g=${encodeURIComponent(g.name)}&s=${encodeURIComponent(s.name)}&k=${p.k}&a=${p.a.toFixed(4)}&l=${p.letter}`;
      li.append(a);
    }
    list.append(li);
  }
}

/* ---------- 発見と、1つの惑星を追う ---------- */
function planetLabel(s, p) { if (!s.name) s.name = makeName(2); return `${s.name} ${p.letter}`; }
function announce(s, p, t) {
  const name = planetLabel(s, p);
  const text = `この画面の宇宙で、水がありうる距離の惑星を見つけた: ${halos[0].name}の「${name}」（${KINDS[p.k]}）。生命がいるかどうかは、わからない`;
  addLog(t, "est", text, false, ["追ってみる", () => follow(s, p)]);
  const d = $("#discover"); d.hidden = false;
  $("#discover-text").textContent = text + "。距離だけで選んでいて、大気や磁場などの条件はわからない。";
  $("#discover-go").onclick = () => follow(s, p);
}

// 地球の歩み（1つの例）。惑星が生まれてからの年数（10億年）
const EARTH = [
  { age: 0.8, tag: "est", src: [], title: "最初の生命（微生物）", text: "地球では、生まれて10億年たたないうちに生命の痕跡がある（どこまでさかのぼるかは議論が続いている）。" },
  { age: 1.7, tag: "est", src: [], title: "光で酸素をつくる光合成", text: "地球では、生まれて15〜20億年ごろまでに、光で酸素をつくる微生物が現れた。" },
  { age: 2.1, tag: "sure", src: ["lyons"], title: "大気に酸素が増える", text: "地球では、生まれて約21億年後（約24億年前）に、大気の酸素がはっきり増えた。" },
  { age: 4.0, tag: "est", src: [], title: "大きな多細胞の生き物", text: "地球では、生まれて約40億年後（約5.7億年前）に、目で見える大きさの生き物が海に現れた。" },
  { age: 4.1, tag: "est", src: ["morris"], title: "陸に上がる", text: "地球では、生まれて約41億年後（約4.7億年前）までに、植物が陸に広がりはじめた。" },
  { age: 4.57, tag: "unk", src: [], title: "道具と言葉を使う生き物", text: "地球では、生まれて約45.7億年後に人類が現れた。地球以外の例がないので、これが早いのか遅いのか、めったに起きないことなのかは、わからない。" },
];

function lifeIdeas(s, p) { // その惑星の条件から考えられる生き物の案。地球に実在する例は「確か」、想像は「わからない」
  const ideas = [];
  const add = (tag, src, title, text) => ideas.push({ tag, src, title, text });
  add("sure", [], "熱水の噴き出し口の微生物", "光が届かない海の底でも、地球には岩と水の化学反応からエネルギーを得る微生物がいる。光がなくても始められる生き方。");
  if (s.type.t === "M") {
    add("est", ["kiang"], "黒っぽい植物", `星（${s.type.name}）の光は赤く、赤外線に近い。光合成をする生き物がいるなら、その光をむだなく吸うため、黒っぽく見えるかもしれない。`);
    add("unk", [], "水の中や地下で暮らす生き物", "赤色矮星は若いころ強いフレアを出す。紫外線を避けて、水の中や地下で暮らすほうが生き残りやすいかもしれない。");
  }
  if (p.locked) add("unk", ["barnes"], "昼と夜の境目に集まる生き物", "この惑星は片面だけを星に向けている（推定）。ずっと昼の面は暑く、ずっと夜の面は寒い。その境目の、ちょうどよい温度の帯に生き物が集まるかもしれない。");
  if (p.grav > 1.3) add("unk", ["chen"], "背が低く、がっしりした生き物", `重力が地球のおよそ${p.grav.toFixed(1)}倍（大きさからの推定）。体を支えるため、背が低く、がっしりした体になるかもしれない。確かめようのない想像。`);
  if (p.grav < 0.7) add("unk", [], "大気を保てるかが分かれ目", `重力が地球のおよそ${p.grav.toFixed(1)}倍と小さい。大気が宇宙へ逃げやすく、生き物が続くには不利かもしれない。`);
  if (p.S < 0.6) add("est", ["christner"], "氷の下の海の生き物", "受ける光が地球より弱く、寒いかもしれない。表面が凍っても、氷の下に海が残れば暮らせるかもしれない。地球では、南極の厚い氷の下の湖に微生物がいることが確かめられている。");
  if (p.S > 1.0) add("est", ["takai"], "熱に強い微生物", "受ける光が地球より少し強い。地表が暑くなるかもしれない。地球では、深海の熱水の噴き出し口（高い圧力の下）で、122℃でも増える微生物が見つかっている。地表の暑さにそのまま当てはまるかは、わからない。");
  const tl = lifetime(s.M);
  if (tl > 30) add("est", [], "時間はたっぷりある", `星の寿命は約${fmtTime(tl)}。地球の歩み（約46億年）の何倍もの時間をかけて、ゆっくり進化できる。`);
  else if (tl < 5) add("est", [], "時間が足りないかもしれない", `星の寿命は約${fmtTime(tl)}と短い。地球と同じ速さなら、大きな生き物が現れる前に星が燃え尽きる。`);
  add("unk", [], "知性まで行けるか", "道具や言葉を使う生き物まで行けるかは、わからない。地球では約45億年かかったが、例は地球の1つだけ。");
  return ideas;
}

function follow(s, p) {
  followed = { s, p, ideas: lifeIdeas(s, p) };
  const box = $("#follow"); box.hidden = false;
  $("#f-name").textContent = `${planetLabel(s, p)} を追う`;
  const g = halos[rootOf(s.h)];
  $("#f-facts").textContent = `${g.name} ／ ${s.type.name}（重さ 太陽の${s.M < 1 ? s.M.toFixed(2) : s.M.toFixed(1)}倍）を回る${KINDS[p.k]} ／ 大きさ 地球の${p.rad.toFixed(2)}倍 ／ 重力 地球の約${p.grav.toFixed(1)}倍 ／ 受ける光 地球の${p.S.toFixed(2)}倍` + (p.locked ? " ／ 片面だけ星を向いている（推定）" : "");
  const ul = $("#f-ideas"); ul.textContent = "";
  for (const i of followed.ideas) {
    const li = el("li");
    li.append(el("span", "tag tag-" + i.tag, TAG[i.tag]), el("strong", null, i.title), el("p", null, i.text));
    if (i.src.length) li.append(el("p", "src", "出典: " + i.src.map((k) => SOURCES[k]).join(" ／ ")));
    ul.append(li);
  }
  $("#f-go").href = `../planet/?m=${s.M.toFixed(3)}&born=${s.born.toFixed(3)}&g=${encodeURIComponent(g.name)}&s=${encodeURIComponent(s.name)}&k=${p.k}&a=${p.a.toFixed(4)}&l=${p.letter}`;
  renderFollow();
  selected = s;
  if (window.innerWidth < 960) box.scrollIntoView({ block: "start" });
}
function renderFollow() {
  if (!followed) return;
  const { s, p } = followed;
  const age = Math.max(0, Math.min(tNow, s.alive ? tNow : s.dies) - s.born);
  const st = $("#f-status");
  if (!p.alive) st.textContent = "この惑星は、星の最期に巻き込まれて亡くなった。";
  else if (!s.alive) st.textContent = `星が燃え尽きた。惑星は冷えていく。生き物がいたとしても、表面では続けられない（生まれて${fmtTime(age)}）。`;
  else st.textContent = `生まれて${fmtTime(age)}。もし地球と同じ速さで進んだら、今ごろは下の「済」の段階まで来ている（本当に進んでいるかは、わからない）。`;
  const ol = $("#f-earth"); ol.textContent = "";
  for (const e of EARTH) {
    const li = el("li", age >= e.age && p.alive && s.alive ? "done" : "");
    li.append(el("span", "lt", fmtTime(e.age)), el("span", "tag tag-" + e.tag, TAG[e.tag]), el("strong", null, (age >= e.age ? "済 " : "") + e.title), el("p", null, e.text));
    ol.append(li);
  }
}

/* ---------- 生命さがし ---------- */
// 見つけやすさは仮の値: 生命がいる惑星のしるしを捉えられるのは3回に1回ほど、生命のいない惑星が生命のように見える誤検出もある
const DETECT = 0.35, FP_HZ = 0.05, FP_OTHER = 0.005;
function search() {
  const home = 0; let n = 0; const cands = [];
  for (const s of stars) {
    if (!s.alive || rootOf(s.h) !== home) continue;
    for (const p of s.pl) {
      if (!p.alive) continue; n++; p.checked = true;
      const hit = p.life === "yes" ? R() < DETECT : R() < (p.hz ? FP_HZ : FP_OTHER);
      p.cand = hit; if (hit) cands.push({ s, p });
    }
  }
  found = { n, cands, t: tNow };
  const box = $("#search-result"); box.textContent = "";
  box.append(el("p", null, `${halos[0].name}（画面の真ん中の、私たちの銀河）の惑星 ${n.toLocaleString("ja-JP")}個を調べた。生命のしるしに似た反応が出た惑星は ${cands.length}個（画面の水色の輪）。本物の生命かどうかは、答え合わせまでわからない。`));
  box.append(el("p", "note", "ほかの銀河の惑星は遠すぎて調べられない（本物の望遠鏡でも同じ）。しるしが出ても、本物の生命か、火山などの化学による見まちがいかは、ここからはわからない。"));
  const ul = el("ul", "list");
  for (const c of cands.slice(0, 8)) {
    const li = el("li"); const b = el("button", null, `${c.s.name || (c.s.name = makeName(2))} ${c.p.letter}（${KINDS[c.p.k]}）`);
    b.type = "button"; b.addEventListener("click", () => showStar(c.s)); li.append(b); ul.append(li);
  }
  if (cands.length > 8) ul.append(el("li", "note", `ほか ${cands.length - 8}個`));
  box.append(ul);
  $("#reveal").hidden = false; revealed = false; $("#reveal-result").textContent = "";
  if (selected) showStar(selected);
}
function reveal() {
  if (!found) return;
  revealed = true;
  let real = 0, fake = 0, missed = 0, far = 0, ever = 0;
  for (const c of found.cands) c.p.life === "yes" ? real++ : fake++;
  for (const s of stars) for (const p of s.pl) {
    if (p.life === "yes" || p.life === "gone") ever++;
    if (p.life !== "yes" || !s.alive) continue;
    if (rootOf(s.h) === 0) { if (!p.cand) missed++; } else far++;
  }
  const box = $("#reveal-result"); box.textContent = "";
  const ul = el("ul", "stats");
  for (const [v, w] of [[real, "反応のうち、本物の生命だった"], [fake, "反応のうち、見まちがいだった"], [missed, "見落とした生命（私たちの銀河）"], [far, "調べられないほかの銀河の生命"], [ever, "これまでに生命が生まれた惑星（燃え尽きた星も含む）"]]) { const li = el("li"); li.append(el("b", null, String(v)), document.createTextNode(w)); ul.append(li); }
  box.append(ul);
  box.append(el("p", "note", `この答えは、つまみで置いた「生命が生まれる確率 ${fmtP(lifeP)}」と、見つけやすさの仮の値で決まっている。本物の宇宙で生命が見つかった例は、地球のほかにまだ1つもない。`));
  if (selected) showStar(selected);
}
function fmtP(p) { const v = p * 100; return (v >= 1 ? v.toFixed(0) : v >= 0.01 ? v.toFixed(2) : v.toFixed(3)) + "%"; }

/* ---------- 動かす ---------- */
function loop(ts) {
  const dt = last ? Math.min(0.1, (ts - last) / 1000) : 0; last = ts;
  step(dt); draw();
  if (Math.floor(ts / 200) !== Math.floor((ts - dt * 1000) / 200)) { renderStats(); if (followed && Math.floor(ts / 1000) !== Math.floor((ts - dt * 1000) / 1000)) renderFollow(); }
  requestAnimationFrame(loop);
}
function setSpeed(v) { speed = v; document.querySelectorAll("[data-speed]").forEach((b) => b.setAttribute("aria-pressed", String(Number(b.dataset.speed) === v))); }

document.addEventListener("DOMContentLoaded", () => {
  cv = $("#sky"); ctx = cv.getContext("2d");
  durSec = Number($("#len").value);
  init(); resize(); window.addEventListener("resize", resize);
  setSpeed(1);
  $("#pause").addEventListener("click", () => {
    if (prog >= 1) { init(); durSec = Number($("#len").value); setSpeed(1); $("#pause").textContent = "一時停止"; return; }
    playing = !playing; $("#pause").textContent = playing ? "一時停止" : "再開";
  });
  $("#restart").addEventListener("click", () => { init(); durSec = Number($("#len").value); setSpeed(1); $("#pause").textContent = "一時停止"; });
  $("#len").addEventListener("change", (e) => { durSec = Number(e.target.value); });
  document.querySelectorAll("[data-speed]").forEach((b) => b.addEventListener("click", () => setSpeed(Number(b.dataset.speed))));
  cv.addEventListener("click", (e) => {
    const r = cv.getBoundingClientRect(); const x = e.clientX - r.left, y = e.clientY - r.top;
    let best = null, bd = 18;
    for (const s of stars) { if (!s.alive) continue; const d = Math.hypot(s.x - x, s.y - y); if (d < bd) { bd = d; best = s; } }
    if (best) showStar(best);
  });
  const lp = $("#lifep"); const showP = () => { lifeP = Math.pow(10, Number(lp.value)); $("#lifep-v").textContent = fmtP(lifeP); };
  lp.addEventListener("input", showP); showP();
  $("#search").addEventListener("click", search);
  $("#reveal").addEventListener("click", reveal);
  const src = $("#sources"); for (const k in SOURCES) src.append(el("li", null, SOURCES[k]));
  requestAnimationFrame(loop);
});
