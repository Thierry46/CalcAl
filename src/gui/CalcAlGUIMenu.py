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

from tkinter import *

class CalcAlGUIMenu(Menu):
    """ Menu definition class """

    def __init__(self, master, dirProject):
        """ Constructor : Define menu bar GUIs widgets """
        Menu.__init__(self, master)
        self.master = master
        self.configApp = self.master.getConfigApp()
        self.logger = logging.getLogger(self.configApp.get('Log', 'LoggerName'))


        self.selectionMenu = Menu(self, tearoff=0)
        self.selectionMenu.add_command(label=_("Modify"),
                                       state=DISABLED,
                                       command=self.master.getCalculatorFrame().CopySelection)
        self.selectionMenu.add_command(label=_("Group"),
                                       state=DISABLED,
                                       command=self.master.getCalculatorFrame().groupFood)
        self.selectionMenu.add_command(label=_("Ungroup"),
                                       state=DISABLED,
                                       command=self.master.getCalculatorFrame().UngroupFood)
        self.selectionMenu.add_command(label=_("Delete"),
                                       state=DISABLED,
                                       command=self.master.getCalculatorFrame().deleteFood)
        self.add_cascade(label=_("Selection"), menu=self.selectionMenu)

        otherMenu = Menu(self, tearoff=0)
        otherMenu.add_command(label=_("About"), command=self.master.about)
        self.isLoglevelDebug = BooleanVar()
        self.isLoglevelDebug.set(False)
        # Observer self.setLogLevel on self.isLoglevelDebug called if modified : 'w'
        self.isLoglevelDebug.trace_variable('w', self.setLogLevel)
        otherMenu.add_checkbutton(label='Debug log', variable=self.isLoglevelDebug,
                                  onvalue=True, offvalue=False)
        self.add_cascade(label="?", menu=otherMenu)

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

    def enableSelectionMenu(self, isEnabled):
        """ Autorise ou non les options de configuration du menu Fichier """
        if isEnabled:
            etat = NORMAL
        else:
            etat = DISABLED
        for itemMenu in range(4):
            self.selectionMenu.entryconfigure(itemMenu, state=etat)


