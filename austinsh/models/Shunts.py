from __future__ import division
from itertools import count


class Shunts:
    _ids = count(0)

    def __init__(self,
                 Bus,
                 G_MW,
                 B_MVAR,
                 shunt_type,
                 Vhi,
                 Vlo,
                 Bmax,
                 Bmin,
                 Binit,
                 controlBus,
                 flag_control_shunt_bus=False,
                 Nsteps=[0],
                 Bstep=[0]):

        """ Initialize a shunt in the power grid.
        Args:
            Bus (int): the bus where the shunt is located
            G_MW (float): the active component of the shunt admittance as MW per unit voltage
            B_MVAR (float): reactive component of the shunt admittance as  MVar per unit voltage
            shunt_type (int): the shunt control mode, if switched shunt
            Vhi (float): if switched shunt, the upper voltage limit
            Vlo (float): if switched shunt, the lower voltage limit
            Bmax (float): the maximum shunt susceptance possible if it is a switched shunt
            Bmin (float): the minimum shunt susceptance possible if it is a switched shunt
            Binit (float): the initial switched shunt susceptance
            controlBus (int): the bus that the shunt controls if applicable
            flag_control_shunt_bus (bool): flag that indicates if the shunt should be controlling another bus
            Nsteps (list): the number of steps by which the switched shunt should adjust itself
            Bstep (list): the admittance increase for each step in Nstep as MVar at unity voltage
        """
        self.id = self._ids.__next__()
        self.bus = Bus
        self.g_mw = G_MW
        self.b_mvar = B_MVAR
        self.g = self.g_mw/100
        self.b = self.b_mvar/100
        self.shunt_type = shunt_type
        self.vhi = Vhi
        self.vlo = Vlo
        self.bmax = Bmax/100
        self.bmin = Bmin/100
        self.binit = Binit/100
        self.controlbus = controlBus
        self.flag_control_shunt_bus = flag_control_shunt_bus
        self.nsteps = Nsteps
        self.bstep = Bstep