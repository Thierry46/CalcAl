# -*- coding: utf-8 -*-
"""
************************************************************************************
Classe : FrameBaseCalcAl
Auteur : Thierry Maillard (TMD)
Date : 12/3/2016 - 28/6/2016

Rôle : Define base frame for all notebook panels.
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
