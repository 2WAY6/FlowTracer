#!/usr/bin/env python3.8
# -*- encoding: utf-8 -*-

'''

FLOW TRACER

Created:    01.02.2020
Modified:   19.02.2021

@author: Paz (2WAY6)

TODO: add Testing
TODO: add Typing
TODO: Put rasterization into extra module
TODO: Improve description
TODO: Rewrite numba functions with cython
TODO: Add english description

'''

import os
import argparse
from time import time

from mesh.mesh import Mesh
from compute.simulation import create_drops, run_simulation_rasterized
from importexport.export import write_traces_to_shapefile


VERSION = 2.1


def main():
    t0 = time()
    paths, params = parse_args()

    print("\n\n~ ~ ~ Importing Data ~ ~ ~")
    mesh = Mesh()
    mesh.import_2dm_mesh(paths['mesh'])
    mesh.import_2dm_vector_dat(paths['dat'])

    print("\n\n~ ~ ~ Creating Vector Field ~ ~ ~")
    mesh.create_rasterized_vector_field()

    # write_field_shape(paths['mesh'][:-4] + "_field.shp", mesh)

    print("\n\n~ ~ ~ Running Simulation ~ ~ ~")
    drops = create_drops(mesh.nodes, params['n_drops'])
    drop_paths = run_simulation_rasterized(mesh, drops, params['dt'], 
                                           params['n_steps'])

    print("\n\n~ ~ ~ Writing Output ~ ~ ~")
    write_traces_to_shapefile(paths['out_shape'], drop_paths, params['modulo'])

    print("\n\nProgram finished after {:.3} seconds.".format(time() - t0))


def parse_args():
    description = "FlowTrace erzeugt aus den Ergebnisdaten ein Linien-Shape mit Fliesswegen.\n" + \
                  "Dies erfolgt, indem die maximalen Geschwindigkeitsvektoren als Vektorfeld interpretiert werden. " + \
                  "Man koennte FlowTrace als eine Partikelsimulation bezeichnen.\n\n" + \
                  "In dieses Geschwindigkeitsfeld werden dann an zufaelligen Positionen Partikel in das Netz gegeben. " + \
                  "Abhaengig von den benachbarten Knoten wird fuer jeden Partikel eine Geschwindigkeit interpoliert. " + \
                  "Mit dieser Geschwindigkeit v wird der Partikel dann fuer den Zeitschritt dt weiterbewegt. \n" + \
                  "Zurueckgelegter Weg s -> s [m] = dt [s] * v [m/s]"

    ap = argparse.ArgumentParser(description=description, epilog="$Flow Tracer",
                                 formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--mesh", metavar='netz.2dm', type=str, required=True,
                    help="Name des 2dm-Netzes")
    ap.add_argument("--dat", metavar='veloc_max.dat', type=str, required=True,
                    help="Name der veloc_max.dat")
    ap.add_argument("--dt", metavar='60', type=int, required=False, default=60,
                    help="Groesse des Zeitschritts, in dem der Partikel bewegt wird [Sekunde]")
    ap.add_argument("--h", metavar='2', type=float, required=False, default=2,
                    help="Gesamtdauer der Partikelsimulation [Stunden]. (Hier kann die Hydro_AS-Simulationszeit verwendet werden.)")
    ap.add_argument("--n", metavar='10000', type=int, required=False, default=10000,
                    help="Anzahl der Partikel (= Regentropfen = Polylinien), die zum Zeitpunkt t0 in das Geschwindigkeitsfeld gegeben werden.")
    ap.add_argument("--mod", metavar='5', type=int, required=False, default=5,
                    help="Schreibe nur jede x-te Stützstelle in die Polylinien. (Verringert die Datenmenge)")

    args = vars(ap.parse_args())

    dir_path = '.'

    path_mesh = os.path.join(dir_path, args['mesh'])
    path_dat = os.path.join(dir_path, args['dat'])
    dt = args['dt']
    seconds = args['h'] * 60 * 60
    n_steps = int(seconds/dt) + 1
    n_drops = args['n']

    modulo = args['mod']

    path_out_shape = os.path.join(
        os.path.dirname(path_dat),
        f"Flow_Traces_n{n_drops}_{args['h']}h_dt{dt}s.shp")

    params_dict = {'dt': dt,
                   'n_steps': n_steps,
                   'n_drops': n_drops,
                   'modulo': modulo}

    paths_dict = {'mesh': path_mesh,
                  'dat': path_dat,
                  'out_shape': path_out_shape}

    print("\nChosen and calculated parameters: ")
    print(f"- {n_drops} particles will move for simulated {args['h']} hours "
          "inside the vector field.")
    print(f"- The internal timestep of each iteration will be {dt} seconds.")
    print(f"- This results in a total number of {n_steps} timesteps to be "
          "calculated.")
    print(f"- Only saving each {modulo}th particle position to save some "
          "space.")

    return paths_dict, params_dict


def print_title():
    print("\n")
    print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
    print(r"______ _             _____ ")
    print(r"|  ___| |           |_   _| ")
    print(r"| |_  | | _____      _| |_ __ __ _  ___ ___ _ __ ")
    print(r"|  _| | |/ _ \ \ /\ / / | '__/ _` |/ __/ _ \ '__|")
    print(r"| |   | | (_) \ V  V /| | | | (_| | (_|  __/ |   ")
    print(r"\_|   |_|\___/ \_/\_/ \_/_|  \__,_|\___\___|_| ")
    print(f"\n~ ~ ~ ~ ~ ~ ~ ~ ~ Version {VERSION} ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")
    print("\nCreating Flow Traces from 2D simulation results.")
    print("(c) Pascal Wiese, 2021\n")
    print("~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~ ~")


if __name__ == '__main__':
    print_title()
    main()
