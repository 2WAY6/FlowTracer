from tqdm import tqdm
import shapefile


def write_traces_to_shapefile(path_traces, drop_paths, modulo):
    print("\nWriting flow traces to shapefile...")
    print(path_traces)
    w = shapefile.Writer(path_traces)

    w.field("ID", "N")
    for col in tqdm(range(drop_paths.shape[1])):
        points = drop_paths[:, col]

        w.record(col)
        w.linez([points[0:1:modulo]])
        # w.linez([points])

    w.close()


def write_vectorfield_to_shapefile(path_shp, mesh):
    print("\nWriting vector field to point shape...")
    w = shapefile.Writer(path_shp)

    w.field("Vx", "F", decimal=3)
    w.field("Vy", "F", decimal=3)

    for row in tqdm(range(mesh.vector_field.shape[0])):
        for col in range(mesh.vector_field.shape[1]):
            x = col + mesh.x_min
            y = mesh.y_max - row

            w.record(mesh.vector_field[row, col, 0],
                     mesh.vector_field[row, col, 1])
            w.point(x, y)
    w.close()
