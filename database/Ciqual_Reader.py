# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : Ciqual_Reader
Author : Thierry Maillard (TMD)
Date  : 13/6/2016 - 18/2/2017

Role : Read a Ciqual 2017 database from .xls (Excel 97) file.

Note : To import older database (.csv file), use a version of CalcAl <= 0.53

Modifications :
- 18/12/2016 : V0.45 : Read Ciqual 2016 CSV file.
- 25/12/2016 : v0.45a : correct pb encoding ligature oe iso8859-1 -> cp1252
- 18/2/2017 : V0.54 : Support new xls format for ANSES CIQUAL Database

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
import logging
import locale
import os
import re

class Ciqual_Reader():
    """ Read a Ciqual 2013 or 2016 database from CSV or CSVzipped text file. """

    def __init__(self, configApp, dirProject, connDB, dbname, typeDatabase):
        """ Initialize a Ciqual database reader
        configApp : ressource .ini for application
        dirProject : installation directory name of the software
        connDB : cursor opened on database to fill
        dbname : name of the database to fill
        typeDatabase : "Ciqual_2017"
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

        if not typeDatabase.endswith("2017"):
            raise ValueError("Ciqual_Reader : " + _("Ciqual version not supported") + " " +
                             typeDatabase)
        self.typeDatabase = typeDatabase

        self.source = ""
        self.dateSource = self.typeDatabase[-4:]
        self.urlSource = self.configApp.get('Ciqual', 'CiqualUrl')

        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))

        if self.configApp.getboolean('Ciqual', 'getOnlyAlimentMoyen'):
            self.logger.warning(_("Warning : getOnlyAlimentMoyen mode !"))

    def initDBFromFile(self, pathXlsFileInit):
        """ Initialize a database with information read in an .xls (Excel 97) file :
            pathXlsFileInit """
 
        self.logger.debug("Ciqual_Reader : Initialize new database from %s ...", pathXlsFileInit)
        if not pathXlsFileInit.endswith(".xls"):
            raise ValueError("Ciqual_Reader : " + _("Only .xls files allowed") + " : " +
                             pathXlsFileInit)
        if not os.path.exists(pathXlsFileInit):
            raise ValueError("Ciqual_Reader : " + _("Init xls file doesn't exist") + " : " +
                             pathXlsFileInit)

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
        self.source = os.path.basename(pathXlsFileInit)
        self.processFile(pathXlsFileInit, cursor)

        self.connDB.commit()
        cursor.close()

        self.logger.info(_("Database %s initialized."), self.dbname)

    def processFile(self, pathXlsFileInit, cursor):
        """ Process a file pathXlsFileInit
            Write content in database using cursor
        """
        import xlrd

        # Open Excel 97 workbook and load the sheet that contains data
        workbook = xlrd.open_workbook(filename=pathXlsFileInit, on_demand=True)
        listSheet = workbook.sheet_names()
        self.logger.debug("List of sheets found in workbook : %s", str(listSheet))
        sheetName = self.configApp.get('Ciqual', 'CiqualSheetName')
        if sheetName not in listSheet:
            raise ValueError(
                    _("Ciqual_Reader : Sheet {sheetName} not found in workbook {workbook}").format(
                        sheetName=sheetName, workbook=pathXlsFileInit))
        sheetCiqual = workbook.sheet_by_name(sheetName)

        # Parse header line
        headerSplitted = sheetCiqual.row_values(0)
        dictConstituantsPosition = self.analyseHeaderCiqual(cursor, headerSplitted)

        # Parse products lines
        linenum = 0
        for linenum in range(1, sheetCiqual.nrows):
            lineSplitted = sheetCiqual.row_values(linenum)
            self.analyseProductCiqual(cursor, lineSplitted, dictConstituantsPosition)
            
        self.logger.warning(_("%d products read."), linenum)
 
    def analyseHeaderCiqual(self, cursor, headerSplitted):
        """ Analyse header line of Ciqual database
            Insert nams of constituants in constituantsValues table
            returns
               - dictConstituantsPosition : dictionary of (numField (>=0) : code constituant)
                """

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

        # V0.45+ : if Ciqual version > =2016 :
        # read components codes not in database
        compCodesFilePath = os.path.join(
                                    self.databaseRefDir,
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
 
        # Check first fieldsnames in given columns
        for fieldProp in ('fieldAlimCode', 'fieldAlimNomFr', 'fieldSousGroup'):
            fieldPosname = self.configApp.get('Ciqual', fieldProp).split(";")
            readField = headerSplitted[int(fieldPosname[0])-1]
            if fieldPosname[1] != readField:
                raise ValueError(_("Ciqual file : invalid header field") + " " +
                                 fieldPosname[0] +
                                 " : " + readField + " " + _("instead of") +
                                 " " + fieldPosname[1])

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
        regexpConstituant = re.compile(r'^(?P<nameConstituant>.*?)' +
                                           r' \((?P<unitConstituant>[µmk]?[Jgc][a]?[l]?)/100g\)$')
        constituants = []
        dictConstituantsPosition = dict()
        numField = self.configApp.getint('Ciqual', 'firstComponentField') - 1
        for constituantDescription in headerSplitted[numField:]:
            match = regexpConstituant.search(constituantDescription)
            nameConstituant = match.group('nameConstituant')
            unitConstituant = match.group('unitConstituant')
            if match:
                try:
                    code = dicoCompCodes[constituantDescription]
                except KeyError:
                    raise ValueError(_("Ciqual file : invalid header field") + " " +
                                 str(numField+1) +
                                 " : " + constituantDescription)
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

        self.logger.info(_("%d constituants available."), len(constituants))
        return dictConstituantsPosition

    def analyseProductCiqual(self, cursor, productSplitted,
                             dictConstituantsPosition):
        """ Analyse product line of Ciqual xls file
            and record product in database"""

        # Get Product code
        fieldAlimPop = self.configApp.get('Ciqual', 'fieldAlimCode').split(";")
        numFieldProductCode = int(fieldAlimPop[0]) - 1
        productCode = productSplitted[numFieldProductCode]

        # Get Product family
        fieldGroupPop = self.configApp.get('Ciqual', 'fieldSousGroup').split(";")
        numFieldGroupe = int(fieldGroupPop[0]) - 1
        familyName = productSplitted[numFieldGroupe]

        # Get Product Name without blanks and tabs at beginning and at the end
        fieldProctuctNamePop = self.configApp.get('Ciqual', 'fieldAlimNomFr').split(";")
        numFieldProductName = int(fieldProctuctNamePop[0]) - 1
        productName = productSplitted[numFieldProductName].strip()

        # If prop getOnlyAlimentMoyen is set only register in database
        # "Aliment Moyen" products
        if self.configApp.getboolean('Ciqual', 'getOnlyAlimentMoyen') and \
           "(aliment moyen)" not in productName:
            return

        # Create a record for this product
        cursor.execute("""
                       INSERT INTO products(familyName, code, name, source, dateSource, urlSource)
                       VALUES(?, ?, ?, ?, ?, ?)
                       """,
                       (familyName, productCode, productName,
                        self.source, self.dateSource, self.urlSource))

        # Record constituants values in database
        numField = self.configApp.getint('Ciqual', 'firstComponentField') - 1 
        for constituantValue in productSplitted[numField:]:
            qualifValue = ""
            # Empty values in Excel file are considered as - : Unknown
            if constituantValue == "":
                constituantValue = "-"

            # Analyse values
            if constituantValue == "-":
                value = 0.0
                qualifValue = "-"
            elif constituantValue == "traces":
                value = 0.0
                qualifValue = "T"
            elif constituantValue.startswith('< '):
                constituantValue = constituantValue.replace('< ', '')
                value = float(constituantValue.replace(',', '.'))
                qualifValue = '<'
            else:
                try:
                    value = float(constituantValue.replace(',', '.'))
                except ValueError as exc:
                    # Give more detail on exception
                    raise ValueError("productName="+ productName +
                                     ", numField="+ str(numField+1) +
                                     ", constituantValue=" + constituantValue +
                                     " : " + str(exc))
                qualifValue = 'N'
            # V0.28 : Don't Register components with value not defined
            if constituantValue != '-':
                cursor.execute("""INSERT INTO constituantsValues(productCode, constituantCode,
                                                             value, qualifValue)
                              VALUES(?, ?, ?, ?)""",
                               (productCode, dictConstituantsPosition[numField],
                                value, qualifValue))
            numField = numField + 1
