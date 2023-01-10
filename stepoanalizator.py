# -*- coding: utf-8 -*-
#!/usr/bin/python
# TODO
# plik vtk z step, bez łuków
# orientacja z plików  vtk
#
# IMPORTY
import wx
import vtk
import builtins
import os
import sys
import numpy as np
# from vtk.util.colors import *
import gzip
import zipfile
from vtkfun import *
import wx.lib.agw.customtreectrl as CT
from xml.dom.minidom import *
import shutil
import time
import vtkmodules
import vtkmodules.all
from step_fun import *
import csv

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCC.Core.TopoDS import topods_Face, TopoDS_Iterator, TopoDS_ListOfShape
from OCC.Core.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa
# from OCC.Core import BRepAdaptor
# print(dir(BRepAdaptor))
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Pnt, BRep_Tool_IsGeometric, BRep_Tool_Parameter, BRep_Tool_Curve
# sys.exit()
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCC.Core.TopoDS import topods_Vertex
from OCC.Display.SimpleGui import init_display
#from OCC.Display.wxDisplay import wxBaseViewer
from mywxDisplay import wxBaseViewer, wxViewer3d
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

shtypes = ["COMPOUND", "COMPSOLID", "SOLID",
           "SHELL", "FACE", "WIRE", "EDGE", "VERTEX"]

nazwa = "E:/GIT/DOKTORAT/STEPY/dwuteownik_00059.stp"

stepdir = "E:/GIT/DOKTORAT/STEPY"
stepdir = "/home/maciejm/GIT/STEPY/PARTY2/BLACHY/"
stepdir = "/home/maciejm/GIT/STEPY/PARTY2/PROFILE/"

steplista = os.listdir(stepdir)
# print(steplista)

failist = ""
# steplista = ["dwuteownik_00059.stp"]

fulltopolista = []
eulist = []
solist = []

