# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : FamilyNameChooser
Role : Family and food name chooser
Date  : 30/5/2016

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
        tkinter.Label(master, text=_("Family") + " :").pack(side=tkinter.TOP)
        self.familyVar = tkinter.StringVar()
        self.familyVar.trace_variable("w", self.updateFamilyList)
        familyEntry = tkinter.Entry(master, textvariable=self.familyVar)
        familyEntry.pack(side=tkinter.TOP)
        familyEntry.focus_set()
        familyListFrame = tkinter.Frame(master)
        familyListFrame.pack(side=tkinter.TOP)
        self.familyList = tkinter.Listbox(familyListFrame,
                                  background=self.configApp.get('Colors', 'colorFamilyList'),
                                  height=10, width=30)
        self.familyList.grid(row=0, columnspan=2)
        scrollbarRight = tkinter.Scrollbar(familyListFrame, orient=tkinter.VERTICAL,
                                   command=self.familyList.yview)
        scrollbarRight.grid(row=0, column=2, sticky=tkinter.W+tkinter.N+tkinter.S)
        self.familyList.config(yscrollcommand=scrollbarRight.set)
        self.familyList.bind('<ButtonRelease-1>', self.clicFamily)
        self.updateFamilyList()

        tkinter.Label(master, text=_("Name") + " :").pack(side=tkinter.TOP)
        self.nameVar = tkinter.StringVar()
        tkinter.Entry(master, textvariable=self.nameVar).pack(side=tkinter.TOP)
        return familyEntry # initial focus

    def clicFamily(self, dummy):
        """ Update food definition with new components chosen """
        # Get selection
        selectedFamily = list(self.familyList.curselection())
        if len(selectedFamily) > 0:
            self.familyVar.set(self.familyList.get(selectedFamily[0]))

    def updateFamilyList(self, *dummy):
        """ Update familyList filtering with self.familyVar Entry content """
        self.familyList.delete(0, tkinter.END)
        stringInFamily = self.familyVar.get()
        if stringInFamily == "":
            familyNamesFiltered = self.familyNames
        else:
            familyNamesFiltered = [name for name in self.familyNames
                                   if stringInFamily.upper() in name.upper()]
        for family in familyNamesFiltered:
            self.familyList.insert(tkinter.END, family)

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
