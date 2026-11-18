(function(){'use strict';
var me=document.getElementById('me');if(!me)return;
var site=document.documentElement.getAttribute('data-site')||'x',KEY='study:'+site,S={},OK=true,msg=document.getElementById('me-msg');
try{S=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){OK=false;S={}}
function today(){return Math.floor((Date.now()-new Date().getTimezoneOffset()*6e4)/864e5)}
function $(s){return me.querySelectorAll(s)}
function set(k,v){var e=me.querySelector('[data-v='+k+']');if(e)e.textContent=v}
var t0=today(),read=S.read||{},miss=Object.keys(S.miss||{}).length,cards=S.cards||{},best=S.best||{},ch=(S.qz&&S.qz.ch)||{},all=0,rd=0,nt=null;
document.getElementById('me-nojs').hidden=true;me.hidden=false;
[].forEach.call($('.me-row'),function(r){var ls=r.dataset.ls?r.dataset.ls.split(' '):[],n=0;ls.forEach(function(id){if(read[id])n++});all+=ls.length;rd+=n;
if(ls.length){r.querySelector('.me-bar i').style.width=Math.round(n/ls.length*100)+'%';r.querySelector('.me-n').textContent=ls.length+'レッスン中 '+n+'レッスンを読みました'}
var c=ch[r.dataset.ci];if(c&&c.n)r.querySelector('.me-q').textContent='クイズの正答率 '+Math.round(c.ok/c.n*100)+'%（'+c.n+'問）';
var t=r.dataset.t;if(t&&!best[t]&&ls.length&&n===ls.length&&!nt)nt={h:t,s:r.querySelector('small').textContent}});
var nc=me.dataset.terms|0,ok=0,due=0;Object.keys(cards).forEach(function(k){if(cards[k].b>=3)ok++;if(cards[k].d<=t0)due++});
set('read',rd+' / '+all);set('miss',miss+'問');set('terms',ok+' / '+nc);
var st=S.st,g=st?t0-st.d:9;set('streak',st&&g<=1?st.n+'日':'0日');
if(st){var d=new Date(st.d*864e5);set('last','最後に学んだ日 '+(d.getUTCMonth()+1)+'月'+d.getUTCDate()+'日')}
var h='';if(due)h+='<a class="btn sub" href="/cards/">暗記カード（復習の時期の語 '+due+'語）</a>';else if(!Object.keys(cards).length&&nc)h+='<a class="btn sub" href="/cards/">暗記カードで用語を覚える</a>';
if(nt)h+='<a class="btn sub" href="'+nt.h+'">'+nt.s+'の章末テストに挑戦</a>';
var nx=document.getElementById('me-next');if(h){nx.querySelector('.btns').innerHTML=h;nx.hidden=false}
if(!rd&&!miss&&!st)document.getElementById('me-empty').hidden=false;
function keys(){var out=[];try{for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k===KEY||k.indexOf('check:'+site+':')===0)out.push(k)}}catch(e){}return out}
if(!OK){msg.textContent='このブラウザでは記録を保存できません（プライベートブラウズなど）。通常のウィンドウで開くと、記録が残ります。';[].forEach.call($('.me-io button,.me-io label'),function(b){b.hidden=true})}
document.getElementById('me-out').onclick=function(){var data={};keys().forEach(function(k){data[k]=localStorage.getItem(k)});
if(!Object.keys(data).length){msg.textContent='まだ書き出す記録がありません。';return}
var dt=new Date(),ds=dt.getFullYear()+'-'+('0'+(dt.getMonth()+1)).slice(-2)+'-'+('0'+dt.getDate()).slice(-2),
b=new Blob([JSON.stringify({app:'seadice-study',site:site,v:1,date:ds,data:data})],{type:'application/json'}),a=document.createElement('a');
a.href=URL.createObjectURL(b);a.download=site+'-kiroku-'+ds+'.json';document.body.appendChild(a);a.click();a.remove();setTimeout(function(){URL.revokeObjectURL(a.href)},1e3);
msg.textContent='記録をファイルに書き出しました（'+a.download+'）。移った先の端末で、このページの「記録を読み込む」から選んでください。'};
document.getElementById('me-in').onchange=function(){var f=this.files[0];this.value='';if(!f)return;var fr=new FileReader();
fr.onload=function(){var j;try{j=JSON.parse(fr.result)}catch(e){j=null}
if(!j||j.app!=='seadice-study'||typeof j.data!=='object'){msg.textContent='読み込めませんでした。このページで書き出したファイルを選んでください。';return}
if(j.site!==site){msg.textContent='別の講座の記録です。その講座の「わたしの学習」で読み込んでください。';return}
if(!confirm('今のこの端末の記録を、'+(j.date||'')+' に書き出した記録で置き換えます。よろしいですか？'))return;
try{keys().forEach(function(k){localStorage.removeItem(k)});Object.keys(j.data).forEach(function(k){if(k===KEY||k.indexOf('check:'+site+':')===0)localStorage.setItem(k,String(j.data[k]))});location.reload()}
catch(e){msg.textContent='このブラウザでは記録を保存できませんでした。'}};fr.readAsText(f)};
document.getElementById('me-del').onclick=function(){if(!confirm('この端末の学習の記録をすべて消します。元に戻せません。よろしいですか？'))return;
try{keys().forEach(function(k){localStorage.removeItem(k)})}catch(e){}location.reload()};
})();