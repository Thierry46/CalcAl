#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Name : test_Database_Pathologies.py
    Author : Thierry Maillard (TMD)
    Date : 23/11/2016
    Role : Tests unitaires du projet Calcal avec py.test
        module Database, fonctions pathologies
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
import os
import os.path
import shutil

import pytest

import CalcAl
from database import DatabaseManager

# Code to execute before and at the end of all test
@pytest.fixture(scope="session")
def initEnv():
    """ Code to be executed when called by test function """
    fileConfigApp = 'CalcAl.ini'
    configApp = configparser.RawConfigParser()
    configApp.read(fileConfigApp, encoding="utf-8")
    CalcAl.setLocaleCalcal(configApp, '.')

    # Create and open test database
    baseDirPath = os.path.join(configApp.get('Resources', 'ResourcesDir'),
                               configApp.get('Resources', 'DatabaseDir'))
    baseTestDirPath = os.path.join(baseDirPath, "test")
    if not os.path.exists(baseTestDirPath):
        os.mkdir(baseTestDirPath)
    demoDatabaseName = configApp.get('Resources', 'DemoDatabaseName')
    shutil.copyfile(os.path.join(baseDirPath, demoDatabaseName),
                    os.path.join(baseTestDirPath, demoDatabaseName))

    databaseManager = DatabaseManager.DatabaseManager(configApp, '.', baseTestDirPath)
    databaseManager.openDatabase(demoDatabaseName)

    # Init user table in test database
    database = databaseManager.getDatabase()
    database.createUserTables()

    # Values returned to each test calling function
    return configApp, databaseManager

def test_emptyPatholology():
    """ Test getter on empty database """
    # Call init fixture
    dummy, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    assert database.getDefinedPathologiesNames() == []

    # Close demo database
    databaseManager.closeDatabase()

def test_1Patholology():
    """ Test inserting a pathology in database """
    # Call init fixture
    dummy, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    name = "diabete type A"
    description = "Probleme pancréas"
    reference = "TMD Bof Bof"
    listConstituantsCodes = [400, 328]
    database.deletePathology(name)
    assert name not in database.getDefinedPathologiesNames()

    database.savePathology(name, description, reference, listConstituantsCodes)
    assert name in database.getDefinedPathologiesNames()

    listCompRead = database.getComponentsCodes4Pathologies([name])
    assert len(listConstituantsCodes) == len(listCompRead)
    for component in listConstituantsCodes:
        assert component in listCompRead

    nameR, descriptionR, referenceR, listCompRead2 = database.getDefinedPathologiesDetails(name)
    assert name == nameR
    assert description == descriptionR
    assert reference == referenceR
    assert listCompRead2 == listCompRead

    # Test update pathology
    name = "diabete type A"
    description = "Probleme pancréas et cellules"
    reference = "TMD Bof Bof 2"
    listConstituantsCodes = [400, 328, 10110]
    database.savePathology(name, description, reference, listConstituantsCodes)
    nameR, descriptionR, referenceR, listCompRead = database.getDefinedPathologiesDetails(name)
    assert name == nameR
    assert description == descriptionR
    assert reference == referenceR
    assert len(listConstituantsCodes) == len(listCompRead)
    for component in listConstituantsCodes:
        assert component in listCompRead

    database.deletePathology(name)
    assert name not in database.getDefinedPathologiesNames()

    # Close demo database
    databaseManager.closeDatabase()

def test_1PatholologyError():
    """ Test exception while inserting a pathology in database """
    # Call init fixture
    dummy, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    name = ""
    description = "Probleme pancréas"
    reference = "TMD Bof Bof"
    listConstituantsCodes = [400, 328]
    with pytest.raises(ValueError):
        database.savePathology(name, description, reference, listConstituantsCodes)

    name = "diabete type A"
    description = "Probleme pancréas"
    reference = "TMD Bof Bof"
    listConstituantsCodes = []
    with pytest.raises(ValueError):
        database.savePathology(name, description, reference, listConstituantsCodes)

    with pytest.raises(ValueError):
        database.getComponentsCodes4Pathologies([])

    # Unknown constituant
    name = "diabete type A"
    description = "Probleme pancréas"
    reference = "TMD Bof Bof"
    listConstituantsCodes = [999999]
    with pytest.raises(ValueError):
        database.savePathology(name, description, reference, listConstituantsCodes)

    name = "diabete type B"
    with pytest.raises(ValueError):
        database.getComponentsCodes4Pathologies([name])

    database.deletePathology(name)

    # Close demo database
    databaseManager.closeDatabase()

def test_2Patholology():
    """ Test getting components for 2 pathologies in database """
    # Call init fixture
    dummy, databaseManager = initEnv()
    database = databaseManager.getDatabase()

    name1 = "diabete type A"
    description1 = "Probleme pancréas"
    reference1 = "TMD Bof Bof"
    listConstituantsCodes1 = [400, 328]
    database.deletePathology(name1)
    assert name1 not in database.getDefinedPathologiesNames()
    database.savePathology(name1, description1, reference1, listConstituantsCodes1)

    name2 = "diabete type B"
    description2 = "Probleme pancréas et cellules"
    reference2 = "TMD Bof Bof 2"
    listConstituantsCodes2 = [400, 328, 10110]
    database.savePathology(name2, description2, reference2, listConstituantsCodes2)
    assert len(database.getDefinedPathologiesNames()) == 2

    waitedSetComp = set(listConstituantsCodes1) | set(listConstituantsCodes2)
    listCompRead = database.getComponentsCodes4Pathologies([name1, name2])
    assert len(listCompRead) == len(waitedSetComp)
    for component in waitedSetComp:
        assert component in listCompRead

    database.deletePathology(name1)
    database.deletePathology(name2)
    # Close demo database
    databaseManager.closeDatabase()
