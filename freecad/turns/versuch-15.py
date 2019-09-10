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

import FreeCAD,FreeCADGui,Sketcher,Part

App = FreeCAD
Gui = FreeCADGui

from PySide import QtCore


import numpy as np
import time



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
		if obj.step<>0:
#			print "EX ",e
#			print "step ",obj.step
#			print "b2",vb2
#			print "a",va
#			print "b",vb
			FreeCAD.Console.PrintError(" \nEX step"+ str(obj.step)+" "+ str(e)+"\n")
		rc=-99

	if rc==0:
		a=App.ActiveDocument.recompute()
		tb=time.time()
		print "update time ",round(tb-ta,3)
		return

	for lup in range(1):
		# print "LLLLLLLLLLLOOOOP" ,lup
		sk.deleteAllGeometry()

		va2=va+vb2-vb
		vm=(va2+vb2)*0.5

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

	#	print "Move ..."
		try:
			sk.movePoint(m,1,vm,0)
		except Exception as e:
			FreeCAD.Console.PrintWarning("\n!!!!!!!!!!!!!!!"+ str(e))


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
#		print "ergebnis solve a_",rc


		sk.addConstraint(Sketcher.Constraint('Symmetric',b2,1,a2,1,m,1))

		rc=sk.solve()
#		print "ergebnis solve aa_",rc
#		sk.delConstraint(25)


		cb=sk.addConstraint(Sketcher.Constraint('Equal',12,8))
		rc=sk.solve()
#		print "ergebnis solve ac_",rc,"  bei ",cb

		rc=sk.solve()
#		print "ergebnis solve ad_",rc

		sk.addConstraint(Sketcher.Constraint('Equal',11,7))

		rc=sk.solve()
#		print "ergebnis solve ae_",rc


		sk.toggleDriving(a2x)



		cb=sk.addConstraint(Sketcher.Constraint('Equal',12,9))

		sk.toggleDriving(a2y)

		rc=sk.solve()
#		print "ergebnis solve b_",rc

		sk.addConstraint(Sketcher.Constraint('Equal',6,5))

		sk.delConstraint(25)

		rc=sk.solve()
#		print "ergebnis solve d_",rc

	#	for i in range(9,27):
	#		sk.setVirtualSpace(i, True)

		rc=sk.solve()
#		print "ergebnis solve e_",rc

		sk.toggleDriving(b2x)
		rc=sk.solve()
#		print "ergebnis solve Za_",rc

		sk.toggleDriving(b2x)
		rc=sk.solve()
#		print "ergebnis solve Zb_",rc

		a=App.ActiveDocument.recompute()
		tb=time.time()
		print e, "\nrecreate sketch time ",round(tb-ta,3)
		if rc==0:
			FreeCAD.Console.PrintWarning(" new and success step:"+ str(obj.step))


def updateSketch(obj):
	print "\n!-step:" + str(obj.step) + " for " + obj.Label

	rc=runAAA(obj,obj.b2,obj.b,obj.a)
	obj.a2=FreeCAD.Vector(obj.getDatum('a2x').Value,obj.getDatum('a2y').Value,)
	obj.a=FreeCAD.Vector(obj.getDatum('ax').Value,obj.getDatum('ay').Value,)







class FeaturePython:
	''' basic defs'''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def attach(self, vobj):
		self.Object = vobj.Object


	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None


class ViewProvider:
	''' basic defs '''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None


	def setupContextMenu(self, obj, menu):
		menu.clear()
		action = menu.addAction("simulate track")
		action.triggered.connect(lambda:self.methodA(obj.Object))
		action = menu.addAction("MyMethod #2")
		menu.addSeparator()
		action.triggered.connect(lambda:self.methodB(obj.Object))
		action = menu.addAction("Edit Sketch")
		action.triggered.connect(lambda:self.myedit(obj.Object))


	def myedit(self,obj):
		self.methodB(None)
		Gui.activeDocument().setEdit(obj.Name)
		self.methodA(None)

	def methodA(self,obj):
		print "Method A",obj.Label
		ss=2
		if not obj.trailerOn:
			anz=int(round(obj.path.Shape.Length/10))
	#		anz=10
			for s in range(obj.beginSegment,obj.endSegment+1):
			# for s in range(anz+1):
				obj.step=s
				a=FreeCAD.ActiveDocument.recompute()
				if s%ss==0: Gui.updateGui()

			FreeCAD.activeDocument().recompute()

		else:
			obj.truck.step=obj.truck.beginSegment
			for s in range(obj.truck.beginSegment,obj.truck.endSegment+1):
				obj.truck.step=s+1
				obj.step=s
				a=FreeCAD.ActiveDocument.recompute()
				if obj.error:
					print "fbs error -- break"
					break
				if s%ss==0: Gui.updateGui()

			FreeCAD.activeDocument().recompute()

		Gui.updateGui()
		FreeCAD.activeDocument().recompute()


	def methodB(self,obj):
		print "my method B Starter"
		FreeCAD.activeDocument().recompute()

	def methodC(self,obj):
		print "my method C After Edit finished"
		Gui.activateWorkbench("NurbsWorkbench")
		FreeCAD.activeDocument().recompute()

	def unsetEdit(self,vobj,mode=0):
		self.methodC(None)


	def doubleClicked(self,vobj):
		print "double clicked"
		self.myedit(vobj.Object)
		print "Ende double clicked"


