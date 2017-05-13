# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : PathologyFrame
Author : Thierry Maillard (TMD)
Date   : 21/11/2016 - 30/11/2016

Role : Define Pathology frame content.
************************************************************************************
"""
from tkinter import *

from util import CalcalExceptions

from . import CallTypWindow
from . import FrameBaseCalcAl

class PathologyFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Pathology frame used to manage components in relation with pathologies """

    def __init__(self, master, mainWindow, logoFrame,
                 calculatorFrameModel, patientFrameModel):
        """ Initialize Pathologys Frame """
        super(PathologyFrame, self).__init__(master, mainWindow, logoFrame)
        self.calculatorFrameModel = calculatorFrameModel
        self.calculatorFrameModel.addObserver(self)
        self.patientFrameModel = patientFrameModel
        self.patientFrameModel.addObserver(self)

        self.listComponents = []
        self.listPathologies = []

        ##########
        # Defined pathologies Frame
        definedPathologiesFrame = LabelFrame(self, text=_("Defined pathologies"))
        definedPathologiesFrame.pack(side=LEFT, padx=5)

        # Defined pathologies listbox
        definedPathologiesListboxFrame = Frame(definedPathologiesFrame)
        definedPathologiesListboxFrame.pack(side=TOP)
        color = self.configApp.get('Colors', 'colorPathologiesList')
        self.pathologiesListbox = Listbox(definedPathologiesListboxFrame, selectmode=EXTENDED,
                                          background=color, height=10, width=40,
                                          exportselection=False)
        self.pathologiesListbox.grid(row=0, columnspan=2)
        CallTypWindow.createToolTip(self.pathologiesListbox,
                                    _("Use Ctrl and Shift keys") + "\n" + \
                                    _("for multiple selection"),
                                    self.delaymsTooltips)
        scrollbarRightPathologies = Scrollbar(definedPathologiesListboxFrame, orient=VERTICAL,
                                              command=self.pathologiesListbox.yview)
        scrollbarRightPathologies.grid(row=0, column=2, sticky=W+N+S)
        self.pathologiesListbox.config(yscrollcommand=scrollbarRightPathologies.set)
        self.pathologiesListbox.bind('<ButtonRelease-1>', self.clicPathologiesListbox)

        # Command buttons of definedPathologies Frame
        buttonDefinedPathologiesFrame = Frame(definedPathologiesFrame)
        buttonDefinedPathologiesFrame.pack(side=TOP)
        Button(buttonDefinedPathologiesFrame, text=_("Select composants in calculator"),
               command=self.selectInCalculator).pack(side=TOP)
        Button(buttonDefinedPathologiesFrame, text=_("Delete"),
               command=self.deletePathology).pack(side=TOP)

        ##########
        # Pathologies definition Frame
        pathologyDefinitionFrame = LabelFrame(self, text=_("Pathology definition"))
        pathologyDefinitionFrame.pack(side=LEFT, padx=5)

        entriesFrame = Frame(pathologyDefinitionFrame)
        entriesFrame.pack(side=TOP)
        bottomDefinitionFrame = Frame(pathologyDefinitionFrame)
        bottomDefinitionFrame.pack(side=TOP, pady=10)

        Label(entriesFrame, text=_("Pathology name")).grid(row=0, column=0, sticky=E)
        self.pathologyNameEntryVar = StringVar()
        self.pathologyNameEntry = Entry(entriesFrame, textvariable=self.pathologyNameEntryVar,
                                        width=35)
        self.pathologyNameEntry.grid(row=0, column=1, sticky=W)

        Label(entriesFrame, text=_("Description") + " :").grid(row=1, column=0, sticky=W)
        colorBG = self.configApp.get('Colors', 'colorPathologyDesctiptionEditor')
        self.pathologyDescriptionTextEditor = Text(entriesFrame,
                                                   wrap=NONE,
                                                   height=5, width=60,
                                                   background=colorBG)
        self.pathologyDescriptionTextEditor.grid(row=2, columnspan=2)
        scrollbarRightDescription = Scrollbar(entriesFrame,
                                              command=self.pathologyDescriptionTextEditor.yview)
        scrollbarRightDescription.grid(row=2, column=2, sticky=W+N+S)
        scrollbarBottom = Scrollbar(entriesFrame, orient=HORIZONTAL,
                                    command=self.pathologyDescriptionTextEditor.xview)
        scrollbarBottom.grid(row=3, columnspan=2, sticky=N+E+W)
        self.pathologyDescriptionTextEditor.config(yscrollcommand=scrollbarRightDescription.set)
        self.pathologyDescriptionTextEditor.config(xscrollcommand=scrollbarBottom.set)

        Label(entriesFrame, text=_("Reference")).grid(row=4, column=0, sticky=E)
        self.pathologyReferenceEntryVar = StringVar()
        self.pathologyReferenceEntry = Entry(entriesFrame,
                                             textvariable=self.pathologyReferenceEntryVar, width=35)
        self.pathologyReferenceEntry.grid(row=4, column=1, sticky=W)

        # Bottom definition frame frame
        Label(bottomDefinitionFrame,
              text=_("Componants\nto folllow\nfor this\npathology")).pack(side=LEFT)
        componentsFrame = Frame(bottomDefinitionFrame)
        componentsFrame.pack(side=LEFT)
        color = self.configApp.get('Colors', 'componentsListboxColor')
        self.componentsListbox = Listbox(componentsFrame, selectmode=EXTENDED,
                                         background=color, height=10, width=18,
                                         exportselection=False)
        self.componentsListbox.grid(row=0, columnspan=2)
        CallTypWindow.createToolTip(self.componentsListbox,
                                    _("Use Ctrl and Shift keys") + "\n" + \
                                    _("for multiple selection"),
                                    self.delaymsTooltips)
        scrollbarRightComponents = Scrollbar(componentsFrame, orient=VERTICAL,
                                   command=self.componentsListbox.yview)
        scrollbarRightComponents.grid(row=0, column=2, sticky=W+N+S)
        self.componentsListbox.config(yscrollcommand=scrollbarRightComponents.set)

        buttonDefinitionFrame = Frame(bottomDefinitionFrame)
        buttonDefinitionFrame.pack(side=LEFT)
        Button(buttonDefinitionFrame, text=_("Save pathology"),
               command=self.savePathology).pack(side=TOP)
        Button(buttonDefinitionFrame, text=_("Clear pathology"),
               command=self.clearPathologyDefinition).pack(side=TOP)


    def update(self, observable, event):
        """Called when the model object is modified. """
        self.logger.debug("PathologyFrame received from model : " + event)
        try:
            if observable == self.calculatorFrameModel:
                if event == "INIT_DB":
                    self.init()
            elif observable == self.patientFrameModel:
                if event == "UPDATE_PATHOLOGIES_PATIENT":
                    self.selectPathologies()

        except CalcalExceptions.CalcalValueError as exc:
            message = _("Error") + " : " + str(exc) + " !"
            self.mainWindow.setStatusText(message, True)

    def init(self):
        """ Initialyse definition frame entries
            Set to empty string id filters fields """
        self.pathologyNameEntryVar.set("")
        self.pathologyDescriptionTextEditor.delete('1.0', END)
        self.pathologyReferenceEntryVar.set("")
        self.componentsListbox.delete(0, END)

        # List components
        self.listComponents = self.calculatorFrameModel.getListComponents()
        self.componentsListbox.delete(0, END)
        for component in self.listComponents:
            self.componentsListbox.insert(END, component[1] + ' (' + component[2] + ')')

        # List of Defined pathologies
        self.initListPathologies()

    def initListPathologies(self):
        """ Init pathologies listBox content """
        self.pathologiesListbox.delete(0, END)
        database = self.databaseManager.getDatabase()
        self.listPathologies = database.getDefinedPathologiesNames()
        for pathology in self.listPathologies:
            self.pathologiesListbox.insert(END, pathology)

    def savePathology(self):
        """ Save a new pathology in database """
        # Get user definition values
        name = self.pathologyNameEntryVar.get()
        description = self.pathologyDescriptionTextEditor.get('1.0', 'end-1c')
        reference = self.pathologyReferenceEntryVar.get()
        # Get Constituants selected by user
        listUserComponentCode = set([self.listComponents[index][0]
                                     for index in self.componentsListbox.curselection()])
        try:
            database = self.databaseManager.getDatabase()
            database.savePathology(name, description, reference, listUserComponentCode)
            self.initListPathologies()
            self.patientFrameModel.initListPathologies()
            self.mainWindow.setStatusText(_("Pathology saved in database") + " : " + name)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def clearPathologyDefinition(self):
        """ Clear definition fields for pathology """
        self.pathologyNameEntryVar.set("")
        self.pathologyDescriptionTextEditor.delete('1.0', END)
        self.pathologyReferenceEntryVar.set("")
        self.componentsListbox.selection_clear(0, END)

    def clicPathologiesListbox(self, evt=None):
        """ Update Definition frame with pathology selected by user """
        listIndexSelection = self.pathologiesListbox.curselection()
        if len(listIndexSelection) == 1:
            self.setStateInputFields(state=NORMAL)
            self.clearPathologyDefinition()
            pathologyName = self.pathologiesListbox.get(listIndexSelection[0])
            try:
                # Get info in database
                database = self.databaseManager.getDatabase()
                name, description, reference, listComponentsCodes = \
                        database.getDefinedPathologiesDetails(pathologyName)
                # Update definition fields
                self.pathologyNameEntryVar.set(name)
                self.pathologyDescriptionTextEditor.delete('1.0', END)
                self.pathologyDescriptionTextEditor.insert(INSERT, description)
                self.pathologyReferenceEntryVar.set(reference)
                # Update components list
                self.componentsListbox.selection_clear(0, END)
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
            except ValueError as exc:
                self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)
        elif len(listIndexSelection) > 1:
            self.setStateInputFields(state=DISABLED)
            self.pathologyDescriptionTextEditor.config(state=DISABLED)

    def setStateInputFields(self, state):
        """ Set state for all input fields """
        self.clearPathologyDefinition()
        self.pathologyNameEntry.config(state=state)
        self.pathologyDescriptionTextEditor.config(state=state)
        self.pathologyReferenceEntry.config(state=state)
        self.componentsListbox.config(state=state)

    def selectInCalculator(self, changeTab=True):
        """ For chosen pathologies, select components to follow in Calculator frame """
        listIndexSelection = self.pathologiesListbox.curselection()
        nbSelectedRows = len(listIndexSelection)
        try:
            if nbSelectedRows < 1:
                raise ValueError(_("Please select at least one pathology"))
            listPathologiesNames = [self.pathologiesListbox.get(index)
                                    for index in listIndexSelection]
            self.calculatorFrameModel.selectComponentsCodes(listPathologiesNames)

            if changeTab:
                self.mainWindow.enableTabCalculator(True)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)


    def deletePathology(self):
        """ Delete a pathology in database """
        listIndexSelection = self.pathologiesListbox.curselection()
        nbSelectedRows = len(listIndexSelection)
        try:
            if nbSelectedRows != 1:
                raise ValueError(_("Please select one and only one pathology to delete"))
            pathologyName = self.pathologiesListbox.get(listIndexSelection[0])
            isDestructionOk = messagebox.askyesno(_("Deleting selected user element in database"),
                                                  _("Do you really want to delete selection in database ?") + \
                                                  "\n" + pathologyName,
                                                  icon='warning')
            if isDestructionOk:
                database = self.databaseManager.getDatabase()
                database.deletePathology(pathologyName)
                self.clearPathologyDefinition()
                self.initListPathologies()
                self.patientFrameModel.initListPathologies()
                self.mainWindow.setStatusText(_("Pathology deleted in database") + " : " + pathologyName)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def selectPathologies(self):
        """ Select pathologies asked by patient model """
        listPathologies2Select = self.patientFrameModel.getCurrentPatient().getPathologies()
        self.pathologiesListbox.selection_clear(0, END)
        firstIndex = True
        for pathology2Select in listPathologies2Select:
            index = 0
            for pathology in self.listPathologies:
                if pathology == pathology2Select:
                    self.pathologiesListbox.selection_set(index)
                    if firstIndex:
                        self.pathologiesListbox.see(index)
                        firstIndex = False
                    break
                index += 1
        # Select corresponging element in calculator
        self.clicPathologiesListbox()
        self.selectInCalculator(changeTab=False)
