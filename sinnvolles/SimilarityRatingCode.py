from vtk import *
from math import sqrt, atan2


final_shape = "final_shape.stl"
initial_shape = "initial_shape.stl"

aplha   = 1        # standard deviation influence on the HD value
beta    = 1        # average HD distance influence on the HD value
gamma   = 1        # overall HD distance influence on the HD value
delta   = 5        # (delta - 1) Planes are generated per axis
epsilon = 0.001    # tolerance value for the planes
zeta    = 1        # influence of the average distance in the planes on the individual plane value
eta     = 1        # influence of the average angle in the planes on the individual plane value
theta   = 1        # influence of the standard deviation of the distances on the ind. plane value
iota    = 1        # influence of the standard deviation of the angles on the ind. plane value




# define the class which creates objects store the data of the STL files
class STL_Object:
  numberOfSTLObjects = 0
  # initiation of the objects
  def __init__(self, fileName):

    # increasing the objectcounter
    STL_Object.numberOfSTLObjects += 1

    # defining the attributes
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

    # reads the Objekt from the stl file
    self.reader = vtk.vtkSTLReader()
    self.reader.SetFileName(fileName)
    self.reader.Update()
    self.polydata = vtk.vtkPolyData()
    self.polydata = self.reader.GetOutput()

    # determine the number of Points
    self.numberOfPoints = self.polydata.GetNumberOfPoints()
    print "\nTrying to store -%s-! Point Number:%s" %(self.fileName, self.numberOfPoints)

    # store the point from the STL file into arrays to work with
    self.objectPoints = []
    for x in range(self.numberOfPoints):
      self.objectPoints.append(self.polydata.GetPoints().GetPoint(x))
    print "\n%s succesfully stored. Length of the storing array: %d" %(self.fileName, len(self.objectPoints))

    self.updateCoordinates()


  # determine the (new) number of points in the object
  def updateNumberOfPoints(self):
    self.numberOfPoints = len(self.objectPoints)
    print "\nNumber of Points in %s updated: %s" %(self.fileName, self.numberOfPoints)


  # store the individual axes-coordianes in arrays
  def updateCoordinates(self):
    self.xCoordinates = []
    self.yCoordinates = []
    self.zCoordinates = []
    for p in self.objectPoints:
      self.xCoordinates.append(p[0])
      self.yCoordinates.append(p[1])
      self.zCoordinates.append(p[2])

    # determine the extrema 
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
  # get rid of the irrelevant points
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

  # reverse the STL file
  def buildNegative(self):
    # create the box to build the negative with
    self.box = vtk.vtkCubeSource()
    completeList = []
    completeList.append(self.minX + 0.0000001)
    completeList.append(self.maxX - 0.0000001)
    completeList.append(self.minY + 0.0000001)
    completeList.append(self.maxY - 0.0000001) 
    completeList.append(self.minZ + 0.0000001)
    completeList.append(self.maxZ - 0.0000001)
    self.box.SetBounds(completeList)

    self.triangledBox = vtk.vtkTriangleFilter()
    self.triangledBox.SetInputConnection(self.box.GetOutputPort())
    self.triangledBox.Update()

    # get the difference between the box and the file
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

    # rewrite polydata
    self.polydata = self.triangles.GetOutput()
    self.numberOfPoints = self.polydata.GetNumberOfPoints()
    self.objectPoints = []
    for x in range(self.numberOfPoints):
      self.objectPoints.append(self.polydata.GetPoints().GetPoint(x))
    self.updateCoordinates()



  # determine the surface area of the object
  def getPropertyInfo(self):
    self.massP = vtk.vtkMassProperties()
    self.massP.SetInputData(polydata)
    self.massP.Update()
    self.vol = self.massP.GetVolume()
    self.surfA = self.massP.GetSurfaceArea()


  # vizualize the object 
  def visualize(self):

    self.mapper = vtk.vtkPolyDataMapper()
    self.mapper.SetInputData(self.polydata)
    #self.mapper.SetInputConnection(self.booleanfilter.GetOutputPort())
    self.mapper.ScalarVisibilityOff()
    self.actor = vtk.vtkActor()
    self.actor.SetMapper(self.mapper)
    self.actor.GetProperty().EdgeVisibilityOn()



