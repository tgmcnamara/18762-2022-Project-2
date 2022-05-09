import numpy as np
from models.Buses import Buses

def initialize(Initial_state, buses, generators, slacks, loads, transformers, optimization):
        for ele in generators:
                vr = Buses.bus_key_[str(ele.bus) + "_vr"]
                vi = Buses.bus_key_[str(ele.bus) + "_vi"]
                q = Buses.bus_key_[str(ele.bus) + "_q"]
                bus = ele.bus
                Initial_state[vr] = buses[bus - 1].init_Vr
                Initial_state[vi] = buses[bus - 1].init_Vi
                Initial_state[q] = ele.q
        for elem in slacks:
                vr = Buses.bus_key_[str(elem.bus) + "_vr"]
                vi = Buses.bus_key_[str(elem.bus) + "_vi"]
                ir = elem.node_Ir_Slack
                ii = elem.node_Ii_Slack
                bus = elem.bus
                Initial_state[vr] = buses[bus - 1].init_Vr
                Initial_state[vi] = buses[bus - 1].init_Vi
                Initial_state[ir] = elem.ir_init
                Initial_state[ii] = elem.ii_init
        for elem in loads:
                vr = Buses.bus_key_[str(elem.bus) + "_vr"]
                vi = Buses.bus_key_[str(elem.bus) + "_vi"]
                bus = elem.bus
                Initial_state[vr] = buses[bus - 1].init_Vr
                Initial_state[vi] = buses[bus - 1].init_Vi
        if optimization:
                for elem in buses:
                        lr = elem.node_lambda_r
                        li = elem.node_lambda_i
                        Initial_state[lr] = 10**-4
                        Initial_state[li] = 10**-4
                        if elem.Type == 2:
                                lq = elem.node_lambda_q
                                Initial_state[lq] = 10**-4
                for elem in slacks:
                        lr = elem.node_lambdar_ir
                        li = elem.node_lambdai_ii
                        Initial_state[lr] = 10**-4
                        Initial_state[li] = 10**-4
                for elem in transformers:
                        lr_ir = elem.node_LR_IR
                        li_ii = elem.node_LI_II
                        lr_2 = elem.node_LR_2
                        li_2 = elem.node_LI_2
                        Initial_state[lr_ir] = 10**-4
                        Initial_state[li_ii] = 10**-4
                        Initial_state[lr_2] = 10**-4
                        Initial_state[li_2] = 10**-4
        return Initial_state