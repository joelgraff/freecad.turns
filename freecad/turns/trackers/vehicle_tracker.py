# -*- coding: utf-8 -*-
#***********************************************************************
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
Vehicle Tracker class
"""

import FreeCADGui as Gui

from pivy_trackers.tracker.line_tracker import LineTracker
from pivy_trackers.trait.base import Base

class VehicleTracker(Base):
    """
    Vehicle Tracker class
    """

    def __init__(self, name, data, parent):
        """
        Constructor
        """

        super().__init__(name=name, parent=parent)

        self.body = None
        self.axis = None
        self.axles = []
        self.wheels = {}

        self.build_body(data)
        self.build_under_carriage(data)

        self.set_visibility()
        self.name = name

    def build_body(self, vehicle):
        """
        Construct the body tracker
        """

        _veh_pts = [_p + (0.0,) for _p in vehicle.points]
        _axis_pts = [_p + (0.0,) for _p in vehicle.axis.end_points]

        #add the first to the end to create a closed polygon
        _veh_pts.append(_veh_pts[0])

        print(_veh_pts)

        self.body = LineTracker(self.name + '_body', _veh_pts, self.base)
        self.axis = LineTracker(self.name + '_axis', _axis_pts, self.base)

    def build_under_carriage(self, vehicle):
        """
        Construct the vehicle axles
        """

        _nm = self.name + '_{}.{}'

        #build the axles
        for _i, _a in enumerate(vehicle.axles):

            _pts = [_p + (0.0,) for _p in _a.end_points]

            self.axles.append(
                LineTracker(_nm.format('axle', str(_i)), _pts, self.base)
            )

        #build the wheels
        for _axle in vehicle.axles:

            print(_axle.wheels)

            for _wheel in _axle.wheels:

                _pts = [_p + (0.0,) for _p in _wheel.points]

                _lt = LineTracker(
                    _nm.format('wheel', str(len(self.wheels))),
                    _pts, self.base)

                _lt.geometry.transform.center.setValue(
                    _wheel.center + (0.0,))

                self.wheels[_wheel] = _lt

    def update(self, vehicle):
        """
        Update the vehicle geometry
        """

        for _axle in vehicle.axles:

            print(_axle.is_fixed)
            if _axle.is_fixed:
                continue

            for _wheel in _axle.wheels:

                _ctr = _wheel.center + (0.0,)

                print('wheel rotate = ', _ctr, _wheel.angle)

                self.wheels[_wheel].geometry.set_rotation(_wheel.angle)
