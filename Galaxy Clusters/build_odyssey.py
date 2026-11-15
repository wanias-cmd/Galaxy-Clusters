#!/usr/bin/env python3
"""Merge the Odyssey hub + 8 modules + common.css + sfx.js + Earth textures into ONE file: odyssey.html"""
import base64, json, pathlib, re, sys, urllib.request

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
rd = lambda p: (root / p).read_text(encoding='utf-8')
fix = lambda s: '<' + s.lstrip() if s.lstrip().startswith('!DOCTYPE') else s

ORDER = ['mars', 'earth', 'blackhole', 'cosmic', 'stars', 'builder', 'landing', 'pilot']
css_path = 'assets/common.css' if (root / 'assets/common.css').exists() else 'common.css'
css = rd(css_path)

sfx_path = root / 'assets' / 'sfx.js' if (root / 'assets' / 'sfx.js').exists() else root / 'sfx.js'
sfx = sfx_path.read_text(encoding='utf-8') if sfx_path.exists() else ''
if not sfx:
    print('Note: sfx.js not found, building without sound')

SHIM = """<script>
document.addEventListener('click',function(e){var a=e.target.closest('a[href="#hub"]');if(a){e.preventDefault();parent.postMessage({odyssey:'hub'},'*')}},true);
addEventListener('load',function(){if(document.getElementById('hud'))return;var b=document.createElement('button');b.textContent='Next mission \\u2192';
b.style.cssText='position:fixed;left:12px;bottom:12px;z-index:25;padding:8px 14px;border:1px solid #4fd8ff;border-radius:8px;background:rgba(6,11,28,.85);color:#e6eeff;font:600 14px system-ui,sans-serif;cursor:pointer';
b.onclick=function(){parent.postMessage({odyssey:'next'},'*')};document.body.appendChild(b)});
</script>"""

TEXDIR = (root / 'assets' / 'textures') if (root / 'assets').exists() else (root / 'textures')
TEXDIR.mkdir(parents=True, exist_ok=True)
BASE = 'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/'
TEX = {}
for n in ['earth_atmos_2048.jpg', 'earth_specular_2048.jpg', 'earth_normal_2048.jpg', 'earth_lights_2048.png', 'earth_clouds_1024.png']:
    f = TEXDIR / n
    if not f.exists():
        print('Downloading', n)
        try:
            f.write_bytes(urllib.request.urlopen(BASE + n, timeout=60).read())
        except Exception as e:
            sys.exit(f'Could not download {n}: {e}\nDownload it from {BASE}{n} and save it in {TEXDIR}')
    TEX[n] = 'data:image/' + ('png' if n.endswith('png') else 'jpeg') + ';base64,' + base64.b64encode(f.read_bytes()).decode()

