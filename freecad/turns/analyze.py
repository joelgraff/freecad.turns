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
Swept Path Analysis
"""

from .support.singleton import Singleton

from .model.vehicle import Vehicle

def test():

    a = Analyze()

    _v = Vehicle((8.0, 20.0), 1.0)
    _v.add_axle(0.0, 3.0)
    _v.add_axle(10.0, 3.0)

    a.vehicles.append(_v)
    a.step()

class Analyze(metaclass=Singleton):
    """
    Swept Path Analysis
    """

    def __init__(self):
        """
        Constructor
        """

        #list of vehicles to analyze
        self.vehicles = []

        #list of tuples for path coordinates
        self.path = []

        #position along path
        self.position = 0.0

    def step(self):
        """
        Step the analysis along the path
        """

        angle = self.get_path_tangent()

        for _v in self.vehicles:

            _v.update(angle)
            print('step', self.position, 'vehicle', _v.points)

    def get_path_tangent(self):
        """
        Calculate the tangent at the current position along the path
        Angle measured ccw+ from x-axis
        """

        self.position += 0.1

        return self.position
