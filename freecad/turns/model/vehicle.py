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

import math

from ..support.tuple_math import TupleMath

from .axis import Axis
from .body import Body
from .wheel import Wheel

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

        #indices of points which are to be tracked in analysis
        self.track_idx = range(0, len(points))

        #axle positions along centerline of vehicle
        self.axles = []
        self.axle_dists = []
        self.axle_distance = 0.0
        self.wheels = {}
        self.delta = 0.0
        self.radius = 0.0
        self.center = None

    def add_axle(self, displacement, length):
        """
        Add an axle.

        length - total length of axle
        displacement - distance along vehicle axis from center point
        """

        _axle = Axis(vector=self.axis.ortho(), center=self.axis.project(displacement))

        _axle.set_length(length)

        self.axles.append(_axle)

        self.wheels[_axle] = (
            Wheel(_axle.end_points[0]),
            Wheel(_axle.end_points[1])
        )

        self.axle_dists.append(displacement)
        self.axle_distance = abs(max(self.axle_dists) - min(self.axle_dists))

    def update(self, angle):
        """
        Update the vehicle position using the given steering angle (radians)
        """

        # The angle subtended by the radius of the arc on which the front and
        # center wheel midpoints lie is equal to the steering angle.
        #
        # The radius is the distance between the axles divided by
        # the tangent of the steering angle
        #
        # The wheel angles are the arctangent of the axle distance divided by
        # the radius, offset by half the vehicle width.
        #
        # The arc direction is -cw / +ccw
        _result = []

        self.angle = angle
        self.radius = self.axle_distance / math.tan(math.pi / 2.0 - angle)

        #sign of angle to add / subtract from central steering angle.
        #relative to ccw-oriented (left-hand) wheel
        _sign = math.copysign(1.0, angle)

        _back_axle = self.axle_dists.index(min(self.axle_dists))
        _back_center = self.axles[_back_axle].center
        _back_vector = self.axles[_back_axle].ortho(_sign > 0.0)

        self.center = TupleMath.add(
            _back_center,
            TupleMath.scale(_back_vector, self.radius * -_sign)
        )

        #iterate each wheel pair.  Left wheel is first in pair
        for _axle, _wheels in self.wheels.items():

            #The wheel angle is the extra angle for each wheel
            #added to the central stering angle
            _wheel_angle = math.atan(self.axle_distance / (_axle.length/2.0))

            _wheels[0].angle = _sign * _wheel_angle
            _wheels[1].angle = -_sign * _wheel_angle

        return _result

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