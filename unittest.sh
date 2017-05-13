#!/bin/sh
# Name ..... : unittest.sh
# Object ... : Launch CalcAl unit tests software on Unix-like systems
# Parameters : None, -h for help
# Author ... : MAILLARD Thierry (TMD)
# Date ..... : 27/10/2016
# Modif .... :
# Prerequisite : Pytest installed
#   sudo python3 -m pip install -U pytest

echo "Start CalcAl unittest..."
echo "python3 CalcAl.py"
python3 -m pytest unittest
