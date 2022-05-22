# -*- coding: utf-8 -*-
import vtk								#to trzeba doinstalowac, "pip install vtk"
import sys
import os
import math
import random

f = open("kwadratowe.csv","r")
linie = f.read().splitlines()
f.close()
print(linie)
#print(linia0)
#sys.exit()

kwadraty = []


for i in linie:
    kwadraty.append(int(i))

print(kwadraty)


#print(profile[250])
#print(profile[0])
for k in range(250):
    knum = k
    while knum > len(kwadraty)-1:
        knum -= len(kwadraty)
        # print("knum", knum)

    print(k,kwadraty[knum])
    tk = kwadraty[knum]

    vpts = vtk.vtkPoints()
    u = vtk.vtkUnstructuredGrid()
    vpts.InsertNextPoint([0,tk/2,tk/2])
    vpts.InsertNextPoint([0,tk/-2,tk/2])
    vpts.InsertNextPoint([0,tk/-2,tk/-2])
    vpts.InsertNextPoint([0,tk/2,tk/-2])

    pointIds = vtk.vtkIdList()
    for i in range(4):
        pointIds.InsertId(i,i)
    seid = u.InsertNextCell(9, pointIds)
    # print(vpts)
    u.SetPoints(vpts)

    gf = vtk.vtkGeometryFilter()
    gf.SetInputData(u)
    gf.Update()

    skalowanie = vtk.vtkTransformFilter()
    skala = vtk.vtkTransform()
    skala.Scale(1,1,1)
    skalowanie.SetTransform(skala)
    skalowanie.SetInputData(gf.GetOutput())
    skalowanie.Update()

    elen = random.randint(250,3000)

    ex = vtk.vtkLinearExtrusionFilter()
    ex.SetInputData(skalowanie.GetOutput())
    ex.SetExtrusionTypeToVectorExtrusion()
    ex.SetVector(-elen, 0, 0)
    ex.Update()

    uw  = vtk.vtkXMLPolyDataWriter()
    uw.SetInputData(ex.GetOutput())
    uw.SetFileName("E:/GIT/DOKTORAT/PROCEDURAL/kwadrat_%s.vtp"%(str(k+1).zfill(5)))
    uw.Update()
