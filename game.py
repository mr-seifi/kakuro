from copy import deepcopy
from time import time

CLUE = 0
WHITE = 1
BLACK = 2

DOWN = 'down'
RIGHT = 'right'


class Board:
    def __init__(self, width, height, configuration) -> None:
        self.width = width
        self.height = height
        self.configuration = configuration
        self.board = []
        self.create_board()

    def create_board(self):
        [self.board.append([str(WHITE) for _ in range(self.height)]) for _ in range(self.width)]
        for key, val in self.configuration.items():
            values = val.split(':')
            cell_type = eval(values[0])
            cell_val1 = None if len(values) < 2 else values[1]
            cell_val2 = None if len(values) < 2 else values[2]

            self.board[int(key[1])][int(key[3])] = f'{cell_type}'
            if cell_val1 or cell_val2:
                self.board[int(key[1])][int(key[3])] += f':{cell_val1}'
                self.board[int(key[1])][int(key[3])] += f':{cell_val2}'
    
    def print_board(self):
        print(self.board)
    
    def get_type(self, i, j):
        return int(self.board[i][j].split(':')[0])
    
    def get_clue_value(self, i, j):
        _clue = self.board[i][j].split(':')
        return _clue[1] or -1, _clue[2] or -1
    
    # OUTPUTS LEFT, UP CLUE IN ORDER
    def _find_adjacent_clue_value(self, i, j):
        left, up = -1, -1
        if self.board[i][j].split(':')[0] != WHITE:
            return left, up
        
        for __j in range(j, 0, -1):
            if self.board[i][__j].split(':')[0] == CLUE:
                left = int(self.board[i][__j].split(':')[1])
                break
        
        for __i in range(i, 0, -1):
            if self.board[__i][j].split(':')[0] == CLUE:
                up = int(self.board[__i][j].split(':')[2])
                break
        
        return left, up
        

    def check_solved(self):
        ...


class Variable:
    def __init__(self, i, j, val=None) -> None:
        self.i, self.j, self.val = i, j, val
    
    def cordinate(self):
        return (self.i, self.j)
    
    def __str__(self) -> str:
        return f"X[{self.i}][{self.j}] = {self.val}"


class ConstraintSum:
    def __init__(self, variables, equal) -> None:
        self.variables = variables
        self.equal = equal
    
    def validate(self, assignment):
        return sum(map(lambda var: assignment[(var.i, var.j)], self.variables)) == self.equal
    
    def __str__(self) -> str:
        summed = " + ".join(list(map(lambda var: f"X[{var.i}][{var.j}]", self.variables)))
        return f"{summed} = {self.equal}"

class ConstraintInEquality:
    def __init__(self, variables) -> None:
        self.variables = variables
    
    def validate(self, assignment):
        for i in range(0, len(self.variables)):
            for j in range(i + 1, len(self.variables)):
                if assignment[(self.variables[i].i, self.variables[i].j)] == assignment[(self.variables[j].i, self.variables[j].j)]:
                    return False
        return True
    
    def __str__(self) -> str:
        ineq = ""
        for i in range(0, len(self.variables)):
            for j in range(i + 1, len(self.variables)):
                ineq += f"X[{self.variables[i].i}][{self.variables[i].j}] != X[{self.variables[j].i}][{self.variables[j].j}]\t"
        return ineq
    

