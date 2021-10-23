import numpy as np
import networkx as nx
from typing import Union
from utils import *
from collections import namedtuple
import csv


class MCPGraph:
    def __init__(self, data: Union[str, np.ndarray, namedtuple]):
        if isinstance(data, tuple):
            adj_matrix = self.read_and_prepare_data(osp.join(DATA_DIR, data.GraphName))
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
            logger.error(f"\n Wrong input data format: {type(data)}\n "
                         f"Should be <str> - (path to data)  or <np.ndarray> (adjacency matrix)")
        self.maximum_clique_size_found = -1
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
                      nx.coloring.strategy_random_sequential,
                      nx.coloring.strategy_independent_set,
                      nx.coloring.strategy_connected_sequential_bfs,
                      nx.coloring.strategy_connected_sequential_dfs,
                      nx.coloring.strategy_saturation_largest_first,
                      nx.coloring.strategy_smallest_last]

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

    def __repr__(self):
        return f"Ground Truth Max Clique Size: {self.maximum_clique_size_gt} \n" \
               f"Found Max Clique Size: {self.maximum_clique_size_found}\n"
