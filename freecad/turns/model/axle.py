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

from .. import utils

class Axle():

    def __init__(self, axis, displacement, offset):
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
        self.displacement = displacement
        self.position = axis * displacement

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

        #wheel positions(left, center, right)
        self.wheels = None

    def update(self, angle):
        """
        Return a list of tuples of the axle wheel coordinates.
        At minimum this is [(left), (center), (right)]
        """

        #rotation computed as:
        #    x_rot = cos(angle*x) - sin(angle*x)
        #    y_rot = sin(angle*x) + cos(angle*y)

        #create axle axis ortho to vehicle axis and multiply by angle
        _axle_comps = np.array([self.vehicle_axis[1], -self.vehicle_axis[0]])
        _axle_comps *= angle

        print('\nAxle components = ',_axle_comps)

        #apply trig functions to axis compoents
        _axle_comps = np.array([
            math.cos(_axle_comps[0]) - math.sin(_axle_comps[1]),
            math.sin(_axle_comps[0]) + math.cos(_axle_comps[1])
        ])

        print('\taxle position =', self.position)

        #new axis
        self.vector = utils.np_normalize(_axle_comps - self.position)

        print('\tself.vector', self.vector, utils.np_length(self.vector))

        #calculate the new wheel positions
        self.wheels = np.array([
            self.center  + (self.vector * self.offset),
            self.center,
            self.center + (self.vector * self.offset * -1)
        ])
