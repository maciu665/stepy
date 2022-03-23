# -*- coding: utf-8 -*-
import wx
import os
import shutil
#import pyvtk as vtk
import vtk
import math
import builtins
from wx.lib.agw.floatspin import FloatSpin as FS
#import numpy as np
#from numpy import array, dot, sqrt

baseClass = wx.Window
if wx.Platform == "__WXGTK__":
	import wx.glcanvas
	baseClass = wx.glcanvas.GLCanvas

global movecenter, picktype, pickstart, pickdxyz, mdown, pickid
movecenter = False
picktype = 0
pickstart = None
mdown = 0
pickid = None
_useCapture = (wx.Platform == "__WXMSW__")

class EventTimer(wx.Timer):
	def __init__(self, iren):
		wx.Timer.__init__(self)
		self.iren = iren
	def Notify(self):
		self.iren.TimerEvent()

class vtkwin(baseClass):
	USE_STEREO = True
	a = vtk.vtkCommand
	#print dir(a)

	global movecenter, picktype, pickstart, mdown, pickid

	def __init__(self, parent, ID, actors, *args, **kw):
		self.__RenderWhenDisabled = 0
		stereo = 0
		#print __builtin__.parallel
		#self.SetStereoTypeToRedBlue()

		if 'stereo' in kw:
			if kw['stereo']:
				stereo = 1
			del kw['stereo']

		elif self.USE_STEREO:
			stereo = 1
		position, size = wx.DefaultPosition, (800,600)

		if 'position' in kw:
			position = kw['position']
			del kw['position']

		if 'size' in kw:
			size = kw['size']
			del kw['size']

		style = wx.WANTS_CHARS | wx.NO_FULL_REPAINT_ON_RESIZE

		if 'style' in kw:
			style = style | kw['style']
			del kw['style']

		if wx.Platform != '__WXMSW__':
			l = []
			p = parent
			while p: # make a list of all parents
				l.append(p)
				p = p.GetParent()
			l.reverse() # sort list into descending order
			for p in l:
				p.Show(1)

		if baseClass.__name__ == 'GLCanvas':
			attribList = [wx.glcanvas.WX_GL_RGBA,
						  wx.glcanvas.WX_GL_MIN_RED, 1,
						  wx.glcanvas.WX_GL_MIN_GREEN, 1,
						  wx.glcanvas.WX_GL_MIN_BLUE, 1,
						  wx.glcanvas.WX_GL_DEPTH_SIZE, 16,
						  wx.glcanvas.WX_GL_DOUBLEBUFFER]
			if stereo:
				attribList.append(wx.glcanvas.WX_GL_STEREO)

			try:
				baseClass.__init__(self, parent, ID, position, size, style,
								   attribList=attribList)
			except wx.PyAssertionError:
				baseClass.__init__(self, parent, ID, position, size, style)
				if stereo:
					stereo = 0

		else:
			baseClass.__init__(self, parent, ID, position, size, style)

		# create the RenderWindow and initialize it
		self._Iren = vtk.vtkGenericRenderWindowInteractor()
		#a = self._Iren
		#print dir(a)
		self._Iren.SetRenderWindow( vtk.vtkRenderWindow() )
		self._Iren.AddObserver('CreateTimerEvent', self.CreateTimer)
		self._Iren.AddObserver('DestroyTimerEvent', self.DestroyTimer)
		self._Iren.GetRenderWindow().AddObserver('CursorChangedEvent',
												 self.CursorChangedEvent)
		#self._Iren.GetRenderWindow().SetAAFrames(50)
		tball = vtk.vtkInteractorStyleTrackballCamera()
		#tball = vtk.vtkInteractorStyleRubberBandPick()
		self._Iren.SetInteractorStyle(tball)
		#print self._Iren.CurrentMode()
		#print self.CurrentMode()


		self.axes = vtk.vtkAxesActor()
		aa2dx = self.axes.GetXAxisCaptionActor2D()
		aa2dy = self.axes.GetYAxisCaptionActor2D()
		aa2dz = self.axes.GetZAxisCaptionActor2D()
		self.widget = vtk.vtkOrientationMarkerWidget()
		self.widget.SetOrientationMarker(self.axes)
		self.widget.SetInteractor(self._Iren)
		self.widget.SetViewport(-0.1, -0.1, 0.2, 0.2 )

		propA = vtk.vtkTextProperty()
		propA.ItalicOff()
		propA.BoldOff()
		propA.SetColor([1,0,1])
		aa2dx.SetCaptionTextProperty(propA)
		aa2dy.SetCaptionTextProperty(propA)
		aa2dz.SetCaptionTextProperty(propA)

		self.widget.SetKeyPressActivation(0)

		###########################################

		self.boxWidget = vtk.vtkBoxWidget()
		self.boxWidget.SetKeyPressActivation(0)
		#self.boxWidget.SetKeyPressActivationValue("t")
		self.boxWidget.SetInteractor(self._Iren)
		self.boxWidget.SetPlaceFactor(1.1)
		self.boxWidget.SetRotationEnabled(0)

		########################################################


		self.picker = vtk.vtkPointPicker()

		builtins.myactor = self.picker
		self.picker.PickFromListOn()

		# Now at the end of the pick event call the above function.
		self.picker.AddObserver("EndPickEvent", self.annotatePick)


		self._Iren.SetPicker(self.picker)

		try:
			self._Iren.GetRenderWindow().SetSize(size.width, size.height)
		except AttributeError:
			self._Iren.GetRenderWindow().SetSize(size[0], size[1])

		if stereo:
			self._Iren.GetRenderWindow().StereoCapableWindowOn()
			self._Iren.GetRenderWindow().SetStereoTypeToAnaglyph()
			#self._Iren.GetRenderWindow().SetStereoTypeToRedBlue()
			#print self._Iren.GetRenderWindow().GetAnaglyphColorMask()
			self._Iren.GetRenderWindow().SetAnaglyphColorMask(4,3)
			self._Iren.GetRenderWindow().SetAnaglyphColorSaturation(0.0)

			#print self._Iren.GetRenderWindow().GetAnaglyphColorMask()


		self.__handle = None

		self.BindEvents()

		self.__has_painted = False

		# set when we have captured the mouse.
		self._own_mouse = False
		# used to store WHICH mouse button led to mouse capture
		self._mouse_capture_button = 0

		# A mapping for cursor changes.
		self._cursor_map = {0: wx.CURSOR_ARROW, # VTK_CURSOR_DEFAULT
							1: wx.CURSOR_ARROW, # VTK_CURSOR_ARROW
							2: wx.CURSOR_SIZENESW, # VTK_CURSOR_SIZENE
							3: wx.CURSOR_SIZENWSE, # VTK_CURSOR_SIZENWSE
							4: wx.CURSOR_SIZENESW, # VTK_CURSOR_SIZESW
							5: wx.CURSOR_SIZENWSE, # VTK_CURSOR_SIZESE
							6: wx.CURSOR_SIZENS, # VTK_CURSOR_SIZENS
							7: wx.CURSOR_SIZEWE, # VTK_CURSOR_SIZEWE
							8: wx.CURSOR_SIZING, # VTK_CURSOR_SIZEALL
							9: wx.CURSOR_HAND, # VTK_CURSOR_HAND
							10: wx.CURSOR_CROSS, # VTK_CURSOR_CROSSHAIR
						   }

	def perspective(self):
		#global parallel
		builtins.parallel = not builtins.parallel
		#print __builtin__.parallel
		ren = self._Iren.GetRenderWindow().GetRenderers()
		ren = ren.GetFirstRenderer()
		ren.GetActiveCamera().SetParallelProjection(builtins.parallel)
		distance = ren.GetActiveCamera().GetDistance()
		ren.GetActiveCamera().SetParallelScale(distance/4)
		self.Render()

	def align(self):
		#print "align"
		ren = self._Iren.GetRenderWindow().GetRenderers()
		ren = ren.GetFirstRenderer()
		camera = ren.GetActiveCamera()
		pos = camera.GetPosition()
		foc = camera.GetFocalPoint()
		dx = pos[0]-foc[0]
		dy = pos[1]-foc[1]
		dz = pos[2]-foc[2]
		camdist = math.sqrt(math.pow(dx,2)+math.pow(dy,2)+math.pow(dz,2))
		ren.ResetCamera()

		uvec = 0

		ux, uy, uz = camera.GetViewUp()
		if abs(ux) > abs(uy) and abs(ux) > abs(uz):
			#if abs(ux) > math.sqrt(math.pow(uy,2) + math.pow(uz,2)):
			if ux>0:
				camup = 1,0,0
			else:
				camup = -1,0,0
			uvec = 0
			#elif abs(uy) > math.sqrt(math.pow(ux,2) + math.pow(uz,2)):
		elif abs(uy) > abs(ux) and abs(uy) > abs(uz):
			if uy>0:
				camup = 0,1,0
			else:
				camup = 0,-1,0
			uvec = 1
		else:
			if uz>0:
				camup = 0,0,1
			else:
				camup = 0,0,-1
			uvec = 2

		if uvec == 0:
			if abs(dy) > abs(dz):
				if dy > 0:
					newpos = [foc[0],foc[1]+camdist,foc[2]]
				else:
					newpos = [foc[0],foc[1]-camdist,foc[2]]
			else:
				if dz > 0:
					newpos = [foc[0],foc[1],foc[2]+camdist]
				else:
					newpos = [foc[0],foc[1],foc[2]-camdist]
		elif uvec == 1:
			if abs(dx) > abs(dz):
				if dx > 0:
					newpos = [foc[0]+camdist,foc[1],foc[2]]
				else:
					newpos = [foc[0]-camdist,foc[1],foc[2]]
			else:
				if dz > 0:
					newpos = [foc[0],foc[1],foc[2]+camdist]
				else:
					newpos = [foc[0],foc[1],foc[2]-camdist]
		elif uvec == 2:
			if abs(dx) > abs(dy):
				if dx > 0:
					newpos = [foc[0]+camdist,foc[1],foc[2]]
				else:
					newpos = [foc[0]-camdist,foc[1],foc[2]]
			else:
				if dy > 0:
					newpos = [foc[0],foc[1]+camdist,foc[2]]
				else:
					newpos = [foc[0],foc[1]-camdist,foc[2]]

		try:
			dvx = dx/abs(dx)
		except:
			dvx = 0
		try:
			dvy = dy/abs(dy)
		except:
			dvy = 0
		try:
			dvz = dz/abs(dz)
		except:
			dvz = 0

		dcd = camdist/1.732
		iso = False
		if abs(dx) >= abs(dy) and abs(dx) >= abs(dz) and abs(dy) > (0.4*abs(dx)) and abs(dz) > (0.4*abs(dx)):
			iso = True
		elif abs(dy) >= abs(dx) and abs(dy) >= abs(dz) and abs(dx) > (0.4*abs(dy)) and abs(dz) > (0.4*abs(dy)):
			iso = True
		elif abs(dz) >= abs(dx) and abs(dz) >= abs(dy) and abs(dx) > (0.4*abs(dz)) and abs(dy) > (0.4*abs(dz)):
			iso = True

		if iso:
			newpos = [foc[0]+dcd*dvx,foc[1]+dcd*dvy,foc[2]+dcd*dvz]

		camera.SetPosition(newpos)
		camera.SetViewUp(camup)
		self.Render()

	def annotatePick(self,object, event):
		#print object, event

		#print self.picker.GetPointId()

		global picker, textActor2, textMapper, movecenter, picktype, pickstart, pickdxyz, pickid
		#print picktype
		#vtk.vtkAreaPicker(picker)
		if picktype == 2 and pickstart == None:
			picktype = 1

		if self.picker.GetPointId() < 0:
			#textActor2.VisibilityOff()
			pass
		else:
			if movecenter:
				movecenter = not movecenter
				pickPos = self.picker.GetPickPosition()
				#print pickPos
				ren = self._Iren.GetRenderWindow().GetRenderers()
				ren = ren.GetFirstRenderer()
				camera = ren.GetActiveCamera()
				camera.SetFocalPoint(pickPos)
				self.Render()
			else:
				#print "mu"
				#selPt = self.picker.GetSelectionPoint()
				#print selPt
				pickPos = self.picker.GetPickPosition()
				ren = self._Iren.GetRenderWindow().GetRenderers()
				#vtk.vtkAreaPicker(self._Iren.GetPicker())
				#print ren
				ind = builtins.nactors.index(self.picker.GetActor())
				#print self.picker.GetActor().GetMapper().GetArrayName()

				#print __builtin__.arrays[ind][0].GetTuple(self.picker.GetPointId())[0]

				ren = ren.GetFirstRenderer()
				if picktype == 0:
					pickstart = None
					propT = vtk.vtkTextProperty()
					propT.ItalicOff()
					propT.BoldOff()
					propT.SetColor(builtins.actor2dcol)
					print(pickPos)
					splab = vtk.vtkCaptionActor2D()
					if builtins.pmode:
						splab.SetCaption("%.3f [m/s], %.3f [bar]"%(builtins.arrays[ind][0].GetTuple(self.picker.GetPointId())[0],builtins.arrays[ind][1].GetTuple(self.picker.GetPointId())[0]))
					else:
						splab.SetCaption("%.3f [m/s], %.3f [Pa]"%(builtins.arrays[ind][0].GetTuple(self.picker.GetPointId())[0],builtins.arrays[ind][1].GetTuple(self.picker.GetPointId())[0]))
					#print self.picker.GetPointId()
					splab.LeaderOn()
					splab.ThreeDimensionalLeaderOff()
					splab.SetPosition(40,40)
					splab.SetHeight(0.04)
					splab.BorderOn()
					splab.SetCaptionTextProperty(propT)
					splab.SetAttachmentPoint(pickPos)
					splab.GetProperty().SetColor(builtins.actor2dcol)

					builtins.actors.append(splab)
					ren.AddActor(splab)
					self.Render()
					'''
				elif picktype == 1 or (picktype == 2 and mdown == 1):
					sdisp = 0
					sdxyz = 0
					svmis = 0
					__builtin__.spoint.SetCenter(self.picker.GetPickPosition())

					if picktype == 1:
						pickstart = self.picker.GetPickPosition()
						pickdxyz = sdxyz
						pickid = self.picker.GetPointId()

					__builtin__.statusbar.SetStatusText('VMIS = 2f MPA ')
					ren.AddActor(__builtin__.spActor)
					__builtin__.actors.append(__builtin__.spActor)

					koza = vtk.vtkIdList()
					__builtin__.ext.GetPointCells(self.picker.GetPointId(),koza)
					if picktype == 2:
						koza2 = vtk.vtkIdList()
						__builtin__.ext.GetPointCells(pickid,koza2)
						for i in range(koza2.GetNumberOfIds()):
							koza.InsertNextId(koza2.GetId(i))

					#print koza.GetNumberOfIds()
					sn = vtk.vtkSelectionNode()
					sn.SetFieldType(0)      # POINTS (vtkSelectionNode enum)
					sn.SetContentType(4)    # INDICES ('')
					idsArray = vtk.vtkIdTypeArray()
					pointsList = vtk.vtkIdList()
					for h in range(koza.GetNumberOfIds()):
						idsArray.InsertNextValue(koza.GetId(h))

					sn.SetSelectionList(idsArray)
					s = vtk.vtkSelection()
					s.AddNode(sn)
					__builtin__.scell.SetInput(1,s)

					__builtin__.scell.Update()
					__builtin__.bdscell.SetInput(__builtin__.scell.GetOutput())
					__builtin__.bdscell.Update()
					__builtin__.actors.append(__builtin__.scActor)

					scMapper = vtk.vtkPolyDataMapper()
					scMapper.SetInput(__builtin__.bdscell.GetOutput())
					__builtin__.scActor = vtk.vtkActor()
					__builtin__.scActor.GetProperty().SetColor(1,0,1)
					__builtin__.scActor.GetProperty().SetRepresentationToWireframe()
					__builtin__.scActor.GetProperty().SetLighting(0)
					__builtin__.scActor.SetMapper(scMapper)
					scMapper.ScalarVisibilityOff()
					ren.AddActor(__builtin__.scActor)
					__builtin__.actors.append(__builtin__.scActor)
					self.Render()

				else:
					sdisp = __builtin__.disparray.GetTuple(self.picker.GetPointId())[0]
					sdxyz = __builtin__.dxyzarray.GetTuple(self.picker.GetPointId())
					svmis = __builtin__.vmisarray.GetTuple(self.picker.GetPointId())[0]
					#__builtin__.spoint.SetCenter(self.picker.GetPickPosition())

					mpoint = self.picker.GetPickPosition()
					#print
					#print pickstart
					#print mpoint
					#print plen(pickstart,mpoint)
					addmeasure(pickstart,pickdxyz,mpoint,ren,sdxyz)
					self.Render()
					'''

	def selcolor(self):
		ren = self._Iren.GetRenderWindow().GetRenderers()
		ren = ren.GetFirstRenderer()
		propT = vtk.vtkTextProperty()
		propT.ItalicOff()
		propT.BoldOff()
		propT.SetColor(builtins.actor2dcol)
		for i in builtins.actors:
			try:
				i.SetCaptionTextProperty(propT)
				i.GetProperty().SetColor(builtins.actor2dcol)
			except:
				pass
		self.Render()

	def clearsel(self):
		ren = self._Iren.GetRenderWindow().GetRenderers()
		ren = ren.GetFirstRenderer()
		for i in builtins.actors:
			ren.RemoveActor(i)
		self.Render()

	def showhelp(self):
		ren = self._Iren.GetRenderWindow().GetRenderers()
		ren = ren.GetFirstRenderer()
		if builtins.helpOn:
			ren.RemoveActor(builtins.helpActor)
			builtins.helpOn = False
		else:
			ren.AddActor(builtins.helpActor)
			builtins.helpOn = True
		self.Render()

	def BindEvents(self):
		"""Binds all the necessary events for navigation, sizing,
		drawing.
		"""
		# refresh window by doing a Render
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		# turn off background erase to reduce flicker
		self.Bind(wx.EVT_ERASE_BACKGROUND, lambda e: None)

		# Bind the events to the event converters
		self.Bind(wx.EVT_RIGHT_DOWN, self.OnButtonDown)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnButtonDown)
		self.Bind(wx.EVT_MIDDLE_DOWN, self.OnButtonDown)
		self.Bind(wx.EVT_RIGHT_UP, self.OnButtonUp)
		self.Bind(wx.EVT_LEFT_UP, self.OnButtonUp)
		self.Bind(wx.EVT_MIDDLE_UP, self.OnButtonUp)
		self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
		self.Bind(wx.EVT_MOTION, self.OnMotion)

		self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
		self.Bind(wx.EVT_CHAR, self.OnKeyDown)
		self.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

		self.Bind(wx.EVT_SIZE, self.OnSize)
		if _useCapture and hasattr(wx, 'EVT_MOUSE_CAPTURE_LOST'):
			self.Bind(wx.EVT_MOUSE_CAPTURE_LOST,
					self.OnMouseCaptureLost)


	def __getattr__(self, attr):
		"""Makes the object behave like a
		vtkGenericRenderWindowInteractor.
		"""
		if attr == '__vtk__':
			return lambda t=self._Iren: t
		elif hasattr(self._Iren, attr):
			return getattr(self._Iren, attr)
		else:
			raise AttributeError(self.__class__.__name__ + \
				  " has no attribute named " + attr)

	def CreateTimer(self, obj, evt):
		self._timer = EventTimer(self)
		self._timer.Start(10, True)

	def DestroyTimer(self, obj, evt):
		return 1

	def _CursorChangedEvent(self, obj, evt):
		cur = self._cursor_map[obj.GetCurrentCursor()]
		c = wx.StockCursor(cur)
		self.SetCursor(c)

	def CursorChangedEvent(self, obj, evt):
		wx.CallAfter(self._CursorChangedEvent, obj, evt)

	def HideCursor(self):
		c = wx.StockCursor(wx.CURSOR_BLANK)
		self.SetCursor(c)

	def ShowCursor(self):
		rw = self._Iren.GetRenderWindow()
		cur = self._cursor_map[rw.GetCurrentCursor()]
		c = wx.StockCursor(cur)
		self.SetCursor(c)

	def GetDisplayId(self):
		d = None
		'''
		try:
			d = wx.GetXDisplay()

		except NameError:
			pass
		'''
		if d:
			d = hex(d)
			if not d.startswith('0x'):
				d = '0x' + d
			d = '_%s_%s' % (d[2:], 'void_p')

		return d

	def OnMouseCaptureLost(self, event):
		if _useCapture and self._own_mouse:
			self._own_mouse = False

	def OnPaint(self,event):
		event.Skip()
		dc = wx.PaintDC(self)
		self._Iren.GetRenderWindow().SetSize(self.GetSize())
		if not self.__handle:
			d = self.GetDisplayId()
			if d:
				self._Iren.GetRenderWindow().SetDisplayId(d)

			self.__handle = self.GetHandle()
			self._Iren.GetRenderWindow().SetWindowInfo(str(self.__handle))
			self.__has_painted = True

		self.Render()

	def OnSize(self,event):
		event.Skip()

		try:
			width, height = event.GetSize()
		except:
			width = event.GetSize().width
			height = event.GetSize().height
		self._Iren.SetSize(width, height)
		self._Iren.ConfigureEvent()

		# this will check for __handle
		self.Render()

	def OnMotion(self,event):
		event.Skip()

		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
											event.ControlDown(),
											event.ShiftDown(),
											chr(0), 0, None)
		self._Iren.MouseMoveEvent()

		#ren = self._Iren.GetRenderWindow().GetRenderers()
		#ren = ren.GetFirstRenderer()
		#print self._Iren.GetEventPosition()
		#picktype = 1
		(x,y)= self._Iren.GetEventPosition()
		#print x, y
		#self.picker.Pick(x,y,0,ren)

	def OnEnter(self,event):
		event.Skip()

		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
											event.ControlDown(),
			  event.ShiftDown(),
			  chr(0), 0, None)
		self._Iren.EnterEvent()


	def OnLeave(self,event):
		event.Skip()

		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
											event.ControlDown(),
			  event.ShiftDown(),
			  chr(0), 0, None)
		self._Iren.LeaveEvent()


	def OnButtonDown(self,event):
		global picktype
		event.Skip()

		ctrl, shift = event.ControlDown(), event.ShiftDown()
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
											ctrl, shift, chr(0), 0, None)

		button = 0
		if event.LeftDown():
			self._Iren.LeftButtonPressEvent()
			button = 'Left'
		elif event.RightDown():
			if self.boxWidget.GetEnabled():
				self._Iren.RightButtonPressEvent()
			else:
				#print "down"
				#self.picker.InvokeEvent("EndPickEvent")
				(x,y)= self._Iren.GetEventPosition()
				#print x, y

				ren = self._Iren.GetRenderWindow().GetRenderers()
				ren = ren.GetFirstRenderer()
				#print self._Iren.GetEventPosition()
				picktype = 0
				self.picker.Pick(x,y,0,ren)
			button = "Right"


		elif event.MiddleDown():
			self._Iren.MiddleButtonPressEvent()
			button = 'Middle'
		if _useCapture and not self._own_mouse:
			self._own_mouse = True
			self._mouse_capture_button = button
			self.CaptureMouse()


	def OnButtonUp(self,event):
		event.Skip()

		button = 0
		if event.RightUp():
			button = 'Right'
		elif event.LeftUp():
			button = 'Left'
		elif event.MiddleUp():
			button = 'Middle'

		if _useCapture and self._own_mouse and button==self._mouse_capture_button:
			self.ReleaseMouse()
			self._own_mouse = False

		ctrl, shift = event.ControlDown(), event.ShiftDown()
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
											ctrl, shift, chr(0), 0, None)

		if button == 'Right':
			self._Iren.RightButtonReleaseEvent()
		elif button == 'Left':
			self._Iren.LeftButtonReleaseEvent()
		elif button == 'Middle':
			self._Iren.MiddleButtonReleaseEvent()


	def OnMouseWheel(self,event):
		event.Skip()

		ctrl, shift = event.ControlDown(), event.ShiftDown()
		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
											ctrl, shift, chr(0), 0, None)
		if event.GetWheelRotation() < 0:
			self._Iren.MouseWheelForwardEvent()
		else:
			self._Iren.MouseWheelBackwardEvent()


	def OnKeyDown(self,event):
		global movecenter, picktype, mdown
		event.Skip()

		ctrl, shift = event.ControlDown(), event.ShiftDown()
		keycode, keysym = event.GetKeyCode(), None

		#print keycode
		if keycode == 344:
			self.perspective()
		elif keycode == 340:
			self._Iren.MiddleButtonPressEvent()
			button = 'Middle'
		elif keycode == 341:
			self._Iren.RightButtonPressEvent()
			button = 'Right'
		elif keycode == 342:
			self._Iren.LeftButtonPressEvent()
			button = 'Left'
		elif keycode == 343:
			self.align()
		elif keycode == 347:
			ren = self._Iren.GetRenderWindow().GetRenderers()
			ren = ren.GetFirstRenderer()
			ren.ResetCamera()
			self.Render()
		elif keycode == 27:
			self.clearsel()
		elif keycode == 104:
			self.showhelp()
		elif keycode == 32:
			self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),	ctrl, shift, chr(0), 0, None)
			(x,y)= self._Iren.GetEventPosition()
			ren = self._Iren.GetRenderWindow().GetRenderers()
			ren = ren.GetFirstRenderer()
			#print self._Iren.GetEventPosition()
			picktype = 1
			self.picker.Pick(x,y,0,ren)
		elif keycode == 109:
			mdown = 1
			self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),	ctrl, shift, chr(0), 0, None)
			(x,y)= self._Iren.GetEventPosition()
			ren = self._Iren.GetRenderWindow().GetRenderers()
			ren = ren.GetFirstRenderer()
			#print self._Iren.GetEventPosition()
			picktype = 2
			self.picker.Pick(x,y,0,ren)

		key = chr(0)
		if keycode < 256:
			key = chr(keycode)

		if keycode != 113 and keycode != 101 and keycode != 102 and keycode != 346 and keycode != 112 and keycode != 115 and keycode != 119:
			(x,y)= self._Iren.GetEventPosition()
			self._Iren.SetEventInformation(x, y,ctrl, shift, key, 0,keysym)
			self._Iren.KeyPressEvent()
			self._Iren.CharEvent()
		elif keycode == 346:
			(x,y)= self._Iren.GetEventPosition()
			#self._Iren.SetEventInformation(x, y, ctrl, shift, key, 0, keysym)
			movecenter = True
			ren = self._Iren.GetRenderWindow().GetRenderers()
			ren = ren.GetFirstRenderer()
			self.picker.Pick(x,y,0,ren)


	def OnKeyUp(self,event):
		event.Skip()
		global mdown

		ctrl, shift = event.ControlDown(), event.ShiftDown()

		if mdown:
			mdown = 0
			self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),	ctrl, shift, chr(0), 0, None)
			(x,y)= self._Iren.GetEventPosition()
			ren = self._Iren.GetRenderWindow().GetRenderers()
			ren = ren.GetFirstRenderer()
			#print self._Iren.GetEventPosition()
			picktype = 2
			self.picker.Pick(x,y,0,ren)
		mdown = 0

		ctrl, shift = event.ControlDown(), event.ShiftDown()
		keycode, keysym = event.GetKeyCode(), None

		if keycode == 340:
			self._Iren.MiddleButtonReleaseEvent()
		elif keycode == 341:
			self._Iren.RightButtonReleaseEvent()
		elif keycode == 342:
			self._Iren.LeftButtonReleaseEvent()


		key = chr(0)
		if keycode < 256:
			key = chr(keycode)

		self._Iren.SetEventInformationFlipY(event.GetX(), event.GetY(),
											ctrl, shift, key, 0,
											keysym)
		self._Iren.KeyReleaseEvent()


	def GetRenderWindow(self):
		return self._Iren.GetRenderWindow()

	def Render(self):
		RenderAllowed = 1

		if not self.__RenderWhenDisabled:
			topParent = wx.GetTopLevelParent(self)
			if topParent:
				RenderAllowed = topParent.IsEnabled()

		if RenderAllowed:
			if self.__handle and self.__handle == self.GetHandle():
				self._Iren.GetRenderWindow().Render()

			elif self.GetHandle() and self.__has_painted:
				self._Iren.GetRenderWindow().SetNextWindowInfo(
					str(self.GetHandle()))
				d = self.GetDisplayId()
				if d:
					self._Iren.GetRenderWindow().SetDisplayId(d)

				# do the actual remap with the new parent information
				self._Iren.GetRenderWindow().WindowRemap()

				# store the new situation
				self.__handle = self.GetHandle()
				self._Iren.GetRenderWindow().Render()

	def SetRenderWhenDisabled(self, newValue):
		self.__RenderWhenDisabled = bool(newValue)

