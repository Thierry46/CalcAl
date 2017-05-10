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
import platform

from tkinter import *
from tkinter import ttk
from tkinter import font

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
        self.imagesDirPath = os.path.join(self.ressourcePath,
                                    self.configApp.get('Resources', 'ImagesDir'))
        self.databaseDirPath = os.path.join(self.ressourcePath,
                                            self.configApp.get('Resources', 'DatabaseDir'))
        localDirPath = os.path.join(dirProject,
                                         self.configApp.get('Resources', 'LocaleDir'))
        localeLang = locale.getlocale()[0][:2]
        self.localDirPath = os.path.join(localDirPath, localeLang)

        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.delaymsTooltips = int(self.configApp.get('Limits', 'delaymsTooltips'))


        # Logo in top frame
        imageFrame = Frame(self)
        imageFrame.pack(side=TOP)
        self.buttonTopImage = self.createButtonImage(imageFrame, imageRessourceName, text4Image)
        self.buttonTopImage.configure(command=self.about)
        self.buttonTopImage.pack(side=TOP)

    def createButtonImage(self, parent, imageRessourceName=None, text4Image=None):
        """ Create a button or label with an image and a text dipayed """
        imageMessagePath = os.path.join(self.imagesDirPath,
                                            self.configApp.get('Resources', imageRessourceName))
        imgobj = PhotoImage(file=imageMessagePath)
        buttonImage = ttk.Button(parent, compound='top', image=imgobj, text=text4Image)
        buttonImage.img = imgobj # store a reference to the image as an attribute of the widget
        return buttonImage

    def about(self):
        window = Toplevel(self.master)

        appName = self.configApp.get('Version', 'AppName')
        helv36 = font.Font(family="Helvetica", size=36, weight="bold")
        Label(window, text=appName, font=helv36, fg="red").pack(side=TOP)

        version = "Version : " + self.configApp.get('Version', 'Number') + ' - ' + \
            self.configApp.get('Version', 'Date')
        Label(window, text=version).pack(side=TOP)

        labelLogo = self.createButtonImage(window,
                                      imageRessourceName='logoAboutBox',
                                      text4Image=self.configApp.get('Version', 'Author'))
        labelLogo.pack(side=TOP)

        versionPython = "Python : " + platform.python_version() + \
            ", Tk : " + str(TkVersion)
        Label(window, text=versionPython).pack(side=TOP)
        osMachine = _("On") + " : " + platform.system() + ", " + platform.release()
        Label(window, text=osMachine).pack(side=TOP)

