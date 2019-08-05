#!/bin/bash
# a sample job submission script to submit a hybrid MPI/OpenMP job to the sandyb 
# partition on Midway1 please change the --partition option if you want to use 
# another partition on Midway1

#SBATCH --time=02:00:00

# set the job name to hello-hybrid
#SBATCH --job-name=hello-hybrid

# send output to hello-hybrid_4.out
#SBATCH --output=100000_test.out

# this job requests 8 MPI processes
#SBATCH --ntasks=14


# and request 16 cpus per task for OpenMP threads
#SBATCH --cpus-per-task=16

# this job will run in the sandyb partition on Midway1
#SBATCH --partition=broadwl

# load the openmpi default module
module load openmpi

# set OMP_NUM_THREADS to the number of --cpus-per-task we asked for
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

# Run the process with mpirun. Notice -n is not required. mpirun will
# automatically figure out how many processes to run from the slurm options
make
for i in 8 10 12 14
do
   for j in 4 8 12
   do
      export OMP_NUM_THREADS=$j
      mpiexec -np $i ./VFI
   done
done

#mpirun ./VFI
