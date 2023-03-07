import cv2
from PIL import Image
import sys
import os

isize = 299
idirname = "images3"

ifolderSB = "/home/maciejm/PHD/PUBLIKACJA_02/%s/res%i/SHADED_BLACK_BG/"%(idirname,isize)
ifolderWB = "/home/maciejm/PHD/PUBLIKACJA_02/%s/res%i/FEATURE_BLACK_BG/"%(idirname,isize)
ifolderFB = "/home/maciejm/PHD/PUBLIKACJA_02/%s/res%i/OVERLAY_BLACK_BG/"%(idirname,isize)
ifolderC1 = "/home/maciejm/PHD/PUBLIKACJA_02/%s/res%i/COMP3_BLACK_BG/"%(idirname,isize)

try:
    os.mkdir(ifolderC1)
except:
    print("jest")

import glob

shfiles = []
for file in glob.glob("%s/*/*.png"%ifolderSB):
    shfiles.append(file)

for folder in glob.glob("%s/*"%ifolderSB):
    #print(folder)
    try:
        os.mkdir(folder.replace("SHADED","COMP3"))
    except:
        print("jest")

#print(shfiles[0])

print(os.path.dirname(shfiles[0]))
#sys.exit()
for shfile in shfiles:
    #shfile = shfiles[0]
    wffile = shfile.replace("SHADED","FEATURE")
    fbfile = shfile.replace("SHADED","OVERLAY")
    c1file = shfile.replace("SHADED","COMP3")

    shimage = cv2.imread(shfile)
    wfimage = cv2.imread(wffile)
    fbimage = cv2.imread(fbfile)

    (shB, shG, shR) = cv2.split(shimage)
    (wfB, wfG, wfR) = cv2.split(wfimage)
    (fbB, fbG, fbR) = cv2.split(fbimage)

    merged = cv2.merge([shB, wfG, fbR])
    #cv2.imshow("Merged", merged)
    #cv2.waitKey(0)
    #sys.exit()
    print(c1file)

    cv2.imwrite(c1file, merged)
