import FreeCAD as App
import FreeCADGui as Gui

import numpy as np
import Part

import Sketcher

import time

from PySide import QtCore
from PySide import QtGui

from turns.feature_python import FeaturePython, ViewProvider

def create(name="MyDriver"):

    obj = App.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
    DriverSketch(obj)

    return obj

def runAAA(obj,vb2,vb,va):
    ta=time.time()

    sk=obj

    try:
        rc=obj.solve()

        if rc==0:
            try:
                obj.setDatum('b2x',vb2.x)
                obj.setDatum('b2y',vb2.y)
                rc=sk.solve()
            except:
                obj.setDatum('b2y',vb2.y)
                obj.setDatum('b2x',vb2.x)
                rc=sk.solve()
        if rc==0:
            try:
                obj.setDatum('ax',va.x)
                obj.setDatum('ay',va.y)
                rc=sk.solve()
            except:
                obj.setDatum('ay',va.y)
                obj.setDatum('ax',va.x)
                rc=sk.solve()
        if rc==0:
            try:
                obj.setDatum('by',vb.y)
                obj.setDatum('bx',vb.x)
                rc=sk.solve()
            except:
                obj.setDatum('bx',vb.x)
                obj.setDatum('by',vb.y)
                rc=sk.solve()

    except Exception as e:
        if obj.step != 0:
