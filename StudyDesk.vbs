Set objFSO = CreateObject("Scripting.FileSystemObject")
strCurrentDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

Set WshShell = CreateObject("WScript.Shell")
strPythonw = strCurrentDir & "\.venv\Scripts\pythonw.exe"

' Jika .venv belum ada, jalankan setup bat dulu
If Not objFSO.FileExists(strPythonw) Then
    WshShell.Run Chr(34) & strCurrentDir & "\Jalankan_StudyDesk.bat" & Chr(34), 1, True
Else
    strCommand = Chr(34) & strPythonw & Chr(34) & " " & Chr(34) & strCurrentDir & "\main.py" & Chr(34)
    WshShell.Run strCommand, 0, False
End If

Set WshShell = Nothing
Set objFSO = Nothing
