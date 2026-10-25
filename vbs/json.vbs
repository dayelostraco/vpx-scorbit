' Small strict JSON reader; never evaluates server responses as script.
Class SBJsonValue
    Public Kind, Scalar, Children
End Class

Class SBJsonReader
    Private source, pos, depth
    Public Function Parse(text)
        ' Return a fresh typed tree or raise; no script evaluation or schema validation.
        ' Bound work on the VPX timer thread before copying/parsing a response.
        If Len(text) > 65536 Then Fail
        source = text : pos = 1 : depth = 0
        Set Parse = ReadNode()
        SkipSpace
        If pos <= Len(source) Then Fail
    End Function
    Private Sub Fail()
        Err.Raise 5, "SBJsonReader", "Invalid JSON"
    End Sub
    Private Sub SkipSpace()
        Do While pos <= Len(source)
            If InStr(" " & vbTab & vbCr & vbLf, Mid(source, pos, 1)) = 0 Then Exit Do
            pos = pos + 1
        Loop
    End Sub
    Private Function ReadString()
        Dim result, c, escape, digits, rx
        If Mid(source, pos, 1) <> Chr(34) Then Fail
        pos = pos + 1 : result = ""
        Do While pos <= Len(source)
            c = Mid(source, pos, 1) : pos = pos + 1
            If c = Chr(34) Then ReadString = result : Exit Function
            If c = "\" Then
                escape = Mid(source, pos, 1) : pos = pos + 1
                Select Case escape
                    Case Chr(34), "\", "/": c = escape
                    Case "b": c = Chr(8)
                    Case "f": c = Chr(12)
                    Case "n": c = vbLf
                    Case "r": c = vbCr
                    Case "t": c = vbTab
                    Case "u"
                        digits = Mid(source, pos, 4)
                        Set rx = New RegExp : rx.Pattern = "^[0-9a-fA-F]{4}$"
                        If Not rx.Test(digits) Then Fail
                        c = ChrW(CLng("&H" & digits)) : pos = pos + 4
                    Case Else: Fail
                End Select
            ElseIf AscW(c) >= 0 And AscW(c) < 32 Then
                Fail
            End If
            result = result & c
        Loop
        Fail
    End Function
    Private Function ReadNode()
        Dim node, c, key, child, ending, number, rx, matches
        depth = depth + 1
        If depth > 32 Then Fail
        SkipSpace
        Set node = New SBJsonValue
        c = Mid(source, pos, 1)
        Select Case c
            Case "{", "["
                If c = "{" Then node.Kind = "object" : ending = "}" Else node.Kind = "array" : ending = "]"
                Set node.Children = CreateObject("Scripting.Dictionary")
                pos = pos + 1 : SkipSpace
                If Mid(source, pos, 1) <> ending Then
                    Do
                        SkipSpace
                        If node.Kind = "object" Then
                            key = ReadString() : SkipSpace
                            If Mid(source, pos, 1) <> ":" Then Fail
                            pos = pos + 1
                        Else
                            key = node.Children.Count
                        End If
                        If node.Children.Exists(key) Then Fail
                        Set child = ReadNode()
                        node.Children.Add key, child
                        SkipSpace
                        c = Mid(source, pos, 1)
                        If c = ending Then Exit Do
                        If c <> "," Then Fail
                        pos = pos + 1
                    Loop
                End If
                pos = pos + 1
            Case Chr(34)
                node.Kind = "string" : node.Scalar = ReadString()
            Case "t"
                If Mid(source, pos, 4) <> "true" Then Fail
                node.Kind = "boolean" : node.Scalar = True : pos = pos + 4
            Case "f"
                If Mid(source, pos, 5) <> "false" Then Fail
                node.Kind = "boolean" : node.Scalar = False : pos = pos + 5
            Case "n"
                If Mid(source, pos, 4) <> "null" Then Fail
                node.Kind = "null" : node.Scalar = Null : pos = pos + 4
            Case Else
                Set rx = New RegExp
                rx.Pattern = "^-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?"
                Set matches = rx.Execute(Mid(source, pos))
                If matches.Count <> 1 Then Fail
                number = matches(0).Value
                ' Preserve JSON numeric text; callers validate expected integer range.
                node.Kind = "number" : node.Scalar = number : pos = pos + Len(number)
        End Select
        depth = depth - 1
        Set ReadNode = node
    End Function
End Class
