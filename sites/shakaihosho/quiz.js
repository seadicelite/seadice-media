(function(){'use strict';
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
})();