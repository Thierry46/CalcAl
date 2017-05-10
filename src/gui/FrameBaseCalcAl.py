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

from tkinter import *
from tkinter import ttk

class FrameBaseCalcAl(Frame):
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
        self.configApp = mainWindow.getConfigApp()
        self.mainWindow = mainWindow
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))

        # Logo in top frame
        imageFrame = Frame(self)
        imageFrame.pack(side=TOP)
        imageMessagePath = os.path.join(self.mainWindow.getImagesPath(),
                                            self.configApp.get('Resources', imageRessourceName))
        imgobj = PhotoImage(file=imageMessagePath)
        self.labelImage = ttk.Label(imageFrame, compound='top', image=imgobj, text=text4Image)
        self.labelImage.img = imgobj # store a reference to the image as an attribute of the widget
        self.labelImage.pack(side=TOP)
