from time import time

import numpy as np


# TODO: Use Cython instead
def run_simulation_rasterized(mesh, drops, dt, n_steps):
    print("\nSimuliere die Partikel im Vektorfeld...")
    t0 = time()

    # TODO: That can be done before when the old code is deleted
    drops[:, 0] -= mesh.x_min
    drops[:, 1] -= mesh.y_min

    drop_paths = []
    field = mesh.vector_field
    vectors = np.zeros((drops.shape[0], 2))

    # print(drops)
    # print(f"drops.min(axis=0)\t{drops.min(axis=0)}")
    # print(f"drops.max(axis=0)\t{drops.max(axis=0)}")
    # print(f"drops.shape\t{drops.shape}")
    # print(f"vectors.shape\t{vectors.shape}")
    # print(f"field.shape\t{field.shape}")

    for tsi in range(n_steps):
        # print("- Entering timestep {} / {} -> {} s...".format(tsi + 1,
        #                                                       n_steps,
        #                                                       tsi * dt))
        # Save momentary drop positions
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

    print(drop_paths[0])

    drop_paths = np.array(drop_paths)
    drop_paths[:, :, 0] += mesh.x_min
    drop_paths[:, :, 1] += mesh.y_min

    print("Finished after {:.3} seconds.".format(time() - t0))
    return drop_paths
