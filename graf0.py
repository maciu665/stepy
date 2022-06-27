import urllib.request
import io, zipfile
import networkx as nx
import matplotlib as mpl
import matplotlib.pyplot as plt
import sys
'''
url = "http://www-personal.umich.edu/~mejn/netdata/football.zip"

sock = urllib.request.urlopen(url)  # open URL
s = io.BytesIO(sock.read())  # read into BytesIO "file"
sock.close()

zf = zipfile.ZipFile(s)  # zipfile object
txt = zf.read("football.txt").decode()  # read info file
gml = zf.read("football.gml").decode()  # read gml data
print(gml)
#sys.exit()
# throw away bogus first line with # from mejn files
gml = gml.split("\n")[1:]
'''

gml = 'graph\n[\ndirected 1\nnode\n[\nid 0\nlabel "koza"\nvalue 2\n]\nnode\n[\nid 1\nlabel "chomik"\nvalue 5\n]\nedge\n[\nsource 0\ntarget 1\n]\n]'

gml = gml.split("\n")

G = nx.parse_gml(gml)  # parse gml data

d = dict(G.degree)
low, *_, high = sorted(d.values())
norm = mpl.colors.Normalize(vmin=low, vmax=high, clip=True)
mapper = mpl.cm.ScalarMappable(norm=norm, cmap=mpl.cm.twilight_shifted)

options = {
    "node_size": 500,
    "linewidths": 0,
    "width": 0.1,
}

'''
G = nx.Graph()  # or DiGraph, MultiGraph, MultiDiGraph, etc
G.add_node(1)
G.add_node("Hello")
K3 = nx.Graph([(0, 1), (1, 2), (2, 0)])
G.add_node(K3)
G.number_of_nodes()
'''

plt.figure(figsize =(30, 18))
#nx.draw(G,with_labels=True,nodelist=d,node_color=[mapper.to_rgba(i)for i in d.values()])
nx.draw(G,with_labels=True,nodelist=d)
plt.show()
