"""
    ************************************************************************************
    Classe : Observer
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
class Observer:
    def update(self, observable, arg):
        """Called when the observed object is
            modified. You call an Observable object's
            notifyObservers method to notify all the
            object's observers of the change.

            Abstract methode that subclass must implement
            """
        raise Exception("NotImplementedException")
