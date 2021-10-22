from graph import Graph
import cplex
from utils import *
import math
import random
import numpy as np


class BNBSolver:
    """The solver work pipeline:
     1. Cplex Model Construction
     2. Initial Heuristic
     3. BnB recursive call
    """
    def __init__(self, graph: Graph, branching_strategy: str = "random"):
        self.graph = graph
        self.branching_strategy = branching_strategy
        self.cplex_model = self.construct_model()
        self.best_solution = []
        self.maximum_clique_size = 0
        self.branch_num = 0
        self.eps = 1e-5

    def construct_model(self):
        nodes_amount = len(self.graph.nodes)
        obj = [1.0] * nodes_amount
        upper_bounds = [1.0] * nodes_amount
        lower_bounds = [0.0] * nodes_amount
        types = ["C"] * nodes_amount
        columns_names = [f'x{x}' for x in range(nodes_amount)]

        not_connected_edges_amount = len(self.graph.not_connected_vertexes)
        independent_vertex_sets_amount = len(self.graph.independent_vertex_sets)

        right_hand_side = [1.0] * (not_connected_edges_amount + independent_vertex_sets_amount)
        constraint_names = [f'c{x}' for x in range(not_connected_edges_amount + independent_vertex_sets_amount)]
        constraint_senses = ['L'] * (not_connected_edges_amount + independent_vertex_sets_amount)

        problem = cplex.Cplex()
        problem.set_results_stream(None)
        problem.set_warning_stream(None)
        problem.set_error_stream(None)
        problem.objective.set_sense(problem.objective.sense.maximize)
        problem.variables.add(obj=obj, ub=upper_bounds, lb=lower_bounds,
                              names=columns_names, types=types)

        constraints = []
        # set constraints for all vertexes in independent set x_0 + x_1 + ... +  x_i  <=1 with i = len(independent_set)
        for ind_set in self.graph.independent_vertex_sets:
            constraint = [[f"x{i}" for i in ind_set], [1.0] * len(ind_set)]
            constraints.append(constraint)

        # set constraints for not connected edges x_i + x_j <=1
        for xi, xj in self.graph.not_connected_vertexes:
            contraint = [[f"x{xi}", f"x{xj}"], [1.0, 1.0]]
            constraints.append(contraint)

        problem.linear_constraints.add(lin_expr=constraints,
                                       senses=constraint_senses,
                                       rhs=right_hand_side,
                                       names=constraint_names)
        return problem

    @timeit
    def solve(self):
        # self.initial_heuristic()
        logger.info(f"Current best MCP size {self.maximum_clique_size}")
        self.branching()
        logger.info(f"Objective Value of MCP Problem (Maximum Clique Size): {self.maximum_clique_size}")
        for idx in range(len(self.best_solution)):
            if self.best_solution[idx] != 0:
                logger.info(f"x_{idx} = {self.best_solution[idx]}")

    def branching(self):
        self.cplex_model.solve()
        current_values = self.cplex_model.solution.get_values()
        current_objective_value = self.cplex_model.solution.get_objective_value()
        logger.debug(current_values)
        # There is no sense in branching further
        if current_objective_value <= self.maximum_clique_size:
            logger.info(f"Skip Branch with MCP size {current_objective_value}!")
            return

        if all([math.isclose(x, np.round(x), rel_tol=self.eps) for x in current_values]):
            # Best Solution updated.
            self.best_solution = [round(x) for x in current_values]
            self.maximum_clique_size = math.floor(current_objective_value)
            logger.info(f"Best Solution updated. New value is {self.maximum_clique_size}")
            return

        self.branch_num += 1
        cur_branch = self.branch_num
        # Choose branching var from non integers vars
        if self.branching_strategy == "max":
            not_integer_vars = [(idx, x) for idx, x in enumerate(current_values)
                                if not math.isclose(x, np.round(x), rel_tol=self.eps)]

            branching_var = max(not_integer_vars, key=lambda x: x[1])
        elif self.branching_strategy == "random":
            not_integer_vars = [(idx, x) for idx, x in enumerate(current_values)
                                if not math.isclose(x, np.round(x), rel_tol=self.eps)]
            branching_var = random.choice(not_integer_vars)

        else:
            logger.error("Wrong branching strategy")

        # Add Left constraints
        self.add_left_constraint(branching_var, cur_branch)
        self.branching()
        self.cplex_model.linear_constraints.delete(f'c{cur_branch}')
        logger.info(f"The c{cur_branch} deleted")

        # Add Right constraints
        self.add_right_constraint(branching_var, cur_branch)
        self.branching()
        self.cplex_model.linear_constraints.delete(f'c{cur_branch}')

    def add_left_constraint(self, branching_var: tuple, current_branch: int):
        branching_var_idx, branching_var_value = branching_var
        right_hand_side = [math.floor(branching_var_value)]
        logger.info(f"Adding left constraint x{branching_var_idx} == {math.floor(branching_var_value)}")
        self.cplex_model.linear_constraints.add(lin_expr=[[[f"x{branching_var_idx}"], [1.0]]],
                                                senses=['E'],
                                                rhs=right_hand_side,
                                                names=[f'c{current_branch}'])

    def add_right_constraint(self, branching_var: tuple, current_branch: int):
        branching_var_idx, branching_var_value = branching_var
        right_hand_side = [math.ceil(branching_var_value)]
        logger.info(f"Adding right constraint x{branching_var_idx} == {math.ceil(branching_var_value)}")
        self.cplex_model.linear_constraints.add(lin_expr=[[[f"x{branching_var_idx}"], [1.0]]],
                                                senses=['E'],
                                                rhs=right_hand_side,
                                                names=[f'c{current_branch}'])

    def initial_heuristic(self):
        #TODO Implement
        logger.info("Initial heuristic working")
        pass
