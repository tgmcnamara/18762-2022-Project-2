from __future__ import division
from itertools import count
from models.Buses import Buses


class Shunts:
	_ids = count(0)

	def __init__(self,
				 Bus,
				 G_MW,
				 B_MVAR,
				 shunt_type,
				 Vhi,
				 Vlo,
				 Bmax,
				 Bmin,
				 Binit,
				 controlBus,
				 flag_control_shunt_bus=False,
				 Nsteps=[0],
				 Bstep=[0]):

		""" Initialize a shunt in the power grid.
		Args:
			Bus (int): the bus where the shunt is located
			G_MW (float): the active component of the shunt admittance as MW per unit voltage
			B_MVAR (float): reactive component of the shunt admittance as  MVar per unit voltage
			shunt_type (int): the shunt control mode, if switched shunt
			Vhi (float): if switched shunt, the upper voltage limit
			Vlo (float): if switched shunt, the lower voltage limit
			Bmax (float): the maximum shunt susceptance possible if it is a switched shunt
			Bmin (float): the minimum shunt susceptance possible if it is a switched shunt
			Binit (float): the initial switched shunt susceptance
			controlBus (int): the bus that the shunt controls if applicable
			flag_control_shunt_bus (bool): flag that indicates if the shunt should be controlling another bus
			Nsteps (list): the number of steps by which the switched shunt should adjust itself
			Bstep (list): the admittance increase for each step in Nstep as MVar at unity voltage
		"""
		self.bus = Bus
		self.id = self._ids.__next__()
		self.G = G_MW/100
		self.B = B_MVAR/100
		self.type = shunt_type

	def stamp_linear(self, bus, row, col, val, ind):
		bus_id = Buses.all_bus_key_[self.bus]
		node_Vr = bus[bus_id].node_Vr
		node_Vi = bus[bus_id].node_Vi
		# Stamp the real circuit
		row[ind] = node_Vr
		col[ind] = node_Vr
		val[ind] = self.G
		ind += 1
		row[ind] = node_Vr
		col[ind] = node_Vi
		val[ind] = -self.B
		ind += 1
		# Stamp the imaginary circuit
		row[ind] = node_Vi
		col[ind] = node_Vr
		val[ind] = self.B
		ind += 1
		row[ind] = node_Vi
		col[ind] = node_Vi
		val[ind] = self.G
		ind += 1

		return ind
