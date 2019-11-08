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
Vehicle model object
"""

from ..support.tuple_math import TupleMath

from .axis import Axis
from .body import Body

class Vehicle(Body):
    """
    Vehicle model object
    """

    def __init__(self, points, center=None, axis=None):
        """
        Constructor

        points - Tuple of 2D float coordinates defining vehicle border
        center - The vehicle center as a 2D coordinate tuple
        axis - The axis along which axles are positioned. 2D vector tuple
        """

        super().__init__(points, center, axis)

        print('vehicle stats', self.points, self.axis.end_points)

        #indices of points which are to be tracked in analysis
        self.track_idx = range(0, len(points))

        #axle positions along centerline of vehicle
        self.axles = []
        self.max_displacement = 0.0

    def add_axle(self, displacement, length):
        """
        Add an axle.

        length - total length of axle
        displacement - distance along vehicle axis from center point
        """

        print('\n\tadd axle',self.axis.ortho(), self.axis.project(displacement))
        _axle = Axis(vector=self.axis.ortho(), center=self.axis.project(displacement))

        _axle.set_length(length)

        self.axles.append(_axle)

        return
        if displacement > self.max_displacement:
            self.max_displacement = displacement

    def update(self, angle):
        """
        Update the vehicle position using the given turn angle (radians)
        """

        _result = []

        self.angle = angle

        for _a in self.axles:
            _a.update(self.angle)
            _result += [_a.wheels]

        return _result

        #_radius = self.axle_distance / math.tan(math.pi/2.0 - angle)

# INPUTS
#
# Lead vehicle:
# 1. Geometric description of the vehicle outer boundarieas
# 2. Wheel positions along axles 
# 3. Distance between fixed and turning axles (d)
# 4. Angle of lead turning axle (a_l)
#
# Trailing vehicles:
# 1. - 4. Dimensions as indicated in Lead Vehicle (d_t, a_t)
# 5. Pivot distance from center of last fixed axle to pivot point (d_p)
#
# CALCULATIONS
#
# 1. Calculate lead vehicle radius as:
#    r_l = d / tan(90 - a_l)
#
# 2. Iterate trailing vehicles as:
#
#    Pivot Angle:
#    a_p = atan(d_p / r_l)
#
#    Trailer Angle:
#    a_t = asin(d_t / sqrt(d_p^2 + r_l^2))
#
#    Total Angle:
#    a_p + a_t
#
#  3. Calculate wheel positions as ortho vector projections from centers