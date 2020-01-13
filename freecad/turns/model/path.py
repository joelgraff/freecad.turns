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
Path model object
"""

from support.tuple_math import TupleMath

from .path_segment import PathSegment

from Part import BSplineCurve

class Path():
    """
    Path model object
    """

    def __init__(self, geometry, steps):
        """
        Constructor
        """

        self.segments = []
        self.steps = steps
        self.geometry = geometry
        self.points = []

        self.update()

    def update(self):
        """
        Update the path based on the current parameters
        """

        _points = self._discretize()
        self._flip_reversed_edges(_points)
        self.points = self._combine_points(_points)

        self._build_segments()

    def _discretize(self):
        """
        Discretize geometry into points, returning a dict of points
        keyed to the reference to the originating Part edge
        """

        _pts = {}

        for _edge in self.geometry:

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

    def _flip_reversed_edges(self, dct):
        """
        Reverse the points of flipped edges in the geometry dictionary
        """

        _keys = tuple(dct.keys())
        _prev = _keys[0]
        _flip_test = []
        _flipped_edges = {}

        #check for proper point order
        for _edge in _keys[1:]:

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
                    dct[_edge] = dct[_edge][::-1]

            #flip the previous edge points if first or last case
            if _flip_test[0] or _flip_test[2]:

                if _prev not in _flipped_edges:
                    _flipped_edges[_prev] = True
                    dct[_prev] = dct[_prev][::-1]

            _prev = _edge

    def _combine_points(self, dct):
        """
        Combine a dictionary of points into a single list,
        eliminating duplicates and building the vector / angle tuples
        """

        _points = []

        for _v in dct.values():

            _p = [_w for _w in _v]

            #Eliminate duplicates at start / end points
            if _points:
                if TupleMath.manhattan(_p[0], _points[-1]) < 0.01:
                    _p = _p[1:]

            _points += _p

        return _points

    def _build_segments(self):
        """
        Build the path data set, pre-calculating key values
        """

        #define each segment starting point and unit vector
        _prev = self.points[0]

        for _pt in self.points[1:]:
            self.segments.append(PathSegment(_prev, _pt))
            _prev = _pt

        #define each segment angle and tangent w.r.t next segment
        _prev = self.segments[0]

        for _seg in self.segments[1:]:
            _prev.set_look_ahead(_seg.vector)
            _prev = _seg

    def finish(self):
        """
        Cleanup
        """

        self.segments = []
        self.steps = 0
        self.geometry = None
        self.points = []
