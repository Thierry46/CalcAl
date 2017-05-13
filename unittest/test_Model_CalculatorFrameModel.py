#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_CalculatorFrameModel.py
Author : Thierry Maillard (TMD)
Date : 26/10/2016 - 17/11/2016
Role : Tests unitaires du projet Calcal avec py.test
Use : See unittest.sh

Licence : GPLv3
Copyright (c) 2015 - Thierry Maillard

   This file is part of Calcal project.

   Calcal project is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   FinancesLocales project is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with Finance Locales project.  If not, see <http://www.gnu.org/licenses/>.
"""
import pytest
from pytest import approx

import configparser
import os.path
import pwd
import gettext

import CalcAl
from model import CalculatorFrameModel
from database import DatabaseManager
from util import CalcalExceptions

# Code to execute before and at the end of all test
@pytest.fixture(scope="session")
def initEnv():
    # Code to be executed when called by test function
    fileConfigApp = 'CalcAl.ini'
    configApp = configparser.RawConfigParser()
    configApp.read(fileConfigApp, encoding="utf-8")
    CalcAl.setLocaleCalcal(configApp, '.')

    # Open demo database
    baseDirPath = os.path.join(configApp.get('Resources', 'ResourcesDir'),
                               configApp.get('Resources', 'DatabaseDir'))
    databaseManager = DatabaseManager.DatabaseManager(configApp, '.', baseDirPath)
    databaseManager.openDatabase(configApp.get('Resources', 'DemoDatabaseName'))

    # Values returned to each test calling function
    return configApp, databaseManager

def test_initGetterNone():
    """ Test constructor and getter, no database loaded """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    assert len(calculatorFrameModel.getAllExistingComponents()) == 0

    # Close demo database
    databaseManager.closeDatabase()

def test_setDatabase():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)

    # Set a database in CalculatorFrameModel
    calculatorFrameModel.setDatabase(database)

    assert len(calculatorFrameModel.getAllExistingComponents()) > 0
    assert len(calculatorFrameModel.askedByUserCodes) == 0

    # Close demo database
    databaseManager.closeDatabase()

def test_addFoodInTable():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)

    # Set a database in CalculatorFrameModel
    calculatorFrameModel.setDatabase(database)

    # Add a foodstuff in calculatorFrameModel
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1]])
    assert calculatorFrameModel.getNumberOfFoodStuff() == 1
    assert calculatorFrameModel.dictFoodStuff[foodname1].getData("name") == foodname1
    assert calculatorFrameModel.dictFoodStuff[foodname1].getData("quantity") == approx(float(quantity1))
    assert len(calculatorFrameModel.dictFoodStuff[foodname1].dictComponents) == 7

    foodname2 = "Légumes, pur jus (aliment moyen)"
    quantity2 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname2, quantity2]])
    assert len(calculatorFrameModel.dictFoodStuff) == 2

    # Update quantity in foodname1
    quantity3 = str(50.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity3]])
    assert calculatorFrameModel.getNumberOfFoodStuff() == 2
    assert calculatorFrameModel.dictFoodStuff[foodname1].getData("quantity") == approx(float(quantity3))

    # Add quantity in foodname1
    quantity4 = str(150.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity4]], addQuantity=True)
    assert calculatorFrameModel.getNumberOfFoodStuff() == 2
    assert calculatorFrameModel.dictFoodStuff[foodname1].getData("quantity") == \
                        approx(float(quantity3) + float(quantity4))

    # Close demo database
    databaseManager.closeDatabase()

def test_addFoodInTable_Error():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)

    # Set a database in CalculatorFrameModel
    calculatorFrameModel.setDatabase(database)

    # Add a foodstuff with empty name
    foodname1 = ""
    quantity1 = str(200.)
    with pytest.raises(CalcalExceptions.CalcalValueError) as e:
        calculatorFrameModel.addFoodInTable([[foodname1, quantity1]])

    # Add a foodstuff with empty name
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = "a,"
    with pytest.raises(CalcalExceptions.CalcalValueError) as e:
        calculatorFrameModel.addFoodInTable([[foodname1, quantity1]])

    # Close demo database
    databaseManager.closeDatabase()

def test_updateFollowedComponents():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)

    # Set a database in CalculatorFrameModel
    calculatorFrameModel.setDatabase(database)

    # Update current followed components without food in model
    askedByUserCodes = set([400])
    calculatorFrameModel.updateFollowedComponents(askedByUserCodes)
    assert len(calculatorFrameModel.askedByUserCodes) == 1
    listComp = configApp.get('Energy', 'EnergeticComponentsCodes')
    energyComponents = set([int(code) for code in listComp.split(";")])
    energyTotalKcalCode = set([int(configApp.get('Energy', 'EnergyTotalKcalCode'))])
    waterCode = set([int(configApp.get('Water', 'WaterCode'))])
    otherComponents = energyComponents | energyTotalKcalCode | waterCode
    assert len(calculatorFrameModel.currentComponentCodes) == len(otherComponents)

    # Close demo database
    databaseManager.closeDatabase()

def test_updateFollowedComponents_withFood():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)

    # Add a foodstuff in calculatorFrameModel
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1]])

    # TestUpdate current followed components witht food in model
    compWater = 400
    askedByUserCodes = set([compWater])
    calculatorFrameModel.updateFollowedComponents(askedByUserCodes)
    assert compWater in calculatorFrameModel.dictFoodStuff[foodname1].dictComponents

    compSodium = 10110
    askedByUserCodes = set([compSodium])
    calculatorFrameModel.updateFollowedComponents(askedByUserCodes)
    assert compWater in calculatorFrameModel.dictFoodStuff[foodname1].dictComponents
    assert compSodium in calculatorFrameModel.dictFoodStuff[foodname1].dictComponents

    # Add a foodstuff in calculatorFrameModel
    foodname2 = "Légumes, pur jus (aliment moyen)"
    quantity2 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname2, quantity2]])
    assert compWater in calculatorFrameModel.dictFoodStuff[foodname2].dictComponents
    assert compSodium in calculatorFrameModel.dictFoodStuff[foodname2].dictComponents

    # Close demo database
    databaseManager.closeDatabase()

def test_getListFoodModifiedInTable():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1]])
    compWater = 400
    askedByUserCodes = set([compWater])
    calculatorFrameModel.updateFollowedComponents(askedByUserCodes)

    # Test getListFoodModifiedInTable()
    foodModif = calculatorFrameModel.getListFoodModifiedInTable()
    assert len(foodModif) == 1
    name, quantity, dictComponent = foodModif[0]
    assert name == foodname1
    assert quantity == float(quantity1)
    assert compWater in dictComponent
    assert float(dictComponent[compWater]) == approx(88.9 * 2)

    # Close demo database
    databaseManager.closeDatabase()

@pytest.mark.parametrize("nbDays", [1, 2])
def test_getTotalLineStr(nbDays):
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1]])
    compWater = 400
    askedByUserCodes = set([compWater])
    calculatorFrameModel.updateFollowedComponents(askedByUserCodes)

    # Test getTotalLineStr() 1 food in table
    nameTotal, quantityTotal, dictComponentTotal = calculatorFrameModel.getTotalLineStr(nbDays)
    assert nameTotal.startswith(_("Total"))
    if nbDays > 1:
        assert nameTotal.endswith(_("per day"))
    assert quantityTotal == approx(float(quantity1) / float(nbDays))
    assert compWater in dictComponentTotal
    foodModif = calculatorFrameModel.getListFoodModifiedInTable()
    assert len(foodModif) == 1
    name, quantity, dictComponent = foodModif[0]
    assert quantityTotal == approx(quantity / float(nbDays))
    if nbDays == 1:
        assert dictComponent == dictComponentTotal
    else:
        assert float(dictComponentTotal[compWater]) == \
                approx(float(dictComponent[compWater])/ float(nbDays))

    # Test getTotalLineStr() 2 foods in table
    foodname2 = "Légumes, pur jus (aliment moyen)"
    quantity2 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname2, quantity2]])
    nameTotal, quantityTotal, dictComponentTotal = calculatorFrameModel.getTotalLineStr(nbDays)
    foodModif = calculatorFrameModel.getListFoodModifiedInTable()
    assert len(foodModif) == 1
    name2, quantity2, dictComponent2 = foodModif[0]
    assert quantityTotal == approx((quantity + quantity2) / nbDays)
    # Enlarge tolerance to 0.1 because values are rounded for each food before adding
    assert float(dictComponentTotal[compWater]) == \
            approx((float(dictComponent[compWater]) + float(dictComponent2[compWater])) / \
                   float(nbDays), rel=1e-1)

    # Close demo database
    databaseManager.closeDatabase()

# Test getFullTable()
def test_getFullTable():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    foodname2 = "Légumes, pur jus (aliment moyen)"
    quantity2 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1], [foodname2, quantity2]])
    compWater = 400
    askedByUserCodes = set([compWater])
    calculatorFrameModel.updateFollowedComponents(askedByUserCodes)
    line0 = calculatorFrameModel.getListFoodModifiedInTable()[0]
    line1 = calculatorFrameModel.getListFoodModifiedInTable()[1]

    fullTable = calculatorFrameModel.getFullTable()
    assert len(fullTable) == 2
    assert line0 in fullTable.values()
    assert line1 in fullTable.values()

    # Close demo database
    databaseManager.closeDatabase()

# Test deleteFood()
def test_deleteFood():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    foodname2 = "Légumes, pur jus (aliment moyen)"
    quantity2 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1], [foodname2, quantity2]])
    line0 = calculatorFrameModel.getListFoodModifiedInTable()[0]
    line1 = calculatorFrameModel.getListFoodModifiedInTable()[1]
    assert calculatorFrameModel.getNumberOfFoodStuff() == 2

    calculatorFrameModel.deleteFoodInModel([foodname2], False)
    assert calculatorFrameModel.getNumberOfFoodStuff() == 1

    fullTable = calculatorFrameModel.getFullTable()
    assert len(fullTable) == 1
    assert line0 in fullTable.values()
    assert line1 not in fullTable.values()

    # Close demo database
    databaseManager.closeDatabase()

# Test groupFood()
def test_groupFood():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    foodname2 = "Légumes, pur jus (aliment moyen)"
    quantity2 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1], [foodname2, quantity2]])
    line0 = calculatorFrameModel.getListFoodModifiedInTable()[0]
    line1 = calculatorFrameModel.getListFoodModifiedInTable()[1]
    assert calculatorFrameModel.getNumberOfFoodStuff() == 2

    # Take a picture of model
    fullTableBeforeGroup = calculatorFrameModel.getFullTable()

    # Group 2 foodstuffs
    familyName = "New Family"
    productName = "Jus Fruit Légume"
    try:
        database.deleteUserProduct(productName)
    except AssertionError:
        pass
    listFoodName2Group = [foodname1, foodname2]
    calculatorFrameModel.groupFood(familyName, productName, listFoodName2Group)
    fullTableAfterGroup = calculatorFrameModel.getFullTable()

    assert calculatorFrameModel.getNumberOfFoodStuff() == 1
    assert calculatorFrameModel.dictFoodStuff[productName].getData("quantity") == \
            approx(float(quantity1) + float(quantity2))
    assert fullTableBeforeGroup != fullTableAfterGroup

    calculatorFrameModel.deleteFoodInModel([productName], True)

    # Close demo database
    databaseManager.closeDatabase()

# Test ungroupFood()
def test_ungroupFood():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)

    # Create a group
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    foodname2 = "Légumes, pur jus (aliment moyen)"
    quantity2 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1], [foodname2, quantity2]])
    fullTableBeforeGroup = calculatorFrameModel.getFullTable()
    familyName = "New Family"
    productName = "Jus Fruit Légume"
    try:
        database.deleteUserProduct(productName)
    except AssertionError:
        pass
    listFoodName2Group = [foodname1, foodname2]
    calculatorFrameModel.groupFood(familyName, productName, listFoodName2Group)

    # Ungroup food
    calculatorFrameModel.ungroupFood(productName)

    # Take a picture of model
    fullTableAfterUngroup = calculatorFrameModel.getFullTable()
    assert fullTableBeforeGroup == fullTableAfterUngroup

    calculatorFrameModel.deleteFoodInModel([productName], True)

    # Close demo database
    databaseManager.closeDatabase()

def test_ungroupFoodAndUpdateExisting():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)

    # Create a group
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    foodname2 = "Légumes, pur jus (aliment moyen)"
    quantity2 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1], [foodname2, quantity2]])
    familyName = "New Family"
    productName = "Jus Fruit Légume"
    try:
        database.deleteUserProduct(productName)
    except AssertionError:
        pass
    listFoodName2Group = [foodname1, foodname2]
    calculatorFrameModel.groupFood(familyName, productName, listFoodName2Group)

    # Insert a produst in model that is already in the group
    foodname3 = foodname1
    quantity3 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname3, quantity3]])

    # Ungroup food
    calculatorFrameModel.ungroupFood(productName)

    # 2 food must be in the list :
    assert calculatorFrameModel.getNumberOfFoodStuff() == 2
    # The quantity of foodname3 must have been updated
    assert calculatorFrameModel.dictFoodStuff[foodname3].getData("quantity") == \
            approx(float(quantity1) + float(quantity3))

    calculatorFrameModel.deleteFoodInModel([productName], True)
    # Close demo database
    databaseManager.closeDatabase()

def test_portion():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)

    # Portion field
    portionName = "test portion"
    portionDate = "10/11/2016"
    portionPatient = "TMD"
    portionType = "Ration"
    portionPeriod = "Matin"

    # Try to delete this portion in database if it exists
    portionCode, exists = database.getPortionCode(portionName, portionDate, portionPatient)
    if exists:
        database.deletePortion(portionCode)

    # Create a portion
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    foodname2 = "Légumes, pur jus (aliment moyen)"
    quantity2 = str(100.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1], [foodname2, quantity2]])
    listFoodAdded = calculatorFrameModel.getListFoodModifiedInTable()
    listFoodname = [element[0] for element in listFoodAdded]
    calculatorFrameModel.savePortion([portionName, portionDate, portionPatient,
                                      portionType, portionPeriod])
    portionCode, exists = database.getPortionCode(portionName, portionDate, portionPatient)
    assert exists

    # Delete all food in this model
    fullTableStart = calculatorFrameModel.getFullTable()
    totalLineStart = calculatorFrameModel.getTotalLineStr()
    calculatorFrameModel.deleteFoodInModel(listFoodname, inDatabase=False)
    assert calculatorFrameModel.getNumberOfFoodStuff() == 0

    # Insert portion in model
    calculatorFrameModel.displayPortion(portionCode)
    assert calculatorFrameModel.getNumberOfFoodStuff() == 2
    fullTableAfterInsert = calculatorFrameModel.getFullTable()
    totalLineAfterInsert = calculatorFrameModel.getTotalLineStr()
    assert fullTableAfterInsert == fullTableStart
    assert totalLineAfterInsert == totalLineStart

    # Try to delete this portion in database if it exists
    portionCode, exists = database.getPortionCode(portionName, portionDate, portionPatient)
    if exists:
        database.deletePortion(portionCode)
    # Close demo database
    databaseManager.closeDatabase()

def test_getEnergyComponentsNames():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)

    listComp = configApp.get('Energy', 'EnergeticComponentsCodes')
    energeticComponentsCodes = [int(code) for code in listComp.split(";")]
    listEnergyComponentsNames = calculatorFrameModel.getEnergyComponentsNames()
    assert len(listEnergyComponentsNames) == len(energeticComponentsCodes) + 1

    # Close demo database
    databaseManager.closeDatabase()

def test_getEnergyRatio():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)

    # Create a foodstuff
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(200.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1]])

    # Get energetics components values
    listComp = configApp.get('Energy', 'EnergeticComponentsCodes')
    energeticComponentsCodes = [int(code) for code in listComp.split(";")]
    listSupplyEnergyRatio, listValues, listSupplyEnergy = calculatorFrameModel.getEnergyRatio()
    assert len(listSupplyEnergyRatio) == len(energeticComponentsCodes) + 1
    assert len(listValues) == len(energeticComponentsCodes) + 1
    assert len(listSupplyEnergy) == len(energeticComponentsCodes) + 1

    # Close demo database
    databaseManager.closeDatabase()

def test_getWaterEnergy():
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()
    calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
    calculatorFrameModel.setDatabase(database)

    waterUnknownValue = configApp.get('Water', 'WaterUnknownValue')

    # Test with no food Selected
    isDataAvailable, waterInFood, waterNeeded, isEnougthWater = calculatorFrameModel.getWaterEnergy()
    assert not isDataAvailable
    assert waterInFood == waterUnknownValue
    assert waterNeeded == waterUnknownValue
    assert isEnougthWater

    # Create a foodstuff
    foodname1 = "Jus de fruits (aliment moyen)"
    quantity1 = str(20.)
    calculatorFrameModel.addFoodInTable([[foodname1, quantity1]])

    # Test with food Selected (enougth water)
    isDataAvailable, waterInFood, waterNeeded, isEnougthWater = calculatorFrameModel.getWaterEnergy()
    assert isDataAvailable
    assert waterInFood != waterUnknownValue
    assert waterNeeded != waterUnknownValue
    assert isEnougthWater

    # Create a lot of foodstuff that bring a lot of energy
    foodname2 = "Beurre allégé (aliment moyen)"
    quantity2 = str(250.)
    calculatorFrameModel.addFoodInTable([[foodname2, quantity2]])

    # Test with food Selected (enougth water)
    isDataAvailable, waterInFood, waterNeeded, isEnougthWater = calculatorFrameModel.getWaterEnergy()
    assert isDataAvailable
    assert waterInFood != waterUnknownValue
    assert waterNeeded != waterUnknownValue
    assert not isEnougthWater

    # Close demo database
    databaseManager.closeDatabase()

