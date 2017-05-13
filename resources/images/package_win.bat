@ECHO off
REM Name ..... : Package_win.bat
REM Object ... : Package CalcAl software on Windows systems
REM              Build a Calcal.exe and its resources in a dist derectory
REM Parameters : None, -h for help
REM Author ... : MAILLARD Thierry (TMD)
REM Date ..... : 10-14/1/2017
REM Prerequisites :
REM - Install python 3.4 : today version highter than 3.4 is not supported by py2exe
REM = Install py2exe : python -m pip install py2exe
REM Use Inno Setup to package app : http://www.jrsoftware.org/isinfo.php
REM innosetup-5.5.9-unicode.exe
REM To createz installation script, wizard was used
REM Welcome : create new script file using wizard....
REM Modif .... :

REM Convert EOL terminator to MS-DOS standard :
REM With Notepad++,  File / EOL termination / MS-DOS + Save

echo "Erase dist directory ..."
rmdir /S /Q dist
 
echo "Create CalcAl.exe ..."
python setup_win.py py2exe

echo "Delete demos files in dist to light distribution ..."
REM http://stackoverflow.com/questions/3900375/understanding-what-files-in-the-tcl-are-required-for-distributing-frozen-python
rmdir /S /Q dist\tcl\tix8.4.3\demos
rmdir /S /Q dist\tcl\tk8.6\demos

REM Do it here because setup.py can only copy one file but not directory containig files
REM Else : must detail all files in python script.
REM It's simpler to do it in this DOS .bat
REM Use robocopy instead xcopy because xcopy is deprecated on Windows 7.
REM So XP is not supported.
echo  "Copy resources files ..."
robocopy /njh /njs /ndl /nc /ns /E locale dist\locale
robocopy /njh /njs /ndl /nc /ns /E resources dist\resources 

REM Use Inno Setup to package app : http://www.jrsoftware.org/isinfo.php
REM innosetup-5.5.9-unicode.exe
REM Welcome : create new script file using wizard.
REM Installer OK
echo "Run installer compiler..."
"C:\Program Files\Inno Setup 5\ISCC" calcal.iss
dir ..\calcal*setup.exe

echo "Launch installer to test it."
echo "Stop this script if problem"
PAUSE

echo "Clean building directory"
rmdir /S /Q dist

echo "package_win.bat : END"
