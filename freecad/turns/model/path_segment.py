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
PathSegment model object
"""

from ..support.tuple_math import TupleMath

class PathSegment():

    def __init__(self, previous, current):
        """
        Constructor
        """

        self.position = previous
        self.vector = TupleMath.unit(TupleMath.subtract(current, previous))
        self.angle = 0.0
        self.tangent = self.vector

    def __str__(self):
        """
        Stringify
        """

        return 'pos: {}; vec: {}; ang: {}; tan: {}'.format(
            str(self.position), str(self.vector), str(self.angle), str(self.tangent)
        )

    def set_look_ahead(self, vector):
        """
        Set the angle between the segment vector and passed vector
        vector - a unit vecotr in tuple form
        """

        self.angle = -TupleMath.signed_bearing(vector, self.vector)
        self.tangent = TupleMath.add(vector, self.vector)

    def finish(self):
        """
        Cleanup
        """

        self.position = None
        self.vector = None
        self.angle = 0.0
        self.tangent = None
