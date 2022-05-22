# -*- coding: utf-8 -*-
import vtk								#to trzeba doinstalowac, "pip install vtk"
import sys
import os
import math
import random

f = open("rury.csv","r")
linie = f.read().splitlines()
f.close()
print(linie)

linia0 = linie[:1][0]
linie = linie[1:]

#print(linie)
#print(linia0)
# sys.exit()

rury = []


for i in linie:
    print(i)
    linia = i.split(",")
    diam = float(linia[0])
    # print(dimx,dimy)
    for j in range(1,len(linia)):
        r = float(linia[j])
        # print(r)
        if r:
            rury.append([diam,float(linia0.split(",")[j])])

print(rury[230])
print(rury[480])
print(rury[0])
print(len(rury))
print(rury)
#profile = profile[:250]
rury = rury[230::2]
print(len(rury))
print(rury)
#sys.exit()


print(len(rury))
for p in range(len(rury)):
    pr = rury[p]
    print(pr)

    r1 = pr[0]/2
    r2 = pr[0]/2-pr[1]

    vpts = vtk.vtkPoints()
    u = vtk.vtkUnstructuredGrid()
    for a in range(360):
        vpts.InsertNextPoint([0,math.sin(math.radians(a))*r2,math.cos(math.radians(a))*r2])
        vpts.InsertNextPoint([0,math.sin(math.radians(a))*r1,math.cos(math.radians(a))*r1])
    # print(vpts)
    u.SetPoints(vpts)

    for c in range(360):
        pointIds = vtk.vtkIdList()
        pointIds.InsertId(0, c*2)
        pointIds.InsertId(1, c*2+1)
        if c<359:
            pointIds.InsertId(2, c*2+3)
            pointIds.InsertId(3, c*2+2)
        else:
            pointIds.InsertId(2, 1)
            pointIds.InsertId(3, 0)
        seid = u.InsertNextCell(9, pointIds)
    # print(u)

    gf = vtk.vtkGeometryFilter()
    gf.SetInputData(u)
    gf.Update()

    skalowanie = vtk.vtkTransformFilter()
    skala = vtk.vtkTransform()
    skala.Scale(1,1,1)
    skalowanie.SetTransform(skala)
    skalowanie.SetInputData(gf.GetOutput())
    skalowanie.Update()

    elen = random.randint(500,3000)

    ex = vtk.vtkLinearExtrusionFilter()
    ex.SetInputData(skalowanie.GetOutput())
    ex.SetExtrusionTypeToVectorExtrusion()
    ex.SetVector(-elen, 0, 0)
    ex.Update()

    uw  = vtk.vtkXMLPolyDataWriter()
    uw.SetInputData(ex.GetOutput())
    uw.SetFileName("E:/GIT/DOKTORAT/PROCEDURAL/rury_%s.vtp"%(str(p+1).zfill(5)))
    uw.Update()

    # sys.exit()

































sys.exit()
