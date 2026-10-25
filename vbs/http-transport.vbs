' Poll-driven legacy helper protocol transport. No synchronous network waits.
' Credentials are provided privately by the helper bootstrap, never logged.
' Default is disconnected. Host calls Tick from its table timer.
Class SBHttpFactory
    Public Function Create()
        ' Fresh asynchronous-capable COM request; tests inject an offline factory.
        Set Create = CreateObject("Msxml2.ServerXMLHTTP.6.0")
    End Function
End Class

Class SBHttpTransport
    Public Entries, Enabled, NeedsPairing, VenueMachineId, LastError, LastStatus
    Private request, inFlight, requestKind, requestId, startedAt, nextAt, token, endpoint
    Private responseJson, reader, claims(3), factory
    Private Sub Class_Initialize()
        Set Entries = New SBEntryQueue
        Set reader = New SBJsonReader
        Set factory = New SBHttpFactory
        Enabled = False : inFlight = False : NeedsPairing = True
        VenueMachineId = "" : LastError = "" : LastStatus = 0 : nextAt = 0
    End Sub
    Public Property Set RequestFactory(value)
        ' Dependency injection while disconnected only; never replace an active request.
        If Enabled Then Err.Raise 5, "SBHttpTransport", "Cannot replace active factory"
        Set factory = value
    End Property
    Public Sub Connect(privateToken, apiHost)
        ' Enables the whitelisted HTTPS endpoint; initial host setup calls this once.
        ' This is not a complete identity-switch/reconnect or pending-queue migration API.
        If apiHost <> "api.scorbit.io" And apiHost <> "staging.scorbit.io" Then Err.Raise 5, "SBHttpTransport", "Unknown API host"
        If Len(privateToken) < 8 Or InStr(privateToken, vbCr) Or InStr(privateToken, vbLf) Then Err.Raise 5, "SBHttpTransport", "Invalid token"
        token = privateToken : endpoint = "https://" & apiHost
        Enabled = True : nextAt = 0
    End Sub
    Public Sub Disconnect()
        ' Abort the current request and forget the token; entries remain in memory.
        If inFlight Then request.abort
        inFlight = False : Enabled = False : token = ""
        ' No game-finished message is manufactured here.
    End Sub
    Public Function GetName(player)
        ' Player seats are 1-based; empty string is the current unclaimed heuristic.
        GetName = ""
        If player >= 1 And player <= 4 Then GetName = claims(player-1)
    End Function
    Public Sub ClearClaims()
        ' Clear local display-name cache only; no service-side unclaim request is sent.
        Dim i
        For i = 0 To 3 : claims(i) = "" : Next
    End Sub
    Public Sub Tick(nowMs)
        ' Called by the table timer; milliseconds share the lifecycle clock.
        ' HTTP failures stay local and queued entries require explicit ACK.
        If Not Enabled Then Exit Sub
        ' Contain network errors so an unavailable server cannot stop table play.
        On Error Resume Next
        Poll nowMs
        If Err.Number <> 0 Then
            LastError = "Network or response error"
            Err.Clear
            If inFlight Then request.abort
            inFlight = False : nextAt = nowMs + 5000
        End If
        On Error GoTo 0
    End Sub
    Private Sub Poll(nowMs)
        Dim body
        If inFlight Then
            If request.readyState = 4 Then
                LastStatus = request.status
                If LastStatus = 200 Then
                    ' Parse BEFORE acknowledging; malformed responses cannot claim success.
                    Set responseJson = reader.Parse(request.responseText)
                    ApplyResponse responseJson
                    If requestKind = "entry" Then Entries.Acknowledge requestId
                    LastError = "" : nextAt = nowMs + 2000
                ElseIf LastStatus = 401 Or LastStatus = 403 Then
                    Enabled = False : LastError = "Authentication rejected"
                Else
                    LastError = "Request not acknowledged" : nextAt = nowMs + 5000
                End If
                inFlight = False
            ElseIf nowMs - startedAt > 10000 Or nowMs < startedAt Then
                request.abort : inFlight = False : nextAt = nowMs + 5000
                LastError = "Request timed out; entry retained"
            End If
            Exit Sub
        End If
        If nowMs < nextAt Then Exit Sub
        Set request = factory.Create()
        request.setTimeouts 3000, 3000, 5000, 5000
        If Entries.Count > 0 And Not NeedsPairing Then
            requestKind = "entry" : requestId = Entries.HeadSequence
            body = Entries.HeadBody
            request.open "POST", endpoint & "/api/entry/", True
            request.setRequestHeader "Content-Type", "application/x-www-form-urlencoded"
        Else
            requestKind = "heartbeat" : body = ""
            request.open "GET", endpoint & "/api/heartbeat/?session_active=" & LCase(CStr(Not Entries.IsClosed)), True
        End If
        request.setRequestHeader "Cache-Control", "no-cache"
        request.setRequestHeader "Authorization", "SToken " & token
        startedAt = nowMs : inFlight = True
        request.send body
    End Sub
    Private Sub ApplyResponse(root)
        Dim rows, row, node, key, slot, pairedNext, venueNext, claimsNext(3), i, rx
        ' Commit pairing/claims only after validating the entire response.
        pairedNext = NeedsPairing : venueNext = VenueMachineId
        For i = 0 To 3 : claimsNext(i) = claims(i) : Next
        If root.Kind <> "object" Then Err.Raise 5, "SBHttpTransport", "Unexpected response"
        If root.Children.Exists("unpaired") Then
            Set node = root.Children("unpaired")
            If node.Kind <> "boolean" Then Err.Raise 5, "SBHttpTransport", "Unexpected pairing state"
            pairedNext = node.Scalar
            If pairedNext Then
                venueNext = ""
                For i = 0 To 3 : claimsNext(i) = "" : Next
            End If
        End If
        If root.Children.Exists("venuemachine_id") Then
            Set node = root.Children("venuemachine_id")
            If node.Kind = "number" Then
                Set rx = New RegExp : rx.Pattern = "^[1-9][0-9]{0,14}$"
                If Not rx.Test(node.Scalar) Then Err.Raise 5
                If root.Children.Exists("unpaired") Then
                    If root.Children("unpaired").Scalar Then Err.Raise 5, "SBHttpTransport", "Conflicting pairing state"
                End If
                venueNext = node.Scalar : pairedNext = False
            ElseIf node.Kind <> "null" Then
                Err.Raise 5, "SBHttpTransport", "Unexpected venue identity"
            End If
        End If
        ' Claim response structure is validated against fixtures before deployment.
        If root.Children.Exists("players") Then
            Set rows = root.Children("players")
            If rows.Kind <> "array" Then Err.Raise 5
            If rows.Children.Count > 4 Then Err.Raise 5
            For i = 0 To 3 : claimsNext(i) = "" : Next
            For Each key In rows.Children.Keys
                slot = CInt(key) : Set row = rows.Children(key)
                If row.Kind <> "object" Then Err.Raise 5
                If row.Children.Exists("cached_display_name") Then
                    Set node = row.Children("cached_display_name")
                    If node.Kind <> "string" And node.Kind <> "null" Then Err.Raise 5
                    If node.Kind = "string" Then claimsNext(slot) = node.Scalar
                End If
            Next
        End If
        NeedsPairing = pairedNext : VenueMachineId = venueNext
        For i = 0 To 3 : claims(i) = claimsNext(i) : Next
    End Sub
End Class
