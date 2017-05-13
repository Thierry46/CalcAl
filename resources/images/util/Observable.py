# -*- coding: utf-8 -*-
"""
************************************************************************************
Classe : Observable
Usage  : Lors de l'implémentation du design pattern Modèle-Vue-controler
    les classes modèle doivent être dérivées de cette classe pour
    pouvoir communiquer avec leurs observateurs
    qui doivent possèder une méthode update appelée lors d'un changement dans le
    modèle. Cette méthode devra interroger le modèle pour connaître quels sont ses
    changements.

Origine du code : Adaptation à python de la classes Java : java.util.Observable
    de : http://python-3-patterns-idioms-test.readthedocs.org/en/latest/Contributors.html
    http://python-3-patterns-idioms-test.readthedocs.org/en/latest/Observer.html
    Simplifié sans prise en compte synchronisation des Threads.

Ref : Design Patterns: Elements of Reusable Object-Oriented Software
Erich Gamma, Richard Helm, Ralph Johnson et John Vlissides
Préface Grady Booch
https://en.wikipedia.org/wiki/Design_Patterns

2/12/2016 : Replace update name with updateObserver to avoid conflicts with
    tkinter update method.
************************************************************************************
"""

class Observable(object):
    """ Define method  for observable in MVC design pattern """
    def __init__(self):
        """ Init list of observer and change flag """
        self.obs = []
        self.changed = False

    def addObserver(self, observer):
        """ Add the calling observer to the list of observer of this observable """
        if observer not in self.obs:
            self.obs.append(observer)

    def deleteObserver(self, observer):
        """ Remove observer from the list of observer of this observable """
        self.obs.remove(observer)

    def notifyObservers(self, arg=None):
        """If 'changed' indicates that this object
        has changed, notify all its observers, then
        call clearChanged(). Each observer has its
        updateObserver() called with two arguments: this
        observable object and the generic 'arg'."""
        if self.changed:
            for observer in self.obs:
                observer.updateObserver(self, arg)
            self.clearChanged()

    def deleteObservers(self):
        """ Remove all observers from the list of observer of this observable """
        self.obs = []

    def setChanged(self):
        """ Set change flag """
        self.changed = True

    def clearChanged(self):
        """ Clear change flag """
        self.changed = False

    def hasChanged(self):
        """ Get change flag """
        return self.changed

    def countObservers(self):
        """ Return the number of observers registred on this model """
        return len(self.obs)
