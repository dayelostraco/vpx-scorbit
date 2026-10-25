"""Compile a deliberately narrow, validated upstream map subset to VBScript.

Unsupported layouts/encodings fail; this is not a second general map parser.
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate(mapping, rom):
    """Return VBS source for a supported map/ROM; never write files or execute it.

    Offsets are zero-based bytes in the WPC RAM prefix. Unsupported field
    semantics raise ValueError; missing schema fields may raise KeyError.
    Treat externally supplied metadata as untrusted, including the ROM name.
    """
    # ROM names become VBScript string literals; metadata membership alone is
    # not a trust boundary when the map itself is supplied by a caller.
    if not isinstance(rom, str) or not re.fullmatch(r"[a-z0-9_]{1,64}", rom):
        raise ValueError("Unsafe ROM identifier")
    meta = mapping["_metadata"]
    if meta["platform"] != "williams-wpc-12K" or rom not in meta["roms"]:
        raise ValueError("Unsupported platform or ROM revision")
    fields = mapping["game_state"]

    def expr(field):
        allowed = {"label", "_notes", "start", "length", "encoding"}
        if set(field) - allowed:
            raise ValueError("Unsupported field semantics")
        offset = field["start"]
        if isinstance(offset, str):
            offset = int(offset, 0)
        length = field.get("length", 1)
        encoding = field["encoding"]
        if type(offset) is not int or type(length) is not int:
            raise ValueError("Field offset and length must be integers")
        if encoding not in {"int", "bool", "bcd"} or not 1 <= length <= 6 or not 0 <= offset <= 0x3000 - length:
            raise ValueError("Unsupported field encoding or location")
        return f'SBReadField(nv, {offset}, {length}, "{encoding}")'

    if len(fields["scores"]) != 4:
        raise ValueError("Exactly four score slots required")
    lines = [
        "' Generated from upstream map; retain maps licenses and source provenance.",
        "Function SBDecode(nv, actualRom)",
        "    Dim s, scores, size",
        f'    If LCase(actualRom) <> "{rom}" Then Err.Raise 5, "SBDecode", "ROM mismatch"',
        '    If Not IsArray(nv) Then Err.Raise 5, "SBDecode", "No snapshot"',
        '    If LBound(nv) <> 0 Then Err.Raise 5, "SBDecode", "Unsupported array base"',
        "    size = UBound(nv) + 1",
        '    If size <> 12288 And size <> 12334 Then Err.Raise 5, "SBDecode", "Unsupported snapshot size"',
        "    Set s = New SBRomSnapshot",
    ]
    for attr, key in [
        ("GameOver", "game_over"),
        ("PlayerCount", "player_count"),
        ("Player", "current_player"),
        ("Ball", "current_ball"),
    ]:
        lines.append(f"    s.{attr} = {expr(fields[key])}")
    lines += [
        "    s.Scores = Array(" + ", ".join(expr(f) for f in fields["scores"]) + ")",
        "    SBValidateSnapshot s",
        "    Set SBDecode = s",
        "End Function",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--map", type=Path, required=True)
    p.add_argument("--rom", required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    with a.output.open("x", encoding="utf-8") as f:
        f.write(generate(json.loads(a.map.read_text()), a.rom))
