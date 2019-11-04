# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************

"""
Base Task class
"""

import types

from PySide import QtGui

import FreeCADGui as Gui

class BaseTask():
    """
    Base Task class
    """

    @staticmethod
    def getMainWindow():
        """
        Return reference to main window
        """
        top = QtGui.QApplication.topLevelWidgets()

        for item in top:
            if item.metaObject().className() == 'Gui::MainWindow':
                return item

        raise RuntimeError('No main window found')

    def __init__(self, panel_filepath):
        """
        Constructor
        """

        self.panel = None
        self.ui = panel_filepath
        self.widgets = []

    def setup(self):
        """
        Initiailze the task window and controls.
        Override in inheriting class (optional)
        """

        #get a reference to the QWidget of the task panel
        self.panel = \
            BaseTask.getMainWindow().findChild(QtGui.QWidget, 'TaskPanel')

        if not self.widgets:
            return

        #build a dict keyed to the control name which stores a SimpleNameSpace
        #object to store
        self.panel.widgets = {}

        for _v in self.widgets:

            self.panel.widgets[_v[0]] = types.SimpleNamespace(
                reference=self.panel.findChild(QtGui.QWidget, _v[0]),
                signal=_v[1],
                callback=_v[2]
            )

        #connect the widget signals to the assicated callbacks
        for _v in self.panel.widgets.values():
            getattr(_v.reference, _v.signal).connect(_v.callback)

    def accept(self):
        """
        Accept the task parameters.  Override in inheriting class.
        """

        self.finish()

        return None

    def reject(self):
        """
        Reject the task.  Override in inheriting class.
        """

        self.finish()

        return None

    def finish(self):
        """
        Task cleanup
        """

        #close dialog
        Gui.Control.closeDialog()

        #delete control referecnes
        self.panel.widgets.clear()
        self.panel = None
