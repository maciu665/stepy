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
import numpy as np
import svgwrite
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
from scipy.spatial.transform import Rotation

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCC.Core.TopoDS import topods_Face,TopoDS_Iterator,TopoDS_ListOfShape
from OCC.Core.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa
from OCC.Core.HLRBRep import HLRBRep_Algo, HLRBRep_HLRToShape
from OCC.Core.HLRAlgo import HLRAlgo_Projector

from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_SurfaceProperties
# from OCC.Core import BRepAdaptor
# print(dir(BRepAdaptor))
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Pnt, BRep_Tool_IsGeometric, BRep_Tool_Parameter, BRep_Tool_Curve
from OCC.Core.gp import (    gp_Pnt,    gp_Vec,    gp_Pnt2d,    gp_Lin,    gp_Dir,    gp_Ax2,    gp_Quaternion,    gp_QuaternionSLerp,    gp_XYZ,    gp_Mat,)
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

shtypes =["COMPOUND","COMPSOLID","SOLID","SHELL","FACE","WIRE","EDGE","VERTEX"]
ctypes = ["Line" , "Circle" , "Ellipse" , "Hyperbola" , "Parabola" , "BezierCurve" , "BSplineCurve" , "OffsetCurve" , "OtherCurve"]

nazwa = "E:/GIT/DOKTORAT/STEPY/dwuteownik_00057.stp"
nazwa = "E:/GIT/DOKTORAT/STEPY/plaskownik_00003.stp"
nazwa = "E:/GIT/DOKTORAT/STEPY/dwuteownik_00058.stp"

stepdir = "E:/GIT/DOKTORAT/STEPY"




hebfile = "E:/GIT/DOKTORAT/BELKI/HEB.csv"
f = open(hebfile,"r")
heblines = f.read().splitlines()
f.close()

dwgheb = svgwrite.Drawing(hebfile.replace("csv","svg"), profile='tiny')
heby = {}

def heb2lines(hebline):
    heb = hebline.split(",")
    print(heb)
    #b,h,s,t,r = float(heb[1]),float(heb[2]),float(heb[3]),float(heb[4]),float(heb[5])
    [b,h,s,t,r] = [float(h) for h in heb[1:]]
    ppts = []
    ppts.append([0,0])
    ppts.append([b,0])
    ppts.append([b,t])
    ppts.append([b/2+s/2+r,t])
    ppts.append([b/2+s/2,t+r])
    ppts.append([b/2+s/2,h-t-r])
    ppts.append([b/2+s/2+r,h-t])
    ppts.append([b,h-t])
    ppts.append([b,h])
    ppts.append([0,h])
    ppts.append([0,h-t])
    ppts.append([b/2-s/2-r,h-t])
    ppts.append([b/2-s/2,h-t-r])
    ppts.append([b/2-s/2,t+r])
    ppts.append([b/2-s/2-r,t])
    ppts.append([0,t])
    pegs = []
    for p in range(len(ppts)-1):
        pegs.append([p,p+1])
    pegs.append([len(ppts)-1,0])
    pname = heb[0]
    return pname,ppts,pegs

for line in heblines:
    print(line)
    pname,ppts,pegs = heb2lines(line)
    heby[pname] = [ppts,pegs]
    for e in range(len(pegs)):
        dwgheb.add(dwgheb.line(ppts[pegs[e][0]], ppts[pegs[e][1]], stroke=svgwrite.rgb(10, 10, 16, '%')))
    break

dwgheb.save()

#sys.exit()

tsteplista = os.listdir(stepdir)
print(tsteplista)
steplista = []
for i in tsteplista:
    if "dwuteownik" in i:
        steplista.append(i)

steplista = [nazwa]

failist = ""

for s in steplista:
    nazwa = os.path.join(stepdir,s)
    print(nazwa)


print(os.path.exists(nazwa))

# shp = get_step_file("E:/GIT/DOKTORAT/model2.stp")
step_reader = STEPControl_Reader()
status = step_reader.ReadFile(nazwa)

if status == IFSelect_RetDone:  # check status
    failsonly = False
    step_reader.PrintCheckLoad(failsonly, IFSelect_ItemsByEntity)
    step_reader.PrintCheckTransfer(failsonly, IFSelect_ItemsByEntity)
    step_reader.TransferRoot(1)
    shp = step_reader.Shape(1)
else:
    print("Error: can't read file.")
    sys.exit(0)

