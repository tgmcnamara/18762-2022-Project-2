from __future__ import division
from itertools import count
from models.Buses import Buses

class Loads:
    _ids = count(0)

    def __init__(self,
                 Bus,
                 P,
                 Q,
                 IP,
                 IQ,
                 ZP,
                 ZQ,
                 area,
                 status):
        """Initialize an instance of a PQ or ZIP load in the power grid.

        Args:
            Bus (int): the bus where the load is located
            P (float): the active power of a constant power (PQ) load.
            Q (float): the reactive power of a constant power (PQ) load.
            IP (float): the active power component of a constant current load.
            IQ (float): the reactive power component of a constant current load.
            ZP (float): the active power component of a constant admittance load.
            ZQ (float): the reactive power component of a constant admittance load.
            area (int): location where the load is assigned to.
            status (bool): indicates if the load is in-service or out-of-service.
        """
        self.id = Loads._ids.__next__()
        self.bus = Bus 
        self.p = P/100
        self.q = Q/100
        self.area = area
        self.status = status

    def pq_derivative(self, PreviousSolution):
        real_V = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vr"]]
        imag_V = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vi"]]
        real_I_by_real_V = ((self.p*(imag_V**2 - real_V**2) - 2 * self.q * real_V * imag_V) /
                            (real_V**2 + imag_V**2)**2)
        real_I_by_imag_V = ((self.q*(real_V**2 - imag_V**2) - 2 * self.p * real_V * imag_V) /
                            (real_V**2 + imag_V**2)**2)
        imag_I_by_real_V = real_I_by_imag_V
        imag_I_by_imag_V = -real_I_by_real_V
        return real_I_by_real_V, real_I_by_imag_V, imag_I_by_real_V, imag_I_by_imag_V

    def pq_history(self, PreviousSolution, IR_by_VR, IR_by_VI, II_by_VR, II_by_VI):
        real_V = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vr"]]
        imag_V = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vi"]]
        real_I = (self.p * real_V + self.q * imag_V) / (real_V**2 + imag_V**2)
        imag_I = (self.p * imag_V - self.q * real_V) / (real_V**2 + imag_V**2)
        j_real_stamp = - (real_I - IR_by_VR * real_V - IR_by_VI * imag_V)
        j_imag_stamp = - (imag_I - II_by_VR * real_V - II_by_VI * imag_V)
        return j_real_stamp, j_imag_stamp

    def optimize_derivative(self, PreviousSolution):
        LR = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_r"]]
        LI = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_i"]]
        VR = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vr"]]
        VI = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vi"]]
        real_A_by_real_V = ((2*VR*(LR*self.p - LI*self.q)*(VR**2 - 3*VI**2) -
                            2*VI*(LR*self.q + LI*self.p)*(VI**2 - 3*VR**2)) /
                            (VR**2 + VI**2)**3)
        real_A_by_imag_V = ((2*VI*(self.q*LI - self.p*LR)*(VI**2 - 3*VR**2) -
                            2*VR*(self.q*LR + self.p*LI)*(VR**2 - 3*VI**2)) /
                            (VR**2 + VI**2)**3)
        imag_A_by_real_V = ((-2*VR*(LR*self.q + LI*self.p)*(VR**2 - 3*VI**2) +
                            2*VI*(LI*self.q - LR*self.p)*(VI**2 - 3*VR**2)) /
                            (VR**2 + VI**2)**3)
        imag_A_by_imag_V = ((2*VI*(self.p*LI + self.q*LR)*(VI**2 - 3*VR**2) +
                            2*VR*(self.q*LI - self.p*LR)*(VR**2 - 3*VI**2)) /
                            (VR**2 + VI**2)**3)
        return real_A_by_real_V, real_A_by_imag_V, imag_A_by_real_V, imag_A_by_imag_V

    def optimize_history(self, PreviousSolution, IR_by_VR, IR_by_VI, II_by_VR, II_by_VI,
                        AR_by_VR, AR_by_VI, AI_by_VR, AI_by_VI):
        LR = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_r"]]
        LI = PreviousSolution[Buses.bus_key_[str(self.bus) + "_lambda_i"]]
        VR = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vr"]]
        VI = PreviousSolution[Buses.bus_key_[str(self.bus) + "_vi"]]
        real_A = LR*IR_by_VR + LI*II_by_VR
        imag_A = LR*IR_by_VI + LI*II_by_VI
        j_real_stamp = - (real_A - AR_by_VR * VR - AR_by_VI * VI - IR_by_VR * LR - II_by_VR * LI)
        j_imag_stamp = - (imag_A - AI_by_VR * VR - AI_by_VI * VI - IR_by_VI * LR - II_by_VI * LI)
        return j_real_stamp, j_imag_stamp