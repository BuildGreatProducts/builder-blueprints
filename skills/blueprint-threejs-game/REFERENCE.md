# Three.js Game — Reference

> Last verified: 2026-10. three.js changes every month, and its WebGPU and TSL APIs still move between releases. Before writing code, run `npm view three version` and use the docs and examples for that release: https://threejs.org/docs, https://threejs.org/examples (always the latest release), or Context7 if available. For Blender, check https://docs.blender.org/api/current/bpy.ops.export_scene.html.

## Contents
1. Default approach
2. Versions checked
3. Project layout
4. Renderer setup (WebGPU)
5. The game loop
6. Input
7. Game state, entities and UI
8. Physics
9. Audio
10. Loading and disposing assets
11. Blender → web pipeline
12. Optimising assets with glTF Transform
13. AI-generated models and asset packs
14. Driving Blender with an MCP server
15. Performance budgets and techniques
16. Mobile and robustness
17. Building and hosting
18. The React Three Fiber path
19. Patterns to avoid

---

## 1. Default approach

- **Plain three.js + TypeScript + Vite.** You own the loop, so a fixed timestep is easy, there are fewer layers between the agent and the bug, and WebGPU and TSL work without waiting for a wrapper to catch up. Use React Three Fiber only for React teams or UI-heavy games (section 18).
- **`WebGPURenderer`**, imported from `three/webgpu`. It uses WebGPU where the browser supports it and falls back to WebGL 2 automatically. The three.js manual still describes it as maturing rather than finished, so test on every target device. If a feature you need is missing, try `forceWebGL: true` before switching renderers.
- **TSL for shaders.** `ShaderMaterial`, `RawShaderMaterial`, `onBeforeCompile` and `EffectComposer` don't work with `WebGPURenderer`. Write custom shading as node materials in TSL (`three/tsl`) and post-processing with `RenderPipeline`.
- **Rapier for physics**, a fixed 60 Hz simulation step, an input action map, and a simple state machine for menu / play / pause / game-over.
- **One asset pipeline for everything:** Blender (or AI, or a pack) → `export_glb.py` → glTF Transform (Meshopt + KTX2) → `GLTFLoader`.
- **ES modules only.** Import from `three`, `three/webgpu`, `three/tsl` and `three/addons/...`. Don't use `require()`.

## 2. Versions checked

Checked on npm and official sites in October 2026. Use these as a sanity check, not a pin: always run `npm view <package> version`.

| Thing | Version seen | Notes |
|---|---|---|
| three / @types/three | 0.186.x (r186) | `Clock` deprecated in r183 (use `Timer`); `PostProcessing` renamed `RenderPipeline` in r183; `PCFSoftShadowMap` removed in r186 |
| vite | 8.x | |
| @dimforge/rapier3d-compat | 0.21.x | Also `-deterministic-compat` and `-simd-compat` variants |
| jolt-physics | 1.1.x | |
| cannon-es | 0.20.x | No release since 2022; tiny projects only |
| @react-three/fiber | 9.8.x (v10 is alpha) | v9 needs React 19 |
| @react-three/drei / @react-three/rapier | 10.7.x / 2.2.x | |
| koota / bitecs | 0.6.x / 0.4.x | |
| howler / zustand / stats-gl | 2.2.x / 5.x / 4.2.x | |
| @gltf-transform/cli | 4.5.x | KTX2 needs KTX-Software 4.4.0+ (`ktx` on PATH) |
| Blender | 5.2 LTS (5.2.2) | glTF export parameter names checked against 5.0, 5.2 and main |
| Blender Lab MCP server | needs Blender 5.1+ | |

## 3. Project layout

```
my-game/
├── art/                    # .blend source files (not shipped)
├── assets-raw/             # straight Blender exports (gitignored, rebuilt by script)
├── public/
│   └── basis/              # KTX2 transcoder, copied from three/examples/jsm/libs/basis/
├── src/
│   ├── main.ts             # renderer, loop, state machine
│   ├── core/               # loop.ts, input.ts, audio.ts, assets.ts, quality.ts
│   ├── game/               # player.ts, enemies.ts, level.ts, rules.ts
│   ├── ui/                 # HTML/CSS overlay: menus, HUD
│   └── models/             # optimised .glb files, imported with ?url so Vite hashes them
├── tools/
│   ├── export_glb.py       # copied from this skill
│   └── build-assets.sh
├── docs/game-brief.md
├── CREDITS.md
└── vite.config.ts          # base: './' so the build works inside itch.io's iframe
```

