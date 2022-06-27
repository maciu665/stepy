# -*- coding: utf-8 -*-
import vtk								#to trzeba doinstalowac, "pip install vtk"
import sys
import os
import math
from stl_render_fun import *
from PIL import Image

#import vtkOSPRayPass


cfolder = "E:/GIT/DOKTORAT/STL_PROC"		#folder z plikami stl
ifolder1 = "E:/GIT/DOKTORAT/STL_8IMAGES_SW"		#folder z obrazkami
ifolder2 = "E:/GIT/DOKTORAT/STL_8IMAGES_SB"		#folder z obrazkami
ifolder3 = "E:/GIT/DOKTORAT/STL_8IMAGES_WW"		#folder z obrazkami
ifolder4 = "E:/GIT/DOKTORAT/STL_8IMAGES_WB"		#folder z obrazkami

resolution = 299,299			#rodzielczosc
bgcolor = 0,0,0					#kolor tla, rgb w zakresie 0-1
surface = 1						#czy wyswietlac powierzchnie
scolor = 0.5,0.5,0.5			#kolor powierzchni
edges = 1						#czy wyswietlac krawedzie
ecolor = 1,1,1					#kolor krawedzi
ethickness = 1					#grubosc krawedzi

campos = 1,1,1					#pozycja kamery
camper = 0						#0-perspektywa, 1-rzutowanie rownolegle
noshading = 0					#wylaczenie cieniowania
cam_angle = 1					#pozycja kamery z kątów
azimuth = 45					#azymut kamery
elevation = 30					#wznios kamery

merge = 1						#czy skleic pliki w jeden duzy

################################################################################

lista = os.listdir(cfolder)		#lista plikow
print(lista)
lista.sort()

profile = [[],[],[],[]]
for i in lista:
	if "kwadratowy" in i:
		profile[0].append(i)
	elif "okragly" in i:
		profile[1].append(i)
	elif "profil" in i:
		profile[2].append(i)
	elif "rura" in i:
		profile[3].append(i)

#print(profile[2])
#print(profile[3])
print(len(profile[0]),len(profile[1]),len(profile[2]),len(profile[3]))
# sys.exit()
f = open("E:/GIT/DOKTORAT/camera.txt","r")
linie = f.read().splitlines()
f.close()

print(len(linie))
# sys.exit()



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

smapper = vtk.vtkDataSetMapper()
#smapper.SetInputConnection(edges3.GetOutputPort())
smapper.SetResolveCoincidentTopologyToPolygonOffset()
smapper.ScalarVisibilityOff()
sactor = vtk.vtkActor()
sactor.SetMapper(smapper)

sprop = sactor.GetProperty()
sprop.SetEdgeColor(scolor)
sprop.SetColor(scolor)
sprop.SetLineWidth(ethickness)
sprop.SetRepresentationToWireframe()
sprop.SetOpacity(1)

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
	ren.AddActor(eactor)
if surface:
	ren.AddActor(pactor)
ren.ResetCamera()

lastfile = lista[0]

for l in range(len(linie[:])):
	linia = linie[l].split("_")
	print(linia)

	plik = profile[int(linia[1])][int(linia[0])]
	print(plik)
	coords = linia[5].split("(")[1].split(")")[0]
	print(coords)
	cx = float(coords.split(", ")[0])
	cy = float(coords.split(", ")[1])
	cz = float(coords.split(", ")[2])

	'''
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
	'''

	################################################################################		RENDEROWANIE
	azimuth = float(linia[3])
	elevation = float(linia[4])
	x = math.sin(math.radians(azimuth))*math.cos(math.radians(elevation))
	y = math.cos(math.radians(azimuth))*math.cos(math.radians(elevation))
	z = math.sin(math.radians(elevation))
	vector = [x,y,z]
	print(vector)
	imname = plik.replace(".stl","")+"-view%s.png"%(str(int(linia[2])+1).zfill(2))
	imfile = os.path.join(ifolder1,imname)
	print(plik, imname)
	print(imfile)

	campos = cx*1,cy*1,cz*1
	camfoc = (cx-y)*1,(cy-x)*1,(cz-z)*1
	camera.SetPosition(campos)
	camera.SetFocalPoint(camfoc)
	#camera.SetFocalPoint(0,0,0)
	camera.SetViewUp(0,0,1)

	cangle = 39.5978
	if lastfile != plik:
		stlr.SetFileName(os.path.join(cfolder,plik))
		stlr.Update()
		stl = stlr.GetOutput()

		spb = stl.GetBounds()
		print(spb)
		#sys.exit()
		maxdim = max(spb[3]-spb[2],spb[5]-spb[4])
		#print(maxdim,4*maxdim)
		#print(spb[1] > (2*maxdim))
		if spb[1] > (2*maxdim):
			tx = (2*maxdim) - spb[1]
		else:
			tx = 0
		#print("tx",tx)

		transowanie = vtk.vtkTransformFilter()
		trans = vtk.vtkTransform()
		trans.Scale(1, 1, 1)
		#trans.Translate(tx,0,spb[4]*-1)
		transowanie.SetTransform(trans)
		transowanie.SetInputData(stl)
		transowanie.Update()
		stl = transowanie.GetOutput()

		mapper.SetInputData(stl)

		edges3.SetInputData(stl)
		edges3.Update()


		lastfile = plik

	#print(camera.GetPosition())
	#print(camera.GetFocalPoint())
	#print(camera.GetClippingRange())
	camera.SetViewAngle(cangle)
	#ren.ResetCamera()
	# print(camera.GetPosition())
	ren.ResetCameraClippingRange()

	sil = vtk.vtkPolyDataSilhouette()
	sil.SetInputData(stl)
	sil.SetCamera(ren.GetActiveCamera())
	sil.SetEnableFeatureAngle(0)
	smapper.SetInputConnection(sil.GetOutputPort())

	try:
		ren.RemoveActor(pactor)
		ren.RemoveActor(eactor)
		ren.RemoveActor(sactor)
	except:
		pass

	ren.AddActor(pactor)
	ren.SetBackground(1,1,1)
	wrender(1,imfile)
	ren.SetBackground(0,0,0)
	imfile = os.path.join(ifolder2,imname)
	wrender(1,imfile)

	ren.RemoveActor(pactor)
	ren.AddActor(eactor)
	ren.AddActor(sactor)
	ren.SetBackground(1,1,1)
	eprop.SetEdgeColor(0,0,0)
	sprop.SetEdgeColor(0,0,0)
	eprop.SetColor(0,0,0)
	sprop.SetColor(0,0,0)

	imfile = os.path.join(ifolder3,imname)
	wrender(1,imfile)

	ren.SetBackground(0,0,0)
	eprop.SetEdgeColor(1,1,1)
	sprop.SetEdgeColor(1,1,1)
	eprop.SetColor(1,1,1)
	sprop.SetColor(1,1,1)
	imfile = os.path.join(ifolder4,imname)
	wrender(1,imfile)

sys.exit()

#
#ifolder1 = "E:/GIT/DOKTORAT/STL_IMAGES_SW"		#folder z obrazkami
#ifolder2 = "E:/GIT/DOKTORAT/STL_IMAGES_SB"		#folder z obrazkami
#ifolder3 = "E:/GIT/DOKTORAT/STL_IMAGES_WW"		#folder z obrazkami
#ifolder4 = "E:/GIT/DOKTORAT/STL_IMAGES_WB"
