# -*- coding: utf-8 -*-
#!/usr/bin/python
# TODO
# lista punktow
# lista krawedzi
# lista powierzchni
# plik vtk z step, bez łuków
#
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

from OCC.Core.TopExp import TopExp_Explorer,topexp_MapShapes,topexp_MapShapesAndAncestors
from OCC.Core.TopTools import TopTools_MapOfShape,TopTools_IndexedMapOfShape,TopTools_IndexedDataMapOfShapeListOfShape,TopTools_ListOfShape
from OCC.Core.TopoDS import TopoDS_Compound, topods_Face
from OCC.Core.TopAbs import TopAbs_SHELL,TopAbs_FACE,TopAbs_WIRE,TopAbs_EDGE,TopAbs_VERTEX
from OCC.Core.TopLoc import TopLoc_Location

shtypes = ["COMPOUND", "COMPSOLID", "SOLID",
           "SHELL", "FACE", "WIRE", "EDGE", "VERTEX"]

ctypes = ["Geom_Line", "Geom_Circle", "Geom_Ellipse", "Geom_BSplineCurve", "Geom_BezierCurve", "Geom_TrimmedCurve", "Geom_Parabola", "Geom_OffsetCurve", "Geom_Hyperbola", "Geom_Conic", "Geom_BoundedCurve"]

#HEB_2800.stp
#DIN_EN_ISO_4032_-_M10_14.stp
nazwa = "DIN_IPE_200_1631459070782.stp"

stepdir = "/home/maciejm/GIT/STEPY/PARTY/"

steplista = os.listdir(stepdir)
# print(steplista)

failist = ""
# steplista = ["dwuteownik_00059.stp"]

fulltopolista = []

#for s in steplista:
#    try:

s = "DIN_IPE_200_1631459070782.stp"

nazwa = os.path.join(stepdir, s)
print(nazwa)

faces = []
edges = []
vertices = []

print(os.path.exists(nazwa))
#sys.exit()

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

faces = []

faceid = 0

shelmap = TopTools_IndexedMapOfShape()
facemap = TopTools_IndexedMapOfShape()
wiremap = TopTools_IndexedMapOfShape()
edgemap = TopTools_IndexedMapOfShape()
vertmap = TopTools_IndexedMapOfShape()




print("NBCHILDREN", shp.NbChildren(), shtypes[shp.ShapeType()])

