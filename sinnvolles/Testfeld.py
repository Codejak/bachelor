from vtk import *


final_shape = "final_shape.stl"
initial_shape = "initial_shape.stl"


#define the class which creates objects store the data of the STL files
class STL_Object:
  numberOfSTLObjects = 0
  # initiation of the objects
  def __init__(self, fileName):

    #increasing the objectcounter
    STL_Object.numberOfSTLObjects += 1

    #definening the attributes
    self.fileName = fileName
    self.objectPoints = []
    self.xCoordinates = []
    self.yCoordinates = []
    self.zCoordinates = []

    #reads the Objekt from the stl data
    self.reader = vtk.vtkSTLReader()
    self.reader.SetFileName(fileName)
    self.reader.Update()
    self.polydata = vtk.vtkPolyData()
    self.polydata = self.reader.GetOutput()

    #determine number of Points
    self.numberOfPoints = self.polydata.GetNumberOfPoints()
    print "Number of Points in %s updated: %s" %(self.fileName, self.numberOfPoints)


  # determine the (new) number of points in the object
  def updateNumberOfPoints(self):
    self.numberOfPoints = self.polydata.GetNumberOfPoints()
    print "Number of Points in %s updated: %d" %(self.fileName, self.numberOfPoints)


  #store the point from the STL file into arrays to work with
  def storePoints(self):
    self.objectPoints = []
    for x in range(self.numberOfPoints):
      self.objectPoints.append(self.polydata.GetPoints().GetPoint(x))
    print "Points of %s succesfully stored. \nLength of the array: %d" %(self.fileName, len(self.objectPoints))
    self.storeCoordinates()


  #Store the individual axes-coordianes in arrays
  def storeCoordinates(self):
    self.xCoordinates = []
    self.yCoordinates = []
    self.zCoordinates = []
    for p in self.objectPoints:
       self.yCoordinates.append(p[1])
      self.zCoordinates.append(p[2])
    print "Coordinates of %s succesfully stored. \nLength of the arrays: \n %d \n %d \n %d" %(self.fileName, len(self.xCoordinates), len(self.yCoordinates),len(self.zCoordinates))




object1 = STL_Object("final_shape.stl")
#object1.updateNumberOfPoints()
object1.storePoints()







"""
box = vtk.vtkCubeSource()

box.SetBounds(getBoxValues("polydata1"))

triangledBox = vtk.vtkTriangleFilter()
triangledBox.SetInputConnection(box.GetOutputPort())
triangledBox.Update()

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







booleanfilter = vtk.vtkBooleanOperationPolyDataFilter()
booleanfilter.SetOperationToDifference()
booleanfilter.SetInputConnection(1, reader1.GetOutputPort())
booleanfilter.SetInputConnection(0, triangledBox.GetOutputPort())
booleanfilter.SetTolerance(0.000000000000000001)
"""







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

#mapper3 = vtk.vtkPolyDataMapper()
#mapper3.SetInputConnection(booleanfilter.GetOutputPort())

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
#renderer.AddActor(actor3)
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
"""
mapper1 = vtk.vtkPolyDataMapper()
mapper1.SetInputConnection(object1.reader.GetOutputPort())

actor1 = vtk.vtkActor()
actor1.SetMapper(mapper1)

renderer = vtk.vtkRenderer()
renderer.AddActor(actor1)
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