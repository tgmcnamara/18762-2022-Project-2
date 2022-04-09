import numpy as np
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import spsolve


class PowerFlow:

    def __init__(self,
                 case_name,
                 tol,
                 max_iters,
                 enable_limiting,
                 data,
                 size):
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
        self.data = data
        self.size = size

    def solve(self, Y, J):
        dense = True
        if dense:
            Yd = Y.todense()
            return np.linalg.solve(Yd, J)
        return spsolve(Y,J)

    def apply_limiting(self, buses, gens):
        Q = 0
        for bus in buses:
            if bus.Type == 3:
                Q = v[bus.node_Q]
            for gen in gens:
                if bus.Bus == gen.Bus:
                    if Q < gen.Qmin:
                        v[bus.node_Q] = gen.Qmin
                    if Q > gen.Qmax:
                        v[bus.node_Q] = gen.Qmax

    def check_error(self, vsol, vprev):
        err = vsol - vprev
        return (np.absolute(err)).max()

    def stamp_linear(self, J, bus, slack, branch, shunt, transf):
        Y = csc_matrix((self.size,self.size))
        for ele in bus:
            buslin = ele.lin_stamp_control(J, self.size,slack,shunt)
            Y += buslin
        for ele in branch:
            brchlin = ele.stamp_lin(self.size,bus)
            Y += brchlin
        for ele in transf:
            trlin = ele.stmp_lin(self.size,bus)
            Y += trlin

        return Y

    def stamp_nonlinear(self, Y, J, vp, bus, gen, load):
        for ele in bus:
            Y += ele.nl_stmp_cntrl(J, vp, gen, load, self.size)
        return Y


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

        J = np.zeros(self.size)

        # # # Stamp Linear Power Grid Elements into Y matrix # # #
        # TODO: PART 1, STEP 2.1 - Complete the stamp_linear function which stamps all linear power grid elements.
        #  This function should call the stamp_linear function of each linear element and return an updated Y matrix.
        #  You need to decide the input arguments and return values.
        Y = self.stamp_linear(J, bus, slack, branch, shunt, transformer)
        #print(Y)
        #print(J)

        # # # Initialize While Loop (NR) Variables # # #
        # TODO: PART 1, STEP 2.2 - Initialize the NR variables
        err_max = 2*self.tol  # maximum error at the current NR iteration
        tol = self.tol  # chosen NR tolerance
        NR_count = 0  # current NR iteration

        # # # Begin Solving Via NR # # #
        # TODO: PART 1, STEP 2.3 - Complete the NR While Loop
        while (err_max > tol) and (NR_count < self.max_iters):
            #print(NR_count)
            Ynl = Y.copy()
            Jnl = np.copy(J)
            vprev = np.copy(v_sol)

            # # # Stamp Nonlinear Power Grid Elements into Y matrix # # #
            # TODO: PART 1, STEP 2.4 - Complete the stamp_nonlinear function which stamps all nonlinear power grid
            #  elements. This function should call the stamp_nonlinear function of each nonlinear element and return
            #  an updated Y matrix. You need to decide the input arguments and return values.
            Ynl = self.stamp_nonlinear(Ynl, Jnl, vprev, bus, generator, load)
            #if(NR_count == 0):
                #print(Ynl-Y)
                #print(Jnl)

            # # # Solve The System # # #
            # TODO: PART 1, STEP 2.5 - Complete the solve function which solves system of equations Yv = J. The
            #  function should return a new v_sol.
            #  You need to decide the input arguments and return values.
            v_sol = self.solve(Ynl,Jnl)

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 1, STEP 2.6 - Finish the check_error function which calculates the maximum error, err_max
            #  You need to decide the input arguments and return values.
            err_max = self.check_error(v_sol,vprev)

            # # # Compute The Error at the current NR iteration # # #
            # TODO: PART 2, STEP 1 - Develop the apply_limiting function which implements voltage and reactive power
            #  limiting. Also, complete the else condition. Do not complete this step until you've finished Part 1.
            #  You need to decide the input arguments and return values.
            if self.enable_limiting and err_max > tol:
                self.apply_limiting(bus, generator)
            else:
                pass
            NR_count += 1

        print(f'Number of iterations: {NR_count}')

        return v_sol
