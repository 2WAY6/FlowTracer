import numpy as np
from numba import jit


# TODO: Use Cython
@jit
def is_ccw(vec_a, vec_b, vec_c):
    return (vec_c[1] - vec_a[1]) * (vec_b[0] - vec_a[0]) >= (vec_b[1] - vec_a[1]) * (vec_c[0] - vec_a[0]) # >= because of zero area case


# TODO: Use Cython
@jit
def interpolate_z_on_triangle(p, nodes, values):
    v1 = nodes[0]
    v2 = nodes[1]
    v3 = nodes[2]
    w1 = (((v2[1] - v3[1]) * (p[0] - v3[0]) +
           (v3[0] - v2[0]) * (p[1] - v3[1])) /
          ((v2[1] - v3[1]) * (v1[0] - v3[0]) +
           (v3[0] - v2[0]) * (v1[1] - v3[1])))
    w2 = (((v3[1] - v1[1]) * (p[0] - v3[0]) +
           (v1[0] - v3[0]) * (p[1] - v3[1])) /
          ((v2[1] - v3[1]) * (v1[0] - v3[0]) +
           (v3[0] - v2[0]) * (v1[1] - v3[1])))
    w3 = 1 - w1 - w2

    z = w1 * values[0] + w2 * values[1] + w3 * values[3]
    return z


# TODO: Use Cython
@jit
def rasterize(nodes, vals,  elements, glob_xmin, glob_xmax, glob_ymin,
              glob_ymax, raster):
    glob_xmin_int = int(glob_xmin)
    glob_xmax_int = int(glob_xmax)
    glob_ymin_int = int(glob_ymin)
    glob_ymax_int = int(glob_ymax)

    for ti in range(elements.shape[0]):
        nids = elements[ti]
        triangle = nodes[nids]
        values = vals[nids]

        xmin = int(np.floor(triangle[:, 0].min()))
        ymin = int(np.floor(triangle[:, 1].min()))
        xmax = int(np.ceil(triangle[:, 0].max()))
        ymax = int(np.ceil(triangle[:, 1].max()))

        pnt = np.array([0, 0])
        for i in range(xmin, xmax):
            for j in range(ymin, ymax):
                pnt[0] = i
                pnt[1] = j

                bool1 = is_ccw(pnt, triangle[0], triangle[1])
                bool2 = is_ccw(pnt, triangle[1], triangle[2])
                bool3 = is_ccw(pnt, triangle[2], triangle[0])
                if (bool1 and bool2 and bool3) or \
                   (not bool1 and not bool2 and not bool3):
                    rcol = i - glob_xmin_int  # - 1
                    rrow = j - glob_ymin_int
                    # rrow = glob_ymax_int - j

                    raster[rrow, rcol, 0] = interpolate_z_on_triangle(
                        pnt, triangle, values[:, 0])
                    raster[rrow, rcol, 1] = interpolate_z_on_triangle(
                        pnt, triangle, values[:, 1])
