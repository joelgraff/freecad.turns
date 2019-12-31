# -*- coding: utf-8 -*-
#***********************************************************************
#* Copyright (c) XXXX FreeCAD Author <freecad_author@gmail.com>        *
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
DrawPath Command
"""
import os

from PySide import QtGui

import FreeCAD as App
import FreeCADGui as Gui

from freecad.turns import ICONPATH

class PathEditorCommand():
    """
    PathEditor Command - launches sketcher to create a new path.
    """

    resources = {
        'Pixmap'  : os.path.join(ICONPATH, "template_resource.svg"),
        'Accel'   : "Shift+1",
        'MenuText': "Create / Edit Path",
        'ToolTip' : "Create / Edit Path Command",
        'CmdType' : "ForEdit"
    }

    def GetResources(self):
        """
        Return the command resources dictionary
        """
        return self.resources

    def Activated(self):
        """
        Activation callback - create / edit a sketch
        """

        _sel = Gui.Selection.getSelection()

        #edit an existing sketch, if selected
        if _sel:

            if _sel[0].isDerivedFrom('Sketcher::SketchObject'):

                if Gui.Control.activeDialog():
                    Gui.Control.closeDialog()

                Gui.runCommand('Sketcher_EditSketch')
                return

            Gui.Selection.clearSelection()

        #otherwise, create a new sketch
        _path = QtGui.QInputDialog.getText(
            None, 'Create New Path', 'Path name:')[0]

        if not _path:
            return

        if Gui.Control.activeDialog():
            Gui.Control.closeDialog()

        App.ActiveDocument.addObject('Sketcher::SketchObject', _path)
        Gui.ActiveDocument.setEdit(_path)
        App.ActiveDocument.recompute()

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

Gui.addCommand('PathEditorCommand', PathEditorCommand())
