# -*- coding: utf-8 -*-
"""
************************************************************************************
File : CallTypWindow.py
Role : Add tooltips to widgets
Usage :
    from . import CallTypWindow
    CallTypWindow.createToolTip(self.componentsListbox, "Test tooltip")

Ref : http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml
Author : Michael Foord
Modified : 26/4/2016 - 27/4/2016 : TMD
   - Adapt to python 3
   - Correction : self.widget.bbox("insert") -> self.widget.bbox("active")
   - Hide tooltip after a delay in ms
       - Add parameter delayms : Delay after what tooltip is hidden
       - Use self.widget.after(self.delayms, self.hidetip) to hide tooltip after delay
   - Ignore exception TypeError in self.widget.bbox("active") instruction
   - Documentation

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

class ToolTip(object):
    """ Add tooltips to widgets """
    def __init__(self, widget, delayms):
        """ Tooltip constructor """
        self.widget = widget
        self.delayms = delayms
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.text = ""

    def showtip(self, text):
        """Display text in tooltip window"""
        self.text = text
        if self.tipwindow or not self.text:
            return

        try:
            x, y, dummy, yLenght = self.widget.bbox("active")
            x = x + self.widget.winfo_rootx() + 27
            y = y + yLenght + self.widget.winfo_rooty() + 27
            self.tipwindow = tkinter.Toplevel(self.widget)
            # Prevent Windows Manager to decorate this Toplevel objet
            # It will not have a title or a border, and cannot be moved or closed via ordinary means
            self.tipwindow.wm_overrideredirect(1)
            self.tipwindow.wm_geometry("+%d+%d" % (x, y))
            try:
                # For Mac OS
                self.tipwindow.tk.call("::tk::unsupported::MacWindowStyle",
                                       "style", self.tipwindow._w,
                                       "help", "noActivates")
            except tkinter.TclError:
                pass
            label = tkinter.Label(self.tipwindow, text=self.text, justify=tkinter.LEFT,
                                  background="#ffffe0", relief=tkinter.SOLID, borderwidth=3,
                                  font=("comic Sans MS", "12", "normal"))
            label.pack(ipadx=1)
            self.widget.after(self.delayms, self.hidetip)
        except TypeError:
            pass

    def hidetip(self):
        """ Destroy tooltip window """
        tipwindow = self.tipwindow
        self.tipwindow = None
        if tipwindow:
            tipwindow.destroy()

def createToolTip(widget, text, delayms):
    """
        Create and attach a tooltip to a widget
        widget : The widget to attach the tooltip
        Text : Text to display in tooltip
        delayms : int : delay in ms after what tooltip will disappear
    """
    toolTip = ToolTip(widget, delayms)
    def enter(dummy):
        """ Called when enter in widget """
        toolTip.showtip(text)
    def leave(dummy):
        """ Called when leave widget """
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
