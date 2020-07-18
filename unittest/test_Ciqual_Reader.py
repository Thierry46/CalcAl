#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Name : test_Ciqual_Reader.py
    Author : Thierry Maillard (TMD)
    Date : 14/2/2017
    Role : Unit tests of project Calcal with py.test
        module Ciqual_Reader
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
import sqlite3
import xlrd
import pytest

import CalcAl
from database import Ciqual_Reader

# Code to execute before and at the end of all test
@pytest.fixture
def initEnv():
    """ Code to be executed when called by test function """
    fileConfigApp = 'CalcAl.ini'
    configApp = configparser.RawConfigParser()
    configApp.read(fileConfigApp, encoding="utf-8")
    CalcAl.setLocaleCalcal(configApp, '.')
    # Force getOnlyAlimentMoyen property to False
    # to consider all products in tests as default for all tests
    configApp.set('Ciqual', 'getOnlyAlimentMoyen', value="False")

    # Create and open test database
    baseDirPath = os.path.join(configApp.get('Resources', 'ResourcesDir'),
                               configApp.get('Resources', 'DatabaseDir'))
    baseTestDirPath = os.path.join(baseDirPath, "test")
    if not os.path.exists(baseTestDirPath):
        os.mkdir(baseTestDirPath)
    databasePath = os.path.join(baseTestDirPath, 'test_CiqualReader.db')
    if os.path.exists(databasePath):
        os.remove(databasePath)
 
    # Values returned to each test calling function
    return configApp, databasePath

