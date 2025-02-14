#=======================================================================
#
#     ipopt_wrapper.py : an interface to IPOPT and PYIPOPT 
#
#     Simon Scheidegger, 06/17
#
#=======================================================================

##from parameters import *
from econ import *
import numpy as np

#=======================================================================
#   Objective Function to start VFI (in our case, the value function)
        
def EV_F(X, k_init, paramL):
    n_agents = paramL['n_agents']
    delta = paramL['delta']
    beta = paramL['beta']
    
    # Extract Variables
    cons=X[0:n_agents]
    lab=X[n_agents:2*n_agents]
    inv=X[2*n_agents:3*n_agents]
    
    knext= (1-delta)*k_init + inv
    # Compute Value Function
    
    VT_sum=utility(paramL, cons, lab) + beta*V_INFINITY(paramL, knext)

    return VT_sum

# V infinity
def V_INFINITY(paramL, k=[]):
    beta = paramL['beta']
    
    e=np.ones(len(k))
    c=output_f(paramL, k,e)
    v_infinity=utility(paramL,c,e)/(1-beta)
    return v_infinity

#=======================================================================
#   Objective Function during VFI (note - we need to interpolate on an "old" sprase grid)
    
def EV_F_ITER(X, k_init, paramL, grid_list): 
    n_agents = paramL['n_agents']
    beta = paramL['beta']
    delta = paramL['delta']
    
    # Extract Variables
    cons=X[0:n_agents]
    lab=X[n_agents:2*n_agents]
    inv=X[2*n_agents:3*n_agents]
    knext= (1-delta)*k_init + inv
    
    # Compute Value Function
    e0 = grid_list[0].evaluate(knext)
    e1 = grid_list[1].evaluate(knext)
    e2 = grid_list[2].evaluate(knext)
    e3 = grid_list[3].evaluate(knext)
    e4 = grid_list[4].evaluate(knext)
    
    
    expectation = 1/5.*(e0+e1+e2+e3+e4)
        
    utility_temp = utility(paramL, cons, lab)
    
    VT_sum = utility_temp + beta*expectation
    
    return VT_sum[0]
    
#=======================================================================
#   Computation of gradient (first order finite difference) of initial objective function 

def EV_GRAD_F(X, k_init, paramL):

    N=len(X)
    GRAD=np.zeros(N, float) # Initial Gradient of Objective Function
    h=1e-4
    
    
    for ixN in range(N):
        xAdj=np.copy(X)
        
        if (xAdj[ixN] - h >= 0):
            xAdj[ixN]=X[ixN] + h            
            fx2=EV_F(xAdj, k_init, paramL)
            
            xAdj[ixN]=X[ixN] - h
            fx1=EV_F(xAdj, k_init, paramL)
            
            GRAD[ixN]=(fx2-fx1)/(2.0*h)
            
        else:
            xAdj[ixN]=X[ixN] + h
            fx2=EV_F(xAdj, k_init, paramL)
            
            xAdj[ixN]=X[ixN]
            fx1=EV_F(xAdj, k_init, paramL)
            GRAD[ixN]=(fx2-fx1)/h
            
    return GRAD
    
#=======================================================================
#   Computation of gradient (first order finite difference) of the objective function 
    
def EV_GRAD_F_ITER(X, k_init, paramL, grid_list):
    
    N=len(X)
    GRAD=np.zeros(N, float) # Initial Gradient of Objective Function
    h=1e-4
    
    
    for ixN in range(N):
        xAdj=np.copy(X)
        
        if (xAdj[ixN] - h >= 0):
            xAdj[ixN]=X[ixN] + h            
            fx2=EV_F_ITER(xAdj, k_init, paramL, grid_list)
            
            xAdj[ixN]=X[ixN] - h
            fx1=EV_F_ITER(xAdj, k_init, paramL, grid_list)
            
            GRAD[ixN]=(fx2-fx1)/(2.0*h)
            
        else:
            xAdj[ixN]=X[ixN] + h
            fx2=EV_F_ITER(xAdj, k_init, paramL, grid_list)
            
            xAdj[ixN]=X[ixN]
            fx1=EV_F_ITER(xAdj, k_init, paramL, grid_list)
            GRAD[ixN]=(fx2-fx1)/h
            
    return GRAD
       
#======================================================================
#   Equality constraints for the first time step of the model
            
