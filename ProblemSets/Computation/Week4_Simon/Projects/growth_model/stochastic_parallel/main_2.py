import os
os.environ["Method"] = "stochastic"
import nonlinear_solver_initial as solver     #solves opt. problems for terminal VF
import nonlinear_solver_iterate as solviter   #solves opt. problems during VFI
import interpolation as interpol              #interface to sparse grid library/terminal VF
import interpolation_iter as interpol_iter    #interface to sparse grid library/iteration
import postprocessing as post
import TasmanianSG                            #sparse grid library
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from IPython.display import HTML
from mpi4py import MPI
from mpi4py.MPI import ANY_SOURCE
import time

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


paramL = dict()
# Depth of "Classical" Sparse grid
paramL['size'] = size
paramL['rank'] = rank
paramL['comm'] = comm
paramL['iDepth']=1
paramL['iOut']=1         # how many outputs
paramL['which_basis'] = 1 #linear basis function (2: quadratic local basis)

# control of iterations
paramL['numstart'] = 0   # which is iteration to start (numstart = 0: start from scratch, number=/0: restart)
paramL['numits'] = 5    # which is the iteration to end

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
paramL['theta_list'] = [0.9, 0.95, 1.00, 1.05, 1.10]
paramL['curr_theta'] = 1.00

if (size == 5):
    print("This algorithm isn't set up to take more or less than 5 processes")

def get_iteration_list(iteration):
    output = []
    for shock in range(5):
        v=TasmanianSG.TasmanianSparseGrid()
        v.read("valnew_1." + str(iteration) +'.s{}'.format(shock)+ ".txt")
        output.append(v)
    
    return output

def main():
    start_time = time.clock()
    print('Size: ', size, ' rank ', rank)
    paramL['curr_theta'] = paramL['theta_list'][rank]
    valnew=TasmanianSG.TasmanianSparseGrid()
    valnew=interpol.sparse_grid(paramL)
    valold = TasmanianSG.TasmanianSparseGrid()
    valold = valnew
    valnew.write("valnew_1." + str(paramL['numstart']) +".s{}".format(rank)+ ".txt") #write file to disk for restart
    
    comm.barrier()

    for i in range(paramL['numstart']+1, paramL['numits']+1):
        print('Size: ', size, ' rank ', rank)
        paramL['curr_theta'] = paramL['theta_list'][rank]
        valnew=TasmanianSG.TasmanianSparseGrid()
        output = get_iteration_list(i-1)
        valnew=interpol_iter.sparse_grid_iter(paramL, list(output))
        valold = TasmanianSG.TasmanianSparseGrid()
        valold = valnew
        valnew.write("valnew_1."+str(i)+".s{}".format(rank)+".txt")
        comm.barrier()


    end_time = time.clock() - start_time
    print('END')
    if rank == 0:
        avg_err=post.ls_error(paramL)
        print(end_time)
    


main()