def clearReportView(name):
	from PySide import QtGui
	mw=Gui.getMainWindow()
	r=mw.findChild(QtGui.QTextEdit, "Report view")
	r.clear()
	import time
	now = time.ctime(int(time.time()))
	App.Console.PrintWarning("Cleared Report view " +str(now)+" by " + name+"\n")


class DriverSketch(FeaturePython):
	'''Sketch Object with Python'''

	##\cond
	def __init__(self, obj, icon='/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/draw.svg'):
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
				obj.a= self.pts[obj.step]+FreeCAD.Vector(0,-80)


				updateSketch(obj)
				a=obj.a
				b=obj.b

				self.trackpoints = [FreeCAD.Vector(a)]
				self.trackpoints = []
				self.trackpoints2 = [FreeCAD.Vector(a)]
				#self.trackpoints2 = [FreeCAD.Vector(a)]
				self.trackpoints3 = [FreeCAD.Vector(a)]
				self.trackpoints4 = []
				self.trackpoints5 = []
				self.trailerpoints = [FreeCAD.Vector(a)]
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
				self.trackpoints += [FreeCAD.Vector(a2)]

				kvr=0.3*obj.width/50

				t2=(obj.b2-obj.a2)
				vr=FreeCAD.Vector(t2).cross(FreeCAD.Vector(0,0,1))*kvr
				vl=FreeCAD.Vector(t2).cross(FreeCAD.Vector(0,0,1))*(-kvr)
				self.trackpoints2 += [FreeCAD.Vector(a2)+vr]
				self.trackpoints3 += [FreeCAD.Vector(a2)+vl]

				t2=(obj.b2-obj.a2)
				vr=FreeCAD.Vector(t2).cross(FreeCAD.Vector(0,0,1))*kvr
				vl=FreeCAD.Vector(t2).cross(FreeCAD.Vector(0,0,1))*(-kvr)

				self.trackpoints4 += [FreeCAD.Vector(b2)+vr]
				self.trackpoints5 += [FreeCAD.Vector(b2)+vl]

				targ=obj.car
				db=b2-a2
				alpha=np.arctan2(db.x,db.y)*180.0/np.pi
				if targ<>None:
					targ.Placement=FreeCAD.Placement(FreeCAD.Vector(b2),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),-alpha))