## 4. Renderer setup (WebGPU)

```ts
import * as THREE from 'three/webgpu';
import { Inspector } from 'three/addons/inspector/Inspector.js';

const renderer = new THREE.WebGPURenderer({ antialias: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)); // 3x phones cost 2.25x the pixels of 2x
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);
await renderer.init(); // WebGPU starts asynchronously; required before KTX2Loader.detectSupport()

renderer.onDeviceLost = (info) => showFatal(`Graphics reset (${info.message}). Tap to reload.`);
if (import.meta.env.DEV) renderer.inspector = new Inspector(); // built-in inspector, dev only

window.addEventListener('resize', () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});
```

- `onDeviceLost` fires for both a lost WebGPU device and a lost WebGL context on the fallback path.
- **TSL basics:** node materials (`MeshStandardNodeMaterial` and friends) expose slots like `colorNode`, `positionNode` and `emissiveNode`. Build them with functions from `three/tsl` (`uniform`, `texture`, `mix`, `time`, `positionWorld`…). Look up current names in the TSL docs and the `webgpu_*` examples for your release; don't write them from memory.
- **Shadows:** default `PCFShadowMap` is fine. One shadow-casting directional light, with its shadow camera fitted tightly around the play area.

## 5. The game loop

Fixed-timestep simulation with render interpolation, driven by `renderer.setAnimationLoop` (which also waits for the renderer to be ready).

```ts
const STEP = 1 / 60;          // simulation rate: 60 Hz, independent of screen refresh rate
const MAX_STEPS = 5;          // cap catch-up so a long frame can't snowball ("spiral of death")
const timer = new THREE.Timer();
timer.connect(document);      // ignores time spent in a hidden tab
let accumulator = 0;

renderer.setAnimationLoop((time) => {
  timer.update(time);
  accumulator += Math.min(timer.getDelta(), 0.25);
  let steps = 0;
  while (accumulator >= STEP && steps < MAX_STEPS) {
    game.storePreviousTransforms();
    input.update();                 // sample devices once per step
    if (state.current === 'playing') game.fixedUpdate(STEP); // gameplay + physics
    accumulator -= STEP;
    steps++;
  }
  if (steps === MAX_STEPS) accumulator = 0;
  game.interpolate(accumulator / STEP); // lerp/slerp meshes between previous and current state
  stats?.update();
  renderer.render(scene, camera);
});
```

- Gameplay and physics only change state in `fixedUpdate`. Rendering only reads it. This makes the game behave the same at 30, 60 and 120 fps, and keeps multiplayer possible later.
- Never allocate in the loop (`new Vector3()` per frame). Reuse scratch objects.

## 6. Input

Map devices to **actions**, and have gameplay read only actions:

```ts
type Action = 'moveX' | 'moveY' | 'jump' | 'fire' | 'pause';
const bindings = {
  keyboard: { KeyA: ['moveX', -1], KeyD: ['moveX', 1], KeyW: ['moveY', 1], KeyS: ['moveY', -1], Space: ['jump', 1], Escape: ['pause', 1] },
  gamepad:  { axes: { 0: 'moveX', 1: 'moveY' }, buttons: { 0: 'jump', 7: 'fire', 9: 'pause' } },
};
// input.value('moveX') → -1..1, input.pressed('jump') → true only on the step it went down
```

- **Keyboard:** use `event.code` (layout-independent), not `event.key`. Clear held keys on `blur`.
- **Mouse look:** Pointer Lock (`canvas.requestPointerLock()`) must be requested from a click. Handle `pointerlockchange` to pause when the user presses Esc.
- **Gamepad:** poll `navigator.getGamepads()` every step; there are no button events. Apply a dead zone (about 0.15).
- **Touch:** virtual stick on the left half, buttons on the right, built with Pointer Events. Set `touch-action: none` on the canvas.
- Let players rebind keys if the game is keyboard-heavy. Store bindings in `localStorage`.

