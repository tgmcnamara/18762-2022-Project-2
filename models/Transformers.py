from __future__ import division
from itertools import count
from models.Buses import Buses
import numpy as np
from scipy.sparse import csc_matrix


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
        self.nodeAr = None
        self.nodeAi = None
        self.nodeBr = None
        self.nodeBi = None
        self.tr = tr
        self.trcos = tr*np.cos(2*np.pi*ang)
        self.trsin = tr*np.sin(2*np.pi*ang)
        self.Bl = x/(x*x + r*r)
        self.Gl = r/(x*x + r*r)
        self.from_bus = from_bus
        self.to_bus = to_bus

        # You will need to implement the remainder of the __init__ function yourself.
        # You should also add some other class functions you deem necessary for stamping,
        # initializing, and processing results.

    def assign_nodes(self):
        self.nodeAr = Buses._node_index.__next__()
        self.nodeAi = Buses._node_index.__next__()
        self.nodeBr = Buses._node_index.__next__()
        self.nodeBi = Buses._node_index.__next__()

    def stmp_lin(self, size, buses):
        Bl = self.Bl
        Gl = self.Gl
        nodeAi = self.nodeAi
        nodeAr = self.nodeAr
        nodeBi = self.nodeBi
        nodeBr = self.nodeBr
        trsin = self.trsin
        trcos = self.trcos
        Vrto = None
        Vito = None
        Vrfrom = None
        Vifrom = None
        for ele in buses:
            if ele.Bus == self.to_bus:
                Vrto = ele.node_Vr
                Vito = ele.node_Vi
            if ele.Bus == self.from_bus:
                Vrfrom = ele.node_Vr
                Vifrom = ele.node_Vi

        row = np.array([Vrfrom,Vifrom,nodeAr,nodeAr,nodeAr,nodeAi,nodeAi,nodeAi,\
                  Vrto,  Vrto,  Vrto,  Vrto,  Vito,  Vito,  Vito,  Vito,\
                  nodeBr,nodeBr,nodeBr,nodeBr,nodeBr,nodeBr,nodeBi,nodeBi,nodeBi,nodeBi,nodeBi,nodeBi])

        col = np.array([nodeAr,nodeAi,Vrfrom,nodeBr,nodeBi,Vifrom,nodeBr,nodeBi,\
                  Vrto,  Vito,nodeBr,nodeBi,  Vrto,  Vito,nodeBr,nodeBi,\
                    Vrto,  Vito,nodeAr,nodeAi,nodeBr,nodeAi,  Vrto,  Vito,nodeAr,nodeAi,nodeBr,nodeBi])

        dat = np.array([     1,     1,     1, trcos,-trsin,     1, trsin, trcos,\
                    Gl,    Bl,   -Gl,   -Bl,   -Bl,    Gl,    Bl,   -Gl,\
                     -Gl,   -Bl,-trcos,-trsin,    Gl,    Bl,    Bl,   -Gl, trsin,-trcos,   -Bl,    Gl])

        return csc_matrix((dat, (row, col)), shape=(size,size))
