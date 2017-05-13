# -*- coding: utf-8 -*-
"""
Role : Parameters for generation of calcal Software on Mac with py2app
This is a setup.py script is generated by py2applet
Ref : doc/packaging.txt

py2applet --make-setup --force-system-tk --report-missing-from-imports \
Calcal.py --iconfile resources/images/logo_calcal.icns \
--resources CalcAl.ini,locale,resources \
—-packages database,gui,model

Modified by TMD :
- Add encoding at the top
- Correct OPTIONS

Requirement :
Install Pip : Ref : https://pypi.python.org/pypi/pip
curl -O https://raw.githubusercontent.com/pypa/pip/master/contrib/get-pip.py
su
cd /Users/thierry/Documents/informatique/logiciels/python/python3
python3 get-pip.py

Install p2app :
sudo python3 -m pip install py2app

Date : 8/10/2016 - 14/1/2017

Usage : python3 setup.py py2app
Used by package_mac.sh
"""

from setuptools import setup

APP = ['Calcal.py']
APP_NAME = 'Calcal'
DATA_FILES = ['CalcAl.ini', 'locale', 'resources', 'gui', 'database', 'model']

##################################################
# To choose type distribution
# 'semi_standalone': True
#   for light distribution 1 Mo instead of 6 Mo
#   but python3.5 must be installed on target computer
#   If false , executable don't need python and tcl to be
#	already installed on conputer
##################################################
OPTIONS = {'argv_emulation': True,
           'force_system_tk': True,
           'packages' : ['gui', 'database', 'model'],
           'iconfile' : 'resources/images/logo_calcal.icns',
           'report_missing_from_imports' : True,
           'semi_standalone' : False,
           'plist': {'CFBundleName' : APP_NAME,
                     'CFBundleDisplayName' : APP_NAME,
                     'CFBundleGetInfoString' : "Food calculator",
                     'CFBundleIdentifier' : "fr.pagesperso-orange.maillard.thierry",
                     'CFBundleVersion' : "0.1.0",
                     'CFBundleShortVersionString' : "VERSION_NUMBER",
                     'NSHumanReadableCopyright' : u"Copyleft © 2016, Thierry Maillard, GNU GPL"}}

setup(app=APP,
      data_files=DATA_FILES,
      options={'py2app': OPTIONS},
      setup_requires=['py2app'])