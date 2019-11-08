#/**********************************************************************
#*                                                                     *
#* Copyright (c) XXXX FreeCAD AUthor <freecad_author@gmail.com>               *
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
GUI Initialization module
"""

import os

import FreeCADGui as Gui

from freecad.turns import ICONPATH

#use this to track workbench versioning
TURNS_WB_VERSION = '(alpha)'

class TurnsWorkbench(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """

    #Constants for UI locations for toolboxes
    MENU = 1
    TOOLBAR = 2
    CONTEXT = 4

    #Workbench GUI-specific attributes
    MenuText = "Turns Workbench" + TURNS_WB_VERSION
    ToolTip = "FreeCAD Truns Swept Path Analysis Workbench"
    Icon = os.path.join(ICONPATH, "template_resource.svg")
    toolbox = []

    def __init__(self):
        """
        Constructor
        """

        self.command_ui = {

            'Turns': {
                'gui': self.MENU + self.TOOLBAR,
                'cmd': ['TestVehicleCommand']
            }
        }

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        Import commands here
        """

        #import commands here to be added to the user interface
        from .commands import test_vehicle_command

        #iterate the command toolboxes defined in __init__() and add
        #them to the UI according to the assigned location flags
        for _k, _v in self.command_ui.items():

            if _v['gui'] & self.TOOLBAR:
                self.appendToolbar(_k, _v['cmd'])

            if _v['gui'] & self.MENU:
                self.appendMenu(_k, _v['cmd'])

        self.appendToolbar("Tools", self.toolbox)
        self.appendMenu("Tools", self.toolbox)

    def Activated(self):
        """
        Workbench activation occurs when switched to
        """
        pass

    def Deactivated(self):
        """
        Workbench deactivation occurs when switched away from in the UI
        """
        pass

    def ContextMenu(self, recipient):
        """
        Right-click menu options
        """

        #Populate the context menu when it's called
        for _k, _v in self.command_ui.items():
            if _v['gui'] & self.CONTEXT:
                self.appendContextMenu(_k, _v['cmd'])

Gui.addWorkbench(TurnsWorkbench())