mods = {}
for k in ORDER:
    mod_path = f'modules/{k}.html' if (root / f'modules/{k}.html').exists() else f'{k}.html'
    h = fix(rd(mod_path))
    h = re.sub(r'<link[^>]+href=["\'](?:\.\./assets/|\.\./)?common\.css["\'][^>]*>', '<style>' + css + '</style>', h)
    h = h.replace('../index.html', '#hub').replace('index.html', '#hub')
    if k == 'mars':
        ASTRO = r"""
let view=1,ph=0,hd=0;
const AS=new THREE.Group(),MT=(c,r,m)=>new THREE.MeshStandardMaterial({color:c,roughness:r==null?.65:r,metalness:m||0}),SU=MT(0xc4c8d0,.7),WH=MT(0xe8eaee,.7),GR=MT(0x6f7480,.5,.3);
const add=(g,m,x,y,z,p)=>{const o=new THREE.Mesh(g,m);o.position.set(x,y,z);o.castShadow=true;(p||AS).add(o);return o},sph=(r,n)=>new THREE.SphereGeometry(r,n||22,16),bx=(w,h,d)=>new THREE.BoxGeometry(w,h,d);
add(sph(.34),SU,0,1.12,0).scale.set(1,1.15,.85);add(sph(.3),SU,0,.86,0).scale.set(1,.7,.9);
add(bx(.22,.2,.07),GR,0,1.42,-.27);add(bx(.36,.16,.07),GR,0,1.25,-.28);
add(bx(.64,.78,.3),WH,0,1.3,.36);add(bx(.12,.5,.2),GR,.36,1.25,.36);add(bx(.12,.5,.2),GR,-.36,1.25,.36);
add(sph(.31,28),WH,0,1.8,0);
add(new THREE.SphereGeometry(.322,28,18,Math.PI*1.12,Math.PI*.76,Math.PI*.27,Math.PI*.46),new THREE.MeshPhongMaterial({color:0x7d8798,specular:0xffffff,shininess:120,side:THREE.DoubleSide}),0,1.8,0);
add(new THREE.TorusGeometry(.215,.022,10,28),GR,0,1.78,-.285);add(new THREE.TorusGeometry(.2,.03,8,24),GR,0,1.5,0).rotation.x=Math.PI/2;
const limb=(x,y)=>{const g=new THREE.Group();g.position.set(x,y,0);add(sph(.125,14),SU,0,0,0,g);add(new THREE.CylinderGeometry(.1,.092,.46,16),SU,0,-.23,0,g);add(sph(.11,14),WH,0,-.5,0,g).scale.set(1,1.1,.9);AS.add(g);return g};
const aL=limb(-.42,1.4),aR=limb(.42,1.4);aL.rotation.z=.28;aR.rotation.z=-.28;
const leg=x=>{const g=new THREE.Group();g.position.set(x,.88,0);add(new THREE.CylinderGeometry(.13,.12,.82,16),SU,0,-.41,0,g);add(sph(.15,16),WH,0,-.8,-.06,g).scale.set(1,.7,1.5);AS.add(g);return g};
const lL=leg(-.16),lR=leg(.16);sc.add(AS);
function astro(dx,dz,dt){const mv=Math.hypot(dx,dz)/Math.max(dt,.001);AS.visible=!!view;if(!view)return;if(mv>.1)hd=Math.atan2(-dx,-dz);AS.rotation.y+=Math.atan2(Math.sin(hd-AS.rotation.y),Math.cos(hd-AS.rotation.y))*Math.min(1,dt*10);
AS.position.set(px,Hh(px,pz)+hy,pz);ph+=mv*dt*(1.4+wd.g*.12);const air=hy>.02,sw=air?0:Math.sin(ph)*Math.min(1,mv/3)*(.9-.04*wd.g);
lL.rotation.x=air?-.45:sw;lR.rotation.x=air?.45:-sw;aL.rotation.x=air?-.9:-.7-sw*.5;aR.rotation.x=air?-.9:-.7+sw*.5}
function tv(){view=1-view;document.getElementById('vw').textContent=view?'View: astronaut (V)':'View: first person (V)'}
document.getElementById('vw').onclick=tv;addEventListener('keydown',e=>{if(e.code=='KeyV')tv()});
build('mars');requestAnimationFrame(loop);"""
        CAM = "if(view){const cx=px+Math.sin(yaw)*5.5,cz=pz+Math.cos(yaw)*5.5;cam.position.set(cx,Math.max(Hh(cx,cz)+1.2,Hh(px,pz)+2.8+hy),cz);cam.rotation.set(pitch-.18,yaw,0)}else{cam.position.set(px,Hh(px,pz)+1.7+hy,pz);cam.rotation.set(pitch,yaw,0)}astro(dx,dz,dt);"
        VIEWBTN = '<div class="panel" style="left:12px;bottom:12px;top:auto;width:auto;max-width:250px"><button class="chip on" id="vw">View: astronaut (V)</button><p class="mu" style="margin:6px 0 0;font-size:12px">Jump on each world and watch how gravity changes your hop and your stride.</p></div><div class="ov" id="ov">'
        for a, b in [("build('mars');requestAnimationFrame(loop);", ASTRO), ('cam.position.set(px,Hh(px,pz)+1.7+hy,pz);cam.rotation.set(pitch,yaw,0);', CAM), ('<div class="ov" id="ov">', VIEWBTN)]:
            if a not in h:
                sys.exit('Mars module: could not find ' + a)
            h = h.replace(a, b, 1)
    if k == 'pilot':
        exitbtn = '<a class="btn" href="#hub" style="position:fixed;left:12px;top:118px;z-index:40;padding:6px 14px;font-size:13px;text-decoration:none;color:inherit;background:rgba(5,10,22,.8)">EXIT</a><div id="rot">'
        fuelmsg = "st.fuel=Math.max(0,st.fuel);if(st.fuel<=0&&msgT<=0)msg('OUT OF FUEL - press EXIT to leave','#ff5d6c');"
        TELE_DIV = '<div id="tele" style="position:absolute;right:calc(12px + env(safe-area-inset-right));top:172px;width:200px;font-size:11px;line-height:1.35;background:rgba(5,10,22,.72);border:1px solid var(--ln);border-radius:6px;padding:6px 10px"><div id="telh" style="pointer-events:auto;cursor:pointer;color:var(--am);font-weight:600;letter-spacing:.1em">MISSION TELEMETRY &#9662;</div><div id="telb"></div></div><div id="dash">'
        TELE_JS = r"""function tele(dM,spd){if((tele.n=(tele.n||0)+1)%6)return;const t=st.t,fl=st.fw>0,kp=fl?6:2+((Math.abs(Math.sin(t/25))*2)|0),cls=fl?'M5.2':'C1.'+(((t|0)*7)%10),f=n=>Math.round(n).toLocaleString('en-US'),
ph=stage==0?'Departure':stage<5?'Cruise':dM<760?'Orbit insertion':'Approach',sd=ship.position.distanceTo(earth.position)*.0334,need=130+(fire?60:0)+(st.sh?220:0),spent=Math.round(100+(100-st.fuel)*1.5+(100-st.hull)*4+t*.3),
R=[['Phase',ph],['Mission time',Math.floor(t*.8)+' days'],['Velocity',spd.toFixed(2)+' km/s'],['Distance to target',f(dM*1e4)+' km'],['Distance travelled',f((st.trav||0)*1e4)+' km'],['Signal delay',sd<60?'&lt; 1 min':Math.round(sd/60)+' min'],['Fuel',Math.round(st.fuel)+'%',st.fuel<25],['Power gen / need','780 / '+need+' W'],['Battery',Math.round(st.pow)+'%',st.pow<25],['Data collected',(t*.05+stage*5).toFixed(1)+' GB'],['Space weather','Kp '+kp+' \u2022 '+cls,fl],['Spent','$'+spent+'M / $600M']];
document.getElementById('telb').innerHTML=R.map(r=>'<div style="display:flex;justify-content:space-between;gap:6px"><span style="color:#8aa0c4">'+r[0]+'</span><b style="color:'+(r[2]?'#ff5d6c':'#dcebff')+'">'+r[1]+'</b></div>').join('')}
document.getElementById('telh').onclick=()=>{const b=document.getElementById('telb');b.style.display=b.style.display=='none'?'':'none'};if(innerHeight<500)document.getElementById('telb').style.display='none';
function hud(dM,spd){tele(dM,spd);"""
        ORION = r"""ship.children.forEach(o=>o.visible=false);
{const m=(c,me,r)=>new THREE.MeshStandardMaterial({color:c,metalness:me||0,roughness:r==null?.5:r}),g=new THREE.Group(),a=(geo,mt,x,y,z,rx)=>{const o=new THREE.Mesh(geo,mt);o.position.set(x,y,z);if(rx)o.rotation.x=rx;g.add(o);return o},SP=new THREE.MeshStandardMaterial({color:0x143a8a,emissive:0x0a2a66,metalness:.8,roughness:.25});
a(new THREE.CylinderGeometry(.9,2.2,2.6,28),m(0xd0d4dc,.4,.45),0,0,-2.6,-Math.PI/2);a(new THREE.CylinderGeometry(2.3,2.3,.25,28),m(0x34343c,.2,.8),0,0,-1.25,Math.PI/2);
a(new THREE.CylinderGeometry(2.1,2.1,3,28),m(0xb9bec9,.6,.4),0,0,.4,Math.PI/2);a(new THREE.CylinderGeometry(.55,.55,.5,16),m(0x888e9a,.6,.4),0,0,-4.1,Math.PI/2);a(new THREE.ConeGeometry(.9,1.2,20),m(0x2b2f3a,.5,.6),0,0,2.5,-Math.PI/2);
[-1,1].forEach(q=>{a(new THREE.BoxGeometry(5.6,.12,1.7),SP,q*5,0,.4);a(new THREE.BoxGeometry(.12,5.6,1.7),SP,0,q*5,.4)});ship.add(g);ex.position.z=5}
"""
        for a, b in [('bub.visible=false;ship.add(bub);sc.add(ship);', 'bub.visible=false;' + ORION + 'ship.add(bub);sc.add(ship);'), ('<div id="rot">', exitbtn), ('st.fuel=Math.max(0,st.fuel);', fuelmsg), ('<div id="dash">', TELE_DIV), ('function hud(dM,spd){', TELE_JS), ('hud(dM,spd)}', 'st.trav=(st.trav||0)+vel.length()*dt;hud(dM,spd)}')]:
            if a not in h:
                sys.exit('Pilot module: could not find ' + a)
            h = h.replace(a, b, 1)
    if k == 'earth':
        h, n1 = re.subn(r"const B='[^']*',", 'const TEX=' + json.dumps(TEX) + ',', h)
        h = re.sub(r"B\+'([^']+)'", r"TEX['\1']", h).replace('L.load(B+n)', 'L.load(TEX[n])')
        if not n1:
            sys.exit('Earth module: texture line not found - was earth.html edited?')
    h = h.replace('</body>', SHIM + (('<script>' + sfx + "SFX.init('" + k + "')</script>") if sfx else '') + '</body>')
    mods[k] = h