## 7. Game state, entities and UI

- **State machine:** `boot → menu → playing ⇄ paused → gameOver → menu`. Each state has `enter`, `exit` and `update`. Pause stops `fixedUpdate` but keeps rendering.
- **Entities:** plain classes (`Player`, `Enemy`, `Pickup`) are fine for a vertical slice. If entity counts or combinations grow, move to an ECS: **koota** (pmndrs) by default, **bitECS** when raw performance with thousands of entities matters.
- **UI:** an HTML/CSS overlay above the canvas, not 3D text. Keep UI state in **zustand** (`createStore` from `zustand/vanilla`). Write to the store when values change (score, health), not every frame.
- **Saves:** `localStorage` with a version number in the saved object, so you can migrate old saves.

## 8. Physics

**Rapier** (`@dimforge/rapier3d-compat`) by default. The WASM is inlined, so it works in Vite with no plugins:

```ts
import RAPIER from '@dimforge/rapier3d-compat';
await RAPIER.init();
const world = new RAPIER.World({ x: 0, y: -9.81, z: 0 });
world.timestep = STEP;                   // match the loop
const controller = world.createCharacterController(0.01); // kinematic character controller
// in fixedUpdate: controller.computeColliderMovement(collider, desired); then world.step();
```

- Use the kinematic character controller for the player (slopes, steps, snapping to the ground) rather than pushing a dynamic body around.
- Build colliders from simple shapes: boxes, capsules, convex hulls. Use `COL_` meshes from Blender (section 11) for level geometry; avoid trimesh colliders on moving objects.
- Need identical results across machines (replays, lockstep)? Use `@dimforge/rapier3d-deterministic-compat`.
- **Jolt** (`jolt-physics`) is the alternative for very large scenes or soft bodies. You must free objects yourself (`Jolt.destroy(obj)`), or memory leaks.
- **cannon-es** only for tiny projects that need a few bouncing boxes.

## 9. Audio

- **Howler.js** for music and sound effects. It unlocks audio on the first touch or click automatically; start music only after the player presses "Play". Provide WebM/Opus plus an MP3 fallback, and use audio sprites for many short effects.
- **`THREE.PositionalAudio`** (with an `AudioListener` on the camera) for sounds that must come from a place in the world. Call `listener.context.resume()` from the first user gesture.
- Separate volume sliders for music and effects, plus mute. Remember the setting.
- Pause all audio on `visibilitychange` when the page is hidden.

## 10. Loading and disposing assets

```ts
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import heroUrl from './models/hero.glb?url'; // Vite gives it a hashed filename

const manager = new THREE.LoadingManager();
manager.onProgress = (_url, loaded, total) => ui.setProgress(loaded / total);
const ktx2 = new KTX2Loader(manager)
  .setTranscoderPath(`${import.meta.env.BASE_URL}basis/`)
  .detectSupport(renderer);                 // after await renderer.init()
const gltfLoader = new GLTFLoader(manager).setKTX2Loader(ktx2).setMeshoptDecoder(MeshoptDecoder);
```

- **Asset manager:** one place that loads by URL, caches, reports progress to the loading screen, and clones. Use `SkeletonUtils.clone()` (`three/addons/utils/SkeletonUtils.js`) for skinned characters; a plain `clone()` breaks the skeleton.
- **Dispose on scene change:** traverse the old scene and call `dispose()` on every geometry, material and texture, then check `renderer.info` shows the counts going back down.
- **Animation:** one `AnimationMixer` per character; `THREE.AnimationClip.findByName(gltf.animations, 'Run')`; blend with `crossFadeTo`. Update mixers in the render step with the real delta, or in `fixedUpdate` with `STEP`, but not both.

## 11. Blender → web pipeline

### Before you model
- Scene units: Metric, unit scale 1.0. **1 Blender unit = 1 metre.** A person is about 1.8 m tall, a door about 2 m.
- Model the front facing **−Y** in Blender. After export (+Y up) it faces +Z in three.js, which is what `lookAt` expects.
- Put the **origin at the intended pivot**: feet for characters, hinge for doors, base centre for props (Object › Set Origin).
- **Apply transforms** before rigging and export: select, Ctrl+A › All Transforms. Unapplied scale is the top cause of wrong sizes and misaligned colliders.