#			print "EX ",e
#			print "step ",obj.step
#			print "b2",vb2
#			print "a",va
#			print "b",vb
            App.Console.PrintError(" \nEX step"+ str(obj.step)+" "+ str(e)+"\n")
        rc=-99

    App.Console.PrintWarning('\n\tstep = ' + str(obj.step) + 'rc = ' + str(rc))

    if rc==0:
        a=App.ActiveDocument.recompute()
        tb=time.time()
        print ("update time ",round(tb-ta,3))
        return

    for lup in range(1):

        sk.deleteAllGeometry()

        va2 = va + vb2 - vb
        vm = (va2 + vb2) * 0.5

        b2=sk.addGeometry(Part.Point(vb2))
        b=sk.addGeometry(Part.Point(vb))
        a=sk.addGeometry(Part.Point(va))
        a2=sk.addGeometry(Part.Point(va2))
        m=sk.addGeometry(Part.Point(vm))


        b2x=sk.addConstraint(Sketcher.Constraint('DistanceX',b2,1,vb2.x))
        sk.renameConstraint(b2x, u'b2x')
        b2y=sk.addConstraint(Sketcher.Constraint('DistanceY',b2,1,vb2.y))
        sk.renameConstraint(b2y, u'b2y')
        c=sk.addConstraint(Sketcher.Constraint('DistanceX',b,1,vb.x))
        sk.renameConstraint(c, u'bx')
        c=sk.addConstraint(Sketcher.Constraint('DistanceY',b,1,vb.y))
        sk.renameConstraint(c, u'by')
        c=sk.addConstraint(Sketcher.Constraint('DistanceX',a,1,va.x))
        sk.renameConstraint(c, u'ax')
        c=sk.addConstraint(Sketcher.Constraint('DistanceY',a,1,va.y))
        sk.renameConstraint(c, u'ay')

        a2x=sk.addConstraint(Sketcher.Constraint('DistanceX',a2,1,va2.x))
        sk.renameConstraint(a2x, u'a2x')
        a2y=sk.addConstraint(Sketcher.Constraint('DistanceY',a2,1,va2.y))
        sk.renameConstraint(a2y, u'a2y')


        ab=sk.addGeometry(Part.LineSegment(va,vb),False)
        sk.addConstraint(Sketcher.Constraint('Coincident',ab,1,a,1))
        sk.addConstraint(Sketcher.Constraint('Coincident',ab,2,b,1))

        a2b2=sk.addGeometry(Part.LineSegment(va2,vb2),False)
        sk.addConstraint(Sketcher.Constraint('Coincident',a2b2,1,a2,1))
        sk.addConstraint(Sketcher.Constraint('Coincident',a2b2,2,b2,1))


        lab=sk.addGeometry(Part.LineSegment(va,va2),False)
        sk.addConstraint(Sketcher.Constraint('Coincident',lab,1,a,1))
        sk.toggleConstruction(lab)

        sk.addConstraint(Sketcher.Constraint('Perpendicular',lab,ab))

        r=sk.addGeometry(Part.LineSegment(vm,vb),False)
        sk.addConstraint(Sketcher.Constraint('Coincident',r,1,m,1))
        sk.addConstraint(Sketcher.Constraint('Coincident',r,2,b,1))
        sk.toggleConstruction(r)

        sk.addConstraint(Sketcher.Constraint('PointOnObject',lab,2,r))

        print ("Move ...")
        try:
            sk.movePoint(m,1,vm,0)
        except Exception as e:
            App.Console.PrintWarning("\n!!!!!!!!!!!!!!!"+ str(e))


        b2m=sk.addGeometry(Part.LineSegment(vb2,vm),False)
        sk.addConstraint(Sketcher.Constraint('Coincident',b2m,1,b2,1))
        sk.addConstraint(Sketcher.Constraint('Coincident',b2m,2,m,1))
        sk.toggleConstruction(b2m)

        a2m=sk.addGeometry(Part.LineSegment(va2,vm),False)
        sk.addConstraint(Sketcher.Constraint('Coincident',a2m,1,a2,1))
        sk.addConstraint(Sketcher.Constraint('Coincident',a2m,2,m,1))
        sk.toggleConstruction(a2m)

        a2l=sk.addGeometry(Part.LineSegment(va2,vm),False)
        sk.addConstraint(Sketcher.Constraint('Coincident',a2l,1,a2,1))
        sk.addConstraint(Sketcher.Constraint('Coincident',a2l,2,lab,2))
        sk.toggleConstruction(a2l)

        b2l=sk.addGeometry(Part.LineSegment(vb2,vm),False)
        sk.addConstraint(Sketcher.Constraint('Coincident',b2l,1,b2,1))
        sk.addConstraint(Sketcher.Constraint('Coincident',b2l,2,lab,2))
        sk.toggleConstruction(b2l)

        rc=sk.solve()
        print ("ergebnis solve a_",rc)

        sk.addConstraint(Sketcher.Constraint('Symmetric',b2,1,a2,1,m,1))

        rc=sk.solve()
        print ("ergebnis solve aa_",rc)
        sk.delConstraint(25)


        cb=sk.addConstraint(Sketcher.Constraint('Equal',12,8))
        rc=sk.solve()
        print ("ergebnis solve ac_",rc,"  bei ",cb)

        rc=sk.solve()
        print ("ergebnis solve ad_",rc)
        sk.addConstraint(Sketcher.Constraint('Equal',11,7))

        rc=sk.solve()
        print ("ergebnis solve ae_",rc)

        sk.toggleDriving(a2x)



        cb=sk.addConstraint(Sketcher.Constraint('Equal',12,9))

        sk.toggleDriving(a2y)

        rc=sk.solve()
        print ("ergebnis solve b_",rc)

        sk.addConstraint(Sketcher.Constraint('Equal',6,5))

        sk.delConstraint(25)

        rc=sk.solve()
        print ("ergebnis solve d_",rc)

        for i in range(9,27):
            sk.setVirtualSpace(i, True)

        rc=sk.solve()
        print ("ergebnis solve e_",rc)

        sk.toggleDriving(b2x)
        rc=sk.solve()
        print ("ergebnis solve Za_",rc)

        sk.toggleDriving(b2x)
        rc=sk.solve()
        print ("ergebnis solve Zb_",rc)

        a=App.ActiveDocument.recompute()
        tb=time.time()
        print ("\nrecreate sketch time ",round(tb-ta,3))
        if rc==0:
            App.Console.PrintWarning(" new and success step:"+ str(obj.step))

def clearReportView(name):

    mw=Gui.getMainWindow()
    r=mw.findChild(QtGui.QTextEdit, "Report view")
    r.clear()

    now = time.ctime(int(time.time()))
    App.Console.PrintWarning("Cleared Report view " +str(now)+" by " + name+"\n")


def updateSketch(obj):

    print ("\n!-step:" + str(obj.step) + " for " + obj.Label)

    rc=runAAA(obj,obj.b2,obj.b,obj.a)
    obj.a2=App.Vector(obj.getDatum('a2x').Value,obj.getDatum('a2y').Value,)
    obj.a=App.Vector(obj.getDatum('ax').Value,obj.getDatum('ay').Value,)

