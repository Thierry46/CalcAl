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
************************************************************************************
"""

class Observable(object):
    def __init__(self):
        self.obs = []
        self.changed = False

    def addObserver(self, observer):
        if observer not in self.obs:
            self.obs.append(observer)

    def deleteObserver(self, observer):
        self.obs.remove(observer)

    def notifyObservers(self, arg = None):
        """If 'changed' indicates that this object
        has changed, notify all its observers, then
        call clearChanged(). Each observer has its
        update() called with two arguments: this
        observable object and the generic 'arg'."""
        if self.changed:
            for observer in self.obs:
                observer.update(self, arg)
            self.clearChanged()

    def deleteObservers(self):
        self.obs = []

    def setChanged(self):
        self.changed = True

    def clearChanged(self):
        self.changed = False

    def hasChanged(self):
        return self.changed

    def countObservers(self):
        return len(self.obs)
