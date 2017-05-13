@ECHO off
REM Name ..... : CalcAl.bat
REM Object ... : Launch CalcAl software on Windows systems
REM Parameters : None, -h for help
REM Author ... : MAILLARD Thierry (TMD)
REM Date ..... : 8/5/2015 - 24/9/2016
REM Modif .... :

REM Convert EOL terminator to MS-DOS standard :
REM With Notepad++,  File / EOL termination / MS-DOS + Save

echo "Start CalcAl ..."
echo "python %~dp0\CalcAl.py"
REM if error or problem detecting locale in Calcal, uncomment next line
REM set LANG=fr_FR.cp1252
python %~dp0\CalcAl.py %1
