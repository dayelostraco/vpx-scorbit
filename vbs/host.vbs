' Shared table host. Build supplies SB_ROM, SB_CATALOG_ID, SB_OPDB,
' SB_NETWORK_ENABLED, SB_STATE_NAME and SB_TEST_QR. Network defaults off.
Dim SBClient, SBAuth, SBTracker, SBPanel, SBFSO, SBTable, SBController, SBRunning
Dim SBQRSignature, SBQRAt, SBQRChoice, SBClaimVenue, SBConnected, SBLastError

Sub SBCommonStart(table, panel, controllerObject)
    ' Called after table/controller initialization; table owns supplied objects.
    ' Starts a 200 ms panel timer. Generated configuration keeps pilot networking off.
    Set SBTable = table : Set SBPanel = panel
    Set SBController = controllerObject
    Set SBClient = New SBHttpTransport : Set SBAuth = New SBHelpers
    Set SBTracker = New SBLifecycle : Set SBFSO = CreateObject("Scripting.FileSystemObject")
    SBRunning = True : SBConnected = False : SBQRSignature = ""
    SBQRChoice = 0 : SBClaimVenue = "" : SBLastError = ""
    SBPanel.Visible = False
    SBSizeDesktopQR SBPanel, WindowWidth, WindowHeight
    SBPanel.TimerInterval = 200 : SBPanel.TimerEnabled = True
    If SB_NETWORK_ENABLED Then
        On Error Resume Next
        SBAuth.Start TablesDirectory, SBFSO.BuildPath(TablesDirectory, SB_STATE_NAME), SB_CATALOG_ID, SB_OPDB, "api.scorbit.io", GameTime
        If Err.Number <> 0 Then SBLastError = "Scorbit initialization unavailable" : Err.Clear
        On Error GoTo 0
    End If
End Sub

Sub SBCommonStop()
    ' Idempotent table-exit hook; stop display/polling without fabricating final scores.
    If Not SBRunning Then Exit Sub
    SBRunning = False : SBPanel.Visible = False : SBPanel.TimerEnabled = False
    SBClient.Disconnect
    ' Never manufacture a finished session when VPX closes.
End Sub

Sub SBCommonOption(table, eventId)
    ' Manual recall invalidates the image signature; safe-window guards still apply.
    Dim choice
    choice = table.Option("Scorbit QR", 0, 1, 1, 0, 0, Array("Auto", "Show again"))
    If eventId = 1 And choice = 1 And SBQRChoice <> 1 Then SBQRSignature = ""
    SBQRChoice = choice
End Sub

Sub SBQRPanel_Timer()
    ' VPX timer entrypoint: contain runtime errors and abort only the open local game.
    If Not SBRunning Then Exit Sub
    On Error Resume Next
    SBCommonTick
    If Err.Number <> 0 Then
        ' Invalid memory or a plugin error must never take down the table.
        SBLastError = "Scorbit snapshot/runtime unavailable"
        SBPanel.Visible = False
        SBTracker.Reset
        SBClient.Entries.Abort
        Err.Clear
    End If
    On Error GoTo 0
End Sub

Sub SBCommonTick()
    ' Poll helpers/HTTP and decode one snapshot; called through the guarded timer.
    ' GameTime drives telemetry, while Now drives visible QR timeout during captures.
    Dim nv, snapshot, eventName, guid, qrPath, timeout, safeToShow, file, signature
    If SB_NETWORK_ENABLED Then
        SBAuth.Tick GameTime
        If SBAuth.Ready And Not SBConnected Then
            SBAuth.ConnectTransport SBClient : SBConnected = True
        End If
        SBClient.Tick GameTime
        If SBClient.VenueMachineId <> "" And SBClient.VenueMachineId <> SBClaimVenue Then
            SBAuth.GenerateClaim SBClient.VenueMachineId
            SBClaimVenue = SBClient.VenueMachineId
        End If
    End If
    nv = SBController.NVRAM
    Set snapshot = SBDecode(nv, SBController.GameName)
    eventName = SBTracker.Feed(snapshot, GameTime)
    If SB_NETWORK_ENABLED And SBClient.Enabled And Not SBClient.NeedsPairing Then
        Select Case eventName
            Case "start"
                guid = Mid(CreateObject("Scriptlet.TypeLib").Guid, 2, 36)
                SBClient.ClearClaims
                SBClient.Entries.Begin guid, GameTime, snapshot
            Case "update"
                If Not SBClient.Entries.IsClosed Then SBClient.Entries.Update snapshot, GameTime
            Case "finish"
                If Not SBClient.Entries.IsClosed Then SBClient.Entries.Finish snapshot, GameTime
            Case "abort"
                SBClient.Entries.Abort
        End Select
    End If
    qrPath = "" : timeout = 30 : safeToShow = snapshot.GameOver
    If SB_NETWORK_ENABLED Then
        If SBAuth.Ready Then
            If SBClient.NeedsPairing Then
                qrPath = SBAuth.QRPairPath
            ElseIf Not snapshot.GameOver And SBTracker.Active Then
                If snapshot.Player >= 1 And snapshot.Player <= 4 Then
                    If SBClient.GetName(snapshot.Player) = "" Then
                        qrPath = SBAuth.QRClaimPath : timeout = 15
                        safeToShow = SBSafeClaimWindow(snapshot)
                    End If
                End If
            End If
        End If
    Else
        qrPath = SB_TEST_QR
    End If
    If qrPath = "" Then SBPanel.Visible = False : SBQRSignature = "" : Exit Sub
    If Not SBFSO.FileExists(qrPath) Then SBPanel.Visible = False : Exit Sub
    Set file = SBFSO.GetFile(qrPath)
    signature = qrPath & CStr(file.DateLastModified) & CStr(file.Size)
    If timeout = 15 Then signature = signature & ":seat=" & snapshot.Player
    If signature <> SBQRSignature Then
        SBLoadQR SBPanel, qrPath
        SBQRSignature = signature : SBQRAt = Now
    End If
    ' Desktop is qualified by capture decoding; headset rendering is pending.
    SBPanel.Visible = safeToShow And Now >= SBQRAt And DateDiff("s", SBQRAt, Now) < timeout And RenderingMode <> 2
End Sub
