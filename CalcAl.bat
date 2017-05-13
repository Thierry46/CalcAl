@ECHO off
REM Name ..... : CalcAl.bat
REM Object ... : Launch CalcAl software on Windows systems
REM Parameters : None, -h for help
REM Author ... : MAILLARD Thierry (TMD)
REM Date ..... : 8/5/2015
REM Modif .... :

echo "Start CalcAl ..."
echo "python src/CalcAl.py"
REM if error in Calcal detecting locale, set LANG=fr_FR.cp1252
python src\CalcAl.py %1
