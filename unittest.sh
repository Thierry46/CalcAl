#!/bin/sh
# Name ..... : unittest.sh
# Object ... : Launch CalcAl unit tests software on Unix-like systems
# Parameters : -s to display stdout or other pytest parameters
# See python -m pytest -h for more options
# Author ... : MAILLARD Thierry (TMD)
# Date ..... : 27/10/2016
# Modif .... : 14/02/2018 : parameters allowed and transmitted to pytest
# Prerequisite : Pytest installed
#   sudo python3 -m pip install -U pytest

echo "Start CalcAl unittest..."
python3 -m pytest unittest $*
