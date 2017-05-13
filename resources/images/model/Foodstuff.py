# -*- coding: utf-8 -*-
"""
************************************************************************************
Class : Foodstuff
Author : Thierry Maillard (TMD)
Date : 21/11/2015 - 18/11/2016

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
from util import CalcalExceptions

class Foodstuff(ModelBaseData.ModelBaseData):
    """ Model for foodstuff
        2 way for building :
            from database if listFollowedComponents is not None
            from a list of values if listInfoProduct is not None
        """
    def __init__(self, configApp, database, name, quantity,
                 listFollowedComponents=None,
                 listInfoProduct=None):
        """ Minimal constructor """
        super(Foodstuff, self).__init__(configApp, database, _("Foodstuff"))
        self.dictComponents = dict()
        self.setData("name", name)
        self.setData("quantity", quantity)
        if listFollowedComponents is not None:
            self.update(self.database.getInfoFood(name))
            for codeComponent in listFollowedComponents:
                component = Component.Component(self.configApp, self.database, self.getData("code"),
                                                codeComponent, quantity)
                self.dictComponents[codeComponent] = component
            self.logger.debug(_("Created in model from database") + str(self))
        elif listInfoProduct is not None:
            self.setData("code", listInfoProduct[2])
            self.setData("familyName", listInfoProduct[3])
            self.setData("source", listInfoProduct[4])
            self.setData("dateSource", listInfoProduct[5])
            self.setData("urlSource", listInfoProduct[6])
            isGroup = self.getData("code") < \
                      int(self.configApp.get('Limits', 'startGroupProductCodes'))
            self.setData("isGroup", isGroup)
            self.logger.debug(_("Created in model from list") + str(self))
        else:
            raise CalcalExceptions.CalcalValueError(self.configApp,
                                                    "Bad usage for Foodstuff constructor")

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

    def updateFollowedComponents(self, componentCodes2delete, componentCodes2Add):
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


    def addComponentFromList(self, listInfoComponent):
        """ Create a new component without to access to database, from info in listInfoComponent """
        codeComponent = listInfoComponent[0]
        component = Component.Component(self.configApp, self.database, self.getData("code"),
                                        codeComponent, self.getData("quantity"),
                                        listInfoComponent)
        self.dictComponents[codeComponent] = component

    def addMissingComponents(self, listFollowedComponents):
        """ Add missing components according listFollowedComponents in this foodstuff """
        missingCompCodes = set(listFollowedComponents) - self.dictComponents.keys()
        for codeComp in missingCompCodes:
            component = Component.Component(self.configApp, self.database, self.getData("code"),
                                            codeComp, self.getData("quantity"))
            self.dictComponents[codeComp] = component
            self.logger.debug("addMissingComponents : add component " + str(codeComp) + " in " +
                              self.getData("name"))

    def getNumberOfComponents(self):
        """ Get number of defined components for this foodstuf """
        return len(self.dictComponents)
