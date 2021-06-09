# Mininum Obstacle Removal in a 2D graph: CS517 Final Project
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
Now you should be in the virtual environment. Anything you install with pip in this environment will be contained inside the env folder.

### Install packages
Either with or without the virtual environment setup, run the following to install all packages:
`pip install -r requirements.txt`

### install SMT Solver
- Install MathSAT (other solvers would likely work as well):
`pysmt-install --msat`
- Update PYTHONPATH:
`pysmt-install --env`
- Run output of the above command. Example for my machine below:
`export PYTHONPATH="/home/andrey/.local/lib/python3.6/site-packages:${PYTHONPATH}"`

### Leave virtual environment
`deactivate`

## Solving and Graphing

## Generating data
'utils.py' generates obstacle maps of various sizes and obstacle counts. They are stored in the 'mapData' folder, along with some pre-generated maps. Obstacle maps are stored as '.csv'.
Example usage:
> 'utils.py '