LOADER = """<div id="mod" style="position:fixed;inset:0;z-index:100;display:none;background:#02040b"><iframe id="mf" allow="fullscreen; autoplay" style="width:100%;height:100%;border:0"></iframe></div>
<script>
const MODS=__MODS__,ORDER=__ORDER__;let curMod=null;
window.launchMod=function(k){curMod=k;if(window.SFX)SFX.hold(1);try{const i=M.findIndex(m=>FILE[m.id]==k);if(i>=0){seen.add(i);prog()}}catch(e){}
document.getElementById('mf').srcdoc=MODS[k];document.getElementById('mod').style.display='block'};
function closeMod(){if(window.SFX)SFX.hold(0);document.getElementById('mod').style.display='none';document.getElementById('mf').srcdoc='<body style="background:#02040b"></body>';
try{if(document.fullscreenElement)document.exitFullscreen()}catch(e){}curMod=null}
addEventListener('message',function(e){const d=e.data;if(!d||!d.odyssey)return;
if(d.odyssey=='hub')closeMod();
if(d.odyssey=='next'){const n=ORDER[ORDER.indexOf(curMod)+1];n?window.launchMod(n):closeMod()}});
</script>"""
LOADER = LOADER.replace('__MODS__', json.dumps(mods).replace('</', '<\\/')).replace('__ORDER__', json.dumps(ORDER))

