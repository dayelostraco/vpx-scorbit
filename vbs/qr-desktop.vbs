 ' Desktop backdrop is orthographic: z is discarded by VPX. These rotations
' scale one axis without perspective, producing square pixels at any aspect.
Sub SBSizeDesktopQR(panel, width, height)
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

Sub SBLoadQR(panel, imagePath)
    ' Load a trusted local helper/test image via WIA and copy nearest-neighbor pixels.
    ' Bounds protect our expansion, not WIA's initial decode; no URI trust is inferred.
    Dim qrImage, vector, pixels(), i, x, y, factor, width, height
    Set qrImage = CreateObject("WIA.ImageFile")
    qrImage.LoadFile imagePath
    If qrImage.Width < 21 Or qrImage.Width > 1024 Or qrImage.Height <> qrImage.Width Then
        Err.Raise 5, "SBLoadQR", "Expected bounded square QR image"
    End If
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
