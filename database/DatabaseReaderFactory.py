# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : DatabaseReaderFactory
Author : Thierry Maillard (TMD)
Date  : 13/6/2016 - 17/12/2016

Role : Return a database reader according parameters.
************************************************************************************
"""
import os.path

class DatabaseReaderFactory():
    """ Class used to get a database reader using the design pattern Factory.
    """

    def getInstance(configApp, dirProject, typeDatabase, connDB, dbname):
        """ return a database reader """
        databaseReader = None

        # Test if reader plugin exists
        readerBaseName = typeDatabase
        if typeDatabase.startswith("Ciqual"):
            readerBaseName = "Ciqual"
        readersPath = os.path.join(dirProject,
                                   configApp.get("Resources", "ReadersDir"),
                                   readerBaseName + "_Reader.py")
        if not os.path.isfile(readersPath):
            raise ImportError(_("Reader for base") + " " + typeDatabase + " " + _("not found") +
                              " !\n" + _("Please contact support team") + " : " +
                              configApp.get("Version", "EmailSupport1") + " " + _("or") + " " +
                              configApp.get("Version", "EmailSupport2"))

        if typeDatabase.startswith("Ciqual"):
            from . import Ciqual_Reader
            databaseReader = Ciqual_Reader.Ciqual_Reader(configApp, dirProject,
                                                         connDB, dbname, typeDatabase)
        elif typeDatabase == "USDA_28":
            from . import USDA_28_Reader
            databaseReader = USDA_28_Reader.USDA_28_Reader(configApp, dirProject,
                                                           connDB, dbname)
        else:
            raise ImportError(_("Reader for base") + " " + typeDatabase + " " +
                              _("can not be loaded") +
                              " !\n" + _("Please contact support team") + " : " +
                              configApp.get("Version", "EmailSupport1") + " " + _("or") + " " +
                              configApp.get("Version", "EmailSupport2"))
        return databaseReader

    # To use method getInstance() without instantiating class : static method
    getInstance = staticmethod(getInstance)