### Materials and textures
- **Principled BSDF only**, with Image Texture nodes plugged in directly (Base Color, Metallic, Roughness, Normal via a Normal Map node, Emission, Alpha). The exporter understands little else.
- **Bake procedural materials** (noise, gradients, complex node trees) to image textures before export (Cycles › Bake). Procedural nodes don't export.
- Textures: square powers of two. **1024 by default, 2048 maximum**, and only for hero assets on desktop. Share one material and texture atlas across many props to cut draw calls. For flat low-poly art, vertex colours or a small palette texture beat many materials.

### Naming conventions
| Name | Means | Used by |
|---|---|---|
| `COL_<name>` | Invisible collision mesh: a box, capsule or convex shape | Code builds Rapier colliders from it, then hides it |
| `<name>_LOD0`, `<name>_LOD1`… | Detail levels, 0 = full detail | Code builds a `THREE.LOD` |
| `SPAWN_<name>`, `SOCKET_<name>` | Empties marking spawn points or attachment points (e.g. `SOCKET_hand_R`) | Code reads their positions |
| `Idle`, `Walk`, `Run`, `Jump`, `Attack` | Action names | Become clip names in three.js |

Custom properties on objects (e.g. `collider: "trigger"`) export as glTF extras and appear in `object.userData`.

### Animation
- One armature per character. One **action per clip**, named clearly. Make loops seamless (first frame = last frame) and keep movement **in place**: code moves the character, the animation shouldn't.
- In the Action Editor, **Push Down** each action onto the NLA (or give it a fake user) so it's saved and exported.
- Export with animation mode **Actions** (the default): every active action and every action on an NLA track becomes its own glTF animation, named after the action.

### Export
Manual: File › Export › glTF 2.0 › Format **glTF Binary (.glb)**, Transform **+Y Up**, Mesh **Apply Modifiers**, Animation mode **Actions**. Note that applying modifiers drops shape keys.

Scripted (repeatable and CI-friendly): copy `export_glb.py` from this skill into `tools/`, then:

```sh
blender -b art/hero.blend --python-exit-code 1 --python tools/export_glb.py -- --out assets-raw/hero.glb
# options: --selection-only, --no-animations, --no-apply (keeps shape keys)
```

On macOS, `blender` is `/Applications/Blender.app/Contents/MacOS/Blender` unless you've added it to your PATH. The script warns about unapplied scale and shape keys and exits non-zero on failure.

`tools/build-assets.sh`, run after any `.blend` changes:

```sh
#!/usr/bin/env bash
set -euo pipefail
for f in art/*.blend; do
  name=$(basename "$f" .blend)
  blender -b "$f" --python-exit-code 1 --python tools/export_glb.py -- --out "assets-raw/$name.glb"
  npx @gltf-transform/cli optimize "assets-raw/$name.glb" "src/models/$name.glb" \
    --compress meshopt --texture-compress ktx2 --texture-size 1024 --join false --flatten false
done
```

## 12. Optimising assets with glTF Transform

```sh
npx @gltf-transform/cli optimize in.glb out.glb --compress meshopt --texture-compress ktx2
```

- `--compress meshopt` (the default) compresses geometry **and** animation and decodes faster than Draco. Prefer it to Draco.
- `--texture-compress ktx2` converts textures to KTX2/Basis, which stay compressed in GPU memory. It automatically uses **UASTC** for normal, occlusion and metal-rough maps and **ETC1S** for colour. It needs **KTX-Software** installed with `ktx` on your PATH (from github.com/KhronosGroup/KTX-Software/releases; check with `ktx --version`). If you can't install it, use `--texture-compress webp`: smaller downloads, but full size in GPU memory.
- `--texture-size 1024` caps texture size (default 2048).
- `optimize` also **joins and flattens** meshes by default, which merges named nodes. For anything your code looks up by name (`COL_`, `SOCKET_`, LODs, characters), add `--join false --flatten false`.
- **Inspect before and after:** `npx @gltf-transform/cli inspect out.glb` lists meshes, triangle counts, textures and sizes. `validate` checks the file against the glTF spec.
- **LODs:** `npx @gltf-transform/cli simplify in.glb lod1.glb --ratio 0.5 --error 0.01`, or a Decimate modifier in Blender for more control. Load them into a `THREE.LOD`.
- Copy `node_modules/three/examples/jsm/libs/basis/` into `public/basis/` so `KTX2Loader` can find its transcoder.

