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
Envelope Tracker class
"""

from types import SimpleNamespace

from ..core.coin.coin_styles import CoinStyles as Styles

from ..core.trait.base import Base
from ..core.tracker.polyline_tracker import PolyLineTracker

from ..core.support.core.tuple_math import TupleMath
from ...model.line_segment import LineSegment

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

        #identify starting point for each track
        #calculate transformation from body center
        #calculate transformation to track point
        #combine transformations
        #update poly lines

        self.data = data

        self.points = self.get_track_points()
        self.transforms = self.get_track_transforms()
        print('envelope points:', self.points)
        self.trackers = self.generate_trackers()
        self.body_start = data.center + (0.0,)

        self.set_visibility()

    def get_track_points(self):
        """
        Get the track points for the envelope tracks
        """

        _points = self.data.points

        for _a in self.data.axles:

            for _w in _a.wheels:

                _t = TupleMath.mean(_w.points[0:2])
                _u = TupleMath.mean(_w.points[1:])
                _v = _t

                if (abs(_u[1]) > abs(_t[1])):
                    _v = _u

                _points += (_v,)

        _points = tuple([_v + (0.0,) if len(_v) == 2 else _v for _v in _points])

        return _points

    def get_track_transforms(self):
        """
        Get translation transforms for track points
        """

        _c = self.data.center + (0.0, )

        return (TupleMath.subtract(_p, _c) for _p in self.points)

    def generate_trackers(self):
        """
        Generate Polyline Trackers for tracked points
        """

        _r = [
            PolyLineTracker(
                'Track #{}'.format(str(_i)), [_p], self.base,
                False, subdivided = False)\
                for _i, _p in enumerate(self.points)
            ]

        for _v in _r:
            _v.set_visibility()

        return _r

    def refresh(self, position):
        """
        Update the polylines, appending new track points
        """

        #print('\n\t>>>>>>> {} REFRESH <<<<<<<\n'.format(self.name))
        _path_delta = TupleMath.subtract(self.body_start, self.data.center)
        _orientation = self.data.orientation

        #transform the points by biulding a matrix combining the orientation and
        #the translation append transformed points to the individual trackers

        for _i, _t in enumerate(self.trackers):
            #print('\n\t-=-=-=-=-=-=-=',self.name, position, _t.points)

            _pts = tuple(_t.points) + (TupleMath.add(_t.points[0], position),)
            _t.update(coordinates=_pts)

    def reset(self):
        """
        Reset the envelope tracker coordinates
        """

        return

        #_tracks = self.tracks.inner\
        #        + self.tracks.outer_left + self.tracks.outer_right

        #if not _tracks:
        #    return

        #for _i, _t in enumerate(_tracks):
        #    _t[0].reset()

    def get_envelope(self, path):
        """
        Return the outer envelope
        """

        return None

        print('getting envelope for path', path.points, path.segments)
        _x = self._build_envelope_segments(path)
        _b = self._build_outer_envelope(_x)

        return _b        