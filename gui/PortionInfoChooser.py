# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : PortionInfoChooser
Role : Get information from user to save a portion
Date  : 25/9/2016 - 25/11/2016

Licence : GPLv3
Copyright (c) 2015 - Thierry Maillard

This file is part of Calcal project.

Calcal project is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

FinancesLocales project is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Finance Locales project.  If not, see <http://www.gnu.org/licenses/>.
************************************************************************************
"""
import datetime

from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

from util import DateUtil
from . import TkSimpleDialog
from . import CallTypWindow

class PortionInfoChooser(TkSimpleDialog.TkSimpleDialog):
    """ Dialog box used to get information from user to save a portion """
    def __init__(self, parent, database, configApp, title=None):
        self.database = database
        self.configApp = configApp
        self.portionIdAll = list(self.database.getPortions())
        super(PortionInfoChooser, self).__init__(parent, title)

    def body(self, master):
        """ Body content of this dialog """
        delaymsTooltips = int(self.configApp.get('Limits', 'delaymsTooltips'))

        # Filters frame
        filtersFrame = LabelFrame(master, text=_("Filters"))
        filtersFrame.pack(side=TOP)
        Label(filtersFrame, text=_("Portion name") + " :").grid(row=0, column=0, sticky=W)
        self.nameVar = StringVar()
        self.nameVar.trace_variable("w", self.updatePortionListBox)
        nameEntry = Entry(filtersFrame, textvariable=self.nameVar)
        nameEntry.grid(row=0, column=2, sticky=W)
        nameEntry.focus_set()

        Label(filtersFrame, text=_("Date")).grid(row=1, column=0, sticky=W)
        Button(filtersFrame, text=_("Today"),
               command=self.setTodayDate).grid(row=1, column=1, sticky=W)
        self.dateVar = StringVar()
        self.dateVar.trace_variable("w", self.updatePortionListBox)
        dateEntry = Entry(filtersFrame, textvariable=self.dateVar)
        dateEntry.grid(row=1, column=2, sticky=W)
        CallTypWindow.createToolTip(dateEntry,
                                    _("Allowed formats for dates")+":\n"+\
                                    _("DD/MM/YYYY") + ", " +  _("DD/MM/YY") + ", " + \
                                    _("YYYY/MM/DD"),
                                    delaymsTooltips)


        Label(filtersFrame, text=_("Patient code") + " :").grid(row=2, column=0, sticky=W)
        listPatientCodes = [""] + self.parent.getPatientFrameModel().getAllPatientCodes()
        self.patientCodeCombobox = Combobox(filtersFrame, exportselection=0,
                                            state="readonly", width=20,
                                            values=listPatientCodes)
        self.patientCodeCombobox.bind('<<ComboboxSelected>>', self.updatePortionListBox)
        self.patientCodeCombobox.grid(row=2, column=2, sticky=W)


        Button(filtersFrame, text=_("Erase filters"),
               command=self.eraseFilters).grid(row=3, column=1, sticky=W)

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

    def setTodayDate(self):
        """ Display today date in date field """
        dateNow = datetime.datetime.now()
        dateFormated = '{:04d}/{:02d}/{:02d}'.format(dateNow.year, dateNow.month, dateNow.day)
        self.dateVar.set(dateFormated)

    def eraseFilters(self):
        """ Set to empty string id filters fields """
        self.nameVar.set("")
        self.dateVar.set("")
        self.patientCodeCombobox.set("")

    def clicExistingPortion(self, evt):
        """ Update portion input field with chosen listbox item """
        # Get selection
        selectedExistingPortion = list(self.portionListBox.curselection())
        if len(selectedExistingPortion) > 0:
            nameDate = self.portionListBox.get(selectedExistingPortion[0]).split(" / ")
            self.nameVar.set(nameDate[0])
            dateRead = nameDate[1]
            try:
                DateUtil.formatDate(dateRead)
            except ValueError as exc:
                self.bell()
                messagebox.showwarning(_("Loading values"),
                                       str(exc) + "\n" +
                                       _("Please correct the date displayed") + " !")
            self.dateVar.set(dateRead)
            self.patientCodeCombobox.set(nameDate[2])
            self.portionTypeVar.set(nameDate[3])
            self.periodCombobox.set(nameDate[4])

    def updatePortionListBox(self, *args):
        """ Update portionListBox filtering with id frame fields content """
        self.portionListBox.delete(0, END)
        userIdFilters = [self.nameVar.get(), self.dateVar.get(), self.patientCodeCombobox.get()]
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
            DateUtil.formatDate(self.dateVar.get())
            if self.patientCodeCombobox.get() == "":
                raise ValueError(_("Please give a patient code"))
            if self.portionTypeVar.get() == "":
                raise ValueError(_("Please give a portion type"))
            if self.periodCombobox.get() == "":
                raise ValueError(_("Please give a period"))

            # Ask if portion exists
            code, portionExists = self.database.getPortionCode(self.nameVar.get(),
                                                               self.dateVar.get(),
                                                               self.patientCodeCombobox.get())

            if portionExists:
                isMofificationOk = messagebox.askyesno(_("Add or modify Portion in database"),
                        _("Do you really want to modify this existing portion in database ?") + \
                        "\n" + _("Portion code") + " : " + str(code) + \
                        "\n" + _("Portion name") + " : " + self.nameVar.get() + \
                        "\n" + _("Date") + " : "  + self.dateVar.get() + \
                        "\n" + _("Patient code") + " : "  + self.patientCodeCombobox.get(),
                        icon='warning')
                if not isMofificationOk:
                    raise ValueError(_("Please modify portion identificators"))

            isOK = True
        except ValueError as exc:
            self.bell()
            messagebox.showwarning(_("Bad input"), message=_("Error") + " : " + str(exc) + " !")
        return isOK

    def apply(self):
        self.setResult([self.nameVar.get(), self.dateVar.get(), self.patientCodeCombobox.get(),
                        self.portionTypeVar.get(), self.periodCombobox.get()])
