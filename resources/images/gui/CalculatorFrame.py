# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : CalculatorFrame
Author : Thierry Maillard (TMD)
Date  : 31/3/2016 - 4/12/2016

Role : Define food calculator frame content.
************************************************************************************
"""
import tkinter
import tkinter.ttk
from tkinter import messagebox

from util import CalcalExceptions

from . import CallTypWindow
from . import FrameBaseCalcAl
from . import TableTreeView
from . import FamilyNameChooser
from . import PortionInfoChooser
from . import EnergyFrame
from . import WaterEnergyFrame

class CalculatorFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, logoFrame,
                 calculatorFrameModel,
                 patientFrameModel):
        """ Initialize welcome Frame """
        super(CalculatorFrame, self).__init__(master, mainWindow, logoFrame)
        self.calculatorFrameModel = calculatorFrameModel
        self.calculatorFrameModel.addObserver(self)
        self.patientFrameModel = patientFrameModel
        self.formatFloatValue = "{0:." + self.configApp.get('Limits', 'nbMaxDigit') + "f}"
        self.bgLabelFC = self.configApp.get('Colors', 'colorLabelTableFood')
        self.bgLabelComp = self.configApp.get('Colors', 'colorComponantTableFood')
        self.bgValueComp = self.configApp.get('Colors', 'colorComponantValueTableFood')

        # List of tupple (code,shortcut,unit) for each existing components
        # Used to convert shortcuts to its unique code
        self.listComponents = []
        self.emptyComponents = []

        upperFrame = tkinter.Frame(self)
        upperFrame.pack(side=tkinter.TOP, fill=tkinter.X)
        middleFrame = tkinter.Frame(self)
        middleFrame.pack(side=tkinter.TOP, fill=tkinter.X)

        if self.mainWindow.isBigScreen():
            buttonSelectionFrame = tkinter.LabelFrame(self, text=_("Actions on selection"))
            buttonSelectionFrame.pack(side=tkinter.TOP)
        bottomFrame = tkinter.Frame(self)
        bottomFrame.pack(side=tkinter.TOP, fill=tkinter.X)

        upperLeftFrame = tkinter.LabelFrame(upperFrame, text=_("Search food"))
        upperLeftFrame.pack(side=tkinter.LEFT, padx=5)
        upperMiddleFrame = tkinter.Frame(upperFrame)
        upperMiddleFrame.pack(side=tkinter.LEFT, padx=5)
        foodstuffFrame = tkinter.LabelFrame(upperMiddleFrame, text=_("Foodstuff definition"))
        foodstuffFrame.pack(side=tkinter.TOP)
        upperRightFrame = tkinter.LabelFrame(upperFrame, text=_("Interesting components"))
        upperRightFrame.pack(side=tkinter.LEFT, padx=5)

        # SearchFoodByNameFrame
        upperLeftFrameUp = tkinter.Frame(upperLeftFrame)
        upperLeftFrameUp.pack(side=tkinter.TOP, fill=tkinter.BOTH)
        tkinter.Label(upperLeftFrameUp, text=_("Name") +  " :").pack(side=tkinter.LEFT)
        self.nameToSearch = tkinter.StringVar()
        self.nameToSearch.trace_variable("w", self.validateNameToSearchEntry)
        self.nameToSearchEntry = tkinter.Entry(upperLeftFrameUp, textvariable=self.nameToSearch,
                                               width=35)
        self.nameToSearchEntry.pack(side=tkinter.LEFT)
        CallTypWindow.createToolTip(self.nameToSearchEntry,
                  _("Use Wildcards :\n* replaces n chars\n? replaces 1 only")+"\n"+\
                  _("Ex.:fr*s -> fruits, frais,...")+"\n"+\
                  _("Use ? for character letters like é, â, ô..."),
                                    self.delaymsTooltips * 2)

        listNamesFrame = tkinter.Frame(upperLeftFrame)
        listNamesFrame.pack(side=tkinter.TOP, padx=5, pady=5)
        CallTypWindow.createToolTip(listNamesFrame,
                                    _("Click on food name to copy it in definition frame"),
                                    self.delaymsTooltips)
        heigthFoundNamesListbox = 7
        if self.mainWindow.isTinyScreen():
            heigthFoundNamesListbox = 5
        self.foundNamesListbox = tkinter.Listbox(listNamesFrame,
                                                 height=heigthFoundNamesListbox, width=40)
        self.foundNamesListbox.grid(row=0, columnspan=2)
        scrollbarNameRight = tkinter.Scrollbar(listNamesFrame, orient=tkinter.VERTICAL,
                                               command=self.foundNamesListbox.yview)
        scrollbarNameRight.grid(row=0, column=2, sticky=tkinter.W+tkinter.N+tkinter.S)
        self.foundNamesListbox.config(yscrollcommand=scrollbarNameRight.set)
        self.foundNamesListbox.bind('<ButtonRelease-1>', self.clicNamesListbox)


        # Foodstuff selection frame by family and name
        tkinter.Label(foodstuffFrame, text=_("Family")).grid(row=0, column=0, sticky=tkinter.E)
        self.familyFoodstuffCombobox = tkinter.ttk.Combobox(foodstuffFrame, exportselection=0,
                                                            state="readonly", width=30)
        self.familyFoodstuffCombobox.bind('<<ComboboxSelected>>', self.updatefoodstuffName)
        self.familyFoodstuffCombobox.grid(row=0, column=1, sticky=tkinter.W)

        tkinter.Label(foodstuffFrame, text=_("Name")).grid(row=1, column=0, sticky=tkinter.E)
        self.foodstuffNameCombobox = tkinter.ttk.Combobox(foodstuffFrame, exportselection=0,
                                                          state="readonly", width=30)
        self.foodstuffNameCombobox.grid(row=1, column=1, sticky=tkinter.W)

        tkinter.Label(foodstuffFrame, text=_("Quantity (g)")).grid(row=2, column=0,
                                                                   sticky=tkinter.E)
        self.foodstuffQuantity = tkinter.StringVar()
        self.foodstuffQuantityEntry = tkinter.Entry(foodstuffFrame,
                                                    textvariable=self.foodstuffQuantity,
                                                    width=10)
        self.foodstuffQuantityEntry.grid(row=2, column=1, sticky=tkinter.W)
        self.foodstuffQuantityEntry.bind('<Return>', self.addFoodInTable)
        self.foodstuffQuantityEntry.bind('<KP_Enter>', self.addFoodInTable)

        # Button to put defined food in table
        imageName = 'arrowDown'
        if self.mainWindow.isTinyScreen():
            imageName = None
        addFoodButton = self.mainWindow.createButtonImage(upperMiddleFrame,
                                                          imageRessourceName=imageName,
                                                          text4Image=_("Put in the list"))
        addFoodButton.configure(command=self.addFoodInTable)
        addFoodButton.pack(side=tkinter.LEFT, padx=5, pady=5)

        # Combo to choose number of day for all food displayed
        tkinter.Label(upperMiddleFrame,
                      text=_("Portion duration (days)") + " :").pack(side=tkinter.LEFT)
        maxNbDays2Eat = int(self.configApp.get('Limits', 'maxNbDays2Eat'))
        self.nbDaysCombobox = tkinter.ttk.Combobox(upperMiddleFrame, exportselection=0,
                                       state="readonly", width=len(str(maxNbDays2Eat)),
                                       values=list(range(1, maxNbDays2Eat+1)))
        self.nbDaysCombobox.bind('<<ComboboxSelected>>', self.updateNbDays)
        self.nbDaysCombobox.pack(side=tkinter.LEFT)

        # Componants frame
        color = self.configApp.get('Colors', 'componentsListboxColor')
        # exportselection = False :
        # else lost of selection when user selects text in an other Entry component
        # selection in listbox is used in update method to display selected components
        heightComponentsListbox = 10
        if self.mainWindow.isTinyScreen():
            heightComponentsListbox = 7
        self.componentsListbox = tkinter.Listbox(upperRightFrame, selectmode=tkinter.EXTENDED,
                                         background=color, height=heightComponentsListbox, width=18,
                                         exportselection=False)
        self.componentsListbox.grid(row=0, columnspan=2)
        CallTypWindow.createToolTip(self.componentsListbox,
                                    _("Use Ctrl and Shift keys") + "\n" + \
                                    _("for multiple selection"),
                                    self.delaymsTooltips)
        scrollbarRight = tkinter.Scrollbar(upperRightFrame, orient=tkinter.VERTICAL,
                                   command=self.componentsListbox.yview)
        scrollbarRight.grid(row=0, column=2, sticky=tkinter.W+tkinter.N+tkinter.S)
        self.componentsListbox.config(yscrollcommand=scrollbarRight.set)
        self.componentsListbox.bind('<ButtonRelease-1>', self.clicComponentsListbox)

        # Table for foods and their components
        mealFrame = tkinter.LabelFrame(middleFrame, text=_("List of food"))
        mealFrame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.YES, padx=5, pady=2)
        mealFrame.grid_rowconfigure(0, weight=1)
        mealFrame.grid_columnconfigure(0, weight=1)
        firstColumns = [_("Name"), _("Qty (g)")]
        self.foodTable = TableTreeView.TableTreeView(mealFrame, firstColumns,
                                int(self.configApp.get('Size', 'foodTableNumberVisibleRows')),
                                int(self.configApp.get('Size', 'foodTableFistColWidth')),
                                int(self.configApp.get('Size', 'foodTableOtherColWidth')),
                                int(self.configApp.get('Size', 'foodTableColMinWdth')),
                                selectmode=tkinter.EXTENDED)
        self.foodTable.setColor('normalRow', self.bgValueComp)
        self.foodTable.setColor('totalRow', self.bgLabelFC)
        self.foodTable.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.YES)
        self.foodTable.setBinding('<Double-Button-1>', self.copySelectionInDefinitionFrame)
        self.foodTable.setBinding('<Command-c>', self.copyInClipboard)
        self.foodTable.setBinding('<Control-c>', self.copyInClipboard)
        CallTypWindow.createToolTip(self.foodTable,
                                    _("Use Ctrl and Shift keys") + " " + \
                                    _("for multiple selection") + "\n" + \
                                    _("Clic on header :") + "\n" + \
                                    _("- of 1st column to select or unselect all") + "\n" + \
                                    _("- of other column to sort rows")+ "\n" + \
                                    _("Ctrl-C to put in clipboard")+ "\n" + \
                                    _("Double-clic to modify"),
                                    2 * self.delaymsTooltips)

        # Buttons for action on selection or whole array
        if self.mainWindow.isBigScreen():
            modifySelection = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                               imageRessourceName='arrowUp',
                                               text4Image=_("Modify"))
            modifySelection.configure(command=self.copySelectionInDefinitionFrame)
            modifySelection.pack(side=tkinter.LEFT)
            groupSelectionButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                 imageRessourceName='groupSelection',
                                                 text4Image=_("Group")+"...")

            groupSelectionButton.configure(command=self.groupFood)
            groupSelectionButton.pack(side=tkinter.LEFT)
            ungroupSelectionButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                     imageRessourceName='ungroupSelection',
                                                     text4Image=_("Ungroup"))
            ungroupSelectionButton.configure(command=self.ungroupFood)
            ungroupSelectionButton.pack(side=tkinter.LEFT)

            eraseFoodButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                     imageRessourceName='eraseSelection',
                                                     text4Image=_("Erase line"))
            eraseFoodButton.configure(command=lambda inBd=False: self.deleteFood(inBd))
            eraseFoodButton.pack(side=tkinter.LEFT)

            deleteFoodButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                  imageRessourceName='deleteSelection',
                                                  text4Image=_("Delete in database"))
            deleteFoodButton.configure(command=lambda inBd=True: self.deleteFood(inBd))
            deleteFoodButton.pack(side=tkinter.LEFT)

            copyInClipboardFoodButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                        imageRessourceName='copy2clipboard',
                                                        text4Image=_("Clipboard"))
            copyInClipboardFoodButton.configure(command=self.copyInClipboard)
            copyInClipboardFoodButton.pack(side=tkinter.LEFT)

            infoFoodButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                              imageRessourceName='info',
                                                              text4Image=_("Info"+"..."))
            infoFoodButton.configure(command=self.infoFood)
            infoFoodButton.pack(side=tkinter.LEFT)

            savePortionButton = self.mainWindow.createButtonImage(buttonSelectionFrame,
                                                   imageRessourceName='savePortion',
                                                   text4Image=_("Save portion") + "...")
            savePortionButton.configure(command=self.savePortion)
            savePortionButton.pack(side=tkinter.LEFT)

        # Energy table
        EnergyFrame.EnergyFrame(bottomFrame, self.mainWindow,
                                self.calculatorFrameModel,
                                self.configApp).pack(side=tkinter.LEFT)

        # Water frame
        WaterEnergyFrame.WaterEnergyFrame(bottomFrame, self.mainWindow,
                                          self.calculatorFrameModel,
                                          self.configApp).pack(side=tkinter.LEFT, padx=5, pady=5)

    def updateObserver(self, observable, event):
        """Called when the model object is modified. """
        if observable == self.calculatorFrameModel:
            self.logger.debug("CalculatorFrame received from its model : " + event)
            try:
                if event == "INIT_DB":
                    self.init(initDb=True)
                elif event == "CHANGE_FOOD":
                    self.changeFood()
                elif event == "CHANGE_COMPONENTS":
                    self.changeComponents()
                elif event == "DELETE_FOOD":
                    self.changeDeleteFood(updateList=True)
                elif event == "ERASE_FOOD":
                    self.changeDeleteFood(updateList=False)
                elif event == "GROUP_FOOD":
                    self.changeGroupFood()
                elif event == "UNGROUP_FOOD":
                    self.changeUngroupFood()
                elif event == "SAVE_PORTION":
                    self.changeSavePortion()
                elif event == "DISPLAY_PORTION":
                    self.changeDisplayPortion()
                elif event == "CHANGE_NB_DAYS":
                    self.changeNbDays()
                elif event == "CHANGE_NB_DAYS_BY_MODEL":
                    self.changeNbDaysByModel()
                elif event == "CHANGE_SELECTED_COMPONENTS":
                    self.changeSelectedComponent()

            except CalcalExceptions.CalcalValueError as exc:
                message = _("Error") + " : " + str(exc) + " !"
                self.mainWindow.setStatusText(message, True)

    def init(self, initDb=False):
        """Initialyse calculator"""
        self.logger.debug("CalculatorFrame : init(initDb=" + str(initDb) + ")")

        if initDb:
            # Update components list
            self.foodTable.deleteAllRows()
            self.componentsListbox.delete(0, tkinter.END)
            self.listComponents = self.calculatorFrameModel.getListComponents()
            for component in self.listComponents:
                self.componentsListbox.insert(tkinter.END, component[1] + ' (' + component[2] + ')')

            # Update familyFoodstuffCombobox
            self.updateFamilyFoodstuffCombobox()

        # Empty entry fields and tables
        self.nameToSearch.set("")
        self.validateNameToSearchEntry()
        self.familyFoodstuffCombobox.set("")
        self.foodstuffNameCombobox.set("")
        self.foodstuffQuantity.set("")
        self.nbDaysCombobox.current(0)

        self.componentsListbox.selection_clear(0, tkinter.END)
        self.foodTable.updateVariablesColumns([], [])

        # Limit width size of main window
        self.mainWindow.maxsize(int(self.mainWindow.winfo_width()),
                                int(self.mainWindow.winfo_screenheight()))

    def updateFamilyFoodstuffCombobox(self):
        """ Update FamilyFoodstuffCombobox with database """
        database = self.databaseManager.getDatabase()
        listFamilyFoodstuff = database.getListFamilyFoodstuff()
        assert (len(listFamilyFoodstuff) > 0), \
                "CalculatorFrame/init() : no family in database !"
        self.familyFoodstuffCombobox['values'] = listFamilyFoodstuff
        self.familyFoodstuffCombobox.current(0)

    def changeFood(self):
        """ Change a line in foodtable """
        self.logger.debug("CalculatorFrame : changeFood()")

        self.deleteTotalLines()

        # Update modified food lines
        for foodName, quantity, dictComponents \
            in self.calculatorFrameModel.getListFoodModifiedInTable():
            columnsValues = [quantity] + self.getColumnValues(dictComponents)
            self.foodTable.insertOrCreateRow(foodName, columnsValues)

        # Update total line
        self.updateTotalLines()

        self.mainWindow.setStatusText(_("Foodstuff") + " " + _("added"))

    def deleteTotalLines(self):
        """ Deletes all totallines in food table """
        self.foodTable.deleteRow(_("Total"))
        self.foodTable.deleteRow(_("Total") + " " + _("per day"))

    def updateTotalLines(self):
        """ Update total line according to model content and self.nbDaysCombobox """
        totalName, quantity, dictComponents = self.calculatorFrameModel.getTotalLineStr()
        columnsValues = [quantity] + self.getColumnValues(dictComponents)
        self.foodTable.insertOrCreateRow(totalName, columnsValues, tag='totalRow')

        nbDays = int(self.nbDaysCombobox.get())
        if nbDays > 1:
            totalName, quantity, dictComponents = self.calculatorFrameModel.getTotalLineStr(nbDays)
            columnsValues = [quantity] + self.getColumnValues(dictComponents)
            self.foodTable.insertOrCreateRow(totalName, columnsValues, tag='totalRow')

    def changeComponents(self):
        """ Change components columns in foodtable """
        self.logger.debug("CalculatorFrame : changeComponents()")

        self.deleteTotalLines()

        # Prepare list of components to be inserted
        # with respect of food and components order
        dictTable = self.calculatorFrameModel.getFullTable()
        listFoodname = self.foodTable.getKeyNames()
        listColumnsValues = []
        for foodname in listFoodname:
            dictComponents = dictTable[foodname][2]
            columnsValues = self.getColumnValues(dictComponents)
            listColumnsValues.append(columnsValues)

        # Update list of displayed components
        listUserComponentTitle = [self.listComponents[index][1] + " (" +
                                  self.listComponents[index][2] + ")"
                                  for index in self.componentsListbox.curselection()]

        self.foodTable.updateVariablesColumns(listUserComponentTitle, listColumnsValues)

        # Create new total line
        if self.calculatorFrameModel.getNumberOfFoodStuff() > 0:
            self.updateTotalLines()

        self.mainWindow.setStatusText(str(len(listUserComponentTitle)) + " " +
                                      _("Components displayed"))

    def changeDeleteFood(self, updateList):
        """ Delete foodstuffs in foodtable
            V0.43 : if updateList, update definition combobox Family and name """
        self.logger.debug("CalculatorFrame : changeDeleteFood()")

        self.deleteTotalLines()

        listFoodname = self.calculatorFrameModel.getListDeletedFoodnames()
        for foodname in listFoodname:
            self.foodTable.deleteRow(foodname)

        # Create new total line
        if self.calculatorFrameModel.getNumberOfFoodStuff() > 0:
            self.updateTotalLines()

        # V0.43 : if updateList, update definition combobox Family and name
        if updateList:
            self.updateFamilyFoodstuffCombobox()
            self.updatefoodstuffName()

        if len(listFoodname) < 2:
            foodstuff = _("foodstuff")
        else:
            foodstuff = _("foodstuffs")
        message = str(len(listFoodname)) + " " + foodstuff + " " + _("removed from above table")
        self.mainWindow.setStatusText(message)

    def getColumnValues(self, dictComponents):
        """ return a list [quantity, ordered components] according self.dictSelectedComponents
            components are asked by user in list of components """
        listUserComponentCode = [self.listComponents[index][0]
                                 for index in self.componentsListbox.curselection()]
        columnsValues = [dictComponents[componentCode]
                         for componentCode in listUserComponentCode]
        self.logger.debug("CalculatorFrame/getColumnValues() : columnsValues = " +
                          str(columnsValues))
        return columnsValues

    def changeGroupFood(self):
        """ Called by the model when a group is created """
        self.logger.debug("CalculatorFrame : changeGroupFood()")

        self.deleteTotalLines()

        productName = self.calculatorFrameModel.getListDeletedFoodnames()[0]
        familyName = self.calculatorFrameModel.getGroupedFamilyFoodname()

        # Update family listbox by asking
        listFamily = list(self.familyFoodstuffCombobox['values'])
        if familyName not in listFamily:
            listFamily.append(familyName)
            self.familyFoodstuffCombobox['values'] = listFamily

        # Create new total line
        self.updateTotalLines()

        self.mainWindow.setStatusText(_("New product") + " " + productName + " " +
                                      _("saved in database"))

    def changeUngroupFood(self):
        """ Called by the model when a food is ungrouped """
        self.logger.debug("CalculatorFrame : changeUngroupFood()")
        self.deleteTotalLines()

        # Delete ungrouped food in table
        foodNameUngrouped = self.calculatorFrameModel.getListDeletedFoodnames()[0]
        self.foodTable.deleteRow(foodNameUngrouped)

        # Add or update ungrouped parts
        for foodName, quantity, dictComponents in self.calculatorFrameModel.getListFoodModifiedInTable():
            columnsValues = [quantity] + self.getColumnValues(dictComponents)
            self.foodTable.insertOrCreateRow(foodName, columnsValues)

        # Create new total line
        self.updateTotalLines()

        self.mainWindow.setStatusText(_("Composed product") + " " + foodNameUngrouped + " " +
                                      _("ungrouped"))

    def changeSavePortion(self):
        """ Called by the model when a portion is saved """
        self.logger.debug("CalculatorFrame : changeSavePortion()")

        # Activate Portion pane
        self.mainWindow.enableTabPortion(True)
        self.mainWindow.setStatusText(_("Portion saved in database"))

    def changeDisplayPortion(self):
        """ Called by the model when a portion must be displayed """
        self.logger.debug("CalculatorFrame : changeDisplayPortion()")

        # Erase food table
        self.foodTable.deleteAllRows()

        # Erase components to speed operation
        self.componentsListbox.selection_clear(0, tkinter.END)
        self.foodTable.updateVariablesColumns([], [])

        # Update modified food lines
        tableContent = []
        for foodName, quantity, dictComponents in self.calculatorFrameModel.getListFoodModifiedInTable():
            tableContent.append([foodName, [quantity] + self.getColumnValues(dictComponents)])
        self.foodTable.insertGroupRow(tableContent)

        # Create new total line
        self.updateTotalLines()

        self.mainWindow.enableTabCalculator(True)
        self.mainWindow.setStatusText(_("Selected portion added in calculator"))

    def changeSelectedComponent(self):
        """ Model asks to change selected components in components Listbox """
        # Ask to model what components to select
        listComponentsCodes = self.calculatorFrameModel.getAskedByUserCodes()
        # Select componenents
        self.componentsListbox.selection_clear(0, tkinter.END)
        firstIndex = True
        for code in listComponentsCodes:
            index = 0
            for component in self.listComponents:
                if code == component[0]:
                    self.componentsListbox.selection_set(index)
                    if firstIndex:
                        self.componentsListbox.see(index)
                        firstIndex = False
                    break
                index += 1
        self.changeComponents()
        self.mainWindow.setStatusText(_("Components selected"))


    def validateNameToSearchEntry(self, *args):
        """ File self.foundNamesListbox with products that match nameToSearchEntry content"""
        foodNamePart = self.nameToSearch.get()

        # Search in database product containing foodNamePart
        if len(foodNamePart) > 0:
            database = self.databaseManager.getDatabase()
            assert (database is not None), \
                    "CalculatorFrame/validateNameToSearchEntry() : no open database !"
            listFoodName = database.getProductsNamesContainingPart(foodNamePart)
            # Update self.foundNamesListbox with results
            self.foundNamesListbox.delete(0, tkinter.END)
            for name in listFoodName:
                self.foundNamesListbox.insert(tkinter.END, name)
        else:
            self.foundNamesListbox.delete(0, tkinter.END)

    def updateNbDays(self, *args):
        """ User changes nb days to eat portion """
        nbDays = int(self.nbDaysCombobox.get())
        self.calculatorFrameModel.updateNbDays(nbDays)

    def changeNbDays(self):
        """ Called if an event said that user has changed nbDays Combo """
        self.deleteTotalLines()
        self.updateTotalLines()

        # Make updated totalLine visible
        nbDays = int(self.nbDaysCombobox.get())
        name = _("Total")
        if nbDays > 1:
            name = _("Total") + " " + _("per day")
        self.foodTable.see(name)

    def changeNbDaysByModel(self):
        """ V 0.41 : Called if an event said that model asked to change nbDays Combo value """
        nbDays = self.calculatorFrameModel.getNbDays()

        # Test if nbDays stored in database can be displayed and adapt combobox values
        if nbDays > max([int(val) for val in self.nbDaysCombobox['values']]):
            self.nbDaysCombobox['width'] = len(str(nbDays))
            self.nbDaysCombobox['values'] = list(range(1, nbDays+1))

        self.nbDaysCombobox.set(nbDays)

    def updatefoodstuffName(self, *args):
        """ Update foodstuff list name """
        database = self.databaseManager.getDatabase()
        assert (database is not None), "CalculatorFrame/updatefoodstuffName() : no open database !"
        familyname = self.familyFoodstuffCombobox.get()

        listFoodstuffName = database.getListFoodstuffName(familyname)
        assert (listFoodstuffName is not None), \
            "CalculatorFrame/init() : no food name for family " + familyname + " in database  !"
        self.foodstuffNameCombobox['values'] = listFoodstuffName
        self.foodstuffNameCombobox.current(0)

    def clicNamesListbox(self, evt=None):
        """ Update food definition with new components chosen """
        # Get selection
        selectedNames = list(self.foundNamesListbox.curselection())
        if len(selectedNames) > 0:
            foodName = self.foundNamesListbox.get(selectedNames[0])

            # Update foodstuffFrame comboboxes
            self.updateFoodstuffFrame(foodName)

    def clicComponentsListbox(self, evt=None):
        """ Update model with new components chosen """
        listUserComponentCode = set([self.listComponents[index][0]
                                     for index in self.componentsListbox.curselection()])

        # Send users choosen codeComponents to model
        self.calculatorFrameModel.updateFollowedComponents(listUserComponentCode)

    def addFoodInTable(self, event=None):
        """ Called when hitting Retun key in foodstuffQuantity entry """
        # Check User's input data
        foodName = self.foodstuffNameCombobox.get()
        quantity = self.foodstuffQuantity.get()
        try:
            self.calculatorFrameModel.addFoodInTable([[foodName, quantity]])
        except CalcalExceptions.CalcalValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def groupFood(self):
        """ Group and Save foodstuffs that are selected by user in Database """
        listFoodName2Group = self.foodTable.getKeyNames(excludeRowWithTitle=_("Total"),
                                                        onlySelected=True)
        try:
            if len(listFoodName2Group) < 2:
                raise ValueError(_("Please select more than one foodstuff in food table"))

            # Ask new name and family for this new product
            database = self.databaseManager.getDatabase()
            dialog = FamilyNameChooser.FamilyNameChooser(self, database, self.configApp,
                                                         title=_("Save group in database"))
            results = dialog.getResult()
            if results is None:
                raise ValueError(_("Group recording canceled"))

            # Insert new produt in database
            familyName = results[0]
            productName = results[1]

            # Ask to the model to group selected foods
            self.calculatorFrameModel.groupFood(familyName, productName, listFoodName2Group)

        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def ungroupFood(self):
        """ Ungroup foodstuff selected by user
            v0.30 : Sum ungrouped quantities to existing rows that contain the same food """
        listSelectedFoodName = self.foodTable.getKeyNames(excludeRowWithTitle=_("Total"),
                                                          onlySelected=True)
        try:
            if len(listSelectedFoodName) != 1:
                raise ValueError(_("Please select one and only one line in food table"))
            # Ask to the model to group selected foods
            foodname = listSelectedFoodName[0]
            self.calculatorFrameModel.ungroupFood(foodname)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def deleteFood(self, inDatabase):
        """ Ask to model to remove foodstuffs selected by user """
        listSelectedFoodName = self.foodTable.getKeyNames(excludeRowWithTitle=_("Total"),
                                                          onlySelected=True)
        nbSelectedRows = len(listSelectedFoodName)
        try:
            if nbSelectedRows < 1:
                raise ValueError(_("Please select at least one line in food table"))
            if inDatabase and nbSelectedRows != 1:
                raise ValueError(_("Please select one and only one line in food table"))
            isDestructionOk = True
            if inDatabase:
                isDestructionOk = messagebox.askyesno(
                                    _("Deleting selected user element in database"),
                                    _("Do you really want to delete selection in database ?") + \
                                    "\n" + listSelectedFoodName[0],
                                    icon='warning')
            if isDestructionOk:
                self.calculatorFrameModel.deleteFoodInModel(listSelectedFoodName, inDatabase)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def copySelectionInDefinitionFrame(self, event=None):
        """ Copy name and quatity of first element selected in foodTable
            to meal definition frame """
        try:
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

    def infoFood(self, event=None):
        "v0.30 : 22-23/8/2016 : Display information on selected food"
        maxNameLengthInPopup = int(self.configApp.get("Limits", "maxNameLengthInPopup"))
        listSelectedRows = self.foodTable.getSelectedItems(excludeRowWithTitle=_("Total"))
        try:
            if len(listSelectedRows) != 1:
                raise ValueError(_("Please select one and only one line in food table"))
            foodName = self.foodTable.getTextForItemIndex(listSelectedRows[0])
            database = self.databaseManager.getDatabase()
            assert (database is not None), "CalculatorFrame/infoFood() : no open database !"
            dictInfoFood = database.getInfoFood(foodName)

            # Format information
            title = _("Info") + " "
            if dictInfoFood["isGroup"]:
                title += _("about foodstuff group")
            else:
                title += _("about foodstuff")
            tooLongName = ""
            if len(dictInfoFood["name"]) > maxNameLengthInPopup:
                tooLongName = "..."
            title += " " + dictInfoFood["name"][:maxNameLengthInPopup] + tooLongName
            message = ""
            if dictInfoFood["isGroup"]:
                message += _("Foodstuff group")
            else:
                message += _("Foodstuff")
            message += " : " + dictInfoFood["name"] + "\n" + \
                    _("Code") + " : " + str(dictInfoFood["code"]) + "\n" + \
                    _("Family") + " : " + dictInfoFood["familyName"] + "\n" + \
                    _("Input Date") + " : " + dictInfoFood["dateSource"] + "\n" + \
                    _("Number of constituants") + " : " + str(dictInfoFood["nbConstituants"])

            if dictInfoFood["isGroup"]:
                message += "\n\n" + _("Group details") + " :\n" + \
                           _("Number of items") + " : " + str(dictInfoFood["nbGroupsMembers"])
                for dictGroup in dictInfoFood["groups"]:
                    tooLongName = ""
                    if len(dictGroup["namePart"]) > maxNameLengthInPopup:
                        tooLongName = "..."
                    message += "\n- " +  dictGroup["namePart"][:maxNameLengthInPopup] + \
                            tooLongName + "\n\t" + \
                            str(dictGroup["percentPart"]) + " %"
            else:
                message += "\n" + \
                            _("Source") + " : " + dictInfoFood["source"] + "\n" + \
                            _("URL") + " : " + dictInfoFood["urlSource"]

            # Display information's on this Foodstuff in a standard dialog
            messagebox.showinfo(title=title, message=message)
            self.mainWindow.copyInClipboard(message)

        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def savePortion(self):
        """ Save Portion in Database """
        try:
            if self.calculatorFrameModel.getNumberOfFoodStuff() < 1:
                raise ValueError(_("No food to save"))
            # Ask information to qualify this portion
            database = self.databaseManager.getDatabase()
            dialog = PortionInfoChooser.PortionInfoChooser(self, database, self.configApp,
                                                           title=_("Save portion in database"))
            results = dialog.getResult()
            if results is None:
                raise ValueError(_("Portion recording canceled"))

            # Ask model to insert new portion in database
            self.calculatorFrameModel.savePortion(results)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def updateFoodstuffFrame(self, foodName):
        """Update familyFoodstuffCombobox and foodstuffNameCombobox in foodstuffFrame """
        database = self.databaseManager.getDatabase()
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

    def getPatientFrameModel(self):
        """ Return calculator frame model """
        return self.patientFrameModel
