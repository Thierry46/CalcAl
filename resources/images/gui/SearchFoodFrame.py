# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : SearchFoodFrame
Author : Thierry Maillard (TMD)
Date  : 27/4/2016 - 4/12/2016

Role : Define search food frame content.
************************************************************************************
"""
import queue

import tkinter
from tkinter.ttk import Combobox

from model import SearchThreadedTask
from . import CallTypWindow
from . import FrameBaseCalcAl
from . import TableTreeView

class SearchFoodFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Search frame used to choose food according a component selection """

    def __init__(self, master, mainWindow, logoFrame, calculatorFrameModel):
        """ Initialize Search Frame """
        super(SearchFoodFrame, self).__init__(master, mainWindow, logoFrame)
        self.calculatorFrameModel = calculatorFrameModel
        self.calculatorFrameModel.addObserver(self)

        self.numberFilter = int(self.configApp.get('Search', 'numberFilter'))
        self.nbMaxResultSearch = int(self.configApp.get('Limits', 'nbMaxResultSearch'))
        maxWidthComponent = int(self.configApp.get('Search', 'maxWidthComponent'))
        self.endMarker = _("OK") # Marker at the beginning of last message
        self.listComponents = []
        self.queue = None

        topFrame = tkinter.Frame(self)
        topFrame.pack(side=tkinter.TOP)
        filtersFrame = tkinter.LabelFrame(topFrame, text=_("Filters definition"))
        filtersFrame.pack(side=tkinter.LEFT, padx=5, pady=5)
        CallTypWindow.createToolTip(filtersFrame,
                                    _("Set logical expressions on filters lines")+"\n"+\
                                    _("Filter line are combined with logical AND")+"\n"+\
                                    _("To deselect a filter line, set its operator to empty value"),
                                    self.delaymsTooltips * 3)

        buttonFiltersFrame = tkinter.Frame(topFrame)
        buttonFiltersFrame.pack(side=tkinter.LEFT, padx=5, pady=5)
        resultsFrame = tkinter.LabelFrame(self, text=_("Foodstufs matching filters (values for 100g)"))
        resultsFrame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.YES, padx=5, pady=2)
        resultsFrame.grid_rowconfigure(0, weight=1)
        resultsFrame.grid_columnconfigure(0, weight=1)

        # filtersFrame components definition
        listLabel = [_("Components"), _("Operator"), _("Levels")]
        for numCol in range(len(listLabel)):
            tkinter.Label(filtersFrame, text=listLabel[numCol]).grid(row=0, column=numCol)

        self.listConboboxComponents = []
        self.listOperatorCombobox = []
        self.listUserValueEntry = []
        valuesOperator = ["", "<=", ">="]
        for numLine in range(self.numberFilter):
            componentCombobox = Combobox(filtersFrame, exportselection=0,
                                         state="readonly",
                                         width=maxWidthComponent)
            self.listConboboxComponents.append(componentCombobox)
            self.listConboboxComponents[numLine].grid(row=numLine+1, column=0)

            operatorCombobox = Combobox(filtersFrame, exportselection=0, values=valuesOperator,
                                        state="readonly", width=5)
            operatorCombobox.bind('<<ComboboxSelected>>', self.eraseEmptyRows)
            self.listOperatorCombobox.append(operatorCombobox)
            self.listOperatorCombobox[numLine].grid(row=numLine+1, column=1)

            self.listUserValueEntry.append(tkinter.Entry(filtersFrame, width=10))
            self.listUserValueEntry[numLine].grid(row=numLine+1, column=2)

        # buttonFiltersFrame
        self.btnSearch = self.mainWindow.createButtonImage(buttonFiltersFrame,
                                                           imageRessourceName='btn_search',
                                                           text4Image=_("Search in data"))
        self.btnSearch.configure(command=self.search)
        self.btnSearch.pack(side=tkinter.TOP)
        tkinter.Button(buttonFiltersFrame, text=_("Reset filters"),
               command=self.reset).pack(side=tkinter.TOP)
        tkinter.Button(buttonFiltersFrame, text=_("Clipboard"),
                command=self.copyInClipboard).pack(side=tkinter.TOP)

        # resultsFrame components definition
        firstColumns = [_("Name")]
        heigthFoodTable = int(self.configApp.get('Size', 'searchResultTableNumberVisibleRows'))
        if self.mainWindow.isTinyScreen():
            heigthFoodTable -= 3
        self.searchResultTable = TableTreeView.TableTreeView(resultsFrame, firstColumns,
                        heigthFoodTable,
                        int(self.configApp.get('Size', 'searchResultTableFistColWidth')),
                        int(self.configApp.get('Size', 'searchResultTableOtherColWidth')),
                        int(self.configApp.get('Size', 'searchResultTableColMinWdth')),
                        selectmode="extended")
        self.searchResultTable.setColor('normalRow', self.configApp.get('Colors',
                                                                        'colorSearchTable'))
        self.searchResultTable.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.YES)
        self.searchResultTable.setBinding('<Double-Button-1>', self.putInCalculator)
        self.searchResultTable.setBinding('<Command-c>', self.copyInClipboard)
        self.searchResultTable.setBinding('<Control-c>', self.copyInClipboard)
        CallTypWindow.createToolTip(self.searchResultTable,
                        _("Click on first column header to select all") +
                        "\n" +
                        _("Click on a component column header to sort by this component values")+
                        "\n" +
                        _("Double-click on a result line to put it in calculator")+
                        "\n" +
                        _("Ctrl-C to put in clipboard"),
                        2 * self.delaymsTooltips)

    def updateObserver(self, observable, event):
        """Called when the model object is modified. """
        if observable == self.calculatorFrameModel:
            self.logger.debug("SearchFoodFrame received from model : " + event)
            try:
                if event == "INIT_DB":
                    self.init()
                else:
                    self.logger.debug("SearchFoodFrame : ignore event : " + event)

            except CalcalExceptions.CalcalValueError as exc:
                message = _("Error") + " : " + str(exc) + " !"
                self.mainWindow.setStatusText(message, True)

    def eraseEmptyRows(self, evt):
        """ Erase filter line if its operator is empty """
        for numLine in range(self.numberFilter):
            if self.listOperatorCombobox[numLine].get() == "":
                self.listConboboxComponents[numLine].set("")
                lenValueInEntry = len(self.listUserValueEntry[numLine].get())
                if lenValueInEntry > 0:
                    self.listUserValueEntry[numLine].delete(0, lenValueInEntry)

    def putInCalculator(self, event=None):
        """ Update food definition in calculator pane with new components chosen """
        try:
            # Get selection
            listSelectedRows = self.searchResultTable.getSelectedItems()
            if len(listSelectedRows) != 1:
                raise ValueError(_("Please select one and only one line in food table"))
            foodName = self.searchResultTable.getTextForItemIndex(listSelectedRows[0])

            # Update foodstuffFrame comboboxes of calculator frame
            self.mainWindow.getCalculatorFrame().updateFoodstuffFrame(foodName)
            self.mainWindow.enableTabCalculator(True)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def copyInClipboard(self, event=None):
        "Copy search results in clipboard"
        try:
            text = self.searchResultTable.getTableAsText()
            self.mainWindow.copyInClipboard(text)
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def init(self):
        """Initialyse filters combobox"""
        self.logger.debug("SearchFoodFrame/init()")
        self.searchResultTable.deleteAllRows()
        self.reset()

        database = self.databaseManager.getDatabase()
        assert (database is not None), "SearchFoodFrame/init() : no open database !"

        self.listComponents = database.getMinMaxForConstituants()
        assert (self.listComponents is not None), \
            "SearchFoodFrame/init() : no constituants in database !"
        valuesConboboxComponents = []
        for component in self.listComponents:
            valuesConboboxComponents.append(component[1] +
                                            " [ " + str(component[3]) + " "  + component[2] + " ; " +
                                            str(component[4]) + " " + component[2] + "] ")

        for numLine in range(self.numberFilter):
            self.listConboboxComponents[numLine]['values'] = valuesConboboxComponents

    def search(self):
        """ Search products that match filters in DB
            V0.31 : Thread use"""
        # Get selected components, operator and threshold to filter database
        try:
            listFilters = []
            listSelectedComponentsCodes = []
            listTitle4Components = []

            for numLine in range(self.numberFilter):
                selectedOperator = self.listOperatorCombobox[numLine].get()
                if len(selectedOperator) > 0:
                    # Check fields for active filter lines
                    selectedComponent = self.listConboboxComponents[numLine].get()
                    if len(selectedComponent) == 0:
                        raise ValueError(_("Please select a component for filter number") +
                                         " : " + str(numLine+1))
                    try:
                        level = float(self.listUserValueEntry[numLine].get().replace(",", "."))
                    except ValueError:
                        raise ValueError(_("Level must be a float number for filter number") +
                                         " : " + str(numLine+1))
                    if level < 0.0:
                        raise ValueError(_("Level must be greater than zero for filter number") +
                                     " : " + str(numLine+1))
                    # Get constituantCode
                    indexChoosenComponent = \
                            self.listConboboxComponents[numLine]['values'].index(selectedComponent)
                    constituantCode = self.listComponents[indexChoosenComponent][0]
                    if constituantCode not in listSelectedComponentsCodes:
                        listSelectedComponentsCodes.append(constituantCode)
                        constituantName = self.listComponents[indexChoosenComponent][1]
                        constituantUnit = self.listComponents[indexChoosenComponent][2]
                        listTitle4Components.append(constituantName + " (" + constituantUnit + ")")

                    # Append current filter to the list
                    listFilters.append([constituantCode, selectedOperator, level, constituantName])

            self.logger.debug("SearchFoodFrame/search() : listFilters = " + str(listFilters))
            # Clean result table
            self.searchResultTable.deleteAllRows()
            # Update table header line with components names selected in filters
            self.searchResultTable.updateVariablesColumns(listTitle4Components, [])

        	# Search food that match filter criteria
            self.queue = queue.Queue()
            SearchThreadedTask.SearchThreadedTask(self, self.queue, self.endMarker,
                                                  listFilters).start()
            self.master.after(100, self.process_queue)
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def process_queue(self):
        """ Display messages that thread have put in the queue """
        try:
            msg = self.queue.get(0)
            error = msg.endswith("!")
            self.mainWindow.setStatusText(msg, error)
            if not msg.startswith(self.endMarker) and not error:
                # Listen again to thread
                self.master.after(100, self.process_queue)
        except queue.Empty:
            self.master.after(100, self.process_queue)

    def reset(self):
        """ Reset filters in DB """
        for numLine in range(self.numberFilter):
            self.listOperatorCombobox[numLine].current(0)
