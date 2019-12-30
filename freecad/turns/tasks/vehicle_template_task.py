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
Create / edit vehicle templates
"""

import FreeCAD as App

from PySide.QtGui import QStyle

import FreeCADGui as Gui

from .. import resources

from ..model.vehicle import Vehicle

from .base_task import BaseTask

class VehicleTemplateTask(BaseTask):
    """
    Swept path analysis task
    """

    def __init__(self):
        """
        Constructor
        """
        self.name = 'SweptPathAnalysisTask'

        return
        #initialize the inherited base class
        super().__init__(resources.__path__[0] + '/test_vehicle.ui')

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

        return
        
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
