(function(){'use strict';
var L=[].slice.call(document.querySelectorAll('.tl-item')),P=[].slice.call(document.querySelectorAll('.tl-pick a'));if(!L.length)return;
function apply(){var h=decodeURIComponent(location.hash.slice(1)),hit=null;L.forEach(function(s){if(s.id===h)hit=s});
L.forEach(function(s){s.hidden=!!hit&&s!==hit});
P.forEach(function(a){if(hit&&a.getAttribute('href')==='#'+h)a.setAttribute('aria-current','true');else a.removeAttribute('aria-current')});
var all=document.getElementById('tl-all');if(all)all.hidden=!hit;
if(hit){var t=hit.querySelector('h3');hit.scrollIntoView();if(t){t.setAttribute('tabindex','-1');try{t.focus({preventScroll:true})}catch(e){}}}}
window.addEventListener('hashchange',apply);apply()})();