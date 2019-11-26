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

import FreeCADGui as Gui

from Part import BSplineCurve

from pivy_trackers.trait.timer import Timer
from pivy_trackers.tracker.context_tracker import ContextTracker
from ..trackers.envelope_tracker import EnvelopeTracker

from ..model.analyzer import Analyzer
from ..model.vehicle import Vehicle

from ..support.tuple_math import TupleMath

from .vehicle_tracker import VehicleTracker

class AnalysisTracker(ContextTracker, Timer):
    """
    Analysis Tracker class
    """

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

        return _analyzer

    def on_insert(self):
        """
        Override of base function
        """

        #animation timer
        self.add_timer(
            interval=1.0, data=None, callback=self.animate,
            timer_id='analysis_animator', start=False)

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

    def set_animation_speed(self, value):
        """
        Set the animation speed in frames per second
        """

        self.set_timer_interval('analysis_animator', 1.0 / float(value))

    def set_animation_loop(self, value):

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
            print('refreshing...')
            _v.refresh()
            self.envelopes[_i].refresh()

    def discretize_path(self, path_geometry):
        """
        Discretize geometry into a series of points
        """

        _points = self.discretize_part_geometry(path_geometry)
        self.flipped_reversed_edges(_points)
        pts = self.combine_points(_points)

        return self.build_path_data(pts)

    def discretize_part_geometry(self, part_geometry):
        """
        Discretize Part geometry into points, returning a dict of points
        keyed to the reference to the originating Part edge
        """

        _pts = {}

        for _edge in part_geometry:

            #discretize the edge
            if _edge.isDerivedFrom('Part::GeomArcOfCircle') \
                or isinstance(_edge, BSplineCurve):

                _pts[_edge] = [
                    tuple(_v) for _v in _edge.discretize(self.steps)
                ]

            elif _edge.isDerivedFrom('Part::GeomLineSegment'):
                _pts[_edge] = [
                    tuple(_v) for _v in [_edge.StartPoint, _edge.EndPoint]
                ]

        return _pts

    def flipped_reversed_edges(self, geo_dct):
        """
        Reverse the points of flipped edges in the geometry dictionary
        """

        _prev = None
        _flip_test = []
        _flipped_edges = {}

        #check for proper point order
        for _edge, _points in geo_dct.items():

            if not _prev:
                _prev = _edge
                continue

            #test for flipped endpoints
            _flip_test = [
                TupleMath.manhattan(_prev.StartPoint, _edge.StartPoint) < 0.01,
                TupleMath.manhattan(_prev.EndPoint, _edge.EndPoint) < 0.01,
                TupleMath.manhattan(_prev.StartPoint, _edge.EndPoint) < 0.01
            ]

            #flip the current edge points if either of last two cases
            if _flip_test[1] or _flip_test[2]:

                if _edge not in _flipped_edges:
                    _flipped_edges[_edge] = True
                    geo_dct[_edge] = geo_dct[_edge][::-1]

            #flip the previous edge points if first or last case
            if _flip_test[0] or _flip_test[2]:

                if _prev not in _flipped_edges:
                    _flipped_edges[_prev] = True
                    geo_dct[_prev] = geo_dct[_prev][::-1]

            _prev = _edge

    def combine_points(self, dct):
        """
        Combine a dictionary of points into a single list,
        eliminating duplicates and building the vector / angle tuples
        """
        ###
        #combine the points into a single list of tuples
        ###
        _points = []

        for _v in dct.values():

            _p = [_w for _w in _v]

            #Eliminate duplicates at start / end points
            if _points:
                if TupleMath.manhattan(_p[0], _points[-1]) < 0.01:
                    _p = _p[1:]

            _points += _p

        return _points

    def build_path_data(self, points):
        """
        Build the path data set, pre-calculating key values
        """

        ###
        #build final path data set
        ###

        _pos = points[0]
        _prev = TupleMath.unit(TupleMath.subtract(points[1], points[0]))
        _path = []

        for _i in range(1, len(points) - 2):

            #calculate look-ahead vector, and angle beteen vectors
            _next = TupleMath.subtract(points[_i + 1], points[_i])
            _next = TupleMath.unit(_next)

            _angle = -TupleMath.signed_bearing(_next, _prev)

            #add to path and update state
            _path.append((_pos, _prev, _angle))
            _prev = _next
            _pos = points[_i]

        #add end-of-path tuples
        _path.append((_pos, _prev, 0.0))

        return _path

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

    def set_path(self, path_geometry):
        """
        Discretize and set the path points for the chosen path
        """

        _path = self.discretize_path(path_geometry)

        self.analyzer.set_path(_path)
        self.refresh()

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
