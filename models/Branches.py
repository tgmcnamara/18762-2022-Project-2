from __future__ import division
from itertools import count
from models.Buses import Buses
import numpy as np


class Branches:
	_ids = count(0)

	def __init__(self,
				 from_bus,
				 to_bus,
				 r,
				 x,
				 b,
				 status,
				 rateA,
				 rateB,
				 rateC):
		"""Initialize a branch in the power grid.

		Args:
			from_bus (int): the bus number at the sending end of the branch.
			to_bus (int): the bus number at the receiving end of the branch.
			r (float): the branch resistance
			x (float): the branch reactance
			b (float): the branch susceptance
			status (bool): indicates if the branch is online or offline
			rateA (float): The 1st rating of the line.
			rateB (float): The 2nd rating of the line
			rateC (float): The 3rd rating of the line.
		"""
		self.id = self._ids.__next__()
		self.r = r
		self.b = b
		self.x = x
		self.from_bus = from_bus
		self.to_bus = to_bus
		self.G = r/(r**2 + x**2)
		self.VCCS = x/(r**2 + x**2)
	
	def stamp_linear(self, bus, row, col, val, ind):
		# Append to the given arrays
		f_bus = Buses.all_bus_key_[self.from_bus]
		t_bus = Buses.all_bus_key_[self.to_bus]
		f_real = bus[f_bus].node_Vr
		t_real = bus[t_bus].node_Vr
		f_imag = bus[f_bus].node_Vi
		t_imag = bus[t_bus].node_Vi

		# Stamp the real circuit components
		# Stamp VCCS, series and shunt
		# Real circuit from
		row[ind] = f_real
		col[ind] = f_imag
		val[ind] = self.VCCS - (self.b/2.0)
		ind += 1
		row[ind] = f_real
		col[ind] = t_imag
		val[ind] = -self.VCCS
		ind += 1
		# Real circuit to
		row[ind] = t_real
		col[ind] = f_imag
		val[ind] = -self.VCCS
		ind += 1
		row[ind] = t_real
		col[ind] = t_imag
		val[ind] = self.VCCS - (self.b/2.0)
		ind += 1

		# Stamp Conductance
		# Real circuit from
		row[ind] = f_real
		col[ind] = f_real
		val[ind] = self.G
		ind += 1
		row[ind] = f_real
		col[ind] = t_real
		val[ind] = -self.G
		ind += 1
		# Real circuit to
		row[ind] = t_real
		col[ind] = f_real
		val[ind] = -self.G
		ind += 1
		row[ind] = t_real
		col[ind] = t_real
		val[ind] = self.G
		ind += 1

		# Stamp the imaginary circuit components
		# Stamp VCCS, series and shunt
		# Imaginary circuit from
		row[ind] = f_imag
		col[ind] = f_real
		val[ind] = -self.VCCS + (self.b/2.0)
		ind += 1
		row[ind] = f_imag
		col[ind] = t_real
		val[ind] = self.VCCS
		ind += 1
		# Imaginary circuit to
		row[ind] = t_imag
		col[ind] = f_real
		val[ind] = self.VCCS
		ind += 1
		row[ind] = t_imag
		col[ind] = t_real
		val[ind] = -self.VCCS + (self.b/2.0)
		ind += 1

		# Stamp Conductance
		# Imaginary circuit from
		row[ind] = f_imag
		col[ind] = f_imag
		val[ind] = self.G
		ind += 1
		row[ind] = f_imag
		col[ind] = t_imag
		val[ind] = -self.G
		ind += 1
		# Imaginary circuit to
		row[ind] = t_imag
		col[ind] = f_imag
		val[ind] = -self.G
		ind += 1
		row[ind] = t_imag
		col[ind] = t_imag
		val[ind] = self.G
		ind += 1

		return ind
