from models.Buses import Buses
import numpy as np
import math
import matplotlib.pyplot


def process_results(v,bus):
    angs = np.zeros((1,0))
    mags = np.zeros((1,0))
    bus_size = 0
    
    print("Bus voltage:\n#        Mag(pu)        Ang(deg)")
    for b in bus:
        bus_size += 1
        vr_node = Buses.bus_map[b.Bus].node_Vr
        vi_node = Buses.bus_map[b.Bus].node_Vi
        x,y = [v[vr_node], v[vi_node]]
        mag = np.round(x**2 + y**2,5)
        ang = np.round(math.degrees(math.atan2(y,x)),5)
        
        angs = np.append(angs,ang)
        mags = np.append(mags,mag)
        print("{}".format(b.Bus) +"        {:.5f}    {:.5f}".format(mag,ang))
        
        
    if (bus_size == 4):
        gt_mags = np.array([1,0.982,0.969,1.020])
        gt_angs = np.array([0,-0.976,-1.872,1.523])
    elif (bus_size == 14):
        gt_mags = np.array([1.06,1.045,1.01,1.018,1.02,1.07,1.062,1.09,1.056,1.051,1.057,1.055,
                            1.05,1.036])
        gt_angs = np.array([0,-4.983,-12.725,-10.313,-8.774,-14.221,-13.360,-13.360,-14.939,
                            -15.097,-14.791,-15.076,-15.156,-16.034])
    
    print("mags:",mags,"gt mags:",gt_mags)    
    mag_diff = np.average( ((mags - gt_mags) / gt_mags) * 100)
    ang_diff = np.average( ((angs - gt_angs) / 360) * 100)
    
    print("Bus magnitude (%) difference: {}".format(mag_diff))     
    print("Bus angle (%) difference: {}".format(ang_diff))   
        