# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : Database
Author : Thierry Maillard (TMD)
Date  : 23/3/2016 - 8/5/2016

Role : Define a database and method to create, consult and save it.
************************************************************************************
"""
import logging
import os.path
import sqlite3
import re
import locale
import getpass

from database import DatabaseReaderFactory

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
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.formatFloatValue = "{0:." + self.configApp.get('Limits', 'nbMaxDigit') + "f}"
        # table for qualification reduction rules
        self.QRulesS = self.configApp.get('QualifValue', 'QRulesS').split(";")
        self.QRules0 = self.configApp.get('QualifValue', 'QRules0').split(";")
        self.QRulesO = self.configApp.get('QualifValue', 'QRulesO').split(";")

        self.connDB = sqlite3.connect(databasePath)
        self.dbname = os.path.basename(databasePath)
        self.logger.info("Database : " + databasePath + " opened.")

        if initDB:
            databaseReader = DatabaseReaderFactory.DatabaseReaderFactory.getInstance(self.configApp,
                                                                                     localDirPath,
                                                                                     "CIQUAL",
                                                                                     self.connDB,
                                                                                     self.dbname)
            source = self.configApp.get('Resources', 'CiqualCSVFile')
            pathZipFileInit = os.path.join(self.ressourcePath,
                                           self.configApp.get('Resources', 'CiqualCSVFile')) + \
                              ".zip"
            databaseReader.initDBFromFile(pathZipFileInit)

    def close(self):
         """ Close database """
         if self.connDB:
            self.connDB.close()
            self.connDB = None
            self.logger.info("Database : " + self.getDbname() + " closed.")


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

    def existFoodstuffName(self, foodname):
        """ Return True if foodname exists in database """
        cursor = self.connDB.cursor()
        cursor.execute("SELECT DISTINCT name FROM products WHERE name=?",
                       (foodname,))
        existname = cursor.fetchone() is not None
        cursor.close()
        self.logger.info(foodname + " exists ? :" + str(existname))
        return existname

    def getComponentsValuesRaw4Food(self, foodName, quantity, listComponentsCodes):
        """ Return for 1 given foodname
            a list of (constituant codes, value multipled by quantity, qualifValue)
            sorted according components shortcut"""
        listComponentsValues = []
        if len(listComponentsCodes) > 0:
            cursor = self.connDB.cursor()
            # Get values for all asked componentsCodes
            cursor.execute("SELECT constituantCode,value*" + str(quantity) + "/100.0, qualifValue\n" +\
                           """ FROM constituantsValues
                               INNER JOIN products
                               INNER JOIN constituantsNames
                               WHERE constituantsValues.productCode = products.code
                               AND  constituantsNames.code = constituantsValues.constituantCode
                               AND products.name=?
                               AND constituantCode IN (""" + \
                       ",".join([str(code) for code in listComponentsCodes]) + \
                       ") ORDER BY shortcut",
                       (foodName,))
            listComponentsValues = cursor.fetchall()
            cursor.close()
        return listComponentsValues

    def getComponentsValues4Food(self, foodName, quantity, listComponentsCodes):
        """ Return components values multipled by quantity for a given foodName"""
        listComponentsValuesRaw = self.getComponentsValuesRaw4Food(foodName, quantity,
                                                                   listComponentsCodes)
        listComponentsValues = self.formatListComponentsValues(listComponentsValuesRaw)
        return listComponentsValues

    def sumComponents4FoodList(self, listNamesQties, listComponentsCodes):
        """Compute a sum for each components values for given foodNames and quantities
            Return :
             - sum of food quantities
             - a list of (constituant codes, sum of values multipled by quantity,
                          reduced qualifValue)"""
        constituantCodes = [0 for comp in listComponentsCodes]
        totalValues = [0.0 for comp in listComponentsCodes]
        qualifValues = ["" for comp in listComponentsCodes]
        sumQuantities = 0.0
        for name, quantity in listNamesQties:
            listComponentsValuesRaw = self.getComponentsValuesRaw4Food(name, quantity,
                                                                   listComponentsCodes)
            sumQuantities = sumQuantities + float(quantity)
            index = 0
            for constituantCode, value, qualifier in listComponentsValuesRaw:
                constituantCodes[index] = constituantCode
                totalValues[index] = totalValues[index] + value
                qualifValues[index] = qualifValues[index] + qualifier
                index = index + 1

        # Reduce number of value qualifier to 1
        index = 0
        for index in range(len(qualifValues)):
            qualifValues[index] = self.reducQualifier(qualifValues[index], totalValues[index])
            index = index + 1

        # Prepare  by Constituant result list
        totalByConstituant = []
        for constituant, value, qualifValue in zip(constituantCodes, totalValues, qualifValues):
            totalByConstituant.append([constituant, value, qualifValue])

        return sumQuantities, totalByConstituant

    def sumComponents4FoodListFormated(self, listNamesQties, listComponentsCodes):
        """Return result of sumComponents4FoodList formated """
        result = None
        if len(listNamesQties) > 0 :
            sumQuantities, totalByConstituant = self.sumComponents4FoodList(listNamesQties,
                                                                            listComponentsCodes)
            listComponentsValues = self.formatListComponentsValues(totalByConstituant)
        return sumQuantities, listComponentsValues

    def reducQualifier(self, qualif2Reduce, value):
        """ Reduce qualif2Reduce expression by applying rules read in config file """
        qualifResult = "".join(set(qualif2Reduce))
        nbReduction = 0
        while nbReduction < 5 and len(qualifResult) > 1:
            # Apply rules
            if value >= float(self.configApp.get("Limits", "near0")):
                QRule2apply = self.QRulesS
            else: # For value near 0
                QRule2apply = self.QRules0
            QRule2apply= QRule2apply + self.QRulesO
            for rule in QRule2apply:
                if rule[0] in qualifResult and rule[1] in qualifResult:
                    qualifResult = qualifResult.replace(rule[0], rule[2])
                    qualifResult = qualifResult.replace(rule[1], rule[2])
                qualifResult = "".join(set(qualifResult))
            nbReduction = nbReduction + 1
        assert nbReduction<5, "reducQualifier don't converge : " + qualif2Reduce +\
                              " can't be reduce : " + qualifResult + \
                              ". Check config/[QualifValue]/QRules"
        return qualifResult

    def formatListComponentsValues(self, listComponentsValuesRaw):
        """ Format components values according values qualifiers """
        listComponentsValuesFormated = []
        for constituantCode, value, qualifier in listComponentsValuesRaw:
            if qualifier == "N" :
                resultValue = self.formatFloatValue.format(value)
            elif qualifier == "-" :
                resultValue = "-"
            elif qualifier == "T" :
                resultValue = _("Traces")
            elif qualifier == "<" :
                resultValue = "< " + self.formatFloatValue.format(value)
            else:
                raise ValueError("formatListComponentsValues : unknown value qualifier : " +\
                                qualifier)
            listComponentsValuesFormated.append(resultValue)
        return listComponentsValuesFormated

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
                totalQuantity, totalComponentsValues = self.sumComponents4FoodList(listNamesQty,
                                                                         listeCodesConstituant)
                assert totalQuantity > 0, "insertNewComposedProduct() : totalQuantity for group = 0"
                index = 0
                fieldsComposants = []
                for compValue in totalComponentsValues:
                     fieldsComposants.append([newProductCode, compValue[0],
                                              compValue[1] * 100.0 / totalQuantity,
                                              compValue[2]])

                fieldsCompositionProducts = []
                for element in listNamesQty:
                    cursor.execute("SELECT code FROM products WHERE name=?", (element[0],))
                    quantityPercent = element[1] * 100.0 / totalQuantity
                    fieldsCompositionProducts.append([newProductCode, cursor.fetchone()[0],
                                                      quantityPercent])

                # Save in compositionProducts table details of new product
                cursor.executemany("""
                        INSERT INTO compositionProducts(productCode, productCodeCiqual,
                                                        quantityPercent)
                        VALUES(?, ?, ?)
                        """, fieldsCompositionProducts)

                # Save components values of new product
                cursor.executemany("""
                    INSERT INTO constituantsValues(productCode, constituantCode, value, qualifValue)
                    VALUES(?, ?, ?, ?)
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
            quantityPart = round(nameQty[1] * quantity / 100.0, 1)
            listNamesQty.append([nameQty[0], quantityPart])

        cursor.close()
        return listNamesQty
