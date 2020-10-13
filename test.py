import os

from math import sqrt
from tqdm import tqdm
import numpy as np
from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import shapefile


folder = r"e:\Temp\flowtrace"
path_mesh = os.path.join(folder, "hydro_as-2d.2dm")
path_veloc = os.path.join(folder, "VELOC_max.dat")
path_shape = None # os.path.join(folder, "BBox.shp")
path_traces = os.path.join(folder, "flow_traces.shp")
dt = 2 # seconds
n_drops = 10000
n_steps = 3500

n_neighs = 3
max_dist = 20

write_modulo = 5


print("\nChosen simulation time: {} hours.".format(round(dt*n_steps/60/60, 2)))

print("\nReading Mesh...")
nodes = []
for line in open(path_mesh, encoding='latin1'):
    if line.startswith("ND"):
        nd, i, x, y, z = line.split()
        nodes.append([float(x), float(y), 0, 0])

print("\nReading Veloc_max...")
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

print("\nCreating initial drop positions...")
if path_shape is None:
    x_min, y_min, vx_min, vy_min = nodes.min(axis=0)
    x_max, y_max, vx_max, vy_max = nodes.max(axis=0)
    drops = np.random.rand(nodes.shape[0], 2)
    drops[:, 0] = x_min + drops[:, 0] * (x_max - x_min)
    drops[:, 1] = y_min + drops[:, 1] * (y_max - y_min)
else:
    sf = shapefile.Reader(path_shape)
    bboxes = []
    for i in range(0, len(sf.shapes())):
        x_min, y_min, x_max, y_max = sf.bbox

        drops = np.random.rand(nodes.shape[0], 2)
        drops[:, 0] = x_min + drops[:, 0] * (x_max - x_min)
        drops[:, 1] = y_min + drops[:, 1] * (y_max - y_min)

        print(" -> ONLY USING FIRST FEATURE")
        break


print("\nBuilding KDTree...")
kdtree = KDTree(nodes[:, (0, 1)])


def dist_2d(A, B):
    dx = B[0] - A[0]
    dy = B[1] - A[1]
    return sqrt(dx**2 + dy**2)

print("\nCalculating paths...")
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
        a = 1


# plt.scatter(nodes[:, 0], nodes[:, 1], c='black', marker='o', s=2)
#
# for drop_path in drop_paths:
#     xs = [a[0] for a in drop_path]
#     ys = [a[1] for a in drop_path]
#     plt.plot(xs, ys)
#
# plt.show()


w = shapefile.Writer(path_traces)

w.field("ID", "N")
for i, drop_path in enumerate(drop_paths):
    if len(drop_path) == 1:
        continue

    w.record(i)
    w.linez([xy for m, xy in enumerate(drop_path) if m%write_modulo == 0])

w.close()
