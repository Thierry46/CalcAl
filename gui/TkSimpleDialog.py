# -*- coding: utf-8 -*-
"""
************************************************************************************
Name : TkSimpleDialog.py
Role : Modal dialog box base constructor (should be overridden)
Source : http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
Modified by TMD : 30/5/2016 - 1/6/2016

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
import tkinter

class TkSimpleDialog(tkinter.Toplevel):
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
        body = tkinter.Frame(self)
        self.initialFocus = self.body(body)
        body.pack(padx=5, pady=5)
        self.buttonbox(self)

        self.grab_set()
        if not self.initialFocus:
            self.initialFocus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        x, y, dummy, yLength = self.parent.bbox("active")
        x = x + self.parent.winfo_rootx() + 27
        y = y + yLength + self.parent.winfo_rooty() + 27
        self.wm_geometry("+%d+%d" % (x, y))

        self.initialFocus.focus_set()
        # The wait_window method enters a local event loop, and doesn’t return
        # until the given window is destroyed (either via the destroy method,
        # or explicitly via the window manager)
        self.parent.wait_window(self)

    def buttonbox(self, master):
        """ add standard button box. override if you don't want the
            standard buttons """

        box = tkinter.Frame(master)

        tkinter.Button(box, text=_("OK"), width=10,
                       command=self.okCallback, default=tkinter.ACTIVE
                       ).pack(side=tkinter.LEFT, padx=5, pady=5)
        tkinter.Button(box, text=_("Cancel"), width=10, command=self.cancel
                      ).pack(side=tkinter.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.okCallback)
        self.bind("<Escape>", self.cancel)

        box.pack()
    #
    # standard button semantics

    def okCallback(self, dummy=None):
        """ Ok button pressed : prepare data returned for user """
        if not self.validate():
            self.initialFocus.focus_set() # put focus back to parent widget
        else:
            self.apply()
            self.withdraw()
            self.parent.update_idletasks()
            self.cancel()

    def cancel(self, dummy=None):
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
