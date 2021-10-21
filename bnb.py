from graph import Graph
import cplex


class BNBSolver:
    def __init__(self, graph: Graph, is_integer: bool = True):
        self.graph = graph
        self.is_integer = is_integer
        self.cplex_model = self.construct_model()

    def construct_model(self):
        if not self.is_integer:
            type_one = 1.0
            type_zero = 0.0
            var_type = "C"
        else:
            type_one = 1
            type_zero = 0
            var_type = "B"

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


graph = Graph(data="/home/alexander/HSE_Stuff/Max_Clique/DIMACS_subset_ascii/C125.9.clq")
graph.coloring()
bnb_solver = BNBSolver(graph=graph)
print(bnb_solver.cplex_model)