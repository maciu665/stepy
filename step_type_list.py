# -*- coding: utf-8 -*-
#!/usr/bin/python
########################################
##  author: maciu665
########################################

#IMPORTY
import cv2
import os
from pathlib import Path
import random, string
import sys
import json

global punkt, nooks, oks, ims, halfsize
global imw, imh
nooks = 0
oks = 0
halfsize = 32

imdir = "/home/maciejm/GIT/STEPY/IMG/"
stepdir = "/home/maciejm/GIT/STEPY/PARTY0/"
mvdir = "/home/maciejm/GIT/STEPY/PARTY2"
rmfile = "/home/maciejm/GIT/STEPY/rmfile.sh"
mvfile = "/home/maciejm/GIT/STEPY/mvfile.sh"

#print(getrname())
pliki = []
tpliki = os.listdir(imdir)
for i in tpliki:
    pliki.append(os.path.join(imdir, i))
print(len(pliki))
pnum = 0
ims = 1
plik = pliki[pnum]
print(plik)
image = cv2.imread(plik)

(imw,imh,imc) = image.shape
print(imw,imh,imc)

#sys.exit()

###############

cv2.namedWindow("image")
#cv2.setMouseCallback("image", click)

sets = []

rmtxt = "#!/bin/sh\n"
mvtxt = "#!/bin/sh\n"

while True:
    # display the image and wait for a keypress
    cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    else:
        goon = 0
        typ = None
        if key == ord("i"):
            print("inne")
            print(pliki[pnum])
            goon = 1
        elif key == ord("b"):
            typ = "BLACHY"
            goon = 2
        elif key == ord("c"):
            typ = "CEOWNIKI"
            goon = 2
        elif key == ord("d"):
            typ = "DWUTEOWNIKI"
            goon = 2
        elif key == ord("f"):
            typ = "FLANSZE"
            goon = 2
        elif key == ord("k"):
            typ = "KATOWNIKI"
            goon = 2
        elif key == ord("n"):
            typ = "NAKRETKI"
            goon = 2
        elif key == ord("h"):
            typ = "PLASKOWNIKI"
            goon = 2
        elif key == ord("s"):
            typ = "PODKLADKI"
            goon = 2
        elif key == ord("o"):
            typ = "PRETY_OKRAGLE"
            goon = 2
        elif key == ord("p"):
            typ = "PROFILE"
            goon = 2
        elif key == ord("r"):
            typ = "RURY"
            goon = 2
        elif key == ord("z"):
            typ = "SRUBY"
            goon = 2
        

        if goon:
            rmline = "rm %s\n"%pliki[pnum]
            rmtxt += rmline
            if goon == 2:
                mvline = "mv %s %s\n"%(pliki[pnum].replace(imdir,stepdir).replace("png","stp"),os.path.join(mvdir,typ))
                mvtxt += mvline

            pnum += 1
            image = cv2.imread(pliki[pnum])
            ims += 1


f = open(rmfile, 'w')
f.write(rmtxt)
f.close()

f = open(mvfile, 'w')
f.write(mvtxt)
f.close()

cv2.destroyAllWindows()
