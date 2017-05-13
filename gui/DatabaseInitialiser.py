# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : DatabaseInitialiser
Role : Window used to initialize Database
Date  : 30/5/2016 - 19/12/2016
************************************************************************************
"""
import tkinter
from tkinter import messagebox
from tkinter import filedialog

from . import TkSimpleDialog

class DatabaseInitialiser(TkSimpleDialog.TkSimpleDialog):
    """ Dialog box to choose a food name and family """
    def __init__(self, parent, configApp, databaseManager, title=None):
        self.configApp = configApp
        self.databaseManager = databaseManager
        self.dbName = ""
        self.delaymsTooltips = int(self.configApp.get('Limits', 'delaymsTooltips'))
        super(DatabaseInitialiser, self).__init__(parent, title)

    def body(self, master):
        """ Body content of this dialog """
        allDatabase = ["Ciqual_2013", "Ciqual_2016", "USDA_28"]

        tkinter.Label(master, text=_("Enter a new database name") + " :").grid(row=0, column=0,
                                                                               sticky=tkinter.W)
        self.dbNameVar = tkinter.StringVar()
        dbNameEntry = tkinter.Entry(master, textvariable=self.dbNameVar)
        dbNameEntry.grid(row=0, column=1, sticky=tkinter.W)
        dbNameEntry.focus_set()

        tkinter.Label(master, text=_("Database type") + " :").grid(row=1, column=0,
                                                                   sticky=tkinter.W)
        databaseTypeFrame = tkinter.Frame(master)
        databaseTypeFrame.grid(row=1, column=1, sticky=tkinter.EW)

        self.databaseType = tkinter.StringVar()
        self.databaseType.set(allDatabase[0]) # initialize
        for typeDB in allDatabase:
            tkinter.Radiobutton(databaseTypeFrame, text=typeDB,
                                variable=self.databaseType, value=typeDB) .pack(side=tkinter.LEFT)

        tkinter.Label(master,
                      text=_("Download init file") +
                      " :").grid(row=2, column=0, sticky=tkinter.W)
        tkinter.Button(master, text=_("Copy WEB link in clipboard"),
                       command=self.copylink).grid(row=2, column=1, sticky=tkinter.W)

        btnFileChooser = tkinter.Button(master, text=_("Database init file") + "...",
                                        command=self.chooseInitFile)
        btnFileChooser.grid(row=3, column=0, sticky=tkinter.W)
        self.initFilnameVar = tkinter.StringVar()
        initFileEntry = tkinter.Entry(master, textvariable=self.initFilnameVar, width=60)
        initFileEntry.grid(row=3, column=1, sticky=tkinter.W)

        return dbNameEntry # initial focus

    def chooseInitFile(self):
        """ Choose ans initialisation file """
        filename = filedialog.askopenfilename(filetypes=(("Zip File", "*.zip"),
                                                         ("CSV File", "*.csv"),
                                                         ("All Files", "*.*")),
                                              title=_("Choose a file"))

        if filename:
            self.initFilnameVar.set(filename)

    def copylink(self):
        """ Copy right link according database type in the clipboard """
        link = "?"
        type = self.databaseType.get()
        if type.startswith("Ciqual"):
            link = self.configApp.get('Ciqual', 'CiqualUrl')
            fileInfo = self.configApp.get('Ciqual', 'fileInfo')
        if type == "USDA_28":
            link = self.configApp.get('USDA', 'USDAUrl')
            fileInfo = self.configApp.get('USDA', 'fileInfo')
        self.parent.getMainWindow().copyInClipboard(link)
        title = _("Download a source file") + " " + type
        message = _("Open your web browser\nand download from") + "\n" + link
        message += "\n\n" + _("URL is in your clipboard\nready to be pasted in address bar") + "."
        message += "\n\n" + _("File to download on your computer") + " :\n" + fileInfo
        messagebox.showinfo(title=title, message=message)

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
