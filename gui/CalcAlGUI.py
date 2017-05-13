#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-
"""
*********************************************************
Class : CalcAlGUI
Auteur : Thierry Maillard (TM)
Date : 7/5/2016 - 4/12/2016

Role : GUI for CalcAl Food Calculator project.

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
*********************************************************
"""
import logging
import os.path
import platform

import tkinter
from tkinter import ttk
from tkinter import font

from model import CalculatorFrameModel
from model import PatientFrameModel

from . import CalcAlGUIMenu
from . import StartFrame
from . import CalculatorFrame
from . import SearchFoodFrame
from . import PortionFrame
from . import PathologyFrame
from . import PatientFrame

class CalcAlGUI(tkinter.Tk):
    """ Main GUI class """

    def __init__(self, configApp, dirProject, databaseManager):
        """
        Constructor : Define all GUIs widgets
        parameters :
        - configApp : configuration properties read by ConfigParser
        - dirProject : local directory of th project to access resources
        """
        tkinter.Tk.__init__(self, None)
        self.configApp = configApp
        self.dirProject = dirProject
        self.databaseManager = databaseManager
        self.delaySeconds2ClearMessage = int(self.configApp.get('Limits',
                                                                'delaySeconds2ClearMessage')) * 1000
        self.cancelMessageId = None
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.logger.info(_("Starting GUI") + "...")

        # Adapt to screen size
        heightBigScreenInPixel = int(self.configApp.get('Limits', 'heightBigScreenInPixel'))
        heightSmallScreenInPixel = int(self.configApp.get('Limits', 'heightSmallScreenInPixel'))
        screenheight = self.winfo_screenheight()
        self.bigScreen = (screenheight > heightBigScreenInPixel)
        self.tinyScreen = (screenheight < heightSmallScreenInPixel)
        self.logger.debug("screenheight=" + str(screenheight) +
                          ", bigScreen=" + str(self.bigScreen) +
                          ", tinyScreen=" + str(self.tinyScreen))

        # Set handler called when closing main window
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        # Set application title
        self.setTitle()

        # Central panels notebook
        self.note = ttk.Notebook(self)
        self.currentTab = None
        self.note.bind_all("<<NotebookTabChanged>>", self.tabChangedEvent)

        # Create model for calculator Frame
        self.calculatorFrameModel = CalculatorFrameModel.CalculatorFrameModel(configApp)
        # Create model for calculator Frame
        self.patientFrameModel = PatientFrameModel.PatientFrameModel(configApp)

        # Create panels contents
        self.startFrame = StartFrame.StartFrame(self.note, self, 'logoStartFrame',
                                                self.calculatorFrameModel,
                                                self.patientFrameModel)
        self.note.add(self.startFrame, text=_("Welcome"))
        self.calculatorFrame = CalculatorFrame.CalculatorFrame(self.note, self, 'logoCalculator',
                                                               self.calculatorFrameModel,
                                                               self.patientFrameModel)
        self.note.add(self.calculatorFrame, text=_("Calculator"), state="disabled")

        self.searchFoodFrame = SearchFoodFrame.SearchFoodFrame(self.note, self, 'logoSearchFood',
                                                               self.calculatorFrameModel)
        self.note.add(self.searchFoodFrame, text=_("Search"), state="disabled")

        self.portionFrame = PortionFrame.PortionFrame(self.note, self, 'logoPortion',
                                                      self.calculatorFrameModel,
                                                      self.patientFrameModel)
        self.note.add(self.portionFrame, text=_("Portions"), state="disabled")

        self.pathologyFrame = PathologyFrame.PathologyFrame(self.note, self, 'logoPathology',
                                                            self.calculatorFrameModel,
                                                            self.patientFrameModel)
        self.note.add(self.pathologyFrame, text=_("Pathologies"), state="disabled")
        self.patientFrame = PatientFrame.PatientFrame(self.note, self, 'logoPatient',
                                                      self.patientFrameModel)
        self.note.add(self.patientFrame, text=_("Patients"), state="disabled")

        self.note.pack(side=tkinter.TOP)

        # Add menu bar
        self.menuCalcAl = CalcAlGUIMenu.CalcAlGUIMenu(self, self.calculatorFrameModel)
        self.config(menu=self.menuCalcAl)

        # Create Status frame at the bottom of the sceen
        statusFrame = tkinter.Frame(self)
        self.statusLabel = tkinter.Label(statusFrame, text=_('Ready'))
        self.statusLabel.pack(side=tkinter.LEFT)
        self.statusLabel.pack(side=tkinter.TOP)
        statusFrame.pack(side=tkinter.TOP)

    def getStartFrame(self):
        """Return start frame"""
        return self.startFrame

    def getCalculatorFrame(self):
        """Return calculator frame"""
        return self.calculatorFrame

    def setStatusText(self, text, isError=False):
        """ Display a text in status bar and log it
            V0.42 : normal messages are cleard after delay"""
        if self.cancelMessageId is not None:
            # Remove autoclear registred before
            self.statusLabel.after_cancel(self.cancelMessageId)
            self.cancelMessageId = None
        self.statusLabel['text'] = text
        if isError:
            self.bell()
            self.logger.error(text)
        else:
            self.logger.info(text)
            # V0.42 : clear message after delay
            self.cancelMessageId = self.statusLabel.after(self.delaySeconds2ClearMessage,
                                                          self.clearStatusText)

    def clearStatusText(self):
        """ Clear status message by writting Ready """
        self.statusLabel['text'] = _('Ready')

    def onClosing(self):
        """ Handler called at the end of main window """
        self.closeDatabase()
        self.destroy()

    def setTitle(self, dbName=None):
        """ Set title bar. """
        title = self.configApp.get('Version', 'AppName') + ' - Version ' + \
        self.configApp.get('Version', 'Number') + ' - ' + \
        self.configApp.get('Version', 'Date')
        if dbName:
            title = title + ' - ' + dbName
        self.title(title)

    def getConfigApp(self):
        """ Return configuration resources of the project """
        return self.configApp

    def getDirProject(self):
        """ Return project main installation directory """
        return self.dirProject

    def getDataBaseManager(self):
        """ Return database manager of the project """
        return self.databaseManager

    def tabChangedEvent(self, event):
        """ Callback called when user changes tab """
        newTab = event.widget.tab(event.widget.index("current"), "text")
        if newTab != self.currentTab:
            self.currentTab = newTab
            self.logger.info(_("Tab") + " " + self.currentTab + " " + _("selected") + ".")
            self.menuCalcAl.enableDatabaseMenu(event.widget.index("current") == 0)
            self.menuCalcAl.enableSelectionMenu(event.widget.index("current") == 1)

    def closeDatabase(self):
        """ Close database """
        self.databaseManager.closeDatabase()
        self.enableTabCalculator(False)
        self.enableTabSearch(False)
        self.enableTabPortion(False)
        self.enableTabPathology(False)
        self.enableTabPatient(False)
        self.setTitle(None)

    def enableTabCalculator(self, isEnable):
        """ Activate or desactivate calculator tab """
        if isEnable:
            stateTab = 'normal'
            self.menuCalcAl.enableDatabaseMenu(False)
        else:
            stateTab = 'disabled'
        self.note.tab(1, state=stateTab)
        self.menuCalcAl.enableSelectionMenu(isEnable)
        if isEnable:
            self.note.select(1)

    def enableTabSearch(self, isEnable=True):
        """ Activate or desactivate search tab """
        if isEnable:
            stateTab = 'normal'
        else:
            stateTab = 'disabled'
        self.note.tab(2, state=stateTab)
        if isEnable:
            self.searchFoodFrame.init()
            self.note.select(2)

    def enableTabPortion(self, isEnable=True):
        """ Activate or desactivate portion tab """
        if isEnable:
            stateTab = 'normal'
        else:
            stateTab = 'disabled'
        self.note.tab(3, state=stateTab)
        if isEnable:
            self.note.select(3)

    def enableTabPathology(self, isEnable=True):
        """ Activate or desactivate portion tab """
        if isEnable:
            stateTab = 'normal'
        else:
            stateTab = 'disabled'
        self.note.tab(4, state=stateTab)
        if isEnable:
            self.note.select(4)

    def enableTabPatient(self, isEnable=True):
        """ Activate or desactivate portion tab """
        if isEnable:
            stateTab = 'normal'
        else:
            stateTab = 'disabled'
        self.note.tab(5, state=stateTab)
        if isEnable:
            self.note.select(5)

    def isBigScreen(self):
        """ Return True if a big screen is detected > config('Limits', 'heightBigScreenInPixel') """
        return self.bigScreen

    def isTinyScreen(self):
        """ Return True if a tiny screen is detected
            < config('Limits', 'heightSmallScreenInPixel') """
        return self.tinyScreen

    def about(self):
        """ Display about box """
        window = tkinter.Toplevel(self.master)

        appName = self.configApp.get('Version', 'AppName')
        helv36 = font.Font(family="Helvetica", size=36, weight="bold")
        tkinter.Label(window, text=appName, font=helv36, fg="red").pack(side=tkinter.TOP)

        version = _("Version") + " : " + self.configApp.get('Version', 'Number') + ' - ' + \
        self.configApp.get('Version', 'Date')
        tkinter.Label(window, text=version).pack(side=tkinter.TOP)

        labelLogo = self.createButtonImage(window,
                                           imageRessourceName='logoAboutBox',
                                           text4Image=self.configApp.get('Version', 'Author'))
        labelLogo.pack(side=tkinter.TOP)

        emails = self.configApp.get('Version', 'EmailSupport1')  + ", " +\
                 self.configApp.get('Version', 'EmailSupport2')
        tkinter.Label(window, text=emails).pack(side=tkinter.TOP)
        tkinter.Label(window, text=_(self.configApp.get('Ciqual',
                                                        'CiqualNote'))).pack(side=tkinter.TOP)

        versionPython = "Python : " + platform.python_version() + ", Tk : " + str(tkinter.TkVersion)
        tkinter.Label(window, text=versionPython).pack(side=tkinter.TOP)
        osMachine = _("On") + " : " + platform.system() + ", " + platform.release()
        tkinter.Label(window, text=osMachine).pack(side=tkinter.TOP)

    def createButtonImage(self, parent, imageRessourceName=None, text4Image=None):
        """ Create a button or label with an image and a text dipayed """
        compoundValue = 'image'
        if text4Image:
            compoundValue = 'top'
        if imageRessourceName is not None:
            imagePath = os.path.join(self.dirProject,
                                 self.configApp.get('Resources', 'ResourcesDir'),
                                 self.configApp.get('Resources', 'ImagesDir'),
                                 self.configApp.get('Resources', imageRessourceName))
            imgobj = tkinter.PhotoImage(file=imagePath)
            buttonImage = ttk.Button(parent, image=imgobj, compound=compoundValue, text=text4Image)
            buttonImage.img = imgobj # store a reference to the image as an attribute of the widget
        else:
            buttonImage = ttk.Button(parent, text=text4Image)
        return buttonImage

    def copyInClipboard(self, text):
        """Copy text in clipboard"""
        self.clipboard_clear()
        self.clipboard_append(text)
        self.setStatusText(str(len(text)) + " " + _("characters copied and available in clipboard"))
