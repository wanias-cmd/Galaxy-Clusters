/* Odyssey sound engine: every sound is generated with the Web Audio API (no audio files needed).
   The build script injects this into the hub and every module, then calls SFX.init('<module>'). */
(function(){
const W=window,P=W.parent||W,$=i=>document.getElementById(i);let ac,out,held=0,nb;
function ctx(){if(ac)return ac;try{ac=new(W.AudioContext||W.webkitAudioContext)();out=ac.createGain();out.gain.value=.5;out.connect(ac.destination)}catch(e){}return ac}
const run=()=>ctx()&&ac.state=='running',unlock=()=>{ctx();if(ac&&ac.state=='suspended')ac.resume()};
function apply(){if(out)out.gain.setTargetAtTime((P.__muted||held)?0:.5,ac.currentTime,.1)}
function tone(f,d,ty,v,t0,f2){if(!run())return;const t=ac.currentTime+(t0||0),o=ac.createOscillator(),g=ac.createGain();o.type=ty||'sine';o.frequency.setValueAtTime(f,t);if(f2)o.frequency.exponentialRampToValueAtTime(f2,t+d);g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(v||.1,t+.01);g.gain.exponentialRampToValueAtTime(.0001,t+d);o.connect(g).connect(out);o.start(t);o.stop(t+d+.05)}
function buf(){if(nb)return nb;nb=ac.createBuffer(1,ac.sampleRate*2,ac.sampleRate);const d=nb.getChannelData(0);for(let i=0;i<d.length;i++)d[i]=Math.random()*2-1;return nb}
function noise(d,v,f,ty){if(!run())return;const t=ac.currentTime,s=ac.createBufferSource(),fl=ac.createBiquadFilter(),g=ac.createGain();s.buffer=buf();fl.type=ty||'lowpass';fl.frequency.value=f||800;g.gain.setValueAtTime(v||.2,t);g.gain.exponentialRampToValueAtTime(.0001,t+d);s.connect(fl).connect(g).connect(out);s.start(t);s.stop(t+d)}
function bed(f,ty,v){const s=ac.createBufferSource(),fl=ac.createBiquadFilter(),g=ac.createGain();s.buffer=buf();s.loop=true;fl.type=ty||'lowpass';fl.frequency.value=f;g.gain.value=v;s.connect(fl).connect(g).connect(out);s.start();return{g,fl}}
function osc(f,ty,v){const o=ac.createOscillator(),g=ac.createGain();o.type=ty||'sine';o.frequency.value=f;g.gain.value=v;o.connect(g).connect(out);o.start();return{o,g}}
function lfo(p,r,d){const o=ac.createOscillator(),g=ac.createGain();o.frequency.value=r;g.gain.value=d;o.connect(g).connect(p);o.start()}
function pad(fs,ty,v){fs.forEach(f=>{const x=osc(f,ty||'sine',v);lfo(x.g.gain,.08+Math.random()*.12,v*.6)})}
function steps(v,cond){const d={};addEventListener('keydown',e=>d[e.code]=1);addEventListener('keyup',e=>d[e.code]=0);setInterval(()=>{if(['KeyW','KeyA','KeyS','KeyD','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].some(k=>d[k])&&(!cond||cond())){noise(.08,v,260);tone(78,.12,'sine',v*.7)}},430)}
function watch(id,cb){const e=$(id);if(e)new MutationObserver(cb).observe(e,{attributes:true,childList:true,subtree:true})}
const arp=(fs,ty,v)=>fs.forEach((f,i)=>tone(f,.5,ty||'triangle',v||.08,i*.12));
const K={
hub(){pad([110,164.8,220.5],'sine',.025);setInterval(()=>tone(1200+Math.random()*1200,.7,'sine',.012),4000)},
mars(){const w=bed(380,'lowpass',.1);lfo(w.g.gain,.15,.04);steps(.22);
setInterval(()=>{const n=($('wn')||{}).textContent||'';w.g.gain.setTargetAtTime(/Moon/.test(n)?0:/Mars/.test(n)?.05:.14,ac.currentTime,.3)},500);
addEventListener('keydown',e=>{if(e.code=='Space')tone(180,.3,'sine',.08,0,420);if(/Digit[123]/.test(e.code))tone(440,.15,'triangle',.06,0,660)})},
earth(){const a=osc(55,'sine',.05);osc(110.5,'triangle',.018);setInterval(()=>tone(1500+Math.random()*1500,.9,'sine',.01),3500);
setInterval(()=>{const s=$('s');if(s)a.o.frequency.setTargetAtTime(80-30*s.value/100,ac.currentTime,.3)},250)},
blackhole(){const a=osc(45,'triangle',.08);osc(90,'sine',.03);const n=bed(160,'lowpass',.06);lfo(n.g.gain,.3,.03);
setInterval(()=>{const m=$('m');if(m)a.o.frequency.setTargetAtTime(70-8*m.value,ac.currentTime,.3)},250);
addEventListener('pointerdown',e=>{if(e.target.id=='c')tone(420,.45,'sine',.08,0,70)})},
cosmic(){pad([110,165,220,277],'sine',.02)},
stars(){const w=bed(300,'lowpass',.03);lfo(w.g.gain,.12,.015);steps(.12,()=>!/Stand/.test(($('hint')||{}).textContent||''));
setInterval(()=>{if(Math.random()<.7)[0,.09,.18].forEach(t=>tone(4200+Math.random()*250,.05,'sine',.012,t))},650);
watch('cd',()=>{if($('cd').style.display=='block'){tone(880,.6,'sine',.07);tone(1320,.8,'sine',.04,.08)}})},
builder(){pad([98,147,196],'sine',.02);let ok=0,bad=0;
watch('res',()=>{const r=$('res');if(r.style.display=='none'){ok=bad=0;return}if(/APPROVED/.test(r.textContent)){if(!ok){ok=1;arp([523,659,784,1047])}}else if(/rejected/.test(r.textContent)&&!bad){bad=1;tone(150,.6,'sawtooth',.07,0,80)}})},
landing(){const e=bed(500,'lowpass',0),r=osc(70,'sawtooth',0);let th=0;
addEventListener('keydown',k=>{if(/KeyW|ArrowUp|Space/.test(k.code))th=1});addEventListener('keyup',k=>{if(/KeyW|ArrowUp|Space/.test(k.code))th=0});
const b=$('bt');if(b){b.addEventListener('pointerdown',()=>th=1);b.addEventListener('pointerup',()=>th=0);b.addEventListener('pointercancel',()=>th=0)}
setInterval(()=>{e.g.gain.setTargetAtTime(th?.3:0,ac.currentTime,.05);r.g.gain.setTargetAtTime(th?.05:0,ac.currentTime,.05)},50);
watch('eo',()=>{if($('eo').classList.contains('off'))return;if(/CRASH/.test(($('et')||{}).textContent||'')){noise(1,.5,600);tone(70,.9,'sawtooth',.15,0,30)}else{noise(.2,.3,300);arp([523,659,784],'triangle',.07)}})},
pilot(){}};
W.SFX={init(key){ctx();const pos=key=='hub'?'right:12px;bottom:12px':key=='pilot'?'left:12px;top:156px':'left:104px;top:12px';
const b=document.createElement('button');b.id='sfxb';b.setAttribute('aria-label','Toggle sound');b.style.cssText='position:fixed;z-index:70;width:38px;height:38px;border-radius:50%;border:1px solid #27407a;background:rgba(6,11,28,.85);color:#e6eeff;font-size:17px;cursor:pointer;'+pos;
const paint=()=>b.textContent=P.__muted?'\uD83D\uDD07':'\uD83D\uDD0A';b.onclick=()=>{P.__muted=!P.__muted;paint();apply();if(!P.__muted)tone(660,.1,'sine',.08)};paint();document.body.appendChild(b);
addEventListener('pointerdown',e=>{unlock();const t=e.target;if(t.closest&&t.closest('button,a,.chip,.btn,.card')&&t.id!='sfxb'){tone(660,.07,'square',.035);tone(990,.06,'sine',.03,.04)}},true);addEventListener('keydown',unlock,true);
let lt=0;addEventListener('input',e=>{const r=e.target;if(r.type=='range'){const n=performance.now();if(n-lt<70)return;lt=n;tone(260+(r.value-r.min)/(r.max-r.min||1)*520,.06,'triangle',.035)}},true);
addEventListener('pagehide',()=>{try{ac&&ac.close()}catch(e){}});setInterval(apply,300);if(ctx()&&K[key])K[key]()},
hold(v){held=v;apply()},tone,noise};
})();