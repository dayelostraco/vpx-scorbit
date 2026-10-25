"""Assemble an OFFLINE common-runtime MM pilot; preserve source and live tables.

All player runtime code is embedded VBScript. No Python companion is used.
Production networking cannot be enabled by this diagnostic builder.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.generate_rom_adapter import generate  # noqa: E402 - standalone CLI imports repository code

MODULES = [
    "rom-core.vbs",
    "entry-queue.vbs",
    "json.vbs",
    "http-transport.vbs",
    "helpers.vbs",
    "qr-desktop.vbs",
    "host.vbs",
]


def inject(script):
    """Return script text with exact MM lifecycle hooks; reject ambiguous declarations.

    Init runs after existing initialization; exit/options delegate to the common
    host. Call only after the builder has verified the source script hash.
    """
    # Anchor full declarations, not comments or another routine with similar name.
    init = re.compile(r"(?im)^Sub Table1_Init(?:\(\))?\s*\n")
    matches = list(init.finditer(script))
    if len(matches) != 1:
        raise ValueError("Ambiguous Table1_Init hook")
    end = re.search(r"(?im)^End Sub\s*$", script[matches[0].end() :])
    if not end:
        raise ValueError("Missing init end")
    at = matches[0].end() + end.start()
    script = script[:at] + "    SBCommonStart Table1, SBQRPanel, Controller\n" + script[at:]
    for declaration, call in [
        ("Sub Table1_exit", "SBCommonStop"),
        ("Sub Table1_OptionEvent(ByVal eventId)", "SBCommonOption Table1, eventId"),
    ]:
        pattern = re.compile(r"(?im)^" + re.escape(declaration) + r"\s*\n")
        script, count = pattern.subn(lambda match, call=call: match.group() + "    " + call + "\n", script)
        if count != 1:
            raise ValueError("Ambiguous hook: " + declaration)
    return script


def build(extraction, output, vpxtool, test_qr=None):
    """Build an offline MM pilot in a new directory and return its manifest.

    Inputs are developer-owned Paths; vpxtool is an explicitly trusted local
    executable. Source hashes guard the hooks. Assembly failure propagates and
    may leave diagnostic staging output; it never replaces the live table.
    """
    profile = json.loads((ROOT / "profiles/medieval-madness.json").read_text())
    original = (extraction / "script.vbs").read_bytes()
    if hashlib.sha256(original).hexdigest() != profile["script_sha256"]:
        raise ValueError("Unrecognized effective table script")
    if output.exists() or output.with_suffix(".vpx").exists():
        raise FileExistsError("Use a new staging output")
    script = inject(original.decode("utf-8-sig"))
    filename = "Flasher.SBQRPanel.json"
    index = json.loads((extraction / "gameitems.json").read_text())
    if any(item["file_name"] == filename for item in index):
        raise ValueError("Existing Scorbit panel: refuse duplicate integration")
    qr_path = str(test_qr.resolve(strict=True)) if test_qr else ""
    if any(c in qr_path for c in ['"', "\r", "\n"]):
        raise ValueError("Invalid test image path")
    script += (
        "\n"
        + "\n".join(
            [
                "' Shared runtime 0.1.0-dev; OFFLINE diagnostic build.",
                "Const SB_NETWORK_ENABLED = False",
                'Const SB_ROM = "mm_109b"',
                "Const SB_CATALOG_ID = 0",
                'Const SB_OPDB = ""',
                'Const SB_STATE_NAME = "Scorbit-MM109"',
                f'Const SB_TEST_QR = "{qr_path}"',
                "Function SBSafeClaimWindow(snapshot)",
                "    SBSafeClaimWindow = snapshot.Ball = 1 And Controller.Switch(18) <> 0 And Controller.Switch(11) = 0",
                "End Function",
            ]
        )
        + "\n"
    )
    manifest = {
        "runtime": "0.1.0-dev",
        "network_enabled": False,
        "rom": profile["rom"],
        "source_script_sha256": profile["script_sha256"],
        "modules": {},
        "limitations": [
            "MM gameplay not qualified",
            "VR QR intentionally hidden until validated",
            "catalog identity unresolved",
        ],
    }
    for module in MODULES:
        data = (ROOT / "vbs" / module).read_bytes()
        script += "\n" + data.decode("utf-8")
        manifest["modules"][module] = hashlib.sha256(data).hexdigest()
    script += "\n" + generate(json.loads((ROOT / "maps/mm_109.map.json").read_text()), "mm_109b")
    shutil.copytree(extraction, output)
    (output / "script.vbs").write_text(script, encoding="utf-8")
    panel = {
        "height": 0.0,
        "pos_x": 120.0,
        "pos_y": 375.0,
        "rot_x": 0.0,
        "rot_y": 0.0,
        "rot_z": 0.0,
        "color": "#ffffff",
        "is_timer_enabled": False,
        "timer_interval": 200,
        "name": "SBQRPanel",
        "image_a": "",
        "image_b": "",
        "alpha": 100,
        "modulate_vs_add": 1.0,
        "is_visible": False,
        "add_blend": "none",
        "is_dmd": True,
        "render_mode": None,
        "render_style": 0,
        "display_texture": False,
        "depth_bias": 0.0,
        "image_alignment": "wrap",
        "filter": "none",
        "filter_amount": 100,
        "light_map": "",
        "backglass": True,
        "drag_points": [],
    }
    for x, y in [(20, 300), (20, 450), (220, 450), (220, 300)]:
        panel["drag_points"].append(
            {
                "x": x,
                "y": y,
                "z": 0.0,
                "smooth": False,
                "is_slingshot": False,
                "has_auto_texture": True,
                "tex_coord": 0.0,
                "is_locked": False,
                "editor_layer": 0,
                "editor_layer_name": "Scorbit",
                "editor_layer_visibility": True,
            }
        )
    (output / "gameitems" / filename).write_text(json.dumps({"Flasher": panel}, indent=2))
    index_file = output / "gameitems.json"
    index.append(
        {
            "file_name": filename,
            "is_locked": False,
            "editor_layer": 0,
            "editor_layer_name": "Scorbit",
            "editor_layer_visibility": True,
        }
    )
    index_file.write_text(json.dumps(index, indent=2))
    subprocess.run([str(vpxtool), "assemble", str(output)], check=True)
    manifest["embedded_script_sha256"] = hashlib.sha256((output / "script.vbs").read_bytes()).hexdigest()
    output.with_suffix(".build.json").write_text(json.dumps(manifest, indent=2))
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--vpxtool", type=Path, required=True)
    parser.add_argument("--test-qr", type=Path)
    args = parser.parse_args()
    build(args.extraction, args.output, args.vpxtool, args.test_qr)
