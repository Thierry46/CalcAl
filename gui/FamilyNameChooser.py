# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : FamilyNameChooser
Role : Family and food name chooser
Date  : 30/5/2016
************************************************************************************
"""
from tkinter import *
from tkinter import messagebox
from . import TkSimpleDialog

class FamilyNameChooser(TkSimpleDialog.TkSimpleDialog):
    """ Dialog box to choose a food name and family """
    def __init__(self, parent, database, configApp, title=None):
        self.database = database
        self.configApp = configApp
        self.familyNames = self.database.getListFamilyFoodstuff()
        super(FamilyNameChooser, self).__init__(parent, title)

    def body(self, master):
        """ Body content of this dialog """
        Label(master, text=_("Family") + " :").pack(side=TOP)
        self.familyVar = StringVar()
        self.familyVar.trace_variable("w", self.updateFamilyList)
        familyEntry = Entry(master, textvariable=self.familyVar)
        familyEntry.pack(side=TOP)
        familyEntry.focus_set()
        familyListFrame = Frame(master)
        familyListFrame.pack(side=TOP)
        self.familyList = Listbox(familyListFrame,
                                  background=self.configApp.get('Colors', 'colorFamilyList'),
                                  height=10, width=30)
        self.familyList.grid(row=0, columnspan=2)
        scrollbarRight = Scrollbar(familyListFrame, orient=VERTICAL,
                                   command=self.familyList.yview)
        scrollbarRight.grid(row=0, column=2, sticky=W+N+S)
        self.familyList.config(yscrollcommand=scrollbarRight.set)
        self.familyList.bind('<ButtonRelease-1>', self.clicFamily)
        self.updateFamilyList()

        Label(master, text=_("Name") + " :").pack(side=TOP)
        self.nameVar = StringVar()
        Entry(master, textvariable=self.nameVar).pack(side=TOP)
        return familyEntry # initial focus

    def clicFamily(self, evt):
        """ Update food definition with new components chosen """
        # Get selection
        selectedFamily = list(self.familyList.curselection())
        if len(selectedFamily) > 0:
            self.familyVar.set(self.familyList.get(selectedFamily[0]))

    def updateFamilyList(self, *args):
        """ Update familyList filtering with self.familyVar Entry content """
        self.familyList.delete(0, END)
        stringInFamily = self.familyVar.get()
        if stringInFamily == "":
            familyNamesFiltered = self.familyNames
        else:
            familyNamesFiltered = [name for name in self.familyNames
                                   if stringInFamily.upper() in name.upper()]
        for family in familyNamesFiltered:
            self.familyList.insert(END, family)

    def validate(self):
        """ Check Data entered by user
            if OK return True
        """
        isOK = False
        try:
            if self.familyVar.get() == "":
                raise ValueError(_("Please give a family"))
            if self.nameVar.get() == "":
                raise ValueError(_("Please give a food name"))
            # Name must not exist in database
            if self.database.existFoodstuffName(self.nameVar.get()):
                raise ValueError(_("Please give a food name that doesn't exist in database"))
            isOK = True
        except ValueError as exc:
            self.bell()
            messagebox.showwarning(_("Bad input"), message=_("Error") + " : " + str(exc) + " !")
        return isOK

    def apply(self):
        self.setResult([self.familyVar.get(), self.nameVar.get()])
