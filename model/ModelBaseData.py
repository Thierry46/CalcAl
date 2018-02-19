# -*- coding: utf-8 -*-
"""
************************************************************************************
Classe : ModelBaseData
Auteur : Thierry Maillard (TMD)
Date : 25/10/2016

Rôle : Base class for model classes.

Licence : GPLv3
Copyright (c) 2016 - Thierry Maillard

This file is part of CalcAl project.

CalcAl project is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CalcAl project is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CalcAl project.  If not, see <http://www.gnu.org/licenses/>.
************************************************************************************
"""

import logging

class ModelBaseData(object):
    """ Base class for model classes """

    def __init__(self, configApp, database, nameElement):
        self.configApp = configApp
        self.logger = logging.getLogger(configApp.get('Log', 'LoggerName'))
        self.database = database
        self.nameElement = nameElement
        self.dictData = dict()

    def getData(self, key):
        """ Get value for a key of this model data """
        return self.dictData[key]

    def setData(self, key, value):
        """ Set value for a key of this model data """
        self.dictData[key] = value

    def update(self, otherDictData):
        """ Update keys and values of this model data """
        self.dictData.update(otherDictData)

    def clear(self):
        """ Empty this model """
        self.dictData.clear()

    def __str__(self):
        """ Return this object as a string """
        retStr = self.nameElement + " contains "
        retStr += str(self.dictData)
        return retStr
