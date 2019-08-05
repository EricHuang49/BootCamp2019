#!/bin/bash
# `a sample job submission script to submit a hybrid MPI/OpenMP job to the broadwl
# partition on Midway please change the --partition option if you want to use 
# another partition on Midway

# set the job name to hello-hybrid
#SBATCH --job-name=hello-hybrid

# send output to hello-hybrid.out
#SBATCH --output=8_threads_hybrid.out

# this job requests 4 MPI processes
#SBATCH --ntasks=8


# and request 8 cpus per task for OpenMP threads
#SBATCH --cpus-per-task=16

# this job will run in the broadwl partition on Midway
#SBATCH --partition=broadwl

# load the openmpi default module
make
module load openmpi

# set OMP_NUM_THREADS to the number of --cpus-per-task we asked for
export OMP_NUM_THREADS=8

# Run the process with mpirun. Notice -n is not required. mpirun will
# automatically figure out how many processes to run from the slurm options
for i in 1 2 4 8
do
   mpirun -np $i ./BS.exec
done
