import cplex
import numpy as np
from algorithms.base import MaxCliqueSolver
from graph import MCPGraph
from utils import *
import math

# TODO Code refactoring


class BNCSolver(MaxCliqueSolver):
    def __init__(
        self,
        graph: MCPGraph,
        branching_strategy: str = "max",
        debug_mode: bool = False,
        tailing_off_time_threshold: int = 3600,
    ):
        super(BNCSolver, self).__init__(
            graph=graph,
            branching_strategy=branching_strategy,
            debug_mode=debug_mode,
        )
        self.cplex_model = self.construct_model()
        self.best_solution = []
        self.maximum_clique_size = 0
        self.eps = 1e-5
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

        right_hand_side = [1.0] * independent_vertex_sets_amount
        constraint_names = [
            f"c{x}" for x in range(independent_vertex_sets_amount)
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

    def separation(self, solution, top_k: int = 2):
        independent_sets = self.graph.independent_sets_generation(
            minimum_set_size=2,
            iteration_number=1,
            max_weighted=True,
            solution=solution,
            strategies=[nx.coloring.strategy_random_sequential],
        )
        sorted_set = sorted(
            independent_sets,
            key=lambda item: item[1],
            reverse=True,
        )
        top_k = min(top_k, len(sorted_set))
        new_constraints = [ind_set[0] for ind_set in sorted_set][:top_k]
        return new_constraints if len(new_constraints) else None

    def get_solution(self):
        try:
            self.cplex_model.solve()
            # get the solution variables and objective value
            current_values = self.cplex_model.solution.get_values()
            current_objective_value = (
                self.cplex_model.solution.get_objective_value()
            )
            if self.debug_mode:
                logger.debug(current_values)
            return current_objective_value, current_values

        except:
            return None, None

    @timeit
    def solve(self):
        self.init_model_with_heuristic_solution()
        self.branch_and_cut()
        solution_nodes = np.where(
            np.isclose(self.best_solution, 1.0, atol=1e-5),
        )
        # log result
        if self.is_clique(solution_nodes[0].tolist()):
            logger.info(
                f"Objective Value of MCP Problem (Maximum Clique Size): {self.maximum_clique_size}. It is a clique!",
            )
            self.is_solution_is_clique = True
        else:
            logger.info(
                f"Objective Value of MCP Problem (Maximum Clique Size): {self.maximum_clique_size}. It is not a clique!",
            )
            self.is_solution_is_clique = False

    @staticmethod
    def get_complement_edges(subgraph):
        graph_complement = nx.complement(subgraph)
        return list(
            filter(lambda edge: edge[0] != edge[1], graph_complement.edges()),
        )

    def check_solution(self, curr_values):
        solution_nodes = np.where(np.isclose(curr_values, 1.0, atol=1e-5))
        is_clique, subgraph = self.is_clique(solution_nodes[0].tolist())
        return None if is_clique else self.get_complement_edges(subgraph)

    def goto_left_branch(self, branching_var, cur_branch):
        # Add Left constraints
        self.add_left_constraint(branching_var, cur_branch)
        self.branch_and_cut()
        self.cplex_model.linear_constraints.delete(f"c{cur_branch}")
        if self.debug_mode:
            logger.info(f"|{self.graph.name}| The c{cur_branch} deleted")

    def goto_right_branch(self, branching_var, cur_branch):
        # Add Right constraints
        self.add_right_constraint(branching_var, cur_branch)
        self.branch_and_cut()
        self.cplex_model.linear_constraints.delete(f"c{cur_branch}")
        if self.debug_mode:
            logger.info(f"|{self.graph.name}| The c{cur_branch} deleted")

    def branch_and_cut(self):
        current_objective_value, current_values = self.get_solution()
        if current_objective_value is None:
            return
        # There is no sense in branching further
        if not self.current_solution_is_best(current_objective_value):
            return
        start_time = time.time()
        while time.time() - start_time <= self.tailing_off_time_threshold:
            new_constraints = self.separation(current_values)
            if new_constraints is None:
                if self.debug_mode:
                    logger.info("No more new separations! ")
                break
            self.add_multiple_constraints(new_constraints)
            current_objective_value, current_values = self.get_solution()
            if current_objective_value is None:
                return
            if not self.current_solution_is_best(current_objective_value):
                return

        self.branch_num += 1
        cur_branch = self.branch_num
        branching_var = self.get_branching_var(current_values)
        if branching_var == -1:
            broken_constraints = self.check_solution(current_values)
            if broken_constraints is not None:
                self.add_multiple_constraints(broken_constraints)
                self.branch_and_cut()
            else:
                self.best_solution = [round(x) for x in current_values]
                self.maximum_clique_size = math.floor(current_objective_value)
            return

        # go to  right branch if value closer to 1
        if round(branching_var[1]):
            self.goto_right_branch(branching_var, cur_branch)
            self.goto_left_branch(branching_var, cur_branch)
        else:
            self.goto_left_branch(branching_var, cur_branch)
            self.goto_right_branch(branching_var, cur_branch)
