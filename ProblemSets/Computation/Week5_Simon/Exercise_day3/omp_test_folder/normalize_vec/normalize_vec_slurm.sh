#!/bin/bash
# a sample job submission script to submit an OpenMP job to the broadwl
# partition on Midway please change the --partition option if you want to use 
# another partition on Midway

# set the job name to omp_example
#SBATCH --job-name=normalize_vec

# send output to output.out
#SBATCH --output=normalize_vec.out

# this job requests node
#SBATCH --ntasks=1


# and request 8 cpus per task for OpenMP threads
#SBATCH --cpus-per-task=16

# this job will run in the broadwl partition on Midway1
#SBATCH --partition=broadwl



# Run the process with mpirun. Notice -n is not required. mpirun will
# automatically figure out how many processes to run from the slurm options
### openmp executable
# Run the process 
make
for i in 1 2 4 8 12 16
do
   export OMP_NUM_THREADS=$i
   ./normalize_vec.exec
done
