from scripts.Solve import solve

# path to the grid network RAW file

# casename = 'testcases/GS-4_prior_solution.RAW'
# casename = 'testcases/IEEE-14_prior_solution.RAW'
# casename = 'testcases/IEEE-118_prior_solution.RAW'
# casename = 'testcases/ACTIVSg500_prior_solution.RAW'
# casename = 'testcases/PEGASE-9241_flat_start.RAW'
# casename = 'testcases/GS-4_stressed.RAW'
casename = 'testcases/IEEE-14_stressed_1.RAW'
# casename = 'testcases/IEEE-14_stressed_2.RAW'

# the settings for the solver
settings = {
    "Tolerance": 1E-07,
    "Max Iters": 1000,
    "Limiting":  False,
    "Optimization": True
}

# run the solver
solve(casename, settings)