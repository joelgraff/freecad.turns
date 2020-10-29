import FreeCADGui as Gui

from ...examples.select_drag.select_drag_tracker import SelectDragTracker

def dump_graph():

    utils.dump_node(Gui.ActiveDocument.ActiveView.getSceneGraph())

def gen_tracker():

    _t = SelectDragTracker(Gui.ActiveDocument.ActiveView)
    _t.insert_into_scenegraph()

    return _t

def generate():

    dump_graph()

    return gen_tracker()

def finish(tracker):

    tracker.finish()

    dump_graph()