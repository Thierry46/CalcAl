# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : StartFrame
Author : Thierry Maillard (TMD)
Date  : 12/3/2016 - 18/6/2016

Role : Define start frame content.
************************************************************************************
"""
from tkinter import *

import os.path

from gui import CallTypWindow

from gui import FrameBaseCalcAl
from database import Database
from tkinter import simpledialog
from tkinter import messagebox

class StartFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, dirProject, logoFrame):
        """ Initialize welcome Frame """
        super(StartFrame, self).__init__(master, mainWindow, dirProject, logoFrame)

        Label(self, text=_(self.configApp.get('Version', 'CiqualNote'))).pack(side=TOP)
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

        Button(buttonFrame, text=_('New'), command=self.newDB).pack(side=TOP)
        self.deleteButton = Button(buttonFrame, text=_('Delete'),
                                   command=self.deleteDB, state=DISABLED)
        self.deleteButton.pack(side=TOP)

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
            self.mainWindow.closeDatabase()
            self.mainWindow.enableTabCalculator(False)

    def start(self):
        """ start calculator frame with chosen database """
        index = self.databaseListbox.curselection()
        if index:
            self.mainWindow.closeDatabase()
            dbName = self.databaseListbox.get(index)
            self.logger.info(dbName + " " + _('chosen'))
            extDB = self.configApp.get('Resources', 'DatabaseExt')
            dbName = dbName + extDB
            databasePath = os.path.join(self.databaseDirPath, dbName)
            database = Database.Database(self.configApp, self.ressourcePath, databasePath, False,
                                         self.localDirPath)
            self.mainWindow.setDatabase(database)
            self.mainWindow.enableTabCalculator(True)
            message = _("Start calculator with database") + ' ' + dbName
            self.mainWindow.setStatusText(message)
        else:
            self.mainWindow.setStatusText(_("Please select a database") + " !", True)

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
                self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

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
                    # Python error because DISABLED icon is not define
                    #self.startButton.configure(state=DISABLED)
                except OSError as exc:
                    message = _("Error") + " : " + str(exc) + " !"
                    self.mainWindow.setStatusText(message, True)
        else:
            self.mainWindow.setStatusText(_("Please select a database") + " !", True)
        print("sortie de deleteDB")

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
