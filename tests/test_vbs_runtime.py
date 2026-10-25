import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.generate_rom_adapter import generate

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("cscript"), "Windows VBScript host required")
class VBScriptRuntimeTests(unittest.TestCase):
    def test_snapshot_types_mutation_and_locale(self):
        self.run_vbs("""
Dim s, tracker, result, bad, q, locale
Set s=New SBRomSnapshot
s.GameOver=True : s.PlayerCount=1 : s.Player=1 : s.Ball=1 : s.Scores=Array(0,0,0,0)
For Each bad In Array(Null, Empty, "100", 1.5, -1, True)
    s.Scores=Array(bad,0,0,0)
    On Error Resume Next
    SBValidateSnapshot s
    If Err.Number=0 Then WScript.Quit 2
    Err.Clear
    On Error GoTo 0
Next
s.Scores=Array(0,0,0,0)
Set tracker=New SBLifecycle
result=tracker.Feed(s,0) : result=tracker.Feed(s,200)
s.GameOver=False
If tracker.Feed(s,400) <> "none" Then Err.Raise 513
If tracker.Feed(s,600) <> "start" Then Err.Raise 514
s.Scores=Array(100,0,0,0)
result=tracker.Feed(s,800)
s.Scores=Array(0,0,0,0)
If tracker.Feed(s,1000) <> "abort" Then Err.Raise 515
For Each locale In Array(1033,1031,1036)
    SetLocale locale
    Set q=New SBEntryQueue
    s.Scores=Array(CDbl("9876543210"),0,0,0)
    q.Begin "12345678-1234-1234-1234-123456789abc", 1000, s
    If InStr(q.HeadBody,"current_p1_score=9876543210&")=0 Then Err.Raise 516
Next
WScript.Echo "PASS mutation/types/locale"
""")

    def run_vbs(self, body):
        mapping = json.loads((ROOT / "maps/mm_109.map.json").read_text())
        source = "Option Explicit\n" + (ROOT / "vbs/rom-core.vbs").read_text()
        source += "\n" + (ROOT / "vbs/entry-queue.vbs").read_text()
        source += "\n" + (ROOT / "vbs/json.vbs").read_text()
        source += "\n" + (ROOT / "vbs/http-transport.vbs").read_text()
        source += "\n" + (ROOT / "vbs/helpers.vbs").read_text()
        source += "\n" + generate(mapping, "mm_109b") + "\n" + body
        with tempfile.TemporaryDirectory() as folder:
            script = Path(folder) / "test.vbs"
            script.write_text(source, encoding="utf-8")
            result = subprocess.run(
                ["cscript", "//Nologo", str(script)], capture_output=True, text=True, timeout=15, check=False
            )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_real_vbscript_decoder_bounds_bcd_and_rom_guard(self):
        self.run_vbs("""
Dim nv(12333), i, s, result
For i = 0 To UBound(nv): nv(i) = 0: Next
nv(135) = 1 : nv(5901) = 4
nv(5792) = &H98 : nv(5793) = &H76 : nv(5794) = &H54 : nv(5795) = &H32 : nv(5796) = &H10
nv(5802) = &H22 : nv(5808) = &H33 : nv(5814) = &H44
Set s = SBDecode(nv, "mm_109b")
If s.Scores(0) <> CDbl("9876543210") Then Err.Raise 513
If s.Scores(1) <> 22 Or s.Scores(2) <> 33 Or s.Scores(3) <> 44 Then Err.Raise 514
On Error Resume Next
Set s = SBDecode(nv, "mm_10")
If Err.Number = 0 Then WScript.Quit 2
Err.Clear
nv(5792) = &HFA
Set s = SBDecode(nv, "mm_109b")
If Err.Number = 0 Then WScript.Quit 3
Err.Clear
result = SBReadField(nv, 12333, 5, "bcd")
If Err.Number = 0 Then WScript.Quit 4
Err.Clear
On Error GoTo 0
WScript.Echo "PASS decoder"
""")

    def test_pending_request_retains_final_and_next_game(self):
        self.run_vbs("""
Dim q, s, first, body, endSeen, nextSeen
Set q = New SBEntryQueue : Set s = New SBRomSnapshot
s.GameOver=False : s.PlayerCount=2 : s.Player=1 : s.Ball=1
s.Scores=Array(CDbl("9876543210"), 200, 0, 0)
q.Begin "12345678-1234-1234-1234-123456789abc", 1000, s
first=q.HeadSequence : body=q.HeadBody
s.Scores=Array(CDbl("9876543211"), 300, 0, 0)
q.Update s, 1200
q.Update s, 1400
If q.Count <> 2 Or q.HeadBody <> body Then Err.Raise 513
s.Scores=Array(CDbl("9876543212"), 400, 0, 0) : s.GameOver=True
q.Finish s, 1600
If q.Count <> 3 Or q.HeadSequence <> first Or q.HeadBody <> body Then Err.Raise 514
s.GameOver=False : s.Scores=Array(0, 0, 0, 0)
q.Begin "22345678-1234-1234-1234-123456789abc", 1700, s
q.Update s, 1800
endSeen=False : nextSeen=False
Do While q.Count > 0
    body=q.HeadBody
    If InStr(body,"active=false") > 0 Then
        If InStr(body,"current_p1_score=9876543212")=0 Or InStr(body,"current_p2_score=400")=0 Then Err.Raise 515
        If InStr(body,"current_player=-1")=0 Then Err.Raise 516
        endSeen=True
    End If
    If InStr(body,"22345678-") > 0 Then
        If Not endSeen Then Err.Raise 517
        nextSeen=True
    End If
    q.Acknowledge q.HeadSequence
Loop
If Not nextSeen Then Err.Raise 518
q.Abort
If q.Count <> 0 Then Err.Raise 519
q.Begin "32345678-1234-1234-1234-123456789abc", 2000, s
q.Finish s, 2100
q.Begin "42345678-1234-1234-1234-123456789abc", 2200, s
q.Abort
If q.Count <> 2 Then Err.Raise 520
If InStr(q.HeadBody,"32345678-")=0 Then Err.Raise 521
WScript.Echo "PASS pending final queue"
""")

    def test_fake_http_failure_retry_finish_and_auth_rejection(self):
        self.run_vbs("""
Class FakeRequest
    Public readyState, status, responseText, body, method, url, aborted
    Public Sub setTimeouts(a,b,c,d)
    End Sub
    Public Sub open(verb, address, async)
        method=verb : url=address : readyState=1 : aborted=False
    End Sub
    Public Sub setRequestHeader(name,value)
    End Sub
    Public Sub send(data)
        body=data
    End Sub
    Public Sub abort()
        aborted=True
    End Sub
End Class
Class FakeFactory
    Public Latest
    Public Function Create()
        Set Latest=New FakeRequest
        Set Create=Latest
    End Function
End Class
Dim t, factory, s, firstBody, oldRequest, q
Set t=New SBHttpTransport : Set factory=New FakeFactory
Set t.RequestFactory=factory
t.Connect "offline-test-only", "staging.scorbit.io"
t.Tick 0
factory.Latest.readyState=4 : factory.Latest.status=200
factory.Latest.responseText="{""venuemachine_id"":123,""unpaired"":false,""players"":[17]}"
t.Tick 10
If Not t.NeedsPairing Or t.VenueMachineId <> "" Or t.LastError = "" Then Err.Raise 522
t.Disconnect
Set t=New SBHttpTransport : Set t.RequestFactory=factory
t.Connect "offline-test-only", "staging.scorbit.io"
t.Tick 0
If factory.Latest.method <> "GET" Then Err.Raise 513
factory.Latest.readyState=4 : factory.Latest.status=200
factory.Latest.responseText="{""venuemachine_id"":123,""unpaired"":false}"
t.Tick 10
If t.NeedsPairing Then Err.Raise 514
Set s=New SBRomSnapshot
s.GameOver=False : s.PlayerCount=1 : s.Player=1 : s.Ball=1 : s.Scores=Array(10,0,0,0)
t.Entries.Begin "12345678-1234-1234-1234-123456789abc", 100, s
t.Tick 2100
firstBody=factory.Latest.body
s.Scores=Array(999,0,0,0) : s.GameOver=True
t.Entries.Finish s, 2200
t.Tick 2200
If t.Entries.Count <> 2 Then Err.Raise 515
factory.Latest.readyState=4 : factory.Latest.status=503 : factory.Latest.responseText="unavailable"
t.Tick 2300
If t.Entries.Count <> 2 Then Err.Raise 516
t.Tick 7400
If factory.Latest.body <> firstBody Then Err.Raise 517
factory.Latest.readyState=4 : factory.Latest.status=200 : factory.Latest.responseText="{}"
t.Tick 7500
If t.Entries.Count <> 1 Then Err.Raise 518
t.Tick 9600
If InStr(factory.Latest.body,"active=false")=0 Or InStr(factory.Latest.body,"current_p1_score=999")=0 Then Err.Raise 519
Set oldRequest=factory.Latest
t.Tick 19700
If Not oldRequest.aborted Or t.Entries.Count <> 1 Then Err.Raise 520
t.Tick 24800
factory.Latest.readyState=4 : factory.Latest.status=401
t.Tick 24900
If t.Enabled Or t.Entries.Count <> 1 Then Err.Raise 521
t.Disconnect
WScript.Echo "PASS fake HTTP"
""")

    def test_json_claim_names_and_malformed_responses(self):
        self.run_vbs(r"""
Dim reader, value, bad, candidate, key
Set reader=New SBJsonReader
Set value=reader.Parse("{""players"":[{""cached_display_name"":""A, B: C""},{""cached_display_name"":""Zo\u00eb""}],""unpaired"":false}")
If value.Children("unpaired").Scalar <> False Then Err.Raise 513
If value.Children("players").Children(0).Children("cached_display_name").Scalar <> "A, B: C" Then Err.Raise 514
If value.Children("players").Children(1).Children("cached_display_name").Scalar <> "Zo" & ChrW(&HEB) Then Err.Raise 515
For Each bad In Array("{", "[1,]", "{""x"":1,}", "01", "true false", "{""x"":1,""x"":2}")
    On Error Resume Next
    Set candidate=reader.Parse(bad)
    If Err.Number=0 Then WScript.Quit 7
    Err.Clear
    On Error GoTo 0
Next
WScript.Echo "PASS JSON"
""")

    def test_lifecycle_bonus_settle_reset_gap_and_late_attach(self):
        self.run_vbs("""
Function Snap(over, seats, player, ball, score)
    Dim s : Set s = New SBRomSnapshot
    s.GameOver = over : s.PlayerCount = seats : s.Player = player : s.Ball = ball
    s.Scores = Array(score, 0, 0, 0)
    Set Snap = s
End Function
Sub Expect(actual, expected)
    If actual <> expected Then Err.Raise 513, "Expect", actual & " != " & expected
End Sub
Dim tracker : Set tracker = New SBLifecycle
Expect tracker.Feed(Snap(False,1,1,2,100), 0), "none"
Expect tracker.Feed(Snap(False,1,1,2,100), 500), "none"
Expect tracker.Feed(Snap(True,1,1,3,100), 1000), "none"
Expect tracker.Feed(Snap(True,1,1,3,100), 1500), "none"
Expect tracker.Feed(Snap(False,1,1,1,0), 2000), "none"
Expect tracker.Feed(Snap(False,1,1,1,10), 2500), "start"
Expect tracker.Feed(Snap(False,1,1,3,100), 3000), "update"
Expect tracker.Feed(Snap(True,1,1,3,100), 3500), "none"
Expect tracker.Feed(Snap(True,1,1,3,150), 4500), "none"
Expect tracker.Feed(Snap(True,1,1,3,150), 5500), "none"
Expect tracker.Feed(Snap(True,1,1,3,150), 6500), "finish"
Expect tracker.Feed(Snap(True,1,1,3,150), 7000), "none"
Expect tracker.Feed(Snap(False,1,1,1,0), 7500), "none"
Expect tracker.Feed(Snap(False,1,1,1,10), 8000), "start"
Expect tracker.Feed(Snap(False,1,1,1,0), 8500), "abort"
Expect tracker.Feed(Snap(False,1,1,1,10), 9000), "none"
tracker.Reset
Expect tracker.Feed(Snap(True,1,1,3,100), 10000), "none"
Expect tracker.Feed(Snap(True,1,1,3,100), 10500), "none"
Expect tracker.Feed(Snap(False,1,1,1,0), 11000), "none"
Expect tracker.Feed(Snap(False,1,1,1,0), 11500), "start"
Expect tracker.Feed(Snap(True,1,1,3,0), 15000), "abort"
If tracker.Active Then Err.Raise 514
WScript.Echo "PASS lifecycle"
""")

    def test_observed_attract_does_not_authorize_late_ball_start(self):
        self.run_vbs("""
Dim t, s, i, eventName
Set t=New SBLifecycle : Set s=New SBRomSnapshot
s.GameOver=True : s.PlayerCount=1 : s.Player=1 : s.Ball=3 : s.Scores=Array(100,0,0,0)
eventName=t.Feed(s,0) : eventName=t.Feed(s,200)
s.GameOver=False : s.Ball=2
eventName=t.Feed(s,400) : eventName=t.Feed(s,600)
If t.Active Or t.Armed Then Err.Raise 513
WScript.Echo "PASS late ball guard"
""")

    def test_host_hides_pairing_and_claimed_seat_codes(self):
        body = """
Const SB_NETWORK_ENABLED=True, SB_CATALOG_ID=0, SB_OPDB="", SB_STATE_NAME="test", SB_TEST_QR="", TablesDirectory="unused"
Dim GameTime, WindowWidth, WindowHeight, RenderingMode
Sub SBSizeDesktopQR(panel,width,height)
End Sub
Sub SBLoadQR(panel,path)
End Sub
Function SBSafeClaimWindow(snapshot)
    SBSafeClaimWindow=True
End Function
"""
        body += (ROOT / "vbs/host.vbs").read_text()
        body += """
Class FakeController
    Public Data, GameName
    Public Property Get NVRAM()
        NVRAM=Data
    End Property
End Class
Class FakeTracker
    Public Active
    Public Function Feed(s,t)
        Feed="none"
    End Function
End Class
Class FakeClient
    Public VenueMachineId, Enabled, NeedsPairing, Claimed
    Public Sub Tick(t)
    End Sub
    Public Function GetName(player)
        GetName=Claimed
    End Function
End Class
Class FakePanel
    Public Visible
End Class
Class FakeFSO
    Public LastPath
    Public Function FileExists(path)
        LastPath=path : FileExists=False
    End Function
End Class
Dim memory(12333), i
For i=0 To UBound(memory): memory(i)=0: Next
memory(135)=1 : memory(5901)=1 : memory(946)=1 : memory(947)=1
Set SBController=New FakeController : SBController.Data=memory : SBController.GameName="mm_109b"
Set SBTracker=New FakeTracker : SBTracker.Active=False
Set SBClient=New FakeClient : SBClient.VenueMachineId="" : SBClient.Enabled=True
SBClient.NeedsPairing=False : SBClient.Claimed=""
Set SBAuth=New SBHelpers : SBAuth.Ready=True : SBAuth.QRPairPath="pair.png" : SBAuth.QRClaimPath="claim.png"
SBConnected=True : SBClaimVenue=""
Set SBPanel=New FakePanel : Set SBFSO=New FakeFSO : SBFSO.LastPath=""
SBCommonTick
If SBFSO.LastPath<>"" Or SBPanel.Visible Then Err.Raise 513
memory(135)=0 : SBController.Data=memory : SBTracker.Active=True
SBCommonTick
If SBFSO.LastPath<>"claim.png" Then Err.Raise 514
SBFSO.LastPath="" : SBClient.Claimed="Claimed player"
SBCommonTick
If SBFSO.LastPath<>"" Or SBPanel.Visible Then Err.Raise 515
SBClient.NeedsPairing=True
SBCommonTick
If SBFSO.LastPath<>"pair.png" Then Err.Raise 516
WScript.Echo "PASS host QR eligibility"
"""
        self.run_vbs(body)


class GeneratorTests(unittest.TestCase):
    def test_refuses_unimplemented_semantics(self):
        mapping = json.loads((ROOT / "maps/mm_109.map.json").read_text())
        mapping["game_state"]["scores"][0]["scale"] = 1000
        with self.assertRaises(ValueError):
            generate(mapping, "mm_109b")
