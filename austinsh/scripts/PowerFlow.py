
import numpy as np
from models.Buses import Buses
from models.Generators import Generators
from models.Loads import Loads
from scipy import sparse
from scipy.sparse.linalg import spsolve

class PowerFlow:

    def __init__(self,
                 case_name,
                 tol,
                 max_iters,
                 enable_limiting):
        """Initialize the PowerFlow instance.

        Args:
            case_name (str): A string with the path to the test case.
            tol (float): The chosen NR tolerance.
            max_iters (int): The maximum number of NR iterations.
            enable_limiting (bool): A flag that indicates if we use voltage limiting or not in our solver.
        """
        # Clean up the case name string
        case_name = case_name.replace('.RAW', '')
        case_name = case_name.replace('testcases/', '')

        self.case_name = case_name
        self.tol = tol
        self.max_iters = max_iters
        self.enable_limiting = enable_limiting

    def solve(self, y_matrix, j_matrix):
        v = spsolve(y_matrix, j_matrix)
        return v

    def apply_limiting(self):
        pass

    def check_error(self, difference):
        """Returns the number of variables outside their accepted tolerance."""
        if_error = difference > self.tol
        if_error = if_error.astype(int)
        num_of_error = int(np.sum(if_error))
        return num_of_error

    # # # Stamp Linear Power Grid Elements into Y matrix # # #
    #  This function should call the stamp_linear function of each linear element and return an updated Y matrix.

    def stamp_linear(self, branches, slack, size):
        i_linear = []
        j_linear = []
        linear_value = []
        j_row = []
        j_column = []
        j_value = []
        for ele in branches:
            vr_i = Buses.bus_key_[str(ele.from_bus) + "_vr"]
            vi_i = Buses.bus_key_[str(ele.from_bus) + "_vi"]
            vr_j = Buses.bus_key_[str(ele.to_bus) + "_vr"]
            vi_j = Buses.bus_key_[str(ele.to_bus) + "_vi"]
            y_stamps = [
                [vr_i, vr_i, ele.conductance], [vr_i, vr_j, -ele.conductance], [vr_j, vr_j, ele.conductance],
                [vr_j, vr_i, -ele.conductance], 
                [vi_i, vi_i, ele.conductance], [vi_i, vi_j, -ele.conductance], [vi_j, vi_j, ele.conductance],
                [vi_j, vi_i, -ele.conductance],
                [vr_i, vi_i, ele.se_coeff], [vr_i, vi_j, -ele.se_coeff], [vr_j, vi_j, ele.se_coeff],
                [vr_j, vi_i, -ele.se_coeff], 
                [vi_i, vr_i, -ele.se_coeff], [vi_i, vr_j, ele.se_coeff], [vi_j, vr_j, -ele.se_coeff],
                [vi_j, vr_i, ele.se_coeff],
                [vr_i, vi_i, ele.sh_coeff], [vr_j, vi_j, ele.sh_coeff], [vi_i, vr_i, -ele.sh_coeff],
                [vi_j, vr_j, -ele.sh_coeff]
            ]
            for indicies in y_stamps:
                i, j, value = indicies
                i_linear.append(i)
                j_linear.append(j)
                linear_value.append(value)
        for elem in slack:
            vr = Buses.bus_key_[str(elem.bus) + "_vr"]
            vi = Buses.bus_key_[str(elem.bus) + "_vi"]
            ir = elem.node_Ir_Slack
            ii = elem.node_Ii_Slack
            y_stamps = [
                [ir, vr, 1], [ii, vi, 1],
                [vr, ir, 1], [vi, ii, 1]
            ]
            j_stamps = [
                [ir, 0, elem.vrset],
                [ii, 0, elem.viset]
            ]
            for indicies in y_stamps:
                i, j, value = indicies
                i_linear.append(i)
                j_linear.append(j)
                linear_value.append(value)
            for indicies in j_stamps:
                i, j, value = indicies
                j_row.append(i)
                j_column.append(j)
                j_value.append(value)
        y_matrix = sparse.coo_matrix((linear_value, (i_linear, j_linear)), shape = (size, size)).tocsr()
        j_vector = sparse.coo_matrix((j_value, (j_row, j_column)), shape = (size, 1)).tocsr()
        return y_matrix, j_vector

    def stamp_nonlinear(self, generators, loads, pre_sol):
        i_nonlinear = []
        j_nonlinear = []
        nonlinear_value = []
        j_row = []
        j_column = []
        j_value = []
        for ele in generators:
            vr = Buses.bus_key_[str(ele.bus) + "_vr"]
            vi = Buses.bus_key_[str(ele.bus) + "_vi"]
            q = Buses.bus_key_[str(ele.bus) + "_q"]
            IR_by_Q, IR_by_VR, IR_by_VI, II_by_Q, II_by_VR, II_by_VI, VR_by_Q, VI_by_Q = \
                Generators.pv_derivative(ele, pre_sol)
            y_stamps = [
                [vr, vr, IR_by_VR], [vr, vi, IR_by_VI], [vr, q, IR_by_Q],
                [vi, vi, II_by_VI], [vi, vr, II_by_VR], [vi, q, II_by_Q],
                [q, vr, VR_by_Q], [q, vi, VI_by_Q]
            ]
            j_VR, j_VI, j_Q = Generators.pv_history(
                ele, pre_sol, IR_by_Q, IR_by_VR, IR_by_VI, II_by_Q, II_by_VR, II_by_VI
                )
            j_stamps = [
                [vr, 0, j_VR], 
                [vi, 0, j_VI], 
                [q, 0, j_Q]
            ]
            for indicies in y_stamps:
                i, j, value = indicies
                i_nonlinear.append(i)
                j_nonlinear.append(j)
                nonlinear_value.append(value)
            for index in j_stamps:
                i, j, value = index
                j_row.append(i)
                j_column.append(j)
                j_value.append(value)
        for elem in loads:
            vr = Buses.bus_key_[str(elem.bus) + "_vr"]
            vi = Buses.bus_key_[str(elem.bus) + "_vi"]
            IR_by_VR, IR_by_VI, II_by_VR, II_by_VI = Loads.pq_derivative(elem, pre_sol)
            y_stamps = [
                [vr, vr, IR_by_VR], [vr, vi, IR_by_VI],
                [vi, vr, II_by_VR], [vi, vi, II_by_VI]
            ]
            j_VR, j_VI = Loads.pq_history(
                elem, pre_sol, IR_by_VR, IR_by_VI, II_by_VR, II_by_VI
                )
            j_stamps = [
                [vr, 0, j_VR],
                [vi, 0, j_VI]
            ]
            for indicies in y_stamps:
                i, j, value = indicies
                i_nonlinear.append(i)
                j_nonlinear.append(j)
                nonlinear_value.append(value)
            for index in j_stamps:
                i, j, value = index
                j_row.append(i)
                j_column.append(j)
                j_value.append(value)
        size = len(pre_sol)
        y_matrix = sparse.coo_matrix((nonlinear_value, (i_nonlinear, j_nonlinear)), shape = (size,size)).tocsr()
        j_vector = sparse.coo_matrix((j_value, (j_row, j_column)), shape = (size, 1)).tocsr()
        return y_matrix, j_vector

    def run_powerflow(self,
                      v_init,
                      bus,
                      slack,
                      generator,
                      transformer,
                      branch,
                      shunt,
                      load):
        """Runs a positive sequence power flow using the Equivalent Circuit Formulation.

        Args:
            v_init (np.array): The initial solution vector which has the same number of rows as the Y matrix.
            bus (list): Contains all the buses in the network as instances of the Buses class.
            slack (list): Contains all the slack generators in the network as instances of the Slack class.
            generator (list): Contains all the generators in the network as instances of the Generators class.
            transformer (list): Contains all the transformers in the network as instance of the Transformers class.
            branch (list): Contains all the branches in the network as instances of the Branches class.
            shunt (list): Contains all the shunts in the network as instances of the Shunts class.
            load (list): Contains all the loads in the network as instances of the Load class.

        Returns:
            v(np.array): The final solution vector.

        """

        # # # Copy v_init into the Solution Vectors used during NR, v, and the final solution vector v_sol # # #
        v = np.copy(v_init)
        v_sol = np.copy(v)

        # # # Initialize While Loop (NR) Variables # # #

        err_measure = 1  # maximum error at the current NR iteration
        tol = self.tol  # chosen NR tolerance
        NR_count = 0  # current NR iteration

        # # # Begin Solving Via NR # # #
        # TODO: PART 1, STEP 2.3 - Complete the NR While Loop
        while err_measure > tol:

            # # # Stamp Nonlinear Power Grid Elements into Y matrix # # #
            # TODO: PART 1, STEP 2.4 - Complete the stamp_nonlinear function which stamps all nonlinear power grid
            #  elements. This function should call the stamp_nonlinear function of each nonlinear element and return
            #  an updated Y matrix. You need to decide the input arguments and return values.

            state_variables = len(v)
            y_n_sparse, j_n_sparse = self.stamp_nonlinear(generator, load, v)
            y_l_sparse, j_l_sparse = self.stamp_linear(branch, slack, state_variables)

            y_matrix = y_n_sparse + y_l_sparse
            j_vector = j_n_sparse + j_l_sparse

            # # # Solve The System # # #
            # TODO: PART 1, STEP 2.5 - Complete the solve function which solves system of equations Yv = J. The
            #  function should return a new v_sol.
            #  You need to decide the input arguments and return values.
            v_new = self.solve(y_matrix, j_vector)

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 1, STEP 2.6 - Finish the check_error function which calculates the maximum error, err_max
            #  You need to decide the input arguments and return values.

            iteration_difference = abs(v_new - v)
            err_measure = self.check_error(iteration_difference)
            v = v_new

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 2, STEP 1 - Develop the apply_limiting function which implements voltage and reactive power
            #  limiting. Also, complete the else condition. Do not complete this step until you've finished Part 1.
            #  You need to decide the input arguments and return values.
            if self.enable_limiting and err_measure > tol:
                self.apply_limiting()
        print(v)
        return v
