# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : DatabaseReaderFactory
Author : Thierry Maillard (TMD)
Date  : 13/6/2016 - 17/12/2016

Role : Return a database reader according parameters.

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
import os.path

class DatabaseReaderFactory():
    """ Class used to get a database reader using the design pattern Factory.
    """

    # Decorator to use method getValueFormatedStatic()
    # without instantiating class : static method
    @staticmethod
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
