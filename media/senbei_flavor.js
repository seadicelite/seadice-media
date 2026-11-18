var K=Z.K,N=Z.N,L={r:"似た研究あり（水溶液など）",e:"推定",u:"まだわからない"},f=document.getElementById("sbf");if(!f)return;
var LS="senbei-flavor-v1",order=[],cur=null;
function $(i){return document.getElementById(i)}
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
var D=Z.D.map(function(r){var k={};r[2].forEach(function(i){k[K[i]]=1});return{m:Z.M[r[0]],n:Z.Q[r[1][0]]+(r[1][1]?" "+r[1][1]:""),k:k,l:r[3],s:r[4]?Z.P[Z.U[r[4]-1][0]]+Z.U[r[4]-1][1]:"",y:r[5]}});
function find(b,a){var ex=[],nr=[];D.forEach(function(x){for(var i=0;i<a.length;i++)if(!x.k[a[i]])return;(x.k[b]?ex:nr).push(x)});return[ex,nr]}
function tg(k){var o={};Z.T[k].forEach(function(t){o[t]=1});return o}
function judge(x,y){var X=tg(x),Y=tg(y),out=[];Z.R.forEach(function(r){var cs=r[5]?r[5].split(","):[];[[X,Y],[Y,X]].some(function(p){var A=p[0],B=p[1];if(!A[r[0]]||(r[1]!=="*"&&!B[r[1]]))return false;if(cs.indexOf("same")>=0&&r[0]!==r[1])return false;if(cs.indexOf("ni")>=0&&(A.I||B.I))return false;var nb=cs.filter(function(c){return c.indexOf("nb:")===0});if(nb.length&&B[nb[0].slice(3)])return false;out.push([r[2],r[3],r[4],r[6]]);return true})});
out.sort(function(a,b){return"reu".indexOf(a[0])-"reu".indexOf(b[0])});out=out.slice(0,2);return out.length?out:[["u","この2つの組み合わせを、人が味わって調べた研究は見つからなかった",[],""]]}
function pairs(ps){var o=[];for(var i=0;i<ps.length;i++)for(var k=i+1;k<ps.length;k++)o.push([ps[i],ps[k],judge(ps[i],ps[k])]);return o}
function sl(ss){return ss.map(function(s){var v=Z.S[s];return'<a href="'+v[1]+'" target="_blank" rel="noopener">'+esc(v[0])+"</a>"}).join("、")}
function nm(a){return a.map(function(k){return N[k]}).join("＋")}
function host(u){try{return new URL(u).hostname.replace(/^www\./,"")}catch(e){return""}}
function yr(x){return x.y>0?(2000+x.y)+"年の発表":x.y<0?"2026年10月20日に公式の商品ページに掲載":"年不明"}
function list(xs){var seen={},out=[];xs.forEach(function(x){if(out.length<3&&!seen[x.m]){seen[x.m]=1;out.push(x)}});xs.forEach(function(x){if(out.length<3&&out.indexOf(x)<0)out.push(x)});
return'<ul class="exl">'+out.map(function(x){var h=host(x.s);return"<li>"+esc(x.m)+"「"+esc(x.n)+"」"+(x.l?"（限定品）":"")+"<small>"+yr(x)+"。今も売っているかは未確認。出典: "+(x.s?'<a href="'+esc(x.s)+'" target="_blank" rel="noopener">'+esc(h==="prtimes.jp"?"PR TIMES":h)+"</a>":"楽天市場（補助・購入ページのためリンクなし）")+"</small></li>"}).join("")+"</ul>"}
var BH={soy:"醤油を薄く塗り、トースターなどで焦がさないように乾かす",salt:"塩をごく少しふる",sugar:"砂糖を少量の水で溶いて薄く塗り、乾かす（ざらめをのせてもよい）",amakara:"醤油と砂糖（またはみりん）を合わせて薄く塗り、焦がさないように乾かす",miso:"味噌を少しの水やみりんでのばして薄く塗り、焦がさないように乾かす"};
function sel(){var b=f.querySelector('input[name="base"]:checked');return b?b.value:"soy"}
function run(om){var b=sel(),a=order.slice();$("save").disabled=!a.length;$("savedmsg").hidden=true;$("omk").hidden=!om;if(om)$("omk").textContent="おまかせ: 足す味の組み合わせが839件の味名に無く、研究と食い違わないものから選びました。美味しいとは限りません。";
if(!a.length){cur=null;$("rt").textContent="足す味を選んでください";$("r1").innerHTML='<p class="rw">土台と足す味を選ぶと、SEADICEが調べた市販の煎餅・米菓839件の味名に、同じ組み合わせが出てくるかを出します。</p>';$("r2").innerHTML=$("r3").innerHTML='<p class="rw">-</p>';return}
cur={b:b,a:a};$("rt").textContent=N[b]+" ＋ "+nm(a);
var r=find(b,a),ex=r[0],nr=r[1],n=ex.length+nr.length,h,bn='<p class="rw">定番の土台（醤油・塩・砂糖・味噌など）は味名に書かれないことが多く、土台の一致は少なめに数えています。</p>';
if(n){h='<p class="big">調べた839件の味名に、'+esc(nm(a))+(a.length>1?"の組み合わせ":"")+"は"+n+"件出てきた</p>"+'<p class="rw">そのうち味名に「'+esc(N[b])+"」も書かれているもの: "+ex.length+"件。</p>"+bn+'<p class="rw">例（土台も同じものを先に）:</p>'+list(ex.concat(nr))}
else{h='<p class="big">調べた839件の味名には、同じ組み合わせは出てこなかった</p><p class="rw">定番の土台は味名に書かれないことが多く、近い味が出回っている可能性があります。まだない、とは言い切れません。調べた範囲と漏れていそうな所は<a href="#data">調べてわかったこと</a>に書いています（2026年10月20日時点）。</p>';
h+='<p class="rw">'+a.map(function(k){var q=find(k,[k]);return esc(N[k])+"だけなら"+(q[0].length+q[1].length)+"件"}).join("、")+"。</p>"}
$("r1").innerHTML=h;
var pj=pairs([b].concat(a)),neg=false,j="";pj.forEach(function(p){j+='<div class="pj"><p class="pjn">'+esc(N[p[0]])+" × "+esc(N[p[1]])+"</p>"+p[2].map(function(x){if(x[3]==="n")neg=true;return'<p class="rw"><span class="bs b-'+x[0]+'">'+L[x[0]]+"</span>"+esc(x[1])+(x[2].length?"（"+sl(x[2])+"）":"")+"</p>"}).join("")+"</div>"});
var v=Z.V[a.length];if(!(neg&&a.length===1))j+='<div class="pj"><p class="pjn">組み合わせ全体</p><p class="rw"><span class="bs b-'+v[0]+'">'+L[v[0]]+"</span>"+esc(v[1])+(v[2].length?"（"+sl(v[2])+"）":"")+"</p></div>";$("r2").innerHTML=j;
$("r3").innerHTML='<ul class="exl"><li>土台: 素焼きか薄味の煎餅に、'+esc(BH[b])+"</li>"+a.map(function(k){return"<li>"+esc(N[k])+": 例として、"+esc(Z.H[k])+"</li>"}).join("")+'<li>比べ方: 同じ煎餅で、足す前のものと食べ比べる</li></ul><p class="rw">ぬれた物をのせると湿気でしけやすいので、食べる直前に（<a href="/stale-senbei-dry-again/">しけた煎餅は乾かせば戻る？</a>）。あぶるときは焦がしすぎないように（<a href="/senbei-browning-limit/">煎餅の焦げは体に悪い？</a>）。</p>'}
f.addEventListener("change",function(e){var t=e.target;if(t.name==="add"){var i=order.indexOf(t.value);if(t.checked){if(i<0)order.push(t.value);while(order.length>2){var o=order.shift(),el=f.querySelector('input[name="add"][value="'+o+'"]');if(el)el.checked=false}}else if(i>=0)order.splice(i,1)}run()});
function setSel(b,a,om){var r=f.querySelector('input[name="base"][value="'+b+'"]');if(r)r.checked=true;var cs=f.querySelectorAll('input[name="add"]');for(var i=0;i<cs.length;i++)cs[i].checked=a.indexOf(cs[i].value)>=0;order=a.slice();run(om)}
var pool=null;$("omakase").addEventListener("click",function(){if(!pool){pool=[];var bs=K.filter(function(k){return!Z.H[k]}),as=K.filter(function(k){return Z.H[k]});
for(var i=0;i<as.length;i++)for(var k=i+1;k<as.length;k++){var a=[as[i],as[k]],q=find(a[0],a);if(q[0].length+q[1].length)continue;bs.forEach(function(b){if(!pairs([b].concat(a)).some(function(p){return p[2].some(function(x){return x[3]})}))pool.push([b,a])})}}
if(!pool.length)return;var c=pool[Math.floor(Math.random()*pool.length)];setSel(c[0],c[1],true);if(window.innerWidth<960)$("rt").scrollIntoView({behavior:"smooth",block:"start"})});
$("clr").addEventListener("click",function(){setSel(sel(),[])});
function load(){try{var v=JSON.parse(localStorage.getItem(LS)||"[]");return Array.isArray(v)?v:[]}catch(e){return[]}}
function store(v){try{localStorage.setItem(LS,JSON.stringify(v));return true}catch(e){return false}}
var RS={ok:"合った",ng:"合わなかった","":"まだ"};
function draw(){var v=load(),ul=$("myl");$("myempty").hidden=!!v.length;
ul.innerHTML=v.map(function(x,i){var n=(N[x.b]||"")+"＋"+nm(x.a.filter(function(k){return N[k]}));return'<li><p class="myn">'+esc(n)+'</p><p class="myd">入れた日 '+esc(x.d)+" ／ いまの記録: "+RS[x.r||""]+'</p><div class="myb" role="group" aria-label="'+esc(n)+'の記録">'+["ok","ng",""].map(function(r){return'<button type="button" class="bt" data-i="'+i+'" data-r="'+r+'" aria-pressed="'+((x.r||"")===r)+'">'+RS[r]+"</button>"}).join("")+'<button type="button" class="bt del" data-i="'+i+'" data-del="1">消す</button></div></li>'}).join("");
$("myout").value=v.map(function(x){return(N[x.b]||"")+"＋"+nm(x.a.filter(function(k){return N[k]}))+"（"+RS[x.r||""]+"、"+x.d+"）"}).join("\n")}
$("myl").addEventListener("click",function(e){var t=e.target.closest("button");if(!t)return;var v=load(),i=+t.getAttribute("data-i");if(!v[i])return;if(t.getAttribute("data-del"))v.splice(i,1);else v[i].r=t.getAttribute("data-r");store(v);draw()});
$("save").addEventListener("click",function(){if(!cur)return;var v=load(),key=cur.b+":"+cur.a.slice().sort().join(","),m=$("savedmsg");m.hidden=false;
if(v.some(function(x){return x.b+":"+x.a.slice().sort().join(",")===key})){m.textContent="この味は、もう「試したい味」に入っています。";return}
var d=new Date(),ds=d.getFullYear()+"-"+("0"+(d.getMonth()+1)).slice(-2)+"-"+("0"+d.getDate()).slice(-2);v.unshift({b:cur.b,a:cur.a,d:ds,r:""});
m.textContent=store(v)?"「試したい味」に入れました（この端末だけに保存）。":"このブラウザでは保存できませんでした（プライベートモードなど）。";draw()});
draw();run();
