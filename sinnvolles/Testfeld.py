from vtk import *


final_shape = "final_shape.stl"
initial_shape = "initial_shape.stl"


#reading the shit
reader1 = vtk.vtkSTLReader()
reader1.SetFileName(final_shape)
reader1.Update()

reader2 = vtk.vtkSTLReader()
reader2.SetFileName(initial_shape)
reader2.Update()

polydata1 = vtk.vtkPolyData()
polydata1 = reader1.GetOutput()
polydata2 = vtk.vtkPolyData()
polydata2 = reader2.GetOutput()


pointNumberObject1 = polydata1.GetNumberOfPoints()
pointNumberObject2 = polydata2.GetNumberOfPoints()

print pointNumberObject1
print pointNumberObject2

pointsObject1 = []
pointsObject2 = []

box = vtk.vtkCubeSource()
box.SetXLength()

def storePoints(objectToBeStored):
  if objectToBeStored == "polydata1":
    for x in range(pointNumberObject1):
      pointsObject1.append(polydata1.GetPoints().GetPoint(x))
    print "Points of object 1 succesfully stored"
    print len(pointsObject1)

  elif objectToBeStored == "polydata2":
    for x in range(pointNumberObject2):
      pointsObject2.append(polydata2.GetPoints().GetPoint(x))
    print "Points of object 2 succesfully stored"
    print len(pointsObject2)

  else:
    print "Something went wrong with the point storing..."

storePoints("polydata1")


def getBoxValues(objectTobeValued):
  if objectTobeValued == "polydata1":
    xList = []
    yList = []
    zList = []
    completeList =[]

    for p in pointsObject1:
      xList.append(p[0])
      yList.append(p[1])
      zList.append(p[2])

    completeList.append(min(xList))
    completeList.append(max(xList))
    completeList.append(min(yList))
    completeList.append(max(yList))
    completeList.append(min(zList))
    completeList.append(max(zList))
  print completeList
  return completeList


def createQuader(objectToBeBoxed):
  box.SetBounds(getBoxValues(objectToBeBoxed))

createBox("polydata1")
print box.GetBounds()

extractGeometryBox = vtk.vtkExtractGeometry()
#extractGeometryBox.SetImplicitFunction(box)
extractGeometryBox.SetInputData(box)



booleanfilter = vtk.vtkBooleanOperationPolyDataFilter()
booleanfilter.SetOperationToDifference()
booleanfilter.SetInputConnection(0, extractGeometryBox.GetOutputPort())
booleanfilter.SetInputConnection(1, reader1.GetOutputPort())


"""
def getBoundaries(objectToBeAnalyzed):
  sameList = []
  if objectToBeAnalyzed == "polydata1":
    for x in pointsObject1:
      px = x[0]
      py = x[1]
      print py
      for x2 in pointsObject1:
        qx = x2[0]
        qy = x2[1]
        if abs(qx - px)< 0.05  and qy != py:
          sameList.append(abs(qy-py))
        else: 
          pass
  print sameList

getBoundaries("polydata1")
"""



















"""
#smooth the shit
smooth1 = vtk.vtkSmoothPolyDataFilter()
smooth1.SetInputConnection(reader1.GetOutputPort())
smooth1.Update()

smooth2 = vtk.vtkSmoothPolyDataFilter()
smooth2.SetInputConnection(reader2.GetOutputPort())
smooth2.Update()


#clean the shit
clean1 = vtk.vtkCleanPolyData()
clean1.SetInputConnection(smooth1.GetOutputPort())
clean1.ConvertStripsToPolysOn()
clean1.ConvertPolysToLinesOn()
clean1.ConvertLinesToPointsOn()
clean1.Update()

clean2 = vtk.vtkCleanPolyData()
clean2.SetInputConnection(smooth2.GetOutputPort())
clean2.ConvertStripsToPolysOn()
clean2.ConvertPolysToLinesOn()
clean2.ConvertLinesToPointsOn()
clean2.Update()


#triangle that shit
triangle1 = vtk.vtkTriangleFilter()
triangle1.SetInputConnection(clean1.GetOutputPort())
triangle1.PassVertsOff()
triangle1.PassLinesOff()
triangle1.Update()

triangle2 = vtk.vtkTriangleFilter()
triangle2.SetInputConnection(clean2.GetOutputPort())
triangle2.PassVertsOff()
triangle2.PassLinesOff()
triangle2.Update()


#normal that shit
normal1 = vtk.vtkPolyDataNormals()
normal1.SetInputConnection(triangle1.GetOutputPort())
normal1.ComputePointNormalsOn()
normal1.ComputeCellNormalsOff()
normal1.SplittingOff()
normal1.ConsistencyOn()
normal1.AutoOrientNormalsOff()
normal1.Update()

normal2 = vtk.vtkPolyDataNormals()
normal2.SetInputConnection(triangle2.GetOutputPort())
normal2.ComputePointNormalsOn()
normal2.ComputeCellNormalsOff()
normal2.SplittingOff()
normal2.ConsistencyOn()
normal2.AutoOrientNormalsOff()
normal2.Update()

booleanfilter = vtk.vtkBooleanOperationPolyDataFilter()
booleanfilter.SetOperationToDifference()
booleanfilter.SetInputConnection(0, normal1.GetOutputPort())
booleanfilter.SetInputConnection(1, normal2.GetOutputPort())
"""




mass1 = vtk.vtkMassProperties()
mass1.SetInputConnection(reader1.GetOutputPort())
mass1.Update()
volume1 = mass1.GetVolume()

mass2 = vtk.vtkMassProperties()
mass2.SetInputConnection(reader2.GetOutputPort())
mass2.Update()
volume2 = mass2.GetVolume()







mapper1 = vtk.vtkPolyDataMapper()
mapper1.SetInputConnection(reader1.GetOutputPort())

mapper2 = vtk.vtkPolyDataMapper()
mapper2.SetInputConnection(reader2.GetOutputPort())

mapper3 = vtk.vtkPolyDataMapper()
mapper3.SetInputConnection(booleanfilter.GetOutputPort())

actor1 = vtk.vtkActor()
actor1.SetMapper(mapper1)

actor2 = vtk.vtkActor()
actor2.SetMapper(mapper2)
#actor2.GetProperty().EdgeVisibilityOn()

actor3 = vtk.vtkActor()
actor3.SetMapper(mapper3)

renderer = vtk.vtkRenderer()
#renderer.AddActor(actor1)
renderer.AddActor(actor2)
renderer.AddActor(actor3)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

axes = vtk.vtkAxesActor()
widget = vtk.vtkOrientationMarkerWidget()
widget.SetOrientationMarker(axes)
widget.SetInteractor(interactor)
widget.SetEnabled(1)
widget.InteractiveOn()

window.Render()
interactor.Initialize()
interactor.Start() 
