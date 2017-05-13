# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : Database
Author : Thierry Maillard (TMD)
Date  : 23/3/2016 - 7/1/2017

Role : Define a database and method to create, consult and save it.
************************************************************************************
"""
import logging
import os.path
import sqlite3
import time

from util import DateUtil
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
        self.databasePath = None
        self.connDB = None
        self.dbname = None

    def initDBFromFile(self, databasePath, databaseType, initFile):
        """ Create a new database databasePath by reading a file initFile """
        self.open(databasePath)
        databaseReader = DatabaseReaderFactory.DatabaseReaderFactory.getInstance(self.configApp,
                                                                                 self.dirProject,
                                                                                 databaseType,
                                                                                 self.connDB,
                                                                                 self.dbname)
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
        """ Return current database path """
        return self.databasePath

    def getDbname(self):
        """ Return current database short name """
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
            1st letter case is ignored
            27/12/2016 : Pb capitalising all letters when there is accent."""
        cursor = self.connDB.cursor()
        partWildcardLower = "*" + partWildcard + "*"
        partWildcardCap = "*" + partWildcard.capitalize() + "*"
        cursor.execute("""SELECT name FROM products
        				WHERE name GLOB ? OR name GLOB ?
        				ORDER BY name""",
                       (partWildcardLower, partWildcardCap))
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

    def getProductComponents4Filters(self, listFilters, messageQueue):
        """ Return list by filter [dict[product] = [constituantCode, qualifValue, value]]
            that match the listfilter
            """
        if len(listFilters) == 0:
            raise ValueError(_("Please select at least one operator in a filter line"))

        numFilter = 1
        numberResults = 0
        messageproductsCondition = ""
        listDictProductValues = []
        for constituantCode, selectedOperator, level in listFilters:
            dictProductValues = {}
            # Build condition for extraction of products from BD
            condition = " AND constituantCode=" + str(constituantCode) + \
                " AND value" + selectedOperator + str(level)
            productValues = self.getProductNamesCondition(condition)
            for product in productValues:
                dictProductValues[product[0]] = [product[1], product[2], product[3]]
            numberResults += len(productValues)
            messageproductsCondition = _("Filter") + " " + str(numFilter) + " : " + \
                                        str(numberResults) + " " + _("results")
            messageQueue.put(messageproductsCondition)
            listDictProductValues.append(dictProductValues)
            numFilter += 1
        return listDictProductValues

    def getProductNamesCondition(self, condition):
        """ Return a list [name, constituantCode, qualifValue, value]
            that mach the given condition on their values """
        cursor = self.connDB.cursor()
        cursor.execute("""SELECT products.name, constituantCode, qualifValue, value
            FROM products, constituantsValues
            WHERE constituantsValues.productCode = products.code""" + condition)
        listProductNamesConstituantsValues = cursor.fetchall()
        cursor.close()
        return listProductNamesConstituantsValues

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
        if productCode >= int(self.configApp.get('Limits', 'startGroupProductCodes')):
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
                dictInfoFood["groups"] = listGroup

        cursor.close()
        return dictInfoFood

    def getInfoComponent(self, codeProduct, codeComponent):
        """ Return a dictionnary of info for a given product component in this database
            V0.36 : 26/10/2016
            V0.45 : Return empty values if component is not found in table """
        self.logger.debug("Database : getInfoComponent for codeProduct=" + str(codeProduct) +
                          ", codeComponent=" + str(codeComponent))
        dictComponent = dict()
        dictComponent["productCode"] = codeProduct
        dictComponent["constituantCode"] = codeComponent
        dictComponent["name"] = ""
        dictComponent["shortcut"] = ""
        dictComponent["value"] = 0.0
        dictComponent["qualifValue"] = '-'

        cursor = self.connDB.cursor()
        # Get info about component for a product
        cursor.execute("""SELECT name, shortcut
                        FROM constituantsNames
                        WHERE code=?""",
                       (codeComponent,))
        result = cursor.fetchone()
        if result is not None:
            dictComponent["name"] = result[0]
            dictComponent["shortcut"] = result[1]

            # Get values
            cursor.execute("""SELECT value, qualifValue
                          FROM constituantsValues, constituantsNames
                          WHERE productCode=? AND constituantCode=?""",
                           (codeProduct, codeComponent))
            result = cursor.fetchone()
            if result:
                dictComponent["value"] = result[0]
                dictComponent["qualifValue"] = result[1]
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
        assert returnValue is not None, "deleteUserProduct() : foodname to delete : " + \
                                        foodName + " not found !"
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

    def joinDatabase(self, dbNameSecondary, isUpdate):
        """ Join this database to an other : dbNameSecondary
            intersection, current = main database has the priority
            dbNameSecondary : database used to modify main database
            isUpdate : True if products of main database must be updated
            in v0.30 : groups created by user are not merged"""
        self.logger.debug("Database/joinDatabase with " + dbNameSecondary +
                          " mode update=" + str(isUpdate))

        cursor = self.connDB.cursor()
        cursor.execute("ATTACH DATABASE ? AS secondDB", (dbNameSecondary,))

        # V0.45 : When updating a database : delete all information present in 2nd database
        #   theese information are added after
        if isUpdate:
            self.logger.debug("Database/joinDatabase delete all information to be updated")
            cursor.execute("""DELETE FROM main.products
                                WHERE main.products.code > 0 AND
                                    main.products.code IN
                                    (SELECT secondDB.products.code FROM secondDB.products)""")
            cursor.execute("""DELETE FROM main.constituantsValues
                                WHERE main.constituantsValues.productCode > 0 AND
                                    main.constituantsValues.productCode IN
                                    (SELECT secondDB.products.code FROM secondDB.products)""")

        self.logger.debug("Database/joinDatabase add all information from " + dbNameSecondary)

        # V0.45 : UNIQ contrainst on name in products table
        #   Select for elimination products in double :
        #   with same name and  different code
        cursor.execute("""SELECT main.products.name, secondDB.products.code
            FROM main.products, secondDB.products
            WHERE main.products.code > 0 AND
                  main.products.name = secondDB.products.name AND
                  main.products.code != secondDB.products.code  """)
        results = cursor.fetchall()
        if results is not None:
            namesDoubleProducts = [result[0] for result in results]
            codesDoubleProducts = ",".join([str(result[1]) for result in results])
            self.logger.warning("Database/joinDatabase() : " +
                                _("Conflict for products with same name and diferent codes") +
                                " : " + str(namesDoubleProducts) + "\n" +
                                _("ignore products from second database") + " " +
                                dbNameSecondary)

        cursor.execute("""INSERT INTO main.products
                          SELECT * FROM secondDB.products
                            WHERE secondDB.products.code > 0 AND
                                secondDB.products.code NOT IN (
                                SELECT main.products.code FROM main.products) AND
                                secondDB.products.code NOT IN
                                    (""" + codesDoubleProducts +")")
        cursor.execute("""INSERT INTO main.constituantsValues
                          SELECT * FROM secondDB.constituantsValues
                            WHERE secondDB.constituantsValues.productCode > 0 AND
                                  secondDB.constituantsValues.productCode NOT IN (
                                  SELECT main.constituantsValues.productCode
                                        FROM main.constituantsValues) AND
                                  secondDB.constituantsValues.productCode NOT IN
                                        (""" + codesDoubleProducts +")")
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
                period TEXT,
                nbDays INTEGER
                )""")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portionsDetails(
                portionCode INTEGER,
                productCode INTEGER,
                quantity REAL
                )""")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pathologies(
                name TEXT PRIMARY KEY UNIQUE,
                description TEXT,
                reference TEXT
                )""")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pathologiesConstituants(
                pathologyName TEXT,
                constituantCode INTEGER
                )""")

        # V0.41 : Add column nbDays to existing portions table
        try:
            cursor.execute(" ALTER TABLE portions ADD COLUMN nbDays INTEGER DEFAULT 1")
            self.logger.warning("v0.41 : Table portions has got old schema : add an nbDays field")
        except sqlite3.OperationalError:
            self.logger.debug("OK v0.41 : Table portions as got an nbDays field")

        # V0.41 : Check and correct dates in portions table (to delete in a future version)
        cursor.execute("SELECT code, date FROM portions")
        listCodeDate = cursor.fetchall()
        listPb = []
        nbDateCorrected = 0
        for codeDate in listCodeDate:
            code, date = codeDate
            try:
                dateFormated = DateUtil.formatDate(date)
                if dateFormated != date:
                    cursor.execute("UPDATE portions SET date=? WHERE code=?", (dateFormated, code))
                    nbDateCorrected += 1
            except ValueError:
                listPb.append([code, date])
        if len(listPb) > 0:
            self.logger.warning(_("Dates are invalid in following portions") + " : " + str(listPb))
        if nbDateCorrected > 0:
            self.logger.warning(str(nbDateCorrected) + " " +_("dates corrected in portions table"))

        # V0.42 : 26/11/2016 : Patient tables
        # Check if patientInfo table exists
        cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='patientInfo'")
        if cursor.fetchone() is None:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patientInfo(
                    code TEXT PRIMARY KEY UNIQUE,
                    birthYear INTEGER DEFAULT 0,
                    gender TEXT DEFAULT "U",
                    size INTEGER DEFAULT 170,
                    notes TEXT DEFAULT ""
                )""")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS patientPathologies(
                    patientCode TEXT,
                    pathologyName TEXT
                )""")
          # Create patient whith existing ration info (to delete in a future version)
            cursor.execute("SELECT DISTINCT patient FROM portions")
            CodePatents = cursor.fetchall()
            nbInsertedPatient = 0
            for code in CodePatents:
                cursor.execute("INSERT INTO patientInfo(code) VALUES(?)", (code[0],))
                nbInsertedPatient += 1
            if nbInsertedPatient > 0:
                self.logger.warning(str(nbInsertedPatient) + " " +_("patient get from portion table"))

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
            for num, inputFilter in enumerate(listUserFilters):
                numField = num
                if withCode:
                    numField = numField + 1
                cond = (inputFilter == "" or inputFilter.upper() in portionId[numField].upper())
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
                                                 fields4ThisPortion[2])
        cursor = self.connDB.cursor()
        if exist:
            # Delete existing products for this portion
            cursor.execute("DELETE FROM portionsDetails WHERE portionCode=?",
                           (portionCode,))
            fields4ThisPortion.append(portionCode)
            # Even 3 Ids field must be modified because of char case
            cursor.execute("""
                UPDATE portions
                    SET name=?, date=?, patient=?, type=?, period=?, nbDays=?
                    WHERE code=?
                """, fields4ThisPortion)
            self.logger.debug("insertPortion : portionCode=" + str(portionCode) + " modified")
        else:
            fields4ThisPortion.insert(0, portionCode)
            cursor.execute("""
                INSERT INTO portions(code, name, date, patient, type, period, nbDays)
                VALUES(?, ?, ?, ?, ?, ?, ?)
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
        cursor.executemany("""INSERT INTO portionsDetails(portionCode, productCode, quantity)
                                      VALUES(?, ?, ?)""",
                           fieldsPortionsDetails)

        self.connDB.commit()
        cursor.close()
        self.logger.debug("insertPortion : saved")

    def getAllInfo4Portion(self, portionCode, specialComponentsCodes):
        """ Return infos for the portion selected by portionCode
            ! There can be missing components for products : replaced by "-" in Calculator frame
            The case where all special components are missing for a product is ignored
            """
        self.logger.debug("Database : getAllInfo4Portion for portion " + str(portionCode))

        # Build IN sqlite clause for specialComponentsCodes
        specialComponentsCodesStr = [str(code) for code in specialComponentsCodes]
        inClause = ",".join(specialComponentsCodesStr)

        cursor = self.connDB.cursor()
        # V0.41 : get nbDays for this portion
        cursor.execute("SELECT nbDays FROM portions WHERE code=?", (portionCode,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError(_("Portion code not found in database") + " : " + str(portionCode))
        nbDays = result[0]

        cursor.execute("""SELECT portionsDetails.quantity, products.name, products.code,
                                products.familyName, products.source, products.dateSource,
                                products.urlSource, constituantsNames.code,
                                constituantsNames.name, constituantsNames.shortcut,
                                constituantsValues.value, constituantsValues.qualifValue
                        FROM portionsDetails, products, constituantsNames, constituantsValues
                        WHERE portionsDetails.portionCode=? AND
                            portionsDetails.productCode=products.code AND
                            constituantsNames.code=constituantsValues.constituantCode AND
                            products.code=constituantsValues.productCode AND
                            constituantsNames.code IN (""" + inClause + """)
                            ORDER BY products.code""",
                       (portionCode,))
        listProductPortion = cursor.fetchall()
        cursor.close()

        self.logger.debug("getAllInfo4Portion : get " +
                          str(len(listProductPortion)) + " items for portion " +
                          str(portionCode))
        return nbDays, listProductPortion

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

    def savePathology(self, name, description, reference, listConstituantsCodes):
        """ Insert a new pathology in database
            V0.40 : 22/11/2016 """
        self.logger.debug("Database/savePathology " + name)
        cursor = self.connDB.cursor()

        # Checks parameters
        if name is None or len(name) < 2:
            raise ValueError(_("Invalid pathology name : use more than one letter") + " : " + name)
        if listConstituantsCodes is None or len(listConstituantsCodes) < 1:
            raise ValueError(_("No component given for that pathology") + " : " + name)
        for code in listConstituantsCodes:
            # Get info about component for a product
            cursor.execute("SELECT code FROM constituantsNames WHERE code=?", (code,))
            result = cursor.fetchone()
            if result is None:
                raise ValueError(_("Invalid component code given for pathology") + " : " +
                                 str(code))
        cursor.close()

        # Replace existing pathology
        self.deletePathology(name)
        cursor = self.connDB.cursor()
        cursor.execute("""INSERT INTO pathologies(name, description, reference)
                            VALUES(?, ?, ?)
                        """, (name, description, reference))

        # V0.41 : insert all pathology constituants with only one SQL statement
        # Save in pathologiesConstituants table (pathologyName, constituantCode) composing
        # pathology componants
        pathologiesConstituants = []
        for code in listConstituantsCodes:
            pathologiesConstituants.append([name, code])
        cursor.executemany("""INSERT INTO pathologiesConstituants(pathologyName, constituantCode)
                                VALUES(?, ?)""",
                           pathologiesConstituants)

        self.connDB.commit()
        cursor.close()

    def getDefinedPathologiesNames(self):
        """ Return a list of all pathologies defined in database
        V0.40 : 22/11/2016 """
        self.logger.debug("Database/getDefinedPathologiesNames")
        cursor = self.connDB.cursor()
        cursor.execute("SELECT name FROM pathologies")
        results = cursor.fetchall()
        cursor.close()
        listNames = [result[0] for result in results]
        self.logger.debug("Database/getDefinedPathologiesNames : " + str(listNames))
        return listNames

    def deletePathology(self, name, forPatient=False):
        """ Delete the name pathology in this database
        V0.40 : 22/11/2016 """
        self.logger.debug("Database/deletePathology for name " + name)
        cursor = self.connDB.cursor()

        # Delete elements values
        cursor.execute("DELETE FROM pathologiesConstituants WHERE pathologyName=?", (name,))
        cursor.execute("DELETE FROM pathologies WHERE name=?", (name,))
        if forPatient:
            cursor.execute("DELETE FROM patientPathologies WHERE pathologyName=?", (name,))

        # Commit to be seen by other database connexion
        self.connDB.commit()
        cursor.close()
        self.logger.debug("deletePathology : name " + name + " " + _("deleted"))

    def getComponentsCodes4Pathologies(self, listPathologiesNames):
        """ Delete the name pathology in this database
        V0.40 : 22/11/2016 """
        self.logger.debug("Database/getComponentsCodes4Pathologies for names " +
                          str(listPathologiesNames))
        if listPathologiesNames is None or len(listPathologiesNames) < 1:
            raise ValueError(_("No pathology selected"))
        cursor = self.connDB.cursor()
        inClause = ",".join(["'" + patho + "'" for patho in listPathologiesNames])
        cursor.execute("""SELECT constituantCode
                        FROM pathologiesConstituants
                        WHERE pathologyName IN (""" +
                       inClause + ")")
        results = cursor.fetchall()
        listCodes = set([result[0] for result in results])

        if len(results) == 0:
            raise ValueError(_("Unknown pathologies selected") + " : " + str(listPathologiesNames))

        cursor.close()
        self.logger.debug("getComponentsCodes4Pathologies : " + str(len(listCodes)) +
                          " distincts codes founds")
        return listCodes

    def getDefinedPathologiesDetails(self, name):
        """ Return a details (id fields and constituants) for name pathology
        V0.40 : 22/11/2016 """
        self.logger.debug("Database/getDefinedPathologiesDetails")
        cursor = self.connDB.cursor()
        cursor.execute("""SELECT description, reference FROM pathologies
                        WHERE name=?""", (name,))
        result = cursor.fetchone()
        if result is None:
            raise ValueError(_("Unknown pathology : ") + " : " + name)
        cursor.close()
        description = result[0]
        reference = result[1]

        listComponentsCodes = self.getComponentsCodes4Pathologies([name])

        self.logger.debug("Database/getDefinedPathologiesDetails : name=" + name +
                          " description=" + description + " reference=" + reference +
                          " constituants=" + str(listComponentsCodes))
        return name, description, reference, listComponentsCodes

    def getAllPatientCodes(self):
        """ Return a list of all patient codes defined in database
            V0.42 : 26/11/2016 """
        self.logger.debug("Database/getAllPatientCodes")
        cursor = self.connDB.cursor()
        cursor.execute("SELECT code FROM patientInfo ORDER BY code")
        results = cursor.fetchall()
        cursor.close()
        listCodes = [result[0] for result in results]
        self.logger.debug("Database/getAllPatientCodes : " + str(listCodes))
        return listCodes

    def getInfoPatient(self, patientCode):
        """ Return a dictionary for value defined for this patient
        V0.42 : 28/11/2016 """
        self.logger.debug("Database/getInfoPatient")
        cursor = self.connDB.cursor()
        dictPatient = dict()
        cursor.execute("""SELECT code, birthYear, gender, size, notes
                       FROM patientInfo WHERE code=?""",
                       (patientCode,))
        result = cursor.fetchone()
        cursor.close()
        if result is None:
            raise ValueError(_("Please select at least one operator in a filter line"))
        dictPatient["code"] = result[0]
        dictPatient["birthYear"] = result[1]
        dictPatient["gender"] = result[2]
        dictPatient["size"] = result[3]
        dictPatient["notes"] = result[4]
        self.logger.debug("Database/getInfoPatient : " + str(dictPatient))
        return dictPatient

    def insertPatientInDatabase(self, listInfoPatient):
        """Insert new patient in database """
        self.logger.debug("Database/insertPatientInDatabase")
        cursor = self.connDB.cursor()
        cursor.execute("""
            INSERT INTO patientInfo(code, birthYear, gender, size, notes)
                VALUES(?, ?, ?, ?, ?)
            """, (listInfoPatient[0], int(listInfoPatient[1]),
                  listInfoPatient[2], int(listInfoPatient[3]),
                  listInfoPatient[4]))
        self.connDB.commit()
        cursor.close()

    def updatePatientInDatabase(self, listInfoPatient):
        """Update patient in database """
        self.logger.debug("Database/updatePatientInDatabase")
        cursor = self.connDB.cursor()
        cursor.execute("""
            UPDATE patientInfo
            SET birthYear=?, gender=?, size=?, notes=?
            WHERE code=?
            """, (int(listInfoPatient[1]),
                  listInfoPatient[2], int(listInfoPatient[3]),
                  listInfoPatient[4], listInfoPatient[0]))
        self.connDB.commit()
        cursor.close()

    def updatePatientPathologies(self, patientCode, listpathologies):
        """ Update pathologies for a patient """
        self.logger.debug("Database/updatePatientPathologies : patient " + patientCode +
                          "pathologies=" + str(listpathologies))
        cursor = self.connDB.cursor()
        cursor.execute("DELETE FROM patientPathologies WHERE patientCode=?", (patientCode,))

        # Insert New pathologies in table
        values2Insert = [(patientCode, pathology) for pathology in listpathologies]
        cursor.executemany("""
            INSERT INTO patientPathologies(patientCode, pathologyName)
            VALUES(?, ?)
            """, values2Insert)

        self.connDB.commit()
        cursor.close()

    def getPathologies4Patient(self, patientCode):
        """ Return list of pathologies registred for patient patientCode """
        self.logger.debug("Database/getPathologies4Patient : patient " + patientCode)
        cursor = self.connDB.cursor()
        cursor.execute("SELECT pathologyName FROM patientPathologies WHERE patientCode=?",
                       (patientCode,))
        results = cursor.fetchall()
        cursor.close()
        listPathologies = [pathology[0] for pathology in results]
        self.logger.debug("listPathologies=" + str(listPathologies))
        return listPathologies

    def deletePatient(self, patientCode):
        """ Delete all information for given patient in database """
        self.logger.debug("Database/deletePatient : patient " + patientCode)
        cursor = self.connDB.cursor()
        cursor.execute("DELETE FROM patientPathologies WHERE patientCode=?", (patientCode,))
        cursor.execute("DELETE FROM patientInfo WHERE code=?", (patientCode,))
        cursor.execute(""" DELETE FROM portionsDetails
                           WHERE portionCode IN (SELECT code FROM portions WHERE patient=?)""",
                       (patientCode,))
        cursor.execute("DELETE FROM portions WHERE patient=?", (patientCode,))
        self.connDB.commit()
        cursor.close()

    def correctEnergyKcal(self):
        """ V0.47 : correct problem in Ciqual 2016 table
            Compute energy in kcal for products in database without energy provided """

        # Get energy codes useful to compute missing energies
        energyTotalKcalCode = self.configApp.get('Energy', 'EnergyTotalKcalCode')
        energyTotalKJCode = self.configApp.get('Energy', 'EnergyTotalKJCode')
        CoefKcal2Kj = float(self.configApp.get('Energy', 'CoefKcal2Kj'))
        listComp = self.configApp.get('Energy', 'EnergeticComponentsCodes')
        energeticComponentsCodes = [int(code) for code in listComp.split(";")]
        energyCodesStr = listComp.replace(";", ",")
        # Suppress sugar components already included in glucide
        sugarCode = self.configApp.get('Energy', 'SugarCode')
        energyCodesStr = energyCodesStr.replace(sugarCode, '')
        energyCodesStr = energyCodesStr.replace(',,', ',')
        if energyCodesStr.endswith(','):
            energyCodesStr = energyCodesStr[:-1]
        listEnergy = self.configApp.get('Energy', 'EnergySuppliedByComponents')
        energySuppliedByComponents = [float(value) for value in listEnergy.split(";")]
        assert len(energeticComponentsCodes) == len(energySuppliedByComponents), \
            "Pb .ini : Energy keys EnergeticComponentsCodes and EnergeticComponentsCodes " + \
            "have the same length !"
        dictCoefEnergy = dict()
        for numComp, code in enumerate(energeticComponentsCodes):
            dictCoefEnergy[code] = energySuppliedByComponents[numComp]

        # Select all products and their energetics components
        # from database when their energy in kcal is not supplies
        cursor = self.connDB.cursor()
        cursor.execute("""
                SELECT productCode, constituantCode, value
                  FROM constituantsValues
                  WHERE productCode IN (
                    SELECT code FROM products WHERE code NOT IN (
                        SELECT code FROM products, constituantsValues
                            WHERE code = productCode AND constituantCode=?))
                    AND constituantCode IN (""" + energyCodesStr + ") ORDER BY productCode",
                       (energyTotalKcalCode,))
        results = cursor.fetchall()

        # Compute energy in kcal and kJ for each products found
        listCorrectedEnergies = []
        listCodesProducts = []
        productCodePrev = 0
        energy = 0.0
        nbProducts = 0
        for result in results:
            productCode, constituantCode, value = result
            if productCode != productCodePrev: # Change of products
                nbProducts += 1
                if productCodePrev != 0: # Register computed energy
                    listCorrectedEnergies.append((productCodePrev,
                                                      int(energyTotalKcalCode),
                                                      energy, 'N'))
                    listCorrectedEnergies.append((productCodePrev,
                                                    int(energyTotalKJCode),
                                                    energy * CoefKcal2Kj, 'N'))
                    listCodesProducts.append(str(productCodePrev))
                productCodePrev = productCode
                energy = 0.0
            energy += value * dictCoefEnergy[constituantCode]
        if productCodePrev != 0:
            listCorrectedEnergies.append((productCodePrev,
                                              int(energyTotalKcalCode),
                                              energy, 'N'))
            listCorrectedEnergies.append((productCodePrev,
                                            int(energyTotalKJCode),
                                            energy * CoefKcal2Kj, 'N'))
            listCodesProducts.append(str(productCodePrev))

        # Message to user
        if len(listCorrectedEnergies) == 0:
            self.logger.debug("Database/correctEnergyKcal() : All energies are OK")
        else:
            self.logger.warning("Database/correctEnergyKcal() : Energies kcal modification for " +
                                str(nbProducts) + " products !")

        # Create all missing enegy in kcal components in constituantsValues table
        cursor.executemany("""
            INSERT INTO constituantsValues(productCode, constituantCode, value, qualifValue)
                VALUES(?, ?, ?, ?)
            """, listCorrectedEnergies)

        # Update product table source code to indicate that Energy is corrected
        listCodesProductsStr = ",".join(listCodesProducts)
        cursor.execute("""SELECT code, source
                            FROM products
                            WHERE code IN (""" + listCodesProductsStr + ")")
        results = cursor.fetchall()
        listCodesProductsSourceM = [[source + " (" + _("Energies recalculated by CalcAl") + " !)", code]
                                    for code, source in results]
        cursor.executemany("UPDATE products SET source=? WHERE code=?",
                           listCodesProductsSourceM)
