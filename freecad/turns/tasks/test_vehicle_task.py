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
Example task template
"""

import FreeCAD as App

from PySide.QtGui import QStyle

import FreeCADGui as Gui

from .. import resources

from ..commands.path_editor_command import PathEditorCommand
from ..trackers.analysis_tracker import AnalysisTracker

from .base_task import BaseTask

class TestVehicleTask(BaseTask):
    """
    Test vehicle task template
    """

    def __init__(self):
        """
        Constructor
        """

        self.name = 'TestVheicleTask'
        #initialize the inherited base class
        super().__init__(resources.__path__[0] + '/test_vehicle.ui')

        #Initialize state that will be global to the task here
        self.view = Gui.ActiveDocument.ActiveView
        self.path_editor = PathEditorCommand()

        # define the widget signalling data tuples as:
        # (widget_name, widget_signal_name, callback)
        self.widget_callbacks = [
            ('loop_checkbox', 'stateChanged', self.loop_checkbox_cb),
            ('animation_speed_slider', 'valueChanged', self.speed_slider_cb),
            ('create_path_button', 'clicked', self.create_edit_path_cb),
            ('edit_path_button', 'clicked', self.create_edit_path_cb),
            ('path_combo', 'currentIndexChanged', self.path_cb),
            ('angle_edit', 'editingFinished', self.angle_cb),
            ('radius_edit', 'editingFinished', self.radius_cb),
            ('max_steps_edit', 'editingFinished', self.max_steps_cb),
            ('cur_step_edit', 'editingFinished', self.cur_step_cb),
            ('back_button', 'clicked', self.step_back_cb),
            ('play_button', 'clicked', self.play_cb),
            ('forward_button', 'clicked', self.step_forward_cb)
        ]

        self.is_playing = False
        self.tracker = AnalysisTracker()
        self.tracker.insert_into_scenegraph()

    def setup_ui(self):
        """
        Additional UI intialization code
        """

        _sel = Gui.Selection.getSelection()

        super().setup_ui()

        #button references
        _play = self.widgets.play_button
        _forward = self.widgets.forward_button
        _back = self.widgets.back_button

        #button icons
        _play.setIcon(_play.style().standardIcon(QStyle.SP_MediaPlay))
        _forward.setIcon(
            _forward.style().standardIcon(QStyle.SP_MediaSeekForward))

        _back.setIcon(_back.style().standardIcon(QStyle.SP_MediaSeekBackward))

        #populate the path combobox
        for _o in App.ActiveDocument.Objects:
            if _o.isDerivedFrom('Sketcher::SketchObject'):
                self.widgets.path_combo.addItem(_o.Name)

        #set the current path in the analyzer to a pre-selected object
        if _sel and _sel[0].isDerivedFrom('Sketcher::SketchObject'):
            _idx = self.widgets.path_combo.findText(_sel[0].Name)
            self.widgets.path_combo.setCurrentIndex(_idx)

        self.widgets.max_steps_edit.setInputMask("999")
        self.widgets.cur_step_edit.setInputMask("999")

        print(self.widgets.cur_step_edit.text())
        self.tracker.set_step(
            int(self.widgets.cur_step_edit.text())
        )

        self.max_steps_cb(100)
        self.path_cb(0)
        self.speed_slider_cb(3)

    def loop_checkbox_cb(self, value):
        """
        Callback for loop checkbox state
        """

        self.tracker.set_animation_loop(self.widgets.loop_checkbox.isChecked())

    def create_edit_path_cb(self):
        """
        Edit an existing sketch path
        """

        self.path_editor.Activated()

    def speed_slider_cb(self, value):
        """
        Callback for changes to the animation slider position
        """

        if not value:
            value = 1

        else:
            value *= 5

        self.tracker.set_animation_speed(value)

    def path_cb(self, value):
        """
        Callback for path combobox (currentIndexChanged)
        """

        _name = self.widgets.path_combo.currentText()

        if not _name:
            return

        Gui.Selection.clearSelection()

        _sketch = App.ActiveDocument.getObject(_name)

        if not _sketch:
            return

        Gui.Selection.addSelection(_sketch)

        self.tracker.set_path(_sketch.Geometry)

    def angle_cb(self):
        """
        Callback for vehicle max steering angle line edit
        """

        print('angle_cb')

    def radius_cb(self):
        """
        Callback for vehicle min turning radius line edit
        """

        print('radius_cb')

    def max_steps_cb(self, value):
        """
        Callback for maximum steps line edit
        """

        self.tracker.set_max_steps(int(value))

    def cur_step_cb(self, value):
        """
        Callback for current step line edit
        """

        self.tracker.set_step(int(value))

    def step_forward_cb(self):
        """
        Step forward callback
        """

        self.tracker.move_step(1)

    def step_back_cb(self):
        """
        Step backward callback
        """

        self.tracker.move_step(-1)

    def play_cb(self):
        """
        Play simulation callback
        """

        _icon = QStyle.SP_MediaPlay

        if self.is_playing:
            self.tracker.stop_animation()

        else:
            self.tracker.start_animation()
            _icon = QStyle.SP_MediaStop

        self.is_playing = not self.is_playing

        _play = self.widgets.play_button
        _play.setIcon(_play.style().standardIcon(_icon))

    def accept(self):
        """
        Overrides base implementation (optional)
        """

        super().accept()

    def reject(self):
        """
        Overrides base implementation (optional)
        """

        super().reject()
