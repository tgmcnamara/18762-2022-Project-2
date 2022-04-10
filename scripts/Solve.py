from parsers.parser import parse_raw
from scripts.PowerFlow import PowerFlow
from scripts.process_results import process_results
from scripts.initialize import initialize
from models.Buses import Buses
import numpy as np


def solve(TESTCASE, SETTINGS):
	"""Run the power flow solver.

	Args:
		TESTCASE (str): A string with the path to the test case.
		SETTINGS (dict): Contains all the solver settings in a dictionary.

	Returns:
		None
	"""

	# # # Parse the Test Case Data # # #
	case_name = TESTCASE
	parsed_data = parse_raw(case_name)

	# # # Assign Parsed Data to Variables # # #
	bus = parsed_data['buses']
	slack = parsed_data['slack']
	generator = parsed_data['generators']
	transformer = parsed_data['xfmrs']
	branch = parsed_data['branches']
	shunt = parsed_data['shunts']
	load = parsed_data['loads']

	# # # Solver Settings # # #
	tol = SETTINGS['Tolerance']  # NR solver tolerance
	max_iters = SETTINGS['Max Iters']  # maximum NR iterations
	enable_limiting = SETTINGS['Limiting']  # enable/disable voltage and reactive power limiting

	# # # Assign System Nodes Bus by Bus # # #
	# We can use these nodes to have predetermined node number for every node in our Y matrix and J vector.
	for ele in bus:
		ele.assign_nodes()

	# Assign any slack nodes
	for ele in slack:
		ele.assign_nodes()

	# CONSIDER ADDITIONAL NODES FOR XFMR HERE
	for ele in transformer:
		ele.assign_nodes()

	# # # Initialize Solution Vector - V and Q values # # #

	# determine the size of the Y matrix by looking at the total number of nodes in the system
	size_Y = Buses._node_index.__next__()

	# Function to initialize solution vector v_init.
	empty = np.zeros((size_Y, 1))  # create a solution vector filled with zeros of size_Y
	v_init = initialize(empty, bus, generator, load, slack, transformer)
	
	# # # Run Power Flow # # #
	powerflow = PowerFlow(case_name, tol, max_iters, enable_limiting)
	v = powerflow.run_powerflow(v_init, bus, slack, generator, transformer, branch, shunt, load)

	# # # Process Results # # #
	process_results(bus, v)
