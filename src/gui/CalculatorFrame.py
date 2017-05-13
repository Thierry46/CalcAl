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
from gui import TableTreeView
from gui import FamilyNameChooser

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
        upperLeftFrame.pack(side=LEFT, padx=5)
        upperMiddleFrame = Frame(upperFrame)
        upperMiddleFrame.pack(side=LEFT, padx=5)
        foodstuffFrame = LabelFrame(upperMiddleFrame, text=_("Foodstuff definition"))
        foodstuffFrame.pack(side=TOP)
        upperRightFrame = LabelFrame(upperFrame, text=_("Interesting components"))
        upperRightFrame.pack(side=LEFT, padx=5)

        # SearchFoodByNameFrame
        upperLeftFrameUp = Frame(upperLeftFrame)
        upperLeftFrameUp.pack(side=TOP)
        Label(upperLeftFrameUp, text=_("Name") +  " :").pack(side=LEFT)
        self.nameToSearch = StringVar()
        self.nameToSearch.trace_variable("w", self.validateNameToSearchEntry)
        self.nameToSearchEntry = Entry(upperLeftFrameUp, textvariable=self.nameToSearch, width=10)
        self.nameToSearchEntry.pack(side=LEFT)
        CallTypWindow.createToolTip(self.nameToSearchEntry,
                  _("Use Wildcards :\n* replaces n chars\n? replaces 1 only")+"\n"+\
                  _("Ex.:fr*s -> fruits, frais,...")+"\n"+\
                  _("Use ? for character letters like é, â, ô..."),
                                    self.delaymsTooltips * 2)
        SearchButton = Button(upperLeftFrameUp, text=_("Search by components"),
                            command=self.mainWindow.enableTabSearch)
        SearchButton.pack(side=LEFT)

        listNamesFrame = Frame(upperLeftFrame)
        listNamesFrame.pack(side=TOP, padx=5, pady=5)
        CallTypWindow.createToolTip(listNamesFrame,
                                    _("Click on food name to copy it in definition frame"),
                                    self.delaymsTooltips)
        self.foundNamesListbox = Listbox(listNamesFrame, height=7, width=40)
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
        self.foodstuffQuantityEntry.bind('<Return>', self.addFoodInTableEvt)
        self.foodstuffQuantityEntry.bind('<KP_Enter>', self.addFoodInTableEvt)

        # Button to put define food in table
        addFoodButton = self.mainWindow.createButtonImage(upperMiddleFrame,
                                               imageRessourceName='arrowDown',
                                               text4Image=_("Put in the list"))
        addFoodButton.configure(command=self.addFoodInTable)
        addFoodButton.pack(side=TOP, padx=5, pady=5)

        # Componants frame
        color = self.configApp.get('Colors', 'componentsListboxColor')
        self.componentsListbox = Listbox(upperRightFrame, selectmode=EXTENDED,
                                         background=color, height=10, width=18)
        self.componentsListbox.grid(row=0, columnspan=2)
        CallTypWindow.createToolTip(self.componentsListbox,
                                    _("Use Ctrl and Shift keys") + "\n" + \
                                    _("for multiple selection"),
                                    self.delaymsTooltips)
        scrollbarRight = Scrollbar(upperRightFrame, orient=VERTICAL,
                                   command=self.componentsListbox.yview)
        scrollbarRight.grid(row=0, column=2, sticky=W+N+S)
        self.componentsListbox.config(yscrollcommand=scrollbarRight.set)
        self.componentsListbox.bind('<ButtonRelease-1>', self.clicComponentsListbox)

        # Table for foods and their components
        mealFrame = LabelFrame(middleFrame, text=_("List of food"))
        mealFrame.pack(side=TOP, fill=BOTH, expand=YES, padx=5, pady=2)
        mealFrame.grid_rowconfigure(0, weight=1)
        mealFrame.grid_columnconfigure(0, weight=1)
        firstColumns = [_("Name"), _("Qty (g)")]
        self.foodTable = TableTreeView.TableTreeView(mealFrame, firstColumns,
                                int(self.configApp.get('Size', 'foodTableNumberVisibleRows')),
                                int(self.configApp.get('Size', 'foodTableFistColWidth')),
                                int(self.configApp.get('Size', 'foodTableOtherColWidth')),
                                int(self.configApp.get('Size', 'foodTableColMinWdth')),
                                selectmode="extended")
        self.foodTable.setColor('normalRow', self.bgValueComp)
        self.foodTable.setColor('totalRow', self.bgLabelFC)
        self.foodTable.pack(side=TOP, fill=BOTH, expand=YES)
        self.foodTable.setBinding('<Double-Button-1>', self.copySelectionInDefinitionFrame)
        self.foodTable.setBinding('<Command-c>', self.copyInClipboard)
        self.foodTable.setBinding('<Control-c>', self.copyInClipboard)
        CallTypWindow.createToolTip(self.foodTable,
                                    _("Use Ctrl and Shift keys") + " " + \
                                    _("for multiple selection") + "\n" + \
                                    _("Clic on header :") + "\n" + \
                                    _("- of 1st column to select or unselect all") + "\n" + \
                                    _("- of other column to sort rows" ),
                                    2 * self.delaymsTooltips)

        # Buttons for action on selection
        if self.mainWindow.isBigScreen():
            modifySelection = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                               imageRessourceName='arrowUp',
                                               text4Image=_("Modify"))
            modifySelection.configure(command=self.copySelectionInDefinitionFrame)
            modifySelection.pack(side=LEFT)
            groupSelectionButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                 imageRessourceName='groupSelection',
                                                 text4Image=_("Group"))
            groupSelectionButton.configure(command=self.groupFood)
            groupSelectionButton.pack(side=LEFT)
            ungroupSelectionButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                     imageRessourceName='ungroupSelection',
                                                     text4Image=_("Ungroup"))
            ungroupSelectionButton.configure(command=self.UngroupFood)
            ungroupSelectionButton.pack(side=LEFT)
            deleteFoodButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                  imageRessourceName='deleteSelection',
                                                  text4Image=_("Delete"))
            deleteFoodButton.configure(command=self.deleteFood)
            deleteFoodButton.pack(side=LEFT)
            copyInClipboardFoodButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                        imageRessourceName='copy2clipboard',
                                                        text4Image=_("Clipboard"))
            copyInClipboardFoodButton.configure(command=self.copyInClipboard)
            copyInClipboardFoodButton.pack(side=LEFT)

        # Energy table
        energyFrame = LabelFrame(bottomFrame, text=_("Energy given by foods"))
        energyFrame.pack(side=LEFT)
        listComp = self.configApp.get('Energy', 'EnergeticComponentsCodes')
        self.EnergeticComponentsCodes = [int(code) for code in listComp.split(";")]
        self.emptyComponents = ['-' for index in range(len(self.EnergeticComponentsCodes))]
        listEnergy = self.configApp.get('Energy', 'EnergySuppliedByComponents')
        self.EnergySuppliedByComponents = [float(value) for value in listEnergy.split(";")]
        assert len(self.EnergeticComponentsCodes) == len(self.EnergySuppliedByComponents), \
                "pb in ini file : EnergeticComponentsCodes and EnergySuppliedByComponents" +\
                " must have the same number of elements"
        self.energyTable = TableTreeView.TableTreeView(energyFrame, [_("Components")],
                                      int(self.configApp.get('Size', 'energyTableNumberVisibleRows')),
                                      int(self.configApp.get('Size', 'energyTableFirstColWidth')),
                                      int(self.configApp.get('Size', 'energyTableOtherColWidth')),
                                      int(self.configApp.get('Size', 'energyTableColMinWdth')),
                                      selectmode="extended")
        self.energyTable.setColor('normalRow', self.bgValueComp)
        self.energyTable.pack(side=TOP)
        self.energyTable.setBinding('<Command-c>', self.copyEnergyInClipboard)
        self.energyTable.setBinding('<Control-c>', self.copyEnergyInClipboard)

        # Water frame
        waterFrame = LabelFrame(bottomFrame, text=_("Water needed"))
        waterFrame.pack(side=LEFT, padx=5, pady=5)
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

        # Update energy table componants name and their units
        componentsName = []
        for componentCode in self.EnergeticComponentsCodes:
            for component in self.listComponents:
                if componentCode == component[0]:
                    componentsName.append(component[1])
        self.energyTable.updateVariablesColumns(componentsName, None)

        # Limit width size of main window
        self.mainWindow.maxsize(int(self.mainWindow.winfo_width()),
                                int(self.mainWindow.winfo_screenheight()))

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
        selectedComponentsName = [self.componentsListbox.get(index)
                                  for index in self.selectedComponents]
        self.foodTable.deleteRow(_("Total"))
        listStableRows = self.foodTable.getStableColumnsValues(excludeRowWithTitle=_("Total"))
        listNamesQties = [[foodName, float(lQuantity[0])] for foodName, lQuantity in listStableRows]
        listComponentsCodes = [self.listComponents[numSelectedComponent][0]
                                for numSelectedComponent in self.selectedComponents]
        database = self.mainWindow.getDatabase()
        listComponentsValues= []
        for foodName, quantity in listNamesQties:
            componentsValues = database.getComponentsValues4Food(foodName, quantity,
                                                                 listComponentsCodes)
            listComponentsValues.append(componentsValues)
        self.foodTable.updateVariablesColumns(selectedComponentsName, listComponentsValues)
        self.addTotalRow()

    def addFoodInTableEvt(self, event):
        """ Called when hitting Retun key in foodstuffQuantity entry """
        self.addFoodInTable()

    def addFoodInTable(self, foodNameAndQuantity = None, withTotalLine=True):
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
                    quantity = float(self.foodstuffQuantity.get().replace(',', '.'))
                except ValueError as excName:
                    raise ValueError(_("Food quantity must be a number"))
                if quantity <= 0.:
                    raise ValueError(_("Qantity must be greater than zero"))

            #Get values in database
            listComponentsCodes = [self.listComponents[numSelectedComponent][0]
                                   for numSelectedComponent in self.selectedComponents]
            database = self.mainWindow.getDatabase()
            assert (database is not None), "CalculatorFrame/addFoodInTable() : no open database !"
            listComponentsValues = database.getComponentsValues4Food(foodName, quantity,
                                                                     listComponentsCodes)
            self.foodTable.deleteRow(_("Total"))
            columnsValues = [quantity] + listComponentsValues
            self.foodTable.insertOrCreateRow(foodName, columnsValues)
            if withTotalLine:
                self.addTotalRow()

            self.updateEnergyTable()
            self.updateWaterFrame()

            self.mainWindow.setStatusText(_("Foodstuff") + " " + foodName + " " + _("added"))
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def groupFood(self):
        """ Group and Save foodstuffs that are selected by user in Database """
        listComponentsCodes = [component[0] for component in self.listComponents]
        listStableRows = self.foodTable.getStableColumnsValues(excludeRowWithTitle=_("Total"),
                                                               onlySelected=True)
        try :
            if len(listStableRows) < 2 :
                raise ValueError(_("Please select more than one foodstuff in food table"))
            listNamesQties = [[foodName, float(lQuantity[0])] for foodName, lQuantity in listStableRows]
            database = self.mainWindow.getDatabase()

            # Ask new name and family for this new product
            dialog = FamilyNameChooser.FamilyNameChooser(self, database, self.configApp,
                                                         title=_("Save group in database"))
            results = dialog.getResult()
            if results == None:
                raise ValueError(_("Group recording canceled"))

            # Insert new produt in database
            familyName = results[0]
            productName = results[1]
            totalQuantity = database.insertNewComposedProduct(productName, familyName,
                                                              listNamesQties)

            # Update family listbox
            listFamily = list(self.familyFoodstuffCombobox['values'])
            if familyName not in listFamily:
                listFamily.append(familyName)
                self.familyFoodstuffCombobox['values'] = listFamily

            # Delete Grouped elements and add new group stuff
            self.deleteFood(self.foodTable.getSelectedItems(excludeRowWithTitle=_("Total")))
            self.addFoodInTable((productName, totalQuantity))

            self.mainWindow.setStatusText(_("New product") + " " + productName + " " +
                                          _("saved in database"))
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def UngroupFood(self):
        """ Ungroup and Save foodstuffs that are selected by user in Database """
        listComponentsCodes = self.listComponents
        listSelectedRows = self.foodTable.getSelectedItems(excludeRowWithTitle=_("Total"))
        try :
            if len(listSelectedRows) != 1:
                raise ValueError(_("Please select one and only one line in food table"))
            foodName = self.foodTable.getTextForItemIndex(listSelectedRows[0])
            quantity = float(self.foodTable.getItemValue(listSelectedRows[0], 0))
            # Get part of this composed products
            database = self.mainWindow.getDatabase()
            assert (database is not None), "CalculatorFrame/UngroupFood() : no open database !"
            foodNamesAndQuantities = database.getPartsOfComposedProduct(foodName, quantity)
            self.deleteFood(listSelectedRows)
            for nameQty in foodNamesAndQuantities:
                self.addFoodInTable(nameQty, False)
            self.addTotalRow()
            self.mainWindow.setStatusText(_("Composed product") + " " + foodName + " " +
                                                  _("ungrouped"))
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def deleteFood(self, listSelectedRows=None):
        """ Delete foodstuffs in table that are selected by user """
        isDestructionOk = True
        if not listSelectedRows:
            listSelectedRows = self.foodTable.getSelectedItems(excludeRowWithTitle=_("Total"))
            isDestructionOk = False
        nbSelectedRows = len(listSelectedRows)
        try :
            if len(listSelectedRows) < 1:
                raise ValueError(_("Please select at least one line in food table"))
            if not isDestructionOk:
                isDestructionOk = messagebox.askyesno(_("Deleting selected food in table"),
                                                      _("Do you want to delete selection ?"),
                                                      icon='warning')
            if isDestructionOk:
                self.foodTable.deleteListItems(listSelectedRows)
                self.foodTable.deleteRow(_("Total"))
                self.addTotalRow()

                self.updateEnergyTable()
                self.updateWaterFrame()

                if nbSelectedRows < 2:
                    foodstuff = _("foodstuff")
                else:
                    foodstuff = _("foodstuffs")
                message = str(nbSelectedRows) + " " + foodstuff + " " + _("deleted")
                self.mainWindow.setStatusText(message)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def copySelectionInDefinitionFrame(self, event=None):
        """ Copy name and quatity of first element selected in foodTable to meal definition frame """
        try :
            listSelectedRows = self.foodTable.getSelectedItems(excludeRowWithTitle=_("Total"))
            if len(listSelectedRows) != 1:
                raise ValueError(_("Please select one and only one line in food table"))
            foodName = self.foodTable.getTextForItemIndex(listSelectedRows[0])
            if foodName == _("Total"):
                raise ValueError(_("Total") + " " + _("can't be modified"))
            # Update foodstuffFrame comboboxes
            self.updateFoodstuffFrame(foodName)
            # Update quantity
            quantity = self.foodTable.getItemValue(listSelectedRows[0], 0)
            self.foodstuffQuantity.set(quantity)
            message = _("foodstuff") + " " + foodName + " " + _("copied in modification area")
            self.mainWindow.setStatusText(message)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def copyInClipboard(self, event=None):
        "Copy selected food in clipboard"
        try:
            text = self.foodTable.getTableAsText()
            self.mainWindow.copyInClipboard(text)
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def copyEnergyInClipboard(self, event=None):
        "Copy selected energy item in clipboard"
        try:
            text = self.energyTable.getTableAsText()
            self.mainWindow.copyInClipboard(text)
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def addTotalRow(self):
        """ Sum all colomns of foodTable and add a total line to food table """
        listComponentsCodes = [self.listComponents[numSelectedComponent][0]
                                for numSelectedComponent in self.selectedComponents]
        listStableRows = self.foodTable.getStableColumnsValues(excludeRowWithTitle=_("Total"))
        if len(listStableRows) > 0 :
            listNamesQties = [[foodName, float(lQuantity[0])] for foodName, lQuantity in listStableRows]
            database = self.mainWindow.getDatabase()
            sumQuantities, listComponentsValues = database.sumComponents4FoodListFormated(
                                                                        listNamesQties, listComponentsCodes)
            columnsValues = [sumQuantities] + listComponentsValues
            self.foodTable.insertOrCreateRow(_("Total"), columnsValues, tag='totalRow')

    def updateEnergyTable(self):
        """ Update energy table according foodstuffs entered in foodTable """
        # Get sum values for energetic components
        listStableRows = self.foodTable.getStableColumnsValues(excludeRowWithTitle=_("Total"))
        if len(listStableRows) > 0 :
            listNamesQties = [[foodName, float(lQuantity[0])] for foodName, lQuantity in listStableRows]
            database = self.mainWindow.getDatabase()
            sumQuantities, totalComponentsValues = database.sumComponents4FoodList(listNamesQties,
                                                             self.EnergeticComponentsCodes)
            # Sort Component according the order of self.EnergeticComponentsCodes
            totalComponentsValuesSorted = []
            for codeComponent in self.EnergeticComponentsCodes:
                for comp in totalComponentsValues:
                    if codeComponent == comp[0]:
                        totalComponentsValuesSorted.append(comp)
            totalComponentsValues = totalComponentsValuesSorted
            sumEnergy = 0.0
            for totalCompValue, energyByComponent in zip(totalComponentsValues,
                                                         self.EnergySuppliedByComponents):
                sumEnergy = sumEnergy + totalCompValue[1] * energyByComponent

            # Compute ratio and energetic values to display
            supplyEnergyValues = []
            supplyEnergyRatio = []
            for indexComponent in range(len(totalComponentsValues)):
                energyByComponent = totalComponentsValues[indexComponent][1] * \
                                self.EnergySuppliedByComponents[indexComponent]
                qualifValue = ""
                if totalComponentsValues[indexComponent][2] == "<":
                    qualifValue = "< "
                supplyEnergyValues.append(qualifValue +
                                      self.formatFloatValue.format(energyByComponent) + " kcal")
                if sumEnergy < float(self.configApp.get("Limits", "near0")):
                    valuePercent = 0.0
                else:
                    valuePercent = round(energyByComponent *  100.0 / sumEnergy)
                supplyEnergyRatio.append(str(valuePercent) + " %")
        else: # if len(listNamesQties) > 0
            supplyEnergyValues = self.emptyComponents
            supplyEnergyRatio = self.emptyComponents

        # Update rows
        self.energyTable.insertOrCreateRow(_("By ratio"), supplyEnergyRatio)
        self.energyTable.insertOrCreateRow(_("By value"), supplyEnergyValues)


    def updateWaterFrame(self):
        """ Update water frame elements according foodstuffs entered in foodTable """
        waterInFood = '-'
        waterNeeded = '-'
        listComponentsCodes = [self.WaterCode, self.EnergyTotalKcalCode]
        bgWaterInFood = self.bgValueComp

        # Get sum values for energetic components
        listStableRows = self.foodTable.getStableColumnsValues(excludeRowWithTitle=_("Total"))
        if len(listStableRows) > 0 :
            listNamesQties = [[foodName, float(lQuantity[0])] for foodName, lQuantity in listStableRows]
            database = self.mainWindow.getDatabase()
            sumQuantities, totalComponentsValues = database.sumComponents4FoodList(listNamesQties,
                                                                                   listComponentsCodes)
            waterInFood = self.formatFloatValue.format(totalComponentsValues[0][1]) + " ml"
            waterNeededFloat = totalComponentsValues[1][1] * self.warterMlFor1kcal
            waterNeeded = self.formatFloatValue.format(waterNeededFloat) + " ml"
            if totalComponentsValues[0][1] < waterNeededFloat:
                bgWaterInFood = self.configApp.get('Colors', 'colorWaterNOK')
            else:
                bgWaterInFood = self.configApp.get('Colors', 'colorWaterOK')
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
