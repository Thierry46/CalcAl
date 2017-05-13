# -*- coding: utf-8 -*-
"""
************************************************************************************
Class : CalculatorFrameModel
Author : Thierry Maillard (TMD)
Date : 12/11/2016 - 24/11/2016

Role : Define the model for calculator frame.

Ref : Design Patterns: Elements of Reusable Object-Oriented Software
Erich Gamma, Richard Helm, Ralph Johnson et John Vlissides
Préface Grady Booch
https://en.wikipedia.org/wiki/Design_Patterns

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
from model import Foodstuff
from model import TotalLine
from model import Component
from util import Observable
from util import CalcalExceptions

import logging

class CalculatorFrameModel(Observable.Observable):
    """ Model for food table, manage access to database and receive commands from GUI """
    def __init__(self, configApp):
        super(CalculatorFrameModel, self).__init__()
        self.configApp = configApp
        self.logger = logging.getLogger(configApp.get('Log', 'LoggerName'))
        self.dictAllExistingComponents = dict()
        self.dictFoodStuff = dict()
        self.totalLine = TotalLine.TotalLine(configApp)
        self.nbDays = 1
        self.listComponents = []

        # Special component to follow for Energy and Water tables
        listComp = self.configApp.get('Energy', 'EnergeticComponentsCodes')
        self.energyTotalKcalCode = int(configApp.get('Energy', 'EnergyTotalKcalCode'))
        self.energeticComponentsCodes = [int(code) for code in listComp.split(";")]
        self.energeticComponentsCodes.append(self.energyTotalKcalCode)

        self.waterCode = int(self.configApp.get('Water', 'WaterCode'))
        self.waterMlFor1kcal = float(self.configApp.get('Water', 'WaterMlFor1kcal'))
        self.waterEnergyCodes = [self.energyTotalKcalCode, self.waterCode]
        self.waterUnknownValue = self.configApp.get('Water', 'WaterUnknownValue')

        self.currentComponentCodes = set()
        self.askedByUserCodes = set()
        listEnergy = self.configApp.get('Energy', 'EnergySuppliedByComponents')
        self.EnergySuppliedByComponents = [float(value) for value in listEnergy.split(";")]
        self.EnergySuppliedByComponents.append(1.0) # Coeff for energy total

        self.specialComponentsCodes = set(self.energeticComponentsCodes) |\
                                      set(self.waterEnergyCodes)
        self.emptyEnergyComponents = ['-' for index in range(len(self.energeticComponentsCodes))]

        self.database = None
        self.listFoodModifiedInTable = []
        self.listDeletedFoodnames = []
        self.lastGroupedFamilyName = None

    def setDatabase(self, database):
        """ Change database used """
        self.database = database
        self.listComponents = database.getListComponents()
        assert (len(self.listComponents) > 0), \
                "CalculatorFrameModel/setDatabase() : no constituants in database !"

        for code, shortcut, unit in self.listComponents:
            self.dictAllExistingComponents[code] = [shortcut, unit]
        self.currentComponentCodes = self.specialComponentsCodes
        self.askedByUserCodes = set()
        # Delete all existing food
        self.dictFoodStuff.clear()
        self.setChanged()
        self.notifyObservers("INIT_DB")

    def getListComponents(self):
        """ Return list of all available components in database """
        return self.listComponents

    def addFoodInTable(self, listFoodnameQuantity, notifObs=True, addQuantity=False):
        """ Add a list of foodstuff and quantity in the dictFoodStuff of this model
            notifObs (default True) can be false to avoid too many GUI uddating
            while inserting a lot of food
            addQuantity (Default False) if a food already exists add quantities instead replacing"""

        for foodname, quantityStr in listFoodnameQuantity:
            if foodname == "":
                raise CalcalExceptions.CalcalValueError(self.configApp,
                                                        _("Food name must not be empty"))
            try:
                quantity = float(quantityStr.replace(',', '.'))
            except ValueError:
                raise CalcalExceptions.CalcalValueError(self.configApp,
                                                        _("Food quantity must be a number"))

            # Find if this foodstuff is already in listFoodStuff
            try:
                if self.dictFoodStuff[foodname].updateQuantity(quantity, addQuantity):
                    self.logger.debug("addFoodInTable : food " + foodname + "modified in model")
                    self.setChanged()
            except KeyError:
                newFood = Foodstuff.Foodstuff(self.configApp, self.database,
                                              foodname, quantity,
                                              listFollowedComponents=self.currentComponentCodes)
                self.dictFoodStuff[foodname] = newFood
                self.logger.debug("addFoodInTable : new food " + foodname + " appended in model")
                self.setChanged()

        if self.hasChanged():
            self.listFoodModifiedInTable = [foodname for foodname, quantity in listFoodnameQuantity]
        if notifObs:
            self.totalLine.update(self.dictFoodStuff)
            self.notifyObservers("CHANGE_FOOD")

    def updateFollowedComponents(self, askedByUserCodes, notifyObservers=True):
        """ Update this model according components asked by user """
        self.askedByUserCodes = askedByUserCodes
        askedByUserCodesAndOther = askedByUserCodes | self.specialComponentsCodes
        componentCodes2delete = self.currentComponentCodes - askedByUserCodesAndOther
        componentCodes2Add = askedByUserCodesAndOther - self.currentComponentCodes

        for foodStuff in self.dictFoodStuff.values():
            foodStuff.updateFollowedComponents(componentCodes2delete, componentCodes2Add)
        self.currentComponentCodes = askedByUserCodesAndOther
        self.totalLine.update(self.dictFoodStuff)

        # Notify Observers
        self.logger.debug("updateFollowedComponents : components " + str(self.currentComponentCodes))
        if notifyObservers:
            self.setChanged()
            self.notifyObservers("CHANGE_COMPONENTS")

    def getListFoodModifiedInTable(self):
        """ Return a list of last name, quantity and dict(codeComponents, qty formated) for
            last modified foods """
        # Find objet for last modified food
        returnValue = []
        self.logger.debug("getListFoodModifiedInTable() : self.listFoodModifiedInTable = " +
                          str(self.listFoodModifiedInTable))
        foodnameModif = ""
        try:
            for foodnameModif in self.listFoodModifiedInTable:
                returnValue.append(self.dictFoodStuff[foodnameModif].getFormattedValue())
        except KeyError:
            raise CalcalExceptions.CalcalInternalError("getListFoodModifiedInTable() : food " +
                                                       foodnameModif +
                                                       " not in model table")
        self.logger.debug("getListFoodModifiedInTable() : returnValue = " + str(returnValue))
        return returnValue

    def getTotalLineStr(self, nbDays=1):
        """ Return name, quantity and dict[codeComponents] = qty formated)
            for all components of total line  """
        return self.totalLine.getFormattedValue(nbDays)

    def getTotalLineValues(self):
        """ Return name, quantity and dict[codeComponents] = qty)
            for all components of total line  """
        return self.totalLine.getFormattedValue()

    def getAllExistingComponents(self):
        """ Return a dict of tupple {code:(shortcut,unit)}
            for each entry from constituantsNames table """
        return self.dictAllExistingComponents

    def getFullTable(self):
        """ Return a dict[name] = [name, qty, dictComponent] of all food and their components
            it's the job of GUI to display only asked components
            in the right order"""
        dictTable = dict()
        for foodStuff in self.dictFoodStuff.values():
            dictTable[foodStuff.getData("name")] = foodStuff.getFormattedValue()
        return dictTable

    def getTotalComponents(self, askedGroup):
        """ Return dict of tupple {code : (shortcut,unit,value, valueStr)}
            for each Energy component or empty dict if no database set
            parameter : askedGroup
                - "ENERGY" : to get total component values for Energy table
                - "WATER" : to get total component values for Water table
            """
        if askedGroup == "ENERGY":
            group = self.energeticComponentsCodes
        elif askedGroup == "WATER":
            group = self.waterEnergyCodes
        else:
            raise CalcalExceptions.CalcalInternalError("getTotalComponents() : askedGroup " +
                                                       askedGroup +
                                                       " out of {ENERGY, WATER")
        dictTotalComponents = dict()
        if len(self.dictAllExistingComponents) > 0:
            name, quantity, dictComponentsValueStr = self.totalLine.getFormattedValue()
            name, quantity, dictComponentsValue = self.totalLine.getRawValue()
            for componentCode in group:
                if componentCode in self.dictAllExistingComponents:
                    shortcut, unit = self.dictAllExistingComponents[componentCode]
                    value = dictComponentsValue[componentCode][0]
                    valueStr = dictComponentsValueStr[componentCode][1]
                    dictTotalComponents[componentCode] = [shortcut, unit, value, valueStr]
        return dictTotalComponents

    def getListDeletedFoodnames(self):
        """ Return the list of last deleted food """
        return self.listDeletedFoodnames

    def getNumberOfFoodStuff(self):
        """ Return the number of foodtuff in this model """
        return len(self.dictFoodStuff)

    def deleteFoodInModel(self, listFoodnames, inDatabase, notifObs=True):
        """ Delete listFoodnames in the model
            and if inDatabase delete also foodstuffs in database
            notifObs can be false to avoid too many GUI uddating
            while inserting a lot of food"""
        if len(listFoodnames) >= 1:
            # Delete food in database if needed
            if inDatabase:
                if len(listFoodnames) != 1:
                    raise ValueError(_("Please select one and only one line in food table"))
                self.database.deleteUserProduct(listFoodnames[0])

            # Delete foodstufs in this model
            for foodname in listFoodnames:
                self.dictFoodStuff.pop(foodname, None)

            if notifObs:
                self.totalLine.update(self.dictFoodStuff)

                # For observer information
                self.listDeletedFoodnames = listFoodnames
                self.setChanged()
                self.notifyObservers("DELETE_FOOD")

            self.listDeletedFoodnames = listFoodnames
            self.logger.debug("deleteFood : foodstufs deleted : " + str(listFoodnames))

    def groupFood(self, familyName, productName, listFoodName2Group):
        """ Group food in a new user product, give :
            familyName and productName of new product
            list (foodname and qty for new product parts """

        self.logger.debug("CalculatorFrameModel/groupFood() listFoodName2Group=" +
                          str(listFoodName2Group))

        if len(listFoodName2Group) < 2:
            raise ValueError(_("Please select more than one foodstuff in food table"))

        # Build the list of names and quantities for all food to group
        listFoodNameAndQty2Group = [[foodname, self.dictFoodStuff[foodname].getData("quantity")]
                                    for foodname in listFoodName2Group]

        # Create dictFood2group with all food to group and every components
        dictFood2Group = dict()
        for foodname, quantity in listFoodNameAndQty2Group:
            newFood = Foodstuff.Foodstuff(self.configApp, self.database,
                                          foodname, quantity,
                                          listFollowedComponents=self.dictAllExistingComponents.keys())
            dictFood2Group[foodname] = newFood

        # Create a total line to group theese foodstuffs
        totalLineGroup = TotalLine.TotalLine(self.configApp)
        totalLineGroup.update(dictFood2Group)
        totalQuantity = totalLineGroup.getData("quantity")
        totalLineGroup.normalise4for100g()

        # Insert new group in database
        self.database.insertNewComposedProduct(productName, familyName,
                                               totalQuantity,
                                               totalLineGroup.getData("dictComponentsQualifierQuantity"),
                                               listFoodNameAndQty2Group)

        # Insert new group foodstuff in this model
        self.addFoodInTable([[productName, str(totalQuantity)]])

        # delete from model old grouped products + notify observers
        self.deleteFoodInModel(listFoodName2Group, False)

        # Notify observers
        self.lastGroupedFamilyName = familyName
        self.setChanged()
        self.notifyObservers("GROUP_FOOD")

    def getGroupedFamilyFoodname(self):
        """ Return last food grouped by user """
        return self.lastGroupedFamilyName

    def ungroupFood(self, productName):
        """ Ungroup a composed product """

        # Insert group parts in model without notifying observer
        quantity = self.dictFoodStuff[productName].getData("quantity")
        listNamesQty = self.database.getPartsOfComposedProduct(productName, quantity)
        listNamesQtyStr = [[name, str(quantity)] for name, quantity in listNamesQty]
        self.addFoodInTable(listNamesQtyStr, notifObs=False, addQuantity=True)
        # Delete ungrouped product without notifying observer
        self.deleteFoodInModel([productName], False)

        # Notify observers
        self.setChanged()
        self.notifyObservers("UNGROUP_FOOD")

    def savePortion(self, listIdPortion):
        """ Save all food in model as portion in database """
        # Get names and quantities for all foodstuffs in model
        listNamesQties = [[foodname, self.dictFoodStuff[foodname].getData("quantity")]
                          for foodname in self.dictFoodStuff.keys()]

        # V0.41 : add nbDays to save this value in database
        listIdPortion.append(self.nbDays)

        # Insert portion in database
        self.database.insertPortion(listIdPortion, listNamesQties)

        # Notify observers
        self.setChanged()
        self.notifyObservers("SAVE_PORTION")

    def displayPortion(self, portionCode):
        """ Reset the model and add foodstuffs from chosen portion """
        self.logger.debug("CalculatorFrameModel/displayPortion() : start")
        self.dictFoodStuff.clear()
        self.listFoodModifiedInTable = []
        self.currentComponentCodes = self.specialComponentsCodes

        # Get all infos from database for this portion : 2 access for speed
        # v0.41 : get nbDays and update observers for this portion
        nbDays, listProductPortion = self.database.getAllInfo4Portion(portionCode,
                                                                      self.specialComponentsCodes)

        # Notify observer for updating nbDays
        self.updateNbDaysByModel(nbDays)

        # Create model elements : foodstuffs and components
        currentProductCode = 0
        for productPortion in listProductPortion:
            quantity = productPortion[0]
            foodname = productPortion[1]
            productCode = productPortion[2]
            if productCode != currentProductCode:
                self.dictFoodStuff[foodname] = Foodstuff.Foodstuff(self.configApp,
                                                                   self.database,
                                                                   foodname, quantity,
                                                                   listInfoProduct=productPortion[0:7])
                currentProductCode = productCode
                self.listFoodModifiedInTable.append(foodname)
            self.dictFoodStuff[foodname].addComponentFromList(productPortion[7:])

        # Add missing components for all foodstuffs
        for food in self.dictFoodStuff.values():
            food.addMissingComponents(self.currentComponentCodes)

        self.logger.debug("CalculatorFrameModel/displayPortion() : end model modif")

        self.totalLine.update(self.dictFoodStuff)

        # Notify observers
        self.setChanged()
        self.notifyObservers("DISPLAY_PORTION")

    def getEnergyComponentsNames(self):
        """ Return energy table componants names """
        componentsName = []
        for componentCode in self.energeticComponentsCodes:
            componentsName.append(self.dictAllExistingComponents[componentCode][0])
        return componentsName

    def getEnergyRatio(self):
        """Return values and ratio for energetics constituants """
        listSupplyEnergyRatio = []
        listValues = []
        listSupplyEnergy = []

        if self.getNumberOfFoodStuff() > 0 and len(self.dictAllExistingComponents) > 0:
            name, quantity, dictComponentsValue = self.totalLine.getRawValue()
            name, quantity, dictComponentsValueStr = self.totalLine.getFormattedValue()
            energyTotal = dictComponentsValue[self.energyTotalKcalCode][1]
            index = 0
            for componentCode in self.energeticComponentsCodes:
                # Compute ratio
                qualifier = dictComponentsValue[componentCode][0]
                value = dictComponentsValue[componentCode][1]
                energy = value * self.EnergySuppliedByComponents[index]
                supplyEnergyRatio = round(energy * 100.0 / energyTotal)
                listSupplyEnergyRatio.append(str(supplyEnergyRatio) + " %")
                listValues.append(dictComponentsValueStr[componentCode])
                formatedEnergy = Component.Component.getValueFormatedStatic(self.configApp,
                                                                            qualifier, energy)
                listSupplyEnergy.append(formatedEnergy)
                index = index + 1
        else:
            listValues = self.emptyEnergyComponents
            listSupplyEnergyRatio = self.emptyEnergyComponents
            listSupplyEnergy = self.emptyEnergyComponents

        self.logger.debug("getEnergyRatio : listSupplyEnergyRatio=" + str(listSupplyEnergyRatio) +
                          ", listValues=" + str(listValues) +
                          ", listSupplyEnergy=" + str(listSupplyEnergy))

        return listSupplyEnergyRatio, listValues, listSupplyEnergy

    def getWaterEnergy(self):
        """Return values for water needed frame """
        waterInFood = self.waterUnknownValue
        waterNeeded = self.waterUnknownValue
        isDataAvailable = False
        isEnougthWater = True
        if self.getNumberOfFoodStuff() > 0 and len(self.dictAllExistingComponents) > 0:
            name, quantity, dictComponentsValue = self.totalLine.getRawValue()
            name, quantity, dictComponentsValueStr = self.totalLine.getFormattedValue()
            waterInFood = dictComponentsValueStr[self.waterCode] + " ml"
            waterInFoodValueFloat = dictComponentsValue[self.waterCode][1]
            waterInFoodQualifier = dictComponentsValue[self.waterCode][0]
            energyTotal = dictComponentsValue[self.energyTotalKcalCode][1]
            waterNeededFloat = energyTotal * self.waterMlFor1kcal
            isEnougthWater = waterNeededFloat < waterInFoodValueFloat
            waterNeeded = Component.Component.getValueFormatedStatic(self.configApp,
                                                                     waterInFoodQualifier,
                                                                     waterNeededFloat) + " ml"
            isDataAvailable = True
        self.logger.debug("getWaterEnergy : isDataAvailable=" + str(isDataAvailable) +
                          ", waterInFood=" + waterInFood + ", waterNeeded=" + waterNeeded +
                          ", isEnougthWater=" + str(isEnougthWater))

        return isDataAvailable, waterInFood, waterNeeded, isEnougthWater

    def updateNbDays(self, nbDays):
        """ Called if user change nb days to eat food displayed in table """
        if self.nbDays != nbDays:
            self.nbDays = nbDays
            if self.getNumberOfFoodStuff() > 0:
                # Notify observers
                self.setChanged()
                self.notifyObservers("CHANGE_NB_DAYS")

    def updateNbDaysByModel(self, nbDays):
        """ Called if model change nb days to eat food displayed in table
            Typically when loading a portion """
        if self.nbDays != nbDays:
            self.nbDays = nbDays
            # Notify observers
            self.setChanged()
            self.notifyObservers("CHANGE_NB_DAYS_BY_MODEL")

    def getNbDays(self):
        """ Return nb days to eat food """
        return self.nbDays

    def selectComponentsCodes(self, listPathologiesNames):
        """ select components codes to follow """
        listComponentsCodes = self.database.getComponentsCodes4Pathologies(listPathologiesNames)
        self.updateFollowedComponents(listComponentsCodes, notifyObservers=False)
        self.setChanged()
        self.notifyObservers("CHANGE_SELECTED_COMPONENTS")

    def getAskedByUserCodes(self):
        """ Return components codes asked by user """
        return self.askedByUserCodes
