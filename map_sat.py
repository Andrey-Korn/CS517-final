# CS 517 final project
# minimum obstacle removal on a 2d grid
# Authors: Andrey Kornilovich & Chunxue Xu

from pysmt.shortcuts import Symbol, And, Not, Or, Equals, NotEquals, Bool, TRUE, FALSE
from pysmt.shortcuts import Solver, is_sat, get_model, serialize, simplify
import numpy as np
from pysmt import typing

import math
import argparse
import csv

class map_sat():


    def __init__(self):
        self.map = []
        self.n = 0
        self.k = 0
        self.path = []
        self.obst = []
        self.num_obst = 0

    def read_obst_csv(self, filename):
        with open(filename) as file:
            csv_reader = csv.reader(file, delimiter=",")
            line_count = 0
            self.obst = []
            for row in csv_reader:
                # first line in csv is graph size
                if line_count == 0:
                    self.n = int(row[0])
                    self.k = (2 * self.n) - 1

                # second line in csv is # obstacles
                elif line_count == 1:
                    self.num_obst = int(row[0])

                # add obstacles as a quintuple representing:
                # x1, x2, y1, y2 of the rectangle, and weight 
                else:
                    # uncomment this line for formatting including weight
                    # self.obst.append((int(row[0])
                    #                 , int(row[1])
                    #                 , int(row[2])
                    #                 , int(row[3]) 
                    #                 , int(row[5]) ))


                    # uncomment this line for formatting excluding weight
                    self.obst.append((int(row[0])
                                    , int(row[1])
                                    , int(row[2])
                                    , int(row[3]) ))

                line_count += 1

            print(f"size of map: {self.n} x {self.n}")
            print(f"number of obstacles: {self.num_obst}")
            print(f"obstacle_list: {self.obst}\n")

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

    def in_path(self, pt):
        for i in range(len(self.path)):
            if self.path[i] == pt:
                return True
        return False

    def covered_by_obst(self, pt, obst):
        x, y = pt[0], pt[1]
        if obst[0] <= x <= obst[1] and obst[2] <= y <= obst[3]:
            return True
        return False

    def pt_obst_coverage(self, pt):
        pt_obst_list = []
        for i in range(self.num_obst):
            if self.covered_by_obst(pt, self.obst[i]):
                pt_obst_list.append(i)
        return pt_obst_list


    def is_obstructed(self, pt):
        for i in range(self.num_obst):
            if self.covered_by_obst(pt, self.obst[i]):
                return True
        return False

    def path_coordinates(self, path_type):
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
        self.path = path


    def pt_formula(self, pt):
        pt_obst_list = self.pt_obst_coverage(pt)

        if pt_obst_list:
            formula = Or([Symbol(f"o{i}") for i in pt_obst_list])
            return formula
        else:
            return TRUE()



    def get_prepared_solver(self, path_type, obst_limit):
        """
        Return a solver for the obstacle map. Pick one of 3
        s-t path types: diagonal, right->up, and up->right.
        s is always at (0,0), and t will always be at (n-1, n-1)
        """

        self.path_coordinates(path_type)
        self.print_map()

        # decrement obst counter to set limit to boolean formula construction
        self.obst_limit = obst_limit

        # loop through points in the path, and construct obstacle literals
        formula = And(self.pt_formula(self.path[k]) for k in range(0, self.k))

        return formula


    def solve(self, obst_file, path_type):
        self.read_obst_csv(obst_file)
        formula = self.get_prepared_solver(path_type, 4)

        print(f"full       formula: {formula}")
        print(f"simplified formula: {simplify(formula)}")
        m = get_model(formula)

        if m is not None:
            print("SAT")
            print(m)
        else:
            print("UNSAT")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='check 2d robot map satisfiability.')
    # parser.add_argument('int 2D grid size')

    m = map_sat()

    # run solver with the obstacle file, and 1 of 3 path types
    m.solve("test1.csv", 2)