def rectangle(p0,p1,p2,p3,renderer,c0,c1,c2,light):
	tpoints = vtk.vtkPoints()

	tpoints.InsertNextPoint(p0)
	tpoints.InsertNextPoint(p1)
	tpoints.InsertNextPoint(p2)
	tpoints.InsertNextPoint(p3)

	quads = vtk.vtkCellArray()

	quad = vtk.vtkTetra()
	quad.GetPointIds().SetId(0,0)
	quad.GetPointIds().SetId(1,1)
	quad.GetPointIds().SetId(2,2)
	quad.GetPointIds().SetId(3,3)
	quads.InsertNextCell(quad)
	quadPolyData = vtk.vtkPolyData()
	quadPolyData.SetPoints( tpoints )
	quadPolyData.SetPolys( quads )
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInput(quadPolyData)
	actor = vtk.vtkActor()
	actor.GetProperty().SetColor(c0, c1, c2)
	actor.GetProperty().SetLighting(light)
	actor.SetMapper(mapper)
	renderer.AddActor(actor)

def consnum2actor(cactor,consnum,x,y,z,bsize):
	ax = vtk.vtkArrowSource()
	rx = vtk.vtkDiskSource()

	rx.SetInnerRadius(0.115*bsize)
	rx.SetOuterRadius(0.125*bsize)
	rx.SetRadialResolution(1)
	rx.SetCircumferentialResolution(12)

	ascale = 0.25*bsize

	s = vtk.vtkSphereSource()
	s.SetCenter(x,y,z)
	s.SetRadius(0.005*bsize)

	sMapper = vtk.vtkPolyDataMapper()
	sMapper.SetInput(s.GetOutput())
	sActor = vtk.vtkActor()
	sActor.GetProperty().SetColor(1,0,1)
	sActor.SetMapper(sMapper)
	cactor.append(sActor)

	if "1" in consnum:
		tdx = vtk.vtkTransform()
		tdx.Scale(ascale,ascale,ascale)
		tdx.Translate(x/ascale,y/ascale,z/ascale)
		#tdx.RotateY(270)

		axt = vtk.vtkTransformPolyDataFilter()
		axt.SetInputConnection(ax.GetOutputPort())
		axt.SetTransform(tdx)

		sMapper = vtk.vtkPolyDataMapper()
		sMapper.SetInput(axt.GetOutput())
		sActor = vtk.vtkActor()
		sActor.GetProperty().SetColor(1,0,1)
		sActor.SetMapper(sMapper)
		#ren.AddActor(sActor)
		cactor.append(sActor)
	if "4" in consnum:
		trx = vtk.vtkTransform()
		trx.Translate(x,y,z)
		trx.RotateY(90)
		axr = vtk.vtkTransformPolyDataFilter()
		axr.SetInputConnection(rx.GetOutputPort())
		axr.SetTransform(trx)
		sMapper = vtk.vtkPolyDataMapper()
		sMapper.SetInput(axr.GetOutput())
		sActor = vtk.vtkActor()
		sActor.GetProperty().SetColor(1,0,1)
		sActor.SetMapper(sMapper)
		#ren.AddActor(sActor)
		cactor.append(sActor)
	if "2" in consnum:
		tdy = vtk.vtkTransform()
		tdy.Scale(ascale,ascale,ascale)
		tdy.Translate(x/ascale,y/ascale,z/ascale)
		tdy.RotateZ(90)

		ayt = vtk.vtkTransformPolyDataFilter()
		ayt.SetInputConnection(ax.GetOutputPort())
		ayt.SetTransform(tdy)

		sMapper = vtk.vtkPolyDataMapper()
		sMapper.SetInput(ayt.GetOutput())
		sActor = vtk.vtkActor()
		sActor.GetProperty().SetColor(1,0,1)
		sActor.SetMapper(sMapper)
		#ren.AddActor(sActor)
		cactor.append(sActor)
	if "5" in consnum:
		tryy = vtk.vtkTransform()
		tryy.Translate(x,y,z)
		tryy.RotateX(90)
		ayr = vtk.vtkTransformPolyDataFilter()
		ayr.SetInputConnection(rx.GetOutputPort())
		ayr.SetTransform(tryy)
		sMapper = vtk.vtkPolyDataMapper()
		sMapper.SetInput(ayr.GetOutput())
		sActor = vtk.vtkActor()
		sActor.GetProperty().SetColor(1,0,1)
		sActor.SetMapper(sMapper)
		#ren.AddActor(sActor)
		cactor.append(sActor)
	if "3" in consnum:
		tdz = vtk.vtkTransform()
		tdz.Scale(ascale,ascale,ascale)
		tdz.Translate(x/ascale,y/ascale,z/ascale)
		tdz.RotateY(270)

		azt = vtk.vtkTransformPolyDataFilter()
		azt.SetInputConnection(ax.GetOutputPort())
		azt.SetTransform(tdz)

		sMapper = vtk.vtkPolyDataMapper()
		sMapper.SetInput(azt.GetOutput())
		sActor = vtk.vtkActor()
		sActor.GetProperty().SetColor(1,0,1)
		sActor.SetMapper(sMapper)
		#ren.AddActor(sActor)
		cactor.append(sActor)
	if "6" in consnum:
		trz = vtk.vtkTransform()
		trz.Translate(x,y,z)
		trz.RotateZ(90)
		azr = vtk.vtkTransformPolyDataFilter()
		azr.SetInputConnection(rx.GetOutputPort())
		azr.SetTransform(trz)
		sMapper = vtk.vtkPolyDataMapper()
		sMapper.SetInput(azr.GetOutput())
		sActor = vtk.vtkActor()
		sActor.GetProperty().SetColor(1,0,1)
		sActor.SetMapper(sMapper)
		#ren.AddActor(sActor)
		cactor.append(sActor)

