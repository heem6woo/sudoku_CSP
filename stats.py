import statistics
from copy import deepcopy
import time
import random

import stats
from main import SudokuCSP, BackTrack, BackTrackFC, BackTrackFCH, easy, medium, hard, evil, verifying


# Calculate the average time for a given level and algorithm
def calculate_average_time(level, algorithm):
    total_time = 0.0
    total_nodes = 0
    it = 0
    num_iterations = 50
    sudoku = None

    times = []
    nodes = []

    while it < num_iterations:
        if level == "easy":
            sudoku = deepcopy(easy)

        elif level == "medium":
            sudoku = deepcopy(medium)

        elif level == "hard":
            sudoku = deepcopy(hard)

        elif level == "evil":
            sudoku = deepcopy(evil)

        csp = SudokuCSP(sudoku)

        assignment = {}

        start_time = time.time()

        retval = False
        if algorithm == "B":
            retval = BackTrack(assignment, csp)
        elif algorithm == "BFC":
            retval = BackTrackFC(assignment, csp)
        elif algorithm == "BFCH":
            retval = BackTrackFCH(assignment, csp)

        end_time = time.time()
        elapsed_time = end_time - start_time
        total_time += elapsed_time
        total_nodes += csp.expanded_nodes

        for row, col in assignment:
            sudoku[row][col] = assignment[row, col]

        if not verifying(csp.constraints) or not retval:
            total_time -= elapsed_time
            total_nodes -= csp.expanded_nodes
            continue
        times.append(elapsed_time)
        nodes.append(csp.expanded_nodes)
        it += 1

    average_time = total_time / num_iterations
    average_nodes = total_nodes / num_iterations

    # Calculate standard deviation
    squared_diffs_times = [(time - average_time) ** 2 for time in times]
    mean_squared_diff_time = sum(squared_diffs_times) / num_iterations
    standard_deviation_t = statistics.sqrt(mean_squared_diff_time)

    squared_diffs_nodes = [(node - average_nodes) ** 2 for node in nodes]
    mean_squared_diff_node = sum(squared_diffs_nodes) / num_iterations
    standard_deviation_n = statistics.sqrt(mean_squared_diff_node)

    return average_time, standard_deviation_t, average_nodes, standard_deviation_n


# Main code
if __name__ == '__main__':
    #'easy', 'medium', 'hard',
    levels = [ 'evil']
    #'B',,"BFCH"'BFCH', 'BFC',
    algorithms = [ 'B']
    f = open("results.txt", "w")
    for algorithm in algorithms:
        for level in levels:
            #try:
            average_time, standard_deviation_t, average_nodes, standard_deviation_n = calculate_average_time(level, algorithm)
            print(f"Average time for level {level} and algorithm {algorithm}:\n\t {average_time} seconds, {standard_deviation_t} std seconds, \n\t {average_nodes} nodes, {standard_deviation_n} std nodes")
            with open("results.txt", "a") as file:
                file.write("Level: " + level + "\n")
                file.write("Algorithm: " + algorithm + "\n")
                file.write("Average Time: " + str(average_time) + "\n")
                file.write("Standard Deviation Time: " + str(standard_deviation_t) + "\n")
                file.write("Average Nodes: " + str(average_nodes) + "\n")
                file.write("Standard Deviation Nodes: " + str(standard_deviation_n) + "\n")
                file.write("\n")
            #except:
                #print(f"There is an Error in level {level} and algorithm {algorithm}")
