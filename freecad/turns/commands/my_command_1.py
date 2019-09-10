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

from freecad.workbench_starterkit import ICONPATH

class MyCommand1():
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
        'Accel'   : "Shift+1",
        'MenuText': "MyCommand1",
        'ToolTip' : "Test command #1 for Workbench Starter Kit",
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

        print('\n\tRunning My Command 1...')

        App.ActiveDocument.addObject('Part::Box', 'Starter_Box')
        App.ActiveDocument.ActiveObject.Label = 'Starter kit box'
        App.ActiveDocument.recompute()
        Gui.SendMsgToActiveView('ViewFit')

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

Gui.addCommand('MyCommand1', MyCommand1())