def cons2actor(cactor,x,y,z,bsize):
	s = vtk.vtkSphereSource()
	s.SetCenter(x,y,z)
	s.SetRadius(bsize*0.02)

	sMapper = vtk.vtkPolyDataMapper()
	sMapper.SetInput(s.GetOutput())
	sActor = vtk.vtkActor()
	sActor.GetProperty().SetColor(1,0,1)
	#sActor.GetProperty().SetLighting(0)
	sActor.SetMapper(sMapper)
	#ren.AddActor(sActor)
	cactor.append(sActor)

def conm2actor(cactor,x,y,z,masa,bsize):
	propT = vtk.vtkTextProperty()
	propT.ItalicOff()
	propT.BoldOff()
	propT.SetColor(builtins.actor2dcol)

	s = vtk.vtkSphereSource()
	s.SetCenter(x,y,z)
	s.SetRadius(bsize*0.02)

	sMapper = vtk.vtkPolyDataMapper()
	sMapper.SetInput(s.GetOutput())
	sActor = vtk.vtkActor()
	sActor.GetProperty().SetColor(1,0,1)
	sActor.SetMapper(sMapper)
	#ren.AddActor(sActor)
	cactor[0].append(sActor)

	mlab = vtk.vtkCaptionActor2D()
	mlab.SetCaption("%.1f kg,"%(masa))
	mlab.LeaderOn()
	mlab.ThreeDimensionalLeaderOff()
	mlab.SetPosition(40,40)
	mlab.SetHeight(0.03)
	mlab.SetWidth(0.15)
	mlab.BorderOn()
	mlab.SetCaptionTextProperty(propT)
	mlab.SetAttachmentPoint(x,y,z)
	mlab.GetProperty().SetColor(1,0,1)
	cactor[1].append(mlab)

