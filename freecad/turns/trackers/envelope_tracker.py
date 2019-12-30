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
        super().__init__(name=name + '_ENVELOPE', parent=parent)

        self.tracks = SimpleNamespace()
        self.tracks.outer_left = []
        self.tracks.outer_right = []
        self.tracks.inner = []
        self.tracks.envelope = None

        self.transform_node = None

        self.data = data

        self._build_envelope_tracks()

        self.set_visibility()

    def get_track_points(self):
        """
        Return the track points in a list of tuple lists
        """

        return (
            [_t[0].coordinates for _t in \
                self.tracks.outer_left + self.tracks.inner[0:2]],

            [_t[0].coordinates for _t in \
                self.tracks.outer_right + self.tracks.inner[2:4]],

            [_t[0].coordinates for _t in self.tracks.inner[4:]]
        )

    def _build_envelope_tracks(self):
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
            (_track('rear_left', [_wheel(1, 0)()], self.base), _wheel(1, 0)),
            (_track('front_right', [_wheel(0, 1)()], self.base), _wheel(0, 1)),
            (_track('rear_right', [_wheel(1, 1)()], self.base), _wheel(1, 1)),
            (_track('front_center', [_axle(0)()], self.base), _axle(0)),
            (_track('rear_center', [_axle(1)()], self.base), _axle(1)),
        ]

        _axis = self.data.axis.vector + (0.0,)

        for _i, _v in enumerate(self.data.points):

            #transform the points according to the current vehicle tracker
            _fn_pt = _point(_i)
            _pt = _fn_pt()

            _tpl = (_track('outer_' + str(_i), [_pt]), _fn_pt)

            if TupleMath.point_direction(_pt, _axis) < 0:
                self.tracks.outer_right.append(_tpl)

            else:
                self.tracks.outer_left.append(_tpl)

        for _t in self.tracks.outer_left + self.tracks.outer_right:
            _t[0].set_style(self.outer_style)

        for _t in self.tracks.inner:
            _t[0].set_style(self.inner_style)

    def get_envelope(self, path):
        """
        Return the outer envelope
        """

        import timeit

        _t = timeit.default_timer()
        _x = self._build_envelope_segments(path)
        _t1 = timeit.default_timer() - _t

        _t = timeit.default_timer()
        _b = self._build_outer_envelope(_x)
        _t2 = timeit.default_timer() - _t

        return _b

    def _build_outer_envelope(self, data):
        """
        Build the outer envelope
        """

        _outer_points = [_v[0] for _v in data]
        _other_points = [_v[1:] for _v in data]

        #iterate each side
        for _j, _side in enumerate(_other_points):

            #iterate each track
            for _k, _track in enumerate(_side):

                #iterate the point / distance tuples
                for _l, _point in enumerate(_track):

                    if _outer_points[_j][_l][1] < _point[1]:
                        _outer_points[_j][_l] = _point

        return _outer_points

    def _build_envelope_segments(self, path):
        """
        Build a structure of track segments split by left / right side
        """

        _pts = self.get_track_points()

        _tracks = []

        #there are three 'groups': left, right, and center tracks
        for _group in _pts:

            _seg_group = []

            #iterate the points in each group, building segments
            #and storing the results.
            for _points in _group:

                _segments = [
                    LineSegment(_points[_i], _points[_i+1])\
                        for _i in range(0, len(_points)-1)
                ]

                _seg_group.append([_segments, 0, len(_segments)])

            _tracks.append(_seg_group)

        _null_ortho = LineSegment((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))
        _result = []

        for _i, _s in enumerate(_tracks[0:2]):
            _result.append([])

            for _j, _t in enumerate(_s):
                _result[-1].append([])

        #step along the path, building the individual orthos and the
        #track segments that are on the left and right sides of each section
        for _i, _seg in enumerate(path.segments):

            _prev = path.segments[_i]

            _lt = TupleMath.scale(TupleMath.ortho(_prev.tangent), 10)

            #tangent / orthogonal pair
            _o_segs = [_lt, TupleMath.scale(_lt, -1.0)]

            #calculate end point for unit-length tangent and orthogonal
            _o_segs = [TupleMath.add(_prev.position, _v) for _v in _o_segs]
            _o_segs = [LineSegment(_prev.position, _v) for _v in _o_segs]

            _pt = _prev.position

            #iterate left and right sides
            for _j, _side in enumerate(_tracks[0:2]):

                #iterate each track on the side
                for _k, _track in enumerate(_side):

                    _pt_int = (_pt, 0.0)

                    _segments = _track[0]

                    #iterate each segment in the track
                    for _l in range(_track[1], _track[2]):

                        #pick the current segment from the track 
                        #and save it's manhattan distance from the path
                        _seg = _segments[_l]

                        _int = _o_segs[_j].is_intersecting(_seg)
                        _dist = TupleMath.manhattan(_int[1], _pt)

                        #if the segment intersects the orthogonal,
                        #save the intersection constants and distance
                        #and save the segment starting position
                        if _int[0]:
                            _pt_int = (_int[1], _dist)
                            _track[1] = _l + 1
                            break

                        else:

                            #test previous segment in case of a 'close fail'
                            if _int[2][1] >= 0.0 or _l < 0:
                                continue

                            _seg = _segments[_l - 1]
                            _int = _o_segs[_j].is_intersecting(_seg)
                            _dist = TupleMath.manhattan(_int[1], _pt)

                            if _int[0]:
                                _pt_int = (_int[1], _dist)
                                _track[1] = _l + 1
                                break

                    #save the intersection data
                    _result[_j][_k].append(_pt_int)

        return _result

    def reset(self):
        """
        Reset the envelope tracker coordinates
        """

        _tracks = self.tracks.inner\
                + self.tracks.outer_left + self.tracks.outer_right

        if not _tracks:
            return

        for _i, _t in enumerate(_tracks):
            _t[0].reset()

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

        if self.tracks:

            for _t in self.tracks.inner\
                  + self.tracks.outer_left + self.tracks.outer_right:

                _t[0].finish()

        self.tracks = None
        self.data = None
        self.transform_node = None

        super().finish()
