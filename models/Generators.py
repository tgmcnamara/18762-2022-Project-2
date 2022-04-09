from __future__ import division
from itertools import count
from scripts.global_vars import global_vars
import numpy as np
from scipy.sparse import csc_matrix

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
        self.Bus = Bus
        self.P = P/100
        self.Vset = Vset
        self.Qmin = Qmin
        self.Qmax = Qmax


        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.

    def stamp_nl(self, J, Vp, size, vr, vi, q):
        low = Vp[vr]*Vp[vr] + Vp[vi]*Vp[vi]
        hr = -self.P*Vp[vr] - Vp[q]*Vp[vi]
        hi = -self.P*Vp[vi] + Vp[q]*Vp[vr]

        drdr = (-low*self.P - 2*Vp[vr]*hr)/(low*low)
        drdi = (-low*Vp[q] - 2*Vp[vi]*hr)/(low*low)
        drdq = -Vp[vi]/low

        didr = (low*Vp[q] - 2*hi*Vp[vr])/(low*low)
        didi = (-low*self.P - 2*Vp[vi]*hi)/(low*low)
        didq = Vp[vr]/low

        row = np.array([  vr,  vr,  vr,  vi,  vi,  vi,       q,       q])
        col = np.array([  vr,  vi,   q,  vr,  vi,   q,      vr,      vi])
        dat = np.array([drdr,drdi,drdq,didr,didi,didq,2*Vp[vr],2*Vp[vi]])

        J[vr] += drdr*Vp[vr] + drdi*Vp[vi] + drdq*Vp[q] - hr/low
        J[vi] += didr*Vp[vr] + didi*Vp[vi] + didq*Vp[q] - hi/low
        J[q] += 2*Vp[vr]*Vp[vr] + 2*Vp[vi]*Vp[vi]

        return csc_matrix((dat, (row, col)), shape=(size,size))
