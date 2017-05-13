# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : Database
Author : Thierry Maillard (TMD)
Date  : 23/3/2016 - 2/10/2016

Role : Define a database and method to create, consult and save it.
************************************************************************************
"""
import logging
import os.path
import sqlite3
import re
import time

from . import DatabaseReaderFactory

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

    def initDBFromFile(self, databasePath, databaseType, initFile):
        """ Create a new database databasePath by reading a file initFile """
        self.open(databasePath)
        databaseReader = DatabaseReaderFactory.DatabaseReaderFactory.getInstance(self.configApp,
                                     self.dirProject, databaseType, self.connDB, self.dbname)
        databaseReader.initDBFromFile(initFile)

    def open(self, databasePath):
        """ Open or create a sqlite database """
        self.databasePath = databasePath
        self.connDB = sqlite3.connect(databasePath)
        self.dbname = os.path.basename(databasePath)
        self.logger.info("Database : " + databasePath + " opened.")
        self.createUserTables() # V0.32

    def close(self):
         """ Close database """
         if self.connDB:
            self.connDB.close()
            self.connDB = None
            self.logger.info("Database : " + self.getDbname() + " closed.")

    def getDatabasePath(self):
        return self.databasePath

    def getDbname(self):
        return self.dbname

    def getListComponents(self):
        """ Return list of tupple (code,shortcut,unit)
            for each entry from constituantsNames table """
        cursor = self.connDB.cursor()
        cursor.execute("SELECT code,shortcut,unit FROM constituantsNames ORDER BY shortcut")
        listComponentsUnits = cursor.fetchall()
        cursor.close()
        self.logger.info(str(len(listComponentsUnits)) + " Components available.")
        return listComponentsUnits

    def getListFamilyFoodstuff(self):
        """ Return list of family from products table """
        cursor = self.connDB.cursor()
        cursor.execute("SELECT DISTINCT familyName FROM products ORDER BY familyName")
        listFamilyFoodstuff = [familyName[0] for familyName in cursor.fetchall()]
        cursor.close()
        self.logger.info(str(len(listFamilyFoodstuff)) + " family names available.")
        return listFamilyFoodstuff

    def getListFoodstuffName(self, familyname):
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
        listNameComponentsValuesRaw= []
        for foodName in productNameAllOk:
            listComponentsValuesRaw = self.getComponentsValuesRaw4Food(foodName, 100.0,
                                                                   listSelectedComponentsCodes)
            listNameComponentsValuesRaw.append([foodName, listComponentsValuesRaw])
            counter = counter + 1
            if counter >= nbMaxResultSearch:
                break

        return nbFoundProducts, listNameComponentsValuesRaw

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

    def insertNewComposedProduct(self, productName, familyName,
                                 totalQuantity, dictComponentsQualifierQuantity,
                                 listFoodNameAndQty2Group):
        """ Insert new composed product in database
            return total quantity for all food """
        if productName is None or  len(productName.strip()) < 2:
            raise ValueError(_("Invalid food name : use more than one letter"))

        if productName is None or len(familyName.strip()) < 2:
            raise ValueError(_("Invalid family name : use more than one letter"))

        assert (listFoodNameAndQty2Group is not None) and len(listFoodNameAndQty2Group) > 1, \
                             "insertNewComposedProduct() : Invalid listFoodNameAndQty2Group"
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

                # Prepare components values to record in database
                # Format of record to insert : productCode, componentCode, qualifValue, value
                fieldsComposants = []
                for componentCode, fields in dictComponentsQualifierQuantity.items():
                     fieldsComposants.append([newProductCode, componentCode, fields[0], fields[1]])

                # Prepare composition product % to record in database
                # Format of record to insert : productCode, productCodePart, quantityPercent
                fieldsCompositionProducts = []
                for element in listFoodNameAndQty2Group:
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
                    INSERT INTO constituantsValues(productCode, constituantCode, qualifValue, value)
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
        self.logger.debug("Database : getInfoDatabase")
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
        self.logger.debug("Database : getInfoFood for product " + foodName)
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

    def getInfoComponent(self, codeProduct, codeComponent):
        """ Return a dictionnary of info for a given product component in this database
            V0.36 : 26/10/2016 """
        self.logger.debug("Database : getInfoComponent for codeProduct=" + str(codeProduct) +
                          ", codeComponent=" + str(codeComponent))
        dictComponent = dict()
        dictComponent["productCode"] = codeProduct
        dictComponent["constituantCode"] = codeComponent

        cursor = self.connDB.cursor()
        # Get info about component for a product
        cursor.execute("""SELECT name, shortcut
                        FROM constituantsNames
                        WHERE code=?""",
                       (codeComponent,))
        result = cursor.fetchone()
        dictComponent["name"] = result[0]
        dictComponent["shortcut"] = result[1]

        # Get values
        cursor.execute("""SELECT  value, qualifValue
                          FROM constituantsValues, constituantsNames
                          WHERE productCode=? AND constituantCode=?""",
                       (codeProduct, codeComponent))
        result = cursor.fetchone()
        if result:
            dictComponent["value"] = result[0]
            dictComponent["qualifValue"] = result[1]
        else:
            dictComponent["value"] = 0.0
            dictComponent["qualifValue"] = '-'
        cursor.close()
        return dictComponent

    def deleteUserProduct(self, foodName):
        """ Delete a given user foodname in this database
        V0.30 : 23/8/2016 """
        self.logger.debug("Database : deleteUserProduct for product " + foodName)
        cursor = self.connDB.cursor()

        # Get foodName code
        cursor.execute("SELECT code FROM products WHERE name=?", (foodName,))
        returnValue = cursor.fetchone()
        assert returnValue is not None, "deleteUserProduct() : foodname to delete : " + foodName + " not found !"
        code = returnValue[0]

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
        self.logger.debug("Database : joinDatabase with " + dbNameSecondary)
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

    def createUserTables(self):
        """ V0.32 : Create al user tables """
        self.logger.debug("Database : createUserTables")
        cursor = self.connDB.cursor()

        # Controls how strings are encoded and stored in the database
        cursor.execute('PRAGMA encoding = "UTF-8"')

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compositionProducts(
                productCode INTEGER,
                productCodePart INTEGER,
                quantityPercent REAL
                )""")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portions(
                code INTEGER PRIMARY KEY UNIQUE,
                name TEXT,
                date TEXT,
                patient TEXT,
                type TEXT,
                period TEXT
                )""")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portionsDetails(
                portionCode INTEGER,
                productCode INTEGER,
                quantity REAL
                )""")

        self.connDB.commit()
        cursor.close()

    def getPortions(self, withCode=False):
        """ Return all portions registred in database """
        cursor = self.connDB.cursor()
        fields = "name, date, patient, type, period"
        if withCode:
            fields = "code, " + fields
        cursor.execute("SELECT " + fields + " FROM portions ORDER BY name, date, patient")
        portionIdAll = cursor.fetchall()
        cursor.close()
        self.logger.info(str(len(portionIdAll)) + " portions available.")
        return portionIdAll

    def getPortionsFiltred(self, listUserFilters, withCode=False):
        """ Return portions registred in database and filtered according userFilters fields"""
        portionIdFiltered = []
        for portionId in self.getPortions(withCode):
            condTotal = True
            for num, input in enumerate(listUserFilters):
                numField = num
                if withCode:
                    numField = numField + 1
                cond = input == "" or input.upper() in portionId[numField].upper()
                condTotal = condTotal and cond
            if condTotal:
                portionIdFiltered.append(portionId)
        self.logger.debug(str(len(portionIdFiltered)) + " portions selected.")
        return portionIdFiltered

    def getPortionCode(self, portionName, portionDate, portionPatient):
        """ Return the code in database for the portion given its Ids and True if it exists """
        cursor = self.connDB.cursor()
        cursor.execute("""SELECT code from portions 
                          WHERE UPPER(name)=? and UPPER(date)=? and UPPER(patient)=?""",
                       (portionName.upper(), portionDate.upper(), portionPatient.upper()))
        results = cursor.fetchone()
        exist = results is not None and len(results) == 1
        if exist:
            code = results[0]
        else:
            # Generate a new code
            # Find a free code number for this new portion
            cursor.execute("SELECT code from portions ORDER BY code")
            listeCodes = [codePortion[0] for codePortion in cursor.fetchall()]
            if len(listeCodes) == 0:
                code = 1
            else:
                listeCodesSet = set(listeCodes)
                sequence = set(range(1, listeCodes[-1] + 2))
                missing = sequence - listeCodesSet
                code = list(missing)[0]

        cursor.close()
        self.logger.debug("getPortionCode : portionCode=" + str(code) + ", exist=" + str(exist))
        return code, exist

    def insertPortion(self, fields4ThisPortion, listNamesQties):
        """ Insert or modify a portion in database """
        portionCode, exist = self.getPortionCode(fields4ThisPortion[0], fields4ThisPortion[1],
                                                 fields4ThisPortion[2],)
        cursor = self.connDB.cursor()
        if exist :
            # Delete existing products for this portion
            cursor.execute("DELETE FROM portionsDetails WHERE portionCode=?",
                           (portionCode,))
            fields4ThisPortion.append(portionCode)
            # Even 3 Ids field must be modified because of char case
            cursor.execute("""
                UPDATE portions
                    SET name=?, date=?, patient=?, type=?, period=?
                    WHERE code=?
                """, fields4ThisPortion)
            self.logger.debug("insertPortion : portionCode=" + str(portionCode) + " modified")
        else:
            fields4ThisPortion.insert(0, portionCode)
            cursor.execute("""
                INSERT INTO portions(code, name, date, patient, type, period)
                VALUES(?, ?, ?, ?, ?, ?)
                """, fields4ThisPortion)
            self.logger.debug("insertPortion : portionCode=" + str(portionCode) + " created")

        # Get products code that compose this portion and prepare inserting
        fieldsPortionsDetails = []
        for element in listNamesQties:
            cursor.execute("SELECT code FROM products WHERE name=?", (element[0],))
            results = cursor.fetchone()
            fieldsPortionsDetails.append([portionCode, results[0], element[1]])
        self.logger.debug("insertPortion : " + str(len(fieldsPortionsDetails)) +
                          " products to insert for portion " + str(portionCode))

        # Save in portionsDetails table products and quantities composing this portion
        cursor.executemany(""" INSERT INTO portionsDetails(portionCode, productCode, quantity)
                                      VALUES(?, ?, ?)""",
                           fieldsPortionsDetails)

        self.connDB.commit()
        cursor.close()
        self.logger.debug("insertPortion : saved")

    def getFoodNameAndQuantity4Portion(self, portionCode):
        """ Return a list of (FoodName, Quantity) contained in portion which code is given """
        cursor = self.connDB.cursor()
        cursor.execute("""SELECT products.name, quantity
                        FROM portionsDetails
                        INNER JOIN products
                        WHERE productCode=products.code AND portionCode=? """,
                       (portionCode,) )
        listFoodNameQuantity = cursor.fetchall()
        cursor.close()
        self.logger.debug("getFoodNameAndQuantity4Portion : get " +
                            str(len(listFoodNameQuantity)) + " items for portion " +
                            str(portionCode))
        return listFoodNameQuantity

    def deletePortion(self, portionCode):
        """ Delete a given portion in this database
        V0.32 : 28/9/2016 """
        self.logger.debug("Database : deletePortion for portion " + str(portionCode))
        cursor = self.connDB.cursor()

        # Delete elements values
        cursor.execute("DELETE FROM portionsDetails WHERE portionCode=?", (portionCode,))
        cursor.execute("DELETE FROM portions WHERE code=?", (portionCode,))

        # Commit to be seen by other database connexion
        self.connDB.commit()
        cursor.close()
        self.logger.debug("deletePortion : portion " + str(portionCode) + " " + _("deleted"))