## 13. AI-generated models and asset packs

**Generators:** Meshy (good all-rounder, auto-rigging), Tripo (fast), Rodin by Hyper3D (most detail), Hunyuan3D by Tencent (open weights, can run locally). Check each tool's licence for your plan before using output commercially.

**Always clean up AI output in Blender before it enters the pipeline:**
1. Import, then fix scale to real-world metres, face −Y, set the origin, and apply transforms.
2. Reduce triangles to budget (Decimate modifier, or retopology for hero characters). Raw output is often far too dense.
3. Check the UVs and normals. Rebake textures into one 1024 (or 2048 for heroes) atlas on a Principled BSDF, removing baked-in lighting if you can.
4. Rig or check the auto-rig, then name actions and push them to the NLA.
5. Export with `export_glb.py` and optimise, like every other asset.

**Free packs (CC0, credit anyway):** Kenney (game-ready props, characters, UI, audio), Quaternius (low-poly animated characters and nature), Poly Haven (photo-real textures, HDRIs and models). Pack models still go through `optimize`. Record every source in `CREDITS.md`.

## 14. Driving Blender with an MCP server

An MCP server lets the coding agent control Blender directly: create objects, run scripts, take viewport screenshots.

- **Recommended: the official Blender Lab MCP server** (projects.blender.org/lab/blender_mcp). It needs Blender 5.1 or later, a Blender add-on, and the server run with `uv`. Blender Lab warns that it executes AI-generated Python inside Blender **without a sandbox**, which could delete files or send data elsewhere. It recommends a virtual machine or a computer with no sensitive data.
- **Alternative: MCP for Blender** (`mcp-for-blender`, formerly `blender-mcp` by ahujasid; community-made, not affiliated with Blender). Set `BLENDER_MCP_SAFE_MODE=1` so scripts that touch files, the network or other programs are blocked before they run.

**Safety rules for either:**
- Save and back up the `.blend` file first, and work on a copy.
- Ask the agent to show any script that deletes, writes files outside the project, or uses the network before running it, and read it.
- Keep secrets and personal files off the machine or VM running Blender.
- Disconnect the server when you're done.
- Everything made this way still goes through `export_glb.py` and `optimize`.

## 15. Performance budgets and techniques

| Per frame | Mobile | Desktop |
|---|---|---|
| Draw calls | about 100 | a few hundred |
| Triangles | 100k–300k | 1M+ is usually fine |
| Texture size | 1024 | 2048 max |
| Shadow map | 512–1024 | 2048 |

| Per asset | Triangles |
|---|---|
| Hero character | 10k–30k |
| Props | 0.5k–5k |

