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


nazwa = "E:/GIT/DOKTORAT/STEPY/dwuteownik_00059.stp"

stepdir = "E:/GIT/DOKTORAT/STEPY"

steplista = os.listdir(stepdir)
print(steplista)

failist = ""

for s in steplista:
    nazwa = os.path.join(stepdir,s)
    print(nazwa)



    try:

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

        BRepMesh_IncrementalMesh(shp, 0.25)
        builder = BRep_Builder()
        comp = TopoDS_Compound()
        builder.MakeCompound(comp)

        bt = BRep_Tool()
        ex = TopExp_Explorer(shp, TopAbs_FACE)

        pts = vtk.vtkPoints()
        ugrid = vtk.vtkUnstructuredGrid()


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

        stlw = vtk.vtkSTLWriter()
        stlw.SetInputConnection(cpd.GetOutputPort())
        stlw.SetFileTypeToBinary()
        stlw.SetFileName(nazwa.replace(".stp",".stl").replace("STEPY","STL"))
        stlw.Update()
    except:
        failist += "%s\n"%nazwa

f = open("E:/GIT/DOKTORAT/fail.txt","w")
f.write(failist)
f.close()
