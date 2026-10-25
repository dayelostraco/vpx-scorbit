"""Report which upstream ROM maps this generator can decode; not gameplay support."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.generate_rom_adapter import generate


def audit(root):
    """Return static eligibility rows, excluding upstream index metadata.

    Relative map paths stay within root; report errors without machine-specific
    filesystem paths so the resulting discovery report can be published.
    """
    index = json.loads((root / "index.json").read_text())
    rows = []
    for rom, relative in sorted(index.items()):
        if rom.startswith("_"):
            continue
        row = {"rom": rom, "map": relative, "qualification": "discovered only"}
        try:
            path = (root / relative).resolve()
            if not path.is_relative_to(root.resolve()):
                raise ValueError("Map path escapes maps root")
            mapping = json.loads(path.read_text(encoding="utf-8-sig"))
            generate(mapping, rom)
            row["decoder"] = "supported subset; untested live"
            row["mapped_fields"] = sorted(mapping["game_state"])
        except (ValueError, KeyError, TypeError, FileNotFoundError) as exc:
            row["decoder"] = "needs adapter work"
            row["reason"] = "Map file missing" if isinstance(exc, FileNotFoundError) else str(exc)
        rows.append(row)
    return rows


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maps-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = audit(args.maps_root)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(rows, stream, indent=2)
    supported = sum(row["decoder"].startswith("supported") for row in rows)
    print(
        f"{len(rows)} indexed ROM revisions; {supported} match the current decoder subset; "
        "none qualified by this static audit."
    )
