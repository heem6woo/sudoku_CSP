# Sudoku Puzzle with CSP
import time
from copy import deepcopy
import random

# assignment

# variable the empty assignments
# domain 1..9
# constraints
# 1. A cell in the same column cannot have same domain Ci,j != Ck,j for k != i
# 2. A cell in the same row cannot have same domain Cj,i != Cj,k for k != i
# 3. A cell in the same box cannot have same domain
# Box 1  0 <= i <= 2, 0 <= j <= 2
# Box 2  3 <= i <= 5, 0 <= j <= 2
# Box 3  0 <= i <= 2, 0 <= j <= 2

easy = [[0, 5, 8, 0, 6, 2, 1, 0, 0],
        [0, 0, 2, 7, 0, 0, 4, 0, 0],
        [0, 6, 7, 9, 0, 1, 2, 5, 0],
        [0, 8, 6, 3, 4, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 7, 6, 8, 9, 0],
        [0, 2, 9, 6, 0, 8, 7, 4, 0],
        [0, 0, 3, 0, 0, 4, 9, 0, 0],
        [0, 0, 5, 2, 9, 0, 3, 8, 0]]

medium = [[8, 3, 0, 6, 0, 0, 0, 0, 7],
          [0, 0, 7, 0, 2, 0, 0, 5, 0],
          [0, 2, 1, 0, 0, 9, 0, 8, 0],
          [6, 0, 0, 0, 8, 0, 0, 0, 9],
          [0, 0, 0, 4, 6, 5, 0, 0, 0],
          [3, 0, 0, 0, 9, 0, 0, 0, 2],
          [0, 8, 0, 2, 0, 0, 3, 9, 0],
          [0, 5, 0, 0, 4, 0, 2, 0, 0],
          [2, 0, 0, 0, 0, 8, 0, 1, 6]]

hard = [[1, 0, 0, 0, 3, 0, 0, 0, 0],
        [0, 6, 2, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 7, 0, 2, 8, 0, 4],
        [0, 7, 0, 1, 4, 0, 0, 0, 2],
        [0, 4, 0, 0, 0, 0, 0, 9, 0],
        [8, 0, 0, 0, 5, 6, 0, 7, 0],
        [6, 0, 9, 8, 0, 7, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 2, 1, 0],
        [0, 0, 0, 0, 6, 0, 0, 0, 9]]

evil = [[0, 1, 0, 0, 0, 0, 0, 0, 6],
        [9, 0, 0, 2, 0, 0, 0, 0, 0],
        [7, 3, 2, 0, 4, 0, 0, 1, 0],
        [0, 4, 8, 3, 0, 0, 0, 0, 2],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [3, 0, 0, 0, 0, 4, 6, 7, 0],
        [0, 9, 0, 0, 3, 0, 5, 6, 8],
        [0, 0, 0, 0, 0, 2, 0, 0, 1],
        [6, 0, 0, 0, 0, 0, 0, 3, 0]]

zeros = [[0 for _ in range(9)] for _ in range(9)]

class SudokuCSP:
    sudoku: list[list[int]] = []
    expanded_nodes = 0
    forward_fails = 0

    def __init__(self, board: list[list[int]]):
        self.sudoku = board
        self.variables = []  # empty cells, value == 0, 0 ... 80   Ci,j = i + (j * 9)
        self.domains = {}  # dictionary variable : domain
        self.constraints = []
        self.neighbors = {}

        self.constraintsInit()
        self.variableInit()
        self.domainInit()
        self.neighborsInit()
        self.expanded_nodes = 0

    def neighborsInit(self):
        for var in self.variables:
            neighbor = []
            for v in self.variables:
                if v != var and Connected(var, v):
                    neighbor.append(v)
            self.neighbors[var] = neighbor

    def constraintsInit(self):

        rows = [set(cell for cell in row if cell != 0) for row in self.sudoku]
        cols = [set(self.sudoku[row][col] for row in range(9) if self.sudoku[row][col] != 0) for col in range(9)]
        boxes = []
        for row in range(0, 9, 3):
            for col in range(0, 9, 3):
                box = set()
                for i in range(3):
                    for j in range(3):
                        cell = self.sudoku[row + i][col + j]
                        if cell != 0:
                            box.add(cell)
                boxes.append(box)

        self.constraints = [rows, cols, boxes]

    def variableInit(self):

        self.variables = [(row, col) for row in range(9) for col in range(9) if self.sudoku[row][col] == 0]
        random.shuffle(self.variables)

    # should be initiated after variables are initiated
    def domainInit(self):

        for row, col in self.variables:
            domain = []
            for d in range(1, 10):
                if (d in self.constraints[0][row]) or (d in self.constraints[1][col]) or (d in self.constraints[2][
                    find_box(row, col)]):
                    continue
                else:
                    domain.append(d)
            random.shuffle(domain)

            self.domains[row, col] = domain


