#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
    *********************************************************
    Class : Table
    Auteur : Thierry Maillard (TMD)
    Date : 8/5/2016 - 21/5/2016

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

from tkinter import *
from tkinter.ttk import *

class TableTreeView(Frame):
    def __init__(self, master, firstColumnsTitle, nbMinLines,
                 firstColWidth=100, otherColWidth=75, colMinWidth=50,
                 selectmode="none"):
        self.decimal_point = locale.localeconv()['decimal_point']

        """ Define  a table with labels cells """
        super(TableTreeView, self).__init__(master)
        self.numStableCol = len(firstColumnsTitle) - 1
        self.firstColWidth = firstColWidth
        self.otherColWidth = otherColWidth
        self.colMinWidth = colMinWidth

        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Create treeview, scrollbars
        self.treeview = Treeview(self, height=nbMinLines, selectmode=selectmode)
        vsb = Scrollbar(self, orient=VERTICAL, command=self.treeview.yview)
        vsb.grid(row=0, column=1, sticky=(N,S))
        hsb = Scrollbar(self, orient=HORIZONTAL, command=self.treeview.xview)
        hsb.grid(row=1, column=0, sticky=(E,W))
        self.treeview.config(yscrollcommand=vsb.set)
        self.treeview.config(xscrollcommand=hsb.set)
        self.treeview.grid(row=0, sticky=(N,S,W,E))
        self.grid_rowconfigure(0, weight = 1)

        # Create header line
        # Item key column
        self.treeview.heading("#0", text=firstColumnsTitle[0],
                              command=lambda select=True:self.selectAllOrNothing(select))
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
        # TODO : parameter widths
        self.treeview.column("#0", anchor=W, width=self.firstColWidth,
                             stretch=False, minwidth=self.colMinWidth )
        for columnName in self.treeview['columns']:
            self.treeview.column(columnName, anchor=E, width=self.otherColWidth,
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
         self.treeview.see(self.searchItem(name))

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
            if (not excludeRowWithTitle or self.getTextForItemIndex(rowItem) != excludeRowWithTitle ) \
                and (not onlySelected or (rowItem in listSelectedRows)):
                valuesRow = [self.treeview.item(rowItem, option='text'),
                             self.treeview.item(rowItem, option='values')[:self.numStableCol]]
                listValues.append(valuesRow)
        return listValues

    def getColumnsValues(self):
        """ Return all column values for all rows"""
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
            self.treeview.heading(numCol, command=lambda col=numCol:self.sortby(col, False))
            numCol = numCol + 1

        # Add value in last colums of each row
        nbRowsInTable = self.treeview.get_children()
        assert nbRowsInTable is None or variablesColValues is None or \
              len(nbRowsInTable) == len(variablesColValues),\
            "Error : " + str(nbRowsInTable) +  " rows in table is different than " + \
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
        data =  self.change2Numeric(data)
        # now sort the data in place
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            self.treeview.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        self.treeview.heading(col, command=lambda col=col:self.sortby(col, not descending))

    def change2Numeric(self, data):
        """ Try to convert each first field of data in numeric value
            if all values can't be converted, return data parameter
            if a numeric value exists in the column, all text values are considered as 0 """
        areAllText = True
        dataConverted = []
        for ix, item in data:
            try:
                ixFloat = float(ix.replace("< ", ""))
                areAllText = False
            except ValueError:
                ixFloat = 0.0
            dataConverted.append((ixFloat, item))
        if areAllText:
            dataConverted = data
        return dataConverted

    def selectAllOrNothing(self, selectAll):
        """ Select every or no normal row according parameter """
        for child in self.treeview.get_children():
            if 'normalRow' in self.treeview.item(child, option='tags'):
                if selectAll :
                    self.treeview.selection_add(child)
                else:
                    self.treeview.selection_remove(child)
        selectAll = not selectAll
        self.treeview.heading("#0", command=lambda select=selectAll:self.selectAllOrNothing(select))

    def getTableAsText(self):
        """ Return table selected content in text format """
        textBuffer = ""
        selectedItems = self.getSelectedItems()
        if len(selectedItems) == 0:
            raise ValueError(_("Please select at least one line in list of food"))
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
            if self.decimal_point != '.':
                colsValuesFormatted = colsValuesFormatted.replace('.', self.decimal_point)
            textBuffer = textBuffer + colsValuesFormatted + "\n"
        return textBuffer

    def setBinding(self, event, command):
        """ Bind an event to an action for the treeview object """
        self.treeview.bind(event, command)
