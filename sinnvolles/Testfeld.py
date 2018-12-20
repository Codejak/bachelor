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

    completeList.append(min(xList) + 0.01)
    completeList.append(max(xList) - 0.01)
    completeList.append(min(yList) + 0.01)
    completeList.append(max(yList) - 0.01) 
    completeList.append(min(zList) + 0.001)
    completeList.append(max(zList) - 0.001)
  print completeList
  return completeList


storePoints("polydata1")
box.SetBounds(getBoxValues("polydata1"))

triangledBox = vtk.vtkTriangleFilter()
triangledBox.SetInputConnection(box.GetOutputPort())
triangledBox.Update()


booleanfilter = vtk.vtkBooleanOperationPolyDataFilter()
booleanfilter.SetOperationToDifference()
booleanfilter.SetInputConnection(1, reader1.GetOutputPort())
booleanfilter.SetInputConnection(0, triangledBox.GetOutputPort())
booleanfilter.SetTolerance(0.000000000000000001)



"""
#smooth the shit
smooth1 = vtk.vtkSmoothPolyDataFilter()
smooth1.SetInputConnection(reader1.GetOutputPort())
smooth1.Update()

#clean the shit
clean1 = vtk.vtkCleanPolyData()
clean1.SetInputConnection(smooth1.GetOutputPort())
clean1.ConvertStripsToPolysOn()
clean1.ConvertPolysToLinesOn()
clean1.ConvertLinesToPointsOn()
clean1.Update()

#triangle that shit
triangle1 = vtk.vtkTriangleFilter()
triangle1.SetInputConnection(clean1.GetOutputPort())
triangle1.PassVertsOff()
triangle1.PassLinesOff()
triangle1.Update()

#normal that shit
normal1 = vtk.vtkPolyDataNormals()
normal1.SetInputConnection(triangle1.GetOutputPort())
normal1.ComputePointNormalsOn()
normal1.ComputeCellNormalsOff()
normal1.SplittingOff()
normal1.ConsistencyOn()
normal1.AutoOrientNormalsOff()
normal1.Update()

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
actor3.GetProperty().EdgeVisibilityOn()

renderer = vtk.vtkRenderer()
#renderer.AddActor(actor1)
#renderer.AddActor(actor2)
renderer.AddActor(actor3)
renderer.SetBackground(1,1,1)

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
