#!/usr/bin/env python3
"""Merge the Odyssey hub + 5 modules + common.css + Earth textures into ONE file: odyssey.html"""
import base64, json, pathlib, re, sys, urllib.request

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.')
rd = lambda p: (root / p).read_text(encoding='utf-8')
fix = lambda s: '<' + s.lstrip() if s.lstrip().startswith('!DOCTYPE') else s

ORDER = ['mars', 'earth', 'blackhole', 'cosmic', 'pilot']
css_path = 'assets/common.css' if (root / 'assets/common.css').exists() else 'common.css'
css = rd(css_path)

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

# Hub card art fix
hub = re.sub(r'\.a-ecl(?![a-z])', '.a-cosmic', hub)
hub = re.sub(r'\.a-pil(?![a-z])', '.a-pilot', hub)

if "location.href='modules/'+FILE[m.id]+'.html'" in hub:
    hub = hub.replace("location.href='modules/'+FILE[m.id]+'.html'", 'window.launchMod(FILE[m.id])')
elif "location.href=FILE[m.id]+'.html'" in hub:
    hub = hub.replace("location.href=FILE[m.id]+'.html'", 'window.launchMod(FILE[m.id])')
else:
    sys.exit('Could not find the hub launch line in index.html - was it edited?')

hub = hub.replace('</body>', LOADER + '</body>')

out = root / 'odyssey.html'
out.write_text(hub, encoding='utf-8')
print('Built', out, f'({out.stat().st_size // 1024} KB)')
