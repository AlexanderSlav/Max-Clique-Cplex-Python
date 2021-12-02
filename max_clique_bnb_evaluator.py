import argparse
from graph import MCPGraph
from algorithms.branch_and_bound import BNBSolver
from algorithms.branch_and_cut import BNCSolver
from utils import *
from tqdm import tqdm
import json


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--solver",
        "-s",
        type=str,
        help="solver",
        choices=["BnB", "BnC"],
        default="BnB",
    )
    parser.add_argument(
        "--input_data_file",
        "-i",
        type=str,
        help="path to file with input benchmarks data",
        default="medium.txt",
    )
    parser.add_argument(
        "--output_results_dump",
        "-o",
        type=str,
        help="path to output file",
        default="results.csv",
    )
    return parser.parse_args()


@timeit
def benchmark(graph: namedtuple, solver_name: str):
    graph = MCPGraph(data=graph)
    graph.independent_sets_generation()
    graph.filter_covered_not_connected()
    solver = (
        BNBSolver(graph=graph)
        if solver_name == "BnB"
        else BNCSolver(graph=graph)
    )
    solver.solve()
    graph.maximum_clique_size_found = solver.maximum_clique_size
    graph.is_solution_is_clique = solver.is_solution_is_clique
    return graph


def main():
    args = parse_args()
    benchmark_graphs = read_benchmarks(args.input_data_file)
    column_names = [
        "Graph Name",
        "Correct Max Clique",
        "Graph Complexity",
        "Found Max Clique",
        "Is Clique",
        "Consumed Time",
    ]
    results = [column_names]
    logger_output_path = osp.join(
        osp.dirname(__file__),
        "becnhmark_logs",
        f"{args.input_data_file[:-4]}.log",
    )

    if os.path.exists(logger_output_path):
        os.remove(logger_output_path)

    logger.add(logger_output_path)

    for idx, graph in enumerate(tqdm(benchmark_graphs)):
        graph_name = graph.GraphName[:-4]
        logger.info(f"{args.solver} started for {graph_name} !")
        # try:
        graph, work_time = benchmark(graph, args.solver)
        results.append(
            [
                str(graph.name),
                str(graph.maximum_clique_size_gt),
                str(graph.complexity_type),
                str(graph.maximum_clique_size_found),
                str(graph.is_solution_is_clique),
                str(work_time),
            ],
        )
        curr_result = {
            "Right Maximum Clique Size": str(graph.maximum_clique_size_gt),
            "Found Maximum Clique Size": str(graph.maximum_clique_size_found),
            "Consumed Time": str(work_time),
            "Is Clique": str(graph.is_solution_is_clique),
            "Graph Complexity": str(graph.complexity_type),
        }
        per_graph_result_dir = osp.join(
            RESULTS_DIR,
            "per_graph_results",
            f"{args.solver}",
        )
        if not osp.exists(per_graph_result_dir):
            os.makedirs(per_graph_result_dir)

        with open(
            osp.join(per_graph_result_dir, f"{graph_name}.json"),
            "w",
        ) as file:
            json.dump(curr_result, file, indent=4)

        logger.info(f"{args.solver} finished for {graph_name} !")

    dump_results_to_csv("report", results)


if __name__ == "__main__":
    main()
