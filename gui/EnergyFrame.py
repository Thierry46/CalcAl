# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : EnergyFrame
Role : Frame to display energy given by food table
Date  : 11/11/2016 - 19/12/2016
************************************************************************************
"""
import logging

import tkinter

from util import CalcalExceptions
from . import TableTreeView

class EnergyFrame(tkinter.LabelFrame):
    """ Frame to display energy given by food table """
    def __init__(self, parent, mainWindow, calculatorFrameModel, configApp):
        super(EnergyFrame, self).__init__(parent, text=_("Energy given by foods"))
        self.mainWindow = mainWindow
        self.calculatorFrameModel = calculatorFrameModel
        self.configApp = configApp
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.calculatorFrameModel.addObserver(self)

        listComp = self.configApp.get('Energy', 'EnergeticComponentsCodes')
        self.eComponentsCodes = [int(code) for code in listComp.split(";")]
        self.emptyComponents = ['-' for index in range(len(self.eComponentsCodes))]
        listEnergy = self.configApp.get('Energy', 'EnergySuppliedByComponents')
        self.eSuppliedByComponents = [float(value) for value in listEnergy.split(";")]
        assert len(self.eComponentsCodes) == len(self.eSuppliedByComponents), \
            "pb in init file : EnergeticComponentsCodes and EnergySuppliedByComponents" + \
            " must have the same number of elements"

        self.energyTable = TableTreeView.TableTreeView(self, [_("Components")],
                                 int(self.configApp.get('Size', 'energyTableNumberVisibleRows')),
                                 int(self.configApp.get('Size', 'energyTableFirstColWidth')),
                                 int(self.configApp.get('Size', 'energyTableOtherColWidth')),
                                 int(self.configApp.get('Size', 'energyTableColMinWdth')),
                                 selectmode="extended")
        self.energyTable.setColor('normalRow',
                                  self.configApp.get('Colors', 'colorComponantValueTableFood'))
        self.energyTable.pack(side=tkinter.TOP)
        self.energyTable.setBinding('<Command-c>', self.copyEnergyInClipboard)
        self.energyTable.setBinding('<Control-c>', self.copyEnergyInClipboard)

    def copyEnergyInClipboard(self, dummy=None):
        "Copy selected energy item in clipboard"
        try:
            text = self.energyTable.getTableAsText()
            self.mainWindow.copyInClipboard(text)
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
        self.mainWindow.setStatusText(message, True)

    def updateObserver(self, observable, event):
        """Called when the model object is modified. """
        if observable == self.calculatorFrameModel:
            self.logger.debug("EnergyFrame received from its model : " + event)
            try:
                if event == "INIT_DB":
                    self.init()
                elif event == "CHANGE_FOOD":
                    self.updateEnergyTable()
                elif event == "DELETE_FOOD":
                    self.updateEnergyTable()
                elif event == "ERASE_FOOD":
                    self.updateEnergyTable()
                elif event == "DISPLAY_PORTION":
                    self.updateEnergyTable()
                else:
                    self.logger.debug("EnergyFrame : ignore event : " + event)

            except CalcalExceptions.CalcalValueError as exc:
                message = _("Error") + " : " + str(exc) + " !"
                self.mainWindow.setStatusText(message, True)

    def init(self):
        """ Init energy table componants name """
        self.logger.debug("EnergyFrame : init()")

        componentsName = self.calculatorFrameModel.getEnergyComponentsNames()
        self.energyTable.updateVariablesColumns(componentsName, None)

    def updateEnergyTable(self):
        """ Update energy table according foodstuffs entered in model """
        self.logger.debug("EnergyFrame : updateEnergyTable()")

        listSupplyEnergyRatio, listValues, listSupplyEnergy = \
                                self.calculatorFrameModel.getEnergyRatio()
        self.energyTable.deleteAllRows()
        self.energyTable.insertGroupRow([(_("By ratio"), listSupplyEnergyRatio),
                                         (_("By energy") + " (kcal)", listSupplyEnergy),
                                         (_("By value"), listValues)])
