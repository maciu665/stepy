# -*- coding: utf-8 -*-
import vtk
import sys
import numpy as np
import os
import math
from vtk.util.numpy_support import vtk_to_numpy
from stl_render_fun import *
import subprocess
from PIL import Image
import gc

#import vtkOSPRayPass

cfolder = "E:/GIT/DOKTORAT/STL"

lista = os.listdir(cfolder)
print(lista)


fname = "dwuteownik_00083.stl"

def wrender(im,imname="koza",killit=0):
	if im:
		win.Render()

		w2if = vtk.vtkWindowToImageFilter()
		w2if.SetInput(win)
		w2if.Update()

		iw = vtk.vtkPNGWriter()
		iw.SetFileName("E:/GIT/DOKTORAT/STL_IMAGE/"+"%s.png"%imname)
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





im = 1

for fname in lista[660:]:

	ren = vtk.vtkRenderer()
	#win = vtk.vtkRenderWindow()
	win = vtkwin()
	win.AddRenderer(ren)
	ren.GradientBackgroundOff()
	ren.SetBackground(1,1,1)
	#ren.SetBackground(1,0.9,1)
	#ren.SetBackground2(0.7,0.70,1)
	win.SetSize(960,540)
	#if fhd:
	win.SetSize(1080,1080)
	win.SetSize(540,540)
	ren.SetBackground(81.0/255.0,87.0/255.0,110.0/255.0)
	ren.SetBackground(0,0,0)
	ren.SetBackground(1,1,1)

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
	stlr.SetFileName(os.path.join(cfolder,fname))
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
	vprop.SetColor(0.5,0.5,0.5)
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

	ecolor = 1,1,1
	ecolor = 0,0,0

	eprop = eactor.GetProperty()
	eprop.SetEdgeColor(ecolor)
	eprop.SetColor(ecolor)
	eprop.SetLineWidth(1)
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

	########################################################################	SHADED

	sb0tprop = vtk.vtkTextProperty()
	sb0tprop.SetFontSize(40)
	sb0tprop.SetColor(1,0,1)
	sb0tprop.SetFontFamilyToArial()
	sb0tprop.BoldOff()
	sb0tprop.ItalicOff()
	sb0tprop.ShadowOff()
	sb0tprop.SetOrientation(90)
	sb0tprop.SetVerticalJustificationToCentered()
	sb0tprop.SetJustificationToCentered()

	sb0text = vtk.vtkTextActor()
	# sb0text.SetTextScaleModeToProp()
	sb0text.SetInput("Velocity [m/s]")
	sb0text.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
	sb0text.GetPositionCoordinate().SetValue(0.03, 0.82)
	sb0text.SetTextProperty(sb0tprop)
	#ren.AddActor(sb0text)

	labtp = vtk.vtkTextProperty()
	labtp.SetFontSize(16)
	labtp.SetColor(1,0,1)
	labtp.SetFontFamilyToArial()
	labtp.BoldOff()
	labtp.ItalicOff()
	labtp.ShadowOff()

	########################################################################	TYTUL

	titprop = vtk.vtkTextProperty()
	titprop.SetFontSize(2)
	titprop.SetFontFamilyToArial()
	titprop.BoldOff()
	titprop.ItalicOff()
	titprop.ShadowOff()
	#titprop.SetVerticalJustificationToCentered()
	#titprop.SetJustificationToCentered()

	titext = vtk.vtkTextActor()
	titext.SetTextScaleModeToProp()
	titext.SetInput("100")
	titext.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
	titext.GetPositionCoordinate().SetValue(0.5, 0.5)
	titext.SetTextProperty(titprop)
	# ren.AddActor(titext)



	ren.AddActor2D(eactor)
	ren.AddActor2D(pactor)
	ren.ResetCamera()
	ren.ResetCamera()

	imname = "image"

	wrender(1,"image1")

	ren.SetBackground(0,0,0)
	ecolor = 1,1,1
	eprop = eactor.GetProperty()
	eprop.SetEdgeColor(ecolor)
	eprop.SetColor(ecolor)
	ren.RemoveActor2D(pactor)

	wrender(1,"image2")

	ren.SetBackground(1,1,1)
	ecolor = 0,0,0
	eprop = eactor.GetProperty()
	eprop.SetEdgeColor(ecolor)
	eprop.SetColor(ecolor)
	ren.AddActor2D(pactor)

	vprop.LightingOff()
	vprop.SetColor(1,1,1)
	vprop.SetSpecular(0)
	vprop.SetSpecularPower(100)

	pactor.SetProperty(vprop)

	wrender(1,"image3")



	vprop.LightingOn()
	vprop.SetColor(1,1,1)
	vprop.SetInterpolationToPBR()
	vprop.SetMetallic(0.3)
	vprop.SetRoughness(0.3)
	pactor.GetProperty().SetOcclusionStrength(1)
	pactor.SetProperty(vprop)

	#osprayPass = vtkOSPRayPass()
	#ren.SetPass(osprayPass)
	tcm = vtk.vtkEquirectangularToCubeMapTexture()
	tcm.SetInputTexture(tex)
	tcm.MipmapOn()
	tcm.InterpolateOn()
	tcm.Update()
	#print(tex)
	print(tcm)

	ren.AutomaticLightCreationOff()
	ren.UseSphericalHarmonicsOff()
	ren.UseImageBasedLightingOn()
	ren.SetEnvironmentTexture(tcm)

	wrender(1,"image4")




	image1 = Image.open("E:/GIT/DOKTORAT/STL_IMAGE/image1.png")
	image2 = Image.open("E:/GIT/DOKTORAT/STL_IMAGE/image2.png")
	image3 = Image.open("E:/GIT/DOKTORAT/STL_IMAGE/image3.png")
	image4 = Image.open("E:/GIT/DOKTORAT/STL_IMAGE/image4.png")
	#resize, first image
	# image1 = image1.resize((1080, 1080))
	image1_size = image1.size
	image2_size = image2.size
	new_image = Image.new('RGB',(1080,1080), (250,250,250))
	new_image.paste(image1,(0,0))
	new_image.paste(image2,(540,0))
	new_image.paste(image3,(0,540))
	new_image.paste(image4,(540,540))
	new_image.save("E:/GIT/DOKTORAT/STL_IMAGE/%s"%(fname.replace(".stl",".png")),"PNG")

	del ren,win, iren, emapper, mapper, pactor,eactor,image1,image2,image3,image4
	gc.collect()