'''
gprops = GProp_GProps()
brepgprop_VolumeProperties(shp, gprops)
volume = gprops.Mass()
com = gprops.CentreOfMass()
# print(dir(gprops))
print(volume,com)
# sys.exit()
'''


#shp = read_step_file("E:/GIT/DOKTORAT/all_together.step")
print(shp)
#print(dir(shp))
print(shp.NbChildren())
print(shp.ShapeType())
print(shp.TShape())

tsldi = TopoDS_Iterator(shp)
tsldi.Initialize(shp)

allvs = []

while tsldi.More():
    tshp = tsldi.Value()
    tshli = TopoDS_Iterator(tshp)
    tshli.Initialize(tshp)
    while tshli.More():
        ttshp = tshli.Value()
        tfaci = TopoDS_Iterator(ttshp)
        tfaci.Initialize(ttshp)
        while tfaci.More():
            tttshp = tfaci.Value()
            twiri = TopoDS_Iterator(tttshp)
            twiri.Initialize(tttshp)
            while twiri.More():
                ttttshp = twiri.Value()
                a = 0.0
                b = 0.0
                [curve_handle, a, b] = BRep_Tool.Curve(ttttshp)
                ctypename = curve_handle.DynamicType().Name().replace("Geom_","")
                print(ctypename)
                if ctypename == "Line":
                    tveri = TopoDS_Iterator(ttttshp)
                    tveri.Initialize(ttttshp)
                    pts = []
                    while tveri.More():
                        tttttshp = tveri.Value()
                        v = topods_Vertex(tttttshp)
                        pnt = BRep_Tool.Pnt(v)
                        #print("3d gp_Pnt selected coordinates : X=", pnt.X(), "Y=", pnt.Y(), "Z=", pnt.Z())
                        tveri.Next()
                        pts.append([pnt.X(), pnt.Y(), pnt.Z()])
                    allvs.append(np.array(pts[1])-np.array(pts[0]))
                twiri.Next()
            tfaci.Next()
        tshli.Next()
    tsldi.Next()
print(allvs)
uvs = []
for v in allvs:
    va = np.array(v)
    norm1 = va / np.linalg.norm(va)
    if list(norm1) not in uvs and list(-1*norm1) not in uvs:
        uvs.append(list(norm1))
print(uvs)

dwg = svgwrite.Drawing(nazwa.replace("STEPY","SVG").replace("stp","svg"), profile='tiny')

for uv in uvs:

    myAlgo = HLRBRep_Algo()
    aProjector = HLRAlgo_Projector(gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(uv[0],uv[1],uv[2])));
    myAlgo.Add(shp)
    myAlgo.Projector(aProjector)
    myAlgo.Update()
    myAlgo.Hide()

    #HLRBRep_HLRToShape aHLRToShape(myAlgo)
    hlr_shapes = HLRBRep_HLRToShape(myAlgo)

    aCompound = TopoDS_Compound()
    aBuilder  = BRep_Builder()

    #@visible_smooth_edges = hlr_shapes.Rg1LineVCompound()
    visible_edges = hlr_shapes.VCompound()
    print(visible_edges)

    edges = list(TopologyExplorer(visible_edges).edges())

    #dwg.add(dwg.text('Test', insert=(0, 0.2), fill='red'))
    dpts = []
    degs = []

    for i in edges:
        #print(i.ShapeType())

        curv = BRepAdaptor_Curve(i).Curve()
        print(BRepAdaptor_Curve(i).GetType())
        print(ctypes[BRepAdaptor_Curve(i).GetType()])

        tveri = TopoDS_Iterator(i)
        tveri.Initialize(i)
        pts = []

        while tveri.More():
            p = tveri.Value()
            #print(tttttshp.NbChildren())
            #print(tttttshp.ShapeType(),shtypes[tttttshp.ShapeType()])
            # print(dir(tttttshp))

            v = topods_Vertex(p)
            pnt = BRep_Tool.Pnt(v)
            print("3d gp_Pnt selected coordinates : X=", pnt.X(), "Y=", pnt.Y(), "Z=", pnt.Z())
            npt = [pnt.X(),pnt.Y()]
            if npt in dpts:
                print("JEST")
                pts.append(dpts.index(npt))
            else:
                dpts.append(npt)
                pts.append(dpts.index(npt))

            #pts.append([pnt.X(),pnt.Y()])
            tveri.Next()
        degs.append(pts)
    for i in degs:
        dwg.add(dwg.line(dpts[i[0]], dpts[i[1]], stroke=svgwrite.rgb(10, 10, 16, '%')))





dwg.save()


















sys.exit()
