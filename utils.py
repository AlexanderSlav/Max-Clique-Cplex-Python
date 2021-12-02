import csv
import datetime
import os
import os.path as osp
import time
from collections import namedtuple
import networkx as nx
from loguru import logger

DATA_DIR = osp.join(osp.dirname(__file__), "benchmarks")
SOURCE_GRAPH_DIR = osp.join(osp.dirname(__file__), "data")
RESULTS_DIR = osp.join(osp.dirname(__file__), "results")
LOG_DIR = osp.join(osp.dirname(__file__), "becnhmark_logs")

EPS = 1e-5
STRATEGIES = [
    nx.coloring.strategy_largest_first,
    nx.coloring.strategy_random_sequential,
    nx.coloring.strategy_connected_sequential_bfs,
    nx.coloring.strategy_connected_sequential_dfs,
    nx.coloring.strategy_saturation_largest_first,
    nx.coloring.strategy_smallest_last,
]

timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H:%M")


def dump_results_to_csv(output_name, results):
    if not osp.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    path = osp.join(RESULTS_DIR, f"{output_name}_{timestamp}.csv")
    with open(path, "w") as file:
        writer = csv.writer(file)
        writer.writerows(results)


def timeit(f):
    """Measures time of function execution"""

    def wrap(*args):
        time1 = time.time()
        result = f(*args)
        time2 = time.time()
        work_time = round(time2 - time1, 3)
        logger.info(f"Function: <{f.__name__}> worked {work_time} seconds")
        return result, work_time

    return wrap


def read_benchmarks(data_file: str = "benchmarks.txt"):
    with open(osp.join(DATA_DIR, data_file)) as test_data:
        column_names = test_data.readline().strip().split(",")
        BencmarkGrpah = namedtuple("BenchmarkGraph", column_names)
        benchmark_data = tuple(
            [
                BencmarkGrpah(*tuple(line.strip().split(",")))
                for line in test_data.readlines()
            ],
        )
        return benchmark_data
