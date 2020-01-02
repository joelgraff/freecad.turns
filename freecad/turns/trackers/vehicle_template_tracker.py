# -*- coding: utf-8 -*-
#***********************************************************************
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
Vehicle Template Tracker class
"""

from types import SimpleNamespace

import FreeCADGui as Gui

from pivy_trackers.tracker.context_tracker import ContextTracker
from pivy_trackers.tracker.empty_tracker import EmptyTracker
from pivy_trackers.tracker.box_tracker import BoxTracker
from pivy_trackers.tracker.line_tracker import LineTracker

from ..support.tuple_math import TupleMath

from .envelope_tracker import EnvelopeTracker

class VehicleTemplateTracker(ContextTracker):
    """
    Vehicle Template Tracker class
    """

    def __init__(self, data):
        """
        Constructor

        data - a dict of the vehicle data (empty or None for default):
            'symbol' - vehicle type symbol ('UNK')
            'description' - description of vehicle type ('')
            'length' - total length (19.0)
            'width - maximum width (7.0)
            'height - maximum height (4.25)
            'max_radius' - maximum turning radius (13.7)
            'min_angle' - minimum turning angle (radius controls)
            'pivot_offset' - distance of pivot point from front
            'axle_count_1 / _2' - number of group 1 axles
            'axle_spacing_1 / _2' - spacing between group 1 axles
            'axle_offset_1 / _2' - distance of group from prev. group / front
        """

        super().__init__(name='vehicle template', parent=None,
                         view=Gui.ActiveDocument.ActiveView)

        self.data = self.validate_data(data)
        self.points = self.build_points()

        self.trackers = self.build_trackers()
        self.set_visibility()

    def build_points(self):
        """
        Build a dict containing the points needed for the trackers
        """

        _points = SimpleNamespace()

        _l = self.data['length'] / 2.0
        _w = self.data['width'] / 2.0

        _points.body = ((-_l, _w), (_l, -_w))

        _points.axles = []

        _axle_1 = SimpleNamespace()
        _axle_1.center = (_l - self.data['axle_offset_1'], 0.0)
        _axle_1.points = []

        _cur_offset = -int((self.data['axle_count_1']-1.0)/2.0)\
            * self.data['axle_offset_1']

        for _i in range(0, self.data['axle_count_1']):

            _axle_1.points.append((
                (_axle_1.center[0] + _cur_offset, _w - 1.0),
                (_axle_1.center[0] + _cur_offset, -(_w - 1.0)),
            ))

            _cur_offset += 1.0

        _points.axles.append(_axle_1)

        _axle_2 = SimpleNamespace()
        _axle_2.center = (_axle_1.center[0] - self.data['axle_offset_2'], 0.0)
        _axle_2.points = []

        _cur_offset =\
            -int((self.data['axle_count_2']-1.0)/2.0) * self.data['axle_offset_2']

        for _i in range(0, self.data['axle_count_2']):

            _axle_2.points.append((
                (_axle_2.center[0] + _cur_offset, _w - 1.0),
                (_axle_2.center[0] + _cur_offset, -(_w - 1.0)),
            ))

            _cur_offset += 1.0

        _points.axles.append(_axle_2)

        _points.pivot = None

        if self.data['pivot_offset']:

            _pvt = _l - self.data['pivot_offset']
            _points.pivot = (
                (_pvt - 0.5, 0.5), (_pvt + 0.5, 0.5),
                (_pvt + 0.5, -0.5), (_pvt - 0.5, -0.5), (_pvt - 0.5, 0.5)
            )

        return _points

    def validate_data(self, data):
        """
        Validate the data set and populate the points for the trackers
        """

        if not data:
            data = {}

        data['length'] = 40.0
        data['width'] = 8.0
        data['height'] = 4.25
        data['max_radius'] = 13.7
        data['pivot_offset'] = 0.0
        data['axle_count_1'] = 1
        data['axle_offset_1'] = 4.0
        data['axle_spacing_1'] = 0.0
        data['axle_count_2'] = 2
        data['axle_offset_2'] = 33.0
        data['axle_spacing_2'] = 2.0

        return data

    def build_trackers(self):
        """
        Build trackers from the validated data set
        """

        _tracker = SimpleNamespace()

        _tracker.body = BoxTracker(
            self.name + '_body', corners=self.points.body, parent=self.base)

        EmptyTracker.is_separated = True
        _tracker.axle_group_1 = EmptyTracker(
            self.name + '_group_1_transform', parent=self.base)

        EmptyTracker.is_separated = True
        _tracker.axle_group_2 = EmptyTracker(
            self.name + '_group_2_transform', parent=self.base)

        return
        _tracker.axle_group_1.set_center(self.points.axles[0].center)
        _tracker.axle_group_2.set_center(self.points.axles[1].center)

        _tracker.axle_1 = LineTracker(
            self.name + '_group_1', points=self.points.axle_group_1,
            parent=_tracker.axle_group_1)

        _tracker.axle_2 = LineTracker(
            self.name + '_group_2', points=self.points.axle_group_2,
            parent=_tracker.axle_group_2)

        _tracker.axle_1.set_vertex_groups(
            (2,)*(len(self.points.axles[0].points) / 2.0)
        )

        _tracker.axle_2.set_vertex_groups(
            (2,)*(len(self.points.axles[0].points) / 2.0)
        )

        _tracker.pivot = None

        if self.points.pivot:
            _tracker.pivot = BoxTracker(
                self.name + '_pivot', corners=self.points.pivot,
                parent=self.base)

        return _tracker

    def build_envelope(self):
        """
        Build trackesr for the envelope tracks
        """

        self.envelope = EnvelopeTracker(
            name=self.name + '_ENVELOPE', data=self.vehicle, parent=None)

        #insert the envelope at the top, before the transform node
        self.base.insert_node(self.envelope.root, self.base.top, 0)

        self.envelope.transform_node = self.geometry.transform

    def build_radius_tracker(self):
        """
        Create radius trackers for visualizing the vehicle turning radius
        """

        _pts = [(0.0, 0.0, 0.0)]*6

        self.radius_tracker = LineTracker(
            name='radius', points=_pts, parent=self.base, selectable=False)

        self.radius_tracker.line.numVertices.setValues(0, 2, (3, 3))

    def build_body(self):
        """
        Construct the body tracker
        """

        _veh_pts = [_p + (0.0,) for _p in self.vehicle.points]
        _axis_pts = [_p + (0.0,) for _p in self.vehicle.axis.end_points]

        #add the first to the end to create a closed polygon
        _veh_pts.append(_veh_pts[0])

        self.body = LineTracker(
            self.name + '_body', _veh_pts, self.base, selectable=False)

        self.axis = LineTracker(
            self.name + '_axis', _axis_pts, self.base, selectable=False)

    def build_under_carriage(self):
        """
        Construct the vehicle axles
        """

        _nm = self.name + '_{}.{}'

        #build the axles
        for _i, _a in enumerate(self.vehicle.axles):

            _pts = [_p + (0.0,) for _p in _a.end_points]

            self.axles.append(LineTracker(
                _nm.format('axle', str(_i)), _pts, self.base, selectable=False
            ))

        #build the wheels
        for _axle in self.vehicle.axles:

            for _wheel in _axle.wheels:

                _pts = [_p + (0.0,) for _p in _wheel.points]
                _pts.append(_pts[0])

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

    def refresh_radius(self):
        """
        Refresh the radius tracker
        """

        _wheels = self.vehicle.turn_axle.wheels

        _axle_centers = [
            self.vehicle.fixed_axle.center + (0.0,),
            self.vehicle.turn_axle.center + (0.0,)
        ]

        _wheel_centers = [
            _wheels[0].center + (0.0,), _wheels[1].center + (0.0,)]

        _ortho = \
            TupleMath.scale(self.vehicle.axis.ortho(), self.vehicle.radius)

        _center = TupleMath.add(_ortho, _axle_centers[0]) + (0.0,)

        _pts = [
            _axle_centers[0], _center, _axle_centers[1],
            _wheel_centers[0], _center, _wheel_centers[1]
        ]

        self.radius_tracker.update(points=_pts, notify=False)

    def refresh(self):
        """
        Refresh the vehicle geometry based on the data model
        """

        if not self.vehicle.path:
            return

        _pos = self.vehicle.path.segments[self.vehicle.step].position

        self.geometry.set_translation(_pos)
        self.geometry.set_rotation(self.vehicle.orientation)

        for _axle in self.vehicle.axles:

            if _axle.is_fixed:
                continue

            for _wheel in _axle.wheels:

                _ctr = _wheel.center + (0.0,)
                self.wheels[_wheel].geometry.set_rotation(_wheel.angle)

        self.refresh_radius()
        self.envelope.refresh()

    def finish(self):
        """
        Cleanup
        """

        self.body = None
        self.axis = None
        self.axles = []
        self.wheels = {}

        if self.radius_tracker:
            self.radius_tracker.finish()
            self.radius_tracker = []

        super().finish()
