#!/bin/sh
# Name ..... : CalcAl.sh
# Object ... : Launch CalcAl software on UNix systems
# Parameters : None, -h for help
# Author ... : MAILLARD Thierry (TMD)
# Date ..... : 10/3/2015
# Modif .... :

CalcalPath="/Applications/education/CalcAl"

echo "Start CalcAl ..."
echo "python3 src/CalcAl.py"
# Use locale -a to find all local installed on your system
#export LANG=en_US.UTF-8
python3 ${CalcalPath}/src/CalcAl.py $1