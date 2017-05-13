# -*- coding: utf-8 -*-
"""
This is a setup.py script is generated for py2exe
to build a standalone Windows executable file
with ressources, python and tcl files in ../dist

Ressources are copied out of this script

Date : 14/1/2017

Usage : python setup_win.py py2exe
Used by package_win.bat script
Ref. : http://www.py2exe.org
"""
from distutils.core import setup
import py2exe
setup(windows=['Calcal.py'],
	data_files=[('', ['CalcAl.ini'])],
                options={
                         'py2exe': {
                                    "optimize": 2,
                                    'packages': ['gui', 'database', 'model', 'util']
                        }})
