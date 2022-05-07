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

nazwa = "E:/GIT/DOKTORAT/plaskowniki3.stl"
nazwaclip = "E:/GIT/DOKTORAT/plaskowniki3clip.stl"

stepdir = "/home/maciejm/GIT/DOKTORAT/STL_ORIENT2/"
stepdir = "E:/GIT/DOKTORAT/STL_ORIENT2/"

tsteplista = os.listdir(stepdir)
tsteplista.sort()
# print(tsteplista)
steplista = []

for i in tsteplista:
    if "pla" in i:
        steplista.append(i)

print(steplista)
# sys.exit()

appn = vtk.vtkAppendFilter()
appnclip = vtk.vtkAppendFilter()


for i in range(0,len(steplista[:])):
    print("i",i)
    stlr = vtk.vtkSTLReader()
    stlr.SetFileName(os.path.join(stepdir,steplista[i]))
    stlr.Update()

    sp = stlr.GetOutput()

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
    # sys.exit()




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
