def run_FreeCAD_swept(self):
	ta=time.time()
	l=self.getData("steps")
	step=self.getData("step")

	# the border of the car
	trackpoints=self.getData("trackPoints")
#	say(trackpoints)
	path=self.getPinObject("Path")
#	say(path)
	pts=path.discretize(l+1)
#	say(pts)
	centerAxis=self.getData("centerAxis")
#	return
	pols=[]
	pms=[]
	pts=FreeCAD.ActiveDocument.Sketch.Shape.Edge1.discretize(l+1)

	centers=[]
	a=pts[0]+centerAxis
	pols=[Part.makePolygon([a,pts[0]])]
	for i in range(l):
		b=pts[i]
		b2=pts[i+1]

		A=np.array([[b.x-a.x,b.y-a.y],[b.x-b2.x,b.y-b2.y]])
		B=np.array([(b-a).dot(a),(b-b2).dot((b+b2)*0.5)])
		x=np.linalg.solve(A,B)
		m=FreeCAD.Vector(x[0],x[1])
		centers += [m]
		r=FreeCAD.Rotation(b-m,b2-m)
		pm=FreeCAD.Placement(FreeCAD.Vector(),r,m)

		a2=pm.multVec(a)
		pols += [Part.makePolygon([a2,b2])]
		pms += [pm]

		a=a2

	# the axes flow of the car movement
	flows = Part.Compound(pols)
	self.setPinObject("flowAxes_out",flows)

	# calculate the list of transformations
	pm=FreeCAD.Placement()
	pms2=[pm]
	for p in pms:
		pm=p.multiply(pm)
		pms2 += [pm]

	# the tracks of the trackpoints
	tcols=[]
	for c0 in trackpoints:
		ptcs=[p.multVec(c0) for p in pms2]
		tcols+= [Part.makePolygon(ptcs)]
	shapea=Part.Compound(tcols)
	
	#shapea=Part.makePolygon(centers)
	
	self.setPinObject("tracks_out",shapea)

	# display the starting car
	car=trackpoints+[trackpoints[0]]
	# Part.show(Part.makePolygon(trackpoints+[trackpoints[0]]))

	# display the final car
	carend=[pms2[step].multVec(c) for c in car]
	shape=Part.makePolygon(carend)
	#say(shape)
	self.setPinObject("Car_out",shape)
	self.outExec.call()


	say(time.time()-ta)