def find_box(row, col):
    box_row = row // 3
    box_col = col // 3
    box_number = (box_row * 3) + box_col
    return box_number


def BackTrack(assignment: dict, csp: SudokuCSP):  # return true or false

    if len(assignment) == len(csp.variables):
        return True

    # ChoooseVarInOrder
    var = csp.variables[len(assignment)]
    r, c = var

    domain = csp.domains[var]

    for d in domain:
        if d not in csp.constraints[0][r] and \
                d not in csp.constraints[1][c] and \
                d not in csp.constraints[2][find_box(r, c)]:

            assignment[var] = d

            csp.constraints[0][r].add(d)
            csp.constraints[1][c].add(d)
            csp.constraints[2][find_box(r, c)].add(d)

            csp.expanded_nodes += 1
            retval = BackTrack(assignment, csp)

            if retval:
                return True

            assignment.pop(var)

            csp.constraints[0][r].remove(d)
            csp.constraints[1][c].remove(d)
            csp.constraints[2][find_box(r, c)].remove(d)

    return False

#Backtrack with Forward Checking
def BackTrackFC(assignment: dict, csp: SudokuCSP):  # return true or false

    if len(assignment) == len(csp.variables):
        return True

    # ChoooseVarInOrder
    var = csp.variables[len(assignment)]
    r, c = var

    domain = csp.domains[var]

    for d in domain:
        if d not in csp.constraints[0][r] and \
                d not in csp.constraints[1][c] and \
                d not in csp.constraints[2][find_box(r, c)]:

            assignment[var] = d

            csp.constraints[0][r].add(d)
            csp.constraints[1][c].add(d)
            csp.constraints[2][find_box(r, c)].add(d)

            domains = deepcopy(csp.domains)

            forward, neighbor = ForwardChecking(csp, assignment, var, d)

            if forward:
                csp.expanded_nodes += 1
                retval = BackTrackFC(assignment, csp)
                if retval:
                    return True
                #ForwardBackup(csp, neighbor, var, d)
            # back up the domain

            csp.domains = domains

            assignment.pop(var)

            csp.constraints[0][r].remove(d)
            csp.constraints[1][c].remove(d)
            csp.constraints[2][find_box(r, c)].remove(d)

    return False

#BackTrack with Forward Checking + 3Heuristic(MRV + Degree + LCV)
def BackTrackFCH(assignment: dict, csp: SudokuCSP):  # return true or false

    if len(assignment) == len(csp.variables):
        return True

    # Fewest Domain First (MRV) minimum-remaining-values
    vars = MRV(csp.domains, assignment)

    if len(vars) > 1:
        var = Degree(vars, csp)
    else:
        var = vars[0]
    r, c = var

    domain = LCV(var, assignment, csp)

    for d in domain:
        if d not in csp.constraints[0][r] and \
                d not in csp.constraints[1][c] and \
                d not in csp.constraints[2][find_box(r, c)]:

            assignment[var] = d

            csp.constraints[0][r].add(d)
            csp.constraints[1][c].add(d)
            csp.constraints[2][find_box(r, c)].add(d)

            domains = deepcopy(csp.domains)

            forward, neighbor = ForwardChecking(csp, assignment, var, d)

            if forward:
                csp.expanded_nodes += 1
                retval = BackTrackFCH(assignment, csp)
                if retval:
                    return True
                #ForwardBackup(csp, neighbor, var, d)
            # back up the domain

            csp.domains = domains

            assignment.pop(var)

            csp.constraints[0][r].remove(d)
            csp.constraints[1][c].remove(d)
            csp.constraints[2][find_box(r, c)].remove(d)

    return False


