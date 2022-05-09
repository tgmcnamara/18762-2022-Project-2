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
        q_by_real_V = 2*real_V
        q_by_imag_V = 2*imag_V
        return real_I_by_q, real_I_by_real_V, real_I_by_imag_V, imag_I_by_q, imag_I_by_real_V, \
                imag_I_by_imag_V, q_by_real_V, q_by_imag_V

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

    def optimize_derivative(self, PreviousSolution):
        LR = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_r"]]
        LI = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_i"]]
        VR = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vr"]]
        VI = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vi"]]
        LQ = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_q"]]
        Q = PreviousSolution[Buses.bus_key_[str(self.bus) + "_q"]]
        real_A_by_real_V = ((2*VR*(LI*Q - LR*self.p)*(VR**2 - 3*VI**2) +
                            2*VI*(LR*Q + LI*self.p)*(VI**2 - 3*VR**2)) /
                            (VR**2 + VI**2)**3) + 2*LQ
        real_A_by_imag_V = ((2*VI*(self.p*LR - Q*LI)*(VI**2 - 3*VR**2) +
                            2*VR*(Q*LR + self.p*LI)*(VR**2 - 3*VI**2)) /
                            (VR**2 + VI**2)**3)
        real_A_by_Q = (LR*2*VR*VI + LI*(VI**2 - VR**2)) / (VR**2 + VI**2)**2
        imag_A_by_real_V = ((2*VR*(LR*Q + LI*self.p)*(VR**2 - 3*VI**2) +
                            2*VI*(LR*self.p - LI*Q)*(VI**2 - 3*VR**2)) /
                            (VR**2 + VI**2)**3)
        imag_A_by_imag_V = ((2*VI*(-self.p*LI - Q*LR)*(VI**2 - 3*VR**2) +
                            2*VR*(-Q*LI + self.p*LR)*(VR**2 - 3*VI**2)) /
                            (VR**2 + VI**2)**3) + 2*LQ
        imag_A_by_Q = (LR*(VI**2 - VR**2) - 2*LI*VR*VI) / (VR**2 + VI**2)**2
        AQ_by_real_V = real_A_by_Q
        AQ_by_imag_V = imag_A_by_Q
        return real_A_by_real_V, real_A_by_imag_V, real_A_by_Q, imag_A_by_real_V, \
            imag_A_by_imag_V, imag_A_by_Q, AQ_by_real_V, AQ_by_imag_V

    def optimize_history(self, PreviousSolution, IR_by_VR, IR_by_VI, II_by_VR, II_by_VI,
                        IR_by_Q, Q_by_VR, Q_by_VI, II_by_Q, AR_by_VR, AR_by_VI, AI_by_VR, 
                        AI_by_VI, AR_by_Q, AI_by_Q, AQ_by_VR, AQ_by_VI):
        LR = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_r"]]
        LI = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_i"]]
        LQ = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_q"]]
        VR = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vr"]]
        VI = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vi"]]
        Q = PreviousSolution[Buses.bus_key_[str(self.bus) + "_q"]]
        real_A = LR*IR_by_VR + LI*II_by_VR + LQ*Q_by_VR
        imag_A = LR*IR_by_VI + LI*II_by_VI + LQ*Q_by_VI
        AQ = LR*IR_by_Q + LI*II_by_Q
        j_real_stamp = - (real_A - AR_by_VR*VR - AR_by_VI*VI - AR_by_Q*Q - IR_by_VR*LR - 
                        II_by_VR*LI - Q_by_VR*LQ)
        j_imag_stamp = - (imag_A - AI_by_VR*VR - AI_by_VI*VI - AI_by_Q*Q - IR_by_VI*LR -
                        II_by_VI*LI - Q_by_VI*LQ)
        j_q_stamp = - (AQ - AQ_by_VR*VR - AQ_by_VI*VI - IR_by_Q*LR - II_by_Q*LI)
        return j_real_stamp, j_imag_stamp, j_q_stamp