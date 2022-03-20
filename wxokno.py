# -*- coding: utf-8 -*-
#!/usr/bin/python
#TODO
#tworzenie nowego vml
#załączone pliki?
# powrót do rozmiaru po screenshocie
#
#IMPORTY
import wx
#import vtk
import builtins
import os
import sys
# from vtk.util.colors import *
import gzip, zipfile
#from kflow_vtkfun import *
import wx.lib.agw.customtreectrl as CT
from xml.dom.minidom import *
import shutil
import time
#import vtkmodules
#import vtkmodules.all

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCC.Core.TopoDS import topods_Face,TopoDS_Iterator
# from OCC.Core import BRepAdaptor
# print(dir(BRepAdaptor))
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Pnt, BRep_Tool_IsGeometric, BRep_Tool_Parameter, BRep_Tool_Curve
# sys.exit()
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCC.Display.SimpleGui import init_display
#from OCC.Display.wxDisplay import wxBaseViewer
from mywxDisplay import wxBaseViewer,wxViewer3d
#from OCC.Core.BRepool import Curve
from step_fun import *

from OCC.Extend.TopologyUtils import TopologyExplorer

softname = "STEPY"

builtins.actors = []
builtins.parallel = True
builtins.vmisarray = None
builtins.disparray = None
builtins.actor2dcol = [1,1,1]
builtins.helpActor = None
builtins.helpOn = False

actors = []

#APLIKACJA
aplikacja=wx.App(False)

################################################################################################################

root=wx.Frame(None, -1, softname, wx.Point(0,0), wx.Size(1100, 1000))
# root.SetIcon(wx.Icon('kon.ico', wx.BITMAP_TYPE_ICO))
root.Centre()
#builtins.statusbar = root.CreateStatusBar()
#builtins.statusbar.SetStatusText('')

menubar = wx.MenuBar()
menuplik = wx.Menu()
#
menubar.Append(menuplik, '&Plik')
##
mopenvtk = wx.MenuItem(menuplik,3001, '&Otwórz .stp\tCtrl+O', "Otwiera plik *.stp")
menuplik.Append(mopenvtk)

menuplik.AppendSeparator()
pquit = wx.MenuItem(menuplik, 3003, '&Zakończ\tCtrl+Q', "Zakończ")
#pquit.SetBitmap(wx.Image('../gf/exit_16.png',wx.BITMAP_TYPE_PNG).ConvertToBitmap())
menuplik.Append(pquit)
#
menuview = wx.Menu()
menubar.Append(menuview, "&Widok")
root.SetMenuBar(menubar)

################################################################################################################

mbox = wx.GridBagSizer(5,0)
sbox = wx.GridBagSizer(5,5)
#rbox = wx.GridBagSizer(0,0)

stepwin = wxViewer3d(root)
print(stepwin)
print(dir(stepwin))
stepwin.InitDriver()
display = stepwin._display
print(display)
# sys.exit()

#displayvtk = vtkwin(root, -1, actors)
#displayvtk.Enable(1)
#displayvtk.AddObserver("ExitEvent", lambda o,e,f=root: f.Close())
#ren = vtk.vtkRenderer()
#displayvtk.GetRenderWindow().AddRenderer(ren)

ntree = CT.CustomTreeCtrl(root, 665, size=(300,700), style=wx.SUNKEN_BORDER, agwStyle=CT.TR_HAS_BUTTONS | CT.TR_HAS_VARIABLE_ROW_HEIGHT)

#rpanel = wx.Panel(root,size=(50,100))

details = wx.TextCtrl(root, -1, "", size=(200, 150), style = wx.TE_MULTILINE)
details.SetEditable(False)
details.SetToolTip(wx.ToolTip("Szczegóły"))

sbox.Add(ntree,(0,0),(1,2),wx.EXPAND,4 )
sbox.Add(details,(1,0),(1,2),wx.EXPAND,4 )
sbox.AddGrowableRow(0)

mbox.Add(sbox,(0,0),(1,1),wx.EXPAND,4 )
mbox.Add(stepwin,(0,1),(1,1),wx.EXPAND,4 )
#mbox.Add(displayvtk,(0,2),(1,1),wx.EXPAND,4 )
#mbox.Add(rpanel,(0,3),(1,1),wx.EXPAND,4 )

#rpanel.Show(False)

mbox.AddGrowableRow(0)
#rbox.AddGrowableRow(1)
mbox.AddGrowableCol(1)
sbox.AddGrowableCol(0)

root.SetSizerAndFit(mbox)
root.Maximize(True)
root.Refresh()

def get_step_file(filename):
    """read the STEP file and returns a compound"""
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(filename)

    if status == IFSelect_RetDone:  # check status
        failsonly = False
        step_reader.PrintCheckLoad(failsonly, IFSelect_ItemsByEntity)
        step_reader.PrintCheckTransfer(failsonly, IFSelect_ItemsByEntity)
        step_reader.TransferRoot(1)
        a_shape = step_reader.Shape(1)
    else:
        print("Error: can't read file.")
        sys.exit(0)
    return a_shape


