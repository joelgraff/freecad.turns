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
Envelope Tracker class
"""

from types import SimpleNamespace

from pivy_trackers.tracker.geometry_tracker import GeometryTracker
from pivy_trackers.tracker.line_tracker import LineTracker

from ..support.tuple_math import TupleMath

class EnvelopeTracker(GeometryTracker):

    """
    Vehicle Tracker class
    """

    def __init__(self, name, data, parent):
        """
        Constructor
        """

        super().__init__(name=name, parent=parent)

        self.tracks = SimpleNamespace()
        self.tracks.outer = []
        self.tracks.inner = []

        self.transform_node = None

        self.data = data

        self.build_envelope_tracks()

        self.set_visibility()


    def build_envelope_tracks(self):
        """
        Create the envelope tracker objects
        """

        _track = lambda _n, _p, _r=self.base: LineTracker(_n, _p, _r)

        _point = lambda _x: lambda _y=_x: self.data.points[_y] + (0.0,)

        _axle = lambda _x: lambda _y=_x: self.data.axles[_y].center + (0.0,)

        _wheel = lambda _x, _y:\
            lambda _a=_x, _b=_y: self.data.axles[_a].wheels[_b].center + (0.0,)

        _veh = self.data

        self.tracks.inner = [
            (_track('front_left', [_wheel(0, 0)()], self.base), _wheel(0, 0)),
            (_track('front_center', [_axle(0)()], self.base), _axle(0)),
            (_track('front_right', [_wheel(0, 1)()], self.base), _wheel(0, 1)),
            (_track('rear_left', [_wheel(1, 0)()], self.base), _wheel(1, 0)),
            (_track('rear_center', [_axle(1)()], self.base), _axle(1)),
            (_track('rear_right', [_wheel(1, 1)()], self.base), _wheel(1, 1))
        ]

        for _i, _v in enumerate(self.data.points):
            self.tracks.outer += [
                (_track('outer_' + str(_i), [_point(_i)()]), _point(_i))
            ]

    def refresh(self):
        """
        Update the envelope geometry
        """

        _tracks = self.tracks.inner + self.tracks.outer
        _points = [_t[1]() for _t in _tracks]
        _points = self.transform_points(_points, self.transform_node)

        for _i, _t in enumerate(_tracks):
            _t[0].update(_t[0].points + [_points[_i]], False)
