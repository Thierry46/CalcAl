#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-
"""
    *********************************************************
    Class : Table
    Auteur : Thierry Maillard (TMD)
    Date : 8/6/2016

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
from tkinter import *
from tkinter.ttk import *

class TableTreeView(Frame):
    def __init__(self, master, firstColumnsTitle, nbMinLines):
        """ Define  a table with labels cells """
        super(TableTreeView, self).__init__(master)
        self.numStableCol = len(firstColumnsTitle) - 1

        self.grid_rowconfigure(0, weight = 1)
        self.grid_columnconfigure(0, weight = 1)

        # Create treeview, scrollbars
        self.treeview = Treeview(self, height=nbMinLines)
        vsb = Scrollbar(self, orient=VERTICAL, command=self.treeview.yview)
        vsb.grid(row=0, column=1, sticky=(N,S))
        hsb = Scrollbar(self, orient=HORIZONTAL, command=self.treeview.xview)
        hsb.grid(row=1, column=0, sticky=(E,W))
        self.treeview.config(yscrollcommand=vsb.set)
        self.treeview.config(xscrollcommand=hsb.set)
        self.treeview.grid(row=0, sticky=(N,S,W,E))
        self.grid_rowconfigure(0, weight = 1)

        # Create header line
        self.treeview.heading("#0", text=firstColumnsTitle[0]) # Item key column
        if self.numStableCol > 0:
            self.treeview['columns'] = firstColumnsTitle[1:] # Other columns
            for titleCol in firstColumnsTitle[1:]:
                self.treeview.heading(titleCol, text=titleCol)
        else:
            self.treeview['columns'] = []

        # Apply column properties
        self.setColumnsDefaultProperties()

    def setColumnsDefaultProperties(self):
        """ Set Default column properties """
        # TODO : parameter widths
        self.treeview.column("#0", anchor=W, width=100, stretch=False, minwidth=50)
        for columnName in self.treeview['columns']:
            self.treeview.column(columnName, anchor=E, width=75, stretch=False, minwidth=50)

    def searchItem(self, name):
        """ find a name in each item text key and return the corresponding item
            or None if not found """
        foundItem = None
        for rowItem in self.treeview.get_children():
            if self.treeview.item(rowItem, option='text') == name:
                foundItem = rowItem
        return foundItem

    def insertOrCreateRow(self, name, columnsValues, tag='normalRow'):
        """ Modify the values of an existing row or create a new one """
        # Search if item name already exists
        foundItem = self.searchItem(name)
        if foundItem:
            self.treeview.item(foundItem, values=columnsValues)
        else:
            self.treeview.insert('', 'end', text=name, values=columnsValues, tags=(tag,))

    def deleteRow(self, name):
        """ Delete a row given its item name """
        foundItem = self.searchItem(name)
        if foundItem:
            self.treeview.delete(foundItem)

    def deleteListItems(self, listItem):
        """ Delete a list of row items """
        for item in listItem:
            self.treeview.delete(item)

    def getStableColumnsValues(self, excludeRowWithTitle=None):
        """ Return keyNames and stable cols for each rows """
        listValues = []
        for rowItem in self.treeview.get_children():
            if not excludeRowWithTitle or self.getTextForItemIndex(rowItem) != excludeRowWithTitle:
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

        # Restore title for each col
        numCol = 0
        for title in listTitlesCol:
            self.treeview.heading(numCol, text=title)
            numCol = numCol + 1

        # Add value in last colums of each row
        numRow = 0
        for rowItem in self.treeview.get_children():
            listRowValues = list(self.treeview.item(rowItem, option='values')[:self.numStableCol])
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
