import os
import sys
from typing import List, Tuple

import gmsh
import numpy as np


# Disable prints
def blockPrint():
    sys.stdout = open(os.devnull, 'w')


# Restore prints
def enablePrint():
    sys.stdout = sys.__stdout__


def import_and_mesh(file_name: str, element_size: float, mesh_order: int = 1):
    # init gmsh
    if not gmsh.isInitialized():
        gmsh.initialize()

    # add new model
    gmsh.model.add(file_name)

    # add load step file
    gmsh.merge(file_name)
    # set file name
    gmsh.model.set_file_name(file_name)

    # set element size
    gmsh.model.mesh.set_size(gmsh.model.getEntities(), element_size)
    gmsh.model.mesh.generate()
    # mesh order
    gmsh.model.mesh.set_order(mesh_order)
    # optimize mesh
    # gmsh.model.mesh.optimize("HighOrderFastCurving")
    # gmsh.model.mesh.optimize("HighOrder")


def plot_loads():
    # calculate loads
    pass


def add_view(dimTags: List[Tuple[int, int]], nodal_loads: np.ndarray, view_name: str):
    # set general settings
    gmsh_settings_general()

    node_tags = []
    # get nodeTags in gmsh
    for dim_tag in dimTags:
        node_tags.append(gmsh.model.mesh.get_nodes(*dim_tag, includeBoundary=True)[0])

    # add view
    view = gmsh.view.add(view_name)
    # add view with stresses
    gmsh.view.addModelData(view, 0, '', "NodeData",
                           np.concatenate(node_tags),
                           nodal_loads.reshape((-1, 3)))

    # view settings
    gmsh_settings_view(view)


def gmsh_settings_general():
    # init gmsh
    if not gmsh.isInitialized():
        gmsh.initialize()

    # set colormap for arrows (can't be done by api directly, only by file)
    gmsh.merge(r"settings\colormap_orange.opt")

    # set mesh colors
    gmsh.option.set_number("Mesh.ColorCarousel", 0)
    gmsh.option.set_color("Mesh.Color.Triangles", 0, 0, 0)

    # hide geometry except surfaces
    gmsh.option.set_number("Geometry.Points", 0)
    gmsh.option.set_number("Geometry.PointLabels", 0)
    gmsh.option.set_number("Geometry.Curves", 0)
    gmsh.option.set_number("Geometry.CurveLabels", 0)
    gmsh.option.set_number("Geometry.Surfaces", 1)
    gmsh.option.set_number("Geometry.SurfaceType", 2)
    gmsh.option.set_number("Geometry.SurfaceLabels", 0)
    gmsh.option.set_number("Geometry.Volumes", 0)
    gmsh.option.set_number("Geometry.VolumeLabels", 0)

    # show mesh edges
    gmsh.option.set_number("Mesh.SurfaceEdges", 1)

    # change arrow geometry
    gmsh.option.set_number("General.ArrowHeadRadius", 0.10)
    gmsh.option.set_number("General.ArrowStemLength", 0.65)
    gmsh.option.set_number("General.ArrowStemRadius", 0.04)
    gmsh.option.set_number("General.QuadricSubdivisions", 30)

    # viewport
    gmsh.option.set_number("General.Trackball", 0)
    # hide KoSys
    gmsh.option.set_number("General.SmallAxes", 0)
    # disable shininess
    gmsh.option.set_number("General.Shininess", 0.1)


def gmsh_settings_view(view: int):
    # set arrow size constant
    gmsh.view.option.set_number(view, 'ArrowSizeMax', 100)
    gmsh.view.option.set_number(view, 'ArrowSizeMin', 0)
    # hide scale
    gmsh.view.option.set_number(view, 'ShowScale', 0)
    # show loads at nodes instead of element centers
    gmsh.view.option.set_number(view, 'GlyphLocation', 2)
