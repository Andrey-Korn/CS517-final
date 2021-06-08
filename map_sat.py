# CS 517 final project
# minimum obstacle removal on a 2d grid
# Authors: Andrey Kornilovich & Chunxue Xu

# import pysmt shortcuts
from pysmt.shortcuts import Symbol, And, Not, Or, Iff, TRUE, FALSE
from pysmt.shortcuts import get_model, serialize, simplify, get_atoms

# import standard python libraries
import os
import logging as log
import numpy as np
import argparse
import csv

from utils import data_generation

debug_file = 'info.log'

class map_sat():

    def __init__(self):
        self.map = []
        self.n = 0
        self.k = 0
        self.path = []
        self.obst = []
        self.num_obst = 0

        # delete old log file
        if os.path.isfile(debug_file):
            os.remove(debug_file)

        # setup log file
        log.basicConfig(format='%(message)s', filename=debug_file, level=log.INFO)


    def read_obst_csv(self, filename="test1.csv"):
        '''
        Read in obstacle csv. First line is graph size n, second
        line is #_obstacles, and the following are obstacle coordinates
        '''

        with open(filename) as file:
            csv_reader = csv.reader(file, delimiter=",")

            # save obstacles to class for use later
            line_count = 0
            self.obst = {}

            # iterate through csv
            for row in csv_reader:

                # first line in csv is graph size
                if line_count == 0:
                    self.n = int(row[0])
                    self.k = (2 * self.n) - 1

                # second line in csv is # obstacles
                elif line_count == 1:
                    self.num_obst = int(row[0])

                # add obstacles as a 5-tuple to a dictionary:
                # (x1, x2, y1, y2 of the rectangle, weight) 
                else:
                    self.obst[Symbol(f"o{line_count - 2}")] = ((int(row[0])
                                                              , int(row[1])
                                                              , int(row[2])
                                                              , int(row[3])
                                                              , int(row[4]) ))

                line_count += 1

            log.info("Obstacle data read successfully")
            log.info(f"size of map: {self.n} x {self.n}")
            log.info(f"length of paths: {self.k}")
            log.info(f"number of obstacles: {self.num_obst}")
            log.info(f"obstacle_dictionary: {self.obst}\n")


    def print_map(self):
        '''
        print contents of the map to the terminal
        '0' == uncovered   
        '1' == covered by an obstacle
        '-' == critical chosen path. Uncovered
        '!' == critical chosen path. Covered by an obstacle
        '''
        print("\n")
        graph = np.empty((self.n, self.n), dtype='str')

        for x in range(self.n):
            for y in range(self.n):
                pt = (x, y)
                if self.in_path(pt):
                    # print("in path")
                    if self.is_obstructed(pt):
                        graph[y][x] = '!'
                    else:
                        graph[y][x] = '-'
                else:
                    if self.is_obstructed(pt):
                        graph[y][x] = '1'
                    else:
                        graph[y][x] = '0'

        # print(self.is_obstructed(0,4))
        # print map, reverse the rows for clarity
        for y in range(self.n - 1, -1, -1):
            print(graph[y])


    def build_path(self, path_type):
        '''
        construct a list of (x,y) coordinates representing
        1 of 3 paths. All paths will be of length (2*n)-1
        '''
        path = []

        # diagonal path
        if path_type == 0:
            log.info("diagonal path:")
            x, y = 0, 0
            for k in range(self.k//2):
                path.append((x, y))
                x += 1
                path.append((x, y))
                y += 1

            path.append((x,y))

        # up -> right path
        elif path_type == 1:
            log.info("up -> right path:")
            for y in range(self.n - 1):
                path.append((0, y))

            for x in range(self.n):
                path.append((x, self.n - 1))

        # right -> up path
        else:
            log.info("right -> up path:")
            for x in range(self.n - 1):
               path.append((x, 0))

            for y in range(self.n):
                path.append((self.n - 1, y))

        log.info(f"{path}\n")
        assert len(path) ==  self.k, "path length incorrect"
        return path


    # delete if old graph function is removed
    def in_path(self, pt):
        for i in range(len(self.path)):
            if self.path[i] == pt:
                return True
        return False


    def covered_by_obst(self, pt, obst_num):
        '''check if (x,y) covered by a specific obstacle'''
        # grab obstacle from dictionary
        obst = self.obst[self.obst_symbol(obst_num)]
        x, y = pt[0], pt[1]
        # check if point is within rectangular obstacle area
        if obst[0] <= x <= obst[1] and obst[2] <= y <= obst[3]:
            return True
        return False


    def pt_obst_coverage(self, pt):
        '''return list of obstacle numbers that cover a point'''
        pt_obst_list = []
        for i in range(self.num_obst):
            if self.covered_by_obst(pt, i):
                pt_obst_list.append(i)
        return pt_obst_list


    # delete alongside old graph function
    def is_obstructed(self, pt):
        for i in range(self.num_obst):
            if self.covered_by_obst(pt, i):
                return True
        return False


    def construct_pt_clause(self, pt):
        '''
        Return Boolean formula for a point clause for SAT checking.
        For every obstacle covering the point, OR together those
        obstacles. If the point is not covered, just return True.
        '''
        # find what obstacles cover a given point (list of obstacle indices)
        pt_obst_list = self.pt_obst_coverage(pt)

        # OR of SMT symbols built with the obstacle indices
        if pt_obst_list:
            return Or([self.obst_symbol(i) for i in pt_obst_list])

        # if uncovered, return true
        return TRUE()


    def get_path_formula(self, path):
        '''
        Construct boolean formula. Create k (len of path) clauses.
        Use And to connect all point clauses together.
        '''
        return And(self.construct_pt_clause(path[k]) for k in range(0, self.k))


    def obst_symbol(self, obst_num):
        '''
        return SMT bool symbol for an obstacle, used both for constructing
        formulas, and for generating obstacle dictionary keys
        '''
        return Symbol(f"o{obst_num}")


    def build_result_formula(self, literals):
        '''
        Construct Boolean formula based on previous SAT results. Used to 
        prevent the same solution being possible on subsequent SAT checks.
        Use Iff() to force equality between the obstacle symbol and previous
        T/F value.
        '''
        # for value in literals:
            # print(value[0], value[1])

        # loop through all boolean values
        return And([Iff(val[0], val[1]) for val in literals])


    def solve(self, path):
        '''
        Solve boolean formula of path/obstacle SAT representation.
        Whenever a solution is found, negate the result, And() 
        it to the existing formula, and continue finding more solutions.
        '''
        solutions = []
        formula = self.get_path_formula(path)

        # log formula information
        log.info("Boolean formula of path:")
        log.info(f"full      : {formula.serialize()}")
        log.info(f"simplified: {simplify(formula)}")
        log.info(f"obstacles : {get_atoms(formula)}\n")

        while(True):

            # Get satisfiability results
            res = get_model(formula)

            if res:
                solutions.append(res)

                log.info("SAT solution:")
                log.info(f"{res}\n")

                # get negation of result. Add to formula and rerun to 
                # find all solutions
                negated_solution = Not(self.build_result_formula(res))
                formula = And(negated_solution, formula)

            # All solutions found, break
            else:
                log.info("UNSAT, no more solutions.")
                break

        return solutions


    def best_cost(self, solutions):
        '''
        Given a set of solutions to the obstacle map for a given path, 
        return the solution with the minimum overall cost
        '''
        min_cost = float('inf')
        min_solution = None

        # iterate through all solutions
        sol_num = 1
        for sol in solutions:
            current_cost = 0
            for lit in sol:
                current_cost += self.obst[lit[0]][4] * (int(lit[1] == TRUE()))

            log.info(f"cost of solution {sol_num}: {current_cost}")

            if current_cost <= min_cost:
                min_cost = current_cost
                min_solution = sol

            sol_num +=1
        
        log.info(f"minimum cost found: {min_cost}")
        return min_cost, min_solution


    def solve_all_paths(self, obst_file):
        ''' 
        with an obstacle map file, construct and solve boolean 
        formula representations for 3 different path types. 
        '''
        # parse obstacle file
        self.read_obst_csv(obst_file)

        # build paths through the graph
        diagonal_path = self.build_path(0)
        up_right_path = self.build_path(1)
        right_up_path = self.build_path(2)

        # find boolean formula solutions 
        
        log.info(f"\n\nFind all SAT solutions for diagonal path")
        log.info("----------------------------------------")
        diagonal_results = self.solve(diagonal_path) 
        log.info(f"\n\nFind all SAT solutions for up-right path")
        log.info("----------------------------------------")
        up_right_results = self.solve(up_right_path)
        log.info(f"\n\nFind all SAT solutions for right-up path")
        log.info("----------------------------------------")
        right_up_results = self.solve(right_up_path) 

        # find best solution for each path type
        log.info("\n\nCalculate diagonal path solution costs")
        log.info("--------------------------------------")
        diagonal_cost, diagonal_sol = self.best_cost(diagonal_results)
        log.info("\nCalculate up-right path solution costs")
        log.info("--------------------------------------")
        up_right_cost, up_right_sol = self.best_cost(up_right_results)
        log.info("\nCalculate right-up path solution costs")
        log.info("--------------------------------------")
        right_up_cost, right_up_sol = self.best_cost(right_up_results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='check 2d robot map satisfiability.')
    # parser.add_argument('int 2D grid size')
    
    '''
    parser.add_argument('--size', type=int, default=5)
    parser.add_argument('--blocks', type=int, default=4)
    args = parser.parse_args()

    # generate data (16 blocks at most)
    data_directory = data_generation(args.size, args.blocks)
    '''
    
    m = map_sat()

    # pass in obstacle csv to the solver
    m.solve_all_paths("test1.csv")
