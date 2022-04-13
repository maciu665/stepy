# -*- coding: utf-8 -*-
import vtk
import sys
import os


def setcam(camera,camset):
	camera.SetPosition(camset["cpos"][0],camset["cpos"][1],camset["cpos"][2])
	camera.SetViewUp(camset["cvup"][0],camset["cvup"][1],camset["cvup"][2])
	camera.SetFocalPoint(camset["fpnt"][0],camset["fpnt"][1],camset["fpnt"][2])
	camera.SetParallelScale(camset["cpsc"])
	camera.SetParallelProjection(camset["cpar"])



class my_iren(vtk.vtkInteractorStyleTrackballCamera):
	def __init__(self, parent=None):
			self.AddObserver("CharEvent",self.onKeyPressEvent)

	def onKeyPressEvent(self, renderer, event):
		key = self.GetInteractor().GetKeySym()
		#print key
		self.OnChar()
		if key == "F7":
			(x,y)= self.GetInteractor().GetEventPosition()
			#self._Iren.SetEventInformation(x, y, ctrl, shift, key, 0, keysym)
			movecenter = True
			ren = self.GetInteractor().GetRenderWindow().GetRenderers()
			ren = ren.GetFirstRenderer()
			#print x,y
			self.GetInteractor().GetRenderWindow().picker.Pick(x,y,0,ren)
		if key == "v":
			self.GetInteractor().GetRenderWindow().getviu()
		if key == "F8":
			self.GetInteractor().GetRenderWindow().creset()
		if key == "F5":
			self.GetInteractor().GetRenderWindow().cpar()


class vtkwin(vtk.vtkRenderWindow):
	def __init__(self, *args, **kw):
		print("koza")
		#self.BindEvents()
		self._Iren = vtk.vtkGenericRenderWindowInteractor()
		self._Iren.SetRenderWindow( self)

		self.picker = vtk.vtkPointPicker()
		self.picker.AddObserver("EndPickEvent", self.annotatePick)
		self._Iren.SetPicker(self.picker)


		self.axes = vtk.vtkAxesActor()
		aa2dx = self.axes.GetXAxisCaptionActor2D()
		aa2dy = self.axes.GetYAxisCaptionActor2D()
		aa2dz = self.axes.GetZAxisCaptionActor2D()


		self.axes.GetYAxisTipProperty().SetColor(1,1,0)
		self.axes.GetYAxisShaftProperty().SetColor(1,1,0)
		self.axes.GetZAxisTipProperty().SetColor(0,1,0)
		self.axes.GetZAxisShaftProperty().SetColor(0,1,0)


		#aa2dx.GetProperties().SetColor(0,1,0)
		self.widget = vtk.vtkOrientationMarkerWidget()
		self.widget.SetOrientationMarker(self.axes)
		self.widget.SetInteractor(self._Iren)
		self.widget.SetViewport(-0.11, -0.0, 0.25, 0.25 )
		#self.widget.SetViewport(0, 0, 0.2, 0.2 )

		propA = vtk.vtkTextProperty()
		propA.ItalicOff()
		propA.BoldOff()
		propA.SetFontSize(20)
		propA.SetColor([1,1,1])
		aa2dx.SetCaptionTextProperty(propA)
		aa2dy.SetCaptionTextProperty(propA)
		aa2dz.SetCaptionTextProperty(propA)

	def annotatePick(self,x,y):
		#print "mucha"
		#print x
		pickPos = self.picker.GetPickPosition()
		#print pickPos
		ren = self._Iren.GetRenderWindow().GetRenderers()
		ren = ren.GetFirstRenderer()
		camera = ren.GetActiveCamera()
		camera.SetFocalPoint(pickPos)
		self.Render()

	def getviu(self):
		print("viu")
		#print self
		rens = self.GetRenderers()
		#print rens
		ren = rens.GetFirstRenderer()
		cam = ren.GetActiveCamera()
		fp = cam.GetFocalPoint()
		cp = cam.GetPosition()
		vu = cam.GetViewUp()
		pp = cam.GetParallelProjection()
		cd = cam.GetDistance()
		ps = cam.GetParallelScale()

		print("[%s,%s,%s,%s,%s,%s]"%(fp,cp,vu,pp,cd,ps))

		'''
		cam.SetFocalPoint(3000,0,1000)
		cam.SetPosition(-3000,-6000,7000)
		cam.SetViewUp(0,0,1)
		cam.SetParallelProjection(1)
		cam.SetDistance(1000)
		cam.SetParallelScale(3000)
		cam.SetClippingRange(0,100000)
		'''

	def creset(self):
		rens = self.GetRenderers()
		ren = rens.GetFirstRenderer()
		ren.ResetCamera()
	def cpar(self):
		rens = self.GetRenderers()
		ren = rens.GetFirstRenderer()
		ren.ResetCamera()
		cam = ren.GetActiveCamera()
		cam.SetParallelProjection(not cam.GetParallelProjection())
