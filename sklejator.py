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

nazwa = "/home/maciejm/GIT/DOKTORAT/katowniki.stl"
nazwa = "E:/GIT/DOKTORAT/dwuteowniki2.stl"

stepdir = "/home/maciejm/GIT/DOKTORAT/STL_ORIENT2/"
stepdir = "E:/GIT/DOKTORAT/STL_ORIENT2/"

tsteplista = os.listdir(stepdir)
tsteplista.sort()
# print(tsteplista)
steplista = []

for i in tsteplista:
    if "dwu" in i:
        steplista.append(i)

print(steplista)
# sys.exit()

appn = vtk.vtkAppendFilter()


stlr = vtk.vtkSTLReader()
stlr.SetFileName(os.path.join(stepdir,steplista[0]))
stlr.Update()

sp = stlr.GetOutput()

if

sys.exit()

appn.AddInputData(sp)




for i in range(1,len(steplista[:])):
    print("i",i)
    stlr = vtk.vtkSTLReader()
    stlr.SetFileName(os.path.join(stepdir,steplista[i]))
    stlr.Update()

    sp = stlr.GetOutput()



    transowanie = vtk.vtkTransformFilter()
    trans = vtk.vtkTransform()
    # trans.Scale(1, -1, 1)
    trans.Translate(0,0,i*1000)
    transowanie.SetTransform(trans)
    transowanie.SetInputData(sp)
    transowanie.Update()
    stl = transowanie.GetOutput()
    tbnds = stl.GetBounds()
    print(tbnds)

    appn.AddInputData(stl)

appn.Update()

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

#bnds = sp.GetBounds()
# cob = [(bnds[0]+bnds[1])/2,(bnds[2]+bnds[3])/2,(bnds[4]+bnds[5])/2]
#cob = [(bnds[0]+bnds[1])/2,(bnds[2]+bnds[3])/2,bnds[4]]


# print(tbnds)

# print(transowanie.GetOutput())

stlw = vtk.vtkSTLWriter()
stlw.SetInputConnection(gf.GetOutputPort())
stlw.SetFileTypeToBinary()
stlw.SetFileName(nazwa)
stlw.Update()
