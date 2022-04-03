import wx
import vtk
import builtins
import os
import sys

abcdir = "E:/GIT/DOKTORAT/ABC0000"

abclista = os.listdir(abcdir)
print(abclista)

failist = ""

num = 0

for s in abclista:
    nazwa = os.path.join(abcdir,s)
    # print(nazwa)
    if nazwa.endswith("yml"):
        print(nazwa)
        f = open(nazwa,"r")
        flista = f.read().splitlines()
        f.close()
        for line in flista:
            if line.startswith("name"):
                nname = line.split(": ")[-1]
                print(nname)
                try:
                    os.rename(nazwa.replace("yml","step").replace("metadata","step"), os.path.join(abcdir,"%s_%s.stp"%(nname,str(num).zfill(6))))
                except:
                    pass


                num += 1
