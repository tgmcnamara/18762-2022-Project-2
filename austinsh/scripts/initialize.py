import numpy as np

def initialize(Initial_state, buses, generators, slacks):
       
    bus_counter = 0
    count_pq_and_slack = 0
    count_pv = 0
    count_slack_pq = -2

    for ele in range(len(Initial_state)):
        if bus_counter < len(buses):
            bus_type = buses[bus_counter].Type
            if bus_type == 1 or bus_type == 3:
                count_pq_and_slack += 1
                if count_pq_and_slack % 2 == 0:
                    Initial_state[ele - 1] = buses[bus_counter].init_Vr
                    Initial_state[ele] = buses[bus_counter].init_Vi
                    bus_counter += 1
            elif bus_type == 2:
                count_pv += 1
                if count_pv % 3 == 0:
                    Initial_state[ele - 2] = buses[bus_counter].init_Vr
                    Initial_state[ele - 1] = buses[bus_counter].init_Vi
                    for i in range(len(generators)):
                        # Doesn't deal with multiple slacks...need to think about this more
                        if generators[i].bus == bus_counter + 1:
                            qinit = generators[i].q
                    Initial_state[ele] = qinit
                    bus_counter += 1
        if bus_counter == len(buses):
            count_slack_pq += 1
            if count_slack_pq % 2 == 0:
                Initial_state[ele - 1] = slacks[count_slack_pq -2].pinit
                Initial_state[ele] = slacks[count_slack_pq -2].qinit
            if count_slack_pq == -1:
                count_slack_pq = 0
    return Initial_state