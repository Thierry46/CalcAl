# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : DatabaseInitialiser
Role : Window used to initialize Database
Date  : 30/5/2016 - 18/02/2018

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
import webbrowser
import locale
import os.path
import pathlib

import tkinter
from tkinter import messagebox
from tkinter import filedialog

from . import TkSimpleDialog

class DatabaseInitialiser(TkSimpleDialog.TkSimpleDialog):
    """ Dialog box to import a new database """
    def __init__(self, parent, configApp, databaseManager, title=None):
        self.configApp = configApp
        self.databaseManager = databaseManager
        self.dbName = ""
        self.delaymsTooltips = int(self.configApp.get('Limits', 'delaymsTooltips'))
        super(DatabaseInitialiser, self).__init__(parent, title)

    def body(self, master):
        """ Body content of this dialog """
        allDatabase = ["Ciqual_2017", "USDA_28"]

        tkinter.Button(master, text=_("Get help for this operation"),
               command=self.getHelpOnImport).grid(row=0, column=1, sticky=tkinter.W)
        tkinter.Label(master, text=_("Enter a new database name") + " :").grid(row=1, column=0,
                                                                               sticky=tkinter.W)
        self.dbNameVar = tkinter.StringVar()
        dbNameEntry = tkinter.Entry(master, textvariable=self.dbNameVar)
        dbNameEntry.grid(row=1, column=1, sticky=tkinter.W)
        dbNameEntry.focus_set()

        tkinter.Label(master, text=_("Database type") + " :").grid(row=2, column=0,
                                                                   sticky=tkinter.W)
        databaseTypeFrame = tkinter.Frame(master)
        databaseTypeFrame.grid(row=2, column=1, sticky=tkinter.EW)

        self.databaseType = tkinter.StringVar()
        self.databaseType.set(allDatabase[0]) # initialize
        for typeDB in allDatabase:
            tkinter.Radiobutton(databaseTypeFrame, text=typeDB,
                                variable=self.databaseType, value=typeDB).pack(side=tkinter.LEFT)

        tkinter.Label(master,
                      text=_("Download init file") +
                      " :").grid(row=3, column=0, sticky=tkinter.W)
        tkinter.Button(master, text=_("Download file"),
                       command=self.openWEBBrowser).grid(row=3, column=1, sticky=tkinter.W)

        btnFileChooser = tkinter.Button(master, text=_("Database init file") + "...",
                                        command=self.chooseInitFile)
        btnFileChooser.grid(row=4, column=0, sticky=tkinter.W)
        self.initFilnameVar = tkinter.StringVar()
        initFileEntry = tkinter.Entry(master, textvariable=self.initFilnameVar, width=60)
        initFileEntry.grid(row=4, column=1, sticky=tkinter.W)

        return dbNameEntry # initial focus

    def chooseInitFile(self):
        """ Choose ans initialisation file """
        filename = None
        dbType = self.databaseType.get()
        if dbType == "Ciqual_2017":
            filename = filedialog.askopenfilename(filetypes=(("Excel 97 File", "*.xls"),
                                                             ("All Files", "*.*")),
                                                  title=_("Choose a file"))

        if dbType == "USDA_28":
            filename = filedialog.askopenfilename(filetypes=(("Zip File", "*.zip"),
                                                             ("All Files", "*.*")),
                                                  title=_("Choose a file"))


        if filename:
            self.initFilnameVar.set(filename)

    def openWEBBrowser(self):
        """ Open user favorite WEB browser with a new tab displaying
            official database init file provider WEB site
            V0.52 : Possibility to cancel web browser launching """
        link = "?"
        dbType = self.databaseType.get()
        if dbType == "Ciqual_2017":
            link = self.configApp.get('Ciqual', 'CiqualUrl')
            fileInfo = self.configApp.get('Ciqual', 'fileInfo')
        if dbType == "USDA_28":
            link = self.configApp.get('USDA', 'USDAUrl')
            fileInfo = self.configApp.get('USDA', 'fileInfo')
        self.parent.getMainWindow().copyInClipboard(link)
        title = _("Download a source file") + " " + dbType
        message = _("Your web browser is going to be\nopen on official data providers WEB site")
        message += " :\n" + link
        message += "\n\n" + _("Please download the following file")
        message += " :\n" + fileInfo
        if messagebox.askokcancel(title=title, message=message):
            webbrowser.open_new_tab(link)

    def getHelpOnImport(self):
        """ Display help for this database initialisation """
        curLocale = locale.getlocale()[0][:2]
        htmlImportPath = os.path.join(self.master.getDirProject(),
                                      self.configApp.get('Resources', 'DocumentationDir'),
                                      curLocale,
                                      self.configApp.get('Resources', 'DocumentationImportFile'))
        htmlImportAbsPath = os.path.abspath(htmlImportPath)
        urlHtmlImportPath = pathlib.Path(htmlImportAbsPath).as_uri() + "#" + \
                            self.configApp.get('Resources', 'DocumentationImportSection')
        self.parent.logger.info(_("Start web browser with") + " " + urlHtmlImportPath)
        webbrowser.open_new_tab(urlHtmlImportPath)

    def validate(self):
        """ Check Data entered by user
            if OK return True
        """
        isOK = False
        try:
            self.dbName = self.dbNameVar.get().lower().strip()
            if self.dbName == "":
                raise ValueError(_("Please give a name for your new database"))
            if not self.dbName.isalnum():
                raise ValueError(_("Invalid database name"))
            # Check if database exists
            if self.databaseManager.existsDatabase(self.dbName):
                raise ValueError(_("this database already exists") + " : " + self.dbName)

            if self.initFilnameVar.get() == "":
                raise ValueError(_("Please give a filename containing data to import"))
            isOK = True
        except ValueError as exc:
            self.bell()
            messagebox.showwarning(_("Bad input"), message=_("Error") + " : " + str(exc) + " !")
        return isOK

    def apply(self):
        self.setResult([self.dbName, self.databaseType.get(), self.initFilnameVar.get()])
