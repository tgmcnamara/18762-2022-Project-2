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
        self.vset = Vset
        self.ang = ang * np.pi / 180
        self.pinit = Pinit/100
        self.qinit = Qinit/100
        self.vrset = self.vset * np.cos(self.ang)
        self.viset = self.vset * np.sin(self.ang)
        self.ir_init = (self.vrset*self.pinit + self.viset*self.qinit)/(self.vset**2)
        self.ii_init = (self.viset*self.pinit - self.vrset*self.qinit)/(self.vset**2)

    def assign_nodes(self):
        """Assign the additional slack bus nodes for a slack bus.

        Returns:
            None
        """
        self.node_Ir_Slack = Buses._node_index.__next__()
        self.node_Ii_Slack = Buses._node_index.__next__()

    def optimization_nodes(self):
        self.node_lambdar_ir = Buses._node_index.__next__()
        self.node_lambdai_ii = Buses._node_index.__next__()