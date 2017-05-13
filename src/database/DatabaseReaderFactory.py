# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : DatabaseReaderFactory
Author : Thierry Maillard (TMD)
Date  : 13/6/2016

Role : Return a database reader according parameters.
************************************************************************************
"""
from database import CiqualReader

class DatabaseReaderFactory():
    """ Classused to get a database reader using the design pattern Factory.
    """

    def getInstance(configApp, localDirPath, typeDatabase, connDB, dbname):
        """ retourne un controleur adapté à celui demandé par typeControler """
        databaseReader = None
        if typeDatabase  == "CIQUAL":
            databaseReader = CiqualReader.CiqualReader(configApp, localDirPath, connDB, dbname)
        else:
            raise Exception("typeDatabase " + typeDatabase + " non implemented.")
        return databaseReader

    # To use method getInstance() without instantiating class : static method
    getInstance = staticmethod(getInstance)
