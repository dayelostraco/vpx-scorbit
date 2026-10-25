' vpx-scorbit pilot: appended to a staged table script by tools/stage_mm.py.
' Uses the existing Controller instance. No process-memory writes or network calls.
Dim SBRoot, SBFSO, SBRunning, SBLastQR, SBLastError, SBQRShownAt, SBQROption
SBRoot = "@@RUNTIME@@"
SBRunning = False
SBLastQR = ""
SBLastError = ""
SBQROption = 0

Sub SBOptionEvent(eventId)
    ' Historical prototype's manual recall; it does not bypass active-play guards.
    Dim choice
    choice = Table1.Option("Scorbit QR", 0, 1, 1, 0, 0, Array("Auto", "Show again"))
    If eventId = 1 And choice = 1 And SBQROption <> 1 Then SBLastQR = ""
    SBQROption = choice
End Sub

Sub SBStart()
    ' Enable the 500 ms diagnostic file writer using this table's existing controller.
    Set SBFSO = CreateObject("Scripting.FileSystemObject")
    SBRunning = True
    SBQRPanel.Visible = False
    SBSizeDesktopQR SBQRPanel, WindowWidth, WindowHeight
    vpmTimer.AddTimer 500, "SBTick'"
End Sub

Sub SBStop()
    ' Disable polling/display; never tell the optional companion that a game finished.
    SBRunning = False
    SBQRPanel.Visible = False
End Sub

Sub SBTick()
    ' Publish a full snapshot by file rename and refresh local QR display.
    ' This older diagnostic runs file I/O on VPX's timer; it is not the common host.
    If Not SBRunning Then Exit Sub
    Dim nv, parts(), i, f, tmp, dest, qr, signature, seat, timeout, safeToShow
    On Error Resume Next
    nv = Controller.NVRAM
    If Err.Number = 0 And IsArray(nv) Then
        ReDim parts(UBound(nv))
        For i = 0 To UBound(nv)
            parts(i) = Right("0" & Hex(nv(i)), 2)
        Next
        tmp = SBRoot & "\nvram.tmp"
        dest = SBRoot & "\nvram.hex"
        Set f = SBFSO.CreateTextFile(tmp, True)
        f.Write Join(parts, "")
        f.Close
        If SBFSO.FileExists(dest) Then SBFSO.DeleteFile dest
        SBFSO.MoveFile tmp, dest
        qr = SBRoot & "\pair.png"
        timeout = 30
        If Not SBFSO.FileExists(qr) Then
            seat = nv(946)
            qr = SBRoot & "\claim-" & seat & ".png"
            timeout = 15
        End If
        If SBFSO.FileExists(qr) Then
            Set f = SBFSO.GetFile(qr)
            signature = qr & CStr(f.DateLastModified) & CStr(f.Size)
            If signature <> SBLastQR Then
                SBLoadQR SBQRPanel, qr
                If Err.Number = 0 Then
                    SBLastQR = signature
                    SBQRShownAt = Now
                End If
            End If
            ' Claim before launching ball one; never cover active ball play.
            safeToShow = (nv(135) <> 0)
            If timeout = 15 And nv(947) = 1 And nv(946) >= 1 Then
                safeToShow = safeToShow Or (Controller.Switch(18) <> 0 And Controller.Switch(11) = 0)
            End If
            SBQRPanel.Visible = (SBLastQR = signature) And safeToShow And (DateDiff("s", SBQRShownAt, Now) < timeout)
        Else
            SBQRPanel.Visible = False
            SBLastQR = ""
        End If
    End If
    If Err.Number <> 0 Then
        If SBLastError <> Err.Description Then Debug.Print "SCORBIT telemetry: " & Err.Description
        SBLastError = Err.Description
        Set f = SBFSO.CreateTextFile(SBRoot & "\telemetry-error.txt", True)
        f.Write SBLastError
        f.Close
        SBQRPanel.Visible = False
        Err.Clear
    End If
    On Error GoTo 0
    If SBRunning Then vpmTimer.AddTimer 500, "SBTick'"
End Sub

Sub SBLoadQR(panel, imagePath)
    ' Historical WIA pixel-copy experiment; see vbs/qr-desktop.vbs for current bounds.
    Dim qrImage, vector, pixels(), i, x, y, factor, width, height
    Set qrImage = CreateObject("WIA.ImageFile")
    qrImage.LoadFile imagePath
    Set vector = qrImage.ARGBData
    factor = 1
    If qrImage.Width < 256 Then factor = 4
    width = qrImage.Width * factor : height = qrImage.Height * factor
    ReDim pixels(width * height - 1)
    For y = 0 To height - 1
        For x = 0 To width - 1
            pixels(y * width + x) = CLng(vector.Item((y \ factor) * qrImage.Width + (x \ factor) + 1)) And &HFFFFFF
        Next
    Next
    panel.DMD = True
    panel.ImageA = ""
    panel.Color = RGB(255,255,255)
    panel.DMDWidth = width
    panel.DMDHeight = height
    panel.DMDColoredPixels = pixels
End Sub

Sub SBSizeDesktopQR(panel, width, height)
    ' Scale the orthographic backdrop for pixel aspect, not a VR/world-space surface.
    Dim ratio, angle
    If width <= 0 Or height <= 0 Then Exit Sub
    panel.RotX = 0 : panel.RotY = 0 : panel.RotZ = 0
    If width > height Then
        ratio = height / width
        angle = Atn(Sqr(1 - ratio * ratio) / ratio) * 180 / (4 * Atn(1))
        panel.RotY = angle
    ElseIf height > width Then
        ratio = width / height
        angle = Atn(Sqr(1 - ratio * ratio) / ratio) * 180 / (4 * Atn(1))
        panel.RotX = angle
    End If
End Sub
