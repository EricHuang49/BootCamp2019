#======================================================================
#
#     This routine interfaces with the TASMANIAN Sparse grid
#     The crucial part is 
#
#     aVals[iI]=solver.initial(aPoints[iI], n_agents)[0]  
#     => at every gridpoint, we solve an optimization problem
#
#     Simon Scheidegger, 11/16 ; 07/17
#======================================================================

import TasmanianSG
import numpy as np
import nonlinear_solver_initial as solver

#======================================================================

def sparse_grid(paramL): ###n_agents, iDepth
    
    grid  = TasmanianSG.TasmanianSparseGrid()

    k_range=np.array([paramL['k_bar'], paramL['k_up']])

    ranges=np.empty((paramL['n_agents'], 2))


    for i in range(paramL['n_agents']):
        ranges[i]=k_range

    iDim = paramL['n_agents']

    grid.makeLocalPolynomialGrid(iDim, paramL['iOut'], paramL['iDepth'], paramL['which_basis'], "localp")
    grid.setDomainTransform(ranges)

    aPoints=grid.getPoints()
    iNumP1=aPoints.shape[0]
    aVals=np.empty([iNumP1, 1])
    
    file=open("comparison0.txt", 'w')
    for iI in range(iNumP1):
        aVals[iI]=solver.initial(aPoints[iI], paramL)[0]
        v=aVals[iI]*np.ones((1,1))
        to_print=np.hstack((aPoints[iI].reshape(1,paramL['n_agents']), v))
        np.savetxt(file, to_print, fmt='%2.16f')
        
    file.close()
    grid.loadNeededPoints(aVals)
    
    f=open("grid.txt", 'w')
    np.savetxt(f, aPoints, fmt='% 2.16f')
    f.close()
    
    return grid