def forc2actors(cactor,i,bsize):
	#2540
	propT = vtk.vtkTextProperty()
	propT.ItalicOff()
	propT.BoldOff()
	propT.SetColor(builtins.actor2dcol)

	fps = vtk.vtkPoints()
	fgrid = vtk.vtkUnstructuredGrid()
	fgrid.Allocate(1, 1)

	fdata = vtk.vtkFloatArray()
	fgrid.GetPointData().AddArray(fdata)
	fdata.SetNumberOfComponents(3)
	fdata.SetNumberOfValues(len(i))
	fdata.SetName("forces")

	a = vtk.vtkArrowSource()
	a.SetTipResolution(24)

	for nj,j in enumerate(i):
		#print j
		fps.InsertPoint(nj,j[0],j[1],j[2])
		fgrid.SetPoints(fps)

		fdata.InsertTuple3(nj,j[3],j[4],j[5])

		flab = vtk.vtkCaptionActor2D()
		flab.SetCaption("%.1f N\nX %.2f\nY %.2f\nZ %.2f"%(j[6]/1000.0,j[3],j[4],j[5]))
		flab.LeaderOn()
		flab.ThreeDimensionalLeaderOff()
		flab.SetPosition(40,40)
		flab.SetHeight(0.12)
		flab.BorderOn()
		flab.SetCaptionTextProperty(propT)
		flab.SetAttachmentPoint(j[0],j[1],j[2])
		flab.GetProperty().SetColor(1,0,1)
		cactor[1].append(flab)

	fgrid.GetPointData().SetActiveVectors("forces")

	fglyph = vtk.vtkGlyph3D()
	fglyph.ScalingOn()
	#fglyph.SetScaleModeToScaleByVector()
	fglyph.SetVectorModeToUseVector()
	fglyph.SetScaleFactor(bsize*0.2)
	fglyph.SetInput(fgrid)
	fglyph.SetSource(a.GetOutput())

	appendData = vtk.vtkAppendPolyData()
	#appendData.AddInput(mglyph.GetOutput())
	appendData.AddInput(fglyph.GetOutput())

	aMapper = vtk.vtkPolyDataMapper()
	aMapper.SetInput(appendData.GetOutput())
	aActor = vtk.vtkActor()
	aActor.GetProperty().SetColor(1,0,1)
	aActor.SetMapper(aMapper)
	#ren.AddActor(aActor)

	cactor[0].append(aActor)

