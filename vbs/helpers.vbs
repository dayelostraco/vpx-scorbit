' Existing sToken/sQRCode helpers, shared executable folder, isolated table state.
' Caller must supply a verified Scorbit VPIN catalog identity. No default ID.
Class SBHelpers
    Public Ready, LastError, StateFolder, QRClaimPath, QRPairPath
    Private fso, shell, reader, tokenFile, helperFolder, beganAt, launched, privateToken
    Private opdbId, apiHost
    Private Sub Class_Initialize()
        Set fso = CreateObject("Scripting.FileSystemObject")
        Set shell = CreateObject("WScript.Shell")
        Set reader = New SBJsonReader
        Ready = False : launched = False : LastError = ""
    End Sub
    Private Function Quote(path)
        If InStr(path, Chr(34)) Or InStr(path, vbCr) Or InStr(path, vbLf) Then Err.Raise 5, "SBHelpers", "Invalid path"
        Quote = Chr(34) & path & Chr(34)
    End Function
    Public Sub Start(helpersPath, statePath, catalogId, catalogOpdb, host, nowMs)
        ' Trusted installation paths and verified VPIN identity; clock in milliseconds.
        ' Deletes previous outputs only in caller-selected table state, then launches
        ' sToken asynchronously. Packaging verifies executable hashes; this host does not.
        Dim rx, locator, service, devices, device, mac, uuid, serial, parts, prefix, command
        If launched Then Err.Raise 5, "SBHelpers", "Already started"
        If Not IsNumeric(catalogId) Then Err.Raise 5, "SBHelpers", "Missing verified catalog ID"
        If catalogId <= 0 Or catalogId <> Fix(catalogId) Then Err.Raise 5, "SBHelpers", "Invalid catalog ID"
        Set rx = New RegExp : rx.Pattern = "^[A-Za-z0-9_-]+$"
        If Not rx.Test(catalogOpdb) Then Err.Raise 5, "SBHelpers", "Invalid OPDB ID"
        If host <> "api.scorbit.io" And host <> "staging.scorbit.io" Then Err.Raise 5, "SBHelpers", "Unknown API host"
        helperFolder = fso.GetAbsolutePathName(helpersPath)
        StateFolder = fso.GetAbsolutePathName(statePath)
        If LCase(helperFolder) = LCase(StateFolder) Then Err.Raise 5, "SBHelpers", "State must be table-specific"
        If Not fso.FileExists(fso.BuildPath(helperFolder, "sToken.exe")) Or Not fso.FileExists(fso.BuildPath(helperFolder, "sQRCode.exe")) Then
            Err.Raise 5, "SBHelpers", "Install the common helper package"
        End If
        If Not fso.FolderExists(StateFolder) Then fso.CreateFolder StateFolder
        tokenFile = fso.BuildPath(StateFolder, "sToken.dat")
        QRPairPath = fso.BuildPath(StateFolder, "QRcode.png")
        QRClaimPath = fso.BuildPath(StateFolder, "QRclaim.png")
        ' Keep the established helper identity derivation for ordinary hardware.
        ' Refuse missing/placeholder firmware identities instead of borrowing one.
        Set locator = CreateObject("WbemScripting.SWbemLocator")
        Set service = locator.ConnectServer(".", "root\cimv2")
        Set devices = service.ExecQuery("SELECT * FROM Win32_NetworkAdapter WHERE physicaladapter=true")
        mac = ""
        For Each device In devices
            If Not IsNull(device.MACAddress) Then mac = Replace(device.MACAddress, ":", "") : Exit For
        Next
        rx.Pattern = "^[A-Fa-f0-9]{12}$"
        If Not rx.Test(mac) Then Err.Raise 5, "SBHelpers", "No stable adapter identity"
        uuid = ""
        For Each device In service.ExecQuery("SELECT * FROM Win32_ComputerSystemProduct")
            uuid = device.UUID : Exit For
        Next
        rx.Pattern = "^[A-Fa-f0-9]{8}(-[A-Fa-f0-9]{4}){3}-[A-Fa-f0-9]{12}$"
        If Not rx.Test(uuid) Then Err.Raise 5, "SBHelpers", "No stable firmware identity"
        If LCase(uuid) = "03000200-0400-0500-0006-000700080009" Then Err.Raise 5, "SBHelpers", "Firmware needs a private stable UUID override"
        serial = CDbl(CLng("&H" & Mid(mac, 5))) + catalogId
        parts = Split(uuid, "-")
        prefix = LCase(Hex(CLng("&H" & parts(0)) + catalogId))
        uuid = prefix & parts(1) & parts(2) & parts(3) & parts(4)
        uuid = String(32-Len(uuid), "0") & uuid
        ' Remove only this table's previous output; a failed launch cannot use it.
        If fso.FileExists(tokenFile) Then fso.DeleteFile tokenFile
        If fso.FileExists(QRPairPath) Then fso.DeleteFile QRPairPath
        If fso.FileExists(QRClaimPath) Then fso.DeleteFile QRClaimPath
        opdbId = catalogOpdb : apiHost = host
        command = Quote(fso.BuildPath(helperFolder, "sToken.exe")) & " " & uuid & " vpin " & serial & " " & catalogId & " " & Quote(StateFolder) & " " & Quote(tokenFile) & " " & host
        shell.Run command, 0, False
        beganAt = nowMs : launched = True
    End Sub
    Public Sub Tick(nowMs)
        ' Poll private helper output; partial JSON is retried until the 30-second limit.
        Dim stream, value, node
        If Ready Or Not launched Then Exit Sub
        If nowMs - beganAt > 30000 Or nowMs < beganAt Then
            launched = False : LastError = "Authentication helper timed out" : Exit Sub
        End If
        If Not fso.FileExists(tokenFile) Then Exit Sub
        ' Helper may still be writing. Wait for complete valid JSON; no busy loop.
        On Error Resume Next
        Set stream = fso.OpenTextFile(tokenFile, 1)
        Set value = reader.Parse(stream.ReadAll)
        stream.Close
        If Err.Number = 0 Then
            If value.Kind = "object" Then
                If value.Children.Exists("stoken") Then
                    Set node = value.Children("stoken")
                    If node.Kind = "string" And Len(node.Scalar) >= 8 Then privateToken = node.Scalar : Ready = True
                End If
            End If
        End If
        Err.Clear
        On Error GoTo 0
    End Sub
    Public Sub ConnectTransport(transport)
        ' Pass the private token only after Ready; token renewal is not implemented.
        If Not Ready Then Err.Raise 5, "SBHelpers", "Authentication not ready"
        transport.Connect privateToken, apiHost
    End Sub
    Public Sub GenerateClaim(venueId)
        ' Launch QR generation for a provisioned venue machine, not a catalog ID.
        ' Completion is observed through the output file; the process is not awaited.
        Dim rx, command
        Set rx = New RegExp : rx.Pattern = "^[1-9][0-9]*$"
        If Not Ready Or Not rx.Test(CStr(venueId)) Then Err.Raise 5, "SBHelpers", "Invalid venue identity"
        command = Quote(fso.BuildPath(helperFolder, "sQRCode.exe")) & " " & venueId & " " & opdbId & " " & Quote(StateFolder)
        shell.Run command, 0, False
    End Sub
End Class
