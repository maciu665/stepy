import os
import sys
import shutil

idir = "/home/maciejm/PHD/PUBLIKACJA_02/299bg/"
# idir = "/home/maciejm/PHD/PUBLIKACJA_02/images30/res299/RENDER_SIMPLE"
idir = "/home/maciejm/PHD/PUBLIKACJA_02/images30/res299/HIDDEN_BLACK_BG"
# idir = "/home/maciejm/PHD/PUBLIKACJA_02/images30/res299/SHADED_BLACK_BG"
# idir = "/home/maciejm/PHD/PUBLIKACJA_02/images30/res299/WIREFRAME_BLACK_BG"
# idir = "/home/maciejm/PHD/PUBLIKACJA_02/images30/res299/FEATURE_BLACK_BG"
# idir = "/home/maciejm/PHD/PUBLIKACJA_02/images30/res299/OVERLAY_BLACK_BG"
# idir = "/home/maciejm/PHD/PUBLIKACJA_02/images30/res299/WNOAA_BLACK_BG"
# idir = "/home/maciejm/PHD/PUBLIKACJA_02/images30/res299/SNOAA_BLACK_BG"

nazwy = ["C-BEAM","I-BEAM","L-BEAM","FLAT-BAR","SQUARE-BAR","ROUND-BAR","HOLLOW-SECTION","PIPE"]
old_nazwy = ["ceownik","dwuteownik","katownik","plaskownik","kwadratowy","okragly","profil","rura"]

for k in nazwy:
    try:
        os.mkdir(os.path.join(idir,k))
    except:
        print("jest")

###

tlist = os.listdir(idir)
list = []
for i in tlist:
    if i.endswith("png"):
        list.append(i)
list.sort()
print(list[:10])

#sys.exit()


'''
imnum = 0
for part in range(250):
    for type in range(8):
        for view in range(4):
            print(part,nazwy[type],view, "-", list[imnum])
            nname = nazwy[type]+"_"+str(part+1).zfill(5)+"-view"+str(view+1).zfill(2)
            print(nname)
            shutil.copy(os.path.join(idir,list[imnum]),os.path.join(os.path.join(idir,nazwy[type]),nname+".png"))
            imnum += 1
    sys.exit()
'''




for i in list:
    namestr = i.split("_")[0]
    nazwa = nazwy[old_nazwy.index(namestr)]
    nname = i.replace(namestr,nazwa)
    print(nname)
    shutil.copy(os.path.join(idir,i),os.path.join(os.path.join(idir,nazwa),nname))
    #shutil

