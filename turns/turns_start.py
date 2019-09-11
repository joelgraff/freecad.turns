# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- simulation ackermann drive forward
#--
#-- microelly 2018 v 0.14
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

# from say import *
# import nurbswb.pyob
#------------------------------

import FreeCAD as App
import FreeCADGui as Gui
import Sketcher
import Part

from PySide import QtCore


import numpy as np
import time

import turns.driver_sketch as ds

from .driver_sketch import DriverSketch


def add_object(name, color):
    """
    Add a Part::Feature to the active document
    """

    obj = App.ActiveDocument.addObject("Part::Feature", name)
    obj.ViewObject.LineColor = color

    return obj

def run():


    ds.clearReportView("Restart")

    fbs = ds.create(name="Driver")

    fbs.track1 = add_object('Track rear center', (1.0, 1.0, 1.0))
    fbs.track2 = add_object('Track rear right', (0.0, 1.0, 0.0))
    fbs.track3 = add_object('Track rear left', (1.0, 0.0, 0.0))
    fbs.track4 = add_object('Track front right', (0.0, 0.5, 0.0))
    fbs.track5 = add_object('Track front left', (0.5, 0.0, 0.0))

    _paths=Gui.Selection.getSelection()

    for _p in _paths:
        fbs.path = _p
        fbs.step = 0
        fbs.trackOn = 1
        fbs.width = 20
        fbs.beginSegment = 1
        fbs.endSegment = 200
        #fbs.car=App.ActiveDocument.Cone
        fbs.car = App.ActiveDocument.Sketch021 #('Auto')


    if False: # create a trailer
        trail = ds.create(name="Trailer")
        trail.trailerOn = 1
        trail.truck = fbs

        trail.trackOn = 1
        trail.width = 60

        #trail.car=App.ActiveDocument.Cylinder
        trail.car = App.ActiveDocument.Sketch022 #Auto001
        trail.endSegment = trail.truck.endSegment - 1

        trail.track1 = add_object('Track Trailer rear center', (1.0, 1.0, 1.0))
        trail.track2 = add_object('Track Trailer rear right', (0.0, 1.0, 0.0))
        trail.track3 = add_object('Track Trailer rear left', (1.0, 0.0, 0.0))
        trail.track4 = add_object('Track Trailer front right', (0.0, 0.5, 0.0))
        trail.track5 = add_object('Track Trailer front left', (0.5, 0.0, 0.0))

        trail.ViewObject.Proxy.methodA(trail)

    else:

        fbs.ViewObject.Proxy.methodA(fbs)

#-------------------------------

run()
