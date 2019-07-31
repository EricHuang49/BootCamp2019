/* ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ 
 * solver.cpp
 * 
 * This defines the ValIt function, which takes the Old Value 
 * Function Guess and performs one Value function iteration.
 * 
 *  The function creates a communicator for each theta state if the number of MPI processes 
 * is greater or equal than the number of said states; otherwise, the function only uses MPI_COMM_WORLD. We can also 
 * use the hybrid switch defined in params.cpp to manually deactivate the Comm Splitting. 
 * 
 * Each communicator splits the nk states among the MPI processes within it and collects the results in the rank 0 
 * process of that communicator. We do this for each theta if we have a single communicator; otherwise, each 
 * communicator does this for a single theta. If we do have a communicator for each theta state, we create one 
 * last communicator that contains those mpi processes with rank 0 within their respective communicators so that we 
 * can gather all of their results in the process with world rank 0 (that is, rank 0 within the MPI_Comm_World 
 * Communicator).
 * 
 * Simon Scheidegger -- 06/17.
 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++*/ 

#include <iostream>
#include <stdio.h>
#include "param.hpp"
#include "econ.hpp"
#include "omp.h"
#include <mpi.h>

using namespace Eigen;


// Value Function Iteration

// The following funtion defines the routine for one iteration of value function iteration, and produces the new
// value function. This is the Bellman equation

// In this problem, the control (knext here) is discrete, so maximization reduces to computing a list of
// values implied by all possible choices, and taking the max.

