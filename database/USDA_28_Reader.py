# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : USDA_28_Reader
Author : Thierry Maillard (TMD)
Date  : 29/7/2016 - 2/10/2016

Role : Read a USDA 2013 database from CSV or CSVzipped text file.

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
import zipfile
import os

class USDA_28_Reader():
    """Read a USDA 2013 database from CSV or CSVzipped text file"""
    def __init__(self, configApp, dirProject, connDB, dbname):
        """ Initialize a USDA database reader
        configApp : ressource .ini for application
        connDB : cursor opened on database to fill
        dbname : name of the database to fill
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
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))

    def initDBFromFile(self, pathZipFileInit):
        """ Initialize a database with information read in a zip File downloaded from the WEB """

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
        # Create constitiants values table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constituantsValues(
                productCode INTEGER,
                constituantCode INTEGER,
                value REAL,
                qualifValue TEXT
                )""")

        if pathZipFileInit.endswith(".zip"):
            with zipfile.ZipFile(pathZipFileInit, "r") as zfile:
                with zfile.open(self.configApp.get('USDA', 'USDATXTFile')) as readfile:
                    self.processFile(readfile, cursor, True)
                readfile.close()
            zfile.close()
        else:
            cursor.close()
            raise ValueError("USDA_28_Reader : " + _("Only .zip files allowed"))

        self.connDB.commit()
        cursor.close()

    def processFile(self, handle, cursor, decode):
        """ Process a file given a handle on it
            Write content in database using cursor
            decode = True if content must be decoded
        """
        # Source for USDA file
        source = self.configApp.get('USDA', 'USDATXTFile')
        dateSource = self.configApp.get('USDA', 'USDATXTFileDate')
        urlSource = self.configApp.get('USDA', 'USDAUrl')
        shiftCodeProduct = int(self.configApp.get('USDA', 'shiftCodeProduct'))

        # Record constituants names
        dictConstituantsPosition = self.registerConstituantsName(cursor)

        linenum = 0
        productNameList = []
        for linebytes in handle:
            linenum = linenum + 1
            if decode:
                lineDecoded = linebytes.decode('iso8859_1')
            else:
                lineDecoded = linebytes
            # strip to remove final CR et NL
            # Remove string indicators ~
            lineSplitted = lineDecoded.strip().replace('~', '').split("^")

            # Analyse and record product line of USDA database
            numField = 1
            productCode = ""
            familyName = ""
            productName = ""
            for field in lineSplitted:
                if numField == 1:
                    productCode = str(int(field) + shiftCodeProduct)
                elif numField == 2:
                    familyName = field.split(',')[0].capitalize()
                    productName = field.capitalize()
                    # Duplicated products names are not allowed in database
                    if productName in productNameList:
                        self.logger.warning("analyseProductUSDA() : productName=" + productName +
                                            " already recorded -> ignored, linenum=" + str(linenum))
                        break
                    else:
                        productNameList.append(productName)
                        cursor.execute("""
                            INSERT INTO products(familyName, code, name, source,
                                                  dateSource, urlSource)
                            VALUES(?, ?, ?, ?, ?, ?)
                            """,
                                       (familyName, productCode, productName, source,
                                        dateSource, urlSource))
                elif str(numField) in dictConstituantsPosition.keys():
                    # Record constituants values in database if not empty
                    if len(field) > 0:
                        qualifValue = "N"
                        value = float(field)
                        cursor.execute("""INSERT INTO constituantsValues(productCode,
                                                                         constituantCode,
                                                                         value, qualifValue)
                                       VALUES(?, ?, ?, ?)""",
                                       (productCode, dictConstituantsPosition[str(numField)],
                                        value, qualifValue))
                numField = numField + 1
        self.logger.info(str(linenum) + " lines read.")

    def registerConstituantsName(self, cursor):
        """ Record constituants name and properties
            Ref : sr28abbr.zip/sr28_doc.pdf : Description abbreviate file format :
            p.39 (with headers : p.43)"""

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

        # Create constituants in database
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS constituantsNames(
            code INTEGER PRIMARY KEY UNIQUE,
            name TEXT,
            unit TEXT,
            shortcut TEXT
            )""")

        # Read USDA constituants description in file
        constituants = []
        dictConstituantsPosition = dict()
        uSDAConstitFilePath = os.path.join(self.databaseRefDir,
                                                self.configApp.get('USDA',
                                                                   'USDAConstituantsFilePath'))
        with open(uSDAConstitFilePath, 'r', encoding='utf-8') as fileConstituants:
            for line in fileConstituants.read().splitlines():
                # Eliminate comment
                posComment = line.find('#')
                if posComment != -1:
                    line = line[:posComment]
                # If valid parameter line, register key and value in dictionary
                param = line.split(';')
                if len(param) == 4:
                    numField = param[0].strip()
                    nameConstituant = param[1].strip()
                    codeConstituant = param[2].strip()
                    unitConstituant = param[3].strip()
                    constituants.append((codeConstituant,
                                         nameConstituant,
                                         unitConstituant,
                                         dicoShortcuts[codeConstituant]))
                    dictConstituantsPosition[numField] = codeConstituant
        fileConstituants.close()

        # Record in constituants names table
        assert len(constituants) > 0, uSDAConstitFilePath + " : bad file"
        cursor.executemany("""
                            INSERT INTO constituantsNames(code, name, unit, shortcut)
                            VALUES(?, ?, ?, ?)
                            """,
                           constituants)

        self.logger.info(str(len(constituants)) + " constituants available.")
        return dictConstituantsPosition