if shp.NbChildren() == 1 and shtypes[shp.ShapeType()] == "SOLID":
    print("poprawna bryla")
    mapshels = topexp_MapShapes(shp, TopAbs_SHELL, shelmap)
    mapfaces = topexp_MapShapes(shp, TopAbs_FACE, facemap)
    mapwires = topexp_MapShapes(shp, TopAbs_WIRE, wiremap)
    mapedges = topexp_MapShapes(shp, TopAbs_EDGE, edgemap)
    mapverts = topexp_MapShapes(shp, TopAbs_VERTEX, vertmap)

    print(shelmap)
    print(dir(shelmap))

    numshels = shelmap.Size()
    numfaces = facemap.Size()
    numwires = wiremap.Size()
    numedges = edgemap.Size()
    numverts = vertmap.Size()


    print("shells:",numshels)
    print(" faces:",numfaces)
    print(" wires:",numwires)
    print(" edges:",numedges)
    print(" verts:",numverts)
    #print(shellmap.FindKey(1))

    # V - E + F = 2
    fp, fc, fo = 0, 0, 0
    euler = numverts - numedges + numfaces
    if euler == 2 and numshels == 1:
        print("EULER OK")
    else:
        print("EULER ERROR")
        sys.exit()

    ###############################################################################################
    
    # FACES #
    # {[type,#wires,#edges,#verts,list_of_edge_indexes,list_of_vertex_indexes]}
    # types = ["Plane","Cylinder","Cone","Sphere","Torus","BezierSurface","BSplineSurface","SurfaceOfRevolution","SurfaceOfExtrusion","OffsetSurface","OtherSurface"]

    for i in range(numfaces):       #iterate over all faces
        nf = i+1
        tflist = []
        tfshp = facemap.FindKey(nf)  #face shape

        surf = BRepAdaptor_Surface(topods_Face(tfshp), True)
        stype = surf.GetType()
        tflist.append(stype)

        twiremap = TopTools_IndexedMapOfShape()
        tmapwires = topexp_MapShapes(tfshp, TopAbs_WIRE, twiremap)
        tflist.append(twiremap.Size())

        tedgemap = TopTools_IndexedMapOfShape()
        tmapedges = topexp_MapShapes(tfshp, TopAbs_EDGE, tedgemap)
        tflist.append(tedgemap.Size())
        tfedgelist = []
        for j in range(tedgemap.Size()):
            ne = j+1
            tedge = tedgemap.FindKey(ne)
            tedge2 = edgemap.FindIndex(tedge)
            #print(tedge2)
            tfedgelist.append(tedge2)

            a = 0.0
            b = 0.0
            [curve_handle, a, b] = BRep_Tool.Curve(tedge)
            ctypename = curve_handle.DynamicType().Name()
            ctype = ctypes.index(ctypename)
            #print(ctypename,ctype)


        tvertmap = TopTools_IndexedMapOfShape()
        tmapverts = topexp_MapShapes(tfshp, TopAbs_VERTEX, tvertmap)
        tflist.append(tvertmap.Size())
        tflist.append(tfedgelist)

        print(tflist)

        sys.exit()
        


        
        #print(twiremap.Size(),wiremap.FindIndex(twiremap.FindKey(1)))

    sys.exitx()

    tface = facemap.FindKey(7)
    tedgemap = TopTools_IndexedMapOfShape()
    tmapedges = topexp_MapShapes(tface, TopAbs_EDGE, tedgemap)
    print(tedgemap.Size())
    tedge = tedgemap.FindKey(2)
    #print(tedge)
    print(edgemap.FindIndex(tedge))


    #print(t)

    parentfacemap = TopTools_IndexedDataMapOfShapeListOfShape()
    tmapwires2 = topexp_MapShapesAndAncestors(shp, TopAbs_EDGE, TopAbs_FACE, parentfacemap)



    parentfacemap = TopTools_IndexedDataMapOfShapeListOfShape()
    tmapwires2 = topexp_MapShapesAndAncestors(shp, TopAbs_EDGE, TopAbs_FACE, parentfacemap)

    parentfacemap.FindFromIndex(7)
    #print(parentfacemap.Size())


    #print(dir(twiremap))
    tshp = edgemap.FindKey(26)

    parentfaces = TopTools_ListOfShape()
    parentfaceindex = TopTools_IndexedMapOfShape()

    parentfaces = parentfacemap.FindFromKey(tshp)
    parentfaceindex = parentfacemap.FindFromKey(tshp)
    #print(dir(parentfaces))
    #print(parentfaces.Size())
    print(parentfaceindex.Size())
    print(parentfaceindex.First())
    print(parentfaceindex.Last())
    print(facemap.FindIndex(parentfaceindex.First()))
    print(facemap.FindIndex(parentfaceindex.Last()))





    sys.exit()


    
    for i in range(numfaces):
        nf = i+1
        tshp = facemap.FindKey(nf)
        twiremap = TopTools_IndexedMapOfShape()
        tmapwires = topexp_MapShapes(tshp, TopAbs_WIRE, twiremap)
        #print(twiremap.Size(),wiremap.FindIndex(twiremap.FindKey(1)))

        #tmapfaces = topexp_MapShapes(tshp, TopAbs_WIRE, twiremap)
    parentfacemap = TopTools_IndexedDataMapOfShapeListOfShape()
    tmapwires2 = topexp_MapShapesAndAncestors(shp, TopAbs_EDGE, TopAbs_FACE, parentfacemap)



    parentfacemap.FindFromIndex(7)
    print(parentfacemap.Size())


    sys.exit()


    #print(dir(twiremap))
    tshp = edgemap.FindKey(7)

    parentfaces = TopTools_ListOfShape()
    parentfaceindex = TopTools_IndexedMapOfShape()

    parentfaces = parentfacemap.FindFromKey(tshp)
    parentfaceindex = parentfacemap.FindFromKey(tshp)
    #print(dir(parentfaces))
    print(parentfaces.Size())
    print(parentfaceindex.Size())









    twiremap = TopTools_IndexedMapOfShape()
    tmapwires = topexp_MapShapes(tshp, TopAbs_FACE, twiremap)
    #print(twiremap.Size())


    





    #print(facemap.FindKey(1))
    #print(facemap.FindKey(33))
    

    sys.exit()
    tsldi = TopoDS_Iterator(shp)
    tsldi.Initialize(shp)
    while tsldi.More():
        print("SHELL")
        tshp = tsldi.Value()
        '''
        #print(tshp, TopAbs_FACE, mapos)
        mapshapes = topexp_MapShapes(tshp, TopAbs_EDGE, mapos)
        print(mapos)
        print(dir(mapos))
        print(mapos.Size())
        print(mapos.FindKey(2))

        #TopAbs_FACE,TopAbs_EDGE
        sys.exit()
        '''
        print()
        print(tshp.NbChildren(), tshp.ShapeType(), shtypes[tshp.ShapeType()])
        tshli = TopoDS_Iterator(tshp)
        tshli.Initialize(tshp)
        while tshli.More():
            print("FACE")
            ttshp = tshli.Value()
            print(ttshp)
            print(ttshp.NbChildren())
            print(ttshp.ShapeType(), shtypes[ttshp.ShapeType()])
            tfaci = TopoDS_Iterator(ttshp)
            tfaci.Initialize(ttshp)


            surf = BRepAdaptor_Surface(topods_Face(ttshp), True)
            stypetxt = surf_type2text(surf.GetType())
            print(stypetxt)
            #sys.exit()

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
                    #print(dir(ttttshp))
                    print("edż",ttttshp,ttttshp)
                    print(ttttshp.ShapeType(), shtypes[ttttshp.ShapeType()],"edge?")
                    print("curve0")
                    #curv = BRepAdaptor_Curve(ttttshp).Curve()
                    # print("curv",curv.GetType())
                    # print(dir(curv))
                    # print(curv)
                    print("curve")
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
                        print(tttttshp.ShapeType(),shtypes[tttttshp.ShapeType()])
                        # print(dir(tttttshp))

                        v = topods_Vertex(tttttshp)
                        pnt = BRep_Tool.Pnt(v)
                        print("3d gp_Pnt selected coordinates : X=",pnt.X(), "Y=", pnt.Y(), "Z=", pnt.Z())
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

        print(topolist)
    #    except:
    #        failist += "%s\n" % nazwa

    sys.exit()

    f = open("E:/GIT/DOKTORAT/afail.txt", "w")
    f.write(failist)
    f.close()

    fulltopocsv = ""
    for l in fulltopolista:
        linia = ""
        for k in l:
            linia += str(k)+","
        linia = linia[:-1]
        linia += "\n"
        fulltopocsv += linia

    f = open('E:/GIT/DOKTORAT/topolista.csv', 'w')
    f.write(fulltopocsv)
    f.close()



    print(fulltopolista)


    sys.exit()