# determine a value based on the comparison of 2 object
# the method of comparison is developed on the basis of the Hamming distance
def determineHD(origObject, genObject):
  distListHD = []
  avgDistHD = 0
  stdDevHD = 0
  distHD = 0 
  finalValueHD = 0
  for x in genObject.objectPoints:
    pointDistList = []
    for y in origObject.objectPoints:
      pointDistList.append(sqrt(vtkMath.Distance2BetweenPoints(x,y)))
    distListHD.append(min(pointDistList))
  print distListHD

  for a in distListHD:
    avgDistHD += a
  avgDistHD = avgDistHD/len(distListHD)

  for b in distListHD:
    stdDevHD += (b - avgDistHD)**2
  stdDevHD = sqrt(stdDevHD/len(distListHD))

  distHD = max(distListHD)
  finalValueHD = (1/(1+aplha*stdDevHD)) * (1/(1+beta*(avgDistHD/randObject.avgMaxDist))) * (1/(1+gamma*(distHD/randObject.avgMaxDist)))
  
  print  len(distListHD), finalValueHD
  return finalValueHD



# get Values from the cutting planes in every axes direction
def determinePlaneValues(oObject, gObject):
  axisValue = 0
  xPlaneValues = []
  xValue = 0
  yPlaneValues = []
  yValue = 0
  zPlaneValues = [] 
  zValue = 0
  finalValuePlane = 0

  # create X Planes
  for x in range(delta - 1):
    xPlanePointsO = []
    xPlaneOriginDistO = []
    xPlanePointDistO = []
    xPlaneAvgPointDistO = 0
    xPlaneStdDevDistO = 0
    xPlanePointAnglesO = []
    xPlaneAvgAngleO = 0
    xPlaneStdDevAngleO = 0
    xPlanePointsG = []
    xPlaneOriginDistG = []
    xPlanePointDistG = []
    xPlaneAvgPointDistG = 0
    xPlaneStdDevDistG = 0
    xPlanePointAnglesG = []
    xPlaneAvgAngleG = 0
    xPlaneStdDevAngleG = 0

    # store Planes
    for pointA in oObject.objectPoints:
      if pointA[0] > (((x+1)/delta)*oObject.distX - epsilon) or pointA[0] < (((x+1)/delta)*oObject.distX + epsilon):
        xPlanePointsO.append(pointA)
    for pointB in gObject.objectPoints:
      if pointB[0] > (((x+1)/delta)*oObject.distX - epsilon) or pointB[0] < (((x+1)/delta)*oObject.distX + epsilon):
        xPlanePointsG.append(pointB)

    # find the distance from the Points to the origin
    for pointC in xPlanePointsO:
      xPlaneOriginDistO.append(sqrt(pointC[1]**2+pointC[2]**2))
    for pointD in xPlanePointsG:
      xPlaneOriginDistG.append(sqrt(pointD[1]**2+pointD[2]**2))

    # store the Distances to the farest point from the origin
    for pointE in xPlanePointsO:
      if sqrt(pointE[1]**2+pointE[2]**2) == max(xPlaneOriginDistO):
        for pointF in xPlanePointsO:
          if vtkMath.Distance2BetweenPoints(pointE,pointF) == 0:
            pass
          else:
            xPlanePointDistO.append(sqrt(vtkMath.Distance2BetweenPoints(pointE,pointF)))
    for pointG in xPlanePointsG:
      if sqrt(pointG[1]**2+pointG[2]**2) == max(xPlaneOriginDistG):
        for pointH in xPlanePointsG:
          if vtkMath.Distance2BetweenPoints(pointG,pointH) == 0:
            pass
          else:
            xPlanePointDistG.append(sqrt(vtkMath.Distance2BetweenPoints(pointG,pointH)))

    # get average Point distances
    for dist1 in xPlanePointsDistO:
      xPlaneAvgPointDistO += dist1
    xPlaneAvgPointDistO = xPlaneAvgPointDistO/len(xPlanePointsDistO)
    for dist2 in xPlanePointsDistG:
      xPlaneAvgPointDistG += dist2
    xPlaneAvgPointDistG = xPlaneAvgPointDistG/len(xPlanePointsDistG)

    # get the standard deviation of these distances
    for c in xPlanePointsDistO:
      xPlaneStdDevDistO += (c - xPlaneAvgPointDistO)**2
    xPlaneStdDevDistO = sqrt(xPlaneStdDevDistO/len(xPlanePointsDistO))
    for d in xPlanePointsDistG:
      xPlaneStdDevDistG += (d - xPlaneAvgPointDistG)**2
    xPlaneStdDevDistG = sqrt(xPlaneStdDevDistG/len(xPlanePointsDistG))

    # get angles between points
    for pointI in xPlanePointsO:
      if sqrt(pointI[1]**2+pointI[2]**2) == max(xPlaneOriginDistO):
        for pointJ in xPlanePointsO:
          if vtkMath.Distance2BetweenPoints(pointI,pointJ) == 0:
            pass
          else:
            xPlanePointAnglesO.append(atan2(pointJ[2]-pointI[2],pointJ[1]-pointI[1]))
    for pointK in xPlanePointsG:
      if sqrt(pointK[1]**2+pointK[2]**2) == max(xPlaneOriginDistG):
        for pointL in xPlanePointsG:
          if vtkMath.Distance2BetweenPoints(pointK,pointL) == 0:
            pass
          else:
            xPlanePointAnglesG.append(atan2(pointL[2]-pointK[2],pointL[1]-pointK[1]))

    # get the average angle
    for dist3 in xPlanePointAnglesO:
      xPlaneAvgAngleO += dist3
    xPlaneAvgAngleO = xPlaneAvgAngleO/len(xPlanePointAnglesO)
    for dist4 in xPlanePointAnglesG:
      xPlaneAvgAngleG += dist4
    xPlaneAvgAngleG = xPlaneAvgAngleG/len(xPlanePointAnglesG)

    # get the standard deviation of the angles
    for e in xPlanePointAnglesO:
      xPlaneStdDevAngleO += (e - xPlaneAvgPointDistO)**2
    xPlaneStdDevAngleO = sqrt(xPlaneStdDevAngleO/len(xPlanePointAnglesO))
    for f in xPlanePointAnglesG:
      xPlaneStdDevAngleG += (f - xPlaneAvgPointDistG)**2
    xPlaneStdDevAngleG = sqrt(xPlaneStdDevAngleG/len(xPlanePointAnglesG))

    # get axis value and store it
    axisValueX = (1/(1+(zeta*(abs((xPlaneAvgPointDistO - xPlaneAvgPointDistG)/xPlaneAvgPointDistO)))))*(1/(1+(eta*(abs((xPlaneAvgAngleO - xPlaneAvgAngleG)/xPlaneAvgAngleO)))))*(1/(1+(theta*(abs(xPlaneStdDevDistO - xPlaneStdDevDistG)/xPlaneStdDevDistO))))*(1/(1+(iota*(abs(xPlaneStdDevAngleO - xPlaneStdDevAngleG)/xPlaneStdDevAngleO))))
    xPlaneValues.append(axisValueX)

  for listX in xPlaneValues:
    xValue += listX
  xValue = xValue/len(xPlaneValues)




  # create Y Planes
  for y in range(delta - 1):
    yPlanePointsO = []
    yPlaneOriginDistO = []
    yPlanePointDistO = []
    yPlaneAvgPointDistO = 0
    yPlaneStdDevDistO = 0
    yPlanePointAnglesO = []
    yPlaneAvgAngleO = 0
    yPlaneStdDevAngleO = 0
    yPlanePointsG = []
    yPlaneOriginDistG = []
    yPlanePointDistG = []
    yPlaneAvgPointDistG = 0
    yPlaneStdDevDistG = 0
    yPlanePointAnglesG = []
    yPlaneAvgAngleG = 0
    yPlaneStdDevAngleG = 0

    # store Planes
    for pointM in oObject.objectPoints:
      if pointM[0] > (((y+1)/delta)*oObject.distY - epsilon) or pointM[0] < (((y+1)/delta)*oObject.distY + epsilon):
        yPlanePointsO.append(pointM)
    for pointN in gObject.objectPoints:
      if pointN[0] > (((y+1)/delta)*oObject.distY - epsilon) or pointN[0] < (((y+1)/delta)*oObject.distY + epsilon):
        yPlanePointsG.append(pointN)

    # find the distance from the Points to the origin
    for pointO in yPlanePointsO:
      yPlaneOriginDistO.append(sqrt(pointO[0]**2+pointO[2]**2))
    for pointP in yPlanePointsG:
      yPlaneOriginDistG.append(sqrt(pointP[0]**2+pointP[2]**2))

    # store the Distances to the farest point from the origin
    for pointQ in yPlanePointsO:
      if sqrt(pointQ[0]**2+pointQ[2]**2) == max(yPlaneOriginDistO):
        for pointR in yPlanePointsO:
          if vtkMath.Distance2BetweenPoints(pointQ,pointR) == 0:
            pass
          else:
            yPlanePointDistO.append(sqrt(vtkMath.Distance2BetweenPoints(pointQ,pointR)))
    for pointS in yPlanePointsG:
      if sqrt(pointS[0]**2+pointS[2]**2) == max(yPlaneOriginDistG):
        for pointT in yPlanePointsG:
          if vtkMath.Distance2BetweenPoints(pointS,pointT) == 0:
            pass
          else:
            yPlanePointDistG.append(sqrt(vtkMath.Distance2BetweenPoints(pointS,pointT)))

    # get average Point distances
    for dist5 in yPlanePointsDistO:
      yPlaneAvgPointDistO += dist5
    yPlaneAvgPointDistO = yPlaneAvgPointDistO/len(yPlanePointsDistO)
    for dist6 in yPlanePointsDistG:
      yPlaneAvgPointDistG += dist6
    yPlaneAvgPointDistG = yPlaneAvgPointDistG/len(yPlanePointsDistG)

    # get the standard deviation of these distances
    for g in yPlanePointsDistO:
      yPlaneStdDevDistO += (g - yPlaneAvgPointDistO)**2
    yPlaneStdDevDistO = sqrt(yPlaneStdDevDistO/len(yPlanePointsDistO))
    for h in yPlanePointsDistG:
      yPlaneStdDevDistG += (h - yPlaneAvgPointDistG)**2
    yPlaneStdDevDistG = sqrt(yPlaneStdDevDistG/len(yPlanePointsDistG))

    # get angles between points
    for pointU in yPlanePointsO:
      if sqrt(pointU[0]**2+pointU[2]**2) == max(yPlaneOriginDistO):
        for pointV in yPlanePointsO:
          if vtkMath.Distance2BetweenPoints(pointU,pointV) == 0:
            pass
          else:
            yPlanePointAnglesO.append(atan2(pointV[2]-pointU[2],pointV[0]-pointU[0]))
    for pointW in yPlanePointsG:
      if sqrt(pointW[0]**2+pointW[2]**2) == max(yPlaneOriginDistG):
        for pointX in yPlanePointsG:
          if vtkMath.Distance2BetweenPoints(pointW,pointX) == 0:
            pass
          else:
            yPlanePointAnglesG.append(atan2(pointX[2]-pointW[2],pointX[0]-pointX[0]))

    # get the average angle
    for dist7 in yPlanePointAnglesO:
      yPlaneAvgAngleO += dist7
    yPlaneAvgAngleO = yPlaneAvgAngleO/len(yPlanePointAnglesO)
    for dist8 in yPlanePointAnglesG:
      yPlaneAvgAngleG += dist8
    yPlaneAvgAngleG = yPlaneAvgAngleG/len(yPlanePointAnglesG)

    # get the standard deviation of the angles
    for i in yPlanePointAnglesO:
      yPlaneStdDevAngleO += (i - yPlaneAvgPointDistO)**2
    yPlaneStdDevAngleO = sqrt(yPlaneStdDevAngleO/len(yPlanePointAnglesO))
    for j in yPlanePointAnglesG:
      yPlaneStdDevAngleG += (j - yPlaneAvgPointDistG)**2
    yPlaneStdDevAngleG = sqrt(yPlaneStdDevAngleG/len(yPlanePointAnglesG))

    # get axis value and store it
    axisValueY = (1/(1+(zeta*(abs((yPlaneAvgPointDistO - yPlaneAvgPointDistG)/yPlaneAvgPointDistO)))))*(1/(1+(eta*(abs((yPlaneAvgAngleO - yPlaneAvgAngleG)/yPlaneAvgAngleO)))))*(1/(1+(theta*(abs(yPlaneStdDevDistO - yPlaneStdDevDistG)/yPlaneStdDevDistO))))*(1/(1+(iota*(abs(yPlaneStdDevAngleO - yPlaneStdDevAngleG)/yPlaneStdDevAngleO))))
    yPlaneValues.append(axisValueY)

  for listY in yPlaneValues:
    yValue += listY
  yValue = yValue/len(yPlaneValues)

  finalValuePlane = (xValue + yValue + zValue)/3
  print finalValuePlane
  return finalValuePlane




  # create Z Planes
  for z in range(delta - 1):
    zPlanePointsO = []
    zPlaneOriginDistO = []
    zPlanePointDistO = []
    zPlaneAvgPointDistO = 0
    zPlaneStdDevDistO = 0
    zPlanePointAnglesO = []
    zPlaneAvgAngleO = 0
    zPlaneStdDevAngleO = 0
    zPlanePointsG = []
    zPlaneOriginDistG = []
    zPlanePointDistG = []
    zPlaneAvgPointDistG = 0
    zPlaneStdDevDistG = 0
    zPlanePointAnglesG = []
    zPlaneAvgAngleG = 0
    zPlaneStdDevAngleG = 0

    # store Planes
    for pointY in oObject.objectPoints:
      if pointY[0] > (((z+1)/delta)*oObject.distZ - epsilon) or pointY[0] < (((z+1)/delta)*oObject.distZ + epsilon):
        zPlanePointsO.append(pointY)
    for pointZ in gObject.objectPoints:
      if pointZ[0] > (((z+1)/delta)*oObject.distZ - epsilon) or pointZ[0] < (((z+1)/delta)*oObject.distZ + epsilon):
        zPlanePointsG.append(pointZ)

    # find the distance from the Points to the origin
    for pointAA in zPlanePointsO:
      zPlaneOriginDistO.append(sqrt(pointAA[1]**2+pointAA[0]**2))
    for pointAB in zPlanePointsG:
      zPlaneOriginDistG.append(sqrt(pointAB[1]**2+pointAB[0]**2))

    # store the Distances to the farest point from the origin
    for pointAC in zPlanePointsO:
      if sqrt(pointAC[1]**2+pointAC[0]**2) == max(zPlaneOriginDistO):
        for pointAD in zPlanePointsO:
          if vtkMath.Distance2BetweenPoints(pointAC,pointAD) == 0:
            pass
          else:
            zPlanePointDistO.append(sqrt(vtkMath.Distance2BetweenPoints(pointAC,pointAD)))
    for pointAE in zPlanePointsG:
      if sqrt(pointAE[1]**2+pointAE[0]**2) == max(zPlaneOriginDistG):
        for pointAF in zPlanePointsG:
          if vtkMath.Distance2BetweenPoints(pointAE,pointAF) == 0:
            pass
          else:
            zPlanePointDistG.append(sqrt(vtkMath.Distance2BetweenPoints(pointAE,pointAF)))

    # get average Point distances
    for dist9 in zPlanePointsDistO:
      zPlaneAvgPointDistO += dist9
    zPlaneAvgPointDistO = zPlaneAvgPointDistO/len(zPlanePointsDistO)
    for dist10 in zPlanePointsDistG:
      zPlaneAvgPointDistG += dist10
    zPlaneAvgPointDistG = zPlaneAvgPointDistG/len(zPlanePointsDistG)

    # get the standard deviation of these distances
    for k in zPlanePointsDistO:
      zPlaneStdDevDistO += (k - zPlaneAvgPointDistO)**2
    zPlaneStdDevDistO = sqrt(zPlaneStdDevDistO/len(zPlanePointsDistO))
    for l in zPlanePointsDistG:
      zPlaneStdDevDistG += (l - zPlaneAvgPointDistG)**2
    zPlaneStdDevDistG = sqrt(zPlaneStdDevDistG/len(zPlanePointsDistG))

    # get angles between points
    for pointAG in zPlanePointsO:
      if sqrt(pointAG[1]**2+pointAG[0]**2) == max(zPlaneOriginDistO):
        for pointAH in zPlanePointsO:
          if vtkMath.Distance2BetweenPoints(pointAG,pointAH) == 0:
            pass
          else:
            zPlanePointAnglesO.append(atan2(pointAH[1]-pointAG[1],pointAH[0]-pointAG[0]))
    for pointAI in zPlanePointsG:
      if sqrt(pointAI[1]**2+pointAI[0]**2) == max(zPlaneOriginDistG):
        for pointAJ in zPlanePointsG:
          if vtkMath.Distance2BetweenPoints(pointAI,pointAJ) == 0:
            pass
          else:
            zPlanePointAnglesG.append(atan2(pointAJ[1]-pointAI[1],pointAJ[0]-pointAI[0]))

    # get the average angle
    for dist11 in zPlanePointAnglesO:
      zPlaneAvgAngleO += dist11
    zPlaneAvgAngleO = zPlaneAvgAngleO/len(zPlanePointAnglesO)
    for dist12 in zPlanePointAnglesG:
      zPlaneAvgAngleG += dist12
    zPlaneAvgAngleG = zPlaneAvgAngleG/len(zPlanePointAnglesG)

    # get the standard deviation of the angles
    for m in zPlanePointAnglesO:
      zPlaneStdDevAngleO += (m - zPlaneAvgPointDistO)**2
    zPlaneStdDevAngleO = sqrt(zPlaneStdDevAngleO/len(zPlanePointAnglesO))
    for n in zPlanePointAnglesG:
      zPlaneStdDevAngleG += (n - zPlaneAvgPointDistG)**2
    zPlaneStdDevAngleG = sqrt(zPlaneStdDevAngleG/len(zPlanePointAnglesG))

    # get axis value and store it
    axisValueZ = (1/(1+(zeta*(abs((zPlaneAvgPointDistO - zPlaneAvgPointDistG)/zPlaneAvgPointDistO)))))*(1/(1+(eta*(abs((zPlaneAvgAngleO - zPlaneAvgAngleG)/zPlaneAvgAngleO)))))*(1/(1+(theta*(abs(zPlaneStdDevDistO - zPlaneStdDevDistG)/zPlaneStdDevDistO))))*(1/(1+(iota*(abs(zPlaneStdDevAngleO - zPlaneStdDevAngleG)/zPlaneStdDevAngleO))))
    zPlaneValues.append(axisValueZ)

  for listZ in zPlaneValues:
    zValue += listZ
  zValue = zValue/len(zPlaneValues)










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
-  print Befehle entfernen
-  zentrierung?
-  Ausgangspunkt für Ebenen prüfen
-  if befehle für Listenlänge
"""