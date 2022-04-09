import numpy as np

def process_results(v,buses):
    for ele in buses:
        bus = ele.Bus
        vr = v[ele.node_Vr]
        vi = v[ele.node_Vi]
        mag = np.sqrt(vr*vr + vi*vi)
        ang = 360*np.arctan2(vi, vr)/(2*np.pi)

        print(f'Mag at Bus{bus} is {mag:.3f}')
        print(f'Ang at Bus{bus} is {ang:.3f}')

        if(ele.Type == 2):
            q = v[ele.node_Q]*100
            print(f'Q at Bus{bus} is {q:.3f}')
