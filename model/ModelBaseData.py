# -*- coding: utf-8 -*-
"""
************************************************************************************
Classe : ModelBaseData
Auteur : Thierry Maillard (TMD)
Date : 25/10/2016

Rôle : Base class for model classes.
************************************************************************************
"""

import logging
from util.CalcalExceptions import CalcalInternalError

class ModelBaseData(object):
    """ Base class for model classes """

    def __init__(self, configApp, database, nameElement) :
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
