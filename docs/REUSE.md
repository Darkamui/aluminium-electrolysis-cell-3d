# Reusing the cell

Download the model package from the repository's latest release. Source archives
alone do not contain the generated `.blend` or `.glb` files.

## Blender

Open `cell.blend` in Blender 5.2.1 or rebuild it using `build_all.py`. The scene
is saved assembled, with live drivers. Append collections from the file if you
want to incorporate the cell into another scene.

Dimensions in `spec.py` are millimetres. Blender geometry uses **metres**, with
one Blender unit equal to one metre. The origin is the centre of the cell in X
and Y; Z = 0 is the top surface of the shell bottom plate. X runs along the
cell, Y across it, and Z points up.

Change dimensions in `spec.py` and rebuild rather than scaling individual
parts. Run both the datasheet self-check and Blender QA after changing geometry.
Repeated components share mesh data: editing a shared mesh changes its instances.

The explosion control is defined in `lib/explode.py`. In scripts, use
`set_explosion()` so Blender's dependency graph is tagged correctly. At value
0 the cell is assembled; at 1 the subsystems are fully separated. The master
file preserves drivers, while the animated GLB contains their baked result.

## glTF / GLB

Import `cell.glb` for a static asset or `cell_anim.glb` for animation. Exports
use metres and glTF's Y-up convention; the exporter converts Blender's Z-up
coordinates. Avoid applying another axis conversion if your importer already
handles glTF.

Object names follow `{NN}_{SUBSYSTEM}_{part}_{index:03d}`. Numeric prefixes map
to the nine model subsystems:

| Prefix | Subsystem |
| --- | --- |
| 01 | Shell |
| 02 | Refractory |
| 03 | Cathode |
| 04 | Process layers |
| 05 | Anodes |
| 06 | Busbars |
| 07 | Superstructure |
| 08 | Hooding |
| 09 | Hardware |

The animated export has one `Scene` clip, linear keys beginning at frame 0,
and 15 animated rig nodes. Driver expressions are not carried by glTF.

For a Three.js slider, initialize and pause an action, then set its own time:

```js
const mixer = new THREE.AnimationMixer(gltf.scene);
const clip = gltf.animations[0];
const action = mixer.clipAction(clip);
action.play();
action.paused = true;

function setExplosion(fraction) {
  action.time = Math.max(0, Math.min(1, fraction)) * clip.duration;
  mixer.update(0);
}
```

Calling `mixer.setTime()` on a paused action does not scrub it. Unpaused repeat
playback can wrap from the final frame to the assembled position.

## Web viewer

Open the generated `cuve400.html`, or serve it as a static page. It embeds the
GLB but loads Three.js and fonts over the internet. The source template has an
empty model slot; generate the usable page with `python tools/embed_glb.py`.
No Node.js project, package installation or story application is required.

## Redistribution

Include `LICENSE` with copies or derivatives of the original model and code.
Attribution linking to this repository is appreciated. If you bundle external
viewer dependencies for offline use, retain their corresponding license files
as described in `THIRD_PARTY_NOTICES.md`.
