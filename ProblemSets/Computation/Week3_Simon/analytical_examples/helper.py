import TasmanianSG
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
from IPython.display import HTML
import math
from numpy.random import uniform
from datetime import datetime
import numpy as np

## Oscillatory
def f_1(x, w, c):
    return np.cos(2*np.pi*w[0]+np.dot(x, c))

## Product Peak
def f_2(x, w, c):
    output_vector = (c**(-2) +(x - w)**2)**(-1)
    return np.prod(output_vector)

## Corner Peak
def f_3(x, w, c):
    d = x.shape[0]
    return (1+np.dot(x, c))**(-d-1)

## Gaussian
def f_4(x, w, c, t=1):
    return np.exp(t*(c**2 * (x - w)**2).sum())

## Continous
def f_5(x, w, c):
    return np.exp(-(c*np.abs(x-w)).sum())

## Discontinuous
def f_6(x, w, c):
    if x[0] > w[0] or x[1] > w[1]:
        return 0
    else:
        return np.exp(np.dot(c, x))
    
    
def main(function, d, function_name = 'Not given', refinement_level = 5):
    print('\n ----------------')
    print("TasmanianSG version: {0:s}".format(TasmanianSG.__version__))
    print("TasmanianSG license: {0:s}".format(TasmanianSG.__license__))
    
    output0 = dict()
    output1 = dict()
    
    grid  = TasmanianSG.TasmanianSparseGrid()
    grid1 = TasmanianSG.TasmanianSparseGrid()
    grid2 = TasmanianSG.TasmanianSparseGrid()

    #############################################################################

    # EXAMPLE 1 for OSM:
    # interpolate: f(x,y) = cos(0.5 * pi * x) * cos(0.5 * pi * y)
    # using piecewise linear basis functions.

    # 1000 3-dimensional sample points 
    w = uniform(0.01, 10, d)
    c = uniform(-5.0, 5.0, d)
    
    aPnts = np.empty([1000, d])  
    for iI in range(1000):
        aPnts[iI][:] = uniform(-1.0, 1.0, d)
    
    # Result
    aTres = np.empty([1000,])
    
    for iI in range(1000):
        aTres[iI] = function(aPnts[iI][:], w, c)

    # Sparse Grid with dimension 2 and 1 output and refinement level 5
    iDim = d
    iOut = 1
    iDepth = 3
    which_basis = 1 #1= linear basis functions -> Check the manual for other options

    print("Using fixed sparse grid with depth {0:1d}".format(iDepth))
    
    # construct sparse grid
    grid.makeLocalPolynomialGrid(iDim, iOut, iDepth, which_basis, "localp")
    aPoints = grid.getPoints()
    iNumP1 = aPoints.shape[0]
    aVals = np.empty([aPoints.shape[0], 1])
    for iI in range(aPoints.shape[0]):
        aVals[iI] = function(aPoints[iI][:],w,c)
    grid.loadNeededPoints(aVals)

    # compute the error
    aRes = grid.evaluateBatch(aPnts)
    fError1 = max(np.fabs(aRes[:,0] - aTres))

    output0['aPoints'] = aPoints.copy()
    output0['iNumP1'] = iNumP1
    output0['fError1'] = fError1

    aTres = np.empty([1000,])
    
    for iI in range(1000):
        aTres[iI] = function(aPnts[iI][:], w, c)
        
    # Adaptive Sparse Grid with dimension d and 1 output and maximum refinement level 5, refinement criterion.
    iDim = d
    iOut = 1
    iDepth = 1
    fTol = 1.E-5
    which_basis = 1 
    # level of grid before refinement
    grid1.makeLocalPolynomialGrid(iDim, iOut, iDepth, which_basis, "localp")

    aPoints = grid1.getPoints()
    aVals = np.empty([aPoints.shape[0], 1])
    for iI in range(aPoints.shape[0]):
        aVals[iI] = function(aPnts[iI][:], w, c)
    grid1.loadNeededPoints(aVals)

    print("Classic refinement ")

    #refinement level
    for iK in range(refinement_level):
        grid1.setSurplusRefinement(fTol, -1, "fds")   #also use fds, or other rules
        aPoints = grid1.getNeededPoints()
        aVals = np.empty([aPoints.shape[0], 1])
        for iI in range(aPoints.shape[0]):
            aVals[iI] = function(aPoints[iI][:], w, c)
        
        grid1.loadNeededPoints(aVals)

        aRes = grid1.evaluateBatch(aPnts)
        fError1 = max(np.fabs(aRes[:,0] - aTres))
        
        output1[iK+1] = {'aPoints':aPoints, 'iNumP1':grid1.getNumPoints(), 'fError1':fError1, 'aVals':aVals}

    print('\n ----------------')
    return output0, output1


def draw_plots(data):
    refinement = []
    error = []
    num_p = []
    for i in list(data[1].keys()):
        refinement.append(i)
        error.append(data[1][i]['fError1'])
        num_p.append(data[1][i]['iNumP1'])
        
    fig, ax = plt.subplots(1, 3, figsize=(10,5))
    ax[0].scatter(refinement, error)
    ax[0].axhline(y=data[0]['fError1'], color='r', linestyle='-')
    ax[0].set_xlabel('Refinement')
    ax[0].set_ylabel('Error')
    
    ax[1].scatter(refinement, num_p)
    ax[1].axhline(y=data[0]['iNumP1'], color='r', linestyle='-')
    ax[1].set_xlabel('Refinement')
    ax[1].set_ylabel('Number of points')
    
    ax[2].scatter(num_p, error)
    ax[2].set_xlabel('Number of points')
    ax[2].set_ylabel('Error')
    
    return fig, ax


def draw_3d(data, z_axis=[0,1]):
    fig = plt.figure()
    ax = Axes3D(fig)
    axes = [-1, 1, -1, 1]
    ax.axis(axes)
    ax.set_zlim(z_axis[0], z_axis[1])
    print('fig size: {0} DPI, size in inches {1}'.format(
        fig.get_dpi(), fig.get_size_inches()))

    ax.scatter([],[],[])

    def update(i):
        label = 'refinement {0}'.format(i+1)
        ax.scatter(data[1][i+1]['aPoints'][:,0], data[1][i+1]['aPoints'][:,1],data[1][i+1]['aVals'][:,0],color='blue')
        ax.set_title(label)

    anim = FuncAnimation(fig, update, frames=np.arange(0, 10), interval=1000)
    return anim
    