def moms2actors(cactor,i,bsize):
	propT = vtk.vtkTextProperty()
	propT.ItalicOff()
	propT.BoldOff()
	propT.SetColor(builtins.actor2dcol)

	mps = vtk.vtkPoints()
	mgrid = vtk.vtkUnstructuredGrid()
	mgrid.Allocate(1, 1)

	mdata = vtk.vtkFloatArray()
	mgrid.GetPointData().AddArray(mdata)
	mdata.SetNumberOfComponents(3)
	mdata.SetNumberOfValues(len(i))
	mdata.SetName("moments")

	a0 = vtk.vtkArrowSource()
	a0.SetTipResolution(24)

	transform0 = vtk.vtkTransform()
	bsc = 0.5
	bsc = bsize*0.0002
	#transform0.Scale(0.5,1.5,1.5)
	transform0.Scale(bsc,bsc*3,bsc*3)

	transform1 = vtk.vtkTransform()
	transform1.Scale(bsc,bsc,bsc)
	transform1.Translate(0,1,-0.5)
	transform1.RotateY(270)

	transform2 = vtk.vtkTransform()
	transform2.Scale(bsc,bsc,bsc)
	transform2.Translate(0,-1,0.5)
	transform2.RotateY(90)

	transform3 = vtk.vtkTransform()
	transform3.Scale(bsc,bsc,bsc)
	transform3.Translate(0,0.5,1)
	transform3.RotateZ(270)

	transform4 = vtk.vtkTransform()
	transform4.Scale(bsc,bsc,bsc)
	transform4.Translate(0,-0.5,-1)
	transform4.RotateZ(90)

	a0t = vtk.vtkTransformPolyDataFilter()
	a0t.SetInputConnection(a0.GetOutputPort())
	a0t.SetTransform(transform0)
	a1t = vtk.vtkTransformPolyDataFilter()
	a1t.SetInputConnection(a0.GetOutputPort())
	a1t.SetTransform(transform1)
	a2t = vtk.vtkTransformPolyDataFilter()
	a2t.SetInputConnection(a0.GetOutputPort())
	a2t.SetTransform(transform2)
	a3t = vtk.vtkTransformPolyDataFilter()
	a3t.SetInputConnection(a0.GetOutputPort())
	a3t.SetTransform(transform3)
	a4t = vtk.vtkTransformPolyDataFilter()
	a4t.SetInputConnection(a0.GetOutputPort())
	a4t.SetTransform(transform4)

	for nj,j in enumerate(i):
		#print "MOMENT", j
		mps.InsertPoint(nj,j[0],j[1],j[2])
		mgrid.SetPoints(mps)

		#mdata.InsertTuple3(nj,j[3],j[4],j[5])
		x = 0.8
		y = 0.8
		z = 0.8

		mdata.InsertTuple3(nj,j[3],j[4],j[5])
		#mdata.InsertTuple3(nj,-z,-x,y)
		#mdata.InsertTuple3(nj,x,y,z)

		mlab = vtk.vtkCaptionActor2D()
		mlab.SetCaption("%.1f Nm\nX %.2f\nY %.2f\nZ %.2f"%(j[6]/1000000.0,j[3],j[4],j[5]))
		mlab.LeaderOn()
		mlab.SetPosition(40,40)
		mlab.SetHeight(0.12)
		mlab.BorderOn()
		mlab.ThreeDimensionalLeaderOff()
		mlab.SetCaptionTextProperty(propT)
		mlab.SetAttachmentPoint(j[0],j[1],j[2])
		mlab.GetProperty().SetColor(1,0,1)
		cactor[1].append(mlab)

	mgrid.GetPointData().SetActiveVectors("moments")

	appendData0 = vtk.vtkAppendPolyData()
	appendData0.AddInput(a0t.GetOutput())
	appendData0.AddInput(a1t.GetOutput())
	appendData0.AddInput(a2t.GetOutput())
	appendData0.AddInput(a3t.GetOutput())
	appendData0.AddInput(a4t.GetOutput())

	mglyph = vtk.vtkGlyph3D()
	mglyph.ScalingOn()
	mglyph.SetVectorModeToUseVector()
	mglyph.SetScaleFactor(500)
	mglyph.SetInput(mgrid)
	#mglyph.SetSource(a0.GetOutput())
	mglyph.SetSource(appendData0.GetOutput())

	appendData = vtk.vtkAppendPolyData()
	#appendData.AddInput(mglyph.GetOutput())
	appendData.AddInput(mglyph.GetOutput())

	aMapper = vtk.vtkPolyDataMapper()
	aMapper.SetInput(appendData.GetOutput())
	aActor = vtk.vtkActor()
	aActor.GetProperty().SetColor(1,0,1)
	aActor.SetMapper(aMapper)
	#ren.AddActor(aActor)

	cactor[0].append(aActor)

