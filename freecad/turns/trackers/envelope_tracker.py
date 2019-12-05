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

from pivy_trackers.coin.coin_styles import CoinStyles as Styles

from pivy_trackers.trait.base import Base
from pivy_trackers.tracker.line_tracker import LineTracker

from ..support.tuple_math import TupleMath
from ..support.line_segment import LineSegment

class EnvelopeTracker(Base):

    """
    Vehicle Tracker class
    """

    outer_style = Styles.Style('dashed', color=Styles.Color.GREEN)
    inner_style = Styles.Style('dashed', color=Styles.Color.GOLD)

    def __init__(self, name, data, parent):
        """
        Constructor
        """

        #initialize wih a separator, then reset to defaults
        super().__init__(name=name, parent=parent)

        self.tracks = SimpleNamespace()
        self.tracks.outer_left = []
        self.tracks.outer_right = []
        self.tracks.inner = []
        self.tracks.envelope = None

        self.transform_node = None

        self.data = data

        self.build_envelope_tracks()

        self.set_visibility()

    def get_track_points(self):
        """
        Return the track points in a list of tuple lists
        """

        return (
            [_t[0].coordinates for _t in self.tracks.outer_left],
            [_t[0].coordinates for _t in self.tracks.outer_right],
            [_t[0].coordinates for _t in self.tracks.inner]
        )

    def build_envelope_tracks(self):
        """
        Create the envelope tracker objects
        """

        _track = lambda _n, _p, _r=self.base: LineTracker(
            _n, _p, _r, selectable=False)

        _point = lambda _x: lambda _y=_x: self.data.points[_y] + (0.0,)

        _axle = lambda _x: lambda _y=_x: self.data.axles[_y].center + (0.0,)

        _wheel = lambda _x, _y:\
            lambda _a=_x, _b=_y: self.data.axles[_a].wheels[_b].center + (0.0,)

        _veh = self.data

        self.envelope = LineTracker('envelope', None, self.base)
        self.envelope.set_style(Styles.ERROR)

        self.tracks.inner = [
            (_track('front_left', [_wheel(0, 0)()], self.base), _wheel(0, 0)),
            (_track('front_center', [_axle(0)()], self.base), _axle(0)),
            (_track('front_right', [_wheel(0, 1)()], self.base), _wheel(0, 1)),
            (_track('rear_left', [_wheel(1, 0)()], self.base), _wheel(1, 0)),
            (_track('rear_center', [_axle(1)()], self.base), _axle(1)),
            (_track('rear_right', [_wheel(1, 1)()], self.base), _wheel(1, 1))
        ]

        _axis = self.data.axis.vector + (0.0,)

        for _i, _v in enumerate(self.data.points):

            _pt = _point(_i)

            _tpl = (_track('outer_' + str(_i), [_pt()]), _pt)

            if TupleMath.point_direction(_pt(), _axis) < 0:
                self.tracks.outer_right.append(_tpl)

            else:
                self.tracks.outer_left.append(_tpl)

        for _t in self.tracks.outer_left + self.tracks.outer_right:
            _t[0].coordinates += _t[0].coordinates
            _t[0].set_style(self.outer_style)

        for _t in self.tracks.inner:
            _t[0].coordinates += _t[0].coordinates
            _t[0].set_style(self.inner_style)

    def build_envelope(self):
        """
        Build the ordered set of points which represent the outer envelope
        """

        _tracks = self.tracks.outer_left

        _outer_track = None
        _points = []

        for _i in range(0, len(_tracks[0][0].points)-1):

            _cur_outer_track = _outer_track

            for _t in _tracks:

                #don't test edge against itself
                if _outer_track is _t[0]:
                    continue

                if not _outer_track:
                    _outer_track = _t[0]

                #ensure we aren't picking up the original edge croos
                #if more than one crossing on the same edge occurs
                if _t[0] is _cur_outer_track:
                    continue

                _outer_edge = LineSegment(
                    _outer_track.points[_i], _outer_track.points[_i+1])

                _edge =\
                    LineSegment(_t[0].points[_i], _t[0].points[_i+1])

                if _outer_edge.intersect(_edge):
                    _outer_track = _t[0]

                _points += _outer_edge.points

        self.envelope.update(_points)

    def reset(self):
        """
        Reset the envelope track data
        """

        for _t in self.tracks.inner \
                  + self.tracks.outer_left + self.tracks.outer_right:

            _t[0].coordinates = []

    def refresh(self):
        """
        Update the envelope geometry
        """

        _tracks = self.tracks.inner\
                + self.tracks.outer_left + self.tracks.outer_right

        _points = [_t[1]() for _t in _tracks]
        _points = self.transform_points(_points, self.transform_node)

        for _i, _t in enumerate(_tracks):
            _t[0].update(_t[0].coordinates + [_points[_i]], notify=False)

    def finish(self):
        """
        Cleanup
        """

        for _t in self.tracks.inner\
                  + self.tracks.outer_left + self.tracks.outer_right:

            _t[0].finish()

        self.tracks = None
        self.data = None
        self.transform_node = None
