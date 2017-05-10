#! /usr/bin/env python
# -*- coding: ISO-8859-1 -*-
"""
    *********************************************************
    Class : TableCheckButton
    Auteur : Thierry Maillard (TMD)
    Date : 17/6/2016

    Role : Table Checkbutton widget.

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

class TableCheckButton(Checkbutton):
    def __init__(self, master, numRow):
        """ Define  a table with labels cells """
        self.varState=IntVar(0)
        super(TableCheckButton, self).__init__(master,
                                               command=self.checkButtonCallback,
                                               variable=self.varState)
        self.master = master
        self.numRow = numRow

    def checkButtonCallback(self):
        """ Apply the state of this heading cell to all other rows"""
        if self.numRow == 0 or self.numRow == self.master.getRowsTotalNumber() - 1:
            self.master.setAllCheckButton(self.isSelected())
        else:
            self.master.setCheckButton(0, False)
            self.master.setCheckButton(self.master.getRowsTotalNumber() - 1, False)


    def isSelected(self):
        """ Return True if this checkButton is selected """
        return self.varState.get() == 1
