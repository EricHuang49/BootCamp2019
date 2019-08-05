#!/bin/bash
# a sample job submission script to submit an OpenMP job to the broadwl
# partition on Midway please change the --partition option if you want to use 
# another partition on Midway

# set the job name to omp_example
#SBATCH --job-name=dcdp_omp

# send output to dcdp_omp.out
#SBATCH --output=dcdp_omp.out

# this job requests node
#SBATCH --ntasks=1


# and request 8 cpus per task for OpenMP threads
#SBATCH --cpus-per-task=8

# this job will run in the broadwl partition on Midway1
#SBATCH --partition=broadwl



# Run the process with mpirun. Notice -n is not required. mpirun will
# automatically figure out how many processes to run from the slurm options
### openmp executable
# Run the process 
make
export OMP_NUM_THREADS=1
./VFI
export OMP_NUM_THREADS=2
./VFI
export OMP_NUM_THREADS=4
./VFI
export OMP_NUM_THREADS=8
./VFI
