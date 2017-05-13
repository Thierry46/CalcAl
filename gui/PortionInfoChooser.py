# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : PortionInfoChooser
Role : Get information from user to save a portion
Date  : 25/9/2016
************************************************************************************
"""
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox
from . import TkSimpleDialog

class PortionInfoChooser(TkSimpleDialog.TkSimpleDialog):
    """ Dialog box used to get information from user to save a portion """
    def __init__(self, parent, database, configApp, title=None):
        self.database = database
        self.configApp = configApp
        self.portionIdAll = list(self.database.getPortions())
        super(PortionInfoChooser, self).__init__(parent, title)

    def body(self, master):
        """ Body content of this dialog """

        # Filters frame
        filtersFrame = LabelFrame(master, text=_("Filters"))
        filtersFrame.pack(side=TOP)
        Label(filtersFrame, text=_("Portion name") + " :").grid(row=0, column=0, sticky=W)
        self.nameVar = StringVar()
        self.nameVar.trace_variable("w", self.updatePortionListBox)
        nameEntry = Entry(filtersFrame, textvariable=self.nameVar)
        nameEntry.grid(row=0, column=1, sticky=W)
        nameEntry.focus_set()

        Label(filtersFrame, text=_("Date") + " :").grid(row=1, column=0, sticky=W)
        self.dateVar = StringVar()
        self.dateVar.trace_variable("w", self.updatePortionListBox)
        Entry(filtersFrame, textvariable=self.dateVar).grid(row=1, column=1, sticky=W)

        Label(filtersFrame, text=_("Patient code") + " :").grid(row=2, column=0, sticky=W)
        self.patientVar = StringVar()
        self.patientVar.trace_variable("w", self.updatePortionListBox)
        Entry(filtersFrame, textvariable=self.patientVar).grid(row=2, column=1, sticky=W)

        Button(filtersFrame, text=_("Erase filters"),
               command=self.eraseFilters).grid(row=3, columnspan=2)

        # Portion listbox frame
        idListFrame = Frame(master)
        idListFrame.pack(side=TOP)
        Label(idListFrame, text=_("Filtered existing portions")).grid(row=0, columnspan=2)
        self.portionListBox = Listbox(idListFrame,
                                  background=self.configApp.get('Colors', 'colorFamilyList'),
                                  height=10, width=35)
        self.portionListBox.grid(row=1, columnspan=2)
        scrollbarRight = Scrollbar(idListFrame, orient=VERTICAL,
                                   command=self.portionListBox.yview)
        scrollbarRight.grid(row=1, column=2, sticky=W+N+S)
        self.portionListBox.config(yscrollcommand=scrollbarRight.set)
        self.portionListBox.bind('<ButtonRelease-1>', self.clicExistingPortion)
        self.updatePortionListBox()

        # Otherfield frame
        otherfieldFrame = Frame(master)
        otherfieldFrame.pack(side=TOP)
        Label(otherfieldFrame, text=_("Portion type") + " :").grid(row=0, column=0, sticky=W)
        portionTypeFrame = Frame(otherfieldFrame)
        portionTypeFrame.grid(row=0, column=1, sticky=EW)
        self.portionTypeVar = StringVar()
        Radiobutton(portionTypeFrame, text=_("Ration"),
                    variable=self.portionTypeVar, value=_("Ration")).pack(side=LEFT)
        Radiobutton(portionTypeFrame, text=_("Ingesta"),
                    variable=self.portionTypeVar, value=_("Ingesta")).pack(side=LEFT)
                    
        Label(otherfieldFrame, text=_("Period Of day") + " :").grid(row=1, column=0, sticky=EW)
        periodValues = [_("Morning"), _("Noon"), _("Evening"), _("Day"), _("Other")]
        self.periodCombobox = Combobox(otherfieldFrame, exportselection=0, values=periodValues,
                             state="readonly", width=10)
        self.periodCombobox.grid(row=1, column=1, sticky=EW)

        return nameEntry # initial focus

    def eraseFilters(self):
        """ Set to empty string id filters fields """
        self.nameVar.set("")
        self.dateVar.set("")
        self.patientVar.set("")

    def clicExistingPortion(self, evt):
        """ Update portion input field with chosen listbox item """
        # Get selection
        selectedExistingPortion = list(self.portionListBox.curselection())
        if len(selectedExistingPortion) > 0:
            nameDate = self.portionListBox.get(selectedExistingPortion[0]).split(" / ")
            self.nameVar.set(nameDate[0])
            self.dateVar.set(nameDate[1])
            self.patientVar.set(nameDate[2])
            self.portionTypeVar.set(nameDate[3])
            self.periodCombobox.set(nameDate[4])

    def updatePortionListBox(self, *args):
        """ Update portionListBox filtering with id frame fields content """
        self.portionListBox.delete(0, END)
        userIdFilters = [self.nameVar.get(), self.dateVar.get(), self.patientVar.get()]
        portionIdFiltered = self.database.getPortionsFiltred(userIdFilters)
        portionListSeparatorSeparator = ' ' + \
            self.configApp.get('Other', 'portionListSeparatorSeparator') + ' '
        for portionId in portionIdFiltered:
            self.portionListBox.insert(END, portionListSeparatorSeparator.join(portionId))

    def validate(self):
        """ Check Data entered by user
            if OK return True
        """
        isOK = False
        try:
            if self.nameVar.get() == "":
                raise ValueError(_("Please give a portion name"))
            if self.dateVar.get() == "":
                raise ValueError(_("Please give a date"))
            if self.patientVar.get() == "":
                raise ValueError(_("Please give a patient code"))
            if self.portionTypeVar.get() == "":
                raise ValueError(_("Please give a portion type"))
            if self.periodCombobox.get() == "":
                raise ValueError(_("Please give a period"))

            # Ask if portion exists
            code, portionExists = self.database.getPortionCode(self.nameVar.get(),
                                                               self.dateVar.get(),
                                                               self.patientVar.get())

            if portionExists:
                isMofificationOk = messagebox.askyesno(_("Add or modify Portion in database"),
                        _("Do you really want to modify this existing portion in database ?") + \
                        "\n" + _("Portion code") + " : " + str(code) + \
                        "\n" + _("Portion name") + " : " + self.nameVar.get() + \
                        "\n" + _("Date") + " : "  + self.dateVar.get() + \
                        "\n" + _("Patient code") + " : "  + self.patientVar.get(),
                        icon='warning')
                if not isMofificationOk:
                    raise ValueError(_("Please modify portion identificators"))

            isOK = True
        except ValueError as exc:
            self.bell()
            messagebox.showwarning(_("Bad input"), message = _("Error") + " : " + str(exc) + " !")
        return isOK

    def apply(self):
        self.setResult([self.nameVar.get(), self.dateVar.get(), self.patientVar.get(),
                        self.portionTypeVar.get(), self.periodCombobox.get()])
