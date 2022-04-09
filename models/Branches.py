from __future__ import division
from itertools import count
import numpy as np
from scipy.sparse import csc_matrix


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
        self.from_bus = from_bus
        self.to_bus = to_bus
        self.r = r
        self.x = x
        self.b = b
        self.status = status
        self.rateA = rateA
        self.rateB = rateB
        self.rateC = rateC

        self.Bl = x/(r*r+x*x)
        self.Gl = r/(r*r+x*x)

        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.


    def stamp_lin(self, size, buses):
        Bl = self.Bl
        Gl = self.Gl
        b = self.b/2
        Vrto = None
        Vrfrom = None
        Vito = None
        Vifrom = None
        for ele in buses:
            if ele.Bus == self.to_bus:
                Vrto = ele.node_Vr
                Vito = ele.node_Vi
            if ele.Bus == self.from_bus:
                Vrfrom = ele.node_Vr
                Vifrom = ele.node_Vi
        row = np.array([Vrfrom,Vrfrom,Vrfrom,Vrfrom,Vifrom,Vifrom,Vifrom,Vifrom,\
                        Vrto  ,Vrto  ,Vrto  ,Vrto  ,Vito  ,Vito  ,Vito  ,Vito  ,\
                        Vrfrom,Vifrom,Vrto  ,Vito])

        col = np.array([Vrfrom,Vifrom,Vrto  ,Vito  ,Vrfrom,Vifrom,Vrto  ,Vito  ,\
                        Vrfrom,Vifrom,Vrto  ,Vito  ,Vrfrom,Vifrom,Vrto  ,Vito  ,\
                        Vifrom,Vrfrom,Vito  ,Vrto])

        dat = np.array([Gl    ,-Bl   ,-Gl   ,Bl    ,Bl    ,Gl    ,-Bl   ,-Gl   ,\
                        -Gl   ,Bl    ,Gl    ,-Bl   ,-Bl   ,-Gl   ,Bl    ,Gl    ,\
                        -b    ,b     ,-b    ,b])

        branchlin = csc_matrix((dat, (row, col)), shape=(size,size))
        return branchlin
