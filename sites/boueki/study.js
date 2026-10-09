(function(){'use strict';
var KEY='study:'+(document.documentElement.getAttribute('data-site')||'x'),S=null,OK=true;
function load(){if(S)return S;try{S=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){S={};OK=false}S.read=S.read||{};S.miss=S.miss||{};S.cards=S.cards||{};S.best=S.best||{};return S}
function save(){try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){OK=false}}
function $(s,r){return(r||document).querySelectorAll(s)}
function esc(t){var d=document.createElement('i');d.textContent=t;return d.innerHTML}
function today(){return Math.floor((Date.now()-new Date().getTimezoneOffset()*6e4)/864e5)}
load();
/* 学んだ日（レッスンを読み終えた・問題を解いた日）と連続日数 */
function studied(){var t=today(),st=S.st||{d:0,n:0};if(st.d!==t){st.n=st.d===t-1?st.n+1:1;st.d=t}S.st=st}
/* 章末テスト・模擬試験のベストスコア（ページ単位。PARTが分かれていても合算） */
var TP=$('.quiz[data-mode="test"] .qz'),TN=TP.length,TA=0,TO=0;
/* 確認問題 */
function setupQuiz(z,onAnswer){var qs=$('.qz',z),n=0,ok=0,miss={};
qs.forEach(function(q){var bs=$('button',q),a=+q.dataset.a;bs.forEach(function(b,i){b.addEventListener('click',function(){if(q.dataset.done)return;q.dataset.done=1;n++;
var r=q.querySelector('.res'),id=q.dataset.q;if(i===a){ok++;r.textContent='正解です';r.className='res ok';if(id&&S.miss[id]){delete S.miss[id]}}
else{miss[q.dataset.h]=q.dataset.t;r.textContent='惜しい。正解は '+(a+1)+' です。解説を読んでみましょう';r.className='res ng';if(id)S.miss[id]={l:q.dataset.h,t:Date.now()}}
save();bs.forEach(function(x,j){x.disabled=true;if(j===a)x.classList.add('ok');else if(j===i)x.classList.add('ng')});var d=q.querySelector('details');d.open=true;d.querySelector('summary').textContent='解説';
studied();save();if(onAnswer)onAnswer(q,i===a);
if(n===qs.length){var s=z.querySelector('.score');if(s){var k=Object.keys(miss),h=qs.length+'問中'+ok+'問正解。';
if(!k.length)h+='全問正解です。';else if(z.dataset.mode==='test')h+='次のレッスンを読み直すと、迷ったところがはっきりします。<ul>'+k.map(function(u){return '<li><a href="'+u+'">'+miss[u]+'</a></li>'}).join('')+'</ul>';
else if(z.dataset.mode!=='review'&&z.dataset.mode!=='redo')h+='迷った問題は<a href="/review/">復習ページ</a>に自動で入りました。';s.innerHTML=h}
if(z.dataset.l)markRead(z.dataset.l,true)}
if(z.dataset.mode==='test'&&TN){TA++;if(i===a)TO++;if(TA===TN){var kp=location.pathname,b=S.best[kp],nb=!b||TO>b.ok;if(nb){S.best[kp]={ok:TO,n:TN,d:today()};save()}
var s2=z.querySelector('.score');if(s2){var p=document.createElement('p');p.className='best';p.textContent=nb?(b?'ベストスコアを更新しました（前回のベスト '+b.ok+'/'+b.n+'問）':'このテストの記録を残しました。次はこの点数を超えるのが目標です'):'これまでのベスト: '+b.ok+'/'+b.n+'問';s2.appendChild(p)}}}})})})}
/* 進み具合 */
function markRead(id,on){if(on){S.read[id]=today();S.last=id;studied()}else delete S.read[id];save();$('.mark').forEach(function(b){if(b.dataset.l===id)paint(b)})}
function paint(b){var on=!!S.read[b.dataset.l];b.setAttribute('aria-pressed',on?'true':'false');b.textContent=on?'読み終えました（もう一度押すとチェックを外せます）':'このレッスンを読み終えた'}
$('.mark').forEach(function(b){b.hidden=false;paint(b);b.addEventListener('click',function(){markRead(b.dataset.l,!S.read[b.dataset.l])})});
$('.quiz').forEach(function(z){if(z.dataset.mode!=='redo')setupQuiz(z)});
var items=$('li[data-l]'),seen={},order=[];items.forEach(function(li){var id=li.dataset.l;if(S.read[id]&&!li.querySelector('.ck')){var c=document.createElement('span');c.className='ck';c.textContent='読了';li.firstChild.appendChild(c)}
if(!seen[id]){seen[id]=1;order.push(li)}});
$('a[href]').forEach(function(a){var b=S.best[a.getAttribute('href')];if(b&&!a.querySelector('.ck')){var c=document.createElement('span');c.className='ck';c.textContent='ベスト '+b.ok+'/'+b.n;a.appendChild(c)}});
var rs=$('.resume');if(rs.length&&order.length){var done=order.filter(function(li){return S.read[li.dataset.l]}).length,mk=Object.keys(S.miss).length,at=0;
order.forEach(function(li,i){if(li.dataset.l===S.last)at=i+1});var nx=null;for(var i=0;i<order.length&&!nx;i++){var li=order[(at+i)%order.length];if(!S.read[li.dataset.l])nx=li}
if(done||mk||S.st)rs.forEach(function(r){var h='<p>'+order.length+'レッスン中 '+done+'レッスンを読みました。</p>';
if(S.st){var g=today()-S.st.d,dt=new Date(S.st.d*864e5),ds=(dt.getUTCMonth()+1)+'月'+dt.getUTCDate()+'日';
h+='<p class="streak">'+(g===0?'今日も学びました。連続 '+S.st.n+'日です。':g===1?'最後に学んだ日: '+ds+'（連続 '+S.st.n+'日）。今日も1レッスン進めると '+(S.st.n+1)+'日連続です。':'最後に学んだ日: '+ds+'（'+g+'日前）。今日の1レッスンから、また始めましょう。')+'</p>'}
h+='<div class="btns">';
if(nx)h+='<a class="btn" href="'+nx.querySelector('a').getAttribute('href')+'">続きから読む: '+esc(nx.dataset.s)+'</a>';
if(mk)h+='<a class="btn sub" href="/review/">間違えた問題を解き直す（'+mk+'問）</a>';if(location.pathname!=='/me/')h+='<a class="btn sub" href="/me/">わたしの学習を見る</a>';r.innerHTML=h+'</div>';r.hidden=false})}
/* トップの章の地図 */
$('ol.map li[data-ls]').forEach(function(r){var ls=r.dataset.ls.split(' '),n=ls.filter(function(id){return S.read[id]}).length;if(n){r.querySelector('.mp-n').textContent=n+'/'+ls.length;if(n===ls.length)r.classList.add('done')}});
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
})();