

from vtk import *#

final_shape = "final_shape.stl"
initial_shape = "initial_shape.stl"



#reading the shit
reader1 = vtk.vtkSTLReader()
reader1.SetFileName(final_shape)
reader1.Update()

reader2 = vtk.vtkSTLReader()
reader2.SetFileName(initial_shape)
reader2.Update()



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
#clean1.ConvertStripsToPolysOn()
#clean1.ConvertPolysToLinesOn()
#clean1.ConvertLinesToPointsOn()
clean1.Update()

clean2 = vtk.vtkCleanPolyData()
clean2.SetInputConnection(smooth2.GetOutputPort())
#clean2.ConvertStripsToPolysOn()
#clean2.ConvertPolysToLinesOn()
#clean2.ConvertLinesToPointsOn()
clean2.Update()



#triangle that shit
triangle1 = vtk.vtkTriangleFilter()
triangle1.SetInputConnection(clean1.GetOutputPort())
#triangle1.PassVertsOff()
#triangle1.PassLinesOff()
triangle1.Update()

triangle2 = vtk.vtkTriangleFilter()
triangle2.SetInputConnection(clean2.GetOutputPort())
#triangle2.PassVertsOff()
#triangle2.PassLinesOff()
triangle2.Update()




#normal that shit
normal1 = vtk.vtkPolyDataNormals()
normal1.SetInputConnection(triangle1.GetOutputPort())
#normal1.ComputePointNormalsOn()
#normal1.ComputeCellNormalsOff()
#normal1.SplittingOff()
#normal1.ConsistencyOn()
#normal1.AutoOrientNormalsOff()
normal1.Update()

normal2 = vtk.vtkPolyDataNormals()
normal2.SetInputConnection(triangle2.GetOutputPort())
#normal2.ComputePointNormalsOn()
#normal2.ComputeCellNormalsOff()
#normal2.SplittingOff()
#normal2.ConsistencyOn()
#normal2.AutoOrientNormalsOff()
normal2.Update()



#boolean Operation
booleanfilter = vtk.vtkBooleanOperationPolyDataFilter()
booleanfilter.SetOperationToDifference()
booleanfilter.SetInputConnection(0, reader1.GetOutputPort())
booleanfilter.SetInputConnection(1, reader2.GetOutputPort())

"""
boolean = vtk.vtkImplicitBoolean()
boolean.SetOperationTypeToDifference()
boolean.AddFunction(box)
boolean.AddFunction(sphere)


sample = vtk.vtkSampleFunction()
sample.SetImplicitFunction(boolean)
sample.SetModelBounds(-1,2,-1,1,-1,1)
sample.SetSampleDimensions(40,40,40)
sample.ComputeNormalsOff()


surface = vtk.vtkContourFilter()
surface.SetInputConnection(sample.GetOutputPort())
surface.SetValue(0, 0.0)
"""

mappera = vtk.vtkPolyDataMapper()
mappera.SetInputConnection(booleanfilter.GetOutputPort())


actora = vtk.vtkActor()
actora.SetMapper(mappera)
actora.GetProperty().EdgeVisibilityOn()
actora.GetProperty().SetEdgeColor(0.1,0.1,0.1)


rendera = vtk.vtkRenderer()
rendera.AddActor(actora)
#rendera.SetBackground(1,1,1)


windowa = vtk.vtkRenderWindow()
windowa.AddRenderer(rendera)
#windowa.SetSize(200,200)


interactora = vtk.vtkRenderWindowInteractor()
interactora.SetRenderWindow(windowa)
interactora.Initialize()
interactora.Start() 
