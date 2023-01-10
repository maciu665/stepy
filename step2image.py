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
# from vtk.util.colors import *
import gzip, zipfile
from vtkfun import *
import wx.lib.agw.customtreectrl as CT
from xml.dom.minidom import *
import shutil
import time
import vtkmodules
import vtkmodules.all
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 

from stl_render_fun import *
from step_fun import *
from scipy.spatial.transform import Rotation

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCC.Core.TopoDS import topods_Face,TopoDS_Iterator,TopoDS_ListOfShape
from OCC.Core.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa


from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_SurfaceProperties
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

shtypes =["COMPOUND","COMPSOLID","SOLID","SHELL","FACE","WIRE","EDGE","VERTEX"]

nazwa = "E:/GIT/DOKTORAT/STEPY/dwuteownik_00057.stp"
nazwa = "E:/GIT/DOKTORAT/STEPY/dwuteownik_00058.stp"
nazwa = "E:/GIT/DOKTORAT/STEPY/plaskownik_00003.stp"

stepdir = "E:/GIT/DOKTORAT/STEPY"
stepdir = "/home/maciejm/GIT/STEPY/PARTY2/PROFILE"
stepdir = "/home/maciejm/GIT/STEPY/PARTY0"
stepdir = "/home/maciejm/GIT/STEPY/PARTY2/BLACHY"
stls = "/home/maciejm/GIT/STEPY/STL"
imtmpdir = "/home/maciejm/GIT/STEPY"
imdir = "/home/maciejm/GIT/STEPY/IMG"

tsteplista = os.listdir(stepdir)
#print(tsteplista)
steplista = []
for i in tsteplista:
    if "stp" in i:
        steplista.append(i)

#steplista = [nazwa]





resolution = 960,540			#rodzielczosc
bgcolor = 0,0,0					#kolor tla, rgb w zakresie 0-1
surface = 1						#czy wyswietlac powierzchnie
scolor = 0.5,0.5,0.5			#kolor powierzchni
edges = 1						#czy wyswietlac krawedzie
ecolor = 1,1,1					#kolor krawedzi
ethickness = 3					#grubosc krawedzi

campos = 1,1,1					#pozycja kamery
camper = 0						#0-perspektywa, 1-rzutowanie rownolegle
noshading = 0					#wylaczenie cieniowania
cam_angle = 1					#pozycja kamery z kątów
azimuth = 45					#azymut kamery
elevation = 30					#wznios kamery

merge = 1						#czy skleic pliki w jeden duzy


def wrender(im,imfile,killit=0):
	if im:
		win.Render()

		w2if = vtk.vtkWindowToImageFilter()
		w2if.SetInput(win)
		w2if.Update()

		iw = vtk.vtkPNGWriter()
		iw.SetFileName(imfile)
		iw.SetInputData(w2if.GetOutput())
		iw.Write()
		if killit:
			sys.exit()
	else:
		win.OffScreenRenderingOff()
		# ren.ResetCamera()
		win.Render()
		iren.Initialize()
		iren.Start()
		win.Render()

im = 1

ren = vtk.vtkRenderer()
win = vtkwin()
win.AddRenderer(ren)
ren.GradientBackgroundOff()
win.SetSize(resolution)
ren.SetBackground(bgcolor)

if im:
	win.OffScreenRenderingOn()
else:
	win.Render()
	lights = ren.GetLights()
	lights.InitTraversal()
	hl = lights.GetNextItem()
	hl.SetIntensity(0.0)


#sys.exit()
mapper = vtk.vtkPolyDataMapper()



########################################################################
camera = ren.GetActiveCamera()
camera.SetPosition(campos)
camera.SetViewUp(0,0,1)
camera.SetFocalPoint(0,0,0)
camera.SetParallelScale(1)
camera.SetParallelProjection(camper)

########################################################################	LIGHT

#print hl

lightKit = vtk.vtkLightKit()


lightKit.SetKeyLightWarmth(0.6)
lightKit.SetKeyLightIntensity(0.75)
lightKit.SetKeyLightElevation(50)
lightKit.SetKeyLightAzimuth(10)

lightKit.SetFillLightWarmth(0.4)
lightKit.SetKeyToFillRatio(3)
lightKit.SetFillLightElevation(-75)
lightKit.SetFillLightAzimuth(-10)

