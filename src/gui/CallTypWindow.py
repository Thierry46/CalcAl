# -*- coding: utf-8 -*-
"""
************************************************************************************
File : CallTypWindow.py
Role : Add tooltips to widgets
Usage :
    from gui import CallTypWindow
    CallTypWindow.createToolTip(self.componentsListbox, "Test tooltip")

Ref : http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml
Author : Michael Foord
Modified : 26/4/2016 - 27/4/2016 : TMD
   - Adapt to python 3 : from Tkinter import * -> from tkinter import *
   - Correction : self.widget.bbox("insert") -> self.widget.bbox("active")
   - Hide tooltip after a delay in ms
       - Add parameter delayms : Delay after what tooltip is hidden
       - Use self.widget.after(self.delayms, self.hidetip) to hide tooltip after delay
   - Ignore exception TypeError in self.widget.bbox("active") instruction
   - Documentation
************************************************************************************
"""

from tkinter import *

class ToolTip(object):

    def __init__(self, widget, delayms):
        self.widget = widget
        self.delayms = delayms
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return

        try:
            x, y, cx, cy = self.widget.bbox("active")
            x = x + self.widget.winfo_rootx() + 27
            y = y + cy + self.widget.winfo_rooty() + 27
            self.tipwindow = tw = Toplevel(self.widget)
            # Prevent Windows Manager to decorate this Toplevel objet
            # It will not have a title or a border, and cannot be moved or closed via ordinary means
            tw.wm_overrideredirect(1)
            tw.wm_geometry("+%d+%d" % (x, y))
            try:
                # For Mac OS
                tw.tk.call("::tk::unsupported::MacWindowStyle",
                           "style", tw._w,
                           "help", "noActivates")
            except TclError:
                pass
            label = Label(tw, text=self.text, justify=LEFT,
                          background="#ffffe0", relief=SOLID, borderwidth=1,
                          font=("tahoma", "12", "normal"))
            label.pack(ipadx=1)
            self.widget.after(self.delayms, self.hidetip)
        except TypeError:
            pass

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def createToolTip(widget, text, delayms):
    """ 
        Create and attach a tooltip to a widget
        widget : The widget to attach the tooltip
        Text : Text to display in tooltip
        delayms : int : delay in ms after what tooltip will disappear
    """

    toolTip = ToolTip(widget, delayms)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)
