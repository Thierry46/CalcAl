# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : TkSimpleDialog.py
Role : Modal dialog box base constructor (should be overridden)
Source : http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
Modified by TMD : 30/5/2016 - 1/6/2016
************************************************************************************
"""
from tkinter import *

class TkSimpleDialog(Toplevel):
    """ Modal dialog box base constructor (should be overridden) """
    def __init__(self, parent, title=None):
        """ Construct this modal frame """
        super(TkSimpleDialog, self).__init__(parent)
        self.parent = parent
        self.result = None
        #self = Toplevel(parent)
        self.transient(parent)

        if title:
            self.title(title)
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox(self)

        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        x, y, cx, cy = self.parent.bbox("active")
        x = x + self.parent.winfo_rootx() + 27
        y = y + cy + self.parent.winfo_rooty() + 27
        self.wm_geometry("+%d+%d" % (x, y))

        self.initial_focus.focus_set()
        # The wait_window method enters a local event loop, and doesn’t return
        # until the given window is destroyed (either via the destroy method,
        # or explicitly via the window manager)
        self.parent.wait_window(self)

    def buttonbox(self, master):
        """ add standard button box. override if you don't want the
            standard buttons """

        box = Frame(master)

        w = Button(box, text=_("OK"), width=10, command=self.ok, default=ACTIVE)
        w.pack(side=LEFT, padx=5, pady=5)
        w = Button(box, text=_("Cancel"), width=10, command=self.cancel)
        w.pack(side=LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()
    #
    # standard button semantics

    def ok(self, event=None):
        """ Ok button pressed : prepare data returned for user """
        if not self.validate():
            self.initial_focus.focus_set() # put focus back to parent widget
        else:
            self.apply()
            self.withdraw()
            self.parent.update_idletasks()
            self.cancel()

    def cancel(self, event=None):
        """ Put focus back to the parent window """
        self.parent.focus_set()
        self.destroy()

    #########################
    # Method to be orridden
    #########################

    # Construction hook
    def body(self, master):
        """ create dialog body.  return widget that should have
            initial focus.  this method should be overridden """
        pass

    # command hooks to override
    def validate(self):
        """ Validation function that return True, must be overriden """
        return True

    def apply(self):
        """ Prepare results, must be overriden """
        pass

    def setResult(self, result):
        """ Prepare results """
        self.result = result

    def getResult(self):
        """ Return results collected by this dialog """
        return self.result
