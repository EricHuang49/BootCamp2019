/* ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
 * param.hpp
 * 
 * This file declares the parameters of the problem. It 
 * declares the preference parameters, the state space, the 
 * level of discretization, and the number of iterations. 
 * It also declares parameters useful for 
 * formatting the output files of the program.
 * 
 * Simon Scheidegger -- 06/17.
 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*/ 

#ifndef param_hpp
#define param_hpp

#define EIGEN_DONT_PARALLELIZE // Disables Eigen's OpenMP application to matrix operations
#include <stdio.h>
#include "../eigen/Eigen/Dense"

using namespace Eigen;

// Preference Parameters
extern double alpha;
extern double gamm;
extern double beta;

// Capital Stock Interval

// Minimum and Maximum Capital Stock
extern double kmin;
extern double kmax;

// Choose nk, the number of capital stocks, and kappa, the discretization level
extern int nk;
extern double kappa;


// Create Vector of Productivity States
extern int ntheta;
extern double theta_min;
extern double theta_step;

// grids
extern ArrayXd kgrid;
extern ArrayXd thetagrid;

// Number of Iterations
extern int numstart;    // Iterations begin at this timestep
extern int Numits;      // Iterations end at this timestep

// Maximum error
extern double errmax;

// Number of Columns for output
extern int nout;

// Frequency with which data will be printed
extern int datafreq;

// Hybrid Switch ( 0 for Comm Splitting; 1 to use regular hybrid)
extern int hybrid_switch;

#endif /* param_hpp */
