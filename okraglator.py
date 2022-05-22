# -*- coding: utf-8 -*-
import vtk								#to trzeba doinstalowac, "pip install vtk"
import sys
import os
import math
import random

f = open("okragle.csv","r")
linie = f.read().splitlines()
f.close()
print(linie)
#print(linia0)
#sys.exit()

prety = []


for i in linie:
    prety.append(int(i))

print(prety)

# sys.exit()
#print(profile[250])
#print(profile[0])
for k in range(250):
    knum = k
    while knum > len(prety)-1:
        knum -= len(prety)
        # print("knum", knum)

    print(k,prety[knum])
    tk = prety[knum]

    vpts = vtk.vtkPoints()
    u = vtk.vtkUnstructuredGrid()
    vpts.InsertNextPoint([0,0,0])

    r = prety[knum]/2
    for a in range(360):
        vpts.InsertNextPoint([0,math.sin(math.radians(a))*r,math.cos(math.radians(a))*r])

    for c in range(360):
        pointIds = vtk.vtkIdList()
        pointIds.InsertId(0, 0)
        pointIds.InsertId(1, c+1)
        if c < 359:
            pointIds.InsertId(2, c+2)
        else:
            pointIds.InsertId(2, 1)
        seid = u.InsertNextCell(5, pointIds)


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

    elen = random.randint(150,3000)

    ex = vtk.vtkLinearExtrusionFilter()
    ex.SetInputData(skalowanie.GetOutput())
    ex.SetExtrusionTypeToVectorExtrusion()
    ex.SetVector(-elen, 0, 0)
    ex.Update()

    uw  = vtk.vtkXMLPolyDataWriter()
    uw.SetInputData(ex.GetOutput())
    uw.SetFileName("E:/GIT/DOKTORAT/PROCEDURAL/pret_%s.vtp"%(str(k+1).zfill(5)))
    uw.Update()
