# -*- coding: utf-8 -*-
#!/usr/bin/python
#
#IMPORTY
import os
import sys
# from vtk.util.colors import *
#import gzip, zipfile
#from kflow_vtkfun import *
#from xml.dom.minidom import *
#import shutil
#import time
#from step_fun import *

from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
#from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
#from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
#from OCC.Core.TopoDS import topods_Face,TopoDS_Iterator
#from OCC.Core.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa
# from OCC.Core import BRepAdaptor
# print(dir(BRepAdaptor))
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Pnt, BRep_Tool_IsGeometric, BRep_Tool_Parameter, BRep_Tool_Curve, BRep_Builder


# sys.exit()
#from OCC.Core.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
#from OCC.Display.SimpleGui import init_display
#from OCC.Display.wxDisplay import wxBaseViewer
#from mywxDisplay import wxBaseViewer,wxViewer3d
#from OCC.Core.BRepool import Curve

from OCC.Extend.TopologyUtils import TopologyExplorer

from OCC.Core.TCollection import TCollection_ExtendedString
from OCC.Core.TDocStd import TDocStd_Document
#from OCC.Core.XCAFDoc import (XCAFDoc_DocumentTool_ShapeTool,XCAFDoc_DocumentTool_ColorTool,XCAFDoc_DocumentTool_LayerTool,XCAFDoc_DocumentTool_MaterialTool,)
from OCC.Core.XCAFDoc import XCAFDoc_DocumentTool_ShapeTool
from OCC.Core.STEPCAFControl import STEPCAFControl_Reader,STEPCAFControl_Writer
from OCC.Core.IFSelect import IFSelect_RetDone
from OCC.Core.TDF import TDF_LabelSequence,TDF_Label
#from OCC.Core.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform

#from OCC.Core.BRepBndLib import brepbndlib_Add
from OCC.Core.Bnd import Bnd_Box

#from OCC.Core.gp import gp_Trsf, gp_Vec

#from OCCUtils.edge import Edge

filename = "/home/maciejm/GIT/STEPY/ASSES/F4150-151-002.stp"
filename = "/home/maciejm/GIT/STEPY/23_Luftsysteme_2022-08-12.stp"
filename = "/home/maciejm/GIT/STEPY/10_Stahlbau_2022-05-24.stp"

if not os.path.isfile(filename):
    print("file not found.")

output_shapes = {}
output_labs = {}

# create an handle to a document
doc = TDocStd_Document(TCollection_ExtendedString("pythonocc-doc"))

# Get root assembly
shape_tool = XCAFDoc_DocumentTool_ShapeTool(doc.Main())
#color_tool = XCAFDoc_DocumentTool_ColorTool(doc.Main())
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
    print("Name sub :", name)
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

        if not shape_disp in output_shapes.keys():
            output_shapes[shape_disp] = lab.GetLabelName()
            output_labs[lab.GetLabelName()] = shape_disp
            if lab.GetLabelName() == "":
                print("koza")


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
    
    #print(output_shapes)
    #print()
    #print(output_labs)

print("koza")
_get_shapes()

for i in output_labs.keys():
    if output_labs[i].ShapeType() == 2:
        print(i,'_'.join(i.split()))
        nfilename = '_'.join(i.split())
        print(output_labs[i])
        print(output_labs[i].ShapeType())
        print()

        writer = STEPControl_Writer()
        koza = writer.Transfer(output_labs[i],STEPControl_AsIs)
        writer.Write("/home/maciejm/GIT/STEPY/PARTY/%s.stp"%nfilename);
        





