# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : StartFrame
Author : Thierry Maillard (TMD)
Date  : 12/3/2016 - 31/3/2016

Role : Define start frame content.
************************************************************************************
"""
from tkinter import *

import os.path

from gui import FrameBaseCalcAl
from database import Database

class StartFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, dirProject, logoFrame):
        """ Initialize welcome Frame """
        super(StartFrame, self).__init__(master, mainWindow, dirProject, logoFrame)

        databaseFrame = Frame(self)
        databaseFrame.pack(side=TOP, padx=5, pady=5)

        Label(databaseFrame, text=_('Choose a database to use')).grid(row=0, column=1)
        self.databaseListbox = Listbox(databaseFrame)
        self.updateDatabaseListbox()
        self.databaseListbox.grid(row=1, column=1)
        self.databaseListbox.bind('<ButtonRelease-1>', self.clicListBoxItem)
        self.startButton = Button(databaseFrame, text=_('Start'),
                                  command=self.start, state=DISABLED)
        self.startButton.grid(row=2, column=1, sticky=EW)
        Button(databaseFrame, text=_('New'),
               command=self.newDB).grid(row=1, column=0, sticky=W)
        self.deleteButton = Button(databaseFrame, text=_('Delete'),
                                   command=self.deleteDB, state=DISABLED)
        self.deleteButton.grid(row=1, column=3, sticky=W)

    def clicListBoxItem(self, evt):
        """ Activate New and Delete button when a database is chosen """
        index = self.databaseListbox.curselection()
        if index:
            dbName = self.databaseListbox.get(index)
            self.logger.info(dbName + " " +  _('chosen'))
            self.startButton.configure(state=NORMAL)
            self.deleteButton.configure(state=NORMAL)
            self.mainWindow.closeDatabase()
            self.mainWindow.enableTabCalculator(False)

    def start(self):
        """ start calculator frame with chosen database """
        index = self.databaseListbox.curselection()
        if index:
            self.mainWindow.closeDatabase()
            dbName = self.databaseListbox.get(index)
            self.logger.info(dbName + _('chosen'))
            extDB = self.configApp.get('Resources', 'DatabaseExt')
            dbName = dbName + extDB
            databasePath = os.path.join(self.databaseDirPath, dbName)
            database = Database.Database(self.configApp, self.ressourcePath, databasePath, False, self.localDirPath)
            self.mainWindow.setDatabase(database)
            self.mainWindow.enableTabCalculator(True)
            message = _("Start calculator with database") + ' ' + dbName
            self.mainWindow.setStatusText(message)
        else:
            messagebox.showwarning(_("Database"), _("Please select a database !"))

    def newDB(self):
        """ Create a new database """
        dbName = simpledialog.askstring(_("New database"), _("Enter its name :"))
        extDB = self.configApp.get('Resources', 'DatabaseExt')
        if dbName:
            try:
                dbName = dbName.lower().strip()
                if len(dbName) == 0 or not dbName.isalnum():
                    raise ValueError(_("Invalid database name") + " : " + dbName)

                dbName = dbName + extDB
                databasePath = os.path.join(self.databaseDirPath, dbName)
                # Check if database exists
                if os.path.exists(databasePath):
                    raise ValueError(_("this database already exists") + " : " + dbName)

                self.mainWindow.closeDatabase()
                database = Database.Database(self.configApp, self.ressourcePath,
                                             databasePath, True, self.localDirPath)
                database.close()
                self.mainWindow.setStatusText(_("Database initialised") + " : " + dbName)
                self.updateDatabaseListbox()
            except ValueError as exc:
                message = _("Error") + " : " + str(exc) + " !"
                self.mainWindow.setStatusText(message, True)

    def deleteDB(self):
        """ Delete a database """
        index = self.databaseListbox.curselection()
        if index:
            dbName = self.databaseListbox.get(index)
            extDB = self.configApp.get('Resources', 'DatabaseExt')
            isOK = messagebox.askokcancel(_("Database"),
                                          _("Do you realy want to delete this database ?"))
            if isOK:
                try:
                    self.mainWindow.closeDatabase()
                    dbName = dbName + extDB
                    databasePath = os.path.join(self.databaseDirPath, dbName)
                    os.remove(databasePath)
                    self.updateDatabaseListbox()
                    self.mainWindow.setStatusText(_("Database") + " : " + dbName + " " + _("deleted"))
                    self.startButton.configure(state=DISABLED)
                except OSError as exc:
                    message = _("Error") + " : " + str(exc) + " !"
                    self.mainWindow.setStatusText(message, True)
        else:
            messagebox.showwarning(_("Database"), _("Please select a database !"))

    def updateDatabaseListbox(self):
        """ update databaseListbox with names in ressouces dir """
        extDB = self.configApp.get('Resources', 'DatabaseExt')
        listDBFiles = [filename.replace(extDB, '')
                       for filename in os.listdir(self.databaseDirPath)
                       if filename.endswith(extDB)]
        listDBFiles.sort()
        self.databaseListbox.delete(0, END)
        for dbFile in listDBFiles:
            self.databaseListbox.insert(END, dbFile)
