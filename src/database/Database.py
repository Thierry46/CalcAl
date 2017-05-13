# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : Database
Author : Thierry Maillard (TMD)
Date  : 23/3/2016 - 23/8/2016

Role : Define a database and method to create, consult and save it.
************************************************************************************
"""
import logging
import os.path
import sqlite3
import re
import time

from database import DatabaseReaderFactory

class Database():
    """ Define a database """

    def __init__(self, configApp, dirProject):
        """ Initialize a database 
            dirProject : project directory
            If initDB : import data in a new dataBase
            """
        self.configApp = configApp
        self.dirProject = dirProject
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.formatFloatValue = "{0:." + self.configApp.get('Limits', 'nbMaxDigit') + "f}"
        # table for qualification reduction rules
        self.QRulesS = self.configApp.get('QualifValue', 'QRulesS').split(";")
        self.QRules0 = self.configApp.get('QualifValue', 'QRules0').split(";")
        self.QRulesO = self.configApp.get('QualifValue', 'QRulesO').split(";")

    def initDBFromFile(self, databasePath, databaseType, initFile):
        """ Create a new database databasePath by reading a file initFile """
        self.open(databasePath)
        databaseReader = DatabaseReaderFactory.DatabaseReaderFactory.getInstance(self.configApp,
                                     self.dirProject, databaseType, self.connDB, self.dbname)
        databaseReader.initDBFromFile(initFile)

    def open(self, databasePath):
        """ Open or create a sqlite database """
        self.connDB = sqlite3.connect(databasePath)
        self.dbname = os.path.basename(databasePath)
        self.logger.info("Database : " + databasePath + " opened.")

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
        """ Return, for a given foodname and a listComponentsCodes, a list of
            (constituant codes, value multipled by quantity, qualifValue)
            27-28/7/2016 : v0.28 : Unknown constituant values not stored in database
                return defalt value [constituantCode, 0.0, "-"] if
                a component is not found for this foodname
                Constituants are now sorted according order of listComponentsCodes
            """
        listComponentsValues = []
        listComponentsValuesAll = []
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
                       ",".join([str(code) for code in listComponentsCodes]) + ")",
                       (foodName,))
            listComponentsValues = cursor.fetchall()
            cursor.close()

            # 27/7/2016 : v0.28 : add default constituant values to results
            # sorted by listComponentsCodes order
            for constituantCode in listComponentsCodes:
                values4thisComponent = [values for values in listComponentsValues
                                            if constituantCode == values[0]]
                nbValues = len(values4thisComponent)
                assert nbValues <= 1, "getComponentsValuesRaw4Food() find more than 1 record (" + \
                                      str(nbValues) + ") in table constituantsValues " + \
                                      "for constituantCode=" + \
                                      str(constituantCode)  + " and for foodName=" + foodName
                if nbValues > 0:
                    listComponentsValuesAll.append(values4thisComponent[0])
                else:
                    listComponentsValuesAll.append([constituantCode, 0.0, "-"])
        return listComponentsValuesAll

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

    def getProductComponents4Filters(self, listFilters, listSelectedComponentsCodes):
        """ v0.28 : Return the total number of products that match the filter
            and a list of products names and their constituants values
            that match the given filters for the first nbMaxResultSearch items"""
        productNameAllOk = set()
        listProductListName = []
        nbMaxResultSearch = int(self.configApp.get('Limits', 'nbMaxResultSearch'))

        if len(listFilters) == 0:
            raise ValueError(_("Please select at least one operator in a filter line"))

        for constituantCode, selectedOperator, level in listFilters:
            # Build condition for extraction of products from BD
            condition = " AND constituantCode=" + str(constituantCode) + \
                " AND value" + selectedOperator + str(level)
            listProductListName.append(set(self.getProductNamesCondition(condition)))

        # Intersection of all listProductListName sets
        if len(listProductListName) > 0 and len(listProductListName[0]) > 0:
            productNameAllOk = listProductListName[0]
            index = 1
            while index < len(listProductListName):
                productNameAllOk = productNameAllOk.intersection(listProductListName[index])
                index = index + 1

        # Get components values for all results product
        nbFoundProducts = len(productNameAllOk)
        counter = 0
        listComponentsValues= []
        for foodName in productNameAllOk:
            componentsValues = self.getComponentsValues4Food(foodName, 100.0,
                                                             listSelectedComponentsCodes)
            listComponentsValues.append([foodName, componentsValues])
            counter = counter + 1
            if counter >= nbMaxResultSearch:
                break

        return nbFoundProducts, listComponentsValues

    def getProductNamesCondition(self, condition):
        """ Return a list of products names that mach the given condition on their values """
        listeFoodstuffNames=[]
        cursor = self.connDB.cursor()
        cursor.execute("""SELECT name FROM products
            INNER JOIN constituantsValues
            WHERE constituantsValues.productCode = products.code""" + condition)
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
                cursor.execute("SELECT min(code) from products")
                newProductCode = min(cursor.fetchone()[0] - 1,
                                    int(self.configApp.get('Limits', 'startGroupProductCodes'))-1)

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
                    results = cursor.fetchone()
                    quantityPercent = element[1] * 100.0 / totalQuantity
                    fieldsCompositionProducts.append([newProductCode, results[0], quantityPercent])

                # Save in compositionProducts table details of new product
                cursor.executemany("""
                        INSERT INTO compositionProducts(productCode, productCodePart,
                                                        quantityPercent)
                        VALUES(?, ?, ?)
                        """, fieldsCompositionProducts)

                # Save components values of new product
                cursor.executemany("""
                    INSERT INTO constituantsValues(productCode, constituantCode, value, qualifValue)
                    VALUES(?, ?, ?, ?)
                    """, fieldsComposants)

                # Insert new composed product in products table
                source = "Group"
                dateSource = time.strftime("%G")
                urlSource = "Group"
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
        if productCode >= int(self.configApp.get('Limits', 'startGroupProductCodes')) :
            raise ValueError(_("Can't ungroup") + " " + productName + " : " + _("not a group"))
        # Get members of this group
        cursor.execute("""SELECT name, quantityPercent
                            FROM compositionProducts
                            INNER JOIN products
                            WHERE productCodePart=code and productCode=?""",
                       (productCode,))
        for nameQty in cursor.fetchall():
            quantityPart = round(nameQty[1] * quantity / 100.0, 1)
            listNamesQty.append([nameQty[0], quantityPart])

        cursor.close()
        return listNamesQty

    def getInfoDatabase(self):
        """ Return a dictionnary of counters for elements in this database
            V0.30 : 21-22/8/2016 """
        startGroupProductCodes = int(self.configApp.get('Limits', 'startGroupProductCodes'))
        dictCounters = dict()
        dictCounters["dbName"] = self.getDbname()
        cursor = self.connDB.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        dictCounters["nbProducts"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(DISTINCT familyName) FROM products")
        dictCounters["nbFamily"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products WHERE code < ?",
                       (startGroupProductCodes,))
        dictCounters["nbGroup"] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM constituantsNames")
        dictCounters["nbConstituants"] = cursor.fetchone()[0]
        cursor.close()
        return dictCounters

    def getInfoFood(self, foodName):
        """ Return a dictionnary of info for a given foodname in this database
        V0.30 : 22/8/2016 """
        dictInfoFood = dict()
        dictInfoFood["isGroup"] = False
        cursor = self.connDB.cursor()

        # Get info about product or group
        cursor.execute("""SELECT name, code, familyName, source, dateSource, urlSource
                            FROM products WHERE name=?""",
                       (foodName,))
        result = cursor.fetchone()
        dictInfoFood["name"] = result[0]
        dictInfoFood["code"] = result[1]
        dictInfoFood["familyName"] = result[2]
        dictInfoFood["source"] = result[3]
        dictInfoFood["dateSource"] = result[4]
        dictInfoFood["urlSource"] = result[5]
        if dictInfoFood["code"] < int(self.configApp.get('Limits', 'startGroupProductCodes')):
            dictInfoFood["isGroup"] = True

        # Get info on its components
        cursor.execute("SELECT COUNT(*) FROM constituantsValues WHERE productCode = ?",
                       (dictInfoFood["code"],))
        dictInfoFood["nbConstituants"] = cursor.fetchone()[0]

        # Get info on members of this group
        if dictInfoFood["isGroup"]:
            cursor.execute("SELECT COUNT(*) FROM compositionProducts WHERE productCode = ?",
                       (dictInfoFood["code"],))
            dictInfoFood["nbGroupsMembers"] = cursor.fetchone()[0]
            if dictInfoFood["nbGroupsMembers"] > 0:
                listGroup = []
                cursor.execute("""SELECT name, quantityPercent
                                  FROM compositionProducts, products
                                  WHERE productCode=? and code=productCodePart""",
                               (dictInfoFood["code"],))
                for namePercent in cursor.fetchall():
                    dictGroup = dict()
                    dictGroup["namePart"] = namePercent[0]
                    dictGroup["percentPart"] = namePercent[1]
                    listGroup.append(dictGroup)
                dictInfoFood["groups"] =listGroup

        cursor.close()
        return dictInfoFood

    def deleteUserProduct(self, foodName):
        """ Delete a given user foodname in this database
        V0.30 : 23/8/2016 """
        cursor = self.connDB.cursor()

        # Get foodName code
        cursor.execute("SELECT code FROM products WHERE name=?", (foodName,))
        code = cursor.fetchone()[0]

        # Only user foodstufs can be deleted
        if code >= int(self.configApp.get('Limits', 'startGroupProductCodes')):
            raise ValueError(_("Can't delete") + " " + foodName[:30] + " : " +
                             _("Not created by user"))

        # Can't delete an element if it is used by an other
        cursor.execute("""SELECT name
                          FROM compositionProducts, products
                          WHERE productCodePart=? and code=productCode""",
                       (code,))
        results = cursor.fetchone()
        if results:
            nameParentElement = results[0]
            raise ValueError(_("Can't delete") + " " + foodName[:30] + " : " +
                             _("used by") + " " + nameParentElement)

        # Delete elements values
        cursor.execute("DELETE FROM constituantsValues WHERE productCode=?",
                       (code,))
        cursor.execute("DELETE FROM compositionProducts WHERE productCode=?",
                       (code,))
        cursor.execute("DELETE FROM products WHERE code=?",
                       (code,))

        # Commit to be seen by other database connexion
        self.connDB.commit()
        cursor.close()

    def joinDatabase(self, dbNameSecondary):
        """ Join this database to an other : dbNameSecondary
            intersection, current = master database has the priority
            in v0.30 : groups created by user are not merged"""
        cursor = self.connDB.cursor()
        cursor.execute("ATTACH DATABASE ? AS secondDB", (dbNameSecondary,))
        cursor.execute("""INSERT INTO main.products
                          SELECT * FROM secondDB.products
                            WHERE secondDB.products.code > 0 AND
                                secondDB.products.code NOT IN (
                                SELECT main.products.code FROM main.products)""")
        cursor.execute("""INSERT INTO main.constituantsValues
                          SELECT * FROM secondDB.constituantsValues
                            WHERE secondDB.constituantsValues.productCode > 0 AND
                                  secondDB.constituantsValues.productCode NOT IN (
                                  SELECT main.constituantsValues.productCode
                                  FROM main.constituantsValues)""")
        cursor.execute("""INSERT INTO main.constituantsNames
                            SELECT * FROM secondDB.constituantsNames
                            WHERE secondDB.constituantsNames.code NOT IN (
                                SELECT main.constituantsNames.code
                                FROM main.constituantsNames)""")
        self.connDB.commit()
        cursor.close()

