# -*- coding: utf-8 -*-
"""
************************************************************************************
Class : PatientFrameModel
Author : Thierry Maillard (TMD)
Date : 27/11/2016 - 1/12/2016

Role : Define the model for Patient frame.

Ref : Design Patterns: Elements of Reusable Object-Oriented Software
Erich Gamma, Richard Helm, Ralph Johnson et John Vlissides
Préface Grady Booch
https://en.wikipedia.org/wiki/Design_Patterns

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
************************************************************************************
"""

import logging
from util import Observable
from . import Patient

class PatientFrameModel(Observable.Observable):
    """ Model for food table, manage access to database and receive commands from GUI """
    def __init__(self, configApp):
        """ Construct an empty patient model """
        super(PatientFrameModel, self).__init__()
        self.configApp = configApp
        self.logger = logging.getLogger(configApp.get('Log', 'LoggerName'))

        self.currentPatient = None
        self.listAllPatientCodes = []
        self.listAllPathologies = []
        self.database = None

    def setDatabase(self, database):
        """ Initialise this model when changing database """
        self.database = database
        self.currentPatient = None
        self.listAllPatientCodes = database.getAllPatientCodes()
        self.listAllPathologies = database.getDefinedPathologiesNames()

        # Notify observers
        self.setChanged()
        self.notifyObservers("INIT_DB")

    def changePatient(self, patientCode):
        """ Change patient of this model """
        if patientCode != "" and \
            (self.currentPatient is None or \
             self.currentPatient.getData("code") != patientCode):
            self.currentPatient = Patient.Patient(self.configApp, self.database, patientCode)
            self.setChanged()
            self.notifyObservers("PATIENT_CHANGED")

    def createOrModifyPatient(self, listInfoPatient):
        """ Create or modify a patient """
        isNewPatient = listInfoPatient[0] not in self.listAllPatientCodes
        if isNewPatient:
            self.currentPatient = Patient.Patient(self.configApp, self.database, listInfoPatient[0],
                                                  listInfoPatient)
            self.listAllPatientCodes = self.database.getAllPatientCodes()
            # Notify observers
            self.setChanged()
            self.notifyObservers("NEW_PATIENT")
        elif self.currentPatient.updateInfo(listInfoPatient):
            self.setChanged()
            self.notifyObservers("PATIENT_UPDATED")

    def getCurrentPatient(self):
        """ Return patient defined here or None if nothing """
        return self.currentPatient

    def getAllPatientCodes(self):
        """ Return all existing patient code in database """
        return self.listAllPatientCodes

    def getAllPathologies(self):
        """ Return all pathologies names in database """
        return self.listAllPathologies

    def updatePathologies(self, listpathologies):
        """ Update pathologies for current patient """
        if self.currentPatient != None and self.currentPatient.updatePathologies(listpathologies):
            self.setChanged()
            self.notifyObservers("UPDATE_PATHOLOGIES_PATIENT")

    def initListPathologies(self):
        """ Update list of pathologies """
        self.listAllPathologies = self.database.getDefinedPathologiesNames()
        self.setChanged()
        self.notifyObservers("UPDATE_ALL_PATHOLOGIES")

    def deleteCurrentPatient(self):
        """ Delete current patient and notify observers """
        if self.currentPatient is not None:
            self.currentPatient.deleteInDatabase()
            self.currentPatient = None
            self.listAllPatientCodes = self.database.getAllPatientCodes()
            self.setChanged()
            self.notifyObservers("PATIENT_DELETED")
