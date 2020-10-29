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
Create / edit vehicle templates
"""

import FreeCAD as App

from PySide.QtGui import QStyle

import FreeCADGui as Gui

from freecad_python_support.singleton import Singleton

from .. import resources

from ..model.vehicle import Vehicle

from ..trackers.project.vehicle_template_tracker import VehicleTemplateTracker

from .base_task import BaseTask

class VehicleTemplateTask(BaseTask):
    """
    Swept path analysis task
    """

    def __init__(self):
        """
        Constructor
        """
        self.name = 'VehicleTemplateTask'

        #initialize the inherited base class
        super().__init__(resources.__path__[0] + '/vehicle_template.ui')

        #Initialize state that will be global to the task here
        self.view = Gui.ActiveDocument.ActiveView

        # define the widget signalling data tuples as:
        #(widget_name, widget_signal_name, callback)
        self.widget_callbacks = {

            'edit_vehicle_type': (
                'editingFinished', self.fr_edit_vehicle_type, None),

            'edit_vehicle_description':\
                ('editingFinished', self.fr_edit_vehicle_description, None),

            'edit_length': (
                'editingFinished', self.fr_edit_length, self.to_edit_length),

            'edit_width': (
                'editingFinished', self.fr_edit_width, self.to_edit_width),

            'edit_height': (
                'editingFinished', self.fr_edit_height, self.to_edit_height),

            'edit_min_radius': (
                'editingFinished', self.fr_edit_min_radius, None),

            'edit_max_angle': ('editingFinished', self.fr_edit_max_angle),

            'edit_pivot_offset': ('editingFinished',
                self.fr_edit_pivot_offset, self.to_edit_pivot_offset),

            'spin_axle_count': ('valueChanged', self.fr_spin_axle_count, None),

            'spin_axle_count_2': (
                'valueChanged', self.fr_spin_axle_count_2, None),

            'edit_axle_spacing': (
                'editingFinished', self.fr_edit_axle_spacing, None),

            'edit_axle_spacing_2': (
                'editingFinished', self.fr_edit_axle_spacing_2, None),

            'edit_axle_offset': ('editingFinished',
                self.fr_edit_axle_offset, self.to_edit_axle_offset),

            'edit_axle_offset_2': ('editingFinished',
                self.fr_edit_axle_offset_2, self.to_edit_axle_offset_2)

        }

        self.tracker = VehicleTemplateTracker(None)
        self.tracker.insert_into_scenegraph(True)

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

    def fr_edit_vehicle_type(self, value):
        """
        Update from form control
        """

    def fr_edit_vehicle_description(self, value):
        """
        Update from form control
        """

    def fr_edit_length(self, value):
        """
        Update from form control
        """

    def to_edit_length(self, value):
        """
        Update to form control
        """

    def fr_edit_width(self, value):
        """
        Update from form control
        """

    def to_edit_width(self, value):
        """
        Update to form control
        """

    def fr_edit_height(self, value):
        """
        Update from form control
        """

    def to_edit_height(self, value):
        """
        Update to form control
        """

    def fr_edit_min_radius(self, value):
        """
        Update from form control
        """

    def fr_edit_max_angle(self, value):
        """
        Update from form control
        """

    def fr_edit_pivot_offset(self, value):
        """
        Update from form control
        """

    def to_edit_pivot_offset(self, value):
        """
        Update to form control
        """

    def fr_spin_axle_count(self, value):
        """
        Update from form control
        """

    def fr_spin_axle_count_2(self, value):
        """
        Update from form control
        """

    def fr_edit_axle_spacing(self, value):
        """
        Update from form control
        """

    def fr_edit_axle_spacing_2(self, value):
        """
        Update from form control
        """

    def fr_edit_axle_offset(self, value):
        """
        Update from form control
        """

    def to_edit_axle_offset(self, value):
        """
        Update to form control
        """

    def to_edit_axle_offset_2(self, value):
        """
        Update to form control
        """

    def fr_edit_axle_offset_2(self, value):
        """
        Update from form control
        """

    def to_edit_axle_offset_2(self, value):
        """
        Update to form control
        """
