 ' Shared VPX Scorbit ROM primitives. No network, file writes, or table globals.
Class SBRomSnapshot
    ' Zero-based four-slot Scores array; integer values held as Double for BCD.
    ' Snapshot ownership transfers only by copy when retained by the lifecycle.
    Public GameOver, PlayerCount, Player, Ball, Scores
End Class

' Numeric strings, Empty, Null and fractional values must not become payloads.
Function SBWholeNumber(value, minimum, maximum)
    SBWholeNumber = False
    Select Case VarType(value)
        Case 2, 3, 4, 5, 6, 14, 17
            If value >= minimum And value <= maximum Then
                SBWholeNumber = (value = Fix(value))
            End If
    End Select
End Function

Function SBCopySnapshot(source)
    ' Copy validated scalars and four score slots; never retain caller-owned state.
    Dim copy
    Set copy = New SBRomSnapshot
    copy.GameOver = source.GameOver : copy.PlayerCount = source.PlayerCount
    copy.Player = source.Player : copy.Ball = source.Ball
    copy.Scores = Array(source.Scores(0), source.Scores(1), source.Scores(2), source.Scores(3))
    Set SBCopySnapshot = copy
End Function

Function SBReadField(nv, offset, count, encoding)
    ' Zero-based byte offset, 1-6 bytes, big-endian int/bool/BCD. Invalid bytes raise.
    ' Double arithmetic avoids 32-bit overflow for five-byte decimal scores.
    Dim result, i, b, hi, lo
    If Not IsArray(nv) Then Err.Raise 5, "SBReadField", "Not a memory snapshot"
    If Not SBWholeNumber(offset, 0, 12333) Or Not SBWholeNumber(count, 1, 6) Then Err.Raise 5, "SBReadField", "Invalid field bounds"
    If count < 1 Or count > 6 Or offset < LBound(nv) Or offset + count - 1 > UBound(nv) Then
        Err.Raise 5, "SBReadField", "Field outside snapshot"
    End If
    result = CDbl(0)
    For i = offset To offset + count - 1
        b = nv(i)
        If Not SBWholeNumber(b, 0, 255) Then Err.Raise 5, "SBReadField", "Invalid byte"
        Select Case encoding
            Case "bcd"
                hi = b \ 16 : lo = b Mod 16
                If hi > 9 Or lo > 9 Then Err.Raise 5, "SBReadField", "Invalid BCD"
                result = result * 100 + hi * 10 + lo
            Case "int", "bool"
                result = result * 256 + b
            Case Else
                Err.Raise 5, "SBReadField", "Unsupported encoding"
        End Select
    Next
    If encoding = "bool" Then result = CBool(result <> 0)
    SBReadField = result
End Function

Sub SBValidateSnapshot(s)
    ' Raises before lifecycle/queue use; construction of SBRomSnapshot alone is unchecked.
    Dim i
    If VarType(s.GameOver) <> 11 Then Err.Raise 5, "SBDecode", "Invalid game-over flag"
    If Not SBWholeNumber(s.PlayerCount, 0, 4) Then Err.Raise 5, "SBDecode", "Invalid seat count"
    If Not SBWholeNumber(s.Player, 0, 4) Or Not SBWholeNumber(s.Ball, 0, 9) Then Err.Raise 5, "SBDecode", "Invalid player or ball"
    If Not IsArray(s.Scores) Then Err.Raise 5, "SBDecode", "Missing scores"
    If LBound(s.Scores) <> 0 Or UBound(s.Scores) <> 3 Then Err.Raise 5, "SBDecode", "Exactly four scores required"
    If Not s.GameOver Then
        If s.Player < 1 Or s.Player > s.PlayerCount Or s.Ball < 1 Or s.Ball > 9 Then
            Err.Raise 5, "SBDecode", "Boot or invalid active state"
        End If
    End If
    For i = 0 To 3
        If Not SBWholeNumber(s.Scores(i), 0, CDbl("9999999999")) Then
            Err.Raise 5, "SBDecode", "Unsupported score range"
        End If
    Next
End Sub

' Offline state machine; host decides whether a qualified transport may send.
' Clock is supplied in milliseconds, not wall time. Gap/reset never means finish.
Class SBLifecycle
    Public Active, Armed, EndStableMs, MaxGapMs
    Private previous, lastActive, candidate, candidateAt, lastAt
    Private Sub Class_Initialize()
        EndStableMs = 2000 : MaxGapMs = 2500
        Reset
    End Sub
    Public Sub Reset()
        ' Discard observation history without finishing; rearming requires attract.
        Active = False : Armed = False
        Set previous = Nothing : Set lastActive = Nothing : Set candidate = Nothing
        candidateAt = -1 : lastAt = -1
    End Sub
    Private Function SameState(a, b)
        Dim i
        SameState = False
        If a Is Nothing Then Exit Function
        If b Is Nothing Then Exit Function
        If a.GameOver <> b.GameOver Or a.PlayerCount <> b.PlayerCount Or a.Player <> b.Player Or a.Ball <> b.Ball Then Exit Function
        For i = 0 To 3
            If a.Scores(i) <> b.Scores(i) Then Exit Function
        Next
        SameState = True
    End Function
    Private Function Regressed(s)
        Dim i
        Regressed = False
        If lastActive Is Nothing Then Exit Function
        If s.PlayerCount < lastActive.PlayerCount Then Regressed = True : Exit Function
        For i = 0 To lastActive.PlayerCount - 1
            If s.Scores(i) < lastActive.Scores(i) Then Regressed = True : Exit Function
        Next
    End Function
    Public Function Feed(s, nowMs)
        ' nowMs is monotonic table milliseconds. Returns a transition string;
        ' no network side effects. Invalid snapshots raise instead of advancing.
        Dim wasActive, stable
        SBValidateSnapshot s
        Feed = "none"
        If lastAt >= 0 Then
            If nowMs <= lastAt Or nowMs - lastAt > MaxGapMs Then
                wasActive = Active : Reset
                If wasActive Then Feed = "abort"
                Exit Function
            End If
        End If
        lastAt = nowMs
        stable = SameState(previous, s)
        If Not Active Then
            If s.GameOver Then
                If stable Then Armed = True
            ElseIf Armed Then
                If s.Player <> 1 Or s.Ball <> 1 Then
                    Armed = False
                ElseIf Not previous Is Nothing Then
                    If Not previous.GameOver And previous.PlayerCount = s.PlayerCount And previous.Player = s.Player And previous.Ball = s.Ball Then
                        ' Late attach cannot start: arming requires observed attract first.
                        Active = True : Armed = False : Set lastActive = SBCopySnapshot(s)
                        Feed = "start"
                    End If
                End If
            End If
        ElseIf Regressed(s) Then
            Reset : Feed = "abort" : Exit Function
        ElseIf s.GameOver Then
            If Not SameState(candidate, s) Then
                Set candidate = SBCopySnapshot(s) : candidateAt = nowMs
            ElseIf nowMs - candidateAt >= EndStableMs Then
                Active = False : Armed = True : Set lastActive = Nothing
                Set candidate = Nothing : Feed = "finish"
            End If
        Else
            Set candidate = Nothing : candidateAt = -1
            Set lastActive = SBCopySnapshot(s) : Feed = "update"
        End If
        Set previous = SBCopySnapshot(s)
    End Function
End Class
