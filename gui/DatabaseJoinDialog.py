# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : DatabaseJoinDialog
Role : Window used to join two Database
Date  : 26/8/2016
************************************************************************************
"""
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

from . import CallTypWindow
from . import TkSimpleDialog

import os.path

class DatabaseJoinDialog(TkSimpleDialog.TkSimpleDialog):
    """ Dialog box to choose a food name and family """
    def __init__(self, parent, configApp, databaseManager, dbNameMaster, title=None):
        self.configApp = configApp
        self.databaseManager = databaseManager
        self.dbNameMaster = dbNameMaster
        self.dbName = ""
        self.delaymsTooltips = int(self.configApp.get('Limits', 'delaymsTooltips'))
        super(DatabaseJoinDialog, self).__init__(parent, title)

    def body(self, master):
        """ Body content of this dialog """
        Label(master, text=_("Please choose secondary database") + " :").pack(side=TOP)
        listOtherDatabase = [databaseName for databaseName in self.databaseManager.getListDatabaseInDir()
                                      if databaseName != self.dbNameMaster]
        self.secondaryDatabaseCombobox = Combobox(master, exportselection=0,
                                             state="readonly", values=listOtherDatabase)
        self.secondaryDatabaseCombobox.current(0)
        self.secondaryDatabaseCombobox.pack(side=TOP)

        Label(master, text=_("Enter a result database name") + " :").pack(side=TOP)
        self.dbNameResultVar = StringVar()
        dbNameEntry = Entry(master, textvariable=self.dbNameResultVar)
        dbNameEntry.pack(side=TOP)
        dbNameEntry.focus_set()

        return dbNameEntry # initial focus

    def validate(self):
        """ Check Data entered by user
            if OK return True
        """
        isOK = False
        try:
            self.dbNameResult = self.dbNameResultVar.get().lower().strip()
            if self.dbNameResult == "":
                raise ValueError(_("Please give a name for your new database"))
            if not self.dbNameResult.isalnum():
                raise ValueError(_("Invalid database name"))
            # Check if database exists
            if self.databaseManager.existsDatabase(self.dbNameResult):
                raise ValueError(_("this database already exists") + " : " + self.dbNameResult)
            isOK = True
        except ValueError as exc:
            self.bell()
            messagebox.showwarning(_("Bad input"), message = _("Error") + " : " + str(exc) + " !")
        return isOK

    def apply(self):
        self.setResult([self.secondaryDatabaseCombobox.get(), self.dbNameResult])