MatrixXd ValIt(MatrixXd ValOld=MatrixXd::Zero(nk, ntheta)) {
    
    // Create Index Variable for Storing the location (index) of the optimal policy choice
    MatrixXd::Index maxIndex;
    
    
    // The following array will contain the consumption choices implied by each policy
    ArrayXd c(nk);
    
    // Temp will contain the list of values implied by each policy choice
    ArrayXd temp(nk);
    
    // Processes' ID's inside MPI_COMM_WORLD and the size of said Communicator
    int world_rank;
    int world_size;
    
    // Obtain number of proccesses and their id's within Comm World
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &world_size);
    
    /* Determine the number of communicators we will be using. If the number of MPI processes is less than the
     number of theta states, or if the user has manually deactivated the Comm Splitting, we will only use one
     Communicator. Otherwise, we will use split MPI_Comm_World into ntheta communicators. Each communicator
     will determine de the new values corresponding to a particular theta state.
     */
    
    int num_comms=( (world_size/ntheta == 0) || (hybrid_switch==1) ) ? 1: ntheta;
    
    // Create Matrices for storing the New Value Functions and the Policy Functions.
    // Only process with world rank 0 will have the full nk x ntheta matrices.
    
    /* We now create and initialize ValNew, which will store the new value function guess after the iteration. 
     * We initially set ValNew equal to the Old Value Function Guess. 
     * Only world rank 0 needs to store the New Value Function. 
     * Thus, all other processes define ValNew to be a 1x1 matrix of zeros in order to save space in memory.
     */

    MatrixXd ValNew=(world_rank==0) ? ValOld: MatrixXd::Zero(1,1);
    
    
    /* Declare and Initialize the Policy Function to a Matrix of Zeros. Only the process with rank 0 inside
     MPI_Comm_World needs to store the complete (nk x ntheta) matrix. Thus, all other processes define
     Policy to be a 1x1 matrix of zeros in order to save space in memory.
     */
    
    MatrixXd Policy=(world_rank==0) ? MatrixXd::Zero(nk, ntheta): MatrixXd::Zero(1,1);

    // The following defines the value function iteration if we are only using the MPI_COMM_WORLD
    // communicator
    
    
    if (num_comms==1) {
        
        /* We now proceed to split the number of capital states among the MPI Processes within MPI_Comm_World.
         Each process will compute the new values and optimal policies corresponding to those capital states.
         
         We try to divide those capital states among the processes as evenly as posisble. If the number of
         capital states is not divisible by the number of mpi processes, the first r processes get
         an extra capital stock each, where r is the remainder after dividing nk by world_size.
         
         */
        
        // Determine approximately how many capital states are assigned to each process.
        int nump=nk/world_size;
        
        // Obtain the remainder from the previous division
        int r=nk % world_size;
        
        /*
         
         Assuming that we have a zero remainder, the idea is to have process 0 work on the first
         nump capital states, process 1 on the next nump capital states, and so on. If we have a 
         nonzero remainder r, we will give each of the first r processes an extra capital state.
         
         The following variable indicates where each process' kgrid segment starts.
         
         */
        
        int my_start;
        
        
        /* The following determines how many capital states each mpi process will work on. It also
         determines the value for my_start.
         */
        
        if (world_rank<r) {
            nump+=1;
            my_start=world_rank*nump;
        }
        
        // We now determine the starting indices of the processes that were not assigned
        // a remainder.
        
        else {
            my_start=r + world_rank*nump;
        }

        
        /* Create the kgrid containing the k's for which the process will compute the
         new values and policies
         */
        
        ArrayXd my_kgrid=kgrid.segment(my_start, nump); // Segment of nump capital stocks starting at kgrid(my_start)
        
        // Each process will store the new values and policies corresponding to their states in the
        // following buffers. These will be then sent to the world rank 0 process.
        
        ArrayXd val_sendbuff=ArrayXd::Zero(nump);
        ArrayXd pol_sendbuff=ArrayXd::Zero(nump);
        
        /* Receive Buffers. Process with world rank 0 will gather the results sent by the other processes in the
         following buffers, which will then be assigned to the New Value function and Policy matrices.
         Only world rank 0 process needs to store the complete nk array */
        
        
        ArrayXd val_recvbuff= (world_rank==0) ? ArrayXd::Zero(nk) : ArrayXd::Zero(1);
        ArrayXd pol_recvbuff= (world_rank==0) ? ArrayXd::Zero(nk) : ArrayXd::Zero(1);
        
        
        // Create "Displacement Array" for MPI_Gatherv: Indicates where each process will start saving their
        // respective data in the receive buffer.
        
        int displs[world_size];
        
        
        // Create array that indicates how many elements we are going to receive from each process
        
        int recvcounts[world_size];
        
        
        /* The first r processes will each send 1+ nk/size elements to each of the receive buffers, 
	 * since they each were assigned an extra capital stock. Thus, their starting points must be spaced out accordingly.
         */
        
        for (int i=0; i<r; i++) {
            displs[i]=i*(1+nk/world_size);
            recvcounts[i]=1+nk/world_size;
        }
        
        // The remaining procceses only store nk/size elements. Their starting points are spaced out
        // accordingly as well.
        for (int j=r; j<world_size; j++) {
            displs[j]=r + j*nk/world_size;
            recvcounts[j]=nk/world_size;
        }
        
        
        /*
         The following is the economics part of the program. For each state (theta, k), we compute the new value and policy 
         functions. Since the problem is discrete, the problem reduces to computing the values associated with each policy 
         choice and choosing the one that yields the highest value. These policies and new values will then be part of our new 
         value and policy function guesses.
         
         The following makes use of MPI and OpenMP. Since we only have one communicator, we parallelize over the capital states.
         */
        
        // The outer loop is over the theta states
        for (int itheta=0; itheta<ntheta; itheta++) {

// OpenMP is initialized and the threads are created within each MPI process.
#pragma omp parallel private(maxIndex, c, temp)
            {
// We distribute the for loop among the process' threads
#pragma omp for
                /*
                 
                 Given the theta state, we now determine the new values and optimal policies corresponding to each 
                 capital state.
                 
                 */
                for (int ik=0; ik<nump; ik++) {
                    
                    // Compute the consumption quantities implied by each policy choice
                    c=f(my_kgrid(ik), thetagrid(itheta))-kgrid;
                    
                    // Compute the list of values implied implied by each policy choice
                    temp=util(c) + beta*ValOld*p(thetagrid(itheta));
                    
                    /* Take the max of temp and store its location. 
                     The max is the new value corresponding to (ik, itheta).
                     The location corresponds to the index of the optimal policy choice in kgrid.
                     
                     We store the new value and the corresponding policy information in the send buffers declared earlier
                     
                    */
                    
                    val_sendbuff(ik)=temp.maxCoeff(&maxIndex);
                    pol_sendbuff(ik)=kgrid(maxIndex);
                }
                
            }
            
            
            /* Given the theta state, World Rank 0 gathers the new values and policies computed by all processes and
             stores them in the receive buffers declared earlier.
             */
            
            MPI_Gatherv(val_sendbuff.data(), nump, MPI_DOUBLE, val_recvbuff.data(), recvcounts, displs, MPI_DOUBLE, 0, MPI_COMM_WORLD);
            
            MPI_Gatherv(pol_sendbuff.data(), nump, MPI_DOUBLE, pol_recvbuff.data(), recvcounts, displs, MPI_DOUBLE, 0, MPI_COMM_WORLD);
            
            /* Now that we have obtained the new values and policies for all nk states for a given theta, we update
             the Value and policy matrices in the world rank 0 process. That is, we assign the receive buffers to the 
             corresponding columns in the Value and Policy function matrices.
             */
            if (world_rank==0) {
                ValNew.col(itheta)=val_recvbuff;
                Policy.col(itheta)=pol_recvbuff;
            }
            
        }

    }
    
    
    /* The following defines Value Function iteration if we have Split the MPI_Comm_World into ntheta communicators: one
     for each theta state. Each of these communicators will encompass a group of MPI processes that will compute the 
     optimal values and policies of every capital state, but only for a particular theta. That is, each communicator will
     work on a particular column of the value and policy function matrices.
     */
    
    else {
        
        
        
        // Create the Communicators. Each communicator will correspond to a particular theta state.
        MPI_Comm theta_comm;
        
        /* Color for Splitting World Communicator. All of the processes with the same value for color will be set
         in the same communicator. We use the remainder so we can distribute the processes as evenly as possible among
         the communicators.
         */
        
        
        int color= world_rank % num_comms;
        
        // The color variable will also be used to determine the index of the theta state each communicator will
        // be woriking on. The processes encompassed by theta_comm will be assigned thetagrid(color).
        
        int itheta=color;   //itheta is used to emphasize its role as an index for thetagrid
        
        // We split the processes in the MPI_Comm_World Communicator into ntheta communicators
        // using the color variable as previously described.
        
        MPI_Comm_split(MPI_COMM_WORLD, color, world_rank, &theta_comm);
        
        // We now obtain the ranks and sizes of each theta_comm and store them.
        int theta_rank, theta_size;
        
        MPI_Comm_rank(theta_comm, &theta_rank);
        MPI_Comm_size(theta_comm, &theta_size);
        
        
        // Communicator for gathering
        MPI_Comm gather_comm;
        
        
        // Those with rank 0 in theta_comm will be in one communicator and the rest in another
        int gather_color= (theta_rank==0) ? 0: 1;
        
        MPI_Comm_split(MPI_COMM_WORLD, gather_color, world_rank, &gather_comm);
        
        int gather_rank, gather_size;
        
        MPI_Comm_rank(gather_comm, &gather_rank);
        MPI_Comm_size(gather_comm, &gather_size);
        
        /* For each theta_comm we distribute the capital states among the MPI Processes in the communicator.
         Each process will compute the new values and optimal policies corresponding to the capital states
         that were assigned to it. We try to divide the capital states among those processes as evenly as posisble.
         If the number of capital states is not divisible by the number of mpi processes within the communicator, 
         the first r processes of that theta_comm get an extra capital stock each, where r is the remainder after 
         dividing nk by theta_size.
         */

        // Determine approximately how many states are computed per processor
        int nump=nk/theta_size;
        
        // Obtain the remainder from the previous division
        int r=nk % theta_size;
        
        /* The following variable will be used to give each process a segment of the original kgrid.
         Assuming that we have a zero remainder, the idea is to have process 0 work on the first
         nump capital states, process 1 on the next nump capital states, and so on. If we have a
         nonzero remainder r, we will give each of the first r processes an extra capital state.
         
         The following variable indicates where each process' kgrid segment starts.
         
         */
        
        
        int my_start;
        
        
        /* The following determines how many capital states each mpi process within theta_comm will work on. 
         It also determines the value for my_start for each process.
         */
        
        if (theta_rank<r) {
            nump+=1;
            my_start=theta_rank*nump;
        }
        
        // We now determine the starting indices of the processes that were not assigned
        // a remainder.
        
        else {
            my_start=r + theta_rank*nump;
        }

        // We now determine the starting indices of the processes that were not assigned
        // a remainder.
        
        
        // Create the grid containing the k's the process will work on
        
        ArrayXd my_kgrid=kgrid.segment(my_start, nump);
        
        
        // Each process will store the new values and policies corresponding to their states in the
        // following buffers. These will then be sent to the process with rank 0 within theta_comm.

        ArrayXd val_sendbuff=ArrayXd::Zero(nump);
        ArrayXd pol_sendbuff=ArrayXd::Zero(nump);
        
        
        /* Receive Buffers. Process with theta rank 0 will gather the results sent by the other processes within
        theta_comm in the following buffers. The processes with theta_rank 0 will then send their respective arrays to the
         process with world rank 0, which will then store them in the ValNew and Policy matrices.
         */

        ArrayXd val_recvbuff(nk);
        ArrayXd pol_recvbuff(nk);


        
        
        
        /* The first r processes in theta_comm will each send 1+ nk/theta_size elements to each of the receive buffers in
         theta_rank 0, since they each were assigned an extra capital stock. Thus, their starting points must be spaced out accordingly.
         */
        
        /* The remaining procceses within theta_comm only send nk/theta_size elements to theta_rank 0. Their starting points
         are spaced out accordingly as well.
         */
        
        
        // Create "Displacement Array" for MPI_Gatherv: Indicates where each process will start saving their
        // respective data in the receive buffer.
        
        int displs[theta_size];
        
        // Create array that indicates how many elements theta_rank 0 is going to receive from each process in theta_comm.
        
        int recvcounts[theta_size];
        
        for (int i=0; i<r; i++) {
            displs[i]=i*(1+nk/theta_size);
            recvcounts[i]=1+nk/theta_size;
        }
        
        for (int j=r; j<theta_size; j++) {
            displs[j]=r + j*nk/theta_size;
            recvcounts[j]=nk/theta_size;
        }
        
        /*
         The following is the economics part of the program. For each state (theta, k), we compute the new value and policy
         functions. Since the problem is discrete, the problem reduces to computing the values associated with each policy
         choice and choosing the one that yields the highest value. These policies and new values will then be part of our new
         value and policy function guesses.
         
         Since we have split the communicator, each theta_comm will compute the new values and policies for a single
         theta. The nk states will be distributed among the processes within theta_comm and each process will then compute the
         values and policies of the capital states that were assigned to them. Each communicator then gathers the data
         corresponding to the theta assigned to it on the process with theta rank 0. Finally, we use MPI communicator
         gather_comm to group all processes with theta_rank 0 in order to gather their results and store
         them in the ValNew and Policy matrices located in the process with world rank 0.
         */

        
// OpenMP is initialized and the threads are created within each MPI process.
#pragma omp parallel private(maxIndex, c, temp)
        {
// We distribute the for loop among the process' threads
#pragma omp for
            /*
             
            We now determine the new values and optimal policies corresponding to each
             capital state.
             
             */

            for (int ik=0; ik<nump; ik++) {
                
                // Compute the consumption quantities implied by each policy choice
                c=f(my_kgrid(ik), thetagrid(itheta))-kgrid;
                
                // Compute the list of values implied implied by each policy choice
                temp=util(c) + beta*ValOld*p(thetagrid(itheta));
                
                /* Take the max of temp and store its location.
                 The max is the new value corresponding to kgrid(ik), thetagrid(itheta).
                 The location corresponds to the index of the optimal policy choice in kgrid.
                 
                 We store the new value and the corresponding policy information in the send buffers declared earlier
                 */
                
                val_sendbuff(ik)=temp.maxCoeff(&maxIndex);
                pol_sendbuff(ik)=kgrid(maxIndex);
            }
            
        }
    
        
        /* Within theta_comm, theta_rank 0 gathers the new values and policies computed by the processes inside
         the communicator and stores them in the receive buffers declared earlier.
         */
     MPI_Gatherv(val_sendbuff.data(), nump, MPI_DOUBLE, val_recvbuff.data(), recvcounts, displs, MPI_DOUBLE, 0, theta_comm);
        
     MPI_Gatherv(pol_sendbuff.data(), nump, MPI_DOUBLE, pol_recvbuff.data(), recvcounts, displs, MPI_DOUBLE, 0, theta_comm);
    
        /* All the processes with theta rank 0 across the communicators group together and send their results to the
         world rank 0 process, which then stores the values and policies in the ValNew and Policy matrices, respectively.
         */
        if (theta_rank==0) {
            MPI_Gather(val_recvbuff.data(), nk, MPI_DOUBLE, ValNew.data(), nk, MPI_DOUBLE, 0, gather_comm);
        }
    
     }
    

    // World Rank 0 Process concatenates ValNew and Policy into a single (2nk x theta_ntheta) matrix and returns it

    if (world_rank==0) {
        MatrixXd result(2*nk, ntheta);
        
        result<< ValNew, Policy;
        
        return result;
    }
    
    // All other processes just return ValNew, which is just a 1x1 Zero matrix outside of world rank 0.
    
    else {
        return ValNew;
    }
    
}
