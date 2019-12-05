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

from Part import BSplineCurve

from pivy_trackers.coin.coin_styles import CoinStyles as Style
from pivy_trackers.trait.timer import Timer
from pivy_trackers.tracker.context_tracker import ContextTracker
from pivy_trackers.tracker.line_tracker import LineTracker
from ..trackers.envelope_tracker import EnvelopeTracker

from ..model.analyzer import Analyzer
from ..model.vehicle import Vehicle

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

        import timeit

        print('method b..')
        _b = timeit.default_timer()
        _x = self._build_envelope_segments()
        print(timeit.default_timer() - _b, len(_x))

#        _c = [] #list(self.tracker.coordinates)
#        _g = self.tracker.groups
#        _null_ortho = LineSegment((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))

#        for _side in _x:
#            for _segments in _side:
#                for _segment in _segments:
#                    _c += [_segment[0].start, _segment[0].end]
#                    _g += [2]

#        self.tracker.set_style(Style.ERROR)
#        self.tracker.update(_c, _g, notify=False)

        _b = self._build_outer_envelope(_x)

        _c = []
        _g = []

        for _side in _b:

            for _seg in _side:

                _c += [_seg.start, _seg.end]

        self.tracker.set_style(Style.ERROR)
        self.tracker.update(_c, _g, notify=False)

    def _build_outer_envelope(self, data):
        """
        Build the outer envelope
        """

        print(data)

        _pos = self.path[0][0]
        _outer_idx = []
        _boundary = []
        _idx = -1

        #determine the outermost track on each side
        for _segments in data[0].sides:

            _prev = None
            _seg = None
            _side_boundary = []

            for _i, _segment in enumerate(_segments):

                if not _segment:
                    continue

                _dist = TupleMath.manhattan(_pos, _segment[0].start)

                if _prev is not None:

                    if _dist < _prev:
                        continue

                    _dist = _prev
                    _seg = _segment
                    _idx = _i
                    break

                _prev = _dist
                _seg = _segment
                _idx = _i

            _outer_idx.append(_idx)
            _boundary.append([_seg[0]])

        # with the outer segments determined, iterate the subseqent segments
        # on each side of each point, testing tracking the segments which
        # cross it

        #iterate the positions, getting the segments on both sides
        for _i, _section in enumerate(data[1:]):

            #iterate the groups of segments on each side
            for _j, _segments in enumerate(_section.sides):

                print(_i, _j, _segments, _outer_idx)

                _side_boundary = _segments[_outer_idx[_j]][0]

                print(_i, _side_boundary)

                for _k, _segment in enumerate(_segments):

                    if _k == _outer_idx[_j]:
                        break

                    if not _segment:
                        continue

                    if _segment[0].is_intersecting(_side_boundary):
                        _side_boundary = _segment[0]
                        _outer_idx[_j] = _k

                _boundary[_j].append(_side_boundary)

        return _boundary

    def _build_envelope_segments(self):

        _result = []

        for _e in self.envelopes.values():
            _pts = _e.get_track_points()

        _tracks = []

        for _group in _pts[0:2]:

            _seg_group = []

            for _points in _group:

                _segments = [
                    LineSegment(_points[_i], _points[_i+1])\
                        for _i in range(0,len(_points)-1)
                ]

                _seg_group.append([_segments, 0, len(_segments)])

            _tracks.append(_seg_group)

        _null_ortho = LineSegment((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))

        #iterate the path points:
        for _i in range(0, len(self.path) - 1):

            _prev = self.path[_i]

            _lt = TupleMath.scale((-_prev[3][1], _prev[3][0], 0.0), 10)
            _rt = TupleMath.scale(_lt, -1.0)

            _lt = TupleMath.add(_prev[0], _lt)
            _rt = TupleMath.add(_prev[0], _rt)

            _ortho_segs = [
                LineSegment(_prev[0], _lt),
                LineSegment(_prev[0], _rt)
            ]

            _sides = []
            _section = self.create_section(_prev)

            #iterate left and right-side tracks
            for _h, _t in enumerate(_tracks):

                _segments = []

                #iterate each track segment pair
                for _j, _v in enumerate(_t):

                    _found_intersect = False

                    #iterate the track segments
                    for _k in range(_v[1], _v[2]):

                        _seg = _v[0][_k]
                        _seg_int = _ortho_segs[_h].is_intersecting(_seg)
                        _found_intersect = _seg_int[0]

                        if _found_intersect:

                            _section.sides[_h].append((_seg, _seg_int[1]))
                            #store the side, track, and segment indices
                            #_segments.append((_seg, _j, _seg_int[1]))
                            _v[1] = _k + 1
                            break

                        print ('\n\t----<NOT FOUND>----\n\t',_i,_seg,_seg_int[1])

                    if not _found_intersect:
                        _section.sides[_h].append(())
                        #_segments.append(())

                #_sides.append(_segments)

            _result.append(_section)

        return _result

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
        # path consists of a tuple containing the following data:
        # - starting point of segment
        # - directed unit vector
        # - bearing angle of vector
        # - tangent vetor at starting point
        ###

        _pos = points[0]
        _prev = TupleMath.unit(TupleMath.subtract(points[1], points[0]))
        _path = []

        for _i in range(1, len(points) - 2):

            #calculate look-ahead vector, and angle beteen vectors
            _next = TupleMath.subtract(points[_i + 1], points[_i])
            _next = TupleMath.unit(_next)

            _angle = -TupleMath.signed_bearing(_next, _prev)

            _tangent = TupleMath.add(_next, _prev)

            #add to path and update state
            _path.append((_pos, _prev, _angle, _tangent))
            _prev = _next
            _pos = points[_i]

        #add end-of-path tuples
        _path.append((_pos, _prev, 0.0, _prev))

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

        self.path = self.discretize_path(path_geometry)

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
