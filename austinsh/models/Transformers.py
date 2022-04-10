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
        self.status = status
        self.tr = tr
        self.ang = ang * np.pi/180
        self.gsh_raw = Gsh_raw
        self.bsh_raw = Bsh_raw
        self.rating = rating/100
        self.cos = tr * np.cos(self.ang)
        self.sin = tr * np.sin(self.ang)
        self.se_coeff = self.x / (self.r**2 + self.x**2)
        self.conductance = self.r / (self.r**2 + self.x**2)

    def assign_nodes(self):
        """Assign the additional transformer bus nodes.

        Returns:
            None
        """
        self.node_Ir_i = Buses._node_index.__next__()
        self.node_Ii_i = Buses._node_index.__next__()
        self.node_Vr_2 = Buses._node_index.__next__()
        self.node_Vi_2 = Buses._node_index.__next__()
