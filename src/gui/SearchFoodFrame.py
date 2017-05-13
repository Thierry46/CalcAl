# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : SearchFoodFrame
Author : Thierry Maillard (TMD)
Date  : 27/4/2016

Role : Define search food frame content.
************************************************************************************
"""
from tkinter import *
from tkinter.ttk import Combobox

from gui import CallTypWindow

from gui import FrameBaseCalcAl
from gui import TableTreeView
from database import Database

class SearchFoodFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, ressourcePath, logoFrame):
        """ Initialize welcome Frame """
        super(SearchFoodFrame, self).__init__(master, mainWindow, ressourcePath, logoFrame)
        self.numberFilter = int(self.configApp.get('Search', 'numberFilter'))
        self.nbMaxResultSearch = int(self.configApp.get('Limits', 'nbMaxResultSearch'))
        maxWidthComponent = int(self.configApp.get('Search', 'maxWidthComponent'))

        topFrame = Frame(self)
        topFrame.pack(side=TOP)
        filtersFrame = LabelFrame(topFrame, text=_("Filters definition"))
        filtersFrame.pack(side=LEFT, padx=5, pady=5)
        CallTypWindow.createToolTip(filtersFrame,
                                    _("Set logical expressions on filters lines")+"\n"+\
                                    _("Filter line are combined with logical AND")+"\n"+\
                                    _("To deselect a filter line, set its operator to empty value"),
                                    self.delaymsTooltips * 3)

        buttonFiltersFrame = Frame(topFrame)
        buttonFiltersFrame.pack(side=LEFT, padx=5, pady=5)
        resultsFrame = LabelFrame(self, text=_("Foodstufs matching filters (values for 100g)"))
        resultsFrame.pack(side=TOP, fill=BOTH, expand=YES, padx=5, pady=2)
        resultsFrame.grid_rowconfigure(0, weight=1)
        resultsFrame.grid_columnconfigure(0, weight=1)

        # filtersFrame components definition
        listLabel = [_("Components"), _("Operator"), _("Levels")]
        for numCol in range(len(listLabel)):
            Label(filtersFrame, text=listLabel[numCol]).grid(row=0, column=numCol)

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

            self.listUserValueEntry.append(Entry(filtersFrame, width=10))
            self.listUserValueEntry[numLine].grid(row=numLine+1, column=2)

        # buttonFiltersFrame
        btnSearch = self.mainWindow.createButtonImage(buttonFiltersFrame,
                                                      imageRessourceName='btn_search',
                                                      text4Image=_("Search in data"))
        btnSearch.configure(command=self.search)
        btnSearch.pack(side=TOP)
        Button(buttonFiltersFrame, text=_("Reset filters"),
               command=self.reset).pack(side=TOP)
        Button(buttonFiltersFrame, text=_("Clipboard"),
                command=self.copyInClipboard).pack(side=TOP)

        # resultsFrame components definition
        firstColumns = [_("Name")]
        self.searchResultTable = TableTreeView.TableTreeView(resultsFrame, firstColumns,
                        int(self.configApp.get('Size', 'searchResultTableNumberVisibleRows')),
                        int(self.configApp.get('Size', 'searchResultTableFistColWidth')),
                        int(self.configApp.get('Size', 'searchResultTableOtherColWidth')),
                        int(self.configApp.get('Size', 'searchResultTableColMinWdth')),
                        selectmode="extended")
        self.searchResultTable.setColor('normalRow',self.configApp.get('Colors',
                                                                       'colorSearchTable'))
        self.searchResultTable.pack(side=TOP, fill=BOTH, expand=YES)
        self.searchResultTable.setBinding('<Double-Button-1>', self.putInCalculator)
        self.searchResultTable.setBinding('<Command-c>', self.copyInClipboard)
        self.searchResultTable.setBinding('<Control-c>', self.copyInClipboard)

        CallTypWindow.createToolTip(self.searchResultTable,
                        _("Click on first column header to select all") +
                        "\n" +
                        _("Click on a component column header to sort by this component values")+
                        "\n" +
                        _("Click on a result line to put it in calculator"),
                        2 * self.delaymsTooltips)

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
        try :
            # Get selection
            listSelectedRows = self.searchResultTable.getSelectedItems()
            if len(listSelectedRows) != 1:
                raise ValueError(_("Please select one and only one line in food table"))
            foodName = self.searchResultTable.getTextForItemIndex(listSelectedRows[0])

            # Update foodstuffFrame comboboxes of calculator frame
            self.mainWindow.getCalculatorFrame().updateFoodstuffFrame(foodName)
            self.mainWindow.enableTabCalculator(True, init=False)
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
        self.reset()

        database = self.mainWindow.getDatabase()
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
        """ Search products that match filters in DB """
        productNameAllOk = set()
        listProductListName = []
        listSelectedComponentsCodes = []
        listTitle4Components = []
        isAtLeast1Filter = False

        # Clean result table
        self.searchResultTable.deleteAllRows()
        self.searchResultTable.updateVariablesColumns(listTitle4Components, [])
        database = self.mainWindow.getDatabase()

        try:
            for numLine in range(self.numberFilter):
               selectedOperator = self.listOperatorCombobox[numLine].get()
               if len(selectedOperator) > 0:
                    isAtLeast1Filter = True
                    # Check fields for active filter lines
                    selectedComponent = self.listConboboxComponents[numLine].get()
                    if len(selectedComponent) == 0:
                        raise ValueError(_("Please select a component for filter number") +
                                         " : " + str(numLine+1))
                    try :
                        level = float(self.listUserValueEntry[numLine].get().replace(",", "."))
                    except ValueError as excName:
                        raise ValueError(_("Level must be a float number for filter number") +
                                         " : " + str(numLine+1))
                    if level < 0.0:
                        raise ValueError(_("Level must be greater than zero for filter number") +
                                         " : " + str(numLine+1))
                    # Get constituantCode
                    indexChoosenComponent = self.listConboboxComponents[numLine]['values'].index(selectedComponent)
                    constituantCode = self.listComponents[indexChoosenComponent][0]
                    if constituantCode not in listSelectedComponentsCodes:
                        listSelectedComponentsCodes.append(constituantCode)
                        constituantName = self.listComponents[indexChoosenComponent][1]
                        constituantUnit = self.listComponents[indexChoosenComponent][2]
                        listTitle4Components.append(constituantName + " (" + constituantUnit + ")")

                    # Build condition for extraction of products from BD
                    condition = " AND constituantCode=" + str(constituantCode) + \
                                " AND value" + selectedOperator + str(level)
                    listProductListName.append(set(database.getProductNamesCondition(condition)))

            if (not isAtLeast1Filter):
                raise ValueError(_("Please select at least one operator in a filter line"))

            # Intersection of all listProductListName sets
            if len(listProductListName) > 0 and len(listProductListName[0]) > 0:
                productNameAllOk = listProductListName[0]
                index = 1
                while index < len(listProductListName):
                    productNameAllOk = productNameAllOk.intersection(listProductListName[index])
                    index = index + 1

            # Update table header line with selected components names
            # 28/5/2016 : Sort listTitle4Components to match component order given by
            # database.getComponentsValues4Food() function
            listTitle4Components.sort()
            self.searchResultTable.updateVariablesColumns(listTitle4Components, [])

            # Get components values for all results product
            counter = 0
            listComponentsValues= []
            for foodName in productNameAllOk:
                componentsValues = database.getComponentsValues4Food(foodName, 100.0,
                                                                     listSelectedComponentsCodes)
                self.searchResultTable.insertOrCreateRow(foodName, componentsValues,
                                                          seeItem=False)
                counter = counter + 1
                if counter >= self.nbMaxResultSearch:
                    break

            # Check number of results
            nbFoundProducts = len(productNameAllOk)
            if (nbFoundProducts > self.nbMaxResultSearch):
                self.mainWindow.setStatusText(_("Too many results") +" : " +
                                              str(self.nbMaxResultSearch) +
                                              " " + _("on") + " " + str(nbFoundProducts) +
                                              " " + _("displayed") + ". " +
                                              _("Please improve filters") + " !", True)
            else:
                self.mainWindow.setStatusText(str(nbFoundProducts) + " " +
                                          _("results matching filters"))
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def reset(self):
        """ Reset filters in DB """
        for numLine in range(self.numberFilter):
            self.listOperatorCombobox[numLine].current(0)
