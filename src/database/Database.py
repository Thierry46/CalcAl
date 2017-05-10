# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : Database
Author : Thierry Maillard (TMD)
Date  : 23/3/2016 - 30/5/2016

Role : Define a database antd method to create, consult and save it.
************************************************************************************
"""
import logging
import os.path
import zipfile
import sqlite3
import re
import locale
import getpass

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
        self.nbMaxDigit = int(self.configApp.get('Limits', 'nbMaxDigit'))

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
                value REAL
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
            value = 0.0
            if valueStr != '-' and valueStr != 'traces':
                if valueStr.startswith('< '):
                    valueStr = valueStr.replace('< ', '')
                    isValmax = 1
                value = float(valueStr.replace(',', '.'))
            cursor.execute("""INSERT INTO constituantsValues(productCode, constituantCode, value)
                              VALUES(?, ?, ?)""",
                               (productCode, dictConstituantsPosition[numField], value))
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
        listUnit = []
        for name in selectedComponentsName:
            cursor.execute(""" SELECT unit FROM constituantsNames
                               WHERE shortcut=?
                               ORDER BY shortcut""",
                           (name,))
            listUnit.append(cursor.fetchone()[0])
        cursor.close()
        return listUnit

    def getComponentsValues4Food(self, foodName, quantity, listComponentsCodes):
        """ Return components values for a given foodName from constituantsValues table"""
        listComponentsValues = []

        if len(listComponentsCodes) > 0:
            # Format list of constituants codes
            listCompFormat = ""
            for componentCode in listComponentsCodes:
                listCompFormat = listCompFormat + ", " + str(componentCode)
            listCompFormat = listCompFormat[2:]

            cursor = self.connDB.cursor()
            # Get values for all asked componentsCodes
            cursor.execute(""" SELECT constituantCode, value FROM constituantsValues
                INNER JOIN products
                WHERE constituantsValues.productCode = products.code
                AND products.name=?
                AND constituantCode IN (""" + listCompFormat + ")",
                           (foodName,))

            results = cursor.fetchall()
            for componentCode in listComponentsCodes:
                foundCompInResults = False
                for lineResult in results:
                    if lineResult[0] == componentCode:
                        componentValueFloat = lineResult[1] * float(quantity) / 100.0
                        componentValueStr = ("{0:." + str(self.nbMaxDigit) + "f}").format(componentValueFloat)
                        listComponentsValues.append(componentValueStr)
                        foundCompInResults = True
                assert foundCompInResults, "Problem component not found"
            cursor.close()
        return listComponentsValues

    def getFamily4FoodName(self, foodName):
        """ Given a foodName return its family name """
        cursor = self.connDB.cursor()
        familyName = []
        cursor.execute(""" SELECT familyName FROM products WHERE name=?""", (foodName,))
        familyName = cursor.fetchone()[0]
        cursor.close()
        return familyName

    def getProductsNamesContainingPart(self, partWildcard):
        """ get all Product's Names Containing the pattern partWildcard
            partWildcard may contain wilcards handle by sqlite3 like * or ?
            The asterisk sign represents zero or multiple numbers or characters.
            The ? represents a single number or character.
            Case is ignored"""
        cursor = self.connDB.cursor()
        partWildcard = "*" + partWildcard + "*"
        cursor.execute("SELECT name FROM products WHERE UPPER(name) GLOB ? ORDER BY name",
                       (partWildcard.upper(),))
        listeFoodstuffName = [name[0] for name in cursor.fetchall()]
        cursor.close()
        self.logger.info(str(len(listeFoodstuffName)) + " products names available for " +
                            partWildcard)
        return listeFoodstuffName

    def getMinMaxForConstituants(self):
        """ Get Min and Max values for each constituant """
        cursor = self.connDB.cursor()
        cursor.execute("""
                        SELECT constituantCode, shortcut, unit, MIN(value), MAX(value)
                            FROM constituantsValues
                            INNER JOIN constituantsNames
                            ON constituantsValues.constituantCode = constituantsNames.code
                            GROUP BY constituantCode
                            ORDER BY shortcut
                        """)
        listMinMax = cursor.fetchall()
        cursor.close()
        return listMinMax

    def getProductNamesCondition(self, condition):
        """ Return a list of products  names that mach the given condition on their values """
        listeFoodstuffNames=[]
        cursor = self.connDB.cursor()
        cursor.execute("""SELECT name FROM products
            INNER JOIN constituantsValues
            where constituantsValues.productCode = products.code""" + condition)
        listenames = cursor.fetchall()
        cursor.close()
        if len(listenames) > 0:
            listeFoodstuffNames = [name[0] for name in listenames]
        return listeFoodstuffNames

    def insertNewComposedProduct(self, productName, familyName, listNamesQty):
        """ Insert new composed product in database
            return total quantity for all food """
        totalQuantity = 0

        if productName is None or  len(productName.strip()) < 2:
            raise ValueError(_("Invalid food name : use more than one letter"))

        if productName is None or len(familyName.strip()) < 2:
            raise ValueError(_("Invalid family name : use more than one letter"))

        assert (listNamesQty is not None) and len(listNamesQty) > 1, \
                             "insertNewComposedProduct() : Invalid listNamesQty"
        try:
            with self.connDB:
                cursor = self.connDB.cursor()
                # Set the new productCode
                cursor.execute("SELECT max(code) from products")
                newProductCode = max(cursor.fetchone()[0] + 1,
                                    int(self.configApp.get('Limits', 'minCompositionProductCode')))

                # Get the codes for all existing components
                cursor.execute("SELECT DISTINCT code from constituantsNames")
                listeCodesConstituant = [codeConstituant[0]
                                         for codeConstituant in cursor.fetchall()]

                # Prepare data
                totalCompValues = [0.0 for comp in listeCodesConstituant]
                fieldsCompositionProducts = []
                for element in listNamesQty:
                    totalQuantity = totalQuantity + int(element[1])

                for element in listNamesQty:
                    cursor.execute("SELECT code FROM products WHERE name=?", (element[0],))
                    quantityPercent = float(element[1]) * 100.0 / float(totalQuantity)
                    fieldsCompositionProducts.append([newProductCode,
                                                      cursor.fetchone()[0],
                                                      quantityPercent])

                    # Add component values in g for each component
                    compValues = self.getComponentsValues4Food(element[0], element[1],
                                                          listeCodesConstituant)
                    for index in range(len(listeCodesConstituant)):
                        totalCompValues[index] = totalCompValues[index] + float(compValues[index])

                assert totalQuantity > 0 , \
                             "insertNewComposedProduct() : totalQuantity for group = 0"
                index = 0
                fieldsComposants = []
                for comp in listeCodesConstituant:
                    fieldsComposants.append([newProductCode, comp,
                                             totalCompValues[index] * 100.0 / float(totalQuantity)])
                    index = index + 1

                # Save in compositionProducts table details of new product
                cursor.executemany("""
                        INSERT INTO compositionProducts(productCode, productCodeCiqual,
                                                        quantityPercent)
                        VALUES(?, ?, ?)
                        """, fieldsCompositionProducts)

                # Save components values of new product
                cursor.executemany("""
                    INSERT INTO constituantsValues(productCode, constituantCode, value)
                    VALUES(?, ?, ?)
                    """, fieldsComposants)

                # Insert new composed product in products table
                source = self.configApp.get('Resources', 'CiqualCSVFile')
                dateSource = self.configApp.get('Resources', 'CiqualCSVFileDate')
                urlSource = self.configApp.get('Resources', 'CiqualUrl')
                cursor.execute("""
                    INSERT INTO products(familyName, code, name, source, dateSource, urlSource)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """, (familyName, newProductCode, productName,
                                source, dateSource, urlSource))

                cursor.close()
        except sqlite3.IntegrityError:
            raise ValueError(_("Problem with this new composition product (name already exist)") +
                             " : " + productName)
        return totalQuantity

    def getPartsOfComposedProduct(self, productName, quantity):
        """ Get part of a composed products given a group of food
            return part names and their quantity according quantity of group
            given in parameter """
        listNamesQty = []
        cursor = self.connDB.cursor()
        cursor.execute("SELECT code FROM products WHERE name=?", (productName,))
        productCode = cursor.fetchone()[0]
        if productCode < int(self.configApp.get('Limits', 'minCompositionProductCode')) :
            raise ValueError(_("Can't ungroup") + " " + productName + " : " + _("not a group"))
        # Get members of this group
        cursor.execute("""SELECT name, quantityPercent
                            FROM compositionProducts
                            INNER JOIN products
                            WHERE productCodeCiqual=code and productCode=?""",
                       (productCode,))
        for nameQty in cursor.fetchall():
            quantityPart = int(round(float(nameQty[1]) * float(quantity) / 100.0, 0))
            listNamesQty.append([nameQty[0], quantityPart])

        cursor.close()
        return listNamesQty
