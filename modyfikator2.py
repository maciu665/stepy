# -*- coding: utf-8 -*-
import vtk								#to trzeba doinstalowac, "pip install vtk"
import sys
import os
import math
import random
import trimesh

'''
0-nic,1-skosx1,2-skosx2,3-podciecie,4-slot,5-otwory - randint 1-10
1,2 random kat 45-75deg, 4 slot len 1-4 x 1/3 szerokosci, otwory 1/4 - 1/2 szerokosci
dla kwadratu 4xfaza, dla preta faza
'''
idir = "E:/GIT/DOKTORAT/PROCEDURAL"
odir = "E:/GIT/DOKTORAT/PROCSTL0"
tdir = "E:/GIT/DOKTORAT/PROCTOOLS"

def cleantool(idata):
    tri1 = vtk.vtkTriangleFilter()
    tri1.SetInputData(idata)
    tri1.Update()
    clean1 = vtk.vtkCleanPolyData()
    clean1.SetInputConnection(tri1.GetOutputPort())
    clean1.Update()


    return clean1.GetOutput()

def objdif(tname):
    rura = trimesh.load("E:/GIT/DOKTORAT/tbody.obj", force='mesh')
    kostka = trimesh.load("E:/GIT/DOKTORAT/%s.obj"%tname, force='mesh')
    koza = trimesh.boolean.difference([rura,kostka], engine="blender")
    e = koza.export("E:/GIT/DOKTORAT/tout.obj")

def saveobj(idata,oname):
    ow = vtk.vtkOBJWriter()
    ow.SetInputData(idata)
    ow.SetFileName("E:/GIT/DOKTORAT/%s.obj"%oname)
    ow.Update()

def savetool(idata,oname):
    ow = vtk.vtkOBJWriter()
    ow.SetInputData(idata)
    ow.SetFileName(os.path.join(tdir,oname))
    ow.Update()

pliki = os.listdir(idir)

