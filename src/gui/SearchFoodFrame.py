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
from database import Database

class SearchFoodFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, ressourcePath, logoFrame):
        """ Initialize welcome Frame """
        super(SearchFoodFrame, self).__init__(master, mainWindow, ressourcePath, logoFrame)
        self.numberFilter = int(self.configApp.get('Search', 'numberFilter'))

        filtersFrame = LabelFrame(self, text=_("Filters definition"))
        filtersFrame.pack(side=TOP, padx=5, pady=5)
        CallTypWindow.createToolTip(filtersFrame,
                                    _("Set logical expressions on filters lines")+\
                                    _("\nFilter line are combined with logical AND")+\
                                    _("\nTo deselect a filter line, set its operator to empty value"),
                                    self.delaymsTooltips * 3)

        buttonFiltersFrame = Frame(self)
        buttonFiltersFrame.pack(side=TOP, padx=5, pady=5)
        resultsFrame = LabelFrame(self, text=_("Foodstufs matching filters"))
        resultsFrame.pack(side=TOP, padx=5, pady=5)

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
                                         state="readonly", width=50)
            self.listConboboxComponents.append(componentCombobox)
            self.listConboboxComponents[numLine].grid(row=numLine+1, column=0)

            operatorCombobox = Combobox(filtersFrame, exportselection=0, values=valuesOperator,
                                        state="readonly", width=5)
            self.listOperatorCombobox.append(operatorCombobox)
            self.listOperatorCombobox[numLine].grid(row=numLine+1, column=1)

            self.listUserValueEntry.append(Entry(filtersFrame, width=10))
            self.listUserValueEntry[numLine].grid(row=numLine+1, column=2)

        # buttonFiltersFrame
        Button(buttonFiltersFrame, text=_("Search in database"),
               command=self.search).pack(side=LEFT)
        Button(buttonFiltersFrame, text=_("Reset filters"),
               command=self.reset).pack(side=LEFT)

        # resultsFrame components definition
        self.foundNamesListbox = Listbox(resultsFrame, height=12, width=75)
        self.foundNamesListbox.grid(row=0, columnspan=2)
        scrollbarNameRight = Scrollbar(resultsFrame, orient=VERTICAL,
                                       command=self.foundNamesListbox.yview)
        scrollbarNameRight.grid(row=0, column=2, sticky=W+N+S)
        self.foundNamesListbox.config(yscrollcommand=scrollbarNameRight.set)
        self.foundNamesListbox.bind('<ButtonRelease-1>', self.clicNamesListbox)

    def clicNamesListbox(self, evt):
        """ Update food definition with new components chosen """
        # Get selection
        selectedNames = list(self.foundNamesListbox.curselection())
        if len(selectedNames) > 0:
               foodName = self.foundNamesListbox.get(selectedNames[0])

        # Update foodstuffFrame comboboxes of calculator frame
        self.mainWindow.getCalculatorFrame().updateFoodstuffFrame(foodName)
        self.mainWindow.enableTabCalculator(True)


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
                                            " (" + component[2] + ")" +
                                            " [ " + str(component[3]) + " ; " +
                                            str(component[4]) + "] ")

        for numLine in range(self.numberFilter):
            self.listConboboxComponents[numLine]['values'] = valuesConboboxComponents

    def search(self):
        """ Search products that match filters in DB """
        database = self.mainWindow.getDatabase()
        assert (database is not None), "SearchFoodFrame/init() : no open database !"
        productNameAllOk = set()
        listProductListName = []
        try:
            for numLine in range(self.numberFilter):
               selectedOperator = self.listOperatorCombobox[numLine].get()
               if len(selectedOperator) > 0:

                    # Check fields for active filter lines
                    selectedComponent = self.listConboboxComponents[numLine].get()
                    if len(selectedComponent) == 0:
                        raise ValueError(_("Please select a component for filter number") +
                                         " : " + str(numLine+1))
                    try :
                        level = float(self.listUserValueEntry[numLine].get())
                    except ValueError as excName:
                        raise ValueError(_("Level must be a float number for filter number") +
                                         " : " + str(numLine+1))
                    if level < 0.0:
                        raise ValueError(_("Level must be greater than zero for filter number") +
                                         " : " + str(numLine+1))
                    # Get constituantCode
                    indexChoosenComponent = self.listConboboxComponents[numLine]['values'].index(selectedComponent)
                    constituantCode = self.listComponents[indexChoosenComponent][0]

                    # Build condition for extraction of products from BD
                    condition = " AND constituantCode=" + str(constituantCode) + \
                                " AND value" + selectedOperator + str(level)
                    listProductListName.append(set(database.getProductNamesCondition(condition)))

            # Intersection of all listProductListName sets
            if len(listProductListName[0]) > 0:
                productNameAllOk = listProductListName[0]
                index = 1
                while index < len(listProductListName):
                    productNameAllOk = productNameAllOk.intersection(listProductListName[index])
                    index = index + 1

                # Insert products names in the list
                self.foundNamesListbox.delete(0, END)
                for productName in list(productNameAllOk):
                    self.foundNamesListbox.insert(END, productName)

        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def reset(self):
        """ Reset filters in DB """
        for numLine in range(self.numberFilter):
            self.listOperatorCombobox[numLine].current(0)
