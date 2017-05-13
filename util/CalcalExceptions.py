# -*- coding: utf-8 -*-
"""
************************************************************************************
programme : CalcalExceptions.py
Auteur : Thierry Maillard (TMD)
Date : 23/10/2016

Role : Project exceptions.
************************************************************************************
"""
import logging

class CalcalValueError(ValueError):
    '''Triggered when an user input value is bad'''
    def __init__(self, configApp, message, *args):
        super(CalcalValueError, self).__init__(message, *args)
        self.configApp = configApp
        self.logger = logging.getLogger(configApp.get('Log', 'LoggerName'))
        self.logger.error(_("Input error") + " : " + message)

class CalcalInternalError(ValueError):
    '''Triggered when there is a programming error'''
    def __init__(self, configApp, message, *args):
        super(CalcalInternalError, self).__init__(message, *args)
        self.configApp = configApp
        self.logger = logging.getLogger(configApp.get('Log', 'LoggerName'))
        self.logger.error(_("Internal error") + " : " + message)

class DatabaseException(Exception):
    '''Triggered when error with database'''
    def __init__(self, configApp, message, *args):
        super(DatabaseException, self).__init__(message, *args)
        self.configApp = configApp
        self.logger = logging.getLogger(configApp.get('Log', 'LoggerName'))
        self.logger.error(_("Database error") + " : " + message)
