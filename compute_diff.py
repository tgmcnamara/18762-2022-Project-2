import numpy as np

mpower = np.loadtxt("mat_out.txt")
mval = np.copy(mpower[:, 1:3])
lpower = np.loadtxt("powerflow.txt")
lval = np.copy(lpower[:, 1:3])

diff = np.absolute(mval - lval)
avg = np.sum(diff, axis=0) / diff.shape[0]

print("AVERAGE MAGNITUDE ERROR: ", avg[0])
print("AVERAGE PHASE ERROR: ", avg[1])
