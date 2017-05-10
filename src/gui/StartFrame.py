# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : StartFrame
Author : Thierry Maillard (TMD)
Date  : 12/3/2016

Role : Define start frame content.
************************************************************************************
"""
from tkinter import *
from tkinter import messagebox

from gui import FrameBaseCalcAl

class StartFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Welcome frame used to choose database to use """

    def __init__(self, master, mainWindow, logoFrame):
        super(StartFrame, self).__init__(master, mainWindow, logoFrame)

        databaseFrame = Frame(self)
        databaseFrame.pack(side=TOP, padx=5, pady=5)

        Label(databaseFrame, text=_('Choose a database to use')).grid(row=0, column=1)
        self.databaseListbox = Listbox(databaseFrame)
        self.databaseListbox.grid(row=1, column=1)
        self.databaseListbox.bind('<ButtonRelease-1>', self.clicListBoxItem)
        self.startButton = Button(databaseFrame, text=_('Start'),
                                  command=self.start, state=DISABLED)
        self.startButton.grid(row=2, column=1, sticky=EW)
        Button(databaseFrame, text=_('New'),
               command=self.newDB).grid(row=1, column=0, sticky=W)
        self.deleteButton = Button(databaseFrame, text=_('Delete'),
                                   command=self.deleteDB, state=DISABLED)
        self.deleteButton.grid(row=1, column=3, sticky=W)

    def clicListBoxItem(self, evt):
        """ Activate New and Delete button when a database is chosen """
        index = self.databaseListbox.curselection()
        if index:
            dbname = self.databaseListbox.get(index)
            self.logger.info(dbname + _('chosen'))
            self.startButton.configure(state=NORMAL)
            self.deleteButton.configure(state=NORMAL)

    def start(self):
        """ start calculator frame with chosen database """
        index = self.databaseListbox.curselection()
        if index:
            dbname = self.databaseListbox.get(index)
            self.logger.info(dbname + _('chosen'))
            message = 'TODO start calculator'
            self.mainWindow.setStatusText(message)
            self.logger.info(message)

    def newDB(self):
        """ Create a new database """
        self.logger.info('TODO create database')

    def deleteDB(self):
        """ Delete a database """
        self.logger.info('TODO delete database')
