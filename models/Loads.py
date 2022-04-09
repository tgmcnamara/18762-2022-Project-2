from __future__ import division
from itertools import count
import numpy as np
from scipy.sparse import csc_matrix


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
        self.id = Loads._ids.__next__()
        self.P = P/100
        self.Q = Q/100
        self.Bus = Bus


        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.
        #
    def stamp_nl(self, J, Vp, size, vr, vi):
        low = Vp[vr]*Vp[vr] + Vp[vi]*Vp[vi]
        hr = self.P*Vp[vr] + self.Q*Vp[vi]
        hi = self.P*Vp[vi] - self.Q*Vp[vr]

        drdr = (low*self.P - hr*2*Vp[vr])/(low*low)
        drdi = (low*self.Q - hr*2*Vp[vi])/(low*low)

        didr = (-low*self.Q - hi*2*Vp[vr])/(low*low)
        didi = (low*self.P - hi*2*Vp[vi])/(low*low)

        row = np.array([  vr,  vr,  vi,  vi])
        col = np.array([  vr,  vi,  vr,  vi])
        dat = np.array([drdr,drdi,didr,didi])

        J[vr] += drdr*Vp[vr] + drdi*Vp[vi] - hr/low
        J[vi] += didr*Vp[vr] + didi*Vp[vi] - hi/low

        return csc_matrix((dat, (row, col)), shape=(size,size))

