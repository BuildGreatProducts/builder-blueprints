# Three.js Game — Checklist

Audit the real game against every item. **[must]** blocks launch. **[should]** is strongly recommended. Each item says how to verify it. Run the command, read the file, or play the game; never assume a pass.

## Build and project
- [ ] **[must]** `npm run build` succeeds with no TypeScript errors. *Verify: run it.*
- [ ] **[must]** The production build runs from a subfolder: `vite.config.ts` has `base: './'` and no code uses absolute asset paths (`'/models/…'`). *Verify: read the config, `grep -rn "['\"]/\(models\|assets\|audio\|textures\)/" src/`, then `npx vite preview` and play.*
- [ ] **[must]** No errors in the browser console from start screen to game-over. *Verify: play through with the console open.*
- [ ] **[should]** three.js is a recent release and the code uses its current APIs (no `THREE.Clock`, `PostProcessing`, `ShaderMaterial`, `onBeforeCompile` or `EffectComposer` with `WebGPURenderer`). *Verify: `npm view three version` vs `package.json`, and grep for those names.*
- [ ] **[should]** ES module imports only (`three`, `three/webgpu`, `three/tsl`, `three/addons/…`), no `require()`. *Verify: `grep -rn "require(" src/`.*

## Game loop and architecture
- [ ] **[must]** Gameplay and physics run on a fixed timestep with a cap on catch-up steps, driven by `renderer.setAnimationLoop`. *Verify: read the loop.*
- [ ] **[must]** The game plays the same at 30, 60 and 120 fps (jump height, speed, timers). *Verify: throttle the CPU in browser dev tools, or test on a high-refresh screen.*
- [ ] **[must]** The game has menu, playing, paused and game-over states, and can be restarted without reloading the page. *Verify: play through twice.*
- [ ] **[should]** Gameplay reads actions from an input layer, not raw key codes. *Verify: `grep -rn "event.key\|KeyW\|keydown" src/` outside the input module.*
- [ ] **[should]** Rendering interpolates between physics steps (no visible jitter on moving objects). *Verify: read the loop; watch a moving object closely.*
- [ ] **[should]** No allocations in the per-frame path (`new Vector3`, `new Matrix4`, array spreads). *Verify: read `update`/`fixedUpdate` functions.*

## Controls
- [ ] **[must]** Every action in the brief's controls table works on each target input (keyboard and mouse, touch, gamepad). *Verify: play with each.*
- [ ] **[must]** If mobile is a target: on-screen touch controls, no page scroll or pinch-zoom while playing. *Verify: play on a real phone.*
- [ ] **[should]** Pointer Lock (if used) is requested from a click, and pressing Esc pauses. *Verify: play.*
- [ ] **[should]** Held keys are cleared when the window loses focus. *Verify: hold a key, alt-tab, return.*

## Assets and pipeline
- [ ] **[must]** Every model in the build went through `optimize` (Meshopt-compressed, textures KTX2 or WebP). *Verify: `npx @gltf-transform/cli inspect <file>` on each `.glb`; look for `EXT_meshopt_compression` and `KHR_texture_basisu` or `EXT_texture_webp`.*
- [ ] **[must]** The loader is configured for those formats (`setMeshoptDecoder`, `setKTX2Loader` with `detectSupport` after `renderer.init()`), and the Basis transcoder ships with the build. *Verify: read the loader code; check `dist/` for the transcoder files.*
- [ ] **[must]** Models appear at the right size, facing the right way, with their pivot where expected. *Verify: play; compare against a 1.8 m capsule.*
- [ ] **[must]** No texture larger than 2048, and no texture larger than 1024 on mobile-tier assets. *Verify: `inspect` output.*
- [ ] **[should]** Assets are exported by script (`tools/export_glb.py`) and rebuilt by one command. *Verify: run the asset build script.*
- [ ] **[should]** Named nodes the code depends on (`COL_`, `SOCKET_`, `SPAWN_`, LODs) survive optimisation. *Verify: `inspect` the optimised file, or log the names at load.*
- [ ] **[should]** Animations are named clips (Idle, Walk, Run…) and play and blend correctly. *Verify: log `gltf.animations.map(a => a.name)`; play.*
- [ ] **[should]** Hero characters are within 10k–30k triangles and props within 0.5k–5k. *Verify: `inspect`.*

## Performance
- [ ] **[must]** Holds a steady frame rate on the weakest target device during the busiest moment of the game. *Verify: play it there with stats-gl or the Inspector visible.*
- [ ] **[must]** Pixel ratio is capped at 2 or lower. *Verify: grep `setPixelRatio`.*
- [ ] **[should]** Mobile stays within about 100 draw calls and 100k–300k triangles per frame. *Verify: read `renderer.info.render.drawCalls` and `.triangles` in the busiest scene.*
- [ ] **[should]** Repeated objects use `InstancedMesh` or `BatchedMesh`. *Verify: read the level code; check draw calls.*
- [ ] **[should]** No point-light shadows; shadow maps 512–1024 on mobile. *Verify: grep `castShadow` and `shadow.mapSize`.*
- [ ] **[should]** At least two quality tiers, with mobile starting on the low one. *Verify: read the quality module; test on a phone.*
- [ ] **[should]** Geometries, materials and textures are disposed on level change. *Verify: watch `renderer.info.memory` across three restarts; it shouldn't climb.*

## Robustness
- [ ] **[must]** The game pauses (including audio) when the tab is hidden, and resumes cleanly. *Verify: switch tabs mid-game.*
- [ ] **[must]** Audio starts only after a user gesture, and works on iOS Safari if mobile is a target. *Verify: load on a phone, tap Play.*
- [ ] **[should]** A lost GPU device or WebGL context shows a message instead of a frozen screen (`renderer.onDeviceLost`). *Verify: read the handler.*
- [ ] **[should]** Resize and phone rotation keep the right aspect ratio and HUD placement. *Verify: resize the window; rotate a phone.*
- [ ] **[should]** A loading screen shows progress, and the menu appears before the heaviest assets finish. *Verify: throttle the network in dev tools.*
- [ ] **[should]** Music and effects volume and mute exist and are remembered. *Verify: change, reload.*

## Licences and credits
- [ ] **[must]** Every third-party model, texture, sound and font has a licence that allows this use, and AI-generated assets follow the generator's terms for the user's plan. *Verify: read `CREDITS.md` against the asset folders.*
- [ ] **[should]** Credits are visible in the game (menu or end screen) or on the store page. *Verify: play / read the page.*

## Release
- [ ] **[must]** The production ZIP has `index.html` at its root, stays within itch.io's limits (500 MB, 1,000 files, 200 MB per file), and filenames match their references exactly, including case. *Verify: `unzip -l` the ZIP; count files.*
- [ ] **[should]** First load is small: the initial JS bundle plus the assets needed for the menu. *Verify: `ls -lh dist/assets`, and the Network tab on first load.*
- [ ] **[should]** Hashed files get long-lived immutable cache headers on your own host; `.wasm` is served as `application/wasm`; no COOP/COEP headers unless threads are used. *Verify: `curl -I` on a deployed asset.*
- [ ] **[should]** Someone who isn't the developer has played from start to game-over without help. *Verify: ask the user.*
