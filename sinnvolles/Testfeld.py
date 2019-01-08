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

    #defining the attributes
    self.fileName = fileName
    self.objectPoints = []
    self.xCoordinates = []
    self.yCoordinates = []
    self.zCoordinates = []
    self.maxX = 0
    self.minX = 0
    self.maxY = 0 
    self.minY = 0
    self.maxZ = 0
    self.minZ = 0

    #reads the Objekt from the stl file
    self.reader = vtk.vtkSTLReader()
    self.reader.SetFileName(fileName)
    self.reader.Update()
    self.polydata = vtk.vtkPolyData()
    self.polydata = self.reader.GetOutput()

    #determine the number of Points
    self.numberOfPoints = self.polydata.GetNumberOfPoints()
    print "\nTrying to store -%s-! Point Number:%s" %(self.fileName, self.numberOfPoints)

    #store the point from the STL file into arrays to work with
    self.objectPoints = []
    for x in range(self.numberOfPoints):
      self.objectPoints.append(self.polydata.GetPoints().GetPoint(x))
    print "\n%s succesfully stored. Length of the storing array: %d" %(self.fileName, len(self.objectPoints))




  #determine the (new) number of points in the object
  def updateNumberOfPoints(self):
    self.numberOfPoints = len(self.objectPoints)
    print "\nNumber of Points in %s updated: %s" %(self.fileName, self.numberOfPoints)


  #store the individual axes-coordianes in arrays
  def updateCoordinates(self):
    self.xCoordinates = []
    self.yCoordinates = []
    self.zCoordinates = []
    for p in self.objectPoints:
      self.xCoordinates.append(p[0])
      self.yCoordinates.append(p[1])
      self.zCoordinates.append(p[2])

    #determine the extrema 
    self.maxX = max(self.xCoordinates)
    self.minX = min(self.xCoordinates)
    self.maxY = max(self.yCoordinates)
    self.minY = min(self.yCoordinates)
    self.maxZ = max(self.zCoordinates)
    self.minZ = min(self.zCoordinates)
    print "\nCoordinates of %s succesfully updated. Length of the arrays: %s, %s, %s \nThese are the min/max coordinates: X[%s,%s], Y[%s,%s], Z[%s,%s] " %(self.fileName, len(self.xCoordinates), len(self.yCoordinates), len(self.zCoordinates), self.minX,self.maxX,self.minY,self.maxY,self.minZ,self.maxZ)
    self.updateNumberOfPoints()

  """
  #get rid of the irrelevant points
  def deleteBoxPoints(self):
    newlist = []
    for i in self.objectPoints:
      if (self.minX - 0.1) < i[0] < (self.minX + 0.1):
        pass
      elif (self.maxX - 0.1) < i[0] < (self.maxX + 0.1):
        pass
      if (self.minY - 0.1) < i[1] < (self.minY + 0.1):
        pass
      elif (self.maxY - 0.1) < i[1] < (self.maxY + 0.1):
        pass
      else:
        newlist.append(i)
      self.objectPoints = newlist
  """


  #reverse the STL file
  def buildNegative(self):
    #create the box to build the negative with
    self.box = vtk.vtkCubeSource()
    completeList = []
    completeList.append(self.minX + 0.01)
    completeList.append(self.maxX - 0.01)
    completeList.append(self.minY + 0.01)
    completeList.append(self.maxY - 0.01) 
    completeList.append(self.minZ + 0.0000001)
    completeList.append(self.maxZ - 0.0000001)
    self.box.SetBounds(completeList)

    self.triangledBox = vtk.vtkTriangleFilter()
    self.triangledBox.SetInputConnection(self.box.GetOutputPort())
    self.triangledBox.Update()

    #get the difference between the box and the file
    self.booleanfilter = vtk.vtkBooleanOperationPolyDataFilter()
    self.booleanfilter.SetOperationToDifference()
    self.booleanfilter.SetTolerance(0.000000000001)
    self.booleanfilter.SetInputConnection(1, self.reader.GetOutputPort())
    self.booleanfilter.SetInputConnection(0, self.triangledBox.GetOutputPort())

    self.clean = vtk.vtkCleanPolyData()
    self.clean.SetInputConnection(self.booleanfilter.GetOutputPort())
    self.clean.SetTolerance(0.00001)

    self.triangles = vtk.vtkTriangleFilter()
    self.triangles.SetInputConnection(self.clean.GetOutputPort())
    self.triangles.Update()

    #rewrite polydata
    self.polydata = self.triangles.GetOutput()
    self.numberOfPoints = self.polydata.GetNumberOfPoints()
    self.objectPoints = []
    for x in range(self.numberOfPoints):
      self.objectPoints.append(self.polydata.GetPoints().GetPoint(x))
    self.updateCoordinates()


    """
    self.triangles = vtk.vtkTriangleFilter()
    self.triangles.SetInputConnection(self.booleanfilter.GetOutputPort())
    self.triangles.Update()


    self.triangles2 = vtk.vtkTriangleFilter()
    self.triangles2.SetInputConnection(self.clean.GetOutputPort())
    self.triangles2.Update()

    self.writer = vtk.vtkSTLWriter()
    self.writer.SetFileName("file.stl")
    self.writer.SetInputConnection(self.triangles2.GetOutputPort())
    self.writer.Write()
    """




  #vizualize the object 
  def visualize(self):

    self.mapper = vtk.vtkPolyDataMapper()
    self.mapper.SetInputData(self.polydata)
    #self.mapper.SetInputConnection(self.booleanfilter.GetOutputPort())
    self.mapper.ScalarVisibilityOff()
    self.actor = vtk.vtkActor()
    self.actor.SetMapper(self.mapper)
    self.actor.GetProperty().EdgeVisibilityOn()





object1 = STL_Object("initial_shape.stl")
object1.updateCoordinates()
object1.buildNegative()
object1.visualize()






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
actor1.GetProperty().EdgeVisibilityOn()

renderer = vtk.vtkRenderer()
renderer.AddActor(object1.actor)
#enderer.AddActor(actor1)
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
      if (self.minZ - 0.0001) < i[2] < (self.minZ + 0.0001):
        pass
      elif (self.maxZ - 0.0001) < i[2] < (self.maxZ + 0.0001):
        pass
"""