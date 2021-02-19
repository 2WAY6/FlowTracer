from time import time

import numpy as np


def run_simulation_rasterized(mesh, drops, dt, n_steps):
    print("\nSimulating particle movement within the vector field...")
    t0 = time()

    drops[:, 0] -= mesh.x_min
    drops[:, 1] -= mesh.y_min

    drop_paths = []
    field = mesh.vector_field
    vectors = np.zeros((drops.shape[0], 2))

    for tsi in range(n_steps):
        drop_paths.append(np.copy(drops))

        # Find drop position buckets
        positions = np.array(drops, dtype=np.int)
        positions[positions[:, 0] < 0, 0] = 0
        positions[positions[:, 1] < 0, 1] = 0
        positions[positions[:, 0] >= field.shape[1], 0] = field.shape[1] - 1
        positions[positions[:, 1] >= field.shape[0], 1] = field.shape[0] - 1

        # Updating drop velocities
        vectors = field[positions[:, 1], positions[:, 0]]

        # Update positions
        drops += dt * vectors

    drop_paths = np.array(drop_paths)
    drop_paths[:, :, 0] += mesh.x_min
    drop_paths[:, :, 1] += mesh.y_min

    print("Finished after {:.3} seconds.".format(time() - t0))
    return drop_paths


def create_drops(nodes, n_drops):
    print(f"\nCreating initial position for {n_drops} particles...")

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