class CSPModel:
    def __init__(self, board: Board) -> None:
        self.board: Board = board
        self.variables = {}
        self.constrains = []
        self.domain = range(1, 10)
        self.neighbors = {}
        self.create_variables()
        self.create_constraints()
        self.get_neighbors()
    
    def create_variables(self):
        for i in range(self.board.width):
            for j in range(self.board.height):
                if self.board.get_type(i, j) == WHITE:
                    self.variables[(i, j)] = Variable(
                        i=i, j=j
                    )
    
    def create_constraints(self):
        left_clue = -1
        up_clue = -1
        for i in range(self.board.width):
            vars = []
            for j in range(self.board.height):
                if self.board.get_type(i, j) == CLUE:
                    if vars:
                        self.constrains.append(
                            ConstraintSum(variables=deepcopy(vars), equal=left_clue)
                        )
                        self.constrains.append(
                            ConstraintInEquality(variables=deepcopy(vars))
                        )
                    vars.clear()
                    left_clue, _ = self.board.get_clue_value(i, j)
                    left_clue = int(left_clue)

                elif self.board.get_type(i, j) == WHITE:
                    vars.append(self.variables[(i, j)])

            if vars:
                self.constrains.append(
                    ConstraintSum(variables=deepcopy(vars), equal=left_clue)
                )
                self.constrains.append(
                    ConstraintInEquality(variables=deepcopy(vars))
                )
            vars.clear()
        
        for j in range(self.board.height):
            vars = []
            for i in range(self.board.width):
                if self.board.get_type(i, j) == CLUE:
                    if vars:
                        self.constrains.append(
                            ConstraintSum(variables=deepcopy(vars), equal=up_clue)
                        )
                        self.constrains.append(
                            ConstraintInEquality(variables=deepcopy(vars))
                        )
                    vars.clear()
                    _, up_clue = self.board.get_clue_value(i, j)
                    up_clue = int(up_clue)

                elif self.board.get_type(i, j) == WHITE:
                    vars.append(self.variables[(i, j)])

            if vars:
                self.constrains.append(
                    ConstraintSum(variables=deepcopy(vars), equal=up_clue)
                )
                self.constrains.append(
                    ConstraintInEquality(variables=deepcopy(vars))
                )
            vars.clear()
    
    def _get_neighbors(self, i, j):
        up_i, bottom_i = 0, self.board.width
        left_j, right_j = 0, self.board.height
        
        neighbors = []
        for __i in range(i - 1, -1, -1):
            if self.board.get_type(__i, j) == WHITE:
                up_i = __i
                neighbors.append((__i, j))
            else:
                break
        
        for __i in range(i + 1, self.board.width):
            if self.board.get_type(__i, j) == WHITE:
                bottom_i = __i
                neighbors.append((__i, j))
            else:
                break
        
        for __j in range(j - 1, -1, -1):
            if self.board.get_type(i, __j) == WHITE:
                left_j = __j
                neighbors.append((i, __j))
            else:
                break
        
        for __j in range(j + 1, self.board.height):
            if self.board.get_type(i, __j) == WHITE:
                right_j = __j
                neighbors.append((i, __j))
            else:
                break
        
        return neighbors
    
    def get_neighbors(self):
        for i in range(self.board.width):
            for j in range(self.board.height):
                neighbors = self._get_neighbors(i, j)
                self.neighbors[(i, j)] = neighbors
    
    def get_domain_of_variable(self, assignment, variable):
        legal_domain = set(self.domain)
        for neighbor in self.neighbors[(variable.i, variable.j)]:
            if (neighbor[0], neighbor[1]) in assignment and assignment[(neighbor[0], neighbor[1])] in legal_domain:
                legal_domain.remove(assignment[(neighbor[0], neighbor[1])])
        return legal_domain

    def check_forward(self, assignment, variable, value, domain):
        # assignment[(variable.i, variable.j)] = value
        self._var_assign(assignment, variable, value, domain)
        for neighbor in self.neighbors[(variable.i, variable.j)]:
            if len(domain[neighbor[0], neighbor[1]]) == 0:
                return False
        # del assignment[(variable.i, variable.j)]
        self._rm_assign(assignment, variable, value, domain)
        return True

    def check_consistency(self, assignment, domain):
        vars = self.get_unassigned_variables(assignment)

        for var in vars:
            # domain = self.get_domain_of_variable(assignment, var)
            d = domain[(var.i, var.j)]
            for val in d:
                if not self.check_forward(assignment, var, val, domain):
                    d.remove(val)
                if not d:
                    return False
        return True

    def get_unassigned_variable(self, assignment):
        unassigned_vars = [var for key, var in self.variables.items() if (var.i, var.j) not in assignment]
        if not unassigned_vars:
            return None
        return unassigned_vars[0]
    
    def get_unassigned_variables(self, assignment):
        unassigned_vars = [var for key, var in self.variables.items() if (var.i, var.j) not in assignment]
        if not unassigned_vars:
            return None
        return unassigned_vars
    
    def get_unassigned_variable_mrv(self, assignment, domain):
        unassigned_vars = [var for key, var in self.variables.items() if (var.i, var.j) not in assignment]
        if not unassigned_vars:
            return None
        
        min_remaining_variable = len(domain[(unassigned_vars[0].i, unassigned_vars[0].j)])
        selected_var = unassigned_vars[0]
        for var in unassigned_vars:
            domain_len = len(domain[var.i, var.j])
            if domain_len < min_remaining_variable:
                min_remaining_variable = domain_len
                selected_var = var

        return selected_var
    
    def solve(self, report=True):
        assignment = {}
        self.cached_domains = {}
        start = time()
        # SIMPLE Backtrack
        # self.solution = self.backtrack(assignment)

        # MRV + Backtrack
        # self.solution = self.backtrack(assignment, mrv=True)
        
        # MRV + LCV + Backtrack
        # self.solution = self.backtrack(assignment, mrv=True, lcv=True)

        # MRV + ForwardChecking + Backtrack
        domains = {(v[0], v[1]): set(range(1, 10)) for v in self.variables}
        # self.solution = self.backtrack(assignment, domain=domains, mrv=True, forward_checking=True)

        # MRV + ArcConsistency + Backtrack
        self.solution = self.backtrack(assignment, domain=domains, mrv=True, arc_consistency=True)
        end = time()

        if report:
            print(f'TIME-SPAN: {end - start:.4}')

        return self.solution

    def _check_assignment(self, assignment):
        if len(assignment) == len(self.variables):
            all_ok = True
            for constraint in self.constrains:
                if not constraint.validate(assignment):
                    all_ok = False
                    break
            if all_ok:
                return assignment
        return None
    
    def _var_assign(self, assignment, var, val, domains):
        assignment[(var.i, var.j)] = val
        for neighbor in self.neighbors[(var.i, var.j)]:
            if val in domains[(neighbor[0], neighbor[1])]:
                domains[(neighbor[0], neighbor[1])].remove(val)
    
    def _rm_assign(self, assignment, var, val, domains):
        del assignment[(var.i, var.j)]
        for neighbor in self.neighbors[(var.i, var.j)]:
            domains[(neighbor[0], neighbor[1])].add(val)
        
        
    def _lcv_backtrack(self, assignment, mrv=False):
        res = self._check_assignment(assignment)
        if res:
            return res
        
        if not mrv:
            var = self.get_unassigned_variable(assignment)
        else:
            var = self.get_unassigned_variable_mrv(assignment)

        if not var:
            return None
        
        domain_length = 100000
        selected_val = list(self.domain)[0]
        for value in self.domain:
            assignment[(var.i, var.j)] = value
            _domain_length = 0
            for neighbor in self.neighbors[(var.i, var.j)]:
                _domain_length += len(self.get_domain_of_variable(assignment, Variable(i=neighbor[0], j=neighbor[1])))
            if _domain_length < domain_length:
                domain_length = _domain_length
                selected_val = value
            del assignment[(var.i, var.j)]

        assignment[(var.i, var.j)] = selected_val
        result = self._lcv_backtrack(assignment, mrv=mrv)
        if result is not None:
            return result
        del assignment[(var.i, var.j)]

        return None

    def backtrack(self, assignment, domain, mrv=False, lcv=False, forward_checking=False, arc_consistency=False):
        if lcv:
            return self._lcv_backtrack(assignment, mrv=mrv)
        
        res = self._check_assignment(assignment)
        if res:
            return res

        if not mrv:
            var = self.get_unassigned_variable(assignment)
        else:
            var = self.get_unassigned_variable_mrv(assignment, domain)

        if not var:
            return None

        if arc_consistency:
            ok = self.check_consistency(assignment, domain)
            if not ok:
                return None

        for value in domain[(var.i, var.j)]:
            if forward_checking:
                if not self.check_forward(assignment, var, value, domain):
                    continue
            self._var_assign(assignment, var, value, domain)
            result = self.backtrack(assignment, domain=domain, mrv=mrv, lcv=lcv, 
                                    forward_checking=forward_checking, 
                                    arc_consistency=arc_consistency)
            if result is not None:
                return result
            self._rm_assign(assignment, var, value, domain)

        return None