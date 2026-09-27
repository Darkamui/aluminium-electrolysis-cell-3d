"""Regression checks for producing usable distributions from a fresh checkout."""

import base64
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import zipfile

from tools.embed_glb import generate
from tools.package_release import FILES, package


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.glb = self.root / "model.glb"
        chunk = b'{"asset":{"version":"2.0"}} '
        chunk += b' ' * (-len(chunk) % 4)
        self.data = struct.pack('<4sIIII', b'glTF', 2, 20 + len(chunk), len(chunk), 0x4E4F534A) + chunk
        self.glb.write_bytes(self.data)
        self.template = self.root / "template.html"
        self.template.write_text('<title>Cell</title>\nconst b64 = "";\n', encoding="utf-8")

    def test_fresh_output_embeds_exact_model_and_preserves_template(self):
        page = self.root / "fresh/output.html"
        generate(self.glb, self.template, page)
        payload = page.read_text(encoding="utf-8").split('const b64 = "')[1].split('"')[0]
        self.assertEqual(base64.b64decode(payload), self.data)
        self.assertIn('const b64 = "";', self.template.read_text(encoding="utf-8"))

    def test_invalid_model_does_not_replace_existing_page(self):
        page = self.root / "output.html"
        page.write_text("previous page", encoding="utf-8")
        self.glb.write_bytes(b"not a GLB")
        with self.assertRaises(ValueError):
            generate(self.glb, self.template, page)
        self.assertEqual(page.read_text(encoding="utf-8"), "previous page")

    def test_missing_or_ambiguous_slot_is_rejected(self):
        for template in ('<title>No slot</title>', 'const b64 = "";\nconst b64 = "";'):
            self.template.write_text(template, encoding="utf-8")
            with self.assertRaises(ValueError):
                generate(self.glb, self.template, self.root / "output.html")

    def test_template_cannot_be_overwritten(self):
        with self.assertRaises(ValueError):
            generate(self.glb, self.template, self.template)

    def test_package_has_models_license_and_matching_checksums(self):
        for relative in FILES.values():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(relative.encode())
        archive, manifest = package(self.root, self.root / "release", "v1.0.0")
        original = archive.read_bytes()
        with zipfile.ZipFile(archive) as bundle:
            self.assertEqual(set(bundle.namelist()), set(FILES))
            self.assertIsNone(bundle.testzip())
            for line in manifest.read_text(encoding="utf-8").splitlines():
                expected, name = line.split("  ")
                actual = original if name == archive.name else bundle.read(name)
                self.assertEqual(hashlib.sha256(actual).hexdigest(), expected)
        package(self.root, self.root / "release", "v1.0.0")
        self.assertEqual(archive.read_bytes(), original)

    def test_incomplete_build_and_unsafe_version_are_rejected(self):
        with self.assertRaises(FileNotFoundError):
            package(self.root, self.root / "release", "v1.0.0")
        with self.assertRaises(ValueError):
            package(self.root, self.root / "release", "../elsewhere")


if __name__ == "__main__":
    unittest.main()
