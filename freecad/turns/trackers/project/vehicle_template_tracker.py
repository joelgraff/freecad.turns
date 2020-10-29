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

import math

import FreeCADGui as Gui

from ..core.trait.drag import Drag
from ..core.trait.select import Select

from ..core.coin.coin_group import CoinGroup
from ..core.tracker.context_tracker import ContextTracker
from ..core.tracker.box_tracker import BoxTracker
from ..core.tracker.line_tracker import LineTracker
from ..core.coin.coin_enums import NodeTypes as Nodes
from ..core.coin.coin_enums import Keys
from ..core.coin.todo import todo

from ..core.support.core.tuple_math import TupleMath

from ...resources.qt_frameless_ui import QtFramelessUi

from .envelope_tracker import EnvelopeTracker

class VehicleTemplateTracker(ContextTracker, Drag):
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
            'width' - maximum width (7.0)
            'height' - maximum height (4.25)
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

        self.set_translate_increment(1.0)
        self.set_rotate_increment(0.30)

        self.frameless_ui = QtFramelessUi(Gui.getMainWindow())
        self.frameless_ui.set_signal_callback(self._edit_length_finished)

        self.editing_line = None

        _view_size = Gui.getMainWindow().centralWidget().size().toTuple()
        _view_pos = Gui.getMainWindow().centralWidget().pos().toTuple()
        _win_pos = Gui.getMainWindow().pos().toTuple()

        self.ui_reference_point =\
            TupleMath.add([_win_pos, _view_pos, (0.0, _view_size[1])])

    def build_points(self):
        """
        Build a dict containing the points needed for the trackers
        """

        _points = SimpleNamespace()

        _l = self.data['length'] / 2.0
        _w = self.data['width'] / 2.0

        _points.body = ((-_l, _w), (_l, -_w))

        _points.axles = []

        #add axle points
        for _i in range(0, 2):

            _off = 'axle_offset_' + str(_i)
            _count = 'axle_count_' + str(_i)

            _axle = SimpleNamespace()

            #distance measured from center of body
            _axle.center = (_l - self.data[_off], 0.0)
            _axle.points = []

            _cur_incr = self.data['axle_spacing_' + str(_i)]
            _cur_offset = (_cur_incr * (self.data[_count] - 1) / 2.0)

            #add axles
            for _j in range(0, self.data[_count]):

                _axle.points.append((
                    (_axle.center[0] + _cur_offset, _w - 1.0),
                    (_axle.center[0] + _cur_offset, -(_w - 1.0)),
                ))

                _cur_offset -= _cur_incr

            _points.axles.append(_axle)

            _l = _axle.center[0]

        _points.pivot = None

        #add pivot point
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
        data['axle_count_0'] = 1
        data['axle_offset_0'] = 4.0
        data['axle_spacing_0'] = 5.0
        data['axle_count_1'] = 2
        data['axle_offset_1'] = 32.0
        data['axle_spacing_1'] = 4.0

        return data

    def get_label(self, label, indices):
        """
        Recalculate line length and update label
        """

    def _on_drag_text(self, line):
        """
        Update the line which shares endpoints with this line and was
        partially dragged
        """

        _coords = line.get_drag_coordinates()

        if not _coords:
            return

        _len = TupleMath.length(_coords)

        line.drag_text_update(str(TupleMath.length(_coords)))

    def _after_drag_text(self, line):
        """
        Update the text for partially dragged lines at end of operation
        """
        _coords = line.get_drag_coordinates()

        #self.base.dump()
        if _coords:
            line.set_text(str(TupleMath.length(_coords)))

        self.base.dump()

    def _edit_length_finished(self):
        """
        Callback triggered when line length editing has completed
        """

        print('hide')
        self.frameless_ui.hide()

        _len = None

        try:
            _len = float(self.frameless_ui.text())

        except ValueError:
            return

        self.editing_line.set_length(_len)

    def _edit_length_keypress(self, line, key):
        """
        On key up called in the context of the line
        """

        if not line.is_selected():
            return

        print(line.name, 'selected')

        _pos = self.view_state.view.getPointOnScreen(line.center[0], line.center[1], line.center[2])

        _pos = TupleMath.add(self.ui_reference_point, (_pos[0], -_pos[1]))

        self.editing_line = line
        print(line, _pos)
        self.frameless_ui.set_position(_pos)
        self.frameless_ui.show()

    def build_trackers(self):
        """
        Build trackers from the validated data set
        """

        _tracker = SimpleNamespace()

        _tracker.body = BoxTracker(
            self.name + '_body', corners=self.points.body, parent=self.base)

        print('points', self.points.body)
        _lock_axes = [
            (0.0, 1.0, 0.0),
            (1.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (1.0, 0.0, 0.0)
        ]

        _offsets = [
            ((0.0, 1.0, 0.0), 0.0),
            ((1.0, 0.0, 0.0), -math.pi / 2.0),
            ((0.0, -2.0, 0.0), math.pi),
            ((-1.0, 0.0, 0.0), math.pi / 2.0)
        ]

        _indices = [(1, 3), (0, 2), (1, 3), (0, 2)]

        _on_lambda = lambda line: lambda u, p=line: self._on_drag_text(p)
        _after_lambda = lambda line: lambda u, p=line: self._after_drag_text(p)

        _labels = []

        #iterate the lines and set up callbacks to the adjoining lines
        for _i, _l in enumerate(_tracker.body.lines):

            _l.disable_drag_rotation()
            _l.drag_axis = _lock_axes[_i]

            _l.add_text('LINE ' + str(_i), 'LINE '+ str(_i))

            _l.text.set_visibility(True)

            print(_l.coordinates)
            _offset = TupleMath.add(
                _offsets[_i][0], TupleMath.mean(_l.coordinates)
            )

            _l.text_offset = _offset

            print('coords=',_l.coordinates)
            #hook adjoining line drag callbacks to the current line
            for _j in _indices[_i]:

                _line = _tracker.body.lines[_j]
                _l.on_drag_callbacks.append(_on_lambda(_line))
                _l.after_drag_callbacks.append(_after_lambda(_line))

            todo.delay(_l.set_text, str(_l.get_length()))

            _l.set_keypress_callback(Keys.TAB, self._edit_length_keypress)

        _tracker.axle_groups = []
        _tracker.axles = []
        _tracker.wheels = []

        for _i in range(0, 2):

            _group = CoinGroup(
                is_separated=True, is_switched=False,
                parent=self.base, name=self.name + '_AXLE_GROUP_' + str(_i)
            )

            _group.transform = _group.add_node(
                Nodes.TRANSFORM, _group.name + '_transform')

            _group.set_center(self.points.axles[_i].center + (0.0,))

            #build the undercarriage axles
            for _j, _pair in enumerate(self.points.axles[_i].points):

                _p = [_v + (0.0,) for _v in _pair]

                _axle = LineTracker(
                    _group.name + '_AXLE_' + str(_j), points=_p, parent=_group)

                _front = _tracker.body.lines[1]
                _rear = _tracker.body.lines[3]

                if _i == 0:
                    print('linking', _axle.name, 'to front...')
                    _front.link_geometry(_axle, 0, [0], True)
                    _front.link_geometry(_axle, 1, [1], True)

                else:
                    print('linking', _axle.name, 'to rear...')
                    _rear.link_geometry(_axle, 1, [0], True)
                    _rear.link_geometry(_axle, 0, [1], True)

                _tracker.axles.append(_axle)
                _tire = (1.0, 0.5, 0.0)
                _tire_inv = (-1.0, 0.5, 0.0)

                #generate wheels
                for _k, _p in enumerate(_pair):

                    _corners = (
                        TupleMath.add(_p, _tire_inv),
                        TupleMath.subtract(_p, _tire_inv)
                    )

                    _wheel = BoxTracker(
                        _axle.name + '_WHEEL_' + str(_k), corners=_corners,
                        is_resizeable=False, parent=_axle.geometry.top
                    )

                    _wheel.is_draggable = False
                    _wheel.update_transform = True
                    _axle.link_geometry(_wheel, _k, -1)

            _tracker.axle_groups.append(_group)

        #_tracker.axle_1.set_vertex_groups(
        #    (2,)*(len(self.points.axles[0].points) / 2.0))

        #_tracker.axle_2.set_vertex_groups(
        #    (2,)*(len(self.points.axles[0].points) / 2.0))

        _tracker.pivot = None

        return _tracker

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
