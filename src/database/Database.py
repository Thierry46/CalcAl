# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : Database
Author : Thierry Maillard (TMD)
Date  : 23/3/2016

Role : Define a database antd method to create, consult and save it.
************************************************************************************
"""
import logging
import os.path
import zipfile
import sqlite3
import re
import locale

class Database():
    """ Define a database """

    def __init__(self, configApp, ressourcePath, databasePath, initDB, localDirPath):
        """ Initialize a database 
            ressourcePath : path to database and image data
            If initDB : import data in a new dataBase
            """
        self.configApp = configApp
        self.ressourcePath = ressourcePath
        self.databasePath = databasePath
        self.localDirPath = localDirPath
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))

        self.connDB = sqlite3.connect(databasePath)
        self.dbname = os.path.basename(databasePath)
        self.logger.info("Database : " + databasePath + " opened.")

        if initDB:
            self.initDBFromFile()

    def close(self):
         """ Close database """
         if self.connDB:
            self.connDB.close()
            self.connDB = None
            self.logger.info("Database : " + self.getDbname() + " closed.")

    def initDBFromFile(self):
        """ Initialize a database with information read in CSV File """

        # Source for Ciqual file
        source = self.configApp.get('Resources', 'CiqualCSVFile')
        dateSource = self.configApp.get('Resources', 'CiqualCSVFileDate')
        urlSource = self.configApp.get('Resources', 'CiqualUrl')
        dictConstituantsPosition = dict()

        pathZipFileInit = os.path.join(self.ressourcePath, source) + ".zip"
        self.logger.info("Database : Initialize new database from " + pathZipFileInit + "...")
        linenum = 0
        cursor = self.connDB.cursor()

        # Create products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products(
                familyName TEXT,
                code INTEGER PRIMARY KEY UNIQUE,
                name TEXT,
                source TEXT,
                dateSource TEXT,
                urlSource TEXT
                )""")
        # Create constitiants values table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constituantsValues(
                productCode TEXT,
                constituantCode INTEGER,
                isValmax INTEGER,
                isUnknown INTEGER,
                isTraces INTEGER,
                value REAL
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
        with open(shortcutsFilePath, 'r') as fileShort:
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
            valueStr = constituantValue
            isValmax = 0
            isUnknown = 0
            isTraces = 0
            value = 0.0
            if valueStr == '-':
                isUnknown = 1
            elif valueStr == 'traces':
                isTraces = 1
            else:
                if valueStr.startswith('< '):
                    valueStr = valueStr.replace('< ', '')
                    isValmax = 1
                value = float(valueStr.replace(',', '.'))
            cursor.execute("""INSERT INTO constituantsValues(productCode, constituantCode,
                                                             isValmax, isUnknown, isTraces, value)
                              VALUES(?, ?, ?, ?, ?, ?)""",
                               (productCode, dictConstituantsPosition[numField],
                                isValmax, isUnknown, isTraces, value))
            numField = numField + 1

    def getDbname(self):
        return self.dbname

    def getListeComponents(self):
        """ Return list of tupple (code,shortcut,unit)
            for each entry from constituantsNames table """
        cursor = self.connDB.cursor()
        cursor.execute("SELECT code,shortcut,unit FROM constituantsNames ORDER BY shortcut")
        listComponentsUnits = cursor.fetchall()
        cursor.close()
        self.logger.info(str(len(listComponentsUnits)) + " Components available.")
        return listComponentsUnits

    def getListeFamilyFoodstuff(self):
        """ Return list of family from products table """
        cursor = self.connDB.cursor()
        cursor.execute("SELECT DISTINCT familyName FROM products ORDER BY familyName")
        listFamilyFoodstuff = [familyName[0] for familyName in cursor.fetchall()]
        cursor.close()
        self.logger.info(str(len(listFamilyFoodstuff)) + " family names available.")
        return listFamilyFoodstuff

    def getListeFoodstuffName(self, familyname):
        """ Return list of name in products table belonging to familyname """
        cursor = self.connDB.cursor()
        cursor.execute("SELECT DISTINCT name FROM products WHERE familyName=? ORDER BY name",
                       (familyname,))
        listeFoodstuffName = [name[0] for name in cursor.fetchall()]
        cursor.close()
        self.logger.info(str(len(listeFoodstuffName)) + " product names available.")
        return listeFoodstuffName

    def getUniteComponents(self, selectedComponentsName):
        """ Return units for a given component's shortcut list from constituantsNames table """
        cursor = self.connDB.cursor()
        listLabel = []
        for name in selectedComponentsName:
            cursor.execute(""" SELECT unit FROM constituantsNames
                               WHERE shortcut=?
                               ORDER BY shortcut""",
                           (name,))
            listLabel.append(cursor.fetchall()[0][0])
        cursor.close()
        return listLabel

    def getComponentsValues4Food(self, foodName, quantity, listComponentsCodes):
        """ Return components values for a given foodName from constituantsValues table """
        cursor = self.connDB.cursor()
        # Get foodstuff code
        cursor.execute(""" SELECT code FROM products WHERE name=? """,
                       (foodName,))
        codeFood = cursor.fetchall()[0][0]

        # Extract list of values
        listValues100g = []
        for componentCode in listComponentsCodes:
            cursor.execute(""" SELECT value FROM constituantsValues
                                    WHERE productCode=? AND constituantCode=?""",
                           (codeFood, componentCode,))
            listValues100g.append(cursor.fetchall()[0][0])
        cursor.close()
        listComponentsValues = [value * float(quantity) / 100.0
                                for value in listValues100g]
        return listComponentsValues

