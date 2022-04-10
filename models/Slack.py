from __future__ import division
from models.Buses import Buses
import numpy as np


class Slack:

	def __init__(self,
				 Bus,
				 Vset,
				 ang,
				 Pinit,
				 Qinit):
		"""Initialize slack bus in the power grid.

		Args:
			Bus (int): the bus number corresponding to the slack bus.
			Vset (float): the voltage setpoint that the slack bus must remain fixed at.
			ang (float): the slack bus voltage angle that it remains fixed at.
			Pinit (float): the initial active power that the slack bus is supplying
			Qinit (float): the initial reactive power that the slack bus is supplying
		"""
		self.bus = Bus
		self.Vset = Vset
		self.ang = ang
		self.Pinit = -Pinit/100
		self.Qinit = Qinit/100

		# initialize nodes
		self.node_Vr_Slack = None
		self.node_Vi_Slack = None

	def assign_nodes(self):
		"""Assign the additional slack bus nodes for a slack bus.

		Returns:
			None
		"""
		self.node_Vr_Slack = Buses._node_index.__next__()
		self.node_Vi_Slack = Buses._node_index.__next__()

	def init_v(self, v_init, bus):
		# Set Voltage at the slack bus
		bus_id = Buses.all_bus_key_[self.bus]
		Vm = self.Vset
		Va = self.ang * np.pi / 180
		v_init[bus[bus_id].node_Vr, 0] = Vm*np.cos(Va)
		v_init[bus[bus_id].node_Vi, 0] = Vm*np.sin(Va)
		# Add garbage value for slack bus currents
		v_init[self.node_Vr_Slack, 0] = 0
		v_init[self.node_Vi_Slack, 0] = 0
			
	def stamp_linear(self, bus, row, col, val, ind, J):
		bus_id = Buses.all_bus_key_[self.bus]
		Vm = self.Vset
		Va = self.ang * np.pi / 180
		# Stamp the source constants
		row[ind] = bus[bus_id].node_Vr
		col[ind] = self.node_Vr_Slack
		val[ind] = 1
		ind += 1
		row[ind] = bus[bus_id].node_Vi
		col[ind] = self.node_Vi_Slack
		val[ind] = 1
		ind += 1
		row[ind] = self.node_Vr_Slack
		col[ind] = bus[bus_id].node_Vr
		val[ind] = 1
		ind += 1
		row[ind] = self.node_Vi_Slack
		col[ind] = bus[bus_id].node_Vi
		val[ind] = 1
		ind += 1
		# Stamp the J vector
		J[self.node_Vr_Slack, 0] = Vm*np.cos(Va)
		J[self.node_Vi_Slack, 0] = Vm*np.sin(Va)
		return ind
