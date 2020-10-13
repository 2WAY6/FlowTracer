import os

from math import sqrt
from tqdm import tqdm
import argparse
import numpy as np
from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import shapefile

from flowtrace.parsing import parse_args


def main():
    paths, params = parse_args()

    print("\nGewaehlte Simulatonszeit: {} Stunden.".format(round(params['dt'] * params['n_steps'] / 60 / 60, 2)))

    nodes = import_mesh_veloc(paths['mesh'], paths['veloc'])

    drops = create_drops(nodes, params['n_drops'])

    kdtree = create_search_tree(nodes)

    drop_paths = run_simulation(drops, params['n_drops'], params['dt'], params['n_steps'], kdtree, params['n_neighs'], params['max_dist'], nodes)

    write_shape(os.path.join(".", "Flow_Traces.shp"), drop_paths, params['write_modulo'])


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

    x_min, y_min, vx_min, vy_min = nodes.min(axis=0)
    x_max, y_max, vx_max, vy_max = nodes.max(axis=0)
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


def write_shape(path_traces, drop_paths, write_modulo):
    print("\nSchreibe Tropfen-Pfade als Shape...")
    w = shapefile.Writer(path_traces)

    w.field("ID", "N")
    for i, drop_path in enumerate(drop_paths):
        if len(drop_path) == 1:
            continue

        w.record(i)
        w.linez([xy for m, xy in enumerate(drop_path) if m%write_modulo == 0])

    w.close()
