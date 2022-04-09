from __future__ import division
from itertools import count
import numpy as np
from scipy.sparse import csc_matrix


class Buses:
    _idsActiveBuses = count(1)
    _idsAllBuses = count(1)

    _node_index = count(0)
    bus_key_ = {}
    all_bus_key_ = {}

    def __init__(self,
                 Bus,
                 Type,
                 Vm_init,
                 Va_init,
                 Area):
        """Initialize an instance of the Buses class.

        Args:
            Bus (int): The bus number.
            Type (int): The type of bus (e.g., PV, PQ, of Slack)
            Vm_init (float): The initial voltage magnitude at the bus.
            Va_init (float): The initial voltage angle at the bus.
            Area (int): The zone that the bus is in.
        """

        self.Bus = Bus
        self.Type = Type
        self.Vm_init = Vm_init
        self.Va_init = Va_init

        # initialize all nodes
        self.node_Vr = None # real voltage node at a bus
        self.node_Vi = None # imaginary voltage node at a bus
        self.node_Q = None  # reactive power or voltage contstraint node at a bus

        # initialize the bus key
        self.idAllBuses = self._idsAllBuses.__next__()
        Buses.all_bus_key_[self.Bus] = self.idAllBuses - 1

    def __str__(self):
        return_string = 'The bus number is : {} with Vr node as: {} and Vi node as {} '.format(self.Bus,
                                                                                               self.node_Vr,
                                                                                               self.node_Vi)
        return return_string

    def assign_nodes(self):
        """Assign nodes based on the bus type.

        Returns:
            None
        """
        # If Slack or PQ Bus
        if self.Type == 1 or self.Type == 3:
            self.node_Vr = self._node_index.__next__()
            self.node_Vi = self._node_index.__next__()

        # If PV Bus
        elif self.Type == 2:
            self.node_Vr = self._node_index.__next__()
            self.node_Vi = self._node_index.__next__()
            self.node_Q = self._node_index.__next__()


    def lin_stamp_control(self, J, size, slack, shunt):
        Y = csc_matrix((size,size))
        for ele in slack:
            if(ele.Bus == self.Bus):
                slacklin = ele.stamp_lin(J, size, self.node_Vr, self.node_Vi)
                Y += slacklin
        for ele in shunt:
            if(ele.Bus == self.Bus):
                shuntlin = ele.stamp_lin(size, self.node_Vr, self.node_Vi)
                Y += shuntlin
        return Y

    def nl_stmp_cntrl(self, J, vp, gen, load, size):
        Y = csc_matrix((size,size))
        for ele in gen:
            if(ele.Bus == self.Bus):
                Y += ele.stamp_nl(J, vp, size, self.node_Vr, self.node_Vi, self.node_Q)
        for ele in load:
            if(ele.Bus == self.Bus):
                Y += ele.stamp_nl(J, vp, size, self.node_Vr, self.node_Vi)
        return Y


