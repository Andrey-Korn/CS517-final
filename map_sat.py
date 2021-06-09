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

# import utils.py 
import utils

result_directory = 'resultData'
map_directory = 'mapData'
log_file = 'info.log'

class map_sat():

    def __init__(self):
        self.map = []
        self.n = 0
        self.k = 0
        self.path = []
        self.obst = {}
        self.num_obst = 0

        # delete old log file
        if os.path.isfile(log_file):
            os.remove(log_file)

        # setup log file
        log.basicConfig(format='%(message)s', filename=log_file, level=log.INFO)


    def read_obst_csv(self, filename="test1.csv"):
        '''
        Read in obstacle csv. Second line is graph size n, third
        line is #_obstacles, and the following are obstacle coordinates
        '''

        with open(filename, 'r') as file:
            csv_reader = csv.reader(file, delimiter=",")

            # save obstacles to class for use later
            line_count = 0
            self.obst = {}

            # iterate through csv
            for row in csv_reader:

                # first line denotes input type
                if line_count == 0:
                    assert row != "map", "This is a result file! Please input a correct map input."
                
                # first line in csv is graph size
                elif line_count == 1:
                    self.n = int(row[0])
                    self.k = (2 * self.n) - 1

                # second line in csv is # obstacles
                elif line_count == 2:
                    self.num_obst = int(row[0])

                # add obstacles as a 5-tuple to a dictionary:
                # (x1, x2, y1, y2 of the rectangle, weight) 
                else:
                    self.obst[Symbol(f"o{line_count - 3}")] = ((int(row[0])
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


    def write_result_csv(self, solution, file_path, path_name):
        '''Write final solutions as csv to resultData/ directory'''
        # create result directory
        if not os.path.exists(result_directory):
            os.makedirs(result_directory)

        # write solution csv to result folder
        file_path = f"{file_path}_{path_name}.csv"
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, mode='w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerow([path_name])
            writer.writerow([self.n])
            num_obstacles = 0
            for obstacle in solution:
                if obstacle[1] == TRUE():
                    num_obstacles += 1
            writer.writerow([num_obstacles])
            for obstacle in solution:
                if obstacle[1] == TRUE():
                    writer.writerow([self.obst[obstacle[0]][i] for i in range(0, 5)])


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
        return SMT bool symbol for an obstacle. Used both for constructing
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

                # get negation of result. Add to formula and rerun 
                # to find all solutions
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
                # add obstacle cost if it was chosen in solution
                current_cost += self.obst[lit[0]][4] * (int(lit[1] == TRUE()))

            log.info(f"cost of solution {sol_num}: {current_cost}")

            if current_cost <= min_cost:
                min_cost = current_cost
                min_solution = sol

            sol_num +=1
        
        log.info(f"minimum cost found: {min_cost}")
        return min_cost, min_solution


    def solve_all_paths(self, obst_file,  graph=False):
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


        # save best obstacle removal to csv result
        _, file_name = os.path.split(obst_file)
        file_name = file_name.split('.')[0]
        file_path = f"{result_directory}/{file_name}"
        self.write_result_csv(diagonal_sol, file_path, "diagonal")
        self.write_result_csv(up_right_sol, file_path, "up")
        self.write_result_csv(right_up_sol, file_path, "right")
        
        print(f"cost of best diagonal path: {diagonal_cost}")
        print(f"cost of best up-right path: {up_right_cost}")
        print(f"cost of best right-up path: {right_up_cost}")

        # logs
        log.info("\n\nFinal results")
        log.info("-----------------------------------------------------------")
        log.info(f"cost of best diagonal path: {diagonal_cost}")
        log.info(f"cost of best up-right path: {up_right_cost}")
        log.info(f"cost of best right-up path: {right_up_cost}\n")
        
        log.info(f"best diagonal solution:")
        log.info(f"{diagonal_sol}\n")
        log.info(f"best up-right solution:")
        log.info(f"{up_right_sol}\n")
        log.info(f"best right-up solution:")
        log.info(f"{right_up_sol}\n")

        print("see info.log for more full boolean solutions and other stats")

        # graph results if requested
        if(graph):
            utils.map_plotting(f"{file_path}_diagonal.csv")
            utils.map_plotting(f"{file_path}_up.csv")
            utils.map_plotting(f"{file_path}_right.csv")

        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='check 2d robot map satisfiability.')
    parser.add_argument("filename", nargs=1, help="filepath of obstacle map csv input")
    parser.add_argument("--graph", help="automatically plot the result graph",
                         action="store_true")
    args = parser.parse_args()
    
    m = map_sat()

    # pass in obstacle csv filename to the solver, and optional graphing flag
    if(args.graph):
        m.solve_all_paths(args.filename[0], args.graph)
    else:
        m.solve_all_paths(args.filename[0])
