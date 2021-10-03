import cplex
import argparse
import numpy as np
from time import time
from igraph import Graph

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_data', type=str, help='path to input data',default='')
    return parser.parse_args()


def construct_problem(adjacency_matrix, not_connected_edges: np.array, is_integer: bool, ivs: list):
    if not is_integer:
        type_one = 1.0
        type_zero = 0.0
        var_type = "C"
    else:
        type_one = 1
        type_zero = 0
        var_type = "B"
    
    num_nodes = len(adjacency_matrix)
    obj = [type_one] * len(adjacency_matrix)
    upper_bounds = [type_one] * num_nodes
    lower_bounds = [type_zero] * num_nodes


    types = [var_type] * num_nodes
    columns_names = [f'x{x}' for x in range(num_nodes)]
    right_hand_side = [type_one] * (len(not_connected_edges) + len(ivs))
    constraint_names = [f'c{x}' for x in range(len(not_connected_edges) + len(ivs))]
    constraint_senses = ['L'] * (len(not_connected_edges) + len(ivs))

    problem = cplex.Cplex()
    problem.set_log_stream(None)
    problem.set_results_stream(None)
    problem.set_warning_stream(None)
    problem.set_error_stream(None)
    problem.objective.set_sense(problem.objective.sense.maximize)
    problem.variables.add(obj=obj, ub=upper_bounds, lb=lower_bounds,
                          names=columns_names, types=types)

    constraints = []

    for xi, xj in not_connected_edges:
        constraints.append(
            [['x{0}'.format(xi), 'x{0}'.format(xj)], [type_one, type_one]])
    
    for ind_set in ivs:
        constraints.append([['x{0}'.format(x) for x in ind_set], [type_one] * len(ind_set)])

    problem.linear_constraints.add(lin_expr=constraints,
                                   senses=constraint_senses,
                                   rhs=right_hand_side,
                                   names=constraint_names)
    return problem


def read_and_prepare_data(path: str):
    with open(path, 'r') as file:
        for line in file:
            # graph description
            if line.startswith('c'):  
                continue
            # first line: p name num_of_vertices num_of_edges
            elif line.startswith('p'):
                _, name, vertices_num, edges_num = line.split()
                print(f"{name}, {vertices_num} , {edges_num}")
                adjacency_matrix = np.zeros((int(vertices_num), int(vertices_num)), dtype = np.bool)
            elif line.startswith('e'):
                _, v1, v2 = line.split()
                adjacency_matrix[int(v1) - 1][int(v2) - 1] = 1
            else:
                continue
    return adjacency_matrix


def get_not_connected_inds(adjacency_matrix: np.array):
    data_inv = np.invert(adjacency_matrix, dtype=np.bool)
    inds = np.column_stack(np.tril(data_inv, k=-1).nonzero())
    return inds


def main():
    args = parse_args()
    is_integer = True
    adjacency_matrix = read_and_prepare_data(args.input_data)
    np.fill_diagonal(adjacency_matrix, 1)
    graph = Graph.Adjacency(adjacency_matrix, mode="lower")
    ivs = graph.independent_vertex_sets(min=4, max=6)

    inds = get_not_connected_inds(adjacency_matrix)
    problem_max_clique = construct_problem(adjacency_matrix, inds, is_integer, ivs)  
    problem_max_clique.set_log_stream(None)
    problem_max_clique.set_results_stream(None)
    start = time()
    problem_max_clique.solve()
    print(f"{round(time() - start, 3)} seconds")
    values = problem_max_clique.solution.get_values()
    objective_value = problem_max_clique.solution.get_objective_value()

    print(f"Objective Value: {objective_value}")
    
    for idx in range(len(values)):
        if values[idx] !=0:
            print(f"x_{idx} = {values[idx]}") 

if __name__ == "__main__":
    main()