class DriverSketch(FeaturePython):
    '''Sketch Object with Python'''

    ##\cond
    def __init__(self, obj, icon='/home/thomas/.App/Mod/App-nurbs/icons/draw.svg'):
        obj.Proxy = self
        self.Type = self.__class__.__name__
        self.obj2 = obj
        obj.addProperty("App::PropertyBool",'clearReportview', 'Base',"clear window for every execute")
        obj.addProperty("App::PropertyBool",'error', 'Base',"error solving sketch")
#		obj.addProperty("App::PropertyBool",'autoupdate', 'Base',"auto recompute")

        obj.addProperty("App::PropertyLink",'path')
        obj.addProperty("App::PropertyBool",'trackOn')
        obj.addProperty("App::PropertyLink",'track1')
        obj.addProperty("App::PropertyLink",'track2')
        obj.addProperty("App::PropertyLink",'track3')
        obj.addProperty("App::PropertyLink",'track4')
        obj.addProperty("App::PropertyLink",'track5')

        obj.addProperty("App::PropertyBool",'trailerOn')
        obj.addProperty("App::PropertyLink",'truck')
        obj.addProperty("App::PropertyLink",'car')

        obj.addProperty("App::PropertyInteger",'step')
        obj.addProperty("App::PropertyInteger",'beginSegment').beginSegment=3
        obj.addProperty("App::PropertyInteger",'endSegment').endSegment=50
        obj.addProperty('App::PropertyVector','b2')
        obj.addProperty('App::PropertyVector','a2')
        obj.addProperty('App::PropertyVector','b')
        obj.addProperty('App::PropertyVector','a')
        obj.addProperty('App::PropertyFloat','width').width=50.



        ViewProvider(obj.ViewObject)
        self.trackpoints = []
        self.trackpoints2 = []
        self.trackpoints3 = []
        self.trackpoints4 = []
        self.trackpoints5 = []
        self.trailerpoints=[]
    ##\endcond


    def myExecute(proxy,obj):

        debug=False
        debug=True


        return

    def onChanged(self, obj, prop):

        #print('onchanged', self, obj, prop)
#
        if prop=='step':
            a2=obj.a2
            if obj.clearReportview:
                clearReportView(obj.Label)
            print ("onChange", prop,obj.Label)
            if not hasattr(obj,'trackOn'): return

            if obj.trailerOn:
                self.pts=obj.truck.Proxy.trailerpoints
            try: self.pts
            except:
                anz=int(round(obj.path.Shape.Length/10))
                self.pts=obj.path.Shape.discretize(anz+1)

            if obj.step>obj.endSegment:
                return

            if obj.step==obj.beginSegment:

                if obj.trailerOn:
                    self.pts=obj.truck.Proxy.trailerpoints
                else:
                    anz=int(round(obj.path.Shape.Length/10))
                    self.pts=obj.path.Shape.discretize(anz+1)


#				print "startposition"
                obj.b2= self.pts[obj.step+1]
                obj.b= self.pts[obj.step]
                obj.a= self.pts[obj.step]+App.Vector(0,-80)


                updateSketch(obj)
                a=obj.a
                b=obj.b

                self.trackpoints = [App.Vector(a)]
                self.trackpoints = []
                self.trackpoints2 = [App.Vector(a)]
                #self.trackpoints2 = [App.Vector(a)]
                self.trackpoints3 = [App.Vector(a)]
                self.trackpoints4 = []
                self.trackpoints5 = []
                self.trailerpoints = [App.Vector(a)]
                self.placements=[]


            else:
#				print "Alter Wert"
#				print "b2",obj.b2
#				print "b",obj.b
#				print "a",obj.a
#
#				print "--"
                b2= obj.b2
                a2= obj.a2

                b= obj.b
                a= obj.a

                obj.b2= self.pts[obj.step+1]

