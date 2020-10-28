import os

import numpy as np
from numba import jit

from .geometry import is_ccw, interpolate_z_on_triangle, rasterize


class Mesh:
    def __init__(self):
        print("\nInitializing Mesh Object...")
        self.nodes = []
        self.values = None
        self.elements = []

        self.x_min, self.y_min, self.x_max, self.y_max = None, None, None, None

        self.vector_field = None

    # Function for importing 2dm meshes
    def import_2dm_mesh(self, path_mesh):
        print("\nImporting mesh from {}...".format(
              os.path.basename(path_mesh)))

        with open(path_mesh, encoding="latin1") as f:
            for line in f:
                # Import nodes
                if line.startswith("ND"):
                    x, y, z = line.split()[2:]
                    self.nodes.append([float(x), float(y), float(z)])

                # Import tris
                elif line.startswith("E3T"):
                    n1, n2, n3 = line.split()[2:5]
                    self.elements.append([int(n1)-1, int(n2)-1, int(n3)-1])

                # Import quads as tris
                elif line.startswith("E4Q"):
                    n1, n2, n3, n4 = line.split()[2:6]
                    self.elements.append([int(n1)-1, int(n2)-1, int(n3)-1])
                    self.elements.append([int(n3)-1, int(n4)-1, int(n1)-1])

        self.nodes = np.array(self.nodes, dtype=np.float)
        self.elements = np.array(self.elements, dtype=np.int)

        print("- Calculating bounding box...")
        self.x_min, self.y_min = np.min(self.nodes[:, :2], axis=0)
        self.x_max, self.y_max = np.max(self.nodes[:, :2], axis=0)
        print("  - BBox: ({}, {}) ({}, {})".format(self.x_min,
                                                   self.y_min,
                                                   self.x_max,
                                                   self.y_max))

        print("- Imported {} nodes and {} elements.".format(
              self.nodes.shape[0], self.elements.shape[0]))

    # Function for importing 2dm vector dats (= pair of values)
    def import_2dm_vector_dat(self, path_dat):
        print("\nImporting vector dat from {}...".format(
              os.path.basename(path_dat)))
        with open(path_dat) as f:
            lines = f.readlines()

        # TODO: Make dats with more header lines than 4 importable
        n_nodes = self.nodes.shape[0]
        values = [list(map(float, line.split())) for line
                  in lines[4:(4+n_nodes)]]
        self.values = np.array(values)

    # TODO: Import UnRunOff mesh
    def import_uro_mesh(self, path_mesh):
        pass

    # TODO: Import UnRunOff results
    def import_uro_ergmax(self, path_ergmax):
        pass

    # Creating a rasterized vector field from the mesh
    def create_rasterized_vector_field(self, resolution=1):
        print("\nCreating a rasterized vector field from mesh...")
        print("- Resolution: {} m.".format(resolution))

        self.vector_field = np.zeros((int(self.x_max - self.x_min),
                                      int(self.y_max - self.y_min),
                                      2))

        # TODO: Use Cython for this part
        rasterize(self.nodes, self.values, self.elements, self.x_min,
                  self.y_max, self.vector_field)