- **Measure:** with `WebGPURenderer`, read `renderer.info.render.drawCalls` and `renderer.info.render.triangles` (with `WebGLRenderer` it's `info.render.calls`). Show them in a dev overlay with **stats-gl** (`new Stats({ trackGPU: true })`, `stats.init(renderer)`, `stats.update()` each frame), and use the built-in Inspector.
- **`InstancedMesh`** for many copies of the same mesh (trees, coins, bullets). **`BatchedMesh`** for different geometries that share one material. Merge static level geometry.
- Cap pixel ratio at `Math.min(devicePixelRatio, 2)` (1.5 or 1 on the low tier).
- Shadows: one shadow-casting light, a tight shadow camera, small maps on mobile. **Avoid point-light shadows** (each one renders the scene six times). Bake shadows and ambient occlusion into textures for static scenery.
- **Quality tiers:** at least low and high. Change pixel ratio, shadows, post-processing, LOD distances, particle counts. Start mobile on low. Drop a tier automatically if average frame time stays over budget for a few seconds.
- **Dispose** of everything when changing level (section 10), and watch memory in the Inspector.
- Profile on the weakest target device, not your development machine.

## 16. Mobile and robustness

- Touch controls (section 6), a viewport meta tag that blocks pinch-zoom, and `touch-action: none` on the canvas.
- Audio unlock on first tap (Howler does this; resume the three.js `AudioListener` context too).
- Default to the low quality tier, and show a fullscreen button.
- Handle a lost GPU device or WebGL context with `renderer.onDeviceLost`: show a message and offer a reload.
- Pause the game and audio on `visibilitychange` and `blur`.
- Handle resizes and rotation. Respect safe areas (`env(safe-area-inset-*)`) for HUD elements.
- Show a clear message if neither WebGPU nor WebGL 2 is available.

## 17. Building and hosting

- `vite build` outputs `dist/` with hashed filenames in `dist/assets/`. Set `base: './'` in `vite.config.ts` so the build works from any folder (itch.io needs relative paths). Import models with `?url` so they're hashed too; files in `public/` keep their names.
- **Cache headers:** hashed files get `Cache-Control: public, max-age=31536000, immutable`. On Cloudflare Pages, add `public/_headers`:
  ```
  /assets/*
    Cache-Control: public, max-age=31536000, immutable
  ```
- Serve `.wasm` as `application/wasm` (the big static hosts do; check with `curl -I`). Rapier's compat build inlines its WASM, so this mostly matters for the Basis transcoder.
- **COOP/COEP headers only if you use threads** (`SharedArrayBuffer`). They break embeds and third-party scripts otherwise.
- Keep the first download small: show the menu while the level loads. Very large assets go on R2 or another CDN, with CORS enabled.
- **itch.io:** upload a ZIP of the **contents** of `dist/` (`index.html` at the root of the ZIP, not in a folder). Limits: 500 MB extracted, 1,000 files, 200 MB per file, 240-character paths; filenames are case-sensitive. Tick "Mobile friendly" if you support phones, and enable the fullscreen button. Only tick the SharedArrayBuffer option if the build uses threads. HTML5 games on itch.io can take donations, not fixed prices.
- **Own URL:** Cloudflare Pages (recommended), Netlify or Vercel. All serve a static `dist/` for free at this scale.

## 18. The React Three Fiber path

For React teams or UI-heavy games: React Three Fiber v9 (React 19) + drei + `@react-three/rapier`.

- **Mutate in `useFrame`, never `setState` per frame.** Keep refs to objects and change `ref.current.position` directly. React state is for things that change rarely (menus, score).
- `@react-three/rapier`'s `<Physics>` already runs a fixed `1/60` step with interpolation by default.
- WebGPU in v9: pass an async `gl` factory to `<Canvas>` that creates `THREE.WebGPURenderer` from `three/webgpu` and awaits `renderer.init()`, and `extend(THREE)` with the WebGPU build. v10, with first-class WebGPU, is still alpha.
- Use drei's `useGLTF` for loading, and make sure Meshopt and KTX2 are configured.
- Everything else in this file (pipeline, budgets, hosting) still applies.

## 19. Patterns to avoid

- Building art, menus or features before the core loop is playable.
- Writing WebGPU/TSL code from memory or old tutorials. Check the version and the matching examples.
- `ShaderMaterial`, GLSL strings, `onBeforeCompile` or `EffectComposer` with `WebGPURenderer`.
- `THREE.Clock` (deprecated; use `Timer`), `PostProcessing` (now `RenderPipeline`), `PCFSoftShadowMap` (removed).
- Variable-timestep physics (`world.step()` once per rendered frame with whatever delta it got).
- Game logic that reads raw keys instead of actions.
- `setState` or allocations every frame.
- Shipping raw Blender or AI exports: unoptimised, 4K textures, wrong scale, origin in the wrong place.
- Draco when Meshopt would do; uncompressed PNG textures in the final build.
- Loading the same model twice instead of cloning; never calling `dispose()`.
- Point-light shadows, uncapped pixel ratio, or post-processing on phones.
- Absolute paths (`/models/x.glb`) that break on itch.io.
- Assets without a known licence, or no `CREDITS.md`.
- Running AI-generated Blender scripts on your only copy of a file.
- Multiplayer in the first version.
