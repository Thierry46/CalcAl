# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : WaterEnergyFrame
Role : Frame to display water needed table
Date  : 12/11/2016
************************************************************************************
"""
import logging
import tkinter

from util import CalcalExceptions

class WaterEnergyFrame(tkinter.LabelFrame):
    """ Dialog box used to get information from user to save a portion """
    def __init__(self, parent, mainWindow, calculatorFrameModel, configApp):
        super(WaterEnergyFrame, self).__init__(parent, text=_("Water needed"))
        self.mainWindow = mainWindow
        self.calculatorFrameModel = calculatorFrameModel
        self.configApp = configApp
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.calculatorFrameModel.addObserver(self)

        bgNameTable = self.configApp.get('Colors', 'colorNameTableFood')
        bgValueComp = self.configApp.get('Colors', 'colorComponantValueTableFood')
        waterUnknownValue = self.configApp.get('Water', 'WaterUnknownValue')
        tkinter.Label(self, text=_("Water supplied by food") + " : ",
                      bg=bgNameTable).grid(row=0, column=0, sticky=tkinter.E)
        self.labelWaterSupplied = tkinter.Label(self, text=waterUnknownValue, bg=bgValueComp)
        self.labelWaterSupplied.grid(row=0, column=1, sticky=tkinter.E)
        tkinter.Label(self, text=_("Water needed") + " : ",
              bg=bgNameTable).grid(row=1, column=0, sticky=tkinter.E)
        self.labelWaterNeeded = tkinter.Label(self, text=waterUnknownValue, bg=bgValueComp)
        self.labelWaterNeeded.grid(row=1, column=1, sticky=tkinter.E)

    def updateObserver(self, observable, event):
        """Called when the model object is modified. """
        if observable == self.calculatorFrameModel:
            self.logger.debug("WaterEnergyFrame received from its model : " + event)
            try:
                if event == "INIT_DB":
                    self.updateWaterTable()
                elif event == "CHANGE_FOOD":
                    self.updateWaterTable()
                elif event == "DELETE_FOOD":
                    self.updateWaterTable()
                elif event == "DISPLAY_PORTION":
                    self.updateWaterTable()
                else:
                    self.logger.debug("WaterEnergyFrame : ignore event : " + event)

            except CalcalExceptions.CalcalValueError as exc:
                message = _("Error") + " : " + str(exc) + " !"
                self.mainWindow.setStatusText(message, True)

    def updateWaterTable(self):
        """ Update water frame elements according foodstuffs entered in foodTable """
        self.logger.debug("WaterEnergyFrame/updateWaterFrame()")

        # Get sum values for energetic components from model
        isDataAvailable, waterInFood, waterNeeded, isEnougthWater = \
                    self.calculatorFrameModel.getWaterEnergy()
        if isDataAvailable:
            if isEnougthWater:
                bgWaterInFood = self.configApp.get('Colors', 'colorWaterOK')
            else:
                bgWaterInFood = self.configApp.get('Colors', 'colorWaterNOK')
        else:
            bgWaterInFood = self.configApp.get('Colors', 'colorComponantValueTableFood')

        self.labelWaterSupplied.configure(text=waterInFood, bg=bgWaterInFood)
        self.labelWaterNeeded.configure(text=waterNeeded)
