#======================================================================
#
#     This routine solves an infinite horizon growth model 
#     with dynamic programming and sparse grids
#
#     The model is described in Scheidegger & Bilionis (2017)
#     https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2927400
#
#     external libraries needed:
#     - IPOPT (https://projects.coin-or.org/Ipopt)
#     - PYIPOPT (https://github.com/xuy/pyipopt)
#     - TASMANIAN (http://tasmanian.ornl.gov/)
#
#     Simon Scheidegger, 11/16 ; 07/17
#======================================================================

import nonlinear_solver_initial as solver     #solves opt. problems for terminal VF
import nonlinear_solver_iterate as solviter   #solves opt. problems during VFI
### from parameters import *                      #parameters of model
import interpolation as interpol              #interface to sparse grid library/terminal VF
import interpolation_iter as interpol_iter    #interface to sparse grid library/iteration
import postprocessing as post                 #computes the L2 and Linfinity error of the model

import TasmanianSG                            #sparse grid library
import numpy as np
#=====================================================================
##### Parameters #####

paramL = dict()
# Depth of "Classical" Sparse grid
paramL['iDepth']=1
paramL['iOut']=1         # how many outputs
paramL['which_basis'] = 1 #linear basis function (2: quadratic local basis)

# control of iterations
paramL['numstart'] = 0   # which is iteration to start (numstart = 0: start from scratch, number=/0: restart)
paramL['numits'] = 10    # which is the iteration to end

# How many random points for computing the errors
paramL['No_samples'] = 1000

### Model Paramters
paramL['n_agents']=2  # number of continuous dimensions of the model

paramL['beta']=0.8
paramL['rho']=0.95
paramL['zeta']=0.5
paramL['psi']=0.36
paramL['gamma']=2.0
paramL['delta']=0.025
paramL['eta']=1
paramL['big_A']=(1.0-paramL['beta'])/(paramL['psi']*paramL['beta'])

# Ranges For States
paramL['range_cube']=5 # range of [0..1]^d in 1D
paramL['k_bar']=0.2
paramL['k_up']=3.0

# Ranges for Controls
paramL['c_bar']=1e-2
paramL['c_up']=10000.0

paramL['l_bar']=1e-2
paramL['l_up']=1.0

paramL['inv_bar']=1e-2
paramL['inv_up']=10000.0

# Stochastic
paramL['theta_list'] = [0.90, 0.95, 1.00, 1.05, 1.10]
paramL['curr_theta'] = 1.00

#======================================================================
# terminal value function
valList = []
if (paramL['numstart']==0):
    for state in range(5):
        valnew=TasmanianSG.TasmanianSparseGrid()
        valnew=interpol.sparse_grid(paramL)
        valList.append(valnew)
        valnew.write("valnew_1." + str(paramL['numstart']) + ".txt") #write file to disk for restart

# value function during iteration
else:
    valnew.read("valnew_1." + str(paramL['numstart']) + ".txt")  #write file to disk for restart

valListold = []
for state in range(5):
    valold=TasmanianSG.TasmanianSparseGrid()
    valold=valList[state]
    valListold.append(valold)

for i in range(paramL['numstart'], paramL['numits']):
    for state in range(5):
        paramL['curr_theta'] = paramL['theta_list'][state]
        valnew=TasmanianSG.TasmanianSparseGrid()
        valnew=interpol_iter.sparse_grid_iter(paramL, valListold[state])
        valList[state] = valnew
    for state in range(5):
        valold=TasmanianSG.TasmanianSparseGrid()
        valold=valList[state]
        valListold[state] = valold
    
#======================================================================
print( "===============================================================")
print( " " )
print( " Computation of a growth model of dimension ", paramL['n_agents'] ," finished after ", paramL['numits'], " steps")
print( " " )
print( "===============================================================")
#======================================================================

# compute errors   
avg_err=post.ls_error(paramL)

#======================================================================
print( "===============================================================")
print( " ")
print( " Errors are computed -- see errors.txt")
print( " ")
print( "===============================================================")
#======================================================================