#				t2=(b2-obj.a)
                self.trackpoints += [App.Vector(a2)]

                kvr=0.3*obj.width/50

                t2=(obj.b2-obj.a2)
                vr=App.Vector(t2).cross(App.Vector(0,0,1))*kvr
                vl=App.Vector(t2).cross(App.Vector(0,0,1))*(-kvr)
                self.trackpoints2 += [App.Vector(a2)+vr]
                self.trackpoints3 += [App.Vector(a2)+vl]

                t2=(obj.b2-obj.a2)
                vr=App.Vector(t2).cross(App.Vector(0,0,1))*kvr
                vl=App.Vector(t2).cross(App.Vector(0,0,1))*(-kvr)

                self.trackpoints4 += [App.Vector(b2)+vr]
                self.trackpoints5 += [App.Vector(b2)+vl]

                targ=obj.car
                db=b2-a2
                alpha=np.arctan2(db.x,db.y)*180.0/np.pi
                if targ:
                    targ.Placement=App.Placement(App.Vector(b2),App.Rotation(App.Vector(0,0,1),-alpha))

#				print ("okay!! Label,step,trackpoints=", obj.Label,obj.step,len(self.trackpoints))

                try:
                    t2=t2.normalize()
                    t1=(obj.b-obj.a)
                    t1=t1.normalize()
                except:
                    return

                if t2==t1:
                    print ("parallel")
                    obj.a2=obj.a+obj.b2-obj.b
                    obj.b=b2
                    obj.a=a2
                    obj.deleteAllGeometry()
                    #self.trackpoints += [a2]
                else:
                    obj.b=b2
                    obj.a=a2
                    updateSketch(obj)

            obj.recompute()
            self.trailerpoints += [App.Vector(a2)]

            if obj.trackOn:

                '''
                if obj.track1 <> None:
                    obj.track1.Shape=Part.makePolygon(self.trackpoints+[App.Vector(a2)])

                if obj.track2 <> None:
                    obj.track2.Shape=Part.makePolygon(self.trackpoints2+[App.Vector(a2)])

                if obj.track3 <> None:
                    obj.track3.Shape=Part.makePolygon(self.trackpoints3+[App.Vector(a2)])

                if obj.track4 <> None:
                    obj.track4.Shape=Part.makePolygon(self.trackpoints4+[self.trackpoints2[-1],self.trackpoints4[-1],App.Vector(b2)])


                if obj.track5 <> None:
                    obj.track5.Shape=Part.makePolygon(self.trackpoints5+[self.trackpoints3[-1],self.trackpoints5[-1],App.Vector(b2)])
                '''


                if obj.track1 and len(self.trackpoints)>2:
                    obj.track1.Shape=Part.makePolygon(self.trackpoints+[App.Vector(a2)])

                if obj.track2 and len(self.trackpoints2)>2:
                    obj.track2.Shape=Part.makePolygon(self.trackpoints2)

                if obj.track3 and len(self.trackpoints3)>2:
                    obj.track3.Shape=Part.makePolygon(self.trackpoints3)

                if obj.track4 and len(self.trackpoints4)>2:
                    obj.track4.Shape=Part.makePolygon(self.trackpoints4)

                if obj.track5 and len(self.trackpoints5)>2:
                    obj.track5.Shape=Part.makePolygon(self.trackpoints5)


            print ("okay!! Label,step,trackpoints=", obj.Label,obj.step,len(self.trackpoints))



    def someOtherFunction(self):
        print ("run auto update")
        App.ActiveDocument.recompute()

    def execute(self,obj):
        print ('! execute ....' + obj.Label)


        obj.recompute()
        try:
            if obj.trackOn:
                a2=obj.a2
                b2=obj.b2
                if obj.track1:
                    obj.track1.Points=self.trackpoints+[App.Vector(a2)]
                    obj.track1.Closed=False

                if obj.track2:
                    obj.track2.Points=self.trackpoints2#+[App.Vector(a2)]
                    obj.track2.Closed=False

                if obj.track3:
                    obj.track3.Points=self.trackpoints3#+[App.Vector(a2)]
                    obj.track3.Closed=False

                if obj.track4:
                    obj.track4.Points=self.trackpoints4#+[self.trackpoints2[-1],self.trackpoints4[-1],App.Vector(b2)]
                    obj.track4.Closed=False

                if obj.track5:
                    obj.track5.Points=self.trackpoints5#+[self.trackpoints3[-1],self.trackpoints5[-1],App.Vector(b2)]
                    obj.track5.Closed=False
        except:
            pass