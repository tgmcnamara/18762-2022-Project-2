import numpy as np

def initialize(size, bus):
    v = np.zeros(size)
    for ele in bus:
        v[ele.node_Vr] += ele.Vm_init*np.cos(2*np.pi*ele.Va_init)
        v[ele.node_Vi] += ele.Vm_init*np.sin(2*np.pi*ele.Va_init)
    return v
