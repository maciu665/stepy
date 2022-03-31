# -*- coding: utf-8 -*-
#!/usr/bin/python
#TODO
#tworzenie nowego vml
#załączone pliki?
# powrót do rozmiaru po screenshocie
#
#IMPORTY
import wx
import vtk
import builtins
import os
import sys
# from vtk.util.colors import *
import gzip, zipfile
from vtkfun import *
import wx.lib.agw.customtreectrl as CT
from xml.dom.minidom import *
import shutil
import time
import vtkmodules
import vtkmodules.all
from step_fun import *

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCC.Core.TopoDS import topods_Face,TopoDS_Iterator,TopoDS_ListOfShape
from OCC.Core.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa
# from OCC.Core import BRepAdaptor
# print(dir(BRepAdaptor))
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Pnt, BRep_Tool_IsGeometric, BRep_Tool_Parameter, BRep_Tool_Curve
# sys.exit()
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCC.Core.TopoDS import topods_Vertex
from OCC.Display.SimpleGui import init_display
#from OCC.Display.wxDisplay import wxBaseViewer
from mywxDisplay import wxBaseViewer,wxViewer3d
#from OCC.Core.BRepool import Curve

from OCC.Extend.TopologyUtils import TopologyExplorer

from OCCUtils.edge import Edge

from OCC.Core.BRep import BRep_Builder, BRep_Tool
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh

from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import TopoDS_Compound, topods_Face
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopLoc import TopLoc_Location

softname = "STEPY AKERMAŃSKIE PRO"

builtins.actors = []

actors = []

shtypes =["COMPOUND","COMPSOLID","SOLID","SHELL","FACE","WIRE","EDGE","VERTEX"]

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

displayvtk = vtkwin(root, -1, actors)
displayvtk.Enable(1)
#displayvtk.AddObserver("ExitEvent", lambda o,e,f=root: f.Close())
ren = vtk.vtkRenderer()
displayvtk.GetRenderWindow().AddRenderer(ren)

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
mbox.Add(displayvtk,(0,2),(1,1),wx.EXPAND,4 )
#mbox.Add(rpanel,(0,3),(1,1),wx.EXPAND,4 )

#rpanel.Show(False)

mbox.AddGrowableRow(0)
#rbox.AddGrowableRow(1)
mbox.AddGrowableCol(1)
#mbox.AddGrowableCol(2)
sbox.AddGrowableCol(0)

root.SetSizerAndFit(mbox)
root.Maximize(True)
root.Refresh()

def elen(edg):
    curve_adapt = BRepAdaptor_Curve(edg)
    length = GCPnts_AbscissaPoint().Length(curve_adapt, curve_adapt.FirstParameter(), curve_adapt.LastParameter(), 1e-6)
    return length

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
                print("ELEN",elen(ttshp))
                curv = BRepAdaptor_Curve(ttshp).Curve()
                print(dir(curv))
                print(curv)
                # print(curv.Circle())
                a = 0.0
                b = 0.0
                [curve_handle, a, b] = BRep_Tool.Curve(ttshp)
                print(dir(curve_handle))
                # print(curve_handle.D0)
                ctypename = curve_handle.DynamicType().Name().replace("Geom_","")
                print(ctypename)
                nedge = ntree.AppendItem(selsurf, ctypename)
                telen = ntree.AppendItem(nedge, "Len=%.2f"%elen(ttshp))
                # print(curv.GetType())
                #print(dir(curv))
                twi.Next()
            #print(dir(tshp))
            #print(tshp)
            print(tshp.ShapeType())
            tdi.Next()
        ntree.ExpandAll()

# first loads the STEP file and display
# shp = read_step_file("E:/GIT/DOKTORAT/face_recognition_sample_part.stp")
# def getstep(e):

