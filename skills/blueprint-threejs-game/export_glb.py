"""Export a .blend file to a web-ready .glb, headless and repeatable.

Run it with Blender, not plain Python:

    blender -b path/to/file.blend --python-exit-code 1 --python export_glb.py -- --out assets/raw/model.glb

(`--python-exit-code 1` makes Blender itself exit 1 if Python crashes; the
script also exits 1 on every failure it can detect.)

Options (everything after the lone `--` belongs to this script):
    --out PATH          Where to write the .glb (required). Folders are created if missing.
    --selection-only    Export only the objects that were selected when the file was saved.
    --no-animations     Skip animation export (static props, level geometry).
    --no-apply          Don't apply modifiers. Use this when a mesh has shape keys
                        (morph targets): applying modifiers drops shape keys on export.

What it does by default:
    - glTF Binary (.glb), +Y up, modifiers applied, custom properties kept as extras.
    - Every action that is active or pushed onto an NLA track becomes its own
      named animation clip (Idle, Walk, Run...).
    - No compression here. Compress afterwards with glTF Transform (see REFERENCE.md),
      so there is one place that decides compression and texture formats.

Exit codes: 0 on success, 1 on any failure (bad arguments, not in Blender, export error).
Dependencies: none beyond Blender's bundled Python and its built-in glTF add-on.
"""

import argparse
import os
import sys

USAGE_HINT = (
    "Run this inside Blender: "
    "blender -b file.blend --python export_glb.py -- --out out.glb"
)


