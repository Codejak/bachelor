from vtk import *
from math import sqrt


final_shape = "final_shape.stl"
initial_shape = "initial_shape.stl"

aplha = 1
beta = 1
gamma = 1




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
    self.xDist = 0
    self.maxY = 0 
    self.minY = 0
    self.yDist = 0
    self.maxZ = 0
    self.minZ = 0
    self.zDist = 0
    self.avgMaxDist = 0
    self.vol = 0
    self.surfA = 0

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

    self.updateCoordinates()


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
    self.xDist = self.maxX - self.minX
    self.yDist = self.maxY - self.minY
    self.zDist = self.maxZ - self.minZ
    self.avgMaxDist = (self.xDist+self.yDist+self.zDist)/3
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


  #determine the surface area of the object
  def getPropertyInfo(self):
    self.massP = vtk.vtkMassProperties()
    self.massP.SetInputData(polydata)
    self.massP.Update()
    self.vol = self.massP.GetVolume()
    self.surfA = self.massP.GetSurfaceArea()


  #vizualize the object 
  def visualize(self):

    self.mapper = vtk.vtkPolyDataMapper()
    self.mapper.SetInputData(self.polydata)
    #self.mapper.SetInputConnection(self.booleanfilter.GetOutputPort())
    self.mapper.ScalarVisibilityOff()
    self.actor = vtk.vtkActor()
    self.actor.SetMapper(self.mapper)
    self.actor.GetProperty().EdgeVisibilityOn()



#determine a value based on the comparison of 2 object
#the method of comparison is developed on the basis of the Hamming distance
def determineHD(origObject, randObject):
  distListHD = []
  addedDistHD = 0
  avgDistHD = 0
  stdDevHD = 0
  distHD = 0 
  finalValueHD = 0
  for x in randObject.objectPoints:
    pointDistList = []
    for y in origObject.objectPoints:
      pointDistList.append(sqrt(vtkMath.Distance2BetweenPoints(x,y)))
    distListHD.append(min(pointDistList))
  print distListHD

  for a in distListHD:
    addedDistHD += a
  avgDistHD = addedDistHD/len(distListHD)

  for b in distListHD:
    stdDevHD += (b - avgDistHD)**2
  stdDevHD = sqrt(stdDevHD/len(distListHD))

  distHD = max(distListHD)
  finalValueHD = (1/(1+aplha*stdDevHD)) * (1/(1+beta*(avgDistHD/randObject.avgMaxDist))) * (1/(1+gamma*(distHD/randObject.avgMaxDist)))
  
  print  len(distListHD), finalValueHD
  return finalValueHD





generatedObject = STL_Object("initial_shape.stl")
originalObject = STL_Object("final_shape.stl")
originalObject.updateCoordinates()
generatedObject.updateCoordinates()
originalObject.buildNegative()
generatedObject.buildNegative()
originalObject.visualize()
generatedObject.visualize()
#print determineHD(originalObject, generatedObject)




renderer = vtk.vtkRenderer()
renderer.AddActor(originalObject.actor)
renderer.SetBackground(1,1,1)

renderer2 = vtk.vtkRenderer()
renderer2.AddActor(generatedObject.actor)
renderer2.SetBackground(1,1,1)

window = vtk.vtkRenderWindow()
window.AddRenderer(renderer)

window2 = vtk.vtkRenderWindow()
window2.AddRenderer(renderer2)

interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(window)

interactor2 = vtk.vtkRenderWindowInteractor()
interactor2.SetRenderWindow(window2)

axes = vtk.vtkAxesActor()

widget = vtk.vtkOrientationMarkerWidget()
widget.SetOrientationMarker(axes)
widget.SetInteractor(interactor)
widget.SetEnabled(1)
widget.InteractiveOn()

widget2 = vtk.vtkOrientationMarkerWidget()
widget2.SetOrientationMarker(axes)
widget2.SetInteractor(interactor2)
widget2.SetEnabled(1)
widget2.InteractiveOn()



window.Render()
window2.Render()
interactor.Initialize()
interactor.Start() 
interactor2.Initialize()
interactor2.Start() 





"""
print distListHD
"""