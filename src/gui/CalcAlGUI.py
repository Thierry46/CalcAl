#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-
"""
*********************************************************
Class : CalcAlGUI
Auteur : Thierry Maillard (TM)
Date : 7/5/2015 - 22/5/2015

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
        self.ressourcePath = os.path.join(dirProject, self.configApp.get('Resources', 'ResourcesDir'))
        self.imagesPath = os.path.join(self.ressourcePath,
                                       self.configApp.get('Resources', 'ImagesDir'))
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.logger.info("Démarrage de l'IHM.")

        # Set handler called when closing main window
        self.protocol("WM_DELETE_WINDOW", self.onClosing)

        # Set application title
        self.setTitle()

        # Ajout barre des menus et ajout comme observateurs de la configuration
        self.menuCalcAl = CalcAlGUIMenu.CalcAlGUIMenu(self)
        self.config(menu=self.menuCalcAl)

        # Central panels notebook
        self.note = ttk.Notebook(self)
        self.currentTab = None
        self.note.bind_all("<<NotebookTabChanged>>", self.tabChangedEvent)

        # Create panels contents
        startFrame = StartFrame.StartFrame(self.note, self, 'logoApp')
        self.note.add(startFrame, text = _("Welcome"))
        self.note.pack(side=TOP)

        # Create Status frame at the bottom of the sceen
        statusFrame = Frame(self)
        self.statusLabel = Label(statusFrame, text=_('Ready'))
        self.statusLabel.pack(side=LEFT)
        self.statusLabel.pack(side=TOP)
        statusFrame.pack(side=TOP)

    def setStatusText(self, text):
        """ Display a text in status bar """
        self.statusLabel['text'] = text

    def onClosing(self):
        """ Handler called at the end of main window """
        stopAppli = True
        # TODO
        self.destroy()

    def setTitle(self):
        """ Set title bar. """
        title = self.configApp.get('Version', 'AppName') + ' - Version ' + \
        self.configApp.get('Version', 'Number') + ' - ' + \
        self.configApp.get('Version', 'Date')
        self.title(title)

    def getConfigApp(self):
        """ Return configuration resources of the project """
        return self.configApp

    def getImagesPath(self):
        """ Return image directory path """
        return self.imagesPath

    def tabChangedEvent(self, event):
        """ Callback called when user changes tab """
        newTab = event.widget.tab(event.widget.index("current"), "text")
        if newTab != self.currentTab:
            self.currentTab = newTab
            self.logger.info(_("Tab") + " " + self.currentTab + " " + _("selected") + ".")

