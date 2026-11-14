# Odyssey: Space Explorer Hub

An interactive, browser-based space education game. Players explore seven hands-on missions that teach real physics and engineering: gravity, orbits, black holes, eclipses, spacecraft design, powered landing and interplanetary flight. Everything runs in the browser with no installation and no account.

> **Team:** _add team name_ · **Hackathon:** _add hackathon / challenge name_ · **Live demo:** _add Vercel link_

## The idea

Space science is usually taught from diagrams. Odyssey lets learners touch it: drag a slider and watch gravity, mass or throttle change the picture and the numbers in real time. Each mission has a short "You will learn" list, on-screen controls and live readouts that connect what you see to the underlying physics.

## Missions

| # | Mission | Type | What you learn |
|---|---------|------|----------------|
| 1 | **Walk on Another Planet** | 3D exploration | How gravity changes jumps and stride on the Moon, Mars and Earth. Third-person astronaut or first-person view. |
| 2 | **Earth From Space** | 3D globe | Orbit height vs. speed and period, horizon distance, real satellites (ISS, Hubble, GPS, geostationary). Clouds and city-light layers. |
| 3 | **Black Hole Simulator** | Physics lab | Event horizon, photon sphere, last stable orbit and gravitational lensing. Drop probes, fire light beams. |
| 4 | **Cosmic Event Simulator** | Sky simulator | Solar and lunar eclipses, meteor showers and planetary alignments on a timeline. |
| 5 | **Spacecraft Builder** | Team engineering | Trade-offs between mass, power, heat and cost. Up to 4 players, each with an engineering role. |
| 6 | **Rocket Landing** | 2D flight game | Gravity, drag, fuel, stopping distance and impact energy (½mv²) on three worlds. |
| 7 | **Become a Space Pilot** | 3D flight game | Newtonian motion, fuel and power management, solar flares and a live mission-telemetry panel. |

### Highlights

- **Guided flow:** splash screen, hub with a progress ("Explorer rank") bar, guided tour, and a "Next mission" button that carries players through the modules in order.
- **Spacecraft Builder:** eight components (solar panels, batteries, radiators, cameras, science sensors, antennas, comm systems, fuel tanks), three launch rockets, a $100M budget, and checks for mass, cost, power, eclipse battery, cooling, comms and instruments.
- **Team roles:** Systems Engineer, Payload Engineer, Power & Thermal Engineer, Budget & Ops Manager. Each role can only change its own parts, so the team has to cooperate. Live shared design, team launch vote and a team mission score.
- **AI Mission Advisor:** explains engineering problems in plain language, for example "Your spacecraft is 5 kg over the Small rocket's 150 kg limit. Remove unneeded equipment or choose a larger rocket." It is rule-based, so it works offline.
- **Mission telemetry (Pilot):** phase, mission time, velocity, distance to target and travelled, signal delay, fuel, power generated vs. needed, battery, data collected, space weather and budget spent.

## Controls

| Module | Keyboard / mouse | Touch |
|--------|------------------|-------|
| Walk on Another Planet | W A S D move, Shift run, Space jump, drag to look, 1/2/3 Moon/Mars/Earth, V change view | Left thumb walk, right thumb look, JUMP button |
| Earth From Space | Drag rotate, scroll or slider for altitude | Drag, slider |
| Black Hole Simulator | Mass slider, click space to drop a probe | Tap |
| Cosmic Event Simulator | Event buttons, time slider, Play | Same |
| Spacecraft Builder | + / − buttons, role chips, vote buttons | Same |
| Rocket Landing | W / Space thrust, A D tilt, 1/2/3 world | On-screen buttons |
| Become a Space Pilot | W thrust, S brake, arrows steer, Q/E roll, F shield, C view | Stick and buttons (landscape) |

## Multiplayer (Spacecraft Builder)

1. **Same browser:** open the game in up to 4 tabs. Each tab picks a different role.
2. **Online:** one player presses **Host room** and shares the 4-letter code. Up to 3 others press **Join** and enter it. Rooms use [PeerJS](https://peerjs.com) (WebRTC) through its free public broker, so no server or API key is needed. Very strict networks or firewalls can block WebRTC.

## Run locally

Requirements: Python 3 and a browser. An internet connection is needed the first time (Earth textures and fonts).

```bash
python build_odyssey.py          # merges everything into odyssey.html
python -m http.server 8000       # serve the folder
# open http://localhost:8000/odyssey.html
```

The build script merges the hub and all modules into one self-contained `odyssey.html` and embeds the Earth textures so the globe never depends on a network request.

## Project structure

```
src/
  index.html            hub (splash, mission cards, guided tour, progress)
  modules/
    mars.html           Walk on Another Planet
    earth.html          Earth From Space
    blackhole.html      Black Hole Simulator
    cosmic.html         Cosmic Event Simulator
    builder.html        Spacecraft Builder (multiplayer)
    landing.html        Rocket Landing
    pilot.html          Become a Space Pilot
  assets/common.css     shared look for all modules
build_odyssey.py        merges src/ into one odyssey.html
deploy/index.html       built game (what gets deployed)
```

## Deploy to Vercel

1. Run `python build_odyssey.py`, then copy `odyssey.html` into a `deploy/` folder and rename it `index.html`.
2. Push the repo to GitHub.
3. On vercel.com choose **Add New → Project**, import the repo, set **Root Directory** to `deploy`, framework preset **Other**, leave build command empty, and click **Deploy**.

Or from a terminal: `cd deploy && npx vercel --prod`.

## Tech stack

- Vanilla HTML, CSS and JavaScript (no framework, no build step beyond the merge script)
- Canvas 2D for the black hole, cosmic events, landing and spacecraft drawing
- [three.js r128](https://threejs.org) for the 3D modules (Mars/Moon walk, Earth, Pilot)
- PeerJS for online rooms
- Python 3 build script

## Limitations

- The advisor is rule-based, not a language model.
- Online rooms depend on a free public WebRTC broker.
- Distances, times and costs are scaled for gameplay and are simplified, not mission-accurate.
- Best on a laptop or a phone held sideways. The Builder's panels are tight on small screens.

## AI assistance disclosure

This project was designed and built with the help of an AI assistant (Claude by Anthropic). The prompts used are listed in [`PROMPTS.md`](PROMPTS.md).

## Credits

- Earth textures: three.js examples (`examples/textures/planets`), MIT licence.
- Font: Chakra Petch (Google Fonts, OFL).
- three.js and PeerJS are open-source libraries.

## Licence

_Add your licence (for example MIT)._
