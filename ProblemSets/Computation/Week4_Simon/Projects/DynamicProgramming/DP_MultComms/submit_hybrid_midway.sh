#!/bin/bash
# a sample job submission script to submit a hybrid MPI/OpenMP job to the sandyb 
# partition on Midway1 please change the --partition option if you want to use 
# another partition on Midway1

#SBATCH --time=01:00:00

# set the job name to hello-hybrid
#SBATCH --job-name=hybrid_run

# send output to hello-hybrid.out
#SBATCH --output=Vanilla_hybrid_36000_simple.out

# this job requests 5 MPI processes
#SBATCH --ntasks=1


# and request 16 cpus per task for OpenMP threads
#SBATCH --cpus-per-task=28

# this job will run in the sandyb partition on Midway1
#SBATCH --partition=broadwl

# load the openmpi default module
module load openmpi

# set OMP_NUM_THREADS to the number of --cpus-per-task we asked for
make
export OMP_NUM_THREADS=1

# Run the process with mpirun. Notice -n is not required. mpirun will
# automatically figure out how many processes to run from the slurm options
mpirun ./VFI


