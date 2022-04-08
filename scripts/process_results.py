from models.Buses import Buses
import numpy as np
import math
import matplotlib.pyplot


def process_results(v,bus):
    print("Bus voltage:\n#        Mag(pu)        Ang(deg)")
    for b in bus:
        vr_node = Buses.bus_map[b.Bus].node_Vr
        vi_node = Buses.bus_map[b.Bus].node_Vi
        x,y = [v[vr_node], v[vi_node]]
        mag = np.round(x**2 + y**2,5)
        ang = np.round(math.degrees(math.atan2(y,x)),5)
        print("{}".format(b.Bus) +"        {:.5f}    {:.5f}".format(mag,ang))
        
        
        
        