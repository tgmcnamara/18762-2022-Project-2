from __future__ import division
from itertools import count
from scripts.global_vars import global_vars
from models.Buses import Buses
import numpy as np

class Generators:
	_ids = count(0)
	RemoteBusGens = dict()
	RemoteBusRMPCT = dict()
	gen_bus_key_ = {}
	total_P = 0

	def __init__(self,
				 Bus,
				 P,
				 Vset,
				 Qmax,
				 Qmin,
				 Pmax,
				 Pmin,
				 Qinit,
				 RemoteBus,
				 RMPCT,
				 gen_type):
		"""Initialize an instance of a generator in the power grid.

		Args:
			Bus (int): the bus number where the generator is located.
			P (float): the current amount of active power the generator is providing.
			Vset (float): the voltage setpoint that the generator must remain fixed at.
			Qmax (float): maximum reactive power
			Qmin (float): minimum reactive power
			Pmax (float): maximum active power
			Pmin (float): minimum active power
			Qinit (float): the initial amount of reactive power that the generator is supplying or absorbing.
			RemoteBus (int): the remote bus that the generator is controlling
			RMPCT (float): the percent of total MVAR required to hand the voltage at the controlled bus
			gen_type (str): the type of generator
		"""
		self.id = self._ids.__next__()
		self.Q_init = Qinit/100.0
		self.bus = Bus
		self.P = P/100.0
		self.Vset = Vset

	def init_v(self, v_init, bus):
		# Set Voltage for all generator buses
		bus_id = Buses.all_bus_key_[self.bus]
		Vm = bus[bus_id].Vm_init
		Va = bus[bus_id].Va_init * np.pi / 180.0
		v_init[bus[bus_id].node_Vr, 0] = Vm*np.cos(Va)
		v_init[bus[bus_id].node_Vi, 0] = Vm*np.sin(Va)
		# For all non-slack buses, set initial Q as well
		if bus[bus_id].Type == 2:
			v_init[bus[bus_id].node_Q, 0] = self.Q_init
	
	def calc_stamps(self, Q, Vr, Vi):
		P = self.P
		den = (Vr**2 + Vi**2)
		# Real Circuit
		self.dIr_Q = -Vi / den
		self.dIr_Vr = ( (-P/den) + 
				(2*P*(Vr**2)) / (den**2) +
				(2*Q*Vr*Vi) / (den**2) )
		self.dIr_Vi = ( (-Q/den) + 
				(2*P*Vr*Vi) / (den**2) +
				(2*Q*(Vi**2)) / (den**2) )
		# Imaginary Circuit
		self.dIi_Q = Vr / den
		self.dIi_Vr = ( (Q/den) - 
				(2*Q*(Vr**2)) / (den**2) +
				(2*P*Vr*Vi) / (den**2) )
		self.dIi_Vi = ( (-P/den) - 
				(2*Q*Vr*Vi) / (den**2) +
				(2*P*(Vi**2)) / (den**2) )

	def stamp_nonlinear(self, bus, row, col, val, ind, v, J):
		# determine all of the previous iteration quantities
		bus_id = Buses.all_bus_key_[self.bus]
		Q =  v[bus[bus_id].node_Q , 0]
		Vr = v[bus[bus_id].node_Vr, 0]
		Vi = v[bus[bus_id].node_Vi, 0]

		# Call create stamp function
		self.calc_stamps(Q, Vr, Vi)

		# Stamp Y matrix and J vector
		node_Q  = bus[bus_id].node_Q 
		node_Vr = bus[bus_id].node_Vr
		node_Vi = bus[bus_id].node_Vi

		# Stamp real Y
		row[ind] = node_Vr
		col[ind] = node_Q
		val[ind] = self.dIr_Q
		ind += 1
		row[ind] = node_Vr
		col[ind] = node_Vr
		val[ind] = self.dIr_Vr
		ind += 1
		row[ind] = node_Vr
		col[ind] = node_Vi
		val[ind] = self.dIr_Vi
		ind += 1
		# Stamp real J
		Irg = ( (-self.P*Vr - Q*Vi) /
				(Vr**2 + Vi**2) )
		J[node_Vr, 0] -= Irg
		dIrg = Q*self.dIr_Q + Vr*self.dIr_Vr + Vi*self.dIr_Vi
		J[node_Vr, 0] += dIrg

		# Stamp imaginary Y
		row[ind] = node_Vi
		col[ind] = node_Q
		val[ind] = self.dIi_Q
		ind += 1
		row[ind] = node_Vi
		col[ind] = node_Vr
		val[ind] = self.dIi_Vr
		ind += 1
		row[ind] = node_Vi
		col[ind] = node_Vi
		val[ind] = self.dIi_Vi
		ind += 1
		# Stamp imaginary J
		Iig = ( (-self.P*Vi + Q*Vr) /
				(Vr**2 + Vi**2) )
		J[node_Vi, 0] -= Iig
		dIig = Q*self.dIi_Q + Vr*self.dIi_Vr + Vi*self.dIi_Vi
		J[node_Vi, 0] += dIig

		# Stamp Voltage control condition
		# Stamp Y
		row[ind] = node_Q
		col[ind] = node_Vr
		val[ind] = 2 * Vr
		ind += 1
		row[ind] = node_Q
		col[ind] = node_Vi
		val[ind] = 2 * Vi
		ind += 1
		# Stamp J
		Vsetg = self.Vset**2 + Vr**2 + Vi**2
		J[node_Q, 0] += Vsetg

		return ind
