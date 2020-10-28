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
Line Segment class definition
"""

import math

from freecad_python_support.tuple_math import TupleMath

class LineSegment():

    #one-tenth millimeter default tolerance for lines to be touching
    EPSILON = 0.00

    def __init__(self, start_point, end_point):
        """
        Constructor
        """

        self.start = start_point
        self.end = end_point
        self.points = (self.start, self.end)
        self.vector = TupleMath.subtract(self.end, self.start)
        self.box = self.build_bounding_box()

    def __str__(self):
        """
        Stringify
        """

        return '{}-{}'.format(str(self.start), str(self.end))

    def build_bounding_box(self):
        """
        Build the bounding box for the line
        """

        _box = [self.start[0], self.end[0], self.start[1], self.end[1]]

        if _box[1] < _box[0]:
            _box[0], _box[1] = _box[1], _box[0]

        if _box[3] < _box[2]:
            _box[2], _box[3] = _box[3], _box[2]

        return _box

    def collide(self, line_segment):
        """
        Return true if line segment bounding boxes collide
        """

        return not(
            self.box[0] > line_segment.box[1]\
            or self.box[1] < line_segment.box[0]\
            or self.box[2] > line_segment.box[3]\
            or self.box[3] < line_segment.box[2]
        )

    def is_intersecting(self, line_segment, get_point=True):
        """
        Test to see if two line segments are interescting
        --------
        Algorithm designed by Simon Walton, Dept. of Computer Sciene, Swansea
        http://cs.swan.ac.uk/~cssimon/line_intersection.html
        """

        _y43 = line_segment.vector[1]
        _x43 = line_segment.vector[0]
        _y21 = self.vector[1]
        _x21 = self.vector[0]
        _x31 = line_segment.start[0] - self.start[0]
        _y31 = line_segment.start[1] - self.start[1]

        _d = ((_x43*-_y21)-(-_x21*_y43))

        _u = ((-_y43*-_x31) + (_x43*-_y31)) / _d
        _v = ((-_y21*-_x31) + (_x21*-_y31)) / _d

        _is_true = (0.0 <= _u <= 1.0) and (0.0 <= _v <= 1.0)
        _data = ()

        if _is_true:

            if get_point:
                _data = TupleMath.add(self.start, (_u*_x21, _u*_y21)) + (0.0,)

            else:
                _data = (
                    (_x21, _y21),
                    (_x43, _y43),
                    (_u, _v)
                )
        else:
            _data = _u, _v

        return (_is_true, _data, (_u, _v))

    def get_intersection(self, segment):
        """
        Calculate the intersection of two line segments
        """

        _lhs = TupleMath.subtract(self.end, self.start)[0:2]
        _lhs = TupleMath.multiply(_lhs, (1.0, -1.0))

        _lhs += (sum(TupleMath.multiply(_lhs, self.start)),)

        _rhs = TupleMath.subtract(segment.end, segment.start)[0:2]
        _rhs = TupleMath.multiply(_lhs, (1.0, -1.0))

        _rhs += (sum(TupleMath.multiply(_rhs, segment.start)),)

        _determinant = TupleMath.cross(_lhs, _rhs, (0, 0, 1))[2]

        if not _determinant:
            return (math.nan, math.nan)

        _intersection = (
            TupleMath.cross(_lhs, _rhs, (1, 0, 0))[0],
            TupleMath.cross(_lhs, _rhs, (0, 1, 0))[1]
        )

        return TupleMath.scale(_intersection, 1.0 / _determinant)
