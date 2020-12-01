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
Body model object
"""

from ..trackers.core.support.core.tuple_math import TupleMath
from .axis import Axis

class Body():
    """
    Body model object
    """

    def __init__(self, dimensions, center=None, axis=None):
        """
        Constructor
        dimensions - 2D tuple of body dimensions (length, width)
        center - 2D coordinate tuple of body center.  Calulated if None
        axis - 2D vector tuple of body axis.  Calculated if None
        """

        self.axis = Axis(vector=axis, center=center)
        self.points = None
        self.dimensions = dimensions
        self.validate()

    def validate(self):
        """
        Validates the parameters.
        """

        _l = self.dimensions[0] / 2.0
        _w = self.dimensions[1] / 2.0

        _points = ((_l, _w), (-_l, _w), (-_l, -_w), (_l, -_w))

        _ctr = self.axis.center

        if not _ctr:
            _ctr = (0.0, 0.0)

        _x_coords = [_p[0] + _ctr[0] for _p in _points]
        _y_coords = [_p[1] + _ctr[1] for _p in _points]

        _fit = self.best_fit(_x_coords, _y_coords)

        #Center is calulated as the geometric mean of points, if undefined
        if not self.axis.center:

            _len = len(_points)
            self.axis.center = (sum(_x_coords) / _len, sum(_y_coords) / _len)

        #body orienatation is assumed horizontal with front toward +x,
        #and centered on horizontal axis
        if not self.axis.vector:

            #use the slope of line of best fit for the vector
            self.axis.set_vector((1.0, _fit(1.0)))

        #get the x-axis extrema
        _pts = [min(_points), max(_points)]

        #calculate the corresponding extrema along the line of best fit
        _pts = [
            (_pts[0][0], _fit(_pts[0][0])),
            (_pts[1][0], _fit(_pts[1][0]))
        ]

        #calculate the corresponding length
        self.length = TupleMath.length(TupleMath.subtract(_pts[1], _pts[0]))
        self.axis.set_length(self.length)

        self.points = [TupleMath.add(_ctr, _p) for _p in _points]
        #self.points = [TupleMath.add(_ctr, _p) for _p in self.points]

    def best_fit(self, x_vals, y_vals):
        """
        Calculate best fit of specified points.
        Returns lambda fn of line in form of y = mx + b

        Source:
        https://stackoverflow.com/questions/22239691/code-for-best-fit-straight-line-of-a-scatter-plot-in-python#31800660
        """

        _x_bar = sum(x_vals) / len(x_vals)
        _y_bar = sum(y_vals) / len(y_vals)

        _count = len(x_vals)

        numerator = sum([_x * _y for _x, _y in zip(x_vals, y_vals)])
        numerator -= _count * _x_bar * _y_bar

        denominator = sum([_x**2 for _x in x_vals])
        denominator -= _count * _x_bar**2

        _m = numerator / denominator
        _b = _y_bar - _m * _x_bar

        return lambda _x: _m*_x + _b

    def finish(self):
        """
        Cleanup
        """

        if self.axis:
            self.axis.finish()

        self.points = None
