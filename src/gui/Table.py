#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-
"""
    *********************************************************
    Class : Table
    Auteur : Thierry Maillard (TM)
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

class Table(Frame):
    def __init__(self, master, foodName, quantity,
                 nbMaxComponents, nbMaxDigit,
                 colorLabel, colorComponents):
        """ Define  a table with 2 lines and labels cells """
        super(Table, self).__init__(master, background="black")
        self._cells = []
        self.txtFont=font.Font(family="Arial", size=9)

        self.nbMaxComponents = nbMaxComponents
        self.nbMaxDigit = nbMaxDigit
        self.numStableCol = 2
        self.numRowTitle = 1
        numRow = self.appendNewRow()
        self.modifyRow(numRow, foodName, quantity, colorLabel, colorComponents)

    def setCellValue(self, row, column, value, colorBg=None):
        """ Set a value in a cell """
        cell = self._cells[row][column]
        cell.configure(text=value)
        if colorBg:
            cell.configure(bg=colorBg)

    def getCellValue(self, row, column):
        """ Get a value in a cell """
        cell = self._cells[row][column]
        return cell["text"]

    def getCellValueInt(self, row, column):
        """ Get an int value in a cell """
        return int(self.getCellValue(row, column))

    def getColumnWidth(self, column):
        width = 0
        for row in range(len(self._cells)):
            cell = self._cells[row][column]
            width = max(width, cell.winfo_width())
            print("getColumnWidth/width=", width)
        return width

    def setColumnWidth(self, column, witdh):
        for row in range(len(self._cells)):
            self._cells[row][column]['width'] = witdh

    def getColumnsValuesText(self, numCol, withFirstRow=True, withLastRow=True):
        """ Get all the values from a column of this table without title """
        columnValues = []
        firstRow = 0
        nbRows = len(self._cells)
        if not withFirstRow:
            firstRow = 1
        if nbRows > 0 and not withLastRow:
            nbRows = nbRows - 1
        for row in range(firstRow, nbRows):
            if row >= self.numRowTitle:
                columnValues.append(self.getCellValue(row, numCol))
        return columnValues

    def getColumnsValuesInt(self, numCol, withFirstRow=True, withLastRow=True):
        """ Get all the values converted in integer from a column of this table without title """
        columnValuesText = self.getColumnsValuesText(numCol, withFirstRow, withLastRow)
        colomnValuesInt = [int(value) for value in columnValuesText]
        return colomnValuesInt

    def getColumnsValuesFloat(self, numCol, withFirstRow=True, withLastRow=True):
        """ Get all the values converted in float from a column of this table without title """
        columnValuesText = self.getColumnsValuesText(numCol, withFirstRow, withLastRow)
        colomnValuesFloat = [float(value) for value in columnValuesText]
        return colomnValuesFloat

    def getRowForText(self, foodName, numCol, withFirstRow=True, withLastRow=True):
        """ Give the row of a value searched in a column
            return -1 if not found """
        numRow = -1
        # Get values for ALL rows to get rigth indices, not from a truncated list
        listExistingNames = self.getColumnsValuesText(numCol, True, True)
        if foodName in listExistingNames:
            numRow = listExistingNames.index(foodName) + self.numRowTitle

        # Reply according parameters
        if (numRow == 0 and not withFirstRow) or \
           (numRow == len(self._cells) and not withLastRow):
            numRow = -1
        return numRow

    def modifyRow(self, numRow, foodName, quantity, colorfirstCol, colorComponents,
                  componentsValues=None):
        self.setCellValue(numRow, 0, foodName, colorfirstCol)
        self.setCellValue(numRow, 1, str(quantity), colorfirstCol)
        numCol = self.numStableCol
        if componentsValues:
            for value in componentsValues:
                if isinstance(value, float):
                    valueStr = ("{0:." + str(self.nbMaxDigit) + "f}").format(value)
                else:
                    valueStr = str(value)
                self.setCellValue(numRow, numCol, valueStr, colorComponents)
                numCol = numCol + 1
        while numCol < self.nbMaxComponents + self.numStableCol:
            self.setCellValue(numRow, numCol, '', colorComponents)
            numCol = numCol + 1

    def appendNewRow(self):
        """ Create a new row and return its number """
        row = []
        numcol = 0
        numRow = len(self._cells)
        for nb in range(self.nbMaxComponents + + self.numStableCol):
            labelCell = Label(self, text="")
            labelCell.grid(row=numRow, column=numcol, sticky=N+S+E+W, padx=1, pady=1)
            row.append(labelCell)
            numcol = numcol + 1
        self._cells.append(row)
        return numRow
