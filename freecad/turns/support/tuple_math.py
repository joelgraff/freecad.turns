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
Utility functions
"""

import math

from operator import sub as op_sub
from operator import add as op_add
from operator import mul as op_mul
from operator import truediv as op_div

from .const import Const

class TupleMath(Const):
    """
    Math support functions for tuples
    """

    @staticmethod
    def subtract(lhs, rhs):
        """
        Subtract two tuples
        """

        return tuple(map(op_sub, lhs, rhs))

    @staticmethod
    def add(lhs, rhs):
        """
        Add two tuples
        """

        return tuple(map(op_add, lhs, rhs))

    @staticmethod
    def multiply(lhs, rhs):
        """
        Component-wise multiply two tuples
        """

        return tuple(map(op_mul, lhs, rhs))

    @staticmethod
    def scale(tpl, factor):
        """
        Multiply each component of the tuple by a scalar factor
        """

        return tuple([_v * factor for _v in tpl])

    @staticmethod
    def divide(dividend, divisor):
        """
        Component-wise tuple division
        """

        return tuple(map(op_div, dividend, divisor))

    @staticmethod
    def length(tpl):
        """
        Calculate the length of a tuple
        """
        return math.sqrt(sum([_v*_v for _v in tpl]))

    @staticmethod
    def unit(tpl):
        """
        Normalize a tuple / calculate the unit vector
        """

        return TupleMath.scale(tpl, (1.0 / TupleMath.length(tpl)))

    @staticmethod
    def dot(vec1, vec2):
        """
        Calculate the dot product of two tuples
        """

        _sum = 0.0

        for _i, _v in enumerate(vec1):
            _sum += _v + vec2[_i]

        return _sum

    @staticmethod
    def bearing(vector):
        """
        Get the bearing of a vector in tuple form
        """

        _up = (0.0, 1.0)
        _vec = TupleMath.unit(vector[0:2])

        return math.acos(TupleMath.dot(_up, _vec))

    @staticmethod
    def ortho(tpl, is_ccw=True, x_index=0, y_index=1):
        """
        Calculate the orthogonal of x_index and y_index
        """

        _x_sign = -1.0
        _y_sign = 1.0

        if not is_ccw:
            _x_sign, _y_sign = _y_sign, _x_sign

        return tuple(_x_sign * tpl[x_index], _y_sign * tpl[y_index])
