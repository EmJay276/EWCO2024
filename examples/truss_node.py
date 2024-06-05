import timeit
from typing import List, Tuple

import gmsh
import numpy as np

from src.common import import_and_mesh, blockPrint, enablePrint, add_view
from src.moment2force import moment2force

################################################
# import model to gmsh and mesh it
################################################
import_and_mesh('step/truss_node.stp', element_size=2, mesh_order=1)

################################################
# get points and triangles
################################################
# Load Cases -> DimTag per Load
load_case_dimTags: List[List[Tuple[int, int]]] = [[(2, 5), (2, 4), (2, 6), (2, 1)], ]

load_cases: List[np.ndarray] = [np.array([[ -495.84161,  -982.11983,   719.40029],
                                          [-1905.27692, 10831.23167,  -107.83179],
                                          [ 1191.57727, -1318.71017,  -747.33607],
                                          [ 1209.54126, -8530.40166,   135.76757]]), ]

################################################
# computational time
################################################
print(f"Time usage:")
for load_case, dimTags in zip(load_cases, load_case_dimTags):
    for force_compensation in [False, True]:
        for load, dimTag in zip(load_case, dimTags):
            blockPrint()
            coords = gmsh.model.mesh.get_nodes(*dimTag, includeBoundary=True)[1].reshape(-1, 3)
            center = gmsh.model.occ.get_center_of_mass(*dimTag)
            durations = timeit.Timer(
                lambda: moment2force(coords, load, center, force_compensation=force_compensation)).repeat(repeat=1000,
                                                                                                          number=1)
            enablePrint()
            print(f"{load=}, {force_compensation=}: {np.min(durations) * 1e6:0f}µs")

################################################
# add views to gmsh
################################################
for i, (load_case, dimTags) in enumerate(zip(load_cases, load_case_dimTags)):
    for force_compensation in [False, True]:
        nodal_loads = []
        # moment to force for every surface
        for load, dimTag in zip(load_case, dimTags):
            coords = gmsh.model.mesh.get_nodes(*dimTag, includeBoundary=True)[1].reshape(-1, 3)
            center = gmsh.model.occ.get_center_of_mass(*dimTag)
            nodal_loads.append(moment2force(coords, load, center, force_compensation=force_compensation))

        # combine all nodal loads to a single vector
        nodal_loads = np.concatenate(nodal_loads)

        # add view to gmsh
        add_view(dimTags, nodal_loads, view_name=f"Load Case {i}, Force comp: {force_compensation}")

################################################
# show result
################################################
# start UI
gmsh.fltk.run()
