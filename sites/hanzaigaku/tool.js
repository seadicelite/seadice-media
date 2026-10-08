(function(){'use strict';
var F=document.getElementById('ck');if(!F)return;
var KEY='check:'+(document.documentElement.getAttribute('data-site')||'x')+':'+location.pathname,H=[],OK=true;
try{H=JSON.parse(localStorage.getItem(KEY)||'[]')||[]}catch(e){OK=false;H=[]}
var B=[].slice.call(F.querySelectorAll('input[type=checkbox]')),G=[].slice.call(F.querySelectorAll('.ck-g')),sum=document.getElementById('ck-sum'),hist=document.getElementById('ck-hist');
function today(){return Math.floor((Date.now()-new Date().getTimezoneOffset()*6e4)/864e5)}
function ds(d){var t=new Date(d*864e5);return(t.getUTCMonth()+1)+'月'+t.getUTCDate()+'日'}
function on(){return B.filter(function(b){return b.checked}).map(function(b){return b.name})}
function esc(t){var d=document.createElement('i');d.textContent=t;return d.innerHTML}
function upd(){var c=on();G.forEach(function(g){var bs=g.querySelectorAll('input'),k=0;for(var i=0;i<bs.length;i++)if(bs[i].checked)k++;g.querySelector('.ck-n').textContent=k+' / '+bs.length});
var todo=B.filter(function(b){return!b.checked}).slice(0,3),h='<p class="big">'+B.length+'項目中 '+c.length+'項目できています</p>';
if(todo.length)h+='<p>まだチェックが付いていない項目（上から3つ）:</p><ol>'+todo.map(function(b){return '<li><a href="#c-'+b.name+'">'+esc(b.parentNode.querySelector('b').textContent)+'</a></li>'}).join('')+'</ol>';
else h+='<p>すべてできています。季節の変わり目や引っ越しのときに、もう一度確かめましょう。</p>';sum.innerHTML=h}
function show(msg){if(!H.length&&!msg){hist.hidden=true;return}var h=msg?'<p><b>'+esc(msg)+'</b></p>':'';
if(H.length)h+='<p>これまでの記録（このブラウザだけに保存）</p><ul>'+H.slice(-5).reverse().map(function(r){return '<li>'+ds(r.d)+' ・ '+B.length+'項目中 '+r.c.length+'項目</li>'}).join('')+'</ul>';
hist.innerHTML=h;hist.hidden=false}
if(H.length){var last=H[H.length-1];B.forEach(function(b){b.checked=last.c.indexOf(b.name)>=0})}
B.forEach(function(b){b.addEventListener('change',upd)});
document.getElementById('ck-save').addEventListener('click',function(){var t=today(),c=on(),prev=null;
for(var i=H.length-1;i>=0;i--)if(H[i].d!==t){prev=H[i];break}
if(H.length&&H[H.length-1].d===t)H[H.length-1]={d:t,c:c};else H.push({d:t,c:c});H=H.slice(-30);
try{localStorage.setItem(KEY,JSON.stringify(H))}catch(e){OK=false}
var m=!OK?'このブラウザでは記録を保存できませんでした。印刷して紙で残すこともできます。':prev?('記録しました。前回（'+ds(prev.d)+'）は'+prev.c.length+'項目、今日は'+c.length+'項目です。'+(c.length>prev.c.length?(c.length-prev.c.length)+'項目増えました。':c.length<prev.c.length?'前回より少なくなりました。できなくなったものを見直しましょう。':'')):'記録しました。次に見直したとき、今日と比べられます。';show(m)});
document.getElementById('ck-print').addEventListener('click',function(){window.print()});
sum.hidden=false;document.getElementById('ck-btns').hidden=false;upd();show(H.length?'前回（'+ds(H[H.length-1].d)+'）の記録を読み込みました。':'')})();