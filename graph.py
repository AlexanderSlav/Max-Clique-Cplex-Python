from typing import Union

import networkx as nx
import numpy as np

from utils import *


class MCPGraph:
    def __init__(self, data: Union[str, np.ndarray, namedtuple]):
        if isinstance(data, tuple):
            adj_matrix = self.read_and_prepare_data(
                osp.join(SOURCE_GRAPH_DIR, data.GraphName),
            )
            self.graph = nx.from_numpy_array(adj_matrix)
            # the graph name without extension
            self.name = data.GraphName[:-4]
            # right answer for MCP
            self.maximum_clique_size_gt = int(data.CorrectMaxClique)
            self.complexity_type = data.Level

        elif isinstance(data, str):
            adj_matrix = self.read_and_prepare_data(data)
            self.graph = nx.from_numpy_array(adj_matrix)
            self.name = osp.basename(data)[:-4]
            self.maximum_clique_size_gt = None
            self.complexity_type = None

        elif isinstance(data, np.ndarray):
            self.graph = nx.from_numpy_array(data)
            self.name = None
            self.maximum_clique_size_gt = None
            self.complexity_type = None

        else:
            logger.error(
                f"\n Wrong input data format: {type(data)}\n "
                f"Should be <str> - (path to data)  or <np.ndarray> (adjacency matrix) or NamedTuple",
            )
        self.maximum_clique_size_found = -1
        self.independent_vertex_sets = set()
        self.not_connected_vertexes = nx.complement(self.graph).edges
        self.nodes = self.graph.nodes
        self.is_solution_is_clique = None

    @timeit
    def apply_coloring(
        self,
        minimum_set_size: int = 3,
        iteration_number: int = 50,
        time_limit: int = 500,
    ):
        """Inplace independent_vertex_sets generation

        Returns:
        Nothing returns. Function update self.independent_vertex_sets field
        """

        # define strategies for graph coloring
        strategies = [
            nx.coloring.strategy_largest_first,
            nx.coloring.strategy_random_sequential,
            nx.coloring.strategy_connected_sequential_bfs,
            nx.coloring.strategy_saturation_largest_first,
            nx.coloring.strategy_smallest_last,
        ]
        if len(self.graph.nodes) < 500:
            strategies.append(
                nx.coloring.strategy_independent_set,
            )
        start_time = time.time()
        for _ in range(iteration_number):
            if time.time() - start_time >= time_limit:
                logger.info("Reach time limit at searching ind sets")
                break

            for strategy in strategies:
                dict_of_independet_sets = dict()
                # get coloring with current strategy: running_coloring - dict(key=vertex, value=color)
                running_coloring = nx.coloring.greedy_color(
                    self.graph,
                    strategy=strategy,
                )
                for vertex, color in running_coloring.items():
                    if color not in dict_of_independet_sets.keys():
                        dict_of_independet_sets[color] = []
                    dict_of_independet_sets[color].append(vertex)

                for _, ind_set in dict_of_independet_sets.items():
                    if len(ind_set) >= minimum_set_size:
                        self.independent_vertex_sets.add(
                            tuple(sorted(ind_set)),
                        )

    def filter_covered_not_connected(self, filtration_limit: int = 300000):
        filtered_not_connected = []
        for idx, not_connected_vertexes in enumerate(
            self.not_connected_vertexes,
        ):
            vertexes_are_covered_by_set = False
            vertex_1, vetex_2 = not_connected_vertexes
            if idx < filtration_limit:
                for ind_set in self.independent_vertex_sets:
                    if (vertex_1 in ind_set) and (vetex_2 in ind_set):
                        vertexes_are_covered_by_set = True
                        break
            if not vertexes_are_covered_by_set:
                filtered_not_connected.append(not_connected_vertexes)
        self.not_connected_vertexes = filtered_not_connected

    @staticmethod
    def read_and_prepare_data(path: str):
        """Read the graph data from file and convert it to adjacency matrix

        Parameters:
        path (str): Path to the file with DIMACS graph description

        Returns:
        np.ndarray: adjacency matrix

        """
        with open(path, "r") as file:
            for line in file:
                # graph description
                if line.startswith("c"):
                    continue
                # first line: p name num_of_vertices num_of_edges
                elif line.startswith("p"):
                    _, name, vertices_num, edges_num = line.split()
                    logger.info(
                        f"Graph description: Vertexes number: {vertices_num} , Edges number: {edges_num}",
                    )
                    adjacency_matrix = np.zeros(
                        (int(vertices_num), int(vertices_num)),
                        dtype=np.bool,
                    )
                elif line.startswith("e"):
                    _, v1, v2 = line.split()
                    adjacency_matrix[int(v1) - 1][int(v2) - 1] = 1
                else:
                    continue
        return adjacency_matrix

    def __repr__(self):
        return (
            f"Ground Truth Max Clique Size: {self.maximum_clique_size_gt} \n"
            f"Found Max Clique Size: {self.maximum_clique_size_found}\n"
        )
