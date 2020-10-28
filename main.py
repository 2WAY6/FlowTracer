
#!/usr/bin/env python3.8
# -*- encoding: utf-8 -*-

'''

FLOW TRACER
Version 2.0

Created:    01.02.2020
Modified:   13.10.2020

@author: Pascal Wiese

TODO: Put functions in separate python files
TODO: Improve description 
TODO: Broadcast the simulation for better performance
TODO: flake8
'''

import os
import sys

from math import sqrt
from tqdm import tqdm
import numpy as np
from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import shapefile

from flowtrace.parsing import parse_args
from flowtrace.mesh import Mesh
from flowtrace.simulation import run_simulation_rasterized


def main():
    paths, params = parse_args()

    mesh = Mesh()
    mesh.import_2dm_mesh(paths['mesh'])
    mesh.import_2dm_vector_dat(paths['veloc'])
    mesh.create_rasterized_vector_field()
    print(mesh.nodes.min(axis=0))

    drops = create_drops(mesh.nodes, params['n_drops'])

    drop_paths = run_simulation_rasterized(mesh, drops, params['dt'], 
                                           params['n_steps'])

    write_shape(paths['out_shape'], drop_paths, params['modulo'])

    print("\nProgramm abgeschlossen.")

    sys.exit()
    # before:
    nodes = import_mesh_veloc(paths['mesh'], paths['veloc'])

    drops = create_drops(nodes, params['n_drops'])

    kdtree = create_search_tree(nodes)

    drop_paths = run_simulation(drops, params['n_drops'], params['dt'], params['n_steps'], kdtree, params['n_neighs'], params['max_dist'], nodes)

    write_shape(paths['out_shape'], drop_paths, params['modulo'])

    print("\nProgramm abgeschlossen.")


def import_mesh_veloc(path_mesh, path_veloc):
    print("\nLese Mesh...")
    nodes = []
    for line in open(path_mesh, encoding='latin1'):
        if line.startswith("ND"):
            nd, i, x, y, z = line.split()
            nodes.append([float(x), float(y), 0, 0])

    print("\nLese Veloc_max...")
    ni = 0
    for line in open(path_veloc):
        try:
            vx, vy = line.split()
            nodes[ni][2] = float(vx)
            nodes[ni][3] = float(vy)
            ni += 1
        except:
            pass

    nodes = np.array(nodes)
    return nodes


def create_drops(nodes, n_drops):
    print("\nErzeuge die Startpositionen der Tropfen...")

    x_min, y_min = nodes[:, :2].min(axis=0)
    x_max, y_max = nodes[:, :2].max(axis=0)
    print("- Random positions between ({}, {}) und ({}, {})".format(x_min,
                                                                    y_min,
                                                                    x_max,
                                                                    y_max))

    drops = np.random.rand(n_drops, 2)
    drops[:, 0] = x_min + drops[:, 0] * (x_max - x_min)
    drops[:, 1] = y_min + drops[:, 1] * (y_max - y_min)
    return drops


def create_search_tree(nodes):
    print("\nBaue raeumliche Suchstruktur...")
    kdtree = KDTree(nodes[:, (0, 1)])
    return kdtree


def dist_2d(A, B):
    dx = B[0] - A[0]
    dy = B[1] - A[1]
    return sqrt(dx**2 + dy**2)


def run_simulation(drops, n_drops, dt, n_steps, kdtree, n_neighs, max_dist, nodes):
    print("\nBerechne Tropfen-Pfade...")
    drop_paths = [[] for n in range(n_drops)]
    for di in tqdm(range(n_drops)):
        for n in range(n_steps):
            # Save position
            x0 = drops[di, 0]
            y0 = drops[di, 1]
            drop_paths[di].append([x0, y0])

            # Move drop
            dists, ids = kdtree.query(drops[di], n_neighs)
            neigh_ids = [ids[i] for i in range(len(ids)) if dists[i] < max_dist]
            if len(neigh_ids) < 3:
                break

            vx_res, vy_res = 0, 0
            weight_sum = 0
            for neigh_id in neigh_ids:
                x1, y1, vx, vy = nodes[neigh_id]
                weight = 1/dist_2d((x0, y0), (x1, y1))
                vx_res += weight * vx
                vy_res += weight * vy
                weight_sum += weight

            vx_res = vx_res/weight_sum
            vy_res = vy_res/weight_sum

            dx = vx_res * dt
            dy = vy_res * dt
            drops[di, 0] += dx
            drops[di, 1] += dy

    return drop_paths


def write_shape(path_traces, drop_paths, modulo):
    print("\nSchreibe Tropfen-Pfade als Shape...")
    print(path_traces)
    w = shapefile.Writer(path_traces)

    w.field("ID", "N")
    for i, drop_path in enumerate(tqdm(drop_paths)):
        if len(drop_path) == 1:
            continue

        points = [xy for m, xy in enumerate(drop_path) if m % modulo == 0]
        points.append(drop_path[-1])

        if len(points) < 2:
            continue

        w.record(i)
        w.linez([points])

    w.close()


if __name__ == '__main__':
    main()
