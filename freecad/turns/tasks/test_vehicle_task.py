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
from ..analyze import Analyze
from ..model.vehicle import Vehicle
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

        #initialize the inherited base class
        super().__init__(resources.__path__[0] + '/test_vehicle.ui')

        #Initialize state that will be global to the task here
        self.view = Gui.ActiveDocument.ActiveView
        self.path_editor = PathEditorCommand()

        #list of tuples, associating the control name with the
        #signal and task callback
        #define the widget signalling data
        self.widget_callbacks = [
            ('create_path_button', 'clicked', self.create_edit_path_cb),
            ('edit_path_button', 'clicked', self.create_edit_path_cb),
            ('path_combo', 'currentIndexChanged', self.path_cb),
            ('angle_edit', 'editingFinished', self.angle_cb),
            ('radius_edit', 'editingFinished', self.radius_cb),
            ('steps_button', 'clicked', self.steps_cb),
            ('back_button', 'clicked', self.step_back_cb),
            ('play_button', 'clicked', self.play_cb),
            ('forward_button', 'clicked', self.step_forward_cb)
        ]

        self.analyzer = self.build_analyzer()
        self.tracker = AnalysisTracker()

        for _i, _v in enumerate(self.analyzer.vehicles):
            self.tracker.add_vehicle(_v)

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

    def build_analyzer(self):
        """
        Create analyzer for vehicle
        """

        _analyzer = Analyze()

        _v = Vehicle('car.1', (19.0, 7.0))
        _v.add_axle(6.5, 6.0, False)
        _v.add_axle(-4.5, 6.0)
        _v.set_minimum_radius(24.0)

        _analyzer.vehicles.append(_v)

        return _analyzer

    def create_edit_path_cb(self):
        """
        Edit an existing sketch path
        """

        self.path_editor.Activated()

    def path_cb(self, value):
        """
        Callback for path combobox (currentIndexChanged)
        """

        _name = self.widgets.path_combo.currentText()
        Gui.Selection.clearSelection()
        _sketch = App.ActiveDocument.getObject(_name)

        Gui.Selection.addSelection(_sketch)

        _path = self.discretize_path(
            _sketch.Geometry, self.widgets.steps_spin_box_value())

        self.analyzer.set_path(_path)

    def angle_cb(self):
        """
        Callback for vehicle length line edit (editingFinished)
        """

        print('angle_cb')

    def radius_cb(self):
        """
        Callback for vehicle length line edit (editingFinished)
        """

        print('radius_cb')

    def steps_cb(self, value):
        """
        Callback for vehicle length line edit (clicked)
        """

        print('steps_cb')

    def step_forward_cb(self):
        """
        Step forward callback
        """

        self.analyzer.step(True)

        for _v in self.analyzer.vehicles:
            self.tracker.update(_v)

    def step_back_cb(self):
        """
        Step backward callback
        """

        self.analyzer.step()

        for _v in self.analyzer.vehicles:
            self.tracker.update(_v)

    def play_cb(self):
        """
        Play simulation callback
        """

    def setp_back_cb(self):
        """
        Callback to step the simulation back
        """

    def delete_object_callback(self):
        """
        Callback to step the simulation forward
        """

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

    def discretize_path(self, path, steps):
        """
        Discretize geometry into a series of points
        """

        _path = []

        for _edge in path:

            if _edge.isDerivedFrom('Part::GeomArcOfCircle') \
                or _edge.isDerivedFrom('Part::GeomCircle'):

                _path += [tuple(_v) for _v in _edge.discretize(steps)]

            elif _edge.isDerivedFrom('Part::GeomLineSegment'):
                _path += [tuple(_v) for _v in [_edge.StartPoint,_edge.EndPoint]]

        return _path
