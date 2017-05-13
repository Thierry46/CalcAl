# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : DatabaseManager
Author : Thierry Maillard (TMD)
Date  : 31/7/2016 - 2/10/2016

Role : Manage database operations for CalcAl software.
************************************************************************************
"""
import logging
import os.path
import shutil

from . import Database

class DatabaseManager():
    """ Manage database operations for CalcAl software """

    def __init__(self, configApp, dirProject, baseDirPath):
        """ Initialize a database
            dirProject : project directory
            baseDirPath : path to user's dataBase
            """
        self.configApp = configApp
        self.dirProject = dirProject
        self.baseDirPath = baseDirPath
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.extDB = self.configApp.get('Resources', 'DatabaseExt')
        self.currentDatabase = None

    def getDatabase(self):
        """ return  current Database object or None if no database in use"""
        return self.currentDatabase

    def closeDatabase(self):
        """ Close database in use"""
        if self.currentDatabase:
            self.currentDatabase.close()
            self.currentDatabase = None
            self.logger.info("DatabaseManager/closeDatabase() : database closed")
        else:
            self.logger.debug("DatabaseManager/closeDatabase() : no database opened")

    def openDatabase(self, dbName):
        """ open a database which name dbName is given in parameter """
        self.logger.debug("DatabaseManager/openDatabase() : try to open " + dbName + "...")
        databasePath = os.path.join(self.baseDirPath, dbName)
        database = Database.Database(self.configApp, self.dirProject)
        database.open(databasePath)
        self.currentDatabase = database
        self.logger.info("DatabaseManager/openDatabase() : database " + dbName + " opened")

    def existsDatabase(self, dbName):
        """ return True if database dbName given exists """
        databasePath = self.buildDbNamePath(dbName)
        return os.path.exists(databasePath)

    def buildDbNamePath(self, dbName):
        """return full path for short name dbmame """
        if not dbName.endswith(self.extDB):
            dbName = dbName + self.extDB
        databasePath = os.path.join(self.baseDirPath, dbName)
        return databasePath

    def initDBFromFile(self, dbName, databaseType, initFile):
        """ Create a new database databasePath by reading a file initFile """
        database = Database.Database(self.configApp, self.dirProject)
        databasePath = self.buildDbNamePath(dbName)
        database.initDBFromFile(databasePath, databaseType, initFile)
        database.close()

    def getListDatabaseInDir(self):
        """ return a list of database names that already exists """
        listDBFiles = [filename for filename in os.listdir(self.baseDirPath)
                       if filename.endswith(self.extDB)]
        listDBFiles.sort()
        return listDBFiles

    def deleteDatabase(self, dbName):
        """ Delete a database giving its short name """
        if dbName != self.configApp.get('Resources', 'DemoDatabaseName'):
            if self.existsDatabase(dbName):
                databasePath = self.buildDbNamePath(dbName)
                os.remove(databasePath)
            else:
                raise ValueError(_("The database") + " " + dbName + " " +
                                 _("doesn't exist") + " !")

        else:
            raise ValueError(_("The database") + " " + dbName + " " +
                             _("can't be deleted"))

    def joinDatabase(self, dbNameMaster, dbNameSecondary, dbNameResult):
        """ Join 2 databases """
        # Duplicate master Database to result database
        databaseMasterPath = self.buildDbNamePath(dbNameMaster)
        databaseResultPath = self.buildDbNamePath(dbNameResult)
        shutil.copyfile(databaseMasterPath, databaseResultPath)

        # Merge table from dbNameSecondary in dbNameResult
        databaseResult = Database.Database(self.configApp, self.dirProject)
        databaseResult.open(databaseResultPath)
        databaseSecondaryPath = self.buildDbNamePath(dbNameSecondary)
        databaseResult.joinDatabase(databaseSecondaryPath)
        databaseResult.close()
