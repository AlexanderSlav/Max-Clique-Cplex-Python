import math
import cplex
from graph import MCPGraph
from utils import *
import numpy as np


class MaxCliqueSolver:
    def __init__(
        self,
        graph: MCPGraph,
        branching_strategy: str = "max",
        debug_mode: bool = False,
    ):
        self.graph = graph
        self.branching_strategy = branching_strategy
        self.cplex_model = self.construct_model()
        self.best_solution = []
        self.maximum_clique_size = 0
        self.branch_num = 0
        self.eps = 1e-5
        self.debug_mode = debug_mode

    def construct_model(self):
        problem = cplex.Cplex()
        problem.set_results_stream(None)
        problem.set_warning_stream(None)
        problem.set_error_stream(None)
        problem.objective.set_sense(problem.objective.sense.maximize)
        return problem

    # below code taken from https://stackoverflow.com/questions/59009712/
    # fastest-way-of-checking-if-a-subgraph-is-a-clique-in-networkx
    def is_clique(self, nodelist):
        chek_subgraph = self.graph.graph.subgraph(nodelist)
        num_nodes = len(nodelist)
        return chek_subgraph.size() == num_nodes * (num_nodes - 1) / 2

    @timeit
    def solve(self):
        raise NotImplementedError

    def add_left_constraint(self, branching_var: tuple, current_branch: int):
        branching_var_idx, branching_var_value = branching_var
        # solver sometime can produce variables like that -1.1102230246251565e-16 and math.floor() round it to -1
        if math.floor(branching_var_value) == -1:
            branching_var_value = 0
        right_hand_side = [math.floor(branching_var_value)]
        if self.debug_mode:
            logger.info(
                f"|{self.graph.name}| Adding left constraint x{branching_var_idx} == {math.floor(branching_var_value)}",
            )
        self.cplex_model.linear_constraints.add(
            lin_expr=[[[f"x{branching_var_idx}"], [1.0]]],
            senses=["E"],
            rhs=right_hand_side,
            names=[f"c{current_branch}"],
        )

    def add_right_constraint(self, branching_var: tuple, current_branch: int):
        branching_var_idx, branching_var_value = branching_var
        right_hand_side = [math.ceil(branching_var_value)]
        if self.debug_mode:
            logger.info(
                f"|{self.graph.name}| Adding right constraint x{branching_var_idx} == {math.ceil(branching_var_value)}",
            )
        self.cplex_model.linear_constraints.add(
            lin_expr=[[[f"x{branching_var_idx}"], [1.0]]],
            senses=["E"],
            rhs=right_hand_side,
            names=[f"c{current_branch}"],
        )


    def init_model_with_heuristic_solution(self):
        # helper function
        def generate_init_best_solution(best_heuristic_sol):
            solution = np.zeros(len(self.graph.nodes))
            solution[list(best_heuristic_sol)] = 1
            return solution

        # apply greedy heuristic first
        best_heuristic_sol, _ = self.initial_heuristic()
        is_clique = self.is_clique(list(best_heuristic_sol))
        if is_clique:
            logger.info(f"Initial heuristic solution is clique!")
            self.best_solution = generate_init_best_solution(
                best_heuristic_sol,
            )
            self.maximum_clique_size = len(best_heuristic_sol)
            logger.info(
                f"Initial heuristic: Start best MCP size {self.maximum_clique_size}",
            )
            logger.info(
                f"Initial heuristic: Start best MCP solution {self.best_solution}",
            )
        else:
            logger.info(f"Initial heuristic solution is not clique!")
            raise Exception("The Initial Heuristic has a mistake !!!")

        
    @timeit
    def initial_heuristic(self):
        """Greedy Init Heuristic

        # :return:
        # Max Clique by Heuristic: set
        """
        logger.info("Initial heuristic working")
        best_clique = set()
        for vertex in self.graph.nodes:
            current_clique = set()
            current_clique.add(vertex)
            vertexes_degree = {
                vertex: self.graph.graph.degree(vertex)
                for vertex in self.graph.graph.neighbors(vertex)
            }
            while True:
                max_degree_vertex = max(
                    vertexes_degree,
                    key=vertexes_degree.get,
                )
                current_clique.add(max_degree_vertex)

                max_degree_vertex_neighbors = {
                    vertex: self.graph.graph.degree(vertex)
                    for vertex in self.graph.graph.neighbors(max_degree_vertex)
                }

                vertexes_degree = {
                    vertex: vertexes_degree[vertex]
                    for vertex in set(vertexes_degree).intersection(
                        set(max_degree_vertex_neighbors),
                    )
                }
                if not vertexes_degree:
                    break

            if len(current_clique) > len(best_clique):
                best_clique = current_clique
        return best_clique
