import numpy as np


# TODO: Use Cython instead
def run_simulation_rasterized(mesh, drops, dt, n_steps):
    print("\nSimuliere die Partikel im Vektorfeld...")

    # TODO: That can be done before when the old code is deleted
    drops[:, 0] -= mesh.x_min
    drops[:, 1] -= mesh.y_min

    drop_paths = []
    field = mesh.vector_field
    vectors = np.zeros((drops.shape[0], 2))

    for tsi in range(n_steps):
        print("- Entering timestep {} / {} -> {} s...".format(tsi + 1,
                                                              n_steps,
                                                              tsi * dt))
        # Save momentary drop positions
        drop_paths.append(np.copy(drops))

        # Find drop position buckets
        positions = np.array(drops, dtype=np.int)

        # Updating drop velocities
        vectors = field[positions[:, 0], positions[:, 1]]

        # Update positions
        drops += dt * vectors

    return np.array(drop_paths)
