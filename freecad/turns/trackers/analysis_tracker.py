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
Analysis Tracker class
"""

from types import SimpleNamespace

import FreeCADGui as Gui

from pivy_trackers.coin.coin_styles import CoinStyles as Style
from pivy_trackers.trait.timer import Timer
from pivy_trackers.tracker.context_tracker import ContextTracker
from pivy_trackers.tracker.line_tracker import LineTracker
from ..trackers.envelope_tracker import EnvelopeTracker

from ..model.analyzer import Analyzer
from ..model.vehicle import Vehicle
from ..model.path import Path

from ..support.tuple_math import TupleMath
from ..support.line_segment import LineSegment

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
        self.vehicles = {}
        self.envelopes = {}
        self.path = None

        self.tracker = LineTracker('intersects', [], self.base, selectable=False)

        #create analysis model / engine
        self.analyzer = self.build_analyzer()

        #add vehicle trackers
        for _v in self.analyzer.vehicles:
            self.add_vehicle(_v)

        self.set_visibility()

    def build_analyzer(self):
        """
        Create analyzer for vehicle
        """

        _analyzer = Analyzer()

        _v = Vehicle('car.1', (19.0, 7.0))
        _v.add_axle(6.5, 6.0, False)
        _v.add_axle(-4.5, 6.0)
        _v.set_minimum_radius(24.0)

        _analyzer.vehicles.append(_v)

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

    def add_vehicle(self, vehicle):
        """
        Add a vehicle tracker as described by the Vehicle model object
        """

        _idx = str(len(self.vehicles))

        _v = VehicleTracker(name=vehicle.name, data=vehicle, parent=self.base)
        self.vehicles[vehicle.name] = _v

        self.envelopes[vehicle.name] =\
            EnvelopeTracker(name=vehicle.name, data=vehicle, parent=self.base)

        self.envelopes[vehicle.name].transform_node = _v.geometry.coordinate
        #self.envelopes[vehicle.name].set_visibility(False)

    def start_animation(self):
        """
        Start the animation timer
        """

        self.start_timer('analysis_animator')

    def stop_animation(self):
        """
        Stop the animation timer
        """

        self.stop_timer('analysis_animator')

        import timeit

        _t = timeit.default_timer()
        _x = self._build_envelope_segments()
        _t1 = timeit.default_timer() - _t
        _t = timeit.default_timer()
        _b = self._build_outer_envelope(_x)
        _t2 = timeit.default_timer() - _t

        _c = []
        _g = []
        _c += [_v[0] for _v in _b[0]] + [_v[0] for _v in _b[1]]
        _g += [len(_b[0]), len(_b[1])]

        self.tracker.set_style(Style.ERROR)
        self.tracker.update(_c, _g, notify=False)
        self.tracker.show_markers()

        print(1.0 / (_t1 + _t2))

    def _build_outer_envelope(self, data):
        """
        Build the outer envelope
        """

        _pos = self.path.segments[0].position
        _outer_points = [data[0][0], data[1][0]]
        _other_points = [data[0][1:], data[1][1:]]

        #iterate each side
        for _j, _side in enumerate(_other_points):

            #iterate each track
            for _k, _track in enumerate(_side):

                #iterate the point / distance tuples
                for _l, _point in enumerate(_track):

                    if _outer_points[_j][_l][1] < _point[1]:
                        _outer_points[_j][_l] = _point

        return _outer_points

    def _build_envelope_segments(self):
        """
        Build a structure of track segments split by left / right side
        """

        for _e in self.envelopes.values():
            _pts = _e.get_track_points()

        _tracks = []

        for _group in _pts[0:2]:

            _seg_group = []

            for _points in _group:

                _segments = [
                    LineSegment(_points[_i], _points[_i+1])\
                        for _i in range(0, len(_points)-1)
                ]

                _seg_group.append([_segments, 0, len(_segments)])

            _tracks.append(_seg_group)

        _null_ortho = LineSegment((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
        _result = []

        for _i, _s in enumerate(_tracks):
            _result.append([])

            for _j, _t in enumerate(_s):
                _result[-1].append([])

        #step along the path, building the individual orthos and the
        #trak csegments that are on the left and right sides of each section
        for _i, _seg in enumerate(self.path.segments):

            _prev = self.path.segments[_i]
            _section = self.create_section(_prev)

            _lt = TupleMath.scale(TupleMath.ortho(_prev.tangent), 10)
            _rt = TupleMath.scale(_lt, -1.0)

            _lt = TupleMath.add(_prev.position, _lt)
            _rt = TupleMath.add(_prev.position, _rt)

            _ortho_segs = [
                LineSegment(_prev.position, _lt),
                LineSegment(_prev.position, _rt)
            ]

            _pt = _prev.position

            #iterate left and right sides
            for _j, _side in enumerate(_tracks):

                #iterate each track on the side
                for _k, _track in enumerate(_side):

                    _pt_int = (_pt, 0.0)

                    #iterate each segment in the track
                    for _l in range(_track[1], _track[2]):

                        _seg = _track[0][_l]
                        _int = _ortho_segs[_j].is_intersecting(_seg)
                        _dist = TupleMath.manhattan(_int[1], _pt)

                        if _int[0]:
                            _pt_int = (_int[1], _dist)
                            _track[1] = _l + 1
                            break

                        else:

                            #test previous segment in case of a 'close fail'
                            if _int[2][1] >= 0.0 or _l < 0:
                                continue

                            _seg = _track[0][_l - 1]
                            _int = _ortho_segs[_j].is_intersecting(_seg)
                            _dist = TupleMath.manhattan(_int[1], _pt)

                            if _int[0]:
                                _pt_int = (_int[1], _dist)
                                _track[1] = _l + 1
                                break

                    _result[_j][_k].append(_pt_int)

        return _result


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

            if _v.at_path_end() and not self.analyzer.loop:
                self.stop_animation()

                return

        self.analyzer.step()
        self.refresh()

    def refresh(self):
        """
        Refresh the vehicles in the tracker based on state changes
        """

        for _i, _v  in self.vehicles.items():
            _v.refresh()
            self.envelopes[_i].refresh()

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

        self.path = Path(geometry, self.steps)
        self.analyzer.set_path(self.path)

        for _e in self.envelopes.values():
            _e.reset()

    def finish(self):
        """
        Cleanup
        """

        if self.analyzer:
            self.analyzer.finish()

        for _v in self.vehicles.values():
            _v.finish()

        for _e in self.envelopes.values():
            _e.finish()

        super().finish()
