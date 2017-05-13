# -*- coding: utf-8 -*-
"""
************************************************************************************
Class : Component
Author : Thierry Maillard (TMD)
Date : 21/10/2016 - 18/11/2016

Role : Define a Component.

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
from model import ModelBaseData
from util import CalcalExceptions

class Component(ModelBaseData.ModelBaseData):
    """ Model for a component """
    def __init__(self, configApp, database, codeProduct, codeComponent, quantity,
                 listInfoComponent=None):
        super(Component, self).__init__(configApp, database, "Component")
        if listInfoComponent is not None:
            assert len(listInfoComponent) == 5, "Bad usage for Component constructor : len list"
            self.setData("productCode", codeProduct)
            self.setData("constituantCode", codeComponent)
            self.setData("name", listInfoComponent[1])
            self.setData("shortcut", listInfoComponent[2])
            self.setData("value", listInfoComponent[3])
            self.setData("qualifValue", listInfoComponent[4])
        else:
            self.update(self.database.getInfoComponent(codeProduct, codeComponent))
        self.updateQuantity(quantity)
        self.logger.debug("Created in model" + str(self))

    def updateQuantity(self, quantity):
        """ Update value for this component given quantity of food """
        self.setData("quantity", quantity * self.dictData["value"] / 100.0)

    def getValueFormated(self):
        """ Format value of this component according qualifier """
        return Component.getValueFormatedStatic(self.configApp,
                                                self.getData("qualifValue"),
                                                self.getData("quantity"))

    def getValueFormatedStatic(configApp, qualifier, quantity):
        """ Static method to convert (qualifier, quantity) into a string """
        formatFloatValue = "{0:." + configApp.get('Limits', 'nbMaxDigit') + "f}"
        resultValue = ""
        if qualifier == "N":
            resultValue = formatFloatValue.format(quantity)
        elif qualifier == "-":
            resultValue = "-"
        elif qualifier == "T":
            resultValue = _("Traces")
        elif qualifier == "<":
            resultValue = "< " + formatFloatValue.format(quantity)
        else:
            raise CalcalExceptions.CalcalInternalError(configApp,
                                                       "getValueFormated : unknown value qualifier : " +\
                                                       qualifier)
        return resultValue

    # To use method getValueFormatedStatic() without instantiating class : static method
    getValueFormatedStatic = staticmethod(getValueFormatedStatic)
