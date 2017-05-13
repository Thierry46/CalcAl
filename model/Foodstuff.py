# -*- coding: utf-8 -*-
"""
************************************************************************************
Class : Foodstuff
Author : Thierry Maillard (TMD)
Date : 21/11/2015 -2/11/2016

Role : Define a foodstuff.

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
from model import Component

class Foodstuff(ModelBaseData.ModelBaseData):
    """ Model for foodstuff """
    def __init__(self, configApp, database, foodname, quantity, listFollowedComponents):
        super(Foodstuff, self).__init__(configApp, database, _("Foodstuff"))
        self.dictComponents = dict()
        self.update(self.database.getInfoFood(foodname))
        self.setData("quantity", quantity)
        for codeComponent in listFollowedComponents:
            component = Component.Component(configApp, database, self.getData("code"),
                                            codeComponent, quantity)
            self.dictComponents[codeComponent] = component
        self.logger.debug(_("Created in model") + str(self))

    def updateQuantity(self, quantity, addQuantity=False):
        """ Update quantity of this foodstuff :
            addQuantity (Default False) if a food already exists add quantities instead replacing"""
        updated = False
        if addQuantity:
            quantity += self.getData("quantity")
        if abs(self.getData("quantity") - quantity) > float(self.configApp.get("Limits", "near0")):
            updated = True
            self.setData("quantity", quantity)
            for component in self.dictComponents.values():
                component.updateQuantity(quantity)
            self.logger.debug("Quantity updated" + str(self))
        return updated

    def updateFollowedComponents(self,componentCodes2delete, componentCodes2Add):
        """ Update this model according components asked by user """

        # Delete components removed by user
        for k in componentCodes2delete:
            self.dictComponents.pop(k, None)

        # Add new components asked by user
        for codeComponent in componentCodes2Add:
            self.dictComponents[codeComponent] = Component.Component(self.configApp, self.database,
                                                                     self.getData("code"),
                                                                     codeComponent,
                                                                     self.getData("quantity"))
        self.logger.debug("Add components : " + str(list(componentCodes2Add)))

    def getFormattedValue(self):
        """ Return food name, quantity and dict(codeComponents, qty formated) for all components """
        name = self.getData("name")
        quantity = self.getData("quantity")
        dictComponentValueFormated = {}
        for codeComponent, component in self.dictComponents.items():
            dictComponentValueFormated[codeComponent] = component.getValueFormated()
        return name, quantity, dictComponentValueFormated



