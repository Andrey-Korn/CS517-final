# CS 517 final project
# minimum obstacle removal on a 2d grid
# Authors: Andrey Kornilovich & Chunxue Xu

from pysmt.shortcuts import Symbol, And, Not, Equals, NotEquals, Int, get_model
from pysmt.shortcuts import Solver, is_sat
import numpy as np
from pysmt import typing

import math
import argparse

class map_sat():

    def __init__(self, n, obst, path_type):
        self.map = []
        self.n = size
        self.k = (2 * size) - 1
        self.path = []
        self.obst = obst
        self.num_obst = len(obstacles)
        self.path_type = path_type

        # self.solver = get_prepared_solver()

    def reset(self, size, obstacles):
        pass


    def path_coordinates(self, path_type):
        path = []
        # x, y = 0, 0

        # diagonal path
        if self.path_type == 0:
            print("diagonal path")
            x, y = 0, 0
            for k in range(self.k//2):
                path.append((x, y))
                x += 1
                path.append((x, y))
                y += 1

            path.append((x,y))

        # up -> right path
        elif self.path_type == 1:
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


        print(len(path))
        print(path)
        assert len(path) ==  self.k, "path length incorrect"

        self.path = path

    def get_prepared_solver(self, path_type):
        """
        Return a solver for the obstacle map. Pick one of 3
        s-t path types: diagonal, right->up, and up->right.
        s is always at (0,0), and t will always be at (n-1, n-1)
        """

        path = self.path_coordinates(path_type)
        # solver = Solver()

        # return solver


    def solve(self):
        self.get_prepared_solver(self.path_type)

        # with Solver() as solver:
            # solver.add_assertion(self.formula)
            # if solver.solve():
                # print("yay")
            # else:
                # print("No solution found")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='check 2d robot map satisfiability.')
    # parser.add_argument('int 2D grid size')
    obstacles = []
    size = 5

    m = map_sat(size, obstacles, 0)
    m.solve()