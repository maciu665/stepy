import trimesh

#f = open("E:/GIT/DOKTORAT/rura.obj","r")
#rura = trimesh.exchange.obj.load_obj(f)
'''
0-nic,1-skosx1,2-skosx2,3-podciecie,4-slot,5-otwory - randint 1-10
1,2 random kat 45-75deg, 4 slot len 1-4 x 1/3 szerokosci, otwory 1/4 - 1/2 szerokosci
dla kwadratu 4xfaza, dla preta faza
'''



rura = trimesh.load("E:/GIT/DOKTORAT/rura.obj", force='mesh')
kostka = trimesh.load("E:/GIT/DOKTORAT/kfaza.obj", force='mesh')
koza = trimesh.boolean.difference([rura,kostka], engine="blender")

e = koza.export("E:/GIT/DOKTORAT/cutkfaza.obj")
#f.close()
print(koza)