def EV_G(X, k_init, paramL):
    n_agents = paramL['n_agents']
    delta = paramL['delta']
    zeta = paramL['zeta']
    
    N=len(X)
    M=3*n_agents+1  # number of constraints
    G=np.empty(M, float)
    
    # Extract Variables
    cons=X[:n_agents]
    lab=X[n_agents:2*n_agents]
    inv=X[2*n_agents:3*n_agents]
    
    
    # first n_agents equality constraints
    for i in range(n_agents):
        G[i]=cons[i]
        G[i + n_agents]=lab[i]
        G[i+2*n_agents]=inv[i]
    
    
    f_prod=output_f(paramL, k_init, lab)
    Gamma_adjust=0.5*zeta*k_init*((inv/k_init - delta)**2.0)
    sectors_sum=cons + inv - delta*k_init - (f_prod - Gamma_adjust)
    G[3*n_agents]=np.sum(sectors_sum)
    
    return G
    
#======================================================================
#   Equality constraints during the VFI of the model

def EV_G_ITER(X, k_init, paramL):
    n_agents = paramL['n_agents']
    delta = paramL['delta']
    zeta = paramL['zeta']    
    
    N=len(X)
    M=3*n_agents+1  # number of constraints
    G=np.empty(M, float)
    
    # Extract Variables
    cons=X[:n_agents]
    lab=X[n_agents:2*n_agents]
    inv=X[2*n_agents:3*n_agents]
    
    
    # first n_agents equality constraints
    for i in range(n_agents):
        G[i]=cons[i]
        G[i + n_agents]=lab[i]
        G[i+2*n_agents]=inv[i]
    
    
    f_prod=output_f(paramL, k_init, lab)
    
    Gamma_adjust=0.5*zeta*k_init*((inv/k_init - delta)**2.0)
    sectors_sum=cons + inv - delta*k_init - (f_prod - Gamma_adjust)
    G[3*n_agents]=np.sum(sectors_sum)
    
    return G

#======================================================================
#   Computation (finite difference) of Jacobian of equality constraints 
#   for first time step
    
def EV_JAC_G(X, flag, k_init, paramL):
    n_agents = paramL['n_agents']

    N=len(X)
    M=3*n_agents+1
    NZ=M*N
    A=np.empty(NZ, float)
    ACON=np.empty(NZ, int)
    AVAR=np.empty(NZ, int)    
    
    # Jacobian matrix structure
    
    if (flag):
        for ixM in range(M):
            for ixN in range(N):
                ACON[ixN + (ixM)*N]=ixM
                AVAR[ixN + (ixM)*N]=ixN
                
        return (ACON, AVAR)
        
    else:
        # Finite Differences
        h=1e-4
        gx1=EV_G(X, k_init, paramL)
        
        for ixM in range(M):
            for ixN in range(N):
                xAdj=np.copy(X)
                xAdj[ixN]=xAdj[ixN]+h
                gx2=EV_G(xAdj, k_init, paramL)
                A[ixN + ixM*N]=(gx2[ixM] - gx1[ixM])/h
        return A

#   Computation (finite difference) of Jacobian of equality constraints 
#   during iteration  
  
def EV_JAC_G_ITER(X, flag, k_init, paramL):
    n_agents = paramL['n_agents']
    
    N=len(X)
    M=3*n_agents+1
    NZ=M*N
    A=np.empty(NZ, float)
    ACON=np.empty(NZ, int)
    AVAR=np.empty(NZ, int)    
    
    # Jacobian matrix structure
    
    if (flag):
        for ixM in range(M):
            for ixN in range(N):
                ACON[ixN + (ixM)*N]=ixM
                AVAR[ixN + (ixM)*N]=ixN
                
        return (ACON, AVAR)
        
    else:
        # Finite Differences
        h=1e-4
        gx1=EV_G_ITER(X, k_init, paramL)
        
        for ixM in range(M):
            for ixN in range(N):
                xAdj=np.copy(X)
                xAdj[ixN]=xAdj[ixN]+h
                gx2=EV_G_ITER(xAdj, k_init, paramL)
                A[ixN + ixM*N]=(gx2[ixM] - gx1[ixM])/h
        return A    
    
#======================================================================

    
    
    
    
    
    
    
    
    
            
            
            
    
    
    
    
    
    