lightKit.SetBackLightWarmth(0.5)
lightKit.SetKeyToBackRatio(3.50)
lightKit.SetBackLightElevation(0)
lightKit.SetBackLightAzimuth(110)

lightKit.SetHeadLightWarmth(0.5)
lightKit.SetKeyToHeadRatio(3)

lightKit.MaintainLuminanceOn()
lightKit.AddLightsToRenderer(ren)







pactor = vtk.vtkActor()
eactor = vtk.vtkActor()


font = ImageFont.truetype("NotoMono-Regular.ttf", 40)

failist = ""

for s in steplista:
    nazwa = os.path.join(stepdir,s)
    snazwa = os.path.join(stls,s.replace(".stp",".stl"))
    inazwa = os.path.join(imdir,s.replace(".stp",".png"))
    print(nazwa,snazwa)



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
        print(dir(shp))
        print(shp.NbChildren())
        print(shp.ShapeType())
        print(shp.TShape())



        allpoints = []
        sedges = []

        maxarea = 0
        maxfacedir = None

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

                surf = BRepAdaptor_Surface(topods_Face(ttshp), True)
                stypetxt = surf_type2text(surf.GetType())
                '''
                print(stypetxt)
                print(dir(surf))
                print(surf.Plane())
                print(dir(surf.Plane()))
                print(surf.Plane().Axis())
                '''
                if stypetxt == "Plane":
                    pldir = surf.Plane().Axis().Direction()

                    gprops = GProp_GProps()
                    brepgprop_SurfaceProperties(ttshp, gprops)
                    area = gprops.Mass()
                    print(area)
                    if area > maxarea:
                        maxarea = area
                        maxfacedir = [pldir.X(),pldir.Y(),pldir.Z()]

                while tfaci.More():
                    tttshp = tfaci.Value()
                    print(tttshp.NbChildren())
                    print(tttshp.ShapeType(),shtypes[tttshp.ShapeType()])
                    twiri = TopoDS_Iterator(tttshp)
                    twiri.Initialize(tttshp)
                    while twiri.More():
                        ttttshp = twiri.Value()
                        print(ttttshp.NbChildren(),"edz")
                        print(ttttshp.ShapeType(),shtypes[ttttshp.ShapeType()])



                        #curv = BRepAdaptor_Curve(ttttshp).Curve()
                        #print(dir(curv))
                        # print(curv)
                        # print(curv.Circle())
                        a = 0.0
                        b = 0.0
                        [curve_handle, a, b] = BRep_Tool.Curve(ttttshp)
                        # print(dir(curve_handle))
                        print(curve_handle.D0)
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


        while ex.More():
            print("FEJS")
            face = topods_Face(ex.Current())
            location = TopLoc_Location()
            facing = bt.Triangulation(face, location)
            tab = []
            for ni in range(facing.NbNodes()):
                tab.append(facing.Node(ni+1))
            tri = []
            for ni in range(facing.NbTriangles()):
                tri.append(facing.Triangle(ni+1))
            #print(tab)
            #print(dir(tab))

            # for i in range(facing.NbNodes()):
                # print("pt",tab.Value(i))
                # pts.InsertPoint(i,tab.Value(i))

            print(len(tab))
            for i in range(facing.NbTriangles()):
                trian = tri[i]
                index1, index2, index3 = trian.Get()
                # print("pt",tab.Value(index1))
                # print("pt",tab.Value(index1).Coord()[0])
                # print(dir(tab.Value(index1)))
                '''
                pts.InsertPoint(index1,tab.Value(index1).Coord()[0],tab.Value(index1).Coord()[1],tab.Value(index1).Coord()[2])
                pts.InsertPoint(index2,tab.Value(index2).Coord()[0],tab.Value(index2).Coord()[1],tab.Value(index2).Coord()[2])
                pts.InsertPoint(index3,tab.Value(index3).Coord()[0],tab.Value(index3).Coord()[1],tab.Value(index3).Coord()[2])
                '''
                print(index1,index2,index3)

                ti1 = pts.InsertNextPoint(tab[index1-1].Coord()[0],tab[index1-1].Coord()[1],tab[index1-1].Coord()[2])
                ti2 = pts.InsertNextPoint(tab[index2-1].Coord()[0],tab[index2-1].Coord()[1],tab[index2-1].Coord()[2])
                ti3 = pts.InsertNextPoint(tab[index3-1].Coord()[0],tab[index3-1].Coord()[1],tab[index3-1].Coord()[2])

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

        pts2 = vtk.vtkPoints()
        ugrid2 = vtk.vtkUnstructuredGrid()


        evdirs = []
        evlens = []

        for k in range(int(len(allpoints)/2)):
            ti1 = pts2.InsertNextPoint(allpoints[k*2])
            ti2 = pts2.InsertNextPoint(allpoints[k*2+1])
            pointIds = vtk.vtkIdList()
            pointIds.InsertId(0, ti1)
            pointIds.InsertId(1, ti2)
            seid = ugrid2.InsertNextCell(3, pointIds)
            np0 = np.array(allpoints[k*2])
            np1 = np.array(allpoints[k*2+1])
            pvector = np1-np0
            plen = np.linalg.norm(pvector)
            pdir = list(pvector/plen)
            pdir = [round(pdir[0],6),round(pdir[1],6),round(pdir[2],6)]
            print("pvector", pvector, np1, np0, plen, pdir)
            if list(pdir) in evdirs:
                evlens[evdirs.index(list(pdir))] += plen
                print("index",evdirs.index(list(pdir)))
            elif list(pdir*-1) in evdirs:
                evlens[evdirs.index(list(pdir*-1))] += plen
            else:
                evdirs.append(list(pdir))
                print("append",plen, pdir)
                evlens.append(plen)

        print("evlens",evlens)
        print(evdirs)

        ldir = evdirs[evlens.index(max(evlens))]
        print(ldir)
        print(maxfacedir)

        tzdir = np.array(maxfacedir)
        zdir = np.array([0,0,-1])
        xdir = np.array([1,0,0])
        print(list(tzdir) == list(zdir))
        print(list(tzdir) == list(zdir*-1))

        rot2z = [None]
        rldir = None

        if list(tzdir) != list(zdir*-1) and list(tzdir) != list(zdir):
            print("ROTATE TO Z")
            print(np.cross(zdir,tzdir))
            print(np.dot(zdir,tzdir))
            kros = np.cross(zdir,tzdir)
            tkros1 = kros/np.linalg.norm(kros)
            print(tkros1)

            angle = np.arccos(np.dot(zdir,tzdir))
            print(angle,np.degrees(angle),np.linalg.norm(np.cross(zdir,tzdir)))
            tkros = tkros1*np.degrees(angle)
            print(tkros)

            rot = Rotation.from_rotvec(tkros,True)
            rot2z = rot.as_euler('XYZ',True)
            print(rot2z)

            rldir = rot.apply(ldir,True)
            print("LDIR",ldir,rldir)
            ldir = rldir
            # sys.exit()
        print("LDIR",ldir)

        ugrid2.SetPoints(pts2)

        if rot2z[0] != None:
            transowanie = vtk.vtkTransformFilter()
            trans = vtk.vtkTransform()
            # trans.Translate(-cob[0], -cob[1], -cob[2])
            trans.RotateWXYZ(-np.degrees(angle),tkros1[0],tkros1[1],tkros1[2])
            transowanie.SetTransform(trans)
            transowanie.SetInputData(ugrid)
            transowanie.Update()
            ugrid = transowanie.GetOutput()

        xangle = None
        # if list(ldir) != list(xdir*-1) and list(ldir) != list(xdir):
            # print("dot",np.dot(xdir,ldir))
        if (abs(abs(np.dot(xdir,ldir))-1)) > 0.0001:
            print(abs(np.dot(xdir,ldir)-1))
            print("ROTATE TO X")
            print(np.cross(xdir,ldir))
            print("DOT",np.dot(xdir,ldir))
            xros = np.cross(xdir,ldir)
            # if np.linalg.norm(xros) == 0:
                # print(xdir,ldir)
                # sys.exit()
            txros1 = xros/np.linalg.norm(xros)
            print(txros1)
            print(xdir,ldir)
            xangle = np.arccos(np.dot(xdir,ldir))
            print("xangle",math.degrees(xangle))

        if xangle != None:
            transowanie = vtk.vtkTransformFilter()
            trans = vtk.vtkTransform()
            # trans.Translate(-cob[0], -cob[1], -cob[2])
            trans.RotateWXYZ(-np.degrees(xangle),txros1[0],txros1[1],txros1[2])
            transowanie.SetTransform(trans)
            transowanie.SetInputData(ugrid)
            transowanie.Update()
            ugrid = transowanie.GetOutput()

        gf = vtk.vtkGeometryFilter()
        gf.SetInputData(ugrid)
        gf.Update()

        print("POINTS",gf.GetOutput().GetNumberOfPoints())

        cpd = vtk.vtkCleanPolyData()
        cpd.SetInputData(gf.GetOutput())
        cpd.Update()

        print("POINTS",cpd.GetOutput().GetNumberOfPoints())

        bnds = cpd.GetOutput().GetBounds()
        # cob = [(bnds[0]+bnds[1])/2,(bnds[2]+bnds[3])/2,(bnds[4]+bnds[5])/2]
        cob = [(bnds[0]+bnds[1])/2,(bnds[2]+bnds[3])/2,bnds[4]]

        print(bnds,cob)

        transowanie = vtk.vtkTransformFilter()
        trans = vtk.vtkTransform()
        trans.Translate(-cob[0], -cob[1], -cob[2])
        transowanie.SetTransform(trans)
        transowanie.SetInputConnection(cpd.GetOutputPort())
        transowanie.Update()
        tbnds = transowanie.GetOutput().GetBounds()
        print(tbnds)

        # print(com.X(),com.Y(),com.Z())

        # tcom = [com.X()-cob[0],com.Y()-cob[1],com.Z()-cob[2]]
        # print(tcom)

        #points = []

        #for tp in range(transowanie.GetOutput().GetNumberOfPoints()):
            #points.append(list(transowanie.GetOutput().GetPoint(tp)))

        #if transowanie.GetOutput().GetNumberOfCells() < 4:
        #    k = bnds/0
        #    sys.exit()
        print()

        stl = transowanie.GetOutput()

        stlw = vtk.vtkSTLWriter()
        stlw.SetInputData(stl)
        stlw.SetFileTypeToBinary()
        stlw.SetFileName(snazwa)
        stlw.Update()
        
        for a in [eactor,pactor]:
            try:
                ren.RemoveActor(a)
            except:
                pass


        mapper.SetInputData(stl)
        mapper.ScalarVisibilityOff()
        mapper.SetResolveCoincidentTopologyToPolygonOffset()
        mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(-3.5,-3.5)
        # mapper.SetResolveCoincidentTopologyToShiftZBuffer()


        edges3 = vtk.vtkFeatureEdges()
        edges3.ColoringOff()
        edges3.SetInputData(stl)
        edges3.ManifoldEdgesOn()
        edges3.NonManifoldEdgesOn()
        edges3.FeatureEdgesOn()
        edges3.BoundaryEdgesOn()
        edges3.Update()

        vprop = vtk.vtkProperty()
        vprop.LightingOn()
        if noshading:
            vprop.LightingOff()
        vprop.SetColor(scolor)
        vprop.SetSpecular(0)
        vprop.SetSpecularPower(100)

        pactor = vtk.vtkActor()
        pactor.SetMapper(mapper)
        pactor.SetProperty(vprop)

        emapper = vtk.vtkDataSetMapper()
        emapper.SetInputConnection(edges3.GetOutputPort())
        emapper.SetResolveCoincidentTopologyToPolygonOffset()
        emapper.ScalarVisibilityOff()
        eactor = vtk.vtkActor()
        eactor.SetMapper(emapper)

        eprop = eactor.GetProperty()
        eprop.SetEdgeColor(ecolor)
        eprop.SetColor(ecolor)
        eprop.SetLineWidth(ethickness)
        eprop.SetRepresentationToWireframe()
        eprop.SetOpacity(1)

        if edges:
            ren.AddActor(eactor)
        if surface:
            ren.AddActor(pactor)
        ren.ResetCamera()

                #print(camera.GetPosition())
        #print(camera.GetFocalPoint())
        #print(camera.GetClippingRange())
        camera.SetViewAngle(20)
        #ren.ResetCamera()
        # print(camera.GetPosition())
        ren.ResetCameraClippingRange()


        imfile1 = os.path.join(imtmpdir,"image1.png")
        bnds = stl.GetBounds()
        print("bnds", bnds)
        
        bndcenter = [(bnds[1]+bnds[0])/2,(bnds[3]+bnds[2])/2,(bnds[5]+bnds[4])/2]
        bndsize = [(bnds[1]-bnds[0]),(bnds[3]-bnds[2]),(bnds[5]-bnds[4])]
        print(bndcenter)
        print(bndsize)

        camera.SetParallelScale(80)

        psfromheight = bndsize[2]/2*1.1
        psfromwidth = bndsize[1]/2/(16/9)*1.1
        #print(psfromheight,psfromwidth)

        camera.SetParallelScale(max(psfromheight,psfromwidth))

        camera.SetParallelProjection(1)
        camera.SetPosition(bndcenter[0]+10000,bndcenter[1],bndcenter[2])
        camera.SetFocalPoint(bndcenter)
        ren.ResetCameraClippingRange()
        camera.SetViewUp(0,0,1)

        #ren.AddActor(pactor)
        #ren.AddActor(eactor)
        ren.SetBackground(1,1,1)
        eprop.SetEdgeColor(0,0,0)
        eprop.SetColor(0,0,0)
        wrender(1,imfile1)

        camera.SetPosition(bndcenter[0],bndcenter[1]+10000,bndcenter[2])
        psfromheight = bndsize[2]/2*1.1
        psfromwidth = bndsize[0]/2/(16/9)*1.1
        camera.SetParallelScale(max(psfromheight,psfromwidth))
        camera.SetViewUp(0,0,1)
        ren.ResetCameraClippingRange()
        imfile2 = os.path.join(imtmpdir,"image2.png")
        wrender(1,imfile2)

        camera.SetPosition(bndcenter[0],bndcenter[1],bndcenter[2]+10000)
        psfromheight = bndsize[1]/2*1.1
        psfromwidth = bndsize[0]/2/(16/9)*1.1
        camera.SetParallelScale(max(psfromheight,psfromwidth))
        camera.SetViewUp(0,1,0)
        ren.ResetCameraClippingRange()
        imfile3 = os.path.join(imtmpdir,"image3.png")
        wrender(1,imfile3)

        camera.SetPosition(bndcenter[0]+10000,bndcenter[1]+10000,bndcenter[2]+10000)
        camera.SetParallelProjection(0)
        camera.SetViewUp(0,1,0)
        vprop.SetOpacity(0.5)
        ren.ResetCamera()
        ren.ResetCameraClippingRange()
        imfile4 = os.path.join(imtmpdir,"image4.png")
        wrender(1,imfile4)
        vprop.SetOpacity(1.0)
        
        if merge:
            image1 = Image.open(imfile1)
            image2 = Image.open(imfile2)
            image3 = Image.open(imfile3)
            image4 = Image.open(imfile4)
            draw1 = ImageDraw.Draw(image4)
            draw1.text((0, 0),"X=%.1f\nY=%.1f\nZ=%.1f"%(bndsize[0],bndsize[1],bndsize[2]),(255,0,255),font=font)


            #resize, first image
            # image1 = image1.resize((1080, 1080))
            image1_size = image1.size
            new_image = Image.new('RGB',(image1_size[0]*2,image1_size[1]*2), (250,250,250))
            new_image.paste(image1,(0,0))
            new_image.paste(image2,(image1.size[0],0))
            new_image.paste(image3,(0,image1.size[1]))
            new_image.paste(image4,(image1.size[0],image1.size[1]))
            new_image.save(inazwa,"PNG")

            os.remove(imfile1)
            os.remove(imfile2)
            os.remove(imfile3)
            os.remove(imfile4)

        #sys.exit()


        '''

        ew = vtk.vtkXMLUnstructuredGridWriter()
        ew.SetInputData(ugrid2)
        ew.SetFileName(nazwa.replace(".stp",".vtu").replace("STEPY","STL_ORIENT"))
        ew.Update()
        '''



    # sys.exit()
    except:
        failist += "%s\n"%nazwa

f = open("/home/maciejm/GIT/STEPY/fail.txt","w")
f.write(failist)
f.close()
