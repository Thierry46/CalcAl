# -*- coding: utf-8 -*-
"""
************************************************************************************
Class  : PatientFrame
Author : Thierry Maillard (TMD)
Date   : 26/11/2016 - 1/12/2016

Role : Define Patient frame content.
************************************************************************************
"""
import datetime

import tkinter
from tkinter.ttk import Combobox
from tkinter import messagebox

from util import CalcalExceptions
from . import CallTypWindow
from . import FrameBaseCalcAl

class PatientFrame(FrameBaseCalcAl.FrameBaseCalcAl):
    """ Patient frame used to manage patient information """

    def __init__(self, master, mainWindow, logoFrame, patientFrameModel):
        """ Initialize Patients Frame """
        super(PatientFrame, self).__init__(master, mainWindow, logoFrame)
        self.patientFrameModel = patientFrameModel
        self.patientFrameModel.addObserver(self)
        self.listPathologies = []

        ##########
        # Patient definition Frame
        patientMainFrame = tkinter.LabelFrame(self, text=_("Patient information"), padx=10)
        patientMainFrame.pack(side=tkinter.TOP)
        rightFrame = tkinter.Frame(patientMainFrame)
        rightFrame.pack(side=tkinter.LEFT)
        patientDefinitionFrame = tkinter.Frame(rightFrame)
        patientDefinitionFrame.pack(side=tkinter.TOP)

        labelPatientCode = tkinter.Label(patientDefinitionFrame, text=_("Patient code") + " :")
        labelPatientCode.grid(row=0, column=0, sticky=tkinter.E)
        CallTypWindow.createToolTip(labelPatientCode,
                                    _("Type new patient code or select an existant"),
                                    self.delaymsTooltips)

        self.patientCodeVar = tkinter.StringVar()
        self.patientCodeVar.trace_variable("w", self.changePatient)
        widthCode = int(self.configApp.get('Size', 'patientCodeComboboxWidth'))
        self.patientCodeCombobox = Combobox(patientDefinitionFrame, exportselection=0,
                                            textvariable=self.patientCodeVar,
                                            state=tkinter.NORMAL,
                                            width=widthCode)
        self.patientCodeCombobox.grid(row=0, column=1, sticky=tkinter.W)

        tkinter.Label(patientDefinitionFrame, text=_("Birth year") + " :").grid(row=1, column=0,
                                                                                sticky=tkinter.E)
        self.currentYear = datetime.datetime.now().year
        self.oldestPatient = int(self.configApp.get('Patient', 'oldestPatient'))
        self.birthYearCombobox = Combobox(patientDefinitionFrame, exportselection=0,
                                          state="readonly",
                                          width=len(str(self.currentYear + self.oldestPatient)),
                                          values=list(range(self.currentYear-self.oldestPatient,
                                                            self.currentYear+1)))
        self.birthYearCombobox.bind('<<ComboboxSelected>>', self.modifyPatient)
        self.birthYearCombobox.grid(row=1, column=1, sticky=tkinter.W)
        tkinter.Label(patientDefinitionFrame, text=_("Gender") + " :").grid(row=2, column=0,
                                                                            sticky=tkinter.E)
        genderFrame = tkinter.Frame(patientDefinitionFrame)
        genderFrame.grid(row=2, column=1, sticky=tkinter.EW)
        self.genderVar = tkinter.StringVar()
        tkinter.Radiobutton(genderFrame, text=_("M"), variable=self.genderVar, value="M",
                    command=self.modifyPatient).pack(side=tkinter.LEFT)
        tkinter.Radiobutton(genderFrame, text=_("F"), variable=self.genderVar, value="F",
                    command=self.modifyPatient).pack(side=tkinter.LEFT)
        tkinter.Radiobutton(genderFrame, text=_("U"), variable=self.genderVar, value="U",
                    command=self.modifyPatient).pack(side=tkinter.LEFT)
        tkinter.Label(patientDefinitionFrame, text=_("Size") + " (cm) :").grid(row=3, column=0,
                                                                               sticky=tkinter.E)
        self.sizeMin = int(self.configApp.get('Patient', 'sizeMin'))
        self.sizeMax = int(self.configApp.get('Patient', 'sizeMax'))
        self.sizeCombobox = Combobox(patientDefinitionFrame, exportselection=0,
                                     state="readonly", width=len(str(self.sizeMax)),
                                     values=list(range(self.sizeMin, self.sizeMax+1)))
        self.sizeCombobox.bind('<<ComboboxSelected>>', self.modifyPatient)
        self.sizeCombobox.grid(row=3, column=1, sticky=tkinter.W)

        # Buttons command
        buttonDefinitionFrame = tkinter.Frame(rightFrame)
        buttonDefinitionFrame.pack(side=tkinter.TOP)
        tkinter.Button(buttonDefinitionFrame, text=_("Delete"),
               command=self.deletePatient).pack(side=tkinter.LEFT)

        # Notes frame
        patientNoteFrame = tkinter.LabelFrame(patientMainFrame, text=_("Notes for this patient"),
                                              padx=10)
        patientNoteFrame.pack(side=tkinter.LEFT)
        self.patientNotesTextEditor = tkinter.Text(patientNoteFrame,
                                           wrap=tkinter.NONE,
                                           height=10, width=30,
                                           background=self.configApp.get('Colors',
                                                                         'colorPatientEditor'))
        self.patientNotesTextEditor.bind('<FocusOut>', self.modifyPatient)
        self.patientNotesTextEditor.grid(row=2, columnspan=2)
        scrollbarRightNotes = tkinter.Scrollbar(patientNoteFrame,
                                                command=self.patientNotesTextEditor.yview)
        scrollbarRightNotes.grid(row=2, column=2, sticky=tkinter.W+tkinter.N+tkinter.S)
        scrollbarBottom = tkinter.Scrollbar(patientNoteFrame, orient=tkinter.HORIZONTAL,
                                    command=self.patientNotesTextEditor.xview)
        scrollbarBottom.grid(row=3, columnspan=2, sticky=tkinter.N+tkinter.E+tkinter.W)
        self.patientNotesTextEditor.config(yscrollcommand=scrollbarRightNotes.set)
        self.patientNotesTextEditor.config(xscrollcommand=scrollbarBottom.set)

        patientListsFrame = tkinter.Frame(patientMainFrame, padx=10)
        patientListsFrame.pack(side=tkinter.LEFT)
        # Pathologies listbox for this patient
        pathologiesListboxFrame = tkinter.LabelFrame(patientListsFrame,
                                                     text=_("Patient pathologies"))
        pathologiesListboxFrame.pack(side=tkinter.TOP)
        color = self.configApp.get('Colors', 'colorPathologiesList')
        self.pathologiesListbox = tkinter.Listbox(pathologiesListboxFrame,
                                                  selectmode=tkinter.EXTENDED,
                                          background=color, height=9, width=20,
                                          exportselection=False)
        self.pathologiesListbox.grid(row=0, columnspan=2)
        CallTypWindow.createToolTip(self.pathologiesListbox,
                                    _("Use Ctrl and Shift keys") + "\n" + \
                                    _("for multiple selection"),
                                    self.delaymsTooltips)
        scrollbarRightPathologies = tkinter.Scrollbar(pathologiesListboxFrame,
                                                      orient=tkinter.VERTICAL,
                                                      command=self.pathologiesListbox.yview)
        scrollbarRightPathologies.grid(row=0, column=2, sticky=tkinter.W+tkinter.N+tkinter.S)
        self.pathologiesListbox.config(yscrollcommand=scrollbarRightPathologies.set)
        self.pathologiesListbox.bind('<ButtonRelease-1>', self.clicPathologiesListbox)

    def changePatient(self, *dummy):
        """ Inform model that patient has changed by clicking on combobox or changing its value"""
        try:
            self.logger.debug("PatientFrame/changePatient()")
            newPatientCode = self.patientCodeVar.get()
            if newPatientCode in self.patientCodeCombobox['values']:
                self.patientFrameModel.changePatient(newPatientCode)
                self.mainWindow.setStatusText(_("Patient displayed") + " : " + newPatientCode)
            else:
                self.clearPatientDefinition()
        except CalcalExceptions.CalcalValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def clearPatientDefinition(self):
        """ Clear Patient definition frame """
        #self.birthYearCombobox.set(self.currentYear - self.oldestPatient//2)
        self.birthYearCombobox.set("")
        self.genderVar.set("U")
        #self.sizeCombobox.set((self.sizeMax + self.sizeMin)//2)
        self.sizeCombobox.set(0)
        self.patientNotesTextEditor.delete('1.0', tkinter.END)

    def updateObserver(self, observable, event):
        """Called when the model object is modified. """
        if observable == self.patientFrameModel:
            self.logger.debug("PatientFrame received from model : " + event)
            try:
                if event == "INIT_DB":
                    self.init()
                elif event == "PATIENT_CHANGED":
                    self.displayOtherPatient()
                elif event == "NEW_PATIENT":
                    self.patientCreated()
                elif event == "PATIENT_UPDATED":
                    self.patientUpdated()
                elif event == "UPDATE_ALL_PATHOLOGIES":
                    self.initListPathologies()
                elif event == "PATIENT_DELETED":
                    self.patientDeleted()

            except ValueError as exc:
                message = _("Error") + " : " + str(exc) + " !"
                self.mainWindow.setStatusText(message, True)

    def initListPathologies(self):
        """ Init Pathologies list content """
        self.pathologiesListbox.delete(0, tkinter.END)
        self.listPathologies = self.patientFrameModel.getAllPathologies()
        for pathology in self.listPathologies:
            self.pathologiesListbox.insert(tkinter.END, pathology)

    def modifyPatient(self, *dummy):
        """ Modify patient info in database """
        try:
            listInfoPatient = [self.patientCodeVar.get(), self.birthYearCombobox.get(),
                               self.genderVar.get(), self.sizeCombobox.get(),
                               self.patientNotesTextEditor.get('1.0', 'end-1c')]
            self.patientFrameModel.createOrModifyPatient(listInfoPatient)
        except ValueError as exc:
            self.mainWindow.setStatusText(_("Error") + " : " + str(exc) + " !", True)

    def deletePatient(self):
        """ Delete patient info in database """
        isDestructionOk = messagebox.askyesno(_("Deleting selected user element in database"),
                                      _("Do you really want to delete selection in database ?") + \
                                      "\n" + self.patientCodeVar.get(),
                                      icon='warning')
        if isDestructionOk:
            self.patientFrameModel.deleteCurrentPatient()
        else:
            self.mainWindow.setStatusText(_("Destruction canceled"))

    def init(self):
        """ Initialyse fields from database """
        listCodes = self.patientFrameModel.getAllPatientCodes()
        self.patientCodeCombobox['values'] = listCodes
        self.initListPathologies()

    def clicPathologiesListbox(self, dummy=None):
        """ Add or remove pathologies for this patient """
        selectedIndex = list(self.pathologiesListbox.curselection())
        if len(selectedIndex) > 0:
            listpathologies = set([self.pathologiesListbox.get(index)
                                   for index in selectedIndex])
            self.patientFrameModel.updatePathologies(listpathologies)

    def displayOtherPatient(self):
        """ Update because model said patient has changed """
        patient = self.patientFrameModel.getCurrentPatient()
        self.birthYearCombobox.set(patient.getData("birthYear"))
        self.genderVar.set(patient.getData("gender"))
        self.sizeCombobox.set(patient.getData("size"))
        self.patientNotesTextEditor.delete('1.0', tkinter.END)
        self.patientNotesTextEditor.insert(tkinter.INSERT, patient.getData("notes"))

        listPathologies2Select = patient.getPathologies()
        self.pathologiesListbox.selection_clear(0, tkinter.END)
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
        self.clicPathologiesListbox()

    def patientCreated(self):
        """ Called when model sid that a patient has been created """
        listCodes = self.patientFrameModel.getAllPatientCodes()
        self.patientCodeCombobox['values'] = listCodes
        self.pathologiesListbox.selection_clear(0, tkinter.END)

        self.mainWindow.setStatusText(_("Patient created in database") + " : " +
                                      self.patientCodeVar.get())

    def patientUpdated(self):
        """ Called when model said that current patient has been updated in database """
        self.mainWindow.setStatusText(_("Patient info updated in database") + " : " +
                                      self.patientCodeVar.get())

    def patientDeleted(self):
        """ Called when model said that current patient has been deleted in database """
        self.clearPatientDefinition()
        listCodes = self.patientFrameModel.getAllPatientCodes()
        self.patientCodeCombobox['values'] = listCodes
        self.patientCodeCombobox.set("")
        self.mainWindow.setStatusText(_("Patient deleted in database"))