for s in steplista:
    try:
        nazwa = os.path.join(stepdir, s)
        print(nazwa)

        faces = []
        edges = []
        vertices = []

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

        print("NBCHILDREN", shp.NbChildren(), shtypes[shp.ShapeType()])
        tsldi = TopoDS_Iterator(shp)
        tsldi.Initialize(shp)
        solids = 0
        while tsldi.More():
            print("SHELL")
            tshp = tsldi.Value()
            solids += 1
            print(tshp.NbChildren())
            print(tshp.ShapeType(), shtypes[tshp.ShapeType()])
            tshli = TopoDS_Iterator(tshp)
            tshli.Initialize(tshp)
            while tshli.More():
                print("FACE")
                ttshp = tshli.Value()
                print(ttshp.NbChildren())
                print(ttshp.ShapeType(), shtypes[ttshp.ShapeType()])
                tfaci = TopoDS_Iterator(ttshp)
                tfaci.Initialize(ttshp)

                surf = BRepAdaptor_Surface(topods_Face(ttshp), True)
                stypetxt = surf_type2text(surf.GetType())

                faces.append(stypetxt)

                while tfaci.More():
                    tttshp = tfaci.Value()
                    print(tttshp.NbChildren())
                    print(tttshp.ShapeType(), shtypes[tttshp.ShapeType()])
                    twiri = TopoDS_Iterator(tttshp)
                    twiri.Initialize(tttshp)
                    while twiri.More():
                        ttttshp = twiri.Value()
                        print(ttttshp.NbChildren())
                        print(ttttshp.ShapeType(),
                              shtypes[ttttshp.ShapeType()])

                        #curv = BRepAdaptor_Curve(ttttshp).Curve()
                        # print("curv",curv.GetType())
                        # print(dir(curv))
                        # print(curv)
                        # print(curv.Circle())
                        a = 0.0
                        b = 0.0
                        [curve_handle, a, b] = BRep_Tool.Curve(ttttshp)
                        # print(dir(curve_handle))
                        # print(curve_handle.D0)
                        ctypename = curve_handle.DynamicType().Name().replace("Geom_", "")
                        print(ctypename)
                        edges.append(ctypename)
                        tveri = TopoDS_Iterator(ttttshp)
                        tveri.Initialize(ttttshp)
                        while tveri.More():
                            tttttshp = tveri.Value()
                            print(tttttshp.NbChildren())
                            print(tttttshp.ShapeType(),
                                  shtypes[tttttshp.ShapeType()])
                            # print(dir(tttttshp))

                            v = topods_Vertex(tttttshp)
                            pnt = BRep_Tool.Pnt(v)
                            print("3d gp_Pnt selected coordinates : X=",
                                  pnt.X(), "Y=", pnt.Y(), "Z=", pnt.Z())
                            vertices.append([pnt.X(), pnt.Y(), pnt.Z()])
                            tveri.Next()

                            # allpoints.append([pnt.X(),pnt.Y(),pnt.Z()])

                        # nedge = ntree.AppendItem(selsurf, ctypename)
                        # telen = ntree.AppendItem(nedge, "Len=%.2f"%elen(ttshp))

                        twiri.Next()

                    tfaci.Next()

                tshli.Next()

            tsldi.Next()
            print(faces)
            print(edges)
            fudict = dict.fromkeys(faces)
            for f in fudict.keys():
                fudict[f] = list(np.where(np.array(faces) == f)[0])
            print(fudict)
            eudict = dict.fromkeys(edges)
            for e in eudict.keys():
                eudict[e] = list(np.where(np.array(edges) == e)[0])
            print(eudict)
            print(" ")
            for i in fudict.keys():
                print(i, len(fudict[i]))
            print(" ")
            for i in eudict.keys():
                print(i, len(eudict[i]))
            print(vertices)
            avertices = np.array(vertices)
            # print(np.unique(avertices,axis=0))
            print(len(vertices), len(list(np.unique(avertices, axis=0))))

            numfaces = len(faces)
            numedges = int(len(edges) / 2)
            numverts = len(list(np.unique(avertices, axis=0)))

            # V - E + F = 2
            fp, fc, fo = 0, 0, 0
            euler = numverts - numedges + numfaces
            print("EULER", euler)
            if "Plane" in fudict.keys():
                fp = len(fudict["Plane"])
            if "Cylinder" in fudict.keys():
                fc = len(fudict["Cylinder"])
            fo = numfaces - fp - fc

            el, ec, ee, eo, ece = 0, 0, 0, 0, 0
            if "Line" in eudict.keys():
                el = int(len(eudict["Line"]) / 2)
            if "Circle" in eudict.keys():
                ec = int(len(eudict["Circle"]) / 2)
            if "Ellipse" in eudict.keys():
                ee = int(len(eudict["Ellipse"]) / 2)
            eo = numedges - el - ec - ee
            ece = ec + ee

            topolist = [s.rsplit("_")[0], numfaces, numedges,
                        numverts, fp, fc, fo, el, ec, ee, eo, ece, euler]
            fulltopolista.append(topolist)
            if euler != 2:
                eulist.append(nazwa)
            if solids > 1:
                solist.append(nazwa)

            print(topolist)
    except:
        failist += "%s\n" % nazwa


f = open("/home/maciejm/GIT/STEPY/afail.txt", "w")
f.write(failist)
f.close()

fulltopocsv = ""
eulista = ""
solista = ""

for l in fulltopolista:
    linia = ""
    for k in l:
        linia += str(k)+","
    linia = linia[:-1]
    linia += "\n"
    fulltopocsv += linia

for i in eulist:
    eulista += "rm %s\n"%i

for i in solist:
    solista += "rm %s\n"%i

f = open('/home/maciejm/GIT/STEPY/topolista.csv', 'w')
f.write(fulltopocsv)
f.close()

f = open('/home/maciejm/GIT/STEPY/eulista.sh', 'w')
f.write(eulista)
f.close()

f = open('/home/maciejm/GIT/STEPY/solista.sh', 'w')
f.write(solista)
f.close()

print(fulltopolista)


sys.exit()
