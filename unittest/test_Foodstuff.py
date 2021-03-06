#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_Foodstuff.py
Author : Thierry Maillard (TMD)
Date : 27/10/2016
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
import gettext
import platform

from model import Foodstuff
from database import DatabaseManager
from util import CalcalExceptions
import CalcAl

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

def test_init():
    """ Test constructor """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    foodname = "Jus de fruits (aliment moyen)"
    listFollowedComponents = []
    quantity = 200.
    foodstuff = Foodstuff.Foodstuff(configApp, database, foodname, quantity, listFollowedComponents)

    assert foodstuff.getData("name") == foodname
    assert foodstuff.getData("code") == 2004
    assert foodstuff.getData("familyName") == "Aliments moyens pour les enquêtes Inca"
    assert foodstuff.getData("source") == "CIQUAL2013-Donneescsv.csv"
    assert foodstuff.getData("dateSource") == "2013"
    assert foodstuff.getData("urlSource") == "https://pro.anses.fr/tableciqual"
    assert foodstuff.getData("isGroup") == False
    assert len(foodstuff.dictComponents) == 0
    assert foodstuff.getData("quantity") == approx(quantity)

    # Close demo database
    databaseManager.closeDatabase()

def test_initWithComponents():
    """ Test constructor """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    foodname = "Jus de fruits (aliment moyen)"
    listFollowedComponents = [400, 10110, 10120]
    quantity = 100.
    foodstuff = Foodstuff.Foodstuff(configApp, database, foodname, quantity, listFollowedComponents)

    assert len(foodstuff.dictComponents) == 3
    for codeComp in listFollowedComponents:
        assert foodstuff.dictComponents[codeComp].getData("productCode") == foodstuff.getData("code")
        assert foodstuff.dictComponents[codeComp].getData("constituantCode") == codeComp
        value = foodstuff.dictComponents[codeComp].getData("value")
        quantity = foodstuff.dictComponents[codeComp].getData("quantity")
        assert value == approx(quantity)

    # Close demo database
    databaseManager.closeDatabase()

def test_updateQuantity():
    """ Test updateQuantity """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    foodname = "Jus de fruits (aliment moyen)"
    listFollowedComponents = []

    quantity = 100.
    foodstuff = Foodstuff.Foodstuff(configApp, database, foodname, quantity, listFollowedComponents)
    assert foodstuff.getData("quantity") == approx(quantity)

    quantity = 200.
    foodstuff.updateQuantity(quantity)
    assert foodstuff.getData("quantity") == approx(quantity)

    # Close demo database
    databaseManager.closeDatabase()

def test_updateQuantity_add():
    """ Test updateQuantity with addQuantity parameter True"""
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    foodname = "Jus de fruits (aliment moyen)"
    listFollowedComponents = []

    quantity = 100.
    foodstuff = Foodstuff.Foodstuff(configApp, database, foodname, quantity, listFollowedComponents)

    quantity2 = 200.
    foodstuff.updateQuantity(quantity2, addQuantity=True)
    assert foodstuff.getData("quantity") == approx(quantity + quantity2)

    # Close demo database
    databaseManager.closeDatabase()

def test_updateQuantityWithComponents():
    """ Test updateQuantity with components checked """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    foodname = "Jus de fruits (aliment moyen)"
    listFollowedComponents = [400, 10110, 10120]
    quantity = 100.
    foodstuff = Foodstuff.Foodstuff(configApp, database, foodname, quantity, listFollowedComponents)

    assert foodstuff.getData("quantity") == approx(quantity)

    quantity = 200.
    foodstuff.updateQuantity(quantity)
    for codeComp in listFollowedComponents:
        value = foodstuff.dictComponents[codeComp].getData("value")
        quantity = foodstuff.dictComponents[codeComp].getData("quantity")
        assert 2.0 * value == approx(quantity)

    # Close demo database
    databaseManager.closeDatabase()

def test_getFormattedValue():
    """ Test getFormattedValue """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    foodname = "Jus de fruits (aliment moyen)"
    listFollowedComponents = []
    quantity = 200.
    foodstuff = Foodstuff.Foodstuff(configApp, database, foodname, quantity, listFollowedComponents)

    name, quantityR, dictComponentValueFormated = foodstuff.getFormattedValue()
    assert name == foodname
    assert quantityR == quantity
    assert len(dictComponentValueFormated) == 0

    # Close demo database
    databaseManager.closeDatabase()