def initTables(connDB):
    cursor = connDB.cursor()
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
    # Create constituants values table
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS constituantsValues(
                productCode INTEGER,
                constituantCode INTEGER,
                value REAL,
                qualifValue TEXT
                )""")
    connDB.commit()
    cursor.close()
 
def test_Ciqual_Reader_init_Ok():
    """ Test init Ciqual Reader : OK """
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')

    assert reader.dateSource == '2017'

    # Close test database
    connDB.close()

def test_Ciqual_Reader_init_Pb_Year():
    """ Test init Ciqual Reader Constructor with bad parameter """
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    with pytest.raises(ValueError,
                       message="Expecting error on year 2018") as exc:
        badTypedatabase = 'Ciqual_2018'
        reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                             os.path.basename(databasePath),
                                             badTypedatabase)

    print(exc)
    assert "Ciqual_Reader : " in str(exc.value)
    assert badTypedatabase in str(exc.value)

    # Close test database
    connDB.close()

def test_analyseHeaderCiqualOK():
    """ Test analyseHeaderCiqual with header OK reda in file
        unittest/data_reader/TableCiqual2017_part1.xls """
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')
    pathXlsFileInit = "unittest/data_reader/TableCiqual2017_part1.xls"
    workbook = xlrd.open_workbook(filename=pathXlsFileInit, on_demand=True)
    sheetName = configApp.get('Ciqual', 'CiqualSheetName')
    sheetCiqual = workbook.sheet_by_name(sheetName)
    headerSplitted = sheetCiqual.row_values(0)
    cursor = connDB.cursor()
    dictConstituantsPosition = reader.analyseHeaderCiqual(cursor,
                                                          headerSplitted)
    connDB.commit()
    print("len(dictConstituantsPosition)", len(dictConstituantsPosition))
    assert dictConstituantsPosition

    # Check database content
    cursor.execute("SELECT COUNT(*) FROM constituantsNames")
    nbConstituantsDB = cursor.fetchone()[0]
    print("nbConstituantsDB", nbConstituantsDB)
    assert len(dictConstituantsPosition) == nbConstituantsDB

    # Close test database
    cursor.close()
    connDB.close()

def test_analyseHeaderCiqualPbcomponent():
    """ Test analyseHeaderCiqual
        with bad component name inserted in file
        unittest/data_reader/TableCiqual2017_part1_bad_component_eau.xls"""
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')
    pathXlsFileInit = "unittest/data_reader/TableCiqual2017_part1_bad_component_eau.xls"
    workbook = xlrd.open_workbook(filename=pathXlsFileInit, on_demand=True)
    sheetName = configApp.get('Ciqual', 'CiqualSheetName')
    sheetCiqual = workbook.sheet_by_name(sheetName)
    headerSplitted = sheetCiqual.row_values(0)
    cursor = connDB.cursor()

    with pytest.raises(ValueError,
                       message="Expecting error bad water component") as exc:
        dictConstituantsPosition = reader.analyseHeaderCiqual(cursor,
                                                              headerSplitted)
    assert "Ciqual" in str(exc.value)
    assert "pourrie" in str(exc.value)

    # Close test database
    cursor.close()
    connDB.close()

def test_analyseProductLine1CiqualOK():
    """ Test analyseProductLine reading the header and the 1st line
        of file unittest/data_reader/TableCiqual2017_part1.xls"""
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    initTables(connDB)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')
    pathXlsFileInit = "unittest/data_reader/TableCiqual2017_part1.xls"
    workbook = xlrd.open_workbook(filename=pathXlsFileInit, on_demand=True)
    sheetName = configApp.get('Ciqual', 'CiqualSheetName')
    sheetCiqual = workbook.sheet_by_name(sheetName)
    headerSplitted = sheetCiqual.row_values(0)
    cursor = connDB.cursor()

    # Get constituants positions in header
    dictConstituantsPosition = reader.analyseHeaderCiqual(cursor,
                                                          headerSplitted)
    lineSplitted = sheetCiqual.row_values(1)
    reader.analyseProductCiqual(cursor, lineSplitted, dictConstituantsPosition)
    connDB.commit()

    # Test values inserted in database
    # Test Values inserted in product table
    cursor.execute("""SELECT familyName, code, name, source, dateSource, urlSource
                        FROM products""")
    productsList = cursor.fetchall()
    print("productsList :", productsList)
    assert len(productsList) == 1
    assert productsList[0][0] == "salades composées et crudités"
    assert productsList[0][1] == 25600
    assert productsList[0][2] == "Céleri rémoulade, préemballé"
    assert productsList[0][3] == "" # Set by initDBFromFile but was not called here
    assert productsList[0][4] == "2017"
    assert productsList[0][5] == configApp.get('Ciqual', 'CiqualUrl')

    # Test Values inserted in constituantsValues table
    cursor.execute("""SELECT productCode, constituantCode, value, qualifValue
                        FROM constituantsValues""")
    constituantsValues = cursor.fetchall()
    print("constituantsValues[0] :", constituantsValues[0])
    assert len(constituantsValues) == 52
    for constituant in constituantsValues:
        assert constituant[0] == 25600
    # Test composant Eau, code=400
    cursor.execute("""SELECT value, qualifValue
                        FROM constituantsValues
                        WHERE productCode=25600 AND constituantCode==400""")
    constituantWater = cursor.fetchall()
    print("constituantWater (value, qualifValue) :", constituantWater)
    assert len(constituantWater) == 1
    assert constituantWater[0][0] == pytest.approx(78.5, 0.01)
    assert constituantWater[0][1] == 'N'

    # Close test database
    cursor.close()
    connDB.close()


def test_processFileSpecial():
    """ Test processFile on Ciqual xls file with special fields
       unittest/data_reader/TableCiqual2017_pb_fields.xls """
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    initTables(connDB)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')

    pathXlsFileInit = "unittest/data_reader/TableCiqual2017_pb_fields.xls"
    cursor = connDB.cursor()
    reader.processFile(pathXlsFileInit, cursor)

    # Test values inserted in database
    # Test Values inserted in product table
    cursor.execute("SELECT name FROM products")
    productsList = cursor.fetchall()
    print("productsList :", productsList)
    assert len(productsList) == 2
    assert productsList[0][0] == "Crudité, sans assaisonnement (aliment moyen)"
    assert productsList[1][0] == "Salade César au poulet (salade verte, fromage, croûtos, sauce)"

    # Test produit aliment moyen et composant Polyols totaux non renseigné
    # Codes composant dans resources/databas/ciqual_2016_constituants_Codes.txt
    cursor.execute("""SELECT value, qualifValue
                        FROM constituantsValues
                        WHERE productCode=25616 AND constituantCode==34000""")
    constituantValues = cursor.fetchall()
    print("constituantValues :", constituantValues)
    # A unknown contituant value is not registred in database
    assert len(constituantValues) == 0
        
    # Close test database
    cursor.close()
    connDB.close()

def test_processFilePbWorkbookName():
    """ Test processFile with a bad name for in the Ciqual xls workbook :
         unittest/data_reader/TableCiqual2017_pbworkbook.xls """
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')

    pathXlsFileInitPb = "unittest/data_reader/TableCiqual2017_pbworkbook.xls"
    cursor = connDB.cursor()
    with pytest.raises(ValueError,
                       message="Expecting error on file extension") as exc:
        reader.processFile(pathXlsFileInitPb, cursor)
    assert "Ciqual_Reader : " in str(exc.value)
    assert pathXlsFileInitPb in str(exc.value)

    # Close test database
    cursor.close()
    connDB.close()

def test_initDBFromFileReducedOK():
    """ Integration test for Ciqual Reader
         on Ciqual xls file reduced to 3 products
         unittest/data_reader/TableCiqual2017_part1.xls """
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')

    pathXlsFileInit = "unittest/data_reader/TableCiqual2017_part1.xls"
    reader.initDBFromFile(pathXlsFileInit)
    assert os.path.getsize(databasePath) > 0
    
    cursor = connDB.cursor()
    cursor.execute("SELECT name FROM products")
    productsList = cursor.fetchall()
    print("productsList :", productsList)
    assert len(productsList) == 3

    # Close test database
    cursor.close()
    connDB.close()

def test_initDBFromFileBadExtention():
    """ Test init Ciqual Reader with a file with bad extension :
        xslx instead xls """
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')

    pathXlsFileInitPb = "unittest/data_reader/TableCiqual2017_part1.xlsx"
    with pytest.raises(ValueError,
                       message="Expecting error on file extension") as exc:
        reader.initDBFromFile(pathXlsFileInitPb)
    assert "Ciqual_Reader : " in str(exc.value)
    assert ".xls" in str(exc.value)
    assert str(exc.value).endswith("1.xlsx")

    # Close test database
    connDB.close()

def test_initDBFromFileNotExist():
    """ Test init Ciqual Reader with a on existant file """
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')

    pathXlsFileInitPb = "unittest/data_reader/badPath.xls"
    with pytest.raises(ValueError,
                       message="Expecting error on unknown init file") as exc:
        reader.initDBFromFile(pathXlsFileInitPb)
    assert "Ciqual_Reader : " in str(exc.value)
    assert ".xls" in str(exc.value)
    assert "badPath.xls" in str(exc.value)

    # Close test database
    connDB.close()

def test_initDBFromFileOK():
    """ Integration test for Ciqual Reader
         on Ciqual xls full file 
         ../CIQUAL/TableCiqual2017_ExcelFR_2017 11 17.xls """
    configApp, databasePath = initEnv()
    connDB = sqlite3.connect(databasePath)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')

    pathXlsFileInit = "../CIQUAL/TableCiqual2017_2017 11 21/TableCiqual2017_ExcelFR_2017 11 17.xls"
    print("Warning table Ciqual outside CalcAl " + pathXlsFileInit)
    reader.initDBFromFile(pathXlsFileInit)

    # Check number of aliments
    cursor = connDB.cursor()
    cursor.execute("SELECT name FROM products")
    productsList = cursor.fetchall()
    print("len(productsList) :", len(productsList))
    assert len(productsList) > 1000
 
    # Close test database
    cursor.close()
    connDB.close()

def test_initDBFromFileOKOnlyAlimentMoyen():
    """ Integration test for Ciqual Reader
         on Ciqual xls full file to get only aliment moyen 
         unittest/data_reader/TableCiqual2017_pb_fields.xls """
    configApp, databasePath = initEnv()

    # Force getOnlyAlimentMoyen property to True
    # to consider only "Aliments Moyens products in tests
    configApp.set('Ciqual', 'getOnlyAlimentMoyen', value="True")

    connDB = sqlite3.connect(databasePath)
    reader = Ciqual_Reader.Ciqual_Reader(configApp, '.', connDB,
                                         os.path.basename(databasePath),
                                         'Ciqual_2017')

    pathXlsFileInit = "unittest/data_reader/TableCiqual2017_pb_fields.xls"
    reader.initDBFromFile(pathXlsFileInit)

    # Check if only Aliments Moyens products are selected
    cursor = connDB.cursor()
    cursor.execute("SELECT name FROM products")
    productsList = cursor.fetchall()
    print("productsList :", productsList)
    assert len(productsList) == 1
    for product in productsList:
        assert "(aliment moyen)" in product[0]

    # Close test database
    connDB.close()
