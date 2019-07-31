#======================================================================
#
#     This routine interfaces with the TASMANIAN Sparse grid
#     The crucial part is 
#
#     aVals[iI]=solveriter.iterate(aPoints[iI], n_agents)[0]  
#     => at every gridpoint, we solve an optimization problem
#
#     Simon Scheidegger, 11/16 ; 07/17
#======================================================================

import TasmanianSG
import numpy as np
import nonlinear_solver_iterate as solveriter

#======================================================================

def sparse_grid_iter(paramL, valold_list):
    n_agents = paramL['n_agents']
    
    grid  = TasmanianSG.TasmanianSparseGrid()

    k_range=np.array([paramL['k_bar'], paramL['k_up']])

    ranges=np.empty((n_agents, 2))


    for i in range(n_agents):
        ranges[i]=k_range

    iDim=n_agents
    iOut=1

    grid.makeLocalPolynomialGrid(iDim, iOut, paramL['iDepth'], paramL['which_basis'], "localp")
    grid.setDomainTransform(ranges)

    aPoints=grid.getPoints()
    iNumP1=aPoints.shape[0]
    aVals=np.empty([iNumP1, 1]) ## Change to 5d
    
    file=open("comparison1.txt", 'w')
    for iI in range(iNumP1):
        aVals[iI]= solveriter.iterate(aPoints[iI], paramL, valold_list)[0]
        v=aVals[iI]*np.ones((1,1))
        to_print=np.hstack((aPoints[iI].reshape(1,n_agents), v))
        np.savetxt(file, to_print, fmt='%2.16f')
        
    file.close()
    grid.loadNeededPoints(aVals)
    
    f=open("grid_iter.txt", 'w')
    np.savetxt(f, aPoints, fmt='% 2.16f')
    f.close()
    
    return grid

#======================================================================

def sparse_grid_iter_adap(paramL, valold_list):
    ## Not working
    n_agents = paramL['n_agents']
    
    grid  = TasmanianSG.TasmanianSparseGrid()

    k_range=np.array([paramL['k_bar'], paramL['k_up']])

    ranges=np.empty((n_agents, 2))


    for i in range(n_agents):
        ranges[i]=k_range

    iDim=n_agents
    iOut=1
    fTol = 1.E-5

    grid.makeLocalPolynomialGrid(iDim, iOut, paramL['iDepth'], paramL['which_basis'], "localp")
    grid.setDomainTransform(ranges)

    aPoints=grid.getPoints()
    iNumP1=aPoints.shape[0]
    aVals=np.empty([iNumP1, 1]) ## Change to 5d
    
    for iK in range(3):
        grid.setSurplusRefinement(fTol, -1, "fds")   #also use fds, or other rules
        aPoints = grid1.getNeededPoints()
        aVals = np.empty([aPoints.shape[0], 1])
        for iI in range(aPoints.shape[0]):
            aVals[iI]= solveriter.iterate(aPoints[iI], paramL, valold_list)[0]
            v=aVals[iI]*np.ones((1,1))
            
        grid.loadNeededPoints(aVals)

    
    f=open("grid_iter.txt", 'w')
    np.savetxt(f, aPoints, fmt='% 2.16f')
    f.close()
    
    return grid

