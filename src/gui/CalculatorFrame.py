# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : CalculatorFrame
Author : Thierry Maillard (TMD)
Date  : 31/3/2016

Role : Define calculator frame content.
************************************************************************************
"""
from tkinter import *
from tkinter.ttk import Combobox
from tkinter import messagebox
from tkinter import font

from gui import CallTypWindow

from gui import FrameBaseCalcAl
from gui import Table
from database import Database

class CalculatorFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, ressourcePath, logoFrame):
        """ Initialize welcome Frame """
        super(CalculatorFrame, self).__init__(master, mainWindow, ressourcePath, logoFrame)
        self.formatFloatValue = "{0:." + self.configApp.get('Limits', 'nbMaxDigit') + "f}"
        self.bgLabelFC = self.configApp.get('Colors', 'colorLabelTableFood')
        self.bgLabelComp = self.configApp.get('Colors', 'colorComponantTableFood')
        self.bgNameTable = self.configApp.get('Colors', 'colorNameTableFood')
        self.bgValueComp = self.configApp.get('Colors', 'colorComponantValueTableFood')

        # List of tupple (code,shortcut,unit) for each existing components
        # Used to convert shortcuts to its unique code
        self.listComponents = []
        self.selectedComponents = []
        self.emptyComponents = []

        upperFrame = Frame(self)
        upperFrame.pack(side=TOP, fill=X)
        middleFrame = Frame(self)
        middleFrame.pack(side=TOP, fill=X)
        if self.mainWindow.isBigScreen():
            buttonSelectionFrame = LabelFrame(self, text=_("Actions on selection"))
            buttonSelectionFrame.pack(side=TOP)
        bottomFrame = Frame(self)
        bottomFrame.pack(side=TOP, fill=X)

        upperLeftFrame = LabelFrame(upperFrame, text=_("Search food"))
        upperLeftFrame.pack(side=LEFT, padx=5, pady=5)
        upperMiddleFrame = Frame(upperFrame)
        upperMiddleFrame.pack(side=LEFT, padx=5, pady=5)
        foodstuffFrame = LabelFrame(upperMiddleFrame, text=_("Foodstuff definition"))
        foodstuffFrame.pack(side=TOP)
        upperRightFrame = LabelFrame(upperFrame, text=_("Interesting components"))
        upperRightFrame.pack(side=LEFT, padx=5, pady=5)

        energyFrame = LabelFrame(bottomFrame, text=_("Energy given by foods"))
        energyFrame.pack(side=LEFT, padx=5, pady=5)
        waterFrame = LabelFrame(bottomFrame, text=_("Water needed"))
        waterFrame.pack(side=LEFT, padx=5, pady=5)


        # SearchFoodByNameFrame
        upperLeftFrameUp = Frame(upperLeftFrame)
        upperLeftFrameUp.pack(side=TOP)
        Label(upperLeftFrameUp, text=_("Name") +  " :").pack(side=LEFT)
        self.nameToSearch = StringVar()
        self.nameToSearch.trace_variable("w", self.validateNameToSearchEntry)
        self.nameToSearchEntry = Entry(upperLeftFrameUp, textvariable=self.nameToSearch)
        self.nameToSearchEntry.pack(side=LEFT)
        CallTypWindow.createToolTip(self.nameToSearchEntry,
                  _("Use Wildcards :\n* replaces n chars\n? replaces 1 only")+\
                  _("\nEx.:fr*s -> fruits, frais,...")+\
                  _("\nUse ? for character letters like é, â, ô..."),
                                    self.delaymsTooltips * 2)
        SearchButton = Button(upperLeftFrameUp, text=_("Search by components"),
                            command=self.displaySearchFrame)
        SearchButton.pack(side=LEFT)


        listNamesFrame = Frame(upperLeftFrame)
        listNamesFrame.pack(side=TOP, padx=5, pady=5)
        self.foundNamesListbox = Listbox(listNamesFrame, height=8, width=40)
        self.foundNamesListbox.grid(row=0, columnspan=2)
        scrollbarNameRight = Scrollbar(listNamesFrame, orient=VERTICAL,
                                       command=self.foundNamesListbox.yview)
        scrollbarNameRight.grid(row=0, column=2, sticky=W+N+S)
        self.foundNamesListbox.config(yscrollcommand=scrollbarNameRight.set)
        self.foundNamesListbox.bind('<ButtonRelease-1>', self.clicNamesListbox)


        # Foodstuff frame
        Label(foodstuffFrame, text=_("Family")).grid(row=0, column=0, sticky=E)
        self.familyFoodstuffCombobox = Combobox(foodstuffFrame, exportselection=0,
                                                state="readonly", width=30)
        self.familyFoodstuffCombobox.bind('<<ComboboxSelected>>', self.updatefoodstuffName)
        self.familyFoodstuffCombobox.grid(row=0, column=1, sticky=W)

        Label(foodstuffFrame, text=_("Name")).grid(row=1, column=0, sticky=E)
        self.foodstuffNameCombobox = Combobox(foodstuffFrame, exportselection=0,
                                      state="readonly", width=30)
        self.foodstuffNameCombobox.grid(row=1, column=1, sticky=W)

        Label(foodstuffFrame, text=_("Quantity (g)")).grid(row=2, column=0, sticky=E)
        self.foodstuffQuantity = StringVar()
        self.foodstuffQuantityEntry = Entry(foodstuffFrame, textvariable=self.foodstuffQuantity,
                                            width=10)
        self.foodstuffQuantityEntry.grid(row=2, column=1, sticky=W)

        # Button to put define food in table
        addFoodButton = self.createButtonImage(upperMiddleFrame,
                                               imageRessourceName='arrowDown',
                                               text4Image=_("Put in the list"))
        addFoodButton.configure(command=self.addFoodInTable)
        addFoodButton.pack(side=TOP, padx=5, pady=5)

        # Componants frame
        color = self.configApp.get('Colors', 'componentsListboxColor')
        self.componentsListbox = Listbox(upperRightFrame, selectmode=EXTENDED,
                                         background=color, height=11)
        self.componentsListbox.grid(row=0, columnspan=2)
        CallTypWindow.createToolTip(self.componentsListbox,
                                    _("Use Ctrl and Shift keys\nfor multiple selection"),
                                    self.delaymsTooltips)
        scrollbarRight = Scrollbar(upperRightFrame, orient=VERTICAL,
                                   command=self.componentsListbox.yview)
        scrollbarRight.grid(row=0, column=2, sticky=W+N+S)
        self.componentsListbox.config(yscrollcommand=scrollbarRight.set)
        self.componentsListbox.bind('<ButtonRelease-1>', self.clicComponentsListbox)

        # Table for foods and their components
        mealFrame = LabelFrame(middleFrame, text=_("List of food"))
        mealFrame.pack(side=TOP, padx=5, pady=2, fill=X)
        # Scrollbar for tablefood
        vsb = Scrollbar(mealFrame, orient=VERTICAL)
        vsb.grid(row=0, column=1, sticky=N+S)
        hsb = Scrollbar(mealFrame, orient=HORIZONTAL)
        hsb.grid(row=1, column=0, sticky=E+W)
        self.canvas = Canvas(mealFrame, borderwidth=0,
                             yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.canvas.grid(row=0, column=0, sticky=E+W)
        firstColumns = [_("Name"), _("Qty (g)")]
        self.foodTable = Table.Table(self.canvas, firstColumns,
                                     self.bgLabelFC,
                                     self.bgLabelComp)
        self.foodTable.pack(side=TOP)
        vsb.config(command=self.canvas.yview)
        hsb.config(command=self.canvas.xview)
        mealFrame.grid_rowconfigure(0, weight=1)
        mealFrame.grid_columnconfigure(0, weight=1)
        self.canvas.create_window(0, 0, window=self.foodTable)
        self.foodTable.bind("<Configure>", self.onFoodTableConfigure)

        numRow = self.foodTable.appendNewRow()
        firstColumns = [_("Total"), '0']
        self.foodTable.modifyRow(numRow, firstColumns,
                                 self.bgLabelFC,
                                 self.bgLabelComp)

        # Buttons for action on selection
        if self.mainWindow.isBigScreen():
            modifySelection = self.createButtonImage(buttonSelectionFrame,
                                               imageRessourceName='arrowUp',
                                               text4Image=_("Modify"))
            modifySelection.configure(command=self.CopySelection)
            modifySelection.pack(side=LEFT)
            groupSelectionButton = self.createButtonImage(buttonSelectionFrame,
                                                 imageRessourceName='groupSelection',
                                                 text4Image=_("Group"))
            groupSelectionButton.configure(command=self.groupFood)
            groupSelectionButton.pack(side=LEFT)
            ungroupSelectionButton = self.createButtonImage(buttonSelectionFrame,
                                                     imageRessourceName='ungroupSelection',
                                                     text4Image=_("Ungroup"))
            ungroupSelectionButton.configure(command=self.UngroupFood)
            ungroupSelectionButton.pack(side=LEFT)
            deleteFoodButton = self.createButtonImage(buttonSelectionFrame,
                                                  imageRessourceName='deleteSelection',
                                                  text4Image=_("Delete"))
            deleteFoodButton.configure(command=self.deleteFood)
            deleteFoodButton.pack(side=LEFT)

        # Energy table
        listComp = self.configApp.get('Energy', 'EnergeticComponentsCodes')
        self.EnergeticComponentsCodes = [int(code) for code in listComp.split(";")]
        listEnergy = self.configApp.get('Energy', 'EnergySuppliedByComponents')
        self.EnergySuppliedByComponents = [float(value) for value in listEnergy.split(";")]
        assert len(self.EnergeticComponentsCodes) == len(self.EnergySuppliedByComponents), \
                "pb in ini file : EnergeticComponentsCodes and EnergySuppliedByComponents" +\
                " must have the same number of elements"
        firstColumns = [_("Components")]
        self.energyTable = Table.Table(energyFrame, firstColumns,
                                       self.bgLabelFC,
                                       self.bgLabelComp,
                                       withCheckBox=False)
        self.energyTable.pack(side=TOP)
        # Init other rows for energyTable
        numRow = self.energyTable.appendNewRow()
        firstColumns = [_("By ratio")]
        self.energyTable.modifyRow(numRow, firstColumns,
                                   self.bgNameTable,
                                   self.bgValueComp)
        numRow = self.energyTable.appendNewRow()
        firstColumns = [_("By value")]
        self.energyTable.modifyRow(numRow, firstColumns,
                                   self.bgNameTable,
                                   self.bgValueComp)

        # Water frame
        self.EnergyTotalKcalCode = int(self.configApp.get('Energy', 'EnergyTotalKcalCode'))
        self.WaterCode = int(self.configApp.get('Water', 'WaterCode'))
        self.warterMlFor1kcal = float(self.configApp.get('Water', 'warterMlFor1kcal'))
        Label(waterFrame,
              text=_("Water supplied by food") + " : ",
              bg = self.bgNameTable).grid(row=0, column=0, sticky=E)
        self.labelWaterSupplied = Label(waterFrame, text="-", bg=self.bgValueComp)
        self.labelWaterSupplied.grid(row=0, column=1, sticky=W)
        Label(waterFrame,
              text=_("Water needed") + " : ",
              bg = self.bgNameTable).grid(row=1, column=0, sticky=E)
        self.labelWaterNeeded = Label(waterFrame, text="-", bg=self.bgValueComp)
        self.labelWaterNeeded.grid(row=1, column=1, sticky=W)

    def onFoodTableConfigure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def validateNameToSearchEntry(self, *args):
        """ File self.foundNamesListbox with products that match nameToSearchEntry content"""
        isNameFound = False
        foodNamePart = self.nameToSearch.get()

        # Search in database product containing foodNamePart
        if len(foodNamePart) > 0:
            database = self.mainWindow.getDatabase()
            assert (database is not None), "CalculatorFrame/validateNameToSearchEntry() : no open database !"
            listFoodName = database.getProductsNamesContainingPart(foodNamePart)
            # Update self.foundNamesListbox with results
            self.foundNamesListbox.delete(0, END)
            for name in listFoodName:
                self.foundNamesListbox.insert(END, name)
        else:
            self.foundNamesListbox.delete(0, END)

    def displaySearchFrame(self):
        """ Display search tab"""
        self.mainWindow.enableTabSearch(True)

    def init(self):
        """Initialyse calculator"""

        database = self.mainWindow.getDatabase()
        assert (database is not None), "CalculatorFrame/init() : no open database !"

        # Update components list
        self.componentsListbox.delete(0, END)
        self.listComponents = database.getListeComponents()
        assert (self.listComponents is not None), \
               "CalculatorFrame/init() : no constituants in database !"
        for component in self.listComponents:
            self.componentsListbox.insert(END, component[1] + ' (' + component[2] + ')')

        # Update familyFoodstuffCombobox
        listFamilyFoodstuff = database.getListeFamilyFoodstuff()
        assert (listFamilyFoodstuff is not None), "CalculatorFrame/init() : no family in database !"
        self.familyFoodstuffCombobox['values'] = listFamilyFoodstuff
        self.familyFoodstuffCombobox.current(0)

        # Update energy table componants name
        firstColumns = [self.energyTable.getCellValue(0, 0)]
        componentsName = []
        for componentCode in self.EnergeticComponentsCodes:
            for component in self.listComponents:
                if componentCode == component[0]:
                    componentsName.append(component[1])
        self.energyTable.adjustNumberOfColumn(len(componentsName))
        self.energyTable.modifyRow(0, firstColumns,
                         self.bgLabelFC,
                         self.bgLabelComp,
                         componentsName)
        self.emptyComponents = ['-' for index in range(len(self.EnergeticComponentsCodes))]
        numRow = self.energyTable.getRowForText(_("By ratio"), 0)
        assert numRow != -1, "energyTable: " + _("By ratio") + " not found"
        firstColumns = [_("By ratio")]
        self.energyTable.modifyRow(numRow, firstColumns,
                                   self.bgNameTable,
                                   self.bgValueComp,
                                   self.emptyComponents)
        numRow = self.energyTable.getRowForText(_("By value"), 0)
        assert numRow != -1, "energyTable: " + _("By value") + " not found"
        firstColumns = [_("By value")]
        self.energyTable.modifyRow(numRow, firstColumns,
                                   self.bgNameTable,
                                   self.bgValueComp,
                                   self.emptyComponents)

    def updatefoodstuffName(self, *args):
        """ Update foodstuff list name """
        database = self.mainWindow.getDatabase()
        assert (database is not None), "CalculatorFrame/updatefoodstuffName() : no open database !"
        familyname = self.familyFoodstuffCombobox.get()

        listFoodstuffName = database.getListeFoodstuffName(familyname)
        assert (listFoodstuffName is not None), \
            "CalculatorFrame/init() : no food name for family " + familyname + " in database  !"
        self.foodstuffNameCombobox['values'] = listFoodstuffName
        self.foodstuffNameCombobox.current(0)

    def clicNamesListbox(self, evt):
        """ Update food definition with new components chosen """
        # Get selection
        selectedNames = list(self.foundNamesListbox.curselection())
        if len(selectedNames) > 0:
            foodName = self.foundNamesListbox.get(selectedNames[0])

            # Update foodstuffFrame comboboxes
            self.updateFoodstuffFrame(foodName)

    def clicComponentsListbox(self, evt):
        """ Update foodTable list with new components chosen """
        self.selectedComponents = list(self.componentsListbox.curselection())

        # Adjust number of column in table (problem of table col reduction)
        # See : Table.py/deleteCol()
        self.foodTable.adjustNumberOfColumn(len(self.selectedComponents))

        # Display title in foodTable for self.selectedComponents
        selectedComponentsName = [self.componentsListbox.get(index)
                                    for index in self.selectedComponents]
        titleCol0 = self.foodTable.getCellValue(0, 0)
        titleCol1 = self.foodTable.getCellValue(0, 1)
        firstColumns = [titleCol0, titleCol1]
        self.foodTable.modifyRow(0, firstColumns,
                                 self.bgLabelFC,
                                 self.bgLabelComp,
                                 selectedComponentsName)

        # Update existing food rows
        database = self.mainWindow.getDatabase()
        assert (database is not None), "CalculatorFrame/clicComponentsListbox() : no open database !"
        listComponentsCodes = [self.listComponents[numSelectedComponent][0]
                                for numSelectedComponent in self.selectedComponents]
        listFoodName = self.foodTable.getColumnsValuesText(0, withFirstRow=False,
                                                           withLastRow=False,
                                                           onlyVisible=True)
        for foodName in listFoodName:
            numRow = self.foodTable.getRowForText(foodName, 0)
            assert (numRow != -1), "CalculatorFrame/clicComponentsListbox() : " + foodName +\
                                    " not found in table !"

            quantity = self.foodTable.getCellValueInt(numRow, 1)
            componentsValues = database.getComponentsValues4Food(foodName,
                                                                quantity,
                                                                listComponentsCodes)
            firstColumns = [foodName, str(quantity)]
            self.foodTable.modifyRow(numRow, firstColumns,
                                     self.bgNameTable,
                                     self.bgValueComp,
                                     componentsValues)

        # Update total table
        sumQuantities, listSumComponents = self.sumFoodTable()
        numRow = self.foodTable.getRowForText(_("Total"), 0)
        assert (numRow != -1), "CalculatorFrame/clicComponentsListbox() : Total column not found !"
        firstColumns = [_("Total"), str(sumQuantities)]
        self.foodTable.modifyRow(numRow, firstColumns,
                                      self.bgLabelFC,
                                      self.bgLabelComp,
                                      listSumComponents)

    def addFoodInTable(self, foodNameAndQuantity = None):
        """ Add a foodstuff in table """
        try :
            if foodNameAndQuantity:
                foodName = foodNameAndQuantity[0]
                quantity = foodNameAndQuantity[1]
            else:
                # Check User's input data
                foodName= self.foodstuffNameCombobox.get()
                if foodName == "":
                    raise ValueError(_("Food name must not be empty"))
                try :
                    quantity = int(self.foodstuffQuantity.get())
                except ValueError as excName:
                    raise ValueError(_("Food quantity must be an integer"))
                if quantity <= 0:
                    raise ValueError(_("Qantity must be greater than zero"))

            #Get values in database
            componentsValues = None
            listComponentsCodes = [self.listComponents[numSelectedComponent][0]
                                   for numSelectedComponent in self.selectedComponents]
            if len(listComponentsCodes) > 0:
                database = self.mainWindow.getDatabase()
                assert (database is not None), "CalculatorFrame/addFoodInTable() : no open database !"
                componentsValues = database.getComponentsValues4Food(foodName, quantity,
                                                                         listComponentsCodes)

            # Set the number of the row to modify
            # Try to update foodName row or total rox if foodname not found
            addNewTotalLine = False
            numRow = self.foodTable.getRowForText(foodName, 0)
            if numRow == -1 :
                # Replace total line with line for this foodname -> No total line
                numRow = self.foodTable.getRowForText(_("Total"), 0)
                assert (numRow != -1), "CalculatorFrame/addFoodInTable() : Total column not found !"
                addNewTotalLine = True

            # Modify the row : food or total
            firstColumns = [foodName, str(quantity)]
            self.foodTable.modifyRow(numRow, firstColumns,
                                     self.bgNameTable,
                                     self.bgValueComp,
                                     componentsValues)

            # Add total line
            sumQuantities, listSumComponents = self.sumFoodTable()
            if addNewTotalLine:
                # Total line has been used for the new food, add a new one
                numRow = self.foodTable.appendNewRow()
            else:
                numRow = self.foodTable.getRowForText(_("Total"), 0)

            firstColumns = [_("Total"), str(sumQuantities)]
            self.foodTable.modifyRow(numRow, firstColumns,
                                     self.bgLabelFC,
                                     self.bgLabelComp,
                                     listSumComponents)
            self.updateEnergyTable()
            self.updateWaterFrame()

            self.mainWindow.setStatusText(_("Foodstuff") + " " + foodName + " " + _("added"))
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def groupFood(self):
        """ Group and Save foodstuffs that are selected by user in Database """
        listSelectedRows = self.foodTable.getSelectedRows()
        nbSelectedRows = len(listSelectedRows)
        if nbSelectedRows > 1:
            productName = simpledialog.askstring(_("Save selected food group in database"),
                                                 _("Enter the name of new product") + " : ")
            familyName = simpledialog.askstring(_("Save selected food group in database"),
                                                _("Enter the family name of new product") + " : ")
            # Get all selected products names and quantities
            listNamesQty = []
            for numRow in listSelectedRows:
                listNamesQty.append([self.foodTable.getCellValue(numRow, 0),
                                     self.foodTable.getCellValue(numRow, 1)])

            # Insert new produt in database
            database = self.mainWindow.getDatabase()
            assert (database is not None), "CalculatorFrame/groupFood() : no open database !"
            try:
                totalQuantity = database.insertNewComposedProduct(productName,
                                                                  familyName,
                                                                  listNamesQty)

                # Update family listbox
                liteFamily = list(self.familyFoodstuffCombobox['values'])
                liteFamily.append(familyName)
                self.familyFoodstuffCombobox['values'] = liteFamily

                # Delete Grouped elements and add new group stuff
                self.deleteFood(listSelectedRows)
                self.addFoodInTable((productName, totalQuantity))

                self.mainWindow.setStatusText(_("New product") + " " + productName + " " +
                                              _("saved in database"))
            except ValueError as exc:
                self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)
        else:
            self.mainWindow.setStatusText(_("Please select more than one foodstuff in list of food !"),
                                          True)

    def UngroupFood(self):
        """ Ungroup and Save foodstuffs that are selected by user in Database """
        listSelectedRows = self.foodTable.getSelectedRows()
        if len(listSelectedRows) == 1:
            foodName = self.foodTable.getCellValue(listSelectedRows[0], 0)
            quantity = int(self.foodTable.getCellValue(listSelectedRows[0], 1))
            # Get part of this composed products
            database = self.mainWindow.getDatabase()
            assert (database is not None), "CalculatorFrame/UngroupFood() : no open database !"
            try:
                foodNamesAndQuantities = database.getPartsOfComposedProduct(foodName, quantity)
                self.deleteFood(listSelectedRows)
                for nameQty in foodNamesAndQuantities:
                    self.addFoodInTable(nameQty)

            except ValueError as exc:
                self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)
        else:
            self.mainWindow.setStatusText(_("Please select one and only one line in list of food !"),
                                          True)

    def deleteFood(self, listSelectedRows=None):
        """ Delete foodstuffs in table that are selected by user """
        isDestructionOk = True
        if not listSelectedRows:
            listSelectedRows = self.foodTable.getSelectedRows()
            isDestructionOk = False
        nbSelectedRows = len(listSelectedRows)
        if nbSelectedRows > 0:
            if not isDestructionOk:
                isDestructionOk = messagebox.askyesno(_("Deleting selected food in table"),
                                                      _("Do you want to delete selection ?"),
                                                      icon='warning')
            if isDestructionOk:
                self.foodTable.deleteRow(listSelectedRows)
                # Update totals
                sumQuantities, listSumComponents = self.sumFoodTable()
                numRow = self.foodTable.getRowForText(_("Total"), 0)
                firstColumns = [_("Total"), str(sumQuantities)]
                self.foodTable.modifyRow(numRow, firstColumns,
                                         self.bgLabelFC,
                                         self.configApp.get('Colors', 'colorComponantTableFood'),
                                         listSumComponents)

                self.updateEnergyTable()
                self.updateWaterFrame()

                if nbSelectedRows < 2:
                    foodstuff = _("foodstuff")
                else:
                    foodstuff = _("foodstuffs")
                message = str(nbSelectedRows) + " " + foodstuff + " " + _("deleted")
                self.mainWindow.setStatusText(message)
        else:
            self.mainWindow.setStatusText(_("Please select at least one line in list of food !"),
                                      True)

    def CopySelection(self):
        """ Copy name and quatity of first element selected in foodTable to meal definition frame """
        listSelectedRows = self.foodTable.getSelectedRows()
        if len(listSelectedRows) == 1:
            foodName = self.foodTable.getCellValue(listSelectedRows[0], 0)

            # Update foodstuffFrame comboboxes
            self.updateFoodstuffFrame(foodName)

            # Update quantity
            quantity = self.foodTable.getCellValue(listSelectedRows[0], 1)
            self.foodstuffQuantity.set(quantity)
        else:
            self.mainWindow.setStatusText(_("Please select one and only one line in list of food !"),
                                          True)


    def sumFoodTable(self):
        """ Sum all colomns of foodTable and update totalTable """
        # Total row if exists must not be included in sum
        withLastRow = (self.foodTable.getRowForText(_("Total"), 0) == -1)
        sumQuantities = 0
        qtyValues = self.foodTable.getColumnsValuesInt(1, withLastRow=withLastRow)

        # Sum food quantities
        for qty in qtyValues:
            sumQuantities = sumQuantities + qty
        
        # Sum food components values
        listSumComponents = []
        listVisibleComponentsCols = self.foodTable.getListVisibleComponentsCols()
        for colComponent in listVisibleComponentsCols:
            if self.foodTable.getCellValue(0, colComponent) != '': # To bypass the problem of col del
                sumComponent = 0.0
                for qtyComp in self.foodTable.getColumnsValuesFloat(colComponent,
                                                                    withLastRow=withLastRow):
                    sumComponent = sumComponent + qtyComp
                listSumComponents.append(self.formatFloatValue.format(sumComponent))
            else:
                listSumComponents.append('')
        return sumQuantities, listSumComponents

    def updateEnergyTable(self):
        """ Update energy table according foodstuffs entered in foodTable """

        supplyEnergyValues = []
        supplyEnergyRatio = []

        # Get information from foodTable about visible food
        database = self.mainWindow.getDatabase()
        assert (database is not None), "CalculatorFrame/updateEnergyTable() : no open database !"
        foodNames = self.foodTable.getColumnsValuesText(0, withFirstRow=False, withLastRow=False,
                                                        onlyVisible=True)
        if len(foodNames) > 0:
            qtyValues = self.foodTable.getColumnsValuesInt(1, withFirstRow=False, withLastRow=False,
                                                       onlyVisible=True)

            # For each food, get and sum values for energetic components
            totalComponentsValues = [0.0 for component in self.EnergeticComponentsCodes]
            for indexFood in range(len(foodNames)):
                componentsValues = database.getComponentsValues4Food(foodNames[indexFood],
                                                                   qtyValues[indexFood],
                                                                   self.EnergeticComponentsCodes)
                for indexComponent in range(len(componentsValues)):
                    totalComponentsValues[indexComponent] = \
                                        totalComponentsValues[indexComponent] + \
                                        float(componentsValues[indexComponent])

            # Compute Energy given by each component
            supplyEnergyValues = []
            supplyEnergyRatio = []
            sumEnergy = 0.0
            # Sum every energies given by energetic components
            for indexComponent in range(len(totalComponentsValues)):
                sumEnergy = sumEnergy + totalComponentsValues[indexComponent] *\
                            self.EnergySuppliedByComponents[indexComponent]
            for indexComponent in range(len(totalComponentsValues)):
                energyByComponent = totalComponentsValues[indexComponent] * \
                                    self.EnergySuppliedByComponents[indexComponent]
                supplyEnergyValues.append(self.formatFloatValue.format(energyByComponent) + " kcal")
                supplyEnergyRatio.append(str(round(energyByComponent *  100.0 / sumEnergy)) + " %")
        else: # No food found
            supplyEnergyValues = self.emptyComponents
            supplyEnergyRatio = self.emptyComponents

        # Update rows
        numRow = self.energyTable.getRowForText(_("By ratio"), 0)
        assert numRow != -1, "energyTable: " + _("By ratio") + " not found"
        firstColumns = [_("By ratio")]
        self.energyTable.modifyRow(numRow, firstColumns,
                                   self.bgNameTable,
                                   self.bgValueComp,
                                   supplyEnergyRatio)
        numRow = self.energyTable.getRowForText(_("By value"), 0)
        assert numRow != -1, "energyTable: " + _("By value") + " not found"
        firstColumns = [_("By value")]
        self.energyTable.modifyRow(numRow, firstColumns,
                                   self.bgNameTable,
                                   self.bgValueComp,
                                   supplyEnergyValues)

    def updateWaterFrame(self):
        """ Update water frame elements according foodstuffs entered in foodTable """
        waterInFood = '-'
        waterNeeded = '-'
        waterEnergyCodes = [self.WaterCode, self.EnergyTotalKcalCode]
        bgWaterInFood = self.bgValueComp

        # Get information from foodTable about visible food
        database = self.mainWindow.getDatabase()
        assert (database is not None), "CalculatorFrame/updateWaterFrame() : no open database !"
        foodNames = self.foodTable.getColumnsValuesText(0, withFirstRow=False, withLastRow=False,
                                                        onlyVisible=True)
        if len(foodNames) > 0:
            qtyValues = self.foodTable.getColumnsValuesInt(1, withFirstRow=False, withLastRow=False,
                                                           onlyVisible=True)
            # For each food, get and sum values for water components
            totalComponentsValues = [0.0 for component in waterEnergyCodes]
            for indexFood in range(len(foodNames)):
                componentsValues = database.getComponentsValues4Food(foodNames[indexFood],
                                                                     qtyValues[indexFood],
                                                                     waterEnergyCodes)
                for indexComponent in range(len(componentsValues)):
                    totalComponentsValues[indexComponent] = \
                                        totalComponentsValues[indexComponent] + \
                                        float(componentsValues[indexComponent])
            waterInFoodFloat = totalComponentsValues[0]
            waterInFood = self.formatFloatValue.format(waterInFoodFloat) + " ml"
            waterNeededFloat = totalComponentsValues[1] * self.warterMlFor1kcal
            waterNeeded = self.formatFloatValue.format(waterNeededFloat) + " ml"
            if waterInFoodFloat < waterNeededFloat:
                bgWaterInFood = self.configApp.get('Colors', 'colorWaterNOK')
            else:
                    bgWaterInFood = self.configApp.get('Colors', 'colorWaterOK')
        else:
            bgWaterInFood = self.bgValueComp

        self.labelWaterSupplied.configure(text=waterInFood, bg=bgWaterInFood)
        self.labelWaterNeeded.configure(text=waterNeeded)

    def updateFoodstuffFrame(self, foodName):
        """Update familyFoodstuffCombobox and foodstuffNameCombobox in foodstuffFrame """
        database = self.mainWindow.getDatabase()
        assert (database is not None), "CalculatorFrame/updateFoodstuffFrame() : no open database !"
        familyName = database.getFamily4FoodName(foodName)

        # Update comboboxes and values
        indexFamily = self.familyFoodstuffCombobox['values'].index(familyName)
        self.familyFoodstuffCombobox.current(indexFamily)
        self.updatefoodstuffName()
        indexName = self.foodstuffNameCombobox['values'].index(foodName)
        self.foodstuffNameCombobox.current(indexName)

        # User messages
        message = _("Foodstuff") + " " + foodName + " " + _("selected and copied")
        self.mainWindow.setStatusText(message)
        self.logger.info(message)
