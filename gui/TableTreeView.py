#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    *********************************************************
    Class : Table
    Auteur : Thierry Maillard (TMD)
    Date : 8/5/2016 - 15/10/2016

    Role : Table widget.

    Licence : GPLv3
    Copyright (c) 2016 - Thierry Maillard


    This file is part of CalcAl project.

    CalcAl project is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    CalcAl project is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with CalcAl project.  If not, see <http://www.gnu.org/licenses/>.
    *********************************************************
"""
import locale

import tkinter
import tkinter.ttk

class TableTreeView(tkinter.Frame):
    """ Table widget """
    def __init__(self, master, firstColumnsTitle, nbMinLines,
                 firstColWidth=100, otherColWidth=75, colMinWidth=50,
                 selectmode="none"):
        self.decimalPoint = locale.localeconv()['decimal_point']

        """ Define  a table with labels cells """
        super(TableTreeView, self).__init__(master)
        self.numStableCol = len(firstColumnsTitle) - 1
        self.firstColWidth = firstColWidth
        self.otherColWidth = otherColWidth
        self.colMinWidth = colMinWidth

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create treeview, scrollbars
        self.treeview = tkinter.ttk.Treeview(self, height=nbMinLines, selectmode=selectmode)
        vsb = tkinter.Scrollbar(self, orient=tkinter.VERTICAL, command=self.treeview.yview)
        vsb.grid(row=0, column=1, sticky=(tkinter.N, tkinter.S))
        hsb = tkinter.Scrollbar(self, orient=tkinter.HORIZONTAL, command=self.treeview.xview)
        hsb.grid(row=1, column=0, sticky=(tkinter.E, tkinter.W))
        self.treeview.config(yscrollcommand=vsb.set)
        self.treeview.config(xscrollcommand=hsb.set)
        self.treeview.grid(row=0, sticky=(tkinter.N, tkinter.S, tkinter.W, tkinter.E))
        self.grid_rowconfigure(0, weight=1)

        # Create header line
        # Item key column
        self.treeview.heading("#0", text=firstColumnsTitle[0],
                              command=lambda select=True: self.selectAllOrNothing(select))
        if self.numStableCol > 0:
            self.treeview['columns'] = firstColumnsTitle[1:] # Other columns
            for titleCol in firstColumnsTitle[1:]:
                self.treeview.heading(titleCol, text=titleCol,
                                      command=lambda c=titleCol: self.sortby(c, False))
        else:
            self.treeview['columns'] = []

        # Apply column properties
        self.setColumnsDefaultProperties()

    def setColumnsDefaultProperties(self):
        """ Set Default column properties """
        self.treeview.column("#0", anchor=tkinter.W, width=self.firstColWidth,
                             stretch=False, minwidth=self.colMinWidth)
        for columnName in self.treeview['columns']:
            self.treeview.column(columnName, anchor=tkinter.E, width=self.otherColWidth,
                                 stretch=False, minwidth=self.colMinWidth)

    def searchItem(self, name):
        """ find a name in each item text key and return the corresponding item
            or None if not found """
        foundItem = None
        for rowItem in self.treeview.get_children():
            if self.treeview.item(rowItem, option='text') == name:
                foundItem = rowItem
        return foundItem

    def insertOrCreateRow(self, name, columnsValues, tag='normalRow', seeItem=True):
        """ Modify the values of an existing row or create a new one """
        # Search if item name already exists
        foundItem = self.searchItem(name)
        if foundItem:
            self.treeview.item(foundItem, values=columnsValues)
        else:
            self.treeview.insert('', 'end', text=name, values=columnsValues, tags=(tag,))
        if seeItem:
            self.see(name)

    def see(self, name):
        """ Display on the screen an item whoose key is given in parameter """
        self.treeview.see(self.searchItem(name))

    def insertGroupRow(self, listNameListColumn):
        """ V0.35 For speeding up : insert a group of row """
        for name, columnsValues in listNameListColumn:
            self.treeview.insert('', 'end', text=name, values=columnsValues, tags=('normalRow',))

    def deleteRow(self, name):
        """ Delete a row given its item name """
        foundItem = self.searchItem(name)
        if foundItem:
            self.treeview.delete(foundItem)

    def deleteListItems(self, listItem):
        """ Delete a list of row items """
        for item in listItem:
            self.treeview.delete(item)

    def deleteAllRows(self):
        """ Delete all table rows """
        for rowItem in self.treeview.get_children():
            self.treeview.delete(rowItem)

    def getStableColumnsValues(self, excludeRowWithTitle=None, onlySelected=False):
        """ Return keyNames and stable cols for each rows """
        listSelectedRows = []
        if onlySelected:
            listSelectedRows = self.getSelectedItems(excludeRowWithTitle)
        listValues = []
        for rowItem in self.treeview.get_children():
            if (not excludeRowWithTitle or \
                self.getTextForItemIndex(rowItem) != excludeRowWithTitle) and \
                (not onlySelected or (rowItem in listSelectedRows)):
                valuesRow = [self.treeview.item(rowItem, option='text'),
                             self.treeview.item(rowItem, option='values')[:self.numStableCol]]
                listValues.append(valuesRow)
        return listValues

    def getKeyNames(self, excludeRowWithTitle=None, onlySelected=False):
        """ Return keyNames and stable cols for each rows """
        listSelectedRows = []
        if onlySelected:
            listSelectedRows = self.getSelectedItems(excludeRowWithTitle)
        listValues = []
        for rowItem in self.treeview.get_children():
            if (not excludeRowWithTitle or \
                self.getTextForItemIndex(rowItem) != excludeRowWithTitle) and \
                (not onlySelected or (rowItem in listSelectedRows)):
                listValues.append(self.treeview.item(rowItem, option='text'))
        return listValues

    def getAllColumnsValues(self, excludeRowWithTitle=None):
        """ V0.33 : Return all values for optional columns """
        numberOfColumns = len(self.treeview['columns'])
        listValues = []
        for rowItem in self.treeview.get_children():
            if not excludeRowWithTitle or self.getTextForItemIndex(rowItem) != excludeRowWithTitle:
                valuesRow = self.treeview.item(rowItem, option='values')
                listValues.append(valuesRow)
        return numberOfColumns, listValues

    def getColumnsValues(self):
        """ Return number of columns values and all column values for all rows"""
        listValues = []
        for rowItem in self.treeview.get_children():
            listValues.append(self.treeview.item(rowItem, option='values'))
        return listValues

    def updateVariablesColumns(self, selectedComponentsName, variablesColValues):
        """ Update variable column and their content """
        # Save existing stable colums titles and names
        listTitlesCol = []
        for numCol in range(self.numStableCol):
            listTitlesCol.append(self.treeview.heading(numCol, option='text'))
        listNamesCol = list(self.treeview['columns'][:self.numStableCol])

        # Add new variable column titles and names
        listTitlesCol = listTitlesCol + selectedComponentsName
        listNamesCol = listNamesCol + selectedComponentsName
        self.treeview['columns'] = listNamesCol

        # Restore title and sort command for each col
        numCol = 0
        for title in listTitlesCol:
            self.treeview.heading(numCol, text=title)
            self.treeview.heading(numCol, command=lambda col=numCol: self.sortby(col, False))
            numCol = numCol + 1

        # Add value in last colums of each row
        nbRowsInTable = self.treeview.get_children()
        assert nbRowsInTable is None or variablesColValues is None or \
              len(nbRowsInTable) == len(variablesColValues),\
            "Error : " + str(len(nbRowsInTable)) +  " rows in table is different than " + \
            str(len(variablesColValues)) + " rows values to update !"
        numRow = 0
        for rowItem in self.treeview.get_children():
            listRowValues = list(self.treeview.item(rowItem, option='values')[:self.numStableCol])
            if variablesColValues:
                listRowValues = listRowValues + variablesColValues[numRow]
            self.treeview.item(rowItem, values=listRowValues)
            numRow = numRow + 1

        # Set column size
        self.setColumnsDefaultProperties()

    def getSelectedItems(self, excludeRowWithTitle=None):
        """" Return list of index for selected rows """
        listSelectedItem = self.treeview.selection()
        if excludeRowWithTitle:
            for item in listSelectedItem:
                if self.getTextForItemIndex(item) == excludeRowWithTitle:
                    self.treeview.selection_remove((item,))
            listSelectedItem = self.treeview.selection()
        return listSelectedItem

    def getTextForItemIndex(self, item):
        """ Return text for this row item """
        return self.treeview.item(item, option='text')

    def getItemValue(self, item, num):
        """ Return Value number num in row item """
        return self.treeview.item(item, option='values')[num]

    def setColor(self, tag, color):
        """ Set background color for all rows marked with tag """
        self.treeview.tag_configure(tag, background=color)

    def sortby(self, col, descending):
        """sort tree contents when a column header is clicked on
            alphabetically for culumn containing only text, else numerically.
            Only normal rows are sorted """
        # grab values to sort
        data = [(self.treeview.set(child, col), child)
                for child in self.treeview.get_children()
                if 'normalRow' in self.treeview.item(child, option='tags')]
        # if the data to be sorted is numeric change to float
        data = change2Numeric(data)
        # now sort the data in place
        data.sort(reverse=descending)
        for numItemData, item in enumerate(data):
            self.treeview.move(item[1], '', numItemData)
        # switch the heading so it will sort in the opposite direction
        self.treeview.heading(col, command=lambda col=col: self.sortby(col, not descending))

    def selectAllOrNothing(self, selectAll):
        """ Select every or no normal row according parameter """
        for child in self.treeview.get_children():
            if 'normalRow' in self.treeview.item(child, option='tags'):
                if selectAll:
                    self.treeview.selection_add(child)
                else:
                    self.treeview.selection_remove(child)
        selectAll = not selectAll
        self.treeview.heading("#0",
                              command=lambda select=selectAll: self.selectAllOrNothing(select))

    def getTableAsText(self):
        """ Return table selected content in text format """
        textBuffer = ""
        selectedItems = self.getSelectedItems()
        if len(selectedItems) == 0:
            raise ValueError(_("Please select at least one line in table"))
        # Get headers titles
        titleCols = []
        titleCols.append(self.treeview.heading("#0", option='text'))
        for col in self.treeview['columns']:
            titleCols.append(self.treeview.heading(col, option='text'))
        textBuffer = textBuffer + ";".join(titleCols) + "\n"
        # Get selected rows values
        for item in selectedItems:
            cols = [self.treeview.item(item, option='text')] + \
                    list(self.treeview.item(item, option='values'))
            # Format decimal values
            colsValuesFormatted = ";".join(cols)
            if self.decimalPoint != '.':
                colsValuesFormatted = colsValuesFormatted.replace('.', self.decimalPoint)
            textBuffer = textBuffer + colsValuesFormatted + "\n"
        return textBuffer

    def setBinding(self, event, command):
        """ Bind an event to an action for the treeview object """
        self.treeview.bind(event, command)

def change2Numeric(data):
    """ Try to convert each first field of data in numeric value
        if all values can't be converted, return data parameter
        if a numeric value exists in the column, all text values are considered as 0 """
    areAllText = True
    dataConverted = []
    for numItemData, item in data:
        try:
            ixFloat = float(numItemData.replace("< ", ""))
            areAllText = False
        except ValueError:
            ixFloat = 0.0
        dataConverted.append((ixFloat, item))
    if areAllText:
        dataConverted = data
    return dataConverted
