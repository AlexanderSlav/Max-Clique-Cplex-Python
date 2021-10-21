from graph import Graph
import cplex
from utils import timeit


class BNBSolver:
    def __init__(self, graph: Graph):
        self.graph = graph
        self.cplex_model = self.construct_model()

    def construct_model(self):
        type_one = 1.0
        type_zero = 0.0
        var_type = "C"

        nodes_amount = len(self.graph.nodes)
        obj = [type_one] * nodes_amount
        upper_bounds = [type_one] * nodes_amount
        lower_bounds = [type_zero] * nodes_amount
        types = [var_type] * nodes_amount
        columns_names = [f'x{x}' for x in range(nodes_amount)]

        not_connected_edges_amount = len(self.graph.not_connected_edges)
        independent_vertex_sets_amount = len(self.graph.independent_vertex_sets)

        right_hand_side = [type_one] * (not_connected_edges_amount + independent_vertex_sets_amount)
        constraint_names = [f'c{x}' for x in range(not_connected_edges_amount + independent_vertex_sets_amount)]
        constraint_senses = ['L'] * (not_connected_edges_amount + independent_vertex_sets_amount)

        problem = cplex.Cplex()
        problem.set_log_stream(None)
        problem.set_results_stream(None)
        problem.set_warning_stream(None)
        problem.set_error_stream(None)
        problem.objective.set_sense(problem.objective.sense.maximize)
        problem.variables.add(obj=obj, ub=upper_bounds, lb=lower_bounds,
                              names=columns_names, types=types)

        constraints = []

        for xi, xj in self.graph.not_connected_edges:
            contraint = [['x{0}'.format(xi), 'x{0}'.format(xj)], [type_one, type_one]]
            constraints.append(contraint)

        for ind_set in self.graph.independent_vertex_sets:
            constraint = [['x{0}'.format(x) for x in ind_set], [type_one] * len(ind_set)]
            constraints.append(constraint)

        problem.linear_constraints.add(lin_expr=constraints,
                                       senses=constraint_senses,
                                       rhs=right_hand_side,
                                       names=constraint_names)
        return problem

    @timeit
    def solve(self):
        self.cplex_model.solve()
        values = self.cplex_model.solution.get_values()
        objective_value = self.cplex_model.solution.get_objective_value()

        print(f"Objective Value: {objective_value}")

        for idx in range(len(values)):
            if values[idx] != 0:
                print(f"x_{idx} = {values[idx]}")