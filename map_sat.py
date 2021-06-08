# CS 517 final project
# minimum obstacle removal on a 2d grid
# Authors: Andrey Kornilovich & Chunxue Xu

from pysmt.shortcuts import Symbol, And, Not, Or, Equals, NotEquals, Bool, Iff, TRUE, FALSE
from pysmt.shortcuts import Solver, is_sat, get_model, serialize, simplify, get_atoms
import numpy as np
from pysmt import typing

import math
import argparse
import csv
from utils import data_generation

DEBUG = True
CSV_DEBUG = True

class map_sat():

    def __init__(self):
        self.map = []
        self.n = 0
        self.k = 0
        self.path = []
        self.obst = []
        self.num_obst = 0


    def read_obst_csv(self, filename="test1.csv"):

        with open(filename) as file:
            csv_reader = csv.reader(file, delimiter=",")
            line_count = 0
            # self.obst = []
            self.obst = {}
            for row in csv_reader:

                # first line in csv is graph size
                if line_count == 0:
                    self.n = int(row[0])
                    self.k = (2 * self.n) - 1

                # second line in csv is # obstacles
                elif line_count == 1:
                    self.num_obst = int(row[0])

                # add obstacles as a 5-tuple representing:
                # x1, x2, y1, y2 of the rectangle, and weight 
                else:
                    # dictionary append
                    self.obst[Symbol(f"o{line_count - 2}")] = ((int(row[0])
                                                              , int(row[1])
                                                              , int(row[2])
                                                              , int(row[3])
                                                              , int(row[4]) ))

                    # list append
                    # self.obst.append((int(row[0])
                    #                 , int(row[1])
                    #                 , int(row[2])
                    #                 , int(row[3]) 
                    #                 , int(row[4]) ))

                line_count += 1

            if(CSV_DEBUG):
                print(f"size of map: {self.n} x {self.n}")
                print(f"number of obstacles: {self.num_obst}")
                print(f"obstacle_dictionary: {self.obst}\n")


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
        path = []
        # x, y = 0, 0

        # diagonal path
        if path_type == 0:
            print("diagonal path")
            x, y = 0, 0
            for k in range(self.k//2):
                path.append((x, y))
                x += 1
                path.append((x, y))
                y += 1

            path.append((x,y))

        # up -> right path
        elif path_type == 1:
            print("up -> right path")
            for y in range(self.n - 1):
                path.append((0, y))

            for x in range(self.n):
                path.append((x, self.n - 1))

        # right -> up path
        else:
            print("right -> up path")
            for x in range(self.n - 1):
               path.append((x, 0))

            for y in range(self.n):
                path.append((self.n - 1, y))

        # print(len(path))
        print(path)
        assert len(path) ==  self.k, "path length incorrect"
        return path


    def in_path(self, pt):
        for i in range(len(self.path)):
            if self.path[i] == pt:
                return True
        return False


    def covered_by_obst(self, pt, obst_num):
        obst = self.obst[self.obst_symbol(obst_num)]
        x, y = pt[0], pt[1]
        if obst[0] <= x <= obst[1] and obst[2] <= y <= obst[3]:
            return True
        return False


    def pt_obst_coverage(self, pt):
        pt_obst_list = []
        for i in range(self.num_obst):
            # if self.covered_by_obst(pt, self.obst[i]):
            if self.covered_by_obst(pt, i):
                pt_obst_list.append(i)
        return pt_obst_list


    def is_obstructed(self, pt):
        for i in range(self.num_obst):
            if self.covered_by_obst(pt, i):
                return True
        return False


    def construct_pt_clause(self, pt):
        pt_obst_list = self.pt_obst_coverage(pt)

        if pt_obst_list:
            formula = Or([self.obst_symbol(i) for i in pt_obst_list])
            return formula
        else:
            return TRUE()


    def get_path_formula(self, path):
        # self.print_map()

        # loop through points in the path, and construct obstacle literals
        formula = And(self.construct_pt_clause(path[k]) for k in range(0, self.k))

        return formula


    def obst_symbol(self, obst_num):
        return Symbol(f"o{obst_num}")


    def build_result_formula(self, literals):
        for value in literals:
            # print(type(value[0]))
            print(value[0], value[1])
        # print(literals[Symbol("o0")])
        return And([Iff(val[0], val[1]) for val in literals])


    def solve(self, path):
        sol_exists = True
        solutions = []
        formula = self.get_path_formula(path)

        while(sol_exists):

            print("\nformula of chosen path:")
            # print(f"full      : {formula}")
            print(f"full      : {formula.serialize()}")
            # print(f"simplified: {simplify(formula)}")
            # print(f"obstacles : {get_atoms(formula)}\n")

            res = get_model(formula)

            if res:
                print("SAT")
                # print(res)
                solutions.append(res)
                negated_solution = Not(self.build_result_formula(res))
                # print(negated_solution)
                formula = And(negated_solution, formula)

            else:
                print("UNSAT")
                sol_exists = False

        return solutions


    def best_cost(self, solutions):
        min_cost = float('inf')
        min_solution = None
        for sol in solutions:
            print("solution")
            current_cost = 0
            for lit in sol:
                print(lit[0], lit[1])
                current_cost += self.obst[lit[0]][4] * (int(lit[1] == TRUE()))

            print(current_cost)

            if current_cost <= min_cost:
                min_cost = current_cost
                min_solution = sol
        
        print(min_cost)
        return min_cost, min_solution


    def solve_all_paths(self, obst_file):
        self.read_obst_csv(obst_file)
        diagonal_path = self.build_path(0)
        up_right_path = self.build_path(1)
        right_up_path = self.build_path(2)

        diagonal_results = self.solve(diagonal_path) 
        # up_right_results = self.solve(up_right_path)
        # right_up_results = self.solve(right_up_path) 

        # self.best_cost(diagonal_results)
        diagonal_cost, diagonal_sol = self.best_cost(diagonal_results)
        # up_right_cost, up_right_sol = self.best_cost()
        # right_up_cost, right_up_sol = self.best_cost()


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

    # m.solve("test1.csv", 2)

    # pass in obstacle csv to the solver
    m.solve_all_paths("test1.csv")
