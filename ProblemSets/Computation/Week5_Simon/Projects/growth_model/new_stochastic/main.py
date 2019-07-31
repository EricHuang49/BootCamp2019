import os
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
import pickle


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

with open('parameters.pickle', 'rb') as handle:
    paramL = pickle.load(handle)


if (size != 5):
    print("This algorithm isn't set up to take more or less than 5 processes")

def get_iteration_list(iteration):
    # Gets all the sparse grids from the iteration specified.
    output = []
    for shock in range(5):
        v=TasmanianSG.TasmanianSparseGrid()
        v.read("valnew_1." + str(iteration) +'.s{}'.format(shock)+ ".txt")
        output.append(v)
    
    return output

def main():
    start_time = time.clock()
    
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
if (size != 5):
    print("This algorithm isn't set up to take more or less than 5 processes. OUTPUT WILL BE WRONG.")

