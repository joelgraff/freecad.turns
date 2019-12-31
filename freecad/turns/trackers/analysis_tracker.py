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
Analysis Tracker class
"""

from types import SimpleNamespace

import FreeCADGui as Gui

from pivy_trackers.support.todo import todo

from pivy_trackers.coin.coin_styles import CoinStyles as Styles
from pivy_trackers.trait.timer import Timer
from pivy_trackers.tracker.context_tracker import ContextTracker
from pivy_trackers.tracker.line_tracker import LineTracker

from ..model.analyzer import Analyzer
from ..model.vehicle import Vehicle
from ..model.path import Path

from .vehicle_tracker import VehicleTracker

class AnalysisTracker(ContextTracker, Timer):
    """
    Analysis Tracker class
    """

    @staticmethod
    def create_section(pos):
        """
        Create a path section object
        """

        return SimpleNamespace(pos=pos, sides=[[]]*2)

    def __init__(self):
        """
        Constructor
        """

        super().__init__(
            name='AnalysisTracker',
            view=Gui.ActiveDocument.ActiveView
        )

        self.steps = 100
        self.vehicles = []
        self.envelopes = {}
        self.path = None
        self.tracker = None

        self.to_step = lambda x: print('to_cur_step')
        self.to_length = lambda x: print('to_length')
        self.to_width = lambda x: print('to_width')
        self.to_radius = lambda x: print('to_radius')
        self.to_angle = lambda x: print('to_angle')

        #create analysis model / engine
        self.analyzer = self.build_analyzer()

        #add vehicle trackers
        for _v in self.analyzer.vehicles:
            self.add_vehicle(_v)

        self.set_visibility()

    def build_envelope_tracker(self):
        """
        Build envelope trackers
        """

        self.tracker = LineTracker(
            'intersects', [], self.base, selectable=False)

    def build_analyzer(self):
        """
        Create analyzer for vehicle
        """

        _analyzer = Analyzer()
        _analyzer.set_step(0, True)

        return _analyzer

    def on_insert(self):
        """
        Override of base function
        """

        #animation timer
        self.add_timer(
            interval=1.0, data=None, callback=self.animate,
            timer_id='analysis_animator', start=False)

        super().on_insert()

    def set_vehicle(self, vehicle_symbol):
        """
        Add a vehicle tracker as described by the Vehicle model object
        """

        for _v in self.vehicles:
            _v.finish()

        self.vehicles = []
        self.add_vehicle(vehicle_symbol)

    def add_vehicle(self, vehicle_symbol):
        """
        Add a vehicle tracker as described by the Vehicle model object
        """

        #create and add the vehicle model data to the analyzer list
        _model = Vehicle.from_template(vehicle_symbol)
        self.analyzer.set_vehicle(_model)

        #create amd add the vehicle tracker data to the tracker list
        _tracker = VehicleTracker(
            name=_model.name, data=_model, parent=self.base)

        self.vehicles.append(_tracker)

    def start_animation(self):
        """
        Start the animation timer
        """

        if not self.tracker:
            todo.delay(self.build_envelope_tracker, None)

        self.reset_animation()
        self.start_timer('analysis_animator')

    def pause_animation(self):
        """
        Pause the animation timer
        """

        self.stop_timer('analysis_animator')

    def stop_animation(self):
        """
        Stop the animation timer
        """

        self.stop_timer('analysis_animator')

        _result = None

        for _v in self.vehicles:
            _result  = _v.envelope.get_envelope(self.path)
            break

        _c = [_v[0] for _v in _result[0]] + [_v[0] for _v in _result[1]]
        _g = [len(_result[0]), len(_result[1])]

        self.tracker.set_style(Styles.ERROR)
        self.tracker.set_visibility()
        self.tracker.update(_c, _g, notify=False)
        self.tracker.show_markers()

    def reset_animation(self):
        """
        Reset the animation
        """

        for _v in self.vehicles:
            _v.envelope.reset()

        self.set_step(0)

        if not self.tracker:
            todo.delay(self.build_envelope_tracker, None)
            return

        self.tracker.reset()
        self.tracker.set_visibility(False)

    def set_animation_speed(self, value):
        """
        Set the animation speed in frames per second
        """

        self.set_timer_interval('analysis_animator', 1.0 / float(value))

    def set_animation_loop(self, value):
        """
        Enable / disable animation looping
        """

        self.analyzer.loop = value

    def animate(self, data, sensor):
        """
        Animation callback
        """

        for _v in self.analyzer.vehicles:

            if _v.at_path_end():

                if not self.analyzer.loop:
                    self.stop_animation()
                    return

                self.reset_animation()

        self.analyzer.step()
        self.refresh()
        self.to_step(self.analyzer.cur_step)
        self.to_radius(self.analyzer.vehicles[0].radius)
        self.to_angle(self.analyzer.vehicles[0].angle)

    def refresh(self):
        """
        Refresh the vehicles in the tracker based on state changes
        """

        for _v  in self.vehicles:
            _v.refresh()

    def set_max_steps(self, steps):
        """
        Set the maximum number of steps for the path and re-discretize
        """

        self.steps = steps

    def set_step(self, step):
        """
        Set the current path step for the analyzer
        """

        self.analyzer.set_step(step)

    def move_step(self, step):
        """
        Move the specified number of steps from the current step
        """

        self.analyzer.set_step(self.analyzer.step + step)

    def set_path(self, geometry):
        """
        Discretize and set the path points for the chosen path
        """

        if self.is_inserted:
            self.reset_animation()

        self.path = Path(geometry, self.steps)
        self.analyzer.set_path(self.path)

        for _v in self.vehicles:
            _v.refresh()
            _v.envelope.reset()

    def finish(self):
        """
        Cleanup
        """

        if self.analyzer:
            self.analyzer.finish()

        for _v in self.vehicles:
            _v.finish()

        super().finish()
