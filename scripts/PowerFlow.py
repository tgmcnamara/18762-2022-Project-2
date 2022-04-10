import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve


class PowerFlow:

	def __init__(self,
				 case_name,
				 tol,
				 max_iters,
				 enable_limiting):
		"""Initialize the PowerFlow instance.

		Args:
			case_name (str): A string with the path to the test case.
			tol (float): The chosen NR tolerance.
			max_iters (int): The maximum number of NR iterations.
			enable_limiting (bool): A flag that indicates if we use voltage limiting or not in our solver.
		"""
		# Clean up the case name string
		case_name = case_name.replace('.RAW', '')
		case_name = case_name.replace('testcases/', '')

		self.case_name = case_name
		self.tol = tol
		self.max_iters = max_iters
		self.enable_limiting = enable_limiting

	def solve(self, row, col, val, ind, J):
		size = np.shape(J)[0]
		# Hack off unused parts of constructor arrays
		Y = ( csr_matrix((val[0:ind-1], (row[0:ind-1], col[0:ind-1])),
					shape=(size, size)) )
		return spsolve(Y, J)

	def apply_limiting(self, bus, v_new, v_sol):
		limit = 0.05
		vmax = 1.5
		# v_new - v_sol convention
		# if positive, then apply maximum limiting
		# if negative, then apply minimum limiting
		# Create temp array which captures the delta
		v_temp = v_new - v_sol
		for b in bus:
			Vr_n = b.node_Vr
			Vi_n = b.node_Vi
			dVr = v_temp[Vr_n, 0]
			dVi = v_temp[Vi_n, 0]

			# Real
			# Check delta
			if dVr > limit:
				v_new[Vr_n, 0] = v_sol[Vr_n, 0] + limit
			elif dVr < -limit:
				v_new[Vr_n, 0] = v_sol[Vr_n, 0] - limit
			# Check absolute limits
			if v_new[Vr_n, 0] > vmax:
				v_new[Vr_n, 0] = vmax
			if v_new[Vr_n, 0] < -vmax:
				v_new[Vr_n, 0] = -vmax

			# Imaginary
			# Check delta
			if dVi > limit:
				v_new[Vi_n, 0] = v_sol[Vi_n, 0] + limit
			elif dVi < -limit:
				v_new[Vi_n, 0] = v_sol[Vi_n, 0] - limit
			# Check absolute limits
			if v_new[Vi_n, 0] > vmax:
				v_new[Vi_n, 0] = vmax
			if v_new[Vi_n, 0] < -vmax:
				v_new[Vi_n, 0] = -vmax

	def check_error(self, v_sol, v_new):
		err = np.absolute(v_sol-v_new)
		return np.amax(err)

	def stamp_linear(self, bus, slack, branch, transformer, shunt, row_ind, col_ind, val_ind, ind, J):
		for b in branch:
			ind = b.stamp_linear(bus, row_ind, col_ind, val_ind, ind)
		for s in slack:
			ind = s.stamp_linear(bus, row_ind, col_ind, val_ind, ind, J)
		for t in transformer:
			ind = t.stamp_linear(bus, row_ind, col_ind, val_ind, ind)
		for u in shunt:
			# Stamp for fixed shunts
			ind = u.stamp_linear(bus, row_ind, col_ind, val_ind, ind)
		return ind

	def stamp_nonlinear(self, bus, generator, load, row, col, val, ind, v, J):
		# Loop through generators
		for g in generator:
			ind = g.stamp_nonlinear(bus, row, col, val, ind, v, J)
		# Loop through loads
		for l in load:
			ind = l.stamp_nonlinear(bus, row, col, val, ind, v, J)
		return ind

	def run_powerflow(self,
					  v_init,
					  bus,
					  slack,
					  generator,
					  transformer,
					  branch,
					  shunt,
					  load):
		"""Runs a positive sequence power flow using the Equivalent Circuit Formulation.

		Args:
			v_init (np.array): The initial solution vector which has the same number of rows as the Y matrix.
			bus (list): Contains all the buses in the network as instances of the Buses class.
			slack (list): Contains all the slack generators in the network as instances of the Slack class.
			generator (list): Contains all the generators in the network as instances of the Generators class.
			transformer (list): Contains all the transformers in the network as instance of the Transformers class.
			branch (list): Contains all the branches in the network as instances of the Branches class.
			shunt (list): Contains all the shunts in the network as instances of the Shunts class.
			load (list): Contains all the loads in the network as instances of the Load class.

		Returns:
			v(np.array): The final solution vector.

		"""

		# # # Copy v_init into the Solution Vectors used during NR, v, and the final solution vector v_sol # # #
		v = np.copy(v_init)
		v_sol = np.copy(v)


		# # # Create constructors for sparse Y matrix and J vector # # #
		row_ind = np.empty(500000)
		col_ind = np.empty(500000)
		val_ind = np.empty(500000)
		ind = 0
		J = np.zeros(v.shape)

		# # # Stamp Linear Power Grid Elements into Y matrix # # #
		ind = self.stamp_linear(bus, slack, branch, transformer, shunt, row_ind, col_ind, val_ind, ind, J)

		# # # Initialize While Loop (NR) Variables # # #
		err_max = 1  # maximum error at the current NR iteration
		tol = self.tol  # chosen NR tolerance
		NR_count = 1  # current NR iteration

		# # # Begin Solving Via NR # # #
		while err_max > tol:

			# Exit if max iterations exceeded
			if NR_count > self.max_iters:
				break

			# Create copy of linear-stamped matrix to modify
			NR_row = np.copy(row_ind)
			NR_col = np.copy(col_ind)
			NR_val = np.copy(val_ind)
			NR_J = np.copy(J)
			NR_ind = ind

			# # # Stamp Nonlinear Power Grid Elements into Y matrix # # #
			NR_ind = self.stamp_nonlinear(bus, generator, load, NR_row, NR_col, NR_val, NR_ind, v_sol, NR_J)

			# # # Solve The System # # #
			v_new = self.solve(NR_row, NR_col, NR_val, NR_ind, NR_J)
			v_new = np.reshape(v_new, (-1, 1))

			# # # Append the most recent solution to v
			v = np.append(v, v_new, axis=1)

			# # # Compute The Error at the current NR iteration # # #
			err_max = self.check_error(v_sol, v_new)

			# # # Compute The Error at the current NR iteration # # #
			if self.enable_limiting and err_max > tol:
				self.apply_limiting(bus, v_new, v_sol)
			else:
				pass

			# Increment the NR iteration count
			NR_count += 1
			v_sol = np.copy(v_new)
		return v
