import argparse
from graph import MCPGraph
from bnb import BNBSolver
from utils import *
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_data_file', type=str, help='path to file with input benchmarks data',
                        default='benchmarks.txt')
    parser.add_argument('--output_results_dump', type=str, help='path to output file',
                        default='results.csv')
    return parser.parse_args()


@timeit
def benchmark(graph: namedtuple):
    graph = MCPGraph(data=graph)
    graph.apply_coloring()
    bnb_solver = BNBSolver(graph=graph)
    bnb_solver.solve()
    graph.maximum_clique_size_found = bnb_solver.maximum_clique_size
    # # check if we get right solution
    # assert graph.maximum_clique_size_found == graph.maximum_clique_size_gt
    return graph


def main():
    args = parse_args()
    benchmark_graphs = read_benchmarks(args.input_data_file)
    column_names = ["Graph Name","Correct Max Clique", "Graph Complexity", "Found Max Clique", "Consumed Time"]
    results = [column_names]
    for idx, graph in enumerate(tqdm(benchmark_graphs)):
        graph_name = graph.GraphName[:-4]
        logger.add(osp.join(osp.dirname(__file__), "logs", f"{graph_name}.log"))
        logger.info(f"BnB started for {graph_name} !")
        graph, work_time = benchmark(graph)
        results.append([str(graph.name),
                        str(graph.maximum_clique_size_gt),
                        str(graph.complexity_type),
                        str(graph.maximum_clique_size_found),
                        str(work_time)])
        logger.info(f"BnB finished for {graph_name} !")
        print(graph, f"Consumed Time: {work_time}")
    dump_results_to_csv("report", results)


if __name__ == "__main__":
    main()