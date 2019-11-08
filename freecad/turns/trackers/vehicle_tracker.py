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

    def __init__(self, vehicle_name, vehicle):
        """
        Constructor
        """

        super().__init__(vehicle_name, Gui.ActiveDocument.ActiveView)

        _veh_pts = [_p + (0.0,) for _p in vehicle.points]
        _axis_pts = [_p + (0.0,) for _p in vehicle.axis.end_points]

        #add the first to the end to create a closed polygon
        _veh_pts.append(_veh_pts[0])

        self.body = LineTracker(self.name + '_body', _veh_pts, self.base)
        self.axis = LineTracker(self.name + '_axis', _axis_pts, self.base)
        self.axles = []

        for _i, _a in enumerate(vehicle.axles):

            _pts = [_p + (0.0,) for _p in _a.end_points]

            self.axles.append(
                LineTracker(self.name + '_axle' + str(_i), _pts, self.base)
            )

        #    _wheels = []

        #    for _p in _a.wheels:
        #        _wheels.append(_p + (0.0,))

        self.set_visibility()
