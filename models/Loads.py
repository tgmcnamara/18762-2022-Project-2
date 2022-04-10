from __future__ import division
from itertools import count
from models.Buses import Buses
import numpy as np

class Loads:
	_ids = count(0)

	def __init__(self,
				 Bus,
				 P,
				 Q,
				 IP,
				 IQ,
				 ZP,
				 ZQ,
				 area,
				 status):
		"""Initialize an instance of a PQ or ZIP load in the power grid.

		Args:
			Bus (int): the bus where the load is located
			P (float): the active power of a constant power (PQ) load.
			Q (float): the reactive power of a constant power (PQ) load.
			IP (float): the active power component of a constant current load.
			IQ (float): the reactive power component of a constant current load.
			ZP (float): the active power component of a constant admittance load.
			ZQ (float): the reactive power component of a constant admittance load.
			area (int): location where the load is assigned to.
			status (bool): indicates if the load is in-service or out-of-service.
		"""
		self.bus = Bus
		self.id = Loads._ids.__next__()
		self.P = P/100.0
		self.Q = Q/100.0
	
	def init_v(self, v_init, bus):
		# Want to use self.bus to key into the list of buses and find the Vr and Vi
		# indices
		bus_id = Buses.all_bus_key_[self.bus]
		Vm = bus[bus_id].Vm_init
		Va = bus[bus_id].Va_init * np.pi / 180.0
		v_init[bus[bus_id].node_Vr, 0] = Vm*np.cos(Va)
		v_init[bus[bus_id].node_Vi, 0] = Vm*np.sin(Va)
			
	def calc_stamps(self, Vr, Vi):
		P = self.P
		Q = self.Q
		denom = Vr**2 + Vi**2
		# Calculate real stamps
		self.dIr_Vr = ( (P/denom) - (2*P*(Vr**2)/(denom**2))
				- (2*Q*Vr*Vi/(denom**2)) )
		self.dIr_Vi = ( (Q/denom) - (2*Q*(Vi**2)/(denom**2))
				- (2*P*Vr*Vi/(denom**2)) )
		# Calculate imaginary stamps
		self.dIi_Vr = ( (-Q/denom) + (2*Q*(Vr**2)/(denom**2))
				- (2*P*Vr*Vi/(denom**2)) )
		self.dIi_Vi = ( (P/denom) - (2*P*(Vi**2)/(denom**2))
				+ (2*Q*Vr*Vi/(denom**2)) )

	def stamp_nonlinear(self, bus, row, col, val, ind, v, J):
		bus_id = Buses.all_bus_key_[self.bus]
		node_Vr = bus[bus_id].node_Vr
		node_Vi = bus[bus_id].node_Vi
		Vr = v[node_Vr, 0]
		Vi = v[node_Vi, 0]
		# Calculate the stamp values
		self.calc_stamps(Vr, Vi)

		# Stamp the real circuit Y
		row[ind] = node_Vr
		col[ind] = node_Vr
		val[ind] = self.dIr_Vr
		ind += 1
		row[ind] = node_Vr
		col[ind] = node_Vi
		val[ind] = self.dIr_Vi
		ind += 1
		# Stamp the real J
		Irl = ( (self.P*Vr + self.Q*Vi) /
				(Vr**2 + Vi**2) )
		J[node_Vr, 0] -= Irl
		dIrl = self.dIr_Vr*Vr + self.dIr_Vi*Vi
		J[node_Vr, 0] += dIrl

		# Stamp the imaginary circuit Y
		row[ind] = node_Vi
		col[ind] = node_Vr
		val[ind] = self.dIi_Vr
		ind += 1
		row[ind] = node_Vi
		col[ind] = node_Vi
		val[ind] = self.dIi_Vi
		ind += 1
		# Stamp the imaginary J
		Iil = ( (self.P*Vi - self.Q*Vr) /
				(Vr**2 + Vi**2) )
		J[node_Vi, 0] -= Iil
		dIil = self.dIi_Vr*Vr + self.dIi_Vi*Vi
		J[node_Vi, 0] += dIil

		return ind
