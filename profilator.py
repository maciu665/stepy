# -*- coding: utf-8 -*-
import vtk								#to trzeba doinstalowac, "pip install vtk"
import sys
import os
import math
import random

f = open("profile.csv","r")
linie = f.read().splitlines()
f.close()
print(linie)

linia0 = linie[:1][0]
linie = linie[1:]

#print(linie)
#print(linia0)
# sys.exit()

profile = []


for i in linie:
    linia = i.split(",")
    dims = linia[0].split("x")
    dimx,dimy = int(dims[0]),int(dims[1])
    # print(dimx,dimy)
    for j in range(1,len(linia)):
        r = float(linia[j])
        # print(r)
        if r:
            # print(dimx,dimy,r,float(linia0.split(",")[j]))
            profile.append([dimx,dimy,r,float(linia0.split(",")[j])])

#print(profile[250])
#print(profile[0])
profile = profile[:250]

print(len(profile))
for p in range(len(profile)):
    pr = profile[p]
    print(pr)
    rot = random.randint(0,1)
    if rot:
        nc = [pr[1]/2-pr[2],pr[0]/2-pr[2]]
    else:
        nc = [pr[0]/2-pr[2],pr[1]/2-pr[2]]
    r1 = pr[2]-pr[3]
    r2 = pr[2]

    vpts = vtk.vtkPoints()
    u = vtk.vtkUnstructuredGrid()
    for a in range(91):
        vpts.InsertNextPoint([0,nc[0]+math.sin(math.radians(a))*r2,nc[1]+math.cos(math.radians(a))*r2])
        vpts.InsertNextPoint([0,nc[0]+math.sin(math.radians(a))*r1,nc[1]+math.cos(math.radians(a))*r1])
    # print(vpts)
    u.SetPoints(vpts)

    for c in range(90):
        pointIds = vtk.vtkIdList()
        pointIds.InsertId(0, c*2)
        pointIds.InsertId(1, c*2+1)
        pointIds.InsertId(2, c*2+3)
        pointIds.InsertId(3, c*2+2)
        seid = u.InsertNextCell(9, pointIds)
    # print(u)


    app = vtk.vtkAppendFilter()
    app.AddInputData(u)
    for m in range(3):
        transowanie = vtk.vtkTransformFilter()
        trans = vtk.vtkTransform()
        if m == 0:
            trans.Scale(1,-1,1)
        elif m == 1:
            trans.Scale(1,1,-1)
        else:
            trans.Scale(1,-1,-1)
        transowanie.SetTransform(trans)
        transowanie.SetInputData(u)
        transowanie.Update()
        #ugrid = transowanie.GetOutput()
        app.AddInputData(transowanie.GetOutput())

    fs = [[180,181,545,544],[365,364,546,547],[726,727,363,362],[183,182,0,1]]

    app.Update()
    for f in fs:
        pointIds = vtk.vtkIdList()
        pointIds.InsertId(0, f[0])
        pointIds.InsertId(1, f[1])
        pointIds.InsertId(2, f[2])
        pointIds.InsertId(3, f[3])
        seid = app.GetOutput().InsertNextCell(9, pointIds)

    gf = vtk.vtkGeometryFilter()
    gf.SetInputData(app.GetOutput())
    gf.Update()

    skalowanie = vtk.vtkTransformFilter()
    skala = vtk.vtkTransform()
    skala.Scale(1,1,1)
    skalowanie.SetTransform(skala)
    skalowanie.SetInputData(gf.GetOutput())
    skalowanie.Update()

    elen = random.randint(600,3000)

    ex = vtk.vtkLinearExtrusionFilter()
    ex.SetInputData(skalowanie.GetOutput())
    ex.SetExtrusionTypeToVectorExtrusion()
    ex.SetVector(-elen, 0, 0)
    ex.Update()

    uw  = vtk.vtkXMLPolyDataWriter()
    uw.SetInputData(ex.GetOutput())
    uw.SetFileName("E:/GIT/DOKTORAT/PROCEDURAL/profil_%s.vtp"%(str(p+1).zfill(5)))
    uw.Update()

    # sys.exit()

































sys.exit()
