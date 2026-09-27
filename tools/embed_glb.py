"""Generate the single-file viewer from tracked source and a GLB.

    python tools/embed_glb.py --glb out/cell_anim.glb --page out/cuve400.html

The model is embedded; Three.js and fonts still require an internet connection.
Only Python's standard library is needed.
"""

from __future__ import annotations

import argparse
import base64
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'const b64 = "'


def generate(glb: Path, template: Path, page: Path) -> None:
    data = glb.read_bytes()
    if len(data) < 12 or struct.unpack_from('<4sII', data) != (b'glTF', 2, len(data)):
        raise ValueError(f"Not a valid glTF 2.0 binary header: {glb}")
    lines = template.read_text(encoding="utf-8").splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.lstrip().startswith(PREFIX)]
    if len(hits) != 1:
        raise ValueError(f"Expected exactly one {PREFIX!r} line in {template}; found {len(hits)}")
    if page.resolve() in (template.resolve(), glb.resolve()):
        raise ValueError("The output page must not overwrite its template or model")
    payload = base64.b64encode(data).decode("ascii")
    lines[hits[0]] = f'{PREFIX}{payload}";\n'
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--glb", type=Path, default=ROOT / "out/cell_anim.glb")
    parser.add_argument("--template", type=Path, default=ROOT / "viewer/index.html")
    parser.add_argument("--page", type=Path, default=ROOT / "out/cuve400.html")
    args = parser.parse_args()
    generate(args.glb, args.template, args.page)
    print(f"Generated {args.page} ({args.page.stat().st_size / 1048576:.2f} MiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
