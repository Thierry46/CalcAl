# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : PortionFrame
Author : Thierry Maillard (TMD)
Date   : 25/9/2016 - 13/11/2016

Role : Define portion frame content.
************************************************************************************
"""
from tkinter import *
from tkinter.ttk import Combobox

from . import CallTypWindow

from . import FrameBaseCalcAl
from . import TableTreeView
from database import Database

class PortionFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Portion frame used to manage ration and eaten food saved in database """

    def __init__(self, master, mainWindow, logoFrame, calculatorFrameModel):
        """ Initialize Portions Frame """
        super(PortionFrame, self).__init__(master, mainWindow, logoFrame)
        self.calculatorFrameModel = calculatorFrameModel
        self.calculatorFrameModel.addObserver(self)

        # Filters frame
        filtersFrame = LabelFrame(self, text=_("Filters"))
        filtersFrame.pack(side=TOP)
        Label(filtersFrame, text=_("Portion name")).grid(row=0, column=0, sticky=E)
        self.nameVar = StringVar()
        self.nameVar.trace_variable("w", self.updateSearchResultTable)
        nameEntry = Entry(filtersFrame, textvariable=self.nameVar)
        nameEntry.grid(row=0, column=1, sticky=W)
        nameEntry.focus_set()

        Label(filtersFrame, text=_("Date")).grid(row=1, column=0, sticky=E)
        self.dateVar = StringVar()
        self.dateVar.trace_variable("w", self.updateSearchResultTable)
        Entry(filtersFrame, textvariable=self.dateVar).grid(row=1, column=1, sticky=W)

        Label(filtersFrame, text=_("Patient code")).grid(row=2, column=0, sticky=E)
        self.patientVar = StringVar()
        self.patientVar.trace_variable("w", self.updateSearchResultTable)
        Entry(filtersFrame, textvariable=self.patientVar).grid(row=2, column=1, sticky=W)

        Label(filtersFrame, text=_("Portion type")).grid(row=0, column=2, sticky=E)
        portionTypeFrame = Frame(filtersFrame)
        portionTypeFrame.grid(row=0, column=3, sticky=EW)
        self.portionTypeVar = StringVar()
        self.portionTypeVar.trace_variable("w", self.updateSearchResultTable)
        Radiobutton(portionTypeFrame, text=_("All"),
                    variable=self.portionTypeVar, value="").pack(side=LEFT)
        Radiobutton(portionTypeFrame, text=_("Ration"),
                    variable=self.portionTypeVar, value=_("Ration")).pack(side=LEFT)
        Radiobutton(portionTypeFrame, text=_("Ingesta"),
                    variable=self.portionTypeVar, value=_("Ingesta")).pack(side=LEFT)

        Label(filtersFrame, text=_("Period Of day")).grid(row=1, column=2, sticky=E)
        periodValues = ["", _("Morning"), _("Noon"), _("Evening"), _("Day"), _("Other")]
        self.periodCombobox = Combobox(filtersFrame, exportselection=0, values=periodValues,
                                       state="readonly", width=10)
        self.periodCombobox.grid(row=1, column=3, sticky=W)
        self.periodCombobox.bind('<<ComboboxSelected>>', self.updateSearchResultTable)

        Button(filtersFrame, text=_("Erase filters"),
               command=self.init).grid(row=3, columnspan=4)

        # resultsFrame components definition
        resultsActionFrame = Frame(self)
        resultsActionFrame.pack(side=TOP)
        resultsFrame = LabelFrame(resultsActionFrame, text=_("Portions matching filters"))
        resultsFrame.pack(side=LEFT)
        # Code field is necessary because first column of TableTreeView must contain uniq values
        firstColumns = [_("Code"), _("Portion name"), _("Date"), _("Patient code"),
                        _("Portion type"), _("Period Of day")]
        self.portionResultTable = TableTreeView.TableTreeView(resultsFrame, firstColumns,
                     int(self.configApp.get('Size', 'portionResultTableNumberVisibleRows')),
                     int(self.configApp.get('Size', 'portionResultTableFirstColWidth')),
                     int(self.configApp.get('Size', 'portionResultTableOtherColWidth')),
                     int(self.configApp.get('Size', 'portionResultTableableColMinWdth')),
                     selectmode="extended")
        self.portionResultTable.setColor('normalRow',self.configApp.get('Colors',
                                                                       'colorPortionTable'))
        self.portionResultTable.pack(side=TOP, fill=BOTH, expand=YES)
        self.portionResultTable.setBinding('<Double-Button-1>', self.putInCalculator)
        self.portionResultTable.setBinding('<Command-c>', self.copyInClipboard)
        self.portionResultTable.setBinding('<Control-c>', self.copyInClipboard)
        CallTypWindow.createToolTip(self.portionResultTable,
                        _("Click on first column header to select all") +
                        "\n" +
                        _("Click on a component column header to sort by this component values")+
                        "\n" +
                        _("Double-click on a result line to put it in calculator")+
                        "\n" +
                        _("Ctrl-C to put in clipboard"),
                        2 * self.delaymsTooltips)
        # Command buttons
        ButtonFrame = Frame(resultsActionFrame)
        ButtonFrame.pack(side=LEFT)
        Button(ButtonFrame, text=_("Calculator"),
               command=self.putInCalculator).pack(side=TOP)
        Button(ButtonFrame, text=_("Delete Portion"),
               command=self.deletePortion).pack(side=TOP)
        Button(ButtonFrame, text=_("Clipboard"),
               command=self.copyInClipboard).pack(side=TOP)

    def update(self, observable, event):
        """Called when the model object is modified. """
        if observable == self.calculatorFrameModel:
            self.logger.debug("PortionFrame received from model : " + event)
            try:
                if event == "INIT_DB":
                    self.init()
                if event == "SAVE_PORTION":
                    self.updateSearchResultTable(None)
                else:
                    self.logger.debug("PortionFrame : ignore event : " + event)

            except CalcalExceptions.CalcalValueError as exc:
                message = _("Error") + " : " + str(exc) + " !"
                self.mainWindow.setStatusText(message, True)

    def putInCalculator(self, event=None):
        """ Update food definition in calculator pane with new components chosen """
        try :
            # Get selection
            listSelectedRows = self.portionResultTable.getSelectedItems()
            if len(listSelectedRows) != 1:
                raise ValueError(_("Please select one and only one line in portion table"))

            # Get all foodstuf that compose this portion
            portionCode = self.portionResultTable.getTextForItemIndex(listSelectedRows[0])

            # Ask to frame model to display chosen portion
            self.calculatorFrameModel.displayPortion(portionCode)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def copyInClipboard(self, event=None):
        "Copy search results in clipboard"
        try:
            text = self.portionResultTable.getTableAsText()
            self.mainWindow.copyInClipboard(text)
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def updateSearchResultTable(self, *args):
        """ Update portionResultTable filtering with id frame fields content """
        self.logger.debug("PortionFrame/updateSearchResultTable()")
        self.portionResultTable.deleteAllRows()
        listUserFilters = [self.nameVar.get(), self.dateVar.get(), self.patientVar.get(),
                           self.portionTypeVar.get(), self.periodCombobox.get()]
        database = self.databaseManager.getDatabase()
        assert (database is not None), "PortionFrame/addFoodInTable() : no open database !"
        # Code field is necessary because first column of TableTreeView must contain uniq values
        listPortions = database.getPortionsFiltred(listUserFilters, withCode=True)
        for portion in listPortions:
            self.portionResultTable.insertOrCreateRow(str(portion[0]), portion[1:])

    def init(self):
        """ Initialyse filters combobox
            Set to empty string id filters fields """
        self.nameVar.set("")
        self.dateVar.set("")
        self.patientVar.set("")
        self.portionTypeVar.set("")
        self.periodCombobox.set("")

    def deletePortion(self):
        """ Delete selected portion in database """
        try :
            # Get selection
            listSelectedRows = self.portionResultTable.getSelectedItems()
            if len(listSelectedRows) != 1:
                raise ValueError(_("Please select one and only one line in portion table"))
            portionCode = self.portionResultTable.getTextForItemIndex(listSelectedRows[0])
            isDestructionOk = messagebox.askyesno(_("Deleting selected user element in database"),
                                      _("Do you really want to delete selection in database ?") + \
                                      "\n" + _("Portion code") + " : " + portionCode,
                                      icon='warning')
            if isDestructionOk:
                # Delete portion in database
                database = self.databaseManager.getDatabase()
                assert (database is not None), "CalculatorFrame/deleteFood() : no open database !"
                database.deletePortion(portionCode)
                self.init()
                self.mainWindow.setStatusText(_("Portion deleted"))
            else:
                self.mainWindow.setStatusText(_("Destruction canceled"))

        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)
