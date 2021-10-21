import numpy as np
import networkx as nx
from typing import Union
from loguru import logger
from utils import timeit


class Graph:
    def __init__(self, data: Union[str, np.ndarray]):
        if isinstance(data, str):
            adj_matrix = self.read_and_prepare_data(data)
            self.graph = nx.from_numpy_array(adj_matrix)
        elif isinstance(data, np.ndarray):
            self.graph = nx.from_numpy_array(data)
        else:
            logger.error(f"\n Wrong input data format: {type(data)}\n "
                         f"Should be <str> - (path to data)  or <np.ndarray> (adjacency matrix)")
        self.independent_vertex_sets = []
        self.not_connected_vertexes = nx.complement(self.graph).edges
        self.nodes = self.graph.nodes

    @timeit
    def apply_coloring(self):
        """Inplace independent_vertex_sets generation

        Returns:
        Nothing returns. Function update self.independent_vertex_sets field
       """

        # define strategies for graph coloring
        strategies = [nx.coloring.strategy_largest_first,
                      nx.coloring.strategy_smallest_last,
                      nx.coloring.strategy_independent_set,
                      nx.coloring.strategy_saturation_largest_first]

        for strategy in strategies:
            # get coloring with current strategy: running_coloring - dict(key=vertex, value=color)
            running_coloring = nx.coloring.greedy_color(self.graph, strategy=strategy)
            for unique_color in set(running_coloring.values()):
                self.independent_vertex_sets.append([vertex for vertex, color in running_coloring.items()
                                                     if color == unique_color])

    @staticmethod
    def read_and_prepare_data(path: str):
        """Read the graph data from file and convert it to adjacency matrix

        Parameters:
        path (str): Path to the file with DIMACS graph description

        Returns:
        np.ndarray: adjacency matrix

       """
        with open(path, 'r') as file:
            for line in file:
                # graph description
                if line.startswith('c'):
                    continue
                # first line: p name num_of_vertices num_of_edges
                elif line.startswith('p'):
                    _, name, vertices_num, edges_num = line.split()
                    logger.info(f"Graph description: Vertexes number: {vertices_num} , Edges number: {edges_num}")
                    adjacency_matrix = np.zeros((int(vertices_num), int(vertices_num)), dtype=np.bool)
                elif line.startswith('e'):
                    _, v1, v2 = line.split()
                    adjacency_matrix[int(v1) - 1][int(v2) - 1] = 1
                else:
                    continue
        return adjacency_matrix
