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

from ..support.singleton import Singleton
from .vehicle import Vehicle

def test():

    _a = Analyzer()

    _v = Vehicle((8.0, 20.0), 1.0)
    _v.add_axle(0.0, 3.0)
    _v.add_axle(10.0, 3.0)

    _a.vehicles.append(_v)
    _a.step()

class Analyzer(metaclass=Singleton):
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

        #loop analysis
        self.loop = False

    def set_path(self, path):
        """
        Set the path (a list of tuple coordinates) for vehicles
        """

        for _v in self.vehicles:
            _v.set_path(path)

    def move_steps(self, steps):
        """
        Move the analysis a number of steps from the current step
        """

        for _v in self.vehicles:

            _next_step = _v.step + steps
            _end = len(_v.path) - 1

            if _next_step > _end:

                if self.loop:
                    _next_step = 0

                else:
                    _next_step = _end

            elif _next_step < 0:

                if self.loop:
                    _next_step = _end

                else:
                    _next_step = 0

            if _next_step != _v.step:
                _v.set_step(_next_step)

    def set_step(self, step):
        """
        Set the analysis at a specific step along the path
        """

        for _v in self.vehicles:
            _v.set_step(step)

    def step(self):
        """
        Step the animation of each vehicle one step forward
        """

        self.move_steps(1)

    def update(self, angles):
        """
        Update the vehicles with a list of angles
        """

        for _i, _v in self.vehicles:
            _v.update(angles[_i])