def getstep(e):
    if (e):
        dlg = wx.FileDialog(root, "Wskaż plik STP", "", "", "*.*", wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            ofilename = dlg.GetFilename()
            dirname = dlg.GetDirectory()
            nazwa = (os.path.join(dirname, ofilename))
            dlg.Destroy()
        else:
            sys.exit()
    else:
        nazwa = "E:/GIT/DOKTORAT/model2.stp"
        nazwa = "E:/GIT/DOKTORAT/F4150-151-002.stp"
        nazwa = "E:/GIT/DOKTORAT/F4100-001-001.stp"
        nazwa = "E:/GIT/DOKTORAT/ASSES/F4100-001-001.stp"
        nazwa = "E:/GIT/DOKTORAT/STEPY/IPE 160 - 1211.stp"
        print(os.path.exists(nazwa))

    # shp = get_step_file("E:/GIT/DOKTORAT/model2.stp")
    shp = get_step_file(nazwa)
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
    display.EraseAll()
    allpoints = []
    sedges = []

    print("NBCHILDREN",shp.NbChildren(),shtypes[shp.ShapeType()])
    tsldi = TopoDS_Iterator(shp)
    tsldi.Initialize(shp)
    while tsldi.More():
        print("SHELL")
        tshp = tsldi.Value()
        print(tshp.NbChildren())
        print(tshp.ShapeType(),shtypes[tshp.ShapeType()])
        tshli = TopoDS_Iterator(tshp)
        tshli.Initialize(tshp)
        while tshli.More():
            print("FACE")
            ttshp = tshli.Value()
            print(ttshp.NbChildren())
            print(ttshp.ShapeType(),shtypes[ttshp.ShapeType()])
            tfaci = TopoDS_Iterator(ttshp)
            tfaci.Initialize(ttshp)
            while tfaci.More():
                tttshp = tfaci.Value()
                print(tttshp.NbChildren())
                print(tttshp.ShapeType(),shtypes[tttshp.ShapeType()])
                twiri = TopoDS_Iterator(tttshp)
                twiri.Initialize(tttshp)
                while twiri.More():
                    ttttshp = twiri.Value()
                    print(ttttshp.NbChildren())
                    print(ttttshp.ShapeType(),shtypes[ttttshp.ShapeType()])



                    curv = BRepAdaptor_Curve(ttttshp).Curve()
                    # print(dir(curv))
                    # print(curv)
                    # print(curv.Circle())
                    a = 0.0
                    b = 0.0
                    [curve_handle, a, b] = BRep_Tool.Curve(ttttshp)
                    # print(dir(curve_handle))
                    # print(curve_handle.D0)
                    ctypename = curve_handle.DynamicType().Name().replace("Geom_","")
                    print(ctypename)
                    if ctypename == "Line":
                        tveri = TopoDS_Iterator(ttttshp)
                        tveri.Initialize(ttttshp)
                        while tveri.More():
                            tttttshp = tveri.Value()
                            print(tttttshp.NbChildren())
                            print(tttttshp.ShapeType(),shtypes[tttttshp.ShapeType()])
                            # print(dir(tttttshp))

                            v = topods_Vertex(tttttshp)
                            pnt = BRep_Tool.Pnt(v)
                            print("3d gp_Pnt selected coordinates : X=", pnt.X(), "Y=", pnt.Y(), "Z=", pnt.Z())
                            tveri.Next()

                            allpoints.append([pnt.X(),pnt.Y(),pnt.Z()])


                    # nedge = ntree.AppendItem(selsurf, ctypename)
                    # telen = ntree.AppendItem(nedge, "Len=%.2f"%elen(ttshp))

                    twiri.Next()



                tfaci.Next()

            tshli.Next()

        tsldi.Next()

    print(len(allpoints))

    BRepMesh_IncrementalMesh(shp, 0.25)
    builder = BRep_Builder()
    comp = TopoDS_Compound()
    builder.MakeCompound(comp)

    bt = BRep_Tool()
    ex = TopExp_Explorer(shp, TopAbs_FACE)

    pts = vtk.vtkPoints()
    ugrid = vtk.vtkUnstructuredGrid()

    pts2 = vtk.vtkPoints()
    ugrid2 = vtk.vtkUnstructuredGrid()




    for k in range(int(len(allpoints)/2)):
        ti1 = pts2.InsertNextPoint(allpoints[k*2])
        ti2 = pts2.InsertNextPoint(allpoints[k*2+1])
        pointIds = vtk.vtkIdList()
        pointIds.InsertId(0, ti1)
        pointIds.InsertId(1, ti2)
        seid = ugrid2.InsertNextCell(3, pointIds)
    ugrid2.SetPoints(pts2)



    while ex.More():
        print("FEJS")
        face = topods_Face(ex.Current())
        location = TopLoc_Location()
        facing = bt.Triangulation(face, location)
        tab = facing.Nodes()
        tri = facing.Triangles()
        print(tab)
        print(dir(tab))

        # for i in range(facing.NbNodes()):
            # print("pt",tab.Value(i))
            # pts.InsertPoint(i,tab.Value(i))


        for i in range(1, facing.NbTriangles() + 1):
            trian = tri.Value(i)
            index1, index2, index3 = trian.Get()
            # print("pt",tab.Value(index1))
            # print("pt",tab.Value(index1).Coord()[0])
            # print(dir(tab.Value(index1)))
            '''
            pts.InsertPoint(index1,tab.Value(index1).Coord()[0],tab.Value(index1).Coord()[1],tab.Value(index1).Coord()[2])
            pts.InsertPoint(index2,tab.Value(index2).Coord()[0],tab.Value(index2).Coord()[1],tab.Value(index2).Coord()[2])
            pts.InsertPoint(index3,tab.Value(index3).Coord()[0],tab.Value(index3).Coord()[1],tab.Value(index3).Coord()[2])
            '''
            ti1 = pts.InsertNextPoint(tab.Value(index1).Coord()[0],tab.Value(index1).Coord()[1],tab.Value(index1).Coord()[2])
            ti2 = pts.InsertNextPoint(tab.Value(index2).Coord()[0],tab.Value(index2).Coord()[1],tab.Value(index2).Coord()[2])
            ti3 = pts.InsertNextPoint(tab.Value(index3).Coord()[0],tab.Value(index3).Coord()[1],tab.Value(index3).Coord()[2])

            pointIds = vtk.vtkIdList()
            pointIds.InsertId(0, ti1)
            pointIds.InsertId(1, ti2)
            pointIds.InsertId(2, ti3)
            seid = ugrid.InsertNextCell(5, pointIds)
            '''

            for j in range(1, 4):
                if j == 1:
                    m = index1
                    n = index2
                elif j == 2:
                    n = index3
                elif j == 3:
                    m = index2
                me = BRepBuilderAPI_MakeEdge(tab.Value(m), tab.Value(n))

                if me.IsDone():
                    builder.Add(comp, me.Edge())
            '''
        ex.Next()

    # print(pts)
    ugrid.SetPoints(pts)
    # print(ugrid)

    gf = vtk.vtkGeometryFilter()
    gf.SetInputData(ugrid)
    gf.Update()

    print("POINTS",gf.GetOutput().GetNumberOfPoints())

    cpd = vtk.vtkCleanPolyData()
    cpd.SetInputData(gf.GetOutput())
    cpd.Update()

    print("POINTS",cpd.GetOutput().GetNumberOfPoints())

    emapper = vtk.vtkDataSetMapper()
    emapper.SetInputData(ugrid2)
    emapper.ScalarVisibilityOff()

    eactor = vtk.vtkActor()
    eactor.SetMapper( emapper )
    eprop = eactor.GetProperty()
    eprop.LightingOff()

    eprop.SetEdgeColor([1,0,1])
    eprop.SetColor([1,0,1])
    eprop.SetRepresentationToWireframe()
    eprop.SetOpacity(1)

    print(ugrid2)

    ren.RemoveAllViewProps()
    ren.AddActor(eactor)


    nmapper = vtk.vtkDataSetMapper()
    nmapper.SetInputConnection(cpd.GetOutputPort())
    # nmapper.SetScalarModeToUsePointFieldData()
    nmapper.ScalarVisibilityOff()
    nActor = vtk.vtkActor()
    nActor.SetMapper( nmapper )
    vprop = nActor.GetProperty()
    # vprop.LightingOff()
    ren.AddActor(nActor)

    ren.ResetCamera()
    displayvtk.Render()
    print("POINTS",ugrid.GetNumberOfPoints())





    display.DisplayShape(shp, update=True)
    display.DisplayShape(comp, update=True)
    display.FitAll()
    display.SetSelectionModeFace()
    # display.SetSelectionModeShape()
    display.register_select_callback(get_face)
    display.FitAll()

root.Bind(wx.EVT_MENU, getstep, id=3001)
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
root.Bind(wx.EVT_CLOSE, onexit)
root.Bind(wx.EVT_MENU, saveimage, id=3101)
root.Bind(wx.EVT_MENU, showmax, id=3202)
root.Bind(wx.EVT_MENU, fullon, id=3301)
for i in range(3310,3312):
	root.Bind(wx.EVT_MENU, anaglyph, id=i)
root.Bind(wx.EVT_MENU, showcax, id=3302)
'''

getstep(0)
#displayvtk.widget.SetEnabled(1)
#displayvtk.widget.InteractiveOff()

#ren.GetActiveCamera().SetParallelProjection(True)
root.Show()

aplikacja.MainLoop()

'''
COMPOUND: A group of any of the shapes below.
COMPSOLID: A set of solids connected by their faces. This expands the notions of WIRE and SHELL to solids.
SOLID: A part of 3D space bounded by shells.
SHELL: A set of faces connected by some of the edges of their wire boundaries. A shell can be open or closed.
FACE: Part of a plane (in 2D geometry) or a surface (in 3D geometry) bounded by a closed wire. Its geometry is constrained (trimmed) by contours.
WIRE: A sequence of edges connected by their vertices. It can be open or closed depending on whether the edges are linked or not.
EDGE: A single dimensional shape corresponding to a curve, and bound by a vertex at each extremity.
VERTEX: A zero-dimensional shape corresponding to a point in geometry.
'''
