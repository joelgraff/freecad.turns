# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- simulation ackermann drive forward
#--
#-- microelly 2018 v 0.14
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

TESTHOME=True

# from say import *
# import nurbswb.pyob
#------------------------------

import FreeCAD as App
import FreeCADGui as Gui

from PySide import QtCore


import numpy as np
import time

import turns.feature_python
from turns import driver_sketch


def add_object(name, color):

    obj = App.ActiveDocument.addObject("Part::Feature",name)
    obj.ViewObject.LineColor = color

    return obj

def run():

    fbs=driver_sketch.create(name="Driver")

    fbs.rear_ctr = add_object('Rear center', (1.0, 1.0, 1.0))
    fbs.rear_rt = add_object('Rear right', (0.0, 1.0, 0.0))
    fbs.rear_lt = add_object('Rear left', (1.0, 0.0, 0.0))
    fbs.front_rt = add_object('Front right', (0.0, 0.5, 0.0))
    fbs.front_lt = add_object('Front left', (0.5, 0.0, 0.0))

    _paths = Gui.Selection.getSelection()

    for _p in _paths:

        fbs.path = _p
        fbs.step = 0
        fbs.trackOn = 1
        fbs.width = 20
        fbs.beginSegment = 1
        fbs.endSegment = 200

        fbs.car = App.ActiveDocument.Sketch021


    if 1: # create a trailer

        trail = driver_sketch.create(name="Trailer")
        trail.trailerOn = 1
        trail.truck = fbs

        trail.trackOn = 1
        trail.width = 60

        trail.car = App.ActiveDocument.Sketch022
        trail.endSegment = trail.truck.endSegment-1

        trail.rear_ctr = add_object('Trailer rear center', (1.0, 1.0, 1.0))
        trail.rear_rt = add_object('Trailer rear right', (0.0, 1.0, 0.0))
        trail.rear_lt = add_object('Trailer rear left', (1.0, 0.0, 0.0))
        trail.front_rt = add_object('Trailer front right', (0.0, 0.5, 0.0))
        trail.front_lt = add_object('Trailer front left', (0.5, 0.0, 0.0))

        trail.ViewObject.Proxy.methodA(trail)

    else:

        fbs.ViewObject.Proxy.methodA(fbs)

#-------------------------------

run()
