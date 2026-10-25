' Shared legacy /api/entry/ payload queue. Does not perform network I/O.
' A transport must acknowledge the exact sequence only after HTTP success.
Class SBEntryQueue
    Private messages, nextSequence, nextId, sessionId, startedAt, closed, initialized, sessionFirstId
    Private Sub Class_Initialize()
        Set messages = CreateObject("Scripting.Dictionary")
        initialized = False : closed = True : nextId = 0
    End Sub
    Public Property Get Count()
        ' Includes retained entries from completed games awaiting acknowledgment.
        Count = messages.Count
    End Property
    Public Property Get IsClosed()
        ' True means no open local game, not that all queued messages were uploaded.
        IsClosed = closed
    End Property
    Public Sub Begin(id, nowMs, snapshot)
        ' Start a game with a caller-generated identity and millisecond clock.
        ' Pending older finished games may remain; a second open game is rejected.
        Dim pattern
        If initialized And Not closed Then Err.Raise 5, "SBEntryQueue", "Previous session still open"
        If messages.Count >= 64 Then Err.Raise 5, "SBEntryQueue", "Offline backlog full"
        Set pattern = New RegExp
        pattern.Pattern = "^[a-zA-Z0-9-]{32,36}$"
        If Not pattern.Test(id) Then Err.Raise 5, "SBEntryQueue", "Invalid session identifier"
        SBValidateSnapshot snapshot
        sessionId = id : startedAt = nowMs : nextSequence = 0 : sessionFirstId = nextId
        initialized = True : closed = False
        Append snapshot, nowMs, False
    End Sub
    Public Sub Update(snapshot, nowMs)
        ' Keep latest validated scores; coalescing may leave transmitted sequence gaps.
        If Not initialized Or closed Then Err.Raise 5, "SBEntryQueue", "No open session"
        SBValidateSnapshot snapshot
        ' Bound backlog by coalescing only a never-dispatched ordinary update.
        ' Head is immutable even while a transport retries it; start/final survive.
        If messages.Count >= 2 Then
            Dim keys, tail
            keys = messages.Keys : tail = keys(UBound(keys))
            If tail > sessionFirstId Then messages.Remove tail
        End If
        Append snapshot, nowMs, False
    End Sub
    Public Sub Finish(snapshot, nowMs)
        ' Close only the local session; server acceptance still requires an ACK.
        If Not initialized Or closed Then Err.Raise 5, "SBEntryQueue", "No open session"
        SBValidateSnapshot snapshot
        ' Retain final scores and finish together, regardless of an in-flight head.
        Append snapshot, nowMs, True
        closed = True
    End Sub
    Public Sub Abort()
        ' Deliberately no synthetic completed-game message on disconnect/reset.
        ' Preserve completed older games waiting for acknowledgement.
        Dim key
        If initialized And Not closed Then
            For Each key In messages.Keys
                If key >= sessionFirstId Then messages.Remove key
            Next
        End If
        closed = True : initialized = False
    End Sub
    Public Property Get HeadSequence()
        ' Local immutable message ID, not the per-game session_sequence sent to Scorbit.
        Dim keys
        If messages.Count = 0 Then Err.Raise 5, "SBEntryQueue", "Empty queue"
        keys = messages.Keys : HeadSequence = keys(0)
    End Property
    Public Property Get HeadBody()
        ' Return the same form body until that exact head is acknowledged or aborted.
        HeadBody = messages(HeadSequence)
    End Property
    Public Sub Acknowledge(sequence)
        ' Remove only the current head; caller must validate HTTP/application success.
        If sequence <> HeadSequence Then Err.Raise 5, "SBEntryQueue", "Out-of-order acknowledgement"
        messages.Remove sequence
    End Sub
    Private Sub Append(snapshot, nowMs, final)
        Dim body, i, ball, player, active
        If nowMs < startedAt Then Err.Raise 5, "SBEntryQueue", "Clock reset"
        active = "true" : ball = snapshot.Ball : player = snapshot.Player
        If final Then active = "false" : ball = -1 : player = -1
        body = "session_uuid=" & sessionId & "&session_time=" & (nowMs-startedAt+1) & _
            "&session_sequence=" & nextSequence & "&active=" & active
        For i = 0 To snapshot.PlayerCount - 1
            body = body & "&current_p" & (i+1) & "_score=" & CStr(snapshot.Scores(i))
        Next
        body = body & "&current_ball=" & ball & "&current_player=" & player
        messages.Add nextId, body
        nextId = nextId + 1
        nextSequence = nextSequence + 1
    End Sub
End Class
