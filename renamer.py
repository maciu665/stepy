import os
import sys
import shutil


nazwa = "E:/GIT/DOKTORAT/ASSES/F4100-001-001.stp"

f = open(nazwa,"r")
stp = f.read().splitlines()
f.close()
print(len(stp))

nazwy = {}

for k in range(len(stp)-1):
    line = stp[k]
    if "=PRODUCT('" in line:
        if line.endswith(","):
            line += stp[k+1]
        # print(line)
        lista = line.split("=PRODUCT(")[-1].split(",")
        index = lista[1].replace("'","")
        nname = lista[2].replace("'","")
        if nname != "" and nname != "$":
            nazwy[index] = nname
