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

from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCC.Core.TopoDS import topods_Face,TopoDS_Iterator
from OCC.Core.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa
# from OCC.Core import BRepAdaptor
# print(dir(BRepAdaptor))
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Pnt, BRep_Tool_IsGeometric, BRep_Tool_Parameter, BRep_Tool_Curve, BRep_Builder
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
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader,STEPCAFControl_Writer
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TDF import TDF_LabelSequence,TDF_Label
from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.Bnd import Bnd_Box

from OCC.Core.gp import gp_Trsf, gp_Vec

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

class ExportCAFMethod (object):

    def __init__(self, name="name", tol=1.0E-10):
        self.name = name
        self.step = STEPCAFControl_Writer()
        self.step.SetNameMode(True)
        self.h_doc = Handle_TDocStd_Document()
        self.x_app = XCAFApp_Application.GetApplication().GetObject()
        self.x_app.NewDocument(TCollection_ExtendedString("MDTV-CAF"), self.h_doc)
        self.doc   = self.h_doc.GetObject()
        self.h_shape_tool = XCAFDoc_DocumentTool_ShapeTool(self.doc.Main())
        self.shape_tool   = self.h_shape_tool.GetObject()
        Interface_Static_SetCVal("write.step.schema", "AP214")

    def Add (self, shape, name="name"):
        """
        STEPControl_AsIs                   translates an Open CASCADE shape to its highest possible STEP representation.
        STEPControl_ManifoldSolidBrep      translates an Open CASCADE shape to a STEP manifold_solid_brep or brep_with_voids entity.
        STEPControl_FacetedBrep            translates an Open CASCADE shape into a STEP faceted_brep entity.
        STEPControl_ShellBasedSurfaceModel translates an Open CASCADE shape into a STEP shell_based_surface_model entity.
        STEPControl_GeometricCurveSet      translates an Open CASCADE shape into a STEP geometric_curve_set entity.
        """
        label = self.shape_tool.AddShape(shape)
        self.step.Transfer(self.h_doc, STEPControl_AsIs)

    def Write (self, filename=None):
        if not filename:
            filename = self.name
        path, ext = os.path.splitext(filename)
        if not ext:
            ext = ".stp"
        status = self.step.Write(path + ext)
        assert(status == IFSelect_RetDone)

def elen(edg):
    curve_adapt = BRepAdaptor_Curve(edg)
    length = GCPnts_AbscissaPoint().Length(curve_adapt, curve_adapt.FirstParameter(), curve_adapt.LastParameter(), 1e-6)
    return length

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
        name = lab.GetLabelName()
        if name == "":
            print("Is Assembly    :", shape_tool.IsAssembly(lab))
            print("Is Free        :", shape_tool.IsFree(lab))
            print("Is Shape       :", shape_tool.IsShape(lab))
            print("Is Compound    :", shape_tool.IsCompound(lab))
            print("Is Component   :", shape_tool.IsComponent(lab))
            print("Is SimpleShape :", shape_tool.IsSimpleShape(lab))
            print("Is Reference   :", shape_tool.IsReference(lab))

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
        if name == "":
            "!\n!\n!\n!"

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

                    locs.append(loc)
                    _get_sub_shapes(label_reference, loc)
                    locs.pop()

        elif shape_tool.IsSimpleShape(lab):
            # print("\n########  simpleshape label :", lab)
            shape = shape_tool.GetShape(lab)
            # print("    all ass locs   :", locs)

            loc = TopLoc_Location()
            for l in locs:
                # print("    take loc       :", l)
                loc = loc.Multiplied(l)


            shape_disp = BRepBuilderAPI_Transform(shape, loc.Transformation()).Shape()
            if not shape_disp in output_shapes:
                output_shapes[shape_disp] = lab.GetLabelName()
                if lab.GetLabelName() == "":
                    print("koza")


            '''
            for i in range(l_subss.Length()):
                lab_subs = l_subss.Value(i + 1)
                # print("\n########  simpleshape subshape label :", lab)
                shape_sub = shape_tool.GetShape(lab_subs)


                shape_to_disp = BRepBuilderAPI_Transform(
                    shape_sub, loc.Transformation()
                ).Shape()
                # position the subshape to display
                if not shape_to_disp in output_shapes:
                    output_shapes[shape_to_disp] = lab_subs.GetLabelName()
                    if lab_subs.GetLabelName() == "":
                        print("chomik")
            '''
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

    trsf = sshp[0].Location().Transformation()
    curloc = trsf.TranslationPart().Coord()
    print(curloc)




    bbox = Bnd_Box()
    brepbndlib_Add(sshp[0], bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    print(xmin, ymin, zmin, xmax, ymax, zmax)
    xc = (xmin+xmax)/2
    yc = (ymin+ymax)/2
    zc = (zmin+zmax)/2
    print("old",xc,yc,zc)

    dx = curloc[0]-xc
    dy = curloc[1]-yc
    dz = curloc[2]-zc

    print(dx,dy,dz)

    trsf = gp_Trsf()
    trsf.SetTranslation(gp_Vec(-xc, -yc, -zc))
    sshp[0].Move(TopLoc_Location(trsf))

    bbox = Bnd_Box()
    brepbndlib_Add(sshp[0], bbox)
    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    print(xmin, ymin, zmin, xmax, ymax, zmax)
    xc = (xmin+xmax)/2
    yc = (ymin+ymax)/2
    zc = (zmin+zmax)/2
    print("new",xc,yc,zc)

    display.EraseAll()
    display.DisplayShape(sshp[0])
    display.FitAll()

    builder = BRep_Builder()
    '''
    TopoDS_Compound compound;
    builder.MakeCompound(compound);
    builder.Add(compound, box1);
    builder.Add(compound, box2);
    '''
    writer = STEPControl_Writer()
    koza = writer.Transfer(sshp[0],STEPControl_AsIs);

    # aStat = writer.Write("D:/res.stp");

    writer.Write("E:/GIT/DOKTORAT/export.stp");

    '''
    root = ExportCAFMethod (name="koza")
    root.Add(sshp[0])
    root.Write()
    '''
    # sshp[0].Location().Transformation().TranslationPart().Coord() = (dx,dy,dz)

    # sshp[0].Move()

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
