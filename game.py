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
        return f"X[{self.i}][{self.j}]"


class ConstraintSum:
    def __init__(self, variables, equal) -> None:
        self.variables = variables
        self.equal = equal
    
    def validate(self, assignment):
        return sum(map(lambda var: assignment[(var.i, var.j) if type(var) != tuple else var], self.variables)) == self.equal
    
    def get_sum(self, assignment):
        return sum(map(lambda var: assignment[(var.i, var.j)] if (var.i, var.j) in assignment else 0, self.variables))
    
    def __str__(self) -> str:
        summed = " + ".join(list(map(lambda var: f"X[{var.i}][{var.j}]", self.variables)))
        return f"{summed} = {self.equal}"

class ConstraintInEquality:
    def __init__(self, variables) -> None:
        self.variables = variables
    
    def validate(self, assignment):
        for i in range(0, len(self.variables)):
            for j in range(i + 1, len(self.variables)):
                if self.variables[i].val and self.variables[j].val and assignment[(self.variables[i].i, self.variables[i].j)] == assignment[(self.variables[j].i, self.variables[j].j)]:
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
        self.variable_to_constraint = {}
        self.create_variables()
        self.create_constraints()
        self.get_neighbors()
        self.get_variable_to_constraints_mapping()
    
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
                        # self.constrains.append(
                        #     ConstraintInEquality(variables=deepcopy(vars))
                        # )
                    vars.clear()
                    left_clue, _ = self.board.get_clue_value(i, j)
                    left_clue = int(left_clue)

                elif self.board.get_type(i, j) == WHITE:
                    vars.append(self.variables[(i, j)])

            if vars:
                self.constrains.append(
                    ConstraintSum(variables=deepcopy(vars), equal=left_clue)
                )
                # self.constrains.append(
                #     ConstraintInEquality(variables=deepcopy(vars))
                # )
            vars.clear()
        
        for j in range(self.board.height):
            vars = []
            for i in range(self.board.width):
                if self.board.get_type(i, j) == CLUE:
                    if vars:
                        self.constrains.append(
                            ConstraintSum(variables=deepcopy(vars), equal=up_clue)
                        )
                        # self.constrains.append(
                        #     ConstraintInEquality(variables=deepcopy(vars))
                        # )
                    vars.clear()
                    _, up_clue = self.board.get_clue_value(i, j)
                    up_clue = int(up_clue)

                elif self.board.get_type(i, j) == WHITE:
                    vars.append(self.variables[(i, j)])

            if vars:
                self.constrains.append(
                    ConstraintSum(variables=deepcopy(vars), equal=up_clue)
                )
                # self.constrains.append(
                #     ConstraintInEquality(variables=deepcopy(vars))
                # )
            vars.clear()
    
    def _get_neighbors(self, i, j):
        neighbors = []
        for __i in range(i - 1, -1, -1):
            if self.board.get_type(__i, j) == WHITE:
                neighbors.append((__i, j))
            else:
                break
        
        for __i in range(i + 1, self.board.width):
            if self.board.get_type(__i, j) == WHITE:
                neighbors.append((__i, j))
            else:
                break
        
        for __j in range(j - 1, -1, -1):
            if self.board.get_type(i, __j) == WHITE:
                neighbors.append((i, __j))
            else:
                break
        
        for __j in range(j + 1, self.board.height):
            if self.board.get_type(i, __j) == WHITE:
                neighbors.append((i, __j))
            else:
                break
        
        return neighbors
    
    def get_neighbors(self):
        for i in range(self.board.width):
            for j in range(self.board.height):
                neighbors = self._get_neighbors(i, j)
                self.neighbors[(i, j)] = neighbors
    
    def get_variable_to_constraints_mapping(self):
        for _, variable in self.variables.items():
            self.variable_to_constraint[(variable.i, variable.j)] = []
            for constraint in self.constrains:
                if (variable.i, variable.j) in list(map(lambda var: (var.i, var.j), constraint.variables)):
                    self.variable_to_constraint[(variable.i, variable.j)].append(constraint)
    

    def get_domain_of_variable(self, assignment, variable):
        legal_domain = set(self.domain)
        for neighbor in self.neighbors[(variable.i, variable.j)]:
            if (neighbor[0], neighbor[1]) in assignment and assignment[(neighbor[0], neighbor[1])] in legal_domain:
                legal_domain.remove(assignment[(neighbor[0], neighbor[1])])
        return legal_domain

    def get_unassigned_variable(self, assignment):
        unassigned_vars = [var for key, var in self.variables.items() if (var.i, var.j) not in assignment]
        if not unassigned_vars:
            return None
        return unassigned_vars[0]
    
    def get_unassigned_variable_mrv(self, assignment, domain):
        unassigned_vars = [(var, len(domain[key])) for key, var in self.variables.items() if (var.i, var.j) not in assignment]
        if not unassigned_vars:
            return None
        
        return min(unassigned_vars, key=lambda var: var[1])[0]
    
    def order_lcv_values(self, assignment, variable, domain):
        values = []
        for value in domain[variable.i, variable.j]:
            removed = self.assign_var(assignment, variable, value, domain)
            domain_sum = sum(map(lambda var: len(domain[var]), self.neighbors[(variable.i, variable.j)]))
            values.append((domain_sum, value))
            self.del_var(assignment, variable, value, domain, removed)
        
        values.sort(reverse=True)
        domain_of_var = [v[1] for v in values]
        domain[(variable.i, variable.j)] = set(domain_of_var)
        return list(domain_of_var)

    
    def get_unassigned_variables(self, assignment):
        unassigned_vars = [var for _, var in self.variables.items() if (var.i, var.j) not in assignment]
        if not unassigned_vars:
            return None
        return unassigned_vars
    
    def check_forward(self, domain):
        for _, d in domain.items():
            if len(d) == 0:
                return False
        return True
    
    def check_consistency(self, assignment, domain):
        unassigned_variables = self.get_unassigned_variables(assignment)
        for var in unassigned_variables:
            domain_len = len(domain[(var.i, var.j)])
            removed_count = 0
            for val in deepcopy(domain[(var.i, var.j)]):
                print(assignment, str(var), val, domain[var.i, var.j], domain, ':(')
                removed = self.assign_var(assignment, var, val, domain)
                print(assignment, str(var), val, domain[var.i, var.j], domain, ':)')
                if not self.check_forward(domain):
                    self.del_var(assignment, var, val, domain, removed)
                    domain[(var.i, var.j)].remove(val)
                    removed_count += 1
                    continue
                self.del_var(assignment, var, val, domain, removed)
            if removed_count == domain_len:
                return False
        return True
    
    def solve(self, report=True, mrv=False, lcv=False, forward_checking=False):
        assignment = {}
        
        domains = {(v[0], v[1]): set(range(1, 10)) for v in self.variables}
        start = time()
        self.solution = self.backtrack(assignment, domains, mrv=False, lcv=lcv, forward_checking=forward_checking)
        end = time()

        if report:
            print(f'TIME-SPAN: {end - start:.4}s')

        return self.solution
    
    
    def remove_bigger_than_clue_values(self, assignment, variable, domain, leaf=False):
        removed = []
        for val in deepcopy(domain[variable]):
            cnt = 0
            for constraint in self.variable_to_constraint[variable]:
                if not leaf:
                    if val + constraint.get_sum(assignment) > constraint.equal:
                        if val in domain[variable]:
                            domain[variable].remove(val)
                            removed.append(val)
                else:
                    if val + constraint.get_sum(assignment) != constraint.equal:
                        cnt += 1
                    if cnt == len(self.variable_to_constraint[variable]):
                        if val in domain[variable]:
                            domain[variable].remove(val)
                            removed.append(val)
        return removed
    
    def check_if_it_is_the_last_one(self, assignment, variable):
        neighbors = self.neighbors[variable]
        bad = 2
        for i in range(self.board.width):
            if i == variable[0]:
                continue
            if (i, variable[1]) not in neighbors:
                continue
            if (i, variable[1]) not in assignment and (i, variable[1]) != variable:
                bad -= 1
                break
        
        for j in range(self.board.height):
            if j == variable[1]:
                continue
            if (variable[0], j) not in neighbors:
                continue
            if (variable[0], j) not in assignment and (variable[0], j) != variable:
                bad -= 1
                break

        return bad != 0

    def assign_var(self, assignment, variable, value, domain):
        assignment[(variable.i, variable.j)] = value
        removed_values_from_domain = {}

        for neighbor in self.neighbors[(variable.i, variable.j)]:
            if neighbor in assignment:
                continue
            if value in domain[neighbor]:
                # print(assignment, str(variable), value)
                domain[neighbor].remove(value)
            # print(assignment, variable, neighbor, domain[neighbor], self.check_if_it_is_the_last_one(assignment, neighbor), ':(')
            if self.check_if_it_is_the_last_one(assignment, neighbor):
                removed = self.remove_bigger_than_clue_values(assignment, neighbor, domain, leaf=True)
                # print(assignment, variable, neighbor, domain[neighbor], self.check_if_it_is_the_last_one(assignment, neighbor), ':)')
            else:
                removed = self.remove_bigger_than_clue_values(assignment, neighbor, domain)
            removed_values_from_domain[neighbor] = removed
        return removed_values_from_domain

    
    def del_var(self, assignment, variable, value, domain, removed_vals):
        del assignment[(variable.i, variable.j)]
        for neighbor in self.neighbors[(variable.i, variable.j)]:
            domain[neighbor].add(value)
            if neighbor in removed_vals:
                for removed_val in removed_vals[neighbor]:
                    domain[neighbor].add(removed_val)
    
    def validate_assignment(self, assignment):
        for constraint in self.constrains:
            if not constraint.validate(assignment):
                return False
        return True
    
    # THE CODE WILL BE FORWARD CHECKED!
    def backtrack(self, assignment, domain, mrv=False, lcv=False, forward_checking=False, arc_consistency=False):
        if len(assignment) == len(self.variables):
            return assignment
        
        # consistent = self.check_consistency(assignment, domain)
        # if not consistent:
        #     del assignment[list(assignment.items())[-1][0]]
        #     return self.backtrack(assignment, domain, mrv=mrv, lcv=lcv, forward_checking=forward_checking, arc_consistency=arc_consistency)
        
        var = self.get_unassigned_variable_mrv(assignment, domain) if mrv else self.get_unassigned_variable(assignment)
        if not var:
            return None
        
        var_domain = None
        if lcv:
            var_domain = self.order_lcv_values(assignment, var, domain)

        for value in deepcopy(domain[(var.i, var.j)]) if not lcv else var_domain:
            removed_vals = self.assign_var(assignment=assignment, variable=var, value=value, domain=domain)
            if forward_checking and not self.check_forward(domain):
                self.del_var(assignment=assignment, variable=var, value=value, domain=domain, removed_vals=removed_vals)
                continue
            result = self.backtrack(assignment, domain=domain, mrv=mrv, lcv=lcv, 
                                    forward_checking=forward_checking, 
                                    arc_consistency=arc_consistency)
            if result is not None:
                return result
            self.del_var(assignment=assignment, variable=var, value=value, domain=domain, removed_vals=removed_vals)

        return None