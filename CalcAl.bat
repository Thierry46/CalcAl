@ECHO off
REM Name ..... : CalcAl.sh
REM Object ... : Launch CalcAl software on UNix systems
REM Parameters : None, -h for help
REM Author ... : MAILLARD Thierry (TMD)
REM Date ..... : 10/3/2015
REM Modif .... :

echo "Start CalcAl ..."
echo "python src/CalcAl.py"
python3 src\CalcAl.py %1
