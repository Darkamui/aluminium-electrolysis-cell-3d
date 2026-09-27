"""Package generated models, viewer and reuse notices for a GitHub release."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    "cell.blend": "out/cell.blend",
    "cell.glb": "out/cell.glb",
    "cell_anim.glb": "out/cell_anim.glb",
    "cuve400.html": "out/cuve400.html",
    "LICENSE": "LICENSE",
    "THIRD_PARTY_NOTICES.md": "THIRD_PARTY_NOTICES.md",
    "README.md": "docs/REUSE.md",
}


def package(root: Path, destination: Path, version: str) -> tuple[Path, Path]:
    if not re.fullmatch(r"v\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?", version):
        raise ValueError("Use a version such as v1.0.0 or v1.0.0-rc.1")
    missing = [name for name in FILES.values() if not (root / name).is_file()]
    if missing:
        raise FileNotFoundError("Build the release inputs first: " + ", ".join(missing))
    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"aluminium-electrolysis-cell-3d-{version}.zip"
    checksums = []
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for name, relative in FILES.items():
            data = (root / relative).read_bytes()
            # Fixed metadata makes identical inputs produce identical archives.
            entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            bundle.writestr(entry, data)
            checksums.append(f"{hashlib.sha256(data).hexdigest()}  {name}")
    checksums.append(f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}")
    manifest = destination / f"SHA256SUMS-{version}.txt"
    manifest.write_text("\n".join(checksums) + "\n", encoding="utf-8")
    return archive, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--destination", type=Path, default=ROOT / "out/releases")
    args = parser.parse_args()
    archive, manifest = package(ROOT, args.destination, args.version)
    print(f"Packaged {archive} ({archive.stat().st_size / 1048576:.2f} MiB)")
    print(f"Checksums: {manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
