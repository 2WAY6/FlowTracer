import os
import argparse


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
    ap.add_argument("--mesh",
                    metavar='netz.2dm',
                    type=str,
                    required=True,
                    help="Name des 2dm-Netzes")
    ap.add_argument("--v",
                    metavar='veloc_max.dat',
                    type=str,
                    required=True,
                    help="Name der veloc_max.dat")
    ap.add_argument("--dt",
                    metavar='60',
                    type=int,
                    required=False,
                    default=60,
                    help="Groesse des Zeitschritts, in dem der Partikel bewegt wird [Sekunde]")
    ap.add_argument("--h",
                    metavar='2',
                    type=float,
                    required=False,
                    default=2,
                    help="Gesamtdauer der Partikelsimulation [Stunden]. (Hier kann die Hydro_AS-Simulationszeit verwendet werden.)")
    ap.add_argument("--n",
                    metavar='10000',
                    type=int,
                    required=False,
                    default=10000,
                    help="Anzahl der Partikel (= Regentropfen = Polylinien), die zum Zeitpunkt t0 in das Geschwindigkeitsfeld gegeben werden.")
    ap.add_argument("--neighs",
                    metavar='3',
                    type=int,
                    required=False,
                    default=3,
                    help="Anzahl der fuer jeden Partikel zur Interpolation verwendeten Nachbarknoten im Geschwindigkeitsfeld")
    ap.add_argument("--radius",
                    metavar='20',
                    type=int,
                    required=False, 
                    default=20,
                    help="Suchradius zur Nachbarn-Suche [Meter]")
    ap.add_argument("--mod",
                    metavar='5',
                    type=int,
                    required=False,
                    default=5,
                    help="Schreibe nur jede x-te Stützstelle in die Polylinien. (Verringert die Datenmenge)")

    args = vars(ap.parse_args())

    print("\nGewaehlte Simulatonszeit: {} Stunden.".format(args['h']))

    dir_path = '.'

    path_mesh = os.path.join(dir_path, args['mesh'])
    path_veloc = os.path.join(dir_path, args['v'])
    dt = args['dt']
    seconds = args['h'] * 60 * 60
    n_steps = int(seconds/dt) + 1
    n_drops = args['n']

    n_neighs = args['neighs']
    max_dist = args['radius']
    write_modulo = args['mod']

    path_out_shape = os.path.join(os.path.dirname(path_veloc),
                                  "Flow_Traces_{}raindrops_{}h_dt{}s.shp".format(n_drops, args['h'], dt))
    params_dict = {'dt': dt,
                   'n_steps': n_steps,
                   'n_drops': n_drops,
                   'n_neighs': n_neighs,
                   'max_dist': max_dist,
                   'modulo': write_modulo}

    paths_dict = {'mesh': path_mesh,
                  'veloc': path_veloc,
                  'out_shape': path_out_shape}

    print("Gewaehlte und ermittelte Parameter: ")
    print("dt [seconds]: {}".format(dt))
    print("n_steps [-]:  {}".format(n_steps))

    return paths_dict, params_dict
