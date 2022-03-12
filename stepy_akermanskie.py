
from __future__ import print_function

import os
import os.path
import sys

from OCC.Core.STEPControl import STEPControl_Reader
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
from OCC.Core.TopoDS import topods_Face,TopoDS_Iterator
# from OCC.Core import BRepAdaptor
# print(dir(BRepAdaptor))
from OCC.Core.BRep import BRep_Tool, BRep_Tool_Pnt, BRep_Tool_IsGeometric, BRep_Tool_Parameter, BRep_Tool_Curve
# sys.exit()
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface,BRepAdaptor_Curve
from OCC.Display.SimpleGui import init_display
#from OCC.Core.BRepool import Curve

from OCC.Extend.TopologyUtils import TopologyExplorer


def read_step_file(filename):
    """read the STEP file and returns a compound"""
    step_reader = STEPControl_Reader()
    status = step_reader.ReadFile(filename)

    if status == IFSelect_RetDone:  # check status
        failsonly = False
        step_reader.PrintCheckLoad(failsonly, IFSelect_ItemsByEntity)
        step_reader.PrintCheckTransfer(failsonly, IFSelect_ItemsByEntity)
        step_reader.TransferRoot(1)
        a_shape = step_reader.Shape(1)
    else:
        print("Error: can't read file.")
        sys.exit(0)
    return a_shape


def recognize_face(a_face):
    """Takes a TopoDS shape and tries to identify its nature
    whether it is a plane a cylinder a torus etc.
    if a plane, returns the normal
    if a cylinder, returns the radius
    """
    surf = BRepAdaptor_Surface(a_face, True)
    surf_type = surf.GetType()
    if surf_type == GeomAbs_Plane:
        print("--> plane")
        # look for the properties of the plane
        # first get the related gp_Pln
        gp_pln = surf.Plane()
        location = gp_pln.Location()  # a point of the plane
        normal = gp_pln.Axis().Direction()  # the plane normal
        # then export location and normal to the console output
        print(
            "--> Location (global coordinates)",
            location.X(),
            location.Y(),
            location.Z(),
        )
        print("--> Normal (global coordinates)", normal.X(), normal.Y(), normal.Z())
    elif surf_type == GeomAbs_Cylinder:
        print("--> cylinder")
        # look for the properties of the cylinder
        # first get the related gp_Cyl
        gp_cyl = surf.Cylinder()
        location = gp_cyl.Location()  # a point of the axis
        axis = gp_cyl.Axis().Direction()  # the cylinder axis
        # then export location and normal to the console output
        print(
            "--> Location (global coordinates)",
            location.X(),
            location.Y(),
            location.Z(),
        )
        print("--> Axis (global coordinates)", axis.X(), axis.Y(), axis.Z())
    else:
        # TODO there are plenty other type that can be checked
        # see documentation for the BRepAdaptor class
        # https://www.opencascade.com/doc/occt-6.9.1/refman/html/class_b_rep_adaptor___surface.html
        print("not implemented")


def recognize_clicked(shp, *kwargs):
    """This is the function called every time
    a face is clicked in the 3d view
    """
    for shape in shp:  # this should be a TopoDS_Face TODO check it is
        print("Face selected: ", shape)
        recognize_face(topods_Face(shape))
        print(dir(shape))
        print("NBCHILDREN",shape.NbChildren())
        tdi = TopoDS_Iterator(shape)
        tdi.Initialize(shape)
        while tdi.More():
            print("WIRE")
            tshp = tdi.Value()
            print(tshp.NbChildren())
            twi = TopoDS_Iterator(tshp)
            twi.Initialize(tshp)
            while twi.More():
                ttshp = twi.Value()
                tei = TopoDS_Iterator(ttshp)
                tei.Initialize(ttshp)
                print(dir(ttshp))
                print("shapetype", ttshp.ShapeType())
                while tei.More():
                    tttshp = tei.Value()
                    print("TYP 2", tttshp)
#                    print(dir(tttshp))
                    tei.Next()
                #print("TYP", ttshp.ShapeType())
                print("TYP", ttshp)
                curv = BRepAdaptor_Curve(ttshp).Curve()
                print(curv)
                # print(curv.Circle())
                a = 0.0
                b = 0.0
                [curve_handle, a, b] = BRep_Tool.Curve(ttshp)
                print(curve_handle.DynamicType().Name())
                # print(curv.GetType())
                print(dir(curv))
                twi.Next()
            print(dir(tshp))
            print(tshp)
            print(tshp.ShapeType())
            print(tshp.TShape())
            tdi.Next()


def recognize_batch(event=None):
    """Menu item : process all the faces of a single shape"""
    # then traverse the topology using the Topo class
    t = TopologyExplorer(shp)
    # loop over faces only
    for f in t.faces():
        # call the recognition function
        recognize_face(f)


def exit(event=None):
    sys.exit()


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.register_select_callback(recognize_clicked)
    # first loads the STEP file and display
    # shp = read_step_file("E:/GIT/DOKTORAT/face_recognition_sample_part.stp")
    shp = read_step_file("E:/GIT/DOKTORAT/model2.stp")
    #shp = read_step_file("E:/GIT/DOKTORAT/all_together.step")
    print(shp)
    print(dir(shp))
    print(shp.NbChildren())
    print(shp.ShapeType())
    print(shp.TShape())
    '''
    tdi = TopoDS_Iterator(shp)
    tdi.Initialize(shp)
    while tdi.More():
        print("POZYCJA")
        tshp = tdi.Value()
        print(tshp.NbChildren())
        print(dir(tshp))
        print(tshp)
        print(tshp.ShapeType())
        tdi.Next()
    '''
    display.DisplayShape(shp, update=True)
    add_menu("recognition")
    add_function_to_menu("recognition", recognize_batch)
    display.SetSelectionModeFace()
    #print(dir(display))
    #sys.exit()
    start_display()
    # display.SetSelectionModeFace()
