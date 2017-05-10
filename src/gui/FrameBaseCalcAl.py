# -*- coding: utf-8 -*-
"""
************************************************************************************
Classe : FrameBaseCalcAl
Auteur : Thierry Maillard (TMD)
Date : 27/11/2015

Rôle : Define base frame for all notebook panels.
************************************************************************************
"""
import logging
import os.path
import locale
import os.path

from tkinter import *
from tkinter import ttk

class FrameBaseCalcAl(Frame):
    """ Fenetre de base pour les éléments du Notebook """

    def __init__(self, master, mainWindow, dirProject, imageRessourceName=None, text4Image=None):
        """
        Define a logo on top.
        master : conteneur parent
        mainWindow : root window de l'appli
        dirProject : Base apllication path
        imageRessourceName : Nom de la resource qui indique l'image à afficher
        """
        super(FrameBaseCalcAl, self).__init__(master)

        self.master = master
        self.configApp = mainWindow.getConfigApp()
        self.mainWindow = mainWindow

        self.ressourcePath = os.path.join(dirProject,
                                          self.configApp.get('Resources', 'ResourcesDir'))
        self.imagesPath = os.path.join(self.ressourcePath,
                                    self.configApp.get('Resources', 'ImagesDir'))
        self.databaseDirPath = os.path.join(self.ressourcePath,
                                            self.configApp.get('Resources', 'DatabaseDir'))
        localDirPath = os.path.join(dirProject,
                                         self.configApp.get('Resources', 'LocaleDir'))
        localeLang = locale.getlocale()[0][:2]
        self.localDirPath = os.path.join(localDirPath, localeLang)

        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))

        # Logo in top frame
        imageFrame = Frame(self)
        imageFrame.pack(side=TOP)
        imageMessagePath = os.path.join(self.imagesPath,
                                        self.configApp.get('Resources', imageRessourceName))
        imgobj = PhotoImage(file=imageMessagePath)
        self.labelImage = ttk.Label(imageFrame, compound='top', image=imgobj, text=text4Image)
        self.labelImage.img = imgobj # store a reference to the image as an attribute of the widget
        self.labelImage.pack(side=TOP)
