from __future__ import division
from itertools import count
import numpy as np


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
            Type (int): The type of bus (e.g., PV, PQ, or Slack)
            Vm_init (float): The initial voltage magnitude at the bus.
            Va_init (float): The initial voltage angle at the bus.
            Area (int): The zone that the bus is in.
        """

        self.Bus = Bus
        self.Type = Type
        self.vm_init = Vm_init
        self.va_init = Va_init * np.pi/180
        # initialize all nodes
        self.init_Vr = self.vm_init * np.cos(self.va_init)
        self.init_Vi = self.vm_init * np.sin(self.va_init)
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
        # If PQ (loads) or Slack Bus
        if self.Type == 1 or self.Type == 3:
            self.node_Vr = self._node_index.__next__()
            self.node_Vi = self._node_index.__next__()
            self.bus_key_[str(self.Bus) + "_vr"] = self.node_Vr
            self.bus_key_[str(self.Bus) + "_vi"] = self.node_Vi

        # If PV Bus
        elif self.Type == 2:
            self.node_Vr = self._node_index.__next__()
            self.node_Vi = self._node_index.__next__()
            self.node_Q = self._node_index.__next__()
            self.bus_key_[str(self.Bus) + "_vr"] = self.node_Vr
            self.bus_key_[str(self.Bus) + "_vi"] = self.node_Vi
            self.bus_key_[str(self.Bus) + "_q"] = self.node_Q
