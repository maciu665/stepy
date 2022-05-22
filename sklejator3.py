# -*- coding: utf-8 -*-
#!/usr/bin/python
#TODO
#tworzenie nowego vml
#załączone pliki?
# powrót do rozmiaru po screenshocie
#
#IMPORTY
import vtk
import os
import sys
import shutil
import time
import random


nazwa = "E:/GIT/DOKTORAT/rury3.stl"
nazwaclip = "E:/GIT/DOKTORAT/rury3clip.stl"
nazwatool = "E:/GIT/DOKTORAT/rury3tool.stl"

stepdir = "/home/maciejm/GIT/DOKTORAT/STL_ORIENT2/"
stepdir = "E:/GIT/DOKTORAT/PROCSTL0/"
tooldir = "E:/GIT/DOKTORAT/PROCTOOLS/"

tsteplista = os.listdir(stepdir)
tsteplista.sort()
# print(tsteplista)
steplista = []

for i in tsteplista:
    if "rur" in i:
        steplista.append(i)

print(steplista)
# sys.exit()

appn = vtk.vtkAppendFilter()
appnclip = vtk.vtkAppendFilter()
appntool = vtk.vtkAppendFilter()


for i in range(0,len(steplista[:])):
#for i in range(0,3):
    print("i",i)
    stlr = vtk.vtkSTLReader()
    stlr.SetFileName(os.path.join(stepdir,steplista[i]))
    stlr.Update()

    rotate = vtk.vtkTransformFilter()
    rt = vtk.vtkTransform()
    rt.RotateZ(180)
    rotate.SetTransform(rt)
    rotate.SetInputData(stlr.GetOutput())
    rotate.Update()
    sp = rotate.GetOutput()

    spb = sp.GetBounds()
    print(spb)
    maxdim = max(spb[3]-spb[2],spb[5]-spb[4])
    print(maxdim,4*maxdim)
    print(spb[1] > (2*maxdim))
    if spb[1] > (2*maxdim):
        tx = (2*maxdim) - spb[1]
    else:
        tx = 0
    print(tx)
    print("spb", spb)
    #sys.exit()




    transowanie = vtk.vtkTransformFilter()
    trans = vtk.vtkTransform()
    # trans.Scale(1, -1, 1)
    trans.Translate(tx,0,i*1000-spb[4])
    transowanie.SetTransform(trans)
    transowanie.SetInputData(sp)
    transowanie.Update()
    stl = transowanie.GetOutput()
    tbnds = stl.GetBounds()
    print("tbnds",tbnds)
    appn.AddInputData(stl)


    if os.path.exists(os.path.join(tooldir,steplista[i].replace("stl","obj"))):
        obr = vtk.vtkOBJReader()
        obr.SetFileName(os.path.join(tooldir,steplista[i].replace("stl","obj")))
        obr.Update()
        ttool = obr.GetOutput()

        if "pret" in steplista[i] or "rura" in steplista[i]:
            rotate = vtk.vtkTransformFilter()
            rt = vtk.vtkTransform()
            rt.RotateX(random.randint(1,120))
            rotate.SetTransform(rt)
            rotate.SetInputData(ttool)
            rotate.Update()
            ttool = rotate.GetOutput()

        ttransowanie = vtk.vtkTransformFilter()
        ttrans = vtk.vtkTransform()
        # trans.Scale(1, -1, 1)
        ttrans.Translate(tbnds[1],0,i*1000-spb[4])
        ttransowanie.SetTransform(ttrans)
        ttransowanie.SetInputData(ttool)
        ttransowanie.Update()
        tool = ttransowanie.GetOutput()
        #tbnds = stl.GetBounds()
        #print("tbnds",tbnds)
        appntool.AddInputData(tool)

    if tx != 0:
        cplane = vtk.vtkPlane()
        cplane.SetOrigin(-2*maxdim,0,0)
        cplane.SetNormal(1,0,0)

        clip = vtk.vtkClipDataSet()
        clip.SetClipFunction(cplane)
        clip.SetInputData(transowanie.GetOutput())
        clip.SetValue(0.0)
        clip.GenerateClippedOutputOn()
        clip.Update()
        appnclip.AddInputData(clip.GetOutput())
    else:
        appnclip.AddInputData(stl)



appn.Update()
appnclip.Update()
appntool.Update()

skalowanie = vtk.vtkTransformFilter()
skala = vtk.vtkTransform()
skala.Scale(0.001,0.001,0.001)
skalowanie.SetTransform(skala)
skalowanie.SetInputData(appn.GetOutput())
skalowanie.Update()

gf = vtk.vtkGeometryFilter()
gf.SetInputConnection(skalowanie.GetOutputPort())
gf.Update()
print(gf.GetOutput().GetBounds())

stlw = vtk.vtkSTLWriter()
stlw.SetInputConnection(gf.GetOutputPort())
stlw.SetFileTypeToBinary()
stlw.SetFileName(nazwa)
stlw.Update()

skalowanie.SetInputData(appnclip.GetOutput())
skalowanie.Update()
gf.Update()

stlw = vtk.vtkSTLWriter()
stlw.SetInputConnection(gf.GetOutputPort())
stlw.SetFileTypeToBinary()
stlw.SetFileName(nazwaclip)
stlw.Update()


skalowanie.SetInputData(appntool.GetOutput())
skalowanie.Update()
gf2 = vtk.vtkGeometryFilter()
gf2.SetInputConnection(skalowanie.GetOutputPort())
gf2.Update()

stlw = vtk.vtkSTLWriter()
stlw.SetInputConnection(gf2.GetOutputPort())
stlw.SetFileTypeToBinary()
stlw.SetFileName(nazwatool)
stlw.Update()
