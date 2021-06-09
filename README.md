# Minimum Obstacle Removal in a 2D graph: CS517 Final Project
## Installation
An environment with python3 is required. Guide is intended for Linux or macOS users.
### Virtual Environment
It is recommended that you set up the project within a python virtual environment, to avoid installing unnecessary packages onto your system, but it is optional. Run the following inside the project directory to create the virtual environment:

- Install python3-venv:

`apt-get install python3-venv`

- Initialize:

`python3 -m venv env`

- start virtual environment:

`source env/bin/activate`

- Now you should be in the virtual environment. Anything you install with pip in this environment will be contained inside the env folder and not affect the rest of your system.

### Install packages
Either with or without a virtual environment, run the following to install all necessary packages:

`pip install -r requirements.txt`

### Install SMT Solver
- Install MathSAT (other solvers would likely work as well):

`pysmt-install --msat`

- Update PYTHONPATH (was found to be needed when using a virtual environment, so pySMT can find the solver):

`pysmt-install --env`

- Run the output of the above command. Example for my machine below:

`export PYTHONPATH="/home/andrey/.local/lib/python3.6/site-packages:${PYTHONPATH}"`

- After exporting the path, everything should be ready to use.

### Leave virtual environment
`deactivate`

## Generating and graphing data
`util.py` is used for generating and graphing .csv formatted data. The data generation utility needs 2 integer arguments, the graph size, and obstacle count. It will also automatically place new data in the `mapData/` directory. The graphing utility requires a filepath of the .csv you would like to graph. The outputs will always be placed in `mapData/` if it is an input case, and in `resultData/` if it's a result case.

- Data generation example of graph size 8 with 6 obstacles 

`python3 utils.py --generate 8 6`

- Graph generation example for an input case

`python3 utils.py --graph mapData/8x8_6blocks.csv`

- Graph generation example for a result case

`python3 utils.py --graph resultData/8x8_6blocks_diagonal.csv`

- Help
 
`python3 utils.py --help`

## SAT solving
`map_sat.py` takes in a obstacle map file path as an argument, and solves all SAT instances of that map for 3 different s-t path types. It will print out the minimum traversal cost of all 3 s-t paths. All 3 solutions are outputted as their own csv file to the `resultData/` directory. 

- Usage:

`python3 map_sat.py mapData/8x8_6blocks.csv`

- Solve and automatically graph using the above graphing utility:

`python3 map_sat.py mapData/8x8_6blocks.csv --graph`

- Help

`python3 map_sat.py --help`

---
After running `map_sat.py`, the following are logged to `info.log`:

- Confirmation of .csv obstacle read, graph size, obstacle printout
- (x,y) coordinates of the 3 s-t path types (diagonal, up-right, right-up)
- Full and simplified Boolean formula representations of each path
- All SAT solutions to the Boolean formula
- Cost calculation of all solutions
- Best solutions and costs for all 3 s-t paths

The script erases this filename at the beginning each run, so rename logfiles you would like to keep. 
