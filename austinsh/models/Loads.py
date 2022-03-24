from __future__ import division
from itertools import count

from numpy import array_equal


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

    def pq_derivative(PreviousSolution, load):
        
        pass
        # real_V = PreviousSolution[]
        # imag_V = PreviousSolution[]
        # real_I_by_real_V = ((load.p*(imag_V**2 - real_V**2) - 2 * load.q * real_V * imag_V) /
        #                     (real_V**2 + imag_V**2)**2)
        # real_I_by_imag_V = ((load.q*(real_V**2 - imag_V**2) - 2 * load.p * real_V * imag_V) /
        #                     (real_V**2 + imag_V**2)**2)
        # imag_I_by_real_V = real_I_by_imag_V
        # imag_I_by_imag_V = -real_I_by_real_V
        # return real_I_by_real_V, real_I_by_imag_V, imag_I_by_real_V, imag_I_by_imag_V

    # def pq_history(PreviousSolution, IR_by_VR, IR_by_VI, II_by_VR, II_by_VI):
    #     real_I = PreviousSolution[]
    #     imag_I = PreviousSolution[]
    #     real_V = PreviousSolution[]
    #     imag_V = PreviousSolution[]
    #     j_real_stamp = real_I - IR_by_VR * real_V - IR_by_VI * imag_V
    #     j_imag_stamp = imag_I - II_by_VR * real_V - II_by_VI * imag_V
    #     return j_real_stamp, j_imag_stamp