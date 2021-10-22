import argparse
from graph import Graph
from bnb import BNBSolver

# class
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_data', type=str, help='path to input data',
                        default='/home/alexander/HSE_Stuff/Max_Clique/DIMACS_subset_ascii/johnson16-2-4.clq')
    return parser.parse_args()


def main():
    args = parse_args()
    graph = Graph(data=args.input_data)
    graph.apply_coloring()
    bnb_solver = BNBSolver(graph=graph)
    bnb_solver.solve()


if __name__ == "__main__":
    main()