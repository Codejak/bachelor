from vtk import *
from math import sqrt, atan2


final_shape = "final_shape.stl"
initial_shape = "initial_shape.stl"

aplha   = 1         # standard deviation influence on the HD value
beta    = 1         # average HD distance influence on the HD value
gamma   = 1         # overall HD distance influence on the HD value
delta   = 3         # (delta - 1) Planes are generated per axis
epsilon = 0.001     # tolerance value for the planes
zeta    = 1         # influence of the average distance in the planes on the individual plane value
eta     = 1         # influence of the average angle in the planes on the individual plane value
theta   = 1         # influence of the standard deviation of the distances on the ind. plane value
iota    = 1         # influence of the standard deviation of the angles on the ind. plane value
kappa   = 1         # influence of the difference of the volumes on the boundary value
my      = 1         # influence of the difference of the surface areas on the boundary value
sigma   = 1         # influence of on the final Value
rho     = 1         # influence of on the final Value
omega   = 1         # influence of on the final Value
tolerancevalue = 0.0001
tolerancevalue2 = 0.00000001

# define the class which creates objects store the data of the STL files
class STL_Object:
  # initiation of the objects
  def __init__(self, fileName):

    # defining the attributes
    self.booleanfilter = vtk.vtkBooleanOperationPolyDataFilter()
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
    self.valueHD = 0
    self.valuePlane = 0 
    self.valueBoundary = 0
    self.similarity = 0

    # reads the Objekt from the stl file
    self.reader = vtk.vtkSTLReader()
    self.reader.SetFileName(fileName)
    self.reader.Update()
    self.polydata = vtk.vtkPolyData()
    self.polydata = self.reader.GetOutput()

    # determine the number of Points
    self.numberOfPoints = self.polydata.GetNumberOfPoints()
    #print "\nTrying to store -%s-! Point Number:%s" %(self.fileName, self.numberOfPoints)

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
    #print "\nCoordinates of %s succesfully updated. Length of the arrays: %s, %s, %s \nThese are the min/max coordinates: X[%s,%s], Y[%s,%s], Z[%s,%s] " %(self.fileName, len(self.xCoordinates), len(self.yCoordinates), len(self.zCoordinates), self.minX,self.maxX,self.minY,self.maxY,self.minZ,self.maxZ)
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
    completeList.append(self.minX + tolerancevalue)
    completeList.append(self.maxX - tolerancevalue)
    completeList.append(self.minY + tolerancevalue)
    completeList.append(self.maxY - tolerancevalue) 
    completeList.append(self.minZ + tolerancevalue)
    completeList.append(self.maxZ - tolerancevalue)
    self.box.SetBounds(completeList)

    self.triangledBox = vtk.vtkTriangleFilter()
    self.triangledBox.SetInputConnection(self.box.GetOutputPort())
    self.triangledBox.Update()

    # get the difference between the box and the file
    self.booleanfilter = vtk.vtkBooleanOperationPolyDataFilter()
    self.booleanfilter.SetOperationToDifference()
    self.booleanfilter.SetTolerance(tolerancevalue2)
    self.booleanfilter.SetInputConnection(1, self.reader.GetOutputPort())
    self.booleanfilter.SetInputConnection(0, self.triangledBox.GetOutputPort())

    self.triangles = vtk.vtkTriangleFilter()
    self.triangles.SetInputConnection(self.booleanfilter.GetOutputPort())
    self.triangles.Update()

    self.clean = vtk.vtkCleanPolyData()
    self.clean.SetInputConnection(self.booleanfilter.GetOutputPort())
    self.clean.SetTolerance(0.00001)
    self.clean.Update()
    
    
    # determine the volume and surface area of the object
    self.massP = vtk.vtkMassProperties()
    self.massP.SetInputConnection(self.booleanfilter.GetOutputPort())
    self.massP.Update()
    self.vol = self.massP.GetVolume()
    self.surfA = self.massP.GetSurfaceArea()
    
    # rewrite polydata
    self.polydata = self.clean.GetOutput()
    self.numberOfPoints = self.polydata.GetNumberOfPoints()
    self.objectPoints = []
    for x in range(self.numberOfPoints):
      self.objectPoints.append(self.polydata.GetPoints().GetPoint(x))
    self.updateCoordinates()


  # vizualize the object 
  def visualize(self):
    self.mapper = vtk.vtkPolyDataMapper()
    #self.mapper.SetInputData(self.polydata)
    self.mapper.SetInputConnection(self.booleanfilter.GetOutputPort())
    self.mapper.ScalarVisibilityOff()
    self.actor = vtk.vtkActor()
    self.actor.SetMapper(self.mapper)
    self.actor.GetProperty().EdgeVisibilityOn()


