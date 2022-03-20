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
from step_fun import *

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCC.Core.TopoDS import topods_Face,TopoDS_Iterator
from OCC.Core.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa
# from OCC.Core import BRepAdaptor
# print(dir(BRepAdaptor))
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Pnt, BRep_Tool_IsGeometric, BRep_Tool_Parameter, BRep_Tool_Curve
# sys.exit()
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCC.Display.SimpleGui import init_display
#from OCC.Display.wxDisplay import wxBaseViewer
from mywxDisplay import wxBaseViewer,wxViewer3d
#from OCC.Core.BRepool import Curve

from OCC.Extend.TopologyUtils import TopologyExplorer

from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.TDocStd import TDocStd_Document
from OCC.Core.XCAFDoc import (
    XCAFDoc_DocumentTool_ShapeTool,
    XCAFDoc_DocumentTool_ColorTool,
    XCAFDoc_DocumentTool_LayerTool,
    XCAFDoc_DocumentTool_MaterialTool,
)
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TDF import TDF_LabelSequence,TDF_Label
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from OCCUtils.edge import Edge

softname = "STEPY"
global shp

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

def elen(edg):
    curve_adapt = BRepAdaptor_Curve(edg)
    length = GCPnts_AbscissaPoint().Length(curve_adapt, curve_adapt.FirstParameter(), curve_adapt.LastParameter(), 1e-6)
    return length

def get_step_file(filename):
    """read the STEP file and returns a compound"""

    _shapes = []

    doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))

    # Get root assembly
    shape_tool = XCAFDoc_DocumentTool_ShapeTool(doc.Main())
    l_colors = XCAFDoc_DocumentTool_ColorTool(doc.Main())
    l_layers = XCAFDoc_DocumentTool_LayerTool(doc.Main())
    l_materials = XCAFDoc_DocumentTool_MaterialTool(doc.Main())

    step_reader = STEPCAFControl_Reader()
    step_reader.SetColorMode(True)
    step_reader.SetLayerMode(True)
    step_reader.SetNameMode(True)
    step_reader.SetMatMode(True)

    status = step_reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        step_reader.Transfer(doc)

    labels = TDF_LabelSequence()
    color_labels = TDF_LabelSequence()

    shape_tool.GetFreeShapes(labels)

    print("Number of shapes at root :%i" % labels.Length())
    for i in range(labels.Length()):
        sub_shapes_labels = TDF_LabelSequence()
        print("Is Assembly :", shape_tool.IsAssembly(labels.Value(i + 1)))
        sub_shapes = shape_tool.GetSubShapes(labels.Value(i + 1), sub_shapes_labels)
        print("Number of subshapes in the assemly :%i" % sub_shapes_labels.Length())
    l_colors.GetColors(color_labels)

    print("Number of colors=%i" % color_labels.Length())
    for i in range(color_labels.Length()):
        color = color_labels.Value(i + 1)
        print(color.DumpToString())

    for i in range(labels.Length()):
        label = labels.Value(i + 1)
        a_shape = shape_tool.GetShape(label)
        m = l_layers.GetLayers(a_shape)
        _shapes.append(a_shape)

    return _shapes

