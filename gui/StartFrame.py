# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : StartFrame
Author : Thierry Maillard (TMD)
Date  : 12/3/2016 - 18/12/2016

Role : Define start frame content.

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
import tkinter
from tkinter import messagebox

import os
import os.path

from . import CallTypWindow
from . import DatabaseInitialiser
from . import DatabaseJoinDialog
from . import FrameBaseCalcAl

class StartFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, logoFrame,
                 calculatorFrameModel, patientFrameModel):
        """ Initialize welcome Frame """
        super(StartFrame, self).__init__(master, mainWindow, logoFrame)
        self.calculatorFrameModel = calculatorFrameModel
        self.patientFrameModel = patientFrameModel
        ressourcePath = os.path.join(self.dirProject,
                                     self.configApp.get('Resources', 'ResourcesDir'))
        self.databaseDirPath = os.path.join(ressourcePath,
                                            self.configApp.get('Resources', 'DatabaseDir'))

        tkinter.Label(self, text=_("Based on Nutrial components database Ciqual 2017")
                      ).pack(side=tkinter.TOP)
        centerFrame = tkinter.Frame(self)
        centerFrame.pack(side=tkinter.TOP)
        buttonFrame = tkinter.Frame(centerFrame)
        buttonFrame.pack(side=tkinter.LEFT)
        databaseFrame = tkinter.LabelFrame(centerFrame, text=_('Choose a database to use'))
        databaseFrame.pack(side=tkinter.LEFT)

        # Databases list frame definition
        self.databaseListbox = tkinter.Listbox(databaseFrame, width=40, height=4)
        self.updateDatabaseListbox()
        self.databaseListbox.grid(row=0, columnspan=2)
        scrollbarRight = tkinter.Scrollbar(databaseFrame, orient=tkinter.VERTICAL,
                                   command=self.databaseListbox.yview)
        scrollbarRight.grid(row=0, column=2, sticky=tkinter.W+tkinter.N+tkinter.S)
        self.databaseListbox.config(yscrollcommand=scrollbarRight.set)
        CallTypWindow.createToolTip(self.databaseListbox,
                                    _("Select a database\nand click startbutton"),
                                    self.delaymsTooltips)
        self.databaseListbox.bind('<ButtonRelease-1>', self.clicListBoxItem)
        # V0.33 : bind return keys
        self.databaseListbox.bind('<Return>', self.start)
        self.databaseListbox.bind('<KP_Enter>', self.start)

        tkinter.Button(buttonFrame, text=_('New'), command=self.newDB).pack(side=tkinter.TOP)
        self.infoButton = tkinter.Button(buttonFrame, text=_('Info'),
                                 command=self.infoDB, state=tkinter.DISABLED)
        self.infoButton.pack(side=tkinter.TOP)
        self.deleteButton = tkinter.Button(buttonFrame, text=_('Delete'),
                                   command=self.deleteDB, state=tkinter.DISABLED)
        self.deleteButton.pack(side=tkinter.TOP)
        self.joinButton = tkinter.Button(buttonFrame, text=_('Join'), command=self.joinDB,
                                 state=tkinter.DISABLED)
        self.joinButton.pack(side=tkinter.TOP)

        self.startButton = self.mainWindow.createButtonImage(centerFrame,
                                                             imageRessourceName='btn_start',
                                                             text4Image=_("Start"))
        self.startButton.configure(command=self.start)

        self.startButton.pack(side=tkinter.LEFT)

    def clicListBoxItem(self, dummy):
        """ Activate New and Delete button when a database is chosen """
        index = self.databaseListbox.curselection()
        if index:
            dbName = self.databaseListbox.get(index)
            self.logger.info(dbName + " " +  _('chosen'))
            self.startButton.configure(state=tkinter.NORMAL)
            self.deleteButton.configure(state=tkinter.NORMAL)
            self.infoButton.configure(state=tkinter.NORMAL)
            self.joinButton.configure(state=tkinter.NORMAL)
            self.mainWindow.closeDatabase()
            self.mainWindow.enableTabCalculator(False)

    def start(self, dummy=None):
        """ start calculator frame with chosen database """
        index = self.databaseListbox.curselection()
        if index:
            self.mainWindow.closeDatabase()
            dbName = self.databaseListbox.get(index)
            self.mainWindow.closeDatabase()
            self.databaseManager.openDatabase(dbName)
            self.calculatorFrameModel.setDatabase(self.databaseManager.getDatabase())
            self.patientFrameModel.setDatabase(self.databaseManager.getDatabase())
            self.mainWindow.setTitle(dbName)
            self.mainWindow.enableTabSearch()
            self.mainWindow.enableTabPortion(True)
            self.mainWindow.enableTabPathology(True)
            self.mainWindow.enableTabPatient(True)
            self.mainWindow.enableTabCalculator(True)
            message = _("Start calculator with database") + ' ' + dbName
            self.mainWindow.setStatusText(message)
        else:
            self.mainWindow.setStatusText(_("Please select a database") + " !", True)

    def newDB(self):
        """ Create a new database """
        dialog = DatabaseInitialiser.DatabaseInitialiser(self, self.configApp,
                                                         self.databaseManager,
                                                         title=_("Initialize a  database"))
        results = dialog.getResult()
        try:
            if results is None:
                raise ValueError(_("New database canceled"))

            self.mainWindow.closeDatabase()
            dbname = results[0]
            self.databaseManager.initDBFromFile(results[0], results[1], results[2])
            self.mainWindow.setStatusText(_("Database initialised") + " : " + dbname)
            self.updateDatabaseListbox()
        except ValueError as exc:
            if results is not None:
                self.databaseManager.deleteDatabase(results[0])
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)
        except ImportError as exc:
            messagebox.showwarning(_("Can't create database"), str(exc))
            self.databaseManager.deleteDatabase(results[0])
            self.mainWindow.setStatusText(_("Can't create database") + " !", True)

    def infoDB(self):
        """ Provide information on a database
            V0.30 : 21-22/8/2016 """
        index = self.databaseListbox.curselection()
        if index:
            # Get Info on this database
            dbName = self.databaseListbox.get(index)
            self.mainWindow.closeDatabase()
            self.databaseManager.openDatabase(dbName)
            database = self.databaseManager.getDatabase()
            dictCounters = database.getInfoDatabase()

            # Format information
            title = _("Info") + " " + _("about database") + " " + dictCounters["dbName"]
            message = _("Database name") + " : " + dictCounters["dbName"] + "\n" + \
                _("Number of foodstuffs") + " : " + str(dictCounters["nbProducts"]) + "\n" + \
                _("Number of food families") + " : " + str(dictCounters["nbFamily"]) + "\n" + \
                _("Number of food groups") + " : " + str(dictCounters["nbGroup"]) + "\n" + \
                _("Number of food constituants") + " : " + str(dictCounters["nbConstituants"])

            # Display information's counters in a standard dialog
            messagebox.showinfo(title=title, message=message)
            self.mainWindow.copyInClipboard(message)

            self.mainWindow.closeDatabase()
        else:
            self.mainWindow.setStatusText(_("Please select a database") + " !", True)

    def deleteDB(self):
        """ Delete a database """
        index = self.databaseListbox.curselection()
        if index:
            dbName = self.databaseListbox.get(index)
            try:
                isOK = messagebox.askokcancel(_("Database"),
                                              _("Do you realy want to delete this database ?"))
                if isOK:
                    self.mainWindow.closeDatabase()
                    self.databaseManager.deleteDatabase(dbName)
                    self.updateDatabaseListbox()
                    self.mainWindow.setStatusText(_("Database") + " : " + dbName + " " +
                                                  _("deleted"))
                    # Python error because DISABLED icon is not define
            except OSError as exc:
                message = _("Error") + " : " + str(exc) + " !"
                self.mainWindow.setStatusText(message, True)
            except ValueError as exc:
                message = _("Error") + " : " + str(exc) + " !"
                self.mainWindow.setStatusText(message, True)
        else:
            self.mainWindow.setStatusText(_("Please select a database") + " !", True)

    def joinDB(self):
        """ Join two database
        V0.30 : 24-26/8/2016 """
        try:
            if self.databaseListbox.size() < 2:
                raise ValueError(_("At lest 2 database are needed to join them"))
            index = self.databaseListbox.curselection()
            if not index:
                raise ValueError(_("Please choose master database for joinning"))
            dbNameMaster = self.databaseListbox.get(index)
            dialog = DatabaseJoinDialog.DatabaseJoinDialog(self, self.configApp,
                                                           self.databaseManager,
                                                           dbNameMaster,
                                                           title=_("Join a database to") + " " + \
                                                                dbNameMaster)
            results = dialog.getResult()
            if results is None:
                raise ValueError(_("New database canceled"))
            self.mainWindow.closeDatabase()
            self.databaseManager.joinDatabase(dbNameMaster, results[0], results[1], results[2])
            self.updateDatabaseListbox()
            self.mainWindow.setStatusText(_("Database joined in") + " " + results[1])
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def updateDatabaseListbox(self):
        """ update databaseListbox with names in ressouces dir """
        self.databaseListbox.delete(0, tkinter.END)
        for dbFile in self.databaseManager.getListDatabaseInDir():
            self.databaseListbox.insert(tkinter.END, dbFile)
