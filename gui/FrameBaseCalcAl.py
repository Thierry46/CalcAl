# -*- coding: utf-8 -*-
"""
************************************************************************************
Classe : FrameBaseCalcAl
Auteur : Thierry Maillard (TMD)
Date : 12/3/2016 - 4/12/2016

Rôle : Define base frame for all notebook panels.

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
import logging

import tkinter

class FrameBaseCalcAl(tkinter.Frame):
    """ Fenetre de base pour les éléments du Notebook """

    def __init__(self, master, mainWindow, imageRessourceName=None, text4Image=None):
        """
        Define a logo on top.
        master : conteneur parent
        mainWindow : root window de l'appli
        imageRessourceName : Nom de la resource qui indique l'image à afficher
        """
        super(FrameBaseCalcAl, self).__init__(master)

        self.master = master
        self.mainWindow = mainWindow
        self.dirProject = mainWindow.getDirProject()
        self.configApp = mainWindow.getConfigApp()
        self.databaseManager = mainWindow.getDataBaseManager()

        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.delaymsTooltips = int(self.configApp.get('Limits', 'delaymsTooltips'))

        # V0.44 : Don't display banner on Frames only screen is tiny (pocket PC)
        if not self.mainWindow.isTinyScreen():
            # Logo in top frame
            imageFrame = tkinter.Frame(self)
            imageFrame.pack(side=tkinter.TOP)
            self.buttonTopImage = self.mainWindow.createButtonImage(imageFrame, imageRessourceName,
                                                                text4Image)
            self.buttonTopImage.configure(command=self.mainWindow.about)
            self.buttonTopImage.pack(side=tkinter.TOP)

    def getMainWindow(self):
        """ Return mainWindow """
        return self.mainWindow

    def getDirProject(self):
        """ Return path of project installation directory """
        return self.dirProject
