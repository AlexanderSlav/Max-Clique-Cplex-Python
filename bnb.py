from graph import Graph
import cplex
from utils import *
import math
import random


class BNBSolver:
    """The solver work pipeline:
     1. Cplex Model Construction
     2. Initial Heuristic
     3. BnB recursive call
    """
    def __init__(self, graph: Graph):
        self.graph = graph
        self.cplex_model = self.construct_model()
        self.best_solution = []
        self.maximum_clique_size = -1
        self.branch_num = 0

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
        problem.objective.set_sense(problem.objective.sense.maximize)
        problem.variables.add(obj=obj, ub=upper_bounds, lb=lower_bounds,
                              names=columns_names, types=types)

        constraints = []
        # set constraints for not connected edges x_i + x_j <=1
        for xi, xj in self.graph.not_connected_vertexes:
            contraint = [['x{0}'.format(xi), 'x{0}'.format(xj)], [1.0, 1.0]]
            constraints.append(contraint)
        # set constraints for all vertexes in independent set x_0 + x_1 + ... +  x_i  <=1 with i = len(independent_set)
        for ind_set in self.graph.independent_vertex_sets:
            constraint = [['x{0}'.format(x) for x in ind_set], [1.0] * len(ind_set)]
            constraints.append(constraint)

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
        print(f"Objective Value of MCP Problem (Maximum Clique Size): {self.maximum_clique_size}")
        for idx in range(len(self.best_solution)):
            if self.best_solution[idx] != 0:
                print(f"x_{idx} = {self.best_solution[idx]}")

    def branching(self):
        try:
            self.cplex_model.solve()
        except cplex.exceptions.errors.CplexSolverError:
            return
        current_values = self.cplex_model.solution.get_values()
        current_objective_value = self.cplex_model.solution.get_objective_value()
        logger.debug(current_values)
        # There is no sense in branching further
        if current_objective_value <= self.maximum_clique_size:
            logger.info(f"Skip Branch with MCP size {current_objective_value}!")
            return

        if all(x.is_integer() for x in current_values):
            # Best Solution updated.
            self.best_solution = [round(x) for x in current_values]
            self.maximum_clique_size = math.floor(current_objective_value)
            logger.info(f"Best Solution updated. New value is {self.maximum_clique_size}")
            return

        self.branch_num += 1
        cur_branch = self.branch_num
        # Randomly choose branching var from non integers vars
        not_integer_vars = [(idx, x) for idx, x in enumerate(current_values) if not x.is_integer()]
        branching_var = random.choice(not_integer_vars)

        # Add Left constraints
        self.add_left_constraint(branching_var)
        self.branching()
        self.cplex_model.linear_constraints.delete(f'c{cur_branch}')

        # Add Right constraints
        self.add_right_constraint(branching_var)
        self.branching()
        self.cplex_model.linear_constraints.delete(f'c{cur_branch}')

    def add_left_constraint(self, branching_var: tuple):
        branching_var_idx, branching_var_value = branching_var
        right_hand_side = [math.floor(branching_var_value)]
        logger.info(f"Adding left constraint x{branching_var_idx} <= {math.floor(branching_var_value)}")
        self.cplex_model.linear_constraints.add(lin_expr=[[[f"x{branching_var_idx}"], right_hand_side]],
                                                senses=['L'],
                                                rhs=right_hand_side,
                                                names=[f'c{branching_var_idx}'])

    def add_right_constraint(self, branching_var: tuple):
        branching_var_idx, branching_var_value = branching_var
        right_hand_side = [math.ceil(branching_var_value)]
        logger.info(f"Adding right constraint x{branching_var_idx} >= {math.ceil(branching_var_value)}")
        self.cplex_model.linear_constraints.add(lin_expr=[[[f"x{branching_var_idx}"], right_hand_side]],
                                                senses=['G'],
                                                rhs=right_hand_side,
                                                names=[f'c{branching_var_idx}'])

    def initial_heuristic(self):
        #TODO Implement
        logger.info("Initial heuristic working")
        pass
