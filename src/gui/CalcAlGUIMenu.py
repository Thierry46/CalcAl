# -*- coding: utf-8 -*-
"""
************************************************************************************
programme : CalcAlGUI
Auteur : Thierry Maillard (TMD)
Date : 12/3/2016

Role : Menu bar for CalcAl Food Calculator project.

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
import os.path
import platform

from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import font

class CalcAlGUIMenu(Menu):
    """ Menu definition class """

    def __init__(self, master):
        """ Constructor : Define menu bar GUIs widgets """
        Menu.__init__(self, master)
        self.master = master
        self.configApp = self.master.getConfigApp()
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))
        self.imagesPath = self.master.getImagesPath()

        self.MenuesMenu = Menu(self, tearoff=0)
        self.MenuesMenu.add_command(label=_("New..."),
                                      state=DISABLED, command=self.createMenu)
        self.MenuesMenu.add_command(label=_("Load..."),
                                      state=DISABLED, command=self.loadMenu)
        self.MenuesMenu.add_command(label=_("Save..."),
                                      state=DISABLED, command=self.saveMenu)
        self.add_cascade(label=_("Menu"), menu=self.MenuesMenu)

        otherMenu = Menu(self, tearoff=0)
        otherMenu.add_command(label=_("About"), command=self.aPropos)
        otherMenu.add_command(label="Aide...", command=self.afficheAide)
        self.isLoglevelDebug = BooleanVar()
        self.isLoglevelDebug.set(False)
        # Observer self.setLogLevel on self.isLoglevelDebug called if modified : 'w'
        self.isLoglevelDebug.trace_variable('w', self.setLogLevel)
        otherMenu.add_checkbutton(label='Debug log', variable=self.isLoglevelDebug,
                                  onvalue=True, offvalue=False)
        self.add_cascade(label="?", menu=otherMenu)

    def aPropos(self):
        window = Toplevel(self.master)
        appName = self.configApp.get('Version', 'AppName')
        helv36 = font.Font(family="Helvetica", size=36, weight="bold")
        Label(window, text=appName, font=helv36, fg="red").pack(side=TOP)
        version = "Version : " + self.configApp.get('Version', 'Number') + ' - ' + \
                  self.configApp.get('Version', 'Date')
        Label(window, text=version).pack(side=TOP)

        logoPath = os.path.join(self.imagesPath, self.configApp.get('Resources', 'logoApp'))
        imgobj = PhotoImage(file=logoPath)
        logoTxt = self.configApp.get('Version', 'Author')
        labelLogo = ttk.Label(window, compound='top', image=imgobj, text=logoTxt)
        labelLogo.img = imgobj # store a reference to the image as an attribute of the widget
        labelLogo.pack(side=TOP)

        versionPython = "Python : " + platform.python_version() + \
                        ", Tk : " + str(TkVersion)
        Label(window, text=versionPython).pack(side=TOP)
        osMachine = _("On") + " : " + platform.system() + ", " + platform.release()
        Label(window, text=osMachine).pack(side=TOP)

    def afficheAide(self):
        messagebox.showinfo(self.configApp.get('Version', 'AppName') + " - " + _("description"),
                        _("This software helps to evaluate food suplies.") + "\n" +
                        _("Please consult its documentation for more information."))

    def setLogLevel(self, *args):
        """ Set logging level """

        # Get handler to write on console
        streamHandler = self.logger.handlers[1]

        if self.isLoglevelDebug.get():
            self.logger.setLevel(logging.DEBUG)
            streamHandler.setLevel(logging.DEBUG)
            self.logger.info(_("Debug logging mode : all messages in file and on console."))
        else:
            self.logger.setLevel(logging.INFO)
            streamHandler.setLevel(logging.WARNING)
            self.logger.info(_("Logging in file with mode INFO and on console in mode WARNING."))

    def createMenu(self):
        """ Create a new Menu """
        menuName = simpledialog.askstring(_("New menu"), _("Enter its name :"))
        # TODO
        if menuName:
            message = _("New menu") + " : " + menuName
            self.master.setStatusText(message)
            self.logger.info(message)

    def loadMenu(self):
        """ Load an existing menu """
        # TODO
        menuName = "TODO"
        self.master.setStatusText(_("Menu") + " " + menuName + " " + _("loaded") + ".")

    def saveMenu(self):
        """ Save a menu """
        # TODO
        menuName = "TODO"
        self.master.setStatusText(_("Menu") + " " + menuName + " " + _("saved") + ".")

    def enableMenuMenues(self, isEnabled):
        """ Autorise ou non les options de configuration du menu Fichier """
        if isEnabled:
            etat = NORMAL
        else:
            etat = DISABLED
        for itemMenu in range(4):
            self.MenuesMenu.entryconfigure(itemMenu, state=etat)
