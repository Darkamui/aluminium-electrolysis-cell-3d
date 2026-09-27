# Contributing

Read `AGENTS.md` and the design history before changing model structure.
Dimensions belong in `spec.py`; modules consume them and own one collection
each. Preserve object names, shared meshes and the assembled datum.

## Validation

Run the fast, dependency-free checks with Python 3.11 or later:

```sh
python spec.py
python -m unittest discover -s tests -v
```

For changes to geometry, materials, rigs or Blender exports, also run:

```sh
blender --background --python-exit-code 1 --python qa/validate.py
```

There is no `--qa` option on `build_all.py`. GitHub Actions runs the Python
checks; it does not replace the Blender QA run. For low-level helper changes,
`tools/lib_test.py` provides an additional Blender exercise including a render.

## Release a model package

Build the master and both exports using the README commands, then run:

```sh
python tools/embed_glb.py
python tools/package_release.py --version v1.0.0
```

The packager writes a model ZIP and SHA-256 checksum file under `out/releases/`.
It includes the original license and reuse documentation. Attach both files to
a GitHub release at the matching source tag. Rendered videos can be attached
separately. Do not commit generated models, embedded viewer output, videos or
dependency directories to Git.

Inspect the exported models and viewer before publishing. A release should
record the Blender version, the QA result and any known fidelity limitations.