def fail(message):
    """Print a clear error and exit non-zero so CI and agents notice."""
    print(f"export_glb: ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def parse_args():
    # Blender passes its own flags on sys.argv. Only the part after a lone `--`
    # is meant for this script.
    if "--" not in sys.argv:
        fail("No script arguments found (missing `--`). " + USAGE_HINT)
    script_args = sys.argv[sys.argv.index("--") + 1:]

    parser = argparse.ArgumentParser(
        prog="export_glb.py",
        description="Export the open .blend file to a web-ready .glb.",
        epilog=USAGE_HINT,
    )
    parser.add_argument("--out", required=True, help="Output .glb path.")
    parser.add_argument(
        "--selection-only",
        action="store_true",
        help="Export only objects selected when the file was saved.",
    )
    parser.add_argument(
        "--no-animations",
        action="store_true",
        help="Do not export animations.",
    )
    parser.add_argument(
        "--no-apply",
        action="store_true",
        help="Do not apply modifiers (keeps shape keys).",
    )
    try:
        return parser.parse_args(script_args)
    except SystemExit as exc:
        # argparse exits with 0 for --help and 2 for bad arguments.
        if exc.code not in (0, None):
            fail("Invalid arguments. " + USAGE_HINT)
        raise


def warn(message):
    print(f"export_glb: WARNING: {message}", file=sys.stderr)


def preflight_checks(bpy, args):
    """Catch the mistakes that most often produce a broken or oversized .glb."""
    objects = list(bpy.context.scene.objects)
    if args.selection_only:
        objects = [o for o in objects if o.select_get()]
        if not objects:
            fail(
                "--selection-only was set but nothing is selected. "
                "Select the objects in Blender, save the file, and run again."
            )

    for obj in objects:
        if obj.type != "MESH":
            continue
        # Unapplied scale is the classic cause of wrong sizes and physics
        # colliders that don't line up in three.js. (Rotation and location are
        # fine on placed objects, so they aren't checked.)
        if any(abs(s - 1.0) > 1e-4 for s in obj.scale):
            warn(
                f"'{obj.name}' has unapplied scale {tuple(round(s, 3) for s in obj.scale)}. "
                "Select it and use Ctrl+A > Scale, unless the scale is animated."
            )
        if obj.data.shape_keys and not args.no_apply:
            warn(
                f"'{obj.name}' has shape keys, which are dropped when modifiers "
                "are applied. Re-run with --no-apply if you need them."
            )


def main():
    try:
        import bpy  # Only available inside Blender.
    except ImportError:
        fail("The `bpy` module isn't available. " + USAGE_HINT)

    args = parse_args()

    out_path = os.path.abspath(args.out)
    if not out_path.lower().endswith(".glb"):
        fail(f"--out must end in .glb (got '{args.out}').")
    if not bpy.data.filepath:
        warn("No .blend file is open; exporting the default scene. " + USAGE_HINT)

    if not hasattr(bpy.ops.export_scene, "gltf"):
        fail(
            "The glTF exporter isn't available. Enable the built-in "
            "'glTF 2.0 format' add-on in Preferences > Add-ons, then save preferences."
        )

    preflight_checks(bpy, args)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Parameter names checked against the Blender Python API reference for
    # bpy.ops.export_scene.gltf. Anything not listed keeps Blender's default.
    export_options = dict(
        filepath=out_path,
        # Single binary file: mesh, textures and animation in one request.
        export_format="GLB",
        use_selection=args.selection_only,
        # glTF and three.js are +Y up; Blender is +Z up. This converts on export.
        export_yup=True,
        # Bake modifiers (Mirror, Subdivision, Decimate...) into the mesh so the
        # web sees what the viewport shows. Armature modifiers are never applied.
        # Caveat: applying modifiers drops shape keys, hence --no-apply.
        export_apply=not args.no_apply,
        # Custom properties become glTF "extras", which three.js puts in
        # object.userData. Handy for game metadata (spawn points, collider type).
        export_extras=True,
        # Lights and cameras are set up in code for games, not in the asset.
        export_cameras=False,
        export_lights=False,
        # Keep textures in their source format (PNG/JPEG/WebP). glTF Transform
        # converts them to KTX2 or WebP later in one consistent step.
        export_image_format="AUTO",
        # Compression happens in glTF Transform, so leave the exporter's off.
        export_draco_mesh_compression_enable=False,
        export_animations=not args.no_animations,
    )

    if not args.no_animations:
        export_options.update(
            # 'ACTIONS' (the exporter's default, set explicitly here) exports the
            # active action plus every action pushed onto an NLA track, each as
            # its own glTF animation named after the action. Name actions
            # Idle, Walk, Run... and those become the clip names in three.js.
            export_animation_mode="ACTIONS",
            # Bake every animated channel at each frame. Avoids interpolation
            # differences between Blender and three.js (e.g. constraints, drivers).
            export_force_sampling=True,
            # Drop keyframes that don't change anything, shrinking the file.
            export_optimize_animation_size=True,
            # Return bones to rest pose between actions so one clip can't leak
            # its pose into the next.
            export_reset_pose_bones=True,
            # Skip control/IK bones that don't deform the mesh: fewer bones,
            # smaller files, faster skinning in the browser.
            export_def_bones=True,
        )

    print(f"export_glb: exporting '{bpy.data.filepath or 'untitled'}' -> {out_path}")
    try:
        result = bpy.ops.export_scene.gltf(**export_options)
    except TypeError as exc:
        # Raised when a keyword isn't recognised (parameter renamed in a newer Blender).
        fail(
            f"Exporter rejected an option: {exc}. Check the parameter names at "
            "https://docs.blender.org/api/current/bpy.ops.export_scene.html"
        )
    except RuntimeError as exc:
        fail(f"Export failed: {exc}")

    if "FINISHED" not in result:
        fail(f"Exporter returned {result} instead of FINISHED.")
    if not os.path.isfile(out_path) or os.path.getsize(out_path) == 0:
        fail(f"Export reported success but {out_path} is missing or empty.")

    size_kb = os.path.getsize(out_path) / 1024
    print(f"export_glb: done, {size_kb:.0f} KB written to {out_path}")
    print("export_glb: next, optimise it with glTF Transform (see REFERENCE.md).")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # Blender exits 0 on an uncaught error; force 1.
        fail(f"Unexpected error: {exc!r}")
