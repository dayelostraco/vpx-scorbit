"""Build an isolated Medieval Madness pilot from an existing vpxtool extraction.

Never modifies the source extraction or the live table. Requires the exact
script hash recorded by the first pilot; other revisions need explicit review.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def main():
    """Parse CLI paths and stage the historical file-telemetry pilot, never the live table.

    Trusted developer inputs and a matching source hash are required. Assembly
    errors propagate and may leave staging artifacts for inspection.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--extraction", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument("--vpxtool", type=Path, required=True)
    args = ap.parse_args()
    repo = Path(__file__).resolve().parents[1]
    pilot = json.loads((repo / "profiles/medieval-madness.json").read_text())
    source = args.extraction / "script.vbs"
    if hashlib.sha256(source.read_bytes()).hexdigest() != pilot["script_sha256"]:
        raise ValueError("Unknown table script revision: inspect hooks before adapting")
    if args.output.exists():
        raise ValueError("Output already exists; use a new staging directory")
    runtime = args.runtime.resolve()
    if any(c in str(runtime) for c in ('"', "\r", "\n")):
        raise ValueError("Runtime path cannot be embedded in VBScript")
    runtime.mkdir(parents=True, exist_ok=True)
    shutil.copytree(args.extraction, args.output)
    text = source.read_text(encoding="utf-8-sig")
    for old, new in [
        ("Sub Table1_Init", "Sub Table1_Init\n    SBStart"),
        ("Sub Table1_exit", "Sub Table1_exit\n    SBStop"),
        ("Sub Table1_OptionEvent(ByVal eventId)", "Sub Table1_OptionEvent(ByVal eventId)\n    SBOptionEvent eventId"),
    ]:
        if text.count(old) != 1:
            raise ValueError("Ambiguous lifecycle hook")
        text = text.replace(old, new, 1)
    helper = (repo / "assets/telemetry.vbs").read_text().replace("@@RUNTIME@@", str(runtime))
    (args.output / "script.vbs").write_text(text + "\n" + helper, encoding="utf-8")
    # Screen-space desktop backdrop; runtime compensates viewport aspect ratio.
    panel = {
        "height": 0.0,
        "pos_x": 120.0,
        "pos_y": 375.0,
        "backglass": True,
        "rot_x": 0.0,
        "rot_y": 0.0,
        "rot_z": 0.0,
        "color": "#ffffff",
        "is_timer_enabled": False,
        "timer_interval": 100,
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
    name = "Flasher.SBQRPanel.json"
    (args.output / "gameitems" / name).write_text(json.dumps({"Flasher": panel}, indent=2))
    index_file = args.output / "gameitems.json"
    index = json.loads(index_file.read_text())
    index.append(
        {
            "file_name": name,
            "is_locked": False,
            "editor_layer": 0,
            "editor_layer_name": "Scorbit",
            "editor_layer_visibility": True,
        }
    )
    index_file.write_text(json.dumps(index, indent=2))
    # Explicit local developer-selected executable, argument vector, no shell.
    # This CLI deliberately runs vpxtool; it is not exposed to remote callers.
    # nosemgrep: python.lang.security.audit.dangerous-subprocess-use-tainted-env-args.dangerous-subprocess-use-tainted-env-args
    subprocess.run([str(args.vpxtool), "assemble", str(args.output)], check=True)


if __name__ == "__main__":
    main()
