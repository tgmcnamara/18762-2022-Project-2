import numpy as np
import os
from models.Buses import Buses

def process_results(bus, v):
	# Create new output file to hold statistics
	if os.path.exists("powerflow.txt"):
		os.remove("powerflow.txt")
	f = open("powerflow.txt", "w+")
	# Print output and write in nice format to file
	for b in bus:
		b.display_grid_data(v[:, -1], f)
	# Close file to force write
	f.close()
	# Reopen file to start at beginning and get statistics
	f = open("powerflow.txt", "r")
	# Use first bus as basis, work through list
	init = f.readline().split()
	min_mag_bus = init[0]
	max_mag_bus = init[0]
	min_mag = float(init[1])
	max_mag = float(init[1])
	min_ang_bus = init[0]
	max_ang_bus = init[0]
	min_ang = float(init[2])
	max_ang = float(init[2])
	# Loop through remainder of file
	for r in f:
		curr = r.split()
		# Check magnitude
		if float(curr[1]) > max_mag:
			max_mag_bus = curr[0]
			max_mag = float(curr[1])
		if float(curr[1]) < min_mag:
			min_mag_bus = curr[0]
			min_mag = float(curr[1])
		# Check phase
		if float(curr[2]) > max_ang:
			max_ang_bus = curr[0]
			max_ang = float(curr[2])
		if float(curr[2]) < min_ang:
			min_ang_bus = curr[0]
			min_ang = float(curr[2])
	# Close the file
	f.close()
	# Print out the stats
	print("MAX VOLTAGE: BUS", max_mag_bus,",", max_mag, "V")
	print("MIN VOLTAGE: BUS", min_mag_bus, ",", min_mag, "V")
	print("MAX ANGLE: BUS", max_ang_bus, ",", max_ang, "\xb0")
	print("MIN ANGLE: BUS", min_ang_bus, ",", min_ang, "\xb0")
	# Print out the number of N-R iterations required
	print("NR Iterations: ", v.shape[1] - 1)
