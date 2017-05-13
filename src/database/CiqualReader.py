# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : DatabaseReaderFactory
Author : Thierry Maillard (TMD)
Date  : 13/6/2016

Role : Read a Ciqual 2013 database from CSVzipped text file.
************************************************************************************
"""
import logging
import zipfile
import os
import re

class CiqualReader():

    def __init__(self, configApp, localDirPath, connDB, dbname):
        """ Initialize a Ciqual database by reading a CSV File
        configApp : ressource .ini for application
        connDB : cursor opened on database to fill
        dbname : name of the database to fill
        """
        self.configApp = configApp
        self.localDirPath = localDirPath
        self.connDB = connDB
        self.dbname = dbname
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))

    def initDBFromFile(self, pathZipFileInit):
        """ Initialize a database with information read in CSV File
            pathZipFileInit """

        # Source for Ciqual file
        source = self.configApp.get('Resources', 'CiqualCSVFile')
        dateSource = self.configApp.get('Resources', 'CiqualCSVFileDate')
        urlSource = self.configApp.get('Resources', 'CiqualUrl')
        dictConstituantsPosition = dict()

        self.logger.info("Database : Initialize new database from " + pathZipFileInit + "...")
        linenum = 0
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
        # Create constitiants values table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constituantsValues(
                productCode INTEGER,
                constituantCode INTEGER,
                value REAL,
                qualifValue TEXT
                )""")

        cursor.execute("""
                CREATE TABLE IF NOT EXISTS compositionProducts(
                    productCode INTEGER,
                    productCodeCiqual INTEGER,
                    quantityPercent REAL
                    )""")

        with zipfile.ZipFile(pathZipFileInit, "r") as zfile:
            with zfile.open(source) as readfile:
                for linebytes in readfile:
                    linenum = linenum + 1
                    # Important : decoder la chaine lue !
                    # Read : https://marcosc.com/2008/12/zip-files-and-encoding-i-hate-you/
                    # Read : http://stackoverflow.com/questions/539294/how-do-i-determine-file-encoding-in-osx
                    # file -I ../CIQUAL2013-Donneescsv.csv -> text/x-c; charset=iso-8859-1
                    # strip pour enlever le CR et NL final
                    lineSplitted = linebytes.decode('iso8859_1').strip().split(";")
                    if linenum == 1:
                        dictConstituantsPosition = self.analyseHeaderCiqual(cursor,lineSplitted)
                    else:
                        self.analyseProductCiqual(cursor,lineSplitted, linenum,
                                                  source, dateSource, urlSource,
                                                  dictConstituantsPosition)

            readfile.close()
        zfile.close()

        self.connDB.commit()
        cursor.close()
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
        fileShort.closed

        numField = 0
        # Check 4 first fields
        FirstFieldsCiqualFile = self.configApp.get('Resources', 'FirstFieldsCiqualFile').split(";")
        for fieldName in FirstFieldsCiqualFile :
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
        self.regexpConstituant = re.compile(r'^(?P<codeConstituant>\d{1,5}) ' +
                                    r'(?P<nameConstituant>.*?)' +
                                    r' \((?P<unitConstituant>[µmk]?[Jgc][a]?[l]?)/100g\)$')
        constituants = []
        dictConstituantsPosition = dict()
        for constituantDescription in headerSplitted[numField:]:
            match = self.regexpConstituant.search(constituantDescription)
            if match:
                code = match.group('codeConstituant')
                constituants.append((code,
                                     match.group('nameConstituant'),
                                     match.group('unitConstituant'),
                                     dicoShortcuts[match.group('codeConstituant')]))
                dictConstituantsPosition[numField] = code
                numField = numField + 1
            else:
                raise ValueError(_("Ciqual file : invalid header field") + " " +
                                  str(numField1+1) +
                                  " : " + constituantDescription)
        cursor.executemany("""
                        INSERT INTO constituantsNames(code, name, unit, shortcut)
                        VALUES(?, ?, ?, ?)
                        """,
                        constituants)

        self.logger.info(str(len(constituants)) + " constituants available.")
        return dictConstituantsPosition

    def analyseProductCiqual(self, cursor, productSplitted, linenum,
                             source, dateSource, urlSource,
                             dictConstituantsPosition):
        """ Analyse product line of Ciqual database """

        # Record product in database
        productCode = productSplitted[2]
        cursor.execute("""
                       INSERT INTO products(familyName, code, name, source, dateSource, urlSource)
                       VALUES(?, ?, ?, ?, ?, ?)
                       """,
                       (productSplitted[1], productCode, productSplitted[3],
                        source, dateSource, urlSource))

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
            cursor.execute("""INSERT INTO constituantsValues(productCode, constituantCode,
                                                             value, qualifValue)
                              VALUES(?, ?, ?, ?)""",
                               (productCode, dictConstituantsPosition[numField],
                                value, qualifValue))
            numField = numField + 1
