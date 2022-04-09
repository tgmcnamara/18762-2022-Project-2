from __future__ import division
from models.Buses import Buses
import numpy as np
from scipy.sparse import csc_matrix


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
        # You will need to implement the remainder of the __init__ function yourself.
        self.Bus = Bus
        self.Vset = Vset
        self.ang = ang
        self.Pinit = Pinit
        self.Qinit = Qinit

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

        #print(self.node_Vr_Slack)
        #print(self.node_Vi_Slack)
    # You should also add some other class functions you deem necessary for stamping,
    # initializing, and processing results.

    def stamp_lin(self, J, size, node_Vr, node_Vi):
        row = np.array([node_Vr, node_Vi, self.node_Vr_Slack, self.node_Vi_Slack])
        col = np.array([self.node_Vr_Slack, self.node_Vi_Slack, node_Vr, node_Vi])
        data = np.array([1,1,1,1])

        J[self.node_Vr_Slack] += self.Vset*np.cos(2*np.pi*self.ang)
        J[self.node_Vi_Slack] += self.Vset*np.sin(2*np.pi*self.ang)

        slackLin = csc_matrix((data, (row, col)), shape=(size,size))
        return slackLin

