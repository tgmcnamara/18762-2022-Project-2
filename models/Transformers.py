from __future__ import division
from itertools import count
from models.Buses import Buses
import numpy as np


class Transformers:
	_ids = count(0)

	def __init__(self,
				 from_bus,
				 to_bus,
				 r,
				 x,
				 status,
				 tr,
				 ang,
				 Gsh_raw,
				 Bsh_raw,
				 rating):
		"""Initialize a transformer instance

		Args:
			from_bus (int): the primary or sending end bus of the transformer.
			to_bus (int): the secondary or receiving end bus of the transformer
			r (float): the line resitance of the transformer in
			x (float): the line reactance of the transformer
			status (int): indicates if the transformer is active or not
			tr (float): transformer turns ratio
			ang (float): the phase shift angle of the transformer
			Gsh_raw (float): the shunt conductance of the transformer
			Bsh_raw (float): the shunt admittance of the transformer
			rating (float): the rating in MVA of the transformer
		"""
		self.id = self._ids.__next__()
		self.from_bus = from_bus
		self.to_bus = to_bus
		self.r = r
		self.x = x
		self.G = r/(r**2 + x**2)
		self.VCCS = x/(r**2 + x**2)
		self.tr = tr
		self.ang = ang * np.pi / 180
	
	def assign_nodes(self):
		self.node_Vr_ideal = Buses._node_index.__next__()
		self.node_Vi_ideal = Buses._node_index.__next__()
		self.node_Ir_ideal = Buses._node_index.__next__()
		self.node_Ii_ideal = Buses._node_index.__next__()
	
	def init_v(self, v_init, bus):
		# Initialize dummy bus voltages with secondary bus voltage
		bus_id = Buses.all_bus_key_[self.to_bus]
		Vm = bus[bus_id].Vm_init
		Va = bus[bus_id].Va_init * np.pi / 180
		v_init[self.node_Vr_ideal, 0] = Vm*np.cos(Va)
		v_init[self.node_Vi_ideal, 0] = Vm*np.sin(Va)

	def stamp_linear(self, bus, row, col, val, ind):
		# Convenience variables
		tr = self.tr
		ang = self.ang
		r = self.r
		x = self.x
		G = self.G
		VCCS = self.VCCS
		# Shorthand for the nodes
		f_bus = Buses.all_bus_key_[self.from_bus]
		t_bus = Buses.all_bus_key_[self.to_bus]
		# Real
		f_real = bus[f_bus].node_Vr # From
		m_real = self.node_Vr_ideal # Mid
		t_real = bus[t_bus].node_Vr # To
		i_real = self.node_Ir_ideal # Primary current
		# Imaginary
		f_imag = bus[f_bus].node_Vi
		m_imag = self.node_Vi_ideal
		t_imag = bus[t_bus].node_Vi
		i_imag = self.node_Ii_ideal

		# Stamp VCVS
		# Stamps for current variable
		row[ind] = f_real
		col[ind] = i_real
		val[ind] = 1
		ind += 1
		row[ind] = f_imag
		col[ind] = i_imag
		val[ind] = 1
		ind += 1
		row[ind] = i_real
		col[ind] = f_real
		val[ind] = 1
		ind += 1
		row[ind] = i_imag
		col[ind] = f_imag
		val[ind] = 1
		ind += 1
		# Actual values of VCVS
		# Negated so constraint is applied
		row[ind] = i_real
		col[ind] = m_real
		val[ind] = -tr * np.cos(ang)
		ind += 1
		row[ind] = i_real
		col[ind] = m_imag
		val[ind] = tr * np.sin(ang)
		ind += 1
		row[ind] = i_imag
		col[ind] = m_real
		val[ind] = -tr * np.sin(ang)
		ind += 1
		row[ind] = i_imag
		col[ind] = m_imag
		val[ind] = -tr * np.cos(ang)
		ind += 1


		# Stamp VCCS for secondary currents
		row[ind] = m_real
		col[ind] = i_real
		val[ind] = -tr * np.cos(ang)
		ind += 1
		row[ind] = m_real
		col[ind] = i_imag
		val[ind] = -tr * np.sin(ang)
		ind += 1
		row[ind] = m_imag
		col[ind] = i_real
		val[ind] = tr * np.sin(ang)
		ind += 1
		row[ind] = m_imag
		col[ind] = i_imag
		val[ind] = -tr * np.cos(ang)
		ind += 1

		# Stamp the series losses
		# Stamp VCCS, real
		row[ind] = t_real
		col[ind] = t_imag
		val[ind] = VCCS
		ind += 1
		row[ind] = t_real
		col[ind] = m_imag
		val[ind] = -VCCS
		ind += 1
		row[ind] = m_real
		col[ind] = t_imag
		val[ind] = -VCCS
		ind += 1
		row[ind] = m_real
		col[ind] = m_imag
		val[ind] = VCCS
		ind += 1
		# Stamp VCCS, imag
		row[ind] = t_imag
		col[ind] = t_real
		val[ind] = -VCCS
		ind += 1
		row[ind] = t_imag
		col[ind] = m_real
		val[ind] = VCCS
		ind += 1
		row[ind] = m_imag
		col[ind] = t_real
		val[ind] = VCCS
		ind += 1
		row[ind] = m_imag
		col[ind] = m_real
		val[ind] = -VCCS
		ind += 1

		# Stamp conductance, real
		row[ind] = t_real
		col[ind] = t_real
		val[ind] = G
		ind += 1
		row[ind] = t_real
		col[ind] = m_real
		val[ind] = -G
		ind += 1
		row[ind] = m_real
		col[ind] = t_real
		val[ind] = -G
		ind += 1
		row[ind] = m_real
		col[ind] = m_real
		val[ind] = G
		ind += 1
		# Stamp conductance, imag
		row[ind] = t_imag
		col[ind] = t_imag
		val[ind] = G
		ind += 1
		row[ind] = t_imag
		col[ind] = m_imag
		val[ind] = -G
		ind += 1
		row[ind] = m_imag
		col[ind] = t_imag
		val[ind] = -G
		ind += 1
		row[ind] = m_imag
		col[ind] = m_imag
		val[ind] = G
		ind += 1
		return ind
