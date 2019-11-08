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

import FreeCADGui as Gui

from .. import resources

from ..analyze import Analyze
from ..model.vehicle import Vehicle
from ..trackers.vehicle_tracker import VehicleTracker

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

        #list of tuples, associating the control name with the
        #signal and task callback
        self.widgets = [
            ('back_button', 'clicked', self.step_back_cb),
            ('play_button', 'clicked', self.play_cb),
            ('forward_button', 'clicked', self.step_forward_cb)
        ]

        self.analyzer = self.build_analyzer()

        self.tracker = VehicleTracker('car', self.analyzer.vehicles[0])

        self.tracker.insert_into_scenegraph()

    def build_analyzer(self):
        """
        Create analyzer for vehicle
        """

        _analyzer = Analyze()

        _v = Vehicle((19.0, 7.0))
        _v.add_axle(6.5, 6.0)
        _v.add_axle(-4.5, 6.0)

        _analyzer.vehicles.append(_v)

        return _analyzer

    def step_forward_cb(self):
        """
        Step forward callback
        """

        self.analyzer.step()

    def step_back_cb(self):
        """
        Step backward callback
        """

    def play_cb(self):
        """
        Play simulation callback
        """

    def setup(self):
        """
        Override of base class method.  Optional
        """

        super().setup()

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