hub = fix(rd('index.html'))
hub = re.sub(r'<link[^>]+href=["\'](?:assets/)?common\.css["\'][^>]*>', '<style>' + css + '</style>', hub)

if "location.href='modules/'+FILE[m.id]+'.html'" in hub:
    hub = hub.replace("location.href='modules/'+FILE[m.id]+'.html'", 'window.launchMod(FILE[m.id])')
elif "location.href=FILE[m.id]+'.html'" in hub:
    hub = hub.replace("location.href=FILE[m.id]+'.html'", 'window.launchMod(FILE[m.id])')
else:
    sys.exit('Could not find the hub launch line in index.html - was it edited?')

hub = re.sub(r'\.a-ecl(?![a-z])', '.a-cosmic', hub)
hub = re.sub(r'\.a-pil(?![a-z])', '.a-pilot', hub)

NEWCSS = ".a-builder{background:linear-gradient(#050914,#101a3a)}.a-builder::before{content:'';position:absolute;left:50%;top:50%;width:calc(110px + var(--v)*70px);height:30px;margin:-15px 0 0 calc((110px + var(--v)*70px)/-2);background:repeating-linear-gradient(90deg,#2a64d8 0 18px,#8fb4ff 18px 20px);transition:.25s}.a-builder::after{content:'';position:absolute;left:50%;top:50%;width:44px;height:58px;margin:-29px;border-radius:4px;background:#d5dcec;box-shadow:0 -14px 0 -10px #ffb454}.a-stars{background:radial-gradient(circle at 20% 30%,#fff 0 1.5px,transparent 2px),radial-gradient(circle at 70% 20%,#ffd9a0 0 2px,transparent 3px),radial-gradient(circle at 50% 55%,#fff 0 1px,transparent 2px),radial-gradient(circle at 85% 65%,#9fc4ff 0 2px,transparent 3px),radial-gradient(circle at 30% 75%,#fff 0 1px,transparent 2px),linear-gradient(#02040b,#0b1230 75%,#1a2036)}.a-stars::before{content:'';position:absolute;left:50%;bottom:14px;width:calc(70px + var(--v)*60px);height:14px;margin-left:calc((70px + var(--v)*60px)/-2);background:#7a1624;border:2px solid #e0bd6a;border-radius:2px;transition:.25s}.a-landing{background:linear-gradient(#000,#1b1b22 72%,#6d6d78 73%)}.a-landing::before{content:'';position:absolute;left:50%;bottom:calc(30px + var(--v)*60px);width:22px;height:30px;margin-left:-11px;background:#e8ecf6;clip-path:polygon(50% 0,100% 100%,0 100%);transition:bottom .25s}.a-landing::after{content:'';position:absolute;left:calc(50% - 22px);bottom:26px;width:44px;height:5px;background:#d8dbe4}</style>"
NEWM = "M.push({id:'stars',n:'Stargazing Night',t:'Night sky',lv:'Beginner',d:'Walk to a carpet, lie down and look up at the real night sky. Click any star to learn its name, distance and temperature.',learn:['How to find stars and constellations','Why starlight is old light','How color shows a star\u2019s temperature'],ctl:[['W A S D','Walk'],['E','Lie down / stand up'],['Click a star','See its details']],demo:{l:'Star distance (light-years)',a:4,b:2600,s:1,v:430,f:v=>'You see it as it was in <b>'+(()=>{const y=2026-Math.round(v);return y>0?'the year '+y:(1-y)+' BC'})()+'</b>',art:v=>v/2600}},{id:'builder',n:'Spacecraft Builder',t:'Team engineering',lv:'Intermediate',d:'Design a spacecraft with solar panels, batteries, antennas and instruments. Work as a team of up to 4 engineers.',learn:['How mass, power and cost trade off','Why every part needs power and cooling','How teams decide together'],ctl:[['+ / −','Add or remove parts'],['Role chips','Pick your engineer role'],['Launch vote','Team decides to launch']],demo:{l:'Solar panels',a:0,b:10,s:1,v:2,f:v=>'Panels make <b>'+v*60+' W</b>. A basic spacecraft needs about 110 W.',art:v=>v/10}},{id:'landing',n:'Rocket Landing',t:'2D flight game',lv:'Intermediate',d:'Land a rocket safely on the Moon, Mars or Earth. Learn why timing the braking burn matters.',learn:['Why landing speed matters (kinetic energy)','How gravity and air change a landing','What stopping distance means'],ctl:[['W / Space','Fire engine'],['A D / arrows','Tilt ship'],['1 · 2 · 3','Moon, Mars, Earth']],demo:{l:'Touchdown speed (m/s)',a:0,b:30,s:1,v:5,f:v=>'A 1-tonne lander carries <b>'+(0.5*v*v).toFixed(0)+' kJ</b> on impact '+(v<5?'(safe landing)':'(crash)'),art:v=>1-v/30}});const FILE={stars:'stars',builder:'builder',landing:'landing',"
for a, b in [('</style>', NEWCSS), ('const FILE={', NEWM), ("seen.size*20+'%'", "seen.size*100/M.length+'%'"), ("' / 5'+(seen.size==5", "' / '+M.length+(seen.size==M.length"), ('Explore all 5', 'Explore all 8'),
 ('<button class="btn" id="tb" style="padding:6px 14px">Back</button>', '<button class="btn" id="tx" style="padding:6px 14px">Exit tour</button><button class="btn" id="tb" style="padding:6px 14px">Back</button>'),
 ('<button class="btn" id="tour2">Guided tour</button></div></div>', '<button class="btn" id="tour2">Guided tour</button><button class="btn" id="home">Main menu</button></div></div>'),
 ("$('start').onclick=()=>scr('hub');", "$('start').onclick=()=>scr('hub');$('home').onclick=()=>{touring=0;endTour();scr('splash')};"),
 ('let ti=0;', "let ti=0,touring=0,tourFrom='splash';function exitTour(){if(!touring)return;touring=0;endTour();scr(tourFrom)}"),
 ("function tour(){scr('hub');", "function tour(){tourFrom=$('hub').classList.contains('on')?'hub':'splash';touring=1;scr('hub');"),
 ("$('tb').onclick=()=>{if(ti>0){ti--;step()}};", "$('tb').onclick=()=>{if(ti>0){ti--;step()}else exitTour()};$('tx').onclick=exitTour;"),
 ('return endTour();ti++', 'return exitTour();ti++'),
 ("if(e.key=='Escape'){endTour();", "if(e.key=='Escape'){touring?exitTour():endTour();")]:
    if a not in hub:
        sys.exit('Hub: could not find ' + a)
    hub = hub.replace(a, b, 1)