def gravs2actors(cactor,i,myActor,bsize):
	propT = vtk.vtkTextProperty()
	propT.ItalicOff()
	propT.BoldOff()
	propT.SetColor(builtins.actor2dcol)

	gps = vtk.vtkPoints()
	ggrid = vtk.vtkUnstructuredGrid()
	ggrid.Allocate(1, 1)

	gdata = vtk.vtkFloatArray()
	ggrid.GetPointData().AddArray(gdata)
	gdata.SetNumberOfComponents(3)
	gdata.SetNumberOfValues(len(i))
	gdata.SetName("gravs")

	a = vtk.vtkArrowSource()

	cabs = myActor.GetBounds()

	cx = (cabs[0]+cabs[1])/2.0
	cy = (cabs[2]+cabs[3])/2.0
	cz = (cabs[4]+cabs[5])/2.0

	#print "\nCABS"
	#print cabs
	#print cx, cy,cz
	#print

	gx = 0
	gy = 0
	gz = 0

	for nj,j in enumerate(i):
		gx += j[0]*j[3]/9806.6
		gy += j[1]*j[3]/9806.6
		gz += j[2]*j[3]/9806.6

	if gx == 0 and gy ==0 and gz == 0:
		return

	gps.InsertPoint(0,cx,cy,cz)
	ggrid.SetPoints(gps)

	gdata.InsertTuple3(0,gx,gy,gz)
	wg = math.sqrt(math.pow(gx,2)+math.pow(gy,2)+math.pow(gz,2))

	#print "wg", wg

	glab = vtk.vtkCaptionActor2D()
	#glab.SetCaption("%.1f m/s^2\nX %.2f\nY %.2f\nZ %.2f"%(j[3]/1000.0,j[0],j[1],j[2]))
	glab.SetCaption("%.2f G\nX %.2f\nY %.2f\nZ %.2f"%(wg,gx,gy,gz))
	glab.LeaderOn()
	glab.SetPosition(40,40)
	glab.SetHeight(0.12)
	glab.BorderOn()
	glab.ThreeDimensionalLeaderOff()
	glab.SetCaptionTextProperty(propT)
	glab.SetAttachmentPoint(cx,cy,cz)
	glab.GetProperty().SetColor(1,0,1)
	cactor[1].append(glab)

	ggrid.GetPointData().SetActiveVectors("gravs")

	gglyph = vtk.vtkGlyph3D()
	gglyph.ScalingOn()
	gglyph.SetVectorModeToUseVector()
	gglyph.SetScaleFactor(bsize*0.25)
	gglyph.SetInput(ggrid)
	gglyph.SetSource(a.GetOutput())

	appendData = vtk.vtkAppendPolyData()
	appendData.AddInput(gglyph.GetOutput())

	aMapper = vtk.vtkPolyDataMapper()
	aMapper.SetInput(appendData.GetOutput())
	aActor = vtk.vtkActor()
	aActor.GetProperty().SetColor(1,0,1)
	aActor.SetMapper(aMapper)
	#ren.AddActor(aActor)

	cactor[0].append(aActor)

