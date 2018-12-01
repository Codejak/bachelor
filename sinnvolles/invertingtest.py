

from vtk import *
final_shape = "final_shape.stl"

box = vtk.vtkBox()

readera = vtk.vtkSTLReader()
readera.SetFileName(final_shape)
readera.Update()


"""boolean = vtk.vtkImplicitBoolean()
boolean.SetOperationTypeToDifference()
boolean.AddFunction(final_shape)
boolean.AddFunction(box)
"""

mappera = vtk.vtkPolyDataMapper()
mappera.SetInputConnection(box.GetOutputPort())

actora = vtk.vtkActor()
actora.SetMapper(mappera)

rendera = vtk.vtkRenderer()
rendera.AddActor(actora)

windowa = vtk.vtkRenderWindow()
windowa.AddRenderer(rendera)
windowa.SetSize(200,200)

interactora = vtk.vtkRenderWindowInteractor()
interactora.SetRenderWindow(windowa)
interactora.Initialize()

windowa.Render()
interactora.Start() 
print "lol"