#				print ("okay!! Label,step,trackpoints=", obj.Label,obj.step,len(self.trackpoints))

				try:
					t2=t2.normalize()
					t1=(obj.b-obj.a)
					t1=t1.normalize()
				except:
					return

				if t2==t1:
					print "parallel"
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
			self.trailerpoints += [FreeCAD.Vector(a2)]

			if obj.trackOn:

				'''
				if obj.track1 <> None:
					obj.track1.Shape=Part.makePolygon(self.trackpoints+[FreeCAD.Vector(a2)])

				if obj.track2 <> None:
					obj.track2.Shape=Part.makePolygon(self.trackpoints2+[FreeCAD.Vector(a2)])

				if obj.track3 <> None:
					obj.track3.Shape=Part.makePolygon(self.trackpoints3+[FreeCAD.Vector(a2)])

				if obj.track4 <> None:
					obj.track4.Shape=Part.makePolygon(self.trackpoints4+[self.trackpoints2[-1],self.trackpoints4[-1],FreeCAD.Vector(b2)])


				if obj.track5 <> None:
					obj.track5.Shape=Part.makePolygon(self.trackpoints5+[self.trackpoints3[-1],self.trackpoints5[-1],FreeCAD.Vector(b2)])
				'''


				if obj.track1 <> None and len(self.trackpoints)>2:
					obj.track1.Shape=Part.makePolygon(self.trackpoints+[FreeCAD.Vector(a2)])

				if obj.track2 <> None and len(self.trackpoints2)>2:
					obj.track2.Shape=Part.makePolygon(self.trackpoints2)

				if obj.track3 <> None and len(self.trackpoints3)>2:
					obj.track3.Shape=Part.makePolygon(self.trackpoints3)

				if obj.track4 <> None and len(self.trackpoints4)>2:
					obj.track4.Shape=Part.makePolygon(self.trackpoints4)

				if obj.track5 <> None and len(self.trackpoints5)>2:
					obj.track5.Shape=Part.makePolygon(self.trackpoints5)


			print ("okay!! Label,step,trackpoints=", obj.Label,obj.step,len(self.trackpoints))



	def someOtherFunction(self):
		print ("run auto update")
		FreeCAD.ActiveDocument.recompute()



	def execute(self,obj):
		print "! execute ...."+obj.Label


		obj.recompute()
		try:
			if obj.trackOn:
				a2=obj.a2
				b2=obj.b2
				if obj.track1 <> None:
					obj.track1.Points=self.trackpoints+[FreeCAD.Vector(a2)]
					obj.track1.Closed=False

				if obj.track2 <> None:
					obj.track2.Points=self.trackpoints2#+[FreeCAD.Vector(a2)]
					obj.track2.Closed=False

				if obj.track3 <> None:
					obj.track3.Points=self.trackpoints3#+[FreeCAD.Vector(a2)]
					obj.track3.Closed=False

				if obj.track4 <> None:
					obj.track4.Points=self.trackpoints4#+[self.trackpoints2[-1],self.trackpoints4[-1],FreeCAD.Vector(b2)]
					obj.track4.Closed=False

				if obj.track5 <> None:
					obj.track5.Points=self.trackpoints5#+[self.trackpoints3[-1],self.trackpoints5[-1],FreeCAD.Vector(b2)]
					obj.track5.Closed=False
		except:
			pass


def createDriverSketch(name="MyDriver"):

	obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
	DriverSketch(obj)
	return obj


def run():

#if __name__ == '__main__':

	clearReportView("Restart")

	fbs=createDriverSketch(name="Driver")

	fbs.track1 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track rear center")
	fbs.track1.ViewObject.LineColor=(1.,1.,1.)
	fbs.track2 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track rear right")
	fbs.track2.ViewObject.LineColor=(0.,1.,0.)
	fbs.track3 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track rear left")
	fbs.track3.ViewObject.LineColor=(1.,0.,0.)
	fbs.track4 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track front right")
	fbs.track4.ViewObject.LineColor=(0.,0.5,0.)
	fbs.track5 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track front left")
	fbs.track5.ViewObject.LineColor=(0.5,0.,0.)


	if TESTHOME:

		pathes=[
	#		App.ActiveDocument.Sketch003,
	#		App.ActiveDocument.Sketch002,
			App.ActiveDocument.Sketch,
	#		App.ActiveDocument.Sketch004,
	#		App.ActiveDocument.Sketch005,
		]

	else:
		pathes=Gui.Selection.getSelection()


	for p in pathes:
		fbs.path=p
		fbs.step=0
		fbs.trackOn=1
		fbs.width=20
		fbs.beginSegment=1
		fbs.endSegment=20
		#fbs.car=App.ActiveDocument.Cone
		fbs.car=App.ActiveDocument.Sketch021
        

	if 1: # create a trailer
		trail=createDriverSketch(name="Trailer")
		trail.trailerOn=1
		trail.truck=fbs

		trail.trackOn=1
		trail.width=60
		#trail.car=App.ActiveDocument.Cylinder
		trail.car=App.ActiveDocument.Sketch022
		trail.endSegment=trail.truck.endSegment-1

		trail.track1 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track Trailer rear center")
		trail.track1.ViewObject.LineColor=(1.,1.,1.)
		trail.track2 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track Trailer rear right")
		trail.track2.ViewObject.LineColor=(0.,1.,0.)
		trail.track3 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track Trailer rear left")
		trail.track3.ViewObject.LineColor=(1.,0.,0.)
		trail.track4 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track Trailer front right")
		trail.track4.ViewObject.LineColor=(0.,0.5,0.)
		trail.track5 = FreeCAD.ActiveDocument.addObject("Part::Feature","Track Trailer front left")
		trail.track5.ViewObject.LineColor=(0.5,0.,0.)

		trail.ViewObject.Proxy.methodA(trail)

	else:

		fbs.ViewObject.Proxy.methodA(fbs)

#-------------------------------

run()
