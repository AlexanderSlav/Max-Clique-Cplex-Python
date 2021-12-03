from typing import Union
import numpy as np
from utils import *
from math import inf


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

    def independent_sets_generation(
        self,
        minimum_set_size: int = 3,
        iteration_number: int = 50,
        time_limit: int = 500,
        max_weighted: bool = False,
        solution=None,
        strategies=STRATEGIES,
    ):
        """Independent Vertex Sets generation via graph coloring

            This function is also solve Max Weighted Independent Sets problem (Not a proper way of solve
                                                                                            it via coloring. I know)

        Returns:
        Nothing returns. Function update self.independent_vertex_sets field if max_weighted = False
                                                                            else return set of weighted ind sets
        """
        generated_independent_sets = (
            self.independent_vertex_sets if not max_weighted else set()
        )
        if len(self.graph.nodes) < 500 and not max_weighted:
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

                    if not max_weighted:
                        dict_of_independet_sets[color].append(vertex)
                    else:
                        dict_of_independet_sets[color].append(
                            (vertex, solution[vertex]),
                        )

                for _, ind_set in dict_of_independet_sets.items():
                    set_weight = (
                        sum(vertex[1] for vertex in ind_set)
                        if max_weighted
                        else inf
                    )
                    ind_set = (
                        [vertex[0] for vertex in ind_set]
                        if max_weighted
                        else ind_set
                    )
                    if max_weighted:
                        if (
                            len(ind_set) >= minimum_set_size
                            and set_weight > 1 + EPS
                        ):
                            generated_independent_sets.add(
                                tuple((tuple(ind_set), set_weight)),
                            )
                    else:
                        if len(ind_set) >= minimum_set_size:
                            generated_independent_sets.add(
                                tuple(sorted(ind_set)),
                            )
        if max_weighted:
            return generated_independent_sets

    def filter_covered_not_connected(self, filtration_limit: int = 300000):
        filtered_not_connected = []
        for idx, not_connected_vertexes in enumerate(
            self.not_connected_vertexes,
        ):
            vertexes_are_covered_by_set = False
            vertex_1, vertex_2 = not_connected_vertexes
            if idx < filtration_limit:
                for ind_set in self.independent_vertex_sets:
                    if (vertex_1 in ind_set) and (vertex_2 in ind_set):
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
