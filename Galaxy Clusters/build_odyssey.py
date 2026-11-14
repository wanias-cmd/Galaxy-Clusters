#!/usr/bin/env python3
"""Merge the Odyssey hub + 7 modules + common.css + Earth textures into ONE file: odyssey.html"""
import base64, json, pathlib, re, sys, urllib.request

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
rd = lambda p: (root / p).read_text(encoding='utf-8')
fix = lambda s: '<' + s.lstrip() if s.lstrip().startswith('!DOCTYPE') else s

ORDER = ['mars', 'earth', 'blackhole', 'cosmic', 'builder', 'landing', 'pilot']
css = rd('common.css')

SHIM = """<script>
document.addEventListener('click',function(e){var a=e.target.closest('a[href="#hub"]');if(a){e.preventDefault();parent.postMessage({odyssey:'hub'},'*')}},true);
addEventListener('load',function(){if(document.getElementById('hud'))return;var b=document.createElement('button');b.textContent='Next mission \\u2192';
b.style.cssText='position:fixed;left:12px;bottom:12px;z-index:25;padding:8px 14px;border:1px solid #4fd8ff;border-radius:8px;background:rgba(6,11,28,.85);color:#e6eeff;font:600 14px system-ui,sans-serif;cursor:pointer';
b.onclick=function(){parent.postMessage({odyssey:'next'},'*')};document.body.appendChild(b)});
</script>"""

# Earth textures: downloaded once into textures/, then embedded as data URIs
TEXDIR = root / 'textures'
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
    h = fix(rd(f'{k}.html'))
    h = re.sub(r'<link[^>]+href=["\'](?:\.\./assets/|\.\./)?common\.css["\'][^>]*>', '<style>' + css + '</style>', h)
    h = h.replace('../index.html', '#hub').replace('index.html', '#hub')
    if k == 'pilot':
        exitbtn = '<a class="btn" href="#hub" style="position:fixed;left:12px;top:118px;z-index:40;padding:6px 14px;font-size:13px;text-decoration:none;color:inherit;background:rgba(5,10,22,.8)">EXIT</a><div id="rot">'
        fuelmsg = "st.fuel=Math.max(0,st.fuel);if(st.fuel<=0&&msgT<=0)msg('OUT OF FUEL - press EXIT to leave','#ff5d6c');"
        for a, b in [('<div id="rot">', exitbtn), ('st.fuel=Math.max(0,st.fuel);', fuelmsg)]:
            if a not in h:
                sys.exit('Pilot module: could not find ' + a)
            h = h.replace(a, b, 1)
    if k == 'earth':
        h, n1 = re.subn(r"const B='[^']*',", 'const TEX=' + json.dumps(TEX) + ',', h)
        h = re.sub(r"B\+'([^']+)'", r"TEX['\1']", h).replace('L.load(B+n)', 'L.load(TEX[n])')
        if not n1:
            sys.exit('Earth module: texture line not found - was earth.html edited?')
    h = h.replace('</body>', SHIM + '</body>')
    mods[k] = h

LOADER = """<div id="mod" style="position:fixed;inset:0;z-index:100;display:none;background:#02040b"><iframe id="mf" allow="fullscreen; autoplay" style="width:100%;height:100%;border:0"></iframe></div>
<script>
const MODS=__MODS__,ORDER=__ORDER__;let curMod=null;
window.launchMod=function(k){curMod=k;try{const i=M.findIndex(m=>FILE[m.id]==k);if(i>=0){seen.add(i);prog()}}catch(e){}
document.getElementById('mf').srcdoc=MODS[k];document.getElementById('mod').style.display='block'};
function closeMod(){document.getElementById('mod').style.display='none';document.getElementById('mf').srcdoc='<body style="background:#02040b"></body>';
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

NEWCSS = ".a-builder{background:linear-gradient(#050914,#101a3a)}.a-builder::before{content:'';position:absolute;left:50%;top:50%;width:calc(110px + var(--v)*70px);height:30px;margin:-15px 0 0 calc((110px + var(--v)*70px)/-2);background:repeating-linear-gradient(90deg,#2a64d8 0 18px,#8fb4ff 18px 20px);transition:.25s}.a-builder::after{content:'';position:absolute;left:50%;top:50%;width:44px;height:58px;margin:-29px;border-radius:4px;background:#d5dcec;box-shadow:0 -14px 0 -10px #ffb454}.a-landing{background:linear-gradient(#000,#1b1b22 72%,#6d6d78 73%)}.a-landing::before{content:'';position:absolute;left:50%;bottom:calc(30px + var(--v)*60px);width:22px;height:30px;margin-left:-11px;background:#e8ecf6;clip-path:polygon(50% 0,100% 100%,0 100%);transition:bottom .25s}.a-landing::after{content:'';position:absolute;left:calc(50% - 22px);bottom:26px;width:44px;height:5px;background:#d8dbe4}</style>"
NEWM = "M.push({id:'builder',n:'Spacecraft Builder',t:'Team engineering',lv:'Intermediate',d:'Design a spacecraft with solar panels, batteries, antennas and instruments. Work as a team of up to 4 engineers.',learn:['How mass, power and cost trade off','Why every part needs power and cooling','How teams decide together'],ctl:[['+ / −','Add or remove parts'],['Role chips','Pick your engineer role'],['Launch vote','Team decides to launch']],demo:{l:'Solar panels',a:0,b:10,s:1,v:2,f:v=>'Panels make <b>'+v*60+' W</b>. A basic spacecraft needs about 110 W.',art:v=>v/10}},{id:'landing',n:'Rocket Landing',t:'2D flight game',lv:'Intermediate',d:'Land a rocket safely on the Moon, Mars or Earth. Learn why timing the braking burn matters.',learn:['Why landing speed matters (kinetic energy)','How gravity and air change a landing','What stopping distance means'],ctl:[['W / Space','Fire engine'],['A D / arrows','Tilt ship'],['1 · 2 · 3','Moon, Mars, Earth']],demo:{l:'Touchdown speed (m/s)',a:0,b:30,s:1,v:5,f:v=>'A 1-tonne lander carries <b>'+(0.5*v*v).toFixed(0)+' kJ</b> on impact '+(v<5?'(safe landing)':'(crash)'),art:v=>1-v/30}});const FILE={builder:'builder',landing:'landing',"
for a, b in [('</style>', NEWCSS), ('const FILE={', NEWM), ("seen.size*20+'%'", "seen.size*100/M.length+'%'"), ("' / 5'+(seen.size==5", "' / '+M.length+(seen.size==M.length"), ('Explore all 5', 'Explore all 7')]:
    if a not in hub:
        sys.exit('Hub: could not find ' + a)
    hub = hub.replace(a, b, 1)
hub = hub.replace('</body>', LOADER + '</body>')

out = root / 'odyssey.html'
out.write_text(hub, encoding='utf-8')
print('Built', out, f'({out.stat().st_size // 1024} KB)')