def MRV(domains: dict, assignment):
    min_value_size = float('inf')
    keys_with_min_value = []

    for key, value in domains.items():
        value_size = len(value)
        if key not in assignment and value_size < min_value_size:
            min_value_size = value_size
            keys_with_min_value = [key]
        elif value_size == min_value_size:
            keys_with_min_value.append(key)

    return keys_with_min_value


def LCV(var, assignment, csp):
    r, c = var
    b = find_box(r, c)
    values = csp.domains[var]

    def count_constrained_values(value):
        count = 0
        for v in csp.variables:
            if v not in assignment and Connected(var, v):
                if value in csp.domains[v]:
                    count += 1
        return count

    values.sort(key=count_constrained_values)

    return values


# tie-breaker for MRV, if there are more than one MRVs, then choose by degree heuristic
# return the most
def Degree(vars: list, csp: SudokuCSP):
    return min(vars, key=lambda var: len(csp.domains[var]))


def ForwardBackup(csp: SudokuCSP, neighbor, var: tuple, val: int):
    for v in neighbor:
        # any variables connected to var, same row, same col or same box
        if val not in csp.domains[v]:
            csp.domains[v].append(val)

"""
def ForwardChecking(csp: SudokuCSP, assignment, var: tuple, val: int):
    neighbor = csp.neighbors[var]
    temp = []
    for v in neighbor:
        if v not in assignment:
            if (len(csp.domains[v]) == 1) and (csp.domains[v][0] == val):
                csp.forward_fails += 1
                return False, None
            temp.append(v)

    for v in temp:
        if val in csp.domains[v]:
            csp.domains[v].remove(val)

    return True, temp
"""


def ForwardChecking(csp: SudokuCSP, assignment, var: tuple, val: int):
    neighbor = csp.neighbors[var]
    temp = []
    for v in neighbor:
        if v not in assignment and val in csp.domains[v]:
            csp.domains[v].remove(val)
            if len(csp.domains[v]) == 0:
                csp.forward_fails += 1
                return False, None


    return True, temp




def Connected(var1: tuple, var2: tuple):
    r1, c1 = var1
    r2, c2 = var2
    return (r1 == r2) or (c1 == c2) or (find_box(r1, c1) == find_box(r2, c2))


def verifying(constraints):
    for c in constraints:
        s = 0
        for set in c:
            s = sum(set)
        if s != 45: return False

    return True


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    level = input("Enter level:")
    mode = input("Enter Algorithm:")
    sudoku = None

    if level == "easy":
        sudoku = deepcopy(easy)

    elif level == "medium":
        sudoku = deepcopy(medium)

    elif level == "hard":
        sudoku = deepcopy(hard)

    elif level == "evil":
        sudoku = deepcopy(evil)
    elif level == "zeros":
        sudoku = deepcopy(zeros)

    csp = SudokuCSP(sudoku)
    # print(len(csp.variables))
    assignment = {}

    start_time = time.time()
    if mode == "B":
        BackTrack(assignment, csp)
    elif mode == "BFC":
        BackTrackFC(assignment, csp)
    elif mode == "BFCH":
        BackTrackFCH(assignment, csp)
    end_time = time.time()
    elapsed_time = end_time - start_time

    for a in assignment:
        sudoku[a[0]][a[1]] = assignment[a]

    print(sudoku)

    print("Time: ", elapsed_time)

    print("Expaneded nodes:", csp.expanded_nodes)

    print("Fails from forward", csp.forward_fails)

    with open("BFC.txt", "a") as file:
        file.write("Time: " + str(elapsed_time) + "\n")
        file.write("Nodes: " + str(csp.expanded_nodes) + "\n")
        file.write("\n")

    if verifying(csp.constraints): print("Success!")
