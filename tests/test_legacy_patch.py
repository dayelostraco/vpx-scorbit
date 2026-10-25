import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.patch_legacy_log import patch

SOURCE = b"""Class ScorbitIF
    Private LOGFILE(10000000), LogIdx
    Public Sub StartSession()
        LogIdx=0
    End Sub
    Public Sub Append(value)
			LOGFILE(LogIdx)=value
        LogIdx=LogIdx+1
    End Sub
    Public Function Row(index)
        Row=LOGFILE(index)
    End Function
End Class
"""


class LegacyPatchTests(unittest.TestCase):
    def test_scope_and_double_patch_guard(self):
        prefix = b"' Preserve original encoding: \xa0\r\n"
        result = patch(prefix + SOURCE)
        self.assertTrue(result.startswith(prefix))
        self.assertIn(b"Private LOGFILE(), LogIdx", result)
        with self.assertRaises(ValueError):
            patch(result)
        with self.assertRaises(ValueError):
            patch(SOURCE + SOURCE)

    @unittest.skipUnless(shutil.which("cscript"), "Windows VBScript host required")
    def test_generated_patch_preserves_records_and_resets(self):
        source = (
            patch(SOURCE)
            + b"""
Dim client, i
Set client=New ScorbitIF
client.StartSession
For i=0 To 4096: client.Append "row-" & i: Next
For i=0 To 4096
    If client.Row(i) <> "row-" & i Then Err.Raise 513
Next
client.StartSession
client.Append "new game"
If client.Row(0) <> "new game" Or Not IsEmpty(client.Row(1)) Then Err.Raise 514
WScript.Echo "PASS"
"""
        )
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "log-buffer.vbs"
            script.write_bytes(source)
            result = subprocess.run(
                ["cscript", "//Nologo", str(script)], capture_output=True, text=True, timeout=15, check=False
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)
