#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_ModelBaseData.py
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
import configparser
import os.path

import pytest

from model import ModelBaseData
from database import DatabaseManager
import CalcAl

# Code to execute before and at the end of all test
@pytest.fixture(scope="session")
def initEnv():
    """ Code to be executed when called by test function """
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

    nameElement = "Test"
    modelBaseData = ModelBaseData.ModelBaseData(configApp, database, nameElement)
    assert modelBaseData.configApp == configApp
    assert modelBaseData.database == database
    assert modelBaseData.nameElement == nameElement
    assert len(modelBaseData.dictData) == 0

    # Close demo database
    databaseManager.closeDatabase()

def test_setgetData():
    """ Test accessors setData and getData """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    nameElement = "Test"
    modelBaseData = ModelBaseData.ModelBaseData(configApp, database, nameElement)

    key = "Key"
    value = "Example"
    modelBaseData.setData(key, value)
    assert len(modelBaseData.dictData) == 1
    assert modelBaseData.getData(key) == value

    key2 = "Key2"
    value2 = "Example2"
    modelBaseData.setData(key2, value2)
    assert len(modelBaseData.dictData) == 2
    assert modelBaseData.getData(key2) == value2

    # Close demo database
    databaseManager.closeDatabase()

def test_updateData():
    """ Test updateData """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    nameElement = "Test"
    modelBaseData = ModelBaseData.ModelBaseData(configApp, database, nameElement)

    key = "Key"
    value = "Example"
    key2 = "Key2"
    value2 = "Example2"
    modelBaseData.setData(key, value)
    modelBaseData.setData(key2, value2)

    valueNew = "Example New"
    key3 = "Key3"
    value3 = "Example3"
    otherDict = {key : valueNew, key3 : value3}
    modelBaseData.update(otherDict)
    assert modelBaseData.getData(key) == valueNew
    assert modelBaseData.getData(key2) == value2
    assert modelBaseData.getData(key3) == value3
    assert len(modelBaseData.dictData) == 3

    # Close demo database
    databaseManager.closeDatabase()

def test_clear():
    """ Test accessors setData and getData """
    # Call init fixture
    configApp, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    nameElement = "Test"
    modelBaseData = ModelBaseData.ModelBaseData(configApp, database, nameElement)

    key = "Key"
    value = "Example"
    modelBaseData.setData(key, value)

    modelBaseData.clear()
    assert len(modelBaseData.dictData) == 0

    # Close demo database
    databaseManager.closeDatabase()