# determine a value based on the comparison of 2 object
# the method of comparison is developed on the basis of the Hamming distance
def getHD():
  distListHD = []
  avgDistHD = 0
  stdDevHD = 0
  distHD = 0 
  finalValueHD = 0
  for x in generatedObject.objectPoints:
    pointDistList = []
    for y in originalObject.objectPoints:
      pointDistList.append(sqrt(vtkMath.Distance2BetweenPoints(x,y)))
    distListHD.append(min(pointDistList))

  for a in distListHD:
    avgDistHD += a
  avgDistHD = avgDistHD/len(distListHD)

  for b in distListHD:
    stdDevHD += (b - avgDistHD)**2
  stdDevHD = sqrt(stdDevHD/len(distListHD))

  distHD = max(distListHD)
  finalValueHD = (1/(1+aplha*stdDevHD)) * (1/(1+beta*(avgDistHD/generatedObject.avgMaxDist))) * (1/(1+gamma*(distHD/generatedObject.avgMaxDist)))
  
  print  "finalValueHD is: %s" %(finalValueHD)
  generatedObject.valueHD = finalValueHD



# get Values from the cutting planes in every axes direction
def getPlaneValues():
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
    for pointA in originalObject.objectPoints:
      if pointA[0] > (((x+1)/delta)*originalObject.xDist - epsilon) or pointA[0] < (((x+1)/delta)*originalObject.xDist + epsilon):
        xPlanePointsO.append(pointA)
    for pointB in generatedObject.objectPoints:
      if pointB[0] > (((x+1)/delta)*originalObject.xDist - epsilon) or pointB[0] < (((x+1)/delta)*originalObject.xDist + epsilon):
        xPlanePointsG.append(pointB)

    # find the distance from the Points to the origin
    if len(xPlanePointsO) > 1 and len(xPlanePointsG) > 1:
      for pointC in xPlanePointsO:
        xPlaneOriginDistO.append(sqrt(pointC[1]**2+pointC[2]**2))
      for pointD in xPlanePointsG:
        xPlaneOriginDistG.append(sqrt(pointD[1]**2+pointD[2]**2))

    # store the Distances to the farest point from the origin
    if len(xPlaneOriginDistO) > 1 and len(xPlaneOriginDistG) > 1:
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

    if len(xPlanePointDistO) > 0 and len(xPlanePointDistG) > 0:
      # get average Point distances
      for dist1 in xPlanePointDistO:
        xPlaneAvgPointDistO += dist1
      xPlaneAvgPointDistO = xPlaneAvgPointDistO/len(xPlanePointDistO)
      for dist2 in xPlanePointDistG:
        xPlaneAvgPointDistG += dist2
      xPlaneAvgPointDistG = xPlaneAvgPointDistG/len(xPlanePointDistG)

      # get the standard deviation of these distances
      for c in xPlanePointDistO:
        xPlaneStdDevDistO += (c - xPlaneAvgPointDistO)**2
      xPlaneStdDevDistO = sqrt(xPlaneStdDevDistO/len(xPlanePointDistO))
      for d in xPlanePointDistG:
        xPlaneStdDevDistG += (d - xPlaneAvgPointDistG)**2
      xPlaneStdDevDistG = sqrt(xPlaneStdDevDistG/len(xPlanePointDistG))

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

    if len(xPlanePointAnglesO) > 0 and len(xPlanePointAnglesG) > 0:
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

    if xPlaneAvgPointDistO != 0 and xPlaneAvgPointDistG != 0:
      if xPlaneAvgAngleO != 0 and xPlaneAvgAngleG != 0:
        if xPlaneStdDevDistO != 0 and xPlaneStdDevDistG != 0:
          if xPlaneStdDevAngleO != 0 and xPlaneStdDevAngleG != 0:
            # get axis value and store it
            axisValueX = (1/(1+(zeta*(abs((xPlaneAvgPointDistO - xPlaneAvgPointDistG)/xPlaneAvgPointDistO)))))*(1/(1+(eta*(abs((xPlaneAvgAngleO - xPlaneAvgAngleG)/xPlaneAvgAngleO)))))*(1/(1+(theta*(abs(xPlaneStdDevDistO - xPlaneStdDevDistG)/xPlaneStdDevDistO))))*(1/(1+(iota*(abs(xPlaneStdDevAngleO - xPlaneStdDevAngleG)/xPlaneStdDevAngleO))))
            xPlaneValues.append(axisValueX)
            print "Axis Value for x Plane nr. %s is: %s" %(x,axisValueX)
          else:
            print "no angle std deviation in this x-Pane"
        else:
          print "no distance std deviation in this x-Plane"
      else:
        print "not enough angles in this x-Plane"
    else:
      print "not enough points in this x-Plane"


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
    for pointM in originalObject.objectPoints:
      if pointM[0] > (((y+1)/delta)*originalObject.yDist - epsilon) or pointM[0] < (((y+1)/delta)*originalObject.yDist + epsilon):
        yPlanePointsO.append(pointM)
    for pointN in generatedObject.objectPoints:
      if pointN[0] > (((y+1)/delta)*originalObject.yDist - epsilon) or pointN[0] < (((y+1)/delta)*originalObject.yDist + epsilon):
        yPlanePointsG.append(pointN)

    # find the distance from the Points to the origin
    if len(yPlanePointsO) > 1 and len(yPlanePointsG) > 1:
      for pointO in yPlanePointsO:
        yPlaneOriginDistO.append(sqrt(pointO[0]**2+pointO[2]**2))
      for pointP in yPlanePointsG:
        yPlaneOriginDistG.append(sqrt(pointP[0]**2+pointP[2]**2))

    # store the Distances to the farest point from the origin
    if len(yPlaneOriginDistO) > 1 and len(yPlaneOriginDistG) > 1:
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

    if len(yPlanePointDistO) > 0 and len(yPlanePointDistG) > 0:
      # get average Point distances
      for dist5 in yPlanePointDistO:
        yPlaneAvgPointDistO += dist5
      yPlaneAvgPointDistO = yPlaneAvgPointDistO/len(yPlanePointDistO)
      for dist6 in yPlanePointDistG:
        yPlaneAvgPointDistG += dist6
      yPlaneAvgPointDistG = yPlaneAvgPointDistG/len(yPlanePointDistG)

      # get the standard deviation of these distances
      for g in yPlanePointDistO:
        yPlaneStdDevDistO += (g - yPlaneAvgPointDistO)**2
      yPlaneStdDevDistO = sqrt(yPlaneStdDevDistO/len(yPlanePointDistO))
      for h in yPlanePointDistG:
        yPlaneStdDevDistG += (h - yPlaneAvgPointDistG)**2
      yPlaneStdDevDistG = sqrt(yPlaneStdDevDistG/len(yPlanePointDistG))

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
              yPlanePointAnglesG.append(atan2(pointX[2]-pointW[2],pointX[0]-pointW[0]))

    if len(yPlanePointAnglesO) > 0 and len(yPlanePointAnglesG) > 0:
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

    if yPlaneAvgPointDistO != 0 and yPlaneAvgPointDistG != 0:
      if yPlaneAvgAngleO != 0 and yPlaneAvgAngleG != 0:
        if yPlaneStdDevDistO != 0 and yPlaneStdDevDistG != 0:
          if yPlaneStdDevAngleO != 0 and yPlaneStdDevAngleG != 0:
            # get axis value and store it
            axisValueY = (1/(1+(zeta*(abs((yPlaneAvgPointDistO - yPlaneAvgPointDistG)/yPlaneAvgPointDistO)))))*(1/(1+(eta*(abs((yPlaneAvgAngleO - yPlaneAvgAngleG)/yPlaneAvgAngleO)))))*(1/(1+(theta*(abs(yPlaneStdDevDistO - yPlaneStdDevDistG)/yPlaneStdDevDistO))))*(1/(1+(iota*(abs(yPlaneStdDevAngleO - yPlaneStdDevAngleG)/yPlaneStdDevAngleO))))
            yPlaneValues.append(axisValueY)
            print "Axis Value for y Plane nr. %s is: %s" %(y,axisValueY)
          else:
            print "no angle std deviation in this y-Pane"
        else:
          print "no distance std deviation in this y-Plane"
      else:
        print "not enough angles in this y-Plane"
    else:
      print "not enough points in this y-Plane"


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
    for pointY in originalObject.objectPoints:
      if pointY[0] > (((z+1)/delta)*originalObject.zDist - epsilon) or pointY[0] < (((z+1)/delta)*originalObject.zDist + epsilon):
        zPlanePointsO.append(pointY)
    for pointZ in generatedObject.objectPoints:
      if pointZ[0] > (((z+1)/delta)*originalObject.zDist - epsilon) or pointZ[0] < (((z+1)/delta)*originalObject.zDist + epsilon):
        zPlanePointsG.append(pointZ)

    # find the distance from the Points to the origin
    if len(zPlanePointsO) > 1 and len(zPlanePointsG) > 1:
      for pointAA in zPlanePointsO:
        zPlaneOriginDistO.append(sqrt(pointAA[1]**2+pointAA[0]**2))
      for pointAB in zPlanePointsG:
        zPlaneOriginDistG.append(sqrt(pointAB[1]**2+pointAB[0]**2))

    # store the Distances to the farest point from the origin
    if len(zPlaneOriginDistO) > 1 and len(zPlaneOriginDistG) > 1:
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

    if len(zPlanePointDistO) > 0 and len(zPlanePointDistG) > 0:
      # get average Point distances
      for dist9 in zPlanePointDistO:
        zPlaneAvgPointDistO += dist9
      zPlaneAvgPointDistO = zPlaneAvgPointDistO/len(zPlanePointDistO)
      for dist10 in zPlanePointDistG:
        zPlaneAvgPointDistG += dist10
      zPlaneAvgPointDistG = zPlaneAvgPointDistG/len(zPlanePointDistG)

      # get the standard deviation of these distances
      for k in zPlanePointDistO:
        zPlaneStdDevDistO += (k - zPlaneAvgPointDistO)**2
      zPlaneStdDevDistO = sqrt(zPlaneStdDevDistO/len(zPlanePointDistO))
      for l in zPlanePointDistG:
        zPlaneStdDevDistG += (l - zPlaneAvgPointDistG)**2
      zPlaneStdDevDistG = sqrt(zPlaneStdDevDistG/len(zPlanePointDistG))

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

    if len(zPlanePointAnglesO) > 0 and len(zPlanePointAnglesG) > 0:
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

    if zPlaneAvgPointDistO != 0 and zPlaneAvgPointDistG != 0:
      if zPlaneAvgAngleO != 0 and zPlaneAvgAngleG != 0:
        if zPlaneStdDevDistO != 0 and zPlaneStdDevDistG != 0:
          if zPlaneStdDevAngleO != 0 and zPlaneStdDevAngleG != 0:
            # get axis value and store it
            axisValueZ = (1/(1+(zeta*(abs((zPlaneAvgPointDistO - zPlaneAvgPointDistG)/zPlaneAvgPointDistO)))))*(1/(1+(eta*(abs((zPlaneAvgAngleO - zPlaneAvgAngleG)/zPlaneAvgAngleO)))))*(1/(1+(theta*(abs(zPlaneStdDevDistO - zPlaneStdDevDistG)/zPlaneStdDevDistO))))*(1/(1+(iota*(abs(zPlaneStdDevAngleO - zPlaneStdDevAngleG)/zPlaneStdDevAngleO))))
            zPlaneValues.append(axisValueZ)
            print "Axis Value for z Plane nr. %s is: %s" %(z,axisValueZ)
          else:
            print "no angle std deviation in this z-Pane"
        else:
          print "no distance std deviation in this z-Plane"
      else:
        print "not enough angles in this z-Plane"
    else:
      print "not enough points in this z-Plane"

  if len(xPlaneValues) > 0:
    for listX in xPlaneValues:
      xValue += listX
    xValue = xValue/len(xPlaneValues)

  if len(yPlaneValues) > 0:
    for listY in yPlaneValues:
      yValue += listY
    yValue = yValue/len(yPlaneValues)

  if len(zPlaneValues) > 0:
    for listZ in zPlaneValues:
      zValue += listZ
    zValue = zValue/len(zPlaneValues)

  if xValue > 0 and yValue > 0 and zValue > 0:
    finalValuePlane = (xValue + yValue + zValue)/3
  else:
    print "a plane value is lost"
    if xValue > 0:
      if yValue > 0:
        finalValuePlane = (xValue + yValue)/2
      else:
        if zValue > 0:
          finalValuePlane = (xValue + zValue)/2
        else:
          finalValuePlane = xValue
    else:
      if yValue > 0:
        finalValuePlane = (zValue + yValue)/2
      else:
        if zValue > 0:
          finalValuePlane = zValue
        else:
          print "final plane value is completely lost"


  generatedObject.valuePlane = finalValuePlane
  print "final plane value: %s" %(finalValuePlane)

