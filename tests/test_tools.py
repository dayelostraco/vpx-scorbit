"""Developer tooling tests use tiny fixtures, never live tables or helper binaries."""

import hashlib
import json
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from tools import build_common_pilot, package_helpers, stage_mm
from tools.audit_maps import audit
from tools.generate_rom_adapter import generate

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    "Sub Table1_Init\n    InitializeROM\nEnd Sub\n"
    "Sub Table1_exit\nEnd Sub\n"
    "Sub Table1_OptionEvent(ByVal eventId)\nEnd Sub\n"
)


class ToolTests(unittest.TestCase):
    def test_legacy_stage_rejects_script_literal_in_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, extraction = self.fixture(root)
            argv = [
                "stage_mm",
                "--extraction",
                str(extraction),
                "--output",
                str(root / "output"),
                "--runtime",
                str(root / 'bad"path'),
                "--vpxtool",
                "vpxtool.exe",
            ]
            with patch.object(stage_mm, "__file__", str(repo / "tools/stage_mm.py")), patch.object(sys, "argv", argv):
                with self.assertRaisesRegex(ValueError, "cannot be embedded"):
                    stage_mm.main()
            self.assertFalse((root / "output").exists())

    def test_packager_allowlist_hash_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "helper.exe").write_bytes(b"inert fixture, never executed")
            (root / "sToken.dat").write_text("private fixture must stay out")
            lock = {
                "helpers": [
                    {"name": "helper.exe", "sha256": hashlib.sha256((root / "helper.exe").read_bytes()).hexdigest()}
                ]
            }
            lockfile = root / "lock.json"
            lockfile.write_text(json.dumps(lock))
            output = root / "bundle.zip"
            self.assertEqual(package_helpers.build(root, output, lockfile), ["helper.exe"])
            with ZipFile(output) as archive:
                self.assertEqual(set(archive.namelist()), {"Tables/helper.exe", "helpers.lock.json", "README.txt"})
            with self.assertRaises(FileExistsError):
                package_helpers.build(root, output, lockfile)
            (root / "helper.exe").write_bytes(b"changed")
            with self.assertRaises(ValueError):
                package_helpers.build(root, root / "bad.zip", lockfile)
            self.assertFalse((root / "bad.zip").exists())
            for name in ("../sToken.dat", "sub/file.exe", "sub\\file.exe"):
                lock["helpers"][0]["name"] = name
                lockfile.write_text(json.dumps(lock))
                with self.assertRaises(ValueError):
                    package_helpers.build(root, root / "bad.zip", lockfile)

    def fixture(self, root):
        repo = root / "repo"
        (repo / "profiles").mkdir(parents=True)
        (repo / "profiles/medieval-madness.json").write_text(
            json.dumps({"rom": "mm_109b", "script_sha256": hashlib.sha256(SCRIPT.encode()).hexdigest()})
        )
        for folder, files in [
            ("vbs", build_common_pilot.MODULES),
            ("maps", ["mm_109.map.json"]),
            ("assets", ["telemetry.vbs"]),
        ]:
            (repo / folder).mkdir()
            for name in files:
                (repo / folder / name).write_bytes((ROOT / folder / name).read_bytes())
        extraction = root / "input"
        (extraction / "gameitems").mkdir(parents=True)
        (extraction / "script.vbs").write_bytes(SCRIPT.encode())
        (extraction / "gameitems.json").write_text("[]")
        return repo, extraction

    def test_common_builder_isolation_and_preflight(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, extraction = self.fixture(root)
            output = root / "output"
            qr = root / "qr.png"
            qr.write_bytes(b"path-only fixture")
            with (
                patch.object(build_common_pilot, "ROOT", repo),
                patch.object(build_common_pilot.subprocess, "run") as assemble,
            ):
                manifest = build_common_pilot.build(extraction, output, Path("vpxtool.exe"), qr)
                self.assertFalse(manifest["network_enabled"])
                self.assertEqual((extraction / "script.vbs").read_text(), SCRIPT)
                self.assertIn("Const SB_NETWORK_ENABLED = False", (output / "script.vbs").read_text())
                self.assertEqual(len(json.loads((output / "gameitems.json").read_text())), 1)
                assemble.assert_called_once_with(["vpxtool.exe", "assemble", str(output)], check=True)
                with self.assertRaises(FileExistsError):
                    build_common_pilot.build(extraction, output, Path("vpxtool.exe"))
                (extraction / "gameitems.json").write_text('[{"file_name":"Flasher.SBQRPanel.json"}]')
                with self.assertRaises(ValueError):
                    build_common_pilot.build(extraction, root / "duplicate", Path("vpxtool.exe"))
                self.assertFalse((root / "duplicate").exists())
                (extraction / "script.vbs").write_text("unknown revision")
                with self.assertRaises(ValueError):
                    build_common_pilot.build(extraction, root / "unknown", Path("vpxtool.exe"))

    def test_legacy_stage_is_offline_and_isolated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo, extraction = self.fixture(root)
            # main resolves its repo from __file__; keep the actual source testable.
            argv = [
                "stage_mm",
                "--extraction",
                str(extraction),
                "--output",
                str(root / "output"),
                "--runtime",
                str(root / "runtime"),
                "--vpxtool",
                "vpxtool.exe",
            ]
            with (
                patch.object(stage_mm, "__file__", str(repo / "tools/stage_mm.py")),
                patch.object(sys, "argv", argv),
                patch.object(stage_mm.subprocess, "run") as assemble,
            ):
                stage_mm.main()
                assemble.assert_called_once()
                self.assertEqual((extraction / "script.vbs").read_text(), SCRIPT)
                with self.assertRaises(ValueError):
                    stage_mm.main()
                (extraction / "script.vbs").write_text("unknown")
                with self.assertRaises(ValueError):
                    stage_mm.main()

    def test_map_supported_and_rejected_semantics(self):
        original = json.loads((ROOT / "maps/mm_109.map.json").read_text())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.json").write_text(
                json.dumps({"_note": "Generated index metadata", "mm_109b": "map.json", "missing": "missing.json"})
            )
            (root / "map.json").write_text(json.dumps(original))
            rows = audit(root)
            self.assertEqual(sum(r["decoder"].startswith("supported") for r in rows), 1)
            self.assertEqual(len(rows), 2)
            self.assertEqual(next(r for r in rows if r["rom"] == "missing")["reason"], "Map file missing")
        for change in ("platform", "scores", "encoding", "bounds", "extra"):
            mapping = json.loads(json.dumps(original))
            if change == "platform":
                mapping["_metadata"]["platform"] = "unknown"
            elif change == "scores":
                mapping["game_state"]["scores"] = []
            else:
                field = mapping["game_state"]["game_over"]
                field[{"encoding": "encoding", "bounds": "start", "extra": "scale"}[change]] = {
                    "encoding": "unknown",
                    "bounds": 99999,
                    "extra": 2,
                }[change]
            with self.assertRaises(ValueError):
                generate(mapping, "mm_109b")

    def test_cli_generation_audit_and_patch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "index.json").write_text('{"mm_109b":"map.json"}')
            (root / "map.json").write_bytes((ROOT / "maps/mm_109.map.json").read_bytes())
            legacy = root / "legacy.vbs"
            legacy.write_bytes(
                b"Class ScorbitIF\r\nPrivate LOGFILE(10000000)\r\n\t\t\tLOGFILE(LogIdx)=data\r\nEnd Class"
            )
            for module, args in [
                (
                    "tools.generate_rom_adapter",
                    ["--map", str(root / "map.json"), "--rom", "mm_109b", "--output", str(root / "adapter.vbs")],
                ),
                ("tools.audit_maps", ["--maps-root", str(root), "--output", str(root / "audit.json")]),
                ("tools.patch_legacy_log", [str(legacy), str(root / "patched.vbs")]),
            ]:
                with patch.object(sys, "argv", [module, *args]):
                    runpy.run_path(str(ROOT / (module.replace(".", "/") + ".py")), run_name="__main__")
            self.assertIn("ReDim Preserve", (root / "patched.vbs").read_text())