def reac2actors2(cactor,i,bsize):
	#2540
	srumx = 0
	srumy = 0
	srumz = 0
	propT = vtk.vtkTextProperty()
	propT.ItalicOff()
	propT.BoldOff()
	propT.SetColor(builtins.actor2dcol)

	rps = vtk.vtkPoints()
	rgrid = vtk.vtkUnstructuredGrid()
	rgrid.Allocate(1, 1)

	rdata = vtk.vtkFloatArray()
	rgrid.GetPointData().AddArray(rdata)
	rdata.SetNumberOfComponents(3)
	rdata.SetNumberOfValues(len(i))
	rdata.SetName("reacs")

	a = vtk.vtkConeSource()
	a.SetCenter(-0.5,0,0)
	a.SetResolution(24)

	for nj,j in enumerate(i):
		#print j
		rps.InsertPoint(nj,j[0],j[1],j[2])
		rgrid.SetPoints(rps)

		rdata.InsertTuple3(nj,j[3],j[4],j[5])

		rlab = vtk.vtkCaptionActor2D()
		rlab.SetCaption("%.2f N\nX %.2f\nY %.2f\nZ %.2f"%(plen([0,0,0],[j[3],j[4],j[5]]),j[3],j[4],j[5]))
		srumx = srumx + j[3]
		srumy = srumy + j[4]
		srumz = srumz + j[5]
		rlab.LeaderOn()
		rlab.ThreeDimensionalLeaderOff()
		rlab.SetPosition(40,40)
		rlab.SetHeight(0.12)
		rlab.BorderOn()
		rlab.SetCaptionTextProperty(propT)
		rlab.SetAttachmentPoint(j[0],j[1],j[2])
		rlab.GetProperty().SetColor(1,0,1)
		cactor[1].append(rlab)
	rgrid.GetPointData().SetActiveVectors("reacs")

	rglyph = vtk.vtkGlyph3D()
	rglyph.ScalingOn()
	#fglyph.SetScaleModeToScaleByVector()
	rglyph.SetVectorModeToUseVector()
	rglyph.SetScaleFactor(bsize*0.08)
	rglyph.SetInput(rgrid)
	rglyph.SetSource(a.GetOutput())

	appendData = vtk.vtkAppendPolyData()
	#appendData.AddInput(mglyph.GetOutput())
	appendData.AddInput(rglyph.GetOutput())

	aMapper = vtk.vtkPolyDataMapper()
	aMapper.SetInput(appendData.GetOutput())
	aActor = vtk.vtkActor()
	aActor.GetProperty().SetColor(1,0,1)
	aActor.SetMapper(aMapper)
	#ren.AddActor(aActor)

	cactor[0].append(aActor)
	#print "suma", srumx,srumy,srumz
	return [srumx,srumy,srumz]

