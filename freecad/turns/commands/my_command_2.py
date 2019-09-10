# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) XXXX FreeCAD Author <freecad_author@gmail.com>               *
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
Example Command
"""
import os

import FreeCAD as App
import FreeCADGui as Gui

from PySide import QtGui

from freecad.workbench_starterkit import ICONPATH

class MyCommand2():
    """
    Example Command
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Resource definition allows customization of the command icon,
    # hotkey, text, tooltip and whether or not the command is active
    # when a task panel is open
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    resources = {
        'Pixmap'  : os.path.join(ICONPATH, "template_resource.svg"),
        'Accel'   : "Shift+2",
        'MenuText': "MyCommand2",
        'ToolTip' : "Test command #2 for Workbench Starter Kit",
        'CmdType' : "ForEdit"
    }

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return self.resources

    def Activated(self):
        """
        Activation callback
        """

        #_mw = self.getMainWindow()

        #self.form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        print('\n\tRuning My Command 2...')
        print('\n\tUser chose file: ' + self.choose_file())

    def IsActive(self):
        """
        Returns always active
        """

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # IsActive allows the command icon / menu item to be enabled
        # or disabled depending on various conditions.
        #
        # Here, the command is only enabled if a document is open.
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        return App.ActiveDocument is not None

    def getMainWindow(self):
        """
        Return reference to main window
        """
        top = QtGui.QApplication.topLevelWidgets()

        for item in top:
            if item.metaObject().className() == 'Gui::MainWindow':
                return item

        raise RuntimeError('No main window found')

    def choose_file(self):
        """
        Open the file picker dialog and open the file
        that the user chooses
        """

        open_path = ICONPATH

        file_name = QtGui.QFileDialog.getOpenFileName(
            None, 'Select File', open_path
        )

        return file_name[0]

Gui.addCommand('MyCommand2', MyCommand2())
