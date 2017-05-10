#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-
"""
*********************************************************
Class : CalcAlGUI
Auteur : Thierry Maillard (TM)
Date : 7/5/2016 - 8/6/2016

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

from tkinter import *
from tkinter import ttk

from gui import CalcAlGUIMenu
from gui import StartFrame
from gui import CalculatorFrame
from gui import SearchFoodFrame

class CalcAlGUI(Tk):
    """ Main GUI class """

    def __init__(self, configApp, dirProject):
        """
        Constructor : Define all GUIs widgets
        parameters :
        - configApp : configuration properties read by ConfigParser
        - dirProject : local directory of th project to access resources
        """
        Tk.__init__(self, None)
        self.configApp = configApp

        ressourcePath = os.path.join(dirProject, self.configApp.get('Resources', 'ResourcesDir'))
        self.imagesPath = os.path.join(ressourcePath,
                                       self.configApp.get('Resources', 'ImagesDir'))
        self.databaseDirPath = os.path.join(ressourcePath,
                          self.configApp.get('Resources', 'DatabaseDir'))
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.database = None
        self.logger.info("Démarrage de l'IHM.")

        # Adapt to screen size
        heightBigScreenInPixel = int(self.configApp.get('Limits', 'heightBigScreenInPixel'))
        screenheight = self.winfo_screenheight()
        self.bigScreen = (screenheight > heightBigScreenInPixel)
        self.logger.debug("heightBigScreenInPixel=" + str(heightBigScreenInPixel) +
                         ", screenheight=" + str(screenheight) +
                         ", bigScreen=" + str(self.bigScreen))

        # Set handler called when closing main window
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        # Set application title
        self.setTitle()

        # Central panels notebook
        self.note = ttk.Notebook(self)
        self.currentTab = None
        self.note.bind_all("<<NotebookTabChanged>>", self.tabChangedEvent)

        # Create panels contents
        startFrame = StartFrame.StartFrame(self.note, self,
                                           dirProject, 'logoStartFrame')
        self.note.add(startFrame, text = _("Welcome"))
        self.calculatorFrame = CalculatorFrame.CalculatorFrame(self.note, self,
                                                          dirProject, 'logoCalculator')
        self.note.add(self.calculatorFrame, text = _("Calculator"), state="disabled")

        self.searchFoodFrame = SearchFoodFrame.SearchFoodFrame(self.note, self,
                                                       dirProject, 'logoSearchFood')
        self.note.add(self.searchFoodFrame, text = _("Search"), state="disabled")
        self.note.pack(side=TOP)

        # Add menu bar
        self.menuCalcAl = CalcAlGUIMenu.CalcAlGUIMenu(self, dirProject)
        self.config(menu=self.menuCalcAl)

        # Create Status frame at the bottom of the sceen
        statusFrame = Frame(self)
        self.statusLabel = Label(statusFrame, text=_('Ready'))
        self.statusLabel.pack(side=LEFT)
        self.statusLabel.pack(side=TOP)
        statusFrame.pack(side=TOP)

    def getCalculatorFrame(self):
        """Return calculator frame"""
        return self.calculatorFrame

    def setStatusText(self, text, isError=False):
        """ Display a text in status bar and log it """
        self.statusLabel['text'] = text
        if (isError):
            self.bell()
            self.logger.error(text)
        else:
            self.logger.info(text)

    def onClosing(self):
        """ Handler called at the end of main window """
        stopAppli = True
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

    def tabChangedEvent(self, event):
        """ Callback called when user changes tab """
        newTab = event.widget.tab(event.widget.index("current"), "text")
        if newTab != self.currentTab:
            self.currentTab = newTab
            self.logger.info(_("Tab") + " " + self.currentTab + " " + _("selected") + ".")
            self.menuCalcAl.enableSelectionMenu(event.widget.index("current") == 1)

    def setDatabase(self, database):
        """ Set database """
        dbname = None
        if database :
            dbname = database.getDbname()
        self.database = database
        self.setTitle(dbname)

    def getDatabase(self):
        """ get database """
        return self.database

    def closeDatabase(self):
        """ Close database """
        database = self.getDatabase()
        if database:
            database.close()
            self.enableTabCalculator(False)
            self.enableTabSearch(False)
            self.database = None
            self.setTitle(None)

    def enableTabCalculator(self, isEnable):
        """ Activate or desactivate calculator tab """
        if isEnable:
            stateTab = 'normal'
        else:
            stateTab='disabled'
        self.note.tab(1, state=stateTab)
        self.menuCalcAl.enableSelectionMenu(isEnable)
        if isEnable:
            self.calculatorFrame.init()
            self.note.select(1)

    def enableTabSearch(self, isEnable):
        """ Activate or desactivate calculator tab """
        if isEnable:
            stateTab = 'normal'
        else:
            stateTab='disabled'
        self.note.tab(2, state=stateTab)
        if isEnable:
            self.searchFoodFrame.init()
            self.note.select(2)

    def isBigScreen(self):
        return self.bigScreen
