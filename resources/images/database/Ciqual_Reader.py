# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : Ciqual_Reader
Author : Thierry Maillard (TMD)
Date  : 13/6/2016 - 25/12/2016

Role : Read a Ciqual 2013 or 2016 database from CSV or CSV zipped text file.

Modifications :
- 18/12/2016 : V0.45 : Read Ciqual 2016 CSV file.
- 25/12/2016 : v0.45a : correct pb encoding ligature oe iso8859-1 -> cp1252
************************************************************************************
"""
import logging
import locale
import zipfile
import os
import re

class Ciqual_Reader():
    """ Read a Ciqual 2013 or 2016 database from CSV or CSVzipped text file. """

    def __init__(self, configApp, dirProject, connDB, dbname, typeDatabase):
        """ Initialize a Ciqual database reader
        configApp : ressource .ini for application
        connDB : cursor opened on database to fill
        dbname : name of the database to fill
        typeDatabase : "Ciqual_2013" or "Ciqual_2016"
        """
        self.configApp = configApp
        self.localDirPath = os.path.join(dirProject,
                                         self.configApp.get('Resources', 'LocaleDir'))
        curLocale = locale.getlocale()[0][:2]
        self.localDirPath = os.path.join(self.localDirPath, curLocale)
        self.databaseRefDir = os.path.join(dirProject,
                                            self.configApp.get('Resources', 'ResourcesDir'),
                                            self.configApp.get('Resources', 'DatabaseDir'))

        self.connDB = connDB
        self.dbname = dbname
        if not (typeDatabase.endswith("2013") or typeDatabase.endswith("2016")):
            raise ValueError("Ciqual_Reader : " + _("Ciqual version not supported") + " " +
                             typeDatabase)
        self.typeDatabase = typeDatabase

        self.source = ""
        self.dateSource = self.typeDatabase[-4:]
        self.urlSource = self.configApp.get('Ciqual', 'CiqualUrl')

        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))

    def initDBFromFile(self, pathZipFileInit):
        """ Initialize a database with information read in CSV File or
            zip archive containing this file :
            pathZipFileInit """

        self.logger.info("Database : Initialize new database from " + pathZipFileInit + "...")
        cursor = self.connDB.cursor()

        # Controls how strings are encoded and stored in the database
        cursor.execute('PRAGMA encoding = "UTF-8"')

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products(
                familyName TEXT,
                code INTEGER PRIMARY KEY UNIQUE,
                name TEXT UNIQUE,
                source TEXT,
                dateSource TEXT,
                urlSource TEXT
                )""")
        # Create constituants values table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constituantsValues(
                productCode INTEGER,
                constituantCode INTEGER,
                value REAL,
                qualifValue TEXT
                )""")

        # Source for Ciqual file
        self.source = os.path.basename(pathZipFileInit)

        if pathZipFileInit.endswith(".zip"):
            with zipfile.ZipFile(pathZipFileInit, "r") as zfile:
                with zfile.open(self.configApp.get('Ciqual', 'CiqualCSVFile')) as readfile:
                    self.processFile(readfile, cursor, True)
                readfile.close()
            zfile.close()
        elif pathZipFileInit.endswith(".csv"):
            with open(pathZipFileInit, 'r', encoding='cp1252') as readfile:
                self.processFile(readfile, cursor, False)
            readfile.close()
        else:
            cursor.close()
            raise ValueError("Ciqual_Reader : " + _("Only .zip or .csv files allowed"))

        self.connDB.commit()
        cursor.close()

    def processFile(self, handle, cursor, decode):
        """ Process a file given a handle on it
            Write content in database using cursor
            decode = True if content must be decoded
            # Important : decode read string if it comes from a zipfile !
            Read : https://marcosc.com/2008/12/zip-files-and-encoding-i-hate-you/
            Read : http://stackoverflow.com/questions/539294/how-do-i-determine-file-encoding-in-osx
            file -I ../CIQUALxxx.csv -> text/x-c; charset=iso-8859-1
        """
        dictConstituantsPosition = dict()
        linenum = 0
        namePrec = "" # Pb products name duplicated in Ciqual 2016
        for linebytes in handle:
            linenum = linenum + 1
            # strip pour enlever le CR et NL final
            if decode:
                lineDecoded = linebytes.decode('cp1252')
            else:
                lineDecoded = linebytes
            # strip pour enlever le CR et NL final
            lineSplitted = lineDecoded.strip().split(";")
            if linenum == 1:
                dictConstituantsPosition = self.analyseHeaderCiqual(cursor, lineSplitted)
            elif namePrec != lineSplitted[3]: # Pb products name duplicated in Ciqual 2016
                self.analyseProductCiqual(cursor, lineSplitted,
                                          dictConstituantsPosition)
                namePrec = lineSplitted[3]
            else:
                self.logger.warning("Food name " + namePrec +
                                    " duplicated on line " + str(linenum) +
                                    " in file " + self.source)
        self.logger.info(str(linenum) + " lines read.")

    def analyseHeaderCiqual(self, cursor, headerSplitted):
        """ Analyse header line of Ciqual database """

        # Read shortcuts (short names) for alls components codes
        shortcutsFilePath = os.path.join(self.localDirPath,
                                         self.configApp.get('Resources', 'ComponentsShortcuts'))
        dicoShortcuts = {}
        # Shortcut file is utf-8 encoded, we have to decode it
        # No problem on Mac but problem on non utf-8 systems like Windows
        with open(shortcutsFilePath, 'r', encoding='utf-8') as fileShort:
            for line in fileShort.read().splitlines():
                # Eliminate comment
                posComment = line.find('#')
                if posComment != -1:
                    line = line[:posComment]
                # If valid parameter line, register key and value in dictionary
                param = line.split('=')
                if len(param) == 2:
                    dicoShortcuts[param[0].strip()] = param[1].strip()
        fileShort.close()

        # V0.45 : if Ciqual version 2016 : read components codes not in database
        if self.dateSource == "2016":
            compCodesFilePath = os.path.join(self.databaseRefDir,
                                             self.configApp.get('Ciqual',
                                                                'Cilqual2016Codes4ComponentsFilePath'))
            dicoCompCodes = {}
            # ComponantsCodes file is utf-8 encoded, we have to decode it
            # No problem on Mac but problem on non utf-8 systems like Windows
            with open(compCodesFilePath, 'r', encoding='utf-8') as fileCompCodes:
                for line in fileCompCodes.read().splitlines():
                    # Eliminate comment
                    posComment = line.find('#')
                    if posComment != -1:
                        line = line[:posComment]
                    # If valid parameter line, register key and value in dictionary
                    param = line.split(';')
                    if len(param) == 2:
                        dicoCompCodes[param[0].strip()] = param[1].strip()
            fileCompCodes.close()

        numField = 0
        # Check 4 first fields
        FirstFieldsCiqualFile = self.configApp.get('Ciqual', 'FirstFieldsCiqualFile').split(";")
        for fieldName in FirstFieldsCiqualFile:
            readField = headerSplitted[numField]
            if readField != fieldName:
                raise ValueError(_("Ciqual file : invalid header field") + " " +  str(numField+1) +
                                 " : " + readField + " " + _("instead of") +
                                 " " + fieldName)
            numField = numField + 1

        # Create constituants in database
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS constituantsNames(
                code INTEGER PRIMARY KEY UNIQUE,
                name TEXT,
                unit TEXT,
                shortcut TEXT
                )""")

        # Record constituants names table
        # Regular expression for data extraction
        if self.dateSource == "2013":
            regexpConstituant = re.compile(r'^(?P<codeConstituant>\d{1,5}) ' +
                                           r'(?P<nameConstituant>.*?)' +
                                           r' \((?P<unitConstituant>[µmk]?[Jgc][a]?[l]?)/100g\)$')
        else:
            regexpConstituant = re.compile(r'^(?P<nameConstituant>.*?)' +
                                           r' \((?P<unitConstituant>[µmk]?[Jgc][a]?[l]?)/100g\)$')
        constituants = []
        dictConstituantsPosition = dict()
        for constituantDescription in headerSplitted[numField:]:
            match = regexpConstituant.search(constituantDescription)
            nameConstituant = match.group('nameConstituant')
            unitConstituant = match.group('unitConstituant')
            if match:
                if self.dateSource == "2013":
                    code = match.group('codeConstituant')
                else:
                    code = dicoCompCodes[constituantDescription]
                constituants.append((code, nameConstituant, unitConstituant, dicoShortcuts[code]))
                dictConstituantsPosition[numField] = code
                numField = numField + 1
            else:
                raise ValueError(_("Ciqual file : invalid header field") + " " +
                                 str(numField+1) +
                                 " : " + constituantDescription)
        cursor.executemany("""
                            INSERT INTO constituantsNames(code, name, unit, shortcut)
                            VALUES(?, ?, ?, ?)
                            """,
                           constituants)

        self.logger.info(str(len(constituants)) + " constituants available.")
        return dictConstituantsPosition

    def analyseProductCiqual(self, cursor, productSplitted,
                             dictConstituantsPosition):
        """ Analyse product line of Ciqual database """

        # Uncomment 2 next lines to create demo database (Ciqual 2013)
        #if "enquêtes Inca" not in productSplitted[1]:
        #    return

        # Record product in database
        productCode = productSplitted[2]
        # v0.30 : Suppress double quotes in familyName
        familyName = productSplitted[1].replace('"', '')
        cursor.execute("""
                       INSERT INTO products(familyName, code, name, source, dateSource, urlSource)
                       VALUES(?, ?, ?, ?, ?, ?)
                       """,
                       (familyName, productCode, productSplitted[3],
                        self.source, self.dateSource, self.urlSource))

        # Record constituants values in database
        numField = 4
        for constituantValue in productSplitted[numField:]:
            qualifValue = ""
            if constituantValue == '-':
                value = 0.0
                qualifValue = "-"
            elif constituantValue == 'traces':
                value = 0.0
                qualifValue = "T"
            elif constituantValue.startswith('< '):
                constituantValue = constituantValue.replace('< ', '')
                value = float(constituantValue.replace(',', '.'))
                qualifValue = '<'
            else:
                value = float(constituantValue.replace(',', '.'))
                qualifValue = 'N'
            # V0.28 : Don't Register components with value not defined
            if constituantValue != '-':
                cursor.execute("""INSERT INTO constituantsValues(productCode, constituantCode,
                                                             value, qualifValue)
                              VALUES(?, ?, ?, ?)""",
                               (productCode, dictConstituantsPosition[numField],
                                value, qualifValue))
            numField = numField + 1
