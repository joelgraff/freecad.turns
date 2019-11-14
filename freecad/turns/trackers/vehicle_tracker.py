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
from pivy_trackers.trait.geometry import Geometry
from pivy_trackers.trait.style import Style

from ..support.tuple_math import TupleMath

class VehicleTracker(Base, Style, Geometry):
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
        self.radius_tracker = []

        self.vehicle = data

        self.build_body()
        self.build_under_carriage()
        self.build_radius_tracker()

        self.set_visibility()
        self.name = name


    def build_radius_tracker(self):
        """
        Create radius trackers for visualizing the vehicle turning radius
        """

        _pts = [(0.0, 0.0, 0.0)]*6

        self.radius_tracker = \
            LineTracker(name='radius', points=_pts, parent=self.base)

        self.radius_tracker.line.numVertices.setValues(0, 2, (3, 3))

    def build_body(self):
        """
        Construct the body tracker
        """

        _veh_pts = [_p + (0.0,) for _p in self.vehicle.points]
        _axis_pts = [_p + (0.0,) for _p in self.vehicle.axis.end_points]

        #add the first to the end to create a closed polygon
        _veh_pts.append(_veh_pts[0])

        self.body = LineTracker(self.name + '_body', _veh_pts, self.base)
        self.axis = LineTracker(self.name + '_axis', _axis_pts, self.base)

    def build_under_carriage(self):
        """
        Construct the vehicle axles
        """

        _nm = self.name + '_{}.{}'

        #build the axles
        for _i, _a in enumerate(self.vehicle.axles):

            _pts = [_p + (0.0,) for _p in _a.end_points]

            self.axles.append(
                LineTracker(_nm.format('axle', str(_i)), _pts, self.base)
            )

        #build the wheels
        for _axle in self.vehicle.axles:

            for _wheel in _axle.wheels:

                _pts = [_p + (0.0,) for _p in _wheel.points]

                _lt = LineTracker(
                    _nm.format('wheel', str(len(self.wheels))),
                    _pts, self.base)

                _lt.geometry.transform.center.setValue(
                    _wheel.center + (0.0,))

                self.wheels[_wheel] = _lt

    def transform_points(self, points, node):
        """
        Override of super function
        """

        for _i, _p in enumerate(points):
            points[_i] = _p + (0.0,)

        return super().transform_points(points, node)

    def update_radius(self):
        """
        Update the radius tracker
        """

        _wheels = self.vehicle.turn_axle.wheels

        _axle_centers = self.transform_points(
            [self.vehicle.fixed_axle.center, self.vehicle.turn_axle.center],
            self.geometry.coordinate
        )

        _wheel_centers = [
            self.wheels[_wheels[0]].transform_points(
                [_wheels[0].center + (0.0,)], self.geometry.coordinate)[0],

            self.wheels[_wheels[1]].transform_points(
                [_wheels[1].center + (0.0,)], self.geometry.coordinate)[0]
        ]

        _ortho = \
            TupleMath.scale(self.vehicle.axis.ortho(), self.vehicle.radius)

        _center = TupleMath.add(_ortho, _axle_centers[0]) + (0.0,)

        _pts = [
            _axle_centers[0], _center, _axle_centers[1],
            _wheel_centers[0], _center, _wheel_centers[1]
        ]

        self.radius_tracker.update(points=_pts, notify=False)

    def update(self):
        """
        Update the vehicle geometry
        """

        for _axle in self.vehicle.axles:

            if _axle.is_fixed:
                continue

            for _wheel in _axle.wheels:

                _ctr = _wheel.center + (0.0,)
                self.wheels[_wheel].geometry.set_rotation(_wheel.angle)
        
        self.update_radius()