def read_step_file_with_names_colors(filename):
    """Returns list of tuples (topods_shape, label, color)
    Use OCAF.
    """
    if not os.path.isfile(filename):
        raise FileNotFoundError(f"{filename} not found.")
    # the list:
    output_shapes = {}

    # create an handle to a document
    doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))

    # Get root assembly
    shape_tool = XCAFDoc_DocumentTool_ShapeTool(doc.Main())
    color_tool = XCAFDoc_DocumentTool_ColorTool(doc.Main())
    # layer_tool = XCAFDoc_DocumentTool_LayerTool(doc.Main())
    # mat_tool = XCAFDoc_DocumentTool_MaterialTool(doc.Main())

    step_reader = STEPCAFControl_Reader()
    step_reader.SetColorMode(True)
    step_reader.SetLayerMode(True)
    step_reader.SetNameMode(True)
    step_reader.SetMatMode(True)
    step_reader.SetGDTMode(True)

    status = step_reader.ReadFile(filename)
    if status == IFSelect_RetDone:
        step_reader.Transfer(doc)

    locs = []

    def _get_sub_shapes(lab, loc):
        # global cnt, lvl
        # cnt += 1
        # print("\n[%d] level %d, handling LABEL %s\n" % (cnt, lvl, _get_label_name(lab)))
        # print()
        # print(lab.DumpToString())
        # print()
        # print("Is Assembly    :", shape_tool.IsAssembly(lab))
        # print("Is Free        :", shape_tool.IsFree(lab))
        # print("Is Shape       :", shape_tool.IsShape(lab))
        # print("Is Compound    :", shape_tool.IsCompound(lab))
        # print("Is Component   :", shape_tool.IsComponent(lab))
        # print("Is SimpleShape :", shape_tool.IsSimpleShape(lab))
        # print("Is Reference   :", shape_tool.IsReference(lab))

        # users = TDF_LabelSequence()
        # users_cnt = shape_tool.GetUsers(lab, users)
        # print("Nr Users       :", users_cnt)

        l_subss = TDF_LabelSequence()
        shape_tool.GetSubShapes(lab, l_subss)
        # print("Nb subshapes   :", l_subss.Length())
        l_comps = TDF_LabelSequence()
        shape_tool.GetComponents(lab, l_comps)
        # print("Nb components  :", l_comps.Length())
        # print()
        name = lab.GetLabelName()
        print("Name :", name)

        if shape_tool.IsAssembly(lab):
            l_c = TDF_LabelSequence()
            shape_tool.GetComponents(lab, l_c)
            for i in range(l_c.Length()):
                label = l_c.Value(i + 1)
                if shape_tool.IsReference(label):
                    # print("\n########  reference label :", label)
                    label_reference = TDF_Label()
                    shape_tool.GetReferredShape(label, label_reference)
                    loc = shape_tool.GetLocation(label)
                    # print("    loc          :", loc)
                    # trans = loc.Transformation()
                    # print("    tran form    :", trans.Form())
                    # rot = trans.GetRotation()
                    # print("    rotation     :", rot)
                    # print("    X            :", rot.X())
                    # print("    Y            :", rot.Y())
                    # print("    Z            :", rot.Z())
                    # print("    W            :", rot.W())
                    # tran = trans.TranslationPart()
                    # print("    translation  :", tran)
                    # print("    X            :", tran.X())
                    # print("    Y            :", tran.Y())
                    # print("    Z            :", tran.Z())

                    locs.append(loc)
                    # print(">>>>")
                    # lvl += 1
                    _get_sub_shapes(label_reference, loc)
                    # lvl -= 1
                    # print("<<<<")
                    locs.pop()

        elif shape_tool.IsSimpleShape(lab):
            # print("\n########  simpleshape label :", lab)
            shape = shape_tool.GetShape(lab)
            # print("    all ass locs   :", locs)

            loc = TopLoc_Location()
            for l in locs:
                # print("    take loc       :", l)
                loc = loc.Multiplied(l)

            # trans = loc.Transformation()
            # print("    FINAL loc    :")
            # print("    tran form    :", trans.Form())
            # rot = trans.GetRotation()
            # print("    rotation     :", rot)
            # print("    X            :", rot.X())
            # print("    Y            :", rot.Y())
            # print("    Z            :", rot.Z())
            # print("    W            :", rot.W())
            # tran = trans.TranslationPart()
            # print("    translation  :", tran)
            # print("    X            :", tran.X())
            # print("    Y            :", tran.Y())
            # print("    Z            :", tran.Z())
            c = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
            color_set = False
            if (
                color_tool.GetInstanceColor(shape, 0, c)
                or color_tool.GetInstanceColor(shape, 1, c)
                or color_tool.GetInstanceColor(shape, 2, c)
            ):
                color_tool.SetInstanceColor(shape, 0, c)
                color_tool.SetInstanceColor(shape, 1, c)
                color_tool.SetInstanceColor(shape, 2, c)
                color_set = True
                n = c.Name(c.Red(), c.Green(), c.Blue())
                print(
                    "    instance color Name & RGB: ",
                    c,
                    n,
                    c.Red(),
                    c.Green(),
                    c.Blue(),
                )

            if not color_set:
                if (
                    color_tool.GetColor(lab, 0, c)
                    or color_tool.GetColor(lab, 1, c)
                    or color_tool.GetColor(lab, 2, c)
                ):

                    color_tool.SetInstanceColor(shape, 0, c)
                    color_tool.SetInstanceColor(shape, 1, c)
                    color_tool.SetInstanceColor(shape, 2, c)

                    n = c.Name(c.Red(), c.Green(), c.Blue())
                    print(
                        "    shape color Name & RGB: ",
                        c,
                        n,
                        c.Red(),
                        c.Green(),
                        c.Blue(),
                    )

            shape_disp = BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape()
            if not shape_disp in output_shapes:
                output_shapes[shape_disp] = [lab.GetLabelName(), c]
            for i in range(l_subss.Length()):
                lab_subs = l_subss.Value(i + 1)
                # print("\n########  simpleshape subshape label :", lab)
                shape_sub = shape_tool.GetShape(lab_subs)

                c = Quantity_Color(0.5, 0.5, 0.5, Quantity_TOC_RGB)  # default color
                color_set = False
                if (
                    color_tool.GetInstanceColor(shape_sub, 0, c)
                    or color_tool.GetInstanceColor(shape_sub, 1, c)
                    or color_tool.GetInstanceColor(shape_sub, 2, c)
                ):
                    color_tool.SetInstanceColor(shape_sub, 0, c)
                    color_tool.SetInstanceColor(shape_sub, 1, c)
                    color_tool.SetInstanceColor(shape_sub, 2, c)
                    color_set = True
                    n = c.Name(c.Red(), c.Green(), c.Blue())
                    print(
                        "    instance color Name & RGB: ",
                        c,
                        n,
                        c.Red(),
                        c.Green(),
                        c.Blue(),
                    )

                if not color_set:
                    if (
                        color_tool.GetColor(lab_subs, 0, c)
                        or color_tool.GetColor(lab_subs, 1, c)
                        or color_tool.GetColor(lab_subs, 2, c)
                    ):
                        color_tool.SetInstanceColor(shape, 0, c)
                        color_tool.SetInstanceColor(shape, 1, c)
                        color_tool.SetInstanceColor(shape, 2, c)

                        n = c.Name(c.Red(), c.Green(), c.Blue())
                        print(
                            "    shape color Name & RGB: ",
                            c,
                            n,
                            c.Red(),
                            c.Green(),
                            c.Blue(),
                        )
                shape_to_disp = BRepBuilderAPI_Transform(
                    shape_sub, loc.Transformation()
                ).Shape()
                # position the subshape to display
                if not shape_to_disp in output_shapes:
                    output_shapes[shape_to_disp] = [lab_subs.GetLabelName(), c]

    def _get_shapes():
        labels = TDF_LabelSequence()
        shape_tool.GetFreeShapes(labels)
        # global cnt
        # cnt += 1

        print()
        print("Number of shapes at root :", labels.Length())
        print()
        for i in range(labels.Length()):
            root_item = labels.Value(i + 1)
            _get_sub_shapes(root_item, None)

    _get_shapes()
    return output_shapes


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

