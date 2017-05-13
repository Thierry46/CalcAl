#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
************************************************************************************
program : CalcAl
Author : Thierry Maillard (TMD)
Date : 10/3/2016 - 3/12/2016

Object : Food Calculator based on CIQUAL Tables.
    https://pro.anses.fr/tableciqual

Options :
    -h ou --help : Display this help message.
    -d ou --debug : Verbose mode when starting
    -b ou --baseDirPath=path : path for databases shared by users
                     on a computer or a network

Paramèters : None.

Licence : GPLv3
Copyright (c) 2016 - Thierry Maillard


This file is part of CalcAl project.

CalcAl project is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CalcAl project is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CalcAl project.  If not, see <http://www.gnu.org/licenses/>.
************************************************************************************
"""
import sys
import getopt
import gettext
import configparser
import platform
import locale
import os
import os.path
import shutil
import logging
from logging.handlers import RotatingFileHandler
import getpass

from tkinter import TkVersion

from database import DatabaseManager
from gui import CalcAlGUI

##################################################
# main function
##################################################
def main(argv=None):
    """
    Get options, set logging system and launch GUI
    """
    isModeDebug = False
    isPathDBSet = False
    baseDirPath = ""
    #############################
    # Analyse des arguments reçus
    #############################
    if argv is None:
        argv = sys.argv

        # parse command line options
    try:
        opts, args = getopt.getopt(argv[1:], "hdb:", ["help", "debug", "baseDirPath="])
    except getopt.error as msg:
        print(msg)
        print("to get help : --help ou -h", file=sys.stderr)
        sys.exit(1)

    # process options
    progName = sys.argv[0]
    dirProject = os.path.dirname(os.path.abspath(sys.argv[0]))
    for option, arg in opts:
        if option in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        if option in ("-d", "--debug"):
            isModeDebug = True
            print("Debug mode : verbose.")
        if option in ("-b", "--baseDirPath"):
            isPathDBSet = True
            baseDirPath = arg.strip()
            print("Path for database set to ", baseDirPath)

    # Read configuration properties
    fileConfigApp = os.path.join(dirProject, 'CalcAl.ini')
    if not os.path.isfile(fileConfigApp):
        print("Unable to locate config file :", fileConfigApp)
        sys.exit(2)

    configApp = configparser.RawConfigParser()
    configApp.read(fileConfigApp, encoding="utf-8")

    # Set local : country, region and encoding
    setLocaleCalcal(configApp, dirProject)

    # No parameter
    if len(args) > 0:
        print(__doc__)
        print(_("Error : 0 parameter allowed" + " !"))
        sys.exit(1)

    # Get user workdir for loging system
    homeUser = os.path.expanduser("~")
    if platform.system() == 'Darwin': # On Mac
        homeUser = os.path.join(homeUser, "Documents")
    homeCalcAl = os.path.join(homeUser, configApp.get('Resources', 'AppDataDir'))
    if not os.path.exists(homeCalcAl):
        os.mkdir(homeCalcAl)
        print(_("Directory created") + " :", homeCalcAl)

    # Start logging message system
    initLogging(configApp, homeCalcAl, isModeDebug)
    logger = logging.getLogger(configApp.get('Log', 'LoggerName'))

    # Welcome and configuration messages
    idProg = configApp.get('Version', 'AppName') + ' - version ' + \
             configApp.get('Version', 'Number') + ' du ' + \
             configApp.get('Version', 'Date')
    logger.info(_("Starting") + " " + progName + " : " + idProg)
    welcomeMsg = _("Thanks to you") + " " + getpass.getuser() + " " + \
                 _("for using this software") + " !"
    logger.info(welcomeMsg)
    emails = configApp.get('Version', 'EmailSupport1')  + ", " +\
             configApp.get('Version', 'EmailSupport2')
    logger.info(_("To contact authors") + " : " + emails)
    logger.info(_("On") + " : " + platform.system() + ", " + platform.release() + ", " +
                "Python : " + platform.python_version() + ", Tk : " + str(TkVersion))
    logger.info(_("Detected language and encoding on this computer") + " = " +
                str(locale.getlocale()))

    # Init database path and user demo database
    if not isPathDBSet:
        baseDirPath = os.path.join(homeCalcAl,
                                   configApp.get('Resources', 'DatabaseDir'))
    if not os.path.exists(baseDirPath):
        os.mkdir(baseDirPath)
        logger.info(_("Directory created") + " :" + baseDirPath)
    pathDBDemoSvg = os.path.join(dirProject,
                                 configApp.get('Resources', 'ResourcesDir'),
                                 configApp.get('Resources', 'DatabaseDir'),
                                 configApp.get('Resources', 'DemoDatabaseName'))
    pathDBDemo = os.path.join(baseDirPath,
                              configApp.get('Resources', 'DemoDatabaseName'))
    if not os.path.exists(pathDBDemo):
        shutil.copyfile(pathDBDemoSvg, pathDBDemo)
        logger.info(_("Demo DB copied") + " :" + pathDBDemo)

    # Init database manager
    databaseManager = DatabaseManager.DatabaseManager(configApp, dirProject, baseDirPath)

    # Launch GUI
    CalcAlGUI.CalcAlGUI(configApp, dirProject, databaseManager).mainloop()

    logger.info(_("End of") + " " + progName + " : " + idProg)
    logging.shutdown() # Terminaison of logging system

def initLogging(configApp, homeCalcAl, isModeDebug):
    """ Start logging message system """
    logDir = os.path.join(homeCalcAl, configApp.get('Log', 'DirLog'))
    if not os.path.isdir(logDir):
        os.mkdir(logDir)
        print(_("Directory created") + " :", logDir)
    logFileName = configApp.get('Log', 'BaseLogFileName')
    pathLogFileName = os.path.join(logDir, logFileName)
    print(_("Messages now logged in") + " " + pathLogFileName)
    logger = logging.getLogger(configApp.get('Log', 'LoggerName'))
    if isModeDebug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
    fileHandler = RotatingFileHandler(pathLogFileName, 'a',
                                      configApp.getint('Log', 'MaxBytes'), 1)
    fileHandler.setLevel(logging.DEBUG)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    streamHandler = logging.StreamHandler()
    if isModeDebug:
        streamHandler.setLevel(logging.DEBUG)
    else:
        streamHandler.setLevel(logging.WARNING)
    logger.addHandler(streamHandler)

def setLocaleCalcal(configApp, dirProject):
    """ V0.35 :Set local : country, region and encoding
        Big source of bugs and problems on many platform !
        locale is used by gettext package to set messages language
        and by database init files readers.
        I18N settings.
        """
    # Set locale by getting User language and encoding
    # This sets the locale for all categories to the user’s default setting
    # Decimal separator is still . (point)
    # Nowdays, french users don't see any advantage to use , (comma)
    # else it would be possible by using locale fucnction instead float(), str(), format()
    # see : https://docs.python.org/3/library/locale.html#locale.format
    # https://docs.python.org/3/library/locale.html
    # Ref : chapt. 23.2.1. Background, details, hints, tips and caveats

    locale.setlocale(locale.LC_ALL, '')

    # For problem of getting locale in an Mac app Bundle :
    # http://stackoverflow.com/questions/4719789/how-can-you-get-the-system-default-language-locale-in-a-py2app-packaged-python
    # locale.setlocale(locale.LC_ALL, '') detect and return "C"
    # because usuually terminal or shell set LANG
    # Here we set LANG explicitely and call again locale.setlocale(locale.LC_ALL, '')
    # to redetect local
    if not locale.getlocale()[0]:
        os.environ['LANG'] = \
                  configApp.get('DefaultLocale', 'DefaultLanguageCode') + "." + \
                  configApp.get('DefaultLocale', 'DefaultEncodingCode')
        locale.setlocale(locale.LC_ALL, '')

    # i18n : Internationalization for GUI
    localeDirPath = os.path.join(dirProject, configApp.get('Resources', 'LocaleDir'))
    # This installs the function _() in Python’s builtins namespace
    if platform.system() == 'Windows':
        # V0.32 : Hack on Windows : ref http://python.zirael.org/e-localization4.html
        os.environ['LANG'] = locale.getlocale()[0]
    gettext.install("messages", localeDirPath)


##################################################
#to be called as a script
if __name__ == "__main__":
    main()
    sys.exit(0)