#get a value by comparing surface area as well as volume
def getBoundaryValue():
  surfaceValue = 0
  volumeValue = 0
  combinedValue = 0
  #originalObject.getPropertyInfo()
  #generatedObject.getPropertyInfo()
  print "orignal volume: %s" %(originalObject.vol)
  print "generated volume: %s" %(generatedObject.vol)
  if originalObject.vol > 0 and generatedObject.vol > 0:
    if originalObject.surfA > 0 and generatedObject.surfA > 0:
      volumeValue = 1/(1+(kappa*abs((originalObject.vol - generatedObject.vol)/originalObject.vol)))
      print "volume value is: %s" %(volumeValue)
      surfaceValue = 1/(1+(my*abs((originalObject.surfA - generatedObject.surfA)/originalObject.surfA)))
      print "surface value is: %s" %(surfaceValue)
    else:
      print "surface Areas are empty"
  else:
    print "volumes are empty"
  combinedValue = surfaceValue * volumeValue
  generatedObject.valueBoundary = combinedValue
  print "Boundary value is: %s" %(combinedValue)


def getSimilarityValue():
  simValue = 0
  getBoundaryValue()
  getHD()
  getPlaneValues()
  simValue = (((sigma * generatedObject.valueBoundary) + (rho * generatedObject.valuePlane) + (omega * generatedObject.valueHD))/(sigma + rho + omega))
  print "similarity is: %s" %(simValue)
  generatedObject.similarity = simValue


def writeBack():
  file1 = open("SimilarityValue.txt","w")
  file1.write("%s"%generatedObject.similarity)
  file1.close()



originalObject = STL_Object("initial_shape.stl")
generatedObject = STL_Object("initial_shape.stl")
originalObject.updateCoordinates()
generatedObject.updateCoordinates()
print "updated"
originalObject.buildNegative()
print "original reversed"
generatedObject.buildNegative()
print "negatives built"
getSimilarityValue()
writeBack()
originalObject.visualize()
generatedObject.visualize()





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
"""