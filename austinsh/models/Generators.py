from __future__ import division
from itertools import count
from models.Buses import Buses
from more_itertools import bucket
from scripts.global_vars import global_vars


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
        self.bus = Bus
        self.p = P/100
        self.vset = Vset
        self.qmax = Qmax/100
        self.qmin = Qmin/100
        self.pmax = Pmax/100
        self.pmin = Pmin/100
        self.q = Qinit/100
        self.remotebus = RemoteBus
        self.rmpct = RMPCT
        self.gen_type = gen_type
        
    def pv_derivative(self, PreviousSolution):
        real_V = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vr"]]
        imag_V = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vi"]]
        q_gen = PreviousSolution[Buses.bus_key_[str(self.bus) + "_q"]]
        real_I_by_q = -imag_V / (real_V**2 + imag_V**2)
        real_I_by_real_V = ((self.p*(real_V**2 - imag_V**2) + 2 * q_gen * real_V * imag_V) /
                            (real_V**2 + imag_V**2)**2)
        real_I_by_imag_V = ((q_gen*(imag_V**2 - real_V**2) + 2 * self.p * real_V * imag_V) /
                            (real_V**2 + imag_V**2)**2)
        imag_I_by_q = real_V / (real_V**2 + imag_V**2)
        imag_I_by_real_V = real_I_by_imag_V
        imag_I_by_imag_V = -real_I_by_real_V
        real_V_by_q = 2*real_V
        imag_V_by_q = 2*imag_V
        return real_I_by_q, real_I_by_real_V, real_I_by_imag_V, imag_I_by_q, imag_I_by_real_V, \
                imag_I_by_imag_V, real_V_by_q, imag_V_by_q

    def pv_history(self, PreviousSolution, IR_by_Q, IR_by_VR, IR_by_VI, II_by_Q, II_by_VR, II_by_VI):
        real_V = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vr"]]
        imag_V = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vi"]]
        q_gen = PreviousSolution[Buses.bus_key_[str(self.bus) + "_q"]]
        real_I = (-self.p * real_V - q_gen * imag_V) / (real_V**2 + imag_V**2)
        imag_I = (-self.p * imag_V + q_gen * real_V) / (real_V**2 + imag_V**2)
        j_real_stamp = - (real_I - IR_by_Q * q_gen - IR_by_VR * real_V - IR_by_VI * imag_V)
        j_imag_stamp = - (imag_I - II_by_Q * q_gen - II_by_VR * real_V - II_by_VI * imag_V)
        j_q_stamp = self.vset**2 + real_V**2 + imag_V**2
        return j_real_stamp, j_imag_stamp, j_q_stamp