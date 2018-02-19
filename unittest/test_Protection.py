#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Name : test_Protection.py
Author : Thierry Maillard (TMD)
Date : 25/6/2017
Role : Unit tests for module Protection of Calcal project with py.test
Use : See unittest.sh

Licence : GPLv3
Copyright (c) 2017 - Thierry Maillard

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
import logging
import pytest

import CalcAl
from util import Protection

# Code to execute before and at the end of all test
@pytest.fixture(scope="session")
def initEnv():
    """ Code to be executed when called by test function """
    fileConfigApp = 'CalcAl.ini'
    configApp = configparser.RawConfigParser()
    configApp.read(fileConfigApp, encoding="utf-8")
    CalcAl.setLocaleCalcal(configApp, '.')
    logger = logging.getLogger(configApp.get('Log', 'LoggerName'))
    return logger

def test_generateCryptingKeyEqual():
    """ Test Protection.generateCryptingKey() with same parameters : should give the same key """
    # Call init fixture
    logger = initEnv()

    platformId = "My-machine"
    userId = "user foo"
    userDir = "/home/user foo/Documents"
    key1 = Protection.generateCryptingKey(logger, platformId, userId, userDir)
    key2 = Protection.generateCryptingKey(logger, platformId, userId, userDir)
    assert len(key1) == 56
    assert key1 == key2

@pytest.mark.parametrize("platformId, userId, userDir",
                         [('My-machine', 'thierry',
                           '/Users/thierry/Documents/CalcAl_data'),
                          ('Darwin-16.6.0-x86_64-i386-64bit', 'userPP',
                           '/Users/thierry/Documents/CalcAl_data'),
                          ('Darwin-16.6.0-x86_64-i386-64bit', 'thierry',
                           '/Users/userPP/Documents/CalcAl_data')])
def test_generateCryptingKeyDifferent(platformId, userId, userDir):
    """ Test Protection.generateCryptingKey() with different parameters :
        returned keys must be different """
    # Call init fixture
    logger = initEnv()

    # Reference
    platformIdRef = 'Darwin-16.6.0-x86_64-i386-64bit'
    userIdRef = 'thierry'
    userDirRef = '/Users/thierry/Documents/CalcAl_data'
    keyRef = Protection.generateCryptingKey(logger, platformIdRef, userIdRef, userDirRef)

    # Parameter variation
    key = Protection.generateCryptingKey(logger, platformId, userId, userDir)
    assert keyRef != key
