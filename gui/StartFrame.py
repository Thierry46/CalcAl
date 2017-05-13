# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : StartFrame
Author : Thierry Maillard (TMD)
Date  : 12/3/2016 - 29/8/2016

Role : Define start frame content.
************************************************************************************
"""
from tkinter import *
from tkinter import messagebox

import os
import os.path

from . import CallTypWindow
from . import DatabaseInitialiser
from . import DatabaseJoinDialog
from . import FrameBaseCalcAl
from database import Database

class StartFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, logoFrame):
        """ Initialize welcome Frame """
        super(StartFrame, self).__init__(master, mainWindow, logoFrame)

        ressourcePath = os.path.join(self.dirProject,
                                     self.configApp.get('Resources', 'ResourcesDir'))
        self.databaseDirPath = os.path.join(ressourcePath,
                                    self.configApp.get('Resources', 'DatabaseDir'))

        Label(self, text=_(self.configApp.get('Ciqual', 'CiqualNote'))).pack(side=TOP)
        centerFrame = Frame(self)
        centerFrame.pack(side=TOP)
        buttonFrame = Frame(centerFrame)
        buttonFrame.pack(side=LEFT)
        databaseFrame = LabelFrame(centerFrame, text=_('Choose a database to use'))
        databaseFrame.pack(side=LEFT)

        # Databases list frame definition
        self.databaseListbox = Listbox(databaseFrame, width=40, height=4)
        self.updateDatabaseListbox()
        self.databaseListbox.grid(row=0, columnspan=2)
        scrollbarRight = Scrollbar(databaseFrame, orient=VERTICAL,
                                   command=self.databaseListbox.yview)
        scrollbarRight.grid(row=0, column=2, sticky=W+N+S)
        self.databaseListbox.config(yscrollcommand=scrollbarRight.set)
        CallTypWindow.createToolTip(self.databaseListbox,
                                    _("Select a database\nand click startbutton"),
                                    self.delaymsTooltips)
        self.databaseListbox.bind('<ButtonRelease-1>', self.clicListBoxItem)
        # V0.33 : bind return keys
        self.databaseListbox.bind('<Return>', self.start)
        self.databaseListbox.bind('<KP_Enter>', self.start)

        Button(buttonFrame, text=_('New'), command=self.newDB).pack(side=TOP)
        self.infoButton = Button(buttonFrame, text=_('Info'),
                                 command=self.infoDB, state=DISABLED)
        self.infoButton.pack(side=TOP)
        self.deleteButton = Button(buttonFrame, text=_('Delete'),
                                   command=self.deleteDB, state=DISABLED)
        self.deleteButton.pack(side=TOP)
        self.joinButton = Button(buttonFrame, text=_('Join'), command=self.joinDB, state=DISABLED)
        self.joinButton.pack(side=TOP)

        self.startButton = self.mainWindow.createButtonImage(centerFrame,
                                                             imageRessourceName='btn_start',
                                                             text4Image=_("Start"))
        self.startButton.configure(command=self.start)

        self.startButton.pack(side=LEFT)

    def clicListBoxItem(self, evt):
        """ Activate New and Delete button when a database is chosen """
        index = self.databaseListbox.curselection()
        if index:
            dbName = self.databaseListbox.get(index)
            self.logger.info(dbName + " " +  _('chosen'))
            self.startButton.configure(state=NORMAL)
            self.deleteButton.configure(state=NORMAL)
            self.infoButton.configure(state=NORMAL)
            self.joinButton.configure(state=NORMAL)
            self.mainWindow.closeDatabase()
            self.mainWindow.enableTabCalculator(False)

    def start(self, event=None):
        """ start calculator frame with chosen database """
        index = self.databaseListbox.curselection()
        if index:
            self.mainWindow.closeDatabase()
            dbName = self.databaseListbox.get(index)
            self.mainWindow.closeDatabase()
            self.databaseManager.openDatabase(dbName)
            self.mainWindow.setTitle(dbName)
            self.mainWindow.enableTabSearch()
            self.mainWindow.enableTabPortion(True)
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
        database = None
        try:
            if results == None:
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
                    self.mainWindow.setStatusText(_("Database") + " : " + dbName + " " + _("deleted"))
                    # Python error because DISABLED icon is not define
                    #self.startButton.configure(state=DISABLED)
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
            if results == None:
                raise ValueError(_("New database canceled"))
            self.mainWindow.closeDatabase()
            self.databaseManager.joinDatabase(dbNameMaster, results[0], results[1])
            self.updateDatabaseListbox()
            self.mainWindow.setStatusText(_("Database joined in") + " " + results[1])
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def updateDatabaseListbox(self):
        """ update databaseListbox with names in ressouces dir """
        self.databaseListbox.delete(0, END)
        for dbFile in self.databaseManager.getListDatabaseInDir():
            self.databaseListbox.insert(END, dbFile)

