import os
import argparse


def parse_args():
    description = "Importiert Nodestrings aus Shapes. "
    ap = argparse.ArgumentParser(description=description, epilog="$Flow Tracer",
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--mesh",
                    metavar='netz.2dm',
                    type=str,
                    required=True,
                    help="Name eines 2dm-Netzes")
    ap.add_argument("--veloc",
                    metavar='veloc_max.dat',
                    type=str,
                    required=True,
                    help="Name der veloc_max.dat")
    ap.add_argument("--dt",
                    metavar='2',
                    type=int,
                    required=False,
                    default=2,
                    help="Groesse des Zeitschritts")
    ap.add_argument("--h",
                    metavar='2',
                    type=float,
                    required=False,
                    default=2,
                    help="Simulationsdauer")
    ap.add_argument("--n",
                    metavar='10000',
                    type=int,
                    required=False,
                    default=10000,
                    help="Anzahl der Regentropfen")
    ap.add_argument("--neighs",
                    metavar='3',
                    type=int,
                    required=False,
                    default=3,
                    help="Anzahl der zu zur Interpolation verwendeten Nachbarn im Geschwindigkeitsfeld")
    ap.add_argument("--radius",
                    metavar='20',
                    type=int,
                    required=False, 
                    default=20,
                    help="Suchradius zur Nachbarn-Suche in Metern")
    ap.add_argument("--mod",
                    metavar='5',
                    type=int,
                    required=False,
                    default=5,
                    help="Schreibe nur jede x-te Stützstelle in die Polylinien")

    args = vars(ap.parse_args())

    dir_path = '.'
    path_mesh = os.path.join(dir_path, args['mesh'])
    path_veloc = os.path.join(dir_path, args['veloc'])
    paths_dict = {'mesh': path_mesh, 'veloc': path_veloc}
    dt = args['dt']
    n_steps = int(args['h']/dt)+1
    n_drops = args['n']

    n_neighs = args['neighs']
    max_dist = args['radius']
    write_modulo = args['mod']

    params_dict = {'dt': dt,
                   'n_steps:': n_steps,
                   'n_drops': n_drops,
                   'n_neighs': n_neighs,
                   'max_dist': max_dist,
                   'modulo': write_modulo}

    return paths_dict, params_dict
