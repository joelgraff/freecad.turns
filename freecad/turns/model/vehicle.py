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

    class Axle(Axis):

        def __init__(self, axis, length, displacement, is_fixed):
            """
            Axle sublclass to manage wheels
            """

            super().__init__()

            self.vector = axis.ortho()
            self.center = axis.project(displacement)
            self.set_length(length)

            self.wheels = [
                Wheel(self.end_points[0]),
                Wheel(self.end_points[1])
            ]

            self.is_fixed = is_fixed

    def __init__(self, name, points, center=None, axis=None):
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
        self.delta = 0.0
        self.radius = 0.0
        self.minimum_radius = 0.0
        self.maximum_angle = 0.0
        self.center = None
        self.name = name
        self.orientation = 0.0
        self.turn_axle = None
        self.fixed_axle = None

        self.path = None
        self.step = 0
        self.angle = 0.0

        self.radius_trackers = []

    def add_axle(self, displacement, length, is_fixed=True):
        """
        Add an axle.

        length - total length of axle
        displacement - distance along vehicle axis from center point
        """

        #create the axle
        _axle = Vehicle.Axle(
            axis=self.axis, length=length,
            displacement=displacement, is_fixed=is_fixed)

        #add it and it's displacement to their lists
        self.axles.append(_axle)
        self.axle_dists.append(displacement)

        #calculate the maximum axle distance
        _max_dist = max(self.axle_dists)
        _min_dist = min(self.axle_dists)

        self.axle_distance = abs(_max_dist - _min_dist)

        #reference the turning axle and the farthest-back fixed axle
        if not is_fixed:
            self.turn_axle = _axle

        else:
            self.fixed_axle = self.axles[self.axle_dists.index(_min_dist)]

    def set_minimum_radius(self, radius):
        """
        Set the minimum vehicle radius, updating the maximum steering angle
        """

        self.minimum_radius = radius
        self.maximum_angle = math.atan(self.axle_distance / radius)

    def set_maximum_angle(self, angle):
        """
        Set the maximum steering angle, updating the minimum radius
        """

        self.maximum_angle = angle
        self.minimum_radius = self.axle_distance / math.tan(angle)

    def set_path(self, path):
        """
        Set the vehicle path
        """

        self.path = path
        self.step = 0
        self.set_step(0, True)

    def set_step(self, step, force_refresh=False):
        """
        Set the absolulte position of the vehicle along it's path
        """

        if not self.path:
            return

        if step > len(self.path) - 1:
            step = len(self.path) - 1

        if self.step == step and not force_refresh:
            return

        self.orientation = \
            -TupleMath.signed_bearing(self.path[step][1], (1.0, 0.0, 0.0))

        if self.step < len(self.path) - 1:

            _angle = self.path[step][2]

            print('steering angle = ', _angle, self.maximum_angle)

            if _angle:
                self.update(_angle)

            print('radius = ', self.radius)

        self.step = step

    def at_path_end(self):
        """
        True if the vehicle step position is at end of the path
        """

        return self.step >= len(self.path) - 1

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

        _half_pi = math.pi / 2.0

        if abs(angle) > self.maximum_angle:
            return False

        self.axis.angle = angle
        self.radius = self.axle_distance / math.tan(angle)

        #sign of angle to add / subtract from central steering angle.
        #relative to ccw-oriented (left-hand) wheel
        _sign = 1.0 # math.copysign(1.0, angle)

        _back_axle = self.axle_dists.index(min(self.axle_dists))
        _back_center = self.axles[_back_axle].center
        _back_vector = self.axles[_back_axle].ortho(_sign > 0.0)

        self.center = TupleMath.add(
            _back_center,
            TupleMath.scale(_back_vector, self.radius * -_sign)
        )

        #iterate each wheel pair.  Left wheel is first in pair
        for _axle in self.axles:

            if _axle.is_fixed:
                continue

            #The wheel angle is the extra angle for each wheel
            #added to the central steering angle

            _wheel_angles = (
                _sign * self.axle_distance / (self.radius + _axle.length/2.0),
                _sign * self.axle_distance / (self.radius - _axle.length/2.0)
            )

            _axle.wheels[0].angle = math.atan(_wheel_angles[0])
            _axle.wheels[1].angle = math.atan(_wheel_angles[1])

        return True
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