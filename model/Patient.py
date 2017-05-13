# -*- coding: utf-8 -*-
"""
************************************************************************************
Class : Patient
Author : Thierry Maillard (TMD)
Date : 28/11/2016 - 1/12/2016

Role : Define a Patient.

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
import re
import datetime

from model import ModelBaseData
from util import CalcalExceptions

class Patient(ModelBaseData.ModelBaseData):
    """ Model for Patient
        2 way for building :
            from database if listInfoPatient is None
            else from a list of given values
        """
    def __init__(self, configApp, database, patientCode, listInfoPatient=None):
        """ Minimal constructor """
        super(Patient, self).__init__(configApp, database, _("Patient"))
        self.database = database
        self.dictComponents = dict()
        self.listPathologies = set()

        self.codeRegexPatient = configApp.get('Patient', 'codeRegex')
        self.currentYear = datetime.datetime.now().year
        self.oldestPatient = int(configApp.get('Patient', 'oldestPatient'))
        self.sizeMin = int(configApp.get('Patient', 'sizeMin'))
        self.sizeMax = int(configApp.get('Patient', 'sizeMax'))

        if listInfoPatient is None:
            self.update(self.database.getInfoPatient(patientCode))
            self.listPathologies = self.database.getPathologies4Patient(patientCode)
        else:
            self.checkFields(listInfoPatient, isModified=True)
            self.setData("code", listInfoPatient[0])
            self.setData("birthYear", int(listInfoPatient[1]))
            self.setData("gender", listInfoPatient[2])
            self.setData("size", float(listInfoPatient[3].replace(",", ".")))
            self.setData("notes", listInfoPatient[4])
            self.database.insertPatientInDatabase(listInfoPatient)
            self.logger.debug(_("Created in model from list") + str(self))

    def getAllMonitorings4ThisPatient(self):
        """ Return a list (date, dict(param)=value """

    def checkFields(self, listInfoPatient, isModified):
        """ Check fields to insert for the patient described in listInfoPatient
            if not isModified, check if a change control of this object must be done
            Return True if this patient is modified according imput data """
        assert len(listInfoPatient) == 5, \
                "Patient/checkFields() : listInfoPatient must have 5 fields"
        codePatient = listInfoPatient[0].upper()
        if re.match(self.codeRegexPatient, codePatient) is None:
            raise CalcalExceptions.CalcalValueError(self.configApp,
                  _("Patient code must be 3 capital letters followed by 3 digits"))
        isModified = isModified or codePatient != self.getData("code")

        birthYear = int(listInfoPatient[1])
        age = self.currentYear - birthYear
        if age < 0 or age > self.oldestPatient:
            raise CalcalExceptions.CalcalValueError(self.configApp,
                  _("Patient age must be in") + " [0;" + str(self.oldestPatient) + "]")
        isModified = isModified or birthYear != self.getData("birthYear")

        gender = listInfoPatient[2]
        if gender not in "MFU":
            raise CalcalExceptions.CalcalValueError(self.configApp,
                  _("Patient gender must be M F or U"))
        isModified = isModified or gender != self.getData("gender")

        size = int(listInfoPatient[3])
        if size < self.sizeMin or size > self.sizeMax:
            raise CalcalExceptions.CalcalValueError(self.configApp,
                                                    _("Patient size must be in") + " [" +
                                                    str(self.sizeMin) + ";" + str(self.sizeMax) +
                                                    "] cm")
        isModified = isModified or size != self.getData("size")

        notes = listInfoPatient[4]
        isModified = isModified or notes != self.getData("notes")

        self.logger.debug("Patient/checkFields() : isModified = " + str(isModified))
        return isModified

    def updateInfo(self, listInfoPatient):
        """ Update fields for this patient """
        isModified = self.checkFields(listInfoPatient, isModified=False)
        if isModified:
            self.database.updatePatientInDatabase(listInfoPatient)
        return isModified

    def updatePathologies(self, listpathologies):
        """ Update pathologies for this patient
            Return True if pathologies have changed """
        isModified = (listpathologies != self.listPathologies)
        if isModified:
            self.database.updatePatientPathologies(self.getData("code"), listpathologies)
            self.listPathologies = listpathologies
        return isModified

    def getPathologies(self):
        """ Return a list of pathologies for this patient """
        return self.listPathologies

    def deleteInDatabase(self):
        """ Delete this patient in database """
        self.database.deletePatient(self.getData("code"))
