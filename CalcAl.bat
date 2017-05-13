@ECHO off
REM Name ..... : CalcAl.bat
REM Object ... : Launch CalcAl software on Windows systems
REM Parameters : None, -h for help
REM Author ... : MAILLARD Thierry (TMD)
REM Date ..... : 8/5/2015 - 29/5/2016
REM Modif .... :

echo "Start CalcAl ..."
echo "python %~dp0\src\CalcAl.py"
REM if error in Calcal detecting locale, set LANG=fr_FR.cp1252
python %~dp0\src\CalcAl.py %1
