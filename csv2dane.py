import wx
import vtk
import builtins
import os
import sys
import numpy as np
import csv
from statistics import mode,multimode

f = open("E:/GIT/DOKTORAT/topolista.csv","r")
lista = f.read().splitlines()
f.close()

with open("E:/GIT/DOKTORAT/topolista.csv") as f:
    reader = csv.reader(f)
    data = list(reader)

print(data)
fulltopolista = []
for i in data:
    topo = [i[0]]
    for k in range(1,len(i)):
        topo.append(int(i[k]))
    fulltopolista.append(topo)
print(fulltopolista)

typy = {}
for i in fulltopolista:
    if i[0] in typy.keys():
        typy[i[0]][0] += 1
        #curlista = typy[i[0]][1]
        for w in range(1,len(i)):
            #curlista[w] += i[1+w]
            typy[i[0]][w].append(i[w])
    else:
        #typy[i[0]] = [1,i[1:]]
        ntyp = [1]
        for g in range(1,len(i)):
            ntyp.append([i[g]])
        typy[i[0]] = ntyp

print(typy)

################################################################################

statystyka = []

for k in typy.keys():
    print(k)
    statystyka.append([k,"faces","edges","verts","f_plane","f_cylinder","f_other","e_line","e_circle","e_ellipse","e_other","e_c||e","euler"])
    stat_av = ["average"]
    for data in typy[k][1:]:
        stat_av.append(sum(data)/typy[k][0])
    statystyka.append(stat_av)

    stat_min = ["min"]
    for data in typy[k][1:]:
        stat_min.append(min(data))
    statystyka.append(stat_min)

    stat_max = ["max"]
    for data in typy[k][1:]:
        stat_max.append(max(data))
    statystyka.append(stat_max)

    stat_dom = ["mode"]
    for data in typy[k][1:]:
        try:
            stat_dom.append(mode(data))
        except:
            stat_dom.append(str(multimode(data)))
    statystyka.append(stat_dom)
    statystyka.append([" "," "])

topostatcsv = ""
for l in statystyka:
    linia = ""
    for k in l:
        linia += str(k)+","
    linia = linia[:-1]
    linia += "\n"
    topostatcsv += linia

f = open('E:/GIT/DOKTORAT/topostat.csv', 'w')
f.write(topostatcsv)
f.close()

print(statystyka)
