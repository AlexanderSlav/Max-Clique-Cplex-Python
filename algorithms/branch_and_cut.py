import math
import random

import cplex
import numpy as np
from algorithms.base import MaxCliqueSolver
from graph import MCPGraph
from utils import *


class BNCSolver(MaxCliqueSolver):
    def __init__(
        self,
        graph: MCPGraph,
        branching_strategy: str = "max",
        debug_mode: bool = False,
        tailing_off_time_threshold: int = 3600,
    ):
        self.graph = graph
        self.branching_strategy = branching_strategy
        self.cplex_model = self.construct_model()
        self.best_solution = []
        self.maximum_clique_size = 0
        self.branch_num = 0
        self.eps = 1e-5
        self.debug_mode = debug_mode
        self.tailing_off_time_threshold = tailing_off_time_threshold
    
    def construct_model(self):
        nodes_amount = len(self.graph.nodes)
        obj = [1.0] * nodes_amount
        upper_bounds = [1.0] * nodes_amount
        lower_bounds = [0.0] * nodes_amount
        types = ["C"] * nodes_amount
        columns_names = [f"x{x}" for x in range(nodes_amount)]

        independent_vertex_sets_amount = len(
            self.graph.independent_vertex_sets,
        )

        right_hand_side = [1.0] * (independent_vertex_sets_amount)
        constraint_names = [
            f"c{x}"
            for x in range(independent_vertex_sets_amount)
        ]
        constraint_senses = ["L"] * independent_vertex_sets_amount

        problem = cplex.Cplex()
        problem.set_results_stream(None)
        problem.set_warning_stream(None)
        problem.set_error_stream(None)
        problem.objective.set_sense(problem.objective.sense.maximize)
        problem.variables.add(
            obj=obj,
            ub=upper_bounds,
            lb=lower_bounds,
            names=columns_names,
            types=types,
        )

        constraints = []
        # set constraints for all vertexes in independent set x_0 + x_1 + ... +  x_i  <=1 with i = len(independent_set)
        for ind_set in self.graph.independent_vertex_sets:
            constraint = [[f"x{i}" for i in ind_set], [1.0] * len(ind_set)]
            constraints.append(constraint)

        problem.linear_constraints.add(
            lin_expr=constraints,
            senses=constraint_senses,
            rhs=right_hand_side,
            names=constraint_names,
        )
        return problem
    
    @timeit
    def separation(self):
        
        pass
    
    @timeit
    def get_solution(self):
        self.cplex_model.solve()
        # get the solution variables and objective value
        current_values = self.cplex_model.solution.get_values()
        current_objective_value = (
            self.cplex_model.solution.get_objective_value()
        )
        if self.debug_mode:
            logger.debug(current_values)
        
        return current_objective_value, current_values
    
    def is_current_solution_is_best(self, current_objective_value):
        current_objective_value = math.ceil(current_objective_value) if not math.isclose(current_objective_value, 
                                                                                        round(current_objective_value), 
                                                                                        rel_tol=1e-5) else current_objective_value
        if current_objective_value <= self.maximum_clique_size:
            if self.debug_mode:
                logger.info(
                    f"|{self.graph.name}| Skip Branch with MCP size {current_objective_value}!",
                )
            return

    @timeit
    def solve(self):
        current_objective_value, current_values = self.get_solution()
        # There is no sense in branching further

        start_time = time.time()
        while time.time() - start_time <= self.tailing_off_time_threshold:
            separation = self.separation()
            if separation is not None:
                # TODO: add constraints 
                current_objective_value, current_values = self.get_solution()
                if 
        # logger.info("Reach time limit at searching ind sets")

        # # branch&bound recursive algorithm
        # self.branching()
        # solution_nodes = np.where(np.isclose(self.best_solution, 1.0, atol=1e-5))

        # # log result
        # if self.is_clique(solution_nodes[0].tolist()):
        #     logger.info(
        #         f"Objective Value of MCP Problem (Maximum Clique Size): {self.maximum_clique_size}. It is a clique!",
        #     )
        #     self.is_solution_is_clique = True
        # else:
        #     logger.info(
        #         f"Objective Value of MCP Problem (Maximum Clique Size): {self.maximum_clique_size}. It is a clique!",
        #     )
        #     self.is_solution_is_clique = False

        # for idx in range(len(self.best_solution)):
        #     if self.best_solution[idx] != 0:
        #         logger.info(f"x_{idx} = {self.best_solution[idx]}")