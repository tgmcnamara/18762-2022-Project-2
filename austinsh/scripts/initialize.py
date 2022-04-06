import numpy as np

def initialize(Initial_state, buses, generators, slacks):
    # Initializing all of the necesary counters.
    bus_counter = 0
    count_pq_and_slack = 0
    count_pv = 0
    count_slack_pq = -2
    slack_number = 0

    for ele in range(len(Initial_state)):
        if bus_counter < len(buses):
            # Get the current bus type whether it is slack, pq, or pv
            bus_type = buses[bus_counter].Type
            # Initializing the values for slack buses and pq buses because
            # they have similar relationships in accordance to state variables.
            if bus_type == 1 or bus_type == 3:
                # Increment our counter
                count_pq_and_slack += 1
                if bus_type == 3:
                    slack_number += 1
                # Only if the counter is equal to the number of state variables will
                # this loop initialize
                if count_pq_and_slack % 2 == 0:
                    # Stamp the real voltage at the bus first followed by the
                    # imaginary voltage.
                    Initial_state[ele - 1] = buses[bus_counter].init_Vr
                    Initial_state[ele] = buses[bus_counter].init_Vi
                    # This bus is complete, time to increment to the next bus type.
                    bus_counter += 1
            # Initializing state variables for pv buses using the given data.
            elif bus_type == 2:
                # Increment the pv counter by 1.
                count_pv += 1
                # Once the pv counter is equal to the number of state variables for
                # pv buses, this loop will initialize.
                if count_pv % 3 == 0:
                    # Get the initial values for the generator that we are dealing with
                    # beginning with the real voltage followed by the imaginary voltage
                    Initial_state[ele - 2] = buses[bus_counter].init_Vr
                    Initial_state[ele - 1] = buses[bus_counter].init_Vi
                    # Get the initial reactive power for the current bus we are working with
                    for i in range(len(generators)):
                        if generators[i].bus == bus_counter + 1:
                            qinit = generators[i].q
                    # Adding the initial value for the reactive power of the generator
                    Initial_state[ele] = qinit
                    # Increment the bus counter
                    bus_counter += 1
        # At this point, all of the regular state variable will have been introduced but
        # the equivalent circuit for a slack bus is an independent voltage source. Thus,
        # we need to introduce the current state variables for the slack bus in order
        # to utilize modified nodal analysis methods.
        if bus_counter == len(buses):
            # Increment the slack bus counter
            count_slack_pq += 1
            # Once the counter is equal to the number of additional state variables, this
            # loop will initialize to add their initial values to the vector
            if count_slack_pq % 2 == 0:
                # Adding the initial real current for the slack bus followed by the
                # imaginary current to our vector of state variables.
                Initial_state[ele - 1] = slacks[int(count_slack_pq/2 - 1)].ir_init
                Initial_state[ele] = slacks[int(count_slack_pq/2 - 1)].ii_init
                # Needed to make the counter work out properly.
            if count_slack_pq == -1:
                count_slack_pq = 0
    return Initial_state