def recognize_face(a_face):
    surf = BRepAdaptor_Surface(a_face, True)
    surf_type = surf.GetType()
    if surf_type == GeomAbs_Plane:
        gp_pln = surf.Plane()
        location = gp_pln.Location()  # a point of the plane
        normal = gp_pln.Axis().Direction()  # the plane normal
        # then export location and normal to the console output
        print(
            "--> Location (global coordinates)",
            location.X(),
            location.Y(),
            location.Z(),
        )
        print("--> Normal (global coordinates)", normal.X(), normal.Y(), normal.Z())
    elif surf_type == GeomAbs_Cylinder:
        gp_cyl = surf.Cylinder()
        location = gp_cyl.Location()
        axis = gp_cyl.Axis().Direction()
        print(
            "--> Location (global coordinates)",
            location.X(),
            location.Y(),
            location.Z(),
        )
        print("--> Axis (global coordinates)", axis.X(), axis.Y(), axis.Z())
    else:
        print("not implemented")

def get_face(shp, *kwargs):
    print("SHP",shp)
    for shape in shp:
        print(dir(shape))
        ntree.DeleteAllItems()
        print("Face selected: ", shape)
        #recognize_face()
        surf = BRepAdaptor_Surface(topods_Face(shape), True)
        # print(dir(surf))
        # sys.exit()
        stypetxt = surf_type2text(surf.GetType())
        selsurf = ntree.AddRoot(stypetxt)
        # sys.exit()
        print("NBCHILDREN",shape.NbChildren())
        tdi = TopoDS_Iterator(shape)
        tdi.Initialize(shape)
        while tdi.More():
            print("WIRE")
            tshp = tdi.Value()
            print(tshp.NbChildren())
            twi = TopoDS_Iterator(tshp)
            twi.Initialize(tshp)
            while twi.More():
                ttshp = twi.Value()
                tei = TopoDS_Iterator(ttshp)
                tei.Initialize(ttshp)
                #print(dir(ttshp))
                print("shapetype", ttshp.ShapeType())



                while tei.More():
                    tttshp = tei.Value()
                    print("TYP 2", tttshp)
#                    print(dir(tttshp))
                    tei.Next()
                #print("TYP", ttshp.ShapeType())
                print("TYP", ttshp)
                curv = BRepAdaptor_Curve(ttshp).Curve()
                print(curv)
                # print(curv.Circle())
                a = 0.0
                b = 0.0
                [curve_handle, a, b] = BRep_Tool.Curve(ttshp)
                ctypename = curve_handle.DynamicType().Name().replace("Geom_","")
                print(ctypename)
                nedge = ntree.AppendItem(selsurf, ctypename)
                # print(curv.GetType())
                #print(dir(curv))
                twi.Next()
            #print(dir(tshp))
            #print(tshp)
            print(tshp.ShapeType())
            tdi.Next()
        ntree.ExpandAll()

display.register_select_callback(get_face)
# first loads the STEP file and display
# shp = read_step_file("E:/GIT/DOKTORAT/face_recognition_sample_part.stp")
shp = get_step_file("E:/GIT/DOKTORAT/model2.stp")
#shp = read_step_file("E:/GIT/DOKTORAT/all_together.step")
print(shp)
print(dir(shp))
print(shp.NbChildren())
print(shp.ShapeType())
print(shp.TShape())
'''
tdi = TopoDS_Iterator(shp)
tdi.Initialize(shp)
while tdi.More():
    print("POZYCJA")
    tshp = tdi.Value()
    print(tshp.NbChildren())
    print(dir(tshp))
    print(tshp)
    print(tshp.ShapeType())
    tdi.Next()
'''
display.DisplayShape(shp, update=True)
#add_menu("recognition")
#add_function_to_menu("recognition", recognize_batch)
display.SetSelectionModeFace()
# display.SetSelectionModeVertex()
print(dir(display))


'''
root.Bind(wx.EVT_COMBOBOX, updatemenu, id=501)
root.Bind(wx.EVT_COMBOBOX, updatemenu, id=502)
root.Bind(wx.EVT_COMBOBOX, updatemenu, id=503)
ntree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, treesel)
ntree.Bind(wx.EVT_COMBOBOX, ntback, id=1006)
ntree.Bind(CT.EVT_TREE_ITEM_CHECKED, koza)
for i in range(2000,2100):
	ntree.Bind(wx.EVT_COMBOBOX, ntsmod, id=i)
for i in range(4000,6100):
	ntree.Bind(wx.EVT_COMBOBOX, ntsply, id=i)
ntree.Bind(wx.EVT_TREE_ITEM_COLLAPSED, treerefresh)
ntree.Bind(wx.EVT_TREE_ITEM_EXPANDED, treerefresh)
root.Bind(wx.EVT_MENU, onexit, id=3003)
root.Bind(wx.EVT_CLOSE, onexit)
root.Bind(wx.EVT_MENU, saveimage, id=3101)
root.Bind(wx.EVT_MENU, showmax, id=3202)
root.Bind(wx.EVT_MENU, fullon, id=3301)
for i in range(3310,3312):
	root.Bind(wx.EVT_MENU, anaglyph, id=i)
root.Bind(wx.EVT_MENU, showcax, id=3302)
'''

#displayvtk.widget.SetEnabled(1)
#displayvtk.widget.InteractiveOff()

#ren.GetActiveCamera().SetParallelProjection(True)
root.Show()

aplikacja.MainLoop()
