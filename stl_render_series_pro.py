# -*- coding: utf-8 -*-
import vtk								#to trzeba doinstalowac, "pip install vtk"
import sys
import os
import math
from stl_render_fun import *
from PIL import Image

#import vtkOSPRayPass


cfolder = "E:/GIT/DOKTORAT/STL_ORIENT"		#folder z plikami stl
ifolder = "E:/GIT/DOKTORAT/STL_IMAGES_ORIENT2"		#folder z obrazkami

resolution = 540,540			#rodzielczosc
bgcolor = 0,0,0					#kolor tla, rgb w zakresie 0-1
surface = 1						#czy wyswietlac powierzchnie
scolor = 0.5,0.5,0.5			#kolor powierzchni
edges = 1						#czy wyswietlac krawedzie
ecolor = 1,1,1					#kolor krawedzi
ethickness = 2					#grubosc krawedzi

campos = 1,1,1					#pozycja kamery
camper = 0						#0-perspektywa, 1-rzutowanie rownolegle
noshading = 0					#wylaczenie cieniowania

merge = 1						#czy skleic pliki w jeden duzy

################################################################################

lista = os.listdir(cfolder)		#lista plikow
#print(lista)
#sys.exit()

fname = "dwuteownik_00037.stl"
lista = [fname]

def wrender(im,imfile,killit=0):
	if im:
		win.Render()

		w2if = vtk.vtkWindowToImageFilter()
		w2if.SetInput(win)
		w2if.Update()

		iw = vtk.vtkPNGWriter()
		iw.SetFileName(imfile)
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

im = 1

ren = vtk.vtkRenderer()
win = vtkwin()
win.AddRenderer(ren)
ren.GradientBackgroundOff()
win.SetSize(resolution)
ren.SetBackground(bgcolor)

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
if noshading:
	vprop.LightingOff()
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



vprop.LightingOn()
vprop.SetColor(1,1,1)
vprop.SetInterpolationToPBR()
vprop.SetMetallic(0.3)
vprop.SetRoughness(0.3)
pactor.GetProperty().SetOcclusionStrength(1)
pactor.SetProperty(vprop)

#osprayPass = vtkOSPRayPass()
#ren.SetPass(osprayPass)
'''
tcm = vtk.vtkEquirectangularToCubeMapTexture()
tcm.SetInputTexture(tex)
tcm.MipmapOn()
tcm.InterpolateOn()
tcm.Update()
#print(tex)
print(tcm)
'''
tex.MipmapOn()
tex.InterpolateOn()

ren.AutomaticLightCreationOff()
ren.UseSphericalHarmonicsOff()
ren.UseImageBasedLightingOn()
ren.SetEnvironmentTexture(tex)
ren.UseImageBasedLightingOn()
ren.TexturedBackgroundOn()



########################################################################
camera = ren.GetActiveCamera()
camera.SetPosition(campos)
camera.SetViewUp(0,0,1)
camera.SetFocalPoint(0,0,0)
camera.SetParallelScale(1)
camera.SetParallelProjection(camper)

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



obj  = vtk.vtkOBJImporter()
obj.SetFileName("E:/GIT/DOKTORAT/metal_plate_2k.obj")
obj.SetFileNameMTL("E:/GIT/DOKTORAT/metal_plate_2k.mtl")


# sys.exit()



for plik in lista[:]:

	#plik = lista[1]

	typ = plik.rsplit("_")[0]
	klasa = os.path.join(ifolder,typ)
	if os.path.exists(klasa) == 0:
		os.mkdir(klasa)

	imagename = os.path.join(klasa,plik.replace(".stl",".png"))
	print(imagename)

	imagename1 = imagename.replace(".png","-view01.png")
	imagename2 = imagename.replace(".png","-view02.png")
	imagename3 = imagename.replace(".png","-view03.png")
	imagename4 = imagename.replace(".png","-view04.png")
	print(typ)

	################################################################################		RENDEROWANIE


	campos = 1,1,1
	stlr.SetFileName(os.path.join(cfolder,plik))
	stlr.Update()

	ren.ResetCamera()
	print(camera.GetPosition())
	print(camera.GetFocalPoint())
	ccampos = camera.GetPosition()
	ccamfoc = camera.GetFocalPoint()
	camdis = math.sqrt(math.pow(ccampos[0]-ccamfoc[0],2)+math.pow(ccampos[1]-ccamfoc[1],2)+math.pow(ccampos[2]-ccamfoc[2],2))/math.sqrt(2)
	camera = ren.GetActiveCamera()
	camera.SetPosition(ccamfoc[0]+campos[0]*camdis,ccamfoc[1]+campos[1]*camdis,ccamfoc[2]+campos[2]*camdis)
	ren.ResetCameraClippingRange()
	obj.SetRenderWindow(win)
	# print(obj)
	obj.Update()
	wrender(1,imagename1)
	'''
	campos = 1,-1,1
	camera = ren.GetActiveCamera()
	camera.SetPosition(ccamfoc[0]+campos[0]*camdis,ccamfoc[1]+campos[1]*camdis,ccamfoc[2]+campos[2]*camdis)
	ren.ResetCameraClippingRange()
	wrender(1,imagename2)


	campos = -1,-1,1
	camera = ren.GetActiveCamera()
	camera.SetPosition(ccamfoc[0]+campos[0]*camdis,ccamfoc[1]+campos[1]*camdis,ccamfoc[2]+campos[2]*camdis)
	ren.ResetCameraClippingRange()
	wrender(1,imagename3)


	campos = -1,1,1
	camera = ren.GetActiveCamera()
	camera.SetPosition(ccamfoc[0]+campos[0]*camdis,ccamfoc[1]+campos[1]*camdis,ccamfoc[2]+campos[2]*camdis)
	ren.ResetCameraClippingRange()
	wrender(1,imagename4)


	if merge:


		image1 = Image.open(imagename1)
		image2 = Image.open(imagename2)
		image3 = Image.open(imagename3)
		image4 = Image.open(imagename4)
		#resize, first image
		# image1 = image1.resize((1080, 1080))
		image1_size = image1.size
		new_image = Image.new('RGB',(image1_size[0]*2,image1_size[1]*2), (250,250,250))
		new_image.paste(image1,(0,0))
		new_image.paste(image2,(image1.size[0],0))
		new_image.paste(image3,(0,image1.size[1]))
		new_image.paste(image4,(image1.size[0],image1.size[1]))
		new_image.save(imagename,"PNG")

		os.remove(imagename1)
		os.remove(imagename2)
		os.remove(imagename3)
		os.remove(imagename4)
	'''