def addmeasure(pickstart,pickdxyz,mpoint,ren,sdxyz):

	propT = vtk.vtkTextProperty()
	propT.ItalicOff()
	propT.BoldOff()
	propT.SetColor(builtins.actor2dcol)

	s = vtk.vtkLineSource()
	s.SetPoint1(pickstart)
	s.SetPoint2(mpoint)

	sMapper = vtk.vtkPolyDataMapper()
	sMapper.SetInput(s.GetOutput())
	sActor = vtk.vtkActor()
	sActor.GetProperty().SetColor(1,0,1)
	sActor.SetMapper(sMapper)

	builtins.actors.append(sActor)
	ren.AddActor(sActor)

	mdis = plen(pickstart,mpoint)
	mdis2 = plen([pickstart[0]+pickdxyz[0],pickstart[1]+pickdxyz[1],pickstart[2]+pickdxyz[2]],[mpoint[0]+sdxyz[0],mpoint[1]+sdxyz[1],mpoint[2]+sdxyz[2]])
	print(mdis, mdis2)

	mlab = vtk.vtkCaptionActor2D()
	if (mdis2-mdis) >= 0:
		mlab.SetCaption("%.1f mm + %.2f mm"%(mdis,(mdis2-mdis)))
	else:
		mlab.SetCaption("%.1f mm - %.2f mm"%(mdis,abs(mdis2-mdis)))

	builtins.statusbar.SetStatusText('Pomiar: odległość = %.2f dX = %.2f dY = %.2f dZ = %.2f '%(mdis,mpoint[0]-pickstart[0],mpoint[1]-pickstart[1],mpoint[2]-pickstart[2]))

	mlab.LeaderOn()
	mlab.ThreeDimensionalLeaderOff()
	mlab.SetPosition(40,40)
	mlab.SetHeight(0.03)
	mlab.SetWidth(0.15)
	mlab.BorderOn()
	mlab.SetCaptionTextProperty(propT)
	mlab.SetAttachmentPoint((pickstart[0]+mpoint[0])/2,(pickstart[1]+mpoint[1])/2,(pickstart[2]+mpoint[2])/2)
	mlab.GetProperty().SetColor(1,0,1)
	builtins.actors.append(mlab)
	ren.AddActor(mlab)

def bfor2actors(cactor,i,bsize):
	propT = vtk.vtkTextProperty()
	propT.ItalicOff()
	propT.BoldOff()
	propT.SetColor(builtins.actor2dcol)

	for nj,j in enumerate(i):
		#print j
		flab = vtk.vtkCaptionActor2D()
		if j[5] != None:
			flab.SetCaption("Axial %.2fN\nTransverse %.2fN\nfi %.1fmm"%(j[3],j[4],j[5]))
		else:
			flab.SetCaption("Axial %.2fN\nTransverse %.2fN"%(j[3],j[4]))
		flab.LeaderOn()
		flab.SetPosition(40,40)
		flab.SetHeight(0.06)
		flab.BorderOn()
		flab.ThreeDimensionalLeaderOff()
		flab.SetCaptionTextProperty(propT)
		flab.SetAttachmentPoint(j[0],j[1],j[2])
		flab.GetProperty().SetColor(1,0,1)
		cactor.append(flab)

def dist(x,y,z,x1,y1,z1):
	return math.sqrt(math.pow((x1-x),2)+math.pow((y1-y),2)+math.pow((z1-z),2))

def dirv(xxx_todo_changeme, xxx_todo_changeme1):
	(x,y,z) = xxx_todo_changeme
	(x1,y1,z1) = xxx_todo_changeme1
	distance = dist(x,y,z,x1,y1,z1)
	dirx = (float(x)-float(x1))/distance
	diry = (float(y)-float(y1))/distance
	dirz = (float(z)-float(z1))/distance
	return [dirx, diry, dirz]

def provect(vect1, vect2):
	a = array(vect1)
	b = array(vect2)
	#print np.dot(b,a)
	#print (np.dot(b,a))*b
	return (dot(b,a))

def magn(xyz):
	#math.sqrt( math.pow(xyz[0],2) + math.pow(xyz[1],2) + math.pow(xyz[2],2) )
	xyz = array(xyz)
	return sqrt(dot(xyz, xyz))

def proplan(vect1, vect2):
	a = array(vect1)
	b = array(vect2)
	#print np.dot(b,a)
	#print (np.dot(b,a))*b
	return a - (dot(a,b)*b)
