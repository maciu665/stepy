# -*- coding: utf-8 -*-
import vtk								#to trzeba doinstalowac, "pip install vtk"
import sys
import os
import math
import random

plik = "E:/GIT/DOKTORAT/rury3a.stl"
sr = vtk.vtkSTLReader()
sr.SetFileName(plik)
sr.Update()
odir = "E:/GIT/DOKTORAT/STL_PROC"

s = sr.GetOutput()
print(s.GetBounds())


for p in range(250):
    transowanie = vtk.vtkTransformFilter()
    trans = vtk.vtkTransform()
    trans.Translate(0,0,-1*p)
    transowanie.SetTransform(trans)
    transowanie.SetInputData(s)
    transowanie.Update()

    st = transowanie.GetOutput()

    cplane = vtk.vtkPlane()
    cplane.SetOrigin(0,0,-0.5)
    cplane.SetNormal(0,0,1)

    clip = vtk.vtkClipDataSet()
    clip.SetClipFunction(cplane)
    clip.SetInputData(st)
    clip.SetValue(0.0)
    clip.GenerateClippedOutputOn()
    clip.Update()

    cplane1 = vtk.vtkPlane()
    cplane1.SetOrigin(0,0,0.5)
    cplane1.SetNormal(0,0,-1)

    clip1 = vtk.vtkClipDataSet()
    clip1.SetClipFunction(cplane1)
    clip1.SetInputData(clip.GetOutput())
    clip1.SetValue(0.0)
    clip1.GenerateClippedOutputOff()
    clip1.Update()

    sc = clip1.GetOutput()
    print(sc.GetBounds())

    gf2 = vtk.vtkGeometryFilter()
    gf2.SetInputConnection(clip1.GetOutputPort())
    gf2.Update()


    sw = vtk.vtkSTLWriter()
    sw.SetFileName(os.path.join(odir,"rura_%s.stl"%(str(p+1).zfill(5))))
    sw.SetInputData(gf2.GetOutput())
    sw.Update()
