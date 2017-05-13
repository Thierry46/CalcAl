#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_Data_DateUtil.py
Author : Thierry Maillard (TMD)
Date : 24/11/2016
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
import datetime
import configparser
import pytest

import CalcAl
from util import DateUtil

# Code to execute before and at the end of all test
@pytest.fixture(scope="session")
def initEnv():
    """ Code to be executed when called by test function """
    fileConfigApp = 'CalcAl.ini'
    configApp = configparser.RawConfigParser()
    configApp.read(fileConfigApp, encoding="utf-8")
    CalcAl.setLocaleCalcal(configApp, '.')

@pytest.mark.parametrize("dateStr", ["2016/11/24", "2016/09/24", "2016/09/04"])
def test_formatDate_OK(dateStr):
    # Call init fixture
    initEnv()

    dateFormated = DateUtil.formatDate(dateStr)
    assert dateStr == dateFormated

@pytest.mark.parametrize("dateStr, formatStr", [("2016/11/2", '%Y/%m/%d'),
                                             ("2016/9/24", '%Y/%m/%d'),
                                             ("6/9/04", '%d/%m/%y'),
                                             ("16/9/24", '%d/%m/%y'),
                                             ("16/09/24", '%d/%m/%y'),
                                             ("16/09/04", '%d/%m/%y'),
                                             ("9/4/2016", '%d/%m/%Y'),
                                             ("09/04/2016", '%d/%m/%Y'),
                                             ("9/4/06", '%d/%m/%y'),
                                             ("09/04/16", '%d/%m/%y'),
                                             ("09:04:16", '%d:%m:%y'),
                                             ("2016:11:2", '%Y:%m:%d')])
def test_formatDate_convert_OK(dateStr, formatStr):
    # Call init fixture
    initEnv()

    dateFormated = DateUtil.formatDate(dateStr)
    assert dateStr != dateFormated
    assert datetime.datetime.strptime(dateStr, formatStr) == \
            datetime.datetime.strptime(dateFormated, '%Y/%m/%d')

@pytest.mark.parametrize("dateStr", ["2016/11 24", "2016:09/24", "choucroute",
                                     "16 novembre 2016", "31/2/2016", "31/12/6"])
def test_formatDate_Error(dateStr):
    # Call init fixture
    initEnv()

    with pytest.raises(ValueError):
        DateUtil.formatDate(dateStr)
