# -*- coding: utf-8 -*-
#**************************************************************************
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
Axis model object
"""

from ..support.tuple_math import TupleMath

class Axis():
    """
    Axis model object
    """

    def __init__(self, vector=None, length=1.0, center=None):
        """
        Constructor
        center_point - 2D coordinate tuple
        axis - 2D vector tuple
        """

        self.center = center
        self.end_points = ()
        self.vector = ()
        self.length = length
        self.set_vector(vector)

    def project(self, displacement):
        """
        Project the point along the axis vector from the center
        displacement - distance from center
        """

        return TupleMath.add(
            self.center, TupleMath.scale(self.vector, displacement)
        )

    def set_vector(self, vector):
        """
        Set the vector of the axis, converting it to unit length
        Also calculates axis end points
        """

        if vector:
            vector = TupleMath.unit(vector)

        self.vector = vector

        if not self.vector:
            return

    def set_length(self, length):
        """
        Set the axis length and update the axis end points
        """

        self.length = length

        _half_vector = TupleMath.scale(self.vector, self.length/2.0)

        self.end_points = (
            TupleMath.subtract(self.center, _half_vector),
            TupleMath.add(self.center, _half_vector)
        )

    def ortho(self, is_ccw=True):
        """
        Calculate the orthogonal, cw or ccw from direction of axis
        """

        _signs = (-1.0, 1.0)

        if not is_ccw:
            _signs = (1.0, -1.0)

        return(_signs[0] * self.vector[1], _signs[1] * self.vector[0])

    def finish(self):
        """
        Cleanup
        """

        pass
