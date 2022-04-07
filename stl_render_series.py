# -*- coding: utf-8 -*-
import vtk								#to trzeba doinstalowac, "pip install vtk"
import sys
import os
from stl_render_fun import *
from PIL import Image

#import vtkOSPRayPass


cfolder = "E:/GIT/DOKTORAT/STL"		#folder z plikami stl
ifolder = "E:/GIT/DOKTORAT/STL_IMAGES"		#folder z obrazkami

resolution = 540,540			#rodzielczosc
bgcolor = 0,0,0					#kolor tla, rgb w zakresie 0-1
surface = True					#czy wyswietlac powierzchnie
scolor = 0.5,0.5,0.5			#kolor powierzchni
edges = True					#czy wyswietlac krawedzie
ecolor = 1,1,1					#kolor krawedzi
ethickness = 2					#grubosc krawedzi


lista = os.listdir(cfolder)		#lista plikow
#print(lista)
#sys.exit()

#fname = "dwuteownik_00083.stl"

def wrender(im,imname="koza",killit=0):
	if im:
		win.Render()

		w2if = vtk.vtkWindowToImageFilter()
		w2if.SetInput(win)
		w2if.Update()

		iw = vtk.vtkPNGWriter()
		iw.SetFileName(os.path.join(ifolder,"%s.png"%imname))
		iw.SetInputData(w2if.GetOutput())
		iw.Write()
		if killit:
			sys.exit()
	else:
		win.OffScreenRenderingOff()
		# ren.ResetCamera()
		win.Render()
		iren.Initialize()
		iren.Start()
		win.Render()
# sys.exit()

'''
tex = vtk.vtkTexture()
ireader = vtk.vtkImageReader2()
ireader.SetFileName("E:/GIT/DOKTORAT/cloud_layers_4k.jpg")
ireader.Update()
tex.SetInputConnection(ireader.GetOutputPort())


hreader = vtk.vtkHDRReader()
hreader.SetFileName("E:/GIT/DOKTORAT/red_hill_curve_4k.hdr")
hreader.SetFileName("E:/GIT/DOKTORAT/cloud_layers_4k.hdr")
tex.SetColorModeToDirectScalars()
tex.SetInputConnection(hreader.GetOutputPort())
'''


im = 1



ren = vtk.vtkRenderer()
#win = vtk.vtkRenderWindow()
win = vtkwin()
win.AddRenderer(ren)
ren.GradientBackgroundOff()
win.SetSize(resolution)
ren.SetBackground(bgcolor)

iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(win)
iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

# win.widget.SetEnabled(1)
# win.widget.InteractiveOff()


if im:
	win.OffScreenRenderingOn()
else:
	win.Render()
	lights = ren.GetLights()
	lights.InitTraversal()
	hl = lights.GetNextItem()
	hl.SetIntensity(0.0)

######################################################################################################################



stlr = vtk.vtkSTLReader()
stlr.SetFileName(os.path.join(cfolder,lista[0]))
stlr.Update()
stl = stlr.GetOutput()
print(stl)
#sys.exit()
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(stl)
mapper.ScalarVisibilityOff()
mapper.SetResolveCoincidentTopologyToPolygonOffset()
mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(-3.5,-3.5)
# mapper.SetResolveCoincidentTopologyToShiftZBuffer()


edges3 = vtk.vtkFeatureEdges()
edges3.ColoringOff()
edges3.SetInputData(stl)
edges3.ManifoldEdgesOn()
edges3.NonManifoldEdgesOn()
edges3.FeatureEdgesOn()
edges3.BoundaryEdgesOn()
edges3.Update()

vprop = vtk.vtkProperty()
vprop.LightingOn()
vprop.SetColor(scolor)
vprop.SetSpecular(0)
vprop.SetSpecularPower(100)

pactor = vtk.vtkActor()
pactor.SetMapper(mapper)
pactor.SetProperty(vprop)

emapper = vtk.vtkDataSetMapper()
emapper.SetInputConnection(edges3.GetOutputPort())
emapper.SetResolveCoincidentTopologyToPolygonOffset()
emapper.ScalarVisibilityOff()
eactor = vtk.vtkActor()
eactor.SetMapper(emapper)

eprop = eactor.GetProperty()
eprop.SetEdgeColor(ecolor)
eprop.SetColor(ecolor)
eprop.SetLineWidth(ethickness)
eprop.SetRepresentationToWireframe()
eprop.SetOpacity(1)


########################################################################
camera = ren.GetActiveCamera()
camera.SetPosition(1000,1000,1000)
camera.SetViewUp(0,0,1)
camera.SetFocalPoint(0,0,0)
camera.SetParallelScale(1)
camera.SetParallelProjection(0)

########################################################################	LIGHT

#print hl

lightKit = vtk.vtkLightKit()


lightKit.SetKeyLightWarmth(0.6)
lightKit.SetKeyLightIntensity(0.75)
lightKit.SetKeyLightElevation(50)
lightKit.SetKeyLightAzimuth(10)

lightKit.SetFillLightWarmth(0.4)
lightKit.SetKeyToFillRatio(3)
lightKit.SetFillLightElevation(-75)
lightKit.SetFillLightAzimuth(-10)

lightKit.SetBackLightWarmth(0.5)
lightKit.SetKeyToBackRatio(3.50)
lightKit.SetBackLightElevation(0)
lightKit.SetBackLightAzimuth(110)

lightKit.SetHeadLightWarmth(0.5)
lightKit.SetKeyToHeadRatio(3)

lightKit.MaintainLuminanceOn()
lightKit.AddLightsToRenderer(ren)

if edges:
	ren.AddActor2D(eactor)
if surface:
	ren.AddActor2D(pactor)
ren.ResetCamera()
ren.ResetCamera()

#for fname in lista[2]:

imname = "image"

wrender(1,"image1")

wrender(1,"image2")


wrender(1,"image3")

wrender(1,"image4")



image1 = Image.open(os.path.join(ifolder,"image1.png"))
image2 = Image.open(os.path.join(ifolder,"image2.png"))
image3 = Image.open(os.path.join(ifolder,"image3.png"))
image4 = Image.open(os.path.join(ifolder,"image4.png"))
#resize, first image
# image1 = image1.resize((1080, 1080))
image1_size = image1.size
image2_size = image2.size
new_image = Image.new('RGB',(1080,1080), (250,250,250))
new_image.paste(image1,(0,0))
new_image.paste(image2,(image1.size[0],0))
new_image.paste(image3,(0,image1.size[1]))
new_image.paste(image4,(image1.size[0],image1.size[1]))
new_image.save(os.path.join(ifolder,"%s"%(fname.replace(".stl",".png"))),"PNG")
