# -*- coding: utf-8 -*-
#***********************************************************************
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
Swept path analysis task
"""

import FreeCAD as App

from PySide.QtGui import QStyle

import FreeCADGui as Gui

from .. import resources

from ..commands.path_editor_command import PathEditorCommand
from ..trackers.project.analysis_tracker import AnalysisTracker
from ..model.vehicle import Vehicle

from .base_task import BaseTask

class AnalysisTask(BaseTask):
    """
    Swept path analysis task
    """

    def __init__(self):
        """
        Constructor
        """

        self.name = 'SweptPathAnalysisTask'

        #initialize the inherited base class
        super().__init__(resources.__path__[0] + '/analysis.ui')

        #Initialize state that will be global to the task here
        self.view = Gui.ActiveDocument.ActiveView
        self.path_editor = PathEditorCommand()

        # define the widget signalling data tuples as:
        #(widget_name, widget_signal_name, callback)
        self.widget_callbacks = {

            'loop_checkbox': ('stateChanged', self.fr_loop_checkbox, None),

            'animation_speed_slider':\
                ('valueChanged', self.fr_speed_slider, None),

            'create_path_button': ('clicked', self.fr_create_edit_path, None),
            'edit_path_button': ('clicked', self.fr_create_edit_path, None),
            'path_combo': ('currentIndexChanged', self.fr_path, None),
            'type_combo': ('currentIndexChanged', self.fr_type, None),

            'max_steps_edit': ('editingFinished', self.fr_max_steps, None),

            'cur_step_edit':\
                ('editingFinished', self.fr_cur_step, self.to_cur_step),

            'length_edit': ('', None, self.to_length_edit),
            'width_edit': ('', None, self.to_width_edit),
            'cur_angle_edit': ('', None, self.to_cur_angle),
            'cur_radius_edit': ('', None, self.to_cur_radius),

            'back_button': ('clicked', self.fr_step_back, None),
            'play_button': ('clicked', self.fr_play, None),
            'stop_button': ('clicked', self.fr_stop, None)
        }

        self.is_playing = False

        self.tracker = AnalysisTracker()
        self.tracker.insert_into_scenegraph()

    def setup_ui(self):
        """
        Additional UI intialization code
        """

        _sel = Gui.Selection.getSelection()

        super().setup_ui()

        #set callbacks for tracker to update UI
        self.tracker.to_step = self.to_cur_step
        self.tracker.to_radius = self.to_cur_radius
        self.tracker.to_angle = self.to_cur_angle

        #button references
        _play = self.widgets.play_button
        _stop = self.widgets.stop_button
        _back = self.widgets.back_button

        #button icons
        _play.setIcon(_play.style().standardIcon(QStyle.SP_MediaPlay))
        _stop.setIcon(
            _stop.style().standardIcon(QStyle.SP_MediaStop))

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
        self.tracker.set_step(int(self.widgets.cur_step_edit.text()))

        #populate the vehicle type combo
        for _k, _v in Vehicle.templates.items():
            self.widgets.type_combo.addItem('{} ({})'.format(_k, _v['Type']))

        self.widgets.type_combo.setCurrentIndex(0)

    def fr_loop_checkbox(self, value):
        """
        Callback for loop checkbox state
        """

        self.tracker.set_animation_loop(self.widgets.loop_checkbox.isChecked())

    def fr_create_edit_path(self):
        """
        Edit an existing sketch path
        """

        self.path_editor.Activated()

    def fr_speed_slider(self, value):
        """
        Callback for changes to the animation slider position
        """

        if not value:
            value = 1

        else:
            value *= 5

        self.tracker.set_animation_speed(value)

    def fr_type(self, value):
        """
        Callback for vehicle type combobox (currentIndexChanged)
        """

        _symbol = self.widgets.type_combo.currentText()
        _symbol = _symbol.split('(')[0].rstrip()

        self.tracker.set_vehicle(_symbol)

        #set the vehicle data in the UI
        self.widgets.length_edit.setText(
            str(self.tracker.analyzer.vehicles[0].dimensions[0]))

        self.widgets.width_edit.setText(
            str(self.tracker.analyzer.vehicles[0].dimensions[1]))

    def fr_path(self, value):
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

    def to_cur_angle(self, value):
        """
        Callback for vehicle steering angle update
        """

        self.widgets.cur_angle_edit.setText('{:12.2f}'.format(value))

    def to_cur_radius(self, value):
        """
        Callback for vehicle radius
        """

        self.widgets.cur_radius_edit.setText('{:12.2f}'.format(value))

    def fr_max_steps(self, value):
        """
        Callback for maximum steps line edit
        """

        self.tracker.set_max_steps('{:12.2f}'.format(value))

    def fr_cur_step(self, value):
        """
        Callback for current step line edit
        """

        self.tracker.set_step(int(value))

    def to_cur_step(self, value):

        self.widgets.cur_step_edit.setText('{}'.format(str(value)))

    def fr_stop(self):
        """
        Stop and reset the playback
        """

        if not self.is_playing:
            return

        self.is_playing = False

        _play = self.widgets.play_button
        _play.setIcon(_play.style().standardIcon(QStyle.SP_MediaPlay))

        self.tracker.stop_animation()

    def fr_step_forward(self):
        """
        Step forward callback
        """

        self.tracker.move_step(1)

    def fr_step_back(self):
        """
        Step backward callback
        """

        self.tracker.move_step(-1)

    def fr_play(self):
        """
        Play simulation callback
        """

        _icon = QStyle.SP_MediaPlay

        if self.is_playing:
            self.tracker.pause_animation()

        else:
            self.tracker.reset_animation()
            self.tracker.start_animation()
            _icon = QStyle.SP_MediaPause

        self.is_playing = not self.is_playing

        _play = self.widgets.play_button
        _play.setIcon(_play.style().standardIcon(_icon))

    def to_length_edit(self, value):
        """
        Update the length UI edit with the selected vehicle data
        """

        self.widgets.length_edit.setText(str(value))

    def to_width_edit(self, value):
        """
        Update the width UI edit with the selected vehicle data
        """

        self.widgets.width_edit.setText(str(value))

    def accept(self):
        """
        Overrides base implementation (optional)
        """

        self.tracker.finish()
        self.tracker = None

        super().accept()

    def reject(self):
        """
        Overrides base implementation (optional)
        """

        self.tracker.finish()
        self.tracker = None

        super().reject()
