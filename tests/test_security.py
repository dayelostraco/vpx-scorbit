"""Deterministic hostile-input regressions and bounded property-based fuzzing."""

import copy
import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tools.audit_maps import audit
from tools.build_common_pilot import inject
from tools.generate_rom_adapter import generate
from vpx_scorbit.memory import Decoder, decode_field

ROOT = Path(__file__).resolve().parents[1]
MAP = json.loads((ROOT / "maps/mm_109.map.json").read_text())


class InputBoundaryTests(unittest.TestCase):
    def test_decoder_rejects_incomplete_layout_and_state(self):
        mapping = copy.deepcopy(MAP)
        mapping["_metadata"]["platform"] = "unknown"
        with self.assertRaises(ValueError):
            Decoder(mapping, "mm_109b")
        mapping = copy.deepcopy(MAP)
        del mapping["game_state"]["current_ball"]
        with self.assertRaises(ValueError):
            Decoder(mapping, "mm_109b")
        decoder = Decoder(MAP, "mm_109b")
        with self.assertRaises(ValueError):
            decoder.decode(bytes(16))
        raw = bytearray(0x3000)
        raw[135] = 1
        raw[5901] = 5
        with self.assertRaises(ValueError):
            decoder.decode(raw)

    @settings(max_examples=500, derandomize=True)
    @given(st.text(max_size=80))
    def test_rom_literal_fuzz(self, rom):
        mapping = copy.deepcopy(MAP)
        mapping["_metadata"]["roms"] = [rom]
        if re.fullmatch(r"[a-z0-9_]{1,64}", rom):
            self.assertIn(f'<> "{rom}"', generate(mapping, rom))
        else:
            with self.assertRaises(ValueError):
                generate(mapping, rom)

    @settings(max_examples=500, derandomize=True)
    @given(st.binary(min_size=1, max_size=6))
    def test_bcd_fuzz(self, data):
        field = {"start": 0, "length": len(data), "encoding": "bcd"}
        if all(b >> 4 <= 9 and b & 15 <= 9 for b in data):
            self.assertEqual(decode_field(data, field), int(data.hex()))
        else:
            with self.assertRaises(ValueError):
                decode_field(data, field)

    def test_field_type_rejection(self):
        for key in ("start", "length"):
            for value in (True, False, 1.5, None):
                mapping = copy.deepcopy(MAP)
                mapping["game_state"]["game_over"][key] = value
                with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                    generate(mapping, "mm_109b")

    def test_index_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "maps"
            root.mkdir()
            (parent / "outside.json").write_text(json.dumps(MAP))
            (root / "index.json").write_text(json.dumps({"mm_109b": "../outside.json"}))
            self.assertEqual(audit(root)[0]["reason"], "Map path escapes maps root")

    def test_ram_only_clears_previous_trailer(self):
        decoder = Decoder(MAP, "mm_109b")
        raw = bytearray(0x302E)
        raw[135] = 1
        raw[0x3000:] = bytes(range(46))
        decoder.decode(raw)
        decoder.decode(raw[:0x3000])
        self.assertEqual(decoder.parser.get_dot_nv(), raw[:0x3000])

    def test_hook_placement_and_ambiguous_input(self):
        script = (
            "Sub Table1_Init\n    InitializeROM\nEnd Sub\n"
            "Sub Table1_exit\nEnd Sub\n"
            "Sub Table1_OptionEvent(ByVal eventId)\nEnd Sub\n"
        )
        result = inject(script)
        self.assertLess(result.index("InitializeROM"), result.index("SBCommonStart"))
        self.assertIn("Sub Table1_exit\n    SBCommonStop\n", result)
        self.assertIn("SBCommonOption Table1, eventId", result)
        for bad in ("", script + script, script.replace("End Sub", "")):
            with self.assertRaises(ValueError):
                inject(bad)


class NativeFuzzTests(unittest.TestCase):
    def test_native_parser_and_byte_space(self):
        # Differential JSON corpus and exhaustive single-byte BCD oracle; run
        # against cscript itself, not a Python reimplementation of the runtime.
        import random
        import shutil

        if not shutil.which("cscript"):
            self.skipTest("Windows VBScript host required")
        rng = random.Random(20261025)
        corpus = [
            "{}",
            "[]",
            "true",
            "false",
            "null",
            "0",
            "-1.5e2",
            '{"a":1,"a":2}',
            "[1,]",
            '"unterminated',
            "[" * 40 + "0" + "]" * 40,
        ]
        corpus += [
            json.dumps({"n": rng.randrange(-10000, 10000), "v": [rng.choice([True, None, "hello", 12])]})
            for _ in range(300)
        ]
        alphabet = '{}[],:"\\0123456789nulltruefalse \n'
        corpus += ["".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 60))) for _ in range(500)]
        checks = []
        for value in corpus:
            try:

                def unique(pairs):
                    result = {}
                    for key, item in pairs:
                        if key in result:
                            raise ValueError("duplicate")
                        result[key] = item
                    return result

                json.loads(value, object_pairs_hook=unique)
                valid = not value.startswith("[" * 40)
            except ValueError:
                valid = False
            literal = " & ".join("ChrW(" + str(ord(c)) + ")" for c in value) or '""'
            checks.append(f"CheckJson {literal}, {str(valid)}")
        body = """
Dim reader, node, b, nv(0), actual, expected, errors
Set reader = New SBJsonReader
Sub CheckJson(value, valid)
    On Error Resume Next
    Err.Clear
    Set node = reader.Parse(value)
    If (Err.Number = 0) <> valid Then WScript.Quit 2
    Err.Clear
    On Error GoTo 0
End Sub
For b = 0 To 255
    nv(0) = b
    On Error Resume Next
    Err.Clear
    actual = SBReadField(nv, 0, 1, "bcd")
    errors = Err.Number
    Err.Clear
    On Error GoTo 0
    If (b \\ 16 <= 9) And ((b Mod 16) <= 9) Then
        expected = (b \\ 16) * 10 + (b Mod 16)
        If errors <> 0 Or actual <> expected Then WScript.Quit 3
    Else
        If errors = 0 Then WScript.Quit 4
    End If
Next
CheckJson String(65537, " "), False
"""
        source = (
            "Option Explicit\n"
            + (ROOT / "vbs/rom-core.vbs").read_text()
            + "\n"
            + (ROOT / "vbs/json.vbs").read_text()
            + body
            + "\n".join(checks)
            + '\nWScript.Echo "PASS"\n'
        )
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "fuzz.vbs"
            script.write_text(source, encoding="utf-8")
            result = subprocess.run(
                ["cscript", "//Nologo", str(script)], capture_output=True, text=True, timeout=30, check=False
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)