def get_ass(sshp, *kwargs):
    global shp
    print("SHP",sshp)
    top_comps = TDF_LabelSequence()
    print(top_comps)
    print(top_comps.Length())

    print(shp[sshp[0]])
    return 0

    it = TopoDS_Iterator(sshp[0])
    while it.More():
       shp = it.Value()
       trsf = shp.Location().Transformation()
       print (trsf.TranslationPart().Coord())
       it.Next()

    c_label = top_comps.Value(0)
    c_name = c_label.GetLabelName()
    c_entry = c_label.EntryDumpToString()
    print(c_name)
    print(c_entry)

    for shp in sshp:
        print(shp.NbChildren())

        print(shp.ShapeType())
        # print(shp.TShape())



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
    global shp
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
        print(os.path.exists(nazwa))
    # shp = get_step_file("E:/GIT/DOKTORAT/model2.stp")
    # shp = get_step_file(nazwa)
    shp = read_step_file_with_names_colors(nazwa)
    #shp = read_step_file("E:/GIT/DOKTORAT/all_together.step")
    print(shp)
    print(dir(shp))
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
    lshp = []
    print("START")
    for i in shp.keys():
        # print(i)
        lshp.append(i)
    print("END")



    display.DisplayShape(lshp, update=True)
    #display.SetSelectionModeFace()
    # display.SetSelectionModeShape()
    # display.register_select_callback(get_face)
    display.register_select_callback(get_ass)

    print(shp)

    # print(shp.NbChildren())
    # print(shp.ShapeType())
    # print(shp.TShape())






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