pliki.sort()
'''
tpliki = []
for i in pliki:
    print(i)
    if i.endswith(".vtp"):
        tpliki.append(i)
'''
for plik in pliki:
    print(plik)

    #
    #plik = "pret_00250.vtp"
    #plik = "profil_00001.vtp"
    #plik = "kwadrat_00001.vtp"
    filename = os.path.join(idir,plik)
    pr = vtk.vtkXMLPolyDataReader()
    pr.SetFileName(filename)
    pr.Update()

    p = pr.GetOutput()
    pb = p.GetBounds()
    w = pb[3]-pb[2]
    h = pb[5]-pb[4]
    print(w,h)

    pc = cleantool(p)

    modint = random.randint(0,1)
    #modint = 1
    print("MODINT",modint)
    if modint:
        saveobj(pc,"tbody")
        if "kwadrat" in plik or "pret" in plik:
            mtype = random.randint(1,6)
        else:
            mtype = random.randint(1,5)
        #mtype = 7
        print("MTYPE",mtype)

        if mtype == 1:  #skos
            stype = random.randint(0,1)

            cube = vtk.vtkCubeSource()
            cube.SetXLength(500)
            cube.SetYLength(500)
            cube.SetZLength(1300)
            cube.SetCenter([250,0,0])
            cube.Update()
            cc = cleantool(cube.GetOutput())

            rangle = random.randint(10,75)

            rotate = vtk.vtkTransformFilter()
            rt = vtk.vtkTransform()
            rt.RotateY(-rangle)
            rotate.SetTransform(rt)
            rotate.SetInputData(cc)
            rotate.Update()
            ttool = rotate.GetOutput()

            if stype == 1:
                trans = vtk.vtkTransformFilter()
                tt = vtk.vtkTransform()
                dx = math.tan(math.radians(rangle))*h + 1
                tt.Translate(-dx/2,0,0)
                trans.SetTransform(tt)
                trans.SetInputData(rotate.GetOutput())
                trans.Update()
                ttool = trans.GetOutput()

            #saveobj(ttool,"ttool")
            savetool(ttool,plik.replace(".vtp",".obj"))
            #objdif("ttool")

        if mtype == 2:
            #objdif("skosx2")
            obr = vtk.vtkOBJReader()
            obr.SetFileName("E:/GIT/DOKTORAT/skosx2.obj")
            obr.Update()
            savetool(obr.GetOutput(),plik.replace(".vtp",".obj"))

        if mtype == 3:
            cube = vtk.vtkCubeSource()
            cube.SetXLength(500)
            cube.SetYLength(500)
            cube.SetZLength(500)
            cube.SetCenter([250,250,0])
            cube.Update()
            cc = cleantool(cube.GetOutput())

            rx = random.randint(10,int(w))

            trans = vtk.vtkTransformFilter()
            tt = vtk.vtkTransform()
            tt.Translate(-rx,0,0)
            trans.SetTransform(tt)
            trans.SetInputData(cc)
            trans.Update()
            ttool = trans.GetOutput()
            #saveobj(ttool,"ttool")
            savetool(ttool,plik.replace(".vtp",".obj"))
            #objdif("ttool")

        if mtype == 4:

            cube = vtk.vtkCubeSource()
            cube.SetXLength(100)
            cube.SetYLength(w/random.randint(3,4))
            cube.SetZLength(500)
            cube.SetCenter([50,0,0])
            cube.Update()
            cc = cleantool(cube.GetOutput())

            rx = random.randint(2,10)/10*w

            trans = vtk.vtkTransformFilter()
            tt = vtk.vtkTransform()
            tt.Translate(-rx,0,0)
            trans.SetTransform(tt)
            trans.SetInputData(cc)
            trans.Update()
            ttool = trans.GetOutput()
            #saveobj(ttool,"ttool")
            savetool(ttool,plik.replace(".vtp",".obj"))
            #objdif("ttool")

        if mtype == 5:

            cyl = vtk.vtkCylinderSource()
            rad = w/random.randint(6,8)
            cyl.SetRadius(rad)
            cyl.SetHeight(500)
            cyl.SetCenter([-3*rad,0,0])
            cyl.SetResolution(180)
            cyl.Update()
            cc = cleantool(cyl.GetOutput())

            rozstaw = random.randint(4,10)*rad
            #print(cc)

            app = vtk.vtkAppendFilter()
            app.AddInputData(cc)
            for k in range(random.randint(0,5)):
                trans = vtk.vtkTransformFilter()
                tt = vtk.vtkTransform()
                tt.Translate(-rozstaw,0,0)
                trans.SetTransform(tt)
                trans.SetInputData(cc)
                trans.Update()
                app.AddInputData(trans.GetOutput())
            app.Update()
            #print(app.GetOutput())
            gf = vtk.vtkGeometryFilter()
            gf.SetInputData(app.GetOutput())
            gf.Update()
            ttool = gf.GetOutput()
            #saveobj(ttool,"ttool")
            #objdif("ttool")
            savetool(ttool,plik.replace(".vtp",".obj"))

        if mtype == 6:
            if "pret" in plik:
                odstep = random.randint(0,1)
                #odstep = 1
                if odstep:
                    obr = vtk.vtkOBJReader()
                    obr.SetFileName("E:/GIT/DOKTORAT/rfaza.obj")
                    obr.Update()
                    trans = vtk.vtkTransformFilter()
                    tt = vtk.vtkTransform()
                    tt.Translate(w/random.randint(3,4),0,0)
                    trans.SetTransform(tt)
                    trans.SetInputData(obr.GetOutput())
                    trans.Update()
                    #saveobj(trans.GetOutput(),"ttool")
                    #objdif("ttool")
                    savetool(ttool,plik.replace(".vtp",".obj"))
                else:
                    obr = vtk.vtkOBJReader()
                    obr.SetFileName("E:/GIT/DOKTORAT/rfaza.obj")
                    obr.Update()
                    savetool(obr.GetOutput(),plik.replace(".vtp",".obj"))
            else:
                odstep = random.randint(0,1)
                #odstep = 1
                if odstep:
                    obr = vtk.vtkOBJReader()
                    obr.SetFileName("E:/GIT/DOKTORAT/kfaza.obj")
                    obr.Update()
                    trans = vtk.vtkTransformFilter()
                    tt = vtk.vtkTransform()
                    tt.Translate(w/random.randint(3,4),0,0)
                    trans.SetTransform(tt)
                    trans.SetInputData(obr.GetOutput())
                    trans.Update()
                    #saveobj(trans.GetOutput(),"ttool")
                    #objdif("ttool")
                    savetool(ttool,plik.replace(".vtp",".obj"))
                else:
                    obr = vtk.vtkOBJReader()
                    obr.SetFileName("E:/GIT/DOKTORAT/rfaza.obj")
                    obr.Update()
                    savetool(obr.GetOutput(),plik.replace(".vtp",".obj"))
        '''
        obr = vtk.vtkOBJReader()
        obr.SetFileName("E:/GIT/DOKTORAT/tout.obj")
        obr.Update()
        tout = obr.GetOutput()
        if "pret" in plik or "rura" in plik:
            rotate = vtk.vtkTransformFilter()
            rt = vtk.vtkTransform()
            rt.RotateX(random.randint(1,120))
            rotate.SetTransform(rt)
            rotate.SetInputData(tout)
            rotate.Update()
            tout = rotate.GetOutput()
        '''
        sw = vtk.vtkSTLWriter()
        sw.SetInputData(pc)
        sw.SetFileName(os.path.join(odir,plik.replace(".vtp",".stl")))
        sw.Update()


    else:
        sw = vtk.vtkSTLWriter()
        sw.SetInputData(pc)
        sw.SetFileName(os.path.join(odir,plik.replace(".vtp",".stl")))
        sw.Update()
    #sys.exit()
