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

from gui import FrameBaseCalcAl
from gui import Table
from database import Database

class CalculatorFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, ressourcePath, logoFrame):
        """ Initialize welcome Frame """
        super(CalculatorFrame, self).__init__(master, mainWindow, ressourcePath, logoFrame)

        self.mainWindow = mainWindow
        # List of tupple (code,shortcut,unit) for each existing components
        # Used to convert shortcuts to its unique code
        self.listComponents = []
        self.selectedComponents = []

        upperFrame = Frame(self)
        upperFrame.pack(side=TOP)
        middleFrame = Frame(self)
        middleFrame.pack(side=TOP)

        upperLeftFrame = Frame(upperFrame)
        upperLeftFrame.pack(side=LEFT, padx=5, pady=5, fill=X)
        upperRightFrame = LabelFrame(upperFrame, text=_("Interesting components"))
        upperRightFrame.pack(side=LEFT, padx=5, pady=5)

        # Foodstuff frame
        foodstuffFrame = LabelFrame(upperLeftFrame, text=_("Foodstuff definition"))
        foodstuffFrame.pack(side=TOP, fill=X, padx=5, pady=5)

        Label(foodstuffFrame, text=_("Family")).pack(side=TOP, fill=X)
        self.familyFoodstuffCombobox = Combobox(foodstuffFrame, exportselection=0,
                                                state="readonly")
        self.familyFoodstuffCombobox.bind('<<ComboboxSelected>>', self.updatefoodstuffName)
        self.familyFoodstuffCombobox.pack(side=TOP, fill=X)

        Label(foodstuffFrame, text=_("Name")).pack(side=TOP, fill=X)
        self.foodstuffNameCombobox = Combobox(foodstuffFrame, exportselection=0,
                                      state="readonly")
        self.foodstuffNameCombobox.pack(side=TOP, fill=X)

        Label(foodstuffFrame, text=_("Quantity (g)")).pack(side=TOP, fill=X)
        self.foodstuffQuantity = StringVar()
        self.foodstuffQuantityEntry = Entry(foodstuffFrame, textvariable=self.foodstuffQuantity)
        self.foodstuffQuantityEntry.pack(side=TOP, fill=X)

        # buttonMealFrame
        buttonMealFrame = Frame(upperLeftFrame)
        buttonMealFrame.pack(side=TOP, padx=5, pady=5)
        self.AddFoodButton = Button(buttonMealFrame, text=_("Add this foodstuff"),
                                    command=self.addFoodInTable)
        self.AddFoodButton.pack(side=LEFT)
        self.DeleteFoodButton = Button(buttonMealFrame, text=_("Delete empty foodstuff"),
                                       command=self.deleteFood)
        self.DeleteFoodButton.pack(side=LEFT)

        # Componants frame
        color = self.configApp.get('Colors', 'componentsListboxColor')
        self.componentsListbox = Listbox(upperRightFrame, selectmode=EXTENDED,
                                         background=color, height=10)
        self.componentsListbox.grid(row=0, columnspan=2)
        scrollbarRight = Scrollbar(upperRightFrame, orient=VERTICAL,
                                   command=self.componentsListbox.yview)
        scrollbarRight.grid(row=0, column=2, sticky='wns')
        self.componentsListbox.config(yscrollcommand=scrollbarRight.set)
        self.componentsListbox.bind('<ButtonRelease-1>', self.clicComponentsListbox)

        # Table for foods and their components
        mealFrame = LabelFrame(middleFrame, text=_("List of food"))
        mealFrame.pack(side=LEFT, padx=5, pady=5)
        self.foodTable = Table.Table(middleFrame, _("Name"), _("Qty (g)"),
                                     int(self.configApp.get('Limits', 'nbMaxSelectedComponents')),
                                     int(self.configApp.get('Limits', 'nbMaxDigit')),
                                     self.configApp.get('Colors', 'colorLabelTableFood'),
                                     self.configApp.get('Colors', 'colorComponantTableFood'))
        self.foodTable.pack(side=TOP, fill=X)
        numRow = self.foodTable.appendNewRow()
        self.foodTable.modifyRow(numRow, _("Total"), '0',
                                 self.configApp.get('Colors', 'colorLabelTableFood'),
                                 self.configApp.get('Colors', 'colorComponantTableFood'))

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

    def updatefoodstuffName(self, *args):
        """ Update foodstuff list name """
        database = self.mainWindow.getDatabase()
        assert (database is not None), "CalculatorFrame/init() : no open database !"
        familyname = self.familyFoodstuffCombobox.get()

        listFoodstuffName = database.getListeFoodstuffName(familyname)
        assert (listFoodstuffName is not None), \
            "CalculatorFrame/init() : no food name for family " + familyname + " in database  !"
        self.foodstuffNameCombobox['values'] = listFoodstuffName
        self.foodstuffNameCombobox.current(0)

    def clicComponentsListbox(self, evt):
        """ Update Product list with new components chosen """
        try:
            self.selectedComponents = list(self.componentsListbox.curselection())
            nbMaxSelectedComponents = int(self.configApp.get('Limits', 'nbMaxSelectedComponents'))
            if len(self.selectedComponents) > nbMaxSelectedComponents :
                raise ValueError(_("Too many components selected") + " : " +
                                 str(len(self.selectedComponents)) + " (" + _("maximum") + " " +
                                 str(nbMaxSelectedComponents) + ")")

            # Display title in foodTable for self.selectedComponents
            selectedComponentsName = [self.componentsListbox.get(index)
                                      for index in self.selectedComponents]
            self.foodTable.modifyRow(0, _("Name"), _("Qty (g)"),
                                     self.configApp.get('Colors', 'colorLabelTableFood'),
                                     self.configApp.get('Colors', 'colorComponantTableFood'),
                                     selectedComponentsName)

            # Update existing food rows
            database = self.mainWindow.getDatabase()
            listComponentsCodes = [self.listComponents[numSelectedComponent][0]
                                   for numSelectedComponent in self.selectedComponents]
            listFoodName = self.foodTable.getColumnsValuesText(0, withFirstRow=False,
                                                               withLastRow=False)
            for foodName in listFoodName:
                numRow = self.foodTable.getRowForText(foodName, 0,
                                                      withFirstRow=False,
                                                      withLastRow=False)
                assert (numRow != -1), "CalculatorFrame/clicComponentsListbox() : " + foodName +\
                                       " not found in table !"

                quantity = self.foodTable.getCellValueInt(numRow, 1)
                componentsValues = database.getComponentsValues4Food(foodName,
                                                                     quantity,
                                                                     listComponentsCodes)
                self.foodTable.modifyRow(numRow, foodName, quantity,
                                     self.configApp.get('Colors', 'colorNameTableFood'),
                                     self.configApp.get('Colors', 'colorComponantValueTableFood'),
                                     componentsValues)

            # Update total table
            sumQuantities, listSumComponents = self.sumFoodTable(withLastRow=False)
            numRow = self.foodTable.getRowForText(_("Total"), 0,
                                                  withFirstRow=False)
            assert (numRow != -1), "CalculatorFrame/clicComponentsListbox() : Total column not found !"
            self.foodTable.modifyRow(numRow, _("Total"), str(sumQuantities),
                                      self.configApp.get('Colors', 'colorLabelTableFood'),
                                      self.configApp.get('Colors', 'colorComponantTableFood'),
                                      listSumComponents)

        except ValueError as exc:
            self.selectedComponents = []
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def addFoodInTable(self):
        """ Add a foodstuff in table """
        try :
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
            listComponentsCodes = [self.listComponents[numSelectedComponent][0]
                                   for numSelectedComponent in self.selectedComponents]
            database = self.mainWindow.getDatabase()
            componentsValues = database.getComponentsValues4Food(foodName, quantity,
                                                                 listComponentsCodes)

            # Set the number of the row to modify
            # Try to update foodName row
            rowFoundNotFood = True
            numRow = self.foodTable.getRowForText(foodName, 0, withFirstRow=False)
            if numRow == -1 :
                # Replace total line with line for this foodname
                numRow = self.foodTable.getRowForText(_("Total"), 0, withFirstRow=False)
                assert (numRow != -1), "CalculatorFrame/addFoodInTable() : Total column not found !"
            else:
                rowFoundNotFood = False
            # Modify the row
            self.foodTable.modifyRow(numRow, foodName, quantity,
                                     self.configApp.get('Colors', 'colorNameTableFood'),
                                     self.configApp.get('Colors', 'colorComponantValueTableFood'),
                                     componentsValues)

            # Add total line
            sumQuantities, listSumComponents = self.sumFoodTable(withLastRow=rowFoundNotFood)
            if rowFoundNotFood:
                numRow = self.foodTable.appendNewRow()
            else:
                numRow = self.foodTable.getRowForText(_("Total"), 0, withFirstRow=False)
            self.foodTable.modifyRow(numRow, _("Total"), sumQuantities,
                                     self.configApp.get('Colors', 'colorLabelTableFood'),
                                     self.configApp.get('Colors', 'colorComponantTableFood'),
                                     listSumComponents)

            self.mainWindow.setStatusText(_("Foodstuff") + " " + foodName + " " + _("added"))
        except ValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def deleteFood(self):
        """ Delete foodstuffs in table whose quantity are empty """
        print("TODO deleteFood")

    def sumFoodTable(self, withLastRow):
        """ Sum all colomns of foodTable and update totalTable """
        sumQuantities = 0
        qtyValues = self.foodTable.getColumnsValuesInt(1, withFirstRow=False,
                                                       withLastRow=withLastRow)
        for qty in qtyValues:
            sumQuantities = sumQuantities + qty
        listSumComponents = []
        nbColComponents = int(self.configApp.get('Limits', 'nbMaxSelectedComponents'))
        for colComponent in range(2, nbColComponents + 2):
            if self.foodTable.getCellValue(0, colComponent) != '':
                sumComponent = 0
                for qtyComp in self.foodTable.getColumnsValuesFloat(colComponent,
                                                                    withFirstRow=False,
                                                                    withLastRow=withLastRow):
                    sumComponent = sumComponent + qtyComp
                listSumComponents.append(sumComponent)
        return sumQuantities, listSumComponents



