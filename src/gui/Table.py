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
from gui import TableCheckButton

class Table(Frame):
    def __init__(self, master, firstColumns,
                 colorLabel, colorComponents, withCheckBox=True):
        """ Define  a table with labels cells """
        super(Table, self).__init__(master, background="black")
        self.withCheckBox = withCheckBox
        self._cells = []
        self.txtFont=font.Font(family="Arial", size=9)

        self.numStableCol = len(firstColumns)
        numRow = self.appendNewRow()
        self.modifyRow(numRow, firstColumns, colorLabel, colorComponents)

    def setCellValue(self, row, column, value, colorBg=None):
        """ Set a value in the cell at line row and for column"""
        if self.withCheckBox:
            column = column + 1 # User don't have to care about checkbox column
        cell = self._cells[row][column]
        cell.configure(text=value)
        if colorBg:
            cell.configure(bg=colorBg)
        cell.grid(row=row, column=column, sticky=N+S+E+W, padx=1, pady=1)

    def getCellValue(self, row, column):
        """ Get a value in a cell """
        if self.withCheckBox:
            column = column + 1 # User don't have to care about checkbox column
        cell = self._cells[row][column]
        return cell["text"]

    def getCellValueInt(self, row, column):
        """ Get an int value in a cell """
        return int(self.getCellValue(row, column))

    def getColumnsValuesText(self, numCol, withFirstRow=True, withLastRow=True,
                             onlyVisible=False):
        """ Get all the values from a column of this table without title """
        columnValues = []
        nbMinRow = 0
        if not withFirstRow:
            nbMinRow = nbMinRow + 1
        if not withLastRow:
            nbMinRow = nbMinRow + 1

        listRows = self.getListRows(onlyVisible)
        if len(listRows) > nbMinRow:
            firstRow = listRows[0]
            lastRows = listRows[-1]
            if not withFirstRow:
                firstRow = listRows[1]
            if not withLastRow:
                lastRows = listRows[-2]

            for row in listRows:
                if row >= firstRow and row <= lastRows:
                    columnValues.append(self.getCellValue(row, numCol))
        return columnValues

    def getColumnsValuesInt(self, numCol, withFirstRow=False, withLastRow=True,
                            onlyVisible=True):
        """ Get all the values converted in integer from a column of this table without title """
        columnValuesText = self.getColumnsValuesText(numCol, withFirstRow, withLastRow,
                                                     onlyVisible)
        colomnValuesInt = [int(value) for value in columnValuesText]
        return colomnValuesInt

    def getColumnsValuesFloat(self, numCol, withFirstRow=False, withLastRow=True,
                              onlyVisible=True):
        """ Get all the values converted in float from a column of this table without title """
        columnValuesText = self.getColumnsValuesText(numCol, withFirstRow, withLastRow,
                                                     onlyVisible)
        colomnValuesFloat = [float(value) for value in columnValuesText]
        return colomnValuesFloat

    def getRowForText(self, foodName, numCol):
        """ Give the row of a value searched in a column
            return -1 if not found """
        numRow = -1
        # Get values for ALL rows to get rigth indices, not from a truncated list
        listExistingNames = self.getColumnsValuesText(numCol, withFirstRow=True, withLastRow=True,
                                                      onlyVisible=False)
        if foodName in listExistingNames:
            numRow = listExistingNames.index(foodName)
        return numRow

    def modifyRow(self, numRow, firstColumns, colorfirstCol, colorComponents,
                  componentsValues=None):
        assert self.numStableCol == len(firstColumns), 'modifyRow : problem number firstColumns'
        if self.withCheckBox:
            self.setAllCheckButton(False)
        numCol = 0
        for colName in firstColumns:
            self.setCellValue(numRow, numCol, colName, colorfirstCol)
            numCol = numCol + 1
        if componentsValues:
            for value in componentsValues:
                self.setCellValue(numRow, numCol, value, colorComponents)
                numCol = numCol + 1
        self.restoreRow(numRow)

    def restoreRow(self, numRow):
        """ Display all cells of this row """
        for cell in self._cells[numRow]:
            cell.grid()

    def appendNewRow(self):
        """ Create a new row and return its number """
        row = []
        numcol = 0
        numRow = len(self._cells)

        # Checkbox at the beginning of the row
        if self.withCheckBox:
            checkButton = TableCheckButton.TableCheckButton(self, numRow)
            checkButton.grid(row=numRow, column=numcol, sticky=N+S+E+W, padx=1, pady=1)
            row.append(checkButton)
            numcol = numcol + 1

        # Other column
        nbStartColumn = self.numStableCol
        if self.withCheckBox:
            nbStartColumn = nbStartColumn + 1
        totalNumberOfColumn = max(nbStartColumn, self.grid_size()[0])
        while numcol < totalNumberOfColumn:
            row.append(Label(self, text=""))
            numcol = numcol + 1
        self._cells.append(row)
        return numRow

    def setAllCheckButton(self, isSelected=False, withFirstRow=True, withLastRow=True):
        """ Set the checButton state for all rows"""
        firstRow = 0
        nbRows = len(self._cells)
        if not withFirstRow:
            firstRow = 1
        if nbRows > 0 and not withLastRow:
            nbRows = nbRows - 1
        for row in range(firstRow, nbRows):
            self.setCheckButton(row, isSelected)

    def setCheckButton(self, numRow, isSelected=False):
        """ Set the checButton state for given rows"""
        cellCheck = self._cells[numRow][0]
        if isSelected:
            cellCheck.select()
        else:
            cellCheck.deselect()

    def getRowsTotalNumber(self, onlyVisible=False):
        """ Return total of active rows"""
        nbRows = 0
        if onlyVisible:
            nbRows = len(self.getListRows())
        else:
            nbRows = self.grid_size()[1] # Total number of row in grid with hidden
        return nbRows

    def getListRows(self, onlyVisible=False):
        """" Return the list of rows number in the table """
        listNumRows = []

        if onlyVisible:
            for element in self.grid_slaves():
                numRow = int(element.grid_info()["row"])
                if numRow not in listNumRows:
                    listNumRows.append(numRow)
            listNumRows.sort()
        else:
            listNumRows = range(self.grid_size()[1])  # Total number of row in grid with hidden
        return listNumRows

    def getListVisibleComponentsCols(self):
        """" Return the list of column numbers for components columns in the table """
        listNumCols = []
        modif4UserCol = 0
        if self.withCheckBox:
            modif4UserCol = -1

        for element in self.grid_slaves():
            numCol = int(element.grid_info()["column"])
            if numCol > self.numStableCol and (numCol + modif4UserCol) not in listNumCols:
                listNumCols.append(numCol + modif4UserCol)
        listNumCols.sort()
        return listNumCols

    def getSelectedRows(self):
        """" Return rows in the table that are selected """
        listSelectedRows = []
        for numRow in range(1, len(self._cells)-1):
            if numRow != 0:
                cellCheck = self._cells[numRow][0]
                if cellCheck.isSelected():
                    listSelectedRows.append(numRow)
        return listSelectedRows

    def deleteRow(self, listRowsToDelete):
        """ Hide rows in listRows """
        for element in self.grid_slaves():
            if int(element.grid_info()["row"]) in listRowsToDelete:
                element.grid_remove() # grid_remove() keep row setting when hidding

    def deleteCol(self, firstColsToDelete):
        """ Hide rows in listRows """
        # Problem : don't work : don't remove cells from grid
        for element in self.grid_slaves():
            if int(element.grid_info()["column"]) >= firstColsToDelete:
                element.grid_remove() # Don't work
                element.configure(text='') # To bypass the problem

    def adjustNumberOfColumn(self, nbColumnComponents):
        """ Adjust number of column"""
        nbRows = self.grid_size()[1] # Total number of row in grid
        nbExistingCols = self.grid_size()[0] # Total number of column in grid
        nbAskedCols = self.numStableCol + nbColumnComponents
        if self.withCheckBox:
            nbAskedCols = nbAskedCols + 1
        if nbAskedCols != nbExistingCols:
            if nbAskedCols < nbExistingCols:
                self.deleteCol(nbAskedCols)
            else:
                # Create new empty cells in every lines
                numRow = 0
                for row in self._cells:
                    numCol = nbExistingCols
                    while numCol < nbAskedCols:
                        row.append(Label(self, text=""))
                        numCol = numCol + 1
