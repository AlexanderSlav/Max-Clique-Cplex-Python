import argparse
from graph import Graph
from bnb import BNBSolver
from utils import *


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_data', type=str, help='path to input data',
                        default='/home/alexander/HSE_Stuff/Max_Clique/DIMACS_subset_ascii/c-fat200-2.clq')
    return parser.parse_args()


@timeit
def benchmark(args):
    graph = Graph(data=args.input_data)
    graph.apply_coloring()
    bnb_solver = BNBSolver(graph=graph)
    bnb_solver.solve()


def main():
    args = parse_args()
    benchmark(args)


if __name__ == "__main__":
    main()