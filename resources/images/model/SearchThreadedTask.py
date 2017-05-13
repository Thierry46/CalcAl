# -*- coding: utf-8 -*-
"""
************************************************************************************
Class : SearchThreadedTask
Author : Thierry Maillard (TMD)
Date : 2/1/2017

Role : Define a Threaded that search Food in database.
    in association with SearchFoodFrame

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
import threading

from model import Component
from database import Database

class SearchThreadedTask(threading.Thread):
    """ V0.31 : Thread used to search food in database without blocking GUI """
    def __init__(self, parent, queue, endMarker, listFilters):
        """ Initialize this Search Thread :
            parent : Parent id for accessing parent information
            queue : queue to send messagesto parent GUI
            endMarker : string to put in last message
            """
        threading.Thread.__init__(self)
        self.queue = queue
        self.parent = parent
        self.endMarker = endMarker
        self.listFilters = listFilters
        self.formatFloatValue = "{0:." + self.parent.configApp.get('Limits', 'nbMaxDigit') + "f}"

    def run(self):
        self.runSearch()

    def runSearch(self):
        """ Search foodstuffs in database that math filters,
            communicate with thead parents with a queue
            Maybe problem because it update search result table in parentsthread """
        nbMaxResultSearch = int(self.parent.configApp.get('Limits', 'nbMaxResultSearch'))

        # Database must be reopen in this thread
        databasePath = self.parent.databaseManager.getDatabase().getDatabasePath()
        database = Database.Database(self.parent.configApp, self.parent.dirProject)
        database.open(databasePath)

        try:
            self.queue.put(_("Searching in database") + "...")

            # Get all product selected by filters
            listDictProductValues = database.getProductComponents4Filters(self.listFilters,
                                                                           self.queue)

            # Intersection all dictionaries keys to get only common keys
            intersectKeys = set()
            index = 0
            for dictProductValues in listDictProductValues:
                if index == 0:
                    intersectKeys = dictProductValues.keys()
                else:
                    intersectKeys &= dictProductValues.keys()
                index += 1

            messageproductsCondition = _("intersection") + " : " +  str(len(intersectKeys))
            self.queue.put(messageproductsCondition)

            # Build a list One line  per products : list [products,[listCompvalue formated]]
            # Components are ordered according fistFilter
            listComp = [filter[0] for filter in self.listFilters]
            listProductsFormatedComponents = []
            nbFoundProducts = 0
            for product in intersectKeys:
                listCompValues = []
                for codeComp in listComp:
                    for dictProductValues in listDictProductValues:
                        if dictProductValues[product][0] == codeComp:
                            qualifier = dictProductValues[product][1]
                            value = dictProductValues[product][2]
                            formatValue = Component.Component.getValueFormatedStatic(self.parent.configApp,
                                                                                 qualifier, value)
                            listCompValues.append(formatValue)
                            break # Component can be in 2 dict if asked twice by user : take only the first
                listProductsFormatedComponents.append([product, listCompValues])
                if nbFoundProducts > nbMaxResultSearch:
                    break
                nbFoundProducts += 1

            # Update table content with results
            self.parent.searchResultTable.insertGroupRow(listProductsFormatedComponents)

            # Check number of results and send final message
            message = self.endMarker + " : "
            if nbFoundProducts > nbMaxResultSearch:
                message += _("Too many results") +" : " + str(nbMaxResultSearch) + \
                          " " + _("on") + " " + str(len(intersectKeys)) + " " + _("displayed") + \
                          ". " + _("Please improve filters") + " !"
            else:
                message += str(nbFoundProducts) + " " + _("results matching filters")
            self.queue.put(message)
        except ValueError as exc:
            self.queue.put(_("Error") + " : " + str(exc) + " !")
        finally:
            database.close()
