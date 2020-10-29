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
Utility functions
"""

import math

from collections.abc import Iterable

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
    def _operation(op, op1, op2, fail_on_empty=False):

        #default tests for failed operations
        if op1 is None or op2 is None:

            if fail_on_empty or op1 is None:
                return None

        _op1 = op1
        _op2 = op2

        if not isinstance(_op1, Iterable):
            _op1 = (_op1,)

        #recurse against the list of items in op1 if op2 is undefined
        if op2 is None or ():

            _t = _op1[1:]

            #if op1 is a scalar, return op1
            if not _t:
                return _op1

            _result = _op1[0]

            for _v in _op1[1:]:
                _result = tuple(map(op, _result, _v))

            return _result
            #otherwise, recurse, operating all subsequent elements
            #against the first
            _op1 = (op1[0],)*len(op1)-1

            return tuple(map(op, _op1, _t))

        elif not isinstance(op2, Iterable):
            _op2 = (_op2,)

        #op1 and op2 are both defined.
        _nests = [isinstance(_op1[0], Iterable), isinstance(_op2[0], Iterable)]

        #if both operands are not nested iterables, ensure they are
        #equal length, or pad accordingly and return the operation
        #if not any(_nests):

        _lens = [len(_op1), len(_op2)]
        _delta = abs(_lens[0] - _lens[1])

        if _delta:

            _pad = 0

            #truncate the second operand to match the length of the first
            if _lens[0] < _lens[1]:
                _op2 = _op2[:_lens[0]]

            #pad the end of the second operand by the last value to match the
            #number of elements in the first
            elif _lens[0] > _lens[1]:
                _op2 += (_op2[-1],)*_delta

        _result = ()

        if isinstance(_op1[0], Iterable):

            for _i, _v in enumerate(_op1):
                _result += (
                    TupleMath._operation(op, _v, _op2[_i], fail_on_empty),)

            return _result

        return tuple(map(op, _op1, _op2))

    @staticmethod
    def is_zero(tpl):
        """
        REturns true if all elements of the tuple are zero
        """

        return all(_i==0 for _i in tpl)

    @staticmethod
    def add(op1, op2=None, fail_on_empty=False):
        """
        Add two operands as tuples, lists of tuples, or accumulate
        a single list of tuples (op1)
        """

        return TupleMath._operation(op_add, op1, op2, fail_on_empty)

    @staticmethod
    def subtract(op1, op2=None, fail_on_empty=False):
        """
        Subtract two operands as tuples, lists of tuples, or accumulate
        a single list of tuples (op1)
        """

        return TupleMath._operation(op_sub, op1, op2, fail_on_empty)

    @staticmethod
    def multiply(op1, op2=None, fail_on_empty=False):
        """
        Multiply two operands as tuples, lists of tuples, or accumulate
        a single list of tuples (op1)
        """

        return TupleMath._operation(op_mul, op1, op2, fail_on_empty)

    @staticmethod
    def divide(op1, op2=None, fail_on_empty=False):
        """
        Divide two operands as tuples, lists of tuples, or accumulate
        a single list of tuples (op1)
        """

        return TupleMath._operation(op_div, op1, op2, fail_on_empty)

    @staticmethod
    def scale(tpl, factor, fail_on_empty=False):
        """
        Multiply each component of a tuple or list of tuples by a scalar factor
        """

        _len = len(tpl)

        #get length of longest tuple in list
        if isinstance(tpl[0], tuple):

            _len = 0
            _i = 0

            for _v in tpl:

                _i = len(_v)

                if _i > _len:
                    _len = _i

        return TupleMath._operation(op_mul, tpl, [factor]*_len, fail_on_empty)

    @staticmethod
    def mean(op1, op2=None, fail_on_empty=False):
        """
        Compute the arithmetic mean of two or more tuples
        lhs / rhs - tuples for which mean is to be computed
        if rhs is none / empty, lhs must be an iterable of tuples
        """

        _sum = TupleMath.add(op1, op2)

        #assume cumulative add (op1 = list of tuples, op2 = None)
        _count = len(op1)

        #if op1's first element is a number (not a tuple) and op2 is defined
        #we're averaging two tuples
        if not isinstance(op1[0], Iterable):

            if op2:
                _count = 2

        return TupleMath.scale(_sum, 1.0 / _count, fail_on_empty)

    @staticmethod
    def length(tpl, ref_point=None, fail_on_empty=False):
        """
        Calculate the length of a tuple as a vector from the origin
        If a list of tuples, length is calculated as distance between points
        if reference is defined, all points are calculated from the reference
        """

        _has_ref = ref_point is not None

        #length of a list of points in series or from reference point
        if isinstance(tpl[0], Iterable):

            _len = ()

            _prev = tpl[0]

            if _has_ref:
                _prev = ref_point
                _len = (TupleMath.length(
                    TupleMath.subtract(tpl[0], _prev, fail_on_empty),),)

            for _t in tpl[1:]:

                _len += (TupleMath.length(
                    TupleMath.subtract( _t, _prev, fail_on_empty)),)

                if not _has_ref:
                    _prev = _t

            if not _len:
                _len = TupleMath.length(_prev, fail_on_empty=fail_on_empty)

            if len(_len) == 1:
                return _len[0]

            return _len

        _tpl = tpl[:]

        if _has_ref:
            _tpl = TupleMath.subtract(tpl, ref_point, fail_on_empty)

        #vector length from origin to point
        _result = math.sqrt(sum([_v*_v for _v in _tpl]))

        return _result

    @staticmethod
    def unit(tpl, fail_on_empty=False):
        """
        Normalize a tuple / calculate the unit vector
        """

        _length = TupleMath.length(tpl, fail_on_empty=fail_on_empty)

        if not _length:
            return tpl

        return TupleMath.scale(tpl, (1.0 / _length), fail_on_empty)

    @staticmethod
    def dot(vec1, vec2):
        """
        Calculate the dot product of two tuples
        """

        _sum = 0.0

        for _i, _v in enumerate(vec1):
            _sum += _v * vec2[_i]

        return _sum

    @staticmethod
    def project(vec1, vec2, unit=False):
        """
        Return the projection of vec1 on vec2
        vec1 - Vector to project in tuple form
        vec2 - Target vector onto which projection is made in tuple form
        unit - indicates vec2 is a unit vector to save on length calc
        """

        _vec2_len = 1.0

        if not unit:
            _vec2_len = TupleMath.length(vec2)**2

        return TupleMath.scale(vec2, TupleMath.dot(vec1, vec2) / _vec2_len)

    @staticmethod
    def bearing_vector(angle):
        """
        Return a 2D vector in tuple form given the specified angle in radians
        """

        if not angle:
            return None

        _angle = float(angle)

        return (math.sin(_angle), math.cos(_angle), 0.0)

    @staticmethod
    def bearing(vector, up=(0.0, 1.0)):
        """
        Get the bearing of a vector in tuple form
        """

        if up != (0.0, 1.0):
            up = TupleMath.unit(up[0:2])

        _vec = TupleMath.unit(vector[0:2])

        _angle = math.acos(TupleMath.dot(up, _vec))

        if _vec[0] < 0.0:
            _angle = math.pi*2.0 - _angle

        return _angle

    @staticmethod
    def ortho(tpl, is_ccw=True, x_index=0, y_index=1):
        """
        Calculate the orthogonal of x_index and y_index
        """

        _x_sign = -1.0
        _y_sign = 1.0

        if not is_ccw:
            _x_sign, _y_sign = _y_sign, _x_sign

        return (_x_sign * tpl[y_index], _y_sign * tpl[x_index])

    @staticmethod
    def manhattan(lhs, rhs):
        """
        Compute the manhattan distance between two tuples
        Tuples of unequal length are padded with 0.0.
        """

        _distance = 0.0
        _delta = len(rhs) - len(lhs)

        #longer lhs
        if _delta < 0:
            rhs = rhs + (0.0,)*(abs(_delta))

        #longer rhs
        elif _delta > 0:
            lhs = lhs + (0.0,)*(_delta)

        return TupleMath._manhattan(lhs, rhs)

    @staticmethod
    def boolean(tpl):
        """
        Return a numeric tuple as a tuple of booleans.
        Zero = False, non-zero = True
        """

        return TupleMath.invert(TupleMath.invert(tpl))

    @staticmethod
    def invert(tpl):
        """
        Boolean inversion of a tuple.  Non-zero values are returned zero.
        Zero values are returned as one.
        """

        return tuple([not _v for _v in tpl])

    @staticmethod
    def _manhattan(lhs, rhs):
        """
        Optimized manhattan distance, with no tuple length checks
        """

        return [abs(rhs[_i] - _v) for _i, _v in enumerate(lhs)]

    @staticmethod
    def cross(src, dest, components=None):
        """
        Calculate the cross-product of two 3D vector tuples
        src - tuple representing starting vector
        dest - tuple representing ending vector
        components - tuple indicating which components to compute.
            Positions define components to cross (y/z, x/z, x/y)
            - 0 = skip; 1 = compute
            - components=(0,0,1) - compute cross of x and y components
        """

        if components is None:
            components = (1.0, 1.0, 1.0)

        assert len(src) == len(dest), """
        TupleMath.cross(): Source and destination vectors of unequal length
        """

        assert len(components) >= len(src), """
        TupleMath.cross(): Components undefined
        """

        _result = [0.0, 0.0, 0.0]
        _idx = (1, 2, 0, 1)

        for _i, _v in enumerate(src):

            if not components[_i]:
                continue

            _a = _idx[_i]
            _b = _idx[_i + 1]

            _result[_i] = src[_a]*dest[_b] - src[_b]*dest[_a]

        return _result

    @staticmethod
    def signed_bearing(src, dest):
        """
        Calculate the signed bearing between two vectors
        """

        _angle = TupleMath.bearing(src, dest)
        _cross = TupleMath.cross(src, dest)
        _dot = TupleMath.dot(_cross, (0.0, 0.0, 1.0))

        if _dot < 0.0:
            _angle *= -1.0

        return _angle

    @staticmethod
    def point_direction(point, vector, epsilon=0.000001):
        """
        Returns: -1 if left, 1 if right, 0 if on line
        """

        _d = TupleMath.cross(vector, point, (0.0, 0.0, 1.0))[2]

        if abs(_d) <= epsilon:
            return 0

        if _d < 0:
            return -1

        return 1

    @staticmethod
    def angle_between(vec1, vec2):
        """
        Return the angle between two vectors using dot product
        """

        _denom = TupleMath.length(vec1) * TupleMath.length(vec2)

        return math.acos(TupleMath.dot(vec1, vec2) / _denom)
