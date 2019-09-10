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

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  First Things First
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  --- Copyrights ---
#
#  Here at the top of the module, it's good practice to always add
#  the license text.  Add your name and email, if desired.
#  Date is optional and reflects the date of first publication *only*.
#
#  --- Globals ----
#
#  Per standard Python practice, imports are located at the top of the
#  file, with the exception of workbench commands - more later on that.
#
#  Also note the use of the TEMPLATEWB_VERSION constant.  This provides
#  a quick, easy way to version your workbench and makes it easy for
#  a user to know which version they're running.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import FreeCADGui as Gui
import FreeCAD as App
from freecad.workbench_starterkit import ICONPATH

#use this to track workbench versioning
TEMPLATEWB_VERSION = '(alpha)'

class template_workbench(Gui.Workbench):
    """
    class which gets initiated at starup of the gui
    """

    #Constants for UI locations for toolboxes
    MENU = 1
    TOOLBAR = 2
    CONTEXT = 4

    #Workbench GUI-specific attributes
    MenuText = "Template Workbench" + TEMPLATEWB_VERSION
    ToolTip = "An example template workbench"
    Icon = os.path.join(ICONPATH, "template_resource.svg")
    toolbox = []

    def __init__(self):
        """
        Constructor
        """

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The Command Dictionary
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This dictionary provides a straight-forward, easy way to 
# manage workbench commands.  It contains a list of all command
# toolboxes and the locations in the UI where they appear.
#
# The top-level items are dictionaries which represent a toolbox
# to which commands may be assigned.  
# 
# The 'gui' value determines the UI locations in which a
# toolbox appears.
#
# The 'cmd' list contains the names of all commands which are
# assigned to that toolbox.  Commands may be assigned to
# multiple toolboxes.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        self.command_ui = {

            'StarterKit': {
                'gui': self.MENU,
                'cmd': ['MyCommand1', 'MyCommand2', 'MyCommand3']
            },

            'Files': {
                'gui': self.TOOLBAR,
                'cmd': ['MyCommand2']
            },

            'Geometry': {
                'gui': self.TOOLBAR + self.CONTEXT,
                'cmd': ['MyCommand1', 'MyCommand3']
            },
        }

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        Import commands here
        """

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  Starting Up
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#  When the workbench is first activated (the user explicitly attempts
#  to load it), the commands are loaded.
#
#  Placing imports here, rather than at the top of the file, defers
#  additional loading when FreeCAD starts, as all workbench classes are
#  constructed then.
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        #import commands here to be added to the user interface
        from freecad.workbench_starterkit import my_numpy_function

        from .commands import my_command_1, my_command_2, my_command_3

        #iterate the command toolboxes defined in __init__() and add
        #them to the UI according to the assigned location flags
        for _k, _v in self.command_ui.items():

            if _v['gui'] & self.TOOLBAR:
                self.appendToolbar(_k, _v['cmd'])

            if _v['gui'] & self.MENU:
                self.appendMenu(_k, _v['cmd'])

        self.appendToolbar("Tools", self.toolbox)
        self.appendMenu("Tools", self.toolbox)

        #Feel free to add diagnostic code or other start-up related
        #activities...
        App.Console.PrintMessage("\n\tSwitching to workbench_starterkit")

        App.Console.PrintMessage(
            "\n\trun a numpy function: sqrt(100) = {}".format(my_numpy_function.my_foo(100))
        )

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

Gui.addWorkbench(template_workbench())
