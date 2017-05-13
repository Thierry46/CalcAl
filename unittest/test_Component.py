#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_Component.py
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

from model import Component
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

    codeProduct = 2004
    codeComponent = 400
    quantity = 200.
    component = Component.Component(configApp, database, codeProduct, codeComponent, quantity)

    assert component.getData("productCode") == 2004
    assert component.getData("constituantCode") == 400
    assert component.getData("value") == approx(88.9)
    assert component.getData("quantity") == approx(2.0 * 88.9)
    assert component.getData("qualifValue") == 'N'
    assert component.getData("name") == "Eau"

    # Close demo database
    databaseManager.closeDatabase()

def test_updateQuantity():
    """ Test updateQuantity """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    codeProduct = 2004
    codeComponent = 400
    quantity = 200.
    component = Component.Component(configApp, database, codeProduct, codeComponent, quantity)

    assert component.getData("quantity") == approx(2.0 * 88.9)
    component.updateQuantity(100.0)
    assert component.getData("quantity") == approx(88.9)

    # Close demo database
    databaseManager.closeDatabase()

@pytest.mark.parametrize("qualifier, value, strOK",
    [
     ("N", 23.1, "23.1"),
     ("-", 0.0, "-"),
     ("-", 25.8, "-"),
     ("T", 0.0, "Traces"),
     ("T", 25.8, "Traces"),
     ("<", 25.8, "< 25.8")
     ])
def test_getValueFormated(qualifier, value, strOK):
    """ Test getValueFormated """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    codeProduct = 2004
    codeComponent = 400
    quantity = 200.
    component = Component.Component(configApp, database, codeProduct, codeComponent, quantity)

    # Start test
    component.setData("qualifValue", qualifier)
    component.setData("quantity", value)
    assert component.getValueFormated() == _(strOK)

    # Close demo database
    databaseManager.closeDatabase()

def test_getValueFormatedError():
    """ Test getValueFormated """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    codeProduct = 2004
    codeComponent = 400
    quantity = 200.
    component = Component.Component(configApp, database, codeProduct, codeComponent, quantity)

    # Start test
    badQualifier = "XX"
    component.setData("qualifValue", badQualifier)
    component.setData("quantity", 45.0)
    with pytest.raises(CalcalExceptions.CalcalInternalError) as e:
        component.getValueFormated()
    print(e)
    assert "getValueFormated : unknown value qualifier : " in str(e.value)
    assert badQualifier in str(e.value)

    # Close demo database
    databaseManager.closeDatabase()
