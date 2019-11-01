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
Axle model object
"""

import math

import numpy as np

class Axle():

    def __init__(self, axis, position, offset):
        """
        Constructor

        axis - unit length vector as numpy array of 2 floats
        position - float
        offset  - float
        """

        #axis along which axle is positioned,
        #directed from front to rear
        self.vehicle_axis = axis

        #displacement along vehicle axial vector from pivot point
        self.position = position

        #center wheel position
        self.center = self.vehicle_axis * self.position

        #offset of outermost wheel from axle center (equidistant)
        self.offset = offset

        #turning angle in radians of center wheel w.r.t axis, ccw+
        self.angle = math.pi

        #vector pointing along left side of axle
        self.vector = None

        #define initial wheel positions
        self.update(self.angle)

    def update(self, angle):
        """
        Return a list of tuples of the axle wheel coordinates.
        At minimum this is [(left), (center), (right)]
        """

        _cos = math.cos(angle)
        _sin = math.sin(angle)

        #rotate the axle bhy the given angle
        self.vector = np.array([self.vehicle_axis[1], -self.vehicle_axis[0]])
        self.vector *= np.array([[_cos, -_sin],[_sin, _cos]])

        #calcualte the new wheel positions
        self.wheels = np.array([
            self.center  + (self.vector * self.offset),
            self.center,
            self.center + (self.vector * self.offset * -1)
        ])
