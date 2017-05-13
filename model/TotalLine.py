# -*- coding: utf-8 -*-
"""
************************************************************************************
Class : TotalLine
Author : Thierry Maillard (TMD)
Date : 28/10/2016 - 18/11/2016

Role : Define a TotalLine for food table.

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

Modif. :
- dictComponentsValueStr is calculated when calling getFormattedValue()
- getFormattedValue accepts 1 parameter : nbDays
************************************************************************************
"""
from model import ModelBaseData
from model import Component
from util import CalcalExceptions

class TotalLine(ModelBaseData.ModelBaseData):
    """ Model for a TotalLine """
    def __init__(self, configApp):
        super(TotalLine, self).__init__(configApp, None, "TotalLine")
        self.setData("containValues", False)
        self.setData("name", _("Total"))
        self.setData("quantity", 0.0)
        self.setData("dictComponentsQualifierQuantity", dict())

        # table for qualification reduction rules
        self.qRulesS = self.configApp.get('QualifValue', 'QRulesS').split(";")
        self.qRules0 = self.configApp.get('QualifValue', 'QRules0').split(";")
        self.qRulesO = self.configApp.get('QualifValue', 'QRulesO').split(";")

        self.logger.debug("Created in model" + str(self))

    def update(self, dictFoodStuff):
        """ Update total line value according value in parent """

        # Get values of all foodstuff in model
        nbFoodStuff = len(dictFoodStuff)
        if nbFoodStuff > 0:
            # Sum quantities of each food
            self.setData("quantity", 0.0)
            for foodStuff in dictFoodStuff.values():
                self.setData("quantity", self.getData("quantity") + foodStuff.getData("quantity"))

            # Sum all components values and qualifiers
            dictQualifierQuantity = dict()
            for foodStuff in dictFoodStuff.values():
                for codeComponent, component in foodStuff.dictComponents.items():
                    qualifValue = component.getData("qualifValue")
                    quantity = component.getData("quantity")
                    if codeComponent in dictQualifierQuantity.keys():
                        dictQualifierQuantity[codeComponent][0] += qualifValue
                        dictQualifierQuantity[codeComponent][1] += quantity
                    else:
                        dictQualifierQuantity[codeComponent] = [qualifValue, quantity]

            # Reduce qualifiers and format all components
            self.getData("dictComponentsQualifierQuantity").clear()
            for codeComponent, qualifierQuantity in dictQualifierQuantity.items():
                qualifierQuantity[0] = self.reducQualifier(qualifierQuantity[0],
                                                           qualifierQuantity[1])
                self.getData("dictComponentsQualifierQuantity")[codeComponent] = \
                                                        [qualifierQuantity[0],
                                                         qualifierQuantity[1]]

    def reducQualifier(self, qualif2Reduce, value):
        """ Reduce qualif2Reduce expression by applying rules read in config file """
        qualifResult = "".join(set(qualif2Reduce))
        nbReduction = 0
        while nbReduction < 5 and len(qualifResult) > 1:
            # Apply rules
            if value >= float(self.configApp.get("Limits", "near0")):
                qRule2apply = self.qRulesS
            else: # For value near 0
                qRule2apply = self.qRules0
            qRule2apply = qRule2apply + self.qRulesO
            for rule in qRule2apply:
                if rule[0] in qualifResult and rule[1] in qualifResult:
                    qualifResult = qualifResult.replace(rule[0], rule[2])
                    qualifResult = qualifResult.replace(rule[1], rule[2])
                qualifResult = "".join(set(qualifResult))
            nbReduction = nbReduction + 1
        if nbReduction >= 5:
            raise CalcalExceptions.CalcalInternalError(self.configApp,
                                                       "reducQualifier don't converge : " +
                                                       qualif2Reduce +
                                                       " can't be reduce : " + qualifResult +
                                                       ". Check config/[QualifValue]/QRules")
        return qualifResult


    def getFormattedValue(self, nbDays=1):
        """ Return name, quantity and dict(codeComponents) = qty formated
            for all components of this total line
            V0.38 : build dictComponentsValueStr
            getFormattedValue accept 1 optional parameter : Nb days
            Parameter nbDays : all returned values are divided by this integer """
        assert nbDays > 0, "TotalLine/getFormattedValue() : nbDays must be > 0 " + str(nbDays)
        dictComponentsValueStr = dict()
        for codeComponent, qualifierQuantity \
            in self.getData("dictComponentsQualifierQuantity").items():
            dictComponentsValueStr[codeComponent] = \
                    Component.Component.getValueFormatedStatic(self.configApp,
                                                               qualifierQuantity[0],
                                                               qualifierQuantity[1] / float(nbDays))
        totalName = self.getData("name")
        totalQuantity = self.getData("quantity")
        if nbDays > 1:
            totalName += " " + _("per day")
            totalQuantity /= float(nbDays)
        return totalName, round(totalQuantity, 1), dictComponentsValueStr

    def getRawValue(self):
        """ Return name, quantity and dict(codeComponents) =  [Qualifier, quantity]
            for all components of this total line  """
        return self.getData("name"), self.getData("quantity"), \
                    self.getData("dictComponentsQualifierQuantity")

    def normalise4for100g(self):
        """ Normalise all components quantities for 100g of products """
        ratio = 100. / self.getData("quantity")
        for fieldsComponent in self.getData("dictComponentsQualifierQuantity").values():
            fieldsComponent[1] *= ratio
        self.setData("quantity", 100.)
