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

import numpy as np

from .. import utils

from .axle import Axle

class Vehicle():
    """
    Vehicle model object
    """

    def __init__(self, points, pivot, axis=None):
        """
        Constructor

        points - Tuple of 2D float coordinates defining vehicle edges
                 A single coordinate pair is treated as (width, length)
                 Points must describe vehicle in horizontal orienattion
                 with front centered at the origin (0.0, 0.0)
    
        pivot - The pivot point as a float along the vehicle axis.

        axis - The axis along which axles are positioned, as an iterable
               of 2 floats

               Unless defined, calculated as:
                  x - distance of extrema
                  y - average of extrema
        """

        #long axis of vehicle
        self.axis = axis

        #points describing boundary of vehicle.
        self.points = points

        #indices of points which are to be tracked in analysis
        self.track_idx = range(0, len(points))

        #axle positions along centerline of vehicle
        self.axles = []
        self.max_displacement = 0.0

        self.create_boundary()

    def create_boundary(self):
        """
        Create the boundary of the vehicle
        """

        #creation only applies to points = (width, length)
        if not isinstance(self.points[0], float):
            return

        if len(self.points) != 2:
            return

        _w = self.points[0]/2.0
        _l = -self.points[1]

        self.points = [ (_l, -_w), (-_l, _w), (-_l, _w), (_l, _w) ]

        if not self.axis:

            _x_coords = [_v[0] for _v in self.points]
            _y_coords = [_v[1] for _v in self.points]

            #axis is directed from front to rear
            self.axis = np.array([
                min(_x_coords) - max(_x_coords),
                min(_y_coords) - max(_y_coords)
            ])

        #ensure axis is unit length
        self.axis = utils.np_normalize(self.axis)

        return

    def add_axle(self, displacement, offset):
        """
        Add an axle.

        offset - position of outermost wheels (equidisant from center)
        displacement - distance along vehicle axis from pivot point
        """

        self.axles.append(Axle(self.axis, displacement, offset))

        print(self.axles[-1].displacement, self.max_displacement)

        #set the axle distance to the farthest-back axle
        if self.axles[-1].displacement > self.max_displacement:
            self.max_displacement = self.axles[-1].displacement

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