SPLASH_EARTH = r"""<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
(function(){
  const sp = document.getElementById('splash');
  if (!sp || typeof THREE === 'undefined') return;
  const T = __SPLASH_TEX__;

  const st = document.createElement('style');
  st.textContent = '#splash::before,#splash::after{display:none!important}';
  document.head.appendChild(st);

  const cv = document.createElement('canvas');
  cv.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;z-index:0';
  sp.insertBefore(cv, sp.firstChild);
  Array.from(sp.children).forEach(el => { if (el !== cv) el.style.zIndex = '1'; });

  const ren = new THREE.WebGLRenderer({canvas: cv, antialias: true, alpha: true});
  ren.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
  const sc = new THREE.Scene(), cam = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, 0.1, 100);
  cam.position.z = 4.2;

  const L = new THREE.TextureLoader();
  const earth = new THREE.Mesh(
    new THREE.SphereGeometry(1.35, 64, 48),
    new THREE.MeshPhongMaterial({
      map: L.load(T['earth_atmos_2048.jpg']),
      specularMap: L.load(T['earth_specular_2048.jpg']),
      normalMap: L.load(T['earth_normal_2048.jpg']),
      normalScale: new THREE.Vector2(0.85, 0.85),
      specular: new THREE.Color(0x335577),
      shininess: 22
    })
  );
  earth.rotation.z = 0.41;

  const clouds = new THREE.Mesh(
    new THREE.SphereGeometry(1.375, 64, 48),
    new THREE.MeshPhongMaterial({
      map: L.load(T['earth_clouds_1024.png']),
      transparent: true,
      opacity: 0.85,
      depthWrite: false
    })
  );
  earth.add(clouds);

  const atmo = new THREE.Mesh(
    new THREE.SphereGeometry(1.42, 48, 36),
    new THREE.MeshBasicMaterial({color: 0x4fd8ff, transparent: true, opacity: 0.12, side: THREE.BackSide})
  );
  earth.add(atmo);
  sc.add(earth);

  const sun = new THREE.DirectionalLight(0xffffff, 1.35);
  sun.position.set(-4, 2, 3.5);
  sc.add(sun, new THREE.AmbientLight(0x1b2b4a, 0.55));

  function resize(){
    const w = innerWidth, h = innerHeight;
    ren.setSize(w, h, false);
    cam.aspect = w / h;
    cam.updateProjectionMatrix();
    earth.position.set(w > 760 ? 1.35 : 0, w > 760 ? -0.1 : -1.15, 0);
  }
  addEventListener('resize', resize);
  resize();

  function tick(){
    requestAnimationFrame(tick);
    if (!sp.classList.contains('on')) return;
    earth.rotation.y += 0.0018;
    clouds.rotation.y += 0.0006;
    ren.render(sc, cam);
  }
  tick();
})();
</script>""".replace('__SPLASH_TEX__', json.dumps(TEX))

hub = hub.replace('</body>', SPLASH_EARTH + (('<script>' + sfx + "SFX.init('hub')</script>") if sfx else '') + LOADER + '</body>')

out = root / 'odyssey.html'
out.write_text(hub, encoding='utf-8')
print('Built', out, f'({out.stat().st_size // 1024} KB)')
