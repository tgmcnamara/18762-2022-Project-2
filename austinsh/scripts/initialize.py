import numpy as np
from models.Buses import Buses

def initialize(Initial_state, buses, generators, slacks, loads):
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
    return Initial_state